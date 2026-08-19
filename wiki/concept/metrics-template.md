---
title: "Feature Metrics Template (Velocity/ROI Mini-Lab)"
type: concept
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/decision/ai-velocity-roi-mini-lab.md
policy: agent-editable
last_validated: 2026-08-19
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: llm-agent
status: draft
source_paths: wiki/concept/metrics-template.md
tags: [workflow, metrics, llm, template, feature-work, velocity, roi, lead-time, throughput]
---

# Feature Metrics Template (Velocity/ROI Mini-Lab)

Defines `wiki/work/<feature-slug>/metrics.md`, the per-feature metrics file
for the velocity/ROI mini-lab decided in [[wiki/decision/ai-velocity-roi-mini-lab]].
Read that ADR for the protocol; this page defines only the file format.

**This is the v2 field set (2026-08-19, post-pilot revision).** Headline:
time-to-availability (lead time) + throughput weight. Attention is a demoted,
coverage-annotated diagnostic. Pre-v2 files (the WPC pilot) keep their v1
block and carry a marked v2 addendum block; aggregation scripts should prefer
the v2 block where both exist.

## Lifecycle

1. **Exploration start (Engineer):** create `metrics.md` from the skeleton
   below and fill the `ai_est_*` fields plus `ai_est_basis` — **before**
   reading the interview's `## Sealed — human estimates` section. If the seal
   is already broken (this session saw the human's answers), leave the
   `ai_est_*` fields null.
2. **Instruction drafting (Engineer):** add one entry to `units:` per
   instruction unit with `est_hours` and `basis`, before that unit's
   implementation begins.
3. **Close-out (Engineer):** fill the availability date and its anchoring
   artifact (with a one-line why), compute `lead_time_days`, copy the human
   estimates (unsealed) from `interview.md`, set `throughput_weight_hours`
   from the solo estimate's hours reading, fill per-unit `actual_hours` from
   audits where derivable, record the close-out question's answer and a
   one-line findings note, record the attention diagnostic **only if** the
   main session supplied one (with its coverage annotation), then write the
   prose tabulation section.

Missing data at any stage is fine — never gate, never nag, never re-ask
(see the ADR's never-gates rule).

## Field Definitions (headline metrics)

- `ts_open` — the feature's `opened` date: interview / design kickoff.
  Queue/backlog wait before this is deliberately invisible.
- `ts_available` — date of the **first Architect-accepted validation event
  satisfying the feature brief's acceptance criteria**, evidenced by a dated
  artifact (verification.md entry or audit).
- `availability_anchor` — pointer to that dated artifact plus a one-line note
  on why it was chosen as the acceptance evidence.
- `lead_time_days` — raw calendar days from `ts_open` to `ts_available`,
  **weekends and away-time included** (see the ADR for the normative
  rationale).
- `throughput_weight_hours` — the unsealed human solo estimate read in hours;
  summed across features closed in a window to give the throughput metric.
  Hours are never compared against elapsed calendar time.

## Parseability Contract

All metric values live in the single fenced ```yaml block in the body, with
the stable field names below — one value per field, no values buried in prose
— so a future devtools aggregation script can consume every feature's
`metrics.md` without scraping text. Do not rename fields; add new ones only
via a revision to this template and the ADR (this v2 revision is itself such
a change). Unknown values are `null`, never omitted, never prose like "TBD".
Hours are decimal numbers; dates are ISO 8601. Exception for pre-v2 files
only: a retrofitted feature carries its original v1 block plus one marked v2
addendum block; the v2 block is authoritative for aggregation.

## Skeleton

Standard work-artifact frontmatter first (see
[[wiki/concept/feature-work-template]]), then:

```markdown
# Feature Metrics: <Feature Name>

Velocity/ROI mini-lab data per [[wiki/decision/ai-velocity-roi-mini-lab]] (v2).
SEAL NOTE: `interview.md` `## Sealed — human estimates` must not be read by
the estimating agent until close-out.

## Metrics Data

​```yaml
feature_slug: <feature-slug>
feature_abbrev: null            # e.g. wpc; null if none declared
status: open                    # open | closed
opened: YYYY-MM-DD
closed: null                    # YYYY-MM-DD at close-out

# --- Headline: time-to-availability (filled at close-out) ---
ts_open: YYYY-MM-DD              # = opened; interview / design kickoff
ts_available: null               # first Architect-accepted validation event
availability_anchor: ""          # dated artifact pointer + one-line why chosen
lead_time_days: null             # raw calendar days, weekends included

# --- Companion: throughput weight (filled at close-out) ---
throughput_weight_hours: null    # human solo estimate, hours reading

# --- AI pre-exploration sealed estimates (Engineer; written BEFORE reading
# --- the interview's sealed section; null if the seal was already broken) ---
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
human_est_solo_available_date: null  # calendar-posed solo counterfactual
human_est_solo_hours: null           # hours reading of the same estimate (throughput weight)
human_est_ai_available_date: null    # predicted availability with the AI workflow

# --- Diagnostics (optional, never headline; filled at close-out) ---
attention_hours: null            # 15-min-gap proxy, ONLY if main session supplied it
attention_coverage: ""           # mandatory when attention_hours set, e.g. "claude-code sessions only"
actual_api_cost_usd: null        # best-effort; null if unavailable
closeout_attempted_without_ai: null  # answer to "Would you have attempted this feature at all without AI?"

findings: ""  # one free-text line
​```

## Close-Out Tabulation

<Filled at close-out: small estimates-vs-actuals table (human vs. AI vs.
measured availability dates), the lead-time and throughput-weight reading,
and 2-3 sentences of interpretation. Prose goes here; every number must also
exist in the YAML block above.>
```

(The zero-width characters guarding the inner fence are formatting armor for
this template page only; a real `metrics.md` uses a plain ```yaml fence.)

## Related

- [[wiki/decision/ai-velocity-roi-mini-lab]] — the protocol this file serves
- [[wiki/concept/feature-work-template]] — the other work-folder skeletons
- [[wiki/concept/llm-assisted-feature-workflow]] — the workflow this overlays
