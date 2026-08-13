#!/usr/bin/env bash
set -euo pipefail

RUN_ID=${RUN_ID:-all-events-30m-$(date +%s)}
DATA_ROOT=${DATA_ROOT:-/tmp/lintap-${RUN_ID}}
RUN_DIR=${RUN_DIR:-/tmp/validation-runs/${RUN_ID}}
LINTAP_DLL=${LINTAP_DLL:-/home/ubuntu/git/wintap/wintap/bin/Debug/net8.0/Lintap.dll}
VALIDATION_DIR=${VALIDATION_DIR:-/home/ubuntu/git/Wintap-Analytics/validation/process-creation}
WINTAP_DIR=${WINTAP_DIR:-/home/ubuntu/git/wintap}
UV_PROJECT_ENVIRONMENT=${UV_PROJECT_ENVIRONMENT:-/tmp/wpv-venv}
TARGET_SECONDS=${TARGET_SECONDS:-1800}

mkdir -p "$RUN_DIR" "$DATA_ROOT"
CONFIG="$RUN_DIR/etlconfig.json"

cat > "$CONFIG" <<EOF
{
  "DataRoot": "$DATA_ROOT",
  "DisableMCP": true,
  "DisableDuckDBUI": true,
  "DisableSettings": true,
  "DisableETL": false,
  "EnableDirectParquet": false,
  "WriteToParquet": true,
  "SerializationIntervalSec": 10,
  "SkipEsperSend": false,
  "SkipProcessResolve": false,
  "SkipParentProcessResolve": false,
  "SkipProcessRegister": false,
  "DisableSensors": false,
  "Execve": true,
  "Clone": true,
  "Exit": true,
  "Network": true,
  "FileOps": true,
  "ProcessRundown": true,
  "EnableBpfDiagMonitor": false
}
EOF

cleanup() {
  if [[ -n "${LINTAP_PID:-}" ]]; then
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

START_EPOCH=$(date +%s)
{
  echo "RUN_ID=$RUN_ID"
  echo "DATA_ROOT=$DATA_ROOT"
  echo "RUN_DIR=$RUN_DIR"
  echo "START=$(date -Iseconds)"
} | tee "$RUN_DIR/run.env"

echo "==> Starting Lintap all-event normal ETL parquet"
sudo env WINTAP_CONFIG_PATH="$CONFIG" ASPNETCORE_URLS=http://127.0.0.1:0 \
  dotnet "$LINTAP_DLL" > "$RUN_DIR/lintap.out" 2> "$RUN_DIR/lintap.err" &
LINTAP_PID=$!
echo "$LINTAP_PID" > "$RUN_DIR/lintap.pid"
sleep 30

cd "$WINTAP_DIR"
set +e
python3 devtools/process_capture_smoke_test.py --data-root "$DATA_ROOT" --timeout 180 --poll-interval 5 > "$RUN_DIR/process-smoke.out" 2>&1
PROCESS_RC=$?
python3 devtools/file_capture_smoke_test.py --data-root "$DATA_ROOT" --timeout 180 --poll-interval 5 > "$RUN_DIR/file-smoke.out" 2>&1
FILE_RC=$?
python3 devtools/network_capture_smoke_test.py --data-root "$DATA_ROOT" --timeout 180 --poll-interval 5 > "$RUN_DIR/network-smoke.out" 2>&1
NETWORK_RC=$?
set -e
printf '%s\n' "$PROCESS_RC" > "$RUN_DIR/process-smoke.rc"
printf '%s\n' "$FILE_RC" > "$RUN_DIR/file-smoke.rc"
printf '%s\n' "$NETWORK_RC" > "$RUN_DIR/network-smoke.rc"

NOW=$(date +%s)
ELAPSED=$((NOW - START_EPOCH))
NOISY_SECONDS=$((TARGET_SECONDS - ELAPSED - 45))
if [[ "$NOISY_SECONDS" -lt 60 ]]; then
  NOISY_SECONDS=60
fi

echo "==> Running noisy process workload for ${NOISY_SECONDS}s" | tee "$RUN_DIR/noisy-control.out"
cd "$VALIDATION_DIR"
UV_PROJECT_ENVIRONMENT="$UV_PROJECT_ENVIRONMENT" uv run wpv-noisy-processes \
  --run-dir "$RUN_DIR/noisy-workload" \
  --run-id "$RUN_ID" \
  --duration-seconds "$NOISY_SECONDS" \
  --interval-seconds 5 \
  --short-per-interval 12 \
  --long-per-minute 4 \
  --long-lived-seconds 90 > "$RUN_DIR/noisy.out" 2> "$RUN_DIR/noisy.err"

sleep 20
cleanup
trap - EXIT
END_EPOCH=$(date +%s)
{
  echo "END=$(date -Iseconds)"
  echo "DURATION_SECONDS=$((END_EPOCH - START_EPOCH))"
} | tee -a "$RUN_DIR/run.env"

python3 - "$DATA_ROOT" "$RUN_DIR" "$RUN_ID" <<'PY' > "$RUN_DIR/parquet-summary.json"
import glob
import json
import subprocess
import sys
from pathlib import Path

data_root = Path(sys.argv[1])
run_dir = Path(sys.argv[2])
run_id = sys.argv[3]
parquet = data_root / "parquet"
files = sorted(Path(p) for p in glob.glob(str(parquet / "**" / "*.parquet*"), recursive=True) if not p.endswith(".active"))
summary = {"run_id": run_id, "data_root": str(data_root), "run_dir": str(run_dir), "files": len(files), "by_dir": {}}
for file in files:
    key = str(file.parent.relative_to(parquet)) if parquet in file.parents else str(file.parent)
    summary["by_dir"].setdefault(key, {"files": 0, "rows": None})["files"] += 1
for key in list(summary["by_dir"]):
    pattern = str(parquet / key / "*.parquet")
    try:
        sql = f"select count(*) from read_parquet('{pattern}', union_by_name=true)"
        output = subprocess.check_output(["duckdb", "-csv", "-c", sql], text=True)
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        summary["by_dir"][key]["rows"] = int(lines[-1])
    except Exception as exc:
        summary["by_dir"][key]["error"] = str(exc)
print(json.dumps(summary, indent=2, sort_keys=True))
PY

python3 - "$RUN_DIR" "$DATA_ROOT" "$RUN_ID" <<'PY' > "$RUN_DIR/run-summary.json"
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
data_root = sys.argv[2]
run_id = sys.argv[3]
summary = {
    "run_id": run_id,
    "data_root": data_root,
    "run_dir": str(run_dir),
    "process_smoke_rc": int((run_dir / "process-smoke.rc").read_text()),
    "file_smoke_rc": int((run_dir / "file-smoke.rc").read_text()),
    "network_smoke_rc": int((run_dir / "network-smoke.rc").read_text()),
    "process_smoke_pass": "PASS:" in (run_dir / "process-smoke.out").read_text(),
    "file_smoke_pass": "PASS:" in (run_dir / "file-smoke.out").read_text(),
    "network_smoke_pass": "PASS:" in (run_dir / "network-smoke.out").read_text(),
    "parquet_summary": json.loads((run_dir / "parquet-summary.json").read_text()),
}
manifest = run_dir / "noisy-workload" / "manifest.json"
if manifest.exists():
    data = json.loads(manifest.read_text())
    summary["noisy_manifest_processes"] = len(data.get("processes", []))
    summary["noisy_manifest_cases"] = len(data.get("cases", []))
print(json.dumps(summary, indent=2, sort_keys=True))
PY

cat "$RUN_DIR/run-summary.json"
