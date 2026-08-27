---
title: "Brief: Windows Sensor Health-Check"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/etl/load/DirectParquetSink.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/shared/ProcessHash.cs
  - ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
policy: agent-editable
last_validated: 2026-08-24
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/windows-sensor-health-check/brief.md
tags: [feature-work, health-check, windows-sensor, qa, data-quality]
---

# Feature Brief: Windows Sensor Health-Check

Feature opened 2026-08-24. Interview record:
[[wiki/work/windows-sensor-health-check/interview]].

> **Amended 2026-08-24 #1 (Architect redirection):** reporting channel is
> **periodic aggregated Wintap.log entries via WintapLogger** — no
> WintapMessage schema changes, no Parquet/DuckDB health output.
>
> **Amended 2026-08-24 #2 (Architect review of shc-01):** the v1 check list
> is now definitive. "Unknown" process attribution **fails** (reversing the
> earlier pass note — "this is exactly the failure mode i want to catch");
> File/Registry paths must be fully qualified; six high-volume streams must
> show liveness per 5-second interval; `eventtime_invalid` is dropped from
> v1. Both amendments are logged in `metrics.md` `criteria_amendments`; the
> criteria below are the re-frozen set.

## Problem

Wintap's Windows sensors emit full-fidelity telemetry through a shared
egress path, but nothing validates what they emit. Known failure classes —
missing PidHash, unresolved ("Unknown") process attribution, payload/schema
mismatches, unqualified File/Registry paths, and silently stalled event
streams — are today either swallowed (e.g. `DefaultSerializer` catches
reflection failures at Debug level; `Serializer.Save` throws `NULL_PIDHASH`
into a swallowed exception) or invisible until a researcher hits bad rows in
DuckDB. There is no always-on, low-overhead QA layer that makes sensor
data-quality defects observable.

## Goals

- An always-on, low-overhead, low-noise QA layer inside the Windows agent
  validating every WintapMessage at the in-agent egress choke point, before
  serialization.
- Definitive v1 conditions (Architect, 2026-08-24): PidHash present and
  never unknown; ProcessName present and never the "Unknown" sentinel;
  payload/schema fitness per MessageType; fully qualified File and Registry
  paths; per-5-second liveness on the six known high-volume streams (File,
  Registry, MemoryMap, ImageLoad, TcpConnection, UdpPacket).
- Aggregated reporting: per-sensor-stream/per-check failure counters flushed
  periodically as summary lines in Wintap.log via WintapLogger, plus a
  capped first-N sample of offending events; liveness reported on state
  transitions only.
- Extensible check registry so sensor-specific invariants can be added later
  without touching the egress hook or the reporting machinery.
- Coverage: all Windows sensors, including WindowsProcessSensor.

## Non-Goals

- Fixing the sensor bugs the checks surface (separate follow-on sweep
  feature).
- Linux/macOS sensor coverage.
- Offline/ETL-side (DuckDB) validation query pack.
- Per-failure logging or event emission; any sampling scheme (v1 is
  full-stream constant-time checks); per-silent-interval liveness logging.
- Any WintapMessage schema change, health message type, Parquet/DuckDB
  health output, or SQL table.
- EventTime plausibility checking (`eventtime_invalid` — dropped from v1 by
  Architect review; preserved in design.md as a future candidate check).

## User-Facing Behavior

An operator or researcher inspecting Wintap.log sees, on a periodic cadence,
compact machine-parseable `SensorHealth` summary lines: which sensor streams
were checked in the window (with message counts), and — only when failures
occurred — per-check failure counts with up to N compact samples of the
offending events. When a high-volume stream goes silent for a 5-second
interval, exactly one stall line is written (and one recovery line with the
stall duration when it resumes) — never a line per silent interval. A
healthy quiet system produces at most one short summary line per flush
window; an idle system produces none. Cadence and sample cap are tunable via
standard `WINTAP_*` config keys; the layer can be disabled entirely.

## Acceptance Criteria

**FROZEN (re-frozen under amendment #2, 2026-08-24)** per
[[wiki/decision/ai-velocity-roi-mini-lab]] guardrail 1. Any further change
is a logged amendment in `metrics.md` `criteria_amendments`.

1. **Egress hook.** A health-check inspection executes for every
   WintapMessage that reaches the in-agent egress choke point
   (`EventChannel.Send`) before serialization, on **both** egress branches:
   the Esper/serializer path and the `DirectParquetSink` direct-parquet
   path. The known `MemoryMapSensor` direct-send bypass site is also
   inspected.
2. **Definitive v1 checks.** Five per-message check families are implemented
   and enabled by default:
   (a) `pidhash_missing` — PidHash null/empty/whitespace fails;
   (b) `process_unresolved` — attribution that fell back to the unknown
   sentinel fails: ProcessName equal to `"Unknown"` (case-insensitive) or
   PidHash equal to the resolver's unknown-sentinel hash
   (`ProcessHash.GenPidHash(-1, 0)`);
   (c) `processname_missing` — ProcessName null/empty/whitespace fails;
   (d) `payload_mismatch` — the payload object matching the declared
   MessageType must be present (with the `ProcessPartial → Process` alias);
   (e) `path_unqualified` — for File and Registry streams only, the payload
   path must be fully qualified in the sensors' grounded emitted forms
   (File: drive-letter-rooted `x:\...`, UNC `\\...`, or device
   `\device\...`, all lowercase; Registry: rooted at lowercase
   `registry\...`); other streams are exempt.
   Each check is constant-time per message; failure counters increment only
   on failure.
3. **Stream liveness.** The six known high-volume streams — File, Registry,
   MemoryMap, ImageLoad, TcpConnection, UdpPacket — are each required to
   have a nonzero inspected count per 5-second interval. A zero interval
   (after a startup grace period) is reported as a critical condition with
   **exactly one** Error-level stall line at the state transition, and
   exactly one Info-level recovery line (including stall duration) when the
   stream resumes — never a line per silent interval. Stall alarms are
   suppressed across `Stop()`/`Start()` (grace re-arms).
4. **Aggregated log reporting.** Failure counts are aggregated per sensor
   stream (keyed by MessageType) and per check, and flushed on a
   configurable periodic cadence (default 60 s) as compact, key=value
   parseable summary lines written to Wintap.log via WintapLogger.
   Per-stream messages-checked counts appear in the summary so failure
   *rates* are computable from the log. No line is ever written per failure;
   an idle window writes nothing.
5. **Capped samples.** Failure reporting includes at most a configurable
   first-N sample (default 3 per sensor-stream/check per window) of compact
   offending-event summaries.
6. **Kill switch and overhead posture.** The layer can be disabled via
   config; when disabled, the egress hot path performs no health work beyond
   a flag check. When enabled, per-message work is constant-time and
   allocation-free on the pass path.
7. **Extensibility.** A new check can be added by registering an additional
   check implementation, without modifying the egress hook or the
   flush/reporting machinery — demonstrated by a unit test that registers a
   custom check.
8. **No schema or output-format changes.** WintapMessage, all payload
   classes, all serializers, and all Parquet/DuckDB outputs are untouched;
   the feature's only output is Wintap.log lines.
9. **Verification.** All `shc-*` unit tests pass via
   `dotnet test --filter "Category~shc"`; a documented manual run on a live
   Windows host shows periodic `SensorHealth` summary lines with nonzero
   checked counts in Wintap.log, liveness behavior consistent with the
   host's activity, and no measurable events-per-second regression.

## Affected Areas

- New: `wintap/core/infrastructure/health/` (engine, checks, liveness, log
  flush)
- `wintap/core/infrastructure/EventChannel.cs` (two `Inspect` call sites)
- `wintap/platform/windows/sensor/etw/MemoryMapSensor.cs` (one `Inspect`
  call at its direct-send site — also a prerequisite for meaningful
  MemoryMap liveness)
- Service lifecycle site (monitor start/stop)
- `tests/Wintap.Tests/`

## References

- [[wiki/work/windows-sensor-health-check/interview]] — settled decisions
  and redirections
- [[wiki/work/windows-sensor-health-check/design]] — architecture and
  grounding (unknown sentinel, path forms)
- [[wiki/work/windows-sensor-health-check/implementation_plan]] — shc units

## Open Questions

None. Amendment #2 made the v1 check list definitive; MemoryMapSensor gets
a one-line inspect call in the wire-in unit; `eventtime_invalid` and further
sensor-specific invariants are future candidates via the check registry.

## Test Plan

- Pure unit tests for the check engine: counters, samples, flush/reset,
  extensibility, disabled mode, thread-safety smoke — no ETW, no admin.
- Unit tests for each definitive check including the unknown-sentinel and
  path-form matrices, via injected sentinel/log-sink seams.
- Unit tests for the liveness state machine: grace period, single stall
  line on transition, no repeat lines while stalled, recovery line with
  duration, suppression across Stop().
- Egress integration tests using the existing `WINTAP_SKIP_*` seams
  (shc-02).
- Manual live run: verify periodic `SensorHealth` lines in Wintap.log and
  events-per-second sanity.

## Done When

All nine frozen acceptance criteria are demonstrated by dated artifacts
(audits per unit plus a verification entry for the manual run), and the
Architect accepts the validation evidence.
