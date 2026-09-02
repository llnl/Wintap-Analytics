---
title: "Velocity Rollup (Cross-Feature Metrics)"
type: concept
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/decision/ai-velocity-roi-mini-lab.md
  - ../Wintap-Analytics/wiki/concept/velocity-metric.md
  - ../Wintap-Analytics/wiki/work/improve-windows-process-collection/metrics.md
  - ../Wintap-Analytics/wiki/work/windows-sensor-health-check/metrics.md
  - ../Wintap-Analytics/wiki/work/improve-windows-registry-collection/metrics.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: none
audience: mixed
status: draft
source_paths: wiki/metrics.md
tags: [metrics, velocity, rollup, feature-work, solo-hours]
---

# Velocity Rollup

One row per closed feature, appended at feature close-out. Metric definition:
[[wiki/concept/velocity-metric]]; protocol:
[[wiki/decision/ai-velocity-roi-mini-lab]] (v2.1).
`Velocity = solo-hours / (5.714 × days)` — one decimal, uncertainty range
attached. The trend across features, not any single point, is the product.

## Closed Features

| Feature | Lead time (days) | Solo estimate (h) | Feature Velocity (± uncertainty) | Comparability flag | Metrics |
|---|---|---|---|---|---|
| improve-windows-process-collection | 6 | 120 | **3.5** (2–7) — retrofit/unsealed pilot; illustrative, not evidence | willingness-only: UserSid/PEB work would not have been *attempted* solo but was within capability — **not excluded** from the trend | [[wiki/work/improve-windows-process-collection/metrics]] |
| windows-sensor-health-check | 1 | 40 | **7.0** (3.5–17) — first fully valid dual-sealed point; 1-day denominator makes it calendar-noisy | none: Q3 "Yes" — plain counterfactual, capability not exceeded; included in the fitted trend | [[wiki/work/windows-sensor-health-check/metrics]] |
| improve-windows-registry-collection | 1 (same-day open→available; minimum denominator, protocol silent on same-day) | 240 ("6 weeks") | **42.0** (7–84) — widest sealed-estimate spread yet (240 vs 80 h, 3×) on the minimum denominator; noisiest point in the series | willingness-only: Q3 "Yes, but not the ETW discovery" — declines attempt, not capability; the sealed counterfactual priced the ETW work, so the point is **not excluded** from the fitted trend (WPC precedent) | [[wiki/work/improve-windows-registry-collection/metrics]] |

## Portfolio Velocity

**Pending N ≥ several closed features.** Computed as
`sum(solo-hours of features closed in window) / (5.714 × window-days)` over a
trailing window ≥ 4× the median lead time, and read as a smoothed trend only
(WIP is invisible until close; window edges swing short windows; small N
scatters). Until then, only the per-feature points above are meaningful.
