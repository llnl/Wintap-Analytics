---
title: "Wintappy (Wintap-PyUtil) Pipeline Repository"
type: repo
confidence: high
grounded_by:
  - ../Wintappy/README.md
  - ../Wintappy/pyproject.toml
  - ../Wintappy/wintap_dbt/dbt_project.yml
  - ../Wintappy/wintap_dbt/macros/paths.sql
  - ../Wintappy/wintap_dbt/macros/raw_sources.sql
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/models/gold/process_file_summary.sql
  - ../Wintappy/wintap_dbt/models/gold/process_net_summary.sql
  - ../Wintappy/wintap_dbt/models/gold/process_summary.sql
  - ../Wintappy/wintap_dbt/models/schema.yml
  - ../Wintappy/wintap_dbt/macros/time.sql
  - ../Wintappy/review-notes/Architecture.md
  - ../Wintappy/review-notes/DataModel.md
  - ../Wintappy/review-notes/ProjectSummary.md
  - ../Wintappy/review-notes/OpenQuestions.md
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-10-24
repo_scope: Wintappy
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Wintappy/README.md; ../Wintappy/pyproject.toml; ../Wintappy/review-notes; ../Wintappy/wintap_dbt; ../Wintappy/wintappy
tags: [wintappy, wintap-pyutil, dbt, duckdb, etl, data-pipeline, repo]
---

# Wintappy (Wintap-PyUtil) Pipeline Repository

`../Wintappy` is the canonical Python/DBT/DuckDB post-processing repository for Wintap and Lintap telemetry. Its Python package is named `wintappy`; its upstream project name is `Wintap-PyUtil`, described as "Python, DuckDB, and DBT utilities for processing Wintap/Lintap telemetry data."
<!-- GROUND_TRUTH: ../Wintappy/README.md §Wintap-PyUtil -->

Its README carries the same LLNL release identifier, `LLNL-CODE-837816`, that appears in the Wintap-Analytics README, indicating both are registered under the same umbrella LLNL software release even though `pyproject.toml` declares an MIT license for the package itself.
<!-- GROUND_TRUTH: ../Wintappy/README.md §Release -->
<!-- GROUND_TRUTH: ../Wintappy/pyproject.toml §project -->

## Canonical Architecture

### DuckDB maintenance baseline (2026-10-24)

The canonical Python dependency is pinned to DuckDB **1.5.6**; the current
adapter/core tuple remains **dbt-duckdb1.9.6 / dbt-core1.12.2**. The local uv lock
remains intentionally ignored by repo policy; the tracked manifest carries the
engine pin. A fresh full DBT build on retained revision7 AXON drain inputs passed
40 models/42 tests plus its startup hook, retaining collector birth and metadata.
This is dependency validation, not repair of existing data-quality defects or
rollout to installed collectors. See [[wiki/work/duckdb-1-5-maintenance/verification]].
<!-- GROUND_TRUTH: ../Wintappy/pyproject.toml; ../Wintappy/.gitignore; ../Wintappy/uv.lock; wiki/work/duckdb-1-5-maintenance/validation_receipt.json -->

DBT is now the primary canonical ETL path. The intended flow is sensor `raw_sensor` parquet into `Wintap-PyUtil/wintap_dbt`, into a DuckDB analysis database, into notebooks/SQL/future parquet export. `raw_sensor` is the only canonical post-processing input; the older flat `merged` directory stage is deprecated and removed from the normal pipeline.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Current architectural stance -->
<!-- GROUND_TRUTH: ../Wintappy/review-notes/ProjectSummary.md §Key decisions -->

Component boundaries are explicit in the repo's own review notes: the `wintap` repo owns event collection and raw `raw_sensor` parquet materialization and should not own DBT transformations; `Wintap-PyUtil` (this repo) owns canonical ETL transformations, dependency ordering, and tests; analytics notebooks (Wintap-Analytics) own exploratory analysis and modeling, not canonical ETL; `Lintap/teletap` owns development visualization/scaffolding, not the main pipeline.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Major component boundaries -->

## DBT Model Layers

### Integer timestamp precision (2026-10-24 candidate)

FILETIME timestamp/minute macros now use integer epoch subtraction/floor division,
preserving UTC TIMESTAMPTZ output without floating tick loss. Generic integer text
parsing rejects malformed/decimal/scientific/out-of-BIGINT text;raw100ns values and
identity inputs are untouched. Exact raw round-trip requires microsecond-representable
inputs.12fresh full builds recover all12collector births;2,900process lifetimes pass
raw-integer checks. Floating convenience fields/older builder paths remain approximate.
Unordered silver metadata,OS labels and sensor conservation gaps are not fixed here.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/time.sql; ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintappy/tests/test_filetime_precision_sql.py -->
Contract:[[wiki/concept/filetime-derived-timestamp-precision]];
proof:[[wiki/work/host-process-identity-patch/timestamp_and_trace_results]].

DBT bronze models own raw-source schema compatibility: they scan `raw_sensor` parquet partitioned by `dayPK`/`hourPK`(/`protoPK` for network), tolerate optional or missing raw sources, and normalize source drift such as synthesizing missing `ProcessArgs` from `CommandLine`.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/DataModel.md §DBT bronze models -->

For the Linux split-root layout, `WINTAP_DBT_DATASET` defaults directly to
`WINTAP_DATA_ROOT`, so DBT resolves `$WINTAP_DATA_ROOT/raw_sensor/...` rather
than a nested `parquet/` directory.
<!-- GROUND_TRUTH: ../Wintappy/Makefile -->

DBT silver models are the normalized, process-centric detail objects: `host`, `host_ip`, `process`, `process_conn_incr`, `process_net_conn`, `process_file`, `process_registry`, `process_image_load`, `files`, `all_files`, and `process_path`, keyed by `pid_hash` as the primary process entity key used by downstream summaries and labels.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/DataModel.md §DBT silver detail models -->

DBT gold models are analyst-facing summaries: `process_registry_summary`, `process_file_summary`, `process_net_summary`, `process_image_load_summary`, `process_summary`, and `process_uber_summary`. Optional enrichment inputs feeding `process_uber_summary` — labels/networkx, LOLBAS, MITRE, and Sigma — are currently typed empty DBT stubs, not real wired inputs.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Gold -->
<!-- GROUND_TRUTH: ../Wintappy/review-notes/OpenQuestions.md §In progress / high priority -->

### Gold lifetime aggregation correction (2026-10-23 candidate)

Current source groups file/network lifetime summaries only by `pid_hash`, not
mutable process name or agent UUID. Latest observed name/agent is selected with
`arg_max` and a lexical tie-break; this is summary display metadata, not a complete
exec/image timeline. Host display uses `min`; conflicting metadata needs separate QA.
File counters accept case-normalized spelling and include `Open_Events`.
`process_summary` computes full elapsed seconds with `epoch(interval)`, and both
process gold summary models now test lifetime-key uniqueness.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/gold/process_file_summary.sql; ../Wintappy/wintap_dbt/models/gold/process_net_summary.sql; ../Wintappy/wintap_dbt/models/gold/process_summary.sql; ../Wintappy/wintap_dbt/models/schema.yml -->

Regression fixtures and read-only real-sample projections validate these SQL changes;
the original materialized database is unchanged. These corrections neither recover
historical orphan identities nor repair producer receive-byte measurements or OS labels.
<!-- GROUND_TRUTH: ../Wintappy/tests/test_process_gold_quality_sql.py; wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md §historical QA/counters archive members -->

## pidstat Bronze Input (promoted 2026-08-17, patched 2026-08-20)

The pidstat bronze model (`stg_pidstat_metrics`) now behaves like the other optional raw events instead of using a pidstat-only path override. `dbt_project.yml` defines `raw_sensor_dataset` from `WINTAP_DBT_RAW_SENSOR_DATASET` with fallback to `WINTAP_DBT_DATASET`; the shared raw-source helpers build `<raw_sensor_dataset>/raw_sensor/pidstat/...` globs and existence checks from that root. `stg_pidstat_metrics` uses those shared helpers (`raw_event_exists('pidstat')`, `raw_sensor_partition_globs_sql('pidstat')`, and `partition_filter()`), so pidstat now respects the same dataset-root split-I/O/S3 configuration and the same day/hour partition narrowing as models such as `stg_raw_host`.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/dbt_project.yml §vars -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/paths.sql §raw_sensor_dataset_path/raw_sensor_path/raw_sensor_partition_globs_sql/partition_filter -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/raw_sources.sql §raw_event_exists -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql §model -->

The dedicated `PIDSTAT_DATA_PATH` override and `wintap_dbt/macros/pidstat.sql` helper were removed in that follow-up bugfix, so pidstat is now just another canonical optional `raw_sensor` event. It still carries `hostname` and container-attribution columns (`cgroup_path`, `pid_ns_inode`, `container_runtime`, `container_id`), and it still builds a typed empty table when no pidstat parquet exists. The former tab-CSV input remains retired; bronze is parquet-only, and pre-2026-08 CSV datasets still need one-time conversion. Producer side: [[wiki/repo/lintap-supporting-repo]] pidstat collector.
<!-- GROUND_TRUTH: ../Wintappy/Makefile §dbt vars -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/README.md §Configuration -->
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql §typed empty fallback -->

## Legacy Python ETL

Pre-DBT Python/DuckDB console commands (`rawtorolling`, `rawtostdview`, `ubersummary`) remain installed as package entry points and are explicitly kept only "as legacy/reference tooling while the DBT path is hardened"; the README instructs new work to use DBT instead.
<!-- GROUND_TRUTH: ../Wintappy/README.md §Legacy Python ETL commands -->
<!-- GROUND_TRUTH: ../Wintappy/pyproject.toml §project.scripts -->

## Code Dependency From Wintap-Analytics

Wintap-Analytics does not just consume Wintappy's *output* files — its Streamlit apps import the `wintappy` Python package directly. `streamlit/projects/common/dqautil.py` imports `wintappy.datautils.rawutil`, and `streamlit/projects/DataQA/pages/raw_events.py` imports `wintappy.datautils.stdview_duckdb`. This makes `wintappy` a runtime code dependency of Wintap-Analytics' DataQA/eda tooling, not merely a producer of data those tools happen to read.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/common/dqautil.py §import wintappy.datautils.rawutil -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py §import wintappy.datautils.stdview_duckdb -->

## Known Limitations

DBT parquet export is not implemented yet; DuckDB is the current official output, even though some notebooks and published workflows still expect `stdview-*` parquet directories. See [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]] for the resulting cross-repo tension.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/OpenQuestions.md §2. Implement DBT parquet export -->

Optional enrichment sources (labels, LOLBAS, MITRE, Sigma) are not fully wired into DBT; current gold models are typed empty stubs pending real input loading.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/ImplementationStatus.md §Current limitations -->

## Wiki Boundary

Wintappy pages should document the DBT bronze/silver/gold pipeline, its `raw_sensor` input contract, and its role as the canonical post-processing engine. Do not treat Wintappy as a source for sensor/collector semantics (that belongs to [[wiki/repo/wintap-primary-sensor-repo]]) or for exploratory analysis workflows (that belongs to [[wiki/repo/wintap-analytics-host-repo]]).
<!-- SYNTHESIS: inferred from ../Wintappy/review-notes/Architecture.md and ../Wintap-Analytics/AGENTS.md -->

See also [[wiki/repo/wintap-primary-sensor-repo]], [[wiki/repo/wintap-analytics-host-repo]], [[wiki/repo/lintap-supporting-repo]], [[wiki/workflow/future-experiment-analysis-workflows]], and [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]].
