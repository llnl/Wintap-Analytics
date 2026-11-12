---
title: "PowerShell ETW Sensor"
type: component
confidence: medium
grounded_by:
  - ../Wintap/documentation/powershell-sensor.md
  - ../Wintap/wintap/platform/windows/sensor/etw/PowerShellSensor.cs
  - ../Wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../Wintap/wintap/core/infrastructure/EventChannel.cs
  - ../Wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - ../Wintap/wintap/core/etl/extract/DefaultSerializer.cs
  - ../Wintap/wintap/core/etl/load/DirectParquetSink.cs
  - ../Wintap/shared/WintapAPI/WintapMessage.cs
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: ../Wintap/wintap/platform/windows/sensor/etw/PowerShellSensor.cs; ../Wintap/documentation/powershell-sensor.md
tags: [powershell, etw, windows-sensor, telemetry-semantics]
---

# PowerShell ETW Sensor

Wintap's `PowerShellSensor` is a native ETW collector for script-block observations.
Wintap owns the implementation; this repository owns the cross-repo documentation.
The sensor was added in Wintap commit `6add359` and is present on the inspected
`origin/feature/powershell-sensor` and `origin/develop` lines. As of 2026-11-12 it
was not present in Wintap `origin/main`; this status is about the Wintap source
branch, not whether the code is implemented. The October Analytics POC is retained
as historical evidence under [[wiki/work/powershell-sensor/brief]].

This is separate from [[wiki/component/windows-shell-sensor]], which collects
interactive `cmd.exe` input through Microsoft.Windows.Console.Host CookedRead
events. PowerShell's sensor consumes PowerShell-provider script-block ETW events;
neither sensor is a substitute for the other.

## Collection and lifecycle

The sensor defaults to disabled (`PowerShellSensor=false`). When enabled, it owns a
uniquely named real-time ETW session and subscribes to both the Windows PowerShell
and PowerShell Core providers. The subscription uses level 255 and all keywords;
the callback filters to event 4104, version 1 before materializing the payload.
Therefore the event-ID filter does not narrow provider traffic. Unsupported versions,
decode failures, unhandled events, counters, and ETW loss are reported through logs.
The sensor does not enable or change PowerShell logging policy, so event emission
depends on host policy and configuration.

The subscription manager discovers the sensor through the `PowerShellSensor`
setting and starts it after process snapshot/kernel initialization. It stops its
owned ETW session before joining the reader and releases the session after an
unexpected reader exit. Detailed lifecycle and setting behavior are grounded in
the Wintap source and implementation note.
<!-- GROUND_TRUTH: ../Wintap/wintap/platform/windows/sensor/etw/PowerShellSensor.cs; ../Wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs; ../Wintap/wintap/App.config -->

## Data path

Each accepted record is a `WintapMessage` with `MessageType=PowerShell` and
`ActivityType=EventWritten`. It enters `EventChannel` for the normal event-time
process-owner lookup and attribution-retry policy, then flows through the default
serializer without aggregation. Wintap documents the resulting stream as
`data/raw_sensor/raw_powershell`; the diagnostic direct-Parquet path also retains
PowerShell payload columns and performs owner lookup unless diagnostic settings
explicitly disable it.
<!-- GROUND_TRUTH: ../Wintap/wintap/core/infrastructure/EventChannel.cs; ../Wintap/wintap/core/infrastructure/AttributionRetryQueue.cs; ../Wintap/wintap/core/etl/extract/DefaultSerializer.cs; ../Wintap/wintap/core/etl/load/DirectParquetSink.cs; ../Wintap/documentation/powershell-sensor.md -->

The current Wintappy DBT bronze model directory has no PowerShell-specific staging
model. Collection and raw Parquet output therefore do not imply a PowerShell DBT
bronze/silver/gold model or analysis-ready contract. This is a downstream coverage
gap, not a claim that the raw stream cannot be queried directly.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/bronze/ -->

## Qualification and handling

Wintap provides managed tests for payload validation, event-time attribution,
registration retries, serializer behavior, and Parquet round trips, plus an optional
Windows-only synthetic ETW smoke harness. Those tests and the live harness were not
run as part of this Analytics documentation update. A live capture, ETW load/loss
qualification, and host-specific logging-policy check remain separate validation.

Script text can contain sensitive material; the default-off setting is significant.
Access, retention, and handling should be reviewed before enabling collection.
Event 4104 is a script-block observation, not proof of execution or of text typed by
a user. See [[wiki/event_type/powershell-events]] for the payload and semantic
contract, and [[wiki/work/powershell-sensor/verification]] for the historical POC
evidence and current verification boundary.

<!-- GROUND_TRUTH: ../Wintap/tests/Wintap.Tests/PowerShellSensorTests.cs; ../Wintap/devtools/Invoke-PowerShellSensorSmoke.ps1 -->
