---
title: "Linux Setup: VM Host for Process Creation Validation"
type: workflow
confidence: medium
grounded_by:
  - ../wintap/BUILD_AND_TEST.md
  - ../wintap/documentation/Linux Deployment Guide.md
  - ../wintap/wintap/Makefile
  - ../wintap/devtools/README.md
  - ../wintap/devtools/process_capture_smoke_test.py
policy: agent-editable
last_validated: 2026-07-31
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: process
audience: researcher
status: draft
source_paths: ../wintap/BUILD_AND_TEST.md; ../wintap/documentation/Linux Deployment Guide.md; ../wintap/wintap/Makefile; ../wintap/devtools
tags: [wintap, lintap, validation, process-events, ebpf, linux, utm, multipass, dev-environment]
---

# Linux Setup: VM Host for Process Creation Validation

This page describes a practical Linux VM setup for running Lintap process-creation validation from a Mac. It is scoped to research and validation, not production packaging.

## Recommendation

Use **Multipass** if you want the fastest repeatable setup from macOS CLI.

Use **UTM** if you want more control over distro, kernel, VM resources, snapshots, or if Multipass networking/filesystem behavior gets in the way.

For this work, the best operational model is:

```text
Mac host: edit notes, orchestrate runs, keep wiki
Linux VM: build/run sensors, generate workloads, collect raw outputs
Mac -> VM: SSH for commands and file copy
```

Do not try to run eBPF sensors on macOS. Run Lintap, Tetragon, Tracee, and Sysdig inside the Linux VM. Orchestrating from macOS over SSH is fine, but actual sensor processes need Linux kernel access, root/capabilities, BTF/tracepoints, and `/proc` inside the VM.

## UTM vs Multipass

| Option | Pros | Cons | Recommendation |
|---|---|---|---|
| Multipass | Very fast CLI lifecycle, easy SSH, easy rebuild, good for automation | Less explicit control over kernel/distro details, sometimes opaque networking/filesystem behavior | Best first choice for harness development |
| UTM | More control, good snapshots, choose Fedora/Ubuntu, closer to normal VM admin | More manual setup, SSH/networking must be configured | Best for reproducing kernel/distro-specific eBPF behavior |

If both are available, start with Multipass for the first Lintap-only validation harness. Move to UTM once comparing kernel-sensitive behavior, CloneSensor attach failures, or reference sensors.

## VM Requirements

Minimum:

- 4 vCPU
- 8 GB RAM
- 40 GB disk
- Ubuntu 24.04 LTS or Fedora current stable
- SSH access from macOS
- Root/sudo access
- Internet access for packages and GitHub clones

Better for stress testing:

- 8 vCPU
- 16 GB RAM
- 80 GB disk
- Snapshot before installing many sensor stacks

Important kernel capabilities:

- `/sys/kernel/btf/vmlinux` should exist for CO-RE eBPF paths.
- `tracefs`/`debugfs` should be mounted or mountable.
- Root should be able to load eBPF programs.
- Kernel should support BPF ring buffers.

Check inside the VM:

```bash
uname -a
id
test -r /sys/kernel/btf/vmlinux && echo "BTF OK" || echo "BTF MISSING"
mount | grep -E 'tracefs|debugfs' || true
getconf PAGESIZE
```

## Multipass Setup

On the Mac:

```bash
multipass launch 24.04 --name lintap-val --cpus 4 --memory 8G --disk 50G
multipass shell lintap-val
```

Inside the VM:

```bash
sudo apt-get update
sudo apt-get install -y \
  git build-essential clang llvm make pkg-config cmake \
  bpftool linux-tools-common linux-tools-generic \
  python3 python3-venv python3-pip \
  curl wget jq unzip ripgrep \
  duckdb \
  libbpf-dev libelf-dev zlib1g-dev
```

Install .NET 8 SDK. On Ubuntu, prefer Microsoft’s current official instructions if package names change. Typical setup:

```bash
wget https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb
sudo dpkg -i /tmp/packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0 aspnetcore-runtime-8.0
dotnet --info
```

Optional Python package manager for Wintap devtools:

```bash
python3 -m pip install --user uv duckdb
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

From the Mac, discover SSH access:

```bash
multipass info lintap-val
multipass exec lintap-val -- hostname -I
```

You can either use `multipass shell` or SSH. SSH is better once automation starts.

## UTM Setup

Recommended UTM VM choices:

- Ubuntu Server 24.04 for easiest package setup.
- Fedora Server/Cloud if reproducing Fedora-specific CloneSensor behavior.

Suggested UTM settings:

- Architecture: match Mac host defaults, usually ARM64 on Apple Silicon.
- CPU: 4 or 8 cores.
- RAM: 8 GB minimum.
- Disk: 50 GB minimum.
- Network: shared/NAT is fine, bridged is convenient if available.
- Enable SSH during install or install `openssh-server` after boot.

Inside Ubuntu UTM VM, install the same package set as Multipass.

Inside Fedora UTM VM:

```bash
sudo dnf update -y
sudo dnf install -y \
  git make gcc clang llvm cmake pkgconf-pkg-config \
  bpftool kernel-devel kernel-headers \
  python3 python3-pip \
  curl wget jq unzip ripgrep \
  duckdb \
  libbpf-devel elfutils-libelf-devel zlib-devel
```

Install .NET 8 on Fedora:

```bash
sudo dnf install -y dotnet-sdk-8.0 aspnetcore-runtime-8.0
dotnet --info
```

Check SSH from macOS:

```bash
ssh <user>@<vm-ip> uname -a
```

## Source Checkout Layout

Use a consistent layout inside the VM:

```text
~/git/LLNL/wintap
~/git/LLNL/Wintap-Analytics
~/git/LLNL/Lintap
~/git/tetragon
~/git/tracee
~/git/sysdig
```

Clone or copy the repos:

```bash
mkdir -p ~/git/LLNL ~/git
cd ~/git/LLNL
git clone https://github.com/LLNL/Wintap.git wintap
git clone <Wintap-Analytics-remote> Wintap-Analytics
git clone <Lintap-remote> Lintap

cd ~/git
git clone https://github.com/cilium/tetragon.git
git clone https://github.com/aquasecurity/tracee.git
git clone https://github.com/draios/sysdig.git
```

Use the intended Wintap branch:

```bash
cd ~/git/LLNL/wintap
git checkout grantj-ebf-fixes
git rev-parse HEAD
```

Expected branch for this snapshot:

```text
grantj-ebf-fixes
7f932558e5d3f83ec77978f71b8a5588648ecd04
```

## Build Lintap eBPF and .NET

Inside the VM:

```bash
cd ~/git/LLNL/wintap/wintap
make build_ebpf
make build_dotnet
```

The Wintap Makefile builds eBPF tracers from `platform/linux/sensor/ebpf/tracers` and then builds `Lintap.csproj`.
<!-- GROUND_TRUTH: ../wintap/wintap/Makefile §build_ebpf -->

The eBPF tracer Makefile builds CO-RE objects when BTF is available and tracepoint fallback objects otherwise.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile §CORE_OBJS -->

## Lintap Smoke Test Run

Start with process-only direct Parquet because it is the shortest loop for validation harness development.

```bash
cd ~/git/LLNL/wintap
sudo python3 devtools/process_capture_smoke_test.py \
  --start-lintap \
  --lintap-dll ~/git/LLNL/wintap/wintap/bin/Debug/net8.0/Lintap.dll \
  --timeout 240 \
  --poll-interval 5
```

The current smoke test starts Lintap with a temporary JSON config and only the exec process sensor enabled for that test.
<!-- GROUND_TRUTH: ../wintap/devtools/process_capture_smoke_test.py §start_lintap_direct_parquet -->

Also test rundown-only behavior:

```bash
cd ~/git/LLNL/wintap
dotnet run --project diagnostics/process-smoke-test/ProcessSmokeTest.csproj -- \
  --lintap-dll ~/git/LLNL/wintap/wintap/bin/Debug/net8.0/Lintap.dll
```

The diagnostic creates a pre-existing bash/sleep tree before Lintap starts so `ProcessRundownSensor` can capture it.
<!-- GROUND_TRUTH: ../wintap/diagnostics/process-smoke-test/Program.cs §StartLongLivedProcessTree -->

## Suggested First Validation Harness Run

Before running all reference sensors, implement and test the sensor-neutral workload generator inside the VM:

```bash
cd ~/git/LLNL/wintap
python3 devtools/validation/workloads/process_workload.py \
  --run-dir /tmp/validation-runs/manual-process-001 \
  --profile process-baseline-v1
```

Expected artifacts:

```text
/tmp/validation-runs/manual-process-001/
  manifest.json
  workload-stdout.log
  workload-stderr.log
```

Then run Lintap separately, normalize its output, and evaluate against the manifest. Keep each step separate to avoid making the workload generator Lintap-specific.

## Running From Mac vs Inside VM

Preferred split:

- Run sensor commands inside the VM.
- Run workload generator inside the VM.
- Run normalization/evaluation either inside the VM or from Mac after copying artifacts.
- Use Mac SSH only for orchestration and copying results.

Why:

- Workload PIDs only make sense inside the VM where sensors run.
- `/proc` and kernel tracepoints only exist in the VM.
- Localhost network tests should stay inside the VM to avoid host/guest NAT ambiguity.
- Mac orchestration is convenient but should not be part of the measured workload path.

Good SSH pattern from Mac:

```bash
ssh vm 'cd ~/git/LLNL/wintap && git status --short && uname -a'
ssh vm 'cd ~/git/LLNL/wintap/wintap && sudo make run-env'
rsync -a vm:/tmp/validation-runs/ ./validation-runs-from-vm/
```

## Reference Sensor Setup Later

Do not start with all reference sensors. Add one at a time after the manifest/evaluator are stable.

Suggested order:

1. Lintap direct Parquet.
2. Tetragon JSON output or gRPC export.
3. Tracee JSON output.
4. Sysdig raw event/chisel/JSON output.

For each reference sensor, first run a low-load simple exec/fork baseline before burst tests.

## Common Problems To Expect

| Problem | Likely Cause | First Check |
|---|---|---|
| eBPF object fails to build | missing clang/bpftool/libbpf/BTF | `make -C wintap/platform/linux/sensor/ebpf/tracers all` |
| eBPF attach fails | kernel permission/capability/tracepoint issue | run as root; check logs and `dmesg` |
| no Parquet output | config/data root/flush interval | check `WINTAP_CONFIG_PATH`, `DataRoot`, `DirectParquetFlushSeconds` |
| missing short-lived rows | expected timing race or ring loss | increase repetitions; inspect loss counters |
| parent hash missing | parent exited before `/proc`, missing eBPF parent path, resolver disabled | check breadcrumbs and process arguments |
| public network test flaky | DNS/CDN/proxy/NAT | prefer local TCP/UDP server workload |

## Minimum Success Criteria For VM Setup

The Linux VM is ready for harness development when all are true:

- `dotnet --info` works.
- `clang --version` works.
- `bpftool version` works.
- `/sys/kernel/btf/vmlinux` exists or tracepoint fallback build is understood.
- `make build_ebpf` succeeds in `~/git/LLNL/wintap/wintap`.
- `make build_dotnet` succeeds in `~/git/LLNL/wintap/wintap`.
- `sudo python3 devtools/process_capture_smoke_test.py --start-lintap ...` passes at least once.
- Validation artifacts can be copied back to the Mac with `rsync` or `scp`.
