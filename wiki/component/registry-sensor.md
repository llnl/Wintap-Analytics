---
title: "Registry Sensor (Manifest-Only, Capture-Mode Windows Registry Collection)"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryPayloadDecoder.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryCaptureCanary.cs
  - ../wintap/wintap/platform/windows/sensor/shared/RegistryCaptureEnabler.cs
  - ../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/etl/esper/registry.epl
  - ../wintap/wintap/core/etl/extract/RegistrySerializer.cs
  - ../Wintap-Analytics/wiki/decision/registry-provider-strategy.md
  - ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/verification.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: mixed
status: reviewed
source_paths: wintap/platform/windows/sensor; shared/WintapAPI; wintap/core/etl
tags: [wintap, windows-sensor, component, registry, etw, capture-mode, canary, parquet, esper]
---

# Registry Sensor

Manifest-only Windows registry collection built on the
`Microsoft-Windows-Kernel-Registry` provider's **undocumented capture mode**,
delivered by the `improve-windows-registry-collection` feature (opened and
closed 2026-08-25; retroactive spike units wrc-01/wrc-02, build units
wrc-03..wrc-08). It replaced the legacy sensor's XML-string parsing, TOCTOU
live-registry re-reads, and unbounded `RegParents`/`RegValueCache` caches —
all four legacy helper/model files were deleted. Governing decision:
[[wiki/decision/registry-provider-strategy]].

## Capture-mode enablement (wrc-04, Option A)

`RegistryCaptureEnabler` re-enables the provider via `EnableTraceEx2` with a
4-byte `0xFFFFFFFF` `EVENT_FILTER_DESCRIPTOR` payload
(`ENABLE_TRACE_PARAMETERS` Version 2, proven disable-then-enable sequence) —
the POC-discovered mechanism that makes the kernel populate `KeyName`,
`CapturedData`, and `PreviousData` on registry events, closing a gap
publicly documented as an unfixable limitation. Marshaling uses
layout-identical `IntPtr`/GCHandle-pinned buffers (Wintap does not enable
`AllowUnsafeBlocks`). The session handle comes from **guarded reflection**
into TraceEvent's private `m_SessionHandle` (Architect-decided Option A),
pinned to the **TraceEvent 3.1.23** version Wintap ships; three distinct
fail-loud guard points make a TraceEvent bump break at sensor start, never
as silent data loss. The live `TraceEventSession` is handed over via the
minimal `OnEtwSessionStarted(TraceEventSession)` hook added to
`EtwProviderSensor` (wrc-06).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/shared/RegistryCaptureEnabler.cs; ../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs §OnEtwSessionStarted -->

The capture flag is **sticky global provider state**: Wintap enables
host-wide capture and does not restore prior state; reboot persistence and
deliberate-clear semantics are documented unknowns (probe7 never run, by
Architect decision) covered operationally by the re-assert below — see
[[wiki/diagnostic/windows-sensor-sweep-queue]] item 17.

## Keyword mask (wrc-07, FINAL)

Session `MatchAnyKeyword` is **`0x5300`** by default
(SetValueKey | DeleteValueKey | CreateKey | DeleteKey) and **`0x5700`**
(+ QueryValueKey → Read) when the existing
`Properties.Settings.Default.CollectRegistryRead` setting is true, applied
to both the TraceEvent enable (`TraceEventFlags`) and the enabler —
probe8's exact verified configuration. OpenKey/CloseKey are deliberately
excluded (they fed only the deleted `RegParents` bookkeeping). Volume
evidence: ~99.8% cut vs. the all-keywords firehose (probe8 ≈ 31 events/s
masked vs. probe5 ≈ 16k/s; live run 2026-08-25: 500–1,100 events per 30 s
batch typical, bursts to ~6k, zero drops).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs §SelectKeywordMask; ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/verification.md -->

## Capture-loss canary and re-assert (wrc-07)

`RegistryCaptureCanary` writes the `CaptureCanary` value under
`HKLM\SOFTWARE\Wintap\Collectors\Registry` (the key `BaseWindowsSensor`
already owns) every 60 s and watches its own SetValueKey event for **dual
loss modes**: event observed with empty `KeyName` (immediate capture loss)
or event absent by the next tick (silent loss). Recovery goes through the
enabler's `NotifyCaptureLossSuspected` seam (disable-then-enable
re-assert); logging is transition-only (once-only recovery-failed Error,
RECOVERED Info). Independently, a **5-minute periodic re-assert** covers
clobber-to-zero, reboot, and unknown reset paths. The canary is
**write-only** — the sensor performs no live-registry enrichment reads
(frozen criterion); canary self-noise is suppressed sensor-side plus the
existing EventChannel self-PID drop.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryCaptureCanary.cs -->

## Event decode and emission (wrc-03, wrc-06)

Dispatch is by **numeric event ID** (`KindFromEventId` — the provider's
manifest gives no friendly names). Paths come from the event itself, never
from pointer maps or live reads: **CreateKey (id 1) carries no `KeyName`** —
its path is `Join(BaseName, RelativeName)` (BaseName populated under
capture; probe8: 0 unresolved across 364 CreateKeys); SetValueKey /
DeleteValueKey / DeleteKey use their own `KeyName` directly. A
qualification gate mirroring `IsQualifiedRegistry` drops unrooted fragments
rather than emitting them (this closed sweep-queue item 6 by construction).

`RegistryPayloadDecoder.DecodeRegValue` decodes `CapturedData` and
`PreviousData` per REG type — REG_SZ, REG_EXPAND_SZ, REG_BINARY, REG_DWORD,
REG_MULTI_SZ, REG_QWORD plus an unknown-type fallback; UTF-16LE strings
honor terminating NULs inside `DataSize`. Write events emit **pre- and
post-change values**; first writes carry `PreviousDataType = NONE` (kernel
REG_NONE, size 0). **Read events emit `Data=""` / `DataType=NONE` by
design** — QueryValueKey's payload has no `Type` field (documented
limitation, sweep-queue item 16). Known wart: `Registry.PID` is left unset
(legacy parity; the envelope `PID` is authoritative — sweep item 18).
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryPayloadDecoder.cs; ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs §Process_Event -->

## Schema (wrc-05)

`WintapMessage.RegActivityObject` gained `PreviousData` (string, decoded
identically to `Data`) and `PreviousDataType`; `DataTypeEnum` gained
`QWORD` and `NONE`, **appended** so ordinals 0–4 stay stable. Additive-only;
plugin-authored Registry messages predating the change remain valid.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §RegActivityObject/§DataTypeEnum -->

## Parquet output (wrc-08)

`registry.epl` selects (and groups by) `data`, `dataType`, `previousData`,
and `previousDataType` over 10 s batches; rows differing only in previous
value aggregate separately (Architect-confirmed granularity).
`RegistrySerializer.BuildFlatMessage` (order-preserving static seam) writes
an 18-column row to `raw_sensor/registryserializer` — the 15 legacy columns
bit-identical (warts preserved: `HostHame` typo, `FirstSeenMs`/`LastSeenMs`,
`EventTime` from `FromFileTimeUtc(firstSeen)` — sweep item 19) plus the
three wrc-08 additions **`Reg_DataType`, `Reg_PreviousData`,
`Reg_PreviousDataType`**, rendered as enum-name strings
(`"STRING" | "DWORD" | "BINARY" | "MULTI_SZ" | "EXPAND_SZ" | "QWORD" |
"NONE"`, never ordinals) and null-guarded (`""`/`"NONE"`). Note
`publish/esper/registry.epl` is gitignored `dotnet publish` output — never
hand-edited; deployments pick up EPL changes via rebuild/republish.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/registry.epl; ../wintap/wintap/core/etl/extract/RegistrySerializer.cs §BuildFlatMessage -->

## Verification state (2026-08-25)

Shipped as commit `1f66a47` on `develop-wrc` ("Add wrc: manifest-only
registry sensor via undocumented capture-mode filter (wrc-01..08)",
32 files). 134/134 `Category~wrc` tests (52 decode, 11 enabler, 14 schema,
34 sensor, 14 mask/canary, 9 parquet plumbing); full suite 299/299.
Availability
demonstrated by the Architect-run live verification of 2026-08-25 plus the
wrc-08 live smoke test (verbatim record and honest evidence-coverage table
in [[wiki/work/improve-windows-registry-collection/verification]]).
Instruction and audit artifacts (local-only, gitignored):
`../wintap/developer_docs/instructions/wrc-01..08-*.md` and
`../wintap/developer_docs/audits/wrc-03..08-*.md` (all Complete).

## Related

- [[wiki/decision/registry-provider-strategy]] — the governing ADR and capture-mode mechanism record
- [[wiki/work/improve-windows-registry-collection/brief]] — frozen acceptance criteria
- [[wiki/work/improve-windows-registry-collection/implementation_plan]] — unit map wrc-01..08
- [[wiki/work/improve-windows-registry-collection/verification]] — live-run evidence and availability anchor
- [[wiki/diagnostic/windows-sensor-sweep-queue]] — items 13–19 (follow-ons and documented limitations)
- [[wiki/component/windows-sensor-service-internals]] — service lifecycle and EventChannel routing
