---
title: "Implementation Plan: Support for Docker Contexts on Linux"
type: concept
confidence: medium
grounded_by:
  - wiki/work/support-docker-contexts-linux/brief.md
  - wiki/work/support-docker-contexts-linux/design.md
policy: agent-editable
last_validated: 2026-09-01
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/support-docker-contexts-linux/implementation_plan.md
tags: [feature-work, implementation, linux, cgroups, containers]
---

# Implementation Plan: Support for Docker Contexts on Linux

## Scope

Research prototype only. Preserve existing stable schemas while comparing
context collection and attribution approaches.

## Steps

1. Define versioned diagnostic observation records and provenance/error taxonomy.
2. Build phase-1 host, systemd, and Docker cgroup v2 fixtures.
3. Implement baseline cgroup and namespace observation.
4. Implement or adapt snapshot and lifecycle/change capture.
5. Compare producer-local, shared-resolver, and eBPF event-time enrichment.
6. Exercise process, file, network, and pidstat output paths.
7. Add optional OCI/runtime/systemd sources as isolated adapters.
8. Run phase-2 v1/hybrid and Podman validation where available.
9. Analyze fidelity, lifecycle, overhead, dependencies, and failure modes.
10. Produce a recommendation and propose the next normalized schema/design slice.

## Files Likely To Change

- Prototype/diagnostic files in an explicitly selected Linux development location.
- Existing validation harness documentation and feature artifacts.
- Potentially `../wintap` Linux sensor files only after explicit code-development authorization.
- Potentially `../Lintap` collector files only after explicit sibling-repo authorization.

## Tests To Add Or Update

- Cgroup v1/v2/hybrid parser tests.
- Namespace identity and PID reuse tests.
- Membership, migration, emptying, deletion, and short-lived process tests.
- Cross-event-family attribution tests.
- Fixture-level comparison and overhead tests.

## Migration Or Compatibility Notes

No migration and no stable schema change in this prototype. Diagnostic records
must be versioned so later schemas can be derived without recollecting evidence.

## Rollback Plan

Keep the prototype behind explicit diagnostic commands/configuration. Remove or
disable prototype wiring without changing existing Linux sensor output paths.

## Done Checklist

- [ ] Diagnostic observation contract defined.
- [ ] Phase-1 fixture reproducible.
- [ ] Baseline cgroup/namespace collector implemented.
- [ ] Snapshot and lifecycle alternatives compared.
- [ ] Producer-local/shared/eBPF enrichment compared.
- [ ] Cross-event-family evidence collected.
- [ ] Phase-2 compatibility investigated or gap documented.
- [ ] Overhead and loss measured.
- [ ] Recommendation reviewed.
- [ ] Durable findings promoted to canonical wiki pages.
