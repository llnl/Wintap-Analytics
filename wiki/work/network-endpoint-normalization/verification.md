---
title: "TCP endpoint normalization: verification summary"
type: diagnostic
confidence: high
grounded_by:
  - ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs
  - ../Wintappy/tests/test_network_activity_sql.py
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: network
audience: developer
status: reviewed
source_paths: ../wintap; ../Wintappy; streamlit/projects/SmokeTests
tags: [tcp, normalization, verification, retrospective]
---

# Cause and correction

Shared inbound normalization compared slash-style activity names against enum
strings,misassigning receive-local endpoints. DBT's same vocabulary mismatch left
basic TCP counters null. Explicit enum/legacy classification and directed-port
provenance correct these independently;historical raw assignments were not repaired.

Real-production regression tests,Linux/Windows cross-builds,actual-SQL fixtures and
independent dashboard checks pass. Ubuntu normal-ETL non-loopback tests verify Send
and Recv at both endpoints for separate client/server processes and a single process
owning both ends. Missing provenance/observations cannot yield endpoint PASS.

Windows compilation is not live ETW acceptance. IPv6 storage,TCP Accept completeness,
receive-byte accuracy,OS-family labeling and historical repair remain separate.
The event-name audit's independent uppercase `STOP` comparison finding was reported,
not silently folded into this fix. Final updated-package qualification is next-phase work.

Original test commands,host/socket selectors and detailed results:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
Semantics:[[wiki/event_type/network-events]].
Plan:[[wiki/work/network-endpoint-normalization/implementation_plan]].
