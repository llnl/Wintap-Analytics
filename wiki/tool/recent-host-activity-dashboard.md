---
title: "Recent Host Activity Dashboard"
type: tool
confidence: high
grounded_by:
  - streamlit/projects/HostActivity/README.md
  - streamlit/projects/HostActivity/main.py
  - streamlit/projects/HostActivity/queries.py
  - streamlit/projects/HostActivity/s3_source.py
  - streamlit/projects/HostActivity/file_metadata.py
  - streamlit/projects/HostActivity/tests/contract/test_host_activity.py
  - streamlit/projects/HostActivity/status_source.py
  - streamlit/projects/HostActivity/status_views.py
  - streamlit/projects/HostActivity/tests/contract/test_status_source.py
  - streamlit/projects/HostActivity/partition_status.py
  - streamlit/projects/HostActivity/tests/contract/test_partition_status.py
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/wintap/core/etl/extract/HostSerializer.cs
  - ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs
  - ../wintap/wintap/core/etl/extract/UdpPacketSerializer.cs
  - ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
policy: agent-editable
last_validated: 2026-11-17
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/HostActivity; ../Wintap-PyUtil/wintap_dbt/macros
tags: [host-activity, streamlit, duckdb, s3, raw_sensor, read-only]
---

# Recent Host Activity Dashboard

Standalone, manually refreshed Streamlit application for a quick view of the
last 12 hours of Wintap `raw_sensor` file activity. The default metadata mode
reports S3 object counts and sizes by host over filename collect time without
opening Parquet contents. An optional raw-row mode uses DuckDB. It does **not**
invoke DBT, require a DBT materialization, or write to S3.

## Launch and source configuration

From the Wintap-Analytics repository, set DBT's existing environment variables
and launch the app as described in
[`streamlit/projects/HostActivity/README.md`](../../streamlit/projects/HostActivity/README.md):

- Dataset root precedence: `WINTAP_DBT_RAW_SENSOR_DATASET`, then
  `WINTAP_DBT_DATASET`, then `WINTAP_DATA_ROOT`. The value must be an `s3://`
  dataset root containing `raw_sensor/`.
- AWS/S3 settings: `AWS_PROFILE`, `AWS_ENDPOINT_URL`,
  `AWS_DEFAULT_REGION` (fallback `AWS_REGION`), and `DUCKDB_USE_SSL`.
- `AWS_ENDPOINT_URL` follows Wintappy's contract: either a bare host/authority
  or an HTTP(S) origin; TLS is configured separately through `DUCKDB_USE_SSL`.
- Credentials remain in the standard AWS credential chain/profile. Metadata
  mode uses boto3 S3 `ListObjectsV2`; optional row mode creates an ephemeral
  credential-chain secret in an in-memory DuckDB connection. Clients close after
  refresh.

The app currently accepts one dataset root. It snapshots source-configuration
identity in Streamlit session state, but does not store credential material.
The bottom of the sidebar shows the resolved dataset and effective non-secret
profile/region/endpoint/TLS settings; credential values are hidden. This is a
configuration summary, not a credential inspector. The source setup follows
Wintappy's DBT S3 contract.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/s3_source.py §load_settings/open_connection -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/main.py §_render_environment_info/main -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

## Query and display semantics

- The default explicit refresh captures the exact rolling 12-hour UTC interval.
  A custom mode accepts first/last UTC `dayPK/hourPK` partitions, inclusive, and
  processes full partition hours as `[first-hour, hour-after-last)`. Custom
  ranges have no duration cap; the UI warns above 24 hours. Both modes restrict
  discovery to intersecting `dayPK=YYYYMMDD/hourPK=HH` partitions. Partial
  rolling-window boundary hours can result in 13 partitions. Metadata mode uses
  ListObjectsV2 keys and object sizes only, retains nested network `protoPK`
  keys, lists all supported families by default with a one-family filter, and
  never GETs/reads Parquet content.
- Metadata filenames use `hostname+event_type+FILETIME.parquet`. The Win32
  FILETIME in the name is the capture/collect timestamp used for the time series;
  S3 `LastModified` is intentionally ignored. Producer materialization also
  derives `dayPK`/`hourPK` from that capture time. The exact `[start,end)` window
  is applied to filename timestamps. Malformed or mismatched filenames are
  counted and excluded from host/time summaries.
- The default view shows separate file-count and S3 object-size charts, grouped
  by host and adaptive collect-time bucket. A per-host summary includes file
  count, total size, and latest collect time. Changing query/family selection
  does not access S3 until Refresh.
- **Raw Parquet rows** is an optional secondary mode. It selects one family,
  inspects supported row-level host/time columns, and counts physical source
  rows—not deduplicated logical events or a universal cross-family total.
- For `raw_process`, an explicit experimental metric can replace the raw-row
  chart with **likely user activity — process diversity**. It filters to
  `ActivityType = Start`, lowercases/trims process names, trims user names,
  removes small documented system/user and process deny-lists, and counts
  distinct remaining process names per user, host, and fixed 15-minute UTC
  bucket. This is a best-effort background-activity heuristic, not
  interactive-session detection. Select one host to render a time-scaled
  heatmap with usernames on the y-axis and process-type diversity as cell
  intensity. Command lines, paths, and individual process details are not
  displayed. This is a barely acceptable temporary proxy; a real Linux
  session/logon feed is needed for session claims. The raw-row chart remains
  available and unchanged.
  [[wiki/todo/linux-interactive-session-feed]]
  <!-- GROUND_TRUTH: streamlit/projects/HostActivity/queries.py §_process_activity_expression/_process_activity_user_expression/aggregate_family -->
  <!-- GROUND_TRUTH: streamlit/projects/HostActivity/main.py §_process_activity_chart -->
- Host columns are selected case-insensitively from `Hostname`, `ComputerName`,
  `Computer` (confirmed hostname alias), `HostHame`, and `host_name`. When
  schema drift yields more than one available alias, nonblank values are
  coalesced in that priority order. Outer whitespace is trimmed; host values are
  otherwise kept distinct.
- Timestamp interpretation is producer/family-aware. `raw_process.EventTime`
  uses Windows FILETIME; `raw_host`, `raw_process_file`,
  `raw_process_conn_incr`, and SELinux serializers emit integer `EventTime` in
  Unix seconds. `raw_process_file` prefers `FirstSeen`, then `LastSeen` (FILETIME)
  before its Unix-seconds `EventTime`; `raw_process_conn_incr` prefers
  `FirstSeenMs`/`LastSeenMs` (FILETIME); SELinux families prefer their
  `FirstSeen`/`LastSeen` FILETIME columns. `raw_host` uses Unix-seconds
  `EventTime`. Native timestamps/dates and ISO strings are normalized to UTC-naive
  chart labels. Unknown numeric encodings are not guessed. The UI displays the
  timestamp fields/encoding priority used by the snapshot.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/FileSerializer.cs §HandleSensorEvent; ../wintap/wintap/core/etl/extract/Serializer.cs §GetUnixNowTime; ../wintap/wintap/core/etl/esper/file.epl §query; ../wintap/wintap/core/etl/extract/HostSerializer.cs §GetSendableHost/WriteHostRecordAsync; ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs §HandleSensorEvent; ../wintap/wintap/core/etl/extract/UdpPacketSerializer.cs §HandleSensorEvent; ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs §HandleSensorEvent; ../Wintap-PyUtil/wintap_dbt/models/silver/process_file.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql -->
- In row mode, families with no usable host/time mapping or unreadable schemas
  are skipped with a reason. Rows with null/blank hostnames are counted and
  reported, not charted.
- Metadata-mode status identifies object listing and filename/size aggregation;
  row mode reports listing, schema inspection, and timestamp aggregation. Both
  show elapsed time and fail closed without partial charts.
- Partition enumeration is lazy: metadata mode has at most eight concurrent
  partition requests, while raw-row glob discovery submits at most 24 hours of
  partition globs per query. Existing 10,000-object, row, timeout, intermediate
  group, and 1,000-chart-point budgets still apply to custom ranges.
- Buckets start at five minutes, are anchored to the refresh window, and widen
  to fit a 1,000-point view budget. For each host with at least one accepted
  observation in the selected window, missing buckets across the full window are
  filled with zero in both metadata and raw-row charts. Hosts with no qualifying
  observation cannot be identified and receive no synthetic series. Absolute
  row counts support linear or symmetric-log scaling, which remains
  zero-compatible.
  Optional row-mode normalization divides each host by its own peak and is a
  shape comparison, not a volume comparison.
- Chart hovers show only UTC bucket time, host, and the metric used by that
  chart: file count or object size (MiB) in metadata mode; raw-row count or
  normalized peak ratio in row mode; distinct process-type count for the
  experimental process-diversity metric.

Fail-closed limits include 10,000 discovered objects and 1,000 chart points per
view. Standard row-mode families also have a 2,000,000 timestamped in-window raw-row
budget. `raw_process_file` is the exception: it aggregates all matching rows
directly in DuckDB, without sampling or materializing raw rows in Python, under a
120-second query timeout, 1 GB DuckDB memory limit, 1 GB temporary-storage limit,
and 20,000 intermediate host/time-group limit. All paths fail closed and produce
no partial chart when a limit is exceeded.
The experimental `raw_process` user heatmap also uses an aggregate-only SQL scan
and SQL-generated user/bucket cells. It remains available when the physical
raw-row count exceeds the standard 2,000,000-row chart budget; only the raw-row
chart is withheld in that case. Its fixed-resolution grid has a separate
20,000-cell budget, rather than the ordinary 1,000-point line-chart budget.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/s3_source.py §MAX_S3_FILES/discover_files -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/queries.py §MAX_ROWS_PER_FAMILY/MAX_PROCESS_ACTIVITY_CELLS/choose_bucket_minutes/zero_fill_time_buckets/aggregate_family -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/queries.py §MAX_AGGREGATE_GROUPS/PROCESS_FILE_QUERY_TIMEOUT_SECONDS/PROCESS_FILE_MEMORY_LIMIT/PROCESS_FILE_TEMP_LIMIT/_aggregate_process_file -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/main.py §main/_refresh -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/file_metadata.py §parse_file_metadata/aggregate_file_metadata; streamlit/projects/HostActivity/queries.py §zero_fill_time_buckets -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/RawSensorWriter.cs §MaterializeFromParquetGlob/ParseMergedFileName -->
<!-- SYNTHESIS: raw Parquet row counts preserve source row grain but do not establish logical-event equivalence across event families -->

For standard families, bounded raw-row selection, budget statistics, and bucket
aggregation share one materialized DuckDB scan. `raw_process_file` instead
groups the exact filtered rows directly by hostname and five-minute bucket in
DuckDB, then coarsens the compact group result if needed to meet the chart-point
budget. This avoids transferring/materializing millions of raw rows, but still
scans every qualifying source row and therefore remains subject to its explicit
query/resource limits. Neither strategy reduces required partition listings or
eliminates S3 latency.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/queries.py §aggregate_family -->

### Partition compaction overview

The **Partitions** view is a separate metadata-only diagnostic. It defaults to
the most recent 42 complete UTC calendar days and discovers the union of event
directories under the configured dataset's `raw_sensor/` and `compacted/`
roots. For each event type/day cell it checks hourly prefixes only:

- `compacted-present-hours / 24` is the color metric, so incomplete days are
  deliberately penalized;
- raw-only hours contribute zero, compacted-only hours contribute one, and
  raw/compacted overlap contributes one while remaining visible in the tooltip;
- cells with no hour present in either root are blank;
- tooltips include compacted, raw, overlap, and observed-hour counts.

The survey uses paginated, delimiter-scoped `ListObjectsV2` requests and never
opens Parquet objects. It is an availability/overlap signal during potentially
mixed-generation compaction, not proof of migration, deletion, completeness,
or collector health.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/partition_status.py; streamlit/projects/HostActivity/main.py §_render_partition_view/_render_partition_chart -->

## Verification status

On 2026-11-17, the app-scoped suite passes 59 tests. `AppTest` verifies the
effective environment info box (credential values hidden), the rolling default,
and a 25-hour inclusive custom partition range whose exact bounds reach metadata
discovery with the expected >24-hour warning. Synthetic tests verify both
metadata and raw-row charts zero-fill missing per-host buckets across the full
selected interval; duration-aware buckets continue to respect chart budgets.
Focused chart-spec tests verify concise hover fields for both metadata metrics,
raw-row counts, normalized peak ratios, and the experimental process-diversity
user heatmap. Synthetic process tests verify Start-only distinct-name counting
per user in fixed 15-minute UTC buckets. Multi-day tests cover lazy/chunked
partition enumeration and retained row/object budgets. Live S3 custom-range
behavior remains unverified. An aggregate-only live validation of the configured
read-only `raw_process` family selected 2,328 objects and 2,617,339 raw rows;
the 24-hour user heatmap produced 2,134 SQL-generated cells across 18 display
users, with 450 nonzero cells. The raw-row chart correctly remained withheld by
its 2,000,000-row budget. No host values, process names, users, paths, commands,
or raw rows were persisted.
The user tested the zero-filled chart behavior and accepted it on 2026-11-16.

On 2026-11-11, 27 focused tests passed in the app-scoped UV environment
(DuckDB 1.5.6, Streamlit 1.67.0, Altair 6.3.0, Pandas 2.3.3, boto3 1.44.0).
Streamlit `AppTest` rendered both initial metadata state and a mocked metadata
refresh. It verified the default all-family mode and that metadata refresh does
not open a DuckDB connection or inspect/read Parquet. Synthetic tests cover
paginated ListObjectsV2, partition scoping, sizes, filename FILETIME parsing,
exact-window accounting, and count/byte conservation. Row-mode tests still use
synthetic Parquet and mocked discovery, including
  Unix-second versus FILETIME family contracts and rejection of a returned object
  outside the requested day/hour set, exact high-volume aggregation, timeout
  interruption, and the process-file result-display path. A bounded, read-only probe using the
operator-provided environment found 3,988 Parquet object paths across 8 families
in 13 overlapping hourly
partitions; listing took about 26 seconds. `raw_process` schema inspection over
1,226 objects took about 19 seconds and aggregation about 67 seconds (1,305,103
in-window rows, 6 hosts, 598 points). `raw_process_conn_incr` schema inspection
over 990 objects took about 17 seconds and its exact timestamp aggregation found
no in-window rows under the then-current FILETIME interpretation. A selected-
family `raw_host` probe over 59 objects took about 5 seconds end-to-end and
likewise found no rows under that interpretation. A follow-up `raw_process_file`
probe found that integer `EventTime` values were being decoded as FILETIME even
though the producer writes Unix seconds, mapping the sampled timestamps to 1601.
The correct `FirstSeen` FILETIME basis had about 7.9 million rows in the exact
12-hour interval; before the aggregate-only strategy, the 2-million-row budget
failed closed after about 60 seconds. Therefore the earlier 15.5-second empty
chart was a timestamp-decoding error, not evidence of zero file activity. A
read-only feasibility probe grouped the entire interval to 479 five-minute
host/bucket groups in about 20 seconds. The implemented `raw_process_file` query
then returned the full exact result: 7,923,378 host-attributed rows, 5 hosts,
479 chart points, no hostless rows, and a five-minute bucket in about 20 seconds
over 513 discovered objects. The group counts sum to the exact row count. Query
timeout, memory/temp, intermediate-group, and chart-point limits are enforced;
the standard-family 2-million raw-row cap remains intact for ordinary raw-row
charts; the experimental `raw_process` user heatmap uses aggregate-only SQL and
can remain available when that raw-row chart cap is exceeded. The earlier
15.5-second
empty chart was a timestamp-decoding error, not evidence of zero file activity.
The earlier all-family
dashboard refresh took at least five minutes; its `pidstat` result exceeded the
2-million-row fail-closed limit. No root,
endpoint, credential, object key, host value, or raw event row was persisted.
The raw-row UI reports coarse hourly partitions beside its exact event-time
window. The metadata mode has only synthetic/mocked S3 evidence so far: live
listing latency, deployed-endpoint compatibility, and filename alias coverage
remain unverified. Broader family coverage and operational acceptance also
remain open.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/tests/contract/test_host_activity.py -->

## Known limits

This is an availability snapshot, not a completeness, loss, or collector-health
monitor. A zero-filled bucket means no qualifying object/row was returned for
that observed host and bucket; it is not evidence of true zero activity or
complete collection. Object presence/size does not validate file contents or
prove that expected data was collected. Late arrivals, absent partitions,
malformed names, unsupported timestamp encodings, and hostless rows can reduce
chart coverage.
Run tests and launch instructions are maintained in the app's README and the
feature record:
[[wiki/work/recent-host-activity-dashboard/verification]].

The November 22 first-cut test reorganization moves the 59 existing offline cases
intact into `tests/contract/`. From the app directory, use
`python -m unittest discover -s tests -t . -p 'test_*.py'` in the app environment;
legacy project-root discovery still works. These synthetic application checks are
not validation of a fresh sensor capture. Inventory and iteration results:
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/tests/README.md -->

## Advisory compaction/status subset and pending extensions

[[wiki/work/compaction-status-utility/brief]] proposes extending this same app,
on the compaction server, with all/subset partition status, lock/admission state,
a run timeline, compacted event reads and optional retained entity inspection.
The human approved the two modes on November 14 and implementation on November 15;
deployment remains unauthorized. The implemented subset adds Activity/Status/Runs/
Partitions navigation and manual pinned local advisory v1 inspection. All 46 offline
tests pass, including real Streamlit controls; a separate dashboard-runtime process
reads a genuine producer export with the synthetic ledger lock held and files unchanged.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/main.py; streamlit/projects/HostActivity/status_source.py; streamlit/projects/HostActivity/status_views.py; wiki/work/compaction-status-utility/verification.md -->

Status requires `WINTAP_STATUS_EXPORT` (absolute regular local `status.json`),
`WINTAP_STATUS_BINDING_SHA256` (full canonical producer binding) and
`WINTAP_STATUS_LEDGER_ID`. No ledger/lock/data-root/SDK access is performed. Strict
identity/schema/byte/page/timestamp failures show unavailable; age over 180 seconds
shows stale. Producer observation and app retrieval times are distinct. Timestamp
rollback is refused within the pinned session, not a sequence-based or whole-session
freshness guarantee. Changed pins/path clear cached summaries; navigation is cached.

Only allowlisted mode/cursor/owner/job/raw-run/maintenance summaries are displayed.
Roots, authority payloads and free-form block diagnostics are withheld. Reserved is
not grant delivered. Runs shows bounded raw intent markers, not measured bars:
`COMPLETED` is reported disposition only, actual launch/finish/certificates are
unavailable and continuations mean incomplete history. The S3 Partitions view is a
separate metadata-only hourly-presence diagnostic; producer v1 still exports no
authoritative catalog, process-lock observation, progress or entity-only history.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/status_source.py §_validate/read_snapshot; streamlit/projects/HostActivity/status_views.py §render; ../Wintap-PyUtil/wintappy/coordination/service.py §status_page/export_status -->

Activity is still synchronous/raw-only and always displays **Live diagnostic —
uncoordinated**, even with reported `OPEN` or missing status. Full catalog/timeline,
compacted/entity reads and managed live/coordinated job lifecycles remain pending.
The Linux client exists, but is not integrated here; native coordinated shutdown is
unqualified. Status never permits reading, completion, deletion, recovery or reopening.
No unlocked DBT or live-ledger inspection is added. Raw filename metadata is not
compacted row-level host/time, and entity context is not extra event history.
Configure/test through the app README; see [[wiki/work/compaction-status-utility/design]]
for remaining design and [[wiki/work/compaction-status-utility/verification]] for limits.
