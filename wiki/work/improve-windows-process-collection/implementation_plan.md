---
title: "Implementation Plan: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-windows-process-collection/design.md
  - ../wintap/CLAUDE.md
  - ../wintap/tests/Wintap.Tests/Wintap.Tests.csproj
  - ../wintap/developer_docs/audits/wpc-02-sensor-core.md
policy: agent-editable
last_validated: 2026-08-19
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
(`developer_docs/instructions/wpc-<nn>-<slug>.md`) implemented by the
Developer with xUnit tests tagged `[Trait("Category", "wpc-<nn>")]` in
`tests/Wintap.Tests`.

**Feature abbreviation: `wpc`** (windows-process-collection). Units are
`wpc-01` … `wpc-09`; run one unit's tests with
`dotnet test --filter "Category=wpc-01"` and the whole feature with
`dotnet test --filter "Category~wpc"`.

- **Slice 1 (wpc-01–wpc-06):** unified sensor, old paths removed, QA counters.
- **Slice 2 (wpc-07):** opt-in Global Logger boot ETL coverage.
- **Slice 3 (wpc-08):** Windows validation harness + verification runs +
  closeout. **2026-08-18 update:** formal harness implementation is skipped;
  the Architect accepted manual slice-2 validation evidence instead. `wpc-09`
  is added, without renumbering, as the final code-unit minor bug sweep before
  closeout.

## Notes

- **2026-08-18 — wpc-08 skip decision.** The Architect accepted manual slice-2
  validation in place of the formal wpc-08 validation harness: full process tree
  back to kernel-era roots, usernames present on all reviewed records, and a
  stable overnight run. The `wpc-08` row remains in this plan for numbering and
  traceability but is considered skipped, not renumbered or replaced. The final
  code unit is `wpc-09` minor bug sweep.

## Steps

1. **wpc-01 — SID extraction helper.** Port
   `../sid-extraction-test/ProcessTraceDataExtensions.cs` to
   `wintap/platform/windows/sensor/etw/helpers/`, namespace
   `gov.llnl.wintap.platform.windows.collect.etw.helpers`, unchanged logic.
   Tests: synthetic payload fixtures for V3/V4 layouts × 4/8-byte pointers,
   null-SID marker, malformed guards (offset math is pure — highly testable).

2. **wpc-02 — Sensor core.** New `WindowsProcessSensor` subscribing
   `KernelParser.Instance.EtwParser.ProcessStart/ProcessStop` on the shared
   session; live Start create-time canonicalization from the ETW ProcessStart
   timestamp (no per-Start `OpenProcess` / `GetProcessTimes` lookup); Start
   emission registers through `EventChannel` / `ProcessResolver`; Stop emission
   resolves identity through `ProcessResolver` on the hot path (counter +
   hash-from-stop-time fallback on miss). No sensor-owned PID instance map in
   this unit. Tests: ETW timestamp canonicalization, Stop resolver hit, Stop
   resolver miss fallback, resolver-selected PID-reuse instance (behind minimal
   injectable emit/resolver/clock seams — keep it minimal, no new abstraction
   beyond what the tests need).

3. **wpc-03 — Snapshot refresh.** Snapshot enumerator (exact create times,
   parent PID, path, command line via PEB, user via token) emitting Refresh
   events oldest-first; replaces `Initialize()` Security-log reconstruction;
   preserves `ClearProcessDB()`-before-Refresh ordering; seeds the same three
   synthetic system processes (PID 4 / 0 / -1) as today. Start-vs-Refresh
    dedup through resolver-backed PID + create-time tolerance. Tests: parent-instance selection (latest
   create time preceding child's), dedup rule.

4. **wpc-04 — Field enrichment.** SID→user via `LookupAccountSid` with bounded
   cache and `OpenProcessToken` fallback on NoSid/Malformed; command line ETW
   field first, PEB fallback when empty; Win32 path via
   `QueryFullProcessImageName` with device-path translation fallback.
   Enrichment failures never drop the event. Tests: cache behavior, fallback
   selection matrix.

5. **wpc-05 — Stop metrics merge.** User-mode subscription to
   `Microsoft-Windows-Kernel-Process` (keyword 0x10) for ProcessStop
   counters; correlate by PID nearest-in-time (initial window 5 s); Stop
   emission never blocks on the manifest event — metrics default and
   `manifest_metric_misses` increments after window expiry. Tests:
    correlation window hit/miss/expiry, PID-reuse resolver interaction.

6. **wpc-06 — Wire-in and removal.** `WindowsSubscriptionManager` starts
   `WindowsProcessSensor` first (kernel flags already seed
   `Keywords.Process`); delete `ProcessSensor.cs`, `KernelProcessSensor.cs`,
   their settings entries, and the now-unused
   `System.Diagnostics.Eventing.Reader` usage; QA counters logged at interval
   and on shutdown (sid_extracted/null/malformed/fallback, cmdline_empty /
   cmdline_peb_recovered, stop_without_start, manifest_metric_misses,
   snapshot_count, dedup_suppressed). Verification gate: full
   `dotnet build -c Release` + all wpc tests green + manual smoke run
   documented.

7. **wpc-07 — Boot ETL coverage (slice 2).** `EnableBootProcessTrace` setting
   (default off); startup: detect/verify the Global Logger boot session
   (log-file path must match our configured ETL path), stop it before
   `KernelSession` construction, disarm registry; after live subscription +
   snapshot, replay the ETL (`ETWTraceEventSource` file mode) emitting Starts
   for instances not covered by Refresh (PID + create time within tolerance);
   re-arm registry at shutdown when enabled. Tests: dedup tolerance logic,
   session-ownership verification predicate.

8. **wpc-08 — Verification (slice 3, cross-repo).** Extend
   `validation/process-creation` for Windows: scripted workload manifest,
   scoring for start coverage, stop coverage, PidHash stability across
   activity types, lineage accuracy; identity matrix runs (plain user, runas,
   SYSTEM, elevated); audit-policy-off run; armed-reboot boot-coverage run;
    ≥10-min service-mode soak with retention telemetry. Results recorded in
    [[wiki/work/improve-windows-process-collection/verification]].

9. **wpc-09 — Minor bug sweep (final code unit).** Address findings from the
   2026-08-18 overnight smoke before feature closeout: boot-trace arm/disarm
   lifecycle gaps, missing-parent warning triage/fix-or-annotation,
    process-name / DuckDB command-line escaping triage and fix if confirmed,
    the cosmetic QA-counter logger tag only if the wpc-07 rider did not already
    fix it, and restoration of the platform-owned runtime data-root defaults
    after the Windows `/tmp` fallback contributed to DuckDB contention.

## Files Likely To Change

- `../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs` (new)
- `../wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs` (new)
- `../wintap/wintap/platform/windows/sensor/etw/helpers/` snapshot + PEB helpers (new)
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` (deleted)
- `../wintap/wintap/platform/windows/sensor/etw/KernelProcessSensor.cs` (deleted)
- `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
- `../wintap/wintap/core/infrastructure/EventChannel.cs` (wpc-09 parent-warning triage only)
- `../wintap/wintap/core/infrastructure/ProcessResolver.cs` (wpc-09 DuckDB command-line escaping only if confirmed)
- `../wintap/wintap/core/shared/Env.cs` and `ConfigManager.cs` (wpc-09 platform-default restoration)
- `../wintap/wintap/core/etl/ETLConfig.json` (remove shared `/tmp` default)
- `../wintap/platform/windows/WintapCoreSvcMgr/BackupDatabaseManager.cs` (wpc-09 only if logs implicate backup/recovery insert path)
- `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs` (wpc-07 ordering only)
- `../wintap/wintap/Properties/Settings.*` (sensor settings, new boot-trace setting)
- `../wintap/tests/Wintap.Tests/` (new wpc test classes)
- `validation/process-creation/` (Windows harness, wpc-08)

## Tests To Add Or Update

Per-unit xUnit tests as listed in Steps, all tagged
`[Trait("Category", "wpc-<nn>")]`, runnable via
`dotnet test --filter "Category=wpc-<nn>"` (whole feature:
`dotnet test --filter "Category~wpc"`). ETW-session and elevation-dependent
behavior is out of unit-test reach; after the 2026-08-18 wpc-08 skip decision,
boot-trace runtime behavior is covered by Architect-executed manual smoke rather
than heavy registry/session test doubles.

## Migration Or Compatibility Notes

- No WintapMessage/ProcessObject schema or PidHash formula changes (hard
  constraint; live Start PidHash continues to use ETW process-start time as
  Wintap's canonical source, while Refresh uses live create time and dedup /
  tolerance repair handles residual cross-source skew).
- `ClearProcessDB()`-then-Refresh startup contract preserved for
  `ProcessResolver`.
- Esper EPL files unchanged.
- Hosts with audit policy disabled gain process telemetry; nothing regresses
  on hosts with it enabled.
- `EnableBootProcessTrace` defaults off; no registry writes unless opted in.

## Rollback Plan

- All wintap changes land on one feature branch; rollback = revert the merge.
- Old sensors remain in git history; no data-format migration to unwind.
- If wpc-07 misbehaves in the field, setting off = fully inert (no registry
  writes, no replay path).

## Done Checklist

- [x] wpc-01 SID helper + tests merged (2026-08-17, wintap develop-dave
      9862131; 9/9 tests passed, audit filed)
- [x] wpc-02 sensor core + tests complete (2026-08-17; new
      `WindowsProcessSensor`, 5/5 wpc-02 tests passed, audit filed;
      runtime wire-in deferred to wpc-06 as planned)
- [x] wpc-03 snapshot refresh + tests merged (2026-08-17, wintap develop-dave
      b500966 with wpc-02; 7/7 tests passed, audit filed)
- [x] wpc-04 enrichment + tests merged (2026-08-17, wintap develop-dave
      9009d1d; 7/7 tests passed, audit filed)
- [x] wpc-05 stop-metrics merge + tests merged (2026-08-17, wintap develop-dave
      0f273e0; manifest Stop-metric correlation into resolver-backed kernel
      Stop emission, 4/4 wpc-05 tests passed, audit filed)
- [x] wpc-06 wire-in, old paths deleted, Release build + full wpc suite green,
      smoke executed (2026-08-17; `WindowsProcessSensor` wired in
      first, legacy `ProcessSensor`/`KernelProcessSensor` deleted, 35/35 wpc
      tests and 36/36 test-project regression passed, audit filed; elevated
      manual smoke executed by the Architect 2026-08-17 — PASS, audit-policy
      evidence waived; wpc-05 and wpc-06 both landed in wintap develop-dave
      commit 0f273e0)
- [x] wpc-07 boot ETL coverage complete (2026-08-18; opt-in
      `EnableBootProcessTrace` default-off path implemented, 10/10 wpc-07 tests
      passed, 45/45 wpc regression tests and 46/46 full test-project run passed,
      audit filed; Architect deployed published build locally, rebooted, and ran
      overnight with good observed results)
- [x] wpc-08 **skipped** (Architect decision 2026-08-18, not renumbered):
      formal harness replaced by accepted manual validation — process tree to
      kernel-era roots, usernames on all reviewed records, stable overnight
      run; evidence recorded in
      [[wiki/work/improve-windows-process-collection/verification]]
- [x] wpc-09 minor bug sweep complete (2026-08-19, wintap develop-dave
      19e89dc with wpc-07; boot-trace arm/disarm lifecycle fixed, DuckDB
      inserts parameterized, parent-warning annotated, logger tag fixed,
      platform-owned data-root defaults restored;
      19/19 wpc-09 tests, 64/64 wpc suite, 65/65 full test project, Release
      build 0 errors, audit filed; final overnight smoke 2026-08-18→19 PASS
      with boot replay confirmed end-to-end)
- [x] verification.md complete; wiki/log.md closeout entry appended
      (2026-08-19)
- [x] Durable semantics promoted to [[wiki/event_type/process-events]]
      (2026-08-19)
