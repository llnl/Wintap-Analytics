---
title: "Dev Handoff: Recent Host Activity Dashboard"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/SmokeTests/s3_source.py
  - streamlit/projects/SmokeTests/README.md
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
policy: agent-editable
last_validated: 2026-11-10
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/SmokeTests; ../Wintap-PyUtil/wintap_dbt
tags: [host-activity, streamlit, duckdb, s3, feature-work]
---

# Dev Handoff: Recent Host Activity Dashboard

## Copy/Paste Prompt

Use this prompt to hand remaining verification to another agent:

    Switch to code-development mode for recent-host-activity-dashboard.

    Read AGENTS.md and these feature artifacts before editing:
    - wiki/work/recent-host-activity-dashboard/brief.md
    - wiki/work/recent-host-activity-dashboard/interview.md
    - wiki/work/recent-host-activity-dashboard/references.md
    - wiki/work/recent-host-activity-dashboard/design.md
    - wiki/work/recent-host-activity-dashboard/spike.md
    - wiki/work/recent-host-activity-dashboard/implementation_plan.md
    - wiki/work/recent-host-activity-dashboard/verification.md

    The standalone app is already implemented in
    streamlit/projects/HostActivity/. Do not invoke DBT: the app reads the
    existing WINTAP_DBT_RAW_SENSOR_DATASET / WINTAP_DBT_DATASET / WINTAP_DATA_ROOT
    and AWS_* environment variables directly. Do not modify sibling repos.
    Remaining work is a real local Streamlit render with the pinned requirements
    and, when an operator configures the existing read-only AWS profile/root, a
    bounded live-S3 pilot. Do not claim either was completed unless exercised.

    Update verification/plan only with new evidence. Preserve the existing
    implementation and offline results; canonical tool docs and the initial
    operation-log entry already exist.

## Handoff Summary

The confirmed v1 counts raw Parquet rows per event family/hostname over a
rolling 12-hour UTC interval, filters candidate `dayPK`/`hourPK` partitions
before reading with DuckDB, and displays one selected event family as host time
series. Manual refresh, adaptive buckets, linear/log absolute scaling, and an
optional normalized-to-host-peak mode are in scope. Unsupported host/time
schemas must be listed, not hidden.

## Primary Sources For The Dev Agent

- Analytics direct-S3 pattern: `streamlit/projects/SmokeTests/s3_source.py`,
  `streamlit/projects/SmokeTests/README.md`, and its focused S3 tests.
- Existing event summary chart: `streamlit/projects/DataQA/pages/raw_events.py`.
- Canonical input path and partition pruning:
  `../Wintap-PyUtil/wintap_dbt/README.md` and
  `../Wintap-PyUtil/wintap_dbt/macros/paths.sql`.
- S3 secret/credential setup:
  `../Wintap-PyUtil/wintap_dbt/macros/s3.sql`.
- Timestamp conversion:
  `../Wintap-PyUtil/wintap_dbt/macros/time.sql`.

## Recommended First Implementation Slice

Completed: offline tests cover environment validation, bounded partition
discovery, synthetic Parquet, FILETIME/native/ISO timestamps, hostname aliases,
schema drift, raw-row aggregation, normalization, budgets, and no-query-before-
manual-refresh behavior. Next: real app launch/render with the requirements and
operator-assisted bounded S3 verification.

## Non-Goals For This Slice

- No source, DBT, schema, uploader, S3-write, historical backfill, or sibling
  repository work.
- No assertion that missing rows mean the host is inactive or telemetry is
  complete.
- No cross-family semantic weighting or guessed timestamp conversion.

## Testing Expectations

Run the focused unittest command in the app README. Current tests use mocked
DuckDB glob results and do not use AWS credentials. Live S3 validation must be
read-only, manually invoked, bounded to the recent partitions, and use only the
operator's DBT-compatible dataset/AWS environment variables and existing profile.

## Closeout Instructions

- Update `wiki/work/recent-host-activity-dashboard/verification.md` with exact
  commands and results, distinguishing synthetic from live-S3 evidence.
- Update the done checklist in `implementation_plan.md`.
- Append a concise entry to `wiki/log.md`.
- Promote stable dashboard usage and source semantics into a canonical wiki page.
