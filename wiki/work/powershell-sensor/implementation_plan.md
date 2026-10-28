---
title: "Plan: PowerShell ETW POC"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/brief.md
  - ../Wintap-Analytics/wiki/work/powershell-sensor/dev_handoff.md
policy: agent-editable
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/implementation_plan.md
tags: [feature-work, powershell, etw, plan, poc]
---

# PowerShell ETW POC Plan

The approved [[wiki/work/powershell-sensor/brief]] is implemented as a temporary
logman/tracerpt wrapper, not a Wintap listener: build, -File path repair, 5.1 event-shape
inspection and 4104-only output filtering are complete; latest tests pass 35/35 and
existing-capture validation preserves originals. The operator reports the focused
rerun works, but its new dataset has not been independently reviewed. Follow
[[wiki/work/powershell-sensor/dev_handoff]] for commands and
[[wiki/work/powershell-sensor/verification]] for evidence. No installation, policy,
schema or sibling-code migration is authorized; recovery stops only owned sessions.
Next obtain Architect findings acceptance, then separately scope integration and any
PowerShell 7 or attribution work; do not turn optional examples into a coverage project.

- [x] Interview, wrapper, entry repair, first capture inspection and focused-output validation completed.
- [x] Operator reported focused rerun success; not independently verified.
- [ ] Architect accepts findings and records POC closeout; integration requires separate approval.
