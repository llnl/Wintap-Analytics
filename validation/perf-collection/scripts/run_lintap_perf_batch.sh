#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo -E env "PATH=$PATH" bash "$0" "$@"
fi

DURATION_SECONDS="${DURATION_SECONDS:-300}"
INTERVAL_SECONDS="${INTERVAL_SECONDS:-5}"
PROCESS_NAME_SUBSTRING="${PROCESS_NAME_SUBSTRING:-Lintap}"
DATA_ROOT="${WINTAP_DATA_ROOT:-/tmp/lintap-perf}"
RUN_ID="${RUN_ID:-perf-$(date +%s)}"

ARGS=(
  --data-root "$DATA_ROOT"
  --process-name-substring "$PROCESS_NAME_SUBSTRING"
  --duration-seconds "$DURATION_SECONDS"
  --interval-seconds "$INTERVAL_SECONDS"
  --run-id "$RUN_ID"
)

if [[ -n "${DOTNET_COUNTERS_COMMAND:-}" ]]; then
  printf 'DOTNET_COUNTERS_COMMAND is no longer supported; use DOTNET_COUNTERS_FORMAT/DOTNET_COUNTERS_REFRESH_INTERVAL with capture_lintap_perf_for_user.sh or wpc-perf-batch\n' >&2
  exit 1
fi

if [[ -n "${DOTNET_COUNTERS_FORMAT:-}" ]]; then
  ARGS+=(--dotnet-counters-format "$DOTNET_COUNTERS_FORMAT")
fi

if [[ -n "${DOTNET_COUNTERS_BINARY:-}" ]]; then
  ARGS+=(--dotnet-counters-binary "$DOTNET_COUNTERS_BINARY")
fi

if [[ -n "${DOTNET_COUNTERS_REFRESH_INTERVAL:-}" ]]; then
  ARGS+=(--dotnet-counters-refresh-interval "$DOTNET_COUNTERS_REFRESH_INTERVAL")
fi

if [[ -n "${LINTAP_DIAG_COMMAND:-}" ]]; then
  ARGS+=(--lintap-diag-command "$LINTAP_DIAG_COMMAND")
fi

cd "$PROJECT_DIR"
uv run --project . wpc-perf-batch "${ARGS[@]}"
