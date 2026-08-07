---
title: "Current State: Lintap Process Creation Validation"
type: workflow
confidence: medium
grounded_by:
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../Wintap-Analytics/validation/process-creation/noisy-state-1h-summary-multipass-2026-08-06.json
policy: agent-editable
last_validated: 2026-08-06
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: researcher
status: draft
source_paths: ../wintap/wintap/core/infrastructure; ../wintap/wintap/platform/linux/sensor/ebpf; validation/process-creation
tags: [wintap, lintap, validation, process-events, ebpf, process-state, current-state]
---

# Current State: Lintap Process Creation Validation

Snapshot date: 2026-08-06.

## Commits

Current checkpoint commits:

| Repo | Commit | Message |
|---|---|---|
| `../wintap` | `5dccdc1` | Stabilize Linux process state tracking |
| `../Lintap` | `fce6bac` | Refresh Multipass validation setup |
| `Wintap-Analytics` | `3c670de` | Add process creation validation harness |
| `Wintap-Analytics` | `ccbf839` | Remove generated validation state |
| `Wintap-Analytics` | `66eb28e` | Record one-hour process state validation |

## What Works

- Multipass Ubuntu 24.04 arm64 VM can build Lintap eBPF and .NET.
- `uv` validation harness tests pass on macOS and inside the VM.
- Lintap process smoke test passes after the current fixes.
- Five smoke-test rounds over roughly 15 minutes all passed.
- One-hour noisy resolver-mode workload completed and produced process-table metrics.

## Current Lintap Fixes

Implemented in `../wintap`:

- CO-RE exec tracer uses `task_struct.start_time`, which exists on Ubuntu 24.04 arm64.
- Exec eBPF events carry process start time for cases where `/proc` is gone before userspace enrichment.
- Exit eBPF emits only thread-group leader exits to reduce thread-exit pollution.
- `ExecveSensor` and `CloneSensor` attach extra BPF programs by program name instead of unavailable `bpf_object__find_program_by_title`.
- Parent attribution uses `/proc` first and eBPF parent start-time fallback second.
- `ProcessResolver` no longer inserts unmatched Stop-only rows.
- `ProcessResolver` has a pending-exit cache to reconcile Stop-before-Start ordering.
- `GetPidHash` now respects `exit_time` when resolving a PID at a time.
- BPF diagnostic monitor is opt-in via `EnableBpfDiagMonitor=false` by default, avoiding self-generated `bpftool` process noise.

## Validation Harness

Implemented in `Wintap-Analytics/validation/process-creation`:

- uv-managed Python package.
- Manifest schema.
- Mock normalized events and evaluator.
- Lintap process row normalizer.
- `wpv-noisy-processes` workload.
- `run_lintap_noisy_state_test.sh` resolver-mode runner.
- `summarize_lintap_process_table.py` process table summarizer.

## One-Hour Result

Artifact:

```text
validation/process-creation/noisy-state-1h-summary-multipass-2026-08-06.json
```

Summary:

| Metric | Value |
|---|---:|
| Workload duration | 3600 seconds |
| Manifest processes | 8732 |
| Manifest cases | 767 |
| Manifest PIDs observed | 8732 / 8732 |
| Process table rows | 10372 |
| Distinct process IDs in table | 10064 |
| Closed rows | 10060 |
| Open rows | 312 |
| Manifest PIDs with open rows | 285 / 8732 |

Dominant process names:

| Process | Rows | Closed | Open |
|---|---:|---:|---:|
| `bash` | 8783 | 8498 | 285 |
| `python3` | 237 | 237 | 0 |
| `dpkg-deb` | 194 | 194 | 0 |
| `rm` | 115 | 113 | 2 |

Interpretation:

- All workload manifest PIDs were observed.
- Longer-lived Python workload rows closed cleanly.
- Residual open rows are concentrated in very short-lived `bash` rows.
- The remaining open-row rate for workload PIDs is about 3.3%.

## Open Problems

- Residual short-lived `bash` processes still leave open rows.
- `stop_only_like` is not a reliable metric name anymore because after pending-exit reconciliation legitimate short-lived processes can have equal `create_time` and `exit_time` at second precision.
- True `execveat(2)` coverage still needs a small C workload because Ubuntu Python 3.12 lacks `os.execveat`.
- Reference sensors have not yet been run in the harness.
- Live process state is still persisted in DuckDB; the architecture direction remains memory-first attribution with durable store as backing/history.

## Recommended Next Steps

1. Investigate the 285 residual open manifest PIDs from `noisy-state-1786071273`.
2. Add event-order diagnostics for those PIDs: Start count, Stop count, first/last event time, source breadcrumb, and whether pending-exit was applied.
3. Add a C `execveat` workload to validation.
4. Add a Lintap normalizer/evaluator path for resolver-mode `process` DuckDB output, not just Parquet.
5. Run the same noisy workload with Tetragon and Tracee for comparison.

## 30-Minute All-Events Normal ETL Run

On 2026-08-07, a 30-minute Lintap run was executed with normal ETL/Parquet output enabled:

```json
{
  "DisableETL": false,
  "EnableDirectParquet": false,
  "WriteToParquet": true,
  "Execve": true,
  "Clone": true,
  "Exit": true,
  "Network": true,
  "FileOps": true,
  "ProcessRundown": true
}
```

Run summary:

```text
run_id: all-events-30m-1786118104
duration: 1878 seconds
noisy workload processes: 3432
noisy workload cases: 302
process smoke: PASS
file smoke: PASS
network smoke: FAIL
```

Parquet outputs written under `/tmp/lintap-all-events-30m-1786118104/parquet`:

| Output Directory | Files | Rows |
|---|---:|---:|
| `fileserializer` | 1 | 2996 |
| `processserializer` | 1 | 57 |
| `processstopserializer` | 1 | 26 |
| `raw_sensor/raw_host/dayPK=20260807/hourPK=16` | 1 | 1 |
| `raw_sensor/raw_macip/dayPK=20260807/hourPK=16` | 1 | 1 |
| `raw_sensor/raw_process/dayPK=20260807/hourPK=16` | 12 | 32013 |
| `raw_sensor/raw_process_file/dayPK=20260807/hourPK=16` | 6 | 300000 |

Network finding:

- HTTP/HTTPS and UDP test traffic was generated successfully.
- No matching network Parquet rows were found before timeout.
- Lintap logs showed `NetworkSensor aggregated BPF diag (STORE/HIT/MISS) = 0/0/62` and BPF diag miss events, indicating the network path was active enough to emit diagnostics but did not resolve/emit normal TCP/UDP telemetry rows.
- No `raw_process_conn_incr`/TCP/UDP output appeared in the summarized Parquet directories.

Artifacts copied to this repo:

```text
validation/process-creation/all-events-30m-summary-multipass-2026-08-07.json
validation/process-creation/all-events-30m-parquet-summary-multipass-2026-08-07.json
validation/process-creation/all-events-30m-network-smoke-multipass-2026-08-07.out
```

Follow-up network fix:

- Root cause was another libbpf compatibility issue: `NetworkSensor` still used `bpf_object__find_program_by_title`, which is unavailable in the Ubuntu 24.04 arm64 VM's `libbpf.so.1`.
- `NetworkSensor` was patched to attach additional network programs by BPF function name.
- Its diagnostic reporter is now gated by `EnableBpfDiagMonitor` so normal validation does not create extra diagnostic process/message noise.

Validation after the fix:

```text
Direct-Parquet network smoke: PASS
Normal ETL all-events short run: PASS for process, file, and network smoke
```

Normal ETL short all-events output after the fix:

| Output Directory | Files | Rows |
|---|---:|---:|
| `raw_sensor/raw_process_conn_incr/dayPK=20260807/hourPK=16/protoPK=tcp` | 2 | 165 |
| `raw_sensor/raw_process_conn_incr/dayPK=20260807/hourPK=16/protoPK=udp` | 2 | 33 |
| `raw_sensor/raw_process/dayPK=20260807/hourPK=16` | 4 | 9859 |
| `raw_sensor/raw_process_file/dayPK=20260807/hourPK=16` | 2 | 73685 |

Artifacts:

```text
validation/process-creation/all-events-10m-summary-multipass-2026-08-07.json
validation/process-creation/all-events-10m-parquet-summary-multipass-2026-08-07.json
validation/process-creation/all-events-10m-network-smoke-multipass-2026-08-07.out
```

Remaining network follow-up: the older failed 30-minute all-events artifact should be treated as pre-fix evidence. A full 30-minute normal ETL all-events run should be repeated with the network attachment fix when time allows.
