---
title: "Verification: Scheduled DBT and Compaction Coordination"
type: concept
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_cli.py
  - ../Wintap-PyUtil/tests/test_process_entities.py
  - ../Wintap-PyUtil/tests/test_dbt_source_validation.py
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
policy: agent-editable
last_validated: 2026-11-13
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

### Freshness probe — still red

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

- No coordinator/client code or coordination runtime tests exist yet.
- R2 SQL integrity and R3 provenance are repaired in `7d2b7f8` with red/green
  evidence; DBT's separate integrity macro remains narrower than CLI SQL validation.
- R1 freshness representation and R4 migration/repair evidence remain implementation
  prerequisites. Rollback still passes real DBT preflight; do not certify writer recovery.
- Previous three-day rounds qualified SQL bootstrap and DBT compatibility, not
  scheduled incremental entity → deletion → checkpoint operation or complete ancestry.
- Steady-state resource measurements and actual shared-reader/writer latency remain
  unmeasured; example server budgets are unqualified.
- Client-platform supervision and deployment configuration still need confirmation.

## Follow-Ups

Continue the authorized safety milestone with receipt-backed freshness and phase-safe
recovery before real destructive writer integration. Add commands, negative regressions
and runtime qualification results as each planned unit is implemented.
