---
title: ".NET 10 upgrade closure: corrections and remaining qualification gates"
type: workflow
confidence: high
grounded_by:
  - ../wintap/global.json
  - ../wintap/wintap/Wintap.Common.props
  - ../wintap/wintap/Makefile
  - ../wintap/diagnostics/nesper-repro/nesper-repro.csproj
  - ../wintap/diagnostics/process-smoke-test/ProcessSmokeTest.csproj
  - ../wintap/shared/samples/SimpleEventPlugin/SimpleEventPlugin.csproj
  - ../wintap/shared/samples/SimpleMcpPlugin/SimpleMcpPlugin.csproj
  - ../wintap/shared/samples/SimplePluginMcpServer/SimpleMcpPluginServer.csproj
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Lintap/multipass-lintap.sh
  - ../Lintap/multipass-lintap.ps1
  - ../Lintap/packaging/dotnet-common.sh
  - ../Lintap/tests/test_dotnet_packaging.py
  - ../wintap/devtools/test_runtime_alignment.py
policy: agent-editable
last_validated: 2026-10-26
repo_scope: cross-repo
implementation_area: packaging
event_domain: none
audience: developer
status: draft
source_paths: ../wintap; ../Lintap; validation/process-creation/scripts
tags: [net10, upgrade, oversight, packaging, corrective-plan]
---

# Current implementation status

The user authorized implementation, commit and push on the existing feature
branches. Source corrections now cover all 13 C# projects, package dependencies,
project-directory/exact-SDK preflight, provisioning and active run/tool/docs defaults.
SDK **10.0.402** remains mandatory; package scripts reject a changed baseline or
`latestPatch` substitution before cleanup/native compilation, including `--publish-dir`.
Staged main-app runtimeconfig must target `net10.0` with .NET 10.0 frameworks.
<!-- GROUND_TRUTH: ../Lintap/packaging/dotnet-common.sh; ../Lintap/packaging/lintap-deb/build-deb.sh; ../Lintap/packaging/lintap-rpm/build-rpm.sh; ../wintap/devtools/test_runtime_alignment.py -->

Retargeting also fixes the sample MCP project reference and guards the event
sample's Windows-only post-build copy. Redirected native builds now exclude old
repo-local `bin`/`obj` generated sources instead of deleting them. Five diagnostic/
sample lock files accompany their new targets. Dependency majors and telemetry,
identity, retry capacity and experimental default-off controls are unchanged.
<!-- GROUND_TRUTH: ../wintap/shared/samples/SimpleMcpPlugin/SimpleMcpPlugin.csproj; ../wintap/shared/samples/SimpleEventPlugin/SimpleEventPlugin.csproj; ../wintap/Directory.Build.props -->

The broader inventory additionally distinguishes the two legacy `.vdproj` installer
snapshots retained in the older Visual Studio solution from the current WiX release
workflow. Their stale .NET 8 payload inventories are retained and explicitly marked
**not for .NET 10 builds/deployment**; do not claim all historical files contain no 8.
<!-- GROUND_TRUTH: ../wintap/platform/windows/WintapSetup/README.md; ../wintap/.github/workflows/release.yml -->

See [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]] for actual
checks and preserved failures. Operator-assisted native RHEL 9 self-contained RPM
build/inspection/install and bounded process/file/TCP/shutdown plus fresh DBT smoke
were previously reported pass. The user now reports a newer native package was
deployed and two S3 canary rounds reviewed; `sched_exec` provenance and independent
package-to-installed-payload proof remain open. Other package modes/platforms and
full live acceptance remain separate gates.

## Initial source inventory (before these corrections)

The user identifies remaining .NET 8 configuration as an **upgrade oversight**,
not an accepted limitation. This plan closes the original .NET 10 objective.
The initial planning request did not authorize implementation or host changes;
the later explicit implementation/commit/push request supersedes that planning limit.

The initial tracked-file inventory could not confirm source-wide .NET 10 alignment:

| Area | Current source configuration |
|---|---|
| SDK | Wintap `global.json`: 10.0.402, latestPatch, no prereleases. Packaging scripts do not enforce this exact version or ensure SDK discovery from their caller directory. |
| Main projects | Windows Wintap, Linux Lintap, Mactap, WintapAPI, MCP helper, Windows service manager/recorder and Wintap.Tests target .NET 10 (Lintap/Mactap inherit Wintap.Common.props). |
| Five leftover projects | Both diagnostics (`nesper-repro`, `process-smoke-test`) and three shared samples (`SimpleEventPlugin`, `SimpleMcpPlugin`, `SimplePluginMcpServer`) still explicitly target net8.0. |
| Package metadata | Both Debian and RPM builders still emit aspnetcore-runtime-8.0 for framework-dependent builds, including their help text. |
| Operational defaults | Wintap Makefile still defaults DOTNET_TFM to net8.0; Lintap Bash/PowerShell Multipass bootstrap installs SDK/runtime 8 and prints net8 DLL paths. |
| Tooling/docs | Wintap baseline collector, TCPdump validator, diagnostic program and devtools examples retain version-8 references; Analytics' two process-creation runner scripts default to net8 DLL paths. Current README/Multipass documentation also contains stale references. |
| Wintappy | No tracked .NET target/install configuration found; Python/DBT engine versions are not .NET framework versions. |

This is source configuration evidence, not newly executed MSBuild, runtime or
installed-package acceptance. SDK 10.0.402 is not a runtime version; inspect emitted
runtimeconfig/deps files and actual runtime provenance separately.

## Corrective sequence

1. **Fix packaging first.** Replace both builders' framework-dependent dependency
   and help declarations with ASP.NET Core runtime 10.0. Add SDK preflight before
   destructive build cleanup: resolve the project repo's global.json and require
   its qualified SDK 10.0.402 regardless of the caller directory. Missing/wrong SDK
   must fail clearly. Retain latestPatch for development only if exact package-build
   enforcement prevents silent qualification drift. Update the guide to describe
   the corrected mode instead of presenting self-contained output as the solution.
2. **Align active build/provision/run paths.** Change Wintap Makefile's TFM default
   to net10.0; update both Multipass implementations to install/select the same
   qualified SDK and runtime 10, and align displayed/run DLL paths. Update current
   diagnostics, validator and Analytics runner defaults. Keep native storage and
   existing deployment/state/security controls intact.
3. **Retarget the five diagnostics/samples.** Move remaining targets to net10.0;
   resolve their project references and qualify restore/build independently.
   Preserve pre-existing failures, including suspicious sample ProjectReference
   paths, rather than blaming or silently repairing unrelated defects. Do not
   omit these projects and then claim "everywhere".
4. **Synchronize current documentation and add drift gates.** Cover project TFMs,
   selected SDK, package dependency generation, caller-directory behavior, both
   self-contained/framework-dependent modes and operational output paths. A tracked
   source inventory must find no active .NET 8 targets/install/run defaults.
   Historical dated handoffs retain their original findings but must be clearly
   historical and point to the current guide; do not rewrite evidence history.
5. **Qualify artifacts and host behavior.** Fresh locked restore/build/tests and
   native eBPF builds; build/inspect both package modes, verify net10 runtimeconfig,
   correct runtime dependency and self-contained payloads. Operator-assisted RHEL 9
   installation/runtime/sensor/capture/shutdown checks remain a separate live gate.
   Windows compilation is not Windows runtime acceptance. Preserve missing evidence
   as pending rather than issuing a blanket version/runtime certification.

## Version distinctions and acceptance gates

- NuGet/transitive package major versions (e.g. System.Composition 8) and JavaScript
  versions are **not** .NET target/runtime versions. Do not indiscriminately upgrade
  every dependency containing an 8. The explicitly deferred AI/MCP/SPA dependency
  versions in Directory.Packages.props require their own compatibility decision.
- [x] All 13 tracked C# projects resolve to net10.0 or net10.0-windows targets (SDK 10.0.402 MSBuild evaluation).
- [x] Both builders select/enforce SDK 10.0.402 from any supported caller location (regression coverage).
- [x] Both framework-dependent metadata declarations now specify ASP.NET Core 10.0.
- [ ] Framework-dependent Debian/RPM metadata requires ASP.NET Core 10.0, not 8.0;
  self-contained packages do not acquire an unintended system .NET 8 dependency.
- [x] Active bootstrap, run, diagnostic and current-documentation defaults use 10;
  legacy/historical installer snapshots are explicitly excluded from release use.
- [ ] Fresh tests/builds and package inspections pass, with scoped failures preserved.
- [x] Initial RHEL 9 on-host package/capture and two canary-round outcomes supplied;
  declared endpoint/file/process observations pass by report/read-only review.
- [ ] Independently verify the newer RPM payload against trusted digest and correlate
  its loaded object hashes. `sched_exec`, strict-count, parallel-round settlement,
  and multi-day gates remain open.

Generic RHEL 9 prerequisite checks pass, including exact stable SDK selection and
compiler/BTF/header checks. The designated test system is disposable by explicit
user direction; security controls still remain intact. Its identifying details and
raw outputs are conversation-only. Continue on the same feature branches, with
explicit commit/push authorization and no rebase or PR publication.
