---
title: "Implementation Plan: Windows Sensor Health-Check"
type: concept
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/work/windows-sensor-health-check/design.md
  - ../wintap/CLAUDE.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: llm-agent
status: reviewed
source_paths: wiki/work/windows-sensor-health-check/implementation_plan.md
tags: [feature-work, health-check, windows-sensor, qa, instruction-units]
---

# Implementation Plan: Windows Sensor Health-Check

> **Revised 2026-08-24 three times:** (#1, Architect redirection) reporting
> is Wintap.log only; no WintapMessage schema changes; plan reduced from
> three units to **two**. (#2, Architect review of shc-01) the v1 check
> list is definitive — `process_unresolved` ("Unknown" fails) and
> `path_unqualified` (File/Registry fully-qualified paths) added, the
> six-stream 5-second liveness watchdog added, `eventtime_invalid` dropped.
> (#3, Architect decision on the shc-02 elevation conflict) a new enabling
> unit **shc-03** replaces the diskpart drive mapping with QueryDosDevice;
> **shc-02 is paused and shc-03 lands first despite the number** — see
> Execution Order below. Not a criteria amendment: the frozen acceptance
> criteria in brief.md are unchanged.

**Feature abbreviation: `shc`** (declared here per the 2026-08-17 unit
naming convention; verified no collision — `developer_docs/instructions/`
currently holds only `P1.1`, `wpc-*`, and `ptr-*` prefixes). Units are
`shc-01`, `shc-02`, and `shc-03`; traits `[Trait("Category", "shc-NN")]`;
run one unit with `dotnet test --filter "Category=shc-01"`, the feature
with `dotnet test --filter "Category~shc"`.

**Execution order: shc-01 → shc-03 → shc-02.** shc-03 was inserted
2026-08-24 after the Developer, mid-shc-02, correctly stopped on an
instruction/codebase conflict: the shc-02 no-admin integration tests
initialize `StateManager`, whose `WindowsStateManager.RefreshDriveMap()`
spawns `diskpart.exe`, which requires elevation. shc-02 is incomplete (no
audit filed) and paused until shc-03 lands; it then resumes under its
already-approved instruction unchanged.

**Working branch:** `windows-sensor-health-check` off `develop` (ptr/wpc
pattern).

## Scope

Three units, each independently buildable/testable (execution order
shc-01 → shc-03 → shc-02):

### shc-01 — Health-check engine, checks, liveness, and periodic log flush (no wiring)

`SensorHealthMonitor` + `IWintapHealthCheck` + the five definitive v1
checks (`pidhash_missing`, `process_unresolved`, `processname_missing`,
`payload_mismatch`, `path_unqualified`), monotonic fixed-array counters,
capped first-N sample capture, the six-stream 5-second liveness watchdog
(transition-only Error/Info logging, 60 s startup grace, Stop()
suppression), the flush timer producing key=value `SensorHealth` summary
and FAIL lines through an injectable log sink (production default:
WintapLogger), and the three config keys (`WINTAP_HEALTH_ENABLED`,
`WINTAP_HEALTH_FLUSH_SECONDS`, `WINTAP_HEALTH_SAMPLE_CAP`). **Nothing in
production calls it yet.**
Instruction: `developer_docs/instructions/shc-01-health-check-core.md`.

### shc-03 — Replace the diskpart drive mapping with QueryDosDevice (enabling unit; lands before shc-02 resumes)

Replace the elevation-requiring `diskpart.exe` spawn/script/stdout-parse in
`WindowsStateManager.RefreshDriveMap()` with per-drive-letter
`QueryDosDevice` P/Invoke calls (in-repo precedent:
`WindowsProcessSensor.TryTranslateDevicePathToWin32Path`). Parse the
trailing volume number from `\Device\HarddiskVolume<N>` names into the
existing `DiskVolume { VolumeNumber, VolumeLetter }` shape. Never throws
(fail-soft: skip non-HarddiskVolume letters, Warn and return accumulated on
unexpected error). **Widened same day by Architect decision:** also fixes
the consumer-side guard in `BaseWindowsSensor.fromNative` — the
`volumeNumber <= diskVolumes.Count` check is replaced with a direct
`VolumeNumber` lookup (translate on match; preserve the existing logged
`c:` fallback on a genuine miss; remove the dead single-drive
`harddiskvolume1` hack; `private` → `internal` for testability) — so the
accuracy fix is realized immediately rather than deferred to the sweep.
Scoped exception to the feature's no-sensor-changes posture for exactly
this file/fix. `StateManager` ctor caller unchanged. No-admin unit tests
via a `BuildDriveMap(Func<char,string>)` seam, `fromNative`
translation-path tests (old-guard breakage case, multi-drive letter
selection, genuine-miss fallback, format preservation), plus one lenient
live-API smoke test. Rationale: unblocks shc-02's no-admin tests; fixes
the diskpart-index-vs-NT-volume-number correctness bug end-to-end (the
feature's first genuine accuracy fix); removes locale-fragile fixed-column
parsing; 26 cheap API calls instead of a process spawn.
Instruction: `developer_docs/instructions/shc-03-querydosdevice-drive-map.md`.

### shc-02 — Egress wire-in and end-to-end verification (**paused pending shc-03**)

The two `Inspect` call sites in `EventChannel.Send` (pre-DirectParquetSink
and pre-SendEventBean), the one-line `Inspect` at MemoryMapSensor's
direct-send site (also the prerequisite for meaningful MemoryMap liveness),
monitor `Start()` at service startup and `Stop()` (final best-effort flush,
liveness suppression) at shutdown; integration tests via the existing
`WINTAP_SKIP_*` seams; documented manual live run (periodic `SensorHealth`
lines in Wintap.log, liveness behavior consistent with host activity,
before/after events-per-second sanity check) recorded in `verification.md`
— the feature's availability-anchor candidate. Depends on shc-01 **and
shc-03** (its no-admin integration tests hit the diskpart elevation
requirement through the `StateManager` type initializer; Developer stopped
correctly on the conflict 2026-08-24, no audit filed, unit paused). Resumes
under the already-approved instruction unchanged.

## Steps

1. Architect approves the revised `shc-01` instruction → Developer
   implements → audit. **(Done 2026-08-24.)**
2. shc-02 started, stopped on the diskpart elevation conflict, paused.
   Engineer drafts `shc-03` (with per-unit estimate) → Architect approves →
   Developer implements → audit.
3. Developer resumes and completes `shc-02` → audit + manual run in
   `verification.md`.
4. Architect accepts against the re-frozen brief criteria; Engineer folds
   results into the wiki and runs mini-lab close-out.

## Files Likely To Change

- New: `wintap/core/infrastructure/health/SensorHealthMonitor.cs`,
  `.../IWintapHealthCheck.cs`, `.../DefaultHealthChecks.cs` (shc-01)
- `wintap/platform/windows/infrastructure/WindowsStateManager.cs` (shc-03)
- `wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs` (shc-03;
  `fromNative` guard fix only — scoped sensor-file exception by Architect
  decision 2026-08-24)
- `wintap/core/infrastructure/EventChannel.cs` (shc-02)
- `wintap/platform/windows/sensor/etw/MemoryMapSensor.cs` (shc-02)
- Service lifecycle site, e.g. `wintap/core/infrastructure/WintapSvcCore.cs`
  (shc-02)
- New tests under `tests/Wintap.Tests/` per unit

## Tests To Add Or Update

- shc-01: pure unit tests (counters, samples, window drain/reset, log-line
  formatting via injected sink, flush-timer config parse, extensibility via
  custom check, disabled mode, ProcessPartial alias, unknown-enum bucket,
  fail-open, parallel-increment smoke; unknown-sentinel and "Unknown"
  matrices for `process_unresolved` via the injected sentinel seam;
  accepted/rejected path-form matrices for `path_unqualified`; liveness
  state machine via a direct tick seam — grace period, single stall line on
  transition, silence while stalled, recovery line with duration, Stop()
  suppression and grace re-arm).
- shc-03: no-admin parse/mapping tests via the `BuildDriveMap` seam
  (acceptance and rejection matrices for `\Device\HarddiskVolume<N>` vs.
  network/SUBST/optical/malformed names, mixed-environment mapping,
  all-unassigned, per-letter fault isolation), `fromNative`
  translation-path tests via the `private` → `internal` accessibility seam
  (NT number > drive count now translates — the old-guard breakage case;
  multi-drive correct-letter selection; genuine miss falls back to the
  legacy logged `c:` path; rewritten-path format preservation; quoted-path
  cleanup), plus one lenient live `QueryDosDevice` smoke test (no
  elevation, no drive-layout assumptions).
- shc-02: egress inspection via skip-seams, MemoryMapSensor site coverage,
  start/stop lifecycle, fail-open non-interference with telemetry.

## Migration Or Compatibility Notes

- No schema, serializer, EPL, or output-format change of any kind; the only
  new output is Wintap.log text. Downstream (Wintappy/DuckDB) is untouched.
- The monitor compiles into Lintap/Mactap but defaults disabled off-Windows.

## Rollback Plan

`WINTAP_HEALTH_ENABLED=false` disables the layer at runtime with only a flag
check remaining on the hot path; full rollback is reverting the feature
branch merge (the units touch no existing schema or telemetry semantics).

## Done Checklist

- [x] shc-01 implemented, audited, tests pass (2026-08-24 — 33/33 via
  `dotnet test --filter "Category=shc-01"`, independently re-verified by the
  main session same day; audit
  `../wintap/developer_docs/audits/shc-01-health-check-core.md`; no
  production files modified; documented deviation: solution-level
  `dotnet build -c Release` fails with the known Wintap-Workbench MSB4249
  issue, approved project-scoped fallback used)
- [x] shc-03 implemented, audited, tests pass (2026-08-25 — 27/27 via
  `dotnet test --filter "Category=shc-03"`; commit `26ce94c`; audit
  `../wintap/developer_docs/audits/shc-03-querydosdevice-drive-map.md`;
  non-elevated run confirmed)
- [x] shc-02 implemented, tests pass (2026-08-25 — commit `b0528f8`;
  5 integration tests; whole `Category~shc` suite 65/65 independently
  re-run by the main session 2026-08-25; full suite 165/165. **Audit
  never filed** — Developer worked in an external harness; recorded as
  missing data per never-gates, durable evidence in verification.md.
  Architect permitted the shc-03-pattern `Env.SetDataRoot` fixture fix
  for the WintapLogger first-touch hang — cataloged in
  [[wiki/diagnostic/windows-sensor-sweep-queue]])
- [x] Manual live run documented in verification.md (availability anchor:
  2026-08-25 05:39–05:41 lab-host run, Architect-accepted)
- [x] Architect accepted against re-frozen brief criteria (2026-08-25)
- [x] Wiki fold-in + mini-lab close-out complete (2026-08-25 — Feature
  Velocity 7.0, uncertainty 3.5–17; canonical page
  [[wiki/component/sensor-health-monitor]]; sweep queue
  [[wiki/diagnostic/windows-sensor-sweep-queue]]; rollup row in
  [[wiki/metrics]])
