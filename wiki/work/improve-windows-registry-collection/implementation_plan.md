---
title: "Implementation Plan: Improve Windows Registry Collection"
type: concept
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/decision/registry-provider-strategy.md
  - ../wintap/CLAUDE.md
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
  - ../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: llm-agent
status: closed
source_paths: wiki/work/improve-windows-registry-collection/implementation_plan.md
tags: [feature-work, registry, etw, windows-sensor, capture-mode, instruction-units]
---

# Implementation Plan: Improve Windows Registry Collection

> **CLOSED (2026-08-25, close-out dispatch): the Architect accepted the
> feature against the frozen brief criteria on 2026-08-25.** All eight units
> complete (wrc-01/02 retroactive spikes; wrc-03..08 implemented and
> audited, all audits Status: Complete on disk — 134/134 `Category~wrc`,
> 299/299 full suite). Availability anchor: the 2026-08-25 Architect-run
> live verification plus the wrc-08 live smoke test (verdict, verbatim:
> "smoke test looks fantastic") — record in
> [[wiki/work/improve-windows-registry-collection/verification]]. Mini-lab
> closed in [[wiki/work/improve-windows-registry-collection/metrics]]
> (Feature Velocity 42.0, uncertainty 7–84, comparability willingness-only).
> Canonical fold-in: [[wiki/component/registry-sensor]]. Follow-ons live in
> [[wiki/diagnostic/windows-sensor-sweep-queue]] items 13–19.

> **Status (2026-08-25, fifth dispatch): the Architect APPROVED wrc-03
> through wrc-07 (all stamps 2026-08-25)** — Developer handoff on
> the approved units is beginning in parallel. Per-instruction rulings
> recorded on the approval stamps: wrc-03 plain approval; wrc-04
> IntPtr/GCHandle-pinned adaptation confirmed (`AllowUnsafeBlocks` stays
> disabled); wrc-05 append-only ordinals confirmed including the
> unset-object `PreviousDataType` default-ordinal behavior pinned by test,
> with **wrc-06 obligated to set `NONE` explicitly**; wrc-07 canary knobs
> confirmed exactly as proposed (`CaptureCanary` under
> `HKLM\SOFTWARE\Wintap\Collectors\Registry`, 60 s tick / 5 min re-assert,
> dual loss modes, self-noise handling as specified). **wrc-06 is APPROVED as
> written**: Read events use `Data=""` / `DataType=NONE`, the one-line
> `Counter++` is included, and the legacy-parity unset `Registry.PID` behavior
> is retained. It cannot start until the wrc-03/04/05 audits are filed, and
> wrc-07 still executes last.

> **Status addendum (2026-08-25, sixth dispatch): the Architect DECIDED to
> roll in a final unit wrc-08 — parquet value plumbing — before feature
> close**, as a **scoped exception** to the brief's Non-Goals
> (Esper/parquet), citing the shc-03 widening precedent (realize the value
> now rather than defer; wiki/log.md 2026-08-24 entries). **This is NOT a
> criteria amendment**: the frozen brief criteria are unchanged and already
> satisfiable (brief.md stays frozen and untouched;
> `metrics.md` `criteria_amendments` stays empty). wrc-08 carries the
> captured values through to the parquet output users actually query —
> without it, `Reg_DataType`/`Reg_PreviousData`/`Reg_PreviousDataType`
> never exist downstream. **Close-out now waits on wrc-08.** Instruction:
> `../wintap/developer_docs/instructions/wrc-08-parquet-value-plumbing.md`
> (**Status: Approved — Architect approval 2026-08-25**).

**Feature abbreviation: `wrc`** (declared here per the 2026-08-17 unit naming
convention; verified no collision — `developer_docs/instructions/` currently
holds `P1.1`, `wpc-*`, `ptr-*`, and `shc-*` prefixes). Units are `wrc-01`
through `wrc-07`; traits `[Trait("Category", "wrc-NN")]`; run one unit with
`dotnet test --filter "Category=wrc-03"`, the feature with
`dotnet test --filter "Category~wrc"`.

**Working branch:** `develop-wrc` (already created; parallel-feature pattern).

Governing decision: [[wiki/decision/registry-provider-strategy]] (Accepted,
with the session-handle sub-decision OPEN). Frozen acceptance criteria:
[[wiki/work/improve-windows-registry-collection/brief]] (2026-08-25).
Source map: [[wiki/work/improve-windows-registry-collection/references]].

## Retroactive pre-open spike units (already executed — no Developer dispatch)

Per the POC-first/spikes-in-feature model, the discovery work ran **before
feature open** (2026-08-23/24, `C:\PUBLIC\wrc-poc\`, Architect executing all
elevated commands in the main session). These two units exist as audit-trail
records only; they carry **no estimates by definition** and are **excluded
from the per-unit quality loop** (so recorded in `metrics.md`).

### wrc-01 — KCB-correlation spike (NEGATIVE result; retroactive)

Tested whether a classic-kernel KCB rundown can seed a pointer→path map for
manifest-provider events. Result: 0 lookups resolved via the KCB map across
the baseline run and probe3 — classic KCB addresses and manifest `KeyObject`
pointers are disjoint; the hybrid design is dead. Record:
`../wintap/developer_docs/instructions/wrc-01-kcb-correlation-spike.md`.

### wrc-02 — Capture-filter spike (POSITIVE result; retroactive)

The probe1–probe6 series that discovered the 4-byte `0xFFFFFFFF` capture-mode
filter, verified per-REG-type byte-perfect decode of `CapturedData` and
`PreviousData`, and established the sticky-global-state behavior. Record:
`../wintap/developer_docs/instructions/wrc-02-capture-filter-spike.md`.

## Proposed new-sensor units

The sealed AI estimate assumed ~5 units; grounded in the ADR and the current
sensor code, five units is right — but split differently than a naive
one-unit-per-file: decode logic, enablement machinery, and schema are three
independently gated risk surfaces, and the rewrite/wire-in must not be one
mega-unit.

### wrc-03 — Registry payload decode core (pure; no blockers) — APPROVED 2026-08-25

> Instruction: `../wintap/developer_docs/instructions/wrc-03-payload-decode-core.md`
> (2026-08-25). New file `wintap/platform/windows/sensor/etw/helpers/RegistryPayloadDecoder.cs`;
> probe5 byte fixtures reproduced verbatim in the instruction (Developer
> needs no POC access).

New pure helper(s): numeric-event-ID dispatch model (TDH gives no friendly
names for this provider — IDs 1–14 named per the provider manifest, plus the
hive family observed as raw IDs) and a per-REG-type byte decoder covering
REG_SZ(1), REG_EXPAND_SZ(2), REG_BINARY(3), REG_DWORD(4), REG_MULTI_SZ(7),
REG_QWORD(11) plus an unknown-type fallback — the POC's `DecodeRegValue`
semantics, including UTF-16LE strings with terminating NULs inside `DataSize`.
Unit tests use byte fixtures taken verbatim from probe5.log's raw dumps (e.g.
`hello-wrc` = `byte[20]` `68-00-65-00...`). No ETW, no elevation, no schema
dependency. wpc-01 pure-parser pattern.

### wrc-04 — Capture-mode enablement engine (Option A) — APPROVED 2026-08-25 (IntPtr/pinned adaptation confirmed; AllowUnsafeBlocks stays disabled)

> Instruction: `../wintap/developer_docs/instructions/wrc-04-capture-enablement-engine.md`
> (2026-08-25). New file `wintap/platform/windows/sensor/shared/RegistryCaptureEnabler.cs`;
> guarded reflection per Option A; mask injected via constructor (final value
> waits on probe8/wrc-07). Note: Wintap does not enable `AllowUnsafeBlocks`,
> so the instruction specifies the layout-identical `IntPtr`/pinned-buffer
> adaptation of the POC's unsafe structs.

P/Invoke `EnableTraceEx2` + `EVENT_FILTER_DESCRIPTOR` (payload exactly 4
bytes, value `0xFFFFFFFF`, Type value immaterial) + `ENABLE_TRACE_PARAMETERS`
Version 2, using the proven disable-then-enable sequence; periodic re-assert
timer; a capture-loss detection seam (mechanics per Open Question 4; the seam
lands here, the trigger wiring in wrc-07). Session-handle acquisition per the
Architect's choice among the ADR's Options A/B/C — **this unit cannot be
instructed until that decision is made.** Tested through seams (struct
marshaling, sequence ordering, re-assert scheduling); no live ETW in unit
tests.

### wrc-05 — WintapMessage registry schema — APPROVED 2026-08-25 (append-only ordinals confirmed; default-ordinal behavior pinned by test; wrc-06 must set NONE explicitly)

> Instruction: `../wintap/developer_docs/instructions/wrc-05-wintapmessage-registry-schema.md`
> (2026-08-25). Decided shape: `DataTypeEnum` += `QWORD`, `NONE` (appended —
> ordinals 0–4 stable); `RegActivityObject` += `PreviousData` (string,
> decoded identically to `Data`) and `PreviousDataType` (`DataTypeEnum`).
> Additive-only; downstream parquet/EPL see new-but-optional columns; no
> Esper/parquet code changes (brief non-goal).

`shared/WintapAPI/WintapMessage.cs`: extend `RegActivityObject` for pre-change
values and extend `DataTypeEnum` (today `STRING, DWORD, BINARY, MULTI_SZ,
EXPAND_SZ` — no QWORD, no unknown/none) per Open Question 3. Small,
serializer-visible, and deliberately isolated so downstream (Esper EPL,
Parquet, Wintappy) impact is reviewable in one diff.

### wrc-06 — Manifest-only RegistrySensor rewrite + legacy deletion — APPROVED 2026-08-25 (blocked until wrc-03/04/05 audits land)

> Instruction: `../wintap/developer_docs/instructions/wrc-06-manifest-registry-sensor.md`
> (2026-08-25, Status: Approved). Consumes the
> approved interfaces exactly: wrc-03 `RegistryEventKind`/`KindFromEventId`/
> `DecodeRegValue`; wrc-04 `RegistryCaptureEnabler(session, providerId,
> matchAnyKeyword)` + `EnableCapture()` + `DefaultKeywordMask` (interim mask
> until wrc-07); wrc-05 `PreviousData`/`PreviousDataType` with the
> explicit-`NONE` obligation from the wrc-05 approval stamp. Adds the minimal
> `OnEtwSessionStarted(TraceEventSession)` hook to `EtwProviderSensor.cs`
> (the session field is private — the enabler needs the live session).
> Deletion list re-verified 2026-08-25 (repo-wide search: `BaseEvent`/
> `RegistryEvent` users are all within the deleted set; `KernelRegistryEvent`
> unused). Two flagged Engineer calls for the Architect at approval:
> (1) Read events emit `Data=""`/`DataType=NONE` — QueryValueKey's payload
> has no `Type` field (probe schema), so its CapturedData cannot be
> type-decoded, and criterion 3 forbids the legacy live-read/cache fallback;
> (2) a one-line `Counter++` addition — nothing increments
> `BaseWindowsSensor.Counter` today, so the 10 s averager wrc-07's approved
> evidence contract reads always computes 0. Grounding correction recorded:
> the legacy sensor's CreateKey/DeleteKey/DeleteValue emissions (and
> ExpandString/MultiString/QWord writes) actually THREW before
> `EventChannel.Send` (`Enum.TryParse("")`/unparseable-name failure,
> RegistrySensor.cs:273-282, swallowed at the Process_Event catch) — the
> rewrite makes all five activity types genuinely flow; expect a downstream
> volume increase (probe8 scale ≈ 31 events/s total).

> **Probe8 grounding wrc-06 must honor (2026-08-25):** `CreateKey` (event
> id 1) does NOT carry `KeyName` — its path is assembled directly from the
> event as `Join(BaseName, RelativeName)` (BaseName populated under capture,
> e.g. `\REGISTRY\MACHINE`; probe8: 0 unresolved across all 364 CreateKeys —
> no pointer map, ever). **All other emitted event types (SetValueKey,
> DeleteValueKey, DeleteKey) take the path from their own `KeyName` field
> directly** (106/106 populated in probe8). Ignore probe8's spike-1b 46.2%
> KeyObject-map stat — it measured the POC's obsolete map machinery, not
> the design. Additionally, wrc-06's planned "no live registry access"
> assertion must be scoped to **enrichment reads** — wrc-07 adds a
> write-only capture-loss canary (`Microsoft.Win32.Registry` SetValue) that
> must not trip it.

Rewrite `RegistrySensor.Process_Event` on wrc-03/04/05: dispatch on numeric
event ID, take paths from the event's own `KeyName` (`CreateKey`: from
`Join(BaseName, RelativeName)` per the probe8 grounding above), decode
`CapturedData`/`PreviousData`, emit via `EventChannel.Send`. Delete the legacy
machinery: `etw/helpers/RegistryEventParsers.cs` (BaseEvent string-split
parsing and its five event classes), `etw/helpers/RegistryManager.cs`
(`RegParents`/`RegValueCache`), `shared/models/RegistryEvent.cs` (TOCTOU
`GetData()`), `shared/models/KernelRegistryEvent.cs` (no non-registry users —
verified by search 2026-08-25). Preserve the `CollectRegistryRead` setting
gate for read-volume control. Side effect worth recording: the rewrite closes
the sweep-queue item "ungated Registry CreateKey/DeleteKey/DeleteValue emit
sites" by construction (full paths always).

### wrc-07 — Keyword mask, overhead measurement, capture-loss canary, live verification — APPROVED 2026-08-25 (canary knobs confirmed as proposed) — LIVE-VERIFIED 2026-08-25 (Architect-run record in [[wiki/work/improve-windows-registry-collection/verification]])

> Instruction: `../wintap/developer_docs/instructions/wrc-07-mask-canary-live-verification.md`
> (2026-08-25, drafted after probe8 PASS). Mask wiring: sensor selects
> `0x5300` / `0x5700` from the wrc-04 constants via the existing
> `Properties.Settings.Default.CollectRegistryRead` gate
> (`RegistrySensor.cs:62`), applied to both the TraceEvent enable
> (`TraceEventFlags`) and the enabler — probe8's exact verified
> configuration. Canary knobs are **Engineer proposals pending Architect
> approval**: canary value `CaptureCanary` under
> `HKLM\SOFTWARE\Wintap\Collectors\Registry` (the key
> `BaseWindowsSensor` already writes), 60 s write interval, dual loss-mode
> detection (empty-KeyName on the canary's own SetValueKey event, or event
> absent by next tick), recovery via the wrc-04
> `NotifyCaptureLossSuspected` seam, transition-only Error/Info logging,
> self-noise via the existing EventChannel self-PID drop plus a targeted
> sensor-side canary suppression.

Make the session keyword mask explicit Architect-chosen configuration (never
`ulong.MaxValue`; Open Question 2 — RESOLVED FINAL via probe8), measure
event rate/overhead with capture on under the chosen mask, wire the
capture-loss detection trigger (Open Question 4) to the wrc-04 re-assert
path, and support the Architect-run live verification recorded in
`verification.md` (POC self-test pattern: six-type writes + overwrite +
delete, run from a non-Wintap elevated shell so self-PID filtering does not
hide them). This unit produces the feature's availability-anchor candidate.

### wrc-08 — Parquet value plumbing (registry EPL + serializer) — ROLLED IN 2026-08-25 (scoped Non-Goals exception; APPROVED 2026-08-25)

> Instruction: `../wintap/developer_docs/instructions/wrc-08-parquet-value-plumbing.md`
> (2026-08-25, **Status: Approved — Architect approval 2026-08-25**). Decision record:
> Architect 2026-08-25, scoped exception to the brief Non-Goals
> (Esper/parquet) per the shc-03 realize-now precedent; explicitly NOT a
> criteria amendment. Executes after wrc-07; close-out waits on it.

Verified gap (2026-08-25): the wrc-06 sensor sets `Data`/`DataType`/
`PreviousData`/`PreviousDataType` on every emitted Registry message
(`RegistrySensor.cs:189-194`, explicit `NONE`/`""` at 284-287/306-308), but
`core/etl/esper/registry.epl` selects only `registry.data`/`registry.dataType`
(no previous fields), and `RegistrySerializer` writes only `Reg_Data` —
never reading even the `dataType` the EPL already selects. Parquet therefore
lacks `Reg_DataType`, `Reg_PreviousData`, `Reg_PreviousDataType`.

Scope (additive-only, two production files): add
`registry.previousData`/`registry.previousDataType` to the EPL select AND
group-by (the ungrouped-`AgentId` leniency is not imitated; accepted
consequence — batch rows differing only in previous value now aggregate
separately); extract an order-preserving `internal static BuildFlatMessage`
seam in `RegistrySerializer` and add the three `Reg_`-prefixed columns
(sibling convention confirmed) as enum-NAME strings (serializer `.ToString()`
convention — names like `"QWORD"`/`"NONE"`, never ordinals), null-guarded
(`""`/`"NONE"`) for pre-wrc-05 plugin producers. Publish-copy determination:
`publish/esper/registry.epl` is gitignored `dotnet publish` output of the
`Wintap.Common.props:130-133` Content copy (runtime prefers the on-disk copy
per `Serializer.readQueryFromFile`) — a build artifact, NOT independently
maintained, out of scope. Tests (~9, `[Trait("Category", "wrc-08")]`): EPL
embedded-resource text regression, standalone NEsper compile smoke (config
mirrored from `EventChannel.cs:169-178`, documented fallback), and
dictionary-backed mapping tests incl. the 18-column contract and preserved
warts. Post-implementation, the Architect's verification.md addendum is a
single live-data DuckDB query showing the three new columns populated
(PreviousData non-empty on an overwrite row; `NONE` on first writes) —
completing the availability-anchor evidence.

## Execution order

**Recommended Developer execution order (2026-08-25, approved units):
wrc-03 → wrc-05 → wrc-04** — wrc-03 and wrc-05 are order-independent of each
other (no shared files; both risk-free relative to wrc-04's interop novelty).
Then **wrc-06** (hard-gated on the wrc-03/04/05 audits being
filed), then **wrc-07** (its pre-flight check assumes the landed wrc-06
sensor shape), then **wrc-08 last** (rolled in 2026-08-25; needs the wrc-06
sensor emitting the new fields for its live-query addendum, but its code
depends only on wrc-05's schema).

## Files likely to change

- New: `wintap/platform/windows/sensor/etw/helpers/RegistryPayloadDecoder.cs`
  (wrc-03); `wintap/platform/windows/sensor/shared/RegistryCaptureEnabler.cs`
  (wrc-04, Option A — no session-lifecycle P/Invoke needed)
- `shared/WintapAPI/WintapMessage.cs` (wrc-05)
- `wintap/platform/windows/sensor/etw/RegistrySensor.cs` (wrc-06, rewrite)
- Deleted (wrc-06): `etw/helpers/RegistryEventParsers.cs`,
  `etw/helpers/RegistryManager.cs`, `shared/models/RegistryEvent.cs`,
  `shared/models/KernelRegistryEvent.cs`
- `wintap/platform/windows/sensor/shared/EtwProviderSensor.cs` (wrc-06 —
  under the decided Option A, wrc-04 itself changes no existing file; the
  enabler is handed the live `TraceEventSession` at wire-in via a new
  minimal `protected virtual OnEtwSessionStarted(TraceEventSession)` hook,
  called once after `EnableProvider` — the session field is private)
- Mask/canary wiring (wrc-07): `wintap/platform/windows/sensor/etw/RegistrySensor.cs`
  (mask selection off the existing `CollectRegistryRead` setting +
  `TraceEventFlags` + canary wire-in), new
  `wintap/platform/windows/sensor/etw/helpers/RegistryCaptureCanary.cs`, and
  a comment-only pendency update in `RegistryCaptureEnabler.cs` — no new
  Settings entries proposed (knobs are named constants pending Architect
  direction)
- Parquet value plumbing (wrc-08, rolled in 2026-08-25):
  `wintap/core/etl/esper/registry.epl` (select + group-by additions) and
  `wintap/core/etl/extract/RegistrySerializer.cs` (three new `Reg_` columns
  via an order-preserving static mapping seam) — the scoped Non-Goals
  exception covers exactly these two files; `publish/esper/registry.epl` is
  a gitignored build artifact, not maintained
- New tests under `tests/Wintap.Tests/` per unit

## Tests to add

- wrc-03: fixture-driven decode matrices (all six REG types from probe5 raw
  dumps, empty/oversize/truncated payload guards, unknown type fallback,
  event-ID dispatch coverage incl. unknown IDs).
- wrc-04: marshaling-shape tests (descriptor size exactly 4; Version 2;
  FilterDescCount 1), disable-then-enable ordering via seam, re-assert timer
  behavior, fail-loud guard per the chosen handle option.
- wrc-05: WintapMessage construction round-trips for new fields/enum values.
- wrc-06: event→WintapMessage mapping per event ID; create-vs-overwrite
  pre-value semantics; no-live-registry-access assertion by construction
  (no `Microsoft.Win32.Registry` references remain in the sensor path).
- wrc-07: mask selection (CollectRegistryRead false→0x5300 / true→0x5700)
  and keyword-composition constants; canary state machine via seam (both
  loss modes, recovery-failed escalation, transition-only logging, matcher
  purity, fail-open write errors); canary self-noise suppression.
- wrc-08: EPL embedded-resource text regression (new select/group-by
  terms); standalone NEsper compile smoke of the shipped registry.epl
  against the real WintapMessage event type (no runtime/deploy; documented
  fallback); `BuildFlatMessage` mapping matrix (18-column contract,
  enum-name rendering, first-write `NONE` encoding, null guards on new
  columns only, preserved existing-column semantics incl. warts).
- Live ETW verification is manual, Architect-run, recorded in
  `verification.md` (frozen criterion 8); never in unit tests; session names
  never `NT Kernel Logger`; not concurrent with other features' live ETW.

## Open Questions — RESOLVED 2026-08-25 (Architect decisions)

1. **Session-handle acquisition — RESOLVED: Option A, guarded reflection.**
   Rationale (evidence-based, main-session evaluation accepted by the
   Architect): the POC's `EnableProviderWithSystemFlags` is a complete
   working implementation against TraceEvent 3.1.23 — exactly the version
   Wintap pins (`../wintap/wintap/Wintap.csproj` line 22, verified); it
   fails loudly at three distinct guard points (field missing, handle null,
   method missing) so a TraceEvent bump breaks at sensor start, not as
   silent data loss; and it composes directly with
   `EtwProviderCollector.Start()`, which already holds the live
   `TraceEventSession` (`EtwProviderSensor.cs:52-56`), whereas Option B
   would also rework `Stop()`'s attach-by-name. Option C (upstream
   TraceEvent PR) is an OPTIONAL parallel track, not a blocker. Recorded in
   [[wiki/decision/registry-provider-strategy]] §Session-handle acquisition
   (RESOLVED). **wrc-04 unblocked and instructed.**
2. **Keyword mask — RESOLVED FINAL 2026-08-25: `0x5300` default; `0x5700`
   when `CollectRegistryRead` is true — probe8 PASSED (see Pending
   verification below, now closed).** Grounded in the
   non-elevated `logman query providers Microsoft-Windows-Kernel-Registry`
   enumeration (full keyword table recorded verbatim in the ADR's 2026-08-25
   addendum). `0x5300 = SetValueKey|DeleteValueKey|CreateKey|DeleteKey` (the
   four unconditionally-emitted activity types: Write, DeleteValue,
   CreateKey, DeleteKey); `+0x400 QueryValueKey` (→ Read) only under
   `CollectRegistryRead`. OpenKey/CloseKey deliberately EXCLUDED — they fed
   only `RegParents` bookkeeping, which capture-mode `KeyName` obsoletes.
   Volume evidence (probe5, 15 s): mask events ≈ 3,643 of ~240k (~98.5% cut
   vs. the firehose; today's sensor runs unfiltered — `TraceEventFlags`
   default 0). The former pendency (narrowed-`MatchAnyKeyword` × capture
   composition) was closed by probe8's clean PASS (2026-08-25): 106/106
   KeyName, 91/91 CapturedData, six types byte-perfect both directions,
   0 events lost, 470 events/15 s with masked-out types structurally absent
   (~99.8% cut on that run). **wrc-07 instructed on this final value; wrc-04
   still takes the mask as an injected parameter.**
3. **Schema shape — DECIDED: minimal extension.** `DataTypeEnum` gains
   `QWORD` and `NONE` (appended; existing ordinals stable);
   `RegActivityObject` gains `PreviousData` (string, decoded identically to
   `Data`) and `PreviousDataType` (`DataTypeEnum`). No other members change;
   `ActivityTypeEnum` already has every needed value. Downstream
   parquet/EPL see new-but-optional columns — additive, not breaking; no
   Esper/parquet code changes in the unit (brief non-goal). **wrc-05
   unblocked and instructed.**
4. **Capture-loss canary — DEFERRED BY DESIGN (no pre-decision needed).**
   Knobs (interval, canary key path, self-noise suppression) settle at
   wrc-07 instruction drafting after probe8. POC-proven mechanics to build
   on: detection = `KeyName` empty on events that must carry one (run.log
   0/61,042 without capture vs. probes 3/4/5 100% with); trigger =
   self-test write pattern (`DoSelfTestRegistryActivity`); recovery =
   disable-then-enable re-assert (the wrc-04
   `NotifyCaptureLossSuspected` seam).

## Pending verification

- **probe8 — narrowed-mask × capture-filter composition: PASSED
  (Architect-run, elevated, lab host, 2026-08-25 ~11:19 local).** Command
  `WrcPoc.exe 15 FFFFFFFF 1 4 5300`; evidence `C:\PUBLIC\wrc-poc\probe8.log`;
  full record in the ADR addendum (now FINAL). Headlines: KeyName 106/106,
  CapturedData 91/91, six REG types byte-perfect on CapturedData AND
  PreviousData, 0 events lost, 470 events/15 s (~31/s) with masked-out
  types structurally absent. Fallback candidates are moot. **wrc-07
  instructed (Draft) on the strength of this result.**
- **wrc-07 Architect-run live verification: PERFORMED 2026-08-25** (lab
  host, branch build `develop-wrc`) — record and evidence-contract coverage
  table in [[wiki/work/improve-windows-registry-collection/verification]]
  (frozen criteria 6 and 8; items 2–4 of the contract are missing data,
  items 1/6 partial — see the table). Architect acceptance against the
  frozen criteria is still pending; that acceptance happens at close-out.

Settled non-question, recorded to prevent re-litigation: **probe7 (deliberate
clear-behavior test) is not run** — Architect decision 2026-08-25; reboot
persistence and deliberate-clear semantics remain documented unknowns covered
by the re-assert design (ADR §Known unknowns).

## Migration / compatibility notes

- wrc-05 is the only WintapAPI schema change; Esper EPL / Parquet / Wintappy
  impact must be assessed in that unit's instruction once the shape is decided.
- The capture flag is sticky global provider state: deployment/uninstall notes
  must state that Wintap enables host-wide capture for this provider and does
  not attempt to restore prior state (mechanism unknown; ADR §Known unknowns).

## Rollback plan

Disable via the existing `RegistrySensor` settings flag (sensor not started).
Full rollback is reverting the `develop-wrc` branch merge. The capture flag
itself may persist after rollback (sticky state; clear mechanism untested by
decision) — harmless to a non-subscribed host but worth stating in the ADR's
consequences, which it is.

## Done checklist

- [x] wrc-01 retroactive record filed (2026-08-25)
- [x] wrc-02 retroactive record filed (2026-08-25)
- [x] Architect decisions: session handle (Q1 — Option A), schema shape
  (Q3 — minimal extension), both 2026-08-25
- [x] Keyword mask (Q2): decided 0x5300/0x5700; probe8 composition check
  PASSED 2026-08-25 — FINAL
- [x] Canary mechanics (Q4): RESOLVED at wrc-07 approval 2026-08-25 — knobs
  confirmed exactly as proposed (`CaptureCanary` value under
  `HKLM\SOFTWARE\Wintap\Collectors\Registry`, 60 s tick / 5 min re-assert,
  dual loss modes, self-noise handling as specified)
- [x] wrc-03 instructed (2026-08-25), APPROVED 2026-08-25; implemented and
  audited (audit filed, Status: Complete)
- [x] wrc-04 instructed (2026-08-25), APPROVED 2026-08-25 (IntPtr/pinned
  adaptation confirmed); implemented and audited (audit filed, Status:
  Complete)
- [x] wrc-05 instructed (2026-08-25), APPROVED 2026-08-25 (explicit-NONE
  obligation on wrc-06); implemented and audited (audit filed, Status:
  Complete)
- [x] wrc-06 instructed and APPROVED 2026-08-25 (Read events
  `Data=""`/`DataType=NONE`; `Counter++` included; `Registry.PID` wart
  retained); implemented and audited (audit filed, Status: Complete)
- [x] wrc-07 instructed (2026-08-25), APPROVED 2026-08-25 (canary knobs
  confirmed); executed last; implemented and audited (audit filed, Status:
  Complete)
- [x] Architect-run live verification performed 2026-08-25 and recorded in
  [[wiki/work/improve-windows-registry-collection/verification]]
  (evidence-contract coverage table there: items 5 covered, 1/6 partial,
  2/3/4 missing data — recorded, never invented)
- [x] wrc-08 rolled in by Architect decision 2026-08-25 (scoped Non-Goals
  exception, NOT a criteria amendment); instructed and APPROVED 2026-08-25
  (approval conveyed at Developer handoff — formal stamp leapfrogged by the
  handoff, recorded in the instruction header); implemented and audited
  (audit filed, Status: Complete, 9/9 tests); Architect live smoke test
  accepted 2026-08-25 ("smoke test looks fantastic") — the DuckDB query
  output was not pasted into the session, recorded as Architect-verbal with
  query evidence missing data (never-gates) in verification.md
- [x] Architect accepted against the frozen brief criteria 2026-08-25
  (availability anchor finalized: ts_available 2026-08-25)
- [x] Wiki fold-in + mini-lab close-out completed 2026-08-25
  (metrics.md closed; rollup row appended to [[wiki/metrics]]; canonical
  page [[wiki/component/registry-sensor]] created; sweep-queue items 15–19
  cataloged and item 6 marked resolved)
