---
title: "To-Do: Set Raw Sensor Partitions at Upload Time"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/Merge.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
policy: agent-editable
last_validated: 2026-11-10
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/etl/load/CacheManager.cs; ../wintap/wintap/core/etl/load/Merge.cs; ../wintap/wintap/core/etl/load/RawSensorWriter.cs; ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs; ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
tags: [todo, upload, s3, partitioning, raw_sensor, wintap, lintap]
---

# To-Do: Set Raw Sensor Partitions at Upload Time

**Priority:** Untriaged (requested follow-up; correctness implications need
review).
**State:** Open — intake only; no .NET code change is authorized by this TODO.
**Likely next step:** Review the intended timestamp boundary and design a
retry-safe S3-key/path correction in the shared upload code, then obtain explicit
implementation authorization.

## Finding

The user-defined contract is that hosts write `dayPK`/`hourPK` from the UTC
wall-clock time of the actual upload, rather than from event time or earlier
local materialization time. A host returning after an outage is expected to
publish locally cached event rows under the current upload-time partition.

Current Wintap source does not establish that contract:

- `CacheManager.doMerge()` captures `DateTime.UtcNow` before the merge and passes
  that value to each merge operation.
- `Merge` embeds that merge time in the output filename; `RawSensorWriter` derives
  `dayPK`/`hourPK` from the filename timestamp.
- When all upload attempts fail, `CacheManager.upload()` retains the local
  `raw_sensor` file for a later retry.
- The S3 adapter derives the object key by preserving the file's relative
  `raw_sensor` path. It does not currently recalculate the partition on retry.

Therefore a file materialized before an hour boundary can arrive later in its
original hour partition. This conflicts with the requested actual-upload
contract and can make one-pass hourly aggregation incomplete if that partition
was already compacted.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §doMerge/§upload; ../wintap/wintap/core/etl/load/Merge.cs §Start; ../wintap/wintap/core/etl/load/RawSensorWriter.cs §MaterializeFromParquetGlob; ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getS3ObjectNameForFile; ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs §Upload -->
<!-- SYNTHESIS: inferred consequence for hourly aggregation from the current merge-time partition and same-relative-key retry behavior -->

## Requested Outcome

Update the shared .NET upload behavior so a delayed/failed upload is published
under the `dayPK`/`hourPK` corresponding to the UTC wall-clock time of its
actual successful upload, or implement an equivalent mechanism that enforces
that contract. Do not change event timestamps or payload rows as a side effect.

The specific implementation must decide whether to remap only the S3 object
key, move/re-materialize the local file, or use another explicit publication
step. It must preserve retry safety and avoid duplicate objects when a request
may have reached S3 but the client did not receive a success response.

## Investigation / Verification

1. Confirm the contract for S3 and other enabled upload adapters, including the
   exact UTC clock instant used when an upload spans an hour boundary.
2. Trace shared `CacheManager`/adapter behavior for Windows Wintap and Linux
   Lintap packaging; identify any producer that bypasses the shared uploader.
3. Test a file materialized before an hour boundary, failed upload, then
   successful retry after the boundary; assert the final object key uses the
   intended upload-time partition and row timestamps/contents are unchanged.
4. Test retries after ambiguous success, multiple enabled adapters, process
   restart, and day/month/year boundaries; prove no data loss or duplicate
   published rows.
5. Confirm downstream Wintappy raw scans discover the resulting partition and
   document any local-cache versus S3-path distinction.

## Open Questions

- Does “actual upload time” mean attempt start, S3 acceptance/response time, or
  another observable UTC instant?
- Must all uploader adapters share this rule, or is it specifically the S3
  destination contract?
- Should the local cached path also change, or only the remote object key?
- How should retries handle an ambiguous prior PUT so the data is not duplicated
  under both the old and new partition?
- Which exact Wintap/Lintap source branch and deployment path own the correction?

## Scope

This is a cross-repo wiki intake item for a possible shared .NET upload fix.
No source code, schema, raw document, or S3 object was changed. Implementing the
follow-up requires a separate explicit code-development authorization. It is
linked to [[wiki/work/raw-sensor-file-aggregation/brief]], whose no-lookback
scheduled design depends on this contract or an equivalent verified guarantee.
