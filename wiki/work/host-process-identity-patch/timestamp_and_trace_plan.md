---
title: "Timestamp precision fix and bounded attribution provenance"
type: workflow
confidence: medium
grounded_by:
  - ../Wintappy/wintap_dbt/macros/time.sql
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - ../wintap/wintap/core/infrastructure/EventChannel.cs
  - wiki/work/host-process-identity-patch/collection_edge_results.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintappy/wintap_dbt; ../wintap/wintap/core/infrastructure
tags: [precision, attribution, diagnostics, bounded, verification]
---

# Approved continuation

User approved proceeding with the integer timestamp fix and admission/registration/
final-fate diagnostics after revision8. This authorizes scoped Wintappy/Wintap
source edits and isolated qualification; preserve all unrelated changes and failed
experiments. No historical repair, production rollout, queue-sizing change or
grouped-retry implementation. Existing installed revision7 remains the runtime
control until a verified diagnostic package is ready.

# Timestamp semantics

- Preserve timezone-aware timestamp output for numeric FILETIME, subtract epoch
  using integer arithmetic, floor to microseconds (including pre-Unix dates).
- Raw100ns FILETIME remains unchanged. Non-microsecond values lose only the declared
  submicrosecond remainder; never hash the derived timestamp or relax raw identity.
- Remove DOUBLE parsing from the generic integer-FILETIME timestamp helper. Null/
  malformed/out-of-range text stays null; integer text must not be rounded first.
- Existing floating seconds convenience fields remain approximate, not identity
  evidence. Current DBT minute grouping must not use rounded floating seconds.
- Preserve timestamp input semantics, test UTC and non-UTC sessions, all current
  process/file/network/registry/image-load consumers and12saved collector births.

# Done checklist

- [x] Implement exact integer FILETIME timestamp/minute macros and tests.
- [x] Verify focused/broad current SQL suites; preserve pre-existing config failure.
- [x] Replay12captured collector births into fresh DBT outputs, exact birth gates.
- [x] Compare identity/counters/row counts with pre-fix outputs; document only
  intended timestamp/minute-bin differences and unchanged raw files.
- [x] Add default-off bounded diagnostic writer and queue/registration/handoff
  receipts; observer failures/drop/truncation must not change telemetry behavior.
- [ ] Unit/native qualification and isolated diagnostic capture; no premature
  saturation/final-fate conclusions from successful handoff or incomplete traces.
  - [x] Native240tests and Linux build;bounded observer/control tests pass.
  - [x] Extend prepared-producer/aggregate/sender/serializer/parquet receipts;244tests.
  - [x] Build self-contained diagnostic package and verify private apphost startup.
  - [x] Complete scoped off/on observer controls and finalized-output row joins:
    revision11fourrounds;revision10refusals/shared-root failures preserved.
  - [x] Self-contained diagnostic package/private capture and exported-output row joins.
  - [ ] Broad producer→output conservation:revision11TCP54→50Esper→serializer per
    host at revision11; revision13 fixes demonstrated startup admission but AXON
    failed accepted→drained (six counts/two rows) at revision13;revision16conserves
    observed54AXON/60CALDERAcounts after exact shared-defect reproduction/correction.
    - [x] Exact TCP query deployment/listener, callback initialization and projection
      receipts; diagnostic projection→row IDs do not alter raw schemas.
    - [x] Deterministic real production-context/TCP-EPL control: pre-deployment inputs
      are not replayed; registration-first conserves8/8. Native247tests/Linuxbuild pass.
    - [x] Fresh exact live registration/projection evidence and bounded Linux-only,
      default-off readiness correction; revision13 off/on controls preserve strict
      identity/conservation/workload gates and prove collector admission ordering.
    - [x] Observed broadTCP delivery under bounded experimental control:revision14
      proves completed-drain→late-accepted/undrained rows onCALDERA;revision16passes
      producer→projection→accepted→drained→enqueued→finalized/raw on bothhosts.
      No arbitrary sleep, historical13boundary reconstruction or production drain claim.
    - [x] Interior-stimulus samecandidate repeat17/final receipts:58/58TCPcounts
      perhost,allstimuli interior at1/5/10/20s,262source matches/preservation pass.
    - [ ] Separate acceptance: Full kernel/durable/
      resource/custom-EPL/service deadline/rollout acceptance remains outside this gate.
  - [ ] Reproduce preserved saturation/AXONloss/workloadTCPfailures,then cause fix.
- [x] Record verification/results and update canonical time/boundary/glossary notes.

Results:[[wiki/work/host-process-identity-patch/timestamp_and_trace_results]]. Strict
metadata equality fails and is preserved;same-macro controls isolate unordered
selection. Protected counters/process identities/raw precision pass;no blanket
file-ID/display stability or runtime-loss repair claim.

Delivery continuation:[[wiki/work/host-process-identity-patch/delivery_diagnostic_results]].
Exact shutdown continuation:[[wiki/work/host-process-identity-patch/shutdown_delivery_results]].

# Trace scope / safety

Receipts must distinguish retry admission, invocation, resolution/registration,
Esper handoff and durable output. Per-event correlation is diagnostic-only; do not
change identity or the raw schema. Bound rows/bytes/queued records and report
trace refusal/truncation/IO errors. Default-off instrumentation must not perform
I/O, allocate event payload histories or invoke observers on ordinary paths.
An Esper send is **not final durable fate**; unjoined or missing output stays
explicitly unproven. Producer-side loss before EventChannel requires separate
native/aggregator counters and cannot be explained by retry traces alone.
