---
title: "Implementation Plan: Durable Process Entity Manager"
type: concept
confidence: speculative
grounded_by:
  - wiki/work/durable-process-entity-manager/brief.md
  - wiki/work/durable-process-entity-manager/design.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: developer
status: draft
source_paths: wiki/work/durable-process-entity-manager; ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt
tags: [feature-work, implementation-plan, entity-state, parquet, dbt]
---

# Implementation Plan: Durable Process Entity Manager

**Status: first-round implementation authorized and completed; production rollout deferred.** This is a follow-on
to compaction commits PyUtil `aa99efd` and Analytics `6d69f39`, not an amendment
claiming entity state was part of the completed compactor qualification.

## Delivery slices

| Slice | Work and acceptance gate |
| --- | --- |
| DPE-01 schema/reducer spike | Pin instance/parent/evidence/time/coverage schema; confirm nested Parquet across 2.0.0 and 1.5.6; prove associative/commutative/idempotent reduction and conflict handling with known fixtures. Review parent selection and no-GC policy before promotion. |
| DPE-02 local snapshot lifecycle | Per-host full snapshot init/load/update/verify; disposable staging; missing expected host fails; semantic no-op avoids rewrite; explicit replay/rebuild and budget failure. No S3 mutations. |
| DPE-03 S3 publisher and combined hourly mode | Qualified single-object replacement, inventory/content checks, partial multi-host failure report; publish entity phase before calling existing raw merge/delete; preserve skip/grace/count behavior. Mock S3 failure cases first, then separately approved isolated endpoint tests. |
| DPE-04 DBT context reader and parent enrichment | Opt-in root/preflight/staging; deterministic parent resolution, context closure and parent lookup changes; no historical rows in bronze or window lifecycle counts; main DuckDB stays 1.5.6. Disabled-mode regressions unchanged. |
| DPE-05 end-to-end qualification | Bootstrap full history, then narrow-window activity on isolated fixtures; raw-only/mixed/compacted and replay/restart/failure tests. Compare evidence/lineage results independently, not only row counts. Explicit operator acceptance before production use. |

## Likely code ownership and files

In **Wintap-PyUtil only**, subject to explicit implementation authorization:

- `extras/raw-sensor-compact/src/raw_sensor_compact/`: new entity reducer,
  snapshot/store and orchestration modules; CLI/config integration. Keep the
  existing raw engine as the row-preserving merge path.
- `extras/raw-sensor-compact/tests/`: reducer, bootstrap, replay, publisher and
  deletion-safety tests. Keep state-validation gates separate from raw count gates.
- `wintap_dbt/`: entity root/config/access checks, a dedicated bronze state table,
  entity/context silver models, targeted `process` parent and `process_path`
  changes, schema/ancestry QA and docs. Audit current reference dependencies
  before adding activity-key context seeds.
- `scripts/check_dbt_config.py`, `Makefile`, `wintap-run.env.example`, README and
  integration tests: explicit optional root and maintenance expectations.

No sensor/packaging changes, main dependency upgrade, live dataset mutation,
private environment edits, or preemptive implementation commits.

## Required tests

Reducer: repeated identical input, arbitrary file/row/hour order, partition
overlap, missing fields, PID reuse, host isolation, collector restart, unknown
identity, sentinel parent, multiple parent pairs, parent/child pair consistency,
late Refresh after Stop, conflicting lifetime evidence and missing timestamps.

Store: init versus missing/corrupt expected snapshot; typed empty host; unchanged
state; new host; resource exhaustion; local prevalidation; PUT/GET failures,
lost acknowledgment, partial multi-host advancement and fresh-process recovery.

Combined job: state failure preserves all selected process sources; state succeeds
then raw fails; grace and protocol validation unchanged; raw skip does not delete
source; entity replay processes compacted-only history and explicitly requested
late evidence; ordinary no-state mode retains current regression results.
Inject new/changed/removed process objects between entity publication and raw
discovery to prove cross-phase inventory coverage blocks deletion.

DBT: parent before selected window, exited parent/live child, grandparent closure,
activity-only reference, unresolved/conflicted/sentinel parent, non-root cycle,
cross-host identical recorded key, no start-count inflation, schema/config failures
and disabled-mode compatibility. Compare root reachability and parent correctness
against independently constructed expected graphs, not shipping path SQL alone.

## Bootstrap, rollback and operations

Bootstrap an explicit new entity root from retained process archives and declared
host/runtime history, then verify before enabling the hourly mode and DBT reader.
Do not derive history start from collector birth or Refresh EventTime alone.

Rollback disables DBT enrichment and combined mode; raw/compacted telemetry stays
unchanged. State corruption needs an explicit rebuild from archives. Do not claim
that disabling enrichment makes a narrow raw window ancestry-complete, or that
disabling combined mode continues to maintain entity history.

No-GC snapshot growth and full-host rewrite time must be measured. First failure
at a budget limit is a visible capacity issue, not permission for silent pruning.
Sharded state/delta files/retention are later design choices, not hidden additions.

## Done checklist

- [x] Human-selected S3 persistence/hourly writer/infrequent DBT architecture recorded.
- [x] Read relevant wiki notes and current compactor/DBT source boundaries.
- [x] Draft first-round schema, fixed-host snapshot, idempotence, failure and DBT plan.
- [x] Human accepts first-round defaults and authorizes implementation/testing ("Proceed!").
- [x] DPE-01 canonical JSON-in-Parquet reducer and 2.0.0/1.5.6 interoperability pass.
- [x] DPE-02 local init/update/replay/new-root rebuild and explicit init-resume pass.
- [x] DPE-03 publisher/source-deletion safety pass on isolated generated fixtures.
- [x] DPE-04 DBT ancestry enrichment and disabled-mode regressions pass.
- [x] DPE-05 synthetic breakpoint fixtures pass full local and actual-S3 DBT builds.
- [x] Earlier actual hour: raw/mixed/compacted DBT, independent entity scalar and
  terminal-QA comparisons, window counters/summary populations and replay pass.
- [x] Seven daily inventories, 168-hour test execution and file/byte/day/event/runtime
  metrics recorded: 165 raw successes / 3 failed hours; all original hashes unchanged.
- [ ] Reconcile three failed deletion-verification hours without blind existing-output
  reruns; partial outputs and unprocessed inputs are retained.
- [ ] Historical identity-policy and capacity qualification: bootstrap and continued
  entity mode fail unknown-identity guard; only one combined hour passes. No full
  historical snapshot or original audit-window enriched DBT comparison qualified.
- [ ] Production-scale budgets, historical bootstrap and external schedule exclusion approved.
- [x] Update [[wiki/work/durable-process-entity-manager/verification]], canonical
  pages and wiki log; only then prepare a separately approved production rollout.
