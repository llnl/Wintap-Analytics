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
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintappy/coordination/protocol.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/tests/test_coordination_tick.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/execution.py
  - ../Wintap-PyUtil/wintappy/coordination/writer.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/storage.py
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintappy/coordination/verification.py
  - ../Wintap-PyUtil/wintappy/coordination/authority.py
  - ../Wintap-PyUtil/wintappy/coordination/completion.py
  - ../Wintap-PyUtil/tests/test_coordination_authority.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py
  - ../Wintap-PyUtil/scripts/dcc_macos_baseline.py
  - ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py
  - ../Wintap-PyUtil/uv.lock
  - ../Wintap-PyUtil/wintappy/coordination/maintenance.py
  - ../Wintap-PyUtil/wintappy/coordination/recovery.py
  - ../Wintap-PyUtil/tests/test_coordination_maintenance.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_verification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_observations.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_completion.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_publication.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_completion_qualification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publications.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py
policy: agent-editable
last_validated: 2026-11-15
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

### 0. Safety prerequisites — dcc-00 regression gate

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
coverage lineage together. The selected implemented representation is described below.

Freshness design constraints retained by R1:

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

### Selected R1 representation — regression accepted

Use a versioned Parquet authority journal at the entity root's
`_authority/authority.parquet`. DuckDB owns historical rows; Python retains only
the latest bounded host/publication metadata. Every generation records its ordinal
and parent ID, immutable effective-root/namespace/expected-host/policy binding,
original per-host bootstrap declarations, before/after snapshot byte identities,
after semantic identities, update window and original process input fingerprint.
The fixed journal retains all ancestors; exceeding a configured budget fails,
never truncates history. Generation IDs checksum named receipt fields (excluding
the pending/committed status), including the predecessor ID. Snapshot semantic
identities use named-struct JSON row hashes in 1,024-row digest batches, avoiding
the incompatible unnamed-row JSON formats in the two supported DuckDB pins.

Publication writes and verifies a final-row `pending` intent before any host PUT,
then writes/verifies `committed` only after all after candidates and input rechecks
pass. Ordinary DBT/verification rejects pending intent. Exclusive replay/resumed
init may continue only when each live host is one of that intent's exact recorded
before/after byte candidates, binding/window/input evidence still matches, and the
reduced candidate still equals the recorded after state. An arbitrary valid
replacement cannot become trusted through replay. Authority PUT/ack failures keep
the outcome uncertain until exact GET verification/recovery.

Version-4 coverage names its committed generation. Validate the whole unbroken
authority chain and current aggregate identities; each selected hourly checkpoint
must match its own committed receipt's host count, original bootstrap summary,
semantic hashes and input fingerprint, and lie within that receipt's update window.
Do not bind coverage to the live raw inventory: new current-window producer evidence
must remain queryable before hourly maintenance catches up.

Legacy state without authority fails closed. The explicit upgrade path uses fresh
entity and metrics roots initialized from a sufficiently retained raw/compacted
archive under operator exclusion, verified with newly published version-4 coverage, then an
explicit reader-root cutover. Never create authority from an arbitrary existing
snapshot. Preserve the old root/evidence; missing archive history blocks claiming
equivalent recovery. Restoring the entire journal plus snapshots still requires an
independent ledger/operator high-water mark to detect; this slice cannot prove it.

This contract is implemented in the working tree, with 164 focused standalone and
14 focused real-DBT tests passing. Three additional null/window checkpoint cases
failed before their repair. Full gates pass 266 standalone tests (two skips) and
335 isolated main tests (three skips), including fresh entity/metrics cutover;
R4/R5 subsequently pass their prerequisite regression gate; destructive writer
certification still requires independent runtime qualification. Milestone anchors:
PyUtil `7d2b7f8`, Analytics `739e64f`.
<!-- SYNTHESIS: proposed prerequisite ordering from wiki/work/dbt-compaction-coordination/implementation-review.md R1–R5 and live entity/CLI/DBT sources listed in frontmatter -->

The current combined CLI publishes entities, migrates/deletes raw, then publishes
checkpoints. Entity-enabled `reconcile-delete` now publishes checkpoints; entity-only
replay reports raw work `not_run` and can overwrite fixed-hour metrics. These are
three distinct recovery obligations, not one success flag.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/publish_metrics; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows -->

### Selected R4 contract — prerequisite regression accepted

Coordinated CLI invocations supply a stable CLI `--run-id`, the independent
`--coordinator-run-id` and a server-local `--run-evidence-directory`. The local run
archive is separate from all four data roots, fixed-hour coverage and the independent
authoritative ledger; it is not another S3 input/root. Manual compactor invocations
without the archive retain their existing behavior but cannot claim certified
coordinated migration from exit status alone.

Append immutable, checksummed phase records with predecessor identities. Record
the root/window/host/namespace/policy/event binding before writes, committed entity
generation after verification, per-event/protocol original file identities,
row counts and schemas before deletion, deletion intent/outcome, and original
checkpoint candidates before publication. Publish/flush each local record before
the next destructive phase. Never reuse a run identity to overwrite its history.
Skipped, mixed skipped/processed and uncertain raw outcomes are not certified
migration completion; verified empty event-hours may accompany migrations.

An explicit exclusive `checkpoints-repair --confirm-repair --repair-run-id ...`
must validate the original run archive/binding, every surviving output's identity,
schema and per-protocol row count, source absence (or unchanged retained source),
current entity integrity/authority and the original checkpoint's historical receipt.
Only then republish the original checkpoint candidates without rewriting original
migration evidence or fabricating a new bootstrap/generation. Missing evidence or
an early crash without a complete verified raw outcome remains blocked for explicit
reconciliation; the repair command does not reopen or recreate a coordinator ledger.
Conflicting coverage requires `--confirm-replace-checkpoints`; a new repair archive
retains the prior rows and original archive head. Limits are 64 MiB/record,
256 MiB/run and 10,000 records. Streamed byte rechecks, canonical JSON and file/new
directory-link fsync have active-path negative tests. Full standalone passes 307
tests (two skips); combined isolated main passes 343 (three skips). The main suite
started before the directory-link follow-up; the final affected cross-runtime run
passes 51 tests (one skip) including that repair. Actual endpoint/power-loss
recovery and accumulated-state I/O/RSS
budgets remain separate dcc-04/dcc-05 qualification, not prerequisite regression claims.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §RunEvidence/repair_checkpoints; wiki/work/dbt-compaction-coordination/verification.md -->

### R5 active-root routing — implemented

Offline `effective_input_roots` and DBT `active_input_roots` resolve active roots
before access setup. Disabled entity mode ignores metrics overrides; enabled mode
binds the override or sibling default. Seven real routing cases pass, including
direct full local `make dbt-build` with unused remote metrics and four active-remote
controls. Coordination-specific bypass/message assertions belong to dcc-03.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/check_dbt_config.py §effective_input_roots; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §active_input_roots; ../Wintap-PyUtil/tests/test_effective_input_roots.py -->

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

Current working-tree slice implements strict v1 messages and the locked DuckDB
ledger, with transaction-before-PUT/writer-intent, retained terminal/outbox records
and blocked restart. Added six protocol and six ledger hardening failures before
fixes. The final focus passes 54 tests, including actual process death around
COMMIT/WAL recovery; full isolated main passes 397 tests (three skips), accepting
the dcc-01 regression gate. That gate does not certify tick scheduling, the client,
writer completion/cursor advance or operator reopening.
Messages are capped at 1 MiB each; listings at 64 MiB, 10,000 messages and 10,000
pages, failing rather than truncating retained knowledge. Ledger DuckDB uses two
threads/128 MB memory, not a qualified RSS/capacity bound.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/protocol.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; wiki/work/dbt-compaction-coordination/verification.md -->

### 2. dcc-02 — Tick and scheduling

- Take the same nonblocking local process lock before every ledger open, including
  operator commands, and hold it through supervised writer completion.
- Process terminal messages first. Due work enters `DRAINING` before new admission;
  every outstanding reader reservation excludes the writer, delivered or not.
- Persist the oldest unfinished UTC hour; use ten-minute grace and one hour per
  tick. Keep backlog priority until caught up; never infer a cursor from object age.
- Test midnight/grace boundaries, missed ticks, empty hours, overlapping ticks,
  surviving children and failures around launch with controllable clocks.
- Implement the human-required allowlisted, non-secret effective execution receipt,
  durably bound to writer intent before launch. Prove actual command/configuration
  matching, default/override/environment resolution, bounded receipt integrity and
  secret exclusion with active-path red/green evidence. Missing/mismatched settings
  refuse launch; later uncertainty stays blocked. The current command manifest is
  not sufficient. See [[wiki/work/dbt-compaction-coordination/design#Required execution and configuration receipt]].

**Current slice:** controlled-clock `writer_due`/`tick` implements locked bounded
listings, atomic terminal-first ingestion, overlapping readers, oldest-hour due
draining, immutable grant retries and committed callback intent. Five behavioral
failures precede the atomic-ingestion/config/diagnostic repairs; two further
blocked-diagnostic failures precede strict reopen checks. Final focus passes
100 tests, including real abrupt tick death with a surviving synthetic child;
full isolated main passes 443 tests (three skips). All callback outcomes remain `BLOCKED`
without cursor advancement, including exit-zero empty/completed claims. This is
not full dcc-02 acceptance, a supervisor or real writer certification.

Remaining dcc-02 integration: service-level supervision/root binding, verified
completion/empty-hour evidence, transactional cursor/backlog advancement and
admission reopening, advisory status and production-clock wiring.
The callback's command/summary is not proof of actual execution or shutdown.
Do not check off dcc-02 until these gates pass; real-compactor verification remains
coupled to dcc-04's phase archive and authority high-water integration.
Linux-only isolated-subreaper supervision now handles detached/nested descendants,
interruptions, bounded logs/control/report parsing and failure cleanup. Nine active-
path hardening failures precede repairs; four absent-`clock=` baseline failures
precede evolving-clock refresh checks. Final combined focus passes **142 tests**
(44 tick, 34 supervisor, 41 ledger, 23 protocol); full main for this newer revision
passes **485 tests, 3 skipped**, separate from the earlier 443-pass result. These
library primitives are regression accepted, not full dcc-02. A killed supervisor with a
surviving workload still blocks, and a real supervised empty callback cannot certify
completion. Non-Linux clients, external services/cgroup containment and actual
compactor/resource/power-loss qualification remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; wiki/work/dbt-compaction-coordination/verification.md -->

**Collaborative review, November 14:** an active-path controlled-clock probe
confirms that ingestion crossing grace can still reserve a new reader using the
pre-ingestion observation. Capture a formal failing regression, refresh after
ingestion before admission, then record the pass without revoking existing
reservations. This is a confirmed writer-priority defect, not demonstrated
reader/writer overlap. The human also confirms that independent completion and
shutdown verification must precede one atomic completion-evidence/run/cursor/mode
COMMIT; due backlog stays `DRAINING`, otherwise `OPEN`, and queued grants follow
COMMIT. Review evidence is in [[wiki/work/dbt-compaction-coordination/verification]].
No code repair or success API was implemented by that review. The subsequent
slice A repairs R6 with formal red/green evidence. The later v3 local normal-success
API exists; service integration and dcc-02 stay unchecked.

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
  Integrate the required execution receipt with the real qualified CLI and
  completion verifier; do not rely on a callback's declared command or omit
  effective non-secret settings that can change the processing scope.
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

## Completion plan — November 14

### Readiness and human-selected qualification scope

There is enough specification to begin the remaining implementation, **not enough
evidence to accept dcc-02–05 today**. The live prototype has no success/cursor API,
client, service CLI or real-writer adapter at planning time. Slice A subsequently
addresses R6–R8 with 150 affected main and 215 affected standalone passes,
80 expected SQL-mutation failures and 387 full standalone passes (two skips).
Actual macOS execution remains unqualified. In particular,
ledger validation at planning time permitted only the single unresolved writer
record; the subsequent v3 extension now retains completed history.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate/begin_writer; ../Wintap-PyUtil/Makefile §DBT targets -->

The human selected the following scope during this planning review:

- **Linux coordinator/writer; Linux and macOS coordinated DBT readers.** Windows
  coordinated execution is outside this milestone. Local-only DBT remains direct.
- **Actual existing S3 endpoint, fresh isolated feature-owned fixtures.** Deletion
  is limited to fixtures created for this qualification. Confirm exact roots and
  access before any remote write; no production dataset mutation or cron install.
- **Initial qualification envelope: 32 GB RAM / 64 GB disk.** Prioritize completing
  the lifecycle and monitor actual use, then recommend lower operating limits.
  The example 2 GB DuckDB / 4 GB spill limits are not acceptance targets. Account
  for aggregate process-tree RSS and aggregate local disk use, not just individual
  DuckDB settings. Select engine limits with headroom inside the overall envelope.
- A lower recommendation is not qualified until a representative rerun succeeds
  at those limits. Do not prune evidence, ancestry or retained state to obtain a pass.

These are qualification choices, not installed defaults or implementation results.
<!-- SOURCE: Human planning decisions, conversation 2026-11-14. -->

### Dependency order and acceptance boundaries

Do not equate the numbered units with independent implementation silos. dcc-02's
real success path needs dcc-04's independently verified phase/authority evidence;
the client needs an early macOS supervision feasibility gate. Use the slices below
and retain the existing unit checkboxes until all their acceptance evidence exists.

| Slice | Work | Exit gate / unit contribution |
|---|---|---|
| A — Review repairs | R6 post-ingestion clock, R7 authority-independent SQL negatives, R8 portable observations/platform guards. | Recorded red/green behavior; disabling SQL validation breaks the new integrity tests; Linux durability/tree coverage is retained. |
| B — Execution contract and platform feasibility | Resolved non-secret execution receipts, pre-launch binding, explicit runtime/root/budget configuration; macOS reader supervision spike. | Active launch/completion mismatch and secret-exclusion tests; an achievable, tested macOS shutdown contract before broad client integration. |
| C — Completion foundation | Independent read-only phase verifier, authority high-water checks, retained run history and atomic completion transaction. | Synthetic and real local one-hour success/empty cases; crash/corruption/rollback negatives; no callback can certify itself. Supplies dcc-02 and dcc-04. |
| D — Service and client | Production UTC clock/CLI wiring and advisory status; Linux/macOS reader wrapper and Makefile routing. | Scheduling/backlog/crash tests and full client lifetime/local-bypass tests. Close dcc-02 only after slice C's real-writer verification gates pass. |
| E — Audited operations | Qualified isolated compactor adapter, explicit initialization/upgrade, reader recovery, blocked-hour reconciliation and exclusive entity maintenance. | No force-success path; original evidence retained and all phases verified before reopening. Close dcc-04 after recovery gates pass. |
| F — Actual-endpoint qualification | Overlapping readers, queued reader, sequential hours, failure/restart/repair and measured retained-state workload. | Linux/macOS results, actual S3 evidence, full regressions and resource/latency report. Close dcc-03/dcc-05 only with their required platform/runtime evidence. |

The module boundaries below are proposed implementation seams; they are not
existing APIs or a claim that a checksum constitutes execution attestation.
<!-- SYNTHESIS: existing design/handoff acceptance matrix, live prototype and November 14 review R6–R8. -->

### A. Repair the reviewed baseline first

1. Record a formal R6 failure using the original real `ingest_many` plus an evolving
   injected clock. Refresh after ingestion before admission. Test exact grace,
   midnight, existing reservations, delayed grant publication and broken clocks.
   Requests not reserved by the deadline remain queued; never revoke prior grants.
2. Keep the 80 end-to-end authority/freshness negatives. Add SQL-specific negatives
   through `validate_sql` and corrupt pre-publication candidates through active
   update paths. Mutation-disable the validator: these tests must fail. Cover the
   key/evidence/type/scalar classes, not only the two review controls.
3. Observe directory descriptors portably where possible; guard actual Linux-only
   tree/durability integration cases and add unsupported-supervisor refusal tests.
   A platform skip repairs test attribution, not macOS reader support.

Slice A evidence is recorded in
[[wiki/work/dbt-compaction-coordination/verification#Completion slice A — review repairs]].
The full main regression was launched before slice B test additions and subsequently
passes 493 tests (three skips); it does not cover the later execution implementation.

### B. Resolve and bind execution before launch

Create one immutable resolved invocation for the selected hour and independent
coordinator/CLI run IDs. Build a bounded allowlisted receipt covering actual
executable/runtime identity, arguments, working directory, active roots, resolved
non-secret endpoint/region, events, enabled entity settings, deletion options and
all processing/capture/timeout/storage budgets. Record inactive fields explicitly.
Resolve allowed environment/profile/default settings once and pass that resolved
scope explicitly; inherited settings must not change it later.

The live storage helper also resolves endpoint/region from environment and SDK
profile configuration. Receipt generation must capture that effective selection,
not merely an absent CLI override or profile label.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/storage.py §open_s3 -->

Durably create/fsync the receipt before the intent transaction; COMMIT its identity
with the selected invocation before launch. An orphan pre-intent receipt grants
no permission. Recheck exact receipt bytes, qualified runtime/configuration and
actual launch parameters before invocation and during completion. Any uncertainty
after intent stays blocked, even if launch apparently did not occur. Keep
credential delivery separate and ephemeral; never persist secrets or secret hashes.
Exercise synthetic-secret exclusion in receipt, intent and diagnostic/capture paths,
including configuration/launch failures. Do not authorize arbitrary secret-bearing
commands by reusing the qualified compactor adapter.

For macOS, first prove the supported DBT process lifetime and shutdown behavior
with a platform-specific backend. Test interruption, descendants, detached-child
attempts and wrapper death. Where shutdown cannot be established, retain the
reservation; do not equate a root exit or a process-group check with all children
stopped. If a safe supported backend cannot be qualified, stop and review rather
than silently dropping the human-selected platform. Actual macOS execution is
required; Linux emulation and guarded skips cannot close this gate.

**Local receipt/launch slice implemented:** bounded immutable preparation, strict
canonical regular-file reads, qualified standalone runtime/code identity, explicit
CLI/default/root/budget scope and receipt-bound writer intent. Frozen credentials
remain ephemeral; injected SDK resolution makes no endpoint requests. Eight formal
hardening failures precede repairs; the final combined focus passes 194 tests
(44 receipt/launch cases), including real empty and destructive synthetic local
runs. Every outcome still leaves the hour blocked without independent completion.
Full main receipt regression passes 537 tests (three skips); macOS, actual-S3 and
representative aggregate resource gates remain open. Commands and limits:
[[wiki/work/dbt-compaction-coordination/verification#Completion slice B — execution baseline]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/execution.py; ../Wintap-PyUtil/wintappy/coordination/writer.py; ../Wintap-PyUtil/tests/test_coordination_execution.py -->

**Reader feasibility checkpoint — human review required:** the investigated native
Mac candidates do not yet establish the required complete-shutdown contract. Pinned
Apple source rejects automatic kqueue descendant tracking; installed DBT uses a
spawn-context helper even for manifest/lock construction. Three bounded Linux
dependency controls and 34 existing Linux supervision tests pass, but neither is
actual-Mac backend evidence. **The subsequent human instruction is to finish Linux
and let the native Mac worker find a solution.** Continue Linux slices D–F without
waiting for that backend; native-Mac qualification remains separately pending.
No backend, runtime restriction, weaker release or eventual platform removal is
selected. Retain uncertain reservations. Options and source limits:
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]]. Commands/results:
[[wiki/work/dbt-compaction-coordination/verification#Reader-supervision feasibility checkpoint — human review required]].

**November 15 actual-Mac feasibility:** isolated submitted `123b9d3` investigation
confirms native kqueue `ENOTSUP` and sandbox fork/spawn `EPERM`. Prestarting Python's
helper enables a genuine fixed synthetic DBT build/test under restriction, but the
deprecated Apple/private CPython seams are not selected for production. No client
backend, closed lifetime tracking or interruption/wrapper-death/shutdown gate passes.
Review before wiring; preserve Linux supervision and direct local-only DBT.
[[wiki/work/dbt-compaction-coordination/verification#Independent submitted review and native-Mac feasibility — November 15]].

### C. Independent completion and transactional history

Use a separately invoked read-only verifier in the qualified standalone runtime,
under the same coordinator exclusion. It must load/check the immutable phase
archive and independently re-read relevant data, not trust report completion flags:

- Verify exact run/hour/root/event binding, archive chain/order and original
  migration/deletion evidence for every selected event/protocol. Recheck surviving
  byte identities, row counts, schemas and source absence. Empty hours require
  complete bounded source/destination discovery; skips/mixed/partial outcomes block.
- When entities are enabled, verify current SQL integrity and committed authority,
  original bootstraps, retained historical generation lineage and exact selected-hour
  checkpoint evidence. Historical hashes need not equal today's evolving aggregate.
- Enforce the ledger's independent entity-authority high-water ordinal/ID: the
  current committed chain must contain the previously retained exact generation,
  permit forward evolution and reject rollback or a fork. Establish an initial
  baseline only through explicit verified initialization/cutover, never arbitrary
  edited snapshots. Exclusive maintenance updates this evidence before reopening.
- Bind the verifier's evidence to the execution receipt and clean supervised
  shutdown. Missing, changed, oversized or inconsistent evidence cannot complete.

The existing `verify_migrations`/archive helpers can supply bounded checks but do
not themselves authorize ledger completion. Whole-ledger-plus-authority rollback
still requires independent retained operator evidence and external exclusion; a
high-water row in the same restored ledger cannot prove its own freshness.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §load_archive/verify_migrations; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py §Authority -->

Extend the ledger to retain immutable completed/blocked run history and bounded
completion evidence. Make verified evidence retention, run completion, high-water
update, exactly-one-hour cursor advance and backlog mode one transaction. Reobserve
UTC for mode/admission decisions: backlog remains `DRAINING`; otherwise `OPEN`.
Queued reservations/grant publication follow that COMMIT, never a parsed report.
An explicit compatible-ledger upgrade must preserve readers, outbox, tombstones,
run IDs and audits; unresolved old intents stay blocked and acquire no fabricated
completion receipt. Missing/corrupt state still refuses ordinary operation.

The current `execute_prepared` API deliberately blocks every outcome, including
clean local success. Preserve that conservative API while adding the normal
same-lock launch→fresh verification→completion transaction path. Only a clean live
intent belonging to that uninterrupted path may complete automatically. A prior
`BLOCKED` run or a restart-blocked intent must use explicit confirmed, audited
recovery; a fresh passing report does not erase its uncertain disposition. The
completion entrypoint must obtain its own fresh independent evidence, not accept
a caller-supplied verifier dictionary as permission. Keep queued-reader outbox
creation/publication after the completion transaction and reobserve UTC before
any admission.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/writer.py §execute_prepared; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_block_unresolved_writer; ../Wintap-PyUtil/wintappy/coordination/verification.py §verify_prepared -->
<!-- SYNTHESIS: continuation seam preserving the human-required uncertainty/recovery and atomic-completion contracts; implemented locally by the subsequent v3 normal-success prototype, service qualification remains open -->

Add crash hooks before/after intent and completion COMMIT, lost acknowledgments,
restart after external completion but before COMMIT, multiple sequential hours,
empty hours, verification crossing grace, corrupt evidence, complete authority
rollback with a retained ledger, and forward-lineage controls.

**Verifier foundation accepted:** separate read-only completion/data/authority
checks and main receipt/intent/shutdown authentication pass 259 standalone/204 main
focus tests after eight active-path repairs. Frozen full regressions pass **547 main,
three skips / 431 standalone, two skips**, before subsequent ledger integration.
Original historical checkpoint hashes are never compared to today's aggregate.

**Authority integration regression accepted:** ledger v2 adds
explicit confirmed compatible v1 upgrade and retained authority-check proofs/audits.
Verified initialization requires a reason, no prior baseline and zero readers;
ordinary checks use separately supervised, receipt/ledger/dataset-bound observations
against the retained exact generation. Entity admission and writer intent require
fresh same-locked-session verification. Reopen resets freshness, failed checks clear
it and successful intent consumes it, without revoking existing reservations.
Rollback/forks refuse; forward lineage passes. Main entity `verify_prepared` now
verifies a real local migration/checkpoint against the initialized anchor but changes
neither high-water nor permissions. Latest focus passes **236 main / 299 standalone**;
32 main authority cases include upgrade/COMMIT death, uncertainty, corruption/budgets,
rollback/fork and entity integration. Retained proofs are capped at 64 KiB/check and
10,000 checks, validated in 256-row batches without pruning. Full authority standalone
regression passes 439 tests (two skips); full main passes 579 tests (three skips).
Both notifications arrived before completion/history implementation begins; these
frozen-revision results do not cover that next work.

That ledger-v2 revision permitted only one unresolved writer record. The v3
retained-history/normal-completion prototype passes 46 repaired completion/upgrade
and 24 additional semantic/compatibility/paging/secret controls before the final
three budget/clock red/green controls. Ten active failures precede repairs. Full
standalone of the final revision passes 439 tests (two skips); combined main focus
passes 298 tests. Full main passes 641 tests (three skips) in 1055.19 s on the
unchanged revision. Both full notifications arrived before lifting the runtime/test
freeze; the prepared source/runtime-lock manifest still matches. Its same-lock
clean-live-intent path obtains fresh independent evidence
internally; standalone verifier success alone grants nothing. Upgrades preserve
readers, outbox, tombstones, ledger/run identities and audits; uncertain intents stay
blocked without fabricated execution/completion receipts. Whole-ledger-plus-authority
rollback remains an external retained-evidence/exclusion gate.
Retained origin/proof/run/audit/cursor integrity and the prior-completion clock floor
do not prove global clock or coherent restored-store freshness. Completion budgets
remain 128 KiB/proof and 10,000 runs, with no pruning. Real raw/entity crash tests
cover external success before COMMIT and before/after completion COMMIT; genuine
three-hour instrumented paging is not representative retained-state sizing.
Detailed red/green attribution and commands:
[[wiki/work/dbt-compaction-coordination/verification#Completion slice C — ledger-v2 authority integration]].
Initial v3 scope and incomplete-test attribution:
[[wiki/work/dbt-compaction-coordination/verification#Completion slice C — initial ledger-v3 history and atomic completion]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/wintappy/coordination/verification.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py -->

### D. Wire the service and complete reader lifetime

Wire explicit configuration/init/tick/status commands to the main runtime and an
evolving UTC clock. Hold the existing local lock through writer, verifier and
completion. Use the standalone runtime only for compactor/data verification;
it never opens the ledger. Publish bounded advisory status after authoritative
transitions; status errors or stale status never confer admission permission.

Implement the reader client with offline effective-root resolution first. Preserve
direct local `make dbt-build` and local source/test/docs execution without AWS,
compactor installation, entity bootstrap or coordination job state. Route every
active S3 raw/compacted/entity/metrics input through coordination, consistently
ignoring inactive metrics overrides.

Persist a stable request before PUT, validate the exact grant before reads, and
hold one reservation across preflight/build/tests and managed child shutdown.
Persist release/cancellation before PUT and retry identical bytes under the same
job identity. A canceled job never honors a delayed grant; an uncertain request
does not become a replacement job. Failed preflight, missing entity coverage,
DBT failure and interruption release only after shutdown is established; uncertain
shutdown retains ownership. Delivery failures retain the terminal retry record and
report the outstanding job plus DBT outcome. Keep the ten-second poll and immediate
release-upload behavior; do not add a release-acknowledgment wait.

### E. Operator recovery without manufacturing evidence

Linux slice-D service/client/advisory integration, clean-original-run recovery and
the narrow original-exit-2 checkpoint-publication repair are now implemented in an
uncommitted overlay. See
[[wiki/work/dbt-compaction-coordination/verification#Linux integration continuation — slices D/E, qualification pending]]
for active-path red/green attribution, real Linux lifecycle and local Makefile checks.
This does **not** complete slice E: broader partial/deletion disposition, verified
intentional retry and exclusive entity maintenance remain unfinished and fail closed.
The checkpoint path uses a durable maintenance receipt/intent before launch, keeps
the original writer blocked through repair, and requires independent repaired-phase
resolution with unchanged original failure evidence before atomic completion.
Pending maintenance needs audited cannot-resume abandonment; replacement confirmation
retains prior checkpoint rows. History is bounded without pruning. Full standalone
passes 460 tests/two skips with all 261 frozen identities unchanged. Combined main
finishes with 303 passes/one missing-cursor test-wrapper failure; only that wrapper
is repaired, preserving genuine three-hour paging and corruption-refusal assertions.
Its focused control passes; combined main passes 304 tests in 715.34 s on the new
261-identity paging-repair freeze. Complete report inspected after notification and
all identities still match. Full main passes 755 tests/three skips in 1156.34 s;
complete report inspected and all identities still match after notification. See
[[wiki/work/dbt-compaction-coordination/verification#Checkpoint maintenance — narrow repaired-phase path, regressions pending]].

Add locked, audited status/manual-reader-release/hour-resolution and exclusive
maintenance commands. Require an explicit reason and confirmation that the original
reader/writer cannot resume. Stopped processes alone cannot clear data uncertainty.
Use original recorded candidates/archives for reconciliation and checkpoint repair;
hold exclusion through independent verification and the ledger transaction.
Conflicting checkpoint replacement needs its existing explicit confirmation and
retains prior rows. Missing original evidence, partial deletion or unresolved entity
intent stays blocked. A safe intentional retry requires a verified reconciled
disposition, not a blanket `force` flag. Provide placeholder config/cron/runbooks,
but do not install scheduling or mutate an existing research dataset.

#### Next source slice: original-bound recovery and maintenance

Source review during the full-main freeze identifies three boundaries for the
next implementation pass, **not new runtime tests or implemented recovery**:

- Existing `reconcile_deletions()` compares surviving source/output row totals and,
  with evidence enabled, schemas. An absent source takes `already_deleted` without
  validating an original migration. It receives no original archive; do not wrap
  that API's exit zero as proof for a partly deleted original writer. Entity-enabled
  CLI reconciliation also calls `update_entities()` before raw reconciliation and
  derives new metrics afterward; it is not a deletion-only original-generation repair.
  <!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §reconcile_deletions; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py §validate_counts; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/publish_metrics -->
- Original `migration_intent` and `migration_verified` retain source inventories,
  hashes, partitions and output identities before deletion. A new disposition must
  authenticate those originals, reject changed/extra surviving inputs or outputs,
  and record actual new observations separately. Missing required original coverage
  stays blocked; never insert a successful terminal or deletion result into the old
  archive. Entity/checkpoint validation remains independently required.
  <!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §verify_migrations -->
- Ledger v3 currently ties an unresolved active ID to a compaction run and requires
  contiguous verified completion history from the immutable first hour. Intentional
  retry and general entity maintenance need a durable, audited representation that
  preserves the failed original and exact cursor without falsely calling it completed.
  A temporary lock or `DRAINING` alone is not restart-safe maintenance exclusion.
  Any schema change requires explicit compatible upgrade, not ordinary-open replacement.
  <!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate/_validate_completion_history/upgrade -->

After the full-main notification and frozen-identity check, first add active-path
red controls for real partial deletion, changed/extra survivors and outputs, missing
original records, failed/crashed disposition, retry around COMMIT, and entity
initialization/replay with outstanding readers. Then implement narrowly bound
operations with receipt/intent-before-launch, bounded retained history, independent
verification and atomic disposition; keep retry distinct from completion and entity
maintenance distinct from raw migration. No new ledger schema or permissive fallback
is selected by this source review.
<!-- SPECULATIVE: next recovery/maintenance implementation and test sequence; current missing-evidence and uncertain-state refusal remains unchanged -->

Read-only follow-up while deletion regressions remain frozen sharpens the next
controls; none has run yet:

| Planned control | Required boundary |
|---|---|
| Original failure followed by intentional retry | Preserve the original intent, actual failure/shutdown/archive and exact hour. A fresh independent reconciled-disposition check precedes a durable retry transition; no original completion proof or cursor increment is manufactured. |
| Retry interruption before/after disposition COMMIT and before launch | Retain one authoritative owner and the original failure. A lost acknowledgment cannot permit duplicate launch, reuse the old invocation, or reopen uncertain writes. |
| Missing/changed original evidence, partial output, deleted inputs or pending entities | Refuse unless a separately authenticated disposition establishes the exact supported state; confirmation alone, survivor equality and today's entity aggregate are insufficient. |
| Entity init/replay with granted readers or another unresolved owner | Refuse before mutation. Queue/drain through the same authority, then commit a receipt-bound durable exclusive intent before standalone launch; a temporary lock or `DRAINING` alone is insufficient. |
| Entity failure/crash and explicit recovery | Preserve the operation and block through restart. Existing deterministic pending-publication recovery is not permission to bypass the ledger or rebase bootstrap provenance; changed candidates/input remain refused. |
| Entity-only success and retained-history compatibility | Independently verify raw/compacted non-mutation, entity lineage/provenance and selected checkpoints before atomic disposition. Leave the raw hour cursor and original migration receipts unchanged; preserve all readers/outbox/tombstones/identities on any explicit compatible upgrade. |

Read-only implementation ordering, before new source work:

1. Close both frozen retry-preflight affected/full gates and retain that baseline.
2. Keep the original failed intent/archive/shutdown immutable. Ledger v3 cannot
   retain it as unresolved while starting a second compaction owner, and its
   completion history requires genuine verified completion for every cursor hour.
   Define an explicit compatible retry-disposition representation and upgrade with
   active pre/post-COMMIT crash and lost-ack controls; do not mark the failed original
   completed, increment its cursor, erase its block audit or temporarily reopen
   admission. A new invocation needs fresh run/CLI IDs and a separately committed
   receipt-bound intent for the exact original hour and execution scope.
3. Treat entity-only ownership as a distinct operation, not a forged `compact`
   receipt or synthetic raw-completion archive. Current execution receipts and
   public completion/authority requests admit only one-hour `compact` arguments.
   Any entity operation needs separately bounded receipts, independent input/
   non-mutation/authority/checkpoint evidence and restart-visible exclusive ownership;
   do not widen those existing public validators to accommodate it.
4. Qualify fresh genesis separately from replay/pending recovery. `init-authority`
   currently verifies existing committed snapshots; it does not initialize them.
   A pending publication may resume only against its unchanged recorded candidates,
   inputs/window and bootstrap starts. An entity success can update independently
   authenticated high-water evidence, never the raw hour cursor or historical
   checkpoint hashes against today's aggregate.

No schema version or implementation candidate is selected here, and no new
retry/entity test result is claimed. The frozen preflight itself still grants nothing.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate/_validate_completion_history/begin_writer; ../Wintap-PyUtil/wintappy/coordination/execution.py §validate_receipt/command_for; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py §_opened; ../Wintap-PyUtil/wintappy/coordination/service.py §main; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py §prepare -->
<!-- SPECULATIVE: next-slice ordering and compatible representation remain unimplemented -->

Current `maintenance.repair()` requires an already blocked original deletion writer;
it cannot be reused as general entity exclusion. `update_entities()` can re-prepare
a matching pending authority candidate, but `Authority.prepare()` rejects changed
candidate hashes, inputs, windows or bootstrap starts. The next integration must
keep those checks and record actual operation outcomes separately. Ledger v3 still
allows only one non-completed compaction owner; no new schema or retry capability
is selected by this review. Release the deletion freeze only after both runtimes'
full notifications, complete reports and identity checks.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/maintenance.py §repair; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py §check/prepare; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate -->
<!-- SPECULATIVE: planned next-slice controls, not executed tests or implemented permissions -->

### Strict Linux entity service successor

Select strict CLI integration of the existing init/replay and clean-original/immutable-ack
resolution libraries before pending-publication repair. Preserve v4 defaults and expose v5
only through confirmed `upgrade --target-version 5`. Optional `entity_writer` settings are
independent of raw `writer` settings; exact entity start/end hours remain bounded by existing
24-default/168-cap validation. Reject unrelated flags, missing scope/confirmation/reason and
non-Linux entity execution before loading configuration. Original typed recovery loads the
authenticated receipt and preserves original non-secret storage scope instead of preparing
another invocation. No transport, reader admission, raw cursor/history or public-validator
change; the same uninterrupted ledger lock covers library execution/recovery.
<!-- SPECULATIVE: selected service-only successor, not implemented/qualified at preparation -->

- [x] Freeze/review separate genuine service controls and inspect complete retained red.
  All 71 fail (135.78 s): unsupported configuration/missing parser choices and flags/
  absent original loader; both actual children stop at parser exit 2, not COMMIT exit 91.
  Complete lossless 3,052-line report/28-line sidecar/two diagnostics and all 307 identities
  reviewed unchanged. No semantic refusal or service crash boundary is qualified.
- [x] Implement only demonstrated missing dispatch/original-loader/configuration seams;
  review the complete source successor and preserve all prior controls/evidence.
  Complete 303-line two-file delta reviewed; separate 307-identity freeze changes only
  `service.py`/`recovery.py`, preserving all 305 other identities/controls/runtime locks.
  Scoped lint/format and unchanged 71-control collection pass; successor focus now passes.
- [x] Authenticate actual CLI/verifier/archive/ledger/crash/exclusion evidence and pass the
  successor focus. All 71 pass (251.19 s); 32 verifier groups/ten clean CLI captures/60 immutable
  archives, atomic original history/crash/reader boundaries and all 307 identities authenticate.
  Original damage, real restart clock, prepared-only retry receipt and both inspection-only
  failure reports/sources remain intact. No runtime/control repair or broader acceptance.
- [x] Run and independently review the unchanged service-affected Linux gate. The separate
  13-module scope passes 307 controls in 2,036.10 s; report/sidecar, 307 frozen identities,
  both actual crash-child diagnostics, all 5,982 fixture entries, 188 ledger dispositions and
  preserved green/red/forward evidence authenticate. Typed post-COMMIT completion is read via
  the supported history accessor; state is `DRAINING` with no raw-cursor advance. This closes
  only the service-affected gate, not broader integration or dcc-02–05.
  [[wiki/work/dbt-compaction-coordination/verification#Service-affected Linux result — 307-control affected gate closed]].
- [ ] Stage broader focused/affected/full integration gates in both runtimes, preserving
  accepted forward-history evidence rather than overwriting or rerunning that fixture.
- [ ] Qualify pending-publication repair/retry and missing-original migration/deletion
  coverage separately; service dispatch must not silently treat them as clean resolution.

### Original-bound pending-publication controls — source planning only

While the unchanged service-affected run remains frozen, read-only source review identifies
the next separate controls. `Authority.check(..., pending=True)` admits only each recorded
before/after host snapshot with the retained bootstrap start. `Authority.prepare()` reuses
a pending generation only when binding, bootstrap starts, candidate byte/semantic hashes,
window and process fingerprint match. This is standalone deterministic update behavior,
not coordinated permission, original completion or independent recovery qualification.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py §check/prepare; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

Current coordinated CLI archives append `entities_intent` with the operation before the
update; `entities_verified` and checkpoint phases appear only after that update succeeds.
A failure inside host publication therefore lacks the successful publication/checkpoint
records required by the existing exact completion grammar. The pending authority journal
does not itself carry coordinator/CLI run IDs. The next verifier must independently establish
the exact interrupted original's scope/input/predecessor/candidate binding; do not fabricate
missing success records or assume a matching caller-rehashed journal is sufficient.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/_run; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py §SCHEMA; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_operation_verifier.py §_grammar/_publication; ../Wintap-PyUtil/wintappy/coordination/entity_completion.py §_execution_artifacts -->

| Separate planned control | Required original-bound evidence and disposition |
|---|---|
| Genuine interrupted genesis and replay | Use two synthetic expected hosts and an actual supervised CLI publication failure after fresh post-COMMIT input verification. Retain actual receipt/intent/prelaunch/command/shutdown/error/archive and independently observe the pending journal plus mixed before/after snapshots; do not inject successful evidence. |
| Clean-resolution refusal | Invoke the existing loader/resolution against the actual blocked partial original; it must remain blocked with no new entity launch, completion, authority acknowledgment, cursor advancement or reader grant. |
| Matching candidate repair | Require a separate bounded receipt/intent committed under original typed exclusion before any new maintenance invocation. Bind exact original generation, input inventory, window, candidate bytes/semantics and bootstrap provenance; use new maintenance/CLI identities and a separate immutable archive. |
| Candidate/input/scope damage | Changed/extra/missing raw or compacted inputs, replacement snapshot, altered bootstrap/window/host set, changed authority predecessor or unrelated original must refuse before mutation. Rehashed caller dictionaries are not independent observations. |
| Missing/changed original artifacts | Missing receipt/intent/prelaunch/command/shutdown/error/archive or required candidate evidence remains missing and blocked; hard links/symlinks are inadmissible, never reconstructed or repaired by the test. |
| Actual repair COMMIT/launch process death | No-unwind children before/after maintenance intent and outcome COMMIT, and before/after actual launch, retain original ownership and all-or-none typed records. No restart relaunch; any explicit abandonment/retry must preserve prior attempts and original failures. |
| Lost acknowledgment and clock floor | Preserve committed evidence and restore/retain blocked exclusion after uncertainty. Recovery clocks meet the actual retained blocker floor before creating verifier/artifacts; no synthetic substitute for a real restart timestamp. |
| Repair success versus resolution | Independently verify unchanged raw/compacted data and exact repaired candidate/checkpoint scope. A repair result alone advances neither raw cursor nor admission; only a separately authenticated supported disposition may acknowledge repaired state. |
| Missing original migration/deletion coverage | Existing raw checkpoint/deletion recovery must continue refusing partial originals without original migration coverage; survivor equality or generic reconciliation cannot substitute for it. |
| Retained history and integration | Budgets precede payload/owner fetch; same-connection keyset pages, immutable links, exact caps and last-page corruption controls preserve all existing raw/entity history and reader identities. Stage separate main/standalone focused, affected and full gates afterward. |

This matrix is **not an implemented API, selected durable representation, frozen pending-
recovery scope or executed result**. First demonstrate eligible genuine original artifacts
and inspect a separate retained red before choosing narrowly supported repair semantics.
If the required original binding cannot be established, that original stays blocked; any
prospective evidence addition must be separate and cannot backfill historical fixtures.
Preserve existing successful entity archive grammar, v5 schema, public one-hour validators,
current-only clean resolution and all accepted forward-history originals unless an explicit
separately reviewed compatibility change is required. No runtime/control edits during the
active service-affected run, no remote qualification or production operation.
<!-- SPECULATIVE: planned genuine failure and repair controls; original eligibility and separate API/representation remain unqualified -->

### F. Qualification gates and remaining runtime inputs

#### Intentional-retry ownership slice — active, not accepted

The closed 269-identity read-only preflight baseline is retained and rechecked before
this slice. Selected implementation design: an explicit compatible ledger v4 adds a
bounded predecessor-linked `retry_dispositions` table; ordinary open never upgrades
v1/v2/v3. An original remains `BLOCKED` with its exact intent, block audit, actual
exit 2 and archive. Only a validated disposition links that failed original to one
fresh receipt-bound compaction intent for the same hour and unchanged effective
scope. The disposition and new owner commit atomically without an open interval,
cursor change or original completion proof. Genuine new-run completion alone may
advance the cursor. Every committed-but-uncertain retry remains blocked on restart;
neither an orphan receipt nor acknowledgment loss authorizes another launch.

First controls exercise genuine failed merges, original preservation, fresh IDs,
readers waiting through completion, actual pre/post-COMMIT and pre/post-launch
process crashes, lost acknowledgment, changed/missing original evidence and explicit
v3 compatibility. The first retained red run finishes with 11 failures in 28.20 s;
complete report inspected and all 269 accepted identities still match before source
changes. Initial v4/private-launch/retry implementation and scoped Ruff checks now
exist. First rerun retains six failures/five passes in 56.13 s; exact historical
CLI error-capture bytes repair the demonstrated reserialization defect. The first
extended run is interrupted, not accepted. Its fresh resumed run retains two
failures/11 passes in 83.33 s: post-COMMIT input arrival and same-schema/same-count
changed content at launch wrongly complete. Add fresh standalone verification after
COMMIT/before launch and exact original/new migration-intent identity checks shared
with audited resolution. No successor freeze/affected/full gate has begun. This is
not regression or Linux acceptance. Entity-only ownership remains separate.

- [x] Repair the two demonstrated late-input/original-identity defects; the 13
  active controls pass in 89.68 s, with the complete retained report inspected.
- [x] Inspect the extended 41-control report: four missing-service-dispatch failures/
  37 passes in 233.40 s; all 493 lines inspected, failed fixtures preserved.
- [x] Add explicit Linux `retry-hour` original-receipt dispatch under the same lock,
  requiring confirmation/reason and refusing unrelated flags; no transport/grants.
  Repaired 42-control run passes in 244.42 s, complete report inspected.
- [x] Extend compatible upgrade, retained history/corruption/budgets, reader/outbox/
  tombstone preservation and service controls; inspect complete red/green reports.
  First genuine history/exclusion run retains one unordered-row restoration failure/
  12 passes in 60.14 s; complete report inspected. Fix deterministic test comparison
  before a distinct rerun; history validation/corruption assertions stay unchanged.
  Corrected rerun passes 13 in 60.10 s; actual v3 upgrade crash/lost-ack controls pass
  three in 17.99 s; frozen-credential controls pass two in 24.88 s. Complete reports
  inspected. All 14 successor source/test targets reviewed; fresh lint/format passes.
- [x] Complete scoped review, freeze the successor and pass its own focused/affected/
  full gates; each full follows its own affected notification/report/identity check.
  Review and pre-freeze wiki/privacy/whitespace checks pass. Separate 275-identity
  successor freeze created/checked, preserving the accepted preflight manifest.
  Standalone focus passes 45 in 4.20 s; complete report inspected and all identities
  match after notification. Standalone affected passes 248 in 180.48 s; complete
  report inspected and all 275 identities match. Only then launched full standalone.
  Main focus passes 119 in 512.18 s; complete report inspected and all identities
  match. Only then launched main affected. Standalone full passes 554/two opt-in S3
  skips in 290.13 s; complete report inspected and all 275 identities match. Main
  affected passes 607/one isolated-local migration opt-in skip in 1843.36 s; complete
  report inspected and all 275 identities match. Only then launched full main, which
  passes 880/three opt-in skips in 2013.77 s; complete report inspected and all 275
  identities match. Combined intentional-retry local gate closed. Retain the freeze/
  reports; new entity-only source work needs separate active controls/regressions.
- [ ] Implement distinct entity-only ownership and qualification afterward; obtain
  approved isolated S3 inputs and representative resource evidence separately.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_intentional_retry.py; ../Wintap-PyUtil/wintappy/coordination/intentional_retry.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py -->

#### Entity-only ownership slice — active, not accepted

Preserve the accepted intentional-retry 275-identity freeze/reports and all historical
failures. First 22 lint/format-clean controls finish with 22 failures in 35.05 s;
all 749 report lines are inspected, failed fixtures retained and all accepted
identities rechecked unchanged. Missing entity execution, not a semantic refusal,
causes every failure; four child crashes do not reach their requested boundaries.
Standalone-verifier controls subsequently finish with 64 missing-module failures in
29.53 s, exit 1; all 2,972 retained report lines inspected, failed fixtures preserved
and all 275 accepted identities unchanged. No verifier refusal is accepted. Distinct
receipt first red retains 26 missing-module failures (0.51 s), all 523 lines inspected
and failed fixtures preserved. Separate bounded receipt implementation now passes
26 controls (6.16 s); complete report inspected, fresh Ruff lint/format passes and
all 275 accepted identities unchanged. Separate standalone verifier implementation
now passes its initial 64 controls (36.47 s); complete report inspected and all 275
accepted identities unchanged. Review identifies bounded-loader, original-hour,
early configuration and independent historical-publication evidence gaps. Corrected
review red retains 21 failures/two passes (6.94 s), including genuine accepted
historical-statistic corruption; complete report reviewed and all 275 identities match.
Verifier-only streaming SQL and observation/configuration repairs are unqualified;
combined repair and registration reruns each retain 12 failures/75 passes (35.57 s /
35.77 s), with complete reports and accepted-identity checks. Replaced the optional-
NumPy-dependent UDF with bounded one-record SQL staging; runtime lock unchanged.
Expanded qualification first run retains 35 failures/9 passes (20.71 s); complete
exact-deduplicated report and accepted identities reviewed. Repaired nonexistent
Inventory count reference; distinct three-module combined run passes 131 (91.07 s),
with complete report and accepted-identity checks. Ten expanded controls retain five
fixture failures/five passes (8.31 s); complete report/identities reviewed and fixtures
preserved. Fixture-only Unicode-selection/SQL-order corrections pass ten (8.49 s),
with complete report/identity checks. Fresh five-target Ruff lint/format passes;
separate expanded combined rerun passes 141 controls (97.91 s), with complete report
and accepted-identity checks. Expanded standalone verifier focus is closed; entity
ownership is still missing. Accepted source files, DBT and runtime locks unchanged.

Selected next design, not an implemented permission path:

- Distinct `entity_execution` receipts, `entity_writer` ownership/completion and a
  standalone entity-only verifier. Public one-hour completion/authority validators
  remain unchanged; entity CLI emits entity/checkpoint phases without `raw_complete`.
- Explicit compatible ledger v5 with separate entity runs/evidence and exactly one
  restart-visible raw/entity owner. Ordinary open never upgrades. Preserve v1–v4
  permissions, completions, retry dispositions, readers/outbox/tombstones and cursor.
  Keep existing default v4 initialization/upgrade unchanged; require explicit
  `target_version=5` for opt-in upgrade. Validate the original version before one
  transaction, preserving actual proof bytes and adding only typed entity history.
- Genesis requires fresh uninitialized authority/no retained anchor. Replay requires
  independently verified lineage containing the retained anchor. Both require zero
  readers/no unresolved owner. Never adopt unverified existing state as genesis.
- Independent bounded input/destination observations precede intent COMMIT; distinct
  post-COMMIT/pre-launch checks detect changes. Independent completion authenticates
  original phase archives, raw/compacted non-mutation, authority/provenance and
  original-generation checkpoints. Main reads bounded JSON; standalone owns data SQL.
  Historical checkpoint hashes are not compared with today's aggregate.
- Entity success atomically records separate completion and internally typed authority
  linkage, clears only its owner and recomputes backlog mode with a fresh clock. Never
  insert raw completion, change raw cursor, admit readers or call transport/grants.
- Failures/restart/lost acknowledgment stay blocked, never automatically relaunch.
  Clean-original audited resolution needs fresh independent evidence. Publication
  repair/retry needs separate unchanged original candidate/input/window/bootstrap
  evidence. Preserve ancestry/instance identities and `evidence_json`; refuse bounded
  history overflow instead of pruning.

- [x] Inspect complete first red report and recheck accepted identities.
- [x] Add genuine standalone verifier red controls before verifier implementation;
  inspect every failure and recheck accepted identities.
- [x] Inspect the separate receipt-control first red result before receipt implementation.
- [x] Implement distinct bounded receipts and pass the initial 26 focused controls;
  receipt preparation grants no launch permission.
- [x] Add separate standalone entity-only verifier and inspect its initial 64-control
  focused green; this does not establish qualification.
- [ ] Inspect genuine review controls and repair bounded SQL/exclusion processing,
  original-hour types, early configuration and historical-publication authentication.
  Corrected red, both failed repair reruns and expanded qualification first red
  reviewed. Combined 131 controls pass; ten expanded controls' fixture red and corrected
  green reviewed with accepted identities unchanged. Expanded 141-control rerun passes;
  main-side durable publication authentication remains unfinished.
- [x] Close expanded standalone verifier focused evidence: 141 passes (97.91 s),
  complete report reviewed and all 275 accepted identities unchanged. This is not
  ownership or successor-regression acceptance.
- [x] Qualify explicit opt-in v5 schema upgrade before adding entity launch permission.
  Seven new genuine-v4 controls retain seven unsupported-argument failures (35.10 s);
  all 295 report lines reviewed. Post-verifier ownership rerun retains 22 missing-module
  failures (44.08 s), all 960 report lines reviewed; no crash boundary executes.
  Both failed fixture directories preserved and all 275 accepted identities unchanged
  before implementation. Neither red result is a qualified refusal.
  Explicit schema staging now passes seven actual v4 crash/lost-ack controls (36.93 s)
  and 37 expanded compatibility controls (48.43 s); complete reports reviewed.
  The sole accepted-baseline source delta is `ledger.py`; other 274 identities match.
  The 43-control combined genuine-history focus passes (109.80 s), complete report
  reviewed and all 286 identities match after notification. Existing-ledger first
  compatibility retains two failures/149 passes (401.75 s), complete 271-line report
  reviewed and all identities match before repair. Actual COMMIT/lost-ack/row checks
  precede the repeat-upgrade diagnostic failures; later assertions did not execute.
  Restored only default-v4 wording, preserving tests/refusals and opt-in-v5 wording.
  Separate 286-identity repair freeze retained; repaired focus passes 46 (127.49 s),
  complete report/identities reviewed. Repaired compatibility passes 151 (399.51 s),
  complete five-line report reviewed and all 286 repair identities match. This closes
  schema compatibility only; successor focused/affected/full gates remain separate.
  New entity history stays fail-closed; failed fixtures remain preserved.
- [x] Implement explicit opt-in v5 schema staging while preserving default v4 behavior;
  review seven-/37-control focused greens. This is not typed ownership permission,
  durable publication or successor-regression acceptance.
- [ ] Implement separate bounded receipts/verifier and explicit compatible ownership,
  history, atomic completion/authority linkage; pass genuine focused controls.
  Extend main-runtime input authentication and add separately supervised completion
  observations, then typed ownership/history. Preserve the empty-history guard until
  original-bound validation can replace it; returned observations alone grant no launch.
- [x] Qualify main-side read-only entity input authentication before typed ownership.
  New 21-control first red retains missing-module failures (16.90 s), all 496 report
  lines reviewed and all 286 schema-repair identities unchanged before implementation.
  First adapter rerun retains one actual command-byte acceptance failure/20 passes
  (65.77 s), complete report/identities reviewed. Exact command/shutdown-byte repair
  and six added controls pass 27 (83.28 s); complete report reviewed and all 288
  artifact-repair identities match. The repaired artifact focus is closed, not broader
  input qualification. Extend exclusion, multi-hour, budgets and retained-contract
  controls before typed ownership. Failed fixtures and both snapshots preserved.
  Separate expanded qualification retains nine failures/22 passes (102.92 s), complete
  245-line report reviewed and all 289 identities match before repair. Eight mismatch
  controls expose missing hour/aggregate equality; clock refusal occurs after verifier
  launch. Repaired only the adapter, without changing controls; other 288 identities
  match. Combined rerun passes 58 (185.12 s); complete report reviewed and all 289
  contract-repair identities match. Input-authentication focus is closed; historical
  reds, failed fixtures and distinct snapshots remain preserved. No input-focus test remained active.
  Those results do not establish post-COMMIT ownership or durable publication support.
- [x] Add genuine explicit-v5 typed intent/restart-exclusion controls before ownership
  implementation; review the complete retained red and identity snapshot first.
  Separate first run retains 34 import-masked failures (47.41 s); complete 1,132-line
  report reviewed and all 290 identities match. Neither crash child reaches its boundary;
  six budget controls fail before setup. No typed owner or semantic refusal established.
- [x] Implement exclusion-only typed original intent/history and original-bound live
  post-COMMIT inputs; retain unsupported completion/publication/recovery refusals.
  Prototype source added after full first-red/identity review; distinct 34-control
  implementation run retains 33 upgrade-masked failures/one v4 pass (34.61 s), complete
  exact-deduplicated report/291 identities reviewed. No typed assertion/crash-child
  launch established in that run. Same-transaction keyset/budget-before-owner repair
  passes the unchanged 34 controls (125.03 s), complete report/291 identities reviewed.
  Expanded history passes 24; combined main passes 336 (884.70 s) and standalone 141
  (105.56 s), complete reports/all 292 identities reviewed. Exclusion-only focused item
  closed; this establishes no entity execution, affected/full or Linux acceptance.
- [x] Review repaired initial typed-intent focus: genuine COMMIT/restart/lost-ack,
  post-COMMIT input/exclusion and original corruption/budget controls pass 34 (125.03 s)
  on unchanged 291 identities; not launch/completion or affected/full acceptance.
- [x] Qualify separate staged-visibility/rollback, budget-before-fetch, real keyset/tail
  and rehashed-semantic history controls. New 24-control source fully reviewed and
  five-target Ruff lint/format passes; all prior 291 identities unchanged. First run
  passes 24 controls (79.82 s), complete report/all 292 identities reviewed. This is
  expanded history-focused evidence only, not combined/affected/full acceptance.
- [x] Pass separate combined typed/input/schema/receipt and original-ledger compatibility
  focus plus standalone entity-verifier focus. Standalone passes 141 (105.56 s),
  complete report/all 292 identities reviewed. Main passes 336 (884.70 s), complete
  seven-line report/all 292 identities reviewed. Both focuses closed, not affected/full.
- [x] Add genuine current-generation main completion-observation controls and review the
  retained red and unchanged prior identities before original-bound source work.
  Separate 44-control source reviewed and lint/format-clean; all 292 focused identities
  unchanged. First run retains 44 import-masked failures (342.12 s), complete lossless
  409-line review reconstructing all 1,783 report lines inspected; all 293 identities
  match. Failed fixtures retained; no adapter semantic refusal/green established.
  Source work began only after complete red/identity review.
- [x] Qualify initial read-only original-bound current-generation completion focus.
  No publication fallback, ownership/completion or authority transition. Complete new
  adapter reviewed and two-target lint/format passes; all 293 first-red identities
  unchanged. Separate 294-identity implementation freeze retains two helper failures /
  42 passes (470.91 s); complete 81-line report/all identities reviewed. Missing-prelaunch
  and precommit refusals are masked before adapter invocation. Fixture-only positional
  parameter repair is next; preserve source/assertions and rerun all 44 separately.
  Exact two-line helper-only repair reviewed and lint/format-clean; other 293 identities
  unchanged. All-44 fixture-repair rerun passes 44 (471.51 s); complete three-line report/
  all 294 identities reviewed. Both previously masked refusals now execute without launch/
  mutation. Initial focus closed, not expanded completion or affected/full qualification.
- [x] Extend completion artifact aliases/bytes, actual CLI/archive versus rehashed
  dictionaries, supervision/result identities, clocks/counts/budgets and non-mutation
  qualification; preserve current-generation-only and no-transition boundaries.
  Separate 67-control module fully reviewed and three-target lint/format-clean; all 294
  initial-focus identities unchanged. First run passes 67 (353.73 s), exit 0; complete
  three-line report/all 295 identities reviewed, hash unchanged. Expanded observation
  focus closed, not combined/affected/full or entity permission. Genuine invalid Parquet
  and competing-process checks remain isolated; contract dictionaries confer no authority.
- [x] Pass a distinct unchanged combined completion/input/typed/schema/receipt/original-
  ledger focus (447 controls) and standalone entity-verifier focus (141 controls).
  Freeze all 295 identities separately; retain runtime/controls until both notifications,
  complete report reviews and identity checks. Affected/full gates remain later work.
  Distinct byte-identical combined freeze created/checked; standalone passes 141 (110.49 s),
  complete four-line report/all 295 identities reviewed, hash unchanged. Main passes 447
  (1729.40 s), exit 0; complete nine-line report/all 295 identities reviewed, hash unchanged.
  Both focuses closed with no runtime/control changes; affected/full remain separate.
- [x] Add genuine original-generation publication-retention controls before source work;
  independently observed current completion must be retained under the same typed lock.
  No ownership/authority/raw-cursor/launch transition. Authenticate retained original core
  before any future historical verifier request; preserve the current-only adapter.
  Supervised launch/atomic completion-authority linkage, dispatch and audited original-clean
  resolution require separate controls/implementation afterward.
  Separate 46-control module fully reviewed, new-target lint/format and collection pass;
  collection is not execution. Distinct 296-identity first-red freeze adds only this module,
  retaining all 295 closed-focus identities. First red retains 46 import-masked failures
  (402.36 s), exit 1; complete 1,772-line report, both direct child diagnostics and all
  296 unchanged identities reviewed. Children exit 1 at import, not 87; no publication
  COMMIT boundary or semantic refusal executed. At first-red review no test remained active
  and no publication source, permissive history fallback or acceptance existed. Controls bind immutable
  original core/evidence/audit, fresh verification, no transitions, restart/real COMMIT/
  lost-ack, corruption/budgets and authenticated later historical requests.
- [x] Implement and qualify initial bounded immutable original-publication retention/accessor
  and same-transaction typed history after the reviewed first red. Obtain fresh current-only
  completion internally; preserve contracts, original-artifact rechecks, early budgets,
  exclusion/acknowledgment and no-transition boundaries. Retain failed fixtures/report;
  unchanged 46 controls require a distinct successor freeze and complete result review.
  Separate retention/accessor now implemented with bounded immutable envelope/core/audit,
  fresh current-only completion and same-connection typed-history authentication. No success
  permission/authority/cursor/acknowledgment transition; committed lost acknowledgment blocks
  the original while retaining evidence. Complete source and four-target lint/format reviewed;
  distinct 297-identity implementation freeze passes the unchanged 46 controls (629.02 s),
  exit 0; complete three-line report/all identities reviewed, hash unchanged. Only typed
  history and two ledger comments differ among prior identities; all controls/current-only
  adapters/standalone runtime unchanged. Initial focus closed, not expanded/combined/affected/
  full or entity permission. Successful fixtures cleaned; historical failures retained.
- [x] Qualify separate original-publication rehashed envelope/audit/SQL-byte budgets and
  real keyset-tail controls, plus separately retained actual crash-child diagnostics.
  Preserve all closed identities and the existing 46 controls; new tests need a distinct
  successor, complete source/wiki/privacy review and complete result/identity review.
  Separate 651-line/77-control module and 69-line diagnostic-retaining runner fully reviewed;
  six-target Ruff lint/format and 79-control collection pass (including two unchanged original
  crash controls). All 297 closed source identities/operator documents unchanged; distinct
  298-identity successor adds only the new test module and the runner is separately frozen.
  Actual UTF-8 SQL bytes/positive aggregate and count boundaries, staged same-connection
  keyset tails, rehashed contracts/canonical JSON/audits and persisted-corruption reopen are
  qualified by 79 passes (100.90 s), exit 0. Complete four-line report, 29-line sidecar,
  both actual 93-byte child diagnostics and all 298 identities/separate runner/operator
  baselines reviewed after notification. Both children exit 87 at the selected before/after
  publication COMMIT hooks; original exclusion/raw cursor and absent-before/retained-after
  publication assertions execute. All fixtures/historical failures retained; no source,
  control or runner repair. Expanded focus closed, not combined/affected/full or permission.
- [x] Pass distinct combined publication/completion/input/typed/schema/receipt/original-
  ledger focus (570 controls) and standalone entity-verifier focus (141 controls) after
  expanded publication closure, before further entity-writer source work. Preserve every
  prior closed identity and inspect complete reports/diagnostics/identities before acceptance.
  Expanded-green complete 429-line wiki/privacy successor review and fresh six-target lint/
  format, scoped audit/whitespace/operator/source checks pass. Distinct byte-identical
  298-identity combined freeze and separate runner freeze created/checked; unchanged
  570-main/141-standalone focuses use distinct reports/all fixtures retained. Complete
  312-line prepared wiki/privacy review and fresh scoped/whitespace/identity checks pass;
  Standalone passes 141 (109.28 s), exit 0; complete four-line report/21-line sidecar and
  all 298 source identities/separate runner/operator baselines reviewed, hash unchanged.
  Main passes 570 (2430.83 s), exit 0; complete ten-line report/45-line sidecar, both actual
  93-byte exit-87 publication diagnostics and all source/runner/operator identities reviewed
  after notification, hash unchanged. Both focuses complete/all fixtures retained; no test
  active or runtime/control/runner changes at review. Combined focused gate closed, not
  affected/full or entity permission. Review complete successor wiki/privacy/fresh checks
  before the separate writer slice and explicit-v5 red controls.
- [x] Prepare/review a separate explicit-v5 writer red before entity-writer source work.
  Local fixture wrapper and actual crash/lock diagnostics now preserve all 22 controls'
  assertions/parameterizations and shared default-v4 helpers. Two-target lint/format and
  collection pass; distinct 298-identity freeze changes only the writer-control module.
  Separate diagnostic-retaining runner reviewed/frozen; historical controls/failures retained.
  Complete 252-line prepared wiki/privacy review and fresh scoped/whitespace/identity checks
  pass. Red completes with 22 import-masked failures (45.76 s), exit 1; complete 1,010-line
  report/36-line sidecar/four actual exit-1 child diagnostics and all 298 source/runner/operator
  identities reviewed. No hook or lock child executed; no writer boundary accepted. Every
  fixture retained; runtime still absent. Complete active/result wiki/privacy/fresh-check
  review precedes runtime coding; frozen controls/runner and historical failures preserved.
- [x] Implement initial authenticated successful typed history and distinct completion evidence without
  overwriting original publication or relaxing original authority/cursor bindings.
  Selected typed-event records/authority references, no v5 schema/public-validator change.
  Separate 20-control module reviewed/lint/format-clean and collected; 299-identity first-red
  successor adds only that module. Preserve closed unresolved audit allowance; complete
  successor wiki/privacy/fresh checks and full red/identity review before runtime coding.
  Complete 282-line design/prepared wiki/privacy review and fresh scoped/whitespace checks
  pass. Separate red retains four failures/16 setup errors (3.52 s), exit 1, all import-masked;
  complete report/19-line sidecar/all 299 unchanged identities reviewed, fixtures retained.
  No successful history or recovery semantic acceptance follows from this red.
  Five-file runtime successor reviewed and formatted; eight-target lint/format pass,
  frozen 22+20 controls/runner unchanged. Duplicate-completed-receipt refusal and authority
  keyset-tail/SQL-size review repairs precede the first runtime run. Implementation remains
  unqualified; retained-completion acknowledgment resolution still explicitly refuses.
  Preserve original completion/publication and qualify clocks/uncertainty before closure.
  First frozen runtime run retains 40 passes/two failures (244.11 s), exit 1; full 245-line
  report/49-line sidecar/four exit-87 crash plus three exit-88 lock diagnostics and all 301
  identities reviewed. One fixture mixes real restart/old synthetic clocks; the other reaches
  missing immutable committed-ack resolution. Preserve both and prepare a distinct clock/control
  successor without relaxing refusal. No full writer/history gate is closed.
  Later frozen command-contract successor passes all 71 writer/history/resolution controls;
  complete evidence/identities reviewed. Initial focused history is closed, not expanded gates.
- [x] Preserve original history-control bytes and review a distinct clock/control successor.
  Scoped synthetic reopen clock/import formatting changes no assertions, parameterizations,
  helpers or other functions. Separate 407-line/29-control resolution module is reviewed;
  four-target lint/format and 49-control collection pass. Distinct 302-identity control-red
  freeze preserves all other 300 runtime-first identities. No runtime changes or green yet.
- [x] Inspect separate resolution-control red, then implement initial bounded immutable resolution
  records, early block-clock refusal and after-COMMIT uncertainty without overwriting originals.
  Red inspection is complete: 25 passes/nine failures/15 setup errors (343.58 s), exit 1;
  complete report/sidecar and all 302 source/runner/operator identities reviewed. Actual captures
  confirm late block-clock refusal follows successful verification. Original-clean recovery's
  after-COMMIT exception leaves DRAINING; retain the defect evidence and repair conservative
  exclusion. Scoped clock correction passes; artifact/budget semantics remain masked. No green.
  Later immutable runtime plus narrow command-contract control correction passes all 71;
  genuine early-clock/artifact/corruption/uncertainty assertions execute, with all identities fixed.
- [x] Review bounded immutable resolution and early block-clock/uncertainty runtime successor.
  Original runtime bytes retained; complete 343-line two-file delta/separate 450-line module
  reviewed. Eight-target lint/format and AST-preserving format checks pass. Distinct 303-identity
  freeze preserves the other 300 red identities and all controls/runner/operators/public/v5/
  standalone contracts. Source review is complete, not executed qualification or acceptance.
- [x] Pass distinct frozen 71-control writer/history/resolution run and inspect all evidence;
  recheck closed publication four-audit overflow before broader recovery/affected/full gates.
  Complete 470-line prepared wiki/privacy review/fresh checks pass; all 303 identities match.
  First run completes with 69 passes/two failures (516.86 s), exit 1. Full 67-line report/50-line
  sidecar/seven actual diagnostics and all 303 source/runner/operator identities reviewed.
  Original 42 controls pass; two new positives stop on a nonexistent verifier flag after
  successful resolution. Preserve runtime/failed evidence; correct only that test contract
  through a distinct reviewed successor, then rerun all 71 plus closed publication qualification.
  Later corrected frozen focus passes all 71 and unchanged publication follow-through passes
  all 123; complete retained evidence and source/runner/operator identities reviewed.
- [x] Preserve original resolution controls and review the command-contract-only correction.
  Original 407-line bytes retained; complete 31-line delta replaces only the nonexistent flag
  with exact standalone command/canonical request/manifest assertions. Text/AST restoration
  preserves everything else; eight-target lint/format and 71-control collection pass.
  Distinct 303-identity freeze changes only resolution controls; other 302 sources and
  runner/operators remain unchanged. No executed successor result or full 71-control green yet.
  Complete 248-line prepared-final wiki/privacy review and fresh checks pass; the distinct
  frozen all-71 command-contract rerun is active. No result/acceptance; sources/controls fixed.
  Publication affected scope is prepared: all 123 unchanged original/expanded controls collect;
  full control review and six-target lint/format pass. Execution waits for all-71 result review.
- [x] Pass the frozen all-71 writer/history/resolution focused gate and inspect full evidence.
  71 passes (521.59 s), exit 0; full three-line report/50-line sidecar/seven actual diagnostics
  and all 303 source/runner/operator identities reviewed. Previously unexecuted positive
  immutable-original/table/data/artifact/reopen assertions pass; runtime remains unchanged.
- [x] Pass the separate unchanged 123-control publication affected rerun, including exact
  unresolved four-audit overflow and both actual original publication COMMIT process deaths.
  Complete all-71 green/index wiki/privacy review and fresh checks acknowledged; renewed
  six-target lint/format pass. Distinct byte-identical 303-identity source freeze and separate
  unchanged runner freeze bind the prepared rerun. No execution/result yet or broader closure.
  Complete 233-line prepared wiki/privacy review and fresh checks pass; the frozen 123-control
  publication affected rerun is active. No result yet; runtime/controls/runner remain fixed.
  Result reviewed: 123 passes (708.64 s), exit 0; complete four-line report/29-line sidecar/two
  genuine exit-87 publication COMMIT diagnostics and all 303 source/runner/operator identities
  unchanged. Only this affected follow-through closes; expanded/integration gates stay open.
- [x] Implement and initially qualify supervised entity launch/atomic completion-authority linkage and original-bound
  clean resolution after the reviewed red; raw cursor/grants and conservative APIs unchanged.
  The all-71 focused gate closes this initial slice; expanded genuine completion-death,
  SQL-budget/keyset-tail/forward-evolution and strict service/affected/full gates remain open.
- [x] Prepare separate genuine completion-process-death controls with runtime unchanged.
  Complete 254-line publication-result wiki/privacy review/fresh checks precede the new
  345-line/12-control module. Genuine external-verification and before/after typed COMMIT
  deaths cover initialization/replay, original-clean recovery and immutable acknowledgment
  resolution; actual captures bind standalone/CLI/shutdown evidence and raw/reader separation.
  Formatting preserves AST; child parsing, six-target lint/format and 12-control collection pass.
  Distinct 304-identity freeze adds only this module, preserving all 303 prior sources and
  runner/operators. Prepared first run is not active or qualified.
- [x] Execute the frozen genuine completion-process-death controls and authenticate complete
  report/sidecar/actual-child/boundary-capture/all-source/runner/operator evidence after notification.
  Complete 316-line prepared wiki/privacy review/fresh checks pass; distinct frozen 12-control
  first run is active. No result or acceptance; runtime/controls/runner remain fixed.
  Result reviewed: 12 passes (283.57 s), exit 0; complete three-line report/68-line sidecar/all
  12 actual 181-byte exit-89 diagnostics and hash-bound captures authenticate. Independent
  read-only inspection validates 48 actual observation-artifact groups/72 CLI archive records;
  all 545 fixture files and 304 source/runner/operator identities unchanged. Eight fresh
  recoveries/four atomic committed results preserve raw/reader boundaries. Only this focus closes.
- [x] Prepare a separately reviewed/frozen completion/resolution SQL-budget/keyset-tail successor.
  Exact formatting/AST comparison of the initial 531-line draft passes; full review identifies
  only new-module fixture/guard defects before execution. Complete 98-line correction preserves
  all assertions/parameterizations and other helpers; drafts remain retained. Final 548-line/
  44-control source and eight-target lint/format/final collection pass. Distinct 305-identity
  freeze adds only the new module, preserving all 304 predecessors and runner/operators.
  Two genuine completions/resolutions/publications are planned, not executed; no runtime change.
- [x] Execute the frozen 44-control history run and inspect full report/sidecar/actual
  fixture/artifact/source/runner/operator evidence after notification; preserve any failures.
  Complete 480-line prepared/207-line active wiki/privacy reviews and fresh checks pass.
  All 44 pass (62.53 s), exit 0; full three-line report/19-line sidecar reviewed. Complete
  read-only inspection authenticates ten verifier groups/two CLI completions/twelve archives,
  all original/publication/completion/resolution/blocker links and raw/reader boundaries.
  Guessed table/count diagnostic failures remain retained; actual schema/14-event inspection
  passes without runtime/test/fixture changes. All 84 retained files/one symlink and 305
  source/runner/operator identities unchanged. Only this focus closes; no test active.
- [x] Prepare separate genuine raw-cursor/authority forward-history qualification.
  Complete closed-history result wiki/privacy/fresh checks precede the new module. Retained
  261-line unexecuted draft receives only demonstrated request-clock/anchor-shape corrections
  plus lint context consolidation; full 67-line correction/419-line source reviewed. Eight-
  target lint/format and corrected 23-control collection pass; wrong-interpreter collection
  diagnostic retained. Distinct 306-identity freeze adds only this module, preserving all 305
  predecessors/runner/operators/closed-history fixtures. No semantic execution or runtime change.
- [x] Execute the frozen 23-control forward-history run and authenticate complete retained
  report/sidecar/raw and entity verifier/CLI/archive/original/ledger/fixture/identity evidence.
  Complete 340-line prepared/210-line active wiki/privacy reviews and fresh checks passed.
  All 23 pass (87.45 s), exit 0; complete three-line report/19-line sidecar and independent
  read-only inspection authenticate 16 verifier groups/four CLI completions/34 archive records,
  immutable originals/blockers/predecessors, advanced raw cursor and generation four. Guessed
  final-DRAINING inspection failure/source retained; actual raw proof requires OPEN with one
  WAITING reader, no grants or live authority. Only diagnostic expectations corrected; complete
  12-line final inspection passes. All 150 retained files/one symlink and 306 source/runner/
  operator/predecessor-fixture identities unchanged. No active test; only this focus closes.
- [ ] Extend multi-hour/forward evolution, corruption/non-mutation, budgets/paging,
  service flags, compatible-upgrade, crash/lost-ack and original-bound recovery controls.
- [ ] Review source/wiki/privacy, freeze a separate successor and pass both runtimes'
  staged focused/affected/full gates before local entity acceptance.
- [ ] Qualify isolated S3/access and representative/reduced-budget resources separately.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_operations.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run; ../Wintap-PyUtil/wintappy/coordination/ledger.py §authority_high_water -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_completion.py; ../Wintap-PyUtil/tests/test_coordination_entity_completion_observations.py -->
<!-- SPECULATIVE: typed entity ownership/completion/publication and ledger-v5 successor regression gates remain unfinished -->

Retry source work has started after deletion's full-suite notifications and identity
checks. Retain the accepted deletion freeze/reports. Eighteen standalone and nine
main red controls reach missing preflight modules after genuine failed merges;
complete reports inspected. Added preflight modules grant no permission and change
no ledger schema/cursor. First standalone rerun has two fixture-scope failures and
16 scope-masked negatives: the shared fixture still enables deletion. Main's first
rerun likewise has one failure/eight masked passes and its retained receipt confirms
deletion enabled. Both fixtures are now corrected before original launch, without
relaxing runtime refusal. Corrected standalone rerun passes the 19 prior controls but
exposes two late-prefix acceptance defects; repair and rerun before qualification.
After source rechecks of hashes and both prefixes, the 45-test extended standalone
run passes in 4.34 s, exit 0, with complete report inspected. Corrected main's earlier
nine controls pass in 30.17 s. Extended main finishes with three failures/30 passes
in 112.87 s: consistently rehashed verifier captures wrongly accept changed source
rows/files/bytes. Complete report inspected and all 265 deletion identities still
match. Main now binds exact totals to bounded original intent JSON authenticated
through the captured blocked terminal; fresh reruns pass 33 main in 113.08 s and
45 standalone in 4.19 s, exit 0, with complete reports inspected after notifications.
No main data SQL, schema/permission transition or cursor mutation is added.
After both notifications, format-only cleanup and four-target Ruff lint/format pass.
Complete new-source/test/wiki-diff privacy review and scoped wiki/whitespace audits
pass. The separate 269-identity retry freeze adds only four files; all 265 deletion
identities remain unchanged. Frozen standalone focus passes 45 tests in 4.18 s;
main focus passes 33 tests in 112.95 s. Complete reports inspected and all identities
match after each notification. Affected standalone passes 248 tests in 179.13 s,
exit 0; complete report inspected and all 269 identities match after notification.
Full standalone passes 554 tests/two opt-in S3 skips in 287.54 s, exit 0; complete
report inspected and all 269 identities match after notification. Its affected/full
gates pass. Affected main passes 548 tests/one approval-gated isolated-local migration
skip in 1446.75 s, exit 0; complete report inspected and all 269 identities match after
notification. Full main passes 821 tests/three skips in 1602.08 s, exit 0, launched
only after those checks. Complete report inspected and all 269 identities unchanged
after notification; fresh four-target Ruff lint/format pass. The combined read-only
preflight local regression gate is closed, with no regression still running. Retain
the freeze/reports before new durable-retry/entity source work; every new slice needs
separate controls and regressions. This baseline supplies no retry permission.
Current evidence:
[[wiki/work/dbt-compaction-coordination/verification#Retry preflight — prerequisite only, integration pending]].
Durable retry's separate local regression gate is now closed above, not Linux
acceptance. Initial entity receipts/verifier controls pass, but verifier review and
ownership remain unfinished; no coordinated entity operation is qualified.

The active deletion-only continuation and retained red controls are recorded in
[[wiki/work/dbt-compaction-coordination/verification#Original-bound deletion recovery]].
It adds separate original-bound disposition, not generic reconciliation or intentional
retry. Initial seven-test main integration is not acceptance; demonstrated exact-type,
per-hour grammar, traversal, checkpoint-interference and captured-archive defects are
repaired. Corrected three-hour controls preserve public one-hour refusal; scoped
lint/format passes and the 265-identity deletion freeze is retained. Frozen
standalone focus passes 49 tests in 90.48 s, complete report inspected and all
identities unchanged after notification. Frozen main focus passes 33 tests in
348.84 s, with complete report inspected and all identities unchanged. Separate
affected standalone passes 203 tests in 177.37 s, exit 0; complete report inspected
and all 265 identities unchanged after notification. Full standalone passes 509
tests/two opt-in S3 skips in 274.88 s, exit 0; complete report inspected and all
265 identities unchanged after notification. Affected main passes 515 tests/one
explicit isolated-local migration skip in 1345.33 s, exit 0; complete report inspected
and all 265 identities unchanged after notification. Full main passes 788 tests/three
skips in 1492.66 s, exit 0; complete report inspected and all 265 identities unchanged
after notification. Deletion's combined local regression gate is closed. Retain the
freeze/reports and release source for the separate retry/entity-maintenance slice;
its new changes require their own controls and regressions.
Renewed 11-target source/test review and Ruff lint/format pass; complete changed-wiki
diff/privacy inspection and scoped nine-Markdown/seven-frontmatter audit pass, as
do both whitespace checks. Scoped review and local regressions do not qualify Linux. The broader
slice-E and dcc-02–05 checkboxes below remain unchanged.

Prepared stage/approval worksheet:
[[wiki/work/dbt-compaction-coordination/isolated-qualification]]. No environment,
fixture manifest or access is selected; no remote execution or deployment is authorized.
Before actual-endpoint runs, confirm a fresh exact test prefix, approved access via
existing credential configuration, fixture manifest, event scope, first UTC hour,
optional freshly initialized entity roots and a representative retained workload.
The human selects a human-run actual-Mac harness. The prepared offline baseline is
in [[wiki/work/dbt-compaction-coordination/macos-qualification]]. The original
`8ee714c` attempt was blocked before both test stages by the missing main lockfile;
preserve that result. Corrective commit `fab647f900196b0bc473fe7977b7dadcf7f4ce52`
tracks the exact original lock and checks committed/local bytes; all 22 identities
and 18 harness controls pass from a fresh Git-only clone. The separate actual-Mac
rerun now passes 169 main tests/129 reviewed Linux-only skips and 267 standalone
tests/zero skips; future reader-backend shutdown acceptance remains pending. See
[[wiki/work/dbt-compaction-coordination/verification#Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed]].
Never copy access secrets or actual host/account/IP identifiers into this wiki.

First run the combined lifecycle with synthetic local fixtures, then the approved
isolated S3 fixtures: two overlapping readers, due writer, queued third reader,
sequential hours and empty hour, deletion/checkpoint failure, restart and exclusive
repair. Record reservation and actual execution intervals; assert no reader/writer
overlap, no duplicate launch and queued admission only after completion COMMIT.
Run the complete main/standalone suites and platform-specific client gates; compare
DBT schemas/populations/conflict and ancestry semantics against the local baseline.

Run retained-state sizing stages inside the 32 GB RAM / 64 GB disk envelope, with
external aggregate RSS/disk monitoring and explicit time/fixture ceilings before
large runs. Include snapshot read/hash/rewrite, authority/ledger growth, spill,
logs/archives/copies, CPU/I/O and polling versus processing time. If the approved
envelope is insufficient, report the measured blocker and request revised limits;
do not silently exceed it or change semantics. Recommend a lower level only from
measured representative peaks with headroom, and distinguish a recommendation
from a passed reduced-limit rerun.

Crash/WAL/process-restart results are not physical power-loss, hostile-process,
external-service or network-filesystem containment certification. Record those
limits explicitly; any requirement for those additional guarantees needs a separate
qualified test/scope decision. Cleanup touches only fixture-manifest-owned data.
Promote durable implemented facts to canonical guidance, update diagrams and
record code/wiki commits. Production rollout remains a separate human gate.

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
  Ad-hoc queries/dashboards over raw-backed views must participate, except the
  human-approved same-server utility's explicit live diagnostic observation path.
  That exception does not weaken DBT, authoritative verification, ledger locking
  or exclusive maintenance/recovery. It cannot provide completion evidence or
  satisfy dcc-02–05 gates. See
  [[wiki/work/dbt-compaction-coordination/design#Diagnostic observation exception]]
  and [[wiki/work/compaction-status-utility/implementation_plan]].
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

November 14 maintainer review of PyUtil `fe7fcb5` confirms implemented R1–R5
repairs while adding test-isolation/platform follow-through. Prior checked gates
retain their worker-reported Linux scope. See
[[wiki/work/dbt-compaction-coordination/implementation-review]] R6–R8 and the fresh
macOS commands/results in [[wiki/work/dbt-compaction-coordination/verification]].

- [x] Pull manager documentation and inspect live implementation supporting R1–R5.
- [x] Prepare phased plan without implementing or deploying coordination.
- [x] Receive implementation authorization and record the four human acceptance gates.
- [x] R2: active-path red/green tests and bounded SQL integrity parity.
- [x] R3: changed/unchanged/replay/resumed-init provenance red/green tests.
- [x] R1: current-state freshness and historical forward-lineage red/green tests.
- [x] R4: independent phase evidence/repair and final-revision regression review.
- [x] R5: active-root routing and final-revision regression review.
- [x] dcc-00: integrity, provenance, freshness/phase-evidence and routing safety gates.
- [x] dcc-01: protocol/ledger with transaction and restart evidence.
- [x] R6: formal ingestion/grace-boundary regression and post-ingestion admission-clock repair.
- [x] R7: SQL-integrity negative tests fail when the SQL validator is disabled, independently of authority rejection.
- [x] R8: portable observations or explicit Linux guards for the five failing macOS cases; retain Linux coverage and non-Linux refusal checks (actual macOS rerun remains separate).
- [x] Completion slice B local launch: effective receipts, pre-intent binding, configuration/integrity/budget/secret-exclusion negatives and real synthetic CLI executions (194 combined passes).
- [x] Completion slice B/C: full-main receipt regression (537 passes, three skips) and separate completion-side receipt/identity/shutdown validation (204 main focus passes; no permission transition).
- [x] Completion slice C verifier foundation: read-only archive/data/current-authority/historical-checkpoint checks and recorded active-path repairs (259 standalone focus passes).
- [x] Completion slice C: full main/standalone regressions of the verifier-foundation revision (547 main, three skips / 431 standalone, two skips; before ledger integration).
- [x] Completion slice C authority focus: explicit compatible v1→v2 upgrade, verified initialization/freshness gates, retained-proof validation and entity verifier integration (236 main / 299 standalone focus passes; full regressions below).
- [x] Completion slice C: full main/standalone regressions of the ledger-v2 authority revision (579 main, three skips / 439 standalone, two skips; before completion/history work).
- [x] Completion slice C local history/normal-success hardening: ten active failures retained before repairs, 46 completion/upgrade and 24 independent controls pass before final three budget/clock red/green controls; not service/platform/endpoint acceptance.
- [x] Completion slice C: full standalone regression of the final budget/clock revision (439 passes, two skips).
- [x] Completion slice C: final combined main focus of the v3 completion revision (298 passes).
- [x] Completion slice C: complete tracked/new feature-source review, complete wiki-diff privacy review and fresh 18-file Ruff lint/format checks.
- [x] Completion slice C: full main regression of the frozen v3 completion revision (641 passes, three skips; unchanged source/runtime-lock identities confirmed).
- [x] Completion slice D initial Linux service/client integration: receipt-bound same-lock normal completion, post-COMMIT admission, durable request/grant/terminal state and advisory exports; local scope only.
- [x] Completion slice D Linux reader SIGINT/SIGTERM and retry-state hardening: real shutdown/lifetime plus missing/changed evidence, transport and persistent-inode controls (29 reader/lifecycle passes).
- [x] Completion slice D real local-only Makefile compatibility: seven routing cases pass; source preflight/build succeed with unused remote metrics and invalid inactive coordination settings, without client state.
- [x] Completion slice D/E scoped final source/wiki/privacy audit: complete tracked/new feature review, 30-file source/config/doc scope, 23-target fresh Ruff lint/format and nine-Markdown/seven-frontmatter grounding/link audit pass; infographic artifacts inspected and preserved, both whitespace checks pass. Not whole-wiki lint or regression/endpoint acceptance.
- [x] Completion slice D/E final combined affected-main regression of the reader/checkpoint overlay: 304 passes in 715.34 s; complete report inspected and all 261 paging-repair identities unchanged after notification. Earlier 303-pass/one-wrapper-failure evidence remains retained; no full-main/endpoint acceptance.
- [x] Completion slice D/E full main/standalone regressions of the reader/checkpoint overlay: main 755 passes/three skips (1156.34 s), standalone 460 passes/two skips (191.79 s); complete reports inspected and all 261 frozen identities unchanged after notifications. Before reader repairs: standalone 439/two skips; main 697/three skips/one startup failure; historical cause remains unproven. Subsequent source slices require their own regressions.
- [x] Completion slice E narrow checkpoint implementation and intermediate local controls: actual original exit-2 publication failure, separate receipt-bound repair, block-preserving abandonment and independently verified repaired completion (32 main / 66 standalone plus nine extended passes on intermediate revisions; latest hardening covered by the 304 affected/755 full-main and 460 standalone regressions).
- [x] Completion slice D/E paging-test compatibility repair: completed 303-pass/one-failure report and fixtures retained, original freeze unchanged, only independent-cursor delegation added to the test wrapper; real three-hour paging/corruption control passes (one pass, 26 deselected). Combined rerun/full main remain separate.
- [x] Completion slice E provisional original-bound deletion focus: 33 main / 49 standalone passes on the separate 265-identity freeze; complete reports inspected and identities unchanged after notifications. Original failures/archives retained; no deletion regression or dcc acceptance.
- [x] Completion slice E deletion scoped review: 11 runtime/test targets inspected completely, fresh Ruff lint/format, complete wiki diff/new-page privacy inspection, nine-Markdown/seven-frontmatter grounding/link audit and both whitespace checks pass. Other frozen identities and unrelated artifacts remain unchanged; not whole-wiki lint or regression acceptance.
- [x] Completion slice E deletion affected standalone regression: 203 passes in 177.37 s, exit 0; complete report inspected and all 265 frozen identities unchanged after notification. Full standalone launched on unchanged source; main and full-suite acceptance remain separate.
- [x] Completion slice E deletion full standalone regression: 509 passes/two opt-in S3 skips in 274.88 s, exit 0; complete report inspected and all 265 frozen identities unchanged after notification. Main regressions and Linux/endpoint acceptance remain separate.
- [x] Completion slice E deletion affected main regression: 515 passes/one explicit isolated-local migration skip in 1345.33 s, exit 0; complete report inspected and all 265 frozen identities unchanged after notification. Full main launched on unchanged source; no full-main or Linux acceptance.
- [x] Completion slice E deletion affected/full-main/standalone regressions: full main 788 passes/three skips in 1492.66 s, full standalone 509 passes/two opt-in S3 skips in 274.88 s, affected main 515 passes/one opt-in skip and affected standalone 203 passes; exit 0, complete reports inspected and all 265 identities unchanged after each notification. Local-only closure; preserve baseline and require separate evidence for new source changes.
- [x] Completion slice E read-only retry prerequisite hardening: 33 main/45 standalone controls pass after retained scope-masked, late-prefix and count-corruption failures. Original exit 2/block/cursor preserved; success grants no retry or completion permission.
- [x] Completion slice E retry scoped review/freeze: four new source/test files read completely, fresh Ruff lint/format and complete wiki-diff privacy/scoped audit/whitespace checks pass; separate 269-identity freeze adds only retry files and preserves all 265 deletion identities.
- [x] Completion slice E retry frozen focused controls: 33 main passes in 112.95 s and 45 standalone passes in 4.18 s, exit 0; complete reports inspected and all 269 identities unchanged after each notification. Affected/full gates remain separate.
- [x] Completion slice E retry standalone affected/full regressions: 248 affected passes in 179.13 s, 554 full passes/two opt-in isolated-S3 skips in 287.54 s, exit 0; complete reports inspected and all 269 identities unchanged after each notification. Full began only after its affected checks. Main/combined closure remains pending; source stays frozen.
- [x] Completion slice E retry affected main regression: 548 passes/one approval-gated isolated-local compactor/DBT migration skip in 1446.75 s, exit 0; complete report inspected and all 269 identities unchanged after notification. Full main launched only after those checks; no full-main, combined or Linux acceptance.
- [x] Completion slice E read-only retry frozen affected/full regressions: 548 affected main/one opt-in skip, 248 affected standalone, 821 full main/three skips (1602.08 s) and 554 full standalone/two opt-in S3 skips (287.54 s); exit 0, complete reports inspected and all 269 identities unchanged after each notification. Each full began only after its own affected checks. Combined local preflight closure only; retain baseline before new source work.
- [ ] Completion slice E broader audited partial/deletion disposition, verified intentional retry and exclusive entity maintenance; the narrow checkpoint path does not satisfy this gate.
- [ ] Completion slice B/D: Linux and macOS reader supervision and actual-platform qualification.
- [x] Independent submitted `123b9d3` review and portable Mac controls: 76/zero skips
  smoke, exact 307-test collection and provisioned five-module 169/25 Linux-only
  skips with 83 unchanged identities; not full latest-HEAD or native shutdown acceptance.
- [x] Actual-Mac restriction/bootstrap feasibility recorded with unchanged script/
  main-lock/manifest identities; genuine tiny DBT build/test passes, no backend selected.
- [ ] Native dependency/design selection and closed-lifetime interruption/detached-
  child/wrapper-death controls qualify complete shutdown before release.
- [x] Prepare gated isolated Linux/S3/retained-state procedure and approval worksheet;
  concrete environment/fixture/root/access/runner/ceiling selection and execution remain open.
- [x] Complete scoped tracked/untracked source/wiki/privacy review; separate cosmetic
  probe successor repeats genuine synthetic build/test with three unchanged identities.
  Original reports/sources remain retained; no native shutdown or broader gate closes.
- [x] Completion slice B/D source/dependency feasibility investigation: 34 Linux supervision tests and three bounded dependency controls; unresolved native-Mac contract recorded for human review, not backend/platform acceptance.
- [x] Completion slice B: human-run Mac harness selected and committed with public source manifest/15 local harness controls in PyUtil `8ee714c`; exact-revision task dcc-mac-baseline-01 defined (not actual-Mac execution or reader-shutdown acceptance).
- [x] Mac qualification packaging correction: exact original main lock tracked in PyUtil `fab647f`; all 22 committed/local identities verified from a fresh Git-only clone; three pre-fix coverage failures become 18 passing harness controls. Manifest/runtime hashes unchanged; original blocked Mac result retained.
- [x] dcc-mac-baseline-01: unchanged corrective PyUtil `fab647f` passes on an actual Mac with a new private report directory and separate locked runtimes: 169 main passed/129 reviewed Linux-only skips; 267 standalone passed/zero skipped; no timeout. See [[wiki/work/dbt-compaction-coordination/verification#Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed]]. Original `8ee714c` pre-test failure remains separate; reader shutdown is not qualified.
- [x] Maintainer reviews `8ee714c` and attempts actual-Mac locked provisioning; retains the original pre-test failure and R9 handoff finding without substituting dependencies.
- [x] R9 packaging repair: reviewed main lock and committed-blob guard pulled in `fab647f`; independent 22-file pre/post-run identities, both locked Mac runtimes and 18 harness controls pass. Corrected baseline passes; original failed attempt remains in [[wiki/work/dbt-compaction-coordination/verification#Maintainer completion review — Mac provisioning blocked]].
- [x] Completion slice C local library: independent verifier, entity high-water enforcement and atomic retained-history/cursor transaction, with red/green and full main/standalone evidence; not service/platform/endpoint acceptance.
- [ ] dcc-02: scheduling/exclusion with controlled-clock and child-failure evidence.
- [ ] dcc-03: DBT lifetime, terminal-message retry and local compatibility.
- [ ] dcc-04: qualified CLI integration and audited recovery operations.
- [ ] dcc-05: isolated runtime, incremental resource and regression qualification.
- [ ] Human rollout approval; production deployment recorded separately.
