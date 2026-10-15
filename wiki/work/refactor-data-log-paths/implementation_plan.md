---
title: "Implementation Plan: Refactor File System Data and Log Paths"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/shared/Env.cs
  - ../wintap/wintap/core/etl/shared/Paths.cs
policy: agent-editable
last_validated: 2026-10-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/refactor-data-log-paths/implementation_plan.md
tags: [feature-work, packaging, data-pipeline, paths]
---

# Implementation Plan: Refactor File System Data and Log Paths

## Scope

See [[wiki/work/refactor-data-log-paths/brief]]. Slices are ordered so the
code split lands and is unit-proven before packaging and downstream tracking,
with validation gates last. Slice IDs: `rdp-NN`.

## Steps

### rdp-01 — Two-root resolution core (../wintap)

- Generalize `Env.ResolveDataRoot` to resolve both roots
  (override/config/env/default per root); add `Env.FileRuntimeRoot`,
  `Env.SetRuntimeRoot`.
- Add `RuntimeRoot` to `ConfigRoot` in `ConfigManager.cs` (env mapping
  `WINTAP_RUNTIME_ROOT` follows from the existing name mapping).
- Defaults: `<app-root>/data` and `<app-root>/runtime` per design.
- Extend `Paths.cs`: `ParquetDataPath` → data root itself; add runtime-tree
  members (`LogDataPath`, `EventStorePath`, `CsvDataPath`, `RecordingDataPath`,
  `DiagDataPath`, `AiDataPath`, `WorkbenchStatePath`) — names at dev agent's
  discretion, one derivation point per tree is the requirement.
- Unit tests: extend `RuntimeDataRootTests.cs` to both roots × three
  platforms × precedence order; same-directory warning case.

### rdp-02 — Move all runtime-tree consumers (../wintap)

- `WintapLogger.cs` (Logs), `ProcessResolver.cs` (event_store),
  `EventChannel.cs` (workbench-state.json ×2), `EsperServiceController.cs`
  (log tails), `LLMController.cs` (ai/), `NetworkSensor.cs` (replace hardcoded
  `/var/lib/lintap/diag` with the runtime diag path).
- Grep gate: no `Env.FileDataRoot` reference outside `Env.cs`/`Paths.cs`; no
  literal `/var/lib/lintap` or `/var/log/lintap` in `wintap/` sources.
- Startup configuration logging reports both resolved roots.
- Unit test: uploader `getParquetRelativePathForFile` still yields
  `raw_sensor/…` keys under the new data root.

### rdp-03 — Packaging split (../Lintap deb + rpm)

- `lintap.env` (both packagings): set both knobs explicitly to the new
  defaults; comment block explaining the split and shared-mount use.
- `build-deb.sh` / `build-rpm.sh` + maintainer scripts: create/chmod
  `/var/lib/lintap/data` and `/var/lib/lintap/runtime`; purge behavior
  preserves data tree; drop `/var/log/lintap` creation.
- pidstat collector: spool default `<runtime-root>/pidstat-spool` via
  `WINTAP_RUNTIME_ROOT`; `parquet_root` default = data root (drop `/parquet`
  suffix); overrides retained; pytest updated.
- Docs: BUILD_AND_TEST.md, README.md, LLM_RESTART.md path tables.

### rdp-04 — Downstream tracking (../Wintappy, Analytics)

- `../Wintappy/Makefile`: `WINTAP_DBT_DATASET ?= $(WINTAP_DATA_ROOT)` (drop
  `/parquet`).
- Re-verify no other hardcoded old-layout inputs in Wintappy and
  Analytics `streamlit/`/notebooks; fix what the scan finds.

### rdp-05 — Linux package smoke (acceptance gate 1)

- Fresh deb (and rpm if an el8 host is available) install: service starts,
  event tables under `/var/lib/lintap/data/raw_sensor/…`, logs/duckdb/spool
  under `/var/lib/lintap/runtime/…`.
- Upgrade over a deployment with the old `/var/log/lintap` env file: data
  continues to the pointed root (now sans `parquet/` level — release-note
  check), runtime relocates, old tree untouched.

### rdp-06 — Shared-mount simulation (acceptance gate 2)

- Two sensor instances (micro-range VMs preferred, containers acceptable)
  sharing one data dir: no filename contention, mount contains only
  `raw_sensor/` (plus known transient `merged/`/`.active` — record what
  appears), host dirs stay local.
- Demonstrate `hosts/<hostname>` runtime mount pattern; document in the range
  context.

### rdp-07 — Wintappy pipeline run (acceptance gate 3)

- `make dbt-build` against relocated output; expect parity with the
  pre-refactor run (PASS counts match).

### rdp-08 — Closeout

- Release-notes callout drafted (knob semantic change + runtime relocation).
- Promote durable facts: new decision page superseding the layout half of
  [[wiki/decision/platform-runtime-data-root-defaults]]; update
  [[wiki/component/sensor-upload-cache-pipeline]],
  [[wiki/repo/lintap-supporting-repo]], [[wiki/repo/wintappy-pipeline-repo]].
- verification.md finalized; log.md entry; metrics.md (sealed estimates exist).

## Files Likely To Change

- `../wintap/wintap/core/shared/{Env,ConfigManager}.cs`
- `../wintap/wintap/core/etl/shared/Paths.cs`
- `../wintap/wintap/core/infrastructure/{WintapLogger,ProcessResolver,EventChannel}.cs`
- `../wintap/wintap/core/api/{EsperServiceController,LLMController}.cs`
- `../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs`
- `../wintap/wintap/core/etl/load/CacheManager.cs` (startup logging)
- `../wintap/tests/Wintap.Tests/RuntimeDataRootTests.cs` (+ new tests)
- `../Lintap/packaging/lintap-{deb,rpm}/{lintap.env,build-*.sh,*.service,docs}`
- `../Lintap/pidstat-collector.py`, `../Lintap/tests/test_pidstat_collector.py`
- `../Wintappy/Makefile`

## Tests To Add Or Update

- Two-root resolution unit tests (platforms × precedence × same-dir warning).
- Uploader relative-key regression test.
- pidstat collector pytest for new spool/parquet defaults + overrides.
- Grep gates (rdp-02) runnable as a script or CI check.

## Migration Or Compatibility Notes

- No auto-migration (decision). Old trees left in place.
- `WINTAP_DATA_ROOT` semantic narrowing: release-notes callout mandatory;
  packaging env files set both knobs explicitly so packaged hosts are
  unambiguous.
- Wintappy: hosts running old sensor + new Wintappy (or vice versa) must set
  `WINTAP_DBT_DATASET` explicitly to bridge; note in Wintappy README.

## Rollback Plan

- Code: revert the wintap/Lintap/Wintappy commits; no data transformation
  occurs, so rollback is source-only.
- A rolled-back sensor resumes writing to old locations; any data written to
  new locations during the window stays there (same manual-handling posture as
  no-auto-migration).

## Done Checklist

- [ ] rdp-01 two-root core + unit tests
- [ ] rdp-02 runtime consumers moved + grep gates + uploader key test
- [ ] rdp-03 packaging split (deb + rpm) + pidstat + docs
- [ ] rdp-04 Wintappy/Analytics tracking
- [ ] rdp-05 Linux package smoke (gate 1)
- [ ] rdp-06 shared-mount simulation (gate 2)
- [ ] rdp-07 Wintappy DBT run (gate 3)
- [ ] rdp-08 closeout: release notes, promotion, verification, metrics
