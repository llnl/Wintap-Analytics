---
title: "Dev Handoff: Fix Unbounded Process Table Growth"
type: concept
confidence: medium
grounded_by:
  - raw/Issues/Long_Running_Cleanup.md
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
policy: agent-editable
last_validated: 2026-08-13
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

    Goal: continue long-run validation for the bounded currentish-process
    table, using the validated Linux rundown+clone profile and the updated
    shutdown coverage summary, while preserving PID-reuse-safe process
    resolution.

    You are authorized to modify code in ../wintap for this feature.
    ../Lintap and ../Wintappy remain read-only. Wintap-Analytics may be
    modified only under validation/ (harness additions) and wiki/ (feature
    artifacts, log).

    Before editing code, read AGENTS.md and confirm that code-development
    mode is active for this task.

## Handoff Summary

This slice is no longer at the initial implementation stage. The resolver
now has:

1. exited-row retention
2. liveness-based stale-open reconciliation
3. telemetry rows with `pid_hash`
4. Linux live-identity reconciliation aligned with `ProcessRundownSensor`
5. validation harness support for pre-stop `/proc` snapshots and concise
   shutdown-coverage summaries

The current focus is long-run confidence, not first implementation.

Current validated findings:

- `ProcessRundown=true` plus `Clone=true` is the validated Linux profile for
  accurate currentish live-process coverage.
- Pre-stop shutdown coverage must be measured from a `/proc` snapshot taken
  before stopping `Lintap`, not from post-stop helper processes.
- The earlier rundown bug that closed long-lived live daemons has been fixed.
- Snapshot-based validation reached `0` missing live PIDs on:
  - a 90-second run with `Clone=true`
  - a 10-minute run with `Clone=true`

Still-open long-run questions:

- Does the 6h+ run continue to hold `0` missing live snapshot PIDs with the
  validated profile?
- Do stale-open rows remain near-zero over a much longer run?
- Does DuckDB `DELETE` alone keep the hot-path cost flat, or is compaction
  needed later?

## Primary Sources For The Dev Agent

- `../wintap/wintap/core/infrastructure/ProcessResolver.cs` — primary
  implementation site for retention, Linux liveness identity, and telemetry
- `../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs` — live
  rundown seeding path that must stay aligned with resolver identity logic
- `../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs` —
  canonical Linux `/proc` reader now reused by reconciliation
- `validation/process-creation/scripts/run_lintap_noisy_state_test.sh` —
  configurable runner with pre-stop live snapshot capture
- `validation/process-creation/scripts/run_lintap_currentish_long_run.sh` —
  validated long-run currentish profile
- `validation/process-creation/scripts/summarize_currentish_long_run.py` —
  concise shutdown-coverage/telemetry headline for completed runs
- `raw/Issues/Long_Running_Cleanup.md` — motivating issue.
- `wiki/work/lintap-process-creation-validation/current-state-2026-08-06.md`
  — pre-feature validation baseline and harness context.
- `wiki/work/fix-unbounded-process-table-growth/verification.md` — latest
  measured results, including the `Clone=true` zero-miss runs.

## Recommended Next Slice

1. Start the long-running validation in `lintap-dev` with the dedicated
   wrapper:

       multipass exec lintap-dev -- bash -lc "cd /home/ubuntu/git/Wintap-Analytics/validation/process-creation && bash scripts/run_lintap_currentish_long_run.sh"

2. After the run starts, use the headline helper on the artifact directory:

       python3 scripts/summarize_currentish_long_run.py --run-dir /tmp/validation-runs/<run-id>

3. Watch for:
   - `live_pids_missing_open_row == 0`
   - low `stale_open_rows`
   - no surprising jump in `reconciled_closed`
4. Only if the long run regresses, continue code changes; otherwise use the
   run primarily to collect confidence and plateau evidence.

Stretch: gather periodic DB row-count/size snapshots or pidstat alongside the
run for the later plateau/perf analysis.

## Non-Goals For This Slice

- Reworking the retention policy itself unless the long run shows a concrete
  regression.
- Broader sensor-accuracy research outside the currentish-process table goal.
- The pidstat/CPU-correlation study itself; just prepare and run the process
  table validation profile.

## Testing Expectations

- `Lintap.csproj` build still passes in `lintap-dev`.
- `validation/process-creation` pytest still passes.
- Long-run profile uses `ProcessRundown=true` and `Clone=true`.
- Post-run headline from `summarize_currentish_long_run.py` should show no
  missing live snapshot PIDs, or any misses should be explicitly explained.

## Closeout Instructions

- Create wiki/work/fix-unbounded-process-table-growth/verification.md with
  commands run and results.
- If the long run is launched but not yet complete, record the exact command,
  run id, and where the artifacts are accumulating.
- Append a concise entry to wiki/log.md.
- Leave canonical promotion for after the long-run evidence is in hand.
