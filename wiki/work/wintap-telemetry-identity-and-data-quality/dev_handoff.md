---
title: "Next-phase handoff: package qualification and multi-day collection"
type: concept
confidence: medium
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/brief.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/verification.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: packaging
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../wintap; ../Lintap/packaging; ../Wintappy; wiki/work
tags: [feature-work, handoff, qualification, long-duration, safety]
---

# Next phase—not execution authorization

The user plans clean package qualification and days-long collects on several real
hosts. Hosts,durations,resource/deadline limits and installation/rollback authority
must be established before execution. Do not deploy from this document alone.

Feature commits: Wintap `10a782f`, Wintappy `4236cbb`, Lintap `b793082`;
Analytics QA/wiki/harnesses are in this handoff's commit. Branches are local;
push and PR publication have not been performed.

## Minimal context

1. Read the umbrella [[wiki/work/wintap-telemetry-identity-and-data-quality/brief]]
   and [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]].
2. Read each target repo's AGENTS/build/package guide and inspect its current diff.
   Feature work is on `feature/telemetry-identity-data-quality` in all four repos.
   Wintap branches from the tested `chore/net10-dependency-prune` baseline:target that
   branch for an isolated PR until .NET10 merges. Do not reset or include unrelated work.
3. Consult [[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]] only for
   the exact prior control being reproduced. Local JSON is intentionally uncommitted.

## Preserve these contracts

- .NET SDK10.0.402/self-contained Debian packaging;DuckDB1.5.6 engine,official
  .NET wrapper1.5.6.1. DuckDB2.0 remains held.
- Canonical hostname/PID/birth identity and host-bound AgentId persistence;preserve
  state/data and versioned store boundaries. No historical migration by implication.
- Recovery/readiness/shutdown barrier are Linux/default-off experiments. Latest
  delivery tests enabled them explicitly;default behavior has not inherited that proof.
- Retry capacity1024/ten nominal1s attempts. No resizing or grouped-retry implementation.
- Correct endpoint roles/directed ports and raw100ns identity inputs;never synthesize
  lifecycle observations or interpret missing counters as zero.

## Qualification sequence

Clean full native/eBPF/package build → package contents/dependencies/configuration
review → authorized disposable installation/start/restart/shutdown → independent
telemetry and fresh DBT checks → approved real-host multi-day collects.

For long collects,record package/config/capability provenance,host-isolated data roots,
collector capture intervals and resource/disk health. Agree what constitutes failure
and what may stop a collector. Preserve10s primary/1,5,20s edge reporting and exact
identity/count gates. Keep diagnostic evidence complete and bounded.

Treat Windows runtime,performance/deadlines,actual saturation,kernel/durable fate,
OS/metadata defects and older unexplained losses as named follow-ups. A healthy
long-duration service alone does not close all those claims.
