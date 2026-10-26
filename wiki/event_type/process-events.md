---
title: "Process Events"
type: event_type
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c
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
  - ../wintap/tests/Wintap.Tests/TelemetryProjectionQualityTests.cs
policy: agent-editable
last_validated: 2026-10-25
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

Process events are normalized as `WintapMessage` records with `MessageType = Process` and a nested `ProcessObject` containing process identity, parent identity, path, command line, user, exit/resource fields, and hashes. The schema and the PidHash formula (PID + create-time FileTime) were unchanged by the 2026-08 collection overhaul — all improvements below are population-rate and correctness improvements of existing fields.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject -->

## Producer Semantics (unified WindowsProcessSensor, 2026-08)

As of the improve-windows-process-collection feature (wintap `develop-dave`, commits 9862131…19e89dc, closed 2026-08-19), a single `WindowsProcessSensor` owns Windows process lifecycle. It replaced the Security-log `ProcessSensor` (event 4688/4689) and the separate `KernelProcessSensor`; both were deleted, and **process telemetry no longer depends on Security-log audit policy**. Design and decision history: [[wiki/work/improve-windows-process-collection/design]], [[wiki/work/improve-windows-process-collection/implementation_plan]]; per-unit evidence in `../wintap/developer_docs/audits/wpc-01…wpc-09`.

### Live Start/Stop — classic kernel ETW on the shared session

Real-time lifecycle comes from classic NT Kernel Logger ProcessStart/ProcessStop events on the shared kernel session (`Keywords.Process`), with `WindowsProcessSensor` started first by `WindowsSubscriptionManager` because non-process attribution depends on it.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs §Start -->

The **ETW ProcessStart timestamp is canonical** for live Start create time and therefore for `PidHash` — no per-Start `OpenProcess`/`GetProcessTimes` handle lookup (Architect decision 2026-08-17; ETW has been Wintap's process-start ground truth for over a decade). Stops resolve identity through `ProcessResolver` (the sole hot-path identity store — no sensor-owned PID map); resolver misses are counted. The `pid-v2` patch replaces the earlier hash-from-stop-time fallback with the explicit unknown identity: Stop time is not process-start time.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §EmitStart; §EmitStop -->

### Refresh — live snapshot with dedup

At startup the sensor preserves the `ClearProcessDB()`-then-Refresh contract, then emits Refresh events from a live process snapshot with exact create times (`GetProcessTimes`), oldest-first with parents before children, seeding the same synthetic system processes as before. Start-vs-Refresh duplicates are suppressed by resolver-backed PID + create-time-tolerance dedup (Start wins).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §InitializeSnapshotRefresh -->

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

## Analysis Implications

- Process lineage is keyed by `PidHash`/`ParentPidHash`, not PID alone; PID reuse is handled by mixing PID with create time and by `ProcessResolver`'s time-windowed instance resolution.
- Create times are true ETW/process create times, not event-log record times — cross-source joins on PidHash are more stable than under the Security-log era.
- Security-log retention/log-wrap no longer matters for process telemetry, and hosts with audit policy disabled now produce full process telemetry.
- Stop records are first-class again (coverage restored), with resource metrics best-effort per the correlation-window semantics above — treat metric-defaulted stops (`manifest_metric_misses`) as valid terminations, not data errors.

See also [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]], [[wiki/workflow/future-experiment-analysis-workflows]], and [[wiki/repo/wintappy-pipeline-repo]] (downstream `process`/`process_summary`/`process_uber_summary` DBT models).
