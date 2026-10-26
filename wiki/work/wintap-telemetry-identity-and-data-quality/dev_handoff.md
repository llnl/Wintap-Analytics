---
title: "Developer handoff: telemetry identity and data quality"
type: concept
confidence: high
grounded_by:
  - wiki/work/wintap-telemetry-identity-and-data-quality/brief.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/verification.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/implementation_plan.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/rhel9_validation.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification.md
policy: agent-editable
last_validated: 2026-10-26
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../wintap; ../Lintap/packaging; ../Wintappy; validation/telemetry-soak; streamlit/projects/SmokeTests
tags: [feature-work, handoff, qualification, telemetry-quality]
---

# Continuation handoff — not a close-out or rollout approval

This feature remains open. The work is moving to another computer, so use this
page as the operational entry point and follow the linked wiki records; do not
depend on private shell history, local audit archives, or machine-specific files.

## Current position

- Wintap's TCP tuple-lifetime correction and Analytics validation changes are
  committed on the existing feature branches: Wintap `c4f6b1d`, Analytics
  `a293775`. No PR/merge is implied.
- The user reports that a new native RHEL 9 x86_64 RPM was built and deployed.
  Two completed S3-delivered rounds (one with, one without the optional clone
  helper) have been inspected read-only. Declared network, file, and process
  observations—including TCP endpoint provenance—were present without reported
  contradictions. The helper-enabled dedicated clone suite also passed. Omitting
  the helper correctly leaves that dedicated suite skipped.
- These rounds are not full acceptance. Process-start provenance did not include
  `sched_exec`, although the startup capability receipt reports the corresponding
  hook attached. The three-source projection gate therefore remains incomplete.
  Keep unknown provenance unknown; do not infer the missing source from hook
  attachment or relax the gate.
- The user then started two additional canary runners in parallel for an overnight
  observation, one with and one without the helper. Their final manifests, uploads,
  stop status, and validation have not yet been reviewed. Treat them as pending.
- The remote inspection was read-only and did not save summaries or mutate S3.
  Operator-reported package build/deployment is not independent RPM-to-installed-
  payload proof. Check whether the sanitized package-verifier result and trusted
  package/object hashes are available before claiming artifact provenance.

No test-host names, addresses, process identifiers, bucket/prefix/configuration,
raw event details, or private credentials belong in this wiki. Record only
sanitized conclusions and unresolved questions.

## First actions on the new computer

1. Read [[wiki/work/wintap-telemetry-identity-and-data-quality/verification]],
   [[wiki/work/wintap-telemetry-identity-and-data-quality/implementation_plan]],
   and [[wiki/work/wintap-telemetry-identity-and-data-quality/rhel9_validation]].
   Read [[wiki/work/wintap-telemetry-identity-and-data-quality/network_return_qualification]]
   for producer semantics and known limits.
2. Ask the user to stop the two overnight generator sessions when ready. Do not
   stop or restart the collector. Confirm generator exit/status and wait for normal
   upload/flush before treating S3 listings as settled.
3. In the approved private SmokeTests configuration, refresh read-only S3
   discovery and select each exact `canaryRoundId`/round independently. Do not
   group by time proximity or combine the helper/no-helper rounds. Because both
   generators ran concurrently and telemetry rows do not carry a round ID, inspect
   overlap/ambiguity warnings; do not force ambiguous events into either round.
4. Re-run explicit validation against the final settled snapshot. Confirm the TCP
   tuple contract and attached-hook facts, TCP/UDP endpoint checks, exact file and
   process assertions, expected helper skips, and all source-provenance outcomes.
   Keep incomplete results yellow; do not publish raw rows or remote identifiers.
5. Investigate why `sched_exec` observations are absent despite the attached-hook
   receipt. Trace source emission through managed projection and delivered schema;
   preserve `ProcessStartSource` null/unknown behavior and add an adversarial
   regression before changing semantics. This is the leading unresolved coding/
   qualification item.
6. Verify the newly deployed RPM against an independently trusted RPM digest and
   installed payload if that proof has not already been performed. Correlate
   sanitized package proof with receipt object hashes; capability markers alone
   are not cryptographic provenance.
7. Refresh this handoff and the verification/plan/index/log with sanitized results.
   Do not close the feature until the overnight rounds, missing provenance source,
   package provenance, and explicitly accepted remaining limitations are resolved.

## Boundaries and preserved decisions

- Analysis/wiki lives in Wintap-Analytics; Windows/Linux sensor and telemetry
  projections are owned by Wintap; Lintap owns supporting packaging; Wintappy owns
  downstream DBT/DuckDB transformations. Wintappy's case-folded derived file ID is
  a separate unresolved downstream issue; this work did not change it.
- Use SDK **10.0.402**, DuckDB engine **1.5.6**, and official .NET wrapper
  **1.5.6.1**. DuckDB 2.0 remains held. Cross-RID lock-file restore/audit-cache
  limitations are documented in the verification record; preserve NuGet audit and
  TLS checks.
- Keep TCP bytes defined as requested-at-entry, sampled observations—not successful
  transfer or conservation counts. Keep UDP bytes as successful protocol-function
  return values, not syscall/packet conservation. Do not weaken endpoint or identity
  assertions to turn an incomplete result green.
- Keep Linux recovery/readiness/shutdown experiments default-off, retry capacity
  1024, and existing identity formulas/pins/security settings unchanged unless
  separately authorized. No automatic migration or historical raw-data rewrite.
- Canary tools generate stimuli only. They do not attach tracers, change settings,
  restart collectors, upload/clean up data, or certify capture completeness.
  `--clone-helper` is an optional target-architecture process/thread workload, not
  an observer or collector component.
- Never commit credentials, private configuration, host identifiers, raw telemetry,
  or detailed host-specific runtime evidence. Do not use force-push, rebase, merge,
  or publish a PR without separate direction. Preserve unrelated working-tree work.

## Still outside this handoff's acceptance claim

Historical loss/saturation closure; exact kernel-to-durable/upload fate; universal
resource, deadline, and count guarantees; forced socket-pointer reuse; IPv6 and
non-loopback wildcard endpoint coverage; full Windows live acceptance; multi-host
long-duration acceptance; and the Wintappy derived-ID issue remain open. A healthy
service or successful canary round does not close them.

Related entry points: [[wiki/work/wintap-telemetry-identity-and-data-quality/brief]],
[[wiki/work/wintap-telemetry-identity-and-data-quality/verification]],
[[wiki/tool/smoke-test-results-dashboard]],
[[wiki/tool/periodic-telemetry-soak-runner]].
