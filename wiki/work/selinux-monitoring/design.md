---
title: "Feature Design: SELinux Monitoring"
type: concept
confidence: medium
grounded_by:
  - wiki/work/selinux-monitoring/spike.md
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs
policy: agent-editable
last_validated: 2026-09-18
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/selinux-monitoring/design.md
tags: [feature-work, selinux, ebpf, avc, telemetry-semantics, design]
---

# Feature Design: SELinux Monitoring

## Summary

Three SELinux streams, three spike-verified attach points, one new tracer:

| stream | hook (validated) | volume (measured) | shape |
|---|---|---|---|
| AVC denials + audited grants | `avc:selinux_audited` tracepoint | ~0/s baseline; bursts on denial | discrete events, context STRINGS free at capture |
| Context transitions | kprobe `selinux_bprm_committed_creds` | ~2/s commits | discrete events, old/new SID from cred blob |
| Allow-side interaction map | kprobe `avc_has_perm_noaudit` | 2.4-13k/s checks; **421 distinct tuples** observed | in-kernel novel-tuple dedup, periodic count flush |

Everything flows through the standard pipeline (tracer → sensor →
EventChannel → Esper → serializer → `raw_sensor` parquet) parallel to
process/file/network. The one genuinely open problem is SID→context-string
resolution for streams 2-3; this design makes it the first implementation
slice with a prototype-then-fallback decision procedure rather than
guessing now.

## Proposed Approach

### Kernel tracer (`tracers/selinux_tracer.bpf.c`, single tier)

One CO-RE object, three program groups, following `file_ops_tracer.bpf.c`
conventions (ringbuf + stats array + self-PID filter map + batched
wakeups):

1. **`tracepoint/avc/selinux_audited`** → discrete `selinux_avc_event`:
   `requested`/`denied`/`audited` masks, `result`, bounded string copies of
   `scontext`/`tcontext`/`tclass` (256/256/32 bytes — MLS category sets can
   be long; truncation counter if hit), pid/tgid, comm, `ktime` ns.
   Denials and auditallow grants arrive with strings — no SID resolution
   needed on this stream.
2. **`kprobe/selinux_bprm_committed_creds`** → discrete
   `selinux_transition_event`: old/new SID read from
   `current->cred->security` as `struct task_security_struct{osid, sid}`
   (BTF-verified on both kernels), `bprm->filename` (arg0, CO-RE read),
   pid, comm, ts. Emit only when `osid != sid` (actual transitions; ~2/s
   measured commit rate makes filtering cheap either side — filter
   in-kernel to keep the stream pure).
3. **`kprobe/avc_has_perm_noaudit`** → interaction map. **Hook the
   noaudit variant, not `avc_has_perm`:** `avc_has_perm` is a wrapper that
   calls `avc_has_perm_noaudit` + `avc_audit`, while the inode-permission
   fast path calls the noaudit variant directly — so `avc_has_perm_noaudit`
   is the single choke point covering both, with no double counting.
   (Spike measured the wrapper; the first implementation slice re-runs the
   spike's hist method on the noaudit symbol to confirm rate/cardinality —
   expected same order, strictly ≥.)
   **Hook policy (normalized 2026-09-18):** the preferred production hook
   remains `avc_has_perm_noaudit` where attachable, because it covers the
   inode fast path. In the RHEL 8.10 validation environment it is visible
   in kallsyms but rejects perf-event kprobe attach with EINVAL, so
   sel-02 uses `avc_has_perm` as a validated fallback with an explicit
   coverage caveat (logged at attach time). See Edge Cases/Risks and the
   implementation plan's sel-03 gate.
   - Dedup map: `BPF_MAP_TYPE_LRU_HASH`, 16,384 entries (~40× the observed
     421-tuple set), key `(ssid, tsid, tclass, requested)` (16 B), value
     `{count, first_ts, last_ts, first_pid, first_comm}`.
   - Novel key → reserve+submit a `selinux_novel_tuple_event` (emit-first,
     fop-11 pattern; identity captured at first sight, never re-resolved).
   - Existing key → `count++`, `last_ts` update; no ring traffic.
   - Userspace flush sweep every `WINTAP_SELINUX_FLUSH_SEC` (default 30 s):
     iterate map, emit count summaries for entries with
     `count > emitted_at_flush`, in-place snapshot rather than
     delete-and-reinsert (delete would make every tuple "novel" again and
     re-emit; LRU eviction provides the bound).
   - Semantics documented as: novel-tuple emission is at-least-once (LRU
     eviction can re-novel a tuple), counts are conservative
     (never inflated).

fentry upgrades for the two kprobes are a later optimization, gated on
verifying fentry in the validation environment (spike leftover; bpftrace or
a libbpf probe).

### Userspace sensor (`SELinuxSensor.cs` + `SELinuxSidResolver.cs`)

Patterned on `FileOpsSensor` (ring consume thread, bounded send queue,
60 s counters log line, monotonic→realtime offset conversion — all existing
idioms). New responsibilities:

- **Permission-mask decode:** at startup read
  `/sys/fs/selinux/class/<name>/index` and `class/<name>/perms/<perm>` to
  build class→(bit→perm-name) tables; decode `requested`/`denied` masks to
  permission-name lists. Also maps numeric `tclass` (streams 2-3) to the
  class string. Unknown-bit counter for policy drift.
  *(Validated sel-03, 2026-09-18: 132 classes / 2,150 permissions loaded;
  unknown bits are FIRST-CLASS telemetry — counted with a top-N breakdown,
  numeric masks always preserved, never a drop condition. Watch item: the
  observed unknown-mask concentration in fd/sem classes needs a
  root-cause check in sel-04 decode tests.)*
- **SID→context resolution** (streams 2-3) — decision procedure, slice 1:
  - **R1 (prototype first): in-kernel sidtab string-cache read.** Kernels
    ≥5.3 cache context strings alongside sidtab entries after first
    resolution; a CO-RE walk from `selinux_state` could emit strings at
    capture for ALL sids. Highest fidelity; highest fragility (unexported
    internals, verifier depth). Timebox a prototype during validation; adopt
    only if it verifies on both kernels and survives a policy reload test.
  - **R2 (fallback, task side): `/proc/<pid>/attr/current`** read at
    consume time for the novel tuple's `first_pid` (consume latency is ms;
    miss counter `scontext_resolve_miss` — the fop dead-producer lesson
    says expect a nonzero floor).
   *(Validated sel-03, 2026-09-18: working for active source processes —
    resolver hit=2854 / miss=1365 / learned=27 in the first packaged run;
    target contexts often remain unresolved unless learned from other
    sources, as expected for the composite.)*
  - **R3 (fallback, accumulating): learned SID→string table** harvested
    from every tracepoint event (stream 1 carries both sides' strings —
    but only maps the *audited* population) plus periodic sweeps
    (`ps -eo label,pid` equivalent via /proc, file contexts via
    `getxattr(security.selinux)` on paths seen in the File stream).
  - Fallback composite ships numeric `ssid`/`tsid` columns REGARDLESS, so
    unresolved tuples are still distinct and joinable within a boot epoch.
- **Policy-reload handling:** on reload, flush the kernel dedup map, drop
  all learned SID tables, increment a `policy_epoch` counter stamped on
  every record (SIDs are only comparable within an epoch), log the event.
  *(Delegated choice exercised in sel-03: implemented as polling
  `/sys/fs/selinux/policy` rather than the netlink listener
  (`SELNL_MSG_POLICYLOAD`); netlink remains the option if poll latency
  ever matters for epoch stamping.)*
- **Health/QA counters (60 s log line):** per-stream
  emitted/ring_fail/truncated, novel_tuples, counts_flushed,
  scontext/tcontext resolve hit/miss, unknown_perm_bits, policy_epoch.
  `ring_fail_total=0` invariant inherited unchanged.

### ETL (`selinux.epl`, serializer)

- Denial and transition streams: pass-through selects with 10 s
  `time_batch`; **every non-aggregated column in the group by** (the
  n²-eventCount rule from [[wiki/component/fileops-event-pipeline]]).
- Interaction stream: group by (scontext, tcontext, tclass, permission,
  PidHash, AgentId), `sum(eventCount)`, `min(firstSeen)`/`max(lastSeen)`.
- Serializer: follow `FileSerializer` flush pattern; three parquet outputs
  under `raw_sensor` partitioning: `selinux_avc`, `selinux_transition`,
  `selinux_interaction`. `MessageType` values FROZEN (decision 3):
  `SELINUX_AVC`, `SELINUX_TRANSITION`, `SELINUX_INTERACTION`; no changes
  to existing message types.

## Data Model Or Schema Changes

New WintapMessage event type(s) only — no changes to existing schemas.
Proposed flat fields (all three streams share the envelope + identity
block: Hostname, AgentId, PID, PidHash, ProcessName, EventTime,
PolicyEpoch):

- `selinux_avc`: SContext, TContext, TClass (strings), RequestedMask,
  DeniedMask, AuditedMask (u32), RequestedPerms, DeniedPerms (decoded
  name lists), Result, Enforcing (bool from getenforce at event time).
- `selinux_transition`: OldSid, NewSid (u32), OldContext, NewContext
  (strings, resolution-dependent), ExeFile (bprm filename).
- `selinux_interaction`: SSid, TSid (u32), SContext, TContext (strings,
  resolution-dependent), TClass, Permission (one row per set requested
  bit, exploded at ETL — decision 2), EventCount, FirstSeen, LastSeen,
  Novel (bool: first emission vs count flush).

Unresolved-context representation (made explicit 2026-09-18 for sel-04):
**numeric `SSid`/`TSid` are always present; `SContext`/`TContext` are
nullable/empty when unresolved** — resolution state is queryable, rows are
never dropped or blocked on resolution, and SID columns keep unresolved
tuples distinct and joinable within a PolicyEpoch.

PidHash stamping: identity captured at event time in-kernel
(pid/comm/starttime pattern from the exec tracer) and resolved to PidHash
in the sensor — this is the spike/brief's anti-ASOF-join decision;
interaction records carry the FIRST-seen process identity (matches the
fop-11 "identity at first occurrence" semantics).

Context splitting (user:role:type:categories) stays at query time,
matching the legacy `SELINUX_CONTEXT` view's approach — raw strings are
the durable representation.

## Interfaces And User Experience

- Kill switch: `WINTAP_SELINUX_ENABLED` (default true on hosts where
  selinuxfs is present; sensor self-disables cleanly otherwise) —
  consistent with `WINTAP_FILEOPS_AGG_ENABLED` convention.
- Tunables: `WINTAP_SELINUX_FLUSH_SEC` (30), `WINTAP_SELINUX_MAP_MAX`
  (16384), `WINTAP_SELINUX_RING_KB`.
- Startup log states: mode (enforcing/permissive/disabled), tracepoint
  present y/n, hooks attached, resolution strategy active (R1 or R2+R3),
  policy epoch.
- Acceptance queries (DuckDB over `raw_sensor` parquet) land in this
  repo's `validation/` alongside the workload script (criterion 3).

## Edge Cases

- **SELinux disabled/absent host:** sensor logs and stays down; no attach
  attempts; kill-switch semantics unaffected (lintap-dev behavior).
- **Tracepoint missing** (non-RHEL9 kernel variants): fallback tier is
  kprobe `slow_avc_audit` (same coverage, SIDs not strings → resolution
  path applies); startup selects tier by tracefs/kallsyms census exactly
  like the spike did.
- **Policy reload mid-run:** epoch bump + full flush (see above); records
  straddling the reload are attributable via PolicyEpoch.
- **Permissive vs enforcing:** `Result`/`Enforcing` recorded per event;
  permissive environments produce denials with
  `result=0` and no blocking — the acceptance provocation works in both
  modes, but blocking side effects differ; verification notes this.
- **String truncation:** MLS category ranges can exceed the 256-byte
  field; truncation sets a flag + counter rather than dropping.
- **LRU eviction under tuple churn:** re-novel emission is by design;
  eventCount conservation holds (counts are per-emission-window).
- **avc_has_perm_noaudit re-entrancy/nesting:** none expected (leaf
  function), but the slice-1 measurement confirms no double counting via
  the wrapper.
- **`avc_has_perm_noaudit` unprobeable in the RHEL 8.10 validation
  environment (sel-02 finding, 2026-09-18):** its 4.18-series kernel rejects
  perf-event kprobe creation on the symbol with EINVAL even though it is
  present in kallsyms (likely notrace/ftrace-exclusion on 4.18 — a
  tracefs `kprobe_events` test distinguishes). The sensor's wrapper
  fallback engages and produces full interaction data minus whatever
  calls the noaudit variant directly (inode fast path). Acceptance needs
  a working noaudit attach strategy, an alternate attach method, or an
  explicit scope decision (implementation_plan sel-03 gate).

## Error Handling

- Ring reserve failure → per-stream `ring_fail` counters; invariant
  `ring_fail_total=0` gates acceptance (criterion 4).
- Resolution misses → numeric-SID records with `*_resolve_miss` counters;
  never dropped events.
- selinuxfs read failures at startup → mask decode disabled, raw masks
  still shipped, warning logged.
- Netlink listener death → epoch integrity lost; sensor logs ERROR and
  falls back to polling `/sys/fs/selinux/policy` mtime (or restarting the
  listener) — decided in the handoff.

## Risks

- **kprobe overhead on a 2-13k/s path:** worst case ~1-2% of one core at
  the measured load rate; measured with the real tracer in slice 1
  (spike's overhead item); fentry upgrade is the mitigation if needed.
- **R1 (sidtab cache) fragility:** unexported kernel internals; strictly
  timeboxed prototype with R2+R3 as the shipping fallback.
- **cred->security blob offset assumption:** validated at startup by a
  self-handshake (sensor reads its own context via /proc and compares
  with the in-kernel read of its own task; mismatch disables stream 2
  with an ERROR rather than shipping garbage).
- **RHEL kernel updates:** CO-RE + startup kallsyms/tracefs census keeps
  failures loud and early rather than silent (BPF-LSM lesson).
- **Environment variance (2026-09-18):** validation used RHEL 8.10 with a
  4.18-series kernel, not RHEL 9-class as this design assumed, and the brief
  lists RHEL 8 as a v1 non-goal (soft contradiction flagged there).
  Consequences on this tier: the noaudit hook is unprobeable (above),
  fentry is doubtful on 4.18 (decision 5's upgrade path likely
  unavailable), and the `avc:selinux_audited` tracepoint is a RHEL
  backport — its presence must stay a startup census check, never an
  assumption. Kernel-version-sensitive claims in this design should be
  re-checked whenever a genuine RHEL 9 host enters the picture.
- **Denial storms** (background AVC denials were observed during validation):
  stream 1 is per-audited-event; audit
  subsystem rate-limiting applies, but the sensor adds a per-interval
  emission cap with an overflow counter (never silently drop without
  counting).

## Alternatives Considered

- **BPF LSM hooks** — rejected for the critical path: silently inert
  without `bpf` in `lsm=` (proven on lintap-dev); adds nothing over the
  avc-layer hooks even where active (as in the validation environment).
- **auditd/netlink audit consumption** — rejected by the brief (no auditd
  dependency; the superseded POC's whole failure mode).
- **Per-event allow-side emission** — rejected: 12k/s measured; fop
  lesson.
- **Userspace-only dedup** — rejected: pushes 12k/s through the ring
  buffer to dedup what the kernel map dedups for free; in-kernel dedup
  reduces steady-state ring traffic to ~zero.
- **`security_transition_sid` as the transition hook** — computation
  point, fires per exec/create whether or not a transition results
  (22-28/s measured vs ~2/s commits) and the result SID is in an output
  param (needs fexit/kretprobe gymnastics); `selinux_bprm_committed_creds`
  observes actual committed transitions with both SIDs readable.

## Decisions (human-decided 2026-09-17; formerly Open Questions)

1. **Resolution strategy:** prototype R1 (sidtab string-cache read) in
   slice 1, strictly timeboxed; R2+R3 composite is the shipping fallback
   if R1 fails verification or the policy-reload test. Adopt/reject
   outcome gets recorded here.
2. **Interaction-stream permission representation: row per permission.**
   ETL explodes the requested mask so the parquet directly matches the
   acceptance tuple (src, tgt, class, permission); eventCount semantics
   are per-permission; EPL groups on the exploded permission column.
3. **MessageType names frozen now:** `SELINUX_AVC`, `SELINUX_TRANSITION`,
   `SELINUX_INTERACTION`; parquet subdirs `selinux_avc/`,
   `selinux_transition/`, `selinux_interaction/`. No renaming after data
   lands.
4. **Flush policy: 30 s default, skip zero-delta tuples.** Sweeps emit
   only tuples with activity since the last flush; quiet tuples cost
   nothing after their novel emission.
5. **fentry: overhead-gated upgrade.** kprobe ships; measure real tracer
   overhead against acceptance criterion 4 during implementation, and only
   verify/switch to fentry if the kprobe tier fails or crowds that gate.
   *(2026-09-18 note: in the RHEL 8.10 validation environment, 4.18 likely lacks
   fentry trampolines entirely — this decision's upgrade path may be moot
   on that tier; fentry/fexit remains worth one attempt only as a
   possible workaround for the noaudit EINVAL.)*

## Open Questions

None blocking. Slice-1 outputs to record back here: R1 adopt/reject, the
`avc_has_perm_noaudit` rate/cardinality confirmation, and the measured
tracer overhead (decision 5's gate).
