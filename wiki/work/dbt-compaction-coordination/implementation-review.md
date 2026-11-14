---
title: "Review: Durable Entity Implementation and Coordination Impacts"
type: diagnostic
confidence: high
grounded_by:
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/tests/test_process_entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entities.py
  - wiki/work/durable-process-entity-manager/verification.md
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: reviewed
source_paths: ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt
tags: [review, coordination, entity-state, checkpoints, recovery, local-only]
---

# Durable entity implementation: coordination review

**The single-coordinator/shared-reader/exclusive-writer design still fits.** Extend
its dataset binding and completion checks to processing checkpoints. Several
reproducible correctness gaps need attention when integrating writer recovery.
Implementation remains owned by Wintap-PyUtil; this review and the coordination
handoff live in Wintap-Analytics.

## Integrated revisions

- Analytics fast-forwarded `9edb246` → `d904559` (nine commits).
- PyUtil fast-forwarded `c60dbdb` → `c782f63`: coverage checkpoints (`f1aa9c5`),
  explicit quarantine (`722be8c`), bounded quarantine (`dc20808`), SQL state
  (`c782f63`).
- Restored the local coordination/ETL work; merged both sets of index/log additions.
  ETL files and the feature folder matched the preservation stash before review
  edits. The conflict is resolved and the verified preservation stash was dropped.

## Findings

### R1 — High: checkpoint presence does not bind the current entity snapshot

`validate_processing_metrics()` checks selected hours, status/version, namespace,
identity policy and quarantine arithmetic. It does **not** compare recorded input
fingerprints, snapshot hashes, expected host count or bootstrap provenance with
the snapshots being consumed; its `bootstrap_starts` argument is unused.
Restoring/replacing a snapshot while leaving compatible checkpoints can therefore
pass preflight with missing historical context.

**Reproduced:** generated the existing synthetic DBT fixture, removed its historical
bridge/root rows from the snapshot while preserving schema/metadata and checkpoints,
then ran real `validate_raw_sensor_source`. It exited **0**. This is a structural
coverage check, not a freshness or same-generation guarantee. Existing tests also
deliberately allow new current-window evidence before entity maintenance catches up.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics; ../Wintap-PyUtil/tests/test_process_entities.py §test_parent_conflict_terminates_instead_of_arbitrary_repair -->

**Coordination consequence:** never rebuild the coordinator ledger, reopen after
recovery, or infer writer success from these checkpoints alone. Keep a durable
validated run receipt and reconcile current snapshots/checkpoints before reopening.
A future stronger freshness contract must support legitimate forward snapshot
evolution: an old hour's snapshot hash will normally differ from today's aggregate
snapshot, so equality with every historical checkpoint is not a correct fix.

### R2 — High: SQL snapshot verification lost integrity checks

The active `validate_sql()` path checks schema/metadata, row/file budgets, JSON
syntax/host mismatch and derived parent scalars. Compared with `EntityStore.validate`,
it omits unique/valid instance-key checks, full evidence structure/type checks,
publication-bound validation and non-parent scalar/evidence agreement.

**Reproduced:** SQL validation accepts both a duplicate-key snapshot and a snapshot
whose `os_pid` is changed to 999 while evidence still records 10. The earlier Python
validator rejects the latter. The duplicate fixture uses `hive_partitioning=false`
to retain the exact snapshot schema. DBT has its own duplicate checks, but neither
its parent-only scalar check nor the CLI's current `entities-verify` is a complete
replacement for the lost validation.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §validate_state; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §validate/validate_sql; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §entities-verify -->

**Coordination consequence:** restore SQL integrity parity and test corruption before
treating `entities-verify` as sufficient recovery evidence. A lock prevents overlap;
it cannot establish the correctness of an already-corrupt snapshot.

### R3 — Medium: incremental updates reset bootstrap provenance

`update_entities()` constructs metadata from `hours[0]` even for an existing host,
instead of retaining the validated snapshot's original bootstrap declaration.
A changed host is republished with the latest update start; an unchanged host's
report can instead disagree with its retained file metadata.

**Reproduced:** initialize synthetic hour 00, then add a Stop in hour 01 and update
only that hour. Persisted `bootstrap_start` moves from `00:00Z` to `01:00Z` although
the original entity evidence remains. The prior implementation retained metadata
returned by snapshot validation.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

**Coordination consequence:** preserve bootstrap provenance in incremental/replay
tests; do not derive scheduling coverage or reconstruct the cursor from that field.

### R4 — High integration requirement: recovery spans three publication phases

The combined CLI publishes/verifies entities, performs raw compaction/deletion,
then publishes/verifies fixed-hour `processing_metrics` objects. A checkpoint error
can occur after irreversible source deletion, and multi-host/multi-hour publication
is not atomic. `reconcile-delete` may itself update entities when configured, but
its return branch neither publishes checkpoints nor returns the entity report.

**Reproduced:** inject a final checkpoint-publication failure into a two-hour local
combined run. Both raw hours are deleted and compacted outputs exist when the
command fails. A following entity-enabled `reconcile-delete --confirm-delete`
returns **0** without any checkpoint publication. An explicit `entities-replay`
then publishes coverage checkpoints with `(status, raw_status, deletion_status)`
equal to `('completed', 'not_run', 'completed')`.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §publish_metrics/run; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows/ProcessingMetricsStore -->

**Coordination consequence:** hold exclusivity through final checkpoint verification
and receipt COMMIT. Keep failures `BLOCKED`; recovery must establish raw migration,
entity integrity and checkpoint coverage separately. Entity-only checkpoints are
coverage records, not deletion receipts; DBT also accepts
`completed_with_deletion_errors`. Link coordinator run IDs to the CLI-generated
metrics run ID rather than assuming they are the same. Fixed-hour replay overwrites
the checkpoint, so retain the original migration receipt in the ledger/run archive.

### R5 — Medium: fourth-root routing and unfinished-window behavior

`WINTAP_DBT_PROCESSING_METRICS_ROOT` defaults to `<dataset>/processing_metrics`.
Entity-enabled DBT requires these checkpoints. The S3 setup macro also consults
an explicit remote metrics override when entity mode is disabled.

**Reproduced offline:** render `configure_raw_sensor_access()` with local raw and
compacted roots, no entity root, and a synthetic remote metrics override. It invokes
S3 secret setup (captured SQL only; no credentials or network used).
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §defaults; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics -->

**Coordination consequence:** classify/bind the metrics root whenever it is active;
explicitly ignore an unused metrics override consistently in both routing and S3
setup when entities are disabled. Until that integration change, clear the override
when switching to local mode. Preserve the ordinary two-command local quick start.

An entity-enabled request containing an as-yet-uncheckpointed process hour fails
preflight even after receiving a grant. Hourly maintenance intentionally lags the
active hour/grace interval. Report the coverage gap, release after children stop,
and let the caller select a covered window or retry later. Do not silently trim
the window, disable entities, or hold a read grant while waiting for the writer.

## Qualification interpretation

The worker reports two successful isolated three-day rounds: seven snapshots,
2,613,678 entities, 71 checkpoints, entity DBT **146/146 PASS**, non-entity baseline
**140/140 PASS** and matching process key/row counts. SQL state construction solves
the earlier Python decoded-state bottleneck in those runs. The latest round ran
raw compaction without deletion, then entity initialization: it does not qualify
the complete scheduled incremental entity → deletion → checkpoint lifecycle.

The successful bootstrap used explicitly large budgets (128 GB DuckDB memory,
256 GB temporary storage, 64 GiB per-host snapshot limit). Measure steady-state
full-snapshot reads/hashing/rewrites under the coordinator's actual budget; one
selected hour does not bound the size of retained entity state. Historical ancestry
remains incomplete (two root-reached seeds); that is separate from mutual exclusion.
These are imported results, not newly repeated remote tests.
<!-- GROUND_TRUTH: wiki/work/durable-process-entity-manager/verification.md §SQL-backed capacity rerun/Repeat three-day round; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §state_hash -->

## Fresh review evidence

- Standalone `.venv/bin/python -B -m pytest -q -p no:cacheprovider
  tests/test_entities.py tests/test_cli.py`: **38 passed**.
- Main `.venv/bin/python -B -m pytest -q -p no:cacheprovider
  tests/test_process_entities.py tests/test_dbt_source_validation.py
  tests/test_compacted_inputs.py`: **63 passed, 1 skipped** (opt-in coverage).
- Eight focused observations reproduced with disposable local fixtures or captured
  Jinja SQL: bootstrap reset, scalar corruption acceptance, duplicate acceptance,
  post-deletion checkpoint failure, reconciliation without publication, entity-only
  checkpoint statuses, stale-snapshot DBT acceptance, and unused-root S3 setup.
- Probe fixture corrections: disabled inferred Hive columns in the duplicate copy;
  changed the captured-SQL assertion to case-insensitive matching. Both corrected
  probes reproduced the findings. All temporary fixtures were removed.
- Artifact checks: seven page frontmatters, 100 grounding paths, 38 wikilinks/section
  targets, 19 handoff source-table paths, prompt paths, six shell examples and JSON
  syntax pass. Diagram XML/references/geometry validate (ETL: 53 cells; sequence:
  42/44 cells). All three pages render; vertex labels fit after ETL label/edge cleanup.
  Complete changed content was reviewed for privacy; whitespace checks pass.
- Repository checks at review completion: both pulled heads matched their upstream
  tracking refs; no staged or unmerged files. Wiki changes were not yet committed.
  PyUtil retained only its two pre-existing untracked environment files.

The probes import the live fixture helpers and use the existing isolated DuckDB
2.0.0 writer / 1.5.6 DBT environments. They add no source/test files. No remote
qualification was run for this review. Coordination implementation and its
concurrency/restart tests remain future work.

Follow-through: [[wiki/work/dbt-compaction-coordination/dev_handoff]] and
[[wiki/work/dbt-compaction-coordination/design]].
