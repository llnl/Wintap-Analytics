---
title: "Initial Plan: Wintap Test Cleanup"
type: concept
confidence: medium
grounded_by:
  - ../Wintap/tests/Wintap.Tests/README.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan.md
  - ../Wintap/CLAUDE.md
  - ../Wintap/tests/Wintap.Tests/Wintap.Tests.csproj
  - ../Wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs
  - ../Wintap/.github/workflows/release.yml
policy: agent-editable
last_validated: 2026-11-22
repo_scope: wintap
implementation_area: windows-sensor
event_domain: cross-domain
audience: developer
status: draft
source_paths: ../Wintap/tests/Wintap.Tests; ../Wintap/devtools; wiki/work/implement-sensor-fixes-and-cleanup-test-code
tags: [feature-work, testing, xunit, iterative-development, implementation-plan]
---

# Initial Plan: Wintap Test Cleanup

## Current Boundary and Historical First Draft

macOS/Linux feature testing and bounded Linux capture iterations are complete;
`Lintap.Tests` now exists. Native Windows acceptance remains separate. The original
first-cut procedure below is history, not a current static-only development limit.
Use stable .NET 10 and record the actual SDK; see the current handoff for next gates.

Start with inventory/traits and a five-file move **inside the existing Windows
project**. Do not split assemblies, rewrite tests, alter dependencies, or select
sensor fixes in the first cut. The human approved implementation, then explicitly
authorized a **static-checked draft with the Windows baseline deferred**, using
the shared feature-branch checkout with the sensor worker. The five classes now
have additive traits and are relocated; Windows runtime acceptance remains open.
The historical first-cut checkout started at `a418aa4`, refreshed from initial `06849b4`
analysis. Do not confuse this static source baseline with managed test discovery.
<!-- HUMAN-DECISION: conversation 2026-11-22 — proceed with implementation; defer the Windows baseline for a static draft and share the feature-branch worktree with the sensor worker. -->

Wintap unit abbreviation: **`wtc`**. No prior `wtc-<nn>` usage was found
in `developer_docs/` at implementation preflight. Under
Wintap's methodology, the human reviews one self-contained instruction in
`../Wintap/developer_docs/instructions/`, dispatches the Developer, and relays its
audit from `developer_docs/audits/`. No subagent was dispatched for this
human-directed draft. Static unit records are retained in Wintap audits; they
are not Windows runtime acceptance. Later slices retain their approval gates.
<!-- GROUND_TRUTH: ../Wintap/CLAUDE.md §The Methodology; §Unit naming convention -->

## Proposed Classification

Keep `Category` for existing instruction/provenance tags. Add two independent
xUnit trait keys, initially only to reviewed cases:

- `TestKind`: `unit`, `contract`, `integration`, or `qualification`.
- `Execution`: `synthetic`, `source`, or `native-workload`.

These map to the shared taxonomy in
[[wiki/overview/test-suite-organization-and-classification]]. Synthetic integration
can still be expensive or require isolated processes; `synthetic` is not a runtime
budget. Document the sensor subject/platform, actual runner OS, native libraries,
source assets, process-global state, command, and budget in a small test README.
Do not apply a file-wide label to mixed native/source/behavior cases.

Traits alone do **not** exclude native workloads from an unfiltered command.
Initially preserve full-suite and release-CI selection and document a positive
safe-slice filter. A later change must preserve native checks in a separately
named gate before changing any defaults or CI selection. Unclassified tests are
not silently treated as safe or discarded.

## wtc-01 — Baseline and First-Slice Labels

**Draft status:** partial inventory/labels implemented and source-compared.
Steps 2–5 and the runtime portion of step 7 were explicitly deferred, not passed.

1. Agree on the Wintap checkout/worktree with the sensor session; refresh this
   analysis's `06849b4` source baseline against the intended feature revision.
   Do not switch their checkout, update branch refs, or fetch without coordination.
2. On the agreed Windows runner, record revision/dirty state, SDK, configuration,
   existing assets, and build command. Use a stable .NET 10 SDK; a missing environment is
   a blocker, not permission to upgrade packages or install tools.
3. Build only the explicit test project with locked existing dependencies. If
   restore is needed, schedule a locked restore within the approved environment;
   do not regenerate committed lockfiles as part of organization work.
4. List tests using the built assembly; freeze fully qualified names, theory data
   identities where the adapter exposes them, and existing Category selections.
   Discovery can evaluate MemberData; record failures and limits. Do not execute
   the full assembly merely to establish inventory.
5. Execute the first slice plus its immediate neighbor before edits. Record actual
   counts/results, not the static expectation below.
6. Add a README with the partial inventory and commands, and add `TestKind=unit`
   / `Execution=synthetic` to the five reviewed classes. Retain all old Category
   values; adding a `Category=wtc-01` tag is additive, not a replacement.
7. Build, relist, and rerun that slice. Compare test names/data and old Category
   selections; only the new classification/provenance traits may change.

## wtc-02 — Five Mechanical Moves

**Draft status:** all five moves implemented and statically checked; actual SDK
inclusion, discovery, Category filtering, and focused runtime results are pending.

All paths below are relative to `../Wintap/tests/Wintap.Tests/`:

| Original file | Implemented destination | Static expanded expectation |
|---|---|---:|
| `WintapMessageTests.cs` | `Unit/Api/WintapMessageTests.cs` | 1 |
| `BoundedEventTimeCacheTests.cs` | `Unit/Shared/BoundedEventTimeCacheTests.cs` | 15 |
| `WindowsFilePathNormalizerTests.cs` | `Unit/Windows/File/WindowsFilePathNormalizerTests.cs` | 47 |
| `FileOpsAggregatorTests.cs` | `Unit/Linux/File/FileOpsAggregatorTests.cs` | 10 |
| `FileOpsDenyPolicyTests.cs` | `Unit/Linux/File/FileOpsDenyPolicyTests.cs` | 4 |
| **Moved slice** | | **77** |
| `WindowsFilePathEmissionTests.cs` — run, do not move | Immediate fixture consumer | **7** |
| **Focused execution expectation** | | **84**, subject to actual discovery |
<!-- GROUND_TRUTH: ../Wintap/tests/Wintap.Tests/Unit/Api/WintapMessageTests.cs; ../Wintap/tests/Wintap.Tests/Unit/Shared/BoundedEventTimeCacheTests.cs; ../Wintap/tests/Wintap.Tests/Unit/Windows/File/WindowsFilePathNormalizerTests.cs; ../Wintap/tests/Wintap.Tests/Unit/Linux/File/FileOpsAggregatorTests.cs; ../Wintap/tests/Wintap.Tests/Unit/Linux/File/FileOpsDenyPolicyTests.cs; ../Wintap/tests/Wintap.Tests/WindowsFilePathEmissionTests.cs -->

Keep namespaces, classes, method names/data, assertions, fixture members, assembly
name, target framework, and linked/content sources unchanged. Default SDK globbing
should compile relocated files; verify it through the actual build. No forwarding
copies, formatting sweep, shared-helper extraction, or production-source edits.
In particular, preserve `WindowsFilePathNormalizerTests.Map` for the emission test.

### Windows Runtime Commands — Pending

Run from the Wintap repo root after an approved, current build environment exists:

```powershell
dotnet build tests/Wintap.Tests/Wintap.Tests.csproj -c Release --no-restore
dotnet test tests/Wintap.Tests/Wintap.Tests.csproj -c Release --no-build --no-restore --list-tests

$slice = 'FullyQualifiedName~Wintap.Tests.WintapMessageTests|FullyQualifiedName~Wintap.Tests.BoundedEventTimeCacheTests|FullyQualifiedName~Wintap.Tests.WindowsFilePathNormalizerTests|FullyQualifiedName~Wintap.Tests.FileOpsAggregatorTests|FullyQualifiedName~Wintap.Tests.FileOpsDenyPolicyTests|FullyQualifiedName~Wintap.Tests.WindowsFilePathEmissionTests'
dotnet test tests/Wintap.Tests/Wintap.Tests.csproj -c Release --no-build --no-restore --filter $slice
```

Repeat the build/list/focused execution after each unit. `--no-build` is valid
only for binaries just built from the recorded source/configuration; never reuse
an unrelated output as proof. If listing omits expanded theory rows, supplement
with focused run results and source-data comparison rather than claiming a full
case-identity manifest. Confirm `TestKind=unit&Execution=synthetic` selects exactly
the five reviewed classes (expected 77 cases); the neighbor remains outside that
partition. Record the adapter's actual filtered discovery/run behavior.

If existing assets are missing, schedule
`dotnet restore tests/Wintap.Tests/Wintap.Tests.csproj --locked-mode` in the approved Windows
environment before building. Current commands and the classified filter are in
`../Wintap/tests/Wintap.Tests/README.md`. Because this checkout is shared with
sensor implementation, obtain a before/after baseline in a separate approved
checkout using identical production sources on both sides; only undo this
slice's traits/moves there. Comparing different sensor revisions does not isolate
test organization. Never reset or switch the shared worker checkout for a baseline.

Use a **120-second ceiling per command** initially; concurrency cases have unknown
cost until measured. A timeout requires a recorded blocker or separately approved
budget, not silent case removal or broad fallback execution. Keep normalizer
culture restoration and cache concurrency assertions unchanged.

**Acceptance:** build succeeds; focused baseline/post-change results agree and
pass; no unexpected skips or zero-match filters; old Category membership and
unfiltered discovery are preserved; no lost/duplicated methods/theory data;
diff/source-body checks show only approved traits, moves, and documentation.
Static 84 is an expectation, not a required fabricated runtime result.

## wtc-03 — Separate Execution Boundaries, One Group at a Time

- Label copied-source/repo-walking checks as source contracts. Keep content names
  and existing output placement; a portable source-root mechanism is a separate
  repair only if a real gate needs it.
- Classify native command/current-process probes at method level. Preserve
  `pai-06-command` and workload assertions; plan explicit supported/unsupported
  reporting instead of mistaking a non-Windows early return for coverage.
- Run MemoryMap/Esper/egress/registry/drive-map/global-state groups in separately
  named processes as required. Preserve collection fixtures and test data; record
  initialization order and cleanup limits before any fixture consolidation.
- Partition larger Windows process/reconciliation/resolver files only after mapping
  their different seams. Preserve old fully qualified identities where possible;
  record an explicit mapping if a reviewed split changes identities.
- Review release CI separately: a safe regression gate plus retained named native
  and isolated integration gates must cover the old selection before replacing it.

No assembly-wide parallelization change or new skip policy belongs in the mechanical
slice. A directory change alone must not be presented as fixing an isolation defect.

## wtc-04 — Python Harness Controls and Fresh-Capture Loop

1. Start with the isolated synthetic parser file via explicit discovery:
   `python3 -m unittest discover -s devtools -p test_event_name_contracts.py`.
   Other files need their own import/dependency and side-effect review; no broad
   `test_*.py` run in the first cut.
2. Separate native endpoint traffic and Linux subprocess workload from their
   synthetic evaluators without dropping the original workload gate. Keep manifest,
   RPM, source-drift, and actual-object checks distinct.
3. Use temporary explicit evidence/output roots. Review inherited
   `WINTAP_DATA_ROOT` and smoke export settings before running controls; do not let
   tests write operator data. Keep JSON-only controls dependency-light and preserve
   Parquet checks in their own existing DuckDB environment.
4. Receive the exact small sensor change/build, platform/config, immutable capture,
   UTC workload interval, event families, independent expected observations, and
   limitations from the sensor session (main plan TC-03).
5. Pair the relevant producer test with an explicit capture validator and, when
   affected, PyUtil's SQL contract. Distinguish raw capture, WintapAPI normalization,
   serializer output, and derived analytics. Do not compare different layers as
   though their row counts or timestamps had the same meaning.
6. Run the bounded capture check; classify failures as producer, test/oracle,
   downstream, environment, or missing evidence. Repair only the failing slice,
   preserve independent negative controls, then rerun and obtain a new capture
   when producer behavior changes. No blanket tolerance/threshold relaxation.

No existing TODO or unrelated sensor assertion is automatically selected. Use the
same small-round records and privacy rules as TC-03 through TC-05 in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan]].

## wtc-05 — Platform Topology and Evidence Review, Later

Ask the human to reconcile the accepted per-target convention with current shared
and linked Linux tests before creating projects. Retaining the current assembly
temporarily is the smallest first cut, not a reversal of that convention.
`Lintap.Tests` now exists and macOS/Linux feature testing is complete. Any further
platform topology change must design only the required project and
review compile/link ownership, Windows dependencies, internal visibility, copied
assets, solution/CI inclusion, and locked restore. No empty sibling scaffolding.

Review possible test duplication by behavior and replacement evidence, not names,
age, line counts, or use of reflection. Keep source guards and dated harnesses
until an approved replacement/provenance record exists. No deletion/archive is
authorized by this initial plan.

## Checklist and Handoff

- [x] Initial static inventory, execution-risk analysis, and staged plan filed.
- [x] Human approves the first-slice scope and shared feature checkout; explicitly
  defers Windows baseline for the static draft.
- [x] wtc-01 draft: partial inventory and additive first-slice labels, static comparison.
- [x] wtc-02 draft: five moves, unchanged-body/fixture/build-input static checks.
- [ ] wtc-01/wtc-02 acceptance: actual Windows baseline/build/discovery/filtering
  and focused before/after runtime verification.
- [ ] wtc-03: execution tiers and mixed/global-state cases reviewed in small rounds.
- [x] wtc-04: opt-in harness controls and bounded Linux fresh-capture iterations recorded.
- [ ] wtc-05: platform-project decision/evidence review only when needed.

Wintap Developer audits stay in Wintap; sanitized cross-repo status is summarized
in [[wiki/work/implement-sensor-fixes-and-cleanup-test-code/verification]]. If a
unit fails, repair/reverse only its own edits through the normal reviewed workflow;
never reset either repo or discard another session's work.
