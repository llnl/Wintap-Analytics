---
title: "Feature Design: Recent Host Activity Dashboard"
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
source_paths: streamlit/projects/SmokeTests; streamlit/projects/DataQA; ../Wintap-PyUtil/wintap_dbt
tags: [host-activity, streamlit, duckdb, s3, raw_sensor, feature-work]
---

# Feature Design: Recent Host Activity Dashboard

## Summary

Add an independent, read-only Streamlit app whose default view uses S3
`raw_sensor` object metadata for a quick view of host collection activity. It
shows per-host file counts and sizes over the filename's Win32 collect-time
stamp without opening Parquet contents. Raw-row aggregation remains an optional
secondary mode. A 12-hour UTC window, manual refresh, and partition-pruned
listing keep the first version bounded.

## Proposed Approach

1. **Confirm source shape.** At launch, read the DBT-compatible environment
   contract for one dataset root (`WINTAP_DBT_RAW_SENSOR_DATASET`, falling back
   to `WINTAP_DBT_DATASET` / `WINTAP_DATA_ROOT`) and the existing AWS profile,
   endpoint, region, and TLS variables. Inspect the actual root and a bounded
   representative set of Parquet schemas when operator access is available. Do
   not infer host identity from the root or path.
2. **Discover only relevant objects.** For the refresh time `end_utc`, derive
   `start_utc = end_utc - 12 hours`, then enumerate event-family objects under
   overlapping `dayPK`/`hourPK` partitions only. Metadata mode uses S3
   `ListObjectsV2` fields (`Key`, `Size`) and never opens Parquet contents.
   Preserve nested network `protoPK` paths, deduplicate keys, and enforce an
   explicit file budget that fails closed rather than silently truncating.
3. **Parse collection time from metadata.** Parse
   `hostname+event_type+FILETIME.parquet`, treat FILETIME as collection time,
   and apply the exact rolling window to that value. Report malformed names
   rather than silently assigning a time. For optional row mode, inspect column names case-insensitively
   and select row-level hostname and event-time columns supported for that
   family. Convert known FILETIME values with the same integer UTC semantics as
   Wintap-PyUtil; handle timestamp-native values explicitly. If the mapping is
   ambiguous or fields are absent, skip that family and state why.
4. **Aggregate metadata in memory; keep row aggregation in DuckDB.** Group
   object count/size by host and collect-time bucket for the primary view. The
   optional row mode reads selected Parquet keys with schema union
   where safe, filter the precise UTC time interval, then group `count(*)` by
   event family, normalized time bucket, and row hostname. Call the measure
   “raw rows”; never sum family-specific count fields into a universal total.
   For high-volume `raw_process_file`, use an exact aggregate-only DuckDB path
   rather than materializing or truncating raw rows; guard query time, memory/temp
   use, intermediate group count, and final chart points.
5. **Bound chart density.** Target approximately five-minute buckets initially.
   Widen the bucket until the selected view stays within a small fixed point
   budget; show the actual interval. Preserve empty time buckets as gaps/zeros
   only where source availability is known, and never imply that absent source
   data means zero activity.
6. **Render a focused view.** Default to all-family metadata, with an optional
   family filter before manual refresh; changing the selector alone does not
   query S3. Include a host selector and separate count and size charts with a
   line per host, UTC range and refresh time, staged progress and elapsed
   duration, plus absolute linear/log
   scale and a clearly separate normalized-to-own-peak view. The normalized mode
   is for temporal-shape comparison only and labels values as relative.
7. **Keep access ephemeral/read-only.** Use the AWS environment/profile chain;
   use boto3 ListObjectsV2 for metadata and create any DuckDB S3 secret only in
   the in-memory optional row-mode connection. Never display credentials; close
   clients/connections after refresh and issue no S3 writes.

### Scale/readability recommendation

An event-family selector prevents radically different family scales from
sharing one axis. Within a family, linear counts preserve absolute volume; a log
axis makes small hosts visible beside high-volume hosts. A normalized-to-each-
host-peak mode compares patterns but intentionally removes volume differences.
Keep these as explicit modes rather than placing unrelated units on a shared
axis. For six hosts, overlaying host lines is reasonable; add host filtering if
the actual deployment grows substantially.

The existing Analytics direct-S3 dashboard uses DuckDB `httpfs`, a temporary
secret, and explicit root configuration. The DBT source layout and partition
globs provide the pruning contract; the exact deployed host-prefix arrangement
is not established by those source files.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/s3_source.py §open_source/discover_files -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/README.md §Scope/Configuration -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_partition_globs -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/time.sql §win32_to_timestamp_expr -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/RawSensorWriter.cs §MaterializeFromParquetGlob/ParseMergedFileName -->

## Data Model Or Schema Changes

None. The app reads raw Parquet directly and creates only in-memory query
results. A small internal family-to-column adapter may be needed; it must not
change source files or DBT models.

## Interfaces And User Experience

- Separate app entry point and concise run/config instructions.
- Source settings come from DBT-compatible environment variables; AWS secrets
  remain outside app config and UI.
- Manual **Refresh** controls the snapshot time and invalidates prior query
  results.
- Sidebar controls: query mode (file metadata by default; raw Parquet rows
  optional), family or all families in metadata mode, and manual refresh.
  Changing selections alone does not access S3. The dataset root is
  environment-configured.
- Main panel: metadata totals and per-host count/size summary, last-12-hour UTC
  line chart, visible bucket width, source refresh time, and malformed-name or
  source errors. Row mode retains its analysis controls.

## Edge Cases

- Window crosses UTC midnight; include both affected day partitions and only
  intersecting hour partitions.
- Multiple roots point to duplicate keys; do not double-count identical S3
  objects.
- Network paths include `protoPK`; recursive discovery must not lose these
  objects.
- FILETIME, timestamp, nullable, differently-cased, and absent columns; do not
  guess a timestamp scale.
- Filename event aliases must agree with the canonical event directory; names
  with malformed host/type/FILETIME components are counted, not charted.
- Hostname null/blank values and host name case differences; do not merge
  distinct short/FQDN hosts without an explicit rule.
- Empty event family, missing partitions, late arrivals, inaccessible S3, bad
  Parquet, object/row budget exceeded, and zero peak in normalized view.
- Schema drift across hosts/objects; union compatible columns, fail/report
  incompatible event-family inputs.

## Error Handling

Use actionable sanitized messages for config, AWS permission/connectivity,
schema, and budget failures. Never display exception text that could include
secrets, endpoint credentials, signed URLs, or raw event payloads. Distinguish
source unavailable from a valid empty time window. No partial truncated chart is
presented as complete.

## Risks

- DBT's root/partition contract does not reveal actual live S3 prefixes or which
  host/time columns are present. Operator-assisted discovery is required.
- A partition hour is a scan-pruning key, not by itself a confirmed event-time
  or ingestion-completeness guarantee. Use row timestamps for chart membership.
- Some raw files may represent aggregates or multiple producer semantics; raw
  row counts are not comparable as logical event counts across families.
- S3 object count, schema heterogeneity, and network latency may still make a
  12-hour refresh slow; budgets and visible latency are required.
- Event rows may arrive late; this view is an availability snapshot, not a
  loss/health assertion.

## Alternatives Considered

- Add a page to SmokeTests/DataQA: rejected for v1 because the activity monitor
  has a distinct source and purpose and should launch independently.
- Read an existing materialized DBT database: rejected because the request is
  for direct bronze S3 data and the dashboard should avoid a DBT build.
- Use S3 prefix as host identity: rejected until actual data layout proves this
  is required; row hostname is the requested grouping key.
- Plot every family and host on one chart: rejected for readability and scale.
- Always use normalized values: rejected because it hides absolute volume; keep
  normalization as an explicit secondary view.

## Open Questions

- Deployed root/endpoint values are intentionally not recorded. A read-only
  operator profile has verified discovery and representative query paths, but
  other deployment profiles/environments remain unverified.
- Live host/time semantics have been checked for `raw_host`, `raw_process`,
  `raw_process_file`, and `raw_process_conn_incr`; other family adapters still
  need representative schema checks.
- The exact high-volume `raw_process_file` route is implemented with a 120-second
  timeout, 1 GB memory/temp limits, 20,000 intermediate groups, and 1,000 chart
  points. Validate behavior near those limits and latency under other source
  conditions before broader operational acceptance.
