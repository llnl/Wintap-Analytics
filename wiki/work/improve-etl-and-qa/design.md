---
title: "Feature Design: Improve ETL and QA"
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
  - ../Wintappy/wintap_dbt/models/gold/process_uber_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/build_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/process_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/file_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/network_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/perf_chart.sql
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/design.md
tags: [feature-work, design, wintappy, qa, dbt, pidstat]
---

# Feature Design: Improve ETL and QA

## Summary

The feature should treat the current Wintappy DBT stack as two intertwined but
distinct concerns:

1. event-family data modeling: bronze, silver, and gold contracts for process,
   file, network, pidstat, and related detail/summarization paths
2. QA presentation: monitoring/summary/chart models and the canonical Marimo
   dashboard that consume those contracts

The current stack already has useful structure, but it mixes these two concerns
in ways that make the canonical QA path fragile and make pidstat feel bolted on
rather than first-class.

The design direction is therefore:

- define a clearer event-family contract for bronze, silver, and gold
- make pidstat conform to that contract as a normal family
- treat monitoring/QA outputs as consumers of that contract rather than as an
  accidental extension of bronze/raw access patterns
- make Wintappy Marimo the explicit canonical QA surface
- align or de-emphasize Analytics-side legacy QA paths that still assume older
  DB layouts

## Stage 1 Decisions

Recorded 2026-08-27 from the initial contract-decision pass.

### Decision 1: Preserve current canonical silver/gold relation names where they already anchor active QA and wiki contracts

Keep these as the canonical downstream names unless a later design revision has
stronger evidence to change them:

- `process`
- `process_file`
- `process_net_conn`
- `process_summary`
- `process_uber_summary`
- `pidstat_metrics`

Rationale:

- the active Marimo QA notebook already queries these names directly
- the current repo/wiki documentation already treats them as the Wintappy
  canonical outputs
- broad renaming here would mostly create migration churn rather than clarity

Allowed still:

- bronze/staging cleanup
- adding new gold relations, especially for pidstat
- internal reshaping behind those stable downstream names

### Decision 2: Keep monitoring as a distinct cross-family layer, not a replacement for event-family gold

The current monitoring layer remains a valid concept, but its role is narrowed:

- event-family summaries belong in family-owned gold models
- monitoring models remain cross-family QA rollups, row-count views, and chart
  helpers

Implication:

- `build_summary`, `telemetry_event_summary`, and chart models remain monitoring
  outputs
- pidstat should gain its own gold family output instead of living only through
  `perf_chart` and notebook SQL

### Decision 3: Monitoring models should prefer intentional silver/gold inputs over accidental bronze/raw-backed dependencies

Monitoring is allowed to read bronze where there is a conscious QA/debug reason,
but the default rule is:

- silver/gold first
- bronze only when the monitoring purpose genuinely depends on raw-shape detail

Immediate target examples:

- `file_chart` should prefer `process_file` or a family-owned summary contract
  over `stg_raw_process_file`
- `network_chart` should prefer `process_net_conn` or a family-owned summary
  contract over `stg_raw_process_conn_incr`
- the file/network branches of `telemetry_event_summary` should follow the same
  rule

### Decision 4: Do not add broad compatibility aliases for legacy raw-name assumptions

The old Analytics/legacy paths still referencing names like `raw_imageload` or
`raw_process_conn_incr` should not drive the canonical contract.

Default migration strategy:

- update the canonical Wintappy Marimo consumer to the intended contract
- align or explicitly de-emphasize old Analytics-side pages
- only add a temporary alias if a narrow, current, high-value consumer cannot be
  moved in the same slice

Rationale:

- the legacy Python ETL and stdview-era paths are already documented as
  reference/compatibility tooling rather than the primary direction
- broad aliasing would prolong ambiguity about what the canonical DBT contract
  actually is

### Decision 5: First code slice should center on pidstat gold plus monitoring cleanup, not whole-stack renaming

The first implementation slice should deliver visible value while constraining
risk:

- introduce pidstat gold
- rework monitoring models that currently reach back into bronze/raw by accident
- align the Marimo dashboard to the new pidstat and monitoring contract

Defer to later slices:

- larger process/file/network family reshaping when a concrete inconsistency is
  found
- Analytics-side cleanup beyond the most direct conflicts

### Decision 6: Introduce one pidstat family gold model first, keyed as a QA-facing process summary

The first pidstat gold output should be a process-level summary model,
tentatively named `pidstat_process_summary`.

Recommended grouping identity:

- `hostname`
- `container_runtime`
- `container_id`
- `pid_ns_inode`
- `pid`
- `command`

Recommended fields:

- identity/grouping columns above
- `samples`
- `first_seen`
- `last_seen`
- `max_cpu_percent`
- `avg_cpu_percent`
- `max_mem_percent`
- `avg_mem_percent`
- `max_kb_read_per_sec`
- `avg_kb_read_per_sec`
- `max_kb_write_per_sec`
- `avg_kb_write_per_sec`

Purpose:

- give QA a stable family-owned summary relation instead of having the notebook
  invent that contract itself
- avoid collapsing distinct containerized or cross-host PIDs into one row
- keep `pidstat_metrics` as the silver detail source for timeline-like views

### Decision 7: First-slice monitoring rewrites should target summary-style queries, not force a raw-time rewrite where silver does not yet carry the same shape

Recommended first-slice mapping:

- `build_summary`
  - keep existing model counts
  - add `pidstat_process_summary`
- `telemetry_event_summary`
  - process branch stays on `process`
  - file branch moves from `stg_raw_process_file` to `process_file`
  - network branch moves from `stg_raw_process_conn_incr` to `process_conn_incr`
  - performance branch stays on `pidstat_metrics`
- `process_chart`
  - stays on `process`
- `file_chart`
  - moves from `stg_raw_process_file` to `process_file`, using the silver event
    timing fields (`min_event`/`max_event`) as the chart basis
- `network_chart`
  - moves from `stg_raw_process_conn_incr` to `process_conn_incr`, using
    `incr_start` as the chart basis
- `perf_chart`
  - stays on `pidstat_metrics`

Rationale:

- this removes the accidental runtime dependence on raw-backed bronze views for
  the current QA summaries and charts
- it uses intentional silver detail where time-like fields already exist
- it avoids inventing a larger event-time redesign for file/network in the first
  slice

### Decision 8: First-slice Marimo notebook changes should stay query-level and conservative

Recommended notebook changes for the first coding slice:

- keep the existing section layout
- make pidstat availability row-based rather than `table_exists`
- change the pidstat summary and top-process queries to read from
  `pidstat_process_summary`
- keep process/file/network top-activity sections on the current stable
  silver/gold relations unless the monitoring rewrite exposes a better named
  contract in the same slice

## Proposed Approach

### 1. Separate event-family modeling from QA/monitoring presentation

Today, DBT layers already exist in name (`bronze`, `silver`, `gold`,
`monitoring`), but the boundary is inconsistent.

- Bronze models scan raw `raw_sensor` inputs and handle source drift or optional
  sources.
- Silver models normalize detail-level objects used by downstream analysis.
- Gold models summarize some event families, but not all.
- Monitoring views partly summarize silver/gold outputs and partly reach back
  into bronze/raw-backed models.

The intended direction is to make event-family contracts primary and
monitoring/QA contracts secondary:

- Bronze: one raw-facing compatibility layer per event family
- Silver: one normalized detail layer per event family
- Gold: one analyst/QA-facing summary layer per event family where useful
- Monitoring: cross-family rollups/charts that read the intentional event-family
  outputs rather than accidental raw-backed relations

This keeps QA useful without forcing all QA to become gold-only.

### 2. Make pidstat a first-class event family

Pidstat currently has:

- bronze: `stg_pidstat_metrics`
- silver: `pidstat_metrics`
- monitoring: `perf_chart` and the `performance` branch in
  `telemetry_event_summary`

It lacks an intentional gold family layer analogous to the existing
`process_file_summary` and `process_net_summary` patterns.

The design target is:

- bronze pidstat raw-source compatibility remains in one place
- silver pidstat becomes the stable normalized detail table for per-sample or
  per-process-interval performance telemetry
- gold pidstat provides a curated summary contract for QA and downstream
  exploration, instead of making the notebook infer that contract ad hoc

For the first coding slice, that gold contract is `pidstat_process_summary`, a
QA-facing process-level summary keyed by host/container/process identity while
`pidstat_metrics` remains the silver per-sample detail relation.

The exact gold shape is still open, but the important design decision is that it
exists as a first-class family output rather than only as notebook SQL.

### 3. Normalize stage expectations across event families

The feature should not just add pidstat gold in isolation. It should also make
the event-family stage contract more consistent across process, file, network,
and pidstat.

The working stage expectations are:

- Process family
  Event-family detail already lands in `process`; summary already lands in
  `process_summary` and `process_uber_summary`.
- File family
  Detail already lands in `process_file`; summary already lands in
  `process_file_summary`.
- Network family
  Detail already lands in `process_conn_incr` / `process_net_conn`; summary
  already lands in `process_net_summary`.
- pidstat family
  Detail exists in `pidstat_metrics`; summary layer should be introduced and
  named intentionally.

This design does not require every family to have identical naming, but it does
require every family to have an understandable story from bronze through QA.

### 4. Move dashboard dependencies toward intentional outputs

The current Marimo dashboard should be treated as a consumer of the DBT contract,
not as a second place where business logic is invented.

The intended dashboard contract after this feature is:

- event-family sections query named silver/gold/monitoring outputs that are part
  of the canonical DBT contract
- cross-family summary/charts rely on monitoring models that themselves are built
  from intentional event-family outputs
- direct bronze use remains allowed where there is a specific QA/debug reason,
  but it should be explicit rather than accidental

This preserves the user's decision that QA may read bronze while still reducing
the current muddled dependency pattern.

For the first coding slice, the main concrete rewrite is moving summary-style
monitoring and notebook queries off raw-backed bronze views and onto intentional
silver/gold outputs.

### 5. Make Wintappy Marimo canonical, then align or retire legacy conflicts

The old Analytics Streamlit/DataQA path is not the primary target of the
cleanup, but it must stop contradicting the canonical Wintappy QA contract.

The design intent is:

- Wintappy Marimo is the main QA entry point
- Analytics-side legacy pages are either
  - updated where the fix is small and the page remains useful, or
  - explicitly left non-canonical / retired where the legacy assumptions are too
    far from the new stack

This keeps the feature focused while still eliminating the most confusing
cross-repo conflicts.

## Data Model Or Schema Changes

Expected categories of change:

- DBT model additions for pidstat gold
- targeted reshaping across existing process/file/network/pidstat outputs while
  preserving the current canonical downstream silver/gold names unless a later
  design revision explicitly changes that decision
- monitoring model rewrites to depend on intentional silver/gold outputs
- expanded DBT tests in `models/schema.yml`, especially for pidstat

## Interfaces And User Experience

Primary interface:

- `make dbt-build`
- `make dbt-test`
- `make qa-dashboard`

Expected user-visible improvements:

- pidstat appears in QA as a normal family rather than an optional add-on
- dashboard sections reflect a cleaner DBT contract
- QA consumers have a clearer answer to "which models are canonical to query?"
- old conflicting Streamlit assumptions are either corrected or clearly no
  longer canonical

## Edge Cases

- Optional event families remain optional; pidstat must still tolerate missing
  raw parquet and produce a clear QA signal when absent.
- Existing representative datasets may exercise older naming/layout assumptions;
  compatibility decisions need to be made consciously rather than broken by
  accident.
- Some monitoring queries may still need bronze/raw-backed access for QA-only
  debugging; these should be called out explicitly if retained.
- Multi-host or containerized pidstat datasets may need a stronger identity
  contract than `command + pid` at the QA layer.

## Error Handling

- Dashboard sections should distinguish missing/empty optional data from true
  query failures.
- DBT models should keep typed-empty fallbacks only where optionality is part of
  the intended contract.
- Cross-family rollups should avoid hiding dependency failures behind unrelated
  sections when a narrower event-family view would still be valid.

## Risks

- A broad cleanup can sprawl unless stage boundaries stay disciplined.
- Renaming models without a conscious compatibility decision could break
  notebooks or old QA paths in ways that are easy to miss.
- pidstat gold could become a one-off if introduced without applying the same
  reasoning to other event families.
- Monitoring rewrites can accidentally remove useful QA/debug capability if the
  bronze-access cases are not distinguished from accidental coupling.

## Alternatives Considered

### Minimal pidstat-only patch

Rejected because the user explicitly wants all-event-family ETL/QA cleanup, not
just a pidstat visibility fix.

### Gold-only QA rule

Rejected because the user explicitly allowed bronze access for QA when useful.
The design instead distinguishes intentional bronze use from accidental use.

### Analytics-hosted QA as the primary surface

Rejected because the user chose Wintappy Marimo as the canonical QA entry point,
and the current `Makefile`/notebook flow already reflects that direction.

## Open Questions

- Which Analytics Streamlit/DataQA pages are worth aligning versus explicitly
  deprecating?
- Are there any non-pidstat event families whose current silver/gold contract is
  inconsistent enough to justify a later rename despite the default preservation
  decision?
- After the first-slice chart rewrite, is file/network timeline fidelity from
  silver timing fields sufficient, or does a later slice need an explicit
  chart-focused detail contract?
