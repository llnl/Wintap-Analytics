---
title: "Feature Metrics: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
  - wiki/concept/velocity-metric.md
  - wiki/decision/ai-velocity-roi-mini-lab.md
  - wiki/concept/metrics-template.md
  - wiki/work/improve-windows-process-collection/interview.md
  - wiki/work/improve-windows-process-collection/implementation_plan.md
  - ../wintap/developer_docs/audits/wpc-01-sid-helper.md
  - ../wintap/developer_docs/audits/wpc-02-sensor-core.md
  - ../wintap/developer_docs/audits/wpc-03-snapshot-refresh.md
  - ../wintap/developer_docs/audits/wpc-04-field-enrichment.md
  - ../wintap/developer_docs/audits/wpc-05-stop-metrics-merge.md
  - ../wintap/developer_docs/audits/wpc-06-wire-in-removal.md
  - ../wintap/developer_docs/audits/wpc-07-boot-etl-coverage.md
  - ../wintap/developer_docs/audits/wpc-09-bug-sweep.md
policy: agent-editable
last_validated: 2026-08-20
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: reviewed
source_paths: wiki/work/improve-windows-process-collection/metrics.md
tags: [feature-work, metrics, velocity, roi, process-events, windows-sensor]
---

# Feature Metrics: Improve Windows Process Collection

Metric definition: [[wiki/concept/velocity-metric]]. Measurement protocol:
[[wiki/decision/ai-velocity-roi-mini-lab]]. File format:
[[wiki/concept/metrics-template]].

This is the retrospective pilot illustration used by the approved definition,
not evidence for the trend. The feature was already underway when measurement
began: its 120 solo-hour estimate was unsealed, and the reported AI estimate
was anchored to the same source rather than independently sealed. Missing
values remain null rather than being reconstructed.

## Results

- **Estimated delivery speed:** **3.5× one solo developer's pace**
- **Plausible range:** **about 2×–7× faster**
- **Estimate confidence:** **Low**
- **Why confidence is low:** The 120-hour solo estimate was recorded after
  work began, and the AI estimate was not independent.
- **Delivered in:** **6 calendar days** (2026-08-13 → 2026-08-19), including
  an idle three-day weekend
- **Estimated solo effort:** **120 hours**

The feature passed its full acceptance scope when the final overnight smoke-test
confirmed end-to-end boot replay. The developer could have built the feature
without AI, but would not have attempted its UserSid reverse engineering or
PEB command-line lookup. It therefore remains comparable with future features.

## Technical Record

The structured data below preserves the canonical fields used by the
cross-feature rollup.

```yaml
feature_slug: improve-windows-process-collection
feature_abbrev: wpc
status: closed
opened: 2026-08-13
closed: 2026-08-19

# --- Feature Velocity ---
ts_open: 2026-08-13
ts_available: 2026-08-19
availability_anchor: "wiki/work/improve-windows-process-collection/verification.md §Final overnight smoke-test with boot replay — PASS (2026-08-18 → 2026-08-19); first accepted end-to-end evidence for frozen acceptance criterion 6"
criteria_amendments: []
lead_time_days: 6
solo_hours: 120
feature_velocity: 3.5
velocity_uncertainty: "2-7"
comparability: willingness-only

# --- AI pre-exploration sealed estimates ---
ai_est_solo_hours: null
ai_est_solo_available_date: null
ai_est_ai_available_date: null
ai_est_basis: "Retrofit pilot: the Engineer had already seen the human estimate; the reported 120-hour Design-AI estimate was anchored to that source and is not an independent sealed estimate."

# --- Per-unit development estimates ---
units:
  - id: wpc-01
    est_hours: null
    basis: "Retrofit after implementation; no pre-implementation estimate captured."
    actual_hours: null
  - id: wpc-02
    est_hours: null
    basis: "Retrofit after implementation; no pre-implementation estimate captured."
    actual_hours: null
  - id: wpc-03
    est_hours: null
    basis: "Retrofit after implementation; no pre-implementation estimate captured."
    actual_hours: null
  - id: wpc-04
    est_hours: null
    basis: "Retrofit after implementation; no pre-implementation estimate captured."
    actual_hours: null
  - id: wpc-05
    est_hours: null
    basis: "Retrofit after implementation; no pre-implementation estimate captured."
    actual_hours: null
  - id: wpc-06
    est_hours: null
    basis: "Retrofit after implementation; no pre-implementation estimate captured."
    actual_hours: null
  - id: wpc-07
    est_hours: 8.0
    basis: "Pre-implementation estimate: opt-in Global Logger boot ETL path, registry/session ownership helper, replay dedup, and inert-when-off tests."
    actual_hours: null
  - id: wpc-08
    est_hours: null
    basis: "Skipped by Architect decision on 2026-08-18; manual validation accepted in place of formal harness."
    actual_hours: null
  - id: wpc-09
    est_hours: 6.0
    basis: "Sealed pre-implementation estimate captured 2026-08-18 for the final bug sweep, audit, and manual-smoke handoff."
    actual_hours: null

# --- Human estimates (retrospective pilot; seal broken) ---
human_est_solo_hours: 120
human_est_solo_available_date: 2026-09-02
human_est_ai_available_date: null

# --- Diagnostics (optional; never part of Results) ---
attention_hours: 3.47
attention_coverage: "Claude Code sessions only; 15-minute-gap clustering; undercounts single-message blocks and excludes off-session validation and OpenCode activity."
actual_api_cost_usd: null
closeout_attempted_without_ai: "Partially, yes. But I would not have attempted the ProcessTraceData reverse engineering to resolve UserSid, nor would I have attempted the PEB lookup to resolve the CommandLine."

findings: "Retrospective pilot: 120 solo-hours delivered in 6 calendar days gives Feature Velocity 3.5 (uncertainty 2-7); willingness-only comparability; illustrative rather than evidentiary because the dual-estimate seal was broken."
```

## Close-Out Tabulation

| Measure | Human estimate | Engineer estimate | Observed |
|---|---:|---:|---:|
| Solo-hours | 120 (retrospective; seal broken) | null (seal already broken) | n/a — counterfactual |
| Solo availability | 2026-09-02 (reconstructed from “3 work weeks”) | null | n/a — counterfactual |
| AI-workflow availability | null | null | 2026-08-19 |
| Estimated delivery speed | — | — | **3.5×**; plausible range **about 2×–7×** |
| Attention diagnostic | — | — | 3.47 h (partial coverage) |
| API cost | — | — | unavailable |

The calculation is `120 / (5.714 × 6) = 3.5`. In plain language, the feature
arrived at an estimated **3.5× one solo developer's pace**. Because this pilot
lacks two independent estimates made before work began, treat it as a rough
**2×–7×** result rather than a precise measurement. It is an illustration;
future trends across properly recorded features matter more than this point.

The 3.47-hour attention value is retained only as a coverage-annotated
mechanism diagnostic. It is neither the denominator nor an ROI ratio. Per-unit
actual hours are also unavailable: audits record verification evidence rather
than duration, and several units landed in shared same-day commits. No values
were reconstructed.

## Related

- [[wiki/concept/velocity-metric]] — approved definition and framing
- [[wiki/decision/ai-velocity-roi-mini-lab]] — measurement protocol
- [[wiki/concept/metrics-template]] — canonical per-feature format
- [[wiki/metrics]] — cross-feature rollup
