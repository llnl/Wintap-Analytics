---
title: "Feature Design: WindowsShell"
type: concept
confidence: speculative
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
source_paths: wiki/work/windows-shell/design.md
tags: [windows-shell, cooked-read, verification]
---

# WindowsShell Design

An independent sensor subscribes to the machine-wide Microsoft.Windows.Console.Host ETW provider with CookedRead keyword 0x1000 and filters decoded attached clients to cmd.exe. Client PID and creation time supply source lifetime evidence; the ETW header console-host PID does not identify the shell. EventChannel validates the same canonical owner before assigning PidHash/ProcessName and StartTime for normal or direct egress.

WintapMessage.WindowsShell contains CommandText, SessionId and canonical owning-process StartTime. EventTime records when the console reports submitted input; it does not indicate execution or completion. ProcessName and PidHash remain in the standard envelope. Dynamic serialization writes the reduced windowsshell Parquet schema; older files retain removed columns, so readers spanning versions must tolerate missing fields. Existing flush/upload schedules apply.
