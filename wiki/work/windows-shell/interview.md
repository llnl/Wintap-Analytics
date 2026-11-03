---
title: "Feature Interview: WindowsShell"
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
source_paths: wiki/work/windows-shell/interview.md
tags: [windows-shell, cooked-read, verification]
---

# WindowsShell Interview

The user confirmed interactive cmd.exe command lines, built-ins and compound text, canonical shell StartTime/PidHash, service collection across logged-in sessions and default-disabled configuration. The user subsequently requested complete replacement with the supplied Microsoft.Windows.Console.Host ETW approach and reports successful LocalSystem/session-0 prototype collection. This operator report does not independently qualify the integrated replacement; see [[wiki/work/windows-shell/brief]].

The optional solo estimate was not supplied. The AI-assisted delivery prediction was “With AI workflow, i think we can knock this out today.” Today meant 2026-10-27; this remains a prediction, not an availability result.
