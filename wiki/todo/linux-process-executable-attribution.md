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
last_validated: 2026-11-04
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
