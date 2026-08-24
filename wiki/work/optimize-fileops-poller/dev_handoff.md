---
title: "Dev Handoff: Optimize FileOps Poller Event Volume"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
policy: agent-editable
last_validated: 2026-08-24
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

Use this prompt to hand the work to a code-development agent:

    Switch to code-development mode for optimize-fileops-poller.
    You are explicitly authorized to modify ../wintap on the
    grantj-rhel8-testing branch (verify the branch before editing;
    do not commit to main/develop). Wiki and validation artifacts go
    in Wintap-Analytics, also on grantj-rhel8-testing.

    Use these wiki files as the handoff context, in this order:

    - wiki/work/optimize-fileops-poller/brief.md
    - wiki/work/optimize-fileops-poller/design.md
    - wiki/work/optimize-fileops-poller/implementation_plan.md
    - wiki/work/optimize-fileops-poller/dev_handoff.md

    Goal: implement slice fop-01 (counters + baseline) and fop-02
    (userspace dead-work removal) per the implementation plan, with the
    A/B differential harness that proves no information loss.

    Before editing code, read AGENTS.md and confirm that code-development
    mode is active for this task.

## Handoff Summary

`FileOps-Poller` is the dominant hot thread on the RHEL8 field host. The
design ([[wiki/work/optimize-fileops-poller/design]]) identifies where
per-event cost is spent on guaranteed-discard or dead work, and prescribes
seven slices (fop-01..fop-07) that reduce event processing with **no
information loss** — aggregation is explicitly out of scope. Measurement
comes first: fop-01's counters and baseline are the evidence base for
everything else, including the socket/pipe-share number needed for the one
pending human decision.

## Primary Sources For The Dev Agent

- `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs` — the
  userspace pipeline; the `CountPseudoDrop`/`MaybeLogPseudoDrops` pattern is
  the model for new counters.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`
  and `file_ops_tracepoint.bpf.c` — near-identical today; keep them in sync
  for non-CO-RE changes (fop-03/04/06) and document any divergence.
- `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile` — two-tier
  build; fop-05 moves `file_ops_tracer.bpf.o` into `CORE_OBJS`.
- `../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs` — poll
  loop and fallback-object loading.
- `../wintap/wintap/core/infrastructure/EventChannel.cs` — proof that
  sensor-side `GenPidHash` is overwritten (fop-02 justification).
- `Wintap-Analytics/extras/lintap-runtime-diagnostics/` — field measurement.
- `Wintap-Analytics/validation/process-creation/` — the harness pattern to
  follow for the file-ops differential scenario.

## Recommended First Implementation Slice

fop-01 + fop-02 together:

1. Build the deterministic file workload + A/B differential harness under
   `Wintap-Analytics/validation/` (plan §Tests item 2) — you need it to
   prove fop-02 anyway, and it is the standing no-loss gate for all later
   slices.
2. Land kernel + userspace counters (both tracer variants) and capture the
   baseline (idle / workload / network-busy) on the RHEL8 host into
   verification.md — including the socket/pipe share of fd-op volume, which
   feeds the pending human decision for fop-05.
3. Land fop-02 (remove GenPidHash; memoize `/proc` fallback; skip fallback
   on close; zero-alloc decode) and run the differential + field
   measurement.

## Non-Goals For This Slice

- No kernel filtering yet (fop-03/05 land after counters exist to prove
  them).
- No ring-buffer format changes (fop-06).
- No aggregation, sampling, or op-class toggles — out of scope for the whole
  feature.
- Do not "fix" the socket/pipe emission in this slice; measure it. The
  decision gate is recorded in brief.md §Open Questions.

## Testing Expectations

Every slice must satisfy the matching items in implementation_plan.md
§Tests To Add Or Update. Minimum bar for this first slice:

- `make clean && make` in the tracers dir (both objects rebuilt and
  committed) and `dotnet build wintap/Lintap.csproj` with 0 errors.
- Differential harness runs green on baseline-vs-fop-02: regular-file event
  tuples (path, op, PID) equal; no new drops.
- Counter reconciliation holds (kernel emitted ≈ userspace consumed + ring
  drops).
- Decode unit tests for the existing record format (crafted buffers,
  truncated input) in a `../wintap/diagnostics/`-style console project or
  in-harness — your choice, record where.
- Baseline + post-fop-02 `collect-lintap-diagnostics.sh` runs archived and
  summarized in verification.md.

## Closeout Instructions

- Update wiki/work/optimize-fileops-poller/verification.md with commands run
  and results after every slice.
- Update the wiki/work/optimize-fileops-poller/implementation_plan.md done
  checklist as items complete.
- Append a concise entry to wiki/log.md for each substantial slice.
- Flag the socket/pipe decision to the human once the fop-01 numbers exist;
  do not start fop-05 before it is recorded in brief.md.
- Promote durable facts into canonical wiki pages once behavior stabilizes
  (see plan §Done Checklist closeout item).
