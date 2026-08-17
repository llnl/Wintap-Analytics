---
title: "wpc-01 SID Helper Notes"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/improve-windows-process-collection/implementation_plan.md
  - ../wintap/developer_docs/instructions/wpc-01-sid-helper.md
  - ../wintap/developer_docs/audits/wpc-01-sid-helper.md
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs
  - ../wintap/tests/Wintap.Tests/WindowsProcessSidExtractionTests.cs
policy: agent-editable
last_validated: 2026-08-17
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: llm-agent
status: draft
source_paths: ../wintap/developer_docs/instructions/wpc-01-sid-helper.md; ../wintap/developer_docs/audits/wpc-01-sid-helper.md; ../wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs
tags: [feature-work, process-events, etw, windows-sensor, sid, wpc]
---

# 2026-08-17 wpc-01 SID helper notes

Raw Engineer notes for drafting `developer_docs/instructions/wpc-01-sid-helper.md`.

- Architect requested a self-contained instruction for unit `wpc-01` of the
  improve-windows-process-collection feature.
- Required inputs read:
  - `../Wintap-Analytics/wiki/work/improve-windows-process-collection/brief.md`
  - `../Wintap-Analytics/wiki/work/improve-windows-process-collection/references.md`
  - `../Wintap-Analytics/wiki/work/improve-windows-process-collection/design.md`
  - `../Wintap-Analytics/wiki/work/improve-windows-process-collection/implementation_plan.md`
  - `../sid-extraction-test/ProcessTraceDataExtensions.cs`
- Unit is deliberately narrow: port validated SID parser and tests only; no
  sensor wiring or user-name lookup.
- Potential test issue: `ProcessTraceData` is not easy to instantiate. The
  instruction therefore requires a pure payload parser seam so synthetic fixtures
  can exercise the offset math without ETW, elevation, or new packages.
- Constraints carried verbatim into the instruction: no WintapMessage/
  ProcessObject schema changes, no PidHash formula changes, TraceEvent remains
  3.1.23, no new NuGet dependencies.
