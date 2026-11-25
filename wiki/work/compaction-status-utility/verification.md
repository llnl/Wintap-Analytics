---
title: "Verification: Compaction Status Utility"
type: concept
confidence: medium
grounded_by:
  - streamlit/projects/HostActivity/tests/contract/test_host_activity.py
  - streamlit/projects/HostActivity/pyproject.toml
  - streamlit/projects/HostActivity/status_source.py
  - streamlit/projects/HostActivity/status_views.py
  - streamlit/projects/HostActivity/tests/contract/test_status_source.py
  - streamlit/projects/HostActivity/partition_status.py
  - streamlit/projects/HostActivity/tests/contract/test_partition_status.py
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - wiki/work/compaction-status-utility/implementation_plan.md
policy: agent-editable
last_validated: 2026-11-17
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/HostActivity; ../Wintap-PyUtil/wintappy/coordination
tags: [feature-work, status, compaction, verification, streamlit]
---

# Verification: Compaction Status Utility

**Test-location update, November 22:** current HostActivity modules live under
`tests/contract/`; named discovery now uses `tests.contract.test_status_source`.
Historical commands/results below are preserved. The new 59-case mechanical-move
check is recorded separately in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].

### Scoped partition-presence overview — November 17, 2026

Implemented the first bounded Partitions diagnostic in HostActivity. It discovers
the event-family union from `raw_sensor/` and `compacted/`, checks hourly prefixes
with delimiter-scoped S3 metadata listings, and renders a 42-complete-day
heatmap. The metric is compacted-present hours divided by 24; raw-only hours are
zero, overlap is counted as compacted but reported, and no-data cells are blank.
The implementation never reads Parquet objects and retains the Live diagnostic
warning.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/partition_status.py; streamlit/projects/HostActivity/main.py -->

From `streamlit/projects/HostActivity/`:

```sh
uv run python -m unittest discover -s . -p 'test_*.py'
```

Result: **59 tests passed**. The new synthetic partition tests cover event-family
union, raw-only/compacted-only presence, overlap, blank cells, and the full-day
denominator. Live S3 latency and deployed endpoint compatibility remain
unverified.

## Authorized advisory implementation — November 15

The human authorized Analytics implementation plus scoped native-Mac PyUtil work
in isolated worktrees from Analytics `ee9c27a` and PyUtil `123b9d3`. The busy
producer checkout/environments remain untouched; producer interrupted-publication
recovery remains worker-owned. This pass authorizes neither deployment/scheduling
nor real-dataset mutation, commit or push. The November 14 planning/publication
authorization below is historical, not the current implementation boundary.
<!-- SOURCE: Human implementation approval, conversation 2026-11-15. -->

### Commands and retained results

App provisioning: `uv sync --locked --offline --python 3.12` first refused the
uncached `pandas==2.3.3` Mac wheel. `uv sync --locked --python 3.12` then succeeded
without changing manifest/lock. Python is 3.12.12, DuckDB 1.5.6. No dependency or
query-runtime repair was made.

From `streamlit/projects/HostActivity/`:

```sh
.venv/bin/python -m unittest discover -s . -p 'test_*.py' -v
.venv/bin/python -m unittest test_status_source -v
```

| Evidence | Result and attribution |
|---|---|
| Untouched app baseline | 27 passes in 12.763 s, before source edits. |
| First new source-test import | `ModuleNotFoundError: status_source`, before implementation. |
| `utility-first.stderr.txt` / `.json` | 45 passes/one AppTest selector error in 1.062 s; adding View moved Event family to index 1. All ten source/lock identities match before/after. Three remaining selectors corrected; runtime unchanged. |
| `utility-green.stderr.txt` / `.json` | **46 passes/zero skips in 1.546 s**, exit 0; all ten app source/lock identities match before/after. Only non-failing existing Streamlit bare-mode/width warnings. |
| `status-real-producer-contract.json` | Separate dashboard-runtime process reads a real `service.export_status` v1 export while the synthetic producer ledger lock remains held; one waiting job observed, exit 0, all fixture files unchanged. Catalog and delivery remain `null`. |

The first combined failure's private reports were accidentally retained in the
approved temporary parent evidence directory rather than the isolated worktree
parent's `evidence/`; both original and final reports remain retained, not replaced.
The real-export harness initially misused `Ledger.initialize` as a context manager;
corrected initialization followed by `Ledger.open` required no producer code repair.

Report SHA-256 (`utility-green.stderr.txt`):
`9f23312a6ee5399cc9a98208c99ff230ae048cf44fc430655e68704bb9314ec5`.
Contract report SHA-256:
`5522cc4ce6914d42a103aa069a9c8125608d294236b9b624b15cb4921a259562`.
Raw logs/fixture paths stay private; source is cited in place, not copied to `raw/`.

### Qualified subset and limits

Controls exercise mandatory full-binding/ledger pins, missing configuration/no I/O,
wrong identity/version, unknown fields, duplicate/nonfinite/partial JSON, bounded
regular-file reads, FIFO/final-symlink/database-path refusal, timestamps/future/rollback/
staleness, page order/duplicates/continuation and redaction. Binding/version bypass
mutations prove the specific checks cause refusal. Actual Streamlit controls cover
manual-only refresh, cached navigation, no SDK/data connection, unavailable failure
hiding old results, changed pins clearing cache and always-visible Live warnings.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/tests/contract/test_status_source.py; streamlit/projects/HostActivity/tests/contract/test_host_activity.py -->

This qualifies advisory consumer behavior, not producer truth/authenticity or a
consistent dataset. Same-session timestamp checks are not a monotonic sequence or
whole-session rollback defense. V1 has no catalog, entity dispositions, delivery,
launch/finish, progress or completion certificates. Runs is bounded raw intent
markers only; `COMPLETED` is reported, never certified. The Partitions heatmap is
metadata-only availability evidence, not a catalog or completion certificate.
Ordinary raw Activity stays synchronous: no managed jobs, compacted/entity reads,
coordinated refresh or same-server slow-writer/resource pilot has run.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/status_source.py; streamlit/projects/HostActivity/status_views.py; ../Wintap-PyUtil/wintappy/coordination/service.py §status_page -->

Native and producer independent review results:
[[wiki/work/dbt-compaction-coordination/verification#Independent submitted review and native-Mac feasibility — November 15]].

### Final scoped audit and style successor — November 15

The first complete tracked/untracked audit finds no new grounding, link, section,
newline, whitespace or privacy errors. Three historical Python 3.11 installed-package
citations in producer verification are unavailable in this isolated Python 3.12
environment; they remain historical evidence, not newly verified live sources.
Index/log retain their existing frontmatter exceptions; this is not whole-wiki lint.

Ruff 0.16.10's broad six-file check first reports 14 findings; six concern the new
files and eight reproduce existing main/test findings. A four-new-file format
check also requests two test context-manager wraps. Retained `source-audit-before-polish.json`
and an 11-file private source snapshot preserve the original green source/locks.
The successor changes only new-file import order, explicit default `check=False`,
test callback binding and context-manager formatting; producer runtime, existing
main/tests, queries and all manifests/locks stay unchanged.

Distinct successor command from the app:

```sh
.venv/bin/python -B -m unittest discover -s . -p 'test_*.py' -v
```

`utility-style.stderr.txt` / `.json` passes **46 tests/zero
skips in 1.580 s**, exit 0. Full 76-line stderr/empty stdout reviewed; all ten
successor source/lock identities match before/after/current files. Original failures
remain retained with unchanged report hashes and their recorded before/after
identities; the earlier 1.546-second green source authenticates against the retained
pre-polish snapshot. Successor stderr SHA-256:
`0f5d810c816fa75bec6d9a1dd3e518de31af725ab55aa52f0965423c3a22378d`.

`source-audit-polished.json` retains default Ruff lint/100-column format passes for
all four new Python files and `--select E4,E7,E9,F` passes for all six changed Python
files. Broad six-file lint still reports eight baseline findings (imports,
intentional naive-time tests, argument shadowing and sanitized broad exceptions),
with no new finding; it is not represented as a full lint pass. Complete cosmetic
delta reviewed in `source-polish-review.diff`; all six identities stay unchanged
during checks. Native synthetic successor evidence remains feasibility only, below
the same producer verification heading linked above.

Audit command from Analytics, using the already locked producer PyYAML 6.0.3:

```sh
../Wintap-PyUtil/.venv/bin/python -B ../evidence/dcc-final-scope-audit.py \
  --output ../evidence/dcc-final-scope-audit-final.json
```

The app has no PyYAML; the initial tooling import refusal required no dependency
or environment change. `dcc-final-scope-audit-final.json` exits 0 and covers all
**23 changed files/five untracked additions**, **15 wiki pages/13 frontmatters**,
**327 grounding paths/546 inline source paths**, **490 wikilinks/92 sections**,
five local Markdown links, six Python syntax checks, 38 added Python section
references and three linked diagrams. No new errors or added-content privacy
candidates; complete retained diff reviewed and both repositories' fresh
`git diff --check` pass. This is scoped review, not whole-wiki or broad-lint acceptance.

All 365 submitted-archive sources, 83 producer identities, ten utility and three
native successor identities, the 11-file prior green snapshot and retained runner
reauthenticate. All 21 report hashes from the first audit remain unchanged;
cosmetic/full retained diff hashes and six polished source identities also match.
The same audit with fresh output `../evidence/dcc-final-scope-audit-final-recorded.json`
checks this result-recording update separately; prior reports refuse overwrite.
No new runtime/platform or operational gate is accepted.

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
qualification. Changes were uncommitted/unpushed at this historical checkpoint;
use current feature tips rather than this old publication status.

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
| Inspection during write | Held process lock, S3 outage and waiting coordinated job still render status/history without opening ledger or reserving data access. | Synthetic held-lock export read and no-SDK AppTests pass; actual slow-writer/waiting data-job pilot not run |
| Live overlap and warning | Live diagnostics can observe writing/blocked state without messages/reservations; visible warning survives fresh `OPEN`, stale/unknown status and cached/exported results. | Not run |
| Live races | Disappearance/replacement between LIST/schema/rows and mixed snapshot/authority/checkpoint generations stay inconclusive, never false zero/corruption/deletion/migration failure. | Not run |
| Read-only status | No init/recovery mutation; malformed/stale/binding/version failures show unknown; free lock cannot clear blocked intent. | Advisory v1 consumer negatives pass; no lock probe/exporter/recovery path added |
| Catalog scope | Resumable survey, new families/protocols, pagination and unknown inventory; no truncated all-partition completion claim. | Not run |
| Evidence independence | Replay `completed`/raw `not_run`, skipped destinations, failed deletion and missing checkpoint cannot become verified migration success. | Not run |
| Timeline | Data hour versus execution time, missing times, linked repairs and committed disposition; exit zero is not success. | Raw intent markers/missing launch-finish and reported-only completion controls pass; full timeline/certificates pending |
| Event compatibility | Raw/compacted/both exact counts/timestamp equivalence, physical overlap warnings and raw filename-only metadata; existing budgets retained. | Not run |
| Entity context | Disabled mode, expected-host/namespace/authority failures, valid historical coverage and bounded retained-instance inspection without added event rows; live checks remain observational even when they pass. | Not run |
| Mode separation | Explicit coordinated mode cannot read before grant or silently fall back; mode switches/cached mixed-page catalogs cannot upgrade live results to coordinated. | Not run |
| Job lifetime | Both modes stop/reap reading children on interruption/browser loss. Coordinated cancellation/late grant and pending releases retain ownership until shutdown; live jobs create no coordination state. | Not run |
| Same-server interaction | Writer priority and no coordinated reader/writer overlap with researchers/status polling; intentional live overlap remains bounded and cannot publish authoritative evidence. | Not run |
| Operational cost | Status/inventory freshness, live contention, coordinated reservation/drain latency, CPU/RSS/temp use, accumulated catalog/entity budgets on the intended server. | Not run |

## Known gaps and follow-ups

Submitted Linux status/client interfaces exist; the current app consumes only
advisory v1. Agree additional catalog/history/progress interfaces; coordinated
refresh needs qualified managed app/client lifetime, while authoritative timeline
success needs a producer completion-certificate export. Continue recording
actual commands, before/after failures, test results, identity/privacy
checks and isolated pilot limits here. Use synthetic labels in committed evidence;
do not persist private host/account/network values or raw diagnostic payloads.

Plan: [[wiki/work/compaction-status-utility/implementation_plan]]. Requirements:
[[wiki/work/compaction-status-utility/brief]].
