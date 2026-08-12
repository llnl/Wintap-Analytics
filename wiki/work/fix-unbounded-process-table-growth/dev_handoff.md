---
title: "Dev Handoff: Fix Unbounded Process Table Growth"
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
source_paths: wiki/work/fix-unbounded-process-table-growth/dev_handoff.md
tags: [feature-work, dev-handoff, process-events, event-store, duckdb]
---

# Dev Handoff: Fix Unbounded Process Table Growth

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

    Switch to code-development mode for fix-unbounded-process-table-growth.

    Use these wiki files as the handoff context:

    - wiki/work/fix-unbounded-process-table-growth/brief.md
    - wiki/work/fix-unbounded-process-table-growth/references.md
    - wiki/work/fix-unbounded-process-table-growth/dev_handoff.md

    Goal: bound the event_store `process` table on long-running instances
    via a retention sweep plus a liveness-based stale-open reconciliation
    that doubles as a QA feature, without regressing PID-reuse-safe process
    resolution.

    You are authorized to modify code in ../wintap for this feature.
    ../Lintap and ../Wintappy remain read-only. Wintap-Analytics may be
    modified only under validation/ (harness additions) and wiki/ (feature
    artifacts, log).

    Before editing code, read AGENTS.md and confirm that code-development
    mode is active for this task.

## Handoff Summary

`ProcessResolver` (`../wintap/wintap/core/infrastructure/ProcessResolver.cs`)
persists process state in a DuckDB `process` table that nothing deletes
during a run (only Windows startup calls `ClearDB()`; Linux never does).
A documented 10-day run accumulated ~8M rows, ~2/3 without exit codes, with
CPU load growing as the DB grew. Every non-Process event pays a query
against this table (`ResolveProcessAtTime`, with a `GetPidHash` fallback)
in `EventChannel`, so growth degrades the per-event hot path.

The store's intent is "currentish" processes. The feature adds:

1. **Retention sweep** — delete exited rows once they are older than a
   configurable grace window past `exit_time`.
2. **Liveness reconciliation (QA feature, decided 2026-08-12)** — for open
   rows (no `exit_time`), check liveness (`/proc/<pid>` on Linux, process
   snapshot on Windows). Close rows for dead PIDs with a synthesized
   `exit_time`, and emit QA telemetry distinguishing rows closed by real
   Stop events from rows closed by reconciliation (per process name), so
   sensor termination-tracking quality is measurable from a running
   instance. This is a deliverable, not an implementation detail.
3. **Retention-miss metric (decided 2026-08-12)** — when a lookup misses
   because the row was pruned, count it as a retention miss (the existing
   `/proc` start-time fallback in `GetPidHash` still fires so events keep
   identifiers). Do not let these misses pass silently.

Hard integrity constraints (from the brief — read it in full):

- Never delete an open row whose process is alive; long-lived daemons
  predate any window.
- Keep recently exited rows through the grace window for late-arriving
  events.
- All sweep work must be safe under the existing single `_dbLock`
  concurrency model alongside `RegisterProcess`/`ResolveProcessAtTime`.
- Windows startup (`ClearDB` + Security-log reconstruction +
  `SendProcessTreeToEsper` whole-table replay) must keep working; check how
  pruning interacts with the replay's newer-than-boot filter.

Decisions delegated to you (record choice + rationale as you go):

- Where the sweep runs (ProcessResolver timer, merge/upload cycle, or
  EventChannel-driven) — explicitly your discretion per 2026-08-12
  decision.
- Sweep cadence and the telemetry surface (log lines, counters, or a
  diagnostics table). The reconciliation QA output and the retention-miss
  metric should share one mechanism.
- Default retention window — pick a defensible default (consider Esper
  window/serializer flush cadences noted in the brief), make it
  configurable, and state how you validated it.
- Whether DuckDB `DELETE` alone realizes the space/CPU win or a periodic
  `CHECKPOINT`/rewrite is needed — measure, don't assume. Also consider an
  index on `process_id` while you are in there (all hot-path queries filter
  on it; the primary key is `pid_hash`), but treat that as an opportunistic
  measured improvement, not required scope.

## Primary Sources For The Dev Agent

- `../wintap/wintap/core/infrastructure/ProcessResolver.cs` — primary
  change site. Note the existing in-memory pending-exit cache with its
  15-minute prune (`AddPendingExit`/`ApplyPendingExit`/`PrunePendingExits`)
  as the class's only pruning precedent, and
  `TryGetLinuxProcStartFileTimeUtc` as the Linux liveness/start-time
  mechanism to reuse.
- `../wintap/wintap/core/infrastructure/IProcessResolver.cs` — extend if
  you add a prune entry point.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` — hot-path caller;
  retention-miss counting hooks in the `ResolveProcessAtTime`/`GetPidHash`
  fallback path; `WINTAP_SKIP_PROCESS_RESOLVE`/`WINTAP_SKIP_PROCESS_REGISTER`
  env switches for isolating resolver cost.
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` —
  `Initialize` (ClearDB call) and `SendProcessTreeToEsper` (whole-table
  replay) constraints.
- `../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs` — Linux Stop
  producer, for understanding what a "real" Stop close looks like.
- `raw/Issues/Long_Running_Cleanup.md` — motivating issue.
- `wiki/work/lintap-process-creation-validation/current-state-2026-08-06.md`
  — validation baseline to not regress (one-hour noisy run: 10372 rows,
  312 open, ~3.3% residual open rate) and harness entry points.
- `Wintap-Analytics/validation/process-creation/` — the uv-managed harness
  (`run_lintap_noisy_state_test.sh`, `summarize_lintap_process_table.py`)
  to extend with a retention scenario.

## Recommended First Implementation Slice

1. Add the retention sweep + liveness reconciliation to `ProcessResolver`
   behind configuration (retention window, sweep interval, enable flag),
   with your chosen scheduling mechanism.
2. Emit the QA telemetry (reconciliation-closed vs. Stop-closed, per
   process name) and the retention-miss counter through one shared surface.
3. Unit-style tests for the sweep invariants: grace window respected, live
   open rows never deleted, dead-PID open rows closed with synthesized
   exit_time, safe under concurrent register/resolve.
4. A short Lintap validation run (noisy workload, deliberately short
   retention window) demonstrating: table plateau, attribution parity for
   live and recently-exited processes, QA telemetry populated, retention
   misses counted.

Stretch (measure first, only if the win is real): `process_id` index and/or
DuckDB space-reclamation step; multi-hour plateau run.

## Non-Goals For This Slice

- Fixing sensor-level missed terminations (root cause stays in the
  lintap-process-creation-validation thread; your reconciliation telemetry
  will feed it evidence).
- Windows implementation of the liveness snapshot may be stubbed with a
  clear TODO if the dev environment is Linux-only — but do not break the
  Windows build, and document what remains.
- The memory-first attribution architecture, historical analytics, and the
  raw_sensor empty-directory cleanup item.
- Multi-day performance runs and the CPU-correlation study (they need the
  pidstat collector deployment; a later slice).

## Testing Expectations

- Build both `Lintap.csproj` and `Wintap.csproj` (`make -C wintap/wintap
  build_dotnet` covers Linux; Windows build must at least compile).
- New sweep tests pass; existing process/file/network smoke tests pass at
  parity (`Wintap-Analytics/validation/process-creation`).
- One noisy-workload run with a short retention window, summarized with
  `summarize_lintap_process_table.py`, showing plateau + parity vs. the
  2026-08-06 baseline metrics.
- No live-process row deletions across the run (end-of-run liveness
  cross-check).

## Closeout Instructions

- Create wiki/work/fix-unbounded-process-table-growth/verification.md with
  commands run and results.
- Record delegated decisions (scheduling, cadence, telemetry surface,
  default window, DuckDB reclamation findings) in
  wiki/work/fix-unbounded-process-table-growth/design.md — create it from
  the template in wiki/concept/feature-work-template.md; keep it brief and
  grounded in what you actually built and measured.
- Append a concise entry to wiki/log.md.
- Leave promotion of durable facts into canonical pages (process-events
  event_type, possible event-store component page) to the closeout stage;
  flag candidates in your log entry.
