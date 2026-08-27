---
title: "Feature Design: Improve pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collect.sh
  - ../Lintap/packaging/lintap-rpm/lintap.env
  - ../wintap/documentation/Linux Deployment Guide.md
  - ../wintap/wintap/core/infrastructure/PluginManager.cs
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/ETLConfig.json
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../wintap/wintap/core/etl/shared/Utilities.cs
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-08-20
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-pidstat-collector/design.md
tags: [feature-work, design, lintap, pidstat, parquet, s3]
---

# Feature Design: Improve pidstat Collector

## Summary

A single-process Python collector in `../Lintap` samples `/proc` directly,
rotates samples into typed parquet partitioned like raw_sensor
(`dayPK=YYYYMMDD/hourPK=HH`) with hostname and container-attribution columns,
and drops completed files into the sensor's parquet cache under
`raw_sensor/pidstat/`. The sensor's existing CacheManager/uploader pipeline
ships them to S3 (local deletion pending
[[wiki/work/fix-upload-cache-deletion/brief]]) — no C# changes. Wintappy's
pidstat DBT macros and bronze model read the parquet layout.

## Decisions Recorded (from brief, 2026-08-11)

- New script; `pidstat-collect.sh` remains as a minimal example.
- Location: `../Lintap`, for now.
- Runs continuously as a service, independent of individual Lintap runs.
- Sampling interval: 5 s default, configurable.
- Output format: parquet.
- Rotation boundary: the sensor's merge/upload cycle (`UploadIntervalSec`),
  partition layout `dayPK=/hourPK=` matching raw_sensor.
- S3 push: ride the sensor's existing upload mechanism, at least for now.

## Decisions Recorded (post-review, 2026-08-12)

- Sample with `-p ALL` (every process every interval), as implemented in the
  first slice. This deviates from the old activity-only collector and
  multiplies volume roughly 5× (observed ~59k rows/15 min ≈ 5.7M rows/day on a
  quiet host, vs. ~1.1M lines/day before), but idle-process RSS/VSZ is needed
  for the motivating correlation analysis (Lintap memory/CPU vs. event_store
  growth), and complete sampling is the safer default for research data.
  Accepted for now; if volume becomes a problem, filter or compress in the ETL
  layer (Wintappy bronze/silver) later rather than at collection time —
  dropping data at the collector is unrecoverable, dropping it downstream is a
  view choice.

## Decision (2026-08-14): Rewrite the Collector in Python

Decided by the human after the RHEL 8 field test
([[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]]): slice 2
rewrites the collector as a single-process Python program
(`pidstat-collector.py`) using the **duckdb Python interface** for parquet
conversion, replacing the bash implementation.

Rationale:

- The bash hot loop's per-line command substitutions caused a ~700 forks/sec
  storm that flooded the sensor and polluted raw_process data — annoying now
  and a growing liability over time. Python parses in-process; steady state
  runs exactly two processes: the collector and its one `pidstat` child.
- The bash version had grown past the point of readability (~500 lines of
  spool/meta/parse machinery); Python keeps the same semantics in clearer
  code and gets real unit tests (pytest, `../Lintap` already has a uv
  project).
- In-process duckdb also removes the per-rotation CLI child and gives real
  exception detail on conversion failures (absorbing review finding 4).

The validated slice-1 semantics are requirements on the rewrite, not
open questions: same spool/pending/meta crash-salvage mechanics outside the
swept tree, same `dayPK=/hourPK=` layout and file naming, same parquet
schema (bronze columns + `hostname`), same `PIDSTAT_*` environment
interface, `-p ALL` at a configurable interval (default 5 s), rotation
default 300 s synced to `WINTAP_ETL_UPLOAD_INTERVAL_SEC`, accumulation
guard, SIGTERM window sealing, and empty-window skip. The bash
`pidstat-collector.sh` is retired (deleted; git history preserves it) —
`pidstat-collect.sh` remains the simple example.

## Telemetry Source Investigation (2026-08-14)

Question: with the collector moving to Python, is a `pidstat` child still the
best telemetry source? Criteria: well-established solid feed, low overhead,
minimal dependencies. Three options for the developer to implement and test;
the schema's less-common columns (minflt/majflt, `iodelay_ticks`,
`guest_percent`, `%wait`) turn out to be the deciding constraint.

| Option | Feed | Schema coverage | Deps | Steady-state processes |
| --- | --- | --- | --- | --- |
| A. Keep `pidstat` child | sysstat parses /proc, we parse its text | Full (it defined the schema) | sysstat pkg | collector + pidstat |
| B. Direct `/proc` sampler (stdlib) | same kernel files pidstat reads | Full (verified below) | none | collector only |
| C. psutil | psutil's C extension over /proc | **Incomplete** | pip psutil | collector only |

Verified 2026-08-14 on a live kernel (lintap-dev):

- `/proc/<pid>/stat` (52 fields) carries minflt/majflt (10/12), utime/stime
  (14/15), starttime (22), vsize/rss (23/24), `delayacct_blkio_ticks` (42 —
  pidstat's `iodelay`), guest_time (43). `/proc/<pid>/io` carries
  read_bytes/write_bytes/cancelled_write_bytes (kB_rd/kB_wr/kB_ccwr).
  `/proc/<pid>/status` carries voluntary/nonvoluntary_ctxt_switches.
  `/proc/<pid>/schedstat` carries run-delay (pidstat's `%wait` basis).
  Option B therefore reproduces every bronze column from first-party kernel
  files — the same feed pidstat itself consumes.
- psutil's Linux API exposes **no page faults, no guest time, no iodelay**
  (`cpu_times`: user/system/children/iowait only). Option C would need /proc
  supplements for those columns, at which point the dependency buys little.
  <!-- GROUND_TRUTH: verified via psutil API inspection on lintap-dev, 2026-08-14 -->

Recommendation (for the dev to validate, not a mandate):

- **Primary: Option B** — zero new dependencies (duckdb stays the only pip
  dep), zero child processes, eliminates the text-parsing class that caused
  both slice-1 parser bugs (AM/PM locale, glued records), full schema
  coverage. Cost: we own delta/rate math (counter deltas ÷ interval, ticks
  via `os.sysconf('SC_CLK_TCK')`) and known /proc parsing subtleties: parse
  `stat` after the last `)` (comm may contain spaces/parens), detect PID
  reuse between samples via starttime, `/proc/<pid>/io` needs root (the
  collector already runs as root).
- **Fallback and test oracle: Option A** — if B's rate math proves fiddly,
  the pidstat child is a fine conservative choice (one child, C-computed
  rates); either way, keep pidstat in the test suite as the oracle: run both
  sources side-by-side over the same window and assert rates agree within
  tolerance. That converts slice 1's parser into validation leverage.
- **Option C (psutil) is not recommended**: schema-incomplete alone, adds a
  C-extension wheel to the RHEL 8 python-version decision, and anything it
  can't provide comes from /proc anyway.

### Container Attribution (added 2026-08-14, human: "huge plus")

Per-process container info is a wanted enrichment — and it is only available
via option B's feed, which effectively settles the source choice:

- `/proc/<pid>/cgroup` names the container: docker (`/docker/<id>` or
  `docker-<id>.scope`), podman (`libpod-<id>.scope`), Kubernetes
  (`kubepods` slices), plain systemd units otherwise. RHEL 8's cgroup
  v1/hybrid multi-line format and the v2 unified `0::/path` format both
  parse trivially. Verified live on lintap-dev (v2 format).
- `/proc/<pid>/ns/pid` (readlink → `pid:[<inode>]`) identifies namespace
  membership, distinguishing host from containerized processes and grouping
  co-container processes even when runtime parsing fails.

Neither pidstat nor psutil exposes any of this.

Schema addition (coordinate with the Wintappy bronze migration happening in
this same slice — ideal timing): keep full fidelity plus best-effort parse —
`cgroup_path` (raw), `pid_ns_inode` (bigint), `container_runtime` and
`container_id` (nullable VARCHARs, parsed heuristically from cgroup_path).
Cache per (pid, starttime) since cgroup membership rarely changes; cost is
one extra small read + one readlink per new process.

Side benefit: namespace-tagged rows would let the RHEL 8 diagnostic's
interleaved-PID-range question
([[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]]) be answered
from collector data directly.

The dev records the chosen source in this page and implements the sampler
behind a small interface so the choice stays swappable.

### Implemented Source Choice (2026-08-15)

- Implemented **Option B** in `../Lintap/pidstat-collector.py`: a stdlib
  `/proc` sampler with no steady-state child processes. The collector samples
  `/proc/<pid>/stat`, `/proc/<pid>/status`, `/proc/<pid>/io`,
  `/proc/<pid>/schedstat`, `/proc/<pid>/cgroup`, and `/proc/<pid>/ns/pid`,
  caches container metadata by `(pid, starttime)`, and computes deltas/rates
  in-process. PID reuse is detected by `starttime`.
- The old `pidstat` text path is retained only as a **test oracle** in the new
  pytest suite. The live oracle test runs a short workload, samples the target
  PID with both the `/proc` sampler and `pidstat -u -d -r -w -h -p <pid> 1 1`,
  and asserts CPU, RSS, and write-rate agreement within tolerance on
  `lintap-dev`.
- The steady-state fork-regression guard now verifies the collector process has
  zero child PIDs via `/proc/<pid>/task/<pid>/children`, which is stricter than
  the original "one pidstat child allowed" requirement because the chosen
  source no longer needs the fallback child.

### Implemented Container Attribution (2026-08-15)

- The collector now emits `cgroup_path`, `pid_ns_inode`,
  `container_runtime`, and `container_id` alongside the previously validated
  bronze columns plus `hostname`.
- Runtime/ID parsing is best-effort and nullable. The raw `cgroup_path` is
  always preserved even when the runtime heuristic fails.
- Unit coverage now includes both cgroup v1-style Docker paths and cgroup v2
  Podman-style `libpod-<id>.scope` paths.

## Proposed Approach

### Mechanism facts this design relies on (verified 2026-08-11)

- `CacheManager.upload()` enumerates **all** `*.parquet` under
  `{parquetRoot}/raw_sensor/` recursively and hands each file to every enabled
  uploader; it is event-type-agnostic, so a new `raw_sensor/pidstat/` subtree
  rides along without sensor changes.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §upload() -->
- ~~`Uploader_UploadCompleted` deletes each parquet after a successful
  upload, so local retention after upload is already handled.~~
  **Corrected 2026-08-15:** the delete handler exists and is subscribed, but
  no adapter ever raises `UploadCompleted` — the sensor currently re-uploads
  every cached parquet each cycle and never deletes. Confirmed by an
  overnight field test and code review; fix tracked in
  [[wiki/work/fix-upload-cache-deletion/brief]]. Until it lands, the
  collector's accumulation guard is the only effective local-disk bound.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §Uploader_UploadCompleted (handler), §upload() (unused successfulUpload); adapters/S3Adapter.cs §UploadCompleted (declared, never invoked) -->
- Uploaders build the S3 key from the path relative to the parquet root
  (`raw_sensor/<type>/dayPK=…/hourPK=…/file.parquet`), so the S3 layout
  mirrors the local layout automatically.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getS3ObjectNameForFile -->
- The upload loop runs `doMerge()` + upload every `UploadIntervalSec`; the
  collector's rotation should use the same configured value.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §uploader thread -->
- `cleanup()` deletes orphaned `*.active` files, establishing the existing
  in-progress-file convention: only completed data may carry the `.parquet`
  extension inside the swept tree.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §cleanup() -->
- Small-file merging before upload covers the sensor's own serializer files
  (`doMerge()` consolidates each type's flush files into one file per upload
  cycle), **but not pidstat** — corrected 2026-08-17 by field observation:
  pidstat files land in `raw_sensor/pidstat/` pre-partitioned and `doMerge()`
  never touches them, so they accumulate as small per-window files
  (12+/hour/host, more under upload backlog). The 2026-08-16 claim that "no
  merge step is needed for pidstat" held only at single-cycle granularity.
  Follow-up task recorded in [[wiki/work/fix-upload-cache-deletion/brief]]
  (next slice): the upload cycle's merge step should consolidate small files
  for the cycle generically for any event-type directory under `raw_sensor/`,
  including pidstat.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/Merge.cs §Start (serializer dirs only); field observation 2026-08-17 -->

### Collector loop

1. Sample `/proc` for **all processes** every `PIDSTAT_INTERVAL_SEC` seconds
   (default 5 s; equivalent to the accepted `-p ALL` semantics), appending
   normalized TSV rows to an in-progress spool file **outside** the
   `raw_sensor/` tree (e.g., `$WINTAP_DATA_ROOT/pidstat-spool/current.tsv`),
   so the uploader can never see a partial window.
2. On each rotation boundary (aligned to wall-clock so windows map cleanly to
   `hourPK`; boundary length = the sensor's `UploadIntervalSec`), close the
   spool file and convert it to typed parquet in-process via the duckdb
   Python API (slice-2 decision above), applying the same casts/column names
   as today's `stg_pidstat_metrics` (so the parquet schema is already the
   bronze schema). The row date derives from the window-start epoch, not
   wall-clock at parse time (review finding 2, midnight correctness).
3. Atomically move the completed file to
   `{parquetRoot}/raw_sensor/pidstat/dayPK=YYYYMMDD/hourPK=HH/<host>+pidstat+<epoch>.parquet`
   (write to a temp name, `mv` into place — rename is atomic within a
   filesystem).
4. The sensor's upload cycle picks it up, ships to S3, deletes locally.

### Service lifecycle

- A systemd unit (template in `../Lintap/packaging/`) with `Restart=always`
  runs the collector independent of sensor sessions.
- On startup, the collector salvages or discards a leftover spool file from a
  crash (salvage = convert and ship the partial window with its real
  timestamps; the data is still valid samples).

### Accumulation guard

While the sensor is down, completed parquet accumulates locally (nothing
sweeps it). The collector enforces a configurable cap (max total bytes or max
age) on `raw_sensor/pidstat/`, deleting oldest-first past the cap and logging
what was dropped.

### Wintappy coordinated change

- `stg_pidstat_metrics` became a parquet bronze reader with `filename=true`
  provenance and typed-empty fallback.
- Follow-up bugfix 2026-08-20: the dedicated pidstat DBT macros/override were
  removed. pidstat now resolves `raw_sensor/pidstat` from
  `WINTAP_DBT_RAW_SENSOR_DATASET` through Wintappy's shared `raw_sensor`
  path/existence helpers and shares the same day/hour partition-window
  narrowing as the other optional raw events.

## Data Model Or Schema Changes

Parquet columns = today's `stg_pidstat_metrics` output columns (time, uid,
pid, usr_percent … command) plus `hostname`, `cgroup_path`, `pid_ns_inode`,
`container_runtime`, and `container_id`. Filename provenance is now supplied
in Wintappy via `read_parquet(..., filename=true)`.

## Edge Cases

- Midnight rollover: window spanning midnight is split at the boundary (or
  assigned by window-start time — pick one and document; window-start is
  simpler and matches raw_sensor's capture-time-based partitioning).
- Empty windows (pidstat produced no output): skip file creation.
- Clock jumps / suspend-resume: partition by sample timestamps, not wall-clock
  at conversion time.
- duckdb Python module missing/unimportable: fail loudly at service start,
  not at first rotation.
- Sensor down for days: accumulation guard above.

## Error Handling

- Collector logs to journald (via systemd) with the same timestamped style as
  the existing script.
- Conversion failure keeps the spool file and retries next cycle rather than
  dropping samples.
- The Python rewrite now logs full stack traces for DuckDB conversion failures
  before leaving the pending spool in place for retry, closing review finding 4.

## Risks

- The ride-along contract is implicit: nothing in the sensor promises to keep
  sweeping unknown subtrees under `raw_sensor/`. A sensor-side change could
  silently strand pidstat files. Mitigation: record the dependency in the
  sensor repo docs at closeout, and the accumulation guard bounds the damage.
- `pruneCache()` behavior on Linux (drive-letter logic looks Windows-oriented)
  is unverified; if cache pruning misbehaves it could delete unshipped pidstat
  files under pressure.
- Old tab-CSV datasets become unloadable by the updated bronze model unless
  migrated (see below).

## Alternatives Considered

- Standalone `aws s3` sync loop in the collector: independent of sensor
  lifetime, but duplicates credentials, retry, and layout logic. Rejected
  "for now" per brief.
- Keep tab-CSV output: no DBT change needed, but conflicts with the parquet
  decision and uniform-layout goal.
- Implement inside the sensor (C#): best lifecycle integration, but violates
  the brief's non-goal and couples resource monitoring to sensor uptime.

## Open Questions

- Resolved 2026-08-12: the Linux service path does run the upload loop when ETL
  is enabled. The documented Linux systemd service starts `Lintap.dll` with
  `WINTAP_DISABLE_ETL=false`, and `PluginManager` responds by constructing
  `WintapETL`, which starts `CacheManager`.
  <!-- GROUND_TRUTH: ../wintap/documentation/Linux Deployment Guide.md §Example systemd Service -->
  <!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/lintap.env §Enable normal ETL and Linux sensor manager -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/PluginManager.cs §PluginManager() -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/WintapETL.cs §cacheManager_DoWork -->
- Resolved 2026-08-12: the repo-shipped ETL config uses `UploadIntervalSec` =
  `300`, and the current code only exposes an environment override for that
  interval (`WINTAP_ETL_UPLOAD_INTERVAL_SEC`), not for adapter enablement.
  The shipped `ETLConfig.json` leaves `S3Adapter.Enabled=false`, so the
  pidstat ride-along works only on Linux deployments that explicitly enable S3
  in the deployed `ETLConfig.json`; this slice therefore keeps upload
  verification read-only/manual rather than assuming S3 is active everywhere.
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/ETLConfig.json §Adapters -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/ETLConfig.json §UploadIntervalSec -->
  <!-- GROUND_TRUTH: ../wintap/wintap/core/etl/shared/Utilities.cs §GetETLConfig -->
- ~~DuckDB CLI vs. small Python program for the collector~~
  Resolved 2026-08-14 (human): Python, single process, duckdb Python API.
  The bash+duckdb slice-1 implementation worked but its per-line forking
  caused the RHEL 8 fork storm and the code had grown unreadable; see the
  slice-2 decision section above and
  [[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]].
- Resolved 2026-08-15 (revised later the same day after validation): target
  runtime/packaging is a **`uv`-managed dedicated venv** plus a small launcher,
  not a hardcoded host interpreter path. The packaged service now runs:
  `/bin/bash /usr/lib/lintap/pidstat-collector-launch.sh`, which resolves the
  interpreter from `PIDSTAT_VENV_DIR` (default
  `/opt/lintap/pidstat-collector/.venv`) and execs
  `pidstat-collector.py` from that venv. A companion bootstrap script,
  `pidstat-collector-bootstrap.sh`, creates the venv with `uv venv` and
  installs DuckDB into it.

  Default bootstrap runtime is `PIDSTAT_BOOTSTRAP_PYTHON=3.12`, which keeps the
  collector inside its supported `3.11 <= python < 3.13` range while still
  letting `uv` locate or download the interpreter per host. This avoids the
  operational brittleness of pinning `/usr/bin/python3.11` while preserving
  correctness (the service still runs as root for full `/proc` visibility).
- Resolved 2026-08-15: Wintappy bronze is now **parquet-only** for pidstat.
  No temporary CSV/parquet union was added. Existing legacy tab-CSV datasets
  must be converted out-of-band before being run through the updated DBT model.
- Should the validation harness (lintap validation thread) switch its pidstat
  capture to the new collector once it exists?
