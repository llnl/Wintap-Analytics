---
title: "Design: Sensor-Neutral Process Creation Validation Harness"
type: workflow
confidence: medium
grounded_by:
  - ../wintap/devtools/process_capture_smoke_test.py
  - ../wintap/devtools/file_capture_smoke_test.py
  - ../wintap/devtools/network_capture_smoke_test.py
  - ../wintap/diagnostics/process-smoke-test/Program.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
policy: agent-editable
last_validated: 2026-07-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: researcher
status: draft
source_paths: ../wintap/devtools; ../wintap/diagnostics/process-smoke-test; ../wintap/wintap/platform/linux/sensor/ebpf
tags: [wintap, lintap, validation, process-events, smoke-tests, ebpf, research-workflows, test-design]
---

# Design: Sensor-Neutral Process Creation Validation Harness

This design note turns the current Wintap smoke tests into a plan for a cross-sensor validation harness. The immediate goal is to separate workload generation from sensor-specific capture so Lintap, Tetragon, Tracee, Sysdig, and potentially legacy Lintap/Sysdig chisels can be compared against the same known workload.

## Design Constraint

The harness must not assume any sensor is ground truth. The workload generator creates a best-effort manifest of actions it initiated, while the evaluator compares each sensor against that manifest and against its own loss counters.

This matters because process creation is timing-sensitive. The generator can know which subprocess PIDs it observed, command lines it launched, files it touched, and network targets it contacted, but it cannot know that the kernel delivered every lifecycle event to every sensor.

## Existing Assets

The current process smoke test already generates fork/exec, `posix_spawn`, `execveat` through `fexecve`, and short-lived `/bin/true` children.
<!-- GROUND_TRUTH: ../wintap/devtools/process_capture_smoke_test.py §spawn_process_suite -->

It also validates parent PID/hash linkage and Lintap breadcrumbs such as `PROC_START_SRC=sched_exec`, `PROC_START_SRC=execve_or_execveat`, and `PARENT_HASH_SRC=ebpf`.
<!-- GROUND_TRUTH: ../wintap/devtools/process_capture_smoke_test.py §validate_suite -->

The file smoke test creates, writes, reads, appends, and deletes a unique file path, then validates file rows by PID/path/activity.
<!-- GROUND_TRUTH: ../wintap/devtools/file_capture_smoke_test.py §generate_file_activity -->

The network smoke test generates HTTP/HTTPS and UDP traffic and validates captured rows by remote port/IP/protocol.
<!-- GROUND_TRUTH: ../wintap/devtools/network_capture_smoke_test.py §generate_traffic -->

The C# process diagnostic starts a pre-existing bash/sleep tree before Lintap starts so `ProcessRundownSensor` can validate rundown parent linkage without eBPF.
<!-- GROUND_TRUTH: ../wintap/diagnostics/process-smoke-test/Program.cs §StartLongLivedProcessTree -->

## Proposed Repository Shape

If implemented in `../wintap`, place the harness under `devtools/validation/`:

```text
devtools/validation/
  README.md
  workloads/
    process_workload.py
    file_workload.py
    network_workload.py
    combined_workload.py
  runners/
    lintap_runner.py
    tetragon_runner.py
    tracee_runner.py
    sysdig_runner.py
    external_runner.py
  normalizers/
    lintap_normalizer.py
    tetragon_normalizer.py
    tracee_normalizer.py
    sysdig_normalizer.py
  evaluator/
    schema.py
    evaluate_process.py
    evaluate_owner_attribution.py
    report.py
  run_validation.py
```

If implemented in `Wintap-Analytics`, keep the same internal shape under a research workflow directory. The advantage of `../wintap/devtools` is proximity to existing smoke tests and Lintap build/run helpers. The advantage of `Wintap-Analytics` is cross-repo neutrality.

## Run Artifact Layout

Every validation run should be self-contained:

```text
validation-runs/
  20260731T183000Z-lintap-process-baseline/
    manifest.json
    run_config.json
    environment.json
    raw/
      sensor-output/
      sensor-logs/
      workload-stdout.log
      workload-stderr.log
    normalized/
      process_identity.jsonl
      process_fork.jsonl
      exec_attempt.jsonl
      exec_success.jsonl
      process_exit.jsonl
      process_rundown.jsonl
      file_activity.jsonl
      network_activity.jsonl
      sensor_loss.jsonl
    reports/
      report.json
      report.md
```

For repeatability, never overwrite a run directory. Copy or link raw sensor outputs into `raw/` and keep normalized outputs immutable once generated.

## Environment Metadata

Capture at least:

```json
{
  "run_id": "20260731T183000Z-lintap-process-baseline",
  "host": {
    "hostname": "...",
    "kernel_release": "...",
    "kernel_version": "...",
    "architecture": "x86_64",
    "cpu_count": 16,
    "page_size": 4096,
    "distro": "...",
    "btf_vmlinux_present": true,
    "inside_container": false,
    "pid_namespace": "..."
  },
  "sensor": {
    "name": "lintap",
    "repo": "../wintap",
    "branch": "grantj-ebf-fixes",
    "commit": "7f932558e5d3f83ec77978f71b8a5588648ecd04",
    "command": "...",
    "config": {}
  },
  "workload": {
    "profile": "process-baseline-v1",
    "started_utc": "...",
    "ended_utc": "..."
  }
}
```

The exact kernel and page size matter because reference projects have known behavior differences around BTF availability, ring buffer page size, and tracepoint attachment.

## Manifest Schema

The manifest should describe what the workload attempted and what PIDs it observed. It should not assert that every sensor must observe every event unless the case is marked required for that sensor profile.

Top-level shape:

```json
{
  "schema_version": "process-validation-manifest/v1",
  "run_id": "20260731T183000Z-example",
  "created_utc": "2026-07-31T18:30:00Z",
  "workload_profile": "process-baseline-v1",
  "cases": [],
  "processes": [],
  "files": [],
  "network": [],
  "notes": []
}
```

Case shape:

```json
{
  "case_id": "fork_exec_001",
  "case_type": "fork_exec",
  "started_utc": "...",
  "ended_utc": "...",
  "expected_events": ["process_fork", "exec_success", "process_exit"],
  "required": true,
  "tags": ["process", "parent-child", "exec_success"],
  "process_refs": ["proc_parent_001", "proc_child_001"],
  "file_refs": [],
  "network_refs": []
}
```

Process shape:

```json
{
  "process_ref": "proc_child_001",
  "case_id": "fork_exec_001",
  "role": "child",
  "observed_pid": 12345,
  "observed_ppid": 12344,
  "command": ["sleep", "5"],
  "expected_executable": "/usr/bin/sleep",
  "expected_name": "sleep",
  "started_by_workload_utc": "...",
  "ended_by_workload_utc": "...",
  "parent_ref": "proc_parent_001",
  "identity_expectation": "pid_plus_start_time",
  "provenance_markers": ["workload_run_id=...", "case_id=fork_exec_001"]
}
```

File shape:

```json
{
  "file_ref": "file_001",
  "case_id": "file_child_001",
  "path": "/tmp/wintap-validation/<run_id>/file_001.txt",
  "expected_activities": ["open", "write", "read", "delete"],
  "owner_process_ref": "proc_child_001"
}
```

Network shape:

```json
{
  "network_ref": "tcp_001",
  "case_id": "network_child_001",
  "protocol": "tcp",
  "direction": "outbound",
  "remote_host": "127.0.0.1",
  "remote_port": 18080,
  "owner_process_ref": "proc_child_001",
  "payload_marker": "run_id=... case_id=network_child_001"
}
```

Prefer local loopback servers over public internet for deterministic network validation. Existing public endpoint probes are useful smoke tests but introduce DNS/CDN/proxy ambiguity.
<!-- SYNTHESIS: inferred from ../wintap/devtools/network_capture_smoke_test.py endpoint validation tolerances -->

## Normalized Event Schema

Normalize each sensor into JSONL tables. Keep raw tool fields as `raw` where useful.

### process_identity

```json
{
  "sensor": "lintap",
  "run_id": "...",
  "tool_process_id": "...",
  "pid": 12345,
  "tid": 12345,
  "start_time_ns": 1234567890,
  "start_time_utc": "...",
  "identity_confidence": "high",
  "identity_source": "pid_hash|exec_id|entity_id|threadinfo|derived",
  "pid_reuse_safe": true,
  "raw": {}
}
```

### process_fork

```json
{
  "sensor": "lintap",
  "run_id": "...",
  "event_time_utc": "...",
  "parent_pid": 12344,
  "child_pid": 12345,
  "parent_identity": "...",
  "child_identity": "...",
  "fork_kind": "fork|clone|vfork|unknown",
  "clone_flags": "0x...",
  "source_hook": "sched_process_fork|wake_up_new_task|synthetic",
  "raw": {}
}
```

### exec_attempt

```json
{
  "sensor": "lintap",
  "run_id": "...",
  "event_time_utc": "...",
  "pid": 12345,
  "identity": "...",
  "syscall": "execve|execveat",
  "filename": "/bin/sleep",
  "flags": "0x00001000",
  "source_hook": "sys_enter_execve|sys_enter_execveat",
  "raw": {}
}
```

### exec_success

```json
{
  "sensor": "lintap",
  "run_id": "...",
  "event_time_utc": "...",
  "pid": 12345,
  "identity": "...",
  "executable": "/usr/bin/sleep",
  "command_line": "sleep 5",
  "parent_pid": 12344,
  "parent_identity": "...",
  "source_hook": "sched_process_exec",
  "raw": {}
}
```

### sensor_loss

```json
{
  "sensor": "tetragon",
  "run_id": "...",
  "metric_name": "observer_ringbuf_events_lost_total",
  "metric_value": 12,
  "metric_source": "prometheus|log|stats|derived",
  "event_family": "process|all|unknown",
  "captured_utc": "..."
}
```

This schema is deliberately provenance-heavy. Do not collapse `exec_attempt` and `exec_success` into one event during normalization.

## Workload Matrix

Initial process-focused cases:

| Case | Current Seed | Expected Normalized Events | Notes |
|---|---|---|---|
| simple exec | new | `exec_attempt`, `exec_success`, `process_exit` | minimal sanity |
| fork exec | existing process smoke | `process_fork`, `exec_success`, `process_exit` | parent join required |
| posix spawn | existing process smoke | tool-dependent fork/clone plus exec | libc/kernel dependent |
| execveat fexecve | existing process smoke | `exec_attempt` with flags plus `exec_success` | must preserve flags |
| short-lived burst | existing process smoke | many exec/fork/exit rows | report recall, not binary pass |
| pre-existing process | C# diagnostic | `process_rundown` | no live eBPF required |
| fork no exec | new | `process_fork`, maybe exit, no exec success | catches fork-only coverage |
| vfork | extend clone tracer coverage | `process_fork` with vfork marker if available | clone flags/sentinel useful |
| thread-like clone | new pthread or clone case | thread/process ambiguity | requires semantic decision |
| parent exits first | new | child parent identity despite parent gone | tests eBPF parent start time |
| file owned by child | existing file smoke adapted | file rows joined to child identity | tests owner attribution |
| network owned by child | existing network smoke adapted | network rows joined to child identity | use local server |

## Evaluation Modes

Use at least three modes:

| Mode | Purpose | Pass/Fail Style |
|---|---|---|
| smoke | catch broken sensor/config quickly | binary pass/fail |
| baseline | build expected accuracy numbers | report metrics, do not fail on imperfect sensors |
| regression | enforce known behavior for one sensor/version/kernel | threshold pass/fail |

Baseline mode is the most important for this research. It should produce counts and confidence intervals across repeated runs rather than one-off pass/fail results.

## Metrics

Process metrics:

- fork recall: observed expected `process_fork` cases divided by expected fork-like creations.
- exec success recall: observed expected `exec_success` cases divided by expected successful execs.
- exec attempt recall: observed expected `exec_attempt` cases divided by expected attempted exec syscalls.
- exit recall: observed exits divided by expected exits.
- parent join rate: child events with correct parent identity.
- identity stability rate: fork/exec/exit rows for one process share one identity.
- duplicate start count: multiple start-like rows for one identity and source family.
- unknown parent count: records with missing or sentinel parent identity.
- PID reuse correctness: reused PID maps to distinct identities.

Owner attribution metrics:

- file owner join rate.
- network owner join rate.
- unknown file/network owner count.
- owner join latency if timestamps allow it.

Loss and pressure metrics:

- sensor-reported kernel/ring/perf drops.
- userspace queue drops.
- ETL/parquet drops.
- missing output files.
- latency from workload event to sensor output flush.

## Sensor-Specific Normalization Hints

### Lintap

- `PID_HASH` is the native identity.
- `PROC_START_SRC=sched_exec` maps to `exec_success`.
- `PROC_START_SRC=execve_or_execveat` maps to `exec_attempt` unless paired/deduped by evaluator.
- `PARENT_HASH_SRC=ebpf` and `PARENT_HASH_SRC=proc` should be parsed into parent provenance.
- Direct Parquet and ETL Parquet currently use different column names; existing smoke tests already probe schema first.
<!-- GROUND_TRUTH: ../wintap/devtools/process_capture_smoke_test.py §detect_column_names -->

### Tetragon

- `exec_id` should map to `tool_process_id`.
- `process_exec` maps to `exec_success`.
- clone events may be internal/non-notifying in some paths, so process cache-derived state may be needed.
- Collect observer loss metrics with the normalized output.

### Tracee

- entity IDs from PID/TID plus start time should map to `tool_process_id`.
- `sched_process_exec` maps to `exec_success`.
- `execve` and `execveat` syscall events map to `exec_attempt` or failed exec, depending return behavior.
- Control-plane signal loss should be captured separately from regular event loss.

### Sysdig

- There may not be a stable immutable process ID equivalent; derive one from TID/PID plus clone timestamp or start metadata where available.
- `execve <`/exit-style events and sched-derived events need careful mapping by engine.
- Capture scap/libsinsp drop counters and invalid placeholder behavior.
- Avoid pre-analysis filters that drop state-changing events during validation.

## First Implementation Slice

The first useful slice should be small and non-heroic:

1. Create a sensor-neutral `process_workload.py` that only writes `manifest.json` and prints a compact summary.

2. Include these cases only:

- simple exec
- fork exec
- execveat fexecve
- short-lived burst
- pre-existing process tree

3. Create a Lintap normalizer for direct Parquet process output only.

4. Create an evaluator that computes counts, parent join, identity stability, and duplicate starts.

5. Run the same workload three times against Lintap on one VM and save all artifacts.

6. Only after Lintap baseline works, add Tetragon normalizer.

This avoids trying to build four complete sensor integrations before the manifest and evaluator are proven.

## Design Decisions To Revisit

- Whether the workload generator should itself collect `/proc/<pid>/stat` start times for stronger manifest identities.
- Whether local TCP/UDP servers should replace public HTTP/DNS endpoints for all validation runs.
- Whether raw outputs should be copied, symlinked, or only referenced by manifest.
- Whether normalized outputs should be JSONL first, then DuckDB/Parquet later.
- Whether `exec_attempt` and `exec_success` should be evaluated as separate required events or as alternative evidence for a successful process start.
- Whether clone/thread cases should be in the first baseline or deferred until process-vs-thread semantics are explicitly decided.

## Risks

- The manifest will never be perfect ground truth for kernel events; it is ground truth for workload intent and observed child PIDs.
- Public network targets introduce nondeterminism; prefer local servers for accuracy baselines.
- Short-lived burst tests are inherently probabilistic; report recall distributions across repeated runs.
- Comparing sensors without collecting their loss counters can misclassify load drops as semantic gaps.
- PID reuse testing may require privileged/containerized PID namespace control or very large churn.

## Suggested Next Coding Task

Implement `process_workload.py` as a standalone manifest generator by extracting and refactoring the workload-generation half of `../wintap/devtools/process_capture_smoke_test.py`. Do not query sensor output in this script. It should produce `manifest.json`, `workload-stdout.log`, and `workload-stderr.log` under a supplied run directory.

## Initial Code Prototype

An initial uv-managed prototype now exists in this repository:

```text
validation/process-creation/
  pyproject.toml
  uv.lock
  src/wintap_process_validation/
  tests/
```

Implemented commands:

```bash
cd validation/process-creation
uv run --extra dev pytest
uv run wpv-workload --run-dir /tmp/wpv-workload --run-id example
uv run wpv-mock-run --run-dir /tmp/wpv-mock --run-id example
uv run wpv-evaluate --manifest /tmp/wpv-mock/manifest.json --normalized-dir /tmp/wpv-mock/normalized
uv run --extra parquet wpv-normalize-lintap --parquet-root /path/to/parquet --out-dir /tmp/normalized --run-id example
```

Current prototype scope:

- `Manifest` dataclasses and JSON serialization.
- Sensor-neutral process workload manifest generation for simple exec, fork/exec, short-lived burst, and Linux-only execveat when available.
- Mock normalized event writer for local development.
- Evaluator metrics for fork recall, exec-attempt recall, exec-success recall, exit recall, parent join, duplicate exec-success, identity collisions, and sensor loss total.
- Lintap process normalizer logic for direct/ETL-style process rows, with a DuckDB-backed Parquet CLI behind the `parquet` extra.

Validated locally on macOS:

```text
uv run --extra dev pytest
5 passed
```

Also validated:

- `wpv-workload` generated a manifest on macOS, skipping execveat with a manifest note because `os.execveat` is unavailable.
- `wpv-mock-run` generated normalized mock events and reported the deliberately injected duplicate `exec_success` event.

Next implementation step: run the prototype on Linux against Lintap direct Parquet and refine the Lintap normalizer against real output.

## Local Mock Test Notes

On 2026-07-31, a macOS-local mock test exercised the proposed manifest and normalized event model without requiring Linux eBPF or root access.

Validated:

- Wiki work-thread pages had required frontmatter keys.
- Wikilinks among the work-thread pages resolved.
- Checked `GROUND_TRUTH` paths in the new pages resolved from the wiki repository.
- Core source paths for Wintap, Tetragon, Tracee, and Sysdig existed locally.
- An in-memory mock manifest plus normalized event tables produced expected metrics for fork recall, exec-attempt recall, exec-success recall, exit recall, parent-join rate, duplicate exec-success count, and cross-case identity collision count.

The mock deliberately injected one duplicate `exec_success` record for a single process identity. The evaluator metric reported `duplicate_exec_success = 1`, which confirms the proposed metrics can catch one of the main expected Lintap risks: multiple start-like records for one PID/start-time identity.

Not validated on macOS:

- Actual eBPF attachment.
- BPF ring-buffer polling.
- Linux `/proc/<pid>/stat` start-time conversion.
- Lintap direct-Parquet output.
- Tetragon, Tracee, or Sysdig live sensor output.
- Kernel/user loss counters under load.

The next useful implementation remains a real `process_workload.py` manifest generator, followed by a Lintap direct-Parquet normalizer/evaluator on a Linux VM.

## Multipass VM Test Notes

On 2026-08-06, the first Multipass Ubuntu 24.04 arm64 VM test reached a passing Lintap process smoke test after several compatibility fixes.

Environment:

- Multipass Ubuntu 24.04 arm64.
- Kernel `6.8.0-136-generic`.
- BTF available at `/sys/kernel/btf/vmlinux`.
- Wintap branch `grantj-ebf-fixes` at `7f93255`.

Commands validated in the VM:

```bash
cd /home/ubuntu/git/wintap/wintap && make build_ebpf && make build_dotnet
cd /home/ubuntu/git/Wintap-Analytics/validation/process-creation && UV_PROJECT_ENVIRONMENT=/tmp/wpv-venv uv run --extra dev pytest
cd /home/ubuntu/git/Wintap-Analytics/validation/process-creation && UV_PROJECT_ENVIRONMENT=/tmp/wpv-venv uv run wpv-mock-run --run-dir /tmp/validation-runs/wpv-mock --run-id multipass-mock
cd /home/ubuntu/git/wintap && sudo python3 devtools/process_capture_smoke_test.py --start-lintap --lintap-dll /home/ubuntu/git/wintap/wintap/bin/Debug/net8.0/Lintap.dll --timeout 240 --poll-interval 5
```

Observed fixes required:

- `task_struct.real_start_time` was not present in Ubuntu 24.04 arm64 `vmlinux.h`; the CO-RE tracer needed `task_struct.start_time` instead.
- `bpf_object__find_program_by_title` was not exported by `libbpf.so.1`; extra eBPF programs now attach by program name.
- eBPF parent start-time conversion needed to match `/proc/<pid>/stat` clock-tick semantics to produce parent hashes matching parent process rows.
- Normal parent attribution now prefers `/proc` parent enrichment and uses eBPF parent start time as fallback when `/proc` is unavailable.
- The smoke test now ignores `.parquet.active` files and does not require `execveat` flags when the Python runtime lacks `os.execveat` and `os.AT_EMPTY_PATH`.
- `uv` in a shared Mac/VM mount must use a VM-local environment, e.g. `UV_PROJECT_ENVIRONMENT=/tmp/wpv-venv`, to avoid trying to execute a macOS `.venv` interpreter inside Linux.

Passing smoke-test summary:

```text
PASS: captured process records for all creation variants
case=fork_exec parent_rows=5 child_rows=2 ... PROC_START_SRC=sched_exec PARENT_HASH_SRC=proc
case=posix_spawn parent_rows=2 child_rows=5 ... PROC_START_SRC=sched_exec PARENT_HASH_SRC=proc
case=execveat_fexecve parent_rows=5 child_rows=2 ... PROC_START_SRC=sched_exec PARENT_HASH_SRC=proc
```

Note: on this Ubuntu/Python combination, `os.execveat` is unavailable, so the smoke test validates the child process but does not validate `FLAGS=0x00001000`. A lower-level C workload will be needed to validate `execveat(2)` reliably across distros.

## Process Table Noisy Test Notes

On 2026-08-06, a resolver-mode noisy process workload was added and run against Lintap in the Multipass VM. The workload ran for 780 seconds and created a mix of very short-lived `bash -c ':'` processes and longer-lived Python sleep processes.

Initial problem findings:

- The DuckDB process table is named `process` in `<DataRoot>/event_store/main.duckdb`.
- The table behaves as a history table, not a live-only state table.
- The eBPF diagnostic monitor spawned `bpftool map list -j` every five seconds per sensor, and those diagnostic subprocesses were captured by Lintap itself.
- Very short-lived bash processes often exited before their Start event was registered, so Stop events did not match an existing `PidHash`.
- When `/proc` was gone by Start processing time, process Start used current wall-clock time, which caused multiple Start-like events for one PID to receive different `PidHash` values.

Fixes applied before the final noisy run:

- `EnableBpfDiagMonitor` now defaults to `false` and the diagnostic `bpftool` subprocess loop is opt-in.
- `execve_tracer.bpf.c` now captures `task_struct.start_time` for the process itself, not only parent context.
- `ExecveSensor` uses eBPF process start time when `/proc` start time is unavailable.
- `ExitSensor` eBPF emits only thread-group leader exits in the CO-RE tracer.
- `ProcessResolver` no longer inserts Stop-only process rows for unmatched Stops.
- `ProcessResolver` keeps a short in-memory pending-exit cache so a Stop that arrives before Start registration can close the Start row when it arrives.
- `GetPidHash` is now time-window aware and respects `exit_time`.

Final noisy run summary:

```text
run_id: noisy-state-1786064182
duration: 780 seconds
manifest processes: 1888
manifest cases: 166
process table rows: 1983
distinct process IDs in table: 1924
closed rows: 1923
open rows: 60
manifest PIDs observed: 1888 / 1888
manifest PIDs with open rows: 59 / 1888
```

By dominant process names:

| Process Name | Rows | Closed | Open |
|---|---:|---:|---:|
| `bash` | 1895 | 1836 | 59 |
| `python3` | 52 | 52 | 0 |
| `sleep` | 21 | 21 | 0 |

Interpretation:

- The diagnostic self-noise was eliminated as the dominant table-growth source.
- eBPF process start time plus pending-exit reconciliation dramatically reduced duplicate/open rows for short-lived processes.
- There is still residual leakage: 59 manifest PIDs had open rows after the run, mostly short-lived `bash` rows.
- `stop_only_like` rows are still nonzero, so there are remaining cases where Stop and Start are not reconciled perfectly.
- The next iteration should focus on those residual open rows and Stop-only-like rows, using manifest PID joins and event ordering logs.

Artifacts copied to the wiki repo workspace:

```text
validation/process-creation/noisy-state-summary-multipass-2026-08-06.json
validation/process-creation/smoke-15m-summary-multipass-2026-08-06.json
```

## Current Implementation Snapshot

As of the first commit checkpoint for this thread, the validation work has moved from notes into executable code and VM-tested Lintap fixes.

Implemented in `Wintap-Analytics`:

- uv-managed validation harness under `validation/process-creation`.
- Sensor-neutral manifest schema.
- Mock normalized event generator and evaluator.
- Lintap process row normalizer.
- Noisy mixed process workload command.
- Resolver-mode noisy process-state runner.
- Process table summarizer.

Implemented in `../wintap`:

- eBPF exec tracer captures process start time when `/proc` is unavailable.
- eBPF exit tracer filters task-level exits to thread-group leader exits.
- Extra exec/clone eBPF programs attach by program name for Ubuntu libbpf compatibility.
- `ExecveSensor` uses `/proc` parent attribution first and eBPF parent fallback second.
- `ProcessResolver` avoids unmatched Stop-only inserts, reconciles Stop-before-Start with a pending-exit cache, and makes `GetPidHash` respect `exit_time`.
- BPF diagnostic monitor is opt-in to avoid self-generated `bpftool` process noise.
- Process smoke test ignores `.parquet.active` files and relaxes Python-dependent execveat flag validation.

Implemented in `../Lintap`:

- Multipass setup updated for current Wintap/Lintap validation workflow.
- Ubuntu VM provisioning installs current eBPF/.NET/uv/DuckDB/dev tooling.
- Multipass docs and SSH helper updated for the current checkout layout.

Validated before this checkpoint:

- `make build_ebpf && make build_dotnet` passed in Multipass Ubuntu 24.04 arm64.
- `uv run --extra dev pytest` passed locally and in the VM.
- Lintap process smoke test passed after fixes.
- Five process smoke rounds over roughly 15 minutes all passed.
- Noisy resolver-mode process workload observed all 1888 manifest PIDs and reduced process-table open rows to 60.

Known remaining issue:

- Short-lived bash workload still left 59 manifest PIDs with open rows after the 780-second noisy run. This is much improved, but not solved.
