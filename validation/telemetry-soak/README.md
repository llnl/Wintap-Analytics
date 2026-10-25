# Non-interfering Linux telemetry canaries

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

Each round emits five separately named **canary** families:

| Manifest test | Stimulus / expected observations |
|---|---|
| `canary-cross-domain` | Named fork/exec/spawn/thread/file and IPv4 loopback TCP/UDP, including mmap/relative-path file operations |
| `canary-process` | Existing process-suite generator, six short-lived children, parent links, Start and Stop for every selected PID |
| `canary-file` | Eight distinct private files with Open/Read/Write/Close/Delete and distinct-path expectation |
| `canary-clone` | One optional prebuilt native helper round: fork/exec, worker-thread fork, pthread, clone/clone3 process and thread; PID/parent/Stop and negative thread checks |
| `canary-network-endpoints` | Assigned-host separate-process and same-process bidirectional TCP endpoints and process identities |

No local telemetry queries, collector starts/stops, sensor settings, diagnostic
tracer attachment, public-network contacts, package installs or pressure/loss tests.
These are small recurring **canaries**, not full dev-time acceptance. The process
generator's posix_spawn is best effort; unavailable Python execveat is an explicit
skip, not proof of syscall coverage. Native helper/kernel skips remain visible.
HOST startup receipts are not induced or renewed: full runtime-capability tests stay
dev-time/manual. Passive capability correlation is a follow-up, not current canary coverage.

The additional TCP stimuli use an assigned non-loopback host IPv4 address for
separate-process and same-process socket ends. Set `--host-ip` if automatic route
selection fails. Never substitute a NAT public address or relax firewall/security
policy for the runner. Optional `--clone-helper` selects an already-built native
helper; otherwise native clone-family coverage is explicitly skipped.
The runner still writes `named/process/file/clone/endpoints` entries in `status.tsv`;
the manifest identifiers above drive dashboard grouping. Skipped native stimulus is
reported as `skipped`, not `recorded`. Updating code does not expand a runner already
in progress: stop only the signal generator and launch a fresh one-round pilot when
ready; leave Lintap running. Keep prior private evidence.

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
  a passing DBT build is independent of this evidence. In Streamlit use **Canary
  Tests**, select a family/run and explicitly validate it. The Overview is manifest-only.
  Actual expanded-suite native/Garage validation remains an operator pilot check.

Configure Garage and host-isolated collection prefixes separately, using existing
approved configuration. Check disk/evidence accumulation periodically even on
disposable hosts. Open-ended runtime does not guarantee bounded total storage.

Lintap is the regular deployed service; run this signal generator completely
separately (for example in tmux). No service dependency or health-triggered restart
couples them. The only integration is writing evidence to the same data root for
the existing uploader and later SmokeTests dashboard discovery.

Each round records shared `canaryRoundId` metadata in all five manifests. On the
analysis machine, Canary Tests → **Run all validations for this canary** shows all
families/cases and compares them with passive HOST startup context. Summary results
are saved beside the local/S3 dataset, never under raw telemetry. Older expanded
manifests group using their shared `--manifest` round directory. See
`streamlit/projects/SmokeTests/README.md` for cache/stale-result and permission rules.

## Local orchestration checks

```bash
bash -n validation/telemetry-soak/run-smoke-soak.sh
python3 -m unittest discover -s validation/telemetry-soak -p 'test_*.py' -v
```

Tests mock Linux tools and stimulus modules. They exercise orchestration, failure
continuation, private evidence, lock refusal, export errors and deferred selectors;
they do not establish native timeout/signal, sensor, Garage or long-running behavior.
