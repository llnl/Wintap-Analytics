---
title: "Durable process entity manager: S3 Parquet and DBT ancestry"
type: tool
confidence: high
grounded_by:
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_processing_metrics.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql
  - ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql
  - wiki/work/durable-process-entity-manager/verification.md
policy: agent-editable
last_validated: 2026-11-14
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: reviewed
source_paths: ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt
tags: [entity-state, process, ancestry, s3, parquet, dbt, compaction]
---

# Durable process entity manager

Wintap-PyUtil owns the optional batch/state manager and DBT consumer. Analytics
owns this wiki and qualification record. Wintap sensors and Lintap packaging are
unchanged. First-round implementation is opt-in; no production scheduler or
live-dataset bootstrap/cutover is installed.

## Persistence and batch lifecycle

Each expected host has one complete snapshot at
`<entity-root>/hostPK=<sha256(trimmed uppercase hostname)>/entities.parquet`.
Recorded instance hashes are preserved in host scope, never replaced by PID.
File metadata supplies version/host/identity namespace/bootstrap declaration and
timestamp basis, including initialized empty hosts. The worker uses disposable
local staging for publication, not a durable local database. The working reducer
state is held in DuckDB 2.0.0 relations and may spill to the configured temporary
directory; the durable/interoperable state remains the validated Parquet snapshot.
The separate entity root must not overlap raw or compacted scan roots.

`entities-init` bootstraps an explicitly new root from selected raw and compacted
process archives. `--allow-empty-host` acknowledges absent history; `--resume-init`
explicitly recovers partial initialization while validating existing hosts.
Ordinary missing expected snapshots fail closed. `entities-replay` revisits an
explicit window independently of raw skip. `entities-verify` checks state; raw
`verify` also checks entities when configured. Rebuild corrected/corrupt history
into a new root using init, verify, then explicitly switch configuration.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §parser/run -->

Combined `compact --process-entity-root ... --entity-host ... --entity-namespace ...`
prepares all hosts, rechecks inputs/state, publishes changed snapshots and GET
verifies exact content before starting raw compaction/deletion. It binds the same
process source inventory across phases. Rewriting a changed host also compacts
its entity evidence. Existing raw-hour skips never authorize source deletion.
Partial host advancement is reported and replay-safe, not a multi-host transaction.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_inventory -->

Every entity-enabled `entities-init`, `entities-replay`, `compact` and
`reconcile-delete` run reaching checkpoint publication also
publishes one verified checkpoint per requested UTC hour under the sibling
`<dataset>/processing_metrics/dayPK=YYYYMMDD/hourPK=HH/metrics.parquet` prefix.
The operational row records the run/operation status, entity namespace and
expected-host count, snapshot hashes, process input/output fingerprints, source
and output file-byte-row totals, and deletion outcome. The root defaults from the
compactor's source-root sibling and can be overridden explicitly; it must not
overlap raw, compacted or entity roots. DBT treats this as coverage evidence, not
telemetry: selected `raw_process` hours without exactly one successful compatible
checkpoint fail preflight. This catches uncheckpointed hours after failed entity
maintenance/raw-only continuation. Version-4 coverage names its own committed
generation and binds the original snapshot/input identities, expected hosts and
bootstrap summary. Historical hashes are validated against their own receipt,
not against today's evolving aggregate. DBT accepts both `completed` and
`completed_with_deletion_errors` as coverage
statuses; these are not raw-migration or deletion-success certificates.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows/ProcessingMetricsStore; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

Combined commands publish checkpoints **after** raw compaction/deletion. Final
publication failure can therefore follow successful source deletion. Entity-only
replay overwrites fixed-hour checkpoints and reports raw processing `not_run`;
retain migration evidence separately. Entity-enabled `reconcile-delete` now
publishes coverage after its explicit deletion phase. Recovery must reconcile
entity state, raw migration and checkpoint coverage independently.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/publish_metrics -->

The SQL-migration integrity/provenance defects reproduced at `c782f63` are repaired
in PyUtil milestone `7d2b7f8`. Active verification/update paths check canonical host
scope, valid/unique instance keys, exact evidence fields/element types, publication
hour bounds, and all derived scalars and lifecycle flags. Validation reuses the SQL
reducer in separate spillable temporary relations, never a per-process Python cache.
Validated original bootstrap metadata is preserved for changed/unchanged updates,
replay and resumed initialization, including report/file agreement. This does **not**
by itself repair the separate freshness or post-deletion checkpoint boundaries.
Red/green evidence and remaining gates:
[[wiki/work/dbt-compaction-coordination/verification]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §validate_state/_validate_evidence/_reduce_state; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

### Current-state authority and explicit recovery

The subsequent authorized R1 implementation adds a version-1 Parquet journal at
`<entity-root>/_authority/authority.parquet`. DuckDB retains all historical receipt
rows. Each generation's content-derived identity binds its predecessor, canonical
raw/compacted/entity/metrics roots, namespace, expected hosts, identity policy and
ceiling, original per-host bootstraps, before/after snapshot byte identities, after
semantic identities, update window and original process input fingerprint.
Semantic hashing uses named-struct JSON row digests and 1,024-row digest batches;
unnamed row JSON differs between DuckDB 1.5.6 and 2.0.0.

The writer publishes and GET-verifies `pending` intent before any host replacement;
it commits only after all recorded after candidates and input rechecks pass.
DBT and ordinary verification reject unresolved intent. Exclusive replay/resumed
init can accept only each intent's exact recorded before/after candidate, with
unchanged binding/window/input evidence and reproducible after candidates. It
cannot bless an arbitrary self-consistent replacement. Current snapshots must
match the latest committed state; a snapshot rollback retaining the journal fails.
New producer evidence within an already covered hour remains queryable before
maintenance; freshness does not equate coverage to today's raw inventory.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py §Authority; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql §validate_entity_authority; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

Legacy state without authority/version-4 coverage is rejected. Under explicit
operator exclusion, rebuild into fresh entity **and metrics** roots from a
sufficiently retained archive, verify both roots, then cut over reader/worker
configuration together. Preserve old snapshots/checkpoints. Missing archive history
precludes claiming equivalent ancestry recovery. Rollback of the entire journal
and snapshots still needs an independent ledger/operator high-water mark to detect.
Journal rewrite and large retained-state budgets remain unqualified; these receipts
do not close the raw migration/final-checkpoint recovery boundary.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/README.md §Bootstrap and hourly operation; ../Wintap-PyUtil/wintap_dbt/README.md §Durable process context -->

### Independent migration evidence and explicit checkpoint repair

The authorized R4 implementation, included in PyUtil `fe7fcb5`, adds opt-in `--run-id`,
`--coordinator-run-id` and `--run-evidence-directory` CLI flags. The archive is
server-local, separate from raw/compacted/entity/metrics roots and the independent
coordination ledger (protocol/ledger, admission/draining tick and Linux supervision
libraries, not an installed or writer-qualified runtime service).
Immutable, checksummed predecessor-linked JSON records retain
the original run binding, entity generation, original per-file identities and
per-protocol SQL counts/schemas, migration and deletion intent/outcome, and original
checkpoint candidates. Publication fsyncs files, new directory links and directory
entries before advancing; reuse/budget exhaustion fails without overwriting history.
Limits: 64 MiB/record, 256 MiB/run, 10,000 records; hashes stream in 1 MiB chunks.

`checkpoints-repair --confirm-repair --repair-run-id <original-id>` requires external
exclusion and matching original roots/window/hosts/namespace/policy/event selection.
It validates the archive, surviving output byte identities/counts/schemas, source
absence or unchanged retained source, current SQL-validated entity authority and
the original candidates' committed historical receipts. Forward evolution is valid;
repair republishes original rows/generation, never replays/publishes entities or
rewrites the original archive. A new repair archive records the operation. Conflicting
coverage needs explicit `--confirm-replace-checkpoints` disposition, retaining prior
rows. Missing candidate/migration evidence, partial deletion, skips and uncertain
state stay blocked; an early crash before candidate intent can require separately
audited reconciliation or rebuild/cutover.

The reported `phase_evidence.migration_complete` is raw-phase evidence only, not
ledger permission. Empty event-hours may accompany verified migrations; skipped,
mixed skipped/processed and already-deleted outcomes cannot certify migration.
No repair command automatically recreates/reopens the ledger. Linux synthetic
archive/repair and cross-runtime DBT tests pass; actual endpoint/power-loss recovery,
non-Linux durability and accumulated-state I/O/RSS remain unqualified.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §RunEvidence/verify_migrations/repair_checkpoints; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §parser/run; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §validate_checkpoint_receipts -->

## Evidence, conflicts and limits

The SQL reducer projects current observations and prior snapshot evidence into
DuckDB relations, performs distinct aggregation and scalar derivation there, and
only materializes a host's Parquet publication at the boundary. Python retains
paths, publication metadata and reports rather than one decoded `Evidence` object
per process. `evidence_json` remains in the Parquet schema for DBT compatibility;
it is an interchange field, not the Python working-state representation.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

Typed scalar context accompanies canonical JSON candidate sets inside Parquet.
The reducer retains paired parent hash/PID/kind, PID, birth/Stop FILETIME evidence,
lifecycle flags and display candidates. Duplicates, replay and out-of-order hours
do not increment observation counters. Conflicting real parent pairs remain
unresolved; a missing parent PID can be completed within one consistent real hash.
An empty parent-candidate set remains missing context; SQL validation/reduction does
not drop the entity for lacking parent candidates.
Known modern/named sentinels are not fake ancestors. Unknown process identities
use an explicit policy: `reject` is the default and aborts before publication;
`quarantine` retains the raw rows, excludes them from durable entity state, and
records per-hour input denominators, exclusion numerators, ratios, configured
ceiling, reason/host breakdowns and stable fingerprints in `processing_metrics`.
The default quarantine ceiling is 5% per UTC hour and is configurable; a
partition above it fails closed. Neither policy creates a guessed instance,
repairs by PID alone, or invents an ancestor. Refresh effective birth time does
not reopen an exited process or become a new observation timestamp.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §Evidence -->

No initial TTL/GC: retain exited ancestors. Per-host defaults are one million
entities and 256 MiB snapshot budget, plus DuckDB memory/spill/file/hour/deadline
limits. The standalone writer requires DuckDB 2.0.0; the main DBT environment
remains isolated at DuckDB 1.5.6. Capacity exhaustion fails visibly; large-host
sharding is not implemented.
The declared bootstrap start and first/last publication partitions do not prove
gap-free collection or automatically discover missed scheduler windows.

**Required exclusion:** one writer per dataset; pause entity updates through the
entire DBT preflight/build. The writer interval includes final processing-checkpoint
publication/verification; init/replay/rebuild and reconciliation are writers too.
The generation journal does not supply a multi-host storage transaction or
reader/writer coordination service. Production-scale staging/rewrite budgets and
external schedule exclusion still require operator review.
Planned implementation: [[wiki/work/dbt-compaction-coordination/dev_handoff]].

Actual-data qualification exposed these limits: historical bootstrap initially
rejected unknown identities (negative-PID Refresh and sentinel-key Stop evidence).
The explicit quarantine policy and SQL-backed capacity rerun completed on the
preserved three-day window; excluded evidence remains visible in processing
checkpoints and is not counted as durable entity coverage. Entity-enabled DBT and
structural ancestry QA passed, but only two terminal seeds reached a declared
root because the selected bootstrap window has no earlier history. The retained
snapshots are therefore qualification evidence, not complete historical state or
production ancestry proof. No silent filtering, TTL/GC, budget relaxation or
PID-only repair is allowed.
Full expanded source cardinalities also exceed default row limits on two hosts;
identity rejection occurred before capacity certification. No silent filtering,
TTL/GC, budget relaxation or PID-only repair was adopted. See
[[wiki/work/durable-process-entity-manager/verification]] for evidence and the
separate three raw deletion-verification failures requiring reconciliation.

## DBT semantics

Enable `WINTAP_DBT_PROCESS_ENTITY_ROOT`, `WINTAP_DBT_PROCESS_ENTITY_HOSTS`
(comma-separated) and `WINTAP_DBT_PROCESS_ENTITY_NAMESPACE` together. Preflight
checks expected files, schema/metadata/key/evidence and paired-parent scalar
consistency. The writer stays DuckDB 2.0.0; the reader stays 1.5.6.

- `stg_process_entities`: materialized state with bootstrap/namespace provenance.
- `process_entities`: parent resolution from retained plus current-window evidence,
  with deterministic display context and conflict flags.
- `process_context`: window lifecycle/activity references and ancestor closure;
  explicit context-only/activity-only/missing-entity flags.
- `process`: original window seeds/counters/timing metrics, enriched parent/display
  context; no historical snapshot rows inserted into raw bronze observations.
  Original hostname spelling is retained for existing host/summary joins;
  only durable-context lookup predicates normalize hostnames.
- `process_path`: original window seeds traverse known context ancestors, checking
  host/PID pair compatibility and cycles without inventing missing nodes.
- `process_ancestry_quality`: one terminal verdict per window seed. Roots require
  consistent recorded self-parent identities and the declared root PID set
  (`WINTAP_DBT_PROCESS_ROOT_PIDS`, default `0,1,4`, restrict for dataset/OS).
  Other self-links are cycles; this never infers or repairs edges by PID.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_entities.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql; ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql -->

Activity-only context does not automatically become a new summary seed. Disabled
mode retains legacy behavior. This is not a general repair of downstream arbitrary
representatives or historical as-of metadata. Never-collected or contradictory
evidence remains unresolved; a longer chain is not itself proof of completeness.

Operational commands live in
`../Wintap-PyUtil/extras/raw-sensor-compact/README.md` and
`../Wintap-PyUtil/wintap_dbt/README.md`.
Evidence: [[wiki/work/durable-process-entity-manager/verification]].
Context: [[wiki/concept/durable-process-context-and-stream-table-enrichment]] and
[[wiki/workflow/process-ancestry-completeness-qa]].
