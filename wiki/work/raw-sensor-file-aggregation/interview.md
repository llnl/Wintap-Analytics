---
title: "Feature Interview: Raw Sensor File Aggregation"
type: concept
confidence: high
grounded_by:
  - wiki/component/sensor-upload-cache-pipeline.md
  - wiki/repo/wintappy-pipeline-repo.md
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/Merge.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../Wintap-PyUtil/pyproject.toml
policy: agent-editable
last_validated: 2026-11-10
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/raw-sensor-file-aggregation/interview.md
tags: [feature-work, raw_sensor, parquet, duckdb, s3, compaction, interview]
---

# Feature Interview: Raw Sensor File Aggregation

## Initial Idea

Wintap/Lintap hosts send 3–12 event-type Parquet files every five minutes by
default. This gives useful latency but creates too many small files for
downstream consumers reading more than a few hours. The `dayPK`/`hourPK` tree
represents an upload-time window, not event time; cached events can be sent
after an outage. First compact each closed hour into one or a few files per
event type, then consider combining hourly files into daily files. Begin with a
manually run job, schedule with cron after it is stable, and use DuckDB 2.0.0
and `COPY` as the merge engine.

## Context Established Before Questioning

- The sensor's default upload interval is 300 seconds. Its existing `doMerge()`
  combines serializer output before the uploader sweep, but direct-to-`raw_sensor`
  producers can still leave small files. See
  [[wiki/component/sensor-upload-cache-pipeline]].
- Wintappy's canonical downstream input is `raw_sensor` and its current
  environment pins DuckDB 1.5.6 with `dbt-duckdb` 1.9.x. A separate DuckDB 2.0.0
  tool environment avoids silently upgrading that DBT environment.
- Current Wintap source derives `dayPK`/`hourPK` from the UTC merge/materialize
  time. A failed upload retains the local file, and the S3 adapter mirrors its
  existing relative path on retry. This does not currently guarantee a new
  partition based on actual upload time; a separate TODO records the requested
  .NET correction. See the source evidence in `references.md` and
  [[wiki/todo/raw-sensor-upload-time-partition]].
- Source and compacted output must not be placed together under a prefix scanned
  as one `raw_sensor` dataset: consumers would read both copies of the rows.

## Interview Log

### Round 1 — ownership, I/O, and scope

- **Q:** Where should the job live?
  **A:** Standalone CLI/environment in Wintap-Analytics, separate from the
  canonical Wintappy DBT environment.
  **Outcome:** Decision — use an isolated utility; do not change sensor or DBT
  dependencies as part of this feature.
- **Q:** Where should data be read and written?
  **A:** Direct S3.
  **Outcome:** Decision — the utility operates on S3 objects directly.
- **Q:** How should output relate to originals?
  **A:** Separate destination prefix/tree; retain source objects.
  **Outcome:** Constraint — never place both originals and aggregates under the
  same consumer-scanned root.
- **Q:** What is the first milestone?
  **A:** Hourly compaction first; daily compaction later; rescan was initially
  selected as the recommended handling for late arrivals.
  **Outcome:** Deferred pending clarification of the upstream upload-time
  partition contract.

### Round 2 — layout, grain, and sizing

- **Q:** How should the destination be laid out?
  **A:** Mirror the dataset structure as
  `<destination-root>/raw_sensor/<event_type>/dayPK=YYYYMMDD/hourPK=HH[/protoPK=...]/`.
  **Outcome:** Decision — preserve the canonical hive layout in a distinct
  dataset root; consumers can explicitly select it after validation.
- **Q:** What is the merge grain and schema policy?
  **A:** Combine across hosts by event type and exact hive leaf partition,
  including `protoPK`; preserve every row and field; union missing fields by
  name as NULL, and fail a partition on incompatible types.
  **Outcome:** Decision — no row-level transformation or cross-partition merge.
- **Q:** How should large output partitions be split?
  **A:** Use target-size shards; choose the exact target after a representative
  S3 benchmark and keep it configurable.
  **Outcome:** Decision — configurable target-size sharding; numeric default
  deferred to measurement.

### Round 3 — delayed uploads

- **Q:** What guarantee should the compactor rely on for late files?
  **A:** The contract is that hosts write into `dayPK`/`hourPK` from the UTC
  wall-clock time of actual upload. Create a separate TODO to change .NET code
  so failed/delayed uploads update the partition; the compactor need not scan
  old hours once that contract holds.
  **Outcome:** Decision — no automatic lookback in the base design; track the
  producer/uploader correction separately. The current-source mismatch is
  documented as a prerequisite/risk, not treated as already fixed.
- **Q:** Should the exact output shard target wait for a benchmark?
  **A:** Yes.
  **Outcome:** Decision — benchmark representative S3 data before selecting a
  default.

## Decisions

- Standalone manual CLI in Wintap-Analytics, using its own DuckDB 2.0.0
  environment and direct S3 input/output.
- Hourly-only first milestone; daily rollup and cron scheduling are later work.
- Compact across hosts within exact event-type and hive-leaf partitions, retain
  all rows/fields, and write to a separate destination dataset.
- No automated late-hour lookback under the desired upload-time partition
  contract; the .NET upload-partition correction is a separate TODO.
- Make output size configurable; choose its default from a representative
  benchmark.

## Constraints

- Preserve original source objects; do not modify event data or schemas.
- Keep DuckDB 2.0.0 isolated from Wintappy's current DBT/DuckDB dependency set.
- Preserve `protoPK` and the source hive partition values in the destination.
- The current source does not yet meet the desired actual-upload-time partition
  contract; the separate TODO remains open.

## Delegations

None recorded. Publication mechanics, CLI shape, and the exact output-size
default remain design work rather than delegated decisions.

## Deferred / Open Questions

- Exact CLI arguments for source/destination roots and explicit hour/range.
- S3 credential, endpoint, and DuckDB 2.0.0 extension/configuration approach.
- Safe staging, validation, and publication of a complete output partition so
  failed runs do not expose partial files and reruns do not append duplicates.
- Numeric target file size and shard naming after benchmark.
- Upstream completion of [[wiki/todo/raw-sensor-upload-time-partition]] before
  relying on the no-late-old-partition assumption for scheduled operation.

## Playback Summary

The human confirmed the feature playback before artifact creation. See
`brief.md` for the distilled scope and acceptance criteria.

## Sealed — human estimates

The answers below are recorded as given. They provide durations only; no solo
working-hour count or absolute availability date was supplied. Do not convert
durations to hours or infer dates. See
[[wiki/decision/ai-velocity-roi-mini-lab]] and
[[wiki/concept/velocity-metric]].

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available?**
**A:** `1: Human would take 4 days`

**Q: With the AI workflow, on what date do you predict this feature will be
available?**
**A:** `2: AI would take 2 days`

**Combined response received verbatim:** `1: Human would take 4 days, 2: AI
would take 2 days`
