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
last_validated: 2026-08-31
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

### Serializer Cadence Prediction

Before implementation: set only `FileSerializationIntervalSec` to `5` seconds,
leaving the 10,000-event cap and all other serializer intervals unchanged. The
observed FileOps post-aggregation rate should then fit below the cap within each
five-second interval, eliminating `fileserializer` backlog-drop warnings while
preserving event count/byte semantics. The host smoke must fail if any new
`fileserializer: in-memory backlog limit reached` line appears after its start
  marker.

### Serializer High-Water Prediction

Before implementation: request one non-overlapping FileSerializer drain when
queue depth reaches `5000`, retaining the five-second timer and 10,000-event
cap. The 5,000-row margin should absorb the observed burst arrival while the
worker begins its fast drain, eliminating cap warnings without reducing event
fidelity or creating periodic small files during idle operation. A controlled
high-cardinality workload must produce zero serializer drops and retain
FileOps count/byte conservation.

The high-water validation must include at least one
`serializer_flush trigger=high_water` record. A clean no-drop result without
that marker does not exercise the new burst path.

### FileOps Deny Policy Prediction

Before implementation: an empty deny list leaves FileOps behavior unchanged.
For an explicitly configured exact Linux `comm` rule, each matched covered
operation will increment one kernel `policy_suppressed_attempts[rule,op]`
counter and return before ring-buffer reservation; matching work therefore will
not contribute to ring pressure, sender backlog, or FileOps parquet. Nonmatching
work must retain its current telemetry semantics. The metric is a policy-gate
count of covered syscall attempts, not a claim about all filesystem activity by
a vendor product.

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

24. `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter "FullyQualifiedName~FileOpsAggregatorTests|FullyQualifiedName~SerializerScheduleTests"`
25. `dotnet build wintap/Lintap.csproj`
26. `python3 devtools/file_capture_smoke_test.py --data-root /var/log/lintap --timeout 120 --poll-interval 2 --require-no-serializer-drops --serializer-observation-seconds 70`
27. `python3 devtools/file_capture_smoke_test.py --data-root /var/log/lintap --timeout 180 --poll-interval 2 --unique-file-count 6000 --require-no-serializer-drops --serializer-observation-seconds 70`
28. `make build_ebpf`
29. `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter "FullyQualifiedName~FileOpsAggregatorTests|FullyQualifiedName~FileOpsDenyPolicyTests|FullyQualifiedName~SerializerScheduleTests"`
30. `duckdb -c "..."` over the four explicit
    `lintap-perf-20260830-no-tenable` parquet files plus DuckDB regex parsing of
    `/var/log/lintap/Logs/Lintap.log` for `2026-08-30 14:49:06-15:49:05 PDT`;
    calculated first/last/range/half-average/linear-slope resource metrics,
    FileOps and serializer fidelity totals, maintenance timing, and aligned
    queue/resource correlations against `lintap-perf-20260830-tenable-filter`.
31. `dotnet run --project diagnostics/nesper-repro/nesper-repro.csproj --
    --benchmark --events 100000 --cardinality 10000 --rounds 3 --scenario
    <scenario>` for `baseline-no-epl`, `file-cast`, `file-native-enum`,
    `file-cast-plus-broad`, `file-cast-outbound-1`, both concurrent-expiry
    variants, and both context variants.
32. `dotnet build wintap/Lintap.csproj`
33. `dotnet run --project diagnostics/nesper-repro/nesper-repro.csproj`
34. `dotnet run --project diagnostics/nesper-repro/nesper-repro.csproj --
    --cache-benchmark --operations 100000 --keys 10000 --capacity 10000
    --miss-penalty-us 1`
35. `dotnet run --project diagnostics/nesper-repro/nesper-repro.csproj --
    --cache-benchmark --operations 20000 --keys 50000 --capacity 32768
    --miss-penalty-us 250`
36. `dotnet run --project diagnostics/nesper-repro/nesper-repro.csproj --
    --cache-benchmark --operations 2000 --keys 1000 --capacity 1000
    --miss-penalty-us 5000`
37. `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter
    "FullyQualifiedName~BoundedEventTimeCacheTests|FullyQualifiedName~ProcessResolverTests|FullyQualifiedName~FileOpsAggregatorTests|FullyQualifiedName~FileOpsDenyPolicyTests|FullyQualifiedName~SerializerScheduleTests"
    --no-restore`

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
- Intermediate runtime-counter state: the old `dotnet-counters monitor` caveat
  had been addressed in code, but a fresh host rerun was still pending at that
  point. The next two entries close that historical gap.
- Runtime-counter design update: the old `dotnet-counters monitor` caveat has now been addressed both in code and in a real host smoke. Future runs should rely on `dotnet-counters collect` output rather than any terminal-derived path.
- Runtime-counter design update: the collect-based one-hour rerun confirms the new path stays structured across the full capture window rather than collapsing after initial samples the way the old monitor-derived path did.
- Confirmed that the first CPU-observability code slice builds for Linux: the
  serializer now rejects overlapping timer flushes, emits per-flush drain/
  duration/backlog diagnostics, and groups queued messages in one pass rather
  than repeated list scans/removals. No queue-drop policy or sensor fidelity
  setting was changed.
- Confirmed that FileOps now reports FD-cache PID/entry cardinality and
  aggregation flush count/average/max duration in its existing 60-second log
  record. Cache/upload cycles and process-resolver maintenance now emit elapsed
  time plus their relevant cardinality context.
- Implemented the predicted FileSerializer-only cadence change:
  `FileSerializationIntervalSec` defaults to `5` seconds, while the existing
  `SerializationIntervalSec=60` remains the cadence for every other serializer.
  The 10,000-event cap remains a safety backstop, and older deployed ETL configs
  that lack the new property also default to five seconds.
- Added `SerializerScheduleTests` and extended the existing parquet-based file
  smoke test with `--require-no-serializer-drops` plus an explicit post-capture
  log-observation period. The smoke must find generated file activity and see no
  new FileSerializer backlog-drop line after redeploy.
- Implemented the second prediction slice: FileSerializer requests one
  non-overlapping immediate drain at `FileSerializationHighWaterEvents=5000`.
  The five-second timer and 10,000-event cap remain in place. High-water drains
  log `serializer_flush trigger=high_water`; the smoke can now generate a
  configurable high-cardinality burst using `--unique-file-count`.
- Implemented the generic opt-in kernel FileOps exact-`comm` deny policy. An
  empty `FileOpsDenyComms` configuration leaves behavior unchanged. Configured
  exact names install into both FileOps tracer tiers after object load; each
  matching operation increments a pre-ring `policy_suppressed_attempts` counter
  by rule and operation. A configured policy whose maps cannot be installed
  fails FileOps startup rather than silently collecting without the policy.
- Policy parser tests cover empty configuration, exact deduplication, Linux
  `comm` length rejection, and bounded rule count. Both CO-RE and fallback
  tracers compile with the new maps and gate.
- CPU-unit naming update: raw pidstat `cpu_percent` remains compatible, while
  the normalized model now exposes `cpu_core_percent`, gold exposes
  `max_cpu_core_percent` / `avg_cpu_core_percent`, and the canonical dashboard
  labels it `CPU (core-summed %)`. Lintap and Wintappy user-facing READMEs
  explain conversion to host-normalized CPU by dividing by logical CPU count.
- Critical live-host result: `/var/log/lintap/Logs/Lintap.log` shows the active
  `fileserializer` 10,000-event cap dropping newest file events continuously,
  reaching at least `394529` drops by `17:25:13 PDT`. File flushes repeatedly
  drained exactly 10,000 events in `2..19 ms`, with `skipped_overlap=0` and
  `parquet_backlog=1`; the immediate fidelity defect is admission/batch cadence,
  not slow flush CPU.
- FileOps sender drops remained `0` and aggregation `cap_bypass` remained `0`.
  FD-cache state nevertheless grew from `pids=20,entries=24` at `16:38:19 PDT`
  to `pids=1439,entries=1784` at `18:04:37 PDT`, validating the cache-growth
  hypothesis. Cache cycles remained `1.9..6.0 s`; resolver maintenance settled
  around `8.6..13.3 s` every five minutes after startup.
- Regression check: the deployed `/usr/lib/lintap/esper/file.epl` and
  `tracers/file_ops_tracer.bpf.o` SHA-256 hashes exactly match the current
  source. The deployed EPL includes the recently fixed `AgentId` grouping,
  excluding the historical n-squared Esper event-count inflation defect as the
  explanation for this capture. The FileOps `repeats_folded` counters are
  positive, while aggregation cap bypass is zero, proving aggregation is active
  but only folds repeat `(pid,path,operation)` keys inside its one-second window.
  The 10,000-event serializer cap was introduced in June, before this week's
  fop-11/fop-12/fop-13 work.

## Current Gaps

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
- The historical identity cache passed 10h23m plus controlled recovery, but
  higher-churn hosts, queue-age percentiles, and rare multi-second resolution
  stalls remain uncharacterized.
- The retrieved pidstat closes CPU/RSS/I/O trends for the overnight run, but
  smaps composition, GC, process-FD, and map-count coverage was not collected.
- FileOps FD-path state remained unbounded in the validated implementation;
  conservative process-exit plus age/capacity eviction is the active next code
  slice.
- Owning sibling-repo changes are now durably anchored. Canonical owning
  changes are at `../wintap@c03d731..2d3f795`,
  `../Lintap@1b23f77`, and `../Wintappy@a53cce6..e4b3bc3`.

## Field Validation Timeline

The entries below preserve chronological outcomes, including failed or
superseded gates. They are evidence history, not current instructions.

- Initial DBT smoke used a dataset with zero pidstat rows. Later notebook and
  overnight S3-pidstat runs exercised non-empty pidstat data; the original zero-
  row observation is no longer a current gap.
- Live policy validation passed under the active weekly scan with
  `WINTAP_FILEOPS_DENY_COMMS=tenable-utils-L`. The policy suppressed
  `dir_open=114102` then `117327` attempts per 60-second interval. FileOps
  sender depth was only `853` then `192`, with `drops=0`, `cap_bypass=0`, and
  `summary_enqueue_fail=0`, in contrast to the previous 524288-entry sender
  saturation. Non-policy FileOps telemetry continued to emit.
- Filtered one-hour capture `lintap-perf-20260830-tenable-filter` ran from
  `2026-08-30T19:13:55Z` through `20:13:54Z` with `714` procfs samples. The
  policy remained active and no FileOps sender drops, aggregation cap bypass,
  summary enqueue failures, or FileSerializer backlog warnings appeared in the
  capture window. Runtime CPU averaged `22.4%` host-normalized (`1.94..31.44%`),
  equivalent to about `7.2` core-summed CPUs on the 32-core host.
- This run is a no-loss policy validation but not a clean CPU/memory baseline:
  a Wintappy DBT build overlapped its latter half and coincided with FileOps
  sender depth rising into the hundreds of thousands without reaching loss.
  Runtime working set half-averages rose `1543.76 -> 1775.22 MB`, GC heap
  `274.05 -> 350.42 MB`, and CPU `19.39 -> 25.41%`; RSS ranged
  `1429840..2428548 kB`. FD count remained `487..495`.
- High-water redeploy result: the controlled `--unique-file-count 6000` smoke
  passed. The deployed log shows `serializer high-water flush threshold=5000`,
  18 high-water drain requests, and matching `trigger=high_water` drains of
  about 5,000 rows each. Drains took `2..16 ms` except one `86 ms` outlier;
  all had `skipped_overlap=0` and left only `2..542` rows queued. No new
  FileSerializer backlog-limit warning appeared after the smoke marker. This
  validates the high-water prediction for the controlled burst.
- Post-redeploy result: the no-drop smoke passed its bounded observation window
  and the log confirms `fileserializer: serializer flush interval=5s`. The
  strict prediction nevertheless failed under early live bursts: the serializer
  again reached 10,000 at `18:59:52` and `19:03:12 PDT`, with cumulative drops
  of `1` then `434`. This is a large improvement over the prior hundreds of
  thousands of drops, but it is not acceptable as a no-loss result. The next
  design must request an immediate flush below the cap during a burst rather
  than only shorten the periodic interval further.
- The planned post-Tenable comparison completed; the result below supersedes
  the expectation that it would be a quiet-host baseline.
- The requested follow-up, `lintap-perf-20260830-no-tenable`, completed over
  `2026-08-30T21:49:06Z -> 22:49:05Z` with `715` samples in each procfs stream
  and `9720` runtime-counter rows. It is not a quiet/no-loss baseline: every
  FileOps policy summary reported `suppressed_attempts=0`, but sender depth was
  already `524148` at the first matching summary and stayed near its `524288`
  cap (`513561..524223`, average `523313`). The hour recorded `601126` sender
  drops and `192774` summary enqueue failures; aggregation cap bypass remained
  zero.
- FileSerializer passed its own gate during that failed upstream run: zero
  backlog warnings, `385` non-empty flushes (`26` high-water), `654769` rows
  drained, maximum `170` rows remaining, maximum `3 ms` drain time, and zero
  overlap. This localizes the fidelity failure to the FileOps sender boundary,
  not Parquet serialization.
- Within the cap-bound hour, memory was stable: `smaps.Rss 2013792 -> 2015180
  kB` (range `1959768..2041840`, half means `2011872 -> 2013742 kB`) and
  runtime working-set half means `2057.61 -> 2058.42 MB`. CPU remained high but
  flat-to-declining (`30.82%` host-normalized average, half means `31.12% ->
  30.52%`), equivalent to about `9.86` core-summed CPUs on this host.
- The apparent `AnonHugePages 849920 -> 1169408 kB` rise was not net RSS growth:
  total anonymous memory rose only `1052 kB`. GC heap endpoints were also
  misleading (`523.90 -> 765.95 MB`) because the sawtooth range was
  `258.78..778.25 MB`; heap half means differed by only `9.37 MB`, thread-pool
  queue length stayed zero, and total GC pause time was `7.30 s`.
- The internal FileOps FD cache continued to grow (`pids 3146 -> 4052`, entries
  `3890 -> 4899`) while process FDs stayed `487..490`. ProcessResolver's 12
  maintenance cycles averaged `9.70 s`. These remain independent long-run
  state/CPU concerns even though process RSS did not ratchet during the hour.
- Post-window review refines the earlier filtered-run result: that capture was
  loss-free in its exact hour, but sender depth rose `7860 -> 338592`, reached
  its first drop at `13:36:36 PDT` about 23 minutes later, and never recovered.
  During the filtered hour, aligned queue depth correlated with RSS at `r=0.749`
  and anonymous memory at `r=0.748` (`r=0.583` with runtime working set, only
  `r=0.191` with GC heap). This supports bounded sender-backlog occupancy as a
  material contributor to the earlier memory climb, without proving causality
  because the DBT workload remains a confounder.
- Sender/Esper benchmark result: current production-shaped `file.epl` sustained
  a median `178756` synthetic input events/s after warm-up with exact event and
  byte conservation. The no-EPL baseline was `538882/s`. The live sender's
  `5135.7 us` mean sampled call time implies only `194.7/s`, while the same hour
  recorded `425815` process-cache misses (`118.3/s`). Esper statement evaluation
  alone therefore does not explain the live ceiling; synchronous historical
  process resolution is the leading target.
- Esper alternatives were not promoted: one outbound listener thread was
  effectively unchanged (`176280/s` median), native enum literals were slightly
  slower (`162381/s`), and the context-based aggregation pattern reduced input
  throughput to about `51716/s` and failed exact event-count conservation under
  concurrent boundary stress. Concurrent `time_batch` expiration did reduce
  ingress throughput (`83925/s` median), confirming contention but not a safe
  replacement design.
- The broad all-event subscriber statement reduced isolated throughput to
  `62785/s`. The live host had zero plugins but still deployed it because ETL
  was enabled. `PluginManager` now deploys that statement only when subscriber
  plugins exist. The dormant native-enum formatter was also corrected to use
  NEsper's `$` nested-type syntax, but remains disabled.
- Post-change verification passed: `dotnet build wintap/Lintap.csproj` completed
  with 0 errors (existing warnings remain), the default NEsper compile/deploy
  repro passed all six queries, the focused FileOps/policy/serializer suite
  passed `22/22`, and all accepted benchmark variants preserved exact
  represented event counts and bytes. The rejected concurrent context scenario
  intentionally remains recorded as a fidelity failure.
- Implemented the process-attribution follow-on as a 32,768-entry bounded LRU
  of closed process identities. Lookups require the event timestamp to fall in
  the cached create/exit interval and choose the newest matching instance for
  overlapping PID histories. Open rows are not cached. Retention seeds the
  cache before deleting rows and the maintenance-triggering lookup retries it,
  protecting delayed File events beyond the one-hour durable retention window.
- Resolver SQL for event-time lookup, direct/pending Stop, and startup/runtime
  reconciliation now uses timestamp parameters rather than whole-second string
  formatting. Resolver-level tests prove two PID instances within one second
  resolve correctly and that a first lookup which triggers retention deletion
  still receives the deleted row's identity.
- Cache tests passed for interval boundaries, PID reuse, overlapping intervals
  in both insertion orders, identity updates, LRU eviction, 100,000 concurrent
  reads, disabled mode, and clear/reset behavior. The combined focused suite
  passed `39/39`.
- Simulated cache-load results: raw cache hits sustained about `4.94M/s` for a
  10k-entry working set. With a synthetic 5 ms durable miss penalty, throughput
  was approximately `200/s` at 0% hits, `400/s` at 50%, `799/s` at 75%,
  `1995/s` at 90%, and `1.06M/s` at 100%. A 50k-key population against the
  production 32,768 cap evicted exactly 17,232 oldest entries and remained at
  its configured bound.
- FileOps one-in-64 sender diagnostics now report average and maximum total,
  process-resolution, health-check, and Esper durations from one atomically
  snapshotted sample set. Historical identity-cache hits, misses, entries, and
  evictions appear beside the existing active-process-cache counters.
- Independent review found no remaining deployment-blocking correctness or
  event-time fidelity issue after adding the post-maintenance cache retry,
  newest-overlap selection, retention pre-seeding, sub-second timestamp
  parameters, and atomic timing snapshots. Deployment was then performed by the
  operator because this session cannot perform passworded `sudo`.
- Operator deployed RPM `lintap-0.3.4-1.el8.x86_64`; installed
  `/usr/lib/lintap/Lintap.dll` SHA-256 `7bd7ab38...` matched the RPM publish
  payload. Service PID `3322161` started at `20:54:30 PDT`. Startup logged
  historical identity-cache capacity `32768`, plugin count `0`, and no broad
  `Creating Subscriber EPL` statement.
- The first deployed ten-minute gate passed across ten FileOps summaries:
  queue depth `0..1889` (`1 -> 152`, then `100` in the next interval), maximum
  interval high-water `13917`, and zero sender drops, summary enqueue failures,
  aggregation cap bypass, or historical-cache evictions. Historical-cache
  totals were `32700` hits and `6837` misses (`82.7%` hit rate), with `8750`
  entries at the tenth interval.
- Weighted sampled sender time was `449.7 us`, a `91.2%` reduction from the
  prior `5135.7 us`. Resolution accounted for `445.1 us`; Esper averaged only
  `2.7 us`. Maximum sampled sender/resolve times were `56.5/56.5 ms`, so rare
  durable/maintenance stalls remain visible despite the large average gain.
- FileSerializer remained healthy over the gate: `63` non-empty flushes,
  `28` high-water drains, `221668` rows drained, maximum `291` rows remaining,
  maximum `14 ms` drain, one safely skipped overlap, and zero backlog warnings,
  worker errors, or File send errors. Current fileserializer Parquet continued
  to materialize; the post-merge directory held ten recent files with `33647`
  rows over `21:04:53-21:05:53 PDT`.
- Extended passive validation continued on the same PID for 10h23m despite the
  SSH control connection dropping. Across `617` FileOps summaries, queue depth
  was `0..17387` (average `5205.5`), maximum interval high-water was `38707`,
  and sender drops, summary failures, and aggregation cap bypass remained zero.
- The cache stayed bounded at `32768` entries while processing `1667417` hits
  and `542811` misses (`75.4%`) with `394252` evictions. Weighted sender,
  resolution, and Esper averages were `560.6`, `547.1`, and `12.0 us`.
  Full-hour hit rate remained `68.2%..83.0%` and sender averages `482..673 us`,
  showing no degradation trend under sustained eviction churn.
- Passive FileSerializer evidence covered `11208824` drained rows through
  `3447` non-empty flushes (`1260` high-water), maximum remaining depth `353`,
  maximum duration `218 ms`, four safely skipped overlaps, and zero warnings or
  errors.
- The post-baseline `--unique-file-count 6000` smoke passed with all five file
  activities. It drove sender interval high-water to `71802` with zero loss;
  queue depth fell from `8590` to `5416` in the next interval, below the
  pre-burst value. Later natural bursts remained below the passive maximum.
- Limitation: the operator selected logs/Parquet-only monitoring, and no current
  overnight pidstat files were present. CPU, RSS, GC, FD, and map slopes were
  therefore not measured in this run.
- The operator retrieved S3 pidstat as
  `/tmp/spk16-lintap-pidstat-overnight-1m.parquet` (SHA-256
  `17e19df37746f2cb5f2126e79d6199c1ddecae2759e17f0c08bbc20d8b883230`),
  containing 626 passive and 7 burst/recovery minute rows. This closes CPU/RSS/
  I/O trends but not smaps, GC, process-FD, or map-count coverage.
- Passive pidstat CPU averaged `10.12%` host-normalized (`323.8%` core-summed),
  with post-22:00 slope only `+0.124` host percentage points/hour. Controlled
  burst CPU averaged `10.44%`. CPU therefore remained broadly stable and far
  below the prior saturated run's `30.82%` host-normalized average.
- Passive RSS grew `443452 -> 1911876 kB`, with large startup warm-up. Excluding
  that phase, post-22:00 RSS grew `1488404 -> 1911876 kB` at `+35157 kB/hour`;
  the final four-hour slope slowed to `+18973 kB/hour` but did not reach a clear
  plateau. Burst RSS ended only `8876 kB` above its first sample despite a
  transient `2209064 kB` peak.
- FileOps FD-cache state grew `pids 21 -> 9921`, `entries 24 -> 11184`, and
  directory index `658 -> 2137`. Minute alignment produced RSS/FD-entry level
  correlations `r=0.929` overall and `r=0.938` post-22:00, but only `r=0.253`
  for minute deltas. This makes FD-cache eviction the leading residual memory
  hypothesis without claiming sole causality. RSS correlation was only `0.130`
  with sender queue and `0.192` with CPU.

## Follow-Ups

- Consider a second iteration on the pidstat chart UX: container-only narrowing, alternate bucket sizes, or anomaly-focused ranking modes beyond the current peak-selected-metric rule.
- Consider whether `By command` should grow additional aggregation styles (`sum`, `average`, `max`) now that the basic family-level series pattern is validated.
- Consider whether the event-volume correlation chart should stay notebook-only or be promoted into a named monitoring view if it becomes a stable QA concept.
- If linked navigation becomes important, consider collapsing the two charts into a single multi-row Plotly subplot figure so zoom/pan is naturally shared.
- Decide whether `file_chart` and possibly `network_chart` need a later chart-specific detail contract for higher-fidelity timelines.
- Continue with the later feature slices: broader event-family cleanup and Analytics-side conflict handling.
- Use the new focused root wrapper on `spk16` for the next live run instead of trying to broaden general host permissions for `/proc` or .NET diagnostics.
- Add process-exit plus conservative age/capacity cleanup for the FileOps
  FD-path cache, with eviction counters and short-lived-process validation, then
  repeat the same hash/window-qualified long-run comparison.
- Decide which provisional `perf_*` streams should become durable sidecar/DBT
  contracts rather than manual-batch diagnostics.
- Preserve the owning commit anchors when preparing the cross-repo PRs.
- For any aggregation A/B experiment, use repeated operations on the same path,
  PID, and operation inside one second. A general filesystem workload is mostly
  high-cardinality and is not expected to be materially reduced by the
  intentionally emit-first aggregation contract.
- Preserve unique run IDs, exact windows, artifact hashes, and zero-loss/count-
  and-byte-conservation gates for future comparisons.
