---
title: "Future: Privileged eBPF Helper and Unprivileged .NET Boundary"
type: concept
confidence: speculative
grounded_by:
  - ../Lintap/packaging/lintap-rpm/lintap.service
  - ../Lintap/packaging/lintap-deb/lintap.service
  - ../Lintap/packaging/PACKAGING_REVIEW.md
  - ../Lintap/README.md
policy: agent-editable
last_validated: 2026-10-12
repo_scope: cross-repo
implementation_area: packaging
event_domain: cross-domain
audience: mixed
status: stub
source_paths: ../Lintap/packaging/lintap-rpm/lintap.service; ../Lintap/packaging/lintap-deb/lintap.service; ../Lintap/packaging/PACKAGING_REVIEW.md; ../Lintap/README.md
tags: [future-work, lintap, ebpf, least-privilege, systemd, packaging, security]
---

# Future: Privileged eBPF Helper and Unprivileged .NET Boundary

## Current State

The packaged Lintap service currently starts the complete .NET sensor as
`root`, with `NoNewPrivileges=false` and unlimited locked memory. This keeps
initial eBPF validation permissive, but also gives the .NET runtime, event
processing, serialization, ETL, and optional helper components the privileges
needed by the eBPF loader.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/lintap.service; ../Lintap/packaging/lintap-deb/lintap.service -->

The packaging review explicitly identifies this service hardening as work to
revisit after the exact eBPF requirements are known. Lintap's newer TeleTap
implementation is maintained in the Wintap repository, while this repository
documents supporting Linux packaging and deployment behavior.
<!-- GROUND_TRUTH: ../Lintap/packaging/PACKAGING_REVIEW.md §4; ../Lintap/README.md §Lintap now has 2 parallel implementations -->

## Proposed Boundary

Use two independently managed services:

```text
systemd
  |
  +-- lintap-ebpf.service       root or narrowly capability-enabled
  |       |
  |       +-- loads and attaches eBPF programs
  |       +-- owns BPF maps and ring buffers
  |       +-- validates and forwards telemetry records
  |       |
  |       +---- protected AF_UNIX socket ----+
  |                                          |
  +-- lintap.service                 dedicated lintap user
          |
          +-- consumes telemetry
          +-- runs .NET processing and serialization
          +-- writes application output and performs uploads
```

The privileged helper should be deliberately small. It should own the BPF
objects and translate events into a versioned, bounded record protocol. The
.NET service should not submit arbitrary BPF bytecode, choose arbitrary kernel
objects, request filesystem paths, or otherwise turn the helper into a
general-purpose privileged proxy.
<!-- SYNTHESIS: proposed boundary based on the current all-in-one root service in ../Lintap/packaging and the least-privilege deployment goal -->

The strongest initial IPC candidate is a Unix-domain socket at a protected
runtime path such as `/run/lintap/ebpf.sock`:

- Create a dedicated `lintap` service user and group.
- Make the socket `root:lintap` with mode `0660`.
- Verify the peer credentials on connection.
- Use explicit message types, maximum record sizes, and bounded queues.
- Prefer a telemetry-streaming protocol; keep control messages minimal and
  allowlisted.
- Define helper restart, consumer reconnect, and backpressure behavior.

The helper should retain ownership of BPF maps and ring buffers. Loading a
program as root does not by itself guarantee that an unprivileged process can
later read every map or consume every ring buffer safely.
<!-- SPECULATIVE: proposed IPC and object-ownership design — requires implementation and kernel-version validation -->

## Capability and systemd Direction

On newer kernels, the helper may be able to use a narrower capability set than
full root, commonly including `CAP_BPF`, `CAP_PERFMON`, and
`CAP_SYS_RESOURCE`. Some attach types, older kernels, or RHEL 8 compatibility
paths may additionally require `CAP_NET_ADMIN` or `CAP_SYS_ADMIN`.

The capability set must be determined empirically for the supported kernel
matrix. `CAP_SYS_ADMIN` should be treated as a compatibility fallback rather
than assumed to be the final design. `LimitMEMLOCK` and the actual BPF map
memory requirements also need to be measured before replacing the current
unlimited setting.
<!-- SYNTHESIS: capability direction; exact requirements are intentionally unverified and kernel/attach-type dependent -->

The unprivileged .NET service should be hardened independently, for example:

```ini
[Service]
User=lintap
Group=lintap
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictAddressFamilies=AF_UNIX
ReadWritePaths=/var/log/lintap /run/lintap
```

These settings are a starting point, not a drop-in unit. Network address
families must be expanded if the application uploads data, and .NET runtime
features such as JIT behavior must be tested before applying stronger options
such as `MemoryDenyWriteExecute`.
<!-- SPECULATIVE: systemd hardening profile — validate against actual .NET, upload, and runtime behavior -->

The helper can generally use a tighter filesystem and network profile because
it should need only its tracer objects, kernel interfaces, and the runtime
socket. It may require carefully tested access to `/sys`, `/proc`, kernel BTF,
and `/sys/fs/bpf`.

## Migration Sequence

1. Isolate the code that loads objects, attaches programs, consumes maps or
   ring buffers, and decodes records.
2. Define a versioned event protocol and a readiness/error contract.
3. Move that code behind the `lintap-ebpf` process boundary.
4. Change the .NET application to consume the protocol instead of invoking
   libbpf directly.
5. Add the service user, runtime directory, socket ownership, and package
   lifecycle handling to both Debian and RPM packaging.
6. Split the current unit into `lintap-ebpf.service` and an unprivileged
   `lintap.service`, with readiness ordering or socket activation.
7. Add reconnect, malformed-message, oversized-message, queue-bound, and
   helper-restart tests.
8. Test the minimum capability set and systemd sandbox on each supported
   Ubuntu and RHEL kernel target.
9. Promote measured requirements into the canonical packaging page and units.

## Related Privileged Collectors

The separate `lintap-pidstat.service` also currently runs as root for broad
`/proc` visibility. It should be evaluated independently rather than
automatically placed in the eBPF helper. A non-root implementation may be
possible on some systems, but visibility of other users' processes and fields
such as command lines must be tested before changing its service identity.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/lintap-pidstat.service; ../Lintap/packaging/lintap-deb/lintap-pidstat.service; ../Lintap/packaging/lintap-rpm/README.md §Runtime Layout -->

## Open Questions

- Which exact eBPF operations and attach types are required by each supported
  kernel and sensor?
- Can the helper run with `CAP_BPF`, `CAP_PERFMON`, and
  `CAP_SYS_RESOURCE`, or is `CAP_SYS_ADMIN` needed for compatibility?
- Should the helper be native code, a minimal .NET process, or another runtime?
- What event representation gives the .NET consumer enough data without
  exposing raw privileged objects?
- What are the loss, backpressure, and restart semantics for the IPC stream?
- Which `/proc`, `/sys`, and `/sys/fs/bpf` accesses are genuinely required?
- Can pidstat run under `lintap` on every supported deployment?

## Security Position

Dropping privileges inside the existing process after eBPF initialization is a
possible intermediate experiment, but it is weaker than a process boundary:
the loader and application remain in the same address space, inherited file
descriptors and retained capabilities are easy to get wrong, and future code
changes can expand the privileged phase. The two-service design is the
preferred future direction if the operational and performance cost of IPC is
acceptable.
<!-- SYNTHESIS: recommendation based on the current single root service and the proposed least-privilege boundary -->
