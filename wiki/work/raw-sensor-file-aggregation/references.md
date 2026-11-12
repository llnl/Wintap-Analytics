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
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/pidstat_metrics.sql
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/test_s3_http.py
  - https://duckdb.org/docs/2.0/sql/statements/copy.html
  - https://duckdb.org/docs/2.0/data/parquet/overview.html
  - https://duckdb.org/docs/2.0/core_extensions/httpfs/s3api.html
  - https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
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

- `../Wintap-PyUtil/wintap_dbt/macros/s3.sql`
  - Existing named-profile handling explicitly supplies `CHAIN 'config'` and
    `PROFILE`; custom endpoints select path-style addressing, with explicit
    region/TLS settings. Reuse the configuration conventions, qualifying the
    chosen standalone credential flow independently on DuckDB 2.0.0.
  <!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

- `../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` and
  `../Wintap-PyUtil/wintap_dbt/models/silver/pidstat_metrics.sql`
  - Bronze selects DuckDB's virtual source-object `filename`; silver retains
    it. Compaction changes this derived provenance even with identical physical
    telemetry fields. The user's planning clarification in
    [[wiki/work/raw-sensor-file-aggregation/interview]] allows object filenames
    to change while preserving the partition scheme.
  <!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql §parquet_scan; ../Wintap-PyUtil/wintap_dbt/models/silver/pidstat_metrics.sql -->

- `../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py`
  - Nearby boto3 paginated discovery, object identity metadata, and
    connection-scoped temporary DuckDB S3-secret patterns. This implementation
    is read-only and day-scoped; the compactor needs exact-hour scope and writes.
  <!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py §open_source/discover_files/object_identity -->

- `../Wintap-Analytics/streamlit/projects/SmokeTests/test_s3_http.py`
  - Opt-in loopback signed listing/range-read transport coverage; explicitly not
    real Garage acceptance and not multipart-write evidence.
  <!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/SmokeTests/test_s3_http.py §HTTPSourceTest -->

## External Sources

Read on 2026-11-10. These document APIs; exact DuckDB 2.0.0 runtime and target
endpoint behavior still require the implementation plan's P0 spike.

- [DuckDB 2.0 COPY](https://duckdb.org/docs/2.0/sql/statements/copy.html)
  - `FILE_SIZE_BYTES` is approximate; `PER_THREAD_OUTPUT` affects output count;
    remote directory overwrite is unsupported. `RETURN_FILES`/`RETURN_STATS`
    provide output reporting options to qualify in the spike.
  <!-- GROUND_TRUTH: https://duckdb.org/docs/2.0/sql/statements/copy.html §COPY TO options -->
- [DuckDB 2.0 Parquet](https://duckdb.org/docs/2.0/data/parquet/overview.html)
  - Explicit file lists, schema inspection, `union_by_name`, hive inference,
    and virtual filename handling are relevant to physical-field conservation.
  <!-- GROUND_TRUTH: https://duckdb.org/docs/2.0/data/parquet/overview.html §Examples/Parameters -->
- [DuckDB 2.0 S3 API support](https://duckdb.org/docs/2.0/core_extensions/httpfs/s3api.html)
  - S3 writes use multipart upload and globbing uses ListObjectsV2. The `aws`
    extension supplies credential-chain support; S3-compatible services can
    differ in supported features and need endpoint-specific qualification.
  <!-- GROUND_TRUTH: https://duckdb.org/docs/2.0/core_extensions/httpfs/s3api.html §S3 API Support/Configuration and Authentication -->
- [Amazon S3 consistency model](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel)
  - Updates to one key are atomic; updates across keys are not atomic. Strong
    consistency therefore does not make multi-shard publication transactional.
  <!-- GROUND_TRUTH: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html §ConsistencyModel -->

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
- [[wiki/work/raw-sensor-file-aggregation/implementation_plan]] — proposed
  runtime/publication contracts, staged delivery, and acceptance-test mapping.
- [[wiki/work/raw-sensor-file-aggregation/verification]] — evidence record;
  runtime and S3 acceptance are not yet executed.
- [[wiki/tension/raw-sensor-compaction-publication-vs-glob-readers]] — multi-key
  publication versus existing recursive consumer globs.

## Libraries And APIs

- DuckDB 2.0.0 `read_parquet`/`COPY` through the selected CLI/runtime: core
  compaction and Parquet write engine requested by the user. The plan recommends
  the Python API with boto3 control operations in an isolated UV package;
  API choice, S3 configuration, and publication require recorded decisions and
  experimental qualification. The user confirmed DuckDB 2.0.0 for processing
  and per-partition `COUNT(*)` equality for development/operational validation;
  see [[wiki/work/raw-sensor-file-aggregation/interview]].
- AWS S3: source and destination object storage; use isolated prefixes for
  tests. Exact credential provider, endpoint compatibility, and publication
  protocol remain open.

## Notes

- Parquet is the input/output interchange boundary. The current plan uses
  DuckDB 2.0.0 for both compaction and verification; the Wintappy dependency and
  SQL references above provide layout context, not a separate cross-version
  compatibility test requirement.
- The output dataset must not contain both source and aggregate files under the
  same `raw_sensor` root that a consumer scans.
- `dayPK`/`hourPK` are used as exact grouping keys; the compactor does not
  derive output partitions from event timestamps.
- The user's desired rule is partitioning by the UTC wall-clock time of actual
  upload. Current source partitions at UTC merge/materialization time and
  retains that relative path across failed-upload retries. The separate TODO
  tracks this gap; no sibling code change is authorized by this feature brief.
