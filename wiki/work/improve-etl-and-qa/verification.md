---
title: "Verification: Improve ETL and QA"
type: concept
confidence: medium
grounded_by:
  - ../Wintappy/Makefile
  - ../Wintappy/notebooks/wintap_dbt_overview.py
  - ../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/build_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/file_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/network_chart.sql
  - ../Wintappy/wintap_dbt/models/schema.yml
policy: agent-editable
last_validated: 2026-08-29
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/verification.md
tags: [feature-work, verification, wintappy, qa, dbt, pidstat]
---

# Verification: Improve ETL and QA

## Test Commands

1. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && make dbt-build`
2. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && make dbt-test`
3. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --isolated --dev --project . python - <<'PY' ... query smoke for build_summary, telemetry_event_summary, file_chart, network_chart, perf_chart, pidstat_process_summary, and the notebook's pidstat summary/top queries ... PY`
4. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --isolated --dev --project . python - <<'PY' ... verify the notebook availability expression against an empty pidstat_process_summary result ... PY`
5. `source "wintap-run.env" && export WINTAP_DBT_DATASET="${WINTAP_DBT_DATASET:-$WINTAP_DATA_ROOT/parquet}" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --isolated --dev --project . dbt run --project-dir wintap_dbt --profiles-dir wintap_dbt --select process_registry host host_ip process_file process_image_load process_registry_summary process_file_summary process_summary build_summary`
6. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && make dbt-build`
7. `ls -la .venv && make rebuild-venv && uv run --dev --project . python -c "import plotly, marimo; print(plotly.__version__)"`
8. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the new pidstat time-series query (1-minute buckets, peak CPU threshold 25, top 12 processes) and inspect row count / elapsed time ... PY`
9. `uv run --dev --project . python -m py_compile notebooks/wintap_dbt_overview.py`
10. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the revised pidstat time-series query using selected-metric ranking/filtering (example: Memory %, threshold 0.1) and inspect row count / elapsed time ... PY`
11. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the new event-volume-by-type query (1-minute buckets across process/file/network/registry/image_load) and inspect row count / elapsed time ... PY`
12. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the new 'By command' pidstat aggregation query for command='setroubleshootd' and inspect row count, series count, and concurrent PID behavior ... PY`
13. `source "wintap-run.env" && export WINTAP_DBT_DATABASE="${WINTAP_DBT_DATABASE:-$WINTAP_DATA_ROOT/duckdb/wintap.duckdb}" && uv run --dev --project . python - <<'PY' ... execute the command-filtered 'Aggregate by command' pidstat query for command contains 'setroubleshootd' and inspect row count, series count, and elapsed time ... PY`
14. `cd validation/perf-collection && uv run --project . --extra dev pytest`
15. `duckdb -c "select min(RssAnon) as min_rss_anon_kb, max(RssAnon) as max_rss_anon_kb, min(RssFile) as min_rss_file_kb, max(RssFile) as max_rss_file_kb, min(VmRSS) as min_vm_rss_kb, max(VmRSS) as max_vm_rss_kb, min(AnonHugePages) as min_anon_huge_kb, max(AnonHugePages) as max_anon_huge_kb from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_proc_status/**/*.parquet') join read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_smaps_rollup/**/*.parquet') using(time, hostname, pid, process_name, run_id, dayPK, hourPK); select min(open_fd_count) as min_fd, max(open_fd_count) as max_fd, min(mapped_regions) as min_regions, max(mapped_regions) as max_regions from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_fd_map/**/*.parquet');"`
16. `dotnet new console -n "counter_sample"` in `/tmp/opencode`, then `dotnet-counters collect --process-id <sample-pid> --refresh-interval 2 --format json --output /tmp/opencode/counter_sample/counters-json --duration 00:00:06 --counters System.Runtime` and `dotnet-counters collect --process-id <sample-pid> --refresh-interval 2 --format csv --output /tmp/opencode/counter_sample/counters-csv --duration 00:00:06 --counters System.Runtime` to inspect the real export schema used by the new parser`
17. `cd validation/perf-collection && uv run --project . wpc-perf-batch --data-root "/tmp/lintap-perf-user" --pid 743557 --duration-seconds 15 --interval-seconds 5 --run-id "spk16-user-procfs-20260829"`
18. `ls "/tmp/opencode" && dotnet-counters collect --process-id 743557 --refresh-interval 1 --format json --output "/tmp/opencode/dotnet-counters-test" --duration 00:00:05 --counters System.Runtime`
19. `cd validation/perf-collection && bash -n scripts/capture_lintap_perf_for_user.sh`
20. `cd validation/perf-collection && bash scripts/capture_lintap_perf_for_user.sh`
21. `duckdb -c "with smaps as (select * from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_smaps_rollup/dayPK=20260829/hourPK=20/*.parquet')), status as (select * from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_proc_status/dayPK=20260829/hourPK=20/*.parquet')), fd as (select * from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_fd_map/dayPK=20260829/hourPK=20/*.parquet')), counters as (select * from read_parquet('/tmp/lintap-perf/parquet/raw_sensor/perf_dotnet_counters/dayPK=20260829/hourPK=20/*.parquet')) ... summarize row counts, time ranges, first/last/min/max RSS-anon-fd values, and selected counter ranges for run lintap-perf-60m ..."`
22. `ls "/tmp" && RUN_ID=lintap-perf-collect-smoke DURATION_SECONDS=20 INTERVAL_SECONDS=5 DOTNET_COUNTERS_REFRESH_INTERVAL=5 DOTNET_COUNTERS_FORMAT=json WINTAP_DATA_ROOT=/tmp/lintap-perf-collect bash scripts/capture_lintap_perf_for_user.sh` (assistant-run smoke attempt from the noninteractive session; blocked by `sudo` requiring a terminal)`
23. `duckdb -c "describe select * from read_parquet('/tmp/lintap-perf-collect/parquet/raw_sensor/perf_dotnet_counters/dayPK=20260829/hourPK=20/*.parquet'); select count(*) as counter_rows, count(distinct counter_key) as distinct_counter_keys, min(time) as first_time, max(time) as last_time from read_parquet('/tmp/lintap-perf-collect/parquet/raw_sensor/perf_dotnet_counters/dayPK=20260829/hourPK=20/*.parquet'); select counter_provider, counter_name, counter_key, counter_type, counter_tags, value from read_parquet('/tmp/lintap-perf-collect/parquet/raw_sensor/perf_dotnet_counters/dayPK=20260829/hourPK=20/*.parquet') order by time, counter_key limit 40; select count(*) as smaps_rows from read_parquet('/tmp/lintap-perf-collect/parquet/raw_sensor/perf_smaps_rollup/dayPK=20260829/hourPK=20/*.parquet'); select count(*) as status_rows from read_parquet('/tmp/lintap-perf-collect/parquet/raw_sensor/perf_proc_status/dayPK=20260829/hourPK=20/*.parquet'); select count(*) as fd_rows from read_parquet('/tmp/lintap-perf-collect/parquet/raw_sensor/perf_fd_map/dayPK=20260829/hourPK=20/*.parquet');"`

## Manual Checks

- Confirmed that the new DBT gold model `pidstat_process_summary` builds and is included in the schema tests.
- Confirmed that `build_summary`, `telemetry_event_summary`, `file_chart`, and `network_chart` now query successfully against the built DuckDB without first creating the DBT raw-source S3 secret in the direct DuckDB session.
- Confirmed that the Marimo notebook's pidstat availability check no longer relies on mere table existence and handles an empty pidstat dataset without raising a conversion error.
- Confirmed that the registry-model failure caused by mixed `eventtime` types is fixed by the new mixed-schema time macros, and that the same tolerance now covers the analogous host, host_ip, process_file, and process_image_load silver conversions.
- Confirmed that the repo-level uv cleanup works: removing the deprecated `--isolated` Makefile usage, adding `plotly` to dev dependencies for `qa-pidstat`, and rebuilding a broken local `.venv` restores normal `uv run --dev --project . ...` behavior.
- Confirmed that the new pidstat time-series query shape is viable on the current dataset: 1-minute bucketed aggregation over the filtered top processes returned `2811` rows across `12` series in `0.46s`.
- Confirmed that the updated Marimo notebook file compiles cleanly with `python -m py_compile`.
- Confirmed that the revised Plotly-based pidstat panel query shape is also viable when ranking by the selected metric rather than always by CPU; an example Memory % query returned `5845` rows in `0.35s`.
- Confirmed that the new event-volume-by-type comparison query is viable on the current dataset: `5024` rows in `0.33s`, with active series for `process`, `file`, `network`, and `registry` on this dataset.
- Confirmed that the new `By command` aggregation mode behaves as intended for repeated-instance families like `setroubleshootd`: the command-level query returned `380` rows in `0.27s`, collapsed to `1` visible series with concurrent-PID counts preserved per bucket.
- Confirmed that the command substring filter works with aggregation mode: filtering for `setroubleshootd` still returns the expected single command-family series (`380` rows in `0.27s`).
- Confirmed that the new manual-batch performance collection package passes its current parser/output tests (`8 passed`), including `dotnet-counters collect` JSON parsing, CSV parsing, and a fake-collector end-to-end parquet write.
- Confirmed from the existing on-host `/tmp/lintap-perf` parquet that the sampled `Lintap` RSS remains overwhelmingly anonymous/private rather than file-backed: `RssAnon` ranged `2060344..2112368` kB while `RssFile` stayed flat at `169448` kB, and `AnonHugePages` stayed flat at `1177600` kB across the sampled window.
- Confirmed from the existing on-host `/tmp/lintap-perf` parquet that FD and mapping context stayed relatively stable during that 5-minute window (`open_fd_count=485..487`, `mapped_regions=4776..4787`), which weakens the simple "runaway mmap/fd count" explanation for that slice.
- Confirmed from a temporary sample .NET process under `/tmp/opencode` that `dotnet-counters collect` emits robust file-oriented output in both supported formats: JSON contains a top-level `Events` array with provider/name/tags/value fields, and CSV contains stable `Timestamp,Provider,Counter Name,Counter Type,Mean/Increment` columns. The new parser handles both shapes.
- Confirmed that user-level live collection on `spk16` is permission-limited against the root-owned `Lintap` service: a direct `wpc-perf-batch` run could still read `/proc/<pid>/status` and write `perf_proc_status`, but `/proc/<pid>/smaps_rollup` and `/proc/<pid>/fd` returned `Permission denied`.
- Confirmed that user-level `dotnet-counters` attach against the live root-owned `Lintap` process currently fails on `spk16` with `ServerNotAvailableException: Unable to connect to the server. Permission denied`.
- Confirmed that the new focused escalation wrapper parses cleanly with `bash -n` and is now wired to auto-enable file-based `dotnet-counters collect` rather than terminal-scraping `monitor` output.
- Confirmed that the previously validated root-wrapper path on `spk16` still provides the intended host workflow for `smaps`/`status`/`fd` capture and file ownership handoff. The new collect-based `.NET` path still needs one fresh host rerun after this code change.
- Confirmed from the fresh root-wrapper run that the fixed `smaps_rollup` parser works on live host data: the new parquet schema contains only the expected memory metrics and no bogus address-range/header column.
- Confirmed from the fresh root-wrapper run that current `Lintap` memory remains dominated by anonymous/private pages rather than file-backed RSS: `VmRSS` ranged `2405416..2452760` kB, `RssAnon` ranged `2125524..2172868` kB, `RssFile` stayed flat at `169448` kB, `Anonymous` ranged `2130236..2176124` kB, and `AnonHugePages` ranged `1208320..1292288` kB.
- Confirmed from the fresh root-wrapper run that FD/mapping context still looks relatively stable over the sampled window (`open_fd_count=485..487`, `mapped_regions=4770..4791`, `writable_private_regions=1276..1287`) rather than showing a simple runaway descriptor/mmap pattern.
- Confirmed from the previously validated structured `perf_dotnet_counters` parquet that the live root-wrapper path can yield machine-queryable runtime metrics on `spk16`; the new code now replaces that monitor-derived path with `dotnet-counters collect` for future runs.
- Confirmed that the root wrapper returned ownership of the fresh parquet to the normal user on `spk16`; the new files under `/tmp/lintap-perf/parquet/raw_sensor/perf_{smaps_rollup,dotnet_counters}/dayPK=20260829/hourPK=18/` are owned by `johnson30:johnson30`.
- Confirmed that the hour-long idle-host baseline run `lintap-perf-60m` completed successfully on `spk16`: `714` rows each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`, spanning `2026-08-29T19:01:21Z -> 2026-08-29T20:01:17Z`.
- Confirmed from that 60-minute idle baseline that RSS did not continue ratcheting upward across the hour. `smaps.Rss` moved from `2421536` kB to `2389236` kB with a range of `2338784..2427740` kB, while `status.VmRSS` moved from `2419140` kB to `2386360` kB with a range of `2333716..2423212` kB.
- Confirmed that anonymous/private memory still dominates that idle baseline, but it also drifted downward rather than monotonically upward: `Anonymous` moved from `2141500` kB to `2109196` kB (`2058748..2147700` kB), `RssAnon` moved from `2139248` kB to `2106472` kB (`2053832..2143316` kB), and `AnonHugePages` moved from `1218560` kB to `1179648` kB (`1171456..1259520` kB).
- Confirmed that FD/mapping counts stayed broadly stable across the idle baseline as well: `open_fd_count` `486 -> 487` (`486..494`) and `mapped_regions` `4771 -> 4782` (`4765..4838`).
- Confirmed that the old monitor-derived `.NET` path was not reliable for long captures, which is why it was replaced: the hour-long historical monitor run kept a full raw stream but only partial structured rows because screen-rewrite output collapsed multiple updates into ANSI-heavy composite lines.
- Confirmed that an assistant-run live smoke of the new collect-based root wrapper could not be completed from this noninteractive session because `sudo` on `spk16` requires a terminal/password prompt. That is an execution-environment limitation of this session, not a parser/test failure.
- Confirmed that the new collect-based root-wrapper smoke now succeeds on the real root-owned `Lintap` process when run interactively on `spk16`: `/tmp/lintap-perf-collect/parquet/raw_sensor/perf_dotnet_counters/dayPK=20260829/hourPK=20/` contains `108` structured rows across `27` distinct counter keys, spanning `2026-08-29T20:36:46Z -> 2026-08-29T20:37:00Z`, alongside `4` matching rows each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`.
- Confirmed from that collect-based host smoke that the new runtime schema is the intended durable shape: fields include `counter_provider`, `counter_name`, `counter_key`, `counter_type`, `counter_tags`, and numeric `value`, with real `System.Runtime` counters such as `system_runtime_working_set_mb`, `system_runtime_gc_heap_size_mb`, `system_runtime_gc_committed_bytes_mb`, `system_runtime_allocation_rate_b_5_sec`, `system_runtime_cpu_usage`, and GC generation-size/rate counters.
- Confirmed that the collect-based one-hour rerun on `spk16` now yields durable long-run runtime telemetry: the new `hourPK=21` parquet contains `9720` `perf_dotnet_counters` rows across `27` counter keys for `2026-08-29T20:41:27Z -> 2026-08-29T21:41:16Z`, alongside `714` matching rows each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`.
- Confirmed from that collect-based one-hour rerun that RSS and anonymous memory again stayed within a bounded band rather than obvious monotonic runaway growth: `smaps.Rss` moved `2389332 -> 2420164` kB (`2313792..2433876`), `status.VmRSS` moved `2387040 -> 2416260` kB (`2308556..2428896`), `Anonymous` moved `2109032 -> 2140112` kB (`2033484..2153568`), and `AnonHugePages` drifted down overall (`1181696 -> 1089536` kB, min `1026048`, max `1181696`).
- Confirmed that FD/mapping counts remained broadly stable during the collect-based one-hour rerun as well: `open_fd_count` `485 -> 486` (`485..488`) and `mapped_regions` `4757 -> 4768` (`4756..4866`).
- Confirmed that the collect-based runtime counters now cover the full hour cleanly. Example counters for the rerun: `system_runtime_working_set_mb` `2384.674816 -> 2471.87456` (`2361.073664..2483.658752`), `system_runtime_gc_heap_size_mb` `541.854024 -> 659.104768` (`377.130016..1073.363888`), `system_runtime_gc_committed_bytes_mb` `1252.22912 -> 1254.89152` (`1228.017664..1318.354944`), `system_runtime_cpu_usage` `17.97 -> 19.49` (`12.06..23.06`), and `system_runtime_threadpool_queue_length` stayed `0` throughout.
- Confirmed an operator hygiene issue from that rerun: the new collect-based hour-long run reused the historical `run_id` value `lintap-perf-60m`, which makes naive cross-partition queries accidentally blend the earlier monitor-era run with the newer collect-based rerun. Query by explicit path/hour partition or use unique `RUN_ID`s for future comparisons.
- Confirmed from aligned collect-based one-hour samples that Lintap CPU stayed moderately busy even on the mostly idle host (`avg ~= 19.0%`, `min ~= 12.9%`, `max ~= 23.1%`) but only had weak-to-moderate correlation with memory (`corr(cpu, working_set) ~= 0.31`, `corr(cpu, gc_heap) ~= 0.26`, `corr(cpu, rss) ~= 0.28`, `corr(cpu, anonymous) ~= 0.28`). By contrast, runtime working set and OS RSS tracked each other very closely (`corr(working_set, rss) ~= 0.93`).

## Results

- `make dbt-build` passed: `PASS=78 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=78`.
- `make dbt-test` passed: `PASS=39 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=39`.
- Direct built-DuckDB query smoke succeeded for:
  - `build_summary`
  - `telemetry_event_summary`
  - `file_chart`
  - `network_chart`
  - `perf_chart`
  - `pidstat_process_summary`
  - the notebook's pidstat summary query
  - the notebook's top-pidstat query
- Current smoke dataset results:
  - `pidstat_metrics` rows: `0`
  - `pidstat_process_summary` rows: `0`
  - `perf_chart` rows: `0`
  - `file_chart` rows: `901`
  - `network_chart` rows: `234`
- This confirms the first-slice structural cleanup is working, including the key runtime improvement: the canonical QA monitoring queries no longer require raw-backed bronze/S3 access just to open the built DuckDB and query the monitoring layer.
- Follow-up hotfix result: a direct targeted `dbt run` of `process_registry` and related dependent models now succeeds where it previously failed with `Conversion Error: Unimplemented type for cast (TIMESTAMP -> BIGINT) when casting from source column EventTime`.
- Full `make dbt-build` re-run after the hotfix also passed successfully in `129.86s` with `PASS=78 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=78`.
- uv environment recovery result: `.venv/bin/` had been empty, so `uv add` and other project-environment commands were failing. After `make rebuild-venv`, `uv sync --all-extras --dev` completed successfully and `uv run --dev --project . python -c "import plotly, marimo"` passed (`plotly==7.0.0`).
- Pidstat time-series proof point: with real pidstat rows now present, the filtered query backing the new chart returned `2811` bucketed rows for the top `12` process series at a `25%` peak-CPU cutoff. Example high-signal series included `spk16 | Lintap | 743557` with sustained CPU values over the bucketed window.
- Pidstat UX follow-up: the notebook now uses Plotly for the pidstat time-series panel, ranks and filters processes by the selected metric rather than always by peak CPU, adds a host filter, and exposes a range slider for full-width interactive exploration.
- Correlation view added: the pidstat section now includes a second Plotly chart showing 1-minute event counts by type over time from the normalized event-family tables, intended for visual comparison against the pidstat process-resource chart.
- Aggregation-mode follow-up: the pidstat chart now supports both `Per process` and `By command` views. For `setroubleshootd` on the current dataset, command aggregation produces a clean family-level series while still exposing concurrent PID counts in hover.
- Polish follow-up: the pidstat control row now exposes clearer labels (`Per process instance`, `Aggregate by command`) plus a `Command contains` filter, and the event-volume subplot stack now uses a bottom-axis range slider so its time-navigation behavior is closer to the pidstat chart above.
- Manual-batch instrumentation slice landed in this repo under `validation/perf-collection/`: a Linux `/proc` collector writes `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map` rows into canonical raw-style parquet partitions, file-based `.NET` runtime capture now writes structured `perf_dotnet_counters`, and optional external stdout capture remains available for future `perf_lintap_diag_raw` experimentation.
- Collector hardening follow-up: the `smaps_rollup` parser now ignores the address-range header line that previously leaked into parquet as a bogus column, and the `.NET` path now uses `dotnet-counters collect --format json|csv` instead of terminal scraping.
- Live-host constraint on `spk16`: direct unprivileged `/proc` and `.NET` diagnostics access to the root-owned `Lintap` service is still blocked, but the new focused root-wrapper path is now validated and provides the intended operator workflow for collecting fresh readable parquet without broader host permission changes.
- Root-owned-service operator path: `validation/perf-collection/scripts/capture_lintap_perf_for_user.sh` now provides the narrow escalation path for this host by running the capture as `root` and returning file ownership to the invoking user afterward.
- Idle-baseline result on `spk16`: with the machine mostly quiet, the one-hour run did not show continued upward ratcheting. That strengthens the earlier suspicion that burst-correlated workload windows matter more than simple time-since-start or unavoidable idle background drift.
- Runtime-counter design update: the old `dotnet-counters monitor` caveat has been addressed in code by replacing that path with file-based `dotnet-counters collect` parsing. A fresh host rerun is still needed to replace the old monitor-derived host artifacts.
- Runtime-counter design update: the old `dotnet-counters monitor` caveat has now been addressed both in code and in a real host smoke. Future runs should rely on `dotnet-counters collect` output rather than any terminal-derived path.
- Runtime-counter design update: the collect-based one-hour rerun confirms the new path stays structured across the full capture window rather than collapsing after initial samples the way the old monitor-derived path did.

## Known Gaps

- The current configured dataset/window still contains no pidstat parquet, so the new pidstat gold path is structurally verified but not yet validated with non-empty pidstat data.
- `file_chart` now buckets on `process_file.min_event` as a first-slice silver-based replacement for raw file-event timing. This removes the raw-backed dependency, but timeline fidelity versus raw file event times remains a follow-up question.
- Legacy Analytics-side Streamlit/DataQA alignment is not part of this first coding slice yet.
- The mixed-schema time hotfix has only been validated through DBT execution on the current dataset mix; there is not yet a dedicated model-level regression test specifically for timestamp-typed versus numeric-typed `eventtime` inputs.
- `qa-pidstat` still points at the legacy `../Lintap/teletap/grokdata_marimo.py` path; the uv cleanup makes its dependency resolution saner, but that target remains legacy-oriented rather than part of the canonical Marimo QA flow.
- The new pidstat chart is intentionally simple: one metric at a time, 1-minute buckets, filtered by minimum peak CPU and capped by max series count. It does not yet include richer focusing tools such as legend-based hiding, host/container selectors, or anomaly-centric ranking.
- The chart is still intentionally first-pass despite the UX upgrade: it supports host filtering, command substring filtering, and selected-metric ranking now, but still lacks container-only toggles and explicit anomaly-focused ranking modes.
- `By command` aggregation currently sums the selected metric across matching processes within a bucket. That is useful for total family footprint, but future UX may also want `average per instance` or `max instance` aggregation modes.
- The event-volume chart currently uses one normalized count strategy per event family (`num_process_start + num_process_stop`, `event_count`, `total_events`, etc.). If a stricter cross-family notion of "event volume" is needed later, that definition should be made explicit and possibly promoted into a dedicated monitoring model.
- The pidstat and event-volume charts still do not share truly linked zoom because they remain separate Plotly figures; the current improvement is comparable interaction style rather than synchronized navigation.
- Live-host follow-up on `spk16`: direct unprivileged access to the root-owned `Lintap` service is still restricted for `smaps_rollup`, `fd`, and `.NET` diagnostics, but the focused root-wrapper path is now validated and provides a working way to collect fresh readable parquet for those signals.
- Future long runs should use a unique `RUN_ID` each time so collect-based and historical monitor-era captures cannot be merged accidentally in downstream DuckDB queries.

## Follow-Ups

- Re-run the same verification against a dataset/window with actual `raw_sensor/pidstat` parquet so `pidstat_metrics`, `pidstat_process_summary`, and `perf_chart` are exercised with non-empty data.
- Consider a second iteration on the pidstat chart UX: container-only narrowing, alternate bucket sizes, or anomaly-focused ranking modes beyond the current peak-selected-metric rule.
- Consider whether `By command` should grow additional aggregation styles (`sum`, `average`, `max`) now that the basic family-level series pattern is validated.
- Consider whether the event-volume correlation chart should stay notebook-only or be promoted into a named monitoring view if it becomes a stable QA concept.
- If linked navigation becomes important, consider collapsing the two charts into a single multi-row Plotly subplot figure so zoom/pan is naturally shared.
- Decide whether `file_chart` and possibly `network_chart` need a later chart-specific detail contract for higher-fidelity timelines.
- Run the new `validation/perf-collection` tooling on a Linux host against a real `Lintap` process, confirm parquet lands under `raw_sensor/perf_*`, and decide which of the provisional raw event types should be promoted from manual-batch usage to long-term sidecar collection.
- Continue with the later feature slices: broader event-family cleanup and Analytics-side conflict handling.
- Use the new focused root wrapper on `spk16` for the next live run instead of trying to broaden general host permissions for `/proc` or .NET diagnostics.
- Compare this collect-based one-hour rerun against a future intentionally file-heavy perturbation run, using distinct `RUN_ID`s, to see whether `gc_heap_size_mb` and `working_set_mb` climb in lockstep with the workload-linked RSS stairs or whether RSS outpaces managed-heap growth.
