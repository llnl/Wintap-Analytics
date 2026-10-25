---
title: "DuckDB1.5 maintenance: verification summary"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/Directory.Packages.props
  - ../Wintappy/pyproject.toml
  - ../Lintap/uv.lock
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap; ../Wintappy; ../Lintap; streamlit
tags: [duckdb, maintenance, verification]
---

# Qualified maintenance tuple

Official .NET wrapper1.5.6.1/native engine1.5.6 and Python1.5.6;DBT adapter1.9.6/
core1.12.2 retained. Selective lock comparison found no unrelated package-version
drift in the intended updates. DuckDB2.0 remains held for official .NET support.

Native250focused tests,Linux/Windows-helper builds,Python SQL/pidstat/UI suites and
a fresh full83-node DBT build pass. Collector birth/metadata/uniqueness checks pass;
historical DB and installed collector/service/state were not changed. Build proof
is not final installed-package qualification.

## Caveats retained

- Existing `test_default_args` DATASET failure reproduced under the older engine;
  it was not fixed or accepted as an upgrade regression.
- MacLintap `.venv` was unintentionally recreated fromPython3.14to3.12 by a command
  missing an isolated environment override. This was disclosed;the exact old
  environment cannot be reconstructed and must not be claimed preserved.
- Initial platform/tool/environment failures remain archived;corrected native
  supported-environment runs provide the acceptance evidence.

Original commands,engine receipts,lock comparisons and failures:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]],archive member
`wiki/work/duckdb-1-5-maintenance/verification.md`.
Scope:[[wiki/work/duckdb-1-5-maintenance/implementation_plan]].
