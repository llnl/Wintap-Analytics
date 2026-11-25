---
title: "Tension: Private Gateway in Connection Identity"
type: tension
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/wintap/core/etl/transform/IdGenerator.cs
  - ../wintap/wintap/core/etl/shared/Utilities.cs
  - ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md
  - ../wintap/developer_docs/audits/sfx-09-loopback-connection-context.md
  - wiki/decision/canonical-five-tuple-connection-identity.md
policy: human-review-required
last_validated: 2026-11-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: mixed
status: held
poles:
  - "Include a stable private-network namespace so identical RFC1918 tuples from overlapping NAT/private spaces do not collide."
  - "Exclude current per-endpoint gateway values until every sensor derives the same namespace for an exchange, preserving cross-host fusion."
resolution: "For this round, both gateway slots are empty for ConnId; loopback uses hostname context and all non-loopback connections use public context. A symmetric future private-network namespace is deferred."
source_paths: ../wintap/wintap/core/etl/transform/Transformer.cs; ../wintap/wintap/core/etl/transform/IdGenerator.cs; ../wintap/wintap/core/etl/shared/Utilities.cs
tags: [tension, conn-id, private-gateway, nat, endpoint-normalization]
---

# Tension: Private Gateway in Connection Identity

<!-- REVIEW NEEDED: confirm the held resolution accurately records empty gateway slots, hostname/public context, and the deferred symmetric namespace. -->

## Shared requirement

`ConnId` must be identical when endpoint order reverses and when different sensors
observe the same exchange. A network-space discriminator is nevertheless useful
when identical private IP/port tuples from overlapping networks are combined.

## Historical risk and held concern

`Transformer` looks up a gateway only when an endpoint IP matches one of the
observing host's active NICs. For one host-to-host flow, sensor A can therefore
populate the gateway beside endpoint A while sensor B populates it beside endpoint
B. Although `IdGenerator` retains both namespace slots in its private preimage,
`Transformer` now passes both identity namespace slots as empty values. Loopback
host scoping instead uses hostname as connection context; every non-loopback
connection uses `public`. Any future ordinary-gateway participation would need an
equivalent complete namespace from both perspectives or it could
split the cross-host identity that endpoint sorting is meant to fuse.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/Transformer.cs §derivePrivateGateway; §CreateProcessConn; ../wintap/wintap/core/etl/transform/IdGenerator.cs §GenAttrKeyForFive_Tuple_Key -->

## Held resolution

The refined implementation keeps all gateway values metadata-only. Source-linked
tests confirm opposite sensors share an ID when gateway metadata moves endpoint
slots, changing an ordinary gateway does not rekey the tuple, loopback hostnames
separate otherwise identical tuples, and non-loopback hostnames do not. A symmetric
connection-level namespace or configured per-subnet context remains deferred;
`public` does not distinguish overlapping private address spaces.
<!-- GROUND_TRUTH: ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md; ../wintap/developer_docs/audits/sfx-09-loopback-connection-context.md -->

Exact preimage format is not at issue. Any selected design must first pass
opposite-host, reversed-direction, same-host client/server and overlapping-private-
space vectors. No gateway behavior is accepted merely because it is present in the
legacy preimage.
