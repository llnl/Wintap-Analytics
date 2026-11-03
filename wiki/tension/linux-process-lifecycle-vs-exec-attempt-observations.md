---
title: "Tension: Linux Process Lifecycle vs Exec Attempt Observations"
type: tension
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c
policy: agent-editable
last_validated: 2026-11-03
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: mixed
status: open
source_paths: ../wintap/wintap/platform/linux/sensor/ebpf
resolution: null
poles:
  - "Use successful scheduler transitions for concise process/image lifecycle state, reducing redundant Start work and false success inference."
  - "Preserve syscall attempts and requested arguments for research, including failed execs that scheduler exec events do not describe."
tags: [tension, future-work, lintap, process-events, telemetry-semantics, syscalls]
---

# Tension: Linux Process Lifecycle vs Exec Attempt Observations

The current Linux Execve callback emits Start for both syscall entry and
`sched_process_exec`. Those sources describe an attempted operation and an
installed image, respectively; collapsing them can inflate birth counts or blur
failure/success. Discarding syscall observations would also discard useful intent
evidence. A process may exec multiple times under one identity.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c §trace_execve_entry, trace_sched_process_exec -->

## Holding pattern

Keep acquisition provenance and process-instance counts distinct from raw Start
rows. Investigate scheduler-primary lifecycle with separate attempt/image
observations, group-aware Stop meaning and bounded enrichment. No replacement or
schema contract has been selected; cost and fidelity need live comparison.
<!-- SPECULATIVE: hybrid observation/projection design awaiting experiment and explicit decision -->

Research baseline and comparison plan:
[[wiki/work/lintap-process-creation-validation/future-scheduler-lifecycle-vs-syscalls]].
Related boundary: [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]].
