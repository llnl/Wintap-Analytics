---
title: "Feature Design: Compaction Status Utility"
type: concept
confidence: speculative
grounded_by:
  - streamlit/projects/HostActivity/s3_source.py
  - streamlit/projects/HostActivity/partition_status.py
  - streamlit/projects/HostActivity/queries.py
  - streamlit/projects/HostActivity/file_metadata.py
  - streamlit/projects/HostActivity/pyproject.toml
  - streamlit/projects/HostActivity/status_source.py
  - streamlit/projects/HostActivity/status_views.py
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/protocol.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/config.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/inventory.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py
  - wiki/work/dbt-compaction-coordination/design.md
policy: agent-editable
last_validated: 2026-11-17
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/HostActivity; ../Wintap-PyUtil/wintappy/coordination; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, streamlit, compaction, coordination, status, partition-catalog, entity-state]
---

# Feature Design: Compaction Status Utility

## Summary

Extend HostActivity with a small operational surface. Separate **published status**,
default **Live diagnostic** reads without reservations and optional **Coordinated
refresh** reads of mutable shared data. Use the same-server assumption to read
compact local summaries rather than repeatedly query S3 or open the coordinator
database. The human approved both read modes and the scoped diagnostic exception
on November 14; the November 15 implementation plan is also authorized. Production
dependency selection, unavailable producer interfaces and operational acceptance
remain separate gates.

The full design below remains proposed except for the implemented subset described
next. Do not confuse recommended fields with the actual producer v1 schema.
Requirements: [[wiki/work/compaction-status-utility/brief]].

### Implemented advisory subset — November 17

`status_source.py` consumes the existing `service.status_page` v1 local export;
it never opens DuckDB, the ledger/process lock, transport or data roots. Deployment
must pin the full canonical binding SHA-256 and ledger identity. Reads are manual,
bounded to 1 MiB/100 records per kind, regular-file-only and final-symlink refusing;
strict schema/duplicate/nonfinite JSON, identity, page order and timestamp checks
fail to sanitized unavailable. Stale observation (over 180 seconds) stays visible.
Timestamp rollback is refused within the pinned session, but v1 has no sequence
and cannot establish same-second or whole-session rollback protection.

Status renders reported mode/cursor/owner/reserved/queued summaries only. Roots,
authority payloads and free-form diagnostics are withheld. Runs exposes sorted
raw intent markers and reported disposition, not measured execution bars or
completion certificates; continuations stay incomplete rather than opening the
ledger. Partitions now provides a bounded raw/compacted hourly-presence heatmap;
the full catalog, lock observation, delivery, progress, actual launch/finish,
entity-only history and inventory remain unknown.
Activity remains synchronous/raw-only and visibly Live diagnostic; managed jobs,
compacted/entity access and coordinated refresh are not integrated.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/status_source.py §read_snapshot/_read/_validate; streamlit/projects/HostActivity/status_views.py §render; streamlit/projects/HostActivity/main.py §main; ../Wintap-PyUtil/wintappy/coordination/service.py §status_page/export_status -->

## Current source constraints

| Inspected behavior | Design consequence |
|---|---|
| HostActivity resolves only a raw dataset root; discovery and row queries are capped at 12 hours. | Add compacted/entity configuration explicitly; keep long status-history browsing separate from bounded activity scans. |
| Raw metadata parses `hostname+event_type+FILETIME.parquet`. Compaction preserves partition/row semantics, not original filenames. | Keep raw filename charts distinct. Use partition inventory for compacted metadata and row-level host/time for compacted activity. |
| App and main coordination runtime pin DuckDB 1.5.6; compactor is isolated at 2.0.0. | Do not import compactor writer code into the app or use its runtime to open the ledger. |
| `Ledger.open` takes the persistent lock and calls `_block_unresolved_writer`. | It is not a side-effect-free dashboard reader. A SELECT after calling it can already have mutated recovery state. |
| Submitted PyUtil `123b9d3` has Linux service/client, default v4 plus explicit v5, raw completion and typed entity history; status v1 exports bounded raw dispositions only. | Consume the existing advisory subset; qualify additional history/certificate/catalog interfaces before extending the app. |
| Metrics v4 are fixed one-row hourly objects and can be overwritten by entity replay; status can mean coverage despite deletion errors. | Separate coverage from immutable migration history and coordinator disposition. |
| Phase archives preserve checksummed sequence/lineage, but have no uniform phase timestamp field. | Existing records establish order, not measured phase duration. Do not invent timestamps from file modification times. |

<!-- GROUND_TRUTH: streamlit/projects/HostActivity/s3_source.py §load_settings/partition_hours/discover_object_metadata; streamlit/projects/HostActivity/file_metadata.py §parse_file_metadata; streamlit/projects/HostActivity/queries.py §aggregate_family; streamlit/projects/HostActivity/pyproject.toml -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §SCHEMA/open/_block_unresolved_writer; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows/ProcessingMetricsStore; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §RunEvidence.append/load_archive -->

## Proposed approach

### 1. A status plane that never grants access

The coordinator publishes a bounded, versioned local advisory snapshot alongside
its ledger in the private state directory, separate from telemetry roots. The
existing service exports after raw intent COMMIT/before launch and service
transitions. The richer recommended interface would additionally expose verified
disposition and progress from its existing
supervision path without starting another ledger-opening process. Atomic local
replacement avoids half-written JSON. The planned S3 `status.json` may mirror
the summary, but the app's default status path is local.

Recommended summary fields:

- Dataset/binding fingerprint, ledger identity, schema version and monotonic
  snapshot sequence within that identity.
- Producer observation time and last committed-transition time; app retrieval
  time is separate. Progress observation and tick observation are separate when
  available. A re-read does not make an old snapshot fresh.
- Last reported `OPEN`, `DRAINING`, `WRITING` or `BLOCKED`; active coordinator/CLI
  run IDs, data hour, sanitized phase/block reason and configuration-receipt identity.
- Reader-reservation and queued-job counts; bounded job details distinguish
  reservation from grant delivery and show age, action and requested window.
- Scheduling cursor, configured grace, eligible backlog-hour count, last verified
  completion and catalog/history generation identities.

Publish committed facts, not guesses from S3 message counts or child exit zero.
Fresh snapshots are still advisory. Unknown schema, wrong binding, sequence
rollback, missing files, corrupt JSON or stale observations render explicit
unavailable/stale status; they never authorize coordinated telemetry queries or
prove that live observations are consistent.

A separate optional engine-owned helper may nonblockingly probe the **existing**
process-lock inode, without creating/unlinking/replacing it or opening DuckDB.
Report available, busy or unobservable at the probe time; any acquired lock is
immediately released. A locked live-ledger status exporter, if added, must be
side-effect-free and bounded, not reuse `Ledger.open` recovery behavior. Missing
state must never trigger init, checkpoint, reconciliation or automatic blocking.
Deployment permissions must support the chosen observation path.

| Process-lock observation | Last reported dataset mode | Meaning |
|---|---|---|
| Busy | Any mode | Another lock-using command is active; it may be a tick, not a writer. Cached status remains inspectable. |
| Available | `OPEN` | Only an observation; coordinated readers still require a grant, and live diagnostic results remain uncoordinated. |
| Available | `WRITING`/`BLOCKED` | Possible unresolved/crashed writer. Old descendants may survive; no inferred safety or auto-recovery. |
| Unknown | Any/missing | Permission/path/probe failure; display independently of cached mode. |

The dashboard never polls a live DuckDB connection or reads/copies its DB/WAL
around the lock. Status pages do not reserve a data reader or ingest protocol
messages. Known client pending-release state may be shown through a bounded
client summary, not by exposing its whole spool.
<!-- SYNTHESIS: proposed inspection interface constrained by ../Wintap-PyUtil/wintappy/coordination/ledger.py §_locked/open and wiki/work/dbt-compaction-coordination/design.md §Server files created at runtime -->

### 2. Partition catalog and independent evidence axes

Use `(event_type, dayPK, hourPK, optional protoPK)` as the physical leaf key.
Deletion is an event/hour-prefix operation across its protocol leaves; entity
coverage is one dataset/process-hour checkpoint, not one checkpoint per event or
protocol. Hour-level summaries must retain these different grains.

The compactor can discover families beyond HostActivity's fixed query allowlist.
The status catalog must include configured/observed families even if Activity has
no timestamp adapter; unsupported row queries do not hide their compaction status.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/config.py §Leaf; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/inventory.py §Store.events/discover; streamlit/projects/HostActivity/s3_source.py §RAW_EVENT_TYPES -->

Recommended columns:

| Axis | What to display |
|---|---|
| Schedule | Open/in grace, eligible, queued/active or outside configured schedule; derived with timestamp and configuration shown. |
| Current inventory | Raw and compacted object counts/bytes, co-presence and inventory observation time. Not observed is not zero. |
| Raw processing evidence | Not evidenced, merge verified, skipped existing, empty-at-observation or partial/uncertain; reference original run receipt and scope. |
| Deletion evidence | Not requested, verified at run time, failed/uncertain or not evidenced; current raw presence remains independent. |
| Entity coverage | Disabled/not applicable, not checked or process-hour/generation checks; distinguish inconclusive live observations from coordinated validation and last-qualified producer evidence. |
| Recovery | Coordinator block/disposition and missing evidence; informational only. |

Do not compress these axes into a green "compacted" checkbox. A compacted object
alone does not establish a valid whole hour, a skip does not authorize deletion,
and coverage `completed` with raw `not_run` is not migration completion.
Historical verification stays labeled "verified at <time>"; a current survey that
finds new raw objects creates a possible late-arrival/overlap warning rather than
silently rewriting history or treating every new object as a proven duplicate.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/inventory.py §Store.exists; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §migration_complete/verify_migrations -->

**All partitions without unlimited queries:** maintain a rebuildable advisory
catalog from producer inventories and immutable run summaries. Import historical
run archives through a bounded, resumable summary operation. Initial discovery of
older/unrecorded raw and compacted partitions requires an explicit, paginated,
metadata-only survey, live diagnostic by default or coordinated on request; persist
continuation, mode, observation times and scope outside the authoritative ledger.
Accumulate advisory catalog pages rather than keeping a grant across the entire
dataset. Pages are observations at different times, not one consistent inventory;
even coordinated pages do not share one grant. Reconcile selected stale partitions
on demand. An interrupted/failed survey retains explicit incomplete scope, not
empty inventory or evidence of deletion.

Catalog coverage reports surveyed roots/families/date range, cursor/watermark,
completed versus pending survey pages and last observations. Until surveying
finishes, call it "known partitions" and visibly mark incomplete inventory scope.
Receipts imported without a current survey are historical evidence only. Empty
scheduled hours can be summarized from verified empty-hour evidence; absent
receipts cannot establish empty partitions. New families and protocol leaves must
be discoverable during reconciliation, not frozen by the initial catalog.

The default overview aggregates cached catalog rows, with paginated detail and
day/hour/family/protocol/state filters. Scheduled-hour progress uses the declared
start/cursor/eligibility horizon; observed leaf progress uses the catalog's known
leaf denominator. Neither is collection completeness. Changing filters does not
start S3 LIST/GET. Catalog survey budgets, retention and historical acceptance
scope must be settled before implementation.

### 3. Simple run timeline with trustworthy detail

Use bounded coordinator-owned run-summary pages. Display execution/ownership
time on the chart, data-hour start/end as separate labels, and distinguish intent
time, actual launch time and verified finish/disposition time where recorded.
Order ties deterministically by run ID. Do not assume intent time is launch time.

Run details include operation, event scope, original run IDs, CLI result, committed
coordinator disposition, source/output counts and bytes, raw/deletion/entity/
checkpoint outcomes, child-shutdown observation and allowlisted configuration
receipt summary. Link repairs/reconciliation to the original run without replacing
it. Imported standalone runs have no coordinator disposition and are labeled so.

Timeline success is the coordinator's durable verified-completion COMMIT. A run
with missing receipts or a stopped child can remain unresolved/blocked. Coverage
replay does not replace earlier compaction runs. Phase detail may show verified
record order now; phase-duration bars require real producer timestamps later.
Raw logs, whole commands/environments and large per-file archives are not loaded
or rendered automatically. A redacted, bounded detail adapter avoids credential
or payload disclosure.

## Shared data access and activity semantics

### Approved read modes and diagnostic exception

| Mode | Admission and purpose | Result limitations |
|---|---|---|
| **Live diagnostic** (default) | No reservation, request or grant. Bounded LIST/schema/row/entity/checkpoint observations may overlap a writer or maintenance, including reported `WRITING`/`BLOCKED`. | Always uncoordinated and non-authoritative, even if no writer is reported and all reads succeed. Useful for observing change, not verification. |
| **Coordinated refresh** (explicit) | Qualified `shared-command` client and a matching grant before any active-root read. Useful for comparisons and validation with maintenance excluded. | Excludes coordinated writers, not ongoing sensor uploads; a grant does not itself prove coverage, integrity or completeness. |

The explicit coordination-contract exception is recorded in
[[wiki/work/dbt-compaction-coordination/design#Diagnostic observation exception]].
It is limited to this read-only utility's live observation path. It does not allow
unlocked DBT, ordinary ad-hoc SQL, authoritative verification, ledger inspection or
recovery. Diagnostic observations never supply completion evidence, advance a
cursor, authorize deletion/reopening or change a historical verified disposition.

Keep this warning visible on every live data view and its cached/exported results,
not only when the coordinator reports a writer:

> **Live diagnostic — uncoordinated.** Compaction or entity updates may be in
> progress. Observations can be partial, duplicated or mixed-generation; this is
> not a consistent snapshot or authoritative verification.

Show reported writer mode/run/phase, its producer observation time and freshness
alongside the warning. `WRITING` identifies a last-reported writer, not proof it is
still alive; `BLOCKED` shows unresolved state. Missing/stale/unavailable status
means writer activity is unknown. A fresh `OPEN` or a free process lock cannot
remove the warning. If practical, attach before/after status sequences and source
identities to the refresh for correlation; unchanged observations do not prove
that no writes occurred between them.

**Live lifecycle:** freeze the selected mode, configured root/binding identity,
window, query and budgets before launching a supervised job. Validate settings
offline; never use diagnostic mode to bypass a configured root mismatch or obtain
broader filesystem/credential access. Do not wait for a grant, consult lock
availability as permission, or initialize client job/message state. Discovery and
reads may race deletion/replacement/publication. Return bounded results, close all
connections and stop/reap reading descendants on completion, cancellation, timeout
or UI/session loss. There is no reservation to release; this does not remove the
requirement for child cleanup or bounded resource use.

**Race and failure presentation:** missing objects after LIST, changed objects,
read errors, schema conflicts and incomplete entity/authority/checkpoint reads
produce `inconclusive` with the observed scope, failed stage and reason. These
observations cannot establish corruption, zero activity, verified deletion or
compaction failure. Keep authentication/configuration, unsupported schema and
budget errors distinct; not every error is a writer race. Retain prior results
only with their original mode/time and a failed-refresh label. Do not show a
partial chart as a complete result or automatically deduplicate raw/compacted
overlap. A fully successful aggregation is exact for rows actually read, but an
overlapping writer can omit, duplicate or replace data during that read.

Switching modes starts a new explicit refresh; it does not relabel an existing
live result as coordinated. Stop/reap the prior job and preserve its cancellation/
release or unresolved ownership as applicable; mode switching must not discard a
pending request that could later receive a grant. Failed/unavailable coordinated access remains a
failure/wait in that mode, never an automatic live fallback. A user can explicitly
select live mode instead. Cached catalogs preserve per-page mode/time and expose
mixed observations rather than upgrading the whole catalog's consistency label.

### Optional coordinated reader lifecycle

Reuse the existing Linux `shared-command` client rather than create a second
local admission mechanism. It is not yet integrated into this app; native-Mac
coordinated execution explicitly refuses. App-specific managed-job/browser-loss
qualification and genuine Mac shutdown remain dependencies, not portable support
inferred from the Linux client.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/protocol.py §validate_message; ../Wintap-PyUtil/wintappy/coordination/client.py; ../Wintap-PyUtil/wintappy/coordination/LINUX.md -->

1. Freeze selected roots, window, family/query mode and effective configuration.
   Bind to the coordinator's complete active-root/entity-policy identity. Turning
   off entity display does not narrow the dataset-wide lock binding.
2. Run a bounded coordinated refresh as a managed job. No data-root LIST, schema
   inspection, Parquet/checkpoint/entity GET or validation precedes a matching
   grant. Local status/history exports are exempt inspection data, not telemetry roots.
3. Do discovery, authority/coverage checks as applicable and exact aggregation;
   return only bounded results to Streamlit. Query/data coverage failure returns
   an error, not a wait under the grant for the excluded writer to repair it.
4. Stop/reap all source-reading descendants, close DuckDB/S3 and retain/upload
   release through the client. Failed release delivery stays visible/retryable;
   success can return without waiting for the next coordinator tick.
5. Keep cached completed summaries in session state after release. Status refresh
   and chart rendering use no grant. Query cancellation/disconnection/reload must
   use managed job cleanup, not assume a browser-session callback always runs.

Recommend a supervised per-refresh subprocess plus local job/result handle in
both modes, so the UI can render Status while a job waits or queries. No new
daemon is required by this plan. Start with at most one active dashboard data job
per server across both modes to bound load; extra requests wait locally, and only
coordinated jobs acquire reservations. Avoid automatic data-refresh loops, bound
retry/time/memory/temp/results and survey pages, and measure writer impact. Final
coordinated lifecycle design depends on the qualified client. Do not release on
age/timeout alone; first prove the reading children stopped. Never cache open
connections or grants.

In coordinated mode, all partitions remain under the same dataset-wide
reservation, even for a small filter. Keep budgets low enough to avoid excessive
writer drain latency. Coordination excludes maintenance, **not ongoing producer
uploads**; neither mode produces an atomic capture of all sensor data.

### Event roots and metadata

Resolve raw through the existing dataset precedence; compacted through
`WINTAP_DBT_COMPACTED_ROOT` or the dataset's `compacted/` sibling. Enabled entities
use `WINTAP_DBT_PROCESS_ENTITY_ROOT`, expected hosts and namespace, policy/ceiling
and the resolved active processing-metrics root. Ignore unused metrics settings
when entities are disabled. Validate configured roots/binding in both modes;
coordinated mode additionally checks the grant. Reject overlap/mismatch instead of
silently reading another dataset. Missing advisory status does not prohibit live
diagnostic observation of the correctly configured roots.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §compacted_root_path/active_input_roots; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §process_entity_files/processing_metrics_root; streamlit/projects/HostActivity/s3_source.py §load_settings -->

- **Raw filename metadata:** retain existing host/collect-time charts, malformed
  filename accounting and explicit "raw objects only" label.
- **Partition inventory:** raw and compacted counts/bytes by partition, with no
  inferred hostname or event timestamp from a compacted basename. S3 LastModified
  may be an inventory diagnostic, never substituted for capture/event time.
- **Parquet rows:** choose raw-only, compacted-only or both; use the same family
  host/time projection, name-aligned schema handling and precise `[start,end)`
  filtering. Keep provenance-separated counts alongside any combined chart.
  Deduplicate repeated discovery of the identical URI only, not distinct physical
  raw/compacted copies or semantic rows. Combined mode retains `UNION ALL`
  semantics and visible co-presence/possible-double-counting warnings.
- Keep the 12-hour activity window and existing exact aggregation guards for v1.
  A larger merged object or new schema must not silently bypass time/memory/temp/
  output limits. Status-history windows have independent budgets.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_partition_globs; streamlit/projects/HostActivity/queries.py §inspect_family/aggregate_family -->

### Optional entity inspection

Read explicitly configured per-host snapshots and authority through a qualified
read-only validation adapter in either mode; qualification of its logic is not a
claim that a live multi-object read is consistent. Default display: retained entity
count, lifecycle/parent/identity conflict categories, bootstrap declarations,
generation and validation time. Bounded instance lookup uses canonical entity host scope plus
recorded `pid_hash`; do not fabricate instances or repair by OS PID.

Snapshot lifecycle `observed` means retained evidence without confirmed exit,
**not currently running**. First/last publication partitions and bootstrap start
are provenance, not continuous observation or gap-free history. Current aggregate
context is not a historical as-of process description. Hide user/argument/full
evidence payload fields by default; any richer display needs an explicit scope.
No snapshot rows appear as extra activity points or synthetic Start/Stop events.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §SCHEMA; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_process_entities; wiki/tool/durable-process-entity-manager.md §Evidence, conflicts and limits -->

Reuse qualified integrity/authority logic rather than maintain a weaker green
"valid" check in Streamlit. If full retained-state validation exceeds the refresh
budget, fail visibly or show last-qualified producer evidence with its age and
scope; do not silently label a sampled check equivalent to full validation.
In live mode, authority and host snapshots may come from different generations:
show observed identities and checks as observational, with incomplete/conflicting
reads inconclusive. Even successful live checks do not certify current state or
historical coverage; authoritative validation needs coordinated access. Preserve
last-qualified producer evidence separately, with its original scope and time.

## Interfaces, errors and risks

- Implemented local status refresh is manual; stale presentation is 180 seconds.
  Automatic polling (previously recommended at 10 seconds), recent partition
  detail of 24 hours and a seven-day timeline remain future choices. Current raw
  Activity retains its 12-hour window; exported pages are not date-filtered history.
- Show last observation age on every view, separately for status, inventory,
  validation and run history. A long writer can legitimately outlast the minute
  tick cadence. No uniform stale threshold implies death or authorizes recovery;
  heartbeat/progress freshness needs a producer contract.
- Configure paths through deployment configuration, not arbitrary UI file paths,
  SQL or shell input. Use bounded strict JSON and sanitized errors; unsupported
  schema, unavailable source, valid empty observations and exhausted budgets differ.
- Live mode needs only read/list data credentials, like today's read-only S3
  viewer. Optional coordinated mode additionally needs narrowly scoped own-client
  request/release/cancellation PUT permission; lack of that permission disables
  coordinated refresh rather than silently falling back. Do not give the app writer
  data credentials or ledger recovery privileges. Restrict serving to the trusted
  operator environment; same-server deployment is not authentication.
- Advisory catalog/status caches are rebuildable; ledger, phase receipts and
  entity lineage are not. Retention/export changes never prune authoritative
  evidence as a UI convenience. Storage/time/row limits must include pagination,
  accumulated catalog size and result/detail payloads.

## Alternatives considered and open questions

- **Direct DuckDB SELECT from Streamlit:** rejected; process-lock conflict,
  recovery side effects and runtime/schema coupling defeat always-available status.
- **Use S3 status as permission:** rejected; advisory state can be stale even if
  correctly written. Only an identity-bound grant admits a coordinated reader;
  live diagnostics use the explicit exception, never a status-derived permission.
- **Require grants for every diagnostic refresh:** not selected by the human;
  preventing observation during writes defeats the live diagnostic purpose. Keep
  coordinated refresh optional and the exception narrow, visibly non-authoritative.
- **Reuse raw filename parsing for compacted objects:** rejected; merged names
  cannot establish row host/time. Separate metadata and activity measures.
- **Keep a grant for the browser session or all-history scan:** rejected; makes
  inspection delay writers indefinitely. Use bounded jobs and short survey pages.
- **Derive history from processing_metrics:** rejected; replay overwrites coverage
  and entity-only completion can coexist with raw `not_run`.

Before extending the subset: agree additional history/certificate/catalog fields,
managed client integration, bootstrap/retention, progress cadence, OS permissions
and entity validation/detail scope. No telemetry interchange change is proposed.
Submitted Linux producer behavior is source-reviewed, not full latest-HEAD or
endpoint/resource acceptance. The repaired `fab647f` actual-Mac baseline and original
missing-lock failure remain historical; new native feasibility also cannot qualify
reader shutdown. See
[[wiki/work/dbt-compaction-coordination/implementation-review]].

Next: [[wiki/work/compaction-status-utility/implementation_plan]].
