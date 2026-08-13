---
title: "Tension: DBT/DuckDB Canonical Output vs. Legacy stdview Parquet Expectations"
type: tension
status: open
poles:
  - "Wintappy's DBT pipeline is now canonical: it builds bronze/silver/gold models from raw_sensor parquet into a DuckDB database, and parquet export is explicit future work, not yet implemented."
  - "Wintap-Analytics' documented entry points for research (ACME4 Explore, workshop SQL, LLNL's HTTP-published dataset) are built around discovering and reading standard-view (stdview-*) parquet files, a historical layer Wintappy's own docs mark as superseded."
resolution: null
confidence: medium
grounded_by:
  - ../Wintappy/review-notes/DataModel.md
  - ../Wintappy/review-notes/OpenQuestions.md
  - ../Wintap-Analytics/2025-acme4-explore/README.md
  - ../Wintap-Analytics/workshop/5_SQL_Exploration.md
policy: agent-editable
last_validated: 2026-08-11
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
source_paths: ../Wintappy/review-notes/DataModel.md; ../Wintappy/review-notes/OpenQuestions.md; ../Wintap-Analytics/2025-acme4-explore; ../Wintap-Analytics/workshop
tags: [tension, wintappy, dbt, parquet, cross-repo]
---

# Tension: DBT/DuckDB Canonical Output vs. Legacy stdview Parquet Expectations

## Tension

Wintappy's own data-model notes mark the historical `stdview-*`/`stdview` parquet layer as "superseded by DBT silver/gold DuckDB output for current work," with parquet export noted only as something that "may recreate this shape later." The `merged` and `rolling` historical layers are similarly deprecated or superseded.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/DataModel.md §Current model layers -->

At the same time, Wintappy's own open-questions tracker lists implementing DBT parquet export as high priority precisely because "some notebooks and published workflows still expect `stdview-*` parquet directories," and separately flags that "Analytics/notebook expectations vary" between older pipenv/make flows using published `stdview` URLs and ACME4 Explore's modern `uv`-based structure.
<!-- GROUND_TRUTH: ../Wintappy/review-notes/OpenQuestions.md §2. Implement DBT parquet export -->
<!-- GROUND_TRUTH: ../Wintappy/review-notes/OpenQuestions.md §10. Analytics/notebook expectations vary -->

On the Wintap-Analytics side, ACME4 Explore is documented as reading Wintap standard-view Parquet files "either from LLNL's HTTP-published dataset or a local dataset copy," and workshop SQL material documents process-centric queries over tables such as `process_uber_summary`, `process`, `process_path`, and `process_net_conn` without specifying that these are DBT DuckDB models rather than published parquet files.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-acme4-explore/README.md §Accessing the dataset -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/workshop/5_SQL_Exploration.md §Getting started with Wintap Data -->

## Why It Matters

A researcher following Wintap-Analytics' own workshop/ACME4 material today would reasonably expect a `stdview`-shaped parquet dataset to fetch or point DuckDB at. Wintappy's canonical pipeline currently produces only a DuckDB database with equivalently-named tables/views (`process`, `process_path`, `process_uber_summary`, etc.) and no parquet export. The table names line up, which reduces confusion once discovered, but the *distribution mechanism* (parquet directory vs. DBT-built DuckDB file) is not yet reconciled, and no wiki or repo page currently tells a new user which one to expect for a given dataset vintage.
<!-- SYNTHESIS: inferred from ../Wintappy/review-notes/DataModel.md, ../Wintappy/review-notes/OpenQuestions.md, and ../Wintap-Analytics/2025-acme4-explore/README.md -->

## Current Holding Pattern

Treat published/legacy `stdview-*` parquet datasets (e.g. ACME4's HTTP-published dataset) as a snapshot produced by the now-legacy Python ETL path, and treat DBT-built DuckDB databases as the current canonical output for newly processed datasets. Do not assume the two are kept in sync automatically until Wintappy implements parquet export.

## Resolution Criteria

This tension can move to `resolved` when either: Wintappy implements and documents a DBT parquet export step that reproduces the `stdview` directory contract, or Wintap-Analytics' analysis tooling is updated to read DBT-built DuckDB databases directly instead of expecting `stdview-*` parquet.

See also [[wiki/repo/wintappy-pipeline-repo]], [[wiki/repo/wintap-analytics-host-repo]], and [[wiki/workflow/future-experiment-analysis-workflows]].
