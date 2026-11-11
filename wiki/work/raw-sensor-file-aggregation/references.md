---
title: "Feature References: Raw Sensor File Aggregation"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/Merge.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/raw_sources.sql
policy: agent-editable
last_validated: 2026-11-10
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/raw-sensor-file-aggregation/references.md
tags: [feature-work, references, raw_sensor, duckdb, s3, parquet]
---

# Feature References: Raw Sensor File Aggregation

## Live Repo Sources

- `../wintap/wintap/core/etl/load/CacheManager.cs`
  - `WorkerThread_DoWork` runs merge before the upload sweep at the configured
    interval (shipped default documented as 300 seconds in
    [[wiki/component/sensor-upload-cache-pipeline]]).
  - `doMerge()` supplies one `DateTime.UtcNow` merge time to its sensor merges.
  - `upload()` retains files when every enabled upload attempt fails and retries
    them on a later cycle.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §WorkerThread_DoWork; §doMerge; §upload -->

- `../wintap/wintap/core/etl/load/Merge.cs`
  - The provided merge time is embedded in generated output file names.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/Merge.cs §Start -->

- `../wintap/wintap/core/etl/load/RawSensorWriter.cs`
  - The generated timestamp is decoded and used to create `dayPK` and
    `hourPK`; network output adds `protoPK`.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/RawSensorWriter.cs §MaterializeFromParquetGlob -->

- `../wintap/wintap/core/etl/load/adapters/base/Uploader.cs` and
  `../wintap/wintap/core/etl/load/adapters/S3Adapter.cs`
  - The S3 key is derived from the local file's relative `raw_sensor` path; the
    adapter does not currently remap an old partition on retry.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getS3ObjectNameForFile; ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs §Upload -->

- `../Wintap-PyUtil/pyproject.toml`
  - The canonical Python package currently pins `duckdb==1.5.6` and
    `dbt-duckdb>=1.9,<1.10`; the compaction job is intended to use a separate
    DuckDB 2.0.0 environment.
  <!-- GROUND_TRUTH: ../Wintap-PyUtil/pyproject.toml §project.dependencies -->

- `../Wintap-PyUtil/wintap_dbt/macros/paths.sql` and
  `../Wintap-PyUtil/wintap_dbt/macros/raw_sources.sql`
  - DBT builds recursive Parquet globs below the configured raw-sensor dataset
    root, including day/hour partition selection. This motivates a separate
    destination dataset root rather than side-by-side output.
  <!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_path/raw_sensor_glob/raw_sensor_partition_globs; ../Wintap-PyUtil/wintap_dbt/macros/raw_sources.sql -->

## External Sources

- DuckDB 2.0.0 `COPY` and S3 support documentation — confirm exact Python API,
  extension installation, authentication, and multipart-write behavior during
  design; no cloud write behavior is assumed validated by this reference list.

## Related Wiki Pages

- [[wiki/component/sensor-upload-cache-pipeline]] — current producer merge,
  cache, and upload behavior; includes the distinct in-host small-file
  consolidation follow-up.
- [[wiki/repo/wintappy-pipeline-repo]] — canonical DBT raw input and current
  DuckDB dependency.
- [[wiki/work/fix-upload-cache-deletion/brief]] — earlier upload-cache work and
  the generic in-upload-cycle small-file consolidation idea.
- [[wiki/work/duckdb-2-upgrade/brief]] — broader ecosystem DuckDB 2 planning;
  this new isolated compactor is not a cross-ecosystem dependency upgrade.
- [[wiki/todo/raw-sensor-upload-time-partition]] — requested .NET correction
  for delayed uploads and current-vs-intended partition semantics.

## Libraries And APIs

- DuckDB 2.0.0 `read_parquet`/`COPY` through the selected CLI/runtime: core
  aggregation and Parquet write engine requested by the user; Python API versus
  DuckDB CLI, S3 configuration, schema union, row-count validation, and safe
  publication need a design/spike.
- AWS S3: source and destination object storage; use isolated prefixes for
  tests. Exact credential provider, endpoint compatibility, and publication
  protocol remain open.

## Notes

- The output dataset must not contain both source and aggregate files under the
  same `raw_sensor` root that a consumer scans.
- `dayPK`/`hourPK` are used as exact grouping keys; the compactor does not
  derive output partitions from event timestamps.
- The user's desired rule is partitioning by the UTC wall-clock time of actual
  upload. Current source partitions at UTC merge/materialization time and
  retains that relative path across failed-upload retries. The separate TODO
  tracks this gap; no sibling code change is authorized by this feature brief.
