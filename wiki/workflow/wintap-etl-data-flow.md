---
title: "Wintap / Lintap ETL data flow"
type: workflow
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/models/bronze
  - ../Wintap-PyUtil/wintap_dbt/models/silver
  - ../Wintap-PyUtil/wintap_dbt/models/gold
  - ../Wintap-PyUtil/extras/raw-sensor-compact/README.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/execution.py
  - ../Wintap-PyUtil/wintappy/coordination/writer.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/authority.py
  - ../Wintap-PyUtil/wintappy/coordination/verification.py
  - ../Wintap-PyUtil/wintappy/coordination/completion.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_completion.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_publication.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/wintappy/coordination/inputs.py
  - ../Wintap-PyUtil/wintappy/coordination/recovery.py
  - ../Wintap-PyUtil/wintappy/coordination/maintenance.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py
  - ../Wintap-PyUtil/wintappy/coordination/retry.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_execution.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_verification.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_writer.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_history.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_operation_verifier.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/retry_verifier.py
  - wiki/tool/durable-process-entity-manager.md
  - wiki/tool/raw-sensor-compaction.md
  - wiki/work/raw-sensor-file-aggregation/implementation_plan.md
  - ../Lintap/teletap/README.md
policy: agent-editable
last_validated: 2026-11-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/wintap/core/etl/load; ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Lintap/teletap
tags: [wintap, lintap, wintap-pyutil, dbt, duckdb, etl, s3, bronze, silver, gold, drawio]
---

# Wintap / Lintap ETL data flow

The editable [draw.io diagram](wintap-etl-data-flow.drawio) follows host-local
sensor Parquet through S3, optional hourly compaction, dual-root DBT input and
bronze → silver → gold. It also breaks out the separate durable process-entity
snapshot store, processing-checkpoint store and principal Makefile validation targets.

For presentations, the editable [CONOPS infographic](wintap-etl-conops-infographic.drawio)
([PNG preview](wintap-etl-conops-infographic.png)) uses larger type, heavy connectors
and a local-first happy path with optional S3, compaction and durable-context
branches. It distinguishes the four storage concepts and keeps overlap, bounded-QA
and operational caveats visible. The detailed diagram above remains unchanged;
this infographic is a presentation companion, not an expanded implementation or
production-readiness claim.

## Local-only single-user workflow

Small environments can use **local raw Parquet → DBT → local DuckDB** directly.
With the normal Python/DBT environment installed, run from Wintap-PyUtil with DBT
overrides unset:

```sh
export WINTAP_DATA_ROOT='/path/to/local-dataset'
make dbt-build
```

The root must contain supported Parquet under
`raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/.../`. Local date bounds are discovered
automatically; output defaults to `$WINTAP_DATA_ROOT/duckdb/wintap.duckdb`.
A `compacted/` directory is optional, and an unset/empty
`WINTAP_DBT_PROCESS_ENTITY_ROOT` disables durable enrichment. S3 credentials,
compactor installation and entity initialization are unnecessary for this path.
The Linux input router preserves direct local execution without initializing
coordination or its SDK/ledger state.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §defaults/dbt-build; ../Wintap-PyUtil/scripts/check_dbt_config.py §validate; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §matching_raw_sensor_partition_globs; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_process_entities; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

When reusing a shell previously configured for remote builds, reset its DBT
overrides before the two commands above:

```sh
unset WINTAP_DBT_DATASET WINTAP_DBT_RAW_SENSOR_DATASET WINTAP_DBT_COMPACTED_ROOT
unset WINTAP_DBT_PROCESS_ENTITY_ROOT WINTAP_DBT_PROCESS_ENTITY_HOSTS WINTAP_DBT_PROCESS_ENTITY_NAMESPACE
unset WINTAP_DBT_PROCESSING_METRICS_ROOT WINTAP_DBT_PROCESS_UNKNOWN_IDENTITY_POLICY WINTAP_DBT_PROCESS_UNKNOWN_IDENTITY_MAX_RATIO
unset WINTAP_DBT_DATABASE WINTAP_DBT_START_DAY WINTAP_DBT_END_DAY
unset WINTAP_DBT_START_HOUR WINTAP_DBT_END_HOUR
```

S3 setup now considers only active roots. An inherited remote processing-metrics
override is ignored when entities are disabled; the local-only path needs no metrics
directory or credentials even with that unused override. Resetting it remains useful
to avoid unintended configuration when later enabling entity mode.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access; ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_processing_metrics.sql -->

Without durable enrichment, process context comes from the selected raw event
window; retained historical entity snapshots are an optional source of additional
ancestry. Local analysis output is still a normal DuckDB database. Coordination
compatibility requirements: [[wiki/work/dbt-compaction-coordination/design]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §entity_mode -->

## Storage glossary

The diagram uses these short storage names; paths are relative to the configured
dataset, entity or metrics root. `protoPK` appears where protocol partitioning applies.

| Diagram label | Layout |
|---|---|
| **Raw Event Store** | `<dataset>/raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/<file>.parquet` |
| **Compacted Event Store** | `<dataset>/compacted/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/<merged>.parquet`; sibling to `raw_sensor`, unless a direct compacted-root override is configured. |
| **Process Entity Snapshot Store** | `<entity-root>/hostPK=<sha256(trimmed uppercase hostname)>/entities.parquet`; separate from both event scan roots, one complete snapshot per expected host. |
| **Processing Checkpoint Store** | `<metrics-root>/dayPK=YYYYMMDD/hourPK=HH/metrics.parquet`; defaults to `<dataset>/processing_metrics`, separate from event/entity roots; operational coverage, not telemetry. |

## Read the flow

- Wintap and Lintap/TeleTap write canonical event Parquet to host-local
  **Raw Event Store** paths. The configured uploader sends eligible files to
  its S3 destination, preserving the relative layout.
  Failed uploads retain files for retry; successful upload may delete the local
  copy. Upload depends on the deployed adapter/destination configuration.
- Wintap-PyUtil can read a local dataset root or an S3 **Raw Event Store**
  directly. The input root/window are configured independently of the local
  DuckDB output path.
- **Hourly compaction:** the manually invoked PyUtil compactor writes merged
  event Parquet to the **Compacted Event Store**. For selected closed
  partitions it validates output schemas and source/output row totals. Source is
  retained by default;
  explicit validated prefix deletion is optional. Existing destination hours
  skip, so partial output requires manual reconciliation. Automated scheduling
  remains deferred. See [[wiki/tool/raw-sensor-compaction]].
- DBT discovers event files from both the **Raw Event Store** and
  **Compacted Event Store** and reads them with name-aligned `UNION ALL`. After
  a successful migration removes the corresponding source prefix, compacted
  partitions plus still-raw partitions
  provide a single event-history input. There is no overlap suppression: when
  both copies remain, both contribute rows. Completeness still depends on the
  source archive and selected partitions; the job does not infer missing hours
  or recover events never collected.
- **Separate durable process entities:** the optional combined compaction mode
  updates complete per-host Parquet snapshots in the **Process Entity Snapshot
  Store**, outside both event scan roots. It validates/publishes entity state
  before raw process merge/deletion; a failed entity phase blocks source
  deletion. This state retains long-lived and exited process context, and is not
  itself raw event history.
- **Processing checkpoints:** entity-enabled init/replay publishes hourly coverage
  after the entity phase; combined compaction publishes it after raw processing.
  Each fixed-hour checkpoint carries namespace, snapshot/input identities,
  identity-policy/quarantine evidence and operation status. A final checkpoint
  failure may occur after raw deletion; recovery must reconcile entity state,
  raw migration and checkpoint coverage. The optional server-local run archive
  preserves immutable migration/deletion evidence and original candidates separately
  from coverage. Explicit exclusive checkpoint repair validates surviving data and
  historical entity lineage before republishing original candidates; it neither
  replays entities nor automatically reopens a ledger. Missing/uncertain evidence
  stays blocked. See [[wiki/tool/durable-process-entity-manager]].
- When enabled, DBT reads the **Process Entity Snapshot Store** separately into
  process-entity/context relations and uses that context to enrich process/path
  models. It does not add old snapshot rows to raw bronze or count them as
  in-window lifecycle events.
  It also validates version-4 checkpoints against their own committed generation
  receipts for every selected
  process-bearing hour and materializes `stg_processing_metrics` for QA. Active or
  unprocessed hours without checkpoints fail preflight. Checkpoints do not certify
  complete historical ancestry or raw migration success. The entity authority
  journal binds current snapshots and preserves historical receipt lineage; pending
  intent and snapshot rollback with retained authority fail. Legacy state requires
  an explicit fresh entity/metrics root rebuild and cutover.
  Entity enrichment is opt-in; production bootstrap, capacity qualification and
  scheduling/cutover remain deferred. See
  [[wiki/tool/durable-process-entity-manager]].
- `make dbt-build` performs the config check, source preflight, and DBT build.
  Bronze stages the dual-root event input; silver creates normalized details
  and (when enabled) process context; gold builds analyst-facing summaries.
- The output is the configured local DuckDB database. DBT Parquet export is not
  implemented, so the diagram does not depict bronze/silver/gold Parquet objects
  being published back to S3.

## Core Makefile validation targets

Run these from the Wintap-PyUtil repository root:

| Target | What it checks / does |
|---|---|
| `make print-dbt-config` | Runs offline config checks and prints effective input root/type and date/hour window; does not print credentials. |
| `make dbt-check-config` | Checks the local or S3 raw-input configuration, date/hour window, and local DuckDB output location. |
| `make dbt-check-source` | Lists selected raw/compacted inputs and reads one matching event schema. Entity mode additionally validates expected snapshots and selected process-hour checkpoints; the event probe is not an all-file/all-row integrity scan. |
| `make dbt-build` | Runs config and source checks, then builds DBT models. |
| `make dbt-test` | Runs configured DBT model/data tests. |
| `make dbt-check-output` | Checks the configured local output path/database; this is the prerequisite for the dashboard targets, not a raw-source check. |
| `make qa-pid-hash` | Runs SQL checks for `pid_hash` relationship/orphan issues. |
| `make qa-dashboard` | Launches the PyUtil Marimo overview for built DBT relations and QA summaries. |
| `make qa-pidstat` | Launches the pidstat QA notebook. |

The two QA dashboard targets check that the local output root/database is
available; they do not establish raw-input availability. Queries over raw-backed
bronze views still need access to their configured local or S3 source. When entity
enrichment is enabled, configured entity snapshots and processing checkpoints are
additional DBT inputs with schema/coverage checks. A passing raw source preflight
proves only bounded access/schema evidence, not complete dataset integrity or
semantic quality. These dependencies and limits are reflected in the diagram.
The Linux coordination binding covers all active input roots and the writer's final checkpoint
publication; a read grant does not guarantee that its requested window is covered.
Implementation review: [[wiki/work/dbt-compaction-coordination/implementation-review]].

## Linux shared-reader and hourly-writer integration

Wintap-PyUtil owns the Linux integration submitted at **`123b9d3`**; this Analytics
wiki records its semantics and qualification limits. The historical regression
counts below apply only to their frozen revisions, not full latest-HEAD acceptance,
production rollout or dcc-02–05 closure. The Linux runbook is
`../Wintap-PyUtil/wintappy/coordination/LINUX.md`; current results and remaining gates
are in [[wiki/work/dbt-compaction-coordination/verification]]. Native-Mac shutdown
remains a separate worker-owned gate; Windows coordination is outside this milestone.

- **Local-first routing:** Make's source/build/test/docs/debug targets classify
  active raw/compacted/entity/metrics roots offline. Entirely local inputs invoke
  ordinary DBT without AWS, coordination state, compactor installation or entity
  bootstrap. Inactive remote metrics do not activate coordination.
- **Remote reader lifetime:** matching dataset/transport/client-state configuration
  is required when an active root is S3. One reservation spans build preflight,
  DBT execution and descendant shutdown. Immutable invocation precedes request PUT;
  exact request, command manifest, grant, launch and resolved non-secret transport
  scope remain bound. Canonical single-link original shutdown/outcome evidence is
  required for terminal retries; retries do not relaunch DBT. SIGINT/SIGTERM preserve
  130/143; uncertain shutdown or wrapper death retains the reservation. Grants do
  not expire automatically. Native-Mac coordinated execution currently refuses,
  while local DBT remains available.
- **Exclusive writer:** the main DuckDB 1.5.6 runtime alone opens the local ledger.
  The service processes bounded terminal-first messages, refreshes UTC and drains
  due work. With zero readers, it commits receipt-bound intent before supervising
  standalone DuckDB 2.0.0 compaction and independent read-only data/authority
  verification. The same ledger lock spans launch, verification and atomic
  completion/run/high-water/exact-hour cursor/backlog COMMIT. Only afterward, with
  a fresh clock check, may queued readers receive grants. At most one hour launches
  per tick; due backlog retains priority. Conservative `coordinator.tick` and
  `execute_prepared` still block and are not completion bypasses.
- **Advisory status:** private atomically replaced `<state>/status.json` carries
  explicit observation time and bounded job/run/maintenance summaries, not access
  permission or partition/completion certificates. Missing/stale status means
  unknown; export failure cannot undo completion or authorize reads. The separate
  Analytics utility now consumes only this pinned local advisory v1 export, without
  ledger/lock/data-root access. Raw intent markers are reported, not certified;
  inventory, entity dispositions, delivery, progress and launch/finish remain unknown.
  See [[wiki/tool/recent-host-activity-dashboard]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintappy/coordination/inputs.py; ../Wintap-PyUtil/wintappy/coordination/client.py; ../Wintap-PyUtil/wintappy/coordination/service.py; ../Wintap-PyUtil/wintappy/coordination/writer.py; ../Wintap-PyUtil/wintappy/coordination/supervisor.py -->

**Audited recovery is narrower than general data repair.** Explicitly confirmed
cannot-resume operator reader cancellation retains its own terminal-bound audit,
not an invented DBT exit. Original clean blocked writers resolve through fresh
receipt/archive/data/current-authority/historical-checkpoint/shutdown checks under
the same lock. The added checkpoint-only path targets an already blocked
entity-enabled/deletion-enabled original exit-2 publication failure with complete
migration/deletion evidence. It commits a separate maintenance receipt/intent before
supervised repair; repair alone preserves the original block and cursor. Exact
`resolve-hour --maintenance-id` requires independent original/repair evidence before
atomic completion, retaining actual original failure and separate repair success.
Conflicting checkpoint replacement needs separate confirmation and retains prior
rows. Failed/crashed maintenance stays pending until audited cannot-resume
abandonment, which also preserves the original block. Missing original phases,
unqualified incomplete deletion and unresolved entity publication remain blocked.
Raw-only intentional retry has separate closed local regressions. Explicit-v5 Linux
entity init/replay and clean-original resolution are implemented below; interrupted
publication, missing-original recovery and endpoint/resource qualification remain open.
The retry slice is described in
[[wiki/work/dbt-compaction-coordination/verification#Intentional-retry ownership — active, not accepted]],
not accepted by the earlier repair regressions.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/recovery.py; ../Wintap-PyUtil/wintappy/coordination/maintenance.py; ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py -->

**Original-bound deletion disposition (local regressions closed):** `repair-deletions` adds a narrow
path for an already blocked original exit-2 deletion failure with complete retained
migrations for every selected event/protocol. It authenticates unchanged surviving
inputs and exact outputs, rejecting extras/markers/count/schema conflicts before
deletion. Aggregate object/directory-node bounds precede Parquet discovery; all-hour
survivor/checkpoint/current-authority revalidation continues during repair. It never
replays entities or edits original failed archives. Separate disposition checkpoints
retain historical entity provenance but use repair run/operation and actual new
status/time; conflicting coverage needs explicit replacement with retained prior rows.
Repair leaves the block/cursor; independent resolution binds both archives to retained
captures before atomic completion, preserving original exit 2 and repair exit 0.
Public completion/authority verification still accepts only one hour. This slice's
separate full regressions pass 788 main tests/three skips and 509 standalone tests/
two opt-in S3 skips, exit 0; complete reports inspected and all 265 frozen identities
unchanged after notifications. Local regression closure does not qualify dcc-02–05,
actual S3 or representative resources; new retry/entity changes need separate
evidence. Details and retained failures are in
[[wiki/work/dbt-compaction-coordination/verification#Original-bound deletion recovery]].
Generic survivor-row reconciliation cannot certify partial originals and can replay
entities; it is not a substitute. Missing original coverage stays blocked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/wintappy/coordination/maintenance.py; ../Wintap-PyUtil/wintappy/coordination/completion.py -->

### Read-only failed-merge retry preflight

`retry.verify_retry_prepared()` is an internal independent observation, **not a
retry command, completion proof or admission permission**. It supports exactly one
raw-only failed-merge event/hour, deletion disabled, unchanged original inputs and
absent selected output. It authenticates the blocked original's receipt/intent,
actual exit 2, stopped-child capture and three-record failed archive; it preserves
that original failure, cursor, history and exclusion through restart.

The durable exact request precedes supervised standalone DuckDB 2.0.0 verification.
Standalone rechecks original content, schemas/counts and both bounded prefixes after
each data observation; main DuckDB 1.5.6 reads bounded JSON only and requires the
independently reported source rows/files/bytes to equal authenticated original
migration-intent totals. Original/request/result/capture checks repeat after launch.
Entities, deletion, multiple events/hours, partial output and missing/changed original
coverage refuse. Passing preflight cannot launch another writer or release readers;
durable intentional retry has a separate locally regression-accepted implementation
below. Its endpoint/resource qualification remains open; entity-only exclusive
ownership uses a distinct explicit-v5 contract and is not authorized by this preflight.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/retry.py §verify_retry_prepared/_original_source_totals; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/retry_verifier.py §verify_retry/_request/main -->

The separate read-only preflight local regression gate is closed: 821 main tests/
three skips and 554 standalone tests/two opt-in S3 skips. Complete reports and all
269 frozen identities are checked after notifications; each full suite began only
after its own affected pass/report/identity check. Retain this baseline and the prior
failed controls; new durable retry/entity slices require separate evidence. These
results do not qualify actual S3, resources, native-Mac shutdown or dcc-02–05.
<!-- SOURCE: wiki/work/dbt-compaction-coordination/verification.md §Retry preflight — prerequisite only, integration pending -->

### Audited raw-only intentional retry

Linux `service retry-hour` requires explicit cannot-resume confirmation/reason and
the original execution receipt, not current writer overrides. Under uninterrupted
ledger exclusion, a fresh independent preflight permits atomic disposition plus
fresh receipt-bound ownership for exactly one raw-only failed-merge event/hour,
deletion disabled, original inputs unchanged and output absent. The original remains
exactly `BLOCKED` with its actual failure/archive; there is no original completion,
cursor advance or admission-open interval at ownership COMMIT. Unrelated flags refuse
before configuration resolution; this operator path calls no transport/admission/grants.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/service.py §main; ../Wintap-PyUtil/wintappy/coordination/intentional_retry.py §retry_and_complete_prepared -->

Distinct durable independent post-COMMIT/pre-launch evidence precedes launch. Normal
completion and audited resolution require equal authenticated original/new source
hashes, partitions, schemas and counts before new-run completion/cursor/backlog-mode
COMMIT. Main reads bounded JSON only; standalone DuckDB 2.0.0 owns data verification.
Frozen ephemeral credentials are reused under unchanged storage scope. Failures,
restart and acknowledgment uncertainty stay blocked; neither an orphan receipt nor
a committed retry authorizes automatic relaunch. Bounded predecessor-linked ledger-v4
history preserves failures without pruning; explicit compatible v1/v2/v3 upgrade is
required, never ordinary-open replacement. Public one-hour `compact` validators remain
unchanged; entity-only ownership uses a separate explicit-v5 operation, described below.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/intentional_retry.py §_recheck_retry_completion/validate_history; ../Wintap-PyUtil/wintappy/coordination/completion.py §_build_completion_proof; ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade; ../Wintap-PyUtil/wintappy/coordination/recovery.py §resolve_hour -->

Local successor regressions pass 880 main/three opt-in skips and 554 standalone/two
S3 opt-in skips on 275 unchanged identities, following successful focused/affected
gates and complete-report checks. Retain that freeze and all historical failures
before distinct entity-only work. These local passes do not qualify Linux, actual S3,
representative resources, native-Mac shutdown or dcc-02–05.
<!-- SOURCE: wiki/work/dbt-compaction-coordination/verification.md §Intentional-retry ownership — active, not accepted -->

### Read-only entity input authentication

The separate `entity_execution` receipt binds `entities-init` or `entities-replay`,
exact UTC hours and all four roots; preparation grants no launch permission. Default
window budget is 24 hours, hard ceiling 168; canonical event allowlists include
`raw_process`. Raw compaction/deletion/grace/resume settings are excluded, leaving
public one-hour compaction/completion validators unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_execution.py §prepare_entity_execution/validate_entity_receipt -->

The qualified owner-free input-authentication slice requires explicit v5, no owner
and zero readers under the main-runtime ledger lock. Separately supervised standalone DuckDB
2.0.0 verification supplies input/destination observations; main authenticates actual
canonical single-link receipt/request/command/capture/shutdown evidence using bounded
JSON only. Original observations must match their real artifacts before a fresh
unchanged-input check. Hourly file/byte totals equal selected aggregates; clocks before
receipt creation refuse before verifier launch. Result/request/proof budgets are
64 KiB/1 MiB/128 KiB and refuse without pruning.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_verification.py §verify_entity_inputs_prepared/recheck_input_observation/_validate_inputs -->

Successful read-only observations change no dataset, ledger rows, authority, cursor or admission.
The historical 58-control input and 34-control typed-intent repair focuses establish
only their own authentication/exclusion boundaries, including actual COMMIT/restart/
lost-ack controls. Submitted Linux launch/completion now uses these observations
internally through the distinct writer contract below. These older focuses cannot
qualify that later writer, successor full regressions or broader Linux acceptance.
Historical publication needs original-generation durable authentication, never mutually
rehashed archives or comparison with today's aggregate.
<!-- SOURCE: wiki/work/dbt-compaction-coordination/verification.md §Main-side entity input observations — no permission -->
<!-- SOURCE: wiki/work/dbt-compaction-coordination/verification.md §Typed entity intent and restart exclusion — no launch -->

### Read-only current-generation entity completion observations

`verify_entity_completion_prepared` launches only the separate read-only standalone
verifier under retained same-session typed exclusion. Main binds original receipt/intent,
post-COMMIT inputs, actual single-link CLI command/shutdown/capture and archived publication
report, plus fresh bounded standalone completion evidence. CLI pretty-printed bytes and
canonical verifier bytes remain distinct; replay preserves original bootstrap provenance.
`publication: None` and exact genesis/immediate-successor current generation refuse
historical certification. This read-only adapter changes no ledger rows, authority,
cursor, admission or live acknowledgment, including on refusal; the separate writer/
service below owns those transitions.
`validate_completion_observation` checks a retained contract only. Actual-original artifact
recheck is distinct from fresh standalone data verification; dictionaries alone confer
neither current data authority nor historical publication evidence.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_completion.py §verify_entity_completion_prepared/recheck_completion_observation/validate_completion_observation -->

Initial completion-observation focus passes 44 controls on unchanged fixture-repair
identities after complete report review. Separate expanded artifact/data/non-mutation
focus passes 67 controls with all 295 identities unchanged after complete report review.
Combined standalone focus passes 141 and main passes 447; complete reports/all 295
identities reviewed on the unchanged distinct freeze. Combined read-only focus is closed.
Original-generation publication has separate initial focused evidence below. These
historical read-only passes do not accept the later entity writer/recovery/service;
broader affected/full/platform acceptance remains separate. Historical statistics
never derive from mutually rehashed archives or today's aggregate.
<!-- SOURCE: wiki/work/dbt-compaction-coordination/verification.md §Main current-generation completion observations — read-only, active -->

### Immutable original-generation publication evidence

`retain_entity_publication_prepared` obtains fresh current-only completion internally
under the same acknowledged typed exclusion, rechecking original receipt/input/intent,
post-COMMIT prelaunch and actual CLI/archive/capture/shutdown before evidence/audit COMMIT.
It accepts no caller completion or publication dictionary. The retained envelope binds
the exact standalone completion core, original observation and typed intent; the core
keeps `publication_sha256: None`. `get_retained_entity_publication` returns an authenticated
copy of this original core for later historical requests, never today's aggregate.

Ordinary reopen/history uses retained JSON only, without runtime/artifact reconstruction.
Same-connection materialized SQL-limited keyset pages authenticate original owner, core,
observation, audit and predecessor chain, including staged transaction rows. Publication
records cap at 128 KiB/10,000 operations; shared typed intent/publication/audit history caps
at 64 MiB and audits at 16 KiB. Budgets precede owner/payload fetches and refuse without
pruning. Successful retention changes only publication evidence/audit, not ownership,
authority, raw cursor, grants or live acknowledgment. Committed lost acknowledgment keeps
evidence and BLOCKED original ownership; it is neither atomic completion nor audited recovery.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_publication.py; ../Wintap-PyUtil/wintappy/coordination/entity_intent.py §_budget/validate_history -->

The unchanged 46-control initial focus passes on all 297 frozen identities after complete
report review. This includes genuine later-hour evolution without overwriting original
checkpoints and historical standalone requests using the authenticated original core;
the existing main completion adapter still refuses historical certification. Separate expanded
qualification passes 79 controls (77 new plus two unchanged actual COMMIT process-death
controls) on all 298 frozen identities, after complete report/actual-diagnostic review.
Real UTF-8 SQL byte caps, positive budget/equality boundaries and materialized keyset-tail
refusals execute without history reconstruction or pruning. Both actual crash children exit
87 at the selected before/after publication COMMIT hooks and retain original exclusion,
with absent-before/retained-after publication. This is bounded compatibility/process-death
evidence, not representative sizing, physical power loss or entity permission. A distinct
unchanged combined focus passes 570 main and 141 standalone controls, with complete reports,
actual retained publication crash diagnostics and all 298 source/runner/operator identities
reviewed. The publication/completion/exclusion compatibility focused gate is closed;
the later writer/service/recovery is separately evidenced below, and full latest-HEAD
and broader Linux acceptance remain open.
<!-- SOURCE: wiki/work/dbt-compaction-coordination/verification.md §Durable original-generation publication retention — active, not accepted -->

### Explicit-v5 Linux entity writer and clean-original recovery

Default ledger initialization/upgrade remains v4. Entity operations require explicit
v5 opt-in; ordinary open never migrates. Linux service `entities-init`/`entities-replay`
uses separate allowlisted `entity_writer` configuration, explicit confirmation/reason,
an exact bounded UTC window and unowned zero-reader exclusion. The receipt and typed
intent COMMIT precede fresh independently supervised input rechecks and actual CLI
launch. The main DuckDB 1.5.6 ledger lock spans standalone DuckDB 2.0.0 execution,
shutdown authentication, current-generation data verification and atomic completion/
authority/audit COMMIT. No raw compaction or deletion occurs through this operation.

Typed completion preserves the raw cursor and leaves admission `DRAINING`; it does
not grant readers or automatically reopen. `Ledger.entity_evidence(run_id)` is the
supported history accessor, returning typed completion when retained, otherwise
publication evidence. Predecessor-linked completion/resolution records are bounded
at 128 KiB/10,000 each within shared typed history budgets; same-connection materialized
256-row keyset checks authenticate staged rows without pruning or reopening artifacts.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §initialize/upgrade/entity_evidence; ../Wintap-PyUtil/wintappy/coordination/service.py §validate_config/main; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py §execute_entity_and_complete_prepared; ../Wintap-PyUtil/wintappy/coordination/entity_history.py §complete_observation/validate_history; ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py §validate_history -->

Failures, restart and uncertain acknowledgment retain typed exclusion/`BLOCKED`;
committed completion/authority evidence is never erased to fabricate a clean retry.
Linux `resolve-entity` authenticates the exact original receipt, typed intent,
prelaunch observation, CLI/archive/capture/shutdown and fresh current-only verifier
under the same lock. It neither relaunches entities nor uses current overrides to
replace originals. If completion already committed, a distinct immutable resolution
consumes the original blocker and preserves completion/publication/authority records.
Another lost acknowledgment retains a new blocker; successful resolution still
preserves the raw cursor and returns `DRAINING`.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/recovery.py §load_original_entity_execution; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py §_block_uncertain/_recovery_originals/resolve_entity_prepared; ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py §blocked_original/complete_resolution/block_acknowledgment -->

**Clean-original recovery is not interrupted-publication repair.** Partial host
publication has no successful original publication/checkpoint archive. Matching
journal candidates alone cannot supply those records or original coordinator/CLI
identity, authorize historical success or enter clean resolution. Missing/damaged
originals remain blocked; a separate bounded repair contract and its genuine controls
are still producer-worker-owned and unqualified.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_writer.py §resolve_entity_prepared; wiki/work/dbt-compaction-coordination/implementation_plan.md §Original-bound pending-publication controls — source planning only -->

Worker-reported Linux strict-service focus passes 71 controls; the unchanged
13-module service-affected scope passes 307 in 2,036.10 s. Submitted sources/reports
were independently authenticated, and a native-Mac portable smoke passes 76/zero
skips; the private Linux fixture execution was not independently reproduced on Mac.
These focused/affected gates do not replace historical 880/554 regressions with a
full latest-HEAD result. Native shutdown, actual S3, retained-state resources and
dcc-02–05 remain open:
[[wiki/work/dbt-compaction-coordination/verification#Independent submitted review and native-Mac feasibility — November 15]].

### Retained authority and qualification limits

Entity checks require a verified retained anchor and fresh same-session admission/
writer checks; forward committed lineage is allowed, rollback/forks reject with
the retained ledger. Historical checkpoints bind their own generation receipts,
not today's aggregate snapshot hash. SQL validation, Parquet interchange,
`evidence_json`, original bootstrap provenance and ancestry/instance identities
remain unchanged. Reopen authenticates retained completion/maintenance evidence
without reopening historical runtime files; fresh recovery still needs those files.
Maintenance history is bounded at 128 KiB per audit/10,000 operations/64 MiB total,
with 256-row reads and refusal rather than pruning.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/authority.py; ../Wintap-PyUtil/wintappy/coordination/verification.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; ../Wintap-PyUtil/wintappy/coordination/maintenance.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §validate_checkpoint_receipts -->

Cooperative exclusion does not fence sensor uploads or hostile/external services.
Whole-ledger-plus-authority rollback freshness still requires independent external
evidence/exclusion; process-crash/WAL tests do not qualify physical power loss.
Actual isolated S3 roots/access and representative 32 GB RAM / 64 GB disk sizing
with aggregate monitoring remain unqualified; lower limits need a separate rerun.
No production cron is installed. The human-approved utility Live diagnostic exception
cannot bypass DBT, authoritative verification, ledger locking or recovery.
<!-- SYNTHESIS: scoped implementation/tests and acceptance boundaries in wiki/work/dbt-compaction-coordination/implementation_plan.md; wiki/work/dbt-compaction-coordination/design.md §Diagnostic observation exception -->

Related: [[wiki/repo/wintap-primary-sensor-repo]],
[[wiki/repo/lintap-supporting-repo]],
[[wiki/component/sensor-upload-cache-pipeline]],
[[wiki/repo/wintappy-pipeline-repo]],
[[wiki/tool/raw-sensor-compaction]],
[[wiki/tool/durable-process-entity-manager]], and
[[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]].
