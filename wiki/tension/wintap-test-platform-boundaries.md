---
title: "Tension: Wintap Test Platform Boundaries"
type: tension
confidence: high
grounded_by:
  - wiki/decision/test-project-structure-and-first-test.md
  - ../Wintap/tests/Wintap.Tests/Wintap.Tests.csproj
  - ../Wintap/tests/Wintap.Tests/EventChannelHealthWireInTests.cs
policy: agent-editable
last_validated: 2026-11-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: developer
status: open
source_paths: ../Wintap/tests/Wintap.Tests; wiki/decision/test-project-structure-and-first-test.md
tags: [testing, platform-boundaries, xunit, cross-platform]
poles:
  - "Honor the accepted per-target test-project convention and make native platform coverage explicit."
  - "Keep useful shared/Linux-helper regressions in the existing Windows project during small cleanup rounds, avoiding unneeded projects and dependency changes."
resolution: null
---

# Tension: Wintap Test Platform Boundaries

The accepted bootstrap decision names Wintap/Lintap/Mactap test siblings;
`Wintap.Tests` and the Linux-focused `Lintap.Tests` now exist. The Windows assembly
references the Windows agent and links Linux
production helpers/sensors, so subject-platform coverage and actual runner-platform
coverage are not the same. Linux-only branches in an otherwise Windows-tested
assembly are not evidence of a native Linux collector run.
<!-- GROUND_TRUTH: wiki/decision/test-project-structure-and-first-test.md §Decision; ../Wintap/tests/Wintap.Tests/Wintap.Tests.csproj; ../Wintap/tests/Wintap.Tests/EventChannelHealthWireInTests.cs §CollectorProcessRefreshReachesNormalEgressOnLinuxOnly -->

The historical decision anticipated the Windows reference; this is a scope and
follow-up tension, not evidence that the bootstrap was incorrectly implemented.
The initial cleanup retained topology and labeled execution boundaries. Later Linux
test-project work supersedes the "only Wintap.Tests" inventory; macOS/Linux feature
testing is complete. Native Windows acceptance, broader shared-code ownership and
any Mactap project remain distinct. This does not silently resolve the open tension.
<!-- GROUND_TRUTH: ../wintap/tests/Lintap.Tests/README.md; ../wintap/tests/Wintap.Tests/README.md -->

Related analysis and proposed gate:
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis]] and
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]].
