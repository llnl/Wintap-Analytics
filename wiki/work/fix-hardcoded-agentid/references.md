---
title: "References: Fix Hardcoded AgentId"
type: concept
confidence: high
grounded_by:
  - ../wintap/linux-tcp-investigation-2026-06.md
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/shared/StateManager.cs
policy: agent-editable
last_validated: 2026-10-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: network
audience: developer
status: reviewed
source_paths: wiki/work/fix-hardcoded-agentid/references.md
tags: [feature-work, references, agentid, tcp]
---

# Feature References: Fix Hardcoded AgentId

## Live Repo Sources

- `../wintap/linux-tcp-investigation-2026-06.md` — June diagnosis and action
  list; historical source, not a current guide.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` — assigns the current
  AgentId before Esper/direct-parquet routing and limits unresolved-owner logs
  to one per PID.
- `../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs` — preserves
  the event AgentId and uses the shared platform-neutral watchdog copy.
- `../wintap/wintap/core/etl/extract/UdpPacketSerializer.cs` — uses the same
  shared contract.
- `../wintap/wintap/core/shared/StateManager.cs` — blank/invalid AgentId causes
  generation and persistence of a new GUID in the working-directory state file.
- `../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs` and
  `../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c`
  — current attachment, classification, and socket/PID behavior.

## Related Wiki Pages

- [[wiki/diagnostic/linux-tcp-investigation-2026-06]]
- [[wiki/event_type/network-events]]
- [[wiki/work/refactor-data-log-paths/verification]]
