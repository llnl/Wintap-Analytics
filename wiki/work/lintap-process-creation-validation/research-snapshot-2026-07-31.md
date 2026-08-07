---
title: "Research Snapshot: Process Creation Accuracy Across Lintap, Tetragon, Tracee, and Sysdig"
type: workflow
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs
  - ../wintap/wintap/core/shared/ProcessHash.cs
  - ../../tetragon/bpf/process/bpf_execve_event.c
  - ../../tetragon/bpf/process/bpf_fork.c
  - ../../tetragon/pkg/sensors/exec/procevents/proc_reader.go
  - ../../tracee/pkg/ebpf/c/tracee.bpf.c
  - ../../tracee/pkg/datastores/process/proctree.go
  - ../../tracee/pkg/datastores/process/taskid.go
  - ../../sysdig/userspace/sysdig/utils/sinsp_opener.cpp
  - ../../sysdig/userspace/sysdig/sysdig.cpp
policy: agent-editable
last_validated: 2026-07-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: researcher
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor/ebpf; ../../tetragon; ../../tracee; ../../sysdig
tags: [wintap, lintap, ebpf, tetragon, tracee, sysdig, process-events, validation, pid-hash]
---

# Research Snapshot: Process Creation Accuracy Across Lintap, Tetragon, Tracee, and Sysdig

Snapshot date: 2026-07-31.

This page preserves the first deep planning/review pass on accurate Linux process-creation telemetry across Lintap, Tetragon, Tracee, and Sysdig/Falco-style capture. It is a research snapshot, not a final design decision.

## Executive Summary

Accurate process creation collection is not one event. It is a reconciliation problem across multiple signals with different semantics and failure modes.

The common mature pattern is:

| Signal | Meaning | Typical Weakness |
|---|---|---|
| `sys_enter_execve` / `sys_enter_execveat` | attempted exec and raw syscall path/flags | fires before success is known |
| `sched_process_exec` | successful process image replacement | does not show failed exec attempts |
| `sched_process_fork` / `wake_up_new_task` | task/process creation before exec | clone/thread semantics are subtle |
| exit hook | close process lifetime and prevent stale PID identity | drops cause stale cache entries |
| `/proc` scan | startup baseline and enrichment | racy for short-lived processes and reparenting |
| process cache or resolver | PID reuse and parent attribution | can be stale, lossy, or capacity-limited |

No inspected project can guarantee 100% capture under all load and timing conditions. The strongest designs expose loss, preserve lifecycle provenance, key process identity with PID plus start time, and avoid depending on `/proc` as the live event trigger.

## Current Lintap Baseline

Canonical Lintap for this research is the Linux/eBPF implementation in `../wintap`, not the legacy `../Lintap` Sysdig/chisel repo.

Current Wintap branch inspected:

```text
grantj-ebf-fixes @ 7f932558e5d3f83ec77978f71b8a5588648ecd04
```

Lintap process acquisition uses syscall breadcrumbs, successful exec lifecycle, fork lifecycle, and `/proc` rundown.
<!-- SYNTHESIS: inferred from ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c, ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c, and ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs -->

| Event Family | Lintap Source | Reference |
|---|---|---|
| exec attempt | `tracepoint/syscalls/sys_enter_execve` | `../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c` |
| execveat attempt | `tracepoint/syscalls/sys_enter_execveat` | `../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c` |
| successful exec lifecycle | `tracepoint/sched/sched_process_exec` | `../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c` |
| fork/clone/vfork lifecycle | `tracepoint/sched/sched_process_fork` | `../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c` |
| clone flags breadcrumb | `tracepoint/syscalls/sys_enter_clone` | `../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c` |
| vfork breadcrumb | `tracepoint/syscalls/sys_enter_vfork` | `../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c` |
| startup baseline | `/proc` enumeration via `ProcessRundownSensor` | `../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs` |

Lintap uses BPF ring buffers for eBPF-to-userspace transport.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c §events map -->

`ExecveSensor` attaches the primary `trace_execve_entry` program and then attaches extra sections for `execveat` and `sched_process_exec` when present.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §OnStarting -->

`CloneSensor` attaches `trace_process_fork` and then best-effort syscall sections for `clone` and `vfork` flags.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §OnStarting -->

`/proc` is used for enrichment and startup rundown, not as the live trigger for process creation.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs §ReadProcessInfo -->

Lintap process uniqueness uses Wintap `PID_HASH`, computed from PID, process start time, hostname, agent id, and process identity context. Current Linux process events attempt to use process start time so PID reuse produces distinct identities.
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ProcessHash.cs §GenPidHash -->

The most interesting Lintap technique is eBPF parent identity capture. The CO-RE exec tracer reads parent PID, parent comm, and parent `real_start_time`, so userspace can compute a parent hash even if `/proc/<ppid>` is gone by callback time.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c §parent real_start_time -->

Current Lintap risk notes:

- `CloneSensor` attach to `sched_process_fork` has been documented as failing with libbpf `-EACCES` in some Fedora environments.
- Multiple exec sources can produce multiple `Start` records for the same process identity unless downstream deduplication is explicit.
- `CloneFlags` are captured in BPF and represented in the C# struct, but are not yet surfaced into Wintap process output.
- `/proc` enrichment remains racy for short-lived processes.
- Loss/drop visibility is less mature than Tetragon, Tracee, or Sysdig/Falco libs.
<!-- SYNTHESIS: inferred from ../wintap/fedora-handoff-2026-06.md, ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs, and cross-tool comparison -->

## Cross-Tool Comparison

| Tool | Live Exec Source | Live Fork/Clone Source | Startup Existing Processes | Transport | Process Identity | Notable Technique |
|---|---|---|---|---|---|---|
| Lintap | `sys_enter_execve`, `sys_enter_execveat`, `sched_process_exec` | `sched_process_fork`, plus clone/vfork breadcrumbs | `/proc` rundown refresh | BPF ring buffer | `PID_HASH = pid + process start time + host + agent` | eBPF parent `real_start_time` for parent hash |
| Tetragon | raw tracepoint attached to `sched_process_exec` | kprobe `wake_up_new_task` | `/proc` scan seeds `execve_map` and emits synthetic events | perf/ringbuf depending config | `exec_id = base64(node:ktime:pid)` | BPF `execve_map`, userspace process cache, retry event cache |
| Tracee | `sched_process_exec`; syscall exec path for failures/attempts | raw tracepoint `sched_process_fork` | async procfs process tree feed | perf event arrays | entity hash from PID/TID + task start time | dual regular-event and control-plane signal streams |
| Sysdig/Falco libs | kmod/eBPF/modern BPF; modern uses `sched_process_exec` | kmod/eBPF/modern BPF; modern uses `sched_process_fork` | `/proc` process table scan | kmod ring/perf/ringbuf by engine | mutable `sinsp_threadinfo` with clone/start/ns metadata | mature state reconstruction and lifecycle-specific drop counters |

## Tetragon Notes

Tetragon uses PID plus kernel start time (`ktime`) as the durable identity. Linux `exec_id` is base64 of node name, ktime, and pid.
<!-- GROUND_TRUTH: ../../tetragon/pkg/process/process_id_linux.go §exec_id -->

Fork/clone acquisition uses `wake_up_new_task`, and exec acquisition uses a raw tracepoint configured for `sched_process_exec`.
<!-- GROUND_TRUTH: ../../tetragon/bpf/process/bpf_fork.c §event_wake_up_new_task -->

Important Tetragon correctness properties:

- Fork handling depends on parent state already being in `execve_map`; otherwise child creation may be skipped.
- Startup `/proc` scan seeds `execve_map` and emits procfs-derived exec events for already-running processes.
- Userspace process cache and event retry cache mitigate incomplete pod/process/ancestor data only after events reach userspace.
- Ring/perf buffer and userspace queue loss are explicitly counted.
<!-- SYNTHESIS: inferred from ../../tetragon/bpf/process/bpf_fork.c, ../../tetragon/pkg/sensors/exec/procevents/proc_reader.go, and ../../tetragon/pkg/eventcache/eventcache.go -->

Issue references captured during research:

- <https://github.com/cilium/tetragon/issues/4821> reports high-load missed BPF/ringbuf events and queue losses.
- <https://github.com/cilium/tetragon/issues/4883> reports partial procfs snapshot causing attribution loss.
- <https://github.com/cilium/tetragon/issues/2257> reports host procfs mismatch warnings in Mac/arm64 environments.
- <https://github.com/cilium/tetragon/issues/5026> and <https://github.com/cilium/tetragon/issues/4992> cover ringbuf map creation failures on ARM64 page-size variants.
- <https://github.com/cilium/tetragon/issues/1209> covers startup event flood/filter timing.
- <https://github.com/cilium/tetragon/pull/757> covers retrying when a process is not yet in cache.

## Tracee Notes

Tracee separates regular lifecycle events from control-plane process signals. The process store can be fed by both paths, with regular events providing synchronous updates and control-plane signals providing asynchronous enrichment.
<!-- GROUND_TRUTH: ../../tracee/pkg/cmd/flags/stores.go §SourceBoth -->

Tracee uses `sched_process_fork` and `sched_process_exec` for lifecycle events and separate syscall paths for exec attempts/failures.
<!-- GROUND_TRUTH: ../../tracee/pkg/ebpf/c/tracee.bpf.c §sched_process_exec -->

Tracee identity hashes PID/TID plus task start time. This directly addresses PID reuse when time conversion is consistent.
<!-- GROUND_TRUTH: ../../tracee/pkg/datastores/process/taskid.go §HashTaskID -->

Important Tracee correctness properties:

- Startup procfs feed can initialize process tree for existing processes.
- Lost perf-buffer events are counted/logged, but control-plane signal loss is a separate concern.
- Previous bugs around inconsistent procfs/kernel time conversion caused identity and parent attribution mismatches.
- The process tree has special handling for thread-group leaders and parent process versus immediate parent task.
- `execve()` from non-leader thread is an explicit edge case with incomplete process-tree handling.
<!-- SYNTHESIS: inferred from ../../tracee/pkg/ebpf/c/tracee.bpf.c, ../../tracee/pkg/datastores/process/proctree.go, and public Tracee PR/issue references -->

Issue and PR references captured during research:

- <https://github.com/aquasecurity/tracee/issues/4868> covers inconsistent process hash calculation between procfs and kernel signals.
- <https://github.com/aquasecurity/tracee/pull/4873> fixes consistent process hash calculation.
- <https://github.com/aquasecurity/tracee/pull/5053> fixes clock-base and stale procfs-data behavior.
- <https://github.com/aquasecurity/tracee/pull/4884> removes a queue/cache stage that did not solve sustained perf-buffer drops.
- <https://github.com/aquasecurity/tracee/issues/3988> discusses procfs recovery overhead under high load.
- <https://github.com/aquasecurity/tracee/pull/5191> removes runtime procfs querying while keeping startup initialization.
- <https://github.com/aquasecurity/tracee/pull/927> discusses process-tree build timing versus probe attachment.
- <https://github.com/aquasecurity/tracee/pull/1839> introduces task start time into event context for PID reuse.

## Sysdig / Falco Libs Notes

Sysdig selects among savefile, plugin, gVisor, modern BPF, classic BPF, and default kernel-module capture paths.
<!-- GROUND_TRUTH: ../../sysdig/userspace/sysdig/utils/sinsp_opener.cpp §open -->

The local Sysdig checkout pins `falcosecurity/libs` version `0.22.2` through CMake rather than vendoring the low-level source.
<!-- GROUND_TRUTH: ../../sysdig/cmake/modules/falcosecurity-libs.cmake §FALCOSECURITY_LIBS_VERSION -->

Sysdig/Falco libs maintain a mutable process/thread table rather than immutable Wintap-style process IDs. It uses TID/PID, parent fields, clone timestamps, namespace fields, executable metadata, and stale-entry repair heuristics.
<!-- SYNTHESIS: inferred from falcosecurity/libs@0.22.2 userspace/libsinsp/threadinfo.h and parsers.cpp via local temporary inspection; cite upstream if promoted -->

Important Sysdig/Falco correctness properties:

- Modern BPF uses scheduler lifecycle tracepoints to synthesize Sysdig/Falco event shapes.
- Lifecycle-specific drop counters exist for clone/fork/exit, execve exit, and proc exit.
- Filtering before state parsing can drop state-changing events needed for correct process/FD reconstruction.
- Startup `/proc` scans are inherently racy and can skip disappeared processes.
- Short-lived process/container ordering has caused memory leaks and stale thread table behavior.
<!-- SYNTHESIS: inferred from ../../sysdig/userspace/sysdig/sysdig.cpp and falcosecurity/libs@0.22.2 local source inspection -->

Issue and PR references captured during research:

- <https://github.com/falcosecurity/falco/issues/3822> reports high-load modern eBPF drops and livelock-like behavior.
- <https://github.com/falcosecurity/libs/issues/1557> requests conditional kernel-side filtering due high drops.
- <https://github.com/falcosecurity/falco/issues/3664> covers short-lived containers and memory growth.
- <https://github.com/falcosecurity/libs/pull/2629> mitigates clone-related leak from event ordering.
- <https://github.com/falcosecurity/libs/issues/2887> reports memory leak while using libsinsp BPF.
- <https://github.com/falcosecurity/libs/issues/2819> covers stale FD state after exec due missing CLOEXEC handling.
- <https://github.com/falcosecurity/libs/issues/1011> covers stale `proc.name` after thread rename.
- <https://github.com/falcosecurity/libs/pull/2884> fixes savefile proc table ordering/callback behavior.

## Shared Accuracy Failure Modes

| Failure Mode | Why It Matters | Observed In |
|---|---|---|
| ring/perf buffer loss | lifecycle events never reach userspace | Tetragon, Tracee, Sysdig; Wintap should add stronger metrics |
| short-lived process race | `/proc` enrichment sees nothing or sees reparented state | all four |
| startup race | process starts/exits between scan and probe attach | Tetragon, Tracee, Sysdig, Wintap rundown |
| PID reuse | PID alone is insufficient | all four handle with start time or heuristics |
| fork/clone/thread ambiguity | clone may create process-like or thread-like tasks | all four |
| parent exit before enrichment | parent hash/name can be lost | all four; Wintap eBPF parent start time helps |
| filtering/backpressure | state-changing events can be dropped before state tables update | Sysdig explicitly; all pipelines conceptually |
| duplicate lifecycle records | syscall-enter plus sched exec can emit multiple rows | Wintap, Sysdig-style synthesized events, Tracee separate syscall/lifecycle events |

## Semantic Vocabulary For Future Tests

Use these labels instead of a single overloaded `process creation` term:

- `fork_lifecycle`: child task/process created from parent.
- `clone_lifecycle`: clone-created task/process, with flags if available.
- `vfork_lifecycle`: vfork-specific clone case.
- `exec_attempt`: syscall-enter exec/execveat observed.
- `exec_success`: post-exec lifecycle event from `sched_process_exec`.
- `process_rundown`: already-running process observed from `/proc` at sensor startup.
- `process_exit`: process/thread-group lifetime ended.
- `identity_join`: association of lifecycle events into one process identity.
- `parent_join`: association of process identity to parent identity.
- `owner_join`: association of file/network events to process identity.

## Research Conclusions To Carry Forward

- Treat `sched_process_exec` as the authoritative successful exec lifecycle source.
- Preserve syscall-enter exec/execveat as attempt breadcrumbs and path/flags evidence.
- Preserve `sched_process_fork` as the authoritative fork/clone lifecycle source when attach succeeds.
- Preserve `/proc` records as rundown/enrichment with lower confidence than live eBPF lifecycle events.
- Key process identity by PID plus kernel/proc start time, never PID alone.
- Capture and expose loss metrics before comparing accuracy or performance.
- Validation must measure counts, identity joins, parent joins, duplicate starts, unknown owners, and sensor drop counters.
