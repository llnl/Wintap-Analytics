---
title: "Feature brief: Wintap telemetry identity and end-to-end data quality"
type: concept
confidence: high
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/verification.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap; ../Wintappy; ../Lintap; streamlit; wiki/work
tags: [feature-work, retrospective, identity, telemetry-semantics, data-quality]
---

# Wintap telemetry identity and end-to-end data quality

## Problem and scope evolution

The work began with .NET10 upgrade/package verification, then expanded when real
telemetry exposed identity, endpoint, downstream counter/precision and delivery
defects. The useful outcome became **data-quality improvement with independent
proof**, not simply a runtime upgrade.

This is a retrospective workflow, confirmed by the user on2026-10-24. It does not
pretend the final scope, implementation sequence or estimates were known upfront.
Existing workstream records remain historical context; this is the compact entry point.

## Delivered scope

- .NET10 runtime/dependency foundation and supported DuckDB1.5 maintenance.
- Host-unique persisted AgentIds and one canonical hostname/PID/start-time hash.
- TCP endpoint orientation, directed-port provenance and activity vocabulary fixes.
- DBT lifetime grouping, counter conservation and integer FILETIME conversion.
- Bounded attribution experiments, collector-process visibility and honest lifecycle
  and collection-edge interpretation.
- Exact delivery diagnostics and demonstrated startup/shutdown corrections.
- Independent Linux captures, failed controls, pressure tests and fresh DBT verification.

## Acceptance boundary

**Completed milestone:** scoped identity/data-quality improvements and observed
delivery on disposable Linux hosts under explicit experimental controls, including
32/128/256-process bursts and immediate post-workload collector shutdown.

Acceptance requires independent identities, exact generated file counts, bidirectional
non-loopback TCP endpoint checks, complete observed-stage/output joins and downstream
birth/counter preservation. A successful workload, zero sampled drops or an Esper
handoff alone is not sufficient. Failed or incomplete evidence stays failed.

**Not a production release:** package qualification and multi-day real-host collects
are the next phase. No historical migration, universal saturation/coverage guarantee,
Windows live acceptance or complete kernel/fsync/upload proof is claimed.

## Ownership and compatibility

Wintap owns sensor/shared identity, resolver and ETL code; Wintappy owns canonical
Python/DBT/DuckDB processing; Lintap supports packaging/bootstrap; Analytics owns
analysis/QA and this wiki. Preserve unrelated changes across all repositories.

Keep raw100ns identity inputs, genuine lifecycle observations and directionless
connection identity distinct from display timestamps, capture bounds and endpoint
orientation. Unknown sentinels are not identities. Experimental recovery/readiness/
shutdown controls remain opt-in; retry defaults stay1024/ten nominal1s attempts.

## Reading path

Read [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]] for proof
and limits, then [[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]]
for the next phase. Design and reconstructed steps are optional:
[[wiki/work/wintap-telemetry-identity-and-data-quality/design]],
[[wiki/work/wintap-telemetry-identity-and-data-quality/implementation_plan]].
Detailed audit data is excluded from commits; provenance is retained in
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
