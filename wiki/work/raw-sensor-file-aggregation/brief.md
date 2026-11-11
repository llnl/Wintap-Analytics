---
title: "Feature Brief: Raw Sensor File Aggregation"
type: concept
confidence: medium
grounded_by:
  - wiki/component/sensor-upload-cache-pipeline.md
  - wiki/repo/wintappy-pipeline-repo.md
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
policy: agent-editable
last_validated: 2026-11-10
repo_scope: Wintap-Analytics
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/raw-sensor-file-aggregation/brief.md
tags: [feature-work, raw_sensor, parquet, duckdb, s3, compaction]
---

# Feature Brief: Raw Sensor File Aggregation

## Problem

Hosts produce many small event-type Parquet objects in S3. The current
five-minute upload cadence is useful for low latency, but the resulting object
count makes multi-hour and longer downstream reads expensive. The sensor-side
merge does not consolidate all direct-to-`raw_sensor` producer output. This
feature proposes a separate, scheduled S3 compaction path without changing the
original raw objects.

## Goals

- Provide a manually run standalone CLI, with cron scheduling deferred until
  manual operation is stable.
- Use DuckDB 2.0.0 as the core engine for direct S3 Parquet reads and `COPY`
  output and validation, in an isolated environment. Parquet is the input/output
  interchange format; this feature does not require a cross-version DBT test.
- Compact a selected completed UTC hour across hosts, separately for each event
  type and exact hive leaf partition (including network `protoPK`).
- Preserve every source row and field. Union missing columns by name as NULL;
  fail a partition when types cannot be safely reconciled.
- Treat compaction as a name-aligned `UNION ALL`. For development and operational
  validation, compare total source rows with total merged rows in each partition.
- Write one or a few target-size shards to a separate dataset root mirroring
  `raw_sensor/<event_type>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/`.
- Compacted object filenames may change; source-to-output filename consistency
  is not required. Preserve the existing partition scheme.
- Retain all source objects. Consumers switch explicitly to the output dataset
  after validation; do not co-locate source and compacted Parquet under one
  scanned `raw_sensor` root.
- Measure representative data before selecting a configurable target shard
  size.

## Non-Goals

- Changing Wintap/Lintap sensor upload cadence, collector behavior, or raw event
  schema as part of this feature.
- Replacing or deleting source S3 objects.
- Upgrading Wintappy's canonical DBT environment from DuckDB 1.5.6, or changing
  the broader DuckDB 2 upgrade plan. This is a separate tool environment.
- Daily compaction in the first milestone.
- Adding cron/systemd scheduling before the manual job is validated.
- Implementing the separate .NET delayed-upload partition correction in this
  feature; track it in [[wiki/todo/raw-sensor-upload-time-partition]].

## User-Facing Behavior

- An operator invokes a standalone CLI against a source S3 dataset and a
  separately configured destination dataset.
- The first version processes explicitly selected completed UTC hour
  partition(s); it does not automatically scan a recent lookback window.
- Each event-type/partition group is written independently, retaining
  `dayPK`, `hourPK`, and optional `protoPK` as directory partitions.
- Count all rows in that partition's source files and all rows in its output
  shards. Report both totals and their difference; a mismatch fails the partition.
  The same check is available as a read-only operational verification command.
- Output is staged and published only after the entire partition succeeds;
  repeat runs replace/rebuild derived output rather than append duplicate rows.
  The exact safe S3 publication mechanism remains a design question.
- A later operator may point Wintappy's `WINTAP_DBT_RAW_SENSOR_DATASET` at the
  destination dataset root. Existing input remains unchanged.

## Acceptance Criteria

1. A manual CLI run reads only the requested source hour/event partitions from
   S3 and writes the corresponding separate destination partitions.
2. For every successful output partition, `COUNT(*)` across all selected source
   files equals `COUNT(*)` across all merged output shards. Use this same
   per-partition check in development and operation; report a nonzero difference
   as failure. Compaction uses `UNION ALL` semantics, retaining duplicate rows.
3. All source columns are preserved; missing columns across files are
   name-aligned with NULLs; incompatible types fail clearly without publishing
   a partial partition.
4. Network protocol partitions remain distinct. No files from different event
   types or hive leaves are combined.
5. Original source objects remain byte-for-byte untouched.
6. Failed runs do not expose incomplete output. Re-running an hour is
   idempotent and does not duplicate prior aggregates.
7. Output sharding uses a configurable target-size policy. The initial default
   is selected from a representative S3 benchmark and documented with observed
   event-family sizes and runtime.
8. A fresh DuckDB 2.0.0 read opens the completed Parquet output through the
   preserved hive-partition layout, and operational verification reports equal
   source/output row counts per partition. Object filenames and derived
   source-object `filename` values may change, per the clarifications in
   [[wiki/work/raw-sensor-file-aggregation/interview]].
9. A scheduled run is not considered safe under the no-lookback assumption
   until the upload-time partition contract in
   [[wiki/todo/raw-sensor-upload-time-partition]] is implemented or otherwise
   verified.
10. For multi-file input partitions, compaction reduces the number of Parquet
    objects while preserving all rows; the benchmark records before/after file
    counts, bytes, and row counts by event type.

## Affected Areas

- Wintap-Analytics: standalone utility, tests, and feature documentation.
- S3 source and destination dataset roots; no in-place rewrite.
- Wintappy only as an optional later consumer/dataset-root configuration;
  compaction and validation use DuckDB 2.0.0 with Parquet input/output.
- Wintap shared .NET upload code is a separate TODO and requires separate code
  authorization before modification.

## References

See [[wiki/work/raw-sensor-file-aggregation/references]] and the interview
record in [[wiki/work/raw-sensor-file-aggregation/interview]].

The reviewed [[wiki/work/raw-sensor-file-aggregation/implementation_plan]] maps
delivery steps and tests to these acceptance criteria. Runtime evidence will be
recorded in [[wiki/work/raw-sensor-file-aggregation/verification]]. Its proposed
publication, CLI, and schema policies remain implementation decisions to settle.

## Open Questions

- What exact CLI flags/defaults select the source root, destination root, and
  hour range?
- Should the standalone utility use DuckDB's Python API or invoke the DuckDB
  CLI binary?
- What DuckDB 2.0.0 S3 credential/endpoint and extension setup is supported in
  the intended runtime?
- What staging/manifest/publication protocol provides partition-level safety
  under S3 object semantics? See
  [[wiki/tension/raw-sensor-compaction-publication-vs-glob-readers]] and the plan's
  proposed immutable-window dataset roots with explicit consumer selection.
- What target shard size best balances fewer files with scan parallelism and
  memory/runtime limits?
- The current .NET producer/uploader does not yet implement the intended
  actual-upload-time `dayPK`/`hourPK` rule; see the separate TODO.

## Test Plan

- Synthetic local Parquet fixtures: multiple hosts, event types, `protoPK`,
  missing columns, compatible schema drift, and incompatible types.
- DuckDB 2.0.0 per-partition source/output row-count and repeat-run tests against
  temporary input/output roots, plus small fixtures for name alignment and fields.
- S3 tests against an isolated test bucket/prefix: bounded object discovery,
  staged publication, injected failures, retries, and source immutability.
- Representative S3 benchmark across event families to select a configurable
  shard target.
- Reopen completed Parquet through the preserved raw-source partition layout
  using DuckDB 2.0.0 and run the same operational row-count check.
- No production-bucket mutation during development or acceptance testing.

## Done When

- Acceptance criteria pass on synthetic fixtures and an isolated S3 dataset.
- The output layout and rerun/publication contract are documented.
- A representative benchmark selects a configurable default shard target.
- Operational readiness states the status of the separate delayed-upload
  partition TODO and the prerequisite for safe scheduled operation.
