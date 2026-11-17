---
title: "Feature Brief: Compaction Status Utility"
type: concept
confidence: speculative
grounded_by:
  - streamlit/projects/HostActivity/README.md
  - streamlit/projects/HostActivity/main.py
  - streamlit/projects/HostActivity/partition_status.py
  - wiki/work/dbt-compaction-coordination/design.md
  - wiki/work/compaction-status-utility/design.md
  - wiki/tool/durable-process-entity-manager.md
policy: agent-editable
last_validated: 2026-11-17
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/HostActivity; ../Wintap-PyUtil/wintappy/coordination; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, streamlit, s3, compaction, coordination, status, entity-state]
---

# Feature Brief: Compaction Status Utility

## Problem

The existing HostActivity app displays recent raw S3 activity, but not compacted
history, retained process context, scheduled compaction progress or coordination
state. Operators need to distinguish ordinary backlog, active work and unresolved
recovery without running a DBT build or controlling the writer. Diagnostic load
still needs explicit bounds and same-server impact measurement.

## Confirmed requirements

The human requested this follow-on plan on November 14:

- Extend the existing Streamlit S3 viewer, rather than create an unrelated app.
- Include compacted event data and optional entity-cache data.
- Assume the app runs on the same server as compaction/entity-cache processes.
- Show compaction across all partitions or a selected subset.
- Show current lock-mechanism state and compaction-run history as a simple timeline.
- Suggest related useful capabilities.
- Default to **Live diagnostic** observation without a reader reservation, including
  while compaction/entity publication is in progress; always disclose inconsistent
  observation risk.
- Offer an explicit **Coordinated refresh** for comparisons and validation, using
  the normal qualified reader client. Preserve live-ledger locking, DBT coordination
  and exclusive maintenance/recovery.

The human approved these two read modes and the diagnostic-contract exception on
November 14, then authorized the implementation/review plan on November 15:
Analytics utility work plus scoped native-Mac changes in an isolated PyUtil
worktree. The busy producer worker retains interrupted-publication recovery.
No deployment, cron installation, real-dataset mutation, commit or push is authorized.
<!-- SOURCE: Human implementation approval, conversation 2026-11-15. -->

**Implemented subset:** Activity/Status/Runs/Partitions navigation, pinned bounded
local advisory v1 status, raw intent markers, and a bounded metadata-only
raw/compacted hourly-presence heatmap.
Activity stays synchronous/raw-only with its mandatory Live diagnostic warning.
All 59 offline controls pass; full catalog/timeline, compacted/entity access and
managed live/coordinated lifecycles remain pending. No utility operational acceptance.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/status_source.py; streamlit/projects/HostActivity/status_views.py; streamlit/projects/HostActivity/main.py; wiki/work/compaction-status-utility/verification.md -->

## Goals and recommended first version

| View | User-facing behavior |
|---|---|
| **Status** | Last reported dataset mode, independently observed process-lock availability, active writer/hour, reader reservations, waiting jobs, block reason and oldest eligible backlog hour. Show source and age of every observation. |
| **Partitions** | Dataset-wide catalog summary, filterable by UTC day/hour, event family, optional protocol and processing state; paginated details show raw/compacted inventory, migration/deletion evidence and entity-hour coverage separately. |
| **Run timeline** | One bar/marker per scheduled run, with execution time distinct from the data hour it processed; distinguish verified completion, unresolved failure, active/last-reported intent and missing evidence. Select a run for phase/result/configuration summary. |
| **Activity** | Preserve the inexpensive raw filename-metadata view. Add bounded raw-only, compacted-only and combined Parquet-row views. Optional entity subview shows retained process summaries and bounded host/instance lookup, not extra event rows. |

Status, cached history and live diagnostic data remain inspectable while a writer
is active or a coordinated refresh waits for admission. Only coordinated refreshes
hold reader reservations, for bounded work rather than the lifetime of a browser
tab. Live diagnostics are intentionally outside reader/writer exclusion; they may
observe disappearing objects, raw/compacted overlap and mixed entity generations.
They cannot certify migration, integrity, coverage or a safe dataset state.

## Non-goals

- No dashboard buttons to force-unlock, expire readers, delete data, retry a writer,
  repair checkpoints, replay entities or reopen admissions.
- No new scheduler, distributed locking service, sensor changes, DBT invocation,
  universal event count, silent overlap deduplication or ancestry reconstruction.
- No full historical Parquet scan on launch, automatic all-dataset audit or new
  production deployment. All-partition cataloging must be resumable and bounded.
- No claim that object presence, a checkpoint, an apparently free OS lock or a
  successful CLI exit proves dataset safety, completeness or collector health.
- No alteration of ordinary local-only `make dbt-build` or making entities mandatory.

## Acceptance criteria

1. Status renders during a held writer lock, inaccessible S3 and a pending data
   grant. Missing/stale status is visibly unknown, not interpreted as `OPEN`.
2. Inspection never opens the live ledger without its process lock and never
   initializes it, changes recovery state or releases reservations.
3. Lock availability and reported dataset mode are separate: a free OS lock does
   not clear `BLOCKED` or unresolved writer intent; a busy lock need not mean a
   compactor is running. `GRANTED` includes unpublished reservations.
4. All-partition summaries expose catalog scope, unknown/unobserved scope and
   inventory timestamps. Filters and pagination preserve event/hour/protocol
   detail without silently truncating or scanning the entire dataset on every rerun.
5. Inventory presence, verified migration, verified deletion and entity coverage
   are distinct fields. Replay-overwritten checkpoints cannot erase run history or
   falsely certify raw migration. Hour-level evidence is not presented as per-leaf evidence.
6. Raw, compacted and combined row queries preserve producer-specific timestamps
   and exact bounded counts over successfully read objects, not a point-in-time
   dataset total; raw-plus-compacted overlap is conspicuous. Compacted names are
   never parsed as raw host/collection-time filenames.
7. Entity mode is optional. Enabled inspection checks configured host/namespace
   and authority provenance through a qualified read-only adapter, labels retained
   state as context and keeps snapshot rows out of event totals. Validation scope
   and time are visible. Live checks remain observational even when they pass;
   mixed-generation or incomplete checks are inconclusive, not proof of corruption.
8. Every live result, including cached/exported copies, retains an always-visible
   uncoordinated warning, its mode, roots/window and observation times. A fresh
   reported `OPEN` never removes the warning; stale/missing writer status is unknown,
   not evidence of inactivity. Failed/incomplete reads cannot become zero activity,
   verified corruption or compaction failure. No partial chart is shown as complete.
9. Coordinated LIST/schema/row/entity/checkpoint reads obtain a matching grant
   before touching active roots. Release follows query interruption and full child
   shutdown. Cancellation, failed release delivery and session loss cannot permit
   continued work from a late grant. An unavailable client never silently falls
   back to live mode. Both modes use bounded, supervised jobs and cleanup.
10. Telemetry remains read-only. Live mode needs only data LIST/GET permissions,
    creates no reservations/messages and never publishes authoritative evidence.
    Optional coordinated mode adds only its own request/release/cancellation PUTs;
    the UI does not write grants, status, ledger state or data.
11. Timeline success requires the coordinator's committed completion disposition,
    not reconstructed success from metrics or logs. Missing timestamps remain unknown.
12. Existing offline app tests and new semantic/concurrency/AppTest gates pass;
    an operator-assisted same-server isolated pilot records latency, resource use,
    writer impact and freshness before operational acceptance.

## Related additions worth including

- **Backlog age and throughput:** scheduled eligible hours versus verified
  completed hours, oldest pending hour and recent execution durations; estimates
  are labeled estimates, not guaranteed finish times.
- **Coverage and overlap warnings:** process-bearing hours without compatible
  entity coverage, raw/compacted co-presence, skipped destinations and late raw
  objects observed after a migration receipt.
- **Recovery diagnostics:** aged readers, undelivered grants, pending releases
  known to the client, missing phase/checkpoint evidence and sanitized block reasons.
  Link to operator procedures; do not offer automatic repair.
- **Storage benefit:** recorded source/output object counts and bytes, separately
  from current inventory; never add replayed cumulative entity counts across hours.

Alerting, detailed phase-duration charts and ancestry-quality analytics are later
enhancements, not prerequisites for a useful first status utility.

## Affected areas and dependencies

Analytics owns `streamlit/projects/HostActivity/` and these planning artifacts.
PyUtil owns authoritative coordination, reader lifecycle, phase evidence and
entity validation. Agree its status/export, observational entity-validation adapter
and optional shared-reader interfaces with the active worker before integrating;
sibling changes require explicit authorization.
Wintap sensor code and Lintap packaging are unaffected.

Initial `fe7fcb5` planning and `8ee714c`/`fab647f` reviews are historical. Submitted
PyUtil `123b9d3` implements Linux service/client, advisory status and typed entity
writer/history/clean recovery. The utility consumes only `service.status_page` v1:
no partition inventory, entity disposition history, grant delivery, monotonic
sequence, actual launch/finish or completion certificate is exported. These facts
remain unavailable, not inferred from metrics or CLI exits.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/service.py §status_page; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py; ../Wintap-PyUtil/wintappy/coordination/entity_history.py -->

The accepted `fab647f` Mac baseline and original lockfile failure remain separate.
Native shutdown, actual-S3/resource qualification and broader dcc-02–05 acceptance
are still open. Review [[wiki/work/dbt-compaction-coordination/verification]] and
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]]; successful native
restriction/bootstrap feasibility is not a selected production backend.

## Remaining choices for human/worker review

- Four-view read-only scope is selected; recovery actions remain out. Full view
  functionality is not accepted by the implemented advisory subset.
- Recommended defaults: recent 24-hour partition detail, seven-day timeline,
  existing 12-hour activity queries; all-history catalog remains available by
  pagination. These are separate windows, not a global query-limit increase.
- Current status refresh is manual, with a 180-second presentation-only stale
  threshold. Automatic polling, history retention and producer progress cadence
  still need agreement; data/catalog surveys remain explicit future work.
- Prefer coordinator-owned local status/catalog export plus the existing planned
  S3 advisory summary; confirm deployment read permissions and client import/CLI
  interface. Same server does not imply the same OS account or unlocked access.
- Confirm how much historical catalog is needed before v1 acceptance, its initial
  survey budget, and which entity details operators actually want.

## Test plan and done when

Use [[wiki/work/compaction-status-utility/implementation_plan]] and
[[wiki/work/compaction-status-utility/verification]]. Done means the agreed first
version passes offline and same-server lifecycle gates, limitations are visible,
and durable implemented facts are promoted into
[[wiki/tool/recent-host-activity-dashboard]].

Design: [[wiki/work/compaction-status-utility/design]]. Coordination dependency:
[[wiki/work/dbt-compaction-coordination/implementation_plan]].
