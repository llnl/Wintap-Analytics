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

**Review + human response (2026-08-25):** the proposal passed designer review
(approved in principle; see the proposal's §Designer Review) and the human
responded with three direction updates recorded in §Human Review Response:
relative paths get **resolved to absolute** (new precondition slice fop-12 —
ground-truth accuracy is the goal), summary-record identity is stamped at
first occurrence, and the aggregation direction is formally amended —
**(pid, path, op)-level aggregation with grouped totals and min/max
timestamps over short intervals is acceptable for all op classes**, with
emit-first semantics. The OSS sensor survey stays deferred by explicit
direction. Next work: fop-12, then fop-11 per the proposal + review
conditions.

**Milestone wrap-up (late 2026-08-25):** `fop-12` is now implemented and field-
reviewed through the `fd=0` and `dirfd`/`cwd` follow-ons, but it is still not
accepted as the hard precondition for `fop-11`. The newest evidence says
`resolved_dirfd` materially helps while `resolved_cwd` is negligible, yet
`relative_open_resolve_miss` and the `(relative)` prefix bucket remain too high
to safely aggregate on `(pid, path, op)`. Treat `fop-11` as still blocked.
Milestone closeout + next-fix hypotheses are captured in
[[wiki/work/optimize-fileops-poller/milestone-2026-08-25-phase2-wrapup]].

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

    Also read, in order — they carry the current decisions:

    - wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md
      (including §Designer Review and §Human Review Response)

    Prior state: fop-08/fop-09/fop-10 are implemented and deployed. The ring
    no longer overflows (ring_fail_total=0 in all recent bundles); the active
    loss signal is the bounded userspace sender queue under some load phases.
    fop-08 full acceptance still owes a differential-harness rerun.

    Goal for the next pass: treat fop-12 as partially successful but still
    incomplete, and do not start fop-11 until the remaining relative/openat
    identity gap is addressed. Use the milestone wrap-up page plus
    verification.md to decide the next narrow design step.

    fop-12 current state (precondition): base R1, the `fd=0` fix, and the
    `dirfd`/`cwd` follow-on are all implemented. The latest evidence says the
    dominant remaining unresolved class is non-`AT_FDCWD` relative opens whose
    base directory fd path cannot be recovered cheaply enough in userspace by
    decode time. The next step is no longer "implement fop-12" but "design the
    next narrow fix for the unresolved path-identity floor." Read the
    milestone wrap-up page and verification.md first. Keep the existing human
    decisions: do NOT canonicalize absolute-path opens, and keep A4 (distinct
    `Mmap`) out of this pass.

    fop-11 scope (amended direction, 2026-08-25, still blocked): short-interval aggregation
    to the (pid, path, op) level with repeat count, grouped totals (bytes
    etc.), and min/max timestamps — acceptable for ALL op classes. Emit-first
    semantics: the first distinct occurrence in a window emits immediately
    and unchanged; only repeats fold into per-interval summary records.
    Hard conditions: summary-record process identity is stamped at first
    occurrence (never resolved at flush); absolute-path keys via fop-12;
    and the Esper composition rules from the handoff's "Esper-Layer
    Findings" section — File schema gains an explicit repeat-count field
    (default 1) and first/last timestamps, file.epl switches from count(*)
    to sum(<count field>) and takes min/max over the new timestamp fields,
    and the aggregation interval stays well under the 10s Esper batch.
    Honoring those rules makes fop-11 a pure performance change at the
    parquet output (File rows are already 10s aggregates on disk today).
    Layer choice per the designer review: userspace pre-enqueue dedup first
    (reuse the fop-10 measurement dictionary; no verifier spike needed);
    kernel promotion only if ring pressure or poller CPU returns. Sampling
    remains excluded. Sequencing open-first is fine but is not a boundary. Do
    not start this slice until the path-identity precondition is explicitly
    re-cleared.

    Also approved 2026-08-25, fold into these slices where they fit
    naturally: A1 platform-aware path-case policy function (Windows
    lowercases, Linux preserves case; single extraction point), A2 kernel
    timestamps, A3 (s_dev, i_ino) emission in CO-RE records, P3 sampled
    sender cost-split measurement. A4 (distinct Mmap activity type) is
    approved but deliberately deferred to its own future feature enhancement
    — do NOT fold it into these slices; keep mmap collapsing to Read for now
    so stream content stays stable through fop-12/fop-11.

    Acceptance for this pass:

    1. Builds: tracers make clean && make (if touched); dotnet build
       wintap/Lintap.csproj with 0 errors.
    2. Revised differential contract holds on drop-free harness runs:
       op-scoped distinct-tuple equality, count conservation, and byte-total
       conservation for aggregated op classes; strict per-event parity for
       any op class not yet aggregated. compare_fileops.py must learn the
       summary-record shape and count/byte columns.
    3. Schema recorded before coding: repeat-metadata field names, count=1
       default for non-aggregated rows, downstream note (Esper,
       DirectParquetSink, Wintappy models).
    4. Field measurement: queue depth/high-water/drops versus the fop-10-era
       bundles under comparable load; ring_fail_total stays 0. Record summary
       statistics only.

    Constraints:

    - Emit-first is non-negotiable: distinct activity keeps per-event
      immediacy; only repeats aggregate.
    - No sampling; no silent drops — every reduction is counted and logged.
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

## fop-12 Resolution Analysis + Additional Win Candidates (2026-08-25)

Source-grounded suggestions for the implementing agent. File/line references
are to `../wintap` as of this writing; re-verify before relying on them.

### Relative-path resolution options, ranked

**R1 — readlink `/proc/<pid>/fd/<fd>` at decode, pre-enqueue (recommended).**
The open-exit programs already emit the returned fd in the record
(`file_ops_tracer.bpf.c` §t_open_exit/§trace_openat call
`emit_file_event_saved(pid, st.filename, fd, ...)`), so userspace has
(pid, fd, raw path) at decode with no tracer change. The kernel resolves
everything — symlinks, `.`/`..`, dirfd-relative lookups — in one readlink,
and the poller thread has ample headroom (0.1–0.2% CPU). It MUST run
pre-enqueue on the poller, never on the sender: under queue backlog the
sender processes events after producers exit (the same timing argument as
identity stamping). Failure modes to count, not hide: fd closed before the
poller decodes (open→close faster than ring delivery) or producer already
exited → readlink fails. Fallback: keep the raw relative path plus a
resolution-status marker, and log resolved/miss counters in the 60s line so
the miss rate is a measured number.

**R2 — cwd/dirfd join (fallback only, if R1's measured miss rate is
material).** readlink `/proc/<pid>/cwd` and lexically join the relative path.
Weaknesses: `openat_state` does not capture the dirfd today (struct holds
only filename+flags — a tracer change would be needed for non-AT_FDCWD
opens); a chdir between syscall and readlink races; lexical `..` collapse is
wrong across symlinks. A short-TTL per-pid cwd cache would halve its syscall
cost if it is ever needed.

**R3 — kernel-side resolution: not viable on RHEL8 4.18.** `bpf_d_path` is
restricted to fentry/LSM/iterator program types and unavailable to these
tracepoints; manual dentry walks are verifier-hostile. This reconfirms the
deferred fentry migration as the only kernel path — unchanged.

**DECIDED 2026-08-25 (human sign-off): base R1 only.** Resolve
relative/openat paths via fd-readlink; absolute-path opens keep today's
as-requested form. The optional extension — canonicalizing ALL opens through
the same readlink for uniform identity — was considered and explicitly NOT
taken now: it changes stream content for absolute symlink paths (e.g.
`/etc/alternatives/*`), and the as-requested path has security value of its
own (symlink-mediated access looks different from direct access). It remains
a documented future option; if ever taken, carry both paths (schema
addition).

### Deeper accuracy wins found during this analysis

- **A1 — Platform-aware path-case policy (DECIDED 2026-08-25).**
  `NormalizeFilePath` ends with `ToLowerInvariant()` (`FileOpsSensor.cs:895`).
  Linux filesystems are case-sensitive: `/tmp/A` and `/tmp/a` are distinct
  files conflated in the emitted stream, the data-root filter, fop-11 dedup
  keys, and the differential comparator identity. Human direction: the
  lowercasing exists specifically for Windows filesystems — make it
  configurable via a platform-policy function/global (stub: Windows →
  lowercase, Linux → preserve case) that can grow richer over time (e.g.
  per-mount case sensitivity). Apply the same policy consistently to the
  `_dataRootLower` comparison and `compare_fileops.py`. On Linux this also
  deletes a per-event string allocation. Note: `file.epl` groups by
  `file.path`, so the policy defines aggregation identity on both platforms —
  keep it in one place.
- **A2 — Kernel timestamps (fop-07 U5), urgency raised by fop-11.**
  `TimestampNs` is still decoded nowhere; EventTime is `DateTime.UtcNow` at
  poller decode (`FileOpsSensor.cs:275`). Decode-time stamping is close to
  arrival time, but ring/wakeup batching adds up to ~100ms and fop-11's
  min/max repeat timestamps and grouped intervals should be real syscall
  times, not dequeue times. The once-computed monotonic→wallclock offset is
  cheap; do it in or before fop-11.
- **A3 — Emit (s_dev, i_ino) in records.** The CO-RE tier already reads
  `f_inode` for `is_regular_fd` (`file_ops_tracer.bpf.c:240`); `i_ino` and
  the superblock `s_dev` are two more `BPF_CORE_READ`s, +12–16B on the
  compact record. Payoffs: collision-free aggregation identity
  ((pid, dev:ino, op) needs no path hashing at all), validation/repair of
  `_fdToPath` entries against fd/PID reuse, robustness across hard links and
  renames, and attribution for fd ops whose open was never seen. Strong
  companion to fop-11/fop-12; CO-RE tier only.
- **A4 — Stop collapsing mmap into Read.** Decode maps op 5 → `Read`
  (`FileOpsSensor.cs:263`). File-backed mmap is loading/execution-relevant
  signal — and the measured churn is dominated by library trees (`/lib64`,
  `/usr`) — so the collapse erases exactly the distinction that load
  represents. The Esper layer makes the cost/benefit concrete: `file.epl`
  groups output rows by `(file.path, PidHash, PID, activityType,
  ProcessName)`, so today a process that maps AND byte-reads the same file
  produces one merged "Read" row — "was this file executed/loaded or read as
  data?" is unanswerable from the recorded stream. A distinct `Mmap`
  activity type costs at most one extra aggregated row per (pid, path) per
  10s batch — negligible volume — and recovers a signal class security
  analytics care about (code loading vs data access). `bytesRequested` for
  mmap rows is the mapped length, which also stops polluting read byte sums.
  **DECIDED 2026-08-25 (human sign-off): approved — but as its own future
  feature enhancement, implemented later, NOT part of the fop-12/fop-11
  slices.** Recorded in the implementation plan's Phase-2 future tasks; the
  downstream note (Wintappy models keying on activityType) goes with it.
- **A5 — comm truncation.** Kernel `comm` is 16 bytes; identity stamping
  already substitutes the resolved process name on cache hits — record the
  remaining stamp-miss gap as known, no action proposed.

### Deeper performance wins

- **P1 —** fop-11 pre-enqueue dedup remains the big sender lever: it cuts
  queue volume and per-event Esper sends by the measured repeat share
  (52.7–83.7% of opens; read/write repeats now also in scope per the amended
  direction).
- **P2 —** A1 doubles as a perf fix (one fewer allocation per event on the
  hot decode path).
- **P3 — Measure the sender-side cost split before optimizing it further.**
  Add sampled per-stage timing (every Nth event) for stamp-hit vs
  resolve-miss vs `SendEventBean` to the 60s log. Whether the next lever
  after dedup is Esper-side batching or more resolve work should be decided
  from this number, not intuition.
- **P4 —** Queue drop policy is `drop_newest`; under saturation `drop_oldest`
  favors recency instead of history. Either is defensible — record the choice
  as deliberate in the component page at closeout.

### Esper-Layer Findings (2026-08-25) — fop-11 is a pure perf change at the output

Extending the analysis into the Esper stream and its aggregation queries
(human-requested) produced the most important reframing of this phase:

**File telemetry is already aggregate-only on disk.** In the deployed
configuration (DirectParquetSink off), File events reach parquet exclusively
through `file.epl`, which batches into 10-second windows and groups by
`(file.path, PidHash, PID, activityType, ProcessName)`, emitting
`count(*) as eventCount`, `sum(bytesRequested)`, `min(eventTime) as
firstSeen`, `max(eventTime) as lastSeen`. `default.epl` explicitly excludes
`File` from per-event pass-through.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/esper/file.epl; ../wintap/wintap/core/etl/esper/default.epl -->

Consequences:

1. **The fop-11 information tradeoff largely evaporates.** Per-repeat rows
   and per-repeat timestamps already die in the 10s time_batch today; the
   recorded output has always been count/sum/min/max-shaped. A pre-enqueue
   aggregation at (pid, path, op) with count, byte totals, and min/max
   timestamps over an interval ≤ the Esper batch (1s « 10s) composes
   losslessly with `file.epl` — sums of sums, min of mins, max of maxes —
   meaning **fop-11 changes the parquet output not at all** when the
   composition rules below are honored. The emit-first rule still matters for
   any *live* Esper consumers (plugins/user EPL see the stream pre-batch),
   which is why it stays.
2. **Composition rules — these become fop-11 hard conditions:**
   - `count(*)` counts rows: a summary row worth N repeats would count as 1.
     The File schema needs an explicit repeat-count field (default 1) and
     `file.epl` must switch to `sum(<count field>)`.
   - `min/max(eventTime)` over rows would return summary-emission times: the
     schema needs first/last timestamps on the event (e.g. eventTime = first
     occurrence + a lastSeen field) and `file.epl` min/max updated to use
     them.
   - `sum(bytesRequested)` composes only if summary rows carry summed bytes
     (already planned in the amended direction).
3. **The comparator is closer to done than assumed.** It already compares
   distinct tuples of the *aggregated* parquet rows — per-event parity at the
   parquet level never existed. Count conservation reduces to asserting the
   existing `eventCount` column (and byte sums) balance between baseline and
   candidate.
4. **A2 (kernel timestamps) upgrades existing output accuracy, not just
   fop-11's:** today's `firstSeen`/`lastSeen` columns record userspace decode
   times, so their accuracy already degrades under any poller lag; kernel
   timestamps fix a live column, not a future one.
5. **Perf mechanics of the win:** every File event currently pays Esper
   filter evaluation + group-by hash + accumulator update inside synchronous
   `SendEventBean` on the sender thread. Pre-enqueue dedup cuts Esper input
   rows by the measured repeat share (52.7–83.7% of opens) on top of the
   queue/stamping work it already saves — the Esper group-by then aggregates
   mostly-unique rows.
6. **PidHash quality shapes group identity:** `file.epl` groups by PidHash,
   so identity stamping (fop-08 follow-on) also protects output row quality —
   a resolve-miss fragments or merges grouped rows, not just a column value.

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
