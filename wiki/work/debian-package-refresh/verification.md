---
title: "Verification: Debian Package Refresh"
type: concept
confidence: medium
grounded_by: []
policy: agent-editable
last_validated: 2026-10-03
repo_scope: Lintap
implementation_area: packaging
event_domain: none
audience: mixed
status: draft
source_paths: wiki/work/debian-package-refresh/verification.md
tags: [feature-work, lintap-packaging, debian, verification]
---

# Verification: Debian Package Refresh

Arm64 implementation and native smoke evidence are recorded below. The amd64
build and smoke remain outstanding.

## Test Commands

### Arm64 build

Host: `lintap-dev`, Ubuntu 24.04, `aarch64`, kernel `6.8.0-142-generic`.

```sh
/home/ubuntu/git/Lintap/packaging/lintap-deb/build-deb.sh \
  --version 0.1.0 --revision 6
```

Result: PASS. Fresh main publish and separate self-contained MCP publish
completed. Native BTF was available, so tracepoint and CO-RE objects built;
`selinux_tracer.bpf.o` was staged opportunistically.

```sh
dpkg-deb --info /home/ubuntu/git/artifacts/lintap-deb/lintap_0.1.0-6_arm64.deb
dpkg-deb --contents /home/ubuntu/git/artifacts/lintap-deb/lintap_0.1.0-6_arm64.deb
sha256sum /home/ubuntu/git/artifacts/lintap-deb/lintap_0.1.0-6_arm64.deb
```

SHA-256: `66d98e94b92a2e636be5d269e62ed11f2306012b2d9119453e3c2ebda672c833`.
The final default-MCP candidate after the stale-output fix was revision `10`,
SHA-256 `585997054f411eca23f3e5d60e22489432750b7bdce1c6d8f4b77166bdfa9091`.

### Skip-MCP path

```sh
/home/ubuntu/git/Lintap/packaging/lintap-deb/build-deb.sh \
  --version 0.1.0 --revision 9 --skip-mcp
dpkg-deb --contents /home/ubuntu/git/artifacts/lintap-deb/lintap_0.1.0-9_arm64.deb
```

Result: PASS. The package built with no `/usr/lib/lintap/mcp/` content after
stale MCP work-root cleanup was added. SHA-256:
`0ab7ad3826b3e0f1384a3441f5106e48d7d629e5de7a07e62dd06b486aaa29ad`.

### Install, upgrade, remove, purge

```sh
sudo apt-get install -y /home/ubuntu/git/artifacts/lintap-deb/lintap_0.1.0-6_arm64.deb
sudo systemctl start lintap.service
sudo apt-get install -y /home/ubuntu/git/artifacts/lintap-deb/lintap_0.1.0-7_arm64.deb
sudo touch /var/log/lintap/package-refresh-marker
sudo apt-get remove -y lintap
sudo apt-get purge -y lintap
```

Results: initial install enabled but did not start the service; manual start
was active. The revision `6` to `7` upgrade left the service enabled and
active. Remove preserved `/var/log/lintap` data and `/etc/lintap/lintap.env`;
purge removed `/etc/lintap` while preserving the data marker.

## Manual Checks

### Service and output

- `systemctl is-enabled lintap.service`: `enabled`.
- `systemctl is-active lintap.service`: `active` after manual start and after
  the revision `6` to `7` upgrade.
- `/var/log/lintap/parquet/host/host-134355177359822085.parquet` and
  `/var/log/lintap/parquet/macip/macip-134355177362448799.parquet` were created.
- Package contents included all six tracepoint objects, four CO-RE objects,
  and `selinux_tracer.bpf.o`.
- `ldd` passed for required staged binaries and libraries. The optional .NET
  `libcoreclrtraceptprovider.so` reports `liblttng-ust.so.0 => not found` on
  Ubuntu 24.04, which provides the ABI-transitioned `.so.1`; the report is
  retained as a warning rather than treated as a required runtime dependency.

## Results

Arm64 build, package structure, fresh publish, MCP isolation, install/start,
upgrade, remove, and purge checks passed on 2026-10-03. The service emitted
libbpf tracepoint lookup errors for `syscalls/sys_enter_open`,
`syscalls/sys_exit_open`, and `syscalls/sys_enter_unlink` on this validation
kernel, but remained active and produced parquet output. This is recorded as a
host/kernel sensor-attach caveat, not a package installation failure.

## Known Gaps

- Native arm64 host validation is complete; amd64 validation remains.
- `--no-restore` cannot be used from a clean native work root until assets are
  restored into that work root; fresh publish with restore succeeds.
- Ubuntu 24.04's .NET optional diagnostic provider requests the older
  `liblttng-ust.so.0` soname. The package carries ABI alternatives for Ubuntu
  releases, but this optional provider remains unresolved on the validation
  host.

## Follow-Ups

- Run dpr-05 on a native amd64 Ubuntu host.
- Recheck the optional .NET diagnostic-provider dependency on the amd64 host.
