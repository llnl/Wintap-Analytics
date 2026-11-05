---
title: "To-Do: Capture and Model Process Listening Sockets"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql
  - wiki/event_type/network-events.md
policy: agent-editable
last_validated: 2026-11-05
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor/ebpf; ../wintap/shared/WintapAPI; ../Wintap-PyUtil/wintap_dbt/models/silver
tags: [todo, backlog, network-events, listening-sockets, telemetry-semantics, wintap, wintappy]
---

# To-Do: Capture and Model Process Listening Sockets

**Priority:** Untriaged — priority and platform scope remain undecided.
**State:** Open — intake finding; deep dive not started.
**Likely next step:** Promote to a cross-repo investigation that establishes the
desired listener semantics and inventories capture support per platform before
choosing event and DBT model changes.

## Finding

The inspected Linux network tracer knows the `TCP_LISTEN` state value, but its
network-operation enum has no listen operation. The attached
`inet_sock_set_state` tracepoint currently refreshes tuple-cache state rather than
emitting listener lifecycle events. A constant or observed state is therefore
not evidence that listening sockets are captured as process telemetry.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §enum net_op_type, trace_inet_sock_set_state; ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §Start -->

The shared Wintap API does define a generic `LISTEN` state and a
`TcpConnectionObject.State` field, but its activity enum has no explicit listen
activity. This type-level capacity is not evidence that a producer emits or
retains listener records. In the inspected Wintappy silver models,
`process_conn_incr` aggregates connection activity counts and
`process_net_conn` rolls those increments up; neither defines a process-owned
listening-socket relation or listener state interval.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ActivityTypeEnum, StateEnum, TcpConnectionObject; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql -->

The available evidence establishes a gap in these inspected paths, not uniform
absence across every platform or legacy pipeline. Capture parity and the
appropriate common representation remain to be investigated.

## Impact

Researchers cannot reliably ask which process owned a listening endpoint, when
it began or stopped listening, or whether it was still listening during a given
observation window using the inspected canonical DBT network outputs. A listener
has a local endpoint but no remote peer; treating it as an ordinary connected
flow risks corrupting connection counts and peer-oriented analysis.

A peerless TCP disconnect can be compatible with a listener close, but it is not
evidence that the listener was opened, nor proof that an accepted connection
closed. Keep listener lifecycle distinct from accepted-connection lifecycle.
[[wiki/event_type/network-events]]

## Open questions

- Is the desired output a lifecycle event stream, a point-in-time listener
  inventory, or both? What should downstream consumers infer between events?
- Which platforms and sensor backends are in scope, and what fidelity can each
  provide for TCP listeners?
- Should UDP bound sockets be represented separately from TCP sockets in the
  `LISTEN` state?
- What identity should associate a socket with a process across descriptor
  inheritance, shared sockets, process exit, and PID reuse?
- Which socket key and lifecycle transitions can reliably distinguish close,
  replacement, and endpoint reuse without conflating accepted child sockets?
- How should wildcard binds, IPv4/IPv6, address family, network namespace, and
  permission or capture-filter limitations be represented?
- Should listener records be a separate process-associated model rather than
  rows in the existing peer-oriented `process_net_conn` model?
- What compatibility expectations apply to raw sensor output, Wintap's shared
  message contract, and Wintappy's bronze/silver/gold models?

## Suggested deep-dive work

1. Inventory listen/bind and socket-state capture in each supported platform and
   distinguish raw kernel observations from normalized Wintap events.
2. Define listener identity, ownership, lifecycle, endpoint fields, and the
   semantics for missing or late close observations.
3. Decide whether TCP listeners and UDP bound endpoints are separate concepts,
   and whether the downstream representation is event-, interval-, or
   snapshot-oriented.
4. Design a process-associated model without treating a listener as a remote
   connection or inflating existing connection activity aggregates.
5. Build controlled workloads for open/listen/close, accept plus listener
   survival, process exit, inherited descriptors, endpoint reuse, wildcard
   binds, and IPv4/IPv6 where supported.
6. Validate process attribution and lifecycle completeness against independent
   socket observations, then quantify platform and kernel-version limitations.

## References

- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c`
  — Linux network operation types and socket-state tracepoint behavior.
- `../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs` — Linux
  network tracepoint/program attachment and event handling.
- `../wintap/shared/WintapAPI/WintapMessage.cs` — shared activity and TCP
  connection message contract.
- `../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql` and
  `process_net_conn.sql` — current activity-increment and connection rollup
  models.
- [[wiki/event_type/network-events]] — producer semantics, aggregation boundary,
  and listener-close versus accepted-connection distinction.

## Disposition

This is an intake item only. No priority, platform scope, event contract, DBT
model shape, schema change, or implementation has been approved. On promotion,
follow [[wiki/concept/llm-assisted-feature-workflow]] and link the resulting
work folder from [[wiki/todo/index]].
