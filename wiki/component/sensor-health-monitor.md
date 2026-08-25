---
title: "Sensor Health Monitor (Windows Egress QA Layer)"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/health/SensorHealthMonitor.cs
  - ../wintap/wintap/core/infrastructure/health/IWintapHealthCheck.cs
  - ../wintap/wintap/core/infrastructure/health/DefaultHealthChecks.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/infrastructure/WintapSvcCore.cs
  - ../wintap/wintap/platform/windows/sensor/etw/MemoryMapSensor.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs
  - ../wintap/wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wintap/core/infrastructure/health; wintap/core/infrastructure; wintap/platform/windows
tags: [wintap, windows-sensor, component, health-check, qa, data-quality, egress, liveness, drive-map]
---

# Sensor Health Monitor

Always-on, low-overhead, low-noise QA layer inside the Windows agent,
delivered by the `windows-sensor-health-check` feature (opened 2026-08-24,
closed 2026-08-25; units shc-01/shc-02/shc-03). It validates every
`WintapMessage` at the egress choke point and reports aggregated results as
periodic `SensorHealth` lines in Wintap.log — **no WintapMessage schema
change, no new output tables; the only output is log text**.

## Egress hook

`EventChannel.InspectForHealth(msg)` dispatches to
`SensorHealthMonitor.Default` (or a test override seam
`HealthMonitorOverride`). Three call sites give exactly one inspection per
egressing message:
1. the `DirectParquetSink` branch of `EventChannel.Send` (pre-enrichment by
   that branch's design; the branch returns, so no double inspection);
2. the normal branch post-enrichment, immediately above the `skipEsperSend`
   early return that guards `SendEventBean`;
3. one line in `MemoryMapSensor` before its direct `SendEventBean` bypass
   (`MemoryMapSensor.cs:308`).
Messages dropped earlier by the self-PID filter are never inspected.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §InspectForHealth/§Send; ../wintap/wintap/platform/windows/sensor/etw/MemoryMapSensor.cs §308 -->

## Checks (v1, definitive by Architect amendment #2)

Fixed registry of constant-time, never-throwing `IWintapHealthCheck`
implementations; failure counters per (sensor stream keyed by MessageType,
check); capped first-N samples:

- `pidhash_missing` — PidHash null/empty/whitespace
- `process_unresolved` — ProcessName == "Unknown" (OrdinalIgnoreCase) OR
  PidHash == the host-specific unknown sentinel `GenPidHash(-1, 0)`
- `processname_missing` — ProcessName null/empty/whitespace
- `payload_mismatch` — payload object for the MessageType missing/null
  (`ProcessPartial → Process` alias)
- `path_unqualified` — File/Registry only: File.Path must be rooted
  `x:\`, `\\`, or `\device\`; Registry.Path rooted `registry\` (lowercase
  per the sensors' normalization)
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/health/DefaultHealthChecks.cs -->

New checks register without touching the hook or reporting machinery
(demonstrated by unit test). `eventtime_invalid` is the first candidate
future check — see [[wiki/diagnostic/windows-sensor-sweep-queue]].

## Liveness watchdog

Six high-volume streams — File, Registry, MemoryMap, ImageLoad,
TcpConnection, UdpPacket — must show a nonzero inspected count per fixed
5-second tick. Transition-only logging: one Error `STALL` line on
OK→STALLED, one Info `RECOVERED` line with stall duration on return; 60 s
startup grace after `Start()`; `Stop()` suppresses alarms and re-arms grace.
Counters are monotonic lifetime totals; flush and liveness each diff against
their own snapshots, so the hot path is one `Interlocked.Increment` plus the
check evaluations.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/health/SensorHealthMonitor.cs -->

## Reporting and lifecycle

A flush timer (default 60 s) writes via WintapLogger: one key=value summary
line per active window (per-stream checked counts) and one Warn `FAIL` line
per (stream, check) with nonzero count plus up to N samples. Idle windows
write nothing; nothing is ever written per failure. Fail-open: any internal
health-layer exception disables the monitor for the session with a single
Warn line, never breaking telemetry egress. Lifecycle:
`SensorHealthMonitor.Default.Start()` right after `subscriptionMgr.Start()`
(not started when `WINTAP_DISABLE_SENSORS` is set); `Stop()` is the first
action in `StopAsync` (final best-effort flush before the logger closes).
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync/§StopAsync -->

Config (env-overridable): `WINTAP_HEALTH_ENABLED` (default true on Windows,
false elsewhere), `WINTAP_HEALTH_FLUSH_SECONDS` (default 60, min 5),
`WINTAP_HEALTH_SAMPLE_CAP` (default 3, clamp 0–20). The 5 s tick and 60 s
grace are fixed constants, not tunables.

## Companion fix: QueryDosDevice drive map (shc-03)

`WindowsStateManager.RefreshDriveMap()` no longer spawns elevated
`diskpart.exe`; it builds the map from per-letter `QueryDosDevice` calls,
parsing `\Device\HarddiskVolume<N>` into `DiskVolume { VolumeNumber,
VolumeLetter }`, never throwing (non-HarddiskVolume and unassigned letters
skipped). This fixed a real correctness bug: diskpart's `Volume ###` column
is an enumeration index, not the NT volume number
`BaseWindowsSensor.fromNative` looks up. `fromNative` now does a direct
`VolumeNumber` lookup (old `volumeNumber <= diskVolumes.Count` guard and the
dead single-drive `harddiskvolume1` hack removed; legacy logged `c:`
fallback preserved on a genuine miss), so `\device\harddiskvolumeN\...`
process paths translate correctly on multi-drive hosts.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs §RefreshDriveMap/§BuildDriveMap; ../wintap/wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs §fromNative -->

## Verification state (2026-08-25)

65/65 `Category~shc` tests (33 shc-01 engine/checks/liveness, 27 shc-03
drive-map/translation, 5 shc-02 egress integration); full suite 165/165;
availability demonstrated by a live lab-host run 2026-08-25 (see
[[wiki/work/windows-sensor-health-check/verification]]). Known first catch
and open follow-ups live in [[wiki/diagnostic/windows-sensor-sweep-queue]].

## Related

- [[wiki/component/windows-sensor-service-internals]] — service lifecycle and EventChannel routing
- [[wiki/work/windows-sensor-health-check/design]] — full design record and grounding
- [[wiki/work/windows-sensor-health-check/brief]] — the nine frozen acceptance criteria
- [[wiki/diagnostic/windows-sensor-sweep-queue]] — follow-on sweep-feature queue
