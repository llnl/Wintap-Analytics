---
title: "Interview: SELinux Monitoring"
type: concept
confidence: high
grounded_by:
  - ../Lintap/sql/selinux.sql
  - ../Lintap/merge_raw_tsv.sh
  - ../Lintap/README.md
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/
policy: agent-editable
last_validated: 2026-08-27
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/selinux-monitoring/interview.md
tags: [feature-work, selinux, lintap, ebpf, telemetry-semantics]
---

# Feature Interview: SELinux Monitoring

## Initial Idea

> I want to be able to do real time monitoring that the selinux policies are
> working as expected on my machine. In order to do that, I need to easily
> monitor the interactions between selinux contexts as they relate to system
> events happening in the system.

Branch: `lindseyw/selinux-monitoring`.

## Context Established Before Questioning

- Existing SELinux support is a batch, sysdig-era, experimental path:
  auditd-derived TSVs (`raw_selinux_contexts`, `raw_selinux_paths`) merged by
  `../Lintap/merge_raw_tsv.sh` into parquet, post-processed by
  `../Lintap/sql/selinux.sql` (ASOF join to Wintap `PROCESS`, a
  `SELINUX_CONTEXT` master view splitting contexts into user:role:type:cat).
  <!-- GROUND_TRUTH: ../Lintap/sql/selinux.sql; ../Lintap/merge_raw_tsv.sh §raw_selinux loop -->
- The collector that produces those TSVs from auditd was never committed to
  the Lintap repo; `selinux.sql`'s own comments record a 7-hour TZ
  misalignment, ~40% of raw rows failing to join to a Lintap process, and no
  interval filtering between continuous auditd and interval Lintap runs.
  <!-- GROUND_TRUTH: ../Lintap/sql/selinux.sql §Known issues comment -->
- The Lintap sensor's eBPF tracers live in
  `../wintap/wintap/platform/linux/sensor/ebpf/tracers/` (CO-RE + tracepoint
  fallback tiers) and flow tracer → C# sensor → EventChannel → Esper EPL →
  serializer → `raw_sensor` parquet ([[wiki/component/fileops-event-pipeline]]).
- No real-time SELinux capability exists anywhere in the ecosystem; TeleTap
  has no SELinux hooks today.

## Interview Log

### Round 1

**Q:** Primary signal for "policies working as expected"? (denials/grants,
interaction map, label drift, transitions — multi-select)
**A:** All four: AVC denials/grants for *debugging*; context transitions and
the interaction map for *monitoring*.
**Outcome:** decision — dual-purpose signal set, split by use.

**Q:** What does "real time" mean for consumption, given the batch POC?
**A:** "That was a crude POC. We are looking for an in-kernel mechanism that
we can run alongside eBPF. We want SELinux to be first-class events in the
system."
**Outcome:** decision — first-class Lintap event domain, not a bolt-on view;
the auditd batch path is superseded.

**Q:** Collection source — auditd, eBPF/TeleTap LSM, or staged both?
**A:** eBPF/TeleTap LSM.
**Outcome:** decision — eBPF capture, no auditd dependency in v1.

**Q:** Through the semantic Wintap data model or standalone loop?
**A:** "Whatever makes sense; we want them in parallel in Lintap itself."
**Outcome:** decision (mechanism delegated) — streams run in parallel with
process/file/network inside the Lintap sensor pipeline.

### Round 2

**Q:** Target platform/kernel? (RHEL 8's 4.18 lacks BPF LSM and the
`avc:selinux_audited` tracepoint; RHEL 9+/5.14+ has both.)
**A:** RHEL 9 / modern kernel.
**Outcome:** constraint — RHEL 9-class kernel is the v1 target; RHEL 8 out.

**Q:** Volume posture for the allow-side interaction map?
**A:** Novel-tuple dedup (recommended option accepted).
**Outcome:** decision — in-kernel/in-sensor dedup keyed by (source ctx,
target ctx, class, perms); novel tuples emit immediately, counts flush
periodically. Applies the fop-11 aggregation lessons.

**Q:** What evidence closes v1? (multi-select)
**A:** All four: provoked-denial test, transition coverage, interaction-map
query, overhead/no-loss gate.
**Outcome:** decision — the four acceptance criteria in brief.md.

**Q:** Is the monitoring *view* in scope, or the event streams?
**A:** Events first (recommended option accepted).
**Outcome:** decision — v1 delivers the streams; dashboards are a follow-up
feature.

### Round 3

**Q:** Is a RHEL 9 / modern SELinux host available now for spike/dev?
**A:** Yes, existing host.
**Outcome:** constraint — real target exists; enforcing/permissive status
unconfirmed (deferred to spike).

**Q:** Disposition of the old auditd batch path?
**A:** Leave as-is, non-goal (recommended option accepted).
**Outcome:** decision — untouched; documented as the superseded POC; its
context-splitting SQL remains schema reference.

**Q:** Wintappy DBT bronze in v1?
**A:** raw_sensor is the boundary (recommended option accepted).
**Outcome:** decision — v1 ends at correct raw_sensor parquet; DBT later.

## Decisions

- SELinux becomes a first-class Lintap event domain, captured in-kernel via
  eBPF, flowing in parallel with process/file/network through the standard
  pipeline (tracer → sensor → EventChannel → Esper → serializer →
  `raw_sensor` parquet).
- Signal set: AVC denials/grants (debugging); context transitions +
  context-interaction map + label/drift observations (monitoring).
- Allow-side volume handled by novel-tuple dedup keyed by (source context,
  target context, class, permission); denials and transitions emit as
  discrete events.
- v1 deliverable is the event streams; monitoring dashboards/UX are a
  follow-up feature. `raw_sensor` parquet is the downstream boundary (no
  Wintappy DBT in v1).
- Legacy auditd batch path: untouched, non-goal, superseded.

## Constraints

- Target: RHEL 9-class / modern kernel host (existing, available). BPF LSM
  and `avc:selinux_audited` tracepoint are candidates. RHEL 8 (4.18) is not
  a v1 target.
- Sensor code changes land in `../wintap` (Linux sensor tree); wiki
  artifacts live in this repo.
- Esper EPL invariant: every non-aggregated select column MUST be in the
  group by ([[wiki/component/fileops-event-pipeline]] — the n² eventCount
  lesson).

## Delegations

- Exact attach points (BPF LSM hooks vs `selinux_audited` tracepoint vs
  kprobe tiers) — delegated to the spike ([[wiki/work/selinux-monitoring/spike]]).
- Event schema: WintapMessage type(s), `raw_sensor` path naming, context
  representation (SID vs full string; user:role:type:category splitting).
- Whether label/drift detection is a derived query over landed data or needs
  its own capture path.

## Deferred / Open Questions

- Enforcing vs permissive on the target host (spike confirms; affects the
  provoked-denial procedure).
- Monitoring dashboard UX (follow-up feature over the landed streams).
- Wintappy bronze models; RHEL 8 compatibility tier.

## Playback Summary

Playback was presented 2026-08-27 covering the decisions, constraints,
acceptance criteria, delegations, and deferrals exactly as recorded above;
the human proceeded directly to the sealed estimate questions, confirming
the playback.

## Sealed — human estimates

SEALED: any agent that will produce its own estimates (e.g. the Wintap
Engineer at exploration start) must not read this section until feature
close-out. See [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1) and
[[wiki/concept/velocity-metric]].

**Q: If you had to build this exact scope alone, without AI, how many working
hours would it take? And on what date would it realistically have been
available? (Forced counterfactual.)**
**A:** "1 month"
*(Agent annotation, not human words: interpreted as ≈160 solo working hours;
calendar availability ≈ 2026-09-27. Recorded verbatim above per protocol —
never re-asked.)*

**Q: With the AI workflow, on what date do you predict this feature will be
available? (Calendar prediction, open date to availability.)**
**A:** "1 week"
*(Agent annotation: interpreted as predicted availability ≈ 2026-09-03 from
the 2026-08-27 open date.)*
