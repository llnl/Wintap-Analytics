# Wintap Process Creation Validation

Prototype sensor-neutral validation harness for process creation telemetry research.

This project is intentionally runnable on macOS with mock data. Real sensor runs require Linux.

## Quick Start

```bash
cd validation/process-creation
uv run --extra dev pytest
uv run wpv-mock-run --run-dir /tmp/wpv-mock
```

## Commands

- `wpv-workload`: generate a process workload manifest. Works in a limited mode on macOS, with Linux-only cases skipped when unsupported.
- `wpv-evaluate`: evaluate normalized JSONL event tables against a manifest.
- `wpv-mock-run`: create a mock run directory and evaluate it. Useful for local development without Linux eBPF.
- `scripts/run_lintap_noisy_state_test.sh`: configurable Linux VM runner for resolver/process-table validation.
- `scripts/run_lintap_currentish_long_run.sh`: recommended long-run profile for validating the currentish process table. Defaults to `ProcessRundown=true`, `Clone=true`, `PROCESS_SWEEP_INTERVAL_SEC=60`, `PROCESS_EXIT_RETENTION_SEC=3600`, and a 6-hour run.
- `scripts/summarize_currentish_long_run.py`: concise post-run headline summary for shutdown coverage and retention telemetry.

## Long-Run Currentish Profile

Run this in `lintap-dev` for the validated long-run sensor mix:

```bash
cd validation/process-creation
bash scripts/run_lintap_currentish_long_run.sh
```

Useful overrides:

```bash
RUN_ID=currentish-long-check \
DURATION_SECONDS=43200 \
PROCESS_EXIT_RETENTION_SEC=7200 \
bash scripts/run_lintap_currentish_long_run.sh
```

Primary artifacts:

- `/tmp/validation-runs/<run-id>/process-table-summary.json`
- `/tmp/validation-runs/<run-id>/live-proc-snapshot.json`
- `/tmp/validation-runs/<run-id>/lintap.out`
- `/tmp/lintap-<run-id>/event_store/main.duckdb`

Quick headline after a run:

```bash
python3 scripts/summarize_currentish_long_run.py --run-dir /tmp/validation-runs/<run-id>
```

## Current Scope

Implemented now:

- Manifest schema and JSON serialization.
- Normalized JSONL event schema helpers.
- Mock normalized events.
- Evaluator metrics for process fork, exec attempt, exec success, exit, parent joins, duplicate exec success, identity collisions, and sensor loss totals.
- Basic process workload generator for simple exec, fork/exec, short-lived burst, and pre-existing sleep process metadata.

Not implemented yet:

- Lintap Parquet normalizer.
- Tetragon/Tracee/Sysdig normalizers.
- Live sensor runners.
- Linux eBPF setup automation.
