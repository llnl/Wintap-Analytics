---
title: "Feature Design: Support for Docker Contexts on Linux"
type: concept
confidence: speculative
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/ProcReader.cs
  - https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
  - https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md
policy: agent-editable
last_validated: 2026-09-01
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/support-docker-contexts-linux/design.md
tags: [feature-work, design, linux, cgroups, containers, ebpf]
---

# Feature Design: Support for Docker Contexts on Linux

## Summary

Treat Linux context collection as an evidence-comparison problem. Build a
neutral context observation model first, then compare acquisition and
enrichment strategies against the same workloads. Do not make Docker names the
primary key and do not commit stable WintapAPI/DBT fields during this slice.

## Proposed Approach

1. Build phase-1 fixtures for cgroup v2 host processes, systemd scopes/services, and Docker.
2. Capture baseline observations from `/proc/<pid>/cgroup`, namespace links, cgroup directories, and membership files.
3. Compare periodic snapshots with cgroup event notifications for discovery/change/removal.
4. Compare producer-local `/proc` enrichment, a shared userspace resolver, and eBPF event-time cgroup IDs.
5. Add optional OCI/runtime/systemd adapters only as separate evidence sources.
6. Emit diagnostic JSONL plus existing telemetry output where safe and useful.
7. Score approaches on attribution fidelity, short-lived process coverage, lifecycle behavior, overhead, dependency/permission cost, and cross-event consistency.

## Data Model Or Schema Changes

No stable schema change is approved. The diagnostic record should be versioned
and retain raw source values, normalized candidate values, source/provenance,
observation time, PID/start identity where available, namespace IDs, cgroup
path/version, membership, lifecycle state, and errors.

## Interfaces And User Experience

The prototype should expose a repeatable capture command/configuration, fixture
setup guidance, and a comparison report. Operators should be able to disable
optional runtime adapters and run the generic cgroup path without Docker.

## Edge Cases

- PID reuse between observation and event enrichment.
- Short-lived processes that exit before `/proc` resolution.
- cgroup v1 multi-line membership and v2 unified `0::/path` membership.
- Hybrid mounts with multiple controller hierarchies.
- Processes moved between cgroups.
- Empty/deleted cgroups and zombie processes.
- Nested cgroups and ambiguous runtime-like path names.
- Namespace sharing without container runtime metadata.
- Runtime metadata unavailable or stale.

## Error Handling

Never discard an observation solely because runtime parsing fails. Preserve raw
values and an explicit error/provenance record. Distinguish unavailable,
permission-denied, raced-with-exit, malformed, and unsupported-source cases.

## Risks

- Post-event `/proc` reads can race short-lived processes.
- Cgroup paths are not a universal container naming contract.
- Runtime APIs add permissions, daemon coupling, and inconsistent semantics.
- Broad context reads may add significant CPU or I/O overhead.
- Event-time cgroup IDs may require a reliable userspace correlation index.

## Alternatives Considered

- Cgroup polling only: broad and simple, but may miss short-lived transitions.
- Runtime API only: rich Docker metadata, but not generic and operationally coupled.
- eBPF only: strong event-time attribution, but more kernel/toolchain complexity.
- Namespace identity only: useful grouping signal, but insufficient for workload ownership.
- systemd/D-Bus only: useful for services/scopes, not arbitrary cgroup workloads.

## Open Questions

- Preferred identity tuple and lifecycle semantics.
- Minimum viable notification/snapshot cadence.
- Whether cgroup inode, path, namespace tuple, or eBPF cgroup ID should anchor joins.
- Which optional adapters merit continued support after comparison.
