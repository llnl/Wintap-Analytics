---
title: "Named Linux telemetry smoke workload"
type: tool
confidence: high
grounded_by:
  - ../wintap/devtools/telemetry_smoke_workload.py
  - ../wintap/devtools/smoke_manifest.py
  - ../wintap/devtools/smoke_parquet.py
  - ../wintap/devtools/README.md
  - ../wintap/devtools/clone_lifecycle_workload.c
  - ../wintap/devtools/test_telemetry_smoke_workload.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/wintap/core/etl/load/CacheManager.cs
  - ../Lintap/packaging/PATHS_AND_CONFIGURATION.md
  - validation/telemetry-soak/README.md
  - streamlit/projects/SmokeTests/README.md
  - streamlit/projects/SmokeTests/requirements.txt
  - streamlit/projects/SmokeTests/main.py
  - streamlit/projects/SmokeTests/page_views.py
  - https://docs.astral.sh/uv/pip/environments/
policy: agent-editable
last_validated: 2026-10-30
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/devtools; streamlit/projects/SmokeTests; validation/telemetry-soak; ../Lintap/packaging
tags: [smoke-test, linux, process, file, network, field-validation, sudo, s3, raw_smoke_test]
---

# Named Linux telemetry smoke workload

`../wintap/devtools/telemetry_smoke_workload.py` generates named process/file/network
activity for an **already-running** Linux collector. The workload itself uses the
Python standard library and loopback sockets. **Automatic S3 evidence needs Python
DuckDB and write access to the collector data root; on root-owned field systems,
run the workload with `sudo` using an explicitly selected Python interpreter.**
Wintap owns the workload, evidence publisher and uploader; Analytics owns the
dashboard and this operator procedure; Lintap supplies packaging/path conventions.

Visual overview: [[wiki/workflow/live-collector-validation]] — two-page editable
draw.io diagram of the data/evidence paths and root-owned operator workflow.

## Root-owned field host: workload → raw_smoke_test → S3 → validation

The remembered mechanism is **write smoke evidence locally, then let the existing
collector uploader carry it alongside telemetry**. The workload does not upload to
S3 itself. Keep the collector running throughout generation and normal delivery.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_parquet.py §publish; ../wintap/wintap/core/etl/load/CacheManager.cs §WorkerThread_DoWork, upload -->

### 1. Confirm the collector's actual data root

On the Linux collection host:

```bash
sudo grep -E '^(WINTAP_DATA_ROOT|WINTAP_RUNTIME_ROOT)=' /etc/lintap/lintap.env
sudo journalctl -u lintap -b --no-pager | grep -E 'Data root|Runtime root|Esper staging path'
```

The packaged default is `/var/log/lintap/data`; use the resolved startup path if
the deployment overrides it. Confirm collector startup/sensor attachment has
completed before generating activity. The service's environment file is not
automatically loaded into an interactive shell.
<!-- GROUND_TRUTH: ../Lintap/packaging/PATHS_AND_CONFIGURATION.md §Default layout, Verify an installation; streamlit/projects/SmokeTests/README.md §Collection host and analysis host can differ -->

| Argument | Meaning | Example |
|---|---|---|
| `--smoke-data-root` | Local collector directory **containing** `raw_sensor`; uploader watches this tree | `/var/log/lintap/data` |
| `--output` | Fresh workload directory, outside collector data/runtime roots and configured filtered paths | `$HOME/qa/wintap-smoke/<run>` |
| `--manifest` | Fresh portable JSON backup, retained locally outside the uploaded tree | `$HOME/qa/wintap-smoke/manifests/<run>.json` |

Do not append `raw_sensor` to `--smoke-data-root`: the publisher appends
`raw_sensor/raw_smoke_test` itself. It takes a filesystem path, not an `s3://` URL.
Use a home-directory QA path for stimulus rather than assuming `/tmp` is captured;
check the deployed filters. The data-root exclusion applies even when running as root.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_parquet.py §publish; ../wintap/devtools/telemetry_smoke_workload.py §main; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent -->

### 2. Create a persistent Python environment, then invoke it as root

From the **Wintap checkout on the collection host**, in your normal login shell:

```bash
WINTAP_REPO=$(pwd -P)
DATA_ROOT=/var/log/lintap/data  # Replace with this collector's resolved data root.
QA_ROOT="$HOME/qa/wintap-smoke"

# One-time setup in a dedicated, persistent environment.
VENV="$HOME/.local/share/wintap-smoke/venv"
uv venv --no-project --python 3.11 "$VENV"
uv pip install --python "$VENV/bin/python" duckdb==1.5.6
PYTHON="$VENV/bin/python"

# Check that the same environment works through sudo before generating a run.
sudo "$PYTHON" -c 'import os, sys, duckdb; print("uid", os.geteuid(), "python", sys.executable, "duckdb", duckdb.__version__)'
```

Expect `uid 0` and `duckdb 1.5.6`. Proceed after environment creation, package
installation and the sudo import check succeed. For later sessions, reuse the
environment by setting `PYTHON="$HOME/.local/share/wintap-smoke/venv/bin/python"`;
the setup commands are one-time. `uv` installs dependencies as the login user;
`sudo` runs the persistent environment's absolute interpreter path. This works
when root has neither `uv` on PATH nor DuckDB in system Python.
Python 3.11 selects a modern interpreter on older distro installations, and the
DuckDB pin matches the current dashboard/soak tooling. Keep the `venv/bin/python`
path: resolving its symlink to the base Python can lose the installed DuckDB package.
The soak runner can reuse this same persistent `PYTHON` path.
<!-- GROUND_TRUTH: https://docs.astral.sh/uv/pip/environments/ §Creating a virtual environment, Using arbitrary Python environments; streamlit/projects/SmokeTests/requirements.txt -->

**Correction to the earlier recipe:** do not save `sys.executable` from
`uv run --no-project --with ...` for a later sudo invocation. The operator's
2026-10-30 attempt returned a `.../.cache/uv/builds-v0/.tmp.../bin/python` path that
sudo could no longer execute after `uv run` exited. That temporary environment is
not a persistent interpreter handoff. The existing soak README's
`uv run --no-sync python ...` example assumes a persistent project environment;
adding `--with`/`--no-project` does not preserve that assumption.
<!-- SYNTHESIS: operator-reported 2026-10-30 command-not-found result; validation/telemetry-soak/README.md §Generation; https://docs.astral.sh/uv/pip/environments/ -->

Then run one named workload:

```bash
RUN_ID="smoke-$(hostname -s)-$(date -u +%Y%m%dT%H%M%SZ)"
sudo "$PYTHON" "$WINTAP_REPO/devtools/telemetry_smoke_workload.py" \
  --output "$QA_ROOT/$RUN_ID" \
  --manifest "$QA_ROOT/manifests/$RUN_ID.json" \
  --smoke-data-root "$DATA_ROOT"
```

The workload creates its output directory; do not precreate that directory. Use a
fresh run name/manifest for each invocation. The explicit root argument survives
sudo's environment filtering; relying on a user-shell `WINTAP_DATA_ROOT` does not.
`WINTAP_DATA_PATH` is not supported by the smoke wrapper. Local results are created
by root and can be inspected with `sudo cat "$QA_ROOT/manifests/$RUN_ID.json"`.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §smoke_run; ../wintap/devtools/telemetry_smoke_workload.py §main -->

### 3. Check publication, then delivery

Look for all three types of console output:

- `generated ...`: each OS stimulus completed; omitted native helper is an explicit skip.
- `Smoke parquet: .../raw_sensor/raw_smoke_test/...parquet`: a local evidence snapshot
  was published. Normal completion produces start, first-selectors and final revisions
  sharing a portable run UUID.
- `Smoke manifest: ...json`: the retained portable JSON backup.

The published layout is:

```text
<data-root>/raw_sensor/raw_smoke_test/dayPK=YYYYMMDD/hourPK=HH/
  <host>+raw_smoke_test+<run-uuid>+<revision>+<hash>.parquet
```

Partitions use UTC **publication** time. Each parquet snapshot includes the full
portable manifest, so the dashboard can discover the run automatically. Existing
S3 credentials/configuration belong to the collector uploader; the smoke command
only needs local write access. Wait for the configured upload cycle and refresh
the S3 dashboard. Successful upload can delete the local parquet, so an empty local
directory alone is not evidence of export failure or proof of S3 arrival.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §_publish, smoke_run; ../wintap/devtools/smoke_parquet.py §publish; ../wintap/wintap/core/etl/load/CacheManager.cs §upload -->

**An export warning is important even if every case says `generated` and exit is
zero.** The wrapper retains JSON and records `durableExportError` when DuckDB import
or filesystem publication fails; it does not turn that into an OS workload failure.
<!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §_publish -->

### 4. Validate the delivered run on the analysis machine

**First launch?** Follow the dashboard's
[Configure and launch against S3](smoke-test-results-dashboard.md#configure-and-launch-against-s3)
quick start to create `garage.json`, select credentials and open Streamlit.

From **Wintap-Analytics**, with your existing private S3 dashboard configuration:

```bash
export WINTAP_SMOKE_CONFIG="$HOME/.config/wintap-smoke/garage.json"
uv run --no-project \
  --with-requirements streamlit/projects/SmokeTests/requirements.txt \
  python -m streamlit run streamlit/projects/SmokeTests/main.py \
  --server.address 127.0.0.1
```

The config's dataset root must contain the uploaded `raw_sensor` tree. Use the
analysis machine's existing AWS profile/environment credentials. See
[[wiki/tool/smoke-test-results-dashboard]] and
`streamlit/projects/SmokeTests/README.md` for first-time S3 configuration.

1. Include the run's UTC publication/collection days in the sidebar partition window
   (include adjacent days around midnight or delayed telemetry publication).
2. Click **Refresh files / results**. The `raw_smoke_test` parquet supplies the manifest;
   select the test host and **Canary Tests**.
3. Select the `telemetry-workload` family and the correct host/time/run UUID; click
   **Validate selected run**. Overview alone does not scan telemetry.
4. Inspect per-case expected activities, matching rows, identity/endpoint checks and
   missing/skipped observations. Stimulus-only success/native skips may keep the
   overall result yellow; generation and S3 arrival do not certify capture.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/main.py §main; streamlit/projects/SmokeTests/page_views.py §is_canary, test_page; streamlit/projects/SmokeTests/README.md §Read directly from Garage / S3 -->

### Troubleshooting the handoffs

| Symptom | Check / next action |
|---|---|
| `sudo: uv: command not found` | Create the persistent venv using user-side uv, then `sudo "$VENV/bin/python" ...`. |
| `sudo: .../.cache/uv/builds-v0/.tmp.../bin/python: command not found` | The earlier temporary-interpreter recipe failed before the workload launched. Create the persistent venv above and set `PYTHON` to its `bin/python`. |
| `No module named duckdb` under sudo | Run the import check with the exact printed interpreter; system `sudo python3` may select a different environment. |
| Interpreter/source inaccessible to root | Check the actual path and mount permissions (including root-squashed home mounts); use an executable local environment/checkout accessible to root. |
| Only JSON output, no `Smoke parquet:` and no export warning | Supply `--smoke-data-root` explicitly; check for `--no-smoke-parquet`. |
| `WARNING: smoke parquet export failed` | Inspect the error and JSON `durableExportError`; confirm the actual root and filesystem access, then use a fresh run. |
| Local publication but no run on S3 | Check collector upload logs, destination prefix and dashboard UTC window; local publication is not a delivery acknowledgement. |
| Run appears but no matching telemetry | Allow normal ETL/merge/upload, then verify host/time selectors, sensor startup/capabilities and stimulus path filters. |
| Required case failed / supplied clone helper broken | Inspect the manifest's failed case; this produces exit 1. |

Commands above were reviewed against current source on 2026-10-30. A new root-run
field-host/S3 result is not recorded by this documentation update.

## Workload-only quick start

When only local stimulus/JSON is needed, root and DuckDB are unnecessary if the
output paths are writable. All commands below are from the Wintap repo.

```bash
python3 devtools/telemetry_smoke_workload.py --output /home/user/qa/smoke-001
```

Use a fresh directory **outside** collector data/runtime roots and configured
filtered paths. Existing directories are refused. Files are removed as part
of their lifecycle; the manifest and evidence remain for analysis.

## Coverage and selectors

| Domain | Stimulus | Collected-data expectation / caveat |
|---|---|---|
| Process | Named `wt_fork`, `wt_forkexec`, `wt_spawn`, `wt_threads` and child/image names | Start/Stop; fork-only requires Clone; threads must not appear as process Starts. posix_spawn implementation is libc-dependent |
| Native optional | One round of fork/exec, worker-thread fork, pthread, legacy clone process/thread, clone3 process/thread, explicit vfork+exec | Pass compiled clone helper; missing helper is SKIP, unavailable clone3 records errno. vfork child only calls exec/_exit before image replacement |
| File | `wt_file`: create/open/write/read/file-backed mmap/close/delete; dirfd relative openat/unlinkat; rename/truncate extras | Linux normalized Open/Read/Write/Close/Delete; mmap becomes Read, rename/truncate have no dedicated FileOps activity |
| Network | Separate `wt_tcp4srv/cli`, unconnected `wt_udp4srv/cli`, connected-client `wt_udp4cnsrv/cli`; TCP connect/accept/send/recv/disconnect | Independent UDP mode worker/socket/PID cases prevent one connected Receive satisfying unconnected coverage. Server receives still use peer-buffer recvfrom. `--ipv6` is extra stimulus, not certified Linux capture |

Linux comm is limited to 15 bytes. Names alone are **not** an authoritative key:
fork birth inherits parent comm; `/proc` resolver can normalize Python aliases;
exec-entry and image-replacement observations can disagree transiently. Manifest
PID/TID, UTC interval, case command line, file paths and socket ports are selectors.
Thread rows explicitly mark `expectedProcessStart: false`.
Current portable manifests add explicit per-path activity expectations (rename paths
need not each perform every operation) and IPv4 TCP/UDP host-relative socket expectations.
Eight-file canary separately records all eight expected paths. These are stimulus facts,
not raw-data mutation or inferred missing endpoint fields.
The named file worker also creates coexisting `CaseOnly.bin`/`caseonly.bin`, each
with Open/Write/Read/Close/Delete expectations, and a learned-cwd relative Delete.
The cwd change is isolated to that worker and restored before exit. These names
exercise exact production path/key projection, complementing unit-test case pairs.
<!-- GROUND_TRUTH: ../wintap/devtools/telemetry_smoke_workload.py §emit, worker, main; ../wintap/devtools/clone_lifecycle_workload.c §record -->

## Native helper

```bash
cc -O2 -pthread -o /home/user/qa/clone-helper devtools/clone_lifecycle_workload.c
python3 devtools/telemetry_smoke_workload.py --output /home/user/qa/smoke-002 \
  --clone-helper /home/user/qa/clone-helper
```

`WINTAP_SMOKE_NAMES=1` is set only for this native invocation. It enables short
distinct comm labels plus legacy clone process/vfork probes, without changing
the default clone correctness harness manifest. Python remains editable without
recompilation for ordinary cases; clone ABI/stack safety stays in the helper.
For the root-owned S3 workflow, add `--clone-helper /absolute/path/to/clone-helper`
to the sudo workload invocation in step 2, retaining all three output/root arguments.

## What success means

The S3 procedure above publishes this envelope automatically as parquet. For a
manual JSON transfer, choose the shared portable run envelope with
`--manifest /home/user/qa/manifests/run-001.json` (default `./smoke-results/`).
Upload/copy this JSON independently of parquet; the new
[[wiki/tool/smoke-test-results-dashboard]] groups runs by test UUID and queries
the recorded test-host/time/PID/path/ports. The workload's original `manifest.json`
remains detailed stimulus evidence; the dashboard reads the versioned envelope.

`manifest.json` contains generated/failed/skipped results and timestamped operation
expectations; optional native records are also saved in `native.manifest`.
Broken supplied helper or failed required activity yields exit 1, not success.
**Generated means OS workload completed, not that telemetry was captured.** Compare
with collected parquet after normal ETL flush/merge or use existing domain capture
validators. Aggregation, rate limits, filters and unavailable hooks change row
counts. Read [[wiki/schema/runtime-capability-receipt]] first. This does not induce
rundown Refresh, HOST, registry or SELinux/security events.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §MapOpToActivityType; ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §HandleEvent -->

## Verification (Ubuntu arm64)

- `python3 devtools/test_telemetry_smoke_workload.py -v`: two tests pass: all stdlib
  domains, expected activity manifest, thread negative case, lifecycle file removal,
  refusing existing directories and broken helper failure.
- `cc -O2 -Wall -pthread ... clone_lifecycle_workload.c`: no warnings/errors.
- Builder VM `lintap-clone-validation`, Ubuntu 24.04/aarch64, kernel
  `6.8.0-147-generic`: default and optional IPv6 stimulus complete; native one-round
  mode completes with no clone3 skips and distinct clone process/thread/vfork cases.
- Evidence: `/home/ubuntu/clone-validation/telemetry-smoke-first` and
  `/home/ubuntu/clone-validation/telemetry-smoke-final` (final Python manifest
  includes parsed native PID/TID records). These are **stimulus**
  runs, not collected cross-domain acceptance. RHEL and other architectures pending.
- Recompiled helper's default mode also passes actual CO-RE trace validation:
  unchanged 80 process/60 thread manifest, no missing/duplicate births, false thread
  births, wrong worker parents or skips (`smoke-helper-default-regression/report.json`).

Related packaged process acceptance: [[wiki/work/clone-default-true/verification]].
Repeated expanded canaries: [[wiki/tool/periodic-telemetry-soak-runner]] — reuse the
explicit Python interpreter with the sudo runner and start with `--rounds 1`.
