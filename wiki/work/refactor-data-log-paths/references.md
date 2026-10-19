---
title: "References: Refactor File System Data and Log Paths"
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
audience: llm-agent
status: draft
source_paths: wiki/work/refactor-data-log-paths/references.md
tags: [feature-work, packaging, data-pipeline, paths]
---

# Feature References: Refactor File System Data and Log Paths

## Live Repo Sources

### Root resolution and config (`../wintap`)

- `../wintap/wintap/core/shared/Env.cs` — `FileDataRoot`, `ResolveDataRoot`
  (programmatic override → configured value → per-OS default: Windows
  `%ProgramData%\Wintap`, macOS `/Library/Application Support/Mactap`, Linux
  `/var/log/lintap`), `SetDataRoot`, `AppName`. The single point every path
  below derives from; the refactor adds a second root here.
- `../wintap/wintap/core/shared/ConfigManager.cs` — `WINTAP_CONFIG_PATH`,
  env-override mapping (`DataRoot` ↔ `WINTAP_DATA_ROOT` via the
  PascalCase↔`WINTAP_*` name mapping), `ConfigRoot.DataRoot`. New
  `RuntimeRoot` property and `WINTAP_RUNTIME_ROOT` mapping land here.
- `../wintap/wintap/core/etl/ETLConfig.json` — shipped config; deliberately
  carries no `DataRoot` (platform-neutral, per
  [[wiki/decision/platform-runtime-data-root-defaults]]).
- `../wintap/tests/Wintap.Tests/RuntimeDataRootTests.cs` — existing resolution
  tests; seed for two-root tests.

### Derived paths — data tree (`../wintap`)

- `../wintap/wintap/core/etl/shared/Paths.cs` — `CsvDataPath`,
  `ParquetDataPath`, `RecordingDataPath`, all `Path.Combine(Env.FileDataRoot, …)`.
  Central derivation point; csv/recordings are host-only and move to runtime.
- `../wintap/wintap/core/etl/load/RawSensorWriter.cs` — materializes into
  `<ParquetDataPath>/raw_sensor/…` (frozen internals).
- `../wintap/wintap/core/etl/load/CacheManager.cs` — upload sweep over
  `<cache>/raw_sensor`, empty-partition cleanup, startup logging of the roots;
  treats `merged/` and `csv/` as special directory names.
- `../wintap/wintap/core/etl/load/adapters/base/Uploader.cs` —
  `getParquetRelativePathForFile` derives S3 keys relative to
  `Paths.ParquetDataPath` with a `raw_sensor` marker fallback. Must keep
  producing identical keys after the move.
- `../wintap/wintap/core/etl/load/ParquetWriter.cs` — leaf-file naming
  (`<path>-<timestamp>.parquet.active`, per-sensor dirs). Frozen; relevant to
  the shared-mount contention argument and the `.active` open question.
- `../wintap/wintap/core/etl/load/Merge.cs` — operates over a parquet search
  root; `merged/` naming.

### Derived paths — runtime tree (`../wintap`)

- `../wintap/wintap/core/infrastructure/WintapLogger.cs` — logs at
  `<FileDataRoot>/Logs/<name>.log` (ComponentLogger ctor).
- `../wintap/wintap/core/infrastructure/ProcessResolver.cs` — DuckDB store at
  `<FileDataRoot>/event_store/main.duckdb`.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` —
  `<FileDataRoot>/workbench-state.json` (two sites).
- `../wintap/wintap/core/api/EsperServiceController.cs` — reads
  `<FileDataRoot>/Logs/Wintap.log` and `Logs/WintapETL.log` tails.
- `../wintap/wintap/core/api/LLMController.cs` —
  `<FileDataRoot>/ai/api-key.txt`.
- `../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs` — hardcoded
  literal `/var/log/lintap/runtime/diag/diag_counters.csv`, bypassing the configured
  root entirely. Known defect to fold into the refactor.

### Packaging and collector (`../Lintap`, branch `grantj/debian-package-refresh`)

- `packaging/lintap-deb/lintap.env` and `packaging/lintap-rpm/lintap.env` —
  `WINTAP_DATA_ROOT=/var/log/lintap/data` plus `WINTAP_RUNTIME_ROOT` and `PIDSTAT_*` knobs; the field
  convention this feature's knob-repurposing must handle.
- `packaging/lintap-deb/build-deb.sh` — creates/chmods
  `/var/log/lintap/{data,runtime}`; preserves data on purge. RPM builder
  mirrors the layout.
- `packaging/lintap-deb/lintap.service`, `lintap-pidstat.service` —
  `EnvironmentFile=-/etc/lintap/lintap.env`.
- `pidstat-collector.py` — reads `WINTAP_DATA_ROOT` (fallback
  `~/data/lintap/lintap-dev`), spools at `<data_root>/pidstat-spool`,
  `PIDSTAT_SPOOL_DIR` override. Spool is host-only → runtime tree.
- `packaging/PACKAGING_REVIEW.md` — prior hardening review;
  `ReadWritePaths=/var/log/lintap /etc/lintap` suggestion will need the
  two-root treatment.

### Downstream consumers (`../Wintappy`, this repo)

- `../Wintappy` — raw_sensor input contract (frozen); check for hardcoded
  absolute input roots in DBT profiles/scripts/notebooks.
- Wintap-Analytics Streamlit/notebook tooling — check for hardcoded
  `/var/log/lintap` or `<root>/parquet` references.
- (To be enumerated precisely during design; this is the authorized
  "track the change" scope, not a rewrite.)

## External Sources

- `../axon-aegis-micro-range` — the driving deployment (multiple VMs sharing a
  `data` dir). Not present as a local clone at interview time
  (2026-10-15); mount layout details to be confirmed when available.
  <!-- SPECULATIVE: axon-aegis-micro-range layout — repo not yet available locally -->

## Related Wiki Pages

- [[wiki/work/refactor-data-log-paths/interview]] — decisions/constraints record
- [[wiki/work/refactor-data-log-paths/brief]] — the distilled brief
- [[wiki/decision/platform-runtime-data-root-defaults]] — partially superseded
  at close-out (layout changes; resolution precedence survives)
- [[wiki/component/sensor-upload-cache-pipeline]] — upload/merge cycle over the
  parquet tree
- [[wiki/component/fileops-event-pipeline]] — serializer parquet output
- [[wiki/repo/wintappy-pipeline-repo]] — raw_sensor input contract owner
- [[wiki/repo/lintap-supporting-repo]] — packaging contract (deb/rpm)
- [[wiki/workflow/lintap-dev-field-workflow]] — field-host constraints for any
  spk16 verification

## Libraries And APIs

- .NET `Environment.SpecialFolder.CommonApplicationData`, `Path.Combine` —
  existing per-OS root mechanics.
- systemd `EnvironmentFile`, mount/bind-mount conventions for the
  `hosts/<hostname>` runtime pattern.

## Notes

- The pidstat collector's env naming (`WINTAP_DATA_ROOT` for a spool location)
  becomes misleading post-split: spool is runtime, so the collector should
  follow `WINTAP_RUNTIME_ROOT`. Flag in design.
- Everything host-only currently derives from `Env.FileDataRoot` through five
  separate call sites plus one hardcoded literal — the refactor should leave a
  single derivation point per tree (e.g. extend `Paths.cs`) so future paths
  can't silently re-mix the trees.
