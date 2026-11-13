---
title: "Design: S3 Parquet Durable Process Entity Manager"
type: concept
confidence: speculative
grounded_by:
  - wiki/work/durable-process-entity-manager/brief.md
  - wiki/concept/telemetry-identity-and-endpoint-orientation.md
  - wiki/workflow/process-ancestry-completeness-qa.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_processing_metrics.sql
  - ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: draft
source_paths: wiki/work/durable-process-entity-manager; ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt
tags: [feature-work, design, entity-state, ancestry, s3, parquet]
---

# Design: S3 Parquet Durable Process Entity Manager

Everything below is a proposed implementation of the human direction in
[[wiki/work/durable-process-entity-manager/brief]], not implemented behavior.

**Implementation update:** the human subsequently authorized this first round.
The historical proposal below remains the design record; current implemented
behavior is in [[wiki/tool/durable-process-entity-manager]]. Concrete choices are
canonical JSON evidence in typed Parquet (rather than mixed-type nested tuples),
SHA256 host directories, explicit namespace/host flags, `entities-init/replay/verify`
commands and rebuild by init into a new root. Default per-host budgets are one
million instances/256 MiB. No production scheduler or capacity certification.

## 1. Storage and worker model

```text
<dataset>/raw_sensor/<event>/dayPK=.../hourPK=.../...
<dataset>/compacted/<event>/dayPK=.../hourPK=.../...
<dataset>/process_entities/hostPK=<safe-host-key>/entities.parquet
```

The entity root is independently configurable and must not overlap either event
root. Use a stable, path-safe encoded host key; retain the normalized hostname
inside the file and check it against the directory. Preserve recorded pid_hash
and identity provenance; do not recompute historical hashes or make AgentId a
new identity input. The root defines one declared dataset/identity namespace;
ambiguous legacy/modern identity mixtures and same-name host collisions require
explicit operator handling, not silent merging.

**Round-one recommendation:** one complete snapshot per host, one row per known
process instance. Each job downloads the old snapshot, merges new process evidence
in a temporary DuckDB workspace, writes/validates a new local Parquet file, and
replaces that host's object. No durable local DB, remote state service, per-hour
entity deltas, UUID generations, completion manifests or conditional PUT.

Rewriting a snapshot is also its compaction: repeated observations reduce into
entity evidence rather than creating more hourly entity files. Only touched hosts
with changed semantic state are uploaded; untouched hosts retain their files.
No TTL in this round. If a host snapshot exceeds configured row/byte/spill/runtime
budgets, fail visibly rather than evicting ancestors. Hash-shard a host later if
measurements justify it; that would require a new multi-file publication contract.

Missing expected snapshots are errors, not empty tables. Initialize hosts explicitly
with bootstrap coverage, or an explicitly acknowledged empty starting point. A
new host discovered during an update must be initialized, not silently mistaken
for a previously deleted snapshot. Scheduled expected-host configuration supplies
this guard in round one; no implicit recovery from an empty S3 root.
Store host/namespace/schema/bootstrap declarations in Parquet file metadata as
well as populated rows, so an initialized zero-row host remains identifiable.

## 2. Proposed entity schema

Exact types/names must be finalized by the schema/reducer spike, including nested
Parquet interoperability between DuckDB 2.0.0 (writer) and 1.5.6 (DBT reader).

| Group | Proposed contents |
| --- | --- |
| Instance | schema version, normalized hostname, recorded pid_hash, OS PID, identity namespace/provenance, observed agent IDs |
| Lifecycle | observed Start/Refresh/Stop flags; distinct birth/exit evidence with provenance; resolved birth/exit only when evidence permits; unknown/conflicting state flags |
| Parent | distinct parent evidence tuples containing hash/PID and evidence kind; selected parent pair when unambiguous; missing/sentinel/conflict status |
| Display context | deterministic name/path/user/arguments candidates and chosen display values; conflict flags, not arbitrary ANY_VALUE |
| Time basis | lifecycle effective time; genuine receive/observation time when supplied; first/last publication partitions and an explicit timestamp-basis label |
| Coverage | declared bootstrap lower bound, source namespace and relevant evidence-quality flags; no claim that min/max hours prove a gap-free history |

Keep process and parent PID/hash pairs together. Preserve raw time units precisely;
convert only in the consumer's declared model. Refresh EventTime can be the original
birth, not the later snapshot observation. Never substitute job execution time as
birth, or update every entity's last-observed lease because a job ran.

Do not store increment-only observation counts in round-one state: they double
count on replay unless a durable observation ledger is also retained. Raw archived
observations remain the source for counts and detailed history. Entity flags,
distinct candidate sets, and min/max evidence summaries can be replay-safe.

## 3. Deterministic evidence reduction

Require a merge operation whose semantic result is associative, commutative and
idempotent: merging old state and the same input again adds no new facts. Canonicalize
set representations for stable comparison, separately from row-preserving raw COPY.
Physical shard filenames are not entity identity or a new parent vote.

Recommended conservative parent rule:

1. Classify blank, unresolved sentinel and real-key candidates separately.
2. A single consistent real parent pair can resolve a previously missing/sentinel
   parent. Its own absent entity stays an unresolved ancestor boundary.
3. Multiple incompatible real parent pairs remain **conflicted**. Keep all candidate
   evidence; do not choose whichever row arrived last or appeared first in a file.
4. No PID-only lookup, no fake parent nodes, and no automatic root-link repair.
5. A more selective authority ranking between producer evidence kinds requires
   explicit review; Start is not universally assumed superior to Refresh or Stop.

Retain Stop evidence when later input is an older Refresh; a known exited instance
does not become live again on replay. Conflicting birth/exit evidence must not be
collapsed into an apparently certain lifetime. A same-boot collector restart is
not a new process identity or proof that every old process died.

For display fields, choose deterministic representative candidates under an explicit
ordering and label conflicts. A stable tie-break gives reproducibility, not a claim
that the chosen path/name was correct at every historical moment. General SCD/as-of
metadata is outside round one. Parent correctness takes precedence over cosmetic
completeness; uncertain edges must remain visible.

Historical correction/removal is different from adding evidence. Because candidate
sets are monotone, replacing superseded input requires an explicit rebuild, not a
claim that another incremental replay removes previously learned facts.

## 4. Hourly orchestration and deletion safety

Proposed optional `compact --process-entity-root <root>` mode adds an entity phase
before the existing raw compaction/deletion phase. Exact CLI names are provisional.
Ordinary compaction without this option keeps its shipping behavior.

```text
preflight UTC window, roots, credentials, resource limits and expected hosts
discover selected process evidence and stable inventories
load every affected host's initialized entity snapshot
merge and validate complete replacement snapshots locally
recheck process inputs and previous state identities
upload changed host snapshots; GET and validate published content
only after entity phase succeeds: existing merge -> validate -> optional delete
```

Prepare all affected host updates before publication. Publish per host, recording
success/failure explicitly; if any update fails, do not start source deletion for
that invocation. Some host snapshots may have advanced: replay is safe and there
is no multi-host transaction. Entity state being ahead of raw compaction is fine;
it records observed evidence, not proof that the raw hour was migrated.

In the combined mode, a raw_process source hour cannot be deleted before all its
host updates are persisted and verified. Afterward, the existing whole-hour raw
validation/grace protections still apply. Entity failure blocks combined processing.
Bind the raw process merge/delete phase to the same exact key/version inventory
consumed by the entity phase. New, changed or removed process inputs between
phases must abort that hour without deletion; independently rediscovering a
larger raw inventory must not delete evidence absent from the published entities.
The ordinary compactor's within-phase inventory checks alone do not prove this
cross-phase coverage, so the orchestration needs an explicit handoff check.

Raw failure after entity publication leaves usable entity evidence and the existing
raw manual-recovery behavior. Standalone legacy compaction remains available, but
the entity-maintaining scheduler must always select combined mode.

**Do not use raw destination existence as an entity ingestion cursor.** The current
compactor skips before source discovery and never deletes skipped hours. The entity
phase is a separate opt-in read: replay/backfill explicitly enumerates requested
process inputs, including retained compacted archives after source deletion.
It may revisit evidence from a skipped raw destination without changing raw skip
or authorizing a source delete. Raw/compacted overlap is harmless to the idempotent
entity reducer, but remains duplicate input to ordinary DBT facts.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours -->

Read selected available process archives by column name; validate identities,
schemas, physical partitions and stable inventories. A partial existing compacted
hour is not certified complete merely because it can be read. Bootstrap/replay
uses operator-reconciled archives and reports observed coverage, not an invented
original-source count after deletion. Existing no-lookback policy is unchanged;
late arrivals in skipped hours need an explicitly requested entity replay and
separate raw-overlap reconciliation.

## 5. Publication, recovery and consistency

One writer per entity dataset, and no DBT reader overlapping updates. Use an
external schedule/maintenance exclusion, not conditional writes: the qualified
endpoint ignored those conditions. DBT is infrequent, so round one can pause the
hourly job through the entire DBT build rather than introduce snapshot generations.
<!-- GROUND_TRUTH: wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint.md §endpoint qualification -->

Stage files locally and validate schema, unique keys, evidence reduction and
canonical content hash before upload. Never stream a half-built file as the live
snapshot. Verify completed PUT/multipart replacement semantics on an isolated
copy at the actual endpoint, then reread and compare the full semantic content
after upload; state count equality alone is insufficient. A single-object replacement
is the intended publication unit, not a claimed multi-file S3 transaction.

| Failure | Required behavior |
| --- | --- |
| Input/state parse, validation, drift or budget failure before PUT | No source deletion; old published state untouched |
| Crash/failed upload | Do not declare success or delete source; inspect object/upload state, replay or rebuild explicitly |
| PUT succeeded but acknowledgment/verification failed | Source retained; no rollback assumption; verify the live object, then replay/rebuild |
| One host updated and another failed | Report partial state advancement; no source deletion; idempotent rerun |
| State persisted, raw compaction failed | Preserve existing raw failed-output/manual-recovery contract; do not revert good state |
| Snapshot missing/corrupt after source migration | Fail closed and explicitly rebuild from retained raw/compacted history; never silently initialize |

No normal-run S3 temporary objects or automated generation cleanup are needed.
Local staging/spill is disposable and private. Retained row-preserving compacted
archives are the recovery source even after original small files are deleted.
If archive history is removed too, full entity reconstruction cannot be promised.

The entity-enabled writer also publishes a separate operational checkpoint table
under `<dataset>/processing_metrics/`, not under a generic logs prefix. It writes
one verified Parquet object per requested UTC hour at
`dayPK=YYYYMMDD/hourPK=HH/metrics.parquet`. Each row records the entity namespace
and expected-host count, snapshot identities, process input/output inventory
fingerprints, source/output file-byte-row totals, deletion status and operation
status. The local writer uses staged replacement; the S3 writer verifies the
object by a full GET and content hash. This table is operational evidence, not
another telemetry fact relation.

The DBT preflight requires successful entity-enabled checkpoint rows for every
`raw_process` hour selected by the build. Missing, duplicate, incompatible, or
failed rows reject the build. This closes the failure mode in which an entity
bootstrap/update fails and a raw-only continuation leaves stale durable state that
DBT would otherwise consume silently. A metrics root may be explicitly overridden,
but it must remain separate from raw, compacted and entity roots.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §ProcessingMetricsStore -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

## 6. DBT integration: context is not activity

Propose opt-in `WINTAP_DBT_PROCESS_ENTITY_ROOT` with no automatic discovery in
raw event globs. Disabled means current behavior. Configured means strict
existence/schema/key/host checks; missing or invalid state fails preflight.
Load the snapshots into a materialized DBT staging/entity table at build time;
the maintenance exclusion supplies a stable multi-host read. State 2.0.0 output
must be readable by the main 1.5.6 environment without upgrading it.

Keep three relations distinct:

- **Window process observations:** existing raw/compacted inputs and lifecycle
  counters for the selected publication window. Bronze rows remain unchanged.
- **Durable process entities:** all retained instance context, independent of
  DBT day/hour filters. Parent edges derive from combined evidence under the
  reviewed resolver, not `coalesce` of a possibly wrong non-null ANY_VALUE parent.
- **Process context closure:** selected process keys and current-window activity
  references, plus their transitive known ancestors. Ancestors are context-only;
  activity-only instances retain explicit provenance and no fabricated lifecycle
  observations. Use bronze reference keys where available to avoid downstream
  dependency cycles; pidstat PID alone is not an instance key.

Enrich selected process metadata/parent pairs from resolved entity evidence and
expose origin/conflict/coverage flags. Preserve observed counters, timing metrics
and raw duplicates; do not add snapshot rows to `stg_raw_process`. Existing
windowed process summaries remain window-seeded; context-only ancestors are not
extra historical Start events or automatic new summary seeds.

Change `process_path` to retain its window seed population but recurse through
the context relation. Parent conflicts terminate with an explicit unresolved
reason; OS roots, sentinel parents and cycles have separate statuses. Activity
keys lacking a window lifecycle row are available through the context relation
for explicit enrichment, not silently counted as new starts. Audit downstream
joins that still use `process` as their parent lookup, and redirect only the
parent-context side, not activity aggregation or summary seed populations.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql §cte_process_tree; ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql -->

Report root reachability, immediate breaks, ancestor breakpoints, conflicts,
context-only count, cross-host collisions and missing bootstrap evidence. A
longest available chain is not a completeness verdict. Never promise accurate
parents for evidence that was not collected or remains contradictory.

## 7. Bootstrap and operational interfaces

Provisional interfaces, not executable commands yet:

- `entities init/backfill`: declared expected hosts, store namespace and historical
  UTC partition range, reading both raw/compacted process archives; creates only
  an explicitly empty/new store. Include each relevant sensor runtime's startup
  evidence and earlier available ancestors.
- `compact --process-entity-root ...`: hourly update plus existing compaction;
  reports source/state counts, conflicts, semantic change, update verification and
  raw deletion outcomes separately. `plan` remains read-only.
- `entities replay`: revisit an explicit hour range independently of raw skip,
  including late input; no raw mutation or automatic deletion completion.
- `entities rebuild/verify`: reconstruct into a separate explicit root from
  available archive history and compare canonical entity content. Operator switches
  DBT/job configuration only after verification; no production rebuild assumed.

Do not add a max-hour-only checkpoint or skip replay because a newer hour exists.
Explicit windows and replay-safe summaries avoid a processed-object ledger in
round one. Their tradeoff is possible repeated scans and operator-supplied catch-up
ranges; metadata min/max is not proof that all hours were processed.

## Review points

1. Confirm full per-host rewrites and no entity GC for round one.
2. Select exact nested evidence schema and conservative conflict rules.
3. Select bootstrap history, expected-host configuration and identity namespaces.
4. Confirm writer/DBT exclusion and endpoint replacement qualification.
5. Select state/job budget thresholds and which downstream parent joins are in scope.

Delivery: [[wiki/work/durable-process-entity-manager/implementation_plan]].
Validation: [[wiki/work/durable-process-entity-manager/verification]].
