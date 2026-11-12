---
title: "Wintap / Lintap ETL data flow"
type: workflow
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../wintap/wintap/core/etl/load/RawSensorWriter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintap_dbt/README.md
  - ../Wintap-PyUtil/wintap_dbt/models/bronze
  - ../Wintap-PyUtil/wintap_dbt/models/silver
  - ../Wintap-PyUtil/wintap_dbt/models/gold
  - ../Lintap/teletap/README.md
policy: agent-editable
last_validated: 2026-11-11
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/wintap/core/etl/load; ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Lintap/teletap
tags: [wintap, lintap, wintap-pyutil, dbt, duckdb, etl, s3, bronze, silver, gold, drawio]
---

# Wintap / Lintap ETL data flow

The editable [draw.io diagram](wintap-etl-data-flow.drawio) follows host-local
sensor Parquet through delivery to S3 and Wintap-PyUtil's DBT build, with the
bronze → silver → gold model progression and the principal Makefile validation
targets.

## Read the flow

- Wintap and Lintap/TeleTap write canonical event Parquet to host-local
  `raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/` paths. The configured uploader
  sends eligible files to its S3 destination, preserving the relative layout.
  Failed uploads retain files for retry; successful upload may delete the local
  copy. Upload depends on the deployed adapter/destination configuration.
- Wintap-PyUtil can read a local dataset root or an S3 `raw_sensor` dataset
  directly. The input root/window are configured independently of the local
  DuckDB output path.
- `make dbt-build` performs the config check, source preflight, and DBT build.
  Bronze stages raw inputs and handles source variation; silver creates
  normalized detail models; gold builds analyst-facing summaries.
- The output is the configured local DuckDB database. DBT Parquet export is not
  implemented, so the diagram does not depict bronze/silver/gold Parquet objects
  being published back to S3.

## Core Makefile validation targets

Run these from the Wintap-PyUtil repository root:

| Target | What it checks / does |
|---|---|
| `make print-dbt-config` | Runs offline config checks and prints effective input root/type and date/hour window; does not print credentials. |
| `make dbt-check-config` | Checks the local or S3 raw-input configuration, date/hour window, and local DuckDB output location. |
| `make dbt-check-source` | Lists supported inputs in the selected partitions and reads one matching Parquet schema. This is a bounded access probe, not an all-file or all-row integrity scan. |
| `make dbt-build` | Runs config and source checks, then builds DBT models. |
| `make dbt-test` | Runs configured DBT model/data tests. |
| `make dbt-check-output` | Checks the configured local output path/database; this is the prerequisite for the dashboard targets, not a raw-source check. |
| `make qa-pid-hash` | Runs SQL checks for `pid_hash` relationship/orphan issues. |
| `make qa-dashboard` | Launches the PyUtil Marimo overview for built DBT relations and QA summaries. |
| `make qa-pidstat` | Launches the pidstat QA notebook. |

The two QA dashboard targets check that the local output root/database is
available; they do not establish raw-input availability. Queries over raw-backed
bronze views still need access to their configured local or S3 source. A passing
source preflight proves only bounded access/schema evidence, not complete dataset
integrity or semantic quality. These dependencies and limits are reflected in the
diagram.

Related: [[wiki/repo/wintap-primary-sensor-repo]],
[[wiki/repo/lintap-supporting-repo]],
[[wiki/component/sensor-upload-cache-pipeline]],
[[wiki/repo/wintappy-pipeline-repo]], and
[[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]].
