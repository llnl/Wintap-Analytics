---
title: "Verification: Scheduled DBT and Compaction Coordination"
type: concept
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - wiki/work/dbt-compaction-coordination/implementation-review.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entities.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_freshness.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_cli.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py
  - ../Wintap-PyUtil/tests/test_process_entities.py
  - ../Wintap-PyUtil/tests/test_entity_freshness.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py
  - ../Wintap-PyUtil/wintap_dbt/macros/entity_authority.sql
  - ../Wintap-PyUtil/tests/test_dbt_source_validation.py
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../Wintap-PyUtil/tests/test_checkpoint_repair.py
  - ../Wintap-PyUtil/tests/test_effective_input_roots.py
  - ../Wintap-PyUtil/tests/test_coordination_protocol.py
  - ../Wintap-PyUtil/tests/test_coordination_ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/protocol.py
  - ../Wintap-PyUtil/wintappy/coordination/ledger.py
  - ../Wintap-PyUtil/wintappy/coordination/coordinator.py
  - ../Wintap-PyUtil/tests/test_coordination_tick.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/execution.py
  - ../Wintap-PyUtil/wintappy/coordination/writer.py
  - ../Wintap-PyUtil/tests/test_coordination_execution.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/verification.py
  - ../Wintap-PyUtil/wintappy/coordination/authority.py
  - ../Wintap-PyUtil/wintappy/coordination/completion.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_completion.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_completion_qualification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publications.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_publication.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py
  - ../Wintap-PyUtil/tests/test_coordination_completion.py
  - ../Wintap-PyUtil/tests/test_coordination_completion_controls.py
  - ../Wintap-PyUtil/tests/test_coordination_authority.py
  - ../Wintap-PyUtil/tests/test_coordination_verification.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_completion_verifier.py
  - ../Wintap-PyUtil/scripts/dcc_macos_baseline.py
  - ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json
  - ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py
  - ../Wintap-PyUtil/.gitignore
  - ../Wintap-PyUtil/uv.lock
  - ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py
  - ../Wintap-PyUtil/wintappy/coordination/service.py
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/wintappy/coordination/recovery.py
  - ../Wintap-PyUtil/wintappy/coordination/inputs.py
  - ../Wintap-PyUtil/tests/test_coordination_service.py
  - ../Wintap-PyUtil/tests/test_coordination_client.py
  - ../Wintap-PyUtil/tests/test_coordination_recovery.py
  - ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py
  - ../Wintap-PyUtil/tests/test_coordination_local_route.py
  - ../Wintap-PyUtil/wintappy/coordination/maintenance.py
  - ../Wintap-PyUtil/tests/test_coordination_maintenance.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_repaired_completion.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_deletion_recovery.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_deletion_completion.py
  - ../Wintap-PyUtil/tests/test_coordination_deletion_recovery.py
  - ../Wintap-PyUtil/wintappy/coordination/retry.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/retry_verifier.py
  - ../Wintap-PyUtil/tests/test_coordination_retry.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_retry_verifier.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_verification.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_observations.py
  - ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_resolution.py
  - ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py
  - ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/MACOS.md
  - ../Wintap-PyUtil/tests/test_coordination_entity_forward_history.py
policy: agent-editable
last_validated: 2026-11-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/dbt-compaction-coordination; ../Wintap-PyUtil/tests; ../Wintap-PyUtil/extras/raw-sensor-compact/tests
tags: [feature-work, verification, coordination, review, regression]
---

# Verification: Scheduled DBT and Compaction Coordination

## Independent submitted review and native-Mac feasibility — November 15

Submitted PyUtil `123b9d36705a5d9c356724d007b28bac224605a6` and Analytics
`3f11d13` / `ee9c27a75397702700c7f969b39685edc91a2586` matched their submitted
upstream heads. The independent Git-only review retained both source snapshots,
authenticated report hashes and all **365** reviewed source hashes; both submitted
ranges passed `git diff --check`. The worker's Linux 71/307 execution reports retain
their original scope below: collection/source/report review is not an independent
re-execution of its private Linux fixtures.

The human approved isolated implementation/review work including scoped native-Mac
PyUtil changes and the Analytics utility. Separate worktrees from `123b9d3` and
`ee9c27a` keep the busy producer checkout/environments untouched. No deployment,
cron installation, real-dataset mutation, commit or push is authorized. Pending
publication recovery remains with the producer worker. Concrete S3/resource fixtures,
roots and access still need explicit approval.
<!-- SOURCE: Human implementation approval, conversation 2026-11-15. -->

### Portable submitted review and provisioned rerun

`review-results.json`, `portable-review-smoke.txt` and
`submitted-scope-collection.txt` are retained in the private submitted-review
archive. On native Python 3.12.12/main DuckDB 1.5.6, protocol/ledger/local-route/
effective-root smoke passes **76 tests/zero skips in 44.63 s**. The exact 13-module
submitted scope collects **307 tests**, including 71 entity-service controls; this
does not execute the Linux suite on Mac. All 365 source identities match before/after.

Provisioned isolated main and standalone environments with:

```sh
uv sync --locked --offline --dev --python 3.12
# Separately from extras/raw-sensor-compact/ with its own lock/environment:
uv sync --locked --offline --dev --python 3.12
```

Main uses DuckDB 1.5.6; standalone uses 2.0.0. Locks/manifests remain unchanged.
From PyUtil, with a sanitized environment and 1,200-second outer ceiling:

```sh
.venv/bin/python -m pytest -q -ra \
  tests/test_coordination_protocol.py tests/test_coordination_ledger.py \
  tests/test_coordination_execution.py tests/test_coordination_tick.py \
  tests/test_coordination_authority.py
```

| Retained evidence | Result |
|---|---|
| `producer-portable.stdout.txt` / `.json` | Initial **24 failures/145 passes/25 skips in 19.30 s**. All 24 failures are exactly `Qualified standalone execution runtime unavailable`: standalone had not yet been provisioned. No other error class; source unchanged. |
| `producer-portable-provisioned.stdout.txt` / `.json` | After standalone provisioning, **169 passes/25 skips in 14.58 s**, exit 0. Full 22-line stdout/empty stderr inspected after completion notification; all **83** recorded source/lock identities match before/after and current files. |

Reviewed skips: two Linux writer-subreaper execution controls, three Linux procfs/
subreaper tick controls and twenty Linux authority/writer/verifier-supervision
controls. These were not run and cannot qualify Mac shutdown. This five-module
rerun is neither the old nine-module baseline nor full latest-HEAD regression.
Provisioned report SHA-256:
`5bbcd06b89e5cbc720c2ee033b397872fcff9d4ad7925a547686e6b967d52c5c`.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_execution.py; ../Wintap-PyUtil/tests/test_coordination_tick.py; ../Wintap-PyUtil/tests/test_coordination_authority.py -->

### Actual-Mac restriction/bootstrap feasibility

From the isolated PyUtil main environment:

```sh
.venv/bin/python -B scripts/dcc_macos_restriction_probe.py
```

Actual Mac kqueue `NOTE_TRACK` returns `ENOTSUP`. A native no-fork sandbox denies
both `os.fork` and subprocess spawn with `EPERM`; plain DBT `Manifest()` also
refuses because Python must start its resource tracker. Prestarting that helper
before restriction permits a genuine fixed synthetic DBT **build (three passes)**
and **test (two passes)**. Python is 3.12.12; DBT core/adapters/duckdb are
1.12.3/1.24.5/1.9.6, main DuckDB 1.5.6. No repository DBT project, S3 or real data is used.

Both first and formatted probes exit 0. The formatted run finishes in **4.288 s**;
full stdout/empty stderr inspected, with script/main-lock/manifest identities
unchanged before/after. Original formatted-script SHA-256:
`833dfb8dcef173508aec773fd4bb26dd272c8f084ffdf2efbee47090c6b030ed`.
Retained report: `native-mac-restriction-formatted.stdout.txt`, SHA-256
`fe7178ebf3d2cce0569763b99c4d112028919fcab4030431352f5ac3a186ed67`.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py; ../Wintap-PyUtil/uv.lock -->

The final audit's separate import-order/explicit-default style successor reruns the
same `.venv/bin/python -B scripts/dcc_macos_restriction_probe.py` command: exit 0 in
**4.269 s**, genuine synthetic build three/test two passes. Full 38-line stdout/empty
stderr reviewed; all three successor script/main-lock/manifest identities match
before/after/current files. `native-mac-restriction-style.stdout.txt` SHA-256:
`791e328afa780c7dcc864033422f9699aa21a07393a8e7a310c38373be3324f6`.
Current probe SHA-256:
`1db8e762234570653c64ce86efbb17886fed9a9f4fe9a22027566ed4bd37a17b`.
The original probe and ten original utility source/lock files remain authenticated
in an 11-file private pre-polish snapshot; original reports are never replaced.
Scoped final source/wiki/privacy checks and retained baseline lint findings:
[[wiki/work/compaction-status-utility/verification#Final scoped audit and style successor — November 15]].

**Feasibility only:** deprecated Apple sandbox APIs and private CPython tracker/
finalizer seams are not selected production dependencies. The experiment has no
closed lifetime tracker, client/backend integration, detached-child/inheritance/
delegation controls, interruption or wrapper-death qualification. Its ordinary
synthetic cleanup and timeout are not complete-shutdown proof; the report explicitly
sets `native_shutdown_qualified: false`. No reservation/grant/release is published.
Stop for dependency/design review before production wiring; uncertain ownership
remains reserved/`BLOCKED`. The native tension stays open:
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]].

Utility evidence is separate:
[[wiki/work/compaction-status-utility/verification#Authorized advisory implementation — November 15]].
Historical **880 main/three skips** and **554 standalone/two skips** predate later
entity changes. Submitted 307 Linux passes close only their service-affected scope;
no full latest-HEAD, S3/resources, native shutdown, dcc-02–05 or rollout acceptance.

## Linux integration continuation — slices D/E, qualification pending

Human authorized finishing Linux independently of the native Mac worker's unresolved
shutdown backend. This section records the **historical uncommitted overlay** on
PyUtil `fab647f` / Analytics `65bff3d`; it is now included in submitted `123b9d3`.
Use the independent submitted/native review above for the current worktree boundary.
The accepted exact-revision Mac baseline and original omitted-lockfile failure remain
unchanged and separately attributed.

### Implemented Linux paths

- `service.py` validates explicit configuration offline, ingests complete bounded
  terminal-first listings, observes evolving UTC plus the prior-completion floor,
  and holds the same persistent ledger lock through receipt-bound writer execution,
  independent standalone verification and atomic completion. Queued grants follow
  completion COMMIT and a fresh clock check; due backlog retains writer priority.
  The conservative callback tick and `execute_prepared` remain unchanged in policy.
- `client.py` classifies only active roots before initializing coordination. Local
  DBT invokes ordinary commands directly. Coordinated readers retain their transport,
  exact request/grant and launch marker; source preflight and build share one grant.
  Cancellation/release retries preserve immutable bytes and never relaunch work.
  SIGINT/SIGTERM preserve 130/143 and release only after authenticating durable exact
  command-bound child-shutdown evidence; abrupt death or uncertainty retains ownership.
- `recovery.py` records explicitly confirmed operator reader cancellation and its
  exact terminal/identity-bound audit. Original clean complete blocked executions
  can resolve only through fresh original archive/data/authority/shutdown verification
  and atomic completion plus recovery audit. Reader/writer recovery audits are checked
  on reopen. Confirmation is not data evidence and never manufactures an exit outcome.
  A separately audited exact checkpoint repair now supports the narrow recorded
  exit-2 publication-failure case described below; broader recovery remains open.
- Private atomic `<state>/status.json` is advisory only: explicit observation time,
  bounded mode/cursor/count/high-water and job/run/maintenance summaries, 100 records per kind,
  1 MiB per page and explicit continuations. Status failure cannot authorize reads
  or undo completion. Configuration/cron examples are synthetic and not installed.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/service.py; ../Wintap-PyUtil/wintappy/coordination/client.py; ../Wintap-PyUtil/wintappy/coordination/recovery.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; ../Wintap-PyUtil/Makefile -->

### Red/green attribution and current results

All runs use the explicit main environment through the isolated disposable-CWD
runner, with no pytest cache, checkout settings writes or production data access.
Private report basenames below identify retained evidence, not committed raw output.

| Run | Result and scope |
|---|---|
| `dcc-linux-integration-red.txt` | 13 missing-service/client/recovery API failures before implementation. |
| `dcc-linux-integration-first-green.txt` | 13 passes in 27.03 s; before later hardening. |
| `dcc-linux-hardening-red.txt` | Five failures / 28 passes: offline memory validation, prior-completion clock, missing retry-state creation, CLI options and missing writer-recovery audit. All five repaired. |
| `dcc-linux-hardening-green.txt` | 337 passes / one failure in 435.63 s on the pre-signal revision. The real local Makefile build succeeded; the failure was the historical assertion banning the router's module name from Make's echoed command. This run does not cover subsequent signal/state/audit controls. |
| `dcc-linux-lifecycle-first.txt` | Two passes / one failure: real SIGTERM returned 143 without a terminal release because `SystemExit` escaped the wrapper. Filesystem-backed synthetic transport is not actual S3. |
| `dcc-linux-signals-red.txt` | Six failures / one pass / 18 deselected before the signal repair; unrelated exit-zero remains blocked. The filter excluded real lifecycle cases, which remain separately recorded above. |
| `dcc-linux-signals-green.txt` | 25 reader/lifecycle passes in 11.92 s, including real SIGINT/SIGTERM, missing/changed shutdown evidence and cancellation outcome retry. |
| `dcc-linux-client-state-red-bounded.txt` | Four active failures: aliased state/lock, changed retry transport and missing outstanding job ID in sanitized CLI diagnostics. The preliminary unbounded alias probe timed out at 120 s before completion; it is not a completed red result. Added an exact synthetic grant to bound that control, then retained the four failures before repair. |
| `dcc-linux-client-state-green.txt` | 29 reader/lifecycle passes in 12.03 s after the state/transport/diagnostic repairs. |
| `dcc-linux-local-make-green.txt` | Seven routing passes in 40.12 s, including real raw-only Makefile/DBT build with offline locked launch, invalid inactive coordination settings, missing AWS profile, unused remote metrics and zero client-state creation. No compacted/entity directories are required. |
| `dcc-linux-reader-recovery-red.txt` | Four failures before reader-recovery marker/audit retention checks; removed or changed reason/identity evidence had incorrectly survived reopen. Repair adds bounded independent-cursor validation; all four pass in the combined run below. |
| `dcc-linux-focused-final-preformat.txt` | 103 passes / one failure in 178.46 s. `test_real_overlapping_readers_due_writer_and_queued_reader` timed out before both requests arrived; cleanup discarded subprocess diagnostics, so the cause is not established. All five local import-isolation and four reader-audit controls pass. Started before formatting and concurrent validation; neither formatting nor load is an established cause. |

The real Linux lifecycle uses two overlapping readers, a due writer waiting for both,
a later queued reader and execution interval assertions. Abrupt wrapper death keeps
its reservation and refuses restart launch. These are isolated local-process controls,
not endpoint, representative-resource or physical power-loss acceptance.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py; ../Wintap-PyUtil/tests/test_coordination_client.py; ../Wintap-PyUtil/tests/test_coordination_recovery.py; ../Wintap-PyUtil/tests/test_effective_input_roots.py -->

### Historical frozen regression runs — completed before reader repairs

Source/lock freeze records 34 identities privately in
`dcc-linux-full-suite-source-freeze.json`. Both full notifications arrived and all
34 identities are unchanged. The combined new-path/source-routing run finished with the startup
failure above and is not accepted as green. Its five import-isolation controls pass,
covering local source/build/test/docs/debug without SDK, ledger or compactor imports.
Capture reader subprocess exits/stdout/stderr and reproduce the bounded failure
before changing wait expectations; do not relabel the historical result.

Standalone completion notification: **439 passes / two skips in 167.93 s**, exit 0.
All 34 frozen source/runtime-lock identities still match. Main finishes with
**697 passes / three skips / one failure in 828.44 s**, exit 1: the same two-request
startup timeout, still without retained child diagnostics. Source freeze is now
released for the confirmed repairs; neither full result covers them.

Unchanged-source startup diagnostics: twelve bounded ordinary two-reader probes
all publish both requests. A separate forced first-start interleaving through the
actual `run_reader` path reproduces `FileExistsError` in the shared `_mkdir` parent
before one request is published (`dcc-reader-mkdir-race-red.json`). This is a real
client startup defect, not a proven attribution for the historical timeout because
that run retained no child diagnostics. Preserve the ten-second lifecycle wait and
capture child exits/output on failure. The source freeze is released only after
both full notifications and identity checks above.

Additional unchanged-source active-path review probes were **red before repair**:

- `dcc-reader-replay-probe-red.json`: the internal cached DBT worker CLI dispatches
  ordinary DBT twice from the same retained launch files; changing the requested DBT
  end date also forwards the original narrower request to the reader with new
  workload dates. Use a fixed supervised batch without a reusable cached-permission
  entrypoint and reject changed request windows before forwarding a retained job.
- `dcc-reader-terminal-probe-red.json`: terminal retries publish releases after
  original supervision is missing or has `children_stopped: false`, or after the
  retained launch grant identity changes. Require original command/launch/shutdown
  and exact terminal binding on retries, not just valid cached release JSON.

These probes use synthetic transport/captured ordinary DBT dispatch, no endpoint or
production data. The first exploratory window probe did not activate remote routing;
it is not negative-test evidence. The corrected bounded remote-root/fake-store probe
above enters the actual coordinated dispatch. These probes precede source changes;
subsequent repairs require a new source freeze and affected/full reruns.

### Reader repairs — affected green, full rerun still required

`dcc-linux-reader-auth-red.txt` records **12 failures / two passes / 25 deselected
in 2.85 s** before repairs: first-start directory/file/symlink races, cached DBT
worker dispatch, changed command/window and damaged retained terminal evidence.
The repaired client retains `invocation.json` before request PUT, binds launch to
its exact manifest and binds terminal/outcome to original supervision. Ordinary and
signal exits use the same authenticated shutdown check; cancellation requires its
retained signal outcome and no launch. Canonical single-link original records are
required. Missing pre-overlay invocation refuses rather than silently upgrading jobs.
The reusable internal worker CLI was removed; fixed supervised DBT batching spans
preflight/build. The shared-parent race now reuses only an actual directory.
`dcc-linux-reader-auth-green.txt`: **49 passes in 15.37 s** across client, lifecycle
and local-route modules. The ten-second lifecycle wait is unchanged; failures now
retain bounded child exit/stdout/stderr diagnostics.

Follow-up `dcc-linux-reader-scope-red.txt`: **three failures / four passes / 39
deselected in 1.05 s**. Changed resolved endpoint/region and contradictory
`shutdown_uncertain` with stopped children were accepted. Repairs bind non-secret
resolved endpoint/region/addressing style in version-two client transport records
and reject contradictory shutdown. Four cancellation-corruption negatives already
passed. `dcc-linux-reader-scope-green.txt`: **142 passes in 29.32 s**, covering client,
lifecycle, local-route, supervisor and tick. This precedes format-only cleanup;
combined/full regressions and source/diff audits remain required.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/client.py; ../Wintap-PyUtil/wintappy/coordination/service.py §open_message_store; ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_validate_result; ../Wintap-PyUtil/tests/test_coordination_client.py; ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-linux-main-full-final.txt tests
.venv/bin/python -B /tmp/opencode/dcc-run-tests.py standalone \
  /tmp/opencode/dcc-linux-standalone-full-final.txt tests
```

Changed/new integration files pass scoped Ruff lint after formatting; the legacy
source-validation test file has pre-existing format/lint deviations and receives
only its necessary Makefile expectation update. Complete source/wiki diff review
and scoped privacy/artifact audit are closed below; regression acceptance remains
separate.

### Checkpoint maintenance — narrow repaired-phase path, regressions pending

`maintenance.py` accepts only the exact already-blocked original entity-enabled,
deletion-enabled writer. Original immutable receipt, command, actual exit-2
supervision/captures and phase-archive identity are authenticated before repair
launch. A new immutable maintenance receipt and intent audit precede supervised
standalone `checkpoints-repair` under the uninterrupted ledger lock. Successful
repair retains separate observations and its terminal audit, but neither advances
the original cursor nor reopens admission.

`resolve-hour --maintenance-id ...` repeats independent original migration/deletion,
current entity integrity/forward-lineage, historical checkpoint and both-archive
verification. It rechecks original and repair observations before atomic completion.
Version-two completion proofs embed the separate maintenance receipt/outcome while
preserving actual original exit 2; standalone version-three requests bind original
execution and exact repair CLI/coordinator identities plus replacement authorization.
The real repair grammar remains `run_intent`, `entities_verified`, `repair_intent`,
`checkpoint_verified`, `complete` (five records), with repaired/exit 0/migration
complete true. Original blocked archive bytes are not rewritten as successful.

Failed/crashed maintenance remains pending until explicitly audited cannot-resume
abandonment; abandonment preserves the original block. Conflicting checkpoint
replacement requires separate confirmation and retains prior rows in `repair_intent`.
Maintenance history validates 256-row batches with ceilings of 128 KiB per audit,
10,000 operations and 64 MiB aggregate; exhaustion refuses rather than pruning.
Earlier completed proofs remain valid when a later operation is pending under its
own original block. Reopen validates retained ledger evidence without reopening
historical runtime files; fresh resolution still requires original and repair files.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/maintenance.py; ../Wintap-PyUtil/wintappy/coordination/recovery.py; ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/verification.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §repair_checkpoints -->

| Retained private report | Result and attribution |
|---|---|
| `dcc-linux-checkpoint-retained-red.txt` | One real success-control failure before the verifier's assumed repair grammar was corrected to the existing actual retained phases. Failed fixture and child observations retained. |
| `dcc-linux-checkpoint-first-green.txt` | One pass / eight deselected in 11.45 s. Real publication obstruction occurs after entity update and raw deletion; original exits 2, repair preserves the block, independent resolution succeeds with unchanged original archive bytes. |
| `dcc-linux-maintenance-hardening-red.txt` | Four failures / one pass / 18 deselected in 31.25 s: three missing/changed original-evidence cases launched repair, and aggregate history had no ceiling. Malformed-history negative already passed. All four repaired before the 32-pass run. |
| `dcc-linux-maintenance-hardening-green.txt` | 32 maintenance/recovery passes in 214.34 s, before subsequent CLI/history/timing controls. |
| `dcc-linux-repaired-standalone-first.txt` | 14 fixture argument errors before required repair-parser arguments were supplied; not implementation failures. |
| `dcc-linux-repaired-standalone-green.txt` | 66 repaired/completion-verifier passes in 43.98 s, including read-only forward evolution and rehashed original/repair corruption controls; before the later request-version controls. |
| `dcc-linux-maintenance-history-red.txt` | Preliminary next-hour fixture configuration error; not the historical-proof defect's red evidence. |
| `dcc-linux-maintenance-history-active-red.txt` | One failure / 31 deselected in 15.44 s: an earlier repaired proof incorrectly required no pending maintenance globally. Repair authenticates history once without conferring current permission. |
| `dcc-linux-maintenance-extended-green.txt` | Nine passes / 23 deselected in 110.55 s: service repair/resolution, abrupt before/after completion COMMIT, explicit replacement/abandonment, terminal COMMIT and sequential-history/reopen controls. Before later timing/count/retained-runtime controls. |
| `dcc-linux-maintenance-future-audit-red.txt` | One failure / 32 deselected in 11.52 s: a future maintenance terminal-audit timestamp allowed completion. Builder now checks the exact terminal audit before completion COMMIT; the control passes in the completed combined run below. |
| `dcc-linux-checkpoint-combined-main.txt` | 303 passes / one failure in 723.91 s, exit 1. The real three-hour two-row paging control's connection wrapper lacked `cursor()`, now needed by maintenance history. Complete report and failed fixtures retained; all 261 frozen identities match after notification. Latest main-side maintenance controls pass, but this is not a green combined/full-main result. |
| `dcc-linux-checkpoint-paging-green.txt` | One pass / 26 deselected in 14.12 s after adding only independent-cursor delegation to the test wrapper. Original page assertions `[0, 2, 3]` and rehashed corruption refusal on the later page `[0, 2]` remain unchanged. No runtime/safety/timeout changes. |
| `dcc-linux-checkpoint-combined-main-paging-fixed.txt` | 304 passes in 715.34 s, exit 0. Complete affected-main report inspected after notification; all 261 paging-repair identities still match. This covers the latest main-side maintenance controls and real paging/corruption control, not full-main or endpoint/resource acceptance. |
| `dcc-linux-checkpoint-main-full-paging-fixed.txt` | 755 passes / three skips in 1156.34 s, exit 0. Complete full-main report inspected after notification; all 261 paging-repair identities still match. This closes this overlay's local regression, not broader recovery or endpoint/resource acceptance. |

**Original checkpoint freeze:** 261 source/test/DBT/runtime-lock identities in private
`dcc-linux-checkpoint-source-freeze.json`, manifest SHA-256
`ada41bb51cc53673d446cab1a4616bd9a6f0d977bf62d02b4fd935bc81fc290e`.
Scoped Ruff lint passes; format check reports 26 files already formatted. Full
standalone notification passes **460 tests / two skips in 191.79 s**, exit 0;
the complete report was inspected and all 261 identities still match. The combined
main run then completed as recorded above; freeze released only for the demonstrated
test-wrapper defect. That original run remains retained as a failed result.

**Current paging-repair freeze:** `dcc-linux-checkpoint-paging-source-freeze.json`,
261 identities, SHA-256
`453dc0ffb0fc5866b2b477de419f91bcb5bbe00ba15e429f2879e3c743053316`.
Comparison with the original manifest proves only
`tests/test_coordination_completion_controls.py` changed; every runtime/source/DBT/
lock and standalone-test identity is unchanged. The wrapper passes fresh Ruff lint
and format checks. The combined affected-main rerun passes **304 tests in 715.34 s**;
the complete report was inspected and all 261 identities still match after notification.
Full main passes **755 tests / three skips in 1156.34 s**, with its complete separate
`dcc-linux-checkpoint-main-full-paging-fixed.txt` report inspected and all 261 identities
unchanged after notification. Both local full regressions are closed for this revision;
the standalone 460-pass result applies to its unchanged files, not to the main wrapper repair.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-checkpoint-combined-main.txt \
  tests/test_coordination_maintenance.py tests/test_coordination_recovery.py \
  tests/test_coordination_completion.py tests/test_coordination_completion_controls.py \
  tests/test_coordination_authority.py tests/test_coordination_verification.py \
  tests/test_coordination_service.py tests/test_coordination_client.py \
  tests/test_coordination_linux_lifecycle.py tests/test_coordination_local_route.py \
  tests/test_coordination_supervisor.py tests/test_coordination_tick.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-checkpoint-standalone-full.txt tests
.venv/bin/python -B /tmp/opencode/dcc-freeze-check.py check \
  /tmp/opencode/dcc-linux-checkpoint-source-freeze.json
```

The affected-main rerun uses the same target list with the separate paging-fixed
report basename above. Full main was launched only after its green notification,
complete-report inspection and unchanged-identity check:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-checkpoint-main-full-paging-fixed.txt tests
.venv/bin/python -B /tmp/opencode/dcc-freeze-check.py check \
  /tmp/opencode/dcc-linux-checkpoint-paging-source-freeze.json
```

The isolated runner uses each explicit locked runtime, retains failed fixtures and
child observations, and removes successful fixture directories only. After the full-
main notification, inspect the complete report and check the paging-repair manifest
before releasing the freeze for demonstrated defects or the next source slice. That
check now passes; the baseline manifests remain retained while the next recovery
slice starts on separately identified source.
Documentation-only changes are outside this source freeze. No historical full-suite
count is relabeled as covering these reader/checkpoint changes.

### Original-bound deletion recovery

This separate source slice follows the completed reader/checkpoint baseline. Its
**local regression gate is closed; Linux qualification remains open**. The standalone `deletions-repair` path
authenticates retained original migrations before removing survivors, validates
current entities without replay and creates separate disposition/checkpoint records.
Main-runtime maintenance remains bound to the exact original blocked writer, with
receipt/intent before launch and fresh independent verification before completion.
Original exit 2, archive bytes, historical provenance and the cursor are preserved
until separately audited resolution. Generic `reconcile-delete` remains insufficient.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion_recovery.py; ../Wintap-PyUtil/wintappy/coordination/maintenance.py; ../Wintap-PyUtil/wintappy/coordination/recovery.py -->

Private reports below are retained under `/tmp/opencode/`; full reports have been
inspected. Failed fixtures remain private and are not reproduced in this wiki.

| Report basename | Result and attribution |
|---|---|
| `dcc-linux-deletion-main-initial.txt` | Seven initial main integration passes in 51.18 s, before expanded controls. |
| `dcc-linux-deletion-verifier-red.txt` | Five failures / 27 passes in 61.99 s: repair terminal Boolean/integer coercion, integer replacement confirmation and two multi-hour ordering refusals. Three original-corruption passes were masked by incorrect test link authentication; not valid semantic negatives. |
| `dcc-linux-deletion-original-semantic-red.txt` | Corrected authentication uses the archived terminal envelope's `sha256`; two failures / one pass / 29 deselected in 8.85 s establish integer original-terminal acceptance and duplicate original checkpoint acceptance. The original report remains retained. |
| `dcc-linux-deletion-controls-initial.txt` | One failure / 31 passes in 322.34 s: service parser lacks `repair-deletions`. Crash/abandonment, evidence/history damage and atomic-resolution controls pass on the provisional implementation; this run does not include the subsequently appended repair-capture test. |
| `dcc-linux-deletion-capture-red.txt` | One failure / 32 deselected in 12.96 s: rehashed repair archive bypasses the retained maintenance report's archive identity. |
| `dcc-linux-deletion-interference-red.txt` | Two failures / 13 deselected in 2.14 s: empty-directory traversal has no node bound, and changed checkpoint after repair intent is detected only after survivor deletion. |
| `dcc-linux-deletion-preinventory-red.txt` | Three failures / one pass / 13 deselected in 6.90 s: both repair/deletion-intent checkpoint-interference stages and Parquet traversal before prefix-budget validation fail; the restored publication-failure retry tail passes. |
| `dcc-linux-deletion-repair-green-initial.txt` | 47 passes / two failures in 86.45 s. Multi-hour repair and original-byte preservation pass; the appended test tail incorrectly invokes public one-hour completion/authority verification. Both failures stop at the deliberate one-hour window boundary, not failed disposition. Report and fixtures remain retained. |
| `dcc-linux-deletion-multihour-scope-fixed.txt` | Two passes / 30 deselected in 4.33 s. Corrected test retains both public multi-hour refusals and verifies three-hour/two-event disposition read-only through `verify_disposition()` after independent current-authority setup in entity mode; original archives unchanged. |

Standalone originals genuinely unlink one of two source Parquet files before an
injected deletion failure. Main originals genuinely delete one event family while
unprivileged directory permissions prevent deletion of the other; permissions are
restored in `finally`, and supervision establishes actual exit 2/stopped children.
These are synthetic local fixtures, not historical recovery or endpoint evidence.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_deletion_recovery.py §partial; ../Wintap-PyUtil/tests/test_coordination_deletion_recovery.py §blocked_deletion_run -->

After all red-run notifications and complete-report inspection, demonstrated runtime
repairs add exact canonical terminal/confirmation comparison, original checkpoint
prefix uniqueness/order, actual per-hour migration/deletion grammar, aggregate
object/directory-node validation before Parquet discovery and all-hour checkpoint/
survivor revalidation throughout repair. Main completion binds independently verified
repair archive digests/counts to the retained maintenance capture as well as current
archive bytes. Narrow service dispatch is wired; its two service/capture controls
pass in 26.66 s. The initial standalone rerun's two test-scope failures and corrected
multi-hour controls are attributed separately above; no public verification boundary
was widened.
Maintenance receipt v2, completion request v4 and completion proof v3 carry deletion
disposition; existing checkpoint/normal formats remain supported without a ledger
schema change. Scoped Ruff lint/format checks pass all 11 deletion-related Python
targets after formatting/import cleanup. The separate deletion freeze covers 265
source/test/DBT/runtime-lock identities in `dcc-linux-deletion-source-freeze.json`,
SHA-256 `ec2708e2e2722fff7db4bc60327ab05864e8768f6d687ccb3a95a9fd257cca35`.
Frozen standalone deletion focus passes **49 tests in 90.48 s**, exit 0, in
`dcc-linux-deletion-standalone-focused-frozen.txt`. Frozen main focus passes
**33 tests in 348.84 s**, exit 0, in
`dcc-linux-deletion-main-focused-frozen.txt`. Both complete reports inspected after
their notifications; all 265 frozen identities match after each result. Separate
affected standalone regression passes **203 tests in 177.37 s**, exit 0, in
`dcc-linux-deletion-standalone-affected-frozen.txt`. Its complete report is inspected
and all 265 identities match after notification. Full standalone passes
**509 tests, two skips in 274.88 s**, exit 0, in
`dcc-linux-deletion-standalone-full-frozen.txt`; its complete report is inspected
and all 265 identities match after notification. The two skips remain the explicitly
opt-in isolated-S3 read/write tests, not remote qualification. Affected main passes
**515 tests, one skip in 1345.33 s**, exit 0, in
`dcc-linux-deletion-main-affected-frozen.txt`; its complete report is inspected and
all 265 identities match after notification. The skip is the separate explicit
isolated-local compactor/DBT migration opt-in. No load attribution or historical
failure reinterpretation follows from this elapsed time. Affected commands:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-deletion-main-affected-frozen.txt \
  tests/test_coordination_*.py tests/test_effective_input_roots.py \
  tests/test_dbt_source_validation.py tests/test_compacted_inputs.py \
  tests/test_process_entities.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-deletion-standalone-affected-frozen.txt \
  tests/test_cli.py tests/test_compaction.py tests/test_deletion.py \
  tests/test_phase_evidence.py tests/test_completion_verifier.py \
  tests/test_repaired_completion.py tests/test_deletion_recovery.py \
  tests/test_deletion_completion.py
```

Full commands, each launched only after its own affected pass and identity check:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-deletion-standalone-full-frozen.txt tests
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-deletion-main-full-frozen.txt tests
```

Full main passes **788 tests, three skips in 1492.66 s**, exit 0, in
`dcc-linux-deletion-main-full-frozen.txt`. The complete report is inspected after
notification and all 265 frozen identities match with the unchanged manifest hash
above. Together with the separately inspected affected/full standalone and affected
main passes, this closes deletion's combined local regression gate. No elapsed-time
load attribution or reinterpretation of historical failures is made. Retain this
freeze and all reports; source may now change only for the next retry/entity slice,
which requires its own red/green controls, freeze and separate regressions. The Linux
runbook, README and canonical ETL guide reflect this local-only closure; dcc-02–05,
actual S3, representative resources and native-Mac shutdown remain open.

Renewed deletion review is closed separately from local regression evidence: all
11 deletion runtime/test targets were read completely, along with service/client
scope, effective inputs, configuration examples and operator guidance. Compared
with the accepted reader/checkpoint freeze, seven existing Python files changed
and four deletion source/test files were added; all other frozen identities are
unchanged. Fresh scoped Ruff lint/format checks pass those 11 targets. Complete
changed-wiki diff and the new native-Mac tension page were inspected for privacy;
the earlier unread retained-diff prefix is now covered, including subsequent
documentation-only updates. The scoped audit passes nine Markdown/seven
frontmatters, 217 grounding paths, 276 inline sources, 421 wikilinks and 45 section
targets with no new errors. Index/log frontmatter exceptions and unrelated
infographic/data/environment artifacts remain preserved; both repositories'
whitespace checks pass. This is not whole-wiki lint or Linux qualification.

Verified intentional retry and durable
exclusive entity maintenance are not implemented by this slice; dcc-02–05 stay open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_s3_transport.py §test_seeded_fixture_counts/test_fixed_destination_s3_merge_and_skip -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_compacted_inputs.py §test_full_local_migration -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py §_grammar/verify_completion; ../Wintap-PyUtil/wintappy/coordination/completion.py §validate_completion_proof/_build_completion_proof; ../Wintap-PyUtil/wintappy/coordination/service.py §main -->

### Retry preflight — prerequisite only, integration pending

The accepted 265-identity deletion baseline and reports are retained. The next
source slice adds an independent **read-only preflight**, not a retry transition,
completion proof or general entity-maintenance permission. The intended narrow
scope is one raw-only event/hour with exact original failed-merge intent, unchanged
original inputs and an absent output hour. Original failure/receipt/archive and
ledger exclusion/cursor remain unchanged. Entities, deletion and missing original
coverage remain refused; durable retry/entity exclusion still needs separate work.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/retry.py §verify_retry_prepared; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/retry_verifier.py §verify_retry -->

The complete retained red reports are inspected after notifications:

| Report basename | Result and attribution |
|---|---|
| `dcc-linux-retry-standalone-red.txt` | 18 missing-module failures in 1.72 s, exit 1. Fixtures reach actual injected merge failure with retained run/migration intents and blocked terminal. |
| `dcc-linux-retry-main-red.txt` | Nine missing-module failures in 24.10 s, exit 1. Real unprivileged synthetic merges exit 2 before output creation; original supervision establishes stopped children and failures remain retained. |
| `dcc-linux-retry-standalone-green-first.txt` | Two failures / 16 passes in 1.64 s, exit 1: the reused standalone fixture retains `delete_source=True`, outside the intended narrow scope. The 16 negative passes stop at that scope refusal and do **not** establish active-path corruption coverage. Preserve report/fixtures; correct only the fixture's intended pre-run scope and rerun all controls. |
| `dcc-linux-retry-main-green-first.txt` | One failure / eight passes in 27.09 s, exit 1. Complete report and retained original receipt inspected: main's reused execution default also has `delete_source=True`. No verifier request/launch occurred; the eight scope-masked negatives are not active-path corruption evidence. |
| `dcc-linux-retry-standalone-corrected-first.txt` | Two failures / 19 passes in 2.36 s, exit 1. Both fixtures now explicitly disable deletion before the original run. Previously masked standalone negatives and budget control pass; newly added marker/empty-output changes after the second data recheck are wrongly accepted. Preserve report/fixtures and repair the demonstrated final-prefix recheck gap. |
| `dcc-linux-retry-main-corrected-first.txt` | Nine passes in 30.17 s, exit 0. Complete report inspected; valid raw-only preflight reaches the independent verifier and preserves the failed original/cursor/exclusion. Before later extended controls and standalone repair. |
| `dcc-linux-retry-standalone-extended-first.txt` | 45 passes in 4.34 s, exit 0; complete report inspected. Source rechecks content and both prefixes after each data observation. Includes formerly masked negatives, late marker/output/input/archive controls, strict request/checksum/regular-file refusal, original-capture binding, request recheck and result-budget refusal. Before main's count-binding repair and separate freeze/regressions. |
| `dcc-linux-retry-main-extended-first.txt` | Three failures / 30 passes in 112.87 s, exit 1; complete report inspected. Changed source rows/files/bytes are wrongly accepted even with consistently rehashed verifier captures and valid stopped-child evidence. All three controls reach actual independent launch; retain failures/fixtures. Type/range checks alone do not authenticate original totals. |
| `dcc-linux-retry-main-counts-fixed.txt` | 33 passes in 113.08 s, exit 0; complete report inspected after notification. All three changed-total controls now refuse; original failure/block/cursor and ledger tables remain unchanged. Before subsequent format-only cleanup and frozen focus. |
| `dcc-linux-retry-standalone-counts-fixed.txt` | 45 passes in 4.19 s, exit 0; complete report inspected after notification. Standalone source/tests unchanged from the previous 45-control result. |
| `dcc-linux-retry-standalone-focused-frozen.txt` | 45 passes in 4.18 s, exit 0; complete report inspected and all 269 retry identities unchanged after notification. Before affected/full regression. |
| `dcc-linux-retry-main-focused-frozen.txt` | 33 passes in 112.95 s, exit 0; complete report inspected and all 269 retry identities unchanged after notification. Before affected/full regression. |
| `dcc-linux-retry-standalone-affected-frozen.txt` | 248 passes in 179.13 s, exit 0; complete report inspected and all 269 retry identities unchanged after notification. Full standalone launched only after those checks. |
| `dcc-linux-retry-standalone-full-frozen.txt` | 554 passes / two opt-in isolated-S3 skips in 287.54 s, exit 0; complete report inspected and all 269 retry identities unchanged after notification. Standalone affected/full gates pass; main and combined closure remain pending. |
| `dcc-linux-retry-main-affected-frozen.txt` | 548 passes / one approval-gated isolated-local compactor/DBT migration skip in 1446.75 s, exit 0; complete report inspected and all 269 retry identities unchanged after notification. Full main launched only after those checks; final result remains pending. |
| `dcc-linux-retry-main-full-frozen.txt` | 821 passes / three approval-gated skips in 1602.08 s, exit 0; complete report inspected and all 269 retry identities unchanged after notification. Together with both affected and standalone full results, closes the combined read-only preflight local regression gate, not retry permission or Linux acceptance. |

Commands use the explicit main `.venv/bin/python` retained runner from PyUtil,
with runtime selector `standalone`/`main` and the respective
`tests/test_retry_verifier.py`/`tests/test_coordination_retry.py`. Both fixture
corrections retain runtime deletion refusal and historical reports. New green controls
and both affected/full gates pass on the unchanged revision. No new
ledger schema, retry permission or CLI recovery dispatch is added.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_retry_verifier.py §failed_merge; ../Wintap-PyUtil/tests/test_coordination_retry.py §failed_merge -->

Main now reads bounded original migration-intent JSON, binds its identity through
the blocked terminal to the authenticated original failure capture, validates
individual and aggregate integer budgets, and requires independently reported
source rows/files/bytes to equal those original totals exactly. No main-runtime
Parquet SQL is added; the standalone verifier still owns current data observations.
Fresh 33-main/45-standalone reruns pass in the separate `counts-fixed` reports above.
After both notifications, two format-only changes and renewed four-target Ruff
lint/format checks pass. All four new source/test files were read completely,
including original-count authentication, bounded JSON-only main verification,
standalone request/data rechecks and active-path launch/capture negatives. Complete
changed-wiki diff and the new native-Mac tension page were inspected for privacy;
the scoped audit passes nine Markdown/seven frontmatters, 221 grounding paths,
289 inline sources, 423 links and 47 sections; both whitespace checks pass. No
whole-wiki lint or regression/endpoint qualification is implied.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/retry.py §_original_source_totals/verify_retry_prepared -->

The separate `dcc-linux-retry-source-freeze.json` covers **269 identities**, SHA-256
`bb08f68673e26af13aa04fabc468eefdccfe7f2bf2fb6fb2e84f5e34c66ffa0f`.
Comparison retains every accepted deletion identity unchanged and adds only the
four retry files. Frozen main/standalone focuses pass as recorded above. Affected
standalone passes 248 tests and full standalone passes 554 tests/two opt-in S3 skips.
Its full suite began only after its successful affected notification, complete-report
inspection and unchanged-identity check; the full report and identities are now checked.
Affected main passes 548 tests/one approval-gated isolated-local migration skip;
its complete report and all identities are checked after notification. Full main
passes 821 tests/three skips in 1602.08 s; its complete report is inspected and all
269 identities match after notification. Each full suite began only after its own
successful affected notification, complete-report inspection and unchanged-identity
check. The elapsed time establishes
no load attribution and leaves the lifecycle's ten-second wait unchanged.

This closes the **combined read-only retry-preflight local regression gate**. Retain
the freeze and all successful/failed reports; source may now change only as a new
durable-retry/entity slice with separate red/green and frozen regressions. Fresh
four-target Ruff lint/format also pass after the full-main notification. No regression
remains running. No completion, cursor/admission transition or durable retry is
implemented by this baseline.

Closure review inspected the complete changed-wiki diff and the new native-Mac
tension page, including all earlier overlays and the new canonical promotion, for
privacy. Renewed scoped audit passes nine Markdown/seven frontmatters, 223 grounding
paths, 297 inline sources, 425 links and 49 sections; both whitespace checks pass.
Index/log exceptions and unrelated infographic/data/environment artifacts remain
unchanged; this is not whole-wiki lint.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-retry-main-focused-frozen.txt tests/test_coordination_retry.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-retry-standalone-focused-frozen.txt tests/test_retry_verifier.py
.venv/bin/python -B /tmp/opencode/dcc-freeze-check.py check \
  /tmp/opencode/dcc-linux-retry-source-freeze.json
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-retry-standalone-affected-frozen.txt \
  tests/test_retry_verifier.py tests/test_cli.py tests/test_compaction.py \
  tests/test_deletion.py tests/test_phase_evidence.py tests/test_completion_verifier.py \
  tests/test_repaired_completion.py tests/test_deletion_recovery.py \
  tests/test_deletion_completion.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-retry-main-affected-frozen.txt \
  tests/test_coordination_*.py tests/test_effective_input_roots.py \
  tests/test_dbt_source_validation.py tests/test_compacted_inputs.py \
  tests/test_process_entities.py
```

Full suites, each launched after its own affected checks above:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-retry-standalone-full-frozen.txt tests
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-retry-main-full-frozen.txt tests
```

The two skips remain the approval-gated isolated-S3 read-only and destination-
write tests, not platform skips or endpoint passes. No remote operation was attempted.
The main full skips remain separate opt-in S3/entity and isolated-local migration
gates, not endpoint passes. Preflight evidence still cannot authorize retry, entity
maintenance, completion or reader admission. Canonical semantics are promoted to
[[wiki/workflow/wintap-etl-data-flow#Read-only failed-merge retry preflight]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_s3_transport.py §test_seeded_fixture_counts/test_fixed_destination_s3_merge_and_skip -->

### Intentional-retry ownership — active, not accepted

Renewed documentation-only closure audit passes nine Markdown/seven frontmatters,
223 grounding paths, 297 inline sources, 425 links and 49 sections; both whitespace
checks pass. All 269 accepted preflight identities still match the retained manifest.
No old reports/failures or unrelated artifacts were changed.

New `tests/test_coordination_intentional_retry.py` adds genuine failed-original,
fresh-ID, exact-cursor, pre/post-COMMIT and pre/post-launch crash, lost-acknowledgment,
original-evidence refusal and v3-compatible-upgrade controls. First red command
finishes with **11 failures in 28.20 s**, exit 1; complete report inspected. Ten
controls reach the missing retry module after genuine failed originals; the upgrade
control reaches the missing v3 schema fixture. Failed fixtures/report remain retained.
All 269 baseline identities still match before runtime changes:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-first-red.txt \
  tests/test_coordination_intentional_retry.py
```

Selected v4 disposition design is in
[[wiki/work/dbt-compaction-coordination/implementation_plan#Intentional-retry ownership slice — active, not accepted]].
This is not retry permission, regression acceptance or Linux qualification; broader
entity ownership and actual-S3/resource/native-Mac gates remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_intentional_retry.py -->

Initial implementation now adds explicit ledger v4 and compatible v1/v2/v3 upgrade,
bounded original-bound retry history, an internally prepared fresh invocation and
atomic disposition/new-intent COMMIT. Original rows/archives remain failed and
unchanged. Main continues reading JSON only; standalone owns data SQL. Refactored
the private writer launch seam without changing conservative `execute_prepared` or
normal completion semantics. Four-target Ruff lint/format pass. First 11-control
rerun is running; these source changes are not regression-accepted or service-ready.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/intentional_retry.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py; ../Wintap-PyUtil/wintappy/coordination/writer.py -->

That first rerun finishes with **six failures/five passes in 56.13 s**, exit 1;
complete report inspected and failed fixtures retained. Success/COMMIT controls
refuse before their intended boundaries because retained capture reconstruction
incorrectly assumes pretty-printed CLI errors. A fresh synthetic diagnostic reaches
the report/capture mismatch without altering failed fixtures. The repair retains
the exact original error-capture bytes separately and authenticates their parsed
report and supervision hashes; it does not reserialize historical errors.

Two further active controls target post-COMMIT input arrival and same-schema/
same-count content changes at actual retry launch, including audited-resolution
refusal. Their first extended run is **interrupted**, retaining its one-line report
and fixtures; no test result or acceptance is inferred. After the human reports
the network problem fixed, a process inventory shows no surviving test/compactor
process from that run. A fresh 13-control rerun uses a distinct retained report
(`dcc-linux-intentional-retry-extended-red-resumed.txt`) on unchanged source/tests.
No full-suite or service retry gate has begun.

The resumed report finishes with **two failures/11 passes in 83.33 s**, exit 1;
all 68 report lines inspected and failed fixtures retained. The original 11 controls
now pass, but post-COMMIT input arrival and same-schema/same-count changed Parquet
content at actual launch incorrectly complete. Both are acceptance defects, not
fixture or connectivity failures. Repair requires a fresh independent disposition
observation after COMMIT/before launch, plus exact authenticated original/new
migration-intent identity validation shared by normal completion and audited
`resolve-hour`. No successor freeze or affected/full gate exists yet.

Repair adds a distinct independently supervised post-COMMIT prelaunch observation
with durable request/captures and a new receipt/disposition-bound prelaunch record.
Public read-only preflight still requires the original active block. Completion
and audited resolution compare bounded, authenticated original/new migration-intent
JSON identities, including source hashes, partitions, schemas and counts; main
still executes no Parquet SQL. Internal retry completion proof v4 retains the
disposition/prelaunch/source identities without widening standalone one-hour requests.
Repaired 13-control run passes **13 in 89.68 s**, exit 0; complete report inspected.
Five-target Ruff lint/format passes before further controls. A subsequent source
review removes unnecessary ambient credential re-resolution from completion, using
the invocation's already frozen ephemeral credentials under unchanged storage scope;
that delta requires the next rerun. Broader controls and service dispatch remain
pending, not accepted.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/intentional_retry.py; ../Wintap-PyUtil/wintappy/coordination/retry.py; ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py -->

The extended 41-control run finishes with **four failures/37 passes in 233.40 s**,
exit 1; all 493 report lines inspected. All four failures reach argparse's missing
`retry-hour` choice, not an accepted service refusal. The 37 passes include the
credential-reuse delta, retained semantic/history/corruption/budget controls, audited
clean-retry resolution and genuine completed-v3 preservation. Report and failed
fixtures remain unchanged. Implement explicit Linux-only original-receipt dispatch
under uninterrupted exclusion, with confirmation/reason, an evolving clock, no
transport/grant calls and no unrelated maintenance flags, before another rerun.
No successor freeze or affected/full gate exists; Linux/dcc-02–05 remain open.

A separate existing v2 compatibility
control fails in 3.80 s because its synthetic older-schema fixture imports v4's
retry-history origin alongside genuine authority/reservation evidence. Complete
157-line report inspected; fixture failure retained. Corrected the fixture's
version-specific event selection without changing upgrade validation or retained
authority/readers/outbox checks. Fresh focused rerun passes **one in 3.99 s**,
exit 0; complete report inspected. This is a fixture correction, not a demonstrated
failure upgrading an actual v2 ledger. Of 269 accepted baseline identities, 265
remain unchanged before this test-only correction; the four intentional source
deltas are completion, ledger, read-only/private retry adapter and writer.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_completion_controls.py §test_v2_schema_fixture_preserves_genuine_authority_proof_and_reader_reservation -->

Linux-only `retry-hour` now loads the original execution receipt and dispatches
through `retry_and_complete_prepared(..., clock=_now)` inside one `Ledger.open`
context. It requires explicit confirmation/reason and rejects unrelated reader,
maintenance and paging flags before configuration resolution. It requests no
transport or grants. Fresh nine-target Ruff lint/format checks pass. The repaired
combined rerun passes **42 in 244.42 s**, exit 0; the complete report is inspected,
including the original 13, extended 28 and existing v2 compatibility control:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-service-repaired-42.txt \
  tests/test_coordination_intentional_retry.py \
  tests/test_coordination_intentional_retry_controls.py \
  tests/test_coordination_completion_controls.py::test_v2_schema_fixture_preserves_genuine_authority_proof_and_reader_reservation
```

New history/exclusion controls use three genuinely failed originals and independent
successful retries, retained read budgets, instrumented paging/late-audit corruption,
ordinary reopen without historical runtime reads, actual competing-process exclusion,
early flag refusal and original-settings/evolving-clock service checks. This file's
lint/format passes. Its first execution retains **one failure/12 passes in 60.14 s**,
exit 1; all 69 report lines inspected. The genuine three-hour fixture and late-page
corruption refusal execute, but final restoration comparison uses unordered SQL
rows after deleting/reinserting the audit. Only `events` differs in list order.
Make the test's complete-row comparison deterministic; do not weaken runtime history
validation or any corruption assertion. The original report/failed fixture remain:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-history-first.txt \
  tests/test_coordination_intentional_retry_history.py
```

These are pre-freeze controls, not successor regression or Linux acceptance.
No successor freeze/affected/full gate exists; distinct entity-only ownership and
endpoint/resource/native-Mac gates remain separate. Historical failures are retained.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/service.py §main; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_controls.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_history.py -->

The test-only correction uses `ORDER BY ALL` for every retained table, comparing
all columns independently of physical reinsertion order. The distinct rerun passes
**13 in 60.10 s**, exit 0; complete report inspected. Runtime history checks and the
late-page corruption refusal remain unchanged. Fresh ten-target Ruff lint/format
checks pass. Original failed report/fixtures stay untouched:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-history-ordered.txt \
  tests/test_coordination_intentional_retry_history.py
```

Review adds actual before/after-COMMIT process crashes and lost-acknowledgment controls
for the distinct v3 upgrade branch. Synthetic legacy-schema fixtures carry genuine
independently completed proof bytes, reader reservations, outbox/tombstones and exact
original rows; no completion/archive is manufactured. The run passes **three in
17.99 s**, exit 0; complete report inspected. Explicit retry of an uncommitted upgrade
works; an already committed upgrade cannot repeat. New credential-reuse controls
for normal completion and audited resolution are running; they forbid ambient
storage re-resolution on genuine local fixtures and do not qualify S3:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-upgrade-first.txt \
  tests/test_coordination_intentional_retry_upgrade.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-credentials-first.txt \
  tests/test_coordination_intentional_retry_credentials.py
```

Fresh comparison finds **263 of 269 accepted preflight identities unchanged**. Six
intentional deltas are completion, ledger, retry, service, writer and the v2 fixture
test; standalone/DBT/runtime-lock identities remain unchanged. The retained baseline
manifest hash still matches its recorded value. New successor files require their
own freeze. No successor regression, Linux acceptance or entity permission is inferred.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_intentional_retry_history.py §retained_rows; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_upgrade.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_credentials.py -->

Credential controls pass **two in 24.88 s**, exit 0; complete report inspected.
Normal completion and audited resolution reuse the exact frozen credential object
without another storage resolver call. These genuine local controls are not remote
credential-provider or endpoint qualification. The complete 14-target successor
source/test review includes original receipt loading and ephemeral environment delivery,
private launch versus conservative API, public/private preflight, disposition/history/
budgets, migration identities shared with recovery, legacy completed-history validation,
strict service dispatch and all new controls. Fresh 14-target Ruff lint/format pass.
No runtime/test run remains pending before the successor freeze.

#### Successor freeze and staged regressions

The separate successor manifest retains **275 source/test/DBT/runtime-lock identities**
at `/tmp/opencode/dcc-linux-intentional-retry-source-freeze.json`, SHA-256
`01dc68118b911479d666c38d7495ccf6e1493bcc4c36441e0705ae9a21093f95`.
Creation and immediate check pass. The accepted 269-identity preflight manifest is
not overwritten. Pre-freeze scoped audit passes nine Markdown/seven frontmatters,
223 grounding paths, 318 inline sources, 430 links and 54 sections; both whitespace
checks pass. Complete tracked wiki diff privacy scan inspects 2,600 lines with zero
findings, and the native-Mac tension page is read. The first scan used an unsupported
system-Python subprocess option; the explicit main runtime rerun passes. No source
defect or whole-wiki lint claim is inferred.

| Retained report under `/tmp/opencode/` | Successor status |
|---|---|
| `dcc-linux-intentional-retry-main-focused-frozen.txt` | 119 passes in 512.18 s, exit 0; complete report inspected and all 275 identities match after notification. |
| `dcc-linux-intentional-retry-main-affected-frozen.txt` | 607 passes/one isolated-local migration opt-in skip in 1843.36 s, exit 0; complete report inspected and all 275 identities match after notification. |
| `dcc-linux-intentional-retry-main-full-frozen.txt` | 880 passes/three opt-in skips in 2013.77 s, exit 0; complete report inspected and all 275 identities match after notification. Launched only after its own affected checks. |
| `dcc-linux-intentional-retry-standalone-focused-frozen.txt` | 45 passes in 4.20 s, exit 0; complete report inspected and all 275 identities match after notification. |
| `dcc-linux-intentional-retry-standalone-affected-frozen.txt` | 248 passes in 180.48 s, exit 0; complete report inspected and all 275 identities match after notification. |
| `dcc-linux-intentional-retry-standalone-full-frozen.txt` | 554 passes/two opt-in S3 skips in 290.13 s, exit 0; complete report inspected and all 275 identities match after notification. Launched only after its own affected checks. |

Both successor full gates pass, closing the **combined intentional-retry local
regression gate**. Source/tests/DBT/runtime locks stayed frozen through both full
notifications, complete reports and identity checks. Each affected/full launch
followed its own prerequisite notification/report/identity checks. Retain this freeze,
all reports and every historical failure; release source only for a separate entity-
ownership slice with its own active controls and successor regressions. These gates
do not qualify entity-only ownership, S3, resources, native-Mac shutdown or Linux.

```sh
.venv/bin/python -B /tmp/opencode/dcc-freeze-check.py check \
  /tmp/opencode/dcc-linux-intentional-retry-source-freeze.json
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-main-focused-frozen.txt \
  tests/test_coordination_retry.py tests/test_coordination_intentional_retry.py \
  tests/test_coordination_intentional_retry_controls.py \
  tests/test_coordination_intentional_retry_history.py \
  tests/test_coordination_intentional_retry_upgrade.py \
  tests/test_coordination_intentional_retry_credentials.py \
  tests/test_coordination_completion_controls.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-intentional-retry-standalone-focused-frozen.txt \
  tests/test_retry_verifier.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-intentional-retry-standalone-affected-frozen.txt \
  tests/test_retry_verifier.py tests/test_cli.py tests/test_compaction.py \
  tests/test_deletion.py tests/test_phase_evidence.py tests/test_completion_verifier.py \
  tests/test_repaired_completion.py tests/test_deletion_recovery.py \
  tests/test_deletion_completion.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-main-affected-frozen.txt \
  tests/test_coordination_*.py tests/test_effective_input_roots.py \
  tests/test_dbt_source_validation.py tests/test_compacted_inputs.py \
  tests/test_process_entities.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-intentional-retry-standalone-full-frozen.txt tests
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-intentional-retry-main-full-frozen.txt tests
```

Post-freeze status reconciliation also passes the scoped nine-Markdown/seven-
frontmatter audit with the same grounding/link/section counts and both whitespace
checks. Complete tracked wiki diff privacy scan inspects 2,685 lines with zero findings.
These documentation checks do not alter frozen source or establish runtime acceptance.
All successor focused/affected/full gates are green. The two standalone
skips are the approval-gated isolated-S3 read-only and destination-write tests, not
platform skips or endpoint passes. Their live guards were reread; no remote operation
was attempted. No completion is inferred from elapsed time; the lifecycle's ten-second
wait remains unchanged, with no load attribution.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_s3_transport.py §test_seeded_fixture_counts/test_fixed_destination_s3_merge_and_skip -->

Main affected's one skip remains the explicit isolated-local full compactor/DBT
migration gate, not a passed integration or endpoint test. Its live guard was reread.
Full main launched only after the 607-pass notification, complete retained-report
inspection and unchanged 275-identity check. Full main now passes 880/three skips,
with complete report inspected and all identities unchanged after notification.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_compacted_inputs.py §test_full_local_migration -->

The three main full skips remain the isolated copied-S3 migration, synthetic-S3 entity
and isolated-local full migration opt-ins; their live guards were reread, with no
remote operation attempted. Fresh 14-target Ruff lint/format also passes. No regression
remains running. Stabilized intentional-retry facts are promoted to
[[wiki/workflow/wintap-etl-data-flow#Audited raw-only intentional retry]]. Local gate
closure does not authorize general entity ownership, production scheduling or publication.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_compacted_s3_migration.py §test_copied_live_hour_migration; ../Wintap-PyUtil/tests/test_process_entities_s3.py §test_isolated_s3_process_entities -->

### Entity-only ownership — active, not accepted

The accepted intentional-retry 275-identity manifest/reports remain retained. All
275 identities match after adding only `tests/test_coordination_entity_operations.py`;
runtime, standalone verifier, DBT and locks are unchanged. Its 22 lint/format-clean
controls use genuine genesis inputs and independently anchored replay state, strict
public-receipt refusal, no raw-completion/cursor forgery, confirmation/reason/clock/
receipt checks, committed-reader/raw-owner exclusion, unverified-state refusal,
late inputs, clean-original resolution and child crash/competing-process boundaries.
Reader/raw-owner fixtures establish valid replay scope to avoid genesis-state masking.

The first run finishes with **22 failures in 35.05 s**, exit 1. All **749 report
lines are inspected**, and failed fixtures remain at `/tmp/opencode/dcc-retained-8kaw1iqo`.
Every failure reaches missing `wintappy.coordination.entity_execution`; four child
controls exit 1 instead of intended 87. No entity refusal, crash boundary, lock-through-
launch behavior or entity completion has executed or passed. All 275 accepted
identities are rechecked after the notification. No test remains running.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-operations-first-red.txt \
  tests/test_coordination_entity_operations.py
```

The separate standalone-verifier first run finishes with **64 failures in 29.53 s**,
exit 1. Its complete **2,972-line retained report** is inspected (the notification's
2,974 lines additionally include the fixture-retention footer). Every failure reaches
missing `raw_sensor_compact.entity_operation_verifier`, after genuine input/original
fixtures; no fixture failure or verifier refusal is accepted. Failed fixtures remain
at `/tmp/opencode/dcc-retained-2qrtl4sg`. Controls include independently constructed
prelaunch originals, one/multi-hour genesis/replay, forward lineage without comparing
historical checkpoint hashes with current aggregate, content/schema/count non-mutation,
archive corruption/exact types, aliases/FIFOs, final input rechecks and bounded requests.
All 275 accepted identities match after the completed notification/report inspection.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-verifier-first-red.txt \
  tests/test_entity_operation_verifier.py
```

Distinct receipt controls first finish with **26 missing-module failures in 0.51 s**,
exit 1; all **523 report lines** inspected, failed fixtures retained at
`/tmp/opencode/dcc-retained-_mrkbegp`, and all 275 accepted identities unchanged.
Added `wintappy/coordination/entity_execution.py` with separate bounded entity
configuration/receipt validation, exact multi-hour command/path binding, canonical
single-link loading, qualified runtime identity and prelaunch rechecking. Preparation
does not open/upgrade the ledger, write datasets or confer launch permission.
Fresh two-target Ruff lint/format checks pass. The distinct first rerun passes
**26 controls in 6.16 s**, exit 0; complete three-line report inspected and all 275
accepted identities unchanged afterward. Neither report overwrites the first red run.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-execution-first-rerun.txt \
  tests/test_coordination_entity_execution.py
```

Added a separate standalone `entity_operation_verifier.py`, with entity-only input
and completion APIs, exact selected inventories/content/schema/counts, original-bound
phase/checkpoint grammar, single-link local streaming reads and final observations.
Its first distinct rerun passes **64 controls in 36.47 s**, exit 0; complete three-line
report `/tmp/opencode/dcc-linux-entity-verifier-first-rerun.txt` inspected and all 275
accepted identities unchanged after notification. This is an initial focused result,
not verifier qualification. Source review identifies Python invalid-row collection
through the existing loader, insufficient original-hour validation, missing early
resource/storage/work-path checks and historical publication statistics supported
only by a mutually consistent archive/checkpoint, not an independent observation.
Ruff still reports import ordering and two line-length issues; formatting is unfinished.

Added genuine review controls before repairs. First review finishes with **21 failures /
two passes in 5.74 s**, exit 1; all **955 retained report lines** inspected and failed
fixtures `/tmp/opencode/dcc-retained-edpxkmjv` preserved. Eighteen failures reach
loader/validation/historical-observation defects; three corruption fixtures call
nonexistent `ProcessingMetricsStore.write`, so those attacks have not yet executed.
Corrected only that fixture to use the live `publish` API. The distinct corrected red
finishes with **21 failures / two passes in 6.94 s**, exit 1; all **901 report lines**
inspected and failed fixtures `/tmp/opencode/dcc-retained-wd70qr1s` preserved. The
three historical row/byte/conflict attacks now execute and are wrongly accepted;
forward evolution lacks independent original-publication evidence. All 275 accepted
retry identities match after report review.

Added an unqualified verifier-only SQL loader: projection/counts/sorting remain in
DuckDB, exclusion fingerprints stream one bounded canonical diagnostic record at a
time, and only bounded hour/host/reason aggregates leave SQL. The existing writer's
loader stays unchanged. Selected-object evidence now streams into its canonical
digest. Verifier repairs add exact original-hour shapes/types/coverage, early
resource/identity/storage/work-path validation, current parent-conflict checks and
caller-authenticated historical publication observations. Completion requests retain
a separate `publication`; results bind its digest. No historical observation is
reconstructed from current data or a rehashed archive/checkpoint.

Fresh four-target Ruff lint/format checks pass after patch-only formatting cleanup.
The distinct combined repair rerun finishes with **12 failures / 75 passes in
35.57 s**, exit 1; all **1,609 report lines** reviewed, failed fixtures retained at
`/tmp/opencode/dcc-retained-rlxlrlly`, and all 275 accepted identities match. Genuine
input/completion, forward-evolution and quarantine positives fail; negative passes
cannot establish semantic refusal while this loader defect masks execution.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-verifier-repairs-first-rerun.txt \
  tests/test_entity_operation_verifier.py tests/test_entity_verifier_review.py
```

Direct retained-fixture diagnosis reveals an unfinished scalar result at Python-UDF
registration. Changing only that function-existence query to bounded `fetchall`
retains **12 failures / 75 passes in 35.77 s**, exit 1, in
`/tmp/opencode/dcc-linux-entity-verifier-registration-rerun.txt`; all **1,609 report
lines** reviewed, failed fixtures `/tmp/opencode/dcc-retained-o0sf3amu` preserved and
all 275 accepted identities rechecked unchanged. A second direct read-only diagnostic
now reaches the missing optional NumPy dependency at UDF registration. The runtime
lock stays unchanged: replaced the verifier UDF with a separate cursor over an
ephemeral SQL staging relation, canonicalizing/inserting one bounded diagnostic at
a time before SQL sorting/counting and streaming fingerprints. Record/report budgets
are separate, with no pruning. Three direct repeated loader calls now succeed; this
diagnostic alone does not qualify the verifier.

Added distinct expanded compatibility, Unicode/multi-hour quarantine, overlap,
repeated/empty input, budget, excluded-host/lifecycle, retained-publication corruption
and genuine canonical request controls. Fresh five-target Ruff lint/format passes
after patch-only formatting. Their distinct first retained run finishes with
**35 failures / 9 passes in 20.71 s**, exit 1:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-verifier-qualification-first.txt \
  tests/test_entity_verifier_qualification.py
```

The complete report is reviewed through exact paragraph deduplication: all 4,671
original lines are retained, every nonblank line represented with original ranges in
`/tmp/opencode/dcc-linux-entity-verifier-qualification-first-deduplicated.txt`.
Failed fixtures `/tmp/opencode/dcc-retained-a8_20l59` are preserved and all 275
accepted identities match. Nine loader compatibility/budget controls pass, but
publication/request positives and excluded-host/lifecycle controls are masked by a
nonexistent `Inventory.file_count` attribute in the new verifier. A retained direct
read-only stage trace diagnoses that defect. Replaced only this reference with the
bounded sum of selected group lengths; four original genesis/replay input/completion
diagnostics succeed. Public suppression, accepted code and runtime locks are unchanged.
Fresh five-target Ruff lint/format passes. The distinct combined run passes
**131 controls in 91.07 s**, exit 0; complete report inspected and all 275 accepted
identities match after notification:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-verifier-streaming-combined-first.txt \
  tests/test_entity_operation_verifier.py tests/test_entity_verifier_review.py \
  tests/test_entity_verifier_qualification.py
```

Ten additional controls cover legacy SQL Unicode quarantine projection, SQL-owned
single-row materialization without UDFs/batched diagnostics, the shared raw/compacted
file budget and genuine nonzero parent conflicts before/after forward evolution.
Their first retained run finishes with **five failures/five passes/44 deselected in
8.31 s**, exit 1; all 184 report lines inspected, failed fixtures
`/tmp/opencode/dcc-retained-5hlmb3c4` preserved and all 275 accepted identities match.
Four failures assume Python-derived Unicode sentinels are selected by the existing
writer's SQL projection with valid PID; one uses invalid SQL `REPLACE ... EXCLUDE`
ordering. Corrected only fixtures: force quarantine selection with `pid=None`, derive
the lower-level allowlist from the legacy SQL projection and use `EXCLUDE ... REPLACE`.
This preserves the writer's normalization, not a new supported public Unicode scope.
Fresh single-target Ruff lint/format passes. The distinct corrected run passes
**ten controls/44 deselected in 8.49 s**, exit 0; complete three-line report inspected
and all 275 accepted identities match afterward:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-verifier-unicode-materialization-first.txt \
  tests/test_entity_verifier_qualification.py \
  -k 'python_unicode or materialization or shared_across or nonzero_parent'
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-verifier-unicode-materialization-corrected.txt \
  tests/test_entity_verifier_qualification.py \
  -k 'legacy_unicode or materialization or shared_across or nonzero_parent'
```

A separate expanded three-module rerun passes **141 controls in 97.91 s**, exit 0.
Complete four-line report inspected and all 275 accepted identities match after
notification. This closes the expanded standalone verifier focused evidence, not
main-side publication authentication, ownership or successor regression gates:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-verifier-expanded-combined.txt \
  tests/test_entity_operation_verifier.py tests/test_entity_verifier_review.py \
  tests/test_entity_verifier_qualification.py
```

Fresh five-target Ruff lint/format passes. Complete 3,417-line tracked/new-Markdown
review snapshot `dcc-linux-wiki-complete-entity-count-review.diff`, SHA-256
`25cd5029b96606353a1c6f6d6191232b873cd60f6de9e4db01e77a7e6580ee7e`, is now fully
inspected for privacy. The complete 317-line reconciliation delta is also inspected,
retained as `dcc-linux-wiki-expanded-verifier-reconciliation.diff`, SHA-256
`f887b76ac830e6243b432092081d8085de7b2b398dab264fa2047793b664d237`.
Scoped audit passes nine Markdown/seven frontmatters, 223 grounding paths, 341 inline
sources, 435 wikilinks and 59 sections; not whole-wiki qualification.
Existing public one-hour validators, accepted source files, DBT and runtime locks
remain unchanged. No coordinated entity operation is qualified by these focused greens;
durable main-side publication authentication and restart-visible ownership are missing.
Pending-publication repair/retry needs separate original-bound qualification. These
tests do not grant permission or qualify Linux, S3, resources or native-Mac shutdown.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_operations.py; ../Wintap-PyUtil/wintappy/coordination/execution.py §validate_receipt; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py §_opened -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_execution.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_operation_verifier.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_execution.py §prepare_entity_execution/validate_entity_receipt/load_entity_execution/recheck_entity_execution -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_operation_verifier.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_verifier_review.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_input_verifier.py §load_process_inputs/_summary/_record -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_verifier_qualification.py -->

Seven separate explicit-v5-upgrade controls use a genuine independently completed v4
run plus an outstanding committed reader. They check actual before/after-COMMIT
process death, lost acknowledgment, unchanged original proof/cursor/outbox rows,
unconfirmed/invalid target/reason and original corruption refusal. Their first
retained run finishes with **seven failures in 35.10 s**, exit 1; all 295 report
lines inspected. Every failure reaches the unsupported `target_version` argument,
not a semantic refusal or an executed upgrade/crash boundary. Failed fixtures
`/tmp/opencode/dcc-retained-7wc0j4eo` are preserved. The distinct post-verifier
ownership rerun finishes with **22 failures in 44.08 s**, exit 1; all 960 report
lines inspected. All reach missing `entity_writer`, including four child controls
that never reach their crash boundaries. Preserve failed fixtures
`/tmp/opencode/dcc-retained-gxlp1ejr` and earlier reports. All 275 accepted identities
match after both complete report reviews, before source changes:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-upgrade-first-red.txt \
  tests/test_coordination_entity_upgrade.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-operations-after-verifier-red.txt \
  tests/test_coordination_entity_operations.py
```

Opt-in design preserves default v4 initialization/upgrade and adds explicit
`target_version=5`; ordinary open never upgrades. No entity launch permission is
implemented by selecting this schema design.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_upgrade.py -->
<!-- SPECULATIVE: typed entity ownership/completion/publication are not implemented -->

#### Explicit opt-in v5 schema staging — not entity ownership

Implemented explicit compatible v1–v4→v5 upgrade under the existing main-runtime
lock and one actual upgrade COMMIT. Default initialization/default upgrade still
target v4. Source validation precedes schema changes; original raw writer disposition,
reader/outbox/tombstone rows, proof bytes and cursor survive opt-in conversion.
Ordinary open accepts validated v4/v5, refuses legacy/unknown versions and never
migrates. A restarted raw `INTENT` still becomes blocked on ordinary open.
New `entity_runs`/`entity_evidence` tables are separate from raw runs/completions;
their empty-history guard deliberately rejects any entity records or completion
audits until the separate typed ownership adapter exists. Schema selection grants
no entity launch, completion, fresh authority token or reader admission.
Origin/upgrade audits bind source version/time/reason, with SQL-bounded 16 KiB
audit payloads and two-record duplicate detection. No historical runtime/data
is opened for schema selection.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_upgrade_entity_schema/_validate/_validate_entity_schema_origin -->

First repaired seven-control run passes **seven in 36.93 s**, exit 0; complete
three-line report inspected. Actual v4 before/after-COMMIT process death and lost
acknowledgment now execute; earlier missing-argument failures remain retained.
After scoped formatting/SQL audit-read hardening, expanded compatibility run passes
**37 controls in 48.43 s**, exit 0; complete three-line report inspected. This adds
direct v1–v4 reader/writer preservation, unchanged default v4 upgrades, actual legacy
upgrade crash boundaries, corrupt origins/schemas and fail-closed new-history controls.
All **274 other accepted identities remain unchanged**; `ledger.py` is the sole
intentional delta from the retained 275-identity retry baseline. No new ownership
pass is inferred from schema greens.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-upgrade-schema-first-rerun.txt \
  tests/test_coordination_entity_upgrade.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-schema-expanded-first.txt \
  tests/test_coordination_entity_schema.py tests/test_coordination_entity_upgrade.py
```

Six additional genuine-history controls retain independently observed original
authority/raw completion, actual failed-original retry disposition/new completion,
raw completion after v5 selection and original proof-corruption refusal. Their
first combined **43-control** run passes in **109.80 s**, exit 0; complete three-line
report inspected and all 286 identities match after notification. The separate
six-module existing-ledger compatibility first run retains **two failures/149 passes
in 401.75 s**, exit 1; all 271 report lines inspected and all 286 identities match
before repair. Both failures execute actual after-COMMIT/lost-ack and original-row
checks, then fail the repeat-upgrade diagnostic regex; assertions afterward did not
execute. Failed fixtures `/tmp/opencode/dcc-retained-969pqy9a` remain preserved.
Both first runs use the distinct
**286-identity focused snapshot**
`dcc-linux-entity-schema-focused-source-freeze.json`, SHA-256
`dbad9c790c3ff8d6e6418abed85b028f1b2d0b3297c879ef3fafe16f97087578`.
This snapshot is not a closed successor-regression gate.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-schema-history-focused-first.txt \
  tests/test_coordination_entity_upgrade.py tests/test_coordination_entity_schema.py \
  tests/test_coordination_entity_schema_history.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-schema-ledger-compatibility-first.txt \
  tests/test_coordination_ledger.py tests/test_coordination_authority.py \
  tests/test_coordination_completion.py tests/test_coordination_completion_controls.py \
  tests/test_coordination_intentional_retry_upgrade.py \
  tests/test_coordination_intentional_retry_history.py
```

Restored only the default-v4 refusal diagnostic, exactly
`Only compatible v1/v2/v3 ledger upgrade is supported`; opt-in-v5 retains
`Only an older compatible ledger may upgrade to the selected target`. Tests and
refusal semantics are unchanged. The other 274 accepted-retry identities and other
285 schema-focused identities match; only `ledger.py` intentionally differs.
Fresh five-target Ruff lint/format passes. The separate **286-identity repair freeze**
`dcc-linux-entity-schema-diagnostic-repair-source-freeze.json`, SHA-256
`fca412d6b346aed2756f0cae7f403d80c86da3118dc92eb4fb2d21150990e93f`, binds this repair.
The distinct **46-control repaired focus passes in 127.49 s**, exit 0; complete
three-line report inspected and all 286 repair identities match after notification.
The **151-control repaired compatibility passes in 399.51 s**, exit 0; complete
five-line report inspected and all 286 repair identities match after notification.
The explicit opt-in schema-compatibility gate is closed; this is not a successor
focused/affected/full regression gate or entity permission. Both frozen runs are
complete, so subsequent entity source work requires distinct evidence and a later
successor freeze. Original compatibility failures/fixtures remain preserved.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-schema-diagnostic-repair-focused.txt \
  tests/test_coordination_entity_upgrade.py tests/test_coordination_entity_schema.py \
  tests/test_coordination_entity_schema_history.py \
  tests/test_coordination_intentional_retry_upgrade.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-schema-ledger-compatibility-diagnostic-repair.txt \
  tests/test_coordination_ledger.py tests/test_coordination_authority.py \
  tests/test_coordination_completion.py tests/test_coordination_completion_controls.py \
  tests/test_coordination_intentional_retry_upgrade.py \
  tests/test_coordination_intentional_retry_history.py
```
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_upgrade.py -->

Fresh four-target Ruff lint/format passes. Complete 316-line post-verifier/red
documentation delta is inspected for privacy, retained as
`dcc-linux-wiki-entity-schema-red-reconciliation.diff`, SHA-256
`fefaf6649ec7d9a365337fdb95d0451c6ade4453d8ef0fe29470c41648dfcf8a`;
the complete subsequent **371-line** schema/history-green delta is now reviewed for
privacy, retained as `dcc-linux-wiki-entity-schema-history-green-review.diff`, SHA-256
`758b847868453239f5dbe4839def548ffee7f463951d2431c46662cc7228dc87`.
Fresh four-target Ruff lint/format and both repository whitespace checks pass.
Latest scoped audit passes nine Markdown/seven frontmatters, 223 grounding paths,
352 inline sources, 435 wikilinks and 59 sections, not whole-wiki qualification.
The complete **337-line** subsequent diagnostic-repair documentation delta is inspected
for privacy, retained as `dcc-linux-wiki-entity-schema-diagnostic-repair-review.diff`,
SHA-256 `1a0b64e8d3d0269bfc4c61dccadb6f3ccba529b9b1c9a9f348a744bdd8662fc9`.
Fresh five-target Ruff lint/format and both repository whitespace checks pass.
The subsequent complete 288-line focus-green documentation delta is also inspected
for privacy (`dcc-linux-wiki-entity-schema-diagnostic-focus-green-review.diff`, SHA-256
`b02df8c06e7600a9ce8cd9c722ae117909bbfad53174a6d27bda6fd633e2555f`).
Entity ownership/publication/completion/service dispatch and Linux/dcc-02–05 remain
open. No data/remote/production operation outside isolated tests, installed scheduling,
utility implementation, commit or push. Native-Mac shutdown remains separate.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_schema.py; ../Wintap-PyUtil/tests/test_coordination_entity_schema_history.py -->

#### Main-side entity input observations — no permission

Added 21 genuine local controls on explicitly upgraded v5 fixtures before adapter
implementation. First run retains **21 missing-module failures in 16.90 s**, exit 1;
all 496 report lines inspected and all 286 schema-repair identities match before
source changes. Failed fixtures `/tmp/opencode/dcc-retained-nujod9j3` and the report
remain preserved. None establishes an authenticated refusal or entity permission.

New `entity_verification.py` invokes only the separate standalone input verifier,
under the already locked, owner-free v5 ledger with zero readers. It binds exact
entity receipt, original hours, input counts/fingerprints, authority, request,
command/capture/shutdown and non-secret storage scope. Core result/request/proof
budgets are 64 KiB/1 MiB/128 KiB; overflow refuses without pruning. Reusing an earlier
observation rechecks its actual canonical single-link artifacts and requires a fresh
independent unchanged-input observation. No main data SQL, dataset mutation, ledger
row/authority/cursor/admission transition or entity launch is added. Post-COMMIT owner
binding, durable publication authentication, completion and service dispatch remain
unimplemented; the empty-history guard is unchanged.

First adapter rerun retains **one failure/20 passes in 65.77 s**, exit 1; complete
39-line report inspected and all 286 schema-repair identities match before repair.
Appending a newline to original `command.json` is wrongly accepted because parsed
JSON equality is weaker than exact canonical bytes. Preserve failed fixtures
`/tmp/opencode/dcc-retained-ljf989vb` and the separate 288-identity first-rerun source
snapshot. Added exact canonical command/shutdown-byte rechecks and six further
supervision/stderr alias/byte controls, without weakening the original test.
Fresh two-target Ruff lint/format passes. Distinct **27-control artifact-repair** rerun
passes **27 in 83.28 s**, exit 0; complete three-line report inspected and all
288 identities match after notification. The separate **288-identity** freeze is
`dcc-linux-entity-observations-artifact-repair-source-freeze.json`, SHA-256
`752181e1c1ec96e1915266ffc7c2b33f25e2f63023ee6c2c6502ab0d3c23a67e`.
This closes the repaired artifact focus only. Extend main-side input authentication
qualification before typed ownership; observation dictionaries still grant no permission.
All 286 schema-repair identities still match; this slice adds only the new adapter
and its test module, not edits to accepted source/tests/DBT/runtime locks.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-observations-first-red.txt \
  tests/test_coordination_entity_observations.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-observations-first-rerun.txt \
  tests/test_coordination_entity_observations.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-observations-artifact-repair-first-rerun.txt \
  tests/test_coordination_entity_observations.py
```
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_verification.py §verify_entity_inputs_prepared/validate_input_observation/recheck_input_observation; ../Wintap-PyUtil/tests/test_coordination_entity_observations.py -->

The complete **526-line** intervening documentation delta is inspected for privacy:
`dcc-linux-wiki-entity-observation-repair-review.diff`, SHA-256
`ecd9ee4a54024cf43633781328a5bda1f2ad7185934aa6399aa510b3d3224468`.
Historical reds and their failed fixtures remain preserved; successful fixtures are
cleaned by the retained-test harness, so only their reports are durable evidence.

Expanded main-side qualification adds **31 controls** in a separate test module:
genuine four-hour raw/compacted inputs with an empty hour, exact selected-hour totals,
types/bounds, committed readers/live and restarted raw intents, unanchored existing
entities, actual-artifact versus caller-dictionary authentication, duplicate JSON,
independent budgets, receipt-clock refusal and real competing-process locking.
The first retained run finishes with **nine failures/22 passes in 102.92 s**, exit 1;
all 245 report lines inspected and all 289 identities match before repair. Eight
rehashed contract controls wrongly accept mismatched hour/aggregate files or bytes
for raw/compacted inputs. The clock control observes refusal only after an actual
read-only verifier launch; its later row-equality assertion did not execute. These
failures do not establish corrupted-data acceptance or an entity launch/permission
transition. Genuine four-hour positive inputs, committed exclusions and actual
competing-process lock controls execute and pass, but broader qualification remains
open. Preserve failed fixtures `/tmp/opencode/dcc-retained-55skwbte` and the complete
red report. The separate **289-identity** first-run snapshot is
`dcc-linux-entity-observation-qualification-first-source-freeze.json`, SHA-256
`8d3615abe21bdfc3873e2968874b37ca22f91d39edf43fd34d7ac36198a98b0e`.
All original 288 artifact-repair identities match before this run; only the separate
qualification module is added. Entity ownership/history/publication remain unimplemented.

Repaired only `entity_verification.py`: all bounded per-hour file/byte totals must
equal their selected aggregates, and a clock before receipt creation refuses before
verifier launch. All controls remain unchanged; the other 288 identities match the
first-run snapshot. Fresh three-target Ruff lint/format passes. The distinct combined
**58-control** artifact/qualification rerun passes **58 in 185.12 s**, exit 0;
complete three-line report reviewed and all 289 identities match after notification.
The separate **289-identity**
contract-repair freeze, `dcc-linux-entity-observation-qualification-contract-repair-source-freeze.json`,
SHA-256 `2d3c3f8cd5c611488cb059faf8a8285b9741f0d713c06b264c084ad264353bbf`.
This closes the main-side read-only input-authentication focus only. No test remains
active. Retain both snapshots and all historical reds/failed fixtures before typed
intent/restart-exclusion work; entity launch/completion/publication and successor
focused/affected/full regression acceptance remain separate.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-observation-qualification-first-red.txt \
  tests/test_coordination_entity_observation_qualification.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-observation-qualification-contract-repair-first-rerun.txt \
  tests/test_coordination_entity_observations.py \
  tests/test_coordination_entity_observation_qualification.py
```
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_observation_qualification.py -->

The subsequent complete **355-line** artifact-green/expanded-pending documentation
delta is privacy-reviewed (`dcc-linux-wiki-entity-observation-artifact-green-review.diff`,
SHA-256 `908795790188c4c5fe58f0c0c11f97d737ad2d4fd6e2116ba9053dc90b3ed64b`).
Fresh scoped audit passes nine Markdown/seven frontmatters, 229 grounding paths,
361 inline sources, 436 wikilinks and 60 section targets; both repository whitespace
checks pass. This is not whole-wiki, successor-regression or Linux acceptance.

The complete **320-line** contract-repair documentation delta is privacy-reviewed:
`dcc-linux-wiki-entity-observation-contract-repair-review.diff`, SHA-256
`28ae270420a2dac397205adfa6b72b40ab1481d43f62cbf3e3f8d18173890254`.
Fresh scoped wiki and both whitespace checks passed with unchanged audit counts
while the result was pending; the later 58-pass report/identity review is recorded above.

#### Typed entity intent and restart exclusion — no launch

Added a separate **34-control** module before ownership implementation. Fixtures
explicitly select v5 and retain genuine standalone input observations; controls target
typed multi-hour genesis/replay intents, original-bound post-COMMIT observations,
early refusals, v4/no-implicit-upgrade, reader/raw exclusion, actual intent-COMMIT
crash/lost-ack, competing processes, retained JSON corruption and independent read/
write budgets. First retained run has **34 failures in 47.41 s**, exit 1; all **1,132**
report lines inspected and all 290 identities match after notification. Twenty-six
controls reach missing-module imports after fixture setup; two crash children exit 1
at import rather than requested 87, and six budget controls fail import before setup.
No semantic refusal, committed owner or executed crash boundary is established.
Failed fixtures and report remain preserved. All 289 input-repair identities match
before the run; the separate
**290-identity** first-red snapshot is `dcc-linux-entity-intent-first-source-freeze.json`,
SHA-256 `37e379f5250bacb86884ae30626735182e73b434194976bc58412dff50d1f3e8`.
The complete 442-line documentation delta is privacy-reviewed, SHA-256
`e84972bbb9ab824c4b8d05940fd0cf0df89a50b3522d2273fff223eacfd37840`.
Distinct typed source work began after that review; retain the original snapshot and all reds.
The intended sub-slice establishes exclusion only: entity launch/completion,
durable publication, recovery and service dispatch remain later gates.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-intent-first-red.txt \
  tests/test_coordination_entity_intents.py
```
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_intents.py -->

New `entity_intent.py` targets exclusion only: bounded typed original receipt/input
observation, v5 upgrade/authority identities and unchanged raw cursor; receipt and
actual intent artifact precede one ownership COMMIT. Ledger validates typed unresolved
history/audits separately from raw/retry ownership and refuses entity completion/
publication history. Acknowledged same-session original-bound input checks are read-only;
failed checks, reopen and lost acknowledgment retain typed BLOCKED ownership. No entity
operation is launched. Separate **291-identity** implementation freeze, SHA-256
`9c54bf8f93e8794d53fa40d8840fa5ec09f44c4b4df3a1fe6d41ca6757069216`, binds the
distinct implementation rerun: **33 failures/one pass in 34.61 s**, exit 1.
All 291 identities match after notification. Complete failure-specific content is
reviewed through a lossless 1,307-line exact-deduplicated rendering of the 5,691-line
report; the shared 138-line upgrade body is byte-identical across 33 occurrences.
Report SHA-256: `4dd15f263c988aa382d7950ce27050b32753e7949c9764603ee71d6efe37b34d`.
Every failure occurs during fixture v5 upgrade, before typed assertions or crash-child
launch. Only v4/no-implicit-upgrade passes. That run establishes no typed COMMIT,
restart, post-COMMIT input or history-budget qualification. Original controls and 288 prior identities unchanged;
only input adapter/ledger changed plus the new typed module. Four-target Ruff lint/
format and both whitespace checks passed before that run. Both original reds/freezes
and failed fixtures remain retained; implementation-result review is complete.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_intent.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate/_block_unresolved_writer; ../Wintap-PyUtil/wintappy/coordination/entity_verification.py §verify_entity_inputs_prepared -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-intent-implementation-rerun.txt \
  tests/test_coordination_entity_intents.py
```

Retained-fixture diagnosis exposes DuckDB's independent `cursor()` connection: it
cannot see `entity_runs` staged inside the upgrade transaction. A read-only successor
check finds the expected v4 initialization shape (nine tables; one metadata/state row,
three original initialization events, other tables empty), with no v5 audit/table
residue. There is no historical pre-diagnostic hash; do not claim historical byte proof.
Repair replaces typed scans with same-connection SQL-limited keyset pages, materialized
before nested lookups, and moves typed history/budget authentication ahead of owner-ID
fetches and owner JSON extraction. Unsupported history still refuses without pruning.
Only `entity_intent.py`/`ledger.py` change; all other 289 implementation identities,
including the original 34 controls, match. Four-target Ruff lint/format passes.
Separate **291-identity** transaction-repair freeze, SHA-256
`380d7867e18592f91803aada27b2e049984ed299408b2852dd0dbe576c7ba572`, binds the distinct
unchanged-control rerun: **34 passed in 125.03 s**, exit 0. Complete three-line report
reviewed and all **291 identities** match after notification. Genuine typed COMMIT,
restart, lost acknowledgment, original-bound post-COMMIT input, exclusion and original
corruption/budget controls now pass. Successful fixtures were cleaned by the harness;
reports are the durable green evidence. This is exclusion-only focused evidence, not
entity launch/completion/publication/recovery, affected/full regressions or Linux acceptance.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_intent.py §validate_history; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-intent-transaction-repair-first-rerun.txt \
  tests/test_coordination_entity_intents.py
```

Complete **464-line** successor documentation/privacy delta inspected, including
retained new Markdown; review SHA-256
`4256edfe929a5008eb6704228c0a856cf4e7a13752ba427941df044e11879940`.
The initial comparison omitted the retained new-page appendix; its separate report
is preserved but is not a deletion or complete-delta claim. Corrected comparison
shows the native-Mac tension page unchanged. Fresh scoped audit passes nine Markdown/
seven frontmatters, 232 grounding paths, 373 inline sources, 437 links and 61 sections;
both repository whitespace checks pass. Repair-result review was still pending.

Added a distinct **24-control** history module after that green, preserving all original
34 controls and all 291 repair identities. Two staged visibility controls, three
transaction-local corruption/rollback controls, ten budget-before-owner/payload checks,
three real keyset/tail-audit controls and six consistently rehashed semantic-corruption
controls retain genuine original observations. The SQL-delegating guard forbids
independent typed scans and early payload reads; changing real SQL page limits from
256 to one forces continuation without fabricated rows or replaced validators. This
does not qualify large retained histories or representative resources. Complete new
source reviewed; patch-only lint/format fixes preserve the 24 intended controls.
Fresh five-target Ruff lint/format passes. Separate **292-identity** first-history freeze
`dcc-linux-entity-intent-history-first-source-freeze.json`, SHA-256
`2b41275fafaddb5a7d526408d5678e0a278239ef1c4d919a541293b261e261aa`, adds only this module;
its distinct first run passes **24 controls in 79.82 s**, exit 0. Complete three-line
report reviewed and all **292 identities** match after notification, manifest hash
unchanged. All five control groups execute without setup masking; successful fixtures
are cleaned, retaining the report as durable evidence. Expanded history focus is green,
not combined-focus, affected/full or entity execution acceptance.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_intent_history.py -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-intent-history-first-run.txt \
  tests/test_coordination_entity_intent_history.py
```

Complete **428-line** successor documentation/privacy delta (including retained new
Markdown and the intervening acknowledgment edits) and **78-line** operator delta
reviewed. Wiki review SHA-256:
`d19b9172e799d0d4e27fe08afdfc7b901b277dba7f66278a5a33407c1937821b`.
Fresh scoped audit passes nine Markdown/seven frontmatters, 232 grounding paths,
376 inline sources, 437 links and 61 sections; both whitespace checks pass. No
whole-wiki lint or broader qualification claim. Complete new source is 316 lines,
SHA-256 `9d5ab7afeb7efd3cee9e6d63a530536069527fc82c7adb897c0d244faeadb530`.

Separate **292-identity combined-focus freeze**
`dcc-linux-entity-intent-combined-focused-source-freeze.json` retains exactly the same
identities/hash as the first-history snapshot. Main combined focus includes entity
receipts, both input modules, both typed modules, all three opt-in-v5 schema modules
and six original ledger/authority/completion/retry-history compatibility modules.
Standalone three-module entity-verifier focus passes **141 controls in 105.56 s**,
exit 0; complete four-line report reviewed and all **292 identities** match after
notification. Main combined focus passes **336 controls in 884.70 s**, exit 0;
complete seven-line report reviewed and all **292 identities** match afterward, hash
unchanged. Both focused runs are complete. Exclusion-only typed/input/schema/receipt
and original-ledger compatibility focus is closed; subsequent source work requires
new controls and a distinct successor freeze. These are focused gates only;
no affected/full regression or entity launch/
completion/publication/recovery/service/Linux acceptance is inferred.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-intent-combined-main-focus.txt \
  tests/test_coordination_entity_execution.py \
  tests/test_coordination_entity_observations.py \
  tests/test_coordination_entity_observation_qualification.py \
  tests/test_coordination_entity_intents.py \
  tests/test_coordination_entity_intent_history.py \
  tests/test_coordination_entity_upgrade.py tests/test_coordination_entity_schema.py \
  tests/test_coordination_entity_schema_history.py \
  tests/test_coordination_ledger.py tests/test_coordination_authority.py \
  tests/test_coordination_completion.py tests/test_coordination_completion_controls.py \
  tests/test_coordination_intentional_retry_upgrade.py \
  tests/test_coordination_intentional_retry_history.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-intent-combined-standalone-focus.txt \
  tests/test_entity_operation_verifier.py tests/test_entity_verifier_review.py \
  tests/test_entity_verifier_qualification.py
```

Complete **414-line** history-green/combined-pending wiki/privacy delta inspected,
including retained new Markdown; SHA-256
`4ac61806a70eed7a68e7fd09aa67c665757043eb3b026ff27ccb20bf6e064b13`.
The corresponding complete operator delta is **84 lines**. Fresh five-target Ruff
lint/format, scoped wiki audit (unchanged nine/seven/232/376/437/61 counts) and both
whitespace checks pass. Combined-focus results were still pending at this review;
no broader acceptance follows from these scoped checks.

Complete **283-line** standalone-green/main-pending wiki/privacy successor delta and
**86-line** operator delta reviewed; wiki review SHA-256
`6a72376005699b1444939d66c4f983c88d8de1fff711f8c29981e8dc5bf4f1d3`.
Fresh scoped wiki audit and both whitespace checks pass with unchanged counts.
Main combined focus was still pending at that review; its later green is recorded above.

Next sub-slice is main-side read-only completion authentication of actual independently
supervised current-generation entity results, with original typed input/intent/CLI
shutdown binding and unchanged ownership/cursor/authority. Add separate genuine red
controls before implementation. No caller publication dictionary or mutually rehashed
archive may authorize historical statistics, completion or reopening; durable typed
publication/authority linkage, entity launch/completion/recovery/service and wider
qualification remain later work. Retain all focused freezes and historical failures.

Complete **354-line** combined-main-green wiki/privacy successor delta and **90-line**
operator delta reviewed, including intervening acknowledgment edits and retained new
Markdown. Wiki review SHA-256:
`97254fc85527c5cb6f0855b61435744c9b57a6e7dba8965fcfb0a17ccced8e2e`.
Fresh five-target Ruff lint/format, scoped wiki audit (nine Markdown/seven frontmatters,
232 grounding paths/376 inline sources/437 links/61 sections) and both whitespace
checks pass; these are scoped checks only.

#### Main current-generation completion observations — read-only, active

Added a distinct **44-control** module before completion-adapter source work. Genuine
fixtures explicitly select v5, retain typed original input/intent evidence, perform a
separate original-bound post-COMMIT input check, then launch the real supervised CLI
in isolated tests. These test-only launches do not implement service launch permission.
Controls target genesis/replay four-hour completion, early original/prelaunch/receipt/
intent/clock refusals, restarted ownership, actual CLI aliases/bytes, rehashed completion
and historical-publication contracts, actual verifier artifacts, independent byte
budgets, post-CLI input arrival and deliberate isolated forward evolution. No semantic
refusal or completion-observation green is claimed before the first report review.
Complete 392-line source reviewed; new-target Ruff lint/format passes. All 292 closed
combined-focus identities are unchanged. Separate **293-identity** first-red freeze
`dcc-linux-entity-completion-observation-first-source-freeze.json`, SHA-256
`391a4a89a0f2c0016db5545f3f525752e08e50fbefe357339565692a41eceae0`, adds only this module.
The distinct first run finishes with **44 failures in 342.12 s**, exit 1. All 293
frozen identities match after notification. Complete **409-line lossless exact-line
review** inspected and byte reconstruction checked against the entire **1,783-line**
report, SHA-256 `9232844d69bd8cc9e3717af59291cf99a718ad7c9d74e54873a5c25f8c1e5466`.
Review SHA-256 `10d51602f2198051c23928611a14dc982fc81c5b22a49440091a764d97c7c621`.
Twenty-two missing-module failures, 19 launch-guard imports and three budget imports
mask every adapter assertion after genuine fixture execution; the forward fixture
also launches its second isolated CLI. No completion-adapter semantic refusal or green
is established. Failed fixtures/report/freeze retained; no test remained running at
first-red review closure.
Main completion authentication remains missing at this review; original-bound read-only
source work may begin, without ownership/authority/cursor transitions, historical
publication/recovery or broader Linux acceptance.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_observations.py -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-completion-observation-first-red.txt \
  tests/test_coordination_entity_completion_observations.py
```

Complete **244-line** completion-first-pending wiki/privacy delta inspected before
red-result reconciliation; review SHA-256
`c8c4990ab006ecaeb9ee7832c52f841ee503a54581aca45a9a4d114aba8e1e56`.
Scoped audit passes nine Markdown/seven frontmatters, 232 grounding paths, 378 inline
sources, 438 links/62 sections; both whitespace checks pass. These are scoped checks.

**Implementation successor, not accepted:** added the separate read-only main adapter
after complete red/identity review. It binds the retained typed original and acknowledged
same-session exclusion, separate post-COMMIT prelaunch observation, actual canonical
single-link CLI command/shutdown and distinct pretty-printed capture, original archived
publication report, and fresh canonical standalone request/result/shutdown. Bootstrap
provenance is preserved rather than replaced by the replay window. Request binds the
original authority/input core and intent/CLI supervision, with `publication: None`;
result requires exact completion core/transport fields, exact original hours/archive
counts and genesis or immediate-successor current generation. Budgets remain 64 KiB
results, 1 MiB requests and 128 KiB observations; refusal never prunes evidence.
No ledger rows, authority, cursor or `_entity_live_intent` transition is implemented,
including on refusal; no entity writer/service launch or historical fallback exists.
Complete source reviewed and two-target Ruff lint/format passes. All 293 first-red
identities remain unchanged; only `entity_completion.py` is added. Separate **294-identity**
implementation freeze `dcc-linux-entity-completion-observation-implementation-source-freeze.json`,
SHA-256 `45462cdd9a1547336a1faf732e1cf071f54b7c7929b8e8796923ac90dad0cc06`,
binds the unchanged 44-control implementation rerun. It finishes with **two failures /
42 passes in 470.91 s**, exit 1. Complete **81-line** report inspected, SHA-256
`36b4d712d6d20c7501d490696dcc1a72e2cd37202e348b9067e9e91018149523`;
all 294 frozen identities match after notification. Both failures are helper argument
collisions (`observe()` receives positional and keyword `prelaunch`) before adapter
invocation, masking the missing-prelaunch and precommit-substitution refusal assertions.
Those two refusals are not established; the initial completion focus is not accepted.
Failed fixtures/report/freeze remain retained; no test remains active at this review.
Next rename only the helper's positional parameter/default reference, preserving runtime
source and every refusal assertion, then freeze and rerun all 44 controls separately.
Broader completion qualification and both runtimes' affected/full gates remain separate.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_completion.py -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-completion-observation-implementation.txt \
  tests/test_coordination_entity_completion_observations.py
```

Complete **496-line** red-reviewed/implementation-pending wiki/privacy successor delta
inspected, including retained new Markdown and all intervening result edits. Review
SHA-256 `a9b2c41920542543565c1b86e043a5c1e3e3b4a0150de3e39a1a4aba23cbac82`.
Both operator documents remain unchanged from the pre-completion baseline. Scoped wiki
audit passes nine Markdown/seven frontmatters, 235 grounding paths/384 inline sources,
438 links/62 sections; both whitespace checks pass. Implementation result remained
pending at this review; no broader qualification follows.

**Fixture-only successor, initial focus closed:** renamed only the `observe` helper's positional
`prelaunch` parameter and default-value reference to `prelaunch_observation`. Complete
exact **two-line** diff reviewed; every assertion and all other **293 implementation
identities**, including runtime source, remain unchanged. Two-target Ruff lint/format
and PyUtil whitespace checks pass. Separate **294-identity** fixture-repair freeze
`dcc-linux-entity-completion-observation-fixture-repair-source-freeze.json`, SHA-256
`10e246d107a803bce6e7fbf19267a5f2c30f10c05f2685be6617a82fc0b27b05`, binds the all-44-control
rerun, which passes **44 controls in 471.51 s**, exit 0. Complete three-line report
inspected and all 294 frozen identities match after notification, manifest hash unchanged.
Report SHA-256 `8eed445d2dac67e006984382e6f122d49e592efa6473ee1273211575f49f80f1`.
The missing-prelaunch and precommit-substitution controls now reach adapter refusal
without verifier launch or row/data changes; no setup masking remains. Initial completion
observation focus is closed, not expanded completion or affected/full qualification.
Successful fixtures are cleaned by the retained harness; the report is retained evidence.
No test remains active at this review. Historical import-red
and implementation-helper failures retain their separate reports/freezes/failed fixtures.
Expanded qualification and affected/full remain separate; no permission transition.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-completion-observation-fixture-repair.txt \
  tests/test_coordination_entity_completion_observations.py
```

Complete **353-line** implementation-result/fixture-repair-active wiki/privacy successor
delta inspected, including retained new Markdown and the prior acknowledgment relocation.
Review SHA-256 `59ad03d29543c25e29b00800165197f69406483c127a8f73ef641df1a53bf7a0`.
Both operator documents remain unchanged; scoped audit passes nine Markdown/seven
frontmatters, 235 grounding paths/384 inline sources, 438 links/62 sections and both
whitespace checks pass. Follow-up wording distinguishes historical idle review from
the active fixture-repair rerun. This remains scoped review, not completion acceptance.

The subsequent initial green permits separate genuine artifact-rebinding/non-mutation
controls: actual archived publication report aliases, verifier artifact aliases/duplicate
fields, consistently rehashed CLI dictionaries versus original archive bytes, supervision/
result identities, clocks/count types/budgets and independent data corruption checks.
Keep historical reports/freezes distinct and no historical-publication fallback or
ownership/authority/cursor/acknowledgment transition. Wider service/completion/recovery
qualification remains later work.

**Separate expanded qualification, focused gate closed:** added **67 controls** in a new 470-line
module after initial-green/report/identity review; complete source reviewed and three-
target Ruff lint/format passes. All 294 initial-focus identities remain unchanged.
Genuine explicit-v5 fixtures and supervised CLI/verifier setup target original archive
aliases (three), verifier aliases (ten), actual duplicate fields (eight), rehashed actual
CLI statistics versus unchanged archive bytes (four), contract-only CLI dictionaries
versus actual originals (four), shape/count/hash/clock/scope contracts (14), both
supervision contracts (14), retained proof budgets (three), actual invalid entity/metrics/
compacted Parquet (three), a competing lock process (one), and typed-history budgets
before completion launch (three). Dictionary-only controls share one genuine live locked
fixture and deep canonical copies; file damage is isolated per control. Every group
compares complete ledger rows/data/high-water/live acknowledgment, without permission.
Contract validation is not file/data authority: a consistently rehashed structurally
valid dictionary still requires actual-original recheck and fresh independent data
verification; no original-generation historical authentication is implemented here.
Separate **295-identity** first-qualification freeze
`dcc-linux-entity-completion-qualification-first-source-freeze.json`, SHA-256
`6bc44a11aa46750e89ab183b4114851420e35590d05f0d84c16f877cf944e98e`, binds the first
run, which passes **67 controls in 353.73 s**, exit 0. Complete **three-line** retained
report inspected, SHA-256
`e42c01ded73970ce9f6c33b75d401c74b65c4f76bed19d2a7c2fe2f40a888494`;
all **295 frozen identities** match after notification, manifest hash unchanged.
All artifact/contract/data/lock/budget groups execute without setup masking and retain
unchanged rows/data/high-water/live acknowledgment. Expanded completion-observation
focus is closed, not combined focus, affected/full or writer/service/publication acceptance.
Successful fixtures are cleaned by the retained harness; reports remain durable evidence.
No test remained active at result review. Historical failures/freezes/fixtures retained.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_qualification.py -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-completion-qualification-first.txt \
  tests/test_coordination_entity_completion_qualification.py
```

Complete **572-line** initial-green/expanded-active wiki/privacy successor delta
inspected, including retained new Markdown and canonical promotion; review SHA-256
`7ed87fc1f057913efe9025b31eaa89d33b6550c5337162802e1fb49c29b699fd`.
Earlier complete 142-line fixture-repair acknowledgment delta also inspected. Both
operator documents remain unchanged from the pre-completion baseline. Fresh scoped
audit passes nine Markdown/seven frontmatters, 239 grounding paths/388 inline sources,
438 links/62 sections; both whitespace checks pass. Expanded result was pending at that review;
these checks confer no wider acceptance.

Next freeze a distinct unchanged **295-identity** successor for combined main completion/
input/typed/schema/receipt/original-ledger focus (prior 336 controls plus both completion
modules, **447 controls**) and independently rerun the standalone three-module entity-
verifier focus (**141 controls**). Keep runtime/controls fixed until both notifications,
complete retained reports and identity checks. Affected/full qualification stays separate;
new durable publication/launch/completion/recovery/service work requires genuine red
controls after combined-focus closure, not a permissive fallback.

**Combined read-only completion/exclusion focus, closed:** distinct
`dcc-linux-entity-completion-combined-focused-source-freeze.json` is byte-identical to
the reviewed first-qualification manifest: **295 identities**, SHA-256
`6bc44a11aa46750e89ab183b4114851420e35590d05f0d84c16f877cf944e98e`.
Main completion/input/typed/schema/receipt/original-ledger focus and standalone entity-
verifier focus run independently with distinct retained reports. No runtime/control
changes; three-target Ruff lint/format, scoped wiki audit and both whitespace checks
pass before launch. Standalone focus passes **141 controls in 110.49 s**, exit 0;
complete **four-line** retained report inspected, SHA-256
`a322c543efe4be755cc8239faaf471d9a9773a69086049277005cc3bb5823630`;
all **295 frozen identities** match after notification, manifest hash unchanged.
Successful standalone fixtures cleaned; report retained. Main combined focus passes
**447 controls in 1729.40 s**, exit 0; complete **nine-line** retained report inspected,
SHA-256 `3b371f6f53ee7309956032638ca5053b4034d983072f71c8567372e3d436ce78`;
all **295 frozen identities** match after notification, manifest hash unchanged.
Both focuses are complete and the read-only completion/input/typed/schema/receipt/
original-ledger compatibility focused gate is closed. Successful main fixtures cleaned;
reports remain evidence. No test remains active at this review. Affected/full,
durable publication, entity writer/service/recovery and Linux acceptance remain separate.

Fresh standalone-green/main-pending scoped wiki audit passes nine Markdown/seven
frontmatters, 239 grounding paths/388 inline sources, 438 links/62 sections; both
whitespace checks pass. Operator baselines and historical failures remain unchanged.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-completion-combined-main-focus.txt \
  tests/test_coordination_entity_execution.py \
  tests/test_coordination_entity_observations.py \
  tests/test_coordination_entity_observation_qualification.py \
  tests/test_coordination_entity_intents.py \
  tests/test_coordination_entity_intent_history.py \
  tests/test_coordination_entity_upgrade.py tests/test_coordination_entity_schema.py \
  tests/test_coordination_entity_schema_history.py \
  tests/test_coordination_ledger.py tests/test_coordination_authority.py \
  tests/test_coordination_completion.py tests/test_coordination_completion_controls.py \
  tests/test_coordination_intentional_retry_upgrade.py \
  tests/test_coordination_intentional_retry_history.py \
  tests/test_coordination_entity_completion_observations.py \
  tests/test_coordination_entity_completion_qualification.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py standalone \
  /tmp/opencode/dcc-linux-entity-completion-combined-standalone-focus.txt \
  tests/test_entity_operation_verifier.py tests/test_entity_verifier_review.py \
  tests/test_entity_verifier_qualification.py
```

Complete **408-line** expanded-green/combined-active wiki/privacy successor delta
inspected, including retained new Markdown and all result/status edits; review SHA-256
`70e72ecb8cc3ca48fd478e74b7e4b1ae9adde56b660b800da08a3cd3f1cc43b8`.
Both operator documents remain unchanged from the pre-completion baseline. Fresh scoped
audit passes nine Markdown/seven frontmatters, 239 grounding paths/388 inline sources,
438 links/62 sections; both whitespace checks pass. Both combined results were pending at that review;
these are scoped checks only, not wider acceptance.

Next add genuine red controls for bounded durable retention of an original-generation
completion independently observed while it is current, without releasing ownership,
advancing authority/raw cursor or granting entity launch. Preserve current-only adapter
contracts and original files; later historical verification must derive its publication
core from authenticated retained evidence, never a caller dictionary or today's aggregate.
Supervised entity launch/atomic completion-authority linkage, strict Linux dispatch and
audited original-clean resolution remain separate implementation slices. Retain the closed
295-identity combined freeze/reports; new controls need a distinct successor freeze.

Complete **342-line** combined-main-green wiki/privacy successor delta reviewed against
the last reviewed standalone-green complete snapshot, including retained new Markdown;
review SHA-256 `03805f220988f35ca84cbb5cd530ad43d12b47082881e1aef4a6d311bf2e720e`.
Both operator documents are unchanged. Fresh three-target Ruff lint/format, scoped audit
(nine Markdown/seven frontmatters, 239 grounding paths/388 inline sources, 438 links/
62 sections), both whitespace checks and the closed 295-identity check pass. These are
scoped checks only; no affected/full, entity service, endpoint or platform acceptance.

### Durable original-generation publication retention — active, not accepted

Added a separate **46-control**, **771-line** module before runtime implementation;
complete source reviewed, including pre-freeze formatting and the explicit non-hive
projection in the later-hour fixture. New-target Ruff lint/format and isolated collection
pass (**46 collected in 0.63 s**); collection is not execution or semantic acceptance.
Source SHA-256 `6748c0c972715f8e54804b267840bd3f9eb20468d8c535b18d7d01dad113b2a8`.
All **295** closed combined-focus identities are unchanged. Distinct **296-identity**
`dcc-linux-entity-publication-first-red-source-freeze.json`, SHA-256
`d56e311fdff9d5f6a469eb6b4624184a3b1e91e05f9b119e4f54aa85805b0f44`, adds only the
new control module. At first red, publication/writer runtime modules were absent and
typed history rejected every nonempty `entity_evidence`.

Controls specify planned `retain_entity_publication_prepared(ledger, prepared, now,
*, clock, original, prelaunch)` and `get_retained_entity_publication(ledger, run_id)`:
fresh current-only completion is obtained internally, bound to the acknowledged original
receipt/input/intent/post-COMMIT prelaunch and actual CLI/archive/shutdown/capture. No
caller completion/publication dictionary is accepted. The immutable envelope retains the
exact completion core with `publication_sha256: None`, original independent observation
and typed audit; successful retention changes only evidence/audit, not ownership, authority,
raw cursor, grants or acknowledgment. No entity launch is implemented.

Initial controls cover init/replay mixed and empty hours, exact core/transport identities,
fresh verification despite an old valid observation, artifact/data/clock refusal, absent
original-generation evidence after actual later-hour evolution, restart without runtime
reconstruction, copy-return/duplicate refusal, genuine before/after COMMIT process death
and lost acknowledgment, same-connection staged validation, rehashed semantic/audit/chain/
orphan corruption, bounded records/counts/aggregate/audits and budget-before-owner/payload
ordering. The historical verifier setup derives its `publication` from the planned
authenticated accessor while preserving original checkpoints and keeping the existing
completion adapter current-only. Test-only entity CLI launches grant no service permission.
After-COMMIT lost acknowledgment must retain evidence plus typed BLOCKED ownership; a
successful retention is not atomic completion or audited recovery.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publications.py -->
<!-- SPECULATIVE: atomic entity completion/recovery and wider publication/service qualification remain separate -->

First red is reviewed: **46 failures in 402.36 s**, exit 1. Complete **1,772-line**
`dcc-linux-entity-publication-first-red.txt` inspected, SHA-256
`b9e200009bd50754fd980218502b349bc8c007277199d07ce6687b4082d6bc9b`;
all **296 frozen identities** match after notification, manifest hash unchanged.
Both retained `publication-child.json` diagnostics were directly inspected: genuine
setup prints its run identity, then each child exits **1** at missing-module import,
not the required **87**. Neither publication COMMIT boundary executes. The entire
report is import-masked; no semantic refusal, corruption/budget or historical-publication
acceptance follows. Failed fixtures remain retained in `dcc-retained-39byuj6z`.
No test remained active and runtime/controls were unchanged at first-red review. Next was
bounded immutable original-publication evidence/audit and same-transaction history
authentication, replacing the unsupported-history guard rather than simply removing it.
Expanded publication, affected/full, atomic entity
completion/authority linkage, Linux dispatch/recovery, S3/resources and native-Mac remain
separate gates. Both operator baselines and historical failures are preserved.

Complete **488-line** publication-red-prepared wiki/privacy successor delta reviewed
against the reviewed combined-main-green complete snapshot, including retained new
Markdown; review SHA-256
`0c1c8910ca0da6ec52e54cc7d72cec8c51795b0fdae4af8835943028725e6221`.
Snapshot identity/current bytes and both operator baselines match. Fresh new-target
Ruff lint/format, scoped wiki audit (nine Markdown/seven frontmatters, 243 grounding
paths/391 inline sources, 439 links/63 sections), both whitespace checks and all
296 first-red identities pass before launch. No runtime/control changes or broader
acceptance; first-red results awaited notification and complete report/identity review then.

Complete **159-line** prepared-to-active wiki/privacy successor delta also inspected,
including status reconciliation and retained new Markdown; review SHA-256
`9da885b32c880428e69ab25fb196c482d43da09e0c315877b0a5f754ab76308c`.
Both operator baselines remain unchanged; fresh scoped audit and both whitespace
checks pass with unchanged scope/counts. First-red result was pending at that review.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-publication-first-red.txt \
  tests/test_coordination_entity_publications.py
```

**Publication implementation, initial focus closed:** added the separate 285-line
`entity_publication.py` after complete red/child/identity and **325-line** wiki/privacy
successor review (SHA-256
`dfb7b8c9f50540887e389296971505c37eb10405c41c9528346bd90ca75c45a0`).
Retention obtains fresh current-only completion internally and rechecks actual original
artifacts/captures before immutable evidence/audit COMMIT. Authenticated accessor/history
use retained JSON only, preserving the exact original core and never today's aggregate.
Same-connection SQL-limited materialized keyset pages bind sequence/predecessor, original
intent, envelope/core/observation and matching publication audit, including staged rows.
Publication count/record budgets run before owner/payload reads; combined intent/publication/
audit history remains capped at 64 MiB with bounded unresolved-audit capacity reserved
before launch. No pruning or successful ownership/authority/raw-cursor/grant/launch/
acknowledgment transition. Only committed lost acknowledgment blocks the original owner
while retaining publication evidence; retention remains distinct from completion/recovery.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_publication.py; ../Wintap-PyUtil/wintappy/coordination/entity_intent.py §_budget/validate_history -->

Complete new source and typed-history delta reviewed; four-target Ruff lint/format and
PyUtil whitespace pass. The only prior identity changes are `entity_intent.py` history
integration and two `ledger.py` comments; other **294 first-red identities**, all controls,
current-only completion/standalone runtime and both operator baselines remain unchanged.
Distinct **297-identity** `dcc-linux-entity-publication-implementation-source-freeze.json`,
SHA-256 `587df5d2a07bd4cb33fc2c1be7e234a7861a749f20daf7a0d9287069d6688b51`, binds
the unchanged **46-control** implementation rerun. It passes **46 in 629.02 s**, exit 0;
complete **three-line** report inspected, SHA-256
`90e490a24bf6691114fcd2f66d4f071ce137f979dd516256c97749218e89e0bf`.
All **297 frozen identities** match after notification, manifest hash unchanged. Original
fresh-data/artifact/clock/budget/refusal, immutable core/accessor, restart, actual before/
after publication COMMIT process-death/lost-ack, staged same-connection history and genuine
later-generation historical requests now execute without import masking. Successful fixtures
were cleaned by the unchanged runner, so no separately retained green child diagnostics
are claimed; historical first-red diagnostics/fixtures/report remain retained. Initial
publication focus is closed, not wider acceptance. No test remains active at this review.
Next qualify separate rehashed-envelope/audit/SQL-byte/keyset-tail controls and retain new
actual crash-child diagnostics under an unchanged source freeze. Wider publication/combined/
affected/full, entity writer/service/
recovery, Linux/S3/resources and native-Mac remain separate.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-retained.py main \
  /tmp/opencode/dcc-linux-entity-publication-implementation.txt \
  tests/test_coordination_entity_publications.py
```

Complete **514-line** implementation-pending wiki/privacy successor delta inspected,
including retained new Markdown; review SHA-256
`9dc3af2c350eadd01bb5ec6aa0502f3dcd1d72222d966265251fd3d832d12202`.
Both operator baselines unchanged; scoped audit passes nine Markdown/seven frontmatters,
247 grounding paths/397 inline sources, 439 links/63 sections and both whitespace checks
pass. All 297 implementation identities checked before launch; the retained rerun was
active and no result was accepted at that review.

Complete **157-line** implementation-pending-to-active wiki/privacy successor delta also
inspected, SHA-256 `0f6ef39c622c3d3f119e6f20dcfeecc3d8b0eea967d5959735bc6ef052ac7fee`.
Operator baselines remain unchanged; fresh scoped audit and both whitespace checks pass
with unchanged counts. Historical first-red idle wording is explicitly scoped to that
review, not the implementation rerun active then.

Complete **454-line** active-to-initial-green wiki/privacy successor delta inspected,
including the subsequent acknowledgment edits and canonical promotion; review SHA-256
`b92f474b3a8d864cd5776368bcf591edf7c5006822653db3ac8792034e79b5d8`.
Fresh four-target Ruff lint/format, scoped audit (nine Markdown/seven frontmatters,
248 grounding paths/399 inline sources, 439 links/63 sections), both whitespace checks,
operator baselines and all **297** closed identities pass. Historical first-red/input
wording is scoped to those earlier slices. These checks do not qualify expanded publication,
entity permissions, affected/full, S3/resources or native-Mac.

**Separate publication qualification, closed:** added **77 controls** in a fully reviewed
**651-line** module, source SHA-256
`54e0c8426f5a7ec4b29d6f4bb32196bcd37e35f083c1828060724b7a70e9170a`.
A genuine independently observed original publication and audited BLOCKED owner supply
rollback-isolated envelope/core/observation/audit/canonical-JSON controls. Consistent outer
digest/audit and transport/capture rehashing do not relax exact original scope/type/window/
generation/publication contracts. No history is manufactured for acceptance; malformed
tail rows are deliberate refusal fixtures. Runtime/artifact reconstruction is forbidden
during history checks; every refusal preserves injected rows until explicit test rollback,
and leaves original artifacts/data/authority/ownership/live acknowledgment unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py -->

Budget controls use actual SQL UTF-8 byte sizes above default 128-KiB publication/16-KiB
audit caps while character counts still fit, exact observed positive aggregate/count
limits and equality boundaries. Three SQL budget summaries must precede any typed owner
identifier, audit or publication payload across validation, both ledger accessors, public
accessor and retention. Real same-connection one-row SQL pages materialize before nested
lookups and reach genuine publication/audit tails plus injected orphan/chain/unsupported
tails; this is bounded-paging evidence, not retained-state sizing or completed multi-owner
history. Separate persisted-corruption controls require failed ordinary reopen to preserve
all original rows/artifacts, without runtime reconstruction.

New diagnostic-retaining runner is separately reviewed (**69 lines**, SHA-256
`8bf816601713506cdbc443f810eed74b499193d82813b308eaea78d0c812cbb3`), frozen by
`dcc-linux-entity-publication-qualification-runner-freeze.json`. It uses the explicit
runtime and isolated temporary directory, refuses report overwrite and retains every
fixture on success or failure. Its sidecar records actual child-diagnostic byte/hash
identities; it does not reconstruct deleted initial-green diagnostics. The unchanged
original before/after-COMMIT process-death controls are included as **two additional
executions**, so the separate qualification target is **79 controls**.

Six-target Ruff lint/format and isolated collection pass: **79 collected in 0.69 s**,
exit 0; complete **82-line** collection report inspected, SHA-256
`bf059d8fe077aae1a4760a78e78bc3bfe483e50824133943b90c6960761996da`.
Collection executes no data/crash boundary. All **297** closed source identities and
both operator baselines remain unchanged. Distinct **298-identity** successor
`dcc-linux-entity-publication-qualification-source-freeze.json`, SHA-256
`03edefc7bdb4a912c27339b98b2a4332963980b48c01dcf123fe440b8d3d71f5`, adds only the
new qualification module. The separate **79-control** retained first execution passes
**79 in 100.90 s**, exit 0. Complete **four-line** report inspected, SHA-256
`b36c3adc6e1d117a8f6601ee698907b2ca85e9f5541e1ba0105551afbceab1b6`;
complete **29-line** `runner-result.json` inspected, SHA-256
`d245c0b0e9416e7841da49328dd5f01ba51be494ba2dff35961e1b13cc4b7359`.
All **298** frozen source identities, separately frozen runner and both operator baselines
match after notification; manifest unchanged. All successful/failed fixtures remain at
`/tmp/opencode/dcc-diagnostics-4r6vk2rw`; historical first-red fixtures/diagnostics remain
separate and preserved. Expanded publication focus is closed, not wider acceptance.
A distinct combined **570-main/141-standalone** focus must follow
expanded closure before entity-writer work; affected/full and Linux/S3/resources/native-Mac
remain separate. Historical failures/unrelated artifacts are retained; no remote/production
operation, installed scheduling, utility implementation, commit or push.

Both actual `publication-child.json` diagnostics directly inspected and byte/hash-checked
against the sidecar. Each is **93 bytes**, exit **87**, empty stderr and a genuine run-ID
line on stdout. The unchanged test's first parameter targets
`before_entity_publication_commit`, the second `after_entity_publication_commit`; the
child's only exit-87 path is that selected hook, with an assertion if it never executes.
Hashes are `3b06055993b7e1d7c168cb305c71acf60bb5dd603e4f1883ca90d69a22cad1f3`
(before) and `7993ceed18f78f106f4dfa579427eabc96fb74ae9695833100869773ad8934cf`
(after). Required assertions execute: restart retains the original BLOCKED owner, unchanged
raw cursor and no authority/raw completion/admission; before-COMMIT publication is absent,
after-COMMIT publication is authenticated and retained, second reopen preserves rows and
raw/compacted inputs remain unchanged. These are actual new process-death observations,
not reconstructed initial-green diagnostics, physical-power-loss or load attribution.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publications.py §test_actual_publication_commit_process_death_keeps_original_exclusion -->

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-publication-qualification.txt \
  tests/test_coordination_entity_publication_qualification.py \
  tests/test_coordination_entity_publications.py::test_actual_publication_commit_process_death_keeps_original_exclusion
```

Complete **546-line** initial-green-to-qualification-prepared wiki/privacy successor delta
inspected, including acknowledgment edits, retained new Markdown and scope reconciliation;
review SHA-256 `c769575f5caf0b2f891a4c0265c43f502dae8d2e929dcbacc275932df3d0fde2`.
The new preparation entry is placed at the log tail without disturbing prior history.
Fresh scoped audit passes nine Markdown/seven frontmatters, 252 grounding paths/402 inline
sources, 439 links/63 sections; both whitespace checks and all **298** successor identities
pass, both operator baselines unchanged. No actual child diagnostics are claimed before
the separate retained execution.

Complete **133-line** prepared-to-ready wiki/privacy successor delta inspected, SHA-256
`e247fde8f6ca78f2ba9ffc72f5984373130aed2b03f5c791b3e45cf84dc17095`.
Both operator baselines and the separately frozen runner match. Fresh scoped audit and
both whitespace checks pass with unchanged counts; all 298 successor identities checked,
and exact successor comparison confirms only the new qualification module was added.
Launched the separate 79-control run with all fixtures retained on either outcome; no
expanded or wider result is accepted before report/diagnostic/identity review.

Complete **231-line** ready-to-active wiki/privacy successor delta inspected, SHA-256
`492b22b72c910e5d4e9ac2b547e691719f2360ae7dc6aa107068220c8d79cda2`.
Both operator baselines remain unchanged; fresh scoped audit and both whitespace checks
pass with unchanged counts. The separate qualification result was pending at that review;
no source, control or runner changes or wider acceptance followed it.

Complete **90-line** active-acknowledgment wiki/privacy successor delta was inspected,
SHA-256 `b88cf1cee644771d5f3b0f9ad3c986c88df1d5ace1c49753f4bb2dee19938b72`;
the previously reviewed complete snapshot is unchanged at result arrival. No test remains
active at this expanded-result review. No runtime/control/runner repair was needed.
Reconcile scoped facts to canonical ETL documentation, review the complete successor
wiki/privacy delta and run fresh scoped checks before the distinct combined focus.

Complete **429-line** active-to-expanded-green wiki/privacy successor delta inspected,
including all result/diagnostic/identity acknowledgment edits and canonical qualification
limits; review SHA-256
`443ec16d6ddfc9904a9dba04245f2c93e585d8e3d983fa4496597e0e3fd91fd7`.
Fresh six-target Ruff lint/format, scoped audit (nine Markdown/seven frontmatters,
253 grounding paths/403 inline sources, 439 links/63 sections), both whitespace checks,
all **298** closed source identities and both operator baselines pass. These checks close
the scoped expanded-publication record, not affected/full, entity permission or Linux.

**Combined publication/completion/exclusion focus, closed:** distinct
`dcc-linux-entity-publication-combined-focused-source-freeze.json` preserves exactly the
closed **298** identities, byte-identical manifest SHA-256
`03edefc7bdb4a912c27339b98b2a4332963980b48c01dcf123fe440b8d3d71f5`.
Distinct `dcc-linux-entity-publication-combined-runner-freeze.json` preserves the unchanged
diagnostic-retaining runner; manifest SHA-256
`4d9f251a7e4f162962ce2e56082e2982b2e94206401b2a0e1a1f1c5fd74c6225`.
Main includes the closed **447-control** completion/input/typed/schema/receipt/original-
ledger focus plus original publication **46** and separate qualification **77**, totaling
**570 controls**; the two crash controls are already among those 46, not duplicated.
Standalone independently runs the unchanged **141-control** three-module entity-verifier
focus. Both use distinct overwrite-refusing reports and retain all fixtures/actual child
diagnostics; historical failures remain untouched. Complete **312-line** green-to-combined-
prepared wiki/privacy successor delta inspected, SHA-256
`5c501c69103ab4839a8b05ab3fb3b2f5785640a34b4cad6aabc4459cad6ced3d`;
fresh scoped audit and both whitespace checks pass with unchanged counts. All **298**
combined identities checked, with both operator baselines and separate runner unchanged.
Standalone passes **141 in 109.28 s**, exit 0; complete **four-line** report inspected,
SHA-256 `b261df0877acd48cbccc85ba47b317428c872ba8d298e916900d01faf5c8a5c4`.
Complete **21-line** runner sidecar inspected, SHA-256
`8acbf7bb92d5614e19ead798fd1a1a8c78c92e623fe92d3de977fbbac866500f`;
all **298** frozen source identities, separately frozen runner and both operator baselines
match after notification, manifest unchanged. Every standalone fixture is retained at
`/tmp/opencode/dcc-diagnostics-p3fzdoh2`; no publication crash-child diagnostics are expected
or present in this standalone focus. Main passes **570 in 2430.83 s**, exit 0; complete
**ten-line** report inspected, SHA-256
`456e55ccdd88ab9af0c95c6a44f65ba22f2df9b526349fa064bd66494e5edb32`.
Complete **45-line** runner sidecar inspected, SHA-256
`e12565dc697d596ee6abdbf2acfed2eb0ceb7282dedffb27f9072188e68f67bd`.
All **298** frozen source identities, separately frozen runner, both operator baselines
and the reviewed standalone report remain unchanged after main notification. Every main
fixture is retained at `/tmp/opencode/dcc-diagnostics-knnqhao0`. Both actual publication
child diagnostics directly inspected and sidecar byte/hash-checked: **93 bytes** each,
exit **87**, empty stderr and original run-ID stdout. Before-COMMIT SHA-256
`c081beac95fd841d2949545db022a46ceace780c5be73f4907b8423a37525daf`; after-COMMIT
SHA-256 `029c9fc88c584fd2bb4dbb5f0d81182434658da50e2416291c04474b94a2401c`.
The unchanged selected hooks and absent-before/retained-after publication, BLOCKED original
exclusion, raw-cursor/authority/admission and second-reopen assertions execute, not setup
failure or physical-power-loss evidence. No load attribution is made from run duration.
Both combined focuses are complete and the publication/completion/input/typed/schema/
receipt/original-ledger compatibility focused gate is closed. No test remains active at
this result review; no source/control/runner changes. Retain every fixture/report/identity
before the next separate entity-writer slice. Affected/full,
service/recovery, S3/resources and native-Mac remain separate.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-publication-combined-main-focus.txt \
  tests/test_coordination_entity_execution.py \
  tests/test_coordination_entity_observations.py \
  tests/test_coordination_entity_observation_qualification.py \
  tests/test_coordination_entity_intents.py \
  tests/test_coordination_entity_intent_history.py \
  tests/test_coordination_entity_upgrade.py tests/test_coordination_entity_schema.py \
  tests/test_coordination_entity_schema_history.py \
  tests/test_coordination_ledger.py tests/test_coordination_authority.py \
  tests/test_coordination_completion.py tests/test_coordination_completion_controls.py \
  tests/test_coordination_intentional_retry_upgrade.py \
  tests/test_coordination_intentional_retry_history.py \
  tests/test_coordination_entity_completion_observations.py \
  tests/test_coordination_entity_completion_qualification.py \
  tests/test_coordination_entity_publications.py \
  tests/test_coordination_entity_publication_qualification.py
.venv/bin/python -B /tmp/opencode/dcc-run-tests-keep-diagnostics.py standalone \
  /tmp/opencode/dcc-linux-entity-publication-combined-standalone-focus.txt \
  tests/test_entity_operation_verifier.py tests/test_entity_verifier_review.py \
  tests/test_entity_verifier_qualification.py
```

The source/runner freezes are unchanged across both active launches. Passing collection or
the earlier 79-control focus cannot replace these distinct combined execution results.
Both focused results and complete evidence/identity checks are reviewed. Combined focus is
closed, not entity permission/affected/full or wider acceptance.

Complete **283-line** prepared-to-active wiki/privacy successor delta inspected, SHA-256
`25bf41640c53502d2f890870cb6f305fd6427424424482cb775c88fbfcb87afa`.
Both operator baselines and separately frozen runner unchanged; fresh scoped audit and
both whitespace checks pass with unchanged counts. Both combined results were pending at
that review; no source/control/runner changes or wider acceptance followed it.

Complete **80-line** active-acknowledgment wiki/privacy successor delta inspected, SHA-256
`aacee123eaf322fb413ca627e871f22419794a058a881e49a3cd2eb3fe515aff`.
Current complete wiki snapshot matches that reviewed predecessor at standalone-result arrival.
Main remained untouched and active at standalone-result review; no polling, source work or
wider acceptance followed that notification.

Complete **296-line** active-to-standalone-green wiki/privacy successor delta inspected,
SHA-256 `d64d5a852e68e485b04321c3a6cf3cc54aca9d1f815d8141f2827934fe9f66d5`.
Both operator baselines unchanged; fresh scoped audit and both whitespace checks pass
with unchanged counts. Main was pending and all source/controls/runner remained fixed at
that review; it did not establish combined closure or wider acceptance.

Complete **80-line** standalone-green-acknowledgment wiki/privacy successor delta inspected,
SHA-256 `15342dfae4309f6562847d6dd48fd096e36188cd6fe529fbacc76a4f7989d39f`.
The current complete wiki snapshot matches that reviewed predecessor at main-result arrival.
Reconcile combined closure and canonical qualification limits, then completely review the
successor wiki/privacy delta with fresh scoped checks before any entity-writer source work.
Existing **22** writer/ownership/completion/crash controls still require explicitly upgraded
v5 fixtures and a separately frozen reviewed red before implementing the missing writer.
Supervised launch/atomic completion-authority linkage, strict Linux dispatch and audited
original-clean resolution remain subsequent slices, never permission from retained publication.

Complete **383-line** combined-green wiki/privacy successor review and fresh six-target
Ruff lint/format, scoped audit (nine Markdown/seven frontmatters, 253 grounding paths,
403 inline sources, 439 links/63 sections) and both whitespace checks passed. Review
SHA-256 `40b0abfb8436faf7df3780c8652ad0eb43a9fd0426109545ea2b460bc7327c9c`;
complete snapshot and all 298 source/runner/operator identities rechecked unchanged before
writer fixture preparation. This acknowledges combined focused closure only. The original
416-line writer module is separately retained before deliberate fixture/diagnostic changes;
its assertions and shared v4 `seed_scope` must remain unchanged.

### Entity writer explicit-v5 continuation — no launch acceptance

The original 22 writer controls now use a local `writer_scope` wrapper that performs a
confirmed explicit-v5 upgrade. Shared `seed_scope` and all other imported helpers remain
byte/AST-equivalent; all assertions and parameterizations are unchanged. Actual process
results are saved before crash/lock assertions, including failures. The 450-line successor
module SHA-256 is `124c0b5d3010f4d7d8f2dcaed2ba3c71ca57efeb7492bc48405a524d0ad23f5f`;
the original 416-line bytes remain separately retained. Full fixture/diagnostic delta and
separate 74-line runner reviewed; two-target Ruff lint/format and 22-control collection pass.
Collection is not execution or a semantic refusal.

Distinct first-red source freeze retains 298 identities, SHA-256
`7998bf2bb21406bac7822fd2e70bd7fb8c6d77dfd865e3743d3011fe739434ce`; exactly
`tests/test_coordination_entity_operations.py` changes from closed combined history, with
the other 297 identities unchanged. Separate writer runner SHA-256
`dc8996538b8c5942414ff0a68bb47ff0be717f797f3a7f9862093279eeedf204`, runner manifest
SHA-256 `55bb4fba5664e6dd3372ede28bb44168d858b4d4fbbc92cc24a1ac150180baba`.
The closed publication runner and both operator baselines remain unchanged. Every fixture,
historical failure and actual child diagnostic is retained.
Complete **252-line** prepared wiki/privacy successor delta inspected, SHA-256
`b2b29940776e7322579e6333378aedf89ce0035abbb383ab203b1afacff1c695`.
Fresh scoped audit (nine Markdown/seven frontmatters, 253 grounding paths/403 inline sources,
440 links/64 sections), both whitespace checks and all 298 writer-red identities pass.
The distinct red completed: **22 failures / 45.76 s**, exit 1. All are missing-module/
import-masked failures. Complete **1,010-line** report, **36-line** runner sidecar and all
four actual child diagnostics directly reviewed after notification. Each child exits 1
with empty stdout at the missing `wintappy.coordination.entity_writer` import, before any
selected hook; no competing-lock child ran. None of the launch, COMMIT, lock, refusal or
recovery semantics are qualified. Runtime remains unimplemented; no test remains active.
All 298 source identities, separate runner and both operator baselines match after result
review; historical fixtures/failures remain untouched.

Report SHA-256 `904b7fe5d4d666da90f19e3c63ad73a2ba82932519bc84675c8b3e5ee647f5cf`;
sidecar SHA-256 `6fd5216c48faa7be26b6fa7221435e349ebc2e85c752253e6a40abf5832699d6`.
All four 195-byte `entity-child.json` files have SHA-256
`7aa51bae3bd64db730aa50e135fade7665041fb04119dcf9c8b58db78f7cdda3` and are retained
under `/tmp/opencode/dcc-writer-diagnostics-j48pr9vh`. Review the complete active/result
wiki/privacy successor and fresh scoped/source/runner/operator checks before runtime coding.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-writer-first-red.txt \
  tests/test_coordination_entity_operations.py
```

Successful typed history/evidence still needs a separately authenticated design: immutable original
publication must not be overwritten to satisfy the `entity-only-completion` accessor. Original
intent authority/cursor bindings must remain authenticated across legitimate later evolution.
Launch/atomic completion-authority linkage, strict Linux service dispatch, original-clean
resolution and pending-publication repair/retry are not qualified by the closed read-only
focus. Affected/full, S3/resources/native-Mac and broader Linux acceptance remain separate.

Complete **324-line** prepared-to-active/result wiki/privacy successor inspected, SHA-256
`c2697aea545b250cc34ffced72d86d1bfc3169d78f86700690665c2e0fffede6`; fresh scoped
audit passes nine Markdown/seven frontmatters, 253 grounding paths/403 inline sources,
440 links/64 sections. Both whitespace checks, two-target Ruff lint/format and all 298
source identities/both runners/operator baselines/red-evidence identities pass. This closes
red evidence reconciliation only, not writer semantics. Runtime coding may follow reviewed
distinct completion/history design and genuine additional controls; no existing controls,
original publications or unresolved audit-count refusals may be weakened.

Selected a separate typed-event completion record/authority-reference design without v5
table/column changes; original publications remain immutable and public one-hour validation
unchanged. Separate fully reviewed **257-line / 20-control** history module adds genuine
success/replay/original preservation, rehashed corruption/non-mutation, record/aggregate/
audit/count budgets and original-clean/completion-COMMIT acknowledgment recovery controls.
New-target Ruff lint/format and collection pass; no success semantics executed yet. Distinct
299-identity red freeze SHA-256
`2c645d248b8370b115b844d9168bd56eff5f974dc9575bd2b1c5297da168e903` adds only this module;
all 298 writer-red sources, separate runner and operators unchanged. Control SHA-256
`bcaba1e1403ad533333672eceb5e02f36224f60da034ac943d05eb3df63463f4`.
Run only after complete successor wiki/privacy/fresh checks; retain all fixtures and complete
report/identity review before runtime implementation. Real completion-process death, stronger
budget-before-fetch/keyset, raw-cursor evolution and expanded recovery qualification remain
additional gates, not implied by these controls.

Complete **282-line** design/red-prepared wiki/privacy successor reviewed (SHA-256
`2a1560d877572948b4754f02a99b6928b71d9113921d1d2ef8fbdbd4894694d6`); fresh scoped
audit and both whitespace checks pass. Separate 20-control red completes with **four
failures / 16 setup errors / 3.52 s**, exit 1, all missing-writer/import-masked. Complete
report and 19-line sidecar inspected; no child diagnostics expected or produced. Report
SHA-256 `8d6b01bc7da753ffe1cfa4e4a7fbc2247a13192fad423e6e439814ef7143dc81`;
all 299 sources unchanged after execution, every fixture retained under
`/tmp/opencode/dcc-writer-diagnostics-tv9uulp4`. No success/corruption/budget/recovery
semantics executed; no test remains active. Preserve both reds and all frozen controls.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-writer-history-red.txt \
  tests/test_coordination_entity_writer_history.py
```

### Linux entity writer runtime successor — unqualified

The complete **184-line** history-red result successor has been re-read and acknowledged;
its reviewed snapshot remains the pre-runtime wiki baseline. Five-file runtime successor
review now covers `entity_history.py`, `entity_writer.py`, `entity_intent.py`,
`entity_publication.py` and the ledger's changed accessor/authority/history seams. Initial
unformatted bytes are retained separately under
`/tmp/opencode/dcc-linux-entity-writer-unreviewed-runtime/`; scoped formatting does not
change the frozen 22-writer/20-history controls or their runner. Eight-target Ruff lint
and format checks pass. These are source checks only, not launch/history acceptance.

The implementation adds distinct bounded typed-event completion records and separate
authority references, immutable original-publication access, supervised post-COMMIT
input/CLI/completion ordering and a narrow original-clean current-only recovery seam.
Source review repaired duplicate-completed-receipt refusal so it cannot block an old
successful owner, and added pre-fetch authority size/count plus exact keyset-tail checks
so nonpositive sequences cannot be silently skipped. Original raw history/cursor and
authority predecessors remain linked; v5 tables/columns, public one-hour validators,
read-only completion/input adapters, standalone runtime and operator documents are unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_history.py; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate_authority_checks -->

**Known open boundary:** retained committed completion acknowledgment resolution still
explicitly refuses. A separate immutable audited resolution record is required; neither
original completion nor publication may be overwritten. Recovery clocks, exception/COMMIT
uncertainty, original authority/raw-cursor authentication and budget-before-fetch/keyset
behavior remain unqualified. Real completion-process-death and expanded recovery controls
remain separate. No green is claimed; freeze a distinct successor and execute the unchanged
42 controls with all fixtures/actual diagnostics retained, then review the full report,
sidecar, children and all identities before any repair. Dispatch/affected/full, isolated
S3/resources and native-Mac remain open; no remote/production/scheduling/commit/push.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-writer-runtime-first.txt \
  tests/test_coordination_entity_operations.py \
  tests/test_coordination_entity_writer_history.py
```

First runtime execution completed on a distinct **301-identity** source freeze,
SHA-256 `268a208d3b7fb871e55416906da0c062815c60b21fbab85256f5f1d00337f431`.
Only the deliberate five-file runtime successor differs from the history-red freeze;
both frozen controls, runner, operators and other 296 identities remain unchanged.
Complete **300-line** runtime-prepared wiki/privacy delta inspected, SHA-256
`b6b89ff977fca52fea22880d7ac0303a53a95ac25850cbc0f36500bab07e91d4`; fresh scoped
audit passes nine Markdown/seven frontmatters, 253 grounding paths/406 inline sources,
441 links/65 sections, with both whitespace checks passing. Keep sources/controls/runner
fixed through notification and full report/sidecar/actual-child/all-identity review.

Result: **40 passed / two failed / 244.11 s**, exit 1. Complete **245-line** report,
**49-line** sidecar and all **seven** actual diagnostics reviewed. Four crash children
exit 87 with empty stderr at the original intent/launch boundaries; three competing-lock
children exit 88 with empty stdout/stderr. Those controls now execute, unlike the retained
import-masked reds. All 301 source identities, runner and both operator baselines remain
unchanged. Fixtures remain under `/tmp/opencode/dcc-writer-diagnostics-ftlupoih`.
Report SHA-256 `5653b402e853b66079cb686525cfc2610a3332830d5ca288652cafd4d5aa666c`;
sidecar SHA-256 `a4d768f8cc5964016944258d58bb401a8a76476dd17089b7a2994937f340a091`.
No physical-power-loss or workload-attribution claim follows from these children/duration.

The failures are separate: after-completion-COMMIT acknowledgment resolution deliberately
refuses its missing immutable disposition; original-publication clean resolution reaches
fresh verification but refuses a January recovery clock preceding its real November restart
block. Read-only retained-ledger inspection confirms the latter keeps one original publication,
zero completion records and `BLOCKED`; the lost-ack fixture keeps one completion and authority
under `BLOCKED`. Raw cursor/history remain unchanged. Preserve both failures. The clock fixture
needs a scoped synthetic reopen clock, not weakened rollback refusal; add an early block-clock
control and distinct immutable acknowledgment-resolution controls before runtime repair.
No run remains active and no full 42-control green is established. Complete result wiki/privacy
review and fresh checks precede any deliberate control/runtime successor.

### Immutable acknowledgment-resolution controls — prepared, runtime unchanged

The complete **287-line** first-runtime result wiki/privacy successor is acknowledged;
fresh scoped audit and both whitespace checks pass. Original **257-line** history controls
are retained as `/tmp/opencode/dcc-linux-entity-writer-history-original-controls.py`.
Only the publication-resolution fixture gains a function-scoped synthetic reopen clock;
import ordering is formatting-only. AST checks confirm every original assertion and
parameterization, all shared helpers and every other function remain unchanged. The original
40/two-failure report/fixtures and 301-identity freeze remain untouched.

Separate reviewed **407-line / 29-control** resolution module covers early block-clock
refusal before a verifier, fresh immutable acknowledgment resolution with/without original
publication, actual-original artifact rechecks, changed-data verification, rehashed corruption,
budgets and before/after resolution-COMMIT uncertainty (including original-clean completion).
Four-target Ruff lint/format pass; collection finds **49** history/resolution controls.
These controls have no result yet. The runtime still explicitly refuses committed completion;
new corruption/budget controls require genuinely resolved fixtures and may be setup-masked
until implementation. Existing refusals alone do not qualify original-artifact authentication.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_resolution.py; ../Wintap-PyUtil/tests/test_coordination_entity_writer_history.py -->

Distinct **302-identity** control-red freeze SHA-256
`1475f622f19fdd7452d1bed6eada02db84b0cd3056b1e716b179caf91d80e901` adds only the new
module and scoped fixture correction; all other **300** runtime-first identities remain
unchanged. Frozen writer controls/runner, operators, qualified standalone runtime and public
contracts remain unchanged. Complete successor wiki/privacy/fresh checks precede the following
red; full report/sidecar/actual diagnostics and all identities precede runtime repair.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-resolution-controls-red.txt \
  tests/test_coordination_entity_writer_history.py \
  tests/test_coordination_entity_resolution.py
```

Selected resolution design uses separately bounded hash-linked typed records/audits, never
overwritten original completion/publication or release inferred from retained evidence.
No writer/history green, broader Linux/service/affected/full, S3/resource or native-Mac
acceptance follows. No remote/production/scheduling/utility/commit/push action.

Resolution-control red completes: **25 passed / nine failed / 15 setup errors**, **343.58 s**,
exit 1. Complete **1,277-line** report SHA-256
`1913b3085ca241bf36da493bd1b5e69289eff8d278d418a43e606422685149ab` and **20-line**
sidecar SHA-256 `cff1fa73bbef2dd68c66035004aef67ba3483e1c0b943acaf64e7cf0fa13cbaa`
reviewed; all **302** source identities, frozen runner and operators match. Fixtures remain
`/tmp/opencode/dcc-writer-diagnostics-36nsrg3u`. No crash/lock diagnostic controls ran in this
focus; the sidecar's empty diagnostic map does not imply no supervised children.

The scoped publication/reopen-clock correction passes. One original history failure remains
the deliberately unimplemented acknowledgment-resolution path. New early-clock failures show
the uncommitted recovery reaches late staged refusal **after** genuine successful verification;
committed recovery instead reaches the blanket refusal. Read-only failed-ledger/capture
inspection authenticates both retained block clocks and actual verifier stdout/stderr identities.
Original-clean recovery's after-COMMIT failure really leaves **DRAINING**, with retained
completion/authority and unchanged raw cursor, not conservative exclusion. Preserve that failed
ledger as evidence; repair the runtime, not this result. A first read-only inspection script
mistakenly requested a nonexistent supervision `classification` key; corrected inspection uses
the actual `status`/`exit_code`/`children_stopped` fields and makes no ledger/artifact changes.

All 15 corruption/budget cases are masked at their genuinely resolved fixture setup. Five
actual-original negative controls and before-COMMIT original-clean uncertainty pass, but blanket
committed-completion refusal masks the former's intended artifact checks. Changed-data and
committed-resolution uncertainty failures likewise do not establish verifier/COMMIT semantics.
No run remains active, controls/runner/runtime are unchanged since this red freeze, and no
writer/history or broader acceptance is claimed. Complete result wiki/privacy/fresh checks
precede the deliberate runtime repair successor.

### Immutable resolution runtime successor — unqualified

Acknowledged the complete **233-line** resolution-red result wiki/privacy successor and fresh
scoped/whitespace checks. Original runtime bytes are retained under
`/tmp/opencode/dcc-linux-entity-resolution-before-runtime-repair`; initial three-file successor
bytes remain under `/tmp/opencode/dcc-linux-entity-resolution-unformatted-runtime`. Complete
**343-line** two-file source delta and separate **450-line** resolution module reviewed.
Scoped formatting preserves ASTs except removal of one unused import; **eight-target** Ruff
lint/format pass. No test result for this successor exists yet.

The runtime adds immutable `entity_resolution_record` envelopes and separate `entity_resolved`
audits. `entity_resolution_unresolved` preserves acknowledgment uncertainty after an actual
resolution COMMIT, or after original-clean recovery's completion COMMIT, without overwriting
the original block/completion/publication. Each new resolution binds the latest authenticated
blocking audit and fresh actual-original-bound standalone observation; old evidence alone
does not release exclusion. Shared SQL budgets still precede typed owner/payload fetches;
resolution records have separate 128 KiB/10,000 caps inside the unchanged 64 MiB aggregate.
Only actual retained records add their small audit allowance. The closed unresolved allowance
`2 * MAX_ENTITY_RUNS + publications` is unchanged when no completion/resolution exists.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py; ../Wintap-PyUtil/wintappy/coordination/entity_intent.py -->

Blocked recovery now checks the retained blocking clock before any new verifier/artifacts.
Actual original intent/prelaunch/input/CLI/archive/retained-completion-verifier bytes are
rechecked before and after independent verification. Atomic acknowledgment disposition
requires the fresh same-session writer token and exact original completion core; it does
not insert authority, alter raw history/cursor or issue grants. After-COMMIT exceptions retain
evidence and restore `BLOCKED`; before-COMMIT refusals leave the original blocked state.
Ordinary reopen/history validates retained JSON only, never current data or reconstructed
historical observations. These are source-review findings, not executed qualification.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_writer.py; ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py -->

Distinct **303-identity** source freeze SHA-256
`a199ce1d25537e0e583abe0d39aaa426f444c89bab41a1b0dd57dbe4f4ce4292` changes only
`entity_intent.py`/`entity_writer.py` and adds `entity_resolution.py`; all other **300**
red-source identities remain unchanged. Frozen controls/runner/operators, original completion
records, public validators, v5 schema and standalone runtime are unchanged. Complete prepared
wiki/privacy/fresh checks precede the following **71-control** writer/history/resolution run;
retain every fixture/report/actual child diagnostic and inspect all evidence/identities before
repair or acceptance. The closed four-audit unresolved overflow still needs its affected rerun.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-resolution-runtime-first.txt \
  tests/test_coordination_entity_operations.py \
  tests/test_coordination_entity_writer_history.py \
  tests/test_coordination_entity_resolution.py
```

No run is active yet and no writer/history green or broader Linux acceptance follows.
Genuine completion-process-death, stronger SQL-budget/keyset-tail and raw-cursor/authority
forward-evolution controls remain separate, as do affected/full/service, S3/resources and
native-Mac shutdown. No remote/production/scheduling/utility/commit/push action.

The complete **470-line** prepared wiki/privacy successor is inspected; fresh scoped audit
passes nine Markdown/seven frontmatters, 258 grounding paths/415 inline sources, 443 links/
67 sections, and both whitespace checks pass. All **303** source/runner/operator identities
match immediately before launch. The distinct **71-control** runtime run is now active;
no result/green yet. Keep runtime/controls/runner fixed until notification and full retained
report/sidecar/actual child/all-identity review. Historical failures and all fixtures stay intact.

First immutable-resolution runtime run completes: **69 passed / two failed**, **516.86 s**,
exit 1. Complete **67-line** report SHA-256
`06805eeb8cd95f15d54d62ff67428a8e33692849fa63ad86b832a577d77e2e4e`, **50-line**
sidecar SHA-256 `79639e75a5d1b615a1ee1f45a47004a11a4fb586985d468295aeca305da9e896`
and all **seven actual diagnostics** reviewed: four intent/launch crash children exit 87,
three lock competitors exit 88, all with empty stderr. All **303** source identities,
frozen runner and operators match. Fixtures stay `/tmp/opencode/dcc-writer-diagnostics-an782wnj`.

All original **42 writer/history controls** and **27 new controls** pass, including early
block-clock refusal, now-unmasked corruption/budgets/artifact checks, changed-data fresh
verification and before/after resolution-COMMIT uncertainty. Both positive resolution controls
fail only on the newly added test's nonexistent `--entity-completion-only` flag after actual
successful disposition. The preserved standalone entrypoint uses direct
`raw_sensor_compact.entity_operation_verifier --request ... --request-sha256 ...`; the canonical
request's `operation: entity-only-completion` selects completion. Do not change this qualified
runtime contract to accommodate the mistaken test. All assertions **after** that flag check,
including immutable original/table/byte/reopen checks, remain unexecuted in those two cases.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/entity_verification.py §_command; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_operation_verifier.py §_request/main; ../Wintap-PyUtil/tests/test_coordination_entity_resolution.py -->

Read-only inspection of both failed fixture ledgers confirms one completion/resolution each,
the original publication when enabled, `DRAINING` with no owner and unchanged raw cursor.
Actual direct-module command manifest/canonical request/fresh completion-core/supervision/
stdout identities authenticate; no historical ledger or artifact is edited. This diagnostic
inspection does not substitute for rerunning the unexecuted positive assertions. Preserve
the complete failed run and original control bytes; review a distinct correction that asserts
the exact standalone module/command/request operation, retaining all other assertions and
parameterizations. No runtime repair is indicated by these failures. Complete result wiki/
privacy/fresh checks precede the control successor. No run remains active; the full **71-control**
gate, affected/full/service and wider Linux/S3/resources/native-Mac acceptance stay open.

### Resolution command-contract control successor — prepared

Acknowledged the complete **241-line** first-runtime result wiki/privacy review; fresh scoped
audit, both whitespace checks and all source/runner/operator identities pass. Original
**407-line** resolution controls are preserved as
`/tmp/opencode/dcc-linux-entity-resolution-original-controls.py`, SHA-256
`6949b02d8c82c38aebfde0011d75b24911d2265da6f07f82cc36a2be8ab5b24e`. Historical failed
reports, fixtures and freezes remain unchanged.

Only the nonexistent flag assertion is replaced: the positive controls now require the exact
standalone executable, isolated direct-module command, authenticated request path/hash,
canonical request bytes, `operation: entity-only-completion` and actual command manifest.
Complete **31-line** source delta reviewed. Exact text/AST restoration confirms every other
assertion, parameterization, helper and function remains unchanged. The corrected module is
**427 lines**; eight-target Ruff lint/format pass and all **71 controls** collect (0.65 s).
Collection does not qualify the previously unexecuted assertions.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_resolution.py; ../Wintap-PyUtil/wintappy/coordination/entity_verification.py §_command; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_operation_verifier.py §_request/main -->

Distinct **303-identity** control-only freeze
`/tmp/opencode/dcc-linux-entity-resolution-command-contract-source-freeze.json`, SHA-256
`25d1f17d9c611532647d100736d8ed1a17768829abe866745dd91ae96eae7056`, changes only this
control module. All **302** other sources, writer/history/publication controls, runtime,
public validators, v5 schema, standalone runtime, runner and operators remain unchanged.
Complete prepared wiki/privacy review and fresh checks precede the distinct rerun below;
full report/sidecar/actual-child/all-identity review precedes acceptance or further changes.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-resolution-command-contract.txt \
  tests/test_coordination_entity_operations.py \
  tests/test_coordination_entity_writer_history.py \
  tests/test_coordination_entity_resolution.py
```

No run active or 71-control green yet. Closed publication qualification, including exact
unresolved four-audit overflow and actual original publication COMMIT process death, still
needs a separately retained affected rerun. Completion-process-death/SQL-tail/forward-evolution,
affected/full/service, S3/resources and native-Mac remain separate open gates. No remote,
production, scheduling, utility implementation, commit or push action.

Complete **248-line** prepared-final wiki/privacy successor inspected; fresh scoped audit
passes nine Markdown/seven frontmatters, 258 grounding paths/421 inline sources, 444 links/
68 sections, with both whitespace checks and all source/runner/operator identities passing.
The distinct frozen **71-control** command-contract rerun is now active, not green. Keep
runtime/controls/runner fixed until notification and complete retained evidence/identity review.

While that run is active, both unchanged publication-control modules were reviewed in full.
Six-target Ruff lint/format pass; isolated `pytest --collect-only -q -p no:cacheprovider`
collects **123 controls** (0.71 s), retained in
`/tmp/opencode/dcc-linux-entity-publication-post-resolution-collection.txt`. This includes all
46 original plus 77 expanded controls, the exact five-entry unresolved four-audit overflow
and both actual original publication COMMIT process-death cases. No publication test has
launched; its distinct retained affected rerun follows the all-71 evidence/identity review.

Command-contract rerun completes: **71 passed**, **521.59 s**, exit 0. Complete **three-line**
report SHA-256 `2a71e4b75b8e88b80670d5c256bcefe10fa67b8d224df9a72d37f919766501fb`,
**50-line** sidecar SHA-256 `4715e7e2d99d44d32e58aa84942465155d754a9868be6b5c3838b2238108e3f1`
and all **seven actual diagnostics** reviewed. Four genuine intent/launch crash children exit
87; three competing-lock children exit 88; all stderr is empty. All **303** source identities,
frozen runner and operator documents authenticate unchanged. Fixtures remain
`/tmp/opencode/dcc-writer-diagnostics-cbkhymrd`; original 407-line controls and the failed
69/two report remain byte-identical.

Both corrected positive cases now execute their later immutable original/completion/authority/
table/data/artifact/retry-refusal/reopen assertions and pass. All 42 original writer/history
and 29 resolution controls pass on the frozen runtime. This closes the **initial writer/history/
resolution focused gate**, not the closed-publication affected rerun or expanded completion-
process-death/SQL-tail/forward-evolution qualification, affected/full/service, S3/resources or
native-Mac gates. No test remains active. Complete result wiki/privacy review and fresh checks
precede the separately frozen **123-control publication affected rerun**; no source/control/
runner changes are indicated by this green. No remote/production/scheduling/utility/commit/push.

### Publication affected rerun after resolution — prepared

Complete **266-line** all-71 result wiki/privacy successor and **57-line** index historical/
current reconciliation are acknowledged; fresh scoped audit and both whitespace checks pass.
Both unchanged publication modules have full review and **123-control** collection; renewed
six-target Ruff lint/format pass. The affected scope includes all 46 original/77 expanded
controls, the exact `MAX_ENTITY_RUNS = 1` four-audit overflow at all five typed entries, SQL
UTF-8 budgets before identifier/payload fetches, original publication keyset tails, corruption,
historical-core binding and two actual original before/after publication COMMIT deaths.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_publications.py; ../Wintap-PyUtil/tests/test_coordination_entity_publication_qualification.py -->

Distinct `/tmp/opencode/dcc-linux-entity-publication-post-resolution-source-freeze.json`
retains all **303** identities, byte-identical to the all-71 green freeze, SHA-256
`25d1f17d9c611532647d100736d8ed1a17768829abe866745dd91ae96eae7056`. The unchanged
diagnostic-retaining runner is separately frozen; operators are unchanged. No runtime,
controls, public contracts or locks changed. Complete prepared wiki/privacy/fresh checks
precede the distinct retained rerun; full report/sidecar/actual-child/all-identity review
precedes acceptance or further changes.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-publication-post-resolution.txt \
  tests/test_coordination_entity_publications.py \
  tests/test_coordination_entity_publication_qualification.py
```

No test active or affected result yet. This rerun is not the broader entity affected/full
gate. Expanded completion-death/SQL-tail/forward-evolution, pending-publication repair/retry,
original migration/deletion and strict service dispatch remain open, as do both runtimes'
integration gates, isolated S3/resources and native-Mac shutdown. No remote/production/
scheduling/utility/commit/push action.

Complete **233-line** prepared wiki/privacy successor inspected; fresh scoped audit passes
nine Markdown/seven frontmatters, 258 grounding paths/423 inline sources, 445 links/69 sections.
Both whitespace checks and all **303** source/runner/operator identities pass. The separately
frozen **123-control publication affected rerun is active**, with no result yet. Keep runtime,
controls and runner unchanged until notification and complete retained evidence/identity review.

Publication affected rerun completes: **123 passed**, **708.64 s**, exit 0. Complete **four-line**
report SHA-256 `98cd4ec5b7b9737d2b8cf40220a0c9ee4dad84c7008dc7353f711017262559da`,
**29-line** sidecar SHA-256 `5fd0a9168c804a62f4da492b145e529d8b19066580d2ff11b2d764e788f55f4c`
and both actual **93-byte** publication crash diagnostics reviewed; both children exit 87
with empty stderr at the original before/after publication COMMIT boundaries. All **303**
source identities, both runner baselines and operator documents authenticate unchanged.
Every fixture remains in `/tmp/opencode/dcc-writer-diagnostics-83cxsk07`; historical reports,
original controls and prior fixtures are preserved. No test remains active.

This closes only the **post-resolution publication affected follow-through**, including all
46 original/77 expanded controls and exact unresolved four-audit overflow at all five typed
entries. It does not close entity-wide affected/full, genuine completion-process-death,
stronger completion/resolution SQL-budget/keyset-tail, raw-cursor/authority-forward-evolution,
pending-publication repair/retry, original migration/deletion or strict service integration.
Complete result wiki/privacy review and fresh checks precede separately reviewed/frozen new
controls; runtime and all existing controls remain unchanged. S3/resources/native-Mac and
dcc-02–05 acceptance stay separate/open. No remote/production/scheduling/utility/commit/push.

### Genuine typed completion-process-death controls — prepared

Complete **254-line** publication-result wiki/privacy successor is reviewed; fresh scoped
audit, both whitespace checks and all source/runner/operator identities pass. The separate
new **345-line / 12-control** module tests actual `os._exit(89)` without Python unwinding
after genuine standalone verification and at the original before/after typed COMMIT hooks.
Four paths are covered: entity initialization, replay, original-clean recovery with retained
publication, and immutable completion acknowledgment resolution with retained publication.
Unformatted bytes are retained; formatting is text-matched to the reviewed formatter output
and AST-identical. The child script parses; six-target Ruff lint/format and isolated 12-control
collection pass (0.76 s). Collection is not execution or process-death qualification.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_crashes.py -->

The child binds its actual canonical boundary capture by hash in retained stdout. Controls
authenticate the precise request-based standalone command, actual request/capture/manifest/
shutdown, original CLI/archive evidence and typed completion/resolution/authority all-or-none
state. Raw cursor/history, publications, existing audits, data, waiting readers and outbox
remain separate. A verified but uncommitted original remains `BLOCKED` on reopen and requires
a newly supervised original-bound current-only verifier plus explicit audited recovery.
An authenticated actual COMMIT retains the atomic typed result in `DRAINING`; it grants no
reader, raw completion or live-session authority token. Existing caught acknowledgment-loss
controls still require `BLOCKED` and remain unchanged. A scoped synthetic January reopen clock
avoids mixing fixture and wall clocks; it is not production rollback authorization. Later
reopen must validate retained history without runtime/artifact/data reads or verifier launch.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_crashes.py; ../Wintap-PyUtil/tests/test_coordination_entity_writer_history.py; ../Wintap-PyUtil/tests/test_coordination_entity_resolution.py; ../Wintap-PyUtil/tests/test_coordination_completion.py §test_abrupt_completion_death_recovers_all_or_none_and_cannot_relaunch -->

Distinct `/tmp/opencode/dcc-linux-entity-completion-crashes-source-freeze.json` contains
**304 identities**, SHA-256
`17979a977cc41c7bdb3bbe10dd7a84ad246945dc80498e6f2a203665a511a580`; only the new control
module is added, preserving all **303** publication-green source identities. Runtime, existing
controls, public validators, v5 schema, standalone runtime, locks, operators and separately
frozen diagnostic-retaining runner are unchanged. Complete prepared wiki/privacy/fresh checks
precede the isolated first run; notification and complete report/sidecar/actual-child/boundary-
capture/all-identity review precede acceptance or further source/control changes.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-completion-crashes-first.txt \
  tests/test_coordination_entity_completion_crashes.py
```

No run active or executed result yet. Stronger completion/resolution SQL budgets/keyset tails,
raw-cursor/authority forward evolution, maintenance/service and both runtimes' staged wider
integration gates remain open. No remote/production/scheduling/utility/commit/push action;
S3/resources/native-Mac and dcc-02–05 acceptance stay separate.

Complete **316-line** prepared wiki/privacy successor is inspected; fresh scoped audit,
both whitespace checks and all **304** source/runner/operator identities pass. The distinct
frozen **12-control completion-process-death run is active**, with no result yet. Preserve
runtime, controls and runner until notification and complete retained report/sidecar/actual-
child/boundary-capture/all-identity review; do not infer acceptance from collection or launch.

Result reviewed: **12 passed**, **283.57 s**, exit 0. Complete **three-line** report SHA-256
`31b1528deaba02bedc83960a0e22be35fb4570ec337f4d71a42da6245e9ffab8` and **68-line** sidecar
SHA-256 `bd82a1f34fb33d4a38f941aa7a2be909538812b9ef9d96ca2c7169bdabf1a8d1` authenticate.
All **12 actual 181-byte exit-89 diagnostics**, with empty stderr, bind their canonical
boundary captures by the hashes emitted in actual child stdout. Complete actual evidence
inspection authenticates **48 observation-artifact groups** (boundary, original input,
post-COMMIT prelaunch and retained completion/resolution) and **72 immutable CLI archive
records**, including exact request-based standalone dispatch, manifests, saved captures,
shutdown and original CLI statistics. No verifier is launched by the inspection and no
historical checkpoint hash is compared with today's aggregate.

Read-only inspection of every retained ledger authenticates original intent and typed
completion/resolution/authority linkage. The eight verified/pre-COMMIT deaths have distinct
fresh recovery observations; the four after-COMMIT deaths retain their actual boundary
observations. All finish the controls in `DRAINING`, with original raw cursor, no raw
completion/run, no reader/grant and no live-session authority. The controls execute their
original-byte/data preservation, blocked restart, atomic all-or-none, fresh audited recovery
and artifact-free reopen assertions. All **545 retained fixture files** are byte-identical
before/after the independent read-only inspection. An initial diagnostic-only guessed
midnight-cursor assertion was corrected to the original intent's `raw_next_hour`; no runtime,
control or fixture changed, and the complete corrected inspection passes.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_crashes.py -->

All **304** frozen source identities, both runner baselines and operator documents authenticate
unchanged; all **303** publication-green predecessor identities are preserved. Every fixture
remains in `/tmp/opencode/dcc-writer-diagnostics-9r9tccto`; all historical reports, original
controls and freezes remain intact. **No test remains active.** This closes only genuine typed
completion-process-death focused qualification, not stronger completion/resolution SQL-budget-
before-fetch/keyset-tail, raw-cursor/authority forward evolution, pending-publication repair/
retry, original migration/deletion, strict entity service dispatch or staged wider integration.
Complete result wiki/privacy review and fresh checks precede separate reviewed/frozen controls;
runtime and existing controls remain fixed. S3/resources/native-Mac and dcc-02–05 stay open;
no remote/production/scheduling/utility/commit/push action.

### Completion/resolution SQL-budget and keyset-tail qualification — prepared

The complete **307-line** crash-result wiki/privacy review and fresh scoped/whitespace/
source/runner/operator checks precede this control-only successor. Initial **531-line**
formatter output exactly matches the applied source and is AST-identical to retained
**329-line** unformatted bytes. Full source review finds fixture/guard defects before
execution: the shared preparation helper has no `now` keyword; the writer retains its
actual execution-receipt prerequisite; unrelated reader validation uses an independent
cursor; and rollback must remain possible even after a page-materialization guard failure.
The complete **98-line** correction changes only those new-module fixture/guard seams;
all test assertions/parameterizations and other helpers remain unchanged by AST checks.
Draft and intermediate corrected bytes remain retained; no runtime repair is indicated.

The reviewed final **548-line / 44-control** module plans two genuinely executed entity
operations (initialization/replay), two lost-COMMIT-acknowledgment completions, two fresh
audited resolutions and two immutable original publications. Thirty controls exercise
completion/resolution UTF-8 record/count, small-audit and combined aggregate budgets at
validation, owner, evidence, writer and resolution entries before typed identifiers/
JSON/audits are fetched. Three positives use exact measured boundaries without pruning.
Eight controls reduce real sequence SQL from `LIMIT 256` to `LIMIT 1`, covering both
genuine tails plus null/hole/predecessor damage. Three full-history controls require
materialization of owner/publication/completion/global-and-owner-resolution/audit pages,
including unsupported/orphan tail audits. Original SQL results are never replaced; typed
independent cursors are rejected while unrelated reader-only cursors still execute real
SQL. Corruption is rollback-only, including after guard failure. Writer entry permits
only its actual receipt prerequisite; history cannot fetch old data/artifacts or launch
a verifier. All controls compare ledger/data/original artifacts after rollback/refusal.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py; ../Wintap-PyUtil/tests/test_coordination_entity_operations.py §prepare_entity; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py §execute_entity_and_complete_prepared; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate_reader_recoveries -->

Eight-target Ruff lint/format passes; isolated final collection finds **44 controls**
(0.65 s), exit 0. Collection is not executed history qualification. Final control SHA-256:
`08d35b2257bf2b653cfb52517a2f7953082da461e83892b616d9c6f38ee2045c`.
Distinct `/tmp/opencode/dcc-linux-entity-completion-history-source-freeze.json` binds
**305 identities**, SHA-256
`61e86e4eca5ff87edf0ed25b352539d598d76b445b6f8dcc000924e25b0be6e9`; only this new module
is added, with all **304** crash-green predecessor sources, public contracts, v5 schema,
standalone runtime/locks, operators and separately frozen runner unchanged.

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-completion-history-first.txt \
  tests/test_coordination_entity_completion_history_qualification.py
```

**Preparation-time record; no executed result then.** Complete prepared wiki/privacy/fresh
checks precede launch; notification and full retained report/sidecar/actual fixture/artifact/
identity review precede acceptance or further changes. Runtime, existing controls and runner
stay fixed; every original/historical report and fixture remains intact. Raw-cursor/authority
forward evolution, maintenance/service, staged integration and wider Linux/S3/resources/
native-Mac/dcc-02–05 acceptance stay open. No remote/production/scheduling/utility/commit/push.

Complete **480-line** prepared wiki/privacy successor was reviewed; fresh scoped audit,
both whitespace checks and all **305** source/runner/operator identities passed before
the distinct frozen **44-control history-qualification run** launched. The complete
**207-line** launch-status wiki/privacy successor and fresh checks also passed.

#### Executed history result — focused gate closed

The frozen run passes **44 controls in 62.53 s**, exit **0**. Complete **three-line** report
and **19-line** sidecar authenticate; `child_diagnostics` is empty, not missing crash evidence:
this fixture uses genuine ordinary CLI/verifier captures, not exit-89 diagnostic children.
Report SHA-256: `2a9fe3b430d5bc01967e141745781a17c9ceeed766744d7604a8ece22bd24b26`.
Sidecar SHA-256: `ac761f679238fe6cee90b4aaa4b11d946ecb24378d1285c45705c996695edf3e`.

Independent read-only inspection authenticates **ten actual verifier artifact groups**, **two
actual CLI completions** and **twelve immutable archive records**. Original intent/execution/
prelaunch/request/manifest/capture/shutdown bytes, publication/completion/resolution predecessor
chains, original authority/raw-cursor links and retained blocker audits all match. The actual
v5 ledger retains two completed owners and two publications/completions/resolutions/blockers;
its **14** non-origin entity events comprise seven kinds occurring twice. Raw/retry/reader
tables and maintenance event history remain empty. State is `DRAINING` at the original raw
cursor with no active owner/readers or live authority token; authority generation is two.
No verifier is launched, data SQL issued, historical observation reconstructed or historical
checkpoint hash compared with today's aggregate during inspection.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py §TABLES_V5; ../Wintap-PyUtil/wintappy/coordination/maintenance.py §history -->

Two inspection-only mistakes remain preserved: the original guessed `maintenance_operations`
table query failed before final checks; its transcript is explicitly labeled as transcribed,
not a new execution capture. The table-corrected inspection then failed on a guessed **12**-
event total. Actual read-only SQL establishes **14**; only inspection SQL/count assertions
were corrected. Both diagnostics and the failed inspection source remain retained. The full
corrected inspection passes, exit **0**, with its complete **nine-line** capture reviewed:
`/tmp/opencode/dcc-linux-entity-completion-history-inspection-final.txt`, SHA-256
`3880f8e648d3ae862d812419da5fd952d44cf776ac4fda1912571d7bb917e5e3`.
All **84 retained files** (**83 pytest fixture files plus sidecar**) and one symlink are
unchanged before/after the corrected review and also match the failed-inspection pre-read
snapshot. Snapshot SHA-256: `c7355f6018c6b0216b2b6afc29b988c2cdc2588b1ed7095e048320f77abe50d1`.
All **305** frozen source identities, **304** predecessors, both runner baselines and operator
documents authenticate unchanged. Runtime, tests and fixture bytes were not changed.

**No test remains active. Only this SQL-budget/keyset-tail focused gate closes.** Raw-cursor/
authority forward evolution, pending-publication repair/retry, original migration/deletion,
strict entity service dispatch, staged focused/affected/full integration and broader Linux
acceptance remain open. Complete result wiki/privacy/fresh checks precede a separate reviewed/
frozen successor; all historical failures/artifacts remain intact. S3/resources/native-Mac and
dcc-02–05 remain separate; no remote/production/scheduling/utility/commit/push action.

#### Raw-cursor/authority forward-history successor — prepared

Complete **343-line** closed-history result wiki/privacy review and fresh scoped/
whitespace/source/runner/operator/fixture checks precede this separate control-only successor.
The unexecuted **261-line** draft is retained before correction. Live helper/API/clock/
anchor/raw-completion/scope review finds two draft defects: a future-dated waiting request
was ingested before earlier work, and host semantics were queried from the three-field
authority anchor. The complete **67-line** correction makes the request chronological,
uses the actual generation identity and compares original CLI host semantics with the
genuinely captured final raw CLI report. No historical checkpoint is compared with the
current aggregate. Formatting preserves the complete corrected AST; nested refusal contexts
are combined only for lint. Runtime, shared helpers and all predecessor controls are unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_forward_history.py; ../Wintap-PyUtil/wintappy/coordination/authority.py §validate_anchor; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §_run -->

The fully reviewed **419-line** module collects **23 controls**: three genuine forward-history
positives, sixteen rollback-only original-scope/history damage cases and four old execute/
resolve refusals. Fixture setup plans genuine initialization/publication/acknowledgment
resolution, hour-23 raw completion, replay/publication/acknowledgment resolution, then a
standalone-generated next-hour STOP input and genuine hour-00 raw completion. It retains
original owners/completions/publications/resolutions/raw proof and artifact hashes before
evolution; expected final authority generation is four and raw cursor is the next fixed-hour
boundary. Controls prohibit historical artifact/data/verifier reads; terminal writer entries
retain their actual receipt prerequisite. Missing/substituted/late authority and raw
predecessors, null raw identity and cursor rollback must refuse without reopening/mutation.
All injected SQL is rolled back, including unexpected assertion failure.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_forward_history.py; ../Wintap-PyUtil/tests/test_coordination_entity_completion_history_qualification.py §no_original_reads; ../Wintap-PyUtil/tests/test_coordination_entity_writer_history.py §staged; ../Wintap-PyUtil/wintappy/coordination/entity_history.py §validate_original_scope/raw_cursor_identity -->

Eight-target Ruff lint/format pass; the complete embedded standalone input script parses.
An initial collection-only launcher mistakenly resolved the venv interpreter symlink to
system Python and failed before importing pytest. Its capture is retained; corrected
collection uses the venv path unchanged and collects all **23** (0.73 s), exit **0**.
No semantic test executed during either collection attempt. Distinct source freeze:
`/tmp/opencode/dcc-linux-entity-forward-history-source-freeze.json`, **306 identities**,
SHA-256 `b7a2082fd02a13ad0fcf3f72e99cf22ca56a087a3e1cb539254aada6327e07be`.
Module SHA-256: `aa926d6249a516344259d638b8e78de3fdcc955d33b63fdb338144d96b0c5bc2`.
Only this module is added; all **305** closed-history predecessors, retained fixture files,
both prior runner baselines and operator documents remain unchanged. Separate runner freeze
binds the unchanged overwrite-refusing diagnostic-retaining runner.

Prepared first qualification command, from PyUtil:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-forward-history-first.txt \
  tests/test_coordination_entity_forward_history.py
```

**Preparation-time record; no semantic result then.** Complete prepared wiki/privacy/fresh
checks preceded execution. Full retained report/sidecar, genuine raw/entity verifier/CLI/
archive/original/ledger and before/after fixture/source/runner/operator inspection precede
any result closure or runtime repair. Every historical failure remains intact. Original-bound
maintenance/service and staged integration/wider Linux/S3/resources/native-Mac/dcc-02–05
stay open; no remote/production/scheduling/utility/commit/push action.

Complete **340-line** prepared wiki/privacy successor was reviewed; fresh scoped audit,
both whitespace checks and all **306** source/three runner-baseline/operator/closed-history
fixture checks passed before the distinct frozen **23-control forward-history first run**
launched. Complete **210-line** launch-status wiki/privacy review and fresh checks also passed.

#### Executed forward-history result — focused gate closed

The frozen run passes **23 controls in 87.45 s**, exit **0**. Complete **three-line** report
and **19-line** sidecar authenticate; expected `child_diagnostics` is empty because these
controls retain ordinary genuine CLI/verifier captures rather than crash diagnostic children.
Report SHA-256: `ae479845dec5733f5b08418926343f83bf72750e3fa4f816c72eec751b678e21`.
Sidecar SHA-256: `7cc6e290f500c74b860abbfc1e074644c9bde170f38378d4db291aa15bcd1a30`.

Independent read-only inspection authenticates **16 actual verifier artifact groups**, **four
actual CLI completions** and **34 immutable archive records**. Each typed original binds five
independent input/prelaunch/publication/completion/resolution groups and six archive records;
each actual raw completion binds an independent completion verifier, its fresh authority check
and eleven archive records. Two additional public authority checks supply the remaining groups.
Canonical original execution/intent/prelaunch/request/command/capture/shutdown bytes, immutable
publication/completion/resolution chains, original authority/raw-cursor predecessors and exact
blocking-audit links match the saved original-generation capture after forward evolution.
The next-input standalone child exits **0** with empty stdout/stderr. Its actual final raw CLI
host semantics differ from both historical typed CLI captures while bootstrap provenance remains
the original hour. No historical checkpoint hash is compared with today's aggregate.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_forward_history.py; ../Wintap-PyUtil/wintappy/coordination/entity_history.py §validate_original_scope/raw_cursor_identity; ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py §_block -->

The actual v5 ledger retains two completed typed owners/publications/completions/resolutions/
blockers, two completed raw owners, six authority rows with generations **1,1,2,3,3,4**, and
**14** non-origin typed events (seven kinds occurring twice). Three raw execution receipts exist,
but the unchanged seed preparation is not a third launched raw owner. The final state is **`OPEN`
at `2026-01-02T01:00:00Z`**, not `DRAINING`: the authenticated final raw completion commits
`OPEN` because the next hour is not yet due at its original completion observation. Typed
completion alone still uses `DRAINING` and never advances the raw cursor. The one queued reader
remains `WAITING`; no grants, active owner, maintenance/retry history or live authority token
exist on read-only reopen. `OPEN` without fresh same-session authority does not admit that reader.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py §validate_completion_proof/_build_completion_proof; ../Wintap-PyUtil/wintappy/coordination/coordinator.py §writer_due; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_complete_writer/_require_entity_authority/snapshot; ../Wintap-PyUtil/wintappy/coordination/entity_history.py §complete_observation; ../Wintap-PyUtil/tests/test_coordination_entity_forward_history.py -->

The first **14-line** inspection capture and original **303-line** inspection source are retained:
the inspection guessed final `DRAINING` and failed after authenticating both typed and raw
original chains, before final boundary/identity checks. Separate **five-line** read-only SQL
diagnostics establish the actual `OPEN` snapshot and unchanged fixture bytes. The complete
**21-line** diagnostic-only correction binds `OPEN` to the actual final raw proof; it changes
no runtime, controls, ledger or fixture. The corrected **304-line** inspection passes, exit **0**;
its complete **12-line** capture is reviewed:
`/tmp/opencode/dcc-linux-entity-forward-history-inspection-final.txt`, SHA-256
`e37554d0688409c88f011de12cf9cdc4387f9f5e723fab729f92394b49fab1bf`.
All **150 retained files** (**149 pytest fixture files plus sidecar**) and one symlink remain
unchanged before/after both inspections and the separate diagnostic. Pre-read snapshot SHA-256:
`987b075edf3310ea9c3ca63d0e302aabc7eb8cfc53b335080c762f4d39e8c3c6`.
All **306** sources, **305** predecessors, three runner baselines, operator documents and closed-
history fixture bytes authenticate unchanged. No verifier launch, data SQL or reconstruction
was used by inspection; every historical failure and evidence artifact remains retained.

Executed corrected inspection command, from PyUtil (exit **0**):

```sh
PYTHONPATH="$PWD" .venv/bin/python -B \
  /tmp/opencode/dcc-linux-entity-forward-history-inspect-readonly.py \
  /tmp/opencode/dcc-linux-entity-forward-history-inspection-final.txt
```

**No test remains active. Only this raw-cursor/authority forward-history focused gate closes.**
Complete result wiki/privacy/fresh checks precede a separate reviewed/frozen original-bound
recovery/maintenance/service successor. Pending-publication repair/retry, original migration/
deletion recovery coverage, strict Linux entity dispatch, both runtimes' staged focused/affected/
full integration and broader Linux acceptance remain open. Isolated S3/access, representative/
reduced-budget resources, physical power loss, coherent whole-ledger-plus-authority rollback
freshness and native-Mac shutdown remain separate and unqualified. No remote/production/
scheduling/utility/automatic-expiry/commit/push action.

### Strict Linux entity service successor — controls prepared

The closed forward-history runtime/controls/evidence remain unchanged. The selected next
slice exposes only existing qualified library paths: `entities-init`, `entities-replay`,
`resolve-entity` (clean originals or immutable acknowledgment resolution), and explicit
`upgrade --target-version 5`. Default initialization/upgrade remains v4. The optional,
separately allowlisted `entity_writer` configuration preserves raw ticks' one-hour budget;
entity windows require exact `--start-hour`/`--end-hour` and retain the existing 24-hour
default/168-hour cap. New flags cannot leak into unrelated operations. Confirmation,
reason, platform and unrelated-flag checks precede configuration/credential resolution.

Recovery loads only the typed owner's authenticated original receipt; current configuration
cannot redefine its window, command, budgets, roots or non-secret storage scope. Every
operation holds the existing ledger lock, uses the existing supervised/fresh-verifier paths,
and neither requests transport/grants nor advances raw history. No library validator,
standalone verifier, v5 schema or public one-hour contract is weakened. Pending-publication
repair/retry, missing original migrations and deletion recovery coverage stay separate.
<!-- SPECULATIVE: selected bounded service integration; runtime unchanged and no new execution result at preparation -->

Separate `tests/test_coordination_entity_service.py` adds configuration/early-refusal,
genuine init/replay, exact-original recovery, receipt-damage and actual service-process-death
controls. Review corrected draft-only nonexistent metadata/CLI fields and the context-manager
hook before execution; these are not runtime defects or qualified boundaries. Freeze/review
the controls and inspect the complete retained red before source changes. Wider entity
focused/affected/full, Linux, S3/resources and native-Mac gates remain open. No remote,
production, scheduling, utility, automatic-expiry, commit or push action.

The complete 447-line control module and embedded child were reviewed; scoped Ruff lint
and 71-control collection pass. Separate 307-identity first-red freeze adds only this
module, preserving all 306 closed-forward identities. Freeze SHA-256:
`8854c01cb6cd072fd52d752ac07c6ab84195e7ab330b896cdf4968051195f75f`.
The unchanged diagnostic-retaining runner remains independently hash-bound. First red:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-service-first-red.txt \
  tests/test_coordination_entity_service.py
```

No new runtime implementation/result at preparation. All fixtures and complete report/
sidecar/actual child diagnostics must remain retained and reviewed before repair.

### First frozen service red — launch-time record

The prepared first-red command was launched with the unchanged overwrite-refusing,
diagnostic-retaining runner. No completion notification/result has yet been received or
inspected. Preserve all runtime/control/runner bytes until the complete retained report,
sidecar, actual child diagnostics and all 307 frozen identities have been reviewed; do not
rerun or overwrite this evidence and do not infer a qualified crash boundary from preparation.

Resumed read-only checks confirm all 307 identities and the same freeze hash. The complete
297-line corrected preparation delta was re-read for scope/privacy, retaining the separate
384-line omitted-untracked-page snapshot diagnostic without modifying it. Fresh scoped wiki
audit passes nine Markdown files/seven frontmatters with no new link/section exception;
index/log frontmatter omissions remain baseline. Both repositories' `git diff --check` pass.
These checks are not service execution results or broader entity/Linux acceptance.

### First frozen service red — complete missing-seam result

Completion notification received: **71 failures in 135.78 s**, exit 1. Complete retained
3,052-line report was reviewed through a 607-line unique-line catalog with source-line
positions and an independently checked exact-byte reconstruction. Complete 28-line sidecar
and both actual 719-byte diagnostics authenticate against their retained hashes. All 307
source identities and the unchanged runner match the first-red freeze. A separate read-only
snapshot retains 302 regular files/eight symlinks, including deliberately damaged originals;
missing receipts were not reconstructed and existing hard links were not repaired.

- One positive fails because optional `entity_writer` configuration is not supported.
- Sixty-four controls stop at missing entity choices/new flags: parser code 2 is not a
  successful code-1 semantic refusal; later exclusion/original assertions remain unexecuted.
- Four receipt-damage controls reach the absent `load_original_entity_execution` API.
- Both actual service children exit 2 with empty stdout and the retained parser diagnostic.
  Neither requested before/after-completion-COMMIT boundary was reached; no exit-91 evidence.

Report SHA-256: `1cde42845366cea98479852522dc47823bab2833b31eb033d50f3da661553597`.
Sidecar SHA-256: `01d574daa94c8ef76b9554fe69cf9fed9262ca0fe9f704f26bbf42ed2ea26313`.
Retained fixture root: `/tmp/opencode/dcc-writer-diagnostics-_qhzfkt0`.
No run remains active. Next implement only demonstrated service configuration/strict
dispatch/explicit-v5/original-loader seams, then freeze/review a distinct runtime successor
and rerun unchanged controls. Existing library/standalone/public/schema contracts and all
prior evidence stay fixed. Pending-publication repair, staged integration and wider Linux/
S3/resources/native-Mac/dcc-02–05 remain open; no broader acceptance or remote/production/
scheduling/utility/expiry/commit/push action.

### Strict Linux entity service runtime successor — unqualified

After complete 306-line red-result wiki/privacy review and fresh scoped/whitespace checks,
the two original runtime files were retained separately. Only `service.py` and `recovery.py`
change. Complete formatted 303-line delta was reviewed; fresh three-target Ruff lint/format
and unchanged 71-control collection pass. All other 305 source/control/runtime-lock identities
and the separate retained runner stay unchanged. All 310 first-red fixture entries, including
deliberate damage and eight symlinks, recheck unchanged.

The optional `entity_writer` is allowlisted and validated with existing typed budgets before
runtime/credential resolution; raw `writer` remains exactly one hour. New flags are scoped
before configuration, and entity operations require Linux, confirmation/reason and exact
start/end hours or original run identity. Explicit upgrade selection accepts only 4/5 and
leaves default v4 and existing JSON `null` output unchanged. Launch requires v5 and unowned
zero-reader exclusion before receipt preparation, then uses the existing supervised library
under the same ledger lock. Resolution loads the exact blocked typed owner's authenticated
actual receipt/intent, rechecks original path/scope/runtime before credentials, refuses a
changed resolved storage scope, and calls the existing fresh read-only resolution library.
No new invocation is prepared for recovery, no transport/grant is requested and no public
validator, typed schema, standalone verifier or raw cursor contract changes.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/service.py §validate_config/main; ../Wintap-PyUtil/wintappy/coordination/recovery.py §load_original_entity_execution -->

Distinct runtime freeze: `/tmp/opencode/dcc-linux-entity-service-runtime-first-source-freeze.json`,
307 identities, SHA-256 `6312461e08a7e0a32e7dfb75d0686d20b06313dc036bc842999879e1a3a64618`.
Source delta SHA-256: `b047b0ad29774cff15126a8e3f627e37494f2887f30e23afc683fc25cbdae7f6`.
Prepared unchanged-control rerun:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-entity-writer-keep-diagnostics.py main \
  /tmp/opencode/dcc-linux-entity-service-runtime-first.txt \
  tests/test_coordination_entity_service.py
```

No semantic result yet. Complete prepared wiki/privacy/fresh checks precede launch; full
report/sidecar/actual CLI/verifier/archive/ledger/crash/exclusion and identity inspection
precedes closure or repair. Preserve all historical reports/fixtures. Pending-publication
repair, broader focused/affected/full integration, S3/resources/native-Mac and dcc-02–05
remain separate; no remote/production/scheduling/utility/expiry/commit/push action.

Complete **319-line** prepared runtime wiki/privacy successor was reviewed. Fresh scoped
audit, both whitespace checks, all 307 runtime identities and unchanged runner pass; the
accepted forward fixture's 150 files/one symlink also recheck unchanged without a rerun.
At launch, the distinct unchanged 71-control runtime qualification command above was running
in the background, without a completion result. Runtime/controls/runner stayed fixed
until complete retained report/sidecar/actual diagnostic/artifact and identity inspection.
No focused service gate or broader acceptance is closed by launch.

### Executed strict entity service result — focused gate closed

Completion notification received: **71 passed in 251.19 s**, exit 0. Full three-line report,
28-line sidecar and both actual 62-byte child diagnostics authenticate. Both children exit
91 with empty stderr and literal `null` run IDs; actual original receipts, not those diagnostic
values, bind the requested before/after-COMMIT runs. A before-inspection snapshot preserves
439 regular files/eight symlinks; the complete final 18-line read-only review authenticates
all 23 ledgers without `Ledger.open`, data SQL, verifier/entity relaunch or credential resolution.

- Ten genuine original executions retain actual typed intents, original/post-COMMIT input
  observations, canonical requests/manifests, hash-bound stdout/stderr and clean shutdown.
  **32 verifier groups** comprise 20 input, 11 completion and one existing public-authority
  observation; **ten clean entity CLI captures / 60 immutable archives** preserve exact hours,
  original identities, input fingerprints, bootstrap provenance and archived checkpoints.
- Nine typed completion records authenticate with their exact atomic authority references;
  one separately hash-linked acknowledgment disposition preserves its original completion,
  authority and blocker. Original-clean recovery uses fresh independent verification; current
  changed raw-writer budgets are not substituted for the original entity receipt.
- Before-COMMIT death leaves the original `BLOCKED` owner and no completion/authority. Its
  actual later restart block clock is preserved, not moved back to the synthetic fixture clock.
  After-COMMIT death retains completed ownership plus both atomic records, stays `DRAINING`
  without raw advancement, and cannot launch genesis again. Its retry leaves one prepared-only
  receipt with **no intent, verifier, launch or archive**; preparation grants no permission.
- Four actual receipt-damage/original-ID controls retain blocked completed originals; the
  missing receipt is not reconstructed, changed bytes are not repaired and the hard link stays
  inadmissible. Thirteen owner-free configuration/refusal/upgrade fixtures have no typed launch;
  default v4 remains v4 and explicit compatible v5 staging is separately authenticated.
- Raw cursor/history, queued `WAITING` readers, no grants/outbox/retries and no live authority
  acknowledgments remain intact. Runtime/control/runner bytes are unchanged; this is not a new
  data-repair operation, historical-publication fallback or wider integration acceptance.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_entity_service.py; ../Wintap-PyUtil/wintappy/coordination/entity_history.py §validate_completion_record; ../Wintap-PyUtil/wintappy/coordination/entity_resolution.py §validate_owner; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_operation_verifier.py §verify_entity_completion -->

The initial inspector incorrectly assumed exactly one execution directory and stopped on the
prepared-only post-COMMIT retry receipt. Its report/source remain retained. The separate
50-line diagnostic-only correction authenticates that orphan without promoting it to intent.
The second inspector incorrectly expected service configuration for direct-loader controls;
its report/source also remain retained. A separate reviewed 24-line correction reads actual
canonical ledger metadata, leaving absent config/original files absent. The final complete
inspection passes; no source runtime, control, fixture or retained block clock changed.

Retained evidence:

- Fixture root: `/tmp/opencode/dcc-writer-diagnostics-cjmk10w_`.
- Report: `/tmp/opencode/dcc-linux-entity-service-runtime-first.txt`, SHA-256
  `5eb6fddc11ccc114b8bb06d6fd2838424531da6b2c1ce2323cd8cbf5c401438c`.
- Sidecar SHA-256: `2c88013f80a1cd9ee63d938e04dd6fab5eb4af98c9216c965ae85b0db09b7d7e`.
- Before-inspection manifest: `/tmp/opencode/dcc-linux-entity-service-green-retained-files-before.json`,
  SHA-256 `63e5e953fa5feca09f6b58ea2019b003beaf4f4a2bf1822ab722f6ca4a152b25`.
- Inspector/results: `/tmp/opencode/dcc-linux-entity-service-inspect-readonly.py` and
  `/tmp/opencode/dcc-linux-entity-service-inspection-final.txt`. Failed `inspection-first.txt`
  and `inspection-orphan-corrected.txt` remain separately retained with their original sources.

All 447 green entries recheck unchanged before/after inspection, as do all 310 first-red
entries and the accepted forward fixture's 150 files/one symlink. All 307 runtime/control/lock
identities and the unchanged retained runner match. No test is active. **Only strict-service
focus closes** after complete result wiki/privacy/fresh checks; separately reviewed pending-
publication/original-bound repair controls and staged service-affected/broader both-runtime
focused/affected/full integration remain next. S3 roots/access/resource limits, native-Mac
shutdown and dcc-02–05 acceptance remain separate. No remote/production/scheduling/utility/
automatic-expiry/commit/push action.

### Service-affected Linux result — 307-control affected gate closed

The complete 396-line service-result wiki/privacy review is acknowledged. Renewed scoped
audit, both repositories' whitespace checks, all 307 runtime/control/lock identities, the
unchanged retained runner and all green/red/accepted-forward evidence pass before staging.
No source or control changes are selected. A distinct byte-identical 307-identity freeze and
separate hash-bound scope retain **13 existing modules / 307 collected controls** (1.48 s):

- `test_coordination_service.py`, `test_coordination_client.py`,
  `test_coordination_linux_lifecycle.py`, `test_coordination_local_route.py`;
- `test_coordination_recovery.py`, `test_coordination_maintenance.py`,
  `test_coordination_deletion_recovery.py`, `test_coordination_retry.py`;
- `test_coordination_intentional_retry.py`, `test_coordination_intentional_retry_controls.py`,
  `test_coordination_intentional_retry_history.py`,
  `test_coordination_intentional_retry_credentials.py`, `test_coordination_entity_service.py`.

All paths above are under `../Wintap-PyUtil/tests/`. This separately selected scope covers
existing service/client/lifecycle/local-only routing and original-bound raw repair/retry
dispatch; the entire collected report and actual 32-line collection sidecar authenticate.
It excludes `test_coordination_entity_forward_history.py`; the accepted original fixture is
preserved without rerun. The lifecycle's ten-second wait and actual failure diagnostics stay
unchanged. Collection alone does not exercise any CLI, verifier, process-death or recovery gate.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_service.py; ../Wintap-PyUtil/tests/test_coordination_client.py; ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py; ../Wintap-PyUtil/tests/test_coordination_local_route.py; ../Wintap-PyUtil/tests/test_coordination_recovery.py; ../Wintap-PyUtil/tests/test_coordination_maintenance.py; ../Wintap-PyUtil/tests/test_coordination_deletion_recovery.py; ../Wintap-PyUtil/tests/test_coordination_retry.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_controls.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_history.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_credentials.py; ../Wintap-PyUtil/tests/test_coordination_entity_service.py -->

Distinct retained staging artifacts:

- Scope: `/tmp/opencode/dcc-linux-entity-service-affected-first-scope.json`, SHA-256
  `6b896059a5974e62bde665eac11a607612b6d632aed10ca558a720d22b88fef4`.
- Freeze: `/tmp/opencode/dcc-linux-entity-service-affected-first-source-freeze.json`,
  byte-identical to the closed strict-service runtime freeze.
- Collection: `/tmp/opencode/dcc-linux-entity-service-affected-first-collection.txt`,
  SHA-256 `43a641dde646ed3a61ffd83a2d9e6de634a1a3cdeb2a924c81bcc61cdbe3143c`;
  collection-only root `/tmp/opencode/dcc-writer-diagnostics-xnuwuyh0`.

Exact qualification command, initially prepared without a semantic launch:

```sh
.venv/bin/python -B /tmp/opencode/dcc-linux-entity-service-affected-launch.py
```

The reviewed launch helper rechecked scope, all sources, original runner, collection and prior
evidence before invoking the unchanged overwrite-refusing diagnostic-retaining runner with
the exact 13 targets. It used a new fixture root and report
`/tmp/opencode/dcc-linux-entity-service-affected-first.txt`. Complete prepared wiki/privacy/fresh
checks preceded launch; the full actual report/sidecar/diagnostic/artifact/ledger/identity review
below precedes closure. Pending-publication/missing-original controls remain separate and must
not weaken current-only clean resolution or public one-hour validators.

The unchanged service-affected run passes **307 tests in 2,036.10 s (33:56)**, exit 0.
The complete seven-line report, runner sidecar, exact 13-module scope, collection result,
retained runner and all **307 frozen source/control/lock identities** authenticate. Report
SHA-256 is `af9d70ce7752d3bb53b630de216f72c8b03fa1db8d44460f038215d1c00adb9e`; sidecar SHA-256
is `74609b4421b168d8773c3ed5a20b403836d4ab5203dd4e9bb52052cc34d91b76`. The 5,982-entry
post-run fixture snapshot matches the before-inspection manifest; both actual 62-byte child
diagnostics match their retained hashes and record exit 91, empty stderr and `{"run_id": null}`.
Their original receipts identify the actual runs.

Independent read-only inspection validates **170 of 188 ledgers**. The remaining 18 are the
exact retained-history, audit, retry-history and deletion-proof corruption controls expected to
refuse reopen; their fixture identities match the explicit negative tests. For the actual
pre-COMMIT death, the receipt-bound run remains `BLOCKED`, with no typed completion or authority
anchor and no raw-cursor advance. For the actual post-COMMIT death, the supported
`Ledger.entity_evidence()` history accessor authenticates the typed completion and its linked
completion events/authority; the run is `COMPLETED`, the dataset remains `DRAINING`, and the raw
cursor is unchanged. This confirms the intended atomic boundary; it does not establish raw-hour
completion, admission reopening or relaunch permission.

The first post-COMMIT inspection assertion queried the `entity_evidence` storage table directly
and therefore missed the typed completion retained in entity history. That read-only assertion
failed without changing fixtures or the ledger. The corrected inspection uses
`Ledger.entity_evidence()` and its validated retained-event history; the initial inspection
failure/source remain separately retained and are not represented as a test failure.

The accepted forward-history fixture remains unchanged at 150 files/one symlink and was not
rerun. Prior strict-service green/red evidence also matches its retained snapshots. No runtime,
control, fixture or preserved evidence changed during inspection. This closes only the
service-affected Linux gate. Pending-publication/original-bound repair and missing-original
coverage remain unqualified; broader focused/affected/full gates in both runtimes, actual S3,
resource sizing, native-Mac shutdown and dcc-02–05 remain open. No remote/production/scheduling/
utility/expiry/commit/push action.

After recording the result, the fresh changed-wiki/privacy audit passes nine Markdown files,
seven frontmatters, 263 grounded paths, 493 inline sources and 458 wikilinks; six linked diagram
pages validate. The full changed-text privacy scan finds no local username/hostname, IP-like,
account-home or credential-like values. Both repositories' `git diff --check` pass. Existing
index/log frontmatter exceptions are preserved; this is a scoped audit, not whole-wiki lint.

### Pending-publication source review — no new runtime result

Independent of the completed service-affected result, read-only source review distinguishes
standalone matching-candidate retry from coordinated original-bound maintenance. Existing
clean resolution requires the actual exit-zero CLI, successful publication/checkpoint archive
and current-generation independent observation; it cannot certify a partial original. Current
pending journal rows record candidates/window/input/provenance, not coordinator/CLI identities.
The partial-publication path has no successful `entities_verified`/checkpoint records to
reconstruct. Required original eligibility and separate repair representation remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_authority.py §SCHEMA/check/prepare; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/_run; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_operation_verifier.py §_grammar; ../Wintap-PyUtil/wintappy/coordination/entity_writer.py §resolve_entity_prepared -->

A separate source-bound control matrix now covers genuine two-host interrupted genesis/
replay, unchanged clean-resolution refusal, candidate/input/original damage, receipt-before-
maintenance-launch, no-unwind process death/lost acknowledgment, actual clock floors, repair-
versus-resolution, missing migration/deletion coverage and bounded retained history:
[[wiki/work/dbt-compaction-coordination/implementation_plan#Original-bound pending-publication controls — source planning only]].
No pending-recovery tests, data SQL, verifier/entity launch, new source/control freeze or API
implementation is claimed by this review. The service-affected runtime/controls/runner remain
unchanged through the completed result/evidence review; preserved historical originals are not
reconstructed. Broader both-runtime/Linux/S3/resources/native-Mac acceptance stays open.

Complete **327-line** planning successor reviewed against the retained service-affected
baseline, including privacy and all five changed pages. Distinct full snapshot/delta remain
`/tmp/opencode/dcc-linux-wiki-pending-publication-source-planning-first-{snapshot,delta}.diff`;
delta SHA-256 `a74427179090a9407a7e8825dbcfc78cfb4996adcdb61cabb95b7615abd81d12`.
Fresh scoped audit passes nine Markdown files/seven frontmatters, 263 grounding paths,
493 inline sources and 458 wikilinks/82 sections; both repositories' whitespace checks and
all 307 frozen source/control/lock identities pass. Prepared/active/planning log placement
was verified before recording this closure. The later service-affected result is separately
authenticated above; this planning review makes no runtime/control/API change, new recovery
execution or original-eligibility claim. Broader Linux/both-runtime/S3/resources/native-Mac gates
remain open.

### Prior scoped review closure — Linux overlay

Complete tracked feature diffs and new source/tests/configuration were inspected.
The scoped source/config/doc audit passes **30 files (15 tracked / 15 new)**;
fresh Ruff lint and format checks pass **23 Python targets**. The pre-existing
lint/format deviations in `tests/test_dbt_source_validation.py` are preserved;
its complete necessary Makefile-expectation diff was reviewed separately. Unrelated
dataset and environment artifacts are excluded and untouched.

Complete changed-wiki diffs and the new native-Mac tension page were inspected for
privacy; editable infographic XML and its image were also inspected without changing
those user artifacts. Initial scoped Markdown closure passes nine files / seven
required frontmatters, 207 grounding paths, 257 inline sources, 416 wikilinks and
40 section targets. After the affected-green status and next-slice source-review
additions, the follow-up passes **nine files / seven frontmatters, 209 grounding
paths, 263 inline sources, 417 wikilinks and 41 section targets**, with zero new
broken-link/section exceptions. Existing index/log
frontmatter omissions are preserved. This is not a whole-wiki lint or native-Mac
qualification claim. Both repositories' whitespace checks pass.

```sh
# From the Analytics checkout; the audit reads only the changed/new Markdown scope.
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-linux-wiki-audit.py
git diff --check
# From the PyUtil checkout; Ruff uses the explicitly scoped 23 Python targets.
git diff --check
```

Full-main completion and identity checks permit the next source slice.
Audit and local-regression closure do not close broader recovery, endpoint/resource
qualification or dcc-02–05, and authorizes no commit, push or production operation.

### Remaining gates

**dcc-02–05 remain unchecked.** Broader audited partial recovery,
isolated-S3/resource qualification and exclusive entity-maintenance integration remain
unfinished. Raw-only intentional retry has closed local regressions, not Linux acceptance.
The checkpoint path and locally regression-accepted original-bound deletion disposition do not resolve
missing original migration coverage
or pending-publication repair/retry. Immutable publication and typed completion/resolution
have separate focused greens above, not broader entity/service or recovery acceptance.
Such uncertainty stays blocked even after an
unauthenticated standalone repair. Exact isolated
S3 roots/access and fixture scope must be confirmed before remote qualification.
Representative retained-state sizing still starts at 32 GB RAM / 64 GB disk with
aggregate monitoring; a reduced-limit recommendation needs a separate measured rerun.
Native-Mac shutdown remains its worker's separate gate. No production mutation, cron
installation, automatic grant expiry, uncertain-write reopening, commit or push.

## Test Commands

Review baseline: Analytics `91f741e`, PyUtil `c782f63`. Both repositories were
pulled with `git pull --ff-only`; Analytics fast-forwarded from `d904559` and PyUtil
was already current. Existing unrelated PyUtil untracked data/environment artifacts
were preserved. No code implementation, cron deployment or push occurred.

The preceding sentence describes the review baseline, not the authorized work below.

### Authorized integrity/provenance slice — red/green

Human authorization explicitly requires active-path red/green regressions, bounded
SQL validation, stable bootstrap provenance and rollback-safe forward evolution.
Implementation is committed locally in PyUtil as `7d2b7f8`; no production scheduling or push.

Before changing implementation, added `tests/test_entity_integrity.py` and ran in
the standalone compactor:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_entity_integrity.py
```

**Red: 75 failed, 10 passed** across 85 cases. Forty corruptions are exercised
independently through CLI `entities-verify` and `update_entities()`; the producer
unknown-key case and four provenance cases add five tests. Failures include
duplicate keys, noncanonical hosts, invalid bounds/evidence, non-parent scalar/flag
disagreement, and bootstrap drift on changed/unchanged updates, replay and resumed
init. The ten already-rejected corruption cases remain negative compatibility
controls. A preliminary verify-first run was strengthened to independent entrypoint
parameterization so update failures are visible even when CLI verification fails.

After implementation, the same 85 cases plus the existing entity/CLI regressions
pass: **123 passed**. Expanded positive controls cover valid identity/lifetime/parent
conflicts, missing/sentinel parents, empty initialized hosts, retained evidence,
no-op replay and temporary-relation cleanup with `Evidence.restore` replaced by a
failure hook. Actual CLI replay also proves original bootstrap agreement in report,
snapshot and published checkpoint. The expanded new-test run is **92 passed**;
additional positive controls cover signed-integer boundaries and an empty parent
candidate set remaining a retained entity with missing context. All **94 new tests**
pass in the final standalone run.

Implementation reuses the SQL reducer to derive all expected scalar/flag columns
in separate spillable temporary relations and compares them null-safely. It also
validates unique/valid keys, canonical stored hosts, exact JSON fields/array types,
numeric/string/parent element types, duplicate candidates and ten-digit calendar
publication-hour bounds. Python retains no decoded entity cache. Existing validated
snapshot metadata is reused rather than reconstructed from the update start.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §validate_state/_validate_evidence/_reduce_state; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

Full standalone regression command (same isolated wrapper):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider
```

Final result: **234 passed, 2 skipped** (opt-in S3), 49.68 seconds. Changed-file Ruff
lint/format checks pass. The first main cross-runtime rerun caught three lowercase
CLI-host validation failures; canonicalized the caller's host while still requiring
canonical stored rows. That repair is included in the final standalone tests and
a full main-suite rerun initially returned **314 passed, 3 skipped, 1 failed** in
203.35 seconds. The remaining default-config test reads a pre-existing ignored local
settings file containing a dataset setting. It independently fails in the checkout
and passes from a disposable working directory (**4 config tests passed**). The
settings file is untouched. The fully isolated main-suite rerun passes:
**315 passed, 3 skipped**, 202.14 seconds, including all raw/mixed/compacted entity
DBT builds and CLI verification. Its child pytest invocation uses the absolute
main-environment Python and test-directory paths, `PYTHONPATH=<checkout>`, and a
disposable working directory plus `TMPDIR`/`--basetemp` under `/tmp/opencode`.
No unmodified test expectation was relaxed.

An added empty-parent positive fixture initially triggered a legitimate normalization
rewrite because `json_merge_patch` changed JSON key ordering. Corrected the fixture
to preserve canonical serialization; no-op replay and entity retention now pass.

### Bounded synthetic validation probe

A disposable standalone DuckDB 2.0.0 fixture creates 20,000 recorded synthetic
entities, then runs initial update/publication and unchanged replay with Python
`Evidence.restore` disabled. Settings: two threads, 256 MB DuckDB memory and
512 MB temporary storage. Results: initial update 2.468 seconds; replay 1.913 seconds;
20,000 entities; unchanged replay; traced Python peak **1,178,319 bytes**; process
peak RSS **344,120 KiB**. The fixture and spill directory were automatically removed.

This demonstrates SQL-backed validation at small scale, not a Python-versus-SQL
benchmark or a realistic accumulated-state budget. Traced Python allocations are
not total RSS, DuckDB memory limits are not total-process RSS caps, and spill usage
was not measured. Multi-million-entity steady-state qualification remains open.

### Pre-R1 freshness probe — historical red

Used the real main-suite fixture and isolated compactor: retain the original snapshot,
add next-hour process evidence, publish via `entities-replay`, then run real DBT
`validate_raw_sensor_source`. Historical checkpoints contain **two distinct aggregate
hash populations** and forward preflight exits **0**, as required. Restore only the
original snapshot, retaining checkpoints: snapshot integrity correctly passes, but
DBT preflight also exits **0** when freshness should fail. The fixture is disposable
and removed automatically; it does not modify a real dataset.

R1 is therefore **not repaired** by the R2/R3 slice. This independent probe separates
integrity from freshness and demonstrates why every historical hash cannot be
compared to today's aggregate. The next slice needs current-state authority,
historical receipt/lineage validation, recorded publication-intent recovery and an
explicit legacy-state upgrade/cutover contract.

### R1 current-state authority and lineage — red/green continuation

Milestone commits: PyUtil `7d2b7f8`, Analytics `739e64f`; both are local only.
Added formal operational regressions before implementing R1. Standalone command:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_entity_freshness.py
```

**Red: 10 failed, 1 passed**. Integrity-valid snapshot rollback, empty replacement,
bootstrap replacement, missing authority and expected-host rebinding independently
pass CLI verification/update when they should fail. The forward-evolution/replay
control passes. The real main-runtime DBT command against its new same-named test
module returns **8 failed, 1 passed**: four current-state and four historical
checkpoint corruption cases pass preflight incorrectly; differing historical hash
populations correctly pass forward preflight. Both red runs used disposable
`TMPDIR`/pytest roots under `/tmp/opencode` and cleaned their fixtures.

Implemented the selected Parquet authority journal, strict generation/binding/host
lineage, content-derived receipt IDs, pending-before-host and committed-after-recheck
publication, and version-4 coverage linked to its own receipt. CLI rejects untrusted
current bytes/provenance; DBT checks current semantic identities and historical
receipt evidence without equating old hashes to today's aggregate. Read-only local
DBT with entities disabled retains the direct, authority-independent path.

The initial focused pass found two fixture-scope issues: the valid empty-parent
fixture manually replaced a committed snapshot, and the old S3 snapshot failure
hook now intercepted an earlier authority PUT. Constructed the valid empty-parent
candidate before initial publication and restricted that hook to snapshot keys;
the same active verification/no-op and lost-ack recovery expectations are retained.
Added separate authority PUT/ack failure points, altered-intent/input rejection,
receipt corruption and missing-ancestor tests. Expanded standalone focus passes
**164 tests**. An initial main focus caught incompatible unnamed-row JSON between
DuckDB 1.5.6 and 2.0.0. Named-struct JSON hashing with 1,024-row digest batches
repairs that boundary; **14 real-DBT tests pass**, including Unicode and multiple
digest chunks.

Three further real-DBT cases (null checkpoint status, null hour end and altered
window start) were added before their repair: **3 failed**, then strict null-safe
status, exact hour/window receipt checks and explicit legacy schema rejection were
implemented. Final full runs include these cases plus paired fresh entity/metrics
root rebuild/cutover with old evidence preserved. The full standalone suite passes
**266 passed, 2 skipped**, 91.46 seconds. Initial isolated main full run returns
**334 passed, 3 skipped, 1 failed**, 349.35 seconds: the threshold mismatch still
fails closed, but its earlier authority rejection omits the existing test's
`Processing metrics` diagnostic. Preserved that expectation by explaining the shared
authority/metrics roots/hosts/policy binding in the diagnostic; the targeted test
then passes. The full isolated main acceptance rerun passes **335 passed, 3 skipped**,
348.05 seconds (`/tmp/opencode/dcc-r1-main-accepted.txt`). R1's regression gate is
accepted; R4/R5 and actual coordinated lifecycle qualification remain open.

All test wrappers use the project's Python, not the system Python. Two initial
wrapper launches failed before pytest because the system Python lacked modern
`subprocess.run` arguments; corrected wrappers produced the recorded red results.
No remote qualification, real dataset mutation, push or scheduler deployment.
The local writer's directory-fsync path is qualified on Linux only; other writer
platforms and actual endpoint failure/recovery remain unqualified.

### R4 independent phase evidence — historical red

Added five operational tests before implementation and ran standalone
`tests/test_phase_evidence.py`: **5 failed**, 4.64 seconds. The injected final
checkpoint failure follows successful deletion and surviving compacted outputs,
but leaves no original phase archive. Additional cases lack a stable run mapping,
immutable migration evidence across replay, exclusive original-generation checkpoint
repair, refusal to certify skipped hours and rejection of run-identity reuse.
The tests use the active `cli.run()` entrypoint with Namespace fields representing
the proposed CLI options, avoiding argparse failures as a substitute for behavioral
evidence. Fixtures are synthetic, bounded and automatically removed.

### R4 integration and additional negative evidence

The original five cases pass after CLI/archive/migration/checkpoint repair integration
(`dcc-r4-focus.txt`: **5 passed**, 4.24 seconds). They now parse the real CLI options.
Additional active-path probes were captured before their repairs:

- `dcc-r4-hardening-red.txt`: **4 failed, 18 passed**, 16.25 seconds. Repair could
  incorrectly succeed after a checkpoint PUT changed a source, output or entity;
  deletion could proceed after source mutation during intent-record publication.
- `dcc-r4-finalstate-red.txt`: **2 failed**, 1.46 seconds. Ordinary archived compaction
  could certify completion despite an output/entity change during checkpoint PUT.
- `dcc-r4-byteidentity-red.txt`: **2 failed**, 1.11 seconds. Same-size/mtime source
  mutation during deletion intent escaped metadata checks, and duplicate JSON keys
  were accepted by the archive loader.

Repairs recheck streamed byte identities after deletion intent, surviving migrations
and current SQL-validated entity authority before/after checkpoint writes, all final
checkpoint rows, and exact canonical archive bytes. The first expanded affected
suite passes **64 tests** (39.57 seconds). Further archive budget/link/fsync/symlink,
scope, conflicting-coverage disposition, reconciliation and protocol/hour tests are
being qualified. An expanded archive run initially passes 38 tests with one fixture
failure: its fake S3 `ObjectFile` omitted the existing normalized `raw_sensor/`
inventory prefix. Corrected the synthetic fixture, not the path-safety requirement.
That fixture correction retains the scope checks.

### R4/R5 prerequisite acceptance — final revision

`dcc-r4-directory-links-red.txt`: **2 failed** before repairing unflushed new
directory links. The accepted full standalone suite includes that repair:
**307 passed, 2 skipped**, 119.90 seconds (`dcc-r4-standalone-accepted.txt`),
including **41 phase/archive tests**. The real two-runtime checkpoint test injects
a second checkpoint failure after deletion, evolves entities, then repairs the
original generation with unchanged entity/original archive bytes and a successful
real DBT full build (`tests/test_checkpoint_repair.py`). Conflicting newer coverage
is explicitly retained and replaced in a new repair archive; it is never silently
discarded. These passes qualify the tested synthetic Linux paths, not power loss.

R5 captured **two real behavioral failures** and **one missing-resolver failure**
before fixing active-root routing (`dcc-r5-red.txt`). Four active-remote controls
initially had fixture-only failures; the corrected fixtures preserve their remote
activation expectations and all four pass (`dcc-r5-controls.txt`). Final **7 routing
tests pass** (`dcc-r5-green.txt`), including direct full local `make dbt-build` with
entities disabled and an unused remote metrics override, without credentials.

The combined isolated main suite passes **343 passed, 3 skipped**, 410.83 seconds
(`dcc-r4-r5-main-final.txt`). It started before the directory-link repair. The final
affected-main run includes that repair and passes **51 passed, 1 skipped**,
331.06 seconds (`dcc-r4-r5-final-revision.txt`): checkpoint repair, entity freshness,
effective roots, process entities and compacted inputs. Both use absolute main
interpreter/test paths, disposable working directory, `PYTHONPATH=<checkout>`,
`TMPDIR`, pytest `--basetemp` and `-p no:cacheprovider`; unrelated local settings
remain untouched. Scoped Ruff lint passes and the earlier 14-file format check
passes. Both repositories' `git diff --check` pass. Corrected artifact validation
recognizes the existing index/log catalogs rather than parsing their body separators
as YAML: **7 frontmatters, 117 grounding paths, 354 links** and added-content
IP/account-home-path scans pass across nine changed wiki files. Diff review uses
only synthetic identifiers/aggregate results; no identifier disclosure is authorized.

R4/R5 and dcc-00 are prerequisite regression acceptance only. Real coordinated
writer lifecycle, endpoint recovery, whole-authority rollback high-water enforcement
and realistic accumulated-state resource budgets remain separate gates.

### dcc-01 protocol/ledger — implementation baseline

Added strict protocol and real-DuckDB ledger tests before implementation:
**26 failed** solely because `wintappy.coordination` was absent, 0.17 seconds
(`dcc-01-missing-red.txt`). This is missing-implementation evidence, not 26
behavioral regressions. The first protocol implementation passes its initial
**16 tests**, 0.05 seconds (`dcc-01-protocol-initial.txt`). Ledger implementation
and additional behavioral failure points are next; no coordinator/client or real
writer has been launched by this slice.

### dcc-01 transactional authority and hardening — red/green

The initial ledger implementation passes its **10 tests**, 1.61 seconds
(`dcc-01-ledger-initial.txt`). Added behavioral negative probes before fixes:

- Protocol: **6 failed, 16 passed**, 0.16 seconds
  (`dcc-01-protocol-hardening-red.txt`): unhashable action/policy fields did not
  produce protocol errors, failed GET body transfers leaked raw exceptions,
  aggregate listing byte limits were missing, cyclic continuation tokens continued
  listing, and deeply nested JSON leaked a raw recursion error.
- Ledger: **6 failed, 19 passed**, 3.11 seconds
  (`dcc-01-ledger-hardening-red.txt`): orphan writer intent, reader/writer overlap,
  stored request-digest corruption and extra schema columns were accepted on reopen;
  S3 state directories created unintended local paths; transport could publish
  beneath a telemetry scan root. Corrupt-ledger tests require refusal without
  rewriting/recreating authority, not merely a later failed writer.

The repaired combined focus passes **47 tests**, 3.20 seconds
(`dcc-01-hardening-green.txt`). Final expansion adds real abrupt process death
before/after grant and writer COMMIT with WAL recovery, no reader expiry despite
old timestamps, conflicting remote grant retention, failed-initialization refusal,
short streamed reads and original whitespace accounting in byte budgets:
**54 passed**, 6.03 seconds (`dcc-01-final-focus.txt`). Command:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_coordination_protocol.py tests/test_coordination_ledger.py
```

All runs use the isolated main-runtime wrapper described above. Reservations and
outbox commit before PUT; terminal state suppresses pending grants; writer/run
intent commits before any caller-managed launch. A second real process gets busy
before opening DuckDB. Unresolved writer intent becomes `BLOCKED`, retaining the
cursor and independent CLI/coordinator IDs. There is no cursor-advance or reopening
API yet; actual writer completion and high-water enforcement remain dcc-02/dcc-04
integration obligations. Synthetic crash/WAL evidence is not power-loss evidence.

Final combined scoped Ruff lint passes; **20 files** pass format. Both repositories'
whitespace checks pass, including a separate newline/whitespace scan of **14
feature-owned untracked files**. Current wiki artifact checks pass seven
frontmatters, **127 grounding paths and 354 links**; added-content privacy scans
and the scoped code/wiki/new-file review retain only synthetic identifiers in
persistent wiki additions. Existing index/log catalogs are not parsed as YAML.
The full isolated main suite passes **397 passed, 3 skipped**, 414.36 seconds
(`dcc-01-main-final.txt`), including the final 54 protocol/ledger cases and the
R4 directory-link repair. dcc-01 is regression accepted after artifact review.
No scheduler, client wrapper, actual S3 qualification or real destructive child was
introduced. Unrelated settings/data and milestone commit anchors remain unchanged.

### dcc-02 controlled-clock scheduling — implementation baseline

Added `tests/test_coordination_tick.py` before implementation. The isolated main
wrapper returns **20 failed**, 1.05 seconds (`dcc-02-scheduling-missing.txt`), all
`ModuleNotFoundError` for `wintappy.coordination.coordinator`. This is missing-
implementation evidence, not 20 behavioral regressions. Tests specify UTC
midnight/grace boundaries, persisted oldest-hour selection, overlapping readers,
terminal-first cancellation, due-writer draining, queued and undelivered grants,
API failures, duplicate ticks, failed callbacks and a surviving synthetic child.

This first slice must reject unverified callback claims, including exit-zero
`completed`/`empty` results. Supervision, verified completion/cursor advancement,
backlog reopening and real compactor integration remain later qualification;
dcc-02 is not yet accepted. No production scheduler or real-data operation occurs.

### dcc-02 admission/draining and hardening — red/green

Initial tick plus protocol/ledger focus passes **74 tests**, 7.33 seconds
(`dcc-02-scheduling-initial.txt`). Added behavioral probes before repairs:

- **5 failed, 23 passed**, 3.04 seconds (`dcc-02-scheduling-hardening-red.txt`):
  later terminal/request conflicts or a later listing failure could retire an
  earlier reader reservation; callback observations were discarded; invalid
  writer commands were not rejected before access/admission. Completed listings
  followed by atomic terminal-first ingestion now preserve every prior reservation
  on batch failure. Early adapter/command validation and bounded untrusted scalar
  observations repair the other cases. Combined focus then passes **82 tests**,
  8.78 seconds (`dcc-02-scheduling-hardening-green.txt`).
- **2 behavioral failures**, plus **one fixture-only failure**, 7.82 seconds
  (`dcc-02-blocked-diagnostic-red.txt`). Missing or inconsistent blocked-state
  reasons were accepted on reopen. A test insertion accidentally moved the
  original open-ledger control into a blocked-writer fixture; restored that
  control without changing its expectation. The clean pre-fix rerun is
  **2 failed, 39 passed**, 7.25 seconds
  (`dcc-02-blocked-diagnostic-controlled-red.txt`). Reopen now rejects both
  diagnostic corruptions without recreating or changing database bytes.

Final combined focus passes **100 tests**, 12.35 seconds
(`dcc-02-scheduling-final-focus.txt`): 36 tick, 41 ledger and 23 protocol tests.
It adds atomic batch and blocked-disposition transaction failures, bounded
count/byte exhaustion, iterator failure, callback interruptions/identity mutation,
malformed/oversized/empty results and a real abrupt tick death with a surviving
synthetic child. The committed intent/cursor survive WAL recovery; a later tick
cannot launch a replacement or publish new grants. Only test-owned synthetic
children are terminated during cleanup. No real compactor is invoked.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_coordination_tick.py tests/test_coordination_protocol.py \
  tests/test_coordination_ledger.py
```

Runs use the absolute-interpreter/test-path, disposable-CWD main wrapper above.
The full isolated main regression passes **443 tests, 3 skipped**, 558.24 seconds
(`dcc-02-main-regression.txt`). This run qualifies the admission/draining revision,
not subsequent supervisor changes. Scoped Ruff lint and **22-file** format checks,
both repositories' whitespace checks and **16 feature-owned untracked-file**
newline/whitespace checks pass. Wiki review covers seven frontmatters, **135** live
grounding paths and **355** links across nine changed files. Addition privacy scans
and the complete wiki diff review pass; unrelated artifacts remain untouched.
The callback seam does not supervise or certify any writer: all returned claims
stay blocked and no cursor advance/reopening API exists. Its persisted scalar
observations are diagnostics, not full worker reports/phase receipts. Full child-
tree supervision, verified empty-hour completion, backlog advancement, advisory
S3 status and real CLI integration remain required before dcc-02 acceptance.

### dcc-02 Linux supervision — implementation baseline

Recorded **16 missing-module failures**, 0.19 seconds
(`dcc-02-supervision-missing.txt`), before adding the isolated Linux subreaper
supervisor. This is implementation-baseline evidence, not behavioral regression.
The first implementation passes **16 tests**, 2.93 seconds
(`dcc-02-supervision-initial.txt`): root exit with ordinary/detached descendants,
SIGTERM-resistant timeout, unrelated-child isolation, preserved run directories,
bounded stdout/stderr and exact structured-report checks. These tests do not
certify a writer or reopen admission. Interruption, nested reparenting, worker
failure and capture/publication error probes are next; dcc-02 remains unchecked.

### dcc-02 supervision and evolving clocks — recorded hardening

Captured before repairs, using the same isolated main wrapper:

| Report under `/tmp/opencode/` | Result | Active-path finding |
|---|---|---|
| `dcc-02-supervision-hardening-red.txt` | **2 failed, 20 passed**, 5.06 s | A second report read parsed unchecked replacement bytes; capture failure could leave a launched child and retain a false pre-launch shutdown assertion. |
| `dcc-02-supervision-setup-red.txt` | **3 failed, 23 passed**, 5.94 s | Selector setup failure did not stop the launched root; two malformed capture records raised raw key errors instead of coordination errors. |
| `dcc-02-supervision-scalar-red.txt` | **2 failed, 30 passed**, 6.86 s | Non-string status and enormous integer budgets raised type/overflow errors. |
| `dcc-02-supervision-control-red.txt` | **1 failed, 32 deselected**, 0.26 s | A nonreading worker with a large control payload produced a raw broken-pipe failure. The probe uses a short-lived synthetic worker; it does not measure an indefinite-hang deadline. |
| `dcc-02-supervision-exit-red.txt` | **1 failed, 3 passed, 30 deselected**, 0.97 s | An `exited` observation lacking the root exit code was accepted for report reads. |

The first two repairs pass **26 tests**, 5.78 seconds
(`dcc-02-supervision-hardening-green.txt`). Further scalar/control/exit repairs
validate metadata and budgets before use, require consistent root-exit/shutdown
evidence, use sealed bounded control memory instead of a potentially blocking
stdin pipe, and translate missing observations into coordination failures.
Unexpected capture/setup exceptions now kill/reap the launched tree before
propagating; unavailable subreaper support refuses launch. Report parsing consumes
exactly the checksum-verified bytes, never rereads the path to parse a replacement.

The evolving-clock baseline is **4 failed, 36 passed**, 7.26 seconds
(`dcc-02-evolving-clock-red.txt`), solely because `clock=` is absent; this is a
missing-interface baseline, not four behavioral regressions. Refresh observations
after complete listings, grant delivery and writer callback. Clock rollback/access
failure before ingestion retains reservations; post-write clock errors still block
the committed intent using the last valid observation before propagation.

Final combined focus passes **142 tests**, 23.13 seconds
(`dcc-02-supervision-clock-qualified-focus.txt`): **44 tick, 34 supervisor, 41 ledger,
23 protocol**. This includes real nested/`setsid` descendants, SIGTERM-resistant
timeout, unrelated-child isolation, caller INT/TERM/death cleanup, worker death with
a surviving workload and a real supervised callback holding the ledger lock. A
parsed exit-zero empty report still cannot advance the cursor or reopen admission.
Only synthetic test-owned processes are terminated during cleanup. No real
compactor or S3 endpoint was used. Intermediate combined focus reports retain
134/141 passes; the 142-test run is the final revision evidence.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_coordination_tick.py tests/test_coordination_supervisor.py \
  tests/test_coordination_protocol.py tests/test_coordination_ledger.py
```

The full isolated main run for this revision passes **485 tests, 3 skipped**, 609.86
seconds (`dcc-02-supervision-main-regression.txt`), distinct from the earlier **443-pass**
admission/draining revision. Scoped Ruff lint and **24-file** format checks pass;
both repositories' `git diff --check` and **18 feature-owned untracked-file**
newline/whitespace scans pass. Wiki checks cover **seven frontmatters, 145 live
grounding paths and 355 links** across nine changed files. Added-content privacy
scans and the complete 1,331-line wiki diff review pass; no actual host/account/IP
identifiers are added. Unrelated settings/data remain untouched. Linux
subreaper observations apply to cooperative descendant trees only, not external
services, hostile/cgroup containment or non-Linux client platforms. Workload,
startup/cleanup, control/log/report bounds do not certify filesystem/kernel I/O,
RSS or power-loss budgets. These observations are not migration/configuration
receipts; the command manifest deliberately omits environment values. Full service
binding, verified raw/entity/checkpoint completion, authority high-water enforcement,
transactional cursor/backlog/reopening and advisory status remain required.

### dcc-02 collaborative review — confirmed grace defect and completion contract

On November 14, a disposable controlled-clock probe exercised the live tick and
real main-runtime DuckDB ledger with synthetic S3. It called the original
`Ledger.ingest_many`, then advanced the injected clock before returning to the
tick; no ingestion/admission behavior was replaced. Invocation used
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<pyutil-checkout>
<pyutil-checkout>/.venv/bin/python -B -` from `/tmp/opencode`, with automatically
cleaned temporary fixture directories.

The pre-grace control returns `OPEN`, one reader and one grant. Advancing from
`00:09:59` to the `00:10:00` grace boundary during ingestion instead returns
`DRAINING` with one newly reserved reader and one grant. Expected: `DRAINING`, zero
readers/grants and one queued request. The probe exits 1 with **one behavioral
assertion failure**, not a pytest suite result; its control assertion passes.
Evidence: `/tmp/opencode/dcc-02-review-ingestion-clock-red.txt`.

The clock observation precedes ingestion and is reused for admission; the next
refresh happens after grant publication. This is a writer-priority defect, not
demonstrated reader/writer overlap: the new reservation still excludes the writer.
The human confirms that requests not yet reserved when grace expires must remain
queued. Refresh after ingestion before deciding admission; preserve existing
reservations. Formal regression and repair were pending at this review; slice A
subsequently records their red/green implementation below. The earlier 142/485
passes did not cover this boundary and are retained as historical run evidence.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick; ../Wintap-PyUtil/wintappy/coordination/ledger.py §ingest_many/admit -->

The human also confirms the intended completion gate: execution/configuration/run
binding, independently verified migration/deletion or empty-hour evidence,
entity/authority/checkpoint and independent high-water checks when enabled, and
confirmed supervised shutdown must precede success. Retain completion evidence,
complete the run, advance exactly one hour and select `DRAINING` for due backlog
or `OPEN` otherwise in **one ledger transaction**. Queued grants follow COMMIT;
uncertainty retains the cursor and blocks admission/replacement launch. A callback
claiming `empty` is not verified empty-hour evidence. This confirms the design,
not an implemented success API or dcc-02 acceptance. No code was changed during
this review, and no production writer/endpoint was exercised.
<!-- SYNTHESIS: human-confirmed review contract on 2026-11-14, consistent with wiki/work/dbt-compaction-coordination/design.md §7 and §8 -->

### dcc-02 review requirement — non-secret execution/configuration receipt

The human expressly requests an allowlisted, non-secret effective execution and
configuration receipt after reviewing the supervisor manifest's omission of
environment values. Requirement added to the brief, design, handoff and plan:
[[wiki/work/dbt-compaction-coordination/design#Required execution and configuration receipt]].

Acceptance evidence requested at this review: bind the actual qualified executable/runtime/arguments
and resolved roots/hour/run IDs/events/entity policy/deletion/budgets to durable
writer intent before launch; prove default/override/allowed-environment resolution,
receipt integrity and bounds, mismatched scope/command refusal and synthetic secret
exclusion from persisted artifacts/diagnostics. Post-launch uncertainty cannot
advance the cursor or reopen admission. A partial command manifest or exit-zero
report is insufficient. No implementation or behavioral test result is claimed
by this historical review. Slices B/C subsequently implement and verify the
receipt/separate-verification libraries below; dcc-02 remains unchecked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_manifest -->
<!-- SYNTHESIS: explicit human requirement on 2026-11-14, recorded before implementation -->

### Commit snapshot — November 14

Committed the 32 feature-owned PyUtil files as `fe7fcb5` on
`work/raw-sensor-compacted-union`: R1/R4/R5, protocol/ledger and tick/supervision
prototypes, tests and READMEs. Preserved unrelated data, environment files and
ignored settings. The source coordination README at that commit explicitly records the
unrepaired ingestion/grace defect and pending execution-receipt requirement.

Fresh isolated main-runtime rerun of the four coordination test modules passes
**142 tests**, 25.04 seconds (`/tmp/opencode/dcc-commit-coordination-focus.txt`).
It uses absolute interpreter/test paths, disposable CWD, `PYTHONPATH=<checkout>`,
`TMPDIR`, pytest `--basetemp` and `-p no:cacheprovider`. No fresh full-suite result
is claimed; the earlier 485/three-skip run and separate red grace probe retain
their original scope. The ingestion/grace regression is not in this passing suite.

Staged scope, whitespace, file bounds and credential/account-path scans pass.
Scoped Ruff lint/format passes **23 Python files**. The broader lint invocation
reports **53 findings** in two legacy test files; checks against their HEAD
versions confirm identical findings, and neither is reformatted. Evidence:
`/tmp/opencode/dcc-commit-lint-baseline.txt`. Wiki review passes eight frontmatters,
152 grounding paths, 52 scoped links and complete-diff privacy/whitespace checks.
This is an interim snapshot, not dcc-02 acceptance or real-writer qualification.
No push was performed; the human will push both repositories.

### Maintainer milestone review — November 14

Fresh review after fast-forward pulls to Analytics `660b5a8` and PyUtil `fe7fcb5`.
Earlier feedback notes were preserved, index/log conflicts resolved and the verified
preservation stash dropped. Read the worker plan/verification and live repair,
authority, phase-archive, routing, protocol/ledger and tick/supervision sources.
Findings and dispositions: [[wiki/work/dbt-compaction-coordination/implementation-review]].

**Fresh macOS runs:** standalone Python 3.14.0 / DuckDB 2.0.0; main Python
3.12.12 / DuckDB 1.5.6. Wrappers resolve interpreter/test paths absolutely, run
from automatically cleaned temporary directories under the harness-approved root,
set `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH` and `TMPDIR`, and pass isolated pytest
`--basetemp` plus `-p no:cacheprovider`. Commands below show checkout-relative
interpreter/targets. No source/test files were edited.

Standalone full suite:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -rs -p no:cacheprovider tests
```

**305 passed, 2 failed, 2 skipped**, 61.28 seconds. Both failures are the
`test_new_publication_directory_links_are_fsynced_before_success` cases: the test's
fsync observer reads Linux `/proc/self/fd`, unavailable on macOS. The two skips
are opt-in S3 transport cases. Other authority, integrity, provenance, phase repair
and compaction cases pass.

Main focused suite:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -rs -p no:cacheprovider \
  tests/test_coordination_protocol.py tests/test_coordination_ledger.py \
  tests/test_coordination_tick.py tests/test_coordination_supervisor.py \
  tests/test_entity_freshness.py tests/test_effective_input_roots.py \
  tests/test_checkpoint_repair.py tests/test_process_entities.py \
  tests/test_dbt_source_validation.py tests/test_compacted_inputs.py
```

**196 passed, 3 failed, 35 skipped**, 205.15 seconds. All three failures are
unguarded Linux assumptions in `test_coordination_tick.py`: abrupt tick death with
a surviving child reads `/proc/<pid>/stat`; two supervisor integration tests expect
a report or PID file after the Linux-only supervisor correctly refuses launch.
The dedicated supervisor module correctly skips its 34 cases; the remaining skip
is opt-in isolated migration. The included real-DBT freshness/forward-lineage,
cross-runtime checkpoint repair and local-only routing/build cases pass. These
results do not repeat the worker's Linux supervision or remote qualification.

**Independent review probes:**

- R6: wrap the original `Ledger.ingest_many`, advancing only an injected clock
  after it returns, using real local DuckDB and the existing fake S3 helper.
  Pre-grace control passes (`OPEN`, one reader/grant). Crossing `00:09:59` →
  `00:10:00` produces `DRAINING`, one new reader/grant and zero waiting instead
  of zero new readers/grants and one waiting request. The script exits 1 at that
  behavioral assertion. This independently corroborates the worker's known defect.
- R7: in a separate standalone Python process, replace
  `entity_sql._validate_evidence` with a no-op in memory and call `pytest.main`
  for `tests/test_entity_integrity.py -k corrupt_snapshot_rejected_by_verify_and_update`.
  **80 passed, 14 deselected**, 8.93 seconds. The test selection still passes
  because it rewrites committed snapshots and accepts generic authority errors.
  This is mutation evidence of a test gap, not a valid integrity acceptance run.
- R7 controls: use the live seed/rewrite fixture helpers for duplicate-key and
  `os_pid`/evidence disagreement, then invoke `EntityStore.validate_sql` directly.
  Both are rejected with the intended SQL diagnostics. Under the same in-memory
  no-op mutation, both are accepted. The probes establish the repaired validator's
  behavior and identify an independent entrypoint for durable negative tests.

Each probe used disposable synthetic fixtures with automatic cleanup and restored
in-process patches. No actual endpoint, scheduled writer or source-code edit was
involved. R6–R8 are open follow-through in the plan; dcc-02–05 remain unchecked.
The earlier R1–R5 red/green history is retained with its original scope.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py; ../Wintap-PyUtil/tests/test_coordination_tick.py -->

Documentation checks pass for five changed wiki files: three frontmatters, 65
grounding paths and 15 wikilinks/section targets. Whitespace and added-content
home-path/IP scans pass; the complete diff was reviewed for privacy. PyUtil retains
only its pre-existing untracked environment artifacts. Review additions were
uncommitted at review completion; the human subsequently requested publication.

### Completion planning — November 14

Reviewed the current brief/design/handoff/plan, R6–R8 findings and live coordinator,
ledger, supervisor, Makefile, root resolver, CLI, storage resolution, authority and
phase-verification sources. Confirmed the missing success/history/cursor API,
service/client integration and real-writer completion dependencies. This was a
source/planning review, not a new runtime acceptance run.

Human-selected scope: Linux coordinator/writer, Linux/macOS readers; actual existing
S3 endpoint with fresh feature-owned fixtures, exact roots/access confirmed before
writes; initial 32 GB RAM / 64 GB disk qualification with aggregate usage monitoring,
then a reduced-limit recommendation. Reduced-limit acceptance requires its own
representative rerun. No low-budget pass, macOS support or endpoint qualification
is claimed. See the dependency slices and remaining inputs in
[[wiki/work/dbt-compaction-coordination/implementation_plan#Completion plan — November 14]].
<!-- SOURCE: Human planning decisions, conversation 2026-11-14. -->

No source changes, runtime tests, remote writes, fixture deletion, deployment or
push were performed during planning. All R6–R8 and dcc-02–05 implementation gates
remain open.

Scoped documentation checks: `git diff --check` passes. A read-only main-runtime
Python/YAML check validates six changed wiki files, four feature-page frontmatters,
85 grounding paths and 344 wikilinks/section targets. Added-content home-path/IP
scan and complete-diff privacy review pass. The initial strict check identified
pre-existing missing frontmatter in `wiki/index.md` and `wiki/log.md`, confirmed
against HEAD and left unchanged; this is not a whole-wiki lint pass.

### Completion slice A — review repairs

All runs use `/tmp/opencode/dcc-run-tests.py` with the main interpreter for the
wrapper, absolute runtime/test paths, disposable working directory, isolated
`TMPDIR`/`--basetemp`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH` and
`-p no:cacheprovider`. Standalone and mutation runs use the standalone interpreter.
Reports are local evidence, not copied source or remote telemetry.

| Run / report under `/tmp/opencode/` | Selection | Result |
|---|---|---|
| `dcc-r6-formal-red.txt` | main tick: `-k 'ingestion_clock_is_refreshed or clock_failure_after_ingestion'` | 4 failed, 2 passed before post-ingestion clock repair |
| `dcc-r8-procfs-red.txt` | standalone phase tests: `-k new_publication_directory_links` | 2 failed with `/proc` denied before portable observer repair |
| `dcc-r7-independent-sql-mutation-red.txt` | standalone integrity: `-k sql_integrity_rejects`, in-memory `_validate_evidence` no-op | 80 failed, 94 deselected (expected mutation rejection) |
| `dcc-r6-r8-main-green-final.txt` | protocol, ledger, tick and supervisor modules | 150 passed, 24.45 s |
| `dcc-r7-r8-standalone-green.txt` | integrity and phase-evidence modules | 215 passed, 102.29 s |
| `dcc-r7-r8-full-standalone.txt` | complete standalone `tests` | 387 passed, 2 opt-in S3 skips, 153.13 s |
| `dcc-r6-r8-full-main.txt` | complete main `tests`, before slice B additions | 493 passed, 3 skips, 616.08 s |

R6 refreshes immediately after the original atomic ingestion, before admission.
Exact grace and post-ingestion rollback/unreadable clocks preserve prior reservations
and leave unreserved requests queued. The admission-focused fixture omits the
writer adapter: an eligible hour with zero readers may legitimately launch when
an adapter is supplied; the intermediate contrary expectation was corrected.

R7 adds 40 corruption classes at each of two authority-independent entrypoints:
direct `validate_sql` and the next publication candidate during active update.
SQL-specific diagnostics and unchanged committed authority/publication bytes are
required; the original 80 freshness negatives remain. Two initial candidate tests
accidentally made the corrupted STOP-derived fields valid by adding a STOP; using
an unchanged observation in the later hour fixes that fixture collision. The
80-case no-op mutation now fails every new negative without modifying source.

R8 uses portable descriptor device/inode observations while actively denying
`/proc`, and guards the three actual Linux-dependent tick cases. Two synthetic
`darwin`/`win32` controls require refusal before `Popen` and retained blocked intent.
Linux durability/tree coverage remains exercised. No actual macOS rerun or reader
backend has been qualified by this slice.

The full main A-slice run was launched before slice B's new module; its subsequent
completion notification reports 493 passes/three skips. It does not cover the
later execution implementation. Initial wrappers
using system Python failed before tests because of its unsupported `text=` option;
the main interpreter fixes that harness issue. Initial full-suite runs also failed
before tests because bare `tests` was not absolutized; corrected runs were launched.
Neither harness failure is a behavior regression. No endpoint access, deployment,
commit or push occurred. dcc-02–05 remain open.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/coordinator.py §tick; ../Wintap-PyUtil/tests/test_coordination_tick.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_entity_integrity.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py -->

### Completion slice B — execution baseline

The new entirely local `tests/test_coordination_execution.py` was run before any
execution/writer implementation: **23 failed in 0.34 s**, all missing-module/API
failures. Report: `/tmp/opencode/dcc-execution-missing-api-red.txt`. This is an
implementation baseline, not active-path hardening evidence. The first implementation
passes 22/23 initial cases; the real-empty fixture needed an existing compacted
destination for the CLI's read-only migration check. That fixture is corrected,
not treated as a receipt defect. Further active-path probes record five failures
before budget-ceiling/archive-separation, lost-COMMIT-ack blocking and secret-bearing
exception repairs; three injected remote-resolution controls pass. Report:
`/tmp/opencode/dcc-execution-hardening-red.txt` (23 deselected). Post-repair and
broader launch/configuration/secret-exclusion results are recorded below; macOS is open.

| Report under `/tmp/opencode/` | Selection / result |
|---|---|
| `dcc-execution-initial.txt` | 22 passed, one failed: missing compacted root in real-empty fixture; corrected separately from behavioral defects |
| `dcc-execution-hardening-red.txt` | 5 active-path failures, 3 injected SDK passes, 23 deselected: memory/spill ceilings, archive/ledger overlap, lost COMMIT acknowledgment and secret-bearing exception |
| `dcc-execution-file-arg-red.txt` | 3 active-path failures: FIFO/hardlink receipt refusal before read and compiled argument budget before publication |
| `dcc-execution-expanded-green.txt` | 37 passed, 22.73 s after eight hardening repairs |
| `dcc-execution-coordination-green.txt` | 194 passed, 51.80 s: execution, protocol, ledger, tick and supervisor modules (44 receipt/launch cases) |

The final focus includes real local empty and one-row synthetic migration/source
deletion with original phase records retained. Both leave `BLOCKED` and retain the
cursor. Tests cover strict matching-checksum malformed receipts, run/root/command/
runtime identity, argument/capture/time/storage budgets, nonregular files and
pre/post-intent changes. Injected SDK/default/environment/profile resolution freezes
the selected endpoint/region and credentials before later environment changes;
synthetic secret values and their hashes are absent from receipts/intents/audits,
and credential repr is excluded. No actual endpoint request occurs.

Receipt preparation fixes this checkout's standalone `-I -B` CLI and public code/
native-engine identity, explicit active scope and inactive entity/S3 fields. Remote
extension-cache default is `<state>/extensions`; spill and retained phase archive
are separate from ledger/runtime/data roots. Individual 32 GB memory/64 GB spill
ceilings are not aggregate RSS/disk or representative sizing qualification.
Lost intent-COMMIT acknowledgment cannot launch and blocks in the same session.
Secret-bearing provider/launch exceptions are sanitized, not retained as diagnostics.

Scoped Ruff lint and format checks pass eight changed/new Python files; both
repositories' `git diff --check` pass. The full-main receipt-revision run completes:
`dcc-run-tests.py main /tmp/opencode/dcc-execution-full-main.txt tests` reports
**537 passed, 3 skipped in 683.54 s**. Tested runtime sources remained unchanged
until its completion notification. Completion-side high-water/history,
service/client/audited recovery, actual macOS/S3 and resource gates remain open.
No production scheduler, endpoint operation, fixture cleanup, commit or push.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/execution.py; ../Wintap-PyUtil/wintappy/coordination/writer.py; ../Wintap-PyUtil/tests/test_coordination_execution.py -->

### Completion slice C — separate verification, ledger integration pending

All commands below use the disposable-CWD `dcc-run-tests.py` harness described
above, with explicit main/standalone environments, no checkout cache writes and
qualification-owned synthetic local fixtures. Reports remain under `/tmp/opencode/`;
no actual endpoint access or production scheduling occurs.

| Report | Selection / result |
|---|---|
| `dcc-completion-verifier-missing-api-red.txt` | 33 missing standalone API failures before implementation |
| `dcc-completion-prototype-initial.txt` | 9 failed, 24 passed from an injected scratch prototype; not active-path implementation evidence |
| `dcc-completion-verifier-initial.txt` | 33 passed, 14.64 s after promotion into the real module |
| `dcc-completion-archive-hardening-red.txt` | 2 active-path failures: FIFO and hardlinked archive records read before refusal |
| `dcc-verification-missing-api-red.txt` | 9 missing main adapter API failures |
| `dcc-completion-types-hardening-red.txt` | 3 active-path failures: terminal boolean, validation integer and boolean row counts |
| `dcc-verification-live-intent-red.txt` | 1 active-path failure: failed verification left committed intent `WRITING` |
| `dcc-authority-baseline-recheck-red.txt` | 1 active-path failure: stale initialization-candidate snapshot accepted |
| `dcc-verifier-request-red.txt` | 1 active-path argument-parser failure, 3 refusal controls passed |
| `dcc-completion-final-focus.txt` | **259 passed, 118.44 s**: completion (44 cases), phase archive and SQL integrity modules |
| `dcc-verification-final-focus.txt` | **204 passed, 87.56 s**: verification (10 cases), execution, ledger, protocol, tick and supervisor modules |

The eight active-path failures precede repairs. Positive valid-before-corruption
controls distinguish evidence rejection from a broken success fixture. Archive
reads now require bounded single-link regular files before opening. Exact JSON
types reject boolean/integer substitutions. Request parsing refuses checksum,
shape, argument and byte-budget violations without echoing synthetic sensitive
values. Initialization evidence rechecks current snapshots; failed verification
blocks a matching live intent without moving the cursor.

Standalone `completion.verify_completion` independently reopens original archive
and surviving data: exact run/hour/root/event scope, chain/order, original migration
and deletion evidence, hashes/counts/schemas, source absence and complete bounded
empty-hour discovery. Entity-mode local controls verify current SQL state/authority,
original bootstraps, retained exact ordinal/ID anchors and original historical
checkpoint candidates. Forward evolution is permitted without comparing historical
hashes to today's aggregate; rollback/forks/pending state/corruption refuse.
`verify_authority` returns rechecked candidate evidence only.

Main `verification.verify_prepared` authenticates committed receipt/intent and
writer shutdown/captures, publishes an immutable request and separately supervises
the standalone read-only verifier, authenticating its shutdown/captures too. It
rechecks receipt/runtime/request/intent and original observations after verification.
**Success confers no completion permission.** At this foundation revision, entity
mode explicitly refuses until
independently initialized ledger high-water authority is integrated; caller-supplied
anchors do not bypass this main-runtime gate. Ledger remains v1 with one unresolved
run, no retained completed history and no completion/cursor/reopening API.

Fresh scoped Ruff 0.17.5 lint and formatting pass all 13 changed/new Python files.
The full standalone verifier revision completes with **431 passed, 2 skipped in
172.52 s** (`dcc-completion-full-standalone.txt`); full main completes with
**547 passed, 3 skipped in 695.09 s** (`dcc-completion-full-main.txt`). Runtime sources
remained frozen until both notifications arrived. These results precede and do not
cover the subsequent ledger-v2 authority work below. Atomic history/completion integration,
actual macOS reader shutdown, service/client/recovery, actual S3 and representative
32 GB RAM / 64 GB disk qualification remain open; dcc-02–05 stay unchecked.

Post-cleanup artifact/privacy audit passes **10 changed wiki files, 8 frontmatters,
179 grounded paths, 191 inline sources, 377 links and 7 diagram pages**. Existing
index/log frontmatter omissions remain baseline exceptions, not a whole-wiki lint
pass. Both repositories' whitespace checks pass. Complete new source/test files
and tracked runtime diffs were reviewed; unrelated data/environment/settings stay
excluded. No new commit or push is made.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/phase_evidence.py §read_local_record/load_archive; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_completion_verifier.py; ../Wintap-PyUtil/wintappy/coordination/verification.py; ../Wintap-PyUtil/tests/test_coordination_verification.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py -->

### Ledger integration baseline — high-water prerequisites fail before repair

Before changing runtime sources, the disposable-CWD main harness runs
`dcc-run-tests.py main /tmp/opencode/dcc-high-water-baseline-red.txt
/tmp/opencode/dcc-high-water-baseline-tests.py`: **2 failed in 1.19 s**. These scratch
tests call the real ledger with synthetic entity-enabled local bindings. A queued
reader receives a reservation without an independently initialized authority
baseline, and direct `begin_writer` also succeeds without that prerequisite. No
writer subprocess, production dataset or endpoint is involved. The negatives were
subsequently promoted into `tests/test_coordination_authority.py`; their recorded
pre-repair failures and latest passes are attributed below.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §initialize/admit/begin_writer -->

### Completion slice C — ledger-v2 authority integration

The earlier verifier-foundation full passes are **547 main / 431 standalone**, not
authority-revision regression results. All following runs use the same disposable-CWD
harness and synthetic local fixtures; no endpoint request or production operation.

| Report | Result / attribution |
|---|---|
| `dcc-authority-ledger-api-red.txt` | **4 failed, 1.73 s**: two active entity admission/intent prerequisite failures plus two missing upgrade-interface failures |
| `dcc-authority-adapter-missing-api-red.txt` | **6 failed, 4 passed, 2.15 s** before the supervised initialization API existed |
| `dcc-authority-observation-hardening-red.txt` | **3 active failures, 13.63 s**: rehashed command digest, captured result and observations path accepted before authentication repairs |
| `dcc-entity-adapter-integration-red.txt` | **1 expected active integration-gate failure**: real local entity writer passes, but the main adapter still unconditionally refused entity verification |
| `dcc-authority-upgrade-invalid-red.txt` | **1 active diagnostic failure, 3 passed, 1.82 s**: corrupt source exposed a raw DuckDB exception; repair returns sanitized `CoordinationError` without replacement |
| `dcc-authority-upgrade-crash-green-2.txt` | **12 passed, 18 deselected, 20.38 s**: upgrade/abrupt-death controls |
| `dcc-authority-request-green-2.txt` | **8 passed, 44 deselected, 2.15 s**: strict bound authority requests, sensitive-input refusal and changed-request detection |
| `dcc-authority-final-main-green.txt` | **236 passed, 204.99 s**: authority, ledger, execution, verification, tick, protocol and supervisor modules |
| `dcc-authority-final-standalone-green-2.txt` | **299 passed, 139.30 s**: completion, entity freshness/integrity and phase archive modules |
| `dcc-authority-fork-history-final-green.txt` | **2 passed, 30 deselected, 22.58 s** after test-only inline-command cleanup |

Latest main and standalone focus commands:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-authority-final-main-green.txt \
  tests/test_coordination_authority.py tests/test_coordination_ledger.py \
  tests/test_coordination_execution.py tests/test_coordination_verification.py \
  tests/test_coordination_tick.py tests/test_coordination_protocol.py \
  tests/test_coordination_supervisor.py
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py standalone \
  /tmp/opencode/dcc-authority-final-standalone-green-2.txt \
  tests/test_completion_verifier.py tests/test_entity_freshness.py \
  tests/test_entity_integrity.py tests/test_phase_evidence.py
```

Ledger schema v2 adds canonical predecessor-linked `authority_checks`; explicit
confirmed `Ledger.upgrade` preserves ledger/dataset identity, cursor, reservations,
outbox, tombstones, existing audits and writer identities. The schema transaction
is atomic; unresolved-writer blocking may commit before it. Old intents stay blocked
and gain no manufactured execution/completion evidence. Missing/corrupt/mismatched
sources refuse replacement; ordinary open never upgrades or silently initializes.

`verify_authority_prepared` separately supervises a read-only standalone
`--authority-only` version-2 request bound to execution, ledger/dataset identities
and prior anchor. Initialization requires explicit confirmation/reason, no prior
baseline and zero readers in `OPEN`/`DRAINING`. Command/manifest, path, captured bytes,
shutdown, receipt/runtime, request and current evidence are authenticated/rechecked
before proof/audit retention in one transaction. The standalone never opens the
ledger; its candidate alone cannot initialize or authorize admission.

Entity admission and writer intent require the initialized exact generation plus
a fresh check in the same locked session. Reopen resets freshness, failed checks
clear it and successful intent consumes it. Existing reservations are retained.
Forward evolution passes; whole-journal/snapshot rollback with a retained ledger
and a same-ordinal fork valid in isolation refuse without rebasing. The main entity
`verify_prepared` now verifies real local entity migration/deletion and its original
historical checkpoint, leaving high-water/cursor/permissions unchanged. That candidate
still needs the atomic completion transaction.

Authority history is bounded at **64 KiB/check / 10,000 checks**, entirely validated
in **256-row batches**; corruption or exhaustion refuses, never truncates. The
257-row control synthetically extends authenticated repeat-check metadata and
corrupts the final row; it proves validation beyond the first batch, not 257 actual
verifier runs, retained-state sizing or manufactured authority/data/recovery evidence.
Abrupt death and lost acknowledgments around authority/upgrade COMMIT preserve
old/new atomic schema or retained anchor without fresh admission/relaunch permission.

Harness/fixture failures are retained separately: `dcc-authority-final-focus.txt`
records 225 passes/one fixture failure from an extra `make_release` argument;
initial crash fixtures treated `load_execution`'s receipt dictionary as a
`PreparedExecution`, request fixtures omitted required arguments/event selection,
and the initial fork fixture re-created an existing directory. Corrections change
fixtures, not behavior. `dcc-authority-final-standalone-green.txt` selected nonexistent
standalone paths (no tests, exit 4); the corrected 299-pass selection is above.

Latest scoped Ruff **0.17.5** lint and format checks pass six authority/verification
source/test files. Full authority standalone completes with **439 passed, 2 skipped
in 173.60 s** (`dcc-authority-full-standalone.txt`). Full main completes with
**579 passed, 3 skipped in 791.61 s** (`dcc-authority-full-main.txt`):

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-authority-full-main.txt tests
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py standalone \
  /tmp/opencode/dcc-authority-full-standalone.txt tests
```

Runtime sources/tests remained frozen until both automatic completion notifications.
The freeze is now lifted for the next completion/history slice; the full passes
above qualify only the earlier authority revision.
Ledger v2 still retains only one unresolved writer record: completed-run history,
atomic completion-evidence/run/high-water/exact-hour-cursor/backlog-mode COMMIT,
fresh clock/admission integration and audited recovery remain absent. Actual macOS
reader shutdown, exact isolated S3 access/roots and representative 32 GB RAM / 64 GB
disk qualification are open. Whole-ledger-plus-authority rollback freshness and
physical power-loss behavior are not established by these tests. dcc-02–05 remain
unchecked; no production operation, new commit or push occurred.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/ledger.py §upgrade/_validate_authority_checks/_require_entity_authority; ../Wintap-PyUtil/wintappy/coordination/authority.py; ../Wintap-PyUtil/wintappy/coordination/verification.py §verify_authority_prepared/verify_prepared; ../Wintap-PyUtil/tests/test_coordination_authority.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/completion.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_completion_verifier.py -->

**Post-synchronization source/artifact review:** fresh tracked runtime diffs and
feature-owned new source/test files are reviewed without modifying the frozen
runtime. The complete wiki diff is inspected for unauthorized host/account/IP values;
none are added. `../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-check-wiki.py`
passes **10 changed wiki files, 8 frontmatters, 195 grounded paths, 214 inline sources,
379 links and 7 diagram pages**. Index/log frontmatter omissions remain preserved
baseline exceptions, not a whole-wiki lint pass. Both repositories' `git diff --check`
pass. Pinned Ruff **0.17.5** `check` and `format --check`, run through
`uv tool run --cache-dir /tmp/opencode/dcc-ruff-cache --from ruff==0.17.5`, pass all
**15 changed/new feature Python files** (six main coordination sources, four main
test modules, two standalone sources and three standalone test modules).

The continuation plan now explicitly preserves the current launch API's conservative
blocking behavior. Normal success must obtain fresh independent verification inside
a new uninterrupted same-lock live-intent path; previously blocked/restart-blocked
runs remain behind explicit audited recovery. No parsed or caller-supplied report
may clear uncertainty. This is a documented implementation boundary, not a new
success API or runtime test. Full main was still pending during that review; no
polling, source/test changes, endpoint operation, deployment, commit or push occurred.

### Completion slice C — initial ledger-v3 history and atomic completion

The authority full regressions above completed before these edits. Ten formal
completion controls first produced **10 missing-API failures in 11.33 s** in
`dcc-completion-ledger-api-red.txt`; all are missing-entrypoint ImportErrors, not
active behavioral hardening evidence. The first implementation adds schema v3,
retained predecessor-linked completion proofs and an uninterrupted same-lock
writer→fresh independent verifier→completion transaction path. Existing
`execute_prepared` remains conservative; blocked/restarted intents cannot use the
new normal-success entrypoint.

The initial five-file syntax checks pass after import/unused-variable cleanup and
formatting. `dcc-completion-initial.txt` records **10 passed in 66.90 s**:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-initial.txt tests/test_coordination_completion.py
```

This initial focus covers real local empty completion, two sequential hours,
retained prior evidence, verification crossing grace, old/restarted blocking,
before/after-COMMIT lost acknowledgments and archive/shutdown/clock uncertainty.
It is not final completion acceptance. Existing ledger/authority/execution/verifier
regressions and additional real entity, abrupt-death, rehashed/missing-history and
budget controls are running against the prototype; no outcomes are inferred before
notifications. Schema v1/v2 compatibility, complete history validation and atomic
entity high-water advancement still need their resulting evidence. Full regressions,
service/client, audited recovery, actual macOS/S3 and resource gates remain open.
No endpoint operation, production scheduling, cleanup, commit or push.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_complete_writer/_validate_completion_history/upgrade; ../Wintap-PyUtil/wintappy/coordination/writer.py §execute_and_complete_prepared; ../Wintap-PyUtil/tests/test_coordination_completion.py -->

The first existing-regression and additional-hardening invocations hit the harness's
**120-second shell timeout**, with no completed runner report or retained test
outcome. These are incomplete harness runs, not passes or behavioral failures.
Both selections were relaunched with no outer shell timeout (the disposable runner
retains its 1,200-second subprocess ceiling). Runtime sources remained unchanged
until both resulting notifications.

Recorded implementation/hardening results before repairs:

| Report under `/tmp/opencode/` | Result and attribution |
|---|---|
| `dcc-completion-regressions-initial.txt` | **126 passed, 1 failed in 178.98 s**; the only failure is a historical upgrade test expecting target v2 instead of v3, not a failed atomic upgrade. Its identity/schema all-or-none assertions are preserved with the current explicit target and both authority/completion-table checks. |
| `dcc-completion-hardening-red.txt` | **13 passed, 3 failed, 10 deselected in 135.90 s**; active failures accept inactive checkpoint values, erase completion evidence/run/cursor while leaving its audit, and accept removed fresh authority captures. Real local entity advancement, budget refusals and abrupt raw completion-death controls pass. |
| `dcc-completion-hardening-red-2.txt` | **4 failed, 26 deselected in 28.64 s**; active failures accept removed completion audits, joint origin/cursor rebasing, same-session prior-history corruption and original archive removal after verifier return. |

All **seven active failures** are retained before source repairs. The repaired
prototype makes inactive checkpoint fields explicitly null; ties origin, proofs,
completed runs, audits and cursor together; validates prior history again before
completion; and rechecks fresh authority captures/requests plus the bounded original
JSON archive chain before COMMIT. Main archive rechecks inspect byte identities
only, never compactor SQL/data in the main runtime. All actual data verification
remains in the separately supervised standalone DuckDB 2.0.0 runtime.

The origin audit commits with explicit initialization/compatible v1/v2 upgrade,
retaining the original ledger ID, old permissions and proof bytes. It is local
integrity evidence, not protection against coherent whole-ledger-plus-store rollback.
Completion proofs remain capped at **128 KiB/proof / 10,000 completed runs**, with
256-row history pages; authority ceilings remain **64 KiB/check / 10,000 checks**.
No history is pruned. Added genuine entity before/after-completion-COMMIT and
external-success-before-COMMIT death controls, v2 compatibility with genuine authority
proof bytes, audit-independent retained-proof semantic negatives, synthetic-secret
exclusion and three real hours through instrumented two-row pages. The latter tests
multiple pages without manufacturing completions; it is not a 257-real-run or
representative retained-state sizing qualification.

Those repaired runs subsequently complete:

| Report under `/tmp/opencode/` | Result and revision scope |
|---|---|
| `dcc-completion-hardening-green.txt` | **46 passed, 21 deselected in 287.77 s**: completion/history/entity/crash controls and compatible-upgrade focus, before the final budget/clock repair. |
| `dcc-completion-controls-initial.txt` | **24 passed in 44.96 s**: independent retained-proof semantics, genuine-proof v2 compatibility, three-real-hour paging and synthetic-secret controls, before the final budget/clock repair. |
| `dcc-completion-budget-clock-red.txt` | **3 active failures, 24 deselected in 20.91 s**: consistently rebound stdout/stderr capture metadata can exceed the effective receipt ceiling; a later invocation can predate the prior completion and reopen backlog. |
| `dcc-completion-budget-clock-green.txt` | **3 passed, 24 deselected in 16.58 s** after effective capture/report ceiling checks and retained prior-completion clock-floor enforcement. |

These bring completion hardening to **ten recorded active failures before repairs**,
separate from the ten initial missing-API failures and the stale target assertion.
The final clock repair compares a new normal-success invocation to the prior
retained completion before intent/launch, and validates monotonic completed-history
start times. This is not a persistent global clock attestation or coherent rollback
freshness guarantee. Receipt-bound stream/report limits also apply when validating
retained proofs, independently of audit/hash rejection.

Repaired-focus and final-target commands:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-hardening-green.txt \
  tests/test_coordination_completion.py tests/test_coordination_authority.py \
  -k 'completion or history_origin or same_session_history or original_archive_removed or upgrade'
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-controls-initial.txt tests/test_coordination_completion_controls.py
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-budget-clock-red.txt \
  tests/test_coordination_completion_controls.py -k 'retained_writer_capture or clock_before_prior'
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-budget-clock-green.txt \
  tests/test_coordination_completion_controls.py -k 'retained_writer_capture or clock_before_prior'
```

Final combined main coordination focus and full standalone regression were launched
against the frozen budget/clock revision. Full standalone subsequently passes
**439 tests, two skips in 170.76 s**. Combined main focus then completes with
**298 passed in 517.39 s**; its completed report is inspected before full main launch:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-final-main-focus.txt \
  tests/test_coordination_authority.py tests/test_coordination_completion.py \
  tests/test_coordination_completion_controls.py tests/test_coordination_ledger.py \
  tests/test_coordination_execution.py tests/test_coordination_verification.py \
  tests/test_coordination_tick.py tests/test_coordination_protocol.py tests/test_coordination_supervisor.py
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py standalone \
  /tmp/opencode/dcc-completion-full-standalone.txt tests
```

Full main was launched against the unchanged revision and subsequently completes
with **641 passed, 3 skipped in 1055.19 s**. Its completed report and automatic
notification are inspected; source/runtime-lock identities still match the prepared
manifest. Together with 439 standalone passes/two skips, this closes the local v3
full-regression gate, not dcc-02–05:

```sh
../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-completion-v3-full-main.txt tests
```

No outer shell timeout is used; the disposable-CWD runner retains its 1,200-second
subprocess ceiling. Runtime sources/tests remained frozen until both full automatic
notifications, without polling; the freeze is now lifted for the next dependency
slice. Result-only synchronization passes the complete documentation/privacy
inspection; the scoped audit again passes 11 wiki files,
9 frontmatters, 211 grounding paths, 243 inline sources, 387 links and 7 diagram pages.
Both whitespace checks pass. Pinned Ruff **0.17.5** lint/format results cover all
18 unchanged feature Python files after the final budget/clock repairs. Complete
tracked/new feature-source review and full wiki-diff privacy inspection are completed;
stale source-map/design statements about the absent local success API are corrected.
Unrelated data/environment/settings remain excluded and untouched.
Before the Mac runbook addition, the refreshed read-only scoped audit command
`../Wintap-PyUtil/.venv/bin/python -B /tmp/opencode/dcc-check-wiki.py` passed
**10 changed wiki files, 8 frontmatters, 204 grounding paths, 238 inline sources,
381 wikilinks and 7 diagram pages**. Index/log frontmatter omissions remain
preserved baseline exceptions, not a whole-wiki lint pass. The complete 1,787-line
pre-synchronization wiki diff and subsequent documentation edits are inspected;
no actual host/account/IP identifiers are added. Ruff `check` and `format --check`
run through the pinned command above over seven main coordination sources, six
main coordination test files, two standalone sources and three standalone test
files. Both commands pass all 18 files; neither reformats the frozen revision.
dcc-02–05, service/client/audited recovery and actual
macOS/S3/representative-resource gates stay open. No endpoint operation, production
scheduling, cleanup, commit or push.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/completion.py §validate_completion_proof/_recheck_archive/_complete_live_prepared; ../Wintap-PyUtil/wintappy/coordination/ledger.py §_validate_completion_history/_complete_writer/upgrade; ../Wintap-PyUtil/tests/test_coordination_completion.py; ../Wintap-PyUtil/tests/test_coordination_completion_controls.py; ../Wintap-PyUtil/tests/test_coordination_authority.py -->

### Human-run macOS baseline prepared — execution remains pending

The human selected an actual-Mac human-run harness. Instructions and the later
reader-backend acceptance boundary are in
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. Prepared scratch
artifacts are `dcc-macos-baseline.py`, `dcc-macos-source-manifest.json` and
`dcc-macos-baseline-bundle.tar.gz` under `/tmp/opencode/`. The bundle contains only
the 18 feature Python files, coordination README, harness and source manifest;
no data, credential files, virtual environments or unrelated settings are copied.
Tar owner/group metadata is neutralized. The manifest checks the exact baseline
commit and public source/runtime lock files, not secrets or environment hashes.

Harness syntax, all bundle member identities/neutral metadata and an actual Linux
refusal-before-output/pytest control pass. Pinned Ruff **0.17.5** lint/format passes
the separate scratch harness after initial style cleanup. This is harness preparation
and a non-Mac refusal control, **not actual macOS execution, qualified reader shutdown
or representative resource evidence**. Current Linux-only test skips remain explicit.
No runtime source/test file changes occurred during harness preparation or the Linux
full-main freeze. Full main subsequently passes 641 tests/three skips on the unchanged
revision; the freeze is lifted. Human transfer/execution is next;
the future macOS backend remains required before broad reader integration.
The final scoped audit includes the new untracked runbook and passes **11 wiki
files, 9 frontmatters, 211 grounding paths, 243 inline sources, 387 wikilinks and
7 diagram pages**. Complete new runbook/subsequent edits and both whitespace
checks pass; preserved index/log exceptions are not whole-wiki acceptance.

### Committed Mac handoff — dcc-mac-baseline-01 pending

The human authorized feature-only commits and will run the Mac tests on another
system. PyUtil commit `8ee714c0c58e9781a29b0cdc488e3aaf6ebea181` contains 19 prior
feature files plus the durable harness, source manifest and separate harness test
script (22 files total). Unrelated data/environment/settings/venvs are excluded;
no push occurred. The runbook now names this exact commit instead of the obsolete
`fe7fcb5` plus uncommitted-overlay workflow.

The manifest retains all 22 prior public identities: 18 feature Python files and
four runtime/lock files. Its version-two envelope names the reviewed parent and
accepts the explicit full qualification commit; SHA-256:
`c37247ac1962cb6a259e5387d1c9177a37f82a5ff78f913382b293770d2bf3b7`.
No runtime source/test or lockfile bytes changed while making the harness durable.
The 641-main/439-standalone full results above remain runtime evidence, not new
harness results or actual-Mac evidence.

From PyUtil:

```sh
TMPDIR=/tmp/opencode .venv/bin/python -B scripts/test_dcc_macos_baseline.py
```

Result: **15 local harness controls pass**. They cover exact commit versus obsolete
parent, clean tracked state, ancestry, source missing/change/symlink/path rejection,
obsolete manifest, non-Mac refusal, retained failure/skip counts, isolated synthetic
credential exclusion/private sanitized summary, timeout stop and missing interpreter
evidence. Simulated platform/subprocess unit controls are explicitly not Mac runs.
Durable script syntax and an actual Linux CLI refusal before testing/output pass.
Pinned Ruff **0.17.5** `check` and `format --check` pass all 20 Python files (the
unchanged 18 feature files plus two harness scripts). Staged allowlist/exact-byte
inspection and `git diff --cached --check` pass; all 22 original manifest hashes
still match. The identity-only `validate_checkout` check also passes against actual
committed HEAD `8ee714c` after commit; no platform tests run in that check.

Final scoped wiki artifact/privacy audit passes **11 changed files, 9 frontmatters,
217 grounding paths, 250 inline sources, 391 wikilinks and 7 diagram pages**;
index/log frontmatter omissions remain baseline exceptions. Whitespace checks
pass. Complete new runbook and feature diff inspection preserves the privacy rule.

Next task and exact Mac commands:
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. Actual Mac baseline,
reader backend/shutdown, service/client/audited recovery and S3/representative
resources remain unqualified; dcc-02–05 stay unchecked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_baseline.py; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py -->

### Mac packaging correction — original blocked result retained

The Mac worker reports that **dcc-mac-baseline-01 at PyUtil
`8ee714c0c58e9781a29b0cdc488e3aaf6ebea181` was blocked before either test stage ran**:
the clean checkout did not contain main `uv.lock`. Preserve the original private
blocked record; no main/standalone test counts or Mac pass are inferred.
<!-- SOURCE: Mac worker blocked-result report and human-authorized correction, conversation 2026-11-14. -->

Independent `git ls-tree -r --name-only 8ee714c0c58e9781a29b0cdc488e3aaf6ebea181`
inspection confirms 21 of 22 manifest files, with only main `uv.lock` missing.
The prior post-commit `validate_checkout` pass above checked local hashes, not
committed coverage: an ignored matching lockfile concealed the omission. That
historical check remains recorded with this explicit limitation; it was not
fresh-checkout proof. The standalone lock was already committed.

The human authorized a corrective follow-up, committed as PyUtil
`fab647f900196b0bc473fe7977b7dadcf7f4ce52`. Exactly five files changed:
`.gitignore`, main `uv.lock`, the two harness scripts and coordination README.
The lock is the original **593,615 bytes**, SHA-256
`61912ee3abb9e095b46e03fba4a021272d77bed9f1235a8901e92a92a5d9d367`;
it was not regenerated. Complete structured review of local and staged bytes
covers 191 packages and 1,940 public HTTPS registry/artifact URLs, with only
checkout-relative local project paths. The root-only ignore exception leaves
unrelated local lockfiles ignored. No runtime code, feature test or manifest hash
changed; all 22 original identities and the manifest SHA-256 above are retained.

The validator additionally uses `git cat-file blob <full-commit>:<manifest-path>`
to require each committed file's bytes to match its manifest hash. Local matching
files no longer conceal missing or different committed content. Three controls
were recorded before the guard: missing committed file, different committed bytes,
and a real synthetic clean Git repository with an ignored matching lockfile.
From PyUtil, before/after implementation respectively:

```sh
TMPDIR=/tmp/opencode .venv/bin/python -B scripts/test_dcc_macos_baseline.py > /tmp/opencode/dcc-lockfile-commit-coverage-red.txt 2>&1
TMPDIR=/tmp/opencode .venv/bin/python -B scripts/test_dcc_macos_baseline.py > /tmp/opencode/dcc-lockfile-commit-coverage-green.txt 2>&1
```

Inspected red result: **18 tests, exactly the three new failures, zero errors**;
the other 15 controls pass. Final green result: **18 pass in 0.213 s**. Initial
format-only cleanup is separate from the three behavioral red/green controls.
Pinned Ruff **0.17.5** `check --no-cache` and `format --check --no-cache` both pass
all 20 Python files: the unchanged 18 manifest Python files and two harness scripts,
using `uv tool run --cache-dir /tmp/opencode/dcc-ruff-cache --from ruff==0.17.5 ruff`.
Both harness scripts compile; an actual Linux CLI invocation exits 2 before output
or platform test access. Staged five-file allowlist, exact index/local identities,
structured lock review and `git diff --cached --check` pass before commit.

After committing, a new disposable clone was populated only from Git using
`git clone --quiet --no-local --no-hardlinks --no-checkout <local-repo> <new-checkout>`
and `git checkout --quiet --detach fab647f900196b0bc473fe7977b7dadcf7f4ce52`.
No ignored files, credentials, datasets or virtual environments were copied from
the working tree. In that clean clone, all **22 local file and committed blob
hashes** plus the unchanged manifest hash pass, and the updated identity-only
`validate_checkout` returns the full corrective commit. All **18 harness controls
pass again in 0.196 s**, using the existing external main interpreter without
provisioning environments in the clone. Git status remains empty. Inspected report:
`/tmp/opencode/dcc-lockfile-fresh-git-checkout.txt`. Neither actual-Mac test stage ran.

The complete six-file wiki diff is inspected for persistent-content privacy.
`git diff --check` and the scoped read-only artifact/privacy audit pass:
**6 files, 4 frontmatters, 115 grounding paths, 129 inline sources, 352 wikilinks
and 2 diagram pages**. Index/log frontmatter omissions remain baseline exceptions,
not whole-wiki lint acceptance.

Corrected full-revision commands and continuation prompt:
[[wiki/work/dbt-compaction-coordination/macos-qualification]]. The Mac worker must
use a fresh checkout and a **new private report directory**, preserving the original
blocked result. Existing 641-main/439-standalone Linux results retain their original
unchanged-runtime scope; they are not corrective Mac qualification. Mac baseline/
reader shutdown, service/client/audited recovery, actual-S3/representative-resource
gates and dcc-02–05 remain open. No push, remote access, production mutation,
scheduler installation or unrelated-artifact cleanup occurred.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/.gitignore; ../Wintap-PyUtil/uv.lock; ../Wintap-PyUtil/scripts/dcc_macos_baseline.py §validate_checkout; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py -->

### Maintainer completion review — Mac provisioning blocked

Human requested the latest pull, source review and actual Mac tests. Utility planning
was committed and rebased as Analytics `94a6688` over pulled `deae3a3`; PyUtil's
fast-forward pull was already current at
`8ee714c0c58e9781a29b0cdc488e3aaf6ebea181`. No assistant push or source repair.

Created a clean detached disposable worktree at that exact PyUtil revision. Actual
platform: **macOS 26.7.1, arm64**; uv **0.11.26**. Applied the committed runbook:

```sh
uv sync --locked --dev --python 3.12
uv sync --locked --dev --python 3.12 --project extras/raw-sensor-compact
git ls-tree -r --name-only 8ee714c0c58e9781a29b0cdc488e3aaf6ebea181 uv.lock extras/raw-sensor-compact/uv.lock
git check-ignore -v uv.lock
```

- Main provisioning: **exit 2**, `Unable to find lockfile at uv.lock, but --locked
  was provided`. Python 3.12.12 was selected and an empty main environment created;
  dependencies were not installed. It is not a usable test runtime.
- The independent standalone provisioning command succeeded (**exit 0**), reporting
  Python **3.12.12**, DuckDB **2.0.0**, pytest **9.2.0**. These are provisioner-reported
  versions, not completed import/version gates or test results.
- Git tree check finds only `extras/raw-sensor-compact/uv.lock`; root `uv.lock` is
  excluded by `.gitignore`. The original checkout's ignored lock exists but does not
  match the reviewed manifest, so it was not copied or used.
- Direct standard-library `validate_checkout` check of the disposable checkout fails
  with `Required feature source is missing or aliased`. Exact HEAD, reviewed ancestry
  and clean tracked state pass; **21/22** named manifest files are present and match.
  The manifest SHA-256 is unchanged:
  `c37247ac1962cb6a259e5387d1c9177a37f82a5ff78f913382b293770d2bf3b7`.

**Original dcc-mac-baseline-01 attempt: BLOCKED before tests.** No main/standalone pytest stage, runtime
import/version check or committed harness execution followed the provisioning
failure. No harness `summary.json` exists; private `provisioning-review.json` records
the original command outcomes and separate source checks without fabricating test
counts. No lockfiles/manifests were changed and no substitute runtime was used.

The corrected run is recorded separately below; this original failure remains intact.

The source review covers R6–R8 controls, effective execution receipts, separate
verification, retained authority and v3 history/atomic completion. Findings and
worker repair request: [[wiki/work/dbt-compaction-coordination/implementation-review#Completion phase review — 2026-11-14]].
Worker-reported Linux **641/439 full-suite passes** and **298 focus passes** are not
fresh Mac evidence. dcc-02–05, service/client/advisory exports/audited recovery,
supported Mac reader shutdown, actual-S3 and representative-resource gates remain
open. The utility remains planning only; its previous 27-test result is unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/.gitignore; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/dcc_macos_baseline.py §validate_checkout; wiki/work/dbt-compaction-coordination/macos-qualification.md §Stage 1 -->

### Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed

Human selected the newly committed worker repair rather than a substitute-runtime
diagnostic run. Pulled PyUtil `8ee714c` →
`fab647f900196b0bc473fe7977b7dadcf7f4ce52` and Analytics `deae3a3` → `6459c74`;
rebased authorized utility planning as `1051a8c`. Preserved worker documentation,
planning and the original maintainer provisioning evidence through rebase/stash
resolution. No new review commit or assistant push.

A **new clean detached disposable checkout** uses only the repaired committed
sources and newly provisioned native environments. Actual platform: **macOS 26.7.1,
arm64**, uv **0.11.26**. The root lock has the exact previously reviewed SHA-256
`61912ee3abb9e095b46e03fba4a021272d77bed9f1235a8901e92a92a5d9d367`;
the public manifest SHA-256 remains
`c37247ac1962cb6a259e5387d1c9177a37f82a5ff78f913382b293770d2bf3b7`.
All **22 manifest files** pass local and committed-Git-blob identity checks before
and after testing. No source/test/lock/manifest bytes were altered for the run.

Commands from the repaired checkout:

```sh
uv sync --locked --dev --python 3.12
uv sync --locked --dev --python 3.12 --project extras/raw-sensor-compact
.venv/bin/python -B -c 'import sys, duckdb, pytest; print("main", sys.version.split()[0], duckdb.__version__, "pytest", pytest.__version__); assert duckdb.__version__ == "1.5.6"'
extras/raw-sensor-compact/.venv/bin/python -B -c 'import sys, duckdb, pytest; print("standalone", sys.version.split()[0], duckdb.__version__, "pytest", pytest.__version__); assert duckdb.__version__ == "2.0.0"'
.venv/bin/python -B scripts/dcc_macos_baseline.py \
  --root . --manifest scripts/dcc_macos_source_manifest.json \
  --commit fab647f900196b0bc473fe7977b7dadcf7f4ce52 \
  --output '<new-private-output-directory>'
```

Both locked provisioning commands and import/version gates exit **0**. Independent
harness controls also exit **0**: **18 tests in 0.279 seconds**, using
`<checkout>/.venv/bin/python -B <checkout>/scripts/test_dcc_macos_baseline.py`
from isolated CWD/HOME/temp without inherited AWS credentials. The committed
baseline similarly isolates its environment and runs its nine main / three
standalone modules unchanged, **not the full suites**.

| Stage | Import-checked Python / DuckDB / pytest | Passed | Skipped | Exit / timeout | Harness elapsed | Pytest elapsed |
|---|---|---:|---:|---|---:|---:|
| Main | 3.12.12 / 1.5.6 / 9.1.1 | 169 | 129 | 0 / false | 29.53 s | 29.05 s |
| Standalone | 3.12.12 / 2.0.0 / 9.2.0 | 267 | 0 | 0 / false | 47.51 s | 47.12 s |

Both stages report **zero failures, errors and deselections**. Private `summary.json`
reports `baseline_passed: true` and `reader_backend_qualified: false`. Raw
`main.txt`/`standalone.txt`, separate `qualification-review.json` and the full skip
inventory remain private; no account paths or telemetry identifiers are copied here.
The original `8ee714c` checkout and `provisioning-review.json` remain intact in their
separate failed-attempt directory; this result does not retroactively pass that run.

**Skip review:** every one of the **129 cases in 62 report groups** maps to a
committed `sys.platform != "linux"` guard with its reported reason. No unexpected
dependency, provisioning or standalone skip is present. Representative test names
below identify the excluded contracts; the private inventory retains every name
and per-group count.

| Main module | Skipped | Excluded contract and representative test names |
|---|---:|---|
| `test_coordination_authority.py` | 20 | Linux authority/writer-verifier supervision: `test_real_verified_authority_initialization_and_fresh_session_gate`, `test_abrupt_death_recovers_verified_high_water_without_reopening`, `test_entire_history_is_validated_beyond_first_bounded_batch`. |
| `test_coordination_completion.py` | 33 | Linux writer/completion supervision: `test_real_empty_completion_retains_proof_and_advances_exactly_one_hour`, `test_real_entity_completion_advances_high_water_atomically_and_preserves_originals`, `test_abrupt_completion_death_recovers_all_or_none_and_cannot_relaunch`. |
| `test_coordination_completion_controls.py` | 27 | Real Linux writer/verifier controls: `test_retained_proof_semantic_negatives_are_independent_of_audit_rejection`, `test_three_real_completed_hours_validate_across_instrumented_two_row_pages`, `test_v2_schema_fixture_preserves_genuine_authority_proof_and_reader_reservation`. |
| `test_coordination_execution.py` | 2 | Linux writer subreaper: `test_real_bound_empty_compactor_has_receipt_before_launch_but_still_blocks`, `test_real_local_migration_keeps_original_phase_evidence_and_blocks`. |
| `test_coordination_verification.py` | 10 | Linux writer supervision: `test_real_separate_standalone_empty_verifier_binds_intent_without_reopening`, `test_verifier_refuses_missing_or_changed_execution_shutdown_phase_evidence`. |
| `test_coordination_tick.py` | 3 | Linux procfs/subreaper: `test_abrupt_tick_death_never_launches_replacement_even_when_child_survives`, `test_real_supervised_callback_holds_ledger_lock_and_still_cannot_certify_empty_hour`, `test_supervisor_death_with_surviving_workload_remains_blocked`. |
| `test_coordination_supervisor.py` | 34 | Linux subreaper contract, including scalar/report negatives within the guarded module: `test_root_exit_does_not_leave_sleeping_or_detached_descendants`, `test_timeout_stops_sigterm_ignoring_tree_but_not_unrelated_child`, `test_caller_interruption_or_death_requests_cleanup_of_detached_tree`. |

**Disposition:** dcc-mac-baseline-01 passes and R9's reproducible packaging repair is
verified. R6 admission-clock and R7 SQL-integrity controls are included in the passing
native modules, but the worker's separate SQL-mutation result was not rerun. R8's
portable observers/platform refusal baseline passes; Linux-only real-tree and
completion paths remain skipped, not Mac-qualified. The worker's **641 main / 439
standalone full-suite** and **298 focus** Linux results remain separately attributed.
Supported Mac reader lifetime/shutdown, service/client/advisory exports/audited
recovery, actual-S3 and representative 32 GB RAM / 64 GB disk resource qualification
remain open. **dcc-02–05 stay unchecked.** No utility implementation, real grants or
dataset operation, source repair, deployment or assistant push; test data is synthetic.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_baseline.py; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py; ../Wintap-PyUtil/uv.lock; ../Wintap-PyUtil/extras/raw-sensor-compact/uv.lock -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_authority.py; ../Wintap-PyUtil/tests/test_coordination_completion.py; ../Wintap-PyUtil/tests/test_coordination_completion_controls.py; ../Wintap-PyUtil/tests/test_coordination_execution.py; ../Wintap-PyUtil/tests/test_coordination_verification.py; ../Wintap-PyUtil/tests/test_coordination_tick.py; ../Wintap-PyUtil/tests/test_coordination_supervisor.py §Linux-only skip guards -->

Maintainer documentation closure: `git diff --check` passes. Scoped checks cover
**11 changed wiki files, nine required-field frontmatters, 177 grounding paths,
208 inline source paths and 394 wikilinks (31 section targets)** with no new errors.
Existing index/log frontmatter exceptions and one historical broken log link remain
baseline issues, not whole-wiki acceptance. Complete diff/privacy review finds no
unauthorized identifiers; worker/original maintainer log histories and private
failed-attempt evidence are preserved. All stash conflicts are resolved; review
edits were left unstaged/uncommitted at that review checkpoint and the preservation
stash was retained. PyUtil's
unrelated environment artifacts remain untouched.

**Finalization:** the human subsequently authorized commit/push of the wiki review
and existing utility planning. Remaining implementation returns to the worker via
[[wiki/work/dbt-compaction-coordination/dev_handoff#Worker continuation after the Mac review]].
No additional runtime tests or acceptance claims are introduced by publication;
the original failure, reviewed skip boundaries and dcc-02–05 gates remain unchanged.
Finalization checks pass the same 11 wiki files/nine frontmatters, 177 grounding
paths, 208 inline sources and 401 links/37 section targets with no new errors;
complete diff/privacy and whitespace inspection pass. Baseline exceptions above
remain unchanged, and the pending push contains only wiki documentation.

### Baseline review regressions

Independent focused rerun before implementation, November 13, in the standalone
compactor checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_entities.py tests/test_cli.py
```

Result: **38 passed**. The main-checkout focused rerun:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider \
  tests/test_process_entities.py tests/test_dbt_source_validation.py \
  tests/test_compacted_inputs.py
```

Result: **63 passed, 1 skipped** (opt-in coverage). Both
commands were launched through temporary-directory wrappers, with `TMPDIR` and
pytest `--basetemp` scoped to disposable directories under `/tmp/opencode` and
automatic cleanup. They did not use real telemetry S3 qualification roots.

### Reader-supervision feasibility checkpoint — human review required

Continued after the successful Mac-result pull: Analytics fast-forwarded to
`65bff3d`; PyUtil was already current at `fab647f`. Scoped infographic preservation
stash was applied without conflicts and retained; all original unrelated tracked/
untracked edits remain. The successful Mac baseline and original blocked provisioning
attempt remain separate and unchanged. No baseline repeat or utility implementation.

**Source/dependency finding:** no safe native-Mac backend is established from the
investigated candidates. Pinned Apple XNU source rejects automatic `NOTE_TRACK`
descendant tracking and documents that the fork-event payload does not expose the
child PID. Historical launchd source describes same-process-group cleanup only.
These are published-source observations, not execution on the actual Mac. Installed
DBT selects a spawn context and constructs multiprocessing locks; thread-pool model
work does not imply zero child processes. Sources and unresolved candidate contracts:
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]].
<!-- GROUND_TRUTH: ../Wintap-PyUtil/.venv/lib/python3.11/site-packages/dbt/mp_context.py; ../Wintap-PyUtil/.venv/lib/python3.11/site-packages/dbt/contracts/graph/manifest.py §Manifest._lock; ../Wintap-PyUtil/.venv/lib/python3.11/site-packages/dbt/adapters/base/connections.py §BaseConnectionManager.__init__; ../Wintap-PyUtil/uv.lock §dbt-core/dbt-adapters/dbt-duckdb -->

Three fresh isolated dependency commands ran with the existing Linux supervisor,
credential-free workload environments, no source-data access and private immutable
observations under a new `/tmp/opencode/dcc-reader-feasibility-*` directory. Each
command had a 30-second runtime ceiling, 0.2-second stop grace, 5-second shutdown
ceiling and 64-KiB per-stream capture. Exact versions: Python **3.11.13**, DuckDB
**1.5.6**, dbt-core **1.12.3**, dbt-adapters **1.24.5**, dbt-duckdb **1.9.6**.

| Dependency control | Result |
|---|---|
| `get_mp_context().RLock()` in a fresh exec | Exactly one real `spawnv_passfds` launch; previously absent tracker becomes live. |
| `Manifest()` in a fresh exec | Exactly one real helper launch; tracker becomes live. |
| `Manifest()` with synthetic `spawnv_passfds` denial | Expected `PermissionError` propagates; manifest is not constructed, no helper starts, and the single created named semaphore is explicitly unlinked. This is Python injection, not a native-Mac sandbox result. |

All three assertions pass; roots exit zero and Linux `children_stopped` is true.
The two real-helper cases report `descendants_terminated`, not normal `exited`,
because the supervisor observes a surviving helper after root exit. The injected
case reports `exited`. Captured stdout sizes/hashes match the immutable observations.
No completion or grant release is inferred from these statuses. Private summary,
commands and logs are retained; no source/test/lockfile changes were made. These
three controls are dependency evidence, **not new red/green implementation tests**.

Existing Linux supervision regression, from the PyUtil checkout through the
previous disposable-CWD runner:

```sh
.venv/bin/python -B /tmp/opencode/dcc-run-tests.py main \
  /tmp/opencode/dcc-reader-feasibility-linux-supervisor.txt \
  tests/test_coordination_supervisor.py
```

Result: **34 passed, zero skipped, 5.82 seconds**. An earlier invocation with system
`python3` used Python 3.6 and failed in the runner before pytest because `text=True`
was unsupported; it produced no test result. The explicit existing main runtime
above corrected the invocation without changing any environment or dependency.
An initial shell `rg` attempt also failed because that executable is unavailable;
targeted installed-file reads and recursive `grep` supplied the source assessment.
Earlier ignore-filtered search misses were not treated as evidence of absence.

**Disposition:** invoke the handoff's human-review checkpoint. Backend selection
and broad slice-D integration pause; Linux/macOS scope and fail-closed reservation
retention remain selected. No weaker process-group release, automatic expiry,
sandbox dependency or Linux-only staging is approved. Mac runtime/shutdown, integrated
service/client/recovery, actual S3 and resource gates remain open; dcc-02–05 remain
unchecked. No sibling source edits, endpoint operation, production scheduling,
commit or push. Plan/handoff/Mac runbook/index and the open tension record this hold.

Closure checks: all **22 committed/local manifest identities** still match at
`fab647f`; identity-only validation did not rerun the Mac baseline. Scoped wiki
artifact checks pass eight Markdown files, six frontmatters, 154 grounding paths,
180 inline sources, 397 wikilinks and both new section targets. Complete diff/new-page
privacy inspection and `git diff --check` pass. The original infographic workflow
bytes match the preservation stash; every original index/log addition and the
retained stash still exist. Existing diagram XML references and PNG signature pass;
no diagram edit or rerender. Index/log frontmatter exceptions remain unchanged.

### Native Mac design review — coordinated launcher mismatch

Read-only tracing of the committed client found that `run_reader` launches
`DBT_BATCH`, which reaches `_dbt_run` and uses `subprocess.call` for DBT commands;
`dbt-build` runs a separate source preflight and then a build. The native restriction
probe instead invokes `dbtRunner().invoke()` in-process, while its no-fork control
denies subprocess creation. Thus the successful synthetic build/test does not
exercise the current coordinated DBT launch path and cannot establish its
compatibility with the restriction. An in-process coordinated adapter would be a
separate behavior change requiring equivalence coverage, and would still leave
resource-tracker ownership and full interruption/wrapper-death shutdown unresolved.

**Recommendation:** do not wire the sandbox/bootstrap experiment as the production
backend; retain the local-only DBT path unchanged. The human selected preserving
native-Mac scope and design-only work on an OS-supported helper/service boundary.
This source review did not identify a native helper/service contract that proves
detached-descendant shutdown. No backend code until ownership and shutdown proof are
accepted. This was static review only: no runtime, dependency, test, platform-
acceptance or shutdown claim changed.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/client.py §run_reader/main/_dbt_commands/_dbt_run; ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py §_restricted_child -->

### Native Mac helper/service boundary review — 2026-11-15

Reviewed Apple's public XPC, launchd, Endpoint Security, App Sandbox and
Virtualization documentation against the required fail-closed reader lifetime:

| Boundary | Documented capability and design disposition |
|---|---|
| XPC/launchd helper | launchd starts XPC services on demand, stops idle services and restarts crashes; the inspected launchd cleanup contract is process-group scoped. Service lifecycle is not a detached-descendant guarantee. Reject as a sufficient boundary by itself. |
| Endpoint Security | `NOTIFY_FORK` is notification-only and `AUTH_EXEC` authorizes image execution; a pure fork can continue without an exec event. Client setup also requires the documented entitlement/privilege and user approval path. Not established as deny-fork containment. |
| App Sandbox | Public documentation describes resource access constrained by entitlements; it does not establish a configurable no-fork policy or kill/reap semantics for a workload tree. Not a substitute for the deprecated custom profile without separate proof. |
| Virtualization.framework | Apple documents Linux/macOS guests on Intel and Apple-silicon Macs, a virtualization entitlement, and `VZVirtualMachine.stop` completion on successful stop. A stopped Linux guest is a candidate whole-workload boundary, but it is Linux DBT hosted by Mac—not a native macOS reader—and would require explicit scope approval plus guest, data, credential, entitlement and resource design. |

**Design result:** XPC/launchd service wrapping alone does not satisfy the requested
native-host contract. No native service/helper implementation or dependency is
selected. If no supported native-host containment primitive can be identified, a
Mac-hosted Linux VM is an explicit architecture/scope decision, not an inferred
fallback. In all designs, failed/missing stop acknowledgment, helper death or uncertain
ownership retains the reservation. No probe, backend implementation, entitlement
request or Mac runtime test was performed for this design review.
<!-- SOURCE: Apple XPC https://developer.apple.com/documentation/xpc; Apple launchd.plist(5), pinned historical source in wiki/tension/native-macos-readers-vs-descendant-shutdown.md; Apple Endpoint Security NOTIFY_FORK https://developer.apple.com/documentation/endpointsecurity/es_event_type_notify_fork and AUTH_EXEC https://developer.apple.com/documentation/endpointsecurity/es_event_type_auth_exec; Endpoint Security client requirements https://developer.apple.com/documentation/endpointsecurity/client; App Sandbox https://developer.apple.com/documentation/security/app-sandbox; Virtualization https://developer.apple.com/documentation/virtualization; virtualization entitlement https://developer.apple.com/documentation/virtualization/adding-the-virtualization-entitlement-to-your-project; VZVirtualMachine.stop https://developer.apple.com/documentation/virtualization/vzvirtualmachine/stop(completionhandler:); retrieved 2026-11-15. -->
<!-- SYNTHESIS: cited public API contracts compared against the complete-shutdown acceptance in wiki/work/dbt-compaction-coordination/implementation_plan.md and the open tension. -->

### Human-approved native-Mac risk rule — 2026-11-15

The human subsequently accepts a best-effort process-group boundary for coordinated
readers running natively on macOS. This supersedes the preceding disposition only
for the native-Mac normal-release predicate: a surviving supervisor may release
after the wrapper finishes and no live members are observed in the dedicated reader process group,
while accepting the residual risk that an escaped/detached descendant could remain
active and go unnoticed. Supervisor death, timeout, or uncertain group state or
acknowledgment retains the reservation for manual verification; no automatic expiry.
No Linux VM or Docker is a prerequisite. Linux release rules and direct local-only
DBT remain unchanged.

This is a human risk decision, not implementation, dependency/API selection, or
dcc-02–05 acceptance. No test or runtime probe was performed for this decision; the
process-group candidate's actual-Mac synthetic controls were run and recorded later
in this verification page. Broader backend/platform acceptance remains open.
<!-- SOURCE: Human native-Mac risk decision, conversation 2026-11-15. -->

## Baseline Review Manual Checks

- Read the manager brief, full design, handoff and implementation review plus the
  updated canonical ETL and durable-entity pages.
- Inspected live SQL validation, incremental snapshot orchestration, checkpoint
  DBT validation, S3 setup, CLI phase sequencing and metric derivation.
- Source at the reviewed baseline confirmed R1's unused bootstrap argument/missing current-state binding,
  R2's omitted validation parity, R3's update-window metadata construction,
  R4's post-deletion publication and reconciliation return boundary, and R5's
  unconditional consultation of an unused remote metrics override.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql §validate_processing_metrics; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_sql.py §validate_state; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/cli.py §run/publish_metrics; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py §metric_rows; ../Wintap-PyUtil/wintap_dbt/macros/s3.sql §configure_raw_sensor_access -->

Three independent disposable local probes also reproduced R2/R3: SQL validation
accepted a duplicate-key snapshot and a non-parent scalar corrupted against its
retained evidence, while the earlier Python validator rejected both; an incremental
next-hour update moved persisted bootstrap provenance to that update hour. The
probes used live standalone fixture helpers, preserved snapshot metadata, and
removed their temporary files automatically. No source/test files were added.

The manager's other disposable-fixture/captured-SQL observations remain imported
evidence in [[wiki/work/dbt-compaction-coordination/implementation-review]], not
independent reproductions here. Current baseline passes do not close the findings.

Artifact checks pass: two new-page frontmatters, 18 grounding paths, four
wikilinks, both diagram XML/reference checks and new-page whitespace/IP-literal
scans. The complete new pages and index/log diff were manually inspected for
persistent-content privacy; no actual host/account/IP identifiers were added.
`git diff --check` passed. At review time, PyUtil retained only its pre-existing
untracked artifacts; the authorized implementation changes are described above.

## Results

**R2/R3 slice committed locally as PyUtil `7d2b7f8`:** active SQL integrity validation and
bootstrap provenance have pre-fix failures, post-fix passes, positive compatibility
controls and full standalone/main regression coverage. Canonical guidance and the
plan/checklist reflect these changes. Changed-file Ruff lint/format and both
repositories' `git diff --check` pass. Current artifact checks cover three page
frontmatters, 32 live grounding paths and ten wikilinks, plus whitespace and
IP/account-home-path scans. Complete additions/diffs were reviewed for persistent
wiki privacy. Unrelated untracked and ignored local settings/data remain untouched.
The human-requested milestone commit contains only the verified slice. No push or
scheduler deployment was performed.

The selected architecture remains appropriate for cooperative shared access.
[[wiki/work/dbt-compaction-coordination/implementation_plan]] proposes a safety
milestone before real deletion/recovery integration, then retains the five handoff
units. Ledger/protocol tests may use fake children independently of writer fixes.

## Known Gaps

- R9's original `8ee714c` provisioning failure is historical. The repaired `fab647f`
  handoff passes exact-source/locked-runtime checks and the scoped actual-Mac baseline;
  it does not qualify skipped Linux writer/completion paths or Mac reader shutdown.
- R6–R8 are addressed by slice A's formal clock repair, authority-independent SQL
  negatives/mutation evidence and portable observers/platform guards. Actual macOS
  offline rerun passes; supported reader shutdown remains open. Historical results retain
  their original scope.
- Protocol/ledger library is regression accepted with 54 focused and 397 full-main
  passes. The admission/draining tick focus passes 100 cases; its full-main
  regression passes 443 tests (three skips), before supervisor implementation.
  The supervision/evolving-clock revision passes 142 focused cases and 485 full-main
  tests (three skips). This accepts those library primitives, not the full dcc-02 gate.
  No production scheduler/client or coordinated runtime
  qualification exists yet; dcc-02 remains unchecked.
- Completion/cursor/admission atomicity is human-confirmed. The ledger-v3 local
  normal-success prototype now retains completed history and atomically advances
  evidence/run/optional high-water/exact-hour cursor/backlog mode. Its hardened
  local controls pass 46 plus 24 cases before the final three budget/clock red/green
  controls; final combined main focus passes 298 tests and full standalone passes
  439 (two skips). Full main passes 641 (three skips) on the unchanged revision.
  These close local v3 regression, not integrated service acceptance. Receipt-bound
  launch passes 194 combined cases and 537 full-main tests (three skips). Separate
  receipt/intent/shutdown-authenticated verification passes 204 main focus cases;
  standalone data/authority verification passes 259 focus and 431 full tests (two
  skips); full verifier foundation main passes 547 tests (three skips). Ledger v2
  now implements verified authority initialization/freshness, explicit compatible
  upgrade and main entity-verifier integration, with 236 main/299 standalone focus
  passes after recorded prerequisite/authentication/integration repairs. Full authority
  standalone passes 439 tests (two skips); full main passes 579 (three skips), before
  completion/history implementation. No caller-supplied report or receipt is
  completion authority. Conservative launch and blocked/restart recovery boundaries
   remain intact. The uncommitted Linux overlay now adds service/client and audited
   reader, clean-hour and narrow checkpoint/deletion operations; local regressions
   pass, while broader recovery and qualification remain open. This is not actual-S3 or
   macOS backend acceptance.
- R2 SQL integrity and R3 provenance are repaired in `7d2b7f8` with red/green
  evidence; DBT's separate integrity macro remains narrower than CLI SQL validation.
- R1–R5/dcc-00 are prerequisite regression accepted. Do not certify coordinated
  writer recovery from freshness/coverage or synthetic repair success alone.
- Previous three-day rounds qualified SQL bootstrap and DBT compatibility, not
  scheduled incremental entity → deletion → checkpoint operation or complete ancestry.
- Steady-state resource measurements and actual shared-reader/writer latency remain
  unmeasured; example server budgets are unqualified.
- The native-Mac process-group lifecycle now has bounded synthetic qualification;
  real DBT/data, S3/service, representative-resource and deployment acceptance still
  need confirmation.

## Follow-Ups

Worker-reported local v3 high-water/history/atomic-completion full regressions pass;
R9's repair and the actual-Mac offline baseline are verified. The native-Mac
process-group candidate passes synthetic lifecycle qualification, but real DBT/data,
S3/service, representative-resource and broader backend acceptance remain open. Follow
[[wiki/work/dbt-compaction-coordination/macos-qualification#Stage 2: reader backend acceptance remains pending]];
continue service and audited operations before real destructive qualification. Add
commands, negative regressions and runtime qualification results as each planned unit
is implemented.

## Native macOS process-group prototype — actual-Mac synthetic lifecycle

PyUtil commit `c549424`, based on `1f4897a` in the isolated feature branch, implements
a native macOS coordinated reader path and wires it through the existing client. It is
committed locally and not pushed. The accepted risk contract is
unchanged: a normal release may follow wrapper completion and no live member remaining
in the dedicated process group; descendants escaping into another session/group remain
an accepted residual risk. Timeout, interruption, supervisor death, uncertain shutdown
or lost acknowledgment does not publish a release and retains the durable reservation
for manual verification. Direct local-only DBT and Linux's subreaper contract remain
separate and unchanged. No deployment, scheduling, actual S3, or real-data work occurred.

The first kqueue revision signaled the process-group ID after wrapper exit and failed
actual-Mac controls with `EPERM`. A reproduced macOS behavior is that `killpg(..., 0)`
can return `EPERM` for an exited but unreaped group leader; this is not safe evidence
for either emptiness or permission to signal. The corrected worker observes wrapper
exit via kqueue, enumerates live group members with `/bin/ps` while the direct child
remains unreaped, ignores zombie-only members, and sends TERM/KILL only before reaping.
The caller masks termination signals across worker creation; the worker installs its
cleanup handlers before unblocking inherited signals.
After `wait()`, it does not inspect or signal that numeric PGID. Enumeration errors,
ambiguous group state or inherited capture pipes that remain open fail closed. This is
cooperative best-effort supervision, not hostile-process containment.

### Actual-Mac results

- `uv run --locked --python 3.12 --group dev pytest -q tests/test_coordination_macos_supervisor.py` — **12 passed** (3.15 s). Controls include normal/nonzero exit, same-group child shutdown, timeout, missing executable, output limits, detached-child characterization, escaped pipe uncertainty, interrupt, caller/wrapper death, supervisor death/no observation, lost acknowledgment, and coordinated-client release/retention.
- `uv run --locked --python 3.12 pytest -q -rs tests/test_coordination_supervisor.py tests/test_coordination_client.py tests/test_coordination_local_route.py tests/test_coordination_macos_supervisor.py tests/test_coordination_retry.py` — **17 passed, 113 skipped**. The skips are declared Linux subreaper/reader and Linux unprivileged-merge tests; Mac lifecycle and local route controls ran.
- Final ephemeral stress driver — **50 normal exits and 20 same-group descendant shutdowns passed**. It was not added as a checked-in test.
- Black `--check` on the supervisor, client and Mac test, plus `git diff --check`, passed.

### Linux regression after candidate handoff — focused, no behavior change observed

The transferred PyUtil candidate is available as `c549424`, parent `1f4897a`. Its
parent is directly above the previous Linux target `123b9d3`; that intervening
commit adds the native feasibility probe and coordination README notes. Candidate
changes add Darwin dispatch/result-scope handling while retaining the Linux
subreaper worker and Linux client observation contract.

On Linux, the focused supervisor/client/lifecycle/local-route run passes **90** and
skips **12** in **23.43 s**. The skipped tests are the native-Mac-only controls;
Linux supervisor, client and lifecycle controls execute. Command, from the PyUtil
root, with a fresh pytest base directory under `/tmp/opencode`:

```sh
run_dir=$(mktemp -d /tmp/opencode/dcc-macos-linux-focused.XXXXXX)
TMPDIR=/tmp/opencode .venv/bin/python -B -m pytest -q --basetemp="$run_dir" \
  tests/test_coordination_supervisor.py \
  tests/test_coordination_client.py \
  tests/test_coordination_linux_lifecycle.py \
  tests/test_coordination_local_route.py \
  tests/test_coordination_macos_supervisor.py
```

No Linux behavior change was observed in this focused run; direct local-only DBT
and the Linux subreaper shutdown contract remain unchanged. Black check passes via
`.venv/bin/python -m black --check` on the changed Python files, and
`git diff 1f4897a..c549424 --check` passes. The installed Black console-script
launcher has a stale interpreter reference, so the module invocation was used.
This focused regression does **not** rerun the earlier 307-control service-affected
gate or qualify full latest-HEAD integration, actual S3, production DBT/data,
representative resources or deployment.

The suite uses synthetic commands and fake coordination transport. It does not qualify
production DBT/preflight/data behavior, actual S3, Linux runtime, production service
installation, representative resources, or deployment. Producer recovery files were
not edited.
The separate Analytics advisory status utility retains its existing scoped verification
record and was not changed or re-run by this Mac supervision pass.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_mac_worker; ../Wintap-PyUtil/wintappy/coordination/client.py §run_reader/main; ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py; ../Wintap-PyUtil/wintappy/coordination/MACOS.md -->

## Current-revision Linux candidate baseline — affected passed; main red, standalone active

The detached PyUtil checkout is fixed at `c549424b6cf507f33dee301d85bd9e0aeb082e1b`
and remained clean. Its 15-module affected scope passes **341 tests** with **12
expected native-macOS skips** in **1807.15 s**; the complete 19-line report was reviewed
after completion and contains no failure or error. The executed scope comprises the
service, client, Linux lifecycle, local route, recovery, maintenance, deletion recovery,
retry and intentional-retry modules, entity service, supervisor, and native-Mac
supervisor controls. The 12 skips are only the declared Darwin-specific controls.

Both suites collect successfully at this revision: **1535 main** and **697 standalone**
tests. Test processes use isolated home/temp/base directories, an empty AWS config and
credentials file, disabled EC2 metadata, and an environment stripped of opt-in S3
approval variables. The existing main test driver is Python 3.11; the candidate's
standalone environment was provisioned offline with its lock at Python 3.13. The
earlier attempt without that checkout-local standalone runtime (183 failures, 141
passes, 12 skips and 17 errors before timeout) is retained but invalid as regression
evidence; it is not combined with the corrected report. The corrected affected run,
candidate status/whitespace check, and Black check on all four changed Python files are
clean. Ruff passes on the changed runtime modules; no candidate source was edited.

The full main suite completed in **6421.87 s** with **1519 passed, 15 skipped and one
failed**. The failure is
`test_unsupported_writer_supervision_refuses_launch_and_tick_stays_blocked[darwin]`.
Its unchanged control requires unsupported generic/writer supervision to refuse Darwin
before launch. In `c549424`, `_config` now accepts Darwin and `run_supervised` dispatches
every caller to `_run_macos_supervised`; the test's `Popen` sentinel confirms the
worker launch is attempted. The same test is unchanged from the parent, whose
`_config` rejects non-Linux platforms. A separate Darwin-only rerun reproduces the
failure (one failed, 51 deselected). This exposes scope leakage: the candidate's native
Mac contract is coordinated-reader supervision, while the generic library remains
documented as Linux-only. It is a candidate regression requiring correction and a new
affected/full gate, not a Mac-only skip or evidence of real writer execution.

The first standalone full-suite invocation used the repository-root working directory,
so Python 3.13 collected main-suite modules and reported 15 missing-dependency import
errors. That report is runner-invalid and preserved separately. The standalone suite is
being rerun from `extras/raw-sensor-compact/` with its offline-locked runtime and a new
report/temp directory; its result is pending. No source was changed in response to the
main-suite failure. This local synthetic evidence does not qualify real data/S3,
production DBT, representative resources, service deployment, native-Mac backend
acceptance or rollout.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_service.py; ../Wintap-PyUtil/tests/test_coordination_client.py; ../Wintap-PyUtil/tests/test_coordination_linux_lifecycle.py; ../Wintap-PyUtil/tests/test_coordination_local_route.py; ../Wintap-PyUtil/tests/test_coordination_recovery.py; ../Wintap-PyUtil/tests/test_coordination_maintenance.py; ../Wintap-PyUtil/tests/test_coordination_deletion_recovery.py; ../Wintap-PyUtil/tests/test_coordination_retry.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_controls.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_history.py; ../Wintap-PyUtil/tests/test_coordination_intentional_retry_credentials.py; ../Wintap-PyUtil/tests/test_coordination_entity_service.py; ../Wintap-PyUtil/tests/test_coordination_supervisor.py; ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py -->
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_config/run_supervised; ../Wintap-PyUtil/tests/test_coordination_tick.py §test_unsupported_writer_supervision_refuses_launch_and_tick_stays_blocked; ../Wintap-PyUtil/wintappy/coordination/README.md §Linux command-tree supervision -->
