---
title: "Handoff: Process Creation Validation Next Steps"
type: workflow
confidence: medium
grounded_by:
  - ../wintap/devtools/process_capture_smoke_test.py
  - ../wintap/diagnostics/process-smoke-test/Program.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
policy: agent-editable
last_validated: 2026-07-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: researcher
status: draft
source_paths: ../wintap/devtools; ../wintap/diagnostics/process-smoke-test; ../wintap/wintap/platform/linux/sensor/ebpf
tags: [wintap, lintap, validation, process-events, smoke-tests, ebpf, research-workflows]
---

# Handoff: Process Creation Validation Next Steps

This handoff describes the next phase: build validation workloads that generate known process/file/network activity, run them repeatedly against Lintap, Tetragon, Tracee, Sysdig, and possibly legacy Lintap/Sysdig chisels, then compare captured output against expected ground truth.

## Goal

Create repeatable ground-truth workloads that let us answer:

- Which sensors capture each process creation semantic reliably?
- Which sensors lose events under burst/load?
- Which sensors preserve parent and process identity under PID reuse and short-lived processes?
- Which semantic details does Lintap need to borrow from the reference projects?
- Which upstream bugs or documentation gaps can we report or fix in reference projects?

## Current Starting Points

Wintap already has a rich process smoke test that generates fork/exec, posix spawn, execveat, and short-lived children.
<!-- GROUND_TRUTH: ../wintap/devtools/process_capture_smoke_test.py §workload generation -->

Wintap also has a C# diagnostic process smoke test focused on process rundown and parent hash linkage.
<!-- GROUND_TRUTH: ../wintap/diagnostics/process-smoke-test/Program.cs §process rundown diagnostic -->

These should become the seed for a sensor-neutral workload generator and comparison harness.

## Proposed Validation Architecture

Build four layers:

| Layer | Responsibility | Output |
|---|---|---|
| workload generator | creates known process/file/network patterns | ground-truth manifest |
| sensor runner | runs one sensor under controlled config | raw sensor output and logs |
| normalizer | maps each tool output into common event vocabulary | normalized event tables |
| evaluator | compares normalized output to manifest and counters | accuracy/loss report |

The workload generator should not depend on any sensor. It should write a manifest containing expected PIDs where possible, expected parent/child relationships, commands, timing windows, and workload IDs embedded in command lines and file paths.

## Event Vocabulary For Normalization

Normalize all sensor output into these tables first:

| Table | Meaning |
|---|---|
| `process_fork` | parent created child by fork/clone/vfork-like mechanism |
| `exec_attempt` | exec/execveat syscall attempt observed |
| `exec_success` | successful image replacement observed |
| `process_rundown` | pre-existing process observed from startup scan |
| `process_exit` | process lifetime ended |
| `process_identity` | stable identity keyed by PID plus start time or tool-specific ID |
| `parent_join` | child identity to parent identity |
| `file_activity` | file workload actions attributed to identity |
| `network_activity` | network workload actions attributed to identity |
| `sensor_loss` | tool-reported loss/drop/backpressure counters |

Do not force all tools into a single `Process Start` row too early. Keep provenance.

## Workload Cases

Start with deterministic small cases, then add stress.

| Case | Purpose | Expected Observations |
|---|---|---|
| simple exec | `/bin/true` or `/usr/bin/id` | one exec attempt, one exec success, one exit |
| fork then exec | parent forks child and child execs | fork lifecycle plus exec success with correct parent |
| fork no exec | child exits without exec | fork lifecycle and exit; no exec success |
| posix spawn | libc spawn path | fork/clone plus exec, depending libc/kernel behavior |
| execveat path | `execveat` with `AT_EMPTY_PATH` | execveat attempt flags and exec success |
| vfork | vfork-specific path | vfork breadcrumb/clone flags where supported |
| clone thread-like | `clone`/pthread workload | distinguish process versus thread semantics if tool exposes it |
| short-lived burst | many `/bin/true` children | loss and parent attribution under burst |
| parent exits first | child outlives parent or parent exits quickly | parent identity despite `/proc` race |
| PID reuse pressure | many short-lived processes until PID reuse likely | identity differs across reused PID |
| pre-existing process | start process before sensor | rundown/procfs startup capture |
| file after fork | child creates/reads/writes known file | owner process attribution |
| network after fork | child performs localhost TCP/UDP | owner process attribution |
| sustained load | background CPU/process churn | drop counters and latency under load |

Each workload should embed a unique run id, case id, and sequence number in command lines, filenames, and network payloads where possible.

## Repetition Strategy

Run each sensor multiple times per workload:

- cold start with pre-existing processes already running
- warm start with sensor already attached
- burst workload immediately after sensor startup
- burst workload after 30 seconds stable runtime
- low load baseline
- high process churn load
- high CPU load
- high file/network event load

Record kernel version, distro, CPU count, page size, BTF availability, privilege mode, container/VM context, and sensor config for every run.

## Sensor Runner Requirements

For each sensor run, capture:

- exact command line and environment
- sensor version/commit
- kernel and OS metadata
- raw output files
- normalized output files
- stdout/stderr/journal logs
- loss/drop metrics
- start/stop timestamps
- workload manifest
- evaluator report

The runner should leave artifacts in a layout like:

```text
validation-runs/
  YYYYMMDD-HHMMSS-<sensor>-<workload>/
    manifest.json
    sensor-config.json
    raw/
    normalized/
    logs/
    metrics/
    report.json
    report.md
```

## Metrics To Compute

| Metric | Definition |
|---|---|
| fork recall | observed `process_fork` / expected fork-like creations |
| exec success recall | observed `exec_success` / expected successful execs |
| exec attempt recall | observed `exec_attempt` / expected attempted exec syscalls |
| exit recall | observed exits / expected exits |
| duplicate process starts | multiple start-like rows for one expected identity |
| parent join rate | child rows with correct parent identity |
| identity stability | same process lifecycle rows share one identity |
| PID reuse correctness | reused PID maps to different identities |
| owner attribution rate | file/network events mapped to expected process |
| unknown owner count | file/network rows with missing or unknown process |
| sensor-reported drops | ringbuf/perf/scap/queue drops by sensor |
| observed latency | event timestamp to output timestamp if available |

## Lintap-Specific Validation Checks

Check these explicitly for Lintap:

- `PROC_START_SRC=sched_exec` appears for successful exec lifecycle records.
- `PROC_START_SRC=execve_or_execveat FLAGS=...` appears for syscall breadcrumb records.
- `PARENT_HASH_SRC=ebpf` appears when parent `real_start_time` was used.
- `PARENT_HASH_SRC=proc` appears when parent identity came from `/proc` enrichment.
- `CloneFlags` are captured by BPF for clone/vfork cases, even if not yet surfaced downstream.
- Duplicate `PID_HASH` start-like rows are either expected and labeled or deduplicated in the evaluator.
- `ProcessRundownSensor` emits `Refresh` rather than `Start` for pre-existing processes.

## Likely Implementation Steps

1. Extract workload generation from `../wintap/devtools/process_capture_smoke_test.py` into a sensor-neutral script.

2. Define a manifest schema with run id, cases, expected process relationships, expected files, expected network activity, and timing windows.

3. Implement a Lintap runner first, using direct Parquet if available for easy DuckDB analysis.

4. Implement normalizers for Lintap, then Tetragon, Tracee, and Sysdig one at a time.

5. Add loss metric collection per sensor before comparing recall numbers.

6. Run low-load baselines on one known kernel and save reports.

7. Add burst and short-lived workloads after the baseline evaluator is stable.

8. Use findings to prioritize Lintap changes: clone flag surfacing, loss counters, dedupe/provenance, and parent identity improvements.

## Expected Early Lintap Fix Candidates

- Surface `CloneFlags` and vfork/clone provenance from `CloneSensor` output.
- Add first-class ringbuf/drop/backpressure metrics comparable to reference tools.
- Decide whether syscall-enter exec breadcrumbs should emit separate records or annotate/collapse into the `sched_process_exec` identity.
- Strengthen config gating around documented `WINTAP_ENABLE_<SENSOR>_SENSOR` names if those are still intended.
- Add evaluator checks for duplicate starts with same `PID_HASH`.

## Open Decisions

- Should the validation harness live in `../wintap/devtools`, this `Wintap-Analytics` repo, or a separate experiments directory?
- Should normalized comparison output use DuckDB tables, Parquet, JSONL, or all three?
- Should tool-specific sensor output be kept raw forever for reproducibility?
- Should Lintap validation target parity with best reference semantics, or explicitly preserve Wintap API compatibility first?
- Should the first baseline be bare-metal/VM Linux only, or include containerized sensors from the beginning?

## Suggested Next Session Prompt

Start by designing the manifest schema and workload generator API. Use `../wintap/devtools/process_capture_smoke_test.py` as the seed, but make it sensor-neutral. Produce a minimal workload that generates simple exec, fork-exec, execveat, short-lived burst, and pre-existing process cases, then write an evaluator skeleton for Lintap direct Parquet output.
