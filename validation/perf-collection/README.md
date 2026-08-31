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
- `perf_dotnet_counters` from file-based `dotnet-counters collect --format json|csv`
- optional raw line capture from external commands:
  - `perf_lintap_diag_raw`

## Quick Start

```bash
cd validation/perf-collection
uv run --extra dev pytest

# real Linux/manual batch mode
export WINTAP_DATA_ROOT=/tmp/lintap-perf
uv run wpc-perf-batch --process-name-substring Lintap --duration-seconds 300 --interval-seconds 5
```

If `Lintap` is running as a service account or `/proc` access is restricted,
run the collector with `sudo` so `smaps_rollup`, `status`, `fd`, and `maps`
can be read. The shell wrapper now self-elevates automatically if needed:

```bash
cd validation/perf-collection
export WINTAP_DATA_ROOT=/tmp/lintap-perf
bash scripts/run_lintap_perf_batch.sh
```

If you prefer to call the CLI directly, use `sudo -E` yourself:

```bash
sudo -E uv run wpc-perf-batch --process-name-substring Lintap --duration-seconds 300 --interval-seconds 5
```

Shell wrapper:

```bash
cd validation/perf-collection
bash scripts/run_lintap_perf_batch.sh
```

Focused root-owned-service wrapper:

```bash
cd validation/perf-collection
bash scripts/capture_lintap_perf_for_user.sh
```

This wrapper is the recommended path when `Lintap` is running as `root` and you
want the finished parquet handed back to the invoking user. It:

- resolves the live target PID as `root`
- runs `wpc-perf-batch` against that PID
- auto-enables `dotnet-counters collect --format json` when available
- `chown`s the output tree back to the invoking user after the capture finishes

Optional external command capture:

```bash
LINTAP_DIAG_COMMAND='some-future-lintap-diag-command --jsonl' \
bash scripts/run_lintap_perf_batch.sh
```

For `.NET` runtime counters, the collector now uses `dotnet-counters collect`
with file output and parses the resulting `json` or `csv` directly into
`perf_dotnet_counters`. The older terminal-scraping `monitor` path is removed.

## Developer / Operator Usage

### 1. Run a short manual capture on the host

Fastest path on a Linux host with a live `Lintap` process:

```bash
cd validation/perf-collection

export WINTAP_DATA_ROOT=/tmp/lintap-perf
bash scripts/run_lintap_perf_batch.sh
```

If the summary reports `collector_errors` for `perf_smaps_rollup` or
`perf_fd_map`, rerun with `sudo -E`.

### dotnet-counters support

Verify whether `dotnet-counters` is already installed:

```bash
which dotnet
which dotnet-counters || true
dotnet-counters --version
```

If `dotnet-counters` is missing but `dotnet` is present, install it as a global
tool:

```bash
dotnet tool install -g dotnet-counters
```

If it is already installed and you just want the latest version:

```bash
dotnet tool update -g dotnet-counters
```

If `dotnet-counters` installs under `~/.dotnet/tools`, ensure that directory is
on `PATH`:

```bash
export PATH="$HOME/.dotnet/tools:$PATH"
```

Quick smoke check against a running target PID:

```bash
dotnet-counters collect --process-id <PID> --refresh-interval 5 --format json --output /tmp/dotnet-counters-smoke --duration 00:00:10 --counters System.Runtime
```

If the target process is owned by another user, the diagnostics attach may also
need matching privileges even when parts of `/proc/<pid>` remain readable.

If that writes a `json` or `csv` output file successfully, the root wrapper can
use the same tool path for long perf captures.

Useful overrides:

```bash
RUN_ID=lintap-perf-5m \
DURATION_SECONDS=300 \
INTERVAL_SECONDS=5 \
PROCESS_NAME_SUBSTRING=Lintap \
bash scripts/run_lintap_perf_batch.sh
```

Equivalent focused root-wrapper example:

```bash
RUN_ID=lintap-perf-5m \
DURATION_SECONDS=300 \
INTERVAL_SECONDS=5 \
WINTAP_DATA_ROOT=/tmp/lintap-perf \
bash scripts/capture_lintap_perf_for_user.sh
```

If you want to skip runtime counters for one run:

```bash
ENABLE_DOTNET_COUNTERS=0 bash scripts/capture_lintap_perf_for_user.sh
```

If you want the procfs sampler and `dotnet-counters` on different cadences:

```bash
INTERVAL_SECONDS=5 \
DOTNET_COUNTERS_REFRESH_INTERVAL=10 \
bash scripts/capture_lintap_perf_for_user.sh
```

If you want `csv` instead of the default `json` output mode:

```bash
DOTNET_COUNTERS_FORMAT=csv bash scripts/capture_lintap_perf_for_user.sh
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
host, capture structured runtime counters plus any future diagnostic stdout alongside the procfs
collectors:

```bash
DOTNET_COUNTERS_FORMAT=json \
LINTAP_DIAG_COMMAND='some-future-lintap-diag-command --jsonl' \
bash scripts/capture_lintap_perf_for_user.sh
```

Today these land as these event types:

- `perf_dotnet_counters`
- `perf_lintap_diag_raw`

This keeps the `.NET` runtime path durable for long runs while still leaving the
future Lintap-specific diagnostic command flexible.

### 3. Inspect what was written

The collector writes canonical partitioned parquet under:

```text
$WINTAP_DATA_ROOT/parquet/raw_sensor/
  perf_smaps_rollup/
  perf_proc_status/
  perf_fd_map/
  perf_dotnet_counters/       # parsed from dotnet-counters collect output
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
- optional `perf_dotnet_counters`: whether GC/heap signals track RSS steps

### 5. Current scope

This package is intentionally manual-batch-first.

It is suitable for:

- short on-host captures today
- iterating on which signals matter
- writing outputs in the same raw-style parquet layout we would use later for a
  long-running sidecar

It is not yet a fully automated long-term background collector.
