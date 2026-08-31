---
title: "Lintap CPU Unit Conventions"
type: concept
confidence: high
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../Lintap/README.md
  - ../Wintappy/wintap_dbt/models/silver/pidstat_metrics.sql
  - ../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql
  - ../Wintappy/notebooks/wintap_dbt_overview.py
policy: agent-editable
last_validated: 2026-08-31
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/concept/lintap-cpu-unit-conventions.md
tags: [lintap, pidstat, cpu, telemetry-semantics, qa]
---

# Lintap CPU Unit Conventions

Owning implementation is split across sibling `../Lintap` and `../Wintappy`.
Durable commit anchors are `../Lintap@1b23f77` and
`../Wintappy@a53cce6..e4b3bc3`; the live source paths in
`grounded_by` are authoritative.

## Contract

Raw pidstat `cpu_percent` is retained for compatibility but means **core-summed
process CPU percent**. `100` means one fully occupied logical CPU; a multithreaded
process can exceed `100` on a multicore host.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector.py §_build_row -->

The normalized DBT detail model exposes the same value as
`cpu_core_percent`; gold output exposes `max_cpu_core_percent` and
`avg_cpu_core_percent`. The canonical Wintappy QA dashboard labels this metric
as `CPU (core-summed %)`.
<!-- GROUND_TRUTH: ../Wintappy/wintap_dbt/models/silver/pidstat_metrics.sql; ../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql; ../Wintappy/notebooks/wintap_dbt_overview.py §Pidstat controls -->

## Comparison

`top` process `%CPU` and this collector's `cpu_percent` use the same
core-summed convention.
<!-- SYNTHESIS: ../Lintap/pidstat-collector.py divides process CPU time by wall interval without dividing by logical CPU count -->

To compare with host-normalized CPU counters, divide by the number of online
logical CPUs:

```text
cpu_host_percent = cpu_core_percent / logical_cpu_count
cpu_cores = cpu_core_percent / 100
```

For example, on a 32-logical-CPU host, `800` core-summed percent means eight
fully occupied cores, or `25` percent of host CPU capacity.

The filtered Tenable run on this 32-logical-CPU host averaged `.NET` host CPU
usage of `22.4`, equivalent to about `717` core-summed percent or `7.2` busy
logical CPUs. Use this conversion when comparing pidstat charts with runtime
counters.
<!-- SYNTHESIS: lintap-perf-20260830-tenable-filter runtime counter parquet and 32 online logical CPUs on spk16 -->

## Compatibility

Do not rename or reinterpret raw `cpu_percent` in historical parquet. Consumers
that need unambiguous semantics should use `cpu_core_percent` and the matching
gold aliases.
