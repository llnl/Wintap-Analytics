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
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py
  - ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/tests/test_coordination_tick.py
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - wiki/work/dbt-compaction-coordination/verification.md
policy: agent-editable
last_validated: 2026-11-14
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: reviewed
source_paths: ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt
tags: [review, coordination, entity-state, checkpoints, recovery, local-only]
---

# Durable entity implementation: coordination review

**The milestone makes substantial progress; dcc-02 acceptance remains open.**
R1–R5 have implemented repairs, and the protocol/ledger provides a conservative
foundation. Review follow-through covers the confirmed admission bug, SQL-test
isolation and platform-aware tests before continuing integrated completion work.
Implementation remains owned by Wintap-PyUtil; this review and the coordination
handoff live in Wintap-Analytics.

## Milestone review — 2026-11-14

Pulled Analytics `91f741e` → `660b5a8` and PyUtil `c782f63` → `fe7fcb5`, both
fast-forward. Both heads match their fetched upstream branches. Restored the earlier
feedback notes, resolved index/log conflicts retaining both histories, verified the
preserved review/log content and dropped the preservation stash. The worker's
[[wiki/work/dbt-compaction-coordination/implementation_plan]] and
[[wiki/work/dbt-compaction-coordination/verification]] are now available and reviewed.

### Assessment of R1–R5 and implementation scope

| Area | Current assessment |
|---|---|
| R1 freshness | The new authority journal binds committed current state and historical checkpoint generations; pending intent blocks ordinary reads, and forward evolution retains historical lineage. Whole-store rollback still requires the planned independent high-water mark. |
| R2 SQL integrity | Unique/valid keys, evidence structure/types, publication bounds and derived scalar/flag agreement are restored in SQL. Independent direct probes reject the original duplicate/scalar defects. R7 below identifies a regression-test gap. |
| R3 provenance | Existing validated bootstrap metadata is retained for changed/unchanged updates, replay and resumed init. |
| R4 recovery | Immutable local phase archives, explicit CLI/coordinator ID mapping and original-generation checkpoint repair address the prior missing-evidence boundary. Integrated coordinator completion still needs independent verification. |
| R5 local routing | Active-root resolution ignores unused metrics overrides when entities are disabled; ordinary local DBT retains its direct path. |
| dcc-01 | Reader reservation/outbox COMMIT precedes grant publication; writer intent COMMIT precedes callbacks. Restart retains unresolved ownership and blocks replacement. |
| dcc-02–05 | Tick/supervisor libraries are partial. Every callback outcome remains `BLOCKED`; there is no success/cursor/reopening API or DBT client wrapper yet. |

<!-- SYNTHESIS: live milestone sources listed in frontmatter, compared with implementation_plan.md and verification.md; original R1–R5 below describe c782f63. -->

The next integration gates remain the non-secret effective execution/configuration
receipt, independent phase and shutdown verification, authority high-water checks,
atomic completion/run/cursor/mode COMMIT, client lifetime/release handling and
isolated sequential-hour/concurrency/resource qualification. The worker's Linux
red/green and full-suite records remain attributed evidence; this maintainer's
fresh macOS results and probes are recorded separately in
[[wiki/work/dbt-compaction-coordination/verification#Maintainer milestone review — November 14]].

### R6 — Medium: ingestion can cross grace and still admit a reader

**Independently reproduced; already disclosed by the worker.** `tick` refreshes
time before `ingest_many`, then uses that observation for `writer_due` and admission.
The next refresh follows grant publication. A disposable real-DuckDB/fake-S3 probe
runs the original ingestion and advances only the injected clock on return:

- Control at `00:09:59`: `OPEN`, one reader/grant, zero waiting.
- Ingestion crosses to `00:10:00`: `DRAINING`, one newly reserved reader/grant,
  zero waiting; expected zero new readers/grants and one waiting request.

This violates writer priority and can delay catch-up by an entire DBT run. The
reservation still excludes the writer, so the probe establishes no overlap.
Refresh after ingestion before admission, add the formal failing/passing boundary
test, and retain already committed reader reservations.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick, lines 87–103 -->

### R7 — Medium: authority rejection masks SQL-integrity regression tests

**New test-isolation finding.** The 80 parameterized corruption tests rewrite a
committed snapshot, then assert only a generic CLI error or `CompactionError`.
Current-state authority now rejects those bytes even if SQL validation stops
checking keys, evidence and scalar agreement.

**Reproduced:** replace `_validate_evidence` with a no-op only in the review
process, leaving authority active; all **80 tests pass** (14 deselected). No source
file is edited. Direct `EntityStore.validate_sql` probes reject duplicate keys and
scalar/evidence disagreement normally, but accept the same fixtures under that
mutation. Thus the implementation is repaired, while these tests cannot independently
protect it from recurrence.

Add authority-independent negative checks through `validate_sql` and/or corrupt
pre-publication candidates through the active update path, retaining the existing
end-to-end freshness checks. Removing the SQL validator must make the integrity
regressions fail. Require SQL-specific diagnostics where appropriate; do not seed
new trust from an arbitrary edited committed snapshot.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py §test_corrupt_snapshot_rejected_by_verify_and_update; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §validate_sql/update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §_validate_evidence -->

### R8 — Medium: Linux-only test assumptions escape platform guards

The standalone directory-fsync test resolves descriptors through `/proc/self/fd`
without a platform guard; both parameter cases fail on macOS. Two tick integration
tests also invoke the explicitly Linux-only supervisor without the skip applied
to `test_coordination_supervisor.py`. One requires a captured report; the other
requires a child PID file and `/proc` state even though launch is refused.
The abrupt-tick-death test's `launch_child=True` case independently assumes
`/proc/<pid>/stat` exists. These account for all five fresh suite failures:
standalone **305 passed, 2 failed, 2 skipped**; focused main **196 passed,
3 failed, 35 skipped**.

Use portable descriptor observation where practical and mark actual Linux-only
integration tests explicitly. Retain Linux execution of these durability/tree tests
and add a separate non-Linux refusal control; skipping unsupported execution is
not evidence of successful supervision on other client platforms.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py §test_new_publication_directory_links_are_fsynced_before_success; ../Wintap-PyUtil/tests/test_coordination_tick.py §test_abrupt_tick_death_never_launches_replacement_even_when_child_survives/test_real_supervised_callback_holds_ledger_lock_and_still_cannot_certify_empty_hour/test_supervisor_death_with_surviving_workload_remains_blocked; ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_config -->

## Baseline integrated revisions — 2026-11-13

- Analytics fast-forwarded `9edb246` → `d904559` (nine commits).
- PyUtil fast-forwarded `c60dbdb` → `c782f63`: coverage checkpoints (`f1aa9c5`),
  explicit quarantine (`722be8c`), bounded quarantine (`dc20808`), SQL state
  (`c782f63`).
- Restored the local coordination/ETL work; merged both sets of index/log additions.
  ETL files and the feature folder matched the preservation stash before review
  edits. The conflict is resolved and the verified preservation stash was dropped.

## Baseline findings — PyUtil c782f63

The following reproductions and source descriptions are historical. Their current
dispositions are in the milestone assessment above.

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

## Baseline review evidence — 2026-11-13

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

## Worker response — reported 2026-11-13

The human relayed the implementing worker's initial feedback. The worker agrees
with R1–R5 and reports independent reproduction of duplicate-key acceptance,
non-parent scalar corruption acceptance and bootstrap reset, plus the same focused
results: 38 standalone passed; 63 main passed, one skipped. This corroborates the
reported defects; it does not close them or add an independent reproduction of
R1/R4/R5.
<!-- SOURCE: Human-relayed initial worker feedback, conversation 2026-11-13; worker artifacts not yet available in this checkout. -->

The worker recommends a small SQL-integrity/provenance repair milestone before
ledger/protocol work, followed by scheduler, DBT wrapper, compactor/recovery and
isolated sequential-hour/concurrency qualification. Freshness, independent migration
receipts and unused-root routing remain prerequisites for real integration. The
worker reports saving an implementation plan and verification record, with wiki
changes uncommitted and no code changes, cron deployment or push. Those new files
were not present locally when this feedback was received. They became available
and were reviewed with the November 14 milestone above.

**Maintainer assessment:** this is a compatible refinement of the handoff's order.
For the first repair milestone, require failing-before/passing-after regression
evidence through the active verification/update paths; cover invalid/duplicate
keys, evidence/scalar integrity and bootstrap preservation across changed and
unchanged updates/replay. Restore validation in the bounded SQL path so the repair
does not reintroduce the full-state Python materialization bottleneck. Subsequent
freshness checks must accept legitimate forward snapshot evolution while rejecting
rollback; historical checkpoint hashes cannot all equal the current snapshot.
The combined incremental lifecycle and realistic server-budget qualification remain
open acceptance work.
<!-- SYNTHESIS: review R1–R4 and Qualification interpretation above, compared with the human-relayed worker plan. -->

Follow-through: [[wiki/work/dbt-compaction-coordination/dev_handoff]] and
[[wiki/work/dbt-compaction-coordination/design]].
