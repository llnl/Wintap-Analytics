---
title: "Coordination: human-run macOS qualification"
type: workflow
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - ../Wintap-PyUtil/tests/test_coordination_execution.py
  - ../Wintap-PyUtil/tests/test_coordination_tick.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/wintappy/coordination/MACOS.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_phase_evidence.py
  - ../Wintap-PyUtil/pyproject.toml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml
  - ../Wintap-PyUtil/scripts/dcc_macos_baseline.py
  - ../Wintap-PyUtil/scripts/dcc_macos_source_manifest.json
  - ../Wintap-PyUtil/scripts/test_dcc_macos_baseline.py
  - ../Wintap-PyUtil/.gitignore
  - ../Wintap-PyUtil/uv.lock
  - ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py
policy: agent-editable
last_validated: 2026-11-15
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

The isolated PyUtil overlay now implements and wires a native macOS process-group
reader path. Its actual-Mac synthetic lifecycle qualification passes all 12 controls.
This is a scoped implementation result, not backend/platform acceptance: the tests use
synthetic commands and fake coordination transport, not representative DBT/data, actual
S3 or the production service. Historical full-main 641 (three skips) and the scoped Mac
baseline predate later Linux entity/service work; newer submitted 307 Linux passes are
service-affected, not full latest-HEAD acceptance.

After transfer to the Linux target, the focused supervisor/client/Linux-lifecycle/local-
route regression passes **90** with **12 native-Mac-only skips**. No Linux behavior change
was observed; the existing service-affected result was not rerun. Details and exact scope:
[[wiki/work/dbt-compaction-coordination/verification#Linux regression after candidate handoff — focused, no behavior change observed]].

Current actual-Mac evidence, on PyUtil commit `c549424`, based on `1f4897a` in the
isolated feature branch (committed locally, not pushed):

```sh
uv run --locked --python 3.12 --group dev pytest -q tests/test_coordination_macos_supervisor.py
# 12 passed
uv run --locked --python 3.12 pytest -q tests/test_coordination_supervisor.py tests/test_coordination_client.py tests/test_coordination_local_route.py tests/test_coordination_macos_supervisor.py tests/test_coordination_retry.py
# 17 passed, 113 skipped (platform/declared skips)
```

Additional bounded actual-Mac stress controls passed: 50 successive ordinary exits
and 20 same-group descendant shutdowns. The stress driver was ephemeral, not added as
a checked-in test. Black check and whitespace validation passed. These results cover
the current synthetic coordinated-client launch/release path and local-only regression
set; they do not qualify real DBT, real S3, service installation or representative
resources. The prior kqueue attempt that signaled after root exit failed and is
superseded; current code holds the direct child unreaped while it enumerates live
members, signals before reaping, and does not inspect or signal the PGID after reaping.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py; ../Wintap-PyUtil/wintappy/coordination/MACOS.md; ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_mac_worker -->

The human has explicitly accepted a **best-effort native-Mac process-group rule**:
for normal completion, the surviving supervisor may release after the reader wrapper
finishes and no live members are observed in its dedicated process group. This accepts
a residual risk that a detached/escaped descendant can outlive the group and go
unnoticed. If
the supervisor dies, shutdown times out, or group state/acknowledgment is uncertain,
retain the reservation for manual verification; do not auto-expire it. This rule
does not establish a backend or complete descendant containment. It is specific to
coordinated native-Mac readers; Linux release rules and direct local-only DBT remain
unchanged. A Linux VM or Docker is not a prerequisite.

The candidate lifecycle controls now exercise normal/nonzero command completion,
same-group child shutdown, timeout, missing executable, output limits, interruption,
wrapper/supervisor death, acknowledgment loss, coordinated-client release/hold, and
detached-child limitation characterization. No Linux emulation, skip or Stage 1 result
substitutes for those actual-Mac controls. Remaining gate: qualify real DBT/preflight
and representative data behavior, service/transport integration, and the human's broader
backend acceptance. The listed synthetic controls passed on this Mac; stop for human
review if a later rerun or broader actual-Mac qualification fails.
<!-- SYNTHESIS: approved slice B/D acceptance contract in wiki/work/dbt-compaction-coordination/implementation_plan.md; actual-Mac synthetic lifecycle qualification is narrower than backend acceptance. -->

Results belong in [[wiki/work/dbt-compaction-coordination/verification]].
Service, audited recovery, isolated S3 and representative resource acceptance remain
separate gates in [[wiki/work/dbt-compaction-coordination/implementation_plan]].

### Native reader feasibility checkpoint — human review required

At the time of this checkpoint, the source/dependency investigation established
**no safe native-Mac backend** from the investigated candidates. Apple published source rejects automatic kqueue
descendant tracking; DBT's installed spawn-context locks/manifest start a Python
helper. Linux dependency probes and 34 Linux supervision tests do not qualify Mac
shutdown. At that checkpoint, no process-group fallback, blanket no-fork restriction,
sandbox dependency or eventual platform removal had been selected. The November 14
direction authorized Linux-first completion; the initial November 15 direction
preserved native-Mac scope and called for OS-supported helper/service design first.
A later human decision accepts a best-effort process-group release rule, recorded
below; that risk decision did not establish backend ownership or broader actual-Mac
platform acceptance. The Mac gate does not block Linux integration; accepted Stage 1
need not be repeated.

Sources, candidate limits and choices:
[[wiki/tension/native-macos-readers-vs-descendant-shutdown]]. Exact new evidence:
[[wiki/work/dbt-compaction-coordination/verification#Reader-supervision feasibility checkpoint — human review required]].
Any subsequent approved native probe needs its own exact-revision task and private
reports; the historical Stage 1 prompt below is not a Stage 2 command.

### November 15 authorized native probe — not Stage 2 acceptance

The human authorized scoped native source/test work in a separate PyUtil worktree
from submitted `123b9d3`, leaving the busy producer and its recovery work untouched.
The initial follow-up direction preserved native-Mac scope and limited the next slice
to design of an OS-supported helper/service boundary. A subsequent human decision
accepts the best-effort process-group risk rule below; this does not select a helper/
service API or dependency.
Locked Python 3.12.12 environments use main DuckDB 1.5.6 and standalone 2.0.0.
The five-module portable rerun passes 169/25 reviewed Linux-only skips after
standalone provisioning; this is not a repeat of the old manifest-selected baseline.

From the isolated PyUtil main runtime:

```sh
.venv/bin/python -B scripts/dcc_macos_restriction_probe.py
```

The actual Mac rejects kqueue `NOTE_TRACK` with `ENOTSUP`. No-fork sandboxing
denies fork/spawn with `EPERM` and breaks plain manifest construction; prestarting
Python's helper allows a real fixed synthetic DBT build (three passes) and test
(two passes) through in-process `dbtRunner`. The current coordinated client instead
uses `subprocess.call`, so this does not establish launcher compatibility. First/
formatted probes exit 0; the formatted run is 4.288 s with unchanged
script/main-lock/manifest identities. Private reports and command scope:
[[wiki/work/dbt-compaction-coordination/verification#Independent submitted review and native-Mac feasibility — November 15]].
The separate final style successor passes the same synthetic build/test in 4.269 s
with three unchanged successor identities; original source/report evidence is retained.

**The restriction probe itself is not the coordinated backend.** A separate
process-group implementation now exists; the probe's deprecated Apple sandbox and
private CPython helper/finalizer dependencies remain unselected. The probe explicitly
reports `native_shutdown_qualified: false` and publishes no reservation. Its synthetic
build and normal helper cleanup do not expand the current process-group lifecycle
evidence or close the remaining backend-acceptance gates.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py; wiki/tension/native-macos-readers-vs-descendant-shutdown.md -->

### Human-approved native-Mac risk rule — 2026-11-15

The human accepts best-effort supervision for coordinated readers that run natively
on macOS; a Linux VM or Docker is not a prerequisite. For normal completion, a
surviving supervisor may release the reservation after the wrapper finishes and no
live members are observed in the dedicated reader process group. This explicitly
accepts the residual risk that a detached/escaped descendant can outlive that group and go
unnoticed. If the supervisor dies, shutdown times out, or group state/acknowledgment
is uncertain, keep the reservation for manual verification and do not auto-expire it.
Linux shutdown rules and direct local-only DBT are unchanged.

This is a human-approved risk boundary, **not** backend selection or acceptance.
The exact helper/service/API and dependency remain open. Actual-Mac qualification
must exercise the current coordinated launcher, ordinary child shutdown, failures,
interruption, detached-child risk characterization, wrapper/supervisor death and
acknowledgment loss before coordinated native-Mac support is claimed.
<!-- SOURCE: Human native-Mac risk decision, conversation 2026-11-15. -->

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
