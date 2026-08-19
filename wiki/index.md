# Wintap Ecosystem Wiki Index

Master catalog of all pages. Updated by the agent on every ingest.

---

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
| [[wiki/decision/ai-velocity-roi-mini-lab]] | high | Per-feature velocity/ROI mini-lab, revised to v2 post-pilot (2026-08-19): headline time-to-availability (calendar lead time, weekends included) + throughput (counterfactual-hours per window), calendar-posed sealed estimates under the three-question ratchet, per-unit quality loop, attention proxy demoted to coverage-annotated diagnostic, never-gates rule. |
| [[wiki/decision/platform-runtime-data-root-defaults]] | high | Records that unconfigured Wintap deployments use the OS defaults owned by Env.cs while explicit programmatic, environment, and JSON overrides remain supported. |
## Concept

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/concept/llm-assisted-feature-workflow]] | medium | Lightweight workflow for LLM-assisted feature work (interview → brief → references → design → spike → plan → handoff → verification → closeout), with the interactive interview protocol, sealed metrics questions, invocation phrase, and promote-to-canonical operating rule. |
| [[wiki/concept/feature-work-template]] | medium | Full markdown skeletons for every `wiki/work/<feature-slug>/` artifact (interview, brief, references, design, spike, implementation plan, dev handoff, verification, metrics, research-thread index); only `brief.md` is required. |
| [[wiki/concept/metrics-template]] | high | Defines the parseable `wiki/work/<feature-slug>/metrics.md` format for the AI velocity/ROI mini-lab (v2): lead-time fields with availability anchor, throughput weight, calendar-posed sealed estimates, per-unit estimate/actual rows, and a demoted coverage-annotated attention diagnostic block. |
| [[wiki/concept/agentic-ebpf-probe-development]] | low | Unverified brainstorming survey of agentic eBPF probe tooling (MCPtrace, GPTtrace, eunomia-bpf) and additional EDR reference projects (Sysmon for Linux, Bombini). |
## Component

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/component/windows-sensor-service-internals]] | high | Documents Wintap service startup, platform subscription dispatch, Windows ETW sensor ordering, and EventChannel routing. |
| [[wiki/component/wintap-api-shared-data-model]] | high | Canonical page for the WintapMessage envelope, domain objects, plugin contracts, and EventChannel enrichment boundary. |
| [[wiki/component/wintap-recorder]] | high | Captures WintapRecorder recording-session control, registry mode flags, Parquet monitoring, and merge behavior. |
| [[wiki/component/plugin-and-mcp-samples]] | high | Documents plugin discovery/contracts, sample event subscriber behavior, and research/POC MCP SQL tooling caveats. |
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
## Work

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/work/lintap-process-creation-validation/index]] | medium | Research thread for comparing process creation accuracy across Lintap, Tetragon, Tracee, and Sysdig and building cross-sensor validation workloads. |
| [[wiki/work/lintap-process-creation-validation/research-snapshot-2026-07-31]] | medium | Snapshot of process creation acquisition, known accuracy risks, PID uniqueness strategies, and reference-tool issue findings. |
| [[wiki/work/lintap-process-creation-validation/handoff-validation-next-steps]] | medium | Handoff plan for sensor-neutral process/file/network workload generation, cross-sensor runs, normalization, and accuracy reporting. |
| [[wiki/work/lintap-process-creation-validation/validation-harness-design]] | medium | Concrete design for a sensor-neutral validation harness with manifest schema, normalized event tables, workload matrix, and first implementation slice. |
| [[wiki/work/lintap-process-creation-validation/linux-setup]] | medium | UTM and Multipass Linux VM setup guidance for running eBPF validation workloads and reference sensors from a Mac. |
| [[wiki/work/lintap-process-creation-validation/current-state-2026-08-06]] | medium | Current checkpoint summary for committed process-state fixes, one-hour noisy validation results, remaining leakage, and next steps. |
| [[wiki/work/improve-pidstat-collector/brief]] | medium | Feature brief for making the pidstat collector run alongside Lintap with lifecycle management, time-based rotation, S3 push, and DBT `stg_pidstat_metrics` compatibility. |
| [[wiki/work/improve-pidstat-collector/references]] | medium | Cross-repo source map for the pidstat collector feature: Lintap script, Wintappy DBT macros/models, wintap upload adapters, and observed data volumes. |
| [[wiki/work/improve-pidstat-collector/design]] | medium | Design: continuous service, spool-then-parquet rotation into `raw_sensor/pidstat/dayPK=/hourPK=`, ride-along on the sensor's verified type-agnostic upload sweep, coordinated Wintappy parquet change. |
| [[wiki/work/improve-pidstat-collector/implementation_plan]] | medium | Nine-step plan with slice-2 scope marked: review follow-up fixes, systemd unit, Wintappy DBT parquet migration, verification runs, closeout promotion; steps 1–4 complete. |
| [[wiki/work/improve-pidstat-collector/dev_handoff]] | medium | Slice-2 handoff for a code-development agent on another system: review fixes, `-p ALL` README documentation, systemd packaging, and Wintappy parquet migration, with `../Lintap` + `../Wintappy` authorization. |
| [[wiki/work/improve-pidstat-collector/verification]] | medium | Command log and first-slice results for the new Lintap pidstat collector: environment checks, Linux ride-along verification, shell tests, and live parquet smoke run. |
| [[wiki/work/fix-unbounded-process-table-growth/brief]] | medium | Feature brief for bounding event_store process-table growth on long runs (8M rows/10 days observed) with retention + stale-open reconciliation while preserving PID-reuse-safe process resolution. |
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
| [[wiki/work/improve-windows-process-collection/metrics]] | medium | Closed velocity/ROI mini-lab record with v2 addendum: lead time 6 calendar days (anchored on the 2026-08-19 boot-replay-confirming smoke) vs. a reconstructed ~20-calendar-day solo counterfactual, throughput weight 120h, attention 3.47h retained as coverage-annotated diagnostic, retrofit/units-reconstruction caveats recorded honestly. |
| [[wiki/work/improve-windows-process-collection/sid-helper-notes-2026-08-17]] | medium | Migrated Wintap Engineer scratch notes for wpc-01: narrow SID-helper instruction scope, required feature context, payload-parser test seam, and hard no-schema/no-PidHash/no-TraceEvent-upgrade/no-dependency constraints. |
| [[wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17]] | medium | Wintap Engineer scratch notes for wpc-02: shared-kernel ProcessStart/ProcessStop sensor core scope, ETW timestamp canonicalization, ProcessResolver hot-path identity, stop fallback tests, and the flagged PidHash ownership tension. |
| [[wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17]] | high | Out-of-scope smoke observations and their final disposition: wpc-09 fixed the boot-trace lifecycle, parent-warning, DuckDB escaping, and logger-tag items; SensSensor load failure and missing SignedS3UrlAdapter remain future candidates outside the feature. |
| [[wiki/work/improve-windows-process-collection/verification]] | high | Closeout verification record (feature closed 2026-08-19): accepted manual validation evidence — wpc-06 elevated smoke PASS, wpc-07 reboot/overnight PASS, wpc-09 sweep fixes, final overnight smoke with boot replay confirmed — plus 54/54 wpc test state and the wpc-08 skip rationale. |

---

*Last updated: 2026-08-19 (wpc-09 complete; platform-owned runtime data-root defaults documented)*
