---
title: "Milestone handoff: durable process entities and week compaction"
type: concept
confidence: medium
grounded_by:
  - wiki/work/durable-process-entity-manager/verification.md
  - wiki/work/durable-process-entity-manager/implementation_plan.md
  - wiki/tool/durable-process-entity-manager.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: reviewed
source_paths: wiki/work/durable-process-entity-manager; ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt
tags: [feature-work, handoff, milestone, entity-state, compaction, dbt]
---

# Milestone summary

**First-round implementation is complete; this is an intermediate handoff, not
production readiness.** The human accepts the three failed-hour compacted outputs
as correct for this milestone based on their exact comparison with retained local
input evidence. The deletion-verification failures remain failures with unknown
historical cause. Wintap-PyUtil owns the implementation; Analytics owns this wiki
and evidence. The human authorized committing and pushing this Analytics handoff;
that does not authorize a PyUtil code change/push, qualification-data mutation,
DBT run, or production cutover.

Implementation milestone: Wintap-PyUtil **`2cfbad1`**, branch
`work/raw-sensor-compacted-union` (25 files). This handoff, canonical pages and
qualification record are committed separately on Analytics
`work/raw-sensor-file-aggregation`. The Analytics wiki/evidence changes are
committed and pushed independently; this handoff is for continuation from an
on-prem development host. The PyUtil implementation commit is not included in
that wiki push; verify its availability from the on-prem checkout before any code
work, and arrange a separate authorized transfer/push if it is not available.

## Complete

- Optional fixed per-host S3 Parquet snapshots, explicit init/replay/verify/new-root
  rebuild, deterministic evidence/conflict retention, no initial TTL/GC.
- Entity publication and full GET verification before raw compaction/deletion;
  process inventories bound across phases. Single writer; external DBT exclusion.
- Opt-in DBT entity/context/ancestor lookup and terminal QA without injecting
  history into raw observations or inflating window counters/summary populations.
  Main DuckDB 1.5.6 and standalone writer 2.0.0 remain isolated.
- Regression evidence: standalone **132 passed/2 skipped**, main **310 passed/3
  skipped**; synthetic actual-endpoint **58 models/145 gates**, 33 root-reached
  seeds/33 summaries. These are separate from actual historical data.
- Earlier actual November 11/hour 08 migration: raw/mixed/compacted DBT each
  **58 models/145 gates**, counters/populations preserved; independent persisted
  entity-scalar multiset and ancestry-verdict checks pass. Hour-only context does
  not establish historical completeness.
- Week test executed all 168 hours: **165 successful raw compactions**, three
  deletion-verification failures retained. Successful hours: **53,415 → 1,650
  files (96.91% fewer)**; **4,841,533,292 → 4,623,379,532 bytes (4.51% smaller)**;
  **360,027,830 rows count-preserved**, 6.58 hours successful-command time.
- All **71,155 original hashes unchanged**. Daily/event/runtime metrics and
  separate entity/partial-output/source-copy accounting recorded in verification.
- Read-only reconciliation found all **25 partial compacted objects** from failed
  hours match their immutable input rows exactly; all **142 remaining raw objects**
  match their immutable copies. The failed-hour source prefixes were empty later.
- Synthetic Garage deletion diagnostic: 72/24/35-object baseline cases all
  deleted and immediately listed empty; output rows matched exactly. A controlled
  post-delete marker reproduced the exact failure message. This demonstrates one
  possible mechanism, not the historical cause. All synthetic test prefixes were
  cleaned and independently listed empty. Details and optional server-debug
  follow-up are in [[wiki/work/durable-process-entity-manager/verification]].

## Next, in order

1. **Compare the on-prem and laptop/VPN paths.** On-prem checkout and approved
   Garage access are established. The bounded read-only synthetic fixture check
   passed on-prem in 2.18 seconds (pytest-reported duration), covering 24 source
   objects / 17,544 bytes and one compacted object / 970 bytes, with 24 rows and
   zero row delta. This duration includes process/test overhead, not just network
   time. Run the same fixture check from the laptop for a comparable measurement;
   the historical seven-day aggregate is not an apples-to-apples baseline. Do not
   run DBT, repeat production deletion, or mutate preserved qualification data
   without new explicit authorization.
2. **Keep the Garage root-cause test as optional follow-up.** The baseline passed
   and injected-arrival case reproduced the failure signature, but the cause of
   the historical failures remains unknown. If needed, coordinate Garage debug
   logging on every node and rerun the documented synthetic test with client and
   server timestamps. Do not interpret a successful baseline as proof that the
   historical failure was a race.
3. **Resolve unknown-identity handling explicitly.** Historical bootstrap fails
   before publication; week entity maintenance stops at November 5/hour 01 after
   one combined hour. Negative-PID Refresh and sentinel-key positive-PID Stop
   evidence exists. Decide an evidence-preserving contract and tests; do not
   silently filter, invent identities/ancestors or repair by PID alone. The
   retained 33,824-entity/nine-snapshot state is stale and week-limited.
4. **Qualify historical scale after identity policy.** Expanded source counts
   exceed the default one-million-row per-host limit on two hosts. Bootstrap
   failed identity validation, not a demonstrated capacity failure.
   Measure actual staging/decoded evidence/full-snapshot rewrite costs; obtain
   approval for budget changes or sharding rather than silently pruning history.
5. **Complete original audit-window DBT enrichment qualification.** Bootstrap a
   verified historical state, hold the original seed population fixed, compare
   parents/root/gap/conflict verdicts independently, and distinguish larger source
   coverage and recorded-root policy from genuine enrichment improvements.
6. **Consider PIDstat layout tuning separately.** Week PIDstat expands 467.563 →
   1,395.968 MB; other families save 26.21%. Larger-row-group local candidates are
   promising, but shipping settings and S3 outputs were not changed. Qualify
   payload/NULL/duplicate/schema preservation and representative resource/performance
   behavior before accepting a new default.
7. **Only then review production operation.** Explicit roots/hosts/namespace/root
   PID policy, complete bootstrap, one writer, external DBT-reader exclusion,
   missed-hour catch-up and manual failure recovery need operator acceptance.

## On-prem continuation prompt

    Continue the durable-process/compaction work from the on-prem development host.
    Read AGENTS.md, this handoff, and
    wiki/work/durable-process-entity-manager/verification.md.
    First establish the checked-out branches/commits and verify the configured
    Garage endpoint with read-only checks. Measure the on-prem versus laptop/VPN
    performance path on a bounded read-only or synthetic workload; record commands,
    durations, bytes and object counts. Do not run DBT, delete production data,
    or mutate the preserved qualification copy without explicit approval.
    The three compacted failed-hour outputs are accepted as correct for this
    milestone based on exact comparison with preserved local inputs; the deletion
    cause remains unknown. Treat the Garage debug-log reproduction as optional
    follow-up, not as a prerequisite for this handoff.

## Evidence and retained test locations

- [[wiki/work/durable-process-entity-manager/verification]] — detailed commands,
  counts, comparisons, failure diagnosis and storage accounting.
- [[wiki/work/durable-process-entity-manager/implementation_plan]] — remaining gates.
- [[wiki/tool/durable-process-entity-manager]] — implemented contract.
- Actual test root:
  `s3://lintap-alpha/entity-tests/dpe-actual-week-20261112-8f52baa9-5d38-41f1-89a2-79043b50e4bd/`.
  Week raw outputs: `compacted/`; stale entity state:
  `week-limited-process-entities/`; separate earlier hour: `earlier-hour/`.
- Detailed reports, generated inputs and scripts from qualification/diagnostics are
  temporary laptop artifacts and are not committed. Verify their availability and
  safely transfer only what is needed before changing machines. Do not copy raw
  telemetry or credentials into the wiki or a general-purpose handoff.
