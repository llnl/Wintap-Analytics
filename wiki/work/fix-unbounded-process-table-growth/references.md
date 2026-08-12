---
title: "Feature References: Fix Unbounded Process Table Growth"
type: concept
confidence: medium
grounded_by:
  - raw/Issues/Long_Running_Cleanup.md
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
policy: agent-editable
last_validated: 2026-08-12
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/fix-unbounded-process-table-growth/references.md
tags: [feature-work, process-events, event-store, duckdb]
---

# Feature References: Fix Unbounded Process Table Growth

## Live Repo Sources

Primary change site (all in `../wintap`, read-only until code-development
mode is explicitly authorized for that repo):

- `../wintap/wintap/core/infrastructure/ProcessResolver.cs`
  - `RegisterProcess` — insert-on-Start / update-on-Stop; no delete path.
  - `ResolveProcessAtTime`, `GetPidHash` — the per-event hot-path queries
    whose cost scales with table size; `GetPidHash` already has a Linux
    `/proc` start-time fallback for unregistered PIDs. Decided 2026-08-12:
    when a lookup misses because the row was pruned, the fallback must be
    counted as a retention-miss metric, not fire silently.
  - `AddPendingExit` / `ApplyPendingExit` / `PrunePendingExits` — in-memory
    pending-exit cache (15-minute prune) reconciling Stop-before-Start
    ordering; the only existing pruning precedent in the class.
  - `ClearDB` — full table delete; only caller is Windows
    `ProcessSensor.Initialize()`.
  - `InitializeDatabase` — schema: `process` table keyed by `pid_hash`, with
    `create_time`, `exit_time`, `exit_code` columns that a retention sweep
    would filter on. No index beyond the primary key today.
  - `GetAllProcesses` — whole-table scan used by Windows startup replay.
- `../wintap/wintap/core/infrastructure/IProcessResolver.cs` — interface to
  extend if a prune entry point is added.
- `../wintap/wintap/core/infrastructure/EventChannel.cs`
  - `Listen`/message loop — calls `ResolveProcessAtTime` for every
    non-Process event, `GetPidHash` fallback, `RegisterProcess` for Process
    events; `GetProcessHistory()` / `ClearProcessDB()` static wrappers.
  - `WINTAP_SKIP_PROCESS_RESOLVE` / `WINTAP_SKIP_PROCESS_REGISTER` isolation
    switches useful for measuring resolver cost in isolation.
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs`
  - `Initialize` — ClearDB + Security-log process-tree reconstruction.
  - `SendProcessTreeToEsper` — replays all rows newer than boot as Refresh
    events; assumes table ≈ current boot's processes.
- `../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs` — Stop-event
  producer on Linux (`EventChannel.GetProcessHistory(pid, exitUtc)` usage).
- `../wintap/wintap/core/etl/model/ProcessObjectModel.cs` — ETL-side process
  model, for checking downstream assumptions.

## External Sources

- `raw/Issues/Long_Running_Cleanup.md` — motivating issue: ~8M rows over 10
  days, ~1/3 with exit codes, "store for currentish processes" intent,
  CPU-load-grows-with-DB-size hypothesis, missing-termination question.
- DuckDB documentation on `DELETE`, `CHECKPOINT`, and space reclamation —
  needed to answer whether deletes alone realize the performance win
  (row-group compaction/vacuum behavior is version-dependent; verify against
  the DuckDB.NET version pinned in `../wintap`).

## Related Wiki Pages

- [[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]] —
  process-state fixes as of `../wintap` commit `5dccdc1`, one-hour noisy
  validation baseline (10372 rows, 312 open, ~3.3% residual open rate),
  memory-first architecture direction note.
- [[wiki/work/lintap-process-creation-validation/validation-harness-design]] —
  harness to extend with a retention scenario.
- [[wiki/work/improve-pidstat-collector/brief]] — sibling feature from the
  same issue document; provides the CPU/memory measurement data path for the
  correlation test.
- [[wiki/event_type/process-events]] — canonical process event semantics;
  promotion target for the final retention policy.
- [[wiki/component/windows-sensor-service-internals]] — startup ordering
  context for the Windows ClearDB/reconstruction path.

## Libraries And APIs

- DuckDB.NET (`DuckDB.NET.Data`) — embedded store; single-connection,
  single-`_dbLock` usage pattern in ProcessResolver.
- Linux `/proc/<pid>/stat` + `/proc/uptime` — liveness and start-time
  source already used by `TryGetLinuxProcStartFileTimeUtc`; the decided
  mechanism for stale-open reconciliation on Linux (liveness cross-check as
  inherent QA feature, decided 2026-08-12).
- Windows process enumeration (e.g., `Process.GetProcesses()` or ETW
  rundown) — liveness source on Windows for the same cross-check.

## Decisions To Date (2026-08-12)

Recorded in [[wiki/work/fix-unbounded-process-table-growth/brief]] Open
Questions; summarized here for the dev agent:

- Stale-open reconciliation is liveness-check-based and doubles as an
  inherent QA feature (Stop-closed vs. reconciliation-closed telemetry).
- Cleanup scheduling (timer vs. merge cycle vs. EventChannel-driven) is the
  implementing developer's discretion; record the choice and rationale.
- Pruned-row lookup misses are tracked as a retention-miss metric.

Still open: retention grace window value, DuckDB space-reclamation
mechanics, Windows startup-replay constraints, optional hard-cap backstop.

## Notes

- The pending-exit cache prune (15 minutes, in-memory) and the DuckDB table
  are separate lifetimes; only the table is unbounded.
- The event_store DB file persists across runs on Linux (no ClearDB call),
  so cross-run growth compounds the within-run growth. Whether cross-run
  persistence is intentional on Linux is an open design question — Windows
  explicitly clears and rebuilds from the Security log at startup.
- All `process`-table queries filter on `process_id` (an unindexed column;
  primary key is `pid_hash`), so full scans are plausible at query time —
  worth confirming with DuckDB `EXPLAIN` as part of the CPU correlation
  work.
