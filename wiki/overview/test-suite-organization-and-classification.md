---
title: "Test Suite Organization and Classification"
type: concept
confidence: medium
grounded_by:
  - ../Wintap-Analytics/streamlit/projects/SmokeTests
  - ../Wintap-Analytics/streamlit/projects/HostActivity
  - ../Wintap-Analytics/validation
  - ../Wintap-Analytics/wiki/work/host-process-identity-patch
  - ../Wintap-PyUtil/tests
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests
  - ../Wintap-PyUtil/wintap_dbt/tests
  - ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py
  - ../Wintap/tests/Wintap.Tests/Wintap.Tests.csproj
  - ../Wintap/tests/Wintap.Tests/README.md
  - ../Wintap/devtools
policy: agent-editable
last_validated: 2026-11-25
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects; validation; wiki/work/host-process-identity-patch; ../Wintap-PyUtil/tests; ../Wintap-PyUtil/extras/raw-sensor-compact/tests; ../Wintap-PyUtil/wintap_dbt/tests
tags: [testing, test-organization, regression, integration, qualification, streamlit, dbt, coordination, compaction]
---

# Test Suite Organization and Classification

This page is the inventory and refactor plan for the Analytics and Wintappy test
trees. It is intentionally a plan, not authorization to delete evidence. The
first refactor should make purpose and execution boundary visible in the
filesystem; stale or duplicative cases are reviewed only after that boundary is
recorded.

## Wintap Extension — Current Platform Boundary

On November 22 the human expanded this workflow to Wintap repository tests,
requesting initial analysis/planning, not a filesystem change in that pass.
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis]]
records 63 C# files in one Windows-qualified xUnit project (including linked Linux
helpers), plus seven Python test-control files. Static attributes/methods are not
runtime collection or execution results. Native command/traffic workloads, source
guards, and process-wide integration require separate named gates.

The human subsequently approved
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]] and
explicitly deferred the unavailable Windows baseline for a static draft on the
shared feature checkout. Five reviewed classes now have `TestKind=unit` and
`Execution=synthetic` and reside under `Unit/Api`, `Unit/Shared`, and
`Unit/Windows/File` / `Unit/Linux/File`. Existing `Category` tags, source bodies,
fixture access, dependencies, and full-suite/CI selection are unchanged. The test
README records partial inventory and focused Windows commands. macOS/Linux feature
testing is complete and `Lintap.Tests` now exists; native Windows build,
discovery/filtering and execution remain a separate gate. Broader platform ownership
remains under review in
[[wiki/tension/wintap-test-platform-boundaries]]. The Analytics/PyUtil inventory
and historical verification below retain their original scope.
<!-- GROUND_TRUTH: ../Wintap/tests/Wintap.Tests/Wintap.Tests.csproj; ../Wintap/tests/Wintap.Tests/README.md; wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md -->

## Iterative Implementation — November 22

The human selected this plan as Phase 1 of
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief]], then authorized
small first-draft changes with lightweight affected checks and later validation
against fresh small sensor captures from a separate session. The detailed loop is
in [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan]].

The first cut relocates all three HostActivity modules intact to
`tests/contract/` and PyUtil configuration to `tests/unit/config/`. PyUtil's four
synthetic SQL modules remain in place with explicit `contract` markers because
they have shared relative-import dependents. Partial per-suite READMEs record
counts, execution boundaries, and mixed coverage still awaiting separation.
HostActivity passes 59 cases; PyUtil preserves 224 selected identities and passes
17 representative cases. Full-suite defaults are unchanged; no assertions or
historical evidence were removed. Bounded Linux capture/DBT validation is complete;
remaining suite restructuring and native Windows acceptance are tracked in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]].
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/tests/README.md; ../Wintap-PyUtil/tests/README.md; wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md -->

The November 22 tracked file inventory was 11 Analytics application test files, 10
validation files, 14 feature-work files, 60 PyUtil main files, 20 compactor files,
and seven DBT SQL files. No refreshed full-suite collection is claimed. The
original snapshot below is retained as historical context, not today's baseline.

## Historical Snapshot — November 17

The inventory excludes dependency `site-packages`, virtual environments, and
untracked run data/configuration.

| Area | Current inventory | Collection boundary | Main navigation problem |
|---|---:|---|---|
| Analytics Streamlit projects | 10 Python files | Per-project `unittest` discovery | Files mix source contracts, query semantics, transport controls, and UI rendering. |
| Analytics validation | 10 Python files | Per-harness `unittest` or `pytest` | Mocked contract tests and host/collector qualification controls are adjacent but not equivalent. |
| Analytics feature work | 14 Python test files | Explicit feature-work commands | Historical analysis tests sit beside experiment scripts and retained evidence. |
| PyUtil maintained `tests/` | 59 Python files; 1,538 collected tests | Default PyUtil pytest suite | Forty-two coordination files and several entity/history variants form a large flat namespace. |
| PyUtil compactor project | 20 Python files; 702 collected tests | Separate `extras/raw-sensor-compact` pytest project | Unit-like engine/config tests, synthetic qualification, and opt-in S3 tests are flat. |
| PyUtil DBT tests | 7 SQL files | dbt test/build | SQL contracts are already separated, but Python DBT/semantic tests remain beside unrelated tests. |
| PyUtil macOS harness control | 1 Python file | Explicit script/unittest harness | It is a refusal/identity control, not native-Mac qualification, and should be labeled accordingly. |

The 1,538 and 702 figures are collection counts, not unique test-function
counts; parametrization expands the collected cases. The default PyUtil
`pyproject.toml` collection path is `tests`, so the compactor and script suites
must not be assumed to run with the default command.

## Classification vocabulary

Every test file should have one primary class and, where useful, one execution
qualifier. A directory is preferred over a filename suffix for the primary
class.

| Class | Meaning | Default behavior |
|---|---|---|
| `unit` | Pure function/module contract with synthetic in-memory or temporary inputs. | Runs in the normal local regression command. |
| `contract` | Cross-module schema, SQL, CLI, or application-boundary behavior without a live host or external dataset. | Runs in the normal local regression command. |
| `integration` | Multiple real project components cooperate using isolated local fixtures, subprocesses, DuckDB, or a fake transport. | Runs in a named integration gate; may be included in CI after cost review. |
| `qualification` | Evidence-producing control for a release, platform, lifecycle, or retained-artifact claim. | Runs only through a named qualification command and records scope/results. |
| `live` | Requires a real host, S3-compatible service, installed collector, or native platform. | Never runs by accidental default discovery; requires an explicit opt-in. |
| `historical` | Preserved feature-work evidence or an analysis helper tied to a closed investigation. | Retained for provenance, but not part of the maintained default suite. |

`live` is an execution qualifier, not a claim of production readiness. A test
may be `qualification + live`, or `qualification + synthetic`. The test name
must not be the only place where this distinction is encoded.

## Proposed filesystem

### Analytics

Keep each application or validation harness self-contained, but introduce a
small purpose hierarchy:

```text
streamlit/projects/HostActivity/
  tests/
    contract/       # configuration, metadata discovery, query contracts
    ui/             # Streamlit AppTest/render/navigation controls
    transport/      # synthetic S3/connection boundaries, if any

streamlit/projects/SmokeTests/
  tests/
    contract/       # analysis, query, quality, durable-result contracts
    ui/             # app and page navigation/rendering
    transport/      # synthetic source and default-on loopback HTTP/S3 transport

validation/<harness>/
  tests/
    unit/           # pure workload/schema/evaluator/runner behavior
    integration/    # subprocess, DuckDB, or harness composition
    qualification/  # host/platform evidence controls

wiki/work/host-process-identity-patch/
  tests/
    analysis/       # deterministic analysis and evidence parsing tests
    qualification/  # installed/pressure/shutdown/retry evidence controls
```

As of 2026-11-24, the SmokeTests hierarchy is implemented: 86 contract cases,
one default-on loopback transport case with explicit opt-out, and 13 Streamlit UI
cases are discovered exactly once. The additional contract covers exact hourly
evidence discovery; the thirteenth UI case covers sanitized remote connection
diagnostics. No project-root forwarding test modules remain.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/tests/contract; streamlit/projects/SmokeTests/tests/transport; streamlit/projects/SmokeTests/tests/ui -->

The Analytics moves should be mechanical first. Splitting a large file such as
`HostActivity/tests/contract/test_host_activity.py` or `SmokeTests/tests/contract/test_analysis.py` is a
separate change because it changes imports and makes duplicate assertion review
harder.

### PyUtil default suite

Replace the current coordination prefix namespace with purpose-oriented
directories while retaining descriptive test names:

```text
tests/
  unit/
    analytics/ database/ etlutils/
    config/
  contract/
    dbt/ sql/ input-roots/
  integration/
    processing/ coordination/
  qualification/
    coordination/
      authority/ lifecycle/ entity/ retry/ recovery/
  compatibility/
    coordination/ entity/
  platform/
    linux/ macos/
```

The coordination split is by behavior, not by the historical filename prefix:

- `protocol`, `ledger`, `authority`, `client`, `execution`, `service`, `tick`,
  and the ordinary supervisor controls are maintained coordination contracts or
  local integration tests.
- Entity intent, observation, operation, publication, resolution, completion,
  and schema tests are split between ordinary contracts and qualification
  controls according to whether they create genuine retained history and
  independently verify it.
- `*_history`, `*_qualification`, `*_crashes`, and `*_upgrade` are not presumed
  stale. They become visibly named qualification, fault-injection, or
  compatibility suites, with retained-artifact provenance in a README or
  manifest.
- Linux lifecycle and macOS supervisor tests move to platform-qualified
  directories. Native-Mac tests remain skipped unless the platform is Darwin;
  they do not become generic cross-platform regressions.

Other PyUtil groups should be moved as follows:

```text
tests/
  integration/processing/
    compacted_inputs.py compacted_s3_migration.py
    process_entities.py process_entities_s3.py
  contract/dbt/
    dbt_source_validation.py effective_input_roots.py checkpoint_repair.py
  contract/sql/
    filetime_precision.py network_activity.py process_gold_quality.py selinux.py

extras/raw-sensor-compact/tests/
  unit/                 # config, storage, engine, CLI parsing
  integration/          # compaction, deletion, inventory, entity processing
  qualification/        # completion/entity/retry/phase evidence and recovery
  live/                  # explicitly opted-in S3 transport
```

The existing `wintap_dbt/tests/*.sql` directory should remain the canonical
location for dbt SQL tests. The script control should move to
`scripts/tests/test_dcc_macos_baseline.py` or be kept adjacent to the script,
but its README must call it a harness identity/refusal test rather than actual
Mac qualification.

## Candidate review matrix

These are review groups, not deletion decisions.

| Review group | Current files | Initial disposition | Reason |
|---|---|---|---|
| SmokeTests analysis/pages/app | `test_analysis.py`, `test_pages.py`, `test_app.py` | Relocate, then compare/possibly merge assertions | They all cover working sets, selected runs, overlap, and evaluation boundaries at different layers. Keep UI navigation tests separate from pure query/materialization contracts. |
| SmokeTests source/HTTP | `test_s3_source.py`, `test_s3_http.py` | Retain and mark transport tiers | Synthetic source parity and loopback-only HTTP are default-safe. HTTP supports explicit environment opt-out and is not Garage acceptance. |
| Entity observation/completion | `test_coordination_entity_observations.py`, `*_observation_qualification.py`, `*_completion_observations.py`, `*_completion_qualification.py`, `*_completion_history_qualification.py`, `*_completion_crashes.py` | Relocate; build a coverage map before any merge | Names overlap, but the files distinguish ordinary contracts, genuine retained history, crash seams, and budget/immutability controls. |
| Entity publication/history | `test_coordination_entity_publications.py`, `*_publication_qualification.py`, `*_writer_history.py`, `*_forward_history.py`, `*_resolution.py` | Relocate; extract shared fixture support only after comparison | Similar lifecycle vocabulary does not prove duplicate evidence. Preserve independent-original and forward-history controls. |
| Intentional retry | `test_coordination_retry.py`, `test_coordination_intentional_retry.py`, `*_controls.py`, `*_history.py`, `*_credentials.py`, `*_upgrade.py` | Relocate into contract, qualification, compatibility | Separate retry protocol behavior from retained-history, credential-freeze, and schema-upgrade evidence. |
| Completion and verification | `test_coordination_completion.py`, `test_coordination_completion_controls.py`, `test_coordination_verification.py` | Investigate overlap; do not delete | These likely share completion terminology but exercise distinct verifier, retained-proof, and multi-hour controls. |
| Compactor entity verification | `test_entity_operation_verifier.py`, `test_entity_verifier_qualification.py`, `test_entity_verifier_review.py`, `test_entity_integrity.py`, `test_entity_freshness.py`, `test_phase_evidence.py` | Relocate and compare assertions | The cluster has the clearest likely duplication risk, but independent SQL, authority, phase, freshness, and resource-boundary checks may be intentional. |
| Local versus S3 processing | `test_process_entities.py`, `test_process_entities_s3.py`, `test_compacted_s3_migration.py`, compactor `test_s3_transport.py` | Retain with explicit `integration`/`live` labels | The S3 cases have distinct access and mutation scopes; no default test may write external data. |
| Feature-work tests | `wiki/work/host-process-identity-patch/test_*.py` | Relocate under `tests/analysis` or `tests/qualification`; archive only after feature closeout review | These are valuable evidence but should not look like maintained product regressions. |

## Staleness and duplication rules

Do not use age or a filename containing `history`/`qualification` as a removal
criterion. A candidate may be archived or deleted only when all of the following
are recorded:

1. its current production import/API still resolves, or the test is proven to
   target removed behavior;
2. its assertions are mapped to a retained replacement or explicitly declared
   historical evidence;
3. its execution command and platform/data scope are recorded;
4. git history or a feature-work artifact establishes whether it is evidence
   that must be preserved; and
5. the replacement gate passes with the old case removed in an isolated trial.

Before that review, use `retain`, `relocate`, `rename`, `split`, `merge-review`,
`archive-review`, or `investigate` dispositions. `delete` is not an initial
disposition.

## Refactor sequence

1. **Freeze the inventory.** Add per-directory READMEs or a small manifest with
   class, platform, opt-in variables, collection command, and evidence policy.
2. **Add explicit markers/commands.** Introduce stable markers such as
   `unit`, `contract`, `integration`, `qualification`, `live`, and `historical`
   where the project test runner supports them. Make default commands exclude
   live and historical suites.
3. **Relocate without semantic edits.** Move Analytics project tests and the
   small PyUtil non-coordination groups first; update imports and README
   commands, then compare collection counts.
4. **Partition coordination/entity tests.** Move one behavior family at a time,
   extract only genuinely shared fixtures, and preserve a before/after test
   manifest so no qualification case disappears silently.
5. **Separate retained evidence.** Move feature-work tests and compactor
   qualification tests under explicit `qualification`/`historical` paths with
   provenance and a bounded command.
6. **Review candidates.** Use coverage-by-behavior, not line count, to decide
   whether assertions merge. Archive only superseded or irreproducible evidence
   after human review.
7. **Close with a gate.** Record default, integration, qualification, and live
   collection counts separately. Update this page when the target tree is
   implemented.

## Required verification after filesystem changes

At minimum, the implementation should compare:

- Analytics Streamlit project discovery and each validation-harness command;
- PyUtil default pytest collection (historical snapshot: 1,538 collected tests);
- the isolated compactor project (historical snapshot: 702 collected tests);
- the seven dbt SQL tests through the existing dbt command;
- explicit native-Mac refusal/lifecycle controls on Linux and native-Mac
  qualification only on Darwin; and
- every opt-in S3/local qualification command with a fresh isolated scope.

No test move is complete if the suite count changes without an explanation,
an import-path update, and a recorded purpose/collection boundary.
