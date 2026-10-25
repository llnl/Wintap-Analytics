# Periodic Linux telemetry stimuli

Run on disposable Linux hosts with an already-configured collector. This runner
does not start/stop services, configure Garage, handle credentials, fetch packages,
change permissions, or prune evidence. It is not a pressure test or capture oracle.

From the shared Wintap-PyUtil root (adjust sibling paths if necessary):

```bash
PYTHON=$(uv run --no-sync python -c 'import sys; print(sys.executable)')
DEVTOOLS=$(realpath ../wintap/devtools)
RUNNER=$(realpath ../Wintap-Analytics/validation/telemetry-soak/run-smoke-soak.sh)

# First run one bounded round and review status.tsv/manifests/logs.
sudo bash "$RUNNER" \
  --python "$PYTHON" --devtools "$DEVTOOLS" \
  --data-root /var/log/lintap/data \
  --evidence-root /var/log/lintap/runtime/smoke-soak \
  --rounds 1
```

After reviewing the pilot, omit `--rounds 1` to run indefinitely. Keep it in a
persistent terminal such as an existing tmux session; Ctrl-C stops only the runner.
No systemd unit or detached service is installed. The default 900-second interval
is a delay **after** each round, not a wall-clock schedule. Workloads run sequentially,
each bounded by GNU timeout (120 seconds plus 5-second kill grace). A nonblocking
flock excludes concurrent runners sharing the evidence root. Use one evidence root
per host; independently launched runners with different roots are not excluded.

Named stimuli cover fork/exec/spawn/thread/file and IPv4 loopback TCP/UDP cases.
The additional TCP stimuli use an assigned non-loopback host IPv4 address for
separate-process and same-process socket ends. Set `--host-ip` if automatic route
selection fails. Never substitute a NAT public address or relax firewall/security
policy for the runner. Optional `--clone-helper` selects an already-built native
helper; otherwise native clone-family coverage is explicitly skipped.

## Evidence and interpretation

- `--smoke-data-root` explicitly selects the collector's data root (the shared
  wrapper also understands **WINTAP_DATA_ROOT**, not WINTAP_DATA_PATH).
- Wrapper snapshots are published under
  `raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH/`. The existing collector
  uploader sweeps these parquet files like other raw data and may delete them
  locally after upload. The runner neither acknowledges nor retries delivery.
- Protected JSON, workload files, logs and `status.tsv` stay in unique session/round
  directories outside Git; nothing is automatically deleted. They contain real
  host/PID/path/port selectors: keep them private and never commit or paste unredacted.
- Failures do not terminate subsequent rounds. Exit 124/137 can indicate timeout;
  missing/incomplete manifests or export errors remain visible in `status.tsv`.
  `recorded` means local manifest completion, **not** confirmed S3 arrival.
- Success means stimuli were generated, not that sensor output was complete.
  Smoke manifests carry `stimulusOnly`/deferred-validation semantics. No local
  parquet validator runs, avoiding false negatives from successful upload deletion.
- Raw smoke parquet is compatible with the existing SmokeTests dashboard's evidence
  discovery on mounted/synced datasets or its configured read-only Garage/S3 source.
  **Current Wintappy DBT models do not ingest or validate smoke manifests**;
  a passing DBT build is independent of this evidence. Actual Garage dashboard
  validation remains an operator pilot check.

Configure Garage and host-isolated collection prefixes separately, using existing
approved configuration. Check disk/evidence accumulation periodically even on
disposable hosts. Open-ended runtime does not guarantee bounded total storage.

Lintap is the regular deployed service; run this signal generator completely
separately (for example in tmux). No service dependency or health-triggered restart
couples them. The only integration is writing evidence to the same data root for
the existing uploader and later SmokeTests dashboard discovery.

## Local orchestration checks

```bash
bash -n validation/telemetry-soak/run-smoke-soak.sh
python3 -m unittest discover -s validation/telemetry-soak -p 'test_*.py' -v
```

Tests mock Linux tools and stimulus modules. They exercise orchestration, failure
continuation, private evidence, lock refusal, export errors and deferred selectors;
they do not establish native timeout/signal, sensor, Garage or long-running behavior.
