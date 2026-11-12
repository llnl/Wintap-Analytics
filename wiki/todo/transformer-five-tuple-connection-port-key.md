---
title: "To-Do: Verify Transformer Five-Tuple Connection Port Key"
type: diagnostic
confidence: medium
grounded_by:
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs
  - ../wintap/wintap/core/etl/transform/IdGenerator.cs
policy: agent-editable
last_validated: 2026-11-08
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: network
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/etl/transform/Transformer.cs; ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs; ../wintap/wintap/core/etl/transform/IdGenerator.cs
tags: [todo, backlog, network-events, connection-identity, wintap]
---

# To-Do: Verify Transformer Five-Tuple Connection Port Key

**Priority:** P2 — Medium (provisional; validate production impact before
prioritizing a fix).
**State:** Open — investigation only; no Wintap code change is authorized by
this intake item.
**Likely next step:** Trace representative inbound and outbound TCP/UDP events
through `LoHi5Tuple` and `GenKeyForFive_Tuple_Conn`, then add a focused test that
proves both endpoint ports contribute to the generated connection ID.

## Finding

In `Transformer.CreateProcessConn`, the call to
`GenKeyForFive_Tuple_Conn` passes `loHi.HiIPPortInt` for both the low endpoint
port argument and the high endpoint port argument. The `LoHi5Tuple` type keeps
separate `LoIPPortInt` and `HiIPPortInt` properties, and the key generator
accepts separate low- and high-port inputs and appends both to its key preimage.
This makes the low-port argument at `Transformer.cs:37` look suspicious: for
connections whose low and high endpoint ports differ, the generated key may
encode the high port twice instead of encoding the actual endpoint pair.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/Transformer.cs §CreateProcessConn; ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs §LoIPPortInt/HiIPPortInt; ../wintap/wintap/core/etl/transform/IdGenerator.cs §GenAttrKeyForFive_Tuple_Key -->

That would potentially make different low-endpoint ports share a connection
identifier when the remaining key fields match. It could also make the
identifier inconsistent with the local/remote port values later assigned to
`ProcessConnIncrData`. These are plausible consequences, not yet demonstrated
capture defects; audit actual event shapes and downstream grouping before
concluding severity.
<!-- SYNTHESIS: inferred from the argument order in Transformer.CreateProcessConn and the low/high port fields consumed by IdGenerator.GenAttrKeyForFive_Tuple_Key -->

## Investigation

1. Verify the apparent argument mismatch against the intended FiveTupleKey
   semantics and historical compatibility requirements.
2. Exercise both address orderings, same-address/different-port tuples,
   inbound/outbound events, and TCP/UDP protocol values; assert that reversing
   event orientation yields the intended stable ID while changing either
   endpoint port changes the ID.
3. Check how `LoHi5Tuple.compareAndAssign` assigns each port when IP addresses
   compare equal and when the source endpoint sorts higher than the destination.
4. Profile captured `process_net_conn`/increment data for repeated IDs with
   differing normalized endpoint ports, and distinguish confirmed collisions
   from expected process ownership or metadata variation.
5. If confirmed, propose a narrowly scoped fix and regression test in the Wintap
   code repository; review persisted-ID compatibility and migration implications
   before implementation.

## Open questions

- Is the current argument intentional for a legacy identity contract, or a
  copy/paste error?
- Are there existing persisted records whose connection IDs would change if the
  low-port argument were corrected?
- Does any downstream consumer rely on the current collision/identity behavior?

## Scope

This is an analytics-wiki intake note. No Wintap source, schema, or raw
documents were changed while recording it.
