---
title: "Decision: Process hash inputs and a single formula definition"
type: decision
confidence: high
grounded_by:
  - ../wintap/wintap/core/shared/ProcessHash.cs
  - ../wintap/wintap/core/shared/ProcessIdentity.cs
  - ../wintap/platform/windows/WintapCoreSvcMgr/ProcessHash.cs
  - ../wintap/platform/windows/WintapCoreSvcMgr/WintapCoreSvcMgr.csproj
policy: human-review-required
last_validated: 2026-10-23
repo_scope: wintap
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: accepted
decided_on: 2026-10-23
source_paths: ../wintap/wintap/core/shared/ProcessHash.cs; ../wintap/platform/windows/WintapCoreSvcMgr/ProcessHash.cs
tags: [decision, identity, pid-hash, process-events, single-source-of-truth]
---

# Context

The user explicitly clarified that process identity must not depend on the
collecting agent UUID and that the hash calculation must be defined once in the
entire codebase. The newly documented concept described existing source behavior;
that behavior is not the desired contract.

# Decision

The process-instance identity inputs are **hostname, OS PID, and canonical
process-start time**. `agent_id` is collector provenance and must **not** affect
`pid_hash`. The same identity under another agent UUID must produce the same hash.

There must be **one production formula definition** across the codebase, used
for both `PidHash` and `ParentPidHash`, on all platforms and in helper applications.
Multiple callers/wrappers are permitted; copied or independently reimplemented
preimage construction is not. Sensor-specific start-time acquisition remains
separate from the shared hash algorithm.

<!-- HUMAN DECISION: explicit user clarification, 2026-10-23 -->

# Rationale

Process identity describes a process instance on a named host, not an agent
installation. A single formula prevents producer/platform/helper divergence.

# Consequences

**Source implemented as `pid-v2`, not yet deployed.** The earlier shared and
Windows helper copies included agent UUID. Both now delegate to the single
`ProcessIdentity.Compute` source, linked into the separate helper project.
<!-- GROUND_TRUTH: ../wintap/wintap/core/shared/ProcessIdentity.cs §Compute; ../wintap/wintap/core/shared/ProcessHash.cs §GenPidHash; ../wintap/platform/windows/WintapCoreSvcMgr/ProcessHash.cs §GenPidHash; ../wintap/platform/windows/WintapCoreSvcMgr/WintapCoreSvcMgr.csproj -->

Implementation trims/uppercases hostname invariantly, uses UTC FILETIME for start,
invariant numeric serialization, and the existing two-stage MD5/uppercase hex.
It does not substitute event/receive/Stop time for unresolved process-start time.
<!-- REVIEW NEEDED: review patch serialization and versioned-cache isolation before deployment; user authorized source implementation, not historical repair. -->
Fixed namespace/type markers are serialization details, not extra instance inputs.

Regression gates: invariant under agent changes; changed hostname/PID/start gives
changed identity; parent/child and platform/helper callers use the same formula;
source/build guard against duplicate definitions; canonical-time fixture vectors.

Changing the preimage changes hashes relative to existing recordings. New versioned
process-store filenames isolate the formula without deleting old stores. Deployment
and historical-data compatibility still need explicit migration planning; do not
silently rehash only one table or provenance column.
Agent-ID rotation alone no longer changes process hashes.
Hostname changes still change process identity under this contract.

# Alternatives Considered

- Keep agent UUID in the key: rejected by the user.
- Maintain equivalent platform/helper formula copies: rejected; equivalence can drift.
- Recompute historical identities automatically: not authorized by this decision.

Related: [[wiki/concept/telemetry-identity-and-endpoint-orientation]],
[[wiki/work/host-process-identity-patch/verification]],
[[wiki/decision/process-identity-attribution-contract]],
[[wiki/diagnostic/duplicate-agent-id-and-os-family]].
