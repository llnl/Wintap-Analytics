---
title: "Dev Handoff: Fix Hardcoded AgentId"
type: concept
confidence: high
grounded_by:
  - wiki/work/fix-hardcoded-agentid/brief.md
  - wiki/work/fix-hardcoded-agentid/implementation_plan.md
policy: agent-editable
last_validated: 2026-10-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: network
audience: developer
status: reviewed
source_paths: wiki/work/fix-hardcoded-agentid/dev_handoff.md
tags: [feature-work, dev-handoff, agentid, tcp]
---

# Dev Handoff: Fix Hardcoded AgentId

> Historical handoff. Implementation and live validation are complete; see
> [[wiki/work/fix-hardcoded-agentid/verification]].

## Copy/Paste Prompt

Implement the approved `fix-hardcoded-agentid` feature on the existing
`fix/hardcoded-agentid` branch in `../wintap`. Before coding, read:

- `wiki/work/fix-hardcoded-agentid/{brief,references,implementation_plan,verification}.md`
- `wiki/diagnostic/linux-tcp-investigation-2026-06.md`
- `../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs`
- `../wintap/wintap/core/etl/extract/UdpPacketSerializer.cs`
- `../wintap/wintap/core/infrastructure/EventChannel.cs`
- `../wintap/wintap/core/shared/StateManager.cs`

Fix TCP AgentId propagation, platform-neutralize the shared network-idle
message, and sanitize only the tracked nested state template. Add focused tests.
Do not rewrite the existing Linux TCP attachment/PID/protocol/rundown design;
validate it instead. Profile before adding a bounded resolver negative cache.
Never modify a local untracked runtime `wintapstate.json`. Record all commands,
results, live-host constraints, and cache decision in verification; then update
the plan checklist and canonical diagnostic page.
