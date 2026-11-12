---
title: "Feature Interview: Recent Host Activity Dashboard"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/SmokeTests/s3_source.py
  - streamlit/projects/SmokeTests/README.md
  - streamlit/projects/DataQA/pages/raw_events.py
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
policy: agent-editable
last_validated: 2026-11-10
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/SmokeTests; streamlit/projects/DataQA; ../Wintap-PyUtil/wintap_dbt
tags: [host-activity, streamlit, duckdb, s3, raw_sensor, feature-work]
---

# Feature Interview: Recent Host Activity Dashboard

## Initial Idea

> I now have several (6?) hosts that have Wintap/Lintap installed and are
> pushing data to a common S3 bucket. I need a simple, lightweight dashboard to
> show recent activity: total event types by host in a time-series chart. Event
> counts may vary enough to make scaling difficult. Start with the last 12
> hours, query bronze (`raw_sensor`) data in S3, and use DuckDB and Streamlit.

## Context Established Before Questioning

- `streamlit/projects/SmokeTests/s3_source.py` already demonstrates read-only
  DuckDB `httpfs` access to S3 using the normal AWS credential chain and a
  connection-scoped temporary secret. Its configuration accepts one or more
  dataset roots and rejects credential fields.
- The SmokeTests README describes roots that contain `raw_sensor/` (or the
  directory itself), including both a shared collection root and multiple
  host-specific roots. This documents supported shapes in that app, not the
  exact deployed bucket layout for this request.
- The current DataQA Raw Events page charts summary data with a 30-second bucket
  and notes that host-scaled chart height is problematic and bucket sizing
  should adapt to dataset duration.
- The live Wintap-PyUtil DBT README defines
  `<dataset>/raw_sensor/<event_type>/dayPK=YYYYMMDD/hourPK=HH/*.parquet`, with
  `protoPK=tcp|udp` nested below network-increment partitions. Its S3 input
  setting names the dataset root containing `raw_sensor/`; DBT narrows scans by
  day and optionally by hour. The source code does not identify the actual
  user's bucket prefix or prove whether hosts share one root.
- Bronze event families have different schemas and timestamp representations;
  `time.sql` includes an integer FILETIME-to-UTC conversion. The dashboard must
  inspect schemas and avoid treating every family row as an equal semantic
  event.

## Interview Log

### Round 1

**Q:** Where should the first dashboard live?
**A:** Standalone app under `streamlit/projects/`.
**Outcome:** decision — keep the activity dashboard independent of SmokeTests
and DataQA navigation.

**Q:** How should hosts be identified from the shared S3 bucket?
**A:** Investigate the bucket organization in `wintap_dbt`; event types live
under `raw_sensor/`, partitioned by `dayPK` and `hourPK`.
**Outcome:** delegated — use the DBT source contract to guide bounded discovery;
do not assume the path identifies a host. Actual root(s) and host placement in
the live dataset remain to be verified with operator configuration/data.

**Q:** Which chart layout?
**A:** Select an event type and compare host lines.
**Outcome:** decision — event-type selector with one series per host.

**Q:** Refresh behavior?
**A:** Manual refresh.
**Outcome:** decision — no automatic polling in the initial version.

### Round 2

**Q:** What should a count mean?
**A:** Count raw bronze Parquet rows and label them as rows.
**Outcome:** decision — use physical source-row counts, not a fabricated
cross-family logical-event total.

**Q:** How to handle families without usable host/time fields?
**A:** Skip and report them.
**Outcome:** decision — chart only families with usable row-level host and time;
show which families were excluded and why.

**Q:** Initial bucket resolution?
**A:** Adaptive, about five minutes by default and coarser at high volume.
**Outcome:** decision — keep plotted points bounded and display actual bucket
width.

## Decisions

- Standalone Wintap-Analytics Streamlit app; DuckDB reads raw Parquet directly
  from S3. No collector, uploader, DBT, or sibling-repository code changes.
- Rolling 12-hour UTC window evaluated at manual refresh, narrowed first by
  `dayPK`/`hourPK` and then by row timestamp.
- Read one dataset root and S3 parameters from the DBT-compatible environment
  variables; derive host identity from row fields, not a presumed S3 prefix
  convention. `Computer` is confirmed as an accepted hostname alias.
- Count and label raw Parquet rows by event family, host, and time bucket.
- Event-family selector, host time series, adaptive bins (~5 minutes initially),
  linear/log absolute-count scaling, and a separate optional normalized-to-each-
  host-peak view.
- Skip unsupported schemas and report them rather than silently dropping them.
- Manual refresh only in v1.

## Constraints

- Start at 12 hours; do not scan all historical S3 data to construct the chart.
- S3 credentials stay in the normal local AWS profile/environment chain, never
  in committed or displayed configuration. Keep source access read-only.
- Treat event-row counts as activity indicators, not proof of complete capture
  or counts of underlying OS operations.
- Wintap-PyUtil and all sibling repositories remain read-only for this feature.

## Delegations

- Inspect the configured bucket roots and representative Parquet schemas during
  implementation. Support shared or host-specific roots only where the observed
  S3 layout justifies them; do not invent host identity from path names.
- Let the implementation choose a bounded adaptive-bucket algorithm and
  fail-closed listing/query budgets, with the chosen resolution visible.

## Deferred / Open Questions

- Which private S3 root(s), endpoint, and profile will the operator use?
- Which event families in the live data expose both hostname and a usable event
  timestamp, and what timestamp encoding does each use?
- What volume/object-count budget is comfortable for manual 12-hour refreshes?
- Upload lag and missing partitions may make the view incomplete; the dashboard
  is not a completeness or collector-health certification.

## Playback Summary

The human confirmed a standalone, read-only Streamlit/DuckDB dashboard over S3
bronze `raw_sensor` Parquet. It starts with a manually refreshed rolling 12-hour
UTC view; uses day/hour partitions for scan pruning; groups rows by event-family
and row hostname; offers one event-family at a time with host lines; and reports
families lacking usable row-level host/time. Counts are explicitly raw rows.
Adaptive buckets start near five minutes. Absolute counts support linear/log
scaling, with a separate normalized-to-host-peak view to compare patterns
without implying equal volume. The live bucket root and schema remain an
operator-data check. No sensor, DBT, or sibling-repository edits are in scope.

## Sealed — human estimates

The interaction selected “I’ll provide it” for each final estimate, but no
hours or dates were supplied. No estimate is inferred.

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available? (Forced counterfactual — answer even if you would not have
attempted it solo. The hours are the feature's solo-hours: the Velocity
numerator and portfolio weight. The calendar date absorbs weekends and
distractions.)**
**A:** Not supplied.

**Q: With the AI workflow, on what date do you predict this feature will be
available? (Calendar prediction, open date to availability.)**
**A:** Not supplied.
