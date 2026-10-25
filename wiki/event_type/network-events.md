---
title: "Network Events"
type: event_type
confidence: high
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/UdpSensor.cs
  - ../wintap/wintap/core/etl/esper/tcp.epl
  - ../wintap/wintap/core/etl/esper/udp.epl
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/etl/transform/NetworkActivity.cs
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/wintap/core/etl/model/ProcessConnIncrData.cs
  - ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql
policy: agent-editable
last_validated: 2026-10-23
repo_scope: wintap
implementation_area: windows-sensor
event_domain: network
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/UdpSensor.cs; ../wintap/wintap/core/etl/esper/tcp.epl; ../wintap/wintap/core/etl/esper/udp.epl
tags: [network-events, telemetry-semantics, wintap-api]
---

# Network Events

**Identity is not direction:** [[wiki/concept/telemetry-identity-and-endpoint-orientation]]
explains `conn_id` alongside `pid_hash` and `agent_id`, including the same-IP,
same-process case and why a correct connection ID does not prove endpoint orientation.

Network telemetry is split into `TcpConnection` and `UdpPacket` Wintap message types. TCP events use `TcpConnectionObject` for endpoints, ports, packet size, state/window/sequence fields, and failure code; UDP events use `UdpPacketObject` for endpoints, ports, packet size, and failure code.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §TcpConnectionObject; §UdpPacketObject -->

## TCP Producer Semantics

The Windows `TcpSensor` consumes kernel TCP/IP ETW activity from the NT kernel logger using `NetworkTCPIP` flags. It registers IPv4 and IPv6 handlers for send/receive plus TCP connect, accept, reconnect, retransmit, disconnect, ACK/copy activity, and failures. ETW event names are converted into `ActivityTypeEnum` values by removing `/` and parsing the result.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs §Start; §getWintapTCPBuilder -->

For selected reversible event types, TCP source and destination endpoints are intentionally flipped before emission. The source comment marks this as a behavior that still needs verification against pcap.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs §Kernel_TcpIp_TypeGroup1_Handler; §Kernel_TcpIp_TypeGroup2_Handler -->

## UDP Producer Semantics

The Windows `UdpSensor` consumes UDP send, receive, and fail ETW events from the same `NetworkTCPIP` kernel flags. Send/receive events populate source address/port, destination address/port, and packet size, then send the normalized `UdpPacket` message to `EventChannel`.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/UdpSensor.cs §Start; §Kernel_UdpIpSendRecv -->

## ETL Boundary

TCP and UDP ETL both use the shared `Every10Seconds` Esper context. TCP aggregates by source/destination 5-tuple attributes, `PidHash`, process name, PID, activity type, and `AgentId`, emitting packet-size sums/min/max/squares, sequence information, first/last seen, and event count. UDP aggregates by tuple, `PidHash`, PID, process name, activity type, and `AgentId`, emitting packet-size sum, first/last seen, and event count.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/tcp.epl §query -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/udp.epl §query -->

## Analysis Implications

### Directed versus host-relative endpoints

`Source`/`Destination` describe the normalized producer's directed tuple; they
reverse with Send/Recv. `Local`/`Remote` describe the socket from the attributed
process's host perspective: receive/accept/TCP-copy use destination as local,
send/connect/disconnect use source as local. Shared `NetworkActivity` classifies
typed enum members, accepts legacy slash names at the string boundary, and rejects
unknown activities instead of silently assigning an outbound direction.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/NetworkActivity.cs §IsInbound; ../wintap/wintap/core/etl/transform/Transformer.cs §CreateProcessConn -->

The October fix corrects a shared Windows/Linux defect: matching `TcpIp/Recv`
against the producer's `TcpIpRecv` enum string previously misassigned receive
source as local. Windows ETW-specific tuple reversal remains unchanged and precedes
this shared host-relative normalization; these are two distinct boundaries.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs §getWintapTCPBuilder; §Kernel_TcpIp_TypeGroup1_Handler; ../wintap/wintap/core/etl/transform/Transformer.cs §CreateProcessConn -->

Recorded `ProcessConnIncrData` now additionally preserves `SourcePort` and
`DestinationPort`. Both endpoints can legitimately have the same IP, including
same-host traffic over a non-loopback interface. One process can also own both
socket ends: PID/PidHash and ConnId then coincide, while the directed ports and
host-relative socket ports distinguish roles. Never infer orientation from low
ports, IP inequality, or PID alone.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/model/ProcessConnIncrData.cs §SourcePort; §DestinationPort; ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs §SameIpSamePid_BothSocketRolesKeepDirectedProvenance -->

Wintappy's canonical DBT and legacy network SQL normalize slash/case spellings
before calculating activity counters, including IPv6 Send/Recv names. Existing
badly oriented parquet/database rows are not automatically repaired. Source/dest
grouping can still split directional rows even after Local/Remote is corrected;
connection/session reconstruction is a separate analysis concern. IPv6 name
classification does not certify the IPv4-oriented integer address representation.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintappy/wintappy/datautils/rawtostdview.sql §process_conn_incr; ../Wintappy/wintap_dbt/models/silver/process_net_conn.sql -->

Regression/live evidence: [[wiki/work/network-endpoint-normalization/verification]].


Downstream network rows are 10-second stream aggregates, not raw packet captures. Process attribution is added centrally by `EventChannel`, so gaps in process resolution can surface as unknown process names or fallback `PidHash` values.
<!-- SYNTHESIS: inferred from ../wintap/wintap/core/infrastructure/EventChannel.cs, ../wintap/wintap/core/etl/esper/tcp.epl, and ../wintap/wintap/core/etl/esper/udp.epl -->

See also [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] and [[wiki/repo/wintappy-pipeline-repo]] (downstream `process_net_conn`/`process_net_summary` DBT models).
