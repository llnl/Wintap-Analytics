---
title: "Metrics: Windows Sensor Health-Check"
type: concept
confidence: high
grounded_by:
  - ../Wintap-Analytics/wiki/decision/ai-velocity-roi-mini-lab.md
  - ../Wintap-Analytics/wiki/concept/metrics-template.md
policy: agent-editable
last_validated: 2026-08-25
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: llm-agent
status: reviewed
source_paths: wiki/work/windows-sensor-health-check/metrics.md
tags: [feature-work, metrics, velocity, health-check, windows-sensor]
---

# Feature Metrics: Windows Sensor Health-Check

Velocity results governed by [[wiki/decision/ai-velocity-roi-mini-lab]]
(v2.1); metric definition in [[wiki/concept/velocity-metric]].
SEAL NOTE: `interview.md` `## Sealed — human estimates` must not be read by
the estimating agent until close-out. Seal status at estimate time: **intact**
— the Engineer read `interview.md` only up to (not including) the
`## Sealed — human estimates` heading before recording the `ai_est_*` fields
below. **Unsealed at close-out 2026-08-25**: both estimates were
independently sealed, so this is the first fully valid dual-estimate point
(unlike the WPC retrofit pilot).

Acceptance criteria are frozen at feature open (2026-08-24) per ADR
guardrail 1; the frozen criteria live in `brief.md` and any mid-feature change
must be logged in `criteria_amendments` below.

## Results

- **Estimated delivery speed:** **7.0× one solo developer's pace**
- **Plausible range:** **about 3.5×–17× faster**
- **Estimate confidence:** **Moderate**
- **Why confidence is moderate:** Both solo estimates were independently
  sealed before work began and agree closely (40 h vs. 48 h), but the
  1-calendar-day lead time means calendar granularity dominates the
  denominator — a single point this short carries large relative noise.
- **Delivered in:** **1 calendar day** (opened 2026-08-24 → first
  Architect-accepted live demonstration 2026-08-25 05:39–05:41)
- **Estimated solo effort:** **40 hours** (human, sealed)

The availability anchor is the manual live run on the lab host
(2026-08-25, recorded verbatim in
[[wiki/work/windows-sensor-health-check/verification]]): QueryDosDevice
drive map active, egress checks flushing aggregated FAIL lines, no false
liveness stalls, low-noise. The Architect **would** have attempted this
feature solo (Q3: "Yes") — a plain counterfactual, capability not
exceeded, so the point carries **no comparability flag** and is included
in the fitted trend. Notably, the health check produced its first real
catch during the anchor run itself (a PID=-1 snapshot-refresh Process
event egressing as ProcessName=Unknown — see
[[wiki/diagnostic/windows-sensor-sweep-queue]]).

## Technical Record

The structured data below preserves the canonical fields used by the
cross-feature rollup.

```yaml
feature_slug: windows-sensor-health-check
feature_abbrev: shc
status: closed
opened: 2026-08-24
closed: 2026-08-25

# --- Feature Velocity (computed at close-out) ---
ts_open: 2026-08-24              # = opened; interview / design kickoff
ts_available: 2026-08-25         # first Architect-accepted validation event vs. frozen criteria
availability_anchor: "wiki/work/windows-sensor-health-check/verification.md §Availability anchor — manual live run on the lab host 2026-08-25 05:39–05:41 local (branch build), Architect-accepted; first live demonstration of the frozen criteria: QueryDosDevice map active, egress checks flushing aggregated FAIL lines, no false liveness stalls, low-noise."
criteria_amendments:
  - date: 2026-08-24
    change: "Reporting channel amended by Architect redirection: aggregated health results are periodic Wintap.log summary lines via WintapLogger, replacing the dedicated SensorHealth WintapMessage into Parquet/DuckDB. No WintapMessage schema changes anywhere in the feature. Checks, egress choke point, aggregation, sample cap, coverage, and overhead posture unchanged. Criteria re-frozen same day in brief.md."
  - date: 2026-08-24
    change: "v1 check list made definitive by Architect review (amendment #2, same day): (1) 'Unknown' ProcessName / unknown-sentinel PidHash now FAILS (new process_unresolved check — reverses the prior v1 pass note); (2) new path_unqualified check — File and Registry payload paths must be fully qualified in their grounded emitted forms; (3) new stream-liveness condition — File, Registry, MemoryMap, ImageLoad, TcpConnection, UdpPacket must have nonzero inspected counts per 5 s interval, transition-only logging with startup grace; (4) eventtime_invalid DROPPED from v1 (kept as future candidate). Criteria re-frozen same day in brief.md."
lead_time_days: 1                # raw calendar days, weekends included
solo_hours: 40                   # human sealed forced-counterfactual, hours (numerator; portfolio weight)
feature_velocity: 7.0            # 40 / (5.714 × 1) = 7.0
velocity_uncertainty: "3.5-17"   # two sealed estimates imply 7.0 (40 h) to 8.4 (48 h); widened ±2x per protocol
comparability: none              # Q3 = "Yes": plain counterfactual, capability not exceeded; included in fitted trend

# --- AI pre-exploration sealed estimates (Engineer; written BEFORE reading
# --- the interview's sealed section; seal was intact) ---
ai_est_solo_hours: 48            # independent forced-counterfactual, hours
ai_est_solo_available_date: 2026-09-18  # est. date feature available if built solo, no AI
ai_est_ai_available_date: 2026-08-31    # est. date feature available with the AI workflow
ai_est_basis: "One new subsystem at a known choke point + new message type + flush/sample plumbing + tests across ~17 sensors; comparable to a mid-size wpc-era feature, no novel reverse-engineering."

# --- Per-unit development estimates (Engineer, at instruction drafting;
# --- actual_hours filled at close-out from the unit's audit) ---
units:
  - id: shc-01
    est_hours: 4.0
    basis: "Isolated new subsystem (engine + 5 checks + log flush + liveness state machine), no integration, ptr-style test patterns. Revised 2026-08-24 from 2.5 (engine-only) then 3.0 (log-flush fold-in) to 4.0 when Architect amendment #2 added process_unresolved, path_unqualified, and the 5 s stream-liveness watchdog, pre-implementation."
    actual_hours: null  # MISSING DATA (never-gates): audit and wiki log record only the date (2026-08-24, same-day open->implement); no intra-day start/end timestamps to derive a duration from, and developer_docs/ is gitignored so no commit-time trail exists for the artifacts. Verified complete: 33/33 shc-01 tests.
  - id: shc-02
    est_hours: 3.0
    basis: "Recorded 2026-08-24 at instruction drafting, pre-implementation: three one-line Inspect call sites + a small internal EventChannel seam/helper + lifecycle Start/Stop in WintapSvcCore + integration tests that must navigate heavy type initializers (StateManager/EventChannel/Env) via env seams and a temp data root + the documented manual live run with overhead sanity check."
    actual_hours: null  # MISSING DATA (never-gates): completed 2026-08-25 (commit b0528f8) but the audit was never filed — the Developer worked in an external harness. Durable evidence: verification.md + independently re-run 65/65 shc suite. Paused 2026-08-24 on the diskpart elevation conflict; resumed after shc-03.
  - id: shc-03
    est_hours: 2.0
    basis: "Recorded 2026-08-24 at instruction drafting, pre-implementation: single-method replacement in one file with an exact in-repo P/Invoke precedent (WindowsProcessSensor.TryTranslateDevicePathToWin32Path), a pure BuildDriveMap/TryParse seam, and ~7 no-admin tests incl. one lenient live smoke. Revised same day 1.5 -> 2.0, still pre-implementation, when the Architect widened the unit to include the fromNative guard fix in BaseWindowsSensor.cs (+~5 translation-path tests, +private->internal seam); the fix itself is small and fully specified in the instruction."
    actual_hours: null  # MISSING DATA (never-gates): audit records only the date (2026-08-25); no intra-day start/end timestamps; developer_docs/ is gitignored so no commit-time trail for the artifacts. Verified complete: 27/27 shc-03 tests.

# --- Human sealed estimates (copied from interview.md at close-out 2026-08-25) ---
human_est_solo_hours: 40             # forced-counterfactual solo estimate, hours (Q1)
human_est_solo_available_date: null  # MISSING DATA: no solo calendar date given at open (per never-gates)
human_est_ai_available_date: "2026-08-25..2026-08-26"  # given as "1 - 2 days" from the 2026-08-24 open

# --- Diagnostics (optional; never part of Results; filled at close-out) ---
attention_hours: null            # OMITTED: multi-harness feature (Claude Code + external Developer harness); not cheap to compute, per protocol
attention_coverage: ""
actual_api_cost_usd: null        # MISSING DATA: not available
closeout_attempted_without_ai: "Yes"  # verbatim; plain counterfactual, capability not exceeded — no comparability flag

findings: "First fully valid dual-sealed point: 40 solo-hours delivered in 1 calendar day gives Feature Velocity 7.0 (uncertainty 3.5-17); comparability none. Human AI-availability prediction ('1 - 2 days') hit exactly at its optimistic edge; Engineer's AI date (2026-08-31) was 6 days pessimistic; solo-hours spread tight (40 vs 48). The health check scored its first real catch during the anchor run (PID=-1 Refresh event egressing as ProcessName=Unknown) — cataloged with the full sweep queue in wiki/diagnostic/windows-sensor-sweep-queue.md."
```

## Close-Out Tabulation

| Measure | Human estimate (sealed) | Engineer estimate (sealed) | Observed |
|---|---:|---:|---:|
| Solo-hours | 40 | 48 | n/a — counterfactual |
| Solo availability date | missing (not given) | 2026-09-18 | n/a — counterfactual |
| AI-workflow availability date | 2026-08-25..2026-08-26 ("1 - 2 days") | 2026-08-31 | **2026-08-25** |
| Feature Velocity | — | — | **7.0** (uncertainty 3.5–17) |
| Attention diagnostic | — | — | omitted (multi-harness; not cheap) |
| API cost | — | — | unavailable |

The calculation is `40 / (5.714 × 1) = 7.0`. The two independently sealed
solo estimates imply Velocities of 7.0 (40 h) and 8.4 (48 h); widening that
band ±2× per protocol gives the reported **3.5–17** uncertainty range. In
plain language, the feature arrived at an estimated **7.0× one solo
developer's pace** — but the 1-day denominator makes this a noisy single
point; the trend across features remains the product.

**Calibration notes.** The human's AI-workflow prediction ("1 - 2 days")
landed exactly at its optimistic edge — the best-calibrated prediction in
the series so far. The Engineer's AI-workflow date (2026-08-31) was six
days pessimistic; its basis ("comparable to a mid-size wpc-era feature")
overweighted the retired three-unit/Parquet-schema draft scope that the
Architect's log-only redirection cut on day one. The solo-hours spread
(40 vs. 48) is tight — a 1.2× ratio between independent estimators.

**Per-unit quality loop.** Estimates: shc-01 4.0 h, shc-02 3.0 h,
shc-03 2.0 h (9.0 h total, all recorded pre-implementation). Per-unit
actuals are missing data across the board (audits record verification
evidence and dates, not durations; the shc-02 audit was never filed;
`developer_docs/` is gitignored so no artifact commit trail exists). What
is observable: all three units completed inside a two-calendar-day window
with zero instruction rework cycles — the one mid-unit stop (shc-02 on
diskpart elevation) was an instruction/codebase conflict handled by
inserting shc-03, exactly the escalation the methodology prescribes, not
a self-containedness failure of the drafted instructions.

## Related

- [[wiki/concept/velocity-metric]] — approved definition and framing
- [[wiki/decision/ai-velocity-roi-mini-lab]] — measurement protocol (v2.1)
- [[wiki/metrics]] — cross-feature rollup (this feature's row appended 2026-08-25)
- [[wiki/work/windows-sensor-health-check/verification]] — availability anchor
- [[wiki/diagnostic/windows-sensor-sweep-queue]] — findings queue for the follow-on sweep feature
