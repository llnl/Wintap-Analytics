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
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: windows-sensor
event_domain: network
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/UdpSensor.cs; ../wintap/wintap/core/etl/esper/tcp.epl; ../wintap/wintap/core/etl/esper/udp.epl
tags: [network-events, telemetry-semantics, wintap-api]
---

# Network Events

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

Downstream network rows are 10-second stream aggregates, not raw packet captures. Process attribution is added centrally by `EventChannel`, so gaps in process resolution can surface as unknown process names or fallback `PidHash` values.
<!-- SYNTHESIS: inferred from ../wintap/wintap/core/infrastructure/EventChannel.cs, ../wintap/wintap/core/etl/esper/tcp.epl, and ../wintap/wintap/core/etl/esper/udp.epl -->

See also [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] and [[wiki/repo/wintappy-pipeline-repo]] (downstream `process_net_conn`/`process_net_summary` DBT models).
