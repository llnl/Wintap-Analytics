---
title: "Feature References: Support for Docker Contexts on Linux"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../wintap/wintap/platform/linux/sensor/ebpf/ProcReader.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs
  - ../wintap/wintap/platform/linux/sensor/ebpf/NetworkSensor.cs
  - https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
  - https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md
policy: agent-editable
last_validated: 2026-09-01
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/support-docker-contexts-linux/references.md
tags: [feature-work, references, linux, cgroups, containers]
---

# Feature References: Support for Docker Contexts on Linux

## Live Repo Sources

- `../Lintap/pidstat-collector.py` — direct `/proc` sampling, cgroup parsing, PID namespace identity, and metadata caching.
- `../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs` — process event production and event-time fields.
- `../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs` and `ExitSensor.cs` — process lifetime boundaries.
- `../wintap/wintap/platform/linux/sensor/ebpf/ProcReader.cs` — existing Linux `/proc` context reads used by file/network paths.
- `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs` and `NetworkSensor.cs` — file/network producer integration points.
- `../wintap/wintap/platform/linux/infrastructure/LinuxSubscriptionManager.cs` — Linux sensor enablement and lifecycle.

## External Sources

- Linux kernel, [Control Group v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html): cgroup hierarchy, `cgroup.procs`, `cgroup.events`, population notifications, and controller metadata.
- Open Container Initiative, [Linux container configuration](https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md): namespaces, `cgroupsPath`, and runtime configuration boundaries.
- `proc(5)`, `namespaces(7)`, and `cgroups(7)` — candidate kernel observation interfaces for implementation and test fixtures.
- Docker Engine, Podman/libpod, containerd/CRI, and systemd APIs — optional runtime-specific enrichment candidates to evaluate, not assumed dependencies.

## Related Wiki Pages

- [[wiki/work/improve-pidstat-collector/brief]]
- [[wiki/work/improve-pidstat-collector/design]]
- [[wiki/repo/lintap-supporting-repo]]
- [[wiki/component/wintap-api-shared-data-model]]
- [[wiki/event_type/process-events]]
- [[wiki/event_type/file-events]]
- [[wiki/event_type/network-events]]
- [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]]
- [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]]

## Libraries And APIs

- Linux `/proc`, cgroupfs, namespace symlinks, and filesystem notification APIs.
- libbpf/eBPF helpers for event-time cgroup identity, subject to the existing sensor toolchain.
- Optional systemd D-Bus, Docker Engine, Podman, containerd/CRI, and OCI runtime state interfaces.

## Notes

The neutral evidence layer should preserve cgroup path, cgroup version/layout,
namespace identities, process membership, observation source, and parse errors.
Runtime names and IDs should be compared as enrichments and must not silently
replace kernel-derived identity.
