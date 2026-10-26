---
title: "DuckDB 2 upgrade: feature brief"
type: concept
confidence: medium
grounded_by:
  - ../wintap/Directory.Packages.props
  - ../Wintappy/pyproject.toml
  - ../Wintappy/uv.lock
  - ../Lintap/pyproject.toml
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/requirements.txt
  - https://duckdb.org/docs/2.0/operations_manual/migration
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap; ../Wintappy; ../Lintap; streamlit; validation
tags: [duckdb, upgrade, planning, dbt, sensor, analytics]
---

# Feature Brief: DuckDB 2 upgrade

## Problem

DuckDB 2.0.0 LTS was released October 21, 2026. The ecosystem has separately
versioned .NET, Python, DBT and CLI engines. Upgrading one dependency does not
upgrade all of them; new database-file defaults and Python API changes require
an explicit compatibility plan.
<!-- GROUND_TRUTH: https://www.duckdb.org/2026/10/21/announcing-duckdb-200; https://duckdb.org/docs/2.0/operations_manual/migration -->

## Goals

**2026-10-24 user decision:** hold the DuckDB 2.0 upgrade until the official
.NET constraint clears. The subsequently approved latest1.5 maintenance update
is complete separately: [[wiki/work/duckdb-1-5-maintenance/verification]]. Official
wrapper1.5.6.1 still embeds native1.5.6; Python is pinned1.5.6. No2.0 implementation.

- Plan upgrades across the Wintap/Lintap sensor, pidstat collector, canonical
  Wintappy bronze/silver/gold DBT pipeline, and current analysis/validation paths.
- Preserve identity, lifecycle, endpoint semantics, raw parquet and analysis
  outputs; distinguish existing defects from upgrade regressions.
- Establish reproducible package/engine versions, compatible database ownership,
  isolated baseline/candidate proof and a tested rollback.

## Non-Goals

- Repair old notebooks, arbitrary analyst SQL, dated experiment projects or
  historical databases; modernize every manifest simply because it mentions DuckDB.
- Rewrite legacy ETL except a shared helper actually used by an in-scope consumer.
- Fix existing timestamp precision, Linux-as-Windows labels, admission/retry/drain
  or conservation/TCP defects as part of the version bump.
- Adopt Quack/server mode, DuckLake, VARIANT, new telemetry schemas or a new
  third-party .NET provider without a separate decision.
- Install packages, change services or edit source during this planning task.

## User-Facing Behavior

The same current collector, DBT build and QA workflows should work in a pinned
2.0 environment. Historical inputs remain untouched. A staged upgrade may leave
the embedded sensor engine on 1.5 temporarily while Python/DBT uses 2.0 through
the existing parquet boundary; that is partial delivery, not an all-project upgrade.

## Acceptance Criteria

1. Record actual engine versions, not just wrapper versions, for each supported
   package/OS/architecture; lock the Python/DBT tuple and CLI versions.
2. Selected current workflows execute and preserve normalized values, schemas,
   identity/lifetime relationships, metadata and counts relative to fixed inputs.
3. Fresh and existing runtime stores, DB/WAL restart recovery and older-reader
   compatibility behave as explicitly selected; rollback is demonstrated on copies.
4. Native sensor and pidstat regression tests plus a fresh installed capture pass
   their scoped gates; no improvement claim follows from zero drop counters alone.
5. DBT debug/parse/build/test, repeat runs and parallel workers succeed on fresh
   outputs, including missing optional sources and extension provisioning.
6. Existing failed gates remain visible. A build succeeding is not proof of
   data-quality acceptance, and boundary tolerance is not silently relaxed.

## Affected Areas

Wintap owns the embedded resolver/recovery database and sensor packaging payload;
Lintap owns supporting packaging/bootstrap and the pidstat Python collector;
Wintappy owns DBT and shared Python helpers; Analytics owns current UI/validation
consumers and this plan. See [[wiki/work/duckdb-2-upgrade/references]] for inventory.

Initial current-path allowlist: Streamlit SmokeTests, DataQA and their common
helpers; `validation/process-creation`, `validation/perf-collection`; current
host-identity independent analyzers/DBT verifier. ACME4 annotation ingest/report
utilities are conditional on current use; old exploratory notebooks are excluded.

## Open Questions

- Wait for an official DuckDB.NET 2.0 release (recommended), or separately approve
  evaluation of the available unofficial fork?
- Which released DBT adapter is verified with 2.0? Latest available is not proof.
- Which deployed Windows/Linux targets need release acceptance, versus compile-only
  coverage? No new VM/service tests are authorized by this plan.
- Must new output databases remain readable by 1.5 during transition? Recommend
  explicit 1.5-compatible storage until all current readers are upgraded.
- Confirm the allowlist, especially whether ACME4 annotations are a current path.

## Test Plan / Done When

Follow [[wiki/work/duckdb-2-upgrade/implementation_plan]]. Planning is started;
implementation requires explicit approval and sibling-repo write authorization.
