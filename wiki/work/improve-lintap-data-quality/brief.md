---
title: "Feature Brief: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - wiki/work/refactor-data-log-paths/verification.md
  - ../wintap/wintap/core/etl/extract/Serializer.cs
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: stable
source_paths: wiki/work/improve-lintap-data-quality/brief.md
tags: [feature-work, lintap, data-quality, file-events, process-events, network-events]
---

# Feature Brief: Improve Lintap Data Quality

**CLOSED 2026-10-22 — accepted.** The source and fresh packaged-arm64 gates
passed. See [[wiki/work/improve-lintap-data-quality/verification]].

## Problem

The fresh arm64 Lintap smoke lost file events during a 6,000-file burst:
coverage fell to 4,918 paths and FileSerializer drops increased by 27,405.
The same dataset has file and network rows whose non-null PID hashes do not
join to `process`; affected rows report `Unknown` process names. Network
hostname casing may be inconsistent with other event families and potentially
with identity construction.

## Goals

- Eliminate newly observed FileSerializer loss while retaining at least 95%
  distinct-path coverage in the defined burst smoke.
- Measure and improve Linux process/user attribution, hostname consistency, and
  PID-hash orphan quality without claiming unattainable immediate perfection.
- Select queue/backpressure and optional schema changes from reproducible data.
- Make the evidence available through source-build iteration, DBT QA, and the
  packaged arm64 acceptance run.

## Non-Goals

- Windows sensor parity, RPM acceptance, or an unmeasured universal-zero orphan
  claim.
- Silent acceptance of loss by raising thresholds or suppressing diagnostics.

## Acceptance Criteria

1. A benchmark spike records configuration, workload rate, CPU/RSS, queue,
   serializer, coverage, and orphan measures and recommends a remediation.
2. The selected source-built remedy reaches at least 95% path coverage with
   zero new FileSerializer drops under the 6,000-file smoke.
3. Fresh packaged arm64 Multipass validation repeats criterion 2.
4. Attribution QA reports baseline, post-change counts/rates, and categorized
   top orphan evidence; the spike-derived threshold is explicitly met or an
   accepted limitation is recorded.
5. Network hostname convention is verified consistent across event families;
   any PidHash compatibility effect is tested.

## Affected Areas

`../wintap` Linux FileOps/process/network/ETL paths and tests; Lintap source
build/deployment and Debian packaging defaults as needed; Wintappy DBT QA and
Marimo dashboard; this repository's verification/wiki artifacts.

## Test Plan

Run focused unit tests and source builds, the benchmark matrix, process/file/
network smokes, DBT build plus orphan QA, then fresh arm64 packaged acceptance.

## Outcome

Adaptive ring notifications removed the observed over-60-second delivery tail;
a dedicated FileSerializer drain and coordinated producer-to-merge shutdown
removed the measured serializer loss. Kernel event-time conversion closed the
remaining controlled network identity skew. The final package retained all
5,000 workload paths and 40,000 operations with zero pipeline drops and zero
file/network attribution failures. Blank users on Stop-only rows remain a
separate serializer/model limitation; no universal zero-orphan claim is made.
