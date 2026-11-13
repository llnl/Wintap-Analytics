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
last_validated: 2026-11-12
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

### Planning clarification — 2026-11-10

**User:** "There is no need to have consistency in the filename: its just the
dayPK/hourPK partition scheme we need to keep."

**Outcome:** Decision — compacted object filenames may change. Preserve the
existing `dayPK`/`hourPK` layout and previously confirmed `protoPK` leaves;
source-object filename equality is not a consumer-acceptance requirement.

### Processing and validation clarification — 2026-11-10

**User:** "Prefer duckdb 2.0.0 for this processing. Parquet in and out, so no
compatibility issues" and "A simple validation test, for development and
operational use is to count total rows in a partition from the source files and
the merged result. They should always be equal. Its a simple union all operation."

**Outcome:** Decision — use DuckDB 2.0.0 for Parquet compaction and validation.
The required development/operational validation is per-partition source/output
`COUNT(*)` equality. Use `UNION ALL` semantics, preserving duplicates. This
supersedes the plan's proposed full-row multiset comparison and separate DuckDB
1.5.6/DBT compatibility test requirement.

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
- Output object filenames are implementation-defined; preserve the partition
  scheme rather than source-to-output filename consistency.
- DuckDB 2.0.0 handles Parquet input/output and validation. Each partition's
  source and merged row totals must match in both development and operation.

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
- Numeric target file size after benchmark; shard names are implementation-defined.
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

## Publication Approval And Test Authorization — 2026-11-12

Asked whether to approve immutable per-run roots selected explicitly after
verification, each containing only requested hours/families rather than an
accumulating history. Human response:

> Yes. And you can run a test. You can use AWS_PROFILE=lintap-alpha and config
> env env vars in /Users/johnson30/git/LLNL/Wintap-PyUtil/wintap-run.env-lintap-alpha.
> You can create a new root prefix in the S3 to write to

This approves the reader/root contract and bounded testing with a new destination
prefix; it does not authorize source mutation or a relaxed reservation protocol.
The supplied env file is read live, not copied or modified. Runtime findings
are in [[wiki/work/raw-sensor-file-aggregation/verification]]; the accepted root
decision is [[wiki/decision/raw-sensor-compaction-immutable-window-roots]].

## Superseding Fixed-Root Correction And Order Clarification — 2026-11-12

The human rejected persistent UUID run roots after clarifying their meaning:

> Source: `lintap/raw_sensor/<event type>/dayPK/hourPK/....`
> Dest: `lintap/compacted/<event type>/dayPK/hourPK/.../<merged>.parquet`
>
> for dayPK/hourPK to process:
>     if dest dayPK/hourPK existis, skip
>     else
>         merge files into dest
>
> Very simple. If a merge fails, we'll clean manually.

The human also suggested a **later** step: validate the merged hour against source
then delete source, once basics work. This is not current deletion authorization.

Further clarification:

> Order doesn't really matter, except maybe for better compaction. even that is
> a small gain. just merge all the small files in one partition.

Current contract: fixed event/day/hour output, existence-based skip, direct
name-aligned union-all without row sorting, manual cleanup for partial failures.
Optional protocols remain separate leaves; the skip check covers their hour
parent. No manifest/run ID/conditional reservation. This explicitly supersedes
the earlier immutable-root approval and visibility expectations; see
[[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]].

## Dual-Root DBT And Prefix Deletion Approval — 2026-11-12

After the fixed-root basics passed, the human requested that DBT read the union
of remaining raw_sensor and compacted input. Retention-caused overlap is artificial;
before going live, successful merges must validate then delete source as they go.
Temporary overlap and failures are explicitly accepted, without row deduplication
or a compacted-preference reader rule.

The human clarified the deletion scope:

> The sensors sending data have a contract to send into UTC based partitions,
> so waiting until ~5-10 minutes after assures we CAN delete by prefix.
> Is there a risk a clock is off: yes, but extremely low for the deployments we're doing.

The human approved the outlined isolated-copy test plan: raw baseline, partially
migrated input, fully compacted input, fresh DBT builds/results comparison, genuine
duplicates/NULL/schema drift/protocol leaves, merge/validation failures preserving
source and deletion failures requiring manual reconciliation. This authorizes the
compactor deletion implementation and PyUtil input/config/test changes. Live
deletion tests operate only on newly created copies, not the original live dataset.
The assistant chose default 10-minute grace, configurable down to 5 minutes.
No sensor contract rewrite, clock-skew hardening, scheduling or production cutover.

## Full-Model Live-Copy Qualification Expansion — 2026-11-12

The human asked, “Can we expand to all models?” after the scoped host/pidstat
DBT test instructions. Continue the approved isolated-copy migration approach:
copy all available DBT event families for the same 2026-11-11 08:00 UTC hour,
build the full graph in fresh raw/mixed/compacted databases, and compare schema
types/counts/result hashes. No original live deletion or consumer cutover. Absent
image-load/registry inputs are explicitly reported as absent, not live-qualified.

## ANY_VALUE Debt Does Not Block Compaction — 2026-11-12

After strict comparison and unchanged-input replay exposed unstable representatives,
the human clarified:

> The use of ANY_VALUE already has data quality issues we need to address
> anyway, so thats not a blocker.

Continue all-family isolated-copy migration without repairing production DBT
representatives in this task. Retain full builds/tests, matching schemas and
exact bronze results as gates. Record differences in ANY_VALUE-containing
models and their descendants as explicit data-quality diagnostics; keep exact
results required outside that dependency closure. This separates source fidelity
from existing analysis-representative debt, without hiding differences or claiming
all downstream results are equivalent. Original live cutover remains outside scope.

## Compactor Ownership Relocation — 2026-11-12

The human corrected the implementation location:

> I should have noticed this sooner: the compaction code itself belongs in
> Wintap-PyUtil. Can you move that?

Move the standalone package, tests, README, pyproject and lockfile into
`../Wintap-PyUtil/extras/raw-sensor-compact/`. Keep compaction behavior unchanged
and DuckDB 2.0.0 isolated from the main PyUtil DuckDB 1.5.6 environment. Update
integration subprocess paths and documentation/source anchors. Analytics retains
the wiki and historical verification evidence. This relocation does not authorize
new S3 operations, production cutover or ANY_VALUE repairs (ANY_VALUE is used
in DBT, not compaction).

## Artifact Cleanup And Commit Approval — 2026-11-12

> This looks good. Cleanup the S3 artifacts you made, commit current changes.

Remove only this work's identified test-copy/probe/generation objects and its
two initial retain-source compacted outputs; preserve original raw telemetry and
local verification evidence. Commit the feature implementation/documentation
in the existing Analytics and PyUtil branches without publishing private run-env
files. This does not request a push or production migration.
