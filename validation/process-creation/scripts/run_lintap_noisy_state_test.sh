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
  "Clone": false,
  "ProcessRundown": false,
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

cat > "$RUN_DIR/query.sql" <<'SQL'
SELECT 'table_totals' AS section,
  COUNT(*) AS rows,
  COUNT(DISTINCT pid_hash) AS distinct_pid_hashes,
  COUNT(DISTINCT process_id) AS distinct_pids,
  COUNT(*) FILTER (WHERE exit_time IS NULL) AS open_rows,
  COUNT(*) FILTER (WHERE exit_time IS NOT NULL) AS closed_rows
FROM process;

SELECT 'by_name' AS section, process_name, COUNT(*) AS rows,
  COUNT(*) FILTER (WHERE exit_time IS NULL) AS open_rows,
  COUNT(*) FILTER (WHERE exit_time IS NOT NULL) AS closed_rows
FROM process
GROUP BY process_name
ORDER BY rows DESC
LIMIT 25;

SELECT 'duplicate_pid' AS section, process_id, COUNT(*) AS rows,
  COUNT(DISTINCT pid_hash) AS identities,
  COUNT(*) FILTER (WHERE exit_time IS NULL) AS open_rows
FROM process
GROUP BY process_id
HAVING COUNT(*) > 1
ORDER BY rows DESC
LIMIT 25;

SELECT 'stop_only_like' AS section,
  COUNT(*) AS rows
FROM process
WHERE create_time = exit_time AND exit_time IS NOT NULL;
SQL

sudo duckdb -json "$DB" < "$RUN_DIR/query.sql" > "$RUN_DIR/process-table-summary.json"

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
