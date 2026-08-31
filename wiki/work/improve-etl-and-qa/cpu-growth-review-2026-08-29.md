---
title: "CPU Growth Review: Lintap Long-Run Readiness"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py
  - wiki/work/improve-etl-and-qa/verification.md
policy: agent-editable
last_validated: 2026-08-29
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/improve-etl-and-qa/cpu-growth-review-2026-08-29.md
tags: [feature-work, lintap, cpu, memory, fileops, performance, long-run]
---

# CPU Growth Review: Lintap Long-Run Readiness

## Current Evidence

The collect-based one-hour mostly-idle `spk16` run measured `System.Runtime`
CPU usage at about `19.0%` on average (`12.9%..23.1%`). CPU had only
weak-to-moderate correlation with working set, GC heap, RSS, and anonymous
memory (`0.26..0.31`). The run therefore establishes a material CPU baseline,
but not a demonstrated CPU-growth trend or a memory root cause.
<!-- GROUND_TRUTH: wiki/work/improve-etl-and-qa/verification.md §Manual Checks -->

The current manual collector provides process status, memory breakdown, FD/map
context, and `System.Runtime` counters, but not per-thread CPU, process I/O, or
timed application-pipeline work. It cannot distinguish continuously expensive
event handling from recurring 500 ms, 60 s, or five-minute maintenance bursts.
<!-- GROUND_TRUTH: validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py §main -->

## Code Review Findings

### 1. Serializer backlog protection is active but currently drops file events

`Serializer` drops the newest event when its configurable in-memory cap is
reached. The live `spk16` log proves the file serializer cap is active at
`10000` and is dropping events under the current workload. Do not merely raise
the cap: that trades demonstrated data loss for unbounded memory unless the
drain cadence/throughput is corrected first.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Save; §initSensor; /var/log/lintap/Logs/Lintap.log §2026-08-29 fileserializer backlog warnings -->

### 2. Serializer flush work can become disproportionately expensive after bursts

At each serialization interval, a serializer drains its current queue, then
groups mixed message types by repeatedly scanning and removing from a list.
Large queues can therefore amplify CPU and allocation work. The repeating timer
has no explicit non-reentrancy guard, so an overlong flush also needs direct
measurement rather than assumption.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §FlushToDiskTimer_Elapsed; §serialize -->

### 3. FileOps keeps an FD-to-path cache without observed process-exit or age eviction

File opens add entries under PID/FD and close records remove them. The cache is
cleared at sensor shutdown, but the reviewed path has no periodic capacity or
age eviction. Missing close records, ring loss, or short-lived process exits
can therefore retain paths and PID maps. This is a credible joint memory and
GC-CPU hypothesis for a weeks-long deployment, not yet a demonstrated cause.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §StoreFdPath; §RemoveFdPath; §OnStopping -->

### 4. FileOps aggregation is bounded but performs a locked full-table sweep twice per second by default

The aggregation table is capped and preserves fidelity by bypassing aggregation
when full. Its timer runs at half the aggregation window, with a 250 ms floor,
and scans all active keys while holding the same lock used by event absorption.
At high distinct-path cardinality, this is a CPU and contention candidate that
should be correlated with its existing entry-count and cap-bypass telemetry.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs §FlushExpired; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §StartSendWorker -->

### 5. Periodic cache/upload and process-retention work can produce cadence-aligned CPU bursts

The cache manager wakes every second and runs merge, recursive raw-sensor file
enumeration, and upload work on the configured upload interval. Process
retention periodically scans stale open rows, probes liveness, reads expired
rows into memory, and deletes them. Both paths are bounded operational work,
but their duration and file/table cardinality are not currently captured.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §WorkerThread_DoWork; §doMerge; §getRawSensorParquetFiles; ../wintap/wintap/core/infrastructure/ProcessResolver.cs §MaybeRunMaintenanceLocked; §ReconcileStaleOpenRowsLocked; §DeleteExpiredExitedRowsLocked -->

## Required Measurements Before Optimization

1. Capture a unique 24-72 hour baseline while preserving all currently enabled
   sensors, FileOps aggregation, Esper, and serializer behavior. Keep the
   existing root-wrapper/structured-counter capture; use a unique `RUN_ID`.

2. Add process-level CPU attribution at 1-second cadence: user/system CPU,
   voluntary and involuntary context switches, threads, read/write bytes, and
   fault rates. Pair it with `top -H` or `pidstat -t` samples so sustained CPU
   can be separated from one worker thread or timer callback.

3. Capture a short call-stack CPU profile during a representative window, then
   compare samples by cadence: continuous FileOps/EventChannel/DuckDB work,
   500 ms aggregation sweeps, 60 s serializer flushes, upload cycles, and
   five-minute resolver maintenance. Profiling observes behavior without
   changing event semantics or enabling loss.

4. Gate every performance conclusion on fidelity counters already emitted by
   FileOps: queue drops, queue high-water mark, ring failures, aggregation
   cap bypass, sender latency, resolution fallback/miss causes, and directory
   index evictions. A lower CPU result that creates drops is not an acceptable
   optimization result.

5. Add cheap periodic diagnostics before code-path changes: serializer queue
   depth/high-water and flush duration; FD-cache PID/entry cardinality; FileOps
   aggregation sweep duration; cache-cycle duration/file count/bytes; and
   resolver-maintenance duration/table counts. These are the missing signals
   needed to turn the findings above into attribution.

6. Run targeted, isolated reproduction workloads only after the baseline:
   short-lived `open -> exit` producers to test FD-cache retention, and a
   controlled file-heavy workload to compare CPU, managed heap, RSS, event
   counts, and zero-drop fidelity counters. Do not use a production degradation
   or disable FileOps as the primary experiment.

## Decision Rule

Do not optimize based only on the current 19% average CPU. First classify CPU
as continuous or cadence-bound, identify its dominant thread/call stack, and
prove the associated fidelity counters remain clean. Optimize the measured
dominant path, then repeat the same workload and compare CPU, drops, event
count/byte conservation, and long-run state cardinality.
