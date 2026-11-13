---
title: "Durable process entity manager: S3 Parquet and DBT ancestry"
type: tool
confidence: high
grounded_by:
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_processing_metrics.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql
  - ../Wintap-PyUtil/wintap_dbt/models/monitoring/process_ancestry_quality.sql
  - wiki/work/durable-process-entity-manager/verification.md
policy: agent-editable
last_validated: 2026-11-13
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
local staging, not a persistent local DB. The separate entity root must not
overlap raw or compacted scan roots.

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

Every entity-enabled `entities-init`, `entities-replay` and `compact` run also
publishes one verified checkpoint per requested UTC hour under the sibling
`<dataset>/processing_metrics/dayPK=YYYYMMDD/hourPK=HH/metrics.parquet` prefix.
The operational row records the run/operation status, entity namespace and
expected-host count, snapshot hashes, process input/output fingerprints, source
and output file-byte-row totals, and deletion outcome. The root defaults from the
compactor's source-root sibling and can be overridden explicitly; it must not
overlap raw, compacted or entity roots. DBT treats this as coverage evidence, not
telemetry: selected `raw_process` hours without exactly one successful compatible
checkpoint fail preflight, preventing stale state after a failed entity update and
raw-only continuation from being consumed silently.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows/ProcessingMetricsStore; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

## Evidence, conflicts and limits

Typed scalar context accompanies canonical JSON candidate sets inside Parquet.
The reducer retains paired parent hash/PID/kind, PID, birth/Stop FILETIME evidence,
lifecycle flags and display candidates. Duplicates, replay and out-of-order hours
do not increment observation counters. Conflicting real parent pairs remain
unresolved; a missing parent PID can be completed within one consistent real hash.
Known modern/named sentinels are not fake ancestors. Unknown process identities
fail updates rather than creating guessed instances. Refresh effective birth time
does not reopen an exited process or become a new observation timestamp.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §Evidence -->

No initial TTL/GC: retain exited ancestors. Per-host defaults are one million
entities and 256 MiB snapshot/estimated decoded-evidence budget, plus existing
DuckDB memory/spill/file/hour/deadline limits. Python reduction is not spillable.
Capacity exhaustion fails visibly; large-host sharding is not implemented.
The declared bootstrap start and first/last publication partitions do not prove
gap-free collection or automatically discover missed scheduler windows.

**Required exclusion:** one writer per dataset; pause entity updates through the
entire DBT build. Fixed object replacement has no global snapshot generations or
reader/writer coordination service. Production-scale staging/rewrite budgets and
external schedule exclusion still require operator review.

Actual-data qualification exposes these limits: historical bootstrap and November
5/hour 01 combined mode reject unknown identities (negative-PID Refresh and
sentinel-key Stop evidence exists). Only one combined hour passes; the remaining
week successes are explicitly raw-only, not continued entity maintenance. The
retained week-limited snapshots must not be treated as complete historical state.
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
