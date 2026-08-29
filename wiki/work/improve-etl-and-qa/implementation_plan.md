---
title: "Implementation Plan: Improve ETL and QA"
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
  - ../Wintappy/wintap_dbt/models/gold/process_summary.sql
  - ../Wintappy/wintap_dbt/models/gold/process_file_summary.sql
  - ../Wintappy/wintap_dbt/models/gold/process_net_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/build_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/process_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/file_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/network_chart.sql
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-08-29
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/implementation_plan.md
tags: [feature-work, plan, wintappy, qa, dbt, pidstat]
---

# Implementation Plan: Improve ETL and QA

## Scope

This plan stages the work so the feature can deliver a cleaner canonical ETL/QA
contract without trying to redesign every historical query path at once.

Center of gravity:

- `../Wintappy/wintap_dbt`
- `../Wintappy/notebooks/wintap_dbt_overview.py`

Secondary cleanup surface:

- legacy Analytics-side Streamlit/DataQA paths in this repo where they directly
  conflict with the canonical Wintappy QA contract

## Steps

1. Stage 1: Inventory and contract decision pass

- Done 2026-08-27 in `design.md`.
- Decided: preserve the current canonical downstream silver/gold names used by
  Marimo/wiki contracts (`process`, `process_file`, `process_net_conn`,
  `process_summary`, `process_uber_summary`, `pidstat_metrics`).
- Decided: keep monitoring as a distinct cross-family QA layer, but make it a
  consumer of intentional family outputs rather than accidental bronze/raw
  dependencies.
- Decided: do not add broad compatibility aliases for legacy raw-name
  assumptions; only add a narrow temporary alias if a current high-value
  consumer cannot move in the same slice.
- Decided: first code slice centers on pidstat gold plus monitoring cleanup and
  Marimo alignment, not whole-stack renaming.

2. Stage 2: pidstat first-class family implementation

- Keep or refine the current pidstat bronze model as the canonical raw-facing
  compatibility layer.
- Keep or refine `pidstat_metrics` as the normalized silver detail model.
- Introduce `pidstat_process_summary` as the first intentional pidstat gold
  model for QA-facing process summary use.
- Add/update DBT tests for pidstat bronze/silver/gold expectations.

3. Stage 3: event-family contract cleanup across existing families

- Apply the same stage reasoning across process, file, and network outputs.
- Rename or reshape existing models where needed to make the family contract
  clearer and more consistent.
- Update downstream refs so the family contract is explicit.

4. Stage 4: monitoring/QA model cleanup

- Rewrite monitoring models so they consume intentional family outputs rather
  than accidental raw-backed dependencies, except where bronze access is a
  conscious QA/debug choice.
- Revisit `build_summary`, `telemetry_event_summary`, and the chart models in
  light of the new family contracts.

First-slice target mapping:

- `build_summary`: add `pidstat_process_summary`
- `telemetry_event_summary`: file -> `process_file`, network ->
  `process_conn_incr`, performance stays on `pidstat_metrics`
- `file_chart`: move to `process_file`
- `network_chart`: move to `process_conn_incr`
- `perf_chart`: keep on `pidstat_metrics`

5. Stage 5: Marimo QA dashboard alignment

- Update `notebooks/wintap_dbt_overview.py` to use the new canonical contract.
- Make pidstat presentation first-class.
- Improve empty/missing-data signaling where optional event families are absent.

First-slice target notebook changes:

- pidstat availability from row count, not table existence
- pidstat summary query from `pidstat_process_summary`
- top pidstat query from `pidstat_process_summary`

6. Stage 6: Analytics-side conflict cleanup

- Inspect legacy Streamlit/DataQA pages that directly depend on Wintappy or old
  DB assumptions.
- Fix small high-value mismatches.
- Explicitly document or de-emphasize the paths that should no longer be treated
  as canonical.

7. Stage 7: verification and canonical promotion

- Run the chosen reproducible local build/test flow.
- Smoke the canonical QA dashboard against the built DuckDB.
- Record commands/results in `verification.md`.
- Promote durable facts about the final ETL/QA contract into canonical wiki
  pages.

8. Stage 8: Lintap memory-growth instrumentation

- Use the current pidstat/event-volume evidence as the baseline symptom view.
- First implement manual batch-mode capture in this repo so command choice,
  schema, and overhead can be tuned quickly.
- Add `/proc/<pid>/smaps_rollup` sampling for the `Lintap` PID.
- Add .NET runtime counter capture for the `Lintap` process.
- Add periodic internal queue/cache/backlog counters, starting with the file
  pipeline and serializer path.
- Write those streams as raw-style parquet event types so later promotion to
  long-term sidecar collection does not require a storage-contract rewrite.
- Extend QA views so memory-growth diagnosis can compare RSS/heap/backlog/event
  volume over the same time windows.

## Recommended First Implementation Slice

Stage 2 + Stage 4 + Stage 5 as one coherent first coding pass:

- add pidstat gold model(s)
- rewrite file/network/performance monitoring queries onto intentional
  silver/gold inputs where possible
- align the Marimo dashboard to the resulting canonical contract

Concrete file set for this slice:

- `../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql` (new)
- `../Wintappy/wintap_dbt/models/monitoring/build_summary.sql`
- `../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql`
- `../Wintappy/wintap_dbt/models/monitoring/file_chart.sql`
- `../Wintappy/wintap_dbt/models/monitoring/network_chart.sql`
- `../Wintappy/notebooks/wintap_dbt_overview.py`
- `../Wintappy/wintap_dbt/models/schema.yml`

Why this slice first:

- it gives the user-visible pidstat improvement quickly
- it removes the most obvious accidental raw-backed monitoring dependencies
- it avoids unnecessary broad renaming before the contract is proven useful

## Files Likely To Change

- `../Wintappy/wintap_dbt/models/bronze/*.sql`
- `../Wintappy/wintap_dbt/models/silver/*.sql`
- `../Wintappy/wintap_dbt/models/gold/*.sql`
- `../Wintappy/wintap_dbt/models/monitoring/*.sql`
- `../Wintappy/wintap_dbt/models/schema.yml`
- `../Wintappy/notebooks/wintap_dbt_overview.py`
- `../Wintappy/Makefile`
- `streamlit/projects/common/dqautil.py`
- `streamlit/projects/DataQA/pages/*.py`
- instrumentation/ or diagnostics paths in the runtime repo once the collection
  approach is selected

## Tests To Add Or Update

- DBT schema tests for pidstat bronze/silver/gold models.
- DBT tests updated for any renamed or reshaped process/file/network contracts.
- Query smoke checks for the canonical Marimo dashboard.
- Focused regression checks for any Analytics-side legacy pages that remain in
  use.
- Longer-run validation for the new memory-growth instrumentation streams and
  their alignment with pidstat/event-volume windows.

First-slice minimum verification:

- `make dbt-build`
- `make dbt-test`
- query smoke for `pidstat_process_summary`, `telemetry_event_summary`,
  `file_chart`, `network_chart`, and the pidstat notebook queries against the
  built DuckDB

## Migration Or Compatibility Notes

- Default compatibility strategy: preserve the current canonical downstream
  silver/gold names and update consumers behind them.
- Do not add broad aliases for legacy raw-name assumptions from old Analytics or
  stdview-era paths.
- Current representative `raw_sensor` datasets should continue to build unless a
  documented design decision says otherwise.

## Rollback Plan

- Keep changes staged by family/consumer boundary so a problematic rename or QA
  refactor can be reverted without losing unrelated cleanup.
- Avoid mixing contract changes, dashboard rewrites, and legacy Streamlit cleanup
  into one unreviewable patch.

## Done Checklist

- [x] Stage 1 contract decisions recorded in `design.md`
- [x] Stage 2 pidstat bronze/silver/gold path implemented
- [ ] Stage 3 process/file/network family contracts cleaned up as needed
- [x] Stage 4 monitoring outputs aligned to the family contracts
- [x] Stage 5 Marimo QA dashboard aligned to the canonical contract
- [ ] Stage 6 Analytics-side conflicts aligned, retired, or explicitly marked
- [x] Reproducible `dbt build` and `dbt test` verification recorded
- [x] Dashboard smoke verification recorded
- [x] Stage 8 Lintap memory-growth instrumentation planned and manual-batch tooling implemented
- [ ] Durable facts promoted into canonical wiki pages
