---
title: "Linux Capability and Data-Quality Matrix"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
  - ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/task_start_boottime.h
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs
  - ../Lintap/packaging/README.md
  - wiki/work/improve-lintap-data-quality/clone-validation-results.md
  - wiki/work/selinux-monitoring/verification.md
policy: agent-editable
last_validated: 2026-10-26
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/wintap/platform/linux; ../Lintap/packaging
tags: [lintap, linux, ebpf, btf, core, compatibility, telemetry-semantics, data-quality]
---

# Linux Capability and Data-Quality Matrix

**The useful unit of comparison is a capture's actual capabilities, not its distro
name.** Two Ubuntu or RHEL hosts can produce materially different data because
of kernel backports, privileges, installed objects, enabled sensors, attached
hooks, and output mode. A healthy service is not proof of complete coverage.

Scope: live source on the current branches, including the **2026-10-22 clone
follow-up** and the **2026-10-26 CO-RE start-time BTF-name compatibility fix**.
The latter passed native RHEL 8.10 x86_64 compile/package checks but has not
received BPF load/attach or live-capture qualification. Wintap owns
sensors/model/ETL; Lintap owns Linux packaging/dev support; Analytics owns this
matrix; Wintappy owns downstream DBT/DuckDB models. No defaults changed here.

## 1. Vocabulary and selection rules

| Term | Meaning here | What it does **not** guarantee |
|---|---|---|
| eBPF | Kernel programs acquire telemetry and publish ring-buffer records | Permission to load/attach, zero loss, or complete host coverage |
| BTF | Kernel type metadata; native builds generate `vmlinux.h` from it and CO-RE uses target type information | Required hooks/helpers exist or attach succeeds |
| CO-RE | Compile Once–Run Everywhere relocations adapt kernel structure reads | Universal kernel, architecture, tracepoint-layout, or kprobe-signature compatibility |
| Tracepoint fallback | Alternate object avoiding kernel-structure/BTF reads | Same fields/semantics as CO-RE, or support on every old kernel |
| Primary hook | Hook whose successful attach is required by the base sensor | All additional hooks are attached |
| Additional hook | Supplementary syscall/kprobe coverage attached by a sensor | Failure always stops that sensor or triggers object fallback |

**Selection, independently for each enabled sensor:**

```text
environment override → JSON/default enable setting
  disabled → no events from that sensor
  enabled → try preferred object (present → load → primary attach → ring buffer)
    failure → try listed fallback object(s)
      all candidates fail → sensor not registered; other sensors can continue
    primary succeeds → attach additional hooks; poll records
      additional-hook failures can leave partial coverage on the SAME object
```

There is no single global “CO-RE mode.” FileOps can be CO-RE while Clone or Exec
uses a fallback. BTF presence is logged, but runtime selection is driven by
candidate success, not merely that presence flag. Missing optional hooks do not
automatically select the fallback. All these eBPF tiers require ring-buffer
support and the helpers used by their objects; no perf-buffer-only compatibility
tier is implemented here. Do not infer support from an upstream kernel version
alone—enterprise backports matter.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §TryLoadBpfProgram; §LoadBpfProgram; ../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs §IsEnabled; §TryStart -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile §CORE_OBJS; §TRACEPOINT_OBJS -->

## 2. Capability permutations → resulting data

Legend: **Observed** = a named run below; **Source** = current code behavior;
**Risk** = plausible consequence, not a measured universal failure rate.

| Host/build/runtime permutation | Effective capture | Data consequence / interpretation |
|---|---|---|
| BTF available at build and target; matching objects; required hooks load/attach | Preferred CO-RE candidates can run | Richest implemented kernel evidence; still subject to per-sensor limits below. **Source**, not a completeness guarantee |
| Target has BTF, but installed payload contains only fallback objects | Tracepoint candidates | BTF cannot restore absent objects. Reduced identity/path/network fields despite a modern kernel. **Source** |
| No readable build BTF | Makefile builds fallback objects only | No new CO-RE objects generated; SELinux has no tracepoint-only object alternative. Inspect staged payload, not just build success. **Source** |
| Preferred object fails load/primary attach; fallback succeeds | That sensor runs fallback | Stream exists but semantics may degrade; preserve loaded-object logs with the dataset. **Source** |
| All candidates fail, or sensor explicitly disabled | No stream contribution from that sensor | Absence of rows is **absence of observation**, not proof the host performed no activity. Other streams can remain populated. **Source** |
| Primary attaches, some supplementary hooks fail | Partially populated sensor | Missing operation families or classification evidence even though registration succeeded. **Source/Risk** |
| Kernel blocks BPF/tracepoint/kprobe access | Candidate/hook-dependent failures | BTF alone cannot fix permissions/lockdown/security policy. Exact cause must be diagnosed; do not prescribe disabling security controls from this matrix |
| Kernel advertises old version but backports capabilities | Potentially richer support than version suggests | RHEL 4.18-series SELinux evidence below demonstrates why a version-only cutoff is misleading. **Observed** |
| `/proc` inaccessible, process already gone, or callbacks delayed | Kernel records with weaker userspace enrichment | Unknown command/path/parent or approximated identity; more orphan joins possible even when hook capture succeeds. **Source/Risk** |
| Workload includes namespaces/containers | Host task evidence plus collector-visible `/proc` | PID, path and mount views need separate validation; none of these tiers is a demonstrated universal container-normalization contract. **Unknown** |

The subsequent runtime-receipt follow-up standardizes primary/auxiliary
libbpf ERR_PTR checks across Clone/Exec/Network/FileOps/SELinux and persists
outcomes in HOST. Older builds used nonuniform auxiliary checks; historical
registration/“attached N” logs alone are not conclusive evidence. See
[[wiki/schema/runtime-capability-receipt]] for the implemented startup contract.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §OnStarting; ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs §TryAttachProgram; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §OnStarting; ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §OnStarting; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §OnStarting -->

## 3. Process matrix: births, images, identities, exits

| Sensor/path or combination | What the producer observes | Resulting-data caveats |
|---|---|---|
| Clone CO-RE: `clone_core_tracer.bpf.o` | Raw sched-fork child pid/tgid; suppresses non-leader thread births; parent TGID; best-effort start-boottime from `start_boottime` or RHEL 8's `real_start_time` BTF field | Covers fork-only children independently of later exec; `/proc` still supplies much image enrichment and remains an identity fallback. Ubuntu arm64: 80 real births, zero false thread births; RHEL 8 compatibility compile/package passed but was not runtime-qualified |
| Updated Clone fallback: `clone_tracer.bpf.o`, clone + clone3 flags captured | Sched-fork child task ID, parent TGID; userspace filters `CLONE_THREAD` | Same controlled 80-process/60-thread test passes with normal hooks; flags are best-effort rather than authoritative child TGID evidence |
| Clone fallback without usable flag hooks/reads | Sched-fork fires for processes **and threads**; absent flags become zero | Zero flags are treated as non-thread. All 60 workload threads became false process births with hooks deliberately absent; process counts/trees and resolver state can be contaminated |
| Original pre-follow-up Clone fallback | No clone3 flag hook; parent tracepoint task ID | Baseline accepted 40 pthread/clone3 threads as processes and used worker TIDs for 20 fork parents. Do not apply new-fix guarantees to older datasets |
| Clone disabled/failed; Exec working | Exec observations, not every process birth | Fork-only children/ancestors missing; their file/network events may lack a durable lifecycle join. Live `/proc` fallback can help but cannot resurrect a dead unobserved child |
| Clone working; Exec disabled/failed | Births without direct exec observations | Birth image may be inherited, sampled after exec, or unavailable; later image replacements are not reliably observed |
| Exec CO-RE: `execve_tracer.bpf.o` | Exec syscall entry; optional execveat and successful sched-exec; kernel start/parent context | Entry is an **attempt**, not proof of successful image replacement. Parent/start evidence can survive `/proc` disappearance; command line still depends on `/proc` |
| Exec fallback: `execve_tracepoint.bpf.o` | Same hook families when attached; kernel PPID/parent-start/process-start fields set to zero | `/proc` needed for those fields; when process start cannot be read, userspace uses callback time. Same real PID can then acquire mismatched hashes across observations |
| Exec additional sched-exec hook absent | Syscall entries without success confirmation | Cannot distinguish successful exec from failed attempts using that missing source. Fewer rows can mean fewer hooks, not fewer processes |
| Clone + Exec, all tested hooks | Birth + exec-entry + successful-exec observations | Observed **three Start rows per fork+exec child, one PidHash**. Count identities, not Start rows; multiplicity is not fixed across configurations |
| Late Clone after Exec/Refresh/Stop, new resolver guard | Provisional clone metadata marked `PROC_START_SRC=sched_fork` | Existing same-hash resolver row is not overwritten/revived; raw observations remain separate. Guard does not reconcile different hashes or order every other source |
| Exit CO-RE: `exit_tracer.bpf.o` | Leader-task sched-exit; filters non-leader exits; parent TGID and kernel wait status | ExitCode carries kernel wait status, not automatically a decoded shell exit code. Leader exit is not a proven last-thread/group-death signal |
| Exit fallback: `exit_tracepoint.bpf.o` | Every sched-exit task ID; kernel PPID and exit code set to zero | Thread Stop records possible; `ExitCode=0` is a placeholder, **not proof of successful exit**. Resolver/`/proc` may recover parent context but not the lost status |
| Either Exit path, current userspace | Stop enrichment/identity from resolver, then live `/proc`, then fallback | Stop `EventTime` uses `DateTime.UtcNow` at callback, not the supplied kernel timestamp. Lifetime end can be late; unmatched Stop may use an exit-time identity |
| Exit disabled/failed | No Stop observations from Exit | Open lifecycle rows are not proof processes remain alive; reconciliation is a different observation mechanism |
| ProcessRundown enabled | One startup `/proc` inventory, emits Refresh | Helps pre-existing processes; neither continuous birth coverage nor a retroactive birth/exit history. Does not require BTF/eBPF; its `/proc` view/access still matters |

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §HandleEvent; §IsThreadClone; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_core_tracer.bpf.c §trace_process_fork; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c §trace_process_fork; §trace_sys_enter_clone3 -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracepoint.bpf.c §trace_execve_entry; §trace_sched_process_exec -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracer.bpf.c §trace_process_exit; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/exit_tracepoint.bpf.c §trace_process_exit; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §Start -->

Measured counts and limits: [[wiki/work/improve-lintap-data-quality/clone-validation-results]].
Shared model boundary: [[wiki/event_type/process-events]].

## 4. File/network/security matrix

| Domain/path | Kernel evidence retained or lost | Meaning for resulting data |
|---|---|---|
| FileOps CO-RE: `file_ops_tracer.bpf.o` | Device/inode and directory/mount identity where populated; regular-FD filtering for read/write/close/mmap | Stronger path resolution and directory indexing. Identity is supporting evidence, not universal inode availability on every operation |
| FileOps fallback: `file_ops_tracepoint.bpf.o` | File/dir device+inode and mount namespace fields deliberately zero; no kernel regular-FD test | FD cache and live `/proc` have more responsibility; pseudo/non-file activity may be emitted in kernel then filtered/dropped in userspace. No guarantee of path/completeness parity |
| Either FileOps tier | Successful open return; read/write/mmap/unlink/close largely at syscall entry | Read/write bytes are **requested**, not returned; unlink/close record attempts, not guaranteed success. `mmap`→Read is a semantic mapping, not proof actual pages were read |
| FileOps auxiliary hook absent | Missing open-entry/operation records or FD-path teaching | Selective missing operations and dependent path loss; kernel ring-drop zero alone cannot detect a hook never attached |
| Network CO-RE: `network_ops_tracer.bpf.o` | Socket tuple reads, connect/accept/close probes, TCP send/recv, UDP socket/peer hooks | Richer than fallback, but coverage depends on many supplementary probes. Main state tracepoint primarily seeds tuple cache; connect/close evidence relies on kprobes |
| Network CO-RE bytes | TCP send/recv and UDP send use entry/request lengths; several per-socket paths suppress repeats within one second | **Not packet capture or exact byte accounting.** Summing serialized bytes does not establish actual successfully transferred traffic; sampling and entry/return semantics differ by operation |
| Network fallback: `network_tracepoint.bpf.o`, TCP | IPv4 sock state tracepoint; connect/accept/close classification from old/new state; bytes zero; current-context TGID | No TCP send/recv byte records. Zero bytes mean unavailable measurement, not no traffic. State layouts/backports and asynchronous context can weaken classification/owner attribution |
| Network fallback, UDP | IPv4 sendto with explicit destination; recvfrom with source buffer and positive return | Local tuple fields missing (zero); send length requested, receive length returned. Connected sockets without explicit destination and sendmsg/recvmsg-only activity are not equivalent coverage |
| Network IPv6 workload | Fallback explicitly filters AF_INET and emits `is_ipv6=0`; CO-RE has some v6 hooks but substantial tuple handling remains IPv4-oriented | Fallback does **not** provide IPv6 coverage. Presence of v6 hooks/fields in CO-RE is not verified end-to-end IPv6 support; validate separately before using absence as evidence |
| SELinux absent or sensor disabled | No SELinux records | Typical Ubuntu validation had no SELinux filesystem; no records say nothing about generic Linux security decisions or AppArmor |
| SELinux CO-RE primary AVC hook succeeds | Audited AVC events; optional transition and interaction probes | AVC data is audited decisions, not every permission check. Missing transition hook removes that class without necessarily stopping AVC |
| SELinux `avc_has_perm_noaudit` works | Preferred interaction-check coverage | Interaction output is novel-tuple/deduplicated and periodically folded, not one row per permission check |
| SELinux falls back to `avc_has_perm` wrapper | Interaction data can still flow | Inode fast-path coverage may be incomplete; compare interaction rates only with attach mode recorded |
| SELinux primary fails / no CO-RE object | No registered SELinux sensor; no separate BTF-free object fallback | Other process/file/network sensors can continue. Enforcing/permissive mode and policy epoch change interpretation of outcomes/permission masks |

<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c §is_regular_fd_info; §t_read_ent; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c §file_path_event; §trace_openat; §t_read_ent; §t_unlinkat; ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs §HandleEvent -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §trace_inet_sock_set_state; §kprobe__tcp_sendmsg; §kprobe__tcp_recvmsg; §kprobe__udp_sendmsg; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_tracepoint.bpf.c §trace_inet_sock_set_state; §trace_sendto; §trace_recvfrom_exit -->
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/SELinuxSensor.cs §Start; §DecodeAvc; §SafeFlushInteractions -->

## 5. Distro/architecture evidence ledger—not a support certification

| Environment / date | What is actually established | What remains unestablished |
|---|---|---|
| Ubuntu 24.04 arm64, kernel `6.8.0-147-generic`, 2026-10-22 | New Clone CO-RE and updated fallback normal-hook workloads pass; no clone3 skips. CO-RE dual-sensor direct output passes; missing-hook fallback produces 60 false thread births | New-fix package acceptance, long-run load, namespace parity, complete Exit/network fallback parity |
| Ubuntu 24.04 arm64, Debian `0.1.0-102`, data-quality closeout | Controlled packaged file/network + DBT workload passes with Clone explicitly enabled; prior source two-hour file gate passes | That older package does not establish installation of the subsequent clone CO-RE fix; no universal zero-orphan guarantee |
| Fedora 44 UTM VM, 2026-06-09 | Historical process/file/TCP/UDP output; old Clone tracepoint attach fails `-EACCES` while other sensors continue | Exact kernel/architecture not established in the cited memo; cause unresolved; **new raw-tracepoint CO-RE Clone not tested there**. Not evidence all Fedora fails |
| RHEL 8 field host, 2026-08-14 | Historical Clone primary + clone/vfork hooks attach; collector-induced fork storm documented | New clone3/CO-RE classification fixes not tested there; old attach success is not complete-data proof |
| RHEL 8.10, 4.18-series, SELinux permissive, 2026-09-18 | BTF and backported AVC tracepoint present; preferred `avc_has_perm_noaudit` kprobe fails `-22`; wrapper attaches | Not full current-branch/domain acceptance; preferred and wrapper interaction coverage cannot be treated as identical |
| Other Debian, Fedora releases, RHEL kernels, x86_64 clone follow-up | Source/configuration analysis only unless accompanied by another named run | Mark untested rather than infer success from distro family or newer version |

Fedora failure persisted with SELinux permissive, `perf_event_paranoid=1`, and
explicit capabilities; those negative tests do **not** establish a cause/fix.
Sources: `../wintap/fedora-handoff-2026-06.md` (historical);
[[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]] (historical);
[[wiki/work/selinux-monitoring/verification]];
[[wiki/work/improve-lintap-data-quality/verification]];
[[wiki/work/improve-lintap-data-quality/clone-validation-results]].

## 6. Packaging/output permutations that also change interpretation

| Permutation | Resulting-data implication |
|---|---|
| Current application config and Debian/RPM package env have Clone=true; older/local env may retain false | New package default is on; explicit/local opt-out wins. Upgrade does not authorize overwriting administrator settings. JSON alone does not prove fork-only coverage; inspect HOST receipt |
| Native matching-architecture Debian build with BTF | Supplies both tiers; current package validation requires `clone_core_tracer.bpf.o`. Inspect loaded object rather than assuming preferred tier succeeded |
| Debian cross-build | Builder deliberately disables BTF and supplies fallback tier; modern target BTF does not add missing CO-RE objects |
| Current RPM builder | Native x86_64+BTF required by current validation contract; cross-build setup exists but unconditional CO-RE FileOps payload check prevents its fallback-only path passing end to end |
| RPM Uncompressed vs Debian default Snappy | Storage/compression difference, not intended event-semantic difference. RPM setting avoids incompatible native compression library; writer failure would affect delivery rather than sensor coverage |
| Normal ETL/Esper output | File/TCP/UDP rows aggregated (including ten-second EPL groups); file paths lowercased. Raw row counts are not syscall/packet counts; use EventCount carefully |
| Direct parquet / ETL bypass | Different schema and processing stage; process Arguments breadcrumbs retained, unlike standard ProcessSerializer. File sensor may still aggregate before direct output |
| Direct sink with ETL disabled | Data can remain in runtime `esper_staging`, not published `raw_sensor`; an empty published folder is not proof nothing was captured |
| Bypassed registration/resolution (diagnostic switches) | Hook output can be validated without validating normal lifecycle joins; do not promote direct-output passes to resolver/DBT acceptance |
| Historical build before correctness/loss fixes | File counts, hashes, attribution, metadata ordering and delivery can differ independently of distro/BTF. Keep software revision with each capture |

<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §Supported targets; §Build the RHEL 8 RPM; §Install and configure; ../Lintap/packaging/lintap-deb/lintap.env; ../Lintap/packaging/lintap-rpm/lintap.env -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/extract/ProcessSerializer.cs §handleStartEvent; ../wintap/wintap/core/etl/load/DirectParquetSink.cs §AddScalarProperties -->
Aggregation/delivery details: [[wiki/component/fileops-event-pipeline]],
[[wiki/pipeline/nesper-esper-event-stream-processing]],
[[wiki/work/improve-lintap-data-quality/diagram-glossary]].

## 7. Attach a capability receipt to every dataset

**The core startup subset is now implemented in HOST** as
[[wiki/schema/runtime-capability-receipt]]. The fuller receipt below remains a
recommended analyst-facing record; do not assume every listed fact is exported.
Store this beside each capture and update it on restart/kernel/config changes:

| Receipt field | Why it matters |
|---|---|
| Run ID, host/AgentId, capture start/end, restart boundaries | Prevent mixing distinct capture regimes; startup gaps are not steady-state loss |
| Distro release, exact `uname -r`, architecture | Reproduce backport/ABI differences; distro label alone is insufficient |
| App commit/package revision; object names and hashes; libbpf version | Prevent assuming new fixes from an old package or stale tracer |
| Build BTF availability and target BTF availability | Separate what could be built from what could relocate/load |
| Effective enabled sensors and env/config overrides | Separate deliberately unobserved domains from failed ones |
| **Loaded object for each sensor**, registration, successful and failed hooks | Establish mixed-tier/partial-hook coverage rather than merely “BTF=yes” |
| Clone flag-hook status; SELinux interaction attach mode, policy epoch/mode | Explain false-thread risk and security interaction blind spots |
| `/proc`/namespace/access context; privilege/security restrictions | Explain missing enrichment and host/container view mismatches |
| Output mode, schema, aggregation/filter/retry settings | Establish which fields/counters/rows are comparable |
| Ring/sender/serializer/writer loss counters, failed merges, workload QA | Separate unobserved hooks, filtering, aggregation and transport loss |
| Tested operations and explicit skips (clone3, IPv6, etc.) | “Not tested/unsupported” must not silently become “zero events” |

Useful evidence: `/etc/os-release`, `uname -r`, `uname -m`, readable
`/sys/kernel/btf/vmlinux`, installed `tracers/*.bpf.o`, effective service env,
and capture startup logs containing `loaded eBPF object`, `sensor registered`,
`failed to attach`, and `program ... not found`. Record actual links/workload
outcomes when auxiliary logging is insufficient. No security-setting changes
are necessary just to assemble this receipt.

### Analysis guardrails

1. **Missing domain/hook ≠ no activity.** Mark coverage unknown/unobserved.
2. **Zero placeholder ≠ measured zero.** Especially fallback exit codes,
   TCP bytes, inode/mount IDs and UDP local tuples.
3. **More rows ≠ more processes/traffic.** Exec multiplicity, threads,
   rundown, rate limiting and aggregation all change row counts.
4. **Same schema ≠ same evidence.** Fallback fields can be populated from
   `/proc` or left zero while CO-RE supplies kernel evidence.
5. Compare experiments within matched capability receipts, or stratify results
   by loaded tier/hook set/output regime. Preserve unknowns; do not silently
   pool stronger and weaker captures as equivalent ground truth.
<!-- SYNTHESIS: inferred from the per-sensor source and named validation runs above -->
