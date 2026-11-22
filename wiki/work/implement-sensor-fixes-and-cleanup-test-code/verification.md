---
title: "Verification: Implement sensor fixes and cleanup test code"
type: concept
confidence: medium
grounded_by:
  - ../Wintap/tests/Wintap.Tests/README.md
  - ../Wintap/developer_docs/audits/wtc-01-first-slice-labels.md
  - ../Wintap/developer_docs/audits/wtc-02-five-mechanical-moves.md
  - streamlit/projects/HostActivity/tests/README.md
  - streamlit/projects/HostActivity/tests/contract
  - ../Wintap-PyUtil/tests/README.md
  - ../Wintap-PyUtil/tests/unit/config/test_config.py
  - ../Wintap-PyUtil/pyproject.toml
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan.md
policy: agent-editable
last_validated: 2026-11-22
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/HostActivity/tests; ../Wintap-PyUtil/tests; wiki/work/implement-sensor-fixes-and-cleanup-test-code
tags: [feature-work, testing, test-organization, verification, iterative-development]
---

# Verification: Implement sensor fixes and cleanup test code

## Round TC-02 / First Cut — 2026-11-22

Scope: Analytics HostActivity's three existing test modules and PyUtil's
configuration/four SQL modules. Actual macOS, existing separate project Python
environments, synthetic/local temporary inputs only. No sensor change or capture
was run. Both test repos are on the matching feature branch; Wintap's checkout
and Lintap remain unchanged. Changes are uncommitted and unpushed.

### Changes

- HostActivity: whole-file relocation to `tests/contract/`, discoverable packages,
  four application-file path adjustments, and test inventory/command documentation.
- PyUtil: configuration relocation to `tests/unit/config/`, `unit`/`contract`
  registration and module markers, and partial test inventory/command documentation.
- No assertion or fixture changes, test deletion/merge, full-suite selection change,
  source behavior change, dependency installation, or lockfile update.

### Test Commands

From `streamlit/projects/HostActivity/`, before changes:

```sh
.venv/bin/python -m unittest discover -s . -p 'test_*.py'
```

After changes:

```sh
.venv/bin/python -m unittest discover -s tests -t . -p 'test_*.py'
```

From `../Wintap-PyUtil/`, selected post-change execution:

```sh
.venv/bin/python -m pytest \
  tests/unit/config/test_config.py \
  tests/test_filetime_precision_sql.py::test_nonempty_file_and_registry_consumers \
  tests/test_filetime_precision_sql.py::test_nonempty_image_load_consumer \
  tests/test_network_activity_sql.py::test_mixed_spellings_are_counted_together \
  tests/test_process_gold_quality_sql.py::test_network_name_changes_keep_one_lifetime_and_conserve_counters \
  tests/test_selinux_sql.py::test_gold_preserves_family_rows_and_producer_counts \
  --strict-markers -q
```

The same 17-case selection was run before changes using the old configuration path
and without `--strict-markers`. Collection checks used those five complete modules
with `--collect-only -q`, then post-change `--strict-markers` and separate
`-m unit` / `-m contract` filters. No full main or compactor collection was attempted.
Commands had a 120-second ceiling; one-off collection subprocesses had 60 seconds.

### Results

| Check | Before | After | Meaning |
|---|---:|---:|---|
| HostActivity execution | 59 passed, 2.775 s | 59 passed, 4.293 s | All affected application cases execute successfully. |
| PyUtil representative execution | 17 passed, 1.70 s | 17 passed, 2.26 s | Configuration and representative SQL consumers/imports work. |
| PyUtil selected collection | 224 cases | 224 cases | Collection, not full execution of all SQL cases. |
| PyUtil strict marker partition | Not classified | 4 unit + 220 contract | Disjoint complete partition of the selected slice only. |
| HostActivity normalized identities | 59 frozen | 59 identical | Only the module location prefix changed; no missing cases. |
| PyUtil normalized identities | 224 frozen | 224 identical | Only configuration's path changed; parameters/names preserved. |

One-off `unittest.TestLoader` checks confirmed new explicit discovery and legacy
project-root discovery return identical identities, with no forwarding copies or
duplicate cases. Before/after identities were compared using private temporary
JSON manifests; these are local development checks, not durable qualification
artifacts. Per-file counts and commands are retained in the test READMEs.

A source comparison against each repo's `HEAD` reversed only the four
application-path edits and five module-marker additions. All eight test module
bodies then matched exactly; all eight compiled via Python's `compile()` without
writing bytecode. `git diff --check` passed in both test repositories.

The documented focused command
`.venv/bin/python -m pytest tests/unit/config -m unit --strict-markers -q`
also passed all four configuration cases in 0.16 seconds. Required frontmatter
and new workflow links were checked across 13 changed/new wiki pages; the wiki
changes were reviewed for unauthorized identifiers.

Only existing non-failing Streamlit missing-context and width deprecation warnings
were observed. No failure was suppressed, test skipped, threshold changed, or
fallback broad run substituted.

## Known Gaps / Deferred Work

- Fresh sensor dataset validation has **not** started. No independent capture,
  completeness, lifecycle, platform, deployment, or production acceptance is claimed.
- HostActivity UI and synthetic transport coverage remain co-resident in the
  primary contract files; the first draft intentionally does not split assertions.
- PyUtil's four SQL modules are marked but not relocated; shared relative imports
  and the compacted-input renderer dependent need a later bounded move.
- Remaining application/validation, coordination/platform, isolated compactor,
  historical-evidence, and DBT suites were not executed or reorganized.
- Full-suite regression and resource/live-S3 qualification are deferred milestones,
  not inferred from these small checks.

## Next Iteration

Receive the sensor session's exact fix/revision, relevant event families, bounded
read-only capture, independent workload expectations, and known limitations. Then
select the corresponding validator/SmokeTests analysis check, run it explicitly
against the fresh data, classify failures, and refine tests in a recorded small
round. See TC-03 through TC-05 in
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan]].

## Wintap Extension / Initial Analysis — 2026-11-22

**Static inspection only.** Wintap's `develop` checkout at `06849b4` remained clean
and unchanged; the reserved feature ref remains at cached `a418aa4`. No fetch,
branch switch, source/test edit, SDK invocation, restore, build, discovery/execution,
collector run, or dataset read occurred. Existing Analytics/PyUtil changes and
unrelated untracked work were preserved.

Read-only inventory commands included `git status --short --branch`, `git ls-files`,
`git ls-tree -r --name-only <ref> -- tests`, `git rev-parse --short <ref>`, and
`git diff develop..feature/implement-sensor-fixes-and-cleanup-test-code -- tests`.
One-off Python source/AST scans counted attributes/methods and partitioned the
63 tracked C# files by behavior, with no imports of test modules or bytecode writes.

- One Windows-qualified xUnit project, 63 C# files, 451 Fact/135 Theory attributes,
  603 InlineData attributes, nine MemberData uses, six serialized collections.
- Corrected Category scan includes combined attributes: **26 files without any
  Category**, not the preliminary standalone-only count of 38. Per-case trait
  completeness is not established by a per-file scan.
- Seven Python control files contain 39 test methods by AST; neither Python nor
  xUnit runtime collection counts or pass results are claimed.
- The proposed five-file slice has a static expectation of 77 cases; its emission
  fixture consumer adds seven, for an expected focused gate of 84. Actual Windows
  discovery, source revision, and execution must establish the implementation gate.

Analysis and plan:
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis]] and
[[wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan]].
The platform-project question remains open in
[[wiki/tension/wintap-test-platform-boundaries]]. No Wintap approval/audit artifact
or implementation completion is inferred from filing these wiki pages.

Documentation checks: `git diff --check` passed. Python/XML validation confirmed
11 linked C# sources, six copied assets, and existing project/content references;
the three new pages have required frontmatter, valid wiki links, and no IP-shaped
values. New pages and the updated wiki content were reviewed for unauthorized
identifiers. These are documentation/static checks, not Wintap test results.

## Wintap wtc-01/wtc-02 / Static Draft — 2026-11-22

**Implemented, not runtime-accepted.** After approving the plan, the human
explicitly authorized deferring the Windows baseline and sharing the feature
checkout with the sensor implementation worker. This session switched Wintap's
clean `develop` checkout at `06849b4` to its existing feature branch at `a418aa4`;
no fetch or branch-ref update. A clean starting state and a private temporary
source/hash manifest were frozen before editing. The initial-analysis statements
above remain historical and do not describe this later implementation round.
<!-- HUMAN-DECISION: conversation 2026-11-22 — implement a static draft with Windows acceptance pending; share the feature checkout with the sensor worker. -->

### Changes and Ownership

- Added class-level `TestKind=unit` / `Execution=synthetic` to exactly five classes.
  All existing Category traits are unchanged; no `Category=wtc-*` tags were added.
- Moved the five approved files to the destinations in the Wintap plan. No
  forwarding copies, namespace/type/member changes, or fixture extraction.
- Added the partial test README and two static unit audits in Wintap. Updated
  shared workflow progress, navigation, and the current bootstrap-test path cite.
- No sensor code, dependencies/lockfiles, project/CI selection, skip policy,
  assembly-wide parallelization, collector/workload, or capture was changed/run
  here. Separate sensor-worker edits remain outside this session's ownership.

### Commands and Results

Preflight used `git status --short --branch`, `git worktree list --porcelain`,
`git log --oneline -3 feature/implement-sensor-fixes-and-cleanup-test-code`,
`git switch feature/implement-sensor-fixes-and-cleanup-test-code`, and
`dotnet --list-sdks`. Only SDK **8.0.122** is available locally on macOS;
`global.json` requires **10.0.402**. No restore, build, C# compilation,
xUnit discovery, adapter filtering, or managed test execution was attempted.

One-off Python static comparisons ran before and after the moves; manifest/checker
live only in private temporary storage, not in `raw/` or the committed wiki.
Generic command form, run from Wintap's root:

```sh
python3 <private-temp>/verify_wtc_static.py . <private-temp>/baseline.json
git diff --check
```

| Static check | Observed result |
|---|---|
| Five labeled/relocated source bodies | Exact baseline bytes after removing only the two new trait lines per class. |
| Historical categories, method names/data, assertions, fixture members | Preserved by that whole-source equality, not runtime discovery. |
| Emission neighbor and `Map` dependency | Neighbor byte-identical; namespace/type/member reference preserved. |
| C# inventory | 63 files, no old/forwarding copies; all 58 unmoved files byte-identical. |
| Build/dependency/CI inputs | All 33 frozen inputs byte-identical; XML/JSON parse checks pass. |
| Explicit project paths | 11 linked C# sources, six copied assets, two project references resolve; actual SDK glob evaluation remains pending. |
| New source-trait partition | Exactly five reviewed classes; lexical expectation 36 methods / 77 cases. |
| Focused lexical inventory including neighbor | 39 methods / 84 expected cases; not collected or executed counts. |
| Diff whitespace | Passed in Wintap; new untracked files reviewed separately. |

Static source preservation is useful draft evidence, but does not establish that
the Windows assembly builds or that the adapter discovers/filters/executes it.
Both wtc units remain open for runtime acceptance. Audits:
`../Wintap/developer_docs/audits/wtc-01-first-slice-labels.md` and
`../Wintap/developer_docs/audits/wtc-02-five-mechanical-moves.md`.

Documentation checks passed across 19 changed/new wiki Markdown files: 17 required
YAML frontmatters, grounding paths, 470 resolving wikilinks, and whitespace.
The complete tracked wiki diff and new pages were reviewed for unauthorized host,
account, and address identifiers; added material has no IP-shaped or real
home-directory values. All eight new/moved Wintap files also pass direct
whitespace/final-newline checks, including the two audits.

Two initial documentation-check attempts needed correction: HostActivity's venv
has no YAML parser, so validation used the existing PyUtil venv without installing
anything; a git-inventory assertion incorrectly expected the audits to be
untracked. `git check-ignore -v` confirms existing `.gitignore` excludes
`developer_docs/`, so the audits were checked directly and remain **local,
git-ignored evidence**. No ignore-rule change or force-add was made; transfer
these records separately when handing off runtime verification.

### Pending Runtime and Capture Gates

Use the test README's SDK 10.0.402 Windows build/list/focused commands with a
120-second initial ceiling per command. Confirm the 84-case focused gate, the
77-case combined classification filter, unfiltered discovery, and old Category
membership using actual adapter evidence; record failures/skips/expansion limits.
If a locked restore is needed, schedule it explicitly without regenerating locks.

Because the checkout is shared with sensor work, obtain a genuine before/after
baseline in separately approved storage with **identical production sources**;
only reverse this session's traits/moves there. Never reset/switch the shared
worker checkout or infer organization compatibility from different sensor builds.
Fresh-capture handoff and TC-03 through TC-05 remain pending independently.
No commit or push was made; existing Analytics/PyUtil and unrelated work remain
preserved.

## Commit Preparation Checkpoint — 2026-11-22

At the human's request, reviewed and staged both sessions' feature changes across
Analytics, Wintap, and PyUtil; unrelated local binary/log/config artifacts were
explicitly excluded and preserved.

- Re-ran the TC-02 commands above: HostActivity **59 passed in 2.274 s**;
  PyUtil's representative selection **17 passed in 1.26 s**, with no skips.
- All three staged diffs pass `git diff --cached --check`; all five staged Wintap
  moved source bodies match their original `HEAD` bytes after removing only the
  two new trait lines. No managed build/discovery/execution was attempted.
- Validated 19 staged wiki pages with the existing PyUtil YAML environment;
  all 470 wikilinks resolve. Reviewed complete staged diffs and scanned added
  wiki content for identifier-shaped values; no unauthorized additions found.
- Wintap committed as `123bd70`; PyUtil as `564ec43`. Analytics work and this
  checkpoint are included in their accompanying feature commit. No push occurred.
- Wintap static audits remain git-ignored local evidence; transfer them separately.
  Windows runtime acceptance and fresh sensor captures remain open.
<!-- HUMAN-DECISION: conversation 2026-11-22 — commit both sessions' feature changes across the three repos, excluding unrelated local artifacts. -->
