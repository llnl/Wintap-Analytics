---
title: "AI Velocity and ROI Mini-Lab"
type: decision
confidence: high
grounded_by:
  - ../wintap/developer_docs/design/velocity-pitch-2026-08-19.md
  - ../Wintap-Analytics/wiki/concept/velocity-metric.md
  - ../Wintap-Analytics/wiki/concept/llm-assisted-feature-workflow.md
  - ../Wintap-Analytics/wiki/concept/feature-work-template.md
  - ../Wintap-Analytics/wiki/concept/metrics-template.md
  - ../Wintap-Analytics/wiki/metrics.md
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
source_paths: wiki/concept/velocity-metric.md; wiki/concept/metrics-template.md; wiki/concept/llm-assisted-feature-workflow.md; wiki/concept/feature-work-template.md; wiki/metrics.md; ../wintap/CLAUDE.md; ../wintap/.claude/agents/engineer.md
tags: [decision, workflow, metrics, llm, velocity, roi, lead-time, portfolio-velocity, solo-hours]
---

# AI Velocity and ROI Mini-Lab

**Date:** 2026-08-17 (v1) · **Revised:** 2026-08-19 (v2, then v2.1 same day)
**Status:** Accepted

## Revision History

- **v1 (2026-08-17):** Initial protocol. Headline: sealed solo-hours estimate
  vs. a measured human-attention proxy (15-minute-gap message-timestamp
  clustering). Carried an explicit pilot expectation: one planned template
  revision pass after the first real feature closed.
- **v2 (2026-08-19, scheduled post-pilot revision):** After the pilot feature
  `improve-windows-process-collection` closed 2026-08-19: headline metrics
  pivoted to boundary/outcome measures — **time-to-availability (lead time)**
  plus **throughput (solo-hours delivered per window)**. Sealed questions
  re-posed in calendar terms under the existing displacement ratchet. The
  attention proxy demoted to an optional, coverage-annotated diagnostic.
  Pilot data and lessons recorded in
  [[wiki/work/improve-windows-process-collection/metrics]].
- **v2.1 (2026-08-19, same-day refinement after an external review cycle):**
  The Architect iterated the v2 design through external review and approved
  the **Velocity** pitch
  (`../wintap/developer_docs/design/velocity-pitch-2026-08-19.md`, carried
  into [[wiki/concept/velocity-metric]]) as the final protocol statement.
  What changed on top of v2: the headline metric is *named* **Velocity**
  (dimensionless, unit = solo-FTE equivalents), canonical formula
  `Velocity = solo-hours / (5.714 × days)`; **Feature Velocity** and
  **Portfolio Velocity** are two explicitly distinct views sharing one unit
  (Portfolio Velocity supersedes v2's raw throughput sum, which survives as
  its numerator); **"solo-hours" replaces "counterfactual-hours"** as the
  unit label; reporting is **point values to one decimal with a stated
  uncertainty range**; sealed Q1 becomes a **forced counterfactual in hours**
  plus a realistic calendar availability date; three guardrails are adopted —
  frozen acceptance criteria, availability finality, and comparability
  flagging with the capability-vs-willingness distinction. The cross-feature
  rollup page [[wiki/metrics]] is created. Two v2 claims were withdrawn or
  corrected: the "hours are never compared against elapsed time" safety
  argument (the canonical formula compares them deliberately, via a declared
  unit) and an interim conservatism claim about the 5.714 constant (see
  Alternatives Considered).

## Context

The LLM-assisted feature workflow ([[wiki/concept/llm-assisted-feature-workflow]])
now runs real features end to end (pidstat collector, process-table retention,
Windows process collection), but the ecosystem has no structured record of what
the AI workflow actually buys. Anecdotes compound poorly; even crude numbers
compound well.

This decision adds a per-feature measurement overlay — a "mini-lab" — to the
existing workflow. It is explicitly **calibration data and directional
evidence, not rigorous science**: single developer, self-reported solo
estimates, small N. The design accepts large error bars on purpose and
optimizes for zero friction instead of precision.

**Why v2 changed the headline (pilot lessons).** The Architect's full
methodology spans two AI harnesses: Claude Code is the "Architecture & Design"
harness (specification); OpenCode running gpt-5.6-sol is the "Engineering &
Development" harness (implementation and test). The v1 attention proxy mined
only Claude Code transcripts, so it structurally measured at most one channel
of human attention. Beyond that structural gap, the three-year trajectory is
toward parallel and delegated agentic development — models improving, human
agentic skill improving, features increasingly concurrent — which would keep
invalidating any mechanism-level metric. The headline metrics are therefore
**boundary/outcome measures**, immune to changes in tools, techniques, and
methodology: they observe only when a feature opens and when it becomes
available, plus how much solo-equivalent work ships per unit of calendar time.

**Why v2.1 (external review).** v2's lead-time/throughput pair was two numbers
in two units with no shared baseline. The review cycle produced a single
dimensionless expression of both — Velocity in solo-FTE equivalents — plus the
guardrails that protect its two timestamps and its numerator. The approved
pitch ([[wiki/concept/velocity-metric]]) is the authoritative public statement
of the metric; this ADR remains the protocol and honest-limitations record.

## Decision

Every feature run through the LLM-assisted feature workflow carries an
optional metrics overlay with the following protocol. Artifacts:
`wiki/work/<feature-slug>/metrics.md` per feature (skeleton and field
definitions in [[wiki/concept/metrics-template]]), a
`## Sealed — human estimates` section in the feature's `interview.md`, and one
row per closed feature in the cross-feature rollup [[wiki/metrics]].

### Headline metric: Velocity

The headline number is **Velocity** — dimensionless, unit = **solo-FTE
equivalents** (the delivery pace of one continuously allocated, unassisted
developer). Canonical formula:

```
Velocity = solo-hours / (5.714 × days)
```

- **solo-hours** — the sealed forced-counterfactual estimate (see sealed
  questions below). This is the standing unit label; the word
  "counterfactual" survives only in honest-limitations prose.
- **days** — raw calendar days, weekends and away-time **included**. For one
  feature: lead time from feature open to first availability.
- **5.714** — the **standardized one-FTE capacity baseline**: 40 working
  hours per week ÷ 7 calendar days. This is a **declared unit definition** —
  like the watt — NOT a realism claim about anyone's actual availability and
  NOT claimed to be directionally conservative (an earlier conservatism claim
  was reviewed and withdrawn — see Alternatives Considered). It defines what
  Velocity 1.0 means; it is fixed once and never recomputed, so the series
  stays comparable for years.

Velocity 1.0 is one-FTE parity.

### Two views, one unit

The same formula at two scopes answers two different questions — related, but
**not the same metric and not derivable from one another**:

- **Feature Velocity** = feature solo-hours / (5.714 × lead-time-days). A
  *speedup*: how many times faster this feature arrived than one FTE would
  have delivered it.
- **Portfolio Velocity** = (sum of solo-hours of all features closed in a
  window) / (5.714 × window-days). *Normalized delivered throughput*: how
  many continuously allocated solo developers the whole system delivered
  like, over that window. This supersedes v2's raw "throughput" companion
  (solo-hour sum per window); the weighted sum survives as the numerator.

Portfolio Velocity is **not an average** of Feature Velocities: two
concurrent features each at Feature Velocity 3.5 yield Portfolio Velocity 7
over their shared window. That gap between the portfolio line and the
per-feature points is the **parallelism dividend**, expected to grow as
delegation and multi-agent maturity pay off — watching it open up is exactly
what the chart is for. Both views share one chart: per-feature points at
close dates, a rolling portfolio line, and a reference line at 1.0.

Portfolio-view limits, stated up front:

- **WIP is invisible until close** — the line sags during long features and
  jumps at delivery; it measures *delivered* throughput only.
- **Window edges matter** — the trailing window must be ≥ 4× the median lead
  time, and the line is read as a smoothed trend, never a per-window score.
- **Small N scatters** — until several features have closed, only the
  per-feature points are meaningful.

Solo-hour weighting also keeps **scope inflation** from hiding in raw feature
counts: the WPC close-out answer — the UserSid reverse-engineering and PEB
command-line work would not have been attempted solo at all — is the standing
evidence that feature scope grows with capability. The lead-time/throughput
pairing remains the standard queueing characterization (Little's Law; cf.
DORA's lead time + deployment frequency).

### Time boundaries (unchanged from v2)

- **Open boundary:** the `opened` date — the interview / design kickoff.
  Queue or backlog wait before that is deliberately invisible to this metric.
- **Availability boundary:** the **first Architect-accepted validation event
  that satisfies the feature brief's acceptance criteria as frozen at feature
  open**, evidenced by a dated artifact (a `verification.md` entry or an
  audit). Observable artifacts on both ends — no recollection.
- **Weekends, vacations, and away-time are deliberately INCLUDED.** Normative
  rationale, in the Architect's own words: under the current Architect-gated
  workflow, weekend time is "simply IDLE and UNUTILIZED"; as agentic, parallel
  and delegated development matures, "this idle time turns into productivity
  time and our velocity goes up — exactly what the mini-lab should capture."
  Progress-while-away is part of what is being measured. A business-day
  variant was considered and rejected (see Alternatives Considered) because it
  would define that improvement out of existence and reintroduce work-calendar
  bookkeeping friction.

### Guardrails (v2.1)

A metric is only as good as its two timestamps and its denominator. Three
protocol rules protect them:

1. **Frozen acceptance criteria.** Acceptance criteria are written into the
   brief at feature open. The availability anchor must be a dated artifact
   demonstrating *those* criteria; any mid-feature criteria change is a
   logged amendment, visible in the record (`criteria_amendments` in
   `metrics.md`). This prevents both premature "availability" and quiet scope
   drift.
2. **Availability finality (acceptance is the quality gate).** A feature is
   available when it demonstrably meets its frozen acceptance criteria, tests
   passing, at the validation milestone. Post-acceptance defects are normal
   software maintenance: tracked and fixed as their own work, **never
   retroactive to a recorded Velocity**. The incentive stays honest without
   retroaction: systematically shipping fast-but-fragile work generates
   rework, and rework consumes future calendar time in which fewer new
   solo-hours close — depressing future Portfolio Velocity. The ledger
   self-corrects forward; nothing is rewritten backward. (A defect-reopen
   rule was considered and rejected — see Alternatives Considered.)
3. **Comparability flagging.** At close, Q3 ("Would you have attempted this
   feature at all without AI?") flags features where parts of the scope
   exceed what the developer is **capable** of building solo (not merely
   unwilling). For those, the forced counterfactual is undefined for that
   slice: the feature is flagged, plotted as an annotated point, and
   **excluded from the fitted trend**. **Willingness-only answers (like
   WPC's) do NOT exclude the feature.** Scope that AI makes newly
   *attemptable* is tracked as its own finding — a benefit this ratio cannot
   express.

### Sealed dual estimates at feature open (v2.1 phrasing)

- The human answers exactly **two** onboarding-interview questions, recorded
  in a marked `## Sealed — human estimates` section of the interview record:
  1. **Forced counterfactual:** "If you had to build this exact scope alone,
     without AI, how many working hours would it take?" — plus a realistic
     calendar availability date. The hours are the feature's **solo-hours**
     (Velocity numerator and portfolio weight); the calendar date absorbs
     weekends and distractions and keeps the date-calibration game from v2.
  2. **Predicted availability date with the AI workflow** — the same
     calibration game, AI-side. (This displaced v1's "predicted attention
     hours" under the ratchet.)
- The Engineer, at exploration start, writes its own independent estimate of
  the same quantities (solo-hours, solo availability date, AI-workflow
  availability date) to the feature's `metrics.md` **before** reading the
  sealed section — plus a one-line basis. **Independence is the point: an
  anchored estimate is worthless.** This sealed-before-reading rule is a
  standing rule in the Engineer agent definition
  (`../wintap/.claude/agents/engineer.md`).
- Every feature therefore carries **two independently sealed solo-hours
  estimates**; their spread is the per-feature uncertainty signal, and their
  long-run agreement with actuals is a running calibration check on both
  estimators.
- If the estimating agent has already seen the human's answers (e.g. the same
  session ran the interview), the seal is broken; it records no estimate.
  Missing data is fine (see never-gates).
- Reveal and comparison happen only at close-out.

### Reporting convention: point values with stated uncertainty

Feature Velocity is reported as a **point value to one decimal, annotated
with its uncertainty range** — the band implied by the two independently
sealed estimates, widened to a default **±2×** until calibration data narrows
it (e.g., *Velocity 3.5, uncertainty 2–7*). The uncertainty travels with the
number wherever it is quoted. **The product is the trend across features, not
any single point.** (A "bands, never decimals" convention was considered and
rejected — see Alternatives Considered.)

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

1. Forced-counterfactual solo estimate — hours, plus a realistic calendar
   availability date (feature open, sealed).
2. Predicted AI-workflow availability date (feature open, sealed).
3. "Would you have attempted this feature at all without AI?" (close-out).
   Unchanged since v1 — it does triple duty as the **scope-inflation signal**
   and the **comparability flag** (capability vs. willingness).

No mid-flow questions, logging duties, or reminders for the human, ever.
**Ratchet rule:** any future proposed metrics question must displace an
existing one — the budget never grows to four. (This cap applies to metrics
questions only; the design interview's normal adaptive questioning is
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

**Why keep it at all:** Velocity is an outcome metric — when it moves, you
cannot tell why. Attention is the mechanism probe that can later distinguish
"models got faster" from "the human learned to stay out of the way."

### Cost: companion field, never folded in

Compute/API cost is deliberately **not** folded into Velocity — one number
cannot be both a speed and an efficiency metric. Cost is recorded per feature
as a companion field (`actual_api_cost_usd`), and cost-adjusted views are
derived from the two numbers, not baked into one.

### Never-gates rule

Metrics never block, delay, or nag the workflow. Skipped questions or missing
files = missing data, shrug, feature proceeds normally. No agent re-asks. A
feature with an empty or absent `metrics.md` is a normal feature.

### Close-out reveal

At feature close-out the Engineer:

1. Records the **availability anchor**: the dated artifact demonstrating the
   brief's frozen acceptance criteria, with a one-line note on why it was
   chosen; computes the calendar lead time.
2. Unseals the interview's human estimates and copies them into `metrics.md`.
3. Computes **Feature Velocity** by the canonical formula, reported to one
   decimal with the uncertainty band from the two sealed estimates (default
   ±2× until calibration narrows it).
4. Records the close-out question's answer with the
   **capability-vs-willingness distinction** and sets the comparability flag.
5. Fills per-unit actuals from audits where derivable; tabulates estimates
   vs. actuals (human vs. AI vs. measured availability dates).
6. Records the attention diagnostic **only if** the main session supplied it,
   with its coverage annotation; records API cost where available.
7. **Appends the feature's row to [[wiki/metrics]]** (the cross-feature
   rollup) and folds a short summary into the wiki as part of the normal
   results fold-in.

### Ownership note

`../wintap/.claude/agents/engineer.md` and `../wintap/CLAUDE.md` sit outside
the standard directory-ownership table in the Wintap methodology. Edits to
them for this protocol (and any future revision) are **drafted by the Engineer
but land only via Architect review** — they are never self-approved plumbing
changes.

## Rationale

- **One dimensionless number with a baseline.** Hours, story points, and
  activity counts all break in an agentic world (see
  [[wiki/concept/velocity-metric]] §The problem). Velocity answers "faster
  than *what*?" by construction: solo-FTE parity is 1.0.
- **The constant is a unit, not a model.** Declaring 5.714 once — with no
  realism or bias claim attached — keeps the series comparable for years and
  removes both the temptation and the ability to tune the baseline.
- **Boundary/outcome metrics survive methodology change.** Velocity observes
  only the feature's endpoints, so it remains comparable across harness
  changes, model upgrades, delegation-depth changes, and the shift to
  parallel feature work. A mechanism metric (attention) would be invalidated
  by each of them.
- **Calendar inclusion is the point, not a bug.** Idle weekends under the
  current Architect-gated workflow are real elapsed time in which nothing
  ships; when delegated agents convert that idle time into progress, Velocity
  rises. Excluding weekends would hide the very effect the lab exists to
  capture.
- **Two views expose the parallelism dividend.** Feature Velocity cannot see
  concurrency; Portfolio Velocity is built from the same unit precisely so
  the gap between them becomes the delegation-maturity signal.
- **Availability finality keeps incentives honest without retroaction.**
  Fast-but-fragile work punishes itself forward (rework consumes future
  calendar time, depressing future Portfolio Velocity), so no recorded value
  ever needs rewriting — which also keeps the ledger append-only and
  chartable.
- Sealed, independent dual estimates remain the cheapest calibration data on
  both the human's and the AI's forecasting skill; anchoring destroys that
  signal, hence the seal. Two independent solo-hours estimates additionally
  give every point its uncertainty band.
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

- **The solo estimate is a counterfactual and unverifiable.** The numerator
  cannot be checked against reality; every reported Velocity carries its
  uncertainty range, and only the trend across features is load-bearing.
- **N=1 developer**, self-reported estimates, small feature count — this is
  directional evidence and self-calibration data, not rigorous science.
- **Velocity is not gameable-proof.** Padding solo estimates inflates it
  silently; the defenses are sealing, the independent second estimate, the
  running predicted-vs-actual calibration check, and the fact that the
  developer is the primary consumer of the number.
- **Not a people-comparison tool.** It measures a workflow against the same
  developer's own counterfactual; across people it compares estimating
  conventions, not ability.
- **Calendar noise dominates short features:** a 3-day weekend is a 50–100%
  relative distortion on a ~6-day feature. Accepted as a consistent bias that
  shrinks with feature size and with N.
- **Portfolio Velocity is blind to WIP and sensitive to window edges** (see
  the stated limits above); it is read only as a smoothed trend once N and
  window length permit.
- The attention diagnostic, when computed, undercounts (single-message blocks,
  off-session reading, thinking away from keyboard) and may cover only one
  harness — hence the mandatory coverage annotation.
- Estimates may drift toward "safe" values once the estimators have seen prior
  features' reveals; cross-feature learning is a feature for calibration but a
  confound for ROI claims.
- API cost capture is best-effort; when unavailable it is simply missing data.

## Consequences

- The approved pitch is carried into the wiki as the metric's public
  statement: [[wiki/concept/velocity-metric]].
- The metrics file format ([[wiki/concept/metrics-template]]) moves to the
  v2.1 field set: solo-hours terminology, `feature_velocity` +
  `velocity_uncertainty`, `criteria_amendments`, a comparability flag, and a
  leading human-readable headline block; methodology prose becomes links to
  this ADR rather than per-feature restatement.
- The interview's sealed questions take the forced-counterfactual Q1 /
  calendar Q2 phrasing ([[wiki/concept/feature-work-template]],
  [[wiki/concept/llm-assisted-feature-workflow]]).
- A cross-feature rollup page [[wiki/metrics]] holds one row per closed
  feature (lead time, solo estimate, Feature Velocity ± uncertainty,
  comparability flag) and will carry Portfolio Velocity once N ≥ several with
  a trailing window ≥ 4× median lead time.
- The Wintap Engineer agent definition's standing rules and close-out duties
  update to the Velocity protocol (sealed solo-hours + dates; availability
  anchor with one-line why; canonical-formula computation with uncertainty
  band; rollup row; capability-vs-willingness Q3). `../wintap/CLAUDE.md`'s
  mini-lab paragraph changes accordingly (attention proxy: optional
  diagnostic, main-session-supplied when cheap). Both land only via Architect
  review per the ownership note.
- Pre-v2.1 metrics files are not rewritten; the WPC pilot gains a marked
  Velocity addendum (Feature Velocity 3.5, uncertainty 2–7, retrofit and
  willingness-only-comparability caveats)
  ([[wiki/work/improve-windows-process-collection/metrics]]) and seeds the
  rollup as an annotated, illustrative-not-evidentiary point.

## Alternatives Considered

- **Business-day lead time (exclude weekends/vacations):** rejected — it would
  define the anticipated progress-while-away improvement out of existence and
  reintroduce work-calendar bookkeeping friction.
- **Per-developer capacity baselines (replace 5.714 with each developer's
  actual availability):** rejected (v2.1) — extra degrees of freedom and a
  gaming surface; the constant is a declared unit, not a model of anyone's
  calendar, and personalizing it would break series comparability and turn
  the baseline into a negotiation.
- **Directional-bias framing of the constant (claiming 5.714 is
  "conservative"):** withdrawn after external review (v2.1) — the constant
  makes no realism claim in either direction; it is a unit definition, and
  attaching a bias claim invited exactly the argument the declared-unit
  framing avoids.
- **"Bands, never decimals" reporting (report only an uncertainty band, never
  a point value):** rejected (v2.1) — cognitive friction; a point value to
  one decimal with the uncertainty range attached is adopted instead, with
  the band traveling wherever the number is quoted.
- **Defect reopen rule (post-acceptance defects reopen or retroactively adjust
  a recorded Velocity):** rejected (v2.1) — availability finality adopted
  instead. Retroaction would make the ledger unstable and re-litigate every
  point; the forward self-correction argument (rework consumes future
  calendar time, depressing future Portfolio Velocity) keeps the incentive
  honest without it.
- **Full attention pivot / cross-harness adapters now (mine OpenCode
  transcripts too):** deferred — no feature yet routes significant attention
  through the second harness; building adapters ahead of need is friction
  without signal.
- **Abandoning attention measurement entirely:** rejected — kept as the
  optional mechanism diagnostic, because outcome metrics cannot explain their
  own movement.
- **Folding cost into the headline number:** rejected — one number cannot be
  both a speed and an efficiency metric; cost stays a companion field.
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
core flow. v2 and v2.1 revise this decision in place (see Revision History);
there is no separate superseded document. The approved pitch
([[wiki/concept/velocity-metric]], authoritative source
`../wintap/developer_docs/design/velocity-pitch-2026-08-19.md`) is the
metric's public statement; where the two disagree, the pitch wins.
