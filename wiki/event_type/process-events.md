---
title: "Process Events"
type: event_type
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/task_start_boottime.h
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/BootProcessTraceHelper.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/etl/esper/process.epl
  - ../wintap/wintap/core/etl/esper/process-stop.epl
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/etl/extract/ProcessSerializer.cs
  - ../wintap/wintap/core/etl/model/ProcessObjectModel.cs
  - ../wintap/wintap/core/infrastructure/PeriodicProcessRefreshScheduler.cs
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs
  - ../wintap/tests/Lintap.Tests/ProcessObservationTimingTests.cs
  - ../wintap/tests/Lintap.Tests/PeriodicProcessRefreshSchedulerTests.cs
  - ../wintap/tests/Lintap.Tests/ProcessCommandLineQualityTests.cs
  - ../wintap/tests/Lintap.Tests/ProcessExecutionObservationTests.cs
  - ../wintap/tests/Wintap.Tests/TelemetryProjectionQualityTests.cs
policy: agent-editable
last_validated: 2026-11-22
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs; ../wintap/wintap/core/etl/esper/process.epl; ../wintap/wintap/core/etl/esper/process-stop.epl
tags: [process-events, telemetry-semantics, wintap-api, etw]
---

# Process Events

Foundational identity reference: [[wiki/concept/telemetry-identity-and-endpoint-orientation]]
distinguishes `pid_hash` from reusable OS PID, collector `agent_id`, and network
`conn_id`. The clarified contract excludes agent UUID from process identity and
requires one formula definition: [[wiki/decision/process-hash-inputs-and-single-definition]].
The `pid-v2` source patch implements this; installed packages and historical
recordings remain unmigrated. Verification: [[wiki/work/host-process-identity-patch/verification]].

## Linux clone/exec boundary (validated 2026-10-22)

Future investigation and separately qualified 2026-11-03 `develop` source baseline:
[[wiki/work/lintap-process-creation-validation/future-scheduler-lifecycle-vs-syscalls]].
It compares the existing scheduler/syscall hybrid, exec-attempt versus image
semantics, group-aware termination and measured acquisition-to-ETL costs.

Current Debian/RPM package templates enable Clone by default, retaining explicit
`WINTAP_ENABLE_CLONE_SENSOR=false` opt-out. Existing locally opted-out installs
are not automatically changed. Per-run HOST records identify effective enablement,
selected tier and hook outcomes: [[wiki/schema/runtime-capability-receipt]].
Package validation and separate RHEL gate:
[[wiki/work/clone-default-true/verification]].
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/lintap.env; ../Lintap/packaging/lintap-rpm/lintap.env -->

Linux `CloneSensor` prefers `clone_core_tracer.bpf.o`: a raw sched-fork hook
reads child pid/tgid, excludes thread births, and emits parent TGID. Its
tracepoint-only fallback captures best-effort clone/clone3 flags; absent auxiliary
hooks remain a thread-as-process risk. This does not alter Windows producers.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §BpfObjectFileName; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c §trace_process_fork -->

The Clone and Exit CO-RE objects share a start-boottime reader that probes
`task_struct.start_boottime`, then the RHEL 8 BTF spelling
`task_struct.real_start_time`; it returns zero if neither field exists. This
keeps the optional field check compilable when the build host's generated
`vmlinux.h` contains only one spelling. On RHEL 8.10 x86_64, both CO-RE objects
and a self-contained RPM built successfully; this was a compile/package test,
not a BPF load/attach or live-capture qualification.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/task_start_boottime.h; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c §trace_process_fork; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c §trace_process_exit -->

Fork and exec are separate Start observations, not necessarily separate identities:
the Ubuntu arm64 workload produced fork + exec-entry + sched-exec rows sharing
one PidHash. Clone birth metadata is provisional; `PROC_START_SRC=sched_fork`
prevents a late clone upsert from overwriting an existing resolver identity or
reviving its cache after Stop. Raw rows are not suppressed. Count identities rather
than Start rows for process counts. Normal ETL now persists the bounded producer
breadcrumb as nullable `ProcessStartSource`, rather than copying Arguments or
decorating CommandLine. Validation scope and remaining risks:
[[wiki/work/improve-lintap-data-quality/clone-validation-results]].
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §UpsertProcessStart; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent -->

The committed sensor-fix milestone selects Linux process names from
resolved executable evidence, otherwise observed `comm`, otherwise `unknown`.
An unresolved `/proc/<pid>/exe` alias is not executable evidence, and producers
do not infer paths from flattened command lines. A real executable named `exe`,
case and embedded spaces remain valid. Focused synthetic/ETL coverage passes;
bounded Linux `live-01` executable-name evidence passed all 8/8 multi-exec cases.
Historical affected-row lineage remains open, and the repaired binary still needs
a fresh capture for the independent direct-Parquet timing gate.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcessSensorHelper.cs; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs -->

Linux command-line capture now labels the existing rendered value with
`CommandLineSource=procfs-cmdline` and one of `captured`, `empty`, `unavailable`,
`read-error`, or `truncated`. Reads are bounded at 256 KiB; truncated strings end
at a complete NUL-delimited argument. Exec and Refresh carry their own procfs
observation, and clone never substitutes parent text for missing/empty child data.
These fields describe observation quality, not immutable syscall-entry argv or
successful image replacement.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §ReadCommandLineFile; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §SelectCommandLineMetadata; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §CreateRefreshMessage -->

Linux exec rows now distinguish request from installed image explicitly.
`ExecutionObservationKind=exec_attempt` marks execve/execveat syscall entry and
does not assert an outcome. `exec_success` marks `sched_process_exec`, which is
emitted after successful image installation. Clone, Refresh and unsupported
producers leave the field null. Both remain existing Start observations under one
birth-based identity; the field does not create a new lifecycle or executable
selection policy.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §GetExecutionObservationKind, HandleEvent; ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject -->

Process events are normalized as `WintapMessage` records with `MessageType = Process` and a nested `ProcessObject` containing process identity, parent identity, path, command line, user, exit/resource fields, and hashes. The schema and the PidHash formula (PID + create-time FileTime) were unchanged by the 2026-08 collection overhaul — all improvements below are population-rate and correctness improvements of existing fields.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject -->

## Producer Semantics (unified WindowsProcessSensor, 2026-08)

As of the improve-windows-process-collection feature (wintap `develop-dave`, commits 9862131…19e89dc, closed 2026-08-19), a single `WindowsProcessSensor` owns Windows process lifecycle. It replaced the Security-log `ProcessSensor` (event 4688/4689) and the separate `KernelProcessSensor`; both were deleted, and **process telemetry no longer depends on Security-log audit policy**. Design and decision history: [[wiki/work/improve-windows-process-collection/design]], [[wiki/work/improve-windows-process-collection/implementation_plan]]; per-unit evidence in `../wintap/developer_docs/audits/wpc-01…wpc-09`.

### Live Start/Stop — classic kernel ETW on the shared session

Real-time lifecycle comes from classic NT Kernel Logger ProcessStart/ProcessStop events on the shared kernel session (`Keywords.Process`), with `WindowsProcessSensor` started first by `WindowsSubscriptionManager` because non-process attribution depends on it.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs §Start -->

The **ETW ProcessStart timestamp is canonical** for live Start create time and therefore for `PidHash` — no per-Start `OpenProcess`/`GetProcessTimes` handle lookup (Architect decision 2026-08-17; ETW has been Wintap's process-start ground truth for over a decade). Stops resolve identity through `ProcessResolver` (the sole hot-path identity store — no sensor-owned PID map); resolver misses are counted. The `pid-v2` patch replaces the earlier hash-from-stop-time fallback with the explicit unknown identity: Stop time is not process-start time.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §EmitStart; §EmitStop -->

### Refresh — startup reconciliation and periodic inventory

At startup the Windows sensor preserves its bootstrap/replay/snapshot-delta
reconciliation contract. Snapshot Refresh uses exact create times
(`GetProcessTimes`), oldest-first with parents before children; startup
Start-vs-Refresh duplicates are suppressed by resolver-backed PID plus
create-time-tolerance dedup (Start wins).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §InitializeStartupBootstrap/InitializeSnapshotDelta -->

The uncommitted periodic candidate starts scheduling only after that startup
attempt. Linux starts scheduling after startup rundown succeeds. A shared
UTC-aligned one-shot scheduler defaults to hourly `HH:05`, skips missed ticks and
overlaps, and waits for an active inventory on disposal. Periodic Windows
inventory emits current live instances without clearing or reconciling startup
state. Configuration keys are `ProcessRefreshEnabled`,
`ProcessRefreshIntervalMinutes`, and `ProcessRefreshOffsetMinutes`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/PeriodicProcessRefreshScheduler.cs; ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs; ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §StartPeriodicRefresh/RunPeriodicRefreshSnapshot; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §Start/RunSnapshot -->

This replaced the old since-boot Security-log tree reconstruction; the log-wrap "reboot required" failure mode is gone.

### Field enrichment (Start)

- **User:** UserSID extracted from the classic kernel ProcessStart payload (version/pointer-size-aware offset parsing), resolved via `LookupAccountSid` with a bounded SID→name cache; `OpenProcessToken` fallback on NoSid/Malformed.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs §TryGetUserSid -->
- **Command line:** ETW `ProcessTraceData.CommandLine` first; live PEB read fallback when empty. PPL-protected processes fail the PEB read by design and stay empty (counted).
- **Path:** `QueryFullProcessImageName` with device-path translation fallback.
- Enrichment failures never drop the lifecycle event — every enrichment is individually guarded and counted.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §EnrichStartFields -->

### Stop resource metrics — manifest-provider merge

Stop resource counters (CPU cycles, commit charge/peak, hard faults, read/write counts and KB, token elevation) come from a separate `Microsoft-Windows-Kernel-Process` subscription (keyword 0x10), correlated to the kernel Stop by PID nearest-in-time within a 5-second window. Stop emission never blocks on the manifest event: after window expiry the Stop goes out with defaulted metrics and `manifest_metric_misses` increments.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §stop metric correlation -->

### Boot-trace coverage — opt-in Global Logger replay

With `EnableBootProcessTrace` (default **off**, fully inert when off), Wintap arms the Windows Global Logger at shutdown; at startup it verifies session ownership by configured ETL path, stops/disarms only owned sessions (foreign "NT Kernel Logger" sessions are never touched), and replays the boot ETL after snapshot + live subscription, emitting Starts for early-boot processes (smss/csrss/services lineage roots) not already covered by Refresh — dedup by PID + create-time tolerance, counted as `boot_replay_count`. Disabled startup still cleans up owned armed state. End-to-end arm/stop/disarm/replay was validated by an Architect overnight smoke-test 2026-08-18→19 ([[wiki/work/improve-windows-process-collection/verification]]).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/helpers/BootProcessTraceHelper.cs -->

### QA counters

The sensor logs QA counters at interval and shutdown: `sid_extracted/null/malformed/fallback`, `cmdline_empty`/`cmdline_peb_recovered`, `stop_without_start`, `manifest_metric_misses`, `snapshot_count`, `boot_replay_count`, `dedup_suppressed` — making field-population quality and ETW loss measurable from any running instance.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §QA counter snapshot -->

## Core Routing

`EventChannel.Send` treats process events specially: it resolves parent process context when possible and registers process events with `IProcessResolver`. `ProcessResolver` command-line/string persistence is parameterized (DuckDB), so hostile command lines are stored exactly. Unresolvable parents are annotated with an unknown-parent sentinel and warned once per parent PID (expected best-effort attribution, not a defect).
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §RegisterProcess -->

## ETL Boundary

Unchanged by the overhaul. The process ETL query selects `Process` messages whose activity is `Start` or `Refresh`; a separate stop query selects stop activity. Stops now carry `PidHash` consistent with Starts (the old Security-log path had stop handling commented out entirely).
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/process.epl §query -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/process-stop.epl §query -->

Approved greenfield projection (2026-10-25): Start/Refresh parquet adds nullable
string `ProcessStartSource`. `ApplyStartProvenance` reads whitespace-delimited
`PROC_START_SRC=` tokens from producer `Process.Arguments` and accepts only one
distinct recognized value: `sched_fork`, `sched_exec`, or `execve_or_execveat`.
Missing, conflicting or unknown values stay null. This is acquisition/image
provenance, not a distinct-birth or successful-exec guarantee; process hashes,
timestamps, CommandLine and Stop projection are unchanged. Older parquet without
the column remains unknown unless an actual Arguments breadcrumb is present.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §ApplyStartProvenance, handleStartEvent; ../wintap/wintap/core/etl/model/ProcessObjectModel.cs §ProcessStartSource; ../wintap/tests/Wintap.Tests/TelemetryProjectionQualityTests.cs -->

The committed additive timing implementation preserves canonical birth in
`EventTime`/`StartTime` and adds `ObservationTimeFileTimeUtc`,
`ObservationTimeMonotonicNanoseconds`, `ObservationClockDomain`,
`ObservationRunId`, plus the existing envelope `ReceiveTime`, to normal process
ETL. Linux exec/clone retain raw `bpf_ktime_get_ns()`; failed UTC conversion leaves
UTC absent. Refresh rows use userspace UTC scan start and have no kernel monotonic
value. Optional numeric Parquet fields have a stable nullable `long` schema
independent of first-row population. Direct Parquet also carries `ReceiveTime` and
the nested process fields through its scalar projection. The bounded Linux
`live-01` run found that an absent Refresh monotonic value could materialize as
numeric `0` when a kernel-timed row led the direct batch. The repaired projection
retains absent timing keys, and schema inference explicitly recognizes both normal
and `Process_`-prefixed timing fields; synthetic first-row-order regressions pass.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject; ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs §ApplyKernelProcessObservation; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent; ../wintap/wintap/core/etl/load/ParquetWriter.cs §DetermineSchemaFromExpando; ../wintap/wintap/core/etl/load/DirectParquetSink.cs §DirectParquetProjection -->

Normal process ETL persists command-line source/status. Direct Parquet carries the
same nested fields as `Process_CommandLineSource` and
`Process_CommandLineCaptureStatus` through its reflection projection. The bounded
Linux gate found both fields in all 113 files and preserved all 24 deliberately
empty child observations without parent text.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent; ../wintap/wintap/core/etl/model/ProcessObjectModel.cs §ProcessStartData; ../wintap/tests/Lintap.Tests/ProcessCommandLineQualityTests.cs -->

Normal ETL also persists `ExecutionObservationKind`. Direct Parquet retains a
stable optional `Process_ExecutionObservationKind` column even when a null
clone/Refresh row establishes the batch schema. The bounded gate found the field
in all 98 files and exact fork → attempt → success → attempt → success ordering in
all eight repeated-exec controls.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent; ../wintap/wintap/core/etl/load/DirectParquetSink.cs §AddScalarProperties; ../wintap/tests/Lintap.Tests/ProcessExecutionObservationTests.cs -->

## Analysis Implications

- Process lineage is keyed by `PidHash`/`ParentPidHash`, not PID alone; PID reuse is handled by mixing PID with create time and by `ProcessResolver`'s time-windowed instance resolution.
- Create times are true ETW/process create times, not event-log record times — cross-source joins on PidHash are more stable than under the Security-log era.
- Security-log retention/log-wrap no longer matters for process telemetry, and hosts with audit policy disabled now produce full process telemetry.
- Stop records are first-class again (coverage restored), with resource metrics best-effort per the correlation-window semantics above — treat metric-defaulted stops (`manifest_metric_misses`) as valid terminations, not data errors.
- Compare raw monotonic observation nanoseconds only within their capture-run and
  clock domain. They preserve producer ordering evidence but do not guarantee
  nanosecond accuracy or replace birth-based identity.
- Treat numeric `0` from `live-01` as retained serialization-defect evidence, not
  a valid userspace Refresh monotonic timestamp. Repaired-binary `live-02` confirms
  all 1,312 Refresh rows remain null while all 4,988 kernel-timed Start rows remain
  populated and nonzero; both fields are optional in all 124 Parquet files.
- Treat command-line status as part of the observation. Do not fill `empty`,
  `unavailable` or `read-error` rows from parent/neighbor events, and do not parse
  the flattened string as executable path evidence. Process-lifetime DBT selection
  remains a separate unresolved contract.
- Filter executable success using `ExecutionObservationKind=exec_success`, not
  `ActivityType=Start` alone. Preserve attempts as intent evidence, keep name/path
  from the same row, and do not infer a process-lifetime initial/latest policy.

See also [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]], [[wiki/workflow/future-experiment-analysis-workflows]], and [[wiki/repo/wintappy-pipeline-repo]] (downstream `process`/`process_summary`/`process_uber_summary` DBT models).

### Refresh is context, not a new creation (2026-11-12)

Linux and Windows Refresh continue to use canonical process birth as `EventTime`;
the additive observation fields identify when each inventory scan began. Repeated
periodic rows are therefore repeated context observations of the same identity,
not new births. Live-only inventory still cannot recover exited ancestors with
surviving descendants, and startup dedup/reconciliation remains distinct from
periodic republication.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §RunSnapshot/CreateRefreshMessage; ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §RunPeriodicRefreshSnapshot/CreateRefreshMessage -->

Current downstream `num_process_start` counts Start **and** Refresh observations;
it must not be interpreted as distinct new creations when evaluating refresh noise.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §process_base -->
See [[wiki/concept/durable-process-context-and-stream-table-enrichment]] for
unimplemented reconciliation/history options, and
[[wiki/workflow/process-ancestry-completeness-qa]] for structural coverage metrics.
