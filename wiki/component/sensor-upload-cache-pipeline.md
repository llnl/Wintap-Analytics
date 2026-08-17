---
title: "Sensor Upload/Cache Pipeline"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/Merge.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../wintap/wintap/core/etl/ETLConfig.json
  - ../Lintap/pidstat-collector.py
policy: agent-editable
last_validated: 2026-08-17
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/component/sensor-upload-cache-pipeline.md
tags: [wintap, lintap, etl, upload, s3, parquet, cache, cross-repo]
---

# Sensor Upload/Cache Pipeline

Shared `core/etl/load/` behavior for Windows Wintap and Linux Lintap
(`PluginManager` → `WintapETL` → `CacheManager` on both). Promoted from the
fix-upload-cache-deletion and improve-pidstat-collector feature work
(closed 2026-08-17).

## Layout And Cycle

- Cache root is the parquet data path; upload-eligible data lives under
  `raw_sensor/<event_type>/dayPK=YYYYMMDD/hourPK=HH/*.parquet`
  (network adds `protoPK=`). S3 keys mirror this relative layout.
- Every `UploadIntervalSec` (shipped default 300; env override
  `WINTAP_ETL_UPLOAD_INTERVAL_SEC`): `doMerge()` consolidates each
  serializer directory's flush files (written every
  `SerializationIntervalSec`, shipped default 60) into one file per event
  type per cycle, materialized into the partition layout; then the upload
  sweep enumerates `raw_sensor/**/*.parquet` once and hands each file to
  every enabled adapter.

## Contracts (verified 2026-08-15..17)

- **The sweep is event-type-agnostic**: any producer that drops completed
  parquet into a `raw_sensor/<type>/dayPK=/hourPK=/` path rides the upload
  pipeline with no C# changes. The Lintap pidstat collector uses this
  ride-along contract. This contract is implicit — sensor-side changes to
  the sweep can strand ride-along producers.
- **Delete-after-upload** (fixed 2026-08-17, `../wintap` ecfa746; before
  this, no adapter ever raised the delete event and every file re-uploaded
  each cycle forever): after the full adapter loop for a file, "any success
  = all success" deletes it; total failure retains it for retry next cycle.
  Zero-byte files are deleted. Delete/dir-removal failures (Windows AV
  locks, races) are tolerated and retried — the upload thread never dies
  from them.
- **Empty partition directories** are removed bottom-up after their last
  file, never the `raw_sensor` root.
- **Prune backstop**: `raw_sensor/` capped at `RawSensorMaxCacheSizeBytes`
  (config, default 256 MB), oldest-first.
- **Merge-hang recovery** kills the helper and clears unmerged working
  directories only — never `raw_sensor/` contents.
- **In-progress convention**: only completed data may carry the `.parquet`
  extension inside the swept tree (`*.active` names for temp files,
  atomic rename).

## Deployment Prerequisites

- Shipped `ETLConfig.json` has all adapters disabled; S3 ride-along works
  only where the deployed config enables an adapter.
- ETL runs when `WINTAP_DISABLE_ETL=false` (Linux packaging default).
- First deploy of the deletion fix onto a host that ran the broken version:
  clear `raw_sensor/` or accept a one-time sequential backlog drain
  (~4 files/sec throttle).

## Known Follow-Ups

- Generic small-file consolidation: `doMerge()` only merges serializer
  directories; direct-to-`raw_sensor` producers (pidstat) accumulate small
  per-window files. Next slice in
  [[wiki/work/fix-upload-cache-deletion/brief]].
- Live 3+ cycle uploader validation and the Windows service-mode
  delete-after-upload run are pending (post-merge).

## Related

- [[wiki/work/fix-upload-cache-deletion/brief]] - the deletion fix and
  robustness cleanups (closed; evidence and review in its verification)
- [[wiki/work/improve-pidstat-collector/brief]] - the ride-along producer
- [[wiki/repo/lintap-supporting-repo]] - collector packaging
