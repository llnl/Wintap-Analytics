---
title: "Dev Handoff: Support for Docker Contexts on Linux"
type: concept
confidence: medium
grounded_by:
  - wiki/work/support-docker-contexts-linux/brief.md
  - wiki/work/support-docker-contexts-linux/design.md
  - wiki/work/support-docker-contexts-linux/implementation_plan.md
policy: agent-editable
last_validated: 2026-09-01
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/support-docker-contexts-linux/dev_handoff.md
tags: [feature-work, handoff, linux, cgroups, containers]
---

# Dev Handoff: Support for Docker Contexts on Linux

## Copy/Paste Prompt

    Switch to code-development mode for Support for Docker Contexts on Linux.

    Read AGENTS.md and these wiki files before editing:
    - wiki/work/support-docker-contexts-linux/brief.md
    - wiki/work/support-docker-contexts-linux/references.md
    - wiki/work/support-docker-contexts-linux/design.md
    - wiki/work/support-docker-contexts-linux/spike.md
    - wiki/work/support-docker-contexts-linux/implementation_plan.md

    Build only the research prototype. Do not freeze or silently change the stable WintapAPI/DBT schema. Compare cgroup filesystem, namespace, eBPF event-time, shared-resolver, and optional runtime/systemd approaches. Preserve raw observations and failures. Ask for explicit sibling-repo authorization before modifying ../wintap or ../Lintap.

## Handoff Summary

The goal is evidence about Linux context identity and process membership across
host, systemd, Docker, and later v1/hybrid/Podman workloads, with attribution
beside process, file, network, and pidstat telemetry.

## Primary Sources For The Dev Agent

- `../Lintap/pidstat-collector.py`
- `../wintap/wintap/platform/linux/sensor/ebpf/ProcReader.cs`
- `../wintap/wintap/platform/linux/sensor/ebpf/{ExecveSensor,FileOpsSensor,NetworkSensor}.cs`
- Linux cgroup v2 documentation and OCI Linux runtime specification listed in `references.md`.

## Recommended First Implementation Slice

Define diagnostic observations and implement the phase-1 cgroup v2 baseline:
raw cgroup membership, namespace identity, cgroup membership/process list,
source/provenance, lifecycle state, and explicit errors.

## Non-Goals For This Slice

- Stable WintapAPI/DBT schema.
- Kubernetes/containerd support.
- Required Docker daemon or runtime API.
- Image, label, mount, or resource metadata unless needed by evidence.

## Testing Expectations

Use reproducible host/systemd/Docker fixtures, test PID reuse and short-lived
processes, compare event families, and measure overhead and loss.

## Closeout Instructions

- Update `wiki/work/support-docker-contexts-linux/verification.md` with commands and results.
- Update the implementation checklist.
- Append a concise entry to `wiki/log.md`.
- Promote durable findings into canonical wiki pages once behavior stabilizes.
