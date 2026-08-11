---
title: "Process Events"
type: event_type
confidence: high
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/etl/esper/process.epl
  - ../wintap/wintap/core/etl/esper/process-stop.epl
  - ../wintap/shared/WintapAPI/WintapMessage.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs; ../wintap/wintap/core/etl/esper/process.epl; ../wintap/wintap/core/etl/esper/process-stop.epl
tags: [process-events, telemetry-semantics, wintap-api]
---

# Process Events

Process events are normalized as `WintapMessage` records with `MessageType = Process` and a nested `ProcessObject` containing process identity, parent identity, path, command line, user, exit/resource fields, and hashes.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject -->

## Producer Semantics

The Windows `ProcessSensor` monitors the Security event log for Event IDs `4688` and `4689`. Event `4688` is treated as process creation and mapped to `ActivityType = Start`; Event `4689` is treated as termination and mapped to `ActivityType = Stop` when extracted. The start path constructs `PidHash` from PID and process create time and populates process name, path, command line, user, exit code, and parent PID.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs §startSecurityLogMonitoring; §ProcessSecurityLogEvent -->

On initialization, `ProcessSensor` reconstructs the active process tree from Security log events since boot, seeds system processes, clears the process database through `EventChannel.ClearProcessDB()`, and sends reconstructed records as `ActivityType = Refresh`. This makes process context available before non-process event attribution depends on it.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs §Initialize; §ReconstructProcessTreeFromSecurityLog -->

`EventChannel.Send` treats process events specially: it resolves parent process context when possible and registers process events with `IProcessResolver` unless skip flags are enabled. Non-process event attribution later depends on these registered process records.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->

## ETL Boundary

The process ETL query selects `Process` messages whose activity is `Start` or `Refresh`. A separate stop query selects `Process` messages with stop activity. This creates an explicit downstream distinction between current/known process context and process termination records.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/process.epl §query -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/process-stop.epl §query -->

## Analysis Implications

Process lineage is keyed by `PidHash` and `ParentPidHash`, not PID alone. PID reuse is handled by mixing PID with process time when generating hashes and by resolving parent/termination candidates against time windows during reconstruction.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs §FindParentProcess; §FindProcessInstanceForTermination -->

Security log retention matters. If the oldest Security log entry is newer than machine boot time, the sensor logs that a complete process tree cannot be built and a reboot is required.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs §Initialize; §GetOldestSecurityLogEntryTime -->

See also [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]], [[wiki/workflow/future-experiment-analysis-workflows]], and [[wiki/repo/wintappy-pipeline-repo]] (downstream `process`/`process_summary`/`process_uber_summary` DBT models).
