---
title: "File Events"
type: event_type
confidence: high
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs
  - ../wintap/wintap/core/etl/esper/file.epl
  - ../wintap/shared/WintapAPI/WintapMessage.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: windows-sensor
event_domain: file
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs; ../wintap/wintap/core/etl/esper/file.epl
tags: [file-events, telemetry-semantics, wintap-api]
---

# File Events

File events are normalized as `WintapMessage` records with `MessageType = File`, `ActivityType` values such as `Read`, `Write`, `Close`, and `Delete`, and a nested `FileActivityObject` containing file path, bytes requested, and PID.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §FileActivityObject -->

## Producer Semantics

The Windows `FileSensor` consumes kernel FileIO ETW events from the NT kernel logger. It registers handlers for write, delete, name, create, close, and optionally read events when `CollectFileRead` is enabled.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs §Start -->

File paths may arrive indirectly through ETW file keys and file objects, so the sensor maintains a `fileKeyToPath` map. It processes a previous kernel rundown ETL file when present and then invokes `WintapCoreSvcMgr.exe RUNDOWN` to refresh file rundown information.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs §ProcessRundownTrace; §ExecuteEtwRundown -->

The sensor suppresses `.etl` paths and events from Wintap's own PID to avoid feedback loops with ETW internals and Wintap's own writes. Emitted paths are lowercased before sending to `EventChannel`.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs §sendFileEvent; §Kernel_FileIoWrite; §Kernel_FileIoDelete -->

## ETL Boundary

The file ETL query groups file messages in a 10-second time batch by file path, `PidHash`, PID, activity type, and process name. It emits bytes requested, first/last seen times, event count, message type, and `AgentId`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/file.epl §query -->

## Analysis Implications

Downstream file rows are aggregate activity records rather than one row per raw ETW callback. Analysts should treat byte counts and event counts as 10-second grouped observations tied to process attribution added by `EventChannel`.
<!-- SYNTHESIS: inferred from ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs and ../wintap/wintap/core/etl/esper/file.epl -->

Missing path resolution is possible when no rundown ETL exists or the ETW event lacks enough file-key context; the sensor logs that file events may not always contain a path in that case.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs §ProcessRundownTrace -->
