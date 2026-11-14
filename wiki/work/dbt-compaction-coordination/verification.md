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
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
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
reservations. Formal regression and repair remain pending. The earlier 142/485
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

Pending acceptance evidence: bind the actual qualified executable/runtime/arguments
and resolved roots/hour/run IDs/events/entity policy/deletion/budgets to durable
writer intent before launch; prove default/override/allowed-environment resolution,
receipt integrity and bounds, mismatched scope/command refusal and synthetic secret
exclusion from persisted artifacts/diagnostics. Post-launch uncertainty cannot
advance the cursor or reopen admission. A partial command manifest or exit-zero
report is insufficient. No implementation or behavioral test result is claimed
for this new requirement; dcc-02 remains unchecked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_manifest -->
<!-- SYNTHESIS: explicit human requirement on 2026-11-14, recorded before implementation -->

### Commit snapshot — November 14

Committed the 32 feature-owned PyUtil files as `fe7fcb5` on
`work/raw-sensor-compacted-union`: R1/R4/R5, protocol/ledger and tick/supervision
prototypes, tests and READMEs. Preserved unrelated data, environment files and
ignored settings. The source coordination README now explicitly records the
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

- Protocol/ledger library is regression accepted with 54 focused and 397 full-main
  passes. The admission/draining tick focus passes 100 cases; its full-main
  regression passes 443 tests (three skips), before supervisor implementation.
  The supervision/evolving-clock revision passes 142 focused cases and 485 full-main
  tests (three skips). This accepts those library primitives, not the full dcc-02 gate.
  No production scheduler/client or coordinated runtime
  qualification exists yet; dcc-02 remains unchecked.
- Collaborative review confirms a pre-admission grace-boundary defect when
  ingestion crosses the deadline. The active-path probe is red; formal regression
  and repair are pending. Completion/cursor/admission atomicity is human-confirmed,
  but the success/reopening API remains unimplemented.
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

Continue dcc-02 scheduling and DBT lifetime integration before
real destructive writer qualification. Add commands, negative regressions and runtime
qualification results as each planned unit is implemented.
