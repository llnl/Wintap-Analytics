---
title: "Feature References: Improve ETL and QA"
type: concept
confidence: medium
grounded_by:
  - ../Wintappy/Makefile
  - ../Wintappy/notebooks/wintap_dbt_overview.py
  - ../Wintappy/wintap_dbt/dbt_project.yml
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/models/silver/process.sql
  - ../Wintappy/wintap_dbt/models/silver/process_file.sql
  - ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintappy/wintap_dbt/models/silver/process_net_conn.sql
  - ../Wintappy/wintap_dbt/models/silver/pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/models/monitoring/build_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/process_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/file_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/network_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/perf_chart.sql
  - ../Wintappy/wintap_dbt/models/schema.yml
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/references.md
tags: [feature-work, references, wintappy, qa, dbt]
---

# Feature References: Improve ETL and QA

## Live Repo Sources

- `../Wintappy/Makefile` — canonical commands: `dbt-build`, `dbt-test`, `qa-dashboard`, and the current legacy `qa-pidstat` target.
- `../Wintappy/notebooks/wintap_dbt_overview.py` — current Marimo QA notebook and the concrete query contract it expects from the built DuckDB.
- `../Wintappy/wintap_dbt/dbt_project.yml` — DBT project structure and current materialization policy: bronze views, silver tables, gold tables, monitoring views.
- `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` — current pidstat bronze model using the shared raw-event helpers and typed-empty fallback.
- `../Wintappy/wintap_dbt/models/silver/pidstat_metrics.sql` — current pidstat silver passthrough.
- `../Wintappy/wintap_dbt/models/silver/process.sql` — process-centric silver contract.
- `../Wintappy/wintap_dbt/models/silver/process_file.sql` — file-event silver contract.
- `../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql` and `../Wintappy/wintap_dbt/models/silver/process_net_conn.sql` — network-event silver contracts.
- `../Wintappy/wintap_dbt/models/monitoring/build_summary.sql` — current QA row-count rollup.
- `../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql` — event-family summary rollup, currently mixing silver and bronze/raw-backed sources.
- `../Wintappy/wintap_dbt/models/monitoring/process_chart.sql`, `file_chart.sql`, `network_chart.sql`, `perf_chart.sql` — current chart sources for the Marimo QA notebook.
- `../Wintappy/wintap_dbt/models/schema.yml` — current DBT test coverage, which is light on pidstat and focused mainly on existing process/file/network contracts.
- `../Wintap-Analytics/streamlit/projects/common/dqautil.py` and `../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py` — older Analytics-side QA path with direct Wintappy dependency and legacy assumptions.

## Related Wiki Pages

- [[wiki/repo/wintappy-pipeline-repo]] — canonical Wintappy repo orientation and current DBT-layer summary.
- [[wiki/work/improve-pidstat-collector/brief]] — closed producer-side pidstat feature with the post-close note that pidstat is now just another canonical raw event.
- [[wiki/work/improve-pidstat-collector/references]] — earlier pidstat-specific source map, especially useful for raw-event and historical path context.
- [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]] — broader compatibility tension between the DBT/DuckDB path and older published-data assumptions.
- [[wiki/workflow/future-experiment-analysis-workflows]] — Analytics-side context for downstream QA and analysis expectations.

## Notes

- Current QA split discovered during feature start: the Wintappy Marimo dashboard is the active canonical QA surface, but this repo still carries older Streamlit/DataQA code paths that can conflict with the current DBT model layout.
- Current runtime split discovered during feature start: some Marimo notebook sections succeed against the built DuckDB alone, while others still require raw-source access because certain monitoring views depend on raw-backed bronze models.
- Current pidstat state discovered during feature start: pidstat already has bronze/silver models, but no intentional gold layer and no current first-class QA presentation contract.
- Current design opening: this feature is intentionally broader than a pidstat fix. The target is to rationalize the event-family ETL and QA contract across process, file, network, pidstat, and monitoring outputs.
