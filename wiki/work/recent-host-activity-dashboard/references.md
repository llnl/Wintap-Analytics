---
title: "Feature References: Recent Host Activity Dashboard"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/SmokeTests/s3_source.py
  - streamlit/projects/SmokeTests/README.md
  - streamlit/projects/DataQA/pages/raw_events.py
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
policy: agent-editable
last_validated: 2026-11-10
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/SmokeTests; streamlit/projects/DataQA; ../Wintap-PyUtil/wintap_dbt
tags: [host-activity, streamlit, duckdb, s3, raw_sensor, feature-work]
---

# Feature References: Recent Host Activity Dashboard

## Live Repo Sources

- `streamlit/projects/SmokeTests/s3_source.py` — existing read-only S3 listing,
  dataset-root validation, DuckDB `httpfs` setup, and temporary connection-scoped
  S3 secret. It provides a security/data-access precedent, not a dashboard
  implementation to copy wholesale.
- `streamlit/projects/SmokeTests/README.md` — local private config, normal AWS
  profile/environment credentials, shared-root and multiple-root examples, and
  direct-S3 launch guidance.
- `streamlit/projects/SmokeTests/test_s3_source.py` — synthetic S3 listings,
  path validation, file-budget, and DuckDB/S3 setup test patterns.
- `streamlit/projects/DataQA/pages/raw_events.py` — existing Event Summary view;
  it uses a fixed 30-second bucket and comments on host-dependent chart sizing
  and adaptive bucket resolution.
- `../Wintap-PyUtil/wintap_dbt/README.md` — canonical bronze input layout,
  effective dataset-root configuration, S3 credentials/endpoint settings, and
  day/hour scan-pruning behavior.
- `../Wintap-PyUtil/wintap_dbt/macros/paths.sql` — builds per-event Parquet
  globs under `<dataset>/raw_sensor/` and narrows to requested day/hour
  partitions.
- `../Wintap-PyUtil/wintap_dbt/macros/s3.sql` — configures DuckDB S3 access from
  the credential chain, optional named profile, region, endpoint, path style,
  and TLS setting.
- `../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql` — current raw bronze
  event names and historical aliases to inform event-family discovery.
- `../Wintap-PyUtil/wintap_dbt/macros/time.sql` — timestamp conversion helpers,
  including integer FILETIME conversion to UTC.

The DBT README's example has a configured dataset root resolving to
`<root>/raw_sensor/...`; do not append `raw_sensor` when entering such a root.
The canonical DBT setting is a single effective raw-sensor root. The Analytics
SmokeTests app supports multiple roots, but neither source proves the live
six-host bucket's prefix arrangement. That remains a private operator/data
inspection step.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/README.md §Configuration -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_dataset_path/raw_sensor_path/raw_sensor_partition_globs -->
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/README.md §Read directly from Garage / S3 -->

## External Sources

None required for the initial feature brief.

## Related Wiki Pages

- [[wiki/repo/wintappy-pipeline-repo]] — canonical raw_sensor/DBT contract.
- [[wiki/repo/wintap-analytics-host-repo]] — Analytics repository ownership and
  current Streamlit tooling.
- [[wiki/work/smoke-test-dashboard/implementation_plan]] and
  [[wiki/work/smoke-test-dashboard/verification]] — existing direct S3 and
  DuckDB/Streamlit app patterns and limits.
- [[wiki/workflow/future-experiment-analysis-workflows]] — broader analysis
  workflow context.

## Libraries And APIs

- DuckDB Python API with `httpfs` extension for direct S3 Parquet reads.
- DuckDB `glob` over event/day/hour-partitioned patterns for bounded object
  discovery; no access keys embedded in Streamlit configuration.
- Streamlit for the standalone user interface and chart controls.

## Notes

- Partition pruning bounds remote input; the exact source timestamp still needs
  family-aware interpretation. Integer FILETIME conversion should match
  Wintap-PyUtil semantics where that encoding is present.
- Counts are raw Parquet rows. They do not equate to universal underlying event
  counts: raw families have different grains and some may be pre-aggregated.
- Do not assume every advertised bronze family has row-level hostname/time
  columns in the live bucket. Probe representative Parquet schemas and disclose
  skipped families.
