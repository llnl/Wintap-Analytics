---
title: "Future Experiment Analysis Workflows"
type: workflow
confidence: high
grounded_by:
  - ../Wintap-Analytics/2025-acme4-explore/README.md
  - ../Wintap-Analytics/2025-acme4-explore/src/acme4_explore/__init__.py
  - ../Wintap-Analytics/notebooks/ProcessTrees.md
  - ../Wintap-Analytics/workshop/5_SQL_Exploration.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: process
audience: mixed
status: draft
source_paths: ../Wintap-Analytics/2025-acme4-explore; ../Wintap-Analytics/notebooks; ../Wintap-Analytics/workshop
tags: [todo, research-workflows, Wintap-Analytics]
---

# Future Experiment Analysis Workflows

This page tracks analysis workflows that should become first-class wiki topics as the Wintap-Analytics documentation matures.

## ACME4 Explore

ACME4 Explore is a notebook-driven research surge for exploratory analysis and auditing of the ACME4 host-based dataset. It uses Python, Jupyter, `uv`, DuckDB, and Wintap standard-view Parquet files, either from LLNL's HTTP-published dataset or a local dataset copy.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-acme4-explore/README.md §ACME4 Explore; §Getting started; §Accessing the dataset -->

The `connect_db()` helper installs/loads DuckDB `httpfs`, discovers Parquet files over HTTP or local filesystem, creates a DuckDB view per Parquet file, and overlays local work artifacts from `.work/*.parquet` as additional views.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-acme4-explore/src/acme4_explore/__init__.py §connect_db -->

## Process Trees And Paths

Process-tree documentation should cover `Process`, `Process_Path`, `Process_Summary`, and `Process_Uber_Summary`, with `PID_HASH` and `PARENT_PID_HASH` as critical features. Existing notes distinguish process paths from process trees and call for APIs that can create whole-dataset trees, downward trees from a process, and downward trees from selected process sets.
<!-- GROUND_TRUTH: ../Wintap-Analytics/notebooks/ProcessTrees.md §Process Trees -->

Workshop SQL describes process paths as representations up to the root process, including string paths, lists of `pid_hash` values, and lists of `(pid_hash, process_name)` tuples. It also documents process-centric queries over `process_uber_summary`, `process`, `process_path`, and `process_net_conn`.
<!-- GROUND_TRUTH: ../Wintap-Analytics/workshop/5_SQL_Exploration.md §Process Paths -->

## Network Joins

Wintap analysis commonly joins two perspectives of the same network 5-tuple using `conn_id` to represent process-to-network-to-process links across hosts. The workshop material frames `conn_id` as a hash of local IP/port to remote IP/port plus protocol, where local/remote are relative to the host recording the row.
<!-- GROUND_TRUTH: ../Wintap-Analytics/workshop/5_SQL_Exploration.md §Potentially interesting inter-host communication -->

## Future Pages To Split Out

- Process tree concepts and API patterns.
- ACME4 standard-view dataset access.
- SQL workflow over `process_uber_summary` and related tables.
- Process classification JSON and process-name normalization.
- CALDERA/ACME4 annotation provenance and schemas.
- Streamlit/S3-backed dataset access.
