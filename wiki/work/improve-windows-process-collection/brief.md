---
title: "Feature Brief: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs
  - ../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../sid-extraction-test/ProcessTraceDataExtensions.cs
policy: agent-editable
last_validated: 2026-08-13
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-windows-process-collection/brief.md
tags: [feature-work, process-events, etw, windows-sensor, pidhash, kernel-logger]
---

# Feature Brief: Improve Windows Process Collection

## Problem

Windows process collection is split across two half-enabled paths with four
compounding defects:

1. **Dropped/split stop events.** The Security-log path receives 4689
   termination events but its handling is commented out; stops only reach the
   pipeline via the separate `KernelProcessSensor` (manifest-provider
   ProcessStop), which emits them with no `ParentPidHash` and timestamps from a
   different clock domain than starts.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs §ProcessSecurityLogEvent -->
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs §parseUserModeProcessStop -->
2. **Fragile boot reconstruction.** Startup process-tree reconstruction walks
   Security-log 4688/4689 events since boot; if the log wrapped, the sensor
   logs "reboot required" and process context is degraded for the whole run.
   Observed live on host CHUMBUCKET2 on 2026-08-13 (see `wiki/log.md`).
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs §Initialize; §ReconstructProcessTreeFromSecurityLog -->
3. **Approximate create times corrupt PidHash lineage.** Create times are
   taken from event-log record `TimeCreated`, not the kernel's process create
   time. `PidHash = f(PID, createTimeFileTime)` is the lineage key, so every
   consumer inherits the approximation, and cross-source correlation (starts
   from the Security log vs. stops from ETW) is lossy.
4. **Audit-policy dependency.** 4688 collection (and command-line capture)
   silently degrades when the host's audit policy is not configured.

## Goals

- Single unified Windows process sensor that owns Start, Stop, and Refresh
  end-to-end from kernel ETW (classic NT Kernel Logger Process events) on the
  existing shared `KernelSession`.
- True kernel create times everywhere PidHash is computed.
- Stop events restored to first-class: exit status, plus the rich resource
  metrics currently sourced by `KernelProcessSensor` (CPU cycles, IO counts,
  commit charge/peak, hard faults, token elevation).
- Refresh from a live process snapshot with exact create times — no
  Security-log retention dependency, no "reboot required" failure mode.
- User identity from the ETW payload via the validated SID-extraction
  technique, with API fallback for null-SID events.
- Command line from `ProcessTraceData.CommandLine`, with live PEB read
  fallback when empty.
- Boot-time coverage: early-boot process starts (smss, csrss, services)
  captured via the Global Logger boot ETL and ingested at service start.
- No dependency on Windows audit policy for process telemetry.

## Non-Goals

- No changes to WintapMessage/ProcessObject schema or PidHash semantics.
- No changes to Linux/macOS process collection.
- No adoption of the persistent dual-session architecture (validated by the
  POC's `--dual` mode but explicitly not selected).
- No downstream Wintappy/DBT model changes — downstream sees the same shape,
  better data.
- Not attempting lineage for early-boot processes that exited before the boot
  ETL/Global Logger window (accepted loss when boot logging is unarmed).

## User-Facing Behavior

- Process Start/Stop/Refresh events keep their existing shape; data quality
  improves: exact create times, complete stop coverage, populated
  `ParentPidHash` on stops, user + command line populated without audit
  policy.
- On service start: snapshot of running processes emitted as Refresh; if a
  boot ETL exists, early-boot Starts are replayed so lineage roots at boot.
- Security-log 4688/4689 collection and reconstruction are removed; the
  "reboot required" log-wrap condition disappears.

## Acceptance Criteria

1. Scripted workload runs (validation harness) show ≥ the coverage of the old
   path with zero missing stops for observed starts on a clean run.
2. `PidHash` for the same process instance is identical across Start, Stop,
   Refresh, and boot-ETL-replayed events (tolerance-canonicalized create
   time).
3. Parent lineage (`ParentPidHash`) resolves for live starts and snapshot
   processes; stops carry the same PidHash as their start.
4. User (SID-derived) populated on kernel-ETW starts with measured null-SID
   fallback rate reported; command-line empty rate measured and reported.
5. With audit policy fully disabled, process collection is unaffected.
6. After an armed reboot, boot ETL replay yields Start events for
   pre-service processes (smss/csrss/services) with SIDs extracted.
7. Long-run soak (≥ 10 min noisy workload, service mode) shows no ETW session
   drops attributable to the process subscription and stable resolver
   behavior (`process_retention_telemetry` remains healthy).

## Affected Areas

- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` (replaced)
- `../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs`
  (removed; metrics absorbed)
- `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
  (process sensor bootstrap, kernel flags)
- `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs`
  (shared session interplay with the Global Logger boot session)
- `../wintap/wintap/core/infrastructure/EventChannel.cs` /
  `ProcessResolver.cs` (consumers of Refresh/Start registration; no schema
  change expected)
- New: SID extraction extension, snapshot enumerator, boot ETL ingestor
- `C:\PUBLIC\Wintap-Analytics\validation\process-creation` (Windows harness
  extension)

## References

See [[wiki/work/improve-windows-process-collection/references]].

## Open Questions

- Measured `CommandLine`-empty and null-SID rates under production-like load
  (answered by verification).
- Global Logger arming default: opt-in vs. on-by-default (leaning opt-in for
  slice 1; registry writes every-boot ETL churn is the concern).

## Test Plan

- Extend the process-creation validation harness to Windows: scripted
  workload with manifest ground truth; score start coverage, stop coverage,
  lineage accuracy, PidHash stability across activity types.
- Identity matrix from the POC: plain user, runas alternate user,
  SYSTEM/service, elevated — verify SID/user population.
- Audit-policy-off run: confirm collection unaffected.
- Armed-reboot run: verify boot ETL ingestion and early-boot Start events.
- Soak run in service mode with retention telemetry enabled.

## Done When

- Unified sensor merged; old paths deleted; builds green on Windows.
- All acceptance criteria demonstrated and recorded in
  [[wiki/work/improve-windows-process-collection/verification]].
- Durable semantics promoted to [[wiki/event_type/process-events]] and a
  `wiki/log.md` entry appended.
