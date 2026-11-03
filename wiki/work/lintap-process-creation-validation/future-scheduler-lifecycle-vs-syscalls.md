---
title: "Future: Scheduler-Based Process Lifecycle vs Syscall Observations"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs
  - https://github.com/torvalds/linux/blob/v6.12/include/trace/events/sched.h
  - https://github.com/torvalds/linux/blob/v6.12/kernel/fork.c
  - https://github.com/torvalds/linux/blob/v6.12/fs/exec.c
  - https://github.com/torvalds/linux/blob/v6.12/kernel/exit.c
policy: agent-editable
last_validated: 2026-11-03
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: process
audience: mixed
status: draft
source_paths: ../wintap/wintap/platform/linux/sensor/ebpf; Linux v6.12 include/trace/events/sched.h, kernel/fork.c, fs/exec.c, kernel/exit.c
tags: [future-work, lintap, wintap, ebpf, process-events, lifecycle, syscalls, telemetry-semantics, performance]
---

# Future: Scheduler-Based Process Lifecycle vs Syscall Observations

## Research question

Should Linux process identity and lifecycle be driven by `sched_process_fork`,
`sched_process_exec`, and a **thread-group-aware** interpretation of
`sched_process_exit`, with syscall hooks retained for attempted operations and
argument provenance? What fidelity, overhead, and implementation costs would
that have compared with the current mixed acquisition path?

This is a future investigation, with a source-grounded baseline and an unmeasured
cost/benefit hypothesis. Wintap owns the Linux sensor implementation in `../wintap`;
Lintap hosts supporting Linux packaging/dev workflows; Wintap-Analytics hosts this
research record. Windows process collection uses kernel ETW, so the syscall
comparison here applies to the Linux sensor.
See [[wiki/event_type/process-events]] and
[[wiki/work/lintap-process-creation-validation/index]].

## What we actually use today

**The current Linux implementation already uses all three scheduler hooks.**
The comparison is a refinement of an existing hybrid, rather than introduction
of a wholly new mechanism.

Source snapshot: clean `../wintap` checkout on `develop`, HEAD `c29f973`, inspected
2026-11-03. This is source evidence, not proof of the objects/configuration running
on a deployed host. October feature-branch validation in the wiki is separately
dated evidence; re-establish its fixes and payload provenance on the branch chosen
for the experiment. In particular, this checkout's Clone ABI contains no child
start-time field, and Exit contains no start-time field, despite October notes
about a shared start-boottime reader.

| Observation | Current hook and behavior | Important qualification |
|---|---|---|
| Birth | CO-RE Clone uses `raw_tracepoint/sched_process_fork`; child `pid != tgid` is filtered before ring reservation, creator's TGID is emitted as parent. | Includes fork-without-exec; the record does not carry the child's actual kernel creation time. |
| Fallback birth | Ordinary `sched:sched_process_fork`, plus optional syscall-entry hooks for `clone`, `clone3`, and `vfork` flags. | Missing flags are ambiguous; userspace can misclassify threads as births. |
| Exec attempt | `sys_enter_execve` is primary; `sys_enter_execveat` is additionally attached. | Entry is an attempt, including operations that later fail. Filename is copied; argv/envp are not copied by these programs. |
| Exec image installed | Additionally attached `sched:sched_process_exec`; high-bit source marker distinguishes it. | Same callback emits `ActivityType=Start` for both attempts and scheduler exec observations. No syscall-return failure capture here. |
| Exit | `sched:sched_process_exit` in both tiers; CO-RE filters to `pid == tgid`, reads `task->exit_code`. | Leader exit is not necessarily final thread-group exit. Fallback emits task IDs and a placeholder zero status. |

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c §trace_process_fork; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c §trace_process_fork, auxiliary syscall programs; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §OnStarting, HandleEvent -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c §trace_execve_entry, trace_execveat_entry, trace_sched_process_exec; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §OnStarting, HandleEvent -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c §trace_process_exit; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracepoint.bpf.c §trace_process_exit -->

All three callbacks still depend on `/proc` for enrichment. Exec Start uses
creation time as `EventTime`, rather than its captured exec-observation time;
Exit Stop uses callback-time `DateTime.UtcNow`, rather than `TimestampNs`.
Changing hooks alone therefore does not establish an accurate image timeline
or remove short-lived-process enrichment races.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs §HandleEvent -->

The October Ubuntu experiment observed three Start records per fork+exec child
sharing one identity: fork, syscall entry, scheduler exec. Count process instances,
exec attempts, and installed images separately. See
[[wiki/work/improve-lintap-data-quality/clone-validation-results]].
The later RHEL canary record reports missing `sched_exec` provenance despite a
reported attachment; this remains a useful reproduction target, not evidence that
the hook is intrinsically unsuitable:
[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]].

## What the scheduler hooks mean

The kernel references below are pinned to **upstream Linux v6.12**, read on
2026-11-03. Validate the actual Ubuntu/RHEL kernel and backports in a later spike.

- **`sched_process_fork`: successful task creation on the `kernel_clone` path.**
  In that path it fires after `copy_process` succeeds and before `wake_up_new_task`.
  It covers ordinary fork/vfork/clone/clone3 creation through that path and avoids
  having to infer success from syscall entry. It also includes threads and kernel
  tasks; scope/filtering must be explicit. This is not a claim that every internal
  kernel `copy_process` caller emits it. Ordinary tracepoint fields expose task
  PIDs; the raw hook's parent/child pointers enable TGID and identity reads.
  The tracepoint's parent is the **creator** (`current`), which need not equal the
  child's `real_parent` under `CLONE_PARENT`; choose and document lineage meaning.
- **`sched_process_exec`: the new executable image has been installed.**
  `exec_binprm` emits it after successful binary-handler processing, including
  interpreter handling. It does not mean a new process was born or that the program
  executed user instructions or completed successfully. Failed attempts before
  installation produce no such event. Filename is `bprm->filename`, not a guaranteed
  resolved final executable path; scripts and fd-based exec need separate treatment.
- **`sched_process_exit`: an individual task is exiting through `do_exit`.**
  It covers normal exits and fatal-signal paths without requiring an `exit` syscall
  from the victim. It is neither task-free/reap time nor automatically process-wide
  termination. The ordinary payload has comm/PID/prio, not exit status or TGID.
  Kernel task/group state requires an additional kernel read or richer attachment.

<!-- GROUND_TRUTH: https://github.com/torvalds/linux/blob/v6.12/include/trace/events/sched.h §sched_process_fork, sched_process_exec, sched_process_exit; https://github.com/torvalds/linux/blob/v6.12/kernel/fork.c §kernel_clone; https://github.com/torvalds/linux/blob/v6.12/fs/exec.c §exec_binprm, alloc_bprm; https://github.com/torvalds/linux/blob/v6.12/kernel/exit.c §do_exit, do_group_exit -->

### Two lifecycle traps to test explicitly

1. **Leader exits before its workers.** A leader can call `pthread_exit` while
   other threads keep doing file/network work. Filtering Exit to `pid == tgid`
   avoids routine worker Stops but can close process identity too early. Upstream
   `do_exit` separately decrements `signal->live` to determine `group_dead` before
   firing the tracepoint. Investigate a last-live-thread/group-state rule and its
   concurrency/portability limits; a leader-only rule is not sufficient.
2. **A non-leader thread execs.** `de_thread` kills sibling threads and transfers
   the leader's PID and birthdate to the execing thread. `sched_process_exec.old_pid`
   records the old task PID. Today's exec context defines that field but does not
   export it. Correlation keyed only by TGID can confuse attempts from different
   threads; exec-induced sibling/leader exits must not terminate the continuing
   process identity.

<!-- GROUND_TRUTH: https://github.com/torvalds/linux/blob/v6.12/kernel/exit.c §do_exit, release_task; https://github.com/torvalds/linux/blob/v6.12/fs/exec.c §de_thread, exec_binprm; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c §trace_process_exit; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c §sched_process_exec_args, trace_sched_process_exec -->

## Costs and benefits

| Dimension | Scheduler lifecycle | Syscall observations | Implication for this sensor |
|---|---|---|---|
| Correctness | Birth and installed-image events describe achieved transitions; exit covers fatal signals too. | Entry preserves intent; fork/exec entry alone does not establish success. Exit syscall entry misses signal-driven termination. | Prefer scheduler evidence for lifecycle transitions; retain attempt evidence with its own meaning. |
| Research detail | Compact ordinary payloads; no argv/envp, full clone flags, exec errno, or ordinary exit-status field. | Can capture requested filename, argv/envp, dirfd/flags, clone flags and errors with entry/return correlation. | Scheduler-only loses useful failed-exec/intent evidence. Current argv population is `/proc`-based, so entry-time argv fidelity would be additional work. |
| Portability | Common kernel choke points reduce syscall-family/architecture branching. Raw/CO-RE enrichment still depends on supported kernel fields and attach modes. | Specific syscall availability and layouts differ across architectures and compat paths; clone3 needs user-structure reads. | Benchmark ordinary vs raw/CO-RE independently from scheduler vs syscall semantics. |
| Kernel cost | Minimal filtered records can be cheap; fork/exit programs still run for threads even when filtered before publication. | Selected syscall hooks run only for those calls, but attempts plus returns need additional hooks/maps/copies. | Neither mechanism is inherently cheaper. Payload size, hook count, filtering, map work and string reads determine cost. These are not `sched_switch` hooks running on every context switch. |
| End-to-end cost | Scheduler-primary projection can reduce redundant full Start enrichment and resolver/ETL work. | Keeping entry as another full Start duplicates that work on successful exec and also processes failures as Starts. | Savings may be mostly `/proc`, resolver, Esper and serialization, rather than attach-point dispatch. |
| State complexity | Needs group-aware termination, canonical creation time and cross-poller ordering. | Needs bounded pending-attempt maps, return correlation and cleanup for failures, exits and PID reuse. | Hybrid buys fidelity but needs explicit precedence, missing-observation handling and provenance. |

The cost assessment is a **hypothesis**, not a measured speedup. With all relevant
hooks active, a typical fork+exec+exit currently offers four ring records (fork,
entry, installed exec, exit); scheduler-only would offer three for that case.
Removing entry would halve exec records for a single successful exec, not halve
total sensor CPU. An enrichment-only hybrid could keep entry data in a bounded
kernel map and emit it with scheduler exec; preserving failed attempts still needs
a failure-output path. Compare equal-fidelity modes before claiming an optimization.
<!-- SYNTHESIS: inferred from the inspected clone/exec/exit tracer emit paths and userspace HandleEvent paths; performance requires measurement -->

## Proposed direction to investigate

**Scheduler-primary lifecycle with separately modeled syscall attempts/enrichment**
is the leading hypothesis. See the unresolved tradeoff in
[[wiki/tension/linux-process-lifecycle-vs-exec-attempt-observations]].

- Keep a stable process-instance identity across exec, anchored to actual creation
  time. Capture child/parent identity evidence at birth instead of assuming fork
  hook timestamp equals task creation time; use consistent host/namespace PID and
  clock domains across process, file and network sources.
- Record successful execs as image transitions with their own occurrence time and
  sequence. Preserve multiple real execs under one process identity; do not dedup
  every repeated Start by PidHash and discard the image history.
- Preserve syscall intent/attempt time separately. If failure visibility is wanted,
  capture negative returns with errno. Absence of a matching scheduler event alone
  cannot distinguish failure from loss or incomplete attachment.
- Define requested path, installed-image path, argv source, creator lineage,
  inherited birth metadata and credentials as distinct concepts. Bounded kernel
  capture reduces `/proc` races but introduces truncation/read-failure semantics.
- Resolve process Stop from group-aware kernel evidence, with kernel occurrence
  time and an explicitly encoded exit status/signal. Placeholder fallback zero
  must remain distinguishable from a confirmed successful exit.
- Retain startup rundown and reconciliation: hooks cannot recover processes that
  existed before attachment or all observations lost in transport.

These are proposed contracts, not implemented schema decisions. Normalized
WintapAPI events, resolver state, recorded Parquet and downstream Wintappy image/
process analysis must be checked separately. Preserve the shared identity contract:
[[wiki/decision/process-identity-attribution-contract]] and
[[wiki/decision/process-hash-inputs-and-single-definition]].
<!-- SPECULATIVE: future observation/projection contract and schema remain to be designed and validated -->

## Bounded comparison spike

### Modes

1. **Current hybrid baseline:** exact chosen commit, objects and enabled hooks;
   characterize its attempt/image/Start multiplicity before changing it.
2. **Scheduler-only lifecycle:** fork, exec and group-aware exit; report lost
   argument/failed-attempt visibility as part of the result.
3. **Scheduler-primary hybrid:** entry-time bounded intent/argv capture, scheduler
   successful-image emission, separately recorded failures where required.
4. **Syscall-derived reference:** qualified successful fork/clone returns, exec
   entry/return correlation and exit/exit_group entry. Treat signal-death coverage
   as a limitation of this mode. This is an experimental reference, not today's
   implementation.

Run both minimal-record hook comparisons and full normal-ETL comparisons. Hold
payload/enrichment constant in the minimal comparison so changing semantics is
not misreported as a raw-tracepoint performance win.

### Workloads and evidence

- Fork-only child doing file/network work; fork+exec; vfork/clone/clone3 processes;
  pthread/clone3 threads; worker-thread fork; CLONE_PARENT and reparenting.
- Failed exec (ENOENT/EACCES/ENOEXEC), repeated PATH-search attempts, repeated
  successful exec in one PID, script/interpreter, fd/empty-path `execveat` and
  memfd exec, including observable skip reasons where unsupported.
- Leader `pthread_exit` while workers continue; worker exit; worker exec;
  exit_group, SIGTERM/SIGKILL and crash/coredump termination.
- Millisecond-lived children, churn/fork storms, startup/restart rundown, PID reuse,
  PID namespaces/containers and suspend/resume clock consistency.

Use existing manifest/native workload assets where they exist; extend under a
later implementation task. Ground truth should include creator/child relationships,
TID/TGID, pre-exec attempt markers and parent-observed `waitpid`/`waitid` statuses;
`/proc` snapshots alone cannot enumerate millisecond-lived processes.
See [[wiki/work/lintap-process-creation-validation/validation-harness-design]] and
[[wiki/work/improve-lintap-data-quality/clone-validation-plan]].

Measure birth/image/attempt/Stop coverage separately; false thread births; premature
Stops; identity collisions and file/network orphans; argv/path/user completeness;
kernel-time-to-callback and durable-output latency; callback `/proc` reads; CPU,
RSS, allocations, BPF map occupancy, ring bytes/reservation failures and downstream
queue/serializer loss. Repeat matched idle, thread-heavy and fork/exec-heavy runs;
include observer cost and workload throughput/latency.

Record kernel/architecture/BTF, commit/object hashes and actual hook outcomes using
[[wiki/schema/runtime-capability-receipt]]. Existing process tracer reservation
failure branches silently return; per-hook hit/filtered/emitted/reserve-failure
counters are needed for a meaningful absence/overhead comparison. Validate Ubuntu
arm64 and native RHEL x86_64 separately, including supported fallback tiers.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c §trace_process_fork; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c §ring reservation branches; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c §trace_process_exit -->

### Decision output

A recommendation should include a semantic coverage matrix, stage-by-stage cost
comparison, fallback behavior and a proposed process/image/attempt projection.
Set workload fidelity and resource budgets before judging results. Adoption needs
evidence of complete declared lifecycle coverage, no premature process closure,
stable cross-domain attribution and bounded state under stress. Report any measured
tradeoff in failed-attempt/argument visibility explicitly.

**Status:** source review complete; prototype, live benchmark, schema decision and
implementation remain future work.

## Kernel references

- [Tracepoint definitions](https://github.com/torvalds/linux/blob/v6.12/include/trace/events/sched.h): ordinary fields and raw arguments.
- [Fork path](https://github.com/torvalds/linux/blob/v6.12/kernel/fork.c): `kernel_clone`, success and pre-wakeup placement.
- [Exec path](https://github.com/torvalds/linux/blob/v6.12/fs/exec.c): `alloc_bprm`, `de_thread`, `exec_binprm`, `bprm_execve`.
- [Exit path](https://github.com/torvalds/linux/blob/v6.12/kernel/exit.c): `do_exit`, `do_group_exit`, `release_task`, wait-status decoding.
