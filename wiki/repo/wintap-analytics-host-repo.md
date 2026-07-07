---
title: "Wintap-Analytics Host Repository"
type: repo
confidence: high
grounded_by:
  - ../Wintap-Analytics/README.md
  - ../Wintap-Analytics/requirements.txt
  - ../Wintap-Analytics/2025-acme4-explore/README.md
  - ../Wintap-Analytics/workshop/5_SQL_Exploration.md
policy: agent-editable
last_validated: 2026-06-29
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: ../Wintap-Analytics/README.md; ../Wintap-Analytics/requirements.txt; ../Wintap-Analytics/2025-acme4-explore; ../Wintap-Analytics/workshop
tags: [Wintap-Analytics, research-workflows, repo]
---

# Wintap-Analytics Host Repository

`../Wintap-Analytics` is the wiki host repository and a collection of tooling for analyzing and inspecting Wintap data.
<!-- GROUND_TRUTH: ../Wintap-Analytics/README.md §Wintap-Analytics -->

The baseline Python requirements show a DuckDB/Jupyter/pandas/NetworkX/matplotlib-oriented analysis stack, with packages such as `duckdb`, `duckdb-engine`, `ipykernel`, `ipython`, `ipywidgets`, `matplotlib`, `networkx`, `numpy`, `pandas`, `scipy`, and SQLAlchemy.
<!-- GROUND_TRUTH: ../Wintap-Analytics/requirements.txt §requirements -->

## Current Analysis Shape

The ACME4 Explore subproject is a Jupyter/uv/DuckDB workflow for exploratory analysis and auditing of the ACME4 host-based dataset, with a focus on Wintap standard-view Parquet files and reusable methods for similar host-defense datasets.
<!-- GROUND_TRUTH: ../Wintap-Analytics/2025-acme4-explore/README.md §ACME4 Explore -->

Workshop material documents process-centric SQL exploration over Wintap tables such as `process`, `process_path`, `process_net_conn`, and `process_uber_summary`, including process-path representations, process-to-process network joins, labels, MITRE/SIGMA hits, and LOLBAS summaries.
<!-- GROUND_TRUTH: ../Wintap-Analytics/workshop/5_SQL_Exploration.md §Getting started with Wintap Data -->

## Wiki Role

This repo owns the wiki under `wiki/`, external source copies under `raw/`, and analysis-oriented documentation topics. It should not be treated as the primary source for Wintap sensor internals; those belong to `../wintap`.
<!-- SYNTHESIS: inferred from ../Wintap-Analytics/AGENTS.md, ../Wintap-Analytics/README.md, and ../wintap/README.md -->

See also [[wiki/workflow/future-experiment-analysis-workflows]] and [[wiki/repo/wintap-primary-sensor-repo]].
