---
title: "Implementation Plan: SELinux Monitoring"
type: concept
confidence: medium
grounded_by:
  - wiki/work/selinux-monitoring/design.md
  - wiki/work/selinux-monitoring/spike.md
policy: agent-editable
last_validated: 2026-09-18
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: wiki/work/selinux-monitoring/implementation_plan.md
tags: [feature-work, selinux, ebpf, lintap, implementation-plan]
---

# Implementation Plan: SELinux Monitoring

Abbreviation for instruction units and commits: **`sel`** (sel-01 … sel-05).

## Scope

Implements [[wiki/work/selinux-monitoring/design]] (all five open questions
human-decided 2026-09-17): three SELinux streams — `SELINUX_AVC`
(tracepoint), `SELINUX_TRANSITION` (bprm-commit kprobe),
`SELINUX_INTERACTION` (avc_has_perm_noaudit kprobe + in-kernel 16k LRU
emit-first dedup, 30 s zero-delta-skipping flush) — through
tracer → sensor → EventChannel → Esper → serializer → `raw_sensor` parquet.
Code lands in `../wintap` per [[wiki/work/selinux-monitoring/dev_handoff]];
acceptance workload/queries land in this repo's `validation/`.

**Environment variance (2026-09-18, sel-02):** validation used
**RHEL 8.10 with a 4.18-series kernel**, not RHEL 9-class as the
brief/design assumed (and the brief lists RHEL 8
as a v1 non-goal; contradiction flagged there). Evidence so far transfers
(tracepoint backported into 4.18, wrapper kprobe works), with two
environment-specific consequences: `avc_has_perm_noaudit` kprobe attach fails
EINVAL (see the sel-03 gate below), and fentry support is doubtful on
4.18 (decision 5's upgrade path likely unavailable on this tier).

## Steps

### sel-01 — Validation evidence + R1 prototype (no production code)

Closes the three slice-1 measurements design.md defers to:

1. **`avc_has_perm_noaudit` rate + cardinality** — re-run the spike's
   hist-trigger method with the `avc_has_perm_noaudit` symbol
   in the validation environment. Expected same order as the wrapper (≥ 2.4-13k/s,
   cardinality low hundreds); confirms no double counting and final map
   sizing.
2. **R1 timeboxed prototype** — CO-RE read of the sidtab context-string
   cache from a throwaway probe. Verify on the validation kernel AND lintap-dev
   6.8; include a policy-reload survival test. Prerequisite check: BPF
   toolchain availability in the validation environment; if absent,
   cross-compile the CO-RE object with `-D__TARGET_ARCH_x86` on the dev VM
   and load it with bpftool in the validation environment.
   **Timebox: one working session. Outcome (adopt/reject) recorded in
   design.md §Decisions #1.** Reject ⇒ R2+R3 composite ships.
3. **cred→security blob-offset self-handshake** — prototype the startup
   validation (in-kernel read of own task's task_security_struct vs
   /proc/self/attr/current).

Deliverable: design.md updated with the three outcomes; probes stay
throwaway (extras/ or /tmp), nothing lands in `../wintap`.

### sel-02 — Kernel tracer + sensor skeleton

- `tracers/selinux_tracer.bpf.c`: three program groups, ringbuf, stats
  array, self-PID filter, LRU dedup map, per-stream ring_fail counters —
  per design §Kernel tracer. Makefile integration (CO-RE tier only).
- `SELinuxSensor.cs` skeleton: attach/census-at-startup (selinuxfs +
  tracepoint + kallsyms checks, mode logging, `WINTAP_SELINUX_ENABLED`
  gate, clean self-disable on non-SELinux hosts), ring consume thread,
  decode of the three record types, 60 s counters log line. No ETL wiring
  yet — counters prove capture.
- Tests: record decode unit tests (fixed byte fixtures for all three
  event structs); build on dev VM (`*.bpf.o` never deployed cross-arch).

### sel-03 — Sensor completion: resolution, dedup flush, identity

**GATE (added 2026-09-18):** decide the interaction hook strategy before
finalizing sel-03 — either a working `avc_has_perm_noaudit` attach on the
RHEL 8.10 validation environment (tracefs kprobe form, libbpf legacy opts, symbol+offset,
or fentry if kfunc support exists), or an explicit human scope decision
(wrapper-only coverage with the documented inode fast-path gap vs RHEL
8.10 out of scope per the brief's original non-goal). Resolver/flush work
may proceed in parallel; final acceptance depends on this.

- Mask decode from selinuxfs `class/*/perms/` (+ numeric tclass→string);
  unknown-bit counter.
- SID resolver per sel-01 outcome (R1, or R2+R3 composite with
  resolve-miss counters); numeric SIDs always shipped.
- Policy-epoch: SELinux netlink listener (`SELNL_MSG_POLICYLOAD`) → kernel
  map flush + learned-table drop + epoch stamp. Listener-death fallback
  (poll or restart) — dev agent's call, recorded in verification.
- Flush sweep (30 s, skip zero-delta), PidHash stamping via resolver,
  bounded send queue.
- Tests: dedup/flush semantics (novel emit, count fold, zero-delta skip,
  LRU re-novel), resolver fallback paths, epoch flush.

### sel-04 — ETL: message types, EPL, serializer

- Additive WintapMessage types `SELINUX_AVC` / `SELINUX_TRANSITION` /
  `SELINUX_INTERACTION` (frozen names; row-per-permission explode for the
  interaction stream at ETL).
- `selinux.epl` — **every non-aggregated select column in the group by**
  (the n² eventCount rule); 10 s time_batch.
- Serializer flush to `raw_sensor` partitioned parquet
  (`selinux_avc/`, `selinux_transition/`, `selinux_interaction/`).
- Tests: EPL compile/deploy smoke, serializer schema assertions, kill
  switch on/off.

### sel-05 — Validation-environment acceptance (the four frozen criteria)

- Deploy per validation workflow (pull and rebuild tracers in the
  validation environment).
- Workload + DuckDB acceptance queries authored in this repo
  (`validation/selinux-acceptance/`): provoked denial vs ausearch
  (criterion 1 — same-event field match), known transitions (criterion 2),
  scripted interaction workload + DuckDB reproduction (criterion 3),
  overhead/no-loss (criterion 4: `ring_fail_total=0`, CPU with tracer
  on/off alongside existing tracers — also decision 5's fentry gate).
- Retain a minimized, sanitized evidence digest; transcribe the technical
  results into verification.md.

## Files Likely To Change

`../wintap` (authorized by the dev handoff):
- `wintap/platform/linux/sensor/ebpf/tracers/selinux_tracer.bpf.c` (new),
  `tracers/Makefile`
- `wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs` (new; resolver +
  flush helpers may split into own files per FileOpsAggregator precedent)
- Linux platform sensor registration (wherever FileOpsSensor is wired)
- `wintap/collect/models/` — additive WintapMessage types only
- `wintap/core/etl/esper/selinux.epl` (new); serializer under
  `core/etl/extract/` (new class or generic extension)

This repo: `validation/selinux-acceptance/` (new, sel-05).

## Tests To Add Or Update

Per-slice above. Cross-slice invariants: `ring_fail_total=0`; count
conservation across dedup/flush (novel + folded = observed, fop-11
differential style); EPL group-by rule; no existing test regressions
(process/file/network suites).

## Migration Or Compatibility Notes

- Additive only: no changes to existing MessageTypes, schemas, or PidHash
  semantics (brief constraint).
- Linux-only feature; Windows builds must compile untouched.
- No Wintappy DBT models, no auditd dependency, no RHEL 8 (non-goals).
- SIDs comparable only within a PolicyEpoch; documented in the event_type
  page at closeout.

## Rollback Plan

`WINTAP_SELINUX_ENABLED=false` disables capture end to end (kill switch,
criterion-independent). Full rollback = deregister the sensor + drop the
EPL/serializer registration; no data migrations, additive schema means
landed parquet stays queryable.

## Done Checklist

- [ ] sel-01 evidence: noaudit rate/cardinality; R1 adopt/reject in
      design.md; blob-offset handshake verified
- [ ] sel-02 tracer + skeleton sensor; decode tests green
      — 2026-09-18: sel-02 implementation and smoke validation
      complete via wrapper fallback (all three streams capturing; 2.9M
      checks folded to 2,748 novel emissions, decode_errors=0 — see
      verification.md). Formal checkbox remains open pending decode unit
      tests recorded green and explicit resolution of the preferred
      avc_has_perm_noaudit attach blocker (EINVAL — see sel-03 gate)
- [ ] sel-03 resolver/dedup/epoch complete; semantics tests green
      — 2026-09-18: IN PROGRESS — core mechanics implemented and
      package-validated (class/permission decoder
      132/2150, R2/R3 resolver hit=2854/miss=1365/learned=27, LRU flush
      rows=1703/zero_delta=770/errors=0, policy-epoch polling live —
      see verification.md). Remaining: EventChannel emission, semantic
      unit tests, and the hook-scope GATE decision above
- [ ] sel-04 ETL landed; EPL/serializer/kill-switch tests green
- [ ] sel-05 acceptance: criteria 1-4 pass in the validation environment; verification.md
      updated; fentry gate decision recorded
- [ ] Closeout: durable facts promoted (event_type/selinux-events,
      component page), index/log updated, follow-ups filed
