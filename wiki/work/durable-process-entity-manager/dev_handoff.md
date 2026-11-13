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

**First-round implementation is complete; production readiness is not.** The
human requested committing this milestone on November 13. Wintap-PyUtil owns the
implementation, Analytics the wiki/evidence. Use the existing branches; no push,
test-output cleanup, private-config inclusion or production cutover is authorized.

Implementation milestone: Wintap-PyUtil **`2cfbad1`**, branch
`work/raw-sensor-compacted-union` (25 files). This handoff, canonical pages and
qualification record are committed separately on Analytics
`work/raw-sensor-file-aggregation`. Neither branch is pushed.

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

## Next, in order

1. **Reconcile three failed raw hours, read-only first.** November 5/06 network,
   November 9/11 SELinux transition, November 11/20 SELinux interaction failed
   immediate deletion verification. Exact failed event prefixes are empty later,
   but this does not establish why the checks failed or certify the whole hour.
   Inventory and compare partial outputs against immutable local input copies;
   propose exact repair actions before mutating anything. Retain 25 partial
   outputs/60,900,907 bytes and 142 unprocessed inputs/28,481,517 bytes. A blind
   rerun skips existing destinations and cannot reconcile overlap safely.
2. **Resolve unknown-identity handling explicitly.** Historical bootstrap fails
   before publication; week entity maintenance stops at November 5/hour 01 after
   one combined hour. Negative-PID Refresh and sentinel-key positive-PID Stop
   evidence exists. Decide an evidence-preserving contract and tests; do not
   silently filter, invent identities/ancestors or repair by PID alone. The
   retained 33,824-entity/nine-snapshot state is stale and week-limited.
3. **Qualify historical scale after identity policy.** Expanded source counts
   exceed the default one-million-row per-host limit on two hosts. Bootstrap
   failed identity validation, not a demonstrated capacity failure.
   Measure actual staging/decoded evidence/full-snapshot rewrite costs; obtain
   approval for budget changes or sharding rather than silently pruning history.
4. **Complete original audit-window DBT enrichment qualification.** Bootstrap a
   verified historical state, hold the original seed population fixed, compare
   parents/root/gap/conflict verdicts independently, and distinguish larger source
   coverage and recorded-root policy from genuine enrichment improvements.
5. **Consider PIDstat layout tuning separately.** Week PIDstat expands 467.563 →
   1,395.968 MB; other families save 26.21%. Larger-row-group local candidates are
   promising, but shipping settings and S3 outputs were not changed. Qualify
   payload/NULL/duplicate/schema preservation and representative resource/performance
   behavior before accepting a new default.
6. **Only then review production operation.** Explicit roots/hosts/namespace/root
   PID policy, complete bootstrap, one writer, external DBT-reader exclusion,
   missed-hour catch-up and manual failure recovery need operator acceptance.

## Evidence and retained test locations

- [[wiki/work/durable-process-entity-manager/verification]] — detailed commands,
  counts, comparisons, failure diagnosis and storage accounting.
- [[wiki/work/durable-process-entity-manager/implementation_plan]] — remaining gates.
- [[wiki/tool/durable-process-entity-manager]] — implemented contract.
- Actual test root:
  `s3://lintap-alpha/entity-tests/dpe-actual-week-20261112-8f52baa9-5d38-41f1-89a2-79043b50e4bd/`.
  Week raw outputs: `compacted/`; stale entity state:
  `week-limited-process-entities/`; separate earlier hour: `earlier-hour/`.
- Private detailed reports, immutable local copies and scripts:
  `/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/dpe-actual-week-1vnezp50/`.
  These temporary-machine artifacts are not committed; verify availability before
  resuming. The wiki preserves the durable findings, not raw telemetry or credentials.
