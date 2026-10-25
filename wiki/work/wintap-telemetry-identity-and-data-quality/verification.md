---
title: "Verification summary: telemetry identity and end-to-end data quality"
type: diagnostic
confidence: high
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
  - ../wintap/tests/Wintap.Tests/IdentityContractTests.cs
  - ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs
  - ../Wintappy/tests/test_filetime_precision_sql.py
  - ../Lintap/tests/test_dotnet_packaging.py
  - ../wintap/devtools/test_runtime_alignment.py
  - ../wintap/devtools/process_capture_smoke_test.py
  - ../wintap/devtools/file_capture_smoke_test.py
  - ../wintap/devtools/network_endpoint_smoke_test.py
  - ../Wintappy/wintap_dbt/profiles.yml
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: ../wintap/tests; ../Wintappy/tests; wiki/work
tags: [feature-work, retrospective, verification, proof, limits]
---

# Outcome

## Authorized local quality follow-up — 2026-10-25

[[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]]
records source-controlled Accept/UDP return corrections and stronger Analytics
assertions. Final VM verification:93 dashboard/17 runner/12 Wintap Python tests,
159 shared managed tests, all12 tracer builds and repeated15-check actual-object
pass versus original-object failure. Normal-ETL five-family round delivers evidence
and saves/reloads local summary with zero analysis errors; Accept and independent UDP
endpoints observed. Exact file-case and process-source projection plus TCP partial
EOF tuples remain unconfirmed. No field rollout, schema migration, historical loss
closure or release certification; pins/security/default-off controls unchanged.

### Retrospective boundary

**Scoped identity/data-quality improvements and observed disposable-Linux delivery
are verified. A later operator-assisted native RHEL 9 self-contained RPM smoke and
fresh DBT build pass; broader release/package qualification and multi-day real-host
acceptance remain incomplete.** Earlier diagnostic packages were private managed
derivatives, not clean native/eBPF rebuilds or installed release acceptance.

## Meaningful proof

| Area | Result and significance |
|---|---|
| Runtime/dependencies | Installed .NET10 Ubuntu arm64 smoke/30-minute baseline passed. DuckDB official .NET wrapper1.5.6.1/native1.5.6 and Python1.5.6 qualified; DBT adapter/core retained. DuckDB2.0 held. |
| Identity/lifecycle | Independent host,birth,restart,parent and negative controls verify the canonical formula and host-bound AgentIds. Missing evidence remains unknown; Stop/Refresh do not fabricate Start. Collector telemetry is visible without self-I/O feedback. |
| TCP semantics | Source-linked regressions and live non-loopback bidirectional tests cover separate client/server processes and one process owning both endpoints. Local/remote orientation,identity and directed-port provenance pass. |
| Historical SQL audit |98-check audit quantified attribution/aggregation failures; corrected projections restored728,701file events and removed757extra summary rows. Audit execution is not a clean historical QA verdict or database repair. |
| Timestamp precision |209 focused SQL tests;12 fresh full DBT builds restore12/12collector births and verify2,900process lifetimes.216common tables preserve protected keys,counters and multiplicities. |
| Startup/shutdown | Real production EPL controls prove pre-registration loss and queue-before-final-window stranding. Exact live receipts prove post-completed-drain acceptance. Bounded experimental corrections then pass fresh output joins;267native tests/Linux build qualify the final managed candidate. |
| Pressure envelope |24 accepted off/on controls across both hosts and32/128/256-child interior/tail workloads conserve13,312paths/93,184events and3,328child lifetimes/TCPendpoint pairs.24fresh full DBT builds pass births/collector/protected counters. |
| Observer/preservation |12complete pressure traces,zero refusal/error/discard/truncation;exact observed-stage/raw joins pass.28archives hash-verified,262tested sources match;installed DLL/AgentIds/historical DB preserved. Final work-folder suite103passed,bothrepo diff checks pass. |

## Cause proof,not just passing tests

- **Identity:** missing birth previously allowed timestamp-derived hashes. Canonical
  lifecycle evidence/shared formula and explicit unknowns remove that substitution;
  complete missing-birth coverage is not guaranteed.
- **Startup:** inputs before EPL registration are not replayed. Experimental readiness
  makes collector admission follow successful registration/construction.
- **Shutdown:** serializers could finish draining before a final window callback
  accepted more rows. Terminal window execution and callback quiescence precede drains.
- **Pressure oracle:**44failed endpoint pairs/152apparent missing observations were
  all present in raw,excluded only by a stimulus+2s receipt-time predicate. Production
  TCP uses `ReceiveTime`; exact capture/PID/port/identity selection and fresh repeats
  correct the oracle. Original failure remains preserved.

## Limits and preserved failures

- Sampled retry peak348/1024 and zero pressure-child refusals establish a tested burst
  envelope,not actual saturation,universal sizing or performance equivalence.
- Earlier AXON file/TCP deficits and CALDERA capacity-refusal/unknown-identity captures
  remain unexplained in full. Later passes do not reconstruct their missing fate.
- Failed trace-budget/shared-root controls,incomplete historical shutdown cutoffs and
  failed build/deadline attempts remain evidence,not silently converted to passes.
- Metadata/executable file-ID nondeterminism,Linux `os_family='windows'`,the existing
  DATASET configuration test failure and broad sensor/byte coverage remain separate.
- The previously disclosed MacLintap virtual-environment recreation is not claimed
  preserved;the exact earlier environment cannot be reconstructed.
- No complete pre-callback kernel,fsync/upload,custom-EPL/service-deadline,Windows live,
  installed final-package,production rollout or historical migration acceptance.

Final disposable services are inactive/PID0/restarts0;lintap-dev remains active/PID701.
No tests,captures or builds were launched for this documentation condensation.

## Evidence access

The concise committed record retains conclusions and acceptance limits. Per-row JSON,
round-by-round audits and original full documents are preserved outside the commit:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]]. Consult that archive
only when reproducing a specific claim; do not load the full history for normal work.

Documentation closeout checks:26workstream/umbrella pages pass required-frontmatter,
source-path and wikilink validation;124local audit JSON files are confirmed Git-ignored.
`python -m pytest wiki/work/host-process-identity-patch -q`:103passed.
`git diff --check`:passed. Existing harnesses/tests remain unchanged.

Feature commit preflight:209focused Wintappy SQL tests pass;126Analytics harness/query/
durable tests pass plus7subtests;Wintap endpoint/event-name suites pass10+7tests.
All four repo diff checks pass. Dashboard AppTest collection is blocked in the selected
Wintappy environment by missing `streamlit.testing`;no package/environment change
was made. Earlier live/native qualifications above were not rerun for the commit.

2026-10-25 next-phase preparation: Lintap's canonical packaging guide now documents
SDK 10.0.402 selection and an operator-assisted RHEL 9 prerequisite/build/inspection
sequence. SDK-source consistency and shell-fence `bash -n` checks pass; no documented
host commands were executed. RHEL 9 build/install/runtime acceptance remains pending.
The initially stale ASP.NET Core 8 metadata is corrected by the following work.

## .NET 10 oversight correction (2026-10-25)

User authorized source fixes plus commit/push on the same feature branches. Generic
operator-assisted RHEL 9 prerequisite checks pass: stable SDK 10.0.402 selection,
BPF compiler targets, libbpf development headers and BTF parsing. The designated
system is disposable by user direction; no system-specific details/output are filed.

- SDK **10.0.402**, downloaded from official metadata with SHA-512 verification,
  evaluates all **13 C# projects** through `dotnet msbuild -getProperty:TargetFramework
  -p:EnableWindowsTargeting=true`: all net10.0 or Windows-qualified net10.0.
- `python3 -m unittest devtools/test_runtime_alignment.py -q` in Wintap: **6 pass**.
- `../Wintappy/.venv/bin/python -m pytest tests/test_dotnet_packaging.py -q` in
  Lintap: **22 pass** (exact/wrong/missing SDK, unrelated caller directory, pre-cleanup
  failure, staged runtimeconfig modes/negatives, metadata and provisioning drift).
  System Python lacks pytest; the existing Wintappy environment was used unchanged.
- All **five retargeted diagnostics/samples** pass fresh Release builds with
  `-p:RestoreLockedMode=true` in an isolated tracked-source copy plus scoped edits
  and new lock files. Existing sample nullable warnings remain.
- Actual `linux-x64` managed Lintap publishes pass in **both self-contained and
  framework-dependent modes**, with embedded MCP disabled. Runtimeconfig/deps target
  .NET 10; self-contained includes .NET/ASP.NET Core **10.0.13** and `libcoreclr.so`,
  framework-dependent declares **10.0.0** framework minima without `libcoreclr.so`.
  Shared runtimeconfig validation accepts both actual payloads. This was macOS
  cross-publish, not Linux native/eBPF/package installation acceptance.
- Separate MCP helper `linux-x64` self-contained/single-file publish passes using
  the builders' flags; existing nullable warnings remain. This is not live MCP acceptance.
- Real shared SDK preflight passes from an unrelated caller directory. Changed shell
  scripts/helper and builder `--help` pass; three-repo diff checks and changed local
  Markdown link checks pass.

Preserved failures: redirected builds initially compiled old local `obj` sources;
conditional native-output exclusions fix this without deleting old output. The
event sample's existing Windows-only `md/copy` post-build failed on macOS; the target
is now guarded by Windows/defined-solution conditions. Its managed compilation passes.
The MCP sample reference was incorrect and is corrected to the sibling sample.

**Committed-lock limitation:** fresh locked RID publish initially fails NU1004 because
WintapAPI's committed lock lacks `linux-x64`. Ordinary restore in the isolated copy
re-evaluates that RID graph without changing any base dependency/version/content hash;
subsequent locked publishes pass for both modes. Source locks were not overwritten.
Do not claim a pristine committed-lock RID publish passes. Linux builders still use
their ordinary restore default; clean locked cross-RID release qualification remains
open. NuGet audit/security settings are unchanged.

Both package scripts now declare ASP.NET Core 10.0 for framework-dependent builds;
no native Debian/RPM packages were built here. Fresh package metadata/payload
inspection, RHEL 9 live installation/capture/shutdown and Windows runtime acceptance
remain pending. Historical `.vdproj` installer snapshots retain old inventories;
current WiX release packaging is explicitly distinguished from them.

### Operator-reported RHEL 9 package progress

The operator reports a successful native self-contained RPM build, satisfactory
package inspection/transaction preview, installation and both service units inactive.
These are operator-reported package-stage conclusions, not independently reviewed
raw output or runtime/sensor/capture acceptance. Network-restricted restore required
an approved network-enabled Linux system to prefetch into shared package/HTTP caches;
the prefetch must match publish properties and the declared multi-RID graph. SDK
10.0.402, TLS validation and NuGet auditing remain enforced. At that package stage,
installed configuration, runtime, data, shutdown and downstream gates were pending;
the following bounded smoke results advance those gates without full certification.
No identifying system details or raw operator output are persisted.

### Operator-assisted RHEL 9 capture, shutdown and DBT smoke

- Installed payload/configuration review and bounded host-only startup/shutdown
  are operator-reported passes. Timeout exit 124 alone was not treated as proof.
- Normal collector startup is operator-reported healthy; pidstat remained inactive.
  Protected data permissions were retained; validators used the existing uv Python
  interpreter under sudo, without creating a root Python environment.
- Process capture with `--require-stop` passed by operator report. Basic single-path
  file smoke passed with open/read/write/close/delete coverage and serializer-drop
  checking requested; this is not exact event-count certification.
- Independent same-host TCP endpoint validation passed by operator report for both
  directions, separate-process and same-process socket ends, and process identity.
  Validator bodies were called without the host-identifying manifest wrapper.
- Operator reports clean shutdown, no leftover `.active` files and pidstat inactive.
  These reports do not independently establish exact queue conservation/final-window
  delivery or hook/object provenance.
- Fresh DBT output over the stopped capture completed **40 models, 42 data tests and
  one project hook: PASS=83, WARN=0, ERROR=0, SKIP=0**. The supplied summary reports
  DuckDB Python **1.5.6**, dbt-duckdb **1.9.6**, and dbt-core **1.12.3**; the core is
  newer than the earlier local 1.12.2 tuple, not a claim that all environments match.
- Preserve the failed extension attempts locally: `LOAD parquet` alone did not cache
  the installable package, and profile `settings` selected the shared extension cache
  too late for adapter installation. Prefetch both official `httpfs` and `parquet`
  on the network-enabled Linux system; set `config_options.extension_directory` for
  connection-time cache selection. TLS and extension-signature checks stay enabled.
  A temporary profile, database, target and logs kept generated evidence local-only
  and left source profiles/raw telemetry unchanged.

These are bounded operator-assisted package/capture/downstream smoke results, not
multi-day, Windows, framework-dependent package, strict count/identity preservation,
historical-loss closure, or full release acceptance. Detailed evidence stays local;
only generic conclusions and validation counts are committed.

### Periodic Linux stimulus runner (local orchestration only)

User approved a separate open-ended signal generator alongside the regular deployed
collector, with manual stopping and SmokeTests dashboard analysis. Added Analytics
`validation/telemetry-soak/` runner using existing Wintap named stimuli and same-host
TCP selector generation, existing raw smoke evidence snapshots and private local
fallback evidence. No source changes in sibling repos, direct host execution,
collector management, S3 credential configuration or automatic evidence deletion.

`bash -n validation/telemetry-soak/run-smoke-soak.sh`: pass.
`python3 -m unittest discover -s validation/telemetry-soak -p 'test_*.py' -v`:
**11 pass**, mocked Linux orchestration/selector tests, not native live tests.
`git diff --check`: pass. Pilot round, native timeout/signal behavior, Garage evidence
arrival and long-duration behavior remain pending operator execution. Current DBT
does not validate manifests; dashboard analysis is the user's selected path.

### Operator-reported soak delivery and read-only dashboard source

Operator reports one pilot runner round completed, uploader working and smoke evidence
arriving in S3. Per-workload pilot status/ground-truth coverage was not supplied, so
these reports do not certify every stimulus or sensor capture. User selected a direct
read-only Garage/S3 dashboard source on the same branch; see
[[wiki/work/smoke-test-dashboard/verification]] for backend/UI and synthetic HTTP
transport results. Actual Garage dashboard ground-truth checks and long-duration
acceptance remain pending. DBT manifest integration remains deferred.

### Non-interfering canaries and lazy dashboard pages

User refined recurring scope to non-interfering canaries rather than all dev-time
tests. Analytics runner now emits five distinct canary families via safe reused
generators, with no sensor/service/configuration/tracer changes. Dashboard uses
Overview/Canary Tests/Dev-time Tests pages; overview reads evidence only and selected
telemetry validation is explicit, with a bounded no-spill in-memory working set.
See [[wiki/work/smoke-test-dashboard/verification]] for local tests and open native
pilot/Garage gates. Existing running generators are not changed or restarted by
this implementation; operator must launch a fresh pilot for expanded evidence.
