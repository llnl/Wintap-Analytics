---
title: "Development end-to-end integration milestone"
type: concept
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/verification.md
  - wiki/work/durable-process-entity-manager/verification.md
  - wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff.md
  - wiki/todo/raw-sensor-upload-time-partition.md
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_writer.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_execution.py
  - ../Wintap-PyUtil/wintappy/coordination/MACOS.md
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql
  - ../Wintap-Analytics/streamlit/projects/HostActivity/s3_source.py
  - ../Wintap-Analytics/streamlit/projects/HostActivity/main.py
  - ../Wintap-Analytics/streamlit/projects/HostActivity/status_views.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py
  - ../Wintap-Analytics/streamlit/projects/SmokeTests/analysis.py
  - ../Wintap-Analytics/streamlit/projects/DataQA
policy: agent-editable
last_validated: 2026-11-17
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: reviewed
source_paths: wiki/work/dbt-compaction-coordination; ../Wintap-PyUtil/wintappy/coordination; ../Wintap-PyUtil/wintap_dbt; ../Wintap-Analytics/streamlit/projects
tags: [feature-work, planning, integration, development-deployment, real-data, linux, macos, dbt, compaction, entity-state, streamlit, source-modes]
---

# Development end-to-end integration milestone

## Direction and scope

**Integration first; production hardening later.** The human clarified that the
entire sensor → raw-data → ETL/analysis environment is a development deployment.
Its existing telemetry is expendable, not a production archive that must be
preserved. The immediate goal is to run compaction, process-entity cache creation
and Linux/native-Mac DBT clients together on actual sensor-generated data, then
prioritize defects by their demonstrated system impact.
<!-- SOURCE: Human planner-role direction and development-data clarification, conversation 2026-11-16. -->

**Plan approved for handoff on November 16.** The human approved DCC-E2E-01's
integration-first plan and requested wiki commit/push; the human will deliver it
to the Linux runner. Approval is of the plan, not a completed milestone or an
already-selected execution/mutation scope. Strict upload-time UTC enforcement
and downstream delayed-data semantics are explicitly separate later work.
<!-- SOURCE: Human plan approval, deferred upload-client contract and Linux handoff publication request, conversation 2026-11-16. -->

Here, **real data** means telemetry produced by running sensors and transported
through the actual deployment, not only generated Parquet/unit fixtures. It does
not mean production-critical data, guaranteed complete history, or permission to
publish host identifiers. Actual workload evidence can be generated deliberately.

This direction supersedes the **ordering** of the November 15 recovery-first
phases in [[wiki/work/dbt-compaction-coordination/implementation_plan#Next phases — PR deferred, qualification sequence]].
Do not require general interrupted-publication/missing-original repair, every
maintenance corner case, historical ancestry completeness, or repeated unchanged
full suites before attempting development integration. Existing evidence and
fail-closed code remain intact; no unexecuted acceptance box becomes checked.

This is a planner/wiki-maintainer record, not an execution authorization. Select
the actual Linux runner, dataset/transport/state roots, access and mutation scope
before executing. Expendable data removes a preservation objective; it is not a
blanket instruction to delete buckets, reset ledgers, stop collectors or change
sibling source. The human authorized this repository's wiki commit/push only;
production rollout, PR work and persistent scheduler installation remain outside scope.

## Current execution status — 2026-11-17

The earlier Linux live qualification reached 07:00Z after ten independently
verified deletion-enabled hourly ticks. A separate fresh writer ledger later
advanced 31 bounded hourly cursor steps from 2026-10-26 19:00Z to 2026-10-28
02:00Z, including a verified non-empty migration/deletion, empty-hour advancement
and audited recovery of one interrupted verifier. A separate future-cursor,
non-entity Linux reader then completed a one-hour DBT build with **140/140**
resources complete and a readable local DuckDB output. The broader DBT attempt
that exhausted local disk remains a failure record. These results do not satisfy
the complete milestone checklist by themselves.

The current execution tranche is intentionally **Linux-only**. It uses the existing
real S3 `raw_sensor` source, processes the oldest available date forward in small
bounded chunks, and may delete completed source data because this is explicitly
test/development data. The server owns compaction, coordinator, ledger and the Linux
DBT client; Mac DBT, separate Mac output and reader/writer overlap are deferred and
are not blockers for this tranche. Resource ceilings remain secondary to obtaining a
robust end-to-end run, while stop and integrity checks remain mandatory.
<!-- SOURCE: Human scope clarification to use existing S3 test data, allow deletion, run server processes and Linux DBT, and defer Mac DBT, conversation 2026-11-17. -->

## Reviewed position — November 16

Local PyUtil is `badb67f2f4d767ea28f17459ff75422a0506f493` on
`work/raw-sensor-compacted-union`; tracked source is clean. Analytics is `2826c0f`
on `work/raw-sensor-file-aggregation`, with pre-existing uncommitted Mac verification
updates preserved. Private untracked PyUtil environment files were not read or changed.

| Area | Evidence already available | What the milestone still needs |
|---|---|---|
| Linux coordinator/hourly writer | Service CLI, terminal-first ingestion, exclusive writer, independent completion, cursor/backlog transitions and actual compactor launch exist. Current worker-recorded Linux regressions: affected 341/12 skips; full main 1521/15; full standalone 695/2 using tmpfs. | Operate this revision against actual S3 and sensor payloads, not just synthetic/local controls. |
| Linux entity cache | Separate `entities-init`/`entities-replay`, explicit ledger-v5 opt-in, typed completion/high-water/history and clean-original resolution exist; earlier strict service focus passed 71, affected 307. | Fresh coordinated bootstrap followed by ordinary entity-enabled hourly compaction on the same dataset. |
| Linux DBT client | Make routing, request/grant/preflight/build/release, terminal retries and Linux descendant shutdown exist. | Actual S3 builds concurrent with a native-Mac reader and a due writer. |
| Native-Mac DBT client | Reader-only `run_reader_supervised`; November 16 actual-Mac lifecycle 12/12 and six-module suite 67 passed/116 declared Linux-only skips. | Genuine Make/client subprocess preflight/build, actual S3, completion/release and local DuckDB output. The in-process restriction probe is not this path. |
| Real-data component experience | Earlier three-day runs compacted 151,733,675 rows; SQL bootstrap verified 2,613,678 entities; entity-enabled DBT passed 146 resources, twice. | These separate historical runs used larger resources and do not establish current coordinated Linux/Mac integration or the proposed resource envelope. |
| Sensor/upload deployment | Prior package/canary records show actual process/file/network data reaching S3, with known provenance and attribution gaps. | Identify current deployed versions and observe a fresh named workload through delivery and analysis; old host reports are not today's health check. |

Evidence and limitations: [[wiki/work/dbt-compaction-coordination/verification#Authorized reader-scope dispatch repair — Linux regression results]],
[[wiki/work/dbt-compaction-coordination/verification#Native macOS reader-scope requalification — 2026-11-16]],
[[wiki/work/durable-process-entity-manager/verification#Repeat three-day round — completed, 2026-11-13]],
[[wiki/work/wintap-telemetry-identity-and-data-quality/dev_handoff]]. Linux reports
were reviewed here, not re-executed on the Mac during this planning pass.

The live service already wires `execute_and_complete_prepared` and the separate
entity writer; these are **integration qualification gaps**, not a missing entire
implementation. Entity init requires an explicit upgrade to v5 and separate
`entity_writer` settings. Successful entity-only completion leaves the raw cursor
unchanged and admission `DRAINING`; ordinary ticks must finish eligible raw hours
before reader admission resumes.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/service.py §validate_config/service_tick/main; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py §execute_entity_and_complete_prepared; ../Wintap-PyUtil/tests/test_coordination_entity_service.py §test_genuine_entity_service_completion_keeps_raw_cursor_and_queued_reader -->

## Milestone DCC-E2E-01 — working development pipeline

**Approved completion target:** an operator can start from a clean development
scope, collect/upload actual host activity, build and verify process entities,
compact eligible hours, and run Linux and native-Mac DBT clients through the same
coordinator, producing usable local analysis databases. The flow repeats over
successive hours without bypassing coordination or needing invented success.

The pilot initially targets approximately two recent settled hours and a small
explicit host set. Completion includes **at least three successive eligible hour
migrations in total** on the same development scope; verified pilot migrations count.
The sequence must include newly collected activity beyond bootstrap and an actual
UTC eligibility boundary. A four-to-six-hour development soak is a useful
follow-on, not a prerequisite for the first runnable pilot. The human approved the
plan with the three-migration completion target; approximate pilot sizing and the
optional soak remain operating guidance, not executed qualification evidence.

### Exit checklist

- [ ] Fresh sensor-generated process/file/network stimulus is visible in delivered
  raw data and corresponding analysis; record supported families and genuine skips.
- [ ] Linux creates a fresh entity cache through the service's supported v5 path;
  snapshots, authority and matching hourly checkpoints verify.
- [ ] Entity-enabled hourly ticks publish/update entities, migrate/validate event
  data, delete the approved source hours, verify checkpoints and commit completion
  with exactly one-hour cursor advancement. Include all discovered supported event
  families in the selected scope, not just a process-only showcase.
- [ ] Linux and native Mac each execute actual `make dbt-build` source preflight,
  model/data tests and release against the same S3-backed dataset, writing separate
  local DuckDB outputs. Required failures cannot be relabelled as skips or warnings.
- [ ] At least one run observes both readers reserved together, a due writer
  draining them and a third queued reader admitted only after verified completion
  and backlog clearance. Record reservation and actual workload intervals.
- [ ] On a bounded settled reference window, raw-only and post-migration input
  populations/schemas agree; entity mode preserves window process keys and counts.
  Compare deterministic counters/verdicts, allowing documented enrichment changes
  and previously accepted arbitrary-representative drift, not silent row inflation.
- [ ] Repeat over the successive hours above; an ordinary coordinator restart
  between completed operations resumes from the retained cursor without duplicate
  migration. Native-Mac and Linux release checks keep their respective contracts.
- [ ] Report actual DBT/writer/queue durations, aggregate Linux process-tree RSS and
  local disk/spill usage, and Mac client resource use. Demonstrate the selected
  development-size workload within agreed ceilings; do not claim all-history capacity.
- [ ] Publish concise results, reproduction/configuration references and ranked
  remaining defects; reconcile the frozen completion candidate's affected/full
  Linux suites and actual-Mac supported tests once after repairs stabilize.

The milestone does **not** require 100% ancestry/root reachability from a short
bootstrap, flawless upstream attribution, universal crash repair, production-scale
retention, physical-power-loss proof or hostile/detached-descendant containment.
Known defects remain visible; if they make selected data unusable or violate the
exit checks, they are milestone blockers rather than automatically waived.

## Execution order after concrete scope approval

### M0 — Select and bring up the development scope

Use one Linux coordinator/writer, one Linux DBT client and this actual Mac client.
PyUtil owns runtime/harness changes; Wintap owns sensors; Lintap owns packaging;
Analytics owns the integration record and downstream inspection tools.

Retain a small private manifest: source revisions, deployed collector versions,
selected hosts/event families/window, endpoint/profile references, exact raw/
compacted/entity/checkpoint/transport roots and separate local ledger/archive/
spill/client/output locations. Record only anonymized summaries in the wiki.
Do not copy credentials or raw rows into this plan.

Use separate locked main DuckDB 1.5.6 and standalone 2.0.0 environments. Select
budgets with headroom within the prior Linux **32 GB RAM / 64 GB local-disk**
planning envelope, and explicit Mac limits. The shipped 1 GB example settings and
the historical 128 GB/256 GB bootstrap are neither accepted pilot capacities nor
reasons to silently change limits. Start with bounded real data, measure and adjust
only the agreed development scope/budgets.

Reuse the reviewed Linux regression and Mac lifecycle evidence at historical
baseline `badb67f` where applicable, but run the current candidate's relevant
controls. The active candidate is PyUtil `402ead1`, which includes the cumulative
observed-host DBT/entity correction. Do not repeat unchanged multi-hour full suites
before the first data run. A changed candidate needs the relevant regression
controls, not unconditional acceptance.
Drive real service ticks manually or through a bounded development runner at the
normal minute cadence; retain ten-second client polling. Do not install production
cron or replace the service with a mocked clock/permission callback.

### M1 — Actual delivery and a small reference window

Use [[wiki/tool/named-telemetry-smoke-workload]] or the existing canary runner to
generate identifiable process/file/network activity on an approved collection
host. Observe the existing uploader deliver both telemetry and workload evidence.
Select recent closed partitions after grace and confirm delivery has settled for
the bounded comparison; grace alone is not upload-quiescence proof.

A copied actual-data slice in a fresh development prefix is a useful first
processing pilot. Label it **real-payload replay**: copying alone does not prove
the live collector-to-analysis integration required by M4. Retain only the small
reference slice/inventory and outputs needed for comparison, not a mandatory
backup of the entire existing development deployment.

Run a supported raw-only baseline, initially entity-disabled, and record schema,
per-family partition/row totals and key/counter summaries. Any S3-reading baseline
must use a reader grant or externally established zero-client/writer exclusion;
do not bypass coordination through direct DBT during an active service run.

### M2 — Cache creation and hourly compaction through the actual service

Initialize a fresh ledger with matching entity-enabled binding, explicitly upgrade
to v5, then use service `entities-init` with separate `entity_writer` configuration
and the bounded real-data window. The existing quarantine policy may be selected
explicitly with its matching DBT policy/0.05 ceiling; do not silently filter identity
failures or alter the ceiling to obtain a pass.

Start the raw cursor at the oldest recent hour actually selected for migration,
not at the start of a multiweek archive. Bootstrap does not advance it. Run ordinary
entity-enabled ticks to verify raw migration/deletion/checkpoints and catch up until
the next hour is not yet due. Reader admission follows the service's real backlog
rule; do not force `OPEN` to bypass `DRAINING`. Avoid simultaneous raw and compacted
copies in the reference scan: DBT uses `UNION ALL`, not deduplication.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/service.py §service_tick/main; ../Wintap-PyUtil/wintappy/coordination/client.py §_dbt_commands/main; ../Wintap-PyUtil/Makefile §dbt-build; wiki/workflow/wintap-etl-data-flow.md §Read the flow -->

### M3 — Both actual clients, then contested writer admission

First run Linux and Mac sequentially on the same covered window to isolate data/
configuration/platform failures. Use Make → client → subprocess DBT on the Mac,
not the earlier in-process feasibility probe. Compare their selected populations,
schemas and deterministic results; output databases and retry state stay local and
separate. Also check ordinary local-only DBT remains direct.

Then start both real DBT readers so their reservations overlap, allow the next
hour to become due, and submit a third reader while draining. Observe actual
request/grant/release transport, writer exclusion and post-COMMIT admission. Small
builds may require deliberate start timing or a declared bounded reader hold after
the genuine build; report that hold separately, never as DBT runtime or a simulated
successful build. A finite catch-up backlog must clear before asserting starvation.

### M4 — Continue live collection and repeat

Follow newly uploaded activity through the same deployment until the three-migration
total and live-delivery checks above are met. Exercise one ordinary restart between
completed ticks; reuse existing reader-interruption evidence unless actual client
execution exposes a problem. Inspect returned failures rather than launching a
general fault-injection campaign. Rank actual delivery, cache, compaction, DBT and
resource problems as they occur. A passing replay alone cannot check the live-delivery
exit item.

**Separate later task: strict upload-time UTC partitioning.** The human intends to
review and enforce that upload clients write only into the UTC day/hour bucket
current at upload time, including delayed uploads/retries. This is intended to
simplify initial delayed-data handling; downstream delayed-event implications are
also later work. Do not add uploader implementation, lookback/recompaction design
or comprehensive late-arrival testing as prerequisites to DCC-E2E-01.
<!-- SOURCE: Human deferred strict UTC upload-client contract and downstream-work clarification, conversation 2026-11-16. -->

Current uploader compliance is not yet established: merge-time partitions are
preserved on retry, uploads are not fenced by the coordinator, existing destinations
skip, and raw/compacted reads union both roots. Record concrete processed-hour
arrivals or data discrepancies if observed during ordinary integration, and triage
actual unusable output under the normal rules; do not claim that the future contract
or ten-minute grace already resolves current behavior. Follow
[[wiki/todo/raw-sensor-upload-time-partition]] for the separate contract review.
<!-- GROUND_TRUTH: wiki/todo/raw-sensor-upload-time-partition.md §Finding; wiki/tool/raw-sensor-compaction.md §Existence is not verified completion; ../Wintap-PyUtil/wintappy/coordination/service.py §service_tick -->

### M5 — Close a finite milestone

Freeze the final candidate after integration repairs, run affected regressions and
the final platform/runtime suites once, and inspect their complete results. If the
candidate remains `402ead1`, authenticate and reuse its already completed relevant
suites rather than demanding identical repeats. Add new integration reports to
[[wiki/work/dbt-compaction-coordination/verification]], with declared window,
families, limits, elapsed phases and defect dispositions.

Accept **DCC-E2E-01** only when its checklist is demonstrated and human-reviewed.
Keep broader dcc-02–05 criteria separately tracked; do not silently equate this
development milestone with universal recovery/resource or production acceptance.

## Downstream integration plan — compacted inputs, entity cache and consumers

The deletion-enabled Linux qualification changes the practical input contract for
downstream readers: a completed hour can have **zero raw objects**, nine or more
compacted event partitions, a committed entity snapshot, and a processing-metrics
receipt. A reader that treats missing raw objects as zero activity will report a
false absence. The following work is the downstream follow-on to DCC-E2E-01. It is
a plan for application changes and verification, not a claim that those changes
have already landed.

### 1. Make source modes explicit

Every reader and report must carry a source mode and a coverage disposition. The
mode is selected deliberately; it is never inferred from whichever root happens to
contain files.

| Mode | Physical inputs | Intended use | Required semantics |
|---|---|---|---|
| `raw-only` | `raw_sensor/<event>` | Producer and delivery evidence; legacy raw viewers | Missing raw is `unavailable`/`unknown`, never zero. No entity enrichment is implied. |
| `compacted-only` | `compacted/<event>` | Post-migration analysis after approved raw deletion | A compacted partition is a transformed delivery product. Label it as compacted and report its processing receipt/coverage. |
| `raw-plus-compacted` | Both roots for a bounded window | Transition and overlap diagnostics | Use only with an explicit overlap policy. Do not `UNION ALL` overlapping copies and call the result a count. |
| `dbt-duckdb` | DBT’s local DuckDB relations built from configured roots | Reusable analytical models | Record the selected roots, window, build revision and test result beside the local output. DBT output is not currently a published `stdview-*` Parquet contract. |
| `entity-aware` | Event roots plus process-entity snapshots, authority and processing metrics | Process context/ancestry analysis | Fail closed when authority, entity snapshots or per-hour metrics are absent, stale, mismatched, duplicated or outside the binding. |
| `authority/status` | Authority and processing-metrics objects only | Advisory coverage/status display | Describes producer processing; it is not a reader grant, completion certificate or recovery permission. |

The transition adapter should attach at least `source_mode`, `physical_root`,
`event_family`, `dayPK`, `hourPK`, `object_count`, `row_count` (when read),
`coverage_status`, and an optional entity `generation_id` to its snapshot. Source
labels must survive aggregation so raw and compacted results cannot be silently
combined. A missing raw partition after a verified delete is `migrated_to_compacted`,
not `empty`; an absent raw partition with no compacted or receipt evidence is
`unknown`.

DBT already routes each event family through both raw and compacted physical roots
and uses `UNION ALL`; this remains correct only when the migration window is
physically disjoint or the consumer applies an explicit overlap rule.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_event_input_paths/raw_sensor_partition_globs -->

### 2. DBT and entity-cache work

The DBT integration slice should preserve the current fail-closed contracts while
making coverage and provenance visible to downstream users:

1. Keep raw/compacted root routing configurable independently of the general output
   dataset root. Test raw-only, compacted-only, and mixed windows with the same
   model selection and explicit `start_day`/`end_day`/hour bounds.
2. Add a source-coverage relation or run artifact that reports, per event family
   and hour, which physical roots were read, object/row totals where available,
   and whether the hour is raw, compacted, mixed, missing, or unknown. Do not
   deduplicate by an unverified filename or `ANY_VALUE`; detect overlap and report
   it as a migration/data-quality condition.
3. Keep entity mode opt-in and validate the complete binding: entity schema and
   metadata, configured namespace/hosts, cumulative observed-host authority with
   the immutable bootstrap set, authority lineage, semantic snapshot hashes,
   processing-metrics schema, one valid metric receipt per required
   `raw_process` hour, status, identity policy and exclusion ceiling.
4. Expose the entity generation and bootstrap/window provenance in the DBT output
   or a companion relation. `process_context` may enrich activity-only keys through
   the entity table, but enrichment must not create new lifecycle observations or
   inflate event counts.
5. Add migration parity checks over a settled reference hour: source row totals,
   per-family totals, distinct process keys, deterministic counters and schemas
   must agree between raw-only and compacted-only reads. Document accepted
   representative/enrichment differences separately from loss or duplication.
6. Keep local DuckDB outputs isolated by source binding and window. A downstream
   export to legacy `stdview-*` Parquet, if needed, is a separate compatibility
   adapter; it must not be assumed merely because DBT built successfully.

The existing DBT authority and metrics macros already reject missing or invalid
authority, stale snapshots, missing/duplicate hourly receipts, bad status and
identity-policy violations. The new tests should assert those failures remain
visible while validating the cumulative observed-host case.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql §validate_entity_authority; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics/validate_process_entities; ../Wintap-PyUtil/wintap_dbt/models/silver/process_context.sql §entity ancestry enrichment -->

### 3. HostActivity Streamlit application

HostActivity should become a read-only, source-aware viewer rather than a raw-only
viewer with a broader glob. Planned changes:

- Extend the settings contract with optional compacted, entity and metrics roots
  (with safe defaults matching DBT), plus an explicit source-mode selector. Keep
  endpoint/profile validation and credential handling unchanged.
- Discover objects separately by physical root and event/day/hour. Preserve the
  root in metadata and row-query paths; never merge two roots into one anonymous
  file list. The file-metadata view should show raw, compacted, mixed and missing
  coverage per hour and explain that S3 object absence is not a zero-row result.
- In row mode, support compacted-only and explicitly bounded raw-plus-compacted
  inspection. Require a visible overlap policy and source label before presenting
  totals. The default transition behavior should prefer a verified compacted
  result for a migrated hour rather than count both copies.
- Add an entity-aware process view that reads the configured entity snapshot and
  displays generation, authority/metrics disposition and enrichment status. It
  must remain advisory: the dashboard cannot grant access, reopen a ledger or
  certify a migration.
- Keep the existing 12-hour and file/row budgets, schema guards, timestamp
  handling, sanitized errors and no-write behavior. A missing authority or
  processing receipt should produce an explicit unavailable/unknown state, not an
  empty chart.
- Update Status/Partitions/Runs wording to distinguish ledger state, processing
  metrics, raw retention and compacted coverage. `COMPLETED` and `DRAINING` remain
  reported observations, not authority to coordinate another job.

The implementation should add tests for raw-only, compacted-only after raw delete,
mixed non-overlapping hours, overlapping raw/compacted objects, missing metrics,
and a cumulative entity authority. The tests must assert that duplicate physical
inputs do not double chart counts and that missing data is never rendered as zero.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/HostActivity/s3_source.py §S3Settings/load_settings/discover_files/discover_object_metadata; ../Wintap-Analytics/streamlit/projects/HostActivity/main.py §_refresh/main; ../Wintap-Analytics/streamlit/projects/HostActivity/status_views.py §advisory status -->

### 4. SmokeTests, DataQA and EDA boundaries

**SmokeTests remains raw producer-evidence first.** Its manifests, HOST receipts,
stimulus selectors and coverage indicators answer whether a selected producer
workload has corresponding telemetry. The default source mode must remain
`raw-only`; a compacted object is not silently substituted for deleted raw
producer evidence. If an explicit `compacted-replay` mode is added, reports must
say that they validate post-processing/replay equivalence, not direct producer
delivery, and must include processing receipt and source labels. Entity authority
can provide context for a separate analysis but cannot turn a missing raw
producer-evidence case into PASS.

SmokeTests must also retain its current semantics: coverage is separate from
harness generation success, missing families stay explicit, separate canary rounds
are not silently combined, and result fingerprints include the complete object
snapshot and evaluator code. A deleted raw object should invalidate or make the
raw-evidence result unavailable rather than reuse a stale success.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/SmokeTests/s3_source.py §discover_files; ../Wintap-Analytics/streamlit/projects/SmokeTests/analysis.py §input_fingerprint/coverage; ../Wintap-Analytics/streamlit/projects/SmokeTests/batch_views.py §canary_batch_page -->

**DataQA and older EDA consumers need a compatibility boundary.** They currently
expect mounted/local datasets and legacy Parquet/stdview-style access. Do not
point them at a compacted root by changing one environment variable, and do not
claim DBT DuckDB output is a compatible Parquet publication. Choose one of these
explicit follow-ons per consumer:

- keep a documented `raw-only` compatibility profile for historical notebooks and
  old charts;
- add a compacted/entity-aware adapter that publishes stable views and labels the
  source/coverage contract; or
- consume a deliberate DBT DuckDB export contract after its schema and lifecycle
  are separately accepted.

Each adapter needs a migration test showing that raw-only and compacted-only
results agree for a settled reference window, with duplicate prevention and
missing-versus-zero assertions. Legacy consumers that cannot report source mode
and coverage remain explicitly raw-only and are not included in compacted-data
acceptance.
<!-- GROUND_TRUTH: ../Wintap-Analytics/streamlit/projects/DataQA/pages/raw_events.py §legacy stdview/local dataset path; ../Wintap-Analytics/streamlit/projects/DataQA/common; wiki/tension/dbt-duckdb-output-vs-legacy-stdview-parquet.md -->

### 5. Verification matrix and rollout order

Implement and review the downstream changes in this order:

1. **Contract fixtures:** synthetic raw-only, compacted-only, raw-deleted,
   non-overlapping mixed, overlapping mixed, missing-receipt and incomplete
   authority fixtures. Include at least two event families and process rows with
   an entity enrichment key.
2. **DBT gates:** source discovery/labels, raw-vs-compacted parity, duplicate and
   overlap detection, entity schema/metadata, cumulative authority, metrics
   coverage, identity-policy ceiling, and local DuckDB output provenance.
3. **HostActivity gates:** metadata and row modes for every source mode; coverage
   status rendering; source-labeled counts; no double counting; no empty-chart
   success when raw is deleted or authority is unavailable; advisory status only.
4. **SmokeTests gates:** raw producer-evidence behavior remains unchanged;
   compacted replay, if implemented, is separately labeled and cannot satisfy a
   raw-evidence assertion; fingerprints invalidate on source/mode/coverage change.
5. **DataQA/EDA gates:** legacy raw-only behavior remains stable, and every new
   adapter passes the same parity/duplicate/unknown coverage checks before it is
   allowed to consume compacted/entity-aware inputs.
6. **Real development window:** run the adapters against the completed Linux
   compacted/entity scope, compare a retained settled hour with a raw baseline
   where both exist, then exercise a deleted-raw hour. Record event families,
   source modes, entity generation, receipt status, row/count deltas and genuine
   skips. Native-Mac DBT remains deferred; this downstream qualification does not
   change that decision.

Acceptance requires explicit source labels, no unexplained row inflation or loss,
correct missing/unknown semantics, valid entity authority/metrics when entity mode
is selected, and a reviewed compatibility decision for each consumer. Successful
DBT build alone is insufficient.

## Defect triage and bounded repair

| Priority | Examples | Treatment |
|---|---|---|
| P0 — Stop affected scope | Wrong-prefix mutation; writer/reader overlap; unverifiable completion; silent loss/duplicate inflation; credential disclosure; unsafe runaway resource use. | Stop safely, retain concise diagnostics, fix before that scope resumes. |
| P1 — Blocks the milestone | Actual S3/client launch failure; entity bootstrap/checkpoint rejection; DBT required test failure; persistent unexplained `BLOCKED`; inability to catch up at the selected development load. | Reproduce on the real path, add a targeted regression, repair the smallest responsible layer, rerun that integration stage. |
| P2 — Useful but nonblocking | Incomplete old ancestry, accepted representative drift, rare unsupported recovery, dashboard polish, reduced-limit optimization or unrelated upstream field-quality issues. | Record impact and evidence; defer unless selected analysis becomes unusable or an exit criterion fails. |

Permit one narrowly defined repair cycle at a time. If it expands into a new
recovery design or repeatedly fails, return to the planner with impact/options;
do not indefinitely grow a prerequisite test matrix. Existing targeted failing
evidence stays recorded, but exhaustive archive/hash reconstruction is not the
deliverable of every pilot iteration.

For unsupported interrupted publication or missing originals, it is acceptable
to **abort a disposable development scope and rebuild**, rather than implement
general repair first. Establish that old readers/writers cannot resume, retain the
small failure report, leave old ownership blocked, and obtain scope approval for
a fresh independent dataset binding, all data roots, transport namespace and local
ledger/client state. Never forge completion, reset the old ledger to grant access,
reuse outstanding grants or silently clean unrelated prefixes. Destructive cleanup
still needs explicit exact-scope confirmation; it can wait until after the pilot.

Deferred unless encountered: original-bound pending-publication repair, recovery
with missing migration/deletion evidence, the full exclusive-maintenance corner-case
matrix, all-history bootstrap/ancestry, lower-resource certification and broader
platform/package/release hardening. These remain backlog, not abolished invariants.

## Next handoff

**Next action is to implement the source-mode/coverage adapters in a disposable
development branch, beginning with contract fixtures and DBT/HostActivity tests.**
Then select the real development run: confirm the Linux execution host, sensor
source and data window, existing endpoint/access, which development prefixes may
be created/migrated/deleted, and resource/stop ceilings in a private operator
manifest.
The simplified worksheet is in
[[wiki/work/dbt-compaction-coordination/isolated-qualification]]. The human will
deliver [[wiki/work/dbt-compaction-coordination/dev_handoff]] to the Linux runner.
This planning/publication task has not changed application source. The separately
authorized Linux deletion-enabled processing is operational evidence recorded in
the feature verification; any still-running tick must be independently verified
before being described as complete. Native-Mac DBT remains deferred.
