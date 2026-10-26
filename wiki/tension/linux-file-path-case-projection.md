---
title: "Tension: Linux file path case discarded by normal ETL"
type: tension
confidence: high
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/core/etl/extract/FileSerializer.cs
  - ../wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs
  - ../wintap/tests/Wintap.Tests/TelemetryProjectionQualityTests.cs
  - ../Wintappy/wintap_dbt/models/silver/process_file.sql
  - streamlit/projects/SmokeTests/queries.py
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: file
audience: mixed
status: resolved
source_paths: ../wintap/wintap/core/etl/extract; ../wintap/wintap/platform/linux/sensor/ebpf; streamlit/projects/SmokeTests
tags: [linux, file-events, case-sensitive-paths, projection, data-quality]
poles:
  - "Retain existing non-Windows lowercase projection and historical file-key conventions, explicitly preserved by current regression."
  - "Preserve Linux case-sensitive paths so distinct names and exact canary selectors remain distinguishable end to end."
resolution: "User approved producer-case preservation for greenfield development on 2026-10-25; ../wintap/wintap/core/etl/extract/FileSerializer.cs §SelectPath implements it. Downstream DBT file_id case folding remains a separate limit."
---

# Original conflict

Before the approved change, Linux FileOpsSensor preserved case but normal ETL
lowercased the path before `File_Path` and sensor file-key generation. This was
explicitly preserved by the old regression, not an absent-file-activity defect.
<!-- GROUND_TRUTH: wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification.md §Verification so far (original pilot) -->

The new exact per-path canary assertions expose this in normal ETL: all eight files
have every required activity, yet expected mixed-case paths match only after case
folding. Analytics reports that as unconfirmed case-sensitive identity, never an
automatic exact match. A change should explicitly cover prospective file-key and
downstream join compatibility, preserve Windows behavior, test case-only distinct
Linux files plus locale independence, and retain old dataset provenance.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §evaluate_case; wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification.md -->

## Approved resolution — 2026-10-25

The user approved both projection changes, explicitly stating this is greenfield
development with no existing deployments or data to preserve. `SelectPath` now
preserves producer text on every platform; Windows producer normalization is unchanged.
Case-distinct Linux inputs therefore remain distinct in `File_Path` and sensor
file-key preimages, including under Turkish locale. No raw-data rewrite is performed.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/FileSerializer.cs §SelectPath; ../wintap/tests/Wintap.Tests/TelemetryProjectionQualityTests.cs §LinuxCaseDistinctPathsRetainDistinctFileKeysAcrossLocales; ../wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs §SerializerPreservesProducerPathOnEveryPlatform -->

This resolves the **sensor projection** decision, not every downstream identity
convention. Wintappy still derives `file_id` from hostname plus `lower(file_path)`
while retaining `file_path` as filename. Its derived IDs can collide for Linux
case-only names. Wintappy is unmodified; fixing that formula/joins requires separate
work and authorization. Analytics exact canary path checks do not use that DBT ID.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/silver/process_file.sql; streamlit/projects/SmokeTests/queries.py §evaluate_case -->

Related: [[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]],
[[wiki/event_type/file-events]], [[wiki/tool/smoke-test-results-dashboard]].
