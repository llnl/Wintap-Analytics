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
last_validated: 2026-08-26
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

**Gap analysis complete (2026-08-25):** the miss floor is diagnosed as
structural — all fop-12 fallbacks are decode-time `/proc` reads racing
millisecond-lived producers (`dirfd_lookup_miss ≈ relative_open_resolve_miss`
proves both readlinks die together), and the tracer discards the
`O_DIRECTORY` opens that would teach userspace what dirfds point at. The fix
is **fop-13**: a measurement micro-slice (13a), then kernel-time directory
identity + file dev:ino in one record-format slice (13b), after which fop-11
unblocks on the dev:ino aggregation key independent of the residual path
tail. Full analysis, ranked fixes, non-fixes, and acceptance criteria:
[[wiki/work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25]].

**fop-13 implemented locally (2026-08-25):** both slices are coded, built,
and locally tested — DIR_OPEN records, the dir-identity index, file/dirfd
(s_dev, i_ino) emission, the miss-cause split, comparator upgrade matching,
the dirfd-relative workload scenario, and a `resolve=` triage extract in the
diagnostics collector. See verification.md §fop-13a/fop-13b Local Code Slice.

**fop-12/fop-13 CLOSED (2026-08-25, human acceptance):** field evidence met
the bar — miss floor ~8k/min → 0-131/min with `resolved_dir_index` dominant,
producer-dead diagnosis confirmed, `(relative)` out of top prefixes, ring 0,
4x queue validated (drops=0 at ~437k depth). See verification.md §fop-13
Closeout. The differential rerun folds into fop-11's standing gate.

**fop-11 implemented locally (2026-08-25):** emit-first (pid, path, op)
aggregation with 1000ms window, identity-at-first-occurrence summaries,
file.epl composition change (parquet columns unchanged — eventCount now
counts raw events), P3 send-cost sampling, queue default raised to 524288,
comparator count-conservation weighting, 9 aggregator unit tests + synthetic
comparator scenarios green. Kill switch: WINTAP_FILEOPS_AGG_ENABLED=false.
See verification.md §fop-11 Local Code Slice.

**fop-13c/fop-13d FIELD-ACCEPTED (2026-08-26, bundle 053404Z):** eviction/
miss decorrelation confirmed at the 65,536-cap LRU index (29,469 resolves vs
354 misses in the burst minute under 68k/interval churn). Sensor path is
clean end to end. The active loss point moved downstream: the ETL
serializer/parquet-writer stage dropped ~18k rows/min against its 10,000-row
default caps during the heavy window — dispositioned as candidate **fop-14
(downstream durability, measurement-first)** in the implementation plan;
dedup cannot shrink that stage (Esper output is distinct-group-driven).
**Remaining fop-11 gates: kill-switch A/B differential + one bundle from the
updated collector (duckdb/fileops-parquet-sanity.txt) — confirm the host has
pulled the collector update.**

## Bundle Reviewer Prompt (fop-11 collector, 2026-08-25)

Use this prompt for the field-side reviewer processing bundles produced by
the updated `collect-lintap-diagnostics.sh`. The reviewer runs on the
read-only field host: output must be a transcription-ready summary
(summary statistics, ranges, and deltas only — no raw event payloads).

    You are reviewing a Lintap runtime diagnostics bundle on the read-only
    field host. Produce a summary suitable for dev-side transcription into
    the wiki: bundle id, lintap_pid, installed hashes, then findings as
    summary statistics only (counts, rates, ranges, per-interval deltas).
    Do not include raw event data or file contents beyond counter lines.

    Review these bundle files, each against its question:

    1. journal/lintap-file-log-fileops-agg.txt — aggregation health.
       Report: enabled/window_ms; the fold ratio per interval
       (repeats_folded / (first_emits + repeats_folded)) and its range
       (expectation from fop-10: roughly 50-80% during load);
       cap_bypass and summary_enqueue_fail (both must be 0 or near-0 —
       nonzero is a finding); entries trend across the bundle (bounded,
       not ratcheting); bytes_clamped (nonzero is worth noting).
    2. journal/lintap-file-log-fileops-sender.txt — P3 sender cost.
       Report the send_sample_avg_us range and samples count. Sanity-check
       headroom: (first_emits + summaries) per interval / 60 gives the
       sender's required events/s; compare against 1e6/send_sample_avg_us
       as its approximate capacity. State the margin.
    3. Queue section of the counters lines — depth, high_water, drops vs
       capacity, compared against the fop-13-era bundles (high_water was
       27k-44k in the first fop-11 bundles vs ~437k pre-aggregation).
       Any nonzero drops= is a finding.
    4. journal/lintap-file-log-fileops-resolve.txt — path identity must not
       regress: miss levels (0-131/min range expected), resolved_dir_index
       share, miss_producer_dead/alive split, dir_index size/evictions.
       Post-fop-13d (LRU index, cap 65536): during scan windows,
       dir_index_evictions must NOT correlate with
       relative_open_resolve_miss any more — evictions with a stable miss
       floor is healthy LRU aging; evictions with a miss spike would mean
       the hot set exceeds even the new cap (report it prominently).
    5. journal/lintap-file-log-esper-errors.txt — MUST contain no file.epl
       compile/deploy failures. Any Esper statement error here is a
       stop-ship finding: it means File serialization may be broken while
       every sensor counter still looks healthy.
    6. duckdb/fileops-parquet-sanity.txt — the end-to-end composition
       proof. Healthy: raw_events > rows under load (sum(eventCount)
       exceeding row count proves aggregation composed through Esper);
       aggregated_rows > 0; zero_first_seen_rows = 0; min_first_seen and
       max_last_seen are plausible current FileTime values. If the
       composition query fails with an eventCount column error, the
       deployed build predates fop-11 — report that prominently.
    7. kernel=[...] — ring_fail_total must stay 0 for all op classes;
       report dir_open emitted volume.

    Close with: overall verdict (healthy / findings / stop-ship), the two
    or three numbers the dev side must record verbatim, and what the next
    most useful capture would be.

The A/B differential (kill-switch run) is a separate procedure — see the
code-development prompt below.

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

    UPDATE 2026-08-27: gate 1 (kill-switch A/B) PASSED on spk16 —
    results /var/tmp/fop11-ab-results-20260827T032142Z, missing=0. The
    initial FAILs root-caused a pre-existing n² eventCount inflation in
    file.epl/registry.epl (ungrouped AgentId → Esper one-row-per-event
    semantics), fixed in ../wintap 0e01783 — REQUIRED in any deploy, and
    it invalidates all pre-fix parquet eventCount analyses (File/Registry,
    all hosts including Windows). Remaining before fop-11 acceptance:
    gate 2 (collector bundle) and a byte-total-conservation check or
    explicit waiver (comparator verifies counts + distinct tuples only).
    fop-14 severity must be RE-MEASURED post-0e01783 (prior number was
    per-event-row volume). Details: wiki/log.md 2026-08-26/27;
    implementation_plan fop-11/fop-14 entries.

    Goal for the next pass (state as of 2026-08-26): fop-12/fop-13 and
    fop-13c/fop-13d are CLOSED by human acceptance; fop-11 is deployed and
    healthy in field bundles but owes two formal gates:
    1. The kill-switch A/B differential — AUTOMATED (2026-08-26): run as
       root on the field host:
         validation/fileops-differential/run_fop11_ab.sh
       One command does both phases (OFF baseline via the kill switch, ON
       candidate), verifies the agg state from the live counter log,
       harvests each phase's rows by non-overlapping firstSeen windows +
       work-dir prefix (row-level, immune to parquet file-boundary mixing),
       uses service restarts as flush boundaries, refuses to pass if
       serializer backlog-drop warnings appeared during a phase (exit 3 =
       INVALID, fix fop-14 caps first), and runs the count-conserving
       comparator (--ignore-pid --path-prefix --fail-on-unmatched-relative).
       Exit 0 = PASS; results + summary.txt in
       /var/tmp/fop11-ab-results-<ts>/. Aggregation is restored ON even on
       failure/interrupt. Also closes the folded fop-13 differential
       obligation.
    2. One bundle from the UPDATED collector carrying
       duckdb/fileops-parquet-sanity.txt (raw_events > rows is the Esper
       composition proof) — confirm the host pulled the collector update
       first.
    In parallel, the human decides fop-14 (downstream durability): step 1 is
    a config-only serializer-cap experiment on the host; see the
    implementation plan's fop-14 entry.
    Background for what landed: verification.md §fop-11 Local Code Slice,
    §fop-13c/fop-13d + F2/F4, and the fop-11 proposal (+§Designer Review,
    §Human Review Response, §Esper-Layer Addendum) for semantics.

    Deployment steps (RHEL8 field host):
    1. UPDATED 2026-08-25 (fop-13c/13d hardening landed after fop-11): the
       ring record format changed again (path records carry mnt_ns, +8B).
       Rebuild tracers ON THE HOST (make clean && make) AND rebuild/install
       Lintap together — a mixed deploy misreads the new field. Keep the
       validated env setting WINTAP_FILEOPS_MAX_QUEUE_EVENTS if present (the
       code default is now 524288 anyway); the dir index is now LRU with
       default cap 65536 (WINTAP_FILEOPS_DIR_INDEX_MAX to override).
    2. Run the deterministic workload and collect a smoke bundle, then a
       longer bundle under normal host load. The 60s line now carries
       agg=[...] and sender=[...] sections.
    3. Kill switch for A/B: WINTAP_FILEOPS_AGG_ENABLED=false restores
       per-event behavior on the same build.

    Acceptance vs the fop-13-era bundles:
    1. Queue drops collapse under comparable load (repeats_folded should run
       at 50-80% of open volume plus read/write repeats); depth/high_water
       shrink materially.
    2. A/B differential (baseline = aggregation disabled or a fop-13 build;
       candidate = aggregation enabled) passes with the count-conserving
       comparator; use --fail-on-unmatched-relative. This run also closes
       the folded fop-13 differential obligation.
    3. Counter reconciliation: first_emits + repeats_folded ≈ post-filter
       consumed; summaries ≈ expired entries; sum(eventCount) in the parquet
       output ≈ raw event count; summary_enqueue_fail=0; cap_bypass ~0.
    4. ring_fail_total stays 0; resolve=[...] health holds (fop-13 counters
       unchanged by this slice).
    5. Record send_sample_avg_us — the P3 number that decides whether any
       post-fop-11 sender work is warranted.
    6. Esper/parquet sanity: firstSeen/lastSeen sane (no zeros), eventCount
       sums plausible vs kernel emitted totals.

    Keep the existing human decisions: do NOT canonicalize absolute-path
    opens, keep A4 (distinct `Mmap`) out of this pass, no sampling. Deferred
    parallel slices remain available: fop-13c (mnt_ns index keying), F2/F4
    hardening (comparator matcher count-consumption; more DIR_OPEN tests).

    Process constraint (policy, 2026-08-25): the field-side clone is
    READ-ONLY — no commits from that system. Field bundle reviews come back
    as summaries and are transcribed into verification.md/log.md on the
    dev side by the wiki maintainer. Design diagnostics extraction so the
    collector bundle itself carries everything a review needs (that is what
    the agg=/sender=/resolve= triage extracts, the esper-errors extract, and
    duckdb/fileops-parquet-sanity.txt are for).

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
