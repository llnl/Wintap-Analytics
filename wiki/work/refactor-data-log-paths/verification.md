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
