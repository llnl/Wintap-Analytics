---
title: "Design: Windows Sensor Health-Check"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/core/etl/load/DirectParquetSink.cs
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - ../wintap/wintap/core/etl/extract/DefaultSerializer.cs
  - ../wintap/shared/WintapAPI/WintapMessage.cs
  - ../wintap/wintap/core/shared/ConfigManager.cs
  - ../wintap/wintap/core/shared/ProcessHash.cs
  - ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs
  - ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryEventParsers.cs
  - ../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs
  - ../wintap/wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs
  - ../wintap/wintap/core/shared/StateManager.cs
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/windows-sensor-health-check/design.md
tags: [feature-work, health-check, windows-sensor, qa, data-quality, egress, liveness]
---

# Feature Design: Windows Sensor Health-Check

> **Feature closed 2026-08-25.** Stabilized behavior promoted to the
> canonical page [[wiki/component/sensor-health-monitor]]. All sweep-scope
> defects and findings recorded in this document (WintapAlert self-PID
> drop, ungated Registry emit sites, dead `Serializer.Listen`,
> `TranslateTransientPath` authority problem, QueryDosDevice
> consolidation, MemoryMap reroute question, `eventtime_invalid`
> candidate) are consolidated — together with the WintapLogger defects and
> the live-run findings — into the follow-on **sweep-feature queue**:
> [[wiki/diagnostic/windows-sensor-sweep-queue]].

> **Revised 2026-08-24 twice (same day as feature open).**
> **#1 (Architect redirection):** reporting is periodic aggregated
> Wintap.log entries via WintapLogger — nothing else; no WintapMessage
> schema changes anywhere in the feature.
> **#2 (Architect review of shc-01):** the v1 check list is definitive.
> "Unknown" attribution now **fails** ("this is exactly the failure mode i
> want to catch"); File/Registry paths must be fully qualified; six
> high-volume streams get a per-5-second liveness requirement;
> `eventtime_invalid` is dropped from v1 (future candidate, below).
> **#3 (Architect decision on the shc-02 elevation conflict):** enabling
> unit shc-03 replaces the diskpart drive mapping with QueryDosDevice;
> shc-02 paused until it lands. Same day, shc-03 was **widened** to include
> the `fromNative` guard fix (scoped `BaseWindowsSensor.cs` exception) so
> the accuracy fix is realized immediately. See "shc-03 Insert" section
> below. Frozen criteria unchanged.

## Summary

A static, allocation-free-on-pass health monitor hooked into
`EventChannel.Send` — the actual egress choke point every Windows sensor
calls — that runs a fixed registry of constant-time checks on each
WintapMessage, increments per-(sensor-stream, check) failure counters,
captures a capped first-N sample of offending events, watches six
high-volume streams for 5-second silences, and periodically writes compact
aggregated summary lines to Wintap.log via WintapLogger.

## Ground Truth: How Messages Actually Egress

Verified 2026-08-24 against the live repo:

- **Choke point.** All Windows sensors call
  `EventChannel.Send(WintapMessage)`
  (`wintap/core/infrastructure/EventChannel.cs` ~line 221). Send: (1) drops
  events where `PID == StateManager.WintapPID` (Wintap's own PID); (2) tags
  `AgentId`; (3) **if `DirectParquetSink.IsEnabled`, saves directly to the
  parquet sink and returns — before any enrichment**; (4) otherwise resolves
  and attaches `PidHash`/`ProcessName` for non-Process events, resolves
  parent identity for Process events; (5) sends to Esper via
  `SendEventBean`.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->
- **Known bypass.** `MemoryMapSensor.cs:308` calls
  `EventChannel.EsperRuntime.EventService.SendEventBean(wm, "WintapMessage")`
  directly, skipping Send entirely. Everything else routes through Send
  (verified by grep across `wintap/platform/windows` and `wintap/core`).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/MemoryMapSensor.cs §308 -->
- **Correction (2026-08-24, shc-02 grounding pass):** a repo-wide
  `SendEventBean` grep finds a **third** direct call at
  `Serializer.cs:150` — `Serializer.Listen(WintapMessage)` re-injects a
  WintapMessage into Esper. It is **dead code**: no callers anywhere in the
  repo, and its own doc comment reads "TODO: do we still need this?". It
  gets **no `Inspect` call** (wiring dead code would create a latent
  double-inspection path if ever revived); flagged as a deletion candidate
  for the follow-on sweep feature.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/Serializer.cs §Listen -->
- **Wire-in grounding (shc-02, 2026-08-24).** Service lifecycle: sensors
  start in `WinTapSvc.StartupWorkerAsync`
  (`wintap/core/infrastructure/WintapSvcCore.cs`) via
  `subscriptionMgr.Start()` inside the `WINTAP_DISABLE_SENSORS`-gated block;
  shutdown is `WinTapSvc.StopAsync`, which stops plugins then
  `subscriptionMgr.Stop()` and closes WintapLogger last. Monitor `Start()`
  therefore lands immediately after `subscriptionMgr.Start()` (grace begins
  after sensors are live; monitor intentionally not started when sensors
  are disabled), and monitor `Stop()` lands as the first action in
  `StopAsync` (suppresses shutdown stall alarms; final flush happens while
  the logger is open).
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync/§StopAsync -->
- **Silent-drop paths the checks make visible.** `Serializer.Save` throws
  `NULL_PIDHASH` for empty PidHash (exception swallowed upstream);
  `DefaultSerializer.HandleSensorEvent` NREs on a missing/null payload
  property and logs at Debug. Both are silent data loss today.
- **Recorded for the follow-on sweep (does not affect this feature):**
  `Watchdog.sendWintapAlert` / `PluginExceptionHandler.SendWintapAlert`
  construct WintapAlert messages with Wintap's own PID, which Send's first
  filter drops — self-generated WintapAlerts appear silently discarded
  today.
  <!-- SYNTHESIS: inferred from ../wintap/wintap/core/infrastructure/Watchdog.cs §sendWintapAlert and ../wintap/wintap/core/infrastructure/EventChannel.cs §Send -->

## Ground Truth: The Unknown-Attribution Sentinel

- On owner-resolution failure for non-Process events, `EventChannel.Send`
  sets `ProcessName = "Unknown"` (exact literal) and a **fabricated**
  PidHash — either the resolver's `GetPidHash` fallback or a locally
  generated `ProcessHash.GenPidHash(PID, EventTime)`. The fabricated hash is
  built by the real formula and is **not distinguishable from a legitimate
  hash**; the `"Unknown"` ProcessName is the reliable marker of that
  fallback.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Send owner-resolution fallback -->
- The only *distinguishable* sentinel hash in the codebase is
  `EventChannel.UnknownPidHash = ProcessHash.GenPidHash(-1, 0)` — currently
  assigned only to `Process.ParentPidHash` for unresolvable parents. The
  formula (`ProcessHash.GenKeyForProcess`) mixes `Environment.MachineName`
  and `StateManager.AgentId` into the pre-image, so **the sentinel value is
  host-specific, not a constant** — it must be computed at runtime (and
  injected as a seam in tests).
  <!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ProcessHash.cs §GenKeyForProcess; ../wintap/wintap/core/infrastructure/EventChannel.cs §UnknownPidHash -->
- Consequence for the check: `process_unresolved` fails on
  `ProcessName == "Unknown"` (case-insensitive ordinal) **or**
  `PidHash == GenPidHash(-1, 0)`. The PidHash arm is defensive — nothing
  writes the sentinel to the message-level PidHash today, but the Architect
  requirement is "PidHash should NEVER point to unknown", and the
  comparison is one cached string equality. Parent-level sentinels
  (`ParentPidHash`/`ParentProcessName = "Unknown"`, a designed best-effort
  outcome of the ptr ordering-gap handling) are **excluded from v1** as a
  distinct concern — candidate future check via the registry.

## Ground Truth: Emitted File And Registry Path Forms

- **File** (`FileSensor.sendFileEvent`): the emitted `File.Path` is
  **lowercased** (`filePath.ToLower()`); origins are TraceEvent kernel
  FileIO `FileName` values or the sensor's fileKey/fileObject table. Fully
  qualified forms actually seen at egress: drive-letter-rooted (`c:\...`),
  NT device form (`\device\harddiskvolumeN\...` when TraceEvent could not
  map the volume), and UNC (`\\server\share\...`).
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs §sendFileEvent, §resolveIoFilePath -->
- **Registry** (`RegistrySensor` + `RegKeyEvent`): key paths are built from
  kernel KCB names, **lowercased with leading backslashes trimmed at the
  root**, giving the canonical emitted root `registry\...` (e.g.
  `registry\machine\software\...`, `registry\user\<sid>\...`) with no
  leading backslash. `parseRegSetValue`/query paths are gated on
  `Path.StartsWith("registry")`, **but the CreateKey/DeleteKey/DeleteValue
  emit sites are ungated** — a `RegParents` entry whose parent chain was
  never rooted can egress as a relative fragment today. The
  `path_unqualified` check will make exactly that visible.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/helpers/RegistryEventParsers.cs §RegKeyEvent/§FixPath; ../wintap/wintap/platform/windows/sensor/etw/RegistrySensor.cs §parseRegCreateKCB/§parseRegSetValue/§sendRegEventToEsper -->

## shc-03 Insert: The Diskpart Elevation Snag And The QueryDosDevice Drive Map

**The snag (2026-08-24).** The Developer started shc-02 and stopped
correctly on an instruction/codebase conflict: the shc-02 integration tests
(required to be no-admin) fail because the first `EventChannel.Send`
initializes `StateManager`, whose constructor calls
`WindowsStateManager.RefreshDriveMap()`
(`wintap/platform/windows/infrastructure/WindowsStateManager.cs:35`). That
method writes a temp script and spawns `diskpart.exe`, which requires
elevation — `Win32Exception: The requested operation requires elevation` —
and the call has no try/catch, so the exception kills the `StateManager`
type initializer in any non-elevated process. No audit was filed; shc-02 is
paused. (The shc-02 instruction's fixture note "none of this requires
elevation" was wrong on exactly this point; it becomes true once shc-03
lands, so the approved instruction is unchanged.)
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs §RefreshDriveMap; ../wintap/wintap/core/shared/StateManager.cs §ctor -->

**Architect decision:** insert enabling unit **shc-03 — replace the
diskpart drive mapping with QueryDosDevice** — landing before shc-02
resumes (numbering note: shc-03 first despite the number). Not a criteria
amendment; the frozen acceptance criteria are unchanged.

**Grounded consumer map (verified 2026-08-24):**

- `RefreshDriveMap()` has exactly **one production caller**: the
  `StateManager` singleton constructor
  (`wintap/core/shared/StateManager.cs:124`, `#if WINDOWS`). Despite the
  name there is **no refresh cadence** — the 60 s `StateRefresh_Elapsed`
  timer refreshes only user-busy and battery state. The drive map is built
  once per process lifetime; drives mounted later are never picked up
  (existing behavior, preserved; `TranslateTransientPath` exists for the
  transient case).
  <!-- GROUND_TRUTH: ../wintap/wintap/core/shared/StateManager.cs §ctor/§StateRefresh_Elapsed -->
- `StateManager.State.DriveMap` has exactly **one reader**:
  `BaseWindowsSensor.fromNative(path, driveMap)` (line ~388), called from
  `TranslateProcessPath` when a raw process path contains
  `\device\harddiskvolume`. It parses the trailing `N` from the path, looks
  up `VolumeNumber == N`, and rewrites `\device\harddiskvolumeN` →
  `<VolumeLetter>:` in lowercased paths. Nothing serializes `DiskVolume`
  to any output; `VolumeLabel`/`FileSystem`/`VolumeType` are never
  populated or read.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs §TranslateProcessPath/§fromNative -->
- A duplicate `DiskVolume` class exists in the separate
  `platform/windows/WintapCoreSvcMgr` project with no drive-map logic —
  unaffected.

**Rationale for QueryDosDevice (Architect-directed, grounded):**

1. **No elevation, no child process** — unblocks shc-02's no-admin tests
   and removes a per-startup spawn + temp-file write.
2. **Correctness — the current mapping is built from the wrong number.**
   diskpart's `Volume ###` column is an enumeration index; the parser takes
   it as `VolumeNumber` (`lineArray[3]`). But `fromNative` looks up the NT
   `HarddiskVolumeN` number from the path — a different namespace (dynamic
   disks, mounted VHDs, and ordinary EFI/recovery layouts make them
   diverge). Today most lookups silently miss and fall into `fromNative`'s
   hardcode-`c:` fallbacks — accidentally right on single-drive hosts,
   wrong on multi-drive hosts. `QueryDosDevice` returns the authoritative
   NT device name per letter; this is the feature's first genuine accuracy
   fix.
3. **Locale robustness** — the diskpart parser splits localized fixed-column
   text (`lineArray[3]`/`lineArray[8]` of a space-split line); NT device
   names are stable.
4. **Efficiency** — 26 cheap API calls vs. process spawn + stdout parse.

**In-repo precedent:** `WindowsProcessSensor` already P/Invokes
`QueryDosDevice` (declaration at line ~1738; used by
`TryTranslateDevicePathToWin32Path` for `\Device\...` process image paths).
shc-03 mirrors that exact signature. Observation for later: that method
enumerates letters per call rather than using the cached `DriveMap`;
consolidation is a possible sweep-feature cleanup, not shc scope.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §TryTranslateDevicePathToWin32Path -->

**Edge cases (normative in the shc-03 instruction):** letters whose device
name is not `\Device\HarddiskVolume<N>` — network
(`\Device\LanmanRedirector\...`, `\Device\Mup\...`), SUBST (`\??\...`),
optical (`\Device\CdRom0`) — are skipped, not errors; unassigned letters
return failure from `QueryDosDevice` — skip; the function never throws
(Warn and return what it has — a strengthening of today's fail-soft, since
the current code can throw out of `Process.Start`).

**Residual guard — Architect decision (2026-08-24, same day): widen shc-03
rather than defer.** The flagged limitation: `fromNative`'s guard
`if (volumeNumber <= diskVolumes.Count)` compares an NT volume number
against the **count** of mapped letters. On typical hosts the system volume
is `HarddiskVolume3`+ (EFI/recovery consume low numbers) while only 1–2
letters exist, so the guard routes around the now-correct map and hardcodes
`c:` — the full accuracy benefit of the QueryDosDevice map would be
unrealized until the guard is removed. The Architect directed that **the
accuracy fix be realized now, not deferred to the sweep feature**: shc-03
is widened to include the `fromNative` guard fix, with an explicit scoped
exception to the feature's no-sensor-changes posture for exactly
`BaseWindowsSensor.cs` and exactly this fix. The fix: direct `VolumeNumber`
lookup (guard removed); the existing logged `c:` fallback preserved
verbatim on a genuine miss (no new handling invented); the single-drive
`harddiskvolume1` hack removed as provably dead logic (it only ran when the
lookup had already guaranteed `dv.VolumeNumber == volumeNumber`, and it
mutated the shared cached `DriveMap` entry as a side effect); accessibility
`private` → `internal` as the entire testability seam (no delegate
injection or new overload — tests construct `BaseWindowsSensor` directly,
the established wpc test pattern, via `InternalsVisibleTo`).
`TranslateTransientPath`'s WMI partition-number parse has a similar
authority problem (partition ≠ volume numbers) — remains a sweep candidate.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/shared/BaseWindowsSensor.cs §fromNative/§TranslateTransientPath -->

## Proposed Approach

### Hook placement

One internal inspection entry point, `SensorHealthMonitor.Inspect(msg)`,
invoked from **two sites inside `EventChannel.Send`**:

1. immediately before `DirectParquetSink.Save(streamedEvent)` — inspects the
   direct-parquet branch (note: pre-enrichment by design of that branch);
2. on the normal branch **post-enrichment and post-registration**,
   immediately before the `skipEsperSend` early return that guards
   `EsperRuntime.EventService.SendEventBean(...)` — so PidHash/ProcessName
   checks evaluate the final egress values. (Refined 2026-08-24 during
   shc-02 drafting: placing the call just *above* the `skipEsperSend` check
   rather than below it is production-identical — the variable is a
   dev/test-only seam — and lets integration tests drive `Send` end-to-end
   without initializing a live Esper egress.) Because branch 1 returns,
   **every message takes exactly one `Inspect`** — the direct-parquet
   early-return path cannot double-inspect.

Plus a **one-line `Inspect` call in `MemoryMapSensor`** before its direct
`SendEventBean` (adopted default, 2026-08-24) — also the prerequisite for
meaningful MemoryMap liveness.

### Check engine (shc-01)

- `internal interface IWintapHealthCheck`: `Name` (snake_case), constant-time
  never-throwing `Passes(msg)`, `Describe(msg)` called only when a sample
  slot is free.
- `internal sealed class SensorHealthMonitor` — instance class with a static
  default (test-friendly seams: check list, unknown-sentinel value, log
  sink). Fixed `Interlocked` counter arrays indexed by
  `(int)MessageType`; one reserved `_unknown` bucket for enum garbage;
  lazily allocated capped sample slots; fail-open wrapper (a health-layer
  defect disables the monitor for the session with one Warn line, never
  breaking telemetry egress).
- **Checked counters are monotonic lifetime totals** (never reset); the
  flush computes per-window deltas against its previous snapshot, and the
  liveness watchdog computes per-tick deltas against its own. One
  `Interlocked.Increment` per message, no reset races, and liveness gets
  its data for free.

**Definitive v1 checks (Architect, 2026-08-24 — amendment #2):**

| Name | Fails when | Streams |
|---|---|---|
| `pidhash_missing` | `PidHash` null/empty/whitespace | all |
| `process_unresolved` | `ProcessName` equals `"Unknown"` (OrdinalIgnoreCase) OR `PidHash` equals the host-specific unknown sentinel `GenPidHash(-1, 0)` | all |
| `processname_missing` | `ProcessName` null/empty/whitespace | all |
| `payload_mismatch` | payload property for the MessageType missing or null (alias `ProcessPartial → Process`; reflection resolved once at construction) | all |
| `path_unqualified` | `File.Path` not rooted `x:\` / `\\` / `\device\`, or `Registry.Path` not rooted `registry\` (both lowercase per the sensors' normalization); null/empty path also fails | File, Registry only; other streams pass by construction |

### Stream liveness (shc-01, definitive condition)

Watched streams: **File, Registry, MemoryMap, ImageLoad, TcpConnection,
UdpPacket** ("known high-volume event providers"; Tcp/Udp map to the
`TcpConnection`/`UdpPacket` MessageTypes). Requirement: nonzero inspected
count per 5-second interval; a zero interval is a critical condition.

Mechanism (boring, allocation-free on the hot path):

- A second small `System.Timers.Timer` at a fixed 5 s tick (separate from
  the flush timer; independent cadences, no coupling). The tick handler
  reads the monotonic checked totals for the six watched streams and
  compares against its own previous-tick copy — the hot path contributes
  nothing beyond the increment it already does.
- Per-stream two-state machine (OK / STALLED), **transition-only logging**:
  - OK → STALLED (first zero-delta tick after grace): exactly **one**
    `LogLevel.Error` line —
    `SensorHealth STALL: stream=File no events in 5s interval`.
  - STALLED → OK (first nonzero-delta tick): exactly **one**
    `LogLevel.Info` line with duration —
    `SensorHealth RECOVERED: stream=File stalledSeconds=35`.
  - No lines while a stall persists; no lines per healthy interval.
- **Startup grace period:** a fixed 60 s after `Start()` during which no
  stall transitions fire (sensors and ETW sessions are still spinning up).
- **Stop suppression:** `Stop()` halts the liveness timer and clears all
  liveness state; a later `Start()` re-arms the grace period — no stall or
  recovery lines fire across a stop/start cycle.
- **MemoryMap caveat (documented):** MemoryMap events bypass
  `EventChannel.Send` today; its liveness signal is only meaningful once
  shc-02 wires the `Inspect` call at the sensor's direct-send site. Both
  land in the same unit, so the wired system is consistent; unit tests in
  shc-01 exercise the state machine directly.

### Reporting: periodic Wintap.log summary lines (shc-01)

A `System.Timers.Timer` (default 60 s, `WINTAP_HEALTH_FLUSH_SECONDS`)
drains the window and writes via WintapLogger:

- **One summary line** per window with any activity (Info), key=value
  parseable, per-window deltas, only streams with nonzero counts:
  `SensorHealth: window=2026-08-24T18:00:00Z..2026-08-24T18:01:00Z checked Process=1234 File=56789 Registry=4021`
- **One line per (stream, check) with a nonzero failure count** (Warn),
  samples joined by `" | "`:
  `SensorHealth FAIL: stream=File check=path_unqualified count=12 samples: PID=442 ActivityType=Read Path=windows\temp\x.tmp | ...`
- Liveness transition lines (above) are written by the 5 s tick as they
  happen, not batched into the flush — a stalled high-volume stream is a
  critical condition and should not wait up to 60 s for visibility.

No line per failure, nothing on idle windows. Worst case: 1 + (active
streams × failing checks) lines per minute plus one line per liveness
transition. The log sink is injectable so formatting, flush, and liveness
semantics are unit-testable without the real Wintap.log.

### Configuration

Standard `ConfigManager.GetValue<string>` plumbing (env-overridable
`WINTAP_*` keys):

- `WINTAP_HEALTH_ENABLED` — default **true on Windows** (`false` elsewhere).
- `WINTAP_HEALTH_FLUSH_SECONDS` — default 60, min 5.
- `WINTAP_HEALTH_SAMPLE_CAP` — default 3, clamp 0–20.

The liveness tick (5 s) and grace period (60 s) are fixed constants —
Architect-specified condition parameters, not tunables.

### Overhead posture (constant-time argument)

Pass path per message: one enabled-flag check, one `Interlocked.Increment`,
five check evaluations (null/whitespace tests, two cached string
comparisons, one prebuilt-getter payload fetch + null test, and for
File/Registry only a short prefix test on an already-in-hand string). No
allocation, no locks, no dictionary hashing. Failure path adds one
`Interlocked.Increment` and — only while a sample slot is free (≤ N per
window) — one string build. Liveness and flush work run on their timers,
off the hot path, O(streams × checks) per firing.

## Data Model Or Schema Changes

**None.** No WintapMessage change, no new MessageType, no serializer/EPL/
Parquet/DuckDB change. The feature's only output is Wintap.log text.

## Edge Cases

- **Direct-parquet mode** never enriches, so `pidhash_missing` and
  `process_unresolved` behavior differs by branch; direct mode is a
  diagnostic path and the summary lines make its data quality visible.
- **`"Unknown"` ProcessName now fails** (`process_unresolved`) — reversed
  from the first draft by Architect amendment #2. Expect nonzero steady
  counts on hosts with resolver gaps; that is signal, not noise, per the
  Architect ("exactly the failure mode i want to catch"). It is a separate
  counter from `processname_missing`, so genuinely absent names and
  unresolved attributions stay distinguishable.
- **Parent-lineage sentinels** (`ParentPidHash == GenPidHash(-1,0)`,
  `ParentProcessName == "Unknown"`) are a designed best-effort outcome of
  ptr's ordering-gap handling and are excluded from `process_unresolved`
  v1 — candidate future check.
- **`ProcessPartial`** has no same-named payload property; the fitness check
  maps it to `Process`.
- **Registry CreateKey/DeleteKey/DeleteValue paths are ungated today** (no
  `StartsWith("registry")` filter at those emit sites) — relative fragments
  can egress; `path_unqualified` will count them. Fixing the sensor is
  sweep-feature scope.
- **Liveness vs. quiet hosts:** File/Registry/Tcp are effectively never
  silent for 5 s on a live Windows host; if a genuinely idle stream (e.g.
  UdpPacket on some hosts) turns out to flap in practice, tuning membership
  of the watched set is a config follow-up — v1 ships the Architect's six.
- **Skip seams** (`WINTAP_SKIP_ESPER_SEND` etc.): revised 2026-08-24 —
  because the normal-branch `Inspect` sits just above the `skipEsperSend`
  early return, messages in skip modes **are** inspected even though they
  never reach Esper. These are dev/test-only diagnostic modes (unset in
  production), and this placement is exactly what makes the shc-02
  integration tests possible without a live Esper runtime. Messages dropped
  earlier in `Send` (self-PID filter) are never inspected.
- **Enum growth:** arrays sized from the enum at construction; out-of-range
  values land in `_unknown` rather than throwing.
- **Shutdown:** `Stop()` performs a best-effort final flush; losing ≤ one
  window on hard kill is accepted.

## Error Handling

Checks never throw (contract; `Passes` returns `true` as the safe fallback
when a check cannot evaluate). The `Inspect` wrapper fail-opens: any
internal exception permanently disables the monitor for the session with a
single Warn line. Flush- and liveness-timer exceptions are caught and
logged without disabling inspection.

## Risks

- **Hot-path regression** at Registry/File volumes — mitigated by the
  constant-time design, the kill switch, and the wire-in unit's
  before/after events-per-second sanity check.
- **`process_unresolved` volume** — on hosts with real resolver gaps this
  counter may be large; it is aggregated (never per-failure) and that
  volume is precisely the signal the Architect asked for.
- **Liveness false alarms** around session restarts or ETW rundowns —
  bounded by the grace period, Stop() suppression, and transition-only
  logging (worst case one Error + one Info line per genuine gap).
- **MemoryMap bypass drift** — a future sensor could add another direct
  `SendEventBean`; the design note, the liveness watchdog (a stalled stream
  gets noticed), and the sweep feature are the guard.
- **Wintap.log-only visibility** — accepted deliberately ("start simple and
  extend if needed"); the aggregation core is reporting-agnostic, so a
  structured output could be added later without touching checks or hook.

## Alternatives Considered

- **Dedicated `SensorHealth` WintapMessage into the Parquet stream
  (DuckDB-queryable), first-draft design.** Rejected by Architect
  redirection 2026-08-24 (#1): too many moving parts for a supportive
  feature (schema addition, self-PID-filter bypass, sink flatten support,
  a third unit).
- **`eventtime_invalid` check (EventTime > 0 and ≤ now + 5 min skew).**
  Dropped from v1 by Architect review 2026-08-24 (#2) — not one of the
  requested conditions; "start simple and extend if needed." **Preserved
  here as the first candidate future check**; the registry makes it a
  drop-in.
- **Treating `"Unknown"` ProcessName as passing** (first-draft stance, on
  the theory it marks resolver fallback rather than sensor bugs). Reversed
  by the Architect: unresolved attribution is exactly the failure mode to
  catch; v1 counts it under its own check name.
- **Flagging the fabricated fallback PidHash directly.** Not possible — the
  fallback hash uses the real formula over (PID, EventTime) and is
  indistinguishable by value; `"Unknown"` ProcessName is the reliable
  marker, and the distinguishable `GenPidHash(-1, 0)` sentinel arm is kept
  as cheap defense.
- **Liveness via a per-message timestamp store** (record last-seen time per
  stream on the hot path). Rejected: the monotonic counter delta at tick
  time gives the same signal with zero additional hot-path work.
- **Liveness logging per silent interval.** Rejected — Architect requires
  low noise; transition-only logging with stall duration on recovery.
- **Piggybacking liveness on the flush timer at a 5 s tick** (flush every
  Nth tick). Considered; rejected for coupling — two independent boring
  timers are simpler than one timer with modular arithmetic, and the flush
  cadence stays independently configurable.
- **Hook at the top of `Send` (pre-enrichment, single site)** — rejected
  (false positives on legitimately unenriched events); **hook post-Esper in
  serializers** — rejected (misses NULL_PIDHASH drops, runs per-serializer);
  **Esper EPL aggregation** — rejected (failures die before the boundary;
  CEP load); **sampling / per-failure emission** — rejected by interview
  round 1 decisions.

## Open Questions

None. Amendment #2 made the v1 conditions definitive; adopted defaults
stand (MemoryMapSensor one-line Inspect in shc-02; parent-lineage and
eventtime checks deferred as future candidates via the registry).
