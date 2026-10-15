---
title: "Verification: Refactor File System Data and Log Paths"
type: concept
confidence: medium
grounded_by:
  - ../wintap/wintap/core/shared/Env.cs
  - ../wintap/tests/Wintap.Tests/RuntimeDataRootTests.cs
policy: agent-editable
last_validated: 2026-10-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/refactor-data-log-paths/verification.md
tags: [feature-work, verification, data-pipeline, paths, shared-mount]
---

# Verification

## 2026-10-15 — rdp-01/rdp-02 development VM

Environment: Multipass `lintap-dev`, Ubuntu 24.04.5 arm64, kernel
6.8.0-142-generic, .NET SDK 8.0.131, clang 18.1.3, bpftool 7.4.0. The VM
was created from the Lintap `grantj-rhel8-testing` Multipass recipe. The
recipe's optional SSH-config helper was unavailable in the temporary recipe
directory and was not needed; both repository mounts completed successfully.

Mounts verified:

- `/Users/johnson30/git/LLNL` → `/home/ubuntu/git`
- `/Users/johnson30/data/lintap` → `/home/ubuntu/data/lintap`

Commands and results:

- `make build_ebpf` — PASS.
- `make build_dotnet` — PASS; 0 errors, existing warnings only.
- `dotnet restore tests/Wintap.Tests/Wintap.Tests.csproj` — PASS.
- `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --no-restore --filter "FullyQualifiedName~RuntimeDataRootTests"` — PASS, **20 passed**.
- Grep gate for `Env.FileDataRoot` consumers outside `Env.cs`/`Paths.cs` — PASS.
- Grep gate for legacy `/var/lib/lintap` or `/var/log/lintap` literals outside `Env.cs` defaults — PASS.
- `git diff --check` — PASS.

## 2026-10-15 — rdp-05 package smoke (partial)

- Debian arm64 package build on `lintap-dev` — PASS. The builder completed
  eBPF compilation, framework-dependent .NET publish, staged validation, and
  produced `lintap_0.1.0-1_arm64.deb`.
- `dpkg-deb --contents` — PASS: package contains `/var/lib/lintap/data/` and
  `/var/lib/lintap/runtime/`, with no `/var/log/lintap` package directory.
- `sudo dpkg -i lintap_0.1.0-1_arm64.deb` — PASS. Installed env explicitly
  contains both new roots; post-install created both directories with mode
  `0750`; `/var/lib/lintap/data/parquet` was not created.
- Bounded `systemctl start lintap.service` probe — PASS. The service stayed
  active for 15 seconds and journal output reported data path
  `/var/lib/lintap/data`, raw sensor path `/var/lib/lintap/data/raw_sensor`,
  runtime root `/var/lib/lintap/runtime`, and event store/log files under the
  runtime tree. The service was stopped after the probe; no event-output
  count is claimed from this short run.
- RPM smoke — BLOCKED: `rpmbuild` is not installed in the Ubuntu arm64 VM;
  the RPM builder remains statically validated only.
- Full service-start and event-output acceptance remains pending for rdp-05;
  this package-install check does not claim sensor runtime coverage.

The test project required `<IsTestProject>true</IsTestProject>` before
`dotnet test` would execute tests; without it, the SDK silently skipped the
test run with exit code 0. This configuration correction is included with the
test changes.

The complete test project was also run after enabling execution: 333 passed
before the run aborted with 17 pre-existing Linux-incompatible Windows sensor
failures (Windows Principal, Windows process-lineage assumptions, and an ETW
test-host finalizer crash). These failures are outside the path refactor and
are not treated as an rdp gate failure; the focused `RuntimeDataRootTests`
class is the applicable gate for this slice.

## Scope verified

- Data defaults resolve to `<app-root>/data`.
- Runtime defaults resolve to `<app-root>/runtime`.
- Programmatic and configured precedence is covered for both roots.
- Windows, macOS, and Linux default forms are covered.
- Same-directory configuration is accepted and startup warning logic is in
  `CacheManager`.
- Runtime consumers use centralized `Paths` members.
- Uploader relative keys remain rooted at `raw_sensor/` under the new data
  root.

## 2026-10-15 — rdp-03 packaging checkpoint

Packaging worktree: `../Lintap-rdp`, branch `grantj/debian-package-refresh`,
commit `301ff63`.

- Debian and RPM env files explicitly set `WINTAP_DATA_ROOT=/var/lib/lintap/data`
  and `WINTAP_RUNTIME_ROOT=/var/lib/lintap/runtime`.
- Package staging and maintainer scripts create the two new directories and no
  longer create `/var/log/lintap`; purge paths preserve `/var/lib/lintap`.
- The pidstat collector defaults parquet output to the data root and its spool
  to `<runtime-root>/pidstat-spool`; explicit `PIDSTAT_PARQUET_ROOT` and
  `PIDSTAT_SPOOL_DIR` overrides remain supported.
- Deb/RPM README, build/test, and restart documentation now describes the
  split and direct `data/raw_sensor` layout.
- `bash -n` for both package builders — PASS.
- `git diff --check` — PASS.
- VM `python3 -m py_compile pidstat-collector.py` — PASS.
- VM collector-root gate with duckdb import stub — PASS.
- `python3 -m pytest -q tests/test_pidstat_collector.py` — BLOCKED: pytest is
  not installed in the VM; `uv` could not fetch pytest/duckdb because PyPI
  network access timed out. No test result is claimed for this blocked gate.

## 2026-10-15 — rdp-04 downstream checkpoint

Wintappy commit: `018f541` on `main`.

- `WINTAP_DBT_DATASET` now defaults directly to `WINTAP_DATA_ROOT`.
- DBT start/end day discovery now scans `WINTAP_DATA_ROOT/raw_sensor`.
- The example environment no longer suggests a `/parquet` suffix.
- A targeted scan of Analytics `streamlit/` and notebooks found no live
  hardcoded old-layout input to change.
- `git diff --check` and Makefile dry-run configuration gate — PASS.
