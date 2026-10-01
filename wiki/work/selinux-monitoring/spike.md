---
title: "Feature Spike: SELinux Monitoring — attach-point probe"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-09-18
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: reviewed
source_paths: wiki/work/selinux-monitoring/spike.md
tags: [feature-work, selinux, ebpf, spike]
---

# Feature Spike: SELinux Monitoring — attach-point probe

## Question

In an RHEL 9-class validation environment, which eBPF attach points can deliver
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

Also to resolve during validation: SID→context-string resolution strategy; enforcing
vs permissive mode; baseline permission-check rates (sizes the dedup map).

## Hypothesis

A hybrid is likely: the audited tracepoint (or an LSM/kprobe equivalent) for
denials/audited grants, plus a low-cost hook for transitions, plus a
dedup-behind-the-hook capture for the allow-side interaction map. Context
strings will need resolution at or near capture time since SIDs are not
stable across boots.

## Experiment

Run 2026-09-17 on **localhost (`lintap-dev`)**, separate from the RHEL
validation environment. Environment: Ubuntu 24.04.4, kernel 6.8,
aarch64, Multipass VM.

**Platform caveat (bounds everything below):** SELinux in this environment is
compiled in (`CONFIG_SECURITY_SELINUX=y`) but **not active**
(`CONFIG_LSM="landlock,lockdown,yama,integrity,apparmor"`; active list
`lockdown,capability,landlock,yama,apparmor`; `getenforce` → Disabled; no
selinuxfs mount; AppArmor is the active MAC). Therefore: attach mechanics,
tracepoint/BTF field formats, and symbol availability were fully testable;
**provoking a real denial or transition, and measuring true AVC-check
rates, were not possible here** and remain open for a real SELinux host.
`ausearch`/auditd is also absent, so the denial ground-truth procedure was
untestable. Kernel-version caveat: these results are from a 6.8 kernel;
RHEL 9 runs a 5.14-based kernel with backports, so every format/symbol
result must be re-confirmed in the validation environment.

1. Capability census: config, active LSMs, tracepoint format, kallsyms,
   BTF, tooling (bpftrace v0.20.2, bpftool, clang 18, libbpf-dev present;
   passwordless sudo).
2. Throwaway probes from `/tmp/selinux-spike/` (bpftrace one-liners plus a
   minimal clang/libbpf LSM load+attach+fire harness).
3. Allow-side rate measurement via the generic LSM entry points
   (`security_inode_permission` etc.) as a proxy, since `avc_has_perm`
   never runs with SELinux inactive.

## Results

### Tier 1 — `avc:selinux_audited` tracepoint: PRESENT, best-in-class fields

- Exists at `/sys/kernel/tracing/events/avc/selinux_audited` even with
  SELinux inactive (compiled-in trace event).
- Format (6.8): `u32 requested; u32 denied; u32 audited; int result;
  __data_loc char[] scontext; __data_loc char[] tcontext;
  __data_loc char[] tclass` — **full context strings and the class are
  delivered as strings at capture time**; no SID resolution needed on this
  path. Permission masks are bitmasks (need userspace decode against the
  class's permission table).
- No pid field beyond the common header, but the probe runs in the checking
  task's context, so `bpf_get_current_pid_tgid()`/comm capture works —
  event-time process identity (the anti-ASOF-join lesson) is achievable.
- bpftrace attach verified clean. Fires only for *audited* decisions
  (denials + auditallow) by construction — confirmed expectation; it cannot
  feed the allow-side interaction map.

### Tier 2 — BPF LSM: silently inert without `bpf` in the boot LSM list

- `CONFIG_BPF_LSM=y` here, but `bpf` absent from `CONFIG_LSM` and the
  active list. A minimal `lsm/file_open` program **compiled, loaded, AND
  attached without any error — and then never fired** (0 hits across 50
  provoked opens; fentry-style attach to the never-invoked
  `bpf_lsm_file_open` stub).
- This is the operationally dangerous finding: absence of `bpf` in `lsm=`
  is a **silent no-op, not an attach failure**. Any BPF-LSM-based tier must
  verify `bpf` ∈ `/sys/kernel/security/lsm` at sensor startup and refuse
  to claim coverage otherwise. Whether RHEL 9 ships `bpf` in its default
  list must be checked in each validation environment.

### Tier 3 — kprobes/fentry on avc/security functions: all attachable, SIDs not strings

- kallsyms (6.8, arm64): `avc_has_perm` (T), `avc_has_perm_noaudit` (T),
  `slow_avc_audit` (T), `avc_denied` (t), `security_transition_sid` (T),
  `security_bounded_transition` (T), `selinux_bprm_committed_creds` (t),
  `selinux_inode_permission` (t), `selinux_file_permission` (t).
  **`avc_audit` is NOT in kallsyms** — it is a static inline wrapper; the
  hookable audit-path symbol is `slow_avc_audit`.
- BTF signatures (fentry gets named args):
  - `avc_has_perm(u32 ssid, u32 tsid, u16 tclass, u32 requested,
    struct common_audit_data *auditdata)` — exactly the interaction-map
    tuple, one hook, **but as numeric SIDs**.
  - `slow_avc_audit(u32 ssid, u32 tsid, u16 tclass, u32 requested,
    u32 audited, u32 denied, int result, struct common_audit_data *a)` —
    kprobe-equivalent of the tracepoint (plus object info via
    `common_audit_data`), SIDs instead of strings.
  - `security_transition_sid(u32 ssid, u32 tsid, u16 tclass,
    const struct qstr *qstr, u32 *out_sid)` — transition *computation*
    point (fires per exec/inode-create whether or not a transition
    results); `selinux_bprm_committed_creds` kprobe attach verified as the
    committed-transition alternative.
- kprobe and fentry attach verified clean on `avc_has_perm` and
  `slow_avc_audit` (kfunc args readable by name). Zero fires, as expected
  with SELinux inactive.
- CO-RE readability of `cred->security`: `struct task_security_struct
  {u32 osid; u32 sid; u32 exec_sid; ...}` **is present in vmlinux BTF**.
  bpftrace 0.20.2 crashes on the traversal (bpftrace type-handling bug —
  dumped core; use libbpf for this), and note `cred->security` is an LSM
  *blob* pointer: the SELinux struct sits at a boot-computed blob offset,
  which CO-RE alone does not provide — a design-stage detail (offset is 0
  when SELinux is the sole blob user; must not be assumed).

### Allow-side rate proxy (sizes the dedup, confirms per-event emission is impossible)

`avc_has_perm` never runs here, so generic LSM entry points that drive AVC
checks on a SELinux host were measured instead (10 s windows, kprobe
counts):

| hook | idle | fs-heavy load |
|---|---|---|
| `security_inode_permission` | ~2,500/s | **~118,000/s** |
| `security_file_permission` | ~390/s | ~9,200/s |
| `security_bprm_creds_for_exec` | ~11/s | ~580/s |
| `security_socket_sendmsg` | ~33/s | ~32/s |

On a SELinux host each of these translates to ≥1 AVC lookup, so raw
allow-side volume is O(10⁵)/s under load — re-confirming the fop lesson:
**dedup must live behind the hook (in-kernel map), never per-event
emission**. Map sizing should key on distinct-tuple cardinality
(policy-bounded; expected orders of magnitude below event rate), not rate;
SELinux-enabled cardinality measurement remains open.

### RHEL validation run (2026-09-17, second run)

Collector v1 ran in an x86_64 RHEL SELinux validation environment.
**bpftrace was absent**, so the tracefs fallback was used. A minimized,
sanitized digest was retained as the evidence base.

- **SELinux enabled, Permissive** — answers the brief's open question:
  denials log (and reach the tracepoint) but do not block.
- **`CONFIG_LSM="yama,integrity,selinux,bpf"`** — `bpf` IS in the RHEL 9
  boot LSM config (unlike lintap-dev), so BPF LSM is viable there in
  principle. Runtime `/sys/kernel/security/lsm` line not in the v1 digest
  (grep gap, fixed in v2) — confirm before relying on it.
- **Tracepoint present, field set identical to 6.8** (scontext/tcontext/
  tclass as `__data_loc` strings; only the cosmetic `signed` flag differs).
- **Tier 1 proven end to end in validation:** the runcon provocations produced
  2 captured `selinux_audited` events with full context strings
  (`requested=denied=audited=0x200000`, `tclass=file`, `result=0` —
  permissive passthrough). The `ausearch` ground-truth comparison failed
  on a collector bug (v1 passed `-ts` a single quoted datetime; v2 uses
  `-ts recent`) — the criterion-1 field-match dry-run remains open.
- **kallsyms identical to 6.8** for all candidates (`avc_has_perm`,
  `avc_has_perm_noaudit`, `slow_avc_audit` exported; `avc_denied`,
  `selinux_bprm_committed_creds` static; `security_transition_sid`,
  `security_bounded_transition` exported).
- **kprobe tier verified FIRING at real rates** (kprobe_profile deltas,
  15 s windows, zero misses): `avc_has_perm` ≈ **4,560/s idle** and
  ≈ **13,150/s** under the read-only fs walk; `security_transition_sid`
  ≈ 42/s idle / 34/s load; `slow_avc_audit` **0 in both windows** —
  audited decisions are rare outside provocation, so the denial/audited
  stream is naturally low-volume while allow-side dedup stays mandatory.

### RHEL validation run 2 (2026-09-17, collector v2)

- **Active LSM list confirmed: `capability,yama,selinux,bpf`** — `bpf` is
  active at runtime, not just in CONFIG_LSM. BPF LSM is fully available on
  the validation environment (the recommendation still keeps it off the critical path).
- **ausearch ground truth recovered** (v2 `-ts recent` fix): 19 AVC
  records in the window. Record shape matches the tracepoint semantically:
  same scontext/tcontext/tclass identity, with ausearch decoding
  permissions to names (`{ open }`, `{ read }`, `{ lock }`,
  `{ name_connect }`, `{ unlink }`, `{ remove_name }`, `{ rmdir }`) where
  the tracepoint delivers bitmasks — mask→name decode per class is a
  sensor-side job (selinuxfs `class/*/perms/` exposes the bit mapping).
- **Use-case validation:** background AVC denials were observed during the
  validation window (file open/read/lock, tcp_socket name_connect, file
  unlink + dir remove_name, and dir rmdir, all `permissive=1`). This is
  the class of policy-debugging signal the real-time stream is intended to
  surface.
- **Rates (kprobe_profile deltas, 15 s windows, zero misses):**
  `avc_has_perm` ≈ 2,372/s idle, ≈ 11,774/s under the fs walk (order
  matches run 1); `security_transition_sid` 22-28/s;
  `selinux_bprm_committed_creds` ≈ 2/s; `slow_avc_audit` 0 again.
- **THE sizing number — distinct-tuple cardinality (hist trigger,
  kernel-side dedup): 421 distinct `(ssid, tsid, tclass)` tuples** over
  ~30 s idle+load, 212,960 hits, `Dropped: 0` (exact). Extreme skew: the
  top tuple is ~43% of all hits, the top 10 ≈ 89%. A 16k-entry in-kernel
  LRU dedup map gives ~40× headroom over the observed set even before the
  requested-mask key component (small multiplier); post-dedup emission is
  hundreds of novel tuples per boot/policy epoch, not thousands per
  second.
- **Transition tuples: 15 distinct** `(ssid, tsid, tclass)` in the
  workload window (161 hits) — transition volume is low enough for plain
  discrete events, no dedup tier required.

### Validation environment correction (2026-09-18, from sel-02)

The "RHEL 9-class" labels on the two runs above were an assumption carried
from the brief; sel-02 identified the validation environment as
**RHEL 8.10 with a 4.18-series kernel**. All measured data above stands; it
describes a 4.18-backport kernel, not RHEL 9:
the `selinux_audited` tracepoint is a RHEL backport into 4.18 (reinforcing
that its presence is a census check, never a version inference), the
wrapper kprobe results are as recorded, and fentry (never verified) is
now doubtful on this tier. New trap found by sel-02 on this kernel:
`avc_has_perm_noaudit` is in kallsyms but perf-event kprobe attach returns
EINVAL — the recommendation's preferred interaction hook is blocked on
this environment and the sensor runs its wrapper fallback (see verification.md
and the implementation plan's sel-03 gate). Genuine RHEL 9 numbers remain
unmeasured.

### Remaining open items (design/verification-time; none block design.md)

- fentry/BTF verification in the validation environment (kprobe tier verified firing and is
  the design baseline; fentry is an optimization — needs bpftrace or a
  libbpf probe).
- Same-event field-level match of one provoked denial across tracepoint
  and ausearch (shape-level match confirmed; exact-event comparison
  belongs to the acceptance test once the real sensor exists).
- Enforcing-mode behavior — validation used Permissive mode; if deployments
  enforce, re-verify the provoked-denial procedure there.
- Per-check probe overhead with hooks firing (measure with the real
  tracer during implementation).

## Prototype Location

The 2026-09-17 localhost probes were throwaway (`/tmp/selinux-spike/` on
lintap-dev, since deleted; bpftrace one-liners transcribed above;
`lsm_test.bpf.c` / `lsm_fire.bpf.c` + libbpf loaders for the BPF LSM
load/attach/fire experiment). Nothing landed in `../wintap`.

A temporary self-contained collector was used to rerun the census and open
probes: tracepoint capture versus ausearch ground truth, provoked denials,
transition workload, attach-mode tests, and rate/cardinality windows. It
was smoke-tested end to end on lintap-dev in degraded SELinux-inactive mode
on 2026-09-17.

## Recommendation

Hypothesis confirmed with sharper edges — plan the design around a
**three-hook hybrid, none of which is BPF LSM**:

1. **Denials + audited grants: `avc:selinux_audited` tracepoint.** Context
   strings, class string, requested/denied/audited masks and result arrive
   free at capture time; stamp pid/comm from probe context. This is the
   debugging-policy stream. (Fallback if the RHEL 9 kernel lacks the
   tracepoint: kprobe `slow_avc_audit` — same coverage, SIDs instead of
   strings.)
2. **Allow-side interaction map: kprobe, preferred production hook
   `avc_has_perm_noaudit` where attachable** (it covers the inode fast
   path that bypasses the wrapper). In the RHEL 8.10 validation environment,
   `avc_has_perm_noaudit` is visible in kallsyms but rejects perf-event
   kprobe attach with EINVAL, so sel-02 uses **`avc_has_perm` as a
   validated fallback with an explicit coverage caveat** (rates measured
   on the wrapper: ~2.4-4.6k/s idle, ~12-13k/s load across two runs).
   In-kernel dedup map keyed on `(ssid, tsid, tclass, requested)`; novel
   tuples emit, counts flush periodically (fop-11 emit-first pattern).
   Measured cardinality (421 distinct tuples, ~89% of volume in the top
   10) makes a 16k-entry LRU map comfortable; measured rates make
   per-event emission a non-starter.
3. **Transitions: kprobe `selinux_bprm_committed_creds`** (commit point;
   old/new SID via cred blob) or fentry `security_transition_sid`
   (computation point; simpler args, fires per exec/create) — choose in
   design after validation-environment verification.
4. **Keep BPF LSM out of the critical path.** `bpf` is confirmed in the
   validation environment's active LSM list
   (`capability,yama,selinux,bpf`), so the tier
   is genuinely available there — but a missing `bpf` in `lsm=` on any
   other host silently produces zero events after a successful attach.
   Any use must gate on `bpf ∈ /sys/kernel/security/lsm` at startup, and
   the avc-layer hooks already deliver the needed tuples without that
   fragility.

**The open design problem is SID→context resolution for streams 2 and 3.**
SIDs are kernel-internal, boot-local, and remappable on policy reload;
userspace cannot resolve an arbitrary SID directly. Candidate strategies
for design.md: learn SID→string pairs opportunistically (tracepoint events
carry both sides' strings; `/proc/<pid>/attr/current` for live tasks;
`getxattr security.selinux` for files), emit context strings only for
novel tuples via a slower kernel path, or a bounded auditallow learning
window. Whatever is chosen: flush the dedup map on policy reload and never
persist SIDs across boots.

**Spike status: ANSWERED (2026-09-17, after the v2 validation run).** The
attach-point question is resolved in the validation environment: tracepoint end-to-end
with context strings, kprobe tier firing at measured rates, dedup sizing
grounded in exact cardinality (421 tuples, Dropped 0), ausearch ground
truth recovered, `bpf` active. Remaining items are design/verification-
time details, not spike questions. design.md proceeds on this basis.

## Follow-Ups

- v2 validation run completed 2026-09-17; spike questions answered. Feeds
  [[wiki/work/selinux-monitoring/design]] (attach tiers, schema,
  SID→context resolution, dedup residency).
- Carried to design/verification: fentry check, same-event
  tracepoint-vs-ausearch field match, enforcing-mode re-verification,
  per-check overhead measurement.
- The background AVC denials observed during validation are worth
  revisiting once the stream lands as an initial dataset candidate.
- Implementation validation follow-up (sel-02/03, 2026-09-18): the real
  sensor's packaged-service counters confirmed the spike's volume and
  dedup predictions at scale — e.g. 322,851 checks folded to 1,301 novel
  tuples per interval on the wrapper hook, map occupancy well inside 16k
  (see verification.md).
- design.md: attach-point tiers per above, SID→context resolution
  strategy, dedup residency (in-kernel LRU vs userspace), policy-reload
  flush, blob-offset handling for cred→security reads.
