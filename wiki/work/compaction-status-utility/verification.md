---
title: "Verification: Compaction Status Utility"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/HostActivity/test_host_activity.py
  - streamlit/projects/HostActivity/pyproject.toml
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - wiki/work/compaction-status-utility/implementation_plan.md
policy: agent-editable
last_validated: 2026-11-14
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/HostActivity; ../Wintap-PyUtil/wintappy/coordination
tags: [feature-work, status, compaction, verification, streamlit]
---

# Verification: Compaction Status Utility

## Results — planning baseline, November 14

Documentation-only follow-on draft; no utility implementation or deployment.
Existing HostActivity offline suite passes **27 tests**, including real Streamlit
AppTest with mocked S3, in **1.306 seconds** on macOS. This qualifies the unchanged
raw viewer baseline, not compacted/entity queries, status export or coordination.
Streamlit emits non-failing bare-mode/deprecated-width warnings.

## Test commands run

From `streamlit/projects/HostActivity/`, using its existing app environment:

```sh
.venv/bin/python -m unittest discover -s . -p 'test_*.py' -v
```

No live S3, DBT build, ledger initialization, compaction, destructive dataset
operation or sibling-source edit was performed. Documentation checks pass the
four new pages plus the canonical page's required frontmatter fields, 86 grounding
path references and 20 added wikilinks. `git diff --check`, new-file whitespace/
newline checks, local-identifier/IP-pattern checks and complete added-content
privacy review pass. Detailed implementation gates below are not yet run.

## Approved read-mode revision — November 14

The human approved default uncoordinated **Live diagnostic** observation and an
optional **Coordinated refresh**, plus the narrow coordination-contract exception.
Revised the utility artifacts and coordination brief/design/handoff/plan; updated
the index and canonical dashboard's explicitly planned follow-on section. DBT,
authoritative verification, process-locked ledger access and exclusive maintenance/
recovery retain their protections. This is documentation only, not code/deployment
authorization or a new coordination/utility runtime result.

Added mandatory warnings on live/cached/exported observations; unknown/stale writer
status; inconclusive disappearing-object/schema/mixed-entity-generation reads;
per-result/per-page mode and time; no silent coordinated-to-live fallback; and bounded
supervised jobs in both modes. A passing live check is still observational, not
authoritative validation. Reused the existing 27-test baseline above; no additional
app or coordination runtime tests were run for this documentation revision.

Revision documentation checks pass **11 changed/new wiki files**, **9 required-field
frontmatters**, **213 grounding path references** and **28 added wikilinks**, including
**5 section targets**. `git diff --check`, new-file whitespace/newline checks and
added-content local-account/home-path/IP-pattern scans pass. The complete additions
were manually reviewed for persistent-content privacy and read-mode consistency.
These are scoped documentation checks, not a repository-wide wiki lint or runtime
qualification. Changes remain uncommitted/unpushed.

## Post-pull producer review — November 14

Authorized utility planning was committed and rebased as Analytics `94a6688` over
pulled `deae3a3`. PyUtil was already current at `8ee714c`; source review confirms
retained v3 completed runs, receipt-bound independent verification and atomic local
completion. Updated the stale initial planning claims below in brief/design/plan;
advisory status/run/catalog exports and the reader client remain unimplemented.

The original `8ee714c` actual-Mac coordination attempt was **blocked before tests**:
the manifest required root `uv.lock`, which was Git-ignored and absent from that
commit. Main provisioning failed and neither test stage ran. Original evidence:
[[wiki/work/dbt-compaction-coordination/verification#Maintainer completion review — Mac provisioning blocked]].

Human selected the committed worker repair. Pulled PyUtil `fab647f` and Analytics
`6459c74`, rebasing planning as `1051a8c` while preserving both histories. Independent
pre/post-run checks confirm all 22 exact manifest identities and both locked native
runtimes; 18 harness controls pass. The unchanged corrected Mac baseline finishes
with **169 main passed/129 reviewed Linux-only skips** and **267 standalone
passed/zero skipped**, both exit 0 without timeout. Full versions, timings and skip
boundaries: [[wiki/work/dbt-compaction-coordination/verification#Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed]].
Mac reader shutdown, producer service/client/advisory exports/audited recovery and
S3/resource qualification remain open. No utility gate is accepted by these tests.

No utility code, new app tests, deployment or assistant push; the 27-test historical
raw-viewer baseline and all utility acceptance gates retain their original scope.

**Finalization:** the human authorizes committing/pushing the planning and review
documentation, not utility implementation or deployment. Remaining producer gates
return to the worker through
[[wiki/work/dbt-compaction-coordination/dev_handoff#Worker continuation after the Mac review]].

## Source/manual checks — original planning baseline

- Read HostActivity main, source discovery, filename metadata, query projection,
  README, dependency pin and offline tests; canonical/original dashboard artifacts.
- Read the current coordination ledger/protocol/tick, root macros and entity
  consumer contract; physical partition/inventory, processing metrics and immutable
  phase-evidence sources. Main/app DuckDB pin matches at 1.5.6.
- Confirmed `Ledger.open` invokes unresolved-writer blocking, so ordinary open is
  unsuitable for side-effect-free status. Current run states are `INTENT`/`BLOCKED`.
- Confirmed coverage is fixed-hour/replay-overwritable and independent phase
  archives preserve order without a uniform measured phase timestamp.
- Original planning used inspected PyUtil `fe7fcb5`; newer producer review and
  repaired Mac results are recorded above. Existing coordination gates remain in
  [[wiki/work/dbt-compaction-coordination/verification]].

## Pending acceptance matrix

| Gate | Required proof | Status |
|---|---|---|
| Inspection during write | Held process lock, S3 outage and waiting coordinated job still render status/history without opening ledger or reserving data access. | Not run |
| Live overlap and warning | Live diagnostics can observe writing/blocked state without messages/reservations; visible warning survives fresh `OPEN`, stale/unknown status and cached/exported results. | Not run |
| Live races | Disappearance/replacement between LIST/schema/rows and mixed snapshot/authority/checkpoint generations stay inconclusive, never false zero/corruption/deletion/migration failure. | Not run |
| Read-only status | No init/recovery mutation; malformed/stale/binding/version failures show unknown; free lock cannot clear blocked intent. | Not run |
| Catalog scope | Resumable survey, new families/protocols, pagination and unknown inventory; no truncated all-partition completion claim. | Not run |
| Evidence independence | Replay `completed`/raw `not_run`, skipped destinations, failed deletion and missing checkpoint cannot become verified migration success. | Not run |
| Timeline | Data hour versus execution time, missing times, linked repairs and committed disposition; exit zero is not success. | Not run |
| Event compatibility | Raw/compacted/both exact counts/timestamp equivalence, physical overlap warnings and raw filename-only metadata; existing budgets retained. | Not run |
| Entity context | Disabled mode, expected-host/namespace/authority failures, valid historical coverage and bounded retained-instance inspection without added event rows; live checks remain observational even when they pass. | Not run |
| Mode separation | Explicit coordinated mode cannot read before grant or silently fall back; mode switches/cached mixed-page catalogs cannot upgrade live results to coordinated. | Not run |
| Job lifetime | Both modes stop/reap reading children on interruption/browser loss. Coordinated cancellation/late grant and pending releases retain ownership until shutdown; live jobs create no coordination state. | Not run |
| Same-server interaction | Writer priority and no coordinated reader/writer overlap with researchers/status polling; intentional live overlap remains bounded and cannot publish authoritative evidence. | Not run |
| Operational cost | Status/inventory freshness, live contention, coordinated reservation/drain latency, CPU/RSS/temp use, accumulated catalog/entity budgets on the intended server. | Not run |

## Known gaps and follow-ups

No status/export/client API is assumed implemented by this draft. Agree the
consumer/producer contract now; coordinated refresh needs the qualified client,
while authoritative run history needs an export of the implemented local committed
completion disposition. Then record
actual commands, before/after failures, test results, identity/privacy
checks and isolated pilot limits here. Use synthetic labels in committed evidence;
do not persist private host/account/network values or raw diagnostic payloads.

Plan: [[wiki/work/compaction-status-utility/implementation_plan]]. Requirements:
[[wiki/work/compaction-status-utility/brief]].
