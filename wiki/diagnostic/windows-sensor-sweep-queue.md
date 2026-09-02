---
title: "Windows Sensor Sweep Queue (Defects and Findings from Windows Sensor Features)"
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
  - ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/verification.md
  - ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/implementation_plan.md
  - ../wintap/wintap/core/etl/WintapETL.cs
  - ../wintap/wintap/core/etl/extract/RegistrySerializer.cs
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
health check exists to make them visible. Later features append here too
(items 13–14 from `improve-windows-registry-collection`'s live verification;
items 15–19 from that feature's 2026-08-25 close-out; item 6 resolved by its
wrc-06 rewrite).

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

### 6. Ungated Registry CreateKey/DeleteKey/DeleteValue emit sites — RESOLVED 2026-08-25 by wrc-06

`parseRegSetValue`/query paths were gated on `Path.StartsWith("registry")`,
but the CreateKey/DeleteKey/DeleteValue emit sites were ungated — a
`RegParents` entry whose parent chain was never rooted could egress as a
relative key fragment. **Resolved by construction in the
`improve-windows-registry-collection` rewrite (wrc-06):** the manifest-only
sensor takes full paths from the event's own `KeyName` (CreateKey:
`Join(BaseName, RelativeName)`) behind an `IsQualifiedRegistry`-mirroring
qualification gate — fragments are dropped, never emitted, and the legacy
parse/cache machinery (`RegParents` included) was deleted. Kept here as a
closed item; the `path_unqualified` check remains the regression watch.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs (post-wrc-06 rewrite); resolution recorded in ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/implementation_plan.md §wrc-06 -->

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

## Findings from improve-windows-registry-collection live verification (2026-08-25)

Recorded from the Architect-run wrc-07 live verification
([[wiki/work/improve-windows-registry-collection/verification]], 2026-08-25,
branch build `develop-wrc`). Queued here rather than handled in the wrc
feature: registry capture, canary health, and serialization were healthy in
the same run — these are adjacent-domain observations. Architect's verdict:
"The remaining concern is short-lived-process attribution rather than
registry capture or serialization."

### 13. Short-lived-process attribution burstiness on registry events

Process attribution of registry events is still bursty: unresolved registry
events ranged from 13/1,314 to 239/1,839 per batch, often dominated by one
short-lived PID. This is **process-tree/attribution-domain** work, NOT
registry capture — the registry events arrive correctly (full paths, decoded
data) but the owning process cannot be resolved before egress.
Cross-reference: the **ptr (process-tree-recovery) feature's territory**
(merged in `../wintap` 2026-08-22/23; its wiki fold-in is still owed per
`log.md`) — root-cause there or in the sweep, not in wrc.
<!-- GROUND_TRUTH: ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/verification.md §Live verification — Architect-run record -->

### 14. `stop_without_start` growth 3 → 19 over the observation window

Same run: the manifest metric `stop_without_start` rose from 3 to 19 —
occasional stop events arriving without a matching process record.
**Monitoring item, not currently severe** (Architect assessment: "Warrants
monitoring; not currently severe"). Likely related to item 13's short-lived
process races; evaluate together when root-causing.
<!-- GROUND_TRUTH: ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/verification.md §Live verification — Architect-run record -->

## Findings from improve-windows-registry-collection close-out (2026-08-25)

Cataloged at the wrc feature's close-out (feature accepted and closed
2026-08-25) from the feature's plan/instruction carry-overs — observed and
recorded during wrc work, deliberately not handled there.

### 15. Dead `RegWorker_DoWork`/`FileWorker_DoWork` handlers referencing nonexistent EPL files — deletion candidates

`WintapETL.cs:163-166` (`RegWorker_DoWork`) references a nonexistent
`reg-activity.epl` and has **no callers**; the sibling `FileWorker_DoWork`
(`WintapETL.cs:158-162`, `file-activity.epl`) is the same dead pattern.
Observed and recorded during wrc-08 grounding; explicitly out of that unit's
scope. Delete in the sweep (cf. item 7, the same dead-code class).
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/WintapETL.cs §RegWorker_DoWork/§FileWorker_DoWork (lines 158-166); recorded in ../wintap/developer_docs/instructions/wrc-08-parquet-value-plumbing.md §Out of Scope -->

### 16. Registry Read events carry `Data=""` / `DataType=NONE` — documented data gap, by design

The `Microsoft-Windows-Kernel-Registry` QueryValueKey payload has **no
`Type` field** (probe schema evidence), so its `CapturedData` cannot be
type-decoded, and the frozen wrc criteria forbade the legacy live-read/cache
fallback (TOCTOU). Read events therefore emit `Data=""`/`DataType=NONE` —
an Architect-approved documented limitation (wrc-06 approval stamp), NOT a
defect. Cataloged so the sweep does not "rediscover" it; any future fix
would need a different evidence source, not a sensor bug hunt.
<!-- GROUND_TRUTH: ../Wintap-Analytics/wiki/decision/registry-provider-strategy.md §mechanism record (QueryValueKey schema); wrc-06 approval recorded in ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/implementation_plan.md -->

### 17. Capture-flag reboot persistence and deliberate-clear semantics — documented unknowns (probe7 never run)

The provider capture flag is sticky global state; whether it survives
reboot and how to deliberately clear it (valid 4-byte descriptor with
flags=0) remain **documented unknowns** — probe7 was never run, by
Architect decision 2026-08-25. The shipped 5-minute periodic re-assert
covers both cases operationally regardless. Standing consequence for
deployment/uninstall docs: Wintap enables host-wide capture for this
provider and does not attempt to restore prior state. Revisit only if the
re-assert design ever changes.
<!-- GROUND_TRUTH: ../Wintap-Analytics/wiki/decision/registry-provider-strategy.md §Known unknowns; ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/interview.md §Playback (probe7 not run) -->

### 18. `Registry.PID` left unset upstream — retained legacy-parity wart

The rewritten sensor deliberately leaves `Registry.PID` unset (legacy
parity, retained at wrc-06 approval; the Architect may flip). Downstream,
the envelope `PID` is what the EPL/serializer use. Sweep call: set it or
delete the field.
<!-- GROUND_TRUTH: wrc-06 approval stamp recorded in ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/implementation_plan.md §status banner -->

### 19. Preserved registry EPL/serializer warts — cosmetic/consistency cleanup candidates

Deliberately preserved by wrc-08's existing-contract rule, cataloged as a
group: the `HostHame` column-name typo; the EPL selecting `AgentId` without
grouping it (NEsper leniency — not extended to the new fields);
`FirstSeenMs`/`LastSeenMs` naming vs. FileSerializer's
`FirstSeen`/`LastSeen`; `EventTime` derived from `FromFileTimeUtc(firstSeen)`
vs. FileSerializer's `GetUnixNowTime()`. Any fix is a breaking column-name/
semantics change for name-based consumers — batch them, version them, or
leave them; a sweep-level decision, not a drive-by.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/RegistrySerializer.cs §BuildFlatMessage; ../wintap/wintap/core/etl/esper/registry.epl; preserved-warts rule in ../wintap/developer_docs/instructions/wrc-08-parquet-value-plumbing.md -->

## Related

- [[wiki/work/windows-sensor-health-check/design]] — grounding and provenance for items 6–12
- [[wiki/work/windows-sensor-health-check/verification]] — anchor-run evidence for item 4
- [[wiki/work/improve-windows-registry-collection/verification]] — Architect-run record behind items 13–14
- [[wiki/work/improve-windows-registry-collection/implementation_plan]] — carry-over provenance for items 15–19 and the item-6 resolution
- [[wiki/component/registry-sensor]] — the rewritten sensor items 16–19 attach to
- [[wiki/component/sensor-health-monitor]] — the shipped health-check layer these findings flow from
