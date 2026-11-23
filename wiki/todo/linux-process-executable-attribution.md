---
title: "To-Do: Deterministic Linux Process Executable Attribution"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/shared/KernelTimestampConverter.cs
  - ../wintap/tests/Lintap.Tests/ProcessExecutionObservationTests.cs
  - ../wintap/developer_docs/audits/sfx-04-linux-exec-observation-kind.md
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - wiki/work/lintap-process-creation-validation/validation-harness-design.md
policy: agent-editable
last_validated: 2026-11-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor/ebpf; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; wiki/work/lintap-process-creation-validation
tags: [todo, priority, process-events, data-quality, telemetry-semantics, wintap, wintappy]
---

# To-Do: Deterministic Linux Process Executable Attribution

**Priority:** P1 — High (provisional; prioritize because the silver process row
can silently attribute an executable that did not run).
**State:** Promoted-partial. The bounded `sfx-04` sensor distinction is accepted;
deterministic process-lifetime selection and DBT changes remain open.

## Finding

Linux process telemetry can contain multiple start-like observations for one
process lifetime. Syscall-entry observations record a requested executable
before the syscall outcome is known; `sched_process_exec` records a successful
image installation. Those are different facts and need to remain distinguishable.

The Wintap callback emits both observation types as process `Start` messages and
tags their provenance in `Process.Arguments`. It keeps process birth as
`EventTime`; additive fields preserve the individual raw kernel observation and
converted UTC value separately. The accepted `sfx-04` slice now also labels
syscall entry as `ExecutionObservationKind=exec_attempt` and
`sched_process_exec` as `exec_success`.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §OnStarting, HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c §trace_execve_entry, trace_execveat_entry, trace_sched_process_exec -->

## Bounded sensor disposition — 2026-11-22

`sfx-04` adds nullable `ExecutionObservationKind` to the shared process object and
normal/direct Parquet. Linux syscall-entry exec observations use `exec_attempt`;
the successful scheduler image-install hook uses `exec_success`. Clone, Refresh
and unsupported producers remain null. Existing `ActivityType=Start`, identity,
executable name/path evidence, command-line provenance, timing and
`PROC_START_SRC` are unchanged.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs §ProcessObject; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §GetExecutionObservationKind, HandleEvent; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent -->

Focused tests pass 7/7, the combined sensor-fix suite passes 78/78, and the
bounded process-only gate passes 26/26 aggregate assertions. Across eight
controlled repeated-exec lifetimes, every case has one null fork, two attempts
and two successes with exact stage-one/stage-two path pairing and strict
observation ordering. All 24 fork-only controls and all Refresh rows remain null;
the optional field is present in all 98 Parquet files. This closes source-level
attempt-versus-installed-image ambiguity, not process-lifetime selection.
<!-- GROUND_TRUTH: ../wintap/developer_docs/audits/sfx-04-linux-exec-observation-kind.md; ../wintap/tests/Lintap.Tests/ProcessExecutionObservationTests.cs -->

The Wintappy silver process model groups observations by `pidhash` and uses
`any_value` independently for `process_name` and `process_path`, without using
the start-source provenance to select or pair them. An attempted but unsuccessful
exec target can therefore be selected as the reported path, and name/path may
come from different observations. `any_value` also supplies no explicit
deterministic ordering rule.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §process_base -->

Multiple successful execs within one process lifetime add a separate ambiguity:
the process-start `EventTime` does not order those image changes or establish
which successful image the base row should represent.

## Impact

The base process row may report an executable that was never successfully run,
or combine a process name and path from different observations. The current
projection therefore does not provide reliable canonical executable
attribution for a process lifetime. This is a source-level finding; its frequency
and impact in recorded datasets still need measurement.

## Example: wrapper script followed by `dd`

The following is a sanitized, reduced example from a user-provided `raw_process`
extract. The command was:

```text
datacrumbs_wrap dd if=/dev/zero of=/tmp/<output> bs=1M count=1 status=none
```

`datacrumbs_wrap` is a shell script that sets `LD_PRELOAD` and then runs:

```sh
exec "$@"
```

The relevant observations for one process identity can be summarized as:

| Source | Observed image/path | Interpretation |
|---|---|---|
| `sched_fork` | `bash` | Parent creates the child process and its new PID. |
| `sched_exec` | `datacrumbs_wrap` | The child replaces its inherited image with the wrapper script; this is not a new PID. The script's shebang may cause a shell interpreter to be loaded under the same PID. |
| `execve_or_execveat` | Several `dd` candidate paths | Exec syscall-entry observations while resolving the command through `PATH`; they do not by themselves prove successful execution. |
| `sched_exec` | `dd` | The wrapper's `exec "$@"` replaces the wrapper image with `dd`, preserving the PID and process identity. |
| `Stop` | Same process identity | The process lifetime ends. |

All of the Start observations shared one PID, one `PidHash`, one process-birth
`EventTime`, and one parent identity. The Stop retained the same PID and
`PidHash` but had its own termination `EventTime`. The raw `ActivityType=Start`
label therefore does not mean that every Start row is a distinct process birth.
It is carrying fork, exec attempt, and successful-image observations under the
same process-lifetime identity. The process-birth `EventTime` also cannot order
the individual exec observations.

This example makes the `ANY_VALUE` risk concrete: an unordered silver
aggregation grouped by `pidhash` could select `bash`, `datacrumbs_wrap`, `dd`,
or an attempted `dd` path as the representative executable. Independent
selection of `process_name` and `process_path` could also combine values from
different observations. A deterministic model must first define whether the
representative means the initial image, the latest successful image, or another
explicit process-lifetime view; this example does not select that policy.
<!-- SYNTHESIS: user-provided sanitized raw_process example interpreted using ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs, ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c, and ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql -->

### Timestamp precision follow-up

The explicit requirement and implemented additive candidate now live in
[[wiki/todo/process-observation-time-separate-from-birth]]. Preserve canonical
birth for identity independently of the finest available occurrence time;
additive timing preservation and migration of legacy `EventTime` semantics are
separate scopes. Exec/clone kernel timestamps now reach separate normal-ETL
observation fields in the source candidate; live qualification and the broader
executable-selection model remain open.

The same sample warrants a separate timestamp investigation. The Start rows
repeat `134394151359900000`, which is aligned to a much coarser boundary, while
the Stop row carries `134394151363910716` with finer 100-nanosecond FILETIME
precision. This may be intentional rather than ordinary truncation: the Linux
producer canonicalizes process birth times to the `/proc` clock-tick basis so
Clone, Execve, and rundown observations produce the same identity. Stop time is
reported as a termination/event timestamp and need not use that birth-time
normalization.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §TryConvertBootNsToUtc, NormalizeStartTimeUtc; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent -->

Open validation items are the host's effective `CLK_TCK`, the exact FILETIME
conversion for each Start source, whether the observed alignment is consistent
across captures, and whether any downstream logic incorrectly treats Start and
Stop timestamp precision as equivalent. Do not label this as confirmed data loss
until those source and host details are checked.

## Modeling questions

- Should the base process model represent a stable process lifetime, with exec
  attempts and successful image changes represented separately?
- If one path must represent the lifetime, should it mean the initial, latest,
  or current successful executable?
- What event timestamp or ordering evidence is needed to distinguish successive
  successful execs?
- Which provenance and time fields are available and reliable across raw Wintap
  events, recorded Parquet, and Wintappy's normalized model?

## Suggested deep-dive work

1. Consume the now-preserved distinction between exec attempts and successful
   execs without treating either raw-row count as process-birth count.
2. Define how successful image changes relate to a process-lifetime identity.
3. Retain per-exec ordering information separately from process start time.
4. Replace independent arbitrary selection of name and path with an explicit,
   deterministic rule that keeps them tied to the same observation.
5. Add QA fixtures for failed exec attempts, successful execs, multiple image
   changes within one lifetime, and consistent name/path selection.
6. Validate the rule against representative recorded data and document any
   compatibility implications before implementation.

The existing process validation design already models `exec_attempt` and
`exec_success` separately; reuse or extend its fixtures and normalization
guidance during the deep dive:
[[wiki/work/lintap-process-creation-validation/validation-harness-design]].
The broader unresolved lifecycle-versus-attempt tradeoff is tracked in
[[wiki/tension/linux-process-lifecycle-vs-exec-attempt-observations]].

## References

- `../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs` — hook
  attachment, event projection, source provenance, and process-start EventTime.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c`
  — syscall-entry and scheduler exec event producers.
- `../Wintap-PyUtil/wintap_dbt/models/silver/process.sql` — process aggregation
  and field selection.
- `wiki/work/lintap-process-creation-validation/validation-harness-design.md` —
  attempt-versus-success normalization and process QA design.

## Disposition

The additive sensor/projection distinction is accepted. No initial/latest image
policy, DBT implementation, historical repair, syscall-return correlation, or
separate lifecycle API has been selected. Continue through the active feature
workflow and preserve [[wiki/tension/linux-process-lifecycle-vs-exec-attempt-observations]].
