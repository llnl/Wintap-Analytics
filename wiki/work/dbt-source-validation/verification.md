---
title: "DBT source-aware validation verification"
type: diagnostic
confidence: high
grounded_by:
  - ../Wintap-PyUtil/tests/test_dbt_source_validation.py
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql
policy: agent-editable
last_validated: 2026-11-09
repo_scope: Wintappy
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../Wintap-PyUtil/tests/test_dbt_source_validation.py
tags: [dbt, duckdb, s3, validation, regression-tests]
---

# Verification

## Operator follow-up

The human reports the source-aware checks work with their configuration and
authorized topic commits on `work/pidstat-and-dbt-validation`. This is operator
confirmation, not an agent-inspected real-host DBT dataset qualification. The
recorded test results below are unchanged; private run-env files and data remain local.

Implementation saved in `../Wintap-PyUtil` commit `8fe85d0` on that branch.

Implementation: [[wiki/work/dbt-source-validation/implementation_plan]].
Commands ran in `../Wintap-PyUtil`, using existing uv environment, DuckDB1.5.6,
dbt1.12.2 and dbt-duckdb1.9.6. No live/operator S3 credentials or datasets used.

## Named-profile live source preflight (2026-11-09)

Ran `make dbt-check-source` from the current `../Wintap-PyUtil` checkout after
sourcing the operator's local run-env file. Kept `AWS_PROFILE=lintap-alpha` set,
used its `region` and `endpoint_url` from `aws configure`, and matched
`DUCKDB_USE_SSL` to the endpoint scheme. The DBT source check **passed**: S3 listing
found a requested-window `raw_host` Parquet object and DuckDB read its schema.
This validates the named-profile flow against the configured endpoint; it is not
a full `dbt-build`, full-object scan, or model test. No credential values were
printed or recorded.

## Final focused regressions

```sh
uv run --dev pytest tests/test_dbt_source_validation.py tests/test_network_activity_sql.py tests/test_filetime_precision_sql.py tests/test_process_gold_quality_sql.py -q
```

**249 passed**, including 40 source-validation tests. Actual DBT operations
exercise local valid/empty/corrupt/out-of-hour inputs, historical event aliases,
network protoPK nesting and pidstat-only input (other optional events absent).
Actual DuckDB httpfs exercises a loopback S3 protocol fixture: path-style Garage
endpoint, credential-chain test environment, successful listing/schema reads,
day/hour LIST-prefix narrowing, empty windows, denied listing, denied reads and
TLS mismatch. A named-profile case confirms the request uses the selected profile
credentials from a temporary AWS config/credentials fixture. SQL errors remain
errors, not silent empty input. Offline Make
checks cover local date discovery, explicit S3 dates, no-placeholder S3 printing,
source-before-build ordering and raw-independent dashboard prerequisites.

## Broader suite and retained failure

`uv run --dev pytest tests -q`: **272 passed, 1 failed** before the final TLS
case was added. Failure: unchanged legacy
`tests/test_config.py::TestEnvironmentConfig::test_default_args`, where existing
Dynaconf settings include `DATASET` despite the test expecting no dataset defaults.
The same unchanged test fails alone:
`uv run --dev pytest tests/test_config.py::TestEnvironmentConfig::test_default_args -q`.
No legacy settings/code/test edits were made to hide or repair this unrelated failure.

Initial implementation run: 24 passed/9 failed; corrected Make's parsing of a shell
`case` inside `$(shell ...)` and test-operation setup of the local DB parent.
Next run: 33 passed. Inspection then replaced an event wildcard with concrete
bronze event/alias prefixes to avoid broad S3 listing. Final focused result above
includes additional coverage and the output-only readable-database check.

Formatting: `uv run --dev black scripts/check_dbt_config.py tests/test_dbt_source_validation.py`
and `uv run --dev isort scripts/check_dbt_config.py tests/test_dbt_source_validation.py`.
`git diff --check` passes in PyUtil.

## Limits

- Loopback S3 profile coverage uses fixture credentials. The separate live source
  preflight used the operator's configured profile and endpoint, but is not full
  AWS/Garage deployment or profile/role qualification. Native RHEL qualification
  was not performed.
- Preflight reads one schema, not all Parquet files/data pages or DBT model semantics.
- Probe supports current bronze inputs/aliases; its explicit list needs maintenance
  when new events are added. Large windows can still require many LIST requests.
- No canonical real-host DBT build or Go-pidstat acceptance is implied.
- User run-env files/datasets and unrelated checkout work retained locally.
