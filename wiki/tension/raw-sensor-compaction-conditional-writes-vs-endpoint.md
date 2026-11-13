---
title: "Tension: Conditional compaction metadata vs. configured S3 endpoint"
type: tension
status: dissolved
poles:
  - "The initial publisher uses conditional PUT to reserve roots and avoid overwriting immutable completion metadata, including ambiguous successful responses."
  - "The live lintap-alpha endpoint silently accepts and overwrites keys despite If-None-Match: *, so those guarantees cannot be inferred from successful SDK calls."
resolution: "Conditional reservations were removed under the human's fixed-hour/skip/manual-cleanup decision; see wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup.md."
confidence: high
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/verification.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
policy: agent-editable
last_validated: 2026-11-12
repo_scope: Wintap-Analytics
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
source_paths: extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
tags: [tension, raw_sensor, s3, publication, conditional-put]
---

# Conflict

**Historical, dissolved:** [[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]]
removed run reservations/manifests/conditional PUT. The configured endpoint is
usable for the new direct-merge workflow; the earlier probes below remain valid
observations, but are no longer publication prerequisites.

The approved [[wiki/decision/raw-sensor-compaction-immutable-window-roots]]
settles reader selection, not storage concurrency primitives. Two fresh-key
probes on the configured endpoint showed that a conflicting PUT carrying
`If-None-Match: *` returned HTTP 200 and replaced the object. Managed `compact`
now tests enforcement on reservation metadata and fails closed before Parquet.
<!-- GROUND_TRUTH: wiki/work/raw-sensor-file-aggregation/verification.md §Live S3 Tests (historical generation implementation) -->

Direct DuckDB S3 COPY/count verification passed on a deliberately unpublished
test root, with unchanged source hashes. This does not close the publication gap.

## Options Requiring A Decision

1. Use an endpoint that enforces conditional writes and qualify its failure behavior.
2. Design and explicitly approve UUID-only, fresh-root allocation without an atomic
   reservation, including collision/concurrent-writer and lost-response semantics.
   This might preserve the chosen reader contract, but is not implemented or approved.
3. Use a separately scoped external atomic coordination service.

No silent fallback, stable-root overwrite, or source mutation is allowed. Candidates
and probe objects remain unselected; no completed live root has been returned.
