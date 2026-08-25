---
title: "Verification: Windows Sensor Health-Check"
type: concept
confidence: high
grounded_by:
  - ../wintap/developer_docs/audits/shc-01-health-check-core.md
  - ../wintap/developer_docs/audits/shc-03-querydosdevice-drive-map.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/windows-sensor-health-check/verification.md
tags: [feature-work, health-check, windows-sensor, qa, verification]
---

# Verification: Windows Sensor Health-Check

Verification record against the re-frozen acceptance criteria in
[[wiki/work/windows-sensor-health-check/brief]] (amendment #2 set,
2026-08-24).

> **Provenance note:** `/developer_docs/` is **gitignored** in the wintap
> repo — instruction and audit artifacts are local-only process files, not
> version-controlled. This page therefore preserves the durable verification
> evidence (commands, counts, deviations); the audits remain the detailed
> local record.

## shc-01 — Health-check core engine, checks, liveness, log flush (2026-08-24)

- **Audit:** `../wintap/developer_docs/audits/shc-01-health-check-core.md`
  (Status: Complete). Files created:
  `wintap/core/infrastructure/health/IWintapHealthCheck.cs`,
  `.../SensorHealthMonitor.cs`, `.../DefaultHealthChecks.cs`,
  `tests/Wintap.Tests/SensorHealthMonitorTests.cs`. **No production files
  modified** (pure new code, no wiring — as instructed).
- **Commands and results:**
  - `dotnet build -c Release` — **failed** with the known solution-level
    `MSB4249` Wintap-Workbench website-project issue (documented recurring
    deviation since wpc-02).
  - `dotnet build "wintap\Wintap.csproj" -c Release -p:WarningLevel=0` —
    passed (approved project-scoped fallback).
  - `dotnet test "tests\Wintap.Tests\Wintap.Tests.csproj" --filter "Category=shc-01"`
    — **33/33 passed** (0.59 s), covering the five definitive checks
    (including the File/Registry path-form matrices and the injected
    unknown-sentinel seam), sample caps, window drain/idle silence, custom
    check extensibility, fail-open, liveness grace/stall/recovery/Stop()
    suppression, config clamps, and a 4-thread concurrency smoke.
  - Independently re-verified by the main session (Architect) 2026-08-24:
    33/33.
- **Criteria coverage:** contributes evidence toward frozen criteria 2, 3,
  4, 5, 6, 7 (engine-level); criteria 1, 8, 9 complete at shc-02.

## shc-03 — QueryDosDevice drive map + fromNative guard fix (2026-08-25)

- **Audit:** `../wintap/developer_docs/audits/shc-03-querydosdevice-drive-map.md`
  (Status: Complete). Commit `26ce94c`. Files modified:
  `wintap/platform/windows/infrastructure/WindowsStateManager.cs`
  (diskpart spawn → per-letter `QueryDosDevice` P/Invoke, never-throw
  fail-soft), `wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs`
  (`fromNative` direct `VolumeNumber` lookup replacing the
  count-comparison guard; dead `harddiskvolume1` hack removed;
  `private` → `internal` seam), plus — with explicit Architect approval —
  fixture-first initialization added to the pending shc-02 test fixture so
  whole-feature verification could run without xUnit
  synchronization-context hangs.
- **Commands and results:**
  - `dotnet build -c Release` — failed with the known solution-level
    MSB4249 Wintap-Workbench issue (documented recurring deviation);
    approved project-scoped fallback
    `dotnet build "wintap\Wintap.csproj" -c Release -p:WarningLevel=0`
    passed.
  - `dotnet test ... --filter "Category=shc-03"` — **27/27 passed**
    (parse acceptance/rejection matrices, mapping isolation, `fromNative`
    translation-path tests including the old-guard breakage case, live
    non-elevated `QueryDosDevice` smoke).
  - `dotnet test ... --filter "Category~shc"` — **65/65**; full suite
    **165/165**.
- **Behavioral note:** tests ran from a non-elevated shell — the diskpart
  elevation blocker that paused shc-02 is confirmed removed.

## shc-02 — Egress wire-in and lifecycle (2026-08-25)

- **Audit: NOT FILED — missing data per the never-gates rule.** The
  Developer completed shc-02 in an external harness and never filed
  `developer_docs/audits/shc-02-*.md`. The durable evidence is this page
  plus commit `b0528f8` and the independently re-run test suites below.
- **Scope landed** (verified against the live repo 2026-08-25): two
  `EventChannel.InspectForHealth` call sites in `EventChannel.Send`
  (direct-parquet branch line ~262; normal branch post-enrichment, above
  the `skipEsperSend` early return, line ~397); one-line
  `EventChannel.InspectForHealth(wm)` at `MemoryMapSensor.cs:308` before
  its direct `SendEventBean`; lifecycle in `WintapSvcCore.cs` —
  `SensorHealthMonitor.Default.Start()` after `subscriptionMgr.Start()`
  (line ~283) and `SensorHealthMonitor.Default.Stop()` first in `StopAsync`
  (line ~123).
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §InspectForHealth/§Send; ../wintap/wintap/platform/windows/sensor/etw/MemoryMapSensor.cs §308; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync/§StopAsync -->
- **Test results:** 5 shc-02 integration tests (single-inspection on both
  egress branches, failure visibility through egress, self-PID filter
  precedence, fail-open never breaking egress). Whole `Category~shc`
  suite **65/65 — independently re-run by the main session (Architect)
  2026-08-25**; full suite 165/165 and Release project build passing per
  the Developer; root solution retains the known MSB4249 issue.
- **Deviation (Architect-permitted):** the shc-02 tests initially hung on
  the WintapLogger first-touch issue (`ComponentLogger`'s permanent
  BackgroundWorker capturing xUnit's SynchronizationContext); the
  Architect permitted the same `Env.SetDataRoot(<temp>)`-before-first-touch
  fixture fix used in shc-03. Cataloged durably in
  [[wiki/diagnostic/windows-sensor-sweep-queue]].

## Availability anchor — manual live run (2026-08-25, Architect-accepted)

Manual live run on the lab host, **2026-08-25 05:39–05:41 local**, branch
build (`windows-sensor-health-check`). Excerpt recorded verbatim:

```
8/25/2026 5:39:33 AM [Info]  [WindowsStateManager.RefreshDriveMap]:   drive map refreshed via QueryDosDevice, mappings found: 2
8/25/2026 5:39:48 AM [Info]  [SubscriptionManager.Start]:   Starting WindowsSubscriptionManager
8/25/2026 5:40:56 AM [Warn]  [SensorHealthMonitor..ctor]:   SensorHealth FAIL: stream=Process check=process_unresolved count=1 samples: PID=-1 ActivityType=Refresh EventTime=134320520833210430 ProcessName=Unknown PidHashIsUnknownSentinel=false
```

**Why this artifact:** first live demonstration of the frozen criteria —
QueryDosDevice map active, egress checks flushing aggregated FAIL lines,
no false liveness stalls, low-noise. This is the feature's **availability
anchor** (frozen criterion 9); lead time = opened 2026-08-24 → available
2026-08-25 = **1 calendar day**. Two live findings from this run are
cataloged in [[wiki/diagnostic/windows-sensor-sweep-queue]]: the
PID=-1/ActivityType=Refresh `process_unresolved` hit (the health check's
first real catch) and the cosmetic `[SensorHealthMonitor..ctor]` caller
tag on FAIL lines.
