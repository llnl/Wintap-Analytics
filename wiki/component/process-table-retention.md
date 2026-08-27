---
title: "Process Table Retention & Reconciliation"
type: component
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/tests/Wintap.Tests/ProcessResolverTests.cs
policy: agent-editable
last_validated: 2026-08-27
repo_scope: wintap
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: reviewed
source_paths: wiki/component/process-table-retention.md
tags: [wintap, lintap, process, retention, duckdb, cross-repo]
---

# Process Table Retention & Reconciliation

Promoted from [[wiki/work/fix-unbounded-process-table-growth/brief]]
(closed 2026-08-27). Bounds event_store process-table growth on long
runs while preserving PID-reuse-safe resolution.

## Contracts (field-verified through 2026-08-27)

- **Resolver-owned lazy retention sweep**: exited process rows are
  retained briefly then swept; the table plateaus (~47-50k rows on
  spk16 vs the pre-feature 8M rows/10 days).
- **Liveness-based stale-open reconciliation**: open rows whose PID no
  longer exists are closed by sweep (`reconciled_closed` telemetry);
  `live_pids_missing_open_row == 0` is the health invariant.
- **QA telemetry is itself bounded**: `process_retention_telemetry` is
  aggregated/retained, not per-sweep-appended (the unbounded variant
  measurably cost host CPU).
- **CloneSensor thread filter**: `clone(2)` with `CLONE_THREAD` does not
  emit a process-start row — thread IDs are not process identities;
  fork/vfork and process-like clones still emit. Dropped open
  `python3.12`-style thread rows ~35x on the field host.
- **DuckDB read caveat**: the live DB cannot be opened read-only while
  Lintap holds the lock; query a copy (the diagnostics collector does).

## Verification

Milestone tests P1-P3 in [[wiki/work/optimize-fileops-poller/test_plan]]
(pytest harness, boundedness check via the diagnostics bundle, VM
long-run summarizer). Final long-run acceptance runs as
[[wiki/work/extended-deployment-monitoring/brief]].
