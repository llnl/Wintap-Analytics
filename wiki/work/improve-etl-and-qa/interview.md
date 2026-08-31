---
title: "Feature Interview: Improve ETL and QA"
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
source_paths: wiki/work/improve-etl-and-qa/interview.md
tags: [feature-work, interview, wintappy, qa, dbt, pidstat]
---

# Feature Interview: Improve ETL and QA

## Initial Idea

"picking up where we are and going forward needs to become an llm-assisted-feature" for cleaning up `../Wintappy/wintap_dbt` data models and their use in QA, with pidstat treated as a normal event stream rather than a special case.

## Context Established Before Questioning

- `../Wintappy/Makefile` makes `qa-dashboard` run `marimo run notebooks/wintap_dbt_overview.py`, so the current canonical QA notebook already lives in `../Wintappy`.
- `../Wintappy/notebooks/wintap_dbt_overview.py` reads the built DuckDB directly and currently queries `build_summary`, `telemetry_event_summary`, chart views, and `pidstat_metrics`.
- `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` and `../Wintappy/wintap_dbt/models/silver/pidstat_metrics.sql` already give pidstat a bronze/silver foothold, but there is no pidstat-specific gold layer today.
- Several monitoring views (`build_summary`, `telemetry_event_summary`, `file_chart`, `network_chart`) still depend on raw-backed bronze models, so QA can require live raw-source access at query time.
- The older Analytics Streamlit/DataQA path still imports Wintappy helpers directly and carries legacy assumptions that can conflict with the intended Wintappy-first QA contract.
- Current wiki context already documents pidstat as an optional raw event in Wintappy and records the prior pidstat collector feature as closed.

## Interview Log

### Round 1

**Q:** For `improve-etl-and-qa`, what should the initial implementation scope cover?
**A:** Cross-repo incl Analytics.
**Outcome:** decision — feature spans `../Wintappy` and this repo, not just one repo.

**Q:** How explicit do you want pidstat to become in the canonical dbt model stack?
**A:** Full B/S/G first-class.
**Outcome:** decision — pidstat is to be promoted to a normal bronze/silver/gold event family.

**Q:** What should we preserve while cleaning this up?
**A:** Allow model renames.
**Outcome:** decision — compatibility shims are not required by default; cleaner canonical naming is allowed.

**Q:** What evidence should close the feature at minimum?
**A:** Need stronger end-to-end.
**Outcome:** constraint — done criteria must exceed a bare `dbt build`.

### Round 2

**Q:** What is the smallest useful center of gravity for this feature?
**A:** All event families cleanup.
**Outcome:** decision — this is not just a pidstat-only cleanup.

**Q:** What should the intended QA dashboard contract be after this feature?
**A:** Dashboard may read bronze too.
**Outcome:** constraint — the feature does not force a gold-only dashboard contract.

**Q:** How should we treat the older Streamlit/DataQA path in this repo during this feature?
**A:** Align or retire obvious conflicts.
**Outcome:** decision — fix or explicitly de-emphasize the conflicting Analytics-side path, but do not make it the primary QA surface.

**Q:** For the stronger end-to-end evidence, what minimum verification shape do you want?
**A:** Repro local build + dashboard smoke.
**Outcome:** decision — a reproducible local dataset/env with build/test/smoke verification is the minimum target.

### Round 3

**Q:** May this feature change the modeled semantics or naming of existing non-pidstat DBT outputs if that is the cleanest way to unify the stack?
**A:** Yes, structure and names may evolve.
**Outcome:** decision — process/file/network outputs may be reorganized if that produces a cleaner overall contract.

**Q:** What should be the canonical QA entry point after this feature?
**A:** Wintappy Marimo QA.
**Outcome:** decision — Wintappy Marimo becomes the canonical QA entry point.

**Q:** How much compatibility do you want for existing datasets and consumers during the cleanup?
**A:** Undecided.
**Outcome:** deferred — compatibility window stays open for design.

## Decisions

- Feature scope is cross-repo, centered on `../Wintappy` but including this repo where the older QA path conflicts.
- Scope covers all event families, not only pidstat.
- pidstat should become a first-class bronze/silver/gold event family.
- Model names and shapes may evolve if that yields a cleaner canonical stack.
- Wintappy Marimo is the intended canonical QA surface after the feature.
- Analytics Streamlit/DataQA should be aligned where it obviously conflicts or explicitly retired/de-emphasized where appropriate.
- Minimum verification target is reproducible local `dbt` build/test plus QA dashboard smoke against the built DuckDB.

## Constraints

- End-to-end verification must be stronger than a bare `dbt build`.
- Normal QA pages may still read bronze models if that remains useful; the feature does not impose a gold-only dashboard rule.

## Delegations

- The exact bronze/silver/gold contract across all event families is delegated to the later design stage.
- Whether compatibility aliases or model renames are preferable is delegated to design/implementation, subject to the open compatibility question.

## Deferred / Open Questions

- What compatibility window should be preserved for existing datasets, model names, notebooks, and downstream consumers?
- Which current monitoring views should stay as monitoring outputs versus be replaced by event-family-specific gold models?
- How much of the older Analytics Streamlit/DataQA path should be updated versus explicitly retired from canonical use?

## Playback Summary

`improve-etl-and-qa` is a cross-repo Wintappy-centered cleanup feature for the DBT model stack and QA usage across event families. The primary design intent is to make pidstat a first-class bronze/silver/gold event family while also cleaning up process/file/network and monitoring-model inconsistencies so the Marimo QA dashboard becomes the canonical, coherent QA surface. Existing model names and shapes may change if a cleaner contract results, but the compatibility window for existing datasets and consumers remains an explicit open question for design. The minimum success bar is a reproducible local build/test and dashboard smoke run against the resulting DuckDB.

## Sealed — human estimates

**Q: If you had to build this exact scope alone, without AI, how many working hours would it take? And on what date would it realistically have been available? (Forced counterfactual — answer even if you would not have attempted it solo. The hours are the feature's solo-hours: the Velocity numerator and portfolio weight. The calendar date absorbs weekends and distractions.)**
**A:** "2 weeks". No calendar date provided.

**Q: With the AI workflow, on what date do you predict this feature will be available? (Calendar prediction, open date to availability.)**
**A:** "2 days". No calendar date provided.
