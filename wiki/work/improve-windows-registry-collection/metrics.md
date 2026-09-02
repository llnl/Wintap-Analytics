---
title: "Metrics: Improve Windows Registry Collection"
type: concept
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/decision/ai-velocity-roi-mini-lab.md
  - ../Wintap-Analytics/wiki/concept/metrics-template.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: registry
audience: llm-agent
status: reviewed
source_paths: wiki/work/improve-windows-registry-collection/metrics.md
tags: [feature-work, metrics, velocity, registry, windows-sensor, etw]
---

# Feature Metrics: Improve Windows Registry Collection

Velocity results governed by [[wiki/decision/ai-velocity-roi-mini-lab]]
(v2.1); metric definition in [[wiki/concept/velocity-metric]].
SEAL NOTE: `interview.md` `## Sealed — human estimates` must not be read by
the estimating agent until close-out. Seal status at estimate time: **intact**
— the Engineer wrote the `ai_est_*` fields below BEFORE opening `interview.md`
at all (it will be read only up to, not including, the
`## Sealed — human estimates` heading until close-out). **Unsealed at
close-out 2026-08-25** (seal lift authorized by the Architect's close-out
dispatch): both estimates were independently sealed — a second fully valid
dual-estimate point after shc.

Acceptance criteria are frozen at feature open (2026-08-25) per ADR
guardrail 1; the frozen criteria live in `brief.md` and any mid-feature change
must be logged in `criteria_amendments` below.

Estimation note on the spikes-in-feature model: the pre-open POC spike
(retroactive units wrc-01/wrc-02) already retired the discovery risk before
`ts_open`, so the AI-workflow lead time measured here covers design fold-in
plus the new-sensor build. The solo forced-counterfactual deliberately
INCLUDES the ETW reverse-engineering (per the feature dispatch): one
unassisted developer would have had to run the KCB-correlation dead end and
the capture-filter probe series themselves, with only a cryptic conference
note as a lead and no public documentation of the mechanism anywhere.

## Results

- **Estimated delivery speed:** **42.0× one solo developer's pace**
- **Plausible range:** **about 7×–84× faster**
- **Estimate confidence:** **Low-to-moderate**
- **Why confidence is low-to-moderate:** Both solo estimates were
  independently sealed, but they disagree 3× (240 h vs. 80 h) — the widest
  spread in the series — and the same-day open→available lead time forces
  the minimum 1-day denominator, so calendar granularity dominates. The
  headline is directionally strong (even the low estimate gives 14×) but
  the point value is the noisiest in the series.
- **Delivered in:** **same day** (opened 2026-08-25 → Architect-accepted
  availability 2026-08-25; recorded as the 1-day minimum denominator — the
  protocol is silent on same-day features, so the smallest whole calendar
  day is used and noted here)
- **Estimated solo effort:** **240 hours** (human, sealed: "6 weeks" — the
  forced counterfactual deliberately INCLUDED the ETW capture-mode
  reverse-engineering per the estimation note above)

The availability anchor is the Architect-run live verification of
2026-08-25 (wrc-07 evidence, recorded verbatim in
[[wiki/work/improve-windows-registry-collection/verification]]) together
with the wrc-08 live smoke test the Architect accepted the same day
(verdict, verbatim: "smoke test looks fantastic"); feature accepted against
the frozen brief criteria 2026-08-25. Q3 answer, verbatim: **"Yes, but not
the ETW discovery"** — the Architect would have attempted the sensor
cleanup solo but not the undocumented capture-mode reverse-engineering.
Classified **willingness-only** (not excluded from the fitted trend): the
answer declines attempt, not capability, and the sealed 240 h forced
counterfactual explicitly priced the ETW work, so the solo counterfactual
remains defined for the full scope — the WPC precedent. The
scope-AI-makes-attemptable signal is tracked as a finding, exactly what Q3
exists to surface.

## Technical Record

The structured data below preserves the canonical fields used by the
cross-feature rollup.

```yaml
feature_slug: improve-windows-registry-collection
feature_abbrev: wrc
status: closed
opened: 2026-08-25
closed: 2026-08-25

# --- Feature Velocity (computed at close-out) ---
ts_open: 2026-08-25              # = opened; interview / design kickoff
ts_available: 2026-08-25         # first Architect-accepted validation event vs. frozen criteria
availability_anchor: "wiki/work/improve-windows-registry-collection/verification.md — the Architect-run live verification of 2026-08-25 (wrc-07 evidence contract, recorded verbatim) together with the same-day wrc-08 live smoke test (Architect verdict, verbatim: 'smoke test looks fantastic'); chosen because it is the first Architect-accepted dated demonstration of the frozen brief criteria on a branch build, and acceptance against those criteria was declared 2026-08-25."
criteria_amendments: []          # none — wrc-08 was a scoped Non-Goals exception, explicitly NOT a criteria amendment
lead_time_days: 1                # same-day open->available (2026-08-25 -> 2026-08-25); protocol is silent on same-day features, so the minimum whole calendar day (1) is used, stated per the close-out dispatch
solo_hours: 240                  # human sealed forced-counterfactual: "6 weeks" = 6 x 40 h (numerator; portfolio weight)
feature_velocity: 42.0           # 240 / (5.714 × 1) = 42.0
velocity_uncertainty: "7-84"     # two sealed estimates imply 14.0 (80 h) to 42.0 (240 h); widened ±2x per protocol
comparability: willingness-only  # Q3 = "Yes, but not the ETW discovery": declines attempt, not capability; sealed 240 h counterfactual priced the ETW work, so the solo counterfactual is defined for the full scope — included in the fitted trend (WPC precedent)

# --- AI pre-exploration sealed estimates (Engineer; written BEFORE reading
# --- any part of interview.md; seal intact) ---
ai_est_solo_hours: 80            # independent forced-counterfactual, hours
ai_est_solo_available_date: 2026-10-06  # est. date feature available if built solo, no AI
ai_est_ai_available_date: 2026-08-28    # est. date feature available with the AI workflow
ai_est_basis: "Solo scope includes multi-probe reverse-engineering of an undocumented ETW capture filter (publicly documented as an unfixable gap) plus a full sensor rewrite (typed event-ID parsing, 6-type value decode, re-assert logic, tests, live verification) — roughly 2x shc's engineering volume with genuine research risk; AI-side the POC has already retired the discovery, leaving ADR + ~5 units + live verification, calibrated against shc closing in 1 day (where I was 6 days pessimistic)."

# --- Per-unit development estimates (Engineer, at instruction drafting;
# --- actual_hours filled at close-out from the unit's audit) ---
# wrc-01/wrc-02 are retroactive pre-open spike units (already executed as the
# POC); they carry no pre-implementation estimates by definition and are
# excluded from the per-unit quality loop. New-sensor units are appended here
# at instruction drafting time.
# NOTE 2026-08-25: rows below recorded at implementation-plan drafting while
# all units are still Proposed (per the resumed feature-open dispatch); each
# estimate is revisable pre-implementation at instruction drafting if scope
# shifts (shc precedent), never after implementation begins.
units:
  - id: wrc-03
    est_hours: 2.5
    basis: "Recorded 2026-08-25 at plan drafting (unit Proposed): pure decode core — numeric-event-ID dispatch + six-REG-type decoder ported from the POC's verified DecodeRegValue, byte fixtures straight from probe5.log raw dumps; no ETW, no elevation, no schema dependency; wpc-01 pure-parser pattern. CONFIRMED unchanged at instruction drafting 2026-08-25 (scope exactly as planned; fixtures embedded in the instruction)."
    actual_hours: null  # MISSING DATA (never-gates): audit (Complete, 2026-08-25, 52/52 wrc-03 tests) records only the date; no intra-day duration derivable; developer_docs/ is gitignored so no artifact commit trail.
  - id: wrc-04
    est_hours: 3.5
    basis: "Recorded 2026-08-25 at plan drafting (unit Proposed) as 4.0 assuming an A-or-B midpoint on the session-handle option. REVISED to 3.5 at instruction drafting 2026-08-25: Option A decided (guarded reflection — no session-lifecycle P/Invoke), scope pinned to one new enabler class + seams + ~11 no-ETW tests; small residual novelty is the IntPtr/pinned-buffer adaptation (AllowUnsafeBlocks not enabled in Wintap) and pointer-content assertions in the fake."
    actual_hours: null  # MISSING DATA (never-gates): audit (Complete, 2026-08-25, 11/11 wrc-04 tests) records only the date; same derivation gap as wrc-03.
  - id: wrc-05
    est_hours: 1.5
    basis: "Recorded 2026-08-25 at plan drafting (unit Proposed): WintapMessage RegActivityObject/DataTypeEnum extension per the Architect's schema decision — small isolated diff plus round-trip tests; risk is downstream (EPL/Parquet) review, not code volume. CONFIRMED unchanged at instruction drafting 2026-08-25 (decided shape is the minimal two-field/two-member extension assumed)."
    actual_hours: null  # MISSING DATA (never-gates): audit (Complete, 2026-08-25, 14/14 wrc-05 tests) records only the date; same derivation gap.
  - id: wrc-06
    est_hours: 4.0
    basis: "Recorded 2026-08-25 at plan drafting (unit Proposed): RegistrySensor rewrite on wrc-03/04/05 plus deletion of four legacy files (parsers, manager, two models); mapping tests per event ID and create-vs-overwrite semantics; roughly a wpc-02-scale sensor-core unit but with the decode core already landed. CONFIRMED unchanged (4.0 h) at instruction drafting 2026-08-25: scope landed as planned — the emission contract and payload schemas are fully pre-specified from probe8 (no discovery left in the unit), and the two small additions (EtwProviderSensor OnEtwSessionStarted hook + one-line Counter++ statistics fix) are offset by the decode core already being landed; ~16 no-ETW tests via wpc-style DI seams (injected emit + Read-gate)."
    actual_hours: null  # MISSING DATA (never-gates): audit (Complete, 2026-08-25, 34/34 wrc-06 tests) records only the date; same derivation gap.
  - id: wrc-07
    est_hours: 3.0
    basis: "Recorded 2026-08-25 at plan drafting (unit Proposed): keyword-mask config + canary wire-up + overhead measurement + Architect-run live verification support; includes manual-run coordination overhead (shc-02 precedent); blocked on the mask and canary decisions. CONFIRMED unchanged at instruction drafting 2026-08-25 after probe8 PASS: drafting resolved the blocks without growing scope — mask wiring shrank to a two-value selector off the existing CollectRegistryRead setting (no new config surface), and the canary landed as one seam-driven state-machine class (~11 no-ETW tests) roughly as assumed; live-verification effort is Architect-side by design."
    actual_hours: null  # MISSING DATA (never-gates): audit (Complete, 2026-08-25, 14/14 wrc-07 tests) records only the date; Architect live-run time not separable.
  - id: wrc-08
    est_hours: 2.0
    basis: "Recorded 2026-08-25 at instruction drafting, BEFORE implementation (unit rolled in by Architect decision the same day — scoped Non-Goals exception per the shc-03 realize-now precedent; NOT a criteria amendment, criteria_amendments stays empty): two-file additive diff fully pre-specified in the instruction (2 EPL select lines + 2 group-by terms; 3 new Reg_ columns via an order-preserving static BuildFlatMessage seam in RegistrySerializer), ~9 no-Esper-runtime tests; the only novelty risk is the standalone NEsper compile smoke test (config mirrored from EventChannel.cs:169-178, documented fallback if the environment fights it); the live DuckDB query addendum is Architect-side by design."
    actual_hours: null  # MISSING DATA (never-gates): audit (Complete, 2026-08-25, 9/9 wrc-08 tests; Developer worked in an external harness) records only the date; same derivation gap.

# --- Human sealed estimates (copied verbatim from interview.md at close-out 2026-08-25) ---
human_est_solo_hours: 240            # Q1 answer verbatim: "6 weeks" — interpreted as 240 working hours (6 x 40 h) per the interview record
human_est_solo_available_date: null  # MISSING DATA: no explicit solo calendar date given; interview notes ~2026-10-06 as derived from "6 weeks", not separately stated
human_est_ai_available_date: "2026-08-26..2026-08-27"  # Q2 answer verbatim: "2 days" from the 2026-08-25 open

# --- Diagnostics (optional; never part of Results; filled at close-out) ---
attention_hours: null            # OMITTED: multi-harness feature (Developer ran in an external harness); not cheap to compute, per protocol — same reason shc omitted it
attention_coverage: "omitted — multi-harness (Claude Code + external Developer harness); no cross-harness merge attempted per protocol"
actual_api_cost_usd: null        # MISSING DATA: not available
closeout_attempted_without_ai: "Yes, but not the ETW discovery"  # verbatim; willingness-only — see comparability

findings: "Widest sealed-estimate spread in the series (240 vs 80 solo-hours, 3x) delivered same-day: Feature Velocity 42.0 (uncertainty 7-84) on the minimum 1-day denominator; comparability willingness-only (Q3: would have attempted the sensor cleanup solo but not the ETW capture-mode reverse-engineering — the scope-AI-makes-attemptable signal, second occurrence after WPC). Human AI-date prediction ('2 days') was 1-2 days pessimistic; Engineer's AI date (2026-08-28) 3 days pessimistic; the discovery risk had already been retired by the pre-open POC spike, which both estimators underweighted."
```

## Close-Out Tabulation

| Measure | Human estimate (sealed) | Engineer estimate (sealed) | Observed |
|---|---:|---:|---:|
| Solo-hours | 240 ("6 weeks") | 80 | n/a — counterfactual |
| Solo availability date | missing (derived ~2026-10-06, not stated) | 2026-10-06 | n/a — counterfactual |
| AI-workflow availability date | 2026-08-26..2026-08-27 ("2 days") | 2026-08-28 | **2026-08-25** (same day) |
| Feature Velocity | — | — | **42.0** (uncertainty 7–84) |
| Attention diagnostic | — | — | omitted (multi-harness; not cheap) |
| API cost | — | — | unavailable |

The calculation is `240 / (5.714 × 1) = 42.0`, on the minimum 1-day
denominator (same-day open→available; the protocol is silent on same-day
features, so 1 is used and stated). The two independently sealed solo
estimates imply Velocities of 14.0 (80 h) and 42.0 (240 h); widening that
band ±2× per protocol gives the reported **7–84** range. This is by
construction the noisiest point in the series — a 3× estimator spread on a
1-day denominator — and even so its floor (7×) matches shc's headline. The
trend across features, not this point, remains the product.

**Calibration notes.** Both AI-workflow date predictions were pessimistic:
the human's "2 days" by 1–2 days, the Engineer's 2026-08-28 by 3 days —
actual availability landed same-day. Both estimators underweighted the same
structural fact recorded in the estimation note above: the pre-open POC
spike had already retired the feature's discovery risk before `ts_open`, so
the measured AI-workflow window contained only fold-in plus a well-specified
build (the spikes-in-feature model shifts risk outside the measured
boundary — a standing calibration lesson for POC-first features). The
solo-hours spread (240 vs. 80, 3×) is the widest yet, versus shc's tight
1.2× — unsurprising: the dominant unknown is how long an unassisted
developer would take to reverse-engineer an undocumented ETW capture mode
from a cryptic conference note, which neither estimator can ground.

**Per-unit quality loop.** Estimates: wrc-03 2.5 h, wrc-04 3.5 h,
wrc-05 1.5 h, wrc-06 4.0 h, wrc-07 3.0 h, wrc-08 2.0 h (16.5 h total, all
recorded pre-implementation; wrc-01/wrc-02 retroactive spikes excluded by
definition). Per-unit actuals are missing data across the board (audits
record verification evidence and dates, not durations; `developer_docs/` is
gitignored so no artifact commit trail). What is observable: all six units
completed within a single calendar day with **zero instruction rework
cycles** and zero mid-unit stops — including wrc-08, rolled in the same day
it was drafted, approved, implemented, and audited (9/9 unit tests, 134/134
`Category~wrc`, 299/299 full suite). The whole feature landed as a single
commit on `develop-wrc`: `1f66a47` ("Add wrc: manifest-only registry sensor
via undocumented capture-mode filter (wrc-01..08)", 32 files) — unlike shc's
per-unit commits, so no per-unit commit trail exists either.

## Related

- [[wiki/concept/velocity-metric]] — approved definition and framing
- [[wiki/decision/ai-velocity-roi-mini-lab]] — measurement protocol (v2.1)
- [[wiki/metrics]] — cross-feature rollup (this feature's row appended 2026-08-25)
- [[wiki/work/improve-windows-registry-collection/verification]] — availability anchor
- [[wiki/component/registry-sensor]] — canonical fold-in of the stabilized sensor
- [[wiki/diagnostic/windows-sensor-sweep-queue]] — findings cataloged at close-out
