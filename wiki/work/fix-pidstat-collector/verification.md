---
title: "Verification: Fix pidstat Collector"
type: concept
confidence: medium
grounded_by:
  - ../Lintap/pidstat-collector.py
  - ../Lintap/pidstat-go/collector.go
  - ../Lintap/pidstat-go/collector_test.go
  - ../Lintap/pidstat-go/schema.go
  - ../Lintap/packaging/pidstat-common.sh
  - ../Lintap/tests/test_pidstat_packaging.py
  - validation/pidstat-loop/check_sampler.py
  - validation/pidstat-loop/check_spool.py
  - validation/pidstat-loop/check_native_spool.py
  - ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_pidstat_metrics.sql
policy: agent-editable
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: mixed
status: draft
source_paths: ../Lintap/pidstat-go; ../Lintap/packaging; validation/pidstat-loop
tags: [feature-work, pidstat, verification, go]
---

# Verification: Fix pidstat Collector

## Current checkpoint — 2026-11-24

Static Go packaging is integrated and pushed (Lintap `4c280b0`, Analytics `96db9b8`)
on `feature/implement-sensor-fixes-and-cleanup-test-code`. Greenfield deployment is
human-confirmed; no Python-installed-base migration/downgrade gate is required.
Debian arm64 build/install/reinstall/default rotation/crash recovery pass. Development
package remains installed/enabled, both development services stopped. Ubuntu amd64
and native RPM qualification are delegated to other host types, not passed here.

This consolidated record preserves scoped results, repair failures and remaining
gates. Detailed argv/logs/input/binary/hash manifests stay in ignored private
`validation/pidstat-loop/evidence/` and operator-retained temporary storage; no raw
host/account/IP identifiers or detailed capture inventory is persisted here.
Markdown review did not rerun behavioral tests.

## Evidence gates

| Gate | Status |
|---|---|
| fpc-01 writer/schema/static spike | Technical pass; human accepted 2026-10-30 |
| fpc-02 sampler/config/raw replay | Candidate 3 technical pass; human accepted |
| fpc-03 durable spool/recovery | Candidate 3 technical pass; human acceptance unrecorded |
| Four-hour default-cadence soak | Same-session technical pass, not independent/human acceptance |
| PKG-02/03 release build/integration | Both static architectures and builder regressions pass |
| PKG-04/05 Debian arm64 lifecycle | Install/reinstall/rotation/shutdown/recovery pass |
| Paired-live Python/Go/resources | Open; exact replay is not paired-live proof |
| Canonical DBT consumer qualification | Open |
| Native Ubuntu amd64/RPM | Deferred/unqualified |
| Dependency/license/security/release review | Open |

## Historical rewrite evidence — 2026-10-30–31

Reference source remained unchanged at Lintap `b229a597977a2ce04820fffd86574a63f658cfcf`;
Python SHA-256 `3722ef80c87e226a3c0491f9daff34f4cc8bddfba0d1589cf33052aef6e797c5`.
Actual Python produced golden Parquet/TSV from captured real proc inputs; comparators
checked all 26 columns, physical/DuckDB schema, values/nulls, multiplicity,
partitions/windows and unmatched rows. Go 1.27.3 / parquet-go 0.32.0 were pinned;
CGO disabled and local toolchain required. Native first target was Ubuntu arm64.

### fpc-01 — writer spike

One candidate passed actual Python comparisons for three captured datasets
(266 / 705 / 1,640 rows), zero mismatches/unmatched rows. Five controlled writer
edge rows covered Unicode, null text, duplicate rows, widths, rounding and midnight
windows. Five Go tests, vet/modules, both static ELF builds and 19 utility controls
passed; native arm64 encoding matched Python. No interpreter/DT_NEEDED linkage.

Schema contract: 26 OPTIONAL physical fields; naive TIMESTAMP_MICROS,
signed INTEGER/BIGINT, FLOAT rates and UTF8 strings. Parquet bytes need not match;
decoded values did. Live uncached reads and container IDs were not covered.
This was writer-only, not sampler/spool/production proof.

### fpc-02 — sampler/configuration

Candidate 3 passed identical-real-input replay for all three datasets, including
native arm64 replay. Actual Python controlled differentials covered two kernel
tick/page contexts (52 rows each), PID reuse, CPU/memory/I/O/reset/cgroup/namespace
behavior, and 17 configuration cases. Four-sample native readability, kernel-context
discovery, 14 Go tests/vet/modules/static builds and 19 utility controls passed.

Retained failures: configuration parity and rounded-midnight source-window membership
required candidates 2/3; final replay preserves source epoch independently of rounded
row timestamp. No fourth revision or comparator relaxation. Differences recorded:
malformed optional counters skip a Go process versus Python exception; exited/reused
cache entries evict in Go; live scheduling uses monotonic time, replay Python elapsed
clamp; Go config uses signed-64 bounds. Invalid UTF8/live container/uncached-read and
paired-live coverage remained open.

### fpc-03 — durability and recovery

Candidate 3 passed 26 host/native Go tests, durable replay for all real datasets,
actual Python spool recovery (valid/missing/invalid metadata and multiple pending
files), eight accepted codec spellings, sampler/config/writer/utility regressions.
Native SIGTERM/SIGINT sealed readable output; SIGKILL recovered retained spool;
second same-spool writer refused; obstructed conversion retained input and retried.

Retained repairs/failures:

- Candidate 1: obsolete CLI-warning assertion and extra collision suffix failed;
  retained comparator required compatible filename allocation.
- Codec fixture case collisions on macOS were harness failures; indexed directories
  fixed them. An empty-stdin probe was not evidence.
- Self-review found cross-spool shared-output active-file ownership race. Candidate 3
  reserves unique active paths and uses inode/hash publication recognition, preserving
  independent identical rows. All three revision slots used; extra repair needs approval.
- Original host pytest runner unavailable; actual Python method differentials and
  Go tests passed, but no original pytest pass inferred.

Guarantee limits: tested process-crash transitions do not prove power-loss/network-
filesystem persistence or end-to-end exactly-once delivery. Uploader removal before
durable receipt can replay a delivered window. Python does not honor Go spool locks
or journals; never share an active spool. Missing metadata cannot recover lost source
epoch/fold precision. Strict incomplete-tail rejection, early invalid-codec failure,
nonzero failed-recovery exit and uncapped failed spools are deliberate differences.
See [[wiki/tension/pidstat-publication-versus-uploader-receipts]].

### Four-hour sensor-on soak

Default 5s sampling / 300s rotations completed without restart/early death; every
output decoded with exact 26-column reference schema, continuous cadence, correct
local windows and no observed cross-file duplicate identity/time groups. Clean
shutdown left only the spool lock. Generated sensor smoke evidence was readable;
stimulus completion is not completeness/delivery acceptance.

Independent periodic observations measured Go median about 0.47% of one core and
17 MiB RSS, no observed child processes. This is Go-only resource evidence, not
Python comparison or exhaustive short-lived-child tracing. Live container IDs were
absent. Sensor findings retained: partial arm64 file hooks, absent SELinux, disabled
adapter resolution error, expected plugin/UI warnings and unknown-parent warning.
Zero reported drop/backlog counters do not prove uninstrumented completeness.

Archive transfer first failed because its private parent was not traversable;
test-owned copy fixed retrieval without relaxing original permissions. Read-only
decoded query first failed on parameterized CREATE VIEW; relation API retry passed.
Neither repair changed collector, thresholds or budgets. Human fpc-03/soak acceptance
remained open; later packaging authorization supersedes the old packaging hold.

## Package integration — 2026-11-24

Authorized develop merge `b988aa3` brought the module into the feature branch.
Release helper/builders stage `/usr/lib/lintap/pidstat-collector` and hash manifest,
remove Python collector/bootstrap/launcher from copied publish payloads, and directly
execute `--collect`. Go is build-host-only; runtime needs no Python/uv/DuckDB/sysstat/
Go bootstrap. Operator virtual environments and configuration protections remain.

Recorded commands from Lintap (actual toolchain/cache/output paths private):

```sh
make -C pidstat-go test build GO=<verified-go>
uv run pytest -q tests/test_pidstat_packaging.py tests/test_multipass_provisioning.py tests/test_dotnet_packaging.py
```

Latest focused package/provisioning run: **45 passed** (19 pidstat packaging cases).
Native arm64 Go: **27 tests**, vet and module verification pass. Both architecture
release binaries have correct static ELF machine/no interpreter/shared dependency.

Repairs/setup failures: first builder used workspace root instead of Lintap module
path; corrected to script-relative module path and added regression. Guest Go proxy
TLS failed; checksum-verified module cache enabled offline build. Temporary toolchain
extraction/version failures were setup failures, not Go test passes. No pin relaxed.

Debian artifact `lintap_7.0.1~beta.2-1_arm64.deb`, SHA-256
`7822ae95ade46dda2369d80273564667deea10e89dcfe66d0bf18b767663ca62`.
Built with `--skip-mcp`; MCP integration not qualified. Payload/unit/static checks
pass. Optional .NET diagnostic-provider warning retained. Initial raw dpkg install
left package unconfigured for declared LTTng dependency; native package-manager
dependency resolution completed installation. Enabled, not auto-started.

## Installed arm64 lifecycle

Explicit startup uses installed Go executable under restricted root PATH; systemd
unit verification passes. Default run crossed three rotation boundaries at exact
5s cadence, zero restarts, and sealed successfully on SIGTERM. Every file decoded
with the 26 raw fields (Hive inference disabled), optional types/null semantics,
local partitions and single epoch-window membership. Container fields null for
this non-container workload. No raw identifier values copied.

Modified-config reinstall preserved bytes and did not auto-start. Clean-spool
`--recover` succeeded; forced SIGKILL/automatic restart then graceful stop produced
readable pre-crash/restart output with no active/partial remnants, only spool lock.
This is scoped recovery, not exactly-once/power-loss qualification. Initial inspection
used wrong filename delimiter and failed before validation; corrected decoded-time
inspection passed without modifying output or oracle.

Reference-suite run on macOS: **55 pass / 3 fail / 2 skip**; failures were two
runtime-root permission cases and absent Linux procfs. Guest reference setup failed
on unrelated Streamlit dependency download. Preserve those failures; rerun on Linux
with working dependencies before claiming full reference-suite acceptance.

## Next qualification

Use [[wiki/work/fix-pidstat-collector/dev_handoff]] for native commands and
[[wiki/work/fix-pidstat-collector/packaging_plan]] for greenfield gates. Complete
paired-live identity-aware Python/Go comparison/resources, canonical DBT staging,
native Ubuntu amd64/RPM cells and explicit human/release review. Operator-reported
RHEL execution is not inspected native package evidence. Do not modify consumer
SQL or compatibility tolerances to hide differences.
