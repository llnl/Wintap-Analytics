---
title: "Milestone: Improve ETL and QA (2026-08-28 Interim State)"
type: concept
confidence: medium
grounded_by:
  - ../Wintappy/notebooks/wintap_dbt_overview.py
  - ../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/build_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/file_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/network_chart.sql
  - ../Wintappy/wintap_dbt/macros/time.sql
  - ../Wintappy/wintap_dbt/models/schema.yml
policy: agent-editable
last_validated: 2026-08-28
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/milestone-2026-08-28.md
tags: [feature-work, milestone, wintappy, qa, dbt, pidstat]
---

# Milestone: Improve ETL and QA (2026-08-28 Interim State)

## What Landed

- pidstat now has a first-class gold model in Wintappy: `pidstat_process_summary`.
- monitoring queries used by the canonical Marimo QA notebook were moved away
  from accidental raw-backed runtime dependencies and now read the intended
  silver/detail outputs where feasible.
- the canonical Wintappy QA notebook gained a real pidstat exploration surface:
  - selected-metric process/resource chart
  - host filter
  - command substring filter
  - per-process-instance vs aggregate-by-command mode
  - event-volume-by-type correlation chart below the pidstat chart
- mixed-schema `eventtime` handling was hardened so silver models tolerate both
  timestamp-typed and numeric event-time inputs.
- the Wintappy uv workflow was cleaned up enough to recover from a broken local
  `.venv` and stop relying on deprecated `uv run --isolated` invocation.

## What The Current QA Notebook Is Good At

- quickly ranking heavy pidstat series by the selected metric
- collapsing repeated short-lived process families like `setroubleshootd` into a
  single command-level series
- visually comparing process-resource behavior against event volume by family
  over time

## What Is Still Deliberately Rough

- the pidstat and event-volume charts are separate Plotly figures, so they do
  not share truly linked zoom state yet
- `By command` currently uses a `sum` rollup for the selected metric; alternate
  rollup semantics (`average per instance`, `max instance`) remain open
- the event-volume chart is notebook-defined rather than promoted into a named
  DBT monitoring view
- Analytics-side legacy Streamlit/DataQA cleanup has not been tackled yet in
  this feature

## Suggested Next Slice

1. decide whether the event-volume correlation chart should be promoted into a
   dedicated DBT monitoring model
2. decide whether the pidstat/event-volume visuals should be merged into a
   single multi-row Plotly figure for linked zoom
3. continue the broader event-family cleanup and Analytics-side conflict pass
