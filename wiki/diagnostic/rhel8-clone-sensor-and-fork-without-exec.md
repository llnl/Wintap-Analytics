---
title: "RHEL 8 Field Findings: Clone Sensor Attach and Fork-Without-Exec Warnings"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c
  - ../Lintap/packaging/lintap-rpm/lintap.env
policy: agent-editable
last_validated: 2026-08-14
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: mixed
status: draft
source_paths: wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec.md
tags: [lintap, ebpf, clone-sensor, process-events, rhel8, diagnostics, fork-without-exec]
---

# RHEL 8 Field Findings: Clone Sensor Attach and Fork-Without-Exec Warnings

Findings from the first real-machine (RHEL 8) Lintap test on 2026-08-14,
outside the Multipass/Ubuntu validation environment.

## Finding 1: The Fork-Without-Exec Warning Signature

A RHEL 8 run with the packaged sensor set (clone sensor disabled) produced a
high rate of `EventChannel.Send` warnings of two kinds:

```text
Could not resolve parent process (childPid=N, parentPid=N-1)
Could not resolve owner process for PID N (File)
```

Diagnostic pattern: in every parent-resolution failure observed,
`parentPid = childPid - 1` exactly. That is the signature of
**fork-without-exec** — a process forks a child (which receives the next
sequential PID) and the intermediate parent never execs, so the exec-based
sensors never register it. Shell pipelines and subshells produce this
constantly. The file-event owner failures are the same gap seen from the
other side: fork-only or very short-lived processes that are dead before the
resolver's live-`/proc` fallback can look them up.

This field signature matches the VM validation result from the
fix-unbounded-process-table-growth feature: clone-disabled runs missed
exactly the fork-without-exec population, and enabling the clone sensor
closed the live-coverage gap to 0 missing PIDs
([[wiki/work/fix-unbounded-process-table-growth/verification]]).

When triaging these warnings elsewhere, rule out the retention feature with
its own telemetry before blaming cleanup:

```bash
duckdb $WINTAP_DATA_ROOT/event_store/main.duckdb -c \
  "SELECT metric_name, count(*) FROM process_retention_telemetry GROUP BY 1;"
```

A near-zero `retention_miss` count means retention is not the cause.

## Finding 2: Clone Sensor Attaches Cleanly on RHEL 8

The packaged `lintap.env` ships `WINTAP_ENABLE_CLONE_SENSOR=false` with the
comment that `sched_process_fork` attach failed on Fedora during bring-up.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/lintap.env §CloneSensor remains opt-in -->

On the RHEL 8 test machine (2026-08-14), enabling the clone sensor attached
all three programs successfully:

```text
[CloneSensor.OnStarting]: CloneProcess attached 'trace_sys_enter_clone'
[CloneSensor.OnStarting]: CloneProcess attached 'trace_sys_enter_vfork'
```

plus the primary `sched_process_fork` tracepoint, whose success is silent by
design: `BaseEbpfSensor` logs only the failure case (`failed to attach
program`, Error level) and aborts sensor startup on failure — so the absence
of that error plus the `OnStarting` extras attaching is the success
confirmation.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §TryLoadBpfProgram -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §OnStarting -->

Consequence: the Fedora attach failure does not generalize. The opt-out
packaging default is now known to be overly conservative for at least
RHEL 8. Candidate action: revisit the `lintap.env` default (or at minimum
update its comment to name Fedora specifically), especially since both the
retention validation and this field test show the clone sensor is required
for accurate currentish-process tracking.

## Finding 3: Warnings Persisted After Clone Enable — Fork-Storm/Backlog Suspected

The warn stream continued at full rate ~7 minutes after the clone sensor
attached (samples at 3:50 and 4:02 on 2026-08-14). The 4:02 sample
interleaves ranges ~367k, ~419k, and ~516k in the same seconds; the 3:50
sample included PIDs at ~4,134,xxx — just below the systemd-era
`kernel.pid_max` of 4,194,304.

Rate analysis across the two samples: each range advanced at roughly
450–700 PIDs/second, and the ~4.13M range wrapped to low numbers. The most
economical explanation is a **single PID allocator moving at ~500–700
forks/second** (a fork storm on a nominally idle machine), with the
different event streams (process-parent vs. file-owner) observed at
different processing lags of minutes — which would also mean the post-enable
warnings may still be pre-enable backlog. The alternative explanation is
PID-namespaced (container) workloads with independent allocators. Decisive
checks below.

## Root Cause (identified 2026-08-14): pidstat-collector Self-Fork Storm

The raw_process parquet top-forkers query returned `bash` and `date` (both
root) — and the collector's own hot loop explains it exactly. For every line
of pidstat output, `pidstat-collector.sh` executes ~7 command-substitution
subshells, two of which fork+exec `date`
(`$(normalize_pidstat_line ...)` → `$(date '+%Y-%m-%d')`, plus `$(date +%s)`,
`$(window_start_for_epoch)`, `$(current_meta_path)` ×2,
`$(current_spool_path)`). With `-p ALL` emitting ~one line per host process
every 5 s (~100 lines/sec on this machine), that is ~700 forks/sec — matching
the measured PID-advance rate, the top-forker names, and even the warn
signature: each `$(...)` subshell is a fork-without-exec `bash` (PID X) that
forks `date` (PID X+1), producing the `parentPid = childPid − 1` pairs.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector.sh §run_collector, §normalize_pidstat_line -->

**The observability collector was flooding the sensor it feeds** — a
self-observation feedback loop. Consequences beyond log noise: raw_process
data from runs with the unfixed collector is polluted (bash/date dominate)
and should not be used for process-mix conclusions.

Fix (assigned to pidstat slice 2, merged with review finding 2): make the
hot loop fork-free — normalize into a global variable instead of `$(...)`,
use bash-builtin `printf '%(%s)T' -1` for epoch time, derive the date column
from the window-start epoch (also fixes the midnight bug), and replace path
helper substitutions with plain variables. Steady state then forks only one
`pidstat` plus one `duckdb` per rotation window.

## Open Items

- Confirm on the RHEL 8 machine: stop the collector, verify fork rate
  collapses (`/proc/stat processes` delta) and resolve warnings fade as the
  event backlog drains.
- Whether the multi-minute event-processing lag observed under the storm
  merits its own investigation (backpressure/ring-buffer behavior at
  ~700 process-events/sec) — relevant to sensor capacity planning even
  though this particular load was self-inflicted.
- `cat /proc/sys/kernel/pid_max` still worth recording (4,194,304 expected
  from the wrap evidence).
- At the observed rate, these Warn-level lines are themselves a log-growth
  problem for long runs (same theme as `raw/Issues/Long_Running_Cleanup.md`).
  Candidate: demote to Debug and count occurrences in
  `process_retention_telemetry` or a similar counter surface.
- The original Fedora `sched_process_fork` failure remains undiagnosed
  (kernel version? BTF availability?) — worth capturing the Fedora kernel
  details next time that environment is available.

## Related

- [[wiki/work/fix-unbounded-process-table-growth/verification]] - VM
  validation that identified the clone-sensor coverage requirement
- [[wiki/work/lintap-process-creation-validation/index]] - process-creation
  accuracy research thread
- [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] - cross-platform
  sensor compatibility tradeoffs
