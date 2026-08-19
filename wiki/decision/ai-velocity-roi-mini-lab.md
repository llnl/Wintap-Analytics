---
title: "AI Velocity and ROI Mini-Lab"
type: decision
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/concept/llm-assisted-feature-workflow.md
  - ../Wintap-Analytics/wiki/concept/feature-work-template.md
  - ../Wintap-Analytics/wiki/concept/metrics-template.md
  - ../Wintap-Analytics/wiki/work/improve-windows-process-collection/metrics.md
  - ../wintap/CLAUDE.md
  - ../wintap/.claude/agents/engineer.md
policy: agent-editable
last_validated: 2026-08-19
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: accepted
source_paths: wiki/concept/metrics-template.md; wiki/concept/llm-assisted-feature-workflow.md; wiki/concept/feature-work-template.md; ../wintap/CLAUDE.md; ../wintap/.claude/agents/engineer.md
tags: [decision, workflow, metrics, llm, velocity, roi, lead-time, throughput]
---

# AI Velocity and ROI Mini-Lab

**Date:** 2026-08-17 (v1) · **Revised:** 2026-08-19 (v2, scheduled post-pilot revision)
**Status:** Accepted

## Revision History

- **v1 (2026-08-17):** Initial protocol. Headline: sealed solo-hours estimate
  vs. a measured human-attention proxy (15-minute-gap message-timestamp
  clustering). Carried an explicit pilot expectation: one planned template
  revision pass after the first real feature closed.
- **v2 (2026-08-19, this revision):** The scheduled post-pilot revision, after
  the pilot feature `improve-windows-process-collection` closed 2026-08-19.
  Headline metrics pivot to boundary/outcome measures: **time-to-availability
  (lead time)** plus **throughput (counterfactual-hours delivered per
  window)**. Sealed questions re-posed in calendar terms under the existing
  displacement ratchet. The attention proxy is demoted to an optional,
  coverage-annotated diagnostic. Pilot data and lessons are recorded in
  [[wiki/work/improve-windows-process-collection/metrics]].

## Context

The LLM-assisted feature workflow ([[wiki/concept/llm-assisted-feature-workflow]])
now runs real features end to end (pidstat collector, process-table retention,
Windows process collection), but the ecosystem has no structured record of what
the AI workflow actually buys. Anecdotes compound poorly; even crude numbers
compound well.

This decision adds a per-feature measurement overlay — a "mini-lab" — to the
existing workflow. It is explicitly **calibration data and directional
evidence, not rigorous science**: single developer, self-reported
counterfactuals, small N. The design accepts large error bars on purpose and
optimizes for zero friction instead of precision.

**Why v2 changed the headline (pilot lessons).** The Architect's full
methodology spans two AI harnesses: Claude Code is the "Architecture & Design"
harness (specification); OpenCode running gpt-5.6-sol is the "Engineering &
Development" harness (implementation and test). The v1 attention proxy mined
only Claude Code transcripts, so it structurally measured at most one channel
of human attention. Beyond that structural gap, the three-year trajectory is
toward parallel and delegated agentic development — models improving, human
agentic skill improving, features increasingly concurrent — which would keep
invalidating any mechanism-level metric. The v2 headline metrics are therefore
**boundary/outcome measures**, immune to changes in tools, techniques, and
methodology: they observe only when a feature opens and when it becomes
available, plus how much counterfactual work ships per unit of calendar time.

## Decision

Every feature run through the LLM-assisted feature workflow carries an
optional metrics overlay with the following protocol. Artifacts:
`wiki/work/<feature-slug>/metrics.md` per feature (skeleton and field
definitions in [[wiki/concept/metrics-template]]), plus a
`## Sealed — human estimates` section in the feature's `interview.md`.

### Headline metric: time-to-availability (lead time)

The headline per-feature number is **raw calendar time from feature open to
first availability**:

- **Open boundary:** the `opened` date — the interview / design kickoff.
  Queue or backlog wait before that is deliberately invisible to this metric.
- **Availability boundary:** the **first Architect-accepted validation event
  that satisfies the feature brief's acceptance criteria**, evidenced by a
  dated artifact (a `verification.md` entry or an audit). Observable artifacts
  on both ends — no recollection.
- **Weekends, vacations, and away-time are deliberately INCLUDED.** Normative
  rationale, in the Architect's own words: under the current Architect-gated
  workflow, weekend time is "simply IDLE and UNUTILIZED"; as agentic, parallel
  and delegated development matures, "this idle time turns into productivity
  time and our velocity goes up — exactly what the mini-lab should capture."
  Progress-while-away is part of what is being measured. A business-day
  variant was considered and rejected (see Alternatives Considered) because it
  would define that improvement out of existence and reintroduce work-calendar
  bookkeeping friction.

### Companion metric: throughput

**Counterfactual-hours delivered per rolling window:** the sum of the sealed
solo-hour estimates (the per-feature throughput weights) of features closed in
the window. Raw features-closed-per-window may be recorded alongside, but the
weighted figure is primary.

Weighting by counterfactual size normalizes feature count against **scope
inflation**: the WPC close-out answer — the UserSid reverse-engineering and
PEB command-line work would not have been attempted solo at all — is the
standing evidence that feature scope grows with capability, so raw feature
counts understate delivered work.

The lead-time/throughput pair is the standard queueing characterization
(Little's Law; cf. DORA's lead time + deployment frequency): if parallel
features stretch individual lead times, throughput records the compensating
gain.

### Sealed dual estimates at feature open (v2 currency: calendar)

- The human answers exactly **two** onboarding-interview questions, recorded
  in a marked `## Sealed — human estimates` section of the interview record:
  1. **Solo counterfactual, calendar-posed:** "If you had started this
     feature solo, without AI, on the open date, on what date would it
     realistically have been available?" The estimate and the actual thereby
     share the calendar currency, and the counterfactual absorbs weekends and
     distractions too. The **hours reading of the same estimate is retained**
     as the feature's throughput size weight (hours are never compared
     against elapsed time, so the unit is safe there).
  2. **Predicted calendar time-to-availability with the AI workflow** — same
     calibration game as v1's attention prediction, new currency. (This
     DISPLACES v1's "predicted attention hours" under the ratchet.)
- The Engineer, at exploration start, writes its own estimate of the same two
  calendar quantities to the feature's `metrics.md` **before** reading the
  sealed section — plus a one-line basis. **Independence is the point: an
  anchored estimate is worthless.** This sealed-before-reading rule is a
  standing rule in the Engineer agent definition
  (`../wintap/.claude/agents/engineer.md`).
- If the estimating agent has already seen the human's answers (e.g. the same
  session ran the interview), the seal is broken; it records no estimate.
  Missing data is fine (see never-gates).
- Reveal and comparison happen only at close-out.

### Per-unit quality loop (unchanged from v1)

At instruction-drafting time (post-exploration, pre-implementation), the
Engineer records a **per-unit development estimate plus a one-line basis** for
each instruction unit. Per-unit estimate vs. audit actual is a **quality
signal on instruction self-containedness**: development from a good
instruction document should estimate tightly; consistently blown per-unit
estimates indicate the instructions are not as self-contained as the
methodology claims.

### Human question budget: three, hard cap — with a ratchet

The metrics overlay may ask the human exactly **three** questions per feature:

1. Solo availability date (feature open, sealed; hours reading doubles as the
   throughput weight).
2. Predicted AI-workflow availability date (feature open, sealed).
3. "Would you have attempted this feature at all without AI?" (close-out).
   Unchanged from v1 — and it now does double duty as the **scope-inflation
   signal** that keeps the throughput metric honest.

No mid-flow questions, logging duties, or reminders for the human, ever.
**Ratchet rule:** any future proposed metrics question must displace an
existing one — the budget never grows to four. The v2 Q2 change is itself an
application of this ratchet (displacement, not growth). (This cap applies to
metrics questions only; the design interview's normal adaptive questioning is
unaffected.)

### Attention proxy: demoted to diagnostic (not deleted)

Human attention hours are **optional, best-effort, computed only when cheap,
always coverage-annotated** (e.g. "claude-code sessions only"), **never
headline, never gating**. When computed, it is done by the main session (not
the Engineer — the computation needs Bash/transcript access) under the same
normative v1 definition:

> Collect the human's in-session message timestamps across the feature's
> sessions, from feature open to final audit. Sort them. Messages within a
> **15-minute gap threshold** of the previous message belong to the same
> continuous attention block. Each block's duration is its last timestamp
> minus its first timestamp; **block durations sum to the attention figure.**
> A single-message block therefore contributes zero — a known, consistent
> undercount bias.

Standing multi-harness rule: if the proxy is ever computed across multiple
harnesses, **merge all human-message timestamps first and cluster once** —
never cluster per-harness and sum. No cross-harness (OpenCode) adapter is
built until a feature routes significant attention through that harness.

**Why keep it at all:** lead time and throughput are outcome metrics — when
they move, you cannot tell why. Attention is the mechanism probe that can
later distinguish "models got faster" from "the human learned to stay out of
the way."

### Never-gates rule

Metrics never block, delay, or nag the workflow. Skipped questions or missing
files = missing data, shrug, feature proceeds normally. No agent re-asks. A
feature with an empty or absent `metrics.md` is a normal feature.

### Close-out reveal

At feature close-out the Engineer:

1. Fills in actuals: the availability date and its anchoring artifact (with a
   one-line note on which acceptance evidence was chosen and why), the
   computed calendar lead time, the throughput weight from the unsealed solo
   estimate's hours reading, and per-unit actuals from audits where
   derivable.
2. Unseals the interview's human estimates and copies them into `metrics.md`.
3. Tabulates estimates vs. actuals (human vs. AI vs. measured): estimated vs.
   actual availability dates, plus the rough ROI reading (solo calendar
   counterfactual vs. actual lead time, and API cost where available).
4. Records the close-out question's answer and a one-line findings note.
5. Records the attention diagnostic **only if** the main session supplied it,
   with its coverage annotation.
6. Folds a short summary into the wiki as part of the normal results fold-in.

### Ownership note

`../wintap/.claude/agents/engineer.md` and `../wintap/CLAUDE.md` sit outside
the standard directory-ownership table in the Wintap methodology. Edits to
them for this protocol (and any future revision) are **drafted by the Engineer
but land only via Architect review** — they are never self-approved plumbing
changes.

## Rationale

- **Boundary/outcome metrics survive methodology change.** Lead time and
  throughput observe only the feature's endpoints, so they remain comparable
  across harness changes, model upgrades, delegation-depth changes, and the
  shift to parallel feature work — exactly the changes the next three years
  are expected to bring. A mechanism metric (attention) would be invalidated
  by each of them.
- **Calendar inclusion is the point, not a bug.** Idle weekends under the
  current Architect-gated workflow are real elapsed time in which nothing
  ships; when delegated agents start converting that idle time into progress,
  the headline number should improve. Excluding weekends would hide the very
  effect the lab exists to capture.
- **Throughput guards against the parallelism artifact and scope inflation.**
  Parallel features individually stretch lead times (Little's Law); weighted
  throughput records the compensating gain, and counterfactual-hour weighting
  keeps growing feature ambition from masquerading as constant output.
- Sealed, independent dual estimates remain the cheapest calibration data on
  both the human's and the AI's forecasting skill; anchoring destroys that
  signal, hence the seal. Posing them in calendar terms makes estimate and
  actual directly comparable.
- The per-unit estimate loop turns the methodology's central claim
  ("instructions are self-contained") into something falsifiable at near-zero
  cost.
- A three-question hard cap with a displacement ratchet is what keeps this
  overlay alive: measurement systems die by accreting reporting burden onto
  the human. The never-gates rule serves the same goal.
- The demoted attention proxy is retained because outcome metrics cannot
  explain their own movement; a cheap, consistent, coverage-annotated
  mechanism probe can.

## Honest Limitations

Recorded deliberately, per the Architect:

- **N=1 developer**, self-reported counterfactuals, small feature count — this
  is directional evidence and self-calibration data, not rigorous science.
- **Calendar noise dominates short features:** a 3-day weekend is a 50–100%
  relative distortion on a ~6-day feature. Accepted as a consistent bias that
  shrinks with feature size and with N; short-feature lead times should be
  read with that in mind.
- **The solo calendar counterfactual remains unverifiable** (plausibly ±2x),
  exactly as the solo-hours counterfactual was in v1. Changing its currency
  does not make it checkable.
- The attention diagnostic, when computed, undercounts (single-message blocks,
  off-session reading, thinking away from keyboard) and may cover only one
  harness — hence the mandatory coverage annotation.
- Estimates may drift toward "safe" values once the estimators have seen prior
  features' reveals; cross-feature learning is a feature for calibration but a
  confound for ROI claims.
- API cost capture is best-effort; when unavailable it is simply missing data.

## Consequences

- The interview template's sealed section is re-posed in calendar terms
  ([[wiki/concept/feature-work-template]]); the metrics file format gains
  lead-time, availability-anchor, and throughput-weight fields and demotes the
  attention block to a coverage-annotated diagnostic
  ([[wiki/concept/metrics-template]]).
- The Wintap Engineer agent definition's standing rules change currency
  (calendar-posed sealed estimates) and close-out duties (compute lead time
  and throughput weight; attention only if supplied). `../wintap/CLAUDE.md`'s
  mini-lab paragraph changes accordingly. Both land only via Architect review
  per the ownership note.
- The main session's close-out duty becomes: confirm the availability anchor;
  compute the attention diagnostic **only when cheap**, and hand it over with
  its coverage annotation.
- Pre-v2 metrics files (the WPC pilot) are not rewritten; they gain a clearly
  marked v2 addendum re-recording the feature under the new metrics with
  caveats ([[wiki/work/improve-windows-process-collection/metrics]]).
- Cross-feature aggregation (rolling-window throughput) becomes possible once
  N grows; until then per-feature records simply accumulate the weights.

## Alternatives Considered

- **Business-day lead time (exclude weekends/vacations):** rejected — it would
  define the anticipated progress-while-away improvement out of existence and
  reintroduce work-calendar bookkeeping friction.
- **Full attention pivot / cross-harness adapters now (mine OpenCode
  transcripts too):** deferred — no feature yet routes significant attention
  through the second harness; building adapters ahead of need is friction
  without signal.
- **Abandoning attention measurement entirely:** rejected — kept as the
  optional mechanism diagnostic, because outcome metrics cannot explain their
  own movement.
- **Human time logging / self-report:** rejected (v1) — imposes exactly the
  ongoing human burden the three-question cap exists to prevent.
- **Precise instrumentation (wall-clock trackers, editor telemetry, per-turn
  accounting):** rejected (v1) — precision below the counterfactual noise
  floor is wasted effort and adds workflow friction.
- **No measurement (status quo):** rejected (v1) — anecdotes about AI velocity
  do not compound; even crude sealed-estimate calibration does.
- **Unsealed estimates:** rejected (v1) — anchored estimates are worthless as
  calibration data.

## Supersedes / Superseded By

None. This overlays [[wiki/concept/llm-assisted-feature-workflow]] and the
Wintap Architect / Engineer / Developer methodology without changing either's
core flow. v2 revises this decision in place (see Revision History); there is
no separate superseded document.
