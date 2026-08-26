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
## Concept

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/concept/llm-assisted-feature-workflow]] | medium | Lightweight workflow for LLM-assisted feature work (interview → brief → references → design → spike → plan → handoff → verification → closeout), with the interactive interview protocol, when-to-use guidance, the invocation phrase, and the promote-to-canonical operating rule. |
| [[wiki/concept/feature-work-template]] | medium | Full markdown skeletons for every `wiki/work/<feature-slug>/` artifact (interview, brief, references, design, spike, implementation plan, dev handoff, verification, research-thread index); only `brief.md` is required. |
| [[wiki/concept/agentic-ebpf-probe-development]] | low | Unverified brainstorming survey of agentic eBPF probe tooling (MCPtrace, GPTtrace, eunomia-bpf) and additional EDR reference projects (Sysmon for Linux, Bombini). |
## Component

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/component/windows-sensor-service-internals]] | high | Documents Wintap service startup, platform subscription dispatch, Windows ETW sensor ordering, and EventChannel routing. |
| [[wiki/component/wintap-api-shared-data-model]] | high | Canonical page for the WintapMessage envelope, domain objects, plugin contracts, and EventChannel enrichment boundary. |
| [[wiki/component/wintap-recorder]] | high | Captures WintapRecorder recording-session control, registry mode flags, Parquet monitoring, and merge behavior. |
| [[wiki/component/plugin-and-mcp-samples]] | high | Documents plugin discovery/contracts, sample event subscriber behavior, and research/POC MCP SQL tooling caveats. |
| [[wiki/component/sensor-upload-cache-pipeline]] | high | Canonical page for the shared upload/cache pipeline: merge cycle, type-agnostic ride-along sweep contract, delete-after-upload (fixed 2026-08-17), prune backstop, hang-recovery scoping, deployment prerequisites, and the small-file consolidation follow-up. |
## Data_model

| Page | Confidence | Summary |
|------|------------|---------|
## Event_type

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/event_type/process-events]] | high | Defines Security-log-backed process Start/Stop/Refresh semantics, process-tree reconstruction, PidHash lineage, and ETL boundaries. |
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
| [[wiki/work/improve-windows-process-collection/implementation_plan]] | medium | Three-slice plan mapped to wintap wpc-01…wpc-08 instruction units: SID helper, sensor core, snapshot refresh, enrichment, stop-metrics merge, wire-in/removal, opt-in boot ETL, and Windows validation harness, each with xUnit trait categories and a done checklist. |
| [[wiki/work/improve-windows-process-collection/dev_handoff]] | medium | Handoff bridging the Analytics feature artifacts to the wintap Architect/Engineer/Developer loop: per-unit Engineer dispatch prompt, primary sources per unit, wpc-01-first recommendation, testing gates, and closeout/audit duties. |
| [[wiki/work/optimize-fileops-poller/brief]] | high | Feature brief for reducing FileOps event volume with zero information loss: kernel-side self-PID and regular-file filtering, userspace dead-work removal, batched wakeups, and stage counters; aggregation explicitly deferred. |
| [[wiki/work/optimize-fileops-poller/references]] | high | Source map for the FileOps optimization: sensor/tracer/poll-loop hot paths, two-tier Makefile build, EventChannel PidHash-overwrite proof, CO-RE fd-inode traversal idiom, and validation-harness patterns. |
| [[wiki/work/optimize-fileops-poller/design]] | medium | Full design: per-event cost inventory, socket/pipe and self-feedback volume analysis, changes K1–K4/U1–U6 with per-change no-loss arguments, tracked-fd-map alternative rejected, fidelity-gap backlog (rename, pread, io_uring). |
| [[wiki/work/optimize-fileops-poller/implementation_plan]] | medium | Seven fop-nn slices sequenced measurement-first (counters/baseline → userspace dead work → kernel filters → record split → fd-cache eviction), with per-slice test requirements including the A/B no-loss differential. |
| [[wiki/work/optimize-fileops-poller/dev_handoff]] | medium | Current handoff for the FileOps feature after the 2026-08-25 phase-2 burst: queue/ring stabilization and fop-10 are landed, fop-12 path recovery is improved but not yet accepted, and fop-11 remains blocked on path-identity quality. |
| [[wiki/work/optimize-fileops-poller/verification]] | medium | Verification ledger for the FileOps feature: build/harness commands, deployed smoke-test proof, overnight field results, deployed hashes, and the phase-2 analysis summary of sustained ring loss from recorded counter statistics. |
| [[wiki/work/optimize-fileops-poller/deep-analysis-2026-08-25]] | medium | Phase-2 root-cause analysis of sustained FileOps ring-buffer loss: ~778 events/s reserve failures traced to the single-threaded consumer's per-event DuckDB query under a global lock plus synchronous Esper send, with ranked no-loss next slices (fop-08 decoupling front-runner) and answers to the four handoff questions. |
| [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]] | medium | Concrete designer-review proposal for the gated fop-11 step: emit-first short-interval aggregation of repeat `open` / `openat` activity, based on fop-10 duplicate-open evidence and paired with a revised count-conservation differential contract. |
| [[wiki/work/optimize-fileops-poller/milestone-2026-08-25-phase2-wrapup]] | medium | Phase-2 milestone closeout: summarizes what landed, the strongest deployed evidence, why fop-12 is still not accepted, and the best current next-fix hypotheses for the design follow-up. |
| [[wiki/work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25]] | medium | Root-cause diagnosis of the fop-12 relative-open miss floor (decode-time /proc reads racing millisecond-lived producers; O_DIRECTORY opens discarded in-kernel) with the ranked fop-13 fix: kernel-time directory identity index plus file dev:ino as the fop-11 aggregation key. |

---

*Last updated: 2026-08-26 (optimize-fileops-poller: fop-13c/fop-13d field-accepted — LRU dir index decorrelates evictions from misses; fop-11 deployed and healthy, owing the kill-switch A/B and parquet-sanity gates; fop-14 downstream-durability candidate opened for the ETL serializer loss point)*
