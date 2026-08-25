---
title: "Interview: Improve Windows Registry Collection"
type: concept
confidence: high
grounded_by: []
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: mixed
status: draft
source_paths: wiki/work/improve-windows-registry-collection/interview.md
tags: [feature-work, registry, etw, windows-sensor, capture-mode]
---

# Feature Interview: Improve Windows Registry Collection

## Initial Idea

Architect's original statement (main session, 2026-08-24): the Windows
`RegistrySensor` is defective — it parses ETW payloads via
`obj.ToString()`/`Split('"')` fixed indices, re-reads the live registry per
event (TOCTOU, double OpenKey), keeps unbounded caches (`RegValueCache`,
`RegParents`), and its `ExpandString` decode always returns `""`. Replace it
with a correct, efficient manifest-provider-based sensor.

## Context Established Before Questioning

This feature opens **after** a completed proof-of-concept spike (POC-first
model): a multi-day probe series in `C:\PUBLIC\wrc-poc` run in the main
session with the Architect executing all elevated commands. The spike
discovered an undocumented capture mode of the
`Microsoft-Windows-Kernel-Registry` provider (4-byte `0xFFFFFFFF`
`EVENT_FILTER_DESCRIPTOR` payload via `EnableTraceEx2`) that makes the kernel
populate `KeyName`, `CapturedData`, and `PreviousData` on registry events —
closing a gap publicly documented as an unfixable Microsoft limitation. Full
evidence lives in the probe logs (`C:\PUBLIC\wrc-poc\*.log`) and will be
recorded durably in the feature's ADR and retroactive spike instructions
(wrc-01, wrc-02).

- [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1) — metrics overlay
  protocol followed for this feature open.
- [[wiki/concept/feature-work-template]] — artifact skeletons used here.

## Interview Log

The adaptive question rounds were skipped: scope, approach, and design inputs
were fully settled during the spike sessions (2026-08-23/24) before feature
open. The playback below was confirmed by the Architect on 2026-08-25.

### Playback (confirmed 2026-08-25)

- **Decision** — Manifest-only sensor. Drop entirely: XML-string parsing,
  live registry re-reads, `RegValueCache`/`RegParents`, KCB/classic rundown
  machinery (classic KCB addresses proved uncorrelatable with
  manifest-provider `KeyObject` pointers: 0 hits / ~18k lookups).
- **Decision** — Enable the provider with the 4-byte capture filter;
  periodic re-assert (covers clobber-to-zero, reboot, unknown reset paths).
  Consider a clobber-detection heuristic (canary write to a Wintap-owned key).
- **Decision** — Session-level keyword mask chosen per downstream needs
  (avoid the ~17k events/s all-keywords firehose); measure overhead with
  capture on.
- **Decision** — Typed payload parsing by numeric event ID; decode
  `CapturedData` per REG type; emit pre/post values from `SetValueKey`.
- **Decision (2026-08-25)** — probe7 (clear-behavior test: valid 4-byte
  descriptor with flags=0) **not run**, per Architect. Reboot persistence and
  deliberate-clear semantics remain documented unknowns; the periodic
  re-assert design covers them regardless.
- **Constraint** — ETW session names must never be `NT Kernel Logger`; no
  live ETW tests concurrent with the windows-sensor-health-check feature's
  tests. Architect runs all elevated commands manually.
- **Constraint** — No new NuGet dependencies anticipated (P/Invoke only);
  flag to Architect if that changes.
- **Delegated** — Production approach to session-handle acquisition for
  `EnableTraceEx2` (POC's reflection into TraceEvent's private
  `m_SessionHandle` is version-fragile) is an ADR question for the Engineer
  to frame with options.

## Sealed — human estimates

<Asked as the interview's final two questions, answers recorded as given.
SEALED: any agent that will produce its own estimates (e.g. the Wintap
Engineer at exploration start) must not read this section until feature
close-out. See [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1) and
[[wiki/concept/velocity-metric]].>

**Q: If you had to build this exact scope alone, without AI — including the
ETW filter reverse-engineering that made it possible — how many working hours
would it take? And on what date would it realistically have been available?
(Forced counterfactual — answer even if you would not have attempted it solo.
The hours are the feature's solo-hours: the Velocity numerator and portfolio
weight. The calendar date absorbs weekends and distractions.)**
**A:** "6 weeks" — interpreted as 240 working hours (6 × 40 h). No explicit
solo calendar availability date given; 6 calendar weeks from the open date of
2026-08-25 implies ~2026-10-06 (derived from the answer, not separately
stated).

**Q: With the AI workflow, on what date do you predict this feature will be
available? (Calendar prediction, open date to availability.)**
**A:** "2 days" — from the open date of 2026-08-25, i.e. predicted
availability 2026-08-26 to 2026-08-27.
