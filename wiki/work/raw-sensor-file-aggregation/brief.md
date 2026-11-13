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
last_validated: 2026-11-12
repo_scope: cross-repo
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
feature provides a separate S3 compaction path, with optional validated source
prefix deletion and unioned raw/compacted DBT input. Scheduling remains deferred.

## Goals

- Provide a manually run standalone CLI, with cron scheduling deferred until
  manual operation is stable.
- Use DuckDB 2.0.0 as the core engine for direct S3 Parquet reads and `COPY`
  output and validation, in an isolated environment. Parquet is the input/output
  interchange format; the newly approved consumer tests retain PyUtil's DuckDB
  1.5.6 environment rather than upgrading it.
- Compact a selected completed UTC hour across hosts, separately for each event
  type and exact hive leaf partition (including network `protoPK`).
- Preserve every source row and field. Union missing columns by name as NULL;
  fail a partition when types cannot be safely reconciled.
- Treat compaction as a name-aligned `UNION ALL`. For development and operational
  validation, compare total source rows with total merged rows in each partition.
- Write one or a few target-size shards to a separate dataset root mirroring
  `<event_type>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/`, specifically
  `lintap/compacted/` beside `lintap/raw_sensor/`. No generation/run-ID directory
  and no extra `raw_sensor/` level in the destination.
- Compacted object filenames may change; source-to-output filename consistency
  is not required. Preserve the existing partition scheme.
- Retain source by default; explicit `--delete-source` validates the whole event/hour
  then deletes its prefix after the UTC grace (default 10 minutes, minimum 5).
- DBT reads remaining raw_sensor plus compacted with name alignment and UNION ALL.
  Temporary/failure overlap is accepted; no reader deduplication/preference rule.
- For each event/day/hour, skip an existing destination hour; otherwise merge.
  Failed/partial output is manually cleaned. Row order is immaterial; do not sort.
- Measure representative data before selecting a configurable target shard
  size.

## Non-Goals

- Changing Wintap/Lintap sensor upload cadence, collector behavior, or raw event
  schema as part of this feature.
- Deleting original live source objects during testing or rolling out production
  deletion without a separately scoped cutover. Tests delete only isolated copies.
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
- Write directly into an absent destination hour. Repeat runs skip existing
  event/day/hour prefixes, including partial failures; cleanup/rebuild is manual.
  One writer per destination and no readers of an hour during its merge are
  operating assumptions, not a distributed lock or atomic publication guarantee.
- PyUtil resolves `<WINTAP_DBT_RAW_SENSOR_DATASET>/raw_sensor` and its sibling
  `compacted`; `WINTAP_DBT_COMPACTED_ROOT` optionally overrides the direct event
  root. Both participate in partition/event/optional-column discovery. DBT builds
  follow successful migration or manual failure reconciliation, not active overlap.

## Acceptance Criteria

1. A manual CLI run reads only the requested source hour/event partitions from
   S3 and writes the corresponding separate destination partitions.
2. For every successful output partition, `COUNT(*)` across all selected source
   files equals `COUNT(*)` across all merged output shards. Use this same
   per-partition check in development and operation; report a nonzero difference
   as failure. Compaction uses `UNION ALL` semantics, retaining duplicate rows.
3. All source columns are preserved; missing columns across files are
   name-aligned with NULLs; incompatible types fail clearly before writing that
   event/hour. Runtime write/validation failures may leave partial derived output.
4. Network protocol partitions remain distinct. No files from different event
   types or hive leaves are combined.
5. Default mode preserves source byte-for-byte. Deletion mode removes only the
   validated closed event/hour prefix after grace; no deletion after merge/schema/
   validation failure. Isolated-copy tests preserve original live source hashes.
6. Existing destination event/day/hour prefixes are skipped, not overwritten or
   appended. Failed merges can leave directly visible partial output and require
   manual cleanup before rerun; existence is not a completion/validation marker.
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

- Wintap-PyUtil: standalone utility/tests in `extras/raw-sensor-compact/` and
  the dual-root DBT consumer; separate DuckDB 2.0.0 and 1.5.6 environments.
- Wintap-Analytics: shared wiki, feature documentation and verification records.
- S3 source and destination dataset roots; no in-place rewrite.
- Wintappy/PyUtil: shared dual-root DBT macros/config/preflight and migration tests;
  its engine stays DuckDB 1.5.6, the compactor stays DuckDB 2.0.0.
- Wintap shared .NET upload code is a separate TODO and requires separate code
  authorization before modification.

## References

See [[wiki/work/raw-sensor-file-aggregation/references]] and the interview
record in [[wiki/work/raw-sensor-file-aggregation/interview]].

The reviewed [[wiki/work/raw-sensor-file-aggregation/implementation_plan]] maps
delivery steps and tests to these acceptance criteria. Runtime evidence will be
recorded in [[wiki/work/raw-sensor-file-aggregation/verification]]. The explicit
fixed-root/skip-hour correction supersedes immutable generation roots:
[[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]].

## Open Questions

Optional follow-on discussion (not part of current acceptance):
[[wiki/work/raw-sensor-file-aggregation/process-context-options]] considers a
bounded process-context projection fed by the hourly pass. It remains separate
from row-preserving compaction; scope expansion and downstream integration require
an explicit decision.

- What exact CLI flags/defaults select the source root, destination root, and
  hour range?
- Should the standalone utility use DuckDB's Python API or invoke the DuckDB
  CLI binary?
- What DuckDB 2.0.0 S3 credential/endpoint and extension setup is supported in
  the intended runtime?
- Source-prefix deletion and dual-root consumer tests are now authorized on isolated
  copies. Original live cutover remains separate. Fixed output/skip/manual cleanup
  is the chosen contract, not a pending staging/manifest decision.
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
  direct merge, rerun skip, manual failure cleanup, and source immutability.
- Isolated copied-input migration: raw-only baseline, mixed input, fully compacted;
  validate/delete source prefixes and compare fresh DBT model results. Genuine
  duplicates, NULL/missing columns, rollover/protocols and deletion faults included.
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
