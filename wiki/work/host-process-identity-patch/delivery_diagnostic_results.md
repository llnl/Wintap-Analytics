---
title: "Delivery diagnostics and startup cause: summary"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/wintap/core/infrastructure/EtlStartupReadiness.cs
  - ../wintap/wintap/core/etl/esper/tcp.epl
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap/wintap/core; wiki/work/host-process-identity-patch
tags: [diagnostics, delivery, readiness, cause-proof]
---

# Diagnostic progression

Initial controls failed because observer budgets refused receipts,host roots were
mixed and runtime snapshots were missing. Those captures remain failed;missing
trace evidence was not counted as zero telemetry loss.

Corrected host-isolated controls produced complete bounded histories and exact
finalized→raw joins. File payloads conserved,but broadTCP54→50at Esper→serializer
reproduced on both hosts. Exact registration/projection receipts and a real
production-EPL control proved **pre-registration inputs are not replayed**.

Experimental Linux/default-off readiness waits for successful query registration
and completed serializer constructors before collector admission. Native tests/build
and fresh controls pass startup ordering with zero pre-readiness TCP handoffs.

## Remaining historical distinctions

- Revision12CALDERAsix missing counts were pre-registration. AXONfour were early,
  but six additional post-registration/pre-projection counts remain unexplained.
- Revision13CALDERAconserved54TCPcounts;AXONaccepted54/finalized48. Two exact
  accepted row IDs were absent from drain/export;its exact historical cutoff was
  not recorded. Later shared-defect proof is not retrospective reconstruction.

This led to [[wiki/work/host-process-identity-patch/shutdown_delivery_results]].
Complete observer histories still do not prove pre-callback kernel delivery or
fsync/upload. Original failures,stage joins and qualification receipts are retained
in [[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
