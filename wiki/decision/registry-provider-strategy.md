---
title: "Decision: Manifest-provider registry collection via the undocumented capture-mode filter"
type: decision
status: accepted
decided_on: 2026-08-25
confidence: high
grounded_by:
  - C:\PUBLIC\wrc-poc\run.log
  - C:\PUBLIC\wrc-poc\probe1.log
  - C:\PUBLIC\wrc-poc\probe2.log
  - C:\PUBLIC\wrc-poc\probe3.log
  - C:\PUBLIC\wrc-poc\probe4.log
  - C:\PUBLIC\wrc-poc\probe5.log
  - C:\PUBLIC\wrc-poc\probe6.log
  - C:\PUBLIC\wrc-poc\probe8.log
  - C:\PUBLIC\wrc-poc\Program.cs
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
  - ../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs
  - ../wintap/wintap/Wintap.csproj
policy: human-review-required
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: mixed
source_paths: wiki/work/improve-windows-registry-collection
tags: [decision, registry, etw, windows-sensor, capture-mode, event-filter-descriptor, enabletraceex2, kcb, traceevent]
---

# Decision: Manifest-provider registry collection via the undocumented capture-mode filter

Date: 2026-08-25. Status: Accepted. The session-handle sub-decision, OPEN at
first acceptance, was resolved later the same day (2026-08-25): **Option A —
guarded reflection** (see the Session-handle acquisition section). The
keyword-mask value was decided 2026-08-25 and is now **FINAL** (same day,
probe8 clean PASS): **0x5300 default / 0x5700 with CollectRegistryRead** —
see the dated addendum. Feature: improve-windows-registry-collection (wrc).

STANDALONE-RECORD NOTE. As far as this project could determine, no public
documentation of this ETW mechanism exists anywhere; this may be its first
written documentation. This ADR is written to stand alone: everything needed
to reproduce the capture mode is on this page. Primary evidence:
C:\PUBLIC\wrc-poc\run.log, probe1.log through probe6.log, probe8.log, and
C:\PUBLIC\wrc-poc\Program.cs (POC harness; TraceEvent 3.1.23; Windows 11 Pro
22631).

## Context

Wintap's Windows `RegistrySensor` subscribes to the manifest provider
`Microsoft-Windows-Kernel-Registry` (`70EB4F03-C1DE-4F73-A051-33D13D5413BD`)
via `RegisteredTraceEventParser`
(`../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs:58`).
Under a normal provider enable, the provider's registry events *declare*
`KeyName` and value-data fields (`CapturedData`, and on `SetValueKey` also
`PreviousDataType`/`PreviousDataSize`/`PreviousData`), but the kernel leaves
them **empty**: in the baseline run (`run.log`), KeyName was populated on 0
of 49,679 value-op events, and 0 of 58 `SetValueKey` events carried
`CapturedData` — with the `DataSize` field *correct* and the payload
zero-length, i.e. the kernel knows the size but does not copy the bytes.

That gap is publicly described as a known Microsoft limitation not
prioritized for a fix (Nextron Systems' Aurora documentation on empty
CapturedData/KeyName). TraceEvent's own registry key-name tracking is
disabled for real-time sources and marked suspect by its authors (perfview
`KernelTraceEventParser.cs:2989`, `:5447`; classic KCB rundown arrives only
at session stop — perfview issue #928).

The current sensor works around the empty fields with pointer bookkeeping
(`RegParents`), a live registry re-read per value event (TOCTOU, double
OpenKey — `RegistryEvent.GetData()`), an unbounded value cache
(`RegValueCache`), and `ToString()`/`Split('"')` fixed-index payload
parsing; its ExpandString decode always returns `""`. These defects motivate
the feature.

A pre-feature POC spike (2026-08-23/24, retroactive units wrc-01/wrc-02, run
in the main session with the Architect executing all elevated commands)
tested two ideas: (a) whether a classic-kernel KCB rundown can seed a
pointer-to-path map for manifest-provider events, and (b) a cryptic lead
from a years-old conference note by a C++-developer colleague of the
Architect — "EVENT_FILTER_DESCRIPTOR (do not set SCHEMATIZED!) / System
Flags set to 1 / Ulong/long. Last byte all 1s". Idea (a) failed decisively;
idea (b), after two null probes, succeeded and is the basis of this
decision. The note was wrong in two details (filter Type constant does not
matter; the payload must be a 4-byte ULONG, not "Ulong/long") but right in
the essentials, and served as the existence proof justifying continued
probing despite discouraging public information (an SDK header comment
claims filter Type is ignored unless the provider opts in via
`EventSetInformation` — evidently wrong for this provider).

## Decision

1. **Manifest-only registry sensor.** Drop entirely: XML-string payload
   parsing, live registry re-reads, `RegValueCache`/`RegParents`, and all
   KCB/classic-rundown machinery. Grounds: the capture mode makes them
   unnecessary, and the KCB-correlation negative result makes the hybrid
   design impossible anyway.
2. **Enable the provider in the capture mode** (mechanism below) so the
   kernel itself supplies full key paths, value bytes, and pre-change bytes.
3. **Periodic re-assert** of the capture filter — cheap, and it covers
   clobber-to-zero by other consumers, reboot, and unknown reset paths. A
   capture-loss detection heuristic is under consideration (canary write to
   a Wintap-owned key: KeyName suddenly empty implies immediate re-assert).
4. **Session-level keyword mask chosen per downstream needs** — not the
   all-keywords firehose (~16-17k events/s observed on a quiet dev box) —
   with overhead measured with capture on. The concrete mask value was NOT
   settled in the probe logs (all probes ran `MatchAnyKeyword =
   ulong.MaxValue`); **decided 2026-08-25 and confirmed FINAL the same day
   by probe8** (live composition check, clean PASS): `0x5300` default,
   `0x5700` when `CollectRegistryRead` is true. See the addendum below.
5. **Typed payload parsing dispatched by numeric event ID** (TDH supplies no
   friendly names for this provider — events arrive as `EventID(n)`); decode
   `CapturedData`/`PreviousData` per REG type; emit pre/post values from
   `SetValueKey`.
6. **Session-handle acquisition for `EnableTraceEx2`: RESOLVED 2026-08-25 —
   Option A, guarded reflection** (Architect decision; rationale and the
   options record below).

## The capture mode - mechanism record

### Exact descriptor and call

Enable the provider on the session with `EnableTraceEx2` carrying one
`EVENT_FILTER_DESCRIPTOR` whose payload is a 4-byte ULONG with value
`0xFFFFFFFF`:

```c
ULONG captureFlags = 0xFFFFFFFF;      // payload: exactly 4 bytes, little-endian

EVENT_FILTER_DESCRIPTOR filter;
filter.Ptr  = (ULONGLONG)&captureFlags;
filter.Size = 4;                      // MUST be exactly 4; 8 bytes = silent no-op
filter.Type = 0x1;                    // value irrelevant: 0x1 and 0x80000001 both work

ENABLE_TRACE_PARAMETERS params = {0};
params.Version          = 2;          // ENABLE_TRACE_PARAMETERS_VERSION_2 (FilterDescCount honored)
params.EnableFilterDesc = &filter;
params.FilterDescCount  = 1;

EnableTraceEx2(sessionHandle,
               &KernelRegistryGuid,   // 70EB4F03-C1DE-4F73-A051-33D13D5413BD
               EVENT_CONTROL_CODE_ENABLE_PROVIDER,
               TRACE_LEVEL_VERBOSE,
               matchAnyKeyword, 0, 10000, &params);
```

POC procedure detail: the provider was disabled first
(`EVENT_CONTROL_CODE_DISABLE_PROVIDER` on the same handle), then re-enabled
with the filter attached, on the theory that the kernel may sample capture
flags only on the disabled-to-enabled transition. All successful probes used
this disable-then-enable sequence; enabling with the filter without a prior
disable was not isolated as a variable. The C# marshaling used by the POC
(struct layouts, unsafe pointer to a stack ULONG, DllImport signature) is in
`C:\PUBLIC\wrc-poc\Program.cs`, `EnableProviderWithSystemFlags(...)`.

### Parameter sensitivity (probe matrix)

| Probe | filter Type | payload value | payload size | KeyName populated | SetValueKey CapturedData | Verdict |
|---|---|---|---|---|---|---|
| baseline (run.log) | none | — | — | 0 / 49,679 | 0 / 58 | kernel not capturing (DataSize correct, payload empty) |
| probe1 | 0x1 | 0xFFFFFFFFFFFFFFFF | 8 | 0 / 24,172 | 0 | silent no-op (success return, zero effect) |
| probe2 | 0x80000001 | 0xFFFFFFFFFFFFFFFF | 8 | 0 / 20,742 | 0 | silent no-op |
| probe3 | 0x1 | 0xFFFFFFFF | **4** | 72,601 / 72,604 | 73 / 73 | **WORKS** |
| probe4 | 0x80000001 | 0xFFFFFFFF | **4** | 16,807 / 16,807 | 79 / 79 | **WORKS** (Type irrelevant) |
| probe5 | 0x1 | 0xFFFFFFFF | 4 | 94,068 / 94,068 | 170 / 170 | PreviousData verified: all 6 REG types byte-perfect on overwrite |
| probe6 | 0x1 | 8-byte no-op payload | 8 | 35,762 / 35,762 | 66 / 66 | capture state STICKY across disable + filterless re-enable |

Sensitivity summary: the payload **size must be exactly 4** (an 8-byte
payload is silently ignored with a success return); the descriptor **Type
field is irrelevant** (0x1 and 0x80000001 behave identically); the
"SYSTEM_FLAGS"-style naming in the original field note is therefore
incidental — what matters is a 4-byte all-ones payload on the filter
descriptor at enable time.

### What the kernel populates when capture is on

1. **`KeyName`** carries the full absolute `\REGISTRY\...` path on every
   event that declares the field — 94,068 / 94,068 value-op events in probe5
   (probe3: 72,601 / 72,604). No KCB correlation, pointer maps, or registry
   re-reads are needed for paths, ever. Example observed value:
   `\REGISTRY\MACHINE\SYSTEM\ControlSet001\Control\TimeZoneInformation`.
2. **`CapturedData`** carries the actual value bytes on `SetValueKey` (and
   rides `QueryValueKey`, `EnumerateKey`, `EnumerateValueKey`, `QueryKey`,
   `SetInformationKey` too). Verified byte-perfect against self-test writes
   for REG_SZ (1), REG_EXPAND_SZ (2), REG_BINARY (3), REG_DWORD (4),
   REG_MULTI_SZ (7), REG_QWORD (11) — probe3 and probe5 self-test
   verification sections, all `OK`. Strings arrive as UTF-16LE with
   terminating NULs included in `DataSize` (see probe3 raw dumps, e.g.
   `hello-wrc` = `byte[20]`).
3. **`PreviousDataType`/`PreviousDataSize`/`PreviousData`** on `SetValueKey`
   overwrites carry the pre-change value, byte-perfect for all six REG types
   (probe5 PreviousData verification, all `OK`; re-verified under the
   narrowed mask in probe8, all `OK` on both CapturedData and PreviousData);
   empty with type/size 0 on the first write of a new value — correct
   create-vs-overwrite semantics. Probe8's raw dumps pin the exact
   first-write encoding: `PreviousDataType = 0` (kernel **REG_NONE**),
   `PreviousDataSize = 0`, `PreviousData = byte[0]` — so kernel REG_NONE (0)
   maps one-to-one onto the wrc-05 `DataTypeEnum.NONE` member as the
   "no previous value" encoding.
4. Payload sizes grow accordingly: baseline self-test `SetValueKey`
   `EventDataLength` was 58-60 bytes; with capture on, the same writes
   produced 210-272 bytes (probe3/probe5 raw dumps). CapturedData riding
   high-volume query/enumerate events is why overhead must be re-measured
   when the keyword mask is chosen.
5. **`CreateKey` (event id 1) does NOT declare `KeyName`** — its schema is
   `BaseObject, KeyObject, Status, Disposition, BaseName, RelativeName`
   (probe8 payload-schema table). Under capture mode `BaseName` arrives
   populated (observed `\REGISTRY\MACHINE`, `\REGISTRY\USER`), so the full
   path is assembled **directly from the event as
   `Join(BaseName, RelativeName)`** — no pointer lookup, ever: probe8
   recorded **0 unresolved** paths across all 364 CreateKeys (path anatomy:
   6 absolute `RelativeName`s, 348 truly-relative with populated `BaseName`;
   every spike-1 lookup counter zero — no event needed a `BaseObject` map).
   All other emitted event types (`SetValueKey`, `DeleteValueKey`,
   `DeleteKey`) carry their own fully-populated `KeyName` (106/106 in
   probe8). Caution for readers of probe8.log: its spike-1b KeyObject-map
   resolution stat (46.2% on value-ops) measured the POC's obsolete map
   machinery against `KeyObject` pointers — it is **irrelevant to the
   design**; value-op events use their own `KeyName` field (100% populated)
   and no maps are needed anywhere.

### Capture state is sticky global provider state

Probe6 enabled the provider with the known-no-op 8-byte descriptor after an
explicit `EVENT_CONTROL_CODE_DISABLE_PROVIDER` — and capture remained fully
active (KeyName 35,762 / 35,762; CapturedData 66 / 66). Therefore the
capture flag lives in kernel-side provider state, not per-session enable
state: a normal consumer enabling or disabling the provider does NOT clear
it. Design consequence: Wintap cannot assume it owns the flag's lifetime in
either direction — another tool may have set it (Wintap sees capture without
asking) or may clear it by a mechanism we have not observed. Hence decision 3:
periodic re-assert plus capture-loss detection, never a one-shot enable.

<!-- REPAIR NOTE 2026-08-25: this page was truncated by a prior partial
Engineer run (the sticky-state paragraph ended mid-sentence and the four
sections below were "(to be filled)" placeholders). Repaired minimally by the
resumed run from the same evidence base (probe logs, Program.cs,
CONTINUATION.md, interview playback). No prior content above this line was
altered except completing the cut-off sentence. -->

## Known unknowns

1. **Reboot persistence** of the sticky capture flag — not tested. Probe7
   (a valid 4-byte descriptor with value 0, which would also answer
   deliberate clear semantics) was **deliberately not run** — Architect
   decision 2026-08-25, recorded in the feature interview playback and the
   brief's Non-Goals. The periodic re-assert design covers both outcomes.
2. **Deliberate clear-to-zero semantics** — same unrun probe7. Assumed
   possible; re-assert plus capture-loss detection is designed as if it is.
3. **Enable-with-filter without a prior disable** — all successful probes
   used the disable-then-enable sequence; enabling with the filter directly
   was never isolated as a variable. The production engine should keep the
   proven sequence.
4. **Cross-version stability** — observed only on Windows 11 Pro 22631 with
   TraceEvent 3.1.23. The mechanism is undocumented, so no compatibility
   contract exists in either direction (older builds, future updates).
   Capture-loss detection is the mitigation, not an OS-version matrix.
5. **The provider's keyword assignments** — RESOLVED 2026-08-25: enumerated
   via a non-elevated `logman query providers
   Microsoft-Windows-Kernel-Registry` (table in the addendum below). The
   last sub-unknown — **composition** of a narrowed `MatchAnyKeyword` with
   the capture filter — was RESOLVED later the same day by probe8 (clean
   PASS; see the addendum): the mask composes perfectly with capture, and
   masked-out event types are structurally absent.
6. **Overhead under a narrowed mask with capture on** — baseline volume
   (~16-17k events/s all-keywords) was measured, but per-mask cost with the
   larger captured payloads was not. Probe8 supplies the first
   masked-with-capture data point (470 events / 15 s ≈ 31/s on a quiet lab
   host vs. the ~16k/s firehose); production steady-state measurement
   remains in the plan's final unit (wrc-07, frozen criterion 6).

## Session-handle acquisition for EnableTraceEx2 - RESOLVED (2026-08-25: Option A)

**Decision (Architect, 2026-08-25): Option A — guarded reflection.**
Rationale, evidence-based (main-session evaluation accepted by the
Architect):

1. The POC's `EnableProviderWithSystemFlags`
   (`C:\PUBLIC\wrc-poc\Program.cs` — lines 179–221 in the probe8-patched
   file; 172–214 at decision time, pre-patch) is a complete working
   implementation against TraceEvent **3.1.23** — exactly the version Wintap
   pins (`../wintap/wintap/Wintap.csproj` line 22, verified 2026-08-25).
2. It fails loudly at three distinct guard points (field missing, handle
   null, method missing), so a future TraceEvent bump breaks at sensor
   start, not as silent data loss.
3. It composes directly with `EtwProviderCollector.Start()`, which already
   holds the live `TraceEventSession`
   (`../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs:52-56`),
   whereas Option B would also have to rework `Stop()`'s attach-by-name.

**Option C (upstream a TraceEvent change exposing the session handle or
filter support) is recorded as an OPTIONAL parallel track, not a blocker.**
Implemented by unit wrc-04
(`../wintap/developer_docs/instructions/wrc-04-capture-enablement-engine.md`).

The options as framed for the decision (kept for the record):

`EnableTraceEx2` needs the session's raw `TRACEHANDLE`. Wintap's
`EtwProviderCollector` creates its sessions through TraceEvent's
`TraceEventSession`
(`../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs:51`),
which does not expose the handle. The POC reflected into TraceEvent's private
`m_SessionHandle` field — whose runtime type is TraceEvent's **internal
`SafeTraceHandle`, not a `System.Runtime.InteropServices.SafeHandle`** (a
direct cast throws); the POC held it as `object` and reflected its public
`DangerousGetHandle()` (`C:\PUBLIC\wrc-poc\Program.cs`,
`EnableProviderWithSystemFlags`). That works on the pinned TraceEvent 3.1.23
but is version-fragile private-API use. Options as presented (decision
above):

- **Option A — keep the reflection, guarded.** Reflect `m_SessionHandle` +
  `DangerousGetHandle()` exactly as the POC does, but fail loud at sensor
  startup if any reflection step misses (log CRITICAL, sensor refuses to
  start in capture mode). Pros: smallest change; session lifecycle stays
  entirely inside the existing `EtwProviderCollector`; proven working today.
  Cons: private-API dependency that any future TraceEvent bump can silently
  break (mitigated only by the fail-loud guard and the repo's pinned 3.1.23).
- **Option B — own the session natively for this sensor.** Create the
  registry session via P/Invoke (`StartTraceW` + `EVENT_TRACE_PROPERTIES`),
  keep the returned `TRACEHANDLE`, call `EnableTraceEx2` directly, and use
  TraceEvent only for decoding by attaching
  `ETWTraceEventSource(sessionName, TraceEventSourceType.Session)` (public
  API, same as today). Pros: no private-API dependency; the handle is
  legitimately owned; TraceEvent reduced to its supported decode role. Cons:
  Wintap takes over session lifecycle work `TraceEventSession` currently
  provides (properties-struct marshaling, stop/cleanup, orphaned-session
  recovery on restart) — more new P/Invoke surface than Option A.
- **Option C — upstream a TraceEvent change** (expose a raw-handle accessor
  or a filtered-enable overload in perfview/TraceEvent). Pros: cleanest
  long-term answer; benefits everyone. Cons: external timeline; does not
  unblock the feature now; consuming it later means a TraceEvent upgrade the
  project has so far deliberately avoided. Compatible as a follow-up to
  either A or B.

Under the chosen Option A, the proven disable-then-enable sequence, the
4-byte descriptor, and the periodic re-assert are unchanged; the fail-loud
guards must name the TraceEvent version pin so a dependency bump surfaces
immediately. The former block on wrc-04 is lifted.

## Addendum 2026-08-25 — session keyword mask (FINAL; probe8 PASS)

**Decision (Architect, 2026-08-25): `MatchAnyKeyword = 0x5300` by default;
`0x5700` when the existing `CollectRegistryRead` setting is true. FINAL —
confirmed the same day by the Architect-run probe8 (clean PASS; record
below).**

Grounding: the provider's keywords were enumerated 2026-08-25 via a
non-elevated `logman query providers Microsoft-Windows-Kernel-Registry`
(main-session run). Keyword table (verbatim):

| Keyword | Value |
|---|---|
| CloseKey | 0x1 |
| QuerySecurityKey | 0x2 |
| SetSecurityKey | 0x4 |
| EnumerateValueKey | 0x10 |
| QueryMultipleValueKey | 0x20 |
| SetInformationKey | 0x40 |
| FlushKey | 0x80 |
| SetValueKey | 0x100 |
| DeleteValueKey | 0x200 |
| QueryValueKey | 0x400 |
| EnumerateKey | 0x800 |
| CreateKey | 0x1000 |
| OpenKey | 0x2000 |
| DeleteKey | 0x4000 |
| QueryKey | 0x8000 |
| Analytic-channel | 0x8000000000000000 |
| Performance-channel | 0x4000000000000000 |

Mask composition: `0x5300 = SetValueKey (0x100) | DeleteValueKey (0x200) |
CreateKey (0x1000) | DeleteKey (0x4000)` — the four unconditionally-emitted
activity types (Write, DeleteValue, CreateKey, DeleteKey); `+ 0x400
QueryValueKey` (→ Read) only when `CollectRegistryRead`. **OpenKey/CloseKey
are deliberately EXCLUDED** — the legacy sensor consumed them only for
`RegParents` path bookkeeping, which capture-mode `KeyName` obsoletes.

Volume evidence (probe5, 15 s window): mask events ≈ 3,643 of ~240k total —
a ~98.5% cut versus the firehose. Today's sensor never sets
`TraceEventFlags`, i.e. runs unfiltered.

**Status: FINAL (2026-08-25).** The one open interaction — whether a
narrowed `MatchAnyKeyword` composes with the capture filter (every probe
through probe6 ran `ulong.MaxValue`) — was closed by **probe8**
(Architect-run, elevated, lab host, 2026-08-25 ~11:19 local; POC patched
with a 5th CLI argument `[maskHex]` applied to **both** enable calls;
command `WrcPoc.exe 15 FFFFFFFF 1 4 5300`; evidence
`C:\PUBLIC\wrc-poc\probe8.log`). Result: **clean PASS.**

- **Capture fully active under the mask:** `KeyName` populated on 106/106
  value-op events (zero empty); `CapturedData` on 91/91 `SetValueKey`; all
  six REG types byte-perfect on BOTH `CapturedData` (second write) and
  `PreviousData` (first write); session events lost: 0.
- **Masked-out events genuinely absent:** event volume CreateKey 364 +
  SetValueKey 91 + DeleteValueKey 9 + DeleteKey 6 = **470 events / 15 s
  (~31/s)**; no OpenKey/CloseKey/Query*/Enumerate* events arrived at all.
  Versus probe5's ~240k / 15 s firehose that is a **~99.8% volume cut** on
  this run (a quieter window than probe5's CreateKey count, but the
  exclusion is structural — the masked keywords do not fire — not luck).
- Two further mechanism findings folded into the mechanism record above
  (items 3 and 5): the exact REG_NONE first-write encoding grounding
  wrc-05's `DataTypeEnum.NONE`, and CreateKey path assembly via
  `Join(BaseName, RelativeName)` (id 1 carries no `KeyName`) with zero
  unresolved paths — grounding the wrc-06 dispatch design.

The fallback candidates held in reserve at decision time (mask at the
TraceEvent enable only; firehose + user-space drop) are moot. wrc-07 is
unblocked and instructed (2026-08-25, Draft); wrc-04 keeps the mask as an
injected constructor parameter, with its `DefaultKeywordMask` /
`ReadKeywordMask` constants' pendency comment to be updated to FINAL by
wrc-07.

## Consequences

Positive:

- Event-time-correct value data straight from the kernel — the TOCTOU
  live-registry re-read (`RegistryEvent.GetData()`, double OpenKey per value
  event) is eliminated, not worked around.
- Full absolute key paths on every event; `RegParents` pointer bookkeeping
  and its unbounded dictionary go away, as does `RegValueCache`.
- New capability: pre-change values (`PreviousData*`) on overwrites, with
  correct create-vs-overwrite semantics — the legacy sensor never had this.
- The broken ExpandString decode is replaced by a byte-level decoder verified
  against all six REG types in probe3/probe5.
- All `ToString()`/`Split('"')` fixed-index parsing is deleted.

Negative / costs:

- **Dependence on an undocumented kernel mechanism** that Microsoft may
  change or remove in any update, with no deprecation signal. Mitigations:
  periodic re-assert, capture-loss detection, and the sensor-health-check
  layer making a silent regression visible in Wintap.log.
- **Global side effect:** the capture flag is sticky provider-wide state, so
  Wintap turns it on for every consumer of this provider on the host, and
  cannot guarantee exclusive ownership of its lifetime in either direction.
- Larger payloads (self-test `SetValueKey` grew from 58-60 to 210-272 bytes;
  `CapturedData` also rides high-volume query/enumerate events), so the
  keyword-mask choice and a with-capture overhead measurement are mandatory,
  not optional.
- `WintapAPI` schema work is required (pre/post value emission, QWORD) —
  decided 2026-08-25 as a minimal additive extension (`DataTypeEnum` +
  `QWORD`/`NONE`; `RegActivityObject` + `PreviousData`/`PreviousDataType`),
  unit wrc-05.
- The session-handle decision (Option A) accepts a private-API reflection
  dependency on TraceEvent's `m_SessionHandle`, mitigated by three fail-loud
  guards naming the pinned version (3.1.23) and by the repo's deliberate
  version pinning; Option C (upstream accessor) remains an optional parallel
  track.
- As possibly the first written documentation of the mechanism, this ADR is
  the de facto reference; it must stay standalone and evidence-anchored.

## Alternatives Considered

1. **Hybrid classic-kernel KCB rundown + manifest provider** (seed a
   pointer→path map from a classic rundown, join manifest events against
   it). Rejected on decisive negative evidence (retroactive spike wrc-01):
   with a 6,339-entry KCB map harvested at session stop, **0** manifest
   `BaseObject`/`KeyObject` lookups resolved via the KCB map in the baseline
   run (6,268 create/open and 19,827 value-op lookups went unresolved;
   replicated in probe3 with 25,259 unresolved) — classic KCB `KeyHandle`
   addresses and manifest `KeyObject` pointers are disjoint namespaces. Also
   structurally unfit: KCB rundown arrives only at session stop (perfview
   issue #928), and TraceEvent's registry name tracking is disabled for
   real-time sources and marked suspect by its authors.
2. **Repair the status quo** (keep `RegParents` live pointer bookkeeping,
   fix only the parsing). Rejected: even done correctly, the baseline run's
   live-map resolution ceiling was 46.2% (create/open) / 60.1% (value ops),
   the map is unbounded by construction, and values would still require the
   TOCTOU live re-read.
3. **Classic kernel provider only** (NT Kernel Logger `Registry` keyword).
   Rejected: value bytes are not carried, path resolution has the same KCB
   problems as (1), and the one-kernel-logger constraint is shared with the
   process/file sensors.
4. **Sanction the live registry re-read** as the value source. Rejected:
   TOCTOU by construction, double OpenKey per value event, and the source of
   the ExpandString bug class.
5. **Wait for Microsoft / documented APIs only.** Rejected: the empty
   CapturedData/KeyName gap is publicly described as a known limitation not
   prioritized for a fix; no documented path to event-time value capture
   exists.
