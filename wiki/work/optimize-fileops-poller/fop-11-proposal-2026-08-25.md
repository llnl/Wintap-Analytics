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

## Designer Review — 2026-08-25

**Verdict: approved in principle, with two hard conditions and one
recommended re-scoping.** The evidence genuinely supports duplicate-open
suppression: the measured 52.7–83.7% repeat ratios come from a userspace
measurement keyed on `(pid, filePath)` with a 1000 ms window — the same key
shape and the same window the proposal specifies — so the numbers directly
predict the win of the proposed design rather than merely suggesting it.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §RecordMeasurement/§DuplicateOpenWindowMs -->
Emit-first semantics, the open-only narrowing, and the count-conservation
contract shape are all right.

### Hard conditions (must resolve before implementation)

1. **Relative-path identity conflation.** `(relative)` is a top prefix bucket
   in the fop-10 attribution, and the proposed key `(pid, path, op)` conflates
   the same relative path string across different working directories (and
   `openat` dirfds). In the aggregator that suppresses a genuinely distinct
   file's first open as a "repeat" — real information loss that violates the
   proposal's own emit-first guarantee. Fix: **aggregate absolute paths only**
   (relative-path opens stay per-event), or include dirfd/cwd identity in the
   key. Corollary: the measured repeat ratios are slightly inflated by the
   same conflation; the signal stands (absolute `/lib64`, `/usr` dominate) but
   the proposal should note the caveat.
2. **Summary-record identity must be captured at first-occurrence, not at
   flush.** "pid / process identity fields as today" resolved at flush time
   reintroduces the resolve-after-producer-exit failure that the fop-08
   pre-enqueue identity stamping just fixed — summary records flush up to a
   window later, when short-lived producers are already gone. Stamp identity
   when the first occurrence is emitted and carry it into the summary record.

### Recommended re-scoping: implement in userspace first

The kernel-LRU design was framed when ring overflow was the active loss mode.
The evidence has since moved: every recent bundle shows `ring_fail_total=0`
across all op classes, the active loss is the bounded userspace queue, and
`FileOps-Poller` runs at 0.1–0.2% CPU with the sender as the hot thread. A
**pre-enqueue dedup on the poller thread** — reusing the `(pid, path)` →
last-seen dictionary the fop-10 measurement already maintains — achieves the
identical semantic contract while directly cutting queue volume, with no
RHEL8 verifier risk, no kernel map, and no kernel flush-mechanism problem
(risks 2 and much of 3 in §Risks disappear). Kernel promotion stays available
later if ring pressure or poller CPU returns; the semantic contract, schema,
and validation work transfer unchanged. If the kernel variant proceeds
anyway, note RHEL8 4.18 has no `bpf_timer`, so interval flush must be a
userspace sweep or lazy on-next-event (unbounded summary latency for keys
that stop repeating) — settle this in the spike.

### Expectation-setting and contract notes

- **Open-only dedup may not eliminate the worst queue-drop spikes.** The
  largest recorded burst coincided with `write:consumed=1,820,145` in one
  interval — a read/write consumption storm this scope does not touch.
  Acceptance should measure queue-drop reduction under comparable load, not
  assume elimination.
- **The revised contract must be op-scoped:** strict per-event parity remains
  for `read`/`write`/`close`/`mmap`/`unlink`; distinct-tuple equality plus
  count conservation applies to `open`/`openat` only.
- **Count conservation is only decidable on drop-free harness runs** (queue
  `drops=0` and `ring_fail_total=0` across the run window), or with drop
  counters folded into the balance; otherwise aggregation bugs and queue loss
  are indistinguishable. State the precondition in the harness.
- **Comparator work is real:** `compare_fileops.py` needs summary-record
  decode and count columns; include it in the spike deliverables.
- **Schema must be specified before coding:** repeat-metadata field names
  (count, first/last repeat timestamps), defaults for non-aggregated rows
  (count=1), and a downstream note for Esper statements, DirectParquetSink
  columns, and Wintappy bronze/silver models.
- Minor (kernel variant only): 64-bit path-hash collisions are negligible at
  these key cardinalities and the differential harness would catch an
  over-merge; kernel raw-path hashing keys strictly finer than the userspace
  normalized identity, which errs in the safe (under-merge) direction.

## Human Review Response — 2026-08-25

The human reviewed the proposal and the designer review; outcomes:

1. **Relative-path conflation — upgraded from "exclude" to "resolve".**
   Absolute paths are needed anyway: the point of the sensor is accurate
   ground truth about the monitored system. Rather than excluding relative
   opens from aggregation, resolve them to absolute paths at open time. This
   is now precondition slice **fop-12** in the implementation plan
   (recommended mechanism: readlink `/proc/<pid>/fd/<fd>` at open-exit while
   the producer is alive; `bpf_d_path` is unavailable on RHEL8 4.18
   tracepoints).
2. **Summary-record identity at first occurrence — accepted** as a hard
   condition.
3. **Scope — expanded, direction formally amended.** The 2026-08-24 "no
   aggregation" direction is softened to: *aggregation to the (pid, path, op)
   level with grouped totals (bytes etc.) and min/max timestamps over short
   intervals is acceptable* — for all op classes, not just open/openat. The
   goal is as complete a picture as possible; open-first remains reasonable
   sequencing but is no longer a scope boundary. This also means the
   read/write burst caveat in the designer review is addressable within
   fop-11 rather than deferred. Contract addendum: byte-total conservation
   joins count conservation for aggregated op classes.
4. **OSS sensor survey (Tetragon/Tracee/Sysdig) — deliberately wait.**
   Improvements are still landing; the survey stays a saved future task, most
   valuable once fop-11/fop-12 results exist to compare against.

## Esper-Layer Addendum — 2026-08-25

A follow-on analysis of the Esper stream (human-requested) materially
reframes this proposal's information tradeoff: in the deployed configuration,
File events reach parquet only through `file.epl`, which already aggregates
into 10-second batches grouped by `(file.path, PidHash, PID, activityType,
ProcessName)` with `count(*)`, `sum(bytesRequested)`, and min/max event
times; `default.epl` excludes File from per-event pass-through. Per-repeat
rows and timestamps therefore never reach disk today. With the composition
rules honored (schema repeat-count field summed in EPL instead of `count(*)`;
first/last timestamp fields for min/max; sub-batch interval), **fop-11
changes nothing in the recorded output** — the §Semantics "information
tradeoff" applies only to live in-stream Esper consumers, for which
emit-first is retained. The revised differential contract likewise aligns
with what the parquet-level comparator already measures (distinct tuples +
`eventCount`/byte balance). Full detail and the resulting fop-11 hard
conditions: [[wiki/work/optimize-fileops-poller/dev_handoff]] §Esper-Layer
Findings.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/file.epl; ../wintap/wintap/core/etl/esper/default.epl -->
