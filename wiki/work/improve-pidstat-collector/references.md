---
title: "Feature References: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - raw/Issues/Long_Running_Cleanup.md
  - ../Lintap/pidstat-collect.sh
  - ../Wintappy/wintap_dbt/dbt_project.yml
  - ../Wintappy/wintap_dbt/macros/paths.sql
  - ../Wintappy/wintap_dbt/macros/raw_sources.sql
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-08-20
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-pidstat-collector/references.md
tags: [feature-work, references, lintap, pidstat]
---

# Feature References: Improve pidstat Collector

## Live Repo Sources

- `../Lintap/pidstat-collect.sh` — current collector: `pidstat -u -d -r -w -h 2`
  piped through `tail`/`grep`/`awk` (prepends a date column, tab-delimited) into
  one timestamped `.csv` under
  `$1 | $PIDSTAT_DATA_PATH | $PIDSTAT_OUTPUT_PATH | $WINTAP_DATA_ROOT/pidstat`.
- `../Lintap/teletap/pidstat.sql`, `../Lintap/teletap/load-pidstat.sql` —
  earlier standalone DuckDB table definition and loader for the same format;
  useful as schema reference and to keep in sync if the format changes.
- `../Wintappy/wintap_dbt/dbt_project.yml` — defines
  `raw_sensor_dataset` from `WINTAP_DBT_RAW_SENSOR_DATASET` with fallback to
  `WINTAP_DBT_DATASET`; pidstat now follows that same shared dataset-root
  contract instead of a pidstat-only env var.
- `../Wintappy/wintap_dbt/macros/paths.sql` — shared raw path builders,
  partition glob narrowing, and `partition_filter()` logic used by pidstat and
  the other raw events.
- `../Wintappy/wintap_dbt/macros/raw_sources.sql` — shared optional-event
  helpers such as `raw_event_exists()`.
- `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` — current
  parquet bronze reader: shared `raw_event_exists('pidstat')`, shared
  partitioned `parquet_scan(...)`, `filename=true`, container columns, and
  typed-empty fallback when no pidstat parquet exists.
- `../Wintappy/wintap_dbt/models/silver/pidstat_metrics.sql` — passthrough of
  bronze; downstream name analyses depend on.
- `../Wintappy/wintap_dbt/README.md` (lines ~30, ~64) — documents
  the canonical `raw_sensor/pidstat` parquet input as an optional raw event.
- `../wintap/wintap/core/etl/load/CacheManager.cs` and
  `../wintap/wintap/core/etl/load/adapters/` (`S3Adapter.cs`,
  `SignedS3UrlAdapter.cs`, `SMBFileShareAdapter.cs`, `base/Uploader.cs`) — the
  sensor's existing upload pipeline for raw_sensor output; candidate ride-along
  path for pidstat S3 push.
- `../wintap/docs-agent/s3-smb-upload-layout-changes.md` — notes on the upload
  layout.

## External Sources

- `pidstat(1)` / sysstat documentation — flag semantics (`-u -d -r -w -h`) and
  interval behavior.
- `proc(5)` — field layouts for `/proc/<pid>/stat` (incl. minflt/majflt,
  delayacct_blkio_ticks, guest_time, starttime), `/proc/<pid>/io`,
  `/proc/<pid>/status`, `/proc/<pid>/schedstat`; the first-party feed behind
  telemetry-source option B (see design.md).
- psutil documentation — evaluated as option C; Linux API lacks page faults,
  guest time, and iodelay, so it cannot fill the bronze schema alone.

## Related Wiki Pages

- [[wiki/work/lintap-process-creation-validation/index]] — the research thread
  whose validation runs already capture pidstat alongside Lintap; notes that
  canonical Lintap source is `../wintap` on the Linux/eBPF branch, not the
  legacy `../Lintap` repo.
- [[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]] —
  the one-hour all-events dataset with pidstat capture (47454 lines/hour) and
  the note that DBT finds pidstat automatically via
  `$WINTAP_DATA_ROOT/pidstat/*.csv`.
- [[wiki/repo/lintap-supporting-repo]] — `../Lintap` repo role and status.
- [[wiki/repo/wintappy-pipeline-repo]] — the DBT/DuckDB consumer side.

## Libraries And APIs

- sysstat/pidstat (host dependency).
- systemd (candidate lifecycle manager on target hosts).
- AWS S3 (`aws` CLI or the sensor's existing .NET S3 adapter).

## Notes

- Motivating issue: `raw/Issues/Long_Running_Cleanup.md` — "Improve
  pidstat-collector.sh [t]o run alongside lintap and push data to S3" to
  understand CPU/memory over time vs. system load; same note records ~8M
  event_store process rows over 10 days and a CPU-growth-with-DB-size
  hypothesis this data should help confirm.
- Observed volume baseline: 47454 pidstat lines in a ~1h quiet Multipass run
  (2s interval), i.e. roughly 1.1M lines/day per idle-ish host before S3
  compression considerations.
- Post-close bugfix, pidstat no longer has a dedicated DBT macro/override; it
  is loaded through the same `raw_sensor_dataset` and partition-window helpers
  as the other optional raw events.
