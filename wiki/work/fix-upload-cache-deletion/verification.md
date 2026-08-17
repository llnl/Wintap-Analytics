---
title: "Verification: Fix Upload Cache Deletion"
type: concept
confidence: medium
grounded_by:
  - wiki/work/fix-upload-cache-deletion/brief.md
  - ../wintap/wintap/core/etl/load/CacheManager.cs
policy: agent-editable
last_validated: 2026-08-16
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/fix-upload-cache-deletion/verification.md
tags: [feature-work, verification, wintap, etl, upload, cache]
---

# Verification: Fix Upload Cache Deletion

## Test Commands

1. `git checkout grantj-rhel8-testing` in `Wintap-Analytics/`, `../Lintap`, `../Wintappy`, and `../wintap`
Result: all four local checkouts aligned on the same branch name before the upload-cache work started.

2. `multipass exec lintap-dev --working-directory /home/ubuntu/git/wintap/wintap -- bash -lc "dotnet build Lintap.csproj"`
Result: Linux-target `Lintap.csproj` build passed after the cache-management edits.

3. `multipass exec lintap-dev --working-directory /home/ubuntu/git/wintap/wintap -- bash -lc "dotnet build Lintap.csproj -warnaserror:CS0067"`
Result: build passed with `CS0067` promoted to an error, confirming the dead `UploadCompleted` warnings are gone from the active load path.

4. `grep "UploadCompleted" ../wintap/wintap/core/etl/load/**/*.cs`
Result: remaining matches are only in the commented-out `SignedS3UrlAdapter.cs`; no active load-path class still declares or subscribes the event.

5. `multipass exec lintap-dev --working-directory /home/ubuntu/git/wintap/wintap -- bash -lc "mkdir -p /var/tmp/opencode/wintap-win-build-2 && dotnet build Wintap.csproj -p:EnableWindowsTargeting=true -warnaserror:CS0067 -p:BaseIntermediateOutputPath=/var/tmp/opencode/wintap-win-build-2/obj/ -p:BaseOutputPath=/var/tmp/opencode/wintap-win-build-2/bin/"`
Result: `Wintap.csproj` did not complete in this VM, but the failures are unrelated to the upload-cache edits: missing Windows-target/ETW-era dependencies (`TraceEvent`, `System.Configuration.ConfigurationManager`, etc.) already prevent a clean `EnableWindowsTargeting` build in this environment.

## Manual Checks

- Reviewed `CacheManager.upload()` and confirmed the delete site now lives after
  the full uploader loop for each file, gated on the existing
  `successfulUpload` flag.
- Reviewed `CacheManager.WorkerThread_DoWork()` and confirmed `raw_sensor`
  parquet enumeration happens once per cycle, then the same list flows through
  prune and upload.
- Reviewed `pruneCache()` and confirmed:
  - cap accounting is now based on `raw_sensor/*.parquet` size only
  - the threshold-crossing file is actually deleted
  - the hardcoded 256 MB value became `RawSensorMaxCacheSizeBytes`
  - current-window files are protected from pruning once reached
- Reviewed `HangDetector_Elapsed()` and confirmed it now skips `raw_sensor/`,
  `csv/`, and `merged/` directories instead of recursively deleting the entire
  parquet root.
- Reviewed `PostUpload()` handling and confirmed each uploader call is wrapped
  individually so one exception no longer kills the upload worker loop.

## Results

- The dead delete-after-upload path was replaced with inline delete in
  `CacheManager.upload()`.
- Dead `UploadCompleted` event declarations were removed from the active load
  interface and adapters.
- Zero-byte parquet files are now deleted instead of skipped forever.
- Empty partition directories are removed opportunistically after file delete,
  while never deleting the `raw_sensor` root.
- Merge-hang cleanup is scoped away from `raw_sensor` data.
- `Lintap.csproj` builds cleanly in `lintap-dev` with `CS0067` treated as an
  error.

## Known Gaps

- No live uploader target was exercised in `lintap-dev`, so the acceptance
  criteria around single-upload-plus-delete across 3+ cycles still need a real
  filesystem/S3/Garage-style validation run.
- `Wintap.csproj -p:EnableWindowsTargeting=true` is still blocked in this VM by
  unrelated Windows-target dependency/build issues, so the Windows build part
  of the handoff could not be completed here.
- The real packaged service path on Windows remains unverified.

## Follow-Ups

- Run a 3+ cycle uploader validation on a real target host and confirm:
  single upload, delete-after-upload, empty-dir cleanup, and failed-upload
  retention.
- Re-run the `EnableWindowsTargeting` build in an environment where the current
  Windows-target dependencies are already known-good.
- If this fix is accepted and merged, update
  `wiki/work/improve-pidstat-collector/implementation_plan.md` to note that its
  S3/delete-after-upload blocker is removed.
