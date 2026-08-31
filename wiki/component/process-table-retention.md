---
title: "Process Table Retention & Reconciliation"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/BoundedEventTimeCache.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/tests/Wintap.Tests/ProcessResolverTests.cs
policy: agent-editable
last_validated: 2026-08-31
repo_scope: wintap
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: reviewed
source_paths: wiki/component/process-table-retention.md
tags: [wintap, lintap, process, retention, duckdb, cross-repo]
---

# Process Table Retention & Reconciliation

Promoted from [[wiki/work/fix-unbounded-process-table-growth/brief]]
(closed 2026-08-27). Bounds event_store process-table growth on long
runs while preserving PID-reuse-safe resolution.

The newer delayed-event identity-cache implementation is owned by sibling
`../wintap`; its durable commit anchor is pending as
`c03d731`. The live source paths above and
[[wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31]]
are the implementation and field-evidence anchors.

## Contracts (field-verified through 2026-08-27)

- **Resolver-owned lazy retention sweep**: exited process rows are
  retained briefly then swept; the table plateaus (~47-50k rows on
  spk16 vs the pre-feature 8M rows/10 days).
- **Liveness-based stale-open reconciliation**: open rows whose PID no
  longer exists are closed by sweep (`reconciled_closed` telemetry);
  `live_pids_missing_open_row == 0` is the health invariant.
- **QA telemetry is itself bounded**: `process_retention_telemetry` is
  aggregated/retained, not per-sweep-appended (the unbounded variant
  measurably cost host CPU).
- **CloneSensor thread filter**: `clone(2)` with `CLONE_THREAD` does not
  emit a process-start row — thread IDs are not process identities;
  fork/vfork and process-like clones still emit. Dropped open
  `python3.12`-style thread rows ~35x on the field host.
- **DuckDB read caveat**: the live DB cannot be opened read-only while
  Lintap holds the lock; query a copy (the diagnostics collector does).
- **Delayed-event identity cache**: File events that miss the active-process
  cache use a bounded LRU of closed process identities before querying DuckDB.
  Entries are selected by PID plus exact event-time interval, with newest
  matching create time winning for overlapping histories. Open-ended rows are
  never cached. Retention seeds the cache before deleting expired rows so a
  deep FileOps queue can still resolve events older than the process-table
  retention window. Default capacity is 32,768 entries and can be set with
  `WINTAP_PROCESS_HISTORICAL_IDENTITY_CACHE_ENTRIES`; zero disables retention
  while preserving miss accounting.
- **Timestamp precision**: event-time resolution and Stop/reconciliation writes
  use DuckDB parameters, preserving sub-second process boundaries used to guard
  PID reuse.
- The first deployed ten-minute gate observed `82.7%` historical-cache hits,
  `8750/32768` entries, and zero evictions. FileOps sender resolution averaged
  `445 us`, down from the pre-cache end-to-end sender average of `5136 us`.
- Extended validation then ran 10h23m with the cache continuously at capacity:
  `75.4%` aggregate hit rate, `394252` evictions, `547 us` average resolution,
  queue average/max `5206/17387`, and zero sender/summary/serializer loss. A
  final 6,000-file burst reached high-water `71802` and recovered below its
  pre-burst queue depth in the next interval.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §ResolveProcessIdentityAtTime; §DeleteExpiredExitedRowsLocked; §RegisterProcess; §ReconcileStartupOpenRows -->

## Verification

Milestone tests P1-P3 in [[wiki/work/optimize-fileops-poller/test_plan]]
(pytest harness, boundedness check via the diagnostics bundle, VM
long-run summarizer). Final long-run acceptance runs as
[[wiki/work/extended-deployment-monitoring/brief]].
The cache-specific 10h23m gate is recorded in
[[wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31]].
