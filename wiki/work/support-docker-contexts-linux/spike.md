---
title: "Feature Spike: Support for Docker Contexts on Linux"
type: concept
confidence: speculative
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/ProcReader.cs
  - https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
policy: agent-editable
last_validated: 2026-09-01
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: stub
source_paths: wiki/work/support-docker-contexts-linux/spike.md
tags: [feature-work, spike, linux, cgroups, containers]
---

# Feature Spike: Support for Docker Contexts on Linux

## Question

Which Linux context acquisition and enrichment strategy provides the most valid
cross-event attribution for arbitrary cgroup workloads at acceptable overhead?

## Hypothesis

Cgroup path plus namespace identity will be the most portable evidence layer.
Event-time eBPF cgroup identity may improve short-lived process fidelity, while
runtime and systemd sources will provide useful but optional human-readable
enrichment.

## Experiment

- Run the phase-1 host/systemd/Docker matrix on cgroup v2.
- Compare direct cgroup snapshotting, notification-driven discovery, producer-local `/proc` reads, a shared resolver, and eBPF event-time identity.
- Record process membership, context lifecycle, PID reuse, short-lived processes, and cross-event joins.
- Add phase-2 cgroup v1/hybrid and Podman runs when available.
- Measure CPU, memory, read volume, event latency, and drops.

## Prototype Location

To be selected during implementation planning. Prefer a bounded validation
prototype under this repository or an explicitly authorized sibling-repo
diagnostic location; do not silently alter stable telemetry contracts.

## Results

Not started.

## Recommendation

Not started. The recommendation must identify the preferred evidence layer,
integration boundary, inventory semantics, and next schema slice.

## Follow-Ups

- Add Kubernetes/containerd only after phase-1/phase-2 results establish the resolver model.
- Promote durable findings into canonical component/event/schema pages.
