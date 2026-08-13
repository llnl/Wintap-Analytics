#!/usr/bin/env bash
set -euo pipefail

# Long-running currentish-process validation profile.
# Defaults favor accurate live-process coverage over minimal sensor scope.

RUN_ID=${RUN_ID:-currentish-long-$(date +%s)}
DURATION_SECONDS=${DURATION_SECONDS:-21600}
INTERVAL_SECONDS=${INTERVAL_SECONDS:-5}
SHORT_PER_INTERVAL=${SHORT_PER_INTERVAL:-4}
LONG_PER_MINUTE=${LONG_PER_MINUTE:-1}
LONG_LIVED_SECONDS=${LONG_LIVED_SECONDS:-30}

# Validated sensor/profile defaults for currentish live-process accuracy.
PROCESS_RUNDOWN=${PROCESS_RUNDOWN:-true}
CLONE_SENSOR=${CLONE_SENSOR:-true}

# Less aggressive than the debug/short-run settings so late events still have headroom.
PROCESS_SWEEP_INTERVAL_SEC=${PROCESS_SWEEP_INTERVAL_SEC:-60}
PROCESS_EXIT_RETENTION_SEC=${PROCESS_EXIT_RETENTION_SEC:-3600}
PROCESS_RECONCILE_MIN_AGE_SEC=${PROCESS_RECONCILE_MIN_AGE_SEC:-30}

export RUN_ID
export DURATION_SECONDS
export INTERVAL_SECONDS
export SHORT_PER_INTERVAL
export LONG_PER_MINUTE
export LONG_LIVED_SECONDS
export PROCESS_RUNDOWN
export CLONE_SENSOR
export PROCESS_SWEEP_INTERVAL_SEC
export PROCESS_EXIT_RETENTION_SEC
export PROCESS_RECONCILE_MIN_AGE_SEC

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname "$0")" && pwd)
exec bash "$SCRIPT_DIR/run_lintap_noisy_state_test.sh"
