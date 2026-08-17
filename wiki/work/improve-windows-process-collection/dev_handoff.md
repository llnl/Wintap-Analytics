---
title: "Dev Handoff: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-windows-process-collection/implementation_plan.md
  - ../wintap/CLAUDE.md
policy: agent-editable
last_validated: 2026-08-13
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/improve-windows-process-collection/dev_handoff.md
tags: [feature-work, dev-handoff, process-events, etw, windows-sensor]
---

# Dev Handoff: Improve Windows Process Collection

## How This Feature Is Executed

Unlike earlier features handed to a single code-development session, the
wintap repo now runs the Architect/Engineer/Developer methodology
(`../wintap/CLAUDE.md`): the Architect (human, main session in
`C:\PUBLIC\wintap`) dispatches the **Engineer** subagent to turn each
implementation-plan step into one self-contained instruction document under
`developer_docs/instructions/P2.x-*.md`, approves it, then dispatches the
**Developer** subagent to implement exactly that unit with xUnit tests
(`[Trait("Category", "P2.x")]`) and file an audit artifact. This handoff is
the bridge: it tells the Engineer where the approved feature context lives.

## Copy/Paste Prompt

Use this prompt (in the `C:\PUBLIC\wintap` Architect session) to dispatch the
Engineer for the first unit:

    Draft the instruction document for unit P2.1 (SID extraction helper) of
    the improve-windows-process-collection feature.

    Feature context (read all of these first):

    - C:\PUBLIC\Wintap-Analytics\wiki\work\improve-windows-process-collection\brief.md
    - C:\PUBLIC\Wintap-Analytics\wiki\work\improve-windows-process-collection\references.md
    - C:\PUBLIC\Wintap-Analytics\wiki\work\improve-windows-process-collection\design.md
    - C:\PUBLIC\Wintap-Analytics\wiki\work\improve-windows-process-collection\implementation_plan.md
    - C:\PUBLIC\sid-extraction-test\ProcessTraceDataExtensions.cs (the
      validated code to port)

    The instruction must be self-contained: the Developer will not read the
    Analytics wiki. Carry over the constraints verbatim: no
    WintapMessage/ProcessObject schema changes, no PidHash formula changes,
    TraceEvent stays at 3.1.23, no new NuGet dependencies. Verification gate:
    dotnet build -c Release plus dotnet test --filter "Category=P2.1".

For subsequent units, repeat with the matching step from
implementation_plan.md (P2.2 sensor core, P2.3 snapshot refresh, P2.4
enrichment, P2.5 stop-metrics merge, P2.6 wire-in/removal, P2.7 boot ETL,
P2.8 verification harness). Dispatch the Developer only after the Architect
approves each instruction — never hand an unapproved instruction to the
Developer.

## Handoff Summary

Greenfield replacement of Windows process collection, fully specified:
interview complete (all decisions human-confirmed), design settled, plan
sliced into eight P2.x units. The SID-extraction technique is already
validated in a standalone POC and ports as-is. No open design questions block
slice 1; the three open questions in design.md (correlation window length,
boot-replay stop events, QA counter home) have stated defaults and are tuned
or decided during verification/closeout.

## Primary Sources For The Dev Agent

Per unit, the Engineer should quote or reference into the instruction:

- `C:\PUBLIC\sid-extraction-test\ProcessTraceDataExtensions.cs` — port source
  for P2.1 (offset derivation comments included; keep them).
- `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs` —
  `KernelParser.Instance.EtwParser.<Event> += handler` subscription pattern
  (P2.2); see FileSensor/TcpSensor for live examples.
- `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
  — process-sensor-first bootstrap and kernel-flag aggregation (P2.2, P2.6,
  P2.7 ordering constraint).
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` and
  `KernelProcessSensor.cs` — behavior being replaced; the manifest
  ProcessStop field list in `parseUserModeProcessStop` is the exact metric
  set P2.5 must retain; both files are deleted in P2.6.
- `../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs` — Linux
  snapshot-refresh precedent for P2.3's shape.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` and
  `ProcessResolver.cs` — Send/registration contract and start-time-tolerance
  behavior the sensor relies on; read-only for this feature unless a unit
  says otherwise.
- `../wintap/tests/Wintap.Tests/WintapMessageTests.cs` — existing test style
  and trait convention (P1.1).

## Recommended First Implementation Slice

P2.1 (SID extraction helper). Smallest unit, pure logic, highest test
leverage, zero integration risk — and it validates the port of the POC's
core asset before the sensor work begins. Then proceed in plan order;
P2.2–P2.5 are internally ordered by dependency (instance map before
consumers of it).

## Non-Goals For This Slice (and feature)

- No Linux/macOS changes.
- No WintapMessage schema, PidHash, Esper EPL, or downstream Wintappy/DBT
  changes.
- No TraceEvent upgrade, no new NuGet dependencies without Architect
  approval.
- No dual-session architecture; the shared "NT Kernel Logger" session is the
  only kernel session (until P2.7's tightly-scoped boot-session handoff).
- Do not fix unrelated issues encountered in touched files; flag them to the
  Architect instead.

## Testing Expectations

- Every unit: `dotnet build -c Release` green and
  `dotnet test --filter "Category=P2.x"` green; full suite green at P2.6.
- Unit tests cover pure logic (offsets, canonicalization, instance map,
  correlation, dedup); ETW-session/elevation behavior is deliberately left to
  the P2.8 harness — do not build heavy ETW test doubles.
- P2.6 additionally requires a documented manual smoke run (elevated,
  service or console mode): counts of Start/Stop/Refresh observed, QA
  counters logged, no audit-policy dependency.

## Closeout Instructions

- Developer files one audit artifact per unit in
  `../wintap/developer_docs/audits/P2.x-*.md` (existing convention).
- After P2.8, create
  `wiki/work/improve-windows-process-collection/verification.md` with
  commands run and results against the brief's seven acceptance criteria.
- Check off the implementation_plan.md done checklist as units land.
- Append a concise entry to `wiki/log.md` at each slice boundary.
- After behavior stabilizes, promote durable semantics to
  [[wiki/event_type/process-events]] (producer becomes kernel ETW; retire the
  Security-log/log-wrap paragraphs) and record the mechanism change as a
  decision page if the Architect wants it durable.
