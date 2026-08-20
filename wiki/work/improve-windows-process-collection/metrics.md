---
title: "Feature Metrics: Improve Windows Process Collection"
type: concept
confidence: medium
grounded_by:
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
last_validated: 2026-08-19
repo_scope: wintap
implementation_area: windows-sensor
event_domain: process
audience: mixed
status: draft
source_paths: wiki/work/improve-windows-process-collection/metrics.md
tags: [feature-work, metrics, velocity, roi, process-events, windows-sensor]
---

# Feature Metrics: Improve Windows Process Collection

Velocity/ROI mini-lab data per [[wiki/decision/ai-velocity-roi-mini-lab]].
SEAL NOTE: this file was retrofitted after feature open and after the human
and reported Design-AI solo estimate were known. The sealed-estimate discipline
is therefore broken for this feature; missing values stay null rather than
being reconstructed. The wpc-09 per-unit estimate is the only genuinely
sealed pre-implementation estimate in this feature.

## Metrics Data

```yaml
feature_slug: improve-windows-process-collection
feature_abbrev: wpc
status: closed
opened: 2026-08-13
closed: 2026-08-19

# --- AI pre-exploration sealed estimates (Engineer; written BEFORE reading
# --- the interview's sealed section; null if the seal was already broken) ---
ai_est_solo_human_hours: 120
ai_est_attention_design_hours: null
ai_est_attention_dev_hours: null
ai_est_basis: "Retrofit: Architect reported Design-AI estimate of 3 solo-dev weeks; not sealed or independent. Feature is 8 units spanning kernel ETW replacement, snapshot/enrichment, boot ETL, and validation harness."

# --- Per-unit development estimates (Engineer, at instruction drafting;
# --- actual_hours filled at close-out from the unit's audit) ---
# Close-out note on actual_hours: audits record verification evidence, not
# durations, and multiple units landed in shared same-day commits (wpc-02/03
# in b500966; wpc-05/06 in 0f273e0; wpc-07/09 in 19e89dc), so per-unit
# wall-clock actuals are not derivable — left null per never-reconstruct.
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
    basis: "Remaining pre-implementation estimate: opt-in Global Logger boot ETL path, registry/session ownership helper, replay dedup, inert-when-off tests."
    actual_hours: null
  - id: wpc-08
    est_hours: null
    basis: "Skipped by Architect decision on 2026-08-18; manual validation accepted in place of formal harness."
    actual_hours: null
  - id: wpc-09
    est_hours: 6.0
    basis: "SEALED pre-implementation estimate captured 2026-08-18 at instruction drafting: final bug sweep covering boot-trace startup arm/disarm lifecycle, parent-warning triage, DuckDB command-line escaping tests/fix if confirmed, optional logger-tag cleanup, audit, and manual-smoke handoff."
    actual_hours: null

# --- Human sealed estimates (copied from interview.md at close-out ONLY) ---
human_est_solo_hours: 120
human_est_ai_attention_hours: null

# --- Actuals (filled at close-out) ---
ts_feature_open: 2026-08-13
ts_design_end: 2026-08-17   # first Architect-approved instruction (wpc-01, per mini-lab phase boundary)
ts_final_audit: 2026-08-18  # wpc-09 audit date
actual_attention_hours: 3.47
actual_api_cost_usd: null   # unavailable; best-effort per the mini-lab decision
closeout_attempted_without_ai: "Partially, yes. But I would not have attempted the ProcessTraceData reverse engineering to resolve UserSid, nor would I have attempted the PEB lookup to resolve the CommandLine."

findings: "Estimated 120 solo hours vs. 3.47 measured attention hours (~35x, with the retrofit seal-break caveat and the proxy's known undercount bias); the two hardest sub-problems (UserSid reverse engineering, PEB command-line lookup) would not have been attempted solo at all."
```

## Attention Proxy Method Record

Computed by the main session 2026-08-19 per the normative 15-minute-gap
definition in [[wiki/decision/ai-velocity-roi-mini-lab]]:

- Window: 2026-08-13T21:49Z → 2026-08-19T13:40Z, 72 human messages across
  wintap-project sessions.
- 18 attention blocks at the 15-minute gap threshold; 7 single-message blocks
  contributing zero (the known undercount bias).
- Per-day: 2026-08-13: 0.33 h; 2026-08-17: 2.89 h; 2026-08-18: 0.03 h;
  2026-08-19: 0.22 h. **Total: 3.47 h.**
- The 08-18 figure illustrates the undercount: the Architect was active
  (smoke validation, wpc-09 approval) but in brief, widely spaced check-ins
  that mostly formed single-message blocks.

## Close-Out Tabulation

| Quantity | Human est. | AI est. | Actual |
| --- | --- | --- | --- |
| Solo, no-AI hours | 120 (retrofit, seal broken) | 120 (retrofit, anchored — same source) | n/a (counterfactual) |
| AI-workflow attention hours | not captured | not captured | 3.47 (proxy) |
| API cost (USD) | — | — | unavailable |
| wpc-07 development hours | — | 8.0 | not derivable |
| wpc-09 development hours | — | 6.0 (sealed) | not derivable |

**Rough ROI:** ~120 estimated solo hours vs. 3.47 measured attention hours —
roughly 35:1, before API cost (unavailable) and subject to two large caveats:
(1) the solo estimate was retrofitted after disclosure, so the human/AI
estimates are not independent and the 120 h figure carries the counterfactual
±2x noise floor; (2) the attention proxy consistently undercounts
(single-message blocks contribute zero; off-session validation time such as
the overnight smoke setups is invisible to it).

**Close-out question:** "Partially, yes. But I would not have attempted the
ProcessTraceData reverse engineering to resolve UserSid, nor would I have
attempted the PEB lookup to resolve the CommandLine." — i.e. the feature
would have shipped, if at all, without its two highest-value enrichment
capabilities.

**Per-unit quality signal:** no estimate-vs-actual comparison is possible
this feature (actuals not derivable from day-granularity shared commits);
the sealed wpc-09 estimate demonstrates the intended drafting-time protocol
for future features.

## v2 Addendum (2026-08-19) — re-recorded under the revised mini-lab

Re-recording per the v2 revision of
[[wiki/decision/ai-velocity-roi-mini-lab]] (headline pivot to
time-to-availability + throughput; attention demoted to diagnostic). The v1
record above is preserved unchanged; this block is the authoritative one for
cross-feature aggregation. All v2-specific caveats are listed below the
block.

```yaml
# --- v2 metrics block (authoritative for aggregation) ---
feature_slug: improve-windows-process-collection
feature_abbrev: wpc
status: closed
opened: 2026-08-13
closed: 2026-08-19

# Headline: time-to-availability
ts_open: 2026-08-13
ts_available: 2026-08-19
availability_anchor: "wiki/work/improve-windows-process-collection/verification.md §Final overnight smoke with boot replay — PASS (2026-08-18 → 2026-08-19); chosen because brief acceptance criterion 6 (armed-reboot boot ETL replay) is inside acceptance scope and was only evidenced end-to-end by this 2026-08-19-dated artifact"
lead_time_days: 6

# Companion: throughput weight
throughput_weight_hours: 120

# AI pre-exploration sealed estimates — not reconstructable (retrofit; seal
# was already broken in v1, and v2 postdates feature close)
ai_est_solo_available_date: null
ai_est_ai_available_date: null
ai_est_basis: "v2 postdates feature close; no sealed calendar estimate existed to convert."

# Human sealed estimates (v2 currency)
human_est_solo_available_date: 2026-09-02  # UNITS RECONSTRUCTION — see caveats
human_est_solo_hours: 120
human_est_ai_available_date: null          # never captured (v1 retrofit gap)

# Diagnostics (never headline)
attention_hours: 3.47
attention_coverage: "claude-code sessions only; 15-min-gap clustering; known undercount (single-message blocks, off-session validation invisible)"
actual_api_cost_usd: null
closeout_attempted_without_ai: "Partially, yes. But I would not have attempted the ProcessTraceData reverse engineering to resolve UserSid, nor would I have attempted the PEB lookup to resolve the CommandLine."

findings: "Lead time 6 calendar days (2026-08-13 → 2026-08-19, includes an idle 3-day weekend) vs. a reconstructed ~20-calendar-day solo counterfactual (~3.3x); throughput weight 120h; the two hardest sub-problems would not have been attempted solo at all."
```

### v2 availability-anchor rationale

The feature brief's acceptance criteria explicitly include criterion 6:
armed-reboot boot ETL replay yielding pre-service Start events with SIDs. The
Architect's 2026-08-18 manual-validation acceptance (kernel-era roots,
usernames, stable overnight — the wpc-08 skip decision) predated the
end-to-end boot-replay confirmation, which the earlier Code42-AAT event-store
lock had blocked. The first dated artifact evidencing Architect-accepted
validation of the full acceptance scope is therefore the final overnight
smoke concluding **2026-08-19** (recorded in `verification.md`; feature
closeout the same day). Lead time: 2026-08-13 → 2026-08-19 = **6 calendar
days**, deliberately including the idle 2026-08-14→16 three-day weekend.

### v2 caveats

- **Solo counterfactual is a UNITS RECONSTRUCTION.** The estimate was
  captured pre-convention as "3 weeks" meaning three 5-day work weeks
  (~120 h), on a feature already carrying a retrofit seal-break caveat.
  Reconstructed calendar reading: three work-weeks from Thursday 2026-08-13
  → ~2026-09-02 ≈ **20 calendar days**. Treat the date with even wider error
  bars than a normally-sealed calendar estimate.
- **Calendar noise:** the idle 3-day weekend inside the 6-day lead time is a
  50–100%-scale relative distortion of the kind the v2 ADR accepts as
  consistent bias on short features.
- **Attention 3.47 h is a coverage-annotated diagnostic only** (claude-code
  sessions only; the OpenCode Engineering & Development harness channel was
  not mined), retained from v1 as the mechanism probe — it does not headline.

## Velocity Addendum (2026-08-19) — v2.1 Feature Velocity

Added under the v2.1 Velocity protocol ([[wiki/concept/velocity-metric]];
[[wiki/decision/ai-velocity-roi-mini-lab]] Revision History), adopted the same
day the feature closed. Computed per the canonical formula from the v2
addendum's existing lead time (6 calendar days) and 120 solo-hours weight.
Prior blocks are preserved unchanged; this block is authoritative for
Velocity aggregation.

```yaml
# --- v2.1 Velocity addendum (authoritative for Velocity aggregation) ---
solo_hours: 120
feature_velocity: 3.5        # 120 / (5.714 × 6) = 3.5003 → 3.5
velocity_uncertainty: "2-7"  # default ±2x band pending calibration (see caveats)
comparability: willingness-only
```

- **Feature Velocity 3.5 (uncertainty 2–7):**
  `120 solo-hours / (5.714 × 6 days) ≈ 3.5`.
- **Pilot caveats carry over — illustrative, not evidentiary.** The 120
  solo-hours figure is the retrofit, unsealed estimate (disclosed before
  recording), and the AI estimate was anchored to the same source, so no
  independent second estimate exists to form a two-estimate spread; the
  uncertainty range is the default ±2× widening as stated in the approved
  pitch's own asterisked pilot illustration.
- **Comparability: willingness, not capability.** The close-out answer says
  the UserSid reverse engineering and PEB command-line lookup would not have
  been *attempted* solo — a willingness statement about scope the developer
  was capable of building. Per the v2.1 comparability guardrail,
  willingness-only answers do **not** exclude a feature from the fitted
  trend: WPC stays in the trend as an annotated point.
- Rollup row: [[wiki/metrics]].
