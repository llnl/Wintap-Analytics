---
title: "Raw sensor compaction: optional bounded process-context state"
type: concept
confidence: speculative
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/brief.md
  - wiki/work/raw-sensor-file-aggregation/implementation_plan.md
  - wiki/concept/durable-process-context-and-stream-table-enrichment.md
  - wiki/diagnostic/process-tree-context-completeness.md
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/raw-sensor-file-aggregation; wiki/concept/durable-process-context-and-stream-table-enrichment.md
tags: [feature-work, compaction, entity-state, ancestry, retention, proposal]
---

# Recommendation and scope

**Follow-on planning selected 2026-11-12:**
[[wiki/work/durable-process-entity-manager/brief]] records the human's first-round
S3 Parquet store/hourly writer/infrequent DBT direction. That design proposes full
per-host rewrites and no initial entity GC. The bounded-horizon/mark-and-sweep
options below remain future alternatives, not selected first-round retention.
The human subsequently authorized implementation; the first round is now
[[wiki/tool/durable-process-entity-manager]]. The bounded-state alternatives below
remain proposals. Completed raw compaction row semantics are unchanged.

**Use the hourly compaction pass to feed an optional process-context projection,
not to replace raw process events with latest-state rows.** Compaction remains
row-preserving `UNION ALL` with source/output count equality. The projection has
different semantics and needs its own validation and explicit consumer support.
This note is an unapproved follow-on option; it does not change the brief's
milestones, acceptance criteria, no-lookback assumption, or source-retention policy.

The goal is **telemetry ground-truth collection**, independent of particular
experiments. Later experiments consume the complete dataset or subsets of it;
they do not control collection or state-retention policy. The user's research
qualification is not a requirement for long-horizon schema evolution or backward
compatibility. This optional projection can be designed on its own merits, while
the current compactor's explicitly agreed row-preservation contract remains intact.

Tactically, select DBT publication partitions spanning the relevant deployed
sensor runtimes, including startup/rundown publications and delivery slack.
Subset activity afterward while retaining its required process context. This
reduces missing long-lived context without first implementing a state service;
it does not recover ancestors that the collector never published.

## Proposed bounded working set

Define an **operational context horizon H** and an allowed late-arrival/replay
grace G. These are dataset-processing policy inputs, not experiment durations or
selected settings. Original raw archives remain unchanged and outside this
working-set bound. The derived state is an acceleration/context mechanism, not
the sole historical record of collected telemetry.

Keep the union of:

1. Instances recently confirmed live by trustworthy inventory or activity evidence.
2. Instances referenced by activity/process seeds within H, plus G.
3. **All known transitive ancestors** of those instances, even if exited or born
   before H. Record unresolved boundaries rather than inventing nodes.

An ancestor's birth-age TTL is unsafe: a weeks-old parent can still be needed by
today's child. Once an exited instance is outside H/G and unreachable
from retained seeds, its derived context can be reclaimed. This is
**reachability-based retention / mark-and-sweep garbage collection** over a
process graph. It bounds the normal working set by supported activity and its
dependencies, not by all instances ever observed.

## Storage and update optimizations

- Maintain one compact instance record keyed in canonical host/`pid_hash` scope;
  never key solely by reusable PID. Collector runtime/boot provenance scopes
  coverage, but does not redefine the process identity.
- Store birth, parent identity, lifecycle evidence, metadata/provenance and the
  latest genuine observation/publication time. Do not refresh every row's lease
  merely because the maintenance job ran. Refresh EventTime can be the old birth.
- Collapse repeated Refresh into an idempotent derived update, while preserving
  those observations in raw compacted output. A late Refresh must not reopen a
  process with authoritative Stop evidence; parent/metadata conflicts stay visible.
- Split small lineage skeletons from large arguments/path/metadata payloads where
  useful. Ancestor-only nodes can retain identity/edges and selected display fields;
  detailed historical metadata can be loaded from archived partitions on demand.
- Read new process observations incrementally; update retained references from
  the relevant activity families. Merely reading `raw_process` does not reveal
  which instances the last H of file/network activity still needs.
- Partition state by host, and use trustworthy boot/collection metadata for
  retirement and lookup. A collector restart or redeployment on the same boot is
  **not** evidence that every old process exited.
- Publish dataset-level state checkpoints with coverage/provenance, rather than
  copying the whole working-state table into every hourly partition. Later subset
  readers select activity and obtain its required context from retained state,
  checkpoints or archived history. Checkpoints belong to the collection dataset,
  not to specific experiments. Their own storage/retention costs must be budgeted.

## Limits that must remain explicit

**A dependency-preserving working set is not a strict fixed-size guarantee.** A
long-lived descendant may retain a long chain of exited ancestors. Missing Stops
can also make an inferred active set accumulate indefinitely. Reconcile with
successful inventory evidence where available; absence from a partial inventory
is not death. Stale/unknown instances need an explicit retention policy, not
fabricated Stop events.

Set row/byte and per-host budgets, expose active/recent/ancestor-only/stale counts, and
fail or report degraded coverage when exact closure cannot fit. An LRU that
silently drops required ancestors recreates the original defect. If a hard bound
is mandatory, restrict the operational working horizon, spill to colder storage, or
explicitly accept context truncation. No bounded table can guarantee complete
ancestry for arbitrary all-time queries; older queries must replay raw history
or use retained dataset-level context checkpoints. Evicting derived state must
not silently remove ground-truth rows from the retained dataset or make an
otherwise supported historical subset appear context-complete.

## Integration work beyond compaction

The hourly pass is a convenient place to share discovery and process-row reads,
but durable updates introduce ordering, rebuild and recovery requirements absent
from a stateless per-hour merge:

- Process only verified source sets; checkpoint which source generations were
  applied. Re-running/rebuilding an hour must not double-apply state, lose evidence,
  or silently leave a projection based on superseded input.
- Bootstrap from the required sensor-runtime partitions. No new state projection
  can recover unknown pre-bootstrap ancestors without historical input.
- Handle late data and out-of-order hour processing explicitly. The existing
  upload-partition TODO remains relevant; G is an additional proposed state policy,
  not a silent change to the compactor's confirmed no-lookback scope.
- Publish coherent, versioned state/context snapshots outside consumer-scanned
  `raw_sensor` trees. Raw-output and state completion need explicit checkpoints;
  multi-object S3 writes are not a transaction.
- Add a DBT context input/union/enrichment contract separately. Existing consumers
  will not discover or use a side-state relation automatically. Do not inject
  historical context into raw hourly output and break row-count conservation.

Proposed tests: repeated Refresh, late Stop/Refresh ordering, PID reuse, same-boot
collector restart, exited parent/live child, missing Stop, incomplete inventory,
hour replay/rebuild, horizon expiry, dataset-checkpoint recovery, budget exhaustion, and
context-only rows excluded from in-window birth/activity counts.

<!-- SYNTHESIS: user clarification 2026-11-12 separates ground-truth collection from downstream experiments; bounded state and dataset-checkpoint mechanics remain proposals -->

<!-- SYNTHESIS: optional design inferred from the compaction brief/plan and anonymized ancestry audit; no implementation or scope expansion approved -->

Related: [[wiki/workflow/process-ancestry-completeness-qa]],
[[wiki/tension/refresh-republication-vs-durable-process-context]],
[[wiki/tension/raw-sensor-compaction-publication-vs-glob-readers]].
