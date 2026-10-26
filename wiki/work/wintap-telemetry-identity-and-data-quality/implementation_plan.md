---
title: "Reconstructed implementation: telemetry identity and data quality"
type: concept
confidence: high
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/verification.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/evidence.md
policy: agent-editable
last_validated: 2026-10-26
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../wintap; ../Wintappy; ../Lintap; wiki/work
tags: [feature-work, retrospective, implementation, closeout]
---

# Reconstructed workflow

This summarizes the actual progression; it is not a pre-implementation plan.
Completed items mean scoped implementation/verification,not release certification.

- [x] Establish the .NET10 package baseline and reproduce real-data QA defects.
- [x] Centralize process identity and persist host-unique AgentIds.
- [x] Correct shared TCP endpoint orientation and downstream activity comparisons.
- [x] Fix lifetime summary grouping/counters; independently audit the supplied data
  without modifying the historical database.
- [x] Acquire canonical lifecycle inputs and reject callback/exit-time identities;
  qualify bounded recovery while preserving missing-birth negative controls.
- [x] Include collector Process/Refresh telemetry without self-I/O feedback or
  synthetic lifecycle observations; separate collection edges from lifetime bounds.
- [x] Upgrade supported DuckDB1.5 dependencies and correct integer timestamp precision;
  verify fresh canonical DBT output and protected-field conservation.
- [x] Add bounded provenance through admission,registration,projection and final output.
- [x] Prove startup subscription loss; qualify experimental readiness ordering.
- [x] Prove late post-drain acceptance; qualify terminal-window/callback shutdown ordering.
- [x] Repeat independent interior and shutdown-tail pressure controls through256 children.
  Preserve and fix the demonstrated pressure-oracle time predicate,not the sensor.
- [x] Condense results,retain failures/evidence provenance,and hand off the next phase.

## Deferred to the user's next phase

Upgrade oversight correction (2026-10-25):
[[wiki/work/wintap-telemetry-identity-and-data-quality/runtime_alignment_plan]] —
all 13 C# projects now evaluate to .NET 10; exact-SDK packaging checks, runtime
metadata, diagnostics/sample targets and active provision/run defaults are corrected.
Legacy installer snapshots are explicitly not the release path. Artifact and live
acceptance remain separate gates, not implied by source alignment.

- [x] Correct .NET 10 source/configuration oversights and add SDK/TFM drift tests.
- [x] Add operator-approved periodic Linux stimulus runner with existing raw smoke
  evidence export, private local manifests and deferred capture validation.
- [ ] Pilot periodic runner on a native test host and verify Garage evidence arrival.

- [ ] Clean native/eBPF and self-contained package qualification on selected hosts.
- [ ] Multi-day real-host collection with declared resource/deadline and coverage gates.
- [ ] Review whether experimental controls remain opt-in or become supported behavior.
- [ ] Windows live regression if cross-platform release acceptance is intended.
- [x] Scoped diff/commit review on dedicated feature branches; preserve unrelated work
  and avoid generated audit payloads. Push/PR publication is a separate operation.

Actual saturation,historical failure reconstruction,kernel/durable fate and metadata/
OS-label defects remain explicit follow-ups,not hidden unchecked delivery milestones.
This retrospective alone does not authorize additional execution or rollout.

## Authorized quality follow-up — 2026-10-25

- [x] Analytics adversarial regressions and source-aware per-path/lifecycle/endpoint checks
- [x] Wintap single-owner Accept and kernel-provenance/success-return UDP corrections
- [x] Add version-gated operation/PID-filter/sampling/byte receipt facts
- [x] Split independent UDP client modes and record exact IPv4 socket/per-path expectations
- [x] Build all12 tracer objects and managed sensor with SDK10.0.402
- [x] Strict actual-object old/fixed15-check comparison, zero-length/failure/cleanup negatives
- [x] Expanded shared network/receipt/identity/resolver/root tests:159 passed
- [x] Normal-ETL five-family VM pilot evaluation and evidence delivery review; uncertainty retained
- [x] User-approved greenfield Linux file-case and additive process-source projections;
  180 managed/94 dashboard tests and fresh normal-ETL five-family pilot, limits retained
- [x] Operator-reported native package deployment and first independent canary rounds
- [ ] Trusted package/payload provenance and remaining on-target qualification

Detailed limits: [[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]].

## Approved advisory bundle and RHEL follow-up

- [x] Reject malformed/conflicting legacy source tokens; explicit-column null remains unknown
- [x] Detect known endpoint contradictions even with null companion fields; consistent-role matching
- [x] Carry unlinkat/AT_FDCWD event-time base identity and conservatively resolve learned bases
- [x] Unit regressions for closed/reused/missing/evicted/namespace-qualified directory identities
- [x] Normal-ETL case-only pair and relative/cwd Delete proof; distinct sensor keys
- [x] Bounded24-lifetime UDP turnover48-check qualification and15-check return regression
- [x] Monotonic observer timing and outer load/attachment/cleanup deadline
- [x] Ubuntu build/targeted tests and five-family pilot; clean actual collector exit0
- [x] Prepare read-only RPM payload verifier and explicit post-delivery validation command
- [x] Verify fingerprinted CLI summary reload without telemetry rescan
- [x] Operator reports native RHEL9 RPM build/deployment and two initial S3 canary rounds reviewed
- [ ] Independently verify trusted RPM digest and installed payload/object provenance
- [ ] Stop/settle/review the two parallel overnight rounds separately; preserve overlap uncertainty
- [ ] Resolve absent `sched_exec` observations without weakening source-provenance gates
- [ ] Complete scoped RHEL validation and record remaining skips/limitations
- [ ] Qualify summary reuse/staleness during ongoing Garage uploads and longer multi-host runs

The TCP continuation below resolves the two partial provenance checks. Broader
Windows/logging-test qualification remains open; downstream Wintappy IDs remain
separately scoped. Procedure:
[[wiki/work/wintap-telemetry-identity-and-data-quality/rhel9_validation]].

## Authorized TCP continuation (completed before RHEL deployment)

- [x] Isolate local-port loss in EOF/close output and reproduce with prior actual object
- [x] Preserve complete cached tuples and sample clocks across state changes
- [x] Prevent state callback cache resurrection after close; clear cache on new connect
- [x] Gate TCP tuple receipt contract on actual object marker and attached lifecycle hooks
- [x] Add strict10-check actual-object data/half-close/delayed-EOF/close regression
- [x] Complete fresh normal-ETL five-family qualification with unchanged endpoint assertions
- [x] Record tests/results, update package validation, and commit/push corrected bundle

Current next-step handoff:
[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]].
