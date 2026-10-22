---
title: "Implementation Plan: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/extract/Serializer.cs
  - wiki/work/refactor-data-log-paths/verification.md
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: stable
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
   acceptance6 workload validate those paths. The later acceptance6 output also
   exposed serializer loss, requiring complete pipeline draining without
   assigning the lifecycle gap to an unmeasured tracer failure. Kernel-source
   network event time then removed the remaining rapid-exit skew. Controlled
   source and packaged workloads now have zero file/network orphans and
   `Unknown` names. Stop-only user blanks remain out of scope; do not generalize
   these workload results into a universal zero-orphan claim.
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
- [x] ldq-01 benchmark and recommendation (retain adaptive ring notifications
  with a dedicated FileSerializer drain; adaptive notification alone reduces
  latency but does not prevent serializer loss)
- [x] ldq-02 file-loss remediation (the remediated two-hour run retained all
  124,800 paths with zero serializer, writer, sender, or ring drops)
- [x] ldq-03 attribution remediation (source and packaged controlled workloads
  pass with zero file/network orphans or `Unknown` names and zero unknown Start
  users; Stop-only user blanks remain a documented model limitation)
- [x] ldq-04 downstream QA contract
- [x] ldq-05 source and fresh packaged arm64 acceptance
- [x] Post-closeout architecture/sequence diagram glossary and documentation
  link/citation audit
