---
title: "Feature Design: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs
  - ../sid-extraction-test/ProcessTraceDataExtensions.cs
  - ../sid-extraction-test/README.md
policy: agent-editable
last_validated: 2026-08-13
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-windows-process-collection/design.md
tags: [feature-work, process-events, etw, windows-sensor, design]
---

# Feature Design: Improve Windows Process Collection

## Summary

One new `WindowsProcessSensor` replaces `ProcessSensor` (Security-log) and
`KernelProcessSensor` (manifest stop metrics). It fuses four sources into a
single Start/Stop/Refresh stream with kernel-true create times and one PidHash
per process instance:

| Source | Yields | When |
| --- | --- | --- |
| Boot ETL replay (Global Logger) | Start events for early-boot processes | Service start, if armed + file present |
| Live process snapshot (Win32/NT) | Refresh events, exact create times | Service start, after live subscription is active |
| Classic kernel ETW ProcessStart/End (shared NT Kernel Logger session) | Real-time Start/Stop lifecycle + SID + command line | Continuous |
| Manifest provider ProcessStop (`Microsoft-Windows-Kernel-Process`) | Stop resource metrics (CPU cycles, IO, commit, token elevation) | Continuous, merged into Stop |

## Proposed Approach

### Sensor structure

- New class `WindowsProcessSensor` under
  `platform/windows/sensor/etw/`, started first by
  `WindowsSubscriptionManager` exactly as `ProcessSensor` is today (process
  attribution depends on it). It contributes
  `KernelTraceEventFlags = Keywords.Process` (already seeded by the manager).
- Lifecycle subscription uses the shared-session pattern:
  `KernelParser.Instance.EtwParser.ProcessStart += ...` and
  `ProcessStop/End += ...`. No per-sensor kernel session; live DCStart is not
  enabled (snapshot covers refresh).
- The sensor also owns a small user-mode subscription
  (`EtwProviderCollector`-style, `Wintap.Collectors.Process`) to
  `Microsoft-Windows-Kernel-Process` keyword `WINEVENT_KEYWORD_PROCESS` (0x10)
  solely for ProcessStop metrics. "One sensor" is a code-ownership
  consolidation, not necessarily one ETW session: the classic Process/End
  payload lacks the resource counters, and the process is gone by stop time so
  they cannot be queried via API.

### Create-time canonicalization (PidHash integrity)

All PidHash computation flows through one helper on the sensor:

1. On ProcessStart, attempt `OpenProcess` + `GetProcessTimes` to read the
   kernel create time; use it for PidHash. Fall back to the ETW event
   timestamp when the process is already gone (short-lived).
2. Snapshot refresh uses `GetProcessTimes` directly — same clock, same value.
3. Boot ETL Starts use the replayed event timestamp (no live process to
   query); these are the tree roots, and their children's ParentPidHash is
   derived from the sensor's own instance table, not recomputed.
4. Stop events never recompute create time from the stop-side payload: the
   sensor keeps an in-memory instance map `PID -> (createTime, PidHash,
   ParentPidHash)` populated by Start/Refresh/boot-replay, and stamps Stops
   from it. This fixes today's missing `ParentPidHash` on stops. Misses fall
   back to `ProcessResolver` lookup, then to hash-from-event-time (current
   EventChannel fallback), and are counted.

`ProcessResolver`'s start-time-tolerance repair (from
fix-unbounded-process-table-growth) remains the safety net for residual
sub-millisecond skew between sources.

### Field sourcing per event

**Start (classic kernel ProcessStart):**
- PID, ParentID, SessionID, ImageFileName, CommandLine from
  `ProcessTraceData`.
- Full path: `ImageFileName` is a kernel/ANSI name; resolve to Win32 path via
  `QueryFullProcessImageName` on the opened handle when available, else
  device-path translation. (The old path got this from the Security log's
  `NewProcessName`.)
- User: `TryGetUserSid` (POC extension, dropped in as
  `platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs`) →
  `LookupAccountSid` with a bounded SID→name cache (POC pattern). On
  `NoSid`/`Malformed`: fall back to `OpenProcessToken` on the live process;
  count both statuses.
- CommandLine fallback: when the ETW field is empty, read the live PEB
  (`NtQueryInformationProcess` → `RTL_USER_PROCESS_PARAMETERS.CommandLine`),
  best-effort with a single retry; count empties and fallback successes.

**Stop:** classic Process/End provides PID + ExitStatus + timestamp; instance
map provides PidHash/ParentPidHash/name/path; manifest ProcessStop (correlated
by PID, nearest-in-time within a short window) contributes CPUCycleCount,
CommitCharge/Peak, HardFaultCount, Read/Write counts and KB,
TokenElevationType. If the manifest event never arrives (drop), the Stop is
emitted after the correlation window with metrics defaulted — stop coverage
must not depend on the second provider.

**Refresh (snapshot):** enumerate processes (`Process.GetProcesses` or
`NtQuerySystemInformation`), per process: exact create time
(`GetProcessTimes`), parent PID (`NtQueryInformationProcess`), path
(`QueryFullProcessImageName`), command line (PEB read), user
(`OpenProcessToken`). Parent lineage: parent instance = the snapshot/boot
instance with matching PID whose create time precedes the child's. Mirrors
Linux `ProcessRundownSensor`.

### Startup sequencing

1. If the Global Logger boot session is active (it runs under the name
   "NT Kernel Logger"), stop it and capture the ETL path before
   `KernelSession` creates its own session. This ordering constraint lives in
   `WindowsSubscriptionManager.Start()` ahead of sensor construction —
   `KernelSession`'s constructor uses `TraceEventSessionOptions.Create`,
   which would otherwise clobber the boot session. Disarm the registry
   (`Start=0`) after capture; re-arm at shutdown only if the boot-coverage
   setting is enabled.
2. Start live kernel subscription (shared session) — from here, no new
   process escapes observation.
3. Take the snapshot; emit Refresh events (oldest create time first, parents
   before children).
4. Replay the boot ETL (`ETWTraceEventSource` file mode, POC replay leg):
   emit Start events only for instances not already covered by a snapshot
   Refresh (dedup key: PID + canonicalized create time within tolerance).
   Replayed instances that are still alive enrich the instance map roots.
5. `EventChannel.ClearProcessDB()` semantics are preserved: clear once before
   step 3 so the resolver rebuilds from Refresh, as today.

Events arriving live during steps 3–4 are processed concurrently; the
instance map is the dedup point (a process that starts during the snapshot
appears once as Start, not also as Refresh — Start wins).

### Configuration

- `WindowsProcessSensor` replaces the hardcoded `ProcessSensor` bootstrap; the
  `ProcessSensor`/`KernelProcessSensor` settings entries are retired.
- New setting `EnableBootProcessTrace` (default **off** for slice 1): governs
  Global Logger re-arming at shutdown and ETL ingestion at startup.
- QA counters (WintapLogger + optional telemetry rows, following the
  process_retention_telemetry precedent): sid_extracted / sid_null /
  sid_malformed / sid_fallback, cmdline_empty / cmdline_peb_recovered,
  stop_without_start, manifest_metric_misses, snapshot_count,
  boot_replay_count, dedup_suppressed.

## Data Model Or Schema Changes

None. WintapMessage/ProcessObject fields and PidHash formula unchanged
(hard constraint). All improvements are population-rate and correctness
improvements of existing fields.

## Interfaces And User Experience

- Downstream Esper EPL (`process.epl`, `process-stop.epl`) unchanged:
  Start/Refresh and Stop selection still works; stops now carry PidHash
  consistent with starts.
- Operators: no audit-policy prerequisite; new log lines and QA counters; one
  optional registry-arming behavior behind `EnableBootProcessTrace`.

## Edge Cases

- **Short-lived processes** (exit before enrichment): OpenProcess fails →
  create time falls back to ETW timestamp; command-line fallback and token
  fallback unavailable → fields default, counters increment. ETW field data
  (CommandLine, SID) still usually present — this is strictly better than the
  Security-log path.
- **PID reuse during correlation windows:** instance map is keyed by PID but
  stores create time; a new Start for a PID with a pending stop-metrics
  correlation flushes the old instance immediately.
- **Stops with no known start** (drops, processes older than any source):
  counted, emitted with resolver-fallback PidHash — current EventChannel
  behavior preserved.
- **Log-wrap condition:** eliminated (no Security-log dependency). The
  "reboot required" branch is deleted.
- **Boot ETL absent/corrupt while armed:** log + skip; snapshot alone still
  yields a complete live tree (degraded lineage for exited early-boot
  processes only).
- **WOW64/pointer-size differences in SID offsets:** handled by the POC
  extension (per-event `PointerSize`), including replayed ETLs from other
  architectures.
- **Session name collision:** another tool owning "NT Kernel Logger" is a
  pre-existing Wintap-wide condition; the boot-session stop in startup
  sequencing must verify the session's log file is our configured boot ETL
  path before treating it as ours.

## Error Handling

- Every per-event enrichment (SID, PEB, path, times) is individually
  try/caught with counters — enrichment failure never drops the lifecycle
  event.
- Manifest-provider subscription failure degrades to metric-less stops with a
  single Warn, not a sensor failure.
- Boot-trace handling failures never block live collection (strict ordering:
  live subscription starts before replay is attempted).

## Risks

- **ETW event loss under load** on the shared session (250 MB buffers) now
  affects lifecycle, not just metrics. Mitigation: stop_without_start /
  dedup counters expose loss; soak criterion in the brief.
- **PEB reads on protected processes** (PPL) fail by design → command line
  empty for those; acceptable, counted.
- **Global Logger arming** touches boot-path registry config; wrong values
  can fail the boot session (POC README documents the 32-byte padding
  gotcha). Mitigated by opt-in default and verify-before-stop check.
- **Create-time skew** between `GetProcessTimes` and ETW timestamps larger
  than expected → PidHash mismatches; mitigated by canonicalization-first
  design and resolver tolerance repair; measured by acceptance criterion 2.
- **Startup ordering regression:** other kernel-flag sensors already race the
  shared session (`Thread.Sleep` mitigations in the manager); inserting the
  boot-session stop must not widen that window. Keep it strictly before any
  `TraceEventSession` construction.

## Alternatives Considered

- **Manifest provider (`Microsoft-Windows-Kernel-Process`) as primary
  lifecycle source:** own session, no classic-MOF parsing; but no CommandLine
  or UserSID in ProcessStart, weaker rundown, and the POC investment targets
  classic events. Rejected in interview round 1/3.
- **ETW rundown (DCStart) for refresh:** same session as live events but thin
  fields (no reliable command line/user) and no exact create-time guarantee.
  Rejected for live snapshot (interview round 1).
- **Keep Security log as fallback:** dual-path maintenance and correlation
  complexity for a path whose main value (user/command line without ETW
  tricks) the POC obsoletes. Rejected in interview round 2.
- **Persistent dual-session architecture** (POC `--dual`): validated but not
  needed once the shared session + Global Logger covers the gaps. Not
  adopted (interview round 3).

## Open Questions

- Manifest-stop correlation window length (initial: 5 s, tune in
  verification).
- Whether boot ETL replay should also emit Stop events for early-boot
  processes that exited pre-service (currently: no — they fail the
  still-alive check and only matter as lineage parents, which the instance
  map handles).
- Exact home for the QA counters (log-only vs. telemetry table) — follow
  whatever the retention-telemetry promotion decides at closeout.
