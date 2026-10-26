---
title: "RHEL 8 RPM Build Prerequisites"
type: workflow
confidence: high
grounded_by:
  - ../Lintap/packaging/README.md
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Lintap/packaging/dotnet-common.sh
  - ../wintap/global.json
  - ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile
policy: agent-editable
last_validated: 2026-10-26
repo_scope: Lintap
implementation_area: packaging
event_domain: none
audience: developer
status: reviewed
source_paths: ../Lintap/packaging/README.md; ../Lintap/packaging/lintap-rpm/build-rpm.sh; ../wintap/global.json
tags: [Lintap, RHEL8, RPM, packaging, build-prerequisites]
---

# RHEL 8 RPM Build Prerequisites

Use this checklist to prepare a **native RHEL 8 x86_64** host to build the
Lintap RPM from the sibling `Lintap/` and `wintap/` checkouts. It covers build
tools only; installing or starting the resulting sensor is a separate action.

The current RPM builder requires a readable `/sys/kernel/btf/vmlinux` and
validates the CO-RE `file_ops_tracer.bpf.o` payload. Use a native x86_64 host;
do not use the script's cross-build option as a workaround. Historical RHEL 8
notes naming .NET SDK 8 are obsolete: the current project requires SDK
**10.0.402**.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §Supported targets; §Build prerequisites; §Build the RHEL 8 RPM; ../Lintap/packaging/lintap-rpm/build-rpm.sh §require_cmd; §expected_bpf_objects; ../wintap/global.json -->

## 1. Check the host and enabled repositories (read-only)

Run before installing anything. Review the output and confirm the host is
registered and its organization-approved BaseOS/AppStream repositories are
enabled. Do not enable repositories or add a third-party package feed without
the system administrator's approval.

```bash
cat /etc/redhat-release
uname -m
uname -r
dnf repolist --enabled
id
df -h /var/tmp
test -r /sys/kernel/btf/vmlinux && echo 'Readable kernel BTF: yes' || echo 'Readable kernel BTF: NO'
```

Proceed with this RPM workflow only when `uname -m` is `x86_64` and the BTF
check succeeds. Installing `kernel-devel` does **not** create
`/sys/kernel/btf/vmlinux`; if BTF is absent, stop and resolve the kernel/host
qualification separately.

## 2. Install operating-system build tools

After confirming the repository/package plan with the host administrator,
install the tools and headers used by the RPM builder and tracer compilation:

```bash
sudo dnf install -y \
  ca-certificates curl git python3 gcc \
  rpm-build tar gzip make clang llvm bpftool \
  libbpf libbpf-devel elfutils-libelf elfutils-libelf-devel \
  zlib-devel binutils file pkgconf-pkg-config \
  glibc libgcc libstdc++ openssl-libs libicu tzdata krb5-libs
```

RHEL 8 repository composition varies. If DNF cannot find a package, retain the
error and inspect the enabled, approved repositories; do not silently add an
unapproved repository or substitute arbitrary libraries. `kernel-devel` is not
what supplies BTF and is not required by the current tracer Makefile's build
commands; install matching `kernel-devel-$(uname -r)` only if local policy or
another explicitly identified build step requires kernel headers.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §Build prerequisites; ../Lintap/packaging/lintap-rpm/build-rpm.sh §require_cmd; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile §preflight -->

Check the required commands and BTF tooling:

```bash
for cmd in dotnet python3 make rpmbuild tar clang bpftool; do
  command -v "$cmd" || echo "MISSING: $cmd"
done
clang --version
bpftool version
bpftool btf dump file /sys/kernel/btf/vmlinux format c >/dev/null
rpm --version
```

`rpm-build` provides `rpmbuild`. `gcc` is used by the tracer Makefile to
identify the host target triple; `libbpf-devel` supplies the `<bpf/...>`
headers included by the eBPF sources. The RPM builder compiles the tracer
objects; it does not need to install or start the Lintap service.

## 3. Select the exact .NET SDK

The source-of-truth version is in `wintap/global.json`. Check whether the
approved package repositories already provide **10.0.402** before installing a
separate SDK:

```bash
dnf --showduplicates list dotnet-sdk-10.0
command -v dotnet && dotnet --info || true
```

Do not install an arbitrary `dotnet-sdk-10.0` package and assume it is the
required patch. If an approved package installation selects exactly 10.0.402,
use it. Otherwise, with approval for downloading Microsoft's official
installer, install the pinned SDK into a user-local, isolated directory (this
does not replace a system SDK):

```bash
SDK_VERSION=10.0.402
export DOTNET_ROOT="$HOME/.dotnet/wintap-sdk-$SDK_VERSION"
mkdir -p "$DOTNET_ROOT"
curl --fail --location https://dot.net/v1/dotnet-install.sh \
  -o "$DOTNET_ROOT/dotnet-install.sh"
# Inspect/approve the downloaded installer before running it; do not curl | bash.
bash "$DOTNET_ROOT/dotnet-install.sh" \
  --version "$SDK_VERSION" --install-dir "$DOTNET_ROOT" --no-path
export PATH="$DOTNET_ROOT:$PATH"
```

The RPM builder resolves `global.json` and rejects an SDK other than 10.0.402
before cleaning or compiling. Verify selection both at the shell and from the
Wintap checkout:

```bash
test "$(dotnet --version)" = 10.0.402 || { echo 'Wrong SDK selected'; exit 1; }
(cd wintap && test "$(dotnet --version)" = 10.0.402) || { echo 'Wintap selects a different SDK'; exit 1; }
dotnet --info
dotnet --list-runtimes
```

Keep this SDK on `PATH` for the build. Do not confuse the SDK version with the
.NET runtime version bundled into the default self-contained RPM.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §Install/select the pinned SDK; ../Lintap/packaging/dotnet-common.sh; ../wintap/global.json -->

## 4. Confirm the source checkouts and disk location

Use the expected sibling layout, and build from the parent directory on a
native filesystem (the default work area is `/var/tmp`, not a shared mount):

```text
parent/
├── Lintap/
└── wintap/
```

From `parent/`, confirm the project and record source state before the build:

```bash
test -f Lintap/packaging/lintap-rpm/build-rpm.sh
test -f wintap/wintap/Lintap.csproj
git -C Lintap rev-parse HEAD
git -C wintap rev-parse HEAD
git -C Lintap status --short
git -C wintap status --short
```

The script cleans its chosen work/publish directories and runs `make clean` in
the tracer source directory. Review/save any local work first; do not run the
build as root. Once prerequisites pass, use the canonical
[`../Lintap/packaging/README.md`](../../../Lintap/packaging/README.md) for the build
command, RPM inspection, and any separately approved install/smoke test.

## Common incorrect assumptions

- SDK 8.0 is not compatible with the current source baseline; use exact SDK
  10.0.402.
- An RPM named `.el8` does not prove the build ran on RHEL 8 or that BTF was
  available.
- `kernel-devel` does not supply running-kernel BTF.
- Installing build prerequisites does not authorize installing the package,
  starting/stopping a collector, changing security controls, or modifying
  existing telemetry/data.
