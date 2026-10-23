---
title: "References: Linux capability smoke triage"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs
  - ../Lintap/packaging/README.md
  - streamlit/projects/SmokeTests/README.md
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap; ../Lintap/packaging; streamlit/projects/SmokeTests
tags: [feature-work, references]
---

# References

## Live code

- `../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs` and
  `tracers/clone_core_tracer.bpf.c`, `tracers/clone_tracer.bpf.c`: classification tiers.
- `../wintap/wintap/core/infrastructure/ProcessResolver.cs`: late birth guard.
- `../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs`, `PluginManager.cs`,
  `WintapSvcCore.cs`: receipt lifecycle and publication.
- `../wintap/wintap/core/etl/model/Host.cs`, `extract/HostSerializer.cs`: HOST column.
- `../wintap/devtools/{smoke_manifest.py,smoke_parquet.py,telemetry_smoke_workload.py}`:
  portable evidence and stimuli. `validate_clone_*.py`,
  `validate_runtime_capabilities.py`: operational harnesses.
- `../Lintap/packaging/lintap-{deb,rpm}/{lintap.env,build-*.sh}`: defaults, payload
  checks and service package-version stamping.
- `streamlit/projects/SmokeTests/{main.py,queries.py,test_*.py,README.md}`: app/tests.

## Existing detailed records (retained, not duplicated)

- [[wiki/work/improve-lintap-data-quality/clone-validation-plan]]
- [[wiki/work/improve-lintap-data-quality/clone-validation-results]]
- [[wiki/work/improve-lintap-data-quality/runtime-capability-verification]]
- [[wiki/work/clone-default-true/verification]]
- [[wiki/work/clone-default-true/dev_handoff]] — external RHEL acceptance.
- [[wiki/work/smoke-test-dashboard/verification]]
- [[wiki/work/smoke-test-dashboard/durable-evidence-plan]] — accepted transport scope.

## Canonical documentation

- [[wiki/schema/runtime-capability-receipt]]
- [[wiki/diagnostic/linux-capability-data-quality-matrix]]
- [[wiki/event_type/process-events]]
- [[wiki/tool/named-telemetry-smoke-workload]]
- [[wiki/tool/smoke-test-results-dashboard]]
- [[wiki/work/linux-capability-smoke-triage/brief]]
