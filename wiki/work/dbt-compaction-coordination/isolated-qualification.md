---
title: "Runbook: Isolated Linux, S3 and Resource Qualification"
type: workflow
confidence: speculative
grounded_by:
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - ../Wintap-PyUtil/wintappy/coordination/LINUX.md
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_writer.py
  - ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_service.py
policy: human-review-required
last_validated: 2026-11-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap-PyUtil/wintappy/coordination; wiki/work/dbt-compaction-coordination
tags: [qualification, linux, s3, resources, coordination, runbook]
---

# Isolated Linux, S3 and resource qualification

**Prepared procedure only; no environment or fixture is selected and no remote run
is authorized by this page.** PyUtil owns execution; Analytics owns this record.
Submitted `123b9d3` is the reviewed producer baseline, not a production release.
<!-- REVIEW NEEDED: approve the concrete environment, private fixture/root manifest, access, harness and ceilings before execution. -->

## Approval worksheet — all unset until confirmed

Keep actual machine/account/IP values and secrets in the private operator manifest,
not this wiki. Persist only synthetic labels, aggregate results and manifest hashes.

| Required selection | Constraint |
|---|---|
| Disposable Linux execution environment | Actual Linux supervision; isolated checkout and separate locked main/standalone environments, never the busy worker's checkout. |
| Exact source revision plus overlay identities | Hash source, controls, runner, manifests and both locks before/after; preserve submitted/historical evidence. |
| Private root/fixture manifest | Fresh disjoint raw, compacted, optional entity/metrics, transport and local state/archive/temp/output roots; no production aliases or existing ledger. |
| Existing approved access configuration | Explicit endpoint/region/profile scope; credentials ephemeral and never retained in receipts/wiki. No implicit default production access. |
| Fixture provenance and mutation scope | Generated fixtures or expressly approved copied data; originals remain read-only/hash-verified. Confirm creation, deletion and later cleanup separately. |
| Runtime/resource/timeout ceilings | Initial 32 GB RAM / 64 GB disk envelope, aggregate accounting; select wall-time, log/archive/fixture ceilings and stop margins before launch. |
| Qualified retained runner and stop control | Bounded capture and complete Linux descendant shutdown; outer timeout/root exit alone is not a certificate. |

Re-read the current worker source and verification before freezing. Pending-publication
repair is not in the reviewed baseline and must not be improvised during this run.
Ordinary local-only `make dbt-build`, default v4 and explicit v5 remain separate controls.

## Staged execution after approval

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
[[wiki/work/dbt-compaction-coordination/verification]]. Native-Mac complete shutdown,
physical power loss, external delegation and whole-ledger/store rollback remain
separate, unqualified guarantees. Reduced-budget recommendations need headroom and
a separate measured reduced-limit rerun before acceptance.

Preserve failed fixtures and all original evidence. Cleanup requires explicit approval
and the exact fixture manifest; never broad-prefix deletion or ledger reset. No commit,
push, deployment or rollout is authorized. Human acceptance of each dcc-02–05 gate
and any later rollout remains separate from successful qualification commands.
