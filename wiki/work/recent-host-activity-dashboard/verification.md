---
title: "Verification: Recent Host Activity Dashboard"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/HostActivity/test_host_activity.py
  - streamlit/projects/HostActivity/README.md
  - streamlit/projects/HostActivity/main.py
policy: agent-editable
last_validated: 2026-11-10
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/recent-host-activity-dashboard
tags: [host-activity, verification, feature-work]
---

# Verification: Recent Host Activity Dashboard

## Test Commands

- `uv run python -m unittest discover -s . -p 'test_*.py' -v` from
  `streamlit/projects/HostActivity/` — 23 tests passed in the app's locked UV
  environment (DuckDB 1.5.6, Streamlit 1.67.0, Altair 6.3.0, Pandas 2.3.3).
- `uv run python -m compileall -q .` from the app directory — passed.
- `uv lock --check` — passed; the app-scoped `uv.lock` is current.
- `git diff --check` from the repository root — passed.

The app uses `pyproject.toml` and an app-scoped `uv.lock`; no pip requirements
file or DBT runtime is needed.

## Manual Checks

- Streamlit `AppTest` rendered the app with no exceptions, showed the selected-
  family control and manual refresh button, and confirmed neither initial
  render nor changing families creates a snapshot/query before the button is
  clicked. A subsequent AppTest refresh with mocked S3/query helpers verified
  selected-family-only discovery, connection closure, timestamp-source display,
  the over-budget no-chart path, and elapsed-time status without contacting S3.
- A focused mocked refresh test verified listing, schema, and aggregation
  progress messages and the completed status state.
- Synthetic Parquet verified FILETIME, native timestamp, ISO-offset timestamp,
  Unix-second numeric/string `EventTime`, file `FirstSeen`/`LastSeen` priority,
  connection-increment FILETIME bounds, exact-window filtering, hostname aliases
  (including `Computer`), mixed host/time-column schema drift, blank/null
  hostname accounting, adaptive buckets, and row/point budgets.
- Mocked discovery verified event/day/hour-scoped globs, nested `protoPK`
  preservation, path deduplication, exclusion/rejection of out-of-window hour
  objects, file-budget failure, and out-of-root rejection.
- `secret_sql` configuration was unit-tested, including DBT-compatible bare
  endpoint authority syntax.
- An initial bounded read-only pilot using the operator-provided environment found 3,988
  object paths across 8 families and 13 overlapping hourly partitions; listing
  took about 26 seconds. `raw_process` (1,226 objects) took about 19 seconds for
  schema inspection and 67 seconds for aggregation (1,305,103 exact-window rows,
  6 hosts, 598 chart points). `raw_process_conn_incr` (990 objects) took about
  17 seconds for schema inspection and 7 seconds for aggregation, with no rows
  under the then-current EventTime-as-FILETIME interpretation. A follow-up
  confirmed those families' integer EventTime fields are Unix seconds, and the
  app now uses family-specific timestamp semantics. With corrected decoding,
  `raw_host` (62 objects) aggregated 59 exact-window rows across 6 hosts in about
  0.5 seconds; `raw_process_conn_incr` (972 objects) aggregated 157,821 rows,
  5 hosts and 479 points in about 25 seconds after schema inspection.
- For `raw_process_file`, the serializer writes EventTime as Unix seconds but
  preserves the 10-second batch's event-time bounds as FILETIME `FirstSeen` and
  `LastSeen`. The previous app decoded Unix EventTime as FILETIME, mapping a
  bounded 2,000,001-row sample to 1601 and yielding a misleading empty chart.
  The corrected `FirstSeen` query found about 7.9 million rows in the reported
  exact 12-hour window. The existing 2-million-row cap remains unchanged; the
  before the family-specific aggregate-only path, the dashboard failed closed
  after about 60 seconds at the 2-million-row cap.
  No root, endpoint, object key, host value, credential, or raw event row was
  retained.
- **Initial high-volume strategy probe:** a read-only DuckDB feasibility
  query grouped the entire selected `raw_process_file` interval directly by row
  hostname and five-minute event-time bucket instead of first materializing raw
  rows up to the 2-million limit. Across 502 discovered objects it counted
  7,923,378 exact-window rows, 5 hosts, 479 nonempty host/bucket groups, and no
  rows without a hostname in about 20 seconds. The theoretical five-minute chart
  size is 5 × 144 = 720 points, under the existing 1,000-point budget. The query
  returned only aggregate summary values; it did not fetch the chart series or
  expose host values/raw rows. A subsequent existing-cap query on the same file
  list took 4.9 seconds after the feasibility query had already read the objects,
  so that warm-cache timing is not a comparable cold-run baseline. This supports
  feasibility, not yet an end-to-end performance guarantee. The candidate still
  scans every qualifying row; adopting it would replace the raw-row guard with
  explicit runtime, memory/intermediate-group, and final-point safeguards. The
  operator then authorized implementation.
- **Implemented live validation:** the dashboard's actual `aggregate_family`
  path ran against 513 currently discovered `raw_process_file` objects. In about
  19.9 seconds it returned the complete exact result: 7,923,378 host-attributed
  rows, 5 hosts, five-minute buckets, 479 chart points whose counts sum to the
  total, and zero rows without hostname. The 120-second timer, 1 GB DuckDB memory
  limit, 1 GB temp-storage limit, 20,000 intermediate-group limit, and 1,000
  final-point limit were active. This was a read-only live query; no S3 objects,
  raw rows, endpoint/root values, or hostnames were written to records.

## Results

Standalone app, DBT-compatible S3 source setup, schema-aware query/aggregation,
UV project/lock, launch guide, and offline tests were implemented. No source
schemas, raw files, or S3 objects were changed.

## Known Gaps

- The deployed root value and credential material are intentionally not
  recorded. Live coverage remains partial: `raw_process`, `raw_process_conn_incr`,
  `raw_process_file`, and `raw_host` were sampled, not every family. The
  user's previous all-family refresh took at least five minutes; `pidstat`
  exceeded the current 2-million-row budget. The app now scans one selected
  family per explicit click. Correct decoding produces chartable `raw_host`,
  `raw_process_conn_incr`, and `raw_process_file` results; the latter now uses
  exact aggregate-only grouping with its own resource guards. `raw_process` takes
  about 86 seconds and retains the standard raw-row cap. Per-family query latency,
  upload lag, performance under other source conditions, and acceptable
  operational latency remain open.

## Follow-Ups

- Exercise timeout and intermediate-group failures against representative
  high-volume inputs, and assess the 1 GB memory/temp limits on deployment hosts.
- Evaluate the `pidstat` raw-row cap and remaining families with the operator
  before operational acceptance. Distinguish bounded live evidence from
  synthetic tests.
