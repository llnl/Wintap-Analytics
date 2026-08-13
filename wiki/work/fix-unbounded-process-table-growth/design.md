---
title: "Feature Design: Fix Unbounded Process Table Growth"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../Wintap-Analytics/validation/process-creation/scripts/summarize_lintap_process_table.py
  - ../Wintap-Analytics/validation/process-creation/scripts/run_lintap_noisy_state_test.sh
policy: agent-editable
last_validated: 2026-08-13
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: developer
status: draft
source_paths: wiki/work/fix-unbounded-process-table-growth/design.md
tags: [feature-work, process-events, event-store, duckdb, retention]
---

# Feature Design: Fix Unbounded Process Table Growth

## Summary

This slice adds periodic process-table maintenance inside `ProcessResolver` itself. The resolver now performs a bounded sweep on the existing `_dbLock` path, closes stale-open rows by liveness check, deletes exited rows after a configurable retention window, and records QA/retention metrics in a small DuckDB telemetry table.

## Proposed Approach

- Run maintenance lazily from `ProcessResolver` methods instead of adding a new timer or `EventChannel` scheduler.
- Gate sweep execution by `WINTAP_PROCESS_SWEEP_INTERVAL_SEC` so the hot path only pays the maintenance cost once per interval.
- Keep exited rows for `WINTAP_PROCESS_EXIT_RETENTION_SEC` after `exit_time`, then delete them.
- Reconcile stale-open rows older than `WINTAP_PROCESS_RECONCILE_MIN_AGE_SEC` by checking current liveness:
  - Linux: `/proc/<pid>/stat` start time.
  - Windows: `Process.GetProcessById(pid).StartTime`.
- Close a stale-open row only when the current live PID hash does not match the stored row, preserving PID-reuse-safe semantics.
- Preserve a short in-memory cache of recently pruned rows keyed by PID so `GetPidHash()` can count retention misses and still return the pruned row's hash for late events inside that cache horizon.
- Persist sweep telemetry in `process_retention_telemetry` with metric names `stop_closed`, `reconciled_closed`, `retention_deleted`, and `retention_miss`, and include `pid_hash` on each telemetry row so cleanup/reconciliation evidence can be joined back to process identity later.
- On Linux, derive reconciliation liveness from the same `ProcReader.ReadProcessInfo()` path used by `ProcessRundownSensor`, not from an independent `/proc` parser alone. If a live PID's current `/proc` start time matches the row `create_time` within a small tolerance, treat it as the same process instance even if the stored `pid_hash` differs, and repair the row's `pid_hash` in place.

## Data Model Or Schema Changes

- Existing `process` table unchanged.
- New DuckDB table:

```sql
CREATE TABLE IF NOT EXISTS process_retention_telemetry (
    observed_at TIMESTAMP,
    metric_name VARCHAR,
    process_name VARCHAR,
    pid_hash VARCHAR,
    metric_value BIGINT
)
```

## Interfaces And User Experience

- New env-configurable knobs, all read via `ConfigManager`:
  - `WINTAP_PROCESS_RETENTION_ENABLED` default `true`
  - `WINTAP_PROCESS_RECONCILE_STALE_OPEN_ENABLED` default `true`
  - `WINTAP_PROCESS_SWEEP_INTERVAL_SEC` default `300`
  - `WINTAP_PROCESS_EXIT_RETENTION_SEC` default `3600`
  - `WINTAP_PROCESS_RECONCILE_MIN_AGE_SEC` default `60`
- Validation harness script now accepts the sweep/retention env overrides and uses the shared summarizer so telemetry is included in summaries.

## Edge Cases

- Live long-running processes are never pruned because only rows with non-null `exit_time` are delete-eligible.
- PID reuse stays safe because stale-open reconciliation only closes a row when the live PID hash differs from the stored row.
- Linux rundown rows for long-lived processes can carry historical hash drift for some non-boot processes; reconciliation now uses live start-time equivalence as a second identity check and repairs the row instead of closing it when the process instance is clearly the same.
- Stop-before-Start handling stays in the existing pending-exit cache; stop-closed telemetry is emitted when the stop ultimately lands on a row.
- Late events for recently pruned rows can still recover the pruned `PidHash` from the in-memory pruned-row cache, and those recoveries are counted as `retention_miss`.

## Error Handling

- Maintenance runs under `_dbLock`; failures log a warning and back off to a one-minute retry instead of breaking event processing.
- The new Windows live-start-time path is best-effort and returns `null` on failure.

## Risks

- Maintenance still runs on a request path, so an overly aggressive sweep interval can add latency spikes.
- The pruned-row cache is memory-only, so retention misses across restart boundaries are still best-effort only.
- This slice does not yet measure DuckDB reclaim behavior beyond row-count reduction; `VACUUM`/`CHECKPOINT` work remains open.

## Alternatives Considered

- Background timer in `ProcessResolver`: rejected for this slice in favor of fewer moving parts and reuse of the existing lock/concurrency model.
- `EventChannel`-driven scheduling: rejected because the resolver owns the table and telemetry.
- Pure age-based stale-open deletion: rejected by prior human decision; liveness reconciliation is required.

## Open Questions

- Whether DuckDB `DELETE` alone is enough for the long-run CPU/storage win, or whether periodic compaction is required.
- Whether a `process_id` index is worth adding after measurement.
- Whether the recently-pruned cache horizon should be independently configurable from exited-row retention.
