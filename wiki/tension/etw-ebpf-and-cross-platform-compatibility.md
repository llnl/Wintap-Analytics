---
title: "ETW, eBPF, and Cross-Platform Compatibility"
type: tension
confidence: medium
grounded_by:
  - ../wintap/README.md
  - ../wintap/documentation/wintap-developer-guide.md
  - ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../Lintap/README.md
  - ../Lintap/teletap/README.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: open
source_paths: ../wintap/README.md; ../wintap/documentation/wintap-developer-guide.md; ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs; ../Lintap/README.md; ../Lintap/teletap/README.md
resolution: null
poles:
  - "Use platform-native telemetry mechanisms such as Windows ETW and Linux eBPF/sysdig to preserve fidelity."
  - "Maintain a coherent Wintap semantic model so analytics can reason across process, file, and network events across platforms."
tags: [tension, windows-sensor, ebpf, cross-repo]
---

# ETW, eBPF, and Cross-Platform Compatibility

## Tension

Wintap has platform-specific builds and collectors for Windows, Linux, and macOS, while the core architecture still routes events through shared `EventChannel`, ETL, Parquet, plugins, and MCP layers.
<!-- GROUND_TRUTH: ../wintap/README.md §Platform Layout; §Architecture Summary -->

On Windows, `WindowsSubscriptionManager` starts ETW-based modeled sensors, dynamically loads configured sensors, handles generic ETW providers, and creates a shared kernel ETW listener with accumulated kernel flags. This is deeply tied to Windows ETW semantics.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs §Start -->

On Linux, the Wintap README says current Linux sensor work centers on eBPF tracers under the Wintap repo, while the Lintap README says the newer TeleTap/eBPF Lintap implementation has moved into Wintap and the Lintap repo retains support/post-processing and legacy sysdig playground material.
<!-- GROUND_TRUTH: ../wintap/README.md §Architecture Summary -->
<!-- GROUND_TRUTH: ../Lintap/README.md §Lintap -->

TeleTap output is expected to use canonical raw sensor Parquet layout, and the full ETL is documented outside the TeleTap directory in `Wintap-PyUtil/wintap_dbt`. That means cross-platform compatibility spans multiple repos and workflow stages.
<!-- GROUND_TRUTH: ../Lintap/teletap/README.md §Data output; §Full ETL with DBT -->

## Current Holding Pattern

Document platform-specific producer behavior separately from WintapAPI-normalized semantics. Treat Windows ETW behavior, Linux eBPF/sysdig behavior, raw sensor Parquet, and downstream standard views as distinct layers.
<!-- SYNTHESIS: inferred from ../wintap/documentation/wintap-developer-guide.md, ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs, and ../Lintap/teletap/README.md -->

## Prior Art Note

A brainstorming note suggests Sysmon for Linux as prior art for this exact tension: Microsoft's eBPF-based Sysmon port reportedly documents how Windows event concepts (Process Creation, Network Connection, FileCreateTime) were mapped onto Linux eBPF hooks. Unverified; see [[wiki/concept/agentic-ebpf-probe-development]].
<!-- SPECULATIVE: raw/Agentic_Coding_for_eBPF.md — unverified brainstorming claim; no source inspection of Sysmon for Linux yet -->
