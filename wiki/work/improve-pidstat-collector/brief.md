---
title: "Feature Brief: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - raw/Issues/Long_Running_Cleanup.md
  - ../Lintap/pidstat-collect.sh
  - ../Wintappy/wintap_dbt/macros/pidstat.sql
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs
policy: agent-editable
last_validated: 2026-08-14
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: reviewed
source_paths: wiki/work/improve-pidstat-collector/brief.md
tags: [feature-work, lintap, pidstat, monitoring, s3]
---

# Feature Brief: Improve pidstat Collector

> **Feature closed 2026-08-17** on branch `grantj-rhel8-testing` with accepted reviews; durable facts promoted to [[wiki/component/sensor-upload-cache-pipeline]], [[wiki/repo/lintap-supporting-repo]], and [[wiki/repo/wintappy-pipeline-repo]]. Follow-ups tracked in implementation_plan.md: collector CPU investigation (needs multi-system data), small-file consolidation (assigned to fix-upload-cache-deletion next slice), target-host systemd/reboot check, live container fixture, S3 end-to-end (unblocked once the upload fix merges).


## Problem

`../Lintap/pidstat-collect.sh` samples per-process CPU/memory/IO/context-switch
metrics via `pidstat -u -d -r -w -h 2` and writes one timestamped,
tab-delimited `.csv` file per invocation to `$WINTAP_DATA_ROOT/pidstat/` (or
`$PIDSTAT_DATA_PATH`). It is a manually started foreground script stopped with
Ctrl+C.

For long-running Lintap instances this is inadequate. The motivating issue
(`raw/Issues/Long_Running_Cleanup.md`) observed that CPU load grows
significantly as the event_store DuckDB grows over multi-day runs, and asks for
the collector to run alongside Lintap and push data to S3 so CPU/memory use can
be understood over time and in relation to system load.

Current weaknesses:

- No lifecycle management: not started/stopped with the Lintap sensor; requires
  a human and a terminal.
- One unbounded output file per invocation: no time-based rotation, so nothing
  can be shipped incrementally and a crash risks the tail of the run (output
  passes through a `tail | grep | awk` pipeline with block buffering).
- No S3 push: raw_sensor parquet is uploaded by the sensor's cache/upload
  adapters, but pidstat CSVs stay on the host.
- No local retention/cleanup policy after upload (related to the wider
  Long_Running_Cleanup issue).

## Goals

Decided 2026-08-11 (human-edited; see [[wiki/work/improve-pidstat-collector/design]]
for rationale and mechanism):

- Create a new script; leave the existing `pidstat-collect.sh` as a simple
  example of the core concept of process performance collection.
- The new collector lives in `../Lintap` for now.
- Run continuously as a managed service (e.g., systemd unit), not only during
  Lintap runs — the performance data is useful for other purposes. Starting
  and stopping alongside the sensor remains supported.
- Sampling interval: default 5 seconds, configurable.
- Output is parquet, not tab-delimited CSV.
- Rotate output on the same time boundary as the wintap/lintap data merge
  cycle (`UploadIntervalSec` in the sensor's ETL config), partitioned the same
  as raw_sensor: `dayPK=YYYYMMDD/hourPK=HH`. A crash loses at most one partial
  window.
- Push to S3 via the same mechanism as raw_sensor, at least for now: write
  completed parquet into the sensor's cache layout under
  `{parquetRoot}/raw_sensor/pidstat/dayPK=…/hourPK=…/`, where the sensor's
  CacheManager upload loop sweeps all `*.parquet` under `raw_sensor/`
  type-agnostically and each uploader preserves the relative path as the S3
  key — the S3 layout therefore mirrors raw_sensor so DBT/pull tooling can
  fetch both uniformly, with no C# changes expected.
- Keep local disk bounded: the collector's accumulation guard is the
  effective bound. (Corrected 2026-08-15: the sensor's delete-after-upload
  was found never to fire — adapters never raise `UploadCompleted` — so
  uploads currently repeat and nothing deletes; fix tracked in
  [[wiki/work/fix-upload-cache-deletion/brief]].)
- Deliberately version the downstream contract: Wintappy's
  `stg_pidstat_metrics` currently hardcodes tab-delimited
  `read_csv('$PIDSTAT_DATA_PATH/**/*.csv')`; moving to parquet requires a
  coordinated change to the pidstat macros and bronze model (`read_parquet`
  over the new layout).
- Enable the motivating analysis: correlate Lintap process resource use with
  system load and event_store growth over multi-day runs.
- Added 2026-08-14 (human, "huge plus"): per-process container attribution —
  cgroup path, namespace identity, and best-effort container runtime/ID
  columns from `/proc/<pid>/cgroup` and `/proc/<pid>/ns/pid` (see the
  telemetry-source investigation in
  [[wiki/work/improve-pidstat-collector/design]]).

## Non-Goals

- Replacing pidstat with a native Wintap/Lintap sensor plugin or eBPF-based
  resource telemetry.
- Windows-side resource collection.
- Changing Wintappy silver/gold model semantics or adding dashboards — the
  bronze loader changes to read parquet, but column meanings stay the same
  (analysis-side work can follow separately).
- Modifying `../wintap` C# code — the upload ride-along works with the
  existing type-agnostic sweep; if that turns out to be wrong, it becomes a
  design revision, not a silent scope change.
- Solving the event_store cleanup routine itself (tracked separately in
  Long_Running_Cleanup).

## User-Facing Behavior

An operator enables the pidstat collector once (as a service, independent of
any single Lintap run). Completed parquet windows appear under
`raw_sensor/pidstat/dayPK=…/hourPK=…/` locally, are uploaded to S3 alongside
raw_sensor data on the sensor's merge cycle and deleted locally after upload,
and a Wintappy DBT run over the fetched data materializes `pidstat_metrics`
without manual file handling.

## Acceptance Criteria

- Collector runs as a managed service without a human terminal session and
  survives operator logout and reboot.
- Output rotates on the merge-cycle boundary into `dayPK=/hourPK=` partitions;
  each completed parquet file is independently loadable by the (updated) DBT
  bronze model.
- Completed files are uploaded to S3 by the sensor's existing upload pipeline
  and deleted locally after confirmed upload; in-progress windows are never
  visible to the uploader as `*.parquet`.
- An interrupted run (kill -9, reboot) loses at most the current partial
  window.
- Sampling interval is configurable and defaults to 5 seconds.
- A multi-hour test run produces data that the updated `stg_pidstat_metrics`
  loads without schema errors.

## Affected Areas

- `../Lintap` — new collector script lives here; `pidstat-collect.sh` stays as
  the simple example (sibling repo; code changes need explicit authorization).
- `../wintap` upload path (`core/etl/load/CacheManager.cs`,
  `adapters/S3Adapter.cs`, `adapters/base/Uploader.cs`) — read/verify only; no
  changes expected since the sweep is type-agnostic.
- `../Wintappy/wintap_dbt/macros/pidstat.sql` and
  `models/bronze/stg_pidstat_metrics.sql` — coordinated change from tab-CSV to
  parquet over the new layout (sibling repo; code changes need explicit
  authorization).
- This repo's validation harness docs, which already rely on pidstat capture
  during validation runs.

## References

See [[wiki/work/improve-pidstat-collector/references]].

## Open Questions

The gating questions (code location, S3 mechanism, format, rotation, interval)
are decided above. Remaining design-level questions are tracked in
[[wiki/work/improve-pidstat-collector/design]]:

- Parquet writer technology in a `../Lintap` script: DuckDB CLI vs. Python.
- Confirm the Linux service build actually runs the CacheManager upload loop
  with an S3 adapter enabled (the sweep logic was verified in shared code, not
  in a Linux deployment).
- Exact completed-file naming convention and the in-progress-window
  convention (write outside `raw_sensor/` or as a non-`.parquet` name, then
  atomic rename).
- Accumulation bound while the sensor (and thus the uploader) is down.
- Migration for existing tab-delimited CSV datasets already collected.

## Test Plan

- shellcheck (or unit tests, if the collector is written in Python) for the
  collector itself.
- Short local run verifying rotation: multiple completed parquet files plus
  one in-progress window; kill mid-window and confirm completed files intact
  and no partial `*.parquet` visible.
- DBT check: point the updated pidstat macros at rotated output and confirm
  `stg_pidstat_metrics` builds with row counts matching collected samples.
- Upload path: opt-in integration test on a host with the sensor's uploader
  configured (no network in default tests), confirming upload + local delete.
- End-to-end: a Multipass validation run (per the lintap validation thread's
  setup) with the collector enabled for 1+ hour.

## Done When

- The remaining design questions are resolved in
  [[wiki/work/improve-pidstat-collector/design]].
- Acceptance criteria above pass on a real multi-hour run.
- Durable facts (final collector behavior, file layout, S3 layout) are
  promoted to canonical wiki pages and `wiki/log.md` is updated.
