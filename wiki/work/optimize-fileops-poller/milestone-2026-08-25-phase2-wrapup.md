---
title: "Milestone: FileOps Phase-2 Wrap-Up (2026-08-25)"
type: concept
confidence: medium
grounded_by:
  - wiki/work/optimize-fileops-poller/verification.md
  - wiki/work/optimize-fileops-poller/dev_handoff.md
  - wiki/work/optimize-fileops-poller/implementation_plan.md
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: file
audience: mixed
status: draft
source_paths: wiki/work/optimize-fileops-poller/milestone-2026-08-25-phase2-wrapup.md
tags: [feature-work, file-events, ebpf, linux-sensor, milestone, phase-2]
---

# Milestone: FileOps Phase-2 Wrap-Up (2026-08-25)

This page closes the current phase-2 implementation burst for
`optimize-fileops-poller` and captures the exact handoff state for the next
design/development pass.

## Milestone Outcome

The phase-2 work materially improved the FileOps pipeline and narrowed the
remaining problem, but it did not yet finish the path-identity precondition
needed to safely enable `fop-11` aggregation.

Current milestone verdict:

- Queue/ring health is much better than the pre-phase-2 state.
- `fop-10` produced enough evidence to justify the `fop-11` design direction.
- `fop-12` improved relative/openat path recovery, including a real new `dirfd`
  win.
- `fop-12` is still **not accepted** as complete, because too many relative
  opens still fail absolute-path recovery.
- `fop-11` should remain blocked until path identity is good enough that
  `(pid, path, op)` keys do not conflate distinct files.

## What Landed In Code

In `../wintap`:

- bounded userspace queue between ring-buffer decode and sender-path work
- active-process cache for File-event identity stamping
- startup-cached EventChannel config lookups
- pre-enqueue File identity stamping
- `fop-10` summary measurement counters in the 60s FileOps log
- `fop-12` relative/openat absolute-path recovery using `/proc/<pid>/fd/<fd>`
- Linux path-case preservation instead of unconditional lowercasing
- kernel monotonic timestamp conversion for File event wallclock time
- `fd=0` participation in the resolution/cache path
- `dirfd` carriage in tracer records plus `opened-fd -> cwd -> dirfd` fallback
  ordering with reason-split counters

In `Wintap-Analytics`:

- Linux-case-preserving comparator update in
  `validation/fileops-differential/compare_fileops.py`
- diagnostics bundle support for `/tmp/fileops-phase2-smoke`
- updated feature artifacts capturing the deployed evidence and the amended
  `fop-11` design direction

## Strongest Evidence

### Stability / Throughput

- Pre-phase-2 overnight evidence showed sustained kernel ring loss.
- After the queue/cache/identity changes, the active loss mode shifted away
  from the ring and onto the sender queue.
- In the more recent `fop-12` bundles, `ring_fail_total=0` stayed true in all
  reviewed intervals, and several reviewed windows also held `queue drops=0`.
<!-- SYNTHESIS: inferred from wiki/work/optimize-fileops-poller/verification.md bundle reviews for 20260825T172341Z, 20260825T184934Z, 20260825T203648Z, 20260825T225502Z, 20260825T232323Z, and 20260825T234559Z -->

### `fop-10` Gate Evidence

- The deployed measurement slice showed duplicate-open ratios high enough to
  justify a concrete `fop-11` proposal.
- Representative duplicate-open ratios were roughly `52.7%` to `83.7%`, often
  in the `60-80%` range.
- Dominant surviving emitters included `rpm`, `systemd`, `splunkd`, `git`, and
  `setroubleshoot*`.
- Dominant surviving prefixes included `/lib64`, `/usr`, `(relative)`, `/opt`,
  `/var`, and `/`.
<!-- SYNTHESIS: inferred from wiki/work/optimize-fileops-poller/verification.md §Root-Run Diagnostics Bundle Review (First Deployed fop-10 Build) -->

### `fop-12` Path-Recovery Evidence

- First deployed `fop-12` bundle proved the new resolution counters were live,
  but misses stayed high and `(relative)` remained a top prefix bucket.
- The `fd=0` fix recovered real additional resolution opportunity, but still
  left the relative bucket large.
- The `dirfd`/`cwd` follow-on proved that `dirfd` contributes materially while
  `cwd` contributes almost nothing in the sampled workload.
- In the latest short-smoke-correlated bundle, `resolved_dirfd` contributed
  roughly `548-958` recoveries per minute, while `resolved_cwd` was `0-1`.
- Even after that, `relative_open_resolve_miss` still sat around
  `7997-8814` in the smoke-window lines, and `(relative)` remained around
  `8162-10727` total.
<!-- SYNTHESIS: inferred from wiki/work/optimize-fileops-poller/verification.md §Root-Run Diagnostics Bundle Review entries for 20260825T225502Z, 20260825T232323Z, and 20260825T234559Z -->

## What We Now Know

1. The main no-loss-ish stabilization work was worthwhile.
2. `fop-10` was the right measurement slice and produced actionable design
   evidence.
3. `fop-11` should be userspace-first if/when it happens; the current loss mode
   is sender/queue-side, not ring-side.
4. `fop-12` improved path quality, but the unresolved class is now better
   defined: many remaining misses are non-`AT_FDCWD` relative opens whose base
   directory fd cannot be recovered cheaply enough in userspace at decode time.
5. `cwd` fallback is not the main answer for the current workload.
6. `dirfd` fallback helps, but not enough.

## Current Best Ideas For Fixes

These are the best next-step hypotheses from the current evidence, ordered from
most plausible / least disruptive to more invasive:

1. **Capture stronger open-time base identity in the tracer.**
   The dominant unresolved class now looks like "relative open with a non-
   `AT_FDCWD` base that is gone by userspace decode time." The most direct fix
   is to preserve more base-directory identity at capture time rather than
   relying on a later `/proc/<pid>/fd/<dirfd>` readlink.
2. **Emit `s_dev` / `i_ino` for CO-RE records and use that as the trusted
   aggregation identity where available.**
   This does not solve every fallback-tier path problem, but it could remove a
   large class of path-conflation risk for the CO-RE path and materially change
   the `fop-11` key story.
3. **Treat remaining unresolved relative opens as explicitly unfit for
   aggregation instead of silently using the raw relative string.**
   If `fop-11` eventually proceeds before perfect path recovery exists, it
   should only aggregate rows whose identity is proven safe. That may mean an
   explicit "unresolved relative" class stays per-event.
4. **Consider open-time canonical identity as a separate field instead of
   replacing the as-requested path.**
   The current human direction declined full canonicalization of absolute paths,
   but a dual-field model remains a future option if the design agent decides
   the sensor needs both user-requested path and canonical identity.
5. **Keep `cwd` fallback only as a minor supporting path, not the primary next
   investment.**
   The evidence so far does not justify spending the next design cycle on it.

## Recommended Next Pass

1. Do not start `fop-11` implementation yet.
2. Have the next design pass focus specifically on the remaining non-
   `AT_FDCWD` relative-open identity gap.
3. Decide whether the real next move is:
   - better open-time identity capture in the tracer,
   - `dev:ino`-based identity for CO-RE records,
   - or a split contract where only safe identities aggregate.
4. Preserve the current evidence as the milestone baseline for that decision.

## Commit Scope This Milestone

This milestone is suitable for commit/push in both repos because it includes:

- completed code changes already deployed/tested in `../wintap`
- synchronized validation and wiki artifacts in `Wintap-Analytics`
- a stable milestone conclusion for the next design review
