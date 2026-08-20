---
title: "Velocity: One Number for AI-Assisted Development"
type: concept
confidence: high
grounded_by:
  - ../wintap/developer_docs/design/velocity-pitch-2026-08-19.md
policy: human-review-required
last_validated: 2026-08-20
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: reviewed
source_paths: ../wintap/developer_docs/design/velocity-pitch-2026-08-19.md
tags: [concept, metrics, velocity, llm, workflow, lead-time, throughput, solo-hours]
---

# Velocity: One Number for AI-Assisted Development

**2026-08-19 — Approved**
**Author: David Frye (drafted with AI assistance)**

> Wiki carry-over note: the metric definition and protocol below come from the
> Architect-approved pitch at
> `../wintap/developer_docs/design/velocity-pitch-2026-08-19.md`. On 2026-08-20,
> the Architect simplified the wiki's reader-facing presentation without
> changing the formula or evidence. Protocol mechanics live in
> [[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1).

## Wiki presentation convention

The approved formula and technical fields below remain unchanged. Feature
metrics documents present them in plain language under **Results**:

- **Estimated delivery speed:** `<n.n>× one solo developer's pace`
- **Plausible range:** `about <lo>×–<hi>× faster`
- **Estimate confidence:** `High`, `Medium`, or `Low`
- **Why confidence is <label>:** one direct sentence

The structured field remains `velocity_uncertainty`; the reader-facing phrase
“plausible range” replaces shorthand such as “uncertainty 2–7.” Technical
details and the canonical YAML record belong under **Technical Record**. See
[[wiki/concept/metrics-template]].

---

## The problem

We are three years into a transition where AI agents do an increasing share of
software development work. Everyone has anecdotes about how much faster this
is. Anecdotes don't compound, don't chart, and don't survive a skeptical
audience. We need a number.

The obvious candidates all break in an agentic world:

- **Hours spent** stops meaning anything when most of the work happens while
  the human is away. Measuring the human's attention undercounts the work;
  measuring the agents' wall-clock overcounts it.
- **Story points per sprint** measure throughput but have no baseline — they
  can't answer "faster than *what*?"
- **Lines of code, commits, PRs** measure activity, not delivery, and agents
  produce arbitrary amounts of all three.

What we actually want to know is simple: **how fast do features arrive,
measured against what one unassisted developer could deliver?**

## The proposal

Velocity expresses delivery in a single unit: **solo-FTE equivalents** — the
delivery pace of one continuously allocated, unassisted developer. It is
computed from three inputs:

```
Velocity = solo-hours / (5.714 × days)
```

| Input | Definition |
|---|---|
| **solo-hours** | A forced-counterfactual estimate, sealed at feature start: *"If you had to build this exact scope alone, without AI, how many working hours would it take?"* Two such estimates are captured independently (see "Uncertainty"). |
| **days** | Raw calendar days. For a single feature: lead time from feature start (design kickoff) to first availability — the first accepted validation artifact demonstrating acceptance criteria frozen at start (see "Guardrails"). Weekends and time away are **included**, deliberately (see below). |
| **5.714** | The standardized one-FTE capacity baseline: 40 working hours per week ÷ 7 calendar days. A declared unit — like the watt — fixed once so the series stays comparable for years. It makes no claim about any individual's actual availability; it defines what "1.0" means. |

Velocity 1.0 is one-FTE parity. A feature at Velocity 3.5 arrived three and a
half times faster than one unassisted developer could have delivered it.

### Two views, one unit

The same formula, applied at two scopes, answers two different questions —
related, but **not** the same metric, and not derivable from one another:

- **Feature Velocity** — the formula over one feature's solo-hours and lead
  time. It is a *speedup*: how many times faster this feature arrived than
  one FTE would have delivered it.
- **Portfolio Velocity** — the formula over the sum of solo-hours of all
  features closed in a time window, divided by the window's days. It is
  *normalized delivered throughput*: how many continuously allocated solo
  developers the whole system delivered like, over that window.

Portfolio Velocity is not an average of Feature Velocities. Two concurrent
features each at Feature Velocity 3.5 yield a Portfolio Velocity of 7 over
their shared window — concurrency raises portfolio output without changing
any single feature's speedup. That divergence is informative, not anomalous:
**the gap between the portfolio line and the per-feature points is the
parallelism dividend**, and watching it open up is precisely how the chart
will show delegation and multi-agent maturity paying off.

Both views share the solo-FTE unit and one chart: per-feature points at their
close dates, a rolling portfolio line, and a reference line at 1.0.

The portfolio view has known statistical limits, stated up front:

- **Work in progress is invisible until close.** The line sags during long
  features and jumps at delivery. It measures *delivered* throughput only.
- **Window edges matter.** A large feature closing just inside or outside a
  window swings short-window values; windows must be long relative to the
  median lead time (trailing window ≥ 4× median lead time), and the line is
  read as a smoothed trend, never as a per-window score.
- **Small N scatters.** Until several features have closed, only the
  per-feature points are meaningful.

### Why calendar time, not work time

This was the most contested design choice, and the resolution is the heart of
the metric: **whether progress happens while you're away is part of what we
are measuring.** Under today's workflow, a weekend is idle time — the agents
wait for human direction. As agentic, parallel, and delegated development
matures, that idle time converts into productive time, and Velocity rises.
A work-time metric would define this improvement out of existence.

### Uncertainty: two sealed estimates and stated error bars

The numerator is a counterfactual and cannot be verified. The protocol
compensates three ways:

1. **Sealing.** Estimates are recorded before development starts and never
   revised, eliminating hindsight bias.
2. **A second, independent estimator.** The AI design agent writes its own
   solo-hours estimate *before* being shown the human's. Every feature
   therefore carries two independently sealed estimates; their spread is a
   per-feature uncertainty signal, and their long-run agreement with actuals
   is a running calibration check on both estimators.
3. **Point values with an honest plausible range.** Feature Velocity is
   calculated to one decimal. Its range comes from the two sealed estimates
   and is widened to a default ±2× until calibration data narrows it. A 3.5
   result is presented as *estimated delivery speed 3.5× one solo developer's
   pace; plausible range about 2×–7× faster*. **The product is the trend
   across features, not any single point.**

## Guardrails

A metric is only as good as its two timestamps and its denominator. Three
protocol rules protect them:

- **Frozen acceptance criteria.** The feature's acceptance criteria are
  written into the brief at feature start. The availability anchor must be a
  dated artifact demonstrating *those* criteria; any mid-feature criteria
  change is a logged amendment, visible in the record. This prevents both
  premature "availability" and quiet scope drift.
- **Acceptance is the quality gate — and availability is final.** A feature
  is available when it demonstrably meets its frozen acceptance criteria,
  tests passing, at the validation milestone. Defects discovered afterward
  are normal software maintenance: they are tracked and fixed as their own
  work, and they never retroactively alter a recorded Velocity. Demanding
  perpetually bug-free code as the bar for "done" would be a standard no
  software organization meets. The incentive stays honest without
  retroaction: systematically shipping fast-but-fragile work generates
  rework, and rework consumes future calendar time in which fewer new
  solo-hours close — depressing future Portfolio Velocity. The ledger
  self-corrects going forward; nothing needs to be rewritten backward.
- **Comparability flagging.** At close the developer answers: *"Would you
  have attempted this feature at all without AI?"* Where parts of the scope
  exceed what the developer is *capable* of building solo (not merely
  unwilling), the forced-counterfactual estimate is undefined for that slice;
  such features are flagged, plotted as annotated points, and excluded from
  the fitted trend. Scope that AI makes newly *attemptable* is tracked as its
  own finding — it is a benefit, but not one this ratio can express.

Compute/API cost is deliberately **not** folded into Velocity — one number
cannot be both a speed and an efficiency metric. Cost is recorded per feature
as a companion field, and cost-adjusted views are derived from the two
numbers, not baked into one.

## A pilot illustration (not evidence)

The protocol was retrofitted onto its first feature mid-flight, so this
datapoint carries an explicit asterisk: the solo estimate was recorded before
close but **not under the sealing discipline**, and the independent AI
estimate was anchored. It is shown to make the computation concrete, not to
support the number.

The feature: a Windows process-telemetry collection overhaul (nine
implementation units including kernel ETW work, boot-trace coverage, and a
bug sweep).

| | |
|---|---|
| Solo estimate (retrofit, unsealed) | 3 working weeks ≈ 120 solo-hours |
| Feature opened | Thu 2026-08-13 |
| First available (validation artifact) | 2026-08-19 |
| Lead time | 6 calendar days (including a 3-day weekend with zero activity) |
| **Estimated delivery speed** | **3.5× one solo developer's pace** |
| **Plausible range** | **About 2×–7× faster** |
| **Estimate confidence** | **Low** — retrospective, unsealed, and anchored |

Note the weekend: under today's human-gated workflow those three days were
idle, and they count against Velocity anyway. That is the metric working as
designed — the idle-to-utilized conversion is exactly the improvement the
series should reveal over time.

## What Velocity is not

- **It is not a people-comparison tool.** It measures a *workflow* against
  the same developer's own counterfactual. Comparing Velocity across people
  compares their estimating conventions, not their ability.
- **It is not precise.** The numerator is an unverifiable counterfactual.
  Every result carries a plain-language plausible range and confidence reason;
  only the trend is load-bearing.
- **It is not gameable-proof.** Padding solo estimates inflates Velocity
  silently. The defenses are sealing, the independent second estimate, the
  running calibration check against predicted-vs-actual delivery dates, and
  the fact that the developer is the primary consumer of the number.
- **It is not a quality or cost metric.** Quality is enforced at the
  acceptance gate; post-acceptance defects are maintenance, not retroactive
  penalties. Cost is a companion field. Velocity answers one question only:
  how fast do accepted features arrive.
- **It is not Scrum velocity.** Scrum's velocity is raw throughput (points
  per sprint) with no baseline. The name collision is acknowledged; the
  one-line definition resolves it.

## The measurement protocol (deliberately minimal)

The entire per-feature cost to the human is **three questions**:

1. At feature open (sealed): the forced-counterfactual solo estimate — hours,
   and a realistic calendar availability date.
2. At feature open (sealed): predicted availability date with the AI
   workflow.
3. At feature close: "Would you have attempted this feature at all without
   AI?" — the comparability flag.

The AI-side sealed estimates, the frozen acceptance criteria, and both
timestamps come from artifacts the workflow produces anyway (a dated
design-kickoff record; a dated validation record). No time tracking, no
logging duties, no new tooling. Metrics never gate or delay the work; a
feature with missing metrics is a normal feature.

---

Full protocol, definitions, and honest-limitations record:
[[wiki/decision/ai-velocity-roi-mini-lab]]. Per-feature file format:
[[wiki/concept/metrics-template]]. Cross-feature rollup: [[wiki/metrics]].
