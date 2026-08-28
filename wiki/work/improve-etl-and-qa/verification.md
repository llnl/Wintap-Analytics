---
title: "Verification: Improve ETL and QA"
type: concept
confidence: medium
grounded_by:
  - ../Wintappy/Makefile
  - ../Wintappy/notebooks/wintap_dbt_overview.py
  - ../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/build_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/file_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/network_chart.sql
  - ../Wintappy/wintap_dbt/models/schema.yml
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/verification.md
tags: [feature-work, verification, wintappy, qa, dbt, pidstat]
---

# Verification: Improve ETL and QA

## Test Commands

1. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && make dbt-build`
2. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && make dbt-test`
3. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --isolated --dev --project . python - <<'PY' ... query smoke for build_summary, telemetry_event_summary, file_chart, network_chart, perf_chart, pidstat_process_summary, and the notebook's pidstat summary/top queries ... PY`
4. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --isolated --dev --project . python - <<'PY' ... verify the notebook availability expression against an empty pidstat_process_summary result ... PY`
5. `source "wintap-run.env" && export WINTAP_DBT_DATASET="${WINTAP_DBT_DATASET:-$WINTAP_DATA_ROOT/parquet}" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --isolated --dev --project . dbt run --project-dir wintap_dbt --profiles-dir wintap_dbt --select process_registry host host_ip process_file process_image_load process_registry_summary process_file_summary process_summary build_summary`
6. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && make dbt-build`
7. `ls -la .venv && make rebuild-venv && uv run --dev --project . python -c "import plotly, marimo; print(plotly.__version__)"`
8. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the new pidstat time-series query (1-minute buckets, peak CPU threshold 25, top 12 processes) and inspect row count / elapsed time ... PY`
9. `uv run --dev --project . python -m py_compile notebooks/wintap_dbt_overview.py`
10. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the revised pidstat time-series query using selected-metric ranking/filtering (example: Memory %, threshold 0.1) and inspect row count / elapsed time ... PY`
11. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the new event-volume-by-type query (1-minute buckets across process/file/network/registry/image_load) and inspect row count / elapsed time ... PY`
12. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the new 'By command' pidstat aggregation query for command='setroubleshootd' and inspect row count, series count, and concurrent PID behavior ... PY`
13. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the command-filtered 'Aggregate by command' pidstat query for command contains 'setroubleshootd' and inspect row count, series count, and elapsed time ... PY`

## Manual Checks

- Confirmed that the new DBT gold model `pidstat_process_summary` builds and is included in the schema tests.
- Confirmed that `build_summary`, `telemetry_event_summary`, `file_chart`, and `network_chart` now query successfully against the built DuckDB without first creating the DBT raw-source S3 secret in the direct DuckDB session.
- Confirmed that the Marimo notebook's pidstat availability check no longer relies on mere table existence and handles an empty pidstat dataset without raising a conversion error.
- Confirmed that the registry-model failure caused by mixed `eventtime` types is fixed by the new mixed-schema time macros, and that the same tolerance now covers the analogous host, host_ip, process_file, and process_image_load silver conversions.
- Confirmed that the repo-level uv cleanup works: removing the deprecated `--isolated` Makefile usage, adding `plotly` to dev dependencies for `qa-pidstat`, and rebuilding a broken local `.venv` restores normal `uv run --dev --project . ...` behavior.
- Confirmed that the new pidstat time-series query shape is viable on the current dataset: 1-minute bucketed aggregation over the filtered top processes returned `2811` rows across `12` series in `0.46s`.
- Confirmed that the updated Marimo notebook file compiles cleanly with `python -m py_compile`.
- Confirmed that the revised Plotly-based pidstat panel query shape is also viable when ranking by the selected metric rather than always by CPU; an example Memory % query returned `5845` rows in `0.35s`.
- Confirmed that the new event-volume-by-type comparison query is viable on the current dataset: `5024` rows in `0.33s`, with active series for `process`, `file`, `network`, and `registry` on this dataset.
- Confirmed that the new `By command` aggregation mode behaves as intended for repeated-instance families like `setroubleshootd`: the command-level query returned `380` rows in `0.27s`, collapsed to `1` visible series with concurrent-PID counts preserved per bucket.
- Confirmed that the command substring filter works with aggregation mode: filtering for `setroubleshootd` still returns the expected single command-family series (`380` rows in `0.27s`).

## Results

- `make dbt-build` passed: `PASS=78 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=78`.
- `make dbt-test` passed: `PASS=39 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=39`.
- Direct built-DuckDB query smoke succeeded for:
  - `build_summary`
  - `telemetry_event_summary`
  - `file_chart`
  - `network_chart`
  - `perf_chart`
  - `pidstat_process_summary`
  - the notebook's pidstat summary query
  - the notebook's top-pidstat query
- Current smoke dataset results:
  - `pidstat_metrics` rows: `0`
  - `pidstat_process_summary` rows: `0`
  - `perf_chart` rows: `0`
  - `file_chart` rows: `901`
  - `network_chart` rows: `234`
- This confirms the first-slice structural cleanup is working, including the key runtime improvement: the canonical QA monitoring queries no longer require raw-backed bronze/S3 access just to open the built DuckDB and query the monitoring layer.
- Follow-up hotfix result: a direct targeted `dbt run` of `process_registry` and related dependent models now succeeds where it previously failed with `Conversion Error: Unimplemented type for cast (TIMESTAMP -> BIGINT) when casting from source column EventTime`.
- Full `make dbt-build` re-run after the hotfix also passed successfully in `129.86s` with `PASS=78 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=78`.
- uv environment recovery result: `.venv/bin/` had been empty, so `uv add` and other project-environment commands were failing. After `make rebuild-venv`, `uv sync --all-extras --dev` completed successfully and `uv run --dev --project . python -c "import plotly, marimo"` passed (`plotly==7.0.0`).
- Pidstat time-series proof point: with real pidstat rows now present, the filtered query backing the new chart returned `2811` bucketed rows for the top `12` process series at a `25%` peak-CPU cutoff. Example high-signal series included `spk16 | Lintap | 743557` with sustained CPU values over the bucketed window.
- Pidstat UX follow-up: the notebook now uses Plotly for the pidstat time-series panel, ranks and filters processes by the selected metric rather than always by peak CPU, adds a host filter, and exposes a range slider for full-width interactive exploration.
- Correlation view added: the pidstat section now includes a second Plotly chart showing 1-minute event counts by type over time from the normalized event-family tables, intended for visual comparison against the pidstat process-resource chart.
- Aggregation-mode follow-up: the pidstat chart now supports both `Per process` and `By command` views. For `setroubleshootd` on the current dataset, command aggregation produces a clean family-level series while still exposing concurrent PID counts in hover.
- Polish follow-up: the pidstat control row now exposes clearer labels (`Per process instance`, `Aggregate by command`) plus a `Command contains` filter, and the event-volume subplot stack now uses a bottom-axis range slider so its time-navigation behavior is closer to the pidstat chart above.

## Known Gaps

- The current configured dataset/window still contains no pidstat parquet, so the new pidstat gold path is structurally verified but not yet validated with non-empty pidstat data.
- `file_chart` now buckets on `process_file.min_event` as a first-slice silver-based replacement for raw file-event timing. This removes the raw-backed dependency, but timeline fidelity versus raw file event times remains a follow-up question.
- Legacy Analytics-side Streamlit/DataQA alignment is not part of this first coding slice yet.
- The mixed-schema time hotfix has only been validated through DBT execution on the current dataset mix; there is not yet a dedicated model-level regression test specifically for timestamp-typed versus numeric-typed `eventtime` inputs.
- `qa-pidstat` still points at the legacy `../Lintap/teletap/grokdata_marimo.py` path; the uv cleanup makes its dependency resolution saner, but that target remains legacy-oriented rather than part of the canonical Marimo QA flow.
- The new pidstat chart is intentionally simple: one metric at a time, 1-minute buckets, filtered by minimum peak CPU and capped by max series count. It does not yet include richer focusing tools such as legend-based hiding, host/container selectors, or anomaly-centric ranking.
- The chart is still intentionally first-pass despite the UX upgrade: it supports host filtering, command substring filtering, and selected-metric ranking now, but still lacks container-only toggles and explicit anomaly-focused ranking modes.
- `By command` aggregation currently sums the selected metric across matching processes within a bucket. That is useful for total family footprint, but future UX may also want `average per instance` or `max instance` aggregation modes.
- The event-volume chart currently uses one normalized count strategy per event family (`num_process_start + num_process_stop`, `event_count`, `total_events`, etc.). If a stricter cross-family notion of "event volume" is needed later, that definition should be made explicit and possibly promoted into a dedicated monitoring model.
- The pidstat and event-volume charts still do not share truly linked zoom because they remain separate Plotly figures; the current improvement is comparable interaction style rather than synchronized navigation.

## Follow-Ups

- Re-run the same verification against a dataset/window with actual `raw_sensor/pidstat` parquet so `pidstat_metrics`, `pidstat_process_summary`, and `perf_chart` are exercised with non-empty data.
- Consider a second iteration on the pidstat chart UX: container-only narrowing, alternate bucket sizes, or anomaly-focused ranking modes beyond the current peak-selected-metric rule.
- Consider whether `By command` should grow additional aggregation styles (`sum`, `average`, `max`) now that the basic family-level series pattern is validated.
- Consider whether the event-volume correlation chart should stay notebook-only or be promoted into a named monitoring view if it becomes a stable QA concept.
- If linked navigation becomes important, consider collapsing the two charts into a single multi-row Plotly subplot figure so zoom/pan is naturally shared.
- Decide whether `file_chart` and possibly `network_chart` need a later chart-specific detail contract for higher-fidelity timelines.
- Continue with the later feature slices: broader event-family cleanup and Analytics-side conflict handling.
