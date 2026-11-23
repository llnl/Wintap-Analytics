---
title: "Tension: Private Gateway in Connection Identity"
type: tension
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/transform/Transformer.cs
  - ../wintap/wintap/core/etl/transform/IdGenerator.cs
  - ../wintap/wintap/core/etl/shared/Utilities.cs
  - ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md
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
resolution: "For this round, ordinary default gateways remain metadata and do not affect ConnId; loopback retains host scoping. A symmetric future private-network namespace is deferred."
source_paths: ../wintap/wintap/core/etl/transform/Transformer.cs; ../wintap/wintap/core/etl/transform/IdGenerator.cs; ../wintap/wintap/core/etl/shared/Utilities.cs
tags: [tension, conn-id, private-gateway, nat, endpoint-normalization]
---

# Tension: Private Gateway in Connection Identity

<!-- REVIEW NEEDED: confirm the held resolution accurately records ordinary-gateway exclusion, loopback host scoping, and the deferred symmetric namespace. -->

## Shared requirement

`ConnId` must be identical when endpoint order reverses and when different sensors
observe the same exchange. A network-space discriminator is nevertheless useful
when identical private IP/port tuples from overlapping networks are combined.

## Historical risk and held concern

`Transformer` looks up a gateway only when an endpoint IP matches one of the
observing host's active NICs. For one host-to-host flow, sensor A can therefore
populate the gateway beside endpoint A while sensor B populates it beside endpoint
B. Although `IdGenerator` retains both namespace slots in its private preimage,
`Transformer` now passes ordinary gateways as empty identity namespaces and passes
the host-scoping value only for loopback. Any future ordinary-gateway participation
would need an equivalent complete namespace from both perspectives or it could
split the cross-host identity that endpoint sorting is meant to fuse.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/Transformer.cs §derivePrivateGateway; §CreateProcessConn; ../wintap/wintap/core/etl/transform/IdGenerator.cs §GenAttrKeyForFive_Tuple_Key -->

## Held resolution

The first implementation round selected metadata-only ordinary gateways while
retaining loopback host scoping. Source-linked tests confirm opposite sensors
share an ID when gateway metadata moves endpoint slots and that changing an
ordinary gateway does not rekey the tuple. A symmetric connection-level namespace
or configured per-subnet context remains deferred.
<!-- GROUND_TRUTH: ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md -->

Exact preimage format is not at issue. Any selected design must first pass
opposite-host, reversed-direction, same-host client/server and overlapping-private-
space vectors. No gateway behavior is accepted merely because it is present in the
legacy preimage.
