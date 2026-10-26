---
title: "DuckDB 2 upgrade: inventory and references"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/Directory.Packages.props
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../Wintappy/pyproject.toml
  - ../Wintappy/uv.lock
  - ../Lintap/uv.lock
  - ../Lintap/pidstat-collector-bootstrap.sh
  - ../Wintap-Analytics/streamlit/projects/common/dqautil.py
  - https://pypi.org/pypi/duckdb/json
  - https://api.nuget.org/v3-flatcontainer/duckdb.net.data.full/index.json
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../wintap; ../Wintappy; ../Lintap; streamlit; validation
tags: [duckdb, dependencies, dbt, compatibility, planning]
---

# DuckDB 2: inventory and references

## Live Repo Sources (2026-10-24)

| Owner / path | Observed baseline | Upgrade implications |
|---|---|---|
| Wintap `Directory.Packages.props`, target lockfiles | `DuckDB.NET.Data.Full` 1.5.6 | Wrapper and bundled native engine must be upgraded together; preserve existing .NET 10 SDK/package strategy. |
| Wintap `wintap/core/infrastructure/ProcessResolver.cs` | Persistent DuckDB store; typed process/lifecycle/heartbeat/gap tables | Test scalar parameters, TIMESTAMP precision, concurrent access, maintenance, restart/WAL and rollback. |
| Wintap `platform/windows/WintapCoreSvcMgr/BackupDatabaseManager.cs` | Separate backup/recovery reader/writer | Include in the same native-engine compatibility matrix, not just the Linux sensor. |
| Wintappy `pyproject.toml`, `uv.lock` | Python >=3.10,<3.13; DuckDB 1.5.5, adapter 1.9.6, dbt-core 1.12.2 locked | Raise Python minimum to 3.11; choose and test a pinned engine/adapter/core tuple. |
| Wintappy `requirements.txt` | Legacy DuckDB 1.1.1 pin | Do not mistake it for the current uv runtime; clarify current installation route, avoid a wholesale legacy refresh. |
| Wintappy `wintap_dbt/profiles.yml` | Four threads; `httpfs` and `parquet` extensions | Test worker isolation, extension availability and offline provisioning; use new output paths. |
| Lintap `pyproject.toml`, `uv.lock` | Python >=3.11,<3.13; DuckDB >=1.5.2, lock 1.5.2 | Python floor is already sufficient; update/test its independent environment. |
| Lintap `pidstat-collector-bootstrap.sh` | Python 3.12, unbounded `duckdb>=1.5.2` | Fresh installs can already select 2.0; pin a tested version and record engine provenance. |
| Lintap `pidstat-collector.py`, tests | Reused single connection, TSV-to-parquet COPY | Preserve single-process behavior, fields, rotation, retries and file counts. |
| Lintap `multipass-lintap.sh`, `fedora-setup-first-pass.sh` | CLI installer uses `latest` | Explicit CLI version needed; CLI and embedded engine are different components. |
| Analytics `streamlit/projects/SmokeTests/requirements.txt` | `duckdb>=1.1,<2` | Deliberate incompatibility with 2.0 today; update only after tests pass. |
| Analytics `streamlit/projects/common/{dqautil,wintapgraph}.py` | Relation `.fetchone()` in current UI paths | Concrete removed API migration needed. |
| Wintappy `wintappy/datautils/rawutil.py` | Relation `.count(...).fetchone()` in shared raw helpers | Same migration where reached from current analysis; inspect exception handling and connection reuse. |
| Analytics `validation/{process-creation,perf-collection}/pyproject.toml` | Python >=3.11; DuckDB >=1.0 | Pin/test active validation environments; no Python floor change needed. |
| Analytics `annotations/acme4/pyproject.toml` | Python 3.12; DuckDB >=0.10 plus DLT | Conditional current ingest/report path; prove DLT compatibility if included. |
| Analytics root `requirements.txt`, `2025-acme4-explore/` | DuckDB 0.10.1 pin / >=1.3.2 | Inventory only; excluded legacy environments unless a selected current command depends on them. |

<!-- GROUND_TRUTH: live paths listed in the table; ../wintap/wintap/Wintap.Common.props; ../wintap/wintap/locks/Lintap/packages.lock.json -->

Actual existing Wintappy `.venv` inspection: Python **3.12.12**, DuckDB package and
`SELECT version()` **1.5.5**, adapter **1.9.6**, dbt-core **1.12.2**. Inspection used
only an in-memory connection; no install, lock update or database write occurred.

The installed package root is `../Wintappy/wintappy/` as declared by setuptools.
Do not automatically patch the duplicate `src/wintappy/wintappy/` tree.
<!-- GROUND_TRUTH: ../Wintappy/pyproject.toml §tool.setuptools.packages.find -->

## External Sources / Availability

- [Official release](https://www.duckdb.org/2026/10/21/announcing-duckdb-200): 2.0.0 LTS, October 21.
- [Engine migration](https://duckdb.org/docs/2.0/operations_manual/migration): storage compatibility, SQL/parser changes, NULL typing, transaction-related risks and extensions.
- [Python migration](https://duckdb.org/docs/2.0/clients/python/migration): Python 3.11+, removed relation fetching APIs, open-result/thread restrictions and transaction failure behavior.
- [PyPI DuckDB metadata](https://pypi.org/pypi/duckdb/json): latest 2.0.0, requires Python >=3.11.0.
- [PyPI adapter metadata](https://pypi.org/pypi/dbt-duckdb/json): latest 1.11.0; broad `duckdb>=1.0.0` requirement does **not** certify 2.0 compatibility.
- [Adapter 1.11.0 release](https://github.com/duckdb/dbt-duckdb/releases/tag/1.11.0): predates 2.0; partition-column quoting behavior also changes.
- [Released adapter source](https://github.com/duckdb/dbt-duckdb/blob/1.11.0/dbt/adapters/duckdb/environments/local.py) still calls `.fetchone()` before registering an external-source dataframe; [development source](https://github.com/duckdb/dbt-duckdb/blob/master/dbt/adapters/duckdb/environments/local.py) instead drains with `.fetchall()` and explicitly mentions DuckDB 2.0's open-result restriction. This is a targeted compatibility risk, not proof that our entire DBT build fails.
- [Official .NET NuGet index](https://api.nuget.org/v3-flatcontainer/duckdb.net.data.full/index.json): latest 1.5.6.1; no official 2.0 package listed at inspection.
- [Unofficial fork](https://www.nuget.org/packages/Skuirrels.DuckDB.NET.Data.Full/2.0.0): separate package ID exists; [index](https://api.nuget.org/v3-flatcontainer/skuirrels.duckdb.net.data.full/index.json) confirms 2.0.0. Not selected or audited. Same assembly identities make mixing official and fork packages unsafe.
- [Release calendar](https://duckdb.org/release_calendar): 2.0.1 tentatively November 18; 1.5 support extended to March 2027. Recheck before implementation.

External pages/registry metadata were read live; no source files were copied into
`raw/`. Availability and development-branch contents can change after this date.

## Compatibility Findings

- Newly created 2.0 databases default to storage version 69, unreadable by 1.x.
  Existing older files retain their storage version when 2.0 writes them, per the
  engine migration guide. Test DB **and WAL** recovery separately; never infer safe
  downgrade from the database header alone. Explicit `storage_compatibility_version`
  or `ATTACH ... STORAGE_VERSION` can constrain new files; select a tested minimum
  current reader rather than blindly using the oldest legacy notebook version.
- Python relation `.fetchone()`/`.fetchmany()` are removed. Scalar reads can use
  `con.execute(...).fetchall()` (drained result) or relation `.fetchall()`; repeated
  relation reads rerun the query. Arrow/Polars migrations depend on whether the
  receiver is an execute result or relation; avoid global search-and-replace.
- A partial execute result or another thread using the same Python connection can
  block reuse with `ResourceInUseException`. One cursor per worker/session and
  explicit draining/closing need tests, not just import checks.
- Failed Python statements now abort explicit transactions. Test missing-table
  handling and adapter rollback/retry before proceeding after a caught exception.
- Current DBT scan found no actual old lambda expression; `process_path.sql` uses
  `'->'` as display text, which must not be rewritten. Still inspect generated SQL,
  regex operators, untyped NULL, divide/modulo zero and incremental MERGE behavior.
- The DBT profile loads extensions. Check version/architecture caches and restricted
  network installs; core/custom-build ICU changes are not a blanket SQL rewrite.

## Existing Quality Baseline

See [[wiki/work/host-process-identity-patch/verification]] and retained revision7
JSONs in that folder. Eight collector DBT builds succeeded; collector retention,
uniqueness and metadata passed, but four captures failed exact derived-birth gates.
`../Wintappy/wintap_dbt/macros/time.sql` uses floating FILETIME arithmetic; OS
labeling and default-round conservation/TCP failures also remain separate defects.
Capture their values under 1.5 and 2.0; preserve failed gates, do not claim a repair
merely because rounding or query execution changes.

Related: [[wiki/repo/wintappy-pipeline-repo]],
[[wiki/concept/collector-process-telemetry-and-collection-boundaries]],
[[wiki/concept/telemetry-identity-and-endpoint-orientation]].
