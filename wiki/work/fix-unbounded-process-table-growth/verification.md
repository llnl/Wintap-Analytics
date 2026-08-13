---
title: "Verification: Fix Unbounded Process Table Growth"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../Wintap-Analytics/validation/process-creation/scripts/summarize_lintap_process_table.py
policy: agent-editable
last_validated: 2026-08-13
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: developer
status: draft
source_paths: wiki/work/fix-unbounded-process-table-growth/verification.md
tags: [feature-work, verification, process-events, retention]
---

# Verification: Fix Unbounded Process Table Growth

## Test Commands

Run in `multipass` VM `lintap-dev` because the Mac host lacks the Linux/.NET runtime used by this feature:

```bash
multipass exec lintap-dev -- bash -lc "cd /home/ubuntu/git/wintap && dotnet build wintap/Lintap.csproj"
multipass exec lintap-dev -- bash -lc "cd /home/ubuntu/git/Wintap-Analytics/validation/process-creation && UV_PROJECT_ENVIRONMENT=/tmp/wpv-venv uv run --extra dev pytest"
multipass exec lintap-dev -- bash -lc "cd /home/ubuntu/git/wintap && dotnet build wintap/Wintap.csproj -p:EnableWindowsTargeting=true"
multipass exec lintap-dev -- bash -lc "cd /home/ubuntu/git/Wintap-Analytics/validation/process-creation && RUN_ID=retention-smoke-1786640189 DURATION_SECONDS=180 INTERVAL_SECONDS=5 SHORT_PER_INTERVAL=12 LONG_PER_MINUTE=2 LONG_LIVED_SECONDS=45 PROCESS_SWEEP_INTERVAL_SEC=15 PROCESS_EXIT_RETENTION_SEC=45 PROCESS_RECONCILE_MIN_AGE_SEC=10 bash scripts/run_lintap_noisy_state_test.sh"
multipass exec lintap-dev -- bash -lc "cd /home/ubuntu/git/Wintap-Analytics/validation/process-creation && python3 scripts/summarize_lintap_process_table.py --db /tmp/lintap-retention-smoke-1786640189/event_store/main.duckdb --manifest /tmp/validation-runs/retention-smoke-1786640189/workload/manifest.json"
```

Recommended long-run command after the accuracy fixes:

```bash
multipass exec lintap-dev -- bash -lc "cd /home/ubuntu/git/Wintap-Analytics/validation/process-creation && bash scripts/run_lintap_currentish_long_run.sh"
```

## Manual Checks

- Confirmed `process_retention_telemetry` is present and included in the summary output.
- Confirmed telemetry rows now include `pid_hash`, so metrics can be related back to specific process identities later instead of only process-name aggregates.
- Confirmed the summary now reports `live_system_processes`, `tracked_open_rows`, `live_open_rows`, `stale_open_rows`, and sample stale-open rows.
- Added `live_process_coverage` to the summary so each run reports how many current `/proc` PIDs have a matching open row in the process table.
- Updated the runner to snapshot live `/proc` just before shutdown and pass that snapshot to the summarizer, so end-of-run coverage is measured against the actual pre-stop live process set rather than against post-stop `python3`/`duckdb` helper processes.
- Confirmed the short noisy run used aggressive sweep settings so retention and stale-open reconciliation executed during the run.
- Confirmed Windows compile was initially blocked by an unrelated missing `using System.IO;` import in `platform/windows/infrastructure/WindowsStateManager.cs`; after adding it, the compile passed.

## Results

- `Lintap.csproj` built successfully in `lintap-dev` with warnings only.
- `validation/process-creation` pytest suite passed in `lintap-dev`: `5 passed`.
- `Wintap.csproj -p:EnableWindowsTargeting=true` built successfully in `lintap-dev` with warnings only after the unrelated import fix.
- Short noisy retention run completed with:
  - run id `retention-smoke-1786640189`
  - workload manifest `438` processes across `39` cases
  - final `process` table `47` rows, `46` closed, `1` open
  - telemetry totals:
    - `stop_closed=507`
    - `reconciled_closed=28`
    - `retention_deleted=499`
  - no `retention_miss` rows observed in this short run
- The aggressive retention settings intentionally removed most short-lived rows before end-of-run summary, so this run demonstrates bounded growth and QA telemetry, not final attribution-parity tuning.
- Additional rerun with `ProcessRundown=true`:
  - command used the same 180-second workload with `PROCESS_RUNDOWN=true`
  - final summary still showed only `1` tracked-open row, but the new summary fields showed `live_system_processes=141`, `live_open_rows=0`, `stale_open_rows=1`
  - telemetry totals shifted to `stop_closed=456`, `reconciled_closed=173`, `retention_deleted=590`
  - interpretation: the reporting fix worked, and it exposed a real bug in how rundown-loaded rows interacted with Linux liveness reconciliation
- Investigation result:
  - first fix aligned the resolver's Linux start-time hash with the same `/proc/stat` boot-time basis used by rundown/exec paths, which corrected the catastrophic mismatch for boot-time processes
  - second fix made Linux reconciliation use `ProcReader.ReadProcessInfo()` directly and treat close start-time matches as the same live process instance, repairing `pid_hash` instead of closing the row when necessary
- Post-fix 90-second `ProcessRundown=true` run (`retention-rundown-fix3b-1786645301`):
  - `live_system_processes=143`
  - `tracked_open_rows=144`
  - `live_open_rows=139`
  - `live_pids_with_matching_open_row=139`
  - `live_pids_missing_open_row=4`
  - remaining misses were recent end-of-run processes, not the earlier long-lived daemon set (`cron`, `dbus-daemon`, `systemd-networkd`, `sshd`, `sshfs`, etc.)
  - previously missing long-lived service PIDs were verified open in DuckDB with `exit_time IS NULL`
- Extended 10-minute `ProcessRundown=true` run (`retention-rundown-10m-1786645515`):
  - workload: `486` manifest processes across `129` cases
  - `live_system_processes=138`
  - `tracked_open_rows=135`
  - `live_open_rows=130`
  - `live_pids_with_matching_open_row=130`
  - `live_pids_missing_open_row=8`
  - remaining misses were again recent processes created near the end of the run, not long-lived baseline services
  - telemetry totals: `stop_closed=524`, `reconciled_closed=48`, `retention_deleted=541`
- Snapshot-based 90-second run (`retention-rundown-snap-90s-1786646651`):
  - pre-stop live snapshot size `142`
  - `live_pids_with_matching_open_row=140`
  - `live_pids_missing_open_row=2`
  - `tracked_open_rows=141`
  - `stale_open_rows=1`
  - telemetry totals: `stop_closed=99`, `reconciled_closed=12`, `retention_deleted=75`
- Snapshot-based 10-minute run (`retention-rundown-snap-10m-1786646842`):
  - workload: `482` manifest processes across `128` cases
  - pre-stop live snapshot size `139`
  - `live_pids_with_matching_open_row=131`
  - `live_pids_missing_open_row=8`
  - `tracked_open_rows=133`
  - `stale_open_rows=2`
  - telemetry totals: `stop_closed=520`, `reconciled_closed=42`, `retention_deleted=530`
  - interpretation: the remaining misses are now a small tail of real pre-stop live processes, not the earlier artifact of summary-time helper processes or the original long-lived daemon mismatch
- Snapshot filter tightening:
  - excluding `Lintap`, the snapshot helper, and the helper ancestor chain removed the remaining harness-self-noise from the coverage metric
  - 90-second run `retention-rundown-snapcov4-90s-1786651921` reached `135/135` live snapshot PIDs covered with `0` missing live PIDs
- Clone-enabled validation:
  - hypothesis: the remaining live misses were mid-run fork-only processes, not retention/reconciliation failures
  - 90-second run with `CLONE_SENSOR=true` (`retention-rundown-clone-90s-1786652858`) reached `135/135` live snapshot PIDs covered with `0` missing live PIDs
  - 10-minute run with `CLONE_SENSOR=true` (`retention-rundown-clone-10m-1786653050`) reached `137/137` live snapshot PIDs covered with `0` missing live PIDs
  - interpretation: the remaining pre-stop live-process misses in the clone-disabled runs were fork-without-exec processes that need the clone sensor to be enabled; the currentish-process table itself is now accurate for the live snapshot when the relevant sensors are on
- Long-run profile prepared:
  - added `scripts/run_lintap_currentish_long_run.sh`
  - defaults: `ProcessRundown=true`, `Clone=true`, `PROCESS_SWEEP_INTERVAL_SEC=60`, `PROCESS_EXIT_RETENTION_SEC=3600`, `PROCESS_RECONCILE_MIN_AGE_SEC=30`, `DURATION_SECONDS=21600`
  - intended for the parallel long-running validation pass
- Note on manifest metrics under aggressive retention:
  - with `PROCESS_EXIT_RETENTION_SEC=45`, end-of-run manifest-join counts are intentionally not a good workload-parity metric because most short-lived workload rows have already been pruned by summary time

## Known Gaps

- Windows runtime behavior unverified (compile only): reconciliation via
  `Process.GetProcessById` and retention interplay with
  `ClearDB`/startup replay need a Windows regression check before feature
  closeout.
- No long-duration plateau run yet.
- No before/after pidstat-based CPU correlation run yet.
- No direct DuckDB compaction/reclaim measurement yet.
- The short noisy run is not sufficient to set the final default retention window.
- Remaining misses are concentrated in very recent end-of-run processes and a small number of stale open rows; the long-lived daemon mismatch that originally broke rundown-enabled validation appears fixed.
- End-of-run live-process coverage is now measured correctly against a pre-stop snapshot, so the residual miss count is a real signal rather than a summary-window artifact.
- With `Clone=true`, pre-stop live-process coverage reached `0` missing live PIDs in both the short and 10-minute validation runs.

## Independent Review (2026-08-13)

Reviewed by the wiki-maintainer session after the slice-1 commits landed
(`../wintap` 9d9c6fb; this repo 22702eb, 3483ab6, 4c797b3).

Independently re-verified in `lintap-dev`: `Lintap.csproj` build (0 errors)
and the validation pytest suite (5 passed).

Code-review assessment of `ProcessResolver.cs`:

- The integrity constraints hold by construction: the retention delete's
  predicate (`exit_time IS NOT NULL AND exit_time < cutoff`) cannot touch
  open rows; reconciliation is gated by min-age, closes only on live-hash
  mismatch, and repairs (with a collision guard) rather than closes when the
  live start time matches within 2 s. Failure backoff, telemetry SQL
  escaping, and stop-closed/pending-exit dedup all check out.
- The `/proc/stat btime` boot-time basis fix is a genuinely durable
  correction — the old uptime-derived basis drifted, which is what broke
  rundown-row reconciliation.

Findings (minor, none blocking):

1. Windows runtime behavior is compile-verified only: the
   `Process.GetProcessById` reconciliation path and retention's interplay
   with `ClearDB`/`SendProcessTreeToEsper` replay have not been exercised.
   Added to Known Gaps and the plan checklist.
2. `GetLinuxBootTimeUtc()` caches `DateTime.UtcNow` as the boot time if
   `btime` is missing/unparseable — a silent wrong-hash generator for the
   rest of the run. Unlikely on real Linux, but the fallback should not be
   cached.
3. Repair-collision warnings are logged uncapped every sweep for the same
   stuck row (mismatch-close logging is capped at 25); a pathological row
   could spam the log.

Review verdict: slice 1 accepted. The QA-telemetry-first design proved
itself — the rundown reconciliation bug was found by the feature's own
metrics, not by chance.

## Follow-Ups

1. Run the noisy workload for longer with a production-like retention window and compare attribution parity against the 2026-08-06 baseline.
2. Measure whether `DELETE` alone is enough for DuckDB query/storage improvement or whether periodic compaction is required.
3. Decide whether to add a `process_id` index after measuring hot-path benefit.
4. Decide whether `Clone=true` should become the default validation profile for long-run currentish-process checks, since fork-without-exec processes are otherwise an expected blind spot.
