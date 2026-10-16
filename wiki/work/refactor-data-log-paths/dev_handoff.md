---
title: "Dev Handoff: Refactor File System Data and Log Paths"
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
audience: llm-agent
status: draft
source_paths: wiki/work/refactor-data-log-paths/dev_handoff.md
tags: [feature-work, packaging, data-pipeline, paths, shared-mount]
---

# Dev Handoff: Refactor File System Data and Log Paths

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

    Switch to code-development mode for the refactor-data-log-paths feature.

    Use these wiki files as the handoff context, in this order:

    - wiki/work/refactor-data-log-paths/brief.md
    - wiki/work/refactor-data-log-paths/design.md
    - wiki/work/refactor-data-log-paths/implementation_plan.md
    - wiki/work/refactor-data-log-paths/references.md
    - wiki/work/refactor-data-log-paths/dev_handoff.md (this file)

    Do NOT read wiki/work/refactor-data-log-paths/interview.md — its sealed
    section contains human estimates that must stay unseen until feature
    close-out (ai-velocity-roi-mini-lab v2.1 protocol).

    Goal: implement slices rdp-01 and rdp-02 first (two-root resolution core
    in ../wintap, then move all runtime-tree consumers), proving the split
    with unit tests and grep gates before touching packaging.

    Authorized write scope for this feature: ../wintap (code + tests),
    ../Lintap packaging + pidstat collector, ../Wintappy path defaults, and
    this repo's wiki/. Field-host clones (e.g. spk16) remain read-only per
    wiki/workflow/lintap-dev-field-workflow.md.

    Before editing code, read AGENTS.md and confirm that code-development
    mode is active for this task.

## Handoff Summary

Split the single configured root (`Env.FileDataRoot`) into two independently
rooted trees:

- **data** — shared, archivable event tables. The repurposed
  `WINTAP_DATA_ROOT` points at the directory *directly containing*
  `raw_sensor/` (no `parquet/` level anymore). This is the tree
  axon-aegis-micro-range VMs mount from shared storage and the S3 uploader
  ships from.
- **runtime** — everything host-specific: `Logs/`, `event_store/`, `csv/`,
  `recordings/`, `pidstat-spool/`, `diag/`, `ai/`, `workbench-state.json`.
  New knob `WINTAP_RUNTIME_ROOT` / JSON `RuntimeRoot`, same
  programmatic → env → JSON → per-OS-default precedence as the data root.

Unconfigured defaults: `<app-root>/data` + `<app-root>/runtime`, where
app-root is Linux `/var/lib/lintap`, Windows `%ProgramData%\Wintap`, macOS
`/Library/Application Support/Mactap`.

Hard constraints (human decisions — do not revisit silently):

1. **Frozen data-tree internals.** `raw_sensor/<event>/dayPK=/hourPK=/
   [protoPK=/]` layout, hostname+event+timestamp leaf naming, parquet schemas:
   untouched. Wintappy's input contract depends on it.
2. **No auto-migration.** Upgrades write to new locations; old trees
   (e.g. spk16's `/var/log/lintap`) are left in place. No move/symlink/merge
   logic anywhere, including maintainer scripts.
3. **No hostname logic in sensor code.** Cross-VM runtime visibility is a
   mount-time convention (`<shared>/hosts/<hostname>/`), documented, not
   implemented.
4. **Cross-platform.** Windows/macOS resolution changes land with the same
   commit series and are unit-tested, even though acceptance gates are
   Linux-only.

## Primary Sources For The Dev Agent

Resolution core:
- `../wintap/wintap/core/shared/Env.cs` — `FileDataRoot`, `ResolveDataRoot`,
  `SetDataRoot`; the generalization point for the second root.
- `../wintap/wintap/core/shared/ConfigManager.cs` — `ConfigRoot` properties,
  PascalCase↔`WINTAP_*` env mapping (gives `WINTAP_RUNTIME_ROOT` for free),
  `WINTAP_CONFIG_PATH`.
- `../wintap/wintap/core/etl/ETLConfig.json` — must stay platform-neutral:
  ship neither `DataRoot` nor `RuntimeRoot` values.
- `../wintap/tests/Wintap.Tests/RuntimeDataRootTests.cs` — seed tests.

Runtime-tree consumers to move (complete list from the design-time sweep):
- `../wintap/wintap/core/etl/shared/Paths.cs` — the one derivation point;
  `CsvDataPath`/`RecordingDataPath` → runtime; `ParquetDataPath` → data root.
- `../wintap/wintap/core/infrastructure/WintapLogger.cs` — `Logs/` (ComponentLogger ctor).
- `../wintap/wintap/core/infrastructure/ProcessResolver.cs` — `event_store/main.duckdb`.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` — `workbench-state.json` (two sites).
- `../wintap/wintap/core/api/EsperServiceController.cs` — `Logs/Wintap.log`, `Logs/WintapETL.log` tails.
- `../wintap/wintap/core/api/LLMController.cs` — `ai/api-key.txt`.
- `../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs` — hardcoded
  literal `/var/lib/lintap/diag` → runtime diag path (known defect, fix here).
- `../wintap/wintap/core/etl/load/CacheManager.cs` — startup logging of roots;
  upload sweep stays on the data tree.
- `../wintap/wintap/core/etl/load/adapters/base/Uploader.cs` —
  `getParquetRelativePathForFile` must keep yielding `raw_sensor/…` keys.

Packaging and collector (`../Lintap`, work from branch
`grantj/debian-package-refresh` state):
- `packaging/lintap-deb/{lintap.env,build-deb.sh,lintap.service,lintap-pidstat.service}`
  and the `lintap-rpm` mirrors — env knobs, directory creation/permissions,
  purge preservation, docs.
- `pidstat-collector.py` — spool default `<runtime-root>/pidstat-spool` via
  `WINTAP_RUNTIME_ROOT`; `parquet_root` default = data root (drop the
  `/parquet` suffix); keep `PIDSTAT_SPOOL_DIR`/`PIDSTAT_PARQUET_ROOT`
  overrides; update `tests/test_pidstat_collector.py`.

Downstream:
- `../Wintappy/Makefile` — `WINTAP_DBT_DATASET ?= $(WINTAP_DATA_ROOT)/parquet`
  → drop `/parquet`. DBT macros (`wintap_dbt/macros/paths.sql`) already funnel
  through `raw_sensor_dataset_path()`; nothing else should need changing, but
  re-verify with a repo-wide scan. Also re-scan Analytics
  `streamlit/`/notebooks (design-time scan found no couplings).

Micro-range (available in the implementation environment, not at design time):
- `../axon-aegis-micro-range` — confirm the shared-data mount layout and
  validate the design's assumptions before rdp-06; if its layout contradicts
  the design (e.g. expects a different mount point shape), stop and surface
  the conflict rather than adapting silently.

## Recommended First Implementation Slice

rdp-01 + rdp-02 as one reviewed unit (see
[[wiki/work/refactor-data-log-paths/implementation_plan]]):

1. Generalize root resolution in `Env.cs`; add `RuntimeRoot` to
   `ConfigManager`; extend `Paths.cs` to be the single derivation point for
   both trees.
2. Move every runtime consumer listed above; fix the NetworkSensor literal.
3. Gates before proceeding to packaging:
   - Full solution build, 0 errors; existing test suite green.
   - New resolution tests: both roots × Windows/macOS/Linux × precedence
     (programmatic > env > JSON > default), same-dir warning case.
   - Uploader key regression test (`raw_sensor/…` under new data root).
   - Grep gates: no `Env.FileDataRoot` outside `Env.cs`/`Paths.cs`; no literal
     `/var/lib/lintap` or `/var/log/lintap` in `wintap/` sources.

Then rdp-03 (packaging) → rdp-04 (downstream) → rdp-05/06/07 (the three
acceptance gates) → rdp-08 (closeout).

## Non-Goals For This Slice

- Anything inside finalized `raw_sensor/` (layout, naming, schemas).
- Migration/symlink logic of any kind.
- Hostname-aware paths in sensor code.
- S3/uploader protocol changes beyond the relative-key regression test.
- Hardening for unmounted/read-only/full shared mounts (document
  `RequiresMountsFor=` in the range pattern instead).
- RPM-builder parity work beyond the path split (the stale
  `file_ops_tracer.bpf.o` assertion from 2026-10-03 remains out of scope).

## Testing Expectations

- Per-slice gates as listed in the implementation plan; record every command
  and result in `verification.md` as you go, including failures.
- Acceptance gates (all three must pass to close):
  1. Linux package smoke — fresh install writes data/runtime to the new
     defaults; upgrade over an old `/var/log/lintap` env-file deployment:
     data follows the pointed root (now without the `parquet/` level — verify
     and record exactly what lands where), runtime relocates, old tree
     untouched.
  2. Shared-mount simulation — two instances, one shared data dir; no
     filename contention; mount contains only `raw_sensor/` plus whatever
     transients appear (record them verbatim — evidence for the open
     question); `hosts/<hostname>` runtime pattern demonstrated.
  3. Wintappy `make dbt-build` parity against relocated output.
- Windows: unit-level only (watch item recorded in the brief; no Windows
  smoke gate).

## Delegated Decisions (agent's discretion, record in verification.md)

- Names of new `Paths.cs` members and the exact shape of the generalized
  resolver.
- Runtime tree sub-layout details beyond the listed children (keep child
  names; `Logs/` casing stays).
- Whether packaging ships a systemd drop-in example (`RequiresMountsFor=`)
  for the range pattern or leaves it to range docs.
- deb-first vs rpm-first for the package smoke, depending on available hosts.

## Escalate To The Human (do not decide)

- Any need to touch `raw_sensor` internals or move finalized output outside
  `data/raw_sensor`.
- Any migration behavior beyond no-auto-migration.
- Conflicts between the design and the actual `axon-aegis-micro-range`
  layout.
- Keeping a `parquet/` level under the data root (rejected in design; only a
  human can un-reject it).

## Closeout Instructions

- Update wiki/work/refactor-data-log-paths/verification.md with commands run
  and results (including the upgrade-case evidence and shared-mount transient
  inventory).
- Update the wiki/work/refactor-data-log-paths/implementation_plan.md done
  checklist as slices complete.
- Append a concise entry to wiki/log.md for substantial progress.
- Draft the release-notes callout (knob semantic change + runtime relocation)
  and store it in the feature folder.
- At close-out: promote durable facts — new decision page superseding the
  layout half of [[wiki/decision/platform-runtime-data-root-defaults]];
  update [[wiki/component/sensor-upload-cache-pipeline]],
  [[wiki/repo/lintap-supporting-repo]], [[wiki/repo/wintappy-pipeline-repo]];
  create metrics.md (sealed estimates exist in interview.md — only now may
  the sealed section be read).
