---
title: "Interview: Windows Sensor Health-Check"
type: concept
confidence: high
grounded_by: []
policy: agent-editable
last_validated: 2026-08-24
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/windows-sensor-health-check/interview.md
tags: [feature-work, health-check, windows-sensor, qa]
---

# Feature Interview: Windows Sensor Health-Check

## Initial Idea

Architect's original statement (2026-08-24): sweep through all non-process
sensors for Windows, evaluate them for efficiency and accuracy, fix any
obvious bugs, and instill an ongoing, low-overhead and low-noise health-check
QA system to flag inconsistencies. Inconsistencies include (but are not
limited to): invalid or missing PidHash, invalid or missing ProcessName, and
schema mismatch (attempting to save raw data into an inappropriate data type).

Scope was then narrowed by the Architect: **Windows sensors only**, and the
**health-check system comes first** as its own feature; the per-sensor
sweep/bug-fix pass is a separate follow-on feature that wires into it.

## Context Established Before Questioning

- Windows sensor inventory from the repo: non-process ETW sensors
  (`FileSensor`, `RegistrySensor`, `TcpSensor`, `UdpSensor`,
  `ImageLoadSensor`, `MemoryMapSensor`, `UISensor`, `WMISensor`,
  `GenericSensor`, `GroupPolicySensor`, `CpuTriggerSensor`, `APICallSensor`),
  non-ETW (`EventlogSensor`, `SensSensor`), cross-platform (`PcapCollector`,
  `OSQuerySensor`), plus `WindowsProcessSensor`.
- [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1) — metrics overlay
  protocol followed for this feature open.
- [[wiki/concept/feature-work-template]] — artifact skeletons used here.

## Interview Log

### Round 1

**Q:** Where should the health checks execute? (options: in-agent at message
egress; per-sensor hooks; offline/ETL-side; in-agent + offline)
**A:** In-agent, at message egress.
**Outcome:** decision — single choke point where every WintapMessage passes
before serialization; one implementation covers all sensors.

**Q:** How should inconsistencies be reported, given low-noise matters?
(options: aggregated health event; per-failure events; log file only;
Windows Event Log)
**A:** Aggregated health event.
**Outcome:** decision — per-sensor/per-check failure counters flushed
periodically as a dedicated health WintapMessage into the normal Parquet
stream, plus a capped first-N sample of offending events for diagnosis.

**Q:** Which sensors does the health-check cover at v1? (options: all Windows
sensors; non-process Windows sensors only)
**A:** All Windows sensors.
**Outcome:** decision — includes `WindowsProcessSensor`; checks are generic
and also protect the recent wpc/ptr work.

**Q:** What overhead posture for the always-on checks? (options: full-stream
cheap checks; sampling 1-in-N; configurable defaulting to full-stream)
**A:** Full-stream cheap checks.
**Outcome:** decision — every message gets constant-time field checks;
counters increment only on failure.

### Round 2 (2026-08-24, post-exploration redirection)

**Q:** (Engineer's exploration surfaced that the aggregated-health-message
design required a WintapMessage schema addition, an exemption from the
self-PID filter in EventChannel.Send, and a three-unit plan.)
**A:** Architect: "It feels overengineered. I don't want to have Schema
changes to WintapMessage just to support healthchecking. This is a supportive
feature, not the mission of wintap. I'd rather we start simple and extend if
needed: no sql tables for healthchecking. I just want log entries in
Wintap.log. Then we go from there."
**Outcome:** decision — reporting channel changed from aggregated health
WintapMessage (Parquet/DuckDB) to **periodic aggregated entries in
Wintap.log via WintapLogger**. No WintapMessage schema changes anywhere in
this feature. Logged as a criteria amendment per the mini-lab guardrails.

## Decisions

- Health checks run **in-agent at the WintapMessage egress choke point**,
  before serialization.
- Reporting is **aggregated log entries in Wintap.log** (amended in Round 2;
  originally a dedicated health WintapMessage into the Parquet stream):
  per-sensor/per-check failure counters flushed periodically as log lines,
  with a capped first-N sample of offending events. No per-failure log spam,
  no new WintapMessage types, no new output tables.
- **No WintapMessage schema changes** in this feature (Round 2).
- **Coverage: all Windows sensors**, process included.
- **Full-stream constant-time checks**; no sampling in v1.
- Start minimal and extend only if needed — supportive feature, not the
  mission (Round 2).

## Constraints

- Low overhead and low noise are first-class requirements, not preferences.
- Windows platform only.

## Delegations

- Exact check implementations, health message schema, flush cadence, sample
  cap, and the concrete egress hook location: delegated to the Engineer's
  exploration and design.
- Feature abbreviation for instruction units: Engineer declares in the
  implementation plan (suggestion: `shc`).

## Deferred / Open Questions

- Offline/ETL-side (DuckDB) validation query pack — possible later addition,
  out of scope for v1.
- Per-sensor bug fixes surfaced by the health check — belong to the follow-on
  sweep feature.
- Linux/macOS coverage — out of scope.

## Playback Summary

An always-on, low-overhead, low-noise QA layer inside the Windows agent that
validates every WintapMessage at a single egress choke point before
serialization. v1 checks: invalid/missing PidHash, invalid/missing
ProcessName, and schema/type fitness — designed so sensor-specific invariants
can be added later. Failures are counted per sensor and per check and flushed
periodically as a dedicated health message into the normal Parquet stream,
with a capped first-N sample of offending events for diagnosis. Covers all
Windows sensors including WindowsProcessSensor. Non-goals: fixing the sensor
bugs it finds (follow-on sweep feature), Linux/macOS sensors, offline
ETL-side validation. Architect confirmed this summary before the sealed
questions were asked.

## Sealed — human estimates

<Asked as the interview's final two questions, answers recorded as given.
SEALED: any agent that will produce its own estimates (e.g. the Wintap
Engineer at exploration start) must not read this section until feature
close-out. See [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1) and
[[wiki/concept/velocity-metric]].>

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available? (Forced counterfactual — answer even if you would not have
attempted it solo. The hours are the feature's solo-hours: the Velocity
numerator and portfolio weight. The calendar date absorbs weekends and
distractions.)**
**A:** 40 hours. (No solo calendar availability date given — missing data,
per never-gates.)

**Q: With the AI workflow, on what date do you predict this feature will be
available? (Calendar prediction, open date to availability.)**
**A:** "1 - 2 days" — from the open date of 2026-08-24, i.e. predicted
availability 2026-08-25 to 2026-08-26.
