# Wintap Ecosystem Wiki Index

WindowsShell ETW replacement: [[wiki/work/windows-shell/brief]], [[wiki/work/windows-shell/design]], [[wiki/work/windows-shell/implementation_plan]], [[wiki/work/windows-shell/interview]], [[wiki/work/windows-shell/references]] and [[wiki/component/windows-shell-sensor]]. Microsoft.Windows.Console.Host ETW collection replaces the helper/polling path; payload fields and dynamic Parquet integration remain. Build/57 focused tests and 380 nearby regressions pass; integrated service acceptance is pending in [[wiki/work/windows-shell/verification]].

Master catalog of all pages. Updated by the agent on every ingest.

---

## Rollup

DBT source-aware validation: [[wiki/work/dbt-source-validation/verification]] —
local/split/S3 inputs, explicit named AWS profile selection, no placeholder directory,
partition-scoped DuckDB preflight, offline dashboard checks. Combined SELinux/source
validation now passes 286 regressions; historical config failure does not reproduce.
Combined release gates: [[wiki/work/selinux-dbt-pipeline/verification]] — required
PR review, full split-local/authenticated-S3 builds, temporary network-ID consumer
qualification, and S3 pull-helper hardening.

Package release policy: [[wiki/workflow/package-release-versioning]] — shared 7.0
release identity, format-specific Debian/RPM/MSI encoding and build-to-install checklist.

Multipass development refresh: [[wiki/repo/lintap-supporting-repo]] — fresh Ubuntu
arm64 provisioning verifies SDK10.0.402, DuckDB1.5.6, all12 tracers, managed build,
24 packaging/provisioning regressions and5 validation-harness tests. A later Bash
provisioning repair uses pip after a reproduced uv HTTP stall, avoids recursive
ownership changes on host mounts, bounds failure diagnostics, and passes the fresh
VM dependency gate plus 26 focused packaging/provisioning tests. The repaired VM
also produced and structurally verified a native arm64 `7.0.1~beta.1-1` Debian
package; install and runtime acceptance remain pending.

Develop merge maintenance: Wintap `5afd320` (local) preserves feature semantics
and fixes standalone MCP's multi-RID lock graph;113focused managed tests and
6runtime-alignment checks pass. See
[[wiki/work/wintap-telemetry-identity-and-data-quality/verification]].

**Telemetry-quality retrospective:**
[[wiki/work/wintap-telemetry-identity-and-data-quality/brief]] — the expanded scope
beyond .NET10: identity,network semantics,downstream precision/counters and delivery.
Read [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]] for concise
proof and limits;[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]]
for the current cross-computer continuation. RHEL package deployment and two initial
S3 canary rounds are reported/reviewed; `sched_exec` provenance, independent payload
proof, and two parallel overnight rounds remain open. This is not production readiness
or historical-loss closure. Detailed
audit payloads are uncommitted;archive provenance is retained,not loaded by default.

RHEL 9 package preparation: [[wiki/repo/lintap-supporting-repo]] — canonical Lintap
guide now selects SDK 10.0.402 and provides operator-assisted prerequisite/build
steps; bounded operator-assisted RHEL 9 package/capture/shutdown and fresh DBT smoke
pass. A newer package deployment and initial canary rounds are reported; independent
payload proof and full live/multi-day qualification remain pending.
Upgrade closure: [[wiki/work/wintap-telemetry-identity-and-data-quality/runtime_alignment_plan]]
— all 13 C# targets and active package/provision/run defaults align with .NET 10;
exact SDK 10.0.402 is enforced. Native self-contained RPM smoke passes by operator
report; other package modes/platforms and broader acceptance remain pending.

Canonical context:
[[wiki/concept/wintap-ecosystem-glossary]],
[[wiki/concept/telemetry-identity-and-endpoint-orientation]],
[[wiki/concept/collector-process-telemetry-and-collection-boundaries]],
[[wiki/concept/filetime-derived-timestamp-precision]].
Open data defects:[[wiki/diagnostic/duplicate-agent-id-and-os-family]].
Historical audit:[[wiki/diagnostic/sample-db-runtime-attribution-audit]].
Research proposals:[[wiki/work/host-process-identity-patch/investigation_mitigation_plan]],
[[wiki/work/host-process-identity-patch/grouped-retry-design-notes]].

Clone follow-up: [[wiki/work/improve-lintap-data-quality/clone-validation-plan]];
[[wiki/work/improve-lintap-data-quality/clone-validation-results]] (Ubuntu arm64
thread/clone3 fixes, duplicate-Start evidence, resolver-ordering regressions).

Durable startup evidence: [[wiki/schema/runtime-capability-receipt]];
[[wiki/work/improve-lintap-data-quality/runtime-capability-verification]].

Clone default-TRUE acceptance: [[wiki/work/clone-default-true/verification]];
RHEL transfer: [[wiki/work/clone-default-true/dev_handoff]].

Field-friendly named process/file/network stimulus, now extended with bounded
same-PID exec/argument/failed-attempt/Refresh cases, and **root-owned field-host S3
quick start**: [[wiki/tool/named-telemetry-smoke-workload]] — persistent user-created
venv, explicit sudo Python/DuckDB, `--smoke-data-root`, automatic `raw_smoke_test` upload and
dashboard validation. The one-shot entry point lives in the Wintap source checkout as
`devtools/telemetry_smoke_workload.py`; there is no current `telemetry_smoke_test.py`.
Visual workflow: [[wiki/workflow/live-collector-validation]] — editable two-page
draw.io diagram for **live-collector validation** and recurring telemetry canaries.
Open-ended disposable-host stimuli with uploaded ground-truth snapshots:
[[wiki/tool/periodic-telemetry-soak-runner]] (pilot first; DBT smoke joins deferred).

Smoke dashboard **first-time configuration and launch**, results / cross-host run manifests:
[[wiki/tool/smoke-test-results-dashboard]];
[[wiki/work/smoke-test-dashboard/implementation_plan]];
[[wiki/work/smoke-test-dashboard/verification]].
Dashboard supports private configured Garage/S3 reads as well as mounted datasets;
all-round summaries persist separately beside data, not under raw telemetry.
Overview now reads manifests only; Canary Tests and Dev-time Tests pages use explicit
validation. One-click canary-round observations and passive HOST startup comparison
expose coverage gaps without certifying capture. Initial S3 rounds show TCP Accept,
UDP and endpoint observations; dedicated native clone passes with the optional helper.
`sched_exec` source provenance and overall completeness remain unresolved.

Recent Host Activity dashboard: [[wiki/tool/recent-host-activity-dashboard]] —
standalone Streamlit direct-S3 view using DBT's existing dataset/AWS environment
variables, without invoking DBT. It defaults to a rolling 12-hour range and now
supports arbitrary inclusive UTC `dayPK/hourPK` ranges (warning above 24 hours),
with lazy/chunked listing and the existing fail-closed budgets. A bottom-of-sidebar
box shows effective non-secret environment settings. The default file-metadata
mode lists object keys/sizes (no Parquet reads), parses filename Win32 FILETIME
as collect time,
and reports per-host counts and sizes; missing per-host buckets are zero-filled
in both chart modes, but zeros are not completeness evidence. Raw-row DuckDB
analysis remains optional. Chart hovers show UTC time, host, and the selected
metric. For `raw_process`, an explicitly experimental likely-user-activity
view counts distinct Start-event process names per normalized user and host in
fixed 15-minute UTC buckets after small deny-lists; it is not session detection
and renders a one-host user/time heatmap. It is a barely acceptable temporary
proxy; [[wiki/todo/linux-interactive-session-feed]] tracks a real Linux
session/logon feed. The suite now passes 59 offline tests.
Pinned local v1 Status/raw-intent Runs need no ledger/lock/SDK/data reads;
Partitions now provides a read-only 42-complete-day raw/compacted hourly
presence heatmap with a full-24-hour compaction denominator and overlap details.
Full catalog/timeline, compacted/entity access and managed live/coordinated
lifecycles remain pending.
Live metadata-mode performance
remains unverified. The row mode retains family-aware timestamps and guarded
exact `raw_process_file` aggregation (7.9 million rows to 479 points in about
20 seconds); standard families retain the 2-million-row cap.

Active iterative workflow: [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief]] and [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan]] — Phase 1 relocates HostActivity/configuration tests and classifies PyUtil SQL contracts; 59 app/17 representative PyUtil cases pass and all 224 selected PyUtil identities are preserved. The sensor milestone repairs Linux names, adds observation timing and periodic Refresh, and labels procfs command-line quality. The latest bounded Linux units distinguish exec attempts from successes, retain executable-path evidence, label Stop exit-value quality, and preserve Stop kernel occurrence/receipt timing without changing identity or `EventTime`. `sfx-07` passes 4/4 focused, 92/92 combined and 50/50 live assertions across 3,634 rows and 47 files. Scope now includes the latest multiple-`process_name`/same-PID finding: Linux is the confirmed primary behavior because repeated exec can preserve one `PidHash`; Windows is a negative-control platform where same-hash name changes should first be treated as identity, snapshot/enrichment, replay, or deduplication anomalies. The plan first separates PID reuse from multi-image observations within one `PidHash`, then measures downstream arbitrary name/path selection. Refresh is a candidate stronger source for current image at scan time, not an automatic lifetime-image override; separate current-state and lifetime views are proposed before DBT/schema changes. Population analysis will distinguish observation volume from lifetime, host-day, host, and recurring-cause prevalence, with stratified feedback and holdout validation before tuning. The `any_value` work is column-specific: the pinned audit inventories 73 source-SQL text matches, and its six new synthetic contract tests pass within a focused 31-pass/one-skip suite; retain candidates only where group invariance proves equivalence, expose conflicts where needed, and replace ordering-sensitive paired features such as name/path. Process-lifetime initial/latest executable policy, immutable argv, BPF truncation/status changes, wait-status decoding, full `EventTime` migration and native Windows acceptance remain open in [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].

Linux test continuation: [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan#Current Linux Tranche — Test Development While Captures Are Pending]] — destination passes 59 HostActivity/7 parser controls; approved isolated uv environment passes 17 PyUtil cases and preserves 224 identities (4 unit / 220 contract). The opt-in bounded readiness helper passes 18 synthetic controls; the existing RHEL database is readable while raw is empty. That path was a one-time bootstrap sample and is not a future raw-data gate. Seven SmokeTests cleanup slices preserve all identities: 85 contract cases, one default-on/explicitly-opt-out localhost transport case, and 12 UI cases now live under purpose-specific packages. Full discovery passes 98/98 with no root forwarding modules. Later validation/PyUtil/coordination cleanup remains open, with no historical-data repair or sensor-correctness claim.

Wintap test extension: [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis]] and [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]] — approved static draft adds unit/synthetic traits and five moves in the shared feature checkout; unchanged bodies, 63-file inventory, fixture access, and build inputs are source-checked. The human explicitly deferred the Windows baseline; no managed build/discovery/run is claimed. See [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]]. Platform-project ownership remains open in [[wiki/tension/wintap-test-platform-boundaries]].

New-system continuation: [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]] — reviewed Analytics `0f8b414`, Wintap `123bd70`, and PyUtil `564ec43`; separate test-cleanup and sensor-preparation prompts, commit/evidence transfer checks, pending Windows gate, and next TC-03 capture handoff. Use the latest Analytics feature-branch tip for the updated handoff; git-ignored audits still need separate transfer.

Test-suite navigation and refactor plan: [[wiki/overview/test-suite-organization-and-classification]] — inventory, purpose/execution taxonomy, proposed filesystem, coordination/entity overlap review, and staged move/archive rules. Partial first-cut moves are implemented; no assertions or historical evidence have been deleted.

Quality follow-up: [[wiki/work/wintap-telemetry-identity-and-data-quality/quality_followup_analysis]]
— current-source Accept emission and UDP memory-domain defects, live incomplete UDP
tuples, source-aware repeated-Start accounting and five synthetic validator blind spots.
Authorized follow-up: [[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]]
— stronger dashboard assertions, source-controlled Accept/UDP return corrections,
distinct UDP mode/endpoint and per-path manifests, actual-object15-check VM comparison,
and159 shared managed tests. Deployed-object provenance and broader capture acceptance
remain open; no field rollout.
Approved greenfield projection follow-up added nullable process source and preserved
Linux path case. Subsequent producer work resolved the relative/cwd Delete and partial
TCP endpoint observations in scoped qualification; Wintappy's separate case-folded
file_id remains open.
Senior review: [[wiki/work/wintap-telemetry-identity-and-data-quality/advisor_review]]
— confirmed relative-unlink path attribution and two reproduced validator blind spots;
recommends a bounded corrective bundle before the next package qualification.
That user-approved bundle is now Ubuntu-qualified:97dashboard/20runner/171targeted
managed tests,48turnover/15return actual-object checks, exact relative/cwd Deletes
and live case-only sensor keys pass. Subsequent authorized TCP repair preserves
complete cached tuples/sample clocks through teardown: strict10-check actual-object
regression and fresh normal-ETL TCP provenance checks pass; all34 focused gates pass.
CLI remains incomplete for independent coverage skips/count caveats; broader
Windows/logging limitations are recorded. Current status and next actions:
[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]].
RHEL payload verifier and post-delivery procedure:
[[wiki/work/wintap-telemetry-identity-and-data-quality/rhel9_validation]].

Accepted durable evidence plan: [[wiki/work/smoke-test-dashboard/durable-evidence-plan]]
(pidstat-style parquet transport, partitioning and dashboard severity overview).

Retrospective umbrella feature: [[wiki/work/linux-capability-smoke-triage/brief]]
(Linux collection capability evidence, Clone defaults/correctness and smoke triage;
same existing branches, feature-only commit/PR scope).

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/metrics]] | high | Cross-feature Velocity rollup: one row per closed feature (lead time, solo estimate, Feature Velocity ± uncertainty, comparability flag, metrics link); Portfolio Velocity pending N≥several with trailing window ≥ 4× median lead time. |

## Tension

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]] | medium | Preserves the unresolved boundary between raw ETW/sysdig/eBPF producer details and stable WintapAPI semantics. |
| [[wiki/tension/refresh-republication-vs-durable-process-context]] | medium | Open refresh-volume versus durable historical context tradeoff; hybrid reconciliation/context-closure proposal, no selected cadence. |
| [[wiki/tension/linux-process-lifecycle-vs-exec-attempt-observations]] | medium | Open tradeoff between scheduler-primary process/image lifecycle and syscall attempt/argument evidence; separate semantics and measured costs remain to be decided. |
| [[wiki/tension/linux-file-path-case-projection]] | high | Resolved sensor projection: approved greenfield producer-case preservation; separate Wintappy lowercase-derived file_id remains a downstream limit. |
| [[wiki/tension/research-flexibility-vs-production-hardening]] | medium | Explains the research-first posture and flags hardening gaps such as unrestricted proof-of-concept MCP SQL access. |
| [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] | medium | Captures tradeoffs between Windows ETW, Linux eBPF/sysdig support paths, raw sensor Parquet, and cross-platform semantics. |
| [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]] | medium | Captures the open mismatch between Wintappy's canonical DuckDB-only DBT output and Wintap-Analytics' documented expectations of published stdview-* parquet datasets. |
| [[wiki/tension/raw-sensor-compaction-publication-vs-glob-readers]] | high | Resolved by scope change: fixed-hour writes and manual cleanup accept visible partial output; atomic publication is not required. |
| [[wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint]] | high | Dissolved: ignored conditional PUT remains an endpoint observation, but reservations/manifests were removed. |
| [[wiki/tension/dbt-arbitrary-representatives-vs-compaction-equivalence]] | high | Resolved by human acceptance: existing ANY_VALUE quality debt is non-blocking for compaction; bronze/schema/build gates remain and affected downstream drift is reported. |
| [[wiki/tension/native-macos-readers-vs-descendant-shutdown]] | medium | Human accepts best-effort native-Mac process-group release for normal completion, with escaped-descendant risk explicit and reservation retention on timeout/supervisor death/uncertain group state; no VM/Docker prerequisite. An isolated candidate passes 12 actual-Mac synthetic lifecycle controls; broader DBT/data/S3/service platform acceptance remains open. |
| [[wiki/tension/private-gateway-connection-identity]] | high | Held after refinement: both gateway identity slots are empty, loopback uses hostname context, non-loopback uses `public`, and a future symmetric private-network namespace remains deferred. |
## Decision

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]] | high | Accepted fixed hours/skip/manual cleanup; subsequently approved optional validated UTC-prefix deletion and unioned raw/compacted DBT input. |
| [[wiki/decision/raw-sensor-compaction-immutable-window-roots]] | high | Historical UUID-generation approval, explicitly superseded by fixed hours and manual cleanup. |
| [[wiki/decision/wiki-scope-cross-repo-wintap-focused]] | high | Records the decision that the wiki is cross-repo but prioritizes Wintap sensor internals, WintapAPI, Esper, and Wintap data analysis. |
| [[wiki/decision/feature-work-artifacts]] | medium | Defines the optional feature-work module: store LLM-assisted feature briefs/design/verification under `wiki/work/<feature>/` and promote durable facts into canonical pages. |
| [[wiki/decision/process-identity-attribution-contract]] | high | Migrated Wintap ADR locking the process identity and attribution contract: core-owned PidHash/ParentPidHash, flat event-time fields, durable Stop/parent backfill, and DuckDB as the starting substrate. |
| [[wiki/decision/test-project-structure-and-first-test]] | high | Migrated Wintap ADR choosing per-target xUnit test projects, standing up `tests/Wintap.Tests/` first, and making the first test a real `WintapMessage` constructor assertion. |
| [[wiki/decision/consolidate-developer-wiki-into-analytics-wiki]] | high | Records the decision to retire `retired developer wiki`, make this Analytics wiki the single Wintap ecosystem knowledge base, and keep Wintap instructions/audits in `../wintap/developer_docs/`. |
| [[wiki/decision/ai-velocity-roi-mini-lab]] | high | Per-feature velocity/ROI mini-lab, revised to v2.1 (2026-08-19, post external review): headline **Velocity** = solo-hours / (5.714 × days) in Feature and Portfolio views, forced-counterfactual sealed Q1 under the three-question ratchet, point-plus-uncertainty reporting, frozen-criteria/availability-finality/comparability guardrails, per-unit quality loop, attention proxy as coverage-annotated diagnostic, never-gates rule. |
| [[wiki/decision/platform-runtime-data-root-defaults]] | high | Records that unconfigured Wintap deployments use the OS defaults owned by Env.cs while explicit programmatic, environment, and JSON overrides remain supported. |
| [[wiki/decision/separate-data-and-runtime-roots]] | high | Accepted layout decision: durable `raw_sensor` data and host-local runtime state use independently configurable roots; Linux defaults are `<data-root> and <runtime-root>` with no automatic migration. |
| [[wiki/decision/canonical-five-tuple-connection-identity]] | high | Defines semantic `ConnId` as hostname context for loopback or `public` otherwise plus a direction-independent five-tuple, keeps exact preimage encoding private to sole .NET generation, and requires downstream passthrough. |
| [[wiki/decision/registry-provider-strategy]] | high | Accepted (2026-08-25, session-handle sub-decision OPEN): manifest-only Windows registry collection via an undocumented Microsoft-Windows-Kernel-Registry capture mode (4-byte 0xFFFFFFFF EVENT_FILTER_DESCRIPTOR at EnableTraceEx2) — standalone mechanism record with the probe matrix, sticky-global-state finding, KCB-correlation negative result, and framed session-handle options. |
## Concept

Process hash contract: [[wiki/decision/process-hash-inputs-and-single-definition]]
— hostname/PID/canonical-start only, no agent UUID, one formula; `pid-v2` source
patch and host-bound agent state: [[wiki/work/host-process-identity-patch/verification]].

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/concept/windows-attribution-and-file-path-correctness-contracts]] | low | Sanitized historical correctness contracts: attribution metrics, stable identity, Windows routing/maintenance boundaries, timestamp regressions, validation gaps, and approved FILE-path design; current implementation not reverified. |
| [[wiki/concept/llm-assisted-feature-workflow]] | medium | Lightweight workflow for LLM-assisted feature work (interview → brief → references → design → spike → plan → handoff → verification → closeout), with the interactive interview protocol, sealed metrics questions, invocation phrase, and promote-to-canonical operating rule. |
| [[wiki/concept/feature-work-template]] | medium | Full markdown skeletons for every `wiki/work/<feature-slug>/` artifact, including optional metrics files that open with plain-language Results and keep canonical fields under Technical Record; only `brief.md` is required. |
| [[wiki/concept/metrics-template]] | high | Defines the parseable `wiki/work/<feature-slug>/metrics.md` format: plain-language **Results** (estimated delivery speed, plausible range, confidence and reason) followed by the canonical Velocity YAML under **Technical Record**, plus availability, comparability, sealed estimates, per-unit rows, cost, and optional attention diagnostics. |
| [[wiki/concept/velocity-metric]] | high | The approved Velocity definition plus the wiki presentation convention: results state estimated multiples of one solo developer's pace, an “about X×–Y× faster” plausible range, and confidence with a direct reason; technical formula, Feature/Portfolio views, guardrails, and parallelism dividend remain unchanged. |
| [[wiki/concept/agentic-ebpf-probe-development]] | low | Unverified brainstorming survey of agentic eBPF probe tooling (MCPtrace, GPTtrace, eunomia-bpf) and additional EDR reference projects (Sysmon for Linux, Bombini). |
| [[wiki/concept/lintap-cpu-unit-conventions]] | high | Defines raw pidstat CPU as core-summed percent, normalized DBT aliases and dashboard labels, host normalization formula, and raw-schema compatibility rule. |
| [[wiki/concept/telemetry-identity-and-endpoint-orientation]] | high | Foundational agent_id, pid_hash and canonical five-tuple conn_id scopes; identity versus direction, socket roles and connection lifetimes. |
| [[wiki/concept/durable-process-context-and-stream-table-enrichment]] | medium | Durable entity state/stream-table concepts; first-round S3 Parquet hourly writer and DBT context implemented, broader refresh/changelog proposals remain open. |
| [[wiki/work/raw-sensor-file-aggregation/process-context-options]] | speculative | Optional compactor-fed process state for ground-truth datasets: runtime-spanning inputs, live/recent references plus ancestor closure, reachability GC and dataset checkpoints; no experiment-specific retention or approved scope expansion. |
| [[wiki/work/durable-process-entity-manager/brief]] | medium | Accepted first-round S3/hourly/DBT direction; implementation authorized with synthetic orphan-breakpoint tests. |
| [[wiki/work/durable-process-entity-manager/design]] | speculative | Historical design record plus concrete implementation choices; no initial GC, entity-before-delete ordering, JSON evidence and separate DBT context. |
| [[wiki/work/durable-process-entity-manager/implementation_plan]] | speculative | DPE-01–05 first-round slices completed on synthetic local/S3 fixtures; production capacity/bootstrap/exclusion still gates. |
| [[wiki/work/durable-process-entity-manager/verification]] | medium | Two isolated three-day rounds reproduce the DuckDB 2.0.0 SQL reducer, seven-snapshot bootstrap, SQL verification, DBT pass results and row/count compatibility. Each finds only 2 root-reached seeds; historical ancestry completeness and production rollout remain unqualified. |
| [[wiki/work/durable-process-entity-manager/dev_handoff]] | medium | Intermediate handoff for on-prem continuation: measure laptop/VPN versus on-prem performance; keep Garage debug-log reproduction optional; preserve unknown deletion cause and historical/entity/production gates. |
## Component

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/component/windows-sensor-service-internals]] | high | Documents Wintap service startup, platform subscription dispatch, Windows ETW sensor ordering, and EventChannel routing. |
| [[wiki/component/wintap-api-shared-data-model]] | high | Canonical page for the WintapMessage envelope, domain objects, plugin contracts, and EventChannel enrichment boundary. |
| [[wiki/component/wintap-recorder]] | high | Captures WintapRecorder recording-session control, registry mode flags, Parquet monitoring, and merge behavior. |
| [[wiki/component/plugin-and-mcp-samples]] | high | Documents plugin discovery/contracts, sample event subscriber behavior, and research/POC MCP SQL tooling caveats. |
| [[wiki/component/process-table-retention]] | high | Process retention/reconciliation plus the bounded delayed-event identity cache; 10h23m field gate passed, with the owning Wintap commit ID still pending. |
| [[wiki/component/fileops-event-pipeline]] | high | Kernel-to-parquet FileOps contracts, adaptive ring notification, bounded attribution, dedicated serializer draining, coordinated durable shutdown, and the remaining FD-path cache follow-up. |
| [[wiki/component/sensor-upload-cache-pipeline]] | high | Canonical page for the shared upload/cache pipeline: merge cycle, type-agnostic ride-along sweep contract, delete-after-upload (fixed 2026-08-17), prune backstop, hang-recovery scoping, deployment prerequisites, and the small-file consolidation follow-up. |
| [[wiki/component/sensor-health-monitor]] | high | Canonical page for the always-on Windows egress QA layer (shc feature, closed 2026-08-25): InspectForHealth hook on both egress branches + MemoryMap bypass, five constant-time checks, six-stream 5 s liveness watchdog, aggregated Wintap.log reporting, config keys, and the shc-03 QueryDosDevice drive-map/fromNative accuracy fix. |
| [[wiki/component/registry-sensor]] | high | Canonical page for the manifest-only Windows registry sensor (wrc feature, closed 2026-08-25, commit 1f66a47): undocumented capture-mode enablement (Option A guarded reflection, TraceEvent 3.1.23 pin), 0x5300/0x5700 keyword mask, capture-loss canary + 5-min re-assert, six-REG-type decode with pre/post values, CreateKey Join(BaseName, RelativeName) path assembly, and the 18-column parquet contract incl. Reg_DataType/Reg_PreviousData/Reg_PreviousDataType. |
| [[wiki/component/powershell-sensor]] | medium | Default-disabled native ETW sensor for 4104 v1 from Windows PowerShell and PowerShell Core; implemented on Wintap feature/develop, not yet Wintap main as of 2026-11-12; raw output exists but DBT staging and live load/loss qualification remain absent. |
## Data_model

| Page | Confidence | Summary |
|------|------------|---------|
## Event_type

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/event_type/process-events]] | high | Defines birth-based process identity, Windows ETW lifecycle/startup reconciliation, Linux clone/exec boundaries, and the uncommitted additive observation-time/UTC-aligned periodic Refresh candidate with ETL implications and remaining live/native gates. |
| [[wiki/event_type/file-events]] | high | Defines ETW FileIO producer behavior, file-key path resolution, feedback suppression, and 10-second aggregate ETL semantics. |
| [[wiki/event_type/network-events]] | high | Defines TCP/UDP ETW producer behavior, endpoint fields, reversible TCP caveats, and 10-second network aggregate ETL semantics. |
| [[wiki/event_type/powershell-events]] | medium | Script-block event contract, fragment/attribution semantics, sensitivity, `raw_powershell` output, and no dedicated Wintappy DBT staging model found. |
## Pipeline

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/pipeline/nesper-esper-event-stream-processing]] | high | EventChannel/Esper semantics plus synchronous dispatch, serializer backpressure, dedicated FileSerializer draining, and producer-to-parquet shutdown ordering. |
## Schema

| Page | Confidence | Summary |
|------|------------|---------|
## Tool

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/tool/streamlit-app-review]] | medium | Source-only review of five apps: HostActivity availability, SmokeTests validation, legacy DataQA lifecycle/DLL QA, EDA graphs, and CALDERA report browsing. DataQA/EDA shell consolidation candidates; concrete dependency/configuration gaps, distinct metrics and unverified usage/runtime relevance. No retirement decision. |
| [[wiki/tool/wintap-workbench]] | high | Summarizes the Angular Workbench UI, feature routes, SignalR/EPL query path, and query-state boundary. |
| [[wiki/tool/durable-process-entity-manager]] | high | Optional fixed-host snapshots/no GC, hourly checkpoints and DBT ancestry; submitted explicit-v5 Linux entity launch/history/clean-original recovery preserves raw cursor and DRAINING. Interrupted-publication repair and broader qualification remain open. |
| [[wiki/tool/recent-host-activity-dashboard]] | high | Raw metadata/optional row viewer plus pinned manual advisory v1 Status/raw intent Runs; 46 offline tests pass. Partitions/history/certificates unavailable; full catalog and managed jobs pending, no deployment. |
## Workflow

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/workflow/wintap-etl-data-flow]] | high | Local-only raw Parquet → DBT quick start, detailed editable shared-S3 ETL diagram and large-type CONOPS infographic: optional compaction, raw_sensor + compacted UNION ALL, four storage concepts, separate durable process entities, bronze/silver/gold and Makefile targets. |
| [[wiki/workflow/future-experiment-analysis-workflows]] | high | Tracks first-class analytics topics including ACME4 Explore, DuckDB view construction, process trees/paths, process-centric SQL, and network joins. |
| [[wiki/workflow/process-ancestry-completeness-qa]] | medium | First-round DBT terminal/context QA implemented; broader root fraction, concentration/K95 and independent validity-audit guidance remains separate. |
| [[wiki/workflow/lintap-dev-field-workflow]] | high | The Lintap dev/field split: field-host clones are read-only by policy (reviews transcribed dev-side), diagnostics bundles must be self-sufficient, deploys pull and rebuild tracers on-host, pushes require the human's credentials, and agent memory must mirror into the wiki. |
| [[wiki/workflow/rhel8-rpm-build-prerequisites]] | high | Preflight and software prerequisites for a native RHEL 8 x86_64 Lintap RPM build, including exact .NET SDK 10.0.402 and the current BTF/CO-RE limitation. |
## Repo

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/repo/wintap-primary-sensor-repo]] | high | Orientation page for the primary Wintap implementation repo, active source tree, core layers, and wiki source-of-truth role. |
| [[wiki/repo/wintap-analytics-host-repo]] | high | Explains Wintap-Analytics as the wiki host and DuckDB/Jupyter/NetworkX-oriented Wintap data analysis repository. |
| [[wiki/repo/lintap-supporting-repo]] | high | Clarifies Lintap's supporting role for Linux TeleTap/eBPF, legacy sysdig, raw sensor Parquet, and packaging/dev workflows. |
| [[wiki/repo/wintappy-pipeline-repo]] | high | Documents Wintappy (Wintap-PyUtil) as the canonical DBT/DuckDB bronze/silver/gold pipeline, its raw_sensor input contract, its legacy Python ETL, and its direct code dependency from Wintap-Analytics' Streamlit tooling. |
## Diagnostic

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/diagnostic/linux-capability-data-quality-matrix]] | medium | Linux build/runtime/distro evidence and per-sensor CO-RE/fallback matrix; explains missing/placeholder fields, thread/identity/byte-count caveats, output permutations, and a recommended dataset capability receipt. |
| [[wiki/diagnostic/lintap-rhel8-selinux-s3-policy]] | medium | Operator-reported RHEL 8 SELinux denials for Garage TCP upload and raw_sensor partition cleanup; custom port labeling, AVC triage, and host-local policy build/deploy notes. |
| [[wiki/diagnostic/nesper-repro]] | high | Documents the standalone Fedora/shared-mount NEsper repro and the evidence that Bad IL range failures are output-location related. |
| [[wiki/diagnostic/dependency-inventory-and-update-status]] | medium | Inventories Python, npm, and .NET dependency manifests across the ecosystem and records observed update availability with tooling caveats. |
| [[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]] | medium | RHEL 8 field findings: clone sensor attaches (Fedora failure doesn't generalize), the fork-without-exec warning signature (parent = child−1), and a suspected ~500-700 forks/sec storm with event-processing lag under investigation. |
| [[wiki/diagnostic/windows-sensor-sweep-queue]] | high | Consolidated defect/finding queue the follow-on Windows sensor sweep feature opens from (19 items across shc and wrc; item 6 resolved by wrc-06): WintapLogger sync-context capture and live-log truncation, Env.SetDataRoot fixture guidance, the health check's first live catch, dead Serializer.Listen and WintapETL handlers, WintapAlert self-PID drop, TranslateTransientPath authority bug, QueryDosDevice consolidation, MemoryMap reroute question, registry attribution burstiness + stop_without_start growth, the Read-event data gap, capture-flag unknowns, and preserved registry warts. |
| [[wiki/diagnostic/windows-attribution-validation-executive-summary]] | low | Sanitized historical summary of 46 developer-archive files: architecture, reported tests and attribution metrics, improved File unresolved rates, unresolved Registry/validator reliability, and evidence limitations; original source references omitted at Architect request ahead of archive deletion. |
| [[wiki/diagnostic/linux-tcp-investigation-2026-06]] | high | Historical June Linux TCP investigation with October source and Ubuntu 24.04 live validation: attachment/PID/protocol/rundown work is present; TCP AgentId, state template, and watchdog defects are resolved; no resolver negative cache was justified. |
| [[wiki/diagnostic/duplicate-agent-id-and-os-family]] | medium | Two hosts share a raw UUID also present in initialized local state; Linux metadata mislabeled Windows by DBT/legacy SQL. Evidence and proposed remediation/regression gates. |
| [[wiki/diagnostic/process-tree-context-completeness]] | medium | Anonymized six-host short-window audit: root reachability, concentrated ancestor breakpoints, independent pidstat corroboration and provenance limits. |

## To-do

Priority finding intake queue: [[wiki/todo/index]] — tracks emerging bugs,
data-quality issues, and enhancements before promotion into a full deep-dive
feature folder. Current P1 items include [[wiki/todo/linux-process-name-exe-fallback]],
whose source repair is accepted while historical data lineage remains open;
[[wiki/todo/linux-process-executable-attribution]], where source rows now preserve
attempt-versus-success semantics and path-evidence origin but process-lifetime
selection remains nondeterministic in Wintappy's silver model; and
[[wiki/todo/lintap-linux-process-command-line-quality]], whose bounded Linux
source/status and clone-attribution slice is accepted while immutable exec argv
and deterministic DBT command-line semantics remain. The P1 OS metadata
correction in [[wiki/diagnostic/duplicate-agent-id-and-os-family]] tracks removal
of hardcoded `windows` labels and platform-derived, backward-compatible family
handling. The P2
[[wiki/todo/linux-nfs-process-network-attribution]] intake tracks the observed
SSH-on-NFS-tuple example, likely process-context attribution, and the need to
verify NFS-backed home and deployed tracer semantics. An untriaged enhancement,
[[wiki/todo/listening-socket-capture-and-modeling]], tracks process-attributed
listening-socket lifecycle capture and downstream modeling; priority and platform
scope remain open. [[wiki/todo/canonical-process-owned-network-grains]] tracks
canonical process-owned increment/connection grains, conflict visibility, and
network-observed process identity semantics for reusable analytics.
[[wiki/todo/unify-lintap-runtime-and-etl-configuration]] tracks replacing the
operator-facing `lintap.env` and `ETLConfig.json` split with one canonical
configuration while preserving local values across installer upgrades.
[[wiki/todo/transformer-five-tuple-connection-port-key]] finds no duplicate-port
call in available v7 history and traces the ACME4 workaround to unsorted producer
ID inputs. The absent historical build still prevents ruling on duplicated
persisted endpoints. The accepted target now preserves .NET as the sole generator;
DBT's exact JSON is not canonical; DBT and legacy raw-view rehashing are now
removed in the bounded source round, and local DBT passthrough qualification is
complete. Native Windows acceptance is deferred, not eliminated. Release uses a
clean cutover to newly collected data with no legacy migration or mixed-data
compatibility requirement.
The provisional P2 [[wiki/todo/lintap-rpm-amazon-linux-2023]] tracks the reported
failure of the current Lintap RPM to install on AWS Amazon Linux 2023; artifact,
error classification, and target-support boundary remain to be established.
The untriaged [[wiki/todo/raw-sensor-upload-time-partition]] tracks the shared
.NET gap between current merge-time partitions and the requested actual-upload
UTC partition contract.
The low-priority [[wiki/todo/daily-compacted-tier]] tracks a future verified
`compacted2/dayPK` roll-up, disjoint reader precedence, and late-arrival
handling; it is separate from the current hourly historical catch-up.
The approved high-priority test maintenance item is
[[wiki/todo/test-suite-reorganization]], which points to the staged
[[wiki/overview/test-suite-organization-and-classification]] plan.
The promoted P1 [[wiki/todo/periodic-process-refresh-listing]] records the
uncommitted UTC-aligned Linux/Windows candidate, hourly `HH:05` default,
collection-time observability and remaining native/live gates.
The promoted P1 [[wiki/todo/process-observation-time-separate-from-birth]] records
the additive raw/UTC observation fields independently of canonical birth/hash;
full legacy `EventTime` migration still requires coordinated resolver/ETL/consumer
work.

## Work

Linux implementation continuation: [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff]] — preserves reviewed Wintap TODOs, destination/transfer checks, existing test-cleanup work, Linux/Windows execution boundaries, and the small approved-unit/capture loop. The first source batch is implemented and synthetically qualified but uncommitted; native Windows, fresh capture and deployment authorization remain open.

Compaction status utility follow-on:
[[wiki/work/compaction-status-utility/brief]],
[[wiki/work/compaction-status-utility/design]],
[[wiki/work/compaction-status-utility/implementation_plan]] and
[[wiki/work/compaction-status-utility/verification]] — human-authorized isolated
implementation from Analytics `ee9c27a` / PyUtil `123b9d3`. Navigation, pinned bounded
manual advisory Status/raw intent Runs and explicit unavailable Partitions pass
46 offline controls/zero skips; separate-runtime genuine export read passes while
the synthetic producer lock stays held and fixture files remain unchanged. Activity
is still synchronous/raw-only and always Live diagnostic — uncoordinated. Reserved
is not delivery, `COMPLETED` is not certified, launch/finish/progress/entity history
are unknown and continuations are incomplete history. Full catalog/timeline,
compacted/entity reads and managed live/optional coordinated refresh remain pending.
The diagnostic exception never relaxes DBT, authoritative verification, ledger or
maintenance. No deployment, scheduling, real-dataset mutation, commit or push.

Scheduled DBT/compaction coordination:

**Approved priority — development end-to-end milestone (November 16):**
[[wiki/work/dbt-compaction-coordination/integration-milestone-plan]] — reviewed Linux
service/writer/entities and native-Mac reader are ready for an actual-data integration
attempt. The human clarifies that all sensor/raw/ETL deployments are developmental;
existing telemetry is expendable. Approved DCC-E2E-01 targets real delivery, cache
creation, hourly compaction and Linux/Mac DBT clients over successive hours, with
impact-based defect triage. Comprehensive recovery/old-data preservation and unchanged
full-suite repeats no longer precede the pilot; ownership/privacy/correctness stay.
Concrete runner/data/access/mutation scope remains to be selected in
[[wiki/work/dbt-compaction-coordination/isolated-qualification]]. The plan itself does
not claim execution or production acceptance. The confirmed 2026-10-25 22:00Z–
2026-10-26 01:00Z block has completed entity initialization and three no-deletion
hourly compactions; entity-aware Linux DBT passed against an immutable local snapshot
through a read-only localhost mirror (59 models/85 tests). This is offline replay only.
The two no-deletion continuation hours (01:00Z–03:00Z), followed by independently
verified deletion-enabled compaction through 19:00Z, have completed. The raw-only DBT
baseline for 04:00Z–05:00Z passed, with coarse and monotonic processing-throughput
samples recorded. The attempted 19:00Z tick left the ledger BLOCKED with an unresolved
writer after an observed-host/entity-expectation mismatch; the raw hour remains and no
retry or authority bypass occurred. The human clarified that any host with data in the
hour is valid, so the fixed expected-host rejection is a deterministic
implementation/requirements mismatch, not invalid input or a transient failure. Read-only review
confirmed two hosts in the failed raw hour; the additional host has process-event times
from the hour's beginning plus older history, not a demonstrated mid-hour arrival. The
PyUtil dynamic first-seen entity fix is implemented and fully tested; the blocked-run
recovery path remains unresolved. Coordinated DBT
awaits supported resolution and native-Mac DBT remains deferred. See
[[wiki/work/dbt-compaction-coordination/verification#Confirmed next block and entity-aware Linux DBT snapshot replay — 2026-11-16]] and
[[wiki/work/dbt-compaction-coordination/verification#Linux-only one-hour continuation — 01:00Z–02:00Z — 2026-11-16]] and
[[wiki/work/dbt-compaction-coordination/verification#Second Linux-only one-hour continuation — 02:00Z–03:00Z — 2026-11-16]] and
[[wiki/work/dbt-compaction-coordination/verification#Production-path runtime and throughput accounting — 2026-11-16]].
The approved Linux-runner assignment is in
[[wiki/work/dbt-compaction-coordination/dev_handoff#Active Linux-runner assignment — DCC-E2E-01]];
the human handles delivery. Strict upload-time UTC client enforcement and downstream
delayed-data semantics are separate later tasks, not pilot prerequisites.

**Current compaction boundary — November 17:** The earlier Linux qualification
reached 07:00Z after ten independently verified deletion-enabled ticks. A separate
fresh writer ledger then advanced 31 bounded cursor steps to 2026-10-28 02:00Z;
the primary ledger is healthy in `DRAINING` with no readers or waiting jobs. A
separate future-cursor, non-entity Linux reader completed a one-hour DBT build
with 140/140 resources and a readable local DuckDB output; its earlier broad
window failed on local disk capacity and remains recorded as such. The current
tranche is Linux-only: server-owned compaction, coordinator, ledger and Linux DBT
use the existing real S3 source from the oldest date forward in small chunks, with
completed test-data deletion allowed after verification. Mac DBT is deferred. The
M0 private-runner gate is replaced by exact-scope operational checks in
[[wiki/work/dbt-compaction-coordination/isolated-qualification]] and the detailed
[[wiki/work/dbt-compaction-coordination/verification#Second Linux-only live tranche — 2026-11-17]].

The plan now includes the downstream source-mode contract for raw-only,
compacted-only, mixed, DBT DuckDB and entity-aware reads. It scopes HostActivity
changes for source/coverage labeling, preserves SmokeTests as raw-producer-evidence
by default, and keeps legacy DataQA/EDA consumers behind an explicit compatibility
boundary. Synthetic raw-only, deleted-raw, compacted-only, overlap,
cumulative-authority and duplicate-count gates are required before compacted or
entity-aware consumer acceptance.

The resumed deletion-enabled Linux scope subsequently completed the 23:00Z–00:00Z
hour: authority generation 29 and its matching metrics generation are committed,
nine compacted objects are present, exact-hour raw objects are absent, and the
ledger is at 00:00Z in `DRAINING`. This is object-level operational evidence; the
hour's row-count parity was not independently measured in that readback. Native-Mac
DBT remains deferred.

**Historical submitted review / isolated native-Mac overlay (November 15):** PyUtil `123b9d3`
and Analytics `ee9c27a` include the Linux service/client/advisory, v4 retry and explicit-v5
entity launch/history/clean-original service paths. Worker-reported 71 strict-service/
307 service-affected Linux passes retain their narrow scopes. Independent submitted
source/report review authenticates 365 hashes; native portable smoke passes 76/zero
skips and a separately provisioned five-module rerun passes 169/25 reviewed Linux-only
skips with 83 unchanged identities. Native kqueue `NOTE_TRACK` returns `ENOTSUP`; the
restriction probe's prestarted helper enables a tiny genuine build/test but does not
qualify the client launcher. Separately, an isolated native process-group candidate is
wired to the coordinated client in local commit `c549424` (based on `1f4897a`);
12 actual-Mac synthetic lifecycle controls pass, as
do bounded 50-normal-exit and 20-same-group-child stress runs. This remains limited
lifecycle evidence, not real DBT/data, actual S3, service, representative-resource or
platform acceptance. Its focused Linux supervisor/client/lifecycle/local-route
cross-check passes 90 with 12 native-Mac-only skips and observes no Linux behavior
change; the prior service-affected gate was not rerun. Pending publication stays
producer-worker-owned; no new full latest-HEAD/S3/resource/dcc-02–05 acceptance.
[[wiki/work/dbt-compaction-coordination/verification#Native macOS process-group prototype — actual-Mac synthetic lifecycle]] and
[[wiki/work/dbt-compaction-coordination/verification#Independent submitted review and native-Mac feasibility — November 15]].
Prepared gated Linux/S3/resource procedure:
[[wiki/work/dbt-compaction-coordination/isolated-qualification]] — concrete private
environment/fixture/root/access/runner/ceiling approval is still required; no remote run.

**Historical implementation/qualification chronology:** the entries below preserve
their original frozen revision/scope, not claims that later interfaces remain absent.
[[wiki/work/dbt-compaction-coordination/brief]],
[[wiki/work/dbt-compaction-coordination/design]] and
[[wiki/work/dbt-compaction-coordination/dev_handoff]] — proposed once-per-minute Python
coordinator, local DuckDB ledger and S3 request/grant/release messages; S3-backed
DBT builds yield to an exclusive hourly writer. Local-only builds retain direct
execution with compaction and durable entity state optional. Companion design
includes an editable two-page draw.io sequence, cron/config, proposed code/runtime
artifacts, client wrapper and restart/recovery behavior. Developer handoff adds
five implementation units and acceptance checks, including the nominal 70-second
startup / 60-second release-observation polling budget.
Post-pull [[wiki/work/dbt-compaction-coordination/implementation-review]] records
four-root/checkpoint recovery requirements, snapshot validation/provenance findings,
and fresh focused regressions (38 standalone; 63 main passed, 1 skipped).
Initial worker feedback corroborated SQL validation/provenance defects and
recommended a repair milestone before ledger/protocol implementation.
Worker [[wiki/work/dbt-compaction-coordination/implementation_plan]] adds safety
prerequisites before real writer integration, followed by the five handoff units;
[[wiki/work/dbt-compaction-coordination/verification]] distinguishes independent
baseline reruns from imported probes and future concurrency evidence. Authorized
integrity/provenance work now repairs active SQL validation and original bootstrap
retention: 75 pre-fix regression failures, then 94 new tests pass; full suites pass
234 standalone and 315 main tests with opt-in skips. Local milestone commits are
PyUtil `7d2b7f8` and Analytics `739e64f`. Subsequent receipt-backed freshness is
implemented with rollback/forward-lineage and publication-intent regressions;
full R1 gates pass 266 standalone and 335 main tests. R4 adds immutable local phase
archives and original-generation exclusive checkpoint repair; 307 standalone tests
pass (two skips) and real cross-runtime repair passes DBT. R5's active-root routing
passes seven cases including direct full local `make dbt-build` with an unused remote
metrics override. Combined main passes 343 tests (three skips); final affected
cross-runtime checks pass 51 tests (one skip) including the directory-link durability
fix. R1–R5/dcc-00 prerequisites are regression accepted. Protocol/ledger library
passes 54 tests including abrupt-process WAL recovery; full main passes 397
(three skips), accepting dcc-01. The first controlled-clock tick slice passes
100 focused tests, including atomic message conflict handling and a child surviving
abrupt tick death; full main passes 443 tests (three skips). The subsequent Linux
supervision/evolving-clock focus passes 142 tests; full main passes 485 (three skips). dcc-02
remains open: integrated verified completion/cursor advancement, advisory status,
client and real-writer/runtime gates remain. Collaborative review reproduces a
grace-boundary admission defect during ingestion; slice A subsequently repairs it. The human
confirms atomic completion-evidence/run/cursor/admission-state COMMIT before grants.
The review also requires an allowlisted, non-secret effective execution/configuration
receipt bound to writer intent; local launch and separate verification now enforce
identity/privacy checks; local v3 normal completion exists, with service integration
still pending.
The earlier committed implementation snapshot is PyUtil `fe7fcb5`; its coordination-only
rerun passes 142 tests, without covering the known ingestion/grace defect. Both
repository snapshots were subsequently pushed and pulled for maintainer review
(Analytics `660b5a8`, PyUtil `fe7fcb5`). The updated implementation review confirms
R1–R5 repairs and records R6–R8 follow-through: independently reproduced grace
admission, authority-masked SQL regression tests and unguarded Linux assumptions.
Fresh macOS results: standalone 305 passed/2 failed/2 skipped; focused main
196 passed/3 failed/35 skipped. All five suite failures are platform-specific tests;
dcc-02–05 remain open in the plan.
November 14 completion planning selects Linux/macOS readers, a Linux writer,
fresh isolated actual-endpoint fixtures and initial 32 GB RAM / 64 GB disk sizing.
The [[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]]
orders review repairs, receipts/platform feasibility, independent completion,
service/client, audited recovery and qualification; reduced budgets require a
separate measured rerun, and implementation/acceptance remains pending.
Slice A's review follow-through passes 150 affected main and 215 affected standalone
tests; all 80 new SQL negatives fail when validation is disabled. Full standalone
passes 387 tests (two skips); full main passes 493 (three skips), before receipt implementation. Portable fsync
observations/platform guards do not establish macOS reader support. Slice B starts
with 23 missing-execution-API failures and eight active-path hardening failures.
The repaired receipt-bound revision passes 194 coordination tests, including real
local empty/destructive synthetic runs; all still block. Full main passes 537
tests (three skips). Partial slice C supplies separate read-only verification and
receipt/intent/shutdown authentication: 259 standalone and 204 main affected tests
pass after eight active-path repairs. Frozen verifier-foundation full regressions
pass 547 main tests (three skips) and 431 standalone tests (two skips), before ledger
integration. Ledger v2 now retains authority proofs, explicitly upgrades compatible
v1 state and requires verified initialization/fresh same-session checks before entity
admission or writer intent. Main entity verification uses the retained anchor without
changing it or permissions. Latest focus passes 236 main / 299 standalone tests;
frozen full authority regressions pass 579 main tests (three skips) and 439 standalone
tests (two skips), before completion/history work.
The ledger-v3 retained-history/normal-completion prototype passes 46 repaired
completion/upgrade and 24 additional semantic/compatibility/paging/secret controls,
before three final budget/clock red/green controls. Ten active failures precede
repairs. Full standalone passes 439 tests (two skips) on that final revision;
combined main focus passes 298 tests; full main passes 641 (three skips). Both full
regressions completed on the unchanged revision. This does not accept the service.
dcc-02–05 stay open.
**dcc-mac-baseline-01 passes** (corrective PyUtil `fab647f`, actual macOS arm64):
169 main passed/129 reviewed Linux-only skips; 267 standalone passed/zero skipped;
both exit 0, no timeout. All 22 pre/post-run identities, separate locked native
runtimes and 18 harness controls pass. Manifest/runtime hashes are unchanged.
Original `8ee714c` was blocked before both stages by the omitted main lockfile;
its evidence remains separate. R9's repair disposition and fresh results are in
[[wiki/work/dbt-compaction-coordination/implementation-review]] and verification.
Later reader-backend acceptance is separate:
[[wiki/work/dbt-compaction-coordination/macos-qualification]].
Finalized worker continuation:
[[wiki/work/dbt-compaction-coordination/dev_handoff#Worker continuation after the Mac review]].
Human subsequently authorizes Linux-first completion; native-Mac solution remains
with the native worker:
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]] — 34 Linux supervision
tests and three dependency controls pass; no actual-Mac backend is established.
Injected SDK scope/secret-exclusion tests make no endpoint requests; supported Mac
reader shutdown, S3, representative resource and integrated service gates remain open.
The then-uncommitted Linux overlay (now submitted in `123b9d3`) integrates service/client/root-aware
Makefile routing, same-lock verified completion and bounded atomic advisory exports.
Reader invocation/launch/shutdown and resolved transport repairs have 49 then 142
affected passes; the original two-request startup timeout remains historically
unattributed, with its ten-second wait unchanged. Narrow checkpoint maintenance
retains original exit-2 evidence, keeps repair blocked and requires independently
verified repaired resolution; intentional retry and general entity maintenance
remain unfinished. Intermediate controls pass 32 main/66 standalone plus nine extended
tests. The latest 261-identity source freeze has a full standalone pass of 460 tests/
two skips (191.79 s); affected main finishes with 303 passes/one missing-cursor
test-wrapper failure. The wrapper-only repair passes its real paging/corruption
control; combined rerun passes 304 tests in 715.34 s with all 261 identities unchanged.
Full main passes 755 tests/three skips in 1156.34 s; all 261 identities match after
notification, closing this revision's local regression, not broader Linux acceptance.
Current scope/results: [[wiki/work/dbt-compaction-coordination/verification#Checkpoint maintenance — narrow repaired-phase path, regressions pending]].
The subsequent deletion-only slice closes local regressions: real partial-deletion controls expose
exact-type/order, traversal, checkpoint-interference and retained-capture defects;
repairs now pass 33 main / 49 standalone focused tests with all 265 identities unchanged.
Renewed source/wiki/privacy audits pass. Affected standalone passes 203 tests with
all identities unchanged; full standalone passes 509 tests/two opt-in S3 skips with
all 265 identities unchanged. Affected main passes 515 tests/one explicit isolated-local
migration skip; full main passes 788 tests/three skips in 1492.66 s, with complete
reports inspected and all 265 identities unchanged after notifications. Retain this
baseline; new retry/entity source changes require separate evidence, tracked in
[[wiki/work/dbt-compaction-coordination/verification#Original-bound deletion recovery]].
Retry work now adds a narrow read-only raw-only prerequisite, without any permission
or cursor transition. Fixture-scope-masked results are disclaimed; corrected main
passes nine controls and standalone's late-prefix repair passes 45 extended controls.
Extended main exposes three accepted count-corruption defects; exact original-intent
totals are now bound, with repaired and frozen 33-main/45-standalone passes,
completed scoped review and a separate 269-identity freeze. Affected standalone
passes 248 tests; full standalone passes 554/two opt-in S3 skips, with all 269
identities unchanged after notification. Affected main passes 548 tests/one
isolated-local migration opt-in skip; full main passes 821 tests/three skips in
1602.08 s. Complete reports inspected and all 269 identities unchanged after each
notification; each full began only after its own affected checks. Combined read-only
preflight local gate closed, without retry permission or Linux acceptance:
[[wiki/work/dbt-compaction-coordination/verification#Retry preflight — prerequisite only, integration pending]].
The successor intentional-retry v4 ownership slice is active but not accepted;
retained red/capture failures and an interrupted extended run remain separate from
that closed baseline. The two resumed acceptance failures are repaired; all 13
controls pass. Extended controls retain four missing-service-dispatch failures/37
passes; strict Linux `retry-hour` dispatch now passes the repaired 42-control run.
History/exclusion retains its ordering failure; corrected rerun passes 13 and actual
v3 upgrade crash/lost-ack controls pass three; local credential-reuse controls pass two.
Separate 275-identity successor freeze created/checked. Frozen standalone focus passes
45 and affected passes 248; main focus passes 119, with all identities unchanged after
each result. Standalone full passes 554/two opt-in S3 skips with unchanged identities.
Main affected passes 607/one isolated-local migration opt-in skip; full main passes
880/three opt-in skips, with complete reports and unchanged identities after each
result. Combined intentional-retry local gate closed, not Linux acceptance:
[[wiki/work/dbt-compaction-coordination/verification#Intentional-retry ownership — active, not accepted]].
Durable implemented semantics, without full acceptance:
[[wiki/workflow/wintap-etl-data-flow#Linux shared-reader and hourly-writer integration]].
Stabilized retry invariants:
[[wiki/workflow/wintap-etl-data-flow#Audited raw-only intentional retry]].
Entity-only controls retain 22 missing-API failures (35.05 s), with all 749 report
lines inspected and all 275 accepted identities unchanged. No entity crash boundary
has executed. Standalone verifier retains 64 missing-module failures (29.53 s), with
all 2,972 report lines inspected and accepted identities unchanged. Distinct receipts
retain 26 first-red failures (0.51 s) and now pass 26 controls (6.16 s); complete
reports inspected and accepted identities unchanged. Separate standalone verifier
passes its initial 64 controls (36.47 s), with complete report/identity checks. Genuine
corrected review red retains 21 failures/two passes (6.94 s), with complete report
and identity checks. Streaming SQL/configuration/historical-publication repairs pass
fresh scoped lint/format. Both repair reruns retain 12 failures/75 passes, fully
reviewed with accepted identities unchanged. Bounded SQL staging avoids the missing
optional UDF dependency; expanded first red retains 35 failures/9 passes with complete
report/identity review. Repaired Inventory-count defect; combined run passes 131 controls.
Ten expanded controls retain five fixture failures/five passes; fixture-only corrections
pass ten, with complete reports/identity checks. Expanded combined rerun passes 141
controls (97.91 s), complete report reviewed and all 275 accepted identities unchanged.
Standalone verifier focused evidence is closed; durable publication authentication
and ownership remain open.
Latest opt-in-v5 controls retain seven unsupported-argument failures (35.10 s);
post-verifier ownership rerun retains 22 missing-module failures (44.08 s). Both
complete reports reviewed and all 275 accepted identities unchanged before coding;
no upgrade or entity crash boundary executed.
Subsequent explicit-v5 schema staging passes seven actual upgrade crash/lost-ack
controls, then 37 expanded compatibility controls. Default v4 is preserved; new
entity history remains fail-closed. The 43-control history focus passes (109.80 s),
complete report reviewed and all 286 identities match. Existing-ledger first
compatibility retains two failures/149 passes (401.75 s), complete report/identities
reviewed; actual COMMIT/lost-ack/row checks precede a default-v4 diagnostic mismatch.
Restored original wording without test/refusal changes. Separate 286-identity repair
freeze binds repaired 46-/151-control runs. Focus passes 46 (127.49 s), complete
report/identities reviewed; compatibility passes 151 (399.51 s), complete report and
all repair identities reviewed. Schema compatibility is closed, not entity permission
or successor full gates. At schema closure only `ledger.py` differed from the accepted
retry baseline; the later input adapter and controls are separate additions.
Ownership/publication remain unfinished.
Receipt preparation grants no launch:
[[wiki/work/dbt-compaction-coordination/verification#Entity-only ownership — active, not accepted]].
Main-side input-observation first red retains 21 missing-module failures (16.90 s),
complete report/identity review done. First adapter rerun retains one command-byte
acceptance failure/20 passes (65.77 s); complete report/identities reviewed. Exact-byte
repair/expanded rerun passes 27 (83.28 s), complete report reviewed and all 288 frozen
identities match. Artifact focus is closed; expanded qualification retains nine
failures/22 passes (102.92 s), complete report/identities reviewed. Adapter-only exact
totals/early-clock repair passes the combined 58 controls (185.12 s), complete report
reviewed and all 289 contract-repair identities match. Main-side input-authentication
focus is closed; explicit-v5 typed intent/restart exclusion has separate focused evidence.
Separate typed first run retains 34 import-masked failures (47.41 s), complete report/
290 identities reviewed, without ownership/crash acceptance:
[[wiki/work/dbt-compaction-coordination/verification#Typed entity intent and restart exclusion — no launch]].
Typed implementation retains 33 upgrade-masked failures/one v4 pass (34.61 s); complete
report/291 identities reviewed, without typed assertions or crash-child launch.
Same-transaction keyset/budget-before-owner repair passes the unchanged 34 controls
(125.03 s), complete report/all 291 identities reviewed. Separate staged-history/
budget/paging/semantic focus passes 24 (79.82 s), complete report/all 292 identities
reviewed, preserving all repair identities. Combined main typed/input/schema/receipt/
original-ledger compatibility focus passes 336 (884.70 s); standalone passes 141
(105.56 s), complete reports/all 292 identities reviewed on the unchanged successor
freeze. Exclusion-only focus is closed; next add genuine main completion-observation
authentication without permission/authority transitions. Entity launch/completion/
publication/recovery and wider acceptance remain open.
Separate 44-control main completion-observation first run retains 44 import-masked
failures (342.12 s); complete lossless report/all 293 identities reviewed,
preserving the 292-identity focused baseline; test-only CLI fixtures confer no service
permission. Separate read-only completion adapter's unchanged 44-control rerun retains
two helper failures / 42 passes (470.91 s); complete report/all 294 identities reviewed.
Two refusals remain masked in that report; exact two-line helper-only successor passes
44 (471.51 s), complete report/all 294 identities reviewed. Runtime/assertions unchanged;
both refusals now execute without launch/mutation. Initial focus closed, not expanded
completion/affected/full; no permission transition or historical fallback:
[[wiki/work/dbt-compaction-coordination/verification#Main current-generation completion observations — read-only, active]].
Separate artifact/data/non-mutation qualification passes 67 (353.73 s), complete report/
all 295 identities reviewed. Expanded read-only focus closed; unchanged combined
standalone passes 141 (110.49 s), complete report/identities reviewed; 447-main focus
passes (1729.40 s), complete nine-line report/all 295 identities reviewed. Combined
read-only focus closed, not affected/full or entity writer/service acceptance. Separate
original-generation publication-retention red controls grant no permission transitions.
Separate 46-control retention module is reviewed/lint/format-clean and collected on a
296-identity successor preserving all 295 closed-focus identities. First red retains
46 import-masked failures (402.36 s); complete 1,772-line report, both child diagnostics
and all unchanged identities reviewed. Children exit 1 at import, not 87; no publication
COMMIT or semantic refusal executes. Separate bounded retention/accessor/history source
passes all unchanged 46 controls (629.02 s), exit 0; complete three-line report/all 297
frozen identities reviewed. Initial publication focus closed, not expanded/combined/affected/
full or entity writer/service acceptance. Current-only adapters/controls/standalone runtime
and no-transition boundaries unchanged. Separate 77-control envelope/audit/SQL-byte/keyset
qualification plus two unchanged original crash controls pass 79 (100.90 s) on a distinct
298-identity successor. Complete report/sidecar, both retained actual exit-87 diagnostics and
all source/runner/operator identities reviewed. Expanded publication focus closed, not entity
permission or wider Linux acceptance. Complete expanded-green wiki/privacy/scoped checks
pass; distinct unchanged source/runner freezes bind the separate combined focus. Standalone
passes 141 (109.28 s); main passes 570 (2430.83 s). Complete reports/sidecars, actual retained
publication crash diagnostics and all source/runner/operator identities reviewed. Combined
focused gate closed, not affected/full, entity permission or wider Linux:
[[wiki/work/dbt-compaction-coordination/verification#Durable original-generation publication retention — active, not accepted]].
The next 22-control writer red has local explicit-v5 fixtures and separately frozen actual
diagnostic retention; assertions/shared helpers remain unchanged. The separate red completes
with 22 import-masked failures (45.76 s); complete report/four exit-1 child diagnostics and
all identities reviewed. No writer boundary executed in that red. The subsequent five-file
Linux writer runtime was reviewed/formatted but initially unqualified; retained-completion
acknowledgment resolution then refused. The first frozen 22+20 runtime run retains 40/two failures (244.11 s);
complete report/seven genuine child diagnostics/all 301 identities reviewed. Clock-fixture
correction and immutable committed-ack resolution were its open follow-through:
[[wiki/work/dbt-compaction-coordination/verification#Entity writer explicit-v5 continuation — no launch acceptance]].
Historical source-only status:
[[wiki/work/dbt-compaction-coordination/verification#Linux entity writer runtime successor — unqualified]].
The separate 29-control immutable-resolution successor and scoped synthetic history-clock
correction were reviewed/frozen with runtime unchanged before the 49-control red:
[[wiki/work/dbt-compaction-coordination/verification#Immutable acknowledgment-resolution controls — prepared, runtime unchanged]].
That red retains 25 passes/nine failures/15 setup errors: late rollback refusal, missing immutable
resolution and original-clean recovery's unsafe after-COMMIT DRAINING state. Full evidence and
all identities were reviewed before runtime repair; Linux acceptance remains open.
The immutable-resolution/early-clock/conservative-uncertainty source successor was reviewed
and frozen before its distinct first 71-control run:
[[wiki/work/dbt-compaction-coordination/verification#Immutable resolution runtime successor — unqualified]].
That run finishes with 69 passes/two test-contract failures after successful resolution;
full evidence/all identities reviewed. Failed evidence is preserved; the positive test contract
was corrected without changing the runtime. Original controls are preserved and the narrow
contract-only correction is reviewed/frozen; all runtime and other controls remain unchanged:
[[wiki/work/dbt-compaction-coordination/verification#Resolution command-contract control successor — prepared]].
The distinct frozen all-71 rerun passes (521.59 s); full retained evidence and unchanged
identities reviewed. Initial writer/history/resolution focus is closed. The separate unchanged
123-control publication affected rerun now passes (708.64 s); complete report/actual COMMIT
diagnostics and all frozen identities reviewed. Only publication follow-through closes;
expanded entity/Linux qualification remains open. Retained evidence:
[[wiki/work/dbt-compaction-coordination/verification#Publication affected rerun after resolution — prepared]].
Separate genuine typed completion-process-death controls pass all 12 (283.57 s), with complete
actual diagnostics/hash-bound captures/artifacts and all 304 frozen identities authenticated.
Only this focused gate closes; runtime and existing controls remain unchanged. Retained evidence:
[[wiki/work/dbt-compaction-coordination/verification#Genuine typed completion-process-death controls — prepared]].
Separate completion/resolution SQL-budget/keyset-tail successor is reviewed/
frozen/collected (44), adding only the new module while preserving all 304 predecessors:
[[wiki/work/dbt-compaction-coordination/verification#Completion/resolution SQL-budget and keyset-tail qualification — prepared]].
The frozen run passes all 44 (62.53 s); full report/sidecar and independent original/artifact/
archive/ledger review authenticate. Inspection-only table/count mistakes are retained and
corrected; all 84 retained files/one symlink and 305 identities unchanged. No test active;
only this focused history gate closes. Separate frozen raw-cursor/authority forward-history
controls now pass all 23 (87.45 s); complete independent inspection authenticates original
chains, 16 verifier groups/four CLI completions/34 archives and all 306 identities, preserving
305 predecessors and 150 retained files/one symlink. Guessed final-mode inspection failure is
retained; actual raw proof requires OPEN at the advanced cursor, without queued-reader grant
or live authority. At forward closure no test/runtime change was active; only that focus closes. Retained evidence:
[[wiki/work/dbt-compaction-coordination/verification#Raw-cursor/authority forward-history successor — prepared]].
The first strict service red retains 71 missing-seam failures (135.78 s), with full report/
diagnostic/307-identity review; both crash children stopped at argument parsing, not COMMIT.
Only the two service/original-loader runtime seams now change in a separate reviewed/frozen
successor; all controls/305 other identities remain unchanged. Its unchanged 71-control rerun
passes (251.19 s); independent read-only inspection authenticates 32 verifier groups/ten clean
CLI captures/60 archives, atomic typed completion/resolution/crash and exclusion boundaries.
Both inspector assumption failures/sources, actual damaged originals and real blocking clocks
are preserved. All 439 green files/eight symlinks, 310 red entries, accepted forward evidence
and 307 identities remain unchanged; no test was active at that focus closure. Only
strict-service focus closes:
[[wiki/work/dbt-compaction-coordination/verification#Executed strict entity service result — focused gate closed]].
Original-bound maintenance and broader both-runtime integration remain open; the separately
completed 307-control service-affected result is recorded below.
Separate service-affected scope passes **307 controls in 2,036.10 s** on the unchanged
307-identity runtime. Complete report/sidecar, two actual crash diagnostics, all 5,982 fixture
entries and prior green/red/accepted-forward evidence authenticate. Independent read-only
inspection validates 170 ledgers and maps 18 expected corruption refusals; post-COMMIT typed
completion/authority remain `DRAINING` with no raw-cursor advance. The accepted forward fixture
was preserved, not rerun. Only the service-affected gate closes; pending-publication/missing-
original repair, broader both-runtime/Linux/S3/resources/native-Mac and dcc-02–05 gates remain open:
[[wiki/work/dbt-compaction-coordination/verification#Service-affected Linux result — 307-control affected gate closed]].
Read-only pending-publication control planning keeps partial originals out of clean resolution;
genuine original eligibility and a separate bounded repair contract remain unqualified:
[[wiki/work/dbt-compaction-coordination/implementation_plan#Original-bound pending-publication controls — source planning only]].
The prior input slice preserved all 286 schema identities and conferred no durable publication:
[[wiki/work/dbt-compaction-coordination/verification#Main-side entity input observations — no permission]].
dcc-02–05, actual isolated S3/resource qualification and native-Mac shutdown stay open.
The historical producer pass authorized no utility work; the later isolated Analytics/
native implementation authorization is recorded above. No deployment, scheduling,
real-dataset mutation, commit or push is authorized by the current pass.

Historical PowerShell ETW POC: [[wiki/work/powershell-sensor/brief]],
[[wiki/work/powershell-sensor/dev_handoff]], [[wiki/work/powershell-sensor/implementation_plan]],
[[wiki/work/powershell-sensor/findings]] and [[wiki/work/powershell-sensor/verification]].
Native wrapper/focused 4104 output pass 35 tests; inspected 5.1 data includes interactive
`write-host hi`, with loss/fragment/test-overlap limits disclosed. Full originals retained;
collection traffic/loss unchanged. Focused rerun works by operator report. These pages
preserve the POC's evidence and limits; the later integrated sensor is documented in
[[wiki/component/powershell-sensor]] and [[wiki/event_type/powershell-events]]. Its
PowerShell 7/live ETW qualification and downstream DBT modeling remain open.
Raw sensor S3 compaction development:
[[wiki/work/raw-sensor-file-aggregation/brief]],
[[wiki/work/raw-sensor-file-aggregation/interview]],
[[wiki/work/raw-sensor-file-aggregation/implementation_plan]],
[[wiki/work/raw-sensor-file-aggregation/verification]], and
[[wiki/work/raw-sensor-file-aggregation/references]] — standalone DuckDB 2.0.0
utility owned by PyUtil at `../Wintap-PyUtil/extras/raw-sensor-compact/` (wiki/evidence
remain in Analytics), manual hourly compaction across hosts from `lintap/raw_sensor/<event>/...`
into `lintap/compacted/<event>/...`. Existing destination event/hours are skipped;
otherwise merge all files per exact optional protocol leaf, without row sorting.
`plan`/`compact`/`verify` and per-leaf count validation implemented; 137 local tests
pass with 2 opt-in skips. Initial fixed-root live S3 test passes: 897,395 rows preserved,
29 → 2 objects, unchanged source hashes, rerun skips with unchanged output hashes.
See [[wiki/tool/raw-sensor-compaction]] and the accepted
[[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]]. No run IDs,
manifests or conditional writes; partial failures need manual cleanup. Optional
`--delete-source` now validates then deletes a closed source-hour prefix after
grace (default 10 minutes, minimum 5), with bounded post-delete confirmation and
diagnostics; hourly deletion is separate from event compaction and
`reconcile-delete --confirm-delete` handles explicit cleanup. PyUtil scans raw_sensor + compacted without
overlap masking. Full synthetic raw/mixed/compacted DBT tests match all 54 models
with 139 gates per state; copied-live host/pidstat tests match 4 models across
897,395 rows, delete 29 copied objects and preserve all original hashes. Suites:
107 compactor and 299 PyUtil passes, with 2 opt-in skips each. Existing ANY_VALUE
quality debt is explicitly non-blocking. Full copied-live migration passes:
54 models/139 gates in each state, exact bronze/schemas/unaffected results,
2,668,265 rows conserved, 399 copied objects → 10 outputs, all original hashes
unchanged. Affected downstream differences are reported. The S3 fixtures and two
initial retain-source outputs were subsequently cleaned up at the human's request
(445 objects); all 399 original hashes still match. Local evidence is preserved;
no surviving full-build fixture is claimed. A Nov 7 on-prem sequential day run
measured 436.168 s copy/setup plus 612.17 s hourly compaction; 18/24 hours
completed and six deletion-check failures were preserved with partial outputs.
The mitigated fresh-copy rerun then completed all 24/24 hours with zero deletion
failures, 240/240 partitions and a zero-delta 57,047,250-row immutable-baseline
verification; copy took 443.653 s and hourly processing 731.664 s.
Broad transport/fault coverage and the representative shard/performance benchmark
remain pending.
Object filenames may change while
the partition scheme is preserved. Daily rollup and cron are deferred; the
upload-time partition TODO is [[wiki/todo/raw-sensor-upload-time-partition]].

Pidstat Go rewrite, fpc-03 review checkpoint and four-hour VM soak completed
(2026-10-31 05:18–09:18UTC;49files/399312rows,2880sample times,80canaries;
human acceptance/packaging pending): [[wiki/work/fix-pidstat-collector/soak_review]], [[wiki/work/fix-pidstat-collector/brief]],
[[wiki/work/fix-pidstat-collector/implementation_plan]],
[[wiki/work/fix-pidstat-collector/dev_handoff]],
[[wiki/work/fix-pidstat-collector/verification]] — remove installed-host uv/Python/
DuckDB requirements while preserving metrics and Parquet contracts. First live gate:
existing Multipass `lintap-dev`, Ubuntu arm64; RHEL 8/amd64 runtime proof deferred.
Native workflow: [[wiki/tool/pidstat-implementation-loop]] — `/pidstat-loop`,
bounded skill, deterministic Python/Parquet/ELF evidence utility and human fpc-01 pause;
fresh review via `/pidstat-review` in a new session. fpc-01 human-approved; fpc-02 raw
sampler/config port passes26-column parity on266/705/1640 real Python rows,
14Go tests,17config cases, static binaries/native arm64 replay and bounded411-row
diagnostic. Fpc-02 approved; fpc-03 durable legacy spool/raw replay,26Go/native tests,
signal seal/SIGKILL recovery/locking/retry pass. Human acceptance pending; original
host pytest runner was blocked, while the current utility rerun passes 19 tests.
Fresh Go checks are blocked by the retained temporary toolchain's missing standard
library. Packaging, comparative resources, DBT and paired-live remain unqualified.
Delivery limits:
[[wiki/tension/pidstat-publication-versus-uploader-receipts]].

Future medium-priority fix: [[wiki/work/reuse-etl-duckdb-instance/brief]] —
dedicated ETL engine reuse, separate from the resolver; lifecycle/concurrency,
CPU comparison and memory-growth qualification required before rollout.

Approved DuckDB1.5 maintenance: [[wiki/work/duckdb-1-5-maintenance/implementation_plan]],
[[wiki/work/duckdb-1-5-maintenance/verification]] — official .NET wrapper1.5.6.1,
Wintappy/Lintap Python engine1.5.6 complete;250native tests,15pidstat,27UI and
fullDBT83nodes pass. Existing config failure/venv recreation disclosed; no deployment.

DuckDB 2 upgrade planning: [[wiki/work/duckdb-2-upgrade/brief]],
[[wiki/work/duckdb-2-upgrade/references]],
[[wiki/work/duckdb-2-upgrade/implementation_plan]] — sensor, pidstat, canonical DBT
and current analysis only; **on hold pending official .NET 2.0 support**.
Latest-1.x maintenance completed separately; no old notebook/SQL repair or
2.0 implementation authorized.

Identity patch: [[wiki/work/host-process-identity-patch/implementation_plan]],
[[wiki/work/host-process-identity-patch/verification]] — source implemented and
isolated restart/endpoint acceptance passed; installed hosts/history unchanged.

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/work/recent-host-activity-dashboard/brief]] | medium | Implemented metadata-first S3 object dashboard (per-host file count/size over filename collect time, no Parquet reads) with optional DuckDB raw-row mode; includes partition pruning, adaptive bins, and explicit refresh. The row mode's guarded `raw_process_file` aggregation returns 7.9 million rows as 479 five-minute groups in about 20 seconds. See [[wiki/work/recent-host-activity-dashboard/interview]], [[wiki/work/recent-host-activity-dashboard/design]], [[wiki/work/recent-host-activity-dashboard/implementation_plan]], [[wiki/work/recent-host-activity-dashboard/dev_handoff]], and [[wiki/work/recent-host-activity-dashboard/verification]]. |
| [[wiki/work/net10-dependency-prune/verification]] | medium | .NET 10 Debian arm64 package: 30-minute soak passes 20 runs/5,000 unique file paths with zero restarts or observed serializer drops; Mac reads all 24 runs; named server-network gaps remain yellow. |
| [[wiki/work/network-endpoint-normalization/implementation_plan]] | high | Shared TCP endpoint/name fix; done checklist and pending package/Windows-live/historical repair gates. |
| [[wiki/work/network-endpoint-normalization/verification]] | high | Enum-based normalization and compatible DBT/legacy counters; 28 .NET + 74 SQL regressions, same-host separate/same-PID live proof and independent green Mac confirmation. |
| [[wiki/work/improve-lintap-data-quality/brief]] | high | CLOSED 2026-10-22: adaptive wakeups, dedicated FileSerializer draining, coordinated shutdown, and kernel-time network attribution passed two-hour source and fresh packaged-arm64 gates. |
| [[wiki/work/improve-lintap-data-quality/diagram-glossary]] | high | Companion glossary for every `[A1–A13]`, `[Q1–Q5]`, and `[S1–S18]` label in the Linux eBPF architecture and shutdown diagrams, with implementation, operations, and evidence references. |
| [[wiki/work/lintap-process-creation-validation/index]] | medium | Research thread for comparing process creation accuracy across Lintap, Tetragon, Tracee, and Sysdig and building cross-sensor validation workloads. |
| [[wiki/work/lintap-process-creation-validation/future-scheduler-lifecycle-vs-syscalls]] | medium | Future investigation: current Linux sensor already uses fork/exec/exit scheduler hooks plus syscall entry; compare lifecycle fidelity, attempt visibility, group-aware exits and end-to-end costs. |
| [[wiki/work/lintap-process-creation-validation/research-snapshot-2026-07-31]] | medium | Snapshot of process creation acquisition, known accuracy risks, PID uniqueness strategies, and reference-tool issue findings. |
| [[wiki/work/lintap-process-creation-validation/handoff-validation-next-steps]] | medium | Handoff plan for sensor-neutral process/file/network workload generation, cross-sensor runs, normalization, and accuracy reporting. |
| [[wiki/work/lintap-process-creation-validation/validation-harness-design]] | medium | Concrete design for a sensor-neutral validation harness with manifest schema, normalized event tables, workload matrix, and first implementation slice. |
| [[wiki/work/lintap-process-creation-validation/linux-setup]] | medium | UTM and Multipass Linux VM setup guidance for running eBPF validation workloads and reference sensors from a Mac. |
| [[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]] | medium | Current checkpoint summary for committed process-state fixes, one-hour noisy validation results, remaining leakage, and next steps. |
| [[wiki/work/fix-upload-cache-deletion/brief]] | high | CLOSED 2026-08-17 (accepted): dead upload-delete path fixed with inline gated delete, hang-recovery scoped, prune fixed/configurable, uploader plumbing guarded; next slice queued: generic small-file consolidation in the upload cycle. |
| [[wiki/work/fix-upload-cache-deletion/dev_handoff]] | high | Handoff authorizing `../wintap` core/etl/load changes: inline delete gated on the unused `successfulUpload` flag, dead-event decision, prioritized robustness cleanups with do-not-change list, ≥3-cycle verification, deployment note for drained backlogs. |
| [[wiki/work/fix-upload-cache-deletion/verification]] | medium | Verification record for the upload-cache deletion fix: inline delete-after-upload, dead-event removal, prune/hang-recovery hardening, Linux build verification, and remaining live-uploader/Windows gaps. |
| [[wiki/work/improve-pidstat-collector/brief]] | medium | CLOSED 2026-08-17 (accepted): Python /proc-sampler collector with container attribution, systemd/uv packaging, and Wintappy parquet bronze; open watch items: collector CPU, small-file consolidation, S3 end-to-end. |
| [[wiki/work/improve-pidstat-collector/references]] | medium | Cross-repo source map for the pidstat collector feature: Lintap script, Wintappy DBT macros/models, wintap upload adapters, and observed data volumes. |
| [[wiki/work/improve-pidstat-collector/design]] | medium | Design: single-process Python collector (2026-08-14 decision) with telemetry-source investigation (/proc sampler preferred over pidstat child and psutil; container attribution via cgroup/ns), spool-then-parquet rotation into `raw_sensor/pidstat/dayPK=/hourPK=`, sensor upload ride-along, coordinated Wintappy parquet change. |
| [[wiki/work/improve-pidstat-collector/implementation_plan]] | medium | Plan with slice 2 redefined (2026-08-14) as a Python rewrite: single-process collector on the duckdb Python API absorbing all review findings, pytest port with fork regression guard, systemd unit, Wintappy DBT parquet migration; steps 1–4 complete. |
| [[wiki/work/improve-pidstat-collector/dev_handoff]] | medium | Slice-2 handoff: rewrite the collector in Python (retiring the fork-storm bash version), hard single-process requirement, carried-over semantics as spec, pytest port, systemd, and Wintappy parquet migration, with `../Lintap` + `../Wintappy` authorization. |
| [[wiki/work/improve-pidstat-collector/verification]] | medium | Verification log for both slices, each with an accepted independent review: slice 1 (bash, retired) and slice 2 (Python /proc sampler, 12/12 pytest, container columns, Wintappy parquet migration); remaining items are operational (target-host systemd, container fixture, S3 end-to-end blocked on the upload fix). |
| [[wiki/work/improve-etl-and-qa/interview]] | medium | Interview record for the ETL/QA cleanup feature: cross-repo scope, all-event-family cleanup, pidstat promoted to first-class bronze/silver/gold, Wintappy Marimo as canonical QA, and compatibility left open for design. |
| [[wiki/work/improve-etl-and-qa/brief]] | medium | Feature brief for cleaning up the Wintappy DBT bronze/silver/gold/monitoring stack and QA contract across event families, with pidstat elevated to a first-class family and Analytics-side conflicts aligned or retired. |
| [[wiki/work/improve-etl-and-qa/references]] | medium | Source map for the ETL/QA cleanup feature: Wintappy DBT models and monitoring views, Marimo QA notebook contract, current test coverage, and the older Analytics-side QA paths that still conflict. |
| [[wiki/work/improve-etl-and-qa/design]] | medium | Design for separating event-family DBT contracts from QA presentation: pidstat promoted to a first-class family, monitoring repositioned as a consumer of intentional family outputs, and Wintappy Marimo made canonical. |
| [[wiki/work/improve-etl-and-qa/implementation_plan]] | medium | Eight-stage plan with DBT/QA and runtime-observability slices tracked separately; durable promotion is partially complete and FD-path cache eviction remains open. |
| [[wiki/work/improve-etl-and-qa/verification]] | medium | Chronological DBT, notebook, perf, serializer, policy, sender, and historical-cache verification; stale gates are separated from current gaps and field artifacts are hash/window qualified. |
| [[wiki/work/improve-etl-and-qa/milestone-2026-08-28]] | medium | Interim milestone snapshot: pidstat gold + interactive QA notebook exploration landed, mixed-schema eventtime hardened, uv workflow cleaned up, and the remaining next-slice decisions called out explicitly. |
| [[wiki/work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth]] | medium | Concrete plan for diagnosing Lintap's stair-step memory growth: keep pidstat as the outer symptom view, then add smaps, .NET runtime counters, and periodic file-pipeline/backlog telemetry to distinguish leak vs allocator/runtime ratcheting. |
| [[wiki/work/improve-etl-and-qa/dev_handoff]] | medium | August 31 continuation state: historical-cache long gate passed; next slice is bounded FileOps FD-path eviction with fidelity gates and pending sibling commit placeholders preserved. |
| [[wiki/work/improve-etl-and-qa/cpu-growth-review-2026-08-29]] | high | Read-only review of current Lintap long-run CPU risks and an evidence-first measurement sequence that treats zero drops and event fidelity as optimization gates. |
| [[wiki/work/improve-etl-and-qa/ebpf-path-audit-2026-08-30]] | high | Source-grounded audit of Lintap's eBPF execution path, layered diagnostics, validation assets, perf-wrapper overlap, cleanup findings, and the documentation plan for developers, architects, and reviewers. |
| [[wiki/work/improve-etl-and-qa/tenable-scan-storm-response-2026-08-30]] | high | Production-response note for the Tenable scan storm: sender-queue saturation evidence, auditable generic kernel `comm` deny-policy recommendation, rejected alternatives, and validation gates. |
| [[wiki/work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30]] | high | Analysis of the no-Tenable capture: policy hits were zero, but the FileOps sender was cap-bound and dropped 601126 events; RSS stabilized with the bounded backlog while CPU and internal FD-cache growth remained high. |
| [[wiki/work/improve-etl-and-qa/esper-sender-path-analysis-2026-08-30]] | high | End-to-end FileOps sender/Esper analysis and benchmark: Esper handles roughly 179k synthetic File events/s, the empty broad subscriber route was removed, threading/context alternatives were rejected, and process-cache misses are the leading live bottleneck. |
| [[wiki/work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31]] | high | Extended field validation of the historical process-identity cache: 10h23m passive run plus a 6,000-file recovery burst, zero pipeline loss, stable latency under bounded cache churn, with resource-slope limitations called out. |
| [[wiki/work/improve-etl-and-qa/future-adaptive-fileops-and-diagnostics-data]] | speculative | Future investigations for rate/type-aware adaptive FileOps sampling with weighted telemetry and promotion of runtime diagnostics from log text into first-class raw-style Parquet/DBT data. |
| [[wiki/work/fix-unbounded-process-table-growth/brief]] | medium | CLOSED 2026-08-27 (accepted): process-table growth bounded (8M rows/10 days → ~47k plateau) via retention sweep + stale-open reconciliation + bounded QA telemetry + CloneSensor thread filter; long-run acceptance runs as extended-deployment-monitoring; knowledge promoted to component/process-table-retention. |
| [[wiki/work/extended-deployment-monitoring/brief]] | high | Parallel acceptance task for both 2026-08-27-closed features: 1-2 week human status checks on multi-host test deployments (P2/T5/T3/T6 from the bundle), exit criteria for final acceptance, and the carried watch items (fop-14, capture flake, ACME dataset check). |
| [[wiki/work/fix-unbounded-process-table-growth/references]] | medium | Source map for the process-table retention feature: ProcessResolver/EventChannel hot paths, ClearDB call sites, validation-harness baseline, decisions to date, DuckDB space-reclamation questions. |
| [[wiki/work/fix-unbounded-process-table-growth/design]] | medium | First-slice design: lazy resolver-owned sweep scheduling, liveness-based stale-open reconciliation, exited-row retention, and DuckDB telemetry for stop/reconciled/deleted/retention-miss counts. |
| [[wiki/work/fix-unbounded-process-table-growth/implementation_plan]] | medium | First-slice implementation checklist for resolver retention/reconciliation, harness updates, VM builds, and the remaining long-run follow-up work. |
| [[wiki/work/fix-unbounded-process-table-growth/dev_handoff]] | medium | Dev handoff authorizing ../wintap changes: retention sweep + liveness reconciliation as QA feature + retention-miss metric, delegated decisions, first slice, testing and closeout duties. |
| [[wiki/work/fix-unbounded-process-table-growth/verification]] | medium | Slice-1 verification and accepted 2026-08-13 review: builds/pytest (independently re-verified), rundown-reconciliation bug found via QA telemetry and fixed, clone-sensor runs reaching 0 missing live PIDs, and remaining gaps before closeout. |
| [[wiki/work/improve-windows-process-collection/interview]] | medium | Interview record for the Windows process collection overhaul: three Q&A rounds resolving kernel-ETW-primary, one-sensor consolidation, snapshot refresh, SID-POC adoption, boot-trace scope, and the no-breaking-changes constraint. |
| [[wiki/work/improve-windows-process-collection/brief]] | medium | Feature brief for replacing Security-log-based Windows process collection with a unified kernel-ETW sensor: true create times, restored stop coverage, snapshot refresh, SID/command-line enrichment, boot ETL ingestion, no schema/PidHash changes. |
| [[wiki/work/improve-windows-process-collection/references]] | medium | Source map for the Windows process collection feature: current dual-path sensors, shared kernel session infrastructure, the validated sid-extraction-test POC (SID offsets, Global Logger boot procedure), and the harness/resolver pages it builds on. |
| [[wiki/work/improve-windows-process-collection/design]] | medium | Design: one WindowsProcessSensor fusing boot ETL replay, live snapshot, classic kernel ProcessStart/End, and manifest ProcessStop metrics, with create-time canonicalization for PidHash integrity, per-field enrichment fallbacks, QA counters, and startup sequencing around the Global Logger boot session. |
| [[wiki/work/improve-windows-process-collection/implementation_plan]] | medium | Plan mapped to wintap wpc-01…wpc-09 instruction units (wpc-08 harness skipped by Architect decision; wpc-09 final bug sweep) with xUnit trait categories; done checklist fully closed 2026-08-19. |
| [[wiki/work/improve-windows-process-collection/dev_handoff]] | medium | Handoff bridging the Analytics feature artifacts to the wintap Architect/Engineer/Developer loop: per-unit Engineer dispatch prompt, primary sources per unit, wpc-01-first recommendation, testing gates, and closeout/audit duties. |
| [[wiki/work/improve-windows-process-collection/metrics]] | medium | Plain-language Velocity pilot: estimated delivery speed **3.5× one solo developer's pace**, plausibly **about 2×–7×**, with low confidence because estimates were retrospective and not independent; attention remains diagnostic only. |
| [[wiki/work/improve-windows-process-collection/sid-helper-notes-2026-08-17]] | medium | Migrated Wintap Engineer scratch notes for wpc-01: narrow SID-helper instruction scope, required feature context, payload-parser test seam, and hard no-schema/no-PidHash/no-TraceEvent-upgrade/no-dependency constraints. |
| [[wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17]] | medium | Wintap Engineer scratch notes for wpc-02: shared-kernel ProcessStart/ProcessStop sensor core scope, ETW timestamp canonicalization, ProcessResolver hot-path identity, stop fallback tests, and the flagged PidHash ownership tension. |
| [[wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17]] | high | Out-of-scope smoke observations and their final disposition: wpc-09 fixed the boot-trace lifecycle, parent-warning, DuckDB escaping, and logger-tag items; SensSensor load failure and missing SignedS3UrlAdapter remain future candidates outside the feature. |
| [[wiki/work/improve-windows-process-collection/verification]] | high | Closeout verification record (feature closed 2026-08-19): accepted manual validation evidence — wpc-06 elevated smoke PASS, wpc-07 reboot/overnight PASS, wpc-09 sweep fixes, final overnight smoke-test with boot replay confirmed — plus 54/54 wpc test state and the wpc-08 skip rationale. |
| [[wiki/work/windows-sensor-health-check/interview]] | high | Interview record for the health-check feature: egress-choke-point placement, aggregated low-noise reporting, all-Windows-sensor coverage, full-stream constant-time checks, and the Round 2 log-only redirection; carries the (now unsealed) human estimates. |
| [[wiki/work/windows-sensor-health-check/brief]] | high | Feature brief with the nine frozen acceptance criteria (re-frozen under amendment #2): egress hook on both branches + MemoryMap bypass, five definitive checks, six-stream liveness, aggregated log reporting, capped samples, kill switch, extensibility, no schema changes, verification. |
| [[wiki/work/windows-sensor-health-check/design]] | high | Design record: EventChannel.Send grounding, unknown-sentinel and path-form ground truth, the shc-03 diskpart→QueryDosDevice insert with the fromNative guard fix, check engine/liveness/reporting architecture, and the sweep-scope findings now consolidated into the sweep queue. |
| [[wiki/work/windows-sensor-health-check/implementation_plan]] | high | Three units (execution order shc-01 → shc-03 → shc-02) with the shc abbreviation declaration; done checklist fully closed 2026-08-25 (shc-02 audit missing — external harness; recorded per never-gates). |
| [[wiki/work/windows-sensor-health-check/verification]] | high | Verification record: shc-01 33/33, shc-03 27/27 + fromNative translation tests, shc-02 egress integration (65/65 feature suite independently re-run), and the 2026-08-25 availability-anchor live run recorded verbatim (lead time 1 day). |
| [[wiki/work/windows-sensor-health-check/metrics]] | high | First fully valid dual-sealed Velocity point: 40 solo-hours in 1 calendar day = **Feature Velocity 7.0** (uncertainty 3.5–17), comparability none (Q3 "Yes"); human AI-date prediction hit its optimistic edge; per-unit actuals and API cost missing data. |
| [[wiki/work/improve-windows-registry-collection/brief]] | high | Feature brief (criteria frozen 2026-08-25): replace the defective RegistrySensor (string-split parsing, TOCTOU re-reads, unbounded caches, broken ExpandString) with a manifest-only sensor built on the POC-discovered capture mode. |
| [[wiki/work/improve-windows-registry-collection/interview]] | high | Interview record: POC-first feature open, adaptive rounds skipped (scope settled during the spike sessions), confirmed playback of the manifest-only/capture-filter/keyword-mask/typed-parsing decisions; carries the (now unsealed at close-out 2026-08-25) human estimates. |
| [[wiki/work/improve-windows-registry-collection/metrics]] | high | Closed mini-lab record: 240 solo-hours ("6 weeks", sealed) delivered same-day = **Feature Velocity 42.0** (uncertainty 7–84, widest sealed spread yet: 240 vs 80 h), comparability willingness-only (Q3 "Yes, but not the ETW discovery"); per-unit actuals, attention proxy, and API cost missing data. |
| [[wiki/work/improve-windows-registry-collection/references]] | high | Source map: legacy sensor files marked for rewrite/deletion (with defect line refs), EtwProviderCollector enable path, WintapMessage integration points, the wrc-poc probe-log evidence set, and sweep-queue cross-links. |
| [[wiki/work/improve-windows-registry-collection/implementation_plan]] | high | Closed plan (2026-08-25): wrc-01/wrc-02 retroactive spikes + wrc-03..08 all implemented, audited, and Architect-accepted (134/134 `Category~wrc`; commit 1f66a47); all four open Architect inputs resolved (Option A session handle, 0x5300/0x5700 mask via probe8, minimal schema extension, canary knobs); wrc-08 rolled in as a scoped Non-Goals exception; done checklist fully closed. |
| [[wiki/work/improve-windows-registry-collection/verification]] | high | Verification record: six unit audits (all Complete, commit 1f66a47), the 2026-08-25 Architect-run live verification recorded verbatim with an honest evidence-contract coverage table, the wrc-08 smoke-test addendum (Architect-verbal, query evidence missing data), and the finalized same-day availability anchor (lead time 1-day minimum). |
| [[wiki/work/optimize-fileops-poller/brief]] | high | CLOSED 2026-08-27 (accepted): FileOps event-volume reduction landed end to end — kernel filters, decoupled poller, fop-11 emit-first aggregation (count+byte conservation field-proven by A/B), fop-12/13 path identity, and the Esper EPL n² eventCount fix; watch items: fop-14 serializer caps (long-term), ~1% open+close capture flake, ACME dataset inflation check. |
| [[wiki/work/optimize-fileops-poller/references]] | high | Source map for the FileOps optimization: sensor/tracer/poll-loop hot paths, two-tier Makefile build, EventChannel PidHash-overwrite proof, CO-RE fd-inode traversal idiom, and validation-harness patterns. |
| [[wiki/work/optimize-fileops-poller/design]] | medium | Full design: per-event cost inventory, socket/pipe and self-feedback volume analysis, changes K1–K4/U1–U6 with per-change no-loss arguments, tracked-fd-map alternative rejected, fidelity-gap backlog (rename, pread, io_uring). |
| [[wiki/work/optimize-fileops-poller/implementation_plan]] | medium | Seven fop-nn slices sequenced measurement-first (counters/baseline → userspace dead work → kernel filters → record split → fd-cache eviction), with per-slice test requirements including the A/B no-loss differential. |
| [[wiki/work/optimize-fileops-poller/dev_handoff]] | medium | Handoff ledger (feature CLOSED 2026-08-27): full fop history with dated updates — queue/ring stabilization, fop-10 measurement, fop-12/13 acceptance, fop-11 A/B gates cleared, EPL fix requirement for deploys. |
| [[wiki/work/optimize-fileops-poller/verification]] | medium | Verification ledger for the FileOps feature through closeout: per-slice proofs, the fop-11 field A/B runs (EPL n² root-cause, byte-verified PASS, tolerance amendment), and the 2026-08-27 acceptance. |
| [[wiki/work/optimize-fileops-poller/test_plan]] | high | Branch-wide closeout test plan (fop T1-T6 + process-table P1-P3): build+unit smoke, harness self-test, deploy smoke, the kill-switch A/B differential, collector parquet sanity, fop-14 watch, process-creation pytest, process-table boundedness, and the on-demand long-run deep dive — supersedes the per-slice intermediate tests. |
| [[wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25]] | medium | Phase-2 root-cause analysis of sustained FileOps ring-buffer loss: ~778 events/s reserve failures traced to the single-threaded consumer's per-event DuckDB query under a global lock plus synchronous Esper send, with ranked no-loss next slices (fop-08 decoupling front-runner) and answers to the four handoff questions. |
| [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]] | medium | Concrete designer-review proposal for the gated fop-11 step: emit-first short-interval aggregation of repeat `open` / `openat` activity, based on fop-10 duplicate-open evidence and paired with a revised count-conservation differential contract. |
| [[wiki/work/optimize-fileops-poller/milestone-2026-08-25-phase2-wrapup]] | medium | Phase-2 milestone closeout: summarizes what landed, the strongest deployed evidence, why fop-12 is still not accepted, and the best current next-fix hypotheses for the design follow-up. |
| [[wiki/work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25]] | medium | Root-cause diagnosis of the fop-12 relative-open miss floor (decode-time /proc reads racing millisecond-lived producers; O_DIRECTORY opens discarded in-kernel) with the ranked fop-13 fix: kernel-time directory identity index plus file dev:ino as the fop-11 aggregation key. |
| [[wiki/work/selinux-monitoring/interview]] | high | Interview record for the SELinux monitoring feature: first-class-events decision, eBPF/RHEL 9 constraints, novel-tuple dedup, four acceptance criteria, delegations to spike/design; carries the sealed human estimates. |
| [[wiki/work/selinux-monitoring/brief]] | high | Feature brief (criteria frozen 2026-08-27): SELinux as a first-class Lintap eBPF event domain — AVC denials/grants (debugging), transitions + novel-tuple-deduped context-interaction map (monitoring) — landing in raw_sensor parquet parallel to process/file/network; dashboards, DBT, and RHEL 8 out of scope. |
| [[wiki/work/selinux-monitoring/references]] | medium | Source map: Lintap tracer/sensor/EPL/serializer patterns to follow, legacy auditd POC as schema reference, kernel attach-point candidates to verify on-host, and the fop volume/join lessons. |
| [[wiki/work/selinux-monitoring/spike]] | medium | ANSWERED 2026-09-17 (localhost + two validation runs; environment later identified as RHEL 8.10/4.18-backport, not RHEL 9 — correction recorded): selinux_audited tracepoint proven end to end with context strings; kprobe tier firing at 2.4-13k checks/s; 421 distinct (ssid,tsid,tclass) tuples (Dropped 0) sizes the dedup map; BPF LSM silently inert without `bpf` in lsm=; SID→context resolution flagged as the central design problem; background AVC denials validate the use case. |
| [[wiki/work/selinux-monitoring/design]] | medium | Design with all five open questions human-decided 2026-09-17 (R1 prototype-then-fallback resolution, row-per-permission, frozen SELINUX_* names, 30s zero-delta-skipping flush, overhead-gated fentry): three streams on the verified hooks, 16k in-kernel LRU novel-tuple dedup, policy-epoch handling, schema/EPL/serializer shapes, counters/kill-switch surface. |
| [[wiki/work/selinux-monitoring/implementation_plan]] | medium | Five sel-NN slices, evidence-first: sel-01 validation measurements + timeboxed R1 prototype, sel-02 tracer+sensor skeleton, sel-03 resolver/dedup/policy-epoch, sel-04 ETL (frozen message types, group-by rule), sel-05 four-criteria validation; files-to-change map, cross-slice invariants, kill-switch rollback. |
| [[wiki/work/selinux-monitoring/dev_handoff]] | medium | Handoff authorizing ../wintap changes (tracer/sensor/EPL/serializer, additive-only message types) plus Analytics validation assets: copy/paste prompt with interview-seal warning, spike traps (noaudit hook, inlined avc_audit, BPF LSM silent-inert, RHEL 8.10 noaudit-kprobe EINVAL), field-workflow rules, delegated decisions, next-session priorities after sel-02. |
| [[wiki/work/selinux-monitoring/verification]] | medium | sel-02 + sel-03 records (2026-09-18, transcribed from sanitized validation summaries): all three streams captured in an RHEL 8.10 validation environment via the wrapper fallback (noaudit kprobe EINVAL-blocked; gate open); sel-03 core mechanics package-validated — decoder 132/2150, R2/R3 resolver (source contexts resolving, targets mostly learned-or-numeric), LRU flush with zero-delta skip (errors=0), policy-epoch polling, unknown-perm-mask telemetry (fd/sem watch item). |
| [[wiki/work/selinux-dbt-pipeline/brief]] | medium | DBT-only downstream work for native SELinux AVC, interaction, and transition parquet: optional bronze, silver normalization, gold detail/summaries, constrained process attribution, and quality verification. |
| [[wiki/work/support-docker-contexts-linux/interview]] | medium | Confirmed interview for a research prototype comparing cgroup, namespace, eBPF, shared-resolver, runtime, and systemd approaches to Linux context enrichment and inventory. |
| [[wiki/work/support-docker-contexts-linux/brief]] | medium | Feature brief for broad Linux cgroup context support across process, file, network, and pidstat telemetry, with schema deferred until prototype evidence is available. |
| [[wiki/work/support-docker-contexts-linux/references]] | medium | Live source and external reference map for Linux cgroup, namespace, OCI, runtime, systemd, and eBPF context collection. |
| [[wiki/work/support-docker-contexts-linux/design]] | speculative | Comparison design for phase-1 cgroup v2 host/systemd/Docker and phase-2 v1/hybrid/Podman research fixtures. |
| [[wiki/work/support-docker-contexts-linux/spike]] | speculative | Prototype question and hypothesis for identifying the most valid cross-event context acquisition strategy. |
| [[wiki/work/support-docker-contexts-linux/implementation_plan]] | medium | Research implementation sequence from diagnostic observation contract through cross-event comparison and schema recommendation. |
| [[wiki/work/support-docker-contexts-linux/dev_handoff]] | medium | Code-development handoff for the first diagnostic cgroup/namespace observation slice, with sibling-repo authorization boundaries. |
| [[wiki/work/support-docker-contexts-linux/verification]] | medium | Verification scaffold awaiting Linux fixture execution and comparison results. |
| [[wiki/work/debian-package-refresh/interview]] | high | Interview record for the Debian package refresh: parity-refresh framing (deb packaging pre-exists and drifted behind the field RPM), both-arch Ubuntu targets, field-parity env, MCP/RPM parity, opportunistic selinux object; carries the sealed human estimates. |
| [[wiki/work/debian-package-refresh/brief]] | high | Feature brief: refresh ../Lintap/packaging/lintap-deb to parity with the field-proven RPM builder (tier-aware tracer validation, MCP publish parity, field env, Snappy kept as a deliberate divergence), validated by install + short smoke on native Ubuntu amd64 and arm64. |
| [[wiki/work/debian-package-refresh/references]] | high | Source map: stale deb builder pieces, the RPM builder sections to mirror (and the RHEL 8-specific ones not to), the two-tier eBPF Makefile contract, Lintap.csproj MCP coupling, and the 2026-06 packaging review backlog split. |
| [[wiki/work/debian-package-refresh/implementation_plan]] | medium | Seven dpr-NN slices: script parity, env sync, upgrade-safe maintainer scripts + ldd-verified Depends, docs refresh, amd64 then arm64 build+smoke, closeout promotion. |
| [[wiki/work/debian-package-refresh/dev_handoff]] | medium | Handoff authorizing writes to ../Lintap/packaging/lintap-deb only, with copy/paste prompt, parity do/don't lists, cross-build validation expectations, and smoke/upgrade testing duties. |
| [[wiki/work/debian-package-refresh/verification]] | medium | Arm64 native and amd64 native UTM build/install/start/upgrade/remove/purge evidence recorded; cross-build evidence retained, with Debian multiarch CPATH and optional .NET diagnostic-provider caveats documented. |
| [[wiki/work/debian-package-refresh/release-README]] | medium | Draft release README for the RPM `0.3.5-12.el8` asset and Debian `0.1.0-14` amd64/arm64 assets, with installation, runtime, upgrade, removal, and checksum guidance. |
| [[wiki/work/debian-package-refresh/metrics]] | low | Closeout metrics record with missing sealed estimates, native arm64/amd64 validation evidence, and the RPM builder parity follow-up boundary. |
| [[wiki/work/privileged-ebpf-helper/future-privileged-ebpf-helper-boundary]] | speculative | Future least-privilege design separating a privileged eBPF helper from the unprivileged .NET processing service through a protected Unix-domain socket. |
| [[wiki/work/refactor-data-log-paths/interview]] | high | Interview record for the data/log path refactor: four Q&A rounds resolving the data/runtime tree split, two independent roots, knob repurposing, FHS-style defaults, mount-time hostname convention, frozen parquet internals, and no-auto-migration; sealed estimates recorded. |
| [[wiki/work/refactor-data-log-paths/brief]] | high | Feature brief for splitting the single mixed root into a shared archivable `data` tree (mountable by shared-storage test environment VMs) and a host-only `runtime` tree, with WINTAP_DATA_ROOT repurposed, new WINTAP_RUNTIME_ROOT, cross-repo packaging/pipeline tracking, and Linux-gated acceptance. |
| [[wiki/work/refactor-data-log-paths/references]] | high | Source map for the path refactor: Env.cs/ConfigManager root resolution, data-tree vs runtime-tree derivation sites, the hardcoded <local-path> defect, Lintap deb/rpm packaging and pidstat spool, and downstream Wintappy/Analytics consumers to track. |
| [[wiki/work/refactor-data-log-paths/design]] | medium | Design: two-root resolution in Env.cs/ConfigManager, data root directly containing raw_sensor (no parquet/ level), runtime tree keeping existing child names, Esper serializer staging under runtime/esper_staging, packaging/pidstat/Wintappy changes, and mount-time hosts/<hostname> pattern. |
| [[wiki/work/refactor-data-log-paths/implementation_plan]] | medium | Eight rdp-NN slices: two-root core + runtime-consumer moves with grep gates first, then deb/rpm + pidstat packaging, Wintappy tracking, the three Linux acceptance gates, and closeout promotion. |
| [[wiki/work/refactor-data-log-paths/dev_handoff]] | medium | Detailed handoff authorizing ../wintap, ../Lintap packaging+collector, and ../Wintappy changes: copy/paste prompt with interview-seal warning, complete consumer-move list, hard constraints (frozen internals, no migration, no hostname code), delegated vs escalate-to-human decisions, and per-gate testing duties. |
| [[wiki/work/refactor-data-log-paths/verification]] | medium | Validation record: focused root tests, Debian arm64 package/install and fresh event-output smoke, manual disposable-host cleanup, and a DBT build against fresh direct-root output passed; two-instance shared-mount validation remains open. |
| [[wiki/work/fix-hardcoded-agentid/brief]] | high | CLOSED 2026-10-20: TCP AgentId propagation, state-template sanitization, neutral watchdog copy, and existing eBPF TCP live validation passed; resolver profiling did not justify a cache. |
| [[wiki/work/fix-hardcoded-agentid/implementation_plan]] | high | Completed implementation and live-validation plan for the hardcoded AgentId feature. |
| [[wiki/work/fix-hardcoded-agentid/verification]] | high | Linux VM validation record: build/contracts, resolver profile decision, live eBPF attachment, smoke traffic, and fresh TCP parquet AgentId/lifecycle evidence all passed. |
---

*Last updated: 2026-10-23 (Linux capability smoke triage and main's AgentId/TCP documentation preserved)*
