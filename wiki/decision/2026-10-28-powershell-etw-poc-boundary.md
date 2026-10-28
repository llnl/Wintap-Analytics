---
title: "Decision: PowerShell ETW-only POC before integration"
type: decision
confidence: medium
grounded_by:
  - ../Wintap-Analytics/wiki/work/powershell-sensor/interview.md
policy: human-review-required
last_validated: 2026-10-28
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: accepted
decided_on: 2026-10-28
source_paths: wiki/decision/2026-10-28-powershell-etw-poc-boundary.md
tags: [decision, powershell, etw, poc]
---

# PowerShell ETW POC Boundary

<!-- REVIEW NEEDED: Review this condensed transcription of Architect-confirmed decisions. -->

## Context
Discover native PowerShell event shapes before defining an integrated Wintap sensor.

## Decision
Use local native ETW tools under unchanged logging policy; investigate available 5.1/7 runtimes, treat embedded/remoting examples as optional, keep raw data private, and provide 4104-only derived XML/counts while retaining full originals.

## Rationale
Inspect actual provider fields without building a listener or exhaustive coverage harness; equivalent underlying listener events remain a working assumption.

## Consequences
Output filtering does not reduce collection traffic/loss or prove execution; no host-policy/remoting changes or sibling edits are authorized, and integration requires a separate Architect gate after [[wiki/work/powershell-sensor/brief]] acceptance.

## Alternatives Considered
Rejected non-ETW reconstruction and logging enablement; deferred custom event-ID filtering, immediate integration and universal input/coverage guarantees.
