---
title: "To-Do: Define Canonical Process-Owned Network Grains"
type: diagnostic
confidence: medium
grounded_by:
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/DataDictionary.md
policy: agent-editable
last_validated: 2026-11-05
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: mixed
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt/models/silver; ../Wintap-PyUtil/DataDictionary.md
tags: [todo, backlog, network-events, dbt, data-quality, graph-analytics]
---

# To-Do: Define Canonical Process-Owned Network Grains

**Priority:** P2 — Medium (provisional; clarify the contracts before changing
existing outputs).
**State:** Open — intake finding; implementation has not been approved.
**Likely next step:** Review the documented increment key against the actual
silver-model grouping, then propose additive canonical relations and regression
tests that preserve existing consumers.

## Goal

Make process-owned network connections and their time-bucketed activity
consistent, reusable analytical facts rather than requiring each downstream
consumer to regroup source rows independently. Stable grains and explicit
process/connection/peer relationships are particularly useful for graph
analytics, where inconsistent grouping can create duplicate entities, split
edges, or make counter totals vary between projections.
<!-- SYNTHESIS: design motivation based on the documented increment key and current silver-model grains in grounded_by -->

## Finding

The data dictionary documents `process_conn_incr` with the key
`PID_HASH + CONN_ID + INCR_START_SECS`. The current silver model uses `GROUP BY
ALL` after deriving counters and timestamps, so process and endpoint metadata
also participate in its grouping. The intended key and actual grouping should be
reconciled explicitly rather than assuming each output row already has the
documented grain.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/DataDictionary.md §Table: process_conn_incr; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql -->

`process_net_conn` rolls up increments, but retains process name, address
spellings, gateway fields, and other dimensions in its `GROUP BY ALL`. Variants
in those fields can therefore leave multiple rows for what a consumer considers
one process-owned connection. The model also uses `any_value(os_pid)`, so a
selected PID is not evidence that observations agreed on the value.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql -->

The canonical `process` relation is independently built from raw process
observations. Network telemetry can carry a `pid_hash`, observed OS PID, process
name, and network time bounds even when that process identity has no matching
process-sensor row. Those are network observations, not proof of executable,
process-start, or process-termination facts.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql -->
<!-- SYNTHESIS: the process and network relations are independently built; whether unmatched network identities occur depends on the dataset and should be measured -->

## Suggested investigation

1. **Specify increment grain.** Confirm whether `PID_HASH + CONN_ID +
   INCR_START` is the complete key, and document how protocol, host/agent,
   oriented endpoints, and descriptive metadata relate to that key.
2. **Specify connection-summary grain.** Define one reusable process-owned
   connection grain for `process_net_conn` (or an additive companion model).
   Preserve local-versus-remote endpoint orientation and all native TCP/UDP
   measures, but do not make descriptive spellings or gateway metadata split a
   connection unless domain semantics require it.
3. **Expose network-observed process identity distinctly.** If useful across
   consumers, add an explicitly named relation for process identities observed
   through network telemetry. Keep it separate from process-lifecycle facts and
   retain observation bounds/provenance; do not union these rows into `process`
   or infer executable/start/termination attributes.
4. **Make disagreements visible.** Audit multiple OS PIDs, process names,
   hosts/agents, or endpoint values for a proposed key. Avoid resolving
   conflicting identity metadata with an unqualified `any_value` or `min`;
   preserve alternatives, add conflict indicators/counts, or document a
   semantically justified selection rule.
5. **Protect existing consumers.** Prefer additive relations initially, or
   demonstrate compatibility before changing existing silver contracts.

## Verification criteria

- Tests assert uniqueness at each documented grain and measure coverage from
  source observations into the canonical relations.
- TCP/UDP counter totals and first/last observation bounds are preserved by any
  regrouping; null remains distinct from a measured zero.
- Tests expose metadata conflicts for a key instead of silently hiding them.
- Network-observed process identities remain distinguishable from process
  lifecycle records and do not fabricate lifecycle or executable fields.
- Existing summaries and downstream joins are compared before and after any
  change, with compatibility deviations documented.

## Open questions

- Should the existing silver relations change grain, or should a new canonical
  connection/activity pair be added first?
- Which identity dimensions are authoritative when `pid_hash`, `conn_id`, and
  endpoint fields disagree?
- What should downstream consumers receive when one identity key has multiple
  observed OS PIDs or process names: separate observations, conflict metadata,
  or a documented representative value?
- Which process-observation fields are useful outside network analytics without
  implying lifecycle semantics?

## References

- `../Wintap-PyUtil/DataDictionary.md` — documented network increment key and
  field semantics.
- `../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql` — current
  increment aggregation, dimensions, counters, and time bounds.
- `../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql` — current
  connection summary grouping and metadata selection.
- `../Wintap-PyUtil/wintap_dbt/models/silver/process.sql` — process identity
  relation sourced from process observations.

## Disposition

This is a modeling to-do, not authorization to change the schema or existing
DBT outputs. Promote it to a feature-work folder after the grain, compatibility
strategy, and intended consumers are agreed.
