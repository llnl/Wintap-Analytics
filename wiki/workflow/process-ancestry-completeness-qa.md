---
title: "Process ancestry completeness QA"
type: workflow
confidence: medium
grounded_by:
  - wiki/diagnostic/process-tree-context-completeness.md
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql
  - ../Wintap-PyUtil/wintap_dbt/qa/pid_hash_orphan_checks.sql
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: mixed
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt/models/silver; ../Wintap-PyUtil/wintap_dbt/qa
tags: [process-tree, qa, ancestry, breakpoints, research-workflows]
---

# Measure context, not merely parent joins

This is a proposed reusable QA contract, illustrated by
[[wiki/diagnostic/process-tree-context-completeness]]. It is **not implemented as
a new DBT test or dashboard**. Wintappy owns canonical downstream transformations;
Wintap-Analytics hosts this analysis guidance. Lintap is supporting infrastructure.

## Declare the graph and denominator

1. Declare the data layer: raw observations, normalized instances, or selected
   materialized parent graph. Record partition selection separately from event-time bounds.
2. Use the canonical process-instance key in its documented host scope, never PID
   alone. Validate key uniqueness and cross-host isolation before walking.
3. Declare OS-specific accepted roots and excluded synthetic records. Report
   kernel-task branches separately if the research question needs PID 1 ancestry.
4. Declare whether seeds are all recorded processes, births in the analysis
   window, or processes referenced by selected file/network activity. Historical
   context records must not silently inflate an in-window seed denominator.
5. Distinguish the selected parent graph from conflicting raw parent observations;
   show conflict counts instead of treating an arbitrary aggregate as authoritative.

## Metrics

| Metric | Definition / interpretation |
|---|---|
| **Root-Reachable Process Fraction (RPF)** | Seeds reaching an accepted root / eligible seeds. Structural context coverage, not lifecycle validity. |
| **Immediate broken-parent rate** | Non-root seeds with no valid same-host direct parent / non-root seeds; split absent nonblank keys, sentinels, and blank parents. |
| **Distinct absent real-key candidates** | Unique absent nonblank, nonsentinel parent keys; do not label them confirmed missing processes without independent evidence. |
| **First-unresolved-ancestor impact** | Count of seeds terminating at each missing key/sentinel/blank boundary; includes indirectly affected descendants. |
| **Top-1 / Top-3 concentration** | Largest one/three breakpoint impacts / unresolved seeds. Also show / all seeds to quantify overall exposure. |
| **K95** | Minimum number of distinct keyed breakpoints covering at least 95% of keyed-breakpoint failures; report blank/cycle failures separately. Undefined when there are no keyed failures. |
| **Independent validity checks** | Parent conflicts, self-links/non-root cycles, missing Start/Refresh, missing Stop, metadata gaps, canonical-birth/hash checks, impossible known lifetimes, and parent/child time compatibility. |

An exited parent may have living descendants. Do **not** require that parent and
child be simultaneously alive at the descendant's later activity time. Check
birth-time plausibility using known evidence; absence of Stop does not prove
continuous life, and incomplete metadata does not prove an invalid instance.

## Read-only graph procedure

Build an in-memory same-host instance map. For each seed, walk selected parent
keys, recognizing accepted roots first. Stop at root, absent key, sentinel, blank,
or non-root cycle. Memoize terminal outcomes so shared ancestor chains are walked
once; retain cycle membership separately. Aggregate terminal outcomes and impact
counts, then compare with materialized path lengths/terminal nodes.

This is an independent diagnostic algorithm, not a copy of production SQL.
Cycles must be guarded even though the current path model prevents repeated keys.
An existing path row means a chain was found, not that the chain reaches a root.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql §cte_process_tree -->

For top breakpoints, inspect Start/Refresh/Stop availability, genuine birth versus
observation time, broader publication partitions, rundown/readiness receipts, and
independent inventory such as pidstat. Report potential repair impact, not promised
RPF improvement: adding an ancestor may reveal another missing ancestor above it.

Keep reports anonymized using snapshot-local aliases and aggregate values. Do not
persist hostnames, IPs, instance hashes, private data paths, or an alias map.

Related: [[wiki/concept/durable-process-context-and-stream-table-enrichment]],
[[wiki/concept/telemetry-identity-and-endpoint-orientation]],
[[wiki/workflow/future-experiment-analysis-workflows]].
