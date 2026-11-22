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
policy: agent-editable
last_validated: 2026-11-19
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
**State:** Open — intake finding; implementation and qualification have not started.
**Likely next step:** Promote this item into a feature-work folder, first defining
the schedule contract and collection-time observability, then implement and
qualify bounded periodic snapshots on both platforms.

## Finding

The current Windows `Refresh` path enumerates the live process snapshot during
sensor startup only. `WindowsSubscriptionManager` calls
`WindowsProcessSensor.InitializeSnapshotRefresh()` once before starting the live
ETW process sensor; no periodic snapshot timer is wired into that sensor.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs §Start; ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §InitializeSnapshotRefresh -->

The current Linux `ProcessRundownSensor` similarly enumerates `/proc` once from
`Start()`, emits `Refresh` messages for the processes it can read, and then
returns. It has no periodic timer or refresh interval configuration. Subsequent
process observations come from the live eBPF lifecycle sensors.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §Start; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §Start; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §EnumerateProcesses -->

The requested behavior is a periodic listing of all currently running processes
on both platforms, with a default cadence of once per hour and an intended
collection point approximately five minutes after the hour. The scheduler must
not be confused with serialization, upload, resolver-maintenance, or legacy
recovery-database intervals.
<!-- HUMAN-REQUESTED: periodic process refresh listing on both platforms, default hourly at approximately five minutes after the hour, conversation 2026-11-19. -->

## Implementation considerations

1. Define whether the schedule is based on UTC or local wall-clock time, whether
   “five minutes after” means a fixed minute (`HH:05`) or a bounded tolerance
   window, and how missed intervals after sleep/restart are handled.
2. Add an explicit, documented interval/schedule configuration with a safe hourly
   default. Preserve a clear enable/disable policy and avoid reusing unrelated
   `SerializationIntervalSec`, upload, or resolver-maintenance settings.
3. Reuse the existing platform snapshot producers: Windows process enumeration
   and exact process creation times; Linux `/proc` enumeration with canonical
   start-time handling. Keep process identity based on PID plus canonical birth
   time, not snapshot time.
4. Preserve Start-versus-Refresh deduplication and PID-reuse protections. A
   process that remains alive must not become a new identity merely because it
   was observed by a later refresh.
5. Make collection cadence observable. Refresh `EventTime` currently represents
   process birth time, so periodic collection must remain distinguishable through
   capture/receive metadata, explicit counters, logs, or another documented
   observation timestamp.
6. Bound snapshot cost and concurrency, handle processes that exit during
   enumeration, and ensure shutdown/restart cannot leave an active timer or
   overlapping full inventories.

## Qualification criteria

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

- [[wiki/event_type/process-events]] documents current Start/Refresh semantics and
  explains why Refresh is context rather than a new process creation.
- [[wiki/concept/durable-process-context-and-stream-table-enrichment]] and
  [[wiki/tension/refresh-republication-vs-durable-process-context]] capture the
  downstream volume, retention, and historical-context tradeoffs.

## Disposition

This is a high-priority implementation intake item, not authorization to modify
Wintap source, schemas, or downstream models. Promote it to a feature-work folder
after the schedule contract, compatibility boundaries, and validation plan are
approved.
