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
  ARGS+=(--dotnet-counters-command "$DOTNET_COUNTERS_COMMAND")
fi

if [[ -n "${LINTAP_DIAG_COMMAND:-}" ]]; then
  ARGS+=(--lintap-diag-command "$LINTAP_DIAG_COMMAND")
fi

cd "$PROJECT_DIR"
uv run --project . wpc-perf-batch "${ARGS[@]}"
