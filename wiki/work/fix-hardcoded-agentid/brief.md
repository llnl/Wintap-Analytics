---
title: "Brief: Fix Hardcoded AgentId"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs
  - ../wintap/wintap/wintapstate.json
policy: agent-editable
last_validated: 2026-10-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: network
audience: mixed
status: reviewed
source_paths: wiki/work/fix-hardcoded-agentid/brief.md
tags: [feature-work, agentid, tcp, linux]
---

# Feature Brief: Fix Hardcoded AgentId

## Problem

Linux TCP parquet rows receive the literal AgentId `grantj` even though
EventChannel assigns every telemetry event the active sensor identity. A tracked
state template also contains a real AgentId. TCP/UDP idle warnings incorrectly
refer to an ETW provider on Linux.

## Goals

- Preserve EventChannel’s AgentId through TCP serialization.
- Sanitize the tracked `wintap/wintapstate.json` template without changing the
  untracked runtime state file.
- Make the shared TCP/UDP watchdog wording platform-neutral.
- Validate existing Linux TCP attachment, attribution, protocol-fallback, and
  rundown behavior with regression and live evidence.
- Preserve the investigation as a validated historical wiki diagnostic.

## Non-Goals

- Rewriting the existing TCP eBPF architecture.
- Changing telemetry schemas or historic recorded data.
- Implementing resolver negative caching without profiling evidence.
- Modifying an operator’s local runtime state.

## Acceptance Criteria

1. TCP serializer output uses the AgentId supplied by the processed event; no
   literal developer identity remains.
2. The sole tracked state template has an empty AgentId and a regression guard.
3. TCP and UDP idle notices do not claim Linux traffic is an ETW provider.
4. Automated tests cover the changed serializer/state/logging behavior.
5. A matched Linux binary/tracer deployment passes the network smoke test and
   records TCP lifecycle output with correct AgentId; `bpftool` evidence records
   the attached programs.
6. A resolver-cache decision cites measured repeated-miss cost; absent that
   evidence, no cache is added.

## Affected Areas

- `../wintap/wintap/core/etl/extract/{TcpConnectionSerializer,UdpPacketSerializer}.cs`
- `../wintap/wintap/wintapstate.json`
- Wintap tests and Linux network smoke/deployment evidence
- `wiki/diagnostic/linux-tcp-investigation-2026-06.md`

## Closure

All acceptance criteria passed on `lintap-dev`. The resolver profile did not
justify a negative cache without sustained live miss-rate evidence. See
[[wiki/work/fix-hardcoded-agentid/verification]] for the commands and results.

## Feature Artifacts

- [[wiki/work/fix-hardcoded-agentid/interview]]
- [[wiki/work/fix-hardcoded-agentid/references]]
- [[wiki/work/fix-hardcoded-agentid/implementation_plan]]
- [[wiki/work/fix-hardcoded-agentid/dev_handoff]]
- [[wiki/work/fix-hardcoded-agentid/verification]]
