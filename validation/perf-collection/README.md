# Wintap/Lintap Performance Collection

Manual-batch collectors for diagnosing long-running `Lintap` behavior.

The goal is to collect additional performance evidence into the same raw-style
partitioned parquet layout used elsewhere:

```text
<data_root>/parquet/raw_sensor/<event_type>/dayPK=YYYYMMDD/hourPK=HH/<file>.parquet
```

Current collectors:

- `perf_smaps_rollup` from `/proc/<pid>/smaps_rollup`
- `perf_fd_map` from `/proc/<pid>/fd` and `/proc/<pid>/maps`
- `perf_proc_status` from `/proc/<pid>/status`
- optional raw line capture from external commands:
  - `perf_dotnet_counters_raw`
  - `perf_lintap_diag_raw`

## Quick Start

```bash
cd validation/perf-collection
uv run --extra dev pytest

# real Linux/manual batch mode
export WINTAP_DATA_ROOT=/tmp/lintap-perf
uv run wpc-perf-batch --process-name-substring Lintap --duration-seconds 300 --interval-seconds 5
```

Shell wrapper:

```bash
cd validation/perf-collection
bash scripts/run_lintap_perf_batch.sh
```

Optional external command capture:

```bash
DOTNET_COUNTERS_COMMAND='dotnet-counters monitor --process-id 12345 --refresh-interval 5 System.Runtime' \
LINTAP_DIAG_COMMAND='some-future-lintap-diag-command --jsonl' \
bash scripts/run_lintap_perf_batch.sh
```

The wrapper does not assume a specific `dotnet-counters` output format yet. It
captures stdout lines as parquet rows so the command can be iterated on quickly
without redesigning storage.

## Developer / Operator Usage

### 1. Run a short manual capture on the host

Fastest path on a Linux host with a live `Lintap` process:

```bash
cd validation/perf-collection

export WINTAP_DATA_ROOT=/tmp/lintap-perf
bash scripts/run_lintap_perf_batch.sh
```

Useful overrides:

```bash
RUN_ID=lintap-perf-5m \
DURATION_SECONDS=300 \
INTERVAL_SECONDS=5 \
PROCESS_NAME_SUBSTRING=Lintap \
bash scripts/run_lintap_perf_batch.sh
```

If you already know the PID, call the CLI directly:

```bash
uv run wpc-perf-batch \
  --data-root "$WINTAP_DATA_ROOT" \
  --pid 12345 \
  --duration-seconds 300 \
  --interval-seconds 5
```

### 2. Optional external collectors

If `dotnet-counters` or a future Lintap diagnostic command is available on the
host, capture its stdout into provisional raw event types alongside the procfs
collectors:

```bash
DOTNET_COUNTERS_COMMAND='dotnet-counters monitor --process-id 12345 --refresh-interval 5 System.Runtime' \
LINTAP_DIAG_COMMAND='some-future-lintap-diag-command --jsonl' \
bash scripts/run_lintap_perf_batch.sh
```

Today these land as raw line-capture event types:

- `perf_dotnet_counters_raw`
- `perf_lintap_diag_raw`

That is deliberate: it keeps command-format iteration cheap before we commit to
a durable parsed schema.

### 3. Inspect what was written

The collector writes canonical partitioned parquet under:

```text
$WINTAP_DATA_ROOT/parquet/raw_sensor/
  perf_smaps_rollup/
  perf_proc_status/
  perf_fd_map/
  perf_dotnet_counters_raw/   # optional
  perf_lintap_diag_raw/       # optional
```

Example quick inspection with DuckDB:

```bash
duckdb -c "
  select *
  from read_parquet('$WINTAP_DATA_ROOT/parquet/raw_sensor/perf_smaps_rollup/**/*.parquet')
  limit 10
"
```

### 4. What to look for first

- `perf_smaps_rollup`: whether the stair steps are mostly `RssAnon` vs `RssFile`
- `perf_proc_status`: whether `VmRSS`, `RssAnon`, and context-switch counters move together
- `perf_fd_map`: whether FD count or mapped-region count ratchets upward with RSS
- optional `perf_dotnet_counters_raw`: whether GC/heap signals track RSS steps

### 5. Current scope

This package is intentionally manual-batch-first.

It is suitable for:

- short on-host captures today
- iterating on which signals matter
- writing outputs in the same raw-style parquet layout we would use later for a
  long-running sidecar

It is not yet a fully automated long-term background collector.
