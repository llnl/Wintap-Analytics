---
title: "To-Do: Implement Periodic Process Refresh Listings on Windows and Linux"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs
  - ../wintap/wintap/core/infrastructure/PeriodicProcessRefreshScheduler.cs
  - ../wintap/wintap/core/etl/ETLConfig.json
  - ../wintap/tests/Lintap.Tests/PeriodicProcessRefreshSchedulerTests.cs
  - ../wintap/tests/Wintap.Tests/WindowsProcessStartupReconciliationTests.cs
  - ../wintap/developer_docs/audits/sfx-02-process-observation-refresh.md
policy: agent-editable
last_validated: 2026-11-22
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
tags: [todo, priority, process-events, refresh, polling, windows, linux, wintap]
---

# To-Do: Implement Periodic Process Refresh Listings on Windows and Linux

**Priority:** P1 — High (human-requested; current deployments do not provide the
intended periodic running-process inventory).
**State:** Promoted — implemented as an uncommitted source candidate with focused
synthetic qualification. Bounded Linux `live-02` accepts repaired periodic output;
native Windows remains open.
**Likely next step:** Run the agreed native Windows platform gate.

## Finding

The candidate now starts a shared periodic scheduler after each platform's startup
inventory boundary: Linux after successful rundown; Windows after bootstrap,
replay and snapshot-delta reconciliation have been attempted. Periodic Windows
inventory never clears or reconciles startup state.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs §Start; ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §StartPeriodicRefresh/RunPeriodicRefreshSnapshot; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §Start/RunSnapshot -->

The requested behavior is a periodic listing of all currently running processes
on both platforms, with a default cadence of once per hour and an intended
collection point approximately five minutes after the hour. The scheduler must
not be confused with serialization, upload, resolver-maintenance, or legacy
recovery-database intervals.
<!-- HUMAN-REQUESTED: periodic process refresh listing on both platforms, default hourly at approximately five minutes after the hour, conversation 2026-11-19. -->

## Implemented schedule contract

1. Scheduling is UTC-epoch aligned. Defaults are enabled, interval 60 minutes and
   offset 5 minutes, producing future `HH:05` boundaries. Completion computes the
   next future boundary, so missed ticks are not replayed in a burst.
2. Configuration is separate from serialization/upload/maintenance:
   `ProcessRefreshEnabled`, `ProcessRefreshIntervalMinutes`, and
   `ProcessRefreshOffsetMinutes`. Invalid interval/offset values fall back safely.
3. Existing platform snapshot producers retain PID plus canonical birth identity.
   Repeated inventories do not replace birth `EventTime` with scan time.
4. One inventory cannot overlap another. Disposal prevents new admission and waits
   for an active inventory; process exit/enumeration failures remain best-effort.
5. All rows in one inventory carry the userspace UTC scan start in
   `ObservationTimeFileTimeUtc`, `ObservationClockDomain = userspace-utc`, and the
   capture-run ID. Normal ETL also propagates envelope `ReceiveTime`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/PeriodicProcessRefreshScheduler.cs; ../wintap/wintap/core/etl/ETLConfig.json; ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent -->

## Qualification criteria

Synthetic status: UTC boundaries, custom interval/offset, disabled mode, overlap,
disposal waiting, repeated Linux identity/timing and a Windows periodic
identity/no-reconciliation case pass. Linux and Windows-targeted Release builds
pass with zero errors. The broader Linux-hosted Windows run is not acceptance;
native Windows and live resource/completeness evidence remain open.
<!-- GROUND_TRUTH: ../wintap/tests/Lintap.Tests/PeriodicProcessRefreshSchedulerTests.cs; ../wintap/tests/Lintap.Tests/ProcessObservationTimingTests.cs; ../wintap/tests/Wintap.Tests/WindowsProcessStartupReconciliationTests.cs -->

The authorized Linux `live-01` gate registered rundown/exec/clone, started two
periodic inventories at the configured two-minute UTC boundaries, and completed
graceful shutdown. A stable workload had three Refresh observations with one
birth/hash/run scope and three UTC scan times. One absent monotonic value became
numeric `0` in direct Parquet; the source repair is synthetically qualified, but
repaired-binary `live-02` confirms all 1,312 Refresh rows write null. It also
repeats the stable anchor and 8/8 multi-exec assertions without regression.

- Windows and Linux each produce a complete, bounded running-process listing at
  the selected schedule while live lifecycle collection continues normally.
- The default schedule is demonstrated at the agreed hourly boundary and is
  independently distinguishable from startup-only rundown and upload/flush work.
- Configured intervals and schedule offsets are covered by focused tests,
  including clock-boundary, missed-tick, restart, overlapping-run, and disabled
  cases.
- Repeated Refresh observations preserve the same process identity and do not
  inflate distinct process-creation counts.
- Logs/metrics and downstream output provide evidence of actual collection time;
  validation does not infer cadence from process birth `EventTime` alone.
- Windows and Linux resource impact, failure behavior, and partial-enumeration
  semantics are documented before deployment.

## Related context

- [[wiki/todo/process-observation-time-separate-from-birth]] tracks independent
  occurrence/observation timing while preserving canonical birth identity. The
  additive candidate now makes UTC scan-start time visible in normal ETL.
- [[wiki/event_type/process-events]] documents current Start/Refresh semantics and
  explains why Refresh is context rather than a new process creation.
- [[wiki/concept/durable-process-context-and-stream-table-enrichment]] and
  [[wiki/tension/refresh-republication-vs-durable-process-context]] capture the
  downstream volume, retention, and historical-context tradeoffs.

## Disposition

This item is promoted into
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief]]. Keep it open until
native Windows establishes platform behavior and its output evidence. The bounded
Linux output gate is complete but does not establish broad deployment resource
impact. No deployment or downstream model change is implied.
