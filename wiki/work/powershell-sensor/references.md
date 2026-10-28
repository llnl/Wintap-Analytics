---
title: "References: PowerShell ETW POC"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/WindowsShellSensor.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/infrastructure/ProcessAttribution.cs
  - ../wintap/wintap/platform/windows/sensor/etw/GenericSensor.cs
policy: agent-editable
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/references.md
tags: [feature-work, powershell, etw, references]
---

# PowerShell ETW References

Live Wintap review at `99aadf6` found cmd.exe-only `WindowsShellSensor.cs`, no dedicated
PowerShell collector, core-owned attribution in `ProcessAttribution.cs`/`EventChannel.cs`,
and later integration points in `WintapMessage.cs`, `DefaultSerializer.cs` and
`DirectParquetSink.cs`; no sibling files changed. **Drift:**
[[wiki/component/windows-shell-sensor]] describes older paths/serialized StartTime;
reviewed code instead uses nonserialized lifetime evidence and a two-field shell
payload. Native sources: [PowerShell logging](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_logging_windows?view=powershell-7.5),
[logman](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/logman-create-trace)
and [tracerpt](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tracerpt).
Local metadata confirms 5.1 GUID `{A0C1853B-5C40-4B15-8766-3CF1C58F985A}`;
Microsoft documents Core GUID `{F90714A8-5509-434A-BF6D-B1624C8A19A2}`, but Core capture
is unverified and a failed name lookup is not installation-absence proof.
`(Get-WinEvent -ListProvider 'Microsoft-Windows-PowerShell').Events` supplies native
field templates; operator ETL/XML/summary/log remain private in the temporary prototype
directory. [[wiki/work/powershell-sensor/findings]] records inspected shapes and limits;
documentation of logging/manifest commands does not authorize using them.
