---
title: "Decision: stable .NET 10 development SDK selection"
type: decision
status: accepted
decided_on: 2026-11-24
confidence: high
grounded_by:
  - ../wintap/developer_docs/instructions/sdk-01-stable-dotnet-10-selection.md
  - ../wintap/global.json
  - ../wintap/tests/Wintap.Tests/README.md
policy: human-review-required
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: none
audience: developer
source_paths: ../wintap/global.json; ../wintap/.github/workflows/release.yml
tags: [net10, sdk, windows, development]
---

# Stable .NET 10 development SDK selection

## Context
Exact SDK 10.0.402 blocks a Windows runner with stable 10.0.404.

## Decision
Approved `sdk-01`: minimum 10.0.100, `latestMinor` within major 10, no prereleases;
update policy tests/guidance, provision Windows CI with `10.0.x`, and record the selected SDK.

## Rationale
Avoid patch-pin churn without changing frameworks or dependencies.

## Consequences
Implementation is complete: minimum 10.0.100, `latestMinor`, no prereleases.
Record the actual selected SDK. macOS/Linux feature testing is complete; native
Windows verification remains separate. Lintap packaging retains an explicit
10.0.402 qualification check; resolver policy does not update that contract.
<!-- REVIEW NEEDED: implementation consequences updated from live sources; Windows and packaging qualification remain separate. -->

## Alternatives Considered
Exact pinning obstructs development; `latestPatch` is too narrow; ecosystem-wide packaging relaxation is deferred.

## Related
- [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/sdk-policy-notes]]
- [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]]
- [[wiki/work/wintap-telemetry-identity-and-data-quality/runtime_alignment_plan]]
