---
title: "Wintap-Analytics Host Repository"
type: repo
confidence: high
grounded_by:
  - ../Wintap-Analytics/README.md
  - ../Wintap-Analytics/requirements.txt
  - ../Wintap-Analytics/2025-acme4-explore/README.md
  - ../Wintap-Analytics/workshop/5_SQL_Exploration.md
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-08-11
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

## Pipeline Dependency on Wintappy

This repo's Streamlit tooling has a direct code dependency on the Wintappy (`Wintap-PyUtil`) package, not just its output data: `streamlit/projects/common/dqautil.py` imports `wintappy.datautils.rawutil`, and `streamlit/projects/DataQA/pages/raw_events.py` imports `wintappy.datautils.stdview_duckdb`.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/common/dqautil.py §import wintappy.datautils.rawutil -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py §import wintappy.datautils.stdview_duckdb -->

Wintappy is the canonical DBT/DuckDB post-processing pipeline that produces the standard-view tables (`process`, `process_path`, `process_uber_summary`, etc.) this repo's notebooks, workshop material, and Streamlit apps query; see [[wiki/repo/wintappy-pipeline-repo]]. There is an open cross-repo tension over whether that pipeline's current DuckDB-only output matches this repo's expectations of published `stdview-*` parquet datasets; see [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]].
<!-- SYNTHESIS: inferred from ../Wintappy/review-notes/Architecture.md and this repo's streamlit/workshop/2025-acme4-explore usage -->

## Wiki Role

This repo owns the wiki under `wiki/`, external source copies under `raw/`, and analysis-oriented documentation topics. It should not be treated as the primary source for Wintap sensor internals; those belong to `../wintap`. It should also not be treated as the primary source for canonical ETL/post-processing; that belongs to `../Wintappy`.
<!-- SYNTHESIS: inferred from ../Wintap-Analytics/AGENTS.md, ../Wintap-Analytics/README.md, ../wintap/README.md, and ../Wintappy/review-notes/Architecture.md -->

See also [[wiki/workflow/future-experiment-analysis-workflows]], [[wiki/repo/wintap-primary-sensor-repo]], and [[wiki/repo/wintappy-pipeline-repo]].
