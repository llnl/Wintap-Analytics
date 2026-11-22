---
title: "Decision: Raw sensor compaction uses immutable window roots"
type: decision
status: superseded
superseded_by: wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup.md
decided_on: 2026-11-12
confidence: high
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/interview.md
  - wiki/work/raw-sensor-file-aggregation/implementation_plan.md
policy: human-review-required
last_validated: 2026-11-12
repo_scope: Wintap-Analytics
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
source_paths: extras/raw-sensor-compact; wiki/work/raw-sensor-file-aggregation
tags: [decision, raw_sensor, compaction, s3, publication]
---

## Context

**Historical decision, superseded:** after clarifying the UUID layout, the human
required fixed `lintap/compacted/<event>/dayPK/hourPK/...` output, existence-based
skip and manual cleanup. See
[[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]]. The text
below preserves the earlier approval, not the current implementation contract.

Current recursive consumers do not consult completion manifests. S3 cannot
atomically replace multiple shards. See
[[wiki/tension/raw-sensor-compaction-publication-vs-glob-readers]].

## Decision

<!-- REVIEW NEEDED: Reader contract approved by the human; implementation/endpoint acceptance remains separately gated. -->

The human approved **immutable per-run roots selected explicitly after
verification**. Each root contains only its requested hours/families; it is not
an accumulating history. Failed candidates remain unselected. A completion
manifest alone does not make arbitrary glob readers safe.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/interview.md §Publication Approval And Test Authorization -->

## Rationale

Separate generations avoid mixing partial or old shards without changing
Wintappy's readers or overwriting the source. A fresh consumer selects exactly
one verified root of the needed coverage, never the common generation parent.

## Consequences

- Reruns may create new generations; only the selected generation contributes
  rows. Source objects remain unchanged; daily rollup/scheduling stay deferred.
- Wide coverage requires a correspondingly wide run, with storage/rebuild costs.
- This approves the **reader contract**, not every implementation/endpoint mode.
  The initial publisher requires conditional metadata writes. The tested endpoint
  ignores that condition, so publication is blocked pending a separate resolution:
  [[wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint]].
- Accepted design is not evidence of completed S3 acceptance; see
  [[wiki/work/raw-sensor-file-aggregation/verification]].

## Alternatives Considered

Stable-root replacement with reader coordination, or manifest-aware reader
changes. Neither is in the approved implementation scope.
