---
title: "Interview: Refactor File System Data and Log Paths"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/Env.cs
  - ../wintap/wintap/core/etl/shared/Paths.cs
policy: agent-editable
last_validated: 2026-10-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/refactor-data-log-paths/interview.md
tags: [feature-work, packaging, data-pipeline, paths, shared-mount]
---

# Feature Interview: Refactor File System Data and Log Paths

## Initial Idea

"Refactor file system data and log paths used by Wintap/Lintap."

## Context Established Before Questioning

- [[wiki/decision/platform-runtime-data-root-defaults]] (2026-08-19): `Env.cs`
  owns platform data-root defaults (Windows `%ProgramData%\Wintap`, macOS
  `/Library/Application Support/Mactap`, Linux `/var/lib/lintap`), with
  programmatic → `WINTAP_DATA_ROOT` → JSON `DataRoot` precedence.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/shared/Env.cs §ResolveDataRoot -->
- Everything today nests under one root: `Logs/`, `csv/`, `parquet/`,
  `recordings/`, `event_store/main.duckdb`, `workbench-state.json`, `ai/`.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/shared/Paths.cs -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/WintapLogger.cs §ComponentLogger ctor -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §MAIN_DB_PATH -->
- One stray hardcoded path bypasses the root entirely: BPF diag counters CSV at
  literal `/var/lib/lintap/diag`.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §diag CSV writer -->
- Field packaging (Lintap branch `grantj/debian-package-refresh`, deb + rpm)
  sets `WINTAP_DATA_ROOT=/var/log/lintap` in `/etc/lintap/lintap.env`, so
  deployed hosts put *everything* (data + logs + duckdb + spool) under
  `/var/log/lintap`.
  <!-- GROUND_TRUTH: ../Lintap packaging/lintap-deb/lintap.env (branch grantj/debian-package-refresh) -->
- The pidstat collector reads the same `WINTAP_DATA_ROOT` and spools under
  `<data_root>/pidstat-spool`.
  <!-- GROUND_TRUTH: ../Lintap pidstat-collector.py §load config (branch grantj/debian-package-refresh) -->
- The S3/upload path selects files only from the parquet tree
  (`Paths.ParquetDataPath`, `raw_sensor` marker fallback).
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getParquetRelativePathForFile -->

## Interview Log

### Round 1

**Q:** Desired end-state layout for Linux data and log paths? (offered: FHS
split; standardize on /var/log/lintap; configurable split with defaults
unchanged)
**A:** More involved than any option. The `parquet` directory is the long-term
archivable structure: event types as top-level tables, time partitions, leaf
files named hostname + event type + timestamp — intentionally contention-free
when multiple sensors write one shared path (shared mount, S3, other), and the
semantic filename components help humans cherry-pick files. The rest of the
directories are host-specific and shouldn't be written to a shared path. The
driving use case is `../axon-aegis-micro-range`: multiple VMs on one system
sharing a `data` dir for long-term data (S3 deployments don't have this problem
because the uploader only ships from the parquet dir). Split the tree so cases
like the micro-range can mount just the parquet portion. Not sold on top-level
directory names — open to suggestions. Also: optionally mount the "host only"
directories from multiple VMs for easier log scanning/grep — maybe the mount
adds a hostname layer for host-only paths while merging the parquet paths. Not
critical.
**Outcome:** decision — split shared/archivable tree from host-only tree;
mountable-data-dir is the driving requirement.

**Q:** Which repos is this refactor authorized to change?
**A:** `../wintap` code, `../Lintap` packaging, and `../Wintappy`/Analytics.
**Outcome:** constraint — cross-repo write authorization recorded.

**Q:** Windows scope?
**A:** Cross-platform.
**Outcome:** decision — Windows/macOS layout changes too; partially supersedes
[[wiki/decision/platform-runtime-data-root-defaults]] (layout, not precedence).

**Q:** Migration for existing field deployments (e.g. spk16 with data under
/var/log/lintap)?
**A:** No auto-migration (recommended option accepted).
**Outcome:** decision — upgrades write to new locations; old data left in
place, matching the wpc-09 precedent.

### Round 2

**Q:** Root model — two independent roots vs one root with fixed subtrees?
**A:** Two independent roots.
**Outcome:** decision — separate config knobs for the shared data tree and the
host-only runtime tree; each defaults per-OS.

**Q:** Naming direction for the two trees?
**A:** `data` + `runtime`.
**Outcome:** decision — "data" = archivable event tables (drops format-centric
"parquet" as the top-level name); "runtime" = host-specific state.

### Round 3

**Q:** Hostname layer for host-only dirs (grep logs across range VMs)?
**A:** Mount-time convention.
**Outcome:** decision — sensors always write plain local paths; the range's
mount/compose setup maps each VM's runtime tree to `<shared>/hosts/<hostname>/`;
documented as a deployment pattern, zero sensor code.

**Q:** Is the internal structure of the shared tree frozen?
(`raw_sensor/<event>/dayPK=/hourPK=/` + hostname+event+timestamp leaves —
Wintappy's input contract.)
**A:** Frozen — constraint.
**Outcome:** constraint — only the location of the tree moves; internals and
leaf naming untouched.

### Round 4

**Q:** What happens to the `WINTAP_DATA_ROOT` knob (today "parent of
everything"; field env files set it to /var/log/lintap)?
**A:** Repurpose cleanly.
**Outcome:** decision — `WINTAP_DATA_ROOT` now means the shared data tree; new
`WINTAP_RUNTIME_ROOT` for host-only state; existing env files keep landing data
where pointed but logs/duckdb move to the runtime default unless also set;
release-notes callout required.

**Q:** Default locations per platform when unconfigured?
**A:** FHS-style split under one app root: Linux `/var/lib/lintap/data` +
`/var/lib/lintap/runtime`; Windows `%ProgramData%\Wintap\data` + `\runtime`;
macOS `/Library/Application Support/Mactap/{data,runtime}`.
**Outcome:** decision.

**Q:** Closing evidence? (multi-select)
**A:** Linux package smoke; shared-mount simulation; Wintappy pipeline run.
Windows smoke not selected.
**Outcome:** decision — three acceptance gates; Windows validation depth noted
as a watch item.

## Decisions

1. Split the on-disk tree into a shared/archivable **data** tree and a
   host-only **runtime** tree, each with its own independently configurable
   root.
2. Names: `data` and `runtime`.
3. `WINTAP_DATA_ROOT` repurposed to mean the data tree; new
   `WINTAP_RUNTIME_ROOT` added; same programmatic → env → JSON precedence model.
4. Unconfigured defaults: sibling `data`/`runtime` dirs under the existing
   per-OS app root (`/var/lib/lintap`, `%ProgramData%\Wintap`,
   `/Library/Application Support/Mactap`).
5. Cross-platform scope (Windows and macOS layouts change too).
6. Hostname layer for host-only dirs is a mount-time deployment convention
   (`<shared>/hosts/<hostname>/`), not sensor code.
7. No auto-migration for existing deployments.

## Constraints

- Parquet-internal contract frozen: `raw_sensor/<event>/dayPK=/hourPK=/`
  layout and hostname+event+timestamp leaf naming unchanged (Wintappy input
  contract).
- Authorized repos: `../wintap` code, `../Lintap` packaging,
  `../Wintappy`/Analytics where downstream paths must track.
- Existing recorded datasets and field hosts (e.g. spk16) keep their current
  trees; manual handling only.

## Delegations

- Exact placement of each host-only item under the runtime tree (Logs,
  event_store, csv, recordings, pidstat-spool, diag, workbench-state.json, ai)
  is left to design.
- Whether `merged/` staging and `.active` files need relocation within this
  feature is left to design within the frozen-internals constraint (see
  Deferred).

## Deferred / Open Questions

- Transient items currently living *inside* the parquet tree (`merged/`
  staging, per-sensor staging dirs, `.active` files) are arguably host-local
  cache polluting a shared mount; internals are frozen this feature, so any
  relocation is a follow-up unless design shows it is required for safe
  shared-mount operation.
- Windows validation depth: the change is cross-platform but acceptance gates
  are Linux-focused; a Windows smoke is a watch item, not a gate.

## Playback Summary

Confirmed by the human 2026-10-15: split the single mixed root into a shared
archivable `data` tree (the parquet event tables, mountable by
`axon-aegis-micro-range` VMs and shipped by S3) and a host-only `runtime` tree
(logs, duckdb, spool, state); two independent roots with
`WINTAP_DATA_ROOT`/`WINTAP_RUNTIME_ROOT` knobs; FHS-style sibling defaults
under the per-OS app root; mount-time `hosts/<hostname>` convention for
cross-VM runtime visibility; frozen parquet internals; no auto-migration;
cross-platform code scope with Linux-gated acceptance (package smoke,
shared-mount simulation, Wintappy DBT run).

## Sealed — human estimates

SEALED: any agent that will produce its own estimates (e.g. the Wintap
Engineer at exploration start) must not read this section until feature
close-out. See [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1) and
[[wiki/concept/velocity-metric]].

(Answered 2026-10-15, shortly after interview close rather than at it — the
human returned to supply the estimates before any implementation estimate
existed.)

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available?**
**A:** "I think it would take a human 1 week." (No separate calendar
availability date given; 1 week is the stated answer, verbatim.)

**Q: With the AI workflow, on what date do you predict this feature will be
available?**
**A:** "With AI assistance, 1 day." (Given as a duration, not a calendar date,
verbatim.)
