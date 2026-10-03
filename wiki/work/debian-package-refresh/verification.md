---
title: "Verification: Debian Package Refresh"
type: concept
confidence: low
grounded_by: []
policy: agent-editable
last_validated: 2026-10-03
repo_scope: Lintap
implementation_area: packaging
event_domain: none
audience: mixed
status: stub
source_paths: wiki/work/debian-package-refresh/verification.md
tags: [feature-work, lintap-packaging, debian, verification]
---

# Verification: Debian Package Refresh

Scaffold awaiting implementation. Acceptance criteria live in
[[wiki/work/debian-package-refresh/brief]]; record evidence per slice
(dpr-01..dpr-06) as it lands.

## Test Commands

<!-- Per-arch build commands, dpkg-deb inspection, install/upgrade/remove
sequences, exact as run. -->

## Manual Checks

<!-- Service state, tracer attach evidence from Lintap.log, parquet
readability, data preservation on remove. -->

## Results

<!-- Dated, per-arch. Include package filenames and SHA-256. -->

## Known Gaps

- arm64 host identity/access not yet supplied (dpr-06 blocked until then).
- NuGet availability on build hosts unconfirmed this cycle.

## Follow-Ups

<!-- Populated during implementation. -->
