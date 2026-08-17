---
title: "Implementation Plan: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-windows-process-collection/design.md
  - ../wintap/CLAUDE.md
  - ../wintap/tests/Wintap.Tests/Wintap.Tests.csproj
policy: agent-editable
last_validated: 2026-08-13
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-windows-process-collection/implementation_plan.md
tags: [feature-work, process-events, etw, windows-sensor, implementation-plan]
---

# Implementation Plan: Improve Windows Process Collection

## Scope

Implements [[wiki/work/improve-windows-process-collection/design]] in three
slices. Code changes land in `../wintap` on a feature branch; harness changes
land in this repo under `validation/`. The wintap repo uses the
Architect/Engineer/Developer methodology (`../wintap/CLAUDE.md`): each step
below is sized to become one approved instruction document
(`developer_docs/instructions/P2.x-*.md`) implemented by the Developer with
xUnit tests tagged `[Trait("Category", "P2.x")]` in `tests/Wintap.Tests`.

- **Slice 1 (P2.1–P2.6):** unified sensor, old paths removed, QA counters.
- **Slice 2 (P2.7):** opt-in Global Logger boot ETL coverage.
- **Slice 3 (P2.8):** Windows validation harness + verification runs +
  closeout.

## Steps

1. **P2.1 — SID extraction helper.** Port
   `../sid-extraction-test/ProcessTraceDataExtensions.cs` to
   `wintap/platform/windows/sensor/etw/helpers/`, namespace
   `gov.llnl.wintap.platform.windows.collect.etw.helpers`, unchanged logic.
   Tests: synthetic payload fixtures for V3/V4 layouts × 4/8-byte pointers,
   null-SID marker, malformed guards (offset math is pure — highly testable).

2. **P2.2 — Sensor core.** New `WindowsProcessSensor` subscribing
   `KernelParser.Instance.EtwParser.ProcessStart/ProcessStop` on the shared
   session; in-memory instance map `PID -> (createTime, PidHash,
   ParentPidHash, name, path)`; create-time canonicalization helper
   (`GetProcessTimes` first, ETW timestamp fallback); Start and Stop emission
   with Stops stamped from the instance map (resolver fallback + counter on
   miss). Tests: canonicalization fallback logic, instance-map PID-reuse
   flush, stop-without-start fallback (behind an injectable clock/process
   accessor seam — keep it minimal, no new abstraction beyond what the tests
   need).

3. **P2.3 — Snapshot refresh.** Snapshot enumerator (exact create times,
   parent PID, path, command line via PEB, user via token) emitting Refresh
   events oldest-first; replaces `Initialize()` Security-log reconstruction;
   preserves `ClearProcessDB()`-before-Refresh ordering; seeds the same three
   synthetic system processes (PID 4 / 0 / -1) as today. Start-vs-Refresh
   dedup through the instance map. Tests: parent-instance selection (latest
   create time preceding child's), dedup rule.

4. **P2.4 — Field enrichment.** SID→user via `LookupAccountSid` with bounded
   cache and `OpenProcessToken` fallback on NoSid/Malformed; command line ETW
   field first, PEB fallback when empty; Win32 path via
   `QueryFullProcessImageName` with device-path translation fallback.
   Enrichment failures never drop the event. Tests: cache behavior, fallback
   selection matrix.

5. **P2.5 — Stop metrics merge.** User-mode subscription to
   `Microsoft-Windows-Kernel-Process` (keyword 0x10) for ProcessStop
   counters; correlate by PID nearest-in-time (initial window 5 s); Stop
   emission never blocks on the manifest event — metrics default and
   `manifest_metric_misses` increments after window expiry. Tests:
   correlation window hit/miss/expiry, PID-reuse flush interaction.

6. **P2.6 — Wire-in and removal.** `WindowsSubscriptionManager` starts
   `WindowsProcessSensor` first (kernel flags already seed
   `Keywords.Process`); delete `ProcessSensor.cs`, `KernelProcessSensor.cs`,
   their settings entries, and the now-unused
   `System.Diagnostics.Eventing.Reader` usage; QA counters logged at interval
   and on shutdown (sid_extracted/null/malformed/fallback, cmdline_empty /
   cmdline_peb_recovered, stop_without_start, manifest_metric_misses,
   snapshot_count, dedup_suppressed). Verification gate: full
   `dotnet build -c Release` + all P2.x tests green + manual smoke run
   documented.

7. **P2.7 — Boot ETL coverage (slice 2).** `EnableBootProcessTrace` setting
   (default off); startup: detect/verify the Global Logger boot session
   (log-file path must match our configured ETL path), stop it before
   `KernelSession` construction, disarm registry; after live subscription +
   snapshot, replay the ETL (`ETWTraceEventSource` file mode) emitting Starts
   for instances not covered by Refresh (PID + create time within tolerance);
   re-arm registry at shutdown when enabled. Tests: dedup tolerance logic,
   session-ownership verification predicate.

8. **P2.8 — Verification (slice 3, cross-repo).** Extend
   `validation/process-creation` for Windows: scripted workload manifest,
   scoring for start coverage, stop coverage, PidHash stability across
   activity types, lineage accuracy; identity matrix runs (plain user, runas,
   SYSTEM, elevated); audit-policy-off run; armed-reboot boot-coverage run;
   ≥10-min service-mode soak with retention telemetry. Results recorded in
   [[wiki/work/improve-windows-process-collection/verification]].

## Files Likely To Change

- `../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs` (new)
- `../wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs` (new)
- `../wintap/wintap/platform/windows/sensor/etw/helpers/` snapshot + PEB helpers (new)
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` (deleted)
- `../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs` (deleted)
- `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
- `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs` (P2.7 ordering only)
- `../wintap/wintap/Properties/Settings.*` (sensor settings, new boot-trace setting)
- `../wintap/tests/Wintap.Tests/` (new P2.x test classes)
- `validation/process-creation/` (Windows harness, P2.8)

## Tests To Add Or Update

Per-unit xUnit tests as listed in Steps, all tagged
`[Trait("Category", "P2.x")]`, runnable via
`dotnet test --filter "Category=P2.x"`. ETW-session and elevation-dependent
behavior is out of unit-test reach — covered by the P2.8 harness instead; do
not build heavy test doubles for it.

## Migration Or Compatibility Notes

- No WintapMessage/ProcessObject schema or PidHash formula changes (hard
  constraint; PidHash inputs get *more accurate*, so PidHashes for the same
  process may differ across the upgrade boundary — same situation as any
  sensor restart, handled by Refresh re-seeding).
- `ClearProcessDB()`-then-Refresh startup contract preserved for
  `ProcessResolver`.
- Esper EPL files unchanged.
- Hosts with audit policy disabled gain process telemetry; nothing regresses
  on hosts with it enabled.
- `EnableBootProcessTrace` defaults off; no registry writes unless opted in.

## Rollback Plan

- All wintap changes land on one feature branch; rollback = revert the merge.
- Old sensors remain in git history; no data-format migration to unwind.
- If P2.7 misbehaves in the field, setting off = fully inert (no registry
  writes, no replay path).

## Done Checklist

- [ ] P2.1 SID helper + tests merged
- [ ] P2.2 sensor core + tests merged
- [ ] P2.3 snapshot refresh + tests merged
- [ ] P2.4 enrichment + tests merged
- [ ] P2.5 stop-metrics merge + tests merged
- [ ] P2.6 wire-in, old paths deleted, Release build + full P2 suite green,
      smoke run documented
- [ ] P2.7 boot ETL coverage merged (opt-in verified inert when off)
- [ ] P2.8 harness runs: acceptance criteria 1–7 of
      [[wiki/work/improve-windows-process-collection/brief]] demonstrated
- [ ] verification.md complete; wiki/log.md entry appended
- [ ] Durable semantics promoted to [[wiki/event_type/process-events]]
