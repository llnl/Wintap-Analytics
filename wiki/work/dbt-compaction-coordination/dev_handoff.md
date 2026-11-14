---
title: "Dev Handoff: Scheduled DBT and Compaction Coordination"
type: concept
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/brief.md
  - wiki/work/dbt-compaction-coordination/design.md
  - wiki/workflow/wintap-etl-data-flow.md
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/dbt_project.yml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/execution.py
  - ../Wintap-PyUtil/wintappy/coordination/writer.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/verification.py
  - ../Wintap-PyUtil/wintappy/coordination/authority.py
  - ../Wintap-PyUtil/wintappy/coordination/completion.py
  - ../Wintap-PyUtil/tests/test_coordination_authority.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py
  - wiki/work/dbt-compaction-coordination/macos-qualification.md
  - ../Wintap-PyUtil/scripts/dcc_macos_baseline.py
  - ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json
policy: agent-editable
last_validated: 2026-11-14
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/dbt-compaction-coordination; ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, dev-handoff, dbt, compaction, coordination, cron, duckdb, s3, local-only]
---

# Dev Handoff: Scheduled DBT and Compaction Coordination

## Handoff summary

**Current snapshot / next gate:** PyUtil commit
`fab647f900196b0bc473fe7977b7dadcf7f4ce52` contains the receipt-bound launch,
independent verification and ledger-v3 completion/history work plus the durable
Mac harness and exact original main lockfile. All 22 manifest files pass committed/
local identity checks in a fresh Git-only clone; 18 harness controls pass. The original
`8ee714c` Mac attempt was blocked before either test stage by the omitted lockfile;
preserve that result. **dcc-mac-baseline-01 now passes** at `fab647f` on macOS arm64:
169 main passed/129 reviewed Linux-only skips; 267 standalone passed/zero skipped.
Both locked runtimes and all 22 identities pass, with no timeout. Evidence:
[[wiki/work/dbt-compaction-coordination/verification#Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed]].
R9's reproducible packaging repair is verified; skipped Linux writer/completion
paths do not establish Mac support. The uncommitted-overlay procedure is superseded.
Finalized review returns the remaining work to the worker; reader-backend/service/
client/advisory exports/audited recovery/
S3/resource gates and dcc-02–05 remain open. Follow
[[wiki/work/dbt-compaction-coordination/macos-qualification#Stage 2: reader backend acceptance remains pending]]
for the later Mac lifetime/shutdown gate, not another unchanged baseline rerun.

Implement the accepted basic plan: **one cron-driven Python coordinator, S3
messages, and a persistent server-local DuckDB ledger**, coordinating hourly
compaction with three to five researchers' occasional local DBT builds over S3.
Preserve the ordinary single-user local-raw workflow as a first-class path.

This document specifies the full integration task. Protocol/ledger and the first
controlled-clock tick and Linux supervision libraries exist. Verified normal
completion/history exists as a locked local library, not the current tick callback;
service integration, client and production scheduling remain proposed. Current local
DBT, dual-root reads, compaction and optional durable entities already exist. Wintap-PyUtil owns
implementation; Wintap-Analytics owns
the shared wiki and this feature folder. Independent deeper compactor qualification
continues separately; integrate against its latest qualified CLI/report contract.

**November 14 completion planning:** the human selected Linux coordinator/writer,
Linux/macOS readers, actual-endpoint qualification on fresh feature-owned fixtures,
and initial 32 GB RAM / 64 GB disk sizing with monitored usage before recommending
lower limits. Read the dependency-ordered completion slices in
[[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]]:
review repairs, execution/platform gates, independent completion, service/client,
audited recovery and integrated qualification. dcc-02's real completion depends
on dcc-04's verifier/high-water evidence; no unit is accepted by this plan alone.
<!-- SOURCE: Human planning decisions, conversation 2026-11-14. -->

**Reviewed baseline:** PyUtil `c782f63`, Analytics `d904559`. Read
[[wiki/work/dbt-compaction-coordination/implementation-review]] for reproduced
snapshot-validation/provenance gaps and required checkpoint/recovery integration.
The basic lock architecture remains applicable. Subsequent R1–R5 safety work and
current acceptance results are tracked in
[[wiki/work/dbt-compaction-coordination/implementation_plan]] and
[[wiki/work/dbt-compaction-coordination/verification]]; review-time findings below
are not claims that the same defects remain in the working tree.

Detailed specification: [[wiki/work/dbt-compaction-coordination/design]].
Requirements: [[wiki/work/dbt-compaction-coordination/brief]].
[Editable sequence diagram](sequence.drawio): shared reader lifecycle and hourly
writer handoff.

**Approved diagnostic exception, November 14:** the follow-on same-server
HostActivity utility defaults to uncoordinated live observation with persistent
warnings and inconclusive race failures; coordinated refresh is optional. Do not
apply its bypass to DBT, authoritative verification, ledger access or recovery, and
do not count diagnostic observations as reserved readers or completion evidence.
The utility is separate planning work, not added implementation scope here. Read
[[wiki/work/dbt-compaction-coordination/design#Diagnostic observation exception]]
before documenting that all dashboards must acquire grants. The worker-owned
local status/run-summary export agreement remains a follow-on dependency.

## Worker continuation after the Mac review

The human finalized this review for commit/push and returns the remaining
implementation to the PyUtil worker. Resume the existing completion plan; do not
restart the accepted baseline or interpret its Linux-only skips as Mac support.

1. **Reader platform gate:** implement and qualify Linux/macOS reader lifetime and
   descendant shutdown. If Mac shutdown cannot be established, stop for human review;
   uncertain readers retain reservations.
2. **Service/client integration (slice D):** wire the qualified locked completion
   adapter into the service, not the conservative `tick` callback. Complete durable
   request/grant/cancel/release handling and bounded advisory exports. Preserve direct
   local-only `make dbt-build` and optional compaction/entities.
3. **Audited recovery (slice E):** add explicit confirmed/reasoned operator operations
   using original evidence under exclusion. Stopped processes or diagnostic reads
   alone never authorize reopening.
4. **Integrated qualification (slice F):** first synthetic local lifecycle controls,
   then human-approved isolated S3 fixtures and representative resource measurements.
   Keep dcc-02–05 unchecked until their own acceptance evidence is recorded.
5. **Utility dependency agreement:** agree status/run/catalog export and reader
   interfaces with the follow-on HostActivity plan. Utility implementation/deployment
   still requires separate approval; Live diagnostic remains non-authoritative and
   Coordinated refresh remains optional.

Read [[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]],
[[wiki/work/dbt-compaction-coordination/macos-qualification#Stage 2: reader backend acceptance remains pending]],
the review/verification evidence, and
[[wiki/work/compaction-status-utility/implementation_plan]] before the next code pass.
Preserve original failures and private reports; record new red/green commands,
revisions and qualification limits in the shared wiki. Production rollout remains
a separate human gate. The original full-scope prompt below is reference material.
<!-- SOURCE: Human finalization and return-to-worker decision, conversation 2026-11-14. -->

## Copy/paste prompt

Use this prompt to start the implementation task from Wintap-Analytics:

```text
Switch to code-development mode for Scheduled DBT and Compaction Coordination.
Implement the coordinator and client integration in ../Wintap-PyUtil, and maintain
the shared feature documentation in this repository's wiki/.

Read AGENTS.md and any applicable instructions in the implementation checkout.
Read these exact handoff files before editing code:
- wiki/work/dbt-compaction-coordination/dev_handoff.md
- wiki/work/dbt-compaction-coordination/brief.md
- wiki/work/dbt-compaction-coordination/design.md
- wiki/work/dbt-compaction-coordination/implementation-review.md
- wiki/work/dbt-compaction-coordination/sequence.drawio
- wiki/workflow/wintap-etl-data-flow.md

Goal: shared DBT grants and exclusive hourly compaction through S3 messages,
a once-per-minute Python tick and a persistent local DuckDB ledger, while
entirely local builds keep the direct make dbt-build workflow.

Inspect both working trees and read the live sources listed in the handoff.
Start with dcc-01: the durable ledger/protocol and failure-point tests using
fake storage/children. Maintain implementation_plan.md and verification.md in
this feature folder against the handoff units and acceptance matrix; track commands
and results there as implementation proceeds. Follow through the remaining units.
Preserve transaction-before-grant/launch ordering, all-input-root classification,
the complete DBT preflight/build/child-shutdown grant lifetime, manual abandoned
reader recovery and blocked-writer reconciliation. Use the current main and
standalone compactor environments separately. Keep fixtures isolated from the
independent compactor qualification data. Update the wiki as behavior stabilizes.
Include active processing_metrics in dataset binding, hold the writer through
final checkpoint verification, and keep migration receipts separate from coverage
checkpoints. Apply the implementation review's recovery and regression requirements.
```

From the PyUtil checkout, the same wiki files are under
`../Wintap-Analytics/wiki/`. The tracking files named above already exist; this
handoff supplies the coordination implementation units.

## Behavior and defaults to implement

| Area | Contract |
|---|---|
| Scheduling | One Python `tick` every minute on the existing compaction server; a tick exits after work or supervises its compactor child to completion. |
| Authority | Only that coordinator grants access; its local DuckDB ledger is authoritative. S3 carries per-job JSON messages. |
| Readers | Multiple DBT grants may coexist. Lock scope includes raw, compacted, configured entities and active processing metrics; request windows are diagnostic. |
| Writers | When an hour is due, enter `DRAINING`, stop new grants, wait for every reserved reader, then compact exclusively. |
| Catch-up | Persist the oldest unfinished UTC hour; default ten-minute grace and one hour per tick. Backlog retains writer priority until caught up. |
| Client polling | Default ten seconds for the client's exact grant key, configurable with `WINTAP_COORDINATION_POLL_SECONDS`. |
| Release | Upload immediately after all managed source-reading children stop. Successful upload lets the client return without another coordinator acknowledgment. |
| Recovery | Documented v1 default is manual abandoned-reader recovery; automatic expiry remains unselected. Uncertain writer outcomes stay `BLOCKED`. |
| Local-only | Resolve all effective input roots first; entirely local inputs execute directly using the main DBT environment. |
| Outputs | DBT analysis database/artifacts remain local. Coordinator ledger, client retry records and optional entity snapshots are distinct artifacts. |

### Polling latency

The retained defaults are **60-second coordinator ticks and 10-second client
polls**, not one-minute polling on both sides:

| Transition | Nominal maximum polling delay |
|---|---:|
| Request becomes visible → coordinator records reservation and publishes grant in the same tick | 60 seconds |
| Grant becomes visible → client observes it and starts preflight | 10 seconds |
| Release becomes visible → coordinator retires reservation | 60 seconds |

Budget approximately **70 seconds before DBT starts**, plus **60 seconds after
completion before the coordinator recognizes release**: 130 seconds of lifecycle
polling overhead. That final delay affects writer admission, not the returning
DBT command after a successful release upload. One-minute client polling would
instead give the discussed 180-second budget. These are polling estimates, not
hard deadlines: exclude DBT runtime, tick/API processing, storage visibility,
retries, due/active compaction and reader draining. A busy long-running writer
tick holds the local lock, so later cron invocations exit busy.

### Local-only compatibility

With ordinary DBT dependencies installed and DBT overrides unset, the supported
invocation from PyUtil remains:

```sh
export WINTAP_DATA_ROOT='/path/to/local-dataset'
make dbt-build
```

Read its `raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/.../*.parquet`, discover local
date bounds, and write `$WINTAP_DATA_ROOT/duckdb/wintap.duckdb`. A missing local
`compacted/` directory is valid. An unset/empty `WINTAP_DBT_PROCESS_ENTITY_ROOT`
disables durable enrichment; process context then comes from the selected event
window. Current source already implements these defaults and skips S3 secret
setup for entirely local inputs.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §defaults/dbt-build; ../Wintap-PyUtil/scripts/check_dbt_config.py §validate; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §matching_raw_sensor_partition_globs; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_process_entities; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

The new routing must bypass coordination initialization, grants, polling and job
records for this path. It needs neither compactor installation nor entity
bootstrap. Check effective **raw, compacted, entity and active processing-metrics**
roots after defaults and overrides; any S3 input selects coordinated access.
R5 now makes offline root resolution and S3 setup consistently ignore unused remote
metrics overrides with entities disabled. Keep that behavior in client routing;
entity-enabled remote metrics must remain an active input.
Existing AWS/coordination
settings alone cannot activate coordination for local inputs. Shell-reset guidance:
[[wiki/workflow/wintap-etl-data-flow#Local-only single-user workflow]].

## Invariants the implementation must preserve

1. Commit `GRANTED` plus the immutable grant outbox entry before PUT. Undelivered
   and unacknowledged grants still count as reservations and exclude a writer.
2. Commit `WRITING` and the run identity before subprocess launch. A restart that
   finds unresolved `WRITING` enters `BLOCKED`; the old child may still be alive.
3. Take the same nonblocking local process lock before every ledger open, including
   operator commands. Hold it through a writer's outcome. Initialize explicitly;
   an ordinary tick cannot replace a missing ledger with empty state.
4. Keep job IDs/digests stable across retries; retain terminal records. Process
   releases/cancellations before admission. A cancellation is terminal even if its
   request arrives later, and that client must never honor a delayed grant.
5. Hold one grant across source preflight, the complete DBT build/tests, and child
   shutdown. Bronze models are views and can read S3 after initial discovery.
6. Release after unsuccessful DBT work once children stop. On uncertain delivery,
   retain a local pending release for retry and report the outstanding job ID.
   If child shutdown is uncertain, retain ownership for recovery.
7. Advance the hour cursor only after verified completion. Stopped children,
   elapsed time, an existing destination or a zero exit status alone do not prove
   successful migration. Partial output/source overlap remains blocked.
8. Treat S3 messages/status as transport/diagnostics; absence or age is never
   permission to run. Failed API calls are errors, not empty listings. Manual
   release requires establishing that the original reader cannot resume.
9. Keep entity initialization/replay/rebuild/cutover and deletion reconciliation
   under exclusive maintenance through the same authority. Hold the normal writer
   through final processing-checkpoint verification and persist separate raw,
   entity and checkpoint outcomes before reopening. Failed final publication can
   follow successful raw deletion; never auto-retry that as an untouched hour.
10. A reader grant does not guarantee entity coverage for an unfinished process
    hour. Fail preflight clearly and release after children stop; do not hold a
    read grant waiting for the writer, trim the window or silently disable entities.
11. Bind the actual writer invocation to a durable, allowlisted, non-secret
    effective execution/configuration receipt and checksum it in the committed
    intent before launch. Resolve defaults/overrides/environment inputs once;
    record roots, hour/run IDs, events, entity policy, deletion options and budgets
    with executable/runtime identity. Missing/mismatched settings refuse launch;
    post-launch uncertainty blocks completion. Never dump the whole environment,
    persist credentials or accept the current environment-omitting command manifest
    as a complete receipt. The local launch, verification and normal-success
    libraries implement this gate; service integration remains pending. See
    [[wiki/work/dbt-compaction-coordination/design#Required execution and configuration receipt]].

The design specifies ledger tables, JSON identity fields, outbox ordering and
recovery commands. The single-authority protocol is grounded in the endpoint's
recorded conditional-write behavior; see
[[wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint]].

## Primary sources and implementation artifacts

Paths below are relative to **Wintap-PyUtil**; read them live.

| Source | Integration point |
|---|---|
| `Makefile`, `scripts/check_dbt_config.py` | Effective roots/output/window, local date discovery, separate source preflight and build targets. |
| `wintap_dbt/macros/paths.sql`, `wintap_dbt/macros/s3.sql`, `wintap_dbt/macros/validate_source.sql` | Raw/compacted discovery, S3 setup, source preflight. |
| `wintap_dbt/macros/process_entities.sql`, `wintap_dbt/models/silver/process.sql` | Optional entity reads and the disabled local baseline. |
| `wintap_dbt/dbt_project.yml`, `wintap_dbt/profiles.yml` | Hooks, model materialization and local DuckDB output. |
| `pyproject.toml`, `extras/raw-sensor-compact/pyproject.toml` | Main Python/DBT runtime uses DuckDB 1.5.6; isolated compactor uses 2.0.0. Only the main runtime opens the coordination ledger. |
| `wintappy/coordination/{protocol,ledger}.py`, `wintappy/coordination/README.md` | Strict v1 messages and locked v3 ledger: reservations/outbox, compatible v1/v2 upgrade, retained authority/completion proofs and internal atomic normal-success transition. Restart/blocked intents still require audited recovery; no installed scheduler/client or recovery command. |
| `wintappy/coordination/coordinator.py`, `tests/test_coordination_tick.py` | First dcc-02 admission/draining slice: bounded complete listings, atomic terminal-first ingestion, oldest-hour priority and blocked callback outcomes. Not a supervisor, full scheduler or completion verifier. |
| `wintappy/coordination/supervisor.py`, `tests/test_coordination_supervisor.py` | Linux/main-thread isolated-subreaper command trees, bounded private logs/control/report parsing and interruption/error cleanup. Tested in a locked tick callback, but never independent completion/reopening authority; non-Linux/external-service containment is unqualified. |
| `wintappy/coordination/{execution,writer}.py`, `tests/test_coordination_execution.py` | Immutable bounded effective receipt and qualified standalone launch bound inside intent. Conservative `execute_prepared` blocks; separate normal-success execution obtains fresh verification internally. No actual-S3 service or macOS qualification. |
| `wintappy/coordination/completion.py`, `tests/test_coordination_completion.py`, `tests/test_coordination_completion_controls.py` | Internal normal-success proof/orchestration, bounded original-archive rechecks and retained history/compatibility/budget/clock/crash controls. Frozen full regressions pass 641 main/439 standalone tests (three/two skips); caller-provided reports cannot complete. |
| `wintappy/coordination/{verification,authority}.py`, `extras/raw-sensor-compact/src/raw_sensor_compact/completion.py`, `tests/test_coordination_authority.py` | Separate receipt/intent/shutdown-authenticated data verification plus explicit ledger high-water initialization and same-session freshness checks. Main entity verification uses the retained anchor without advancing it; no completion/cursor transition. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/cli.py`, `extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py` | One-hour CLI arguments, report fields, optional entity phase, deletion and reconciliation outcomes. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py` | Version-4 fixed-hour coverage names its committed entity generation; final publication remains separate from migration success. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py`, `wintap_dbt/macros/entity_authority.sql` | R1 current-state authority, historical receipt lineage and recorded before/after publication-intent recovery. Legacy upgrade uses fresh entity/metrics roots and explicit cutover. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py`, `extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py` | SQL working state, per-host publication, preserved bootstrap metadata and bounded active integrity validation. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py`, `tests/test_checkpoint_repair.py` | Immutable local run archive; original-generation checkpoint repair after deletion without entity replay or original-history replacement. |
| `tests/test_dbt_source_validation.py`, `tests/test_compacted_inputs.py`, `tests/test_process_entities.py` | Existing local/S3 configuration, dual-root and optional-entity regression fixtures. |

**Root-shape boundary:** `WINTAP_DBT_RAW_SENSOR_DATASET` is the parent containing
`raw_sensor/`; the compactor's `--source-root` is the direct `raw_sensor` event
root. The compacted override/CLI destination are direct event roots. Canonicalize
the bindings consistently rather than appending `raw_sensor` twice.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_path/compacted_root_path; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §parser -->

**Report boundary:** inspect the current `hours`, `partitions`, `delete_source`
and `deletion_failures` evidence as well as exit status. The CLI currently returns
2 for `completed_with_deletion_errors`. A top-level `completed` can coexist with
an event/hour marked `skipped_existing`; inspect every configured event/hour and
require the ledger's verified receipt or explicit reconciliation for a skip.
Capture stdout/stderr as well as parsed JSON because error reports can be on
stderr. Integrate `reconcile-delete` through exclusive recovery.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/main; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours -->

**Checkpoint/recovery boundary:** entity-only replay can publish `completed` with
raw processing `not_run`, and DBT accepts `completed_with_deletion_errors`.
Neither is writer-success evidence. Entity-enabled `reconcile-delete` now publishes
checkpoints; use explicit exclusive recovery for all three phases.
Fixed-hour metrics can be overwritten by replay, so retain the migration receipt
and coordinator-to-CLI run-ID mapping independently using the R4 local archive.
`checkpoints-repair` validates original evidence and current/historical authority
before republishing original rows; missing evidence stays blocked. It acquires no
grant and cannot reopen a ledger. R1–R3 now have regression evidence for freshness,
SQL validation and provenance; those passes alone are not recovery certification.
Current
`entities-verify` success or checkpoint presence alone is insufficient.
<!-- GROUND_TRUTH: wiki/work/dbt-compaction-coordination/implementation-review.md; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows -->

Create the Python package `wintappy/coordination/` with `protocol.py`, `ledger.py`,
`coordinator.py`, `client.py` and `__init__.py`; JSON/crontab examples under
`config/`; four focused `tests/test_coordination_*.py` modules. Update Makefile,
offline config checks and user/operator READMEs. The exact artifact table,
once-per-minute cron entry and config example are in the design.

Server runtime artifacts are the lock, DuckDB/WAL, per-run command/result/logs
and tick log. S3 messages are requests/grants/releases/cancellations plus advisory
status outside telemetry roots. Remote clients retain per-job request/grant/result
and pending terminal-message JSON. Local-only builds create ordinary DBT outputs.

## Implementation units and done checklist

- [x] **dcc-01 — Protocol and durable ledger (first slice).** Implement message
  identity/binding, schema/init, reservations, writer intent, outbox and terminal
  records. Verified completion/cursor/reopening remain later integration.
  Prove transaction ordering/restart behavior with real local DuckDB and fake S3.
- [ ] **dcc-02 — Tick and scheduling.** Implement local lock, message ingestion,
  shared admission, writer priority, UTC cursor/grace/catch-up and advisory status.
  Use supervised fake children to prove reader/writer exclusion and crash handling.
  Require execution/configuration-receipt binding and secret-exclusion checks
  before accepting the service-level launch/completion path.
- [ ] **dcc-03 — DBT wrapper and local compatibility.** Integrate root-aware routing
  into build/source/test/docs targets; span preflight through child shutdown;
  implement polling, cancellation and durable release retry. Prove the local-only
  full-build baseline and mixed-root routing.
- [ ] **dcc-04 — Compactor and operations.** Invoke the qualified isolated CLI for
  one eligible hour, validate full outcomes, persist receipts/cursor and implement
  status/manual reader release/hour reconciliation. Add cron/config and setup docs.
  Include checkpoint repair, independent migration receipts and exclusive entity
  maintenance; address the review's validation/provenance recovery prerequisites.
- [ ] **dcc-05 — Integrated qualification and documentation.** Exercise overlapping
  readers, due writer, queued reader and failure recovery on fresh isolated S3
  fixtures. Record observed polling latency and complete regressions; promote
  implemented behavior to the canonical ETL guide.

## Testing expectations

| Gate | Required evidence |
|---|---|
| Concurrency | Two shared readers overlap; due writer waits for both; a later reader remains queued; no writer interval overlaps any outstanding reservation. |
| Diagnostic boundary | Preserve the explicit utility exception without weakening DBT/shared-command grant assertions or ledger/maintenance protections. Live overlap, warning/race and load qualification belongs to the utility plan, not dcc-02 acceptance. |
| Grant durability | Crash before/after COMMIT and lost PUT acknowledgment; pending grants survive and are republished with identical identities. |
| Message ordering | Duplicates, cancellation before request, delayed grant after cancellation, early terminal delivery and conflicting content preserve ownership correctly. |
| Writer durability | Duplicate ticks exit busy; crashes around launch, surviving children and partial migration leave unresolved writes blocked; missing ledger refuses operation. No duplicate launch. |
| Execution/configuration receipt | Resolve defaults/overrides/allowed environment once; bind actual executable/runtime/arguments, roots, hour/run IDs, events, entity policy, deletion and budgets to the pre-launch intent. Missing/changed/oversized receipts or scope/command mismatches cannot authorize launch/completion. Synthetic secrets never appear in persisted receipt/intent/diagnostics; an environment-omitting manifest or exit zero cannot satisfy the gate. |
| DBT lifetime | Preflight failure, build/test failure, Ctrl-C, child-tree termination and release upload failure exercise the complete reservation lifetime. |
| Local baseline | Full raw-only build without AWS/coordination/entity settings, compacted directory or installed compactor; existing local model/schema/results contract and zero coordination calls/state. |
| Routing | Unused AWS/coordination settings keep local mode; each active S3 raw/compacted/entity/metrics override selects coordination. An unused remote metrics override with entities disabled causes neither coordination nor S3 setup. |
| Scheduling | UTC midnight/grace boundary, missed ticks, multiple backlog hours, empty hour and cursor persistence. |
| Writer results | Successful migration, exit-zero skip/mixed completed report, deletion error, failed entity phase, missing/malformed report and recovery dispositions. |
| Checkpoint/recovery | Failure after raw deletion stays blocked; reconciliation without metrics cannot reopen; replay preserves independent migration receipts. Snapshot rollback/corruption and incremental bootstrap provenance have regression evidence. |
| Entity coverage | Matching namespace/hosts/policy/ceiling; missing checkpoint in requested window fails and releases, without writer-wait deadlock or silent window changes. |
| Polling | Controlled clock proves same-tick grant publication, configured client interval and no extra release acknowledgment; integrated run reports actual delays separately from DBT/writer work. |

Use controllable clocks for timing tests. After the new modules exist, focused
commands from PyUtil are:

```sh
uv run --locked --dev pytest -q tests/test_coordination_*.py
uv run --locked --dev pytest -q tests/test_dbt_source_validation.py tests/test_compacted_inputs.py tests/test_process_entities.py
```

Run the full main suite after integration, plus the standalone compactor suite
from its own locked environment when its integration changes warrant it. Qualify
the real endpoint with feature-owned disposable fixtures and explicit test roots.
Existing compactor/entity results are background evidence, not proof of the new
coordination protocol. No coordination runtime test has been run at this handoff.

## Deployment inputs and closeout

Supply the dataset ID, coordination/raw/compacted roots, first unfinished UTC
hour, event allowlist, AWS profile, absolute server executable/state/log paths
and resource limits. If durable entities are enabled, also supply initialized
entity roots, expected hosts, namespace, budgets, processing-metrics root and
matching identity policy/ceiling. Measure incremental
snapshot read/hash/rewrite cost under the chosen server budgets; imported large-budget
three-day bootstrap results do not qualify these defaults. Confirm supported client
platforms when implementing process-tree shutdown. Defaults remain those in the
design; configuration values are supplied per environment.

At each unit, update `implementation_plan.md` and `verification.md` in this
feature folder with commands, results and remaining gaps, and append substantial
progress to `wiki/log.md`. Keep the diagram/design synchronized with implemented
behavior; promote stable facts into [[wiki/workflow/wintap-etl-data-flow]]. Apply
the root AGENTS.md privacy rule to persisted evidence. Final closeout should name
the owning code/wiki commits, runtime qualification and deployment status.

### November 14 continuation: local normal completion, service remains open

Review repairs pass 493 full-main/387 full-standalone tests before receipt changes.
The later receipt revision passes 194 combined coordination tests, including
44 receipt/launch cases; eight recorded hardening failures precede repairs. Its
full-main regression passes 537 tests (three skips). Use `execution.prepare_execution` and
`writer.execute_prepared`, not the synthetic tick callback seam, for qualified
local launch. Immutable receipts live in `<state>/executions/<coordinator-run-id>/`;
the phase archive remains separate and original records are never overwritten.

Missing/mismatched pre-intent evidence refuses launch. After-intent uncertainty,
including lost COMMIT acknowledgment, remains blocked. Individual engine ceilings
do not establish total RSS/disk acceptance. The standalone process never opens the
ledger. Separate read-only data/authority verification and receipt/intent/shutdown
authentication pass 259 standalone and 204 main affected tests, after eight
additional active-path repairs. The frozen verifier-foundation revision passes
547 full-main tests (three skips) and 431 full-standalone tests (two skips), before
ledger integration. Verification success does not reopen.

Ledger v2 now implements explicit confirmed compatible upgrade, retained
authority-check proofs/audits and separately supervised verified initialization.
Initialization requires a reason, no baseline and zero readers. Entity admission
and writer intent require a fresh check in the same locked session; reopen/failure
clears freshness and successful intent consumes it. Upgrades preserve reservations,
outbox, tombstones, ledger/run identities and audits; unresolved intents stay blocked
without fabricated receipts. Main entity verification now passes real local
migration/checkpoint checks against the retained anchor but leaves high-water,
cursor and permissions unchanged. Forward lineage passes; rollback/forks refuse.
The latest focus passes 236 main and 299 standalone tests. Frozen full authority
regressions pass 579 main tests (three skips) and 439 standalone tests (two skips).
Both notifications arrived before completion/history work; the runtime freeze is
lifted for that next slice, which these results do not cover.

The v3 retained-history/normal-completion prototype passes 46 repaired completion/
upgrade and 24 independent semantic/compatibility/paging/secret controls, before
three final budget/clock red/green controls. Ten active failures precede repairs.
Full standalone of the final revision passes 439 tests (two skips); combined main
focus passes 298 tests. Full main passes 641 tests (three skips) in 1055.19 s on
the unchanged revision; source/runtime-lock hashes match the prepared manifest.
Both full notifications arrived before lifting the runtime/test freeze. The local
independently verified completion-evidence/run/high-water/exact-hour-cursor/backlog-
mode transaction now has complete regression evidence, not service acceptance.
Preserve `execute_prepared`'s conservative
blocking semantics: normal completion needs a same-lock clean-live-intent path that
obtains fresh verification internally. Previously blocked/restart-blocked runs require
explicit audited recovery; passing caller-supplied reports cannot reopen them.
Proof budgets refuse rather than prune;
whole-ledger-plus-authority rollback still requires independently retained external
evidence/exclusion. Commands and red/green attribution:
[[wiki/work/dbt-compaction-coordination/verification#Completion slice C — ledger-v2 authority integration]].
[[wiki/work/dbt-compaction-coordination/verification#Completion slice C — initial ledger-v3 history and atomic completion]]
records v3 scope and all ten active repair controls; it does not accept dcc-02–05.
Origin/proof/run/audit/cursor integrity and the prior-completion clock floor are
local checks, not coherent restored-store/global-clock freshness. Genuine three-hour
instrumented paging does not qualify representative retained-state sizing.
Actual macOS reader shutdown must be qualified before broad client integration; platform skips
and injected remote sessions are not actual-platform/endpoint evidence.
The human selected a human-run Mac harness. Its prepared exact-revision offline
baseline and later backend gate are in
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. The original Mac
attempt was blocked before tests by packaging; the corrective-revision rerun remains
pending. No supported reader-shutdown result is inferred from harness preparation.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/execution.py; ../Wintap-PyUtil/wintappy/coordination/writer.py; ../Wintap-PyUtil/tests/test_coordination_execution.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/wintappy/coordination/verification.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_validate_authority_checks/_require_entity_authority; ../Wintap-PyUtil/wintappy/coordination/authority.py; ../Wintap-PyUtil/tests/test_coordination_authority.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/writer.py §execute_and_complete_prepared; ../Wintap-PyUtil/tests/test_coordination_completion.py; ../Wintap-PyUtil/tests/test_coordination_completion_controls.py -->
