---
title: "Network endpoint normalization: implementation plan"
type: workflow
confidence: high
grounded_by:
  - ../wintap/wintap/core/etl/transform/NetworkActivity.cs
  - ../wintap/devtools/network_endpoint_smoke_test.py
  - ../Wintappy/wintap_dbt/models/silver/process_conn_incr.sql
policy: agent-editable
last_validated: 2026-10-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: developer
status: reviewed
source_paths: ../wintap/wintap/core/etl; ../wintap/devtools; ../Wintappy/wintap_dbt; streamlit/projects/SmokeTests
tags: [tcp, network-events, normalization, regression-tests]
---

# Scope and approval

User authorized implementing the shared sensor/analytics fix and regression
tests, then added same-host separate-process and single-process socket cases.
Wintap owns normalization/producers; Wintappy owns offline counter SQL;
Wintap-Analytics owns the dashboard and shared knowledge base. Existing branch
and unrelated dirty work remain intact; no commits/pushes or database repair.

## Done checklist

- [x] Replace stale inbound string matching with explicit enum classification;
  preserve legacy slash names and reject unclassified names.
- [x] Preserve directed SourcePort/DestinationPort in normalized network parquet.
- [x] Test receive/accept/copy/send/client/server semantics, all network enum
  members/legacy aliases, same-IP/same-PID and unknown-name rejection.
- [x] Normalize canonical DBT and legacy SQL counter comparisons; add actual-SQL
  fixture tests and a DBT unknown-name gate.
- [x] Add a literal/vocabulary audit with self-tests, including other event-domain
  direct comparisons; report the independent ParquetWriter uppercase STOP finding.
- [x] Make endpoint confirmation the normal-ETL network-smoke default; add standalone
  same-host/separate-PID and same-PID generator/validator and independent dashboard checks.
- [x] Build Linux/Windows targets, run regression suites and isolated Ubuntu
  source-build capture; independently confirm mounted results on Mac.
- [ ] Rebuild/install the Debian package containing this fix (old service still running).
- [ ] Live Windows ETW validation; cross-compile/unit tests are not live ETW proof.
- [ ] Separately authorize historical-data repair/rebuild and investigate the STOP
  comparison; IPv6 address storage and Accept/byte-completeness gates remain separate.

Results/commands: [[wiki/work/network-endpoint-normalization/verification]].
