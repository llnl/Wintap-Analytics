---
title: "Telemetry identity: agent_id, pid_hash, conn_id, and endpoint orientation"
type: concept
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/StateManager.cs
  - ../wintap/wintap/core/shared/ProcessHash.cs
  - ../wintap/wintap/core/shared/ProcessIdentity.cs
  - ../wintap/wintap/core/shared/AgentIdentity.cs
  - ../wintap/platform/windows/WintapCoreSvcMgr/ProcessHash.cs
  - ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs
  - ../wintap/wintap/core/etl/transform/IdGenerator.cs
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/wintap/core/etl/model/ProcessConnIncrData.cs
policy: human-review-required
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/wintap/core/shared; ../wintap/wintap/core/etl/transform; ../wintap/wintap/core/etl/model
tags: [identity, agentid, pid-hash, conn-id, five-tuple, telemetry-semantics]
---

# Identity is not direction

**`agent_id` identifies the collecting agent; `pid_hash` identifies a process
instance; `conn_id` identifies a canonical network tuple. None of these tells
you which endpoint is local for a particular event.**

## Three identities, three scopes

**Contract clarification (2026-10-23):** process identity is
`(hostname, PID, canonical process-start time)`; **agent UUID is not an input**.
Its formula must have one production definition across the entire codebase.
[[wiki/decision/process-hash-inputs-and-single-definition]] records the explicit
human decision. The `pid-v2` source patch now implements this contract; installed
old packages and historical recordings have not been migrated.

| Field | Meaning | Important boundary |
|---|---|---|
| `agent_id` / `AgentId` | Persisted collector UUID, host-bound and stable across ordinary restarts. | `pid-v2` checks hostname/machine binding and replaces unbound legacy or differently bound copied state. Fully cloned hostname and machine ID cannot be distinguished locally. It is not a cryptographic host identity. |
| `pid_hash` / `PidHash` | Process-instance key: normalized hostname, OS PID and canonical process-start UTC FILETIME; independent of agent UUID. | PID alone is reusable. `pid-v2` changes historical hashes; legacy stores/recordings are preserved, not silently rekeyed. |
| `conn_id` / `ConnId` | Direction-independent key derived from the full five-tuple: two IP/port endpoints and transport protocol, with context/private-gateway disambiguation. | Does not include PID, agent UUID or connection-start time. It identifies tuple equivalence, not a unique socket lifetime or process owner. |

<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/AgentIdentity.cs §LoadOrCreate; ../wintap/wintap/core/shared/ProcessIdentity.cs §Compute; ../wintap/wintap/core/etl/transform/IdGenerator.cs §GenAttrKeyForFive_Tuple_Key; §GenKeyForFive_Tuple_Conn -->

State now lives in `<runtime-root>/wintapstate.json`, not the installation/build
working directory. Binding uses normalized hostname plus available Linux machine-id
or Windows MachineGuid; hostname/machine changes reissue the collector UUID.
Hostname-only fallback cannot detect same-name clones. Legacy recordings can also
show legitimate renames, so dataset collision diagnostics need temporal context.
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/AgentIdentity.cs §ReadMachineId; §CreateHostBinding; §LoadOrCreate; ../wintap/wintap/core/shared/StateManager.cs §StateManager -->

`wintap/core/shared/ProcessIdentity.cs` is the single formula definition. Sensor
and Windows helper `ProcessHash` wrappers delegate to it; the helper project links
the same source rather than copying it. Hostname is trimmed/uppercase invariant,
numeric serialization uses invariant culture, fixed namespace/type markers and
existing double-MD5/uppercase-hex encoding are retained. Unresolved attribution
uses the explicit unknown sentinel instead of hashing event/Stop time as start time.
<!-- CONTRADICTION[hard]: This unqualified implementation claim conflicts with the still-present Linux ExitSensor missing-start exitUtc hash fallback (ExitSensor.cs:120–121), documented in wiki/diagnostic/sample-db-runtime-attribution-audit.md — REVIEW NEEDED. Core/Windows fixes are verified; all-producer compliance is not. -->

Experiment status: candidate Linux Exit removes its exit-time substitute and recovers
kernel start evidence, but Execve/Rundown missing-start fallbacks and unresolved
lifecycle representation still need acceptance. Preserve the review record above;
this is not an all-producer or deployed-package compliance claim.
See [[wiki/work/host-process-identity-patch/experiment_results]].
<!-- REVIEW NEEDED: remaining producer-input and unresolved lifecycle gates, not the already-tested shared hash formula. -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ProcessIdentity.cs §Compute; ../wintap/platform/windows/WintapCoreSvcMgr/WintapCoreSvcMgr.csproj; ../wintap/wintap/core/infrastructure/EventChannel.cs §Send; ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §EmitStopCore -->

The new process store is `main.pid-v2.duckdb` (helper recovery:
`recovery.pid-v2.duckdb`), preserving old stores without admitting old-formula
cached identities. Deployment/historical acceptance remains separate:
[[wiki/work/host-process-identity-patch/verification]].

## Canonical tuple versus directed tuple versus socket perspective

1. **Canonical Lo/Hi tuple:** endpoints sort by IP, then by port when IPs tie.
   Reversing source/destination preserves `conn_id` for the same gateway context.
2. **Directed Source/Destination tuple:** follows the normalized producer's
   traffic direction. The recorded increment preserves source/destination IPs and
   now `SourcePort`/`DestinationPort`.
3. **Host-relative Local/Remote tuple:** identifies the socket from the attributed
   process's perspective. Receive uses destination as local; send uses source.
   A valid `conn_id` does **not** prove these assignments are correct.

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs §compareAndAssign; ../wintap/wintap/core/etl/transform/Transformer.cs §CreateProcessConn; ../wintap/wintap/core/etl/model/ProcessConnIncrData.cs §SourcePort; §DestinationPort -->

For same-host traffic over one non-loopback IP, with server port 41000 and client
port 51000:

| Observation | Source → Destination ports | Local / Remote ports |
|---|---|---|
| Client Send | 51000 → 41000 | 51000 / 41000 |
| Server Recv | 51000 → 41000 | 41000 / 51000 |
| Server Send | 41000 → 51000 | 41000 / 51000 |
| Client Recv | 41000 → 51000 | 51000 / 41000 |

All four observations share the canonical `conn_id`. Separate client/server
processes have different `pid_hash` values. If one process owns both ends, they
also share `pid_hash` and both IPs: **socket-port roles and activity direction
still distinguish the observations.** A receive-normalization bug can swap those
roles without changing either hash. Directed-port provenance permits an
independent assertion; it is not a change to connection-ID generation.
<!-- GROUND_TRUTH: ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs §SameIpSamePid_BothSocketRolesKeepDirectedProvenance; ../wintap/devtools/network_endpoint_smoke_test.py §validate_rows -->

## Research and join implications

**Experimental exit-only recovery:** canonical identity can be learned from an
authoritative kernel-start Stop and retained in bounded lifetime-keyed history
without a captured Start or durable lifecycle row. Candidate Linux flag
`WINTAP_EXPERIMENT_EXIT_IDENTITY_RECOVERY=true` is default-off; sidecar fields
`ExitEvidenceRetained` and `LifecycleCoverage=exit-only` distinguish evidence from
coverage. Missing kernel start does not authorize recovery; evicted evidence and
processes with no observed exit remain gaps. Attribution success is not lifecycle
completeness, conservation or release acceptance.
<!-- REVIEW NEEDED: experimental exit-only recovery; isolated/three installed CALDERA controls and eight normal-birth regressions pass workload gates; no-start/no-exit coverage, shutdown-window/drain, release and all-producer gates remain open. -->
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/ProcessResolver.cs §RetainExitIdentityEvidence; ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/LinuxLifecycleEvidence.cs §LifetimeObservation -->
Evidence: [[wiki/work/host-process-identity-patch/package_host_results]].

- Use process-instance identity, not bare PID, for process attribution; retain
  host/agent provenance when interpreting historical datasets.
- Use `conn_id` for bidirectional tuple correlation, but also retain time and
  process/socket perspective. Reused tuples can recur across separate lifetimes.
- Do not treat `pid_hash + conn_id` as a unique socket-role key: the single-process
  example has two roles with that exact pair.
- Do not infer local/remote from low service ports, unequal IPs, Lo/Hi ordering,
  or hash equality. Validate both IP **and port** against activity and provenance.
- An offline standard-view label such as `os_family` is metadata, not identity;
  infer it from the collection host, never from the analysis machine's OS.

<!-- SYNTHESIS: ../wintap/wintap/core/shared/ProcessHash.cs and ../wintap/wintap/core/etl/transform/Transformer.cs and same-process regression/live evidence -->

Related: [[wiki/event_type/process-events]], [[wiki/event_type/network-events]],
[[wiki/work/network-endpoint-normalization/verification]],
[[wiki/diagnostic/duplicate-agent-id-and-os-family]].
