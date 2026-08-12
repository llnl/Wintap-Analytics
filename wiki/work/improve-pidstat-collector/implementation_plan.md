---
title: "Implementation Plan: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - wiki/work/improve-pidstat-collector/brief.md
  - wiki/work/improve-pidstat-collector/design.md
policy: agent-editable
last_validated: 2026-08-11
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
6. **Wintappy DBT change**: parquet-oriented pidstat macros
   (`raw_sensor/pidstat/**/*.parquet` default, `PIDSTAT_DATA_PATH` still
   honored) and `read_parquet` bronze model; decide legacy-CSV migration
   (one-time conversion script vs. temporary union).
7. **Verification runs** (record in `verification.md`): shellcheck; local
   rotation + kill test; DBT build over rotated output; opt-in upload test;
   1h+ Multipass end-to-end per the validation thread setup.
8. **Closeout**: promote durable facts (collector behavior, layout, the
   implicit ride-along contract) to canonical pages — likely
   `wiki/repo/lintap-supporting-repo.md`, `wiki/repo/wintappy-pipeline-repo.md`,
   and a note in the sensor upload docs; update `wiki/index.md` and
   `wiki/log.md`.

## Files Likely To Change

- `../Lintap/pidstat-collector.sh` (new), `../Lintap/packaging/…` (new unit),
  `../Lintap/README.md`.
- `../Wintappy/wintap_dbt/macros/pidstat.sql`,
  `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql`,
  `../Wintappy/wintap_dbt/README.md`.
- This wiki: work-folder artifacts, then canonical pages at closeout.

## Tests To Add Or Update

- shellcheck in whatever lint path `../Lintap` uses.
- Rotation/kill/salvage shell tests (bats or minimal harness).
- Wintappy DBT: pidstat model builds against a parquet fixture; empty-input
  path still yields the typed empty table.

## Migration Or Compatibility Notes

- Existing tab-CSV pidstat datasets (e.g., the validation thread's one-hour
  dataset) predate the format change; convert once with DuckDB or keep a
  temporary legacy union in bronze — decide in step 6.
- `PIDSTAT_DATA_PATH` override behavior must keep working for ad-hoc analysis
  layouts.

## Rollback Plan

- The old script remains in place; disabling the new service and reverting the
  Wintappy macro/bronze commit restores the previous end-to-end path.

## Done Checklist

- [ ] Step 1 verification recorded; design open questions resolved
- [ ] Collector + rotation + conversion working locally
- [ ] Crash salvage + accumulation guard tested
- [ ] systemd unit installs and survives reboot
- [ ] Wintappy DBT updated; fixture test green
- [ ] 1h+ end-to-end run with S3 upload + local delete confirmed
- [ ] verification.md filled in; durable facts promoted; log updated
