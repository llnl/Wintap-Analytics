---
title: "To-Do: Improve Lintap Linux Process Command-Line Quality"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcessSensorHelper.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/data/duckdb/wintap.duckdb
  - ../Wintap-PyUtil/data/var/log/lintap/data/raw_sensor/raw_process/
policy: agent-editable
last_validated: 2026-11-04
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor; ../Wintap-PyUtil/wintap_dbt/models; ../Wintap-PyUtil/data
complexity: high
work_state: active
source_added: Human
priority: P1 — High (provisional)
tags: [lintap, linux, process-telemetry, data-quality, dbt, todo]
---

# To-Do: Improve Lintap Linux Process Command-Line Quality

**Priority:** P1 — High (provisional; the focused VM run reported a high blank
rate and process-level values with multiple distinct observations).
**State:** Active intake finding; deep-dive implementation not started.
**Complexity:** High.

## Goal

Resolve process command-line quality at its source and carry trustworthy
semantics through dbt. Do not make blank rates look better by filling missing
values with guesses or by adding a presentation-layer fallback. The sensor, raw
event contract, and process models should make it possible to tell what was
observed, when it was observed, and how reliable that observation is.
<!-- SYNTHESIS: recommended direction based on the sensor and dbt paths cited in grounded_by -->

## Observed problem

In the focused VM run, 2,707 of 3,309 materialized process records had blank
`args` (81.8%). Every one of those blank process records had only blank raw
`CommandLine` values; there was no evidence in this run that dbt turned an
available nonblank command line into a blank result. Raw `sched_exec` starts
were especially sparse: 2,386 of 2,420 had blank command lines. The underlying
raw data and materialized database are cited in `grounded_by`.
<!-- HUMAN-REPORTED: focused VM analysis and counts supplied with this to-do; referenced database and raw-data paths exist, but their contents were not independently re-queried for this intake update -->

On Linux, `ProcReader` obtains command-line text from `/proc/<pid>/cmdline`,
joins NUL-separated values with spaces, and leaves the field unset when it
cannot read the proc file. The sensor's process-object helper normalizes a null
command line to an empty string. `ExecveSensor` and process rundown use this proc
read; the clone sensor also has a parent-command-line fallback when the child's
value is empty. The syscall-entry BPF context exposes an `argv` pointer, but the
current process event is enriched from a later userspace `/proc` read rather
than projecting that vector into the event.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §ReadCmdline; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §CreateRefreshMessage; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c §trace_event_raw_sys_enter_execve -->

The bronze model aliases raw `CommandLine` to `ProcessArgs` when the latter is
absent. The silver model turns empty strings into null but then uses `any_value`
to select one value across observations of a process identity. In this run, 524
of the 602 nonblank process records had multiple distinct raw values, so a
nonblank result is not necessarily a stable or deterministic process-level
value. `num_args` also counts the raw empty string as one distinct value for
blank records.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql -->
<!-- HUMAN-REPORTED: focused VM analysis and counts supplied with this to-do; database contents were not independently queried for this intake update -->

## Developer approach

### 1. Define the data contract before changing the sensor

- Decide whether the canonical data is a structured `argv` vector (including
  `argv[0]`) or a display command-line string, and document any derived
  representation separately.
- Separate executable identity/path from arguments. Do not assume the first
  flattened token is a reliable executable path or that joining arguments with
  spaces is lossless.
- Distinguish a captured empty vector from not collected, unavailable, read
  failure, process-exited-before-read, and truncated/limited capture where the
  sensor can identify those outcomes.
- Record event source and observation time independently from process birth
  time. Keep fork/inherited state, exec attempts, successful execs, and rundown
  snapshots distinguishable.
<!-- SYNTHESIS: proposed contract based on current ProcReader, ExecveSensor, CloneSensor, and ProcessRundownSensor behavior -->

### 2. Capture process arguments at the appropriate sensor boundary

- Investigate bounded capture of `argv` at syscall entry, where the event
  context exposes it, instead of relying on a later read of mutable
  `/proc/<pid>/cmdline` for an exec observation.
- Correlate an exec attempt with kernel-confirmed execution success; retain
  attempt observations as attempts rather than silently treating them as the
  running image.
- Keep `/proc` reads as useful enrichment or rundown snapshots, but label their
  collection method and observation time so they cannot be confused with
  event-time arguments.
- Audit the clone fallback: parent command-line text must not be attributed as
  the child's own arguments. If inherited metadata is useful, represent it
  explicitly as inherited context.
- Add bounded-capture and drop/truncation diagnostics, plus reason-specific
  sensor counters. Avoid broad exception handling that makes a failed read
  indistinguishable from an observed empty value.
<!-- SYNTHESIS: implementation direction; the cited sensor files establish the current read/fallback paths and syscall argument pointer -->

### 3. Preserve observations and quality state through dbt

- Keep event-level process observations, source provenance, capture status, and
  timestamps in bronze rather than collapsing them prematurely.
- Model exec/image observations separately from a process-lifetime summary. A
  summary field should use a documented, deterministic rule (for example, a
  declared initial or latest successful image), not independent `any_value`
  selection.
- Preserve structured arguments if the chosen storage adapter supports them;
  if a string is also needed for display, derive it without replacing the source
  representation.
- Make null/empty/status handling explicit. Do not count an empty placeholder as
  one meaningful distinct argument value, and do not use parent or neighboring
  event values to mask missing capture.
- Add dbt tests for raw-to-bronze field/status preservation, uniqueness and
  ordering of exec observations, deterministic summary selection, and quality
  rates grouped by source and capture status.
<!-- SYNTHESIS: recommended dbt design based on the current staging alias and silver aggregation -->

### 4. Verify end to end with controlled Linux workloads

Build a VM test matrix with known argument vectors and expected event outcomes:
ordinary multi-argument execs, arguments containing spaces, fork followed by
exec, repeated execs in one process lifetime, very short-lived processes, empty
or unavailable proc reads, and capture limits. Compare the expected values with
sensor output, raw Parquet, bronze, and silver. Retain fixtures that prove
successful exec data is not replaced by an attempt, parent, or unrelated
observation.
<!-- SYNTHESIS: proposed verification plan -->

## Completion criteria

- Each process/exec observation carries its source, observation time, and a
  meaningful capture status; blank values are explainable rather than an
  undifferentiated outcome.
- Child command-line fields contain child observations only; inherited parent
  context, if retained, is labeled separately.
- Successful exec observations preserve their own captured arguments or
  explicitly state why capture was unavailable.
- dbt retains event-level evidence and produces any process-level selection
  deterministically under a documented semantic rule.
- Automated tests exercise the sensor-to-Parquet-to-dbt path and report
  completeness by event source and capture status.
<!-- SYNTHESIS: proposed acceptance criteria -->

## Decisions to settle during implementation

- Is the canonical value a full argv vector or a rendered command-line string,
  and does it include `argv[0]`?
- What should a process-lifetime summary mean when the process successfully
  execs more than once: initial image, latest observed successful image, or no
  single canonical image?
- Which Linux/kernel and eBPF constraints define the maximum captured argument
  count and bytes, and how will truncation be represented?
<!-- SPECULATIVE: these are unresolved contract and platform questions; the current source does not define the intended canonical semantics or capture limits -->

## Related findings

This work overlaps the process-lifetime summary and exec-provenance concern in
[[wiki/todo/linux-process-executable-attribution]]. Coordinate the model and QA
design during a future deep dive, while keeping command-line capture quality and
executable-path selection as separately testable outcomes.
The broader lifecycle-versus-attempt tradeoff is tracked in
[[wiki/tension/linux-process-lifecycle-vs-exec-attempt-observations]].

## Source references

- `../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs`
- `../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcessSensorHelper.cs`
- `../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs`
- `../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs`
- `../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs`
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c`
- `../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql`
- `../Wintap-PyUtil/wintap_dbt/models/silver/process.sql`
- `../Wintap-PyUtil/data/duckdb/wintap.duckdb`
- `../Wintap-PyUtil/data/var/log/lintap/data/raw_sensor/raw_process/`
