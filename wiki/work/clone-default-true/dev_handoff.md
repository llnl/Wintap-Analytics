---
title: "Dev handoff: RHEL Clone default-TRUE acceptance"
type: concept
confidence: high
grounded_by:
  - ../Lintap/packaging/README.md
  - ../Lintap/packaging/lintap-rpm/build-rpm.sh
  - ../Lintap/packaging/lintap-rpm/lintap.env
  - ../wintap/devtools/validate_clone_package.py
  - ../wintap/devtools/validate_clone_trace.py
  - wiki/schema/runtime-capability-receipt.md
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: packaging
event_domain: process
audience: developer
status: draft
source_paths: ../Lintap/packaging; ../wintap/devtools
tags: [dev-handoff, rhel, clone, package-acceptance, runtime-capabilities]
---

# Dev handoff: RHEL Clone default-TRUE acceptance

**RHEL validation is pending and must be performed elsewhere.** This handoff
does not certify RHEL support from Ubuntu results. Current source changes enable
Clone in Debian/RPM package env files, retain explicit opt-out, require the new
Clone CO-RE object in native/BTF package validation, and log fallback classification
risks. Wintap owns sensor/ETL/harness implementation; Lintap owns packages;
Analytics owns acceptance records. Work remains on open feature branches.

## Agent prompt / scope

On a designated **disposable RHEL x86_64 test host**, validate a freshly built RPM
from the exact Wintap and Lintap revisions containing Clone CO-RE and HOST receipt
changes. Read repo AGENTS.md, `../Lintap/packaging/README.md`,
[[wiki/schema/runtime-capability-receipt]],
[[wiki/work/improve-lintap-data-quality/clone-validation-results]], and
[[wiki/work/clone-default-true/verification]]. Do not reset unrelated changes or
disable security controls. Obtain explicit approval before touching an active
collector, changing system policies, installing on a shared host or modifying
source beyond an evidence-supported fix. Record failures rather than silently
making the test environment easier.

## 1. Capture environment and build fresh

Record `/etc/os-release`, `uname -r`, `uname -m`, CPU/memory, libbpf package/version,
SELinux mode, `kernel.perf_event_paranoid`, service restrictions, readable target
BTF, compiler/bpftool versions, both git HEADs and dirty diff hashes. Current
Ubuntu work is uncommitted: HEAD alone is insufficient provenance. Do not use
an older package that lacks the fixes. Build natively on RHEL 8-compatible
x86_64 with BTF (the RPM builder's current contract); no cross-build shortcut.

From the parent containing `Lintap/` and `wintap/`, choose a new release number:

```bash
bash Lintap/packaging/lintap-rpm/build-rpm.sh \
  --version 0.1.0 --release 104.el8 --arch x86_64 --runtime linux-x64 --skip-mcp
rpm -qpi artifacts/lintap-rpm/x86_64/lintap-0.1.0-104.el8.x86_64.rpm
rpm -qpl artifacts/lintap-rpm/x86_64/lintap-0.1.0-104.el8.x86_64.rpm
rpm -qp --requires artifacts/lintap-rpm/x86_64/lintap-0.1.0-104.el8.x86_64.rpm
sha256sum artifacts/lintap-rpm/x86_64/lintap-0.1.0-104.el8.x86_64.rpm
```

Require `clone_core_tracer.bpf.o` **and** `clone_tracer.bpf.o`; exclude foreign-OS
native libraries, FUSE files and build metadata. Block glibc requirements newer
than RHEL 8's 2.28. RPM retains `WINTAP_PARQUET_COMPRESSION=Uncompressed` for the
Parquet.Net native writer; verify immediate HOST publication also works through
DuckDB's final materialization. `--skip-mcp` means this acceptance does not cover MCP.

## 2. Install on clean target; default-on normal capture

For a quick manual cross-domain stimulus during capture, also run the Python
[[wiki/tool/named-telemetry-smoke-workload]]. Its manifest isolates process/file/
network cases; generated workload alone is not proof of sensor collection.

```bash
sudo dnf install ./artifacts/lintap-rpm/x86_64/lintap-0.1.0-104.el8.x86_64.rpm
rpm -q lintap
systemctl cat lintap
grep -E '^(WINTAP_.*)=' /etc/lintap/lintap.env
test -f /usr/lib/lintap/tracers/clone_core_tracer.bpf.o
test -f /usr/lib/lintap/tracers/clone_tracer.bpf.o
```

Do not add a Clone=true drop-in, shell override or diagnostic bypass. Default
package env must be true. Keep normal ETL, process registration/resolution and
Esper enabled; direct output must be false. Do not start pidstat unless required
by a separately agreed workload. Verify no unexpected service drop-ins/configs.

Provision Python `duckdb` in a native virtualenv plus C compiler on the test host
(Python version/wheel availability on RHEL may require a separately approved
tooling environment). Build the manifest workload:

```bash
cc -O2 -pthread -o /native/clone-workload wintap/devtools/clone_lifecycle_workload.c
sudo /native/qa-venv/bin/python wintap/devtools/validate_clone_package.py \
  --workload /native/clone-workload --output /native/qa/rhel-clone-default
```

Harness expects an **idle lintap.service**, standard env/data/runtime paths and
CO-RE tier. It starts/stops the service, waits the default 320 seconds per
normal capture for merging, temporarily edits only Clone=true→false for opt-out,
and restores the original env in `finally`. It intentionally fails if the default
selects fallback: investigate/classify that result, do not relabel it CO-RE.
For custom roots supply `--data`/`--runtime`; the service env must already agree.
Run harnesses sequentially; app API port can be fixed despite ASPNETCORE_URLS.

### Acceptance gates

- Fresh HOST receipt is published immediately into `raw_sensor/raw_host`; JSON
  equals final `RUNTIME_CAPABILITIES` log, correct kernel/platform/architecture,
  Clone=true source is package env, CO-RE object/hash and fork hook are recorded.
- Default normal pipeline captures all supported manifest process births,
  excludes every thread TID and assigns worker-fork parent **TGID**, not worker TID.
  Full clone3 support yields 80 process/60 thread cases per 20-round manifest.
  Unsupported clone3 must be explicit SKIP, not silently counted as zero activity.
- Successful fork+exec produces multiple Start observations; report counts and
  PidHash identity splits rather than assuming exactly two or deduplicating raw rows.
- The 100-round bounded workload exercises 400 processes/300 threads when clone3
  works. Check ring/sender/serializer/writer/merge errors and queue growth; no
  new measured drops. This is a bounded churn check, **not** maximal fork-storm
  or long-running PID-reuse certification. Record CPU/RSS during the run and
  compare a same-host opt-out run if claiming incremental overhead.
- Restart preserves prior HOST/history and gets a new run ID. Explicit opt-out
  reports Clone disabled, other sensors continue, fork-only births disappear and
  exec births remain. Restore true afterward; stop the test service before handoff.
- Check emitted file/network rows and lifecycle joins where tested; do not treat
  process-only gates as complete cross-domain/DBT acceptance.

## 3. Fallback and negative attach cases

Do not remove objects from the installed service payload. On an idle target,
stage a **separate native copied app** excluding all CO-RE objects and run the
receipt harness `validate_runtime_capabilities.py --dll /native/full/Lintap.dll
--fallback-dll /native/fallback/Lintap.dll --output /native/qa/receipts` using an
approved .NET runtime. This harness uses direct output/ETL bypass and is not the
normal-pipeline gate above. Confirm fallback warning `CLONE_DATA_QUALITY`, selected
object/tier and flags hook outcomes in HOST. Full hooks do not prove every user
flag read succeeds. Missing vfork hook alone may be architecture-specific.

Actual-object tracer checks, with libbpf-devel available:

```bash
cc -O2 -o /native/clone-runner wintap/devtools/clone_trace_runner.c -lbpf
sudo python3 wintap/devtools/validate_clone_trace.py \
  --object /usr/lib/lintap/tracers/clone_core_tracer.bpf.o \
  --runner /native/clone-runner --workload /native/clone-workload --output /native/qa/core
sudo python3 wintap/devtools/validate_clone_trace.py \
  --object /usr/lib/lintap/tracers/clone_tracer.bpf.o \
  --runner /native/clone-runner --workload /native/clone-workload --output /native/qa/fallback
sudo python3 wintap/devtools/validate_clone_trace.py \
  --object /usr/lib/lintap/tracers/clone_tracer.bpf.o \
  --runner /native/clone-runner --workload /native/clone-workload --output /native/qa/no-flags --primary-only
```

Last command is an **expected data-quality failure**: with no flags hooks all
thread births can be falsely accepted (Ubuntu: 60/60). Save report and nonzero
exit status. Do not “fix” the test to accept it as good process classification.
Failing primary attach must leave Clone unregistered/failed in HOST while other
sensors continue. Preserve logs/errno and required capabilities; do not infer
the Fedora historical EACCES cause or globally disable SELinux/lockdown.

## 4. Upgrade/config preservation and deliverables

On a separate designated upgrade test, preserve a locally opted-out env file and
upgrade. Confirm administrator false survives (RPM may create `.rpmnew`); default
TRUE applies to fresh installs, not an authorization to overwrite opt-outs.

Return package hash/build logs, environment inventory, package env and drop-ins,
HOST/parquet receipts, manifest/report JSON, runtime/service logs, measured loss
counters, resource samples, supported/unsupported hooks, clone3 skips, and normal
pipeline/opt-out/restart/fallback outcome table. Sanitize secrets and do not copy
live source into raw/. Append results to
[[wiki/work/clone-default-true/verification]] and update its pending RHEL checklist.
If RHEL 8 lacks required raw-tracepoint/BTF/helper capabilities, explicitly record
fallback or attach failure as a distinct capability regime; do not retroactively
claim the Ubuntu CO-RE result applies.
