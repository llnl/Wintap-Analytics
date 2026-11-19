---
title: "To-Do: Add a Daily Compacted Storage Tier"
type: diagnostic
confidence: speculative
grounded_by:
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
policy: agent-editable
last_validated: 2026-11-17
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: none
audience: mixed
status: stub
source_paths: ../Wintap-PyUtil/extras/raw-sensor-compact; ../Wintap-PyUtil/wintap_dbt; streamlit/projects/HostActivity
tags: [todo, backlog, p3, compaction, daily-tier, dayPK, hourPK, s3, dbt, data-pipeline]
---

# To-Do: Add a Daily Compacted Storage Tier

**Priority:** P3 — Low; opportunistic performance enhancement, not required for
the current historical catch-up or hourly compaction path.
**State:** Open — design intake only; no implementation is authorized by this
TODO.
**Likely next step:** Create a feature brief and benchmark daily shard reads
against the existing hourly compacted layout before changing producer or reader
behavior.

## Finding

The current compactor publishes event data at fixed UTC hour partitions under a
`dayPK/hourPK` layout. Process entity publication is a separate cumulative
operation: it merges the prior entity snapshots with the selected raw and
compacted process inputs and publishes replacement snapshots. A daily roll-up
should therefore merge already-compacted hourly Parquet without rerunning entity
processing.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §update_entities/process_hours ordering; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

The proposed steady-state layout is:

```text
raw_sensor/       current or not-yet-compacted edge files
compacted/        event/dayPK=YYYYMMDD/hourPK=HH/ hourly outputs
compacted2/       event/dayPK=YYYYMMDD/ daily roll-up outputs
```

The daily job would run after UTC midnight, consume the prior complete day of
hourly compacted outputs, and publish one or more daily Parquet shards per event
family. It should not be assumed that one physical file is appropriate for a
full day; shard size should be benchmarked.

## Required reader semantics

Readers must select disjoint sources rather than unioning all three tiers:

1. use `compacted2` for days with a verified daily publication;
2. use hourly `compacted` for days or hours not covered by a daily publication;
3. use `raw_sensor` only for the current edge or an explicitly uncovered hour.

The current DBT path macros intentionally construct raw-plus-hourly-compacted
input globs with union semantics and no overlap suppression. Adding a daily tier
therefore requires a resolver that knows which physical tier owns each requested
day/hour and emits non-overlapping globs. Existing row-level `dayPK` and
`hourPK` values should be retained in daily output even when `hourPK` is absent
from the physical directory path.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_event_input_paths/partition_globs_for_path/raw_sensor_partition_globs -->

## Publication and late-data requirements

Before a daily tier is selected by readers, the producer must verify:

- all expected hourly event partitions for the UTC day have reached a terminal
  verified state, including intentionally empty hours;
- the daily output inventory and row counts match the hourly inputs;
- a durable manifest or readiness record identifies the covered day, event
  families, input fingerprints, output fingerprints, and publication version;
- readers cannot observe a partially written daily roll-up as authoritative.

Late-arriving data for a day already represented in `compacted2` must have an
explicit policy. Candidate policies are invalidating and rebuilding the daily
roll-up, publishing a new version while retaining the old manifest, or placing
late data in a repair/delta path that readers understand. Silently unioning the
old daily output with late hourly data would duplicate rows.

If hourly outputs are eventually deleted after daily publication, deletion must
be a separate verified phase with recovery evidence. Retaining hourly outputs
initially is safer and allows comparison and rollback, but reduces the storage
and listing benefit.

## Entity-cache boundary

The daily merge must not update or replace process entity snapshots. Entity state
must already have been advanced and verified by the hourly writer before the
corresponding hourly outputs become eligible for daily roll-up. The daily job
may carry forward processing metrics or publication metadata, but it must not
pretend to be a new entity-observation pass.
<!-- SYNTHESIS: inferred from cumulative entity publication in ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py and the hourly execution ordering in ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py -->

## Investigation and verification

1. Define the daily publication contract, readiness marker, versioning, and
   recovery behavior.
2. Implement a read-only inventory/planning mode that proves all 24 hourly
   inputs are present and disjoint from raw edge inputs.
3. Benchmark hourly versus daily reads for DBT and representative dashboard
   queries, measuring object counts, planning time, scan time, and output size.
4. Test empty hours, missing event families, partial daily writes, restart after
   publication, and repeated daily runs.
5. Test late data before and after daily publication, including rebuild and
   version-selection behavior.
6. Update DBT source validation and downstream readers so a closed day is read
   from exactly one tier.
7. Only after reader qualification, evaluate whether verified hourly outputs can
   be removed from closed days.

## Open questions

- Should the daily root be `compacted2`, or should the tier be distinguished by
  a versioned dataset/prefix under the existing compacted root?
- Is a daily roll-up authoritative after a fixed grace period, or only after an
  explicit completeness signal from the uploader/coordination ledger?
- Should late data trigger a full daily rebuild, a new daily version, or a
  supported delta layer?
- Should hourly outputs remain for recovery and audit, or be deleted after a
  retention interval?
- What shard size and compression produce the best DuckDB/S3 tradeoff?
- Which DBT, dashboard, and external analytics readers require the new source
  resolver?

## Scope

This is a cross-repo design intake item for a future PyUtil/DBT/downstream-reader
enhancement. It is deliberately separate from the November historical catch-up,
which should continue using the verified hourly compaction plus serialized entity
publication path. No source code, schema, raw document, or S3 object was changed
by this TODO.
