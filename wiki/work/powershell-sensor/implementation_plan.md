---
title: "Historical Plan: PowerShell ETW POC"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/brief.md
  - ../Wintap-Analytics/wiki/work/powershell-sensor/dev_handoff.md
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/implementation_plan.md
tags: [feature-work, powershell, etw, plan, poc]
---

# Historical PowerShell ETW POC Plan

> This plan tracks the separately scoped native-tool POC. It is not the
> implementation plan for the integrated Wintap sensor, which is recorded in
> [[wiki/component/powershell-sensor]] and
> [[wiki/event_type/powershell-events]].

The approved [[wiki/work/powershell-sensor/brief]] is implemented as a temporary
logman/tracerpt wrapper, not a Wintap listener: build, -File path repair, 5.1 event-shape
inspection and 4104-only output filtering are complete; latest tests pass 35/35 and
existing-capture validation preserves originals. The operator reports the focused
rerun works, but its new dataset has not been independently reviewed. Follow
[[wiki/work/powershell-sensor/dev_handoff]] for commands and
[[wiki/work/powershell-sensor/verification]] for evidence. No installation, policy,
schema or sibling-code migration is authorized; recovery stops only owned sessions.
The original POC findings-acceptance checkbox below remains open; later sensor
implementation does not retroactively close that POC gate. PowerShell 7 coverage,
live ETW qualification, and downstream DBT modeling remain separate questions.

- [x] Interview, wrapper, entry repair, first capture inspection and focused-output validation completed.
- [x] Operator reported focused rerun success; not independently verified.
- [ ] Architect accepts findings and records POC closeout; integration requires separate approval.
