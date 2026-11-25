---
title: "Initial Analysis: Wintap Test Cleanup"
type: concept
confidence: medium
grounded_by:
  - ../Wintap/tests/Wintap.Tests
  - ../Wintap/tests/Wintap.Tests/Wintap.Tests.csproj
  - ../Wintap/CLAUDE.md
  - ../Wintap/Directory.Packages.props
  - ../Wintap/global.json
  - ../Wintap/.github/workflows/release.yml
  - ../Wintap/devtools
  - ../Wintap/diagnostics/process-smoke-test/Program.cs
  - wiki/decision/test-project-structure-and-first-test.md
policy: agent-editable
last_validated: 2026-11-22
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap/tests; ../Wintap/devtools; ../Wintap/diagnostics/process-smoke-test
tags: [feature-work, testing, test-organization, xunit, execution-boundaries]
---

# Initial Analysis: Wintap Test Cleanup

## Finding and Scope

Recommend organizing the existing project in small slices before changing project
topology. The flat suite mixes semantic regressions, source guards, real local
integration, and native workloads; neither its directory nor its historical
`Category` tags reliably describe execution cost or prerequisites.
<!-- SYNTHESIS: ../Wintap/tests/Wintap.Tests; ../Wintap/devtools/test_network_endpoint_smoke.py; ../Wintap/CLAUDE.md -->

The human expanded the workflow to Wintap test **analysis and planning** on
November 22. This pass changes only the Analytics wiki: no Wintap branch switch,
source/test move, restore, build, test execution, collector run, or dataset access.
<!-- HUMAN-DECISION: conversation 2026-11-22 — include Wintap repo tests; prepare initial analysis and plan. -->

Static inspection used Wintap's clean `develop` checkout at `06849b4`. The reserved
feature branch and cached `origin/develop` both point to `a418aa4`; no fetch was
performed. Both revisions contain 63 C# test files; their test-tree difference is
one trailing blank line, but their production-source differences are substantive.
Refresh the selected branch and source baseline before implementing; do not infer
that equivalent test files imply equivalent tested behavior.

**Implementation refresh:** the human subsequently approved the first slice and
explicitly authorized a static draft on the shared feature checkout at `a418aa4`,
deferring the Windows baseline. Five test files now reside under `Unit/` and have
unit/synthetic traits; the 63-file inventory is unchanged. The initial analysis
above remains historical; current draft checks and limits are in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].
<!-- HUMAN-DECISION: conversation 2026-11-22 — approve implementation; defer Windows baseline and share the feature checkout with the sensor worker. -->

## Project and Runner Boundary

- One xUnit project: `tests/Wintap.Tests/Wintap.Tests.csproj`, targeting
  `net10.0-windows10.0.17763.0`, referencing both `WintapAPI` and the Windows agent.
- Eleven linked production C# files include ten Linux helpers/sensors and the
  Windows service-manager hash wrapper. Six copied assets include an agent-state
  template, two BPF sources, and three Linux sensor sources.
- SDK baseline is **10.0.402**; central pins are xUnit **2.9.3**, VSTest adapter
  **3.1.1**, and Microsoft.NET.Test.Sdk **17.14.1**. Keep dependencies unchanged.
- The Windows solution filter includes the test project. Release CI builds on
  Windows and runs the entire project with `dotnet test ... -c Release --no-build`.
- Default SDK C# inclusion permits subdirectory moves, but preserve project and
  assembly names, namespaces, linked-source paths, and copied asset names.
  Production `InternalsVisibleTo("Wintap.Tests")` makes assembly renaming material.
<!-- GROUND_TRUTH: ../Wintap/tests/Wintap.Tests/Wintap.Tests.csproj; ../Wintap/global.json; ../Wintap/Directory.Packages.props §Test only; ../Wintap/Wintap.Windows.slnf; ../Wintap/.github/workflows/release.yml §Build and test; ../Wintap/wintap/platform/windows/sensor/etw/helpers/ProcessTraceDataExtensions.cs -->

Linux helper tests in this assembly are **not native Linux collector coverage**.
Use a Windows runner for the initial managed gate; non-Windows build success or
source inspection must not be reported as native sensor qualification.

The accepted bootstrap decision specifies per-target siblings, but `Lintap.Tests`
and `Mactap.Tests` do not exist. It anticipated the eventual Windows-agent
reference; the current Linux-source mix needs a later architectural review, not
an incidental project split during file cleanup. See
[[wiki/tension/wintap-test-platform-boundaries]].

## Static Inventory — Not Discovered or Executed Cases

Tracked files only; no build products, packages, local data, or audit outputs.
Attribute counts are lexical source counts, not a runtime discovery manifest.

| Behavior group | C# files | Facts | Theories | Initial disposition |
|---|---:|---:|---:|---|
| API/schema | 3 | 6 | 5 | Unit/contract; preserve shared model coverage. |
| Identity and process store | 8 | 62 | 17 | Mixed contract/local DuckDB/OS probe; classify by case. |
| Attribution and bounded cache | 4 | 33 | 10 | Unit/contract plus isolated writer integration. |
| Windows process collection | 4 | 92 | 20 | Replay/snapshot/lineage regressions; retain overlapping seams. |
| Windows file/subscriptions | 6 | 35 | 14 | Normalization units and emission/provider contracts. |
| Linux helpers | 6 | 37 | 1 | Synthetic helpers mixed with copied-source guards. |
| Network projection | 4 | 7 | 6 | Endpoint and serializer contracts; not packet capture evidence. |
| Registry | 8 | 57 | 14 | Payload, aggregation, retry, canary, teardown, plumbing. |
| PowerShell/Windows shell | 3 | 22 | 10 | Synthetic sensor/telemetry contracts; native smoke is separate. |
| ETL/runtime/health and validation controls | 17 | 100 | 38 | Mixed source guards, globals, workers, serializer integration, native command. |
| **Total** | **63** | **451** | **135** | **586 attributed test methods**, not an executed-case total. |

There are **603 InlineData attributes**, **9 MemberData uses** across four files,
and **6 collection definitions**, each disabling parallelization. Theory data
expansion and discovery-time behavior still require the actual runner.
**26 files contain no Category trait at all**; the other 37 are not necessarily
fully tagged. Scan combined attributes such as `[Fact, Trait(...)]` as well as
standalone attributes. Existing tags include instruction IDs and descriptive
categories; preserve all of them, including grandfathered `P1.1`.
<!-- GROUND_TRUTH: ../Wintap/tests/Wintap.Tests; ../Wintap/CLAUDE.md §Build & Verification Commands -->

## Risks That Shape the First Cut

| Evidence | Consequence |
|---|---|
| `FileAttributionValidationTests.ActualCmdWritesAndExits` starts `cmd.exe`, writes/deletes a temporary file, and waits for child termination; it has `pai-06-command`. | Native workload, not a pure evaluator test. Category tags do not opt it out of broad execution. |
| `SystemIdentityProbeTests` mixes DuckDB cases with a current-process Windows start-time probe; that probe returns early off Windows. | An early return is not evidence of probe success on another platform. Preserve it initially; later make unsupported status explicit. |
| `MemoryMapBurstTests` sends 30,000 events, writes assembly-adjacent `ETLConfig.json`, changes roots/environment and Esper deployments, and retains result artifacts. | Explicit isolated-process integration gate; do not include in the small default-safe slice. Collection serialization alone does not prove global state is clean. |
| `EventChannelHealthWireInTests`, registry/drive-map fixtures, runtime-capability and attribution-writer collections manipulate shared state. | Preserve collection names/fixtures and initialization order. Review isolation before moving/splitting these groups. |
| Identity/shutdown/startup guards walk upward from `AppContext.BaseDirectory` to find the repo; other guards read copied source assets. | Redirecting output outside the repo can break tests even when compilation succeeds. Inventory source-root and content-copy assumptions before changing outputs. |
| `WindowsFilePathEmissionTests` uses `WindowsFilePathNormalizerTests.Map`. | Keep namespace/type/member names stable; include emission as the immediate neighbor of a normalizer move. Do not extract the fixture simultaneously. |
| Process sensor, replay/snapshot overlap, startup reconciliation, and resolver files cover related identity behavior at different seams. | Similar names are not duplication proof. Map emission, persistence, parent lifetime, PID reuse, and failure paths before merging. |
<!-- GROUND_TRUTH: ../Wintap/tests/Wintap.Tests/FileAttributionValidationTests.cs; ../Wintap/tests/Wintap.Tests/SystemIdentityProbeTests.cs; ../Wintap/tests/Wintap.Tests/MemoryMapBurstTests.cs; ../Wintap/tests/Wintap.Tests/EventChannelHealthWireInTests.cs; ../Wintap/tests/Wintap.Tests/IdentityContractTests.cs; ../Wintap/tests/Wintap.Tests/WindowsProcessStartupReconciliationTests.cs; ../Wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs -->

Source-string guards are useful implementation checks, but they do not execute
BPF, ETW, or capture paths. Retain and label them; replace them only when a
behavioral test covers the same risk. Reflection-based fixtures likewise need
separate review, not blanket deletion.

## Python and Executable Harnesses

Seven tracked `devtools/test_*.py` files contain **39 test methods by AST**:

| File | Static methods | Boundary |
|---|---:|---|
| `test_event_name_contracts.py` | 7 | Synthetic parser/literal checks. |
| `test_network_endpoint_smoke.py` | 10 | Mixed evaluator/mocks and one real host-interface traffic workload. |
| `test_network_trace_smoke.py` | 7 | Synthetic row oracle and source guard, not actual-object qualification. |
| `test_runtime_alignment.py` | 6 | Tracked project/config/source drift; invokes read-only git inventory. |
| `test_smoke_manifest.py` | 4 | Local JSON/Parquet controls; Python DuckDB and durable-root isolation required. |
| `test_telemetry_smoke_workload.py` | 2 | Linux-only subprocess workload and missing-helper refusal; not collector correctness. |
| `test_verify_rpm_payload.py` | 3 | Mocked RPM/platform and temporary payload controls; not installed-RPM acceptance. |
<!-- GROUND_TRUTH: ../Wintap/devtools/test_event_name_contracts.py; ../Wintap/devtools/test_network_endpoint_smoke.py; ../Wintap/devtools/test_network_trace_smoke.py; ../Wintap/devtools/test_runtime_alignment.py; ../Wintap/devtools/test_smoke_manifest.py; ../Wintap/devtools/test_telemetry_smoke_workload.py; ../Wintap/devtools/test_verify_rpm_payload.py -->

Do not start with broad Python discovery. `smoke_manifest.py` can publish to an
inherited `WINTAP_DATA_ROOT`; verify temporary-root/no-export isolation before
running harness controls. Real smoke CLIs and `Invoke-PowerShellSensorSmoke.ps1`
are separate execution boundaries, not tests collected by xUnit.
<!-- GROUND_TRUTH: ../Wintap/devtools/smoke_manifest.py §smoke_run; ../Wintap/devtools/README.md -->

`diagnostics/process-smoke-test/ProcessSmokeTest.csproj` is a console executable,
not a second xUnit project. It launches Lintap and a process tree and queries
Parquet via the DuckDB CLI. Its bypass configuration and optional parent-hash
check limit its claim; retain as an explicit narrow harness, not generic sensor
or pipeline acceptance.
<!-- GROUND_TRUTH: ../Wintap/diagnostics/process-smoke-test/ProcessSmokeTest.csproj; ../Wintap/diagnostics/process-smoke-test/Program.cs §StartLintap; §Main -->

## Next Step

This is the initial dated inventory, not a current suite census. `Lintap.Tests`
now exists, macOS/Linux feature testing and bounded Linux captures are complete,
and stable .NET 10 selection supersedes the exact development SDK pin. Native
Windows acceptance and further mixed-file/topology review remain separate; use
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]] for current gates.
