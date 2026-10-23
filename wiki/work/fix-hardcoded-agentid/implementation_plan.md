---
title: "Implementation Plan: Fix Hardcoded AgentId"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
policy: agent-editable
last_validated: 2026-10-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: network
audience: developer
status: reviewed
source_paths: wiki/work/fix-hardcoded-agentid/implementation_plan.md
tags: [feature-work, implementation-plan, agentid, tcp]
---

# Implementation Plan: Fix Hardcoded AgentId

## Steps

1. Add a test seam/coverage sufficient to assert that TCP serialized output
   retains the event AgentId; replace the literal with the event value.
2. Replace duplicated ETW-specific TCP/UDP watchdog copy with wording accurate
   for either producer platform.
3. Reset tracked `wintap/wintapstate.json` to `{"AgentId":""}` and add a
   guard that prevents a non-empty tracked template from returning.
4. Build and run focused tests plus existing Linux smoke-test static checks.
5. Profile repeated unresolved-owner lookup behavior. Implement a bounded
   negative cache only if the measurements demonstrate material cost; otherwise
   record the no-change result.
6. On the authorized Linux host, deploy a matched binary/tracer pair, collect
   bpftool attachment evidence, run the network smoke test and realistic TCP
   traffic, and query output for AgentId/lifecycle/attribution evidence.
7. Update verification, the diagnostic addendum, plan checklist, index, and log.

## Files Likely To Change

- `../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs`
- `../wintap/wintap/core/etl/extract/UdpPacketSerializer.cs`
- `../wintap/wintap/wintapstate.json`
- Wintap test project files as needed for regression coverage
- `wiki/work/fix-hardcoded-agentid/verification.md`

## Rollback Plan

Revert the focused Wintap commit(s). The state-template change is safe because
StateManager creates a replacement identity on first use; do not overwrite an
existing deployed runtime-state file.

## Done Checklist

- [x] TCP AgentId regression fixed and tested.
- [x] Platform-neutral watchdog copy fixed and tested.
- [x] Tracked state template sanitized and guarded.
- [x] Resolver-cache profiling decision recorded: no cache added.
- [x] Focused build/tests pass.
- [x] Linux attachment and smoke/live evidence recorded.
- [x] Wiki diagnostic/current status and log updated.
