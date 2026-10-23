---
title: "Feature Metrics: Improve Lintap Data Quality"
type: concept
confidence: high
grounded_by:
  - wiki/concept/metrics-template.md
  - wiki/work/improve-lintap-data-quality/verification.md
policy: agent-editable
last_validated: 2026-10-22
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: llm-agent
status: stable
source_paths: wiki/work/improve-lintap-data-quality/metrics.md
tags: [feature-work, metrics, lintap, data-quality]
---

# Feature Metrics: Improve Lintap Data Quality

See [[wiki/concept/metrics-template]] and
[[wiki/decision/ai-velocity-roi-mini-lab]].

## Results

- **Estimated delivery speed:** **7.0× one solo developer's pace**
- **Plausible range:** **about 3.5×–14× faster**
- **Estimate confidence:** **Low**
- **Why confidence is Low:** The human estimate was sealed, but no independent
  AI estimate is available because that seal had already been read.
- **Delivered in:** **1 calendar day** (2026-10-21 → 2026-10-22)
- **Estimated solo effort:** **40 hours**

The fresh packaged arm64 run closed the frozen loss, coverage, DBT, attribution,
and hostname gates. The developer answered “Yes” to whether this exact feature
would have been attempted without AI, so no comparability exclusion applies.

## Technical Record

```yaml
feature_slug: improve-lintap-data-quality
feature_abbrev: ldq
status: closed
opened: 2026-10-21
closed: 2026-10-22
ts_open: 2026-10-21
ts_available: 2026-10-22
availability_anchor: "wiki/work/improve-lintap-data-quality/verification.md §ldq-05 — fresh packaged arm64 acceptance; first final-code package demonstration of every frozen gate"
criteria_amendments: []
lead_time_days: 1
solo_hours: 40
feature_velocity: 7.0
velocity_uncertainty: "3.5-14"
comparability: none
ai_est_solo_hours: null
ai_est_solo_available_date: null
ai_est_ai_available_date: null
ai_est_basis: "Seal already read in this session."
units:
  - id: ldq-01
    est_hours: null
    basis: ""
    actual_hours: null
human_est_solo_hours: 40
human_est_solo_available_date: null
human_est_ai_available_date: null
attention_hours: null
attention_coverage: ""
actual_api_cost_usd: null
closeout_attempted_without_ai: "Yes"
findings: "Human sealed estimate was 5 working days solo, interpreted as 40 hours; predicted AI duration was 2 days without an ISO availability date."
```

## Close-Out Tabulation

| Measure | Value |
| --- | --- |
| Human sealed solo estimate | 5 working days / 40 hours |
| AI independent estimate | unavailable; seal already read |
| Predicted AI duration | 2 days; no ISO date supplied |
| Measured availability | 1 calendar day |

Calculation: `40 / (5.714 × 1) = 7.0`, or an estimated **7.0× one solo
developer's pace**. With only one sealed estimator, the default ±2× treatment
gives a plausible range of **about 3.5×–14× faster** and low confidence.
