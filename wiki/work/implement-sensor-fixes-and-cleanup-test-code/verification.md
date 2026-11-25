---
title: "Verification: Sensor Fixes and Test Cleanup"
type: concept
confidence: medium
grounded_by:
  - ../wintap/tests/Wintap.Tests/README.md
  - ../wintap/developer_docs/audits/sfx-02-process-observation-refresh.md
  - ../wintap/developer_docs/audits/sfx-03-linux-command-line-provenance.md
  - ../wintap/developer_docs/audits/sfx-04-linux-exec-observation-kind.md
  - ../wintap/developer_docs/audits/sfx-05-linux-executable-path-source.md
  - ../wintap/developer_docs/audits/sfx-06-linux-exit-code-status.md
  - ../wintap/developer_docs/audits/sfx-07-linux-stop-observation-timing.md
  - ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md
  - ../wintap/developer_docs/audits/sfx-09-loopback-connection-context.md
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - streamlit/projects/HostActivity/tests/README.md
  - streamlit/projects/SmokeTests/tests/README.md
  - validation/dataset-smoke/README.md
policy: agent-editable
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: wiki/work/implement-sensor-fixes-and-cleanup-test-code; ../wintap/developer_docs/audits; ../Wintap-PyUtil/tests; streamlit/projects; validation
tags: [feature-work, testing, verification, sensor-fixes]
---

# Verification: Sensor Fixes and Test Cleanup

## Packaging SDK follow-up — 2026-11-25

Subsequent build-host prerequisite repair adds shared checksum-verified native
Go 1.27.3 installation to both Multipass launchers before post-create checks.
Existing VMs use the explicit installer without recreation; package/runtime
installation does not invoke it. Post-create checks validate Go and use the shared
stable .NET SDK preflight instead of equating the selected SDK with the minimum.

```sh
uv run pytest -q tests/test_build_go_setup.py tests/test_dotnet_packaging.py tests/test_pidstat_packaging.py tests/test_multipass_provisioning.py
bash -n packaging/install-build-go.sh multipass-lintap.sh multipass-check-dev.sh packaging/dotnet-common.sh
```

**61 passed**; Bash syntax passes. Provisioning failure stops before build/SSH
changes, including Go installation failure. Fake-download installer tests cover both native
architectures, checksum rejection, valid reinstall and preservation of invalid
existing installations. No actual download/guest installation or PowerShell runtime
execution was performed; live provisioning/package qualification remains separate.

Human authorized replacing Lintap's stale exact-10.0.402 guard with stable .NET 10
project resolution. Both builders retain pre-cleanup rejection and .NET 10 runtime
validation. Tests cover stable minimum/newer patches, wrong major, preview and
below-baseline SDKs, invalid baseline policies, caller-directory resolution and
both builders' failure-before-cleanup behavior. Provisioning's installed SDK is
validated against the minimum rather than required to equal it.

From Lintap:

```sh
uv run pytest -q tests/test_dotnet_packaging.py tests/test_pidstat_packaging.py tests/test_multipass_provisioning.py
bash -n packaging/dotnet-common.sh packaging/lintap-deb/build-deb.sh packaging/lintap-rpm/build-rpm.sh
```

**54 passed**; shell syntax passes. SDK tests use fake tools, not native publish
or installed-service evidence. No guest package build/install or SDK installation
performed by this follow-up; native amd64/RPM qualification remains open.
<!-- GROUND_TRUTH: ../Lintap/packaging/dotnet-common.sh; ../Lintap/tests/test_dotnet_packaging.py -->

## Current acceptance boundary

macOS/Linux feature testing is complete; the initial static-only development
boundary is superseded. Native Windows acceptance is separate. The bounded Linux
repeated-exec producer/capture/DBT tranche is complete. Uploader endpoint/fault
qualification, later organization and final release review remain open.

This consolidated record preserves scoped results and important failures from
2026-11-22 through 2026-11-24. No behavioral tests were rerun for the Markdown
review. Private logs, raw telemetry, identities and capture manifests remain
operator-retained; source/audit citations below locate detailed implementation
evidence where available. Earlier commit/transfer status is historical; use latest
feature-branch tips.

## Test organization — 2026-11-22–24

| Gate | Recorded result |
|---|---|
| HostActivity before/after and Linux destination | 59/59 affected cases; normalized identities preserved |
| PyUtil representative before/after and destination | 17 passed; 224 collected identities preserved, disjoint 4 unit / 220 contract |
| Wintap first mechanical slice | Five unchanged test bodies/fixtures, additive traits, source/build-input comparisons pass; 77 classified / 84 focused are expectations, not executed totals |
| Dataset-readiness helper | 18 synthetic budget/refusal controls pass |
| Wintap stdlib event-name parser | 7/7 on Linux |
| Final SmokeTests | 100/100: 86 contracts, 1 loopback transport, 13 UI; each discovered once |

SmokeTests whole-module contract moves progressed through 34, 56, 69, 80 and 85
cases; transport/UI moves preserved assertions and fixtures with path/import-only
adjustments. Remote diagnostics added a UI case (99 total), hourly discovery a
contract case (100 total). Existing non-failing Streamlit warnings were retained.
Loopback transport defaults on with explicit environment opt-out; it is not
Garage/TLS/authorization or cross-host qualification.

Recorded execution entry points (use each README for environment/current scope):

```sh
# From the corresponding app project:
python -B -m unittest discover -s tests -t . -p 'test_*.py'
# SmokeTests also verified legacy project-root discovery:
python -B -m unittest discover -s . -p 'test_*.py' -v
# From Wintap:
python3 -m unittest discover -s devtools -p test_event_name_contracts.py
```

PyUtil destination checks used strict markers, isolated working directory and
explicit source/config paths, disabled plugin autoload/cache/bytecode, and a
119-second subprocess ceiling. All 375 frozen inputs remained unchanged. Collection
is not execution of every case. Initial Wintap cleanup used source comparisons
because its runner was unavailable; later macOS/Linux feature testing supersedes
that overall development limit without establishing native Windows acceptance.

### Environment and readiness failures retained

- PyUtil's original environment lacked a usable interpreter. `uv --no-sync` tried
  recreation and hit permissions; compatible installed interpreters lacked modules.
- Approved isolated locked provisioning first exhausted space during cross-filesystem
  copying. Only session-created partial files were removed; a cache-symlink retry
  succeeded. This local environment is not portable transfer evidence.
- Initial identity checker omitted baseline rootdir and refused pathless identities;
  corrected runner then confirmed all 224 identities. No test/oracle weakened.
- One-time RHEL readiness sample: database readable with external access disabled,
  bounded memory/time/catalog/sample queries; raw directory empty. Input metadata
  unchanged, no WAL. It was not raw-data/DBT correctness and is not a future gate.

## Linux process units — 2026-11-22

Birth `EventTime` and `PidHash` remain unchanged. Additive fields preserve
observation/receipt time and evidence quality. Full command/results and private
artifact lineage belong to Wintap's cited `sfx-*` audits.

| Unit | Focused / cumulative synthetic | Final bounded live checks |
|---|---|---|
| sfx-01/02: name, timing, periodic Refresh | 65/65 cumulative; Windows periodic synthetic 1/1 on Linux | Repaired timing capture 18/18; repeated-exec controls 8/8 |
| sfx-03: command-line source/status | 6/6; cumulative 71/71 | 28/28; cleared-argv children stay empty, no parent substitution |
| sfx-04: attempt versus success | 7/7; cumulative 78/78 | 26/26; repeated fork → attempt → success sequence, null clone/Refresh kinds |
| sfx-05: executable path source | 5/5; cumulative 83/83 | 37/37; evidence precedence and selected path/name preserved |
| sfx-06: exit-code status | 5/5; cumulative 88/88 | Final repaired round 43/43; CO-RE wait status distinguished from fallback placeholder |
| sfx-07: Stop observation timing | 4/4; cumulative 92/92 | 50/50; converted observation equals Stop occurrence, raw timing retained |

Linux non-incremental Release builds had zero errors with existing warnings.
Windows-targeted cross-build also had zero errors; it is compile evidence only.
Repeat stress passed 1,300 Linux/synthetic cases and 30 Linux-hosted Windows
periodic synthetic runs. Capture sensors, scheduled inventories and graceful
shutdown were checked; no gate-owned process remained in final accepted rounds.

### Failures and limits retained

- Initial focused timing rounds failed before the final repair (60 pass/3 fail,
  then 62/1). The first live direct batch converted absent Refresh monotonic time
  to numeric zero. Narrow projection/schema repair preserves nullable INT64 timing
  in both first-row orders; fresh output confirms Refresh null, kernel Start nonzero.
- Broader Linux-hosted `wpc-10` run was **103 pass / 13 fail**, not acceptance:
  replay-overlap/lifecycle expectations and unsupported Windows SID behavior.
- Command-line unit retained a pre-existing first-row optional `Arguments` schema
  omission; source breadcrumbs covered 7/8 repeated-exec cases, other new-field/
  identity/image checks 8/8. Bounded truncation was synthetic, not live coverage.
- First exit-status live round hit absent-resolver null dereferences before Stop
  output. Narrow guard repaired direct mode; intermediate clean Stop output was
  interrupted before periodic acceptance. Final fresh round closed the live gate.
- Optional-string first-row behavior left observation run ID absent in some exit
  controls; consistent where present. Numeric exit values remain raw wait status,
  not decoded shell status or proof of final thread-group death.
- Direct-Parquet diagnostic acceptance does not establish ordinary ETL delivery,
  deployment, historical repair, or native Windows behavior.

## Connection identity — 2026-11-22–23

The suspected duplicate-port call was absent from available v7 history; older
ACME4 lineage remains unproven. Canonical .NET tests cover endpoint reversal,
same-IP/changed-port sensitivity, protocol/context, opposite-host perspective
and same-host client/server. PyUtil removed DBT and legacy hash generation and
preserves producer IDs.

- Initial source-linked Wintap vectors passed 32/32; PyUtil contracts 222/222.
- Refined loopback/public context passed 33/33; focused PyUtil passthrough 78/78;
  selected real DBT network path passed 11/11 nodes and preserved producer IDs.
- Loopback uses host context, non-loopback public context; both gateway identity
  slots empty. Gateways are metadata, not an asymmetric rekeying input.
- Tuple identity is not a unique connection-instance ID. Clean new-data cutover
  is approved; no mixed historical population or migration acceptance is implied.

Private overlapping-network namespace design and native Windows remain separate.
See [[wiki/decision/canonical-five-tuple-connection-identity]] and
[[wiki/tension/private-gateway-connection-identity]].

## Repeated-exec capture and paired-row DBT — 2026-11-23

The operator completed a bounded multi-round Linux workload with one-minute Refresh
and retained normal ETL/manifest/runtime evidence externally. All 19 targeted
identities matched; graceful shutdown reported no remaining queues, drops or
Parquet failures. Raw evidence showed multiple images under one birth-scoped hash;
failed requests had no matching success and preceded successful replacement.

The initial isolated DBT build passed 139/139 nodes but exposed a semantic defect:
independent ANY_VALUE selections could choose a failed image or disagree with the
latest eligible tuple. Repeated-exec latest-tuple agreement was 3/9, failed-then-
successful controls 7/9, Refresh 1/1. Build success alone did not close correctness.

A read-only paired-row prototype selected all targeted cohorts from eligible source
rows, excluded attempts, and stayed identical across ten randomized input-order
runs. Human-approved production repair prefers latest valid Refresh, latest
successful exec, then eligible fallback; name/path/arguments remain from one row.
Selected evidence role/timing are exposed; raw history and birth aggregates remain.

| Final gate | Result |
|---|---|
| Focused PyUtil contracts | 32 passed, 1 existing skip |
| Isolated finalized-capture DBT | 139/139 nodes, no errors/warnings/skips |
| Legacy raw-schema staging/model | 13/13 |
| Targeted paired fields | 19/19; no selected attempt or failed executable |

No production/historical data rewritten. Explicit as-of/freshness/ambiguity,
non-image ANY_VALUE and native Windows negative controls remain separate. Linux
input still receives hard-coded downstream `os_family='windows'`; that limitation
is not producer evidence. See [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/any-value-audit]].

## S3 dashboard discovery and diagnostics — 2026-11-24

Startup discovers only hourly `raw_smoke_test` evidence; telemetry discovery waits
for explicit run/round validation and uses selector event families and canonical
host filename filtering. Windows/uv guidance selects Python 3.13 with requirements,
not `uv sync`. Remote errors show stage/class and next checks, never raw private
exception text. Upload-hour windows do not derive from event occurrence time.

Recorded checks: focused source/UI 27/27, final full app 100/100; compilation and
diff checks pass. Authorized read-only configured source/evidence loading and
default-page AppTest completed without exceptions or evidence warnings.
Subsequent operator-selected telemetry validation completed 17 cases with **yellow
quality results**, not infrastructure failure or blanket sensor acceptance.

Earlier listing and memory caps failed closed. Hour/event/host pruning reduced
the read scope; checked-in defaults are now 20,000 files and 4 GB, disk spill off.
Prefer narrowing scope to unlimited budget increases. Dashboard read success does
not qualify uploader faults, TLS/authorization matrices or all browser workflows.

## S3 uploader and SDK — 2026-11-24

Shared S3 UTC upload-partition and durable unresolved-attempt binding is implemented.
Focused tests passed 8/8 and Lintap build had zero errors. Tests cover UTC boundaries,
source identity, matching exact-key HEAD, authoritative-miss rebinding,
inconclusive-HEAD exact-key retry and cleanup. No live endpoint in that unit;
authorized ambiguous PUT/HEAD fault qualification remains open.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/base/S3UploadAttemptBinding.cs; ../wintap/tests/Wintap.Tests/S3UploadAttemptBindingTests.cs -->

Stable .NET 10 policy is implemented: minimum 10.0.100, `latestMinor`, no prereleases.
Record actual SDK. Historical 10.0.402 builds remain dated evidence; Lintap's exact
package SDK gate is separate. macOS/Linux completion does not imply native Windows.

## Supporting provisioning/package checks — 2026-11-23–24

Bash Multipass repair retained uv environment creation, used pinned pip installs
with bounded retries, bounded cloud-init diagnostics and avoided recursively
re-owning host-mounted data. Full Ubuntu arm64 dependency/eBPF gate and 26 focused
provisioning/package checks passed. Earlier beta.1 package passed payload/native/
maintainer-script inspection only; no install acceptance at that checkpoint.
Later beta.2 Go integration/install/rotation/recovery evidence is maintained in
[[wiki/work/fix-pidstat-collector/verification]], not inferred from beta.1.

## Remaining gates

- Native Windows build, discovery, filtering and execution with stable .NET 10.
- Authorized S3 uploader endpoint/fault matrix and final human release review.
- Remaining organization only as individually selected; no evidence deletion.
- Separate future work described in the current plan/handoff; no historical repair
  or broader platform/consumer acceptance inferred from this record.
