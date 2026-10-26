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
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
policy: agent-editable
last_validated: 2026-10-25
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

## Linux CO-RE return contract

Current Wintap Linux core tracer emits IPv4 Accept at successful accept return with
accepting TGID and remote→local direction. UDP uses explicit kernel sockaddr provenance
and one successful protocol-function return owner per Send/Receive, including valid
zero-length datagrams; failed returns do not emit. This corrects old missing Accept /
kernel-vs-user Receive reads and duplicate partial syscall-entry sends **prospectively**.
The fallback tier and historical datasets do not inherit this core contract.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §kretprobe__inet_csk_accept, kretprobe__udp_sendmsg, kretprobe__udp_recvmsg, trace_sendto -->

UDP bytes mean successful protocol-function return, not final syscall copy-out success
or packet/byte conservation. TCP Send/Recv remain requested-entry and sampled. One-second
socket sampling remains for TCP Send/Recv, UDP Send and connected-bufferless Receive;
peer-buffer UDP receives remain unsampled. Local wildcard addresses are best-effort,
not proof of routable local IP. Consumers must retain per-operation contracts rather
than equating EventCount with packets/syscalls or treating listener Disconnect as an
accepted connection's fate. Version-gated startup facts and bounded VM qualification:
[[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]].
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §Start; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §kprobe__tcp_sendmsg, kprobe__tcp_recvmsg, kretprobe__udp_sendmsg, kretprobe__udp_recvmsg -->

### TCP tuple lifetime and EOF requests

The corrected Linux CO-RE state callback refreshes only existing cache entries
from complete live IPv4 tuples. It preserves their per-direction sample clocks
and never replaces a learned tuple with teardown's zero local port. Connect,
accept and data paths own cache creation; a state callback after `tcp_close`
cannot recreate the deleted entry. New connect attempts reset cached tuple state,
and close clears connection/owner entries even if the closing task is outside the
optional PID filter. Cache absence/capacity loss still limits recoverability; no
endpoint is inferred from a different socket or process.

An EOF `recv(1)` may therefore emit a correctly attributed request of **one byte**
when outside the sampling interval, despite returning **zero bytes**. This change
repairs tuple lifetime and sample-clock handling; it does not make TCP requested
bytes successful transfer counts. A listener close legitimately has no peer and
is distinct from an accepted connection's close. Consumers must keep both roles
and must not drop partial data rows merely to make validation pass. The new
`tcpTupleContractVersion=1` receipt marker is independent of UDP contract2.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §trace_inet_sock_set_state, kprobe__tcp_close, kprobe__tcp_recvmsg; ../wintap/devtools/network_trace_smoke_test.py §tcp_lifecycle_stimulus -->

### Shared aggregation boundary

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
