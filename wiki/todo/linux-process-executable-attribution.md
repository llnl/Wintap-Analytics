---
title: "To-Do: Deterministic Linux Process Executable Attribution"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - wiki/work/lintap-process-creation-validation/validation-harness-design.md
policy: agent-editable
last_validated: 2026-11-23
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
**State:** Open — intake finding; deep dive not started.
**Likely next step:** Promote to a cross-repo feature investigation, then decide
whether the result is a bug fix, a model enhancement, or both. This intake does
not select the eventual process/image model.

## Finding

Linux process telemetry can contain multiple start-like observations for one
process lifetime. Syscall-entry observations record a requested executable
before the syscall outcome is known; `sched_process_exec` records a successful
image installation. Those are different facts and need to remain distinguishable.

The Wintap callback currently emits both observation types as process `Start`
messages and tags their provenance in `Process.Arguments`. It uses process start
time as `EventTime`, rather than the individual exec-observation timestamp.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §OnStarting, HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c §trace_execve_entry, trace_execveat_entry, trace_sched_process_exec -->

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

## Candidate two-layer direction

Treat the stable process lifetime and its changing executable image as
complementary views. Keep one deterministic representative image for the
process-lifetime row and expose its selected name as `process_name`; separately
retain the ordered detailed observations that explain how the process reached
that image. The representative still needs an explicit policy, such as initial
or latest successful image, and must select name/path from the same observation.

Candidate homes for the ordered detail are:

1. the existing `raw_process` observations plus a normalized ordered view;
2. a process attribute containing an ordered list of provenance/time/name/path
   tuples; or
3. a separate process-image/exec-observation table keyed to the stable process
   lifetime.

No storage shape or representative-image policy is selected yet. Compare query
ergonomics, schema evolution, Parquet/DuckDB behavior, cross-platform meaning,
and preservation of failed exec attempts before choosing among them.
<!-- HUMAN-REQUESTED: candidate direction from conversation 2026-11-23; not an accepted schema decision. -->

### Future refinement: open-source comparison

Investigate how other open-source tools model identity and mutable executable
state across repeated `exec`, beginning with Sysdig/Falco libraries, Cilium
Tetragon, osquery, and Tracee. Consider additional mature references such as
Elastic's Linux/eBPF process telemetry, Sysmon for Linux, and Linux Audit where
their event and state models are comparable.

For each tool, record:

- whether process identity remains stable across `exec`;
- whether the canonical process name is initial, current, latest, or event-local;
- whether failed exec attempts and successful image installation are distinct;
- what timestamps, sequence IDs, or parent-image links order repeated execs;
- whether current state and image history use one record, nested attributes, or
  separate event/entity tables; and
- how downstream queries avoid combining name and path from different
  observations.

Reuse the existing cross-sensor research thread rather than starting a duplicate
survey: [[wiki/work/lintap-process-creation-validation/index]] and
[[wiki/work/lintap-process-creation-validation/research-snapshot-2026-07-31]].
<!-- HUMAN-REQUESTED: future comparative research note, conversation 2026-11-23. -->

## Developer handoff

**Status:** Investigation and design handoff only. No schema, producer, DBT, or
historical-data change is authorized by this TODO.

**Goal:** Propose a two-layer process model that keeps a stable process-lifetime
identity, exposes one deterministic representative successful image as
`process_name`, and retains an ordered history of exec attempts and successful
image transitions.

### Read first

1. This TODO, especially the wrapper-to-`dd` example and candidate direction.
2. [[wiki/tension/linux-process-lifecycle-vs-exec-attempt-observations]].
3. [[wiki/work/lintap-process-creation-validation/validation-harness-design]].
4. The producer and current projection:
   `../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs`,
   `../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c`,
   and `../Wintap-PyUtil/wintap_dbt/models/silver/process.sql`.

### Investigation sequence

1. Measure repeated exec attempts, successful execs, and multi-name lifetimes in
   representative data without treating raw `Start` rows as process births.
2. Complete the open-source comparison described above, reusing the existing
   cross-sensor research thread.
3. Inventory the producer evidence available for ordering each observation.
   Process-birth `EventTime` alone is insufficient; identify any required event
   timestamp, monotonic time, sequence, source, and success fields.
4. Compare the three detail-storage options against DuckDB/Parquet queryability,
   compatibility, cross-platform semantics, and preservation of research evidence.
5. Present an explicit representative-image policy and migration/compatibility
   plan for human review before implementation.

### Minimum acceptance contracts for a proposal

- Repeated exec does not create a new process-lifetime identity.
- Failed attempts cannot become the representative successful executable.
- Representative name and path come from the same observation under a
  deterministic rule.
- Multiple successful image transitions can be ordered independently of process
  birth time.
- Raw intent evidence remains available without inflating process-birth counts.
- PID reuse remains distinct from repeated exec within one lifetime.
- Existing Windows semantics and historical raw data are not silently redefined.
- Fixtures cover failed lookup attempts, wrapper/interpreter transitions,
  multiple successful execs, PID reuse, and Stop after the final image.

**Expected deliverable:** A source-grounded design recommendation and fixture/data
measurement report. If implementation is selected, promote this TODO into a
feature folder and obtain approval for the chosen producer/model/schema changes.
<!-- HUMAN-REQUESTED: developer handoff added in conversation 2026-11-23. -->

## Suggested deep-dive work

1. Preserve the distinction between exec attempts and successful execs in the
   base model.
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

No model choice, schema change, implementation scope, or cross-repo code change
has been authorized by this intake entry. When promoted, follow
[[wiki/concept/llm-assisted-feature-workflow]] and link the resulting work folder
from [[wiki/todo/index]].
