---
title: "Runbook: Development Integration and Broader Qualification"
type: workflow
confidence: speculative
grounded_by:
  - wiki/work/dbt-compaction-coordination/integration-milestone-plan.md
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - ../Wintap-PyUtil/wintappy/coordination/LINUX.md
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_writer.py
  - ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_service.py
policy: human-review-required
last_validated: 2026-11-16
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap-PyUtil/wintappy/coordination; wiki/work/dbt-compaction-coordination
tags: [qualification, linux, s3, resources, coordination, runbook]
---

# Development integration and broader qualification

**Prepared procedure only; no environment or fixture is selected and no remote run
is authorized by this page.** PyUtil owns execution; Analytics owns this record.
Current development candidate is `badb67f`, not a production release.
<!-- REVIEW NEEDED: approve the concrete development runner, private data/root manifest, access, mutation scope and ceilings before execution. -->

**November 16 priority change:** the whole sensor/raw-data/ETL deployment is
developmental and existing telemetry is expendable. Begin the finite actual-data
Linux/Mac integration milestone in
[[wiki/work/dbt-compaction-coordination/integration-milestone-plan]], rather than
waiting for exhaustive recovery work or repeated unchanged full-suite gates.
Disposable data does not authorize an unspecified delete/reset. The concrete
selections below are still needed; production preservation is no longer the pilot's
objective. Broader qualification steps below are deferred, not pilot prerequisites.
<!-- SOURCE: Human planner-role direction and development-data clarification, conversation 2026-11-16. -->

## Development-run selection worksheet

Keep actual machine/account/IP values and secrets in the private operator manifest,
not this wiki. Persist only synthetic labels, aggregate results and manifest hashes.

| Required selection | Constraint |
|---|---|
| Linux coordinator/writer and Linux/Mac clients | Actual Linux supervision and native-Mac reader; select the development machines and separate locked main/standalone environments. Avoid disturbing an active worker's checkout or jobs; a new VM is not inherently required. |
| Exact source revision plus overlay identities | Hash source, controls, runner, manifests and both locks before/after; preserve submitted/historical evidence. |
| Private development root/data manifest | Select actual sensor data, hosts, event families and a small recent window; matching raw/compacted/entity/metrics and transport binding, separate local state/archive/temp/client/output roots. Fresh scope preferred; any reuse needs explicit selection and cannot bypass outstanding jobs or partial output. |
| Existing approved access configuration | Explicit endpoint/region/profile scope; credentials ephemeral and never retained in receipts/wiki. No implicit default production access. |
| Real-data provenance and mutation scope | Actual sensor/upload data, optionally replayed in a fresh scope first. Explicitly select which development prefixes may be created, compacted and deleted; retain only the small comparison oracle/diagnostics needed, not a mandatory whole-deployment backup. |
| Runtime/resource/timeout ceilings | Initial 32 GB RAM / 64 GB disk envelope, aggregate accounting; select wall-time, log/archive/fixture ceilings and stop margins before launch. |
| Development runner and stop control | Bounded actual service/client launch/capture, Linux descendant shutdown and accepted native-Mac process-group release; outer timeout/root exit alone is not a certificate. |

Re-read current source/verification before freezing. Reuse current unchanged green
regressions; run relevant controls if the candidate changes. Pending-publication
repair is unqualified and must not be improvised. Unsupported failures may instead
abort a disposable scope and start a separately approved fresh binding after old
processes cannot resume; never fabricate success or reset the old ledger to reopen.

## Development execution after scope approval

1. Verify exact candidate and separate locked runtimes; perform a short config/
   launch check. No unchanged full-suite rerun is required before the pilot.
2. Observe a fresh named workload through sensor/upload delivery; retain a bounded
   settled reference window and raw-only DBT baseline under correct exclusion.
3. Initialize a fresh entity-enabled ledger, explicitly upgrade to v5, and execute
   service `entities-init` with separate entity settings. Run actual hourly ticks
   through entity update, compaction, approved deletion, verification and COMMIT;
   bootstrap preserves the raw cursor and leaves `DRAINING` until catch-up.
4. Run Linux and actual-Mac Make/client DBT builds sequentially, then with overlapping
   reader reservations, a due writer and a third queued reader. Compare covered
   data and local outputs; observe actual request/grant/release and shutdown.
5. Continue fresh uploads and sequential hours, observe a natural UTC eligibility
   boundary and ordinary between-operation restart. Record observed coverage,
   duplicate/loss symptoms and real resource/latency use; strict upload-time UTC
   client enforcement and broader delayed-data work are separate later tasks,
   not pilot prerequisites. Do not assume that future contract is deployed today.
6. Fix demonstrated blockers narrowly. Once stable, freeze/reconcile final
   affected/full platform regressions and request DCC-E2E-01 acceptance with a
   ranked backlog. Comprehensive recovery and all-history capacity remain separate.

## Deferred broader qualification — not prerequisites to the pilot

The earlier comprehensive sequence is retained as a follow-on matrix. Its full-
suite-first and every-recovery-before-data ordering is superseded by the development
steps above. Source-copy preservation below describes those optional test oracles,
not a claim that existing development telemetry has production retention value.

1. **Provision and collect, without data access.** Use
   `uv sync --locked --offline --dev --python 3.12` separately in main and standalone
   directories. If artifacts are unavailable, record the refusal; approve an online
   locked retry separately.
   Confirm main DuckDB 1.5.6 versus standalone 2.0.0, unmodified locks and exact
   scope collection. No generated lock or skipped required Linux control is acceptance.
2. **Synthetic Linux regression first.** Run the frozen affected scope, then each
   runtime's full suite through the retained runner. Inspect all stdout/stderr,
   skip reasons, actual crash diagnostics, artifacts and ledger/history dispositions;
   check identities after completion. Retain red evidence before any distinct repair.
   Historical 880/554 and focused/affected 71/307 results are not substitutes.
3. **Isolated lifecycle.** Two overlapping qualified readers, a due writer and a
   queued third reader; include sequential/empty hours and grace crossing. Capture
   reservations, actual launch/shutdown and completion COMMIT ordering. No coordinated
   reader/writer overlap, duplicate launch or grant before committed completion.
   Repeat signal, detached-child and wrapper-death controls with reservations retained
   on uncertainty. Live diagnostic reads are separately labelled and not reservations.
4. **Approved S3 fixtures only.** Repeat lifecycle against the approved endpoint and
   manifest-owned prefixes. Verify output schemas/row populations and unchanged original
   inputs independently; grant delivery and status are not data verification. Compare
   local/direct DBT semantics with qualified coordinated results, including entities
   disabled/enabled and retained raw/compacted overlap. No production scheduler or cron.
5. **Audited recovery controls.** Preserve actual failed originals for checkpoint/
   deletion repair and raw-only retry. Repair leaves the original blocked until its
   distinct independent resolution. Explicit-v5 init/replay/clean-original resolution
   preserves raw cursor and `DRAINING`; exercise genuine pre/post-COMMIT death and
   lost acknowledgment. Missing originals/partial publication refuse; journal candidates
   never manufacture historical success. Do not invoke a pending-publication repair
   that has not received its own implementation and qualification gate.
6. **Retained-state resources.** Increment approved cardinality/history stages within
   the envelope; measure aggregate descendant RSS, spill/temp, databases/WAL, authority,
   snapshots, archives/logs and fixture copies, plus CPU/I/O and phase/wait durations.
   Include entity read/hash/rewrite and bounded history paging. Stop before approved
   limits using qualified shutdown; report the blocker rather than raise budgets or
   prune evidence. Tiny/crash fixtures cannot qualify representative accumulated state.

These steps are a proposed procedure grounded in the existing contracts, not new
executed evidence or newly selected acceptance thresholds.
<!-- SYNTHESIS: wiki/work/dbt-compaction-coordination/implementation_plan.md §F. Qualification gates and remaining runtime inputs; ../Wintap-PyUtil/wintappy/coordination/LINUX.md; ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py; ../Wintap-PyUtil/tests/test_coordination_entity_service.py -->

## Result and cleanup gates

Record each stage's command/scope, runtime/source/runner identities, complete report
hashes, aggregate measurements, actual disposition checks and skips/refusals in
[[wiki/work/dbt-compaction-coordination/verification]]. Complete native-Mac descendant containment,
physical power loss, external delegation and whole-ledger/store rollback remain
separate, unqualified guarantees. Reduced-budget recommendations need headroom and
a separate measured reduced-limit rerun before acceptance.

Retain the bounded failure/comparison evidence needed to diagnose the development
run; there is no whole-deployment preservation requirement. Cleanup still requires
explicit approval and exact scope; never broad-prefix deletion or resetting blocked
ownership to obtain a pass. The human approved the plan and this repository's wiki
commit/push for handoff only; source publication, persistent scheduling and production
rollout are not authorized by this runbook. DCC-E2E-01 acceptance, broader dcc-02–05
gates and later production readiness remain distinct.
<!-- SOURCE: Human plan approval, deferred strict UTC upload-client contract and handoff publication request, conversation 2026-11-16. -->
