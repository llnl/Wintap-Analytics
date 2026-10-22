---
title: "Implementation Plan: Improve Lintap Data Quality"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - wiki/work/refactor-data-log-paths/verification.md
policy: agent-editable
last_validated: 2026-10-21
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/improve-lintap-data-quality/implementation_plan.md
tags: [feature-work, lintap, data-quality, implementation-plan]
---

# Implementation Plan: Improve Lintap Data Quality

## Steps

0. **ldq-00 — Fresh source-build VM.** Remove the prior disposable test VM and
   create a new arm64 Ubuntu Multipass host for this feature. Mount the shared
   LLNL checkout at `/home/ubuntu/git` and a fresh feature-specific directory
   beneath `../Wintappy/data` at `/home/ubuntu/data/quality`, so sensor output
   is directly available to macOS DBT/dashboard analysis. Verify the toolchain,
   mounts, BTF, and source-build prerequisites before collecting data.
1. **ldq-01 — Baseline instrumentation and benchmark.** Make source-build
   deployment reproducible; collect the spike matrix and preserve results.
2. **ldq-02 — File loss remediation.** Implement the measured bounded queue,
   flush, or backpressure remedy; add regression tests and zero-new-drop gate.
3. **ldq-03 — Attribution diagnosis/remediation.** Trace process lifecycle,
   hostname casing, PidHash construction, and Unknown process/user fallbacks;
   implement evidence-supported incremental improvements. Clone is enabled for
   normal Linux capture because forked children can perform file I/O before exec
   and otherwise have no Start lifecycle record. A FileOps-emitting isolated
   capture has validated Clone, the live cache-/`/proc` PID-hash fallback, and
   bounded retries for file rows; the final residual network orphan was traced
   to a one-100-ns-tick floating-point `/proc` conversion and corrected with
   integer arithmetic. Two long-capture DBT snapshots and the controlled
   acceptance6 workload validate those paths, but the frozen available
   acceptance6 output exposes a later system-workload lifecycle gap (stable
   child identities with no matching process lifecycle rows). Instrument and
   remediate that gap before
   treating the work as a general zero-orphan or Unknown-user fix.
4. **ldq-04 — Downstream QA contract.** Add/revise DBT checks, categories, and
   dashboard evidence for rates, top identities, and hostname consistency.
5. **ldq-05 — Acceptance.** Source-build regression suite, then a fresh arm64
   packaged Multipass deployment with process/file/network/DBT validation.

## Tests To Add Or Update

- Serializer counter/zero-new-drop and bounded-queue regressions.
- Hostname/PidHash consistency and process/user attribution tests.
- Repeatable benchmark harness/results schema.
- DBT orphan threshold/category and dashboard query tests.

## Done Checklist

- [x] ldq-00 fresh source-build VM and mounted data root
- [ ] ldq-01 benchmark and recommendation
- [ ] ldq-02 file-loss remediation (acceptance6 confirms 32,496 FileSerializer
  in-memory drops despite zero FileOps sender-queue drops)
- [ ] ldq-03 attribution remediation (controlled file/network and UID paths
  pass; the frozen acceptance6 system workload has lifecycle-row gaps, and
  process-user quality remains separate)
- [x] ldq-04 downstream QA contract (capture-isolated DBT acceptance gate remains for ldq-05)
- [ ] ldq-05 source and packaged arm64 acceptance
