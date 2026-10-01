---
title: "Feature Brief: Improve ETL and QA"
type: concept
confidence: medium
grounded_by:
  - ../Wintappy/Makefile
  - ../Wintappy/notebooks/wintap_dbt_overview.py
  - ../Wintappy/wintap_dbt/dbt_project.yml
  - ../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/models/silver/pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/models/monitoring/build_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/telemetry_event_summary.sql
  - ../Wintappy/wintap_dbt/models/monitoring/file_chart.sql
  - ../Wintappy/wintap_dbt/models/monitoring/network_chart.sql
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/improve-etl-and-qa/brief.md
tags: [feature-work, wintappy, qa, dbt, pidstat, marimo]
---

# Feature Brief: Improve ETL and QA

## Problem

The current Wintappy DBT and QA stack is functional but structurally uneven.

- The canonical QA entry point already lives in `../Wintappy` (`make qa-dashboard` -> `notebooks/wintap_dbt_overview.py`), but some of its monitoring views still depend on raw-backed bronze models at runtime instead of relying only on the built DuckDB outputs.
- pidstat is conceptually just another telemetry event stream, but in practice it is not yet treated like a first-class family in the model stack or QA surface.
- The current pidstat path stops at bronze/silver (`stg_pidstat_metrics` -> `pidstat_metrics`) with no intentional gold layer, and the dashboard currently exposes pidstat more like an optional side table than a core event family.
- The older Analytics-side Streamlit/DataQA path still carries legacy assumptions and direct Wintappy imports that can conflict with the intended Wintappy-first QA contract.
- Across event families, the line between bronze, silver, gold, and monitoring outputs is not yet cleanly or consistently expressed.

The result is a QA and ETL contract that is harder to reason about, harder to verify end to end, and less coherent than it should be for ongoing development.

## Goals

- Clean up the Wintappy DBT model stack across event families so the bronze/silver/gold layering is more intentional and easier to reason about.
- Make pidstat a first-class telemetry family with explicit bronze, silver, and gold models.
- Rationalize the relationship between event-family models and QA/monitoring models so the Marimo QA dashboard has a cleaner canonical contract.
- Make Wintappy Marimo the canonical QA entry point.
- Align or explicitly retire obvious conflicts in this repo's older Streamlit/DataQA path so the ecosystem no longer presents multiple contradictory QA surfaces.
- Preserve support for current representative `raw_sensor` datasets unless the design later explicitly justifies a cleaner break.
- Produce stronger end-to-end verification than `dbt build` alone: a reproducible local build/test plus dashboard smoke against the resulting DuckDB.

## Non-Goals

- Rewriting every Analytics notebook or fully modernizing the older Streamlit/DataQA application.
- Forcing QA to read only gold models; bronze-backed QA views remain allowed when they are intentionally part of the design.
- Changing raw telemetry producer behavior in Wintap/Lintap sensors as part of this feature.
- Solving every historical stdview/parquet compatibility issue in one pass unless it is directly required for the new canonical QA contract.

## User-Facing Behavior

- A developer or researcher runs the canonical Wintappy DBT pipeline and gets a coherent set of bronze/silver/gold/monitoring outputs with clearer event-family boundaries.
- pidstat appears as a normal event family in the DBT stack and in QA, not as a special-case side path.
- `make qa-dashboard` opens the canonical Marimo QA surface over the built DuckDB with event-family and monitoring outputs that match the intended model contract.
- The older Analytics-side QA path either follows the same contract where it still exists or is clearly no longer the canonical route.

## Acceptance Criteria

- The Wintappy DBT model stack is reorganized enough that each targeted event family has an intentional bronze/silver/gold story, including pidstat.
- pidstat is materialized through explicit bronze, silver, and gold models and appears in the canonical QA surface as a first-class event family.
- The canonical Marimo QA dashboard queries against a coherent model contract and no longer depends on accidental legacy assumptions.
- Obvious cross-repo QA conflicts in this repo are either aligned to the new contract or explicitly retired/documented.
- A reproducible local dataset/env can run `dbt build` and `dbt test`, then smoke the QA dashboard successfully against the built DuckDB.
- Current representative `raw_sensor` datasets still build unless the eventual design explicitly records and justifies a deliberate compatibility break.

## Affected Areas

- `../Wintappy/wintap_dbt/models/bronze/`
- `../Wintappy/wintap_dbt/models/silver/`
- `../Wintappy/wintap_dbt/models/gold/`
- `../Wintappy/wintap_dbt/models/monitoring/`
- `../Wintappy/wintap_dbt/models/schema.yml`
- `../Wintappy/notebooks/wintap_dbt_overview.py`
- `../Wintappy/Makefile`
- This repo's older QA-related Streamlit/DataQA paths where they directly conflict with the new canonical contract

## References

See [[wiki/work/improve-etl-and-qa/references]].

## Open Questions

- What compatibility window should be preserved for existing model names, notebook queries, and downstream consumers?
- Which current monitoring outputs should remain monitoring views and which should become gold event-family models?
- Should compatibility aliases exist temporarily if major model renames are adopted?
- Which Analytics-side Streamlit/DataQA paths should be updated versus explicitly deprecated?

## Test Plan

- Build a reproducible local test configuration for the chosen representative dataset/env.
- Run `dbt build` and `dbt test` on the cleaned-up model stack.
- Smoke the canonical Marimo QA dashboard against the built DuckDB, including pidstat visibility and at least one non-pidstat event-family path.
- Add focused row/count/schema checks for the new pidstat bronze/silver/gold path once the target contract is defined.
- Verify that any remaining Analytics-side QA paths either still work against the new contract or are explicitly documented as non-canonical.

## Done When

- The feature's design records the intended bronze/silver/gold/monitoring contract and compatibility decisions.
- The implementation lands across `../Wintappy` and this repo as needed.
- Reproducible build/test/dashboard-smoke verification passes.
- Durable facts about the canonical QA contract and the event-family model organization are promoted into canonical wiki pages.
- `wiki/log.md` records the feature start and major progress checkpoints.
