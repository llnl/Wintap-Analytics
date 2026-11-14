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
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint.md
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, design, dbt, compaction, coordination, cron, duckdb, s3, drawio]
---

# Cron, S3 messages and DuckDB coordination

**Selected architecture:** one scheduled coordinator on the compaction server,
S3 messages for clients, and a **local DuckDB coordination ledger**. Coordinator
paths, commands and schemas proposed below are implementation specifications;
the coordinator and DBT wrapper are not implemented yet.

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
| DBT wrapper | Each user's machine, for one invocation | Request access; supervise local DBT children; publish release after they stop. |
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

This is cooperative coordination: all tools that read or modify these roots must
participate. Ordinary S3 permissions do not enforce the protocol. Direct ad-hoc
queries and read-only verification need shared access; entity initialization,
replay, rebuild/cutover and manual reconciliation need exclusive maintenance
access through the same authority, including while resolving `BLOCKED` state.
Sensor uploads continue under the existing collection
contract; a read grant stabilizes compaction activity, not incoming collection.

## 2. Source artifacts to create or change

All paths in this table are relative to **Wintap-PyUtil**. They are proposed files,
not copies of implementation into the wiki.

| Path | Language / format | Contents |
|---|---|---|
| `wintappy/coordination/__init__.py` | Python | Package marker. |
| `wintappy/coordination/protocol.py` | Python | Versioned JSON validation, dataset/root binding, UUIDs, canonical request digest, boto3 messages and idempotent retries. Shared by server and client. |
| `wintappy/coordination/ledger.py` | Python + embedded DuckDB SQL | Transactions, state transitions, durable grant outbox, terminal job records and scheduling cursor. |
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
| `/var/lib/wintap-coordination/runs/<run-id>/command.json` | Selected hour, executable/arguments and configuration identity. |
| `/var/lib/wintap-coordination/runs/<run-id>/result.json` | CLI report, return code, timing and coordinator disposition. |
| `/var/lib/wintap-coordination/runs/<run-id>/stdout.log`, `stderr.log` | Captured child output; available even if report parsing fails. |
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

## 4. DuckDB ledger model

The schema is small and independent of DBT analytics models:

| Table | Principal fields / purpose |
|---|---|
| `metadata` | Schema version and dataset/root configuration binding. |
| `dataset_state` | Dataset ID; mode `OPEN`, `DRAINING`, `WRITING`, `BLOCKED`; `next_hour`; active run ID; block reason. |
| `jobs` | Job UUID; request digest; requested window/action; first-seen time; state `WAITING`, `GRANTED`, `RELEASED`, `CANCELLED`; grant UUID; grant/release times. |
| `outbox` | Message key, immutable serialized payload/digest and publication state. Durable intent permits retry after a lost S3 acknowledgment. |
| `compaction_runs` | Coordinator run UUID, selected UTC hour/action, state, start/end times, report path, return code, CLI metrics run ID when available, and separate migration/entity/checkpoint completion evidence. |
| `events` | State-transition/recovery audit entries keyed by dataset, job or run. |

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

The current S3 macro consults an explicit metrics override even with entities
disabled. Integration must consistently ignore that unused override in both routing
and S3 setup; entity-enabled remote metrics remain a coordinated input. This is
a required compatibility adjustment, not current behavior.
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

Entity-enabled preflight requires a compatible version-3 checkpoint for every
selected process-bearing hour. A grant conveys exclusion, not coverage: active or
unprocessed hours can still fail preflight. Report missing coverage and release;
never hold a reader grant waiting for the excluded writer to catch up, silently
trim the requested window or switch off entities. Checkpoint presence alone does
not prove that a restored snapshot is current (review R1).

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
| DBT exits unsuccessfully | Release after children stop; return the DBT failure. It has not mutated the source dataset. |
| Client machine disappears or release PUT fails | Keep its reservation; display job age/status; retry release or manually resolve. |
| Writer/host crashes | Persistent `WRITING` becomes blocked/uncertain. Confirm old child stopped and reconcile data before reopening. |
| Partial compaction or raw/compacted overlap | Keep the dataset blocked until reconciliation; a stopped writer alone does not make the dataset readable. |
| Entity or checkpoint publication fails, including after raw deletion | Keep `BLOCKED`; reconcile all configured hosts and selected-hour checkpoints as well as raw migration. Old compatible checkpoints are not a freshness guarantee. |
| Missing/corrupt ledger | Refuse ordinary operation; recover under an explicit maintenance procedure with all outstanding clients stopped. |
| Operator restores an older ledger backup | Use the same maintenance recovery procedure. A valid but stale backup cannot be assumed to contain every issued grant. |
| S3 unavailable or malformed/conflicting messages | Fail the tick/request visibly and preserve recorded ownership. Never infer emptiness from an error. |

Proposed operator commands in `coordinator.py`: `status`, `release-reader`, and
`resolve-hour`, all under the same local lock and with an audit reason. Manual
reader release requires confirming that the original wrapper and its children
have stopped and cannot later use an already-issued grant. Removing the S3 grant
alone does not revoke a cached permission. Hour resolution records either verified
completion or a reconciled state ready for an intentional retry. It does not
blindly mark every nonzero compactor exit successful.

Current `reconcile-delete` does not publish checkpoints, even when its entity
update path runs. Recovery may need explicit entity replay/checkpoint repair after
raw reconciliation, under the same exclusive maintenance state; replay alone does
not certify deletion. Preserve the migration evidence before that replay replaces
metrics. Restore the SQL validator's integrity checks and bootstrap-provenance
handling identified in review R2/R3 before relying on them for recovery. Snapshot
restoration/cutover must also resolve R1's freshness gap; historical checkpoint
hashes cannot simply be equated to the latest evolving snapshot.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §reconcile-delete; wiki/work/dbt-compaction-coordination/implementation-review.md -->

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
overlaps a granted reader interval, and no S3 reader starts without its own grant.

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
