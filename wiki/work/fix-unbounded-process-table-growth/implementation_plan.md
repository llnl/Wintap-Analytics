---
title: "Implementation Plan: Fix Unbounded Process Table Growth"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../Wintap-Analytics/validation/process-creation/scripts/run_lintap_noisy_state_test.sh
policy: agent-editable
last_validated: 2026-08-13
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: developer
status: draft
source_paths: wiki/work/fix-unbounded-process-table-growth/implementation_plan.md
tags: [feature-work, process-events, retention]
---

# Implementation Plan: Fix Unbounded Process Table Growth

## Scope

Implement the first working slice: bounded exited-row retention, stale-open reconciliation, telemetry/QA output, VM build validation, and a short noisy retention run.

## Steps

1. Add configurable sweep/reconciliation logic to `ProcessResolver`.
2. Emit stop/reconciled/deleted/retention-miss metrics through one shared telemetry surface.
3. Extend the validation summarizer and noisy-state runner to expose the telemetry.
4. Verify Linux build, validation harness tests, Windows compile, and a short noisy retention run in `lintap-dev`.
5. Follow up with longer-duration plateau/perf validation and DuckDB reclaim measurements.

## Files Likely To Change

- `../wintap/wintap/core/infrastructure/ProcessResolver.cs`
- `../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs`
- `validation/process-creation/scripts/summarize_lintap_process_table.py`
- `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`

## Tests To Add Or Update

- Build `Lintap.csproj` in the Linux VM.
- Build `Wintap.csproj` with `EnableWindowsTargeting=true` in the Linux VM.
- Run `uv run --extra dev pytest` for `validation/process-creation` in the Linux VM.
- Run a short noisy retention scenario with aggressive sweep settings in the Linux VM.

## Migration Or Compatibility Notes

- Existing deployments get retention enabled by default with conservative settings.
- Windows compile required a missing `using System.IO;` import in `WindowsStateManager.cs`; unrelated to the retention feature but necessary for the validation build.

## Rollback Plan

- Disable the feature with `WINTAP_PROCESS_RETENTION_ENABLED=false`.
- If needed, revert the new telemetry queries in the validation harness while keeping the resolver code isolated.

## Done Checklist

- [x] Resolver sweep added behind config.
- [x] Stale-open reconciliation closes dead rows by liveness check.
- [x] QA telemetry emitted for stop-closed vs reconciled-closed rows.
- [x] Retention deletes counted and surfaced in the harness summary.
- [x] Linux VM build passed.
- [x] Validation harness tests passed in the Linux VM.
- [x] Windows project compile passed in the Linux VM after fixing an unrelated import error.
- [x] Short noisy retention run completed in the Linux VM and populated telemetry.
- [x] Slice 1 reviewed and accepted (2026-08-13; build + pytest independently re-verified).

Remaining before feature closeout:

- [ ] Long-run plateau validation (`scripts/run_lintap_currentish_long_run.sh`) with attribution parity vs. the 2026-08-06 baseline.
- [ ] CPU-vs-table-size correlation from pidstat data (before/after) — uses the pidstat collector built by [[wiki/work/improve-pidstat-collector/brief]].
- [ ] DuckDB reclaim behavior measured (DELETE vs. compaction).
- [ ] Windows runtime regression check (reconciliation path, ClearDB/startup replay) — review finding 1.
- [ ] Review findings 2–3 fixed (uncached btime fallback; capped collision logging).
- [ ] Closeout: promote durable facts to canonical pages — candidates: event-store "currentish" retention semantics, env knobs, and `process_retention_telemetry` (new component/data_model page + `wiki/event_type/process-events.md`); the `/proc/stat btime` hash-basis fact; the clone-sensor requirement for fork-without-exec live coverage (also feeds the lintap-process-creation-validation thread).
