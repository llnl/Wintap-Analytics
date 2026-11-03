---
title: "Feature References: WindowsShell"
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
source_paths: wiki/work/windows-shell/references.md
tags: [windows-shell, cooked-read, verification]
---

# WindowsShell References

Live Wintap sources are shared/WintapAPI/WintapMessage.cs for the payload, wintap/core/infrastructure/WindowsShellAttribution.cs and EventChannel.cs for lifetime association, and WindowsSubscriptionManager.cs plus the WindowsShell sensor and CookedRead decoder for subscription and cmd-only filtering. The supplied ETW prototype informs decoding; its private location and runtime evidence are omitted.

See [[wiki/component/windows-shell-sensor]], [[wiki/decision/process-identity-attribution-contract]] and [[wiki/concept/llm-assisted-feature-workflow]]. Machine-wide provider enablement with keyword 0x1000 differs from consumer-side cmd.exe filtering; enablement alone does not prove command delivery on a particular Windows build.
