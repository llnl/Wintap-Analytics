---
title: "Feature Brief: PowerShell ETW POC"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/interview.md
policy: agent-editable
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/brief.md
tags: [feature-work, powershell, etw, poc]
---

# PowerShell ETW POC

Opened and scope-confirmed 2026-10-28 on `feature-powershell-sensor`: inspect native
PowerShell ETW event shapes on this Windows machine before designing a Wintap
sensor. Investigate 5.1 and 7 where installed; embedded/remoting examples are optional,
not setup or coverage gates. Acceptance requires a repeatable procedure, provider/header/
payload findings, explicit unavailable/decoding gaps, private synthetic capture and
Architect review; no logging-policy, manifest, remoting, installation or sibling-code
changes are authorized. Amendment 1 permits native tools rather than a custom listener;
amendment 2 selects 4104-only derived XML/counts while retaining full ETL/XML and
unchanged collection traffic/loss. Do not promise literal keystrokes, complete scripts,
repeated-execution counts or universal availability. The local wrapper is tested and
5.1 findings inspected; the operator reports the focused rerun works, but that new
dataset is not independently reviewed. PowerShell 7 evidence and formal POC acceptance
remain open. Wintap owns eventual code; Analytics owns these artifacts. Estimates cover
only this POC; integration needs a separate approved scope. Continue via
[[wiki/work/powershell-sensor/dev_handoff]], [[wiki/work/powershell-sensor/verification]]
and [[wiki/decision/2026-10-28-powershell-etw-poc-boundary]].
