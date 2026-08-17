---
title: "wpc-02 Sensor Core Notes"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/improve-windows-process-collection/brief.md
  - ../Wintap-Analytics/wiki/work/improve-windows-process-collection/references.md
  - ../Wintap-Analytics/wiki/work/improve-windows-process-collection/design.md
  - ../Wintap-Analytics/wiki/work/improve-windows-process-collection/implementation_plan.md
  - ../wintap/developer_docs/instructions/wpc-02-sensor-core.md
  - ../wintap/developer_docs/audits/wpc-02-sensor-core.md
  - ../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs
policy: agent-editable
last_validated: 2026-08-17
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: llm-agent
status: draft
source_paths: ../wintap/developer_docs/instructions/wpc-02-sensor-core.md; ../wintap/developer_docs/audits/wpc-02-sensor-core.md; ../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs; ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs; ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs
tags: [feature-work, process-events, etw, windows-sensor, pidhash, wpc]
---

# 2026-08-17 wpc-02 sensor core notes

Raw Engineer notes for drafting `developer_docs/instructions/wpc-02-sensor-core.md`.

- Architect requested a self-contained instruction for unit `wpc-02` of the
  improve-windows-process-collection feature.
- Required feature inputs read:
  - `wiki/work/improve-windows-process-collection/brief.md`
  - `wiki/work/improve-windows-process-collection/references.md`
  - `wiki/work/improve-windows-process-collection/design.md`
  - `wiki/work/improve-windows-process-collection/implementation_plan.md`
- Required wintap sources read:
  - `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs`
  - `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
  - `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs`
  - `../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs`
  - `../wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs`
  - `../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs`
  - `../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs`
  - `../wintap/wintap/core/infrastructure/EventChannel.cs`
  - `../wintap/wintap/core/infrastructure/ProcessResolver.cs`
  - `../wintap/wintap/core/shared/ProcessHash.cs`
- Unit is deliberately narrow: create `WindowsProcessSensor`, subscribe classic
  kernel ProcessStart/ProcessStop on the shared kernel parser, canonicalize live
  Start time from the ETW ProcessStart timestamp, use `ProcessResolver` as the
  single hot-path process identity store, and emit Start/Stop events. Runtime
  replacement of old sensors waits for wpc-06.
- Tests need a small internal seam because `ProcessTraceData`, live ETW, and
  resolver/emit side effects are not unit-test friendly. The instruction allows
  only minimal internal seams: resolver fallback delegate, emit delegate, and
  optional clock.
- Architect decision after draft review: choose option 1 for wpc-02 live Start
  timing — ETW ProcessStart timestamp is canonical. Do not use
  `OpenProcess`/`GetProcessTimes` on every process create because Wintap has
  treated ETW as process-start ground truth for over 13 years and the handle
  lookup hot-path cost is not justified.
- Architect follow-up decision: start with `ProcessResolver` on the sole hot
  path rather than introducing a sensor-owned in-memory PID map. Stops resolve
  identity through `EventChannel.GetProcessHistory` / `ProcessResolver`; misses
  are counted and fall back to hash-from-stop-time.
- Architect approved `../wintap/developer_docs/instructions/wpc-02-sensor-core.md`
  for Developer handoff on 2026-08-17 after the ETW timestamp and
  ProcessResolver hot-path revisions.
- Explicitly carried constraints: no `WintapMessage`/`ProcessObject` schema
  changes, no `PidHash` formula changes, TraceEvent remains 3.1.23, no new
  NuGet dependencies.
- Decision tension flagged in the draft: the older process-identity ADR says core
  owns PidHash/ParentPidHash generation, while the current WPC design and live
  sensor code require this Windows process sensor to compute `PidHash` using the
  unchanged formula and canonical create time. The draft follows the settled WPC
  unit request but does not broaden or resolve the older ADR.

## Implementation closeout

- Developer completed wpc-02 on 2026-08-17 and filed
  `../wintap/developer_docs/audits/wpc-02-sensor-core.md`.
- Created `../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs`
  and `../wintap/tests/Wintap.Tests/WindowsProcessSensorTests.cs`.
- Implemented the approved narrow core only: shared-kernel ProcessStart/Stop
  subscription, ETW timestamp canonicalization for live Start, resolver-backed
  Stop identity stamping, Stop resolver miss counting, and hash-from-stop-time
  fallback. The sensor is intentionally not wired into
  `WindowsSubscriptionManager` yet.
- Verification recorded by the audit: project-scoped Release build passed
  (`dotnet build "wintap\Wintap.csproj" -c Release -p:WarningLevel=0`) and
  `dotnet test --filter "Category=wpc-02"` selected and passed 5/5 tests from
  `tests/Wintap.Tests`.
- Deviation recorded by the audit: repo-root `dotnet build -c Release` and
  repo-root filtered test commands target `Wintap.sln`, which currently fails
  under .NET SDK MSBuild on the existing `Wintap-Workbench` website project
  (`MSB4249`). The Developer used project-scoped equivalents.
- Additional implementation detail: a narrow internal `genPidHash` constructor
  seam was added for tests so the wpc-02 unit tests do not initialize
  `StateManager` and trigger elevation-sensitive `diskpart.exe` behavior on the
  Windows host. Production defaults still call the unchanged
  `ProcessHash.GenPidHash(pid, fileTimeUtc)` formula.
