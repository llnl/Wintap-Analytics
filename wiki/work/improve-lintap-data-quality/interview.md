---
title: "Feature Interview: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - wiki/work/refactor-data-log-paths/verification.md
  - ../wintap/devtools/file_capture_smoke_test.py
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: stable
source_paths: wiki/work/improve-lintap-data-quality/interview.md
tags: [feature-work, lintap, data-quality, file-events, process-events, network-events]
---

# Feature Interview: Improve Lintap Data Quality

## Initial Idea

Improve Lintap data quality following the arm64 smoke findings.

## Context Established Before Questioning

Fresh package smoke recorded FileSerializer loss under a 6,000-file burst and
PID-hash orphans in file/network DBT relations. The smoke now recognizes the
current serializer loss counter, and the Wintappy dashboard exposes top orphan
identities. [[wiki/work/refactor-data-log-paths/verification]]

## Decisions

- Address file-loss and attribution quality in phases.
- Preserve the existing file coverage target (at least 95%) and require zero
  new serializer drops.
- Permit coordinated Wintap/Lintap/Wintappy changes, but focus on Linux/Lintap.
- Iterate by building/deploying from source; final acceptance uses a fresh
  packaged arm64 Multipass VM.
- Require a benchmark-and-recommendation spike before choosing queue limits,
  backpressure behavior, or whether additive attribution provenance is needed.
- Add hostname consistency and `Unknown` process/user investigation. Improving
  attribution without reaching 100% is acceptable.

## Deferred / Open Questions

- Measured orphan threshold/categories after the benchmark baseline.
- Root cause and compatibility impact of network hostname case.
- Whether an additive provenance schema is necessary.

## Playback Summary

Confirmed 2026-10-21: Linux/Lintap-only, evidence-first feature covering
serializer loss, PID-hash attribution, hostname consistency, and incremental
Unknown identity remediation; Windows parity and RPM acceptance are out of
scope.

## Sealed — human estimates

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available?**
**A:** 5 days for the meatstick alone, 2 days for SI (AI) help. Part of the time
is that we'll be running longer tests.

**Q: With the AI workflow, on what date do you predict this feature will be
available?**
**A:** See previous answer.
