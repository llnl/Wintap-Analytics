---
title: "Streamlit Apps: Focus, Overlap and Maintenance Review"
type: tool
confidence: medium
grounded_by:
  - ../Wintap-Analytics/README.md
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/pages.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/initial_page.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/dll_inspector.py
  - ../Wintap-Analytics/streamlit/projects/DataQA/pages/dll-queries.sql
  - ../Wintap-Analytics/streamlit/projects/DataQA/requirements.txt
  - ../Wintap-Analytics/streamlit/projects/DataQA/Dockerfile
  - ../Wintap-Analytics/streamlit/projects/eda/pages/graph_viz_page.py
  - ../Wintap-Analytics/streamlit/projects/eda/eda_settings.toml
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - ../Wintap-Analytics/streamlit/projects/common/process-queries.sql
  - ../Wintap-Analytics/streamlit/projects/common/wintapgraph.py
  - ../Wintap-Analytics/streamlit/projects/common/st_graph_util.py
  - ../Wintap-Analytics/streamlit/projects/HostActivity/README.md
  - ../Wintap-Analytics/streamlit/projects/HostActivity/main.py
  - ../Wintap-Analytics/streamlit/projects/HostActivity/s3_source.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/README.md
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/page_views.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/analysis.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/result_store.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py
  - ../Wintap-Analytics/annotations/acme4/caldera/caldera_explorer.py
  - ../Wintap-Analytics/annotations/acme4/caldera/README.md
  - ../Wintap-Analytics/streamlit/tools/cookiecutter/hooks/post_gen_project.py
  - ../Wintap-PyUtil/wintappy/datautils/stdview_duckdb.py
policy: agent-editable
last_validated: 2026-11-22
repo_scope: Wintap-Analytics
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects; streamlit/tools/cookiecutter; annotations/acme4/caldera; ../Wintap-PyUtil/wintappy/datautils
tags: [streamlit, research-workflows, maintenance, data-quality, duckdb]
---

# Streamlit Apps: Focus, Overlap and Maintenance Review

## Bottom Line

There are **five app entry points**, plus shared legacy helpers and a Cookiecutter
template. **DataQA and EDA are the strongest consolidation candidates**.
**HostActivity and SmokeTests are complementary**, while CALDERA Explorer serves
a separate report/annotation workflow. Preserve useful research capabilities
before retiring wrappers; older code is not automatically irrelevant.
<!-- SYNTHESIS: inferred from app entry points, page registries and contracts below. -->

This is a **source/documentation review at Analytics `e6ff8ed`**, not runtime or
usage certification. Reviewed pages, helpers, requirements, configuration,
tracked files, symlink/navigation targets and scoped git history. No app launch,
private dataset/S3 access, dependency installation, test rerun, code change or
deletion was performed for this review. Dispositions are recommendations, not
accepted architecture decisions.

## App Comparison

| App / location | Apparent focus | Data and output | Suggested disposition |
|---|---|---|---|
| **HostActivity** — `streamlit/projects/HostActivity/` | Is telemetry arriving, where is activity visible, and what compaction/status information is available? | One S3 dataset; default file counts/sizes over filename collect time, optional physical raw-row counts and experimental process-diversity heatmap. Pinned local advisory Status/Runs; raw/compacted partition-presence view. Session-local display, no S3 writes. | **Retain as the activity/availability dashboard.** User-activity heuristic is not session detection or health proof. |
| **SmokeTests** — `streamlit/projects/SmokeTests/` | Did a recorded workload/harness have the expected telemetry observations? | Local/mounted or multi-root S3 raw Parquet, JSON/durable manifests and HOST receipts. Explicit run/round validation; private summary JSON beside the dataset. | **Retain as the validation dashboard.** Does not execute workloads or replace all original harness assertions. |
| **DataQA** — `streamlit/projects/DataQA/` | What does a prepared dataset contain, and do lifecycle or DLL patterns look suspicious? | Legacy `dbhelpers/*.db` catalog, standard-view tables/macros and optional rolling Parquet. Dataset summary, event-volume bubble chart, lifecycle categories and DLL-gap chart. | **Consolidation candidate.** Preserve useful diagnostics, adapt their data contract, then retire the old shell only if legacy users no longer need it. |
| **EDA** — `streamlit/projects/eda/` | How do selected processes connect to ancestors and network endpoints? | Same legacy database chooser; `process`, `process_path`, `process_net_conn`, `process_summary`. NetworkX/Cytoscape graph, node details, local GraphML/JSON export. | **Consolidation candidate, not a capability duplicate.** Preserve graph exploration; current prototype is incomplete. |
| **CALDERA Explorer** — `annotations/acme4/caldera/caldera_explorer.py` | How are an operation report's nested records related? | Local read-only DuckDB and schema JSON; `_dlt_id`/`_dlt_parent_id` selections, child tables and schema trees. | **Keep as a labeled research proof of concept** if still used; otherwise archive by human decision. Not a telemetry-dashboard replacement. |

<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/HostActivity/main.py §main; ../Wintap-Analytics/streamlit/projects/HostActivity/README.md -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/SmokeTests/page_views.py §overview_page/test_page; ../Wintap-Analytics/streamlit/projects/SmokeTests/analysis.py §analyze_round; ../Wintap-Analytics/streamlit/projects/SmokeTests/result_store.py §location/save_result -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/pages/pages.py; ../Wintap-Analytics/streamlit/projects/DataQA/pages/initial_page.py; ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py; ../Wintap-Analytics/streamlit/projects/DataQA/pages/dll_inspector.py -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/eda/pages/graph_viz_page.py; ../Wintap-Analytics/streamlit/projects/common/wintapgraph.py §build_graph; ../Wintap-Analytics/streamlit/projects/common/st_graph_util.py §display_graph/export_graph -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/annotations/acme4/caldera/caldera_explorer.py §query_table/display_table_with_selection; ../Wintap-Analytics/annotations/acme4/caldera/README.md -->

## Duplication Versus Unique Value

### DataQA and EDA: identical shells, distinct substantive pages

Their `main.py`, requirements, Dockerfile, base-page class and Streamlit config
are **byte-identical**. READMEs are app-name variants of template text, still
claiming the apps do little beyond opening a database. Both use valid `common/`
and debug-page symlinks in this checkout; **shared helpers are not duplicate
copies or missing pages**. All registered navigation targets exist.
<!-- GROUND_TRUTH: DataQA/EDA main.py, requirements.txt, Dockerfile, pages/_base_page.py, .streamlit/config.toml, README.md and tracked symlinks under ../Wintap-Analytics/streamlit/projects. -->

Both reuse the database chooser, process/host/date summary, session-state utilities
and ad hoc SQL/debug page. A single maintained **dataset explorer with QA and graph
pages** could replace the two wrappers. However, lifecycle/DLL profiling and graph
investigation are different research functions, neither supplied by the modern apps.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/common/utils.py; ../Wintap-Analytics/streamlit/projects/common/page_frags.py; ../Wintap-Analytics/streamlit/projects/common/debug_page.py -->
<!-- SYNTHESIS: possible consolidation inferred from DataQA/EDA page registries; not approved implementation. -->

### DataQA versus HostActivity: related activity questions, different metrics

DataQA's Raw Events page is a **prepared-database volume chart**, not a raw-row
browser. It calls legacy `stdview_duckdb` with fixed 30-second buckets. The helper
mixes physical row counts for process/image events with summed `EventCount` for
file/network/registry. HostActivity's optional row mode counts **physical source
rows**; default mode measures **objects/bytes by filename collect time**. These
charts overlap in purpose, not measurement grain. A port must preserve or relabel
the old metric, not substitute counts silently.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py §page_content; ../Wintap-PyUtil/wintappy/datautils/stdview_duckdb.py §event_summary_metadata/create_event_chart; ../Wintap-Analytics/streamlit/projects/HostActivity/README.md §Dashboard semantics and limits -->

### DataQA versus SmokeTests: quality intent, different evidence

DataQA profiles Complete/Started/No start/Null/Same/Time Travel lifetimes and
gaps exceeding ten seconds between `raw_imageload` observations. Its active pages
have no recorded-workload expectation contract. SmokeTests evaluates explicit
run/host/time/PID/path/socket expectations. Prefer it for **known-stimulus
validation**, but it does not replace generic lifecycle or DLL continuity analysis.
A DLL gap alone is not proof of capture loss; the old canary overlay is unused code.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/common/analytics-ddl.sql §process_life_v1; ../Wintap-Analytics/streamlit/projects/DataQA/pages/dll-queries.sql; ../Wintap-Analytics/streamlit/projects/DataQA/pages/dll_inspector.py §combo; ../Wintap-Analytics/streamlit/projects/SmokeTests/page_views.py §test_page -->
<!-- SYNTHESIS: evidence strengths follow from query inputs, not the apps' names. -->

### Modern apps: adapter duplication, intentionally different policies

HostActivity and SmokeTests independently implement S3 setup/discovery, timestamp/
hostname normalization and rendering; neither uses the legacy `common` framework.
Possible future sharing is **low-level source utilities**, not an immediate app merge:

- HostActivity takes one containing dataset root via DBT/AWS environment variables;
  SmokeTests takes private JSON, supports multiple roots or `raw_sensor` itself,
  and also supports local/mounted data.
- HostActivity manually refreshes hour-scoped activity with filename/family-aware
  timestamps. SmokeTests relists day-scoped evidence on reruns but scans telemetry
  only on explicit validation, using portable-run normalization.
- Availability/advisory diagnostics are not workload validation. SmokeTests also
  has a private summary-write path; HostActivity issues no S3 writes. Neither
  certifies complete sensor capture.

<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/HostActivity/s3_source.py §load_settings/iter_partition_hours; ../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py §load_config/dataset_parts/day_range; ../Wintap-Analytics/streamlit/projects/SmokeTests/queries.py §prepare_data; both app READMEs. -->

CALDERA's schema tree is a **report-table hierarchy**, not EDA's process/network
graph. Its explorer implements no telemetry join or label-generation workflow;
those would be separate annotation-analysis work.
<!-- GROUND_TRUTH: ../Wintap-Analytics/annotations/acme4/caldera/caldera_explorer.py -->

## Concrete Staleness / Incompleteness Evidence

| Finding | Source evidence and implication |
|---|---|
| **Incomplete legacy install recipes** | DataQA/EDA requirements contain only Dynaconf and Streamlit 1.33.0. Imports also need DuckDB, pandas, Altair and Wintappy; EDA needs NetworkX/Jinja2/`st_cytoscape`. Root requirements do not supply Wintappy or `st_cytoscape` either. Local recipes are not self-contained environments. |
| **Old container scaffold** | Identical Dockerfiles use `python:3.8-slim`, copy only the app and install the two-line requirements. External relative helper symlinks are not an independently bundled package. No container build/runtime was tested. |
| **Confirmed EDA asset mismatch** | Settings use `common/Wintap.PNG`; tracked asset is `Wintap.png`. Configured path is absent on this case-sensitive checkout; no UI failure was reproduced. |
| **Unwired EDA inputs** | IP address, port and Max Seeds are collected but not passed to `build_graph`; its `num_seeds` parameter is also unused. These controls do not implement their apparent filtering/bounding intent. |
| **Explicit graph prototype** | Helper says incomplete/being rewritten. Search text enters Jinja SQL instead of bound parameters; details always query `process_summary`, even when a non-process node is selected. Review before advertising supported general exploration. |
| **Unused DataQA prototype** | `dll_inspector.combo()` explicitly retains broken unused code with undefined old variables/APIs. Unused canary SQL has a fixed March 2024 lower bound. This does not establish that the active DLL-gap chart is unused or broken. |
| **Narrow legacy data contract** | Chooser recognizes only `dbhelpers/*.db`; attaches read-only and creates memory views. Pages expect legacy tables/macros/rolling Parquet. Shared displayed `data_range` uses process termination times, not independent collection coverage. A readable current DBT DB alone does not establish page compatibility. |
| **CALDERA launch/default mismatch** | README launches from `annotations/acme4/`; default schema/DB are bare cwd-relative filenames. Checked-in schema is in `caldera/`, not the launch directory. Paths can be entered; actual DB placement was not inspected. Startup immediately opens the default DB without a missing-file guard. |
| **Different maintenance evidence** | Scoped checkout history: DataQA/EDA/common/template last matching commit `6271438` (2026-07-06); CALDERA explorer/README/project manifest `fe808aa` (2026-07-06). HostActivity has November work through the November 22 test move; SmokeTests through `ab2324b` (2026-10-26). Squashed history is not actual last use or proof of abandonment. |
| **Different regression scaffolding** | Tracked `test_*.py`: HostActivity 3 modules, SmokeTests 8; none under DataQA, EDA or CALDERA. Scoped inventory, not test execution or proof of no external coverage. Prior HostActivity 59-case destination pass is recorded separately. |

<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/requirements.txt; ../Wintap-Analytics/streamlit/projects/eda/requirements.txt; ../Wintap-Analytics/requirements.txt; both Dockerfiles; DataQA/EDA imports and tracked symlinks. -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/eda/eda_settings.toml; ../Wintap-Analytics/streamlit/projects/common/Wintap.png; ../Wintap-Analytics/streamlit/projects/eda/pages/graph_viz_page.py §search_form; ../Wintap-Analytics/streamlit/projects/common/wintapgraph.py §build_graph/search_sql; ../Wintap-Analytics/streamlit/projects/common/st_content_util.py §display_node -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/pages/dll_inspector.py §combo; ../Wintap-Analytics/streamlit/projects/DataQA/pages/dll-queries.sql §canaries; ../Wintap-Analytics/streamlit/projects/common/dqautil.py §getdbs/getdbcon; ../Wintap-Analytics/streamlit/projects/common/process-queries.sql §data_range -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/annotations/acme4/caldera/README.md §Running; ../Wintap-Analytics/annotations/acme4/caldera/caldera_explorer.py §sidebar configuration/load_schema; scoped git log/tracked-file checks at Analytics e6ff8ed. -->

## Recommended Review Order

1. **Retain HostActivity and SmokeTests separately.** Clarify availability versus
   known-stimulus validation in navigation rather than merging working semantics.
2. **Confirm whether legacy exploration still has users.** If yes, consider one
   explorer with summary/lifecycle QA/graph pages. Keep DLL inspection if Windows
   image-load continuity remains useful. Qualify exact legacy/DBT schemas before
   moving pages; otherwise archive wrappers while preserving useful SQL/algorithms.
3. **Make CALDERA's status explicit:** clearly labeled research proof of concept or
   archived reference after confirming report/annotation needs, not based on age alone.
4. **Treat Cookiecutter as infrastructure, not a sixth app.** It generates legacy
   shell/dependency/symlink patterns. Freeze or modernize only if still used for new
   apps; do not assume it is the modern-dashboard template.

<!-- SYNTHESIS: recommendations from inventory and existing compatibility tension; human prioritization/code authorization required. -->
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/tools/cookiecutter/hooks/post_gen_project.py; ../Wintap-Analytics/streamlit/tools/cookiecutter/{{cookiecutter.project_slug}}/requirements.txt -->

The existing [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]] remains
open. No new feature skeleton or retirement decision was created. See
[[wiki/tool/recent-host-activity-dashboard]], [[wiki/tool/smoke-test-results-dashboard]],
[[wiki/repo/wintap-analytics-host-repo]], [[wiki/workflow/future-experiment-analysis-workflows]],
and [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].
