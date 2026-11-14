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
policy: agent-editable
last_validated: 2026-11-14
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

### F. Qualification gates and remaining runtime inputs

Before actual-endpoint runs, confirm a fresh exact test prefix, approved access via
existing credential configuration, fixture manifest, event scope, first UTC hour,
optional freshly initialized entity roots and a representative retained workload.
The human selects a human-run actual-Mac harness. The prepared offline baseline is
in [[wiki/work/dbt-compaction-coordination/macos-qualification]]. The original
`8ee714c` attempt was blocked before both test stages by the missing main lockfile;
preserve that result. Corrective commit `fab647f900196b0bc473fe7977b7dadcf7f4ce52`
tracks the exact original lock and checks committed/local bytes; all 22 identities
and 18 harness controls pass from a fresh Git-only clone. The human's new-directory
Mac rerun and future reader-backend shutdown acceptance remain pending. Never copy access
secrets or actual host/account/IP identifiers into this wiki.

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
- [ ] Completion slice B/D: Linux and macOS reader supervision and actual-platform qualification.
- [x] Completion slice B: human-run Mac harness selected and committed with public source manifest/15 local harness controls in PyUtil `8ee714c`; exact-revision task dcc-mac-baseline-01 defined (not actual-Mac execution or reader-shutdown acceptance).
- [x] Mac qualification packaging correction: exact original main lock tracked in PyUtil `fab647f`; all 22 committed/local identities verified from a fresh Git-only clone; three pre-fix coverage failures become 18 passing harness controls. Manifest/runtime hashes unchanged; original blocked Mac result retained.
- [ ] dcc-mac-baseline-01: rerun corrective PyUtil `fab647f` on an actual Mac with a new report directory and separate locked runtimes; original `8ee714c` attempt was blocked before both stages. Retain sanitized pass/failure/skip evidence per [[wiki/work/dbt-compaction-coordination/macos-qualification]].
- [x] Completion slice C local library: independent verifier, entity high-water enforcement and atomic retained-history/cursor transaction, with red/green and full main/standalone evidence; not service/platform/endpoint acceptance.
- [ ] dcc-02: scheduling/exclusion with controlled-clock and child-failure evidence.
- [ ] dcc-03: DBT lifetime, terminal-message retry and local compatibility.
- [ ] dcc-04: qualified CLI integration and audited recovery operations.
- [ ] dcc-05: isolated runtime, incremental resource and regression qualification.
- [ ] Human rollout approval; production deployment recorded separately.
