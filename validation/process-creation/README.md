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
