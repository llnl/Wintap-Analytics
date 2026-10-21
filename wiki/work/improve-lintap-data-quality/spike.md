---
title: "Feature Spike: Improve Lintap Data Quality"
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
source_paths: wiki/work/improve-lintap-data-quality/spike.md
tags: [feature-work, spike, lintap, data-quality, file-events]
---

# Feature Spike: Improve Lintap Data Quality

## Question

Which bounded queue/flush/attribution changes remove observed file loss and
improve identity joins on the arm64 Linux sensor?

## Experiment

On a source-built Lintap deployment, run repeatable 6,000-file (and stepped
smaller/larger) bursts across candidate serializer queue/flush configurations.
For each run record workload parameters, elapsed time, CPU/RSS, queue depth and
peak, accepted/dropped totals, parquet latency, distinct paths, activity mix,
and DBT orphan rate/composition. Capture raw hostname values, PidHash inputs or
available identity evidence, and `Unknown` process/user rates for process,
file, and network output.

## Recommendation Criteria

Recommend only a bounded-memory configuration/design that reaches the file
criterion with zero new drops and gives an evidence-based orphan threshold.
State whether producer ordering/reconciliation, hostname normalization, or an
additive provenance field is required.

## Initial Results — 2026-10-21

The fresh source-build VM produced diagnostic results: an initial clean
6,000-file run captured 5,693 paths (94.9%) with zero FileSerializer drops,
while the controlled rebuild/restart run captured all 6,000 paths (30,000
activity rows) and also had zero drops. In the failed run, the FileOps sender
queue and BPF ring-failure counters were both zero-drop; the missing paths were
the contiguous final indices 5,693–5,999.

**Recommendation:** retain the current bounded serializer and FileOps queue
limits. Run a warm-up/attach-state matrix (immediate, 45-second, and 60-second
readiness delays; repeated bursts) before selecting a queue or backpressure
change. A FileSerializer-limit change is unsupported by current evidence.

Hostname normalization is independently justified: FileSerializer lowercased
only file rows, whereas process and network serializers used shared host
identity. FileSerializer now uses `HostSerializer.Instance.HostId.Hostname`.

Attribution has a separate, evidence-supported configuration experiment: the
source-build capture ran with `Clone=false`. Forked children can perform file
operations before exec, yielding Unknown file identities when no Clone Start
record exists. Enable Clone for a clean before/after capture, then measure the
orphan composition separately from the queue/flush warm-up matrix.
