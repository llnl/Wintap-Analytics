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
  - streamlit/projects/HostActivity/test_host_activity.py
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/wintap/core/etl/extract/HostSerializer.cs
  - ../wintap/wintap/core/etl/extract/TcpConnectionSerializer.cs
  - ../wintap/wintap/core/etl/extract/UdpPacketSerializer.cs
  - ../wintap/wintap/core/etl/extract/SELinuxSerializer.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
policy: agent-editable
last_validated: 2026-11-11
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
The source setup follows Wintappy's DBT S3 contract.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/s3_source.py §load_settings/open_connection -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

## Query and display semantics

- Each explicit refresh captures the exact rolling 12-hour UTC interval. S3
  discovery is restricted to intersecting `dayPK=YYYYMMDD/hourPK=HH` partitions;
  partial boundary hours can result in 13 partitions. Metadata mode uses
  ListObjectsV2 keys and object sizes only and retains nested network `protoPK`
  keys. It lists all supported families by default, with a one-family filter.
  It does not GET/read Parquet content.
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
  reported, not charted. Missing timestamps/partitions are not filled in as zero.
- Metadata-mode status identifies object listing and filename/size aggregation;
  row mode reports listing, schema inspection, and timestamp aggregation. Both
  show elapsed time and fail closed without partial charts.
- Buckets start at five minutes, are anchored to the refresh window, and widen
  to fit a 1,000-point view budget. Absolute row counts support linear or
  logarithmic scaling. Optional row-mode normalization divides each host by its
  own peak and is a shape comparison, not a volume comparison.

Fail-closed limits include 10,000 discovered objects and 1,000 chart points per
view. Standard row-mode families also have a 2,000,000 timestamped in-window raw-row
budget. `raw_process_file` is the exception: it aggregates all matching rows
directly in DuckDB, without sampling or materializing raw rows in Python, under a
120-second query timeout, 1 GB DuckDB memory limit, 1 GB temporary-storage limit,
and 20,000 intermediate host/time-group limit. All paths fail closed and produce
no partial chart when a limit is exceeded.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/s3_source.py §MAX_S3_FILES/discover_files -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/queries.py §MAX_ROWS_PER_FAMILY/choose_bucket_minutes/aggregate_family -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/queries.py §MAX_AGGREGATE_GROUPS/PROCESS_FILE_QUERY_TIMEOUT_SECONDS/PROCESS_FILE_MEMORY_LIMIT/PROCESS_FILE_TEMP_LIMIT/_aggregate_process_file -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/main.py §main/_refresh -->
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/file_metadata.py §parse_file_metadata/aggregate_file_metadata -->
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

## Verification status

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
the standard-family 2-million raw-row cap remains intact. The earlier 15.5-second
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
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/test_host_activity.py -->

## Known limits

This is an availability snapshot, not a completeness, loss, or collector-health
monitor. Object presence/size does not validate file contents or prove that
expected data was collected. Late arrivals, absent partitions, malformed names,
unsupported timestamp encodings, and hostless rows can reduce chart coverage.
Run tests and launch instructions are maintained in the app's README and the
feature record:
[[wiki/work/recent-host-activity-dashboard/verification]].
