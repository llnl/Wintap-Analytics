---
title: "Verification: Scheduled DBT and Compaction Coordination"
type: concept
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_freshness.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - ../Wintap-PyUtil/tests/test_process_entities.py
  - ../Wintap-PyUtil/tests/test_entity_freshness.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py
  - ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql
  - ../Wintap-PyUtil/tests/test_dbt_source_validation.py
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../Wintap-PyUtil/tests/test_checkpoint_repair.py
  - ../Wintap-PyUtil/tests/test_effective_input_roots.py
  - ../Wintap-PyUtil/tests/test_coordination_protocol.py
  - ../Wintap-PyUtil/tests/test_coordination_ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/protocol.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/tests/test_coordination_tick.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/execution.py
  - ../Wintap-PyUtil/wintappy/coordination/writer.py
  - ../Wintap-PyUtil/tests/test_coordination_execution.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/verification.py
  - ../Wintap-PyUtil/wintappy/coordination/authority.py
  - ../Wintap-PyUtil/wintappy/coordination/completion.py
  - ../Wintap-PyUtil/tests/test_coordination_completion.py
  - ../Wintap-PyUtil/tests/test_coordination_completion_controls.py
  - ../Wintap-PyUtil/tests/test_coordination_authority.py
  - ../Wintap-PyUtil/tests/test_coordination_verification.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_completion_verifier.py
  - ../Wintap-PyUtil/scripts/dcc_macos_baseline.py
  - ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json
  - ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py
  - ../Wintap-PyUtil/.gitignore
  - ../Wintap-PyUtil/uv.lock
policy: agent-editable
last_validated: 2026-11-14
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/dbt-compaction-coordination; ../Wintap-PyUtil/tests; ../Wintap-PyUtil/extras/raw-sensor-compact/tests
tags: [feature-work, verification, coordination, review, regression]
---

# Verification: Scheduled DBT and Compaction Coordination

## Test Commands

Review baseline: Analytics `91f741e`, PyUtil `c782f63`. Both repositories were
pulled with `git pull --ff-only`; Analytics fast-forwarded from `d904559` and PyUtil
was already current. Existing unrelated PyUtil untracked data/environment artifacts
were preserved. No code implementation, cron deployment or push occurred.

The preceding sentence describes the review baseline, not the authorized work below.

### Authorized integrity/provenance slice — red/green

Human authorization explicitly requires active-path red/green regressions, bounded
SQL validation, stable bootstrap provenance and rollback-safe forward evolution.
Implementation is committed locally in PyUtil as `7d2b7f8`; no production scheduling or push.

Before changing implementation, added `tests/test_entity_integrity.py` and ran in
the standalone compactor:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_entity_integrity.py
```

**Red: 75 failed, 10 passed** across 85 cases. Forty corruptions are exercised
independently through CLI `entities-verify` and `update_entities()`; the producer
unknown-key case and four provenance cases add five tests. Failures include
duplicate keys, noncanonical hosts, invalid bounds/evidence, non-parent scalar/flag
disagreement, and bootstrap drift on changed/unchanged updates, replay and resumed
init. The ten already-rejected corruption cases remain negative compatibility
controls. A preliminary verify-first run was strengthened to independent entrypoint
parameterization so update failures are visible even when CLI verification fails.

After implementation, the same 85 cases plus the existing entity/CLI regressions
pass: **123 passed**. Expanded positive controls cover valid identity/lifetime/parent
conflicts, missing/sentinel parents, empty initialized hosts, retained evidence,
no-op replay and temporary-relation cleanup with `Evidence.restore` replaced by a
failure hook. Actual CLI replay also proves original bootstrap agreement in report,
snapshot and published checkpoint. The expanded new-test run is **92 passed**;
additional positive controls cover signed-integer boundaries and an empty parent
candidate set remaining a retained entity with missing context. All **94 new tests**
pass in the final standalone run.

Implementation reuses the SQL reducer to derive all expected scalar/flag columns
in separate spillable temporary relations and compares them null-safely. It also
validates unique/valid keys, canonical stored hosts, exact JSON fields/array types,
numeric/string/parent element types, duplicate candidates and ten-digit calendar
publication-hour bounds. Python retains no decoded entity cache. Existing validated
snapshot metadata is reused rather than reconstructed from the update start.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §validate_state/_validate_evidence/_reduce_state; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

Full standalone regression command (same isolated wrapper):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Final result: **234 passed, 2 skipped** (opt-in S3), 49.68 seconds. Changed-file Ruff
lint/format checks pass. The first main cross-runtime rerun caught three lowercase
CLI-host validation failures; canonicalized the caller's host while still requiring
canonical stored rows. That repair is included in the final standalone tests and
a full main-suite rerun initially returned **314 passed, 3 skipped, 1 failed** in
203.35 seconds. The remaining default-config test reads a pre-existing ignored local
settings file containing a dataset setting. It independently fails in the checkout
and passes from a disposable working directory (**4 config tests passed**). The
settings file is untouched. The fully isolated main-suite rerun passes:
**315 passed, 3 skipped**, 202.14 seconds, including all raw/mixed/compacted entity
DBT builds and CLI verification. Its child pytest invocation uses the absolute
main-environment Python and test-directory paths, `PYTHONPATH=<checkout>`, and a
disposable working directory plus `TMPDIR`/`--basetemp` under `/tmp/opencode`.
No unmodified test expectation was relaxed.

An added empty-parent positive fixture initially triggered a legitimate normalization
rewrite because `json_merge_patch` changed JSON key ordering. Corrected the fixture
to preserve canonical serialization; no-op replay and entity retention now pass.

### Bounded synthetic validation probe

A disposable standalone DuckDB 2.0.0 fixture creates 20,000 recorded synthetic
entities, then runs initial update/publication and unchanged replay with Python
`Evidence.restore` disabled. Settings: two threads, 256 MB DuckDB memory and
512 MB temporary storage. Results: initial update 2.468 seconds; replay 1.913 seconds;
20,000 entities; unchanged replay; traced Python peak **1,178,319 bytes**; process
peak RSS **344,120 KiB**. The fixture and spill directory were automatically removed.

This demonstrates SQL-backed validation at small scale, not a Python-versus-SQL
benchmark or a realistic accumulated-state budget. Traced Python allocations are
not total RSS, DuckDB memory limits are not total-process RSS caps, and spill usage
was not measured. Multi-million-entity steady-state qualification remains open.

### Pre-R1 freshness probe — historical red

Used the real main-suite fixture and isolated compactor: retain the original snapshot,
add next-hour process evidence, publish via `entities-replay`, then run real DBT
`validate_raw_sensor_source`. Historical checkpoints contain **two distinct aggregate
hash populations** and forward preflight exits **0**, as required. Restore only the
original snapshot, retaining checkpoints: snapshot integrity correctly passes, but
DBT preflight also exits **0** when freshness should fail. The fixture is disposable
and removed automatically; it does not modify a real dataset.

R1 is therefore **not repaired** by the R2/R3 slice. This independent probe separates
integrity from freshness and demonstrates why every historical hash cannot be
compared to today's aggregate. The next slice needs current-state authority,
historical receipt/lineage validation, recorded publication-intent recovery and an
explicit legacy-state upgrade/cutover contract.

### R1 current-state authority and lineage — red/green continuation

Milestone commits: PyUtil `7d2b7f8`, Analytics `739e64f`; both are local only.
Added formal operational regressions before implementing R1. Standalone command:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_entity_freshness.py
```

**Red: 10 failed, 1 passed**. Integrity-valid snapshot rollback, empty replacement,
bootstrap replacement, missing authority and expected-host rebinding independently
pass CLI verification/update when they should fail. The forward-evolution/replay
control passes. The real main-runtime DBT command against its new same-named test
module returns **8 failed, 1 passed**: four current-state and four historical
checkpoint corruption cases pass preflight incorrectly; differing historical hash
populations correctly pass forward preflight. Both red runs used disposable
`TMPDIR`/pytest roots under `/tmp/opencode` and cleaned their fixtures.

Implemented the selected Parquet authority journal, strict generation/binding/host
lineage, content-derived receipt IDs, pending-before-host and committed-after-recheck
publication, and version-4 coverage linked to its own receipt. CLI rejects untrusted
current bytes/provenance; DBT checks current semantic identities and historical
receipt evidence without equating old hashes to today's aggregate. Read-only local
DBT with entities disabled retains the direct, authority-independent path.

The initial focused pass found two fixture-scope issues: the valid empty-parent
fixture manually replaced a committed snapshot, and the old S3 snapshot failure
hook now intercepted an earlier authority PUT. Constructed the valid empty-parent
candidate before initial publication and restricted that hook to snapshot keys;
the same active verification/no-op and lost-ack recovery expectations are retained.
Added separate authority PUT/ack failure points, altered-intent/input rejection,
receipt corruption and missing-ancestor tests. Expanded standalone focus passes
**164 tests**. An initial main focus caught incompatible unnamed-row JSON between
DuckDB 1.5.6 and 2.0.0. Named-struct JSON hashing with 1,024-row digest batches
repairs that boundary; **14 real-DBT tests pass**, including Unicode and multiple
digest chunks.

Three further real-DBT cases (null checkpoint status, null hour end and altered
window start) were added before their repair: **3 failed**, then strict null-safe
status, exact hour/window receipt checks and explicit legacy schema rejection were
implemented. Final full runs include these cases plus paired fresh entity/metrics
root rebuild/cutover with old evidence preserved. The full standalone suite passes
**266 passed, 2 skipped**, 91.46 seconds. Initial isolated main full run returns
**334 passed, 3 skipped, 1 failed**, 349.35 seconds: the threshold mismatch still
fails closed, but its earlier authority rejection omits the existing test's
`Processing metrics` diagnostic. Preserved that expectation by explaining the shared
authority/metrics roots/hosts/policy binding in the diagnostic; the targeted test
then passes. The full isolated main acceptance rerun passes **335 passed, 3 skipped**,
348.05 seconds (`/tmp/opencode/dcc-r1-main-accepted.txt`). R1's regression gate is
accepted; R4/R5 and actual coordinated lifecycle qualification remain open.

All test wrappers use the project's Python, not the system Python. Two initial
wrapper launches failed before pytest because the system Python lacked modern
`subprocess.run` arguments; corrected wrappers produced the recorded red results.
No remote qualification, real dataset mutation, push or scheduler deployment.
The local writer's directory-fsync path is qualified on Linux only; other writer
platforms and actual endpoint failure/recovery remain unqualified.

### R4 independent phase evidence — historical red

Added five operational tests before implementation and ran standalone
`tests/test_phase_evidence.py`: **5 failed**, 4.64 seconds. The injected final
checkpoint failure follows successful deletion and surviving compacted outputs,
but leaves no original phase archive. Additional cases lack a stable run mapping,
immutable migration evidence across replay, exclusive original-generation checkpoint
repair, refusal to certify skipped hours and rejection of run-identity reuse.
The tests use the active `cli.run()` entrypoint with Namespace fields representing
the proposed CLI options, avoiding argparse failures as a substitute for behavioral
evidence. Fixtures are synthetic, bounded and automatically removed.

### R4 integration and additional negative evidence

The original five cases pass after CLI/archive/migration/checkpoint repair integration
(`dcc-r4-focus.txt`: **5 passed**, 4.24 seconds). They now parse the real CLI options.
Additional active-path probes were captured before their repairs:

- `dcc-r4-hardening-red.txt`: **4 failed, 18 passed**, 16.25 seconds. Repair could
  incorrectly succeed after a checkpoint PUT changed a source, output or entity;
  deletion could proceed after source mutation during intent-record publication.
- `dcc-r4-finalstate-red.txt`: **2 failed**, 1.46 seconds. Ordinary archived compaction
  could certify completion despite an output/entity change during checkpoint PUT.
- `dcc-r4-byteidentity-red.txt`: **2 failed**, 1.11 seconds. Same-size/mtime source
  mutation during deletion intent escaped metadata checks, and duplicate JSON keys
  were accepted by the archive loader.

Repairs recheck streamed byte identities after deletion intent, surviving migrations
and current SQL-validated entity authority before/after checkpoint writes, all final
checkpoint rows, and exact canonical archive bytes. The first expanded affected
suite passes **64 tests** (39.57 seconds). Further archive budget/link/fsync/symlink,
scope, conflicting-coverage disposition, reconciliation and protocol/hour tests are
being qualified. An expanded archive run initially passes 38 tests with one fixture
failure: its fake S3 `ObjectFile` omitted the existing normalized `raw_sensor/`
inventory prefix. Corrected the synthetic fixture, not the path-safety requirement.
That fixture correction retains the scope checks.

### R4/R5 prerequisite acceptance — final revision

`dcc-r4-directory-links-red.txt`: **2 failed** before repairing unflushed new
directory links. The accepted full standalone suite includes that repair:
**307 passed, 2 skipped**, 119.90 seconds (`dcc-r4-standalone-accepted.txt`),
including **41 phase/archive tests**. The real two-runtime checkpoint test injects
a second checkpoint failure after deletion, evolves entities, then repairs the
original generation with unchanged entity/original archive bytes and a successful
real DBT full build (`tests/test_checkpoint_repair.py`). Conflicting newer coverage
is explicitly retained and replaced in a new repair archive; it is never silently
discarded. These passes qualify the tested synthetic Linux paths, not power loss.

R5 captured **two real behavioral failures** and **one missing-resolver failure**
before fixing active-root routing (`dcc-r5-red.txt`). Four active-remote controls
initially had fixture-only failures; the corrected fixtures preserve their remote
activation expectations and all four pass (`dcc-r5-controls.txt`). Final **7 routing
tests pass** (`dcc-r5-green.txt`), including direct full local `make dbt-build` with
entities disabled and an unused remote metrics override, without credentials.

The combined isolated main suite passes **343 passed, 3 skipped**, 410.83 seconds
(`dcc-r4-r5-main-final.txt`). It started before the directory-link repair. The final
affected-main run includes that repair and passes **51 passed, 1 skipped**,
331.06 seconds (`dcc-r4-r5-final-revision.txt`): checkpoint repair, entity freshness,
effective roots, process entities and compacted inputs. Both use absolute main
interpreter/test paths, disposable working directory, `PYTHONPATH=<checkout>`,
`TMPDIR`, pytest `--basetemp` and `-p no:cacheprovider`; unrelated local settings
remain untouched. Scoped Ruff lint passes and the earlier 14-file format check
passes. Both repositories' `git diff --check` pass. Corrected artifact validation
recognizes the existing index/log catalogs rather than parsing their body separators
as YAML: **7 frontmatters, 117 grounding paths, 354 links** and added-content
IP/account-home-path scans pass across nine changed wiki files. Diff review uses
only synthetic identifiers/aggregate results; no identifier disclosure is authorized.

R4/R5 and dcc-00 are prerequisite regression acceptance only. Real coordinated
writer lifecycle, endpoint recovery, whole-authority rollback high-water enforcement
and realistic accumulated-state resource budgets remain separate gates.

### dcc-01 protocol/ledger — implementation baseline

Added strict protocol and real-DuckDB ledger tests before implementation:
**26 failed** solely because `wintappy.coordination` was absent, 0.17 seconds
(`dcc-01-missing-red.txt`). This is missing-implementation evidence, not 26
behavioral regressions. The first protocol implementation passes its initial
**16 tests**, 0.05 seconds (`dcc-01-protocol-initial.txt`). Ledger implementation
and additional behavioral failure points are next; no coordinator/client or real
writer has been launched by this slice.

### dcc-01 transactional authority and hardening — red/green

The initial ledger implementation passes its **10 tests**, 1.61 seconds
(`dcc-01-ledger-initial.txt`). Added behavioral negative probes before fixes:

- Protocol: **6 failed, 16 passed**, 0.16 seconds
  (`dcc-01-protocol-hardening-red.txt`): unhashable action/policy fields did not
  produce protocol errors, failed GET body transfers leaked raw exceptions,
  aggregate listing byte limits were missing, cyclic continuation tokens continued
  listing, and deeply nested JSON leaked a raw recursion error.
- Ledger: **6 failed, 19 passed**, 3.11 seconds
  (`dcc-01-ledger-hardening-red.txt`): orphan writer intent, reader/writer overlap,
  stored request-digest corruption and extra schema columns were accepted on reopen;
  S3 state directories created unintended local paths; transport could publish
  beneath a telemetry scan root. Corrupt-ledger tests require refusal without
  rewriting/recreating authority, not merely a later failed writer.

The repaired combined focus passes **47 tests**, 3.20 seconds
(`dcc-01-hardening-green.txt`). Final expansion adds real abrupt process death
before/after grant and writer COMMIT with WAL recovery, no reader expiry despite
old timestamps, conflicting remote grant retention, failed-initialization refusal,
short streamed reads and original whitespace accounting in byte budgets:
**54 passed**, 6.03 seconds (`dcc-01-final-focus.txt`). Command:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_coordination_protocol.py tests/test_coordination_ledger.py
```

All runs use the isolated main-runtime wrapper described above. Reservations and
outbox commit before PUT; terminal state suppresses pending grants; writer/run
intent commits before any caller-managed launch. A second real process gets busy
before opening DuckDB. Unresolved writer intent becomes `BLOCKED`, retaining the
cursor and independent CLI/coordinator IDs. There is no cursor-advance or reopening
API yet; actual writer completion and high-water enforcement remain dcc-02/dcc-04
integration obligations. Synthetic crash/WAL evidence is not power-loss evidence.

Final combined scoped Ruff lint passes; **20 files** pass format. Both repositories'
whitespace checks pass, including a separate newline/whitespace scan of **14
feature-owned untracked files**. Current wiki artifact checks pass seven
frontmatters, **127 grounding paths and 354 links**; added-content privacy scans
and the scoped code/wiki/new-file review retain only synthetic identifiers in
persistent wiki additions. Existing index/log catalogs are not parsed as YAML.
The full isolated main suite passes **397 passed, 3 skipped**, 414.36 seconds
(`dcc-01-main-final.txt`), including the final 54 protocol/ledger cases and the
R4 directory-link repair. dcc-01 is regression accepted after artifact review.
No scheduler, client wrapper, actual S3 qualification or real destructive child was
introduced. Unrelated settings/data and milestone commit anchors remain unchanged.

### dcc-02 controlled-clock scheduling — implementation baseline

Added `tests/test_coordination_tick.py` before implementation. The isolated main
wrapper returns **20 failed**, 1.05 seconds (`dcc-02-scheduling-missing.txt`), all
`ModuleNotFoundError` for `wintappy.coordination.coordinator`. This is missing-
implementation evidence, not 20 behavioral regressions. Tests specify UTC
midnight/grace boundaries, persisted oldest-hour selection, overlapping readers,
terminal-first cancellation, due-writer draining, queued and undelivered grants,
API failures, duplicate ticks, failed callbacks and a surviving synthetic child.

This first slice must reject unverified callback claims, including exit-zero
`completed`/`empty` results. Supervision, verified completion/cursor advancement,
backlog reopening and real compactor integration remain later qualification;
dcc-02 is not yet accepted. No production scheduler or real-data operation occurs.

### dcc-02 admission/draining and hardening — red/green

Initial tick plus protocol/ledger focus passes **74 tests**, 7.33 seconds
(`dcc-02-scheduling-initial.txt`). Added behavioral probes before repairs:

- **5 failed, 23 passed**, 3.04 seconds (`dcc-02-scheduling-hardening-red.txt`):
  later terminal/request conflicts or a later listing failure could retire an
  earlier reader reservation; callback observations were discarded; invalid
  writer commands were not rejected before access/admission. Completed listings
  followed by atomic terminal-first ingestion now preserve every prior reservation
  on batch failure. Early adapter/command validation and bounded untrusted scalar
  observations repair the other cases. Combined focus then passes **82 tests**,
  8.78 seconds (`dcc-02-scheduling-hardening-green.txt`).
- **2 behavioral failures**, plus **one fixture-only failure**, 7.82 seconds
  (`dcc-02-blocked-diagnostic-red.txt`). Missing or inconsistent blocked-state
  reasons were accepted on reopen. A test insertion accidentally moved the
  original open-ledger control into a blocked-writer fixture; restored that
  control without changing its expectation. The clean pre-fix rerun is
  **2 failed, 39 passed**, 7.25 seconds
  (`dcc-02-blocked-diagnostic-controlled-red.txt`). Reopen now rejects both
  diagnostic corruptions without recreating or changing database bytes.

Final combined focus passes **100 tests**, 12.35 seconds
(`dcc-02-scheduling-final-focus.txt`): 36 tick, 41 ledger and 23 protocol tests.
It adds atomic batch and blocked-disposition transaction failures, bounded
count/byte exhaustion, iterator failure, callback interruptions/identity mutation,
malformed/oversized/empty results and a real abrupt tick death with a surviving
synthetic child. The committed intent/cursor survive WAL recovery; a later tick
cannot launch a replacement or publish new grants. Only test-owned synthetic
children are terminated during cleanup. No real compactor is invoked.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_coordination_tick.py tests/test_coordination_protocol.py \
  tests/test_coordination_ledger.py
```

Runs use the absolute-interpreter/test-path, disposable-CWD main wrapper above.
The full isolated main regression passes **443 tests, 3 skipped**, 558.24 seconds
(`dcc-02-main-regression.txt`). This run qualifies the admission/draining revision,
not subsequent supervisor changes. Scoped Ruff lint and **22-file** format checks,
both repositories' whitespace checks and **16 feature-owned untracked-file**
newline/whitespace checks pass. Wiki review covers seven frontmatters, **135** live
grounding paths and **355** links across nine changed files. Addition privacy scans
and the complete wiki diff review pass; unrelated artifacts remain untouched.
The callback seam does not supervise or certify any writer: all returned claims
stay blocked and no cursor advance/reopening API exists. Its persisted scalar
observations are diagnostics, not full worker reports/phase receipts. Full child-
tree supervision, verified empty-hour completion, backlog advancement, advisory
S3 status and real CLI integration remain required before dcc-02 acceptance.

### dcc-02 Linux supervision — implementation baseline

Recorded **16 missing-module failures**, 0.19 seconds
(`dcc-02-supervision-missing.txt`), before adding the isolated Linux subreaper
supervisor. This is implementation-baseline evidence, not behavioral regression.
The first implementation passes **16 tests**, 2.93 seconds
(`dcc-02-supervision-initial.txt`): root exit with ordinary/detached descendants,
SIGTERM-resistant timeout, unrelated-child isolation, preserved run directories,
bounded stdout/stderr and exact structured-report checks. These tests do not
certify a writer or reopen admission. Interruption, nested reparenting, worker
failure and capture/publication error probes are next; dcc-02 remains unchecked.

### dcc-02 supervision and evolving clocks — recorded hardening

Captured before repairs, using the same isolated main wrapper:

| Report under `/tmp/opencode/` | Result | Active-path finding |
|---|---|---|
| `dcc-02-supervision-hardening-red.txt` | **2 failed, 20 passed**, 5.06 s | A second report read parsed unchecked replacement bytes; capture failure could leave a launched child and retain a false pre-launch shutdown assertion. |
| `dcc-02-supervision-setup-red.txt` | **3 failed, 23 passed**, 5.94 s | Selector setup failure did not stop the launched root; two malformed capture records raised raw key errors instead of coordination errors. |
| `dcc-02-supervision-scalar-red.txt` | **2 failed, 30 passed**, 6.86 s | Non-string status and enormous integer budgets raised type/overflow errors. |
| `dcc-02-supervision-control-red.txt` | **1 failed, 32 deselected**, 0.26 s | A nonreading worker with a large control payload produced a raw broken-pipe failure. The probe uses a short-lived synthetic worker; it does not measure an indefinite-hang deadline. |
| `dcc-02-supervision-exit-red.txt` | **1 failed, 3 passed, 30 deselected**, 0.97 s | An `exited` observation lacking the root exit code was accepted for report reads. |

The first two repairs pass **26 tests**, 5.78 seconds
(`dcc-02-supervision-hardening-green.txt`). Further scalar/control/exit repairs
validate metadata and budgets before use, require consistent root-exit/shutdown
evidence, use sealed bounded control memory instead of a potentially blocking
stdin pipe, and translate missing observations into coordination failures.
Unexpected capture/setup exceptions now kill/reap the launched tree before
propagating; unavailable subreaper support refuses launch. Report parsing consumes
exactly the checksum-verified bytes, never rereads the path to parse a replacement.

The evolving-clock baseline is **4 failed, 36 passed**, 7.26 seconds
(`dcc-02-evolving-clock-red.txt`), solely because `clock=` is absent; this is a
missing-interface baseline, not four behavioral regressions. Refresh observations
after complete listings, grant delivery and writer callback. Clock rollback/access
failure before ingestion retains reservations; post-write clock errors still block
the committed intent using the last valid observation before propagation.

Final combined focus passes **142 tests**, 23.13 seconds
(`dcc-02-supervision-clock-qualified-focus.txt`): **44 tick, 34 supervisor, 41 ledger,
23 protocol**. This includes real nested/`setsid` descendants, SIGTERM-resistant
timeout, unrelated-child isolation, caller INT/TERM/death cleanup, worker death with
a surviving workload and a real supervised callback holding the ledger lock. A
parsed exit-zero empty report still cannot advance the cursor or reopen admission.
Only synthetic test-owned processes are terminated during cleanup. No real
compactor or S3 endpoint was used. Intermediate combined focus reports retain
134/141 passes; the 142-test run is the final revision evidence.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_coordination_tick.py tests/test_coordination_supervisor.py \
  tests/test_coordination_protocol.py tests/test_coordination_ledger.py
```

The full isolated main run for this revision passes **485 tests, 3 skipped**, 609.86
seconds (`dcc-02-supervision-main-regression.txt`), distinct from the earlier **443-pass**
admission/draining revision. Scoped Ruff lint and **24-file** format checks pass;
both repositories' `git diff --check` and **18 feature-owned untracked-file**
newline/whitespace scans pass. Wiki checks cover **seven frontmatters, 145 live
grounding paths and 355 links** across nine changed files. Added-content privacy
scans and the complete 1,331-line wiki diff review pass; no actual host/account/IP
identifiers are added. Unrelated settings/data remain untouched. Linux
subreaper observations apply to cooperative descendant trees only, not external
services, hostile/cgroup containment or non-Linux client platforms. Workload,
startup/cleanup, control/log/report bounds do not certify filesystem/kernel I/O,
RSS or power-loss budgets. These observations are not migration/configuration
receipts; the command manifest deliberately omits environment values. Full service
binding, verified raw/entity/checkpoint completion, authority high-water enforcement,
transactional cursor/backlog/reopening and advisory status remain required.

### dcc-02 collaborative review — confirmed grace defect and completion contract

On November 14, a disposable controlled-clock probe exercised the live tick and
real main-runtime DuckDB ledger with synthetic S3. It called the original
`Ledger.ingest_many`, then advanced the injected clock before returning to the
tick; no ingestion/admission behavior was replaced. Invocation used
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<pyutil-checkout>
<pyutil-checkout>/.venv/bin/python -B -` from `/tmp/opencode`, with automatically
cleaned temporary fixture directories.

The pre-grace control returns `OPEN`, one reader and one grant. Advancing from
`00:09:59` to the `00:10:00` grace boundary during ingestion instead returns
`DRAINING` with one newly reserved reader and one grant. Expected: `DRAINING`, zero
readers/grants and one queued request. The probe exits 1 with **one behavioral
assertion failure**, not a pytest suite result; its control assertion passes.
Evidence: `/tmp/opencode/dcc-02-review-ingestion-clock-red.txt`.

The clock observation precedes ingestion and is reused for admission; the next
refresh happens after grant publication. This is a writer-priority defect, not
demonstrated reader/writer overlap: the new reservation still excludes the writer.
The human confirms that requests not yet reserved when grace expires must remain
queued. Refresh after ingestion before deciding admission; preserve existing
reservations. Formal regression and repair were pending at this review; slice A
subsequently records their red/green implementation below. The earlier 142/485
passes did not cover this boundary and are retained as historical run evidence.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick; ../Wintap-PyUtil/wintappy/coordination/ledger.py §ingest_many/admit -->

The human also confirms the intended completion gate: execution/configuration/run
binding, independently verified migration/deletion or empty-hour evidence,
entity/authority/checkpoint and independent high-water checks when enabled, and
confirmed supervised shutdown must precede success. Retain completion evidence,
complete the run, advance exactly one hour and select `DRAINING` for due backlog
or `OPEN` otherwise in **one ledger transaction**. Queued grants follow COMMIT;
uncertainty retains the cursor and blocks admission/replacement launch. A callback
claiming `empty` is not verified empty-hour evidence. This confirms the design,
not an implemented success API or dcc-02 acceptance. No code was changed during
this review, and no production writer/endpoint was exercised.
<!-- SYNTHESIS: human-confirmed review contract on 2026-11-14, consistent with wiki/work/dbt-compaction-coordination/design.md §7 and §8 -->

### dcc-02 review requirement — non-secret execution/configuration receipt

The human expressly requests an allowlisted, non-secret effective execution and
configuration receipt after reviewing the supervisor manifest's omission of
environment values. Requirement added to the brief, design, handoff and plan:
[[wiki/work/dbt-compaction-coordination/design#Required execution and configuration receipt]].

Acceptance evidence requested at this review: bind the actual qualified executable/runtime/arguments
and resolved roots/hour/run IDs/events/entity policy/deletion/budgets to durable
writer intent before launch; prove default/override/allowed-environment resolution,
receipt integrity and bounds, mismatched scope/command refusal and synthetic secret
exclusion from persisted artifacts/diagnostics. Post-launch uncertainty cannot
advance the cursor or reopen admission. A partial command manifest or exit-zero
report is insufficient. No implementation or behavioral test result is claimed
by this historical review. Slices B/C subsequently implement and verify the
receipt/separate-verification libraries below; dcc-02 remains unchecked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_manifest -->
<!-- SYNTHESIS: explicit human requirement on 2026-11-14, recorded before implementation -->

### Commit snapshot — November 14

Committed the 32 feature-owned PyUtil files as `fe7fcb5` on
`work/raw-sensor-compacted-union`: R1/R4/R5, protocol/ledger and tick/supervision
prototypes, tests and READMEs. Preserved unrelated data, environment files and
ignored settings. The source coordination README at that commit explicitly records the
unrepaired ingestion/grace defect and pending execution-receipt requirement.

Fresh isolated main-runtime rerun of the four coordination test modules passes
**142 tests**, 25.04 seconds (`/tmp/opencode/dcc-commit-coordination-focus.txt`).
It uses absolute interpreter/test paths, disposable CWD, `PYTHONPATH=<checkout>`,
`TMPDIR`, pytest `--basetemp` and `-p no:cacheprovider`. No fresh full-suite result
is claimed; the earlier 485/three-skip run and separate red grace probe retain
their original scope. The ingestion/grace regression is not in this passing suite.

Staged scope, whitespace, file bounds and credential/account-path scans pass.
Scoped Ruff lint/format passes **23 Python files**. The broader lint invocation
reports **53 findings** in two legacy test files; checks against their HEAD
versions confirm identical findings, and neither is reformatted. Evidence:
`/tmp/opencode/dcc-commit-lint-baseline.txt`. Wiki review passes eight frontmatters,
152 grounding paths, 52 scoped links and complete-diff privacy/whitespace checks.
This is an interim snapshot, not dcc-02 acceptance or real-writer qualification.
No push was performed; the human will push both repositories.

### Maintainer milestone review — November 14

Fresh review after fast-forward pulls to Analytics `660b5a8` and PyUtil `fe7fcb5`.
Earlier feedback notes were preserved, index/log conflicts resolved and the verified
preservation stash dropped. Read the worker plan/verification and live repair,
authority, phase-archive, routing, protocol/ledger and tick/supervision sources.
Findings and dispositions: [[wiki/work/dbt-compaction-coordination/implementation-review]].

**Fresh macOS runs:** standalone Python 3.14.0 / DuckDB 2.0.0; main Python
3.12.12 / DuckDB 1.5.6. Wrappers resolve interpreter/test paths absolutely, run
from automatically cleaned temporary directories under the harness-approved root,
set `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH` and `TMPDIR`, and pass isolated pytest
`--basetemp` plus `-p no:cacheprovider`. Commands below show checkout-relative
interpreter/targets. No source/test files were edited.

Standalone full suite:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -rs -p no:cacheprovider tests
```

**305 passed, 2 failed, 2 skipped**, 61.28 seconds. Both failures are the
`test_new_publication_directory_links_are_fsynced_before_success` cases: the test's
fsync observer reads Linux `/proc/self/fd`, unavailable on macOS. The two skips
are opt-in S3 transport cases. Other authority, integrity, provenance, phase repair
and compaction cases pass.

Main focused suite:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -rs -p no:cacheprovider \
  tests/test_coordination_protocol.py tests/test_coordination_ledger.py \
  tests/test_coordination_tick.py tests/test_coordination_supervisor.py \
  tests/test_entity_freshness.py tests/test_effective_input_roots.py \
  tests/test_checkpoint_repair.py tests/test_process_entities.py \
  tests/test_dbt_source_validation.py tests/test_compacted_inputs.py
```

**196 passed, 3 failed, 35 skipped**, 205.15 seconds. All three failures are
unguarded Linux assumptions in `test_coordination_tick.py`: abrupt tick death with
a surviving child reads `/proc/<pid>/stat`; two supervisor integration tests expect
a report or PID file after the Linux-only supervisor correctly refuses launch.
The dedicated supervisor module correctly skips its 34 cases; the remaining skip
is opt-in isolated migration. The included real-DBT freshness/forward-lineage,
cross-runtime checkpoint repair and local-only routing/build cases pass. These
results do not repeat the worker's Linux supervision or remote qualification.

**Independent review probes:**

- R6: wrap the original `Ledger.ingest_many`, advancing only an injected clock
  after it returns, using real local DuckDB and the existing fake S3 helper.
  Pre-grace control passes (`OPEN`, one reader/grant). Crossing `00:09:59` →
  `00:10:00` produces `DRAINING`, one new reader/grant and zero waiting instead
  of zero new readers/grants and one waiting request. The script exits 1 at that
  behavioral assertion. This independently corroborates the worker's known defect.
- R7: in a separate standalone Python process, replace
  `entity_sql._validate_evidence` with a no-op in memory and call `pytest.main`
  for `tests/test_entity_integrity.py -k corrupt_snapshot_rejected_by_verify_and_update`.
  **80 passed, 14 deselected**, 8.93 seconds. The test selection still passes
  because it rewrites committed snapshots and accepts generic authority errors.
  This is mutation evidence of a test gap, not a valid integrity acceptance run.
- R7 controls: use the live seed/rewrite fixture helpers for duplicate-key and
  `os_pid`/evidence disagreement, then invoke `EntityStore.validate_sql` directly.
  Both are rejected with the intended SQL diagnostics. Under the same in-memory
  no-op mutation, both are accepted. The probes establish the repaired validator's
  behavior and identify an independent entrypoint for durable negative tests.

Each probe used disposable synthetic fixtures with automatic cleanup and restored
in-process patches. No actual endpoint, scheduled writer or source-code edit was
involved. R6–R8 are open follow-through in the plan; dcc-02–05 remain unchecked.
The earlier R1–R5 red/green history is retained with its original scope.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py; ../Wintap-PyUtil/tests/test_coordination_tick.py -->

Documentation checks pass for five changed wiki files: three frontmatters, 65
grounding paths and 15 wikilinks/section targets. Whitespace and added-content
home-path/IP scans pass; the complete diff was reviewed for privacy. PyUtil retains
only its pre-existing untracked environment artifacts. Review additions were
uncommitted at review completion; the human subsequently requested publication.

### Completion planning — November 14

Reviewed the current brief/design/handoff/plan, R6–R8 findings and live coordinator,
ledger, supervisor, Makefile, root resolver, CLI, storage resolution, authority and
phase-verification sources. Confirmed the missing success/history/cursor API,
service/client integration and real-writer completion dependencies. This was a
source/planning review, not a new runtime acceptance run.

Human-selected scope: Linux coordinator/writer, Linux/macOS readers; actual existing
S3 endpoint with fresh feature-owned fixtures, exact roots/access confirmed before
writes; initial 32 GB RAM / 64 GB disk qualification with aggregate usage monitoring,
then a reduced-limit recommendation. Reduced-limit acceptance requires its own
representative rerun. No low-budget pass, macOS support or endpoint qualification
is claimed. See the dependency slices and remaining inputs in
[[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]].
<!-- SOURCE: Human planning decisions, conversation 2026-11-14. -->

No source changes, runtime tests, remote writes, fixture deletion, deployment or
push were performed during planning. All R6–R8 and dcc-02–05 implementation gates
remain open.

Scoped documentation checks: `git diff --check` passes. A read-only main-runtime
Python/YAML check validates six changed wiki files, four feature-page frontmatters,
85 grounding paths and 344 wikilinks/section targets. Added-content home-path/IP
scan and complete-diff privacy review pass. The initial strict check identified
pre-existing missing frontmatter in `wiki/index.md` and `wiki/log.md`, confirmed
against HEAD and left unchanged; this is not a whole-wiki lint pass.

### Completion slice A — review repairs

All runs use `/tmp/opencode/dcc-run-tests.py` with the main interpreter for the
wrapper, absolute runtime/test paths, disposable working directory, isolated
`TMPDIR`/`--basetemp`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH` and
`-p no:cacheprovider`. Standalone and mutation runs use the standalone interpreter.
Reports are local evidence, not copied source or remote telemetry.

| Run / report under `/tmp/opencode/` | Selection | Result |
|---|---|---|
| `dcc-r6-formal-red.txt` | main tick: `-k 'ingestion_clock_is_refreshed or clock_failure_after_ingestion'` | 4 failed, 2 passed before post-ingestion clock repair |
| `dcc-r8-procfs-red.txt` | standalone phase tests: `-k new_publication_directory_links` | 2 failed with `/proc` denied before portable observer repair |
| `dcc-r7-independent-sql-mutation-red.txt` | standalone integrity: `-k sql_integrity_rejects`, in-memory `_validate_evidence` no-op | 80 failed, 94 deselected (expected mutation rejection) |
| `dcc-r6-r8-main-green-final.txt` | protocol, ledger, tick and supervisor modules | 150 passed, 24.45 s |
| `dcc-r7-r8-standalone-green.txt` | integrity and phase-evidence modules | 215 passed, 102.29 s |
| `dcc-r7-r8-full-standalone.txt` | complete standalone `tests` | 387 passed, 2 opt-in S3 skips, 153.13 s |
| `dcc-r6-r8-full-main.txt` | complete main `tests`, before slice B additions | 493 passed, 3 skips, 616.08 s |

R6 refreshes immediately after the original atomic ingestion, before admission.
Exact grace and post-ingestion rollback/unreadable clocks preserve prior reservations
and leave unreserved requests queued. The admission-focused fixture omits the
writer adapter: an eligible hour with zero readers may legitimately launch when
an adapter is supplied; the intermediate contrary expectation was corrected.

R7 adds 40 corruption classes at each of two authority-independent entrypoints:
direct `validate_sql` and the next publication candidate during active update.
SQL-specific diagnostics and unchanged committed authority/publication bytes are
required; the original 80 freshness negatives remain. Two initial candidate tests
accidentally made the corrupted STOP-derived fields valid by adding a STOP; using
an unchanged observation in the later hour fixes that fixture collision. The
80-case no-op mutation now fails every new negative without modifying source.

R8 uses portable descriptor device/inode observations while actively denying
`/proc`, and guards the three actual Linux-dependent tick cases. Two synthetic
`darwin`/`win32` controls require refusal before `Popen` and retained blocked intent.
Linux durability/tree coverage remains exercised. No actual macOS rerun or reader
backend has been qualified by this slice.

The full main A-slice run was launched before slice B's new module; its subsequent
completion notification reports 493 passes/three skips. It does not cover the
later execution implementation. Initial wrappers
using system Python failed before tests because of its unsupported `text=` option;
the main interpreter fixes that harness issue. Initial full-suite runs also failed
before tests because bare `tests` was not absolutized; corrected runs were launched.
Neither harness failure is a behavior regression. No endpoint access, deployment,
commit or push occurred. dcc-02–05 remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick; ../Wintap-PyUtil/tests/test_coordination_tick.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py -->

### Completion slice B — execution baseline

The new entirely local `tests/test_coordination_execution.py` was run before any
execution/writer implementation: **23 failed in 0.34 s**, all missing-module/API
failures. Report: `/tmp/opencode/dcc-execution-missing-api-red.txt`. This is an
implementation baseline, not active-path hardening evidence. The first implementation
passes 22/23 initial cases; the real-empty fixture needed an existing compacted
destination for the CLI's read-only migration check. That fixture is corrected,
not treated as a receipt defect. Further active-path probes record five failures
before budget-ceiling/archive-separation, lost-COMMIT-ack blocking and secret-bearing
exception repairs; three injected remote-resolution controls pass. Report:
`/tmp/opencode/dcc-execution-hardening-red.txt` (23 deselected). Post-repair and
broader launch/configuration/secret-exclusion results are recorded below; macOS is open.

| Report under `/tmp/opencode/` | Selection / result |
|---|---|
| `dcc-execution-initial.txt` | 22 passed, one failed: missing compacted root in real-empty fixture; corrected separately from behavioral defects |
| `dcc-execution-hardening-red.txt` | 5 active-path failures, 3 injected SDK passes, 23 deselected: memory/spill ceilings, archive/ledger overlap, lost COMMIT acknowledgment and secret-bearing exception |
| `dcc-execution-file-arg-red.txt` | 3 active-path failures: FIFO/hardlink receipt refusal before read and compiled argument budget before publication |
| `dcc-execution-expanded-green.txt` | 37 passed, 22.73 s after eight hardening repairs |
| `dcc-execution-coordination-green.txt` | 194 passed, 51.80 s: execution, protocol, ledger, tick and supervisor modules (44 receipt/launch cases) |

The final focus includes real local empty and one-row synthetic migration/source
deletion with original phase records retained. Both leave `BLOCKED` and retain the
cursor. Tests cover strict matching-checksum malformed receipts, run/root/command/
runtime identity, argument/capture/time/storage budgets, nonregular files and
pre/post-intent changes. Injected SDK/default/environment/profile resolution freezes
the selected endpoint/region and credentials before later environment changes;
synthetic secret values and their hashes are absent from receipts/intents/audits,
and credential repr is excluded. No actual endpoint request occurs.

Receipt preparation fixes this checkout's standalone `-I -B` CLI and public code/
native-engine identity, explicit active scope and inactive entity/S3 fields. Remote
extension-cache default is `<state>/extensions`; spill and retained phase archive
are separate from ledger/runtime/data roots. Individual 32 GB memory/64 GB spill
ceilings are not aggregate RSS/disk or representative sizing qualification.
Lost intent-COMMIT acknowledgment cannot launch and blocks in the same session.
Secret-bearing provider/launch exceptions are sanitized, not retained as diagnostics.

Scoped Ruff lint and format checks pass eight changed/new Python files; both
repositories' `git diff --check` pass. The full-main receipt-revision run completes:
`dcc-run-tests.py main /tmp/opencode/dcc-execution-full-main.txt tests` reports
**537 passed, 3 skipped in 683.54 s**. Tested runtime sources remained unchanged
until its completion notification. Completion-side high-water/history,
service/client/audited recovery, actual macOS/S3 and resource gates remain open.
No production scheduler, endpoint operation, fixture cleanup, commit or push.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/execution.py; ../Wintap-PyUtil/wintappy/coordination/writer.py; ../Wintap-PyUtil/tests/test_coordination_execution.py -->

### Completion slice C — separate verification, ledger integration pending

All commands below use the disposable-CWD `dcc-run-tests.py` harness described
above, with explicit main/standalone environments, no checkout cache writes and
qualification-owned synthetic local fixtures. Reports remain under `/tmp/opencode/`;
no actual endpoint access or production scheduling occurs.

| Report | Selection / result |
|---|---|
| `dcc-completion-verifier-missing-api-red.txt` | 33 missing standalone API failures before implementation |
| `dcc-completion-prototype-initial.txt` | 9 failed, 24 passed from an injected scratch prototype; not active-path implementation evidence |
| `dcc-completion-verifier-initial.txt` | 33 passed, 14.64 s after promotion into the real module |
| `dcc-completion-archive-hardening-red.txt` | 2 active-path failures: FIFO and hardlinked archive records read before refusal |
| `dcc-verification-missing-api-red.txt` | 9 missing main adapter API failures |
| `dcc-completion-types-hardening-red.txt` | 3 active-path failures: terminal boolean, validation integer and boolean row counts |
| `dcc-verification-live-intent-red.txt` | 1 active-path failure: failed verification left committed intent `WRITING` |
| `dcc-authority-baseline-recheck-red.txt` | 1 active-path failure: stale initialization-candidate snapshot accepted |
| `dcc-verifier-request-red.txt` | 1 active-path argument-parser failure, 3 refusal controls passed |
| `dcc-completion-final-focus.txt` | **259 passed, 118.44 s**: completion (44 cases), phase archive and SQL integrity modules |
| `dcc-verification-final-focus.txt` | **204 passed, 87.56 s**: verification (10 cases), execution, ledger, protocol, tick and supervisor modules |

The eight active-path failures precede repairs. Positive valid-before-corruption
controls distinguish evidence rejection from a broken success fixture. Archive
reads now require bounded single-link regular files before opening. Exact JSON
types reject boolean/integer substitutions. Request parsing refuses checksum,
shape, argument and byte-budget violations without echoing synthetic sensitive
values. Initialization evidence rechecks current snapshots; failed verification
blocks a matching live intent without moving the cursor.

Standalone `completion.verify_completion` independently reopens original archive
and surviving data: exact run/hour/root/event scope, chain/order, original migration
and deletion evidence, hashes/counts/schemas, source absence and complete bounded
empty-hour discovery. Entity-mode local controls verify current SQL state/authority,
original bootstraps, retained exact ordinal/ID anchors and original historical
checkpoint candidates. Forward evolution is permitted without comparing historical
hashes to today's aggregate; rollback/forks/pending state/corruption refuse.
`verify_authority` returns rechecked candidate evidence only.

Main `verification.verify_prepared` authenticates committed receipt/intent and
writer shutdown/captures, publishes an immutable request and separately supervises
the standalone read-only verifier, authenticating its shutdown/captures too. It
rechecks receipt/runtime/request/intent and original observations after verification.
**Success confers no completion permission.** At this foundation revision, entity
mode explicitly refuses until
independently initialized ledger high-water authority is integrated; caller-supplied
anchors do not bypass this main-runtime gate. Ledger remains v1 with one unresolved
run, no retained completed history and no completion/cursor/reopening API.

Fresh scoped Ruff 0.17.5 lint and formatting pass all 13 changed/new Python files.
The full standalone verifier revision completes with **431 passed, 2 skipped in
172.52 s** (`dcc-completion-full-standalone.txt`); full main completes with
**547 passed, 3 skipped in 695.09 s** (`dcc-completion-full-main.txt`). Runtime sources
remained frozen until both notifications arrived. These results precede and do not
cover the subsequent ledger-v2 authority work below. Atomic history/completion integration,
actual macOS reader shutdown, service/client/recovery, actual S3 and representative
32 GB RAM / 64 GB disk qualification remain open; dcc-02–05 stay unchecked.

Post-cleanup artifact/privacy audit passes **10 changed wiki files, 8 frontmatters,
179 grounded paths, 191 inline sources, 377 links and 7 diagram pages**. Existing
index/log frontmatter omissions remain baseline exceptions, not a whole-wiki lint
pass. Both repositories' whitespace checks pass. Complete new source/test files
and tracked runtime diffs were reviewed; unrelated data/environment/settings stay
excluded. No new commit or push is made.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §read_local_record/load_archive; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_completion_verifier.py; ../Wintap-PyUtil/wintappy/coordination/verification.py; ../Wintap-PyUtil/tests/test_coordination_verification.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py -->

### Ledger integration baseline — high-water prerequisites fail before repair

Before changing runtime sources, the disposable-CWD main harness runs
`dcc-run-tests.py main /tmp/opencode/dcc-high-water-baseline-red.txt
/tmp/opencode/dcc-high-water-baseline-tests.py`: **2 failed in 1.19 s**. These scratch
tests call the real ledger with synthetic entity-enabled local bindings. A queued
reader receives a reservation without an independently initialized authority
baseline, and direct `begin_writer` also succeeds without that prerequisite. No
writer subprocess, production dataset or endpoint is involved. The negatives were
subsequently promoted into `tests/test_coordination_authority.py`; their recorded
pre-repair failures and latest passes are attributed below.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §initialize/admit/begin_writer -->

### Completion slice C — ledger-v2 authority integration

The earlier verifier-foundation full passes are **547 main / 431 standalone**, not
authority-revision regression results. All following runs use the same disposable-CWD
harness and synthetic local fixtures; no endpoint request or production operation.

| Report | Result / attribution |
|---|---|
| `dcc-authority-ledger-api-red.txt` | **4 failed, 1.73 s**: two active entity admission/intent prerequisite failures plus two missing upgrade-interface failures |
| `dcc-authority-adapter-missing-api-red.txt` | **6 failed, 4 passed, 2.15 s** before the supervised initialization API existed |
| `dcc-authority-observation-hardening-red.txt` | **3 active failures, 13.63 s**: rehashed command digest, captured result and observations path accepted before authentication repairs |
| `dcc-entity-adapter-integration-red.txt` | **1 expected active integration-gate failure**: real local entity writer passes, but the main adapter still unconditionally refused entity verification |
| `dcc-authority-upgrade-invalid-red.txt` | **1 active diagnostic failure, 3 passed, 1.82 s**: corrupt source exposed a raw DuckDB exception; repair returns sanitized `CoordinationError` without replacement |
| `dcc-authority-upgrade-crash-green-2.txt` | **12 passed, 18 deselected, 20.38 s**: upgrade/abrupt-death controls |
| `dcc-authority-request-green-2.txt` | **8 passed, 44 deselected, 2.15 s**: strict bound authority requests, sensitive-input refusal and changed-request detection |
| `dcc-authority-final-main-green.txt` | **236 passed, 204.99 s**: authority, ledger, execution, verification, tick, protocol and supervisor modules |
| `dcc-authority-final-standalone-green-2.txt` | **299 passed, 139.30 s**: completion, entity freshness/integrity and phase archive modules |
| `dcc-authority-fork-history-final-green.txt` | **2 passed, 30 deselected, 22.58 s** after test-only inline-command cleanup |

Latest main and standalone focus commands:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-authority-final-main-green.txt \
  tests/test_coordination_authority.py tests/test_coordination_ledger.py \
  tests/test_coordination_execution.py tests/test_coordination_verification.py \
  tests/test_coordination_tick.py tests/test_coordination_protocol.py \
  tests/test_coordination_supervisor.py
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py standalone \
  /tmp/opencode/dcc-authority-final-standalone-green-2.txt \
  tests/test_completion_verifier.py tests/test_entity_freshness.py \
  tests/test_entity_integrity.py tests/test_phase_evidence.py
```

Ledger schema v2 adds canonical predecessor-linked `authority_checks`; explicit
confirmed `Ledger.upgrade` preserves ledger/dataset identity, cursor, reservations,
outbox, tombstones, existing audits and writer identities. The schema transaction
is atomic; unresolved-writer blocking may commit before it. Old intents stay blocked
and gain no manufactured execution/completion evidence. Missing/corrupt/mismatched
sources refuse replacement; ordinary open never upgrades or silently initializes.

`verify_authority_prepared` separately supervises a read-only standalone
`--authority-only` version-2 request bound to execution, ledger/dataset identities
and prior anchor. Initialization requires explicit confirmation/reason, no prior
baseline and zero readers in `OPEN`/`DRAINING`. Command/manifest, path, captured bytes,
shutdown, receipt/runtime, request and current evidence are authenticated/rechecked
before proof/audit retention in one transaction. The standalone never opens the
ledger; its candidate alone cannot initialize or authorize admission.

Entity admission and writer intent require the initialized exact generation plus
a fresh check in the same locked session. Reopen resets freshness, failed checks
clear it and successful intent consumes it. Existing reservations are retained.
Forward evolution passes; whole-journal/snapshot rollback with a retained ledger
and a same-ordinal fork valid in isolation refuse without rebasing. The main entity
`verify_prepared` now verifies real local entity migration/deletion and its original
historical checkpoint, leaving high-water/cursor/permissions unchanged. That candidate
still needs the atomic completion transaction.

Authority history is bounded at **64 KiB/check / 10,000 checks**, entirely validated
in **256-row batches**; corruption or exhaustion refuses, never truncates. The
257-row control synthetically extends authenticated repeat-check metadata and
corrupts the final row; it proves validation beyond the first batch, not 257 actual
verifier runs, retained-state sizing or manufactured authority/data/recovery evidence.
Abrupt death and lost acknowledgments around authority/upgrade COMMIT preserve
old/new atomic schema or retained anchor without fresh admission/relaunch permission.

Harness/fixture failures are retained separately: `dcc-authority-final-focus.txt`
records 225 passes/one fixture failure from an extra `make_release` argument;
initial crash fixtures treated `load_execution`'s receipt dictionary as a
`PreparedExecution`, request fixtures omitted required arguments/event selection,
and the initial fork fixture re-created an existing directory. Corrections change
fixtures, not behavior. `dcc-authority-final-standalone-green.txt` selected nonexistent
standalone paths (no tests, exit 4); the corrected 299-pass selection is above.

Latest scoped Ruff **0.17.5** lint and format checks pass six authority/verification
source/test files. Full authority standalone completes with **439 passed, 2 skipped
in 173.60 s** (`dcc-authority-full-standalone.txt`). Full main completes with
**579 passed, 3 skipped in 791.61 s** (`dcc-authority-full-main.txt`):

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-authority-full-main.txt tests
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py standalone \
  /tmp/opencode/dcc-authority-full-standalone.txt tests
```

Runtime sources/tests remained frozen until both automatic completion notifications.
The freeze is now lifted for the next completion/history slice; the full passes
above qualify only the earlier authority revision.
Ledger v2 still retains only one unresolved writer record: completed-run history,
atomic completion-evidence/run/high-water/exact-hour-cursor/backlog-mode COMMIT,
fresh clock/admission integration and audited recovery remain absent. Actual macOS
reader shutdown, exact isolated S3 access/roots and representative 32 GB RAM / 64 GB
disk qualification are open. Whole-ledger-plus-authority rollback freshness and
physical power-loss behavior are not established by these tests. dcc-02–05 remain
unchecked; no production operation, new commit or push occurred.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_validate_authority_checks/_require_entity_authority; ../Wintap-PyUtil/wintappy/coordination/authority.py; ../Wintap-PyUtil/wintappy/coordination/verification.py §verify_authority_prepared/verify_prepared; ../Wintap-PyUtil/tests/test_coordination_authority.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_completion_verifier.py -->

**Post-synchronization source/artifact review:** fresh tracked runtime diffs and
feature-owned new source/test files are reviewed without modifying the frozen
runtime. The complete wiki diff is inspected for unauthorized host/account/IP values;
none are added. `../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-check-wiki.py`
passes **10 changed wiki files, 8 frontmatters, 195 grounded paths, 214 inline sources,
379 links and 7 diagram pages**. Index/log frontmatter omissions remain preserved
baseline exceptions, not a whole-wiki lint pass. Both repositories' `git diff --check`
pass. Pinned Ruff **0.17.5** `check` and `format --check`, run through
`uv tool run --cache-dir /tmp/opencode/dcc-ruff-cache --from ruff==0.17.5`, pass all
**15 changed/new feature Python files** (six main coordination sources, four main
test modules, two standalone sources and three standalone test modules).

The continuation plan now explicitly preserves the current launch API's conservative
blocking behavior. Normal success must obtain fresh independent verification inside
a new uninterrupted same-lock live-intent path; previously blocked/restart-blocked
runs remain behind explicit audited recovery. No parsed or caller-supplied report
may clear uncertainty. This is a documented implementation boundary, not a new
success API or runtime test. Full main was still pending during that review; no
polling, source/test changes, endpoint operation, deployment, commit or push occurred.

### Completion slice C — initial ledger-v3 history and atomic completion

The authority full regressions above completed before these edits. Ten formal
completion controls first produced **10 missing-API failures in 11.33 s** in
`dcc-completion-ledger-api-red.txt`; all are missing-entrypoint ImportErrors, not
active behavioral hardening evidence. The first implementation adds schema v3,
retained predecessor-linked completion proofs and an uninterrupted same-lock
writer→fresh independent verifier→completion transaction path. Existing
`execute_prepared` remains conservative; blocked/restarted intents cannot use the
new normal-success entrypoint.

The initial five-file syntax checks pass after import/unused-variable cleanup and
formatting. `dcc-completion-initial.txt` records **10 passed in 66.90 s**:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-initial.txt tests/test_coordination_completion.py
```

This initial focus covers real local empty completion, two sequential hours,
retained prior evidence, verification crossing grace, old/restarted blocking,
before/after-COMMIT lost acknowledgments and archive/shutdown/clock uncertainty.
It is not final completion acceptance. Existing ledger/authority/execution/verifier
regressions and additional real entity, abrupt-death, rehashed/missing-history and
budget controls are running against the prototype; no outcomes are inferred before
notifications. Schema v1/v2 compatibility, complete history validation and atomic
entity high-water advancement still need their resulting evidence. Full regressions,
service/client, audited recovery, actual macOS/S3 and resource gates remain open.
No endpoint operation, production scheduling, cleanup, commit or push.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_complete_writer/_validate_completion_history/upgrade; ../Wintap-PyUtil/wintappy/coordination/writer.py §execute_and_complete_prepared; ../Wintap-PyUtil/tests/test_coordination_completion.py -->

The first existing-regression and additional-hardening invocations hit the harness's
**120-second shell timeout**, with no completed runner report or retained test
outcome. These are incomplete harness runs, not passes or behavioral failures.
Both selections were relaunched with no outer shell timeout (the disposable runner
retains its 1,200-second subprocess ceiling). Runtime sources remained unchanged
until both resulting notifications.

Recorded implementation/hardening results before repairs:

| Report under `/tmp/opencode/` | Result and attribution |
|---|---|
| `dcc-completion-regressions-initial.txt` | **126 passed, 1 failed in 178.98 s**; the only failure is a historical upgrade test expecting target v2 instead of v3, not a failed atomic upgrade. Its identity/schema all-or-none assertions are preserved with the current explicit target and both authority/completion-table checks. |
| `dcc-completion-hardening-red.txt` | **13 passed, 3 failed, 10 deselected in 135.90 s**; active failures accept inactive checkpoint values, erase completion evidence/run/cursor while leaving its audit, and accept removed fresh authority captures. Real local entity advancement, budget refusals and abrupt raw completion-death controls pass. |
| `dcc-completion-hardening-red-2.txt` | **4 failed, 26 deselected in 28.64 s**; active failures accept removed completion audits, joint origin/cursor rebasing, same-session prior-history corruption and original archive removal after verifier return. |

All **seven active failures** are retained before source repairs. The repaired
prototype makes inactive checkpoint fields explicitly null; ties origin, proofs,
completed runs, audits and cursor together; validates prior history again before
completion; and rechecks fresh authority captures/requests plus the bounded original
JSON archive chain before COMMIT. Main archive rechecks inspect byte identities
only, never compactor SQL/data in the main runtime. All actual data verification
remains in the separately supervised standalone DuckDB 2.0.0 runtime.

The origin audit commits with explicit initialization/compatible v1/v2 upgrade,
retaining the original ledger ID, old permissions and proof bytes. It is local
integrity evidence, not protection against coherent whole-ledger-plus-store rollback.
Completion proofs remain capped at **128 KiB/proof / 10,000 completed runs**, with
256-row history pages; authority ceilings remain **64 KiB/check / 10,000 checks**.
No history is pruned. Added genuine entity before/after-completion-COMMIT and
external-success-before-COMMIT death controls, v2 compatibility with genuine authority
proof bytes, audit-independent retained-proof semantic negatives, synthetic-secret
exclusion and three real hours through instrumented two-row pages. The latter tests
multiple pages without manufacturing completions; it is not a 257-real-run or
representative retained-state sizing qualification.

Those repaired runs subsequently complete:

| Report under `/tmp/opencode/` | Result and revision scope |
|---|---|
| `dcc-completion-hardening-green.txt` | **46 passed, 21 deselected in 287.77 s**: completion/history/entity/crash controls and compatible-upgrade focus, before the final budget/clock repair. |
| `dcc-completion-controls-initial.txt` | **24 passed in 44.96 s**: independent retained-proof semantics, genuine-proof v2 compatibility, three-real-hour paging and synthetic-secret controls, before the final budget/clock repair. |
| `dcc-completion-budget-clock-red.txt` | **3 active failures, 24 deselected in 20.91 s**: consistently rebound stdout/stderr capture metadata can exceed the effective receipt ceiling; a later invocation can predate the prior completion and reopen backlog. |
| `dcc-completion-budget-clock-green.txt` | **3 passed, 24 deselected in 16.58 s** after effective capture/report ceiling checks and retained prior-completion clock-floor enforcement. |

These bring completion hardening to **ten recorded active failures before repairs**,
separate from the ten initial missing-API failures and the stale target assertion.
The final clock repair compares a new normal-success invocation to the prior
retained completion before intent/launch, and validates monotonic completed-history
start times. This is not a persistent global clock attestation or coherent rollback
freshness guarantee. Receipt-bound stream/report limits also apply when validating
retained proofs, independently of audit/hash rejection.

Repaired-focus and final-target commands:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-hardening-green.txt \
  tests/test_coordination_completion.py tests/test_coordination_authority.py \
  -k 'completion or history_origin or same_session_history or original_archive_removed or upgrade'
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-controls-initial.txt tests/test_coordination_completion_controls.py
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-budget-clock-red.txt \
  tests/test_coordination_completion_controls.py -k 'retained_writer_capture or clock_before_prior'
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-budget-clock-green.txt \
  tests/test_coordination_completion_controls.py -k 'retained_writer_capture or clock_before_prior'
```

Final combined main coordination focus and full standalone regression were launched
against the frozen budget/clock revision. Full standalone subsequently passes
**439 tests, two skips in 170.76 s**. Combined main focus then completes with
**298 passed in 517.39 s**; its completed report is inspected before full main launch:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-final-main-focus.txt \
  tests/test_coordination_authority.py tests/test_coordination_completion.py \
  tests/test_coordination_completion_controls.py tests/test_coordination_ledger.py \
  tests/test_coordination_execution.py tests/test_coordination_verification.py \
  tests/test_coordination_tick.py tests/test_coordination_protocol.py tests/test_coordination_supervisor.py
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py standalone \
  /tmp/opencode/dcc-completion-full-standalone.txt tests
```

Full main was launched against the unchanged revision and subsequently completes
with **641 passed, 3 skipped in 1055.19 s**. Its completed report and automatic
notification are inspected; source/runtime-lock identities still match the prepared
manifest. Together with 439 standalone passes/two skips, this closes the local v3
full-regression gate, not dcc-02–05:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-v3-full-main.txt tests
```

No outer shell timeout is used; the disposable-CWD runner retains its 1,200-second
subprocess ceiling. Runtime sources/tests remained frozen until both full automatic
notifications, without polling; the freeze is now lifted for the next dependency
slice. Result-only synchronization passes the complete documentation/privacy
inspection; the scoped audit again passes 11 wiki files,
9 frontmatters, 211 grounding paths, 243 inline sources, 387 links and 7 diagram pages.
Both whitespace checks pass. Pinned Ruff **0.17.5** lint/format results cover all
18 unchanged feature Python files after the final budget/clock repairs. Complete
tracked/new feature-source review and full wiki-diff privacy inspection are completed;
stale source-map/design statements about the absent local success API are corrected.
Unrelated data/environment/settings remain excluded and untouched.
Before the Mac runbook addition, the refreshed read-only scoped audit command
`../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-check-wiki.py` passed
**10 changed wiki files, 8 frontmatters, 204 grounding paths, 238 inline sources,
381 wikilinks and 7 diagram pages**. Index/log frontmatter omissions remain
preserved baseline exceptions, not a whole-wiki lint pass. The complete 1,787-line
pre-synchronization wiki diff and subsequent documentation edits are inspected;
no actual host/account/IP identifiers are added. Ruff `check` and `format --check`
run through the pinned command above over seven main coordination sources, six
main coordination test files, two standalone sources and three standalone test
files. Both commands pass all 18 files; neither reformats the frozen revision.
dcc-02–05, service/client/audited recovery and actual
macOS/S3/representative-resource gates stay open. No endpoint operation, production
scheduling, cleanup, commit or push.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py §validate_completion_proof/_recheck_archive/_complete_live_prepared; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate_completion_history/_complete_writer/upgrade; ../Wintap-PyUtil/tests/test_coordination_completion.py; ../Wintap-PyUtil/tests/test_coordination_completion_controls.py; ../Wintap-PyUtil/tests/test_coordination_authority.py -->

### Human-run macOS baseline prepared — execution remains pending

The human selected an actual-Mac human-run harness. Instructions and the later
reader-backend acceptance boundary are in
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. Prepared scratch
artifacts are `dcc-macos-baseline.py`, `dcc-macos-source-manifest.json` and
`dcc-macos-baseline-bundle.tar.gz` under `/tmp/opencode/`. The bundle contains only
the 18 feature Python files, coordination README, harness and source manifest;
no data, credential files, virtual environments or unrelated settings are copied.
Tar owner/group metadata is neutralized. The manifest checks the exact baseline
commit and public source/runtime lock files, not secrets or environment hashes.

Harness syntax, all bundle member identities/neutral metadata and an actual Linux
refusal-before-output/pytest control pass. Pinned Ruff **0.17.5** lint/format passes
the separate scratch harness after initial style cleanup. This is harness preparation
and a non-Mac refusal control, **not actual macOS execution, qualified reader shutdown
or representative resource evidence**. Current Linux-only test skips remain explicit.
No runtime source/test file changes occurred during harness preparation or the Linux
full-main freeze. Full main subsequently passes 641 tests/three skips on the unchanged
revision; the freeze is lifted. Human transfer/execution is next;
the future macOS backend remains required before broad reader integration.
The final scoped audit includes the new untracked runbook and passes **11 wiki
files, 9 frontmatters, 211 grounding paths, 243 inline sources, 387 wikilinks and
7 diagram pages**. Complete new runbook/subsequent edits and both whitespace
checks pass; preserved index/log exceptions are not whole-wiki acceptance.

### Committed Mac handoff — dcc-mac-baseline-01 pending

The human authorized feature-only commits and will run the Mac tests on another
system. PyUtil commit `8ee714c0c58e9781a29b0cdc488e3aaf6ebea181` contains 19 prior
feature files plus the durable harness, source manifest and separate harness test
script (22 files total). Unrelated data/environment/settings/venvs are excluded;
no push occurred. The runbook now names this exact commit instead of the obsolete
`fe7fcb5` plus uncommitted-overlay workflow.

The manifest retains all 22 prior public identities: 18 feature Python files and
four runtime/lock files. Its version-two envelope names the reviewed parent and
accepts the explicit full qualification commit; SHA-256:
`c37247ac1962cb6a259e5387d1c9177a37f82a5ff78f913382b293770d2bf3b7`.
No runtime source/test or lockfile bytes changed while making the harness durable.
The 641-main/439-standalone full results above remain runtime evidence, not new
harness results or actual-Mac evidence.

From PyUtil:

```sh
TMPDIR=/tmp/opencode .venv/bin/python -B scripts/test_dcc_macos_baseline.py
```

Result: **15 local harness controls pass**. They cover exact commit versus obsolete
parent, clean tracked state, ancestry, source missing/change/symlink/path rejection,
obsolete manifest, non-Mac refusal, retained failure/skip counts, isolated synthetic
credential exclusion/private sanitized summary, timeout stop and missing interpreter
evidence. Simulated platform/subprocess unit controls are explicitly not Mac runs.
Durable script syntax and an actual Linux CLI refusal before testing/output pass.
Pinned Ruff **0.17.5** `check` and `format --check` pass all 20 Python files (the
unchanged 18 feature files plus two harness scripts). Staged allowlist/exact-byte
inspection and `git diff --cached --check` pass; all 22 original manifest hashes
still match. The identity-only `validate_checkout` check also passes against actual
committed HEAD `8ee714c` after commit; no platform tests run in that check.

Final scoped wiki artifact/privacy audit passes **11 changed files, 9 frontmatters,
217 grounding paths, 250 inline sources, 391 wikilinks and 7 diagram pages**;
index/log frontmatter omissions remain baseline exceptions. Whitespace checks
pass. Complete new runbook and feature diff inspection preserves the privacy rule.

Next task and exact Mac commands:
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. Actual Mac baseline,
reader backend/shutdown, service/client/audited recovery and S3/representative
resources remain unqualified; dcc-02–05 stay unchecked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_baseline.py; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py -->

### Mac packaging correction — original blocked result retained

The Mac worker reports that **dcc-mac-baseline-01 at PyUtil
`8ee714c0c58e9781a29b0cdc488e3aaf6ebea181` was blocked before either test stage ran**:
the clean checkout did not contain main `uv.lock`. Preserve the original private
blocked record; no main/standalone test counts or Mac pass are inferred.
<!-- SOURCE: Mac worker blocked-result report and human-authorized correction, conversation 2026-11-14. -->

Independent `git ls-tree -r --name-only 8ee714c0c58e9781a29b0cdc488e3aaf6ebea181`
inspection confirms 21 of 22 manifest files, with only main `uv.lock` missing.
The prior post-commit `validate_checkout` pass above checked local hashes, not
committed coverage: an ignored matching lockfile concealed the omission. That
historical check remains recorded with this explicit limitation; it was not
fresh-checkout proof. The standalone lock was already committed.

The human authorized a corrective follow-up, committed as PyUtil
`fab647f900196b0bc473fe7977b7dadcf7f4ce52`. Exactly five files changed:
`.gitignore`, main `uv.lock`, the two harness scripts and coordination README.
The lock is the original **593,615 bytes**, SHA-256
`61912ee3abb9e095b46e03fba4a021272d77bed9f1235a8901e92a92a5d9d367`;
it was not regenerated. Complete structured review of local and staged bytes
covers 191 packages and 1,940 public HTTPS registry/artifact URLs, with only
checkout-relative local project paths. The root-only ignore exception leaves
unrelated local lockfiles ignored. No runtime code, feature test or manifest hash
changed; all 22 original identities and the manifest SHA-256 above are retained.

The validator additionally uses `git cat-file blob <full-commit>:<manifest-path>`
to require each committed file's bytes to match its manifest hash. Local matching
files no longer conceal missing or different committed content. Three controls
were recorded before the guard: missing committed file, different committed bytes,
and a real synthetic clean Git repository with an ignored matching lockfile.
From PyUtil, before/after implementation respectively:

```sh
TMPDIR=/tmp/opencode .venv/bin/python -B scripts/test_dcc_macos_baseline.py > /tmp/opencode/dcc-lockfile-commit-coverage-red.txt 2>&1
TMPDIR=/tmp/opencode .venv/bin/python -B scripts/test_dcc_macos_baseline.py > /tmp/opencode/dcc-lockfile-commit-coverage-green.txt 2>&1
```

Inspected red result: **18 tests, exactly the three new failures, zero errors**;
the other 15 controls pass. Final green result: **18 pass in 0.213 s**. Initial
format-only cleanup is separate from the three behavioral red/green controls.
Pinned Ruff **0.17.5** `check --no-cache` and `format --check --no-cache` both pass
all 20 Python files: the unchanged 18 manifest Python files and two harness scripts,
using `uv tool run --cache-dir /tmp/opencode/dcc-ruff-cache --from ruff==0.17.5 ruff`.
Both harness scripts compile; an actual Linux CLI invocation exits 2 before output
or platform test access. Staged five-file allowlist, exact index/local identities,
structured lock review and `git diff --cached --check` pass before commit.

After committing, a new disposable clone was populated only from Git using
`git clone --quiet --no-local --no-hardlinks --no-checkout <local-repo> <new-checkout>`
and `git checkout --quiet --detach fab647f900196b0bc473fe7977b7dadcf7f4ce52`.
No ignored files, credentials, datasets or virtual environments were copied from
the working tree. In that clean clone, all **22 local file and committed blob
hashes** plus the unchanged manifest hash pass, and the updated identity-only
`validate_checkout` returns the full corrective commit. All **18 harness controls
pass again in 0.196 s**, using the existing external main interpreter without
provisioning environments in the clone. Git status remains empty. Inspected report:
`/tmp/opencode/dcc-lockfile-fresh-git-checkout.txt`. Neither actual-Mac test stage ran.

The complete six-file wiki diff is inspected for persistent-content privacy.
`git diff --check` and the scoped read-only artifact/privacy audit pass:
**6 files, 4 frontmatters, 115 grounding paths, 129 inline sources, 352 wikilinks
and 2 diagram pages**. Index/log frontmatter omissions remain baseline exceptions,
not whole-wiki lint acceptance.

Corrected full-revision commands and continuation prompt:
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. The Mac worker must
use a fresh checkout and a **new private report directory**, preserving the original
blocked result. Existing 641-main/439-standalone Linux results retain their original
unchanged-runtime scope; they are not corrective Mac qualification. Mac baseline/
reader shutdown, service/client/audited recovery, actual-S3/representative-resource
gates and dcc-02–05 remain open. No push, remote access, production mutation,
scheduler installation or unrelated-artifact cleanup occurred.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/.gitignore; ../Wintap-PyUtil/uv.lock; ../Wintap-PyUtil/scripts/dcc_macos_baseline.py §validate_checkout; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py -->

### Maintainer completion review — Mac provisioning blocked

Human requested the latest pull, source review and actual Mac tests. Utility planning
was committed and rebased as Analytics `94a6688` over pulled `deae3a3`; PyUtil's
fast-forward pull was already current at
`8ee714c0c58e9781a29b0cdc488e3aaf6ebea181`. No assistant push or source repair.

Created a clean detached disposable worktree at that exact PyUtil revision. Actual
platform: **macOS 26.7.1, arm64**; uv **0.11.26**. Applied the committed runbook:

```sh
uv sync --locked --dev --python 3.12
uv sync --locked --dev --python 3.12 --project extras/raw-sensor-compact
git ls-tree -r --name-only 8ee714c0c58e9781a29b0cdc488e3aaf6ebea181 uv.lock extras/raw-sensor-compact/uv.lock
git check-ignore -v uv.lock
```

- Main provisioning: **exit 2**, `Unable to find lockfile at uv.lock, but --locked
  was provided`. Python 3.12.12 was selected and an empty main environment created;
  dependencies were not installed. It is not a usable test runtime.
- The independent standalone provisioning command succeeded (**exit 0**), reporting
  Python **3.12.12**, DuckDB **2.0.0**, pytest **9.2.0**. These are provisioner-reported
  versions, not completed import/version gates or test results.
- Git tree check finds only `extras/raw-sensor-compact/uv.lock`; root `uv.lock` is
  excluded by `.gitignore`. The original checkout's ignored lock exists but does not
  match the reviewed manifest, so it was not copied or used.
- Direct standard-library `validate_checkout` check of the disposable checkout fails
  with `Required feature source is missing or aliased`. Exact HEAD, reviewed ancestry
  and clean tracked state pass; **21/22** named manifest files are present and match.
  The manifest SHA-256 is unchanged:
  `c37247ac1962cb6a259e5387d1c9177a37f82a5ff78f913382b293770d2bf3b7`.

**Original dcc-mac-baseline-01 attempt: BLOCKED before tests.** No main/standalone pytest stage, runtime
import/version check or committed harness execution followed the provisioning
failure. No harness `summary.json` exists; private `provisioning-review.json` records
the original command outcomes and separate source checks without fabricating test
counts. No lockfiles/manifests were changed and no substitute runtime was used.

The corrected run is recorded separately below; this original failure remains intact.

The source review covers R6–R8 controls, effective execution receipts, separate
verification, retained authority and v3 history/atomic completion. Findings and
worker repair request: [[wiki/work/dbt-compaction-coordination/implementation-review#Completion phase review — 2026-11-14]].
Worker-reported Linux **641/439 full-suite passes** and **298 focus passes** are not
fresh Mac evidence. dcc-02–05, service/client/advisory exports/audited recovery,
supported Mac reader shutdown, actual-S3 and representative-resource gates remain
open. The utility remains planning only; its previous 27-test result is unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/.gitignore; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/dcc_macos_baseline.py §validate_checkout; wiki/work/dbt-compaction-coordination/macos-qualification.md §Stage 1 -->

### Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed

Human selected the newly committed worker repair rather than a substitute-runtime
diagnostic run. Pulled PyUtil `8ee714c` →
`fab647f900196b0bc473fe7977b7dadcf7f4ce52` and Analytics `deae3a3` → `6459c74`;
rebased authorized utility planning as `1051a8c`. Preserved worker documentation,
planning and the original maintainer provisioning evidence through rebase/stash
resolution. No new review commit or assistant push.

A **new clean detached disposable checkout** uses only the repaired committed
sources and newly provisioned native environments. Actual platform: **macOS 26.7.1,
arm64**, uv **0.11.26**. The root lock has the exact previously reviewed SHA-256
`61912ee3abb9e095b46e03fba4a021272d77bed9f1235a8901e92a92a5d9d367`;
the public manifest SHA-256 remains
`c37247ac1962cb6a259e5387d1c9177a37f82a5ff78f913382b293770d2bf3b7`.
All **22 manifest files** pass local and committed-Git-blob identity checks before
and after testing. No source/test/lock/manifest bytes were altered for the run.

Commands from the repaired checkout:

```sh
uv sync --locked --dev --python 3.12
uv sync --locked --dev --python 3.12 --project extras/raw-sensor-compact
.venv/bin/python -B -c 'import sys, duckdb, pytest; print("main", sys.version.split()[0], duckdb.__version__, "pytest", pytest.__version__); assert duckdb.__version__ == "1.5.6"'
extras/raw-sensor-compact/.venv/bin/python -B -c 'import sys, duckdb, pytest; print("standalone", sys.version.split()[0], duckdb.__version__, "pytest", pytest.__version__); assert duckdb.__version__ == "2.0.0"'
.venv/bin/python -B scripts/dcc_macos_baseline.py \
  --root . --manifest scripts/dcc_macos_source_manifest.json \
  --commit fab647f900196b0bc473fe7977b7dadcf7f4ce52 \
  --output '<new-private-output-directory>'
```

Both locked provisioning commands and import/version gates exit **0**. Independent
harness controls also exit **0**: **18 tests in 0.279 seconds**, using
`<checkout>/.venv/bin/python -B <checkout>/scripts/test_dcc_macos_baseline.py`
from isolated CWD/HOME/temp without inherited AWS credentials. The committed
baseline similarly isolates its environment and runs its nine main / three
standalone modules unchanged, **not the full suites**.

| Stage | Import-checked Python / DuckDB / pytest | Passed | Skipped | Exit / timeout | Harness elapsed | Pytest elapsed |
|---|---|---:|---:|---|---:|---:|
| Main | 3.12.12 / 1.5.6 / 9.1.1 | 169 | 129 | 0 / false | 29.53 s | 29.05 s |
| Standalone | 3.12.12 / 2.0.0 / 9.2.0 | 267 | 0 | 0 / false | 47.51 s | 47.12 s |

Both stages report **zero failures, errors and deselections**. Private `summary.json`
reports `baseline_passed: true` and `reader_backend_qualified: false`. Raw
`main.txt`/`standalone.txt`, separate `qualification-review.json` and the full skip
inventory remain private; no account paths or telemetry identifiers are copied here.
The original `8ee714c` checkout and `provisioning-review.json` remain intact in their
separate failed-attempt directory; this result does not retroactively pass that run.

**Skip review:** every one of the **129 cases in 62 report groups** maps to a
committed `sys.platform != "linux"` guard with its reported reason. No unexpected
dependency, provisioning or standalone skip is present. Representative test names
below identify the excluded contracts; the private inventory retains every name
and per-group count.

| Main module | Skipped | Excluded contract and representative test names |
|---|---:|---|
| `test_coordination_authority.py` | 20 | Linux authority/writer-verifier supervision: `test_real_verified_authority_initialization_and_fresh_session_gate`, `test_abrupt_death_recovers_verified_high_water_without_reopening`, `test_entire_history_is_validated_beyond_first_bounded_batch`. |
| `test_coordination_completion.py` | 33 | Linux writer/completion supervision: `test_real_empty_completion_retains_proof_and_advances_exactly_one_hour`, `test_real_entity_completion_advances_high_water_atomically_and_preserves_originals`, `test_abrupt_completion_death_recovers_all_or_none_and_cannot_relaunch`. |
| `test_coordination_completion_controls.py` | 27 | Real Linux writer/verifier controls: `test_retained_proof_semantic_negatives_are_independent_of_audit_rejection`, `test_three_real_completed_hours_validate_across_instrumented_two_row_pages`, `test_v2_schema_fixture_preserves_genuine_authority_proof_and_reader_reservation`. |
| `test_coordination_execution.py` | 2 | Linux writer subreaper: `test_real_bound_empty_compactor_has_receipt_before_launch_but_still_blocks`, `test_real_local_migration_keeps_original_phase_evidence_and_blocks`. |
| `test_coordination_verification.py` | 10 | Linux writer supervision: `test_real_separate_standalone_empty_verifier_binds_intent_without_reopening`, `test_verifier_refuses_missing_or_changed_execution_shutdown_phase_evidence`. |
| `test_coordination_tick.py` | 3 | Linux procfs/subreaper: `test_abrupt_tick_death_never_launches_replacement_even_when_child_survives`, `test_real_supervised_callback_holds_ledger_lock_and_still_cannot_certify_empty_hour`, `test_supervisor_death_with_surviving_workload_remains_blocked`. |
| `test_coordination_supervisor.py` | 34 | Linux subreaper contract, including scalar/report negatives within the guarded module: `test_root_exit_does_not_leave_sleeping_or_detached_descendants`, `test_timeout_stops_sigterm_ignoring_tree_but_not_unrelated_child`, `test_caller_interruption_or_death_requests_cleanup_of_detached_tree`. |

**Disposition:** dcc-mac-baseline-01 passes and R9's reproducible packaging repair is
verified. R6 admission-clock and R7 SQL-integrity controls are included in the passing
native modules, but the worker's separate SQL-mutation result was not rerun. R8's
portable observers/platform refusal baseline passes; Linux-only real-tree and
completion paths remain skipped, not Mac-qualified. The worker's **641 main / 439
standalone full-suite** and **298 focus** Linux results remain separately attributed.
Supported Mac reader lifetime/shutdown, service/client/advisory exports/audited
recovery, actual-S3 and representative 32 GB RAM / 64 GB disk resource qualification
remain open. **dcc-02–05 stay unchecked.** No utility implementation, real grants or
dataset operation, source repair, deployment or assistant push; test data is synthetic.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_baseline.py; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py; ../Wintap-PyUtil/uv.lock; ../Wintap-PyUtil/extras/raw-sensor-compact/uv.lock -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_authority.py; ../Wintap-PyUtil/tests/test_coordination_completion.py; ../Wintap-PyUtil/tests/test_coordination_completion_controls.py; ../Wintap-PyUtil/tests/test_coordination_execution.py; ../Wintap-PyUtil/tests/test_coordination_verification.py; ../Wintap-PyUtil/tests/test_coordination_tick.py; ../Wintap-PyUtil/tests/test_coordination_supervisor.py §Linux-only skip guards -->

Maintainer documentation closure: `git diff --check` passes. Scoped checks cover
**11 changed wiki files, nine required-field frontmatters, 177 grounding paths,
208 inline source paths and 394 wikilinks (31 section targets)** with no new errors.
Existing index/log frontmatter exceptions and one historical broken log link remain
baseline issues, not whole-wiki acceptance. Complete diff/privacy review finds no
unauthorized identifiers; worker/original maintainer log histories and private
failed-attempt evidence are preserved. All stash conflicts are resolved; review
edits were left unstaged/uncommitted at that review checkpoint and the preservation
stash was retained. PyUtil's
unrelated environment artifacts remain untouched.

**Finalization:** the human subsequently authorized commit/push of the wiki review
and existing utility planning. Remaining implementation returns to the worker via
[[wiki/work/dbt-compaction-coordination/dev_handoff#Worker continuation after the Mac review]].
No additional runtime tests or acceptance claims are introduced by publication;
the original failure, reviewed skip boundaries and dcc-02–05 gates remain unchanged.
Finalization checks pass the same 11 wiki files/nine frontmatters, 177 grounding
paths, 208 inline sources and 401 links/37 section targets with no new errors;
complete diff/privacy and whitespace inspection pass. Baseline exceptions above
remain unchanged, and the pending push contains only wiki documentation.

### Baseline review regressions

Independent focused rerun before implementation, November 13, in the standalone
compactor checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_entities.py tests/test_cli.py
```

Result: **38 passed**. The main-checkout focused rerun:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_process_entities.py tests/test_dbt_source_validation.py \
  tests/test_compacted_inputs.py
```

Result: **63 passed, 1 skipped** (opt-in coverage). Both
commands were launched through temporary-directory wrappers, with `TMPDIR` and
pytest `--basetemp` scoped to disposable directories under `/tmp/opencode` and
automatic cleanup. They did not use real telemetry S3 qualification roots.

## Baseline Review Manual Checks

- Read the manager brief, full design, handoff and implementation review plus the
  updated canonical ETL and durable-entity pages.
- Inspected live SQL validation, incremental snapshot orchestration, checkpoint
  DBT validation, S3 setup, CLI phase sequencing and metric derivation.
- Source at the reviewed baseline confirmed R1's unused bootstrap argument/missing current-state binding,
  R2's omitted validation parity, R3's update-window metadata construction,
  R4's post-deletion publication and reconciliation return boundary, and R5's
  unconditional consultation of an unused remote metrics override.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §validate_state; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/publish_metrics; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

Three independent disposable local probes also reproduced R2/R3: SQL validation
accepted a duplicate-key snapshot and a non-parent scalar corrupted against its
retained evidence, while the earlier Python validator rejected both; an incremental
next-hour update moved persisted bootstrap provenance to that update hour. The
probes used live standalone fixture helpers, preserved snapshot metadata, and
removed their temporary files automatically. No source/test files were added.

The manager's other disposable-fixture/captured-SQL observations remain imported
evidence in [[wiki/work/dbt-compaction-coordination/implementation-review]], not
independent reproductions here. Current baseline passes do not close the findings.

Artifact checks pass: two new-page frontmatters, 18 grounding paths, four
wikilinks, both diagram XML/reference checks and new-page whitespace/IP-literal
scans. The complete new pages and index/log diff were manually inspected for
persistent-content privacy; no actual host/account/IP identifiers were added.
`git diff --check` passed. At review time, PyUtil retained only its pre-existing
untracked artifacts; the authorized implementation changes are described above.

## Results

**R2/R3 slice committed locally as PyUtil `7d2b7f8`:** active SQL integrity validation and
bootstrap provenance have pre-fix failures, post-fix passes, positive compatibility
controls and full standalone/main regression coverage. Canonical guidance and the
plan/checklist reflect these changes. Changed-file Ruff lint/format and both
repositories' `git diff --check` pass. Current artifact checks cover three page
frontmatters, 32 live grounding paths and ten wikilinks, plus whitespace and
IP/account-home-path scans. Complete additions/diffs were reviewed for persistent
wiki privacy. Unrelated untracked and ignored local settings/data remain untouched.
The human-requested milestone commit contains only the verified slice. No push or
scheduler deployment was performed.

The selected architecture remains appropriate for cooperative shared access.
[[wiki/work/dbt-compaction-coordination/implementation_plan]] proposes a safety
milestone before real deletion/recovery integration, then retains the five handoff
units. Ledger/protocol tests may use fake children independently of writer fixes.

## Known Gaps

- R9's original `8ee714c` provisioning failure is historical. The repaired `fab647f`
  handoff passes exact-source/locked-runtime checks and the scoped actual-Mac baseline;
  it does not qualify skipped Linux writer/completion paths or Mac reader shutdown.
- R6–R8 are addressed by slice A's formal clock repair, authority-independent SQL
  negatives/mutation evidence and portable observers/platform guards. Actual macOS
  offline rerun passes; supported reader shutdown remains open. Historical results retain
  their original scope.
- Protocol/ledger library is regression accepted with 54 focused and 397 full-main
  passes. The admission/draining tick focus passes 100 cases; its full-main
  regression passes 443 tests (three skips), before supervisor implementation.
  The supervision/evolving-clock revision passes 142 focused cases and 485 full-main
  tests (three skips). This accepts those library primitives, not the full dcc-02 gate.
  No production scheduler/client or coordinated runtime
  qualification exists yet; dcc-02 remains unchecked.
- Completion/cursor/admission atomicity is human-confirmed. The ledger-v3 local
  normal-success prototype now retains completed history and atomically advances
  evidence/run/optional high-water/exact-hour cursor/backlog mode. Its hardened
  local controls pass 46 plus 24 cases before the final three budget/clock red/green
  controls; final combined main focus passes 298 tests and full standalone passes
  439 (two skips). Full main passes 641 (three skips) on the unchanged revision.
  These close local v3 regression, not integrated service acceptance. Receipt-bound
  launch passes 194 combined cases and 537 full-main tests (three skips). Separate
  receipt/intent/shutdown-authenticated verification passes 204 main focus cases;
  standalone data/authority verification passes 259 focus and 431 full tests (two
  skips); full verifier foundation main passes 547 tests (three skips). Ledger v2
  now implements verified authority initialization/freshness, explicit compatible
  upgrade and main entity-verifier integration, with 236 main/299 standalone focus
  passes after recorded prerequisite/authentication/integration repairs. Full authority
  standalone passes 439 tests (two skips); full main passes 579 (three skips), before
  completion/history implementation. No caller-supplied report or receipt is
  completion authority. Conservative launch and blocked/restart recovery boundaries
  remain intact; audited recovery commands and integrated service/client are absent.
  This is not an actual-S3 service adapter or macOS gate.
- R2 SQL integrity and R3 provenance are repaired in `7d2b7f8` with red/green
  evidence; DBT's separate integrity macro remains narrower than CLI SQL validation.
- R1–R5/dcc-00 are prerequisite regression accepted. Do not certify coordinated
  writer recovery from freshness/coverage or synthetic repair success alone.
- Previous three-day rounds qualified SQL bootstrap and DBT compatibility, not
  scheduled incremental entity → deletion → checkpoint operation or complete ancestry.
- Steady-state resource measurements and actual shared-reader/writer latency remain
  unmeasured; example server budgets are unqualified.
- Client-platform supervision and deployment configuration still need confirmation.

## Follow-Ups

Worker-reported local v3 high-water/history/atomic-completion full regressions pass;
R9's repair and the actual-Mac offline baseline are now verified. Qualify supported
Mac reader-shutdown feasibility before claiming client acceptance. Follow
[[wiki/work/dbt-compaction-coordination/macos-qualification#Stage 2: reader backend acceptance remains pending]];
continue service and audited operations before real destructive qualification.
Add commands, negative regressions and runtime
qualification results as each planned unit is implemented.
