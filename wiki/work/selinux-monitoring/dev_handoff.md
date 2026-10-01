---
title: "Dev Handoff: SELinux Monitoring"
type: concept
confidence: medium
grounded_by:
  - wiki/work/selinux-monitoring/design.md
  - wiki/work/selinux-monitoring/implementation_plan.md
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
policy: agent-editable
last_validated: 2026-09-18
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: wiki/work/selinux-monitoring/dev_handoff.md
tags: [feature-work, selinux, ebpf, lintap, dev-handoff]
---

# Dev Handoff: SELinux Monitoring

## Copy/Paste Prompt

Use this prompt to hand the work to a code-development agent:

    Switch to code-development mode for the selinux-monitoring feature.
    This handoff authorizes changes
    in ../wintap under wintap/platform/linux/sensor/ebpf/,
    wintap/core/etl/, and additive-only changes in wintap/collect/models/.

    Read first, in order:
    - AGENTS.md (confirm code-development mode and the ../wintap
      authorization in wiki/work/selinux-monitoring/dev_handoff.md)
    - wiki/work/selinux-monitoring/brief.md   (frozen acceptance criteria)
    - wiki/work/selinux-monitoring/design.md  (decided architecture)
    - wiki/work/selinux-monitoring/implementation_plan.md (sel-01..05)
    - wiki/work/selinux-monitoring/spike.md   (validation evidence + traps)
    - wiki/workflow/lintap-dev-field-workflow.md (field rules)

    Goal for this session: execute the next open sel-NN slice from the
    implementation plan's done checklist, honoring its testing gates.

    Do NOT read the "Sealed — human estimates" section of
    wiki/work/selinux-monitoring/interview.md.

## Handoff Summary

SELinux becomes a first-class Lintap eBPF event domain: three streams on
spike-verified attach points — `SELINUX_AVC` from the `avc:selinux_audited`
tracepoint (context strings at capture), `SELINUX_TRANSITION` from kprobe
`selinux_bprm_committed_creds` (osid≠sid filter in-kernel),
`SELINUX_INTERACTION` from a kprobe — preferred hook
**`avc_has_perm_noaudit`** where attachable, `avc_has_perm` wrapper as
the validated fallback in the RHEL 8.10 validation environment, behind a
16,384-entry in-kernel LRU emit-first dedup map keyed
(ssid, tsid, tclass, requested), flushed every 30 s skipping zero-delta
tuples. All design decisions are settled (design.md §Decisions,
2026-09-17); names are FROZEN: `SELINUX_AVC` / `SELINUX_TRANSITION` /
`SELINUX_INTERACTION`.

Measured envelope from validation: checks 2.4-13k/s, 421 distinct
tuples (top-10 ≈ 89% of volume), transitions ~2/s commits, audited events
~0/s baseline.

**Environment correction (2026-09-18, sel-02):** validation used
**RHEL 8.10 with a 4.18-series kernel**, not RHEL 9-class as originally
assumed (the brief lists RHEL 8 as a v1 non-goal; contradiction flagged
there, scope decision pending). SELinux was **Permissive**, BTF and the
required build/audit tooling were present, and **bpftrace was absent**.
The tracepoint exists as a RHEL backport into 4.18; fentry on 4.18 is
doubtful.

## Authorization And Boundaries

- **Authorized:** `../wintap` — new tracer under
  `wintap/platform/linux/sensor/ebpf/tracers/` + Makefile; new sensor
  class(es) alongside FileOpsSensor; Linux sensor registration; new
  `selinux.epl`; new/extended serializer under `core/etl/extract/`;
  **additive-only** WintapMessage types.
- **Authorized (this repo):** `validation/selinux-acceptance/` workload +
  DuckDB queries (sel-05); wiki updates per closeout duties.
- **Not authorized:** changes to existing MessageTypes/schemas/PidHash
  semantics; Windows sensor code; the legacy auditd batch path in
  `../Lintap`; Wintappy; any auditd runtime dependency in the capture
  path. Windows build must compile untouched.

## Primary Sources For The Dev Agent

- Pattern to copy, kernel side:
  `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`
  (ringbuf + stats array + self-PID filter + batched wakeups + CO-RE
  idioms) and `tracers/Makefile`.
- Pattern to copy, userspace: `FileOpsSensor.cs` (consume thread, bounded
  send queue, counters log line, monotonic→realtime offset) and
  `FileOpsAggregator.cs` (emit-first semantics — the kernel map replaces
  its dictionary, same contract language).
- EPL/serializer: `core/etl/esper/file.epl` + `extract/FileSerializer.cs`;
  the group-by invariant is documented in
  [[wiki/component/fileops-event-pipeline]].
- Attach-point ground truth and traps: spike.md — the preferred
  production interaction hook is `avc_has_perm_noaudit` where attachable
  (it covers the inode fast path the wrapper misses); in the RHEL 8.10
  validation environment it rejects perf kprobe attach, so the validated
  fallback is the
  `avc_has_perm` wrapper with an explicit coverage caveat (see the trap
  below); `avc_audit` is inlined (audit-path fallback tier is
  `slow_avc_audit`); BPF LSM attaches-but-never-fires without `bpf` in
  lsm= (do not use); tracepoint format fields; `ausearch -ts` wants
  `recent`, not a quoted datetime.
- **New trap (sel-02, RHEL 8.10):** `avc_has_perm_noaudit` is in kallsyms
  but perf-event kprobe creation returns **EINVAL (-22)** on the
  4.18-series validation kernel; the sensor's wrapper fallback is what
  actually runs there. Investigation order: tracefs `kprobe_events` probe
  on the symbol (separates perf-interface rejection from an unprobeable
  symbol), libbpf legacy kprobe opts, symbol+offset attach, one
  fentry/fexit attempt (doubtful on 4.18). Also: bpftrace is absent on
  the validation environment, so plan measurements around tracefs/bpftool.

## Recommended First Implementation Slice

**sel-01** (evidence, no production code) — it de-risks sel-02/03 and its
R1 adopt/reject outcome changes the resolver you build in sel-03. If the
session cannot reach the validation environment, sel-02 may proceed first
(tracer + skeleton are resolution-independent); note the reordering in the
plan.

**Status update (2026-09-18):** sel-02 was executed first — implementation
and smoke validation complete via wrapper fallback (all three streams
capturing in the RHEL 8.10 validation environment; evidence in
verification.md);
the formal checkbox stays open pending decode unit tests and the noaudit
attach resolution. **Next session priorities:** (1) the sel-03 gate — the
noaudit EINVAL investigation per the trap above, feeding either a fix or
a human scope decision (wrapper-only on 8.10 vs out-of-scope); (2) the
outstanding sel-01 items (R1 sidtab prototype, blob-offset handshake —
noaudit rate/cardinality measurement is superseded in this environment unless
the attach gets fixed); (3) sel-02 decode unit tests recorded green.
sel-03 resolver/flush work may proceed in parallel with (1).

## Non-Goals For This Slice (all slices)

Dashboards/UX, Wintappy DBT models, RHEL 8, auditd-based capture,
enforcing-mode rollout procedures (the validation environment is
Permissive; enforcing
re-verification is a follow-up), fentry unless the sel-05 overhead gate
demands it (decision 5).

## Testing Expectations

- **Packaged-service testing is the preferred validation path**
  (established sel-03, 2026-09-18): build and install the RPM, then run
  under the packaged service so the actual unit configuration is exercised,
  unlike manual `make run`. For focused SELinux tests, use the packaged
  environment configuration to explicitly enable the SELinux sensor and
  disable unrelated sensors (see the verification.md sel-03 config block
  for the known-good set). `WINTAP_API_URLS` is available to avoid local
  test-port conflicts.
- Per-slice tests in the implementation plan are gates, not suggestions;
  runs recorded in verification.md with commands + results.
- Cross-slice invariants: `ring_fail_total=0`; dedup count conservation
  (novel + folded = observed); EPL group-by rule; existing Linux
  process/file/network suites stay green; Windows targets still build.
- Validation runs follow [[wiki/workflow/lintap-dev-field-workflow]]:
  deploys pull and rebuild tracers in the validation environment (never
  ship arm64-built `*.bpf.o`); validation clones are read-only; evidence
  is retained as a minimized, sanitized digest; commits happen on the dev
  VM.

## Delegated To The Dev Agent

- Field naming within Wintap conventions (types/dirs are frozen; column
  spellings follow existing serializer style).
- Netlink-listener failure fallback (poll `/sys/fs/selinux/policy` vs
  restart) — record the choice in verification.md.
- Ring buffer size default and the string-field widths (design proposes
  256/256/32 with truncation counters).
- Whether resolver/flush logic splits into separate classes (follow the
  FileOpsAggregator precedent if so).

## Closeout Instructions

- Update wiki/work/selinux-monitoring/verification.md with commands run
  and results per slice (field evidence transcribed, clearly sourced).
- Tick the implementation_plan.md done checklist as slices complete;
  record sel-01 outcomes in design.md §Decisions.
- Append a concise entry to wiki/log.md for substantial progress.
- At feature close: promote durable facts to canonical pages (new
  `event_type/selinux-events`, likely a component page for the pipeline),
  update wiki/index.md, file follow-ups (dashboard feature, Wintappy
  bronze, RHEL 8 tier, enforcing-mode verification).
