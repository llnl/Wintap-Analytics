---
title: "PowerShell Script-Block Events"
type: event_type
confidence: medium
grounded_by:
  - ../Wintap/documentation/powershell-sensor.md
  - ../Wintap/wintap/platform/windows/sensor/etw/PowerShellSensor.cs
  - ../Wintap/shared/WintapAPI/WintapMessage.cs
  - ../Wintap/wintap/core/infrastructure/EventChannel.cs
  - ../Wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - ../Wintap/wintap/core/etl/extract/DefaultSerializer.cs
  - ../Wintap/wintap/core/etl/load/DirectParquetSink.cs
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: ../Wintap/wintap/platform/windows/sensor/etw/PowerShellSensor.cs; ../Wintap/shared/WintapAPI/WintapMessage.cs
tags: [powershell, script-block, etw, process-events, telemetry-semantics]
---

# PowerShell Script-Block Events

Wintap models native PowerShell event **4104, version 1** from both Windows
PowerShell and PowerShell Core providers. These are process-attributed script-block
observations, not keystroke records. Producer configuration and lifecycle are
documented in [[wiki/component/powershell-sensor]]. This event stream is distinct
from the `cmd.exe` CookedRead observations documented in
[[wiki/component/windows-shell-sensor]].

## Envelope and payload

| Field | Meaning |
|---|---|
| `MessageType` | `PowerShell` |
| `ActivityType` | `EventWritten` |
| `EventTime` | Native ETW event timestamp represented as UTC FILETIME |
| `PID` / `ThreadId` | Emitting process / ETW thread |
| `ActivityId` / `CorrelationId` | Native activity and related-activity GUIDs when present |
| `ProviderGuid` | Windows PowerShell or PowerShell Core provider identity |
| `EventId` / `Version` | 4104 / 1 |
| `MessageNumber` / `MessageTotal` | Native script-block fragment index and reported total |
| `ScriptBlockId` | Native script-block identifier |
| `ScriptBlockText` | Decoded fragment text, retaining Unicode and line endings |
| `Path` | Native path; may be empty and retains source case |

Windows PowerShell uses provider GUID `a0c1853b-5c40-4b15-8766-3cf1c58f985a`;
PowerShell Core uses `f90714a8-5509-434a-bf6d-b1624c8a19a2`.

The standard processing pipeline supplies canonical `PidHash`, `ProcessName`, and
`AgentId`; they are not inferred from script text or activity IDs. PowerShell uses
the emitting ETW PID and ordinary event-time owner resolution, including bounded
retries for process-registration races. Embedded PowerShell hosts are not excluded
by executable name. Retry exhaustion follows the existing unknown-owner policy.
<!-- GROUND_TRUTH: ../Wintap/wintap/platform/windows/sensor/etw/PowerShellSensor.cs; ../Wintap/wintap/core/infrastructure/EventChannel.cs; ../Wintap/wintap/core/infrastructure/AttributionRetryQueue.cs -->

## Observation semantics and limits

Fragments and duplicate ETW records remain separate observations. Wintap does not
assemble fragments, deduplicate repeated observations, or derive an execution count.
A 4104 record alone does not establish that the text executed, that a user typed it,
or that one observation corresponds to one complete script. Empty text/path and
incomplete fragment sets may occur. Event availability and completeness depend on
host logging/provider configuration and ETW delivery; subscribing to the providers
does not itself prove that script-block events are emitted.

Invalid payloads, unsupported versions, decoder failures, and over-limit values
are rejected or counted rather than silently treated as complete coverage. The
current sensor documentation describes limits of 64 decoded fields, 256 KiB of
event data, 65,536 text characters, and 32,768 path characters.
<!-- GROUND_TRUTH: ../Wintap/documentation/powershell-sensor.md; ../Wintap/wintap/platform/windows/sensor/etw/PowerShellSensor.cs -->

## Storage and downstream analysis

The default serializer writes the unaggregated `PowerShell` stream to raw Parquet
under `raw_sensor/raw_powershell`; the diagnostic direct sink uses prefixed payload
columns. As of this review, Wintappy's `wintap_dbt/models/bronze/` contains no
PowerShell-specific staging model. No PowerShell-specific DBT staging or curated
schema is documented here; analysts should inspect the actual raw schema and
explicitly account for fragments, duplicates, attribution gaps, and sensitivity.
<!-- GROUND_TRUTH: ../Wintap/wintap/core/etl/extract/DefaultSerializer.cs; ../Wintap/wintap/core/etl/load/DirectParquetSink.cs; ../Wintap-PyUtil/wintap_dbt/models/bronze/ -->

The earlier native-tool capture and its observed event shapes are preserved in
[[wiki/work/powershell-sensor/findings]] and
[[wiki/work/powershell-sensor/verification]]. That capture was a POC dataset, not
a completeness or production-load qualification of the later integrated sensor.
