---
title: "Coordination: human-run macOS qualification"
type: workflow
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - ../Wintap-PyUtil/tests/test_coordination_execution.py
  - ../Wintap-PyUtil/tests/test_coordination_tick.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml
  - ../Wintap-PyUtil/scripts/dcc_macos_baseline.py
  - ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json
  - ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py
  - ../Wintap-PyUtil/.gitignore
  - ../Wintap-PyUtil/uv.lock
policy: agent-editable
last_validated: 2026-11-14
repo_scope: Wintappy
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wintappy/coordination; tests; extras/raw-sensor-compact
tags: [feature-work, coordination, macos, qualification, human-run]
---

# Human-run macOS qualification

The human selected a reproducible, human-run Mac harness rather than CI or remote
machine access. This is a runner choice, **not macOS support or acceptance**.
<!-- SOURCE: Human runner selection, conversation 2026-11-14. -->

## Stage 1 baseline: dcc-mac-baseline-01

**Original actual-Mac result: blocked before tests at `8ee714c`.** That commit
omitted root `uv.lock`, although the manifest required it; main locked provisioning
and checkout validation failed. Neither test stage ran. The repaired `fab647f`
handoff below includes the reviewed lock; independent Mac source checks and both
locked native runtimes pass. The corrected baseline **passes**: 169 main tests with
129 reviewed Linux-only skips, and 267 standalone tests with no skips; both stages
exit 0 without timeout. Original evidence and repair disposition:
[[wiki/work/dbt-compaction-coordination/verification#Maintainer completion review — Mac provisioning blocked]]
and [[wiki/work/dbt-compaction-coordination/implementation-review#R9 — Medium: exact Mac handoff omits its required main lockfile]].

Fresh Mac timings, versions and skip review:
[[wiki/work/dbt-compaction-coordination/verification#Maintainer repaired Mac baseline — dcc-mac-baseline-01 passed]].
Stage 2 reader-backend acceptance remains the next Mac gate, not granted by this pass.

**Run the unchanged committed coordination baseline on an actual Mac and return
sanitized evidence. Do not implement a backend or qualify real S3 in this task.**

Qualification revision in **Wintap-PyUtil**:
`fab647f900196b0bc473fe7977b7dadcf7f4ce52`
on `work/raw-sensor-compacted-union`. This corrective follow-up includes the exact
original main `uv.lock`, a root-only tracking exception and committed-file coverage
checks/controls. It retains the prior feature code, README, harness and public
source manifest. The 18 feature Python files and four runtime/lock files retain
the hashes used for the worker-reported Linux 641-main/439-standalone regressions.
The committed manifest's SHA-256 is
`c37247ac1962cb6a259e5387d1c9177a37f82a5ff78f913382b293770d2bf3b7`.

**Original result: blocked.** The Mac worker reports that the original
`8ee714c0c58e9781a29b0cdc488e3aaf6ebea181` attempt stopped before either test stage
because the main lockfile was absent. Git inspection independently confirms that
only 21 of the 22 manifest files were committed; the previous local-only identity
check was satisfied by an ignored `uv.lock`. Preserve the worker's original blocked
record; this is a packaging correction, not a retroactive pass or Mac execution.
<!-- SOURCE: Mac worker blocked-result report and human-authorized correction, conversation 2026-11-14. -->

The corrected revision passes all 22 committed/local manifest hashes and the
identity-only validator from a fresh Git-only clone without copied ignored files
or virtual environments. Eighteen local harness controls pass, including three
new committed-coverage regressions. The maintainer's separate actual-Mac run now
verifies provisioning, 18 harness controls and both baseline stages. Any subsequent
rerun still requires a **new private output directory**.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/.gitignore; ../Wintap-PyUtil/uv.lock; ../Wintap-PyUtil/scripts/dcc_macos_baseline.py §validate_checkout; ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py -->

The scratch `fe7fcb5` plus uncommitted-overlay procedure is **superseded**. The
maintainer pulled the corrective commits; the human now authorizes committing and
pushing Analytics utility planning `1051a8c` and the finalized review. This does not
authorize new implementation or deployment. For any new Mac run, make this exact
qualification commit available; an older branch is insufficient. Do not transfer
datasets, settings, credentials or Linux virtual environments.

### Stage 1: commands and scope

1. Start in a **fresh disposable PyUtil checkout containing the full commit**, not
   a working tree with unrelated changes. Require macOS, Git, uv and native Python
   3.12 support. Keep provisioning failures as failures; do not change lockfiles.
2. From that disposable checkout, run:

   ```sh
   git switch --detach fab647f900196b0bc473fe7977b7dadcf7f4ce52
   uv sync --locked --dev --python 3.12
   uv sync --locked --dev --python 3.12 --project extras/raw-sensor-compact
   .venv/bin/python -B -c 'import sys, duckdb; print("main", sys.version.split()[0], duckdb.__version__); assert duckdb.__version__ == "1.5.6"'
   extras/raw-sensor-compact/.venv/bin/python -B -c 'import sys, duckdb; print("standalone", sys.version.split()[0], duckdb.__version__); assert duckdb.__version__ == "2.0.0"'
   .venv/bin/python -B scripts/dcc_macos_baseline.py \
     --root . \
     --manifest scripts/dcc_macos_source_manifest.json \
     --commit fab647f900196b0bc473fe7977b7dadcf7f4ce52 \
     --output '<new-private-output-directory>'
   ```

   Replace the output placeholder with a new absolute local directory **outside**
   the checkout. Its parent must already exist; the directory itself must not.
   Stop if either provisioning/version check fails. The main DuckDB 1.5.6 runtime
   alone owns any synthetic test ledger; the standalone DuckDB 2.0.0 runtime remains
   separate. Dependency provisioning may download packages; the test baseline is
   offline and uses no telemetry endpoint.

The harness refuses non-macOS execution, wrong full HEAD, tracked modifications,
missing reviewed ancestry and source/lock mismatches before testing. Every manifest
file must exist with matching bytes both locally and in the specified Git commit;
an ignored local file cannot satisfy committed coverage. It runs **nine
main coordination modules and three standalone completion/integrity/phase-evidence
modules**, not the full suites. Each stage has a 1,200-second ceiling, disposable
CWD/HOME/temp paths and no inherited AWS credentials/profiles. An ordinary failure
still runs the other independent runtime. Timeout stops further stages: retain
incomplete evidence and inspect only feature-owned test children before a rerun.
There is no certified descendant-shutdown contract for this harness.

No real grants/releases, real-dataset compaction, remote qualification or scheduler
installation are in scope. Any rerun uses a new report directory; never overwrite
the original failure evidence or edit the source manifest to obtain a pass.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_baseline.py; ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json; ../Wintap-PyUtil/pyproject.toml; ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml -->

### Return evidence and done criteria

- Return `summary.json`, both Python/DuckDB version pairs and necessary **sanitized**
  failure/skip reasons with test names. The summary records full commit, manifest ID,
  macOS version/architecture, stage return codes, timeout flags, counts and elapsed
  times; it deliberately records `reader_backend_qualified: false`.
- Keep `main.txt` and `standalone.txt` private: raw reports may contain account paths.
  Follow the repository's persistent-content privacy rule before filing evidence.
- Baseline passes only if both stages finish with exit zero, version/source checks
  pass and all skips are reviewed. A failure, timeout, missing stage or provisioning
  error is an explicit blocked result, not acceptance. Preserve Linux-only skips.
- Record the actual result in [[wiki/work/dbt-compaction-coordination/verification]]
  and append a concise entry to `wiki/log.md`. If repairs are needed, record the
  original failure first and identify a separate repaired revision/rerun.

An all-green baseline, especially with skips, **cannot establish supported macOS
reader lifetime/shutdown**, close dcc-02–05 or qualify representative 32 GB RAM /
64 GB disk sizing. Actual-S3 access/roots and representative retained-state runs
remain separate human-confirmed gates.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_completion.py §pytestmark; ../Wintap-PyUtil/tests/test_coordination_execution.py; ../Wintap-PyUtil/tests/test_coordination_tick.py; ../Wintap-PyUtil/tests/test_coordination_supervisor.py; ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py -->

## Stage 2: reader backend acceptance remains pending

The macOS reader backend and client are not implemented. Worker-reported Linux
full main passes 641 tests (three skips); the scoped Mac baseline passes with
Linux-only supervision paths skipped. After
the backend exists, refresh the manifest/harness for that
exact revision and run real Mac controls for ordinary DBT lifetime, preflight/build
failure, interruption, descendants, detached-child attempts and wrapper death.
Any uncertain shutdown retains reader ownership; root exit/process-group checks
alone cannot authorize release. No Linux emulation, skip or Stage 1 result closes
this gate. If a safe supported contract cannot be qualified, stop for human review
rather than silently dropping macOS.
<!-- SYNTHESIS: approved slice B/D acceptance contract in wiki/work/dbt-compaction-coordination/implementation_plan.md; no implemented macOS backend is claimed. -->

Results belong in [[wiki/work/dbt-compaction-coordination/verification]].
Service, audited recovery, isolated S3 and representative resource acceptance remain
separate gates in [[wiki/work/dbt-compaction-coordination/implementation_plan]].

### Native reader feasibility checkpoint — human review required

The next source/dependency investigation establishes **no safe native-Mac backend**
from the investigated candidates. Apple published source rejects automatic kqueue
descendant tracking; DBT's installed spawn-context locks/manifest start a Python
helper. Linux dependency probes and 34 Linux supervision tests do not qualify Mac
shutdown. No process-group fallback, blanket no-fork restriction, sandbox dependency
or eventual platform removal has been selected. Subsequent human direction authorizes
Linux-first completion and assigns the native solution to the Mac worker. This Mac
gate no longer blocks Linux integration; accepted Stage 1 need not be repeated.

Sources, candidate limits and choices:
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]]. Exact new evidence:
[[wiki/work/dbt-compaction-coordination/verification#Reader-supervision feasibility checkpoint — human review required]].
Any subsequent approved native probe needs its own exact-revision task and private
reports; the historical Stage 1 prompt below is not a Stage 2 command.

### Copy/paste continuation prompt for the Mac

```text
Run dcc-mac-baseline-01 from the committed Mac qualification runbook in
Wintap-Analytics/wiki/work/dbt-compaction-coordination/macos-qualification.md.
Test PyUtil commit fab647f900196b0bc473fe7977b7dadcf7f4ce52 unchanged on this actual Mac.
Use a fresh disposable checkout, separate locked native Python 3.12 environments,
the committed harness/manifest and new private reports outside the checkout.
Preserve the original 8ee714c blocked result: neither test stage ran because the
main committed lockfile was missing. This rerun must use a new output directory.
Do not modify runtime code or lockfiles, use real S3/datasets, install scheduling,
push, or claim reader-shutdown support. Preserve failures and Linux-only skips.
Return the sanitized summary, runtime versions and necessary failure/skip details;
record the actual result in verification.md and wiki/log.md under the wiki privacy
rule. Stop for review if provisioning or tests fail; backend acceptance is later.
```
