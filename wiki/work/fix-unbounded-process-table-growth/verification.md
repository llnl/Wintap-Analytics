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
tags: [feature-work, verification, process-events, retention, starting-point]
---

# Verification: Fix Unbounded Process Table Growth

## Wiki Starting Point

Use this page as the starting point for the current status of the unbounded process-table fix. It captures the accepted Linux slice-1 evidence, the 2026-08-13 Windows runtime check, remaining validation gaps, and links the durable implementation facts back to `ProcessResolver` and the validation harness.

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

## Windows Runtime Check (2026-08-13)

Commands and actions run on the Windows host:

```powershell
cd C:\PUBLIC\Wintap-Analytics\validation\process-creation
uv run --extra dev pytest

cd C:\PUBLIC\wintap
dotnet publish "wintap\Wintap.csproj" -c Debug -r win-x64 --self-contained false
```

The first Windows attempt showed that the already-installed binaries were not the retention build: the test DB had no `process_retention_telemetry` table and the Wintap log lacked the `ProcessResolver retention:` startup line. Rebuilding the current source initially failed because `ProcessResolver.cs` referenced Linux `ProcReader` directly from the Windows build; the Windows compile fix replaced that direct dependency with a reflection-based Linux path and left Windows liveness on `Process.GetProcessById`.

After republishing and redeploying to `C:\Program Files\Wintap`, an elevated service-mode run used temporary service environment overrides:

```text
WINTAP_CONFIG_PATH=C:\tmp\validation-runs\windows-retention-smoke-20260813143307\ETLConfig.json
WINTAP_PROCESS_SWEEP_INTERVAL_SEC=15
WINTAP_PROCESS_EXIT_RETENTION_SEC=45
WINTAP_PROCESS_RECONCILE_MIN_AGE_SEC=10
WINTAP_DISABLE_MCP=true
WINTAP_DISABLE_DUCKDB_UI=true
WINTAP_DISABLE_ETL=true
```

Windows run artifacts:

- run id: `windows-retention-smoke-20260813143307`
- run dir: `C:\tmp\validation-runs\windows-retention-smoke-20260813143307`
- data root: `C:\tmp\wintap-windows-retention-smoke-20260813143307`
- DB: `C:\tmp\wintap-windows-retention-smoke-20260813143307\event_store\main.duckdb`
- transcript: `C:\Users\FRYE3~1.THE\AppData\Local\Temp\opencode\windows-retention-smoke-20260813143307.log`

Windows results:

- `uv run --extra dev pytest` passed on Windows: `5 passed`.
- `dotnet publish "wintap\Wintap.csproj" -c Debug -r win-x64 --self-contained false` passed after the cross-platform compile fix.
- Wintap service startup logged `ProcessResolver retention: enabled=True, sweepIntervalSec=15, exitRetentionSec=45, reconcileOpen=True, reconcileMinAgeSec=10`.
- Workload generated `390` manifest processes across `35` cases.
- Final process table had `278` rows: `223` closed and `55` open.
- `process_retention_telemetry` was present.
- Telemetry totals were `reconciled_closed=755` and `retention_deleted=532`.
- The Windows `Process.GetProcessById` stale-open reconciliation path executed repeatedly, as shown by Wintap log `ProcessResolver reconcile closing ... livePidHash=<missing>` and `livePidHash=<hash>` entries plus persisted telemetry.
- Manifest PID parity is not meaningful under the aggressive 45-second retention window: summary showed `151` observed manifest PIDs and `203` missing manifest PIDs after expired rows were deliberately pruned.

Windows limitation found:

- `ProcessSensor.Initialize` logged `Log wrap detected! Unable to build process tree, computer reboot required.` on this host, so `ClearDB` plus Security-log startup replay could not be fully validated in this run. Real-time process capture, Windows liveness reconciliation, retention deletion, and telemetry were validated.
- Live-process coverage is not comparable to the Linux `ProcessRundown=true` checks on this host because Windows startup replay was skipped after log-wrap detection; the summary therefore showed only `1/463` live snapshot PIDs with matching open rows.

## Known Gaps

- Windows runtime behavior unverified (compile only): reconciliation via
- Windows runtime behavior is now partially verified: service-mode retention,
  `Process.GetProcessById` reconciliation, retention deletion, and telemetry
  worked on 2026-08-13. Full `ClearDB`/startup replay verification still needs
  a Windows host/run where `ProcessSensor.Initialize` does not report Security
  log wrap.
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

## Field Diagnostic Utility (2026-08-23)

Created `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` for the current long-running RHEL 8-style field host where Lintap was observed at roughly 8.5 CPU cores after six days. The utility is read-only, runs as root, redacts common secret-like config keys, and packages process/thread samples, service config/status, recent journals, filesystem summaries, and read-only DuckDB `event_store` summaries including process-table counts, retention telemetry, schema/index metadata, and representative `process_id` lookup `EXPLAIN ANALYZE` output.

Run command:

```bash
sudo bash extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh
```

## Field Diagnostic Results (2026-08-23)

Host `spk16.llnl.gov` diagnostics (`/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260823T205648Z`) showed the first-slice retention logic is bounding the `process` table, but the QA telemetry table has become the new unbounded object in `event_store/main.duckdb`.

- Runtime: `/usr/lib/lintap/Lintap` PID `4055515` had been running for about six days and used roughly `8.5` cumulative CPU cores by `ps`, while `perf stat` sampled `13.9-15.2` CPUs over ten seconds. CPU was spread across many long-lived native `Lintap` threads plus sensor pollers, not a single managed hot loop.
- Fork storm ruled out for this sample: `/proc/stat processes` increased by only `33-37` over ten seconds (`3/sec` integer-rounded by the collector), unlike the earlier pidstat shell storm.
- DuckDB external-read caveat: the live DB cannot be opened read-only while Lintap holds the DuckDB file lock; DB queries were run against a root-made copy at `/root/main.duckdb`.
- `process` table shape: `64,742` rows, `48,788` distinct PIDs, `3,533` open rows, `61,209` closed rows. Most closed rows were within the last hour, consistent with exited-row retention working rather than the previous multi-million-row process table growth.
- `process_retention_telemetry` shape: `16,190,964` rows in six days (`stop_closed=3,837,973`, `reconciled_closed=4,285,786`, `retention_deleted=8,067,205`). This table has no retention/aggregation and now dominates the event-store row count.
- Schema/index evidence: `duckdb_indexes()` returned no indexes for `process`; representative pidhash/process lookup plans still used sequential scans over roughly `64k` process rows.
- Clone quality signal: top process rows and telemetry were dominated by `python3.12`, `sed`, `awk`, `hardware.sh`, `ps.sh`, `cpu.sh`, and similar short-lived monitoring commands. Many open `python3.12` rows had `parent_process_id=3199664`, the pidstat collector process. Because the production collector uses the in-process `/proc` sampler, this is more consistent with clone/thread events being registered as processes than with the collector spawning Python children.

Recommended fix order:

1. Make `process_retention_telemetry` bounded and cheap: aggregate per sweep instead of inserting one row per process identity by default, add a retention/delete policy for telemetry rows, and reserve per-`pid_hash` telemetry for opt-in debugging only.
2. Filter `CloneSensor` thread clones: do not emit process-start rows for `clone(2)` calls carrying `CLONE_THREAD`; keep fork/vfork and process-like clone coverage. This should reduce stale-open reconciliation load and improve pidhash-cache quality by avoiding thread IDs masquerading as process IDs.
3. Re-test `process_id` indexing only after the first two fixes. The copied DB shows sequential scans, but the bounded `process` table is currently much smaller than the telemetry table and may not be the primary CPU driver in this field run.

Post-pidstat-mitigation diagnostic (`/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260823T223445Z`) showed the collector noise fix worked but Lintap CPU remained high:

- `process` fell from `64,742` rows to `47,135` rows, with `1,950` open rows and `45,185` closed rows.
- `process_retention_telemetry` grew from `16,190,964` to `16,362,388` rows over roughly 98 minutes, adding about `171k` rows despite reduced pidstat noise.
- `python3.12` was no longer a top current process-row producer; open `python3.12` rows fell from `1117` to `31`.
- `perf stat` CPU dropped from `13.9-15.2` sampled CPUs to `9.4`, but `ps` still reported roughly `8.5` cumulative CPU cores.

Conclusion: the pidstat collector was a significant avoidable noise source, but the next runtime-quality fix should be in `../wintap`: bound/aggregate `process_retention_telemetry`, then filter `CloneSensor` thread-clone events and reassess process lookup indexing.

## Telemetry Bounding Fix (2026-08-23)

Implemented the first Wintap-side follow-up in `../wintap/wintap/core/infrastructure/ProcessResolver.cs`:

- `process_retention_telemetry` now writes aggregate rows by default: one row per sweep, metric name, and process name, with `metric_value` as the count and `pid_hash=NULL`.
- Per-process telemetry rows are still available by setting `WINTAP_PROCESS_RETENTION_TELEMETRY_DETAIL_ENABLED=true`; default is `false` for long-running hosts.
- `WINTAP_PROCESS_RETENTION_TELEMETRY_RETENTION_SEC` controls telemetry-table retention; default is `86400` seconds (24 hours).
- Each maintenance sweep prunes old telemetry rows after flushing the current sweep's aggregate metrics.
- Startup log now includes `telemetryRetentionSec` and `telemetryDetail` so field diagnostics can confirm the active policy.

Validation:

```bash
cd ../wintap
dotnet build wintap/Lintap.csproj
```

Result: build passed with existing warnings and `0` errors.

During validation, the outer Lintap build initially failed while publishing the
MCP server because stale generated files under
`shared/ai/wintap_mcp_server/mcp_temp/obj/...` were included in the MCP project
source glob, causing duplicate assembly attributes. `wintap_mcp_server.csproj`
already excluded direct `obj/**` and `bin/**`; it now also excludes
`mcp_temp/**` from `Compile`, `None`, `EmbeddedResource`, and `Content` globs.
The direct MCP publish and the outer `dotnet build wintap/Lintap.csproj` both
passed after that fix.

Expected field behavior after deploying/restarting Lintap: `process_retention_telemetry` should stop growing by hundreds of thousands of rows per hour. On first sweep after restart, old telemetry rows beyond 24 hours should be deleted; DuckDB file size may not shrink without a later compaction step.

Post-RPM validation on `spk16.llnl.gov` using `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260824T013652Z` confirmed the expected behavior after installing the new package and running about 2.5 hours:

- Runtime: Lintap PID `1918289`, elapsed `9023` seconds, `ps` CPU `118%`, RSS `1.3 GB`, `130` threads.
- `perf stat` sampled `1.211` CPUs over ten seconds, down from the prior post-pidstat-mitigation sample of `9.4` CPUs and the pre-mitigation `13.9-15.2` CPUs.
- Fork rate remained effectively quiet: `5` process creations over ten seconds.
- `process` table remained bounded: `47,648` rows, `1,977` open rows, `45,671` closed rows.
- `process_retention_telemetry` was bounded and aggregated: `4,721` rows total (`reconciled_closed=1,889` aggregate rows, `retention_deleted=1,373`, `stop_closed=1,459`) carrying aggregate `metric_value` totals.
- Copied DuckDB size was `19.0 MiB`, down from the pre-fix copied DB size of roughly `761 MiB`.
- `pid_hash` lookup plans still used sequential scans over ~47k rows, but measured query times were small in the copied DB (`0.0261s` for the sampled single lookup; `0.0140s` for sampled 100-PID join). Indexing remains a later optimization, not the current blocker.

Conclusion: the telemetry aggregation/retention fix addressed the runaway telemetry table and correlated with a large CPU drop on the field host. Remaining open quality/performance work is lower priority and should focus on CloneSensor thread-clone filtering and optional process lookup indexing.

Follow-up diagnostics from `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260824T033731Z` show the field host remained stable later in the run:

- Lintap PID `1996342` sampled at `1.471` CPUs by `perf stat`, with `ps` reporting `133%` cumulative CPU.
- `process` table was still bounded at `48,628` rows; `process_retention_telemetry` remained bounded at `9,459` aggregate rows.
- Copied DuckDB size was `30.7 MiB`.
- The copied DB contained `idx_process_process_id_create_time` on `(process_id, create_time)`, but the representative lookup `EXPLAIN ANALYZE` still used sequential scans over ~48k rows. Measured copied-DB times remained small (`0.0250s` for the sampled single lookup, `0.0123s` for the sampled 100-PID join).
- Current hot threads were sensor pollers (`CloneProcess`, `FileOps`, `ExitProcess`, `ExecveProcess`) rather than broad DuckDB/telemetry churn.

Conclusion: the process lookup index does not appear to be the next high-leverage optimization in DuckDB as currently planned by the optimizer. If further CPU reduction is needed, prefer reducing event volume/noise first (especially CloneSensor thread-clone filtering), or move hot process attribution to an in-memory current-process map instead of relying on additional DuckDB indexes.

## Clone Thread Filtering (2026-08-24)

Implemented the next event-volume reduction in `../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs`:

- Added a `CLONE_THREAD` flag check (`0x00010000`) before reading child/parent `/proc` state or emitting a process `Start` event.
- Preserved process-like clone/fork coverage when clone flags are missing (`0`) and preserved the vfork sentinel (`0xFFFFFFFFFFFFFFFF`).
- Rationale: `sched_process_fork` fires for thread creation as well as process creation. Thread task IDs are not process identities and were polluting the pidhash/process table, inflating stale-open reconciliation work and QA telemetry.

Validation:

```bash
cd ../wintap
dotnet build wintap/Lintap.csproj
```

Result: build passed with existing warnings and `0` errors.

Expected field behavior after deploying/restarting Lintap: fewer `python3.12`/runtime-worker-style process rows, fewer stale open rows caused by thread IDs, lower `reconciled_closed` totals for thread-heavy processes, and reduced CloneSensor/EventChannel work. Fork/vfork-only processes should still be represented because the filter only drops explicit `CLONE_THREAD` events.
