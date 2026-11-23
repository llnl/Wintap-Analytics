---
title: "Diagnostic: Canonical Five-Tuple Connection Identity"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs
  - ../wintap/wintap/core/etl/transform/IdGenerator.cs
  - ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/tests/test_network_activity_sql.py
  - ../Wintap-PyUtil/tests/test_rawutil_conn_id_passthrough.py
  - ../Wintap-PyUtil/wintappy/datautils/rawutil.py
  - ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md
policy: agent-editable
last_validated: 2026-11-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: mixed
status: stable
source_paths: ../wintap/wintap/core/etl/transform; ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintap-PyUtil/tests/test_network_activity_sql.py; ../Wintap-PyUtil/wintappy/datautils/rawutil.py
tags: [diagnostic, network-events, connection-identity, five-tuple, wintap, dbt]
---

# Diagnostic: Canonical Five-Tuple Connection Identity

**Priority:** P2 — Medium.
**State:** Bounded single-authority implementation complete; native Windows and
deployment/rebuild acceptance remain pending.
**Decision:** Direction-independent semantics are canonical, exact DBT bytes are
not, and Wintap .NET must be the only production generator; see
[[wiki/decision/canonical-five-tuple-connection-identity]].

## Corrected finding

The original intake alleged that `Transformer.CreateProcessConn` passed the high
port for both endpoint-port arguments. That allegation does not reproduce in the
current source or any history available in this repository. The 2024 initial
import already passes `LoIPPortInt` and `HiIPPortInt` separately; later changes
did not repair or alter that call. This establishes the behavior of available v7
history, but cannot rule out a defect in an earlier ACME4-era source/build that is
not present here.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/Transformer.cs §CreateProcessConn; git history through initial commit 9c9ba7752474fb217072eb0d28c83530d4897857 -->

`LoHi5Tuple` orders endpoint pairs by numeric IP and uses port as the same-IP
tie-breaker. The current Wintap key is direction-independent, and direct vectors
against the live C# sources confirm that changing either port, either IP, or the
protocol changes the result.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs §compareAndAssign; ../wintap/wintap/core/etl/transform/IdGenerator.cs §GenAttrKeyForFive_Tuple_Key; ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs -->

## Actual compatibility gap

Wintap and DBT agree on endpoint-pair ordering but not on the complete identity
contract or exact hash:

| Property | Current Wintap producer | Temporary DBT behavior |
|---|---|---|
| Endpoint ordering | Numeric IP, then port for equal IPs | Same |
| Direction reversal | Stable | Stable |
| Tuple sensitivity | Both IPs, both ports and protocol contribute | Same |
| Additional inputs | Context, dotted address strings and both private-gateway strings | Fixed context only; no string-address or gateway inputs |
| Preimage/hash | Nested legacy attribute/entity MD5 preimages | Uppercase MD5 of ordered canonical JSON |
| Incomplete tuple | Numeric inputs are non-nullable; the key method can still hash null strings/default numbers | Returns null if protocol or either endpoint IP/port is missing |
| Exact persisted ID | Legacy Wintap value | Different canonical value |

<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/IdGenerator.cs §GenAttrKeyForFive_Tuple_Key; §GenKeyForFive_Tuple_Conn; git history for removed PyUtil commit 189da24 -->

The DBT override was introduced in commit `189da24` on 2026-11-10 and merged in
`0e2c7eb` on 2026-11-12. It intentionally replaces producer `connid`; its source
and README both call it temporary and assign the authoritative implementation to
Wintap .NET. The history contains no claim that this was a repair for a duplicated
port argument.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintap-PyUtil/wintap_dbt/README.md §Temporary network identity compatibility change -->

The older PyUtil workaround, added in commit `ab9b90a` in 2024, is the closest
available evidence about the ACME4 defect. Its source comment says ACME4 Wintap
created `CONNID` without sorting source/destination fields, then recomputes the ID
from persisted `localipaddr`, `localport`, `remoteipaddr`, `remoteport`, and
protocol. That supports a bad-ID/order diagnosis and assumes the persisted tuple
is usable. It does **not** prove whether a separate producer build ever copied the
remote IP into both persisted IP columns.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/datautils/rawutil.py §get_raw_view; commits ab9b90a and acd89ac -->

These possible defects have different recoverability:

- If only the generator received the remote endpoint twice, while the persisted
  local/remote columns remained correct, both the old workaround and current DBT
  can discard the bad producer ID and compute a valid replacement.
- If serialization wrote the remote IP into both persisted IP columns, current
  DBT hashes that corrupted tuple and cannot recover the lost local IP. Recovery
  would require another trustworthy field or source artifact.

The current DBT formula is therefore both a historical compatibility repair and a
later downstream implementation choice. Its exact JSON preimage and null policy
are not the canonical target and should not be presented as proof of the original
producer defect.

## Verification

Bounded offline evidence is under
`/data/lintap-compactor/sensor-fixes/five-tuple-20261122/`:

- Direct compilation of the live `IdGenerator`, `LoHi5Tuple`, and `Converters`
  sources with SDK 10.0.402 passed reversal, same-IP reversal, both changed-port,
  changed-IP, and changed-protocol vectors. It also proved gateway sensitivity and
  that incomplete/default input can still produce a non-null legacy key.
- Direct DuckDB execution of the existing DBT contract returned zero issues.
- The two formulas produced 32-character uppercase hashes but not the same value
  for the same complete tuple.
- The existing Wintap xUnit class could not execute on Linux because its built
  assembly targets Windows. This is a platform boundary, not a failed semantic
  assertion; native Windows acceptance remains deliberately deferred.
- The PyUtil pytest wrapper was not run because its checked-in environment is
  unavailable. No environment was created and no dependency was installed; the
  shipping contract SQL itself was executed with the installed DuckDB CLI.

## Completed single-authority migration

The exact legacy .NET preimage remains. The bounded source round completed:

1. Prove context plus protocol and both complete IP/port endpoint pairs contribute
   to producer identity.
2. Prove whole-pair reversal stability for send/receive, opposite host sensors,
   and same-host client/server processes, including equal-IP port tie-breaking.
3. Prove changing context, protocol, either IP, or either paired port changes the
   identity.
4. Ordinary gateways remain metadata; loopback retains host scoping. Opposite
   sensors with gateway metadata in opposite endpoint slots now share an ID.
5. Silver DBT and legacy PyUtil raw views preserve producer `connid`; both
   downstream hash implementations and DBT's exact-output contract were removed.
6. Deployment remains gated on native Windows acceptance and coordinated rebuild
   because existing DBT IDs and producer IDs differ. Do not silently mix them.

Repeated uses of one five-tuple continue to share an ID because this is tuple
identity, not socket-lifetime identity.

## Scope

This investigation changed wiki documentation only. The absent ACME4 producer
source/build or sanitized value-level evidence remains required to distinguish a
hash-input/order defect conclusively from duplicated persisted endpoint columns.
Wintap and Wintap-PyUtil
source and tests were modified in the authorized bounded round. Schemas,
historical data, materialized DBT outputs, dependencies, and deployments were not
modified. No network, S3, or native Windows acceptance was performed. Full results:
`../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md`.
