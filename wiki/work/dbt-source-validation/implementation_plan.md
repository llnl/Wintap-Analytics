---
title: "DBT source-aware validation implementation plan"
type: workflow
confidence: high
grounded_by:
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/macros/validate_source.sql
policy: agent-editable
last_validated: 2026-11-11
repo_scope: Wintappy
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt/macros
tags: [dbt, duckdb, s3, validation]
---

# Approved scope and completion

User approved implementation in `../Wintap-PyUtil` after the planning-only review,
then confirmed the checks work and authorized topic commits on
`work/pidstat-and-dbt-validation`. Live-data qualification remains separate.

- [x] Validate effective local/S3 raw source independently of local output.
- [x] Reject unsupported/malformed URIs; validate day/hour dates/order.
- [x] Discover dates only from effective local input; require explicit S3 dates.
- [x] Add engine-native partition-scoped listing and one-Parquet-schema preflight.
- [x] Pass an explicitly selected `AWS_PROFILE` through to DuckDB's S3 credential chain.
- [x] Preserve optional-event behavior and original engine failure diagnostics.
- [x] Run preflight before build; keep configuration printing offline.
- [x] Keep dashboard prerequisites independent of raw-source reachability/dates.
- [x] Test local/split input, S3 protocol, hour narrowing, aliases and failures.
- [x] Update PyUtil README and canonical wiki guidance.
- [x] Revalidate combined source-validation/SELinux branch with the existing environment (286 tests pass).
- [ ] Qualify full combined-revision split-local and authenticated-S3 builds/tests.
- [ ] Obtain required approving review and merge expanded PR #43 normally.

Verification: [[wiki/work/dbt-source-validation/verification]].
Canonical reference: [[wiki/repo/wintappy-pipeline-repo]].
