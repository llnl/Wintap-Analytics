---
title: "Brief: Refactor File System Data and Log Paths"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/Env.cs
  - ../wintap/wintap/core/shared/ConfigManager.cs
  - ../wintap/wintap/core/etl/shared/Paths.cs
policy: agent-editable
last_validated: 2026-10-19
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/refactor-data-log-paths/brief.md
tags: [feature-work, packaging, data-pipeline, paths, shared-mount, axon-aegis-micro-range]
---

# Feature Brief: Refactor File System Data and Log Paths

## Problem

Wintap/Lintap nests two fundamentally different kinds of on-disk content under
one configured root (`Env.FileDataRoot`):

- The **archivable event-table tree** (`parquet/raw_sensor/<event>/dayPK=/hourPK=/`
  with hostname+event+timestamp leaf names) — intentionally contention-free
  when many sensors write one shared location (shared mount, S3), and
  human-navigable for cherry-picking files.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/shared/Paths.cs -->
- **Host-specific runtime state** — `Logs/`, `event_store/main.duckdb`, `csv/`,
  `recordings/`, `workbench-state.json`, `ai/`, pidstat spool, and a stray
  hardcoded `/var/log/lintap/runtime/diag` CSV — none of which should land on a shared
  path.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapLogger.cs §ComponentLogger ctor -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §MAIN_DB_PATH -->
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §diag CSV writer -->

The `axon-aegis-micro-range` deployment has multiple VMs on one system sharing
a `data` directory for long-term telemetry. Today there is no clean way to
mount just the shared-safe portion: pointing `WINTAP_DATA_ROOT` at the shared
mount would drag every host's logs, DuckDB store, and spool onto it. S3
deployments dodge this only because the uploader selects files exclusively
from the parquet tree.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getParquetRelativePathForFile -->

## Goals

1. Split the on-disk layout into two independently rooted trees:
   - **data** — the shared, archivable event tables (today's `parquet/`
     contents).
   - **runtime** — all host-specific state (logs, duckdb event store, csv,
     recordings, spool, diag, workbench state, ai).
2. Two independent config knobs with the existing precedence model
   (programmatic → environment → JSON): `WINTAP_DATA_ROOT` (repurposed: now
   the data tree) and new `WINTAP_RUNTIME_ROOT`.
3. Unconfigured defaults: sibling dirs under the per-OS app root —
   Linux `/var/log/lintap/data` + `/var/log/lintap/runtime`;
   Windows `%ProgramData%\Wintap\data` + `%ProgramData%\Wintap\runtime`;
   macOS `/Library/Application Support/Mactap/{data,runtime}`.
4. Update `../Lintap` packaging (deb + rpm: env files, directory creation,
   maintainer scripts, docs) and the pidstat collector's spool placement to the
   split model.
5. Document the micro-range deployment pattern: VMs mount one shared data dir
   (merged writes, contention-free by leaf naming) and optionally expose their
   runtime trees as `<shared>/hosts/<hostname>/` — a mount-time convention,
   never sensor code.
6. Track the change in `../Wintappy`/Analytics wherever input paths are
   hardcoded to the old layout.

## Non-Goals

- No change to the internal structure of the data tree:
  `raw_sensor/<event>/dayPK=/hourPK=/` layout and hostname+event+timestamp
  leaf naming are frozen (Wintappy input contract).
- No automatic migration of existing deployments; old trees (e.g. spk16's
  `/var/log/lintap`) stay in place for manual handling (wpc-09 precedent, see
  [[wiki/decision/platform-runtime-data-root-defaults]]).
- No hostname-aware path logic inside the sensor.
- No relocation of `merged/` staging or `.active` files beyond what safe
  shared-mount operation strictly requires (open question; internals frozen).
- No S3/uploader protocol changes.

## User-Facing Behavior

- Fresh installs write event tables under `<data-root>` and everything else
  under `<runtime-root>`; both knobs independently overridable.
- Existing env files that set only `WINTAP_DATA_ROOT` keep landing event data
  where pointed; logs/duckdb/spool move to the runtime default unless
  `WINTAP_RUNTIME_ROOT` is also set. Release notes must call this out.
- Micro-range operators mount the shared dir at each VM's data root and get a
  merged, contention-free event-table tree; optionally mount runtime trees as
  `hosts/<hostname>/` for cross-VM log scanning.

## Acceptance Criteria

1. **Linux package smoke** — fresh RPM/deb install starts, writes event tables
   under the data root and logs/duckdb/spool under the runtime root; upgrade
   over an existing `/var/log/lintap` deployment behaves per no-auto-migration.
2. **Shared-mount simulation** — two sensor instances writing one shared data
   dir with no filename contention; host-only dirs stay local; the
   `hosts/<hostname>` runtime mount pattern demonstrated.
3. **Wintappy pipeline run** — DBT bronze/silver/gold runs unchanged against
   the relocated `raw_sensor` tree (proves the frozen contract held).

## Affected Areas

- `../wintap`: `Env.cs` (root resolution), `ConfigManager.cs` (new knob),
  `core/etl/shared/Paths.cs` (derived paths), `WintapLogger.cs`,
  `ProcessResolver.cs` (duckdb path), `EventChannel.cs` (workbench state),
  `EsperServiceController.cs`/`LLMController.cs` (log/ai paths),
  `NetworkSensor.cs` (hardcoded diag path), `CacheManager.cs`/`Uploader.cs`
  (parquet-root derivation), tests.
- `../Lintap`: `packaging/lintap-deb` and `packaging/lintap-rpm` (lintap.env,
  build scripts' directory creation/permissions, maintainer scripts, docs),
  `pidstat-collector.py` spool default.
- `../Wintappy` / Wintap-Analytics: any hardcoded `/var/log/lintap` or
  `<root>/parquet` input paths in pipelines, notebooks, Streamlit tooling.
- Wiki: partially supersedes [[wiki/decision/platform-runtime-data-root-defaults]]
  (single-root layout changes; resolution precedence survives) — new decision
  page at close-out.

## References

See [[wiki/work/refactor-data-log-paths/interview]] for grounded context and
the full Q&A record. Key prior pages:
[[wiki/decision/platform-runtime-data-root-defaults]],
[[wiki/component/sensor-upload-cache-pipeline]],
[[wiki/repo/wintappy-pipeline-repo]],
[[wiki/workflow/lintap-dev-field-workflow]].

## Open Questions

- Do `merged/` staging and `.active` files inside the data tree break
  shared-mount safety in practice, or does the leaf-naming convention cover
  them? If they must move, that is a frozen-internals exception requiring
  explicit human sign-off.
- Windows validation depth: cross-platform code change with Linux-gated
  acceptance; is a Windows smoke required before field deployment of any
  Windows build cut from the refactored code?
- Exact runtime-tree sub-layout (flat vs grouped) — design decision.

## Test Plan

- Unit: `ResolveDataRoot`-style resolution tests extended to both roots and
  all three platforms (existing `RuntimeDataRootTests.cs` as the seed).
- Integration: Linux package install/upgrade smoke (deb and rpm), per
  acceptance criterion 1.
- Shared-mount: two instances against one data dir (VMs or containers), per
  acceptance criterion 2.
- Pipeline: Wintappy `make dbt-build` against relocated output, per
  acceptance criterion 3.

## Done When

All three acceptance criteria pass with evidence recorded in
`verification.md`; packaging and docs updated in `../Lintap`; downstream path
references updated; release-notes callout for the `WINTAP_DATA_ROOT` semantic
change written; durable facts promoted (new/updated decision page superseding
the single-root layout) and `wiki/log.md` updated.
