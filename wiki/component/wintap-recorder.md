---
title: "WintapRecorder"
type: component
confidence: high
grounded_by:
  - ../wintap/platform/windows/WintapRecorder/MainWindow.xaml.cs
  - ../wintap/platform/windows/WintapRecorder/Session.cs
policy: agent-editable
last_validated: 2026-06-29
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/platform/windows/WintapRecorder
tags: [wintap, recorder, telemetry]
---

# WintapRecorder

WintapRecorder is a Windows UI workflow for managing recording sessions around Wintap telemetry. The main window lets users toggle configured collectors, clear the local streaming Parquet cache, start the Wintap sensor supervisor, monitor event/parquet/drop metrics, and finalize a collection.
<!-- GROUND_TRUTH: ../wintap/platform/windows/WintapRecorder/MainWindow.xaml.cs §MainWindow; §startBtn_Click; §Sensor_WintapMetric -->

A recording session starts after the process tree is ready. The recorder creates a `Session`, writes `Mode = Record` and `RecordStartTime` under `SOFTWARE\Wintap\Plugins\WintapETL\Sessions`, derives a session name from machine name and start time, and monitors streaming and merged Parquet counts.
<!-- GROUND_TRUTH: ../wintap/platform/windows/WintapRecorder/MainWindow.xaml.cs §Sensor_ProcessTreeReady -->
<!-- GROUND_TRUTH: ../wintap/platform/windows/WintapRecorder/Session.cs §Start; §SessionWorker_DoWork -->

On stop, the recorder waits for final Parquet flushes, invokes merge logic, removes session registry values, and runs `MergeHelper.exe` for each relevant sensor directory under the streaming Parquet cache.
<!-- GROUND_TRUTH: ../wintap/platform/windows/WintapRecorder/MainWindow.xaml.cs §stopBtn_Click; §FinalParquetWaitWorker_RunWorkerCompleted -->
<!-- GROUND_TRUTH: ../wintap/platform/windows/WintapRecorder/Session.cs §Stop; §Merge; §runCmdLine -->

## Analysis Role

WintapRecorder is not the telemetry model itself. Its wiki role is to document how recorded Parquet sessions are initiated, finalized, and merged for later replay or offline analysis.
<!-- SYNTHESIS: inferred from ../wintap/platform/windows/WintapRecorder/MainWindow.xaml.cs and ../wintap/platform/windows/WintapRecorder/Session.cs -->
