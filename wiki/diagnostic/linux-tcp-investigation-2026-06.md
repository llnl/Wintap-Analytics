---
title: "Linux TCP Capture Investigation (June 2026): Validated Current Status"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/linux-tcp-investigation-2026-06.md
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c
  - ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs
  - ../wintap/wintap/core/etl/load/ParquetWriter.cs
policy: agent-editable
last_validated: 2026-10-20
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: network
audience: developer
status: reviewed
source_paths: wiki/diagnostic/linux-tcp-investigation-2026-06.md
tags: [wintap, lintap, linux, ebpf, tcp, network-events, diagnostics]
---

# Linux TCP Capture Investigation (June 2026): Validated Current Status

## Source and Migration Status

This page is the Analytics-wiki home for the dated investigation originally
written at `../wintap/linux-tcp-investigation-2026-06.md`. The original remains
read-only because it is a live file in the Wintap repository. This page cites
and summarizes it rather than copying it, per the source policy.

The original memo describes a June 2026 RHEL 8 debugging session: UDP reached
the pipeline while TCP did not. It identified stale binary/tracer pairings and
incomplete eBPF attachment as likely causes, then listed follow-up defects.
<!-- GROUND_TRUTH: ../wintap/linux-tcp-investigation-2026-06.md §Problem Statement–§Action Items -->

## October 2026 Source Validation

| Memo claim / action | Current source status | Evidence / implication |
| --- | --- | --- |
| Binary/tracer skew can select a stale object from multiple search locations. | Current | `BaseEbpfSensor.FindBpfObject` still searches eight ordered locations. Deploy the managed binary and tracer together and inspect the selected candidate path. |
| TCP needs more than BaseEbpfSensor's primary-program attach. | Addressed in source; live regression still required | `NetworkSensor.Start` explicitly attaches the additional syscall, TCP lifecycle/send/recv, and UDP programs after the base attaches `trace_inet_sock_set_state`. The June all-program iteration was later replaced by an explicit compatibility list. |
| TCP lifecycle events need socket-keyed PID attribution instead of softirq-context current PID. | Addressed in source; live regression still required | The tracer has `sock_pid_map` keyed by socket pointer; it captures PID in connect/accept paths and uses it for the state tracepoint/lifecycle flow. |
| TCP protocol classification needs an operation-type fallback. | Addressed in source; live regression still required | `NetworkSensor.HandleEvent` classifies operation types 1–5 as TCP when `evt.Protocol` is unreliable. |
| TCP serializer contains a hardcoded `AgentId`. | Resolved and live-validated | `TcpConnectionSerializer` now retains `sensorEvent["AgentId"]` through the shared serializer contract. On `lintap-dev`, all 228 post-restart TCP raw rows used the active UUID and none used `grantj`. |
| A real AgentId is committed in the template state file. | Resolved | The tracked `wintap/wintapstate.json` is now `{"AgentId":""}` and a regression test guards it. StateManager generates and persists a new UUID when its AgentId is blank/invalid. The repository-root state file remains untracked runtime state and is out of scope. |
| Linux network-idle message says “ETW session provider.” | Resolved | TCP and UDP now use the shared platform-neutral network-event inactivity message, covered by regression tests. |
| Parquet writer needs generic null fallback and exception logging repair. | Already addressed | `DetermineSchemaFromExpando` defaults every null value to `typeof(string)` and interpolates the exception object. Do not duplicate this fix. |
| ProcessRundown must be enabled/documented. | Already addressed | `ConfigRoot.ProcessRundown` defaults to true and LinuxSubscriptionManager starts it unless explicitly disabled. |
| Repeated unresolved-owner warnings need a negative cache. | Resolved: no cache justified | EventChannel logs an unresolved owner once per PID. A 1,000-lookup DuckDB resolver profile measured 621.46 µs per unresolved durable lookup, but there is no live sustained-miss-rate evidence to outweigh the risk that a TTL negative cache masks a newly registered identity. |

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §FindBpfObject -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §Start; §HandleEvent -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §sock_pid_map; §trace_inet_sock_set_state -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs §HandleSensorEvent -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/ParquetWriter.cs §DetermineSchemaFromExpando -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ConfigManager.cs §ConfigRoot; ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §Start -->

## Required Live Validation

Source review cannot prove kernel attachment or event fidelity. The following
was completed on the authorized Multipass `lintap-dev` Ubuntu 24.04.5 / kernel
6.8 host: the package service was restarted with the rebuilt managed binary;
`bpftool` showed the lifecycle and connect/close programs attached; two rounds
of HTTP/HTTPS/UDP smoke traffic passed; and fresh staging/raw TCP output showed
the active AgentId with connect/send/receive/disconnect activity. See
[[wiki/work/fix-hardcoded-agentid/verification]] for commands and artifact
paths.

For a new target host, repeat:

1. inspect attached programs with `sudo bpftool prog list`;
2. run `devtools/network_capture_smoke_test.py` against the deployed data root;
3. generate realistic TCP activity beyond idle outbound HTTP;
4. verify TCP connect/send/receive/disconnect rows, owner attribution, and
   non-placeholder AgentId in raw output; and
5. retain the exact host/kernel, commands, output window, and artifact paths in
   [[wiki/work/fix-hardcoded-agentid/verification]].

## Follow-On Boundary

The `fix-hardcoded-agentid` feature fixes the active AgentId and watchdog
defects, sanitizes the tracked state template, and validates existing TCP
collection changes. A bounded resolver negative cache is permitted only after
profiling demonstrates repeat-miss lookup cost.
