---
title: "Feature Spike: Recent Host Activity Dashboard"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - streamlit/projects/SmokeTests/s3_source.py
policy: agent-editable
last_validated: 2026-11-10
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt; streamlit/projects/SmokeTests
tags: [host-activity, s3, duckdb, schema-spike, feature-work]
---

# Feature Spike: Recent Host Activity Dashboard

## Question

Can a 12-hour direct-S3 DuckDB query discover and aggregate the live bronze
event families by row hostname and true row timestamp with acceptably bounded
listing, object, and point counts?

## Hypothesis

The documented `dayPK`/`hourPK` tree is enough to restrict object discovery to a
small recent window. Several event families will expose usable host/time fields;
others can be excluded with a clear explanation.

## Experiment

When the operator's existing DBT-compatible dataset/AWS environment variables
and read-only profile are available, perform a read-only probe: list only
overlapping day/hour partitions, sample one schema per discovered family,
record safe field names/types and object counts, then query a bounded sample
using type-aware UTC conversion. Do not persist raw rows, credentials, bucket
identifiers, or endpoint values in the repository.

## Prototype Location

Offline implementation is complete in `streamlit/projects/HostActivity/` and
uses synthetic Parquet fixtures plus mocked DuckDB glob results. A bounded
read-only live pilot is recorded below; no temporary work belongs in a sibling
repository.

## Results

Offline verification passed 18 focused tests in the app-scoped UV environment
(DuckDB 1.5.6, Streamlit 1.67.0, Altair 6.3.0, Pandas 2.3.3). Streamlit
`AppTest` renders the initial state without an exception and confirms no source
query occurs before manual refresh; a mocked explicit refresh exercises the
selected-family progress/status path. A bounded live probe used 13 overlapping
hour partitions, found 3,988 objects across 8 families in about 26 seconds,
inspected `raw_process` and `raw_process_conn_incr`, and queried bounded data.
`raw_process` aggregation took about 67 seconds; `raw_process_conn_incr` had no
rows inside the exact event-time interval. The user's all-family refresh took at
least five minutes, and `pidstat` exceeded the 2-million-row cap. A selected-
family `raw_host` probe over 59 objects took about 5 seconds and found no
exact-window rows. The app now scans only the selected family after an explicit
click. Code review confirmed
that glob patterns scope discovery to each requested event/day/hour prefix;
returned keys are checked against that same partition set, and per-family row
stats and chart groups share one materialized scan. Per-family latency and
`pidstat` budget handling remain open; no sensitive source values or raw rows
were retained.

## Recommendation

Offline and initial UI verification plus a bounded live probe are complete.
Next, validate selected-family latency and `pidstat` budget handling before
claiming operational verification. Fail closed on unknown timestamp encodings
or exceeded budgets.

## Follow-Ups

- Record supported/skipped family names and sanitized reasons in
  `verification.md` after the operator pilot.
- If partition-hour keys do not cover event-time-window data reliably, present
  the observed limitation rather than silently expanding to a history scan.
