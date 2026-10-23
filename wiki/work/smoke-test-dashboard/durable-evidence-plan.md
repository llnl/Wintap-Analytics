---
title: "Plan: durable smoke evidence and dashboard triage"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../wintap/wintap/core/etl/load/adapters/SMBFileShareAdapter.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../Lintap/pidstat-collector.py
  - ../wintap/devtools/smoke_manifest.py
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/macros/paths.sql
  - streamlit/projects/SmokeTests/main.py
  - streamlit/projects/SmokeTests/queries.py
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/devtools; ../wintap/wintap/core/etl/load; streamlit/projects/SmokeTests
tags: [planning-only, smoke-tests, parquet, durable-data, streamlit, triage]
---

# Plan: durable smoke evidence and dashboard triage

Originally a planning-only investigation. User subsequently accepted normal
transport latency/source deletion and authorized implementation. **The clarification
below supersedes the original durability gates/spool requirements in this plan.**

## Accepted scope and implementation clarification

- Analysis reads the existing mounted/transferred durable dataset. Long-term
  source-host retention, delivery acknowledgements, transport hardening and a retry
  daemon are not feature blockers and are not implemented.
- Shared Python export activates via `--smoke-data-root` or `WINTAP_DATA_ROOT`, with
  `--no-smoke-parquet` opt-out; DuckDB is optional and JSON remains the fallback.
- Up to three immutable start/first-selectors/final snapshots, UTC publication
  partitions, typed metadata/full manifest JSON/hash; automatic latest-revision
  discovery and host/test triage are implemented. First selectors are the coarse
  snapshot trigger, not proof that a test's full stimulus has finished.
- V1 uses local/mounted/synced raw parquet; direct S3 browsing and DBT are deferred.
- Missing data remains yellow, with no delivery watermark requirement. Existing
  transport risks below remain documented observations, not acceptance gates.
<!-- SYNTHESIS: explicit user clarification and implementation authorization, 2026-10-22 -->

## Recommendation

Create **one new evidence dataset**, `raw_smoke_test`, not a new eBPF sensor or
another workload. All existing smoke families publish into it:

```text
WINTAP_DATA_ROOT/raw_sensor/raw_smoke_test/
  dayPK=YYYYMMDD/hourPK=HH/
    <safe-host>+raw_smoke_test+<run-uuid>+<revision>.parquet
```

Use typed searchable run metadata **plus the complete manifest JSON in a string
column**. Preserve local editable JSON as the spool/manual fallback; parquet is
the transfer/analysis envelope. Dashboard auto-discovers runs from the dataset root;
manual uploads remain optional. UUID, not file location or partition, groups a run.
<!-- SYNTHESIS: inferred from pidstat-collector.py, CacheManager.cs and current smoke_manifest.py -->

## Existing mechanism: what actually works

- CacheManager enumerates completed raw-sensor parquet and hands files to adapters
  without an event-type allowlist. A producer writing into the proper tree can ride
  this path without adding a serializer or changing RawSensorWriter's mapping.
- S3/file-share relative paths preserve `raw_sensor/<type>/...`; filenames must be
  collision-safe across hosts and repeated runs. JSON alone is **not** selected by
  the parquet sweep. Do not disguise JSON with a `.parquet` extension.
- pidstat keeps runtime spool, converts using Python DuckDB, writes `.parquet.active`
  then atomically renames to `.parquet`, and retries failed conversions.
- Default upload interval is 300 seconds; all shipped adapters are disabled.
  Data arriving automatically requires an enabled/running uploader or an existing
  external folder-transfer job that includes the new type. Our current VM→Mac
  demonstration used manual archive transfer, not a configured automatic adapter.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §WorkerThread_DoWork, upload, getRawSensorParquetFiles; ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs §getS3ObjectNameForFile; ../Lintap/pidstat-collector.py §convert_spool_to_parquet; ../wintap/wintap/core/etl/ETLConfig.json -->

### Existing transport caveats (accepted, not feature gates)

1. **Startup deletion:** live `clearRawSensor()` deletes existing raw parquet when
   at least one uploader is enabled. Unshipped smoke evidence can disappear on
   collector restart. This must be reconciled before claiming restart-safe delivery:
   preferably a separately reviewed preservation/retry fix; alternatively a runtime
   spool retained until confirmed delivery with explicit bounded retention. Merely
   retaining JSON until parquet conversion succeeds does not protect upload loss.
2. Cache pruning is global, oldest-first with protection; smoke evidence competes
   with telemetry and can be evicted during long outages.
3. **Any adapter success deletes source**, even if another destination failed.
   Define the authoritative analysis destination; do not claim reliable multi-sink
   delivery under the current contract. No silent uploader redesign in this slice.
4. ETL-disabled/startup-test harnesses may have no upload worker; publishing parquet
   does not make a stopped collector transfer it. Keep evidence queued or use the
   deployment's external transfer mechanism. Package opt-out tests stop the service
   before returning, so publication timing and later upload need explicit testing.
5. File-share adapter copies directly to final destination names. Source atomic
   rename does not prevent a reader seeing a destination partial copy. Plan an
   atomic destination publish fix or bounded reader retry; never infer completion
   merely from a file appearing. Separate adapter behavior from S3 object visibility.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/CacheManager.cs §clearRawSensor, pruneCache, upload; ../wintap/wintap/core/etl/load/adapters/SMBFileShareAdapter.cs §Upload -->

## Proposed schema and publication lifecycle

Start with **one row per immutable run snapshot**, not one file per selector:

| Typed column | Purpose |
|---|---|
| schema_version, manifest_version | Envelope/payload evolution |
| run_id, test_name, revision | Stable grouping and snapshot selection |
| hostname, host_id (nullable), boot_id (nullable) | Host context; hostname alone can be reused |
| started_at_utc, completed_at_utc, published_at_utc | Explicit UTC timing, independent of path/mtime |
| phase | started / stimulus-complete / finished; lifecycle distinct from outcome |
| outcome, exit_code, stimulus_only | passed/failed/incomplete; generated is not capture PASS |
| capture_run_ids_json (nullable) | Recorded HOST context when available, not invented from timing |
| manifest_json, manifest_sha256 | Full selectors, expectations, skips/report and conflict detection |

Do not flatten every nested case in v1; DuckDB can extract selectors from JSON.
Later add a view or derived table for cases/checks if needed. Repeated snapshots
have the same run ID and increasing revision, unique immutable filenames. Never
overwrite a swept parquet file: an earlier copy may already have been uploaded
and deleted. Identical retries deduplicate by run/revision/hash; conflicting hashes
at the same revision are an integrity error, not arbitrary last-write-wins.

Keep a local runtime JSON spool/checkpoint. Publish coarse lifecycle snapshots
(start, stimulus-complete, final), not every `record()` call. The early snapshots
make interrupted runs visible; select the latest revision but retain history.
SIGKILL cannot publish a final outcome: stale start becomes incomplete/yellow,
not fabricated failure. Independent converter retries invalid/missing native
dependencies; publication failure must be reported distinctly from stimulus outcome.
Bound/spell out spool retention and manual recovery; avoid infinite tiny-file growth.

Python DuckDB is the closest pidstat precedent; it adds a dependency to the current
stdlib-only workload. Prefer optional durable export using the existing packaged
pidstat Python environment or a dedicated converter, retaining stdlib JSON when
DuckDB is unavailable. Resolve roots explicitly from CLI/config/service env—an
interactive user's environment does not automatically inherit the service's env.
Provide a narrow permissions/group strategy for QA writers; do not require every
workload to run as root or make the entire collector data tree world-writable.
Avoid copying secrets in command arguments, URLs or manifests; sanitize and cap
report size before publication. Keep workload test files **outside** data root
because FileOps deliberately filters it.
<!-- SYNTHESIS: proposed extension of ../wintap/devtools/smoke_manifest.py and pidstat spool lifecycle -->

## Partitioning: keep it, do not let it define runs

Use the existing day/hour layout, with **publication time in UTC** as partition
meaning. pidstat's current partition function uses local `datetime.fromtimestamp`;
do not blindly copy that timezone behavior (RawSensorWriter uses UTC).

Run snapshots may span hours/days; group by UUID across partitions and retain full
start/end times. A date-window browser discovers runs first, then fetches relevant
revisions and queries telemetry using run bounds plus explicit aggregation/clock
tolerance. A start-hour-only scan misses final revisions; an event-time-only scan
misses late-published evidence. Do not split one small manifest across event hours.
No runUUID partition initially (too many tiny directories); typed hostname and
unique filenames support multiple hosts without requiring new host partitions.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector.py §build_destination_file; ../wintap/wintap/core/etl/load/RawSensorWriter.cs §MaterializeFromParquetGlob; ../Wintappy/wintap_dbt/macros/paths.sql §raw_sensor_partition_globs -->

## Analysis-side work

1. Discover only `raw_sensor/raw_smoke_test/**/*.parquet` for run envelopes,
   filter publication partitions/date/host/test and deduplicate revisions.
2. Exclude this evidence family from general telemetry normalization. Current app
   scans all parquet and classifies known event columns; otherwise new envelopes
   become useless 'other' rows and inflate scans.
3. Remove the need to configure a separate manifest source for routine use; keep
   JSON upload as a troubleshooting fallback. Multi-host picker/list uses metadata,
   not analysis-machine hostname. Unlabelled direct data remains an attribution gap.
4. App currently uses local `Path.rglob`; ride-along S3 delivery does **not** add
   S3 browsing automatically. Choose v1 mounted/synced local durable dataset, or
   explicitly scope an S3 DuckDB/httpfs credentials-and-listing enhancement.
5. DBT does not automatically build a model for a new type. Optional Wintappy
   bronze `stg_smoke_test_runs` with empty typed relation when absent, followed by
   latest-run/case views, can follow pidstat. Not required for direct raw-parquet
   dashboard v1; DBT work requires separate sibling-repo authorization.
6. Partition-pruned reads and aggregate checks should replace loading all matching
   event rows into Python. Cache by dataset/file inventory and run revision;
   fetch detail rows only when requested. Necessary for multiple hosts/large datasets.

## Top-level triage: yes, with explicit states

Show a host × test table, colored status **and text/icon**, counts and clickable
links to interesting sections. Default to latest run per host/test with a toggle
for failures/history; older failures must remain discoverable. Compute evidence
checks once and reuse for overview/details.

| State | Rule |
|---|---|
| Red — confirmed problem | Harness failure or explicit identity/thread/parent violation; missing required observations only after data completeness is established |
| Yellow — attention / incomplete | Started/unfinalized run, pending transfer, unknown completeness, skips/partial capabilities, clock/host ambiguity, stale result, parse/schema issue |
| Green — evidence complete | Finished run and all applicable required checks pass with sufficient capture/arrival evidence; stimulus-only completion is never sufficient |
| Gray — not run / not applicable | No run supplied, or an explicitly excluded test; not counted as success |

Display **harness outcome**, **observed coverage** and **arrival/completeness** as
separate dimensions, with overall severity derived from them. A failed workload is
red 'workload failed', not automatically 'sensor failed'. A passing actual-object
trace can be green for trace scope without parquet, not for pipeline scope.
Thread-negative absence requires positive companion capture evidence. Missing
capability-required events after a trusted complete capture can be red; unavailable
hooks should be explicit yellow/unsupported coverage rather than silently dropped
expectations. Our TCP Accept/server UDP Receive findings are attention/coverage
gaps until completeness is established, not proof of a specific sensor defect.

A fixed wait (300/600 seconds) is a **heuristic**, not a transfer watermark. A final
manifest does not prove telemetry arrived: files upload independently and can be
pruned. V1 should keep absence yellow unless there is trusted capture/export
closure; stronger red missing-data claims need an inventory/completion receipt or
validated ingestion watermark (separate design). Without an expected host/test
schedule the app cannot detect a host whose entire run/evidence never arrives.

## Implementation sequence and acceptance

1. Agree schema, snapshot policy, authoritative destination and UTC partition rule.
2. Implement shared optional Python exporter/spool with atomic publication and
   bounded retries; update smoke commands/packaging environment documentation.
3. Resolve startup-deletion/delivery gate and validate the actual deployment's
   enabled transport. No new sensor needed; generic transport hardening is separate.
4. Add dataset discovery, host/run selection and latest-revision checks to the app.
5. Add triage evaluator/overview using explicit pending/unsupported/gray semantics.
6. Optional DBT bronze/view and S3 browsing after v1 acceptance.

Acceptance cases: two hosts with same PIDs; repeated and overlapping runs;
hour/day crossover, differing host timezones, late/reordered snapshots, conflicting
duplicates; unavailable DuckDB/unwritable destination/disk pressure; interrupted
workload; failed upload/restart/retry; adapter-disabled/ETL-disabled/service-stopped
tests; partial file-share copy; manifest-before-telemetry arrival; missing hooks;
no-data/no-run; green requires positive evidence; thread violations red. Exercise
the real VM→durable destination→Mac path without manually transferring manifests.

## Open choices before implementation

- Which deployment transport is authoritative: shared/mounted directory, S3 or UNC?
- Should durable export be on automatically for installed QA environments, or CLI opt-in?
- Is a coarse 2–3 snapshot policy sufficient, and how long should local spool survive?
- Should v1 use raw parquet only or also introduce DBT models/S3 access?

Related: [[wiki/tool/smoke-test-results-dashboard]],
[[wiki/component/sensor-upload-cache-pipeline]].
