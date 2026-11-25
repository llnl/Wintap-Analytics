---
title: "Lintap Supporting Repository"
type: repo
confidence: high
grounded_by:
  - ../Lintap/README.md
  - ../Lintap/teletap/README.md
  - ../Lintap/packaging/README.md
  - ../Lintap/Multipass.md
  - ../Lintap/multipass-lintap.sh
  - ../Lintap/multipass-lintap.ps1
  - ../Lintap/multipass-check-dev.sh
  - ../wintap/global.json
  - ../wintap/wintap/platform/linux/sensor/ebpf/helpers/LibBpf.cs
  - ../Lintap/pidstat-go/main.go
  - ../Lintap/pidstat-go/schema.go
  - ../Lintap/pidstat-go/Makefile
  - ../Lintap/pidstat-go/sampler.go
  - ../Lintap/pidstat-go/config.go
  - ../Lintap/pidstat-go/kernel.go
  - ../Lintap/pidstat-go/replay.go
  - ../Lintap/pidstat-go/collector.go
policy: agent-editable
last_validated: 2026-11-23
repo_scope: Lintap
implementation_area: packaging
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Lintap/README.md; ../Lintap/teletap/README.md; ../Lintap/Multipass.md; ../Lintap/packaging
tags: [Lintap, dev-environment, packaging, repo]
---

# Lintap Supporting Repository

`../Lintap` is a Linux proof-of-concept host-based event sensor repository that implements Wintap-like functionality for Linux environments and transforms Linux telemetry into the semantic Wintap data model for analysis.
<!-- GROUND_TRUTH: ../Lintap/README.md §Lintap -->

This wiki treats Lintap as supporting infrastructure, not the main Wintap sensor implementation. The Lintap README states that the newer TeleTap/eBPF implementation has moved into the Wintap repository, while this repo still contains initial post-processing code and the older sysdig-based playground.
<!-- GROUND_TRUTH: ../Lintap/README.md §Running Lintap -->

## Two Linux Paths

The TeleTap-oriented workflow uses Linux eBPF tools, Python, DuckDB, and both Wintap
and Lintap repos; runtime sensor attachment requires appropriate privileges.
Package preflight follows Wintap's stable .NET 10 `global.json` policy (minimum
10.0.100, `latestMinor`, no prereleases) and records the actual SDK. Multipass may
install 10.0.402, which satisfies that policy but is not mandatory for packaging.
Build commands build/run Wintap's `Lintap.csproj`.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §Build prerequisites; ../wintap/global.json; ../Lintap/teletap/README.md §Build Commands -->

TeleTap output is expected to include canonical raw sensor Parquet under `raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/` and raw process connection increments partitioned by protocol. The old merged-to-raw conversion step is explicitly removed, and the canonical full ETL is stated to live in `Wintap-PyUtil/wintap_dbt`, not in the TeleTap directory. `Wintap-PyUtil` is the `../Wintappy` repo; see [[wiki/repo/wintappy-pipeline-repo]] for its bronze/silver/gold DBT pipeline.
<!-- GROUND_TRUTH: ../Lintap/teletap/README.md §Data output; §Full ETL with DBT -->

The older sysdig workflow captures process, file, network, and optional SELinux activity as TSV/SCAP, converts raw TSV into raw Wintap format, and then relies on Wintap-style ETL scripts for final datasets.
<!-- GROUND_TRUTH: ../Lintap/README.md §Running Lintap (sysdig); §Post-processing -->

## pidstat Collector (promoted 2026-08-17)

**2026-11-24 packaging update:** Debian/RPM builders now package the static Go
collector at `/usr/lib/lintap/pidstat-collector`, with direct service `--collect`
startup and no collector Python/uv/DuckDB/bootstrap runtime requirement. Go 1.27.3
is build-host-only. Python source remains a compatibility test reference; the older
deployment description below is historical. Greenfield Debian Ubuntu arm64 package
build/install/reinstall, default rotations, schema and crash recovery tested;
consumer/paired-live review remains open. Ubuntu amd64
and native RPM qualification deferred to other platforms. See
[[wiki/work/fix-pidstat-collector/verification]].
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/build-deb.sh; ../Lintap/packaging/lintap-rpm/build-rpm.sh; ../Lintap/packaging/lintap-deb/lintap-pidstat.service -->

`../Lintap/pidstat-collector.py` is a single-process Python host-performance collector: it samples `/proc` directly (stat/io/status/schedstat — full pidstat-equivalent schema plus `hostname` and container-attribution columns from cgroup/ns), computes rates from counter deltas, and rotates typed parquet into the sensor's cache at `raw_sensor/pidstat/dayPK=/hourPK=/` every `PIDSTAT_ROTATE_INTERVAL_SEC` (default 300, synced to the sensor upload cycle), where the sensor's uploader ships it ([[wiki/component/sensor-upload-cache-pipeline]]). Configuration is `PIDSTAT_*` env vars; sampling default 5 s; crash salvage via a spool outside the swept tree; accumulation guard caps unshipped bytes/age. It runs as a systemd service (`lintap-pidstat.service`) from a uv-managed Python 3.12 venv (`pidstat-collector-bootstrap.sh` / `-launch.sh`) because RHEL 8's system python3.6 predates duckdb wheels. `pidstat-collect.sh` remains only as a minimal example; the interim bash rotating collector was retired after its per-line command substitutions caused a ~700 forks/sec storm ([[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]]). Wintappy's DBT bronze reads the parquet layout directly.
<!-- GROUND_TRUTH: ../Lintap/pidstat-collector.py; ../Lintap/packaging/lintap-rpm/lintap-pidstat.service; ../Lintap/README.md §Managed pidstat collector -->

Open watch item: collector CPU usage looked higher than expected in early RHEL 8 field runs — investigate with data from more systems (tracked in [[wiki/work/improve-pidstat-collector/implementation_plan]]).

### Go writer feasibility checkpoint (validated 2026-10-30)

`../Lintap/pidstat-go` is an **unpackaged Go collector with explicit durable modes**,
not the installed Python service or a qualified release.
Go1.27.3/parquet-go0.32.0 with pure-Go ZSTD build static Linux arm64/amd64 binaries;
native Ubuntu arm64 execution encoded captured Python TSV with exact26-column
physical-column/schema/value/null and partition/window parity on266/705/1640 rows.
Rates remain FLOAT, signed integer widths/legacy annotations remain unchanged,
all columns are OPTIONAL and timestamp MICROS is local/`isAdjustedToUTC=false`.
Analytics owns native commands/skill and private evidence; Lintap owns the spike;
`../Wintap-PyUtil` is the canonical consumer and has not been DBT-qualified
in this unit. Its separately authorized source preflight is documented in
[[wiki/work/dbt-source-validation/verification]]. See
[[wiki/work/fix-pidstat-collector/verification]] for collector evidence.
Human fpc-01 acceptance is recorded. fpc-02 now passes exact **raw-input** sampler
replay of all3captures,14Go tests,17actual-Python config cases and two52-row controlled
sampler fixtures (100Hz/4KiB;250Hz/16KiB). Native arm64 raw replay and a bounded411-row
diagnostic pass; fpc-02 human approval is recorded. Linux clock ticks come from kernel AT_CLKTCK,
page size from os.Getpagesize, without cgo or child commands. Rates/scheduling are
monotonic in live mode; raw replay retains Python captured durations/clamp. Rounded
microsecond row time can cross midnight while source epoch remains in the preceding
window/partition. Go bounds identity caches and skips malformed optional counters
where Python can raise; missing-field zero/default semantics stay unchanged.
Fpc-02 was human-approved. Fpc-03 now retains legacy TSV/meta with seal/publication
journals, exclusive Go spool locking, unique active-file ownership, successful-close
synced atomic no-overwrite publication, source-retaining retry, codec validation,
signal shutdown and scoped oldest-first caps. Metadata chooses the sample window;
configured hostname owns filenames independently of row hostname. Exact durable raw
replay passes all3real captures and actual Python-created spool recovery;26Go tests
also pass natively on arm64. Native SIGTERM/SIGINT each seal411readable rows;
SIGKILL restart recovers137rows and filesystem failure retries20unchanged-source rows.
Review pending; original host pytest runner is unavailable, not counted as PASS.
The four-hour default-cadence sensor-on soak is complete: 49 files/399312 rows,
2880 uninterrupted sample times, median CPU 0.47% of one core and median RSS about
17 MiB (peak 44.86 MiB). See [[wiki/work/fix-pidstat-collector/soak_review]].
Python/service/package behavior above remains unchanged; comparative resources,
paired-live, DBT and inspected RHEL/native amd64 qualification remain later gates.
The operator reports RHEL execution; no new native evidence was inspected. No lower CPU
claim, power-loss or exactly-once delivery guarantee is established. Python does not
honor Go's lock/journals: never share a spool, and inspect/drain Go state before rollback.
See [[wiki/tension/pidstat-publication-versus-uploader-receipts]].
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/main.go; ../Lintap/pidstat-go/schema.go; ../Lintap/pidstat-go/sampler.go; ../Lintap/pidstat-go/kernel.go; ../Lintap/pidstat-go/replay.go; ../Lintap/pidstat-go/Makefile; ../Wintap-Analytics/wiki/work/fix-pidstat-collector/verification.md -->
<!-- GROUND_TRUTH: ../Lintap/pidstat-go/collector.go; ../Lintap/pidstat-go/collector_test.go; ../Wintap-Analytics/validation/pidstat-loop/check_spool.py; ../Wintap-Analytics/validation/pidstat-loop/check_native_spool.py -->

## Package Builder Contract (promoted 2026-10-05)

Current Debian and RPM build, inspection, installation, and smoke-test
procedures are consolidated in `../Lintap/packaging/README.md`. Format-local
READMEs point there, while dated handoff and review files are retained as
historical records rather than competing instructions.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md -->

The Debian builder under `../Lintap/packaging/lintap-deb/` is the refreshed
package path for Debian/Ubuntu amd64 and arm64. It uses a native `/var/tmp`
work root, validates the tracepoint eBPF tier on every build, validates the
four functional CO-RE objects on native BTF builds, stages SELinux objects
opportunistically, publishes the main application with MCP disabled, and
publishes the MCP helper separately unless `--skip-mcp` is requested.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/build-deb.sh -->

The RPM builder's current supported artifact is RHEL 8-compatible `x86_64`.
Although it contains cross-build setup, cross-build mode disables BTF while
staged-payload validation unconditionally requires the CO-RE
`file_ops_tracer.bpf.o`. Therefore the current end-to-end RPM build contract is
a native `x86_64` host with readable BTF; older successful-cross-build notes are
historical evidence, not validation of the current script.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-rpm/build-rpm.sh §eBPF build; §expected_bpf_objects -->

The canonical guide now includes **operator-assisted RHEL 9 x86_64 qualification**:
read-only inventory, approved repository/prerequisite setup, stable .NET 10 SDK selection,
fresh self-contained `.el9` build, package/native dependency inspection, then
separately approved installation/capture/downstream checks. RHEL 9 validation is
pending; a release suffix or Ubuntu pass is not acceptance. Keep security controls,
existing collectors and historical identity/data intact unless the user explicitly
designates a disposable test system. Both framework-dependent builders now declare
ASP.NET Core 10.0; both validate stable .NET 10 selection from the project directory
before cleanup/compilation and validate the main staged .NET 10 runtimeconfig.
These correct upgrade oversights; source/regression alignment does not certify a
fresh installed package:
[[wiki/work/wintap-telemetry-identity-and-data-quality/runtime_alignment_plan]]
records diagnostics/sample and provisioning/run corrections plus pending live gates.
<!-- GROUND_TRUTH: ../Lintap/packaging/README.md §RHEL 9 prerequisites and operator-assisted qualification; ../Lintap/packaging/lintap-rpm/build-rpm.sh §DOTNET_REQUIRES; ../Lintap/packaging/lintap-deb/build-deb.sh §DOTNET_DEPENDS -->
<!-- GROUND_TRUTH: ../Lintap/packaging/dotnet-common.sh; ../Lintap/tests/test_dotnet_packaging.py -->

The managed libbpf resolver tries `.so.1`, `.so.0`, then `.so`; qualify required APIs
and actual hook behavior, not package-name or library-load success alone. Do not
fake compatibility with a SONAME symlink. SDK minimum 10.0.100, `latestMinor` and
no prereleases govern greenfield packaging; builders report the actual selected SDK.
SDK preflight is not native package qualification.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/helpers/LibBpf.cs §ResolveLibbpf; ../wintap/global.json; ../Lintap/packaging/dotnet-common.sh -->

The Debian environment follows the field sensor settings while deliberately
retaining Snappy Parquet compression because current Ubuntu glibc supports the
bundled compression library. The RHEL 8 RPM environment retains its separate
uncompressed compatibility setting; this is a compression/configuration
divergence, not a semantic event-model divergence.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/lintap.env; ../Lintap/packaging/lintap-rpm/lintap.env -->

Linux packaging explicitly separates the data root
(`/var/log/lintap/data`, directly containing `raw_sensor/`) from the runtime
root (`/var/log/lintap/runtime`, containing logs, DuckDB, and Esper staging).
The manual `packaging/cleanup-test-install.sh --yes` utility is only for
disposable test hosts; package install and upgrade do not migrate or delete
telemetry.
<!-- GROUND_TRUTH: ../Lintap/packaging/PATHS_AND_CONFIGURATION.md -->

The 2026-10 release candidate assets are Debian `0.1.0-14` for amd64 and arm64
and RPM `0.3.5-12.el8` for x86_64. They are independently versioned package
artifacts and should be identified by their package-manager versions when
deployed.
<!-- GROUND_TRUTH: wiki/work/debian-package-refresh/release-README.md -->

## Multipass development dependencies

Both launchers install build-host Go 1.27.3 through
`packaging/install-build-go.sh`, selecting native Linux amd64/arm64 and validating
the archive against official release metadata before isolated installation. The
installer runs even when optional post-create checks are disabled; failure stops
provisioning. Existing VMs can run it explicitly without recreation. It does not
replace system Go or install a package-runtime dependency; login-shell profile
sets `GO`, `GOTOOLCHAIN=local` and PATH. Actual live installation remains to be
qualified; fake-download and packaging/provisioning regressions pass.
<!-- GROUND_TRUTH: ../Lintap/packaging/install-build-go.sh; ../Lintap/multipass-lintap.sh; ../Lintap/multipass-lintap.ps1; ../Lintap/tests/test_build_go_setup.py -->

Lintap owns the Bash/PowerShell Multipass provisioning entry points; the sensor
build uses the mounted Wintap checkout and Analytics owns the validation harness.
Both launchers install SDK **10.0.402** in guest-native `/opt/wintap-sdk`, including
.NET/ASP.NET Core 10, and DuckDB CLI/Python **1.5.6**. Ubuntu supplies Clang/LLVM,
libbpf/libelf development packages and running-kernel tools. The shared guest
check validates project-selected stable .NET 10, both shared runtimes, actual BPF compilation,
kernel BTF parsing and matching DuckDB versions. Cloud-init failures are fatal by
default. In the Bash launcher, the guest-native environment is still created by
`uv`, while pinned dependencies are installed through standard `pip` with bounded
HTTP retries after a reproduced `uv` HTTP stall. Host-mounted data is not recursively
re-owned, and best-effort cloud-init diagnostics have a host-side timeout so an
unresponsive command cannot wedge the launcher after failure. Branch checkout
remains opt-in; the example target is `develop`.
<!-- GROUND_TRUTH: ../Lintap/multipass-lintap.sh §runcmd; ../Lintap/multipass-lintap.ps1 §cloudInit; ../Lintap/multipass-check-dev.sh -->

Python environments and managed build outputs/intermediates use guest-native
storage to avoid reusing host environments or executing on shared mounts.
`BUILD_WINTAP=true` invokes tracer and managed builds; `RUN_VALIDATION_MOCKS=true`
uses a separate guest-local validation environment. Commands and output locations
are documented in `../Lintap/Multipass.md`. Fresh Ubuntu arm64 provisioning,
12-object tracer rebuild and managed compilation passed on 2026-10-26; details
are in [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]].
The repaired Bash path passed its full dependency check on a fresh Ubuntu arm64
development VM on 2026-11-23. A native self-contained arm64 package with version
`7.0.1~beta.1-1` then passed metadata, payload, required-native-dependency and
maintainer-script inspection. Installation and runtime capture were not run.
<!-- GROUND_TRUTH: ../Lintap/Multipass.md §Useful commands inside the VM; ../Lintap/multipass-lintap.sh §BUILD_WINTAP -->

## Wiki Boundary

Lintap pages should focus on Linux dev-environment setup, packaging/deployment support, raw-to-normalized data transition, and compatibility tensions. Do not use Lintap as the canonical source for Windows Wintap sensor semantics.
<!-- SYNTHESIS: inferred from ../Lintap/README.md, ../Lintap/teletap/README.md, and ../Wintap-Analytics/AGENTS.md -->

See also [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] and [[wiki/repo/wintappy-pipeline-repo]].
