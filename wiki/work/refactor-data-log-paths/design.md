---
title: "Design: Refactor File System Data and Log Paths"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/shared/Env.cs
  - ../wintap/wintap/core/shared/ConfigManager.cs
  - ../wintap/wintap/core/etl/shared/Paths.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
policy: agent-editable
last_validated: 2026-10-19
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/refactor-data-log-paths/design.md
tags: [feature-work, packaging, data-pipeline, paths, shared-mount]
---

# Feature Design: Refactor File System Data and Log Paths

## Summary

Split the single `Env.FileDataRoot` tree into two independently rooted trees:
a shared, archivable **data** tree holding exactly the event-table structure
(today's `parquet/` contents), and a host-only **runtime** tree holding
everything else. The data tree becomes directly mountable for multi-VM shared
storage (`axon-aegis-micro-range`) with no host-local state on the mount.

## Proposed Approach

### Root resolution (Env.cs)

Add a second root alongside the existing one, same resolution shape:

| Root | Programmatic | Env | JSON | Default (per OS) |
|---|---|---|---|---|
| Data | `Env.SetDataRoot` | `WINTAP_DATA_ROOT` | `DataRoot` | `<app-root>/data` |
| Runtime | `Env.SetRuntimeRoot` | `WINTAP_RUNTIME_ROOT` | `RuntimeRoot` | `<app-root>/runtime` |

`<app-root>` is the existing per-OS value: Linux `/var/log/lintap`, Windows
`%ProgramData%\Wintap`, macOS `/Library/Application Support/Mactap`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/Env.cs §ResolveDataRoot -->

`ResolveDataRoot` generalizes to a shared resolver taking the per-root
override/config/default triple. `ConfigManager` gains the `RuntimeRoot`
property; the existing PascalCase↔`WINTAP_*` mapping gives
`WINTAP_RUNTIME_ROOT` for free.
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ConfigManager.cs §env-override mapping -->

### Data tree = former parquet directory (no `parquet/` segment)

The repurposed `WINTAP_DATA_ROOT` points at the tree that *directly contains*
`raw_sensor/`:

```
<data-root>/                      ← shared-mountable; S3 uploader ships from here
  raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/[protoPK=…/]<host>+<event>+<ts>.parquet
```

Rationale: the interview renamed the tree from format-centric "parquet" to
"data"; keeping a `parquet/` intermediate directory would preserve the old name
inside the new one and add a pointless level to every mount and S3 prefix.
Internals below the root (`raw_sensor/…`, leaf naming, and finalized output
layout) remain frozen. Esper serializer and merge staging is explicitly
host-local under `<runtime-root>/esper_staging/`; it is not part of the shared
data tree. <!-- SYNTHESIS: inferred from the interview naming decision, ../Wintappy/Makefile WINTAP_DBT_DATASET default, and ../wintap/wintap/core/etl/shared/Paths.cs -->

Consequence: `Paths.ParquetDataPath` becomes the data root itself. The
uploader's `getParquetRelativePathForFile` already computes keys relative to
`Paths.ParquetDataPath` with a `raw_sensor` marker fallback, so S3 keys
(`raw_sensor/…`) are unchanged.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getParquetRelativePathForFile -->

### Runtime tree keeps existing child names

```
<runtime-root>/
  Logs/                 ← WintapLogger (Wintap.log, WintapETL.log, …)
  event_store/          ← ProcessResolver main.duckdb
  csv/                  ← Paths.CsvDataPath
  recordings/           ← Paths.RecordingDataPath (WintapRecorder)
  pidstat-spool/        ← pidstat collector spool
  diag/                 ← NetworkSensor BPF diag CSV
  ai/                   ← LLMController api-key.txt
  workbench-state.json  ← EventChannel
```

Keeping child names unchanged minimizes diff surface and keeps field muscle
memory (`Logs/Wintap.log`) intact; only the parent moves. All derivations go
through one place (extend `Paths.cs` with runtime-tree members) so future code
cannot silently re-mix trees.

### Packaging (../Lintap deb + rpm)

- `lintap.env`: set both knobs explicitly for clarity:
  `WINTAP_DATA_ROOT=/var/log/lintap/data`,
  `WINTAP_RUNTIME_ROOT=/var/log/lintap/runtime` (explicit-but-default keeps
  the operator discoverability the field relies on). Comment block explains
  the split and the shared-mount pattern.
- Build/maintainer scripts: create/chmod `/var/log/lintap/data` and
  `/var/log/lintap/runtime`; purge preserves both (data especially).
- pidstat collector: spool default moves to `<runtime-root>/pidstat-spool`
  (reads `WINTAP_RUNTIME_ROOT`, keeps `PIDSTAT_SPOOL_DIR` override);
  `parquet_root` default becomes the data root itself (drop the `/parquet`
  suffix), keeping `PIDSTAT_PARQUET_ROOT` override.
- Docs (BUILD_AND_TEST, README, LLM_RESTART) updated to the new layout.

### Downstream (../Wintappy, Analytics)

- `../Wintappy/Makefile`: `WINTAP_DBT_DATASET ?= $(WINTAP_DATA_ROOT)`.
  All DBT macros already resolve through
  `raw_sensor_dataset_path()`, so nothing else changes.
  <!-- GROUND_TRUTH: ../Wintappy/Makefile §WINTAP_DBT_DATASET -->
  <!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/macros/paths.sql §raw_sensor_dataset_path -->
- Analytics-side tooling: scan found no hardcoded `/var/log/lintap` or
  `<root>/parquet` couplings in `streamlit/`/notebooks at design time;
  dev agent re-verifies.

### Micro-range deployment pattern (docs only)

Each VM mounts the shared storage at its data root; leaf naming
(hostname+event+timestamp) makes concurrent writes contention-free. Optionally
each VM's runtime tree is additionally exposed on shared storage at
`<shared>/hosts/<hostname>/` (bind mount or export) for cross-VM log
scanning. Sensors always write plain local paths; no hostname logic in code.
To be validated against the actual `axon-aegis-micro-range` environment
(available in the implementation environment, not at design time).

## Data Model Or Schema Changes

None. `raw_sensor` internals, leaf naming, and parquet schemas are frozen.

## Interfaces And User Experience

- New env/JSON knobs: `WINTAP_RUNTIME_ROOT` / `RuntimeRoot`.
- **Semantic change:** `WINTAP_DATA_ROOT` means "the shared data tree,
  directly containing `raw_sensor/`". The packaged default is
  `/var/log/lintap/data`; runtime state defaults independently to
  `/var/log/lintap/runtime`. Release notes must state both effects.
- Startup logging (CacheManager startup configuration block) reports both
  resolved roots.

## Edge Cases

- Only `WINTAP_DATA_ROOT` set (typical field env file): data lands as pointed;
  runtime goes to platform default. Intended per interview.
- Both roots pointed at the same directory: legal, reproduces a mixed tree;
  log a startup warning.
- Data root on a not-yet-mounted share at service start: today's behavior is
  directory-create-on-demand; the service would write into the unmounted
  mountpoint. Document `RequiresMountsFor=` in the micro-range pattern rather
  than adding wait logic.
- Read-only or full shared mount: existing error paths apply; serializer
  retries/backlog behavior unchanged (out of scope to harden here).
- Esper serializer output, host/macip metadata, merge inputs, and `.active`
  files live under `<runtime-root>/esper_staging/` and are excluded from the
  shared data tree. Finalized output is materialized only under
  `<data-root>/raw_sensor/`.

## Error Handling

No new error model. Both trees are created on demand as today
(`Directory.CreateDirectory` at first use); packaging pre-creates them with
correct ownership/permissions.

## Risks

- Missed derivation site: some path that should move to runtime keeps deriving
  from the data root and pollutes shared mounts. Mitigation: single derivation
  point per tree in `Paths.cs` + a grep gate (no `Env.FileDataRoot` uses
  outside `Paths.cs`/`Env.cs`) + shared-mount simulation checks the mount
  contains only `raw_sensor/`.
- Upgrade surprise on field hosts: logs/duckdb silently relocate while data
  stays. Mitigation: release notes + packaging env file sets both knobs
  explicitly + no-auto-migration is the accepted decision.
- Windows regression: cross-platform change with Linux-gated acceptance.
  Mitigation: unit tests cover Windows resolution; Windows smoke is a recorded
  watch item before any Windows field build.
- S3 key drift: if `ParquetDataPath` handling regresses, uploaded keys change
  shape. Mitigation: unit test asserting `getParquetRelativePathForFile`
  yields `raw_sensor/…` keys for files under the new data root.

## Alternatives Considered

- One root with fixed `data/`/`runtime/` children — rejected in interview
  (mounting requires bind-mount tricks; trees can't live on different
  filesystems via config).
- New names for both knobs (retire `WINTAP_DATA_ROOT`) — rejected in
  interview; churn without a safety payoff.
- Legacy umbrella mode (old knob keeps old meaning when alone) — rejected in
  interview; perpetuates the mixed tree.
- Hostname subdirectory written by the sensor — rejected in interview;
  mount-time convention instead.
- Keeping a `parquet/` directory under the data root — rejected here: empty
  indirection contradicting the rename decision; makes every mount/S3 prefix
  one level deeper than needed. (Dev agent: if field constraints surface that
  favor keeping it, this is a human decision, not a silent revert.)

## Open Questions

- `merged/`/`.active` transient files on shared mounts: acceptable clutter
  this feature; relocation is a frozen-internals exception needing human
  sign-off. Re-evaluate with micro-range evidence.
- Whether packaging should also provide a drop-in systemd
  `RequiresMountsFor=` example for the micro-range pattern or leave it purely
  to range docs.
- Runtime log directory casing (`Logs/`) kept as-is; revisit only if the
  micro-range grep workflow wants lowercase uniformity (would break field
  muscle memory — default is keep).
