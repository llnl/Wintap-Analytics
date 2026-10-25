---
title: "Integer timestamps and bounded trace: qualification summary"
type: diagnostic
confidence: high
grounded_by:
  - ../Wintappy/wintap_dbt/macros/time.sql
  - ../wintap/wintap/core/infrastructure/AttributionTrace.cs
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../Wintappy/wintap_dbt; ../wintap/wintap/core/infrastructure
tags: [precision, diagnostics, conservation, verification]
---

# Integer timestamp proof

Canonical FILETIME macros subtract the epoch as HUGEINT,floor to UTC microseconds
and emit TIMESTAMPTZ. Integer text never routes through DOUBLE. Raw100ns identity
inputs are unchanged;older floating convenience fields remain approximate.

209focused SQL tests and12fresh full DBT builds pass:12/12collector births restored,
2,900process lifetimes independently verified.216common model tables preserve
protected keys,counters and multiplicities.

Strict metadata equality **failed and remains preserved**. Twelve same-old-macro
controls reproduced unordered `any_value` metadata/executable file-ID drift without
protected-field changes. This isolates drift;it does not accept deterministic
metadata/file-ID stability. Existing DATASET configuration test failure remains separate.

# Bounded diagnostics

Linux/create-new/default-off tracing records identity lookup,admission/retry,
registration,handoff and later delivery stages with weak diagnostic-only IDs.
Explicit queue/receipt/byte/string/close bounds report refusal,error or truncation;
incomplete histories cannot support absence claims. Raw schemas/identities unchanged.

Later exact delivery qualification:
[[wiki/work/host-process-identity-patch/delivery_diagnostic_results]],
[[wiki/work/host-process-identity-patch/shutdown_delivery_results]]. A handoff or final
rename is not complete kernel/fsync/upload proof. Original comparison failures,
control matrices and receipts:
[[wiki/work/wintap-telemetry-identity-and-data-quality/evidence]].
