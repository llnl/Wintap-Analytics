---
title: "Collection-edge interpretation and outstanding-item reruns"
type: workflow
confidence: medium
grounded_by:
  - wiki/work/host-process-identity-patch/package_host_results.md
  - wiki/work/host-process-identity-patch/collection_edges.py
  - ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/host-process-identity-patch; ../wintap/wintap/platform/linux
tags: [collection-boundaries, quality, verification, experiment]
---

# Approved interpretation

User selected **10 seconds** for both collection edges, with **1/5/20-second**
sensitivity reports. Keep every original strict gate/count. Edge incompleteness is
descriptive, not forgiveness of wrong identity, loss or downstream precision.

Per-sensor bounds bracket possible transitions. Conservative interior must lie
after the latest possible start plus tolerance, and before the earliest possible
cutoff minus tolerance. Edge/outside classification requires agreement for every
possible boundary and every time in an aggregated event span. Otherwise uncertain;
missing bounds/time/verified clock stays unclassified. Never use collector birth,
export time or min/max recorded telemetry as a substitute for capture bounds.

Current BaseEbpfSensor logs bracket hook startup and teardown but cannot certify
continuous polling/delivery. Start is before attachment; started is after poller
launch. Stop begins before disabling polling; stopped is after resource cleanup.
Fresh host clock receipts and startup capabilities are needed before comparing
these local-second log brackets with integer UTC FILETIME event timestamps.
These are operational envelopes, not per-hook availability or drain guarantees.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/shared/BaseEbpfSensor.cs §§Start,Stop -->

# Rerun matrix

- [x] Reclassify all eight revision7 captures; retain absent clock/bound evidence
  as unclassified, not artificially green.
- [x] AXON and CALDERA fresh normal default round: payload conservation and all
  non-loopback endpoint cases; independently canonical identities/collector.
- [x] Both hosts fresh shutdown-window round at unchanged capacity1024/recovery-on:
  separate interior,transition and edge evidence. Preserve failed/unknown exports.
- [x] Fresh canonical DBT model runs for new captures plus another exact-birth precision
  analysis of the four failing revision7 inputs. No float tolerance substitutes.
- [x] Recheck OS labeling, broad config-test failure and dependency regression;
  distinguish existing defects from changed behavior.
- [x] Consolidate results/checklist/verification/glossary and final service/DB receipts.

Results: [[wiki/work/host-process-identity-patch/collection_edge_results]]. Fresh
normal/shutdown scoped raw checks pass; timestamp precision still fails. Historical
loss/saturation causes and exact hook cutoffs are not closed by these reruns.

Use already approved disposable hosts and new capture/evidence roots. Do not
deploy updated dependency packages merely to evaluate boundaries: same installed
revision7 binary is the control. No production/historical migration or capacity
change. Further code fixes follow findings, not speculative causality.
