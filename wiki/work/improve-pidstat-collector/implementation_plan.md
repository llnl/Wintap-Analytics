---
title: "Implementation Plan: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-pidstat-collector/brief.md
  - wiki/work/improve-pidstat-collector/design.md
policy: agent-editable
last_validated: 2026-08-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-pidstat-collector/implementation_plan.md
tags: [feature-work, implementation, lintap, pidstat]
---

# Implementation Plan: Improve pidstat Collector

## Scope

New collector script in `../Lintap` plus systemd packaging, and a coordinated
Wintappy DBT change from tab-CSV to parquet. No `../wintap` code changes
(verify-only). Writing to `../Lintap` and `../Wintappy` requires explicit
authorization for sibling-repo changes per `AGENTS.md`.

## Steps

1. **Verify the ride-along on Linux** (read-only): confirm the Linux service
   build runs `CacheManager`'s upload loop with an S3 (or other) adapter
   enabled, and note the deployed `UploadIntervalSec`. Record findings here
   and resolve the matching design open question.
2. **Collector script** (`../Lintap`, name suggestion:
   `pidstat-collector.sh`): sampling loop at configurable interval (default
   5 s), spool file outside `raw_sensor/`, rotation aligned to wall-clock
   windows of the merge-cycle length.
3. **Parquet conversion**: DuckDB CLI step applying the `stg_pidstat_metrics`
   casts plus a `hostname` column; atomic rename into
   `raw_sensor/pidstat/dayPK=…/hourPK=…/`.
4. **Crash handling + accumulation guard**: startup salvage of leftover spool;
   configurable max-bytes/max-age cap on unshipped parquet, oldest-first.
5. **systemd unit** in `../Lintap/packaging/` (`Restart=always`), plus README
   notes; keep `pidstat-collect.sh` untouched as the simple example.
   *(Slice 2.)*
6. **Rewrite the collector in Python** (`../Lintap/pidstat-collector.py`;
   decided 2026-08-14 after the RHEL 8 fork storm — see design.md and
   [[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]]).
   Single process converting closed windows with the duckdb Python API.
   Telemetry source per the design's 2026-08-14 investigation: implement
   behind a small sampler interface — preferred option B (stdlib `/proc`
   sampler, zero children, full schema coverage), with option A (one
   `pidstat -u -d -r -w -h -p ALL <interval>` child) as the conservative
   fallback and as the side-by-side test oracle either way; record the
   choice in design.md. Container attribution (added 2026-08-14): emit
   `cgroup_path`, `pid_ns_inode`, and best-effort
   `container_runtime`/`container_id` from `/proc/<pid>/cgroup` and
   `/proc/<pid>/ns/pid` (v1/hybrid and v2 formats), cached per
   (pid, starttime); the Wintappy bronze migration in step 7 adds the same
   columns so the schema changes once. Requirements (validated slice-1 semantics carry
   over): identical `PIDSTAT_*` env interface; spool/pending/meta
   crash-salvage mechanics outside the swept tree; `dayPK=/hourPK=`
   partitioning, file naming, and atomic rename; bronze schema + `hostname`;
   accumulation guard; SIGTERM sealing; empty-window skip. The rewrite
   absorbs all three open review findings: row date from the window-start
   epoch (midnight fix), glued-record parsing that keeps valid leading
   records (port the bash test fixture), and full exception detail logged on
   conversion failure. Retire `pidstat-collector.sh` (delete; git history
   preserves it); `pidstat-collect.sh` stays as the simple example.
   Decide and record the Python runtime/packaging approach (RHEL 8 default
   python3 is 3.6 — too old for duckdb wheels; see design open question).
6b. **Port the test suite to pytest** in `../Lintap` (uv project exists):
   all seven bash test cases (conversion/partitioning, loop parsing,
   glued records, salvage, byte cap, age cap, live row preservation) plus
   two new guards — the midnight/window-date case, and a fork regression
   test asserting steady-state child processes == the single pidstat
   (e.g., `/proc/stat processes` delta vs. pidstat-only baseline).
7. **Wintappy DBT change**: parquet-oriented pidstat macros
   (`raw_sensor/pidstat/**/*.parquet` default, `PIDSTAT_DATA_PATH` still
   honored) and `read_parquet` bronze model with `filename=true` provenance;
   legacy-CSV migration — recommended: keep bronze parquet-only and add a
   one-time DuckDB conversion script for existing CSV datasets (dev may choose
   a temporary union instead if cleaner). *(Slice 2.)*
8. **Verification runs** (record in `verification.md`): shellcheck (install
   it or run in a container); rotation + kill test rerun after the parser
   fixes; DBT build over rotated parquet output including the empty-input
   case; opt-in upload test; 1h+ Multipass end-to-end per the validation
   thread setup. *(Slice 2.)*
9. **Closeout**: promote durable facts (collector behavior, layout, the
   implicit ride-along contract, the S3Adapter-disabled-by-default deployment
   prerequisite) to canonical pages — likely
   `wiki/repo/lintap-supporting-repo.md`, `wiki/repo/wintappy-pipeline-repo.md`,
   and a note in the sensor upload docs; update `wiki/index.md` and
   `wiki/log.md`.

## Files Likely To Change

- `../Lintap/pidstat-collector.py` (new) and `pidstat-collector.sh`
  (deleted), `../Lintap/tests/` (pytest port), `../Lintap/pyproject.toml`
  (duckdb dependency), `../Lintap/packaging/…` (new unit),
  `../Lintap/README.md`.
- `../Wintappy/wintap_dbt/macros/pidstat.sql`,
  `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql`,
  `../Wintappy/wintap_dbt/README.md`.
- This wiki: work-folder artifacts, then canonical pages at closeout.

## Tests To Add Or Update

- pytest in `../Lintap` (uv): the seven ported cases, the midnight/window-date
  case, and the fork regression guard.
- Wintappy DBT: pidstat model builds against a parquet fixture; empty-input
  path still yields the typed empty table.

## Migration Or Compatibility Notes

- Verified 2026-08-12: Linux deployments do run `CacheManager`'s upload loop
  when `WINTAP_DISABLE_ETL=false`, but the repo-shipped `ETLConfig.json`
  leaves `S3Adapter` disabled and defaults `UploadIntervalSec` to `300`.
  This first slice therefore aligns the collector to a 300-second default (or
  `WINTAP_ETL_UPLOAD_INTERVAL_SEC` override) and keeps upload verification
  opt-in/manual until deployment config is confirmed on a target host.
- Existing tab-CSV pidstat datasets (e.g., the validation thread's one-hour
  dataset) predate the format change; convert once with DuckDB or keep a
  temporary legacy union in bronze — decide in step 6.
- `PIDSTAT_DATA_PATH` override behavior must keep working for ad-hoc analysis
  layouts.

## Rollback Plan

- The old script remains in place; disabling the new service and reverting the
  Wintappy macro/bronze commit restores the previous end-to-end path.

## Done Checklist

- [x] Step 1 verification recorded; design open questions resolved
- [x] Collector + rotation + conversion working locally
- [x] Crash salvage + accumulation guard tested
- [x] Python collector (`pidstat-collector.py`) implements all carried-over semantics; bash `pidstat-collector.sh` retired
- [x] Telemetry source chosen per design investigation (B preferred) and recorded; pidstat-oracle comparison test green
- [x] Container attribution columns emitted (cgroup_path, pid_ns_inode, runtime/id) with v1/v2 parser test; live containerized-process fixture still open (environment-dependent)
- [x] Review findings absorbed: window-epoch date, glued-record partial emission, conversion errors logged with detail
- [x] pytest suite ported (7 cases) + midnight case + fork regression guard; all green
- [x] Python runtime/packaging decided and recorded (RHEL 8 python3.6 constraint)
- [x] `-p ALL`, env knobs, and Python deps documented in ../Lintap/README.md
- [x] Wintappy DBT updated (parquet macros/bronze, legacy-CSV path decided); fixture test green
- [x] Slice 2 reviewed and accepted (2026-08-16; pytest 12/12 independently re-verified, stat-field offsets checked against proc(5), Wintappy migration verified against spec)
- [ ] Review follow-up: accumulation guard tolerant of files vanishing between listing and stat/delete (the uploader will delete concurrently once the upload fix lands), and guard failures reported distinctly from conversion failures
- [ ] Live containerized-process fixture test (needs a container runtime on the test host)
- [ ] systemd unit (uv-managed venv launcher) installs and survives reboot on a target host
- [ ] 1h+ end-to-end run with S3 upload + local delete confirmed (blocked on [[wiki/work/fix-upload-cache-deletion/brief]] — delete-after-upload currently never fires)
- [ ] verification.md filled in; durable facts promoted; log updated
