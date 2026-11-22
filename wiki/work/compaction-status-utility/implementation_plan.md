---
title: "Implementation Plan: Compaction Status Utility"
type: concept
confidence: speculative
grounded_by:
  - wiki/work/compaction-status-utility/brief.md
  - wiki/work/compaction-status-utility/design.md
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - streamlit/projects/HostActivity/test_host_activity.py
  - streamlit/projects/HostActivity/partition_status.py
  - streamlit/projects/HostActivity/status_source.py
  - streamlit/projects/HostActivity/status_views.py
  - ../Wintap-PyUtil/wintappy/coordination/service.py
policy: agent-editable
last_validated: 2026-11-17
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: developer
status: draft
source_paths: streamlit/projects/HostActivity; ../Wintap-PyUtil/wintappy/coordination
tags: [feature-work, status, streamlit, compaction, implementation-plan]
---

# Implementation Plan: Compaction Status Utility

## Scope and dependency gate

The human authorized this implementation/review plan, including scoped native-Mac
PyUtil source/test work, on November 15. Work is isolated from the busy producer
checkout; interrupted-publication recovery remains with that worker. No deployment,
cron installation, real-dataset mutation, commit or push is authorized. Actual S3
and resource qualification still need specifically approved fixtures/roots/access.
<!-- SOURCE: Human implementation approval, conversation 2026-11-15. -->

Submitted PyUtil `123b9d3` implements Linux service/client and local advisory v1
status. The implemented utility subset uses only that supported export, not the
live ledger. Navigation, pinned bounded status, raw intent markers and explicit
unavailable inventory pass 46 offline controls plus a separate real-export read
with the synthetic producer lock held. This is not full csu-01/02 acceptance.

Initial `fe7fcb5`, `8ee714c` and repaired `fab647f` baseline reviews retain their
historical scope. Mac reader shutdown remains unqualified: the new native sandbox/
tracker-bootstrap experiment is feasibility-only, not selected for production.
Live diagnostic extension must still qualify root binding, races and supervised
bounded jobs. Coordinated refresh waits for qualified app/client lifetime;
authoritative timeline success needs producer certificate/disposition exports.
Existing R6–R8 follow-through and dcc-02–05 gates remain owned by
[[wiki/work/dbt-compaction-coordination/implementation_plan]]. Do not check those
off because a dashboard mock renders successfully.

## Steps

### csu-01 — Agree and qualify inspection contracts

- Confirm first-version scope, windows, freshness, catalog coverage and deployment
  permissions with the human/worker.
- Record the approved default live/optional coordinated modes in the coordination
  contract; agree mode-specific permissions, warnings and observational-result labels.
- Specify versioned local status, bounded run-summary pages and advisory catalog
  export, including binding/ledger identity, observation times and unknown states.
- Agree producer publication at committed transitions and writer launch/disposition;
  any live progress must come from the lock-owning producer, not a second DB process.
- Qualify optional existing-inode lock probe and any side-effect-free locked
  exporter. Ordinary `Ledger.open` is not the inspection implementation.
- Test corruption, partial publication, wrong binding/version, stale data, restart,
  free lock with unresolved intent and busy lock with reported `OPEN`.

### csu-02 — Status and simple timeline UI

- Extend the existing app with Status, Partitions, Runs and Activity navigation.
- Render Status and cached Runs solely from advisory inspection exports; display
  lock observation, reported mode, reservation/delivery distinction and block reason.
- Add deterministic paginated run bars/markers and a bounded redacted detail view.
  Require committed disposition for success; preserve missing times and unresolved
  runs. Keep data hours separate from execution times and phase order from duration.
- Make status refresh independent of active/waiting data jobs. No recovery controls.

### csu-03 — Partition catalog and selected surveys

- Build bounded/resumable catalog import from producer inventories and original
  run summaries; retain event/hour/protocol grain and separate evidence axes.
- Add explicit initial/history metadata survey and selected reconciliation through
  managed short jobs, live by default or explicitly coordinated. Persist advisory
  continuation and per-page mode/time without holding a grant across pages; expose
  scope/watermarks, mixed-time observations and unobserved/partial inventory.
- Support all-known-partition rollups plus UTC/family/protocol/state filters and
  paginated detail. Catalog unknown scope stays visible until the agreed survey finishes.
- Surface raw/compacted co-presence, skipped destinations, late raw arrivals,
  coverage gaps, scheduler backlog and recorded storage-reduction statistics.

### csu-04 — Live/coordinated activity and optional entities

- Add default live diagnostic jobs with no reservations/messages, mandatory warnings
  and correctly configured root binding. Preserve unknown/stale writer status and
  inconclusive disappearing-object/schema/entity-generation failures; do not turn
  failed/partial reads into zero activity, corruption or migration failure.
- For explicit coordinated jobs, reuse the qualified shared-command client and bind
  complete active roots before all data LIST/GET/schema/row/coverage work. Failure or
  missing client remains visible in coordinated mode; never silently fall back.
- Add raw/compacted/both source selection with provenance-aware exact aggregates;
  preserve timestamp contracts, raw filename metadata and 12-hour/resource limits.
- Add optional qualified entity summary and bounded recorded-instance lookup;
  do not add entity rows to activity or label observed lifecycle as running. Passing
  live validation stays observational; conflicting mixed generations are inconclusive.
- Use managed per-refresh jobs with bounded result transfer and one active data job
  per server across modes. Prove interruption, browser loss/reload and child cleanup
  in both modes; prove cancellation/late grant and release retry for coordinated jobs.
  Keep mode/time/warnings attached to cached/exported results across mode switches.
  Cached chart rendering and local status polling hold no data reservation.

### csu-05 — Isolated same-server qualification and closeout

- Run the existing offline suite, new semantic/model tests and Streamlit AppTest.
- Exercise a slow writer with status polling, two existing researchers and a
  coordinated dashboard reader waiting for admission. Verify no coordinated data
  reading before grant or writer overlap, and writer priority at grace. Separately
  prove live diagnostics can read during writing/blocked state without a reservation,
  with warnings and bounded impact; they cannot publish authoritative evidence.
- Inject disappearance/replacement between LIST/schema/row reads and mixed entity/
  authority/checkpoint generations. Require inconclusive results and retained warning
  even with stale/unknown or fresh `OPEN` status; never false zero/corruption/success.
- Test raw-only, compacted-only, retained-source overlap, entities disabled/enabled,
  skipped/partial migration, failed checkpoint after deletion, replay and linked repair.
- Measure same-server status latency, catalog paging, live query/writer contention,
  coordinated reservation duration, writer drain delay, CPU/RSS/temp use and large
  retained-entity validation costs.
  Use fresh isolated fixtures; real-data mutation/production enablement needs separate approval.
- Record commands/results and limits; obtain human acceptance, then promote only
  durable implemented behavior into canonical dashboard/ETL/entity documentation.

## Files likely to change after authorization

- Analytics: `streamlit/projects/HostActivity/main.py`, `s3_source.py`, `queries.py`,
  `file_metadata.py`, focused tests and README; proposed status/catalog/run adapters,
  managed query runner and view modules. Update dependencies only if required.
- PyUtil: native-Mac probe/backend/client work and supporting documentation are
  authorized in the isolated worktree. Producer recovery remains worker-owned;
  additional status/catalog schema work requires interface agreement, not concurrent
  edits to the worker's checkout.
- Wiki: feature verification/checklist/log, canonical dashboard and implemented
  cross-repo data-flow/entity usage where semantics actually change.

## Tests to add or update

Use the criteria in the brief plus independent negative controls: disable/bypass
the specific validation being tested and prove the relevant negatives fail. Avoid
authority rejection masking row validation or UI formatting masking lifecycle bugs.
Portable model/UI tests run on macOS and Linux; genuinely Linux process-supervision
tests need explicit guards with Linux qualification retained.

## Migration, compatibility and rollback

No event/entity interchange migration. Advisory cache/export version changes fail
visibly and can be rebuilt; they never recreate/prune the ledger or phase history.
Preserve standalone read-only raw viewing and the explicit diagnostic exception
for coordinated deployments. Never silently downgrade coordinated jobs or remove
live warnings through UI rollback; stop the app if the selected mode's contract
cannot be preserved. The exception cannot widen to DBT or authoritative verification.
Preserve local-only DBT and optional compaction/entities throughout.

## Done checklist

- [x] Ground the follow-on draft in live HostActivity and coordination/evidence sources.
- [x] Separate human requirements from proposed defaults and worker dependencies.
- [x] Re-run existing offline HostActivity baseline: 27 tests pass.
- [x] Human approves default live diagnostics, optional coordinated refresh and the
  explicit diagnostic exception while retaining DBT/ledger/maintenance protection.
- [x] Refresh producer dependencies after `8ee714c` source review; distinguish local
  completion/history from pending exports/client and the separately scoped Mac baseline.
- [x] Record `fab647f` handoff repair and passing actual-Mac offline baseline without
  accepting skipped Linux paths, Mac reader shutdown or utility producer interfaces.
- [x] Human authorizes the implementation/review scope, including isolated Analytics
  utility and scoped native-Mac PyUtil work; no deployment or commit/push.
- [x] Qualify existing producer v1 advisory shape/pins and bounded consumer negatives;
  real separate-runtime export read passes with synthetic lock held and files unchanged.
- [x] Implement navigation, advisory Status/raw intent Runs and the initial Partitions
  shell; 46 combined offline controls pass with all ten source/lock identities unchanged.
- [x] Add the scoped metadata-only raw/compacted partition-presence heatmap: unioned
  event families, 42 complete UTC-day default, full 24-hour denominator, overlap
  tooltip counts, and no Parquet reads.
- [x] Promote only implemented advisory-subset facts to canonical dashboard/README;
  preserve full catalog/timeline and job-lifetime limitations.
- [x] Audit all tracked/untracked changes, retain original source/report identities
  and qualify the cosmetic successor with 46 offline passes; no broader utility gate.
- [ ] Agree additional csu-01 producer catalog/history/certificate/progress fields.
- [ ] csu-01 inspection/export/lock-probe negative gates pass.
- [ ] csu-02 status/timeline/AppTest gates pass.
- [ ] csu-03 catalog coverage/pagination/evidence-grain gates pass.
- [ ] csu-04 raw/compacted/entity semantics, live warning/race gates and both managed-job lifecycles pass.
- [ ] csu-05 isolated same-server safety/resource qualification passes.
- [ ] Human operational acceptance and canonical promotion; deployment recorded separately.

Evidence: [[wiki/work/compaction-status-utility/verification]].
