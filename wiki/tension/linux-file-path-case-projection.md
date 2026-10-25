---
title: "Tension: Linux file path case discarded by normal ETL"
type: tension
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs
  - streamlit/projects/SmokeTests/queries.py
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: file
audience: mixed
status: open
source_paths: ../wintap/wintap/core/etl/extract; ../wintap/wintap/platform/linux/sensor/ebpf; streamlit/projects/SmokeTests
tags: [linux, file-events, case-sensitive-paths, projection, data-quality]
poles:
  - "Retain existing non-Windows lowercase projection and historical file-key conventions, explicitly preserved by current regression."
  - "Preserve Linux case-sensitive paths so distinct names and exact canary selectors remain distinguishable end to end."
resolution: null
---

# Current boundary

Linux FileOpsSensor preserves path case, but normal FileSerializer lowercases the
non-Windows path before persisted `File_Path` and file-key generation. The Windows
file emission regression explicitly retains existing other-platform behavior.
This is a prospective compatibility decision, not permission to mutate historical
raw datasets or silently merge case-only names.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §NormalizeFilePath; ../wintap/wintap/core/etl/extract/FileSerializer.cs §SelectPath, HandleSensorEvent; ../wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs §SerializerKeepsWindowsValueAndExistingOtherPlatformBehavior -->

The new exact per-path canary assertions expose this in normal ETL: all eight files
have every required activity, yet expected mixed-case paths match only after case
folding. Analytics reports that as unconfirmed case-sensitive identity, never an
automatic exact match. A change should explicitly cover prospective file-key and
downstream join compatibility, preserve Windows behavior, test case-only distinct
Linux files plus locale independence, and retain old dataset provenance.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §evaluate_case; wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification.md -->

Related: [[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]],
[[wiki/event_type/file-events]], [[wiki/tool/smoke-test-results-dashboard]].
