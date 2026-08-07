---
title: "Research Thread: Lintap Process Creation Validation"
type: workflow
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../../tetragon/bpf/process/bpf_execve_event.c
  - ../../tracee/pkg/ebpf/c/tracee.bpf.c
  - ../../sysdig/userspace/sysdig/utils/sinsp_opener.cpp
policy: agent-editable
last_validated: 2026-07-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: researcher
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor/ebpf; ../../tetragon; ../../tracee; ../../sysdig
tags: [wintap, lintap, ebpf, process-events, telemetry-semantics, research-workflows, validation, cross-repo]
---

# Research Thread: Lintap Process Creation Validation

This work thread tracks the long-running research effort to compare Lintap process-creation telemetry against Tetragon, Tracee, and Sysdig/Falco-style capture, then build validation workloads that can quantify accuracy, loss, and semantic differences.

This thread is intentionally separate from canonical `wiki/event_type/process-events.md` until findings are repeatedly validated. Durable conclusions can be promoted later.

## Pages

- [[wiki/work/lintap-process-creation-validation/research-snapshot-2026-07-31]] captures the first cross-tool process creation accuracy snapshot.
- [[wiki/work/lintap-process-creation-validation/handoff-validation-next-steps]] lays out the next engineering/research steps for known-workload validation across sensors.
- [[wiki/work/lintap-process-creation-validation/validation-harness-design]] proposes a concrete sensor-neutral manifest, normalized event schema, workload matrix, evaluator metrics, and first implementation slice.
- [[wiki/work/lintap-process-creation-validation/linux-setup]] describes UTM/Multipass Linux VM setup for running Lintap/reference-sensor validation from a Mac.
- [[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]] summarizes the latest committed state, validation results, open problems, and recommended next steps.

## Current Scope

- Canonical Lintap source is `../wintap` on the current Linux/eBPF work branch, not the legacy `../Lintap` Sysdig/chisel repository.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c §exec hooks -->

- Reference implementations are local checkouts at `../../tetragon`, `../../tracee`, and `../../sysdig` from the perspective of this wiki repository.
<!-- SYNTHESIS: user-provided repo scope plus local source inspection -->

- The immediate validation target is process creation semantics: fork/clone/vfork, exec attempts, successful exec lifecycle, startup rundown, short-lived processes, PID reuse, and parent attribution.
<!-- SYNTHESIS: inferred from comparison of ../wintap/wintap/platform/linux/sensor/ebpf, ../../tetragon/bpf/process, ../../tracee/pkg/ebpf/c, and ../../sysdig/userspace/sysdig -->

## Open Research Questions

- Which event family should be treated as canonical Lintap `Process Start`: `sched_process_exec`, `sched_process_fork`, syscall-enter exec, or a deduplicated fusion?
- How should Lintap preserve provenance without producing duplicate downstream process rows for the same PID/start-time identity?
- Which short-lived process patterns are measurable enough to become regression tests?
- What loss counters and backpressure signals are required before comparing performance or accuracy numbers across sensors?
- Can Lintap expose clone/vfork flags and lifecycle provenance without destabilizing WintapAPI process semantics?
