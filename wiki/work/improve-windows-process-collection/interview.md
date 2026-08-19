---
title: "Feature Interview: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs
  - ../sid-extraction-test/README.md
policy: agent-editable
last_validated: 2026-08-17
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-windows-process-collection/interview.md
tags: [feature-work, process-events, etw, windows-sensor, interview, metrics]
---

# Feature Interview: Improve Windows Process Collection

## Initial Idea

"Start a new feature using the LLM-assisted feature workflow: windows process
event collection. We want to dramatically improve the way processes are
collected in windows."

## Context Established Before Questioning

- [[wiki/event_type/process-events]] — current Security-log-backed semantics.
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` — real-time
  starts come from Security event 4688 via `EventLogWatcher`; **4689 stop
  handling is commented out** (stops silently dropped on that path); boot-time
  tree reconstruction walks the Security log since boot and fails on log wrap
  ("reboot required"); create times are event-log record times, not true
  process create times.
- `../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs` — uses
  the `Microsoft-Windows-Kernel-Process` manifest provider but only handles
  ProcessStop (exit code + resource counters); its ProcessStart parsing is
  commented out. Starts and stops therefore come from different sources with
  different timestamps.
- `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs` and
  `WindowsSubscriptionManager.cs` — shared "NT Kernel Logger" session
  (`KernelSession` singleton); sensors declare `KernelTraceEventFlags`, the
  manager ORs them together and enables the kernel provider once.
- `../sid-extraction-test/` (C:\PUBLIC\sid-extraction-test) — proof-of-concept
  extracting UserSID from classic kernel Process events with the TraceEvent
  3.1.23 already shipped; includes a boot-coverage leg (Global Logger) and a
  dual-session mode.
- `wiki/log.md` 2026-08-13 entry — live occurrence of "Log wrap detected!
  Unable to build process tree, computer reboot required." on host CHUMBUCKET2
  during retention verification, leaving Security-log startup replay
  unverifiable on that host.

## Interview Log

### Round 1

**Q:** Primary collection mechanism? (kernel ETW primary / keep Security log and
fix gaps / hybrid)
**A:** Kernel ETW primary.
**Outcome:** decision — kernel ETW is the single real-time source.

**Q:** What pain drives "dramatically improve"? (multi-select)
**A:** All of the above: missing/incorrect stop events, fragile boot
reconstruction, timing/PidHash accuracy, audit-policy dependency.
**Outcome:** decision — all four are motivating problems.

**Q:** How should existing processes ("Refresh") be enumerated? (live snapshot
with exact times / ETW rundown DCStart / keep Security-log reconstruction)
**A:** Live snapshot + exact times.
**Outcome:** decision — Win32/NT snapshot replaces Security-log reconstruction.

**Q:** Downstream compatibility constraints?
**A:** No breaking changes.
**Outcome:** constraint — WintapMessage/ProcessObject schema and the PidHash
formula (PID + create-time FileTime) stay unchanged.

### Round 2

**Q:** Fate of existing paths (Security-log ProcessSensor + KernelProcessSensor)?
**A:** Consolidate to one sensor.
**Outcome:** decision — one sensor owns Start/Stop/Refresh; rich stop metrics
move into it; old paths removed.

**Q:** How to source command line and user, given ETW field gaps?
**A:** "There is an example project for fetching User/SID at c:\public — take a
look there for the technique. For commandline, we might need to get creative."
**Outcome:** decision + pointer — SID via the sid-extraction-test technique;
command line initially open (resolved in Round 3).

**Q:** What evidence closes the feature?
**A:** Validation harness.
**Outcome:** decision — adapt the sensor-neutral validation approach from
[[wiki/work/lintap-process-creation-validation/index]] to Windows.

### Round 3

**Q:** Status of the SID-extraction POC?
**A:** Validated, technique proven.
**Outcome:** decision — `ProcessTraceDataExtensions.TryGetUserSid` drops in
as-is; no SID spike needed.

**Q:** Command line approach, given `ProcessTraceData.CommandLine` exists on
kernel Process events?
**A:** Use ETW field + fallback.
**Outcome:** decision — ETW CommandLine first, live PEB read fallback when
empty; measure the empty rate during verification.

**Q:** Boot-time process coverage (Global Logger → boot ETL replay) in scope?
**A:** In scope.
**Outcome:** decision — early-boot process starts (smss/csrss/services) are
captured to a boot ETL and ingested at service start.

**Q:** Session architecture — shared "NT Kernel Logger" session or the POC's
persistent dual-session?
**A:** Existing shared session.
**Outcome:** decision — subscribe to Kernel.ProcessStart/Stop on the
`KernelSession` singleton; no new session management.

## Decisions

1. Kernel ETW (classic NT Kernel Logger Process events) is the single
   real-time source for process lifecycle, on the existing shared session.
2. Consolidate to one sensor; remove the Security-log start path and the
   separate `KernelProcessSensor`; retain its rich Stop metrics in the new
   sensor.
3. Refresh via live process snapshot with exact create times.
4. UserSID via the validated `ProcessTraceDataExtensions` technique.
5. Command line: `ProcessTraceData.CommandLine` first, PEB read fallback.
6. Boot-time coverage (Global Logger boot ETL ingestion) is in scope.
7. Verification via a Windows adaptation of the sensor-neutral validation
   harness.

## Constraints

- No breaking changes to WintapMessage/ProcessObject schema or PidHash
  semantics (PID + create-time FileTime).
- TraceEvent stays at the shipped version (3.1.23) — the SID technique was
  validated against it.
- Only one NT Kernel Logger session exists system-wide; the sensor must ride
  the shared session and its OR'd kernel flags.

## Delegations

- Reconciling the Global Logger boot session (which becomes "NT Kernel Logger"
  at boot) with Wintap's own NT Kernel Logger session creation — design stage.
- Ordering/dedup between boot ETL replay, startup snapshot, and live ETW
  events — design stage.
- Where the PEB command-line fallback lives and its failure handling — design
  stage.

## Deferred / Open Questions

- Measured `CommandLine`-empty and null-SID rates in production-like load —
  answered by verification, not blocking design.
- Whether Global Logger arming ships enabled by default or opt-in — leaning
  opt-in for the first slice; confirm at implementation-plan review.

## Playback Summary

Replace Security-log-based Windows process collection with classic kernel ETW
as the single source of truth, consolidated into one sensor that owns
Start/Stop/Refresh: live snapshot with exact create times for refresh, the
validated SID-extraction technique for user identity, ETW CommandLine with PEB
fallback, boot ETL ingestion for early-boot coverage, rich stop metrics
retained, no downstream schema or PidHash changes, verified by a Windows
validation harness. Confirmed by the human 2026-08-13, with design.md
requested in the same session.

## Sealed — human estimates

Retrofitted 2026-08-17 after the ROI/velocity mini-lab protocol was adopted;
this section was **not** captured sealed at feature open. Treat these as
broken-seal retrofit data, not independent sealed estimates.

**Q: Estimated hours to build this feature solo, without AI (total only):**
**A:** 3 weeks, recorded as 120 hours in `metrics.md` assuming 40-hour weeks.

**Q: Predicted hours of your own attention with the AI workflow (total only):**
**A:** Not captured.
