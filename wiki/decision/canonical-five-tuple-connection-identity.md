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
  - ../wintap/developer_docs/audits/sfx-09-loopback-connection-context.md
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

<!-- HUMAN-DECISION: conversation 2026-11-23 — hostname/public context is approved; DBT qualification runs now, Windows testing is deferred but retained, and release is a clean new-data cutover with no legacy/mixed-data requirement. -->

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
- Connection context is selected from the host-oriented local IPv4 endpoint. An
  address in RFC 1122 loopback block `127.0.0.0/8` uses the observing hostname;
  every non-loopback connection uses literal context `public`.
- The existing `Transformer.context = "llnl"` remains for non-connection identities;
  it is no longer the connection context.
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

Ordinary default gateways and loopback host metadata remain recorded but neither
gateway preimage slot receives a value. Loopback host scoping is expressed solely
through connection context, so identical loopback tuples on unrelated hosts do not
collide. A future symmetric private-network namespace remains held; see
[[wiki/tension/private-gateway-connection-identity]].

## Rationale

This contract allows events observed from opposite host/process perspectives to
fuse directly in SQL joins and graph operations without repeating normalization
downstream. Context preserves a namespace hook for overlapping address spaces,
although the current non-loopback value `public` does not itself distinguish
overlapping private networks. Keeping preimage encoding private to the sole .NET
implementation avoids cross-language byte-for-byte coupling.

## Consequences

- Wintap needs semantic tests covering endpoint reversal, opposite-sensor and
  same-host client/server views, both ports, both IPs, protocol and context.
- Downstream exact output is not an acceptance oracle. DBT and the legacy PyUtil
  raw-view repair retain overrides only until .NET behavior is qualified, then
  return to producer `connid`.
- Removing the override changes silver IDs to producer IDs. Release starts a fresh
  new-data population rather than migrating or combining legacy materializations.
- Moving loopback host scoping into context and replacing connection context
  `llnl` with `public` intentionally rekeys all producer connection IDs.
- A future gateway/network-space namespace must preserve cross-sensor symmetry.
- Historical recordings are not mutated or included in the release cutover.

## Alternatives Considered

- **Require .NET to reproduce DBT canonical JSON exactly:** rejected; exact preimage
  encoding is not part of the semantic contract and DBT generation is being removed.
- **Replace the legacy nested Wintap convention solely for format simplicity:**
  rejected; consistency and semantic behavior matter, not preimage aesthetics.
- **Keep DBT authoritative permanently:** rejected because identity must be
  established once at the producer boundary and remain available to all consumers.
