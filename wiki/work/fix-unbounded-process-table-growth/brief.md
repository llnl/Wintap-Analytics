---
title: "Feature Brief: Fix Unbounded Process Table Growth"
type: concept
confidence: medium
grounded_by:
  - raw/Issues/Long_Running_Cleanup.md
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs
policy: agent-editable
last_validated: 2026-08-12
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/fix-unbounded-process-table-growth/brief.md
tags: [feature-work, process-events, event-store, duckdb, process-resolution, long-running]
---

# Feature Brief: Fix Unbounded Process Table Growth

> **STATUS: CLOSED — accepted 2026-08-27** (current state accepted by
> human; long-running acceptance shifted to the parallel
> [[wiki/work/extended-deployment-monitoring/brief]] task ahead of the
> branch PR). Durable knowledge promoted to
> [[wiki/component/process-table-retention]]. The FileOps subtask closed
> the same day: [[wiki/work/optimize-fileops-poller/brief]].

## Problem

`ProcessResolver` persists live process state in a DuckDB `process` table at
`$WINTAP_DATA_ROOT/event_store/main.duckdb`. Rows are inserted on process
Start/Refresh and updated in place on Stop; nothing ever deletes rows during a
run. The only delete path is `ClearDB()`, which is called solely by the
Windows `ProcessSensor.Initialize()` during process-tree reconstruction at
sensor startup. On Linux (Lintap) there is no clear/prune call at all, so the
table also persists and grows across runs.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §RegisterProcess, §ClearDB -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs §Initialize -->

The motivating issue (`raw/Issues/Long_Running_Cleanup.md`) documents the
consequence on long runs: roughly 8M rows accumulated over 10 days, with only
about 1/3 of rows having exit codes, and CPU load growing significantly as the
DB grows. The issue states the intent directly: the event store is meant to be
a store for "currentish" processes, and it needs a cleanup routine.

Growth is not just a disk problem — it degrades the hot path. Every
non-Process event flowing through `EventChannel` runs
`ResolveProcessAtTime()` (a SQL query over the `process` table filtered by
`process_id` and time range) to attribute the event to an owning process, and
falls back to `GetPidHash()` (a second query) when that misses. As the table
grows, every event pays more, which is consistent with the observed
CPU-load-grows-with-DB-size correlation (hypothesis to confirm; see Test
Plan).
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/EventChannel.cs §Listen (ResolveProcessAtTime / GetPidHash fallback) -->

The integrity constraint that makes this non-trivial: the same table is the
source of truth for PID-reuse-safe attribution. Cleanup must not remove rows
that resolution still needs:

- Open rows (no `exit_time`) for genuinely running processes must never be
  removed — long-lived daemons can be older than any retention window.
- Recently exited rows are still needed for late-arriving events (file,
  network, exit) that reference a PID shortly after the process died.
- About 2/3 of rows in the 10-day example have no exit code, so many "open"
  rows are actually dead processes whose Stop event was missed. A naive
  "delete exited rows older than X" policy would leave those forever; a
  policy that treats all open rows as live never converges.
- On Windows, `SendProcessTreeToEsper()` replays all rows newer than boot as
  Refresh events at startup, and `GetAllProcesses()` reads the entire table —
  whole-table scans that assume the table is boot-scoped, not history.

Related but distinct sub-problem from the same issue: why is Lintap missing
so many process terminations in the first place? The
[[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]]
thread reduced the residual open-row rate to ~3.3% of workload PIDs in a
one-hour noisy run (concentrated in very short-lived `bash` processes), but
at 8M-rows-over-10-days scale even a small percentage accumulates.

## Goals

- Bound the `process` table size on long-running (multi-day/multi-week)
  Wintap and Lintap instances, consistent with its stated intent as a store
  for "currentish" processes.
- Preserve process resolution integrity: event attribution (PidHash
  correctness, PID-reuse safety, parent linkage) must not regress for live
  processes, recently exited processes, or late-arriving events.
- Define and implement an explicit retention policy for exited rows (grace
  window after `exit_time` before eligibility for removal).
- Reconcile stale open rows — rows with no `exit_time` whose process is no
  longer alive — via a liveness cross-check (query `/proc` on Linux / a
  process snapshot on Windows and close rows for dead PIDs, synthesizing an
  `exit_time`), so missed terminations cannot pin rows forever.
  Decided 2026-08-12 (human): the cross-check is to be implemented as an
  inherent QA feature, not merely a cleanup pass — each sweep both closes
  stale rows and emits measurable evidence of sensor termination-tracking
  quality (e.g., counts of rows closed by reconciliation rather than by a
  Stop event, per process name). This makes the periodic scan cost
  justified twice over and supersedes the pure age-based alternative.
- Confirm (or refute) the CPU-load-grows-with-DB-size correlation with
  before/after measurements, using the pidstat collector data path built for
  exactly this purpose ([[wiki/work/improve-pidstat-collector/brief]]).
- Keep the durable-store role compatible with the recorded architecture
  direction: memory-first attribution with the durable store as
  backing/history
  ([[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]]).

## Non-Goals

- Eliminating the remaining ~3.3% missed-termination leakage at the sensor
  level (tracked in the lintap-process-creation-validation thread). This
  feature must tolerate missed terminations, not fix their root cause.
- Moving attribution fully to an in-memory model (the memory-first
  architecture direction). Cleanup should not foreclose that direction, but
  implementing it is a separate feature.
- Historical process analytics. Long-term history belongs to the
  raw_sensor Parquet / DBT pipeline, not the live event store.
- The raw_sensor empty-directory cleanup item from the same issue document
  (separate, unrelated mechanism).
- Windows Security-log process-tree reconstruction semantics.

## User-Facing Behavior

No new user-visible features. Operators of long-running instances should
observe: a `process` table whose row count plateaus instead of growing
without bound, stable (non-growing) per-event CPU cost over multi-day runs,
and unchanged telemetry semantics — process, file, and network events remain
attributed to the correct PidHash at the same or better rate as today.
Retention parameters should be configurable with sensible defaults.

## Acceptance Criteria

- On a multi-day Lintap run with a sustained noisy workload, `process` table
  row count reaches a plateau determined by live-process count plus the
  retention window, instead of growing linearly.
- No open row for a genuinely live process is ever deleted (verified by
  liveness cross-check at end of run: every running PID with activity still
  resolves to a correct, stable PidHash).
- Late-arriving events within the retention grace window still resolve to
  the exited process's PidHash (no increase in "Unknown" / fallback-hash
  attributions relative to a baseline run; measurable from EventChannel logs
  and validation-harness output).
- Stale open rows (missed terminations) are closed by the liveness
  cross-check, so the ~2/3-without-exit-code population from the motivating
  issue cannot recur.
- The cross-check emits QA telemetry distinguishing rows closed by a real
  Stop event from rows closed by reconciliation, so sensor
  termination-tracking quality is directly measurable from a running
  instance (replacing the harness-only `stop_only_like`-style metrics).
- Lookups that miss because the referenced row was pruned are counted as a
  retention-miss metric (decided 2026-08-12) rather than falling back
  silently, so the retention window can be tuned from evidence.
- The existing process validation harness passes at parity or better:
  process smoke test, and the one-hour noisy-state workload's
  manifest-PID-observed and open-row metrics
  ([[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]]).
- Windows startup behavior (ClearDB + Security-log reconstruction +
  process-tree replay) is unchanged or explicitly accounted for.
- CPU correlation measured: pidstat data from a multi-day before/after pair
  shows per-event cost no longer trending upward with runtime.

## Affected Areas

- `../wintap/wintap/core/infrastructure/ProcessResolver.cs` — cleanup
  routine, retention policy, stale-open reconciliation (primary change
  site; sibling repo, code changes need explicit authorization).
- `../wintap/wintap/core/infrastructure/IProcessResolver.cs` — possible
  interface additions (e.g., prune entry point).
- `../wintap/wintap/core/infrastructure/EventChannel.cs` — resolution
  fallback behavior when a pruned row is referenced; possible scheduling
  hook for periodic cleanup.
- `../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs` — consumers
  of `GetAllProcesses()`/whole-table replay assumptions.
- Configuration surface (retention window, cleanup interval, liveness
  reconciliation toggle) in the sensor's config mechanism.
- `Wintap-Analytics/validation/process-creation` harness — new long-run
  retention validation scenario and metrics.

## References

See [[wiki/work/fix-unbounded-process-table-growth/references]].

## Open Questions

- Retention window for exited rows: what grace period after `exit_time`
  safely covers late-arriving events on both platforms? (Esper windows and
  serializer flush cadences bound this; needs measurement.)
- ~~Stale-open policy: liveness-check-based vs. pure age-based vs. both?~~
  Decided 2026-08-12: liveness-check-based, implemented as an inherent QA
  feature (see Goals). Remaining design detail: sweep cadence, and the
  exact QA metrics/telemetry surface the reconciliation emits (log lines,
  counters, or rows in a diagnostics output).
- ~~Where does cleanup run: inside `ProcessResolver` on a timer, on the
  existing merge/upload cycle, or driven by `EventChannel`?~~
  Decided 2026-08-12 (human): left to the implementing developer's
  discretion. Not architecturally constrained; the chosen scheduling
  mechanism and its rationale should be recorded in
  [[wiki/work/fix-unbounded-process-table-growth/design]] (or directly in
  verification notes if decided during implementation).
- ~~Should pruned-but-referenced lookups fall back to the Linux `/proc`
  start-time hash (already implemented in `GetPidHash`) silently, or be
  counted/logged as a retention-miss metric?~~
  Decided 2026-08-12 (human): track as a retention-miss metric. The
  fallback still fires (events keep an identifier), but every lookup that
  misses because the row was pruned is counted, so retention-window tuning
  has direct evidence. Remaining design detail: the metric surface, which
  should share whatever telemetry mechanism the reconciliation QA feature
  uses.
- DuckDB specifics: does `DELETE` reclaim space / keep query plans fast, or
  is periodic `CHECKPOINT`/`VACUUM`-equivalent or table rewrite needed to
  realize the CPU win?
- Does the Windows startup replay (`SendProcessTreeToEsper`) constrain how
  aggressively exited rows can be pruned before a service restart?
- Is a row-count or DB-size hard cap wanted as a backstop in addition to
  time-based retention?

## Test Plan

- Unit-level: retention sweep respects grace window; never deletes open rows
  that pass liveness; closes stale open rows for dead PIDs; prune is safe
  under concurrent RegisterProcess/Resolve calls (single `_dbLock` today).
- Harness: extend the process-creation validation harness with a retention
  scenario — sustained noisy workload for N hours with a short configured
  retention window; assert table plateau, attribution parity for live and
  recently-exited processes, and zero live-row deletions.
- Regression: re-run the existing process/file/network smoke tests and the
  one-hour noisy-state workload; compare open-row and resolution metrics to
  the 2026-08-06 baseline.
- Performance: multi-day (or accelerated high-rate) run with pidstat
  collection before/after; compare Lintap CPU trend against table size to
  confirm the correlation hypothesis from the motivating issue.
- Windows: verify startup ClearDB/reconstruction path is unaffected and a
  mid-run prune does not break `SendProcessTreeToEsper` replay semantics on
  restart.

## Done When

- Open questions above are resolved and recorded in
  [[wiki/work/fix-unbounded-process-table-growth/design]].
- Acceptance criteria pass on a real long run on Lintap and a Windows
  regression check.
- Durable facts (retention policy, configuration, event-store role) are
  promoted into canonical wiki pages (likely the process-events event_type
  page and/or a new event-store component page), and `wiki/log.md` is
  updated.
