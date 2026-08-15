---
title: "Feature Brief: Fix Upload Cache Deletion"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs
  - ../wintap/wintap/core/etl/load/adapters/SMBFileShareAdapter.cs
  - ../wintap/wintap/core/etl/load/adapters/SignedS3UrlAdapter.cs
  - raw/Issues/Long_Running_Cleanup.md
policy: agent-editable
last_validated: 2026-08-15
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/fix-upload-cache-deletion/brief.md
tags: [feature-work, wintap, etl, upload, s3, cache, retention, long-running]
---

# Feature Brief: Fix Upload Cache Deletion

## Problem

The sensor's parquet cache is never emptied by successful uploads. An
overnight RHEL 8 field test (2026-08-14/15) showed the S3 uploader re-sending
the same files every upload cycle, forever.

Code review confirms a dead delete path:

- `CacheManager.Uploader_UploadCompleted` (the only delete-after-upload
  mechanism) is subscribed at startup and deletes the file named by the
  event argument — but **no adapter ever raises `UploadCompleted`**.
  `S3Adapter` and `SMBFileShareAdapter` declare the event (satisfying
  `IUpload`) and never invoke it; the only invocation in the codebase is in
  `SignedS3UrlAdapter`, commented out.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §Uploader_UploadCompleted -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs §UploadCompleted declaration; §Upload (returns fileSent, no event) -->
- `CacheManager.upload()` computes `successfulUpload = true; // any success
  = all success, for now.` and **never reads the variable** — visibly where
  the delete was meant to go.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §upload() -->
- The only thing removing cache files is `pruneCache()`'s 256 MB oldest-first
  cap, whose free-space check uses Windows drive-letter logic
  (`cacheDir.FullName.First() + ":\\"`) and is unverified-to-broken on Linux.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §pruneCache() -->

Consequences on long runs: unbounded re-upload bandwidth/request volume
(same S3 keys overwritten every `UploadIntervalSec`), cache growth to the
prune cap, and — because pruning is oldest-first by cap rather than
by-uploaded — possible deletion of never-uploaded data under pressure while
already-uploaded data is resent. The compiler flags the dead events as
CS0067 warnings, buried in warnings-only builds.

Related item from the same motivating issue
(`raw/Issues/Long_Running_Cleanup.md`): emptied `dayPK=/hourPK=` partition
directories under `raw_sensor/` should be removed once their files are gone.

## Goals

- Delete each cached parquet after confirmed upload, preserving the
  documented multi-uploader policy ("any success = all success, for now").
- Make `pruneCache()` free-space and cap logic work on Linux (e.g.,
  `DriveInfo(path).AvailableFreeSpace`, no drive-letter assumptions).
- Remove empty `dayPK=/hourPK=` (and event-type) directories after their
  files are deleted (the Long_Running_Cleanup ask).
- Wire or remove the dead `UploadCompleted` declarations so CS0067 stops
  masking real intent (decision recorded in design).
- Robustness cleanups found in the 2026-08-15 subsystem review (prioritized):
  1. Scope merge-hang recovery: `HangDetector_Elapsed` currently deletes ALL
     parquet under the parquet root on a hung merge — including un-uploaded
     `raw_sensor/` data and future pidstat files. Restrict it to the
     unmerged working directories.
     <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §HangDetector_Elapsed (deleteParquetFiles over Paths.ParquetDataPath) -->
  2. Fix `pruneCache()` accounting: the loop breaks before deleting the
     threshold-crossing file (off-by-one); the cap compares whole-cache size
     while deleting only `raw_sensor/*.parquet` (unreachable-target risk);
     make the hardcoded 256 MB cap configurable; remove the unused
     drive-letter `getFreeBytes` dead code.
     <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §pruneCache() -->
  3. Guard the uploader plumbing: wrap the unguarded `PostUpload()` loop
     (one adapter exception silently kills the upload thread until service
     restart); replace the empty catch in the delete path; raise upload
     failure logs from Info to Warn.
  4. Delete zero-byte parquet files instead of skipping them (post-fix they
     would otherwise be re-enumerated forever, never uploaded, never
     deleted).
  5. Enumerate the raw_sensor file list once per cycle instead of twice.
- Prove it in the field: an overnight run uploads each file exactly once and
  the cache row/file count plateaus near the in-flight window.

## Non-Goals

- Redesigning the adapter interface or reviving `SignedS3UrlAdapter`.
- Upload retry/queueing semantics beyond what exists.
- The pidstat collector's own accumulation guard (separate feature; it
  remains the collector-side backstop).
- Windows-side behavioral changes beyond keeping the shared code correct.

## Acceptance Criteria

- After a successful upload cycle, uploaded files are gone from
  `{parquetRoot}/raw_sensor/` and are not re-uploaded next cycle (verified
  by S3 request logs or upload log counts across ≥3 cycles).
- A file that fails to upload is retained and retried.
- With multiple enabled uploaders, deletion happens only after the full
  uploader loop for that file (no mid-loop file removal).
- Empty partition directories are removed after their last file is deleted.
- `pruneCache()` computes free space correctly on Linux and never deletes a
  file newer than the current upload window while un-uploaded files exist
  (or its limitation is explicitly documented).
- Overnight field test: total S3 PUTs ≈ total files produced (no repeats);
  local cache size plateaus.
- A simulated merge hang deletes only unmerged working files, never
  `raw_sensor/` contents.
- `pruneCache()` deletes exactly enough files to reach the (configurable)
  cap, and its cap is measured against `raw_sensor/` size.
- A thrown exception in one adapter's `PostUpload` does not stop subsequent
  upload cycles.
- Windows (same shared `CacheManager` path via `PluginManager`→`WintapETL`,
  so Windows deployments have this bug too):
  - A file delete that fails due to a transient lock (AV scanner, indexer)
    is tolerated — logged, file retained, re-uploaded once and delete
    retried next cycle; the upload thread never dies from it.
  - Empty-dir removal tolerates `Directory.Delete` failures (non-empty race
    or open handle) by skipping and retrying next cycle — which also makes
    the new-file-arrives-during-delete race safe on both platforms.
  - A Windows service-mode run (the same setup used for the 2026-08-13
    retention check) confirms delete-after-upload across ≥3 cycles with an
    enabled uploader.

## Deployment Note

Machines that ran the broken version (e.g., the RHEL 8 test box) hold a
large already-uploaded backlog; on first deploy of the fix, either clear
`raw_sensor/` manually before start or accept a one-time sequential drain at
the 250 ms/file throttle.

## Affected Areas

- `../wintap/wintap/core/etl/load/CacheManager.cs` — delete-after-upload,
  pruneCache Linux fix, empty-dir cleanup (sibling repo; explicit
  authorization required).
- `../wintap/wintap/core/etl/load/adapters/*.cs` and `interfaces/IUpload.cs`
  — dead-event decision.
- Downstream: the pidstat collector feature's local-disk story
  ([[wiki/work/improve-pidstat-collector/brief]]) and its blocked
  S3 end-to-end checklist item.

## References

Evidence and pointers consolidated in this brief's GROUND_TRUTH comments;
cross-feature context in [[wiki/work/improve-pidstat-collector/design]]
(corrected mechanism fact, 2026-08-15).

## Open Questions

- Multi-adapter policy: keep "any success = all success" (delete when at
  least one uploader succeeded) or require all-enabled-success before
  delete? Current comment says the former is intentional "for now" —
  default to preserving it unless the human says otherwise.
- Wire the `UploadCompleted` event properly (raise after the uploader loop
  from CacheManager side is impossible — it's the adapters' event) or drop
  the event from `IUpload` and delete inline in `upload()`? Inline delete is
  the recommended shape (see design note in dev_handoff); event removal is
  an interface change to record.
- Should deletion be a move-to-`uploaded/` staging dir for one cycle instead
  of immediate delete (cheap undo) — or is immediate delete fine given
  parquet also lands in S3?

## Test Plan

- Build `Lintap.csproj` and `Wintap.csproj -p:EnableWindowsTargeting=true`
  in the dev VM.
- Instrumented VM run with a local-target uploader (or opt-in S3/Garage):
  confirm per-file single upload + deletion + empty-dir removal via logs and
  filesystem inspection across ≥3 upload cycles.
- Failure-path check: force an upload failure (bad credentials/endpoint) and
  confirm retention + retry next cycle.
- Overnight field validation on the RHEL 8 machine (the environment that
  caught this).

## Done When

- Acceptance criteria pass on the VM and the overnight field run.
- The dead-event and multi-adapter policy decisions are recorded.
- Durable facts promoted: the pidstat design's corrected mechanism note
  updated to point at the fixed behavior; upload/cache semantics recorded in
  a canonical page at closeout.
