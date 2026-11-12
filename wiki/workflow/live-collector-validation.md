---
title: "Live-collector validation"
type: workflow
confidence: high
grounded_by:
  - ../wintap/devtools/telemetry_smoke_workload.py
  - ../wintap/devtools/smoke_manifest.py
  - ../wintap/devtools/smoke_parquet.py
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - validation/telemetry-soak/run-smoke-soak.sh
  - validation/telemetry-soak/README.md
  - streamlit/projects/SmokeTests/main.py
  - streamlit/projects/SmokeTests/page_views.py
  - streamlit/projects/SmokeTests/analysis.py
  - streamlit/projects/SmokeTests/README.md
  - https://docs.astral.sh/uv/pip/environments/
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/devtools; ../wintap/wintap/core/etl/load; validation/telemetry-soak; streamlit/projects/SmokeTests
tags: [live-collector-validation, smoke-test, canary, drawio, linux, s3, raw_smoke_test]
---

# Live-collector validation

**Live-collector validation** is the working name for the workflow previously
described as “in situ testing”: generate known host activity while the deployed
collector runs, publish expected-activity evidence alongside its telemetry, then
check the delivered data. “Live” describes the collector; analysis follows normal
ETL/upload latency. A repeated bounded run is a **telemetry canary**.
<!-- SYNTHESIS: ../wintap/devtools/telemetry_smoke_workload.py; validation/telemetry-soak/README.md; streamlit/projects/SmokeTests/README.md -->

## Editable diagram

Open **[live-collector-validation.drawio](live-collector-validation.drawio)** in
diagrams.net / draw.io. It contains two editable pages:

1. **Data and evidence** — Linux host, root-run stimulus, independent collector,
   local telemetry and `raw_smoke_test`, shared uploader, S3 and analysis machine.
2. **Operator workflow** — persistent Python setup, sudo execution, publication
   and delivery checks, dashboard validation, one-shot versus recurring use.

Use [[wiki/tool/named-telemetry-smoke-workload]] for full copy-paste commands;
diagram command labels summarize those steps. Wintap owns stimulus/evidence and
collector code; Analytics owns recurring orchestration, dashboard and this wiki;
Lintap supplies installed-service packaging/path conventions.

**First-time dashboard setup (P7):**
[Configure and launch Streamlit against S3](../tool/smoke-test-results-dashboard.md#configure-and-launch-against-s3)
covers the analysis-machine JSON config, AWS credentials, launch command and browser URL.

## Page 1 anchors: data and evidence

| Anchor | Meaning and source |
|---|---|
| L1 | Persistent user-created Python venv with DuckDB, invoked later through sudo. See the [uv environment reference](https://docs.astral.sh/uv/pip/environments/) and the corrected setup in [[wiki/tool/named-telemetry-smoke-workload]]. |
| L2–L4 | Named workload produces real process/thread, file and socket activity plus local JSON selectors. The periodic runner adds separately identified `canary-*` families. Sources: `../wintap/devtools/telemetry_smoke_workload.py`; `validation/telemetry-soak/run-smoke-soak.sh`. |
| L5–L6 | Already-running sensor feeds its normal attribution/ETL/merge path; uploaded HOST receipts supply startup context. [[wiki/component/fileops-event-pipeline]], [[wiki/component/sensor-upload-cache-pipeline]], [[wiki/schema/runtime-capability-receipt]]. |
| L7–L8 | Shared wrapper and optional DuckDB publisher write start/first-selectors/final evidence snapshots to `DATA_ROOT/raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH/`. Sources: `../wintap/devtools/smoke_manifest.py`; `../wintap/devtools/smoke_parquet.py`. |
| L9–L10 | Existing collector upload sweeps finalized parquet using deployed adapter configuration. Successful transfer may remove the local file. Source: `../wintap/wintap/core/etl/load/CacheManager.cs` (`WorkerThread_DoWork`, `upload`). |
| L11 | Dashboard discovers portable manifests from S3 evidence parquet; Overview is manifest-only. Source: `streamlit/projects/SmokeTests/main.py`; `page_views.py` (`overview_page`). |
| L12–L13 | Explicit selected-run validation compares recorded expectations to matching telemetry. Source: `streamlit/projects/SmokeTests/page_views.py` (`test_page`); details in [[wiki/tool/smoke-test-results-dashboard]]. |

Blue arrows trace activity/collected telemetry; green arrows trace expected-activity
evidence; purple denotes shared delivery; dashed gray denotes operator or local
artifact handoffs. Layout is a dataflow view, not a strict timeline: the publisher
can emit an initial snapshot before stimulus completes.

**The independent branches meet at analysis.** `raw_smoke_test` records stimulus
facts and expectations. It does not prove that the collector recorded those events.
Manifest UUIDs identify runs; matching raw events requires hostname, UTC window,
PID/TID, file paths and socket endpoints. Raw telemetry does not carry the smoke UUID.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §smoke_run; ../wintap/devtools/telemetry_smoke_workload.py §main; streamlit/projects/SmokeTests/README.md §Collection host and analysis host can differ, Pages and lazy validation -->

## Page 2 anchors: operator workflow

| Anchors | Operator checkpoint |
|---|---|
| P1–P3 | Collector startup complete; actual local data root identified; persistent Python/DuckDB environment imports successfully through sudo. |
| P4 | Fresh workload/output/manifest; explicit `--smoke-data-root` points to the directory containing `raw_sensor`. |
| P5 | Observe `generated`, `Smoke parquet:` and `Smoke manifest:` independently. Export warnings can accompany a successful workload exit. |
| P6–P7 | Allow normal delivery, then refresh the correctly configured S3 dataset/window and locate the run. Arrival time and run time can differ. |
| P8–P9 | Canary Tests → exact run → **Validate selected run**. Inspect per-case matches, missing expectations, skipped cases and violations. |
| C1 | One named `telemetry-workload` run; native helper optional. |
| C2 | Expanded periodic canaries use five family manifests and a shared `canaryRoundId`; start with `--rounds 1`. **Run all validations for this canary** is the round-level action. |

Commands and semantics are grounded in the named-workload guide, shared publisher,
runner and dashboard sources cited above. The persistent venv fixes the earlier
temporary `uv run --with` interpreter handoff: a `builds-v0/.tmp.../bin/python`
path may be gone by the time sudo executes it.
<!-- SYNTHESIS: operator-reported 2026-10-30 handoff failure documented in wiki/tool/named-telemetry-smoke-workload.md; https://docs.astral.sh/uv/pip/environments/ -->

## Reading the outcome

Track **generated → published locally → delivered → validated** as separate
checkpoints. A named workload can remain yellow after useful telemetry matches
because it is stimulus-only or includes skips. Missing data stays incomplete;
contradictory observations need investigation. Normal aggregation/sampling means
OS operations and telemetry rows are not necessarily one-to-one.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §_publish; ../wintap/devtools/telemetry_smoke_workload.py §main; streamlit/projects/SmokeTests/page_views.py §test_page; streamlit/projects/SmokeTests/README.md -->

Related: [[wiki/tool/named-telemetry-smoke-workload]],
[[wiki/tool/periodic-telemetry-soak-runner]],
[[wiki/tool/smoke-test-results-dashboard]].
