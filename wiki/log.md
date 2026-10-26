# Wintap Ecosystem Wiki Operation Log

Append-only. Format: `## [YYYY-MM-DD] operation | description`
Query: `grep "^## \[" log.md | tail -10`

---

## [2026-10-26] code | RHEL 8 CO-RE start-time field compatibility

Added shared CO-RE flavor probes for upstream `task_struct.start_boottime` and
RHEL 8 `task_struct.real_start_time`; Clone and Exit now use the same
best-effort start-boottime helper. On RHEL 8.10 x86_64, all tracer CO-RE
objects compiled and a self-contained RPM built in isolated `/tmp/opencode`
work/output directories (SHA-256
`5737b7cefbec9d394b7648aa387ab25245b9077b8e3e00a54f778b34ecfc3943`). Also
compiled both changed objects against a temporary upstream-style BTF header.
No package installation, BPF load/attach, or live capture was performed.
Updated process semantics and Linux capability documentation; pre-existing
untracked work preserved.

## [2026-10-26] docs | RHEL 8 RPM build prerequisites

Added a clean RHEL 8 x86_64 prerequisite workflow: read-only host/repository/BTF
preflight, approved DNF build dependencies, exact isolated .NET SDK 10.0.402
selection, and source/worktree checks. Explicitly supersedes stale SDK 8
handoff notes and clarifies that kernel-devel does not provide BTF. Linked from
the index; no system packages installed and no source-repo files changed.

## [2026-10-22] code | Clone default TRUE and Ubuntu package acceptance

User authorized Ubuntu/arm tests and separate RHEL handoff. Debian/RPM Clone
env defaults now true with opt-out retained; builders require Clone CO-RE payload
on native/BTF builds. Fresh self-contained arm64 package built and installed on
new disposable VM. Normal ETL startup exposed lazy plugin receipt reset erasing
isolation settings; repaired idempotent initialization and added regression
(127 focused tests pass), rebuilt revision 104. Fallback missing-flags negative
still misclassifies 60 threads and is explicitly warned, not certified. Normal
pipeline/churn/restart/opt-out acceptance ongoing; RHEL dev handoff and verification
created. No commits/pushes; unrelated changes preserved.

## [2026-10-22] code | Durable HOST runtime capability receipts

User-authorized sibling Wintap changes add versioned RuntimeCapabilitiesJson to
HOST, frozen per-run startup logging/publication even with ETL/sensors disabled,
effective config/component settings, selected object hashes and candidate/hook
outcomes. Standardized Linux auxiliary ERR_PTR checks. 126 focused tests and
Ubuntu arm64 core/fallback/restart/disabled HOST validation pass; sequential
clone regression retains all 80 births/zero threads. Concurrent harness attempt
hit API port conflict, not sensor loss. Canonical schema/verification added;
matrix updated. Defaults/packages/DBT unchanged; run ID not added to other event
rows, continuous health and downstream temporal joins remain future work.

## [2026-10-22] docs | Linux capability and resulting-data matrix

Created `wiki/diagnostic/linux-capability-data-quality-matrix.md`: separates
per-sensor object/hook selection from distro evidence; maps process/file/network/
SELinux tiers, build packaging and output modes to data caveats; proposes a
dataset capability receipt. Source review highlights placeholder fallback exit
codes/TCP bytes, missing fallback inode/parent/start evidence, callback-time Stop,
network request/rate-limit semantics, and nonuniform auxiliary ERR_PTR checks.
Named Ubuntu/Fedora/RHEL findings are dated, with new-fix/platform gaps explicit.
Linked from index and clone results. Documentation only; no source/default changes.

## [2026-10-22] code | clone lifecycle follow-up

On current branches, added manifest/libbpf/direct-parquet harnesses and five
resolver regressions. Live Ubuntu 24.04 arm64 baseline confirmed 40 false thread
births and 20 worker-TID parents; new CO-RE child pid/tgid filter and updated
clone3-aware fallback pass 80 process / 60 thread cases with normal hooks.
Fallback with absent hooks remains unsafe for thread classification. Dual-sensor
output confirms three Start observations per fork+exec identity; late clone
resolver guard preserves exec metadata and Stop state without raw deduplication.
Linux build and 88 focused tests pass; broad macOS suite fails/aborts in Windows
tests (603 pass, 16 fail). Defaults/packages unchanged. Plan/results added and
linked from verification/index; durable Linux semantics added to process-events.

## [2026-10-22] docs | Lintap packaging guide and eBPF diagram glossary

Consolidated Debian/RPM build, inspection, installation, and smoke-test
instructions into `../Lintap/packaging/README.md`; reduced format-local guides
to pointers/installed quick references and marked dated review/handoff records
as historical. Added the 36-anchor companion glossary for
`wiki/work/improve-lintap-data-quality/ebpf-quality-flow.drawio`, linked it from
verification and the index, and repaired supported live-path citation moves.
The `[A7]`/`[S8]` definitions explicitly cover TCP and UDP's ten-second EPL
aggregation, not only FileOps batching.
The review also surfaced and documented the current RPM limitation: cross-build
mode disables BTF but payload validation still requires the CO-RE FileOps
object, so the present end-to-end RPM contract is native x86_64 with BTF.
Deterministic checks found zero broken local Markdown links, real wikilinks, or
required-frontmatter omissions. Thirty-six unavailable historical/local-only
or optional external-checkout source anchors remain explicitly unretargeted.

## [2026-10-22] docs | improve-lintap-data-quality eBPF flow diagrams

Added a two-page diagrams.net source covering the Linux eBPF-to-parquet
architecture and normal-delivery/coordinated-shutdown sequence. Stable
`A`/`Q`/`S` anchors now map ring latency, attribution, serializer pressure,
durable shutdown, and downstream completeness evidence to exact flow stages.
Linked the anchors and validation matrix from the feature verification page.

## [2026-10-21] verification | improve-lintap-data-quality acceptance3

The isolated arm64 acceptance3 capture produced 10,000 file and 42 TCP staged
rows with no Unknown/empty identities, owner warnings, or FileOps queue drops.
DBT passed 80/80 and matched every file row, but found one orphan among 27
network increments. The remaining cause was floating-point `/proc` start-time
conversion in the live resolver fallback; it is now integer-only with a
regression test and awaits long-run validation. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-22] closeout | improve-lintap-data-quality accepted

Closed the feature after final source and fresh Debian arm64 acceptance. The
two-hour source run retained all 124,800 workload paths with zero serializer,
writer, sender, or ring loss and completed coordinated shutdown. A kernel-time
network correction then passed a rapid-child source run with zero file/network
orphans or `Unknown` names. Package `0.1.0-102` repeated the gate on a fresh
Ubuntu 24.04 arm64 VM: 5,000/5,000 paths, exactly 40,000 operations, DBT 80/80,
zero attribution failures, and clean final merge. Focused tests passed 383/383;
the arm64 build passed with zero errors. Promoted durable flow/shutdown facts to
the FileOps and Esper pages. Wintap commit: `1c048a8`; no push performed.

## [2026-10-21] code | improve-lintap-data-quality live attribution fallback

Moved the stable PID-hash fallback to the live file/TCP/UDP callback path so
rapid children can be attributed before exit; removed callback-time network
hashes. Local and arm64 source builds passed. The isolated rerun has 24 TCP
rows with no Unknown identities or owner warnings, but FileOps kernel counters
advance while userspace file emission remains zero, so file/DBT acceptance is
blocked rather than inferred from an empty relation. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] verification | improve-lintap-data-quality isolated attribution rerun

The isolated Clone-enabled/retry-10 acceptance rerun is not accepted: staged
output has 20 Unknown file identities in 13,097 rows and one Unknown network
identity in 64 rows, with matching owner-resolution warnings. Its raw merge had
not completed, so no DBT acceptance claim was made. The earlier zero-Unknown
capture remains pilot evidence only; ldq-03 stays open. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] code | improve-lintap-data-quality ldq-04 DBT attribution QA

Added Wintappy's `attribution_quality_summary` monitoring view, reporting
orphan and Unknown-name rows/hashes/rates for file and network relations, and
included it in `build_summary`. DBT passed 80/80. The existing orphan diagnostic
correctly fails on the shared mixed-capture raw root, so aggregate rates are
recorded as baseline/intermediate evidence rather than acceptance. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] code | improve-lintap-data-quality ldq-03 lifecycle attribution

Enabled Clone in the controlled source-build runtime and fixed the observed
cross-poller ownership races: active-cache selection now covers network events,
file/network retries are bounded to ten seconds, and Clone/Execve/`/proc`
process-start conversion shares a clock-tick identity basis. The 200-child
rapid-fork capture recorded 10,769 file rows and 32 network rows with zero
Unknown names/hashes; it does not prove process-user remediation or replace the
pending DBT comparison. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] diagnosis | improve-lintap-data-quality ldq-03 lifecycle coverage

The source-build attribution baseline has an evidence-supported cause for its
file orphans: the active runtime configuration disabled `Clone`. A representative
cron/PAM child produced 150 Unknown file identities and a later Stop record but
no Start/Refresh record; the capture log reports failed owner resolution for the
same PID. The next controlled remediation is enabling Clone for a clean
before/after capture and comparing DBT orphan composition. This does not yet
address process-user Unknown values. Corrected the dev handoff to retain the
completed ldq-00 VM setup rather than restart it. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] verification | improve-lintap-data-quality source baseline

Created fresh arm64 `lintap-quality` source-build VM with the LLNL checkout and
feature-isolated Wintappy data mount. The initial 6,000-file run recorded
5,693 paths with zero FileSerializer, FileOps, and BPF ring-buffer drops; a
rebuild/restart run after 45 seconds captured 6,000/6,000 with zero serializer
drops. Queue-limit changes are deferred pending warm-up/attach-state evidence.
Fixed FileSerializer-only lowercase hostname output; refreshed source output
uses `LINTAP-QUALITY` consistently across process, file, and network rows.
DBT passed 79/79; file-orphan/user-attribution counts remain baseline work.
Details: `wiki/work/improve-lintap-data-quality/verification.md` and
`wiki/work/improve-lintap-data-quality/spike.md`.

## [2026-10-21] verification | fresh lintap package mounted-data smoke

Replaced the disposable `lintap-dev` Multipass deployment, mounted
`../Wintappy/data` at `/home/ubuntu/data/smoketest`, installed Debian arm64
package `lintap_0.1.0-101_arm64.deb`, and configured that mount as
`WINTAP_DATA_ROOT`. Package service startup and process/file/network functional
smokes passed; Wintappy DBT passed 79/79. Quality is not accepted: the 6,000
unique-file workload recorded FileSerializer `dropped_total=28533`, although
the current smoke log-text gate returned a false green; DBT found 717
`process_file` orphan rows across 496 unknown process hashes. Recorded details
in `wiki/work/refactor-data-log-paths/verification.md`.

## [2026-10-21] code | smoke QA validation and orphan dashboard drill-down

Updated `../wintap/devtools/file_capture_smoke_test.py` to recognize current
FileSerializer `dropped_total` flush counters against a pre-workload baseline,
and restored Wintappy's early `raw_sensor` DBT-root validation. Added a Top 25
orphan-process-identity drill-down after the dashboard orphan summary, grouped
by relation/host/reported-name/missing-hash and ranked by event impact with
affected item and time-range context. Unit-style parser checks, dashboard SQL,
Marimo syntax/structural checks, and refreshed DBT build passed. The renewed
6,000-file field workload failed at 4,918/6,000 paths and grew the serializer
drop total from 28,533 to 55,938; this remains an acceptance failure. Details:
`wiki/work/refactor-data-log-paths/verification.md`.

## [2026-10-21] feature | improve-lintap-data-quality opened

Completed the adaptive interview and created the `improve-lintap-data-quality`
feature artifacts. Confirmed scope: measured Linux/Lintap-only remediation for
serializer loss, PID-hash orphan attribution, hostname consistency, and
incremental Unknown process/user improvement; source-build iteration first and
fresh packaged arm64 Multipass acceptance last. The benchmark-and-recommendation
spike must set queue and orphan thresholds before implementation chooses a
remedy. Windows parity and RPM acceptance are excluded. Added the feature brief
to `wiki/index.md`.

## [2026-10-20] closeout | fix-hardcoded-agentid

Feature closed after final wiki validation. Changed feature artifacts have
complete frontmatter, valid internal feature links, current validation dates,
and no broken feature wikilinks. Repository-wide lint still reports pre-existing
wiki debt (9 broken template/relative links, 60 stale pages, and 56 orphan-page
candidates), none introduced by this feature.

## [2026-10-20] code | fix-hardcoded-agentid implementation and validation

In `../wintap`, replaced TCP's literal `grantj` AgentId with the event AgentId,
shared platform-neutral TCP/UDP inactivity wording, sanitized the tracked
`wintap/wintapstate.json` template, and added focused serializer/template
contracts plus a repeat-miss resolver profile. Multipass `lintap-dev` (Ubuntu
24.04.5, kernel 6.8) build, focused tests, eBPF attachment inspection, traffic
smoke, and fresh TCP staging/raw parquet checks passed. Post-restart raw rows
had the active UUID and zero `grantj`; lifecycle output included
connect/send/receive/disconnect. The 621.46-us unresolved lookup profile did
not justify a negative cache without evidence of sustained live miss volume.
Updated `wiki/work/fix-hardcoded-agentid/{implementation_plan,verification}.md`,
`wiki/diagnostic/linux-tcp-investigation-2026-06.md`, and the index.

## [2026-10-20] feature-start | fix-hardcoded-agentid

Interview completed and playback confirmed. Created matching
`fix/hardcoded-agentid` branches in Wintap-Analytics and Wintap. Feature
artifacts created: `wiki/work/fix-hardcoded-agentid/{interview,brief,references,implementation_plan,dev_handoff,verification}.md`.

Scope: restore TCP event AgentId propagation; sanitize only the tracked
`wintap/wintapstate.json` template; make TCP/UDP watchdog text platform-neutral;
validate existing attachment/PID/protocol/rundown behavior; profile before any
bounded resolver negative cache; retain Linux live-validation as a closure gate.
Human estimates recorded verbatim: “3 days” solo, “1 day” AI workflow.

## [2026-10-20] ingest | Linux TCP investigation (June 2026)

Created `wiki/diagnostic/linux-tcp-investigation-2026-06.md` as the
source-policy-compliant Analytics wiki home for
`../wintap/linux-tcp-investigation-2026-06.md`; the live Wintap original remains
read-only. Current-source validation found attachment, socket-keyed PID,
protocol-fallback, Parquet null/logging, and default ProcessRundown claims
addressed; hardcoded TCP AgentId, tracked state-template UUID, and Linux
watchdog wording remain open. Contradictions flagged: none.

## [2026-10-19] code | refactor-data-log-paths Linux default correction

Changed the Linux default top-level to `/var/log/lintap`, with independent defaults
`/var/log/lintap/data` and `/var/log/lintap/runtime`. Updated Wintap fallback
resolution/tests/tools, Debian/RPM package roots and maintainer scripts,
pidstat fallbacks, Wintappy documentation, and all active path documentation.
Focused Wintap tests pass 21/21; package rebuild/service smoke is pending VM
network recovery. Commits: Wintap `b3df278`, Lintap `7fa02da`, Wintappy
`6ae485a`.

## [2026-10-19] verification | refactor-data-log-paths lintap-dev cleanup

Cleaned the test-only `lintap-dev` instance after installing package
`0.1.0-99`: removed the legacy data tree and stale build/test artifacts,
disabled the broken pidstat unit, and restarted Lintap. Clean-package smoke
verified active output under `/var/log/lintap/data/raw_sensor` and
`/var/log/lintap/runtime`.

## [2026-10-15] verification | refactor-data-log-paths Esper staging correction

Moved serializer/meta parquet staging and merge inputs to
`runtime/esper_staging`, leaving finalized output under `data/raw_sensor`.
Wintap build and focused path tests passed 21/21; Debian revision 2 was built,
installed over the default package layout, and its bounded service probe
reported both resolved roots. RPM, shared-mount, and full event-output gates
remain open.

## [2026-10-15] docs | refactor-data-log-paths operator path guide

Added `../Lintap-rdp/packaging/PATHS_AND_CONFIGURATION.md` as the dedicated
operator guide for data/runtime roots, `WINTAP_DATA_ROOT` and
`WINTAP_RUNTIME_ROOT` overrides, shared-mount examples, pidstat exceptions, and
verification commands. Linked it from the repository and package READMEs and
included it in generated Debian/RPM documentation. Corrected the remaining
active TeleTap README example to use direct `raw_sensor/` output.

## [2026-10-15] code | refactor-data-log-paths rdp-01/rdp-02

Implemented the two-root Wintap resolution core and moved runtime-tree
consumers to centralized `Paths` members. Data now directly contains
`raw_sensor/`; runtime owns logs, event store, csv, recordings, diagnostics,
AI state, and workbench state. Added RuntimeRoot config/env support, startup
root logging and same-root warning, uploader relative-key coverage, and test
project execution metadata. Multipass `lintap-dev` build passed; focused
path tests passed 20/20; grep gates passed. Full suite retains 17 known
Linux-incompatible Windows sensor failures.

## [2026-10-15] code | refactor-data-log-paths rdp-03

Committed Lintap packaging split as `301ff63` on
`grantj/debian-package-refresh`. Debian/RPM packages now default to
`/var/log/lintap/data` for shared `raw_sensor/` output and
`/var/log/lintap/runtime` for host-local state; maintainer scripts preserve
the data tree and create the `/var/log/lintap/data` and
`/var/log/lintap/runtime` roots. Updated pidstat defaults,
tests, and packaging documentation. Shell/static gates passed; pytest was
blocked by missing VM dependencies and unavailable PyPI access.

## [2026-10-15] code | refactor-data-log-paths rdp-04

Committed Wintappy downstream default update as `018f541`: DBT dataset and
day-range discovery now use the direct `WINTAP_DATA_ROOT/raw_sensor` layout,
and the example environment drops `/parquet`. Analytics Streamlit/notebook
scan found no additional live old-layout input coupling.

## [2026-10-15] verification | refactor-data-log-paths rdp-05

Built and installed the Debian arm64 package in `lintap-dev`; staged and
post-install checks passed for `/var/log/lintap/data` and
`/var/log/lintap/runtime`, with the new `/var/log/lintap/data` and
`/var/log/lintap/runtime` package directories.
RPM validation is blocked by missing `rpmbuild`; service-start/event-output
acceptance remains pending.

The installed Debian service also passed a bounded 15-second start probe and
reported the split data/raw_sensor/runtime paths in journald; no short-run
event count was used as an acceptance result.

## [2026-10-15] artifact | refactor-data-log-paths Debian arm64

Confirmed the built package is available on the Mac host through the mounted
data directory at `/Users/johnson30/data/lintap/artifacts/lintap-deb/`.
SHA-256 `916407eafa64d4347e718d60cae58a50c368667c3dcd3dd83d40ea777d8f55a1`.
Marked ready for external-session testing; rdp-05 remains open.
## [2026-09-03] instruction | fio-03 disable FileSensor fallback diagnostic

Decision made: Architect requested and approved a diagnostic code change to remove Wintap's fallback dictionary from FileSensor emitted path selection so live Parquet output can show whether paths are coming from TraceEvent's `obj.FileName` resolution. Instruction created: `../wintap/developer_docs/instructions/fio-03-disable-file-fallback-diagnostic.md` (Approved 2026-09-03).

Scope: read/write/delete emission should use only TraceEvent-resolved `obj.FileName`; retain dictionary population code, `FileIOInit | DiskFileIO`, and close suppression. Follow-up depends on live validation results.

## [2026-09-03] approval | fio-02 suppress File CLOSE events

Decision made: Architect approved `../wintap/developer_docs/instructions/fio-02-suppress-file-close-events.md` after review amendments. Approved scope suppresses Wintap FileSensor Close emission, preserves read/write/delete/name/create behavior and `FileIOInit | DiskFileIO`, and allows only a temporary local live diagnostic probe to defeat Wintap's fallback resolver for TraceEvent path-provenance measurement; that probe must be reverted before the final production diff.

Instructions updated: `../wintap/developer_docs/instructions/fio-02-suppress-file-close-events.md` status changed from Draft to Approved; Architect approval stamped 2026-09-03.

Open questions: Whether to create a separate FileSensor resolver instrumentation/cleanup unit remains evidence-gated after fio-02 audit/live observations.

## [2026-09-03] instruction | fio-02 suppress File CLOSE events

Finding from Architect live observation after `fio-01`: File path resolution appears to be working, but most emitted File events are `CLOSE`.

Instruction written: `../wintap/developer_docs/instructions/fio-02-suppress-file-close-events.md` (Draft; Architect review pending). Scope: stop subscribing Wintap's FileSensor emission path to `FileIOClose`, preserve write/delete/name/create/read behavior, preserve `FileIOInit | DiskFileIO`, and keep rundown/cache cleanup out of scope. Clarified during review that `obj.FileName` on TraceEvent FileIO read/write/info/simple-op events is already resolved via TraceEvent's internal file-ID lookup, while Wintap's `resolveIoFilePath(...)` is an additional fallback. Draft amended to allow a temporary local live probe that disables Wintap's fallback after checking `obj.FileName`, solely to measure TraceEvent path provenance; any such probe must be reverted before final production diff.

Open questions: Architect review/approval pending. Separate FileSensor resolver cleanup and possible rundown work remain future evidence-gated items.

## [2026-09-03] approval | fio-01 FileIO DiskFileIO path-resolution flag

Decision made: Architect approved `../wintap/developer_docs/instructions/fio-01-fileio-diskfileio-path-resolution.md` as written, with rundown deliberately deferred to a potential later unit if `DiskFileIO` does not sufficiently improve FileSensor path resolution.

Instructions updated: `../wintap/developer_docs/instructions/fio-01-fileio-diskfileio-path-resolution.md` status changed from Draft to Approved; Architect approval stamped 2026-09-03.

Open questions: Whether FileIO rundown needs to be reintroduced remains evidence-gated follow-up after `fio-01` implementation/audit.

## [2026-09-02] instruction | FileIO DiskFileIO path-resolution flag

Sources read: `../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs`; `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`; `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs`; prior Wintap startup instruction/audit; `C:\PUBLIC\perfview-src\src\TraceEvent\Parsers\KernelTraceEventParser.cs`; `TraceEventSession.cs`; `TraceEventNativeMethods.cs`; `Microsoft-Windows-Kernel-File.cs`.

Finding: TraceEvent documents `KernelTraceEventParser.Keywords.DiskFileIO` as the classic-kernel flag that logs file-ID to file-name mappings, while real-time default parser tracking keeps `FileNameToObject` enabled. No TraceEvent-grounded FileIO equivalent of the Registry `EnableTraceEx2` capture-filter path was found.

Instruction written: `../wintap/developer_docs/instructions/fio-01-fileio-diskfileio-path-resolution.md` (Draft; Architect approval pending). Scope is intentionally minimal: add `DiskFileIO` beside `FileIOInit` for `FileSensor`, update shared-kernel flag tests, and do not rewrite FileSensor caches or add manifest-provider/capture-filter machinery.

Contradictions flagged: none. Follow-up: separate FileSensor resolver cleanup remains advisable for unsubscribe, split FileKey/FileObject maps, update-over-add behavior, and cache cleanup.

## [2026-09-01] feature-start | Support for Docker contexts on Linux

Interview completed and playback confirmed. Feature artifacts created:
`wiki/work/support-docker-contexts-linux/{interview,brief,references,design,spike,implementation_plan,dev_handoff,verification}.md`.
Scope: compare cgroup filesystem, namespace, eBPF event-time, shared userspace,
OCI/runtime, systemd, and notification approaches for per-event enrichment plus
a separate context stream; phase 1 targets cgroup v2 host/systemd/Docker,
phase 2 targets v1/hybrid/Podman, and normalized schema work is deferred.
Sealed human estimates recorded verbatim in `interview.md`: “2 weeks to get a
working prototype with acceptable data quality” and “3 days”.
Contradictions flagged: none.

## [2026-06-29] init | Wiki scaffold generated by lore-forge

Sources scanned: /git/LLNL/wintap, /git/LLNL/Wintap-Analytics, /git/LLNL/Lintap
Pages created: index.md, log.md, tension/, decision/, concept/, component/, data_model/, event_type/, pipeline/, schema/, tool/, workflow/, repo/, diagnostic/
Notes: Initial scaffold. All pages are stubs — confidence is provisional.
  First ingest pass will revise based on live source files.

## [2026-06-29] ingest | First grounded wiki pass

Sources read: ../wintap/README.md; ../wintap/documentation/wintap-developer-guide.md; ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/shared/WintapAPI/Interfaces.cs; ../wintap/wintap/core/infrastructure/EventChannel.cs; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs; ../wintap/wintap/core/infrastructure/SubscriptionManager.cs; ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs; ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/UdpSensor.cs; ../wintap/wintap/core/etl/esper/*.epl; ../wintap/wintap/core/etl/extract/Serializer.cs; ../wintap/diagnostics/nesper-repro/README.md; ../wintap/platform/windows/WintapRecorder; ../wintap/shared/Wintap-Workbench; ../wintap/wintap/core/infrastructure/PluginManager.cs; ../wintap/shared/samples/SimpleEventPlugin/SimpleEventPlugin.cs; ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs; ../Wintap-Analytics/README.md; ../Wintap-Analytics/requirements.txt; ../Wintap-Analytics/2025-acme4-explore; ../Wintap-Analytics/notebooks/ProcessTrees.md; ../Wintap-Analytics/workshop/5_SQL_Exploration.md; ../Lintap/README.md; ../Lintap/teletap/README.md.
Pages created: none.
Pages updated: index.md; repo/wintap-primary-sensor-repo.md; repo/wintap-analytics-host-repo.md; repo/lintap-supporting-repo.md; component/windows-sensor-service-internals.md; component/wintap-api-shared-data-model.md; component/wintap-recorder.md; component/plugin-and-mcp-samples.md; event_type/process-events.md; event_type/file-events.md; event_type/network-events.md; pipeline/nesper-esper-event-stream-processing.md; diagnostic/nesper-repro.md; tool/wintap-workbench.md; workflow/future-experiment-analysis-workflows.md; decision/wiki-scope-cross-repo-wintap-focused.md; tension/raw-telemetry-vs-normalized-wintap-semantics.md; tension/research-flexibility-vs-production-hardening.md; tension/etw-ebpf-and-cross-platform-compatibility.md.
Contradictions flagged: none.

## [2026-06-29] ingest | Dependency inventory and update status

Sources read: ../Wintap-Analytics/requirements.txt; ../Wintap-Analytics/Pipfile; ../Wintap-Analytics/2025-acme4-explore/pyproject.toml; ../Wintap-Analytics/2025-dmbd/requirements.txt; ../wintap/wintap/Wintap.Common.props; ../wintap/wintap/Wintap.csproj; ../wintap/wintap/Lintap.csproj; ../wintap/shared/Wintap-Workbench/package.json; ../wintap/shared/ai/wintap_mcp_server/wintap_mcp_server.csproj; ../wintap/devtools/requirements.txt; ../Lintap/pyproject.toml.
Update checks: npm outdated for Workbench runtime dependencies; PyPI JSON lookup for Python manifests; NuGet flat-container lookup for PackageReference entries because dotnet was unavailable. uv and dotnet were not installed, so lock-aware Python and restore-aware .NET checks were not performed.
Pages created: diagnostic/dependency-inventory-and-update-status.md.
Pages updated: index.md; log.md.
Contradictions flagged: none.

## [2026-06-30] methodology | [wintap] Methodology bootstrap

Decisions made: Adopted the Architect / Engineer / Developer role-separated workflow with per-developer wikis to avoid git conflicts — each dev only edited their own wiki directory. Adapted from the OpenCode setup and the Karpathy LLM-wiki pattern. Verification gate: stand up xUnit first (unit P1.1). Role boundaries enforced via subagent tool limits plus instruction discipline. Instruction/design/audit docs live under `developer_docs/`.
ADRs written or updated: none yet.
Wiki pages updated: none yet — the Wintap-side wiki was empty and awaiting first ingest.
Instructions written: none yet. Recommended next: P1.1 — stand up xUnit test project under `tests/`.
Open questions: Where exactly should the xUnit project sit relative to the multi-target agents (Wintap/Lintap/Mactap)? What is the first behavior worth covering with tests?

## [2026-06-30] decision | [wintap] P1.1 design settled (test harness)

Decisions made: Resolved both open questions from the bootstrap entry. Open Question 1 (placement) resolved: per-target test projects mirroring the multi-target agents (`tests/Wintap.Tests/`, `tests/Lintap.Tests/`, `tests/Mactap.Tests/`), chosen by the Architect. Open Question 2 (first behavior) resolved: a real test against `WintapMessage` — construct it and assert `MessageType` matches the `MessageTypeEnum` passed to the constructor. Reconciliation: because `WintapMessage` lives in cross-platform `shared/WintapAPI` while the agent projects are OS-bound, P1.1 stands up only `tests/Wintap.Tests/` now, referencing `shared/WintapAPI`; Lintap/Mactap siblings are deferred to P1.2.
ADRs written or updated: `wiki/decision/test-project-structure-and-first-test.md` (Accepted; migrated from `../wintap/dave-wiki/wiki/decisions/2026-06-30-test-project-structure-and-first-test.md`).
Wiki pages updated: none beyond the ADR and log.
Instructions written: `../wintap/developer_docs/instructions/P1.1-xunit-test-harness.md` (Status was Draft at the time of the original entry).
Open questions: P1.2 owed — stand up `tests/Lintap.Tests/` and `tests/Mactap.Tests/` siblings; decide per sibling whether it references shared code vs. the OS-bound agent. When the first genuinely Windows-agent-specific behavior is tested, `tests/Wintap.Tests/` will additionally reference `wintap/Wintap.csproj` and its `dotnet test` becomes Windows-only.

## [2026-06-30] decision | [wintap] Stage 0 locked (process identity & attribution contract)

Decisions made: Locked the Stage 0 canonical contract from the architecture assessment. Core owns `PidHash`/`ParentPidHash` generation; sensors supply a flat event-time-knowable field list; Stop events resolve identity and backfill required fields including `ParentPidHash` from a durable store; DuckDB is the starting substrate for durable persistence and hot-path attribution lookups; invariants are mechanism-agnostic so tests survive a later substrate change.
ADRs written or updated: `wiki/decision/process-identity-attribution-contract.md` (Accepted; migrated from `../wintap/dave-wiki/wiki/decisions/2026-06-30-process-identity-attribution-contract.md`).
Wiki pages updated: none beyond the ADR and log.
Assessment updated: `../wintap/documentation/design/architecture-assessment.md` — appended DEC-001..DEC-004 to the Decisions Log; reworded INV-001..INV-005; annotated OQ-001/OQ-002/OQ-004 as resolved and OQ-003/OQ-005 as deferred.
Instructions written: none.
Open questions / follow-up: Stage 1 contract tests recommended next; DEC-004 is evidence-gated and the memory-first optimization should be revisited only if measurement shows a throughput/latency ceiling.

## [2026-07-06] maintenance | LLM-wiki contract alignment

Pages created: decision/feature-work-artifacts.md; concept/llm-assisted-feature-workflow.md; concept/feature-work-template.md; work/
Pages updated: index.md; AGENTS.md
Notes: Validated that all wiki pages have required frontmatter keys, have no broken wikilinks, and that `grounded_by` paths resolve. Added the optional feature-work module pages and aligned AGENTS.md directory names with the on-disk `wiki/decision/` and `wiki/tension/` layout.

## [2026-07-31] research | Lintap process creation validation thread

Sources read: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs; ../wintap/wintap/core/shared/ProcessHash.cs; ../wintap/devtools/process_capture_smoke_test.py; ../../tetragon process lifecycle sources; ../../tracee process lifecycle sources; ../../sysdig capture selection sources; public GitHub issues/PRs for Tetragon, Tracee, and Falco/Sysdig process accuracy risks.
Pages created: work/lintap-process-creation-validation/index.md; work/lintap-process-creation-validation/research-snapshot-2026-07-31.md; work/lintap-process-creation-validation/handoff-validation-next-steps.md.
Pages updated: index.md; log.md.
Contradictions flagged: none.

## [2026-07-31] design | Sensor-neutral process validation harness

Sources read: ../wintap/devtools/process_capture_smoke_test.py; ../wintap/devtools/file_capture_smoke_test.py; ../wintap/devtools/network_capture_smoke_test.py; ../wintap/diagnostics/process-smoke-test/Program.cs; ../wintap/BUILD_AND_TEST.md; ../wintap/devtools/README.md.
Pages created: work/lintap-process-creation-validation/validation-harness-design.md.
Pages updated: work/lintap-process-creation-validation/index.md; index.md; log.md.
Contradictions flagged: none.

## [2026-07-31] test | Process validation mock checks on macOS

Commands run: Python frontmatter/wikilink/source-path checker for wiki/work/lintap-process-creation-validation; Python in-memory mock manifest/evaluator exercise for normalized process events.
Results: frontmatter, wikilinks, checked GROUND_TRUTH paths, and key local source paths passed. Mock evaluator produced expected fork, exec-attempt, exec-success, exit, parent-join, duplicate-start, and identity-collision metrics and detected one deliberately injected duplicate exec-success event.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Limitations: no Linux eBPF attachment, ring-buffer polling, Lintap Parquet output, live reference-sensor output, or load/loss behavior could be tested on macOS.

## [2026-07-31] setup | Linux VM setup for validation

Sources read: ../wintap/BUILD_AND_TEST.md; ../wintap/documentation/Linux Deployment Guide.md; ../wintap/wintap/Makefile; ../wintap/devtools/README.md; ../wintap/devtools/process_capture_smoke_test.py.
Pages created: work/lintap-process-creation-validation/linux-setup.md.
Pages updated: work/lintap-process-creation-validation/index.md; index.md; log.md.
Notes: Recommended Multipass for fastest repeatable CLI setup and UTM for kernel/distro control. Recommended running sensors and workloads inside the Linux VM, with macOS used for SSH orchestration and artifact copying.
Contradictions flagged: none.

## [2026-07-31] code | Initial process validation harness prototype

Files created: validation/process-creation/pyproject.toml; validation/process-creation/uv.lock; validation/process-creation/README.md; validation/process-creation/src/wintap_process_validation/*; validation/process-creation/tests/*.
Implemented: uv-managed Python package with manifest schema, workload generator, mock normalized event writer, evaluator metrics, Lintap process row normalizer, and CLIs `wpv-workload`, `wpv-mock-run`, `wpv-evaluate`, `wpv-normalize-lintap`.
Tests run: `uv run --extra dev pytest` in validation/process-creation, result 5 passed. Also ran `wpv-workload` and `wpv-mock-run` on macOS; execveat was skipped with a manifest note because macOS lacks `os.execveat`, and mock evaluation detected the intentionally injected duplicate exec-success row.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Limitations: live Linux eBPF, Lintap Parquet normalization, and reference sensor output remain untested until a Linux VM is available.

## [2026-08-06] test | Multipass Lintap process smoke test

Environment: Multipass Ubuntu 24.04 arm64; kernel 6.8.0-136-generic; BTF present; Wintap branch grantj-ebf-fixes at 7f93255.
Commands run: VM toolchain checks; `make build_ebpf`; `make build_dotnet`; `UV_PROJECT_ENVIRONMENT=/tmp/wpv-venv uv run --extra dev pytest`; `UV_PROJECT_ENVIRONMENT=/tmp/wpv-venv uv run wpv-mock-run`; `sudo python3 devtools/process_capture_smoke_test.py --start-lintap --lintap-dll /home/ubuntu/git/wintap/wintap/bin/Debug/net8.0/Lintap.dll --timeout 240 --poll-interval 5`.
Results: eBPF and .NET builds passed; validation harness tests passed with 5 tests; mock run passed and detected expected duplicate exec-success warning; Lintap process smoke test passed.
Fixes made: Wintap eBPF tracer now uses `task_struct.start_time` for Ubuntu arm64 CO-RE compatibility; ExecveSensor/CloneSensor attach extra programs by program name instead of unavailable `bpf_object__find_program_by_title`; ExecveSensor parent hash conversion now matches `/proc` clock-tick semantics and uses eBPF parent attribution as fallback; process smoke test ignores `.parquet.active` files and relaxes execveat flag validation when Python lacks `os.execveat`.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Limitations: reference sensors not yet run; true `execveat(2)` validation still needs a C workload because Ubuntu Python 3.12 lacks `os.execveat`.

## [2026-08-06] test | Lintap noisy process state table run

Environment: Multipass Ubuntu 24.04 arm64; Wintap branch grantj-ebf-fixes; Lintap resolver-mode config with Execve and Exit enabled, direct parquet and Esper send disabled, Clone/Network/FileOps/Rundown disabled.
Workload: `wpv-noisy-processes` for 780 seconds, 1888 manifest processes across 166 cases, combining short-lived `bash` processes and longer-lived Python sleep processes.
Fixes applied before final run: disabled BPF diag monitor by default; captured process `task_struct.start_time` in exec eBPF events; used eBPF process start time when `/proc` is unavailable; filtered CO-RE exit tracer to thread-group leader exits; stopped inserting unmatched Stop-only rows; added pending-exit reconciliation in ProcessResolver; made GetPidHash respect exit_time.
Results: final noisy run `noisy-state-1786064182` observed all 1888 manifest PIDs in the `process` table. Table had 1983 rows, 1924 distinct process IDs, 1923 closed rows, and 60 open rows. Manifest-specific open rows were 59/1888, mostly short-lived bash. Final process smoke test also passed after the fixes.
Artifacts: validation/process-creation/noisy-state-summary-multipass-2026-08-06.json; validation/process-creation/smoke-15m-summary-multipass-2026-08-06.json.
Limitations: residual open rows remain; true execveat still needs a C workload; reference sensors were not run.

## [2026-08-06] checkpoint | Process validation implementation commit point

Summary: Prepared commit checkpoint after implementing the first executable validation harness, Multipass setup updates, Lintap eBPF/process-state fixes, and noisy process-state tests.
Validated: Wintap build passed in Multipass; validation harness tests passed on macOS and Linux; Lintap process smoke passed; five 15-minute smoke rounds passed; noisy resolver-mode run observed 1888/1888 manifest PIDs with 60 open process rows remaining.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Open follow-up: run a longer one-hour noisy process-state test and investigate the residual short-lived open rows.

## [2026-08-06] test | One-hour Lintap noisy process state run

Environment: Same Multipass Ubuntu 24.04 arm64 validation VM and Wintap process-state fixes as prior noisy run.
Workload: `wpv-noisy-processes` for 3600 seconds with 8732 manifest processes across 767 cases.
Results: all 8732 manifest PIDs were observed in the DuckDB `process` table. Table totals were 10372 rows, 10064 distinct process IDs, 10060 closed rows, and 312 open rows. Manifest-specific open rows were 285/8732, concentrated in short-lived bash workload rows. Longer-lived Python workload rows closed cleanly. A post-run Lintap process smoke test passed.
Artifact: validation/process-creation/noisy-state-1h-summary-multipass-2026-08-06.json.
Limitations: residual short-lived open rows remain; reference sensors and true C-based execveat workload not yet tested.

## [2026-08-06] checkpoint | Current process validation state

Pages created: work/lintap-process-creation-validation/current-state-2026-08-06.md.
Pages updated: work/lintap-process-creation-validation/index.md; index.md; log.md.
Summary: Recorded current commits, validation harness state, one-hour noisy run results, known residual short-lived process leakage, and next-step recommendations.

## [2026-08-07] test | 30-minute all-events normal ETL Parquet run

Environment: Multipass Ubuntu 24.04 arm64; Lintap normal ETL/Parquet config with process, clone, exit, network, file, and process rundown sensors enabled; direct Parquet disabled.
Workload: Existing process/file/network smoke tests plus `wpv-noisy-processes` during a 1878-second capture window.
Results: process smoke passed; file smoke passed; network smoke failed. No TCP/UDP/raw_process_conn_incr Parquet rows were found. Parquet outputs included fileserializer=2996 rows, processserializer=57 rows, processstopserializer=26 rows, raw_process=32013 rows, raw_process_file=300000 rows, raw_host=1 row, raw_macip=1 row. Network logs showed BPF diag misses (`STORE/HIT/MISS = 0/0/62`) but no normal network rows.
Artifacts: validation/process-creation/all-events-30m-summary-multipass-2026-08-07.json; validation/process-creation/all-events-30m-parquet-summary-multipass-2026-08-07.json; validation/process-creation/all-events-30m-network-smoke-multipass-2026-08-07.out.
Open follow-up: diagnose network eBPF/socket PID attribution and why network telemetry is not materialized under normal ETL output.

## [2026-08-07] fix | Network program attachment compatibility

Root cause: NetworkSensor used `bpf_object__find_program_by_title` for additional program attachment, but Ubuntu 24.04 arm64 libbpf did not export that symbol. The network sensor failed startup after the primary program loaded, leaving only diagnostic output and no normal network rows.
Fix: NetworkSensor now attaches additional network programs by BPF function name using `bpf_object__find_program_by_name`, and its diagnostic reporter is gated by `EnableBpfDiagMonitor`.
Validation: direct-Parquet network smoke passed. A short normal ETL all-events run also passed process, file, and network smoke and produced `raw_process_conn_incr` TCP/UDP rows: tcp=165 rows, udp=33 rows.
Artifacts: validation/process-creation/all-events-10m-summary-multipass-2026-08-07.json; validation/process-creation/all-events-10m-parquet-summary-multipass-2026-08-07.json; validation/process-creation/all-events-10m-network-smoke-multipass-2026-08-07.out.

## [2026-08-07] test | One-hour all-events normal ETL dataset with pidstat

Environment: Multipass Ubuntu 24.04 arm64. Normal ETL/Parquet run with process, clone, exit, network, file, and rundown sensors enabled; direct Parquet disabled. Separate pidstat collector wrote to `$WINTAP_DATA_ROOT/pidstat`.
Data root: `/home/ubuntu/data/lintap/all-events-1h-1786139524` in VM, mounted to `~/data/lintap/all-events-1h-1786139524` on Mac.
Results: process smoke passed; network smoke passed; file smoke failed exact-path validation. Dataset includes pidstat CSV with 47454 lines. Raw sensor outputs include raw_process=67600 rows across hour partitions, raw_process_conn_incr tcp=1409 rows, raw_process_conn_incr udp=62 rows, raw_process_file=560000 rows, plus host/macip rows. Serializer outputs include fileserializer=49591 rows, processserializer=3763 rows, processstopserializer=485 rows, tcpconnectionserializer=108 rows.
Artifacts: validation/process-creation/all-events-1h-summary-multipass-2026-08-07.json; validation/process-creation/all-events-1h-parquet-summary-multipass-2026-08-07.json; validation/process-creation/all-events-1h-file-smoke-multipass-2026-08-07.out; validation/process-creation/all-events-1h-network-smoke-multipass-2026-08-07.out.
Open follow-up: investigate file smoke exact-path miss despite large file telemetry volume.

## [2026-08-11] ingest | raw/Agentic_Coding_for_eBPF.md brainstorming note

Source: raw/Agentic_Coding_for_eBPF.md (previously untracked; added SOURCE/RETRIEVED provenance header — exact origin unrecorded, likely Confluence-retrieved AI-assistant output dated 2026-07-16/17).
Pages created: concept/agentic-ebpf-probe-development.md (confidence low; all claims flagged SPECULATIVE pending verification).
Pages updated: index.md; work/lintap-process-creation-validation/index.md (open question: Sysmon for Linux and Bombini as candidate reference sensors); tension/etw-ebpf-and-cross-platform-compatibility.md (prior-art note: Sysmon for Linux as Windows-event-to-eBPF mapping precedent).
Contradictions flagged: none. Tetragon/Tracee/Falco framing is consistent with the 2026-07-31 research snapshot; new material is the agentic-tooling survey (MCPtrace, GPTtrace, eunomia-bpf/Wasm-bpf) plus Sysmon for Linux and Bombini as unexamined reference candidates.
Notes: nothing on the new page is source-grounded, unlike the validation thread's snapshot pages; verification of tool existence/capability is an explicit open question.

## [2026-08-11] ingest | raw/Agentic_Coding_for_eBPF.md brainstorming note

Source: raw/Agentic_Coding_for_eBPF.md (untracked brainstorming note dated 2026-07-16; provenance header added — exact origin unrecorded, likely Confluence-retrieved AI-assistant output with unresolved domain-level citations).
Pages created: concept/agentic-ebpf-probe-development.md (confidence: low; all claims flagged SPECULATIVE pending verification).
Pages updated: index.md (new concept row); work/lintap-process-creation-validation/index.md (open question: Sysmon for Linux and Bombini as candidate additional reference implementations); tension/etw-ebpf-and-cross-platform-compatibility.md (prior-art note: Sysmon for Linux as Windows-event-to-eBPF mapping precedent).
Contradictions flagged: none. Tetragon/Tracee/Falco framing consistent with research-snapshot-2026-07-31; new material limited to agentic tooling (MCPtrace, GPTtrace, eunomia-bpf/Wasm-bpf), Sysmon for Linux, and Bombini.
Open follow-up: verify existence/viability of MCPtrace and GPTtrace before any adoption discussion; decide whether Sysmon for Linux warrants a local checkout and source-inspection pass as a fourth reference sensor.

## [2026-08-11] ingest | Wintappy (Wintap-PyUtil) repo added to ecosystem scope

Source: `../Wintappy` (README.md, pyproject.toml, wintap_dbt/, review-notes/Architecture.md, DataModel.md, ProjectSummary.md, OpenQuestions.md, ImplementationStatus.md), plus this repo's `streamlit/projects/common/dqautil.py` and `streamlit/projects/DataQA/pages/raw_events.py`.
Summary for human: Wintappy is a fourth core repo in this ecosystem — the canonical Python/DBT/DuckDB post-processing pipeline that turns `raw_sensor` parquet from Wintap/Lintap into bronze/silver/gold analysis-ready models (`process`, `process_path`, `process_summary`, `process_uber_summary`, etc.), superseding a legacy Python ETL path (`rawtorolling`/`rawtostdview`/`ubersummary`) that remains only as reference tooling. It was already referenced by name ("Wintap-PyUtil/wintap_dbt") in the existing Lintap and ETW/eBPF tension pages but had no repo page of its own — an orphan-reference gap this ingest closes. Notably, Wintap-Analytics' own Streamlit DataQA/eda apps import the `wintappy` package directly, making it a runtime code dependency, not just an output-data producer.
Pages created: repo/wintappy-pipeline-repo.md (confidence: high); tension/dbt-duckdb-output-vs-legacy-stdview-parquet.md (confidence: medium, status: open — Wintappy's DuckDB-only current output vs. this repo's documented expectations of published stdview-* parquet).
Pages updated: index.md; AGENTS.md (Repository Layout, repo_scope/implementation_area enums, Domain Context, Operating Modes sibling-repo lists); repo/wintap-analytics-host-repo.md (pipeline dependency section); repo/lintap-supporting-repo.md (link Wintap-PyUtil citation to new page); decision/wiki-scope-cross-repo-wintap-focused.md (extend scope to include Wintappy); component/wintap-api-shared-data-model.md; event_type/process-events.md; event_type/file-events.md; event_type/network-events.md (downstream DBT model cross-links); workflow/future-experiment-analysis-workflows.md (identifies Wintappy as the builder of the standard views this page discusses).
Contradictions flagged: none hard. One new open tension (soft framing gap, not a factual conflict): Wintappy's own review notes mark `stdview-*` parquet as superseded by DBT/DuckDB, while this repo's ACME4/workshop material still documents fetching `stdview`-shaped published parquet datasets; captured as tension/dbt-duckdb-output-vs-legacy-stdview-parquet.md rather than resolved, per Wintappy's own open-questions tracker treating it as unresolved.

## [2026-08-11] update | LLM-assisted feature workflow ported from pEyeON-Analytics

Source: pEyeON-Analytics wiki (wiki/concepts/llm_assisted_feature_workflow.md, wiki/concepts/feature_work_template.md, wiki/work/firmware-corpus/dev_handoff.md), adapted to this wiki's frontmatter contract.
Pages updated: concept/llm-assisted-feature-workflow.md (added when-to-use/skip guidance, grounding practices, dev-handoff stage, operating rule for promoting durable facts, invocation expected behavior); concept/feature-work-template.md (full markdown skeletons for all artifacts — brief, references, design, spike, implementation_plan, dev_handoff, verification — plus an optional research-thread index.md skeleton modeled on the lintap validation thread; only brief.md required); index.md.
AGENTS.md updated: wiki/work/ added to Repository Layout; wiki-maintainer mode gains feature-work uses and the skeleton invocation phrase; code-development mode gains handoff-reading and verification/implementation-plan update rules.
Contradictions flagged: none. Prior stub declared five artifacts "required"; replaced with pEyeON's brief.md-only-required stance, matching actual practice in both repos. Existing work/lintap-process-creation-validation folder is grandfathered as the research-thread pattern rather than retrofitted.
Notes: decision/feature-work-artifacts.md intentionally left abbreviated; pEyeON-Analytics retains the full rationale/alternatives history.

## [2026-08-11] feature-work | improve-pidstat-collector started via LLM-assisted feature workflow

Source: raw/Issues/Long_Running_Cleanup.md ("Improve pidstat-collector.sh to run alongside lintap and push data to S3"), plus source inspection of ../Lintap/pidstat-collect.sh, ../Lintap/teletap/*.sql, ../Wintappy/wintap_dbt pidstat macros and bronze/silver models, and ../wintap/wintap/core/etl/load upload adapters.
Pages created: work/improve-pidstat-collector/brief.md (problem, goals, acceptance criteria, open questions, test plan); work/improve-pidstat-collector/references.md (cross-repo source map). First use of the ported feature-work template; design/spike/implementation_plan deferred until the brief's open questions are decided.
Pages updated: index.md (two new Work rows).
Contradictions flagged: none. Noted for design: the lintap validation thread treats ../wintap (Linux/eBPF branch) as canonical Lintap source while the collector script lives in legacy ../Lintap — code-location open question in the brief.
Key facts captured: DBT reads $PIDSTAT_DATA_PATH/**/*.csv tab-delimited with hardcoded columns (rotation-friendly glob already); observed volume 47454 lines/hour at 2s interval; sensor upload pipeline (CacheManager + S3Adapter) is a candidate ride-along path.

## [2026-08-11] feature-work | improve-pidstat-collector: brief decided, design and plan added

Source: human edits to work/improve-pidstat-collector/brief.md (decisions in Goals), plus source verification of ../wintap/wintap/core/etl/load/CacheManager.cs, RawSensorWriter.cs, and adapters/base/Uploader.cs.
Decisions recorded: new script in ../Lintap (old script kept as example); continuous service; 5s configurable interval; parquet output; rotation on the sensor merge cycle with dayPK=/hourPK= partitioning; S3 via the sensor's existing upload mechanism.
Verified mechanism facts: CacheManager.upload() sweeps all *.parquet under raw_sensor/ type-agnostically; Uploader_UploadCompleted deletes after successful upload (local retention free); S3 keys mirror the local relative path; *.active is the existing in-progress-file convention. Ride-along therefore needs no C# changes.
Pages updated: work/improve-pidstat-collector/brief.md (reconciled human decisions: DBT compatibility goal switched to deliberate versioning since parquet breaks the hardcoded tab-CSV bronze reader; acceptance criteria, affected areas, test plan, open questions aligned; ..\Lintap path typo normalized); index.md.
Pages created: work/improve-pidstat-collector/design.md (approach, grounded mechanism facts, edge cases, risks incl. the implicit ride-along contract, alternatives, remaining open questions); work/improve-pidstat-collector/implementation_plan.md (8 steps; flags that ../Lintap and ../Wintappy writes need explicit sibling-repo authorization).
Contradictions flagged: none hard. Human decision "output should be parquet" superseded the brief's original preserve-CSV-compatibility goal; reconciled as a deliberate coordinated Wintappy change rather than left as a conflict.

## [2026-08-11] feature-work | improve-pidstat-collector: dev handoff prepared

Source: work-folder artifacts (brief/design/implementation_plan/references), following the dev_handoff skeleton in concept/feature-work-template.md (first use).
Pages created: work/improve-pidstat-collector/dev_handoff.md — written to be self-contained for a fresh agent on a different system: copy/paste prompt activates code-development mode, grants explicit authorization for ../Lintap only (../wintap and ../Wintappy stay read-only this slice), lists environment expectations (sibling checkouts, pidstat/duckdb/shellcheck, no assumed S3), scopes the first slice to implementation plan steps 1–4 with systemd packaging as stretch, and assigns verification.md/implementation_plan.md/log.md upkeep duties.
Pages updated: index.md.
Contradictions flagged: none.
Notes: this is the workflow's first cross-system handoff test; verification.md is intentionally not pre-created — the dev agent creates it from the template when work starts.

## [2026-08-12] code | Improve pidstat collector first slice

Files created: `../Lintap/pidstat-collector.sh`; `../Lintap/tests/pidstat-collector-tests.sh`; `wiki/work/improve-pidstat-collector/verification.md`.
Pages updated: `wiki/work/improve-pidstat-collector/design.md`; `wiki/work/improve-pidstat-collector/implementation_plan.md`; `wiki/index.md`; `wiki/log.md`.
Results: verified Linux ride-along behavior read-only (`CacheManager` upload loop runs when ETL is enabled, shipped `UploadIntervalSec` is 300, shipped `S3Adapter` remains disabled unless deployment config enables it); implemented spool-then-parquet collector in `../Lintap` with wall-clock rotation, startup salvage, and oldest-first accumulation guard; shell tests passed (4); short live smoke run produced readable parquet from real `pidstat` output.
Limitations: `shellcheck` missing on host; no S3 upload exercised; systemd packaging and Wintappy parquet reader change remain later slices.

## [2026-08-12] test | Improve pidstat collector 15-minute run

Command: `timeout --signal=TERM 905 env WINTAP_DATA_ROOT=/tmp/opencode/pidstat-15m.U6zwhN ../Lintap/pidstat-collector.sh`.
Results: collector ran for 15 minutes with default 5-second sampling and 300-second rotation, producing 4 parquet files under `parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=08/`; DuckDB loaded 15 rows across the files.
Manual follow-up: inspect `/tmp/opencode/pidstat-15m.U6zwhN/parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=08/`.

## [2026-08-12] fix | Improve pidstat collector row-loss bug

Diagnosis: the bad 15-minute output was caused by `normalize_pidstat_line()` inheriting the loop's empty `IFS` and using the wrong field count/index for `pidstat` rows. In practice it only retained commands with embedded spaces, which collapsed the dataset to one `tmux: server`-style row per minute.
Fix: made the parser split on explicit shell whitespace and corrected the `Command` field index/count; added a regression test covering normalization inside the collector's `while IFS= read -r line` loop.
Validation: shell test suite now passes with 5 tests, and a post-fix smoke run at `/tmp/opencode/pidstat-fixcheck.YwrUoU` produced 307 rows in ~16 seconds from the real collector.

## [2026-08-12] fix | Improve pidstat collector joined-record recovery

Diagnosis: a later 15-minute run showed occasional conversion failures because some raw `pidstat` chunks arrived with two records glued together at the sample boundary. The parser was treating the second raw record as part of the first row's command payload.
Fix: made `normalize_pidstat_line()` split glued timestamp tokens, detect a next-record start at the command boundary, and emit multiple normalized rows from one joined raw chunk; added a deterministic joined-record regression test plus a live row-preservation validation that checks raw-detail-row count == normalized-row count == parquet-row count.
Validation: shell test suite now passes with 7 tests.

## [2026-08-12] test | Improve pidstat collector clean 15-minute run

Command: `timeout --signal=TERM 905 env WINTAP_DATA_ROOT=/tmp/opencode/pidstat-15m-clean.dyb7fq ../Lintap/pidstat-collector.sh`.
Results: collector ran cleanly for 15 minutes with explicit `-p ALL`, default 5-second sampling, and 300-second rotation. It produced 4 parquet files under `parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=09/`; DuckDB loaded `59097` rows total with per-file counts `4731`, `19839`, `19631`, and `14896`.
Manual follow-up: inspect `/tmp/opencode/pidstat-15m-clean.dyb7fq/parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=09/`.

## [2026-08-12] feature-work | improve-pidstat-collector: slice-1 review accepted, slice-2 handoff prepared

Source: independent review of ../Lintap c76ea87 and this repo's c16c6b7/c77f026 (test suite re-run on reviewer host: 7/7 passed; sibling-repo boundary check clean; parquet schema confirmed against stg_pidstat_metrics + hostname).
Review verdict: slice accepted. Findings: (1) -p ALL sampling deviated from design — accepted per human decision, documented as a post-review decision in design.md with the ETL-layer-reduction rationale (~5.7M rows/day observed baseline); (2) processing-time sample_date gives ~24h-forward timestamps at midnight; (3) partially malformed glued chunks drop valid leading records; (4) DuckDB conversion errors are swallowed. Findings 2-4 assigned to slice 2.
Pages updated: design.md (post-review -p ALL decision; collector-loop command corrected to include -p ALL); verification.md (Independent Review section); implementation_plan.md (renumbered to nine steps, slice-2 scope marked, review follow-ups added as step 6, checklist expanded); dev_handoff.md (rewritten for slice 2: review fixes, systemd, Wintappy DBT parquet migration; authorization widened to ../Lintap + ../Wintappy, ../wintap still read-only); index.md.
Contradictions flagged: none. The dev's deployment finding (S3Adapter disabled in shipped ETLConfig.json) refines rather than contradicts the design's ride-along mechanism; carried into slice-2 scope and the closeout list.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: feature started

Source: raw/Issues/Long_Running_Cleanup.md (~8M process rows over 10 days, ~1/3 with exit codes, CPU-load-grows-with-DB-size hypothesis), plus source inspection of ../wintap/wintap/core/infrastructure/ProcessResolver.cs (insert-on-Start/update-on-Stop, no delete path; ClearDB only called from Windows ProcessSensor.Initialize), EventChannel.cs (per-event ResolveProcessAtTime + GetPidHash fallback hot path), and ProcessSensor.cs (whole-table replay at startup).
Pages created: work/fix-unbounded-process-table-growth/brief.md (problem, integrity constraints, retention + stale-open reconciliation goals, acceptance criteria, open questions, test plan); work/fix-unbounded-process-table-growth/references.md (change-site map, validation baseline, DuckDB space-reclamation questions).
Pages updated: index.md (two new Work rows).
Contradictions flagged: none. Boundary noted: this feature tolerates missed terminations; fixing their sensor-level root cause stays in the lintap-process-creation-validation thread (~3.3% residual open-row baseline, 2026-08-06). The improve-pidstat-collector feature explicitly deferred the event_store cleanup routine to this feature.
Key facts captured: process table is unbounded within and across runs on Linux (no ClearDB call); all hot-path queries filter unindexed process_id; GetPidHash already has a /proc start-time fallback usable after pruning; design/implementation_plan deferred until the brief's open questions (retention window, stale-open policy, cleanup scheduling, DuckDB space reclamation) are decided.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: stale-open policy decided

Source: human decision in conversation.
Decision recorded: the stale-open reconciliation is liveness-check-based (query /proc on Linux / process snapshot on Windows, close rows for dead PIDs with a synthesized exit_time), and the cross-check is to be implemented as an inherent QA feature — each sweep emits telemetry distinguishing rows closed by real Stop events from rows closed by reconciliation, making sensor termination-tracking quality measurable from a running instance. This supersedes the pure age-based alternative.
Pages updated: work/fix-unbounded-process-table-growth/brief.md (Goals decision note, acceptance criterion for QA telemetry, open question closed with remaining design details: sweep cadence and QA telemetry surface).
Contradictions flagged: none. Note: the QA telemetry deliberately takes over the role of the harness-side stop_only_like metric, which the lintap-process-creation-validation thread had flagged as unreliable after pending-exit reconciliation.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: cleanup scheduling left to developer

Source: human decision in conversation.
Decision recorded: where the cleanup/reconciliation sweep runs (ProcessResolver timer vs. merge/upload cycle vs. EventChannel-driven) is explicitly left to the implementing developer's discretion — it is an implementation detail, not an architectural constraint. The chosen mechanism and rationale are to be recorded in design.md or verification notes when decided.
Pages updated: work/fix-unbounded-process-table-growth/brief.md (open question closed with the delegation note).
Contradictions flagged: none.
Remaining open questions in the brief: retention grace window for exited rows, pruned-row lookup fallback/metrics, DuckDB space reclamation behavior, Windows startup-replay constraints, optional hard-cap backstop.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: hand edits reconciled, dev handoff prepared

Source: human edit to work/fix-unbounded-process-table-growth/brief.md (retention-miss open question decided: track as retention-miss metric), reconciled into standard decided-question format; dev_handoff.md written per the feature-work template.
Decisions now recorded (3): liveness cross-check as inherent QA feature; cleanup scheduling at developer discretion; pruned-row lookup misses tracked as retention-miss metric (fallback still fires, misses counted for retention-window tuning).
Pages updated: brief.md (retention-miss decision formatted, matching acceptance criterion added); references.md (Decisions To Date section for the dev agent; /proc liveness marked as the decided reconciliation mechanism; retention-miss note on GetPidHash fallback); index.md (dev_handoff row, references summary refreshed).
Pages created: dev_handoff.md — copy/paste prompt authorizing ../wintap changes (../Lintap and ../Wintappy stay read-only; Wintap-Analytics writable only under validation/ and wiki/), summary of mechanism and hard integrity constraints, delegated decisions (scheduling, cadence, telemetry surface, default retention window, DuckDB reclamation), first slice scoped to sweep + reconciliation + QA telemetry + short validation run, multi-day CPU-correlation study deferred to a later slice, closeout duties including developer-authored design.md recording delegated decisions.
Contradictions flagged: none. Remaining open questions (retention window default, DuckDB reclamation mechanics, Windows replay constraints, hard-cap backstop) are delegated to the dev agent to resolve by measurement and record in design.md.

## [2026-08-13] code | Fix unbounded process table growth first slice

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs`; `validation/process-creation/scripts/summarize_lintap_process_table.py`; `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`.
Pages created: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/implementation_plan.md`; `work/fix-unbounded-process-table-growth/verification.md`.
Pages updated: `index.md`; `log.md`.
Results: implemented resolver-owned periodic maintenance with configurable exited-row retention, liveness-based stale-open reconciliation, in-memory recently-pruned PID cache for retention-miss attribution, and DuckDB telemetry table `process_retention_telemetry` for `stop_closed` / `reconciled_closed` / `retention_deleted` / `retention_miss`. Validation in Multipass `lintap-dev`: `Lintap.csproj` build passed, validation pytest passed (`5 passed`), `Wintap.csproj -p:EnableWindowsTargeting=true` passed after fixing an unrelated missing `using System.IO;` import in `WindowsStateManager.cs`, and a 180-second noisy retention run with aggressive sweep settings produced telemetry totals `stop_closed=507`, `reconciled_closed=28`, `retention_deleted=499` with final process-table size `47` rows.
Limitations: no long-duration plateau/perf run yet, no DuckDB compaction measurement yet, and the short noisy run is not sufficient to tune the final production retention window.

## [2026-08-13] test | Fix unbounded process table growth rundown rerun

Files changed: `validation/process-creation/scripts/summarize_lintap_process_table.py`; `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: summary now reports end-of-run live system process count and open-row liveness classification. Re-checking the earlier short run showed `live_system_processes=143` with the lone tracked-open row classified as stale, clarifying that `open_rows=1` was never a claim that only one Linux process existed. A rerun with `ProcessRundown=true` still ended with `tracked_open_rows=1`, `live_open_rows=0`, `stale_open_rows=1`, while the VM had `live_system_processes=141` and telemetry totals `stop_closed=456`, `reconciled_closed=173`, `retention_deleted=590`.
Open issue surfaced: the new rundown-enabled result suggests a mismatch between rundown-seeded process rows and the liveness-based reconciliation logic, because many apparently live pre-existing processes were counted as reconciliation-closed instead of remaining open/live-tracked.

## [2026-08-13] fix | Add pid_hash to process retention telemetry

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`.
Pages updated: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: `process_retention_telemetry` now stores per-event telemetry rows with `pid_hash` in addition to `metric_name`, `process_name`, and `metric_value`, and the resolver emits telemetry at process-instance granularity rather than only as process-name aggregates. This preserves the existing summary rollups while allowing later joins back to process identity.

## [2026-08-13] fix | Rundown liveness reconciliation accuracy

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `validation/process-creation/scripts/summarize_lintap_process_table.py`.
Pages updated: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Investigation: the new end-of-run summary fields showed that `ProcessRundown=true` initially preserved almost none of the current live process set (`1/141` tracked-open rows in a short run). First fix aligned the resolver's Linux live-start hash derivation with the same `/proc/stat` boot-time basis used by the rundown and exec sensors. That recovered the boot-time process population but still left a subset of long-lived non-boot services (`cron`, `dbus-daemon`, `systemd-networkd`, repeated `sshd`/`sshfs`/`sudo`) being reconciled closed. Final fix made Linux reconciliation use `ProcReader.ReadProcessInfo()` directly and treat close live-start-time matches as the same process instance, preserving or repairing the row instead of closing it.
Validation: a clean 90-second rundown-enabled run (`retention-rundown-fix3b-1786645301`) finished with `live_pids_with_matching_open_row=139/143`, and the previously missing long-lived daemon set stayed open with `exit_time IS NULL`. A 10-minute aggressive-retention run (`retention-rundown-10m-1786645515`) held `live_pids_with_matching_open_row=130/138`; the remaining misses were recent end-of-run processes rather than long-lived baseline services. Telemetry totals for the 10-minute run were `stop_closed=524`, `reconciled_closed=48`, `retention_deleted=541`.
Open follow-up: the remaining small set of misses/stale opens appears to be dominated by shutdown/final-window timing rather than the original rundown identity bug.

## [2026-08-13] fix | End-of-run live snapshot coverage

Files changed: `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`; `validation/process-creation/scripts/summarize_lintap_process_table.py`.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: the validation harness now snapshots `/proc` immediately before shutting down `Lintap` and scores coverage against that pre-stop live process set. This removes the previous measurement artifact where post-stop `python3`/`duckdb` summary processes inflated the apparent miss count. Validation: a snapshot-based 90-second run reached `140/142` live snapshot PIDs covered with `1` stale open row; a snapshot-based 10-minute run reached `131/139` live snapshot PIDs covered with `2` stale open rows. Remaining misses are now a small real tail rather than shutdown-summary self-noise.

## [2026-08-13] validation | Clone sensor closes remaining live-process coverage gap

Files changed: `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: tightened the live snapshot filter further by excluding the snapshot helper's ancestor chain, which produced a clean clone-disabled 90-second run with `135/135` live snapshot PIDs covered. Investigation of the remaining misses on longer clone-disabled runs showed they were fork-without-exec processes. Added a `CLONE_SENSOR` toggle to the validation runner and reran with `Clone=true`: the 90-second run reached `135/135` live snapshot PIDs covered and the 10-minute run reached `137/137` live snapshot PIDs covered, both with `0` missing live PIDs. Conclusion: the currentish process table is accurate at shutdown when the clone sensor is enabled; the prior residual misses were a sensor-selection issue, not a remaining retention/reconciliation defect.

## [2026-08-13] review | fix-unbounded-process-table-growth slice 1 accepted

Source: independent review of ../wintap 9d9c6fb and this repo's 22702eb/3483ab6/4c797b3. Re-verified in lintap-dev: Lintap.csproj build (0 errors), validation pytest (5 passed).
Review verdict: slice 1 accepted. Integrity constraints hold by construction (retention delete cannot touch open rows; reconciliation gated by min-age + live-hash mismatch, with start-time-tolerance repair and collision guard). The QA-telemetry-first design surfaced the rundown reconciliation bug via its own metrics — the design decision paid for itself in slice 1.
Findings (minor): (1) Windows runtime behavior compile-verified only — added to Known Gaps and the closeout checklist; (2) GetLinuxBootTimeUtc caches DateTime.UtcNow if btime is unparseable — silent wrong-hash fallback should not be cached; (3) repair-collision warnings re-log uncapped every sweep.
Pages updated: work/fix-unbounded-process-table-growth/verification.md (Independent Review section; Windows-runtime Known Gap); implementation_plan.md (slice-1 acceptance checked; remaining-before-closeout checklist with promotion candidates: event-store currentish retention semantics + env knobs + process_retention_telemetry, /proc btime hash basis, clone-sensor requirement for fork-without-exec coverage); dev_handoff.md (context list expanded to include design/plan/verification); index.md.

## [2026-08-13] test | Windows process table retention runtime check

Environment: Windows host CHUMBUCKET2; Wintap service deployed from `C:\PUBLIC\wintap` to `C:\Program Files\Wintap`; validation harness run from `C:\PUBLIC\Wintap-Analytics\validation\process-creation` using `uv`.
Commands/actions: `uv run --extra dev pytest`; fixed Windows harness assumptions (`/bin/sh`, `bash`, `sudo duckdb`); fixed current Wintap Windows compile by removing the direct Linux `ProcReader` compile dependency from `ProcessResolver.cs`; `dotnet publish "wintap\Wintap.csproj" -c Debug -r win-x64 --self-contained false`; redeployed Wintap; ran elevated service-mode noisy process workload with aggressive retention settings.
Results: Windows `uv` test suite passed (`5 passed`); Wintap publish passed; service-mode retention run `windows-retention-smoke-20260813143307` produced `390` manifest processes across `35` cases. Final process table had `278` rows (`223` closed, `55` open); `process_retention_telemetry` was present with `reconciled_closed=755` and `retention_deleted=532`. Wintap logs confirmed `ProcessResolver retention: enabled=True` and Windows stale-open reconciliation via `Process.GetProcessById`.
Limitation: this host logged `Log wrap detected! Unable to build process tree, computer reboot required.`, so full Windows `ClearDB` + Security-log startup replay remains unverified; real-time capture, liveness reconciliation, retention deletion, and telemetry were verified.
Pages updated: work/fix-unbounded-process-table-growth/verification.md (marked as `starting-point`); work/fix-unbounded-process-table-growth/implementation_plan.md; index.md; log.md.
Contradictions flagged: none. Cross-feature note: the CPU-vs-table-size correlation step depends on pidstat collector data — pidstat slice 2 (systemd + Wintappy parquet migration) is still pending and unblocks the correlation study.

## [2026-08-13] update | Interview stage added to LLM-assisted feature workflow

Pages updated: `concept/llm-assisted-feature-workflow.md` (new Interview stage row in the stages table; new Interview Stage section defining the protocol — ground in wiki/repo context first, ask adaptive 2–4-question batches, classify answers as decision/constraint/delegated/deferred, stop when the brief can be stated without guessing, play back for confirmation before writing brief.md; invocation now runs the interview by default with a `(no interview)` opt-out); `concept/feature-work-template.md` (optional `interview.md` artifact added to the skeleton list plus a condensed-log template with Interview Log rounds, Decisions/Constraints/Delegations/Deferred sections, and Playback Summary); `AGENTS.md` (wiki-maintainer-mode invocation description now includes the interview step and opt-out); `index.md` (concept summaries refreshed).
Contradictions flagged: none. Rationale: the workflow previously jumped straight from the invocation phrase to skeleton creation, leaving the agent to guess brief content; the interview makes context-building between human and AI an explicit first-class stage while keeping brief.md the single distilled source of truth.

## [2026-08-13] feature | improve-windows-process-collection started via LLM-assisted feature workflow

Pages created: `work/improve-windows-process-collection/interview.md`, `brief.md`, `references.md`, `design.md`. Pages updated: `index.md`; `log.md`.
Interview (3 rounds, all decisions confirmed by human playback): kernel ETW (classic NT Kernel Logger Process events on the shared KernelSession) becomes the single real-time source for process lifecycle; the Security-log 4688/4689 path and the separate KernelProcessSensor are consolidated into one new WindowsProcessSensor (rich stop metrics retained via a manifest-provider subscription); Refresh moves from Security-log tree reconstruction to a live snapshot with exact create times; UserSID comes from the validated sid-extraction-test POC at C:\PUBLIC\sid-extraction-test (technique proven, drops in as-is); command line uses ProcessTraceData.CommandLine with live PEB fallback; boot-time coverage via Global Logger boot ETL ingestion is in scope (opt-in setting for slice 1); verification via a Windows adaptation of the sensor-neutral validation harness. Hard constraint: no WintapMessage/ProcessObject schema or PidHash changes; TraceEvent stays at 3.1.23.
Motivation (all four confirmed): stops commented out on the Security-log path, fragile since-boot reconstruction (log-wrap "reboot required" — observed live on CHUMBUCKET2 2026-08-13), event-log-time PidHash corruption, and audit-policy dependency.
Next stage: implementation_plan.md + dev_handoff.md, then implementation and verification.

## [2026-08-13] feature-work | improve-windows-process-collection: implementation plan and dev handoff added

Pages created: `work/improve-windows-process-collection/implementation_plan.md` (three slices mapped to wintap P2.1–P2.8 instruction units — slice 1 P2.1–P2.6: SID helper, sensor core, snapshot refresh, enrichment, stop-metrics merge, wire-in/removal; slice 2 P2.7: opt-in Global Logger boot ETL; slice 3 P2.8: Windows validation harness — each unit sized for one approved instruction document with xUnit tests tagged `[Trait("Category", "P2.x")]` and a done checklist); `work/improve-windows-process-collection/dev_handoff.md` (bridges the Analytics feature artifacts to the wintap Architect/Engineer/Developer loop per `../wintap/CLAUDE.md`: per-unit Engineer dispatch prompt with a P2.1 copy/paste example, primary sources per unit, P2.1-first recommendation, testing gates, and closeout/audit duties).
Pages updated: index.md (two new Work rows); log.md.
Contradictions flagged: none.
Next stage: dispatch the wintap Engineer for the P2.1 instruction document using the handoff prompt, then run the approve/implement/audit loop per unit.

## [2026-08-14] diagnostic | RHEL 8 field test: clone sensor attach, fork-without-exec signature, suspected fork storm

Source: operator-reported Lintap logs from the first real-machine RHEL 8 test (2026-08-14), plus source inspection of CloneSensor.cs, BaseEbpfSensor.cs, clone_tracer.bpf.c, and ../Lintap/packaging/lintap-rpm/lintap.env.
Pages created: diagnostic/rhel8-clone-sensor-and-fork-without-exec.md — three findings: (1) the EventChannel warn signature parentPid = childPid−1 identifies fork-without-exec processes invisible to exec-only sensing, matching the VM-validated clone-sensor coverage requirement; (2) the clone sensor's sched_process_fork attach succeeds on RHEL 8, so the Fedora failure behind the opt-out packaging default does not generalize (candidate: revisit the lintap.env default); (3) warnings persisted ~7 min after clone enable — PID-range rate analysis (~450-700 PIDs/sec per stream, observed wrap at pid_max 4,194,304) suggests a fork storm with multi-minute event-processing lag on a nominally idle machine, with pre-enable backlog and PID namespaces as competing explanations; decisive checks recorded (fork-rate from /proc/stat, top forking parents from raw_process parquet).
Pages updated: work/lintap-process-creation-validation/index.md (field-finding pointer); index.md.
Contradictions flagged: none hard. The packaging comment "sched_process_fork attach failed on Fedora" stands but is now known to be Fedora-specific, not general.
Notes: retention feature ruled unlikely as a contributor by the warn signature; process_retention_telemetry query recorded as the standard rule-out for future triage.

## [2026-08-14] diagnostic | Fork storm root cause: pidstat-collector per-line command substitutions

Source: operator-run top-forkers query on the RHEL 8 machine (bash and date, both root, top 2 in raw_process), matched against ../Lintap/pidstat-collector.sh source structure.
Root cause: the collector's hot loop executes ~7 command-substitution subshells per pidstat output line, two exec'ing date (~700 forks/sec at -p ALL on ~500 processes). This matches the measured PID-advance rate, the top-forker names, and the parentPid = childPid−1 warn signature (each $(...) subshell is a fork-without-exec bash that forks date). The observability collector was flooding the sensor it feeds; raw_process data from affected runs is polluted (bash/date dominate) and unfit for process-mix conclusions.
Pages updated: diagnostic/rhel8-clone-sensor-and-fork-without-exec.md (Root Cause section replacing the fork-storm/namespace open question; remaining open items: confirm fork-rate collapse after stopping the collector, and whether the observed multi-minute event lag at ~700 events/sec merits a sensor-capacity investigation); work/improve-pidstat-collector/implementation_plan.md (new CRITICAL slice-2 step 6b: fork-free hot loop — global-variable normalize, printf '%(%s)T' epoch, window-epoch date column merging the midnight fix, plain path variables, plus a no-child-processes regression guard).
Contradictions flagged: none. Reviewer note: the 2026-08-12 slice-1 review flagged conversion cost but missed the per-line fork cost — recorded here so the review checklist for shell collectors includes hot-loop fork auditing.
Notes: clone-sensor-on-RHEL-8 finding (attach works) is unaffected and stands on its own.

## [2026-08-14] decision | pidstat collector slice 2 redefined: Python rewrite

Source: human decision following the fork-storm diagnosis (diagnostic/rhel8-clone-sensor-and-fork-without-exec.md) — bash+duckdb-CLI stays conceptually but the implementation moves to a single-process Python collector using the duckdb Python API, for fork elimination and readability.
Pages updated: work/improve-pidstat-collector/design.md (new decision section: rationale, carried-over slice-1 semantics restated as requirements, bash pidstat-collector.sh retired while pidstat-collect.sh remains the example; DuckDB-CLI-vs-Python open question resolved; new open question: Python runtime/packaging given RHEL 8's default python3.6 vs duckdb wheel requirements); implementation_plan.md (step 6 rewritten as the Python rewrite absorbing all three review findings, step 6b as the pytest port incl. midnight case and fork regression guard; checklist, files-to-change, and tests sections aligned); dev_handoff.md (slice-2 prompt rewritten: hard single-process requirement, delete-the-bash-collector instruction gated on tests passing, runtime/packaging decision assigned to the dev); index.md.
Contradictions flagged: none. The slice-1 acceptance stands — its behavior and test suite become the specification the Python port must satisfy.

## [2026-08-14] investigation | pidstat collector telemetry source options + container attribution

Source: human questions (is pidstat still the right source for the Python collector? can we get container info?), answered with live verification on lintap-dev: /proc/<pid>/stat (52 fields incl. minflt/majflt, delayacct_blkio_ticks, guest_time), /proc/<pid>/io, /proc/<pid>/status ctx switches, /proc/<pid>/schedstat, /proc/<pid>/cgroup (v2 unified here; v1/hybrid on RHEL 8), /proc/<pid>/ns/pid readlink; psutil API inspection (no page faults, no guest time, no iodelay on Linux).
Findings: three source options recorded in design.md — A keep-pidstat-child (full schema, one child, text parsing), B stdlib /proc sampler (full schema, zero children, zero new deps, owns rate math), C psutil (schema-incomplete, not recommended). Container attribution (cgroup_path, pid_ns_inode, best-effort runtime/id) is only available via /proc — effectively deciding for option B; new columns coordinate with the same-slice Wintappy bronze migration so the schema changes once. Recommendation: implement B behind a sampler interface with pidstat retained as side-by-side test oracle.
Pages updated: work/improve-pidstat-collector/design.md (Telemetry Source Investigation + Container Attribution sections); brief.md (container-attribution goal added); references.md (proc(5), psutil evaluation); implementation_plan.md (step 6 source-selection + container columns; checklist items); dev_handoff.md (source-selection and container requirements in the copy/paste prompt); index.md. last_validated bumped to 2026-08-14 across the feature artifacts.
Contradictions flagged: none. Note: container/namespace-tagged rows would also let the RHEL 8 diagnostic's interleaved-PID-range question be answered from collector data directly.

## [2026-08-15] feature-work | fix-upload-cache-deletion started; pidstat mechanism fact corrected

Source: overnight RHEL 8 field test (S3 uploader re-sending the same data every cycle) plus code review of ../wintap/wintap/core/etl/load/ (CacheManager.cs, adapters/S3Adapter.cs, SMBFileShareAdapter.cs, SignedS3UrlAdapter.cs, interfaces/IUpload.cs).
Root cause: the delete-after-upload path is dead code — CacheManager subscribes Uploader_UploadCompleted (which deletes), but no adapter ever raises the event (declared-only in S3/SMB adapters; the sole Invoke is commented out in SignedS3UrlAdapter). CacheManager.upload() sets successfulUpload ("any success = all success, for now") and never reads it — the intended delete site. Only pruneCache()'s 256MB cap removes files, and its free-space check uses Windows drive-letter logic, suspect on Linux.
Pages created: work/fix-upload-cache-deletion/brief.md (evidence with GROUND_TRUTH pointers, goals incl. Linux prune fix and empty dayPK/hourPK dir removal from the Long_Running_Cleanup issue, acceptance criteria incl. overnight single-upload validation); work/fix-upload-cache-deletion/dev_handoff.md (../wintap core/etl/load authorization, recommended inline-delete fix shape with the mid-loop event-raise anti-pattern called out, dead-event decision delegated).
Pages corrected: work/improve-pidstat-collector/design.md — the 2026-08-11 mechanism fact "Uploader_UploadCompleted deletes each parquet after successful upload" was true of the handler code but false in effect (event never fires); struck through with dated correction. brief.md bounded-disk goal corrected (accumulation guard is the effective bound); dev_handoff.md known-issue note added; implementation_plan.md S3 end-to-end checklist item marked blocked on the new feature.
Pages updated: index.md (two new Work rows).
Contradictions flagged: one, resolved by correction — recorded mechanism fact contradicted observed field behavior; lesson noted: handler-exists-and-subscribed is not evidence the event fires; verify the raise site when grounding event-driven claims.

## [2026-08-15] review | Upload subsystem robustness pass folded into fix-upload-cache-deletion

Source: follow-up code review of ../wintap/wintap/core/etl/load/ (CacheManager doMerge/HangDetector/pruneCache/getFreeBytes/getCurrentCacheDirSize, S3Adapter client lifecycle and retry, upload loop).
Additional findings (prioritized into the feature): (1) HangDetector_Elapsed deletes ALL parquet under the parquet root on a hung merge — un-uploaded raw_sensor and future pidstat data included; restrict to unmerged working dirs. (2) pruneCache off-by-one (breaks before deleting the threshold-crossing file), cap measured against whole-cache size while deleting only raw_sensor parquet (unreachable-target risk), hardcoded 256MB cap, unused drive-letter getFreeBytes dead code. (3) Unguarded PostUpload loop can silently kill the upload thread; empty catch in delete handler; upload failures logged at Info. (4) Zero-byte parquet files skipped by upload become permanent stragglers post-fix. (5) Double directory enumeration per cycle. Verified-sound and explicitly out of scope: S3 client per-cycle lifecycle, 429 backoff+jitter, credentials, key mirroring, .Result pattern.
Pages updated: work/fix-upload-cache-deletion/brief.md (goals expanded with GROUND_TRUTH pointers; acceptance criteria for merge-hang scoping, prune accounting, PostUpload resilience; deployment note re one-time backlog drain on machines that ran the broken version); dev_handoff.md (cleanup items in priority order with a do-not-change list); index.md.
Contradictions flagged: none.

## [2026-08-15] update | fix-upload-cache-deletion: Windows considerations made explicit

Source: human question (does the design account for Windows?) plus source confirmation that PluginManager (shared core) constructs WintapETL/CacheManager on both platforms — Windows Wintap runs the identical upload path and has the identical re-upload bug.
Assessment: the fix is platform-neutral by construction (shared code; case-insensitive globs and path→S3-key separator normalization already handled), with three Windows specifics now stated explicitly: transient file-lock tolerance on delete (AV/indexer — log, retain, retry next cycle, never kill the upload thread); Directory.Delete failure tolerance for empty-dir removal (which also makes the new-file race safe on both platforms); and a Windows service-mode verification run (same setup as the 2026-08-13 retention check) confirming delete-after-upload across ≥3 cycles.
Pages updated: work/fix-upload-cache-deletion/brief.md (Windows acceptance criteria); dev_handoff.md (Windows correctness requirement + verification addition).
Contradictions flagged: none.

## [2026-08-15] code | Improve pidstat collector slice 2

Files changed: `../Lintap/pidstat-collector.py` (new), `../Lintap/pidstat-collector.sh` (deleted), `../Lintap/tests/test_pidstat_collector.py` (pytest port), `../Lintap/pyproject.toml`, `../Lintap/.python-version`, `../Lintap/README.md`, `../Lintap/packaging/lintap-{rpm,deb}/*pidstat*`, `../Wintappy/wintap_dbt/macros/pidstat.sql`, `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql`, `../Wintappy/Makefile`, `../Wintappy/wintap_dbt/README.md`, plus this feature's work artifacts.
Results: rewrote the collector in Python around a zero-child `/proc` sampler and DuckDB Python conversion; preserved the slice-1 env/spool/partition/salvage/accumulation semantics; added hostname + container attribution columns; ported the test suite to pytest with pidstat-oracle, midnight, and fork-regression coverage; added pinned-interpreter systemd units; migrated Wintappy pidstat bronze from CSV to parquet and validated both fixture and empty-input paths in `lintap-dev` using `uv`.
Limitations: the pinned `/usr/bin/python3.11` unit path could not be started on the Ubuntu 24.04 validation VM because that interpreter is not installed there; live container fixture coverage and S3/delete-after-upload closeout remain open.

## [2026-08-15] update | Improve pidstat collector runtime packaging switched to uv-managed venv launcher

Source: follow-up implementation request after the hardcoded `/usr/bin/python3.11` path proved too brittle for mixed-host deployment.
Files changed: `../Lintap/pidstat-collector-bootstrap.sh` (new), `../Lintap/pidstat-collector-launch.sh` (new), `../Lintap/packaging/lintap-{rpm,deb}/lintap-pidstat.service`, both `lintap.env` files, packaging READMEs/build scripts, top-level `../Lintap/README.md`, and this feature's work artifacts.
Results: removed the host-interpreter pin; service now launches the collector through `/bin/bash /usr/lib/lintap/pidstat-collector-launch.sh`, which resolves `PIDSTAT_VENV_DIR` and execs the collector from a dedicated `uv`-managed venv. Added `pidstat-collector-bootstrap.sh` to create that venv and install DuckDB, defaulting to `PIDSTAT_BOOTSTRAP_PYTHON=3.12` so the runtime stays within the collector's supported `>=3.11,<3.13` range. Validated in `lintap-dev`: bootstrap created a 3.12.3 venv, launcher produced parquet successfully, and a temp unit with the new `ExecStart` shape passed `systemd-analyze verify`.
Limitations: still not a full package-install/reboot test; the real packaged service must be exercised on a target host later.

## [2026-08-16] review | improve-pidstat-collector slice 2 accepted

Source: independent review of ../Lintap 8eaae5c and ../Wintappy ccbf783 (both on grantj-rhel8-testing) plus this repo's slice-2 wiki commits. Re-verified: pytest 12/12 in ../Lintap (uv, python 3.12).
Review verdict: slice 2 accepted; feature is code-complete. The dev implemented telemetry option B (zero-child /proc sampler) with container attribution, verified stat-field offsets correct against proc(5), pidstat-matching rate semantics (guest-excluded %usr, schedstat-based %wait, delta-tick iodelay), PID-reuse handling via starttime, in-process duckdb conversion with atomic replace and full traceback logging, and all three carried review findings absorbed. Wintappy bronze matches spec (read_parquet + filename provenance + container columns + empty-input typed table). Packaging pivoted mid-slice from a pinned /usr/bin/python3.11 to a uv-managed 3.12 venv bootstrap/launcher after field brittleness — decision properly recorded. Boundary check clean (no pidstat changes in ../wintap).
Findings (minor): (1) enforce_accumulation_guard stats files without FileNotFoundError tolerance and runs inside the conversion try — a real race once the upload fix has the sensor deleting concurrently, with a misleading error attribution; queued as a checklist follow-up. (2) Open items honestly tracked: live container fixture, target-host systemd install/reboot, S3 end-to-end (blocked on fix-upload-cache-deletion).
Pages updated: work/improve-pidstat-collector/verification.md (slice-2 Independent Review section); implementation_plan.md (container/systemd checklist reconciliation, acceptance line, guard-race follow-up); design.md (Summary rewritten to match the shipped Python/proc-sampler reality and the pending-deletion caveat); index.md.
Contradictions flagged: none.

## [2026-08-16] query | Small parquet files are merged before upload — no new task

Source: human question (are the frequent small parquet files merged before upload?), answered from ../wintap/wintap/core/etl/load/Merge.cs, CacheManager.cs (doMerge before upload each cycle), RawSensorWriter.cs, and ETLConfig.json.
Answer: yes on both paths. Serializer flush files (SerializationIntervalSec, shipped default 60s — the wiki's "10-second" figures refer to event aggregation windows, not file cadence) are consolidated by doMerge into one file per event type per upload cycle before the sweep; the pidstat collector writes one file per rotation window by construction, matching that granularity. Upload unit is ~12 files/type/hour. No next-slice task added. Optional future consolidation to hourly files (~12× fewer S3 objects, up to 1h local latency) noted in conversation but deliberately not queued.
Pages updated: work/improve-pidstat-collector/design.md (merge-before-upload added to verified mechanism facts).
Contradictions flagged: none.

## [2026-08-16] code | fix-upload-cache-deletion first implementation pass

Source: code-development pass on branch `grantj-rhel8-testing` in `../wintap`, driven by the feature handoff and brief.
Files changed: `../wintap/wintap/core/etl/load/CacheManager.cs`, `interfaces/IUpload.cs`, `adapters/S3Adapter.cs`, `adapters/SMBFileShareAdapter.cs`, `../wintap/wintap/core/etl/model/ETLConfig.cs`, `../wintap/wintap/core/etl/ETLConfig.json`, `../wintap/wintap/core/etl/shared/Utilities.cs`, plus this feature's `brief.md`, new `verification.md`, and `index.md`.
Results: delete-after-upload moved inline to `CacheManager.upload()` after the full uploader loop, preserving the existing any-success policy; dead `UploadCompleted` event plumbing removed from the active load path; zero-byte files now delete instead of spinning forever; empty partition dirs are pruned after delete; `pruneCache()` now measures `raw_sensor` size, deletes the threshold-crossing file, uses a configurable cap, and protects current-window files; merge-hang cleanup now skips `raw_sensor/`, `csv/`, and `merged/`; `PostUpload()` calls are guarded per uploader. Verified in `lintap-dev`: `dotnet build Lintap.csproj -warnaserror:CS0067` passed. `Wintap.csproj -p:EnableWindowsTargeting=true` remains blocked in this VM by unrelated Windows-target dependency issues.
Limitations: no live uploader target was exercised yet, so single-upload-plus-delete across >=3 cycles still needs target-host verification.

## [2026-08-17] update | improve-windows-process-collection: unit IDs renamed P2.x → wpc-nn

Source: Architect decision in the wintap main session — the P-major numbering was judged unintuitive. New scheme combines the descriptive-slug pattern used by this wiki's Linux feature threads (kebab-case feature names, numbered steps, slices) with the semantic-prefix precedent already in ../wintap's architecture assessment (DEC-/OQ-/INV-).
Scheme: `<feature-abbrev>-<nn>` unit IDs with a descriptive slug in filenames; this feature's abbreviation is `wpc` (windows-process-collection), units wpc-01…wpc-08. xUnit traits become `[Trait("Category", "wpc-<nn>")]`; one unit runs via `dotnet test --filter "Category=wpc-01"`, the whole feature via `Category~wpc`. Instruction docs `developer_docs/instructions/wpc-<nn>-<slug>.md`; audits `developer_docs/audits/wpc-<nn>-<slug>.md`. The wintap bootstrap unit P1.1 (merged, tested, audited) is grandfathered under the old naming.
Pages updated: work/improve-windows-process-collection/implementation_plan.md and dev_handoff.md (all P2.1–P2.8 references renamed, feature abbreviation declared, whole-feature filter documented); index.md (row summaries and Last updated line).
Contradictions flagged: none. ../wintap CLAUDE.md gains the unit-naming convention alongside its existing P1.1 examples.
Next stage: dispatch the wintap Engineer for the wpc-01 instruction document using the handoff prompt, then run the approve/implement/audit loop per unit.

## [2026-08-17] instruction | [wintap] wpc-01 SID helper instruction drafted

Decisions made: Architect approved the wpc-01 instruction for Developer handoff. Drafted the first implementation unit for the improve-windows-process-collection feature from the already-settled Analytics feature design. Kept the unit narrow: port the validated classic kernel ETW `ProcessTraceData` UserSID parser and add synthetic payload tests only; no sensor wiring, account-name lookup, token fallback, command-line fallback, or PidHash/process schema changes.
ADRs written or updated: none.
Wiki pages updated: none beyond this log.
Instructions written: `../wintap/developer_docs/instructions/wpc-01-sid-helper.md` (Status: Approved — Architect approval 2026-08-17).
Scratch notes: `wiki/work/improve-windows-process-collection/sid-helper-notes-2026-08-17.md` (migrated from `../wintap/dave-wiki/sources/2026-08-17-wpc-01-sid-helper-notes.md`).
Open questions: none for wpc-01. The Developer can implement wpc-01 and verify with `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-01"`.

## [2026-08-17] audit | [wintap] wpc-01 SID helper completed

Decisions made: none. Developer completed the approved wpc-01 unit as specified: added the classic kernel ETW `ProcessTraceData` UserSID extraction helper, added the internal payload-parser test seam, and added synthetic xUnit coverage for extracted SIDs, null-SID markers, and malformed payload guards. No sensor wiring, schema changes, PidHash/process hash changes, TraceEvent upgrade, or new NuGet dependencies were introduced.
ADRs written or updated: none.
Wiki pages updated: none beyond this log; no new architecture decision was made by the implementation.
Instructions written: none.
Audit artifact: `../wintap/developer_docs/audits/wpc-01-sid-helper.md` (Status: Complete).
Verification: `dotnet build -c Release` passed from `../wintap/tests/Wintap.Tests`; `dotnet test --filter "Category=wpc-01"` passed with 9/9 tests selected and passing.
Open questions: none for wpc-01. Next Windows process-collection unit can wire the helper into the chosen process sensor path.

## [2026-08-17] maintenance | Consolidate Wintap developer wiki into Analytics wiki

Decisions made: recorded the Architect-settled decision that `../Wintap-Analytics/wiki/` is the single Wintap ecosystem knowledge base, that `../wintap/dave-wiki/` is retired, that Wintap instructions/audits intentionally remain in `../wintap/developer_docs/`, and that the Wintap Engineer is authorized to write to `../Wintap-Analytics/wiki/`.
ADRs written or updated: `wiki/decision/consolidate-developer-wiki-into-analytics-wiki.md`; migrated `wiki/decision/process-identity-attribution-contract.md`; migrated `wiki/decision/test-project-structure-and-first-test.md`.
Wiki pages updated: `wiki/work/improve-windows-process-collection/sid-helper-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`; `../Wintap-Analytics/AGENTS.md`; Wintap repo plumbing docs `../wintap/CLAUDE.md`, `../wintap/.claude/agents/engineer.md`, and `../wintap/.claude/agents/developer.md`; tombstoned `../wintap/dave-wiki/README.md`.
Instructions written: none.
Open questions: none. Historical `../wintap/developer_docs/instructions/` and `../wintap/developer_docs/audits/` files were intentionally not rewritten; stale `dave-wiki` references there are covered by the tombstone.

## [2026-08-17] instruction | [wintap] wpc-02 sensor core instruction drafted

Decisions made: none. Drafted the wpc-02 instruction from the already-settled improve-windows-process-collection design: add a new `WindowsProcessSensor` core that subscribes classic kernel ProcessStart/ProcessStop on the shared NT Kernel Logger parser, canonicalizes create time with `GetProcessTimes` first and ETW timestamp fallback, keeps an in-memory PID instance map, emits Start/Stop process events, and tests canonicalization fallback, PID-reuse replacement, and Stop-without-Start fallback paths through minimal internal seams.
ADRs written or updated: none. Flagged a decision tension in the draft: the older process identity ADR says core owns PidHash/ParentPidHash generation, while the current WPC feature design and existing sensor practice require sensor-side PidHash population using the unchanged formula.
Wiki pages updated: `wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`.
Instructions written: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` (Status: Draft; Architect approval pending).
Open questions: Architect should explicitly approve or revise the flagged PidHash ownership tension before Developer handoff if the wording is not acceptable. The proposed verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-02"`.

## [2026-08-17] decision | [wintap] wpc-02 live Start time canonicalized to ETW timestamp

Decisions made: Architect selected option 1 for wpc-02 create-time canonicalization: use the classic kernel ETW ProcessStart timestamp as the canonical live Start time for `PidHash` generation. Do not perform `OpenProcess` / `GetProcessTimes` on every process create. Rationale: Wintap has used ETW as process-start ground truth for over 13 years, it has proven reliable, and per-create handle lookups add hot-path performance risk. Snapshot Refresh still uses live process create times and must deduplicate/repair against live Starts by PID + create-time tolerance in the later snapshot unit.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/brief.md`; `references.md`; `design.md`; `implementation_plan.md`; `sensor-core-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` revised to remove per-Start `GetProcessTimes`, remove the process-accessor test seam, and require ETW timestamp canonicalization tests.
Open questions: wpc-02 instruction remains Draft / Architect approval pending as a whole.

## [2026-08-17] decision | [wintap] wpc-02 uses ProcessResolver as sole hot-path identity store

Decisions made: Architect selected `ProcessResolver` for the wpc-02 hot path instead of a sensor-owned in-memory PID map. Starts emit through `EventChannel.Send` so `ProcessResolver` registers the process instance. Stops resolve identity through `EventChannel.GetProcessHistory(pid, stopTimeUtc)` / `ProcessResolver` before emission; resolver misses are counted and fall back to hash-from-stop-time. Rationale: avoid introducing a parallel lifecycle cache when the project already has a PID-reuse-safe resolver designed for process identity.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/references.md`; `design.md`; `implementation_plan.md`; `dev_handoff.md`; `sensor-core-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` revised to remove the in-memory PID instance map requirement and replace PID-reuse map tests with resolver-selected-instance tests.
Open questions: wpc-02 instruction remains Draft / Architect approval pending as a whole.

## [2026-08-17] approval | [wintap] wpc-02 sensor core instruction approved

Decisions made: Architect approved the revised wpc-02 instruction for Developer handoff. Final approved scope: new `WindowsProcessSensor` subscribing classic kernel ProcessStart/ProcessStop on the shared kernel parser; ETW ProcessStart timestamp is canonical for live Start `PidHash`; no per-Start `GetProcessTimes`; `ProcessResolver` is the sole hot-path identity store; Stop resolver misses are counted and fall back to hash-from-stop-time. No schema, PidHash formula, TraceEvent version, or NuGet dependency changes.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` (Status: Approved — Architect approval 2026-08-17).
Open questions: none for wpc-02 instruction handoff. Developer verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-02"`.

## [2026-08-17] audit | [wintap] wpc-02 sensor core completed

Decisions made: none. Developer completed the approved wpc-02 unit: added `WindowsProcessSensor` core under `../wintap/wintap/platform/windows/sensor/etw/`, added shared-kernel ProcessStart/ProcessStop subscription, ETW-timestamp Start canonicalization, resolver-backed Stop identity stamping, Stop resolver miss counting, and hash-from-stop-time fallback. Runtime wire-in and old sensor deletion remain deferred to wpc-06 as planned.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/implementation_plan.md`; `wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17.md`; `wiki/log.md`.
Instructions written: none.
Audit artifact: `../wintap/developer_docs/audits/wpc-02-sensor-core.md` (Status: Complete).
Verification: `dotnet build "wintap\Wintap.csproj" -c Release -p:WarningLevel=0` passed; from `../wintap/tests/Wintap.Tests`, `dotnet test --filter "Category=wpc-02" --logger "console;verbosity=detailed"` selected and passed 5/5 tests. The audit records a verification-command deviation: repo-root `dotnet build -c Release` / root filtered test target `Wintap.sln`, which currently fails under .NET SDK MSBuild on the existing `Wintap-Workbench` website project (`MSB4249`), so project-scoped equivalents were used. The audit also records a narrow internal `genPidHash` test seam to avoid elevation-sensitive `StateManager` initialization; production still defaults to unchanged `ProcessHash.GenPidHash`.
Open questions: none for wpc-02. Next unit is wpc-03 snapshot refresh.


## [2026-08-17] instruction | [wintap] wpc-04 field enrichment instruction approved

Decisions made: none. Architect requested and approved the wpc-04 instruction for Developer handoff. Scope is field enrichment on the already-landed `WindowsProcessSensor`: SID/user via wpc-01 helper, `LookupAccountSid` with bounded SID cache, token fallback for NoSid/Malformed, ETW command line with PEB fallback, and executable path via `QueryFullProcessImageName` with device-path translation fallback. The instruction preserves settled WPC constraints: no schema changes, no PidHash formula changes, TraceEvent stays 3.1.23, no new NuGet dependencies, resolver-backed sensor, runtime wire-in deferred to wpc-06, Stop metrics deferred to wpc-05, boot ETL deferred to wpc-07.
ADRs written or updated: none.
Wiki pages updated: `wiki/log.md` only.
Instructions written: `../wintap/developer_docs/instructions/wpc-04-field-enrichment.md` (Status: Approved — Architect approval 2026-08-17).
Open questions: none for wpc-04 instruction handoff. Developer verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-04"`, with the documented project-scoped fallback if the known `Wintap-Workbench` `MSB4249` solution-level issue appears.

## [2026-08-17] instructions | wpc-05 stop metrics merge draft

Source: Wintap Engineer instruction-draft session for `improve-windows-process-collection` unit wpc-05, with context from `wiki/work/improve-windows-process-collection/{brief,design,implementation_plan,dev_handoff}.md`, prior audits `../wintap/developer_docs/audits/wpc-02-sensor-core.md`, `wpc-03-snapshot-refresh.md`, `wpc-04-field-enrichment.md`, and source inspection of `../wintap/wintap/platform/windows/sensor/etw/{WindowsProcessSensor,ProcessSensor,KernelProcessSensor}.cs` plus resolver/test references.
Instruction written: `../wintap/developer_docs/instructions/wpc-05-stop-metrics-merge.md` as Draft/Pending approval. It scopes manifest `Microsoft-Windows-Kernel-Process` keyword `0x10` ProcessStop metrics correlation into resolver-backed kernel Stop emission, carries forward the old `parseUserModeProcessStop` metric list, requires wpc-05 tests, and preserves no-schema/no-PidHash/no-TraceEvent-upgrade/no-new-dependency constraints.
Pages updated: `wiki/log.md` only.
Notes: Implementation-plan checklist intentionally not updated; that remains closeout work after Developer implementation/audit.

## [2026-08-17] approval | [wintap] wpc-05 stop metrics merge instruction approved

Decisions made: Architect approved the wpc-05 instruction for Developer handoff. Scope is manifest `Microsoft-Windows-Kernel-Process` keyword `0x10` ProcessStop metric subscription and nearest-in-time PID correlation into resolver-backed kernel Stop emission, with a named 5-second window, non-blocking expiry/default emission, and `manifest_metric_misses` counting. The instruction preserves settled WPC constraints: no schema changes, no PidHash formula changes, TraceEvent stays 3.1.23, no new NuGet dependencies, no sensor-owned PID instance map, and runtime wire-in/removal deferred to wpc-06.
ADRs written or updated: none.
Wiki pages updated: `wiki/log.md` only.
Instructions updated: `../wintap/developer_docs/instructions/wpc-05-stop-metrics-merge.md` (Status: Approved — Architect approval 2026-08-17).
Open questions: none for wpc-05 instruction handoff. Developer verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-05"`, with the documented project-scoped fallback if the known `Wintap-Workbench` `MSB4249` solution-level issue appears.

## [2026-08-17] process | AI velocity/ROI mini-lab codified

Decisions made: Architect-approved ROI/velocity mini-lab protocol recorded for the LLM-assisted feature workflow. The protocol uses sealed human and AI estimates at feature open, AI design/development and per-unit estimate splits, main-session 15-minute-gap attention-proxy actuals, a three-question hard cap with displacement ratchet, never-gates behavior, close-out reveal/tabulation, and one planned template revision after the next real feature trial.
ADRs written or updated: `wiki/decision/ai-velocity-roi-mini-lab.md` (Accepted).
Wiki pages updated: `wiki/concept/llm-assisted-feature-workflow.md`; `wiki/concept/feature-work-template.md`; `wiki/concept/metrics-template.md`; `wiki/index.md`; `wiki/log.md`.
Wintap process docs updated for Architect review: `../wintap/.claude/agents/engineer.md`; `../wintap/CLAUDE.md`.
Contradictions flagged: none. Notes: the Wintap-side process-doc edits are outside the standard directory-ownership table and are drafted for explicit Architect review, per the ADR ownership note.
Open questions: none for codification; the next real feature is the live trial, after which templates get one planned revision pass.

## [2026-08-17] metrics | [wintap] WPC velocity/ROI retrofit

Decisions made: none. Retrofitted the current `improve-windows-process-collection` feature with mini-lab metrics after the protocol was adopted. The human estimate and reported Design-AI estimate both put solo, no-AI implementation at 3 weeks; recorded as 120 hours assuming 40-hour weeks. Because this was retrofitted after feature open and after the estimate was disclosed, the sealed/independent estimate discipline is explicitly marked broken for this feature.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/interview.md`; `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/index.md`; `wiki/log.md`.
Instructions written: none.
Open questions: human predicted AI-attention estimate was not captured; main-session attention proxy, API cost, close-out question, and per-unit actual hours remain for close-out. Per-unit estimates for wpc-01 through wpc-06 are missing because they were already implemented before the retrofit; wpc-07 has a pre-implementation estimate, and wpc-08 should receive one when its instruction is drafted.

## [2026-08-17] audit | [wintap] wpc-05 and wpc-06 completed — slice 1 of improve-windows-process-collection done

Decisions made: none new. Developer completed the approved wpc-05 (stop-metrics merge) and wpc-06 (wire-in and legacy removal) units; both landed in wintap develop-dave commit 0f273e0 (2026-08-17). Slice 1 (wpc-01 through wpc-06) is complete: the unified `WindowsProcessSensor` is live as the sole Windows process lifecycle sensor — resolver-backed classic kernel ETW Start/Stop, snapshot Refresh with ClearProcessDB-then-Refresh preserved, SID/command-line/path enrichment, manifest-provider Stop metric merge, and QA counter interval/shutdown logging. Legacy `ProcessSensor.cs` (Security-log 4688/4689) and `KernelProcessSensor.cs` were deleted with their settings entries and dead references; no Security-log audit-policy dependency remains for process telemetry.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/implementation_plan.md` (Done Checklist: wpc-05 checked — 4/4 tests, audit filed; wpc-06 amended — elevated manual smoke executed by the Architect 2026-08-17, PASS with audit-policy evidence waived; both units in commit 0f273e0); `wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17.md` (new — out-of-scope smoke observations as follow-up candidates: SensSensor null-value load failure, missing SignedS3UrlAdapter, parent-process resolution warnings, DuckDB unterminated-quote parser errors, cosmetic `[WindowsProcessSensor..ctor]` logger tag on QA lines); `wiki/log.md`.
Audit artifacts: `../wintap/developer_docs/audits/wpc-05-stop-metrics-merge.md` (Complete; 4/4 wpc-05 tests passed); `../wintap/developer_docs/audits/wpc-06-wire-in-removal.md` (Complete; 35/35 wpc tests and 36/36 full test-project regression passed via the documented MSB4249 project-scoped fallback; smoke evidence includes wire-in ordering, Start/Stop/Refresh parquet flow, and parseable interval/shutdown QA counter lines, e.g. snapshot_count=489).
Instructions written: `../wintap/developer_docs/instructions/wpc-07-boot-etl-coverage.md` (Status: Draft — Architect approval pending; slice 2 opt-in Global Logger boot ETL coverage).
Open questions: Architect review of the wpc-07 draft, including the optional logger-tag rider and the `boot_replay_count` QA-counter addition. wpc-08 (validation harness, slice 3) remains after wpc-07.

## [2026-08-17] closeout | improve-pidstat-collector + fix-upload-cache-deletion closed; durable facts promoted

Source: final review of branch grantj-rhel8-testing across all four repos (wintap ecfa746 upload fix; Lintap 8eaae5c Python collector; Wintappy ccbf783 parquet bronze; this repo's verification commits), plus operator field notes from RHEL 8 testing.
Upload-fix review: accepted for merge. Independently re-verified Lintap.csproj build (0 errors, zero CS0067). All specified behaviors landed: gated inline delete after the full uploader loop, dead event removed from IUpload/adapters, zero-byte cleanup, bottom-up empty-partition-dir removal with tolerated failures, merge-hang recovery scoped away from raw_sensor, prune off-by-one fixed with configurable RawSensorMaxCacheSizeBytes measured against raw_sensor only, guarded PostUpload, Warn-level failure logs. Post-merge follow-ups (dev-recorded): 3+ cycle live-uploader run; Windows-targeting build (env-blocked) and service-mode run.
Features closed: both briefs marked reviewed/closed with follow-ups tracked. Durable facts promoted to canonical pages: NEW component/sensor-upload-cache-pipeline.md (layout, merge cycle, type-agnostic ride-along contract, delete-after-upload fix, prune/hang-recovery semantics, deployment prerequisites); repo/lintap-supporting-repo.md (pidstat-collector.py section); repo/wintappy-pipeline-repo.md (parquet-only pidstat bronze section).
Operator field notes recorded: (1) pidstat-collector.py possible high CPU — investigate with multi-system data (pidstat plan follow-ups); (2) Lintap CPU possibly still trending up over long runs — watch; leading hypothesis duckdb event_store size, may need compaction (fix-unbounded plan field-watch item; raises priority of its open DuckDB-reclaim question); (3) pidstat parquet files are NOT merged before upload — 2026-08-16 mechanism fact corrected; generic per-cycle small-file consolidation for all raw_sensor type dirs queued as fix-upload-cache-deletion next slice; (4) attribution below.
Attribution note (per human request): this branch and its features were implemented using Claude (Fable) for design/review/wiki-maintenance and opencode (gpt-5.4) for development.
Contradictions flagged: one, resolved by correction — the 2026-08-16 "no merge step needed for pidstat" mechanism fact contradicted field observation; corrected in the pidstat design page with the consolidation task queued.

## [2026-08-18] closeout | [wintap] wpc-07 boot ETL coverage completed

Decisions made: none new. wpc-07 is closed as complete: the opt-in Global Logger boot ETL coverage path was implemented in `../wintap`, with `EnableBootProcessTrace` defaulting off, startup detect/verify/stop/disarm ordered before `WindowsProcessSensor` and shared kernel session materialization, replay after snapshot + live subscription registration, resolver-backed replay dedup, and `boot_replay_count` QA counter output.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/implementation_plan.md` (wpc-07 checked complete with validation note); `wiki/log.md`.
Audit artifact updated: `../wintap/developer_docs/audits/wpc-07-boot-etl-coverage.md` (post-implementation local validation section added).
Verification: Developer-side verification passed before deployment: `dotnet build "wintap\Wintap.csproj" -c Release -p:WarningLevel=0`; `dotnet build "tests\Wintap.Tests\Wintap.Tests.csproj"`; `dotnet test "tests\Wintap.Tests\Wintap.Tests.csproj" --filter "Category=wpc-07"` (10/10); `--filter "Category~wpc"` (45/45); unfiltered test project (46/46). Architect then published/deployed locally, rebooted, and let the build run overnight; reported results looked good.
Open questions: wpc-08 formal validation harness remains pending if detailed reproducible scoring artifacts are needed; no wpc-07 follow-up is open from this closeout.

## [2026-08-18] instruction | [wintap] wpc-09 minor bug sweep drafted

Decisions made: wpc-08 formal validation harness is skipped, without renumbering, because the Architect accepted manual slice-2 validation on 2026-08-18: process tree back to kernel-era roots, usernames present on all reviewed records, and a stable overnight run. wpc-09 is the final code unit before closeout.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17.md` (2026-08-18 overnight findings recorded); `wiki/work/improve-windows-process-collection/implementation_plan.md` (wpc-08 skip note and wpc-09 unit note); `wiki/work/improve-windows-process-collection/metrics.md` (sealed wpc-09 pre-implementation estimate); `wiki/log.md`.
Instructions written: `../wintap/developer_docs/instructions/wpc-09-bug-sweep.md` (Status: Draft — Architect approval pending).
Open questions: Developer must verify from logs whether the missing-parent warnings are fixable resolution gaps or expected unresolvable-parent races; Developer must verify whether process-name parsing errors share the DuckDB command-line escaping root before changing that path.

## [2026-08-18] approval | [wintap] wpc-09 minor bug sweep instruction approved

Decisions made: Architect approved the wpc-09 minor bug sweep instruction for Developer handoff. Scope remains limited to the final WPC code-unit sweep: boot-trace arm/disarm lifecycle fix, missing-parent warning triage/fix-or-annotation, process-name / DuckDB command-line escaping triage and fix if confirmed, and cosmetic QA-counter logger attribution only if still trivially broken.
ADRs written or updated: none.
Wiki pages updated: `wiki/log.md` only.
Instructions updated: `../wintap/developer_docs/instructions/wpc-09-bug-sweep.md` (Status: Approved — Architect approval 2026-08-18).
Open questions: none for instruction approval; Developer must still record triage dispositions and manual-smoke evidence in `developer_docs/audits/wpc-09-bug-sweep.md`.

## [2026-08-19] closeout | [wintap] improve-windows-process-collection feature closed

Decisions made: Architect approved feature closeout. Outcome: the unified `WindowsProcessSensor` (kernel-ETW Start/Stop on the shared session, ETW-canonical PidHash, snapshot Refresh with dedup, SID/command-line/path enrichment with fallbacks, manifest Stop-metric merge, opt-in Global Logger boot-trace replay, QA counters) fully replaced the Security-log and KernelProcessSensor paths — no audit-policy dependency, no log-wrap failure mode. Final code state: wintap develop-dave `19e89dc` (wpc-07 + wpc-09), 54/54 wpc tests and 55/55 project-wide passing, Release build 0 errors. Final overnight smoke-test 2026-08-18→19 PASS with boot replay confirmed end-to-end (arm at shutdown, owned stop/disarm at startup, replay), resolving the wpc-09 audit's pending item; earlier blocker was an external Code42-AAT lock on the DuckDB event store, and `19e89dc` also fixed the contributing Windows runtime data-root fallback. wpc-08 formal harness remained skipped (Architect decision 2026-08-18; manual validation accepted).
Pages created: `work/improve-windows-process-collection/verification.md` (accepted manual validation evidence, test/build state, wpc-08 skip rationale).
Pages updated: `work/improve-windows-process-collection/metrics.md` (mini-lab close-out: status closed; ts_design_end 2026-08-17, ts_final_audit 2026-08-18; actual_attention_hours 3.47 with proxy method record; human estimates unsealed; close-out answer recorded verbatim — feature only partially attempted solo, SID reverse engineering and PEB lookup not at all; ~120h est. vs 3.47h measured, retrofit seal-break and undercount caveats noted); `event_type/process-events.md` (durable semantics promoted from the feature work folder, regrounded to live `WindowsProcessSensor`/helper sources); `work/improve-windows-process-collection/implementation_plan.md` (done checklist closed: wpc-09 done, wpc-08 explicitly skipped, verification/promotion done); `work/improve-windows-process-collection/smoke-followups-2026-08-17.md` (final disposition: wpc-09 items resolved; SensSensor and SignedS3UrlAdapter remain future candidates outside the feature); `index.md`.
Contradictions flagged: none.
Open questions: none for this feature. Remaining ecosystem follow-up candidates live in `smoke-followups-2026-08-17.md` (SensSensor load failure, missing SignedS3UrlAdapter); deferred measurement of cmdline/SID fallback rates is available via QA counters whenever wanted.

## [2026-08-19] decision | AI velocity/ROI mini-lab revised to v2 (scheduled post-pilot revision)

What changed: headline metrics pivot to boundary/outcome measures — time-to-availability (raw calendar lead time, weekends included, feature open → first Architect-accepted validation artifact) plus throughput (counterfactual-hours delivered per window, weighted by sealed solo estimates); the two sealed interview questions are re-posed in calendar terms under the displacement ratchet; the 15-minute-gap attention proxy is demoted to an optional, coverage-annotated diagnostic (merge-then-cluster rule if ever multi-harness). See `wiki/decision/ai-velocity-roi-mini-lab.md` (Revision History).
Pages updated: `wiki/decision/ai-velocity-roi-mini-lab.md` (v2 in place); `wiki/concept/metrics-template.md` (v2 field set); `wiki/concept/feature-work-template.md` (calendar-posed sealed Q1/Q2); `wiki/concept/llm-assisted-feature-workflow.md` (interview step 7 phrasing); `wiki/work/improve-windows-process-collection/metrics.md` (v2 addendum: lead time 6 calendar days 2026-08-13→19 anchored on the boot-replay-confirming final overnight smoke-test per brief criterion 6; solo counterfactual ~2026-09-02/20 calendar days flagged as a units reconstruction; throughput weight 120h; attention 3.47h kept as coverage-annotated diagnostic); `wiki/index.md`.
Wintap process docs: proposed diffs to `../wintap/.claude/agents/engineer.md` and `../wintap/CLAUDE.md` drafted for Architect review per the ADR ownership note — not applied.
Contradictions flagged: none.
Open questions: none for the revision itself; cross-harness attention adapters remain deferred until a feature routes significant attention through OpenCode.

## [2026-08-19] closeout | [wintap] wpc-09 final scope and verification complete

Decisions made: Architect marked wpc-09 complete. The final sweep includes the boot-trace lifecycle, DuckDB parameterization, parent-warning annotation, QA logger attribution, and restoration of platform-owned runtime data-root defaults after the accidental Windows `C:\tmp\lintap-data` location contributed to external DuckDB contention.
ADRs written or updated: `wiki/decision/platform-runtime-data-root-defaults.md` (Accepted).
Wiki pages updated: `wiki/index.md`; `wiki/work/improve-windows-process-collection/implementation_plan.md`; `wiki/work/improve-windows-process-collection/verification.md`; `wiki/log.md`.
Verification: Release build completed with 0 errors; `Category=wpc-09` 19/19 passed; `Category~wpc` 64/64 passed; full test project 65/65 passed. Architect reported the post-reboot Wintap retry operating successfully and directed completion.
Open questions: none for wpc-09; existing implicit `/tmp` data is intentionally not migrated.

## [2026-08-19] decision | Velocity metric adopted (mini-lab v2.1 after external review)

Decisions made: Architect approved the final **Velocity** protocol (pitch approved 2026-08-19 after an external review cycle; authoritative source `../wintap/developer_docs/design/velocity-pitch-2026-08-19.md`). Headline: Velocity, dimensionless, unit solo-FTE equivalents, canonical formula `Velocity = solo-hours / (5.714 × days)`; 5.714 is a declared one-FTE capacity unit (no realism or conservatism claim, fixed once); two views one unit — Feature Velocity (speedup) and Portfolio Velocity (normalized delivered throughput; not an average — the gap is the parallelism dividend); "solo-hours" replaces "counterfactual-hours"; reporting is point values to one decimal with a stated uncertainty range (band from the two sealed estimates, default ±2×); sealed Q1 becomes a forced counterfactual (hours + realistic calendar date); guardrails adopted: frozen acceptance criteria, availability finality (defect-reopen rule rejected — ledger self-corrects forward), comparability flagging with the capability-vs-willingness distinction; cost stays a companion field.
Pages created: `wiki/concept/velocity-metric.md` (approved pitch carried faithfully into the wiki); `wiki/metrics.md` (cross-feature Velocity rollup, seeded with the WPC row: 6 days, 120 h, Velocity 3.5 uncertainty 2–7, willingness-only flag, retrofit-pilot annotation; Portfolio Velocity pending N≥several with trailing window ≥ 4× median lead time).
Pages updated: `wiki/decision/ai-velocity-roi-mini-lab.md` (v2.1 revision; new Alternatives Considered: per-developer baselines rejected, directional-bias constant framing withdrawn, bands-never-decimals rejected, defect reopen rule rejected); `wiki/concept/metrics-template.md` (v2.1 field set: leading Headline block, `feature_velocity`/`velocity_uncertainty`/`comparability`/`criteria_amendments`, `throughput_weight_hours` → `solo_hours`, `ai_est_solo_hours` added, methodology as links); `wiki/concept/feature-work-template.md` and `wiki/concept/llm-assisted-feature-workflow.md` (forced-counterfactual Q1 / calendar Q2 phrasing); `wiki/work/improve-windows-process-collection/metrics.md` (Velocity addendum: 3.5, uncertainty 2–7, pilot and willingness-not-capability caveats — added, nothing erased); `wiki/index.md`.
Wintap process docs: diffs to `../wintap/.claude/agents/engineer.md` and `../wintap/CLAUDE.md` redrafted against the final protocol and returned for Architect review — not applied, per the ADR ownership note.
Contradictions flagged: none hard. Two v2 statements corrected in place: the raw throughput companion is superseded by normalized Portfolio Velocity (the solo-hour sum survives as its numerator), and v2's "hours are never compared against elapsed time" safety note was removed because the canonical formula compares them deliberately via the declared 5.714 unit.

## [2026-08-20] maintenance | WPC metrics aligned to approved Velocity framing

Pages updated: `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/index.md`; `wiki/log.md`.
Changes: Replaced the accumulated v1/v2/v2.1 narrative and multiple YAML blocks with the canonical single-block Velocity format; made Feature Velocity 3.5 (uncertainty 2–7) the headline; retained the 120 solo-hour, 6-calendar-day, availability-anchor, comparability, per-unit, cost, and attention evidence; explicitly classified the pilot as retrospective/unsealed and illustrative; removed the obsolete attention-based rough-ROI framing and kept 3.47 hours only as a coverage-annotated diagnostic.
Decisions made: none — this is a conformance edit against the Architect-approved `wiki/concept/velocity-metric.md` definition.
Contradictions flagged: none.

## [2026-08-20] maintenance | WPC Velocity scorecard simplified

Pages updated: `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/index.md`; `wiki/log.md`.
Changes: Reworded the feature headline as a plain-language scorecard: estimated delivery speed 3.5× one solo developer's pace, plausible range about 2×–7× faster, low confidence, and a direct explanation for that low confidence. Moved formula-oriented language into a clearly labeled Technical Record while preserving the canonical YAML fields and underlying evidence.
Decisions made: none — presentation-only simplification; the approved metric and recorded values are unchanged.
Contradictions flagged: none.

## [2026-08-20] maintenance | Standardized overnight smoke-test wording

Pages updated: WPC metrics, verification, implementation plan, smoke follow-ups, canonical process-event page, index, and historical log references.
Changes: Replaced “overnight smoke” and “overnight smoke test” with the requested “overnight smoke-test” wording.
Decisions made: none; terminology-only correction.
Contradictions flagged: none.

## [2026-08-20] maintenance | WPC metrics summary labeled Results

Pages updated: `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/log.md`.
Changes: Renamed the plain-language scorecard heading from “Headline” to “Results” so the pilot document models the intended future presentation.
Decisions made: none; presentation-only change.
Contradictions flagged: none.

## [2026-08-20] maintenance | Future feature metrics inherit simplified Results

Pages updated: `wiki/concept/metrics-template.md`; `wiki/concept/velocity-metric.md`; `wiki/concept/feature-work-template.md`; `wiki/concept/llm-assisted-feature-workflow.md`; `wiki/index.md`; `wiki/log.md`.
Changes: Made **Results** the standard reader-facing section for future feature metrics; it now reports estimated delivery speed as a multiple of one solo developer's pace, an “about X×–Y× faster” plausible range, a deterministic Low/Medium/High confidence label, and one direct confidence reason. Canonical formulas and YAML remain under **Technical Record**. Removed inherited “Headline” and reader-facing “uncertainty 2–7” wording from the concept templates and examples.
Decisions made: Presentation convention only; the approved Velocity formula, fields, guardrails, and raw evidence are unchanged.
Contradictions flagged: none.

## [2026-08-20] update | Wintappy pidstat raw_sensor-path bugfix documented

Sources read: `../Wintappy/wintap_dbt/dbt_project.yml`; `../Wintappy/wintap_dbt/macros/paths.sql`; `../Wintappy/wintap_dbt/macros/raw_sources.sql`; `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql`; `../Wintappy/wintap_dbt/README.md`; `../Wintappy/Makefile`.
Pages created: none.
Pages updated: `repo/wintappy-pipeline-repo.md`; `work/improve-pidstat-collector/brief.md`; `work/improve-pidstat-collector/references.md`; `work/improve-pidstat-collector/design.md`; `work/improve-pidstat-collector/dev_handoff.md`; `work/improve-pidstat-collector/implementation_plan.md`; `work/improve-pidstat-collector/verification.md`; `index.md`; `log.md`.
Summary: documented the follow-up bugfix that removed `PIDSTAT_DATA_PATH` and the dedicated pidstat DBT macro/override in Wintappy. `stg_pidstat_metrics` now resolves `raw_sensor/pidstat` from `WINTAP_DBT_RAW_SENSOR_DATASET` through the shared raw-event helpers and uses the same day/hour partition-window narrowing as the other optional raw events.
Contradictions flagged: none.

## [2026-08-23] diagnostic | Lintap runtime high-CPU collector utility

Context: current field host has `/usr/lib/lintap/Lintap` running for six days at roughly 8.5 CPU cores, with all major sensors enabled and default process-retention settings. Non-root inspection could not read `/var/log/lintap/runtime/event_store/main.duckdb`, service environment, file descriptors, or full journals.
Files created: `extras/lintap-runtime-diagnostics/README.md`; `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`.
Purpose: root-run, read-only diagnostic bundle for pidhash/process-table runtime performance work. It collects service/process/thread samples, redacted config, journals, filesystem summaries, fork-rate data, optional perf/dotnet/pidstat samples, and read-only DuckDB summaries/`EXPLAIN ANALYZE` output for process-table and retention telemetry investigation.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-23] diagnostic | spk16 Lintap high-CPU field findings

Source: `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260823T205648Z` root-run diagnostics using a copied DuckDB event-store database.
Findings: `process` table retention is working at field scale (`64,742` rows after six days), but `process_retention_telemetry` has grown to `16,190,964` per-identity rows and is now the unbounded table. Runtime CPU remained high (`8.5` cores by `ps`, `13.9-15.2` CPUs by `perf stat`) across many native `Lintap` threads and sensor pollers. Fork rate was low (`~3/sec`), ruling out the earlier pidstat shell fork storm. Schema output showed no `process` indexes and pidhash lookup plans used sequential scans over ~64k rows. Process rows/telemetry were dominated by short-lived monitor commands and `python3.12` rows parented to the pidstat collector, suggesting clone/thread events are being registered as process rows.
Recommended fixes: aggregate and retain/prune `process_retention_telemetry`; filter `CloneSensor` thread clones (`CLONE_THREAD`) so thread IDs do not pollute the pidhash process table; evaluate `process_id, create_time` indexing after reducing telemetry/thread-clone churn.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-23] fix | pidstat collector conversion noise mitigation

Source: spk16 field diagnostic showed many short-lived `python3.12` process rows parented to the pidstat collector while it was manually running with `PIDSTAT_ROTATE_INTERVAL_SEC=10`.
Files changed: `../Lintap/pidstat-collector.py`; `../Lintap/tests/test_pidstat_collector.py`; `../Lintap/README.md`; `../Lintap/packaging/lintap-rpm/lintap.env`; `../Lintap/packaging/lintap-deb/lintap.env`; `../Lintap/packaging/lintap-rpm/README.md`; `../Lintap/packaging/lintap-deb/README.md`.
Fix: clamp rotation to `PIDSTAT_MIN_ROTATE_INTERVAL_SEC` default `300`, add `PIDSTAT_DUCKDB_THREADS=1`, reuse one DuckDB connection for parquet conversion, and log the effective quieting settings at startup. This reduces collector-induced process/clone noise before addressing broader CloneSensor thread filtering.
Validation: `uv run --group dev pytest tests/test_pidstat_collector.py` in `../Lintap` passed (`14 passed`).
Pages updated: `work/improve-pidstat-collector/verification.md`; `log.md`.

## [2026-08-23] diagnostic | pidstat mitigation post-restart check

Source: `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260823T223445Z` after restarting the manual pidstat collector with `PIDSTAT_MIN_ROTATE_INTERVAL_SEC=300` and `PIDSTAT_DUCKDB_THREADS=1`.
Results: collector-induced noise dropped materially: fork-rate sample was effectively zero (`processes_delta_10s=4`), `python3.12` disappeared from the current top process-row producers, and open `python3.12` rows fell from `1117` to `31`. Lintap CPU improved by `perf stat` sample (`13.9-15.2` CPUs before to `9.4` CPUs after) but remained high by `ps` (`~8.5` cores). `process` remained bounded (`47,135` rows), while `process_retention_telemetry` still grew to `16,362,388` rows, adding ~171k rows over ~98 minutes.
Conclusion: pidstat conversion churn is mitigated, but the remaining high-CPU/runtime-quality work should move to `../wintap`: aggregate/prune `process_retention_telemetry`, filter `CloneSensor` thread clones, then reassess process lookup indexing.
Pages updated: `work/improve-pidstat-collector/verification.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-23] fix | process retention telemetry bounded

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `../wintap/shared/ai/wintap_mcp_server/wintap_mcp_server.csproj`.
Fix: `process_retention_telemetry` now writes aggregate rows by default instead of one row per process identity; per-`pid_hash` detail is opt-in via `WINTAP_PROCESS_RETENTION_TELEMETRY_DETAIL_ENABLED=true`. Added `WINTAP_PROCESS_RETENTION_TELEMETRY_RETENTION_SEC` with a 24-hour default and prunes old telemetry rows every maintenance sweep. Startup logging includes the telemetry retention/detail settings.
Build fix: MCP publish had failed because generated files under `shared/ai/wintap_mcp_server/mcp_temp/obj` were included by the MCP project source glob, causing duplicate assembly attributes. The MCP project now excludes `mcp_temp/**` alongside direct `obj/**` and `bin/**`.
Validation: direct MCP publish passed; `dotnet build wintap/Lintap.csproj` in `../wintap` passed with existing warnings and `0` errors.
Pages updated: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/implementation_plan.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] feature | [wintap] windows-sensor-health-check opened: exploration, design, plan, shc-01 draft

Decisions made (Architect, via interview — recorded in `work/windows-sensor-health-check/interview.md`): health checks run in-agent at the WintapMessage egress choke point before serialization; aggregated per-sensor-stream/per-check counters flushed periodically as dedicated health messages into the normal Parquet stream with a capped first-N sample; coverage is all Windows sensors including WindowsProcessSensor; full-stream constant-time checks, no sampling.
Mini-lab: `work/windows-sensor-health-check/metrics.md` created with the Engineer's independent sealed estimates recorded BEFORE reading the interview's sealed section (seal intact): ai_est_solo_hours 48, solo date 2026-09-18, AI-workflow date 2026-08-31. Acceptance criteria frozen at open in `brief.md` per ADR guardrail 1. Per-unit estimate recorded for shc-01 (2.5 h).
Exploration findings (grounded in `../wintap` source): the real choke point is `EventChannel.Send`, but it has two egress branches (DirectParquetSink early-return — pre-enrichment — and the post-enrichment Esper→Serializer→ParquetWriter path), so the hook lands at both emit sites. Surprises: (1) `MemoryMapSensor.cs:308` bypasses Send entirely via direct `SendEventBean` (no AgentId, no self-PID filter); (2) `Watchdog`/`PluginExceptionHandler` WintapAlert messages carry Wintap's own PID and are silently dropped by Send's self-PID filter — self-generated alerts likely never reach output today; (3) `Serializer.Save` NULL_PIDHASH and `DefaultSerializer` payload-reflection failures are silent drop paths the checks will make visible.
Pages created: `work/windows-sensor-health-check/metrics.md`; `brief.md` (nine frozen acceptance criteria); `design.md` (egress hook, check registry, SensorHealth message schema, 60 s flush, sample cap 3, constant-time overhead argument, risks, alternatives); `implementation_plan.md` (abbreviation `shc` declared, no collision; units shc-01 core engine → shc-02 message+flush → shc-03 wire-in+verification).
Instructions written: `../wintap/developer_docs/instructions/shc-01-health-check-core.md` (Status: Draft — Architect approval pending; pure new engine code, no production wiring, independent of all open design questions).
Open questions (Architect, before shc-02/shc-03 drafting): approve the WintapMessage schema addition (SensorHealth enum + payload); MemoryMapSensor coverage approach; EmitSensorHealth vs. Send exemption branch; optional `process_unresolved` check; confirm defaults (60 s / cap 3 / enabled-on-Windows). Side observation: the ptr feature (merged in ../wintap 2026-08-22/23) has no entries in this log — fold-in appears owed.

## [2026-08-24] redirection | [wintap] windows-sensor-health-check simplified to log-only reporting

Decisions made (Architect, same-day redirection — recorded in interview.md Round 2): health results are periodic aggregated Wintap.log entries via WintapLogger, nothing else. Superseded from the first-draft design: the dedicated SensorHealth WintapMessage/Parquet output, any WintapMessage schema change, the EmitSensorHealth path, and the self-PID-filter exemption (the latter two problems disappear with the schema change). Rationale: "This is a supportive feature, not the mission of wintap... start simple and extend if needed." Unchanged: egress choke point in `EventChannel.Send` (both branches), the four v1 checks, full-stream constant-time cost, aggregated counters + capped first-N samples, all-Windows-sensor coverage, low-noise periodic summaries (never per-failure). Adopted defaults without further round-trips (per Architect direction): MemoryMapSensor gets a one-line Inspect at its direct-send site in the wire-in unit; the `process_unresolved` ("Unknown" sentinel) check is deferred to the follow-on sweep feature.
Mini-lab: criteria amendment logged in `work/windows-sensor-health-check/metrics.md` `criteria_amendments` (2026-08-24, reporting channel Parquet→Wintap.log); criteria re-frozen same day in brief.md. Seal on the interview's human estimates remains intact — the Engineer did not read the sealed section. shc-01 per-unit estimate revised pre-implementation from 2.5 h to 3.0 h (flush/log formatting folded into the unit).
Pages updated: `work/windows-sensor-health-check/brief.md` (re-frozen criteria, now eight; amendment banner); `design.md` (log-line reporting design, WintapAlert self-PID drop finding retained as sweep-feature note, alternatives updated with the rejected first-draft message design); `implementation_plan.md` (reduced from three units to two: shc-01 engine+checks+log flush, shc-02 egress wire-in + end-to-end verification); `metrics.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/shc-01-health-check-core.md` rewritten for the merged scope (engine + checks + periodic log flush via injectable sink; hot-path contract and fail-open wrapper retained; all message/flush-to-Parquet plumbing removed; filename slug unchanged — still accurate). Status: Draft — Architect approval pending.
Open questions: none — the redirection and adopted defaults resolved all previously flagged decisions.

## [2026-08-24] amendment | [wintap] windows-sensor-health-check v1 check list made definitive (amendment #2)

Decisions made (Architect review of the shc-01 draft, same day): the v1 conditions are now definitive. (1) "Unknown" process attribution FAILS — reverses the draft's pass note ("this is exactly the failure mode i want to catch"); implemented as a new `process_unresolved` check: ProcessName == "Unknown" (case-insensitive) OR PidHash == the unknown-sentinel hash. (2) `processname_missing` and `payload_mismatch` stand. (3) New `path_unqualified` check: File and Registry payload paths must be fully qualified in their grounded emitted forms; other streams exempt. (4) New stream-liveness condition: File, Registry, MemoryMap, ImageLoad, TcpConnection, UdpPacket must each show nonzero inspected counts per 5-second interval; a zero interval is a critical condition — transition-only logging (one Error STALL line, one Info RECOVERED line with duration), 60 s startup grace, suppression across Stop(). (5) `eventtime_invalid` DROPPED from v1; preserved in design.md as the first candidate future check.
Grounding added to design.md: the unknown sentinel — EventChannel sets literal ProcessName="Unknown" on owner-resolution failure with a *fabricated but indistinguishable* fallback PidHash; the only distinguishable sentinel hash is `ProcessHash.GenPidHash(-1, 0)` (EventChannel's UnknownPidHash, parent-lineage use only today), and it is HOST-SPECIFIC (formula mixes MachineName + AgentId) so it must be computed at runtime / injected in tests. Path forms — File.Path is lowercased with forms `x:\...`, `\\...` (UNC), `\device\...`; Registry paths are lowercased KCB paths rooted `registry\...` (leading backslash trimmed). Surprise: RegistrySensor's CreateKey/DeleteKey/DeleteValue emit sites are ungated (no StartsWith("registry") filter), so relative key fragments can egress today — `path_unqualified` will count exactly that; fixing the sensor is sweep scope. Parent-lineage "Unknown" sentinels deliberately excluded from v1 (designed ptr best-effort behavior) — candidate future check.
Mini-lab: amendment #2 logged in `work/windows-sensor-health-check/metrics.md` `criteria_amendments`; criteria re-frozen in brief.md (nine criteria); seal on the human estimates remains intact. shc-01 per-unit estimate revised pre-implementation 3.0 h → 4.0 h (two new checks + liveness state machine).
Pages updated: `work/windows-sensor-health-check/brief.md`; `design.md`; `implementation_plan.md`; `metrics.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/shc-01-health-check-core.md` rewritten with the definitive five-check registry, injected sentinel seam, grounded path-form matrices, and the liveness state machine + tick seam. Status: Draft — Architect approval pending.
Open questions: none.

## [2026-08-24] audit+instruction | [wintap] shc-01 complete; shc-02 egress wire-in drafted

Decisions made: none new. Developer completed the approved shc-01 unit: standalone health-check engine, five definitive checks, liveness watchdog, and periodic log flush landed as pure new code under `../wintap/wintap/core/infrastructure/health/` with no production files modified. Verification: 33/33 via `dotnet test --filter "Category=shc-01"`, independently re-verified by the main session 2026-08-24; documented deviation — solution-level `dotnet build -c Release` fails with the known Wintap-Workbench MSB4249 issue, approved project-scoped fallback used. Audit: `../wintap/developer_docs/audits/shc-01-health-check-core.md` (Complete). Provenance note recorded in the feature's new verification.md: `/developer_docs/` is gitignored in the wintap repo, so instruction/audit artifacts are local-only process files — the wiki preserves the durable evidence.
Mini-lab: shc-01 `actual_hours` recorded as missing data per never-gates (audit/log carry only the date; no intra-day timestamps and no commit trail for gitignored artifacts). shc-02 per-unit estimate recorded pre-implementation: 3.0 h (three one-line call sites + EventChannel seam + lifecycle + heavy-statics test fixture + manual live run). Seal on the interview's human estimates remains intact.
Instruction drafted: `../wintap/developer_docs/instructions/shc-02-egress-wire-in.md` (Status: Draft — Architect approval pending). Grounded call-site placements: (1) inside the `DirectParquetSink.IsEnabled` block before `Save` (branch returns — exactly one Inspect per message, no double-inspect); (2) normal branch post-enrichment/post-registration, immediately **above** the `skipEsperSend` early return (production-identical; enables integration tests without live Esper — design.md skip-seam edge note revised accordingly); (3) one line in `MemoryMapSensor.refreshSnapshot` before its direct `SendEventBean` (~line 308) via a shared `EventChannel.InspectForHealth` helper with an internal test-seam override. Lifecycle grounded in `WintapSvcCore.cs`: `SensorHealthMonitor.Default.Start()` immediately after `subscriptionMgr.Start()` (not started under `WINTAP_DISABLE_SENSORS`); `Stop()` as the first action of `StopAsync` (suppresses shutdown stall alarms; final flush before logger close).
Surprise found and recorded in design.md: a third direct `SendEventBean` exists at `../wintap/wintap/core/etl/extract/Serializer.cs:150` (`Serializer.Listen`) — dead code with no callers and a "do we still need this?" TODO; it gets no Inspect call and is flagged as a sweep-feature deletion candidate.
Pages updated: `work/windows-sensor-health-check/implementation_plan.md` (shc-01 checked); `work/windows-sensor-health-check/design.md` (Serializer.Listen correction; refined call-site placement + single-inspection guarantee; skip-seam edge note revision; lifecycle grounding); `work/windows-sensor-health-check/metrics.md`; `wiki/log.md`.
Pages created: `work/windows-sensor-health-check/verification.md` (shc-01 evidence; shc-02/manual-run placeholder as availability-anchor candidate).
Open questions: Architect approval of the shc-02 draft, including two flagged points — the small internal `HealthMonitorOverride`/`InspectForHealth` seam added to EventChannel.cs (kept within the allowed-file list) and the integration-test posture around the heavy StateManager/EventChannel type initializers (temp data root + env seams, with a documented fallback for the direct-parquet branch test).

## [2026-08-24] instruction | [wintap] shc-02 paused on diskpart elevation conflict; enabling unit shc-03 (QueryDosDevice drive map) drafted

Decisions made (Architect): the Developer started the approved shc-02 and stopped correctly on an instruction/codebase conflict — the no-admin integration tests fail because the first `EventChannel.Send` initializes `StateManager`, whose ctor calls `WindowsStateManager.RefreshDriveMap()` (`../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs:35`), which spawns `diskpart.exe` and requires elevation (`Win32Exception`), with no try/catch around the spawn. No audit filed; shc-02 is paused. Architect inserted enabling unit **shc-03 — replace the diskpart drive mapping with QueryDosDevice** — which lands BEFORE shc-02 resumes despite the number (execution order shc-01 → shc-03 → shc-02, recorded in the implementation plan). Explicitly NOT a criteria amendment: the frozen brief criteria are unchanged.
Grounding (verified in ../wintap): `RefreshDriveMap` has one production caller (`StateManager` ctor, `#if WINDOWS`, once per process — the 60 s state timer never refreshes the drive map) and `DriveMap` has one reader (`BaseWindowsSensor.fromNative`, which rewrites `\device\harddiskvolumeN\...` → `letter:\...` by `VolumeNumber` lookup). Nothing serializes `DiskVolume`; its Label/FileSystem/Type fields are dead. Correctness finding: diskpart's `Volume ###` is an enumeration index, not the NT HarddiskVolumeN number `fromNative` looks up, so today's map silently mismatches and most native-path rewrites land in the hardcode-`c:` fallbacks — QueryDosDevice is the authoritative source and shc-03 is the feature's first genuine accuracy fix. Precedent found: `WindowsProcessSensor` already P/Invokes `QueryDosDevice` (`TryTranslateDevicePathToWin32Path`); shc-03 mirrors that signature. Residual flagged for Architect: `fromNative`'s `volumeNumber <= diskVolumes.Count` guard bypasses the corrected map whenever NT numbers exceed the lettered-drive count (typical: EFI/recovery volumes consume low numbers), hardcoding `c:` on multi-drive hosts — not a regression, but the accuracy fix is unrealized until the guard is removed (follow-up unit or sweep feature). `TranslateTransientPath`'s WMI partition-number parse has a similar authority problem (sweep candidate). A duplicate `DiskVolume` in `platform/windows/WintapCoreSvcMgr` is unaffected.
Mini-lab: shc-03 per-unit estimate recorded pre-implementation in `work/windows-sensor-health-check/metrics.md`: 1.5 h (single-file P/Invoke swap with exact in-repo precedent + pure seam + ~7 no-admin tests); shc-02 pause noted on its unit row, estimate unchanged. Seal on the interview's human estimates remains intact — interview.md was not read this session.
Instructions written: `../wintap/developer_docs/instructions/shc-03-querydosdevice-drive-map.md` (Status: Draft — Architect approval pending; exact P/Invoke signature, normative parse rules and edge-case table, never-throws fail-soft contract, `BuildDriveMap` test seam + lenient live smoke test, scope locked to WindowsStateManager.cs + tests, non-elevated test-run requirement).
Pages updated: `work/windows-sensor-health-check/implementation_plan.md` (three units; execution-order section; shc-02 paused; files/tests/checklist rows); `work/windows-sensor-health-check/design.md` (revision banner #3; new "shc-03 Insert" section: snag record, consumer map, grounded rationale, precedent, residual fromNative-guard flag); `work/windows-sensor-health-check/metrics.md`; `wiki/log.md`.
Open questions: Architect approval of the shc-03 draft; Architect decision on where the `fromNative` guard fix lives (widen shc-03? follow-up shc unit? sweep feature?).

## [2026-08-24] instruction | [wintap] shc-03 widened to include the fromNative guard fix (Architect decision)

Decisions made (Architect, same day): the open question from the previous entry is resolved — **widen shc-03** to include the `BaseWindowsSensor.fromNative` guard fix so the drive-map accuracy fix is realized immediately rather than deferred to the sweep feature. The feature's no-sensor-changes posture gets a **scoped exception** for exactly `BaseWindowsSensor.cs` and exactly this fix. Fix as specified in the instruction: remove the `volumeNumber <= diskVolumes.Count` guard (direct `VolumeNumber` lookup always runs; translate on match); on a genuine miss, preserve today's fallback verbatim (the existing logged `Got null DiskVolume...` line + hardcode `c:` — no new handling invented); remove the single-drive `harddiskvolume1` hack as provably dead logic (it only ran where the lookup already guaranteed `dv.VolumeNumber == volumeNumber`, and it mutated the shared cached DriveMap entry); outer catch and pre-`try` parse untouched. Testability seam kept minimal: `fromNative` accessibility `private` → `internal` only (no delegate injection, no overload); tests construct `BaseWindowsSensor` directly via the existing `InternalsVisibleTo`, the established wpc sensor-test pattern. Five translation-path tests added to the unit (NT number > drive count — the old-guard breakage case; multi-drive correct-letter selection; genuine-miss legacy fallback; rewritten-path format preservation; quoted-path cleanup). Still not a criteria amendment; the frozen brief criteria are unchanged.
Process note: while the widening was being folded in, an "Approved 2026-08-24" stamp appeared on the shc-03 instruction file on disk. Per the Architect's explicit direction that the widened version be read before approval, the header was reverted to Status: Draft / Approval: Pending with an explanatory comment — a pre-widening stamp cannot cover the widened content; flagged to the Architect for the (re-)approval gate.
Mini-lab: shc-03 per-unit estimate revised pre-implementation in `work/windows-sensor-health-check/metrics.md`: 1.5 h → 2.0 h (guard fix + ~5 translation-path tests + accessibility seam). Seal on the interview's human estimates remains intact — interview.md was not read this session.
Instructions updated: `../wintap/developer_docs/instructions/shc-03-querydosdevice-drive-map.md` (widened: two production files; grounded current `fromNative` code and exact replacement method; hard-constraints block carries the scoped sensor-file exception; acceptance criteria and Out of Scope updated; tests 8–12 added). Status: Draft — Architect approval pending on the widened version.
Pages updated: `work/windows-sensor-health-check/implementation_plan.md` (shc-03 description/tests/files widened); `work/windows-sensor-health-check/design.md` (revision banner; residual-guard paragraph rewritten as the recorded widen-not-defer decision with the Architect's realize-now rationale); `work/windows-sensor-health-check/metrics.md`; `wiki/log.md`.
Open questions: Architect approval of the widened shc-03 draft (including confirming the reverted approval stamp).

## [2026-08-24] validation | spk16 post-RPM telemetry bounding check

Source: `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260824T013652Z` after building/installing the new RPM with the telemetry aggregation fix and running for about 2.5 hours.
Results: Lintap PID `1918289` sampled at `1.211` CPUs by `perf stat` (vs. `9.4` after pidstat mitigation and `13.9-15.2` before). Fork rate was quiet (`5` process creations over 10 seconds). `process` table remained bounded at `47,648` rows. `process_retention_telemetry` was reduced to `4,721` aggregate rows, with aggregate totals preserved in `metric_value`. Copied DuckDB size was `19.0 MiB`, down from ~`761 MiB` before the telemetry fix. Process lookup plans still used sequential scans over ~47k rows but query times were small in the copied DB.
Conclusion: process-retention telemetry aggregation/retention fixed the runaway telemetry table and materially reduced Lintap runtime CPU on the field host. Remaining follow-ups: CloneSensor thread-clone filtering and optional lookup indexing.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] diagnostic | process lookup index low leverage in field snapshot

Source: `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260824T033731Z`.
Findings: Lintap remained stable at `1.471` CPUs by `perf stat`; `process` had `48,628` rows and `process_retention_telemetry` had `9,459` aggregate rows. The copied DB included `idx_process_process_id_create_time` on `(process_id, create_time)`, but representative pidhash lookup plans still used sequential scans over ~48k rows, with copied-DB query times around `0.012-0.025s`. Hot threads were sensor pollers (`CloneProcess`, `FileOps`, `ExitProcess`, `ExecveProcess`) rather than telemetry/DB churn.
Conclusion: additional DuckDB indexing is not the next highest-leverage fix. Prefer CloneSensor thread-clone filtering or an in-memory current-process map if further CPU reduction is needed.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] fix | CloneSensor filters thread clones

Files changed: `../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs`.
Fix: CloneSensor now skips clone events with `CLONE_THREAD` (`0x00010000`) before reading `/proc` or emitting process `Start` rows. Unknown clone flags (`0`) and the vfork sentinel remain accepted to preserve fork/vfork/process-like clone coverage.
Rationale: field diagnostics showed thread IDs being registered as processes, polluting the pidhash/process table and increasing stale-open reconciliation work.
Validation: `dotnet build wintap/Lintap.csproj` in `../wintap` passed with existing warnings and `0` errors.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] maintenance | Lintap runtime diagnostics utility cleanup

Files updated: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`; `extras/lintap-runtime-diagnostics/README.md`.
Changes: removed hardcoded DuckDB PATH and hardcoded `/root/main.duckdb`; added `--db` override; added upfront required/optional command reporting in `requirements.txt`; added DuckDB CLI discovery across PATH and common install locations; added automatic live-DB lock probing and snapshot fallback that copies `main.duckdb` plus `main.duckdb.wal` when present into `duckdb/snapshot/` before running read-only queries; updated manifest and summary notes to record source/query DB paths.
Validation: `bash -n extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` passed; `--help` output verified.

## [2026-08-24] review | Initial FileOps poller optimization note captured

Source: simple source inspection of `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`, `file_ops_tracer.bpf.c`, `file_ops_tracepoint.bpf.c`, and field diagnostics where `FileOps-Poller` remained the dominant hot thread after pidstat/telemetry fixes.
Result: recorded a future-todo note, explicitly marked as an initial review rather than a decided design. Main hypothesis: reduce ring-buffer volume by emitting fd-based file operations only for tracked fds in eBPF, then consider earlier pseudo-path/data-root/parquet filtering and optional op-class toggles.
Pages updated: `work/fix-unbounded-process-table-growth/implementation_plan.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] feature | optimize-fileops-poller created and handed off

Source: full design/engineering analysis of `../wintap` FileOps path (`FileOpsSensor.cs`, both `file_ops_*.bpf.c` tracers, `BaseEbpfSensor.cs` poll loop, `EventChannel.Send`, `ProcessHash`, tracers `Makefile`), extending the 2026-08-24 initial review.
Key findings: non-regular-file fds (sockets/pipes) always miss the fd cache, pay an uncached `/proc` readlink per syscall, and are emitted as `socket:[N]` File rows; Wintap's own I/O is fully processed then discarded; per-event `GenPidHash` is dead (overwritten in `EventChannel.Send`) or wrong (DirectParquetSink); `_fdToPath` never evicts on process exit (leak + PID-reuse misattribution); kernel timestamps are discarded; `file_ops_tracer.bpf.o` is not actually CO-RE despite its name.
Plan: seven `fop-nn` slices, measurement-first (counters/baseline), then userspace dead-work removal, kernel self-PID filter, wakeup batching, CO-RE `S_ISREG`/superblock-magic filtering (gated on a human socket/pipe-row decision), compact fd-op records, fd-cache eviction + kernel timestamps. No-loss constraint enforced by a standing A/B differential test; aggregation explicitly deferred per human direction. Work proceeds on `grantj-rhel8-testing` in both repos.
Pages created: `work/optimize-fileops-poller/{brief,references,design,implementation_plan,dev_handoff,verification}.md`.
Pages updated: `work/fix-unbounded-process-table-growth/implementation_plan.md` (future-todo item spun off); `index.md`; `log.md`.

## [2026-08-24] code | optimize-fileops-poller fop-01/fop-02 code slice

Files changed in `../wintap`: `FileOpsSensor.cs`, `LibBpf.cs`, `file_ops_tracer.bpf.c`, `file_ops_tracepoint.bpf.c`.
Files created in this repo: `validation/fileops-differential/README.md`, `compare_fileops.py`, `fileops_workload.py`.
Implemented: kernel emitted/ring-fail counters by FileOps op class in both tracer variants; userspace consumed/emitted/drop/fallback counters and periodic logs; removed dead per-event FileOps `GenPidHash`; memoized successful `/proc/<pid>/fd` fallback paths; skipped `/proc` fallback for close events; direct scalar decode before string materialization; deterministic file workload and parquet A/B comparator that fails on missing regular-file tuples.
Validation: tracer `make clean && make` passed; `dotnet build wintap/Lintap.csproj` passed with existing warnings and 0 errors; Python harness syntax passed; comparator positive and negative synthetic parquet smoke tests passed.
Limitations: deployed fop-01 counter baseline and live A/B differential remain pending.
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-24] fix | FileOps verifier failure on unlink path

Source: `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260824T212523Z` showed the deployed fop build failed verifier on `t_unlinkat` with `R8 invalid mem access 'inv'`, so FileOps did not load and the low CPU sample was not a valid optimization result.
Files changed: `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`; `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c`; `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile`; `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Fix: split pathname emission into saved-buffer and raw-user-pointer helpers; unlink/unlinkat now use `bpf_probe_read_user_str()` via `emit_file_event_user()`. Completed the compact tagged record format for fd vs path events and moved `file_ops_tracer.bpf.o` into the CO-RE Makefile tier.
Validation: `make clean && make` in the tracer directory passed, including CO-RE `file_ops_tracer.bpf.o`; `dotnet build wintap/Lintap.csproj` passed with existing warnings and `0` errors.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] closeout | [wintap] windows-sensor-health-check feature closed (Feature Velocity 7.0)

Feature complete and Architect-accepted against the re-frozen brief criteria. Units: shc-01 (core engine + five checks + liveness + log flush, 33/33, commit `524ecdb`, audited 2026-08-24), shc-03 (QueryDosDevice drive map + fromNative guard fix, 27/27, commit `26ce94c`, audited 2026-08-25), shc-02 (egress wire-in + MemoryMap bypass Inspect + lifecycle, 5 integration tests, commit `b0528f8`, completed 2026-08-25 — **audit never filed**: Developer worked in an external harness; recorded as missing data per never-gates, durable evidence in verification.md). Whole `Category~shc` suite 65/65 independently re-run by the main session 2026-08-25; full suite 165/165; root solution retains the known MSB4249 issue. Deviation (Architect-permitted): shc-02 tests initially hung on the WintapLogger first-touch sync-context issue; same `Env.SetDataRoot` fixture fix as shc-03 applied.
Availability anchor (Architect-accepted): manual live run on the lab host 2026-08-25 05:39–05:41 local, branch build — recorded verbatim in verification.md; first live demonstration of the frozen criteria (QueryDosDevice map active, egress checks flushing aggregated FAIL lines, no false liveness stalls, low-noise). Lead time: opened 2026-08-24 → available 2026-08-25 = 1 calendar day.
Mini-lab close-out (per [[wiki/decision/ai-velocity-roi-mini-lab]] v2.1): human estimates unsealed — solo 40 h (no solo date given — missing data), AI-workflow date "1 - 2 days" (2026-08-25..26). **Feature Velocity = 40 / (5.714 × 1) = 7.0, uncertainty 3.5–17** (two sealed estimates imply 7.0–8.4, widened ±2×). Q3 verbatim: "Yes" — plain counterfactual, capability not exceeded, comparability `none`, included in the fitted trend (first fully valid dual-sealed point). Calibration: human's AI date hit exactly at its optimistic edge; Engineer's AI date (2026-08-31) 6 days pessimistic; solo spread tight (40 vs 48). Per-unit actual hours missing across all three units; attention proxy omitted (multi-harness, not cheap); API cost missing. Rollup row appended to [[wiki/metrics]].
Findings cataloged: the previously cancelled cataloging dispatch had produced nothing — the consolidated **sweep-feature queue** was created at [[wiki/diagnostic/windows-sensor-sweep-queue]] (12 items): WintapLogger BackgroundWorker sync-context capture (WintapLogger.cs:174-176; Developer's proposed dedicated-thread fix recorded), WintapLogger live-log truncation via FileMode.Create (WintapLogger.cs:166), standing Env.SetDataRoot-before-WintapLogger test-fixture guidance (shc-02/shc-03 fixture pattern cited), the health check's first live catch (PID=-1 ActivityType=Refresh Process event egressing as ProcessName=Unknown — likely WindowsProcessSensor snapshot-refresh artifact), cosmetic `[SensorHealthMonitor..ctor]` caller tag, plus the design.md carry-overs (ungated Registry CreateKey/DeleteKey/DeleteValue emit sites, dead `Serializer.Listen`, WintapAlert self-PID drop, `TranslateTransientPath` WMI authority problem, QueryDosDevice consolidation with WindowsProcessSensor, MemoryMap reroute-through-Send question, `eventtime_invalid` future check).
Pages created: `component/sensor-health-monitor.md` (canonical fold-in of stabilized behavior); `diagnostic/windows-sensor-sweep-queue.md`.
Pages updated: `work/windows-sensor-health-check/verification.md` (shc-03/shc-02 evidence + anchor); `metrics.md` (Results, unsealed estimates, tabulation, closed); `implementation_plan.md` (done checklist closed); `design.md` (close-out banner + sweep-queue cross-link); `component/windows-sensor-service-internals.md` (egress health inspection note); `wiki/metrics.md` (rollup row); `wiki/index.md` (shc feature pages indexed — they had been missed at open — plus the two new pages); `wiki/log.md`.
Open questions: none for this feature. Next: the follow-on Windows sensor sweep feature opens from [[wiki/diagnostic/windows-sensor-sweep-queue]]. Standing owed item from 2026-08-24 remains: ptr feature fold-in has no entries in this log.

## [2026-08-25] feature | WRC opened and planned

Opened `improve-windows-registry-collection`, repaired/completed the registry-provider ADR, recorded retroactive POC spikes wrc-01/wrc-02, and created the WRC plan/references. Initial open inputs: session-handle strategy, final keyword mask, minimal schema shape, and capture-loss canary mechanics. Details: [[wiki/decision/registry-provider-strategy]] and [[wiki/work/improve-windows-registry-collection/implementation_plan]].

## [2026-08-25] decision+instruction | WRC design inputs resolved; build units drafted/approved

Resolved the WRC design gates and instruction sequence: Option A guarded reflection for the TraceEvent session handle, append-only registry schema, final 0x5300/0x5700 keyword mask after probe8, and canary settings. Drafted/approved wrc-03, wrc-04, wrc-05, wrc-06, and wrc-07; wrc-06 became the manifest-only RegistrySensor rewrite with read events intentionally carrying no typed value data and `Registry.PID` left legacy-unset. Details live in the WRC implementation plan and instruction files.

## [2026-08-25] decision+instruction | WRC wrc-08 parquet value plumbing added

Rolled in wrc-08 as a scoped Non-Goals exception before closeout so the new registry value fields reached Parquet output. The unit was drafted and approved with the accepted group-by granularity consequence and `""`/`"NONE"` null defaults. Details: [[wiki/work/improve-windows-registry-collection/implementation_plan]].

## [2026-08-25] verification | WRC live verification recorded before closeout

Recorded the Architect-run wrc-07 live verification in [[wiki/work/improve-windows-registry-collection/verification]] and queued sweep findings for short-lived-process attribution and `stop_without_start` monitoring. Closeout still waited on wrc-08 implementation/audit and final Architect acceptance.

## [2026-08-25] closeout | [wintap] improve-windows-registry-collection feature closed (Feature Velocity 42.0)

Closed the WRC feature and promoted durable state into [[wiki/component/registry-sensor]], [[wiki/work/improve-windows-registry-collection/verification]], [[wiki/work/improve-windows-registry-collection/metrics]], and [[wiki/diagnostic/windows-sensor-sweep-queue]]. Final code reference: `../wintap` commit `1f66a47`; feature suite `Category~wrc` 134/134 and full suite 299/299 were recorded in verification. Metrics: Feature Velocity 42.0, uncertainty 7–84. Open questions: none for WRC; follow-ons remain in the sweep queue.

## [2026-08-25] code | optimize-fileops-poller expanded deployment and diagnostics

Source: continued work on `../wintap` FileOps path plus live RHEL8 validation using `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T033307Z` (smoke) and `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T142601Z` (overnight).
Files changed in `../wintap`: `FileOpsSensor.cs`, `LibBpf.cs`, `file_ops_tracer.bpf.c`, `file_ops_tracepoint.bpf.c`, `tracers/Makefile`. Files changed in this repo: `extras/lintap-runtime-diagnostics/{collect-lintap-diagnostics.sh,README.md}`, `work/optimize-fileops-poller/{verification,dev_handoff,implementation_plan}.md`, `log.md`.
Implemented and validated in the deployed build: self-PID kernel filter and counters; CO-RE regular-file fd filtering; compact tagged fd vs path records; wakeup batching with `force_wakeup_total`; 16 MiB FileOps ring buffer; kernel pseudo-path filtering and `pseudo_drop_total`; deployed-build fingerprinting and optional `bpftool` capture in the diagnostics bundle.
Results: smoke test proved the new build was live, with FileOps attached, 16 MiB ring buffer visible in `bpftool`, and first-minute `ring_fail_total=0` while `pseudo_drop_total` and `nonregular_drop_total` were already large. Overnight validation showed the same deployed hashes remained installed and that the feature made a substantial practical improvement in observability and early-drop volume reduction, but sustained ring-buffer loss still accumulated under long-running host load (`open`, `read`, `close`, `mmap` still rising materially).
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] feature | optimize-fileops-poller enters phase 2 (deep analysis)

Decision: stay in this feature rather than opening a new one. The original scope
(fop-01..fop-06 substance: counters, dead-work removal, self-PID filter, CO-RE
regular-file filter, kernel pseudo-path filter, compact records, wakeup batching,
16 MiB ring buffer) reached its current deployed state implemented with opencode
gpt-5.5 and gpt-5.4; the feature now continues as a deep-analysis phase.
Evidence constraint: raw runtime diagnostics are no longer readable in this
environment (security); analysis used only wiki-recorded summary statistics plus
read-only `../wintap` source.

Deep analysis (`work/optimize-fileops-poller/deep-analysis-2026-08-25.md`):
sustained overnight ring loss (~778 reserve failures/s across open/read/close/
mmap/write over the 9,121s counter window) is a steady-state userspace consumer
shortfall, not kernel emission or burst behavior. Root cause: the single
FileOps-Poller thread processes each surviving event synchronously through
`EventChannel.Send`, which runs a per-event DuckDB query under the process-global
`_dbLock` (plus a second query on miss) and a synchronous Esper `SendEventBean`,
with no queue between the ring buffer and that work (~12-25ms/lookup from the
2026-08-24 diagnostic implies a ~40-80 events/s ceiling). The 16 MiB ring
(~300k compact records) absorbs the smoke-test minute, then saturates. Ranked
next no-loss slices: fop-08 (bounded in-process queue + in-memory pid→pid_hash
current-process cache) front-runner, fop-09 (hoist per-event config lookups),
fop-10 (top-N per-comm/prefix aggregate counters for path-class attribution),
fop-07 still open; fentry/`bpf_d_path` stays deferred. Next slice selection
pending human sign-off.

Human decision recorded (2026-08-25): non-regular-file fd rows (`socket:[N]`,
`pipe:[N]`, `anon_inode:[N]`, ttys) are permanently dropped from the File
stream, ratifying the deployed CO-RE filter; pipe/anon_inode I/O invisibility
recorded as a fidelity gap (candidate future op class); the BTF-less fallback
tier stays as-is with the tier content difference documented.

Pages created: `work/optimize-fileops-poller/deep-analysis-2026-08-25.md`.
Pages updated: `work/optimize-fileops-poller/{brief,design,implementation_plan,dev_handoff,verification}.md`; `index.md`; `log.md`.

## [2026-08-25] direction | fileops phase-2 strategy discussion recorded

Human direction after reviewing the deep analysis: (1) the userspace workflow
optimizations (fop-08 queue + in-memory cache) are endorsed — memory spend on
queues is acceptable and helps spikes; (2) in-kernel short-interval aggregation
of file events by (pid, op class, identity) is now open for consideration,
amending the 2026-08-24 no-aggregation direction — motivated by suspected high
same-(pid,path) open/openat redundancy and by the fact that Esper aggregates
later in the pipeline anyway; recorded as gated candidate fop-11, with fop-10
extended to measure the open duplicate ratio first; (3) future task saved: an
OSS sensor survey (Falco/Sysdig, Tetragon, Tracee, Elastic ebpf, Sysmon for
Linux, osquery) on how peer projects handle event-volume and ring-drop
pressure.
Pages updated: `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] approval | fileops phase-2 plan approved and handed off

Human approved the full phase-2 plan: sequence fop-08 (+fop-09) → fop-10 →
fop-11 go/no-go. `dev_handoff.md` rewritten as the phase-2 dev handoff: the
copy/paste prompt now targets implementing fop-08 (in-memory pid→pid_hash
current-process cache replacing the per-event DuckDB query under `_dbLock`,
plus a bounded in-process queue between the ring callback and resolve/Esper
with depth/drop counters) and fop-09 (hoist per-event config lookups), with
acceptance criteria tied to the ~778/s ring_fail baseline from the deep
analysis and the standing no-loss differential gate. fop-11 aggregation stays
gated (fop-10 duplicate-ratio evidence + separate human go/no-go + verifier
spike + redefined differential contract). OSS sensor survey remains a parallel
future research task.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `index.md`; `log.md`.

## [2026-08-25] code | fileops phase-2 local fop-08/fop-09 slice

Files changed in `../wintap`: `wintap/core/infrastructure/IProcessResolver.cs`; `wintap/core/infrastructure/ProcessResolver.cs`; `wintap/core/infrastructure/EventChannel.cs`; `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: in-memory active-process cache for File-event pid-hash lookup; bounded FileOps sender queue between the ring callback and resolve/Esper; startup-cached `EventChannel` config/env flags; 60s queue depth/high-water/drop logging and File-event process-cache hit/miss logging; queue capacity knob `WINTAP_FILEOPS_MAX_QUEUE_EVENTS` (default `131072`).
Validation: `make clean && make` for tracers passed; `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.
Open follow-up: rerun the no-loss differential harness, deploy to the RHEL8 field host, capture queue/counter reconciliation, and verify whether overnight `ring_fail_total` growth collapses versus the ~778/s baseline.

## [2026-08-25] test | fileops phase-2 field-host non-root smoke workload session

Environment: deployed field host `spk16.llnl.gov`, but without root access from this shell.
Validation change: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` now copies `/tmp/fileops-phase2-smoke` into the diagnostics bundle when present.
Workload run: repeated deterministic FileOps stimulus using `validation/fileops-differential/fileops_workload.py`, session `/tmp/fileops-phase2-smoke/session-20260825T165200Z`, spanning `2026-08-25T16:52:00Z` to `2026-08-25T16:59:22Z`, 5 runs total, each with `--files 24 --rounds 4`, all exiting `0`.
Limitation: the existing parquet validator `devtools/file_capture_smoke_test.py` is not usable as this non-root user on the deployed host because default data-root discovery hits `PermissionError` on `/var/log/lintap`.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | fileops phase-2 deployed bundle shows queue saturation instead of ring saturation

Reviewed root-run diagnostics bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T172341Z` after the fop-08/fop-09 deployment. Outcome: `ring_fail_total=0` across all recorded FileOps op classes, `FileOps-Poller` is no longer hot, and `FileOps-Sender` is now the dominant CPU thread; however the new bounded userspace queue reaches capacity (`high_water=131072`) and records substantial per-minute drops (examples: `21567`, `47564`, `78368`, `50144`). The copied `/tmp/fileops-phase2-smoke` session is present in the bundle and aligns with the recorded workload window. This changes the active loss signal from kernel ring drops to userspace queue drops while confirming that the decoupling moved work off the poller as intended.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] code | fileops queue follow-on pre-enqueue identity stamping

Files changed in `../wintap`: `wintap/core/infrastructure/EventChannel.cs`; `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: File events now try to capture current-process identity from the active-process cache before entering the bounded sender queue, and `EventChannel.Send` skips sender-thread re-resolution for File events that already carry `PidHash` + `ProcessName`. Motivation came directly from bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T172341Z`, where sender-thread cache misses rose sharply once queue backlog deepened.
Validation: `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | fileops post-identity-stamping bundle removes queue drops in capture window

Reviewed root-run diagnostics bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T184934Z` against prior queue-saturation bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T172341Z`. Outcome: `ring_fail_total` remains `0`, and unlike the earlier bundle the bounded userspace queue records `drops=0` throughout the captured window even when depth rises above `100k` (`depth=102547`, `high_water=103187`). File-event process-cache behavior under backlog is materially healthier (for example `hit=54026,miss=4834` at the deepest recorded backlog versus prior collapse cases like `hit=139,miss=8388`). `FileOps-Sender` remains the dominant CPU thread, but the immediate loss mode improved from frequent queue drops to no observed queue drops during this collection.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] code | fileops fop-10 measurement slice

Files changed in `../wintap`: `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: bounded 60s FileOps measurement summaries for top-N emitted process-name buckets, top-N emitted path-prefix buckets, and the same-`(pid,path)` short-window open duplicate ratio. Summary state is bounded and logs coarse path-prefix buckets only, not raw paths.
Validation: tracer `make clean && make` passed; `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] review | later pre-fop-10 bundle shows queue drops returned

Reviewed additional same-build bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T203648Z` after the more encouraging `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T184934Z` snapshot. Outcome: kernel `ring_fail_total` still stayed `0`, but userspace queue saturation returned in multiple intervals, including substantial drop bursts (`30591`, `91570`, `385435`, `448425`, `1960545`). `FileOps-Sender` remained the dominant hot thread while `FileOps-Poller` stayed cold, confirming again that the current failure mode is sender-path/queue loss rather than ring loss. This downgrades the earlier zero-drop bundle from “likely stable” to “good short-window sample” and reinforces the need for `fop-10` attribution data before choosing the next reduction step.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | first deployed fop-10 bundle provides attribution and duplicate-open evidence

Reviewed first deployed `fop-10` diagnostics bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T210710Z`. Outcome: the new `measure=[...]` section is present in the `FileOps counters` log and reports top process-name buckets, top path-prefix buckets, and the same-`(pid,path)` short-window open duplicate ratio. The duplicate-open ratio is consistently high across sampled intervals (roughly `52.7%` to `83.7%`, commonly `60-80%`), with dominant surviving emitters including `rpm`, `systemd`, `splunkd`, `git`, `setroubleshoot*`, and dominant prefixes `/lib64`, `/usr`, `(relative)`, `/opt`, `/var` or `/`. Kernel `ring_fail_total` stayed `0`; queue drops were `0` in most sampled intervals but did recur later (`2:07:32 PM` interval: `depth=130909`, `high_water=131072`, `drops=39731`). The smoke-workload session `/tmp/fileops-phase2-smoke/session-20260825T205219Z` overlaps the pidstat collector flush schedule (`13:55:02` inside the session window, bounded by `13:50:02` and `14:00:02` writes), giving a practical correlation anchor for future pidstat analysis.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] milestone | fileops fop-11 proposal prepared for designer review

Based on the deployed `fop-10` evidence, the feature reached a new milestone: `fop-11` is no longer just a gated candidate but now has a concrete review-ready proposal. New artifact: `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`, recommending emit-first short-interval aggregation of repeat `open` / `openat` activity only, with bounded kernel state and a revised distinct-tuple-plus-count-conservation differential contract. Related feature pages updated to point at the proposal and to mark the `fop-10` review gate as reached.
Pages created: `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`.
Pages updated: `work/optimize-fileops-poller/brief.md`; `work/optimize-fileops-poller/design.md`; `work/optimize-fileops-poller/implementation_plan.md`; `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/verification.md`; `index.md`; `log.md`.

## [2026-08-25] code | fileops fop-12 absolute-path precondition slice

Files changed in `../wintap`: `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`. Files changed in `Wintap-Analytics`: `validation/fileops-differential/compare_fileops.py`; `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.
Implemented: pre-enqueue relative/openat `open` path resolution through `/proc/<pid>/fd/<fd>` when possible; logged resolution success/miss counters; Linux path-case preservation instead of unconditional lowercasing; File event time sourced from kernel monotonic timestamps converted to wallclock; comparator aligned to preserve Linux case.
Validation: `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests); `python3 -m py_compile validation/fileops-differential/compare_fileops.py` passed.
Open follow-up: deploy, confirm new resolution counters in the 60s FileOps log, verify relative-prefix collapse in `fop-10` measurement output, and rerun the differential harness on Linux-case-preserving output.

## [2026-08-25] review | first deployed fop-12 bundle shows resolution counters but relative-path bucket still large

Reviewed first deployed `fop-12` diagnostics bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T225502Z`. Outcome: the new `resolve=[relative_open_resolved=...,relative_open_resolve_miss=...]` section is present and `ring_fail_total` remains `0`; queue drops also stayed `0` in the sampled window. However, the absolute-path precondition is not yet met: relative-open resolution misses remain high (roughly `8.4k-9.8k` per sampled interval) and `(relative)` remains a top path-prefix bucket (`~8.6k-10.3k` total, mostly opens). The deployment therefore improved observability and preserved performance, but did not yet solve relative/openat identity conflation well enough to call `fop-12` accepted.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | post-fd0 short bundle improves resolution counts but relative bucket remains large

Reviewed short post-`fd=0` diagnostics bundle `/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T232323Z`. Outcome: queue drops stayed `0` and kernel `ring_fail_total` stayed `0`; the `fd=0` fix appears to raise relative-path resolution counts in at least some intervals (for example `relative_open_resolved=10654` with `relative_open_resolve_miss=23424` at `4:18:57 PM`, versus prior examples closer to `1.3k-1.7k` resolves). However, `(relative)` remains a major top-prefix bucket (`~8.3k-23.7k` total in reviewed lines) and miss volume is still too high to accept `fop-12` as complete. This confirms the bug fix was necessary but not sufficient, and points toward a next follow-on that preserves more open-time context such as `dirfd` for fallback absolute-path reconstruction.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] code | fileops fop-12 follow-on dirfd and cwd fallback

Files changed in `../wintap`: `wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`; `wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c`; `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: open/openat path records now carry `dirfd`; relative-path resolution now tries opened-fd first, then `cwd` or `dirfd`-base joins pre-enqueue; reason-split resolution counters were added so the next deployed bundle can show exactly which fallback path is recovering absolute paths and which misses remain.
Validation: tracer `make clean && make` passed; `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Open follow-up: deploy and compare `resolved_fd` vs `resolved_dirfd` vs `resolved_cwd`, and verify whether the `(relative)` top-prefix bucket finally shrinks materially.

## [2026-08-25] review | fop-11 proposal designer review completed

Reviewed [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]] and
the revised validation/semantic contract. Verdict: approved in principle —
the fop-10 evidence is sound (the duplicate measurement uses the same
(pid, path) key and 1000 ms window the proposal specifies, so the 52.7-83.7%
repeat ratios directly predict the design's win). Two hard conditions:
(1) relative-path opens must be excluded from aggregation (or keyed by
dirfd/cwd) — the (relative) bucket conflates distinct files and would break
the emit-first guarantee; (2) summary-record process identity must be stamped
at first-occurrence, not resolved at flush, to avoid reintroducing the
resolve-after-exit failure fop-08 fixed. One recommended re-scoping: implement
dedup in userspace pre-enqueue first (ring_fail is now 0 everywhere, loss is
queue-side, poller has idle headroom, and the fop-10 measurement dictionary is
the needed structure) — kernel promotion stays available later. Contract
notes: op-scope the revised rule, require drop-free runs for count
conservation, spec the repeat-metadata schema and comparator changes in the
spike. Review recorded in the proposal page §Designer Review.
Pages updated: `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`; `log.md`.

## [2026-08-25] direction | fop-11 human review response: scope expanded, fop-12 added

Human response to the fop-11 designer review: (1) relative-path handling
upgraded from "exclude from aggregation" to "resolve to absolute" — accurate
ground truth is the sensor's purpose; recorded as new precondition slice
fop-12 (recommended: readlink /proc/<pid>/fd/<fd> at open-exit, pre-enqueue);
(2) summary-record identity-at-first-occurrence condition accepted;
(3) aggregation direction formally amended: (pid, path, op)-level aggregation
with grouped totals (bytes etc.) and min/max timestamps over short intervals
is acceptable for ALL op classes (2026-08-24 "no aggregation" non-goal struck
in brief.md; sampling still excluded; emit-first semantics stand) — this also
brings the read/write burst loss mode inside fop-11's reach; (4) the OSS
sensor survey (Tetragon/Tracee/Sysdig et al.) stays deliberately deferred —
"improvements still coming"; natural trigger recorded as post-fop-11/12.
Dev handoff copy/paste prompt retargeted from fop-08/09 (deployed) to
fop-12 → fop-11 with the amended contract (count + byte-total conservation on
drop-free runs).
Pages updated: `work/optimize-fileops-poller/{fop-11-proposal-2026-08-25,brief,implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-25] analysis | fop-12 resolution options + additional win candidates

Source analysis of the relative-path resolution problem, recorded as
suggestions in `work/optimize-fileops-poller/dev_handoff.md` §"fop-12
Resolution Analysis + Additional Win Candidates". Ranked options: R1 readlink
`/proc/<pid>/fd/<fd>` at poller decode pre-enqueue (open-exit already emits
the returned fd; kernel resolves symlinks/dot-segments/dirfd in one call;
count misses, never hide them), R2 cwd/dirfd lexical join as fallback only
(openat_state lacks dirfd today; chdir race; symlink-unsafe `..` collapse),
R3 kernel-side not viable on RHEL8 4.18 (`bpf_d_path` is fentry/LSM-only).
Deeper wins found: A1 `NormalizeFilePath` lowercases paths on a
case-sensitive filesystem (`FileOpsSensor.cs:895`) — accuracy bug conflating
distinct files, fix also removes a per-event allocation; A2 kernel timestamps
still unused, needed for fop-11 min/max accuracy; A3 emit (s_dev, i_ino) —
CO-RE tier already reads `f_inode`, giving collision-free aggregation
identity and fd/PID-reuse validation; A4 mmap is collapsed into Read at
decode, erasing load/execution signal; P3 sampled sender cost-split
measurement to steer post-dedup optimization. A1/A4 and optional
full-canonicalization flagged as stream-content changes needing human
sign-off.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] analysis | Esper-layer findings reframe fop-11; A1-A3/P3 decided

Human decisions recorded: A1 path lowercasing becomes a platform-policy
function (Windows lowercases, Linux preserves case; single extraction point,
expandable); A2 kernel timestamps and A3 (s_dev, i_ino) emission and P3
sender cost-split sampling approved; A4 (distinct Mmap activity type)
explained further, sign-off still pending.

Esper-stream analysis (human-requested): `file.epl` already aggregates File
events into 10s batches grouped by (path, PidHash, PID, activityType,
ProcessName) with count(*)/sum(bytes)/min-max(eventTime), and `default.epl`
excludes File from per-event pass-through — so File telemetry is
aggregate-only on disk today, and fop-11 (sub-batch interval, compositional
accumulators) becomes a pure performance change at the parquet output. New
fop-11 hard conditions: File schema repeat-count field (default 1) +
first/last timestamps; file.epl switches count(*) → sum(count field) and
min/max over the new fields. Also noted: the comparator already measures the
aggregated rows (count conservation = asserting eventCount balance), A2
improves the accuracy of the existing firstSeen/lastSeen columns, and PidHash
stamping quality directly shapes output row grouping.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`; `log.md`.

## [2026-08-25] handoff | A4 decided; phase-2 fop-12/fop-11 dev handoff finalized

A4 (distinct Mmap activity type) approved by human sign-off as its own future
feature enhancement, deliberately deferred — not part of fop-12/fop-11;
recorded in the implementation plan's Phase-2 future tasks with the
downstream/comparator notes. Dev handoff for the next phase finalized: the
copy/paste prompt targets fop-12 (absolute-path ground truth via fd readlink,
pre-enqueue) then fop-11 (short-interval (pid, path, op) aggregation,
emit-first, userspace-first) with the Esper composition rules as hard
conditions (schema repeat-count + first/last timestamps, file.epl
count(*) → sum(count), sub-batch interval), plus approved companions A1
(platform path-case policy), A2 (kernel timestamps), A3 (dev:ino emission),
and P3 (sender cost-split sampling).
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] decision | R1 approved in base form; all fop-12/fop-11 sign-offs closed

Human sign-off: fop-12 implements base R1 only — fd-readlink resolution for
relative/openat paths; absolute-path opens keep their as-requested form. The
full-canonicalization extension (resolving all opens, surfacing symlink
targets) was explicitly declined for now and remains a documented future
option (if ever taken, carry both paths as a schema addition). With A1-A4 and
P3 already decided, no stream-content sign-offs remain open; the dev handoff
prompt is fully unblocked for the fop-12 → fop-11 implementation pass.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] milestone | fileops phase-2 wrap-up recorded; fop-11 stays blocked on path identity

Closed the current phase-2 implementation burst with a milestone wrap-up after
reviewing the deployed `fop-12` follow-ons through bundle
`/tmp/lintap-runtime-diagnostics-spk16.llnl.gov-20260825T234559Z`. Outcome:
queue/ring behavior remains materially better than the pre-phase-2 state,
`fop-10` successfully justified the `fop-11` design direction, and the latest
`dirfd`/`cwd` follow-on proved a real `dirfd` recovery contribution while also
showing that `cwd` is negligible. However, `relative_open_resolve_miss` and the
`(relative)` prefix bucket remain too large to accept `fop-12` as the hard
precondition for `fop-11`. A dedicated milestone page now captures the landed
work, strongest supporting evidence, and the best current fix hypotheses for
the next design pass.
Pages created: `work/optimize-fileops-poller/milestone-2026-08-25-phase2-wrapup.md`.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `work/optimize-fileops-poller/verification.md`; `index.md`; `log.md`.

## [2026-08-25] analysis | fop-12 gap diagnosed; fop-13 fix designed

Reviewed the deployed fop-12 work in `../wintap` (commit "Complete fop-12
path recovery") and the milestone evidence. Diagnosis: the ~8k/min
`relative_open_resolve_miss` floor is structural — all fop-12 fallbacks
(opened-fd readlink, cwd, dirfd readlink) read decode-time `/proc` state
while the dominant relative-open producers (`sed`, `awk`, `sh`, `rpm`
helpers) live milliseconds; `dirfd_lookup_miss ≈ relative_open_resolve_miss`
proves both readlinks die together. Structural root cause in the tracer:
O_DIRECTORY opens are discarded at open-exit (the records that would teach
userspace dirfd→path) and directory-fd closes are dropped by is_regular_fd
(so any dirfd knowledge must be identity-keyed, not (pid,fd)-keyed).
Fix recorded as fop-13 in `work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25.md`:
fop-13a miss-cause counter split (measurement-first), fop-13b kernel-time
identity in one record-format slice — dirfd (s_dev,i_ino) stamping, internal
DIR_OPEN records feeding a global (s_dev,i_ino)→dir-path LRU index, and file
dev:ino emission (approved A3) so fop-11 can aggregate on (pid, dev:ino, op)
independent of path quality. Non-fixes recorded (latency shaving, more cwd,
retro-resolution). fop-11 unblocks on the dev:ino track after fop-13b.
Pages created: `work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25.md`.
Pages updated: `work/optimize-fileops-poller/{implementation_plan,dev_handoff}.md`; `index.md`; `log.md`.

## [2026-08-25] code | fop-13a/fop-13b implemented locally

Files changed in `../wintap`: `FileOpsSensor.cs`, `file_ops_tracer.bpf.c`,
`file_ops_tracepoint.bpf.c`. Files changed in this repo:
`validation/fileops-differential/{compare_fileops.py,fileops_workload.py}`.
Implemented per the gap analysis: DIR_OPEN internal records (O_DIRECTORY opens
no longer discarded; un-flagged directory opens detected via i_mode), file and
dirfd (s_dev, i_ino) captured in-kernel at event time, a global bounded
dir-identity index in userspace giving a race-free resolution step that works
after producer exit, miss-cause counter split (producer-dead vs alive), new
resolve/dir_open counters in the 60s log, comparator relative→absolute upgrade
matching with an opt-in gate, and a deterministic dirfd-relative workload
scenario. Build-time find: the open-exit handlers hit the BPF stack limit with
the new locals; fixed by removing the 264-byte openat_state stack copy
(read map value directly, delete after emit).
Validation: both tracer tiers build; Lintap builds with 0 errors;
Linux-relevant test classes 10/10 (Windows-specific test failures verified
pre-existing on this host); comparator synthetic scenarios 4/4; workload smoke
run clean. Field deployment, counter baselining vs 20260825T234559Z, and the
A/B differential remain pending (RHEL8 host rebuilds its own .bpf.o — objects
are gitignored).
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-25] maintenance | diagnostics resolve-triage extract + fop-13 handoff refresh

`extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` now emits
`journal/lintap-file-log-fileops-resolve.txt` — a timestamped extract of just
the `resolve=[...]` counter section so the fop-13 recovery mix, miss-cause
split, and dir-index health are reviewable at a glance (the full counter lines
were already captured; awk extraction verified against a synthetic log line;
`bash -n` passed). `dev_handoff.md` refreshed: fop-13 marked implemented
locally, copy/paste prompt retargeted from "implement fop-13" to "deploy on
the RHEL8 host and run field acceptance," including the rebuild-on-host rule
for the gitignored .bpf.o objects and the acceptance checklist vs the
20260825T234559Z baseline.
Pages updated: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`; `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] review | fop-13 first field run triaged; findings dispositioned

First deployed fop-13 bundle (reviewed by the implementing agent, recorded in
verification.md) confirms the gap-analysis diagnosis: relative_open_resolve_miss
collapsed from the ~7997-8814/min floor to 0-945/min, heavy miss windows are
dominated by miss_producer_dead, the dir index is live and healthy
(dir_open_indexed ~11.6k-19.3k, dir_index_size 1055, evictions 0), (relative)
left the top prefixes, and ring_fail_total stayed 0. Queue drops recurring
under load are the expected sender-ceiling problem — designer position: no
separate follow-on; fop-11 pre-enqueue dedup is the queue-drop fix, sequenced
after fop-13 acceptance (full spaced-smoke bundle + differential rerun).

Code-review findings triaged: F1 (global (s_dev,i_ino) keying aliases across
mount namespaces) accepted → new slice fop-13c, mnt_ns-aware index keying,
not an acceptance blocker; F2 (comparator over-credits relative upgrades,
presence-based matching) accepted → count-conserving matcher in the
test/harness hardening slice; F3 (miss-split best-effort under PID reuse)
accepted as documented limitation, no change; F4 (no automated DIR_OPEN /
recovery-path tests) accepted → same hardening slice (extract dir-index logic
into a testable class).
Pages updated: `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] closeout | fop-12/fop-13 accepted; fop-11 implementation starts

Human acceptance closes fop-12 and fop-13: the path-identity precondition for
fop-11 is met (evidence summarized in verification.md §fop-13 Closeout). The
4x queue capacity (524288) is validated and will become the code default in
the fop-11 slice; RSS accounting deferred to the upcoming longer execution
cycle via the standing pidstat-collector parquet series; the differential
rerun folds into fop-11's standing A/B gate. fop-11 implementation
(pre-enqueue emit-first aggregation per the approved proposal, with P3
cost-split sampling riding along) begins now.
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-25] code | fop-11 implemented locally

Files changed in `../wintap`: `shared/WintapAPI/WintapMessage.cs` (File schema:
EventCount default 1, FirstSeen/LastSeenEventTime FileTime longs),
`wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs` (new, dependency-free,
unit-testable), `FileOpsSensor.cs` (absorb hook, summary emitter, flush timer,
shutdown drain, agg=/sender= counters, P3 send sampling, queue default 524288),
`wintap/core/etl/esper/file.epl` (count(*) → sum(file.eventCount); min/max over
the new fields with case-fallback to eventTime — parquet columns unchanged,
Windows senders safe via defaults), `tests/Wintap.Tests/FileOpsAggregatorTests.cs`
(new, 9 tests) + test csproj compile-include (linux sources are excluded from
the Wintap assembly). Files changed in this repo: `compare_fileops.py`
(eventCount-weighted tuple counts — the standing gate is now count-conserving
across pre/post-aggregation streams).
Semantics: emit-first at (pid, path, op), 1000ms window (matching the fop-10
measurement), summaries carry repeats-only counts and first-occurrence
identity, bounded table with counted per-event bypass, kill switch
WINTAP_FILEOPS_AGG_ENABLED=false for same-build A/B.
Validation: Lintap build 0 errors; 19/19 targeted tests (incl. 9 new
aggregator tests: count conservation, emit-first, rollover, cap bypass,
identity-at-first-occurrence); comparator synthetic aggregation scenarios
pass (conserved rc=0, shortfall rc=1). Field deployment and A/B acceptance
pending; dev_handoff retargeted to the fop-11 deploy/acceptance pass.
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-25] maintenance | fop-13 field feedback transcribed; wiki confirmed current

Pre-push audit found the fop-13 deployed-bundle reviews existed only in the
field-side clone's summaries, not in this clone's verification.md. Transcribed
them into verification.md §fop-13 Field Runs (first deployed bundle, same-
instance follow-up with the 6:19:29 PM at-scale proof line, and the 4x
queue-capacity experiment bundles 023152/024019), clearly sourced and
delimited so a field-side merge can prefer richer local copies if present.
index.md footer refreshed to the current feature state. Wiki now carries the
complete fop-12/fop-13 record: gap analysis, implementation, field feedback,
review-finding dispositions, closeout, and the fop-11 local slice.
Pages updated: `work/optimize-fileops-poller/verification.md`; `index.md`; `log.md`.

## [2026-08-25] maintenance | collector carries the full fop-11 acceptance evidence; field-side read-only policy recorded

Human direction: the field-side clone stays read-only (policy) — no commits
from that system; bundle reviews continue arriving as summaries and are
transcribed here. Consequence: the diagnostics bundle must carry everything a
review needs. `collect-lintap-diagnostics.sh` extended accordingly:
timestamped `agg=[...]` and `sender=[...]` triage extracts (fold ratio,
cap_bypass/summary_enqueue_fail health, P3 send_sample_avg_us), an
esper-errors extract (a silently failed file.epl deploy would break File
output while sensor counters look healthy), and
`duckdb/fileops-parquet-sanity.txt` — newest File parquet queried for
rows vs sum(eventCount) (composition proof), aggregated-row count,
firstSeen/lastSeen sanity, and zero-firstSeen rows, with a build-agnostic
fallback query. Validated: bash -n, awk extracts against synthetic log
lines, and the sanity SQL against synthetic parquet (3 rows → 6 raw events,
1 aggregated row). SUMMARY.txt key-files list updated. A rerun of the
collector on the field host now yields the remaining fop-11 acceptance
evidence except the A/B differential (which needs the kill-switch run).
Pages updated: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`; `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] ingest | dev/field workflow promoted to canonical wiki page

Human direction: project context recorded in agent memory (~/.claude) must
also live in the wiki — the wiki is the shared knowledge base, agent memory
is a private pointer. Promoted the dev/field process knowledge to
`wiki/workflow/lintap-dev-field-workflow.md`: the lintap-dev / spk16 split,
the field-side read-only policy and dev-side transcription process, the
self-sufficient-diagnostics principle, pull-only deploys with on-host tracer
rebuilds, push mechanics (dev VM has no credentials; the human pushes), and
the agent-memory mirroring policy itself. The agent memory file now points
at the wiki page as canonical.
Pages created: `workflow/lintap-dev-field-workflow.md`.
Pages updated: `index.md`; `log.md`.

## [2026-08-25] handoff | bundle reviewer prompt added for the fop-11 collector

The field-side reviewer's guidance predated the collector update, so a
dedicated reviewer prompt was added to dev_handoff.md (§Bundle Reviewer
Prompt): maps each new bundle file to its acceptance question with expected
healthy values — agg fold ratio (50-80% expected under load) and health
counters, P3 sender headroom arithmetic, queue deltas vs fop-13-era bundles,
resolve regression bounds, the esper-errors stop-ship rule, and the
parquet-sanity composition proof (raw_events > rows; the eventCount
column-error signature identifies a pre-fop-11 build). Output contract:
transcription-ready summary statistics only, per the read-only field policy.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] review | fop-11 bundle 041718 triaged; dir-index churn dispositioned as fop-13d

Third fop-11 bundle (same execution) transcribed into verification.md: queue
drops stayed 0, ring 0, aggregation health clean (cap_bypass=0,
summary_enqueue_fail=0, substantial repeats_folded), P3 send_sample_avg_us
captured (~356-2202us). New finding: late-run dir-index saturation — the
index pins at its 16384 cap with 133k-144k evictions/interval and
dir_index_miss ≈ total miss (322-357/min), the signature of a filesystem
walk flooding the FIFO-evicted index and flushing hot base directories.
Designer disposition: a fop-13 structural limit exposed by runtime, not a
fop-11 defect — does NOT block fop-11 acceptance (degraded misses are ~4% of
the pre-fop-13 floor and smoke anchors stay clean); new hardening slice
fop-13d added to the plan (touch-on-hit LRU eviction, cap 16384 → 65536 with
env knob). Remaining fop-11 gates unchanged: kill-switch A/B differential and
a post-collector-update bundle (parquet composition sanity).
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-25] code | fop-13c/fop-13d + F2/F4 hardening implemented locally

Human-directed dev pass implementing all deferred hardening. In `../wintap`:
fop-13c — CO-RE tracer stamps the opener's mount-namespace inum on path
records (+8B; fallback tier zeros) and the dir index keys by
(mnt_ns, s_dev, i_ino), closing the bind-mount/container aliasing risk from
review finding F1; fop-13d — the index is extracted into a dependency-free
DirIdentityIndex class (F4) with touch-on-hit LRU eviction and cap 65536
(WINTAP_FILEOPS_DIR_INDEX_MAX), fixing the scan-flood churn from bundle
041718; DirIdentityIndexTests (7) including LRU hot-entry scan-flood
survival. In this repo: F2 — the comparator's relative→absolute matcher is
count-consuming against the candidate's absolute surplus, longest-suffix
first, with over-credit/count-bound/no-double-dip scenarios verified;
stretch — fileops_workload.py --dir-churn N synthetic filesystem-walk
scenario for field validation of the LRU fix.
Validation: both tracer tiers build; Lintap 0 errors; 26/26 targeted tests;
all comparator scenarios pass; churn workload smoke run clean.
DEPLOY NOTE: record format changed — tracers must be rebuilt on the field
host together with Lintap (mixed deploy misreads mnt_ns). Handoff deploy
steps and reviewer prompt updated (post-13d eviction/miss decorrelation
rule).
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-26] acceptance | fop-13c/fop-13d field-accepted; loss point moves downstream (fop-14 candidate)

Bundle 053404Z transcribed: queue drops 0 throughout, aggregation healthy
with ~50-66% folding, dir index at the new 65,536 cap with heavy eviction
churn AND strong resolution (29,469 resolved vs 354 missed in the burst
minute) — the eviction/miss decorrelation rule is satisfied and fop-13c/13d
are field-accepted. Late-run residual miss pockets (48-49/min, producer-dead
+ cwd) are the known transient-process class, not index pressure.
New finding dispositioned as fop-14 candidate (measurement-first): the ETL
serializer/parquet-writer stage dropped ~63k rows in 3.5 min during the
heavy window against its 10,000-row default caps — the active end-to-end
loss point now sits downstream of the sensor, and dedup cannot shrink it
(Esper output is distinct-group-driven). Owner-resolution warnings noted as
producer-lifetime residual + log-hygiene item. fop-11 still owes the
kill-switch A/B and a parquet-sanity bundle.
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-26] maintenance | end-of-day sync audit; wiki confirmed consistent

Pre-handoff audit for tomorrow's pickup: dev_handoff Phase 2 Status now
carries the fop-13c/13d field acceptance and the fop-14 disposition; the
copy/paste prompt's goal is refreshed to the actual remaining work (fop-11's
two formal gates — kill-switch A/B and a parquet-sanity bundle from the
updated collector — plus the human's fop-14 go/no-go); index.md footer and
the actively-edited docs' last_validated dates bumped to 2026-08-26. State
at close: fop-01..fop-13d complete and field-accepted; fop-11 deployed and
healthy pending its two gates; fop-14 candidate awaiting decision; deferred
future tasks unchanged (Mmap activity type, OSS sensor survey).
Pages updated: `work/optimize-fileops-poller/{dev_handoff,verification,implementation_plan}.md`; `index.md`; `log.md`.

## [2026-08-26] code | comparator gains cross-run A/B flags for the fop-11 gate

Pre-A/B gap found: the comparator keyed tuples by (pid, path, op), so two
separate executions (different PIDs, different background activity) could
never compare cleanly. Added --ignore-pid (collapse the pid key) and
--path-prefix (restrict to the deterministic workload's work dir), verified
with a synthetic cross-run scenario (fails without the flags, clean with
them). The fop-11 kill-switch A/B procedure uses both flags with the SAME
work-dir path for both runs so workload paths are identical across runs.
Pages updated: `validation/fileops-differential/compare_fileops.py`; `log.md`.

## [2026-08-26] code | fop-11 A/B fully automated after manual procedure failed

The manual A/B produced a vacuous result (zero workload tuples both sides —
time-window parquet copying raced the serializer flush cadence, and the
first diagnostic ran without root so the permission-restricted data root
globbed empty silently). Fixes, in order: comparator gained --ignore-pid and
--path-prefix (cross-run A/B was structurally impossible with pid-keyed
tuples), then an exit-2 vacuous-pass guard (empty prefix-scoped baseline can
never read as success), and finally the whole procedure was scripted:
validation/fileops-differential/run_fop11_ab.sh runs both phases end to end
— kill-switch env management with cleanup-on-exit, agg-state verification
from the live counter log, restart-as-flush boundaries, row-level harvesting
by non-overlapping firstSeen windows + work-dir prefix, serializer-backlog
invalidation (exit 3), and the count-conserving comparison with a verdict
summary. A --simulate mode with a fixture generator
(simulate_ab_fixture.py) tests the full pipeline off-host; the first
simulation caught a window-overlap bug (ON harvest captured both phases'
rows) — fixed by clamping each phase's window to start after the previous
phase's end. Final simulation: baseline 6 raw rows vs candidate 5 aggregated
rows weighing 6 — missing=0, added=0, PASS, exit 0.
Pages updated: `validation/fileops-differential/{run_fop11_ab.sh,simulate_ab_fixture.py,compare_fileops.py}`; `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-26] debug | fop-11 A/B FAIL root-caused to file.epl ungrouped-AgentId n² eventCount inflation

Source: first successful field fop-11 A/B runs on spk16 (results 20260826T232412Z and the relative-harvest rerun), preserved per-phase Lintap.log/counters snapshots, and `../wintap` source review (FileOpsAggregator.cs, FileOpsSensor.cs, EventChannel.cs, FileSerializer.cs, esper/*.epl).
Outcome: the comparator FAIL (baseline 5800 event-weighted tuples vs candidate 1470) is NOT a fop-11 defect. `file.epl` (and `registry.epl`) select `AgentId` without grouping or aggregating it, so Esper classifies the statement as aggregated-but-not-fully-aggregated and emits one output row PER INPUT EVENT, each stamped with the batch-group's `sum(eventCount)` — n events in a group become n rows × n counts. Proof from harvested parquet: 32 hot-loop reads → exactly 32 rows × EventCount=32 = 1024; 33 opens → 1090; the aggregated candidate showed 2 rows × group-sum (67/64). `tcp.epl`/`udp.epl` already group AgentId and are unaffected. fop-11 aggregation itself conserved exactly (summary carried 32/32 folded repeats; `summary_enqueue_fail=0`, `cap_bypass=0`).
Fixed in `../wintap` 0e01783 (grantj-rhel8-testing): AgentId added to both group-bys. Consequence for consumers: all production File/Registry `eventCount` values to date are batch-quadratically inflated (larger groups inflate more), which also likely contributed to fop-10's high duplicate-open ratios read from parquet-derived views (the sensor-side `open_dup` measure is pre-Esper and is a separate open question).
Harness hardening landed en route (Wintap-Analytics grantj-rhel8-testing 9139e01..4060483): serializer-count parse fix; harvest narrowed to the real FileSerializer flush schema (`File_Path` lowercased, `FirstSeen` FileTime) and to serializer flush files + raw_sensor/raw_process_file; upload cycle parked via `WINTAP_ETL_UPLOAD_INTERVAL_SEC` (delete-after-upload and startup `clearRawSensor()` were destroying evidence; Lintap.log is LogType.Overwrite so per-phase log snapshots are now saved into the results dir); `WINTAP_ETL_MAX_QUEUE_EVENTS_FILESERIALIZER=100000` for the run (agg-off flood saturates the 10k drop-newest queue and ate the workload burst); zero-row harvest diagnostics; in-window relative rows passed through to the comparator's relative-upgrade matching.
Open follow-up: rebuild/redeploy the fixed sensor on spk16 and rerun the A/B — expected PASS with off-phase hot reads collapsing to 1 row × EventCount 32 per 10s batch. Known operational hazard: an interrupted run leaves the parked upload-interval line in `/etc/lintap/lintap.env` and a later run's cleanup "restores" it as pre-existing; verify the line is absent after failed runs.
Pages updated: `log.md`.

## [2026-08-27] review | fop-11 A/B PASS on spk16 with fixed EPLs — count conservation accepted

Source: field run `/var/tmp/fop11-ab-results-20260827T032142Z` on spk16 with the `../wintap` 0e01783 EPL fix deployed.
Outcome: VERDICT PASS, exit 0. Baseline 1272 event-weighted regular tuples (down from 5800 under the n² inflation — now matching the workload's actual syscall count), candidate 1292, missing=0, added=20 (candidate-side background surplus, tolerated by design), unmatched_relative=0. ON-phase counters healthy: 24.9k repeats folded, 3.9k summaries, `summary_enqueue_fail=0`, `cap_bypass=0`. OFF rows 687 (one row per group per 10s batch, as intended post-fix) vs 1280 in the inflated runs. fop-11 kill-switch count conservation is accepted.
Harness hardening: leftover env-override lines from interrupted runs are now discarded instead of being "restored" into production (the parked upload interval survived two cleanup cycles on spk16 this way; field host cleaned up manually).
Pages updated: `log.md`.

## [2026-08-27] decision | fop closeout dispositions and byte-conservation gate implemented

Human dispositions toward feature closeout:
- **fop-12: ACCEPTED** (post-fop-13 field evidence: relative_open_resolve_miss 0-6/interval, workload relative opens resolving 36/36 via the dir index, vs the 8-10k floor that blocked acceptance).
- **fop-08 differential debt: discharged** by the fop-11 A/B harness runs (OFF phase exercises the full post-fop-08 pipeline; PASS 20260827T032142Z).
- **fop-14: watch long-term** during longer test deployments rather than a dedicated re-measurement now (prior severity number was taken under the per-event-row EPL inflation and is not trusted).
- **EPL-fix mainlining (../wintap 0e01783): deferred** — no production deployments at present, so no urgency beyond normal branch flow.
- **Historical eventCount inflation: check the "ACME" dataset** before treating it as a practical problem — many changes have landed since the last production deployment, so pre-fix inflated parquet may not exist in any dataset anyone consumes. If ACME's File/Registry data predates the last deployment gap, re-baseline or fence it; otherwise close the concern.

Implemented: byte-total conservation in the comparator (`compare_fileops.py --check-bytes`, wired into `run_fop11_ab.sh`, Wintap-Analytics 67f463d) — per regular tuple, candidate summed BytesRequested must not fall below baseline (deficit fails with samples; surplus mirrors tolerated added counts; warn-and-skip when a bytes column is absent). Simulation passes with bytes verified; deficit and missing-column paths unit-tested. The fop-11 differential contract's three invariants (distinct tuples, count conservation, byte conservation) are now all machine-checked; the next field A/B run verifies them together.
Remaining for fop-11 acceptance: the collector-bundle gate (duckdb/fileops-parquet-sanity.txt), then closeout mechanics (verification/brief/index status flips).
Pages updated: `work/optimize-fileops-poller/{implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-27] decision | fop-11 differential contract amended: 1% missing-tuple tolerance for capture noise

Run 20260827T141730Z FAILED with missing=8, added=6 of 1278 baseline event-weighted tuples — while bytes conserved exactly (568320 = 568320) and yesterday's identical run passed with missing=0. Every missing/added entry is a paired open+close single on a distinct `fileops-RR-FFF.dat` round-robin file. Diagnosis: the pre-existing open path-record miss (`open: no_path` ≈14-23/interval in every counters line) drops the open AND orphans its close (the fd→path store never learns the fd), losing ~1% of open/close pairs per phase; which phase eats the flake is a coin flip, so a strict any-missing gate flaps. This is per-event capture noise upstream of aggregation — fop-11 defects lose counts at repeat scale (the EPL bug was -75%), not 0.6%.
Contract amendment: `compare_fileops.py --missing-tolerance <fraction>` (default 0 = strict; `run_fop11_ab.sh` passes 0.01). Missing tuples are still fully reported in result.json; within-tolerance passes print an explicit NOTE. Byte conservation and unmatched-relative gates remain strict. Unit-tested at the observed noise scale (1% pair loss: tol 0 fails, tol 0.01 passes with note); simulation unchanged.
Residual product observation (pre-existing, not fop-11): the open/close pair loss itself — candidate root cause is open-event/path-record correlation; visible as `no_path`+`fallback_miss` on opens. Not queued; noted for any future capture-fidelity work.
Pages updated: `log.md`.

## [2026-08-27] decision | fop feature CLOSED — accepted; closeout test plan published

Human accepted all remaining fop items and closed the feature. Final gates: fop-11 A/B byte-verified PASS on run 20260827T141730Z (counts within the documented 1% tolerance, bytes exactly conserved, relative clean) on top of the strict-zero PASS of 20260827T032142Z. Published [[wiki/work/optimize-fileops-poller/test_plan]] — six critical milestone tests (T1 build+unit smoke, T2 harness simulation self-test, T3 deploy smoke checklist, T4 the kill-switch A/B differential as THE milestone test, T5 collector parquet sanity, T6 fop-14 long-term watch) superseding the per-slice intermediate tests, which remain recorded in verification.md for deep-dives. Brief marked CLOSED; index rows updated.
Carried out of the feature: fop-14 long-term watch; ~1% open+close capture flake (product observation, unqueued); ACME dataset historical-inflation check; ../wintap 0e01783 EPL fix must ride any future deploy.
Pages updated: `work/optimize-fileops-poller/{brief,verification,test_plan}.md`; `wiki/index.md`; `log.md`.

## [2026-08-27] decision | fix-unbounded-process-table-growth CLOSED — accepted; long-run acceptance parallelized; canonical promotion done

Human accepted the current state of the parent feature to unblock the branch PR (Windows developer needs the shared-core changes; no production deployments yet). The dev handoff's long-run evidence gate is superseded: long-running acceptance shifts to the new parallel task [[wiki/work/extended-deployment-monitoring/brief]] — 1-2 week human status checks over multi-host test deployments for ~a few weeks, with short focused patch cycles expected; exit criteria and the carried watch items (fop-14, ~1% capture flake, ACME dataset check) recorded there.
Canonical promotion (deferred by the handoff until closeout) done: [[wiki/component/process-table-retention]] (retention sweep, liveness reconciliation, bounded telemetry, CLONE_THREAD filter, plateau figures, DuckDB lock caveat) and [[wiki/component/fileops-event-pipeline]] (stage contracts kernel→parquet, the Esper group-by rule behind the n² eventCount bug, flush schema, caveats). P1 process-creation pytest re-verified green (5/5) as PR preflight; T2 harness sim green.
Pages updated: `work/fix-unbounded-process-table-growth/{brief,verification}.md`; `work/extended-deployment-monitoring/brief.md` (new); `component/{process-table-retention,fileops-event-pipeline}.md` (new); `wiki/index.md`; `log.md`.

## [2026-08-27] feature-open | selinux-monitoring: SELinux as a first-class Lintap eBPF event domain

Opened via the LLM-assisted feature workflow after a three-round interview.
Core decision:
the auditd/TSV batch path (`../Lintap/sql/selinux.sql`, never-committed
collector, known TZ/join losses) was a crude POC and is superseded as a
non-goal; instead SELinux telemetry becomes first-class Lintap events —
eBPF-captured, flowing in parallel with process/file/network through
tracer → sensor → EventChannel → Esper → serializer → raw_sensor parquet.
Signals split by purpose: AVC denials/grants for policy debugging;
transitions + a novel-tuple-deduped (src ctx, tgt ctx, class, perm)
interaction map for monitoring. Constraints: RHEL 9-class kernel only
(existing host available), ../wintap Linux sensor tree for code, EPL
group-by invariant. Four acceptance criteria frozen (provoked denial vs
ausearch, transition coverage, interaction-map DuckDB query, overhead/
no-loss gate). v1 boundary: raw_sensor parquet — dashboards, Wintappy DBT,
and RHEL 8 deferred. Attach points (selinux_audited tracepoint vs BPF LSM
vs kprobes) delegated to an on-host spike; spike stub created. Sealed human
estimates recorded in interview.md (seal intact for downstream agents).
Pages created: `work/selinux-monitoring/{interview,brief,references,spike}.md`.
Pages updated: `wiki/index.md`; `log.md`.

## [2026-09-17] spike | selinux-monitoring attach-point probe executed on localhost (lintap-dev)

Ran the spike's census + throwaway probes in an Ubuntu 24.04 / kernel 6.8 /
arm64 local validation environment, separate from the RHEL environment: SELinux compiled
in but inactive (AppArmor is the MAC; getenforce Disabled), so attach
mechanics and formats were fully verified while denial/transition
provocation and true AVC rates remained open for the SELinux-enabled environment. Key findings:
(1) `avc:selinux_audited` tracepoint present with scontext/tcontext/tclass
as strings — no SID resolution needed for the denial/audited-grant stream;
(2) BPF LSM programs load AND attach successfully without `bpf` in the
boot lsm= list but silently never fire (0 hits) — do not build on BPF LSM,
or gate hard on /sys/kernel/security/lsm; (3) fentry/kprobe tiers all
attach: `avc_has_perm(ssid,tsid,tclass,requested,…)` is a one-hook source
for the interaction-map tuple (numeric SIDs — SID→context resolution is now
THE design problem), `avc_audit` is inlined (hook `slow_avc_audit`),
transition candidates `selinux_bprm_committed_creds`/`security_transition_sid`
verified attachable; (4) allow-side rate proxy via generic LSM hooks:
~2.5k/s idle → ~118k/s under fs load — in-kernel dedup mandatory, sizing
keys on tuple cardinality not rate. Recommendation: three-hook hybrid
(tracepoint + avc_has_perm fentry w/ novel-tuple dedup + transition kprobe),
no BPF LSM tier. Spike stays open pending the RHEL 9 re-run (backport
deltas, enforcing-mode tests, real rates). Probes were throwaway in
/tmp/selinux-spike; nothing landed in ../wintap.
Pages updated: `work/selinux-monitoring/spike.md` (results+recommendation,
status stub→draft, confidence low→medium); `wiki/index.md`; `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: RHEL 9 spike collector built

Built a temporary self-contained collector that reruns the spike census and every
probe left open by the localhost run: tracepoint capture in a private
tracefs instance vs ausearch ground truth, provoked denials (runcon
attempts designed to be refused), transition workload under a
security_transition_sid/selinux_bprm_committed_creds probe, attach-mode
tests (kfunc/fentry/kprobe + BTF signatures), and 15s idle/load
avc_has_perm rate + distinct-tuple cardinality windows for dedup-map
sizing. Degrades gracefully without bpftrace (tracefs kprobe_profile hit
counts). Output: one self-sufficient tarball per the field-workflow bundle
rule; cleanup trap removes all tracefs state. Smoke-tested end-to-end on
lintap-dev (SELinux-inactive degraded mode): all phases run, attach tests
and BTF dumps correct, zero-event paths handled. Next: run in the RHEL
validation environment and retain a minimized, sanitized digest; results
are transcribed into spike.md before design.md opens.
Pages updated: `work/selinux-monitoring/spike.md` (prototype location,
follow-ups); `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: RHEL validation results transcribed; collector v2

Collector v1 ran in the RHEL validation environment (bpftrace absent →
tracefs fallback); a sanitized digest was transcribed into spike.md. The
environment confirmed SELinux enabled/Permissive; CONFIG_LSM includes
bpf AND selinux; selinux_audited tracepoint present with the identical
string-bearing field set as 6.8; all candidate kallsyms present; Tier 1
proven end to end (2 provoked runcon denials captured with full context
strings in the private tracefs instance). Real rates via kprobe_profile:
avc_has_perm ~4.6k/s idle, ~13.1k/s under fs load; security_transition_sid
~40/s; slow_avc_audit 0 baseline (denial stream naturally low-volume).
Recommendation updated: kprobe avc_has_perm as verified interaction-map
baseline (fentry as later optimization); BPF LSM viable on RHEL 9 but kept
out of the critical path with the startup lsm-list gate. Collector v2
built and smoke-tested (forced-fallback mode, clean teardown verified):
fixes the ausearch -ts quoting bug that voided ground truth, adds
no-bpftrace distinct-tuple cardinality + transition tuples via tracefs
hist triggers (Entries: line = dedup-map sizing), adds the bprm-commit
kprobe to fallback rates; make-digest now captures active-LSM/auditd
lines. Remaining before design freeze: one v2 validation rerun
(cardinality + ausearch match); design.md can start now on the answered
attach-point basis.
Pages updated: `work/selinux-monitoring/spike.md`; `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: spike ANSWERED (v2 validation run); design.md drafted

Collector v2 ran in the RHEL validation environment; a sanitized digest
was transcribed into spike.md and the spike is now ANSWERED
(confidence high, status reviewed). v2 closed the gaps: active LSM list
confirmed `capability,yama,selinux,bpf`; ausearch ground truth recovered
(19 AVC records, shape-matches the tracepoint — masks vs decoded perm
names); THE sizing number measured via hist trigger: 421 distinct
(ssid,tsid,tclass) tuples over ~30s (212,960 hits, Dropped 0, top tuple
43%, top-10 ≈89%); rates ~2.4k/s idle, ~11.8k/s load; transitions 15
distinct tuples, bprm ~2/s. The window also captured background AVC
denials (file/tcp_socket/dir classes, permissive=1), validating the
feature's policy-debugging purpose. Drafted
work/selinux-monitoring/design.md: three streams on the verified hooks —
tracepoint AVC events; bprm-commit transition kprobe (osid!=sid filter,
blob-offset startup self-handshake); interaction map on
**avc_has_perm_noaudit** (design correction: it's the single choke point —
avc_has_perm wraps it and inode_permission calls it directly) with 16k
in-kernel LRU emit-first dedup; SID→context resolution as slice-1
prototype-then-fallback (sidtab string cache vs /proc-attr + learned
tables); policy-epoch via SELinux netlink; schema/EPL (group-by
invariant)/serializer shapes; kill switch WINTAP_SELINUX_ENABLED;
counters incl. ring_fail_total=0 gate. Brief Open Questions annotated
with answers.
Pages updated: `work/selinux-monitoring/{spike,brief}.md`;
`work/selinux-monitoring/design.md` (new); `wiki/index.md`; `log.md`.

## [2026-09-17] decision | selinux-monitoring design: five open questions decided (human, one-at-a-time review)

All five design.md open questions decided, each taking the recommended
option: (1) SID→context resolution — timeboxed R1 sidtab string-cache
prototype in slice 1, R2+R3 composite as shipping fallback; (2)
interaction-stream permissions — one row per permission, mask exploded at
ETL to match the acceptance tuple; (3) MessageType names FROZEN now:
SELINUX_AVC / SELINUX_TRANSITION / SELINUX_INTERACTION (parquet subdirs
selinux_avc/transition/interaction); (4) flush policy — 30 s default,
zero-delta tuples skipped; (5) fentry — overhead-gated upgrade only
(kprobe ships; switch only if criterion-4 overhead gate is crowded).
design.md Open Questions converted to a Decisions section; body text
synced. Design is now unblocked for implementation_plan.md +
dev_handoff.md (slice-1 outputs to record back: R1 adopt/reject,
avc_has_perm_noaudit rate/cardinality confirmation, measured overhead).
Pages updated: `work/selinux-monitoring/design.md`; `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: implementation_plan + dev_handoff published

Published the two remaining pre-implementation artifacts. Implementation
plan declares abbreviation `sel`, five slices evidence-first: sel-01
validation-environment measurements (avc_has_perm_noaudit rate/cardinality via the
spike hist method, timeboxed R1 sidtab-cache prototype with adopt/reject
recorded back into design.md, cred-blob self-handshake) — no production
code; sel-02 tracer + sensor skeleton; sel-03 resolver/dedup-flush/
policy-epoch; sel-04 ETL (frozen SELINUX_* types, row-per-permission
explode, EPL group-by rule); sel-05 the four frozen acceptance criteria
in the validation environment with assets in this repo. Dev handoff authorizes
../wintap changes (platform/linux/sensor/ebpf, core/etl, additive-only
collect/models) + Analytics validation/, carries the copy/paste prompt
(with the interview-seal warning), the spike traps (hook noaudit not the
wrapper; avc_audit inlined; BPF LSM silent-inert; ausearch -ts recent),
field-workflow rules (pull-only deploys, environment-local tracer rebuilds,
and minimized, sanitized evidence digests),
delegated decisions, and closeout/promotion duties. Feature is ready for
the code-development agent; recommended first slice sel-01 (sel-02
permitted first if the validation environment is unavailable).
Pages created: `work/selinux-monitoring/{implementation_plan,dev_handoff}.md`.
Pages updated: `wiki/index.md`; `log.md`.

## [2026-09-18] feature-progress | selinux-monitoring sel-02: tracer + sensor skeleton validated; RHEL 8.10 variance flagged

sel-02 executed in ../wintap (SELinux exploration branch; transcribed from
implementor summaries): selinux_tracer.bpf.c (tracepoint + bprm-commit
kprobe + interaction kprobe preferring avc_has_perm_noaudit with runtime
wrapper fallback, ringbuf/stats/self-PID filter, 16k LRU novel-emit dedup),
SELinuxSensor.cs skeleton (census, load/attach+fallback, decode, heartbeat
+ 60s counters; ETL=sel-04, resolver/flush=sel-03), plus registration,
config keys (WINTAP_ENABLE_SELINUX_SENSOR, WINTAP_API_URLS w/ Program.cs
listen-URL configurability), libbpf_get_error P/Invoke, and a
ProcessRundown disable-override fix. build_ebpf/build_dotnet PASS. In the
validation environment, all three streams captured — 16 AVC events, 20 transitions,
interaction stream folding 2,907,492 checks into 2,748 novel tuples
(~99.9% in-kernel fold, decode_errors=0, map occupancy ≪16k — validates
spike sizing). The environment uses RHEL 8.10 with a 4.18-series kernel,
not RHEL 9-class — a soft contradiction was flagged in brief.md against
the "No RHEL 8 in v1" non-goal; spike environment
labels corrected (data stands; tracepoint is a 4.18 backport; fentry
doubtful). New trap: avc_has_perm_noaudit in kallsyms but perf kprobe
attach EINVAL(-22) on this kernel; wrapper fallback runs with the inode
fast-path coverage caveat. GATE added before sel-03 acceptance: fix the
noaudit attach (tracefs form/legacy opts/offset/fentry attempt) or human
scope decision (wrapper-only 8.10 vs out-of-scope). verification.md
created with the full sel-02 record.
Pages created: `work/selinux-monitoring/verification.md`.
Pages updated: `work/selinux-monitoring/{implementation_plan,design,
dev_handoff,brief,spike}.md`; `wiki/index.md`; `log.md`.

## [2026-09-18] lint | selinux-monitoring: hook-language normalization + sel-02 date provenance

Implementor review flagged an interaction-hook naming drift across the
feature docs (spike.md's recommendation had been reworded to plain
"kprobe on avc_has_perm" when measured rates were inserted, while
design.md/dev_handoff.md kept noaudit-preferred). Normalized all three to
one policy statement: preferred production hook remains
`avc_has_perm_noaudit` where attachable (covers the inode fast path); in
the RHEL 8.10 validation environment it is kallsyms-visible but rejects
perf-event kprobe attach with EINVAL, so sel-02 uses `avc_has_perm` as a
validated fallback with an explicit coverage caveat. Also corrected
sel-02 evidence dates 2026-09-17 → 2026-09-18 to match runtime log
provenance (design decisions keep their true 2026-09-17 date), rephrased
the sel-02 checklist note ("implementation and smoke validation
complete via wrapper fallback; formal checkbox open pending decode unit
tests and noaudit attach resolution"), and recorded two sel-02 details
from the code-alignment review: ringbuf wakeup fix (userspace now
receives novel-tuple events) and attach-error surfacing via
libbpf_get_error. sel-03 gate unchanged.
Pages updated: `work/selinux-monitoring/{spike,design,dev_handoff,
implementation_plan,verification,brief}.md`; `wiki/index.md`; `log.md`.

## [2026-09-18] feature-progress | selinux-monitoring sel-03: core mechanics package-validated

sel-03 partial implementation validated under the packaged service in an
RHEL 8.10 validation environment with a 4.18-series kernel. Results were
transcribed from a minimized, sanitized validation summary.
Green across the new mechanics: class/permission decoder (132 classes /
2,150 perms from selinuxfs, per-event class+perm names in samples), R2/R3
resolver skeleton (hit=2854/miss=1365/learned=27 — live source contexts
resolve via /proc/<pid>/attr/current, targets mostly numeric until
learned), interaction LRU flush (rows=1703, events=259171, zero_delta=770,
iterations=2473, errors=0), policy-epoch via /sys/fs/selinux/policy
polling (delegated netlink-vs-poll choice exercised as polling),
unknown-perm-mask telemetry (counted+top-N, never a drop; fd/sem
concentration flagged as a sel-04 decode-test watch item),
decode_errors=0 throughout; in-kernel dedup at packaged scale 322,851
folded vs 1,301 novel per interval. noaudit EINVAL reproduces identically
under the service — wrapper fallback confirmed in both run modes; sel-03
hook-scope GATE unchanged. Doc changes: verification.md sel-03 section;
plan sel-03 "IN PROGRESS — package-validated"; design confirms
unknown-bits-as-telemetry + R2 validation + polling note + explicit
unresolved-context schema rule for sel-04 (SSid/TSid always present,
SContext/TContext nullable when unresolved); handoff records
packaged-service testing as the preferred validation path and documents
the local test-port override; spike gets the volume-prediction-confirmed
follow-up note.
Remaining before sel-03 closes: EventChannel emission, decode/flush/
resolver unit tests (sel-02 holdover included), hook-scope decision.
Pages updated: `work/selinux-monitoring/{verification,implementation_plan,
design,dev_handoff,spike}.md`; `wiki/index.md`; `log.md`.
## [2026-08-27] feature-work | improve-etl-and-qa started via LLM-assisted feature workflow

Source: source inspection of `../Wintappy/Makefile`, `../Wintappy/notebooks/wintap_dbt_overview.py`, `../Wintappy/wintap_dbt/dbt_project.yml`, pidstat/monitoring/silver model SQL under `../Wintappy/wintap_dbt/models/`, and this repo's legacy Streamlit/DataQA imports under `streamlit/projects/`.
Pages created: `work/improve-etl-and-qa/interview.md`; `work/improve-etl-and-qa/brief.md`; `work/improve-etl-and-qa/references.md`.
Pages updated: `index.md`.
Decisions captured: cross-repo scope with Wintappy as center of gravity; all-event-family ETL/QA cleanup rather than pidstat-only; pidstat promoted to first-class bronze/silver/gold; Wintappy Marimo established as the canonical QA entry point; Analytics-side conflicts to be aligned or retired; stronger end-to-end verification required.
Open questions: compatibility window for existing datasets/consumers; final bronze/silver/gold/monitoring contract per event family; which legacy Analytics QA paths should be updated vs. explicitly deprecated.

## [2026-08-27] feature-work | improve-etl-and-qa: design and staged plan added

Source: source inspection of Wintappy gold models (`process_summary`, `process_file_summary`, `process_net_summary`, `process_uber_summary`), monitoring models, and legacy Analytics-side DataQA code paths.
Pages created: `work/improve-etl-and-qa/design.md`; `work/improve-etl-and-qa/implementation_plan.md`.
Pages updated: `index.md`.
Design direction recorded: separate event-family modeling from QA presentation; make pidstat a first-class family with explicit gold output; normalize the bronze/silver/gold story across process, file, network, and pidstat; treat monitoring as a consumer of intentional family outputs; keep Wintappy Marimo canonical and only align or retire conflicting Analytics-side QA paths.
Implementation staged into seven slices: contract decisions, pidstat family implementation, broader event-family cleanup, monitoring cleanup, Marimo alignment, Analytics-side conflict cleanup, and end-to-end verification/canonical promotion.

## [2026-08-27] feature-work | improve-etl-and-qa: Stage 1 contract decisions recorded

Source: consumer-usage inspection across `../Wintappy/notebooks/wintap_dbt_overview.py`, DBT model refs under `../Wintappy/wintap_dbt/models/`, Wintappy review notes, and this repo's legacy DataQA references.
Pages updated: `work/improve-etl-and-qa/design.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
Decisions recorded: preserve current canonical downstream silver/gold relation names already anchoring Marimo/wiki contracts (`process`, `process_file`, `process_net_conn`, `process_summary`, `process_uber_summary`, `pidstat_metrics`); keep monitoring as a distinct cross-family QA layer; rewrite monitoring to prefer intentional silver/gold inputs over accidental bronze/raw-backed dependencies; do not add broad compatibility aliases for legacy raw-name assumptions; first code slice should center on pidstat gold plus monitoring cleanup and Marimo alignment.
Remaining open questions: exact pidstat gold contract, which legacy Analytics pages merit alignment, and whether any non-pidstat family later justifies a deliberate canonical rename.

## [2026-08-27] feature-work | improve-etl-and-qa: first coding slice defined

Source: detailed inspection of Wintappy monitoring SQL (`build_summary`, `telemetry_event_summary`, `process_chart`, `file_chart`, `network_chart`, `perf_chart`) and the pidstat section of `../Wintappy/notebooks/wintap_dbt_overview.py`.
Pages updated: `work/improve-etl-and-qa/design.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
First-slice contract recorded: add `pidstat_process_summary` as the first pidstat gold model; keep `pidstat_metrics` as silver detail; update monitoring to prefer intentional silver/gold inputs (`process_file`, `process_conn_incr`, `pidstat_metrics`) over raw-backed bronze views where feasible; change the notebook pidstat section to use row-based availability and the new pidstat gold summary. File/network chart rewrites are explicitly first-slice targets using current silver timing fields rather than a larger event-time redesign.
Deferred question narrowed: after the first-slice silver-based chart rewrite, decide whether file/network timeline fidelity is sufficient or whether a later slice needs a chart-specific detail contract.

## [2026-08-27] code | improve-etl-and-qa first coding slice implemented

Files changed: `../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql` (new); `../Wintappy/wintap_dbt/models/monitoring/{build_summary,telemetry_event_summary,file_chart,network_chart}.sql`; `../Wintappy/notebooks/wintap_dbt_overview.py`; `../Wintappy/wintap_dbt/models/schema.yml`; `wiki/work/improve-etl-and-qa/{implementation_plan,verification}.md`; `wiki/index.md`; `wiki/log.md`.
Implemented: introduced the first pidstat gold model (`pidstat_process_summary`), moved summary-style monitoring queries off raw-backed runtime dependencies and onto intentional silver/detail inputs where feasible, and aligned the Marimo pidstat section to use row-based availability plus the new pidstat gold summary.
Verification: `make dbt-build` passed (`PASS=78`); `make dbt-test` passed (`PASS=39`); direct built-DuckDB query smoke for `build_summary`, `telemetry_event_summary`, `file_chart`, `network_chart`, `perf_chart`, `pidstat_process_summary`, and the notebook pidstat queries all succeeded without creating the DBT raw-source S3 secret in the direct session.
Known gap: the current configured dataset/window still has zero pidstat parquet rows, so pidstat gold is structurally verified but not yet validated with non-empty live pidstat data; `file_chart` currently uses `process_file.min_event` as the first-slice silver timing basis and may need a later higher-fidelity chart contract.

## [2026-08-28] fix | improve-etl-and-qa mixed-schema eventtime hotfix

Source: dbt failure report for `process_registry` (`Conversion Error: Unimplemented type for cast (TIMESTAMP -> BIGINT) when casting from source column EventTime`) during a Wintappy build.
Files changed: `../Wintappy/wintap_dbt/macros/time.sql`; `../Wintappy/wintap_dbt/models/silver/{host,host_ip,process_file,process_registry,process_image_load}.sql`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added `unix_or_timestamp_expr()` and `win32_or_timestamp_expr()` macros so silver models tolerate either timestamp-typed or numeric `eventtime` inputs without blindly casting to `bigint`; updated the affected silver models to use the new macros.
Verification: targeted `dbt run` for `process_registry` plus related dependents passed after the change, and a full `make dbt-build` re-run passed in `129.86s` with `PASS=78`.
Known gap: no dedicated timestamp-vs-epoch regression fixture/test exists yet; validation is currently by successful DBT execution on the current dataset mix.

## [2026-08-28] fix | Wintappy uv workflow cleanup

Source: local failure report showing `uv add` could not use `../Wintappy/.venv` because the environment directory existed but had no Python executable, plus the deprecated `--isolated` Makefile usage and missing `plotly` dependency for the legacy `qa-pidstat` target.
Files changed: `../Wintappy/Makefile`; `../Wintappy/pyproject.toml`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: removed deprecated `uv run --isolated` usage from the Makefile's DBT runner, added a `rebuild-venv` target for one-step local recovery, and added `plotly` to dev dependencies so the `qa-pidstat` marimo path resolves its import.
Verification: `make rebuild-venv` recreated `.venv`; `uv sync --all-extras --dev` completed successfully; `uv run --dev --project . python -c "import plotly, marimo; print(plotly.__version__)"` passed with `plotly==7.0.0`.
Note: the broken `.venv` was a local environment-state problem rather than a repository-tracked file issue; the repo changes only make the recovery path and dependency behavior saner going forward.

## [2026-08-28] feature | Simple pidstat time-series chart added to Marimo QA

Source: now-available pidstat rows in the current Wintappy DuckDB plus notebook-focused design follow-up.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a first-pass pidstat time-series panel to the canonical Marimo QA notebook with a metric dropdown (`CPU %`, `Memory %`, `Read KB/s`, `Write KB/s`), a minimum peak-CPU filter, a max-series cap, and a 1-minute bucketed line chart over `pidstat_metrics` for the selected top processes from `pidstat_process_summary`.
Verification: the backing query returned `2811` rows across `12` plotted series in `0.46s` on the current dataset with a `25%` peak-CPU threshold, and the updated notebook compiled cleanly via `python -m py_compile notebooks/wintap_dbt_overview.py`.
Known limitation: this is intentionally a simple first cut; richer focusing controls (legend-based hiding, host/container selectors, alternative ranking criteria) are left for a later UX iteration if the chart proves useful.

## [2026-08-28] feature | Pidstat chart UX upgraded from grokdata review

Source: review of `../Lintap/teletap/grokdata_marimo.py` as a prototype reference for stronger layout and interaction patterns.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: kept the canonical Wintappy notebook but borrowed key grokdata ideas for the pidstat panel — moved from Altair to Plotly for the pidstat time-series area, switched ranking/filtering to the selected metric instead of always peak CPU, added a host filter, and enabled a range-slider-based interactive time axis.
Verification: notebook compiled cleanly; an example selected-metric smoke query (`Memory %`, threshold `0.1`) returned `5845` rows across `5` plotted series in `0.35s`.
Remaining gap: the overall Wintappy page layout is still more section-oriented than grokdata's full dashboard composition; only the pidstat panel was upgraded in this pass.

## [2026-08-28] feature | Event-volume correlation chart added to pidstat section

Source: follow-up user request to compare Lintap CPU/resource usage against event volume by type over time.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a second Plotly chart directly below the pidstat process-resource chart, using the same host filter and 1-minute buckets to show normalized event counts over time by type (`process`, `file`, `network`, `registry`, and `image_load` when present).
Verification: the backing query returned `5024` rows in `0.33s` on the current dataset, with active series for `process`, `file`, `network`, and `registry`; notebook compile check remained clean.
Known limitation: this is currently a notebook-level correlation view built directly from normalized tables rather than a dedicated DBT monitoring model, and cross-family "event count" semantics remain pragmatic rather than formally unified.

## [2026-08-28] feature | Pidstat command aggregation mode added

Source: follow-up exploration request using `setroubleshootd` as the motivating repeated-instance process family.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a pidstat `Aggregation` control with `Per process` and `By command` modes. `By command` ranks series by the selected metric, aggregates matching process instances into one family series, and includes concurrent PID counts in hover data.
Verification: a targeted `setroubleshootd` smoke query returned `380` rows in `0.27s`, collapsed to one visible command-level series with `concurrent_pids` preserved per bucket. This matched the exploratory finding that `setroubleshootd` instances are largely serial repeats rather than long-lived overlapping processes.
Open follow-up: decide whether command aggregation should later offer alternate rollup semantics such as `sum`, `average per instance`, or `max instance`.

## [2026-08-28] feature | Pidstat controls and chart comparability polished

Source: follow-up UX request for clearer aggregate controls and a more comparable event-volume display.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: renamed aggregation options to `Per process instance` and `Aggregate by command`, added a `Command contains` filter for narrowing repeated-instance families like `setroubleshootd`, and enabled a bottom-axis range slider on the event-volume subplot stack so its interaction style more closely matches the pidstat chart above.
Verification: command-filtered aggregate smoke query for `setroubleshootd` returned the expected single family series (`380` rows in `0.27s`); notebook compile check remained clean.
Known limitation: the pidstat and event-volume plots still do not share truly linked zoom because they remain separate Plotly figures.

## [2026-08-28] milestone | improve-etl-and-qa interim checkpoint written

Pages created: `work/improve-etl-and-qa/milestone-2026-08-28.md`.
Pages updated: `index.md`; `log.md`.
Summary: captured the current interim state after the first major wave of code work: pidstat gold landed, the canonical Wintappy QA notebook now supports interactive pidstat exploration plus event-volume correlation, mixed-schema eventtime handling is hardened, uv workflow cleanup is recorded, and the explicit next-slice decisions (monitoring promotion, linked zoom, broader event-family cleanup, Analytics-side conflict pass) are listed in one place.

## [2026-08-28] plan | Lintap stair-step memory-growth instrumentation

Source: analysis of the current run's pidstat and event-volume data for the long-lived `Lintap` process on `spk16`.
Pages created: `work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md`.
Pages updated: `work/improve-etl-and-qa/implementation_plan.md`; `index.md`; `log.md`.
Summary: current evidence points to burst-correlated memory ratcheting, likely file-pipeline-driven, but pidstat alone cannot distinguish true retained state from allocator/runtime retention. The plan therefore layers `/proc/<pid>/smaps_rollup`, .NET runtime counters, and periodic internal file-pipeline/serializer backlog counters on top of the existing pidstat/event-volume view, with sampling cadences and a prioritized rollout order recorded in the new artifact.

## [2026-08-28] update | Lintap instrumentation plan refined for manual-batch-first execution

Source: follow-up planning request focusing on immediate impact versus eventual long-term sidecar collection.
Pages updated: `work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
Summary: refined the plan to distinguish two operating modes: (A) manual batch capture now, recommended first for speed and overhead validation; (B) long-term sidecar collection later, using the same raw-style parquet layout. Added concrete proposed event types (`perf_smaps_rollup`, `perf_dotnet_counters`, `perf_lintap_diag`, `perf_fd_map`) and updated Stage 8 to make manual-batch-first the default implementation path.

## [2026-08-28] code | Manual-batch performance collectors added under validation/

Source: implementation follow-through on the memory-growth instrumentation plan's immediate-impact path.
Files created: `validation/perf-collection/pyproject.toml`; `validation/perf-collection/README.md`; `validation/perf-collection/src/wintap_perf_collection/{__init__.py,procfs.py,parquet.py}`; `validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py`; `validation/perf-collection/scripts/run_lintap_perf_batch.sh`; `validation/perf-collection/tests/{test_procfs.py,test_manual_batch.py}`.
Pages updated: `work/improve-etl-and-qa/{implementation_plan,verification}.md`; `log.md`.
Implemented: a standalone manual-batch collection package that samples `/proc/<pid>/smaps_rollup`, `/proc/<pid>/status`, and `/proc/<pid>/{fd,maps}` for a target process and writes partitioned parquet event types (`perf_smaps_rollup`, `perf_proc_status`, `perf_fd_map`) into canonical `raw_sensor/<event_type>/dayPK=/hourPK=` layout. Optional external stdout line capture is supported for provisional `perf_dotnet_counters_raw` and `perf_lintap_diag_raw` event streams so command shape can be iterated before long-term promotion.
Verification: `cd validation/perf-collection && uv run --project . --extra dev pytest` passed (`4 passed`), including an end-to-end fake-procfs test that writes real parquet outputs.
Known gap: not yet exercised against a live Linux `Lintap` process from this repo; external-command capture is structurally implemented but not yet validated with real `dotnet-counters` or future Lintap diagnostic output.

## [2026-08-29] handoff | Host-ready Lintap memory experiment continuation

Pages created: `work/improve-etl-and-qa/dev_handoff.md`.
Pages updated: `index.md`; `log.md`.
Summary: recorded a host-oriented continuation handoff for the live Lintap experiment. It points the next session at the perf-collection package, the current QA notebook, and the new instrumentation plan; captures the real-run parquet row counts already observed on-host; and explicitly elevates embedded DuckDB inside the long-running .NET process as a major memory-growth suspect alongside file-pipeline and runtime/allocator hypotheses.

## [2026-08-29] code | Live-host perf collector tightening on spk16

Source: direct inspection of `/tmp/lintap-perf` parquet plus follow-up validation commands on the live `spk16` host against PID `743557` (`/usr/lib/lintap/Lintap`).
Files changed: `validation/perf-collection/src/wintap_perf_collection/{procfs.py,cli/manual_batch.py}`; `validation/perf-collection/tests/{test_procfs.py,test_manual_batch.py}`; `validation/perf-collection/README.md`; `wiki/work/improve-etl-and-qa/{implementation_plan.md,verification.md}`; `wiki/log.md`.
Implemented: tightened `smaps_rollup` parsing so the address-range header line no longer becomes a bogus parquet column, and added structured `perf_dotnet_counters` row derivation from captured `dotnet-counters monitor` console output while retaining `perf_dotnet_counters_raw`.
Verification: `cd validation/perf-collection && uv run --project . --extra dev pytest` passed (`6 passed`). Existing on-host raw `dotnet-counters` parquet (`478` lines) now parses into `26` structured counter rows. Existing root-run `smaps`/`status` parquet still points toward anonymous/private memory (`RssAnon 2060344..2112368 kB`, flat `RssFile 169448 kB`, flat `AnonHugePages 1177600 kB`) with stable FD/map counts (`open_fd_count 485..487`, `mapped_regions 4776..4787`).
Permission note: as the current unprivileged user on `spk16`, fresh live collection against the root-owned `Lintap` service can read `/proc/<pid>/status` but not `/proc/<pid>/smaps_rollup`, `/proc/<pid>/fd`, or the .NET diagnostics socket. End-to-end live verification of the fixed `smaps` path and a new `dotnet-counters` capture therefore remains blocked pending a host permission change.

## [2026-08-29] code | Focused root-wrapper added for live spk16 captures

Source: follow-up implementation request after the `spk16` permission check showed that the active `Lintap` service is root-owned and blocks fresh unprivileged `smaps`, `fd`, and .NET diagnostics access.
Files changed: `validation/perf-collection/scripts/capture_lintap_perf_for_user.sh`; `validation/perf-collection/README.md`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a tactical root-side wrapper that self-escalates via `sudo`, resolves the live `Lintap` PID as `root`, runs `wpc-perf-batch` against that PID, auto-enables `dotnet-counters monitor ...` when available, and `chown`s the output tree back to the invoking user so the resulting parquet is immediately usable without wider host permission changes.
Verification: `cd validation/perf-collection && bash -n scripts/capture_lintap_perf_for_user.sh` passed.

## [2026-08-29] test | Fresh root-wrapper capture validated on spk16

Source: operator-ran `validation/perf-collection/scripts/capture_lintap_perf_for_user.sh` against the live root-owned `Lintap` service on `spk16`, producing run `perf-1788028744` under `/tmp/lintap-perf/parquet/raw_sensor/`.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: fresh readable user-owned parquet landed for `perf_smaps_rollup`, `perf_proc_status`, `perf_fd_map`, `perf_dotnet_counters_raw`, and structured `perf_dotnet_counters`. The fixed `smaps_rollup` parser worked on live host data with no bogus header-derived column. Current memory remains mostly anonymous/private (`VmRSS 2405416..2452760 kB`, `RssAnon 2125524..2172868 kB`, flat `RssFile 169448 kB`, `Anonymous 2130236..2176124 kB`, `AnonHugePages 1208320..1292288 kB`) while FD/map counts stayed relatively stable (`open_fd_count 485..487`, `mapped_regions 4770..4791`). Structured runtime counters also landed successfully (`34` parsed rows across `26` counters), including `working_set_mb`, `gc_heap_size_mb`, `gc_committed_bytes_mb`, `cpu_usage`, and `allocation_rate_b_5_sec`.

## [2026-08-29] test | One-hour idle baseline on spk16

Source: operator-ran `capture_lintap_perf_for_user.sh` with run id `lintap-perf-60m` while the host was mostly idle.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: the one-hour procfs baseline completed with `714` rows each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`, covering `2026-08-29T19:01:21Z -> 2026-08-29T20:01:17Z`. RSS and anonymous memory fluctuated within roughly an 80-90 MB band but ended lower than they started (`smaps.Rss 2421536 -> 2389236 kB`, `status.VmRSS 2419140 -> 2386360 kB`, `Anonymous 2141500 -> 2109196 kB`, `RssAnon 2139248 -> 2106472 kB`), while FD/map counts remained broadly stable (`open_fd_count 486..494`, `mapped_regions 4765..4838`). This is useful negative evidence: on an idle host, the current `Lintap` instance did not keep ratcheting upward over an hour.
Runtime-counter caveat: the raw `perf_dotnet_counters_raw` stream spans the full hour (`478` rows through `2026-08-29T20:01:22Z`), but the structured `perf_dotnet_counters` derivation only captured an initial burst (`44` parsed rows) because later `dotnet-counters monitor` screen-refresh output collapses multiple updates into ANSI-heavy composite lines. That points the next runtime-counter improvement toward `dotnet-counters collect --format json|csv` or a richer ANSI-aware parser.

## [2026-08-29] code | dotnet-counters path moved to collect/json-csv

Source: follow-up implementation request after the hour-long idle baseline showed that the old `dotnet-counters monitor` screen-scrape path was too lossy for durable long-run structured parsing.
Files changed: `validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py`; `validation/perf-collection/scripts/{capture_lintap_perf_for_user.sh,run_lintap_perf_batch.sh}`; `validation/perf-collection/tests/test_manual_batch.py`; `validation/perf-collection/README.md`; `wiki/work/improve-etl-and-qa/{dev_handoff.md,verification.md}`; `wiki/log.md`.
Implemented: removed the old monitor/raw `.NET` path, added direct parsing for `dotnet-counters collect --format json|csv`, and switched the root wrapper to auto-enable file-based `collect` output by default. The only remaining raw external-command capture in this package is the future-facing `perf_lintap_diag_raw` path.
Verification: `cd validation/perf-collection && uv run --project . --extra dev pytest` passed (`8 passed`), covering JSON parsing, CSV parsing, and a fake-collector end-to-end parquet write. Also verified the real export schema locally by collecting both JSON and CSV from a temporary sample .NET process under `/tmp/opencode`.
Host note: an assistant-run live smoke of the new root wrapper could not complete from this noninteractive session because `sudo` on `spk16` requires a terminal/password prompt. A user-run rerun on-host is still needed to replace the older monitor-derived `perf_dotnet_counters` host artifacts with new collect-based ones.

## [2026-08-29] test | collect-based dotnet-counters host smoke validated on spk16

Source: operator-ran `capture_lintap_perf_for_user.sh` with `RUN_ID=lintap-perf-collect-smoke`, `DOTNET_COUNTERS_FORMAT=json`, and `WINTAP_DATA_ROOT=/tmp/lintap-perf-collect` against the live root-owned `Lintap` service.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: the new collect-based `.NET` path worked end to end on the real host. `perf_dotnet_counters` landed as structured parquet with `108` rows across `27` distinct counter keys over `2026-08-29T20:36:46Z -> 2026-08-29T20:37:00Z`, including stable provider/name/type/tag/value fields and counters such as working set, GC heap size, GC committed bytes, allocation rate, CPU usage, exception count, threadpool metrics, and per-generation sizes/counts. Matching procfs smoke rows also landed (`4` each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`). This replaces the old monitor-derived host validation as the preferred runtime-counter capture path.

## [2026-08-29] test | collect-based one-hour rerun on spk16

Source: operator-ran a second `lintap-perf-60m` host capture after the collector switched to `dotnet-counters collect`, producing fresh `hourPK=21` parquet under `/tmp/lintap-perf/parquet/raw_sensor/`.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: the collect-based long run produced `9720` structured `perf_dotnet_counters` rows across `27` counter keys for `2026-08-29T20:41:27Z -> 2026-08-29T21:41:16Z`, plus `714` matching rows each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`. Memory again stayed within a bounded band rather than showing obvious monotonic runaway (`smaps.Rss 2389332 -> 2420164 kB`, range `2313792..2433876`; `VmRSS 2387040 -> 2416260 kB`, range `2308556..2428896`; `Anonymous 2109032 -> 2140112 kB`, range `2033484..2153568`). FD/map counts also stayed broadly stable (`open_fd_count 485..488`, `mapped_regions 4756..4866`). The new `.NET` telemetry spans the full hour cleanly, with examples including `working_set_mb 2384.67 -> 2471.87`, `gc_heap_size_mb 541.85 -> 659.10`, `gc_committed_bytes_mb 1252.23 -> 1254.89`, and `cpu_usage 12.06..23.06`.
Operator note: this rerun reused the historical `run_id` value `lintap-perf-60m`, which caused naive cross-partition queries to blend the earlier monitor-era run with the new collect-based rerun. Future comparison runs should use distinct `RUN_ID`s.

## [2026-08-29] review | Lintap long-run CPU readiness

Sources read: current committed `../wintap` Lintap paths for serializer, FileOps aggregation/cache, cache/upload, EventChannel, and process retention; current `validation/perf-collection` collectors; and the `spk16` one-hour verification record.
Pages created: `work/improve-etl-and-qa/cpu-growth-review-2026-08-29.md`.
Pages updated: `work/improve-etl-and-qa/dev_handoff.md`; `index.md`; `log.md`.
Findings: the current roughly 19% idle-host CPU result is a baseline, not a growth trend. Review identified queue/flush work, unmatched FileOps FD-path state, aggregation sweeps, cache/upload cycles, and process-retention maintenance as concrete CPU or joint CPU/memory candidates. Next work is measurement-first: long baseline, per-thread/stack attribution, cadence correlation, and low-overhead queue/cache/cycle diagnostics, all gated by zero-drop and count/byte-conservation evidence.

## [2026-08-29] code | Lintap CPU observability and serializer safety first slice

Branch: `../wintap` `grantj-lintap-cpu-observability` from current `develop` after `git fetch --all --prune`.
Files changed: `../wintap/wintap/core/etl/extract/Serializer.cs`; `../wintap/wintap/platform/linux/sensor/ebpf/{FileOpsAggregator,FileOpsSensor}.cs`; `../wintap/wintap/core/etl/load/CacheManager.cs`; `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `../wintap/tests/Wintap.Tests/FileOpsAggregatorTests.cs`; feature verification/plan/handoff records.
Implemented: serializer flushes cannot overlap, emit drain/duration/remaining-queue/Parquet-backlog diagnostics, and group message types in a single pass. FileOps now reports FD-cache cardinality and aggregation flush timing. Cache/upload and process-retention cycles report elapsed time and bounded-state context. No sensor filters, aggregation semantics, queue limits, or drop policies changed.
Verification: `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter "FullyQualifiedName~FileOpsAggregatorTests"` passed (10/10). The unfiltered Wintap test project remains Linux-incompatible because pre-existing Windows SID/ETW tests fail and the test host aborts during ETW cleanup.

## [2026-08-30] test | First CPU-observability one-hour Lintap capture

Source: `/tmp/lintap-perf/parquet/raw_sensor/*/dayPK=20260830/hourPK=00/` and `/var/log/lintap/runtime/Logs/Lintap.log` on `spk16`, targeting Lintap PID `2400026`.
Results: CPU averaged `11.42%`; the first and second halves averaged `11.39%` and `11.44%`, so no within-hour CPU ratchet was observed. This was startup-adjacent, with service start eight minutes before sampling. The critical result is fidelity failure: `fileserializer` reached its active 10,000-event cap continuously and had dropped at least `394529` file events by 17:25 PDT. Its flushes took `2..19 ms` with no overlap, FileOps sender drops were zero, and aggregation cap bypass was zero, isolating the immediate problem to serializer admission/batch cadence. FD-cache metrics rose from `20` PID maps / `24` entries to `1439` / `1784`, confirming the long-run cache-growth risk. Cache-cycle and resolver-maintenance timing are recorded in the verification artifact.

## [2026-08-30] review | FileOps aggregation regression check

Sources read: last-week FileOps/fop history in `../wintap`, current eBPF-to-Esper-to-serializer path, deployed `/usr/lib/lintap/ETLConfig.json`, `/usr/lib/lintap/esper/file.epl`, and deployed BPF-object hashes.
Result: no evidence that the recent fop aggregation work regressed or that aggregation is bypassed. The deployed EPL and FileOps BPF object exactly match current source; the EPL contains the `AgentId` grouping fix for the historical n-squared inflation bug. Positive `repeats_folded` and zero `cap_bypass` show aggregation is active. Its emit-first, `(pid,path,operation)`-keyed, one-second design intentionally does not reduce high-cardinality unique file activity, so it cannot prevent the demonstrated downstream 10,000-event serializer-cap loss by itself. The cap and drop policy predate the last-week fop work.

## [2026-08-30] code | FileSerializer no-drop cadence

Prediction recorded before implementation: a five-second FileSerializer-only flush cadence should keep observed post-aggregation file volume below the existing 10,000-event cap, eliminating serializer-drop warnings without changing FileOps count/byte semantics or other serializers' 60-second cadence.
Branch: `../wintap` `grantj-lintap-cpu-observability`.
Implemented: added `FileSerializationIntervalSec` (default `5`) to ETL configuration and used a unit-tested serializer schedule resolver so only `fileserializer` overrides the general interval. Older ETL configs that omit the field default to five seconds. Extended `devtools/file_capture_smoke_test.py` with a post-start FileSerializer-drop log gate and configurable observation window.
Verification: focused `FileOpsAggregatorTests` plus `SerializerScheduleTests` passed (`14/14`); `dotnet build wintap/Lintap.csproj` passed with 0 errors; `python3 -m py_compile devtools/file_capture_smoke_test.py` passed. Host validation remains required after redeploy.

## [2026-08-30] test | FileSerializer five-second redeploy result

Result: deployment logged `fileserializer: serializer flush interval=5s`, and the bounded no-drop smoke passed. The strict prediction did not hold across early live bursts: the log shows cap hits at `18:59:52` (`dropped=1`) and `19:03:12` (`dropped=434`). Five seconds materially reduced loss from the prior run but did not eliminate it. Next slice: schedule a single non-overlapping immediate FileSerializer drain below the 10,000-event cap, retaining the periodic cadence as a backstop; validate it with a controlled high-volume no-drop test before another long capture.

## [2026-08-30] code | FileSerializer high-water burst drain

Prediction recorded before implementation: one immediate non-overlapping drain at a 5,000-event FileSerializer high-water mark leaves 5,000 events of burst headroom below the existing cap, eliminating serializer drops without changing event semantics or idle batching.
Branch: `../wintap` `grantj-lintap-cpu-observability`.
Implemented: added `FileSerializationHighWaterEvents` default `5000`; FileSerializer schedules one worker at threshold, waits behind an active drain if needed, and rechecks state after completion. High-water drains log `trigger=high_water`. The file smoke test now supports `--unique-file-count` for a high-cardinality burst and avoids per-file fsync for that stress mode.
Verification: focused `FileOpsAggregatorTests` plus `SerializerScheduleTests` passed (`18/18`); `dotnet build wintap/Lintap.csproj` passed with 0 errors; `python3 -m py_compile devtools/file_capture_smoke_test.py` passed. Host stress validation remains required after redeploy.

## [2026-08-30] test | FileSerializer high-water stress gate passed

Source: live `spk16` `/var/log/lintap/runtime/Logs/Lintap.log` after the high-water redeploy and controlled `--unique-file-count 6000` smoke.
Result: the log recorded the 5,000-event threshold, 18 high-water requests, and corresponding `trigger=high_water` drains of about 5,000 rows. Drains were normally `2..16 ms` with one `86 ms` outlier, had `skipped_overlap=0`, and left only `2..542` rows queued. No new FileSerializer backlog-cap warning appeared after the smoke marker. The controlled no-drop burst prediction passed; next acceptance gate is a warmed-up unique-run-ID one-hour capture with concurrent log review.

## [2026-08-30] review | Lintap eBPF path, diagnostics, and validation audit

Sources read: `../wintap` Linux subscription, eBPF base/sensor/tracer, EventChannel, Esper, devtools, and tests; Analytics performance-collector CLI and both wrappers.
Pages created: `work/improve-etl-and-qa/ebpf-path-audit-2026-08-30.md`.
Pages updated: `index.md`; `log.md`.
Findings: sensor overlap is mostly intentional layered coverage. Concrete cleanup candidates are mismatched documented sensor toggle names, fallback capability visibility, Network extra-attach cleanup, invalid EventChannel rate accounting, bounded FileOps FD-cache cleanup, ambiguous generic BPF map polling, fidelity snapshots in perf capture, stale OpenAt source, and wrapper PID/ownership/counter inconsistencies. The work note also seeds the later developer, architect, and reviewer documentation set.

## [2026-08-30] analysis | Tenable scan storm overwhelms FileOps sender

Source: `lintap-perf-20260830` parquet plus `/var/log/lintap/runtime/Logs/Lintap.log` during the matching hour.
Pages created: `work/improve-etl-and-qa/tenable-scan-storm-response-2026-08-30.md`.
Pages updated: `index.md`; `log.md`.
Results: FileSerializer remained free of backlog warnings, but FileOps sender depth climbed from about 419k to the 524288 cap and then dropped events continuously. Aggregation cap bypass and summary-enqueue failures appeared at saturation. The storm therefore bottlenecks synchronous FileOps sender/EventChannel/Esper work upstream of serialization. Recommended future slice: an opt-in generic kernel exact-`comm` deny policy with per-rule/per-operation pre-ring suppression counters, preceded by local evidence identifying actual worker names; do not hard-code a Tenable name or infer scanner process-tree membership.

## [2026-08-30] code | Generic kernel FileOps deny policy

Prediction: an empty list changes no behavior; each configured exact raw Linux `comm` policy hit is counted by rule and operation before ring reservation, so it removes selected activity from all downstream capacity domains without claiming to count all vendor filesystem activity.
Branch: `../wintap` `grantj-lintap-cpu-observability`.
Implemented: added empty-by-default `FileOpsDenyComms` / `WINTAP_FILEOPS_DENY_COMMS`, a bounded exact-name parser, CO-RE and tracepoint fallback BPF deny maps and policy-stat maps, post-load map installation with fail-closed startup for a configured-but-uninstallable policy, and periodic policy counter deltas in FileOps logs. Rules are exact/case-sensitive, max 15 UTF-8 names, each max 15 bytes.
Verification: both FileOps BPF tiers compiled through `make build_ebpf`; `dotnet build wintap/Lintap.csproj` passed with 0 errors; focused aggregation/policy/schedule tests passed (`22/22`). No live rule test ran because scanner-exclusive worker names have not yet been established.

## [2026-08-30] evidence | First scanner deny-rule candidate identified

Source: live `spk16` process tree during the active weekly scan.
Result: `nessus-agent-module` runs multiple `tenable-utils-LINUX-x86_64.bin find / ...` workers. Their exact Linux `comm` is `tenable-utils-L` (15 bytes), making it the first defensible policy candidate. Generic helpers (`find`, `rpm`, `sed`, `sh`) remain out of scope. The controlled first rollout is `WINTAP_FILEOPS_DENY_COMMS=tenable-utils-L` with a 10-minute in-scan fidelity check.

## [2026-08-30] test | Tenable worker kernel policy live gate passed

Source: active `spk16` weekly scan and `/var/log/lintap/runtime/Logs/Lintap.log` FileOps summaries.
Result: `WINTAP_FILEOPS_DENY_COMMS=tenable-utils-L` suppressed `dir_open=114102` then `117327` attempts in consecutive 60-second windows. Sender depth was `853` then `192`, with zero sender drops, aggregation cap bypass, and summary enqueue failures. This contrasts with the prior scan's sustained 524288-entry queue saturation. The policy's pre-ring accounting and containment contract is validated for the observed Tenable utility workers.

## [2026-08-30] code | Normalize pidstat CPU naming and documentation

Sources changed: `../Lintap/pidstat-collector.py`; `../Lintap/README.md`; `../Wintappy/wintap_dbt/models/{silver/pidstat_metrics,gold/pidstat_process_summary}.sql`; `../Wintappy/notebooks/wintap_dbt_overview.py`; `../Wintappy/wintap_dbt/README.md`.
Implemented: retained raw `cpu_percent` compatibility, added normalized `cpu_core_percent` and gold core-percent aliases, updated canonical QA labels to `CPU (core-summed %)`, and documented conversion to host-normalized CPU. Created canonical `concept/lintap-cpu-unit-conventions.md`.
Verification: Lintap pidstat collector tests passed (`14/14`); Wintappy dashboard compiled; full Wintappy `make dbt-build` passed (`PASS=78 WARN=0 ERROR=0`).

## [2026-08-30] test | One-hour Tenable-filtered capture

Source: `lintap-perf-20260830-tenable-filter` perf parquet under `dayPK=20260830/hourPK=20` plus matching Lintap log records.
Results: the capture covered `19:13:55Z -> 20:13:54Z` with 714 procfs samples. The policy-enabled pipeline recorded no FileOps sender drops, aggregation cap bypass, summary enqueue failures, or FileSerializer backlog warnings. Runtime CPU averaged `22.4%` host-normalized, about `7.2` core-summed CPUs on the 32-logical-CPU host. Limitation: the latter half overlapped a Wintappy DBT build, increasing FileOps queue depth and CPU/memory, so this is a no-loss policy/stress success rather than a clean performance baseline. Follow-up: run a quiet-host one-hour comparison after scan and analytics activity finish.

## [2026-08-30] analysis | No-Tenable capture reveals persistent FileOps saturation

Source: `lintap-perf-20260830-no-tenable` perf parquet under `dayPK=20260830/hourPK=22` plus `/var/log/lintap/runtime/Logs/Lintap.log` for the matching `14:49:06-15:49:05 PDT` window.
Pages created: `work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30.md`.
Pages updated: `work/improve-etl-and-qa/verification.md`; `work/improve-etl-and-qa/dev_handoff.md`; `work/improve-etl-and-qa/tenable-scan-storm-response-2026-08-30.md`; `index.md`; `log.md`.
Results: all 60 policy summaries reported zero suppression, but FileOps sender depth remained near its 524288 cap and the hour recorded `601126` sender drops plus `192774` summary enqueue failures. FileSerializer stayed healthy (`0` warnings, `26` high-water drains, max remaining `170`, max drain `3 ms`). CPU averaged `30.82%` host-normalized; RSS and anonymous memory were stable within the hour. The filtered run's queue had grown `7860 -> 338592` and first dropped 23 minutes after its capture; queue/RSS correlation during that growth was `r=0.749`. Conclusion: the policy controlled its exact Tenable worker, but the non-policy sender path is not sustainable and another long baseline is blocked pending sender CPU/throughput attribution and a zero-loss low-depth gate.

## [2026-08-30] analysis | FileOps sender and Esper throughput

Sources: `../wintap` FileOps sender, EventChannel, ProcessResolver, PluginManager, File EPL/serializer, NEsper 8.9 threading API, the no-Tenable log window, and new isolated benchmark runs in `diagnostics/nesper-repro`.
Pages created: `work/improve-etl-and-qa/esper-sender-path-analysis-2026-08-30.md`.
Pages updated: `pipeline/nesper-esper-event-stream-processing.md`; `component/fileops-event-pipeline.md`; `work/improve-etl-and-qa/{verification,dev_handoff,implementation_plan}.md`; `index.md`; `log.md`.
Code changed in `../wintap`: added deterministic NEsper throughput/fidelity scenarios; stopped deploying the broad all-event subscriber statement when ETL is enabled but no subscriber plugin exists; corrected nested-enum EPL generation from `.` to `$` without enabling the opt-in rewrite.
Results: production-shaped `file.epl` sustained a median `178756` synthetic events/s with exact count/byte conservation, versus the live sender's implied `194.7/s` ceiling and `118.3` process-cache misses/s. The redundant broad statement reduced isolated throughput to `62785/s`. Outbound threading gave no meaningful gain; context aggregation reduced ingress and failed concurrent-boundary fidelity. Lintap build passed with 0 errors and the default NEsper repro passed all queries. No live redeploy was performed because the low-risk Esper cleanup is not sufficient by itself to resolve the dominant process-resolution bottleneck.

## [2026-08-30] code | Bounded historical process identity cache

Sources changed: `../wintap/wintap/core/infrastructure/{BoundedEventTimeCache,IProcessResolver,ProcessResolver,EventChannel}.cs`; `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`; `../wintap/tests/Wintap.Tests/{BoundedEventTimeCacheTests,ProcessResolverTests}.cs`; `../wintap/diagnostics/nesper-repro/{Program.cs,README.md}`.
Implemented: File-only historical identity resolution now uses a configurable 32,768-entry LRU of closed process intervals before DuckDB; retention seeds entries before deletion and the triggering lookup retries after maintenance. Newest valid create time wins across PID reuse. Event-time and Stop/reconciliation SQL preserves sub-second timestamps. Removed per-query debug logging. FileOps sampled timing now reports atomic average/max totals split into resolve, health, and Esper stages, plus historical-cache counters.
Verification: Lintap build passed with 0 errors; combined cache/resolver/FileOps/policy/serializer tests passed `39/39`; resolver tests include sub-second PID reuse and lookup-triggered retention deletion. Simulated 5 ms miss cost produced about `200/s`, `400/s`, `799/s`, `1995/s`, and `1.06M/s` at 0%, 50%, 75%, 90%, and 100% hits. A 50k-key/32,768-cap run evicted exactly 17,232 entries and stayed bounded. Independent review found no deployment blocker after fixes. Live deployment was not run because noninteractive sudo requires a password.

## [2026-08-30] test | Historical identity-cache ten-minute live gate

Source: operator-deployed `lintap-0.3.4-1.el8.x86_64`, `/var/log/lintap/runtime/Logs/Lintap.log`, and `/var/log/lintap/runtime/esper_staging/fileserializer` on `spk16`.
Deployment verification: installed DLL hash matched the `0.3.4` publish payload (`7bd7ab38...`); PID `3322161` started at `20:54:30 PDT`; startup logged cache capacity `32768`, plugin count zero, and no redundant broad subscriber EPL.
Results: ten FileOps intervals had queue depth `0..1889`, zero sender drops/summary failures/cap bypass/cache evictions, and an `82.7%` historical-cache hit rate (`32700/39537`). Weighted sender latency fell from the prior `5135.7 us` to `449.7 us`; resolution was `445.1 us` and Esper `2.7 us`. FileSerializer drained `221668` rows through 63 flushes with zero warnings/errors and current Parquet output remained readable. Short gate PASS; continue extended monitoring for cache-capacity and rare ~56 ms resolution stalls.

## [2026-08-31] test | Historical identity-cache overnight and recovery gate

Source: uninterrupted `lintap-0.3.4` PID `3322161`, `/var/log/lintap/runtime/Logs/Lintap.log`, readable serializer Parquet, and the existing 6,000-file high-cardinality smoke.
Pages created: `work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31.md`.
Pages updated: `component/process-table-retention.md`; `work/improve-etl-and-qa/{verification,dev_handoff}.md`; `index.md`; `log.md`.
Passive results: 10h23m, 617 FileOps intervals, queue average/max `5205.5/17387`, cache hit rate `75.4%`, 394252 bounded evictions, sender/resolve/Esper averages `560.6/547.1/12.0 us`, and zero sender drops, summary failures, cap bypass, serializer warnings, or send errors. FileSerializer drained 11.2M rows. Controlled result: 6,000-file smoke PASS with all five activities; queue high-water `71802`, next-interval depth below pre-burst, and zero fidelity loss. Limitation: logs/Parquet-only mode supplied no overnight CPU/RSS/GC/FD/map slopes.

## [2026-08-31] backlog | Adaptive FileOps sampling and diagnostic Parquet

Source: operator future-work requests after the historical-cache overnight validation.
Pages created: `work/improve-etl-and-qa/future-adaptive-fileops-and-diagnostics-data.md`.
Pages updated: `work/improve-etl-and-qa/implementation_plan.md`; `index.md`; `log.md`.
Future items: investigate event-rate/type-aware adaptive sampling that preserves representative scan telemetry with weighted count/byte estimates; convert timing, queue, cache, policy, resolver, serializer, and loss diagnostics from log text into first-class partitioned Parquet and DBT data. No implementation decision was made.

## [2026-08-31] backlog | Reusable Marimo performance analysis

Source: operator request while analyzing the retrieved overnight pidstat aggregate.
Pages updated: `work/improve-etl-and-qa/future-adaptive-fileops-and-diagnostics-data.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
Future item: promote the current local-time partition selection, passive/burst phase labeling, pidstat resource trends, FileOps diagnostic alignment, correlations, and recovery metrics into a focused Marimo notebook or a separated section of Wintappy's canonical QA notebook.

## [2026-08-31] analysis | Retrieved overnight pidstat resource trends

Source: `/tmp/spk16-lintap-pidstat-overnight-1m.parquet`, retrieved from S3 using local `dayPK`/`hourPK` pruning and aligned with the overnight Lintap log.
Pages updated: `work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31.md`; `component/fileops-event-pipeline.md`; `work/improve-etl-and-qa/verification.md`; `log.md`.
Results: passive CPU averaged `10.12%` host-normalized and was stable post-warm-up. RSS continued increasing post-22:00 at about `35 MB/hour`, slowing to about `19 MB/hour` over the last four hours. FileOps FD-path entries grew `24 -> 11184` at about `1058/hour`; RSS/entry level correlation was `0.929` overall (`0.938` post-22), while minute-delta correlation was `0.253`. FD-cache cleanup is now the leading residual memory hypothesis. The controlled 6,000-file phase averaged `10.44%` host CPU and did not leave a material RSS step.

## [2026-08-31] closeout | Owning commits anchored and Wintap gates strengthened

Owning commits: `../wintap` `c03d731..2d3f795`; `../Lintap` `1b23f77`; `../Wintappy` `a53cce6..e4b3bc3`.
Wintap cleanup: explicit zero serializer settings now retain inherit/disable semantics, policy counter reporting has an event-independent timer, unresolved historical-cache retries no longer double-count misses, and the high-cardinality smoke requires at least 95% distinct-path coverage.
Verification: Wintap Linux build passed, both BPF tiers built, focused tests passed `41/41`, and the strengthened live smoke captured `6000/6000` distinct paths with open/read/write/close/delete and no serializer loss.

## [2026-08-31] maintenance | ETL/QA documentation current-state cleanup

Pages updated: `work/improve-etl-and-qa/{verification,dev_handoff,implementation_plan,no-tenable-run-analysis-2026-08-30,tenable-scan-storm-response-2026-08-30,esper-sender-path-analysis-2026-08-30,historical-cache-overnight-validation-2026-08-31}.md`; `component/{fileops-event-pipeline,process-table-retention}.md`; `pipeline/nesper-esper-event-stream-processing.md`; `concept/lintap-cpu-unit-conventions.md`; `index.md`; `log.md`.
Summary: removed superseded current-state instructions, separated chronological field results from active gaps, and made partial canonical promotion explicit. Replaced high-confidence `/tmp` and `/var/log` frontmatter anchors with durable wiki/source evidence; retained ephemeral locations only as qualified artifact locators with run IDs, exact windows, commands, and SHA-256 values. Canonical pages now carry explicit pending sibling commit placeholders.
Checks: all 116 wiki Markdown files passed required-frontmatter and wikilink
validation; all changed pages passed `grounded_by` and `source_paths` resolution;
no `/tmp` or `/var/log` frontmatter anchors remain; hash/coverage commands and
`git diff --check` passed. `.nfs` files were excluded. No commit or push performed.

## [2026-08-31] diagnosis+instruction | [wintap] improve-windows-process-collection reboot lineage follow-ups

Recorded the WPC reboot-lineage follow-up thread at a summary level: wpc-11 repaired parent linkage on boot-replay dedup, wpc-12 addressed DuckDB UTC `DateTimeKind` round-trips, and wpc-13 was drafted for sub-second `ResolveProcessAtTime` comparisons. Open state: wpc-13 awaits approval/implementation; expected evidence is a reboot smoke with increased parent-link repair count and one lineage PASS.

## [2026-10-03] feature-open | Debian package refresh (debian-package-refresh)

Source: operator request "I'd like to now have a package for debian", scoped against `../Lintap/packaging/`.
Key finding: Debian packaging already exists (`../Lintap/packaging/lintap-deb/`, the June 2026 original the RPM was derived from) but drifted behind the field-proven RPM builder: pre-two-tier tracer validation (fails cross-builds), stale lintap.env missing the field 0.3.4 sensor block, no MCP publish isolation/--skip-mcp, repo-mount work root. Feature is a parity refresh, not greenfield.
Interview (2 rounds + playback, confirmed): Ubuntu amd64 + arm64 both validated (native arm64 host available); field-parity env with Snappy kept as deliberate divergence (Ubuntu glibc satisfies libnironcompress); MCP matches RPM behavior incl. --skip-mcp; selinux_tracer.bpf.o packaged if built, never required; ldd-verified Depends and upgrade-case maintainer scripts in scope; lintian/changelog/copyright, hardening, apt hosting, extended gates, RPM-builder and ../wintap changes out of scope. Sealed estimates recorded in interview.md.
Pages created: `work/debian-package-refresh/{interview,brief,references,implementation_plan,dev_handoff,verification}.md`.
Pages updated: `index.md`; `log.md`.

## [2026-10-03] implementation | Debian package refresh arm64 slice

Implemented dpr-01 through dpr-04 and dpr-06 on matching branch
`grantj/debian-package-refresh` in `../Lintap`. The Debian builder now uses a
native `/var/tmp` work root, tier-aware eBPF validation, separate MCP publish
with `--skip-mcp` isolation, field-parity environment settings while keeping
Snappy, upgrade-safe maintainer scripts, and ldd-based dependency checks. The
arm64 native fresh publish, package inspection, install/start, upgrade, remove,
purge, and skip-MCP checks passed. Ubuntu 24.04 leaves the optional .NET
diagnostic provider's old `liblttng-ust.so.0` unresolved; this is retained as a
warning and documented in the feature verification. dpr-05 amd64 validation is
next.
Branch: `grantj/debian-package-refresh` created in Wintap-Analytics. Next: dev handoff (dpr-01+dpr-02 first slice) — implementation writes authorized for ../Lintap/packaging/lintap-deb only.

## [2026-10-03] implementation | Debian package refresh amd64 cross-build

No native x86_64 Multipass host is available on the Apple Silicon validation
machine. Ran the authorized cross-build from `lintap-dev` (`aarch64`) for
`amd64/linux-x64`: fresh publish, separate MCP publish, package structure, ELF
architecture, maintainer-script syntax, and tracepoint-only object validation
passed. Artifact `lintap_0.1.0-11_amd64.deb` SHA-256 is
`c4bd44e47a94f12498e95aaa2bac7430750d03303e39e9d842232d025179bcda`.
Native amd64 install/start/upgrade smoke remains pending until an x86_64 host
is available.

## [2026-10-03] verification | Debian package refresh native amd64

Native amd64 validation completed on the UTM Debian 12 VM at `192.168.252.5`.
Fresh revision `12` build and package inspection passed; revision `13` was
installed over it with the service remaining enabled and active. The service
produced readable parquet output (105 rows across host and macip files).
Remove preserved data and the conffile; purge removed `/etc/lintap` while
preserving the data marker. Revision `12` SHA-256:
`dccc2f923b3b5f0a9fe300dc67c86b15c965d1bd608cc96534401e4ad12974f9`.
Revision `13` SHA-256:
`497d5ee0aa7720118b8c84db0c808661b5b693237bdd0bc38bcacb0d4a199df9`.
The UTM Debian host required `CPATH=/usr/include/x86_64-linux-gnu` for the
multiarch eBPF headers; no source change was made for that environment issue.

## [2026-10-03] verification | lintap-dev live sensor smoke tests

Ran the available live integration tests against the running arm64 sensor on
`lintap-dev` using `/var/log/lintap`: process creation/tree, file activity, and
network activity. All passed. Process coverage included `fork_exec`,
`posix_spawn`, and `execveat_fexecve` with valid parent linkage and hashes; file
coverage captured open/read/write/close/delete; network coverage captured three
rounds of HTTP/HTTPS and UDP traffic with TCP 443 and UDP 53 parquet rows.
SELinux was not tested because the VM has no SELinux filesystem, tools, or
policy packages installed.

## [2026-10-03] release-prep | Debian artifacts rebuilt; RPM stale blocker recorded

Rebuilt Debian arm64 and amd64 artifacts at application version `0.1.0`,
revision `14`: arm64 SHA-256
`c26c48290997a4120a18b227913722b22d288386b8abafd23c02df915325e961`; amd64
SHA-256 `ea2f2659736a1f81d97ee2780315d8033ae4dcdeb7ae835f0c0bc382da8eaa2f`.
The latest RPM remains `0.1.0-3.el8`, built 2026-06-18, SHA-256
`38bfecbad374b2ecc8dc0f9b85cfd50eaaa3c7936aca61b18055ef0b0dd1657f`.
Attempting a fresh RPM build on the arm64 Multipass host stopped at the RPM
builder's obsolete `file_ops_tracer.bpf.o` assertion; no RPM builder changes
were made because that path is outside the authorized feature scope.

## [2026-10-05] documentation | Release README draft for package assets

Created `work/debian-package-refresh/release-README.md` for the proposed RPM
`lintap-0.3.5-12.el8.x86_64.rpm` and Debian `0.1.0-14` amd64/arm64 assets. The
draft documents the mixed package versions explicitly, installation and
service commands, runtime layout, upgrade/removal behavior, Snappy divergence,
and the required `SHA256SUMS` release companion. The final RPM checksum was
verified from `~/Downloads` and added to the README.

## [2026-10-05] closeout | Debian package refresh

Closed dpr-01 through dpr-07. Promoted the Debian package-builder contract and
compression divergence to `repo/lintap-supporting-repo.md`; finalized
verification, release README, and missing-data metrics artifacts; and updated
the index. Native arm64 and amd64 Debian validation passed. RPM builder parity
remains explicitly out of scope and the published RPM is documented as an
independently versioned release asset.

## [2026-10-05] closeout | Pull requests opened

Implementation PR: https://github.com/llnl/Lintap/pull/6
Analytics/wiki closeout PR: https://github.com/llnl/Wintap-Analytics/pull/24

## [2026-10-12] future-work | Privileged eBPF helper boundary

Source: `../Lintap` packaging units, packaging review, and README.
Pages created: `wiki/work/privileged-ebpf-helper/future-privileged-ebpf-helper-boundary.md`.
Pages updated: `wiki/index.md`.
Summary: recorded a speculative least-privilege deployment pattern that moves
eBPF loading and BPF-object ownership into a privileged helper while running
the .NET processing service as a dedicated non-root user over a protected
Unix-domain socket. Captured capability, systemd hardening, IPC, migration,
and validation questions; current root-service behavior remains grounded in
Lintap packaging sources.
Contradictions flagged: none.

## [2026-10-15] feature-open | Refactor file system data and log paths (refactor-data-log-paths)

Source: operator request via the LLM-assisted feature workflow invocation.
Grounding: Env.cs/ConfigManager root resolution, ETL Paths.cs derivations,
WintapLogger/ProcessResolver/EventChannel/controllers runtime paths, the
hardcoded `/var/log/lintap/runtime/diag` literal in NetworkSensor.cs, Lintap deb/rpm
packaging (`WINTAP_DATA_ROOT=/var/log/lintap`), and the pidstat collector
spool.
Interview (4 rounds + playback, confirmed): split the single mixed root into a
shared archivable `data` tree (today's parquet event tables; the mountable
piece for axon-aegis-micro-range multi-VM shared storage) and a host-only
`runtime` tree (logs, duckdb event store, csv, recordings, spool, diag,
workbench state, ai). Two independent roots: `WINTAP_DATA_ROOT` repurposed to
mean the data tree; new `WINTAP_RUNTIME_ROOT`. FHS-style sibling defaults under
the per-OS app root. Cross-platform code scope; Linux-gated acceptance (package
smoke, two-instance shared-mount simulation, Wintappy DBT run). Constraints:
raw_sensor internals and leaf naming frozen; no auto-migration (wpc-09
precedent). Hostname layer for cross-VM runtime visibility is a mount-time
convention (`<shared>/hosts/<hostname>/`), not sensor code. Partially
supersedes decision/platform-runtime-data-root-defaults at close-out. Sealed
estimates supplied shortly after interview close and recorded verbatim in the
sealed section of interview.md (values not repeated here — sealed until
close-out).
Pages created: `work/refactor-data-log-paths/{interview,brief,references}.md`.
Pages updated: `index.md`; `log.md`.
Contradictions flagged: none.

## [2026-10-15] planning | refactor-data-log-paths design, plan, and dev handoff

Source: continued feature planning on branch `grantj/refactor-data-log-paths`
(created this session), plus design-time scans of ../Wintappy and Analytics
tooling for path couplings.
Key design choices: the repurposed data root directly contains `raw_sensor/`
(no `parquet/` level — keeping it was explicitly rejected; only a human can
un-reject); runtime tree keeps existing child names under a new parent; single
derivation point per tree in Paths.cs with grep gates; Wintappy tracks via one
Makefile default change (`WINTAP_DBT_DATASET` drops `/parquet`) since DBT
macros funnel through `raw_sensor_dataset_path()`; pidstat collector spool
moves to the runtime root. Design-time scan found no hardcoded path couplings
in Analytics streamlit/notebooks (dev agent re-verifies).
Plan: eight rdp-NN slices — two-root core (rdp-01) and consumer moves
(rdp-02) gated before packaging (rdp-03), Wintappy tracking (rdp-04), then
the three acceptance gates (rdp-05..07) and closeout (rdp-08).
Handoff: authorizes ../wintap, ../Lintap packaging+collector, ../Wintappy;
first slice rdp-01+rdp-02; interview.md sealed-section warning included;
micro-range layout conflicts escalate to the human. Implementation moves to
an environment containing ../axon-aegis-micro-range.
Pages created: `work/refactor-data-log-paths/{design,implementation_plan,dev_handoff}.md`.
Pages updated: `work/refactor-data-log-paths/interview.md` (sealed estimates
recorded); `index.md`; `log.md`.

## [2026-10-19] review | refactor-data-log-paths closeout preparation

Source: final implementation review across `../wintap`, `../Lintap-rdp`, and
`../Wintappy`, plus the disposable `lintap-dev` package host.

Confirmed: two-root resolution and focused tests, Debian arm64 fresh package
event-output smoke, runtime/data filesystem boundary, manual test-host cleanup,
and Wintappy `make dbt-build` against six fresh files under a direct data root.
Promoted the durable split-root decision and updated upload/cache, Lintap, and
Wintappy canonical pages. Added a deliberately manual cleanup utility for
disposable test hosts; package install and runtime still do not migrate or
delete data.

Open validation: the two-instance shared-mount simulation is not claimed, and
RPM runtime smoke remains unavailable without an EL8/RPM host. The feature is
therefore prepared for closure but remains open until the shared-mount gate is
performed or explicitly waived.

Pages created: `decision/separate-data-and-runtime-roots.md`.
Pages updated: `decision/platform-runtime-data-root-defaults.md`,
`component/sensor-upload-cache-pipeline.md`,
`repo/{lintap-supporting-repo,wintappy-pipeline-repo}.md`,
`work/refactor-data-log-paths/{implementation_plan,verification}.md`,
`index.md`, `log.md`.
Contradictions flagged: none.
Contradictions flagged: none.
## [2026-10-19] documentation | Sanitized Windows attribution validation executive summary

Architect requested preservation of the reviewed developer-archive summary without source references because the original archives are intended for deletion. Created [[wiki/diagnostic/windows-attribution-validation-executive-summary]] and updated the index. The nine-paragraph historical record preserves architecture, reported test counts, attribution metrics, negative/inconclusive outcomes, and evidence limitations while omitting machine-specific identifiers and source locators. Confidence is low because source references are intentionally not retained; no tests were rerun and no current implementation signoff is implied.

Open questions: sustained Registry attribution, validator cleanup reliability, the full 24-hour acceptance gate, and finalized-Parquet linkage verification remain unresolved in the reviewed evidence. No new architecture decision was made. No original archive, source code, or test file was modified or deleted; no commit or push performed.

## [2026-10-19] documentation | Preserve attribution and FILE-path correctness contracts

Created [[wiki/concept/windows-attribution-and-file-path-correctness-contracts]] at the Architect's request and added it to the index. Retained only technical predicates, compatibility boundaries, tradeoffs, regression expectations, and open validation work; separated accepted contracts, reported implementation, and unverified approved design. Original source references and machine-specific observations are omitted. No new architecture decisions, source/test changes, archive deletions, commits, or pushes. Open validation gaps remain as recorded in the companion executive summary.

## [2026-10-21] verification | improve-lintap-data-quality long isolated captures

The recorded DBT snapshots for acceptance4 and acceptance5 have zero PID-hash
orphans and `Unknown` names across file and network relations; their explicit
file workloads also pass. The controlled acceptance6 workload remains clean and
observes `ubuntu`/`nobody` Start users, but a final rebuild after service stop
found a 20-second system-workload lifecycle gap: 21,571 file and 12 network
orphan rows have stable child identities but no matching process row. Its
FileSerializer also reports 32,496 in-memory drops, although FileOps reports
zero sender-queue and ring-reservation drops. Thus no full-capture acceptance
claim is made. The focused restored xUnit suite passed 348/348. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-22] code | Named cross-domain field stimulus and Ubuntu package result

Added Wintap Python stdlib workload with named process families, current Linux
FileOps and TCP/UDP stimuli, per-run operation/PID/path/port manifest, explicit
skips/failures and optional native clone/clone3/vfork probes. Two Linux regressions
pass; Ubuntu arm64 default/IPv6/native stimulus runs complete. Documentation
separates generated activity from proven capture and marks mmap-as-Read,
rename/truncate and IPv6 limits. Added tool page, README and RHEL handoff link.
Debian revision 104 normal ETL acceptance completed: 80 baseline/400 churn births,
zero thread Starts/wrong worker parents/identity splits; HOST/restart/opt-out pass.
Counter/overhead review and RHEL remain open. No commits or pushes.

## [2026-10-22] code | Smoke results app and portable cross-host run manifests

User requested per-test Streamlit sections/commands/queries/run grouping and
explicitly allowed smoke-script updates, no legacy-data support. Analytics app
uses independent raw-parquet and portable manifest/upload sources; Wintap scripts
emit UUID/test-host/time/PID/path/endpoint envelopes including failed validation.
Queries normalize ETL/direct schemas/time scales, require host attribution and do
not merge repeated runs by process names. Empty UI and run-isolation/query tests
pass; Linux manifest/workload and actual-object Clone checks pass. Fresh packaged
VM→Mac integration collecting; durable app/tool and work records created. No DBT
state/data modified, no commits/pushes, unrelated dirty files preserved.

## [2026-10-22] verification | Smoke dashboard VM-to-Mac integration

Transferred packaged normal-ETL raw parquet and independent portable manifests
from Ubuntu arm64 Multipass to approved Mac temp storage. App queries 33 files
without errors, renders 36 tables and isolates two repeated runs. Second run
captures process lifecycle/five file activities/client TCP and UDP activity;
server TCP Accept and UDP Receive are absent and displayed as gaps. First run
occurred before sensor readiness and remains empty rather than borrowing data.
Final 11 app/query tests pass; Linux manifest/workload tests pass; diff checks
clean. No full network acceptance claimed. Service stopped; docs and work checklist
updated, no commits/pushes.

## [2026-10-22] plan | Durable smoke evidence and dashboard triage

Investigated live CacheManager/uploader, pidstat producer and Wintappy partition
precedents. Proposed raw_smoke_test typed parquet envelopes with manifest JSON,
immutable run revisions, runtime spool, UTC publication partitions and dataset
auto-discovery. Flagged startup raw-parquet deletion with enabled uploaders,
any-success multi-adapter deletion, partial file-share copy, cache pruning and
default-disabled transport as deployment gates. Proposed red/yellow/green plus
gray summary preserving harness/coverage/arrival distinctions; no green from
stimulus alone or red missing-data from a mere wait timeout. Saved plan and index;
no source/app/DBT or configuration changes, no transport setup/tests performed.

## [2026-10-22] code | Durable smoke parquet and dashboard triage

User accepted normal destination latency/source deletion and authorized coding.
Wintap shared smoke wrapper now optionally exports atomic immutable parquet
snapshots (typed metadata/full JSON/hash) into raw_smoke_test UTC partitions.
Analytics auto-discovers/deduplicates runs and adds host/test severity counts,
history/attention filters and section navigation with bounded event detail reads.
Pending/missing/stimulus-only/limited/ambiguous evidence stays yellow; thread,
identity and explicit parent violations surface. 19 app/query tests, four producer
tests and two Linux workload tests pass. Mounted VM→Mac live capture: 23 telemetry
and six evidence parquet, two isolated runs, no separate manifest transfer/errors.
Known server TCP Accept/UDP Receive gaps remain yellow. Updated canonical tool,
plan/checklist and verification. No uploader hardening, DBT, package rebuild,
commits or pushes; unrelated changes preserved.

## [2026-10-23] feature | Linux capability smoke triage retrospective and commits

User confirmed the cross-repo umbrella feature and authorized commits/PR appendices
on existing feature/improve-lintap-data-quality branches. Reconstructed brief,
interview, design, references, implementation/verification and PR summaries under
wiki/work/linux-capability-smoke-triage; linked existing detailed evidence instead
of duplicating it. No prospective metrics invented. HOST property retained;
user-discarded RawSensorWriter mixed-schema branch is not part of committed scope.
Fresh checks: 127 .NET, 19 dashboard/query, four manifest and two Linux workload
tests pass; both package builders pass bash syntax checks. Wintap commit 859a47b;
Lintap commit cfc3f35; Analytics dashboard/wiki/artifacts committed together.
Wintappy has no tracked change/commit. No pushes/branch changes; local state,
generated data, FUSE/editor artifacts and unrelated experiments remain excluded.
RHEL acceptance, isolated Clone overhead review and server-network gaps stay open.

## [2026-10-23] maintenance | Resolve Analytics PR merge conflicts

Merged origin/main into feature/improve-lintap-data-quality at the user's request.
Resolved wiki/index.md and wiki/log.md by retaining both the capability/smoke
feature records and main's AgentId/TCP investigation records; refreshed the index
date. Verified no unmerged paths or conflict markers, clean staged whitespace,
and preservation of both parents' wiki log entries and index links. Documentation
only; source tests not rerun. Unrelated .claude/ files remain untouched.

## [2026-10-23] code | Smoke dashboard PR review correctness fixes

Preserved red failure/observed-violation severity when overlapping runs add an
ambiguity warning. Validated selector objects and supported domains at manifest
ingestion, rejecting null/non-object entries without aborting valid-run rendering;
empty lifecycle selectors remain valid. Added overlap, malformed-input isolation,
and Streamlit rendering regressions. All 23 dashboard/query tests pass in the
isolated venv. Updated canonical dashboard semantics and umbrella plan/verification.
Packaging README review is separate; unrelated local files remain untouched.

## [2026-10-23] environment | .NET 10 SDK on lintap-dev

For the Wintap `chore/net10-dependency-prune` upgrade, installed Ubuntu's
`dotnet-sdk-10.0` on the existing Ubuntu 24.04 arm64 Multipass `lintap-dev`:
`multipass exec lintap-dev -- sudo apt-get update`, then
`multipass exec lintap-dev -- sudo apt-get install -y dotnet-sdk-10.0`.
Verified SDK 10.0.113, runtime/ASP.NET Core 10.0.13, clean `apt-get check`, and
a temporary Release `net10.0` console build/run (`Hello, World!`). SDK 8.0.132
and runtimes 8.0.32 remain installed; the shared dotnet host package is now 10.
No Lintap source/build/packaging changes or branch switches performed yet.

## [2026-10-23] environment | Match pinned SDK and compile Lintap

Reproduced repository build failure: `../wintap/global.json` pins SDK 10.0.402
with `latestPatch`, rejecting Ubuntu's 10.0.113 feature band. Installed Microsoft's
10.0.402 linux-arm64 archive (SHA-512 verified against release metadata) into
`/opt/dotnet-10.0.402` on `lintap-dev`; `/usr/local/bin/dotnet` now points to its
host, leaving apt-managed installations intact. Fresh shell selects 10.0.402.
From `/home/ubuntu/git/wintap/wintap`, `dotnet build Lintap.csproj -c Release
-r linux-arm64` passes: 179 warnings, zero errors, output
`bin/Release/net10.0/linux-arm64/Lintap.dll`. Restore left shared WintapAPI and
MCP server package lockfiles modified; no manual source edits or reversions.
The earlier standalone console smoke did not validate the repository SDK pin.

## [2026-10-23] verification | .NET 10 Debian package on mounted lintap-dev

Installed user-supplied arm64 `lintap_0.1.0-1_arm64.deb` (bundled runtime 10.0.13),
configured fresh mounted data root `net10-package-20261023T220407Z` under
`/home/ubuntu/data/lintap` (Mac `/Users/johnson30/data/lintap`), native runtime,
and 10/15-second serialization/merge. Process Stop/20-child attribution, 100-file
five-activity/no-drop, and outbound TCP/UDP smokes PASS; named/native stimulus
completes. Mac discovers four runs via 12 evidence parquet; Streamlit renders
49 tables without errors, 3 green/1 yellow/4 gray. Named server TCP Accept/UDP
Receive still absent; partial arm64 FileOps legacy hooks, unavailable SELinux,
and unresolved disabled SignedS3UrlAdapter documented. Service left running;
pidstat/DBT/shutdown/long-run gates not tested. Record/index updated; no source
or packaging edits, deletions, branch switches, commits or pushes.

## [2026-10-23] verification-start | .NET 10 packaged 30-minute soak

User authorized 30 minutes on the existing running lintap-dev package/mounted
dataset. Started native runner in background, five six-minute-spaced rounds of
network, process Stop/20 children, 1,000-file/no-serializer-drop, and named/native
clone smokes, with 30-second service/RSS/CPU sampling and baseline-relative log
loss checks. Each test publishes dashboard evidence to the same mounted root.
Service/configuration unchanged; no source edits. Pending completion, not PASS;
details in wiki/work/net10-dependency-prune/verification.md.

## [2026-10-23] verification | .NET 10 packaged 30-minute soak PASS

Completed exactly 1800 seconds (22:31:44–23:01:44 UTC): all 20 runs exit 0;
5,000/5,000 unique workload file paths retained across five rounds/all activities.
PID unchanged, zero restarts/disruptions, all observed serializer drop totals zero,
no new log errors/loss signals. RSS 507.7→532.7 MiB (range 498.7–569.9), sampled
core-summed CPU 2.92%; diagnostic only, no long-run leak/baseline claim. Mac reads
24 runs/72 evidence parquet with zero query errors; 15 soak validators green,
five named workloads yellow for existing server-network gaps/stimulus-only scope.
Service left running. Verification/index updated; DBT/pidstat/shutdown/other
platform gates remain unrun, no source or package changes/commits/pushes.

## [2026-10-23] code | Shared network endpoint normalization and name-contract regressions

User authorized Wintap/Wintappy fixes plus regression guards, then added same-host
separate-PID and single-process socket ends over a non-loopback interface. Replaced
stale slash-name inbound matching with typed classification, preserved directed
ports in parquet, normalized canonical/legacy SQL counters, added DBT vocabulary
gate and literal audit (broader audit separately flags uppercase STOP comparison).
Normal ETL network smokes now confirm endpoints by default; standalone endpoint
manifest and independent dashboard role/provenance/hash checks added. 26 actual
Windows-targeted .NET tests on Ubuntu, 74 SQL, 8 workload/oracle, 7 audit and 26
dashboard tests pass. Isolated source capture (Oct 24 UTC/Oct 23 local) passes both
corner cases and Mac is green; installed PID/restarts unchanged. Existing DB read
only; original package not replaced, no Windows live/full-network acceptance or
historical repair claim. New work plan/verification and network/dashboard pages
updated. No branch switches, commits/pushes; unrelated dirty work preserved.

Final focused counts after numeric/comma-name rejection and explicit-smoke-opt-out
tests: 28 .NET, 74 SQL, 10 endpoint/workload, 7 audit, 27 dashboard; all pass.

## [2026-10-23] documentation | Foundational identities and cross-host metadata findings

Added high-level agent_id/pid_hash/conn_id versus endpoint-orientation concept,
prominently linked from index and process/network pages. Full canonical tuple
identity is directionless and not socket-lifetime identity; directed ports remain
necessary to validate same-IP/same-PID normalization. Read-only supplied database
confirms AXON-TARGET/CALDERA-HOST share UUID fc3e4c62-eddf-42d0-9ab4-830773b61f6f,
also present in local initialized state (committed template empty). Copied-state
deployment is plausible, not verified; documented persistence/clone boundary and
future pid_hash impact of rotation. Confirmed Wintappy's four silver/legacy Windows
labels and sensor registry-only OS-name fallback; recorded platform-derived metadata
and cross-host regression proposals. Linked previous AgentId verification with an
explicit scope follow-up. Source, runtime state, services and database untouched.

## [2026-10-23] decision | Process hash excludes AgentId and has one formula definition

User clarified intended pid_hash inputs: hostname, PID and canonical process-start
time only, excluding agent_id, with a single calculation definition across the
entire codebase. Recorded accepted ADR and corrected concept/process/diagnostic
wording to distinguish intended contract from current code. Live source still
includes AgentId and has a second ProcessHash implementation in the separate Windows
WintapCoreSvcMgr project; multiple shared-helper callers are not duplication.
Linked prior process-identity ADR without changing its other decisions. Formula
consolidation, agent-independent regressions and historical/cache migration remain
implementation work; no code, state, service or dataset changes made.

## [2026-10-23] patch | Agent-independent process hash and host-bound AgentId

User authorized source patch for both identity defects. Added one ProcessIdentity
formula (hostname/PID/canonical UTC FILETIME only), source-linked Windows helper,
regressions, explicit unknown instead of event/Stop-time hash fallbacks, and
versioned process-store isolation preserving legacy files. AgentIdentity persists
runtime-root UUID with host binding, reissues legacy/differently bound copied state
once, locks/atomically writes and fails visibly; common publish uses empty template.
148 real-project focused tests pass on Ubuntu, Linux/Windows sensor/helper builds
pass. Two isolated live endpoint captures pass before/after restart, replace seeded
duplicate UUID once, preserve legacy input and retain the new UUID; Mac independently
reads two green runs and verifies six raw process vectors/zero unmatched workload
network hashes. Installed service unchanged (PID 17138/restarts 0); affected hosts,
original DB and history not migrated. Windows-live/package rollout/soak, fully
identical-clone diagnostics and OS-family fix remain separate. Plan/verification,
identity/process/diagnostic pages, accepted ADR and index updated; ADR patch-review
marker retained for deployment details. No commits/pushes or unrelated reversions.

## [2026-10-23] diagnostic | Supplied database runtime-attribution audit

Read-only attached DB/in-memory snapshots, 98 recorded checks including canonical
orphan/PK SQL and 38 schema equivalents (all zero schema failures). Found 89,325
silver file orphan rows/80,683 hashes, 8,068 Stop-only identities, 5,507 missing
parent entities. Exact historical preimage checks identify 80,409 unknown file
hashes using FirstSeen and 8,042 Stops using exit EventTime; PID 16464 produces
11,763 hashes in 0.574s. Unknown-3 confined to six older Oct 19 observations/four
hashes; historical source ties it to failed username enrichment. Also 757 gold
extra rows, zero gold file counters, all 7,557 basic network counters NULL, wrong
duration rows, receive-buffer byte semantics, partial tuples/path/metadata gaps.
Backlog/short-lived proc race is a theory, not proven loss: no logs/receipts and
process ReceiveTime=0. Current Linux ExitSensor still has an exit-time fallback;
added explicit acceptance gap to identity verification/plan without undoing passed
formula/state work. Diagnostic/script/full JSON/index and related diagnostic updated.
Database size/mtime unchanged; no source, installed service, state, or history
modification, commits/pushes, or unrelated-work reversion.

Hard contradiction flagged on the identity concept and new diagnostic: blanket
unknown-sentinel implementation wording versus residual Linux ExitSensor exit-time
fallback. Both set human-review-required; further semantic promotion paused pending
review. Passed core/Windows/state tests are preserved, not treated as all-producer
runtime acceptance.

## [2026-10-23] plan | Attribution recovery and runtime short-lived classification

Created proposed strategic/tactical plan under host-process-identity-patch: early
kernel lifecycle evidence, explicit unresolved attribution, reason-split diagnostics,
producer safeguards/SQL corrections, shadow-mode versioned role/lifetime classification,
network measurement/path/metadata work, and packaged canary/restart/burst/soak gates.
Short-lived confirmed at exit from authoritative birth; role provisional at fork/exec,
missing-birth lifetime unknown. Proposes <=1s experiment with duration bins, not accepted
semantics; preserves raw capture and bounded post-exit identity retention. Current
retry queue/exit ABI reviewed; historical Windows name map not treated as a Linux
runtime classifier. Implementation plan/index linked. Planning only: no code, schema,
service, state, supplied-DB or deployment changes; existing semantic review flags held.

## [2026-10-23] experiment | Short-lived attribution baseline and candidate recovery

User approved multi-round experiments with real-sample comparison. Added candidate
Exit kernel boottime/monotonic start evidence, legacy/extended ABI validation and
explicit unknown instead of exit-time hash; bounded exit-only lifetime/weak-role
shadow JSONL. Wintappy fixes file spelling/Open counters, file/network lifetime-only
grouping, full elapsed duration and gold uniqueness tests. 153 focused .NET and 82
SQL tests pass; Linux/eBPF builds pass. Actual in-memory sample SQL restores all
728,701 file events, removes 757 extra rows from both gold summaries, fixes 195
duration errors and 7,557 all-NULL network counters; 89,325 historical file orphans
remain visible, original DB size/mtime unchanged.

Initial six live rounds reproduce 9,741 file FirstSeen hashes and 32 exit-time hashes
in old package with disabled births; normal old package splits one Start/Stop too.
Candidate normal/burst/restart retain every expected path/event and canonical hash;
210 lifetime classifications match independent proc/kernel duration evidence.
Three longer-settling/legacy-ABI controls confirm absent kernel start yields unknown
lifetime/identity, not fabrication; 75s settling still loses events despite zero
reported ring/sender/serializer drops. Two opt-in post-producer-stop Esper batch-wait
rounds restore all paths/events; first injected round exceeds harness shutdown
deadline, retained as failed graceful-stop gate. Final same-binary barrier-off/on
pair with 120s observation deadline is pending, not retrospectively certified.

Experiment report/JSON/analysis scripts, implementation/verification/plan, diagnostics,
identity concept, pipeline repo page and index updated. Installed service remains
PID 17138/restarts 0. No rollout, historical repair, branch switch, commit/push or
unrelated-work reversal. Execve/Rundown input guards, full birth/role/retention
recovery, permanent shutdown API, network measurement/OS/path fixes and package
release gates remain open; identity review markers preserved.

## [2026-10-23] verification | Final attribution shutdown-drain A/B

Completed thirteen total isolated rounds. Final same-DLL/exit-object, births-disabled
pair uses 30s workload settling and 120s shutdown observation; both exit 0 without
harness interruption. Barrier off retains 1,975/2,088 paths and 13,369/14,616 payload
events; post-producer-stop 11s Esper wait retains all paths/events. Both export 42/42
canonical Stops, exact lifetime bins and only canonical-or-explicit-unknown file
identities. Barrier-on still has 9,984 unresolved file rows: conservation is corrected,
missing-birth attribution is not. Earlier forced-deadline round preserved as failed.
Source evidence supports pending batch loss missed by zero serializer-drop counters;
experimental flag stays opt-in, permanent drain API/platform/budget acceptance pending.
Final JSON/report/implementation/verification/index and devtools documentation updated.
Installed service PID 17138/restarts 0 and supplied DB unchanged; no rollout/commit/
push or unrelated-work reversal. Final focused regression remains 153 .NET/82 SQL.

## [2026-10-23] experiment | Original-host installed-package acceptance

User approved axon-target/caldera-host candidate installation/service/mount changes.
Both initially had no package/running service. Fresh native-copy self-contained
.NET 10.0.402 arm64 package installed on both; lintap-dev service unchanged.
Initial harness failed: EnvironmentFile precedence ignored isolation assignments,
adding new raw output to default shared data and using existing mounted runtime;
SIGINT ended processes without graceful shutdown despite systemd Result=success.
Evidence retained, database unchanged; runtime logs are not historical provenance.
Corrected later EnvironmentFile/SIGTERM/effective-process-environment assertion;
launched default/drain/burst/restart plus TCP endpoint suite in fresh native and
per-host mounted roots. Independent results pending. Added scripts/results/checkpoint,
index and plan approval scope. No production rollout/history repair/commits/pushes.

## [2026-10-23] verification | Installed original-host workload gates and shutdown gap

Corrected eight installed-package rounds pass independently on Mac: 20,880 paths,
146,160 payload events, 840 canonical process/91,487 canonical file observations,
420 lifetime oracles, 16 separate/same-process TCP endpoint cases; persistent
distinct AgentIds and eight graceful stops without restarts. Original DB unchanged.
Whole-capture inspection finds CALDERA shutdown-only cron PIDs with 119 unresolved
file rows/242 events and two known-hash orphan rows: lifecycle stopped before
FileOps and retry admission closed early. AXON's 15 unknown-named background rows
retain linked identities and exec metadata transitions; not attribution failures.
Added exact anomaly JSON and retained all evidence. Linux-only candidate stops
dependent producers before lifecycle and flushes retries afterward; other-platform
timing unchanged. Revision-2 native build/179 focused .NET tests pass. Revision-1
dual monitored 30-minute package soaks and six isolated revision-2 shutdown A/B
rounds underway; no mid-soak replacement, service change on lintap-dev, historical
repair, production rollout, commits or pushes. Plan/verification/results/index updated.

## [2026-10-23] experiment | Shutdown-order A/B exposes canonical Clone birth defect

Six isolated shutdown-window rounds exit cleanly; lintap-dev installed service
unchanged. Baseline reproduces 1,379/0/1,448 known-hash orphan rows and 755/18/906
unresolved rows. Ordered candidate has zero orphan/unresolved rows in all three,
but fails 33 file/six process canonical vectors in round 1: three Clone births
use fork occurrence 10ms later than independent task birth, and Exit inherits
that history hash. Revision 2 remains failed rather than weakening the oracle.
Revision 3 extends Clone CO-RE 48-byte prefix to 56 with task start_boottime,
checks ABI sizes, prefers kernel birth and uses explicit unknown for legacy
missing-proc birth instead of fork/callback hash. New regressions and native
build underway. Original-host revision-1 soaks remain frozen/running; historical
DB and failed evidence preserved. Results/verification/plan updated; remaining
Execve/Rundown and platform/drain acceptance still open.

## [2026-10-23] verification | Revision-3 shutdown-order and canonical Clone birth

Fresh native package build/181 focused .NET tests pass. Repeated six-round A/B
passes all three revision-3 isolated captures: 6,216 file/1,171 process vectors
independently canonical; zero controlled unresolved or known-hash orphan rows;
489 controlled PIDs have captured activity after SIGTERM, verified logged stop
order and all exits graceful. Baseline still fails all three with 16/39/28
unresolved rows; third baseline reproduces another one-tick Clone birth mismatch.
Variable cutoff excludes post-collection conservation claims. All failed earlier
evidence retained and lintap-dev installed service unchanged. Original-host
revision-1 soaks remain frozen; revision-3 self-contained/SIGTERM missing-birth
and legacy-no-start negative controls underway. Results/verification/plan/index
updated; no historical repair, production rollout, commits/pushes. This isolated
regression pass does not establish general missing-birth or installed release QA.

## [2026-10-23] failure | Revision-3 missing-birth backlog and remote-shell incident

Missing-birth control exceeds 120s shutdown budget, escalates to SIGKILL; legacy
negative never runs. Independent Mac analysis preserves 774/2,088 paths and
4,398/14,616 payload events, 3,571 explicitly unresolved file rows, 42 canonical
Stops, no fabricated timestamp hashes. Truncated sidecar/no summary explicitly
fails a new completeness gate; raw evidence unchanged. Stop hangs at FileOps
sender join with measured slow miss-heavy backlog, not a proven deadlock. Failed
capture archived separately; release/attribution/conservation gates remain open.
During later log search, Multipass shell quoting reconstructed regex as pipeline
and accidentally invoked shutdown on lintap-dev. Cancellation failed; non-forced
VM stop/start restores SSH and original installed service (PID 701/restarts 0).
Service-unchanged earlier A/B claims are scoped before this incident; failed
negative predates it. Original AXON/CALDERA soak PIDs remain 6579/12926, zero
restarts. No files/evidence deleted. Complex remote searches now use scripts or
local archive reads. Results/verification/plan/index updated, no rollout/history
repair/commits/pushes. Revision 3 cannot be accepted generally from normal-birth passes.

## [2026-10-23] verification | Dual installed 30-minute soaks pass; revision-3 host follow-up

Independent Mac analysis passes revision-1 original-host soaks: 1,800s/host,
83,520 paths/584,640 payload events conserved; 369,419 file/3,360 process vectors
canonical; 1,680 lifetime/start/class checks, 20 bidirectional endpoint cases,
375 monitor samples/host, stable distinct agents and zero restarts. Whole-capture
204,094/207,699 file rows contain zero unresolved/known-hash orphan rows; 16/245
unknown-named but linked rows visible. Graceful stops 30.87s/51.37s; original DB
unchanged, remote upload and resource budgets not certified. Archives/native QA
preserved. After completion/archival, experimental revision 3 installed on only
AXON/CALDERA; fresh four-round default/drain/burst/restart and TCP suites underway,
actual-service shutdown-window rounds planned afterward. Missing-birth failure
and release/drain/recovery gates remain open; no production rollout/history repair,
commits/pushes or evidence deletion. Results/plan/verification/index updated.

## [2026-10-23] failure | Installed revision-3 conservation and endpoint gaps

Eight revision-3 installed rounds complete gracefully/no restarts with 840 canonical
process/90,568 canonical file vectors, no whole-capture unresolved/known-hash orphan
file rows, persistent distinct agents. Five pass all gates, three fail conservation:
AXON default loses 29 paths/444 events; CALDERA default 138/1,110; CALDERA drain-on
316/2,553. Exact deficient path oracle records all losses in burst cohort. CALDERA
default separate-process endpoint case entirely absent (not reversed tuples).
AXON serializer/final-merge complete/zero-drop receipts miss upstream loss;
CALDERA sampled delivery delay is ~25–26s mean/~45s max. Counter interval versus
cumulative bases preclude one-snapshot producer loss subtraction. Fixed 11s wait
is not sufficient drain assurance. Captures/full JSON/loss details retained; actual-
service three-round shutdown-window identity suites now running on both approved
hosts, not used to close conservation/missing-birth/release failures. DB unchanged;
no production rollout/history repair/commits/pushes. Results/plan/verification/index updated.

## [2026-10-23] verification | Installed shutdown tests expose delayed-attribution gap

Six revision-3 actual-service shutdown-window rounds complete: four pass acceptance,
CALDERA 0/2 retain full payload but have 122/309 unresolved controlled file rows
(437 events/96 PIDs). All six have canonical process hashes, captured activity after
SIGTERM, logged data-before-lifecycle stop order, endpoint coverage and graceful
stops/no restarts; no known-hash orphans or fabricated identities. Affected file
intervals lie within recorded canonical lifetimes; all 96 exit shadows use history,
and read-only native resolver snapshots plus matching WAL contain their lifetimes.
Final-state identity is not earlier availability; ReceiveTime=0 leaves registration/
retry timing unproven. Copied DB alone looked empty until matching WAL replay;
original stores unchanged. Separately run legacy-no-start control fails stop budget
and conservation (1,260 paths/7,702 events, 6,201 unknown file rows); 41 unknown/one
canonical live Stop, all 42 lifetimes unknown, no timestamp substitutes. Truncated
sidecar/native/archives retained. Both original-host services left stopped with
experimental revision 3/overrides; normal conservation and recovery/release gates
remain open. Results/trace JSON/verification/plan/index updated, no production rollout,
historical repair, commits/pushes or evidence deletion.

## [2026-10-23] code | Diagnostic retry-counter candidate without policy tuning

After CALDERA shutdown unknowns with containing final resolver lifetimes, added
bounded per-stream cumulative retry scheduled/refused/exhausted/invoked/error/
shutdown/pending/high-water snapshots and final logs. No PID/path payloads or
retry-capacity/timing/identity changes; counters do not prove resolved/delivered
events. Regressions distinguish forced final flush from normal exhaustion and
test stream separation/immutable snapshots; initial 183 focused native tests pass,
expanded final tests/revision-4 native build underway. Seven Python harness guards/
compile checks pass; analyzer collects new receipts and prints scoped shutdown
acceptance gates. Stuck pre-retry shutdown still lacks final receipt and remains
incomplete. Feature results/verification/plan updated; delayed attribution, normal
conservation, missing-birth/release gates stay open.

## [2026-10-23] experiment | Revision-4 diagnostic build and CALDERA retry receipts

Final 184 focused native tests pass; self-contained revision-4 package build succeeds
with recorded package/DLL hashes. Installed only on approved stopped CALDERA;
fresh three-round shutdown-window experiment now running with preserved native
identity state. AXON remains stopped on revision 3. No retry policy/recovery changes.
Independent parser three tests pass; preserves cumulative reason counters and flags
malformed/duplicate/negative fields, absent receipts not treated as zero. Optional
analysis gates require four default-stream receipts/pending zero/no callback errors,
not proof of attribution success. Build still warns optional diagnostic-provider
host dependency unresolved. Release/conservation/delayed-attribution failures remain
open; prior captures and historical DB preserved. Results/verification updated.

## [2026-10-23] diagnostic | CALDERA unresolved event counts match retry capacity refusal

Revision-4 three installed shutdown rounds analyzed/archived. Two fail attribution:
218 rows/230 events and 198/218; retry capacity refusals 230/218 with high-water
1024 and zero normal exhaustion. Third passes with no refusals/high-water877.
All 99 affected PIDs have containing canonical Start/Stop observations; aggregate
event counts match refusal counts, not a per-message trace or historical trigger
proof. All TCP/receipts/pending-zero/error-zero/graceful/no-restart gates pass.
CALDERA left stopped on revision4; AXON stopped on revision3. Revision5 diagnostic
Linux-only exact 1024/2048/4096 selector/default unchanged added for six interleaved
same-binary sensitivity controls; native tests/build pending. No permanent tuning/
never-observed-birth recovery/release acceptance. Results/trace/plan/verification/
index updated; captures and historical DB preserved.

## [2026-10-23] experiment | Bounded same-binary retry-capacity controls launched

Revision5 self-contained native build and 196 focused tests pass. Verified package
hash, installed on only approved inactive CALDERA, and launched six interleaved
1024/4096 actual-service shutdown captures with same binary/fresh roots/persistent
native identity. Default remains1024, attempt limit10/interval1s unchanged; Linux-
only experimental knob, not release tuning. Independent effective startup receipt
checks added; five parser tests pass including absent/malformed configuration.
AXON remains stopped on revision3; prior failed evidence preserved. Await controls
without polling; conservation/recovery/permanent memory/deadline gates remain open.
Results/plan/verification updated, no production rollout/history repair/commits/pushes.

## [2026-10-23] verification | Same-binary capacity sensitivity supports admission pressure

All six revision5 CALDERA captures analyzed/archived, same DLL/Exit hashes, matching
effective config, persistent agent, graceful/no-restart stops. Three4096 controls
pass captured identity/attribution/TCP/shadow gates; one1024 control fails336 rows/
358 unresolved events matching358 capacity refusals, all67 PIDs have containing
canonical lifecycle. One4096 control resolves high-water1061 above default; other
pair pressure differs and round1 lacks retry traffic, so no blanket capacity-fix
causality/release claim. All exhausted/error/final-pending counts zero; no known-
hash orphans/fabrication. Default stays1024; missing-birth/conservation/permanent
drain/resource gates open. CALDERA stopped on revision5 with retained experimental
4096/batch-wait override, AXON stopped on revision3. Original DB unchanged; prior
failures/native/archives retained. Results/summary/plan/verification/index/strategy
updated; next recovery requires early birth/per-event fate/PID-reuse/drain budgets,
not simple queue enlargement. No production rollout/history repair/commits/pushes.

## [2026-10-23] code | Exit-only recovery candidate and retained test failure

Revision6 opt-in kernel-start exit evidence reuses bounded lifetime-keyed history,
without synthetic Start/durable row/active entry. Sidecar marks partial coverage;
default off. Initial compile interface mismatch corrected; next216 tests yield
215pass/1fail: pending-Stop logging bypasses injected sink before late-birth cache
invalidation. Corrected logging and canonical pending-Stop identity matching;
added reused-PID regression. Corrected217 tests and self-contained package build
pass, package/DLL hashes recorded. Four isolated same-binary controls underway
(off/on missing birth, on normal, on legacy-no-start), capacity1024/effective-env
check/30s settle/SIGTERM/120s budget; no installed-service changes. Inline remote
launcher fails parsing before execution; retry uses mounted script directly.
Failed evidence retained. Original hosts stopped on revisions3/5; recovery/drain/
conservation/release gates open. Verification/plan/index updated; no history edits,
commits/pushes or evidence deletion.

## [2026-10-23] verification | Exit-only controlled recovery; installed CALDERA pairs launched

Four isolated revision6 controls independently analyzed/archived. Missing-birth
recovery on:8,478/8,478 canonical files,42 canonical Stops/partial receipts,no
synthetic births,2,088 paths/14,616events conserved,12s graceful stop. Off:12,053
unknown files/59s stop. Normal passes9,130files/84process vectors; legacy-no-start
retains zero exit evidence,12,519unknown files,32unknown/10canonical live Stops,
all42lifetimes unknown. All conserve payload/graceful; single pair does not certify
resource/drain budgets. Whole missing-birth on-control has200 nonworkload known-
hash orphans (live harness/daemons), zero unknown files; lifecycle export remains
incomplete. Default1024 retry refusals off/on11,980/0; schedules50,544/519 are not
per-event fate. Installed lintap-dev PID701/restarts0 unchanged; remote upload
unavailable. Source shared semantics concept updated with REVIEW NEEDED, existing
hard review retained.18 independent/harness/parser tests pass. Revision6 package/
DLL verified and installed only on inactive CALDERA; three actual-service off/on
missing-birth pairs/TCP now running, persistent native state/effective-env/120s stop.
First wrong mount-prefix launcher fails before execution, corrected without mount
changes. AXON stopped revision3. Results/full+summaryJSON/verification/plan/index/
strategy updated, supplied DB unchanged; no release/history repair/commits/pushes.

## [2026-10-23] verification | Installed exit-only recovery passes three controlled pairs

Six CALDERA same-binary/default1024 off/on controls independently analyzed/archived.
All three on pass25,434canonical files/126canonical Stops+partial receipts,zero
synthetic births,6,264paths/43,848events conserved,six linked TCP cases. Off fails
37,575unknown workload files plus three sentinel network rows per capture despite
orientation passes. All six graceful/no restarts/effective-env+config match/same
DLL+Exit hashes/persistent agent. Whole on-captures retain708nonworkload known-
hash orphans (live harness/daemons/systemctl exits after lifecycle cutoff),zero
unknown files; lifecycle export remains incomplete. Retry schedules off/on140,679/
650 and refusals32,773/0 support controlled recovery,not per-event fate or resource/
drain budgets. Full+summaryJSON and QA/data archive hashes preserved; historical
DB unchanged.18 Python regression tests pass; analyzer now checks installed verified
environment as well as isolated receipts. After analysis AXON upgraded to verified
revision6 and eight dual-host normal-birth default/drain/burst/restart regressions
launched,exit recovery on/default1024/explicit birth sensors/native persistent state.
Results/verification/plan/index/strategy updated; shared semantic review marker
retained. No production rollout,historical repair,commits/pushes or evidence removal.

## [2026-10-23] verification | Dual-host revision6 normal regressions pass

All eight installed normal-birth default/drain/burst/restart rounds independently
pass:20,880paths/146,160payload events conserved,840canonical process observations/
92,571canonical files,420kernel-start/lifetime checks,16linked TCP cases. Whole
104,518files zero unresolved/unknown-named/known-hash orphans. Effective-env/config
match,same binaries,persistent distinct agents,zero retry refusals/errors/final
pending,graceful3.29–16.37s/no restarts. Both default-no-extra-wait rounds pass;
no claim exit cache alone explains prior revision3 losses or defines permanent
drain/resource budgets. Full+summaryJSON/preliminary CALDERA results/QA+data archives
retained with hashes,supplied DB unchanged. After analysis/archival,six actual-service
shutdown-window rounds launched across both approved hosts,exit recovery on/1024/
enabled birth sensors/native persistent agents; post-cutoff events not conserved
by acceptance. Results/verification/plan/index/strategy/shared review status updated.
No production rollout,historical repair,commits/pushes or failed-evidence removal.

## [2026-10-23] failure | Revision6 saturated shutdown attribution persists

Six shutdown windows independently analyzed/archived:AXON3pass,CALDERA3fail.
CALDERA720/437/189unknown file rows,797/467/207events exactly matching capacity
refusals;1,346rows/1,471events total,199distinct PIDs. All have canonical containing
recorded lifetimes and matching closed final-resolver rows (preserved WAL read-only
replay;DB+WAL SHA256 unchanged). Affected sidecars report history,zero retained
exit evidence; raw process ReceiveTime0 cannot show when identity became available.
No exhaustion/callback errors/final pending;all CALDERA high-water1024. All six
graceful15.08–25.29s/no restarts,post-SIGTERM captured stimulus nonvacuous,TCP linked,
correct stop order/complete effective-config receipts,no known-hash orphans. No
claim full post-cutoff conservation,per-event fate or permanent drain fix.21 Python
tests pass;trace exact birth/both file bounds and no vacuous affected-lifetime proof.
Full+trace summaryJSON/native QA/QA+data archives and hashes retained. Both host
services confirmed stopped on experimental revision6,retained recovery-on/1024/
birth-on/batch-wait overrides. Results/verification/plan/index/strategy updated;
next bounded admission/final-fate and birth-registration timing before early-birth/
staged-drain correction. No queue increase,history writes,production rollout,
commits/pushes or failure deletion.

## [2026-10-24] documentation | Start ecosystem glossary and grouped-retry proposal

At user request, created source-linked living glossary across ecosystem, collection,
identity/lifecycle, clocks/evidence, queues/shutdown, networking and DBT/analysis;
expansion queue retained and existing diagram glossary preserved. Added speculative
grouped-retry notes: local PID+event-time lookup, lifetime-qualified fanout, no blanket
miss denial, per-member deadlines, fair bounded events/bytes and separate adjustable
coalescing wait versus evidence-defined identity validity. Positive caches already
exist; repeated-miss/coordinated wakeup benefit remains unmeasured. Index/strategy
linked; no source/service/config changes or new experiment authorization inferred.

## [2026-10-24] clarification | Collection-edge tolerance and sensor-service shutdown

User accepts incomplete start/end collection observations within an explicit
boundary tolerance. Recorded the principle; numeric edge widths/classification
remain pending. Separate start-edge/interior/end-edge quality,actual collection
from query-slice bounds,and event time from processing/cutoff time; do not extend
identity validity or silently rewrite prior strict failure records. Clarified that
CALDERA shutdown tests stop lintap.service/collector PID with SIGTERM while test
activity continues,not the VM/OS or CALDERA application. Glossary/results/strategy/
plan/index updated; no code/config/service changes or new runtime experiments.

## [2026-10-24] requirement | Collector process visible in normal telemetry

User requires Lintap service process in ordinary telemetry for retrospective normal-
dataset validation. Current EventChannel and Linux Rundown self-PID exclusions
verified; not yet changed. Strategy/plan/results/glossary record recommended normal
process-stream identity/metadata and genuine lifecycle semantics,retained file-I/O
feedback suppression,explicit capture boundaries,and no invented self-exit record.
No source/config/service changes; implementation and normal-dataset tests pending.

## [2026-10-24] implementation | Collector visibility candidate and bounded verification

Approved Linux Process-only self-filter exception and collector Rundown inclusion
implemented; missing-birth inventory no longer hashes observation time. Preserved
self-I/O/other-platform filtering, genuine Refresh and no invented exit/cutoff.
New pure-policy/inventory/egress regressions and independent normal-row/restart/DBT
verification tooling;28Python tests pass. Native attempts preserve compile failure,
229pass/7runtime-permission fixture failures,and229pass then45s testhost abort with
dump/sequence. Isolated pure policy avoids test-triggered runtime static dependency;
fresh test/build pending. Canonical collector/boundary draft/index and verification
updated. No installed-host mutation,production rollout or prior evidence deletion yet.

## [2026-10-24] verification | Collector focused suite passes; packaging snapshot corrected

236focused C# tests pass and Linux publish succeeds. Preserved235pass/1egress
failure:fixture isolation flags were set after static routing initialization;
ordering corrected,not runtime registration semantics. Debian staging fails only
because native snapshot lacked three existing pidstat packaging helpers; fresh
complete snapshot/build launched. Strategy/checklist/glossary/pipeline/canonical
collector semantics updated; ordinary installed/DBT proof remains pending.

## [2026-10-24] experiment | Revision7 collector candidate normal/restart rounds launched

Fresh complete native snapshot:236C#tests pass,self-contained revision7 Debian
package succeeds;package/DLL SHA256 recorded in verification. Copied candidate to
approved inactive AXON/CALDERA; guarded installs/4normal default/drain/burst/restart
rounds launched each with enabled birth inventory,default1024,experimental exit
recovery and persistent native agents. Fresh capture/QA/install roots preserve prior
override/evidence. Ordinary-row collector oracle and fresh canonical DBT model
builds prepared;normal/self-feedback/conservation/endpoint/downstream proof pending.
No production rollout,historical migration or boundary-policy reclassification.

## [2026-10-24] planning | DuckDB 2 ecosystem upgrade

Started `wiki/work/duckdb-2-upgrade/{brief,references,implementation_plan}.md`
and linked index. Verified October21 DuckDB2.0LTS release/Python>=3.11/new-file
storage69; inventoried Wintap embedded1.5.6,Wintappy locked+actual1.5.5/adapter1.9.6/
core1.12.2,Lintap pidstat/bootstrap/CLI and current Analytics paths. Relation
fetchone removal reaches DataQA/shared helpers; latest released adapter1.11.0
predates2.0 and lacks a development-branch result-draining fix. Official .NET
NuGet latest1.5.6.1 has no2.0; unofficial fork exists but not selected/authorized.
Plan separates Python/DBT qualification from native package gate,copy-only DB/WAL
rollback and fresh-output semantic/conservation comparisons. Excludes old notebooks,
arbitrary SQL,legacy cleanup,historical repair and existing defect fixes. Existing
collector DBT completion retained as baseline:8builds retain collector,4exact-birth
failures. No source/dependency/environment/service changes or new runtime experiments.

## [2026-10-24] decision | Hold DuckDB 2 upgrade for official .NET support

User chose to wait on2.0 because official .NET availability is a blocker; brief,
plan and index marked held. Rechecked registries:latest official .NET wrapper
1.5.6.1 still bundles native1.5.6;latest Python1.x is1.5.6. Latest-1.x maintenance
considered separately; no implementation or dependency/environment changes authorized.

## [2026-10-24] maintenance | Latest DuckDB1.5 dependency upgrade verified

User approved the three enumerated components. Wintap official wrapper1.5.6.1 and
five affected locks refreshed; native engine remains1.5.6. Wintappy/Lintap manifests,
uv locks and pidstat bootstrap pin1.5.6; selective lock audits show no unrelated
package-version drift,DBT adapter1.9.6/core1.12.2 retained. NativeSDK10.0.402 tests250
pass,Linux/Windows-helper builds pass;PythonSQL82,pidstat15,SmokeTests27,collector
analyzer7 pass. Fresh fullDBT83nodes (40models/42tests/1hook) pass on retained AXON
drain raw data;collector exact birth/metadata/uniqueness pass,historicalDB size/mtime
unchanged. BroaderPython107pass/1config failure reproduces under1.5.5. Failed command/
platform attempts preserved;unintended uv recreation of MacLintapvenv3.14→3.12
disclosed,prior environment not preserved or falsely claimed. Feature verification/
plan/index and canonicalWintappy dependency note updated. No installed-service,
runtimeDB,agent-state,notebook,history changes or commits/pushes. DuckDB2.0 held.

## [2026-10-24] implementation | Collection-edge overlay and revision8 outstanding-item reruns

User approved10-second start/end edges with1/5/20-second sensitivity. Implemented
integer interval/bracket classification,verified local-clock receipts and endpoint
stimulus intervals;strict gates/counts preserved,no invented capture bounds or
identity extension. Historicalrevision7 lacks independent clock receipts and remains
unclassified. New same-installed-revision7 default+shutdown round per original host
passes all scoped raw gates:normal2,088paths/14,616events each,all TCPcases pass,
31,083whole file rows/no unknowns or known-hash orphans.10-second normal stimulus
interior;shutdown mostly uncertain under broad operational cutoff brackets. CALDERA
shutdown2,615scheduled/high-water932of1024/no refusals,so prior saturated failure
not reproduced or explained.64work-folder tests pass (45boundary/harness).8historical
plus4fresh DBT model runs all pass/retain collector metadata,exact birth fails same
4historical and3fresh at−1µs. Integer-only diagnostic SQL recovers12/12raw births;
source float macro unchanged and Linux-as-Windows defect persists. BroadPython
107pass/1existing config failure repeats. New QA+data archives SHA256 verified,
binary/AgentId unchanged,both services stopped/PID0/restarts0,historicalDB size/mtime
unchanged. Results/verification/checklists/canonical collector/glossary/index updated.
No package/source-sensor/DBTmacro deployment,prior failure deletion,production rollout,
commits/pushes. Next:qualify integer timestamps,admission/final-fate/registration
timing and preserved loss/TCP provenance;more precise cutoffs if uncertainty matters.

## [2026-10-24] implementation | Integer timestamp proof and bounded attribution trace

Approved continuation fixes canonicalWintappy FILETIME timestamp/minute macros using
integer epoch subtraction/floor-toµs,TIMESTAMPTZ output and integer-text parsing;raw
100ns identity unchanged.209focusedSQLtests pass;234broadpass/1existingDATASETconfig
failure retained. Fresh fullDBT12/12 (83nodes each) restores all12collector births;
2,900raw-integer process lifetimes pass.216common tables retain protected keys,
counters/rows;strict metadata comparison fails and remains archived.12same-old-macro
controls reproduce unordered names/paths/args/derivedfileID drift;qualified comparisons
separate those fields/duration without blanket display/file-ID stability acceptance.
Default-offLinux create-new boundedJSONL admission/lookup/registration/handoff trace
implemented;240nativeSDK10.0.402tests/Linuxbuild pass,initialAPI-property compile
failure and subsequent I/O-drop accounting correction preserved. Limits1024queue/
100kreceipts/32MiB/512characters,explicit refusal/error/truncation,2sclose deadline;
handoff is not durable fate.68wikifoldertests pass;new precision contract/results,
glossary/collector/repo/index/plans/verification updated;frontmatter/links/diffchecks
pass. Native logs/TRX/sourcehashes downloaded to approvedr9-native-evidence root.
No live tracing/newpackage/service changes:active lintap-dev left alone;AXON/CALDERA
inactive/PID0/restarts0/Resultsuccess,DLL unchanged,historicalDB size/mtime unchanged.
Self-contained diagnostic captures/export joins,saturation/loss/TCP provenance,
cutoffs,OSlabels and rollout gates remain open. No commits/pushes/DuckDB2upgrade.

## [2026-10-24] diagnostics | Private delivery package and failed observer controls

User approved reproduced-loss milestone. Expanded default-off observer through file
folding/sender/serializer/parquet finalization;244nativeSDK10.0.402tests/Linuxbuild
and self-contained Debian package pass. Four private AXON/CALDERA controls complete;
no installation/service edits,original DLL/AgentId unchanged. Both traces refuse
receipts (15,925/22,339);shared mounted root combines both hosts,strict path-set gates
fail. Per-host grouping2,088paths/14,616events does not accept contaminated captures.
First-round runtime-log snapshot omission also preserved;edges unclassified.
Archives transferred/SHA256verified;78wikifolderpytest pass. Corrected host-specific
roots/stopped snapshots and explicit bounded delivery trace queue32768 prepared;
retrycapacity1024unchanged. Revision11 inherited post-publish RID lock causesNU1004;
failure/locks preserved,live source locks used for locked requalification. Results,
plans,verification,index/glossary updated. Historical loss/TCP provenance remains open.

## [2026-10-24] proof | Complete scoped delivery traces and reproduced TCP stage gap

Revision11locked-source244tests/Linuxbuild/self-containedpackage pass after preserving
NU1004/post-publish locks. Fourprivate host-isolated controls conserve8,352paths/
58,464events,canonicalidentity/collector/workloadTCPpass. Complete scoped traces:
193,040AXON/190,071CALDERAreceipts,zero refusals/errors/truncation;finalizedfile/TCProw
multisets match archivedraw,file-stagecounts match. BroaderTCP54prepared/Esper→50serializer
events per host fails;fourmissingSSHcounts overlap startup. SourceasyncETLStart/fixed
5sdelay and networkstartup beforeTCPinit support readinessrace;precise registration/
projection receipts and controlled correction remain required.40,170wholefile rows
zero unknown/orphans;10sedges/1,5,20ssensitivity preserve gates.80wikifoldertests/diffchecks
pass;archivesSHAverified/sourcehashes match,originalDLL/AgentIds/historicalDB unchanged,
servicesinactive/lintap-devactive untouched. Results/verification/plans/index/glossary/
canonicalboundary updated. Prior AXONloss/workloadTCP/CALDERAsaturation unresolved;
no sourcecausefix/rollout/commits.
## [2026-10-24] verification | Exact startup proof and bounded readiness control

Revision12query/listener/callback/projection diagnostics,productionEPL deterministic
test and247native tests/Linuxbuild pass. Live complete traces prove CALDERA6counts
andAXON4counts handed off before registration;AXON6additional missing remain separate.
Revision13default-off Linux readiness admits collectors only after successfulquery/
completedconstructors,30sbound,existing5sdelay unchanged.254native tests/Linuxbuild;
four off/on controls conserve8,352paths/58,464events,identity/collector/self-I/O/eight
TCPcases pass.42,005wholefile rows zero unknown/orphans.192,688/190,332complete receipts
prove startup ordering;CALDERA54→54→54passes,AXON54→54→48fails. ExactacceptedTCProwIDs
31378/31380 absent fromdrain/enqueue/finalized;lateprojection/shutdown cause unproved.
Final→rawjoins pass but not full delivery acceptance.10sprimary/1,5,20s sensitivity
preserved;revision13workloadintervals uncertain,not softened intointerior.88wiki tests
andbothdiffchecks pass. InitialENOSPCattempt archived/949filesbyteverified before only
newdisposable snapshot removal;activePID701 notsignaled,completeI/Oeffect unproved.
Initial253pass/1closebudget failure archived;boundedwriter tests isolated fromparallel
EPLcodegen without changingproduction2sbudget. Packages12/13managed-only derivatives
of11,notclean native rebuilds/installedacceptance. Updatedresults/plans/verification,
index,glossary/boundary pages;addedexactreadiness/delivery-ID joins and JSONreceipts.
Finalservices/DLL/AgentIds/historicalDB unchanged,258testedsourcefiles matchlive;
no runningcaptures/builds. HistoricalAXONloss/defaultTCP,CALDERAsaturation,resource/
cutoff/draining/rollout gates remainopen. No historicalrepair or DuckDB2change.

## [2026-10-24] milestone | Exact shutdown proof and verified disposable Linux delivery

Revision14exact brackets reproduce twoCALDERATCProws/fourcounts accepted after
completed shutdown,all undrained. ProductionEPL deterministic control proves
queue-before-final-window strands counts. Revision16Linux/default-off terminal
window/callback barrier qualifies267native tests/locked Linuxbuild;revision15
ambiguous-import compile failure archived and corrected in fresh16snapshot.
Fourrevision16controls conserve8,352paths/58,464events and54AXON/60CALDERATCPcounts
through exact accepted/drained/enqueued/finalized row IDs and archivedraw joins.
Samecandidate17 repeats58/58perhost with all payload/endpoint stimuli interior at
1/5/10/20s. Independentidentity/collector/self-I/O/eightTCPcases pass;complete traces
zero refusals/errors/discards/truncation/lateacceptance/cutoffrefusals. Wholefile
39,893rows zero unknown/orphans;10s39,807interior/25start-edge/61uncertain retained.
Scoped observed-delivery milestone verified,not historical loss closure,complete
kernel/durable fate,resource/Windows/customEPL/installed-package/rollout acceptance.
94wikifoldertests/bothdiffchecks pass;archivesSHAverified/262testedsource matches,
originalservices/DLL/AgentIds/historicalDB unchanged;lintap-devPID701 untouched.
Updatedshutdown plan/results,implementation/traceplans/verification,index,canonical
boundary/glossary and JSONreceipts. Managed-only private derivative16,not clean native
rebuild;no install/commit/push/DuckDB2upgrade. No captures/builds remain running.

## [2026-10-24] experiment | Attribution pressure baseline and corrected TCP receipt oracle

User approved samecandidate revision16 pressure with1024capacity unchanged. Independent
32/128/256child file/TCP generator and gated off/on interior/shutdown-tail experiments
created under wiki;no sensor edits or installed rollout.32tier eightcontrols conserve
1,024paths/7,168events;eightfresh fullDBTbuilds pass256births/collector/counters.
Original128revision20 halts escalation on44CALDERAtrace-off endpointpairs/152apparent
misses. Exact archivedraw proves ALL152present after stimulus+2s but within capture:
TCP EPL FirstSeen uses ReceiveTime,not kernel EventTime. Originalfailure preserved;
deterministic test proves falseabsence and bounded capture-scope oracle correction,
not sensorloss/saturation/time-schema change. Separate20recheck/fourDBTbuilds pass.
Fresh128revision24interior/25tail pass1,024childlifetimes/4,096paths/28,672events,
eightDBTbuilds and complete exact delivery traces;no queue refusal/exhaustion/OOMdelta.
256tier still running;no final envelope claim yet.103wiki tests pass. Plans/results,
verification/glossary/index updated;failed evidence/history/control preservation remain
mandatory. No queue resize,production sizing,historical-loss closure or DuckDB2upgrade.

## [2026-10-24] verification | Controlled pressure envelope complete through256 children

Fresh256interior26/shutdown-tail27 pass after gated128repeat24/25. Sixaccepted
experiments/24off-on hostcontrols conserve3,328childlifetimes/TCPendpointpairs,
13,312payloadpaths/93,184events.24fresh canonical83nodeDBTbuilds pass exactbirths,
collectorretention and raw→silver/goldprotectedfilecounters.12complete traces write
1,013,739receipts with zero refusals/errors/discards/truncation;exactobservedstage/
finalrawjoins pass.256TCPcounts1,857AXON/1,855CALDERAinterior,1,845eachtail. Highest
sampledpending348/1024,no pressurechildcapacityrefusal/exhaustion;not actualsaturation
or productionqueue sizing.10s/1,5,20s stimulusbands preserved,tailuncertainty not
relabeled. Original20oraclefailure/all152rawobservations/causeproof and separate
fourDBTrechecks preserved. No sensorfix/capacitychange/historyrepair/installedrollout.
Finalaudit28archivesSHAverified/262sourcesmatch,installedDLL/AgentIds/historicalDB
size-mtimeunchanged,AXON/CALDERAinactive/PID0/restarts0,lintap-devactive/PID701/restarts0.
103wiki tests/bothdiffchecks pass. Plans/results/verification/index/glossary updated.
No builds/captures running. Resource/nativekernel/durable/Windows/package/rollout
acceptance and historicalfailures remain open;DuckDB2held. No commits/pushes.

## [2026-10-24] retrospective | Telemetry identity/data-quality workflow and compact audit

User confirmed the broader retrospective scope beyond .NET10,and explicitly asked
to reduce audit detail in the commit,not merely add an entry point. Created compact
`wiki/work/wintap-telemetry-identity-and-data-quality/` brief,design,reconstructed
implementation,verification,next-phase handoff and evidence provenance. Condensed
old workstream documents from4,442to1,514lines;replaced the repetitive index rollup.
Original193files/62,580,675bytes byte-verified in an external3,840,232byte archive;
SHA256/path/retrieval map recorded in evidence.md.124generated JSON audits
(62,025,196bytes) retained locally but Git-ignored;harnesses/tests/raw/failed evidence
and source/history untouched. Archive is machine-local temporary storage and must
be transferred/verified before cleanup;no durable publication claimed. Updated
canonical evidence citations;sample-db audit remains human-review-required with
REVIEW NEEDED for provenance-only edits,findings unchanged.26pages pass frontmatter/
source/wikilink validation,103work-folder tests and diffcheck pass. No commits/pushes,
new sensor edits,host captures,package installation or long-duration runs. User's
planned package qualification/multi-day real-host collection remains next phase.

## [2026-10-24] commit | Dedicated telemetry-quality branches across four repos

User authorized feature commits and separate PR branches. Created
`feature/telemetry-identity-data-quality` in Wintap, Wintappy, Lintap and Analytics.
Wintap `10a782f` commits identity/network/lifecycle and bounded delivery diagnostics;
Wintappy `4236cbb` commits SQL precision/count/identity fixes and DuckDB maintenance;
Lintap `b793082` commits the qualified DuckDB pin. Analytics commits QA, compact
retrospective, reusable harnesses and wiki semantics in this entry's commit.
Wintap retains its tested .NET10 ancestry: target `chore/net10-dependency-prune`
for an isolated PR until that prerequisite merges. Generated receipts, captured
datasets, initialized AgentId state, local settings and unrelated work stay local.
Preflight: 209 focused SQL tests, 126 Analytics tests plus 7 subtests, and 17 Wintap
Python regressions pass; all staged diff checks pass. Dashboard AppTest collection
is blocked by missing `streamlit.testing` in the selected environment; no environment
changes or new native/host qualification. No pushes or PR publication performed.

## [2026-10-25] documentation | Pinned .NET 10 packaging and operator-assisted RHEL 9

User authorized updating Lintap's packaging guide and adding RHEL 9 prerequisites;
user will execute host commands without direct agent access. Updated live
`../Lintap/packaging/README.md` to select SDK 10.0.402 from Wintap global.json,
distinguish exact qualification checks from latestPatch, and document RHEL 9
inventory/repository/native dependency/build/package inspection and gated service
validation. RHEL 9 remains unqualified. Retained self-contained defaults and flagged
both builders' stale ASP.NET Core 8 framework-dependent metadata; no scripts changed.
Source-verified libbpf SONAME fallback, security preservation and pidstat prerequisites.
Updated supporting-repo page, index and umbrella verification. SDK consistency,
shell-fence syntax and diff checks pass; no RHEL commands, installs, captures or
security changes executed. No new commits or pushes for this documentation update.

## [2026-10-25] plan | Close .NET 10 upgrade oversights, not a package-mode workaround

User clarified that framework-dependent .NET 8 metadata is an oversight in the
original all-.NET-10 upgrade and requested a corrective plan while testing RHEL
dependencies. Tracked source inventory across four repos confirms SDK 10.0.402 and
eight main .NET 10 projects, but five diagnostic/sample net8 projects, both package
builders' runtime-8 dependency declarations, Makefile/provision/run/tooling defaults
and current docs remain stale. Created runtime_alignment_plan.md with package-first
correction, complete target/provision/path alignment, regression inventory and fresh
artifact/live gates; dependency major versions and historical records are distinct.
Updated umbrella implementation/index. No "10 everywhere" or fresh runtime claim;
no source implementation, host execution, commits or pushes under this plan request.

## [2026-10-25] code | .NET 10 source/configuration closure and RHEL build handoff

User authorized correction, commit and push on existing feature branches. All 13
C# projects evaluate to .NET 10 with SDK 10.0.402. Corrected both package runtime
dependencies, exact-SDK/project-directory preflight before cleanup, main runtimeconfig
validation, five targets/sample reference, native generated-source exclusions,
Windows-only sample copy, provisioning and active run/tool/docs defaults. Added five
sample/diagnostic locks; legacy vdproj snapshots explicitly not release packaging.
Six Wintap drift and 22 Lintap packaging regressions pass; five fresh locked sample/
diagnostic builds, both actual linux-x64 managed publish modes and separate MCP
single-file publish pass. Preserved
NU1004 committed API RID-lock mismatch: isolated restore keeps all base hashes/
versions, then locked publishes pass; pristine locked RID release gate remains open.
Generic RHEL 9 prerequisites pass; test system is disposable by user direction.
No host identifiers/raw output persisted, no direct host access/security changes.
Shell/help/link/diff checks pass. Fresh native RPM/Debian inspection and live host
acceptance remain pending; retry/identity/experimental controls unchanged. Commits
and pushes are explicitly authorized; PR publication is not part of this operation.

## [2026-10-25] verification | Operator-reported RHEL 9 package build and installation

Operator reports native self-contained RPM build, satisfactory inspection/transaction
preview and installation with both units inactive. Shared NuGet package/HTTP caches
prefetched on a network-enabled Linux system resolved restricted-network restores;
prefetch must match publish properties/multi-RID graph. No TLS/audit relaxation or
system identifiers/raw output persisted. Runtime/configuration/hook/data/shutdown
acceptance remains pending. Corrected one remaining obsolete framework-dependent
warning in the canonical packaging guide; documentation-only follow-up on same branches.

## [2026-10-25] verification | Bounded RHEL 9 capture, shutdown and downstream smoke

Operator reports host-only/normal startup, process with Stop, basic single-path file,
independent bidirectional same-host TCP identity/endpoints and clean shutdown with no
active files. Pidstat remained inactive and protected data permissions unchanged.
Supplied fresh DBT summary passes 40 models/42 tests/one hook: 83 pass, zero warnings,
errors or skips; engine 1.5.6/adapter 1.9.6/core 1.12.3. Shared official extension
prefetch must INSTALL both httpfs/parquet and use connection-time config_options,
not late settings; failed attempts retained locally, TLS/signature checks intact.
Updated verification, runtime plan and index. No raw output, host identifiers or
system-specific details persisted; generated evidence remains protected/local-only.
Full release/provenance/strict-count/multi-day and other platform/mode gates stay open.

## [2026-10-25] code | Independent periodic Linux stimulus and ground-truth runner

User approved open-ended disposable-host collection, manual stopping and a separate
tmux signal generator on each host; SmokeTests dashboard suffices for ground-truth
analysis. Added Analytics validation/telemetry-soak runner: named process/file/IPv4
TCP/UDP and same-host TCP selectors, existing raw_smoke_test export and private local
JSON/logs, sequential rounds/timeouts, same-root flock and failure continuation.
No collector management, credential/security changes, retention deletion or sibling
code edits. Clarified WINTAP_DATA_ROOT/explicit smoke-data-root (not DATA_PATH),
successful-upload local deletion, stimulus-only outcomes and deferred DBT integration.
Added canonical tool page and updated index/implementation/verification. Eleven
mocked tests, bash syntax and diff checks pass; native pilot/Garage evidence arrival,
signal/timeout and long-running behavior remain pending. No host identifiers or
generated evidence committed; test fixtures are synthetic.

## [2026-10-25] code | Read-only Garage/S3 SmokeTests dashboard source

User selected direct Garage access on the same feature branch and reports one runner
pilot completed, uploader working and smoke evidence reaching S3. Added private
JSON config (credentials rejected), AWS env/profile chain, temporary in-memory
DuckDB secret, path-style listing/reads, connection-time extension cache, inclusive
UTC day pruning, pagination, fail-closed caps and sidebar refresh/source selection.
No object mutations, credential persistence, local dataset sync, collector/uploader
or sibling changes; TLS/signature checks retained. Existing manifest/host/run/triage
semantics and mounted/local mode preserved. Forty-two backend/query/Streamlit tests
pass in an isolated temporary environment; one real synthetic loopback HTTP/S3 test
passes GET/HEAD listing/range-read/ground-truth join after correcting secret syntax.
Actual Garage dashboard validation and long-duration acceptance remain pending;
DBT manifest integration deferred. Updated canonical docs/index/plans/verification.
No real identifiers, credentials, endpoint/prefix configuration or host output filed.
Final suite including real loopback HTTP transport: 43/43 pass; Python parse/diff
checks pass and local config ignore is verified. Commit/push remains on the existing
feature branch; no PR publication.

## [2026-10-25] code | Non-interfering canaries and lazy Streamlit pages

User narrowed recurring scope to canaries that do not interfere with the deployed
sensor, and requested Overview, Canary Tests and Dev-time Tests pages. Expanded
Analytics runner to five distinct canary manifest families using generator-only
adapters: cross-domain, process lifecycle/short-lived, eight-file, optional native
clone and same-host TCP endpoints. Stop requirements are per PID; unsupported
Python execveat/native helper/kernel cases are explicit skips, not coverage claims.
No collector/service/security/tracer/uploader/sibling-code changes or host workloads.
Real Streamlit navigation separates canaries (including legacy stimulus-only runs)
from manual dev-time qualification. Overview reads manifests only; explicit selected
validation materializes one exact-selector working set for reused checks/details,
with fail-closed 100,000-row/256-MB limits and spill disabled. Hidden overlaps,
evidence hashes/conflicts and conservative missing/stimulus-only triage retained.
Native pushdown/partition pruning, passive HOST correlation and cross-rerun caching
remain follow-ups. Local tests use synthetic fixtures/mocked generators; native
expanded canary and live Garage page/validation acceptance remain operator gates.
Private config/profile/credentials/identifiers and live investigation outputs were
not persisted. Updated canonical pages/index/implementation/verification records.
Final checks: 51 dashboard tests (including synthetic real HTTP/S3 transport) and
17 mocked runner/adapter tests pass; shell syntax, Python parse and diff checks pass.
Same feature branch; no PR or live acceptance claim.

## [2026-10-25] code | All-canary validation, passive runtime context and saved summaries

User requested all validations on uploaded canary evidence, one round action, HOST
runtime comparison and result persistence beside data. Added Analytics round metadata,
one bounded shared selector scan, all-family/case/skip/missing/violation summary,
temporal complete-startup context and optional unique inferred short/FQDN correlation.
Exact hostname mismatch initially excluded observations; inferred correlation finds
process lifecycle/Stop, eight-file and both TCP endpoint expectations with no reported
violations. Cross-domain server TCP Accept and UDP Receive remain missing; Network
reports running, so disabled startup does not explain them. Native clone skipped;
all stimulus-only family triage remains yellow. No strict-count/full-capture waiver.
Summary and latest pointer saved/read-verified in Garage's sibling analysis prefix,
not raw telemetry. Fingerprinted reuse, explicit stale warnings, integrity checks,
verified atomic/private local writes, Git/symlink rejection and visible save failures
added; no source configuration/credentials/raw rows in summaries, no private local
investigation artifacts or identifiers committed. Listings/evidence reads still repeat;
no atomic storage snapshot or delivery watermark claimed. 75 dashboard tests including
real synthetic S3 transport and 17 mocked runner/adapter tests pass; Bash/AST/wiki-link/
frontmatter/diff checks pass. Updated canonical tools/index/plans/verification.
No sibling source, service/sensor/tracer/security/SDK/DuckDB/default controls changed;
no running workload restarted or PR published. Operator new UI/multi-host/long-duration
acceptance and native/network coverage remain open. Same feature branch commit/push.

## [2026-10-25] analysis | Canary quality gaps and proposed corrections

Reanalyzed the existing five-family pilot read-only (65.78 seconds, no analysis
errors); no new collection round, raw-data mutation or summary overwrite. Broader
PID/time queries do not recover server TCP Accept/UDP Receive. Current CO-RE source
has no Accept emission call and reads UDP kernel peer context with a user-memory
helper; deployed-object hash differs from local build, so live causal linkage remains
provisional. Live UDP Send tuples have zero endpoint ports; TCP listener-like close
rows also have incomplete peer tuples. All eight file paths have required activities;
selected lifecycle identities have no placeholders/mismatches, but 13 repeated-Start
groups need Clone/Exec provenance classification, not automatic duplicate-birth flags.
Five entirely synthetic evaluator counterexamples expose per-path, lifecycle identity/
repeat/linkage and extra malformed endpoint blind spots. Recorded source-aware fixes,
operation/provenance contracts and separately authorized sensor/pilot sequence in
quality_followup_analysis; updated index, canonical dashboard limitations and handoff.
No private identifiers/configuration/raw rows or investigation payloads filed. No source,
package, service, tracer attachment, security, runtime pin or default control changes.
Capture gaps/native skips and all prior acceptance limits remain open.
Diff whitespace, modified content-page frontmatter/wikilinks and new live grounding
paths pass. Synthetic diagnostics are not committed regressions; no source test-suite
rerun or implementation acceptance claimed. Same feature branch; no PR publication.

## [2026-10-25] code | Strengthened canary quality assertions

User authorized recommended-order fixes and local VM iteration while away. Added
13 synthetic quality regressions and stronger per-path/lifecycle identity/linkage,
source-aware repeated-Start and all-bound network candidate checks. Expected protocols
no longer filter the scan; directed ports also retain malformed host-relative tuples.
Contradictions remain red; incomplete/unbound traffic remains yellow, with summary/UI
warnings and counts. Clone/Exec raw observations are preserved, never counted as
distinct births or deleted. Existing pins/defaults/strict dev-time gates unchanged.
Idle VM uses isolated DuckDB1.5.6/Streamlit1.66.1/boto3 environment; all 88 dashboard
tests pass including real synthetic HTTP/S3, zero skips. Updated canonical tool,
README/plan/verification. Field-host services, raw datasets and private configuration
untouched. Sensor-owned fixes/VM qualification follow separately on existing branch.

## [2026-10-25] code | Local network return correction and qualification

User authorized recommended-order Analytics/Wintap fixes and local VM iteration,
not field rollout. Wintap core Accept now emits at successful return with accepting
TGID/inbound tuple; UDP uses checked kernel pointer provenance and one successful
protocol-return owner per operation. Actual arm64 tests also exposed errno sign-
extension and post-return msg_namelen pitfalls; corrected. Original object fails
strict15-check matrix, corrected object passes; all12 tracers build, managed build
zero errors,159 shared network/receipt/identity/resolver/root tests pass. Added
version-gated operation/sampling/PID-filter receipt facts and distinct UDP client
mode/socket plus per-path activity expectations. Preserved pins/retry/security/
default-off experiments and strict count gates. Evidence remains VM-local. Initial
normal-ETL harness mistakes (receipt phase, evidence ownership) exposed; fresh pilot
review follows. Canonical network/runtime/named-workload/dashboard pages and umbrella
handoff/index/plan updated. Wintap instructions/audit stay in its developer_docs.

Final verification:93 dashboard/17 runner/12 Wintap Python/159 shared managed tests
pass; actual-object repeat15 checks pass. Normal-ETL five-family fresh VM pilot
delivers manifests and observes Accept/all four independent UDP cases, zero evidence/
analysis errors; exact UDP and dedicated TCP endpoint checks have no missing/violation
findings. Local summary integrity/reload/latest passes; raw size/mtime snapshot unchanged.
All triage remains yellow. New tension: normal ETL lowercases Linux file paths despite
complete per-file activities; existing non-Windows behavior is explicitly preserved
by its regression, so no silent case-fold proof or unreviewed compatibility change.
Process projection also omits source breadcrumbs; no command-line/schema mutation
to fabricate provenance. Partial TCP EOF/close tuples remain incomplete. Field
package/install/pilot, file-case and explicit source-column contracts are next gates.

## [2026-10-25] code | Approved greenfield process-source and file-case projections

User explicitly approved both prospective changes; greenfield development does not
require deployment/data migration. Wintap normal Start/Refresh parquet adds nullable
ProcessStartSource from bounded recognized producer Arguments breadcrumbs, not
CommandLine inference. FileSerializer preserves producer case and case-distinct
sensor file-key inputs; Windows behavior/identity formulas/pins/security/retry/default-
off controls unchanged. Analytics prefers explicit source with real Arguments fallback.
Linux build0errors/177warnings;180shared managed and94dashboard tests pass, including
production-schema null/mixed provenance parquet roundtrip and locale/case-key negatives.
Initial new test incorrectly indexed a deserialized null key; corrected assertion,
not writer. Fresh180-second normal-ETL VM pilot delivers five families with0evidence/
analysis errors and0violations. Eight-file/process/clone/dedicated TCP have0missing
checks; all selected repeats source-classify without extra-birth claims. Cross-domain
retains one Delete gap and two incomplete TCP provenance checks; all triage yellow.
Receipt contract2/copied hash, local summary/latest integrity/reload and raw size/mtime
preservation pass; VM collector/observer inactive. Resolved sensor file-case tension;
Wintappy's separate lowercase-derived file_id remains unmodified/uncertified. Updated
canonical process/file/dashboard pages, index, plans, verification and handoff. No
private evidence/identifiers/configuration filed; no Garage writes, field rollout,
Lintap/Wintappy edits or PR. Same feature branches; unrelated work preserved.

## [2026-10-25] review | Senior technical assessment before closing quality round

Reviewed current sensor/projection/generator/dashboard/persistence source and prior
qualification evidence at Wintap c0b6774 / Analytics00dda2d. Synthetic current-code
probes reproduce permissive legacy source parsing and suppression of a known endpoint
contradiction when another field is null. Existing VM pilot read-only investigation
finds the missing relative.bin Delete as a bare relative basename in the same
host/PID/window; unlinkat loses dirfd and managed relative resolution only covers Open.
Created advisor_review with bounded corrective bundle, sampling/churn qualification,
native target-package gate and separate downstream case-ID plan. Prior pass counts
remain scoped; no new collector run or implementation. No private raw evidence,
configuration or identifiers committed. Updated index/handoff; recommendations await
user direction. Temporary synthetic query artifacts removed.

## [2026-10-25] code | Advisory corrective bundle and later RHEL9 validation

User approved Ubuntu source/test implementation and preparation for later RPM
deployment. Fixed strict legacy source parsing (explicit null authoritative) and
known endpoint contradictions with null companion fields. Wintap relative unlink
captures operation-time dirfd/cwd base identity; learned-index-only resolution
preserves unknowns and entry-intent semantics. Added live case-only/cwd stimuli,
conservative directory-resolution regressions, monotonic/outer observer deadlines
and24-lifetime UDP turnover qualification. Network48turnover/15return checks pass;
no forced pointer reuse claim or network sampling change. Linux build0errors/
177warnings;171targeted managed,97dashboard,20runner/CLI and11Wintap Python tests
pass. Broader Ubuntu Windows-targeted suite1160pass/87fail and timed-out isolated
retry of8logging-dependent tests remain explicitly unqualified in verification.

Fresh normal-ETL five-family pilot has0errors/0violations; exact relative/cwd Deletes
and case-only activities/distinct sensor keys pass. All29focused receipt/hash/
projection gates pass; only two partial TCP provenance checks remain incomplete.
Actual collector exits0 without force. CLI summary integrity/latest/reuse verified
without analysis rescan; raw size/mtime/listing preserved. Prepared read-only RPM
payload verifier (synthetic tamper tests) and explicit delivered-round CLI with
strict0/1/2scoped outcome codes. RHEL9 execution/ongoing Garage and multi-host review
remain later steps. Updated canonical file/workload/dashboard pages, review/handoff,
plan/verification/index and new rhel9_validation. Wintap instructions/audit stay in
its developer_docs. No private raw/host/config/credential evidence, field rollout,
Garage writes, runtime-pin/security/default-control changes or Lintap/Wintappy edits.

Wintap source bundle committed as03114f6;15changed production/test files across the
two repos match the qualified VM snapshot byte-for-byte. Same feature branches;
unrelated state/configuration work preserved. No PR or merge.

## [2026-10-25] code | TCP EOF/close tuple attribution before RHEL

User explicitly requested fixing TCP before RPM deployment. State callbacks had
replaced complete cached tuples with teardown's zero local port and reset sampling
clocks. Corrected complete-only existing-entry refresh, connect reset and unconditional
close cleanup; state callbacks cannot resurrect closed entries. TCP requested-entry
byte meaning and one-second sampling retained. Strict10-check actual-object regression
fails prior object/passes correction, including delayed EOF, both connected closes,
separate peerless listener close and empty socket caches. Final48turnover/15return
regressions also pass. SDK10.0.402 build0errors/177warnings;171managed,97dashboard,
21runner/CLI,7network-oracle tests pass. Seven changed production/test sources match VM.

Two fresh normal-ETL pilots, including final rebuilt managed/object pair, have0errors,
0missing checks/violations across five families and34passing receipt/hash/projection
gates. Both TCP provenance checks resolved. Final collector exit0 unforced in184seconds;
collector/observer/testhost inactive. Matching summary reuse/raw-snapshot preservation
pass. CLI remains2/yellow for independent execveat/native-helper skips and repeated-
Start count caveats. Added marker-gated TCP tuple contract1/lifecycle-hook receipt
and required it in later RHEL validation. Canonical network/receipt pages, index,
handoff/plan/verification/procedure updated; private evidence stays outside commits.
Native RHEL package validation and prior broader limitations remain open.

Wintap correction committed/pushed as `c4f6b1d`; Analytics validation/wiki companion
uses the same feature branch. Unrelated working-tree changes remain preserved.

## [2026-10-26] handoff | RHEL canary continuation

Refreshed the telemetry identity/data-quality feature status for computer transition
and replaced the stale dev handoff with a current continuation guide. The user reports
a newer native RHEL package deployment; two completed S3 rounds show declared endpoint,
file and process checks passing, with helper-dependent dedicated clone coverage. The
three-source provenance gate remains incomplete because `sched_exec` was not observed
despite the startup hook being reported attached. Two additional parallel overnight
rounds await stop, upload settlement and separate review; package-to-installed-payload
proof is not recorded. Updated brief, plan, verification, RHEL/network/runtime notes
and index. Persistent updates omit host identifiers, private storage configuration,
raw events and detailed runtime telemetry. No close-out or release claim; no source
changes or S3 writes.

## [2026-10-26] code | Resolve Wintap develop merge conflicts

User-approved merge of develop `c670c26` into the telemetry feature recorded as
Wintap `5afd320` (local, not pushed). The squash tree equals feature ancestor
`c951d21`; retained feature identity, clean state publication and DuckDB1.5.6.1
while removing a silent duplicate supply-chain/version property group. Declared
standalone MCP's Windows/Linux/macOS-build-host RID graph and regenerated its
lock after reproducing NU1004. SDK10.0.402 locked restores and managed builds pass;
113focused managed and6runtime-alignment tests pass. Native/package/runtime
qualification remains separate. Updated verification, plan, handoff and canonical
repo build note. Unrelated local state and untracked work excluded from the merge.

## [2026-10-26] code | Refresh Multipass development provisioning

User authorized Lintap script updates and a fresh development VM. Both launchers
now use qualified SDK10.0.402/CLI-Python DuckDB1.5.6, strict shared dependency
checks, running-kernel BPF tools, guest-native Python/build paths and updated
branch/build examples. Fresh Ubuntu arm64 creation and cloud-init pass; .NET build
has0errors/178warnings; forced rebuild compiles all12 tracer objects.24 packaging/
provisioning regressions pass on host and guest;5 validation-harness tests and its
synthetic mock command pass in the guest. Bash syntax, PowerShell AST and cloud-init
semantic parity pass. Updated Multipass guide, canonical repo page, feature plan/
verification and index. Live sensor/package acceptance is separate.

User subsequently reported successful Debian package builds and authorized
commit/push of the provisioning changes and companion wiki notes. This is
operator-reported build success; package installation/runtime results were not supplied.
