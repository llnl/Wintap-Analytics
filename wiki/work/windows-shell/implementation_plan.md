---
title: "Implementation Plan: WindowsShell"
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
source_paths: wiki/work/windows-shell/implementation_plan.md
tags: [windows-shell, cooked-read, verification]
---

# WindowsShell Implementation Plan

Completed the Microsoft.Windows.Console.Host ETW replacement, attached-client decoding, cmd-only filtering, canonical lifetime guard and normal/direct recording integration. WindowsShellSensor=false is the only feature setting; the payload now contains only CommandText, SessionId and StartTime. The helper, IPC and polling implementation are removed. Build, 62 focused tests and 380 nearby regressions pass; see [[wiki/work/windows-shell/design]].

Next qualify the integrated service across sessions, persisted process/file joins, measured latency/resource use and live shutdown; track evidence in [[wiki/work/windows-shell/verification]]. Disabling WindowsShell stops collection. Local publishing does not qualify an installed-service deployment or release.
