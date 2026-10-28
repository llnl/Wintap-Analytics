---
title: "Feature Brief: WindowsShell"
type: concept
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
source_paths: wiki/work/windows-shell/brief.md
tags: [windows-shell, cooked-read, verification]
---

# WindowsShell Brief

WindowsShell is a default-disabled Windows sensor for interactive cmd.exe command lines, including built-ins, external programs and compound text. Collection uses machine-wide CookedRead events from the Microsoft.Windows.Console.Host ETW provider with keyword 0x1000. EventTime is the ETW event timestamp; attached client PID and creation time identify the shell, rather than the console-host PID. PowerShell, batch execution and cmd /c coverage remain outside scope.

Acceptance requires service collection across user sessions, canonical StartTime/PidHash association, persisted process/file joins, measured latency/resource use and clean shutdown. The user reports successful LocalSystem/session-0 ETW prototype collection; independent integrated qualification remains pending in [[wiki/work/windows-shell/verification]].
