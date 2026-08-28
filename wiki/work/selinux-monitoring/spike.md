---
title: "Feature Spike: SELinux Monitoring — attach-point probe"
type: concept
confidence: low
grounded_by: []
policy: agent-editable
last_validated: 2026-08-27
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: stub
source_paths: wiki/work/selinux-monitoring/spike.md
tags: [feature-work, selinux, ebpf, spike]
---

# Feature Spike: SELinux Monitoring — attach-point probe

## Question

On the actual target RHEL 9-class host, which eBPF attach points can deliver
the three signal classes (AVC decisions, context transitions, allow-side
interaction tuples) with context identity, at acceptable overhead?
Candidates, in preference order to probe:

1. `avc:selinux_audited` tracepoint — covers audited decisions (denials +
   auditallow grants); confirm field set (are scontext/tcontext strings
   included?) and that it does NOT see unaudited allows (expected — rules
   out relying on it alone for the interaction map).
2. BPF LSM hooks — confirm `CONFIG_BPF_LSM` and active `lsm=` list; whether
   attaching is permitted operationally; which hooks give (source, target,
   class, requested) for the interaction map; per-check overhead.
3. kprobes/fentry on avc/security functions (`avc_audit`,
   `slow_avc_audit`, transition-related hooks) — symbol availability,
   argument stability, and CO-RE readability of `task_struct` →
   `cred->security` SID fields.

Also to resolve on-host: SID→context-string resolution strategy; enforcing
vs permissive mode; baseline permission-check rates (sizes the dedup map).

## Hypothesis

A hybrid is likely: the audited tracepoint (or an LSM/kprobe equivalent) for
denials/audited grants, plus a low-cost hook for transitions, plus a
dedup-behind-the-hook capture for the allow-side interaction map. Context
strings will need resolution at or near capture time since SIDs are not
stable across boots.

## Experiment

Planned (not yet run):

1. On-host capability census: kernel version/config (`CONFIG_BPF_LSM`),
   active LSMs, `avc` tracepoint presence and format
   (`/sys/kernel/debug/tracing/events/avc/*/format`), kallsyms symbol check,
   `getenforce`.
2. Throwaway bpftrace/libbpf probes on each candidate: provoke a denial and
   a transition; measure events/sec on the allow-side candidate under normal
   load.
3. Record per-candidate field availability, rates, and overhead notes.

## Prototype Location

TBD — throwaway probes; anything kept lands under a diagnostics path in
`../wintap` per the dev handoff, or is transcribed here.

## Results

Not yet run.

## Recommendation

Pending results.

## Follow-Ups

Feeds `design.md` (attach-point tiers, schema, dedup residency).
