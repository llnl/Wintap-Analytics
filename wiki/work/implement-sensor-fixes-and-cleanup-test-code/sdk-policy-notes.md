---
title: "Approved direction: stable .NET 10 SDK selection"
type: concept
confidence: medium
grounded_by:
  - ../wintap/global.json
  - ../Lintap/packaging/dotnet-common.sh
  - ../Lintap/tests/test_dotnet_packaging.py
  - ../wintap/devtools/test_runtime_alignment.py
  - ../wintap/.github/workflows/release.yml
  - ../wintap/developer_docs/instructions/sdk-01-stable-dotnet-10-selection.md
policy: agent-editable
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: none
audience: developer
status: draft
source_paths: ../wintap/global.json; ../wintap/devtools/test_runtime_alignment.py
tags: [feature-work, sdk, net10, windows]
---

# Stable .NET 10 SDK selection — working notes

Architect approved `../wintap/developer_docs/instructions/sdk-01-stable-dotnet-10-selection.md`
on 2026-11-24; policy and tradeoffs are in [[wiki/decision/stable-dotnet-10-development-sdk]].
Implementation is complete in Wintap: minimum 10.0.100, major-10 `latestMinor`
roll-forward, and no prereleases. Current guidance records the selected stable SDK.
macOS/Linux feature testing is complete. Lintap packaging now accepts the same stable
.NET 10 policy and records the selected version; provisioning may still install
10.0.402 as a valid SDK rather than equating it with the minimum. Native Windows
and native package qualification remain separate. Historical 10.0.402 results
are dated evidence, not current Wintap development prerequisites.

## Related

- [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]]
- [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]]
- [[wiki/work/wintap-telemetry-identity-and-data-quality/runtime_alignment_plan]]
