---
title: "Implementation plan: Linux capability smoke triage"
type: concept
confidence: high
grounded_by:
  - wiki/work/clone-default-true/verification.md
  - wiki/work/smoke-test-dashboard/verification.md
  - ../wintap/tests/Wintap.Tests/RuntimeCapabilitiesTests.cs
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: wiki/work/linux-capability-smoke-triage
tags: [feature-work, implementation-plan, retrospective]
---

# Implementation plan (retrospective)

- [x] Correct Clone CO-RE/fallback classification and provisional resolver metadata.
- [x] Record/freeze/publish startup HOST evidence with idempotent initialization.
- [x] Enable packaged Clone with opt-out and CO-RE payload validation.
- [x] Stamp package version in generated service description.
- [x] Add named workloads and portable evidence across eight smoke families.
- [x] Export time-partitioned immutable parquet run snapshots beside telemetry.
- [x] Add automatic discovery, scoped queries and severity overview/navigation.
- [x] Record Ubuntu package/default/restart/opt-out and mounted cross-host evidence.
- [x] Re-run focused .NET, producer/workload and dashboard checks before commit.
- [x] Reconstruct confirmed feature artifacts and promote canonical usage/semantics.
- [x] Commit selected Wintap (`859a47b`) and Lintap (`cfc3f35`) changes; Analytics
  app/wiki/artifacts are included in this feature's Analytics commit, no pushes.
- [x] Supply concise feature-only PR appendices and record commit references in
  [[wiki/work/linux-capability-smoke-triage/pr_summaries]].
- [x] Address Analytics PR review: preserve red overlap violations, reject invalid
  selector entries/domains, and add query plus rendering regressions (23 tests pass).

## Compatibility and rollback

No legacy staging/dataset preservation requirement. Keep the new HOST property;
no HOST-specific source merge/schema branch. Package upgrades preserve local
configuration. Explicit Clone opt-out and JSON-only smoke export remain available.
Do not use rollback to erase unrelated working files or generated datasets.

## Follow-ups, not current completion gates

RHEL/x86_64 acceptance, Clone overhead/loss review, server-side network gaps,
namespaces/PID reuse and downstream receipt temporal joins. See
[[wiki/work/linux-capability-smoke-triage/verification]].
