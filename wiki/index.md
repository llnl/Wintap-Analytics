# Wintap Ecosystem Wiki Index

Master catalog of all pages. Updated by the agent on every ingest.

---

## Tension

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/tension/raw-telemetry-vs-normalized-wintap-semantics]] | medium | Preserves the unresolved boundary between raw ETW/sysdig/eBPF producer details and stable WintapAPI semantics. |
| [[wiki/tension/research-flexibility-vs-production-hardening]] | medium | Explains the research-first posture and flags hardening gaps such as unrestricted proof-of-concept MCP SQL access. |
| [[wiki/tension/etw-ebpf-and-cross-platform-compatibility]] | medium | Captures tradeoffs between Windows ETW, Linux eBPF/sysdig support paths, raw sensor Parquet, and cross-platform semantics. |
## Decision

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/decision/wiki-scope-cross-repo-wintap-focused]] | high | Records the decision that the wiki is cross-repo but prioritizes Wintap sensor internals, WintapAPI, Esper, and Wintap data analysis. |
| [[wiki/decision/feature-work-artifacts]] | medium | Defines the optional feature-work module: store LLM-assisted feature briefs/design/verification under `wiki/work/<feature>/` and promote durable facts into canonical pages. |
## Concept

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/concept/llm-assisted-feature-workflow]] | medium | Lightweight workflow for LLM-assisted feature work: brief → references → design → plan → verification → closeout. |
| [[wiki/concept/feature-work-template]] | medium | Standard artifact set for `wiki/work/<feature>/` and when to use it. |
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
## Repo

| Page | Confidence | Summary |
|------|------------|---------|
| [[wiki/repo/wintap-primary-sensor-repo]] | high | Orientation page for the primary Wintap implementation repo, active source tree, core layers, and wiki source-of-truth role. |
| [[wiki/repo/wintap-analytics-host-repo]] | high | Explains Wintap-Analytics as the wiki host and DuckDB/Jupyter/NetworkX-oriented Wintap data analysis repository. |
| [[wiki/repo/lintap-supporting-repo]] | high | Clarifies Lintap's supporting role for Linux TeleTap/eBPF, legacy sysdig, raw sensor Parquet, and packaging/dev workflows. |
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

---

*Last updated: 2026-07-31 (Lintap process creation validation research thread)*
