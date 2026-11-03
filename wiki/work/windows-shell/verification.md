---
title: "Verification: WindowsShell"
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
source_paths: wiki/work/windows-shell/verification.md
tags: [windows-shell, cooked-read, verification]
---

# WindowsShell Verification

Live service logs confirm Microsoft.Windows.Console.Host ETW collection, but exact comparison of OS creation time with ETW process-start time dropped every shell event before serialization. The corrected guard preserves canonical process identity and accepts bounded timestamp differences only with canonical hash integrity and a fresh OS lifetime check; exact source-hash matching also handles durable timestamp precision loss. All 62 focused tests and 380 nearby regressions pass, including dynamic Parquet roundtrip, skew and lifetime rejection cases.

Corrected self-contained Windows x64 binaries are published locally. The prior build produced a six-record staged WindowsShell Parquet batch, with four of ten submitted events dropped by attribution. Deployment of the reduced schema, final dataset and process joins remain pending; Terminal coverage, latency/resource use and live shutdown acceptance also require validation. CookedRead records submitted input, not execution success or complete command coverage.