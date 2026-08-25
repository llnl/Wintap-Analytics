---
title: "Dev Handoff: Optimize FileOps Poller Event Volume"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: llm-agent
status: draft
source_paths: wiki/work/optimize-fileops-poller/dev_handoff.md
tags: [feature-work, file-events, ebpf, linux-sensor, dev-handoff]
---

# Dev Handoff: Optimize FileOps Poller Event Volume

## Phase 2 Status (2026-08-25)

The original scope was implemented to its current deployed state with
opencode gpt-5.5 and gpt-5.4. The feature stays open as phase 2 rather than
being closed or forked into a new feature. The deep analysis this handoff
called for was completed 2026-08-25 — see
[[wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25]]. Root cause of
the sustained overnight ring-buffer loss: the userspace consumer ceiling
(per-event DuckDB resolution under a process-global lock plus a synchronous
Esper send, all on the single poller thread), not kernel emission volume.

**Human approval received 2026-08-25** for the phase-2 plan and sequencing:
**fop-08 (+ fop-09) → fop-10 measurement → fop-11 go/no-go**. Two direction
updates came with it: (1) in-kernel short-interval aggregation is reopened as
gated candidate fop-11 (amending the 2026-08-24 no-aggregation direction),
motivated by suspected high same-(pid,path) open/openat redundancy and by the
fact that Esper aggregates later in the pipeline anyway; (2) additional memory
spend on userspace queues is explicitly acceptable — it is wanted for spike
absorption. An OSS sensor survey (Falco/Sysdig, Tetragon, Tracee, Elastic
ebpf, Sysmon for Linux, osquery) is saved as a future research task, runnable
in parallel.

**Post-fop-10 milestone (2026-08-25):** the deployed measurement slice now has
enough evidence to support a concrete `fop-11` review proposal rather than an
abstract candidate. See
[[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]]. The key gate
evidence is now recorded in verification: high duplicate-open ratios across
multiple intervals plus surviving queue-loss under some later load phases even
after sender-path improvements.

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development or deep-analysis agent:

    Switch to code-development mode for optimize-fileops-poller.
    You are explicitly authorized to modify ../wintap on the
    grantj-rhel8-testing branch (verify the branch before editing;
    do not commit to main/develop). Wiki and validation artifacts go
    in Wintap-Analytics, also on grantj-rhel8-testing.

    Read AGENTS.md first and confirm code-development mode is active.

    Use these files as the required handoff context, in this order:

    - wiki/work/optimize-fileops-poller/brief.md
    - wiki/work/optimize-fileops-poller/design.md
    - wiki/work/optimize-fileops-poller/implementation_plan.md
    - wiki/work/optimize-fileops-poller/dev_handoff.md
    - wiki/work/optimize-fileops-poller/verification.md

    Evidence base: the summary statistics recorded in verification.md and
    deep-analysis-2026-08-25.md. The raw diagnostics bundles
    (/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T033307Z and
    -20260825T142601Z) are no longer readable in this environment — by
    security constraint, only the summary statistics recorded in the wiki
    are available.

    Current state: this feature is no longer at the original fop-01/fop-02
    handoff stage. The branch and deployed RHEL8 host already include:

    - kernel + userspace FileOps counters and 60s log summaries
    - userspace dead-work removal (dead GenPidHash removal, memoized readlink
      fallback, no close fallback, scalar-first decode)
    - kernel self-PID filtering
    - wakeup batching with force-wakeup counters
    - CO-RE regular-file filtering for read/write/close/mmap
    - compact tagged fd-vs-path records
    - 16 MiB FileOps ring buffer
    - kernel pseudo-path filtering for open/openat/unlink/unlinkat
    - improved diagnostics bundle support in Wintap-Analytics

    Also read the root-cause analysis before coding:

    - wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25.md

    Goal for the next pass (human-approved 2026-08-25): implement fop-08 and
    fop-09 per the implementation plan's Phase 2 section — raise the userspace
    consumer ceiling. Do NOT start fop-11 (aggregation); it is gated on
    fop-10 measurement data and a separate human go/no-go.

    fop-08 scope:

    1. In-memory pid→pid_hash / process-identity cache for the File event
       path: maintained by ProcessResolver (populated at registration,
       evicted on exit/prune), consulted by EventChannel.Send instead of the
       per-event DuckDB SELECT under _dbLock; DB lookup remains only as the
       miss fallback. Cache hit/miss counters in the 60s log.
    2. Bounded in-process queue between the FileOps ring-buffer callback and
       resolve/Esper: the callback does decode+filter+enqueue only; a worker
       thread drains into resolve+Esper. Generous default capacity (memory
       spend approved), explicit depth gauge and drop counter in the 60s log,
       documented drop policy. Shutdown must drain within the existing 2s
       PollingThread.Join budget or document the revised budget.

    fop-09 scope: hoist the five per-event ConfigManager.GetValue lookups in
    EventChannel.Send into fields cached at startup.

    Acceptance for this pass:

    1. Builds: tracers make clean && make; dotnet build wintap/Lintap.csproj
       with 0 errors.
    2. Differential harness clean on regular-file tuples (no-loss gate).
    3. On the field host, under comparable load: ring_fail_total growth rate
       collapses versus the ~778/s baseline recorded in the deep analysis;
       queue depth/drop counters visible and bounded; FileOps-Poller thread
       CPU share drops. Record summary statistics in verification.md.
    4. Counter reconciliation: kernel emitted ≈ userspace consumed + ring
       drops + queue drops.

    Constraints:

    - Preserve the no-loss contract for regular-file telemetry.
    - Do not introduce aggregation or sampling in fop-08/09/10; aggregation
      is reserved for fop-11 and starts only after its gates are met
      (fop-10 duplicate-ratio evidence + explicit human go/no-go).
    - Do not commit or copy raw event data, sample payloads, or sensitive host
      artifacts into the repo. It is allowed and encouraged to record summary
      statistics, ratios, counter deltas, event counts, representative metric
      examples from log messages, and other non-sensitive derived measurements
      that help prioritize the next change.
    - Do not ignore the overnight evidence just because the first-minute smoke
      test looked clean.
    - If you make new code or validation changes, update verification.md,
      implementation_plan.md, and wiki/log.md.

## Current State

This feature started as a review-driven effort to cut FileOps event volume with
no information loss. It has since progressed through live iteration on the
RHEL8 field host and now has significantly better instrumentation and several
substantive volume-reduction changes already deployed.

The two most important field artifacts are:

- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T033307Z`
  - smoke test after redeploy
  - proved the new build was actually installed and loaded
  - first minute showed `ring_fail_total=0`
- `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T142601Z`
  - overnight run on the same deployed build
  - showed sustained ring-buffer loss still accumulates under long-running host load

## What Has Already Landed

Treat the following as implemented and field-observed, not speculative:

1. Counter scaffolding and observability
- kernel `fileops_stats`
- userspace per-op consumed/emitted/drop/fallback counters
- 60s `FileOps counters` log output
- diagnostics extraction of focused FileOps log lines
- deployed `Lintap.dll` and `*.bpf.o` fingerprint capture
- optional `bpftool` program/map/link capture

2. Userspace dead-work removal
- removed dead per-event `GenPidHash`
- memoized successful `/proc/<pid>/fd/<fd>` fallback results
- removed guaranteed-late close fallback
- scalar-first decode before allocating strings

3. Kernel-side reductions
- self-PID filter map and `self_drop_total`
- CO-RE regular-file filtering for `read`/`write`/`close`/`mmap`
- `nonregular_drop_total`
- compact tagged fd vs path records
- wakeup batching and `force_wakeup_total`
- ring buffer increased to 16 MiB
- kernel pseudo-path filtering for `open`/`openat`/`unlink`/`unlinkat`
- `pseudo_drop_total`

4. Validation harness
- `validation/fileops-differential/fileops_workload.py`
- `validation/fileops-differential/compare_fileops.py`
- comparator fails on missing regular-file `(pid, normalized_path, op)` tuples

## What The Field Data Says

### Smoke Test Outcome

- Build definitely deployed and loaded.
- FileOps tracepoints were attached.
- FileOps ring buffer was confirmed live at 16 MiB via `bpftool`.
- First-minute counters looked excellent:
  - `ring_fail_total=0`
  - large `pseudo_drop_total`
  - large `nonregular_drop_total`
  - `close:fallback_miss=0`

### Overnight Outcome

- Same deployed hashes remained installed overnight.
- The feature clearly removed huge amounts of waste before userspace.
- But long-run counters still showed large sustained ring-buffer loss in the
  surviving regular-file stream, especially for:
  - `open`
  - `read`
  - `close`
  - `mmap`
- FileOps remained the dominant named hot thread.

## Working Interpretation

This feature has already made a major practical improvement from where it
started:

- the pipeline is now measurable
- useless self-traffic is filtered in-kernel
- huge non-regular-fd volume is filtered in-kernel
- huge pseudo-path open volume is filtered in-kernel
- compact records and a larger ring buffer improved early burst behavior
- diagnostics can now prove exactly what was deployed and live

But the host is still not at a no-loss steady state. The deep analysis
(2026-08-25) traced the remaining loss to the userspace consumer ceiling, and
the phase-2 work below attacks that ceiling first.

## Approved Phase-2 Work (human sign-off 2026-08-25)

The four handoff questions — smoke-vs-overnight loss, dominant surviving
classes, next minimal no-loss change, incremental vs structural — are answered
in [[wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25]]. The human
approved the resulting plan in full. Sequence:

1. **fop-08 — raise the consumer ceiling (next code slice, approved).**
   Bounded in-process queue between the ring-buffer callback and
   resolve/Esper, plus an in-memory pid→pid_hash current-process cache that
   eliminates the per-event DuckDB query under the global `_dbLock`. Memory
   spend on the queue is explicitly acceptable — spike absorption is a goal,
   not a side effect. Loss accounting must get better, not worse: queue
   depth and drops are counted and logged.
2. **fop-09 — hoist per-event config lookups (approved, trivial).** Bundle
   with fop-08 or land immediately after.
3. **fop-10 — attribution + redundancy measurement (approved).** Top-N
   per-comm / per-path-prefix emit counters plus the open/openat
   duplicate-ratio statistic (repeats of same (pid, path) within a short
   window). Summary statistics only — no raw event data. This produces the
   evidence for the fop-11 gate.
4. **fop-11 — in-kernel short-interval aggregation (gated candidate).**
   Emit-first-then-count: first occurrence of a distinct (pid, op, identity)
   emits immediately as today; repeats increment a bounded LRU map and flush
   as per-interval summary counts (count, first/last ts, summed bytes).
   Gates before implementation: (a) fop-10 duplicate-ratio numbers prove the
   win, (b) explicit human go/no-go on the information tradeoff (per-repeat
   timestamps collapse to counts within the interval), (c) RHEL8 verifier
   spike for the in-kernel path-hash/map pattern, (d) redefined differential
   contract (distinct-tuple equality + count conservation) and a File schema
   repeat-count field flagged to downstream consumers.

Future task (parallel, research-only): the OSS sensor survey recorded in the
implementation plan's Phase-2 future tasks.

## Testing Expectations For Any Follow-On Code Slice

- `cd ../wintap/wintap/platform/linux/sensor/ebpf/tracers && make clean && make`
- `cd ../wintap && dotnet build wintap/Lintap.csproj`
- Differential harness runs clean on baseline-vs-candidate regular-file tuples
- Diagnostics bundle captures at least two consecutive `FileOps counters`
  intervals after deployment
- Verification must explain the reasoning from the observed counter deltas to
  the engineering conclusion, not just paste commands and outputs
- Verification should record summary statistics only, not raw event data:
  counts, rates, ratios, per-op deltas, representative counter lines, and
  other non-sensitive derived measurements are desired; sensitive payload data
  should stay out of the repo
