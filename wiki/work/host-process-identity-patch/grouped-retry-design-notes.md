---
title: "Grouped attribution retries: lifetime-aware lookup coalescing"
type: concept
confidence: speculative
grounded_by:
  - ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs
  - ../wintap/wintap/core/infrastructure/ProcessResolver.cs
  - ../wintap/wintap/core/infrastructure/BoundedEventTimeCache.cs
  - ../wintap/wintap/core/infrastructure/EventOwnerSelection.cs
  - wiki/work/host-process-identity-patch/package_host_results.md
policy: agent-editable
last_validated: 2026-10-24
repo_scope: wintap
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../wintap/wintap/core/infrastructure
tags: [proposal, attribution, retry, grouping, pid-reuse, bounded-memory]
---

# Proposal and status

User proposed organizing unresolved events by the identity they seek, looking up
one representative and applying a result to a burst. This is a promising **lookup
coalescing** optimization, not an approved implementation or a demonstrated fix.
Only wiki artifacts are being changed for this discussion.

## Current behavior and potential benefit

The retry queue stores individual `(message, attempt, due-time)` entries. Its 1,024
default capacity bounds pending messages across enabled streams, not distinct PIDs.
Resolution ordinarily uses PID plus each event's UTC event time, within one local
host's resolver. The durable query selects the latest containing birth, and the
bounded historical cache already indexes multiple lifetime entries by PID.
<!-- GROUND_TRUTH: ../wintap/wintap/core/infrastructure/AttributionRetryQueue.cs §pending; §TrySchedule; ../wintap/wintap/core/infrastructure/ProcessResolver.cs §BuildResolveProcessAtTimeQuery; ../wintap/wintap/core/infrastructure/BoundedEventTimeCache.cs §TryGet -->

Successful active/historical cache hits already reduce repeated database work.
Grouping could particularly reduce repeated **misses**, timers and retry callbacks,
and allow a newly registered identity to wake its pending group. It cannot remove
the bytes needed to retain every original event or guarantee a never-observed birth.
<!-- SYNTHESIS: proposed from the four infrastructure sources in frontmatter -->

## Safe grouping and result rules

1. **Unresolved key:** local resolver/host context + PID + lookup policy. Preserve
   each member's event time; use time-ordered subgroups to separate possible lifetimes.
   A shared unknown sentinel is never a grouping identity. Cross-host/namespace
   aggregation would need explicit host/namespace scope absent from this local queue.
2. **Resolved key:** authoritative process instance (`pid_hash`/canonical birth),
   after evidence is obtained. PID alone cannot distinguish reuse. Preserve per-event
   policy differences such as the Windows registry teardown exception; do not replace
   producer-prepopulated authoritative identities with representative guesses.
3. **Success:** one representative lookup can supply a lifetime candidate. Apply it
   only to members whose event times are covered by that authoritative lifetime;
   unresolved members stay pending or receive another lookup. A range lookup returning
   all overlapping lifetimes is a possible later alternative. Respect intervening
   reused-PID births even if an older record has no observed Stop.
4. **Miss:** means “not known at this lookup,” not “this process never existed.” Do not
   deny a whole PID group permanently. Any reused miss result needs event-time scope,
   bounded age and invalidation on relevant lifecycle/evidence changes; unrelated
   event times can have different results even within one PID.
5. **Deadlines:** keep original per-event arrival, attempts and deadline. New members
   must not repeatedly extend older members' budgets; cancellation/shutdown needs
   explicit outcomes. Share scheduling, not an unbounded wait or a blanket verdict.

<!-- SYNTHESIS: safety constraints derived from ProcessResolver.cs §BuildResolveProcessAtTimeQuery, EventOwnerSelection.cs §ResolveOwner, BoundedEventTimeCache.cs §TryGet and the observed admission failures; not implemented -->

## Two separate time controls

- **Coalescing interval / retry wait:** adjustable amount of waiting to share work.
  Shorter favors latency; longer may reduce lookups but increases backlog and memory.
  Identity-registration notifications could wake groups early without waiting for a timer.
- **Identity validity interval:** process start through exit (or qualified active
  evidence), with reused-PID boundaries. This is determined by evidence, **not** an
  adjustable tolerance that stretches one identity over nearby events.

Example: PID42 has one lifetime at10.000–10.100 and another at10.200–10.300. A
200ms coalescing bucket may contain events from both; lookup success for an event
at10.050 cannot label an event at10.250. It requires a separate lifetime result.

## Capacity and evidence guardrails

- Bound retained **events and bytes**, group count, per-group occupancy and work per
  turn. Replacing “1,024 events” with “1,024 unlimited PID groups” hides a memory increase.
- Fairness: one noisy PID must not monopolize retained space or delay other groups.
- Preserve all member payloads/counts/timestamps and observable final outcomes.
  Grouping resolution is not telemetry aggregation, suppression or downstream delivery.
- Receipts should distinguish unique lookup work, queued members, groups, resolved
  members, refusals, deadlines, late-birth wakeups, PID-reuse splits and durable fates.
- Aggregate capacity-refusal equality in revision6 supports pressure, not proof that
  grouping alone closes attribution. All199affected PIDs have final containing
  lifetimes, but their registration timing remains unavailable.

Evidence: [[wiki/work/host-process-identity-patch/package_host_results]].

## Suggested evaluation, not implementation authorization

1. Instrument bounded admission/final-fate and lifecycle-registration timing first;
   measure distinct unresolved lifetime/PID groups and repeated lookup work.
2. Test a default-off grouped scheduler under comparable event/byte/wait budgets.
3. Regression cases: same-process burst, reused PID in one time bucket, out-of-order
   births/exits, mixed valid/invalid times, late birth after a miss, no birth,
   per-member deadline, group overflow/fairness, shutdown and downstream exceptions.
4. Independently compare identity, coverage, conserved counts, CPU/lookup load,
   retained bytes, latency and shutdown completion against the same-binary baseline.

Related: [[wiki/concept/wintap-ecosystem-glossary]],
[[wiki/work/host-process-identity-patch/investigation_mitigation_plan]].
