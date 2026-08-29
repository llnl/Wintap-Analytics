# Wintap Ecosystem Wiki Index

Master catalog of all pages. Updated by the agent on every ingest.

---

## Rollup

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/metrics]] | high | Cross-feature Velocity rollup: one row per closed feature (lead time, solo estimate, Feature Velocity ± uncertainty, comparability flag, metrics link), seeded with the WPC pilot row; Portfolio Velocity pending N≥several with trailing window ≥ 4× median lead time. |

## Tension

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]] | medium | Preserves the unresolved boundary between raw ETW/sysdig/eBPF producer details and stable WintapAPI semantics. |
| [[wiki/tension/research-flexibility-vs-production-hardening]] | medium | Explains the research-first posture and flags hardening gaps such as unrestricted proof-of-concept MCP SQL access. |
| [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] | medium | Captures tradeoffs between Windows ETW, Linux eBPF/sysdig support paths, raw sensor Parquet, and cross-platform semantics. |
| [[wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet]] | medium | Captures the open mismatch between Wintappy's canonical DuckDB-only DBT output and Wintap-Analytics' documented expectations of published stdview-* parquet datasets. |
## Decision

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/decision/wiki-scope-cross-repo-wintap-focused]] | high | Records the decision that the wiki is cross-repo but prioritizes Wintap sensor internals, WintapAPI, Esper, and Wintap data analysis. |
| [[wiki/decision/feature-work-artifacts]] | medium | Defines the optional feature-work module: store LLM-assisted feature briefs/design/verification under `wiki/work/<feature>/` and promote durable facts into canonical pages. |
| [[wiki/decision/process-identity-attribution-contract]] | high | Migrated Wintap ADR locking the process identity and attribution contract: core-owned PidHash/ParentPidHash, flat event-time fields, durable Stop/parent backfill, and DuckDB as the starting substrate. |
| [[wiki/decision/test-project-structure-and-first-test]] | high | Migrated Wintap ADR choosing per-target xUnit test projects, standing up `tests/Wintap.Tests/` first, and making the first test a real `WintapMessage` constructor assertion. |
| [[wiki/decision/consolidate-developer-wiki-into-analytics-wiki]] | high | Records the decision to retire `../wintap/dave-wiki/`, make this Analytics wiki the single Wintap ecosystem knowledge base, and keep Wintap instructions/audits in `../wintap/developer_docs/`. |
| [[wiki/decision/ai-velocity-roi-mini-lab]] | high | Per-feature velocity/ROI mini-lab, revised to v2.1 (2026-08-19, post external review): headline **Velocity** = solo-hours / (5.714 × days) in Feature and Portfolio views, forced-counterfactual sealed Q1 under the three-question ratchet, point-plus-uncertainty reporting, frozen-criteria/availability-finality/comparability guardrails, per-unit quality loop, attention proxy as coverage-annotated diagnostic, never-gates rule. |
| [[wiki/decision/platform-runtime-data-root-defaults]] | high | Records that unconfigured Wintap deployments use the OS defaults owned by Env.cs while explicit programmatic, environment, and JSON overrides remain supported. |
| [[wiki/decision/registry-provider-strategy]] | high | Accepted (2026-08-25, session-handle sub-decision OPEN): manifest-only Windows registry collection via an undocumented Microsoft-Windows-Kernel-Registry capture mode (4-byte 0xFFFFFFFF EVENT_FILTER_DESCRIPTOR at EnableTraceEx2) — standalone mechanism record with the probe matrix, sticky-global-state finding, KCB-correlation negative result, and framed session-handle options. |
## Concept

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/concept/llm-assisted-feature-workflow]] | medium | Lightweight workflow for LLM-assisted feature work (interview → brief → references → design → spike → plan → handoff → verification → closeout), with the interactive interview protocol, sealed metrics questions, invocation phrase, and promote-to-canonical operating rule. |
| [[wiki/concept/feature-work-template]] | medium | Full markdown skeletons for every `wiki/work/<feature-slug>/` artifact, including optional metrics files that open with plain-language Results and keep canonical fields under Technical Record; only `brief.md` is required. |
| [[wiki/concept/metrics-template]] | high | Defines the parseable `wiki/work/<feature-slug>/metrics.md` format: plain-language **Results** (estimated delivery speed, plausible range, confidence and reason) followed by the canonical Velocity YAML under **Technical Record**, plus availability, comparability, sealed estimates, per-unit rows, cost, and optional attention diagnostics. |
| [[wiki/concept/velocity-metric]] | high | The approved Velocity definition plus the wiki presentation convention: results state estimated multiples of one solo developer's pace, an “about X×–Y× faster” plausible range, and confidence with a direct reason; technical formula, Feature/Portfolio views, guardrails, and parallelism dividend remain unchanged. |
| [[wiki/concept/agentic-ebpf-probe-development]] | low | Unverified brainstorming survey of agentic eBPF probe tooling (MCPtrace, GPTtrace, eunomia-bpf) and additional EDR reference projects (Sysmon for Linux, Bombini). |
## Component

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/component/windows-sensor-service-internals]] | high | Documents Wintap service startup, platform subscription dispatch, Windows ETW sensor ordering, and EventChannel routing. |
| [[wiki/component/wintap-api-shared-data-model]] | high | Canonical page for the WintapMessage envelope, domain objects, plugin contracts, and EventChannel enrichment boundary. |
| [[wiki/component/wintap-recorder]] | high | Captures WintapRecorder recording-session control, registry mode flags, Parquet monitoring, and merge behavior. |
| [[wiki/component/plugin-and-mcp-samples]] | high | Documents plugin discovery/contracts, sample event subscriber behavior, and research/POC MCP SQL tooling caveats. |
| [[wiki/component/process-table-retention]] | high | Process-table retention/reconciliation contracts: resolver-owned sweep, liveness-based stale-open closing, bounded QA telemetry, CloneSensor CLONE_THREAD filter, ~47-50k row plateau, DuckDB lock caveat. |
| [[wiki/component/fileops-event-pipeline]] | high | Kernel-to-parquet FileOps contracts: tracer tiers and filters, fd/dir-index path identity, fop-11 emit-first aggregation (count+byte conserving), the Esper group-by rule (ungrouped select column = n² eventCount inflation), FileSerializer flush schema, and known caveats. |
| [[wiki/component/sensor-upload-cache-pipeline]] | high | Canonical page for the shared upload/cache pipeline: merge cycle, type-agnostic ride-along sweep contract, delete-after-upload (fixed 2026-08-17), prune backstop, hang-recovery scoping, deployment prerequisites, and the small-file consolidation follow-up. |
| [[wiki/component/sensor-health-monitor]] | high | Canonical page for the always-on Windows egress QA layer (shc feature, closed 2026-08-25): InspectForHealth hook on both egress branches + MemoryMap bypass, five constant-time checks, six-stream 5 s liveness watchdog, aggregated Wintap.log reporting, config keys, and the shc-03 QueryDosDevice drive-map/fromNative accuracy fix. |
## Data_model

| Page | Confidence | Summary |
|------|------------|---------|
## Event_type

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/event_type/process-events]] | high | Defines the unified WindowsProcessSensor semantics (2026-08): kernel-ETW Start/Stop on the shared session with ETW-canonical create times/PidHash, snapshot Refresh with dedup, SID/command-line/path enrichment fallbacks, manifest Stop-metric merge, opt-in boot-trace replay, QA counters, and ETL boundaries. |
| [[wiki/event_type/file-events]] | high | Defines ETW FileIO producer behavior, file-key path resolution, feedback suppression, and 10-second aggregate ETL semantics. |
| [[wiki/event_type/network-events]] | high | Defines TCP/UDP ETW producer behavior, endpoint fields, reversible TCP caveats, and 10-second network aggregate ETL semantics. |
## Pipeline

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/pipeline/nesper-esper-event-stream-processing]] | high | Explains EventChannel Esper runtime setup, EPL compile/deploy, serializer query registration, windows/contexts, backpressure, and NEsper diagnostics. |
## Schema

| Page | Confidence | Summary |
|------|------------|---------|
## Tool

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/tool/wintap-workbench]] | high | Summarizes the Angular Workbench UI, feature routes, SignalR/EPL query path, and query-state boundary. |
## Workflow

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/workflow/future-experiment-analysis-workflows]] | high | Tracks first-class analytics topics including ACME4 Explore, DuckDB view construction, process trees/paths, process-centric SQL, and network joins. |
| [[wiki/workflow/lintap-dev-field-workflow]] | high | The Lintap dev/field split: field-host clones are read-only by policy (reviews transcribed dev-side), diagnostics bundles must be self-sufficient, deploys pull and rebuild tracers on-host, pushes require the human's credentials, and agent memory must mirror into the wiki. |
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
| [[wiki/diagnostic/nesper-repro]] | high | Documents the standalone Fedora/shared-mount NEsper repro and the evidence that Bad IL range failures are output-location related. |
| [[wiki/diagnostic/dependency-inventory-and-update-status]] | medium | Inventories Python, npm, and .NET dependency manifests across the ecosystem and records observed update availability with tooling caveats. |
| [[wiki/diagnostic/rhel8-clone-sensor-and-fork-without-exec]] | medium | RHEL 8 field findings: clone sensor attaches (Fedora failure doesn't generalize), the fork-without-exec warning signature (parent = child−1), and a suspected ~500-700 forks/sec storm with event-processing lag under investigation. |
| [[wiki/diagnostic/windows-sensor-sweep-queue]] | high | Consolidated defect/finding queue the follow-on Windows sensor sweep feature opens from: WintapLogger BackgroundWorker sync-context capture and live-log truncation, Env.SetDataRoot test-fixture guidance, the health check's first live catch (PID=-1 Refresh → ProcessName=Unknown), ungated Registry emit sites, dead Serializer.Listen, WintapAlert self-PID drop, TranslateTransientPath authority bug, QueryDosDevice consolidation, MemoryMap reroute question, eventtime_invalid candidate. |
## Work

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/work/lintap-process-creation-validation/index]] | medium | Research thread for comparing process creation accuracy across Lintap, Tetragon, Tracee, and Sysdig and building cross-sensor validation workloads. |
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
| [[wiki/work/improve-etl-and-qa/implementation_plan]] | medium | Seven-stage implementation plan: contract decisions, pidstat first-class layering, event-family cleanup, monitoring rewrite, Marimo alignment, Analytics-side conflict cleanup, and end-to-end verification. |
| [[wiki/work/improve-etl-and-qa/verification]] | medium | First-slice verification record: new `pidstat_process_summary`, monitoring queries moved off raw-backed runtime dependencies, `dbt build`/`dbt test` passing, and the current dataset's remaining pidstat-data absence called out explicitly. |
| [[wiki/work/improve-etl-and-qa/milestone-2026-08-28]] | medium | Interim milestone snapshot: pidstat gold + interactive QA notebook exploration landed, mixed-schema eventtime hardened, uv workflow cleaned up, and the remaining next-slice decisions called out explicitly. |
| [[wiki/work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth]] | medium | Concrete plan for diagnosing Lintap's stair-step memory growth: keep pidstat as the outer symptom view, then add smaps, .NET runtime counters, and periodic file-pipeline/backlog telemetry to distinguish leak vs allocator/runtime ratcheting. |
| [[wiki/work/improve-etl-and-qa/dev_handoff]] | medium | Host-ready handoff for continuing the live Lintap memory-growth experiment, including the current perf-collection tooling, the real-run row counts, and the explicit warning that embedded DuckDB may be a major contributor to process memory growth. |
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
| [[wiki/work/improve-windows-registry-collection/interview]] | high | Interview record: POC-first feature open, adaptive rounds skipped (scope settled during the spike sessions), confirmed playback of the manifest-only/capture-filter/keyword-mask/typed-parsing decisions; carries the sealed human estimates (unread until close-out). |
| [[wiki/work/improve-windows-registry-collection/metrics]] | high | Mini-lab record (seal intact): sealed AI estimates (solo 80 h; AI-workflow date 2026-08-28) written before reading any of interview.md; plan-time per-unit estimates for wrc-03..07; wrc-01/wrc-02 retroactive spikes carry no estimates by definition. |
| [[wiki/work/improve-windows-registry-collection/references]] | high | Source map: legacy sensor files marked for rewrite/deletion (with defect line refs), EtwProviderCollector enable path, WintapMessage integration points, the wrc-poc probe-log evidence set, and sweep-queue cross-links. |
| [[wiki/work/improve-windows-registry-collection/implementation_plan]] | high | Declares abbreviation `wrc`; wrc-01/wrc-02 recorded as retroactive pre-open spikes; proposes wrc-03 decode core → wrc-04 enablement engine → wrc-05 WintapMessage schema → wrc-06 sensor rewrite + legacy deletion → wrc-07 mask/canary/overhead/live verification (all Proposed); carries the four open Architect inputs incl. the OPEN session-handle decision and the unsettled keyword mask. |
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
---

*Last updated: 2026-08-27 (merged origin/main: wpc/shc/wrc records joined; both branch features CLOSED/accepted — fix-unbounded-process-table-growth and its fop subtask; knowledge promoted to component pages; long-run acceptance shifted to extended-deployment-monitoring ahead of the branch PR)*
