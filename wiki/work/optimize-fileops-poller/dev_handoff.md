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

    Also read these diagnostics bundles directly:

    - /tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T033307Z
    - /tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T142601Z

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

    Goal for the next pass: perform a deep analysis of the completed work and
    identify the next highest-yield no-loss FileOps volume reduction. Use the
    overnight counter data as the primary evidence base.

    Required output from this pass:

    1. A precise summary of what has already landed in code and what has only
       been partially accepted.
    2. A quantified interpretation of the overnight counter trends
       (ring_fail_total, self_drop_total, nonregular_drop_total,
       pseudo_drop_total, force_wakeup_total).
    3. A ranked shortlist of the next no-loss reduction options, with expected
       upside, fidelity risk, and implementation complexity.
    4. A recommendation on whether to stay incremental in the current tracer/
       userspace design or pivot to a more structural change such as
       fentry/`bpf_d_path`.
    5. Concrete verification criteria for the next slice, reusing the existing
       differential harness and diagnostics collector.

    Constraints:

    - Preserve the no-loss contract for regular-file telemetry.
    - Do not introduce aggregation or sampling unless the human explicitly
      changes the feature scope.
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

But the host is still not at a no-loss steady state. The next useful task is
not another generic cleanup pass; it is a focused analysis of the surviving
regular-file volume that still drives `ring_fail_total` upward overnight.

## Recommended Next Task

Do a deep-analysis pass before choosing the next code change.

Questions that analysis should answer:

1. Why does the first-minute smoke test show no ring-fail while the overnight
   run still loses millions of events?
2. Which surviving regular-file classes likely dominate the remaining
   `open`/`read`/`close`/`mmap` pressure?
3. What is the next minimal no-loss change with the highest expected return?
4. Is it still worth staying incremental in the current tracer/userspace
   design, or is it time to consider a more structural move such as
   fentry/`bpf_d_path`?

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
