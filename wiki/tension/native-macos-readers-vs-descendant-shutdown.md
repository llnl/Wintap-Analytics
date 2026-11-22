---
title: "Tension: Native macOS DBT Readers vs. Complete Descendant Shutdown"
type: tension
status: open
poles:
  - "Researchers should run native Linux/macOS DBT clients with the existing Python/DuckDB dependencies and local analysis outputs."
  - "Native macOS may use best-effort dedicated-process-group shutdown for normal reservation release, while accepting that an escaped descendant may be missed; ambiguous shutdown still retains the reservation."
resolution: null
confidence: medium
grounded_by:
  - wiki/work/dbt-compaction-coordination/dev_handoff.md
  - wiki/work/dbt-compaction-coordination/implementation_plan.md
  - wiki/work/dbt-compaction-coordination/verification.md
  - ../Wintap-PyUtil/wintappy/coordination/client.py
  - ../Wintap-PyUtil/wintappy/coordination/supervisor.py
  - ../Wintap-PyUtil/tests/test_coordination_supervisor.py
  - ../Wintap-PyUtil/tests/test_coordination_macos_supervisor.py
  - ../Wintap-PyUtil/wintappy/coordination/MACOS.md
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

An isolated native-Mac process-group prototype is now implemented in Wintap-PyUtil,
and its limited actual-Mac synthetic lifecycle qualification passes 12 controls. It
is **not accepted as a platform backend**: these controls do not exercise
representative DBT/data workloads, actual S3 coordination or production service integration.
The human has accepted a native-Mac best-effort risk boundary: for ordinary completion,
a surviving supervisor may treat observation of no live members in the dedicated
reader process group as sufficient to release the reservation, while acknowledging
that a descendant that escapes that group could remain active and go unnoticed. If
the supervisor dies, shutdown times out, or the group state cannot be confirmed, retain the
reservation for manual verification; do not auto-expire it. This is not proof of
complete descendant shutdown, selection of a particular helper/service/dependency,
or platform acceptance. Native macOS remains in scope without a Linux VM or Docker
requirement; local-only DBT remains direct and unchanged. Linux release rules are
unchanged. The tension stays open until the candidate is qualified beyond synthetic
lifecycle controls and explicitly accepted for use.
<!-- SOURCE: Human direction, conversation 2026-11-14: finish Linux; native Mac worker to find a solution. -->
<!-- SOURCE: Human decision, conversation 2026-11-15: accept best-effort native-Mac process-group release with manual handling of uncertain shutdown; do not require a Linux VM or Docker. -->
<!-- REVIEW NEEDED: native-Mac backend selection and actual-platform shutdown qualification remain unresolved. -->
<!-- GROUND_TRUTH: wiki/work/dbt-compaction-coordination/dev_handoff.md §Worker continuation after the Mac review; wiki/work/dbt-compaction-coordination/implementation_plan.md §B. Resolve and bind execution before launch -->

The accepted actual-Mac baseline is preserved: 169 main passed/129 reviewed
Linux-only skips, 267 standalone passed and 18 harness controls passed. That historical
baseline did not exercise descendant shutdown. The separate process-group candidate
now has 12 passing actual-Mac synthetic lifecycle controls; broader DBT/data, S3 and
service acceptance remain open. PyUtil owns implementation; Analytics owns this shared
evidence and unresolved decision.
<!-- GROUND_TRUTH: wiki/work/dbt-compaction-coordination/macos-qualification.md §Stage 2: reader backend acceptance remains pending -->

On November 15 the human authorized isolated native-Mac work and accepted the
best-effort process-group release boundary. The process-group candidate is wired
to the coordinated client in the isolated PyUtil worktree; this does not select XPC,
launchd, a helper/service implementation, or a dependency, and is not platform
acceptance. The restriction/bootstrap probe below remains separate feasibility
evidence, not dependency acceptance.
<!-- SOURCE: Human implementation approval, conversation 2026-11-15. -->
<!-- SOURCE: Human design direction, conversation 2026-11-15. -->
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
fail closed on any unaccounted fork, but that is not a complete descendant tracker.
The human's accepted process-group rule explicitly tolerates this as a residual
native-Mac risk; it does not make group emptiness proof that every descendant stopped.
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

### The probe does not exercise the coordinated client's DBT launcher

The current coordinated reader builds a `DBT_BATCH` command. That Python wrapper
calls `_dbt_run`, which executes each DBT command with `subprocess.call`; `dbt-build`
also runs a separate source preflight before `build`. By contrast, the restriction
probe calls `dbtRunner().invoke()` in-process. The same probe observes subprocess
spawn denied under the no-fork profile. Therefore the demonstrated synthetic
build/test does **not** show that the current coordinated launch path works under
that restriction; it would be blocked before or during its external DBT command.

An in-process DBT adapter limited to coordinated execution could be investigated,
but it changes the launch contract and needs explicit equivalence controls for the
preflight/build sequence, configuration/environment, output and exit/error/signal
behavior. It would not resolve helper ownership, interruption, wrapper-death or
complete shutdown. The ordinary local-only `_dbt_run` path must remain unchanged.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/wintappy/coordination/client.py §run_reader/main/_dbt_commands/_dbt_run; ../Wintap-PyUtil/scripts/dcc_macos_restriction_probe.py §_restricted_child -->

### OS-supported helper/service boundary review

The initial human direction kept native Mac in scope and called for design of an
OS-supported helper/service boundary. A later decision accepts process-group
emptiness as a best-effort normal-release signal, with detached-descendant risk
explicitly accepted and ambiguous shutdown still fail-closed. That decision sets a
risk boundary; it does not select XPC, launchd, Endpoint Security, an entitlement,
a helper/service implementation or a dependency. Broader actual-Mac qualification
remains required.
<!-- SOURCE: Human direction, conversation 2026-11-15. -->

- **XPC/launchd helper:** Apple's XPC overview describes launchd starting a service
  on demand, stopping it when idle, and restarting it after a crash. The cited
  `launchd.plist(5)` contract says cleanup targets the job's process group. Neither
  statement establishes control over a descendant that creates a new session/group;
  an XPC service boundary alone is insufficient for reader release.
- **Endpoint Security:** Apple's `NOTIFY_FORK` is a notification event, while
  `AUTH_EXEC` authorizes an image execution. A fork-only child need not execute a new
  image before using inherited memory/file descriptors, so these event types do not
  provide a demonstrated deny-fork containment boundary. Apple documents Endpoint
  Security clients as privileged and entitlement-bearing; this also adds system
  extension, approval and operational requirements.
- **App Sandbox:** Apple's public overview describes resource restrictions through
  entitlements. The reviewed public contract does not establish a caller-configurable
  no-fork policy or complete descendant shutdown for an arbitrary DBT workload. It
  cannot be substituted for the deprecated custom `sandbox_init` experiment without
  separate source and actual-Mac proof.
- **Virtualization.framework:** Apple supports Linux and macOS guests on Intel and
  Apple-silicon Macs; VM configuration requires
  `com.apple.security.virtualization`, and `VZVirtualMachine.stop` reports completion
  after a successful stop. This is a possible whole-guest boundary, but running DBT
  in a Linux guest is not a native macOS reader and would require an explicit scope
  amendment, guest/data/credential design, entitlement and resource qualification.

<!-- SOURCE: Apple XPC overview https://developer.apple.com/documentation/xpc; Apple launchd.plist(5), pinned historical source above; Apple Endpoint Security event types https://developer.apple.com/documentation/endpointsecurity/es_event_type_notify_fork and https://developer.apple.com/documentation/endpointsecurity/es_event_type_auth_exec; Endpoint Security client/privilege requirements https://developer.apple.com/documentation/endpointsecurity/client; App Sandbox https://developer.apple.com/documentation/security/app-sandbox; Virtualization https://developer.apple.com/documentation/virtualization; virtualization entitlement https://developer.apple.com/documentation/virtualization/adding-the-virtualization-entitlement-to-your-project; VZVirtualMachine.stop https://developer.apple.com/documentation/virtualization/vzvirtualmachine/stop(completionhandler:); retrieved 2026-11-15. -->
<!-- SYNTHESIS: public service/event contracts do not establish macOS descendant containment; VM stop is a different OS boundary but changes the runtime platform to a Linux guest. -->

**Disposition:** no native macOS helper/service boundary is selected or established
by this review. Do not implement an XPC/launchd wrapper or Endpoint Security watcher
as if it were a subreaper. The separate native process-group candidate has passed its
synthetic actual-Mac lifecycle controls; continue broader actual-Mac qualification
against the human-approved best-effort rule. A Linux VM or Docker is not a prerequisite.
No-live-member observation is an accepted normal-release signal for this Mac path,
not complete descendant proof. Supervisor death, timeout, missing stop acknowledgment
or uncertain group state retains the reservation for manual verification.

Before backend qualification/acceptance, the design must identify: (1) the durable owner and
authenticated mapping from the exact reader grant to its dedicated process group;
(2) how the surviving supervisor observes and terminates that group, while explicitly
documenting that detached/reparented descendants can escape and are the accepted
residual risk; (3) a terminal acknowledgment only after the wrapper has finished and
the managed group is observed empty, with supervisor death, timeout, or lost/uncertain
acknowledgment retaining the reservation for manual verification; and (4) installation,
signing/entitlement, credential/data access and resource costs. Actual-Mac
qualification must exercise normal completion, preflight/build failures, interruption,
ordinary child shutdown, detached-child attempts (to characterize the known limit),
wrapper/supervisor death and stop-acknowledgment loss. Direct local-only DBT and
Linux shutdown rules must stay unchanged. These are design/acceptance criteria, not
evidence that a candidate currently meets them.

## Candidates not accepted

| Candidate | Unclosed requirement |
|---|---|
| Dedicated process-group prototype (implemented, not accepted) | Actual-Mac synthetic lifecycle suite passes 12 controls. The wrapper must finish and the managed group be observed empty for normal release. Detached/reparented descendants may escape; this risk is accepted. Timeout, supervisor death, or uncertain group state retains the reservation for manual verification. Representative DBT/data, S3, service and broader platform qualification remain open. |
| Sampled child lists or root-only kqueue | Do not reliably close the short-lived-parent/reparenting gap or establish the dedicated group state; not accepted as substitutes for the selected best-effort rule. |
| `launchd` default process-group cleanup | Could potentially support the accepted best-effort rule, but Apple's historical published manpage promises cleanup of the same process group, not every detached descendant. No current-Mac qualification has run; no launchd backend is selected. |
| Native process-creation restrictions with a prestarted helper | Actual-Mac in-process synthetic DBT feasibility passes, but the probe differs from the client's subprocess-based DBT launcher. Deprecated/private dependencies, helper ownership, inheritance/delegation, interruption/wrapper death and complete shutdown remain unqualified. No sandbox backend is selected or implemented. |
| XPC/launchd helper or Endpoint Security watcher | Service lifecycle/process-group cleanup is not complete descendant containment; Endpoint Security fork observation is notification-only and no deny-fork contract is established. Installation/privilege/entitlement costs remain unselected. |
| Privileged/signed Mac containment service | No such service or shutdown proof exists in this feature. Installation, entitlements and operating costs are additional decisions, not implied authorization. |
| Virtualization.framework Linux guest | Potential whole-guest boundary, but guest DBT is Linux rather than a native macOS reader; requires explicit scope change, virtualization entitlement, guest/data/credential design and resource qualification. |
| Run readers in a qualified Linux environment | Potential staging path, not native-Mac acceptance. Deferring the human-selected native platform requires explicit approval. |

Historical launchd source:
[process-group cleanup](https://github.com/apple-oss-distributions/launchd/blob/d448a1c8f70a61202f8705f94337f686b87c30c4/man/launchd.plist.5#L364-L368),
inspected 2026-11-14. This source is not a current-OS guarantee.
<!-- SOURCE: Apple published launchd manpage at the pinned link above; retrieved 2026-11-14. -->

## Decision and resolution criteria

Earlier human review selected Linux-first staging with native Mac still pending and
assigned to its native worker. Subsequent human directions preserve native-Mac scope,
reject a Linux VM/Docker requirement, and accept best-effort process-group-based
normal release with manual handling of ambiguous shutdown. No helper/service API,
dependency, automatic expiry, or production backend is selected by this page.

**Review recommendation:** do not select the current sandbox/bootstrap experiment as
the production backend. Keep the native-Mac gate open and local-only DBT direct.
The human-approved process-group rule is a risk boundary for native design and
qualification, not evidence that a backend works or that detached descendants are
contained. No helper/service API is selected. A passing in-process probe cannot
qualify the coordinated launcher or authorize reservation release.

Resolve only after an implemented, human-run actual-Mac backend passes
preflight/build/test lifetime, failure, interruption, ordinary-child shutdown,
detached-descendant risk-characterization and wrapper/supervisor-death controls under
the accepted rule. Uncertainty still retains ownership. Keep local-only DBT direct
and the utility's diagnostic exception separate.
See [[wiki/work/dbt-compaction-coordination/macos-qualification]] and
[[wiki/work/dbt-compaction-coordination/implementation_plan]].
