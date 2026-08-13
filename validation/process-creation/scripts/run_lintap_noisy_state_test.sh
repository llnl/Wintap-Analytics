#!/usr/bin/env bash
set -euo pipefail

RUN_ID=${RUN_ID:-noisy-state-$(date +%s)}
DATA_ROOT=${DATA_ROOT:-/tmp/lintap-${RUN_ID}}
RUN_DIR=${RUN_DIR:-/tmp/validation-runs/${RUN_ID}}
LINTAP_DLL=${LINTAP_DLL:-/home/ubuntu/git/wintap/wintap/bin/Debug/net8.0/Lintap.dll}
VALIDATION_DIR=${VALIDATION_DIR:-/home/ubuntu/git/Wintap-Analytics/validation/process-creation}
UV_PROJECT_ENVIRONMENT=${UV_PROJECT_ENVIRONMENT:-/tmp/wpv-venv}

DURATION_SECONDS=${DURATION_SECONDS:-780}
INTERVAL_SECONDS=${INTERVAL_SECONDS:-5}
SHORT_PER_INTERVAL=${SHORT_PER_INTERVAL:-12}
LONG_PER_MINUTE=${LONG_PER_MINUTE:-4}
LONG_LIVED_SECONDS=${LONG_LIVED_SECONDS:-90}
PROCESS_SWEEP_INTERVAL_SEC=${PROCESS_SWEEP_INTERVAL_SEC:-60}
PROCESS_EXIT_RETENTION_SEC=${PROCESS_EXIT_RETENTION_SEC:-600}
PROCESS_RECONCILE_MIN_AGE_SEC=${PROCESS_RECONCILE_MIN_AGE_SEC:-30}
PROCESS_RUNDOWN=${PROCESS_RUNDOWN:-false}
CLONE_SENSOR=${CLONE_SENSOR:-false}

mkdir -p "$RUN_DIR" "$DATA_ROOT"
CONFIG="$RUN_DIR/etlconfig.json"

cat > "$CONFIG" <<EOF
{
  "DataRoot": "$DATA_ROOT",
  "DisableMCP": true,
  "DisableDuckDBUI": true,
  "DisableSettings": true,
  "DisableETL": true,
  "EnableDirectParquet": false,
  "SkipEsperSend": true,
  "SkipProcessResolve": false,
  "SkipParentProcessResolve": false,
  "SkipProcessRegister": false,
  "DisableSensors": false,
  "Execve": true,
  "Exit": true,
  "Clone": ${CLONE_SENSOR},
  "ProcessRundown": ${PROCESS_RUNDOWN},
  "Network": false,
  "FileOps": false,
  "EnableBpfDiagMonitor": false
}
EOF

cleanup() {
  if [[ -n "${LINTAP_PID:-}" ]] && kill -0 "$LINTAP_PID" 2>/dev/null; then
    sudo kill -INT "$LINTAP_PID" 2>/dev/null || true
    sudo pkill -INT -f "$LINTAP_DLL" 2>/dev/null || true
    for _ in $(seq 1 20); do
      if ! kill -0 "$LINTAP_PID" 2>/dev/null && ! pgrep -f "$LINTAP_DLL" >/dev/null 2>&1; then
        return
      fi
      sleep 1
    done
    sudo kill "$LINTAP_PID" 2>/dev/null || true
    sudo pkill -TERM -f "$LINTAP_DLL" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "==> Starting Lintap resolver-mode run: $RUN_ID"
sudo env WINTAP_CONFIG_PATH="$CONFIG" ASPNETCORE_URLS=http://127.0.0.1:0 \
  WINTAP_PROCESS_SWEEP_INTERVAL_SEC="$PROCESS_SWEEP_INTERVAL_SEC" \
  WINTAP_PROCESS_EXIT_RETENTION_SEC="$PROCESS_EXIT_RETENTION_SEC" \
  WINTAP_PROCESS_RECONCILE_MIN_AGE_SEC="$PROCESS_RECONCILE_MIN_AGE_SEC" \
  dotnet "$LINTAP_DLL" > "$RUN_DIR/lintap.out" 2> "$RUN_DIR/lintap.err" &
LINTAP_PID=$!
echo "$LINTAP_PID" > "$RUN_DIR/lintap.pid"
sleep 25

echo "==> Running noisy process workload for ${DURATION_SECONDS}s"
cd "$VALIDATION_DIR"
UV_PROJECT_ENVIRONMENT="$UV_PROJECT_ENVIRONMENT" uv run wpv-noisy-processes \
  --run-dir "$RUN_DIR/workload" \
  --run-id "$RUN_ID" \
  --duration-seconds "$DURATION_SECONDS" \
  --interval-seconds "$INTERVAL_SECONDS" \
  --short-per-interval "$SHORT_PER_INTERVAL" \
  --long-per-minute "$LONG_PER_MINUTE" \
  --long-lived-seconds "$LONG_LIVED_SECONDS" | tee "$RUN_DIR/workload.out"

echo "==> Waiting for final exit events"
sleep 20

LINTAP_PID_FOR_SNAPSHOT="$LINTAP_PID" python3 - <<'PY' > "$RUN_DIR/live-proc-snapshot.json"
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

def get_boot_time_utc():
    for line in Path('/proc/stat').read_text().splitlines():
        if line.startswith('btime '):
            return datetime.fromtimestamp(int(line.split()[1]), tz=timezone.utc)
    raise RuntimeError('missing btime')

def get_clock_ticks_per_second():
    return os.sysconf(os.sysconf_names['SC_CLK_TCK'])

boot_utc = get_boot_time_utc()
hz = get_clock_ticks_per_second()
rows = []
excluded_pids = {os.getpid(), os.getppid()}

ancestor_pid = os.getppid()
while ancestor_pid > 1 and ancestor_pid not in excluded_pids:
    excluded_pids.add(ancestor_pid)
    try:
        stat = Path(f'/proc/{ancestor_pid}/stat').read_text()
        end = stat.rfind(')')
        if end < 0:
            break
        parts = stat[end + 1:].strip().split()
        if len(parts) < 2:
            break
        ancestor_pid = int(parts[1])
    except Exception:
        break

lintap_pid = os.environ.get('LINTAP_PID_FOR_SNAPSHOT')
if lintap_pid:
    try:
        excluded_pids.add(int(lintap_pid))
    except ValueError:
        pass

def is_descended_from_excluded(pid: int) -> bool:
    current = pid
    visited = set()
    while current > 1 and current not in visited:
        if current in excluded_pids:
            return True
        visited.add(current)
        try:
            stat = Path(f'/proc/{current}/stat').read_text()
            end = stat.rfind(')')
            if end < 0:
                return False
            parts = stat[end + 1:].strip().split()
            if len(parts) < 2:
                return False
            current = int(parts[1])
        except Exception:
            return False
    return current in excluded_pids

for proc_dir in sorted(Path('/proc').iterdir(), key=lambda path: int(path.name) if path.name.isdigit() else -1):
    if not proc_dir.is_dir() or not proc_dir.name.isdigit():
        continue
    pid = int(proc_dir.name)
    if pid in excluded_pids or is_descended_from_excluded(pid):
        continue
    stat_path = proc_dir / 'stat'
    try:
        stat = stat_path.read_text()
        end = stat.rfind(')')
        if end < 0:
            continue
        parts = stat[end + 1:].strip().split()
        if len(parts) <= 19:
            continue
        start_ticks = int(parts[19])
        start_utc = boot_utc + timedelta(seconds=start_ticks / hz)
        rows.append({
            'process_id': int(proc_dir.name),
            'live_start_utc': start_utc.isoformat().replace('+00:00', 'Z'),
        })
    except Exception:
        continue

print(json.dumps({
    'captured_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'processes': rows,
}, indent=2))
PY

cleanup
trap - EXIT

for _ in $(seq 1 30); do
  if ! pgrep -f "$LINTAP_DLL" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

DB="$DATA_ROOT/event_store/main.duckdb"
if [[ ! -f "$DB" ]]; then
  echo "ERROR: missing process resolver DB: $DB" >&2
  exit 3
fi

python3 "$VALIDATION_DIR/scripts/summarize_lintap_process_table.py" \
  --db "$DB" \
  --manifest "$RUN_DIR/workload/manifest.json" \
  --live-snapshot "$RUN_DIR/live-proc-snapshot.json" \
  --out "$RUN_DIR/process-table-summary.json" >/dev/null

python3 - <<PY | tee "$RUN_DIR/run-summary.json"
import json
from pathlib import Path
manifest = json.loads(Path('$RUN_DIR/workload/manifest.json').read_text())
print(json.dumps({
  'run_id': '$RUN_ID',
  'data_root': '$DATA_ROOT',
  'run_dir': '$RUN_DIR',
  'manifest_processes': len(manifest['processes']),
  'manifest_cases': len(manifest['cases']),
  'db': '$DB',
}, indent=2))
PY

echo "==> Run directory: $RUN_DIR"
