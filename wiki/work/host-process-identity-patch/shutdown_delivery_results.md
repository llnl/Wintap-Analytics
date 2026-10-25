---
title: "Shutdown ordering: demonstrated cause and scoped delivery proof"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/EtlShutdownBarrier.cs
  - ../wintap/wintap/core/infrastructure/SerializerCallbackAdmission.cs
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap/wintap/core/etl; ../wintap/wintap/core/infrastructure
tags: [shutdown, ordering, delivery, cause-proof]
---

# Demonstrated cause

Exact revision14CALDERAreceipts show twoTCProws/fourcounts accepted **after completed
zero-depth shutdown**,then absent from drain/export. Production TCP/context EPL
deterministically strands counts when the queue drains before its final window;
window-before-queue conserves them. AXONpassed that round;older failures remain distinct.

# Bounded experimental correction

Linux/default-off shutdown barrier:stop collectors/final attribution flush → freeze
Esper timer → advance pending bundled10s windows → close/detach callback admission →
join admitted callbacks → existing drains. Clock/callback stages have30s wait bounds;
failure is incomplete,not permission to claim live callbacks drained. It cannot cancel
an already-running native call. No OS/event-time/identity change or arbitrary sleep.

# Proof and limits

Revision16managed candidate qualified267native tests/locked Linux build. Fresh
off/on controls conserve file payloads and observedTCPcounts through exact
producer/projection/acceptance/drain/enqueue/finalized/raw joins. Same-package17repeat
conserves58TCPcounts perhost with all payload/endpoint stimuli interior at1/5/10/20s.
Canonical identity,collector visibility,self-I/O suppression and endpoint gates pass.

This verifies observed disposable-Linux delivery with experimental controls,not a
generic custom-EPL drain,production service deadline,complete kernel/durable fate,
clean native rebuild or installed-release acceptance. Revision15compile failure and
historical12/13AXONdeficits stay preserved. Later pressure proof:
[[wiki/work/host-process-identity-patch/pressure_results]].

Full exact row IDs,receipts,package hashes and original failed controls:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
