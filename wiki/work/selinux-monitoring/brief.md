---
title: "Feature Brief: SELinux Monitoring"
type: concept
confidence: high
grounded_by:
  - wiki/work/selinux-monitoring/interview.md
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/
  - ../Lintap/sql/selinux.sql
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/selinux-monitoring/brief.md
tags: [feature-work, selinux, lintap, ebpf, avc, telemetry-semantics]
---

# Feature Brief: SELinux Monitoring

## Problem

There is no way to observe, in real time, whether SELinux policies on a host
are behaving as expected. Verifying policy today means manually digging
through auditd/ausearch output after the fact, and the ecosystem's only
SELinux artifact is a superseded batch POC (auditd TSVs → parquet → manual
DuckDB SQL) whose collector was never committed and whose joins are known to
be lossy (~40% unjoined rows, TZ misalignment).
<!-- GROUND_TRUTH: ../Lintap/sql/selinux.sql §Known issues comment -->

What's missing is the ability to monitor the *interactions between SELinux
contexts* — which source contexts act on which target contexts, with which
operations — as system events happen, so that policy gaps, unexpected
transitions, and mislabeled objects surface while they occur.

## Goals

- Make SELinux telemetry a **first-class Lintap event domain**: captured
  in-kernel via eBPF and flowing in parallel with the existing
  process/file/network streams through the standard sensor pipeline
  (tracer → C# sensor → EventChannel → Esper → serializer → `raw_sensor`
  parquet).
- Capture, by purpose:
  - **Debugging policy:** AVC decisions — denials always; audited grants
    where available.
  - **Monitoring policy:** domain/context transitions, and the allow-side
    **context-interaction map** (source context × target context × class ×
    permission), volume-bounded by novel-tuple dedup with periodic count
    flushes.
  - **Label/drift visibility:** unexpected or mislabeled contexts observable
    from the landed data (derived; own capture path only if the design finds
    it necessary).
- Keep sensor overhead and loss within the established health invariants
  (`ring_fail_total=0` style) alongside the existing tracers.

## Non-Goals

- No monitoring dashboard/UX in this feature — the landed, queryable streams
  are the deliverable; visualization is a follow-up feature.
- No Wintappy DBT models in v1 — `raw_sensor` parquet is the downstream
  boundary.
- No changes to the legacy auditd batch path
  (`../Lintap/merge_raw_tsv.sh` SELinux loop, `../Lintap/sql/selinux.sql`) —
  it remains as the documented superseded POC.
- No RHEL 8 (kernel 4.18) support in v1.
- No auditd dependency in the capture path.

## User-Facing Behavior

- The Lintap sensor, running on a RHEL 9-class SELinux host, continuously
  emits SELinux event streams alongside process/file/network:
  - discrete events for AVC denials (and audited grants) and for context
    transitions, available in the stream within seconds of occurrence;
  - periodic interaction-map records: novel (source ctx, target ctx, class,
    permission) tuples emitted on first sight, with counts flushed on an
    interval.
- Streams land as `raw_sensor` parquet in the standard partitioned layout
  and are queryable with DuckDB in parallel with the other event domains
  (joinable to process identity per the design's schema decisions).
- A kill switch / config gating consistent with existing sensor conventions
  (exact key naming delegated to design).

## Acceptance Criteria

Frozen 2026-08-27 (interview round 2):

1. **Provoked-denial test** — a deliberately triggered AVC denial (test
   domain or mislabeled file) appears in the stream within seconds, with
   fields matching `ausearch` ground truth.
2. **Transition coverage** — known domain transitions (e.g. exec
   transitions into confined domains) appear correctly in the stream.
3. **Interaction-map query** — a DuckDB query over landed `raw_sensor`
   parquet reproduces the expected context-interaction picture for a
   scripted workload.
4. **Overhead/no-loss gate** — `ring_fail_total=0`-style health invariant
   holds and CPU overhead is acceptable alongside the existing tracers.

## Affected Areas

- `../wintap/wintap/platform/linux/sensor/ebpf/` — new SELinux tracer(s) in
  `tracers/`, a new sensor class, Makefile build integration (code changes
  require a dev handoff authorizing `../wintap`).
- `../wintap/wintap/core/etl/` — Esper EPL for the new streams (observing
  the group-by invariant) and serializer output to `raw_sensor`.
- WintapMessage/data model — new message/event type(s) for SELinux
  (schema delegated to design).
- This repo — feature artifacts, later validation queries/workload scripts.

## References

See [[wiki/work/selinux-monitoring/references]].

## Open Questions

- Attach points: BPF LSM hooks vs `avc:selinux_audited` tracepoint vs
  kprobes on avc/security functions — the spike question
  ([[wiki/work/selinux-monitoring/spike]]).
- Context representation: numeric SIDs (kernel-internal, need resolution)
  vs full context strings at capture time; whether to split
  user:role:type:category at capture, at ETL, or at query time (the legacy
  `SELINUX_CONTEXT` view splits at query time).
- Is the target host enforcing or permissive? (Affects the provoked-denial
  procedure and whether denials block or only log.)
- Novel-tuple dedup residency: in-kernel map vs userspace sensor dedup, and
  the flush interval / map-size bounds.
- How interaction-map records join to process identity (PidHash stamping vs
  context-only records).

## Test Plan

Sketch; finalized in `implementation_plan.md`:

- Unit: tracer decode/parse tests; sensor aggregation-dedup tests (novel
  tuple emit, count fold, flush boundary).
- Integration: scripted SELinux workload (provoked denial via test policy
  module or mislabeled file; known transition; scripted allow-side
  interactions) with `ausearch` as independent ground truth for denials.
- Health: counters-based no-loss check (`ring_fail_total=0`), CPU overhead
  comparison with the SELinux tracer on vs off.
- Landing: DuckDB queries over `raw_sensor` parquet verifying schema,
  partitioning, and the acceptance-criteria interaction picture.

## Done When

- All four acceptance criteria pass on the target RHEL 9-class host.
- Streams run in parallel with process/file/network with the health gate
  green.
- Verification recorded in `verification.md`; durable facts promoted to
  canonical pages (likely a new `event_type/selinux-events` and/or
  `component/` page); follow-ups (dashboard feature, Wintappy bronze,
  RHEL 8 tier) logged.
