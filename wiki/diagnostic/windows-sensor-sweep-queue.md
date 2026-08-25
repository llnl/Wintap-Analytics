---
title: "Windows Sensor Sweep Queue (Defects and Findings from windows-sensor-health-check)"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/WintapLogger.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/MemoryMapSensor.cs
  - ../wintap/wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs
  - ../wintap/tests/Wintap.Tests/EventChannelHealthWireInTests.cs
  - ../wintap/tests/Wintap.Tests/WindowsStateManagerDriveMapTests.cs
  - ../Wintap-Analytics/wiki/work/windows-sensor-health-check/design.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wintap/core/infrastructure; wintap/platform/windows/sensor; tests/Wintap.Tests
tags: [wintap, windows-sensor, sweep, defects, health-check, wintaplogger, testing, data-quality]
---

# Windows Sensor Sweep Queue

Consolidated defect/finding catalog from the `windows-sensor-health-check`
feature (closed 2026-08-25). **This is the opening backlog for the follow-on
per-sensor sweep feature** the Architect scoped at the health-check feature's
open (interview, 2026-08-24): "sweep through all non-process sensors for
Windows, evaluate them for efficiency and accuracy, fix any obvious bugs."
Fixing these was explicitly a non-goal of the health-check feature; the
health check exists to make them visible.

Sources: the feature's exploration/grounding passes
([[wiki/work/windows-sensor-health-check/design]]), the shc-02/shc-03 test
work, and the 2026-08-25 availability-anchor live run
([[wiki/work/windows-sensor-health-check/verification]]).

## Infrastructure defects

### 1. WintapLogger BackgroundWorker captures the caller's SynchronizationContext

`ComponentLogger`'s constructor starts an infinite-loop `BackgroundWorker`
(`_loggingThread.RunWorkerAsync()`, `WintapLogger.cs:174-176`) whose
completion plumbing captures the caller's `SynchronizationContext` at first
touch (via `AsyncOperationManager` inside `BackgroundWorker`). Under xUnit —
whose sync context limits concurrent operations — this hangs the test run:
the worker permanently occupies the context. It also permanently consumes a
ThreadPool worker in production.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapLogger.cs §ComponentLogger ctor lines 174-176 -->

**Proposed fix (Developer's, recorded as given, shc-03/shc-02 follow-up
notes):** replace the BackgroundWorker with a dedicated background thread or
cancellable task that does not capture the caller's sync context, terminates
and drains cleanly on `Close()`, doesn't permanently consume a ThreadPool
worker, and handles concurrent append/close safely.

### 2. WintapLogger live-log truncation by a second process

Any second process touching the `WintapLogger` singleton opens the live
`Wintap.log` with `FileMode.Create` + `FileShare.ReadWrite`
(`WintapLogger.cs:166`, the default `LogType.Overwrite` branch) — truncating
a running service's log; interleaved writers are also possible because the
share mode admits them. Observed risk in practice: any diagnostic tool or
test process that first-touches the logger while the service runs destroys
the service's live log.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapLogger.cs §ComponentLogger ctor line 166 -->

### 3. Standing test-writing guidance: redirect the data root before any WintapLogger touch

Not a code defect to fix but standing guidance until items 1–2 land: the
logger singleton binds to `Env.FileDataRoot` at first touch (and item 1's
sync-context capture happens at the same moment). **Test fixtures MUST call
`Env.SetDataRoot(<temp dir>)` before anything can touch
`WintapLogger.Log`** — otherwise tests write to ProgramData and can hang the
xUnit run. The established pattern (shc-03's `DriveMapFixture` and shc-02's
`EgressHealthFixture`, both `ICollectionFixture` with
`DisableParallelization = true`): create a unique temp dir, `Env.SetDataRoot(dataRoot)`,
then `WintapLogger.Log.Init()` (and for egress tests, first-touch
`EventChannel`/`DirectParquetSink` inside the fixture); on `Dispose`,
`Env.SetDataRoot(null)` and best-effort delete the temp dir.
<!-- GROUND_TRUTH: ../wintap/tests/Wintap.Tests/WindowsStateManagerDriveMapTests.cs §DriveMapFixture; ../wintap/tests/Wintap.Tests/EventChannelHealthWireInTests.cs §EgressHealthFixture -->

## Live findings from the health check

### 4. PID=-1 Refresh Process event egresses as ProcessName=Unknown (first real catch)

From the 2026-08-25 availability-anchor run: a Process-stream event with
`PID=-1`, `ActivityType=Refresh` egressed with `ProcessName=Unknown`
(`PidHashIsUnknownSentinel=false`), caught by the `process_unresolved`
check. Likely a `WindowsProcessSensor` snapshot-refresh artifact emitting a
placeholder/invalid PID row; root-cause in the sweep. This is the health
check's first genuine production catch.
<!-- GROUND_TRUTH: ../Wintap-Analytics/wiki/work/windows-sensor-health-check/verification.md §Availability anchor (verbatim log excerpt) -->
<!-- SYNTHESIS: PID=-1 + ActivityType=Refresh points at the WindowsProcessSensor snapshot-refresh path; unconfirmed until root-caused in the sweep -->

### 5. Cosmetic: SensorHealth lines report caller `[SensorHealthMonitor..ctor]`

The production log-sink lambda is created in `SensorHealthMonitor`'s
constructor, so `ComponentLogger.Append`'s `[CallerMemberName]` captures
`.ctor` for every SensorHealth line. Future polish: pass an explicit member
name through the sink so lines read e.g. `[SensorHealthMonitor.Flush]`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/health/SensorHealthMonitor.cs §CreateDefault; ../wintap/wintap/core/infrastructure/WintapLogger.cs §Append CallerMemberName -->

## Carry-over items from the feature's grounding passes

All recorded in [[wiki/work/windows-sensor-health-check/design]] with
ground-truth cites; consolidated here as the sweep's working list.

### 6. Ungated Registry CreateKey/DeleteKey/DeleteValue emit sites

`parseRegSetValue`/query paths are gated on `Path.StartsWith("registry")`,
but the CreateKey/DeleteKey/DeleteValue emit sites are ungated — a
`RegParents` entry whose parent chain was never rooted can egress as a
relative key fragment. The `path_unqualified` check now counts exactly
these; the sweep fixes the sensor.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs §parseRegCreateKCB/§parseRegSetValue/§sendRegEventToEsper -->

### 7. Dead `Serializer.Listen` direct SendEventBean — deletion candidate

`Serializer.cs:150` re-injects a WintapMessage into Esper via direct
`SendEventBean`; no callers anywhere in the repo, own TODO reads "do we
still need this?". Deliberately got no `Inspect` call in shc-02 (wiring
dead code would create a latent double-inspection path if revived). Delete
in the sweep.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Listen -->

### 8. WintapAlert self-PID silent drop

`Watchdog.sendWintapAlert` / `PluginExceptionHandler.SendWintapAlert`
construct WintapAlert messages carrying Wintap's own PID, which
`EventChannel.Send`'s first filter drops — self-generated alerts appear
silently discarded today.
<!-- SYNTHESIS: inferred from ../wintap/wintap/core/infrastructure/Watchdog.cs §sendWintapAlert and ../wintap/wintap/core/infrastructure/EventChannel.cs §Send self-PID filter -->

### 9. `TranslateTransientPath` WMI partition-number authority problem

`BaseWindowsSensor.TranslateTransientPath` parses a WMI **partition**
number where an NT **volume** number is needed — the same
wrong-namespace-authority class of bug shc-03 fixed in the drive map
(partition numbers ≠ HarddiskVolume numbers).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs §TranslateTransientPath -->

### 10. Consolidate QueryDosDevice usage with WindowsProcessSensor's P/Invoke

`WindowsProcessSensor.TryTranslateDevicePathToWin32Path` P/Invokes
`QueryDosDevice` per call, enumerating letters each time rather than using
the now-correct cached `StateManager.State.DriveMap` (rebuilt by shc-03).
Consolidation cleanup: one authoritative map, two consumers.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §TryTranslateDevicePathToWin32Path; ../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs §RefreshDriveMap -->

### 11. MemoryMapSensor: reroute through `EventChannel.Send`?

`MemoryMapSensor.cs:308` still bypasses `Send` via direct `SendEventBean`
(now health-inspected via the one-line `InspectForHealth` call shc-02
added, but still skipping AgentId tagging, the self-PID filter, and
enrichment). Open sweep question: reroute through `Send` proper, or
document the bypass as intentional.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/MemoryMapSensor.cs §308 -->

### 12. `eventtime_invalid` — candidate future health check

Dropped from health-check v1 by Architect review (amendment #2): EventTime
plausibility (> 0 and ≤ now + skew allowance). The check registry makes it
a drop-in; the anchor-run finding (item 4) shows raw FILETIME-style
`EventTime` values in samples, which the sweep may want to humanize too.
<!-- GROUND_TRUTH: ../Wintap-Analytics/wiki/work/windows-sensor-health-check/design.md §Alternatives Considered -->

## Related

- [[wiki/work/windows-sensor-health-check/design]] — grounding and provenance for items 6–12
- [[wiki/work/windows-sensor-health-check/verification]] — anchor-run evidence for item 4
- [[wiki/component/sensor-health-monitor]] — the shipped health-check layer these findings flow from
