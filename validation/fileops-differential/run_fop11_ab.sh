#!/usr/bin/env bash
# run_fop11_ab.sh — automated fop-11 kill-switch A/B differential.
#
# Runs the aggregation-OFF baseline and aggregation-ON candidate phases on
# the field host, harvests each phase's File rows from parquet by
# time-window + path-prefix (row-level, immune to file-boundary mixing),
# guards against serializer backlog invalidating the run, and executes the
# count-conserving comparator. Leaves the service running with aggregation
# ON regardless of outcome.
#
# Usage (as root on the field host):
#   ./run_fop11_ab.sh [--work-dir DIR] [--files N] [--rounds N]
#                     [--dir-churn N] [--data-root DIR] [--results-dir DIR]
#                     [--harvest-timeout SEC]
#
# Exit codes: 0 = PASS, 1 = comparator FAIL, 2 = vacuous/no data,
#             3 = run invalid (serializer backlog during a phase),
#             4 = environment/preflight failure.
set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
WORK_DIR=/var/tmp/fop11-ab/work
FILES=24
ROUNDS=4
DIR_CHURN=500
DATA_ROOT=""
RESULTS_DIR=""
HARVEST_TIMEOUT=600
SIMULATE_DIR=""
ENV_FILE=/etc/lintap/lintap.env
AGG_FLAG_LINE='WINTAP_FILEOPS_AGG_ENABLED=false'

while [ $# -gt 0 ]; do
  case $1 in
    --work-dir) WORK_DIR=${2:?}; shift 2 ;;
    --files) FILES=${2:?}; shift 2 ;;
    --rounds) ROUNDS=${2:?}; shift 2 ;;
    --dir-churn) DIR_CHURN=${2:?}; shift 2 ;;
    --data-root) DATA_ROOT=${2:?}; shift 2 ;;
    --results-dir) RESULTS_DIR=${2:?}; shift 2 ;;
    --harvest-timeout) HARVEST_TIMEOUT=${2:?}; shift 2 ;;
    --simulate) SIMULATE_DIR=${2:?}; shift 2 ;;  # internal: fixture-driven plumbing test
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 4 ;;
  esac
done

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }
die() { echo "FATAL: $*" >&2; exit 4; }

# ---------- environment resolution ----------

if [ -n "$SIMULATE_DIR" ]; then
  DATA_ROOT="$SIMULATE_DIR/dataroot"
  ENV_FILE="$SIMULATE_DIR/lintap.env"
  mkdir -p "$DATA_ROOT/parquet" "$SIMULATE_DIR"
  touch "$ENV_FILE"
else
  [ "$(id -u)" -eq 0 ] || die "must run as root (parquet under the data root is root-readable only)"
  if [ -z "$DATA_ROOT" ] && [ -r "$ENV_FILE" ]; then
    DATA_ROOT=$(awk -F= '/^[[:space:]]*WINTAP_DATA_ROOT[[:space:]]*=/ {gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); gsub(/^"|"$/, "", $2); print $2; exit}' "$ENV_FILE")
  fi
  DATA_ROOT=${DATA_ROOT:-/var/log/lintap}
  [ -d "$DATA_ROOT" ] || die "data root not found: $DATA_ROOT"
  command -v systemctl >/dev/null || die "systemctl not found"
fi

LINTAP_LOG="$DATA_ROOT/Logs/Lintap.log"
RESULTS_DIR=${RESULTS_DIR:-/var/tmp/fop11-ab-results-$(date -u +%Y%m%dT%H%M%SZ)}
mkdir -p "$RESULTS_DIR"
WORKLOAD="$SCRIPT_DIR/fileops_workload.py"
COMPARATOR="$SCRIPT_DIR/compare_fileops.py"
[ -r "$WORKLOAD" ] || die "workload script not found: $WORKLOAD"
[ -r "$COMPARATOR" ] || die "comparator not found: $COMPARATOR"

# Python-with-duckdb runner: prefer uv, fall back to system python3.
# Under sudo, root's secure_path usually lacks the invoking user's
# ~/.local/bin — discover their uv binary explicitly.
UV_BIN=$(command -v uv 2>/dev/null || true)
if [ -z "$UV_BIN" ] && [ -n "${SUDO_USER:-}" ]; then
  for cand in "/home/$SUDO_USER/.local/bin/uv" "/home/$SUDO_USER/.cargo/bin/uv"; do
    [ -x "$cand" ] && { UV_BIN=$cand; break; }
  done
fi
if [ -n "$UV_BIN" ]; then
  log "using uv: $UV_BIN"
  PYRUN=("$UV_BIN" run --with duckdb python3)
elif python3 -c 'import duckdb' 2>/dev/null; then
  PYRUN=(python3)
else
  die "need uv (not found in PATH or /home/\${SUDO_USER}/.local/bin) or python3 with the duckdb package"
fi

# ---------- helpers ----------

filetime_now() {
  # Windows FileTime (100ns since 1601) for 'now', in decimal.
  echo $((($(date -u +%s) + 11644473600) * 10000000))
}

serializer_drop_lines() {
  [ -r "$LINTAP_LOG" ] || { echo 0; return; }
  grep -ci 'serializer.*dropped=' "$LINTAP_LOG" 2>/dev/null || echo 0
}

set_agg() { # $1 = false|true
  if [ -n "$SIMULATE_DIR" ]; then return 0; fi
  sed -i "\%^${AGG_FLAG_LINE}\$%d" "$ENV_FILE"
  if [ "$1" = "false" ]; then
    printf '%s\n' "$AGG_FLAG_LINE" >>"$ENV_FILE"
  fi
  log "restarting lintap (aggregation=$1)"
  systemctl restart lintap || die "systemctl restart lintap failed"
}

wait_for_agg_state() { # $1 = false|true — verified from the live counter log
  if [ -n "$SIMULATE_DIR" ]; then return 0; fi
  local want="agg=[enabled=$1" deadline=$(($(date +%s) + 180)) line
  log "waiting for a FileOps counters line showing enabled=$1 (up to 180s)"
  while [ "$(date +%s)" -lt "$deadline" ]; do
    line=$(grep -E 'FileOps counters' "$LINTAP_LOG" 2>/dev/null | tail -1)
    case $line in *"$want"*) log "verified: $want]"; return 0 ;; esac
    sleep 10
  done
  die "never observed $want] in $LINTAP_LOG — check the service came up"
}

run_workload() { # $1 = phase
  if [ -n "$SIMULATE_DIR" ]; then
    "${PYRUN[@]}" "$SCRIPT_DIR/simulate_ab_fixture.py" \
      --phase "$1" --data-root "$DATA_ROOT" --work-dir "$WORK_DIR" || die "fixture generation failed"
    return 0
  fi
  log "running deterministic workload (phase=$1)"
  python3 "$WORKLOAD" \
    --work-dir "$WORK_DIR" \
    --manifest "$RESULTS_DIR/$1-manifest.json" \
    --files "$FILES" --rounds "$ROUNDS" --dir-churn "$DIR_CHURN" \
    || die "workload failed (phase=$1)"
}

harvest() { # $1 = phase, $2 = start_filetime, $3 = end_filetime
  local phase=$1 start_ft=$2 end_ft=$3
  local out="$RESULTS_DIR/$phase.parquet"
  local deadline=$(($(date +%s) + HARVEST_TIMEOUT)) prev=-1 count=0 stable=0
  log "harvesting $phase rows (firstSeen window + prefix $WORK_DIR)"
  while [ "$(date +%s)" -lt "$deadline" ]; do
    count=$("${PYRUN[@]}" - "$DATA_ROOT" "$WORK_DIR" "$start_ft" "$end_ft" "$out" <<'PYEOF'
import duckdb, glob, sys
data_root, prefix, start_ft, end_ft, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
files = [f for f in glob.glob(f"{data_root}/**/*.parquet", recursive=True)
         if "file" in f.rsplit("/", 1)[-1].lower()]
if not files:
    print(0)
    raise SystemExit(0)
file_list = ", ".join("'" + f.replace("'", "''") + "'" for f in files)
prefix_sql = prefix.replace("'", "''")
con = duckdb.connect()
try:
    con.execute(f"""
        CREATE TABLE hits AS
        SELECT * FROM read_parquet([{file_list}], union_by_name=true)
        WHERE path LIKE '{prefix_sql}%'
          AND COALESCE(firstSeen, 0) >= {start_ft}
          AND COALESCE(firstSeen, 0) <= {end_ft}
    """)
    n = con.execute("SELECT count(*) FROM hits").fetchone()[0]
    if n:
        con.execute(f"COPY hits TO '{out}' (FORMAT PARQUET)")
    print(n)
except Exception as exc:
    print(f"ERR {exc}", file=sys.stderr)
    print(0)
PYEOF
    ) || count=0
    log "  $phase harvest poll: $count rows"
    if [ "$count" -gt 0 ] && [ "$count" -eq "$prev" ]; then
      stable=$((stable + 1))
      # two consecutive identical nonzero counts = flush settled
      [ "$stable" -ge 1 ] && { echo "$count" >"$RESULTS_DIR/$phase.rowcount"; return 0; }
    else
      stable=0
    fi
    prev=$count
    sleep 20
  done
  echo "${count:-0}" >"$RESULTS_DIR/$phase.rowcount"
  [ "${count:-0}" -gt 0 ] && return 0
  return 1
}

flush_boundary() {
  # Force the serializer/parquet writer to emit pending rows: restart the
  # service with the CURRENT env (no mode change).
  if [ -n "$SIMULATE_DIR" ]; then sleep 3; return 0; fi
  log "flush boundary: restarting lintap"
  systemctl restart lintap || die "flush restart failed"
  sleep 15
}

# Always leave the host with aggregation ON, even on failure/interrupt.
cleanup() {
  if [ -z "$SIMULATE_DIR" ] && grep -q "^${AGG_FLAG_LINE}\$" "$ENV_FILE" 2>/dev/null; then
    log "cleanup: removing kill-switch and restarting (aggregation back ON)"
    sed -i "\%^${AGG_FLAG_LINE}\$%d" "$ENV_FILE"
    systemctl restart lintap || true
  fi
}
trap cleanup EXIT INT TERM

# ---------- phase runner ----------

PHASE_INVALID=0
LAST_PHASE_END_FT=0
# 10s margin real, 1s in simulation (fixtures are written seconds apart).
if [ -n "$SIMULATE_DIR" ]; then MARGIN_FT=10000000; else MARGIN_FT=100000000; fi

run_phase() { # $1 = off|on  $2 = agg false|true
  local phase=$1 agg=$2
  set_agg "$agg"
  wait_for_agg_state "$agg"
  local ser_before ser_after
  ser_before=$(serializer_drop_lines)
  local start_ft end_ft
  start_ft=$(( $(filetime_now) - MARGIN_FT ))
  # Windows must never overlap across phases: clamp to after the previous
  # phase's end so cross-phase rows cannot leak into this harvest.
  if [ "$start_ft" -le "$LAST_PHASE_END_FT" ]; then
    start_ft=$(( LAST_PHASE_END_FT + 1 ))
  fi
  run_workload "$phase"
  end_ft=$(( $(filetime_now) + MARGIN_FT ))
  LAST_PHASE_END_FT=$end_ft
  flush_boundary
  ser_after=$(serializer_drop_lines)
  if [ "$ser_after" -gt "$ser_before" ]; then
    log "WARNING: serializer backlog-drop warnings appeared during phase=$phase ($((ser_after - ser_before)) new lines) — run is INVALID (rows may be silently missing)"
    echo "$phase" >>"$RESULTS_DIR/invalid-phases.txt"
    PHASE_INVALID=1
  fi
  if ! harvest "$phase" "$start_ft" "$end_ft"; then
    log "ERROR: no $phase rows harvested within ${HARVEST_TIMEOUT}s"
    return 1
  fi
  log "phase $phase complete: $(cat "$RESULTS_DIR/$phase.rowcount") rows -> $RESULTS_DIR/$phase.parquet"
}

# ---------- main ----------

log "results dir: $RESULTS_DIR (data root: $DATA_ROOT)"
mkdir -p "$WORK_DIR"

HARVEST_FAIL=0
run_phase off false || HARVEST_FAIL=1
run_phase on true || HARVEST_FAIL=1

# cleanup trap already restored aggregation ON; verify state for the record.
if [ "$HARVEST_FAIL" -ne 0 ]; then
  {
    echo "VERDICT: NO-DATA (harvest failed; see phase logs above)"
    echo "Check: serializer backlog (invalid-phases.txt), parquet flush cadence,"
    echo "and whether the upload pipeline deletes parquet before harvest."
  } | tee "$RESULTS_DIR/summary.txt"
  exit 2
fi

log "running comparator"
"${PYRUN[@]}" "$COMPARATOR" \
  --baseline "$RESULTS_DIR/off.parquet" \
  --candidate "$RESULTS_DIR/on.parquet" \
  --ignore-pid --path-prefix "$WORK_DIR" \
  --fail-on-unmatched-relative \
  --json-out "$RESULTS_DIR/result.json" >"$RESULTS_DIR/comparator-stdout.json" 2>"$RESULTS_DIR/comparator-stderr.txt"
CMP_RC=$?

{
  echo "fop-11 A/B result — $(date -u +%FT%TZ)"
  echo "results dir: $RESULTS_DIR"
  echo "off rows: $(cat "$RESULTS_DIR/off.rowcount" 2>/dev/null || echo '?')  on rows: $(cat "$RESULTS_DIR/on.rowcount" 2>/dev/null || echo '?')"
  echo "comparator exit: $CMP_RC (0=pass, 1=fail, 2=vacuous)"
  if [ "$PHASE_INVALID" -ne 0 ]; then
    echo "SERIALIZER BACKLOG DURING RUN: yes — VERDICT: INVALID (fix fop-14 caps and rerun)"
  elif [ "$CMP_RC" -eq 0 ]; then
    echo "VERDICT: PASS"
  elif [ "$CMP_RC" -eq 2 ]; then
    echo "VERDICT: VACUOUS (no baseline population — see comparator-stderr.txt)"
  else
    echo "VERDICT: FAIL (see result.json missing/unmatched samples)"
  fi
  echo "key numbers (result.json): $(python3 -c "import json;d=json.load(open('$RESULTS_DIR/result.json'));print({k:d[k] for k in ('baseline_regular_tuples','candidate_regular_tuples','missing_regular_tuples','added_regular_tuples','matched_relative_tuples','unmatched_relative_tuples')})" 2>/dev/null || echo 'unavailable')"
} | tee "$RESULTS_DIR/summary.txt"

if [ "$PHASE_INVALID" -ne 0 ]; then exit 3; fi
exit "$CMP_RC"
