---
title: "Dev Handoff: Fix pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../Lintap/tests/test_pidstat_collector.py
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-11-24
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: llm-agent
status: draft
source_paths: wiki/work/fix-pidstat-collector/dev_handoff.md
tags: [feature-work, handoff, pidstat, go, engineering-loop]
---

# Dev Handoff: Fix pidstat Collector

## New packaging plan — 2026-11-24

**Completed follow-up:** arm64 default run and config-preserving reinstall pass;
installed crash/restart recovery produces readable output. Six files total, 26,408
rows; default-run subset four files/25,999 rows with 5s cadence and three rotation
boundaries. Both development services stopped; package remains installed/enabled.
Next qualification gaps: consumer/paired-live and other native platforms.

Go payload/units/docs are integrated. Debian arm64 7.0.1~beta.2-1 remains installed
in the development VM. Both services are stopped; no follow-up run remains scheduled.

**Current deployment scope:** greenfield, explicitly confirmed by the human.
No Python-installed-base migration, active upgrade handoff or Go-to-Python downgrade
machinery is required. Next unit is native Ubuntu amd64 and RPM qualification.
Retain config protections, Go recovery and compatibility tests;
historical migration tasks below are superseded for this deployment.

Read [[wiki/work/fix-pidstat-collector/packaging_plan]] before continuation. The
packaging branch now contains the module after the authorized `origin/develop`
merge (`b988aa3`, incorporating `053b2b5`). Build-host Go 1.27.3 and both static
architectures pass. The human authorized implementation and development-VM install/
service tests, and now commits for cross-host testing. No push or field rollout
authorized initially; the human subsequently authorized pushing both feature branches
for cross-host testing. Field rollout remains outside scope. Historical acceptance
remains open.

## Cross-host testing handoff

Branch in both repositories: `feature/implement-sensor-fixes-and-cleanup-test-code`.
Lintap implementation commit: **`4c280b0`**, following develop merge `b988aa3`.
Lintap owns collector/build/package code; Analytics owns these feature records.
Use the committed changes from both repos when moving to another test host.
Do not treat a static cross-build as native runtime qualification.

### Completed here

- 45 focused package/provisioning regressions and 27 native Go tests, vet and
  module verification pass. Both architecture-matched static release binaries pass
  ELF checks (no interpreter/shared dependencies).
- Debian arm64 build, fresh install, enabled-without-autostart, direct Go startup,
  three 300s rotation boundaries at 5s cadence, SIGTERM seal, modified-config
  reinstall and SIGKILL/automatic-restart recovery tested.
- Six files decode, 26,408 rows. Default-run subset: 25,999 rows/199 timestamps,
  exact 26-column types/nulls/local partitions. This is not paired-live parity.
- Artifact `../artifacts/lintap-deb/lintap_7.0.1~beta.2-1_arm64.deb`, SHA-256
  `7822ae95ade46dda2369d80273564667deea10e89dcfe66d0bf18b767663ca62`.
  This build used `--skip-mcp`; MCP integration is not qualified by it.

### Commands on the next native host

Install/select pinned Go 1.27.3 on the **build host**, plus the package guide's
SDK/native build prerequisites. The SDK pin is 10.0.402. Set `GO` to the executable
when it is not on PATH. Build with native temporary work roots; do not reuse arm64
publish output on amd64. Confirm repo paths/project selection before running:

```sh
export GO=/path/to/go1.27.3/bin/go
make -C pidstat-go test build
uv run pytest -q tests/test_pidstat_packaging.py tests/test_dotnet_packaging.py tests/test_multipass_provisioning.py

# Native Ubuntu amd64 (from Lintap checkout):
bash packaging/lintap-deb/build-deb.sh --version 7.0.1~beta.2 --arch amd64 --runtime linux-x64 --skip-mcp --work-root /var/tmp/lintap-go-deb-test

# Native approved RHEL/RPM x86_64 host (from Lintap checkout):
bash packaging/lintap-rpm/build-rpm.sh --version 7.0.1 --release beta.2.el8 --arch x86_64 --runtime linux-x64 --skip-mcp --work-root /var/tmp/lintap-go-rpm-test
```

Use test versions above only if appropriate for the target's release policy;
record the actual version, source commits and hashes. Follow
`../Lintap/packaging/README.md` for prerequisite and install instructions. On a
disposable target, install using the native package manager with dependency
resolution, review `/etc/lintap/lintap.env`, then explicitly start pidstat. Go service
startup must not need Python, uv, DuckDB, sysstat, Go or bootstrap downloads.

### Required evidence on each platform

1. Inspect payload/unit/env and static ELF architecture; no collector Python or
   launcher/bootstrap files. Verify `ExecStart` includes `--collect`.
2. Fresh-install policy: enabled but not auto-started; restricted-root-PATH startup.
3. Default 5s/300s run across three boundaries plus graceful seal. Decode **every**
   output, 26 raw columns/types/nulls, local partitions/window membership/cadence.
   Disable DuckDB hive inference when counting raw columns.
4. Modified-config reinstall with byte-for-byte preservation, Go stop/restart,
   crash/spool recovery and absence of partial output/duplicate collectors. Preserve
   data; no legacy Python migration requirements.
5. Native RPM: record OS/kernel/ABI, permission and SELinux observations. State exact
   RHEL release tested, not blanket RPM/RHEL support.
6. Update [[wiki/work/fix-pidstat-collector/verification]] and plan done checklist
   with failures as well as passes; redact actual host/account/IP identifiers.

### Remaining gaps and known setup issues

- Ubuntu amd64 and native RPM runtime/install cells are **not tested here**.
- Paired-live Python/Go comparison with predefined tolerances and identity-aware
  accounting, comparative resources and canonical Wintap-PyUtil staging remain open.
  Do not change consumer SQL or thresholds to conceal incompatibilities.
- Historical fpc-03/soak human acceptance and release dependency/license/security
  review remain unrecorded. Windows support was discussed only; no implementation
  or feature authorization arose from that planning question.
- Host Python reference suite has three macOS-specific failures (runtime-root
  permissions and absent `/proc`). Linux reference-suite setup hit unrelated
  Streamlit dependency download timeouts; rerun on Linux with working dependencies.
- Guest Go proxy TLS timeouts were bypassed with a checksum-verified host module
  cache and offline `GOPROXY=off`; pin/module checks were not relaxed.
- Raw `dpkg -i` required existing declared LTTng dependencies to be resolved.
  Build inspection emitted the known optional .NET diagnostic-provider warning.

## Historical rewrite checkpoints (not current packaging instructions)

The sections below retain earlier rewrite evidence and approval history. Their
old packaging prohibitions and missing-toolchain status are superseded by the
authorized implementation and successful tests above; acceptance gaps remain.

## Status / Authorization Gate

fpc-01 and fpc-02 are human-approved; **fpc-03 durable spool/recovery technical checks
complete; human review/acceptance pending**, candidate3of3 under the unit budget
beginning21:52PDT. Original host pytest runner is missing; not counted as PASS.
Scoped Lintap edits and isolated Ubuntu arm64 guest work were explicitly
approved. The human subsequently authorized topic commits on
`work/pidstat-and-dbt-validation`; packaging/service changes and agent deployment
remain outside this authorization.
Read [[wiki/work/fix-pidstat-collector/verification]] and inspect actual datasets and
source diffs before proceeding. fpc-03 used all3 candidate revisions; further repair
requires explicit budget extension. Do not start packaging/service work under this
authorization. Read the guarantee/rollback limits and uploader-receipt tension.
Use `validation/pidstat-loop/README.md` and [[wiki/tool/pidstat-implementation-loop]].
Canonical consumer `../Wintap-PyUtil` received separate authorization for the
source-aware local/S3 preflight, documented in
[[wiki/work/dbt-source-validation/verification]]. That change is not a pidstat
compatibility workaround or canonical real-host DBT qualification.

**Four-hour run completed and technically reviewed:** default5s/300s sensor-on
`lintap-dev`,2026-10-31T05:18:50Z–09:18:50Z; all processes stopped cleanly.
49pidstat files/399312rows,2880uninterrupted5s sample times, exact26-column schema,
80/80smoke generations, measured Go median0.47%one-coreCPU/~17MiB RSS. Read
[[wiki/work/fix-pidstat-collector/soak_review]] and the latest verification entry.
Local evidence: `validation/pidstat-loop/evidence/four-hour-20261031T0520/`;
guest originals: `/var/tmp/pidstat-four-hour-20261031T0520`. Private archive-copy
transfer fixed SFTP parent permissions without relaxing original evidence access.
Do not reset the root, restart this completed test or delete evidence. Retain
startup-harness, incidental shared NuGet restore and sensor coverage findings.
Same-session technical collection pass, **not human acceptance**; packaging remains
blocked. Paired-live Python, comparative resources, DBT and platform gates remain.

## Review Now; Historical Start Prompt Below

Open a new Analytics session and run `/pidstat-review fpc-03; inspect source and
evidence recorded in wiki/work/fix-pidstat-collector/verification.md`. Record human
decision before any fpc-04 work; same-session inspection is not independent review.

Start with `/pidstat-loop fpc-01: prove static binaries and actual Python/Go
Parquet compatibility; stop for human review`. The command loads the skill in the
current Build session. The following supplies the full scope if needed:

> Implement the compatibility-preserving Go pidstat rewrite using
> `wiki/work/fix-pidstat-collector/brief.md` and `implementation_plan.md`.
> Read applicable repository instructions and `verification.md` first. The first
> live target is the existing Multipass lintap-dev, Ubuntu arm64; do not recreate
> it or infer RHEL 8 proof. Work only within the expressly approved Lintap collector,
> build/test/package/docs scope plus Analytics wiki records. Preserve unrelated work,
> services, environments and telemetry. Start with fpc-01: freeze actual Python
> output and demonstrate pure-Go Parquet compatibility and static arm64/amd64 builds.
> Preserve and execute the existing Python reference through final review. Require
> exact replay parity on identical captured real /proc inputs and a paired-live
> comparison with predefined timing tolerances. Review actual results from both
> versions, every column, row multiplicity and unmatched rows; synthetic fixtures
> alone are not acceptance. Use ../Wintap-PyUtil for canonical downstream checks.
> Pause for review of the spike before the full port. No uv/Python/DuckDB/cgo runtime
> dependency, no child sampler/converter, no production downstream changes to hide
> incompatibilities. Follow the native pidstat-loop skill: three candidate revisions
> or 60 minutes per requested unit unless explicitly changed. Use evidence.py for
> deterministic evidence, not an external controller. Confirm permissions first.
> Record commands/results/findings after each unit, rerun affected and cumulative
> gates, and escalate rather than weaken compatibility tests. No field rollout,
> source deletion outside reviewed scope, commit/push/merge/release without approval.

## Required Context

- [[wiki/work/fix-pidstat-collector/brief]]
- [[wiki/work/fix-pidstat-collector/implementation_plan]]
- [[wiki/work/fix-pidstat-collector/verification]]
- `../Lintap/pidstat-collector.py`, bootstrap/launcher, collector tests.
- Both package builders/units/env files, canonical packaging guide, applicable AGENTS.md.
- [[wiki/concept/lintap-cpu-unit-conventions]], [[wiki/repo/lintap-supporting-repo]].
- Historical [[wiki/work/improve-pidstat-collector/design]]; current source wins over
  obsolete historical runtime/deployment details.
- Read `../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql` and shared
  `macros/{paths,raw_sources}.sql`. Wintappy's checkout was renamed to Wintap-PyUtil;
  the canonical source location is resolved.

## Deferred Decisions

Go1.27.3, parquet-go0.32.0/pure-Go ZSTD and `../Lintap/pidstat-go` are the spike's
tested initial choices accepted at fpc-01; release license/security review is pending.
The Python reference is unchanged and hash-pinned in verification.md. Sampler/config
raw replay and durable recovery checks now pass. The default-cadence four-hour
resource observation is complete; comparative resources, paired-live,
DBT and inspected native RHEL/amd64 qualification remain pending. The operator
reports successful RHEL execution, not yet inspected native evidence. Review fpc-03
evidence/blocked pytest runner and authorize the next unit; use `/pidstat-review`
in a manually opened new session for fresh review. Human velocity
estimates were not collected in this planning session; do not invent retrospective
sealed values or read future sealed estimates before independent estimating.
