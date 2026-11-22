---
title: "Decision: Fixed compaction hours with skip and manual cleanup"
type: decision
status: accepted
decided_on: 2026-11-12
confidence: high
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/interview.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
policy: human-review-required
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
source_paths: extras/raw-sensor-compact
tags: [decision, raw_sensor, compaction, fixed-root, manual-cleanup]
---

## Context

The human clarified that per-run UUID generations do not fit the required output
layout. The earlier [[wiki/decision/raw-sensor-compaction-immutable-window-roots]]
is superseded, including its reader-ready generation selection assumptions.

## Decision

<!-- REVIEW NEEDED: Human explicitly chose this contract and subsequently approved dual-root DBT and isolated-copy prefix-deletion tests; original live rollout remains separate. -->

<!-- REVIEW NEEDED: Source anchors relocated to PyUtil following the human's 2026-11-12 ownership correction; the accepted behavioral contract is unchanged. -->
PyUtil owns the standalone compactor and DBT consumer; Analytics retains the wiki
and feature evidence. See [[wiki/work/raw-sensor-file-aggregation/interview]].

```text
source: lintap/raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/...
dest:   lintap/compacted/<event>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/<merged>.parquet
```

For each event/day/hour: **if destination exists, skip; otherwise merge all source
files** separately within each optional protocol leaf. No run IDs, manifests,
reservation writes, sorting, or atomic visibility contract. Failed output remains
for manual cleanup, then an intentional rerun. Source/output count validation
remains mandatory. The initial source-retention decision was subsequently expanded
to optional validated prefix deletion below.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/interview.md §Superseding Fixed-Root Correction And Order Clarification -->

## Rationale

Simple stable paths and a presence check satisfy the requested manual workflow.
Name-aligned union-all preserves all rows without event-time ordering or aggregation.

## Consequences

- Existence is not proof of completion or correctness. Partial failed hours and
  empty local directories are skipped until manually cleaned.
- A single writer per destination is required; avoid reading an hour during its
  merge. No distributed concurrency or all-or-nothing publication guarantee.
- Skip is at the event/hour parent: existing TCP also skips a missing UDP leaf.
- Late source arrivals to an existing destination hour do not trigger rebuilds.
- Source is preserved by default. `compact --delete-source` validates every
  protocol leaf and then deletes the exact source event/hour prefix after UTC
  end plus grace (default 10 minutes, minimum 5). The human accepts rare clock
  skew and transient/failure overlap under the deployment's UTC upload contract.
- The endpoint's ignored conditional PUT is no longer a blocker because no
  conditional metadata write is needed.
- PyUtil now reads raw_sensor plus compacted with name alignment and UNION ALL;
  no deduplication/preference logic. DBT runs after successful migration/manual
  failure reconciliation, and affected bronze/materialized models are rebuilt.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/interview.md §Dual-Root DBT And Prefix Deletion Approval; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py -->

## Alternatives Considered

UUID generations, completion manifests, atomic reservations and source deletion
now. The human rejected the generation design and deferred deletion.
That initial deferral ended after basic tests passed; live test deletion is
authorized only for isolated copies, not a production migration.
