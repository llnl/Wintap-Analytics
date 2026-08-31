#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

discover_pid_by_substring() {
  local needle="$1"
  local needle_lower="${needle,,}"
  local comm_path=""
  local comm_name=""
  local pid=""
  local matches=()

  for comm_path in /proc/[0-9]*/comm; do
    [[ -r "$comm_path" ]] || continue
    if ! IFS= read -r comm_name < "$comm_path"; then
      continue
    fi
    if [[ "${comm_name,,}" == *"$needle_lower"* ]]; then
      pid="${comm_path#/proc/}"
      pid="${pid%/comm}"
      matches+=("$pid")
    fi
  done

  if [[ "${#matches[@]}" -eq 0 ]]; then
    printf 'No process matched substring: %s\n' "$needle" >&2
    return 1
  fi

  printf '%s\n' "${matches[-1]}"
}

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo -E env "PATH=$PATH" bash "$0" "$@"
fi

umask 022

DURATION_SECONDS="${DURATION_SECONDS:-300}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-5}"
DOTNET_COUNTERS_REFRESH_INTERVAL="${DOTNET_COUNTERS_REFRESH_INTERVAL:-5}"
DOTNET_COUNTERS_FORMAT="${DOTNET_COUNTERS_FORMAT:-json}"
PROCESS_NAME_SUBSTRING="${PROCESS_NAME_SUBSTRING:-Lintap}"
DATA_ROOT="${WINTAP_DATA_ROOT:-/tmp/lintap-perf}"
RUN_ID="${RUN_ID:-perf-$(date +%s)}"
ENABLE_DOTNET_COUNTERS="${ENABLE_DOTNET_COUNTERS:-1}"

OWNER_USER="${OWNER_USER:-${SUDO_USER:-}}"
OWNER_UID="${OWNER_UID:-${SUDO_UID:-}}"
OWNER_GID="${OWNER_GID:-${SUDO_GID:-}}"

PID="${PID:-}"
if [[ -z "$PID" ]]; then
  PID="$(discover_pid_by_substring "$PROCESS_NAME_SUBSTRING")"
fi

DOTNET_COUNTERS_BINARY="${DOTNET_COUNTERS_BINARY:-dotnet-counters}"
if [[ "$ENABLE_DOTNET_COUNTERS" == "1" ]] && ! command -v "$DOTNET_COUNTERS_BINARY" >/dev/null 2>&1; then
  printf '%s not found on PATH; skipping dotnet-counters collect\n' "$DOTNET_COUNTERS_BINARY" >&2
  ENABLE_DOTNET_COUNTERS=0
fi

mkdir -p "$DATA_ROOT"

ARGS=(
  --data-root "$DATA_ROOT"
  --pid "$PID"
  --duration-seconds "$DURATION_SECONDS"
  --interval-seconds "$INTERVAL_SECONDS"
  --run-id "$RUN_ID"
)

if [[ "$ENABLE_DOTNET_COUNTERS" == "1" ]]; then
  ARGS+=(
    --dotnet-counters-format "$DOTNET_COUNTERS_FORMAT"
    --dotnet-counters-binary "$DOTNET_COUNTERS_BINARY"
    --dotnet-counters-refresh-interval "$DOTNET_COUNTERS_REFRESH_INTERVAL"
  )
fi

if [[ -n "${LINTAP_DIAG_COMMAND:-}" ]]; then
  ARGS+=(--lintap-diag-command "$LINTAP_DIAG_COMMAND")
fi

cd "$PROJECT_DIR"
uv run --project . wpc-perf-batch "${ARGS[@]}"

if [[ -n "$OWNER_UID" && -n "$OWNER_GID" ]]; then
  chown -R "$OWNER_UID:$OWNER_GID" "$DATA_ROOT"
  if [[ -n "$OWNER_USER" ]]; then
    printf 'Returned ownership of %s to %s (%s:%s)\n' "$DATA_ROOT" "$OWNER_USER" "$OWNER_UID" "$OWNER_GID"
  else
    printf 'Returned ownership of %s to %s:%s\n' "$DATA_ROOT" "$OWNER_UID" "$OWNER_GID"
  fi
else
  printf 'Capture complete under %s; no invoking user metadata was available for chown\n' "$DATA_ROOT"
fi
