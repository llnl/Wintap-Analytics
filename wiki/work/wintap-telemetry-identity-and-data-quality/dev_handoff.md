---
title: "Next-phase handoff: package qualification and multi-day collection"
type: concept
confidence: medium
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/brief.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/verification.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: packaging
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../wintap; ../Lintap/packaging; ../Wintappy; wiki/work
tags: [feature-work, handoff, qualification, long-duration, safety]
---

# Next phase—not execution authorization

Latest analysis: [[wiki/work/wintap-telemetry-identity-and-data-quality/quality_followup_analysis]].
Subsequent user-authorized local implementation:
[[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]].
The paragraph below preserves the pre-implementation boundary; the user later
authorized Analytics/Wintap source corrections and disposable-VM qualification,
**not** collection-host install/restart/tracer attachment or rollout. Next operator
gate is trusted package review/provenance and an approved non-interfering pilot.
Prioritize Analytics observation-check regressions; separately authorize Wintap Accept
emission/UDP memory-domain corrections and trusted build qualification. Current source
is not proven identical to the deployed tracer. Repeated raw Starts need source-aware
accounting, not automatic deletion or duplicate-birth classification. No deployment
or source changes are authorized by that analysis.

The user plans clean package qualification and days-long collects on several real
hosts. Hosts,durations,resource/deadline limits and installation/rollback authority
must be established before execution. Do not deploy from this document alone.

Feature commits: Wintap `10a782f`, Wintappy `4236cbb`, Lintap `b793082`;
Analytics QA/wiki/harnesses are in the retrospective commit. Those original commits
were local at closeout; the user now authorizes .NET 10 corrections and commit/push
on the same branches for cross-system builds. PR publication remains separate.
Current correction results and gates:
[[wiki/work/wintap-telemetry-identity-and-data-quality/runtime_alignment_plan]].

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

For the corrected core network contract, verify trusted package/object hash plus
receipt version2 and operation return hooks. Review UDP protocol-return byte meaning,
sampling and exact independent mode/socket expectations. Use only a reviewed prebuilt
native helper on field hosts; actual-object observer is dev-time/idle-VM-only.
Use a helper compiled/reviewed for the target architecture, not the arm64 VM
artifact on x64 hosts. Normal process source-provenance persistence and Linux
file-case projection require their own reviewed prospective contracts; current
dashboard must leave those unknown, not rewrite/merge historical observations.

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
