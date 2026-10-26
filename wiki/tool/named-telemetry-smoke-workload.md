---
title: "Named Linux telemetry smoke workload"
type: tool
confidence: high
grounded_by:
  - ../wintap/devtools/telemetry_smoke_workload.py
  - ../wintap/devtools/clone_lifecycle_workload.c
  - ../wintap/devtools/test_telemetry_smoke_workload.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
policy: agent-editable
last_validated: 2026-10-25
repo_scope: wintap
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/devtools
tags: [smoke-test, linux, process, file, network, field-validation]
---

# Named Linux telemetry smoke workload

`../wintap/devtools/telemetry_smoke_workload.py` is a field-editable Python stdlib
stimulus for an **already-running** collector. It does not install, stop, start,
or reconfigure the sensor. No root needed; sockets use loopback only. Wintap owns
the tool; Analytics hosts this knowledge/verification record.

From the Wintap repo:

```bash
python3 devtools/telemetry_smoke_workload.py --output /home/user/qa/smoke-001
```

Use a fresh directory **outside** collector data/runtime roots and filtered paths
(for example `/tmp`). Existing directories are refused. Files are removed as part
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

## What success means

For cross-host analysis, additionally export the shared portable run envelope with
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
