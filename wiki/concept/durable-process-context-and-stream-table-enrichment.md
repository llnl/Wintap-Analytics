---
title: "Durable process context: stream-table enrichment and snapshot plus changelog"
type: concept
confidence: medium
grounded_by:
  - wiki/diagnostic/process-tree-context-completeness.md
  - wiki/component/process-table-retention.md
  - ../Wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../Wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - https://docs.confluent.io/platform/current/streams/concepts.html
  - https://docs.confluent.io/platform/current/streams/architecture.html
  - https://docs.confluent.io/kafka/design/log_compaction.html
  - https://help.splunk.com/en/splunk-enterprise/manage-knowledge-objects/knowledge-management-manual/10.4/use-the-configuration-files-to-configure-lookups/configure-a-time-based-lookup
  - https://help.splunk.com/en/splunk-enterprise/manage-knowledge-objects/knowledge-management-manual/9.4/use-lookups-in-splunk-web/define-a-kv-store-lookup-in-splunk-web
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: ../Wintap/wintap/platform; ../Wintap-PyUtil/wintap_dbt/models/silver
tags: [stream-table-duality, entity-state, snapshot, changelog, process-context, retention]
---

# The pattern has several complementary names

**Durable entity state / materialized entity table** is the broad answer: retain
the state established by rare lifecycle events independently of a short activity
window. **Stream-table duality** describes a stream of keyed updates maintaining
a table. **Stream-table enrichment** joins frequent activity with that entity
table. **Snapshot plus changelog** bootstraps the table and then applies incremental
changes, with reconciliation snapshots as needed.

A sink-side database is one implementation, not a requirement for a separate
sidecar service. The sink can maintain the entity table alongside its event data;
a stateful stream processor can maintain it before the sink. An append-only event
log can rebuild it if enough history is retained. A transient TTL cache alone
does not solve durable historical context.

For process research, distinguish three things:

1. **Activity facts:** file/network/events selected by the analysis interval.
2. **Current entity state:** the latest known state of each process instance.
3. **Historical process dimension / ancestry ledger:** birth identity, parent
   relationship and lifecycle evidence, including exited ancestors needed by
   surviving descendants or retained historical facts.

If changing metadata must be queried as it was at a past time, use a **temporal
table / as-of join**, commonly modeled as a **slowly changing dimension Type 2**.
If both effective time and when evidence became known matter, consider bitemporal
history. These are design vocabulary, not claims about existing Wintap models.

## Kafka and Splunk: mechanisms, not automatic process solutions

**Kafka Streams:** a `KTable` treats records as keyed updates; null values are
deletions. Local state stores can be recovered from replicated changelog topics.
Kafka log compaction retains the latest value per key even if that key has not
changed recently. Compaction is asynchronous, not immediate deduplication.
<!-- GROUND_TRUTH: https://docs.confluent.io/platform/current/streams/concepts.html §Stream-table duality/KTable; https://docs.confluent.io/platform/current/streams/architecture.html §State stores; https://docs.confluent.io/kafka/design/log_compaction.html §Topic compaction -->

Proposed process design: key by canonical **instance**, not reusable OS PID;
retain final Stop state as a non-null value if ancestry is still needed. A Stop
tombstone deletes that instance from latest state. A host/PID-keyed table loses
older instances on reuse; latest-state compaction also loses intermediate metadata
versions. Time-based deletion (`compact,delete`), tombstone retention, recovery
lag, and separate historical retention must therefore be designed explicitly.
Kafka cannot reconstruct an ancestor that was never published or whose required
history was already deleted.

**Splunk:** official documentation identifies KV Store lookups backed by a
collection and time-based (temporal) lookups. These provide enrichment mechanisms;
they do not automatically construct or retain process ancestry. A proposed design
would maintain an instance-keyed lookup/dimension from lifecycle observations and
use it when searching short-window activity. Historical/as-of semantics require
appropriate retained versions, rather than blindly applying today's latest metadata.

Evidence caveat: Splunk capabilities above were corroborated by official search
results. Direct documentation fetch returned HTTP 403; configuration details,
version-specific restrictions, temporal KV Store compatibility, and a working
Splunk process solution were **not verified**. References:
[KV Store lookup](https://help.splunk.com/en/splunk-enterprise/manage-knowledge-objects/knowledge-management-manual/9.4/use-lookups-in-splunk-web/define-a-kv-store-lookup-in-splunk-web),
[time-based lookup](https://help.splunk.com/en/splunk-enterprise/manage-knowledge-objects/knowledge-management-manual/10.4/use-the-configuration-files-to-configure-lookups/configure-a-time-based-lookup).

## Recommended Wintap-oriented design — not implemented

### Ground-truth collection and tactical processing (human guidance, 2026-11-12)

Collection aims to preserve telemetry ground truth. Later experiments consume
the complete dataset or subsets; particular experiments do not govern collection
or retention. The user's research qualification reduces concern about long-horizon
schema changes/backward compatibility; it does not make telemetry completeness
experiment-specific. A bounded entity-state projection is supplementary derived
context, not a replacement for the retained collected dataset.

Before adding infrastructure, make the DBT input publication window span the
relevant **currently deployed sensor runtimes**, including their startup/rundown
publications and delivery slack. For multiple hosts, include each relevant runtime
start, not just the newest deployment. Retain that process context while selecting
activity for any narrower analysis interval. This should considerably reduce
parent-context loss; runtime starts need independent evidence, not the collector's
process birth or Refresh EventTime alone.

It remains a mitigation, not a guarantee: failed/disabled rundown, retained-tree
dedup, delivery gaps and ancestors never published during the runtime can leave
breaks. Redeployment on the same boot is not an automatic reset of process history.
<!-- SYNTHESIS: human tactical recommendation 2026-11-12, qualified by wiki/diagnostic/process-tree-context-completeness.md and wiki/concept/collector-process-telemetry-and-collection-boundaries.md -->

### Longer-term persistence options

- Keep ordinary lifecycle observations and a durable instance-keyed process
  dimension. Make updates idempotent; reconcile conflicting evidence using explicit
  provenance/time rules, not last-arrival-wins or arbitrary `any_value` alone.
- Preserve **canonical birth**, **snapshot observation time**, and **ingestion /
  publication time** separately. Refresh is an observation of an existing instance,
  not a newly created process or a new identity.
- Bootstrap at collector/subscriber startup, replay after consumer-state loss,
  and reconcile periodically. Snapshot/changelog overlap needs a declared watermark
  or buffering/replay strategy; a snapshot racing births/exits is not an atomic inventory.
- Retain exited ancestors for at least the retained facts that reference them and
  their transitive ancestry. Runtime resolver/cache eviction is a separate policy.
  A fixed short TTL or live-only table is inadequate for long-lived descendants.
- Export **windowed activity plus process-context closure**: seed from the selected
  activity/processes, recursively include required ancestors from durable history,
  and mark those rows as context-only in an extract manifest or separate relation.
  Do not count their old births as new in-window activity. Report remaining boundaries
  instead of manufacturing roots.
- Record snapshot success, scope, skipped entries, and delivery acknowledgment.
  A local "sent" log is not proof that the sink received complete context.

<!-- SYNTHESIS: proposals inferred from wiki/diagnostic/process-tree-context-completeness.md, wiki/component/process-table-retention.md, and Kafka references above; no sensor/sink/DBT implementation requested -->

## Refresh frequency versus noise

**Prefer durable context plus reconciliation over repeatedly treating refresh as
new activity.** Suggested pilot, not a selected configuration:

| Situation | Proposed behavior |
|---|---|
| Startup / new subscriber / state loss | Full context bootstrap and replay where available; verify receipt. |
| Normal operation with durable history | Incremental lifecycle updates; measure whether hourly reconciliation is needed, then consider 4–24 hours if coverage and recovery targets permit. |
| Existing event-only short-window extracts | Hourly full refresh as an interim pilot, plus last successful pre-window snapshot and deltas; live-only refresh still cannot supply exited ancestors. |
| Missing-key burst / delivery gap | Bounded, rate-limited targeted backfill from historical state, not an uncontrolled refresh loop. |
| Scheduled extract boundary | Produce context closure explicitly rather than hoping a refresh happens inside the slice. |

The user's recollection of a historical hourly cycle is **unverified**. Current
Linux rundown preserves true birth as EventTime; Windows startup dedup can suppress
known instances. Re-running those routines is not proof of forced republication.
Any republication design must separate runtime dedup from sink reconciliation.
<!-- GROUND_TRUTH: ../Wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §Start/CreateRefreshMessage; ../Wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §InitializeSnapshotRefresh -->

For N inventory instances, interval T hours, and average serialized row size B,
full refresh costs approximately **N × 24/T rows/day**, or **N × B × 24/T
bytes/day** before compression/envelopes. Illustratively, N=1,000 and B=1 KB means
24,000 rows/~24 MB daily at one hour, versus 6,000 rows/~6 MB at four hours; these
are calculated examples, not observed host sizes. Scan/enrichment CPU, small-file
overhead and downstream update cost also matter. Jitter fleet schedules and batch
publication; compact keyed state separately from the historical event archive.

Choose cadence against measured recovery delay, RPF/breakpoint concentration,
snapshot completeness, bytes, CPU, backlog, and duplicate processing. With a
healthy periodic cycle and uniform failure timing, wait to the next refresh
averages roughly T/2 and is less than T; delivery/retry delays and incomplete
inventories invalidate that bound. Delta-only publication saves bytes but needs a
replay/full-bootstrap path, or an unchanged entity lost by the sink stays absent.

Finally, current silver `num_process_start` counts both Start and Refresh, and
`first_seen`/`last_seen` use lifecycle EventTime. Increasing refresh would raise
observation counts without implying more creations; true-birth Refresh does not
establish its later observation time in those fields. Downstream naming/metrics
would need review before implementation.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §process_base -->

## Optional compactor integration

**First round implemented 2026-11-12:** the human selected and authorized S3 Parquet entity
persistence maintained by the hourly compaction job, consumed by infrequent DBT
runs for parent enrichment. See [[wiki/work/durable-process-entity-manager/brief]]
and [[wiki/tool/durable-process-entity-manager]]. Fixed per-host snapshot
rewrite/no initial GC and conservative evidence/publication rules are implemented
as opt-in behavior in Wintap-PyUtil. The worker is locally stateless; its entity
state persists in S3. This supersedes infrastructure uncertainty for the first
round, not the older notes' warnings about ancestry, conflicts or missing evidence.

The hourly [[wiki/work/raw-sensor-file-aggregation/brief]] now supports a separate
entity phase before raw compaction/deletion, binding process input inventories
across phases. Raw compaction remains row-preserving; derived entity context is
not mixed into its count-conserved output.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_inventory -->

[[wiki/work/raw-sensor-file-aggregation/process-context-options]] historically proposed
retaining recently referenced/live instances and their transitive ancestors,
with reachability-based reclamation, explicit coverage horizons and budget limits.
Dataset-level checkpoints/history support later full or subset reads independently
of particular experiments. Bounded retention/GC/checkpoint generations remain
future alternatives, not the no-GC fixed-host implementation.

Related: [[wiki/workflow/process-ancestry-completeness-qa]],
[[wiki/concept/collector-process-telemetry-and-collection-boundaries]],
[[wiki/component/process-table-retention]], [[wiki/event_type/process-events]],
[[wiki/pipeline/nesper-esper-event-stream-processing]],
[[wiki/tension/refresh-republication-vs-durable-process-context]].
