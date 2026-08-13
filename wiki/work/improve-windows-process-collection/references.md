---
title: "Feature References: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs
  - ../sid-extraction-test/README.md
policy: agent-editable
last_validated: 2026-08-13
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/improve-windows-process-collection/references.md
tags: [feature-work, process-events, etw, references]
---

# Feature References: Improve Windows Process Collection

## Live Repo Sources

- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` — current
  Security-log path: real-time 4688 starts, commented-out 4689 stops
  (§ProcessSecurityLogEvent), since-boot tree reconstruction
  (§ReconstructProcessTreeFromSecurityLog), log-wrap failure (§Initialize),
  PidHash from event-log times.
- `../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs` —
  manifest-provider (`Microsoft-Windows-Kernel-Process`,
  `22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716`, TraceEventFlags 16) ProcessStop
  metrics: ExitCode, CPUCycleCount, CommitCharge/Peak, HardFaultCount,
  Read/Write operation counts and KB, TokenElevationType. ProcessStart parse
  commented out. These are the fields the unified sensor must retain.
- `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs` —
  `KernelSession` singleton ("NT Kernel Logger",
  `TraceEventSessionOptions.Create`, 250/500 MB buffers), `KernelSource`,
  `KernelParser` singletons. Subscription pattern:
  `KernelParser.Instance.EtwParser.<Event> += handler` (see FileSensor,
  TcpSensor, ImageLoadSensor).
- `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
  — starts ProcessSensor first ("for process attribution"), seeds
  `kernelFlags = Keywords.Process`, ORs each sensor's
  `KernelTraceEventFlags`, then enables the kernel provider once and calls
  the blocking `source.Process()` on a background worker.
- `../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs` —
  `EtwProviderCollector` base: per-sensor user-mode sessions
  (`Wintap.Collectors.<name>`) for manifest providers.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` — §Send treats
  Process messages specially (parent resolution, `IProcessResolver`
  registration); `GetProcessHistory()`, `ClearProcessDB()`; fallback
  `GenPidHash(PID, EventTime)` at §279.
- `../wintap/wintap/core/infrastructure/ProcessResolver.cs` — PID-reuse-safe
  resolution keyed by PID + start time; start-time-tolerance repair logic
  added by the fix-unbounded-process-table-growth feature (relevant to
  cross-source create-time canonicalization).
- `../wintap/wintap/core/shared/ProcessHash.cs` §GenPidHash(pid,
  fileTimeUtc) — the compatibility-frozen lineage key.
- `../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs` — Linux
  snapshot-refresh precedent (enumerate + exact start times + Refresh
  messages); shape to mirror on Windows.

## External Sources

- `C:\PUBLIC\sid-extraction-test\` — **validated POC** (technique proven per
  interview 2026-08-13):
  - `ProcessTraceDataExtensions.cs` — drop-in UserSID extraction from classic
    kernel Process events; re-derives the offset TraceEvent skips
    ("Skipping UserSID"); handles V1–V4+ layouts, pointer-size differences,
    null-SID marker, malformed guard. Must be called inside the event
    callback (TraceEvent recycles instances).
  - `Program.cs` — live session (`EnableKernelProvider(Keywords.Process)`,
    `Kernel.ProcessStart/ProcessDCStart`), .etl replay mode, `--dual`
    dual-session mode (not adopted).
  - `README.md` — Global Logger boot-trace procedure: a plain AutoLogger
    cannot carry classic kernel events; set
    `HKLM\SYSTEM\CurrentControlSet\Control\WMI\GlobalLogger` `Start=1`,
    `FileName=<etl path>`, `EnableKernelFlags=01000000`
    (EVENT_TRACE_FLAG_PROCESS; pad to 32 bytes if start fails). At boot it
    becomes an "NT Kernel Logger" session; stop with
    `logman stop "NT Kernel Logger" -ets`, disarm `Start=0`, replay the ETL.
    tokenCheck is skipped in replay mode; early-boot SIDs mostly S-1-5-18.
- TraceEvent 3.1.23 (`Microsoft.Diagnostics.Tracing.TraceEvent`) — shipped by
  Wintap; `ProcessTraceData` exposes `CommandLine`, `ImageFileName`,
  `ParentID`, `SessionID`, `ExitStatus` on classic kernel Process events.
- Win32/NT snapshot APIs for exact create times and identity:
  `GetProcessTimes`/`OpenProcess`, `OpenProcessToken` (POC ground-truth leg),
  PEB read via `NtQueryInformationProcess` for command-line fallback.

## Related Wiki Pages

- [[wiki/event_type/process-events]] — canonical semantics to update at
  closeout.
- [[wiki/component/windows-sensor-service-internals]] — startup ordering and
  EventChannel routing.
- [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] — cross-platform
  semantic parity context.
- [[wiki/work/lintap-process-creation-validation/validation-harness-design]] —
  harness to adapt for Windows verification.
- [[wiki/work/fix-unbounded-process-table-growth/verification]] — 2026-08-13
  Windows run that hit the log-wrap failure; retention telemetry used by the
  soak criterion.

## Libraries And APIs

- TraceEvent 3.1.23 (constraint: do not upgrade for this feature).
- DuckDB.NET (ProcessTree/event_store; unchanged).
- `System.Diagnostics.Eventing.Reader` (removed with the Security-log path).

## Notes

- Classic kernel Process/End payload has `ExitStatus` but not the resource
  counters; the manifest provider's ProcessStop remains the source for those
  metrics inside the unified sensor (one sensor class, two subscriptions).
- ETW ProcessStart event timestamp ≈ create time but may differ microseconds
  from `GetProcessTimes`; PidHash canonicalization across sources is a design
  concern (see design.md).
