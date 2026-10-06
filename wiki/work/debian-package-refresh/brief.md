---
title: "Feature Brief: Debian Package Refresh"
type: concept
confidence: high
grounded_by:
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Lintap/packaging/lintap-rpm/lintap.env
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile
policy: agent-editable
last_validated: 2026-10-03
repo_scope: Lintap
implementation_area: packaging
event_domain: none
audience: mixed
status: draft
source_paths: wiki/work/debian-package-refresh/brief.md
tags: [feature-work, lintap-packaging, debian, ubuntu, systemd, ebpf]
---

# Feature Brief: Debian Package Refresh

## Problem

`../Lintap/packaging/lintap-deb/` was the original Lintap packaging effort
(arm64 Ubuntu smoke test, June 2026) and the template the RPM builder was
derived from, but it has drifted behind the RPM builder that the RHEL 8 field
deployments (lintap 0.3.4 on spk16) hardened:

1. Its expected-tracer validation list predates the two-tier eBPF build
   (`TRACEPOINT_OBJS` always built; `CORE_OBJS` only with BTF), so cross-builds
   fail validation and native builds validate the wrong contract.
   <!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile §OBJS -->
2. Its `lintap.env` lacks the field-validated configuration block (sensor
   enable flags, explicit ETL/sensor enables, runtime MCP/DuckDB-UI disables,
   CloneSensor opt-out) carried by the RPM env.
   <!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/lintap.env -->
3. It lacks the RPM builder's MCP publish isolation (`EnableMcpServer=false`
   plus a separate self-contained MCP publish and `--skip-mcp`), its
   NFS/FUSE-safe native work-root, and its staging hygiene refinements.
4. The 2026-06 packaging review left upgrade-case maintainer scripts and
   binary-verified dependencies unresolved.
   <!-- GROUND_TRUTH: ../Lintap/packaging/PACKAGING_REVIEW.md §Should do -->

A deb built today would not reproduce the field-validated sensor behavior and
would fail its own validation on cross-builds.

## Goals

- Bring `build-deb.sh` to functional parity with `build-rpm.sh` (tier-aware
  tracer validation, MCP publish parity with `--skip-mcp`, native work-root,
  staging hygiene), while keeping its existing amd64+arm64 support.
- Sync `lintap.env` to the RPM 0.3.4 field configuration, with one deliberate
  divergence: keep Snappy parquet compression and `libnironcompress.so`
  (Ubuntu glibc ≥ 2.35 satisfies the lib's GLIBC_2.29 need that RHEL 8 could
  not).
- Package `selinux_tracer.bpf.o` opportunistically when built; never require
  it (the selinux-monitoring feature owns its schedule).
- Verify the `Depends:` line against actual publish-output binaries (`ldd`).
- Handle upgrade/abort maintainer-script cases so in-place upgrades leave the
  service enabled and running.
- Validate on native Ubuntu amd64 and arm64 hosts.

## Non-Goals

- lintian / `changelog.Debian.gz` / `copyright` Debian-policy polish.
- systemd unit hardening changes.
- apt repository hosting or Debian upstreaming.
- Extended (multi-hour) runtime gates — packaging scope only.
- Any `../wintap` sensor code or eBPF Makefile changes.
- Any changes to `../Lintap/packaging/lintap-rpm/`.

## User-Facing Behavior

`Lintap/packaging/lintap-deb/build-deb.sh` produces an installable,
field-configured `lintap_<version>-<rev>_<arch>.deb` for amd64 and arm64 with
the same operational contract as the field RPM: service enabled (not started)
on install, data under `/var/log/lintap`, config at `/etc/lintap/lintap.env`
(conffile), MCP helper staged but runtime-disabled (or omitted via
`--skip-mcp`), data preserved on remove and purge-of-config semantics on purge.

## Acceptance Criteria

Per validated architecture (amd64 and arm64):

1. Package builds cleanly from a fresh `dotnet publish` (no `--publish-dir`).
2. Clean install on a current Ubuntu LTS host; service starts via systemd.
3. Expected tracer tier(s) attach: tracepoint tier always; CO-RE tier on
   native builds with BTF.
4. Parquet output appears under `/var/log/lintap` and is readable.
5. Clean remove preserves `/var/log/lintap` data; purge removes config only.
6. Upgrade in place (install new revision over old) leaves the service
   enabled and running.
7. `Depends:` verified against `ldd` output of the staged binaries.

## Affected Areas

- `../Lintap/packaging/lintap-deb/` only (script, env, units, docs).
- This wiki: feature artifacts, index, log; canonical promotion at closeout
  (likely [[wiki/repo/lintap-supporting-repo]]).

## References

See [[wiki/work/debian-package-refresh/references]].

## Open Questions

- arm64 host identity and access path (resolve at verification time).
- Does the historical NuGet-unreachable limitation still apply on either build
  host? (`--publish-dir` escape hatch exists but release packages should come
  from fresh publishes.)

## Test Plan

- Build matrix: amd64 native, arm64 native (fresh publish each).
- `dpkg-deb --info/--contents` structural checks (script-internal assertions
  cover required paths).
- Install smoke per arch: install → enable state check → start → tracer attach
  check in `Lintap.log` → parquet readability → stop.
- Upgrade smoke: bump revision, install over existing, confirm service still
  enabled/running.
- Remove/purge semantics check.

## Done When

All acceptance criteria pass on both architectures,
[[wiki/work/debian-package-refresh/verification]] records commands and
results, `wiki/log.md` carries the closeout entry, and durable packaging facts
are promoted to canonical pages.
