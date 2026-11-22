---
title: "To-Do: Qualify Lintap RPM Installation on Amazon Linux 2023"
type: diagnostic
confidence: low
grounded_by:
  - ../Lintap/packaging/README.md
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
policy: agent-editable
last_validated: 2026-11-16
repo_scope: cross-repo
implementation_area: packaging
event_domain: none
audience: mixed
status: draft
source_paths: ../Lintap/packaging/README.md; ../Lintap/packaging/lintap-rpm/build-rpm.sh; ../Lintap/packaging/lintap-rpm
tags: [todo, priority, linux, packaging, rpm, amazon-linux, al2023, lintap]
---

# To-Do: Qualify Lintap RPM Installation on Amazon Linux 2023

**Priority:** P2 — Medium (provisional; blocks deployment on the reported target
platform but the failure mode and affected package revisions are not yet known).
**State:** Open — intake finding; no packaging or source change is authorized by
this TODO.
**Likely next step:** Reproduce the installation failure on a disposable AWS
Amazon Linux 2023 host, capture sanitized package-manager and transaction errors,
and compare the RPM's dependencies, scripts, native libraries, service metadata,
and bundled runtime with the host before choosing a packaging or build-target fix.

## Finding

The current Lintap RPM reportedly does not install on AWS Amazon Linux 2023.
The exact RPM revision, host architecture, installation command, dependency
failure, and transaction output have not yet been captured or independently
verified.
<!-- HUMAN-REPORTED: current Lintap RPM installation failure on AWS Amazon Linux 2023; reproduction details are pending -->

The documented RPM contract currently targets a native `x86_64` RHEL 8-compatible
build, with RHEL 9 qualification still pending. That documented target does not
establish Amazon Linux 2023 compatibility, even though both distributions use
RPM tooling. The builder also requires a native BTF-enabled Linux build host and
the package may depend on distribution-specific native libraries, service
conventions, or maintainer-script behavior.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §Supported targets; §RHEL 9 prerequisites and operator-assisted qualification; ../Lintap/packaging/lintap-rpm/build-rpm.sh §required commands and defaults -->

## Investigation and verification

1. Record sanitized AL2023 host release, architecture, kernel, glibc, enabled
   repositories, RPM/DNF versions, installed .NET/native runtime libraries, and
   relevant security policy state.
2. Identify the failing RPM artifact and revision; inspect its metadata, payload,
   dependencies, maintainer scripts, service unit, runtimeconfig, native library
   requirements, and packaged eBPF objects before retrying installation.
3. Reproduce the failure on a disposable AL2023 host and distinguish dependency
   resolution, transaction/scriptlet, filesystem/permission, service-manager,
   runtime ABI, and kernel/BPF compatibility failures.
4. Compare native AL2023 build output with the existing RHEL-compatible RPM. If a
   target-specific build is required, define its release identity, prerequisites,
   architecture scope, and whether it is a separate compatibility target rather
   than silently broadening the existing RHEL claim.
5. Test clean installation, upgrade, removal/rollback behavior, service enablement
   and startup, and the minimum approved sensor smoke path. Preserve existing
   collectors and telemetry data on the disposable test host and do not perform a
   field deployment as part of this intake.
6. Add repeatable package inspection and AL2023 installation evidence to the
   canonical packaging guide only after the target and acceptance boundary are
   explicitly confirmed.

## Completion criteria

- The failing artifact and reproducible AL2023 error are documented without
  credentials, private repository URLs, or host-identifying values.
- The failure is classified as a package dependency, script, runtime/native ABI,
  service, kernel/BPF, or unsupported-target issue.
- A compatible RPM/build path is either implemented and qualified, or the package
  is explicitly documented as unsupported on AL2023 with a clear alternative.
- Installation and upgrade evidence covers the selected architecture and does
  not claim broader Amazon Linux or RHEL compatibility than was tested.

## Disposition

This is a cross-repo packaging and deployment intake item, not authorization to
change `../Lintap`, `../wintap`, package artifacts, repositories, or an AWS host.
Promote it to a feature-work folder after the artifact, failure mode, target
architecture, and desired support boundary are established.
