---
title: "Instrumentation Plan: Lintap Stair-Step Memory Growth"
type: concept
confidence: medium
grounded_by:
  - ../Wintappy/notebooks/wintap_dbt_overview.py
  - ../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql
  - ../Wintappy/wintap_dbt/models/silver/process.sql
  - ../Wintappy/wintap_dbt/models/silver/process_file.sql
  - ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintappy/wintap_dbt/models/silver/process_registry.sql
policy: agent-editable
last_validated: 2026-08-28
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md
tags: [feature-work, plan, lintap, pidstat, memory, instrumentation]
---

# Instrumentation Plan: Lintap Stair-Step Memory Growth

## Question

Why does the long-running `Lintap` process appear to grow in stair steps and not
fully return to earlier memory plateaus over time?

## Current Read From This Run

From the current pidstat-backed QA run:

- `Lintap` is one long-lived process instance on `spk16` with sustained high CPU
  and sustained write activity.
- RSS grows in jumps on the order of tens of MB rather than as a smooth monotone
  slope.
- Some later buckets do fall, but the process rarely returns to its earlier
  plateau, suggesting ratcheting/high-water-mark behavior.
- The strongest workload correlate visible in the current joined 5-minute view is
  file-event volume rather than network/process/registry volume.
- pidstat alone cannot tell whether the stairs come from:
  - true retained application state,
  - managed heap growth that is partly reclaimed but not returned to the OS,
  - allocator arena retention,
  - file-backed / mmap growth,
  - or a queue/buffer/cache that scales up under burst load and shrinks poorly.

Working hypothesis:

- the stair-step pattern is likely burst-correlated memory ratcheting, probably
  file-pipeline-driven, but the current evidence is not enough to distinguish a
  true leak from allocator/runtime retention.

## Goal

Add enough low-overhead, time-correlated telemetry to distinguish:

1. managed heap growth vs non-managed growth
2. anonymous memory growth vs file-backed growth
3. internal queue/cache growth vs runtime/allocator behavior
4. file-pipeline-driven bursts vs other event-family causes

## Plan

### Collection Modes

There are two useful operating modes, and both should use the same downstream
shape so the short-term work is not throwaway.

#### Mode A: Manual batch capture (recommended first)

Run a short, explicit on-host capture for a few minutes while Lintap is under
known workload.

Why this should come first:

- fastest path to evidence today
- lowest integration risk
- easiest to iterate on command choice and schema
- lets us measure observer overhead before promoting anything to long-term use

Recommended use:

- 5-15 minute targeted runs
- capture around known file-heavy or stress windows
- write one or a few completed parquet files per event type into the canonical
  `raw_sensor/<event_type>/dayPK=/hourPK=` layout

#### Mode B: Long-term sidecar capture alongside pidstat and Lintap

Run the same collectors continuously as a sidecar, rotating into partitioned
parquet and letting the existing data-store/upload pattern handle them.

Why this is still valuable:

- needed for real steady-state deployment analysis
- captures rare plateau or recovery behavior that short runs may miss
- creates reusable telemetry for regression detection and tuning over time

Why it should probably not be the first implementation:

- command set and schema are still being discovered
- we do not yet know collection overhead on long-lived hosts
- internal counters are not yet stabilized enough to promise a durable contract

Recommendation:

- design the files and schemas now as if they will become long-term event types
- but implement manual batch mode first and promote only after a short iteration
  cycle validates usefulness and overhead

### Proposed New Event Types

Write the new performance streams as canonical raw-style parquet event types so
they can later be uploaded and modeled the same way as other raw telemetry.

Initial proposed event types:

- `perf_smaps_rollup`
  - one row per sample for `/proc/<pid>/smaps_rollup`
  - focus: `RssAnon`, `RssFile`, private/shared clean/dirty, swap
- `perf_dotnet_counters`
  - one row per sample for .NET runtime/process counters
  - focus: heap size, allocation rate, GC counts, LOH, thread pool where available
- `perf_lintap_diag`
  - one row per sample for application-owned internal counters
  - focus: queue depth, backlog, aggregation-map size, writer batch size, drop/backpressure indicators
- `perf_fd_map`
  - lower-frequency process context rows
  - focus: open fd count, mapped-region count, mapped-byte totals if available

These names are intentionally descriptive but still aligned with the raw event
family pattern used elsewhere.

### Output Layout

For both modes, use the same canonical layout:

```text
<data_root>/parquet/raw_sensor/<event_type>/dayPK=YYYYMMDD/hourPK=HH/<file>.parquet
```

That gives three benefits immediately:

- Wintappy/DBT can ingest them later without inventing a second storage scheme
- manual captures and long-term sidecar captures become comparable
- promotion into uploader-backed long-term collection is mostly an operational
  step rather than a data-contract rewrite

### Layer 1: Keep pidstat, but treat it as the outer symptom signal

Keep the current pidstat collection because it gives the outer shape:

- CPU
- RSS / VSZ
- write throughput
- page faults
- context switches

Use it as the timeline anchor for every other signal below.

No further pidstat schema change is required for this question right now.

### Layer 2: Add Linux process memory breakdown sampling

Add a lightweight sampler for the Lintap PID from `/proc/<pid>/smaps_rollup`
or the closest low-overhead equivalent.

Capture at the same cadence or a coarser cadence than pidstat:

- `Rss`
- `Pss`
- `Private_Clean`
- `Private_Dirty`
- `Shared_Clean`
- `Shared_Dirty`
- `RssAnon`
- `RssFile`
- `RssShmem`
- `Swap`

Why:

- if the stairs are mostly `RssAnon`, this points toward heap / anonymous memory
- if they are mostly `RssFile`, look harder at file-backed mappings / writer
  behavior
- if RSS rises without a matching private-memory signal, allocator/runtime or
  sharing effects become more likely

Recommended storage shape:

- one time-series table keyed by `time`, `hostname`, `pid`, `process_name`
- keep it independent from pidstat for now; join later in QA views
- raw event type: `perf_smaps_rollup`

### Layer 3: Add .NET runtime counters for the Lintap process

Collect runtime counters from the running `Lintap` process.

Minimum counters to capture:

- managed heap size / GC heap size
- allocation rate
- Gen 0 collection count
- Gen 1 collection count
- Gen 2 collection count
- LOH size if available
- thread-pool queue / thread count if available
- exception rate if available

Why:

- if managed heap tracks the RSS stairs closely, suspect retained managed state
- if managed heap stays flatter than RSS, suspect native buffers, allocator
  retention, mmap/file-backed growth, or external library memory
- GC cadence helps distinguish "not collecting" from "collecting but not
  returning memory"

Recommended collection path:

- use the lightest stable .NET counter path available on the target host
- record as timestamped rows in a separate table or CSV/parquet stream
- raw event type: `perf_dotnet_counters`

### Layer 4: Add internal Lintap pipeline/backlog telemetry

This is the highest-value application-owned layer.

Add periodic point-in-time counters for the likely ratcheting structures,
especially around the file pipeline.

Initial targets:

- file-event queue depth
- serializer queue depth
- in-memory aggregation map sizes
- open file-identity map size / fd cache size if applicable
- upload/merge backlog counts
- any "current batch" size used by writers/flushers

Why:

- if RSS steps line up with queue/map growth, we get from symptom to subsystem
- if these structures stay flat while RSS grows, look harder at runtime or
  writer-side buffering

Important constraint:

- keep these counters cheap and periodic, not per-event logging
- raw event type: `perf_lintap_diag`

### Layer 5: Promote file-pipeline workload counters to first-class comparison signals

The current run points most strongly at file workload.

Add or expose time-series counters for:

- file events per minute
- dropped file events per minute
- aggregation flush sizes
- average / max file-event batch sizes
- any queue saturation or backpressure indicator

Why:

- we need a direct view of whether file-event bursts are the driver of the
  memory plateaus, not just correlated background noise

### Layer 6: Add filesystem / mapping context

Capture lower-frequency process context that helps rule in/out file-backed
growth:

- open FD count
- mapped-region count
- total mapped bytes if available cheaply

Why:

- useful for separating heap growth from mmap/file-backed accumulation
- raw event type: `perf_fd_map`

## Prioritized Order

### Priority 1: runtime + memory breakdown + existing pidstat

Do these first:

1. `/proc/<pid>/smaps_rollup` sampling
2. .NET runtime counters
3. preserve existing pidstat collection and current event-volume notebook views

This is the minimum set that can distinguish heap-vs-non-heap-vs-file-backed.

### Priority 2: internal pipeline counters

Add periodic Lintap counters for file pipeline, serializer, and queue/map sizes.

This is the minimum set that can identify the responsible subsystem.

### Priority 3: fd/mmap context and nicer QA joins

Add the lower-level OS context and promote the correlation views into cleaner QA
artifacts once the first two layers produce useful signal.

## Recommended Sampling Cadence

- pidstat: keep current cadence
- smaps/runtime counters: every 30s or 60s is likely enough
- internal pipeline counters: every 30s or 60s
- fd/mmap context: every 60s or 300s

Reason:

- the memory stairs in this run are minute-scale, not millisecond-scale
- coarser sampling reduces observer effect and storage noise

## What Success Looks Like

After one more long run, we should be able to answer:

1. Does managed heap grow in the same stair-step pattern as RSS?
2. If not, is the growth anonymous or file-backed?
3. Do file-pipeline queues/maps grow in the same windows as the RSS steps?
4. Are the stairs associated with event-burst handling, write batching, or a
   long-lived retained structure that never comes back down?

## Concrete Next Slice

1. implement manual batch-mode collectors in this repo for:
   - `/proc/<pid>/smaps_rollup`
   - .NET runtime counters for `Lintap`
   - one periodic Lintap diagnostic snapshot covering file-pipeline and
     serializer backlog/map sizes
2. write each collector's output as parquet into canonical raw-style event
   folders (`perf_smaps_rollup`, `perf_dotnet_counters`, `perf_lintap_diag`)
3. run short captures on the current host/workload and inspect overhead + signal
4. expose those streams in the QA notebook next to the existing pidstat and
   event-volume charts
5. only after that, decide whether the same collectors should be promoted into a
   long-running sidecar alongside pidstat-collector and uploader-backed storage
