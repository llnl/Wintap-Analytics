---
title: "Process-tree context completeness: anonymized short-window audit"
type: diagnostic
confidence: medium
grounded_by:
  - wiki/concept/collector-process-telemetry-and-collection-boundaries.md
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql
  - ../Wintap-PyUtil/wintap_dbt/qa/pid_hash_orphan_checks.sql
  - ../Wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs
  - ../Wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: analytics
event_domain: process
audience: mixed
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt/models/silver; ../Wintap/wintap/platform
tags: [process-tree, collection-boundaries, ancestry, completeness, anonymized-audit]
---

# Outcome and evidence limits

A read-only audit of a six-host, short-partition-window materialized DuckDB
snapshot found **large ancestry gaps concentrated at a few breakpoints**. Missing
long-lived/historical context is the leading explanation, not proof that the
producer lost events. A small immediate-parent defect can disconnect hundreds of
thousands of otherwise linked descendants from an OS root.

**Provenance:** local analyst observations on 2026-11-12, independently checked
with a Python graph walk and the materialized `process_path` relation. The private
database is deliberately not named or copied into this wiki; source links above
ground model behavior, not the numerical observations. Hosts and breakpoints use
snapshot-local aliases, with no persisted identity map. These measurements are
not independently reproducible without operator-supplied access to that snapshot.

Only materialized `process`, `process_path`, `host`, and `pidstat_metrics` were
queried; the stored staging-view definition was inspected, but no remote raw
Parquet rows were read. No DBT rebuild, database repair, or sensor change occurred.
The selected merge/upload partitions cover 15 hourly buckets on one day. Process
birth/EventTime can precede the selected partitions; birth time is not partition
publication time. Broader raw history and deployed startup receipts were not examined.

## Structural results

Traversal follows the selected same-host `parent_pid_hash`. Accepted roots in this
audit are Linux PID 1 and PID 2, and Windows PID 4 System. Root recognition occurs
before cycle detection; Windows System's conventional self-parent is not a defect.
One synthetic Windows PID −1 record is excluded from the denominator. These are
OS-specific structural roots, not a requirement that every process descend from PID 1.

| Alias | Process identities | Root-reachable | Root-reachable fraction | Distinct nonblank absent parent keys |
|---|---:|---:|---:|---:|
| Host-A | 8,044 | 7,893 | 98.1228% | 21 |
| Host-B | 4,382 | 4,137 | 94.4089% | 3 |
| Host-C | 31,349 | 2 | 0.0064% | 50 |
| Host-D | 84,162 | 0 | 0% | 100 |
| Host-E | 33,110 | 0 | 0% | 362 |
| Host-F | 374,964 | 0 | 0% | 77 |

Absent-key counts exclude null/empty parents but include unresolved-parent
sentinels; they are **not counts of proven missing real processes**. Blank-parent
rows are separately observed: Host-A 2, Host-B 1, Host-C 1, others 0 (full process
tables). No non-root graph cycles were found. Root reachability does not certify
metadata, lifecycle completeness, identity correctness, or valid historical lineage.

SSH-service seeds (`sshd`) illustrate the difference between a direct parent and
the full ancestry chain:

| Alias | Seed identities | Immediate-parent breaks | Fail to reach a root |
|---|---:|---:|---:|
| Host-A | 18 | 0 | 0 |
| Host-B | 2 | 0 | 0 |
| Host-E | 7 | 2 | 7 |
| Host-F | 3 | 1 | 3 |

## Descendant amplification

Each affected identity is assigned to its **first unresolved ancestor key**;
impact counts include the directly broken child and all other seeds ending at
that same key. Breakpoint aliases below are local to each host.

| Alias | Largest breakpoint impact | Share of all identities | Top-three combined impact | Share of all identities |
|---|---:|---:|---:|---:|
| Host-C | 13,257 | 42.29% | 26,723 | 85.25% |
| Host-D | 76,293 | 90.65% | 80,485 | 95.63% |
| Host-E | 18,702 | 56.48% | 27,558 | 83.23% |
| Host-F | 353,091 | 94.17% | 365,733 | 97.54% |

- Host-F/BP-1 is an absent long-lived service ancestor; Host-E/BP-1 is another
  absent service ancestor. Their real names, PIDs, and hashes are intentionally omitted.
- Host-D/BP-1 is the absent PID 1 root. Host-D, Host-E, and Host-F have no PID 1
  process record in the materialized table.
- Host-E and Host-F have independent pidstat observations of PID 1 `systemd`,
  PID 2 `kthreadd`, and absent SSH-listener processes. The latter occur across
  4,740 and 4,800 samples respectively. This corroborates existence during
  observation, **not exact process-hash equality or creation-event delivery**.
- Host-C's top three impacts are 13,257, 9,036, and 4,430. BP-1 lies above a
  Stop-only ancestor: one directly broken edge affects 13,257 identities; those
  descendants were all born before the ancestor's recorded exit. A live-only
  refresh after that exit cannot recover the missing historical ancestor.
- Host-C contains only three pre-window birth-context identities, all synthetic
  System/Idle/Unknown entries, each with four Start/Refresh observations. Ordinary
  historical ancestors are absent despite those synthetic observations.

Supplying a breakpoint record offers only **potential** recovery: that ancestor
must itself connect to an accepted root. An unresolved sentinel must not be
"repaired" by inventing a fake parent or linking by PID alone.

## Current-source interpretation, not deployed provenance

Linux startup rundown emits genuine Refresh with canonical birth as EventTime and
skips unavailable births. The inspected method is a startup inventory; an hourly
periodic republication schedule was not verified. Windows same-boot snapshot
recovery may retain resolver state and suppress already-known nonsynthetic
instances. Thus service restart does not guarantee re-export of all ancestor context.
<!-- GROUND_TRUTH: ../Wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs §Start/CreateRefreshMessage; ../Wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs §InitializeSnapshotRefresh -->

The canonical silver process model chooses parent/metadata values using
`any_value`; multiple parent values were observed on several hosts. Its path model
returns the longest **available** chain, not a completeness verdict. The existing
orphan QA checks ownership/keys, not full OS-root reachability.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql §process_base; ../Wintap-PyUtil/wintap_dbt/models/silver/process_path.sql §cte_process_tree/max_level; ../Wintap-PyUtil/wintap_dbt/qa/pid_hash_orphan_checks.sql -->

Do not merge this result with the older timestamp-derived identity failures in
[[wiki/diagnostic/sample-db-runtime-attribution-audit]]. Different snapshots and
mechanisms require different evidence. Here the uninspected alternatives remain:
context never exported, excluded by partition selection, or lost along delivery.

## Related work

- [[wiki/workflow/process-ancestry-completeness-qa]] — reusable definitions and graph procedure.
- [[wiki/concept/durable-process-context-and-stream-table-enrichment]] — persistence and refresh proposals.
- [[wiki/concept/collector-process-telemetry-and-collection-boundaries]] — lifetime, capture, and analysis windows.
- [[wiki/concept/telemetry-identity-and-endpoint-orientation]] — instance keys versus PIDs/sentinels.
- [[wiki/component/process-table-retention]] — bounded runtime history is not durable analytical ancestry.
- [[wiki/event_type/process-events]] — Start/Stop/Refresh producer semantics.
- [[wiki/workflow/future-experiment-analysis-workflows]] — downstream tree/path interpretation.
