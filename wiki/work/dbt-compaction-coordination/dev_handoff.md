---
title: "Dev Handoff: Scheduled DBT and Compaction Coordination"
type: concept
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/brief.md
  - wiki/work/dbt-compaction-coordination/design.md
  - wiki/workflow/wintap-etl-data-flow.md
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/scripts/check_dbt_config.py
  - ../Wintap-PyUtil/wintap_dbt/macros/paths.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/s3.sql
  - ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql
  - ../Wintap-PyUtil/wintap_dbt/dbt_project.yml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/execution.py
  - ../Wintap-PyUtil/wintappy/coordination/writer.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/MACOS.md
  - ../Wintap-PyUtil/wintappy/coordination/verification.py
  - ../Wintap-PyUtil/wintappy/coordination/authority.py
  - ../Wintap-PyUtil/wintappy/coordination/completion.py
  - ../Wintap-PyUtil/tests/test_coordination_authority.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py
  - wiki/work/dbt-compaction-coordination/macos-qualification.md
  - ../Wintap-PyUtil/scripts/dcc_macos_baseline.py
  - ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/wintappy/coordination/recovery.py
  - ../Wintap-PyUtil/wintappy/coordination/maintenance.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py
  - ../Wintap-PyUtil/tests/test_coordination_deletion_recovery.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_verification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_observations.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_completion.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_publication.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_completion_qualification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publications.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py
policy: agent-editable
last_validated: 2026-11-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/dbt-compaction-coordination; ../Wintap-PyUtil/Makefile; ../Wintap-PyUtil/wintap_dbt; ../Wintap-PyUtil/extras/raw-sensor-compact
tags: [feature-work, dev-handoff, dbt, compaction, coordination, cron, duckdb, s3, local-only]
---

# Dev Handoff: Scheduled DBT and Compaction Coordination

## Handoff summary

**Current submitted snapshot / next gate:** PyUtil
`123b9d36705a5d9c356724d007b28bac224605a6`, Analytics `ee9c27a` (following
`3f11d13`). Linux service/client/advisory, v4 retry and explicit-v5 entity writer/
history/clean-original service dispatch are committed in that submitted baseline.
The 71/307 Linux gates below are focused/affected, not full latest-HEAD acceptance.
Independent portable review passes 76/zero skips; a separate provisioned native
five-module rerun passes 169/25 reviewed Linux-only skips with 83 identities intact.
Native restriction/bootstrap permits a tiny genuine DBT build/test, but uses
deprecated/private dependencies and qualifies no complete shutdown. The probe uses
in-process `dbtRunner`, unlike the client's `subprocess.call` path. Separately, the
PyUtil commit `c549424` (based on `1f4897a`) wires a process-group candidate into the
native coordinated reader and passes 12 actual-Mac synthetic lifecycle controls, plus
final bounded stress of 50 normal exits and 20 same-group-child shutdowns. This is limited lifecycle
qualification, not broad backend/service/DBT acceptance. Current evidence:
[[wiki/work/dbt-compaction-coordination/verification#Native macOS process-group prototype — actual-Mac synthetic lifecycle]].

The current human direction preserves native-Mac scope and explicitly accepts a
best-effort process-group shutdown rule: normal release may follow wrapper completion
and observation of no live members in the dedicated reader group, accepting the
residual possibility of an escaped descendant. Timeout, supervisor death or uncertain
group state retains the reservation for manual verification. No Linux VM or Docker is
required. No helper/service API or dependency is selected, and broader actual-Mac
platform acceptance remains open.
Analytics utility implementation remains separately authorized in its isolated
worktree; the busy producer retains interrupted-publication recovery.
The utility implements advisory v1 Status/raw intent Runs only, not catalog,
compacted/entity reads or managed live/coordinated lifecycles. No deployment,
scheduling, real-dataset mutation or push occurred. The local commits below are
explicitly authorized wrap-up commits; no deployment or production acceptance follows.
<!-- SOURCE: Human implementation approval, conversation 2026-11-15. -->

**Historical accepted packaging baseline:** PyUtil commit
`fab647f900196b0bc473fe7977b7dadcf7f4ce52` contains the receipt-bound launch,
independent verification and ledger-v3 completion/history work plus the durable
Mac harness and exact original main lockfile. All 22 manifest files pass committed/
local identity checks in a fresh Git-only clone; 18 harness controls pass. The original
`8ee714c` Mac attempt was blocked before either test stage by the omitted lockfile;
preserve that result. **dcc-mac-baseline-01 now passes** at `fab647f` on macOS arm64:
169 main passed/129 reviewed Linux-only skips; 267 standalone passed/zero skipped.
Both locked runtimes and all 22 identities pass, with no timeout. Evidence:
[[wiki/work/dbt-compaction-coordination/verification#Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed]].
R9's reproducible packaging repair is verified; skipped Linux writer/completion
paths do not establish Mac support. The uncommitted-overlay procedure is superseded.
Subsequent Linux work added the then-uncommitted service/client/advisory and audited-
recovery overlay, now committed in `123b9d3`, including narrow checkpoint/deletion
repair; broader recovery, S3/resource
qualification and dcc-02–05 remain open. Follow
[[wiki/work/dbt-compaction-coordination/macos-qualification#Stage 2: reader backend acceptance remains pending]]
for the later Mac lifetime/shutdown gate, not another unchanged baseline rerun.

**Latest Linux results:** strict entity service focus passes all 71 controls (251.19 s), and
the unchanged 13-module service-affected scope passes **307 controls in 2,036.10 s**. Complete
report/sidecar, actual crash diagnostics, all 307 frozen identities, 5,982 retained fixture
entries and prior green/red/accepted-forward evidence authenticate. Read-only inspection validates
170 ledgers and maps 18 expected reopen refusals to explicit corruption controls. The two actual
service deaths preserve the intended boundaries: pre-COMMIT remains blocked without typed
completion/authority; post-COMMIT retains typed completion and authority in `DRAINING` without
raw-cursor advancement. The post-COMMIT proof is read through the supported history accessor.
The accepted forward-history fixture remains unchanged and was not rerun. Only these Linux
focused/affected gates close; pending-publication/missing-original repair and broader both-runtime
integration remain next. S3, resources, native-Mac shutdown and dcc-02–05 remain open:
[[wiki/work/dbt-compaction-coordination/verification#Service-affected Linux result — 307-control affected gate closed]].

**Native-candidate Linux cross-check:** the transferred PyUtil `c549424` has the
reported `1f4897a` parent, directly above the prior `123b9d3` Linux target. Its
focused supervisor/client/Linux-lifecycle/local-route suite passes **90** with
**12 native-Mac-only skips**; no Linux behavior change was observed. The earlier
307-control service-affected gate was not rerun, and broad latest-HEAD, endpoint,
resource and deployment qualification remain open:
[[wiki/work/dbt-compaction-coordination/verification#Linux regression after candidate handoff — focused, no behavior change observed]].

The selected narrow successor first adds strict init/replay/clean-original resolution service
dispatch and explicit v5 upgrade selection, with separate entity configuration and genuine
controls before coding. The first frozen service red finishes with 71 failures in 135.78 s:
one unsupported configuration, 64 parser-masked controls, four missing-loader failures and
two parser-stopped crash children. Complete lossless report/sidecar/actual diagnostics and
all 307 identities are reviewed; no service COMMIT boundary or semantic refusal is qualified.
Only `service.py`/`recovery.py` now implement those seams; the complete 303-line source delta
is reviewed and a distinct 307-identity runtime freeze preserves all 305 other identities.
The unchanged rerun and full evidence inspection now pass: 32 verifier groups/ten clean CLI
captures/60 immutable archives, nine atomic typed completions and one immutable resolution;
all 439 retained files/eight symlinks and 307 identities authenticate. Both actual service
children exit 91; original receipts identify the runs, not their `null` diagnostics. Before
COMMIT stays blocked with no completion/authority; after COMMIT retains both without raw
advancement. One prepared-only retry receipt confers no intent/verifier/launch/archive. Real
restart block clocks and all damaged/missing originals remain unchanged. Inspection-only
directory/configuration assumptions and both failed reports/sources are retained; no runtime
repair was indicated and no test was active at strict-service focus closure. Pending-publication
repair remains separate, not permission to weaken clean recovery:
[[wiki/work/dbt-compaction-coordination/implementation_plan#Strict Linux entity service successor]].

The service-affected run used 13 existing service/client/lifecycle/local-route/raw-recovery/
maintenance/retry/entity-service modules and a distinct byte-identical source freeze. Its
complete report and fixture review are recorded above; the accepted forward-history module/
fixture was excluded, not rerun. Pending-publication repair controls and broader both-runtime
integration remain separate:
[[wiki/work/dbt-compaction-coordination/implementation_plan#Original-bound pending-publication controls — source planning only]].

Read-only source planning sharpens the next original-bound pending-publication matrix:
genuine partial genesis/replay must not enter current-only clean resolution. Candidate journal
matching is not permission or original success; independently establish original scope/input/
predecessor/candidate binding before selecting a separate repair representation. Missing
original success/candidate evidence is never backfilled. No new pending-recovery controls or
runtime implementation is qualified by the completed service-affected gate:
[[wiki/work/dbt-compaction-coordination/implementation_plan#Original-bound pending-publication controls — source planning only]].

Implement the accepted basic plan: **one cron-driven Python coordinator, S3
messages, and a persistent server-local DuckDB ledger**, coordinating hourly
compaction with three to five researchers' occasional local DBT builds over S3.
Preserve the ordinary single-user local-raw workflow as a first-class path.

This document specifies the full integration task. Protocol/ledger and the first
controlled-clock tick and Linux supervision libraries exist. Verified normal
completion/history exists as a locked local library, not the current tick callback;
service/client integration now exists in submitted `123b9d3`, while
production scheduling remains uninstalled. Current local
DBT, dual-root reads, compaction and optional durable entities already exist. Wintap-PyUtil owns
implementation; Wintap-Analytics owns
the shared wiki and this feature folder. Independent deeper compactor qualification
continues separately; integrate against its latest qualified CLI/report contract.

**November 14 completion planning:** the human selected Linux coordinator/writer,
Linux/macOS readers, actual-endpoint qualification on fresh feature-owned fixtures,
and initial 32 GB RAM / 64 GB disk sizing with monitored usage before recommending
lower limits. Read the dependency-ordered completion slices in
[[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]]:
review repairs, execution/platform gates, independent completion, service/client,
audited recovery and integrated qualification. dcc-02's real completion depends
on dcc-04's verifier/high-water evidence; no unit is accepted by this plan alone.
<!-- SOURCE: Human planning decisions, conversation 2026-11-14. -->

**Reviewed baseline:** PyUtil `c782f63`, Analytics `d904559`. Read
[[wiki/work/dbt-compaction-coordination/implementation-review]] for reproduced
snapshot-validation/provenance gaps and required checkpoint/recovery integration.
The basic lock architecture remains applicable. Subsequent R1–R5 safety work and
current acceptance results are tracked in
[[wiki/work/dbt-compaction-coordination/implementation_plan]] and
[[wiki/work/dbt-compaction-coordination/verification]]; review-time findings below
are not claims that the same defects remain in the working tree.

Detailed specification: [[wiki/work/dbt-compaction-coordination/design]].
Requirements: [[wiki/work/dbt-compaction-coordination/brief]].
[Editable sequence diagram](sequence.drawio): shared reader lifecycle and hourly
writer handoff.

**Approved diagnostic exception, November 14:** the follow-on same-server
HostActivity utility defaults to uncoordinated live observation with persistent
warnings and inconclusive race failures; coordinated refresh is optional. Do not
apply its bypass to DBT, authoritative verification, ledger access or recovery, and
do not count diagnostic observations as reserved readers or completion evidence.
The utility is a separately authorized implementation slice, not producer recovery
work or operational acceptance. Read
[[wiki/work/dbt-compaction-coordination/design#Diagnostic observation exception]]
before documenting that all dashboards must acquire grants. The worker-owned
local status v1 is consumed; catalog/entity history/certificate/progress exports
remain follow-on dependencies.

## Worker continuation after the Mac review

Historically the human finalized the packaging review for commit/push and returned the remaining
implementation to the PyUtil worker. Resume the existing completion plan; do not
restart the accepted baseline or interpret its Linux-only skips as Mac support.
The November 15 implementation initially had no commit/push permission; the human
subsequently authorized local commits. The native-Mac source is PyUtil `c549424` on
the isolated branch, based on `1f4897a`; the Analytics evidence is committed locally
as well. Neither commit was pushed. The Linux worker has no shared filesystem with
this worktree, so transfer the PyUtil commit through the approved channel before
testing/integration; the hash alone is not present on that worker. Use the transferred
commit and verification record above as the continuation baseline.

1. **Reader platform gate:** implement and qualify Linux/macOS reader lifetime and
   shutdown under their respective contracts. For native macOS, normal release may
   follow wrapper completion plus observation of no live members in the dedicated
   process group; the
   human explicitly accepts the residual risk of an escaped descendant. A timeout,
   supervisor death or uncertain group state retains the reservation for manual
   verification. No Linux VM or Docker is required; Linux rules and direct local-only
   DBT stay unchanged.
     **Current feasibility checkpoint:** an isolated native-Mac process-group
     candidate is implemented and wired to the coordinated client; 12 synthetic
     lifecycle controls pass on an actual Mac. This is not backend/platform acceptance:
     real DBT/data, actual S3, production service, representative resources and broader
     Mac behavior remain open. The restriction probe's in-process DBT success remains
     separate from the client's subprocess-based launcher. Apple's XPC/launchd service
     lifecycle does not establish detached-descendant shutdown; Endpoint Security fork
     events are notifications. The human accepted the process-group risk boundary but
     selected no helper/service API or dependency. Read
     [[wiki/tension/native-macos-readers-vs-descendant-shutdown]] and the new verification
     entry. Continue Linux integration independently; do not claim native-Mac production
     support from the synthetic controls or accepted baseline.
2. **Service/client integration (slice D):** the Linux service now wires locked
   completion, durable request/grant/cancel/release handling and bounded advisory
   exports; broader qualification remains open. Do not use the conservative `tick`
   callback as a completion bypass. Preserve direct
   local-only `make dbt-build` and optional compaction/entities.
3. **Audited recovery (slice E):** add explicit confirmed/reasoned operator operations
   using original evidence under exclusion. Stopped processes or diagnostic reads
   alone never authorize reopening.
   **Current narrow path:** clean original runs and recorded exit-2 checkpoint-only
   failures have separate authenticated resolution paths. `repair-checkpoints`
   commits receipt/intent before supervised maintenance; repair leaves the block,
   `resolve-hour --maintenance-id` verifies original/repair evidence before atomic
   completion, and `abandon-maintenance` only audits a pending cannot-resume attempt.
   The subsequent `repair-deletions` path authenticates complete original
   migrations and unchanged survivors/outputs, retains separate actual disposition
   observations and never replays entities. Its local regressions are closed;
   incomplete migration evidence and interrupted entity publication remain
   blocked. Explicit-v5 entity launch/clean-original resolution is implemented;
   missing originals still refuse. Raw-only intentional retry has closed local regressions,
   not endpoint/resource or Linux qualification. Read
   [[wiki/work/dbt-compaction-coordination/verification#Checkpoint maintenance — narrow repaired-phase path, regressions pending]]
   and `../Wintap-PyUtil/wintappy/coordination/LINUX.md` before recovery work.
4. **Integrated qualification (slice F):** first synthetic local lifecycle controls,
   then human-approved isolated S3 fixtures and representative resource measurements.
   Keep dcc-02–05 unchecked until their own acceptance evidence is recorded.
   The gated [[wiki/work/dbt-compaction-coordination/isolated-qualification]] procedure
   is prepared; concrete environment, roots, access, runner and ceilings are unselected.
5. **Utility dependency agreement:** advisory v1 consumer implementation is authorized
   and passes 46 offline controls. Agree additional run/catalog/certificate interfaces
   and qualify managed reader lifetimes before extending it. Deployment still requires
   approval; Live diagnostic is non-authoritative and Coordinated refresh optional.

Read [[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]],
[[wiki/work/dbt-compaction-coordination/macos-qualification#Stage 2: reader backend acceptance remains pending]],
the review/verification evidence, and
[[wiki/work/compaction-status-utility/implementation_plan]] before the next code pass.
Preserve original failures and private reports; record new red/green commands,
revisions and qualification limits in the shared wiki. Production rollout remains
a separate human gate. The original full-scope prompt below is reference material.
Full standalone passes **460 tests/two skips** (191.79 s). The affected main run
then finishes with 303 passes/one test-wrapper failure (723.91 s); its report and
fixtures are retained and all 261 identities match. Only the wrapper's missing
independent `cursor()` delegation is repaired; its real three-hour paging/corruption
control passes. The combined rerun uses `dcc-linux-checkpoint-paging-source-freeze.json`
and passes **304 tests in 715.34 s**. Complete report inspected after notification;
all 261 identities still match. Full main passes **755 tests/three skips in 1156.34 s**,
with the complete separate `dcc-linux-checkpoint-main-full-paging-fixed.txt` report
inspected and all identities still matching after notification.
Every runtime/source/DBT/lock/standalone-test identity is unchanged for that baseline.
The completed full-main notification and identity checks permit the next source slice;
retain this baseline and require separate regression evidence for new source changes.
Existing 697/439 historical
full results precede the reader/checkpoint repairs and must not be promoted as current
acceptance. No current commit/push authorization is implied by the earlier finalized
Mac-review publication.
Scoped final source/wiki/privacy review is closed: 30 source/config/doc files,
23 Python Ruff targets and nine Markdown/seven-frontmatter audit pass; both
whitespace checks pass. Infographic artifacts and unrelated data/environment work
are preserved. Audit/local-regression closure does not substitute for the remaining
Linux qualification gates.
The frozen-wait source review identifies why generic deletion reconciliation cannot
certify partial original runs, and why retry/general maintenance need durable retained
dispositions. Next-pass boundaries and red-control sequence:
[[wiki/work/dbt-compaction-coordination/implementation_plan#Next source slice: original-bound recovery and maintenance]].
This is source-grounded planning, not new test evidence or a selected ledger upgrade.
The subsequent deletion-only source slice has closed its local regression gate: real local partial-deletion
fixtures, retained verifier/service/interference/capture failures and initial runtime
repairs are in
[[wiki/work/dbt-compaction-coordination/verification#Original-bound deletion recovery]].
Frozen standalone deletion focus passes 49 tests in 90.48 s, with its complete report
inspected and all 265 frozen identities unchanged after notification. Frozen main
focus passes 33 tests in 348.84 s, with complete report inspected and all identities
unchanged. Affected standalone passes 203 tests in 177.37 s, exit 0; complete report
inspected and all 265 identities unchanged after notification. Full standalone passes
509 tests/two opt-in S3 skips in 274.88 s, exit 0; complete report inspected and all
265 identities unchanged after notification. Affected main passes 515 tests/one
explicit isolated-local migration skip in 1345.33 s, exit 0; complete report inspected
and all 265 identities unchanged after notification. Full main passes 788 tests/three
skips in 1492.66 s, exit 0; complete report inspected and all 265 identities unchanged
after notification. This closes combined local deletion regressions, not dcc-02–05
or Linux qualification. Retain the accepted freeze/reports, disposition archive and
original failure; do not substitute generic reconciliation, retry a raw writer or
replay entities through current APIs. Source is released for the separate verified
retry/durable entity-maintenance slice, with new active-path red controls and its
own focused/affected/full regression evidence required.
Renewed scoped source/test/config/doc and complete wiki-diff/privacy review is
closed: fresh 11-target Ruff lint/format, nine-Markdown/seven-frontmatter audit and
both whitespace checks pass. Other reader/checkpoint identities remain unchanged.
Actual isolated S3/access, representative resources and native-Mac shutdown remain
separate open gates; no production operation, scheduling installation, commit or push.
<!-- SOURCE: Human finalization and return-to-worker decision, conversation 2026-11-14. -->

## Copy/paste prompt

Use this prompt to start the implementation task from Wintap-Analytics:

```text
Switch to code-development mode for Scheduled DBT and Compaction Coordination.
Implement the coordinator and client integration in ../Wintap-PyUtil, and maintain
the shared feature documentation in this repository's wiki/.

Read AGENTS.md and any applicable instructions in the implementation checkout.
Read these exact handoff files before editing code:
- wiki/work/dbt-compaction-coordination/dev_handoff.md
- wiki/work/dbt-compaction-coordination/brief.md
- wiki/work/dbt-compaction-coordination/design.md
- wiki/work/dbt-compaction-coordination/implementation-review.md
- wiki/work/dbt-compaction-coordination/sequence.drawio
- wiki/workflow/wintap-etl-data-flow.md

Goal: shared DBT grants and exclusive hourly compaction through S3 messages,
a once-per-minute Python tick and a persistent local DuckDB ledger, while
entirely local builds keep the direct make dbt-build workflow.

Inspect both working trees and read the live sources listed in the handoff.
Start with dcc-01: the durable ledger/protocol and failure-point tests using
fake storage/children. Maintain implementation_plan.md and verification.md in
this feature folder against the handoff units and acceptance matrix; track commands
and results there as implementation proceeds. Follow through the remaining units.
Preserve transaction-before-grant/launch ordering, all-input-root classification,
the complete DBT preflight/build/child-shutdown grant lifetime, manual abandoned
reader recovery and blocked-writer reconciliation. Use the current main and
standalone compactor environments separately. Keep fixtures isolated from the
independent compactor qualification data. Update the wiki as behavior stabilizes.
Include active processing_metrics in dataset binding, hold the writer through
final checkpoint verification, and keep migration receipts separate from coverage
checkpoints. Apply the implementation review's recovery and regression requirements.
```

From the PyUtil checkout, the same wiki files are under
`../Wintap-Analytics/wiki/`. The tracking files named above already exist; this
handoff supplies the coordination implementation units.

## Behavior and defaults to implement

| Area | Contract |
|---|---|
| Scheduling | One Python `tick` every minute on the existing compaction server; a tick exits after work or supervises its compactor child to completion. |
| Authority | Only that coordinator grants access; its local DuckDB ledger is authoritative. S3 carries per-job JSON messages. |
| Readers | Multiple DBT grants may coexist. Lock scope includes raw, compacted, configured entities and active processing metrics; request windows are diagnostic. |
| Writers | When an hour is due, enter `DRAINING`, stop new grants, wait for every reserved reader, then compact exclusively. |
| Catch-up | Persist the oldest unfinished UTC hour; default ten-minute grace and one hour per tick. Backlog retains writer priority until caught up. |
| Client polling | Default ten seconds for the client's exact grant key, configurable with `WINTAP_COORDINATION_POLL_SECONDS`. |
| Release | Upload immediately after all managed source-reading children stop. Successful upload lets the client return without another coordinator acknowledgment. |
| Recovery | Documented v1 default is manual abandoned-reader recovery; automatic expiry remains unselected. Uncertain writer outcomes stay `BLOCKED`. |
| Local-only | Resolve all effective input roots first; entirely local inputs execute directly using the main DBT environment. |
| Outputs | DBT analysis database/artifacts remain local. Coordinator ledger, client retry records and optional entity snapshots are distinct artifacts. |

### Polling latency

The retained defaults are **60-second coordinator ticks and 10-second client
polls**, not one-minute polling on both sides:

| Transition | Nominal maximum polling delay |
|---|---:|
| Request becomes visible → coordinator records reservation and publishes grant in the same tick | 60 seconds |
| Grant becomes visible → client observes it and starts preflight | 10 seconds |
| Release becomes visible → coordinator retires reservation | 60 seconds |

Budget approximately **70 seconds before DBT starts**, plus **60 seconds after
completion before the coordinator recognizes release**: 130 seconds of lifecycle
polling overhead. That final delay affects writer admission, not the returning
DBT command after a successful release upload. One-minute client polling would
instead give the discussed 180-second budget. These are polling estimates, not
hard deadlines: exclude DBT runtime, tick/API processing, storage visibility,
retries, due/active compaction and reader draining. A busy long-running writer
tick holds the local lock, so later cron invocations exit busy.

### Local-only compatibility

With ordinary DBT dependencies installed and DBT overrides unset, the supported
invocation from PyUtil remains:

```sh
export WINTAP_DATA_ROOT='/path/to/local-dataset'
make dbt-build
```

Read its `raw_sensor/<event>/dayPK=YYYYMMDD/hourPK=HH/.../*.parquet`, discover local
date bounds, and write `$WINTAP_DATA_ROOT/duckdb/wintap.duckdb`. A missing local
`compacted/` directory is valid. An unset/empty `WINTAP_DBT_PROCESS_ENTITY_ROOT`
disables durable enrichment; process context then comes from the selected event
window. Current source already implements these defaults and skips S3 secret
setup for entirely local inputs.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/Makefile §defaults/dbt-build; ../Wintap-PyUtil/scripts/check_dbt_config.py §validate; ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §matching_raw_sensor_partition_globs; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_process_entities; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

The new routing must bypass coordination initialization, grants, polling and job
records for this path. It needs neither compactor installation nor entity
bootstrap. Check effective **raw, compacted, entity and active processing-metrics**
roots after defaults and overrides; any S3 input selects coordinated access.
R5 now makes offline root resolution and S3 setup consistently ignore unused remote
metrics overrides with entities disabled. Keep that behavior in client routing;
entity-enabled remote metrics must remain an active input.
Existing AWS/coordination
settings alone cannot activate coordination for local inputs. Shell-reset guidance:
[[wiki/workflow/wintap-etl-data-flow#Local-only single-user workflow]].

## Invariants the implementation must preserve

1. Commit `GRANTED` plus the immutable grant outbox entry before PUT. Undelivered
   and unacknowledged grants still count as reservations and exclude a writer.
2. Commit `WRITING` and the run identity before subprocess launch. A restart that
   finds unresolved `WRITING` enters `BLOCKED`; the old child may still be alive.
3. Take the same nonblocking local process lock before every ledger open, including
   operator commands. Hold it through a writer's outcome. Initialize explicitly;
   an ordinary tick cannot replace a missing ledger with empty state.
4. Keep job IDs/digests stable across retries; retain terminal records. Process
   releases/cancellations before admission. A cancellation is terminal even if its
   request arrives later, and that client must never honor a delayed grant.
5. Hold one grant across source preflight, the complete DBT build/tests, and the
   platform's accepted shutdown check. Linux requires its supervised descendant tree
   to stop. Native macOS uses the human-approved best-effort rule: after wrapper
   completion, observation of no live members in the dedicated process group may
   authorize normal release,
   with escaped-descendant risk explicitly accepted. Bronze models are views and can
   read S3 after initial discovery.
6. Release after unsuccessful DBT work only under that platform's shutdown rule. On
   uncertain delivery, retain a local pending release for retry and report the
   outstanding job ID. On native Mac, timeout, supervisor death or uncertain group
   state retains ownership for manual verification; Linux rules are unchanged.
7. Advance the hour cursor only after verified completion. Stopped children,
   elapsed time, an existing destination or a zero exit status alone do not prove
   successful migration. Partial output/source overlap remains blocked.
8. Treat S3 messages/status as transport/diagnostics; absence or age is never
   permission to run. Failed API calls are errors, not empty listings. Manual
   release requires establishing that the original reader cannot resume.
9. Keep entity initialization/replay/rebuild/cutover and deletion reconciliation
   under exclusive maintenance through the same authority. Hold the normal writer
   through final processing-checkpoint verification and persist separate raw,
   entity and checkpoint outcomes before reopening. Failed final publication can
   follow successful raw deletion; never auto-retry that as an untouched hour.
10. A reader grant does not guarantee entity coverage for an unfinished process
    hour. Fail preflight clearly and release after children stop; do not hold a
    read grant waiting for the writer, trim the window or silently disable entities.
11. Bind the actual writer invocation to a durable, allowlisted, non-secret
    effective execution/configuration receipt and checksum it in the committed
    intent before launch. Resolve defaults/overrides/environment inputs once;
    record roots, hour/run IDs, events, entity policy, deletion options and budgets
    with executable/runtime identity. Missing/mismatched settings refuse launch;
    post-launch uncertainty blocks completion. Never dump the whole environment,
    persist credentials or accept the current environment-omitting command manifest
    as a complete receipt. The local launch, verification and normal-success
    libraries implement this gate; the uncommitted Linux service now uses the
    same-lock adapter, with final qualification still pending. See
    [[wiki/work/dbt-compaction-coordination/design#Required execution and configuration receipt]].

The design specifies ledger tables, JSON identity fields, outbox ordering and
recovery commands. The single-authority protocol is grounded in the endpoint's
recorded conditional-write behavior; see
[[wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint]].

## Primary sources and implementation artifacts

Paths below are relative to **Wintap-PyUtil**; read them live.

| Source | Integration point |
|---|---|
| `Makefile`, `scripts/check_dbt_config.py` | Effective roots/output/window, local date discovery, separate source preflight and build targets. |
| `wintap_dbt/macros/paths.sql`, `wintap_dbt/macros/s3.sql`, `wintap_dbt/macros/validate_source.sql` | Raw/compacted discovery, S3 setup, source preflight. |
| `wintap_dbt/macros/process_entities.sql`, `wintap_dbt/models/silver/process.sql` | Optional entity reads and the disabled local baseline. |
| `wintap_dbt/dbt_project.yml`, `wintap_dbt/profiles.yml` | Hooks, model materialization and local DuckDB output. |
| `pyproject.toml`, `extras/raw-sensor-compact/pyproject.toml` | Main Python/DBT runtime uses DuckDB 1.5.6; isolated compactor uses 2.0.0. Only the main runtime opens the coordination ledger. |
| `wintappy/coordination/{protocol,ledger}.py`, `wintappy/coordination/README.md` | Strict v1 messages and locked ledger; the active successor v4 adds compatible v1/v2/v3 upgrade and bounded retry dispositions while preserving reservations/outbox, failed originals and retained authority/completion proofs. Restart/blocked intents require audited recovery through the uncommitted Linux service; no production scheduler is installed. |
| `wintappy/coordination/coordinator.py`, `tests/test_coordination_tick.py` | First dcc-02 admission/draining slice: bounded complete listings, atomic terminal-first ingestion, oldest-hour priority and blocked callback outcomes. Not a supervisor, full scheduler or completion verifier. |
| `wintappy/coordination/supervisor.py`, `tests/test_coordination_supervisor.py` | Linux/main-thread isolated-subreaper command trees, bounded private logs/control/report parsing and interruption/error cleanup. Tested in a locked tick callback, but never independent completion/reopening authority; non-Linux/external-service containment is unqualified. |
| `wintappy/coordination/{execution,writer}.py`, `tests/test_coordination_execution.py` | Immutable bounded effective receipt and qualified standalone launch bound inside intent. Conservative `execute_prepared` blocks; separate normal-success execution obtains fresh verification internally. No actual-S3 service or macOS qualification. |
| `wintappy/coordination/completion.py`, `tests/test_coordination_completion.py`, `tests/test_coordination_completion_controls.py` | Internal normal-success and separately bound repaired-phase proofs, bounded original-archive rechecks and retained history/compatibility/budget/clock/crash controls. Historical 641 main/439 standalone full results (three/two skips) precede the Linux overlay; current regression status is in verification. Caller-provided reports cannot complete. |
| `wintappy/coordination/{verification,authority}.py`, `extras/raw-sensor-compact/src/raw_sensor_compact/completion.py`, `tests/test_coordination_authority.py` | Separate receipt/intent/shutdown-authenticated data verification plus explicit ledger high-water initialization and same-session freshness checks. Main entity verification uses the retained anchor without advancing it; no completion/cursor transition. |
| `wintappy/coordination/{service,client,recovery,maintenance,inputs}.py`, `wintappy/coordination/LINUX.md`, `config/coordination.*` | Uncommitted Linux integration: one-lock normal completion/service, root-aware reader wrapper, bounded local advisory export, audited cancellation/clean-original resolution, checkpoint repair, original-bound deletion disposition and raw-only intentional retry. Deletion/retry local regressions pass; general entity maintenance and actual S3/resource gates remain open. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py`, `tests/test_coordination_deletion_recovery.py` | Complete original-migration validation, bounded survivor/output inventories and separate disposition observations/checkpoints without entity replay; independent resolution preserves original exit 2. Public completion remains one hour; multi-hour standalone repair does not widen it. |
| `wintappy/coordination/retry.py`, `extras/raw-sensor-compact/src/raw_sensor_compact/retry_verifier.py`, corresponding retry tests | Raw-only single-event/hour read-only prerequisite. No retry transition or ledger change. Initial scope-masked negatives are disclaimed; late-prefix/count-corruption failures retained. Exact original-intent totals bind. Frozen focuses pass 33 main/45 standalone; affected passes 548 main/one opt-in skip and 248 standalone; full passes 821 main/three skips and 554 standalone/two opt-in S3 skips. Complete reports inspected and all 269 identities unchanged after notifications. Combined local preflight gate closed; retain baseline for the next slice. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/cli.py`, `extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py` | One-hour CLI arguments, report fields, optional entity phase, deletion and reconciliation outcomes. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py` | Version-4 fixed-hour coverage names its committed entity generation; final publication remains separate from migration success. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py`, `wintap_dbt/macros/entity_authority.sql` | R1 current-state authority, historical receipt lineage and recorded before/after publication-intent recovery. Legacy upgrade uses fresh entity/metrics roots and explicit cutover. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py`, `extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py` | SQL working state, per-host publication, preserved bootstrap metadata and bounded active integrity validation. |
| `extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py`, `tests/test_checkpoint_repair.py` | Immutable local run archive; original-generation checkpoint repair after deletion without entity replay or original-history replacement. |
| `tests/test_dbt_source_validation.py`, `tests/test_compacted_inputs.py`, `tests/test_process_entities.py` | Existing local/S3 configuration, dual-root and optional-entity regression fixtures. |

Both preflight full gates now pass; no regression remains running. Retain the
269-identity baseline/reports before separate durable retry/entity source work. The live
v3 single-owner and genuine-completion history constraints require an explicit
compatible retry disposition, not deletion of the failed original or fake completion.
Entity-only receipts/verification/ownership must stay separate from existing public
one-hour `compact` validators. `init-authority` verifies existing committed state;
it does not launch entity initialization. Reviewed ordering and required crash/
compatibility controls:
[[wiki/work/dbt-compaction-coordination/implementation_plan#E. Operator recovery without manufacturing evidence]].

**Active successor slice, not accepted:** explicit v4 adds bounded original-bound
retry dispositions while leaving failed originals `BLOCKED` and unchanged. Fresh
receipt/new-intent ownership commits atomically before launch; genuine new completion
alone can advance the cursor. Initial controls retain 11 missing-implementation
failures and then six capture-reconstruction failures/five passes. Exact original
error bytes now remain separate from parsed JSON. The interrupted extended run is
not a pass; the fresh resumed run finishes with two failures/11 passes in 83.33 s.
Post-COMMIT input arrival and same-count changed content at launch wrongly complete;
fresh pre-launch disposition and original/new migration-identity checks, including
audited recovery, now pass all 13 controls in 89.68 s. A subsequent credential-scope
review delta is covered by the extended run's 37 passes; four service controls fail
at the missing `retry-hour` dispatch (233.40 s, exit 1; complete report inspected).
Strict Linux original-receipt dispatch is now implemented under one lock, requiring
confirmation/reason and refusing unrelated flags before configuration resolution;
no transport/grants. The repaired run passes 42 controls in 244.42 s, complete report
inspected. First genuine history/exclusion run retains one unordered-row restoration
failure/12 passes (60.14 s); make full-row test comparison deterministic and rerun.
The corrected rerun passes 13 (60.10 s); distinct actual v3 upgrade crash/lost-ack
controls pass three (17.99 s); credential-reuse controls pass two (24.88 s). Complete
reports inspected. All 14 successor source/test targets reviewed, fresh Ruff checks
pass. All 263 unaffected preflight identities still match; six intended
source/fixture deltas and new files are retained in a separate 275-identity successor
freeze, created/checked without overwriting the accepted preflight manifest.
Standalone focus passes 45 (4.20 s), complete report inspected and all 275 identities
match after notification. Standalone affected passes 248 (180.48 s), complete report
inspected and all 275 identities match. Only then launched its full suite. Main focus
passes 119 (512.18 s), complete report inspected and all identities match. Main
affected passes 607/one isolated-local migration opt-in skip (1843.36 s), complete
report inspected and all 275 identities match. Only then launched full main, which
passes 880/three opt-in skips (2013.77 s). Standalone full passes 554/two opt-in S3
skips (290.13 s); complete reports inspected and all 275 identities match after each
notification. Combined intentional-retry local gate closed, not Linux acceptance.
Retain the freeze/reports and all historical failures before distinct entity-only
source work; new controls and successor regressions are required. Entity-only
ownership and isolated-S3/resource qualification remain open:
[[wiki/work/dbt-compaction-coordination/verification#Intentional-retry ownership — active, not accepted]].

The separate entity-only slice has 22 lint/format-clean controls; its first retained
run finishes with 22 failures in 35.05 s. All 749 report lines are inspected and all
275 accepted identities match. Missing execution API causes every failure; four child
controls exit 1, not their requested crash 87. Failed fixtures/report are preserved.
Standalone-verifier first run retains 64 missing-module failures in 29.53 s, exit 1;
all 2,972 retained report lines inspected, failed fixtures preserved and all 275
accepted identities unchanged. No verifier refusal is accepted. Distinct receipt
first red retains 26 missing-module failures (0.51 s), all 523 lines inspected and
fixtures preserved. Distinct receipt implementation now passes 26 controls (6.16 s),
with complete report inspection, fresh Ruff lint/format and all 275 accepted identities
unchanged. Preparation grants no launch authority. Separate standalone verifier
implementation passes its initial 64 controls (36.47 s); complete report inspected and
all accepted identities unchanged. Corrected review red retains 21 failures/two passes
(6.94 s); all 901 report lines reviewed and all accepted identities match, including
genuine wrongly accepted historical-statistic attacks. Verifier-only streaming SQL,
exact original-hour/early configuration and historical-publication repairs are
unqualified. Both repair reruns retain 12 failures/75 passes (35.57 s / 35.77 s), with
complete report/identity checks. Direct diagnosis reaches missing optional NumPy at
UDF registration; bounded one-record SQL staging now avoids that dependency without
lockfile changes. Expanded compatibility/budget/publication/request controls pass
fresh five-target Ruff lint/format. Expanded first run retains 35 failures/9 passes
(20.71 s); complete exact-deduplicated report reviewed, fixtures preserved and accepted
identities unchanged. Repaired nonexistent Inventory count reference after retained
read-only diagnosis; four stage diagnostics succeed. Combined run passes 131 controls
(91.07 s), with complete report/identity checks. Ten expanded controls retain five
fixture failures/five passes (8.31 s); complete report reviewed and fixtures preserved.
Fixture-only legacy Unicode-selection/SQL-order corrections pass ten (8.49 s), with
complete report/identity checks. Fresh five-target Ruff lint/format passes; distinct
expanded combined rerun passes 141 controls (97.91 s), with complete report and all
275 accepted identities unchanged. Standalone verifier focused evidence is closed;
durable publication authentication and ownership remain
missing; DBT/locks unchanged. Opt-in upgrade controls retain seven unsupported-argument
failures (35.10 s), and
post-verifier ownership rerun retains 22 missing-module failures (44.08 s). Complete
295-/960-line reports inspected, failed fixtures preserved and all 275 accepted
identities match before source changes; no crash boundary executes. Compatible ownership
and original-bound
non-mutation/authority/checkpoint evidence are still required. Public one-hour validators
and native-Mac's separate gate remain unchanged. See
[[wiki/work/dbt-compaction-coordination/verification#Entity-only ownership — active, not accepted]]
and [[wiki/work/dbt-compaction-coordination/implementation_plan#Entity-only ownership slice — active, not accepted]].

Explicit opt-in `target_version=5` schema staging is now implemented, not entity
permission. Default initialization/upgrades remain v4; ordinary open never migrates.
Seven actual v4 upgrade crash/lost-ack controls pass (36.93 s), then 37 expanded
compatibility controls pass (48.43 s), complete reports reviewed. Only `ledger.py`
differs from the accepted 275-identity baseline. Separate entity tables refuse nonempty
history until typed ownership/proofs exist. The 43-control genuine-history focus
passes (109.80 s), complete report reviewed and all 286 identities match after
notification. Existing-ledger first compatibility retains two failures/149 passes
(401.75 s), complete report/identity review done. Both actual COMMIT/lost-ack/row
checks precede a repeat-upgrade diagnostic mismatch; later assertions did not execute.
Restored only original default-v4 wording, retaining opt-in-v5 wording and all tests.
Failed fixtures remain preserved. Separate 286-identity diagnostic-repair freeze
binds repaired 46-control focus/151-control compatibility runs. Focus passes 46
(127.49 s), complete report reviewed and all 286 repair identities match. Compatibility
passes 151 (399.51 s), complete five-line report reviewed and all repair identities
match. Schema compatibility is closed, not entity permission or successor full gates.
Extend main-side authenticated entity observations before typed ownership/history;
preserve original failures and the schema freezes when beginning distinct source work.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_validate_entity_schema_origin; ../Wintap-PyUtil/tests/test_coordination_entity_schema_history.py -->

First main-side observation sub-slice adds 21 controls: retained first red has 21
missing-module failures (16.90 s), complete report/identity review done. New read-only
`entity_verification.py` binds actual canonical input-verifier evidence under owner-free
v5 exclusion, with no ledger permission/data changes. First rerun retains one actual
command-byte acceptance failure/20 passes (65.77 s), complete report/identities reviewed.
Exact command/shutdown-byte repair and six new controls pass 27 (83.28 s), complete
three-line report reviewed and all 288 artifact-repair identities match. Artifact focus
is closed; broaden input-authentication qualification before typed ownership. Failed
fixtures and original snapshots retained; no successor full gate is inferred.
Expanded qualification adds 31 controls with genuine mixed four-hour inputs, actual
committed exclusion/competing processes, exact-hour contracts, clocks and budgets.
First run retains nine failures/22 passes (102.92 s), complete report reviewed and all
289 identities match before repair. Eight hour/aggregate mismatch controls are wrongly
accepted; clock refusal occurs only after read-only verifier launch. Adapter-only
equality/early-clock repair preserves all controls and other 288 identities. Combined
rerun passes 58 (185.12 s); complete report reviewed and all 289 contract-repair
identities match. Main-side input-authentication focus is closed; no test remains active.
Next add genuine explicit-v5 typed intent/restart-exclusion controls before source
implementation. Failed fixtures, historical reds and distinct snapshots remain preserved.
At input-focus closure all 286 schema-repair identities remain unchanged. The later
typed overlay has focused evidence only; durable publication/completion still have no fallback.
Separate typed first run retains 34 import-masked failures (47.41 s); all 1,132 report
lines reviewed and 290 identities match. Two crash children exit at import, and six
budget controls fail before setup. No semantic refusal or crash boundary established.
Implementation run retains 33 fixture-upgrade failures/one v4 pass (34.61 s); complete
lossless exact-deduplicated report and all 291 identities reviewed. Neither crash child
launches; typed assertions remain masked. Retained diagnosis confirms independent-cursor
transaction visibility; read-only fixture check finds no v5 rollback residue, without
historical byte proof. Same-connection keyset paging and early typed history/budget
validation pass the unchanged 34-control repair run (125.03 s), complete report and
all 291 frozen identities reviewed. Genuine typed COMMIT/restart/lost-ack/post-COMMIT
input evidence is established, not entity launch/completion/recovery or wider acceptance.
Complete earlier 464-line successor documentation/privacy review and scoped wiki/
whitespace checks pass. Separate 24-control staged visibility/corruption/rollback,
budget-before-fetch, real keyset/tail-audit and rehashed-semantic module is fully
reviewed and five-target lint/format-clean. All 291 repair identities remain unchanged;
first-history run passes 24 (79.82 s), complete report/all 292 identities reviewed.
Complete 428-line successor wiki/privacy and 78-line operator deltas reviewed; scoped
wiki/whitespace checks pass. Separate combined typed/input/schema/receipt and six-module
original-ledger compatibility focus passes 336 (884.70 s) on the unchanged 292-identity
successor freeze. Standalone entity-verifier focus passes 141 (105.56 s); both complete
reports/all identities reviewed. Exclusion-only focused evidence is closed. Next add
separate genuine current-generation main completion-observation red controls before
source work; original typed receipt/input/intent and actual CLI shutdown must bind.
No ownership/authority/cursor transition or caller historical-publication fallback;
affected/full and entity launch/completion/recovery remain separate.
Retain all historical evidence.
Separate 44-control current-generation completion module is now fully reviewed and
lint/format-clean; all 292 closed focus identities unchanged. First retained run
retains 44 import-masked failures (342.12 s) on a distinct 293-identity freeze. Complete
409-line lossless review reconstructing all 1,783 report lines inspected; all frozen
identities match. Failed fixtures retained; no test remained active at first-red review.
Fixtures perform real original-bound
post-COMMIT verification and test-only supervised CLI launches under retained typed
exclusion, not service permission. No adapter refusal/green established; original-bound
read-only completion source work may begin without ownership/authority/cursor transitions
or historical-publication fallback.
Separate completion adapter now added after that review; complete source reviewed and
two-target lint/format passes, preserving all 293 first-red identities. Unchanged
44-control implementation rerun retains two helper failures / 42 passes (470.91 s) on
a distinct 294-identity freeze. Complete 81-line report/all identities reviewed; no test
remained active at implementation-result review. Both duplicate-`prelaunch` helper arguments mask adapter invocation for
missing-prelaunch and precommit substitution; no acceptance of those refusals. Next
rename only the positional helper parameter/default reference, leaving runtime/assertions
unchanged, then freeze and rerun all 44 controls. The adapter launches only a read-only
standalone verifier, binding actual originals,
post-COMMIT prelaunch and CLI/archive/shutdown/capture evidence, exact completion
core/transport counts and current generation. Ledger rows, authority, cursor and live
acknowledgment remain unchanged even on refusal. No entity writer/service permission
or historical-publication fallback; expanded completion and affected/full gates remain open.
Helper-only successor changes exactly two parameter/default-reference lines; complete
diff reviewed and lint/format passes. Runtime/assertions and other 293 implementation
identities unchanged. All-44 fixture-repair rerun passes 44 (471.51 s); complete three-line
report/all 294 identities reviewed. Previously masked prelaunch/precommit refusals now
execute without launch/mutation. Initial completion-observation focus is closed; no test
remains active at review. Successful fixtures cleaned; reports are durable evidence.
Next add separate genuine artifact-rebinding/non-mutation, clocks/counts/budgets and
independent data-corruption qualification. Retain both prior failure reports/fixtures/
freezes; expanded completion and affected/full remain open.
Separate 67-control artifact/data/non-mutation qualification source is fully reviewed
and three-target lint/format-clean. All 294 initial-focus identities unchanged; first
run passes 67 (353.73 s), exit 0, on the separate 295-identity freeze. Complete three-line
report/all identities reviewed, hash unchanged; all groups execute without setup masking.
Expanded completion-observation focus is closed, not combined/affected/full or service
acceptance. Targets include aliases/duplicate fields, actual
CLI statistics versus originals, structurally valid dictionaries versus actual files,
shutdown/count/clock/hash/budget contracts, genuine invalid Parquet and a competing lock
process. No contract validator substitutes for fresh standalone data evidence or durable
historical publication. Next freeze an unchanged 295-identity successor for combined main
focus (447 controls) and standalone verifier focus (141). Keep runtime/controls fixed until
both notifications, complete reports and identity checks; affected/full and entity writer/
service remain open. No test remained active at expanded-result review.
Combined standalone focus passes 141 (110.49 s), exit 0; complete four-line report/all
295 distinct-combined-freeze identities reviewed, hash unchanged. Main focus remains
unchanged and passes 447 (1729.40 s), exit 0; complete nine-line report/all 295 identities
reviewed, hash unchanged. Both focuses are complete; read-only completion/exclusion focus
closed, not affected/full or entity writer/service acceptance. No test remains active at
review. Next add genuine bounded original-generation publication-retention red controls
before source work; no release/authority/cursor/launch transition. Historical requests
must use authenticated retained original evidence, never caller dictionaries or today's
aggregate. Preserve the current-only adapter and closed freeze/reports. Supervised launch/
atomic completion-authority linkage, strict dispatch and audited original-clean resolution
remain separate subsequent slices.
Separate publication-retention module now adds 46 fully reviewed controls; new-target
lint/format and collection pass. All 295 closed-focus identities remain unchanged; distinct
296-identity first-red freeze adds only this module. Planned retention obtains current-only
completion internally and preserves exact original core/observation/audit without owner/
authority/cursor/grant/launch transitions. Accessor authenticates retained JSON only, never
ordinary-reopen runtime reconstruction. Real COMMIT/process-death/lost-ack and fresh-data/
original-artifact/budget/corruption first red retains 46 import-masked failures (402.36 s),
exit 1. Complete 1,772-line report, both direct child diagnostics and all 296 unchanged
identities reviewed. Children exit 1 at missing-module import rather than 87; no publication
COMMIT boundary or target semantics execute. At first-red review no test remained active
and publication/writer source was absent. Implement bounded immutable evidence/audit and genuine
same-transaction history next; preserve the unchanged current-only adapter and all 46
controls for a distinct successor rerun. Failed fixtures/report and operator baselines retained.
Separate retention/accessor and same-connection bounded typed-history authentication are now
implemented with initial focused evidence. Fresh current-only completion/original-artifact rechecks
precede immutable original envelope/core/observation/audit COMMIT; ordinary history/accessor
never reconstruct from runtime files or current aggregates. Early record/count/shared-byte/
audit budgets refuse without pruning. Success leaves ownership/authority/cursor/grants/live
acknowledgment unchanged; committed lost acknowledgment retains evidence and blocks the typed
original, not recovery/completion. Complete source/four-target Ruff lint/format reviewed.
Distinct 297-identity implementation freeze passes all unchanged 46 controls (629.02 s),
exit 0; complete three-line report/all frozen identities reviewed, hash unchanged. Initial
focus closed, not expanded/combined/affected/full. Successful fixtures cleaned by the unchanged
runner; no separately retained green child diagnostics claimed. Next add separate rehashed-
envelope/audit/SQL-byte/keyset-tail qualification and retain actual child diagnostics; preserve
all runtime/controls and historical failures. No test remains active at this review. Entity launch/
atomic completion/recovery/service and affected/full/platform/resource gates remain separate.
Separate expanded module now adds 77 fully reviewed controls for rehashed envelope/observation/
core/audit/canonical JSON, actual SQL UTF-8 byte budgets before any typed identifier/payload,
positive aggregate/count/equality boundaries, same-connection materialized keyset tails and
persisted-corruption reopen. One genuine original publication/audited block supplies staged
rollback-only corruption checks, not fabricated completed history. A separately frozen/reviewed
runner retains all successful/failed fixtures and actual child-diagnostic identities; the two
unchanged original process-death controls join the new module for 79 executions. Six-target
lint/format and 79-control collection pass; collection is not execution. All 297 closed source
identities/operator documents unchanged; distinct 298-identity successor adds only the new
module. Separate first run passes 79 (100.90 s), exit 0; complete four-line report,
29-line sidecar, both actual 93-byte child diagnostics and all 298 identities/separate runner/
operator baselines reviewed after notification. Children exit 87 at the selected actual
before/after publication COMMIT hooks, with absent-before/retained-after evidence and
unchanged BLOCKED original exclusion/raw cursor. All fixtures/historical failures retained;
no runtime/control/runner repair and no test remains active at this result review. Expanded
publication focus closed, not permission/affected/full. Reconcile/review the complete wiki/
privacy successor and fresh scoped checks, then close the distinct combined 570-main/
141-standalone focus before entity-writer work.
Complete 429-line expanded-green wiki/privacy successor delta and fresh six-target lint/
format, scoped audit/whitespace/operator/source checks pass. Distinct byte-identical
298-identity combined source freeze and separate runner freeze bind the prepared unchanged
570-main/141-standalone focuses. Both retain all fixtures and actual child diagnostics in
distinct reports. Complete 312-line prepared wiki/privacy review and fresh scoped/whitespace/
identity checks pass. Standalone passes 141 (109.28 s), exit 0; complete four-line report/
21-line sidecar and all 298 source identities/separate runner/operator baselines reviewed,
hash unchanged. Main passes 570 (2430.83 s), exit 0; complete ten-line report/45-line sidecar,
both actual 93-byte exit-87 publication diagnostics and all source/runner/operator identities
reviewed after notification, hash unchanged. Both focuses complete/all fixtures retained;
no test active or runtime/control/runner changes at result review. Combined compatibility
focused gate closed, not affected/full or entity permission. Review the complete successor
wiki/privacy delta/fresh checks before separate explicit-v5 writer red controls and source
work. Supervised launch/atomic completion-authority linkage, dispatch and audited original-
clean resolution remain unimplemented; retained publication never confers permission.
Combined-green 383-line wiki/privacy review/fresh checks acknowledged; original writer-control
bytes retained. A local explicit-v5 wrapper and actual crash/lock diagnostic retention now
preserve all 22 controls' assertions/parameterizations and shared default-v4 helpers. Complete
fixture delta and separate 74-line runner reviewed; two-target lint/format/collection pass.
Distinct 298-identity writer-red freeze changes only this control module, preserving the
other 297 identities and closed publication runner/operators. Complete 252-line prepared
wiki/privacy review and fresh scoped/whitespace/identity checks pass. Red completes with
22 import-masked failures (45.76 s), exit 1; complete 1,010-line report/36-line sidecar/four
actual exit-1 child diagnostics and all 298 source/runner/operator identities reviewed.
No crash hook or competing-lock child ran; all fixtures retained, runtime absent and no test
active. Complete active/result wiki/privacy/fresh-check review precedes runtime coding.
Successful typed history needs distinct completion evidence,
not replacement of immutable original publication or relaxed original intent bindings.
Selected existing-typed-event completion records and separate authority references, without
v5 schema or public-validator changes. Separate reviewed 20-control history module passes
lint/format/collection on a 299-identity red successor adding only that module; prior writer
controls/runtime/runner/operators unchanged. Complete successor wiki/privacy/fresh checks
and complete red/identity review precede runtime coding; expanded history/recovery remains open.
Complete 282-line successor wiki/privacy/fresh-check review passes. Separate red retains
four failures/16 setup errors (3.52 s), exit 1, all import-masked; complete report/19-line
sidecar/all 299 unchanged source identities reviewed, all fixtures retained. No child
diagnostics produced or semantic assertions executed; runtime coding follows this scoped red.
The complete 184-line red-result wiki successor is acknowledged. Five-file Linux runtime
successor now reviewed/formatted with eight-target lint/format passing, but not executed or
accepted. Distinct completion records and authority references preserve original publication,
schema and public contracts. Duplicate-completed-receipt refusal/authority keyset-tail review
repairs do not change frozen controls. Retained-completion acknowledgment resolution still
refuses; freeze/run the unchanged 42 controls, fully review evidence/identities before repair.
Strict dispatch, expanded recovery/affected/full/S3/resources and native-Mac remain separate.
First runtime result is reviewed: 40 passes/two failures (244.11 s), exit 1; complete report/
sidecar/all seven genuine child diagnostics and all 301 unchanged identities checked. Original
publication stays blocked because the test's January recovery clock predates its real restart;
fix only the scoped fixture clock and add an early rollback control. Committed-completion
acknowledgment resolution needs distinct immutable evidence, not overwritten originals. No test
active or 42-control green; complete result wiki/privacy/fresh checks precede repair successors.
Complete 287-line result review/fresh checks acknowledged; original history bytes preserved.
Scoped synthetic reopen-clock/import-format successor preserves every assertion/parameterization,
helper and other function. Separate reviewed 407-line/29-control resolution module and unchanged
history collection total 49; four-target lint/format pass. Distinct 302-identity control-red
freeze preserves other 300 runtime-first identities, frozen writer/runner/operators and runtime.
Review the complete red/evidence/identities before implementing separate immutable resolution
records, early block-clock refusal and after-COMMIT uncertainty. No runtime repair or green yet.
Resolution-control red reviewed: 25 passes/nine failures/15 setup errors (343.58 s), exit 1.
Complete 1,277-line report/20-line sidecar, actual retained verifier captures and all 302
source/runner/operator identities reviewed. Scoped fixture clock passes; early block-clock
refusal is late, committed resolution is blanket-refused, and original-clean recovery's
after-COMMIT failure leaves DRAINING. Preserve this failed ledger/report; artifact/budget
semantics remain masked. No run active. Result wiki/privacy/fresh checks precede runtime repair.
Complete 233-line result successor acknowledged; original runtime bytes preserved. Separate
450-line immutable-resolution module and complete 343-line two-file integration delta reviewed;
eight-target lint/format pass, AST unchanged by formatting except unused import removal.
303-identity runtime freeze changes only entity intent/writer and adds resolution; other 300
red identities and all controls/runner/operators/schema/public/standalone contracts unchanged.
71-control writer/history/resolution qualification is prepared, not run/green. Review complete
evidence and identities before any further changes, then rerun closed publication overflow
and add genuine completion-death/SQL-tail/forward-evolution qualification. Broader gates stay open.
Complete 470-line prepared wiki/privacy review and fresh scoped/whitespace/all-identity checks
pass; distinct 71-control runtime qualification is active, with no result yet. Freeze runtime/
controls/runner until notification and complete report/sidecar/actual-child/identity review.
First run reviewed: 69 passes/two failures (516.86 s), exit 1. Full 67-line report/50-line sidecar,
four actual exit-87 crash diagnostics/three exit-88 lock diagnostics and all 303 source/runner/
operator identities authenticate. Original 42 controls pass; two positive resolution controls
stop on their nonexistent verifier flag, leaving later immutable-byte/table/reopen assertions
unexecuted. Direct standalone module plus canonical completion request is the unchanged real
contract. Preserve original controls/report/fixtures; make a distinct exact-command/request
assertion correction with runtime unchanged, then rerun all 71 and closed publication controls.
No run active or full 71-control green; wider gates remain open.
Complete 241-line result wiki/privacy review and fresh checks acknowledged. Original 407-line
resolution controls preserved; complete 31-line contract-only correction reviewed, preserving
all other bytes/AST/assertions/parameterizations. Exact standalone command, canonical completion
request and actual manifest replace the nonexistent flag. Eight-target lint/format and all
71-control collection pass; distinct 303-identity freeze changes only this module, preserving
other 302 sources and runner/operators. Distinct all-71 rerun is prepared, not active/green;
closed publication overflow/process-death qualification requires separate retained evidence.
Complete 248-line prepared-final wiki/privacy review and fresh checks pass. Distinct frozen
all-71 command-contract rerun is active, with no result; keep runtime/controls/runner unchanged.
Publication follow-through reviews both unchanged modules in full; six-target lint/format and
123-control collection pass. No publication execution yet; launch after all-71 evidence review.
Command-contract rerun reviewed: all 71 pass (521.59 s), exit 0. Complete three-line report/
50-line sidecar/seven actual diagnostics and all 303 source/runner/operator identities checked.
Both corrected positives now pass their immutable-original/table/data/artifact/reopen assertions.
Initial writer/history/resolution focus closed; all fixtures/original controls/historical reds
preserved and no test active. Complete result wiki/privacy/fresh checks precede the unchanged
123-control publication affected rerun; expanded completion-death/SQL-tail/forward-evolution,
affected/full/service and wider Linux/S3/resources/native-Mac gates remain open.
Complete 266-line all-71 result/57-line index reconciliation wiki/privacy review and fresh
checks acknowledged; renewed six-target lint/format pass. Distinct byte-identical 303-identity
source freeze plus separate unchanged runner freeze prepare the retained 123-control publication
affected rerun. No runtime/control/operator change, execution/result or broader acceptance yet.
Complete 233-line prepared wiki/privacy review and fresh checks pass; frozen 123-control
publication affected rerun is active. No result; runtime/controls/runner remain unchanged.
Publication result reviewed: all 123 pass (708.64 s), exit 0; complete four-line report/29-line
sidecar/two actual 93-byte exit-87 publication COMMIT diagnostics and all 303 source/runner/
operator identities authenticated unchanged. All fixtures/historical failures remain intact;
no run active. Only publication affected follow-through closes. Result wiki/privacy/fresh checks
precede separate genuine completion-process-death/stronger SQL-tail/forward-evolution controls;
entity-wide affected/full, original-bound maintenance/service and wider Linux gates stay open.
Complete 254-line publication-result wiki/privacy review/fresh checks acknowledged. Separate
345-line/12-control genuine completion-process-death successor is fully reviewed; formatting
preserves AST and child parsing/six-target lint/format/collection pass. Initialization/replay,
original-clean recovery and acknowledgment resolution retain actual hashed boundary captures
and test verified/pre-COMMIT/committed all-or-none history without raw/reader release. Scoped
synthetic reopen clock does not authorize rollback. Distinct 304-identity source freeze adds
only the new module; all 303 prior sources and runner/operators unchanged. First run is prepared,
not active/qualified. Complete wiki/privacy/fresh checks precede launch; full retained report/
sidecar/actual-child/boundary-capture/all-identity review precedes further changes. Stronger SQL-
tail/forward-evolution, maintenance/service/integration and wider Linux gates remain open.
Complete 316-line prepared wiki/privacy review/fresh checks pass. Frozen 12-control completion-
process-death first run is active; no result. Runtime/controls/runner stay fixed until notification
and complete actual report/sidecar/child/boundary-capture/all-identity review.
Completion-death result reviewed: all 12 pass (283.57 s), exit 0; complete three-line report/
68-line sidecar/all 12 actual exit-89 diagnostics and hash-bound captures authenticated.
Read-only inspection validates 48 actual observation-artifact groups/72 immutable CLI archive
records; all 545 fixture files and 304 source/runner/operator identities unchanged. Eight
uncommitted deaths use distinct fresh recovery observations; four committed deaths retain
their actual atomic boundary results. Raw cursor/history, reader/grant and live authority
boundaries hold. No test active or runtime/control change indicated; only this focused gate
closes. Complete result wiki/privacy/fresh checks precede a separate stronger completion/
resolution SQL-budget-before-fetch/keyset-tail successor; forward-evolution/maintenance/
service/staged integration and wider Linux/S3/resources/native-Mac gates remain open.
Completion/resolution SQL-budget/keyset successor is prepared only: exact 531-line formatting/
AST checks and complete review identify new-module fixture/guard defects before execution.
Complete 98-line correction preserves all test assertions/parameterizations and other helpers;
original drafts remain retained. Final 548-line/44-control module, eight-target lint/format
and final collection pass. Two genuine completion/resolution/publication originals underpin
early typed-fetch budgets, exact positive caps, one-row real SQL sequence tails and full-history
audit tails. Typed independent cursors remain forbidden; unrelated reader validation and the
writer's actual receipt prerequisite are not disabled. Every corruption/guard failure retains
rollback. Distinct 305-identity freeze adds only this new module; 304 prior sources and runner/
operators unchanged. No run active/result or runtime repair. Complete prepared wiki/privacy/
fresh checks precede launch, and full retained evidence/identity review precedes further changes.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py -->
Complete 480-line prepared/207-line active wiki/privacy reviews and fresh checks passed.
The frozen history run now passes all 44 (62.53 s), exit 0; complete report/sidecar and
ten actual verifier groups/two CLI completions/twelve immutable archives reviewed. Read-only
inspection authenticates original publication/completion/resolution/blocker/authority/cursor
links; 14 actual non-origin entity events and raw/reader/live-authority boundaries hold.
Both guessed-table/count inspection diagnostics remain retained; corrected complete review
passes with all 84 retained files/one symlink and 305 source/runner/operator identities unchanged.
No runtime/test/fixture change or active test; only this focused gate closes. Complete result
wiki/privacy/fresh checks precede separate raw-cursor/authority-forward-evolution controls;
original-bound maintenance/service, staged integration and wider Linux gates remain open.
Separate raw-cursor/authority forward-history preparation-time record: complete
closed-history result wiki/privacy/fresh checks precede full draft/helper/API/clock/anchor/scope
review. Retained 261-line draft receives only demonstrated request-clock/anchor-shape fixes,
real final-CLI semantic comparison and lint context consolidation. Complete 67-line correction/
419-line module, eight-target lint/format and corrected 23-control collection pass. Incorrect
system-interpreter collection diagnostic retained; no semantic test executed. Distinct 306-
identity freeze adds only this module; all 305 predecessors/runner/operators/history fixtures
unchanged. Full prepared wiki/privacy/fresh checks precede frozen execution; complete genuine
raw/entity artifact/ledger/fixture/identity review precedes closure or runtime repair.
Complete 340-line prepared/210-line active wiki/privacy reviews and fresh checks passed before
result review. Frozen forward-history run now passes all 23 (87.45 s), exit 0; complete three-
line report/19-line sidecar and independent original/artifact/ledger review authenticate 16
verifier groups/four CLI completions/34 immutable archives. Six authority rows reach generation
four; original publication/completion/resolution/blocker/raw-cursor links stay unchanged. Final
raw proof requires OPEN at the advanced fixed-hour cursor, not the inspection's guessed DRAINING;
one reader stays WAITING without grants/live authority. Original failed inspection/source and
separate read-only diagnostic remain retained; only inspection expectations corrected. Complete
12-line final inspection passes; all 150 retained files/one symlink and 306 sources/runner/
operators/closed-history fixture identities unchanged. No runtime/control/fixture change or
active test; only forward-history focus closes. Complete result wiki/privacy/fresh checks precede
separate original-bound recovery/maintenance and strict Linux entity dispatch controls; staged
both-runtime integration, wider Linux/S3/resources/native-Mac and dcc-02–05 remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_forward_history.py -->
Subsequent strict Linux service focus now closes with 71 passes and independent retained
evidence/identity inspection, without rerunning the accepted forward fixture. Only that
focus closes; pending-publication/original-bound maintenance and staged integration remain
open. Current result and preserved inspection diagnostics:
[[wiki/work/dbt-compaction-coordination/verification#Executed strict entity service result — focused gate closed]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_service.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_verification.py; ../Wintap-PyUtil/tests/test_coordination_entity_observations.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_observation_qualification.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_intents.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_intent_history.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_observations.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_completion.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_qualification.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publications.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_publication.py; ../Wintap-PyUtil/wintappy/coordination/entity_intent.py §validate_history -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py -->

**Root-shape boundary:** `WINTAP_DBT_RAW_SENSOR_DATASET` is the parent containing
`raw_sensor/`; the compactor's `--source-root` is the direct `raw_sensor` event
root. The compacted override/CLI destination are direct event roots. Canonicalize
the bindings consistently rather than appending `raw_sensor` twice.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/paths.sql §raw_sensor_path/compacted_root_path; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §parser -->

**Report boundary:** inspect the current `hours`, `partitions`, `delete_source`
and `deletion_failures` evidence as well as exit status. The CLI currently returns
2 for `completed_with_deletion_errors`. A top-level `completed` can coexist with
an event/hour marked `skipped_existing`; inspect every configured event/hour and
require the ledger's verified receipt or explicit reconciliation for a skip.
Capture stdout/stderr as well as parsed JSON because error reports can be on
stderr. Integrate `reconcile-delete` through exclusive recovery.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/main; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py §process_hours -->

**Checkpoint/recovery boundary:** entity-only replay can publish `completed` with
raw processing `not_run`, and DBT accepts `completed_with_deletion_errors`.
Neither is writer-success evidence. Entity-enabled `reconcile-delete` now publishes
checkpoints; use explicit exclusive recovery for all three phases.
Fixed-hour metrics can be overwritten by replay, so retain the migration receipt
and coordinator-to-CLI run-ID mapping independently using the R4 local archive.
`checkpoints-repair` validates original evidence and current/historical authority
before republishing original rows; missing evidence stays blocked. It acquires no
grant and cannot reopen a ledger. R1–R3 now have regression evidence for freshness,
SQL validation and provenance; those passes alone are not recovery certification.
Current
`entities-verify` success or checkpoint presence alone is insufficient.
<!-- GROUND_TRUTH: wiki/work/dbt-compaction-coordination/implementation-review.md; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows -->

Create the Python package `wintappy/coordination/` with `protocol.py`, `ledger.py`,
`coordinator.py`, `client.py` and `__init__.py`; JSON/crontab examples under
`config/`; four focused `tests/test_coordination_*.py` modules. Update Makefile,
offline config checks and user/operator READMEs. The exact artifact table,
once-per-minute cron entry and config example are in the design.

Server runtime artifacts are the lock, DuckDB/WAL, per-run command/result/logs
and tick log. S3 messages are requests/grants/releases/cancellations plus advisory
status outside telemetry roots. Remote clients retain per-job request/grant/result
and pending terminal-message JSON. Local-only builds create ordinary DBT outputs.

## Implementation units and done checklist

Current Linux overlay implements the service/client paths and initial recovery, with
real local lifetime/Makefile controls. It does not change the unit-level unchecked
gates below. New evidence and unfinished broader recovery:
[[wiki/work/dbt-compaction-coordination/verification#Linux integration continuation — slices D/E, qualification pending]].

- [x] **dcc-01 — Protocol and durable ledger (first slice).** Implement message
  identity/binding, schema/init, reservations, writer intent, outbox and terminal
  records. Verified completion/cursor/reopening remain later integration.
  Prove transaction ordering/restart behavior with real local DuckDB and fake S3.
- [ ] **dcc-02 — Tick and scheduling.** Implement local lock, message ingestion,
  shared admission, writer priority, UTC cursor/grace/catch-up and advisory status.
  Use supervised fake children to prove reader/writer exclusion and crash handling.
  Require execution/configuration-receipt binding and secret-exclusion checks
  before accepting the service-level launch/completion path.
- [ ] **dcc-03 — DBT wrapper and local compatibility.** Integrate root-aware routing
  into build/source/test/docs targets; span preflight through child shutdown;
  implement polling, cancellation and durable release retry. Prove the local-only
  full-build baseline and mixed-root routing.
- [ ] **dcc-04 — Compactor and operations.** Invoke the qualified isolated CLI for
  one eligible hour, validate full outcomes, persist receipts/cursor and implement
  status/manual reader release/hour reconciliation. Add cron/config and setup docs.
  Include checkpoint repair, independent migration receipts and exclusive entity
  maintenance; address the review's validation/provenance recovery prerequisites.
- [ ] **dcc-05 — Integrated qualification and documentation.** Exercise overlapping
  readers, due writer, queued reader and failure recovery on fresh isolated S3
  fixtures. Record observed polling latency and complete regressions; promote
  implemented behavior to the canonical ETL guide.

## Testing expectations

| Gate | Required evidence |
|---|---|
| Concurrency | Two shared readers overlap; due writer waits for both; a later reader remains queued; no writer interval overlaps any outstanding reservation. |
| Diagnostic boundary | Preserve the explicit utility exception without weakening DBT/shared-command grant assertions or ledger/maintenance protections. Live overlap, warning/race and load qualification belongs to the utility plan, not dcc-02 acceptance. |
| Grant durability | Crash before/after COMMIT and lost PUT acknowledgment; pending grants survive and are republished with identical identities. |
| Message ordering | Duplicates, cancellation before request, delayed grant after cancellation, early terminal delivery and conflicting content preserve ownership correctly. |
| Writer durability | Duplicate ticks exit busy; crashes around launch, surviving children and partial migration leave unresolved writes blocked; missing ledger refuses operation. No duplicate launch. |
| Execution/configuration receipt | Resolve defaults/overrides/allowed environment once; bind actual executable/runtime/arguments, roots, hour/run IDs, events, entity policy, deletion and budgets to the pre-launch intent. Missing/changed/oversized receipts or scope/command mismatches cannot authorize launch/completion. Synthetic secrets never appear in persisted receipt/intent/diagnostics; an environment-omitting manifest or exit zero cannot satisfy the gate. |
| DBT lifetime | Preflight failure, build/test failure, Ctrl-C, child-tree termination and release upload failure exercise the complete reservation lifetime. |
| Local baseline | Full raw-only build without AWS/coordination/entity settings, compacted directory or installed compactor; existing local model/schema/results contract and zero coordination calls/state. |
| Routing | Unused AWS/coordination settings keep local mode; each active S3 raw/compacted/entity/metrics override selects coordination. An unused remote metrics override with entities disabled causes neither coordination nor S3 setup. |
| Scheduling | UTC midnight/grace boundary, missed ticks, multiple backlog hours, empty hour and cursor persistence. |
| Writer results | Successful migration, exit-zero skip/mixed completed report, deletion error, failed entity phase, missing/malformed report and recovery dispositions. |
| Checkpoint/recovery | Failure after raw deletion stays blocked; reconciliation without metrics cannot reopen; replay preserves independent migration receipts. Snapshot rollback/corruption and incremental bootstrap provenance have regression evidence. |
| Entity coverage | Matching namespace/hosts/policy/ceiling; missing checkpoint in requested window fails and releases, without writer-wait deadlock or silent window changes. |
| Polling | Controlled clock proves same-tick grant publication, configured client interval and no extra release acknowledgment; integrated run reports actual delays separately from DBT/writer work. |

Use controllable clocks for timing tests. After the new modules exist, focused
commands from PyUtil are:

```sh
uv run --locked --dev pytest -q tests/test_coordination_*.py
uv run --locked --dev pytest -q tests/test_dbt_source_validation.py tests/test_compacted_inputs.py tests/test_process_entities.py
```

Run the full main suite after integration, plus the standalone compactor suite
from its own locked environment when its integration changes warrant it. Qualify
the real endpoint with feature-owned disposable fixtures and explicit test roots.
Existing compactor/entity results are background evidence, not proof of the new
coordination protocol. The original handoff preceded runtime tests; current local
Linux controls and remaining qualification are recorded in verification.

## Deployment inputs and closeout

Supply the dataset ID, coordination/raw/compacted roots, first unfinished UTC
hour, event allowlist, AWS profile, absolute server executable/state/log paths
and resource limits. If durable entities are enabled, also supply initialized
entity roots, expected hosts, namespace, budgets, processing-metrics root and
matching identity policy/ceiling. Measure incremental
snapshot read/hash/rewrite cost under the chosen server budgets; imported large-budget
three-day bootstrap results do not qualify these defaults. Confirm supported client
platforms when implementing process-tree shutdown. Defaults remain those in the
design; configuration values are supplied per environment.

At each unit, update `implementation_plan.md` and `verification.md` in this
feature folder with commands, results and remaining gaps, and append substantial
progress to `wiki/log.md`. Keep the diagram/design synchronized with implemented
behavior; promote stable facts into [[wiki/workflow/wintap-etl-data-flow]]. Apply
the root AGENTS.md privacy rule to persisted evidence. Final closeout should name
the owning code/wiki commits, runtime qualification and deployment status.

### November 14 continuation: local normal completion, service remains open

Review repairs pass 493 full-main/387 full-standalone tests before receipt changes.
The later receipt revision passes 194 combined coordination tests, including
44 receipt/launch cases; eight recorded hardening failures precede repairs. Its
full-main regression passes 537 tests (three skips). Use `execution.prepare_execution` and
`writer.execute_prepared`, not the synthetic tick callback seam, for qualified
local launch. Immutable receipts live in `<state>/executions/<coordinator-run-id>/`;
the phase archive remains separate and original records are never overwritten.

Missing/mismatched pre-intent evidence refuses launch. After-intent uncertainty,
including lost COMMIT acknowledgment, remains blocked. Individual engine ceilings
do not establish total RSS/disk acceptance. The standalone process never opens the
ledger. Separate read-only data/authority verification and receipt/intent/shutdown
authentication pass 259 standalone and 204 main affected tests, after eight
additional active-path repairs. The frozen verifier-foundation revision passes
547 full-main tests (three skips) and 431 full-standalone tests (two skips), before
ledger integration. Verification success does not reopen.

Ledger v2 now implements explicit confirmed compatible upgrade, retained
authority-check proofs/audits and separately supervised verified initialization.
Initialization requires a reason, no baseline and zero readers. Entity admission
and writer intent require a fresh check in the same locked session; reopen/failure
clears freshness and successful intent consumes it. Upgrades preserve reservations,
outbox, tombstones, ledger/run identities and audits; unresolved intents stay blocked
without fabricated receipts. Main entity verification now passes real local
migration/checkpoint checks against the retained anchor but leaves high-water,
cursor and permissions unchanged. Forward lineage passes; rollback/forks refuse.
The latest focus passes 236 main and 299 standalone tests. Frozen full authority
regressions pass 579 main tests (three skips) and 439 standalone tests (two skips).
Both notifications arrived before completion/history work; the runtime freeze is
lifted for that next slice, which these results do not cover.

The v3 retained-history/normal-completion prototype passes 46 repaired completion/
upgrade and 24 independent semantic/compatibility/paging/secret controls, before
three final budget/clock red/green controls. Ten active failures precede repairs.
Full standalone of the final revision passes 439 tests (two skips); combined main
focus passes 298 tests. Full main passes 641 tests (three skips) in 1055.19 s on
the unchanged revision; source/runtime-lock hashes match the prepared manifest.
Both full notifications arrived before lifting the runtime/test freeze. The local
independently verified completion-evidence/run/high-water/exact-hour-cursor/backlog-
mode transaction now has complete regression evidence, not service acceptance.
Preserve `execute_prepared`'s conservative
blocking semantics: normal completion needs a same-lock clean-live-intent path that
obtains fresh verification internally. Previously blocked/restart-blocked runs require
explicit audited recovery; passing caller-supplied reports cannot reopen them.
Proof budgets refuse rather than prune;
whole-ledger-plus-authority rollback still requires independently retained external
evidence/exclusion. Commands and red/green attribution:
[[wiki/work/dbt-compaction-coordination/verification#Completion slice C — ledger-v2 authority integration]].
[[wiki/work/dbt-compaction-coordination/verification#Completion slice C — initial ledger-v3 history and atomic completion]]
records v3 scope and all ten active repair controls; it does not accept dcc-02–05.
Origin/proof/run/audit/cursor integrity and the prior-completion clock floor are
local checks, not coherent restored-store/global-clock freshness. Genuine three-hour
instrumented paging does not qualify representative retained-state sizing.
Linux service/client integration is now authorized independently of the native-Mac
worker's pending shutdown gate; platform skips and injected remote sessions are not
actual-platform/endpoint evidence.
The human selected a human-run Mac harness. Its prepared exact-revision offline
baseline and later backend gate are in
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. The original Mac
attempt was blocked before tests by packaging; the corrective-revision baseline
passes 169 main/267 standalone tests with 129 reviewed main Linux-only skips.
No supported reader-shutdown result is inferred from that offline baseline.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/execution.py; ../Wintap-PyUtil/wintappy/coordination/writer.py; ../Wintap-PyUtil/tests/test_coordination_execution.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/wintappy/coordination/verification.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_validate_authority_checks/_require_entity_authority; ../Wintap-PyUtil/wintappy/coordination/authority.py; ../Wintap-PyUtil/tests/test_coordination_authority.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/writer.py §execute_and_complete_prepared; ../Wintap-PyUtil/tests/test_coordination_completion.py; ../Wintap-PyUtil/tests/test_coordination_completion_controls.py -->
