#!/usr/bin/env bash
set -u
set -o pipefail

usage() {
  cat <<'USAGE'
Usage: collect-lintap-diagnostics.sh [options]

Read-only diagnostic collector for high-CPU long-running Lintap instances.

Options:
  --output-dir DIR   Directory where the diagnostic bundle directory is created
                     (default: /tmp)
  --data-root DIR    WINTAP_DATA_ROOT to inspect (default: parsed from
                     /etc/lintap/lintap.env, otherwise /var/log/lintap)
  --pid PID          Lintap process id (default: auto-detect /usr/lib/lintap/Lintap)
  --db PATH          DuckDB event_store path to inspect (default:
                     <data-root>/event_store/main.duckdb)
  --sample-seconds N Runtime sampling window for ps/top/pidstat/perf (default: 10)
  --no-tar          Leave the directory only; do not create a .tar.gz bundle
  -h, --help         Show this help

The script must usually run as root to read /var/log/lintap, /proc/<pid>,
and service journals. It never stops services and never writes to the Lintap
data root.
USAGE
}

OUTPUT_PARENT=/tmp
DATA_ROOT=""
DB_PATH_OVERRIDE=""
LINTAP_PID=""
SAMPLE_SECONDS=10
CREATE_TAR=1

while [ "$#" -gt 0 ]; do
  case "$1" in
    --output-dir)
      OUTPUT_PARENT=${2:-}
      shift 2
      ;;
    --data-root)
      DATA_ROOT=${2:-}
      shift 2
      ;;
    --pid)
      LINTAP_PID=${2:-}
      shift 2
      ;;
    --db)
      DB_PATH_OVERRIDE=${2:-}
      shift 2
      ;;
    --sample-seconds)
      SAMPLE_SECONDS=${2:-}
      shift 2
      ;;
    --no-tar)
      CREATE_TAR=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "$SAMPLE_SECONDS" =~ ^[0-9]+$ ]] || [ "$SAMPLE_SECONDS" -lt 1 ]; then
  printf 'ERROR: --sample-seconds must be a positive integer\n' >&2
  exit 2
fi

if [ "$(id -u)" -ne 0 ]; then
  printf 'WARNING: not running as root; some diagnostics will fail with permission denied.\n' >&2
fi

HOSTNAME_SAFE=$(hostname 2>/dev/null | tr -c 'A-Za-z0-9_.-' '_' | sed 's/_$//')
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUTDIR="${OUTPUT_PARENT%/}/lintap-runtime-diagnostics-${HOSTNAME_SAFE:-host}-${TIMESTAMP}"

mkdir -p "$OUTDIR" "$OUTDIR/commands" "$OUTDIR/config" "$OUTDIR/duckdb" "$OUTDIR/proc" "$OUTDIR/journal" "$OUTDIR/filesystem" "$OUTDIR/runtime"

log() {
  printf '[%s] %s\n' "$(date -u +%H:%M:%SZ)" "$*"
}

run_cmd() {
  local outfile=$1
  shift
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n\n'
    "$@"
  } >"$outfile" 2>&1 || true
}

run_shell() {
  local outfile=$1
  shift
  local command=$*
  {
    printf '$ %s\n\n' "$command"
    bash -c "$command"
  } >"$outfile" 2>&1 || true
}

have() {
  command -v "$1" >/dev/null 2>&1
}

resolve_duckdb() {
  local candidate
  if command -v duckdb >/dev/null 2>&1; then
    command -v duckdb
    return 0
  fi

  for candidate in \
    /usr/local/bin/duckdb \
    /usr/bin/duckdb \
    /opt/homebrew/bin/duckdb \
    "$HOME/.duckdb/cli/latest/duckdb" \
    /root/.duckdb/cli/latest/duckdb \
    /home/*/.duckdb/cli/latest/duckdb; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

write_requirements_report() {
  local report=$1
  shift
  local missing=0
  local command_name

  {
    printf 'Required commands:\n'
    for command_name in "$@"; do
      if have "$command_name"; then
        printf '  OK      %s -> %s\n' "$command_name" "$(command -v "$command_name")"
      else
        printf '  MISSING %s\n' "$command_name"
        missing=1
      fi
    done

    if [ -n "${DUCKDB_BIN:-}" ]; then
      printf '  OK      duckdb -> %s\n' "$DUCKDB_BIN"
      "$DUCKDB_BIN" --version 2>/dev/null | sed 's/^/          version: /' || true
    else
      printf '  MISSING duckdb\n'
      missing=1
    fi

    printf '\nOptional commands:\n'
    for command_name in pidstat perf dotnet dotnet-counters dotnet-trace dotnet-dump lsof hostnamectl; do
      if have "$command_name"; then
        printf '  OK      %s -> %s\n' "$command_name" "$(command -v "$command_name")"
      else
        printf '  MISSING %s\n' "$command_name"
      fi
    done
  } >"$report"

  return "$missing"
}

redact_file() {
  local src=$1
  local dst=$2
  if [ ! -r "$src" ]; then
    printf 'Not readable or missing: %s\n' "$src" >"$dst"
    return
  fi

  sed -E \
    -e 's/(AccessKey[[:space:]]*"?[[:space:]]*[:=][[:space:]]*"?)[^",[:space:]]+/\1<redacted>/Ig' \
    -e 's/(SecretKey[[:space:]]*"?[[:space:]]*[:=][[:space:]]*"?)[^",[:space:]]+/\1<redacted>/Ig' \
    -e 's/(SessionToken[[:space:]]*"?[[:space:]]*[:=][[:space:]]*"?)[^",[:space:]]+/\1<redacted>/Ig' \
    -e 's/(CloudflareAccessClient(Id|Secret)[[:space:]]*"?[[:space:]]*[:=][[:space:]]*"?)[^",[:space:]]+/\1<redacted>/Ig' \
    -e 's/(([A-Za-z0-9_]*(PASSWORD|PASSWD|SECRET|TOKEN|ACCESS_KEY|SECRET_KEY|PRIVATE_KEY)[A-Za-z0-9_]*)([[:space:]]*[:=][[:space:]]*"?))[^",[:space:]]+/\1<redacted>/Ig' \
    "$src" >"$dst" 2>&1 || true
}

parse_data_root() {
  if [ -n "$DATA_ROOT" ]; then
    printf '%s\n' "$DATA_ROOT"
    return
  fi

  if [ -r /etc/lintap/lintap.env ]; then
    awk -F= '/^[[:space:]]*WINTAP_DATA_ROOT[[:space:]]*=/ {gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); gsub(/^"|"$/, "", $2); print $2; exit}' /etc/lintap/lintap.env
    return
  fi

  printf '/var/log/lintap\n'
}

detect_lintap_pid() {
  if [ -n "$LINTAP_PID" ]; then
    printf '%s\n' "$LINTAP_PID"
    return
  fi

  pgrep -o -f '/usr/lib/lintap/Lintap|(^|/)Lintap( |$)' 2>/dev/null || true
}

DATA_ROOT=$(parse_data_root)
LINTAP_PID=$(detect_lintap_pid)
SOURCE_DB_PATH="${DB_PATH_OVERRIDE:-$DATA_ROOT/event_store/main.duckdb}"
DB_PATH="$SOURCE_DB_PATH"
DUCKDB_BIN="$(resolve_duckdb 2>/dev/null || true)"

cat >"$OUTDIR/manifest.txt" <<EOF
created_utc=$TIMESTAMP
hostname=$(hostname 2>/dev/null || true)
user=$(id 2>/dev/null || true)
data_root=$DATA_ROOT
source_db_path=$SOURCE_DB_PATH
db_path=$DB_PATH
lintap_pid=$LINTAP_PID
sample_seconds=$SAMPLE_SECONDS
EOF

log "Writing diagnostics to $OUTDIR"

REQUIRED_COMMANDS=(date hostname id mkdir pgrep ps systemctl journalctl ls du find sort tar sed awk grep tr cp timeout stat top vmstat free df bash)
if ! write_requirements_report "$OUTDIR/requirements.txt" "${REQUIRED_COMMANDS[@]}"; then
  log "ERROR: missing required diagnostic commands. See $OUTDIR/requirements.txt"
  printf '\nMissing required commands. See: %s\n' "$OUTDIR/requirements.txt" >&2
  exit 1
fi

log "Collecting host and service metadata"
run_cmd "$OUTDIR/commands/date.txt" date -u
run_cmd "$OUTDIR/commands/hostnamectl.txt" hostnamectl
run_cmd "$OUTDIR/commands/uname.txt" uname -a
run_cmd "$OUTDIR/commands/uptime.txt" uptime
run_cmd "$OUTDIR/commands/os-release.txt" sh -c 'cat /etc/os-release'
run_cmd "$OUTDIR/commands/cpuinfo-summary.txt" sh -c "lscpu 2>/dev/null || true; printf '\n/proc/cpuinfo processors: '; grep -c '^processor' /proc/cpuinfo 2>/dev/null || true"
run_cmd "$OUTDIR/commands/free.txt" free -h
run_cmd "$OUTDIR/commands/vmstat.txt" vmstat 1 5
run_cmd "$OUTDIR/commands/df.txt" df -hT "$DATA_ROOT" /tmp / 2>/dev/null
run_cmd "$OUTDIR/commands/ulimit.txt" sh -c 'ulimit -a'
run_cmd "$OUTDIR/commands/dotnet-info.txt" dotnet --info

run_cmd "$OUTDIR/commands/systemctl-status-lintap.txt" systemctl status lintap --no-pager
run_cmd "$OUTDIR/commands/systemctl-status-lintap-pidstat.txt" systemctl status lintap-pidstat --no-pager
run_cmd "$OUTDIR/commands/systemctl-cat-lintap.txt" systemctl cat lintap --no-pager
run_cmd "$OUTDIR/commands/systemctl-cat-lintap-pidstat.txt" systemctl cat lintap-pidstat --no-pager

redact_file /etc/lintap/lintap.env "$OUTDIR/config/etc-lintap-lintap.env.redacted"
redact_file /usr/lib/lintap/ETLConfig.json "$OUTDIR/config/usr-lib-lintap-ETLConfig.json.redacted"
redact_file "$DATA_ROOT/ETLConfig.json" "$OUTDIR/config/data-root-ETLConfig.json.redacted"

log "Collecting process/runtime samples"
run_cmd "$OUTDIR/runtime/pgrep-lintap-pidstat.txt" pgrep -af 'Lintap|Wintap|pidstat'
run_cmd "$OUTDIR/runtime/ps-key-processes.txt" ps -C Lintap -C dotnet -C pidstat -C python3 -o pid,ppid,etimes,%cpu,%mem,rss,vsz,nlwp,stat,comm,args --sort=-%cpu
run_cmd "$OUTDIR/runtime/ps-all-top-cpu.txt" sh -c 'ps -eo pid,ppid,etimes,%cpu,%mem,rss,vsz,nlwp,stat,comm,args --sort=-%cpu | head -80'

if [ -n "$LINTAP_PID" ] && [ -d "/proc/$LINTAP_PID" ]; then
  run_cmd "$OUTDIR/runtime/ps-lintap-threads.txt" ps -L -p "$LINTAP_PID" -o pid,tid,psr,etimes,%cpu,%mem,stat,comm --sort=-%cpu
  run_cmd "$OUTDIR/runtime/top-lintap-threads.txt" top -b -H -p "$LINTAP_PID" -n 3 -d 2
  run_cmd "$OUTDIR/runtime/pmap-lintap.txt" pmap -x "$LINTAP_PID"

  for proc_file in status stat statm sched schedstat io limits cgroup smaps_rollup numastat; do
    if [ -r "/proc/$LINTAP_PID/$proc_file" ]; then
      cp "/proc/$LINTAP_PID/$proc_file" "$OUTDIR/proc/lintap-$proc_file" 2>/dev/null || true
    fi
  done

  if [ -r "/proc/$LINTAP_PID/environ" ]; then
    tr '\0' '\n' <"/proc/$LINTAP_PID/environ" \
      | sed -E 's/^([^=]*(PASSWORD|PASSWD|SECRET|TOKEN|ACCESS_KEY|SECRET_KEY|PRIVATE_KEY)[^=]*=).*/\1<redacted>/Ig' \
      >"$OUTDIR/proc/lintap-environ.redacted" 2>&1 || true
  fi

  run_cmd "$OUTDIR/proc/lintap-fd-list.txt" ls -l "/proc/$LINTAP_PID/fd"
  if have lsof; then
    run_cmd "$OUTDIR/proc/lintap-lsof.txt" lsof -p "$LINTAP_PID"
  fi
  if have pidstat; then
    run_cmd "$OUTDIR/runtime/pidstat-lintap-thread.txt" pidstat -t -p "$LINTAP_PID" 1 "$SAMPLE_SECONDS"
  fi
  if have perf; then
    run_cmd "$OUTDIR/runtime/perf-stat-lintap.txt" perf stat -p "$LINTAP_PID" sleep "$SAMPLE_SECONDS"
  fi
  if have dotnet-counters; then
    run_cmd "$OUTDIR/runtime/dotnet-counters-system-runtime.txt" timeout "$((SAMPLE_SECONDS + 5))" dotnet-counters monitor --process-id "$LINTAP_PID" System.Runtime
  fi
  if have dotnet-trace; then
    run_cmd "$OUTDIR/runtime/dotnet-trace-ps.txt" dotnet-trace ps
  fi
  if have dotnet-dump; then
    run_cmd "$OUTDIR/runtime/dotnet-dump-ps.txt" dotnet-dump ps
  fi
fi

run_shell "$OUTDIR/runtime/fork-rate.txt" 'p1=; p2=; while read -r key val rest; do if [ "$key" = processes ]; then p1=$val; fi; done < /proc/stat; sleep 10; while read -r key val rest; do if [ "$key" = processes ]; then p2=$val; fi; done < /proc/stat; printf "processes_delta_10s=%s\nprocesses_per_sec=%s\n" "$((p2-p1))" "$(((p2-p1)/10))"'

log "Collecting journals and local logs"
run_cmd "$OUTDIR/journal/lintap-last-2h.txt" journalctl -u lintap --since '-2 hours' --no-pager
run_cmd "$OUTDIR/journal/lintap-warnings-last-24h.txt" journalctl -u lintap --since '-24 hours' -p warning --no-pager
run_cmd "$OUTDIR/journal/lintap-pidstat-last-2h.txt" journalctl -u lintap-pidstat --since '-2 hours' --no-pager
run_cmd "$OUTDIR/journal/lintap-boot-summary.txt" journalctl -u lintap -b --no-pager -n 400
run_cmd "$OUTDIR/filesystem/data-root-list.txt" ls -lah "$DATA_ROOT"
run_cmd "$OUTDIR/filesystem/data-root-du.txt" du -h -d 4 "$DATA_ROOT"
run_shell "$OUTDIR/filesystem/parquet-counts.txt" "find '$DATA_ROOT' -type f \\( -name '*.parquet' -o -name '*.parquet.active' \\) -printf '%h\n' 2>/dev/null | sort | uniq -c | sort -nr | head -100"
run_shell "$OUTDIR/filesystem/recent-files.txt" "find '$DATA_ROOT' -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %s %p\n' 2>/dev/null | sort -r | head -200"

log "Collecting DuckDB event_store diagnostics"
if [ -r "$SOURCE_DB_PATH" ]; then
  run_cmd "$OUTDIR/duckdb/db-file-stat.txt" stat "$SOURCE_DB_PATH"
  run_cmd "$OUTDIR/duckdb/db-dir-list.txt" ls -lah "$(dirname "$SOURCE_DB_PATH")"
else
  printf 'DuckDB path is not readable: %s\n' "$SOURCE_DB_PATH" >"$OUTDIR/duckdb/README-missing-db.txt"
fi

prepare_duckdb_path() {
  local probe_out="$OUTDIR/duckdb/live-lock-probe.out"
  if [ -z "${DUCKDB_BIN:-}" ]; then
    printf 'duckdb CLI not found\n' >"$probe_out"
    return
  fi
  if [ ! -r "$SOURCE_DB_PATH" ]; then
    printf 'DuckDB path is not readable: %s\n' "$SOURCE_DB_PATH" >"$probe_out"
    return
  fi

  {
    printf '$ %q -readonly %q -c "PRAGMA database_size;"\n\n' "$DUCKDB_BIN" "$SOURCE_DB_PATH"
    timeout 30 "$DUCKDB_BIN" -readonly "$SOURCE_DB_PATH" -c "PRAGMA database_size;"
  } >"$probe_out" 2>&1
  local status=$?

  if [ "$status" -eq 0 ]; then
    DB_PATH="$SOURCE_DB_PATH"
    printf 'mode=live-readonly\nsource=%s\nquery_path=%s\n' "$SOURCE_DB_PATH" "$DB_PATH" >"$OUTDIR/duckdb/db-query-source.txt"
    return
  fi

  if ! grep -qi 'conflicting lock\|could not set lock\|lock is held' "$probe_out"; then
    DB_PATH="$SOURCE_DB_PATH"
    printf 'mode=live-readonly-failed-nonlock\nsource=%s\nquery_path=%s\n' "$SOURCE_DB_PATH" "$DB_PATH" >"$OUTDIR/duckdb/db-query-source.txt"
    return
  fi

  local snapshot_dir="$OUTDIR/duckdb/snapshot"
  local snapshot_db="$snapshot_dir/main.duckdb"
  mkdir -p "$snapshot_dir"
  log "DuckDB is locked by the running service; copying DB snapshot for read-only queries"
  cp -p "$SOURCE_DB_PATH" "$snapshot_db" 2>"$OUTDIR/duckdb/snapshot-copy.err" || true
  if [ -r "$SOURCE_DB_PATH.wal" ]; then
    cp -p "$SOURCE_DB_PATH.wal" "$snapshot_db.wal" 2>>"$OUTDIR/duckdb/snapshot-copy.err" || true
  fi

  if [ -r "$snapshot_db" ]; then
    DB_PATH="$snapshot_db"
    printf 'mode=snapshot-after-lock\nsource=%s\nquery_path=%s\nwal_copied=%s\n' "$SOURCE_DB_PATH" "$DB_PATH" "$([ -r "$snapshot_db.wal" ] && printf yes || printf no)" >"$OUTDIR/duckdb/db-query-source.txt"
  else
    DB_PATH="$SOURCE_DB_PATH"
    printf 'mode=snapshot-copy-failed\nsource=%s\nquery_path=%s\n' "$SOURCE_DB_PATH" "$DB_PATH" >"$OUTDIR/duckdb/db-query-source.txt"
  fi
}

prepare_duckdb_path

cat >>"$OUTDIR/manifest.txt" <<EOF
duckdb_bin=${DUCKDB_BIN:-missing}
duckdb_query_path=$DB_PATH
EOF

run_duckdb_sql() {
  local name=$1
  local sql=$2
  local sql_file="$OUTDIR/duckdb/$name.sql"
  local out_file="$OUTDIR/duckdb/$name.out"
  printf '%s\n' "$sql" >"$sql_file"
  if [ -z "${DUCKDB_BIN:-}" ]; then
    printf 'duckdb CLI not found\n' >"$out_file"
    return
  fi
  if [ ! -r "$DB_PATH" ]; then
    printf 'DuckDB path is not readable: %s\n' "$DB_PATH" >"$out_file"
    return
  fi
  {
    printf '$ %q -readonly %q < %q\n\n' "$DUCKDB_BIN" "$DB_PATH" "$sql_file"
    timeout 120 "$DUCKDB_BIN" -readonly "$DB_PATH" <"$sql_file"
  } >"$out_file" 2>&1 || true
}

run_duckdb_sql database-size "PRAGMA database_size;"

run_duckdb_sql schema "
.mode markdown
SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' ORDER BY table_name;
SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = 'main' ORDER BY table_name, ordinal_position;
SELECT * FROM duckdb_indexes() WHERE schema_name = 'main' ORDER BY table_name, index_name;
"

run_duckdb_sql process-summary "
.mode markdown
SELECT
  count(*) AS process_rows,
  count(DISTINCT process_id) AS distinct_pids,
  count(DISTINCT pid_hash) AS distinct_pid_hashes,
  count(*) FILTER (WHERE exit_time IS NULL) AS open_rows,
  count(*) FILTER (WHERE exit_time IS NOT NULL) AS closed_rows,
  min(create_time) AS min_create_time,
  max(create_time) AS max_create_time,
  min(exit_time) AS min_exit_time,
  max(exit_time) AS max_exit_time
FROM process;

SELECT
  source,
  count(*) AS rows,
  count(*) FILTER (WHERE exit_time IS NULL) AS open_rows,
  count(*) FILTER (WHERE exit_time IS NOT NULL) AS closed_rows
FROM process
GROUP BY source
ORDER BY rows DESC;
"

run_duckdb_sql process-age-buckets "
.mode markdown
WITH rows AS (
  SELECT
    CASE
      WHEN create_time >= now() - INTERVAL 1 HOUR THEN '<1h'
      WHEN create_time >= now() - INTERVAL 6 HOUR THEN '1-6h'
      WHEN create_time >= now() - INTERVAL 24 HOUR THEN '6-24h'
      WHEN create_time >= now() - INTERVAL 3 DAY THEN '1-3d'
      WHEN create_time >= now() - INTERVAL 7 DAY THEN '3-7d'
      ELSE '>=7d'
    END AS create_age_bucket,
    exit_time IS NULL AS is_open
  FROM process
)
SELECT create_age_bucket, is_open, count(*) AS rows
FROM rows
GROUP BY create_age_bucket, is_open
ORDER BY create_age_bucket, is_open;
"

run_duckdb_sql top-process-names "
.mode markdown
SELECT process_name, count(*) AS rows, count(*) FILTER (WHERE exit_time IS NULL) AS open_rows
FROM process
GROUP BY process_name
ORDER BY rows DESC
LIMIT 50;

SELECT process_name, count(*) AS open_rows, min(create_time) AS oldest_open, max(create_time) AS newest_open
FROM process
WHERE exit_time IS NULL
GROUP BY process_name
ORDER BY open_rows DESC
LIMIT 50;
"

run_duckdb_sql open-row-samples "
.mode markdown
SELECT pid_hash, process_id, parent_process_id, process_name, create_time, source
FROM process
WHERE exit_time IS NULL
ORDER BY create_time ASC
LIMIT 100;

SELECT pid_hash, process_id, parent_process_id, process_name, create_time, exit_time, source
FROM process
ORDER BY create_time DESC
LIMIT 100;
"

run_duckdb_sql telemetry-summary "
.mode markdown
SELECT metric_name, count(*) AS rows, sum(metric_value) AS total, min(observed_at) AS first_seen, max(observed_at) AS last_seen
FROM process_retention_telemetry
GROUP BY metric_name
ORDER BY metric_name;

SELECT metric_name, process_name, count(*) AS rows, sum(metric_value) AS total
FROM process_retention_telemetry
GROUP BY metric_name, process_name
ORDER BY total DESC
LIMIT 100;
"

run_duckdb_sql pidhash-lookup-explain "
.mode markdown
EXPLAIN ANALYZE
WITH sample AS (
  SELECT process_id, create_time AS event_time
  FROM process
  WHERE process_id > 0
  ORDER BY create_time DESC
  LIMIT 1
)
SELECT p.pid_hash
FROM process p, sample s
WHERE p.process_id = s.process_id
  AND p.create_time <= s.event_time
  AND (p.exit_time IS NULL OR p.exit_time >= s.event_time)
ORDER BY p.create_time DESC
LIMIT 1;

EXPLAIN ANALYZE
WITH sample AS (
  SELECT process_id, create_time AS event_time
  FROM process
  WHERE process_id > 0
  ORDER BY random()
  LIMIT 100
)
SELECT count(*)
FROM sample s
JOIN process p
  ON p.process_id = s.process_id
 AND p.create_time <= s.event_time
 AND (p.exit_time IS NULL OR p.exit_time >= s.event_time);
"

run_duckdb_sql event-table-counts "
.mode markdown
SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' ORDER BY table_name;
SELECT 'process' AS table_name, count(*) AS rows FROM process
UNION ALL
SELECT 'process_retention_telemetry' AS table_name, count(*) AS rows FROM process_retention_telemetry;
"

log "Creating summary"
cat >"$OUTDIR/SUMMARY.txt" <<EOF
Lintap runtime diagnostics collected at $TIMESTAMP UTC

Key files to inspect first:
  manifest.txt
  runtime/ps-key-processes.txt
  runtime/ps-lintap-threads.txt
  runtime/top-lintap-threads.txt
  runtime/fork-rate.txt
  duckdb/process-summary.out
  duckdb/telemetry-summary.out
  duckdb/schema.out
  duckdb/pidhash-lookup-explain.out
  journal/lintap-warnings-last-24h.txt

Notes:
  - Config files are redacted for common secret-like keys.
  - The live DuckDB database is queried read-only when possible. If it is locked,
    the script copies main.duckdb plus main.duckdb.wal (when present) under
    duckdb/snapshot/ and queries the copy.
  - Some optional outputs depend on installed tools: pidstat, perf,
    dotnet-counters, dotnet-trace, dotnet-dump, lsof.
EOF

if [ "$CREATE_TAR" -eq 1 ]; then
  TAR_PATH="$OUTDIR.tar.gz"
  log "Creating bundle $TAR_PATH"
  tar -C "$(dirname "$OUTDIR")" -czf "$TAR_PATH" "$(basename "$OUTDIR")"
  printf '%s\n' "$TAR_PATH" >"$OUTDIR/BUNDLE_PATH.txt"
  log "Done: $TAR_PATH"
  printf '\nDiagnostic bundle: %s\n' "$TAR_PATH"
else
  log "Done: $OUTDIR"
  printf '\nDiagnostic directory: %s\n' "$OUTDIR"
fi
