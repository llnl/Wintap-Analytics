---
title: "DuckDB 1.5 maintenance upgrade"
type: workflow
confidence: high
grounded_by:
  - ../wintap/Directory.Packages.props
  - ../Wintappy/pyproject.toml
  - ../Lintap/pyproject.toml
  - ../Lintap/pidstat-collector-bootstrap.sh
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../wintap; ../Wintappy; ../Lintap
tags: [duckdb, maintenance, dependencies, verification]
---

# DuckDB 1.5 maintenance upgrade

## Approved scope

User approved upgrading the three components just enumerated: Wintap's official
DuckDB.NET.Data.Full **1.5.6 → 1.5.6.1**, Wintappy's canonical Python/DBT engine
**1.5.5 → 1.5.6**, and Lintap's Python dependency/lock/bootstrap **1.5.2 → 1.5.6**.
This explicitly authorizes these sibling-repo dependency edits and local environment
updates. Preserve the adapter/core tuple, .NET SDK10.0.402 and unrelated dirty work.
No DuckDB2.0, historical DB migration, legacy notebook/SQL repair, installed-service
upgrade or new collector capture is included. The .NET wrapper still embeds engine1.5.6.

## Steps / Done checklist

- [x] Confirm baseline manifests, dirty work and official latest1.5 package versions.
- [x] Update central .NET version and refresh affected package locks without unrelated drift.
- [x] Pin Python1.5.6 in canonical manifests/bootstrap and regenerate uv locks selectively.
- [x] Upgrade local Python DuckDB packages. Wintappy's other dependencies retained;
  unintended Lintap venv recreation on Python3.12 explicitly recorded.
- [x] Verify actual engine versions and run focused native/Python/DBT regressions.
- [x] Record commands, failures, preserved inputs and remaining platform/install gates.

Dependency maintenance complete. No installed-service deployment or Windows live
execution occurred. Existing configuration failure reproduces under the old engine.

## Verification / rollback

Use native lintap-dev .NET10 build/test output outside shared sources; do not touch
the installed service. Use new temporary DBT outputs from retained raw inputs.
Record historical DB size/mtime before/after. Keep pre-upgrade manifest/lock receipts
under the approved Mac temporary root. Any rollback must preserve unrelated edits;
no git resets, broad cleanups or venv replacement. Results:
[[wiki/work/duckdb-1-5-maintenance/verification]].
