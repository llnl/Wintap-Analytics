#!/usr/bin/env bash
# Open-ended Linux stimuli; never manages collectors, uploads, or retention.
set -uo pipefail
umask 077

usage() {
  cat <<'EOF'
Usage: bash run-smoke-soak.sh --python PATH --devtools PATH --data-root PATH --evidence-root PATH
  [--interval 900] [--timeout 120] [--rounds 0] [--host-ip ADDRESS] [--clone-helper PATH]

Runs canary cross-domain, process lifecycle, eight-file, native clone (optional),
and same-host TCP endpoint stimuli. Never restarts/reconfigures the sensor.
Interval is the delay AFTER each sequential round; rounds=0 runs until stopped.
Timeout bounds each workload, not the collector. No automatic evidence deletion.
JSON/logs stay under evidence-root; snapshots go to data-root/raw_sensor/raw_smoke_test.
Both roots must be outside Git. Requires Linux, GNU timeout, flock, and DuckDB 1.5.6.
EOF
}
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
PYTHON='' DEVTOOLS='' DATA_ROOT='' EVIDENCE_ROOT='' HOST_IP='' CLONE_HELPER=''
INTERVAL=900 TIMEOUT=120 ROUNDS=0
while (($#)); do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --python|--devtools|--data-root|--evidence-root|--interval|--timeout|--rounds|--host-ip|--clone-helper)
      (($# >= 2)) || fail "Missing value for $1"
      case "$1" in
        --python) PYTHON=$2 ;; --devtools) DEVTOOLS=$2 ;;
        --data-root) DATA_ROOT=$2 ;; --evidence-root) EVIDENCE_ROOT=$2 ;;
        --interval) INTERVAL=$2 ;; --timeout) TIMEOUT=$2 ;; --rounds) ROUNDS=$2 ;;
        --host-ip) HOST_IP=$2 ;; --clone-helper) CLONE_HELPER=$2 ;;
      esac
      shift 2 ;;
    *) fail "Unknown argument: $1" ;;
  esac
done
[[ $(uname -s) == Linux ]] || fail 'This runner targets Linux only'
for tool in timeout flock git realpath mktemp; do
  command -v "$tool" >/dev/null || fail "Missing tool: $tool"
done
for number in "$INTERVAL" "$TIMEOUT" "$ROUNDS"; do
  [[ $number =~ ^(0|[1-9][0-9]{0,6})$ ]] || fail 'Intervals/counts must be decimal integers (maximum 7 digits)'
done
((INTERVAL > 0 && TIMEOUT > 0)) || fail 'Interval and timeout must be positive'
[[ -x $PYTHON ]] || fail '--python must name an executable interpreter'
[[ -d $DEVTOOLS && -n $DATA_ROOT && -n $EVIDENCE_ROOT ]] || fail 'All four required paths must be supplied'
[[ -z $CLONE_HELPER || -x $CLONE_HELPER ]] || fail 'Clone helper is not executable'
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P) || exit 1
DEVTOOLS=$(realpath -- "$DEVTOOLS") || exit 1
DATA_ROOT=$(realpath -m -- "$DATA_ROOT") || exit 1
EVIDENCE_ROOT=$(realpath -m -- "$EVIDENCE_ROOT") || exit 1
for root in "$DATA_ROOT" "$EVIDENCE_ROOT"; do
  ancestor=$root
  while [[ ! -d $ancestor ]]; do ancestor=$(dirname -- "$ancestor"); done
  # Detect working trees even when root's Git refuses a user-owned checkout.
  probe=$ancestor
  while :; do
    [[ ! -e $probe/.git ]] || fail 'Data/evidence roots must be outside Git working trees'
    [[ $probe != / ]] || break
    probe=$(dirname -- "$probe")
  done
  if git -C "$ancestor" rev-parse --show-toplevel >/dev/null 2>&1; then
    fail 'Data/evidence roots must be outside Git working trees'
  fi
done
"$PYTHON" - "$DEVTOOLS" <<'PY' || exit 1
import sys
import duckdb
sys.path.insert(0, sys.argv[1])
import telemetry_smoke_workload
import network_endpoint_smoke_test
import process_capture_smoke_test
import file_capture_smoke_test
if duckdb.__version__ != '1.5.6':
    raise SystemExit('ERROR: DuckDB 1.5.6 required')
PY
mkdir -p -- "$EVIDENCE_ROOT" "$DATA_ROOT/raw_sensor" || exit 1
exec 9>"$EVIDENCE_ROOT/.runner.lock" || exit 1
flock -n 9 || fail 'Another runner is using this evidence root'
SESSION=$(mktemp -d "$EVIDENCE_ROOT/session.XXXXXXXX") || exit 1
printf 'started_utc\ttest\texit_code\tevidence_status\n' >"$SESSION/status.tsv"
STOP=false CHILD=''
stop_runner() {
  STOP=true
  if [[ -n $CHILD ]]; then kill -TERM "$CHILD" 2>/dev/null || true; fi
}
trap stop_runner INT TERM HUP
run_test() {
  local name=$1 rc started evidence
  shift
  started=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  timeout --signal=TERM --kill-after=5s "${TIMEOUT}s" "$@" \
    >"$ROUND/$name.log" 2>&1 &
  CHILD=$!
  wait "$CHILD"; rc=$?
  if $STOP; then wait "$CHILD" 2>/dev/null || true; fi
  CHILD=''
  evidence=$("$PYTHON" - "$ROUND/$name.json" <<'PY'
import json
import sys
try:
    manifest = json.load(open(sys.argv[1]))
    if manifest.get('durableExportError'):
        print('export-error')
    elif not manifest.get('completedAtUtc'):
        print('incomplete')
    elif not manifest.get('selectors'):
        cases = (manifest.get('results') or {}).get('cases', [])
        print('skipped' if cases and all(c.get('status') == 'skipped' for c in cases) else 'no-selectors')
    else:
        print('recorded')
except (OSError, ValueError):
    print('missing-or-invalid')
PY
  ) || evidence='unreadable'
  printf '%s\t%s\t%s\t%s\n' "$started" "$name" "$rc" "$evidence" >>"$SESSION/status.tsv"
  printf '%s %s exit=%s evidence=%s (stimulus only)\n' "$started" "$name" "$rc" "$evidence"
}
printf 'Local-only evidence: %s\n' "$SESSION"
round=0
while ! $STOP; do
  round=$((round + 1))
  ROUND=$(mktemp -d "$SESSION/round.XXXXXXXX") || exit 1
  args=("$PYTHON" "$SCRIPT_DIR/canary-stimulus.py" --devtools "$DEVTOOLS" --suite cross-domain
    --manifest "$ROUND/named.json" --smoke-data-root "$DATA_ROOT" --output "$ROUND/workload")
  run_test named "${args[@]}"
  $STOP && break
  for suite in process file clone; do
    args=("$PYTHON" "$SCRIPT_DIR/canary-stimulus.py" --devtools "$DEVTOOLS" --suite "$suite"
      --manifest "$ROUND/$suite.json" --smoke-data-root "$DATA_ROOT" --output "$ROUND/$suite-workload")
    [[ $suite != clone || -z $CLONE_HELPER ]] || args+=(--clone-helper "$CLONE_HELPER")
    run_test "$suite" "${args[@]}"
    $STOP && break
  done
  $STOP && break
  args=("$PYTHON" "$SCRIPT_DIR/network-endpoint-stimulus.py" --devtools "$DEVTOOLS"
    --manifest "$ROUND/endpoints.json" --smoke-data-root "$DATA_ROOT")
  [[ -z $HOST_IP ]] || args+=(--host-ip "$HOST_IP")
  run_test endpoints "${args[@]}"
  $STOP && break
  ((ROUNDS == 0 || round < ROUNDS)) || break
  sleep "$INTERVAL" &
  CHILD=$!
  wait "$CHILD" || true
  CHILD=''
done
printf 'Runner stopped; collector unchanged. Evidence retained: %s\n' "$SESSION"
