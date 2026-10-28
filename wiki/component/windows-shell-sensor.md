---
title: "WindowsShell sensor"
type: component
confidence: medium
grounded_by:
  - ../Wintap/shared/WintapAPI/WintapMessage.cs
  - ../Wintap/wintap/core/infrastructure/WindowsShellAttribution.cs
  - ../Wintap/wintap/core/infrastructure/EventChannel.cs
  - ../Wintap/wintap/platform/windows/sensor/WindowsShellSensor.cs
  - ../Wintap/wintap/platform/windows/sensor/shell/WindowsShellCookedRead.cs
policy: agent-editable
last_validated: 2026-10-27
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/component/windows-shell-sensor.md
tags: [windows-shell, cooked-read, verification]
---

# WindowsShell Sensor

WindowsShell uses machine-wide CookedRead events from the Microsoft.Windows.Console.Host ETW provider with keyword 0x1000 and filters decoded attached clients to interactive cmd.exe. WindowsShellSensor=false is the only feature setting. Client PID and creation time identify the shell; EventTime comes from ETW, and the console-host header PID is not used as shell identity. Wintap owns the sensor/model; Analytics owns this documentation.

WintapMessage.WindowsShell contains CommandText, SessionId and canonical owning-process StartTime; EventChannel validates lifetime before assigning PidHash and ProcessName. EventTime is when the console reports submitted input, not execution or completion. Redundant executable, timestamp-method and history/polling fields are removed from new dynamic Parquet output; older files retain them. Live collection and a six-record staged Parquet batch are confirmed, but attribution drops and final dataset/joins still require validation in [[wiki/work/windows-shell/verification]].
