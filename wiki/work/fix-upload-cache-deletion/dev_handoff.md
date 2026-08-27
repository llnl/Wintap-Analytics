---
title: "Dev Handoff: Fix Upload Cache Deletion"
type: concept
confidence: high
grounded_by:
  - wiki/work/fix-upload-cache-deletion/brief.md
  - ../wintap/wintap/core/etl/load/CacheManager.cs
policy: agent-editable
last_validated: 2026-08-15
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: wiki/work/fix-upload-cache-deletion/dev_handoff.md
tags: [feature-work, handoff, wintap, etl, upload, cache]
---

# Dev Handoff: Fix Upload Cache Deletion

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

```text
Switch to code-development mode for the fix-upload-cache-deletion feature.

Work from the Wintap-Analytics repository root. Read AGENTS.md first and
confirm code-development mode is active for this task.

Use these wiki files as the handoff context:

- wiki/work/fix-upload-cache-deletion/brief.md (full evidence with
  GROUND_TRUTH pointers; goals; acceptance criteria; open questions)

Goal: make the sensor's upload cache actually drain — delete each cached
parquet after confirmed upload, fix pruneCache() on Linux, and remove
emptied partition directories.

Authorization: you are explicitly authorized to modify files in ../wintap
for this feature (core/etl/load/ and its adapters/interfaces). Do NOT
modify ../Lintap or ../Wintappy. Wintap-Analytics may be modified only
under wiki/ (feature artifacts, log).

The bug (details and line-level GROUND_TRUTH in the brief):
- CacheManager.Uploader_UploadCompleted deletes on the UploadCompleted
  event, but no adapter ever raises it (S3Adapter/SMBFileShareAdapter
  declare it only; SignedS3UrlAdapter's invoke is commented out).
- CacheManager.upload() sets successfulUpload ("any success = all
  success, for now") and never reads it — the intended delete site.

Recommended fix shape (deviate only with recorded rationale):
1. Delete inline in CacheManager.upload() after the full uploader loop
   for each file, gated on successfulUpload. Do NOT raise the event from
   inside adapters mid-loop — with multiple enabled uploaders that would
   delete the file before the next uploader gets it.
2. Preserve the "any success = all success" multi-adapter policy as-is
   (recorded open question; default is keep).
3. Decide the dead-event question: either remove UploadCompleted from
   IUpload and the adapters (interface change — record it), or keep the
   interface and raise it from the delete site for observability. Either
   way, no CS0067 warnings remain in core/etl/load/.
4. Fix pruneCache() free-space logic for Linux (no drive-letter
   assumptions; DriveInfo(path) works cross-platform) and make it prefer
   never deleting files newer than the current upload window while
   un-uploaded files exist, or document the limitation.
5. After deleting a file, remove now-empty dayPK=/hourPK=/event-type
   directories (Long_Running_Cleanup ask). Never remove the raw_sensor
   root.
6. Failure path: a file whose uploads all fail is retained and retried
   next cycle (existing behavior — keep it, add a log line).
7. Robustness cleanups from the 2026-08-15 review (see brief Goals for
   GROUND_TRUTH pointers), in priority order:
   - Scope HangDetector_Elapsed's recovery to unmerged working dirs — it
     currently deletes ALL parquet under the parquet root on a hung
     merge, including un-uploaded raw_sensor data.
   - Fix pruneCache(): delete the threshold-crossing file (current loop
     breaks first), measure the cap against raw_sensor/ size (not the
     whole cache), make the hardcoded 256 MB cap configurable, remove
     the unused drive-letter getFreeBytes.
   - Wrap the PostUpload() loop per-uploader (an exception there
     silently kills the upload thread); replace the empty catch in the
     delete path; upload failures log at Warn, not Info.
   - Delete zero-byte parquet files instead of skipping them.
   - Enumerate the raw_sensor file list once per cycle.
   Do NOT change: S3 client lifecycle, the 429 backoff, credential
   handling, key mirroring, or the .Result upload pattern.
8. Windows correctness (this is shared code — Windows Wintap runs the same
   CacheManager and has the same bug): file deletes and empty-dir removals
   must tolerate transient failures (AV/indexer locks, non-empty race) by
   logging, skipping, and retrying next cycle — never crash the upload
   thread, never double-delete. Case-insensitive filesystems and path
   separators are already handled (globs + getS3ObjectNameForFile
   normalization) — do not add case/separator logic.

Verification additions for Windows: beyond the EnableWindowsTargeting
compile, run a Windows service-mode check (same setup as the 2026-08-13
retention verification) with an enabled uploader confirming
delete-after-upload across >=3 cycles.

Verification (record everything in
wiki/work/fix-upload-cache-deletion/verification.md, created from the
template in wiki/concept/feature-work-template.md):
- Build Lintap.csproj and Wintap.csproj -p:EnableWindowsTargeting=true in
  the dev VM; confirm no CS0067 remains in core/etl/load/.
- Instrumented VM run over >=3 upload cycles with an enabled uploader
  (local/Garage/opt-in S3): each file uploaded exactly once, deleted
  after its cycle, empty partition dirs removed, failed uploads retained.
- Do not run against production S3; no git commits unless the human asks.

As you work: update the brief's Open Questions with your decisions, check
progress into verification.md, and append a concise entry to wiki/log.md.
```

## Handoff Summary

One well-evidenced dead-code bug with an obvious intended fix site, plus
same-subsystem robustness cleanups found in a follow-up review — most
notably scoping the merge-hang recovery, which today deletes the entire
parquet cache including un-uploaded data. Small blast radius: all changes
inside `../wintap/wintap/core/etl/load/`. Field-validated symptom: overnight
RHEL 8 run re-uploaded the same files every cycle.

## Non-Goals For This Slice

- Adapter interface redesign or SignedS3UrlAdapter revival.
- Upload retry/queueing improvements.
- Any Lintap/Wintappy changes.

## Closeout Instructions

- Fill in verification.md (create from template); update the brief's open
  questions with decisions taken.
- Append a concise entry to `wiki/log.md`.
- Notify the pidstat feature: its blocked checklist item
  ("1h+ end-to-end with S3 upload + local delete") unblocks when this
  merges — note it in
  [[wiki/work/improve-pidstat-collector/implementation_plan]].

## Operating Mode Note

`AGENTS.md` distinguishes wiki-maintainer mode from code-development mode.
This handoff grants `../wintap` (core/etl/load/) modification only;
`../Lintap`, `../Wintappy`, and `raw/` remain protected.
