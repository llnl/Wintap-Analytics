---
title: "Feature Brief: Recent Host Activity Dashboard"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/SmokeTests/s3_source.py
  - streamlit/projects/SmokeTests/README.md
  - streamlit/projects/DataQA/pages/raw_events.py
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
policy: agent-editable
last_validated: 2026-11-11
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects; ../Wintap-PyUtil/wintap_dbt
tags: [host-activity, streamlit, duckdb, s3, raw_sensor, feature-work]
---

# Feature Brief: Recent Host Activity Dashboard

## Problem

Several Wintap/Lintap hosts publish telemetry into a common S3 environment.
There is no small, at-a-glance view of recent raw activity by host and event
family. Event volumes differ substantially, so one linear scale may hide quieter
hosts.

## Goals

- Provide a focused standalone Streamlit dashboard in Wintap-Analytics.
- Provide a quick manually refreshed herd overview from S3 object metadata:
  file counts, object sizes, and per-host collection-time trends.
- Keep raw Parquet row-count analysis as an optional secondary query mode.
- Bound S3 listing and data reads with the existing `dayPK`/`hourPK` partitions.
- Keep access read-only and use local AWS profile/environment credentials.
- Make scale differences and unsupported source schemas visible rather than
  misleading.

## Non-Goals

- No sensor/uploader changes, new telemetry, DBT models, schema changes, or
  writes to the S3 dataset.
- No historical dashboard, alerting, completeness certification, collector
  health certification, or cross-family semantic event-count normalization.
- No automatic polling in the first version.
- No assumption that a host is identified by an S3 prefix or by a short/FQDN
  alias.

## User-Facing Behavior

- A standalone app reads one dataset root from `WINTAP_DBT_RAW_SENSOR_DATASET`,
  falling back to `WINTAP_DBT_DATASET` and `WINTAP_DATA_ROOT`; it must contain
  `raw_sensor/`. S3 settings use DBT's `AWS_PROFILE`, endpoint, region, and TLS
  environment variables. Credentials are never shown or persisted.
- The default File metadata mode looks back 12 hours from the current UTC time.
  It lists all supported event families (or one selected family) through S3
  `ListObjectsV2`, using object keys and sizes only; it never opens Parquet
  contents. It reports per-host file counts, sizes, latest collect time, and
  separate file-count and object-size time series.
- Metadata time comes from `hostname+event_type+FILETIME.parquet`; the Win32
  FILETIME is collection time, not S3 upload/LastModified time. Exact filename
  timestamp filtering follows day/hour partition pruning. Malformed filenames
  are reported and excluded from host/time aggregates.
- Raw Parquet rows remain available as an explicit secondary mode, selecting one
  family and using the existing DuckDB schema/event-time logic.
- Changing query mode or family does not query S3 until explicit refresh. The
  status panel reports metadata listing/aggregation or row-mode listing/schema/
  aggregation stages and elapsed time.
- S3 discovery is limited to relevant event-family and `dayPK`/`hourPK`
  partitions. Metadata mode uses listing metadata only; row mode reads the
  discovered Parquet objects and applies exact event-time bounds.
- Metadata mode charts per-host object count or object size over filename
  collect time. Raw-row mode charts rows over event time.
- Adaptive buckets start around five minutes and may widen to respect a bounded
  point/query budget; the current bucket width is displayed.
- Absolute counts support linear/log axis selection. A separate normalized
  view scales each host to its own peak for pattern comparison and is clearly
  labeled as relative, not event volume.
- Families without supported row-level hostname and event-time columns are
  excluded from the chart and listed with the reason. Empty or unreadable data is
  not rendered as zero activity.
- Timestamp decoding is producer-specific: the app uses Unix seconds for known
  serializer families and FILETIME for Windows event fields. File activity uses
  its `FirstSeen`/`LastSeen` activity bounds before the serializer-time
  `EventTime`; the chosen field priority is displayed with the snapshot.
- The standard-family 2,000,000 raw-row cap remains. `raw_process_file` uses an
  exact aggregate-only scan instead of truncating/materializing raw rows, guarded
  by a 120-second query timeout, 1 GB memory/temp limits, 20,000 intermediate
  host/time groups, and the shared 1,000 chart-point limit.

## Acceptance Criteria

1. App launches independently of SmokeTests and DataQA.
2. Uses DuckDB and Streamlit to read configured S3 raw Parquet without changing
   any object or requiring a DBT materialization.
3. Default view is the last 12 hours in UTC, with manual refresh only.
4. `dayPK`/`hourPK` are used to prune candidate objects across midnight; row
   timestamps are then filtered to the precise 12-hour interval.
5. The default metadata refresh reports per-host file counts/sizes and a
   filename-collect-time series without opening Parquet contents; optional
   selected-family raw-row analysis labels the metric unambiguously.
6. Event-family selection, per-host time series, adaptive visible bucket size,
   linear/log absolute counts, and normalized-to-host-peak mode are available.
7. Missing/incompatible families, empty data, access errors, and query budget
   failures are reported distinctly; results are never silently truncated.
8. AWS credentials are not accepted in app config, logged, displayed, or stored
   in the repository. S3 access is read-only.
9. Synthetic local Parquet and mocked S3 tests cover partition pruning, schema
   variation, timestamps, counting, scaling, and error handling.
10. A bounded read-only pilot against the actual configured S3 data confirms
    observed roots, supported families, host values, and acceptable refresh
    behavior before calling the dashboard operationally verified.

## Affected Areas

- Wintap-Analytics: new standalone Streamlit app, query/source helpers, local
  config example, focused tests, and launch documentation.
- Wintap-PyUtil `wintap_dbt`: read-only reference for S3 root and partition
  conventions; no changes authorized or required.
- Wintap/Lintap collection and upload paths: unchanged.

## References

- [[wiki/work/recent-host-activity-dashboard/interview]]
- [[wiki/work/recent-host-activity-dashboard/references]]
- [[wiki/work/recent-host-activity-dashboard/design]]
- [[wiki/work/recent-host-activity-dashboard/implementation_plan]]
- [[wiki/repo/wintappy-pipeline-repo]]
- [[wiki/work/smoke-test-dashboard/implementation_plan]]

## Open Questions

- Actual private S3 root(s), endpoint style, and active AWS profile.
- Which event folders and schema versions in the live bucket have usable row
  hostname and event-time columns.
- Whether current rolling-window partitions contain delayed arrivals that belong
  to the event-time window; display observed source time, not a completeness
  claim.
- Appropriate fail-closed object/row/point budgets after observing data volume.

## Test Plan

- Unit tests for root validation, UTC window-to-partition selection (including
  midnight), filename Win32 timestamp parsing, S3 metadata pagination/size,
  adaptive buckets, raw-row aggregation, and normalized/absolute chart projections.
- Synthetic local Parquet fixtures for multiple hosts/types, mixed column case,
  FILETIME and timestamp forms, unsupported/missing fields, empty hours, and
  nested network `protoPK`.
- Mocked S3 listing/credential setup; verify only relevant partitions are
  selected, limits fail closed, and no writes or secret disclosures occur.
- Streamlit app test for manual refresh, type/host selection, scale modes, and
  empty/error messages.
- Bounded operator-run S3 pilot with an existing read-only profile. Do not store
  real bucket names, credentials, or raw rows in committed test data.

## Done When

- Acceptance criteria 1–9 pass in offline regression tests and local app smoke.
- The operator confirms the actual S3 roots/schemas and one bounded 12-hour
  refresh; remaining coverage/freshness limitations are displayed and recorded.
- `verification.md` and `implementation_plan.md` record results; durable usage
  and source semantics are promoted to the canonical wiki; `wiki/log.md` is
  updated.
