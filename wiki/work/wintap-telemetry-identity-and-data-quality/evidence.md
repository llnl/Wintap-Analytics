---
title: "Evidence provenance: compact telemetry-quality closeout"
type: diagnostic
confidence: high
grounded_by:
  - /private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/telemetry-quality-retrospective-audit-20261024/archive-receipt.json
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: wiki/work; external qualification archives
tags: [audit, archive, provenance, retrospective, context-budget]
---

# Evidence retained without committing detailed audits

User approved condensing detailed audits for a small,meaningful commit. Original
JSON receipts remain local and are ignored by Git;full pre-condensation workstream
documents,receipts and harnesses were additionally archived outside the repo.
No failed capture,raw recording,source code or historical database was deleted.

## Verified pre-condensation archive

- Directory:`/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/telemetry-quality-retrospective-audit-20261024/`
- File:`audit-before-condensation.tar.gz` (3,840,232bytes).
- SHA256:`0d9474040e16129f2a15bc001e59bbe3a0c5dd5a49c7c13994d24c9fc80ea827`.
-193files/62,580,675original bytes;each archived file byte-compared to its original
  before condensation. Archive names retain original `wiki/work/<folder>/<file>` paths.
- Covered folders:`host-process-identity-patch`,`net10-dependency-prune`,
  `network-endpoint-normalization`,`duckdb-1-5-maintenance`,`duckdb-2-upgrade`.
  Python bytecode was excluded;source harnesses were included.
<!-- GROUND_TRUTH: /private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/telemetry-quality-retrospective-audit-20261024/archive-receipt.json -->

**Storage limit:** this is a machine-local temporary archive,not a published or
durably backed-up evidence service. Move it and its receipt to approved durable
storage before cleaning that directory or expecting another machine to reproduce
the audit. Verify the hash after transfer. A cloned repo has summaries,not the archive.

## Selective retrieval map

| Claim | Original archive member(s),under `wiki/work/host-process-identity-patch/` unless noted |
|---|---|
| Historical QA/counters | `sample_db_audit_results.json`, `experiment_sample_projection.json` |
| Identity/recovery and earlier failures | `experiment_results.md`, `package_host_results.md`, `package_r6_shutdown_summary.json`, `package_r3_loss_detail.json` |
| Precision/protected fields | `timestamp_and_trace_results.md`, `package_r9_time_same_macro_control_comparison.json` and `package_r9_time_*_qualified_v2.json` |
| Startup/callback delivery gaps | `delivery_diagnostic_results.md`, `package_r12_tcp_projection_gap.json`, `package_r13_tcp_undrained_rows.json` |
| Shutdown cause/final delivery | `package_r14_shutdown_cause.json`, `package_r17_delivery_milestone.json`, `shutdown_delivery_results.md` |
| Pressure envelope | `pressure_final_results.json`, `pressure_final_state.json` |
| Preserved oracle failure/cause | `package_r20_pressure_summary.json`, `package_r20_pressure_oracle_cause.json`, `package_r20_pressure_capture_scope_recheck.json` |
| Runtime/dependency baseline | `wiki/work/net10-dependency-prune/verification.md`, `wiki/work/duckdb-1-5-maintenance/verification.md` |

Raw/native qualification archives are separate from this document archive. Their
host paths,local archive hashes and manifests are recorded in the original receipts;
recent roots include `r14-shutdown-evidence`,`r16-shutdown-evidence`,
`r17-shutdown-evidence` and `r{18,19,20,24,25,26,27}-shutdown-evidence` under the same
approved OpenCode temporary root. The final preservation audit verified28pressure
archives and262source matches. Final qualified package SHA256:
`e4cd1014898d2e0cd6ef7901b3795864ca9274c93aae72a4bdc0ecbdd539b302`.

Use archived receipts with the retained Python harnesses for historical replay;
do not expect generated audit JSON to exist in a fresh checkout. Normal future
context should load the brief and verification summary,not this inventory or all rounds.
