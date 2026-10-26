---
title: "Collection-edge interpretation: results summary"
type: diagnostic
confidence: high
grounded_by:
  - wiki/work/host-process-identity-patch/collection_edges.py
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/host-process-identity-patch; ../wintap
tags: [collection-edges, uncertainty, verification]
---

# Interpretation and findings

User-selected primary10sstart/end bands with1/5/20ssensitivity use integer timestamps,
verified clock receipts and conservative collector brackets. Collector lifetime,
capture interval,query readiness and stimulus window are distinct. Unknown/orphan
identity and event conservation gates are never weakened by edge labels.

Historical revision7 lacks independent clock receipts and remains unclassified.
Fresh normal/shutdown controls pass raw payload/identity/collector/TCPgates;normal
stimuli are interior,shutdown mostly uncertain. Earlier edge failures remain intact.
CALDERAshutdown high-water932/1024without refusals did not reproduce prior saturation.

DBT initially retained collector rows but showed1µsbirth conversion errors;integer
diagnostic conversion isolated the cause. Later canonical macro correction restores
exact births:[[wiki/work/host-process-identity-patch/timestamp_and_trace_results]].

Later delivery/pressure tests preserve these same bands and uncertainty rules.
No actual native-hook cutoff,identity lifetime extension or historical-loss repair
is inferred. Original edge tables,failed precision comparisons and clock receipts:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
