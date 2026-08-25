---
title: "Proposal: fop-11 Short-Interval FileOps Aggregation"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - wiki/work/optimize-fileops-poller/verification.md
  - wiki/work/optimize-fileops-poller/dev_handoff.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: wintap-api
event_domain: file
audience: developer
status: draft
source_paths: wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md
tags: [feature-work, file-events, aggregation, linux-sensor, ebpf, design-review]
---

# Proposal: fop-11 Short-Interval FileOps Aggregation

## Summary

This proposal turns the now-measured duplicate-open redundancy into a concrete
next-step design for `fop-11`: bounded short-interval in-kernel aggregation for
repeat FileOps activity, with emit-first semantics so distinct activity still
arrives immediately.

The core recommendation is intentionally narrower than “aggregate everything”:

1. Start with **`open` / `openat` repeat aggregation only**.
2. Keep the first occurrence of a distinct `(pid, path, op)` immediate and
   unchanged.
3. Fold only short-window repeats of the same identity into per-interval
   summary records.
4. Leave `read`, `write`, `close`, `mmap`, and `unlink` per-event in the first
   implementation unless a later measurement proves the extra semantic change is
   worth it.

This proposal is ready for designer review, not direct implementation.

## Why Now

The latest `fop-10` bundle supplied the gating evidence that was previously
missing.

Measured duplicate-open ratios in the deployed `fop-10` build were high across
multiple intervals:

- `52.7%`
- `82.5%`
- `60.4%`
- `83.7%`
- `61.8%`
- `80.0%`

Those numbers are large enough that duplicate suppression is no longer a
speculative optimization. They also line up with the observed surviving load:
library and system-tree churn (`/lib64`, `/usr`, `(relative)`, `/opt`, `/var`)
and process-name buckets like `rpm`, `systemd`, `splunkd`, `git`, and
`setroubleshoot*`.

At the same time, recent bundles still show that even after queue decoupling and
pre-enqueue identity stamping, the active failure mode remains userspace queue
loss rather than ring loss under some load phases.

## Proposed Scope

### First-pass scope

- Aggregate **repeat `open` / `openat` events only**.
- Aggregation key: `(pid, normalized_path_hash, op_type)`.
- Window: fixed short interval, proposed default `1000 ms`.
- First occurrence emits immediately as today.
- Subsequent repeats inside the window increment a bounded in-kernel entry.
- On flush, emit one summary File event carrying:
  - repeat count
  - first timestamp in the interval
  - last timestamp in the interval
  - path identity
  - pid / process identity fields as today

### Explicit non-scope for first implementation

- No aggregation of `read`, `write`, `close`, `mmap`, or `unlink` yet.
- No sampling.
- No silent dropping without accounting.
- No change to the first distinct `open` event.

## Why `open`-Only First

`fop-10` measured duplicate redundancy specifically for same-`(pid,path)` open
activity. That is the cleanest place to spend semantic complexity first.

Reasons to avoid starting with broader op aggregation:

- `open` duplicates were directly measured; `read`/`write` duplicates were not.
- `read`/`write` aggregation introduces a larger information tradeoff because
  byte-level sequencing and event timing become less literal.
- `open` is the best fit for an “emit first, count the repeats” rule because
  the first open already captures the distinct activity and later opens are more
  likely to be redundant churn.

## Semantics

### Emit-first behavior

For each distinct aggregation key inside a short interval:

- first event: emit immediately as a normal File event
- later repeats in the same interval: do not emit immediately; increment the
  entry’s repeat counter
- at flush: if repeat counter > 0, emit one summary record

This preserves low-latency visibility for new activity while compressing repeat
noise.

### Information tradeoff

What is preserved:

- the first distinct open event
- the fact that repeats happened
- the count of repeats
- the first/last timing bounds for the repeats
- pid/path/op identity

What is lost:

- individual timestamps for each repeated open inside the interval
- one-row-per-repeat event granularity

That tradeoff should be called out explicitly in review because it changes the
meaning of File telemetry, even if it does not change the meaning of distinct
activity.

## Differential Contract Change

`fop-11` cannot be validated with the current strict per-event parity rule.

Proposed replacement contract:

- distinct-tuple equality for regular-file activity must still hold
- plus count conservation:
  - `distinct immediate opens + aggregated repeat counts` in candidate
    must equal raw open-event cardinality in baseline for the same normalized
    `(pid, path, op)` universe

## Kernel-State Direction

- bounded LRU hash map
- key: `(pid, op_type, path_hash)`
- value: first timestamp, last timestamp, repeat count
- flush on interval expiry, eviction, and best-effort shutdown

## Controls And Guardrails

- feature flag required for first rollout
- bounded map sizes only
- explicit counters for aggregated-first emits, aggregated-repeat hits, summary
  flush emits, evictions, and failed inserts

## Risks

1. semantic drift: repeated opens stop being one-row-per-event
2. verifier complexity risk on RHEL8
3. validation complexity risk because count conservation replaces per-event
   equality
4. downstream ambiguity unless repeat metadata is explicit

## Recommendation

Approve `fop-11` **in principle** for designer review with this narrower scope:

- implement `open` / `openat` repeat aggregation only
- emit-first semantics
- short interval `1000 ms` default
- bounded kernel LRU map
- explicit repeat-count metadata
- revised differential contract based on distinct-tuple equality plus count
  conservation

If the designer agrees, the next engineering step should be a short
implementation spike focused on verifier feasibility, exact record/schema
choice, and the updated validation harness contract.

## Status

Milestone reached 2026-08-25:

- `fop-10` produced the evidence needed to make `fop-11` concrete enough for
  design review rather than speculation.
