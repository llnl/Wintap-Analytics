---
title: "Implementation plan: smoke-test results dashboard"
type: concept
confidence: high
grounded_by:
  - streamlit/projects/SmokeTests/README.md
  - ../wintap/devtools/smoke_manifest.py
policy: agent-editable
last_validated: 2026-10-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/SmokeTests; ../wintap/devtools
tags: [smoke-tests, streamlit, portable-manifests, feature-work]
---

# Smoke-test results dashboard

User requested one read-only Streamlit section per smoke test, tailored data
queries, absent-data handling, run commands and repeated-run grouping. User
explicitly authorized updating existing smoke scripts and excluded legacy-data
support. Test host and analysis host must be independent (Multipass Linux→Mac).

- [x] Shared portable versioned run envelope across eight smoke test families
- [x] Host/run UUID/time/PID/path/endpoint selectors; failed-test evidence retained
- [x] Standalone read-only Streamlit app with independent manifest/data sources and upload
- [x] Sections, run selector, code blocks, tailored SQL, activity/coverage/row displays
- [x] Normal/direct schema and timestamp normalization; explicit direct-source host
- [x] Query/UI and manifest/workload regressions
- [x] VM collected-data→Mac dashboard live integration (missing event evidence preserved)
- [x] Promote durable app usage/semantics and final verification record

Verification: [[wiki/work/smoke-test-dashboard/verification]].

## Durable evidence and triage extension (authorized 2026-10-22)

User accepted normal mounted/uploaded-data latency and source deletion; no
transport redesign, acknowledgements or long-term source spool required.

- [x] Shared optional DuckDB parquet export across all decorated smoke families
- [x] Atomic immutable snapshots, typed metadata/full JSON/hash, UTC partitions
- [x] Automatic dataset discovery, latest revision and conflicting-copy validation
- [x] Exclude smoke evidence from telemetry normalization; bounded detail reads
- [x] Host/test overview, severity counts, history/attention filters and navigation
- [x] Explicit pending/missing/stimulus-only/negative-companion/overlap semantics
- [x] Producer, query and Streamlit regressions
- [x] Mounted Multipass Linux→Mac capture integration, no separate JSON transfer
- [x] Promote final evidence/usage to canonical wiki

Plan and accepted scope: [[wiki/work/smoke-test-dashboard/durable-evidence-plan]].

## Read-only Garage/S3 source (authorized 2026-10-25)

User selected direct Garage access on the same feature branch and reports smoke
evidence reaching S3. No collector/uploader or sibling-repo changes are authorized
or required for this slice; DBT manifest integration remains deferred.

- [x] Private JSON config with credential-free schema and standard AWS env/profile chain
- [x] Path-style Garage access with temporary DuckDB secret and HTTPS verification
- [x] Paginated/UTC partition-pruned evidence and telemetry discovery, fail-closed caps
- [x] Shared remote connection, existing manifest/selector/triage semantics and refresh
- [x] Backend, source-parity, Streamlit and real loopback HTTP transport regressions
- [x] Document launch/configuration/security and preserve local/mounted behavior
- [ ] Operator validates dashboard against the actual Garage dataset

## Canary separation and lazy multipage validation (2026-10-25)

User refined scope to non-interfering recurring canaries, not all dev-time tests,
and requested real Streamlit Overview/Canary/Dev-time pages. Same-branch scope;
collector/uploader, sibling source, SDK/DuckDB and experimental defaults unchanged.

- [x] Define canary contract and expand independent runner to five manifest families
- [x] Reuse process/file/named/native/endpoint generators without invoking validators
- [x] Per-PID Stop checks, bounded eight-file expectations and explicit unsupported skips
- [x] Streamlit `st.Page`/`st.navigation` pages and legacy stimulus-only classification
- [x] Manifest-only overview; select host/family/run before explicit telemetry validation
- [x] Single selected-run in-memory working set, fail-closed row/memory budgets, no spill
- [x] Preserve conflict/hash, missing/stimulus-only triage and hidden-run overlap warnings
- [x] Mocked runner/adapter, query parity/budget, real navigation and S3 transport tests
- [x] Update canonical documentation and record limitations
- [ ] Expanded one-round Linux canary pilot and Garage page/validation operator check
- [ ] Optional native timestamp pushdown, safe partition pruning and memory-only result reuse

## All-round validation, HOST context and saved results (2026-10-25)

- [x] Validate all recorded canary families/cases through one explicit round action
- [x] Explicit/new and shared-directory/older round membership, missing-family inventory
- [x] One bounded shared observation scan and preserved red/skip/overlap semantics
- [x] Passive complete HOST startup context, temporal/race/conflict/unknown handling
- [x] Optional unique inferred short/FQDN correlation, collision rejection
- [x] Summary-only S3/local persistence, verified writes, fingerprints and stale warnings
- [x] Local/query/store/Streamlit tests, no eager telemetry or raw-data mutations
- [x] Agent live Garage all-round observation validation; sanitized results recorded
- [ ] Operator verifies new one-click UI and repeated-run experience

All-canary observations are not full dev-time harness re-validation or release
certification. Native clone remains skipped; TCP Accept/UDP Receive remain missing,
not explained by disabled Network startup. No sensor-side changes in this slice.

## Quality follow-up (authorized 2026-10-25)

- [x] Convert adversarial per-path/lifecycle/endpoint fixtures into committed regressions
- [x] Per-path activity matrix and required Start/Stop identity linkage/presence
- [x] Source-aware repeated-Start counts, preserve raw Clone/Exec observations
- [x] Retain wrong-protocol/directed-port candidates and check attributable extra rows
- [x] Keep incomplete/shared-PID attribution yellow and existing red findings red
- [x] Include quality warnings/counts in individual UI and persisted all-round summaries
- [x] VM isolated pinned Python environment and full suite including synthetic HTTP/S3
- [x] Sensor corrections and bounded VM actual-object/managed qualification (Wintap-owned)
- [x] Distinct UDP mode/socket and rename-aware per-path contracts; VM pilot delivers five families
- [ ] Operator package review and collection-host pilot; never unattended field rollout
