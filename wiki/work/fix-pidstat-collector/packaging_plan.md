---
title: "Plan: Replace Packaged Python pidstat With Go"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Lintap/packaging/lintap-deb/lintap-pidstat.service
  - ../Lintap/packaging/lintap-rpm/lintap-pidstat.service
  - wiki/work/fix-pidstat-collector/implementation_plan.md
  - wiki/work/fix-pidstat-collector/verification.md
  - wiki/work/fix-pidstat-collector/soak_review.md
policy: agent-editable
last_validated: 2026-11-24
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: developer
status: draft
source_paths: ../Lintap/packaging; ../Lintap/pidstat-go (feature/pidstat-go ref)
tags: [feature-work, pidstat, go, packaging, rpm, debian, greenfield]
---

# Plan: Replace Packaged Python pidstat With Go

## Outcome and scope

Debian and RPM packages should install an architecture-matched static Go collector
at `/usr/lib/lintap/pidstat-collector`. `lintap-pidstat.service` should execute it
directly, without Python, uv, DuckDB or bootstrap downloads. Keep the existing raw
schema, output/spool roots, cadence, upload ride-along and service enablement policy.
The subsequent “Proceed” authorizes build/package development. Installation,
shared-service operations, deployment and commit/push require separate approval.

**Human scope correction:** there is no existing deployment footprint; treat this
as greenfield deployment. Python-to-Go upgrade orchestration, legacy deployment
migration and Go-to-Python package downgrade are not release requirements. Preserve
the telemetry contract and existing compatibility evidence; this is not permission
to change metrics or delete reference source, test data or unrelated local work.

“pkg” is interpreted here as the Linux package workflows already owned by Lintap:
Debian and RPM. No macOS installer or macOS collector is included.

## Current findings

**Arm64 lifecycle checkpoint:** default run crossed three rotation boundaries and
sealed successfully: four files, 25,999 rows, 199 sample timestamps at 5s cadence.
All 26 columns/types/nulls/partitions inspected. Config-preserving reinstall and
installed crash/restart recovery pass; both development services now stopped.
Consumer/paired-live review and other native platforms remain open.

**Current implementation:** both builders and units now use Go; Ubuntu arm64
package build/fresh install/direct service startup pass. The human authorizes
development-VM install/service tests and explicitly defers Ubuntu amd64/native RPM
qualification to other platforms. Rotation/restart inspection passes; consumer
qualification remains pending. Earlier Python-wiring statements below are historical.

**Historical authorization:** the initial “Proceed” covered build/package work;
later approval covered development install/service tests and feature commit/push.
Both builders/units now use Go. Field rollout/release acceptance remains separate.

**Update after authorized fetch/merge:** `origin/develop` contains the Go checkpoint
at `053b2b5`. It was merged without conflicts into Lintap's current feature branch
as `b988aa3`. The module is now available in the working tree; no packaging changes
were introduced by that merge. The earlier pre-fetch findings below are historical.

- Both current builders install and assert the Python collector, launcher and
  bootstrap script. Both service units execute the Bash launcher.
- `lintap.env` is already protected as a Debian conffile and RPM
  `%config(noreplace)`; retain that protection and existing local edits.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/build-deb.sh; ../Lintap/packaging/lintap-rpm/build-rpm.sh; ../Lintap/packaging/lintap-rpm/lintap-pidstat.service -->
- The inspected current branch is `feature/implement-sensor-fixes-and-cleanup-test-code`.
  It does not contain `pidstat-go/`. The local `feature/pidstat-go` ref at `b9d5d59`
  contains the Go module; a related checkpoint also exists in history at `053b2b5`.
  No single file named `pidstat-collector.go` was located in the inspected checkout.
- That module's Makefile builds spike-named binaries and pins Go 1.27.3. Its CLI
  requires an explicit `--collect`; no-argument invocation is not continuous sampling.
<!-- GROUND_TRUTH: ../Lintap git ref feature/pidstat-go:b9d5d59 §pidstat-go/Makefile, main.go, go.mod — ref inspection, not a current working-tree path -->
- Existing records establish earlier exact replay/static-build checks and a scoped
  four-hour arm64 soak (49 files, 399,312 rows). They do not establish package
  upgrades, comparative paired-live parity or inspected native RPM acceptance.
  fpc-03 and soak human acceptance remain unrecorded; earlier toolchain/test-runner
  failures must be rechecked rather than silently waived.
<!-- GROUND_TRUTH: wiki/work/fix-pidstat-collector/verification.md; wiki/work/fix-pidstat-collector/soak_review.md -->

## Work units

### PKG-01 — Resolve source and acceptance prerequisites

1. Confirm the intended Go source/ref with the human, refresh remote knowledge when
   authorized, and identify the target integration branch. Inspect topic commits
   before choosing a focused merge/cherry-pick; do not merge unrelated packaging
   drift or switch a dirty/shared checkout.
2. Review retained fpc-03/soak evidence and record acceptance or specific remaining
   findings. Reuse qualified work; do not repeat the entire rewrite by default.
3. Establish a working pinned toolchain, rerun Go tests/vet/module verification and
   relevant Python/evidence regressions. Reconfirm exact replay on preserved inputs.
4. Confirm current CLI/config/recovery behavior and package release versions. Retain
   the Python reference for compatibility testing, not as a deployment rollback target.

**Gate:** source identity, toolchain, reference and approval boundaries recorded;
no missing runner or unexplained compatibility failure labeled PASS.

### PKG-02 — Add a release binary build contract

1. Add a reusable Lintap build helper/target used by both builders. Build from the
   module with `CGO_ENABLED=0`, `GOOS=linux`, architecture mapping
   `amd64/linux-x64 → amd64` and `arm64/linux-arm64 → arm64`.
2. Keep Go and module downloads strictly on the build host. Use pinned modules,
   reproducible flags such as `-trimpath`, and native work-root output rather than
   host-mounted intermediate files. Preserve spike/replay diagnostics for tests.
3. Produce release-named binaries and stage only the selected target executable.
   Record source revision, Go/module versions and binary SHA-256.
4. Assert executable permissions, correct ELF machine, no dynamic interpreter and
   no `DT_NEEDED` entries. Do not infer native execution from cross-compilation.

**Gate:** static binaries for both architectures; no collector runtime dependency
on Go, Python, uv or DuckDB. Unsupported package architecture fails clearly.

### PKG-03 — Change package payload and service wiring

1. Stage `/usr/lib/lintap/pidstat-collector` in both builders and replace Python
   payload assertions with executable/architecture/static checks. Assert absence of
   collector Python, bootstrap and launcher files, including stale publish output.
2. Set both units to
   `ExecStart=/usr/lib/lintap/pidstat-collector --collect`, unless PKG-01 explicitly
   approves a different production CLI. Retain root, working directory, environment
   file, restart policy and current enable-without-fresh-install-autostart behavior.
3. Remove collector-bootstrap instructions from install messages and operator docs.
   Preserve Python source/tests as the compatibility oracle; do not remove unrelated
   Python tools, dependencies or operator-owned virtual environments.
4. Remove Python-only knobs (`PIDSTAT_PYTHON`, `PIDSTAT_VENV_DIR`,
   `PIDSTAT_BOOTSTRAP_PYTHON`, bootstrap spec and `PIDSTAT_DUCKDB_THREADS`) from
   shipped configuration and normal operator instructions. Retain relevant Go
   collector knobs; do not fabricate meanings for obsolete settings.
5. Keep this change separate from
   [[wiki/todo/unify-lintap-runtime-and-etl-configuration]]. Preserve conffile and
   `%config(noreplace)` behavior rather than replacing operator settings.

**Gate:** both package inspections find the Go binary/direct unit and no collector
bootstrap requirements; static tests cover staging and unit CLI explicitly.

### PKG-04 — Test greenfield package lifecycle

1. Verify fresh installation stages the Go binary and reloads/enables the units
   under the existing policy, without starting collection before operator review.
2. Test explicit start, stop, restart and Go spool recovery, including conversion
   failure. Retain the single-writer guard and data-preserving removal behavior.
3. Preserve Debian conffile and RPM `%config(noreplace)` handling for later operator
   edits/reinstalls. No automatic venv deletion or unrelated data cleanup.
4. Cover fresh install, reinstall and remove/purge with focused package-script
   regressions. Do not add Python-service migration markers, stop/start handoff
   machinery or downgrade recovery requirements for a nonexistent installed base.

**Gate:** clean package-to-service startup with no bootstrap/downloads, correct
configuration handling and Go restart/recovery. Historical upgrade requirements are
superseded by the human's greenfield scope correction.

### PKG-05 — Package and platform qualification

1. First run in an explicitly approved isolated Ubuntu arm64 VM window. Inspect the
   current VM/service state; do not recreate it or restart shared collectors implicitly.
2. Build/inspect a new Debian artifact, record hashes and test fresh install/start,
   stop and Go restart/recovery on disposable state.
   Run with root's restricted PATH and no runtime downloads or collector subprocesses.
3. Run default 5-second sampling through at least three 300-second rotations plus
   SIGTERM seal. Decode every output, checking all 26 columns, types, nulls,
   local-time partitions, multiplicity and expected recovery output.
4. Complete remaining real Python/Go paired-live comparison with predefined skew
   tolerances and identity-aware unmatched-row accounting. Measure resources without
   inferring improvement from the historical Go-only soak.
5. Run canonical Wintap-PyUtil staging against Go output and the Python compatibility
   reference in isolated databases, without production SQL changes. Mixed old/new
   deployment-input qualification is not a greenfield release gate.
6. Build/inspect RPM and test native x86_64 on the approved RHEL target. Validate
   systemd startup, ABI/static linkage, proc/kernel assumptions, permissions and
   relevant SELinux behavior. Cross-builds are not RPM installation/runtime proof.
7. Qualify remaining architecture/OS cells explicitly or mark them deferred. If a
   format fails its release gate, do not publish that format as qualified.

**Gate:** artifact-specific fresh-install/runtime/consumer evidence reviewed;
human approves release and any explicitly deferred platforms before rollout.

## Files expected to change after authorization

- Lintap Go module release build target/helper and focused tests.
- `../Lintap/packaging/lintap-{deb,rpm}/build-*.sh`, both pidstat units and env comments.
- `../Lintap/tests/` package/service regressions.
- Lintap root/package READMEs, install messages and cleanup guidance.
- This feature's plan, verification and handoff; canonical repo page after acceptance.

## Done checklist

- [x] Current package wiring, topic-ref source location and historical evidence inspected.
- [x] Replacement, architecture and greenfield lifecycle gates planned; legacy migration gates superseded.
- [x] Latest `origin/develop` fetched and Go checkpoint merged into the current Lintap feature branch (`b988aa3`); existing package/provisioning regressions pass 26/26.
- [ ] Go source/ref and integration branch confirmed; prior acceptance gates resolved.
- [x] Release build contract and static architecture checks pass; both builders invoke the shared helper.
- [x] Debian/RPM payload, direct service CLI and docs integrated; Debian arm64 artifact installed in development VM.
- [x] Debian arm64 fresh-install lifecycle, config handling and Go restart/recovery tested; native RPM lifecycle deferred.
- [ ] Ubuntu arm64 package/live and Python/Go consumer gates reviewed.
- [ ] Native RPM target qualification reviewed or explicitly deferred from release.
- [ ] Canonical docs updated and human authorizes publish/deployment.

The original planning round performed no implementation or service operations.
Subsequent authorized integration and arm64 tests are summarized above and in
[[wiki/work/fix-pidstat-collector/verification]]. Preserve unrelated work and evidence.
