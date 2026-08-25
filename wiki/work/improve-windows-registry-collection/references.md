---
title: "References: Improve Windows Registry Collection"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryEventParsers.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryManager.cs
  - ../wintap/wintap/platform/windows/sensor/shared/models/RegistryEvent.cs
  - ../wintap/wintap/platform/windows/sensor/shared/models/KernelRegistryEvent.cs
  - ../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/etl/esper/registry.epl
  - ../wintap/wintap/core/etl/extract/RegistrySerializer.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: llm-agent
status: draft
source_paths: wiki/work/improve-windows-registry-collection/references.md
tags: [feature-work, registry, etw, windows-sensor, capture-mode, source-map]
---

# References: Improve Windows Registry Collection

Source map for the `wrc` feature. All wintap paths are live cites (never
copied); POC artifacts are external evidence with no repo home, cited by
absolute path.

## Legacy sensor under replacement (wrc-06 deletes/rewrites)

- `../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs` —
  **rewrite target.** Dispatches on `obj.OpcodeName` strings; path repair via
  `regMan.RegParents` pointer map; `parseRegSetValue` does the TOCTOU
  `RegistryEvent.GetData()` live re-read and feeds the unbounded
  `RegValueCache`; `parseReadValue` gated by
  `Properties.Settings.Default.CollectRegistryRead` (line 62; gate preserved
  in the rewrite); emission via `sendRegEventToEsper` →
  `WintapMessage.RegActivityObject` → `EventChannel.Send` (lines 252–286),
  throwing `ArgumentException` on unparseable activity/data types.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs -->
- `../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryEventParsers.cs`
  — **delete.** Note: lives under `etw/helpers/`, not `etw/` as some earlier
  notes said. `BaseEvent` splits `obj.ToString()` on `'"'` and reads fixed
  indices (`EventArray[3]` = PID, `[13]`/`[15]` = Base/KeyObject hex,
  `[23]` = path); `RegKeyEvent`, `RegDeleteValueEvent`, `RegDeleteKeyEvent`,
  `RegCloseEvent`, `RegSetValueEvent` all inherit it (RegSetValueEvent
  additionally uses typed `PayloadByName` — the only typed access in the
  legacy path).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryEventParsers.cs -->
- `../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryManager.cs` —
  **delete.** The two unbounded dictionaries: `RegParents`
  (`Dictionary<ulong,string>`, pointer→path) and `RegValueCache`
  (`Dictionary<string,string>`).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryManager.cs -->
- `../wintap/wintap/platform/windows/sensor/shared/models/RegistryEvent.cs` —
  **delete.** `GetData()` re-reads the live registry per event (double
  OpenKey: `registryKeyExists` opens, then the value read opens again); the
  ExpandString branch expands `Data` while `Data` is still `""` — the
  always-empty ExpandString bug (line 109).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/shared/models/RegistryEvent.cs -->
- `../wintap/wintap/platform/windows/sensor/shared/models/KernelRegistryEvent.cs`
  — **delete.** Near-duplicate of `RegistryEvent` with the same `GetData()`
  defects; no users outside the registry path (repo-wide search 2026-08-25
  found only its own definition).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/shared/models/KernelRegistryEvent.cs -->

## Session/enable path (wrc-04 decision surface)

- `../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs` —
  file defines class `EtwProviderCollector` (name mismatch is historical).
  `Start()` creates `TraceEventSession` (line 51), enables with
  `EnableProvider(EtwProviderId, EventLevel, TraceEventFlags)` (line 55) —
  RegistrySensor never assigns `EventLevel`/`TraceEventFlags`, so both ride
  their defaults — then wires `RegisteredTraceEventParser.All` (line 58).
  The session handle is not exposed → resolved 2026-08-25 as ADR Option A
  (guarded reflection); the wrc-04 enabler is handed this live session at
  wire-in (wrc-06).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/shared/EtwProviderSensor.cs §Start -->
- `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`
  — sensors are instantiated by reflection over `Properties.Settings` entries
  whose names end in `Sensor` and are `True` (line 59); `RegistrySensor`
  toggles live in `App.config`/`Settings.settings` (`RegistrySensor`,
  `CollectRegistryRead`).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs §Start -->

## WintapAPI integration points (wrc-05 decision surface)

- `../wintap/shared/WintapAPI/WintapMessage.cs` —
  `RegActivityObject { Path, DataType, ValueName, Data, PID }` (lines
  225–232); `DataTypeEnum { STRING, DWORD, BINARY, MULTI_SZ, EXPAND_SZ }`
  (line 71) — **no QWORD, no unknown/none, no pre-change fields**;
  `ActivityTypeEnum` (line 68) already carries `Read, Write, CreateKey,
  DeleteKey, DeleteValue` used by the legacy sensor. Shape decided
  2026-08-25 (minimal extension: `QWORD`/`NONE` appended;
  `PreviousData`/`PreviousDataType` added) — instructed as wrc-05.
  <!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §RegActivityObject -->

## Parquet value plumbing (wrc-08 targets, rolled in 2026-08-25)

- `../wintap/wintap/core/etl/esper/registry.epl` — **wrc-08 target.** The
  Esper aggregation statement for Registry (10 s `win:time_batch`, grouped
  by path/dataType/valueName/data/PidHash/PID/activityType/ProcessName).
  Selects `registry.data`/`registry.dataType` but no previous-value fields;
  `AgentId` is selected without being grouped (NEsper leniency — observed,
  not to be imitated). Shipped as an EmbeddedResource AND as Content copied
  to `<output>\esper\` (`Wintap.Common.props:110-133`);
  `Serializer.readQueryFromFile` prefers the on-disk copy
  (`Serializer.cs:439-468`). **`publish/esper/registry.epl` is gitignored
  `dotnet publish` output** (`.gitignore:174`) — a build artifact, not an
  independently maintained copy; only the source file is in scope.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/registry.epl -->
- `../wintap/wintap/core/etl/extract/RegistrySerializer.cs` — **wrc-08
  target.** Flattens the EPL aggregate to the parquet row (15 columns
  today: `AgentId, ActivityType, ProcessName, Reg_Data, EventCount,
  FirstSeenMs, LastSeenMs, PID, PidHash, HostHame(sic), Reg_Path,
  Reg_Value, Reg_Id_Hash, MessageType, EventTime`); writes `Reg_Data` only
  — never reads the `dataType` the EPL already selects. `Reg_` column
  prefix is the registry convention (FileSerializer uses `File_`); enums
  serialize as name strings via `.ToString()`. Parquet schema is inferred
  per flush from the first ExpandoObject
  (`ParquetWriter.DetermineSchemaFromExpando`, `ParquetWriter.cs:262-289`),
  so always-present new members become columns with no ParquetWriter
  change. Note: `WintapETL.cs:163-166` (`RegWorker_DoWork` →
  `reg-activity.epl`) is a dead path — no callers, file does not exist;
  sweep-queue candidate.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/RegistrySerializer.cs §HandleSensorEvent -->

## POC spike evidence (external; no repo home)

- `C:\PUBLIC\wrc-poc\Program.cs` — the spike harness: KCB rundown harvest
  (classic session `WrcPoc.KernelRundown`), live manifest session
  (`WrcPoc.ManifestRegistry`), `EnableProviderWithSystemFlags` (reflection
  handle acquisition + `EnableTraceEx2` P/Invoke, disable-then-enable),
  six-REG-type self-test with overwrite pass, `DecodeRegValue` (the verified
  decoder wrc-03 ports), CLI `WrcPoc.exe [seconds] [flagsHex] [filterTypeHex]
  [dataSize 4|8] [maskHex]` — the 5th argument was added (main session,
  2026-08-25) for the pending Architect-run probe8 (narrowed
  `MatchAnyKeyword` × capture-filter composition); it feeds both enable
  calls.
- `C:\PUBLIC\wrc-poc\run.log` — baseline (no filter): KeyName 0/49,679;
  SetValueKey CapturedData 0/58; KCB-map joins 0 (wrc-01's negative result);
  event-volume and payload-schema tables (IDs 1–14 + hive family).
- `C:\PUBLIC\wrc-poc\probe1.log` / `probe2.log` — 8-byte payload silent
  no-ops (Type 0x1 / 0x80000001).
- `C:\PUBLIC\wrc-poc\probe3.log` — first success (4-byte payload): KeyName
  72,601/72,604; CapturedData 73/73; six-type decode verification.
- `C:\PUBLIC\wrc-poc\probe4.log` — Type-field irrelevance (0x80000001, 4
  bytes): 16,807/16,807; 79/79.
- `C:\PUBLIC\wrc-poc\probe5.log` — full verification run: KeyName
  94,068/94,068; CapturedData 170/170; PreviousData byte-perfect for all six
  REG types; raw payload dumps (wrc-03's test fixtures).
- `C:\PUBLIC\wrc-poc\probe6.log` — stickiness: capture stayed active across
  explicit disable + filterless (no-op 8-byte) re-enable: 35,762/35,762;
  66/66.
- `C:\PUBLIC\wrc-poc\probe8.log` — mask × capture composition (Architect-run
  2026-08-25, `WrcPoc.exe 15 FFFFFFFF 1 4 5300`): **clean PASS** — KeyName
  106/106, CapturedData 91/91, six types byte-perfect on CapturedData AND
  PreviousData, 0 events lost, 470 events/15 s with masked-out types
  structurally absent; CreateKey schema (no KeyName; BaseName+RelativeName
  join, 0 unresolved) and REG_NONE first-write encoding (grounds
  `DataTypeEnum.NONE`). Mask decision FINAL on this evidence.
- `C:\PUBLIC\wrc-poc\CONTINUATION.md` — the spike sessions' durable handoff
  note (superseded by the wiki artifacts, kept as provenance).

## Decision and feature artifacts

- [[wiki/decision/registry-provider-strategy]] — the capture-mode ADR
  (mechanism record, probe matrix, negative results, consequences,
  session-handle OPEN options).
- [[wiki/work/improve-windows-registry-collection/brief]] — frozen acceptance
  criteria (2026-08-25).
- [[wiki/work/improve-windows-registry-collection/implementation_plan]] —
  unit breakdown and Open Questions.
- [[wiki/work/improve-windows-registry-collection/interview]] — playback of
  the spike-settled decisions (sealed section untouched until close-out).
- [[wiki/work/improve-windows-registry-collection/metrics]] — mini-lab record.
- `../wintap/developer_docs/instructions/wrc-01-kcb-correlation-spike.md`,
  `wrc-02-capture-filter-spike.md` — retroactive spike records (local-only:
  `developer_docs/` is gitignored in the wintap repo; the wiki carries the
  durable evidence).
- `../wintap/developer_docs/instructions/wrc-03-payload-decode-core.md`,
  `wrc-04-capture-enablement-engine.md`,
  `wrc-05-wintapmessage-registry-schema.md` — drafted 2026-08-25,
  **Status: Approved (2026-08-25)**; wrc-03 embeds the probe5
  byte fixtures verbatim and wrc-04 the full interop/call-sequence spec, so
  the Developer never needs POC access.
- `../wintap/developer_docs/instructions/wrc-06-manifest-registry-sensor.md`
  — drafted and **Approved 2026-08-25** (Read events `Data=""`/`DataType=NONE`;
  one-line `Counter++`; `Registry.PID` legacy-parity wart retained): the
  manifest-only sensor rewrite + legacy-file deletion + `EtwProviderSensor`
  `OnEtwSessionStarted` hook.
- `../wintap/developer_docs/instructions/wrc-07-mask-canary-live-verification.md`
  — drafted 2026-08-25 after probe8 PASS, **Status: Approved (2026-08-25,
  canary knobs confirmed as proposed)**; executed last, after wrc-06: final
  mask wiring (0x5300/0x5700 off `CollectRegistryRead`), canary, and the
  verification.md evidence contract for the Architect-run live run.
- `../wintap/developer_docs/instructions/wrc-08-parquet-value-plumbing.md`
  — drafted and **Approved 2026-08-25**;
  the rolled-in scoped Non-Goals exception (Architect decision 2026-08-25,
  shc-03 realize-now precedent; NOT a criteria amendment): registry EPL
  select/group-by additions + three new `Reg_` serializer columns; executes
  last; close-out waits on it.
- All five unit audits are filed at
  `../wintap/developer_docs/audits/wrc-03..07-*.md` (Status: Complete,
  2026-08-25; local-only — `developer_docs/` is gitignored).
- [[wiki/work/improve-windows-registry-collection/verification]] — durable
  verification record: unit-audit evidence pointers plus the **Architect-run
  live-verification record (2026-08-25)** with the wrc-07 §3
  evidence-contract coverage table (availability-anchor candidate, pending
  Architect acceptance).

## Related wiki pages

- [[wiki/diagnostic/windows-sensor-sweep-queue]] — carries "ungated Registry
  CreateKey/DeleteKey/DeleteValue emit sites" from the shc feature; the wrc-06
  rewrite closes that item by construction (KeyName is always the full
  absolute path). Cross-noted there at fold-in time.
- [[wiki/component/sensor-health-monitor]] — the egress `path_unqualified`
  check counts exactly the legacy sensor's relative-fragment emissions; the
  rewrite should drive that counter to zero for Registry.
- [[wiki/component/windows-sensor-service-internals]] — EventChannel routing
  the new sensor emits into.
