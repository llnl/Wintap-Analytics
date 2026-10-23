---
title: "PR appendices: Linux capability smoke triage"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/RuntimeCapabilities.cs
  - ../Lintap/packaging/lintap-deb/lintap.env
  - streamlit/projects/SmokeTests/main.py
  - wiki/work/linux-capability-smoke-triage/verification.md
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap; ../Lintap/packaging; streamlit/projects/SmokeTests
tags: [feature-work, pr-summary, commits]
---

# Feature-only PR appendices

Append these to the existing PRs; do not replace summaries of earlier branch work.
All repositories retain `feature/improve-lintap-data-quality`; no pushes performed.

## Wintap — commit `859a47b`

### Linux capability evidence and smoke validation

- Prefer CO-RE Clone process/thread classification, add clone3-aware fallback and
  preserve established resolver identities when provisional birth metadata arrives late.
- Persist frozen per-startup HOST capability receipts with effective settings,
  selected object/tier/hash, hook outcomes and explicit failures; share safe native attachment.
- Add named process/file/loopback-network workloads and repeatable validators with
  portable JSON plus optional durable parquet run evidence.
- Validation: 127 focused .NET tests and six Linux manifest/workload tests pass;
  recorded Ubuntu arm64 packaged baseline/churn, restart and opt-out acceptance passes.
- Limits: fallback without flag hooks remains unsafe; RHEL acceptance and isolated
  Clone overhead review remain pending. No legacy HOST merge compatibility required.

## Lintap — commit `cfc3f35`

### Capability-aware Clone package defaults

- Enable Clone in Debian/RPM templates while retaining explicit opt-out and local
  administrator configuration.
- Require CO-RE Clone payload and stamp package versions into service descriptions.
- Update deployment guidance for capability receipts and fallback limitations.
- Validation: both builders pass shell syntax checks; recorded Debian arm64 package
  acceptance passes. Fresh RHEL/x86_64 RPM validation remains external/pending.

## Wintap-Analytics — this feature's Analytics commit

### Cross-host smoke results and triage

- Add a standalone read-only DuckDB/Streamlit dashboard with automatic durable
  parquet-manifest discovery, host/run isolation and tailored smoke-test queries.
- Add red/yellow/green/gray overview, host/history/attention filters and section/run
  navigation; missing or stimulus-only evidence never constitutes capture PASS.
- Document capability semantics, editable workloads and retrospective feature scope.
- Validation: 19 app/query tests pass; mounted Linux→Mac capture discovers two runs
  across 23 telemetry plus six evidence parquet files without separate JSON transfer.
- Limits: server TCP Accept/UDP Receive gaps remain visible; no uploader redesign,
  DBT integration or direct S3 browsing.

## Wintappy

No new feature commit or PR appendix: no tracked changes were required.

Scope: [[wiki/work/linux-capability-smoke-triage/brief]].
Evidence: [[wiki/work/linux-capability-smoke-triage/verification]].
