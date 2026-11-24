---
title: "Verification: Implement sensor fixes and cleanup test code"
type: concept
confidence: medium
grounded_by:
  - ../wintap/tests/Wintap.Tests/README.md
  - ../wintap/developer_docs/audits/wtc-01-first-slice-labels.md
  - ../wintap/developer_docs/audits/wtc-02-five-mechanical-moves.md
  - streamlit/projects/HostActivity/tests/README.md
  - streamlit/projects/HostActivity/tests/contract
  - ../Wintap-PyUtil/tests/README.md
  - ../Wintap-PyUtil/tests/unit/config/test_config.py
  - ../Wintap-PyUtil/pyproject.toml
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/implementation_plan.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_analysis.md
  - wiki/work/implement-sensor-fixes-and-cleanup-test-code/wintap_test_plan.md
  - ../wintap/developer_docs/audits/sfx-02-process-observation-refresh.md
  - ../wintap/developer_docs/audits/sfx-03-linux-command-line-provenance.md
  - ../wintap/developer_docs/audits/sfx-04-linux-exec-observation-kind.md
  - ../wintap/developer_docs/audits/sfx-05-linux-executable-path-source.md
  - ../wintap/developer_docs/audits/sfx-06-linux-exit-code-status.md
  - ../wintap/developer_docs/audits/sfx-07-linux-stop-observation-timing.md
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/tests/test_network_activity_sql.py
  - ../Wintap-PyUtil/tests/test_rawutil_conn_id_passthrough.py
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md
  - ../wintap/developer_docs/audits/sfx-09-loopback-connection-context.md
  - validation/dataset-smoke/smoke_dataset.py
  - streamlit/projects/SmokeTests/tests/README.md
  - ../Lintap/packaging/lintap-deb/build-deb.sh
  - ../Lintap/tests/test_multipass_provisioning.py
  - ../Lintap/multipass-check-dev.sh
policy: agent-editable
last_validated: 2026-11-24
repo_scope: cross-repo
implementation_area: analytics
event_domain: cross-domain
audience: mixed
status: draft
source_paths: streamlit/projects/HostActivity/tests; streamlit/projects/SmokeTests/tests; validation/dataset-smoke; ../Wintap-PyUtil/tests; ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs; ../wintap/wintap/core/etl/load/adapters/base/S3UploadAttemptBinding.cs; ../wintap/tests/Wintap.Tests/S3UploadAttemptBindingTests.cs; wiki/work/implement-sensor-fixes-and-cleanup-test-code
tags: [feature-work, testing, test-organization, verification, iterative-development]
---

# Verification: Implement sensor fixes and cleanup test code

## SmokeTests Hour-Pruned Lazy S3 Discovery — 2026-11-24

Remote startup now lists only the known `raw_smoke_test` event family at exact UTC
`dayPK`/`hourPK` prefixes and loads its portable manifests. It does not enumerate
ordinary telemetry. Selected-run validation derives canonical event families from
that run's selector domains; all-canary validation derives them from the selected
round. Both list telemetry only after the corresponding explicit validation button.
Legacy day config remains accepted as a full-day expansion, while new
`start_hour`/`end_hour` bounds and sidebar controls allow an inclusive 1–744-hour
upload-partition window.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/s3_source.py §hour_range/§_discover_events/§discover_evidence_files/§discover_telemetry_files; streamlit/projects/SmokeTests/main.py §main; streamlit/projects/SmokeTests/page_views.py §test_page; streamlit/projects/SmokeTests/batch_views.py §canary_batch_page -->

This preserves upload-time semantics: the app does not infer S3 hours from event
timestamps, which could silently miss delayed publication. Operators choose an
explicit upload-hour window and are told to include adjacent hours. File caps still
fail closed; narrowing event family and hour reduces startup and validation scope
without treating omitted partitions as automatically complete.

Commands run with the app-local Python 3.13 requirements environment:

```sh
python -m py_compile s3_source.py main.py page_views.py batch_views.py
python -B -m unittest -v tests.contract.test_s3_source tests.ui.test_app
python -B -m unittest discover -s . -p 'test_*.py' -v
```

- Focused source/UI: **27/27 passed**.
- Full SmokeTests: **100/100 passed** in 3.217 seconds: 86 contracts, one loopback
  transport case, and 13 UI cases.
- `git diff --check` and direct Python compilation pass.

With explicit human authorization, a live configured read-only source check used the
standard credential chain without printing role, bucket, prefix, host, or object
identifiers. Exact evidence-hour discovery returned nine objects; all loaded into
three runs with zero evidence warnings. A default-page Streamlit AppTest against that
source completed with zero exceptions, zero UI errors, and one rendered metric. The
test did not modify S3 data or the private connection config. Explicit telemetry
validation and operator browser acceptance remain pending.

A subsequent operator-selected validation exposed the former 10,000-file listing
cap before telemetry reads began: each of three cross-domain runs selected the same
roughly 10,300-object full-day source set. The private config was atomically raised
to 20,000 and narrowed to an evidence-adjacent 11-hour upload window, reducing the
set to about 5,900 files. Canonical producer filename filtering by the manifest
hostname then reduced the selected-run read set to 635 objects. Schema preparation
completed with zero errors. The former 256 MB and trial 1 GB in-memory limits both
failed closed during working-set materialization; 4 GB completed evaluation of 17
cases with a yellow result rather than an infrastructure error. Disk spill remains
disabled. Checked-in defaults are now 20,000 files and 4 GB; hour/host narrowing is
preferred over repeatedly increasing either budget. No role, host, run, bucket,
prefix, or object identifier is retained here.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/RawSensorWriter.cs §ParseMergedFileName; streamlit/projects/SmokeTests/s3_source.py §load_config/§_host_candidates/§discover_telemetry_files; streamlit/projects/SmokeTests/page_views.py §test_page; streamlit/projects/SmokeTests/garage.example.json -->

## SmokeTests Staged Remote Diagnostics — 2026-11-24

The remote Streamlit path no longer labels every caught exception as an S3
credential/source failure. `main.py` tracks four bounded stages—connection,
listing, evidence loading and dashboard rendering—and renders only the stable stage,
exception class and stage-specific next checks. Raw exception text remains hidden
because SDK/DuckDB failures can include signed URLs, endpoint/object details or
connection SQL. The existing fail-closed listing behavior is unchanged.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/main.py §REMOTE_DIAGNOSTICS, remote_error, main; streamlit/projects/SmokeTests/tests/ui/test_app.py §DashboardTests -->

The UI regression now verifies connection and listing stage codes, no partial
result after listing refusal, and suppression of a synthetic private exception
string. Documentation adds requirements-only uv usage, explicit Python 3.13 to
avoid unsupported-wheel source builds, Windows PowerShell launch, EC2 instance-role
credential-chain behavior and regional AWS S3 endpoint shape.

Commands run from `streamlit/projects/SmokeTests/` with uv 0.13.9 and its Python
3.13 interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --python 3.13 --no-project \
  --with-requirements requirements.txt python -B -m unittest -v tests.ui.test_app
PYTHONDONTWRITEBYTECODE=1 uv run --python 3.13 --no-project \
  --with-requirements requirements.txt python -B -m unittest discover -s . -p 'test_*.py' -v
```

- Focused UI: **13/13 passed** in 12.990 seconds.
- Full SmokeTests: **99/99 passed** in 3.866 seconds, including 85 contracts,
  one loopback transport case and 13 UI cases.
- `git diff --check` and direct Python compilation pass.

The uv invocation materialized an ephemeral app dependency environment; it did not
change a lockfile or project environment. The transport test used localhost only.
No live S3, private dataset, collector, deployment or target Windows system was
accessed by this local verification. Target-system rerun is pending after push.

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

The current Linux tranche below permits destination checks and a small opt-in
dataset-readiness helper while the sensor capture is pending. For correctness,
receive the sensor session's exact fix/revision, relevant event families, bounded
read-only capture, independent workload expectations, and known limitations before
selecting the affected validator. See TC-LNX-01 through TC-LNX-04 and TC-03 through TC-05 in
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
`../wintap/developer_docs/audits/wtc-01-first-slice-labels.md` and
`../wintap/developer_docs/audits/wtc-02-five-mechanical-moves.md`.

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

## Linux Destination Readiness and Existing-Data Smoke — 2026-11-22

The human assigned test implementation/testing to this session, requested an
implementation plan and allowed no-heroics smoke reads of the existing RHEL 8
dataset while awaiting fresh sensor captures. No source/test implementation or
dependency installation was performed in this planning round.
<!-- HUMAN-DECISION: conversation 2026-11-22 — test-engineering continuation; bounded existing-data smoke, not dataset repair or sensor acceptance. -->

### Destination and Commands

Read-only `git status --short --branch` and `git log -1` checks confirm Analytics
`e6ff8ed`, Wintap `123bd70`, PyUtil `564ec43`, on matching feature branches.
Analytics's reviewed `0f8b414` is in its history. Analytics/Wintap are clean;
unrelated PyUtil untracked data/config artifacts were preserved. No switch/fetch.

Linux x86_64, kernel 4.18-series. System Python is 3.6.8. An explicit existing
HostActivity interpreter reports Python 3.13.13, DuckDB 1.5.6, Streamlit 1.67.0,
pandas 2.3.3, Altair 6.3.0 and boto3 1.44.0. PyUtil's expected `.venv/bin/python`
is unavailable despite the environment directory/config existing. Its declared
Python range excludes 3.13; no interpreter substitution or environment repair.
`dotnet` is not on PATH; no managed build/discovery/runtime gate was attempted.

HostActivity, from its project directory:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode \
  .venv/bin/python -B -m unittest discover -s tests -t . -p 'test_*.py'
```

The command ran through a stdlib subprocess wrapper with a 119-second deadline
and private temporary report. **59 tests passed in 6.535 s**, exit 0; no skips.
This is fresh destination evidence for the affected synthetic app slice, not a
new sensor or real-Parquet check. Existing non-failing Streamlit warnings remain
in the private report; no failures were suppressed.

Wintap, from its repository root:

```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode \
  python3 -m unittest discover -s devtools -p test_event_name_contracts.py
```

**7 tests passed in 0.002 s**, exit 0. This selection parses supplied strings,
not the live sensor tree or a running collector. It does not validate the five
relocated C# classes, Windows filtering or their 77/84 lexical expectations.

### Existing Dataset — Bounded Read-Only Probe

The human's relative path resolves under PyUtil:
`../Wintap-PyUtil/data/wintap-analysis/rhel8/`, containing `raw_sensor/` and
`duckdb/wintap.duckdb`. The local **raw directory has zero entries**. No broader
dataset search, download, sync or raw-Parquet query followed that finding.

A one-off `python -B -c` probe used the existing DuckDB 1.5.6 interpreter, with:

- `duckdb.connect(<existing-db>, read_only=True)`; missing DB/WAL checked first.
- External access, extension autoload and extension installation disabled;
  256 MB memory, one thread, no disk spill; 15-second interrupt timer and
  120-second command ceiling.
- `SELECT 1`; catalog query limited to 33 objects to detect a 32-object cap;
  `DESCRIBE` and `SELECT 1 ... LIMIT 128` on one process-related base table.
  No view, stored macro, raw row value, full-table count or join executed/printed.

| Observation | Result / limit |
|---|---|
| Read-only DB open and engine query | Passed with DuckDB 1.5.6. |
| Catalog | 24 objects: 14 base tables, 10 views; views not executed. |
| One selected base-table schema/sample | 6 columns, 0 sampled rows; readable but empty, not event evidence. |
| Input file check | Size/mtime/inode unchanged; WAL absent before/after. Not a full-file hash or snapshot guarantee. |
| Probe elapsed | 0.379 s. |
| Raw Parquet readiness | Unavailable: local raw directory empty. No schema/event validation occurred. |

The empty sample is not a statement about all database tables. Database lineage,
DBT correctness, raw/database parity, process/file/network semantics, producer
completeness and new-fix acceptance remain untested. Stop here rather than repair
or extensively audit the historical copy.

### Next Work and Blockers

The updated implementation plan selects TC-LNX-02's dependency-light opt-in smoke
helper and synthetic negative controls as the next implementation slice. It can
be developed without raw data or a sensor capture. PyUtil reruns require an
approved compatible environment; raw smoke requires available authorized files;
Windows acceptance requires its own SDK 10.0.402 runner. No S3, DBT build, collector,
workload, source/schema edit, dataset write, install, commit or push occurred.

Planning checks: `git diff --check` passes; Analytics ancestor check confirms
`0f8b414`. Stdlib checks find all required frontmatter fields on four changed
feature pages and 420 resolving wikilinks across six changed wiki files. The
complete diff was reviewed for unauthorized identifiers; added-content address,
account-path and email scans report none. The private test report was read fully.

## uv Readiness Follow-up — 2026-11-22

At the human's request, tried uv rather than assuming the missing PyUtil executable
meant a compatible Python was unavailable. `uv --version` reports **0.13.5**;
`uv python list --only-installed` finds installed **3.12.15** and **3.11.13**, both
within PyUtil's declared range, as well as the previously observed interpreters.

From PyUtil, with downloads disabled:

```sh
UV_PYTHON_DOWNLOADS=never PYTHONDONTWRITEBYTECODE=1 \
  uv run --locked --offline --no-sync --dev python -B -c \
  'import sys; print(sys.version.split()[0]); import duckdb, pytest'
```

**Blocked, exit 2:** uv selected Python 3.12.15, then attempted to recreate the
existing project environment and encountered permission denial at `.venv/lib`.
The Python/import check did not execute. No retry, deletion, ownership/permission
change, download or dependency installation followed. `--no-sync` is not a
guarantee that uv leaves an unusable interpreter environment untouched.

Separate `uv run --no-project --offline --no-sync --python <installed-python>`
checks successfully launch Python 3.12.15 and 3.11.13. Both lack `duckdb`, `pytest`,
`jinja2`, `yaml` and `dynaconf` by `importlib.util.find_spec`; no modules installed.
uv warns that `--no-sync` has no effect with `--no-project`; no dependency requests
were supplied. PyUtil's tracked status and unrelated untracked artifacts remain
unchanged; no claim is made about unfrozen ignored environment internals.

The blocker is now **project environment/dependencies**, not availability of a
compatible Python. Proposed next step: separately approved isolated uv environment
under `/tmp/opencode/`, using the existing lockfile and installed Python 3.12;
leave the old `.venv` untouched, then run the documented bounded PyUtil checks.

## Isolated uv Environment and PyUtil Destination Gate — 2026-11-22

The human approved a separate environment under `/tmp/opencode/`, using the
existing lockfile and leaving PyUtil's unusable `.venv` alone. The environment
uses installed Python **3.12.15**, DuckDB **1.5.6**, pytest **9.1.1**, Jinja2
**3.1.6** and Dynaconf **3.3.5**. Provisioning was offline from cached packages;
no Python download, dependency upgrade, editable project install, lockfile change,
repository source/test edit or dataset access.
<!-- HUMAN-DECISION: conversation 2026-11-22 — approve isolated uv environment and bounded PyUtil tests. -->

Provisioning command, from PyUtil (generic temporary environment path):

```sh
UV_PROJECT_ENVIRONMENT=<private-temp>/venv UV_PYTHON_DOWNLOADS=never \
  uv sync --locked --offline --python /usr/bin/python3.12 --dev \
  --no-install-project --link-mode symlink
```

The first attempt without `--link-mode symlink` fell back to copies across
filesystems and failed with no space left on the root filesystem. It created
about 477 MiB of partial temporary files. Removed **only this session's newly
created temporary venv**, not the old environment/cache or any system/user data.
The symlink retry installed 171 locked packages in 1.14 s with about 6.7 MiB of
environment metadata. Approximately 468 MiB of root space remained at readback;
do not use this as permission for large temporary artifacts. Cache symlinks make
this a local, cache-dependent environment, not a portable transfer artifact.

### Isolation and Identity Comparison

A one-off checker reconstructed the five original test files from `564ec43^` in
temporary storage, with symlinks to the unchanged current production SQL/package
sources. It verified exact source-body equality after removing only the added
module-marker lines, then ran pre/post collection in separate subprocesses.
Assertions, fixtures, parameters and production code were not modified.

Execution used a clean temporary working directory to avoid loading private
`wintappy_settings.toml`; any `WINTAPPY_*` variables were removed from child
environments. Explicit source `PYTHONPATH`, `-c <pyutil-root>/pyproject.toml`,
`--rootdir <selected-tree>`, `--strict-markers`, disabled external pytest plugin
autoload and `-p no:cacheprovider` kept the run small and isolated. Bytecode writes
were disabled. Each subprocess had a 119-second ceiling; no broad collection.

The first checker attempt collected 224 cases on both sides but omitted an
explicit baseline rootdir, causing pytest to display pathless snapshot identities.
The identity parser correctly refused that evidence before executing tests.
Preserved those reports; fixed only the temporary runner's rootdir and reran into
separate reports. This was a checker failure, not lost test coverage or a test fix.

### Results

| Gate | Result |
|---|---|
| Original five-module collection | 224 collected, 0.52 s. |
| Current five-module collection | 224 collected, 0.53 s; all normalized identities identical, no duplicates. |
| Unit marker collection | 4 selected / 220 deselected, 0.52 s. |
| Contract marker collection | 220 selected / 4 deselected, 0.53 s; disjoint union equals all 224 identities. |
| Documented representative execution | **17 passed**, 3.45 s, exit 0; no skips/failures. |
| Test/source/dependency freeze | All 375 checked inputs unchanged; includes selected tests, SQL sources, config/package entry points, lockfile and project manifest. |

Per-module collection is configuration **4**, FILETIME SQL **127**, network SQL
**76**, process-gold SQL **8**, SELinux SQL **9**. The 17-case selection is the
existing verification command's configuration and representative consumer nodes,
using the isolated interpreter and working-directory controls above. Private
identity/hash manifests and original/corrected reports remain temporary, not wiki
source copies or destination prerequisites. The complete execution report and
collection/partition manifests were reviewed.

PyUtil's tracked status and unrelated untracked data/config artifacts are
unchanged; lockfile/project git hashes equal their pre-provisioning values. The
old `.venv` received no further repair attempt. TC-LNX-01's selected Linux gate
is closed; **224 collected is not 224 executed passes**. At that checkpoint no raw
read, broader suite or DBT/S3 operation was performed. The RHEL path was later
confirmed as a one-time readiness sample, not a future raw-data acceptance gate.

## Bounded Dataset Readiness Helper — 2026-11-22

Implemented the explicit, opt-in TC-LNX-02 helper in
`validation/dataset-smoke/`. It requires a local dataset root and an existing
contained database, reports raw and database readiness independently, emits only
sanitized statuses/counts, and has no persistence output. Raw discovery is bounded
to 128 entries and one hour partition; selection is capped at three 32 MiB files
and 128 constant sample rows per file. Database access is read-only with external
access, automatic extension loading/installation and disk spill disabled; catalog,
memory, thread and query budgets are fixed. Stored views/macros are catalogued but
never executed.
<!-- GROUND_TRUTH: validation/dataset-smoke/smoke_dataset.py; validation/dataset-smoke/README.md -->

The synthetic command used the existing HostActivity DuckDB 1.5.6 interpreter,
an approved `/data` temporary root and a 120-second process timeout. **18/18**
controls pass in 2.484 seconds. They cover known readable/empty fixtures,
independent missing database/raw states, corrupt Parquet, external view/macro
non-execution, WAL refusal, escaping local paths and remote URLs, unchanged inputs,
sanitized output, explicit-hour/family/row selection, and shared command plus
discovery/file/catalog/query budgets.
Default discovery references synthetic fixtures only.
<!-- GROUND_TRUTH: validation/dataset-smoke/test_smoke_dataset.py -->

The separately invoked helper reported the authorized RHEL snapshot honestly:

| Input | Bounded result |
|---|---|
| Raw Parquet | `empty`: zero finalized files selected; process, file and network explicitly missing. |
| Built DuckDB | `readable`: 24 catalog objects, 14 base tables, 28 inspected columns and 5 constant sample rows from one deterministic base table. |
| Mutation check | Database size, mtime and SHA-256 unchanged before/after; no WAL was present. |

Private command logs and hashes remain outside Git under the approved sensor-fix
evidence root. The empty raw result is not event evidence. The human confirmed this
was strictly an existing sample directory used to bootstrap implementation; it
will not be updated, and no future raw-Parquet read from it is required. The
database sample does not
claim sensor completeness, DBT correctness, raw/database parity, data quality or
historical repair. No network, S3, DBT, deployment, dependency installation or
dataset mutation occurred.
<!-- HUMAN-DECISION: conversation 2026-11-22 — the existing RHEL sample directory will not be updated and must not remain an acceptance gate. -->

## SmokeTests Query/Quality Mechanical Slice — 2026-11-22

Completed the first TC-LNX-03/TC-06 SmokeTests slice. The two complete offline
query/quality modules moved from the project root into
`streamlit/projects/SmokeTests/tests/contract/`; package markers and a focused
inventory/command README were added. The project README now points to that focused
34-case command. No assertion, fixture, test/class name, production query, package
dependency or project-wide default command changed. Root-level analysis,
persistence, S3, HTTP and Streamlit app/page modules remain untouched.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/tests/contract/test_queries.py; streamlit/projects/SmokeTests/tests/contract/test_quality.py -->

The bounded before/after command used the existing DuckDB 1.5.6-capable
HostActivity interpreter only for these dependency-light modules, with temporary
files and logs under `/data` and a 120-second ceiling. This was not a SmokeTests
project environment or full-project execution; no environment was provisioned.

| Gate | Before | After |
|---|---:|---:|
| Focused execution | **34 passed**, 2.920 s | **34 passed**, 2.629 s |
| Selected identities | 34 unique | 34 unique; normalized set/order identical |
| Duplicate selected identities | 0 | 0 |
| Moved bodies and `queries.py` | Frozen SHA-256 | Byte-for-byte identical |

Focused legacy project-root discovery also finds the 34 moved cases exactly once;
there are no forwarding copies. Full SmokeTests discovery/execution still requires
a separately approved compatible project environment. No network, private dataset,
collector, S3, DBT, dependency installation, assertion weakening, commit or push
occurred.

## SmokeTests Analysis/Store Mechanical Slice — 2026-11-22

Completed the second TC-06 SmokeTests slice by moving the complete synthetic
round-analysis and summary-store module into
`streamlit/projects/SmokeTests/tests/contract/`. The test inventory and project
README now describe a 56-case contract package. The cross-repo durable producer
contract and root-level S3 source/HTTP and Streamlit app/page modules remain
untouched. No assertion, fixture, class/method name, production source, dependency
or project-wide default command changed.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/tests/contract/test_analysis.py -->

The selected before/after execution again used the existing DuckDB/Boto3-capable
HostActivity interpreter as a bounded dependency control, not a provisioned
SmokeTests environment or full-project run. Temporary files and reports stayed
under `/data`; both commands had a 120-second ceiling.

| Gate | Before | After |
|---|---:|---:|
| Analysis/store module | **22 passed**, 1.882 s | **22 passed**, 1.759 s |
| Selected identities | 22 unique | 22 unique; normalized set/order identical |
| Duplicate selected identities | 0 | 0 |
| Test plus five immediate source/import files | Frozen SHA-256 | Byte-for-byte identical |
| Classified contract package | 34 cases in prior slice | **56 passed**, 3.032 s |

Focused legacy project-root discovery finds the moved module's 22 cases exactly
once, without a forwarding copy. No network request, live S3, collector, private
dataset, producer execution, DBT, dependency installation, assertion change,
commit or push occurred.

## SmokeTests Synthetic S3-Source Mechanical Slice — 2026-11-22

Completed the third TC-06 SmokeTests slice by moving the complete synthetic S3
configuration/listing/source module into
`streamlit/projects/SmokeTests/tests/contract/`. Its existing local publish helper
continues to create only temporary synthetic Parquet. The dependent analysis test
received one package-relative `Paginator` import adjustment. The inventory and
project README now describe a 69-case package. The root-level durable-producer,
opt-in loopback HTTP and Streamlit app/page test modules remain separate.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/tests/contract/test_s3_source.py; streamlit/projects/SmokeTests/tests/contract/test_analysis.py -->

The before/after runs used the existing HostActivity interpreter as a bounded
dependency control. `SMOKE_S3_HTTP_TEST` was explicitly unset, all temporary files
and reports stayed under `/data`, and each test command had a 120-second ceiling.

| Gate | Before | After |
|---|---:|---:|
| Synthetic S3-source module | **13 passed**, 2.561 s | **13 passed**, 1.893 s |
| Selected identities | 13 unique | 13 unique; normalized set/order identical |
| Duplicate selected identities | 0 | 0 |
| Moved test body | Frozen SHA-256 | Byte-for-byte identical |
| Four supporting source files | Frozen SHA-256 | Byte-for-byte identical |
| Dependent analysis module | Frozen SHA-256 | Only package-relative helper import changed |
| Classified contract package | 56 cases in prior slice | **69 passed**, 3.487 s |

Focused legacy project-root discovery finds all 13 moved cases exactly once,
without a forwarding copy. No HTTP test, socket request, live S3, AWS profile,
private dataset, collector, durable-producer test, DBT, dependency installation,
assertion change or push occurred.

## SmokeTests Durable-Producer Mechanical Slice — 2026-11-23

Completed the fourth TC-06 SmokeTests slice by moving the complete 11-case durable
producer/Parquet contract into `streamlit/projects/SmokeTests/tests/contract/`.
The live Wintap producer-helper path changed only for the additional directory
depth. Three dependent tests now import the moved module through its package path.
No assertion, fixture, class/method name, production source, dependency, or
project-wide default command changed. Root-level Streamlit app/page and opt-in
loopback HTTP execution remain separate.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/tests/contract/test_durable.py; streamlit/projects/SmokeTests/tests/contract/test_s3_source.py; streamlit/projects/SmokeTests/tests/ui/test_app.py; streamlit/projects/SmokeTests/tests/transport/test_s3_http.py -->

The before/after runs used the existing HostActivity interpreter as a bounded
DuckDB dependency control. `SMOKE_S3_HTTP_TEST` was explicitly unset, all temporary
files and reports stayed under `/data`, and each command had a 120-second ceiling.

| Gate | Before | After |
|---|---:|---:|
| Durable module | **11 passed**, 1.188 s | **11 passed**, 1.017 s |
| Selected identities | 11 unique | 11 unique; normalized set/order identical |
| Duplicate selected identities | 0 | 0 |
| Durable test body | Frozen SHA-256 | Byte-for-byte identical after normalizing the required parent-depth path |
| Classified contract package | **69 passed**, 2.254 s | **80 passed**, 2.797 s |
| Project-root discovery | Not changed | 98 cases discovered; all 11 durable identities appear exactly once |

Python compilation and `git diff --check` pass. No HTTP/UI test execution, socket
request, live S3, private dataset, collector, dependency installation, assertion
change, commit, or push occurred. Evidence and checksums are under
`/data/lintap-compactor/sensor-fixes/tc-06-durable-20261123/`.

## SmokeTests Page-Query Mechanical Slice — 2026-11-23

Completed the fifth TC-06 SmokeTests slice by moving the complete 5-case page
query/materialization contract into `streamlit/projects/SmokeTests/tests/contract/`.
The moved file is byte-for-byte identical; no import, assertion, fixture,
class/method name, production source, dependency, or default command changed.
Actual Streamlit AppTest behavior remains in the root-level UI module.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/contract/test_pages.py; streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/README.md -->

| Gate | Before | After |
|---|---:|---:|
| Page-query module | **5 passed**, 0.129 s | **5 passed**, 0.141 s |
| Selected identities | 5 unique | 5 unique; set/order identical |
| Duplicate selected identities | 0 | 0 |
| Moved test body | Frozen SHA-256 | Byte-for-byte identical |
| Classified contract package | **80 passed**, 2.890 s | **85 passed**, 2.948 s |
| Project-root discovery | Not changed | 98 cases discovered; all 5 page-query identities appear exactly once |

Python compilation and `git diff --check` pass. No HTTP/UI test execution,
network request, live S3, private dataset, collector, dependency installation,
assertion change, commit, or push occurred during the mechanical move. Evidence
and checksums are under
`/data/lintap-compactor/sensor-fixes/tc-06-page-query-20261123/`.

## SmokeTests Default-On Loopback HTTP — 2026-11-23

Per human direction, `SMOKE_S3_HTTP_TEST` now defaults to enabled. Explicit
case-insensitive false-like values `0`, `false`, `no`, and `off` skip the test.
The project documentation records both the default and opt-out. The test remains
synthetic, read-only, and loopback-only; it does not become Garage, TLS,
authorization, external S3, or multi-host acceptance.
<!-- HUMAN-DECISION: conversation 2026-11-23 — make SMOKE_S3_HTTP_TEST default true with explicit opt-out. -->
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/transport/test_s3_http.py; streamlit/projects/SmokeTests/README.md -->

The matching DuckDB 1.5.6 `httpfs` extension was already cached. With the variable
unset, the focused localhost case passes **1/1** in 1.945 seconds. With
`SMOKE_S3_HTTP_TEST=0`, the same case is discovered and explicitly skipped. A
direct environment-contract check confirms the unset/default and all four
false-like values. The full project-wide default command passes **98/98** in
7.612 seconds, including 12 Streamlit AppTest cases, the localhost transport case,
and all 85 classified contracts.

No dependency installation, external network/S3/private-data access, collector,
deployment, historical mutation, commit, or push occurred. Temporary files and
evidence remained under
`/data/lintap-compactor/sensor-fixes/tc-06-s3-http-default-20261123/`.

## SmokeTests Transport Mechanical Slice — 2026-11-23

After milestone commit `7056bed`, moved the byte-identical default-on localhost
HTTP test from the SmokeTests project root into `tests/transport/`. Added only the
package marker and updated focused commands; no test body, identity, assertion,
fixture, production source, dependency, or default project selection changed.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/transport/test_s3_http.py; streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/README.md -->

| Gate | Before | After |
|---|---:|---:|
| Default-on transport module | **1 passed**, 1.772 s | **1 passed**, 1.378 s |
| Explicit opt-out | Previously verified | 1 discovered / 1 skipped |
| Selected identities | 1 unique | 1 unique; identical and present exactly once |
| Moved test body | Frozen SHA-256 | Byte-for-byte identical |
| Project-wide default | **98 passed**, 7.486 s | **98 passed**, 7.530 s |

Project discovery reports the sole identity under
`tests.transport.test_s3_http`. Python compilation and `git diff --check` pass.
Only the loopback HTTP server ran; no external network/S3/private-data access,
dependency installation, collector, deployment, historical mutation, or push
occurred. Evidence is under
`/data/lintap-compactor/sensor-fixes/tc-06-transport-20261123/`.

## SmokeTests UI Mechanical Slice — 2026-11-23

Moved the complete 12-case Streamlit AppTest module into `tests/ui/`. The only
test-body edits replace three former same-directory `main.py` paths with the
equivalent project-root path required by the new depth. Assertions, fixtures,
class/method names, production sources, dependencies, page paths, and project-wide
default selection are unchanged.
<!-- GROUND_TRUTH: streamlit/projects/SmokeTests/tests/ui/test_app.py; streamlit/projects/SmokeTests/tests/README.md; streamlit/projects/SmokeTests/README.md -->

| Gate | Before | After |
|---|---:|---:|
| Streamlit AppTest module | **12 passed**, 4.227 s | **12 passed**, 4.087 s |
| Selected identities | 12 unique | 12 unique; set/order identical and each present once |
| Test body | Frozen SHA-256 | Identical after normalizing the required `main.py` path-depth change |
| Classified contract package | 85 cases | **85 passed**, 2.827 s |
| Project-wide default | **98 passed**, 7.674 s | **98 passed**, 7.342 s |

Project discovery reports all UI identities under `tests.ui.test_app`. The final
SmokeTests tree contains 85 contract, one transport, and 12 UI cases with no
project-root forwarding modules. Python compilation and `git diff --check` pass.
No external network/S3/private-data access, dependency installation, collector,
deployment, historical mutation, commit, or push occurred in this downstream
slice. Evidence is under
`/data/lintap-compactor/sensor-fixes/tc-06-ui-20261123/`.

## First Sensor-Fix Batch Source Qualification — 2026-11-22

The uncommitted Wintap candidate on
`feature/implement-sensor-fixes-and-cleanup-test-code` combines:

- `sfx-01` Linux executable-name repair and normal-ETL selected-name projection;
- additive process observation UTC/raw-monotonic/clock/run fields plus propagated
  envelope `ReceiveTime`, without changing birth `EventTime` or `PID_HASH`; and
- UTC-aligned periodic Linux/Windows Refresh, enabled by default hourly at `HH:05`,
  with missed-tick/overlap suppression and disposal synchronization.

Windows scheduling starts only after startup bootstrap/replay/snapshot-delta has
been attempted and periodic inventory never clears or reconciles startup state.
Linux scheduling starts after successful rundown. Full `EventTime` migration,
argv/lifecycle redesign, historical repair and PyUtil changes remain deferred.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/wintap/core/infrastructure/PeriodicProcessRefreshScheduler.cs; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/WindowsProcessSensor.cs -->

All build, scratch, log and result files for this batch are outside Git under
`/data/lintap-compactor/sensor-fixes/sfx-batch-20261122/`. SDK 10.0.402 was invoked
explicitly.

| Gate | Result |
|---|---|
| Pre-live focused Linux/synthetic suite | **63 passed / 0 failed / 0 skipped** (`lintap-focused-final.trx`). |
| Preserved earlier focused results | 60/3, then 62/1; retained as non-acceptance evidence before the final fix. |
| New Windows periodic synthetic case | **1 passed / 0 failed** (`wintap-periodic-synthetic.trx`) on Linux. |
| Authorized bounded Linux `live-01` | All three process sensors registered; two periodic inventories began; capture and graceful shutdown completed; no gate-owned process remained. |
| Multi-exec live assertions | **8/8** for paired clone/exec observations, stable birth/hash/run scope, complete UTC/raw timing, strict observation ordering, and executable-derived names. |
| Stable-process Refresh assertions | Three rows retained one birth/hash/run scope and three UTC scan observations; one absent monotonic value incorrectly materialized as `0`, retaining `live-01` as defect evidence. |
| Post-live direct-Parquet repair | Focused observation tests **8/8** and expanded Linux/synthetic suite **65/65** (`lintap-focused-after-live-repair.trx`). |
| Repaired-binary Linux `live-02` | **18/18** aggregate acceptance checks pass; all three sensors registered, two periodic inventories completed, graceful shutdown completed, and no gate-owned process remained. |
| Repaired timing output | All 1,312 Refresh rows have userspace UTC and null monotonic timing; all 4,988 Start rows have UTC and nonzero kernel-monotonic timing. Stable anchor is 3/3 null, never numeric zero; multi-exec remains 8/8 across all six gates. |
| Per-file direct schema | Both timing fields are optional `INT64`/`BIGINT` in **124/124** Parquet files; no active/zero-byte output, error/fatal/drop/backlog entry, or artifact hash change was found. |
| Repeat stress | Linux/synthetic suite **1,300/1,300** across 20 isolated runs; Linux-hosted Windows periodic synthetic contract **30/30** across isolated runs. |
| Repaired Linux non-incremental Release build | 0 errors / 173 warnings. |
| Windows-targeted non-incremental Release cross-build | 0 errors / 87 warnings with `EnableWindowsTargeting=true`; compile evidence only. |
| Broader Linux-hosted `Category=wpc-10` | 103 passed / 13 failed of 116; **not acceptance evidence**. Nine failures are replay-overlap identity expectations, three are other replay/lifecycle expectations, and one is unsupported Windows SID functionality on Linux. |
| Source checks | `git diff --check` passes; full tracked/new-file scope and privacy review completed. |

The focused tests cover name evidence and ETL projection, sub-FILETIME raw
ordering, honest UTC-conversion failure, repeated Refresh identity/scan timing,
normal/direct Parquet projection, null-first/populated-first schema stability,
UTC boundary/custom interval/disabled scheduling, overlap suppression and shutdown
waiting. Synthetic identifiers only are present in Git-bound additions. Generated
TRX runner identifiers remain in the external evidence root and were not copied
into persistent documentation.

The separately authorized `live-01` gate read 5,254 process rows from its isolated
direct-Parquet output. It loaded only process rundown/exec/clone, used a local
synthetic workload, and performed no network, S3, or DBT activity. The retained
defect showed that a null Refresh monotonic value could become numeric `0` when a
kernel-timed row established the batch schema. The repair keeps absent direct
timing keys and recognizes both normal and `Process_`-prefixed nullable timing
fields during schema inference.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/DirectParquetSink.cs §DirectParquetProjection; ../wintap/wintap/core/etl/load/ParquetWriter.cs §DetermineSchemaFromExpando; ../wintap/tests/Lintap.Tests/ProcessObservationTimingTests.cs -->

Bounded Linux acceptance is complete: `live-01` remains immutable defect evidence
and `live-02` is the repaired-output evidence. Native Windows SDK 10.0.402 execution
remains open; Linux acceptance does not substitute for that platform gate or imply
deployment/historical repair. No commit or push occurred. Full details:
`../wintap/developer_docs/audits/sfx-02-process-observation-refresh.md`.

## sfx-03 Linux Command-Line Provenance — 2026-11-22

The next bounded sensor unit adds `CommandLineSource` and
`CommandLineCaptureStatus`, classifies procfs outcomes, limits reads to 256 KiB,
and removes clone's parent-command-line fallback. It retains the rendered string
contract and does not change birth/hash, resolver, executable-name/path evidence,
observation timing or `PROC_START_SRC` semantics. Structured argv, BPF argv,
exec-result correlation, PyUtil/DBT and historical repair remain deferred.
The implementation is committed locally in Wintap as `2d304d1`; nothing was pushed.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs -->

| Gate | Result |
|---|---|
| Preserved baseline | **65/65** `sfx-01|sfx-02`. |
| Focused command-line contracts | **6/6**. |
| Final combined sensor-fix suite | **71/71**, no failures/skips. |
| Non-incremental Linux Release build | **0 errors / 173 warnings** with SDK 10.0.402. |
| Bounded process-only live gate | Exec/clone/rundown registered, two periodic inventories completed, graceful shutdown, no owned process left. |
| Live acceptance | **28/28** aggregate assertions across 5,937 process rows and 113 files. |
| Controlled command lines | **8/8** repeated-exec cases preserve captured space-bearing values at both image stages; all **24/24** cleared-argv children are `empty`, with zero parent-sentinel values. |
| Quality/schema | Every row has `procfs-cmdline` and an allowed status; value/status consistency passes; all 113 files carry command-line/source/status and optional timing fields. |
| Compatibility | Birth/hash/run scope, executable name/path, Start timing and Refresh timing remain valid. |

Four status classes occurred live: 2,990 captured, 1,189 empty, 1,687 unavailable
and 71 read-error; bounded truncation is covered synthetically. One first-batch
file omitted the pre-existing nullable `Process_Arguments` column, removing source
breadcrumbs from three observations in one repeated-exec case. Source-specific
ordering is therefore available for 7/8 cases, while all five Start rows, image
ordering, identity/timing/name/path and the new fields remain valid in 8/8. That
generic first-row schema limitation is not silently treated as command-line failure
or expanded into a broad repair in this unit.

Private capture, raw identifiers, generated run IDs and hashes remain under the
approved `/data` evidence root. No network, S3, DBT, deployment, dependency
installation, historical-data mutation or push occurred. Full evidence:
`../wintap/developer_docs/audits/sfx-03-linux-command-line-provenance.md`.

## sfx-04 Linux Exec Observation Kind — 2026-11-22

The bounded next sensor unit adds nullable `ExecutionObservationKind` without
changing existing Start rows or identity. Linux exec syscall entry is
`exec_attempt`; scheduler-confirmed image installation is `exec_success`. Clone,
Refresh and unsupported producers stay null. Existing path/name evidence,
command-line provenance, timing and `PROC_START_SRC` remain unchanged.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs; ../wintap/wintap/core/etl/extract/ProcessSerializer.cs -->

| Gate | Result |
|---|---|
| Frozen baseline | **71/71** `sfx-01|sfx-02|sfx-03`. |
| Focused contracts | **7/7**, including null-first mixed direct projection. |
| Final combined suite | **78/78**, no failures/skips. |
| Non-incremental Linux Release build | **0 errors / 173 warnings** with SDK 10.0.402. |
| Bounded process-only live gate | Sensors registered, controlled workloads and two inventories completed, graceful shutdown, no owned process left. |
| Live acceptance | **26/26** aggregate assertions across 5,938 rows and 98 files. |
| Controlled sequence | **8/8** cases have one null fork, two attempts and two successes with exact path-kind pairing and strict observation ordering. |
| Null producers | **24/24** fork-only children and every Refresh row remain null. |
| Schema/compatibility | Optional field present in **98/98** files; birth/hash/run scope, timing, name/path and command-line controls remain valid. |

The live capture contains 1,482 attempt and 1,477 success observations with no
invalid value, source mismatch, non-Start classification, Error/Fatal log entry,
or nonzero drop/backlog diagnostic. This closes source-level distinction only;
syscall outcome correlation and initial/latest successful-image DBT policy remain
deferred. The implementation is committed locally in Wintap as `e93c77b`; nothing
was pushed. Raw telemetry and identifiers remain outside Git. Full evidence:
`../wintap/developer_docs/audits/sfx-04-linux-exec-observation-kind.md`.

## sfx-05 Linux Executable Path Source — 2026-11-22

The next bounded unit adds nullable `ExecutablePathSource` while preserving path
and name selection. Exact Linux values are `exec-event-filename`, `procfs-exe`,
`parent-procfs-exe`, and `unavailable`. Exec, clone and rundown retain their prior
precedence; unsupported producers remain null. No BPF, argv, command-line,
identity, timing, exec-kind or downstream-model behavior changed.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs -->

| Gate | Result |
|---|---|
| Frozen baseline | **78/78** through `sfx-04`. |
| Focused contracts | **5/5**, including source precedence and null-first direct projection. |
| Final combined suite | **83/83**, no failures/skips. |
| Non-incremental Linux Release build | **0 errors / 173 warnings** with SDK 10.0.402. |
| Live acceptance | **37/37** assertions across 5,960 rows and 109 files. |
| Exec evidence | All 2,967 exec attempt/success rows use `exec-event-filename`. |
| Clone evidence | Null-kind Starts use 1,139 own-procfs, 524 parent-procfs and 43 explicit unavailable sources. |
| Refresh evidence | 476 own-procfs and 811 unavailable; every stable-anchor Refresh uses own procfs. |
| Compatibility/schema | Eight repeated-exec and 24 fork-only controls pass; optional path-source, exec-kind and timing fields are present in **109/109** files. |

No null/invalid source, source/path mismatch, Error/Fatal log entry, nonzero
drop/backlog diagnostic or owned-process leak occurred. The field records evidence
origin; it does not claim unobserved syscall outcome, filename truncation status or
initial/latest process-lifetime policy. Raw telemetry and identifiers remain
outside Git. The implementation is committed locally in Wintap as `54ddf07`;
nothing was pushed. Full evidence:
`../wintap/developer_docs/audits/sfx-05-linux-executable-path-source.md`.

## sfx-06 Linux Exit-Code Capture Status — 2026-11-22

This bounded unit adds nullable `ExitCodeCaptureStatus` while preserving numeric
`ExitCode`. Linux CO-RE Exit uses `kernel-wait-status`; fallback tracepoint uses
`unavailable` because its zero is a placeholder. Unsupported producers remain
null. Normal Stop rows and direct Parquet retain the field, including null-first
batches. No wait-status decoding, BPF change, exit filtering, lifecycle identity,
timing, resolver/parent semantics, or prior additive field changed. Direct-mode
qualification required the history lookup to tolerate an absent optional resolver;
initialized-resolver behavior is unchanged.
<!-- GROUND_TRUTH: ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs; ../wintap/wintap/core/infrastructure/EventChannel.cs; ../wintap/wintap/core/etl/extract/ProcessStopSerializer.cs -->

| Gate | Result |
|---|---|
| Frozen baseline | **83/83** through `sfx-05`. |
| Focused contracts | **5/5**, including tier classification and normal/null-first projection. |
| Final combined suite | **88/88**, no failures/skips. |
| Non-incremental Linux Release build | **0 errors / 173 warnings** with SDK 10.0.402. |
| `live-01` defect evidence | CO-RE loaded, but **1,686** callbacks exposed the absent-resolver null dereference before Stop output. |
| `live-02` repair evidence | **1,066** classified Stops and zero runtime errors; interrupted before periodic acceptance. |
| Final `live-03` acceptance | **43/43** assertions across 3,430 rows and 39 files; four sensors registered, two inventories completed, and shutdown was clean. |
| Stop semantics | **574/574** Stops are `kernel-wait-status`, matching recorded Exit tier `core`; every non-Stop row is null. |
| Compatibility/schema | Eight repeated-exec and 24 fork-only controls pass; exit status, exec kind, path source and both timing fields are optional in **39/39** files. |

Observed numeric wait-status values remain uninterpreted. There were no Error/Fatal
entries, nonzero drop/backlog diagnostics, workload stderr, or leaked processes.
The pre-existing null-first optional-string limitation populated observation run
ID in 4/8 repeated-exec cases; it is globally single-valued and consistent where
present, while birth/hash identity and timing pass 8/8. Raw telemetry and
identifiers remain outside Git. The implementation is committed locally in Wintap
as `fde5a56`; nothing was pushed. Full evidence:
`../wintap/developer_docs/audits/sfx-06-linux-exit-code-status.md`.

## sfx-07 Linux Stop Observation Timing — 2026-11-22

This bounded unit retains Linux Exit's existing kernel occurrence timestamp in
the established observation fields and extends normal Stop projection with those
fields plus envelope `ReceiveTime`. Stop `EventTime`, identity, resolver/parent
behavior, exit values/status, BPF and all Start/Refresh behavior remain unchanged.
Failed additive UTC conversion stays null while raw monotonic evidence survives.
<!-- GROUND_TRUTH: ../wintap/wintap/platform/linux/sensor/ebpf/ExitSensor.cs; ../wintap/wintap/core/etl/extract/ProcessStopSerializer.cs; ../wintap/wintap/core/etl/model/ProcessData.cs -->

| Gate | Result |
|---|---|
| Frozen baseline | **88/88** through `sfx-06`. |
| Focused contracts | **4/4**, including identity/EventTime preservation and normal/direct projection. |
| Final combined suite | **92/92**, no failures/skips. |
| Non-incremental Linux Release build | **0 errors / 173 warnings** with SDK 10.0.402. |
| Live acceptance | **50/50** assertions across 3,634 rows and 47 files. |
| Stop timing | **625/625** Stops retain positive raw/UTC timing, expected clock domain, one run scope, and receipt after observation; converted observation FILETIME exactly equals Stop `EventTime`. |
| Compatibility/schema | Eight repeated-exec and 24 fork-only controls pass; all four observation fields are optional in **47/47** files. |

No Error/Fatal entry, nonzero drop/backlog diagnostic, workload stderr, or leaked
process occurred. Raw telemetry and identifiers remain outside Git. The
implementation is committed locally in Wintap as `45939db`; nothing was pushed.
Full evidence:
`../wintap/developer_docs/audits/sfx-07-linux-stop-observation-timing.md`.

## Five-Tuple Connection-Key Investigation — 2026-11-22

The original duplicate-port allegation does not reproduce in current source or
available v7 history: `Transformer.CreateProcessConn` has passed distinct low/high
ports since the 2024 import. This does not rule on the absent ACME4-era build. Its
older PyUtil workaround describes unsorted source/destination ID inputs and
recomputes from persisted endpoints; it cannot repair a local IP already
overwritten in those persisted columns. Live-source C# vectors compiled with SDK
10.0.402 confirm reversal and same-IP stability plus sensitivity to both ports,
IP, and protocol. They also expose the real contract differences: the legacy key
changes with private-gateway metadata and can hash incomplete/default input.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/Transformer.cs; ../wintap/wintap/core/etl/transform/LoHi5Tuple.cs; ../wintap/wintap/core/etl/transform/IdGenerator.cs -->

The existing PyUtil DBT contract SQL returned **0 issues** under direct DuckDB CLI
execution. For one complete synthetic tuple, DBT and Wintap each emitted a
32-character hash but the values differed, as expected from their distinct
preimages. The PyUtil pytest wrapper was unavailable and no dependency/environment
was installed. Attempting the existing Wintap xUnit class from Linux stopped at
the Windows-targeted assembly boundary before tests executed; no native Windows
acceptance was started or claimed.
<!-- GROUND_TRUTH: git history for removed PyUtil commit 189da24; ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs -->

Private evidence and checksums are under
`/data/lintap-compactor/sensor-fixes/five-tuple-20261122/`; no identifiers or raw
telemetry are persisted in Git. No source/schema, historical data, DBT output,
dependency, network, S3, deployment, or package was changed. Disposition:
[[wiki/decision/canonical-five-tuple-connection-identity]] now makes endpoint-
normalized semantics—not DBT's exact JSON—the contract and requires one .NET
generator. Gateway symmetry, DBT override removal and coordinated rebuild remain
open.

### First implementation round — 2026-11-23

Wintap retains its legacy nested preimage but excludes ordinary default gateways
from identity while continuing to record them as metadata. Loopback retains host
scoping. Added vectors cover opposite sensors with gateway metadata in opposite
slots, gateway independence, loopback reversal/host separation, context and every
five-tuple field. Direct SDK 10.0.402 compilation of the actual changed source and
test file with evidence-only stubs passes **32/32** cases.

PyUtil silver DBT and legacy raw views now preserve producer `connid`; the DBT
macro, exact-output contract and legacy scalar-list hash were removed. Focused
model/raw-view/consumer tests pass **86/86**; the classified SQL contracts plus new
raw-view checks pass **222/222**. The two new raw-view checks are classified
`unit`, bringing the documented catalog to **226** cases (**6 unit + 220
contract**). Static single-authority and Python compile checks pass.

A real local DBT regression now seeds producer `ConnId` values, runs a selected
bronze/silver build and its activity/non-null tests, and queries the materialized
DuckDB table. All **11/11** selected DBT operations, models and tests pass; both
synthetic TCP/UDP producer IDs are preserved exactly. The broader compacted-input
file passes **8/8** runnable tests with its separate destructive migration test
skipped by its existing opt-in guard. It used an existing DBT environment and a
fresh fixture under `/data`; no sync, install, S3 or historical data was used. The
initial `dbt --version` probe was not network-isolated and may have performed the
standard package-version metadata check; the build itself used local fixtures and
disabled anonymous telemetry.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_compacted_inputs.py §test_process_conn_dbt_build_preserves_producer_conn_id; ../Wintap-PyUtil/wintap_dbt/tests/process_conn_incr_conn_id_not_null.sql -->

The normal Windows xUnit build remains blocked on Linux by Windows targeting and
stale net8 assets; no restore or dependency install was allowed. The reused test
environment also lacks `dynaconf`, so the unrelated four configuration tests did
not collect. No deployment, historical mutation, source-data/S3 access, native
Windows run or push occurred. Milestone commits were created locally after these
gates. Evidence:
`/data/lintap-compactor/sensor-fixes/conn-id-single-authority-20261123/`; full audit:
`../wintap/developer_docs/audits/sfx-08-canonical-connection-identity.md`.

### Hostname/public connection-context refinement — 2026-11-23

The approved refinement moves loopback host scoping out of gateway preimage slots.
`Transformer` now selects connection context from the host-oriented local IPv4:
RFC 1122 loopback uses hostname and every non-loopback connection uses `public`.
Both gateway identity slots are empty, while gateway values remain emitted
metadata. The existing `llnl` context remains for non-connection identity types.
This intentionally rekeys all connection IDs.

The pre-change source-linked run produced the expected red exact-context mismatch.
After implementation, direct SDK 10.0.402 compilation/execution of the changed
production and test sources passes **33/33** cases. Coverage includes a non-`.1`
loopback address, distinct hosts, reversal, exact hostname context, exact `public`
context, rejection of legacy `llnl` connection context, gateway independence and
all prior endpoint-normalization behavior.

Focused downstream DBT/legacy passthrough contracts pass **78/78**. All **11/11**
selected nodes in the real local DBT regression pass, preserving both synthetic
producer IDs through bronze/silver materialization. No downstream connection hash
was restored. DBT qualification for this round is complete. Native Windows testing
is deferred, not eliminated. Release is a clean cutover to newly collected data;
no legacy migration or mixed-population compatibility is required. Evidence:
`/data/lintap-compactor/sensor-fixes/conn-id-loopback-context-20261123/`; full audit:
`../wintap/developer_docs/audits/sfx-09-loopback-connection-context.md`.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/transform/Transformer.cs; ../wintap/tests/Wintap.Tests/NetworkEndpointNormalizationTests.cs; ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql; ../Wintap-PyUtil/tests/test_compacted_inputs.py; ../Wintap-PyUtil/tests/test_network_activity_sql.py; ../Wintap-PyUtil/tests/test_rawutil_conn_id_passthrough.py -->

## Linux executable-attribution capture preparation — 2026-11-23

The named Linux workload was extended, but no collector was started and no live
telemetry or DBT input was read. The default one-round mode remains compatible with
the existing smoke contract. The optional bounded mode adds repeated successful
same-PID exec stages with changing argument tokens, a failed exec attempt followed by
a successful exec, and a long-lived Refresh candidate. The portable selectors retain
the expected stage kind, PID/TID, token and failed-attempt path independently of
collected rows.
<!-- GROUND_TRUTH: ../wintap/devtools/telemetry_smoke_workload.py; ../wintap/devtools/test_telemetry_smoke_workload.py -->

| Check | Result |
|---|---|
| Python regression | **2/2 passed** with Python 3.12. |
| Python compilation | Passed for workload and regression test. |
| Wintap build | SDK 10.0.402; **0 errors / 174 warnings**; Lintap DLL and Linux eBPF tracer objects emitted under the approved `/data/lintap-compactor` evidence root. |
| Prepared config | Fresh process/exec/clone/exit/rundown, ETL/Parquet, and one-minute Refresh configuration generated under the same evidence root. |
| Workload cycle prepared | Nine rounds at 60-second spacing, 0.25-second worker hold, 600-second Refresh candidate; approximately ten minutes. |
| Collector state | Not started; awaiting operator launch with one-minute process Refresh and confirmed data root. |

The host default `python3` is Python 3.6 and cannot execute the existing test suite's
`subprocess.run(capture_output=...)` calls; use the approved modern persistent
interpreter/virtual environment for the capture. No raw identifiers, hostnames,
telemetry, historical data, deployment, DBT output or source data were persisted.

## Linux executable-attribution capture and DBT qualification — 2026-11-23

The operator completed the prepared bounded Linux cycle under the sanitized capture
label `linux-exec-20261123`: nine rounds at 60-second spacing, all 19 targeted PIDs
matched, and the long-lived Refresh candidate was retained. Ctrl-C shutdown was
graceful. Final serializer evidence reported zero drops, zero remaining queues, zero
Parquet failures, and no serializer backlog. The workload manifest, raw Parquet and
runtime log remain outside Git in operator-retained evidence; this page intentionally
does not record hostnames, account names, IP addresses, or raw identifiers.

### Raw process evidence

The finalized `raw_process` input consisted of three Parquet files with 21,931 rows,
5,807 distinct `PidHash` values and 5,807 distinct PIDs. No row had a null or empty
`PidHash`. The activity split was 15,395 `Start` and 6,536 `Refresh` rows. Observation
kinds were 5,022 `exec_attempt`, 5,007 `exec_success`, and 11,902 null/initial rows.
These counts are producer-layer evidence, independent of the DBT output.

The prevalence/concentration scan found the following at the `PidHash` grouping level:

| Measure | Result |
|---|---:|
| Groups with more than one process name | 4,508 / 5,807 |
| Groups with more than one process path | 4,545 / 5,807 |
| Groups with more than one command line | 686 / 5,807 |
| Maximum distinct names / paths / command lines | 3 / 5 / 5 |
| One-row groups | 371 groups / 371 rows |
| 2–5-row groups | 4,968 groups / 14,950 rows |
| 6–10-row groups | 47 groups / 328 rows |
| 11+-row groups | 421 groups / 6,282 rows |

After restricting to `Start`/`Refresh` rows and excluding `exec_attempt`, 16,909
eligible rows remained. The eligible scan still found 4,508 name-varying groups,
4,544 path-varying groups and 620 command-line-varying groups. These aggregate
figures establish concentration and multiplicity; they do not by themselves
distinguish repeated exec, PID reuse, fork images, or other producer behavior.

### Independent workload contracts

The targeted cohorts retained one `PidHash` while exposing ordered image observations:

| Cohort | Result |
|---|---|
| `wt_reexec` | 9/9 cohorts retained one `PidHash` across multiple images. The latest eligible name/path/arguments tuple matched the DBT row in 3/9 cohorts. |
| `wt_execfail` | 9 missing-executable attempts, 0 corresponding successes, and 9/9 attempts preceded a successful replacement. The latest eligible tuple matched DBT in 7/9 cohorts. |
| `wt_refresh` | 10 Refresh rows retained stable identity; the latest observation was Refresh and the latest eligible tuple matched DBT 1/1. |

Failed attempts are evidence but are not eligible canonical image rows. The Refresh
candidate resolves the live interpreter through procfs, while successful exec rows
retain the invoked executable path; this is consistent with point-in-time/current
state versus historical image evidence and is not a reason to merge the relations.
<!-- GROUND_TRUTH: ../wintap/devtools/telemetry_smoke_workload.py; ../wintap/developer_docs/audits/sfx-03-linux-command-line-provenance.md; ../wintap/developer_docs/audits/sfx-04-linux-exec-observation-kind.md; ../wintap/developer_docs/audits/sfx-05-linux-executable-path-source.md -->

### Isolated DBT result and `any_value` finding

An isolated DBT build against the finalized raw root completed **139/139** nodes.
The build did not modify production data, historical data, source code or schemas.
The process model produced one row for each of the 19 targeted `PidHash` values, but
its current projection uses independent `any_value` expressions for process name,
arguments and path. The selected fields therefore are not guaranteed to come from
one observation row or to represent the latest valid image. In the capture:

- the selected name/path/arguments triple was present in an eligible source row for
  9/9 `wt_reexec`, 8/9 `wt_execfail`, and 1/1 `wt_refresh` cohorts;
- one `wt_execfail` row selected the failed `missing-executable` image, which was an
  ineligible `exec_attempt`; and
- exact latest eligible tuple agreement was only 3/9, 7/9 and 1/1 respectively.

This is a downstream semantic defect, not a raw-telemetry failure. The required
repair is a deterministic paired-row selection policy: for current state, prefer the
latest valid Refresh as of the query time, otherwise the latest successful exec;
retain initial/history and failed-attempt evidence separately. Name, path and
arguments must be selected from that same row. The existing synthetic `any_value`
contracts remain useful for truly invariant columns, but they do not authorize
`any_value` for these changing image fields.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/tests/test_any_value_contract_sql.py -->

The DBT model also reports `os_family='windows'` for this Linux input because that
value is currently hard-coded; this capture records the limitation and does not
reinterpret it as producer evidence. Native Windows negative-control acceptance
remains a separate pending gate.

### Read-only deterministic selector prototype

A read-only DuckDB prototype was evaluated against the isolated database without
changing DBT SQL or source data. It filters canonical image candidates to `Start` or
`Refresh` rows, excludes `exec_attempt`, and selects one complete source row with this
policy: latest valid Refresh, otherwise latest `exec_success`, otherwise an explicit
eligible fallback. The ranking uses observation UTC, comparable monotonic time,
receipt time, and a stable value tie-breaker; name, path and arguments are projected
only from the selected row.

| Prototype check | Result |
|---|---:|
| Full `PidHash` groups selected | 5,807 / 5,807 |
| Full-dataset selection roles | 493 Refresh, 4,947 successful-exec, 367 fallback |
| Targeted cohorts selected | 19 / 19 |
| Targeted cohorts with exact policy/pair agreement | 19 / 19 in each of `wt_reexec`, `wt_execfail`, and `wt_refresh` |
| Selected targeted rows that were `exec_attempt` | 0 |
| Selected targeted triples co-occurred in a source row | 19 / 19 |
| Randomized source-order runs with identical results | 10 / 10 |

This qualified the candidate ranking and pairing contract for the bounded production
implementation. The resulting DBT model is validated below. An explicit as-of
predicate remains a separate future relation rather than a requirement for the
current process model; tie/ambiguity and broader non-image-field audit work also
remain separate follow-ups.

## Deterministic DBT paired-row implementation — 2026-11-23

The approved PyUtil change replaces process-image `any_value` selection with a
deterministic paired-row projection. `stg_raw_process` now supplies nullable defaults
for the additive observation columns when older raw Parquet lacks them. The silver
`process` model:

1. considers only `Start`/`Refresh` rows and excludes `exec_attempt`;
2. prefers the latest valid Refresh, otherwise the latest `exec_success`, otherwise
   an explicit eligible fallback;
3. orders by observation UTC, monotonic observation time, receipt time, event time and
   a stable value tie-breaker; and
4. takes process name, arguments and path from that one selected row.

The model additionally exposes `image_selection`, `image_observation_kind`, and the
selected observation timing fields so downstream consumers can distinguish current
image evidence from process birth timing. Existing lifetime start/stop counts and
birth timestamps remain aggregate projections; failed-attempt and transition rows
remain in the raw/staging evidence.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintap_dbt/models/bronze/stg_raw_process.sql; ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql; ../Wintap-PyUtil/wintap_dbt/models/schema.yml -->

| Gate | Result |
|---|---|
| Focused PyUtil contracts | **32 passed, 1 skipped**. |
| Python compilation | Passed for the changed staging/model tests. |
| Isolated DBT build | **139/139** nodes passed; 0 errors, 0 warnings, 0 skips. |
| Legacy-schema smoke build | **13/13** selected staging/model/tests passed with observation columns absent from raw Parquet. |
| Finalized capture target output | 19/19 targeted process rows retained paired fields; 18 selected `exec_success`, 1 selected `Refresh`. |
| Failed-attempt protection | 0 selected `exec_attempt` rows and 0 selected failed-executable paths. |
| Compatibility | Legacy fixture/model checks pass with nullable observation-column defaults. |

No production or historical data was rewritten. Native Windows negative-control
acceptance and broader cross-platform policy validation remain open.

## Multipass recovery and Debian arm64 build — 2026-11-23

The Bash Multipass provisioning path was recovered after a reproduced `uv`
dependency-download stall and a second host-side stall in cloud-init failure
diagnostics. The repair keeps `uv` for environment creation, installs pinned Python
dependencies with standard pip and bounded retries, avoids recursively changing
ownership on the host-mounted data tree, and bounds each best-effort diagnostic
command. The full VM dependency gate passed, including SDK **10.0.402**, both .NET
runtimes, kernel BTF parsing, eBPF compilation, bpftool, DuckDB **1.5.6**, and pinned
Python imports. Focused provisioning/packaging tests passed **26/26**; Bash syntax
and diff checks also passed.
<!-- GROUND_TRUTH: ../Lintap/multipass-lintap.sh; ../Lintap/tests/test_multipass_provisioning.py; ../Lintap/multipass-check-dev.sh -->

A native arm64, self-contained Debian package was then built from Wintap commit
`57789ff2119bdfe675a510101fb5b1c8431f23e8` and Lintap commit
`432e8f2957ef9783b6329e60ec03bdea4c64b8c2`, with only the unrelated uncommitted
provisioning repair present in Lintap. The build restore briefly added an RID entry
to a tracked Wintap lockfile; that generated source-tree change was removed and the
Wintap checkout was confirmed clean after the build.

| Package check | Result |
|---|---|
| Artifact | `lintap_7.0.1~beta.1-1_arm64.deb`, 102,093,428 bytes |
| SHA-256 | `2aa16462ffee0d751a686457c742222a5a6165d63ea9f50ea427269ea4a7f84d` |
| Metadata | `Package: lintap`; `Version: 7.0.1~beta.1-1`; `Architecture: arm64` |
| Version ordering | Debian comparison confirms the beta sorts before `7.0.1-1` |
| Payload | Main sensor, self-contained MCP helper, pidstat helpers, config, two systemd units, and **12** eBPF objects present |
| Native dependencies | Required `ldd` check passed |
| Maintainer scripts | Shell syntax passed; install enables but does not auto-start the service |
| Build diagnostics | 0 compiler errors; existing compiler warnings remain |

The optional .NET diagnostic provider still reports unresolved
`liblttng-ust.so.0` on this Ubuntu environment; the builder classifies that provider
as optional and records the warning separately. This round establishes package build
and structural inspection only. The package was not installed, upgraded, started,
or runtime-smoke-tested, so no deployment or telemetry acceptance is claimed.
<!-- GROUND_TRUTH: ../Lintap/packaging/lintap-deb/build-deb.sh; ../Lintap/packaging/README.md -->

## S3 upload-time UTC partition correction — 2026-11-24

The approved shared Wintap S3 correction was implemented on the current feature
branch. The source-level change was checked with `git diff --check`. The Lintap
build completed with **0 errors / 173 warnings**, and the focused S3 test filter
completed **8/8 passed** using the available .NET 10 SDK. The focused tests cover
UTC boundary rewriting, exact source identity, matching-object validation,
authoritative-miss rebinding, inconclusive-HEAD exact-key retry policy, and
sidecar cleanup. No live S3 endpoint or source dataset was accessed; endpoint
qualification remains open.
<!-- GROUND_TRUTH: ../wintap/wintap/core/etl/load/adapters/S3Adapter.cs; ../wintap/wintap/core/etl/load/adapters/base/Uploader.cs; ../wintap/wintap/core/etl/load/adapters/base/S3UploadAttemptBinding.cs; ../wintap/tests/Wintap.Tests/S3UploadAttemptBindingTests.cs -->
