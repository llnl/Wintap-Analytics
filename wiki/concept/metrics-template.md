---
title: "Feature Metrics Template (Velocity/ROI Mini-Lab)"
type: concept
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/decision/ai-velocity-roi-mini-lab.md
  - ../Wintap-Analytics/wiki/concept/velocity-metric.md
policy: agent-editable
last_validated: 2026-08-19
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: llm-agent
status: draft
source_paths: wiki/concept/metrics-template.md
tags: [workflow, metrics, llm, template, feature-work, velocity, roi, lead-time, solo-hours]
---

# Feature Metrics Template (Velocity/ROI Mini-Lab)

Defines `wiki/work/<feature-slug>/metrics.md`, the per-feature metrics file
for the velocity/ROI mini-lab decided in
[[wiki/decision/ai-velocity-roi-mini-lab]]. The metric itself is defined in
[[wiki/concept/velocity-metric]]. Read those pages for the protocol and
rationale; this page defines only the file format. Methodology is never
restated per feature — a rendered `metrics.md` links here and to the ADR.

**This is the v2.1 field set (2026-08-19, Velocity protocol).** Headline:
**Feature Velocity** = `solo_hours / (5.714 × lead_time_days)`, one decimal,
with a stated uncertainty range. "Solo-hours" is the standing unit label
(formerly "counterfactual-hours"). Attention remains a demoted,
coverage-annotated diagnostic. Pre-v2.1 files (the WPC pilot) keep their
earlier blocks and carry marked addenda; aggregation scripts prefer the
newest block where several exist.

## Lifecycle

1. **Exploration start (Engineer):** create `metrics.md` from the skeleton
   below and fill the `ai_est_*` fields plus `ai_est_basis` — **before**
   reading the interview's `## Sealed — human estimates` section. If the seal
   is already broken (this session saw the human's answers), leave the
   `ai_est_*` fields null.
2. **Instruction drafting (Engineer):** add one entry to `units:` per
   instruction unit with `est_hours` and `basis`, before that unit's
   implementation begins.
3. **Close-out (Engineer):** record `ts_available` and `availability_anchor`
   (dated artifact demonstrating the brief's frozen acceptance criteria, plus
   a one-line why); compute `lead_time_days`; copy the human estimates
   (unsealed) from `interview.md`; set `solo_hours` from the human sealed
   forced-counterfactual; compute `feature_velocity` (canonical formula, one
   decimal) and `velocity_uncertainty` (band implied by the two sealed
   solo-hours estimates, widened to the default ±2× until calibration
   narrows it); set `comparability` from the close-out question's answer
   (capability vs. willingness — see Field Definitions); fill per-unit
   `actual_hours` from audits where derivable; record the attention
   diagnostic **only if** the main session supplied one (with its coverage
   annotation); write the Headline block and the prose tabulation; **append
   the feature's row to [[wiki/metrics]]**.

Missing data at any stage is fine — never gate, never nag, never re-ask
(see the ADR's never-gates rule).

## Field Definitions (headline metrics)

- `ts_open` — the feature's `opened` date: interview / design kickoff.
  Queue/backlog wait before this is deliberately invisible.
- `ts_available` — date of the **first Architect-accepted validation event
  satisfying the feature brief's acceptance criteria as frozen at open**,
  evidenced by a dated artifact (verification.md entry or audit).
  Availability is final: post-acceptance defects never move it (ADR
  guardrail 2).
- `availability_anchor` — pointer to that dated artifact plus a one-line note
  on why it was chosen as the acceptance evidence.
- `criteria_amendments` — logged mid-feature acceptance-criteria changes, if
  any (ADR guardrail 1); empty list when none.
- `lead_time_days` — raw calendar days from `ts_open` to `ts_available`,
  **weekends and away-time included** (see the ADR for the normative
  rationale).
- `solo_hours` — the human sealed forced-counterfactual estimate, in hours.
  The Velocity numerator and the feature's portfolio weight.
- `feature_velocity` — `solo_hours / (5.714 × lead_time_days)`, reported to
  **one decimal**. 5.714 is the declared one-FTE capacity baseline (40 h/week
  ÷ 7 days); never recomputed.
- `velocity_uncertainty` — the uncertainty range that travels with
  `feature_velocity`: the band implied by the two independently sealed
  solo-hours estimates (human + Engineer), widened to a default ±2× until
  calibration data narrows it. E.g. `"2-7"` for a 3.5 point value.
- `comparability` — `none` | `willingness-only` | `capability-exceeded`,
  derived from the close-out question. `capability-exceeded` (scope beyond
  what the developer could have built solo) flags the feature out of the
  fitted trend as an annotated point; `willingness-only` (would not have
  attempted, but could have) does **not** exclude it.

## Parseability Contract

All metric values live in the single fenced ```yaml block in the body, with
the stable field names below — one value per field, no values buried in prose
— so a future devtools aggregation script can consume every feature's
`metrics.md` without scraping text. Do not rename fields; add new ones only
via a revision to this template and the ADR (this v2.1 revision is itself
such a change: `throughput_weight_hours` → `solo_hours`, plus the new
`feature_velocity`, `velocity_uncertainty`, `criteria_amendments`,
`comparability`, and `ai_est_solo_hours` fields). Unknown values are `null`,
never omitted, never prose like "TBD". Hours are decimal numbers; dates are
ISO 8601. Exception for pre-v2.1 files only: a retrofitted feature carries
its original blocks plus marked addendum blocks; the newest block is
authoritative for aggregation.

## Skeleton

Standard work-artifact frontmatter first (see
[[wiki/concept/feature-work-template]]), then:

```markdown
# Feature Metrics: <Feature Name>

Velocity/ROI mini-lab data per [[wiki/decision/ai-velocity-roi-mini-lab]]
(v2.1); metric definition in [[wiki/concept/velocity-metric]].
SEAL NOTE: `interview.md` `## Sealed — human estimates` must not be read by
the estimating agent until close-out.

## Headline

<Filled at close-out — the short human-readable block; every number repeats
in the YAML below.>

- **Feature Velocity:** <n.n> (uncertainty <lo>–<hi>)
- **Lead time:** <n> calendar days (<ts_open> → <ts_available>)
- **Solo estimate:** <n> solo-hours (sealed at open)
- **Close-out answer:** <Q3 answer in one line, with the
  capability-vs-willingness reading>

## Metrics Data

​```yaml
feature_slug: <feature-slug>
feature_abbrev: null            # e.g. wpc; null if none declared
status: open                    # open | closed
opened: YYYY-MM-DD
closed: null                    # YYYY-MM-DD at close-out

# --- Headline: Feature Velocity (computed at close-out) ---
ts_open: YYYY-MM-DD              # = opened; interview / design kickoff
ts_available: null               # first Architect-accepted validation event vs. frozen criteria
availability_anchor: ""          # dated artifact pointer + one-line why chosen
criteria_amendments: []          # logged mid-feature acceptance-criteria changes
lead_time_days: null             # raw calendar days, weekends included
solo_hours: null                 # human sealed forced-counterfactual, hours (numerator; portfolio weight)
feature_velocity: null           # solo_hours / (5.714 × lead_time_days), one decimal
velocity_uncertainty: ""         # range from the two sealed estimates, default ±2x, e.g. "2-7"
comparability: null              # none | willingness-only | capability-exceeded

# --- AI pre-exploration sealed estimates (Engineer; written BEFORE reading
# --- the interview's sealed section; null if the seal was already broken) ---
ai_est_solo_hours: null          # independent forced-counterfactual, hours
ai_est_solo_available_date: null # est. date feature available if built solo, no AI
ai_est_ai_available_date: null   # est. date feature available with the AI workflow
ai_est_basis: ""                 # one line, e.g. "~4 units, one novel subsystem"

# --- Per-unit development estimates (Engineer, at instruction drafting;
# --- actual_hours filled at close-out from the unit's audit) ---
units:
  - id: <abbrev-01>
    est_hours: null
    basis: ""
    actual_hours: null

# --- Human sealed estimates (copied from interview.md at close-out ONLY) ---
human_est_solo_hours: null           # forced-counterfactual solo estimate, hours (Q1)
human_est_solo_available_date: null  # realistic solo availability date (Q1 companion)
human_est_ai_available_date: null    # predicted availability with the AI workflow (Q2)

# --- Diagnostics (optional, never headline; filled at close-out) ---
attention_hours: null            # 15-min-gap proxy, ONLY if main session supplied it
attention_coverage: ""           # mandatory when attention_hours set, e.g. "claude-code sessions only"
actual_api_cost_usd: null        # companion field; never folded into Velocity
closeout_attempted_without_ai: null  # verbatim answer to the close-out question

findings: ""  # one free-text line
​```

## Close-Out Tabulation

<Filled at close-out: small estimates-vs-actuals table (human vs. AI vs.
measured availability dates and solo-hours), and 2-3 sentences of
interpretation. Prose goes here; every number must also exist in the YAML
block above. Then append the feature's row to [[wiki/metrics]].>
```

(The zero-width characters guarding the inner fence are formatting armor for
this template page only; a real `metrics.md` uses a plain ```yaml fence.)

## Related

- [[wiki/concept/velocity-metric]] — the approved metric definition
- [[wiki/decision/ai-velocity-roi-mini-lab]] — the protocol this file serves
- [[wiki/metrics]] — the cross-feature rollup this file feeds
- [[wiki/concept/feature-work-template]] — the other work-folder skeletons
- [[wiki/concept/llm-assisted-feature-workflow]] — the workflow this overlays
