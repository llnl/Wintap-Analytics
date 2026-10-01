---
title: "Verification: SELinux Monitoring"
type: concept
confidence: medium
grounded_by:
  - wiki/work/selinux-monitoring/implementation_plan.md
policy: agent-editable
last_validated: 2026-09-18
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: wiki/work/selinux-monitoring/verification.md
tags: [feature-work, selinux, ebpf, verification]
---

# Verification: SELinux Monitoring

Evidence transcribed from minimized, sanitized validation summaries per
[[wiki/workflow/lintap-dev-field-workflow]].

## sel-02 — tracer + sensor skeleton (2026-09-18)

### Validation environment (VARIANCE — see note below)

- **RHEL 8.10 with a 4.18-series kernel**, not RHEL 9-class as the brief/
  design assumed. SELinux was present and **permissive**. BTF and the
  required build/audit tooling were present; `bpftrace` was absent.
- Implication: the `avc:selinux_audited` tracepoint (upstream ~5.10) is a
  RHEL backport into 4.18 in this environment; fentry/BTF-trampoline support on
  4.18 is doubtful (bears on design decision 5).

### Code changed (`../wintap`, SELinux exploration branch)

- New: `wintap/platform/linux/sensor/ebpf/tracers/selinux_tracer.bpf.c`
  (CO-RE; tracepoint + bprm-commit kprobe with in-kernel `osid != sid`
  filter + interaction kprobe preferring `avc_has_perm_noaudit` with
  runtime fallback to `avc_has_perm`; ringbuf; stats array; self-PID
  filter; 16,384-entry LRU keyed `(ssid, tsid, tclass, requested)`,
  novel-emit + in-kernel fold).
- New: `wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs` (startup
  census, load/attach with fallback, fixed-layout decode, sample-event
  logging, 10 s initial heartbeat + 60 s counters; no ETL emission — that
  is sel-04; no resolver/dedup flush — that is sel-03).
- Updated: `tracers/Makefile` (builds `selinux_tracer.bpf.o`);
  `platform/linux/infrastructure/LinuxSubscriptionManager.cs` (registers
  SELinuxSensor); `core/shared/ConfigManager.cs` (`SELinux`, `ApiUrls`
  defaults); `wintap/Makefile` (`WINTAP_ENABLE_SELINUX_SENSOR`,
  `WINTAP_API_URLS`); `core/infrastructure/Program.cs` (API listen URL
  configurable via `WINTAP_API_URLS`, default `http://127.0.0.1:8099`);
  `helpers/LibBpf.cs` (`libbpf_get_error` P/Invoke).
- Incidental fix: ProcessRundown override —
  `WINTAP_ENABLE_PROCESS_RUNDOWN_SENSOR=false` now disables it correctly.
- Ringbuf wakeups fixed so userspace receives novel-tuple events; attach
  errors are surfaced through the `libbpf_get_error` P/Invoke.

### Commands and results

- `make build_ebpf` — PASS.
- `make build_dotnet` — PASS (existing warning noise, `0 Error(s)`).
- Manual run using an alternate local test port:

```
sudo make -C <wintap-repo>/wintap run WINTAP_API_URLS=http://127.0.0.1:8199 \
  WINTAP_DISABLE_ETL=true WINTAP_ENABLE_SELINUX_SENSOR=true \
  WINTAP_ENABLE_EXECVE_SENSOR=false WINTAP_ENABLE_CLONE_SENSOR=false \
  WINTAP_ENABLE_EXIT_SENSOR=false WINTAP_ENABLE_NETWORK_SENSOR=false \
  WINTAP_ENABLE_FILEOPS_SENSOR=false WINTAP_ENABLE_PROCESS_RUNDOWN_SENSOR=false
```

### Runtime evidence (implementor log excerpts)

```
SELinux startup census: mode=permissive, btf_present=True, selinux_audited_tracepoint_visible=True
SELinux loaded eBPF object: ./platform/linux/sensor/ebpf/tracers/selinux_tracer.bpf.o
SELinux self-PID filter set
SELinux attached 'k_bprm_commit'
SELinux failed to attach 'k_avc_noaudit' error=-22
SELinux falling back from avc_has_perm_noaudit to avc_has_perm wrapper; inode fast-path coverage may be incomplete
SELinux attached 'k_avc_perm'
SELinux attached 3 programs total
SELinux sensor registered
ProcessRundownSensor disabled by config (ProcessRundown=false)
```

**The one failure — the sel-02 blocker finding:**
`avc_has_perm_noaudit` exists in `/proc/kallsyms`, but perf-event kprobe
creation is rejected: libbpf stderr
`failed to create kprobe 'avc_has_perm_noaudit' perf event: Invalid
argument`, sensor `error=-22` (EINVAL). The designed fallback to the
`avc_has_perm` wrapper engaged and works, with the known coverage caveat
(may miss checks that call the noaudit variant directly, e.g. the inode
fast path).

All three streams produced decoded events (anonymized samples):

```
SELinux sample interaction pid=<pid> comm=<service> ssid=<sid> tsid=<sid> tclass=<class> requested=0x20 count=1 novel=1 first_pid=<pid> first_comm=<service>
SELinux sample interaction pid=<pid> comm=<shell-or-tool> ssid=<sid> tsid=<sid> tclass=<class> requested=0x40 count=1 novel=1 ...
SELinux sample interaction pid=<pid> comm=<remote-login-daemon> ssid=<sid> tsid=<sid> tclass=<class> requested=0x1 count=1 novel=1 ...
```

Counters (60 s lines, then cumulative at stop):

```
interaction_hook=avc_has_perm,links=3 user=[transition:consumed=1,decode_errors=0; interaction:consumed=724,decode_errors=0] kernel=[transition_emitted=1,interaction_novel=724,interaction_folded=75309,interaction_self_drop=86]
interaction_hook=avc_has_perm,links=3 user=[avc:consumed=8,decode_errors=0; transition:consumed=4,decode_errors=0; interaction:consumed=1190,decode_errors=0] kernel=[avc_emitted=8,transition_emitted=5,interaction_novel=1914,interaction_folded=404711,interaction_self_drop=194]
final cumulative: avc_emitted=16 transition_emitted=20 interaction_novel=2748 interaction_folded=2907492 interaction_self_drop=389; decode_errors=0 throughout
```

### Assessment

- **Capture proven end to end in the validation environment for all three streams** (16
  AVC events, 20 transitions, interaction stream live) via
  tracepoint + bprm kprobe + wrapper fallback.
- **In-kernel dedup validated at scale:** 2,907,492 checks folded against
  2,748 novel emissions (~99.9% fold rate); ring traffic stayed at
  novel-only as designed. Map occupancy ≤ 2,748 distinct
  `(ssid,tsid,tclass,requested)` keys — comfortably inside 16,384 and
  consistent with the spike's 421 three-field tuples once the requested
  component and a longer window are added.
- `decode_errors=0` across the run; self-PID drop counter working.
- **Open blocker for acceptance:** preferred `avc_has_perm_noaudit`
  attach fails EINVAL on this kernel — hook-strategy decision required
  before sel-03 finalization (see implementation_plan gate note).
- Not yet verified in sel-02: decode unit tests (not recorded in the
  summary), `ring_fail` behavior under load, longer-run map churn.

### Next technical actions (carried into the plan/handoff)

1. Investigate the EINVAL: try a tracefs `kprobe_events` probe on the
   symbol (distinguishes perf-interface rejection from the symbol being
   unprobeable — likely notrace/ftrace-list exclusion on 4.18), libbpf
   legacy kprobe opts, symbol+offset attach, or fentry/fexit if kfunc
   support exists (doubtful on 4.18).
2. If noaudit stays blocked: explicit scope decision — wrapper-only
   interaction coverage on RHEL 8.10 (documented gap) vs declaring this
   environment tier out of scope per the brief's original non-goal.
3. sel-03 resolver/flush work may proceed in parallel, but final
   acceptance depends on the hook-coverage decision.

## sel-03 — packaged-service validation of core mechanics (2026-09-18)

Evidence transcribed from minimized validation summaries for RHEL 8.10
with a 4.18-series kernel. sel-03 is
**partially implemented**: this run validates the internal mechanics —
class/permission decoder, R2/R3 SID resolver skeleton, interaction LRU
flush with zero-delta skip, policy-epoch polling, and the new counters.
No ETL/WintapMessage emission yet (sel-04); no schema changes.

### Package/deploy context

- RPM package built and installed; packaged services started successfully.
- **Packaged-service mode is now the preferred validation path** (vs the
  sel-02 manual `make run`) — it exercises the actual unit configuration.
- `make build_ebpf` PASS; `make build_dotnet` PASS (existing warning
  noise, `0 Error(s)`).

### Runtime config (SELinux-only focus)

```
WINTAP_DATA_ROOT=/var/log/lintap
WINTAP_DISABLE_MCP=true
WINTAP_DISABLE_DUCKDB_UI=true
WINTAP_DISABLE_ETL=true
WINTAP_DISABLE_SENSORS=false
WINTAP_API_URLS=http://127.0.0.1:8199
WINTAP_ENABLE_SELINUX_SENSOR=true
WINTAP_ENABLE_EXECVE_SENSOR=false
WINTAP_ENABLE_CLONE_SENSOR=false
WINTAP_ENABLE_EXIT_SENSOR=false
WINTAP_ENABLE_NETWORK_SENSOR=false
WINTAP_ENABLE_FILEOPS_SENSOR=false
WINTAP_ENABLE_PROCESS_RUNDOWN_SENSOR=false
```

### Startup evidence

```
SELinux startup census: mode=permissive, btf_present=True, selinux_audited_tracepoint_visible=True
SELinux loaded eBPF object: ./tracers/selinux_tracer.bpf.o
SELinux permission decoder loaded classes=132,permissions=2150,policy_epoch=0
SELinux self-PID filter set
SELinux attached 'k_bprm_commit'
SELinux failed to attach 'k_avc_noaudit' error=-22
SELinux falling back from avc_has_perm_noaudit to avc_has_perm wrapper; inode fast-path coverage may be incomplete
SELinux attached 'k_avc_perm'
SELinux attached 3 programs total
SELinux sensor registered
```

The noaudit EINVAL behaves identically under the packaged service —
wrapper fallback confirmed in both run modes.

### Sample decoded interactions (anonymized)

```
... comm=<remote-login-daemon> tclass=9 class=lnk_file requested=0x1 perms=ioctl scontext_resolved=True tcontext_resolved=False count=1 novel=1 ...
... comm=<remote-login-daemon> tclass=16 class=udp_socket requested=0x2 perms=read scontext_resolved=True tcontext_resolved=False count=1 novel=1 ...
... comm=<desktop-shell> tclass=24 class=unix_dgram_socket requested=0x2 perms=read scontext_resolved=True tcontext_resolved=True count=1 novel=1 ...
```

### Counter evidence (60 s lines)

```
interaction_hook=avc_has_perm,links=3,policy_epoch=0 user=[transition:consumed=1,decode_errors=0; interaction:consumed=895,decode_errors=0] kernel=[transition_emitted=1,interaction_novel=895,interaction_folded=79829,interaction_self_drop=613] flush=[rows=0,events=0,zero_delta=0,iterations=0,errors=0] resolver=[hit=1121,miss=670,learned=20] unknown_perm_masks=183 unknown_perm_top=[class=fd(8),requested=0x10,unknown=0x10:count=92 | class=fd(8),requested=0x40002,unknown=0x40002:count=72 | class=sem(25),requested=0x80000,unknown=0x80000:count=5 | ...] policy_reloads=0

interaction_hook=avc_has_perm,links=3,policy_epoch=0 user=[transition:consumed=1,decode_errors=0; interaction:consumed=406,decode_errors=0] kernel=[transition_emitted=2,interaction_novel=1301,interaction_folded=322851,interaction_self_drop=911] flush=[rows=1703,events=259171,zero_delta=770,iterations=2473,errors=0] resolver=[hit=2854,miss=1365,learned=27] unknown_perm_masks=406 unknown_perm_top=[class=fd(8),requested=0x10,unknown=0x10:count=259 | class=fd(8),requested=0x40002,unknown=0x40002:count=93 | class=sem(25),requested=0x80000,unknown=0x80000:count=14 | ...] policy_reloads=0
```

### Assessment

- **Packaged-service validation PASS** for the sensor skeleton + sel-03
  internal mechanics; `decode_errors=0` and `flush.errors=0` throughout.
- **Decoder:** 132 classes / 2,150 permissions loaded from selinuxfs;
  per-event class + permission-name decode visible in samples.
- **Dedup flush working:** rows=1703, events=259171 folded-count
  deliveries, zero_delta=770 skips, iterations=2473, errors=0.
- **Resolver (R2/R3) working for live source contexts:** hit=2854,
  miss=1365, learned=27 — source contexts resolve via
  `/proc/<pid>/attr/current`; target contexts mostly unresolved unless
  learned from other sources (expected for the composite; numeric SIDs
  preserved regardless).
- **Unknown-permission telemetry working, not a drop path:** 406 masks
  counted, concentrated in `fd` and `sem` classes; numeric masks
  preserved. *Watch item:* the concentration in two low-permission-count
  classes (e.g. `fd` defines few permissions yet shows bits like `0x10`,
  `0x40002`) could be genuinely-undefined policy bits OR a
  class-index/mask mapping subtlety — pin down in sel-04 decode tests
  before schema freeze.
- **Policy-epoch mechanism live** (epoch=0, reloads=0). Delegated-decision
  outcome: implemented as **polling `/sys/fs/selinux/policy`** (the design
  named netlink with polling as fallback; polling is the current primary —
  acceptable, revisit only if poll latency matters for epoch stamping).
- In-kernel dedup at packaged scale: 322,851 folded vs 1,301 novel per
  interval; self-PID filter live (self_drop=911).

### Remaining before sel-03 closes

EventChannel emission, decode/flush/resolver unit tests (also the sel-02
holdover), and the interaction hook-scope decision (sel-03 gate:
noaudit fix vs wrapper-only scope call).
