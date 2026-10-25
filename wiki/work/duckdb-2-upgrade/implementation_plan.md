---
title: "DuckDB 2 upgrade: staged implementation plan"
type: workflow
confidence: medium
grounded_by:
  - ../Wintappy/pyproject.toml
  - ../Wintappy/wintap_dbt/profiles.yml
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../Lintap/pidstat-collector-bootstrap.sh
  - https://duckdb.org/docs/2.0/clients/python/migration
  - https://duckdb.org/docs/2.0/operations_manual/migration
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../wintap; ../Wintappy; ../Lintap; streamlit; validation
tags: [duckdb, dbt, upgrade, verification, rollback, planning]
---

# Implementation Plan: DuckDB 2 upgrade

## Scope / Recommended Approach

**On hold by user decision (2026-10-24):** wait for official .NET 2.0 support.
Latest1.5 maintenance completed separately:
[[wiki/work/duckdb-1-5-maintenance/verification]]. No2.0 implementation started.

Planning only. Read [[wiki/work/duckdb-2-upgrade/brief]] and
[[wiki/work/duckdb-2-upgrade/references]] before any implementation. Do not reuse
prior sibling-repo or disposable-host permissions as automatic upgrade approval.

**Recommendation:** qualify Python/DBT/current analysis first using immutable
parquet and fresh shadow databases; upgrade the embedded sensor only when a
supported official .NET 2.0 package is available. No forced lockstep is needed
across the parquet boundary. Keep new DB files explicitly 1.5-compatible during
transition if any selected reader remains 1.5. No schema/identity change proposed.
<!-- SYNTHESIS: inferred from live dependency inventory and DuckDB migration guides -->

## Steps

### 0. Freeze scope and baseline

- Confirm current-path allowlist, OS/architecture matrix, write permissions and
  whether 1.5-reader compatibility is required; choose DBT and sensor stage gates.
- Record package versions, `SELECT version()`, source revisions, extension versions,
  input manifests/hashes and selected workflow commands; freeze dirty-source state
  without resetting or committing unrelated work.
- Preserve historical DB and raw inputs read-only. Snapshot quiescent runtime
  DB/WAL together before native upgrade experiments; copy-only tests first.
- Record existing quality failures so candidate comparisons are not mislabeled.

### 1. Isolated dependency/API spike (first executable slice after approval)

- Create a separate Python 3.12 environment under the approved temporary root;
  do not replace `../Wintappy/.venv` or edit locks in a read-only spike.
- Compare baseline (DuckDB 1.5.5/adapter 1.9.6/core 1.12.2) against DuckDB 2.0.0
  with adapter 1.11.0, initially keeping core 1.12.2 to reduce confounding changes.
- Test debug/parse/full build/test at threads 1 and 4 on new output paths. Exercise
  external sources, result draining, explicit transaction failure/rollback and
  repeat builds; do not assume the adapter's broad version constraint is support.
- If released adapter fails, preserve results and wait for a fixed release or
  explicitly approve a pinned adapter patch. Development `master` is not a release.
- Inspect 2.0 wheels/native payloads for Linux arm64/x64, macOS arm64 and selected
  Windows targets; record platform minima rather than assuming 1.5 compatibility.
- Run minimal current DataQA/rawutil relation API probes, including empty results,
  query/DDL reuse and session/thread separation.

### 2. Wintappy DBT and active shared helpers

- Update canonical `pyproject.toml`/`uv.lock` to the proven tuple and Python >=3.11;
  keep current upper Python bound unless separately tested. Align tooling targets.
- Migrate reached relation scalar fetches, result lifecycle, exceptions and
  transaction recovery. Restrict changes to helpers used by current consumers.
- Add explicit storage compatibility to DBT connection settings if selected;
  verify the adapter applies it to fresh files and all worker connections.
- Validate extension installation/load and missing optional parquet inputs;
  run local fixtures, gold quality/uniqueness tests and complete DBT models.
- Build fixed historical/revision7 raw inputs into **new** baseline/candidate outputs.
  Compare schemas/types, sorted keyed rows, counts/aggregates, identities/parents,
  exact timestamps, endpoints and collector metadata. SQL hashes alone are insufficient.
- Exercise S3 credentials/extension behavior if it is an accepted current path;
  otherwise explicitly leave remote acceptance pending, not implicitly green.

### 3. Current Analytics consumers

- Update SmokeTests' `<2` constraint and selected validation environment locks;
  point DataQA/common helpers at the tested Wintappy package/environment.
- Migrate `dqautil.py`, `wintapgraph.py` and reached raw helpers; test both synthetic
  rows and fresh DBT outputs, including no-data cases and UI reruns.
- Run SmokeTests, process-creation/performance validation and independent identity/
  collector DBT verifiers against both environments with comparable inputs.
- Include ACME4 annotation/DLT ingest/report smoke only if confirmed current.
  No general notebook, dated-project, arbitrary-SQL or root-requirements cleanup.

### 4. Lintap pidstat / supporting packaging

- Update its independent manifest/lock and pin `PIDSTAT_DUCKDB_SPEC`; replace
  unversioned `latest` CLI provisioning with a selected tested release.
- Run pidstat tests and TSV/parquet rotation/restart/permission/error fixtures;
  prove no fork storm, missing samples, overwrite surprises or schema drift.
- Check Debian/RPM bootstrap and selected distro wheel/glibc compatibility. Keep
  current self-contained sensor packaging and SDK 10.0.402 unless separately changed.

### 5. Embedded sensor (gated by supported .NET package)

- Recheck official NuGet availability. A 1.5.6.1 wrapper upgrade is **not** a 2.0
  engine upgrade. Do not substitute a native library or unofficial package silently.
- Upgrade central package reference and applicable target/test lockfiles together;
  inspect native libraries, runtime identifiers and transitive dependencies.
- Test resolver and Windows backup-manager reader lifetimes, prepared parameters,
  multi-statement commands, disposal, maintenance and transaction behavior against
  actual native 2.0. Verify timestamp round trips without changing pid-v2 inputs.
- Test fresh, old-format, clean-restart and crash/WAL stores in isolated copies;
  confirm chosen storage compatibility and restore procedure on the older package.
- Build native Debian arm64 plus selected Windows/RPM targets. After separate
  approval, fresh package captures should cover churn/PID reuse, start/stop/Refresh,
  collector visibility/self-I/O suppression, file conservation, two-process and
  same-PID bidirectional non-loopback TCP, restart and bounded shutdown.
- Record attribution/admission counters and payload evidence separately. Previous
  failures stay failures; do not infer release acceptance from graceful exits.

## Migration / Rollback

- Raw parquet is the cross-version interchange; there is no historical migration.
- Preserve baseline venv/locks, CLI, packages, runtime DB/WAL and input receipts.
  Never point an older reader at an unverified newly created 2.0-format store.
- Switch DBT output paths rather than mutate the supplied analysis database. Roll
  back consumers to the retained baseline output; rebuild from raw parquet if needed.
- Stop writers before native rollback; restore a coherent pre-upgrade runtime
  snapshot or verified older-compatible state. Do not discard process/agent state,
  copy only one side of DB/WAL, or promise a downgrade without replay tests.
- Compatibility flags, if required, are scoped/documented bridges, not global
  permission to keep arbitrary old SQL working. Old lambda syntax bridge disappears
  in 2.1; change only actual reached lambda expressions, never display arrows.

## Effort / Dependencies

Provisional solo implementation estimate: **3–6 developer-days**, excluding
waiting for a supported .NET/DBT release and broad distro/Windows field acceptance.
Rough slices: isolated spike 0.5–1 day; DBT/helpers/current QA 1–2 days; pidstat/
packaging 0.5–1 day; embedded sensor/rollback/installed proof 1–2 days. This is a
planning estimate, not a delivery commitment; API/adapter/native failures can expand it.
An unofficial provider evaluation would be a separately estimated decision.

## Done Checklist

- [x] Release verified; current manifests, runtime and concrete API risks inventoried.
- [x] Source-linked scope, test stages, rollback and exclusions recorded.
- [ ] User confirms allowlist, compatibility policy and implementation authorization.
- [ ] Isolated 2.0 engine/adapter/API spike passes; released package tuple selected.
- [ ] Wintappy and current Analytics dependencies/API migrations verified.
- [ ] Lintap pidstat/bootstrap/CLI environment verified.
- [ ] Official native sensor package available, integrated and tested on selected targets.
- [ ] DB/WAL downgrade and fresh installed end-to-end proof complete.
- [ ] Known failures separated from upgrade regressions; acceptance explicitly recorded.
- [ ] Canonical docs/glossary and verification updated; no historical repair included.
