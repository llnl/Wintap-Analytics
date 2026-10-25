---
title: "Canary quality follow-up: network emission defects and validation blind spots"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_tracepoint.bpf.c
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/devtools/telemetry_smoke_workload.py
  - streamlit/projects/SmokeTests/queries.py
  - streamlit/projects/SmokeTests/analysis.py
  - validation/telemetry-soak/canary-stimulus.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs
  - wiki/work/improve-lintap-data-quality/clone-validation-results.md
  - https://raw.githubusercontent.com/torvalds/linux/v5.15/net/socket.c
  - https://raw.githubusercontent.com/torvalds/linux/v5.14/net/ipv4/udp.c
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/SmokeTests; ../wintap/wintap/platform/linux/sensor/ebpf; ../wintap/devtools
tags: [canary, data-quality, network-events, validation, proposed-fixes]
---

# Findings and proposed fixes — not implementation authorization

**Historical analysis snapshot:** sections below describe Analytics `3f197e4` /
Wintap `d7df7a9` before implementation. Their live-path source citations identify
ownership; use those git revisions to reproduce the old defects, not current code.
The user subsequently authorized recommended-order local VM iteration. Current
implementation and bounded qualification are in
[[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]].
Original live Garage findings are not overwritten by successful VM tests, and field
package provenance/deployment acceptance remain open.

User requested another analysis pass after the all-round workflow improvement.
Analysis revisits the uploaded pilot; **no second collection round was launched**.
Analytics owns validation/wiki; Wintap owns the sensor and shared stimulus writers;
Lintap owns supporting packaging. No source/configuration/service changes are made.

## Evidence boundary

Read-only Garage discovery still supplies one expanded five-family round. Removing
network port restrictions and widening its PID/host window to ±120 seconds does not
recover server TCP Accept or UDP Receive. All 19 recorded Network hooks are attached,
including accept and UDP entry/return hooks; selected tier is `core`/CO-RE. No evidence
or normalization errors. Existing S3 summary remains available; diagnostic rows,
identifiers, credentials and configuration were not saved locally or in Git.

The receipt's selected-object hash **does not match** the local same-name compiled
artifact. This is not proof the installed package is wrong: architecture/build inputs
can differ. Current source defects and compatible live symptoms are distinct from
proof that the deployed object contains this exact source. Verify the trusted package's
object hash/build provenance before attributing a live defect to a particular commit.

Fresh all-family evaluation took **65.78 seconds**, five families, zero analysis errors.
Deeper read-only checks found all five required activities on each of the eight file
paths, no selected lifecycle placeholder hashes or multi-identity Start/Stop PIDs,
but **13 same-identity repeated-Start groups** in the process family (30 Start and
13 Stop rows among 43 selected rows). These are observation counts, not 30 births.
Both endpoint scenarios include an additional zero-peer-port Disconnect; their
Send/Recv observations alone do not certify every selected network row.

## 1. TCP Accept has no CO-RE emission path — high source confidence

`NET_OP_TCP_ACCEPT` exists, but no emission call uses it. `kretprobe__inet_csk_accept`
only updates `sock_pid_map`. `trace_accept` is a no-op, with an obsolete comment saying
the state tracepoint emits Accept. `trace_inet_sock_set_state` now fills `conn_map` and
returns without emitting lifecycle events. The managed callback can map operation 2,
but that mapping cannot create an event absent from the producer.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §kretprobe__inet_csk_accept, trace_accept, trace_inet_sock_set_state; ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §HandleEvent -->

**Proposed Wintap fix:** emit one IPv4 Accept from the successful accept return hook,
using the accepting TGID and returned socket's tuple. Keep cached tuples host-relative,
but emit Accept **remote→local**, because `NetworkActivity` classifies it inbound and
`Transformer` derives Local from Destination. Reject null/error returns. Do not restore
softirq current-PID/state-transition inference or emit from syscall entry.
<!-- SPECULATIVE: proposed change to network_ops_tracer.bpf.c; not implemented -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/Transformer.cs §CreateProcessConn; ../wintap/wintap/core/etl/transform/NetworkActivity.cs §IsInbound -->

Acceptance: accepted connection observed with correct owner/hash, directed addresses
and ports, one Accept per successful socket, no Accept for failed/nonblocking attempts
or listener close, and no duplicate connect/accept inference. Qualify normal ETL plus
source-level emission regressions on an authorized disposable host.

## 2. UDP peer reads mix kernel and user memory — high source confidence, live linkage provisional

The UDP entry probe prefers `BPF_CORE_READ(msg, msg_name)` and stores that pointer.
The return probe reads it using `bpf_probe_read_user`, ignores the helper's result,
and drops non-AF_INET data. Linux `__sys_recvfrom` supplies a **kernel stack sockaddr**
as `msg_name`; `udp_recvmsg` fills it, then the socket layer copies it to the user
buffer **after** the UDP function returns. Thus the selected kernel buffer is read
with the wrong helper. Falling back to the syscall's user buffer at UDP-function
return would also be too early for the current receive.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §kprobe__udp_recvmsg, kretprobe__udp_recvmsg -->
<!-- GROUND_TRUTH: https://raw.githubusercontent.com/torvalds/linux/v5.15/net/socket.c §__sys_recvfrom; https://raw.githubusercontent.com/torvalds/linux/v5.14/net/ipv4/udp.c §udp_recvmsg -->

**Proposed Wintap fix:** retain explicit pointer provenance; read kernel `msg_name`
with the kernel helper at function return, or defer user-buffer reading until syscall
exit while retaining the local socket tuple. Check helper outcomes, address family
and available length; clean every map on every exit. Keep exactly one owner/emission
path, rather than adding overlapping probes that double-count receives.
<!-- SPECULATIVE: proposed UDP return/context correction; not implemented -->

Acceptance must separate unconnected `recvfrom`, connected `recv`, `recvmsg` and
supported batch calls. Include nonblocking failure/timeout, truncation, zero-length
valid datagrams, IPv4 endpoint orientation and map cleanup. Kernel versions differ;
upstream references establish the memory-domain issue, not target-kernel acceptance.

## 3. Partial UDP tuples and sampling are additional quality limitations

Live widened queries find both client UDP Send rows and both server UDP Send rows
with at least one zero endpoint port; client Receive has a complete port pair. Server
TCP also has a Disconnect row with a zero peer port, compatible with listener close.
Do not certify complete socket endpoints from activity presence alone, or count a
listener close as proof the accepted connection disconnected.

Source `trace_sendto` emits before the syscall returns with unknown local tuple;
`kprobe__udp_sendmsg` uses socket peer fields that are empty on an unconnected socket.
TCP/UDP entry probes may represent requested operations, not successful transferred
bytes, and rate-limit some events at one second per socket. Connected UDP entry
Receive emits zero bytes without a successful return check; UDP return drops `ret==0`
even though zero-length datagrams are legitimate. These are distinct contracts, not
loss counters or exact packet counts.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/network_ops_tracer.bpf.c §trace_sendto, kprobe__udp_sendmsg, kprobe__tcp_sendmsg, kprobe__tcp_recvmsg, kprobe__udp_recvmsg, kretprobe__udp_recvmsg -->

**Proposed direction:** preserve incomplete observations explicitly, add per-operation
tuple/success/sampling capability facts, and prefer success-aware UDP send return
handling with kernel destination context/local tuple captured after autobind. Do not
silently discard raw rows, infer missing ports, disable sampling globally or assert
syscall/EventCount/packet equivalence. Decide requested-operation versus successful-
transfer semantics before changing byte/count meaning.
<!-- SPECULATIVE: producer correction and additive quality provenance need separate design approval -->

## 4. Five synthetic counterexamples expose validator blind spots

In-memory DuckDB 1.5.6 checks against the current evaluator, with entirely synthetic
data, all return **zero missing checks and zero violations**:

| Deliberately defective fixture | Why it currently escapes | Proposed assertion |
|---|---|---|
| Eight files, only one activity each, distributed across all five activity names | Activity presence and distinct-path count are independent | Required activity matrix for each explicitly expected path |
| Process Start/Stop both have empty identity | Process checks count distinct non-null identities but do not require a valid one | Valid canonical identity on each attributable lifecycle row |
| Repeated Start rows share the same identity | Only multiple **distinct** Start identities are flagged | Source-aware lifecycle observation accounting, separately from storage-copy dedup |
| Stop identity differs from Start identity for the same PID | Stop is satisfied by PID alone | Birth-scoped Start/Stop identity consistency, respecting PID reuse |
| Valid endpoint rows plus an attributable wrong directed-tuple row | Endpoint checks inspect only rows already matching expected Source/Destination ports | Validate every attributed candidate; separate missing from unexpected/invalid |

<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §selector_query, evaluate_case; validation/telemetry-soak/canary-stimulus.py §stimulus -->

These expose **case observation** overstatement, not a green release certificate:
the canary run already remains yellow because it is stimulus-only. Nevertheless,
"observed / no violations" is weaker than identity/endpoint correctness. Do not
downgrade existing red findings or weaken original strict dev-time gates.

**Repeated Start is not automatically a producer violation.** Clone and Execve
both publish `Start` for one birth, and Execve source breadcrumbs distinguish
syscall entry from successful sched exec. Prior clone qualification explicitly
preserves these raw observations. Classify source/image observations, verify one
canonical birth identity and Stop linkage, and report repeats separately. Flag
unexplained/contract-invalid duplication only after provenance is sufficient; never
delete observations or enforce one raw Start per birth without a semantic decision.
The live 13 repeated-Start groups have not been source-classified in this pass.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs §HandleEvent; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs §HandleEvent; wiki/work/improve-lintap-data-quality/clone-validation-results.md §Evidence, Resolver behavior -->

`expectedProtocols` is also used as a scan filter, so wrong-protocol candidates can
be invisible when correct rows coexist. Use attribution predicates to collect bounded
candidates, then apply expectations as checks rather than acceptance filters. Red
requires sufficient attribution to the canary; unrelated shared-PID traffic remains
ambiguous, not automatically a sensor defect.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/queries.py §selector_query, evaluate_case -->

## 5. Runtime context and stimulus need finer contracts

- One UDP client case combines unconnected and connected phases: one connected
  Receive can satisfy the combined expectation while unconnected Receive is absent.
  Split mode/time/endpoint expectations, with stimulus-ground-truth timestamps and
  success evidence. Keep all expanded families represented, including explicit skips.
  <!-- GROUND_TRUTH: ../wintap/devtools/telemetry_smoke_workload.py §network, selector construction -->
- `Network=running` and attached hooks do not prove event emission, endpoint completeness
  or success semantics. The optional PID filter and network sampling intervals are
  not recorded by current Network startup code. Expose effective operation-level
  support/filter/sampling facts without dumping configuration or changing defaults.
  <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs §Start; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs §StartupWorkerAsync -->
- Short/FQDN aliases are inferred; boot ID in manifests is not applied to event
  selection, and event rows lack capture-run UUID. Prefer explicit canonical sensor
  hostname/receipt binding for new manifests, retaining OS hostname separately.
  Exact capture ownership needs an additive event/receipt contract, not suffix
  stripping or a hostname-only join. S3 object identity is not executable provenance.
  <!-- GROUND_TRUTH: ../wintap/devtools/smoke_manifest.py §smoke_run; streamlit/projects/SmokeTests/analysis.py §hostname_aliases, runtime_context; streamlit/projects/SmokeTests/queries.py §selector_query -->
- Native Clone is skipped because no helper was supplied, not because Clone failed.
  A prebuilt reviewed helper can enable coverage on a later operator-run pilot; no
  unattended compiler/tracer attachment or collector restart is required.
  <!-- GROUND_TRUTH: validation/telemetry-soak/canary-stimulus.py §stimulus -->

## Recommended sequence and ownership

1. **Analytics first:** turn the five synthetic counterexamples into regressions;
   strengthen per-path, lifecycle identity/duplicate and all-candidate endpoint checks.
   Keep attribution uncertainty, pending data, limits and red-preservation rules.
2. **Wintap, separately authorized:** repair Accept emission and UDP memory-domain/
   return handling, plus contract tests and operation-level capability facts. Build
   a trusted managed/tracer pair; do not deploy from this investigation.
3. **Stimulus/Analytics:** split UDP modes, use explicit socket/lifecycle expectations,
   bind canonical host/provenance and enable an approved prebuilt native helper.
4. **Operator pilot:** after package review/installation authorization, run one
   non-interfering round against the already-running sensor; compare exact endpoint,
   identity and per-path expectations. Capture/upload/harness success remain separate.
5. Only then resume open-ended multi-host observations; historical loss, saturation,
   Windows live acceptance and resource/deadline equivalence remain unclosed.

Preserve SDK 10.0.402, DuckDB engine 1.5.6/.NET wrapper 1.5.6.1, retry capacity 1024,
strict identity/count gates, security controls and default-off Linux experiments.
No schema/source/package/service/security changes are authorized by this page.

## Verification performed in this pass

- Private read-only discovery/HOST inspection and full `analyze_round` evaluation;
  widened network selectors and per-path/lifecycle/tuple aggregate checks. Only
  sanitized counts/findings are retained here; no private reproduction payloads.
- Five synthetic in-memory `evaluate_case` counterexamples on DuckDB 1.5.6 all
  reproduce zero missing checks/violations. These were diagnostic executions,
  **not committed regression tests**; existing 75-test suite was not rerun because
  source behavior is unchanged.
- `git diff --check`: passed. Modified content pages' required frontmatter fields
  and wikilinks, and the new page's local grounding paths: passed via read-only
  Python assertions. Existing index/log format is retained.

Related: [[wiki/work/smoke-test-dashboard/verification]],
[[wiki/schema/runtime-capability-receipt]],
[[wiki/work/improve-lintap-data-quality/clone-validation-results]],
[[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]],
[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]].
