---
title: "Tension: refresh republication versus durable process context"
type: tension
confidence: medium
grounded_by:
  - wiki/diagnostic/process-tree-context-completeness.md
  - wiki/concept/durable-process-context-and-stream-table-enrichment.md
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: process
audience: mixed
status: open
source_paths: wiki/diagnostic/process-tree-context-completeness.md; wiki/concept/durable-process-context-and-stream-table-enrichment.md
tags: [refresh, retention, process-context, research-workflows]
poles:
  - "Frequent full republication makes recent partitions more self-describing and can repair missing live state, at the cost of duplicate volume and scan/update work."
  - "Durable historical entity state and context-complete exports reduce repetition and preserve exited ancestors, but require retention, recovery, and extract-closure mechanisms."
resolution: null
---

# Open design choice

The anonymized [[wiki/diagnostic/process-tree-context-completeness]] audit shows
that a few absent ancestors can disconnect most descendants. Neither an hourly
live snapshot nor a bounded runtime resolver alone guarantees historical ancestry.

[[wiki/concept/durable-process-context-and-stream-table-enrichment]] proposes a
hybrid: lifecycle-driven durable history, startup/recovery bootstrap, periodic
reconciliation, and explicit context closure for short extracts. No cadence,
retention horizon, schema change, or implementation has been approved.

Keep research-selectable windows and incomplete evidence visible. Resolve only
after a human selects recovery/coverage goals and measured operational costs;
do not turn a suggested refresh pilot into a universal completeness claim.
