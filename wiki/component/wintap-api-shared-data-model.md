---
title: "WintapAPI Shared Data Model"
type: component
confidence: high
grounded_by:
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/shared/WintapAPI/Interfaces.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: wintap-api
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/shared/WintapAPI; ../wintap/wintap/core/infrastructure/EventChannel.cs
tags: [wintap-api, telemetry-semantics, data-model]
---

# WintapAPI Shared Data Model

`WintapMessage` is the normalized event envelope used across Wintap. It carries common metadata such as `MessageType`, `EventTime`, `ReceiveTime`, `PID`, `PidHash`, `ProcessName`, `ProcessPath`, `ActivityType`, correlation identifiers, `AgentId`, and one domain object such as `Process`, `TcpConnection`, `UdpPacket`, `File`, `Registry`, `ImageLoad`, `EventLogEvent`, `ApiCall`, `MemoryMap`, `Sysdig`, or `WintapAlert`.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §WintapMessage -->

The model is intentionally cross-domain. `MessageTypeEnum` includes process, thread, TCP, UDP, file, registry, module, UI/session, API/WMI, CPU, memory, group policy, event log, generic message, alert, and Linux `Sysdig` event types. `ActivityTypeEnum` holds lifecycle verbs, file verbs, registry verbs, TCP/UDP ETW activity names, API-call-like actions, and memory activity names.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §MessageTypeEnum and ActivityTypeEnum -->

## Domain Objects

Process events use `ProcessObject` fields for parent PID/hash/name, executable name/path, command line, user, exit and resource counters, hashes, and process keys. Network events use `TcpConnectionObject` and `UdpPacketObject` for endpoint addresses, ports, packet size, state/failure fields, and TCP sequence/window metadata. File events use `FileActivityObject` for path, bytes requested, and PID.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject; §TcpConnectionObject; §UdpPacketObject; §FileActivityObject -->

`WintapBase.ToDynamic()` converts nested object properties into an `ExpandoObject` and stringifies enum values for Parquet compatibility. This matters because downstream ETL pages should distinguish source enum semantics from serialized Parquet strings.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §WintapBase.ToDynamic -->

## Plugin/API Contracts

`Interfaces.cs` defines the public plugin-facing contracts. `ISubscribe` consumes modeled `WintapMessage` events selected by `EventFlags`; `ISubscribeEtw` consumes raw/unmodeled ETW providers; `IRun` supports scheduled runner plugins; `IQuery` registers Esper queries and receives query results; `IProvide` emits plugin-generated events; `IProvideMCP` allows plugin-specific MCP servers; `IInfer` exposes AI inference and MCP tool access to plugins.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/Interfaces.cs §PLUGIN INTERFACES -->

## Enrichment Boundary

`EventChannel.Send` is the main runtime boundary where raw producer events become normalized, enriched Wintap events. It drops Wintap's own process events, tags events with `AgentId`, resolves process ownership for non-process events, resolves parent context for process events, registers process events with the process resolver, and sends the final event to Esper unless direct Parquet or skip flags are enabled.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §EVENT ROUTING & ENRICHMENT -->

## Downstream Consumption

`WintapMessage` events serialized to `raw_sensor` parquet are the canonical input contract for Wintappy's DBT bronze/silver/gold pipeline, which normalizes them further into process-centric analysis models. See [[wiki/repo/wintappy-pipeline-repo]].
<!-- SYNTHESIS: inferred from ../wintap/shared/WintapAPI/WintapMessage.cs and ../Wintappy/review-notes/DataModel.md -->

See also [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]] and [[wiki/pipeline/nesper-esper-event-stream-processing]].
