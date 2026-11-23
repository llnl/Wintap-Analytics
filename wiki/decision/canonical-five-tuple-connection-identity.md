---
title: "Decision: Canonical Five-Tuple Connection Identity"
type: decision
confidence: high
grounded_by:
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/tests/test_network_activity_sql.py
  - ../Wintap-PyUtil/wintappy/datautils/rawutil.py
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs
  - ../wintap/wintap/core/etl/transform/IdGenerator.cs
  - ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md
policy: human-review-required
last_validated: 2026-11-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: mixed
status: accepted
decided_on: 2026-11-23
source_paths: ../wintap/wintap/core/etl/transform; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintap-PyUtil/wintappy/datautils/rawutil.py
tags: [decision, connection-identity, conn-id, five-tuple, dbt, wintap]
---

# Decision: Canonical Five-Tuple Connection Identity

<!-- REVIEW NEEDED: confirm the accepted ADR text reflects the approved first-round implementation and deferred native Windows/rebuild acceptance. -->

## Context

Wintap emits a direction-independent legacy `ConnId` using a nested .NET hash
preimage. Wintap-PyUtil previously replaced it in silver DBT with a different
JSON/MD5 formula. That duplicate implementation made exact hash differences look
like semantic differences even when endpoint normalization agreed; it was removed
in the first implementation round.

An older ACME4 compatibility workaround says the historical producer failed to
sort source/destination fields and recomputes `ConnId` from persisted endpoint
columns. Available evidence does not establish whether any absent producer build
also duplicated a remote IP into both persisted IP columns. This decision defines
future semantics and ownership; it does not identify that old defect conclusively
or make corrupted endpoint columns recoverable.
<!-- GROUND_TRUTH: ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md -->

## Decision

The canonical contract is semantic rather than a mandate to reproduce DBT's exact
preimage:

- `ConnId` represents context plus the network five-tuple: transport protocol and
  two IP/port endpoint pairs.
- Context namespaces otherwise identical private address spaces. It remains
  hardcoded as `llnl` for now; retaining it preserves the future ability to assign
  different contexts to overlapping network spaces.
- Normalize by sorting **whole endpoint pairs**, not independent IP and port
  scalars. Numeric IP orders first; port breaks a same-IP tie.
- Swapping endpoint order must preserve `ConnId`. This applies across opposite
  send/receive views, two sensors observing the same host-to-host exchange, and
  client/server processes on one host.
- Changing context, protocol, either endpoint IP, or its paired port changes the
  represented identity.
- The exact deterministic preimage format is an implementation detail. Wintap's
  legacy names, nesting, redundant address representation and double-MD5 convention
  may remain; matching DBT's JSON bytes is not required.
- Exactly one implementation generates `ConnId`, in Wintap .NET. DBT and legacy
  Python paths must consume producer `connid` rather than recompute it.
- `ConnId` remains tuple identity, not a socket or connection-lifetime identifier.

Ordinary default gateways remain metadata rather than identity inputs in this
round because endpoint-slot derivation is host-relative. Loopback retains its
host-scoping value so identical loopback tuples on unrelated hosts do not collide.
A future symmetric private-network namespace remains held; see
[[wiki/tension/private-gateway-connection-identity]].

## Rationale

This contract allows events observed from opposite host/process perspectives to
fuse directly in SQL joins and graph operations without repeating normalization
downstream. Context preserves a namespace hook for overlapping address spaces,
while keeping preimage encoding private to the sole .NET implementation avoids
cross-language byte-for-byte coupling.

## Consequences

- Wintap needs semantic tests covering endpoint reversal, opposite-sensor and
  same-host client/server views, both ports, both IPs, protocol and context.
- Downstream exact output is not an acceptance oracle. DBT and the legacy PyUtil
  raw-view repair retain overrides only until .NET behavior is qualified, then
  return to producer `connid`.
- Removing the override changes current silver IDs to producer IDs. Dependent
  materializations and joins require coordinated rebuild and qualification.
- A future gateway/network-space namespace must preserve cross-sensor symmetry.
- Historical recordings are not mutated by this decision.

## Alternatives Considered

- **Require .NET to reproduce DBT canonical JSON exactly:** rejected; exact preimage
  encoding is not part of the semantic contract and DBT generation is being removed.
- **Replace the legacy nested Wintap convention solely for format simplicity:**
  rejected; consistency and semantic behavior matter, not preimage aesthetics.
- **Keep DBT authoritative permanently:** rejected because identity must be
  established once at the producer boundary and remain available to all consumers.
