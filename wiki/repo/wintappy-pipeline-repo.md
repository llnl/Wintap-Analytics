---
title: "Wintappy (Wintap-PyUtil) Pipeline Repository"
type: repo
confidence: high
grounded_by:
  - ../Wintappy/README.md
  - ../Wintappy/pyproject.toml
  - ../Wintappy/review-notes/Architecture.md
  - ../Wintappy/review-notes/DataModel.md
  - ../Wintappy/review-notes/ProjectSummary.md
  - ../Wintappy/review-notes/OpenQuestions.md
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-08-11
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

DBT is now the primary canonical ETL path. The intended flow is sensor `raw_sensor` parquet into `Wintap-PyUtil/wintap_dbt`, into a DuckDB analysis database, into notebooks/SQL/future parquet export. `raw_sensor` is the only canonical post-processing input; the older flat `merged` directory stage is deprecated and removed from the normal pipeline.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Current architectural stance -->
<!-- GROUND_TRUTH: ../Wintappy/review-notes/ProjectSummary.md §Key decisions -->

Component boundaries are explicit in the repo's own review notes: the `wintap` repo owns event collection and raw `raw_sensor` parquet materialization and should not own DBT transformations; `Wintap-PyUtil` (this repo) owns canonical ETL transformations, dependency ordering, and tests; analytics notebooks (Wintap-Analytics) own exploratory analysis and modeling, not canonical ETL; `Lintap/teletap` owns development visualization/scaffolding, not the main pipeline.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Major component boundaries -->

## DBT Model Layers

DBT bronze models own raw-source schema compatibility: they scan `raw_sensor` parquet partitioned by `dayPK`/`hourPK`(/`protoPK` for network), tolerate optional or missing raw sources, and normalize source drift such as synthesizing missing `ProcessArgs` from `CommandLine`.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/DataModel.md §DBT bronze models -->

DBT silver models are the normalized, process-centric detail objects: `host`, `host_ip`, `process`, `process_conn_incr`, `process_net_conn`, `process_file`, `process_registry`, `process_image_load`, `files`, `all_files`, and `process_path`, keyed by `pid_hash` as the primary process entity key used by downstream summaries and labels.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/DataModel.md §DBT silver detail models -->

DBT gold models are analyst-facing summaries: `process_registry_summary`, `process_file_summary`, `process_net_summary`, `process_image_load_summary`, `process_summary`, and `process_uber_summary`. Optional enrichment inputs feeding `process_uber_summary` — labels/networkx, LOLBAS, MITRE, and Sigma — are currently typed empty DBT stubs, not real wired inputs.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/Architecture.md §Gold -->
<!-- GROUND_TRUTH: ../Wintappy/review-notes/OpenQuestions.md §In progress / high priority -->

## pidstat Bronze Input (promoted 2026-08-17)

The pidstat bronze model (`stg_pidstat_metrics`) reads typed parquet from `$WINTAP_DATA_ROOT/parquet/raw_sensor/pidstat/**/*.parquet` via `read_parquet(filename=true)` (`PIDSTAT_DATA_PATH` still overrides), carrying host-performance rows with `hostname` and container-attribution columns (`cgroup_path`, `pid_ns_inode`, `container_runtime`, `container_id`); when no files exist it builds a typed empty table. The former tab-CSV input is retired — bronze is parquet-only, and pre-2026-08 CSV datasets need one-time conversion. Producer side: [[wiki/repo/lintap-supporting-repo]] pidstat collector.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/pidstat.sql; ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql -->

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
