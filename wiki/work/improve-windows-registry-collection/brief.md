---
title: "Feature Brief: Improve Windows Registry Collection"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
  - ../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: mixed
status: draft
source_paths: wiki/work/improve-windows-registry-collection/brief.md
tags: [feature-work, registry, etw, windows-sensor, capture-mode]
---

# Feature Brief: Improve Windows Registry Collection

## Problem

The Windows `RegistrySensor`
(`../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs` plus
`RegistryEventParsers.cs` / `helpers/RegistryManager.cs` /
`shared/models/RegistryEvent.cs`) is defective in four independent ways:

1. **Fragile parsing.** ETW payloads are parsed via `obj.ToString()` and
   `Split('"')` fixed indices instead of typed payload access.
2. **TOCTOU re-reads.** `RegistryEvent.GetData()` re-reads the live registry
   per event (double OpenKey per value event) — the reported value is whatever
   is in the registry at read time, not what the event carried.
3. **Unbounded caches.** `RegistryManager.RegParents`
   (`Dictionary<ulong,string>`) and `RegValueCache`
   (`Dictionary<string,string>`) grow without bound.
4. **Broken decode.** The `ExpandString` decode path always returns `""`.

A completed pre-feature POC spike (2026-08-23/24, `C:\PUBLIC\wrc-poc\`)
discovered an undocumented capture mode of the
`Microsoft-Windows-Kernel-Registry` manifest provider that makes the kernel
populate `KeyName`, `CapturedData`, and `PreviousData` on registry events —
eliminating the need for path bookkeeping, live re-reads, and value caches
entirely. Evidence and mechanism: [[wiki/decision/registry-provider-strategy]].

## Goals

- Replace `RegistrySensor` with a manifest-only sensor built on the capture
  mode: full absolute key paths from the event's own `KeyName`, value bytes
  from `CapturedData`, pre-change bytes from `PreviousData`.
- Typed payload parsing dispatched by numeric event ID; per-REG-type decode
  (String, ExpandString, DWord, QWord, Binary, MultiSz) verified byte-perfect
  in the POC.
- Robust capture-mode enablement: 4-byte `0xFFFFFFFF` filter at provider
  enable, periodic re-assert, and detection of capture loss.
- Session-level keyword mask sized to downstream needs (not the all-keywords
  firehose), with measured overhead.
- Bounded memory: no unbounded caches of any kind.

## Non-Goals

- No hybrid classic-kernel/manifest design (proved uncorrelatable — see the
  ADR's negative results).
- No changes to other sensors, the Esper layer, or the parquet pipeline
  beyond what registry emission requires.
- No probe7 (deliberate clear-behavior test) — Architect decision 2026-08-25;
  reboot persistence and deliberate-clear semantics remain documented
  unknowns covered by the periodic re-assert design.

## User-Facing Behavior

Registry `WintapMessage` events carry correct full key paths and correct
event-time value data (including ExpandString), plus pre-change values on
overwrites, at materially lower steady-state cost than the current sensor.

## Acceptance Criteria (frozen at feature open, 2026-08-25)

1. The new manifest-only sensor is the sole Windows registry sensor; the
   legacy string-split parsing, live registry re-reads,
   `RegValueCache`/`RegParents`, and all KCB/classic-rundown machinery are
   deleted.
2. The provider is enabled with the 4-byte `0xFFFFFFFF` capture filter and
   the filter is periodically re-asserted; loss of capture (KeyName suddenly
   empty) is detectable and recovers via re-assert without service restart.
3. Emitted registry events carry the full absolute key path taken from the
   event payload; no code path reads the live registry to enrich an event.
4. `SetValueKey` events emit decoded value data for all six REG types,
   including a correct ExpandString decode, and emit the pre-change value on
   overwrite (empty/absent on first write).
5. All payload parsing is typed and dispatched by numeric event ID; no
   `ToString()`/`Split` payload parsing remains.
6. The session keyword mask is an explicit, Architect-chosen configuration
   (not `ulong.MaxValue`), with measured event-rate/overhead evidence
   recorded with capture enabled.
7. Sensor steady-state memory is bounded (no unbounded dictionaries).
8. Each implementation unit ships passing xUnit tests
   (`[Trait("Category", "wrc-NN")]`); live ETW verification is performed
   manually by the Architect and recorded in `verification.md`.

## Affected Areas

- `wintap/platform/windows/sensor/etw/RegistrySensor.cs` (replace)
- `wintap/platform/windows/sensor/etw/RegistryEventParsers.cs`,
  `wintap/platform/windows/sensor/etw/helpers/RegistryManager.cs`,
  `wintap/platform/windows/sensor/shared/models/RegistryEvent.cs` /
  `KernelRegistryEvent.cs` (delete/retire)
- `wintap/platform/windows/sensor/shared/EtwProviderSensor.cs` (session
  creation path — depends on the session-handle decision)
- `shared/WintapAPI/WintapMessage.cs` — **open question**: pre/post value
  emission and QWORD need `RegActivityObject`/`DataTypeEnum` decisions
- `tests/Wintap.Tests/` (new wrc-NN tests)

## References

- [[wiki/decision/registry-provider-strategy]] — capture-mode ADR (mechanism,
  evidence, negative results, session-handle options)
- [[wiki/work/improve-windows-registry-collection/references]] — source map
- `../wintap/developer_docs/instructions/wrc-01-kcb-correlation-spike.md`,
  `wrc-02-capture-filter-spike.md` — retroactive spike records

## Open Questions

Tracked in [[wiki/work/improve-windows-registry-collection/implementation_plan]]
(§Open Questions): session-handle acquisition approach (ADR options, Architect
decides); concrete keyword mask value; `RegActivityObject` schema shape for
pre/post values and QWORD; capture-loss canary mechanics.

## Test Plan

- Pure unit tests for event-ID dispatch and REG-type decode (byte fixtures
  taken from the probe logs' verified dumps) — no ETW, no elevation.
- Enablement/re-assert logic tested through seams (no live ETW in unit tests).
- Live verification: Architect-run elevated session on the lab host with
  self-test writes (POC pattern), recorded in `verification.md`.
- Constraint: no live ETW tests concurrent with other features' live ETW
  tests; session names never `NT Kernel Logger`.

## Done When

All eight frozen criteria demonstrably hold, the legacy machinery is gone,
tests pass per unit and feature-wide (`Category~wrc`), and the
Architect-accepted live verification is recorded.
