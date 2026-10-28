---
title: "Feature Interview: PowerShell ETW Sensor"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/concept/llm-assisted-feature-workflow.md
  - ../Wintap-Analytics/wiki/decision/ai-velocity-roi-mini-lab.md
policy: agent-editable
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/powershell-sensor/interview.md
tags: [feature-work, powershell, etw, interview]
---

# PowerShell ETW Interview

On 2026-10-28 the Architect requested both interactive and script activity for Windows
PowerShell 5.1/7, a simple local POC before Wintap integration, and time estimates.
Confirmed constraints: native PowerShell ETW only, no logging-policy or implicit
remoting changes, synthetic full-payload capture kept private, and findings review
before integration. Embedded/remoting examples were included where available, then
clarified as optional: inspect event shapes, not exhaustive coverage or a custom
listener; assume the same underlying events in a later listener. The Architect
confirmed playback and POC-only estimate scope, then selected 4104-only derived output
with full originals retained and collection unchanged. No blanket sibling-code
authority was delegated; current decisions are distilled in
[[wiki/work/powershell-sensor/brief]] and [[wiki/work/powershell-sensor/references]].

## Sealed — human estimates

SEALED until closeout for independent estimators; this interviewer has already seen
the answers and records no independent estimate. After confirmed playback, Q1 asked
solo working hours and realistic availability date; answer verbatim: **"3-4 days"**.
Q2 asked AI-workflow availability date; answer verbatim: **"2-3 hours"**. Full response:
"1.  3-4 days   2. 2-3 hours". These are duration ranges, not specified working hours
or calendar dates: do not convert, invent midpoints or re-ask; missing data never gates
the feature. Protocol: [[wiki/decision/ai-velocity-roi-mini-lab]].
