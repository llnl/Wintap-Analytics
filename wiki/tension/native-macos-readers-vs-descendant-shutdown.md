---
title: "Tension: Native macOS DBT Readers vs. Complete Descendant Shutdown"
type: tension
status: open
poles:
  - "Researchers should run native Linux/macOS DBT clients with the existing Python/DuckDB dependencies and local analysis outputs."
  - "A reader reservation may be released only after source-reading descendants cannot continue; root exit, process-group disappearance and sampled process scans are insufficient."
resolution: null
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/dev_handoff.md
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - wiki/work/dbt-compaction-coordination/verification.md
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/uv.lock
  - ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py
policy: human-review-required
last_validated: 2026-11-15
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
source_paths: ../Wintap-PyUtil/wintappy/coordination; ../Wintap-PyUtil/uv.lock; wiki/work/dbt-compaction-coordination
tags: [tension, coordination, macos, dbt, supervision, fail-closed]
---

# Native macOS DBT Readers vs. Complete Descendant Shutdown

## Current checkpoint

**No safe native-macOS reader backend has been established by this investigation.**
The human subsequently authorized **Linux-first completion**, assigning the native
Mac solution to the native Mac worker. Linux service/client work is no longer held.
This is a source/dependency feasibility result, not proof that every possible Mac
design is impossible. Eventual Linux/macOS scope remains unchanged; uncertain readers
retain reservations, and this native-Mac tension remains open.
<!-- SOURCE: Human direction, conversation 2026-11-14: finish Linux; native Mac worker to find a solution. -->
<!-- REVIEW NEEDED: native-Mac backend selection and actual-platform shutdown qualification remain unresolved. -->
<!-- GROUND_TRUTH: wiki/work/dbt-compaction-coordination/dev_handoff.md §Worker continuation after the Mac review; wiki/work/dbt-compaction-coordination/implementation_plan.md §B. Resolve and bind execution before launch -->

The accepted actual-Mac baseline is preserved: 169 main passed/129 reviewed
Linux-only skips, 267 standalone passed and 18 harness controls passed. It did not
execute or qualify a Mac descendant-shutdown backend. PyUtil owns implementation;
Analytics owns this shared evidence and unresolved decision.
<!-- GROUND_TRUTH: wiki/work/dbt-compaction-coordination/macos-qualification.md §Stage 2: reader backend acceptance remains pending -->

On November 15 the human authorized isolated native-Mac implementation/review
work. The actual restriction/bootstrap probe below improves feasibility evidence,
not dependency acceptance: no safe backend is selected or wired into the client.
<!-- SOURCE: Human implementation approval, conversation 2026-11-15. -->
<!-- REVIEW NEEDED: deprecated Apple sandbox and private CPython helper lifecycle dependencies must be reviewed before any production backend selection. -->

## Evidence and limits

### Linux ownership is not a portable process-group algorithm

The existing fresh Linux supervising exec becomes a subreaper before launching
work. It adopts orphaned/double-forked/session-detached descendants and requires
root exit plus `ECHILD` to establish shutdown. The fresh Linux supervision rerun
passes **34 tests**, including detached descendants, interruption and supervisor
failure controls. This does not implement a reader client or certify Mac behavior.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/supervisor.py §_worker/_reap/_stop_tree; ../Wintap-PyUtil/tests/test_coordination_supervisor.py; wiki/work/dbt-compaction-coordination/verification.md §Reader-supervision feasibility checkpoint — human review required -->

### Darwin kqueue does not provide the assumed automatic descendant tracking

Apple's published XNU source rejects `NOTE_TRACK | NOTE_TRACKERR | NOTE_CHILD`
in `filt_procattach` with `ENOTSUP`; its header explicitly describes those flags as
unsupported since 10.5. `NOTE_FORK` can report that a fork occurred, but the header
states that the child's PID is not passed through in the actual event. These are
observations of published source revision `f6217f891ac0bb64f3d375211650a4c1ff8ca1ea`,
**not a probe of the kernel installed on the qualification Mac**.

The subsequent native November 15 probe now independently observes `ENOTSUP` for
`NOTE_TRACK` on the actual Mac. It does not upgrade `NOTE_FORK` to complete tracking.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py §main -->

Sources inspected on 2026-11-14:
- [XNU `filt_procattach`, lines 1099–1107](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/kern/kern_event.c#L1099-L1107).
- [XNU event flags and fork-event payload, lines 255–274 and 362–369](https://github.com/apple-oss-distributions/xnu/blob/f6217f891ac0bb64f3d375211650a4c1ff8ca1ea/bsd/sys/event.h#L255-L274).
<!-- SOURCE: Apple published XNU source at the pinned links above; retrieved 2026-11-14. -->

Consequently, combining fork notifications with sampled child enumeration cannot
be assumed to close the short-lived-parent/reparenting race. A future watcher might
fail closed on any unaccounted fork, but that is not a complete descendant tracker
or a qualified normal-release contract.
<!-- SYNTHESIS: pinned XNU event semantics and the existing complete-shutdown acceptance requirement. -->

### DBT is not strictly single-process merely because model work uses threads

The inspected installed Linux dependencies match the lock: dbt-core **1.12.3**,
dbt-adapters **1.24.5**, dbt-duckdb **1.9.6**. DBT explicitly selects a spawn
multiprocessing context; manifest and connection-manager construction use its
`Lock`/`RLock`. Separate DBT model work uses a thread pool. These installed-package
observations are version-scoped, not committed dependency source or Mac execution.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/uv.lock §dbt-core/dbt-adapters/dbt-duckdb; wiki/work/dbt-compaction-coordination/verification.md §Reader-supervision feasibility checkpoint — human review required (historical installed dependency probes) -->

Two fresh Linux dependency probes each observe **one real helper launch** from
`get_mp_context().RLock()` or `Manifest()`. A third, synthetic helper-launch denial
propagates `PermissionError` from manifest construction; its newly created semaphore
is explicitly cleaned up. All three command trees stop under the Linux supervisor.
This is not a Mac sandbox failure or new red/green implementation evidence.
<!-- GROUND_TRUTH: wiki/work/dbt-compaction-coordination/verification.md §Reader-supervision feasibility checkpoint — human review required -->

Python's documented POSIX spawn behavior includes a resource-tracker process;
the qualified Mac Python **3.12.12** source also launches that helper and makes it
ignore `SIGINT`/`SIGTERM`. A blanket no-child rule needs a compatible, independently
supervised bootstrap/cleanup design; changing DBT's context or allowing arbitrary
Python helpers is not an established solution. The tracker itself is not asserted
to read telemetry, but its existence invalidates a blanket no-descendant assumption.

Sources: [Python 3.12 multiprocessing contexts](https://docs.python.org/3.12/library/multiprocessing.html#contexts-and-start-methods)
and [CPython 3.12.12 resource tracker](https://github.com/python/cpython/blob/v3.12.12/Lib/multiprocessing/resource_tracker.py).
<!-- SOURCE: Python documentation and pinned CPython source; retrieved 2026-11-14. -->

### Actual-Mac restricted DBT bootstrap — feasibility only

The native probe uses Python 3.12.12/main DuckDB 1.5.6 with the unchanged lock's
DBT versions. `sandbox_init` no-fork restrictions deny both fork and subprocess
spawn with `EPERM`; ordinary manifest construction refuses. Starting the resource
tracker before applying restriction enables a genuine synthetic build (three
passes) and test (two passes). First/formatted probes succeed; the formatted run
is 4.288 s with unchanged script/lock/manifest identities and empty stderr. A separate
style successor repeats the same synthetic result in 4.269 s; both revisions and
their original reports remain retained, without backend or shutdown acceptance.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py; wiki/work/dbt-compaction-coordination/verification.md §Independent submitted review and native-Mac feasibility — November 15 -->

This is **not a production containment design**. It uses deprecated Apple sandbox
APIs and private CPython resource-tracker/finalizer/semaphore cleanup seams. The
known helper is bootstrapped but no closed lifetime tracker, restriction inheritance/
delegation matrix, detached-child controls, interruption, wrapper death or complete
shutdown qualification exists. Normal synthetic cleanup and timeout cannot certify
all readers stopped. The script explicitly reports shutdown unqualified and has
no grant/release path. Keep the tension open and stop for dependency/design review
before production wiring; do not weaken Linux or direct local DBT compatibility.
<!-- REVIEW NEEDED: accept/reject the dependency strategy and lifetime design explicitly; successful build/test does not close native-Mac acceptance. -->

## Candidates not accepted

| Candidate | Unclosed requirement |
|---|---|
| Process-group kill, sampled process lists or root-only kqueue | No complete ownership/shutdown proof for detached or reparented descendants; cannot authorize release. |
| `launchd` default process-group cleanup | Apple's historical published manpage promises cleanup of the same process group, not every detached descendant. No current-Mac containment probe has run. |
| Native process-creation restrictions with a prestarted helper | Actual-Mac synthetic DBT feasibility now passes, but deprecated/private dependencies, helper ownership, inheritance/delegation, interruption/wrapper death and complete shutdown remain unqualified. No sandbox backend is selected or implemented. |
| Privileged/signed Mac containment service | No such service or shutdown proof exists in this feature. Installation, entitlements and operating costs are additional decisions, not implied authorization. |
| Run readers in a qualified Linux environment | Potential staging path, not native-Mac acceptance. Deferring the human-selected native platform requires explicit approval. |

Historical launchd source:
[process-group cleanup](https://github.com/apple-oss-distributions/launchd/blob/d448a1c8f70a61202f8705f94337f686b87c30c4/man/launchd.plist.5#L364-L368),
inspected 2026-11-14. This source is not a current-OS guarantee.
<!-- SOURCE: Apple published launchd manpage at the pinned link above; retrieved 2026-11-14. -->

## Decision and resolution criteria

Human review selected Linux-first staging with native Mac still pending and assigned
to its native worker. No weaker automatic release, automatic expiry, private API
dependency or platform removal is selected by this page.

Resolve only after an explicit scope decision or an implemented, human-run
actual-Mac backend passes preflight/build/test lifetime, failure, interruption,
detached-descendant attempts and wrapper-death controls. Uncertainty still retains
ownership. Keep local-only DBT direct and the utility's diagnostic exception separate.
See [[wiki/work/dbt-compaction-coordination/macos-qualification]] and
[[wiki/work/dbt-compaction-coordination/implementation_plan]].
