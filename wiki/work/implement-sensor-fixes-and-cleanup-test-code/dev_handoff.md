---
title: "Dev Handoff: Wintap TODO Review and Linux Implementation Continuation"
type: concept
confidence: medium
grounded_by:
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md
  - streamlit/projects/HostActivity/tests/README.md
  - ../wintap/tests/Wintap.Tests/README.md
  - ../Wintap-PyUtil/tests/README.md
  - wiki/todo/index.md
  - wiki/todo/periodic-process-refresh-listing.md
  - wiki/todo/linux-process-name-exe-fallback.md
  - wiki/todo/lintap-linux-process-command-line-quality.md
  - wiki/todo/linux-process-executable-attribution.md
  - wiki/todo/transformer-five-tuple-connection-port-key.md
  - wiki/todo/linux-nfs-process-network-attribution.md
  - wiki/todo/linux-interactive-session-feed.md
  - wiki/todo/listening-socket-capture-and-modeling.md
  - wiki/todo/raw-sensor-upload-time-partition.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan.md
  - ../wintap/AGENTS.md
  - ../wintap/CLAUDE.md
  - ../wintap/global.json
  - ../wintap/wintap/Makefile
  - ../wintap/tests/Wintap.Tests/Wintap.Tests.csproj
  - ../wintap/tests/Wintap.Tests/S3UploadAttemptBindingTests.cs
  - ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs
  - ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs
  - ../wintap/wintap/core/etl/load/adapters/base/S3UploadAttemptBinding.cs
  - streamlit/projects/SmokeTests/tests/README.md
policy: agent-editable
last_validated: 2026-11-24
repo_scope: cross-repo
implementation_area: dev-environment
event_domain: cross-domain
audience: llm-agent
status: draft
source_paths: wiki/todo; wiki/work/implement-sensor-fixes-and-cleanup-test-code; ../wintap/wintap/platform/linux/sensor; ../wintap/wintap/core/etl
tags: [feature-work, dev-handoff, linux, wintap, todo, sensor-fixes, iterative-development]
---

# Dev Handoff: Wintap TODO Review and Linux Implementation Continuation

## S3 Upload-Time Partition Correction — Handoff 2026-11-24

The approved shared .NET S3 uploader correction is implemented on this feature
branch. The Lintap build passed with 0 errors, and the focused
`S3UploadAttemptBindingTests` filter passed 8/8 using the available .NET 10 SDK.
The implementation uses current UTC upload partitions, durable unresolved-attempt
sidecars, exact-key HEAD validation, safe current-key rebinding after an
authoritative 404, and exact-key retry after an inconclusive HEAD.

Testing continues on another host for an authorized S3-compatible endpoint and
ambiguous PUT/HEAD fault scenarios. Do not treat the local build or focused unit
pass as live endpoint qualification. Preserve the current Wintap source commit
`e92016daef33eb34aec65e35c4c14eba4ef4e10c` and run the endpoint matrix there
without modifying Parquet contents or event timestamps.
<!-- HUMAN-DECISION: conversation 2026-11-24 — commit the implementation locally and continue live S3 testing on another host. -->

## Current Test-Engineering Assignment — Linux Destination

The human has now assigned this session test implementation/testing and requested
the bounded continuation plan in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan#Current Linux Tranche — Test Development While Captures Are Pending]].
Lightweight existing-data readiness checks may precede TC-03; fresh-fix correctness
still requires the sensor engineer's independent capture handoff. The prompts
below preserve the transfer checkpoint; use the current tranche for test next steps.
<!-- HUMAN-DECISION: conversation 2026-11-22 — prepare the test plan and permit no-heroics existing-data smoke while fresh captures are pending. -->

Destination checks pass 59 HostActivity/7 stdlib parser controls. The authorized
RHEL dataset is under PyUtil's `data/wintap-analysis/rhel8/`; DB read-only readiness
passes, and its empty raw directory is a final one-time sample result rather than a
future gate. A subsequently approved isolated uv
environment now passes 17 PyUtil cases and preserves all 224 selected identities
(4 unit / 220 contract); its old `.venv` remains unusable and untouched. Windows
managed acceptance remains deferred. The opt-in helper and first bounded
SmokeTests query/quality cleanup slice are implemented. A second whole-file move
adds analysis/store controls, and a third adds mocked, transport-free S3 source
contracts. A fourth moves the 11-case durable producer/Parquet contract with only
path/import adjustments; a fifth moves the unchanged 5-case page-query contract.
The classified package passes 85 cases. The synthetic localhost HTTP case is now
default-on with explicit environment opt-out. The transport case now lives under
`tests/transport`, and all 12 Streamlit AppTest cases live under `tests/ui`; the
full project passes 98/98 with no root-level forwarding tests. SmokeTests
organization is complete. Select the next validation/PyUtil/coordination slice
from the implementation plan rather than moving these cases again.
<!-- HUMAN-DECISION: conversation 2026-11-22 — the RHEL sample will not be updated; do not wait for raw files there. -->

## Newly Included Process-Name Scope — 2026-11-23

The current feature now includes the latest finding that one OS PID is associated
with multiple `process_name` values. Continue through
[[wiki/todo/linux-process-executable-attribution]] and the bounded plan in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan#Included process-name multiplicity scope — 2026-11-23]].

Do not key the investigation on PID alone. First separate PID reuse across distinct
`PidHash` values from repeated exec observations within one birth-scoped identity.
For the latter, distinguish `exec_attempt` from `exec_success`, order observations
with the additive observation fields, and keep name/path from the same row. The
current PyUtil silver model's independent `any_value` selections are part of the
investigation. No representative initial/latest-image policy, schema change, or
historical repair is approved yet.
<!-- HUMAN-DECISION: conversation 2026-11-23 — include the multiple-name/same-PID issue in this feature. -->

## Test-Cleanup Copy/Paste Prompt

```text
Resume the test-cleanup workstream using:
wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff.md

Read the destination AGENTS.md files and applicable Wintap rules, this handoff,
the implementation plan, verification record, and Wintap test plan. Verify that
Analytics 0f8b414, Wintap 123bd70, and PyUtil 564ec43 are present in the intended
feature checkouts; retain any newer work. Do not repeat the completed moves.

Analytics has 59 passing offline cases; PyUtil has 17 passing representative
cases and 224 preserved collected identities. Wintap's five moves/traits are
static-checked only: Windows SDK 10.0.402 build/discovery/filtering/runtime
acceptance remains pending. Source expectations of 77/84 cases are not passes.

Coordinate ownership with the separate sensor worker in the shared Wintap
checkout. Check the new host's actual OS, tools, and separate Python environments;
report missing prerequisites without installing/upgrading or retargeting tests.
When existing environments are ready, rerun only the documented lightweight
checks, record destination results separately, and retain the 120-second ceiling.

Next: include the approved process-name multiplicity investigation. Obtain the
exact producer/PyUtil revisions, authorized read-only capture, UTC interval and
source layer. Compare same PID with `PidHash`; classify PID reuse, exec attempts,
successful image transitions and downstream aggregation before refining only the
affected tests. Do not preselect initial/latest-image policy, broaden data access,
weaken an oracle, or treat the remaining TODO candidates as an approved work queue.
```

## Sensor-Preparation Copy/Paste Prompt

```text
Resume Wintap implementation preparation on Linux using:
wiki/work/implement-sensor-fixes-and-cleanup-test-code/dev_handoff.md

Read the destination repositories' AGENTS.md and Wintap CLAUDE.md, then this
handoff and the existing feature brief, implementation plan, verification,
and Wintap test plan. Preserve all existing test-cleanup work.

The human reviewed nine Wintap-related TODOs and requested this machine-transfer
handoff. No sensor fix, schema change, build/capture scope, deployment, or
cross-repo code-edit authorization was selected in that review.

Verify destination revisions, dirty/untracked work, Linux prerequisites, and
available test boundaries. Report readiness and ask which TODO and first small
slice to implement. Follow the human-approved Wintap instruction/role workflow;
do not start implementing all nine items or dispatch another agent yourself.
```

## Handoff Summary and Current Authority

The development team is moving from TODO review to a Linux implementation
system. Preserve the following list as the candidate backlog, not an approved
implementation sequence. Handoff preparation was documentation only; it did not
change sensor code, run builds/tests/captures, or access telemetry datasets.
<!-- HUMAN-REQUESTED: conversation 2026-11-22 — retain the reviewed Wintap TODO list and prepare a Linux continuation dev_handoff.md. -->

The existing feature folder hosts the iterative test-cleanup/sensor-capture loop.
Its test session has separate authorization and work already in progress; that
does not automatically select or authorize these sensor fixes. Under Wintap's
standing methodology, the Engineer prepares instructions/wiki, the human approves
and dispatches one unit, and the Developer implements/tests and writes its audit.
Instructions/audits stay in Wintap `developer_docs/`; shared knowledge stays here.
<!-- GROUND_TRUTH: ../wintap/CLAUDE.md §The Methodology — Three Roles; wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan.md §Scope and Ownership -->

## Commit/Transfer Checkpoint — 2026-11-22

The human subsequently authorized committing both sessions' feature work across
the three repositories. A later read-only commit review confirms:

| Repository | Reviewed commit | Preserved state / evidence |
|---|---|---|
| Wintap-Analytics | `0f8b414` | Three HostActivity modules relocated, discovery/path fixes, wiki and original Linux handoff. Latest recorded rerun: 59 passed. |
| Wintap | `123bd70` | Five approved moves and two class traits per file, plus test README. No production/project/dependency change; static checks only. |
| Wintap-PyUtil | `564ec43` | Configuration relocation, unit/contract markers, partial inventories. Latest recorded rerun: 17 passed; 224 selected identities preserved (4 unit / 220 contract), not 224 executed passes. |

All three are checked out on
`feature/implement-sensor-fixes-and-cleanup-test-code`. At pre-edit review,
Wintap was clean; Analytics and PyUtil had no tracked changes and retained
excluded unrelated local artifacts.
No new sensor implementation, dataset capture, or Windows runtime result appears
in these commits. Recorded passes belong to the source Mac environment, not the
destination. Read the verification page for commands and limits.
<!-- GROUND_TRUTH: streamlit/projects/HostActivity/tests/README.md; ../wintap/tests/Wintap.Tests/README.md; ../Wintap-PyUtil/tests/README.md; wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification.md §Commit Preparation Checkpoint -->
<!-- SOURCE: Read-only git log/show/status review of Analytics 0f8b414, Wintap 123bd70, and PyUtil 564ec43, conversation 2026-11-22. -->

At the read-only review, no cached remote-tracking ref contained these commits
and remote availability had not been checked. The human subsequently authorized
committing and pushing the feature work. Wintap `123bd70` and PyUtil `564ec43`
are now pushed to `origin/feature/implement-sensor-fixes-and-cleanup-test-code`.
This updated handoff is included in the follow-up Analytics feature commit,
not in `0f8b414`; use the latest feature-branch tip and verify all three reviewed
commits are present on the destination. The Analytics publication result is
reported after the accompanying commit/push completes.
<!-- HUMAN-DECISION: conversation 2026-11-22 — commit and push all feature changes; preserve the previously excluded local artifacts. -->

The human explicitly excluded the local HostActivity binary, PyUtil keystroke
logs, and environment-config variants; they remain untouched. Wintap's two
`developer_docs/audits/wtc-*` records remain git-ignored local evidence under the
existing convention and need separate transfer. Verify destination commit
availability rather than assuming these local branches have been published.
<!-- HUMAN-DECISION: conversation 2026-11-22 — commit all feature changes, including the other session's test refactors; exclude unrelated local artifacts. -->

The private temporary Wintap source/hash manifest and one-off checker, and the
Python identity manifests, are not committed. Do not make their presence a
destination prerequisite or copy a Mac virtual environment onto another platform.
The five Wintap bodies can be compared against original paths in `123bd70^`
using git objects, removing only the two introduced trait lines for comparison.
If sensor code has advanced, use identical production sources on both sides of
any runtime organization baseline in separately approved storage; never reset
the shared worker checkout. Transfer the local audits separately if detailed
evidence is needed, but do not copy source into `raw/`.

## Test-Workstream Continuation Order

1. Confirm transferred commits, current dirty state, and worker ownership. The
   approved Wintap sharing arrangement is one feature checkout, not permission
   to switch branches or overwrite another worker's tests or sensor files.
2. In separate ready environments, use HostActivity's `tests/README.md` and
   PyUtil's `tests/README.md` for the 59-case app and 17-case representative checks;
   compare selected collection/marker identities where relevant. Do not substitute
   broad collection or the full coordination/compactor suite. Record any absent
   environment as a blocker; environment setup is a separately scoped step.
3. Keep the Windows gate open unless an appropriate Windows/SDK 10.0.402 runner
   actually builds, lists, filters, and executes the focused slice plus
   `WindowsFilePathEmissionTests`. The explicit static-draft exception is not a
   Linux pass or authority to split/retarget the assembly.
4. Obtain TC-03's concrete sensor/capture handoff before real-data validation.
   Run TC-04/TC-05 in small rounds with independent negative controls, and record
   producer, test/oracle, downstream, environment, or missing-evidence failures.
5. Later organization work remains bounded: Wintap execution tiers/harness controls
   or Analytics/PyUtil's remaining slices require the relevant plan and execution
   boundary review. No test deletion, assertion rewrite, full-suite selection
   change, or platform-project split is authorized by this transfer.

The sensor worker can use the separate prompt/backlog below; the test worker
should not select its TODO or start a collector on its behalf.

## Reviewed Nine-Item Backlog

Priorities below follow the individual intake pages; several are provisional.
Findings are recorded evidence/design candidates, not newly reproduced defects.

| Priority | TODO | Wintap work and boundary |
|---|---|---|
| P1 | [[wiki/todo/periodic-process-refresh-listing]] | Hourly running-process Refresh inventories, approximately `HH:05`, with observable collection time and stable identities. Linux can be implemented/qualified here; Windows parity requires its own runner. Settle timezone, offset, missed-tick, and disable semantics first. |
| P1 provisional | [[wiki/todo/linux-process-name-exe-fallback]] | Reproduce unresolved `/proc/<pid>/exe` fallbacks in exec/clone/rundown; choose trustworthy name/unknown semantics without fabricating paths. Historical repair is separate. |
| P1 provisional | [[wiki/todo/lintap-linux-process-command-line-quality]] | Improve bounded argument capture and provenance; distinguish unavailable/empty/truncated data and inherited parent context. Canonical argv/string contract and downstream DBT changes need review. |
| P1 provisional | [[wiki/todo/linux-process-executable-attribution]] | Distinguish fork, exec attempts, and successful image changes; preserve per-observation ordering. Deterministic paired name/path selection is PyUtil-owned, not solely a sensor fix. |
| P2 provisional | [[wiki/todo/transformer-five-tuple-connection-port-key]] | Investigate duplicated high-port input in shared `Transformer` connection-key generation. Prove port sensitivity/orientation and review persisted-ID compatibility before changing keys. |
| P2 provisional | [[wiki/todo/linux-nfs-process-network-attribution]] | Qualify initiating-task versus socket-owner meaning with controlled file/network observations. The observed NFS association is not yet a confirmed sensor bug. |
| P2 provisional | [[wiki/todo/linux-interactive-session-feed]] | Prototype a genuine Linux session lifecycle feed using logind, with optional PAM fallback. Event/API/schema, login-stack changes, and downstream consumption are not approved yet. |
| Untriaged | [[wiki/todo/listening-socket-capture-and-modeling]] | Define listener lifecycle/ownership and capture support; keep peerless listeners distinct from connected flows. Platform scope and shared/API/DBT contracts remain undecided. |
| Implemented; endpoint verification pending | [[wiki/todo/raw-sensor-upload-time-partition]] | Shared .NET S3 uploader now uses current UTC upload partitions with durable unresolved-attempt bindings, exact-key validation, and no second key after an inconclusive HEAD. Build passed; live endpoint qualification remains separate from DCC-E2E-01. |

The Linux sensor implementation is owned by Wintap, even where the intake title
says Lintap. Lintap owns supporting packaging; PyUtil/Wintappy owns canonical DBT;
Analytics owns this wiki and capture-analysis tools. Do not infer sibling-repo
write permission from a cross-repo dependency.

Excluded from this nine-item list: packaging-only and Analytics/PyUtil-only TODOs.
The OS-family queue item is primarily downstream, with a related Wintap Linux
host-metadata follow-up; it was not selected as a tenth item.

## Destination Startup and Transfer Checklist

1. Locate the actual Wintap, Analytics, and optional PyUtil/Lintap checkouts; do
   not assume path capitalization or historical sibling names on Linux. Read
   their current instructions before using repository commands.
2. Confirm revisions, active branches, tracked changes, and untracked files.
   The shared local branch is `feature/implement-sensor-fixes-and-cleanup-test-code`.
   Its original Wintap starting revision was `a418aa4`, not a requirement to
   reset or downgrade the destination. Do not switch/reset another worker's checkout.
3. Preserve existing work during transfer. At pre-commit handoff inspection,
   Wintap's five old top-level test paths appeared deleted
   with replacements under `tests/Wintap.Tests/Unit/` and a new README untracked.
   Analytics/PyUtil also have first-cut cleanup work. These are intended moves,
   not permission to discard files. The later commit checkpoint above supersedes
   that uncommitted feature state; untracked/ignored evidence still needs explicit
   transfer, and a fresh clone cannot see commits that have not been published.
4. Check the Linux distribution, architecture, kernel/BTF, .NET SDK, native
   filesystem output, and required eBPF tools against the selected build target.
   Wintap's declared baseline is SDK **10.0.402**. Do not install/upgrade tools or
   regenerate lockfiles as an implicit migration step.
5. Before a collector/workload run, obtain the concrete disposable host/process,
   privilege, duration, data/runtime/output roots, and read/mutation scope. Use
   explicit isolated roots; do not inherit operator data, S3 configuration, or
   a running collector's state. A field host is not automatically a dev checkout.
6. Re-read the selected TODO's live sources on the destination. The earlier review
   was a backlog review, not proof that its suspected defect exists in that revision.
<!-- GROUND_TRUTH: wiki/work/implement-sensor-fixes-and-cleanup-test-code/brief.md §Branches; ../wintap/global.json; ../wintap/BUILD_AND_TEST.md §Recommended Commands -->
<!-- SOURCE: Read-only branch/status inspection during handoff preparation, 2026-11-22; destination and transfer have not been verified. -->

## Primary Sources and Linux Execution Boundaries

- Start with Wintap `AGENTS.md`, `CLAUDE.md`, `BUILD_AND_TEST.md`,
  `devtools/README.md`, and current `wintap/Makefile`.
- Process: `wintap/platform/linux/sensor/ProcessRundownSensor.cs`,
  `ebpf/{ExecveSensor,CloneSensor}.cs`, `ebpf/helpers/{ProcReader,ProcessSensorHelper}.cs`,
  and the exec tracer files under that sensor tree. Read exact paths from the TODO.
- Network: `wintap/platform/linux/sensor/ebpf/NetworkSensor.cs` and
  `tracers/network_ops_tracer.bpf.c`.
- Shared keys/upload: `wintap/core/etl/transform/{Transformer,LoHi5Tuple,IdGenerator}.cs`
  and the load/adapter paths cited in the upload TODO.
- Shared event contract: `shared/WintapAPI/WintapMessage.cs`.

From the **Wintap repository root**, the current Makefile is `wintap/Makefile`:
`make -C wintap build_dotnet` builds `Lintap.csproj`, and
`make -C wintap build_ebpf` builds native tracers. These are proposed commands
for an authorized slice, not commands run in this handoff. Verify current targets
and dependencies first. `run-env` also depends on a build; it is not read-only
preflight. Use the Makefile's native-filesystem safeguards on shared mounts.
<!-- GROUND_TRUTH: ../wintap/wintap/Makefile §DOTNET_PROJ, build_dotnet, build_ebpf, run-env, shared-mount output handling -->

**Do not treat the current managed test project as a native Linux suite.**
`tests/Wintap.Tests/Wintap.Tests.csproj` targets a Windows-qualified TFM and
references `Wintap.csproj`, even though it links some Linux helpers. Linux
source/build checks cannot close the pending Windows build/discovery/runtime gate.
Do not retarget it, add projects, alter skips, or weaken assertions merely to
produce a Linux pass; agree the smallest appropriate test boundary first.
<!-- GROUND_TRUTH: ../wintap/tests/Wintap.Tests/Wintap.Tests.csproj §TargetFramework, ProjectReference, Compile; wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan.md §Approved First Draft and Deferred Gate -->

## First Small Slice and Evidence Loop

No first TODO has been chosen. Ask the human to select one and agree its scope,
compatibility constraints, test runner, budgets, and capture permissions. Prefer
one independently testable fix; coordinate overlapping process-name/arguments/
exec-provenance work without turning them into an unapproved combined rewrite.

Follow TC-03 through TC-05 in the existing implementation plan:

1. Establish the intended semantic contract and a focused negative regression.
2. Prepare one self-contained Wintap instruction for human approval, with exact
   files, test commands, and acceptance criteria; declare an unused unit abbreviation.
3. After approved implementation, run affected checks and capture a small fresh
   dataset with independent named-workload expectations.
4. Bind evidence to exact source/build/config, platform/enabled sensors, UTC
   interval, event families, schema/source layer, and explicit capture location.
   Keep normal ETL output distinct from diagnostic direct-Parquet bypass output.
5. Give the test session a sanitized TC-03 capture handoff. Separate producer,
   test/oracle, downstream, environment, and insufficient-evidence failures.
   Preserve the negative control and obtain a fresh capture after producer changes.

Existing test-cleanup results and deferred gates are in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]] and
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]].
Do not replace another session's round records or infer fresh capture acceptance
from earlier synthetic/static checks.

## Closeout and Remaining Decisions

- Record each approved unit's audit in Wintap; the Engineer updates the shared
  verification page, plan checklist, and `wiki/log.md` with scoped results/limits.
- Update only the selected TODO's disposition and promote durable semantics to
  canonical pages after qualification. Unselected TODOs remain open.
- Preserve process identity/birth time separately from observation time, existing
  payloads unless an explicit contract change is approved, and independent evidence.
- Dataset repairs, package changes, service deployment, PAM configuration, S3
  writes/deletion, new dependencies, commits/pushes, and broader platform acceptance
  need their own applicable authorization; none were performed by this handoff.
- Apply the canonical privacy rule in Analytics `AGENTS.md` to every persisted
  result; keep identifying raw output out of wiki artifacts.

Outstanding: first TODO/unit, destination revisions and transferred work,
development-host permissions, Linux test execution boundary, Windows parity plan
where needed, and any explicit PyUtil/Lintap implementation scope.
