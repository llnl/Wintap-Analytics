---
title: "Dev Handoff: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-windows-process-collection/implementation_plan.md
  - ../wintap/CLAUDE.md
policy: agent-editable
last_validated: 2026-08-17
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
`developer_docs/instructions/wpc-<nn>-<slug>.md`, approves it, then dispatches
the **Developer** subagent to implement exactly that unit with xUnit tests
(`[Trait("Category", "wpc-<nn>")]`) and file an audit artifact. This handoff
is the bridge: it tells the Engineer where the approved feature context lives.

Unit IDs use the feature abbreviation **`wpc`** (windows-process-collection):
`wpc-01` … `wpc-08`, matching the implementation plan's eight steps.

## Copy/Paste Prompt

Use this prompt (in the `C:\PUBLIC\wintap` Architect session) to dispatch the
Engineer for the first unit:

    Draft the instruction document for unit wpc-01 (SID extraction helper) of
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
    dotnet build -c Release plus dotnet test --filter "Category=wpc-01".

For subsequent units, repeat with the matching step from
implementation_plan.md (wpc-02 sensor core, wpc-03 snapshot refresh, wpc-04
enrichment, wpc-05 stop-metrics merge, wpc-06 wire-in/removal, wpc-07 boot
ETL, wpc-08 verification harness). Dispatch the Developer only after the
Architect approves each instruction — never hand an unapproved instruction to
the Developer.

## Handoff Summary

Greenfield replacement of Windows process collection, fully specified:
interview complete (all decisions human-confirmed), design settled, plan
sliced into eight wpc units. The SID-extraction technique is already
validated in a standalone POC and ports as-is. No open design questions block
slice 1; the three open questions in design.md (correlation window length,
boot-replay stop events, QA counter home) have stated defaults and are tuned
or decided during verification/closeout.

## Primary Sources For The Dev Agent

Per unit, the Engineer should quote or reference into the instruction:

- `C:\PUBLIC\sid-extraction-test\ProcessTraceDataExtensions.cs` — port source
  for wpc-01 (offset derivation comments included; keep them).
- `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs` —
  `KernelParser.Instance.EtwParser.<Event> += handler` subscription pattern
  (wpc-02); see FileSensor/TcpSensor for live examples.
- `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
  — process-sensor-first bootstrap and kernel-flag aggregation (wpc-02,
  wpc-06, wpc-07 ordering constraint).
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` and
  `KernelProcessSensor.cs` — behavior being replaced; the manifest
  ProcessStop field list in `parseUserModeProcessStop` is the exact metric
  set wpc-05 must retain; both files are deleted in wpc-06.
- `../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs` — Linux
  snapshot-refresh precedent for wpc-03's shape.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` and
  `ProcessResolver.cs` — Send/registration contract and start-time-tolerance
  behavior the sensor relies on; read-only for this feature unless a unit
  says otherwise.
- `../wintap/tests/Wintap.Tests/WintapMessageTests.cs` — existing test style
  and trait convention (P1.1, grandfathered pre-wpc naming).

## Recommended First Implementation Slice

wpc-01 (SID extraction helper). Smallest unit, pure logic, highest test
leverage, zero integration risk — and it validates the port of the POC's
core asset before the sensor work begins. Then proceed in plan order;
wpc-02–wpc-05 are internally ordered by dependency (resolver-backed sensor core
before snapshot/enrichment/metrics).

## Non-Goals For This Slice (and feature)

- No Linux/macOS changes.
- No WintapMessage schema, PidHash, Esper EPL, or downstream Wintappy/DBT
  changes.
- No TraceEvent upgrade, no new NuGet dependencies without Architect
  approval.
- No dual-session architecture; the shared "NT Kernel Logger" session is the
  only kernel session (until wpc-07's tightly-scoped boot-session handoff).
- Do not fix unrelated issues encountered in touched files; flag them to the
  Architect instead.

## Testing Expectations

- Every unit: `dotnet build -c Release` green and
  `dotnet test --filter "Category=wpc-<nn>"` green; full feature suite
  (`dotnet test --filter "Category~wpc"`) green at wpc-06.
- Unit tests cover pure logic (offsets, canonicalization, resolver fallback,
  correlation, dedup); ETW-session/elevation behavior is deliberately left to
  the wpc-08 harness — do not build heavy ETW test doubles.
- wpc-06 additionally requires a documented manual smoke run (elevated,
  service or console mode): counts of Start/Stop/Refresh observed, QA
  counters logged, no audit-policy dependency.

## Closeout Instructions

- Developer files one audit artifact per unit in
  `../wintap/developer_docs/audits/wpc-<nn>-<slug>.md` (existing convention).
- After wpc-08, create
  `wiki/work/improve-windows-process-collection/verification.md` with
  commands run and results against the brief's seven acceptance criteria.
- Check off the implementation_plan.md done checklist as units land.
- Append a concise entry to `wiki/log.md` at each slice boundary.
- After behavior stabilizes, promote durable semantics to
  [[wiki/event_type/process-events]] (producer becomes kernel ETW; retire the
  Security-log/log-wrap paragraphs) and record the mechanism change as a
  decision page if the Architect wants it durable.
