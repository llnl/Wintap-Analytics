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
status: reviewed
source_paths: wiki/work/debian-package-refresh/verification.md
tags: [feature-work, lintap-packaging, debian, verification]
---

# Verification: Debian Package Refresh

Arm64 and native amd64 implementation and smoke evidence are recorded below.
An amd64 cross-build is also retained for comparison.

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

### Amd64 cross-build

Host: `lintap-dev`, Ubuntu 24.04, `aarch64`; target: `amd64` / `linux-x64`.

```sh
/home/ubuntu/git/Lintap/packaging/lintap-deb/build-deb.sh \
  --version 0.1.0 --revision 11 \
  --arch amd64 --runtime linux-x64 --host-arch aarch64
dpkg-deb --info /home/ubuntu/git/artifacts/lintap-deb/lintap_0.1.0-11_amd64.deb
```

Result: PASS for cross-build and structural validation. The package reports
`Architecture: amd64`; `file` reports x86-64 `Lintap` and MCP executables; all
six tracepoint objects are present and no CO-RE objects are required. SHA-256:
`c4bd44e47a94f12498e95aaa2bac7430750d03303e39e9d842232d025179bcda`.

### Native amd64 build and smoke

Host: UTM VM `192.168.252.5`, Debian 12, `x86_64`, kernel
`6.1.0-50-amd64`. Debian's multiarch headers required
`CPATH=/usr/include/x86_64-linux-gnu`; this was an environment-only build
setting and no source files were changed.

```sh
env PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  CPATH=/usr/include/x86_64-linux-gnu \
  /home/eyeon/git/Lintap/packaging/lintap-deb/build-deb.sh \
  --version 0.1.0 --revision 12 --host-arch x86_64
sudo apt-get install -y /home/eyeon/git/artifacts/lintap-deb/lintap_0.1.0-12_amd64.deb
sudo systemctl start lintap.service
sudo apt-get install -y /home/eyeon/git/artifacts/lintap-deb/lintap_0.1.0-13_amd64.deb
sudo touch /var/log/lintap/package-refresh-marker
sudo apt-get remove -y lintap
sudo apt-get purge -y lintap
```

Results: PASS. Revision `12` installed enabled and initially inactive, then
started active. Revision `13` upgraded in place with the service still
enabled and active. The service produced 105 readable parquet rows across the
host and macip outputs. Remove preserved `/var/log/lintap` and the conffile;
purge removed `/etc/lintap` while preserving the data marker. Native revision
`12` SHA-256: `dccc2f923b3b5f0a9fe300dc67c86b15c965d1bd608cc96534401e4ad12974f9`.
Native revision `13` SHA-256:
`497d5ee0aa7720118b8c84db0c808661b5b693237bdd0bc38bcacb0d4a199df9`.

### Release artifact rebuild

Fresh Debian artifacts were rebuilt on `lintap-dev` with application version
`0.1.0` and revision `14`:

- `artifacts/lintap-deb/lintap_0.1.0-14_arm64.deb` — SHA-256
  `c26c48290997a4120a18b227913722b22d288386b8abafd23c02df915325e961`
- `artifacts/lintap-deb/lintap_0.1.0-14_amd64.deb` — SHA-256
  `ea2f2659736a1f81d97ee2780315d8033ae4dcdeb7ae835f0c0bc382da8eaa2f`

The existing RPM artifact is stale and was not replaced:
`artifacts/lintap-rpm/x86_64/lintap-0.1.0-3.el8.x86_64.rpm`, built 2026-06-18,
SHA-256 `38bfecbad374b2ecc8dc0f9b85cfd50eaaa3c7936aca61b18055ef0b0dd1657f`.
A fresh RPM build stopped during staged-content validation because the RPM
builder still requires the obsolete single-tier `file_ops_tracer.bpf.o`
contract. Refreshing that builder is outside this feature's authorization.

### Live sensor smoke tests on lintap-dev

The installed arm64 sensor was running against `/var/log/lintap` on
`lintap-dev`.

```sh
sudo python3 /home/ubuntu/git/wintap/devtools/process_capture_smoke_test.py \
  --data-root /var/log/lintap --timeout 180
sudo python3 /home/ubuntu/git/wintap/devtools/file_capture_smoke_test.py \
  --data-root /var/log/lintap --timeout 180
sudo python3 /home/ubuntu/git/wintap/devtools/network_capture_smoke_test.py \
  --data-root /var/log/lintap --timeout 180
```

Results: all three passed on 2026-10-03.

- Process creation/tree: PASS. All three variants (`fork_exec`, `posix_spawn`,
  `execveat_fexecve`) produced process records with valid expected parent/child
  linkage and parent hashes. The `posix_spawn` case required additional parquet
  flush wait time before passing.
- File activity: PASS. Captured five rows across one generated path with
  `open`, `read`, `write`, `close`, and `delete` activities. The test waited
  for parquet visibility before passing.
- Network activity: PASS. Three rounds of HTTP/HTTPS traffic to four endpoints
  and three rounds of UDP probes to `8.8.8.8:53` and `1.1.1.1:53` completed.
  Recent parquet rows included TCP port 443 and UDP port 53 records. Exact
  endpoint-IP matching was not required by the test.

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
- Native amd64 validation is complete on the UTM VM. The Multipass cross-build
  remains useful for validating tracepoint-only cross-build behavior.
- `--no-restore` cannot be used from a clean native work root until assets are
  restored into that work root; fresh publish with restore succeeds.
- Ubuntu 24.04's .NET optional diagnostic provider requests the older
  `liblttng-ust.so.0` soname. The package carries ABI alternatives for Ubuntu
  releases, but this optional provider remains unresolved on the validation
  host.

## Follow-Ups

- Recheck the optional .NET diagnostic-provider dependency on future Ubuntu
  amd64 hosts; Debian 12 resolved it through `liblttng-ust1`.
