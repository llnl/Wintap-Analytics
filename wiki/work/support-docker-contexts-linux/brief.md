---
title: "Feature Brief: Support for Docker Contexts on Linux"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
policy: agent-editable
last_validated: 2026-09-01
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/support-docker-contexts-linux/brief.md
tags: [feature-work, linux, cgroups, containers, docker, telemetry, research]
---

# Feature Brief: Support for Docker Contexts on Linux

## Problem

Linux telemetry can identify processes, but context is currently fragmented
across `/proc` sampling and eBPF producer paths. Cgroup membership and namespace
identity are available signals for grouping arbitrary Linux workloads, while
Docker/Podman/runtime metadata may provide human-readable enrichment. The
project needs evidence about which signals remain valid across process lifetime,
PID reuse, cgroup versions, and event families before committing to a schema.

## Goals

- Prototype per-event context enrichment for process, file, network, and pidstat telemetry.
- Prototype a separate context/inventory stream.
- Compare `/proc`, direct cgroup inspection, eBPF event-time identity, shared resolver, namespace, OCI, runtime, systemd, and notification approaches where feasible.
- Support arbitrary Linux cgroup workloads, with Docker identity as best-effort enrichment.
- Preserve raw observations and parse failures for research analysis.
- Establish evidence-based recommendations for a later normalized schema.

## Non-Goals

- Freezing a WintapAPI or DBT schema in the prototype.
- Requiring Docker or a Docker daemon for generic cgroup collection.
- Making Docker naming the authoritative workload identity.
- Supporting Kubernetes/containerd in the initial validation matrix.
- Collecting image, labels, mounts, or resource limits unless the prototype shows they are necessary and reliable.

## User-Facing Behavior

On a supported Linux host, an operator can run the prototype against host
processes, systemd scopes/services, and Docker workloads. It emits enriched
observations alongside existing telemetry where integration is practical and
writes diagnostic artifacts containing source observations, resolved context,
membership, timestamps, lifecycle state, and errors.

## Acceptance Criteria

- Mixed phase-1 fixture covers ordinary host processes, systemd scopes/services, and Docker under cgroup v2.
- Phase-2 fixture covers cgroup v1/hybrid and Podman when an environment is available.
- Context identity and process membership are captured with source and confidence/provenance information.
- PID reuse and short-lived process behavior are measured.
- Context discovery, change, emptying, and removal are observed or their limitations are documented.
- Context can be compared beside process, file, network, and pidstat output.
- At least two acquisition approaches are compared on fidelity, loss, latency, complexity, and overhead.
- Raw observations and parse failures are retained.
- A recommendation identifies the preferred integration boundary, inventory semantics, and candidates for a future normalized schema.

## Affected Areas

- `../wintap/wintap/platform/linux/sensor/ebpf/` — process, file, and network event producers.
- `../Lintap/pidstat-collector.py` — existing `/proc`-based process context source.
- Linux cgroup and namespace filesystem observation.
- Optional OCI/runtime/systemd metadata adapters.
- This wiki's validation artifacts and, later, Wintappy/schema consumers if a contract is approved.

## References

See [[wiki/work/support-docker-contexts-linux/references]].

## Open Questions

- Which identity tuple is stable enough for cross-event joins?
- Should inventory be snapshot, lifecycle, or hybrid?
- Can eBPF cgroup IDs be resolved reliably without post-event `/proc` races?
- Which optional runtime metadata sources are worth their dependencies and permissions?

## Test Plan

- Synthetic and live phase-1 workload matrix.
- PID reuse, short-lived process, cgroup migration, and context removal cases.
- cgroup v1/v2/hybrid parser and namespace identity tests.
- Cross-producer comparison for process, file, network, and pidstat events.
- Resource overhead and event-loss measurements.

## Done When

The prototype has reproducible artifacts and a reviewed comparison report that
states what context can be collected, how accurately, at what cost, and what
should become the next schema/design slice.
