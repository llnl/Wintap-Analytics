---
title: "Feature Design: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collect.sh
  - ../Lintap/packaging/lintap-rpm/lintap.env
  - ../wintap/documentation/Linux Deployment Guide.md
  - ../wintap/wintap/core/infrastructure/PluginManager.cs
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/ETLConfig.json
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../wintap/wintap/core/etl/shared/Utilities.cs
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-08-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-pidstat-collector/design.md
tags: [feature-work, design, lintap, pidstat, parquet, s3]
---

# Feature Design: Improve pidstat Collector

## Summary

A new collector script in `../Lintap` runs pidstat continuously as a managed
service, rotates samples into parquet files partitioned like raw_sensor
(`dayPK=YYYYMMDD/hourPK=HH`), and drops completed files into the sensor's
parquet cache under `raw_sensor/pidstat/`. The sensor's existing
CacheManager/uploader pipeline ships them to S3 and deletes them locally —
no C# changes. Wintappy's pidstat DBT macros and bronze model change from
tab-delimited CSV to parquet in a coordinated update.

## Decisions Recorded (from brief, 2026-08-11)

- New script; `pidstat-collect.sh` remains as a minimal example.
- Location: `../Lintap`, for now.
- Runs continuously as a service, independent of individual Lintap runs.
- Sampling interval: 5 s default, configurable.
- Output format: parquet.
- Rotation boundary: the sensor's merge/upload cycle (`UploadIntervalSec`),
  partition layout `dayPK=/hourPK=` matching raw_sensor.
- S3 push: ride the sensor's existing upload mechanism, at least for now.

## Decisions Recorded (post-review, 2026-08-12)

- Sample with `-p ALL` (every process every interval), as implemented in the
  first slice. This deviates from the old activity-only collector and
  multiplies volume roughly 5× (observed ~59k rows/15 min ≈ 5.7M rows/day on a
  quiet host, vs. ~1.1M lines/day before), but idle-process RSS/VSZ is needed
  for the motivating correlation analysis (Lintap memory/CPU vs. event_store
  growth), and complete sampling is the safer default for research data.
  Accepted for now; if volume becomes a problem, filter or compress in the ETL
  layer (Wintappy bronze/silver) later rather than at collection time —
  dropping data at the collector is unrecoverable, dropping it downstream is a
  view choice.

## Proposed Approach

### Mechanism facts this design relies on (verified 2026-08-11)

- `CacheManager.upload()` enumerates **all** `*.parquet` under
  `{parquetRoot}/raw_sensor/` recursively and hands each file to every enabled
  uploader; it is event-type-agnostic, so a new `raw_sensor/pidstat/` subtree
  rides along without sensor changes.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §upload() -->
- `Uploader_UploadCompleted` deletes each parquet after a successful upload,
  so local retention after upload is already handled.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §Uploader_UploadCompleted -->
- Uploaders build the S3 key from the path relative to the parquet root
  (`raw_sensor/<type>/dayPK=…/hourPK=…/file.parquet`), so the S3 layout
  mirrors the local layout automatically.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getS3ObjectNameForFile -->
- The upload loop runs `doMerge()` + upload every `UploadIntervalSec`; the
  collector's rotation should use the same configured value.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §uploader thread -->
- `cleanup()` deletes orphaned `*.active` files, establishing the existing
  in-progress-file convention: only completed data may carry the `.parquet`
  extension inside the swept tree.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §cleanup() -->

### Collector loop

1. Run `pidstat -u -d -r -w -h -p ALL <interval>` (default 5 s) continuously
   (`-p ALL` per the post-review decision above),
   appending raw samples to an in-progress spool file **outside** the
   `raw_sensor/` tree (e.g., `$WINTAP_DATA_ROOT/pidstat-spool/current.tsv`),
   so the uploader can never see a partial window.
2. On each rotation boundary (aligned to wall-clock so windows map cleanly to
   `hourPK`; boundary length = the sensor's `UploadIntervalSec`), close the
   spool file and convert it to typed parquet with the DuckDB CLI, applying
   the same casts/column names as today's `stg_pidstat_metrics` (so the
   parquet schema is already the bronze schema).
3. Atomically move the completed file to
   `{parquetRoot}/raw_sensor/pidstat/dayPK=YYYYMMDD/hourPK=HH/<host>+pidstat+<epoch>.parquet`
   (write to a temp name, `mv` into place — rename is atomic within a
   filesystem).
4. The sensor's upload cycle picks it up, ships to S3, deletes locally.

### Service lifecycle

- A systemd unit (template in `../Lintap/packaging/`) with `Restart=always`
  runs the collector independent of sensor sessions.
- On startup, the collector salvages or discards a leftover spool file from a
  crash (salvage = convert and ship the partial window with its real
  timestamps; the data is still valid samples).

### Accumulation guard

While the sensor is down, completed parquet accumulates locally (nothing
sweeps it). The collector enforces a configurable cap (max total bytes or max
age) on `raw_sensor/pidstat/`, deleting oldest-first past the cap and logging
what was dropped.

### Wintappy coordinated change

- `pidstat_data_path()` / `pidstat_csv_glob()` macros become parquet-oriented:
  default glob `$WINTAP_DATA_ROOT/raw_sensor/pidstat/**/*.parquet`, with
  `PIDSTAT_DATA_PATH` still honored for overrides.
- `stg_pidstat_metrics` becomes a `read_parquet` passthrough (casting already
  done at collection time); the silver model is unchanged.

## Data Model Or Schema Changes

Parquet columns = today's `stg_pidstat_metrics` output columns (time, uid,
pid, usr_percent … command, filename-equivalent provenance column TBD). One
addition: a `hostname` column, since data from many hosts lands in one S3
bucket (raw_sensor rows carry host identity via filename convention;
pidstat should carry it in-band).

## Edge Cases

- Midnight rollover: window spanning midnight is split at the boundary (or
  assigned by window-start time — pick one and document; window-start is
  simpler and matches raw_sensor's capture-time-based partitioning).
- Empty windows (pidstat produced no output): skip file creation.
- Clock jumps / suspend-resume: partition by sample timestamps, not wall-clock
  at conversion time.
- DuckDB CLI missing: fail loudly at service start, not at first rotation.
- Sensor down for days: accumulation guard above.

## Error Handling

- Collector logs to journald (via systemd) with the same timestamped style as
  the existing script.
- Conversion failure keeps the spool file and retries next cycle rather than
  dropping samples.

## Risks

- The ride-along contract is implicit: nothing in the sensor promises to keep
  sweeping unknown subtrees under `raw_sensor/`. A sensor-side change could
  silently strand pidstat files. Mitigation: record the dependency in the
  sensor repo docs at closeout, and the accumulation guard bounds the damage.
- `pruneCache()` behavior on Linux (drive-letter logic looks Windows-oriented)
  is unverified; if cache pruning misbehaves it could delete unshipped pidstat
  files under pressure.
- Old tab-CSV datasets become unloadable by the updated bronze model unless
  migrated (see below).

## Alternatives Considered

- Standalone `aws s3` sync loop in the collector: independent of sensor
  lifetime, but duplicates credentials, retry, and layout logic. Rejected
  "for now" per brief.
- Keep tab-CSV output: no DBT change needed, but conflicts with the parquet
  decision and uniform-layout goal.
- Implement inside the sensor (C#): best lifecycle integration, but violates
  the brief's non-goal and couples resource monitoring to sensor uptime.

## Open Questions

- Resolved 2026-08-12: the Linux service path does run the upload loop when ETL
  is enabled. The documented Linux systemd service starts `Lintap.dll` with
  `WINTAP_DISABLE_ETL=false`, and `PluginManager` responds by constructing
  `WintapETL`, which starts `CacheManager`.
  <!-- GROUND_TRUTH: ../wintap/documentation/Linux Deployment Guide.md §Example systemd Service -->
  <!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/lintap.env §Enable normal ETL and Linux sensor manager -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/PluginManager.cs §PluginManager() -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/WintapETL.cs §cacheManager_DoWork -->
- Resolved 2026-08-12: the repo-shipped ETL config uses `UploadIntervalSec` =
  `300`, and the current code only exposes an environment override for that
  interval (`WINTAP_ETL_UPLOAD_INTERVAL_SEC`), not for adapter enablement.
  The shipped `ETLConfig.json` leaves `S3Adapter.Enabled=false`, so the
  pidstat ride-along works only on Linux deployments that explicitly enable S3
  in the deployed `ETLConfig.json`; this slice therefore keeps upload
  verification read-only/manual rather than assuming S3 is active everywhere.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/ETLConfig.json §Adapters -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/ETLConfig.json §UploadIntervalSec -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/shared/Utilities.cs §GetETLConfig -->
- DuckDB CLI vs. small Python program for the collector: bash+duckdb keeps
  `../Lintap`'s script style; Python (uv project already exists there) is
  easier to test. Leaning bash+duckdb for the first slice, tests via bats or
  shell harness.
- Migration of already-collected tab-CSV data: one-time DuckDB conversion
  script, or keep a legacy `read_csv` union in bronze for one release?
- Should the validation harness (lintap validation thread) switch its pidstat
  capture to the new collector once it exists?
