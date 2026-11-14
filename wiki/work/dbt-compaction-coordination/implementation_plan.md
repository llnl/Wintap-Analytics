---
title: "Implementation Plan: Scheduled DBT and Compaction Coordination"
type: concept
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/brief.md
  - wiki/work/dbt-compaction-coordination/design.md
  - wiki/work/dbt-compaction-coordination/dev_handoff.md
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/Makefile
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/dbt-compaction-coordination; ../Wintap-PyUtil/wintappy; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, implementation-plan, coordination, dbt, compaction, recovery]
---

# Implementation Plan: Scheduled DBT and Compaction Coordination

## Scope

**Implementation authorized; production deployment remains outside this milestone.**
Analytics pulled manager commit `91f741e`; PyUtil's reviewed baseline was `c782f63`. The incoming
change contains design, handoff, review and ETL documentation, not coordinator code.
Implementation belongs in PyUtil; work tracking belongs in this wiki.

Verified R2/R3 milestone committed locally in PyUtil as `7d2b7f8`; no push or
production deployment. Freshness and the remaining safety gates follow separately.

Human acceptance gates: capture failing regressions before implementation and passing
results afterward through active verification/update paths; restore validation in
bounded SQL without per-process Python state; preserve bootstrap provenance for
changed/unchanged updates, replay and resumed initialization; reject rollback while
allowing forward evolution with different historical checkpoint hashes.

Retain the selected architecture: one minute-based cron coordinator, S3 messages,
an authoritative local DuckDB ledger, concurrent shared readers and an exclusive
hourly writer. Entirely local DBT stays direct and requires no coordination state.

## Steps

### 0. Safety prerequisites — proposed dcc-00 milestone

Address the manager's review findings before certifying real writer/recovery work:

| Finding | Required follow-through | Exit evidence |
|---|---|---|
| R2: incomplete SQL snapshot validation | Restore valid/unique host-scoped keys, exact evidence shape/types, publication bounds and agreement of all derived scalars/flags with evidence. Stay SQL-backed; do not restore a per-process Python cache. | Corrupted and duplicate snapshots fail; valid conflicts, empty initialized hosts, permutations and replay retain semantics. |
| R3: bootstrap reset | Preserve validated existing bootstrap metadata across incremental updates, replay and resumed initialization; reports agree with persisted metadata. | Update a later hour and repeat an unchanged update without moving provenance. |
| R1: stale snapshot passes coverage checks | Specify and implement a receipt-backed current-state freshness contract: expected hosts, current aggregate snapshot identities, provenance and covered-hour lineage. Validate restoration/cutover explicitly. | Snapshot rollback/replacement fails; legitimate forward evolution and current-window evidence remain supported. |
| R4: deletion/checkpoint phase boundary | Define machine-readable phase evidence and repair behavior. Preserve original per-event migration evidence separately from overwriteable coverage checkpoints; expose coordinator-to-CLI run identity mapping. | Inject failure after deletion, retain uncertainty, repair coverage under exclusivity, and verify all phases before reopening. |
| R5: unused metrics root | Ignore the metrics override consistently in routing and S3 setup when entity mode is disabled; bind it whenever active. | Local-only mode with an unused remote override makes neither S3 nor coordination calls. |

Do **not** compare the latest snapshot hash with every historical hourly hash:
aggregate snapshots legitimately evolve. Define the latest committed state and its
coverage lineage together. Exact receipt/freshness representation is an implementation
design checkpoint, not an already-implemented schema.

Freshness design constraints for the next slice:

- A latest committed-state receipt must bind effective roots, namespace, expected
  hosts, per-host original bootstrap declarations and current aggregate identities.
- Historical coverage must name its own committed generation/input evidence; validate
  that generation's identity and its proven lineage to current state, not equality
  between its historical snapshot hash and today's aggregate snapshot.
- Durable publication intent must precede host replacement. Recovery can accept only
  the recorded before/after candidates of that intent; it cannot bless an arbitrary
  self-consistent snapshot by creating a new receipt. Preserve partial-host, explicit
  resumed-init and lost-ack recovery regressions.
- Missing/legacy authority needs an explicit verified rebuild/cutover procedure;
  existing compatible metadata/checkpoints are not enough to silently seed trust.
- Rejection of a snapshot rollback with retained authority is distinct from detecting
  rollback of the entire authority store. The latter needs an independent high-water
  mark in the eventual local ledger/operator recovery record.

These are proposed constraints, not a selected persisted schema or an implemented
freshness guarantee. A disposable real-DBT forward/rollback probe confirms the gap
remains after the integrity/provenance fixes; see verification.
<!-- SYNTHESIS: proposed prerequisite ordering from wiki/work/dbt-compaction-coordination/implementation-review.md R1–R5 and live entity/CLI/DBT sources listed in frontmatter -->

The current combined CLI publishes entities, migrates/deletes raw, then publishes
checkpoints. `reconcile-delete` returns without checkpoint publication; entity-only
replay reports raw work `not_run` and can overwrite fixed-hour metrics. These are
three distinct recovery obligations, not one success flag.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/publish_metrics; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows -->

### 1. dcc-01 — Protocol and durable ledger

- Implement canonical dataset/root binding, stable job/grant identities and strict
  message validation; preserve terminal records and cancellation tombstones.
- Use real local DuckDB with fake transport to prove transactional reader
  reservations and immutable grant outbox entries precede PUT.
- Commit writer/run intent before subprocess launch. A missing ledger refuses
  ordinary operation; unresolved writer intent becomes `BLOCKED` after restart.
- Prove duplicates, reordered terminal messages, lost acknowledgments and crashes
  cannot erase a reservation or issue a second permission.

This unit can use fake children while prerequisite fixes stabilize; it must not
launch real destructive compaction before the safety gate passes.

### 2. dcc-02 — Tick and scheduling

- Take the same nonblocking local process lock before every ledger open, including
  operator commands, and hold it through supervised writer completion.
- Process terminal messages first. Due work enters `DRAINING` before new admission;
  every outstanding reader reservation excludes the writer, delivered or not.
- Persist the oldest unfinished UTC hour; use ten-minute grace and one hour per
  tick. Keep backlog priority until caught up; never infer a cursor from object age.
- Test midnight/grace boundaries, missed ticks, empty hours, overlapping ticks,
  surviving children and failures around launch with controllable clocks.

### 3. dcc-03 — DBT wrapper and local compatibility

- Resolve defaults and overrides for raw, compacted, entity and active metrics
  inputs before initializing coordination. Any active S3 root selects shared mode.
- Move source preflight inside the same grant as build/tests; use equivalent
  routing for standalone source, test, docs and generic source-reading commands.
- Supervise the full child tree. Persist and upload release only after all managed
  readers stop; retain pending terminal messages for retry after uncertain delivery.
- Missing entity-hour coverage must fail clearly and release, never wait under a
  reader grant for the excluded writer, trim the window or disable enrichment.
- Prove the ordinary local raw-only full build succeeds without AWS, entities,
  compacted directory, compactor installation or coordination calls/job records.

### 4. dcc-04 — Real compactor integration and recovery operations

- Invoke the isolated DuckDB 2.0.0 CLI for one explicitly eligible hour. The main
  DuckDB 1.5.6 environment alone owns the ledger.
- Capture command/config identity, stdout/stderr and full per-event/protocol
  outcomes. Exit zero, a top-level `completed`, or `skipped_existing` alone is not
  sufficient migration evidence.
- Hold exclusivity across entity publication, raw migration/deletion, final
  checkpoint verification, child shutdown and durable receipt/cursor COMMIT.
- Implement audited status, manual abandoned-reader recovery, blocked-hour
  reconciliation and exclusive entity maintenance. No automatic grant expiry.
- Add configuration/cron examples and operator procedures, but do not install or
  enable production cron as part of code qualification.

### 5. dcc-05 — Isolated qualification and closeout

- Use fresh feature-owned S3 fixtures: two overlapping readers, a due writer and
  a queued third reader. Assert no writer overlaps any reader reservation.
- Qualify sequential hourly entity update → raw deletion → checkpoint publication,
  restart and recovery, including checkpoint failure after deletion. The earlier
  three-day bootstrap rounds are not evidence for this combined lifecycle.
- Run full main and standalone regressions; compare local/raw/compacted DBT
  schemas, populations, conflict semantics and ancestry-quality outcomes.
- Measure steady-state entity read/hash/rewrite time, peak RSS/CPU, temporary
  storage/spill and I/O with realistic retained snapshots and chosen server limits.
  One selected hour does not bound accumulated entity state; the example 2 GB/4 GB
  budgets are not qualified by successful 128 GB/256 GB bootstrap runs.
- Report actual polling delays separately from writer/DBT runtime; defaults imply
  up to approximately 70 seconds startup and 60 seconds release observation absent
  contention, not hard deadlines.
- Remove only feature-owned test data after recording anonymized results. Update
  canonical ETL/entity guidance and diagrams once behavior is implemented.

## Files Likely To Change

In PyUtil: proposed `wintappy/coordination/{protocol,ledger,coordinator,client}.py`,
package marker, four coordination test modules and `config/coordination.*` examples;
`Makefile`, `scripts/check_dbt_config.py`, DBT macros, writer entity/CLI/metrics
modules, their tests and user/operator READMEs. See the exact source map in
[[wiki/work/dbt-compaction-coordination/dev_handoff]]. No sensor or packaging changes.

## Tests To Add Or Update

Use the handoff's full acceptance matrix, with R1–R5 negative regressions added
before recovery certification. Record commands/results in
[[wiki/work/dbt-compaction-coordination/verification]]; keep baseline regression
passes distinct from corruption probes and new concurrency qualification.

## Migration Or Compatibility Notes

- Preserve Parquet interchange and `evidence_json`, exited ancestors and recorded
  instance identities. No silent pruning, fabricated ancestry or PID-only repair.
- Keep coverage checkpoints distinct from migration receipts and the ledger. Any
  freshness/schema change needs an explicit upgrade/rebootstrap plan, not automatic
  acceptance of old compatible-looking state.
- Coordination is cooperative, dataset-wide and not a freeze of sensor uploads.
  Ad-hoc queries/dashboards over raw-backed views must participate too.
- Confirm supported client platforms/process-tree supervision, deployment roots,
  endpoint configuration, first unfinished hour, event allowlist, entity identity
  policy and measured budgets before rollout. No secrets in persisted examples.

## Rollback Plan

Stop scheduled admission, establish that every existing reader/writer has stopped
and cannot resume, then return to explicit operator-managed exclusion. Preserve
ledger/WAL, receipts and blocked-state evidence. Do not auto-create an empty ledger,
restore an old backup as current authority, or undo completed deletion by reverting
code. Post-deletion failures require verified data/state repair before reopening.

## Done Checklist

- [x] Pull manager documentation and inspect live implementation supporting R1–R5.
- [x] Prepare phased plan without implementing or deploying coordination.
- [x] Receive implementation authorization and record the four human acceptance gates.
- [x] R2: active-path red/green tests and bounded SQL integrity parity.
- [x] R3: changed/unchanged/replay/resumed-init provenance red/green tests.
- [ ] R1: current-state freshness and historical forward-lineage red/green tests.
- [ ] dcc-00: integrity, provenance, freshness/phase-evidence and routing safety gates.
- [ ] dcc-01: protocol/ledger with transaction and restart evidence.
- [ ] dcc-02: scheduling/exclusion with controlled-clock and child-failure evidence.
- [ ] dcc-03: DBT lifetime, terminal-message retry and local compatibility.
- [ ] dcc-04: qualified CLI integration and audited recovery operations.
- [ ] dcc-05: isolated runtime, incremental resource and regression qualification.
- [ ] Human rollout approval; production deployment recorded separately.
