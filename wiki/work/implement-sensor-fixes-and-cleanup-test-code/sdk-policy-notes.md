---
title: "Approved direction: stable .NET 10 SDK selection"
type: concept
confidence: medium
grounded_by:
  - ../wintap/global.json
  - ../wintap/devtools/test_runtime_alignment.py
  - ../wintap/.github/workflows/release.yml
  - ../wintap/developer_docs/instructions/sdk-01-stable-dotnet-10-selection.md
policy: agent-editable
last_validated: 2026-11-24
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: none
audience: developer
status: draft
source_paths: ../wintap/global.json; ../wintap/devtools/test_runtime_alignment.py
tags: [feature-work, sdk, net10, windows, implementation-pending]
---

# Stable .NET 10 SDK selection — working notes

Architect approved `../wintap/developer_docs/instructions/sdk-01-stable-dotnet-10-selection.md`
on 2026-11-24; policy and tradeoffs are in [[wiki/decision/stable-dotnet-10-development-sdk]].
Implementation and Windows verification are pending; afterward update current SDK gates
and runtime-alignment guidance, retaining historical results.
Linux packaging compatibility requires separate review because it shares `global.json`.

## Related

- [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]]
- [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]]
- [[wiki/work/wintap-telemetry-identity-and-data-quality/runtime_alignment_plan]]
