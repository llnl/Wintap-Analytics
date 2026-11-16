---
title: "Design: Cron, S3 Messages and DuckDB Coordination"
type: concept
confidence: speculative
grounded_by:
  - wiki/work/dbt-compaction-coordination/brief.md
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/dbt_project.yml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint.md
  - ../Wintap-PyUtil/wintappy/coordination/protocol.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/execution.py
  - ../Wintap-PyUtil/wintappy/coordination/writer.py
  - ../Wintap-PyUtil/wintappy/coordination/verification.py
  - ../Wintap-PyUtil/wintappy/coordination/authority.py
  - ../Wintap-PyUtil/wintappy/coordination/completion.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/MACOS.md
  - ../Wintap-PyUtil/wintappy/coordination/recovery.py
  - ../Wintap-PyUtil/wintappy/coordination/maintenance.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publications.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_publication.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py
policy: agent-editable
last_validated: 2026-11-16
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, design, dbt, compaction, coordination, cron, duckdb, s3, drawio]
---

# Cron, S3 messages and DuckDB coordination

**Development milestone, November 16:** the human prioritizes actual sensor-data
integration across the Linux writer/entity cache and Linux/native-Mac DBT clients.
Existing deployment telemetry is expendable; comprehensive repair/preservation
hardening is not a prerequisite to that finite milestone. See
[[wiki/work/dbt-compaction-coordination/integration-milestone-plan]]. This changes
delivery order and acceptance scope, not the protocol's ownership/completion rules.
<!-- SOURCE: Human planner-role direction and development-data clarification, conversation 2026-11-16. -->

**Selected architecture:** one scheduled coordinator on the compaction server,
S3 messages for clients, and a **local DuckDB coordination ledger**. Coordinator
paths, commands and schemas proposed below describe the complete intended service.
Protocol/ledger, evolving-clock admission/draining, Linux command-tree supervision
and receipt-bound local standalone launch/separate verification libraries exist. An
isolated native-Mac process-group candidate is wired to the coordinated reader and
passes 12 actual-Mac synthetic lifecycle controls; broader DBT/data/service acceptance
remains open.
High-water initialization/freshness checks also exist. The historical v3 retained-history/
normal-completion prototype passes hardened local controls; full standalone passes
439 tests (two skips), combined main focus passes 298 tests and full main passes
641 tests (three skips) on the unchanged revision.
The subsequent Linux overlay (committed in `123b9d3`) adds service CLI, root-aware Makefile
routing, durable reader lifetime, advisory exports and audited reader/clean-hour/
checkpoint repair, followed by locally regression-accepted original-bound deletion disposition.
Current regression status and remaining recovery scope
are in [[wiki/work/dbt-compaction-coordination/verification]]. Production scheduling
is not installed; actual-endpoint/resources and broad native-Mac reader acceptance
remain unqualified. The proposal below retains the full intended scope, not full acceptance.
The human has accepted a native-Mac best-effort exception to complete-descendant
shutdown proof: normal release may follow wrapper completion and observation of no
live members in the dedicated process group, with escaped-descendant risk explicit.
Timeout, supervisor death or uncertain group state retains the reservation. Linux supervision and direct
local-only DBT are unchanged; no Linux VM or Docker is required. Synthetic lifecycle
qualification is narrower than backend/platform acceptance. See
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]].
<!-- SOURCE: Human native-Mac risk decision, conversation 2026-11-15. -->

**Local-only compatibility:** single-user builds over local raw Parquet retain
the direct `make dbt-build` path. Compaction, durable entity state and this
coordination protocol are optional; the two sequence pages show the shared-S3 mode.

[Open the editable draw.io sequence diagram](sequence.drawio):

1. **DBT shared access** — request, durable grant, local build, release.
2. **Hourly writer handoff** — writer becomes due, existing readers drain, exclusive
   compaction completes, queued readers receive grants.

Requirements: [[wiki/work/dbt-compaction-coordination/brief]]. Existing data flow:
[[wiki/workflow/wintap-etl-data-flow]].
Implementation entry point: [[wiki/work/dbt-compaction-coordination/dev_handoff]].
Post-pull source review and reproduced gaps:
[[wiki/work/dbt-compaction-coordination/implementation-review]].

## 1. Components and authority

| Component | Runs where / when | Responsibility |
|---|---|---|
| DBT wrapper | Each user's machine, for one invocation | Request access; supervise local DBT work; publish release under the platform's accepted shutdown rule (Linux descendant tree; native Mac best-effort process group). |
| S3 coordination prefix | Existing Garage bucket | Exchange small per-job JSON messages. |
| Coordinator tick | Existing compaction server, once per minute | Admit readers, drain for writers, run one eligible hour, record outcome. |
| DuckDB ledger | Persistent local disk on that server | Authoritative readers, writer state, scheduling cursor, retry/outbox and audit records. |
| Existing compactor | Subprocess of the coordinator | Perform the configured compaction, validation and source deletion. |
| S3 telemetry / optional entities and processing checkpoints | Existing configured roots | DBT input and compactor-managed data. |

Only the coordinator decides admission. All participants use one dataset ID and
coordination root, bound to the effective raw, compacted, optional entity and
active **processing-metrics** roots. Entity mode also binds namespace, expected
hosts, identity policy and quarantine ceiling. Time ranges are diagnostic metadata;
v1 locks the entire dataset, including all four roots.

S3 request/reply objects are individually owned, immutable messages. The protocol
does not need a shared object that multiple clients conditionally overwrite. Earlier
endpoint probes accepted a conflicting `If-None-Match: *` PUT and overwrote the
object; this design avoids depending on that primitive.
<!-- GROUND_TRUTH: wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint.md §Conflict -->

This is cooperative coordination: tools that read or modify these roots must
participate, except existing sensor uploads and the explicitly approved diagnostic
observation path below. Ordinary S3 permissions do not enforce the protocol. Direct
ad-hoc queries and authoritative read-only verification need shared access; entity
initialization, replay, rebuild/cutover and manual reconciliation need exclusive maintenance
access through the same authority, including while resolving `BLOCKED` state.
Sensor uploads continue under the existing collection
contract; a read grant stabilizes compaction activity, not incoming collection.

### Diagnostic observation exception

**Human-approved on November 14; utility implementation not authorized here.** The
same-server HostActivity compaction/status utility may use a default **Live
diagnostic** mode for bounded, read-only LIST/schema/row/entity/checkpoint observation
without requesting or holding a reader reservation. It may intentionally overlap
compaction/entity publication or maintenance, including reported `WRITING`/`BLOCKED`.
An optional, explicitly selected **Coordinated refresh** uses the ordinary matching
grant and managed-client lifecycle for comparisons/validation.

Live diagnostics always disclose possible partial reads, raw/compacted duplication
and mixed generations, even when status reports `OPEN`. Missing/stale writer status
is unknown, not inactivity. Incomplete or conflicting live reads are inconclusive;
they cannot certify corruption, zero activity, migration failure, deletion, coverage
or safe reopening. Diagnostic observations cannot supply authoritative verification
or completion evidence, advance the cursor or alter ledger/run/authority state.

This exception is limited to that utility's explicit observation path, not unlocked
DBT, ordinary ad-hoc queries, authoritative verification or recovery. Every live
ledger access still takes the process lock; the app uses published summaries, not
unlocked DuckDB inspection. Maintenance remains exclusive with coordinated readers
and other writers; live diagnostic observers intentionally remain outside that
exclusion. Bound their load and stop/reap reading children without acquiring a
reservation or blocking writer admission. A failed coordinated refresh must never
silently fall back to live diagnostics.

Consumer warning, mode/provenance handling and race/resource gates:
[[wiki/work/compaction-status-utility/design#Approved read modes and diagnostic exception]]
and [[wiki/work/compaction-status-utility/implementation_plan]]. The two sequence
diagram pages still describe coordinated DBT/writer handoff, not diagnostic reads.

## 2. Source artifacts to create or change

All paths in this table are relative to **Wintap-PyUtil**. They are proposed files,
not copies of implementation into the wiki.

| Path | Language / format | Contents |
|---|---|---|
| `wintappy/coordination/__init__.py` | Python | Package marker. |
| `wintappy/coordination/protocol.py` | Python | Versioned JSON validation, dataset/root binding, UUIDs, canonical request digest, boto3 messages and idempotent retries. Shared by server and client. |
| `wintappy/coordination/ledger.py` | Python + embedded DuckDB SQL | Transactions, state transitions, durable grant outbox, terminal job records and scheduling cursor. |
| `wintappy/coordination/{execution,writer}.py` | Python | Implemented bounded effective receipts and qualified standalone launch; conservative execution blocks, while the separate same-lock normal-success adapter obtains fresh verification internally. Local synthetic evidence only. |
| `wintappy/coordination/completion.py` | Python | Internal normal-success orchestration, receipt-bound proof semantics and bounded original-archive rechecks; retained history/atomic transition belong to the main-runtime ledger. |
| `wintappy/coordination/coordinator.py` | Python | `init`, `tick`, `status` and recovery subcommands; POSIX file lock; scheduler and compactor subprocess supervision. |
| `wintappy/coordination/client.py` | Python | `dbt-build` and shared-command wrapper; polling, cancellation, child supervision and release retry. |
| `config/coordination.example.json` | JSON | Server paths, dataset roots, profile, first hour and compactor settings; placeholders only. |
| `config/coordination.crontab.example` | crontab / shell command | Once-per-minute invocation shown below. |
| `Makefile` | GNU Make | Route S3-backed DBT operations through the wrapper; retain direct local builds, offline checks and familiar target names. |
| `scripts/check_dbt_config.py` | Python | Validate required coordination settings for S3-backed operations without doing S3 reads. |
| `tests/test_coordination_protocol.py` | Python / pytest | Message identity, delayed delivery, retries and cancellation cases. |
| `tests/test_coordination_ledger.py` | Python / pytest + DuckDB | Admission, terminal states, cursor persistence and crash points. |
| `tests/test_coordination_client.py` | Python / pytest | Local bypass and mixed-root routing; preflight/build lifetime, signals and durable pending releases. |
| `tests/test_coordination_tick.py` | Python / pytest | Multiple readers, writer priority, local lock, restart and incomplete compaction. |
| `README.md`, `wintap_dbt/README.md`, `extras/raw-sensor-compact/README.md` | Markdown | Client setup, operator setup, participating commands and recovery procedure. |

Use the existing main Python environment for the client and coordinator. It already
includes boto3 and pins DuckDB **1.5.6**. Invoke the standalone compactor through its
own locked project/environment, which uses DuckDB **2.0.0**. The compactor never
opens the ledger, and the ledger is separate from every user's analysis database.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/pyproject.toml §dependencies; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours -->

## 3. Server configuration and cron

Example deployed config: `/etc/wintap/coordination.json`. All names are generic
placeholders and must be set for the chosen dataset. Credentials remain in the
existing AWS profile configuration.

```json
{
  "protocol_version": 1,
  "dataset_id": "research-dataset",
  "coordination_root": "s3://<bucket>/coordination/research-dataset",
  "source_root": "s3://<bucket>/<dataset>/raw_sensor",
  "compacted_root": "s3://<bucket>/<dataset>/compacted",
  "process_entity_root": null,
  "processing_metrics_root": null,
  "aws_profile": "<configured-profile>",
  "state_directory": "/var/lib/wintap-coordination",
  "first_hour": "<first-unprocessed-UTC-hour>",
  "grace_minutes": 10,
  "max_hours_per_tick": 1,
  "uv_executable": "/opt/bin/uv",
  "compactor_project": "/opt/wintap-pyutil/extras/raw-sensor-compact",
  "target_size_bytes": 134217728,
  "event_types": ["<selected-event-type>"],
  "compactor_timeout_seconds": 1800,
  "memory_limit": "2GB",
  "max_temp_size": "4GB"
}
```

Optional entity mode additionally supplies the expected hosts/namespace, explicit
processing-metrics root, identity policy/ceiling and entity budgets required by the
existing CLI. Resolve the metrics default to the source-root sibling once and bind
that exact root for readers/writers. Current policy defaults are `reject` and
`0.05`; the worker's qualified runs explicitly used `quarantine`. The configured AWS profile resolves the
approved endpoint/region for both the coordinator and child compactor. Install
the main environment from its lockfile and pre-provision the compactor environment
and extensions. Use absolute executable/project/state paths; cron supplies no
interactive shell setup.

**November 14 qualification selection:** Linux coordinator/writer and Linux/macOS
readers; actual-endpoint testing uses fresh feature-owned fixtures. Initial sizing
uses a 32 GB RAM / 64 GB disk envelope, monitoring actual usage before recommending
lower limits. The 2 GB/4 GB values above remain unqualified example settings, not
the selected acceptance budget or installed defaults. Dependency slices, receipt/
completion integration and remaining runtime inputs are in
[[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]].
<!-- SOURCE: Human planning decisions, conversation 2026-11-14. -->

**User crontab on the compaction server** (no username column):

```cron
SHELL=/bin/sh
PATH=/opt/bin:/usr/local/bin:/usr/bin:/bin
* * * * * /opt/wintap-pyutil/.venv/bin/python -m wintappy.coordination.coordinator tick --config /etc/wintap/coordination.json >> /var/log/wintap/coordination.log 2>&1
```

Provision writable state/log directories for the chosen runtime identity. The
Python tick itself takes a nonblocking `fcntl.flock` before opening DuckDB. If
another tick is active, it exits as busy; there is no second hourly cron job.
Short ticks exit after processing messages. A tick that starts compaction remains
alive to supervise that subprocess and holds the local lock through its outcome.
All timestamps and hour calculations are UTC inside Python, independent of cron's
local timezone. A writer scheduled for hour 11:00–12:00 becomes eligible at 12:10
with the default grace period.

### Server files created at runtime

| Path | Format / purpose |
|---|---|
| `/var/lib/wintap-coordination/coordinator.lock` | Persistent lock-file inode; OS advisory lock, not a timestamp semaphore. Do not unlink to unlock. |
| `/var/lib/wintap-coordination/coordinator.duckdb` | Authoritative local DuckDB database. |
| `/var/lib/wintap-coordination/coordinator.duckdb.wal` | DuckDB-managed WAL when present; retain with the database for crash recovery. |
| `<state>/executions/<coordinator-run-id>/execution.json` | Implemented immutable bounded effective invocation receipt, retained and checksummed in the committed writer intent. |
| `<state>/executions/<coordinator-run-id>/observations/command.json`, `supervision.json` | Supervisor command/capture/shutdown observations, separate from the receipt and not completion certificates. |
| `<state>/executions/<coordinator-run-id>/authority-verifications/<id>/` | Implemented immutable receipt/ledger/dataset-bound authority request and separately supervised observations. |
| `<state>/executions/<coordinator-run-id>/verifications/<id>/` | Implemented immutable completion-data request and separately supervised observations; no permission transition. |
| `/var/lib/wintap-coordination/runs/<run-id>/result.json` | CLI report, return code, timing and coordinator disposition. |
| `/var/lib/wintap-coordination/runs/<run-id>/stdout.log`, `stderr.log` | Captured child output; available even if report parsing fails. |
| `/var/lib/wintap-coordination/phase-evidence/<cli-run-id>/*.json` | Independent immutable worker phase archive, separate from ledger and all data roots; original migration/checkpoint candidates retained. |
| `/var/log/wintap/coordination.log` | Append-only structured tick/activity log; ordinary log rotation. |

DuckDB stays on persistent **local disk**, outside S3 and network-shared folders.
Every ledger-opening command, including local status/recovery, takes the same
process lock. If a long tick owns it, status reports busy or reads the advisory
S3 status object; it does not open a second DuckDB process concurrently.

Initialization is explicit. A normal tick refuses to create a missing database.
An explicit `init` binds a new ledger to its dataset, roots and starting cursor.
Lost/corrupt state requires recovery with clients stopped, not automatic empty
state creation or promotion of an old backup. State is recorded before external
effects, so uncertainty remains visible after restart.

### Required execution and configuration receipt

**Human-required on November 14; local launch library implemented.** Before launch, the service
adapter must resolve defaults, overrides and allowed environment settings once,
then durably retain a versioned, canonical, bounded, immutable receipt. Bind its
checksum to the writer intent before launch. The actual supervised invocation and
subsequent completion verification must match that receipt, not merely the
callback's declared command or result.

The explicit allowlist must cover the qualified executable/runtime and arguments,
working directory, dataset/active roots, effective non-secret storage endpoint and
region selection, selected UTC hour, coordinator/CLI run IDs, events, enabled entity
namespace/hosts/identity policy/ceiling, deletion options and applicable processing,
capture, timeout and storage budgets. Disabled settings are explicitly inactive;
unrecorded inherited settings must not silently change the effective data scope.

Only resolved, non-secret settings may be persisted. Do not dump the environment,
record credentials/tokens, or substitute secret hashes for a non-secret configuration
receipt. Keep secret material out of persisted arguments and diagnostic capture;
credential delivery remains separate from the receipt. Apply the root AGENTS.md
privacy rule to any wiki examples or copied qualification evidence.

Missing, malformed, oversized, changed or mismatched receipts/settings refuse
launch. A mismatch or uncertainty discovered after launch remains `BLOCKED`, with
no cursor advancement or admission reopening. Test actual-command/scope mismatch,
default/override/environment resolution, receipt integrity/budgets and synthetic
secret exclusion through active launch/completion paths. Exit zero cannot bypass
these checks. The receipt is necessary execution/configuration evidence, not an
independent raw/entity/checkpoint completion certificate.

The current supervisor manifest deliberately omits environment values, so its
digest alone cannot satisfy this requirement; retain that observation separately
from the effective receipt.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_manifest/run_supervised -->
<!-- SYNTHESIS: explicit human requirement on 2026-11-14; integrates execution binding with the intended writer-intent/completion sequence -->

**Slice B implementation:** `prepare_execution` retains the receipt at
`<state>/executions/<coordinator-run-id>/execution.json`; preparation grants no
permission. `execute_prepared` requires the locked draining cursor with no readers,
COMMITs receipt/path/checksum in `intent_json["execution"]` and rechecks before and
after supervised invocation. The runtime is this checkout's standalone Python with
`-I -B -m raw_sensor_compact.cli`, DuckDB 2.0.0 and identities of public executable,
native engine and compactor source artifacts. Existing prototype intents receive no
fabricated receipts. Receipt reads require exact canonical bounded bytes, strict
shape/types and one nonsymlink regular inode; command budgets apply before publication.

For active S3 roots, the SDK/profile/environment selection resolves once and the
receipt records the non-secret endpoint/region/cache/retry policy. Frozen credentials
are repr-excluded and passed ephemerally in an allowlisted environment with no
inherited scope, profile re-resolution, Python injection or credential-file fallback.
The default extension cache is `<state>/extensions`. No credential value or secret
hash is retained. Spill and phase archive must be separate from ledger/runtime/data
roots. Individual engine ceilings remain within 32 GB memory/64 GB spill; they do
not qualify aggregate process-tree RSS/disk use or a reduced-limit operating budget.

The combined coordination focus passes 194 tests, including 44 receipt/launch cases
and real local empty/destructive synthetic migrations. Eight recorded active-path
failures precede hardening repairs. **Every `execute_prepared` launch still becomes
`BLOCKED`, without cursor advance.** A separate v3 normal-success prototype now
exists, with hardened local controls passing and service qualification pending.
Injected SDK tests make no endpoint requests. Actual S3, macOS, service
and representative resource gates remain open. The full-main receipt regression
passes 537 tests (three skips). Separate verification now checks completion-side
identity without reopening; frozen verifier-foundation full regressions pass 547
main tests (three skips) and 431 standalone tests (two skips), before ledger-v2
authority integration. See
[[wiki/work/dbt-compaction-coordination/verification]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/execution.py §prepare_execution/load_execution/recheck_execution/execution_environment; ../Wintap-PyUtil/wintappy/coordination/writer.py §execute_prepared; ../Wintap-PyUtil/wintappy/coordination/ledger.py §begin_writer; ../Wintap-PyUtil/tests/test_coordination_execution.py -->

**Partial slice C:** standalone read-only verification independently checks original
archive/data and current/historical entity evidence. Main `verify_prepared` binds
the committed receipt/intent and clean writer/verifier shutdown, rechecking them
after invocation. Original checkpoints are checked against their own retained
generation while allowing forward evolution. Main entity mode now requires the
independently initialized ledger high-water and verifies against its retained exact
generation; the returned candidate does not advance high-water or permissions.
Neither adapter nor verifier success advances a cursor or grants access. Initial
affected checks pass 259 standalone/204 main tests after eight active-path repairs;
new authority integration passes 236 main/299 standalone focus tests. The subsequent
v3 history/atomic-completion prototype passes 298 combined main focus controls and
641 full-main tests (three skips); service qualification remains pending.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/wintappy/coordination/verification.py -->

## 4. DuckDB ledger model

**Implementation status:** dcc-01 supplied the protocol/ledger library before the
current Linux service overlay. The original v1 reservation/outbox/intent gate passed 54 focus and 397 full
main tests (three skips). Ledger v2 preserved those permissions/identities
and adds explicit confirmed compatible v1 upgrade, retained authority proofs/audits
and verified high-water initialization/freshness enforcement. The new v3 prototype
adds `COMPLETED`, retained completion proofs and an internal atomic normal-success
transition. Hardened completion/upgrade and independent semantic/compatibility/
paging/secret controls pass, with ten active failures before repairs. Full standalone
passes 439 tests (two skips); combined main focus passes 298 tests and full main
passes 641 tests (three skips) on the unchanged revision.
Current audited blocked-run recovery supports fresh original-clean completion and
separately bound exact checkpoint repair. Original-bound deletion disposition additionally
requires complete original migration evidence and unchanged survivors/outputs;
general incomplete migration or entity maintenance remains unsupported. The
table model below describes the full planned service,
not an installed or fully qualified deployment.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py; wiki/work/dbt-compaction-coordination/verification.md -->

**Intentional-retry local gate closed, not Linux accepted:** ledger v4 adds explicit compatible v1/v2/v3
upgrade and bounded predecessor-linked intentional-retry dispositions. Failed
originals remain `BLOCKED`; fresh receipt/new-owner/disposition COMMIT never advances
the cursor or temporarily opens admission. The Linux `retry-hour` command requires
human cannot-resume confirmation/reason, fresh distinct preflight/prelaunch evidence
and exact original/new migration identities before independently verified completion.
Public one-hour `compact` validators remain unchanged. Pre-freeze service/history/
upgrade controls pass. A separate 275-identity successor freeze is created/checked;
standalone focus passes 45 and affected passes 248; main focus passes 119, with
unchanged identities after each result. Standalone full passes 554/two opt-in S3 skips
with unchanged identities; main affected passes 607/one isolated-local migration
opt-in skip with unchanged identities. Full main passes 880/three opt-in skips with
unchanged identities, closing local successor regressions. Distinct entity-only
ownership and endpoint/resource qualification remain open. Native-Mac stays separate. See
[[wiki/work/dbt-compaction-coordination/verification#Intentional-retry ownership — active, not accepted]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py; ../Wintap-PyUtil/wintappy/coordination/intentional_retry.py; ../Wintap-PyUtil/wintappy/coordination/service.py §main -->

**Opt-in v5 schema staging, not entity permission:** explicit confirmed
`Ledger.upgrade(..., target_version=5)` converts compatible v1–v4 under one lock/
COMMIT, preserving raw cursor, dispositions, proof bytes and existing readers.
Default initialization/upgrade stays v4 and ordinary open never migrates. Separate
entity-run/evidence tables required empty history at schema closure; the later typed
exclusion overlay has focused evidence only. Durable publication authentication and atomic
entity completion are unfinished.
Seven actual v4 upgrade crash/lost-ack controls and 37 expanded compatibility controls
pass; the 43-control genuine-history focus passes with all 286 identities unchanged,
while existing-ledger first compatibility retains two diagnostic failures/149 passes.
Default-v4 refusal wording is restored without test/refusal changes. Repaired focus
passes 46 with all 286 repair identities unchanged; repaired compatibility passes 151
with complete report/identity review. Schema compatibility is closed on that separate
freeze. These schema results do not
qualify entity launches or Linux acceptance.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_upgrade_entity_schema/_validate_entity_schema_origin; ../Wintap-PyUtil/tests/test_coordination_entity_upgrade.py; ../Wintap-PyUtil/tests/test_coordination_entity_schema.py -->

The read-only adapter authenticates separately supervised entity input observations
under owner-free v5 exclusion, never permission or authority initialization. It binds
actual canonical single-link request/command/capture/shutdown, exact original windows
and bounded fingerprints/counts, without main data SQL. The first 21 controls retain
missing-module failures; first adapter rerun retains one command-byte acceptance defect.
Exact canonical command/shutdown-byte repair passes 27 controls with complete report
and all 288 frozen identities reviewed. Broader input qualification, typed post-COMMIT
ownership and durable original-generation publication authentication remain separate.
Expanded input qualification retains nine failures/22 passes: hour/aggregate equality
is missing, and clock refusal follows read-only verifier launch. Adapter-only exact
totals/early-clock repair preserves controls; combined rerun passes 58 with complete
report and all 289 contract-repair identities reviewed. Input-authentication focus is
closed, not typed ownership, launch/completion/publication or successor regressions.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_verification.py; ../Wintap-PyUtil/tests/test_coordination_entity_observations.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_observation_qualification.py -->

Exclusion-only typed source retains 33 fixture-upgrade failures/one v4 pass (34.61 s),
with complete lossless report/291-identity review; no typed assertions or crash children
execute in that run. Independent DuckDB cursors cannot see transaction-local staged v5 tables.
Same-connection SQL-limited keyset pages now retain nested lookup safety and staged
row/audit visibility; typed history/budget validation precedes owner-ID/JSON reads.
The unchanged repair rerun passes 34 controls (125.03 s), complete report/all 291
identities reviewed. Genuine typed COMMIT/restart/lost-ack and post-COMMIT input
evidence is established. Separate staged history/budget-before-fetch/keyset-tail/
semantic focus passes 24 (79.82 s), complete report/all 292 identities reviewed with
no runtime change. Main combined typed/input/schema/receipt/original-ledger compatibility
focus passes 336 (884.70 s) on the unchanged successor freeze; standalone entity-verifier
focus passes 141 (105.56 s), complete reports/all 292 identities reviewed. Exclusion-only
focus is closed. Next is read-only original-bound current-generation completion
authentication, not authority/publication or completion permission.
Entity launch/completion/publication/recovery and wider qualification remain open;
none of these controls certify representative retained-state sizing.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_intent.py §validate_history; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate; ../Wintap-PyUtil/tests/test_coordination_entity_intents.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_intent_history.py -->

Current-generation read-only completion adapter is an active successor, not accepted.
Separate first red retains 44 import-masked failures (342.12 s), complete lossless
report/all 293 identities reviewed. New main adapter binds typed originals, acknowledged
same-session exclusion, actual post-COMMIT inputs, CLI/archive/capture/shutdown and
fresh standalone completion evidence. Canonical verifier bytes and pretty-printed CLI
bytes retain distinct identities; replay retains original bootstrap provenance.
`publication: None` and exact genesis/immediate-successor current generation refuse
historical certification. No ledger/authority/cursor/live-acknowledgment transition,
even on refusal. Unchanged 44-control rerun retains two helper failures / 42 passes
(470.91 s); complete report/all 294 identities reviewed. Duplicate helper `prelaunch`
arguments mask two refusal assertions before adapter invocation. Fixture-only repair
is next, without changing runtime/assertions; completion qualification/affected/full
remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_completion.py; ../Wintap-PyUtil/tests/test_coordination_entity_completion_observations.py -->

Exact two-line helper-only repair now permits keyword `prelaunch` overrides to reach
the adapter. Runtime/refusal assertions and other 293 identities unchanged; separate
294-identity all-44-control rerun passes 44 (471.51 s), complete three-line report/all
identities reviewed. Both masked refusals now execute without launch/mutation; initial
completion-observation focus closed, not expanded artifact/data or affected/full gates.
Separate 67-control artifact/data/non-mutation module is fully reviewed and lint/format-
clean, preserving all 294 initial-focus identities. First run passes 67 (353.73 s), exit 0;
complete three-line report/all 295 identities reviewed, hash unchanged. Expanded read-only
completion-observation focus closed, not combined/affected/full or writer/service gates.
Next is an unchanged distinct combined 447-main/141-standalone focus freeze. Contract-only checks
cannot replace actual-original rechecks, fresh independent data verification or durable
original-generation publication.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_qualification.py -->

Combined standalone focus passes 141 (110.49 s); complete four-line report/all 295
identities reviewed, hash unchanged. Main focus passes 447 (1729.40 s), exit 0; complete
nine-line report/all 295 identities reviewed, hash unchanged. Combined read-only focus
closed, not affected/full or entity writer/service gates. Next is durable original-generation
publication retention after fresh current-only completion under the same lock, with no
owner/authority/cursor/launch transition; add genuine red controls before source work.
Historical requests require authenticated retained publication, not caller dictionaries.

The separate publication-retention red module now specifies fresh current-only completion
under acknowledged original typed ownership, then immutable `entity-original-publication`
evidence/audit retention with no owner/authority/cursor/launch transition. The core remains
exact standalone `COMPLETION_FIELDS` with `publication_sha256: None`; the authenticated
accessor supplies it for future historical requests, never today's aggregate. Reopen uses
bounded typed JSON/history only, with no runtime reconstruction or relaunch. Real COMMIT/
lost-ack controls require BLOCKED ownership after uncertainty while preserving committed
evidence. First red retains 46 import-masked failures (402.36 s), exit 1; complete
1,772-line report, both direct child diagnostics and all 296 unchanged identities reviewed.
Children exit 1 at import, not 87; no publication COMMIT or semantic refusal executes.
Publication runtime/history support were absent at first-red review. Separate bounded
immutable retention/accessor and same-transaction authentication pass all unchanged 46
controls (629.02 s), exit 0, on the distinct 297-identity successor; complete three-line
report/all identities reviewed, hash unchanged. Initial focused evidence only, not expanded/
combined/affected/full or entity writer/service acceptance.
Retain original core/observation/audit only after fresh current-only completion and actual-
original rechecks. Ordinary history/accessor reads retained JSON, never reconstructs from
runtime files or today's aggregate. Success grants no ownership/authority/cursor/launch/
acknowledgment transition; committed lost acknowledgment blocks the typed original while
preserving evidence. Completion/recovery/service permission still has no fallback.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publications.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_publication.py; ../Wintap-PyUtil/wintappy/coordination/entity_intent.py §_budget/validate_history -->
<!-- SPECULATIVE: atomic completion/recovery, entity permission and combined/affected/full qualification remain separate -->

Separate 77-control qualification now specifies rehashed retained envelope/core/observation/
audit and canonical-JSON refusal, actual UTF-8 SQL budgets/positive boundaries before owner
or payload reads, real same-connection materialized keyset tails and non-mutating corrupted
reopen. A genuine original publication/audited block anchors rollback-isolated corrupt rows;
malicious tail fixtures are never accepted completed history. Reviewed diagnostic-retaining
runner plus two unchanged original crash controls pass 79 (100.90 s) on the distinct
298-identity successor. Complete report/sidecar, both actual 93-byte exit-87 diagnostics
and all source/runner/operator identities reviewed after notification. The actual selected
COMMIT hooks preserve BLOCKED original exclusion/raw cursor and absent-before/retained-after
publication; all fixtures remain retained. Expanded publication focus closed with runtime/
controls unchanged, not entity permission/recovery, combined/affected/full or wider Linux.
Complete expanded-green wiki/privacy review/fresh scoped checks pass. A distinct unchanged
298-identity combined freeze and separate diagnostic-retaining runner freeze prepare the
570-main/141-standalone focus. Complete 312-line prepared wiki/privacy review and fresh scoped
checks pass. Standalone passes 141 (109.28 s), complete report/sidecar and all source/runner/
operator identities reviewed. Main passes 570 (2430.83 s), complete report/sidecar, both actual
93-byte exit-87 publication diagnostics and all source/runner/operator identities reviewed
after notification. Both focuses complete/all fixtures retained, runtime/controls unchanged;
combined focused gate closed, not entity permission/recovery, affected/full or wider Linux.
Complete successor wiki/privacy/fresh checks precede separate explicit-v5 writer red/source work.
The separate writer red is now reviewed: 22 import-masked failures (45.76 s), exit 1,
with four actual child import failures before hooks and no competing-lock execution.
It establishes no successful history, launch, COMMIT or recovery authority. Distinct
completion evidence remains a design prerequisite; original publication is immutable,
and original intent authority/cursor bindings must survive legitimate forward evolution.

**Selected writer successor design (not implemented/qualified yet):** retain a distinct
128 KiB completion record in the existing typed event stream, with its own contiguous
sequence/hash predecessor, exact original intent/receipt, independently observed current
completion, original raw-cursor predecessor and original authority-proof identity. The
existing v5 tables/columns and unique-per-run original publication remain unchanged.
`Ledger.entity_evidence` may return authenticated completion for a completed run; the
original-publication accessor must read its immutable table row directly. Completion and
its small audit, typed owner transition and a distinct typed authority-reference proof
commit atomically, never into raw completion history and never advancing the raw cursor.
Public one-hour authority/receipt validation remains unchanged; typed authority references
are authenticated through the separately retained fresh completion observation.

History authenticates the original authority predecessor and original cursor's retained
raw-history prefix, not today's aggregate or merely today's high-water. Unresolved owners
without completion still require exact current authority/cursor binding. Typed records,
small audits and publications share the existing aggregate cap; SQL byte/count budgets
precede owner/JSON fetches and same-connection materialized keyset pages include staged
rows. Preserve `2 * MAX_ENTITY_RUNS + publications` for unresolved audits: completion-record
capacity may account only for separately retained records, not globally increase that
allowance. A completion acknowledgment loss retains committed evidence/authority but blocks
the typed original; explicit original-clean resolution requires actual original artifacts,
retained post-COMMIT inputs, clean shutdown and fresh standalone current-only verification.
It cannot manufacture historical completion, replay entities, issue grants or relax the
read-only adapter's live-session gate. Pending-publication repair/retry remains separate.
The initial five-file implementation is source-reviewed/formatted, not qualified. It still
refuses retained-completion acknowledgment resolution rather than overwriting originals;
a distinct immutable audited resolution design remains required. Duplicate-completed-receipt
refusal must not block old success, and authority keyset validation must compare its scanned
count against SQL count/size bounds so invalid low sequences cannot disappear.
The first runtime run passes 40/42 controls; retained failures distinguish a mixed-clock
fixture from the missing immutable acknowledgment disposition. Recovery must refuse a clock
before the retained block before launching a verifier; a corrected synthetic reopen fixture
does not authorize production-clock rollback. Original completion/publication remain immutable.

Selected acknowledgment-resolution successor: separate `entity_resolution_record` events
retain bounded immutable envelopes (128 KiB per record, 10,000 records, shared 64 MiB
aggregate), a global sequence/predecessor chain, the original completion/intent/publication
identities, exact blocking-audit identity and fresh current-only standalone observation.
`entity_resolved` audits and uncertainty audits are separately bounded at 16 KiB. Original
completion, publication, authority checks and raw history are never replaced. Ordinary reopen
authenticates retained JSON only; actual original intent/prelaunch/CLI/archive/verifier bytes
are rechecked before a new verifier during explicit resolution. Exact original completion
core equality is required; historical publication is not a fallback. No schema/public-validator
change, raw cursor movement or reader grant follows from this resolution.

Resolution-COMMIT acknowledgment uncertainty retains its immutable record and restores
`BLOCKED` with a distinct audit. A later attempt must bind that uncertainty and obtain a new
fresh observation; neither retained completion nor retained resolution alone permits release.
The original-clean recovery completion's after-COMMIT exception requires the same conservative
exclusion, without adding a duplicate original block or rewriting original recovery evidence.
Before any verifier or new artifacts, recovery clocks must meet the retained blocking-evidence
floor. These are selected design requirements, not implementation or qualification claims.
<!-- SYNTHESIS: acknowledgment-resolution successor grounded in ../Wintap-PyUtil/wintappy/coordination/entity_history.py; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py; ../Wintap-PyUtil/tests/test_coordination_entity_resolution.py -->

The reviewed runtime successor implements this selected design in separate resolution events,
including immutable uncertainty references after original-clean completion COMMIT. It leaves
the existing v5 schema/public contracts/authority and publication originals unchanged. Record,
audit and aggregate caps include all retained successors; unresolved-only audit allowance is
unchanged. Qualification is pending the distinct 71-control run, not accepted by source review.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py; ../Wintap-PyUtil/wintappy/coordination/entity_intent.py -->
<!-- SYNTHESIS: successor design grounded in ../Wintap-PyUtil/wintappy/coordination/entity_intent.py; ../Wintap-PyUtil/wintappy/coordination/entity_publication.py; ../Wintap-PyUtil/wintappy/coordination/entity_completion.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py -->

The later corrected frozen writer/history/resolution focus passes all 71 controls, and the
unchanged post-resolution publication affected follow-through passes all 123. Complete retained
evidence and frozen identities are reviewed; these close only those local focused/affected
slices, not entity-wide integration. A separate 12-control successor now prepares genuine
completion-process-death qualification: actual verifier evidence precedes original COMMIT
hooks, atomic committed history remains distinct from an uncommitted blocked original, and
neither confers raw completion, cursor movement, queued-reader release or a fresh authority
token on reopen. Existing caught acknowledgment-loss blocking controls are unchanged. This
new successor subsequently passes all 12 genuine process-death controls (283.57 s); full
actual diagnostic/capture/artifact/archive and frozen-identity review closes only this
focused gate. Eight uncommitted originals need fresh audited recovery; four actual COMMITs
retain their atomic results, without raw/reader release. Stronger SQL-tail/forward-evolution,
maintenance/service and broader Linux acceptance remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_crashes.py; ../Wintap-PyUtil/tests/test_coordination_entity_writer_history.py; ../Wintap-PyUtil/tests/test_coordination_entity_resolution.py -->

The separate completion/resolution SQL qualification successor prepares 44 controls with
runtime unchanged. Two genuinely executed completions, fresh dispositions and immutable
publications must supply originals; no fabricated observations or substituted SQL results.
Budget refusal must precede typed payload/identifier fetches. Real one-row sequence pages
must materialize before nested owner lookups and reject tail nulls/holes/predecessors;
full-history scans must reach unsupported/orphan audit tails. Typed SQL stays on the original
transaction connection. Unrelated reader-only cursors and the actual writer receipt prerequisite
remain valid; rollback cannot be blocked by a guard failure. Prepared source/collection is not
executed evidence, a runtime repair or acceptance of forward evolution/service/wider Linux.
The frozen successor subsequently passes all 44 controls (62.53 s). Complete independent
read-only artifact/archive/ledger/fixture/identity review authenticates genuine originals and
all transaction-local budget/keyset/tail/non-mutation evidence. Inspection-only table/count
mistakes are preserved and corrected against actual schema/14 typed events; runtime and
controls remain unchanged. Only this focused history gate closes; authenticated raw-cursor/
authority forward evolution, original-bound maintenance/service and broader Linux remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py -->

The separate raw-cursor/authority forward-history successor plans genuine interleaved typed
and raw completions, immutable publications/acknowledgment resolutions and genuinely new
STOP evidence. Historical scope binds retained original authority/raw prefixes rather than
today's authority/cursor; comparison uses original versus actual final CLI host statistics,
not historical checkpoints versus current aggregates. All 23 frozen controls subsequently pass
(87.45 s), with complete independent original/artifact/archive/ledger/fixture/identity review.
The original guessed-DRAINING inspection fails and is retained; actual final raw completion
requires OPEN because the next hour is not yet due. Typed completions alone remain DRAINING;
neither historical originals nor OPEN on reopen restore fresh authority or admit the queued
reader. Four actual CLI completions, 16 verifier groups and 34 archive records authenticate;
all 306 source identities and 150 retained files/one symlink stay unchanged. Only this focused
forward-history gate closes; no runtime/schema/public-validator/service change is part of this
control-only successor. Original-bound recovery/maintenance/service and wider acceptance stay open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_forward_history.py; ../Wintap-PyUtil/wintappy/coordination/entity_history.py §validate_original_scope/raw_cursor_identity -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py §validate_completion_proof/_build_completion_proof; ../Wintap-PyUtil/wintappy/coordination/coordinator.py §writer_due; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_require_entity_authority -->

Entity initialization uses `verify_authority_prepared` under the locked
`OPEN`/`DRAINING` ledger with explicit confirmation/reason, no prior baseline and
zero readers. It separately invokes the standalone `--authority-only` verifier,
authenticates receipt/ledger/dataset/request/command/capture/shutdown and rechecks
the evidence before one proof/audit COMMIT. Ordinary checks require the live committed
chain to contain the exact retained generation. Freshness is a same-locked-session
token, reset by reopen/failure and consumed by successful writer intent; existing
reader reservations are never revoked. An arbitrary caller-supplied report/anchor
cannot initialize authority. Proofs retain predecessors and are bounded at 64 KiB
each/10,000 checks, with complete validation in 256-row batches and refusal rather
than truncation. Frozen full authority regressions pass 579 main tests (three skips)
and 439 standalone tests (two skips), before completion/history work. These controls reject
whole-journal/snapshot rollback with a retained ledger and same-ordinal forks, but
cannot prove freshness of a coherently restored ledger plus authority store.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/verification.py §verify_authority_prepared; ../Wintap-PyUtil/wintappy/coordination/authority.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_validate_authority_checks/_require_entity_authority -->

The first dcc-02 slice now supplies locked `writer_due`/`tick`, with all bounded
listings completed before atomic terminal-first ingestion. A later batch conflict
cannot retire an earlier reservation. Due observations drain before admission and all
reservations exclude the callback, delivered or not. Any callback result/failure
becomes `BLOCKED`; bounded scalar observations are diagnostics, not completion
evidence. There is no cursor advancement, reopening or integrated writer supervisor. The
admission/draining focus passes 100 tests; its full main passes 443 (three skips).
The subsequent Linux-supervision/evolving-clock focus passes 142 cases and full
main passes 485 (three skips). Slice A subsequently passes 150 affected main cases
and 493 full-main tests (three skips), before receipt implementation. dcc-02 remains open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; wiki/work/dbt-compaction-coordination/verification.md -->

Collaborative review on November 14 confirms an uncovered timing defect: ingestion
can cross grace after the clock observation, allowing a new reservation before
the post-publication refresh enters `DRAINING`. A real-ledger/synthetic-S3 probe
was red; slice A now refreshes immediately after ingestion, with formal red/green
clock evidence. The human confirms that requests not yet reserved at
the deadline must remain queued, while existing reservations are preserved.
See [[wiki/work/dbt-compaction-coordination/verification]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick -->

The Linux-only supervisor library uses a fresh isolated subreaper to adopt/reap
detached and nested command descendants; root exit alone is not shutdown. It
captures bounded local logs/reports, stops trees on interruption and setup/capture
failure, and refuses uncertain worker outcomes. Evolving UTC observations now
refresh after listings/grant delivery/callback, rejecting backwards/broken clocks.
These primitives are not integrated completion authority: all tick callbacks still
block. External services, non-Linux clients and power-loss/resource budgets remain
unqualified. There is no production service adapter or installed scheduler.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py; ../Wintap-PyUtil/wintappy/coordination/coordinator.py; wiki/work/dbt-compaction-coordination/verification.md -->

**Native-Mac exception, synthetic lifecycle-qualified; platform acceptance pending:**
the isolated process-group candidate is wired to the native coordinated reader and
passes 12 actual-Mac synthetic controls. A surviving supervisor may treat no live
members in the dedicated process group after wrapper completion as a normal-release
signal; this is explicitly best effort and does not prove that an escaped/detached
descendant stopped. On timeout, supervisor death or uncertain group state, retain the
reservation for manual verification. The limited controls do not qualify real DBT/data,
actual S3, production service or representative resources. Linux's subreaper contract
and local-only direct DBT remain unchanged.
<!-- SOURCE: Human native-Mac risk decision, conversation 2026-11-15. -->

The schema is small and independent of DBT analytics models:

| Table | Principal fields / purpose |
|---|---|
| `metadata` | Schema version and dataset/root configuration binding. |
| `dataset_state` | Dataset ID; mode `OPEN`, `DRAINING`, `WRITING`, `BLOCKED`; `next_hour`; active run ID; block reason. |
| `jobs` | Job UUID; request digest; requested window/action; first-seen time; state `WAITING`, `GRANTED`, `RELEASED`, `CANCELLED`; grant UUID; grant/release times. |
| `outbox` | Message key, immutable serialized payload/digest and publication state. Durable intent permits retry after a lost S3 acknowledgment. |
| `compaction_runs` | Coordinator run UUID, selected UTC hour/action, state, start/end times, report path, return code, CLI metrics run ID when available, and separate migration/entity/checkpoint completion evidence. |
| `events` | State-transition/recovery audit entries keyed by dataset, job or run. |
| `authority_checks` | Implemented v2 predecessor-linked receipt/ledger/dataset-bound verification proofs; retained independent entity generation anchor, not completion permission. |
| `completion_evidence` | Implemented v3 bounded predecessor-linked normal-success proofs, committed atomically with completed run, optional authority, exact-hour cursor and backlog mode. |

**`GRANTED` includes not-yet-delivered grants.** A single transaction reserves the
reader in `jobs` and inserts its grant into `outbox`; only after COMMIT may the
coordinator PUT that grant. It never decides there are zero readers from an S3
listing or an advisory status file. All unreleased reservations count.

Similarly, COMMIT `WRITING` plus the run record **before** starting compaction.
A subsequent process discovering `WRITING` after a crash treats it as unresolved
and enters `BLOCKED`. It must not grant readers or launch a replacement writer.
The old child may still exist even though the parent process lock disappeared.

Terminal records are retained for v1. Re-listing an old request cannot grant it
again. Requests/releases/grants use stable UUIDs and immutable payloads, so
retries do not create a new reader or repeat a completed job.

## 5. S3 artifacts and protocol

Keep coordination outside every telemetry, entity and processing-metrics scan root:

The implemented v1 protocol uses 32 lowercase hexadecimal identities, strict
message shapes and canonical dataset/active-root/entity-policy binding. Transport
reads cap each message at 1 MiB and each listing at 64 MiB of original bytes,
10,000 records and 10,000 pages; cyclic pagination/errors/budget exhaustion fail,
never return truncated permission inputs. These are library tests with fake S3,
not endpoint qualification or a terminal-history pruning policy.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/protocol.py -->

```text
s3://<bucket>/coordination/<dataset-id>/
  requests/<job-id>.json       # written by that client
  grants/<job-id>.json         # written only by the coordinator
  releases/<job-id>.json       # written by that client after it stops
  cancellations/<job-id>.json  # client abandons a request without starting work
  status.json                 # coordinator-written, advisory summary
```

| Message | Required content |
|---|---|
| Request | Protocol version, job UUID, dataset ID, effective input roots, action, selected window, creation timestamp. Canonical serialization produces `request_sha256`. |
| Grant | Job UUID, request digest, dataset/root binding, unique grant UUID, granted timestamp, mode `read`. |
| Release | Job UUID, request digest, grant UUID, completion timestamp, DBT exit status; asserts the local source-reading children have stopped. |
| Cancellation | Job UUID, request digest, timestamp; asserts this wrapper has stopped waiting and will never act on a late grant. |
| Status | Dataset mode, outstanding reader count, pending jobs, next eligible hour, active run/block reason and observed timestamp. Never permission to start. |

The wrapper polls its exact grant key (proposed interval: ten seconds). The tick
paginates requests and terminal messages; message handling is idempotent. A
coordinator processes releases/cancellations before admissions and retains
cancellation tombstones even if their request has not yet appeared. A cancellation
also suppresses any pending grant publication. A canceled client never honors a
grant, even if an earlier PUT becomes visible later.

PUT retries use the same key and exact payload. A timeout means unknown delivery,
not failure to acquire: never create a replacement job and discard the first
reservation. On conflicting contents or ambiguous terminal metadata, preserve the
reservation and report the discrepancy. Delayed/missing requests only delay grants;
delayed releases only keep readers reserved. API errors are not empty results.

No client starts based on `status.json`, object age or the absence of a writer
marker. No grant has an automatic expiry in the proposed first version. S3 records
are retained initially; later garbage collection must preserve terminal knowledge.

### Polling budget

With the proposed defaults and an available dataset, allow up to one 60-second
tick interval for request pickup and grant publication in the same tick, then up
to ten seconds for the client to see the grant: **70 seconds before DBT starts**.
The client uploads release immediately after its source-reading children stop;
the coordinator may take another **60 seconds** to retire the reservation.
Successful release upload lets the wrapper return without a coordinator acknowledgment.

The lifecycle polling budget is therefore about **130 seconds**, split across
startup and post-completion writer admission. One-minute client polling would
instead give the discussed 180-second budget; the client default remains ten
seconds. These estimates exclude processing, S3 visibility/retries, DBT runtime
and waits for active/due compaction or draining readers. Long-running writer ticks
hold the local lock and later cron invocations exit busy, so these are not hard
end-to-end deadlines.

## 6. Client changes and created files

### Local-only mode: current behavior and compatibility requirement

With normal DBT dependencies installed and DBT overrides unset, run from the
Wintap-PyUtil repository root:

```sh
export WINTAP_DATA_ROOT='/path/to/local-dataset'
make dbt-build
```

The root contains `raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/.../*.parquet`.
The Makefile discovers the local date bounds and defaults the analysis output to
`$WINTAP_DATA_ROOT/duckdb/wintap.duckdb`. Source validation accepts raw input
without a compacted directory; runtime scans select only globs with matching files.
Leaving `WINTAP_DBT_PROCESS_ENTITY_ROOT` unset/empty skips entity validation and
enrichment. `configure_raw_sensor_access()` returns before S3 secret setup when
all inputs are local. These behaviors are already implemented.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §defaults; ../Wintap-PyUtil/scripts/check_dbt_config.py §validate; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §matching_raw_sensor_partition_globs; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_process_entities; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §entity_mode -->

**Required wrapper behavior:** resolve the effective raw, compacted, optional
entity and active processing-metrics roots before any coordination initialization.
If all are local, directly
run the existing source preflight/build without requiring AWS or coordination
settings, initializing a ledger/client job directory, sending messages or waiting
for a grant. This mode needs only the main DBT environment, with no compactor
installation or entity bootstrap. Apply the same routing to standalone source,
test and docs targets. Existing AWS/coordination settings alone must not activate
the protocol. Local analysis DuckDB output remains part of the ordinary workflow.

R5 now ignores explicit metrics overrides in offline root resolution and S3 setup
with entities disabled. Preserve this behavior in client routing; entity-enabled
remote metrics remain a coordinated input. Empty active overrides use the sibling
default. Real local `make dbt-build` and active-remote controls pass.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

When switching an existing shell from S3 to local, clear previous dataset, raw,
compacted, entity and processing-metrics overrides so inputs really are local; reset
output/window overrides as desired. The canonical guide includes the reset commands:
[[wiki/workflow/wintap-etl-data-flow#Local-only single-user workflow]].

### Shared-S3 mode

Users retain their existing AWS and WINTAP DBT configuration, plus proposed settings:

```sh
export WINTAP_COORDINATION_DATASET=research-dataset
export WINTAP_COORDINATION_ROOT='s3://<bucket>/coordination/research-dataset'
export WINTAP_COORDINATION_POLL_SECONDS=10
make dbt-build
```

The coordination root and effective source roots are checked against the grant.
The AWS profile name is not the dataset identity. Different users may use different
profiles to access the same configured dataset. All S3-backed inputs, including
a remote compacted, entity or active metrics root paired with a local raw root,
require coordination.
An absent local compacted directory is still local; root classification must not
depend on finding files or on whether an AWS profile happens to be configured.

### Shared-S3 Makefile / wrapper lifetime

Today, `dbt-build` depends on `dbt-check-source`, which performs a separate
`dbt run-operation validate_raw_sensor_source` before `dbt build`. Proposed change:
leave only offline configuration checks outside the wrapper; move the remote
source preflight **inside the same grant as the build**.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §dbt-check-source/dbt-build; ../Wintap-PyUtil/scripts/check_dbt_config.py §validate -->

Entity-enabled preflight now requires a version-4 checkpoint and its committed
generation receipt for every
selected process-bearing hour. A grant conveys exclusion, not coverage: active or
unprocessed hours can still fail preflight. Report missing coverage and release;
never hold a reader grant waiting for the excluded writer to catch up, silently
trim the requested window or switch off entities. Checkpoint presence alone does
not prove that a restored snapshot is current. The R1 safety implementation also
requires current-state authority and receipt lineage; see
[[wiki/work/dbt-compaction-coordination/implementation_plan]].

```text
make dbt-build
  offline config checks
  Python client.dbt-build
    persist job/request locally; PUT request; wait for exact grant
    validate grant identity; record it locally
    run dbt run-operation validate_raw_sensor_source
    if successful, run dbt build
    wait for every managed source-reading child to stop
    persist and PUT release; preserve DBT return code
```

Launch existing DBT commands as supervised subprocess argument lists, using the
configured main runtime/DBT command prefix. Do not acquire in a DBT on-run hook:
source discovery and separate preflight calls also need protection. Do not release
after bronze discovery: bronze models are views and later build/test queries can
still read S3. Ctrl-C/termination first stops and waits for the child process tree;
release happens afterward. If child termination cannot be established, retain the
grant for recovery. Implement supervision for the supported client platforms.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/dbt_project.yml §models; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §matching_raw_sensor_partition_globs -->

Proposed `dbt-check-source`, `dbt-test` and `dbt-docs` standalone invocations also
use the shared wrapper when they access S3. Offline config/output checks stay local.
Post-build SQL over materialized local tables needs no grant; SQL over raw-backed
views with S3 inputs needs a new shared grant. A generic shared-command wrapper
can cover such queries without extending one DBT grant indefinitely.

Client metadata lives under
`<client-state>/wintap-coordination/jobs/<job-id>/` (configurable with
`WINTAP_COORDINATION_CLIENT_STATE_DIR`): `request.json`, `grant.json`,
`result.json`, and either `release.json` or `cancellation.json`. Save a pending
terminal message locally before upload so a later retry command can resend it.
If release delivery is uncertain, report the outstanding job ID and retain the
record. Never silently call it unlocked. Existing local DBT database, `target/`
artifacts and logs remain the analysis outputs; clients write only coordination
JSON to S3. One job ID belongs to exactly one invocation and is never reused.

## 7. Tick sequence, hourly selection and writer result

The following is the **full intended sequence**. The uncommitted Linux overlay
now implements receipt-bound same-lock execution, independent verification and
atomic completion before grants; the conservative callback tick stays separate.
Local reader/checkpoint/deletion regressions pass, but endpoint/resource and broader
recovery qualification remain open. No production scheduler is installed.

1. Acquire the local process lock; load config; open/validate the ledger.
2. Recover pending messages and ingest terminal messages. Unresolved `WRITING`
   becomes `BLOCKED`; active reader reservations survive restart. In `BLOCKED`,
   record terminal messages/status and exit without admissions or writer launch.
   Only explicit recovery can clear that state.
3. Compare `next_hour + one hour + grace` with UTC now. If eligible, enter
   `DRAINING` **before granting new readers**, and preserve the selected hour.
4. In `OPEN`, record/publish eligible shared grants. In `DRAINING`, admit none;
   if readers remain, publish advisory status and exit until the next tick.
5. With zero reserved readers, commit `WRITING` and a fresh run record. Invoke
   the existing locked compactor for `[next_hour, next_hour + one hour)` with
   explicit roots, events, limits, target size and validated source deletion.
   Include entity/metrics/policy settings only when that mode is selected and
    initialized. The exclusive interval spans entity publication, raw migration,
    final checkpoint publication/verification, child shutdown and receipt COMMIT.
    Before launch, durably retain and bind the required non-secret execution receipt
    to that intent; verify the actual invocation uses its resolved settings.
6. Capture the report, exit status and elapsed time. Reopen admissions only after
   the selected hour has a recorded successful migration disposition: validations
   succeeded and expected source deletion completed, plus verified entity and
   checkpoint completion when enabled. An empty hour can complete
   with an explicit empty result. A skipped existing destination is not proof of
   completion unless already backed by the ledger's verified receipt.
7. On success, advance `next_hour` transactionally by one hour. Stay `DRAINING`
   if backlog remains; otherwise enter `OPEN` and grant queued readers. On failure,
   partial/ambiguous completion, failed deletion or missing report, enter `BLOCKED`
   and retain the cursor and diagnostic evidence.

The human-confirmed November 14 review contract makes step 7 one indivisible
ledger COMMIT: retain the verified completion evidence, complete the run, advance
the cursor and select the backlog/admission mode together. Queued grants follow
that COMMIT, never a merely successful callback or parsed report. Execution and
effective-configuration binding, independent data/authority/high-water verification
when enabled, and supervised shutdown remain prerequisites. The receipt and
separate verification libraries and ledger-v2 high-water checks implement part of
this gate; the subsequent v3 normal-success prototype has hardened local evidence
and full local regressions, but integrated service qualification remains open.
<!-- SYNTHESIS: human-confirmed review contract on 2026-11-14, consistent with the full intended sequence above -->

The existing `execute_prepared` API intentionally blocks even clean success. The
separate `execute_and_complete_prepared` prototype implements the same-lock clean-
live-intent launch/fresh-verification/transaction path, not automatic promotion of
an existing blocked run. Keep that conservative launch API and require explicit
confirmed, audited recovery for every previously blocked or restart-blocked intent. A completion
entrypoint obtains its own fresh independent evidence; it does not accept a passed
verifier dictionary as a completion capability. Service admission must reobserve UTC after
completion COMMIT, so a grace crossing before grants preserves backlog priority.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/writer.py §execute_prepared; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_block_unresolved_writer; ../Wintap-PyUtil/wintappy/coordination/verification.py §verify_prepared -->
<!-- SYNTHESIS: implementation seam preserving the approved normal-completion versus uncertain-recovery boundary; subsequent v3 prototype remains unqualified -->

The v3 transaction retains the predecessor-linked proof and completion audit, marks
the run `COMPLETED`, retains/advances optional authority and selects the exact next
hour/backlog mode together. Its committed origin and proof/run/audit/cursor checks,
including a retained prior-completion clock floor, are local integrity controls,
not global-clock or coherent restored-ledger/store freshness. Proofs are bounded
at 128 KiB each and 10,000 completed runs without pruning. Raw/entity abrupt-death
controls and three genuine hours through instrumented two-row pages pass locally;
they do not qualify physical power loss or representative retained-state resources.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_complete_writer/_validate_completion_history/_completion_clock_floor; ../Wintap-PyUtil/tests/test_coordination_completion.py; ../Wintap-PyUtil/tests/test_coordination_completion_controls.py -->

The coordinator must inspect both exit status and structured report. The current
CLI can report `completed_with_deletion_errors` and has a separate reconciliation
command; these evolving result shapes must be integrated against the qualified
compactor version before implementation is finalized.
Inspect individual event/hour results as well: a top-level `completed` can coexist
with `skipped_existing`. Require verified completion evidence for every configured
event/hour before advancing the cursor; a skipped destination needs a prior
ledger receipt or explicit reconciliation. Capture both stdout and stderr, where
the CLI emits error reports.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours/reconcile_deletions -->

**Checkpoint boundary:** `processing_metrics` is coverage evidence, not the
coordinator ledger or a migration receipt. DBT accepts
`completed_with_deletion_errors`; entity-only replay records `completed` and
`deletion_status=completed` with `raw_status=not_run`. A later replay overwrites
the fixed-hour checkpoint. Retain full per-event migration receipts independently,
link the CLI-generated metrics run ID to the coordinator run, and require final
checkpoint verification before successful writer completion. Do not reconstruct
the cursor from checkpoint status or `bootstrap_start`.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows/ProcessingMetricsStore; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

Scheduling is a durable cursor, not simply “now minus one hour” on every tick.
One hour per tick bounds a writer invocation; backlogs still take priority until
caught up. The starting cursor is explicitly initialized after checking existing
data. Late arrivals to already-compacted hours retain the existing compactor's
semantics and are not silently rebuilt by this scheduler. The normal uncompacted
tail is the active hour plus grace-period/backlog data, rather than a strict
one-hour bound.

## 8. Failure and recovery behavior

| Event | Proposed behavior |
|---|---|
| Second cron tick while compaction runs | Local lock busy; exit without opening the ledger or starting another writer. |
| Crash after grant COMMIT, before/during PUT | Reader remains reserved; resend the identical grant from outbox. |
| Client cancels while waiting | Persist/publish cancellation, never start from a late grant; coordinator tombstone retires the reservation. |
| DBT exits unsuccessfully | Release after the platform's accepted shutdown check; return the DBT failure. Linux requires its supervised descendant tree to stop. Native Mac may release after the wrapper finishes and no live members are observed in its dedicated process group, accepting escaped-descendant risk; timeout, supervisor death or uncertain group state retains the reservation. It has not mutated the source dataset. |
| Client machine disappears or release PUT fails | Keep its reservation; display job age/status; retry release or manually resolve. |
| Writer/host crashes | Persistent `WRITING` becomes blocked/uncertain. Confirm old child stopped and reconcile data before reopening. |
| Partial compaction or raw/compacted overlap | Keep the dataset blocked until reconciliation; a stopped writer alone does not permit coordinated reads. Live diagnostic observations remain inconclusive and cannot reopen admissions. |
| Entity or checkpoint publication fails, including after raw deletion | Keep `BLOCKED`; reconcile all configured hosts and selected-hour checkpoints as well as raw migration. Old compatible checkpoints are not a freshness guarantee. |
| Missing/corrupt ledger | Refuse ordinary operation; recover under an explicit maintenance procedure with all outstanding clients stopped. |
| Operator restores an older ledger backup | Use the same maintenance recovery procedure. A valid but stale backup cannot be assumed to contain every issued grant. |
| S3 unavailable or malformed/conflicting messages | Fail the tick/request visibly and preserve recorded ownership. Never infer emptiness from an error. |

Current Linux operator commands live in `service.py`: `status`, `release-reader`,
`resolve-hour`, `repair-checkpoints`, `repair-deletions` and
`abandon-maintenance`, all under the same
local lock; mutating recovery additionally requires explicit confirmation and an
audit reason. Manual
reader release requires confirming that the original wrapper and its children
have stopped and cannot later use an already-issued grant. Removing the S3 grant
alone does not revoke a cached permission. Current hour resolution records only
independently verified completion. A reconciled disposition permitting intentional
retry is a separate planned operation; it must not falsely complete the failed
original or advance the cursor. Neither operation may blindly mark a nonzero
compactor exit successful.

Entity-enabled `reconcile-delete` now publishes checkpoints. R4's independent local
archive retains original migration/deletion evidence and candidates before coverage
can be overwritten. Exclusive `checkpoints-repair` validates that archive, surviving
data and current/historical entity authority, then republishes original-generation
rows without entity replay or replacing original history. Conflicting coverage
requires explicit disposition and is retained in the new repair archive. Missing
original candidates/migration evidence or uncertain/partial deletion stays blocked.
The command does not acquire coordination permission or reopen a ledger; future
operator integration must retain exclusivity through independently verified ledger
receipt/cursor commit. The current narrow Linux path now implements that sequence
for an already blocked entity/deletion writer's recorded exit-2 checkpoint-publication
failure: separate receipt/intent before repair launch, block-preserving maintenance,
then exact independently verified repaired resolution. Failed/crashed maintenance
requires audited cannot-resume abandonment; repair/abandonment alone never advances
the hour or admits readers. Original failure observations/archive remain unchanged.
The deletion path likewise requires a separate committed maintenance
intent, authenticates every original migration before deleting unchanged survivors,
never replays entities and records new disposition checkpoints without changing
original archived candidates. Separate independent one-hour resolution retains
original exit 2 and repair exit 0; repair/abandonment alone never reopens admission.
Its local regressions are closed; Linux/endpoint/resource qualification remains open. The broader
verified retry and general entity-maintenance interfaces remain planned. A new
read-only retry prerequisite supports only one raw-only event/hour with deletion
disabled, the exact retained failed-merge intent, unchanged original inputs and
an absent output hour. It authenticates the original exit-2 capture/shutdown and
publishes an exact request before supervised independent verification, then rechecks
the original/context. It does not mutate data, change the ledger/cursor, confer retry
permission or certify completion. Its hardening/regression work remains separate
from the accepted deletion baseline.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/retry.py §verify_retry_prepared; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/retry_verifier.py §verify_retry/main -->
R2/R3 integrity/provenance are repaired in `7d2b7f8`; R1's
authority journal binds current snapshots and historical receipt lineage, but whole
authority rollback now rejects against ledger-v2's retained exact anchor. Restoring
that ledger too still needs independent external operator evidence and exclusion.
Historical checkpoint hashes cannot be equated to the latest evolving snapshot.
Actual coordinated recovery and endpoint/power-loss behavior remain unqualified.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §reconcile-delete; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §repair_checkpoints; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py; ../Wintap-PyUtil/wintappy/coordination/service.py; ../Wintap-PyUtil/wintappy/coordination/recovery.py; ../Wintap-PyUtil/wintappy/coordination/maintenance.py; wiki/work/dbt-compaction-coordination/verification.md -->

Manual abandoned-job recovery is the proposed simple v1 policy. Automatic stale
grant expiry remains unselected: a suspended/disconnected DBT process can still be
alive. No heartbeat timeout is treated as permission for a writer to overlap it.

## 9. Implementation order and verification plan

1. Implement message identities and the transactional DuckDB state machine.
2. Exercise the coordinator with local fake DBT/compactor children and delayed S3
   messages; prove no reader/writer overlap and writer priority.
3. Integrate the DBT wrapper around preflight/build; test exit/cancellation/release
   behavior, including process-tree termination and durable release retry. Verify
   the local-only bypass and classification of each possible S3 input root.
4. Integrate the qualified compactor CLI and one-hour cursor, then cron/config.
5. Qualify using an isolated S3 test dataset: overlapping DBT readers, due writer,
   queued reader, crash/restart and incomplete-migration cases.

Required failure-point checks include grant COMMIT before lost PUT acknowledgment;
delayed grant after cancellation; release before request visibility; duplicate
messages; crash after writer launch; child surviving parent termination; missing
ledger refusal; misleading success/skip/partial reports; midnight and grace
boundaries; missed ticks and multi-hour backlog. Assertion: no writer interval
overlaps a granted reader interval, and no coordinated S3 reader starts without
its own grant. The diagnostic exception is separately qualified by the utility's
live-overlap/warning/resource gates; it cannot relax these coordinated assertions.

Local compatibility gate: a full raw-only `make dbt-build` with no compacted
directory, no entity store, no AWS/coordination settings and no installed compactor
must preserve the existing local model/schema/results contract and create only
ordinary DBT outputs. Assert zero coordination calls/job records. Repeat routing
with unused AWS/coordination settings present, and verify a remote compacted or
entity or active metrics override cannot mistakenly take the local bypass. An
unused remote metrics override with entities disabled must cause neither S3 setup
nor coordination after integration.

Add failure gates for final checkpoint failure after successful deletion,
reconciliation without checkpoint publication, replay overwriting migration
metrics, incompatible identity policy/ceiling, unfinished-window preflight release,
snapshot corruption/rollback and bootstrap metadata across incremental hours.
Measure incremental entity work with realistic retained snapshots: the imported
three-day large-budget bootstrap does not qualify the proposed server limits or
hourly full-state hashing/rewriting time.

**Design evidence:** live Makefile, DBT path/materialization definitions, runtime
pins and current compactor CLI/report paths were read on November 13. The
conditional-write caveat comes from the recorded endpoint probe, not a new test.
These are design/source checks; coordination runtime tests await implementation.
Local-only defaults, missing-compacted handling, S3 setup bypass and entity-disabled
branches were also checked in live source on November 13. Earlier local/disabled
regression evidence is recorded in
[[wiki/work/durable-process-entity-manager/verification]]; the future wrapper's
local compatibility gate remains part of implementation qualification.

**Artifact checks, November 13:** both Markdown frontmatters, grounding paths,
wikilinks, relative diagram links and JSON examples validate. The draw.io XML has
two pages with 42 and 44 cells, unique IDs, valid references and in-page geometry.
Both pages render in the draw.io viewer; renderer label bounds show no overflowing
vertex labels. `git diff --check` passes. The complete additions were reviewed for
persistent-content privacy.
