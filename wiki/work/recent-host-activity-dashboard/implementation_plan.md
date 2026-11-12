---
title: "Implementation Plan: Recent Host Activity Dashboard"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/HostActivity/s3_source.py
  - streamlit/projects/HostActivity/queries.py
  - streamlit/projects/HostActivity/test_host_activity.py
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
policy: agent-editable
last_validated: 2026-11-11
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/SmokeTests; ../Wintap-PyUtil/wintap_dbt
tags: [host-activity, streamlit, duckdb, s3, feature-work]
---

# Implementation Plan: Recent Host Activity Dashboard

## Scope

Standalone read-only Analytics app for manually refreshed, rolling 12-hour UTC
S3 file metadata trends by host, with optional raw-row analysis. Implementation
and tests stay in Wintap-Analytics. Wintap-PyUtil/Wintap sources are read-only
references.

## Steps

1. [x] Inspect existing Analytics app launch/dependency conventions and use
   DBT's existing dataset and AWS environment-variable contract.
2. [x] Run an initial bounded read-only pilot with operator-provided access;
   confirm partitioned discovery and sample `raw_process` /
   `raw_process_conn_incr` schemas. Other live family schemas and complete
   operational validation remain open.
3. [x] Implement validated S3 root configuration, temporary in-memory DuckDB
   S3 access, and bounded event/day/hour object discovery, including nested
   `protoPK` paths; verify every returned key belongs to the requested
   event/day/hour set before scanning it.
4. [x] Implement producer/family-aware UTC timestamp projections (including
   FILETIME activity bounds vs. Unix-seconds serializer timestamps), exact
   rolling-window filters after partition pruning, and fail-closed aggregation.
   Standard families use the 2,000,000 raw-row budget; `raw_process_file` uses
   exact aggregate-only grouping with timeout, memory/temp, intermediate-group,
   and final chart-point guards.
5. [x] Implement standalone Streamlit controls, selected-family-only manual
   refresh, staged status and elapsed-time reporting, host time series, adaptive
   bucket sizing, linear/log and normalized-to-host-peak views, and honest
   empty/error/family-processing states.
6. [x] Add synthetic Parquet, mocked DuckDB glob discovery, query-budget,
   credential-SQL, chart-data, and manual-refresh tests. No writes or credential
   values are used by the test suite.
7. [x] Add the app-scoped UV project/lock, sync the pinned runtime, run the
   focused tests, and verify the initial Streamlit `AppTest` render. Selector
   behavior with loaded data remains unverified until live data is available.
8. [x] Execute a bounded live S3 discovery/schema/query pilot with the
   operator's existing read-only profile; record timings and limitations without
   persisting roots, credentials, object keys, hosts, or raw rows.
9. [x] Change refresh to query only the explicitly selected family; verify that
   changing families does not access S3 until the user clicks Refresh.
10. [x] Promote durable launch/source semantics into a canonical tool page,
    update this checklist and verification record, and append the implementation
    entry to `wiki/log.md`.
11. [x] Add a default metadata-only mode using S3 object key/size listings and
    filename Win32 collect timestamps; retain row-level DuckDB analysis as an
    explicit secondary mode. Verify partition pruning, pagination, budgets,
    exact filename-time filtering, and the no-Parquet-read UI path.

## Files Likely To Change

- `streamlit/projects/HostActivity/main.py` and local query/source modules.
- `streamlit/projects/HostActivity/README.md` with the DBT-compatible
  environment-variable launch contract.
- `streamlit/projects/HostActivity/pyproject.toml` and `uv.lock` for an isolated
  app-scoped UV environment.
- New focused tests/fixtures under the same app directory.
- On closeout: relevant canonical wiki page, `wiki/index.md`,
  `wiki/work/recent-host-activity-dashboard/verification.md`, this plan, and
  `wiki/log.md`.

## Tests To Add Or Update

- UTC 12-hour interval and cross-midnight day/hour partition pruning.
- Safe dataset-root/endpoint config and DBT-compatible credential-chain SQL
  rendering; bare-host endpoint compatibility was also exercised in the live
  pilot.
- Mocked DuckDB glob discovery for one root, deduplication, nested network
  partition, strict requested-hour membership, and max-object fail-closed
  behavior.
- Raw Parquet rows grouped by family/host/time, including FILETIME and native
  timestamps, schema drift, unsupported families, empty windows, and null hosts.
- S3 object-metadata listing by family/day/hour with pagination, size validation,
  filename FILETIME parsing, exact collect-time filtering, and per-host count/size
  aggregation; verify no Parquet open occurs in metadata mode.
- Adaptive bucket point bound, normalized peak behavior, empty-window behavior,
  and no partial output after row/point budget failure. Linear/log selector
  interaction remains part of the real UI smoke.
- Streamlit AppTest verifies the initial render and that changing the selected
  family creates no source snapshot/query before explicit refresh. Host/scale
  selector behavior with populated live results remains untested.
- Sanitized error handling; verify config rejects keys and no object writes are
  attempted.

## Migration Or Compatibility Notes

No data or schema migration. The app reads the existing raw_sensor layout and
does not alter SmokeTests, DataQA, DBT models, or sensor output.

## Rollback Plan

Remove/disable the standalone app and its local config. No S3 data, DBT state,
or collector setting is modified by the dashboard, so no data rollback is
required.

## Done Checklist

- [x] Offline source/query tests pass in the locked UV environment, including
  synthetic multi-host Parquet, an AppTest no-query-before-manual-refresh render
  check, source-specific Unix/FILETIME timestamp tests, exact high-volume
  process-file aggregation, group/point budgets, timeout interruption, and the
  selected-family result-display path.
- [x] Install/sync the app's locked UV dependencies and verify the initial
  Streamlit render using DuckDB 1.5.6.
- [x] Run a bounded live read-only discovery and representative family-query
  pilot, including the corrected file-time basis; remaining-family coverage and
  broader operational acceptance remain open.
- [x] Operator authorized the exact aggregate-only `raw_process_file` strategy;
  implemented and validated it with timeout, memory/temp, intermediate-group,
  and chart-point safeguards while leaving other families' raw-row cap intact.
- [x] Metadata-first mode uses bounded concurrent S3 listings (`Key` and `Size`
  only), parses filename Win32 FILETIME collect stamps, and renders per-host
  counts/sizes without opening Parquet contents. Synthetic/AppTest verification
  passed; live S3 metadata-mode validation remains open.
- [x] Verification, index, canonical usage docs, and operation log are updated.
