---
title: "Feature Interview: Support for Docker Contexts on Linux"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
  - https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md
policy: agent-editable
last_validated: 2026-09-01
repo_scope: cross-repo
implementation_area: windows-sensor
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/support-docker-contexts-linux/interview.md
tags: [feature-work, linux, cgroups, containers, docker, ebpf, namespaces, research]
---

# Feature Interview: Support for Docker Contexts on Linux

## Initial Idea

Expand Linux collection to include Docker contexts, via cgroups or similar.

## Context Established Before Questioning

The existing pidstat collector already emits per-process `cgroup_path`,
`pid_ns_inode`, and best-effort runtime/ID fields, but only in the optional
performance stream. Linux eBPF process, file, and network sensors currently
resolve event context through producer-specific paths. The new feature should
therefore investigate a broader context model rather than simply adding more
pidstat columns.

Related context: [[wiki/work/improve-pidstat-collector/design]],
[[wiki/repo/lintap-supporting-repo]], and
[[wiki/component/wintap-api-shared-data-model]].

## Interview Log

### Round 1

**Q:** Should this enrich existing rows, add a separate context stream, or both; which workloads and event families are in scope; and should the normalized schema change now?
**A:** Both enrichment and a separate context/inventory stream. Support any Linux cgroup workload, with Docker identity best-effort. Include all Linux telemetry attributable to a PID or namespace. Prototype collection first and defer the normalized schema.
**Outcome:** decision — broad research scope with schema deferred.

### Round 2

**Q:** What should the inventory stream represent, which fields matter first, where should enrichment occur, and what evidence is required?
**A:** Leave snapshot versus lifecycle representation to prototyping. Start with identity and process membership. Compare integration approaches rather than choosing a resolver boundary up front. Require mixed fixtures, PID lifetime/reuse behavior, v1/v2/hybrid handling, discovery/change/removal, visibility across process/file/network/pidstat output, and overhead measurements.
**Outcome:** delegated — prototype determines representation and integration boundary.

### Round 3

**Q:** Which acquisition paths, temporary output, and environments should be compared?
**A:** Compare the existing `/proc` collector, Linux eBPF paths, a shared userspace resolver, and direct cgroup polling/snapshots. Emit both existing outputs where practical and diagnostic artifacts. Start with cgroup v2, host processes, systemd scopes/services, and Docker; then test v1/hybrid and Podman; defer Kubernetes/containerd.
**Outcome:** decision — staged comparison matrix and evidence-preserving output.

### Round 4

**Q:** Confirm the staged matrix, fidelity policy, and hard constraints.
**A:** Staging confirmed. Fidelity policy is delegated to the prototype. No hard constraints; additional approaches may be explored.
**Outcome:** delegated — prototype determines valid identity and fidelity rules.

## Decisions

- Both per-event enrichment and a separate context/inventory stream are in scope.
- Any Linux cgroup workload is in scope; Docker naming is best-effort.
- Process, file, network, and pidstat/performance telemetry are in scope where PID or namespace attribution is possible.
- Collection prototyping precedes stable WintapAPI/DBT schema design.
- Phase 1 is cgroup v2, host processes, systemd scopes/services, and Docker.
- Phase 2 is cgroup v1/hybrid and Podman; Kubernetes/containerd is deferred.

## Constraints

- Identity and process membership are the first context fields.
- Raw observations, source paths, timestamps, and parse failures must remain inspectable.
- All requested validation gates apply, including correctness, lifecycle, cross-event-family visibility, and overhead.

## Delegations

- Select the best integration boundary after comparing producer-local enrichment, a shared resolver, and eBPF event-time identity.
- Select snapshot, lifecycle, or hybrid inventory semantics after experimentation.
- Determine fidelity rules and stable fields from evidence.
- Explore runtime APIs, OCI state, systemd metadata, namespace identity, notifications, and other useful sources.

## Deferred / Open Questions

- Final normalized event/table shape and ownership.
- Whether inventory is snapshots, transitions, or both.
- Whether resource, image, label, mount, and command metadata belong in this feature.
- How to correlate eBPF cgroup IDs with userspace context records.
- Whether runtime-specific APIs justify their dependency and permission costs.

## Playback Summary

Build a research prototype that compares cgroup filesystem inspection, namespace
identity, eBPF event-time cgroup identity, shared userspace resolution, and
optional OCI/runtime/systemd/notification sources. Preserve evidence in both
diagnostic artifacts and existing output paths where practical. Do not freeze a
normalized schema until the prototype establishes which context and membership
signals are valid across the staged Linux environments.

## Sealed — human estimates

**Q: If you had to build this exact scope alone, without AI, how many working hours would it take? And on what date would it realistically have been available?**
**A:** 2 weeks to get a working prototype with acceptable data quality

**Q: With the AI workflow, on what date do you predict this feature will be available?**
**A:** 3 days
