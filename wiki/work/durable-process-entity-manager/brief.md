---
title: "Feature Brief: Durable Process Entity Manager"
type: concept
confidence: medium
grounded_by:
  - wiki/concept/durable-process-context-and-stream-table-enrichment.md
  - wiki/work/raw-sensor-file-aggregation/process-context-options.md
  - wiki/diagnostic/process-tree-context-completeness.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
policy: agent-editable
last_validated: 2026-11-13
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: reviewed
source_paths: wiki/work/durable-process-entity-manager; ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt
tags: [feature-work, entity-state, process, ancestry, parquet, s3]
---

# Feature Brief: Durable Process Entity Manager

## Human direction

> For the first round, "persistence" will be parquet files in S3. The when DBT
> runs, which is relatively infrequently, it will use that to enrich the data
> for accurate parents.
>
> The hourly compaction, which will also do this durable process entity
> management, will update that store (and maybe compact those also?).
>
> So its sort of stateless. Plan that out

**Selected architecture:** S3 Parquet persistence; the hourly compaction job also
maintains durable process entities; infrequent DBT jobs consume them for parent
context. The worker has no durable local database or always-running service.
Persistent state is in S3, so this is a stateless worker, not a stateless dataset.
This request authorizes planning, not implementation or new S3 operations.

**Subsequent authorization:** the human accepted the first-round plan and said
"You can test based on the kind of orphaned processes we were seeing before.
Proceed!" Implementation now lives in Wintap-PyUtil. See
[[wiki/tool/durable-process-entity-manager]] for durable facts and
[[wiki/work/durable-process-entity-manager/verification]] for tests. The planning
scope restriction above describes the earlier request, not the current authorization.

## Problem

A short activity window can omit long-lived and exited ancestors. The current
DBT process model reduces only selected lifecycle observations and uses arbitrary
parent representatives. A small missing-ancestor set can disconnect many descendants.
Persisting observed instance context independently of the analysis window supplies
known parents without repeatedly publishing synthetic lifecycle events.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §process_base -->
<!-- SYNTHESIS: wiki/diagnostic/process-tree-context-completeness.md; this store cannot recover never-collected evidence -->

## Recommended first-round scope — proposed defaults

- Separate `process_entities/` S3 root, outside raw/compacted event scan trees.
- One fixed Parquet snapshot per initialized host, rewritten only when entity
  content changes. Rewriting performs entity compaction; no hourly delta-file pile.
- Keep all observed process instances, including exited ancestors. No TTL, LRU
  eviction, or reachability GC in round one. Bound job resources, not history
  correctness; add sharding only after measurement.
- Merge lifecycle evidence deterministically and idempotently by recorded instance
  key in host scope. Preserve conflicts instead of silently choosing a parent.
- Explicit historical bootstrap and rebuild from retained raw plus compacted
  process archives. Hourly updates alone cannot supply earlier missing ancestors.
- Publish and verify entity updates before deleting source process observations.
- DBT joins a separate entity/context dimension; do not inject historical rows
  into bronze raw telemetry or treat them as in-window Start/Refresh activity.

These recommendations were accepted for first-round implementation by the
subsequent "Proceed!" instruction. Details: [[wiki/work/durable-process-entity-manager/design]].

## Non-goals

Other entity domains; sensor/resolver changes; invented parents or PID-only repair;
Kafka, a service or persistent local DB; arbitrary metadata SCD/as-of history;
automatic retention/GC; concurrent writers or DBT/update overlap; general repair
of every existing DBT ANY_VALUE field; changes to raw compaction's count/duplicate/
NULL/skip/grace semantics; production migration or scheduling deployment.

## Proposed acceptance criteria

1. A fresh worker can update initialized S3 snapshots using only S3 inputs and
   disposable local staging; both DuckDB runtime pins remain isolated.
2. Replay, duplicate rows, source/compacted overlap and processing hours out of
   order produce the same semantic entity state as one complete logical pass.
3. PID reuse and same-boot collector restarts do not collapse or rekey instances;
   unknown identity/parent sentinels and host collisions remain explicit.
4. Parent, birth and Stop conflicts are preserved; stale Refresh cannot erase
   known Stop evidence. Missing ancestors remain unresolved, never fabricated.
5. Entity snapshots are validated before upload and reread afterward. Update/read/
   validation/resource failure blocks deletion of affected process source hours.
6. Existing raw destination hours still skip raw compaction and never authorize
   source deletion. Entity replay/backfill can independently revisit selected
   process evidence without using that skip as an ingestion cursor.
7. DBT can reach a parent/ancestor observed outside the selected activity window,
   including exited ancestors, without inflating raw or in-window lifecycle counts.
8. Configured-but-missing/corrupt entity snapshots fail DBT; disabled enrichment
   explicitly preserves the legacy behavior. Coverage and conflict QA are visible.
9. Local restart/failure/replay tests pass before separately approved isolated-S3
   and copied-data full DBT qualification. Never use original datasets as test targets.

## Ownership and next steps

Wintap-PyUtil owns batch/state and DBT code; Analytics owns this wiki and verification
records. Wintap sensor and Lintap packaging code remain unchanged.

- [[wiki/work/durable-process-entity-manager/design]] — layouts, evidence merge,
  safe update sequence and DBT enrichment.
- [[wiki/work/durable-process-entity-manager/implementation_plan]] — staged delivery
  and review gates.
- [[wiki/work/durable-process-entity-manager/verification]] — completed implementation,
  earlier actual-hour and week metrics, with historical/entity/deletion limits.
- [[wiki/work/durable-process-entity-manager/dev_handoff]] — committed milestone
  scope and prioritized follow-up; no production-readiness claim.

## Production decisions still needed

First-round no-GC/per-host snapshots and conservative evidence conflict policy
are implemented. Select actual expected hosts, historical bootstrap and store
namespace/root, deploy external DBT maintenance exclusion, and qualify production
capacity limits before any live cutover. No production deployment performed.
