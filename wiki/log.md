# Wintap Ecosystem Wiki Operation Log

Append-only. Format: `## [YYYY-MM-DD] operation | description`
Query: `grep "^## \[" log.md | tail -10`

---

## [2026-11-17] docs | Add wrapper-to-dd raw process example

Added a sanitized `datacrumbs_wrap` → `dd` example to
`wiki/todo/linux-process-executable-attribution.md`. The example distinguishes
fork, exec attempts, successful image replacement, and Stop for one PidHash, and
connects the observations to the existing unordered `ANY_VALUE` executable
selection risk. Also recorded a follow-up to validate apparent Start-versus-Stop
timestamp precision differences against Linux `/proc` clock-tick normalization.
No sensor, schema, DBT, or raw-data changes were made.

## [2026-11-16] code | experimental raw-process activity heuristic

Added the user-approved, aggregate-only `raw_process` process-diversity metric
to the Recent Host Activity dashboard. It counts distinct normalized process
names from Start events per user/host and fixed 15-minute UTC bucket after small
documented system/user and process deny-lists. The UI labels it as experimental
likely user activity, renders an authorized one-host user/time heatmap, preserves
the raw-row chart, and exposes no paths, command lines, or individual process
details. Synthetic aggregation/UI tooltip tests and locked-suite verification
were updated; S3 remains read-only and no host/user live values were persisted.

## [2026-11-16] verification | raw-process 24-hour aggregate heatmap

The 24-hour read-only validation selected 2,328 objects and 2,617,339 raw rows.
The raw-row chart correctly withheld output at its 2,000,000-row budget, while
the aggregate-only DuckDB path produced 2,134 SQL-generated heatmap cells across
18 display users. The fixed-resolution heatmap uses a separate 20,000-cell
budget. Offline tests, compileall, lock, and diff checks pass; no host/user live
values were persisted.

## [2026-11-16] todo | Linux interactive session/logon feed

Documented that the process-start user heatmap is a barely acceptable temporary
proxy rather than session detection. Added [[wiki/todo/linux-interactive-session-feed]]
with quick research recommending systemd-logind `SessionNew`/`SessionRemoved`
events first, an optional `pam_exec` session-hook fallback, and utmp/wtmp only as
a limited reconciliation source. No sensor, schema, or source-repository code
was changed.

## [2026-11-16] intake | Lintap RPM Amazon Linux 2023 installation failure

Added [[wiki/todo/lintap-rpm-amazon-linux-2023]] as a provisional P2 packaging
intake item for the user-reported failure of the current Lintap RPM to install on
AWS Amazon Linux 2023. The item requests sanitized reproduction evidence and
classification before any RPM/build or source change; the TODO queue and index
were updated. No package, source repository, AWS host, or deployment was changed.

## [2026-11-15] verification | current-revision candidate affected scope

On the unchanged detached PyUtil candidate `c549424`, the corrected 15-module Linux
affected scope passes 341 tests with 12 expected native-Mac skips; the complete report
was inspected. Main/standalone collection is 1535/697. The earlier run without the
checkout-local standalone runtime remains retained as invalid evidence. Full main and
standalone suites are now running sequentially with isolated temporary/home paths and
AWS configuration/opt-ins disabled. No source, original user data, or original
environment files were modified; only the isolated standalone runtime was provisioned.
Endpoint/data/resource and deployment gates remain unapproved.

## [2026-11-15] verification | full-main candidate regression found

The full main suite on unchanged `c549424` finishes 1519 passed, 15 skipped and one
failed. An unchanged Darwin refusal control detects generic `run_supervised` reaching
the new macOS worker path; the parent rejected non-Linux. A Darwin-only rerun confirms
the mismatch. This is a genuine candidate regression against the intended reader-only
Mac scope; no PyUtil source was changed. The initial standalone attempt used the wrong
working directory and is retained as invalid. The correctly rooted standalone run has
694 passed/two expected skips and one `TemporaryDirectory` cleanup error after the
expected byte-budget refusal; a fresh single-test rerun passes, and a fresh full rerun
passes 695/two expected opt-in S3 skips. The complete second full report is reviewed;
the original cleanup failure remains preserved. Candidate acceptance remains blocked
by the main-suite Darwin scope regression; no PR, endpoint/data access or deployment.

## [2026-11-15] code | authorized reader-only macOS dispatch repair

With explicit human authorization, the detached PyUtil candidate now separates
Linux-only generic/writer supervision from the reader-scoped macOS entry point and
wires only the coordinated reader through the latter. Native lifecycle tests/docs were
updated; the Darwin writer-refusal control is preserved. The corrected focused Linux
gate passes 83 with 12 expected native-Mac skips. An earlier test harness accidentally
held a `darwin` platform spoof across lazy imports; that report is retained and the
test now scopes its spoof to the writer callback. The complete coordination tick module
passes 53 tests; the 15-module affected regression passes 341 with 12 expected Mac
skips, and the frozen source diff authenticates unchanged after the run. Full main then
passes 1521 with 15 declared skips in 6397.74 s; all skip reasons were inspected and no
S3 opt-in was set. The correctly rooted standalone full run hit the same temp-directory
cleanup error after the expected byte-budget refusal (694 passed/two skipped); the
failing control passes alone using local `/dev/shm` temp. A complete standalone retry
uses local tmpfs for both TMPDIR and pytest base and passes 695/two expected opt-in S3
skips. Its complete report is reviewed; home-backed-TMPDIR failures remain preserved as
likely filesystem-interference evidence. All local Linux regression gates now pass;
native-Mac execution and broader operational acceptance remain open. No PR/push, S3,
real-data or deployment activity.

## [2026-11-16] code | local reader-scope commit milestone

Committed the authorized reader-only supervision fix in the detached PyUtil candidate
as `badb67f2f4d767ea28f17459ff75422a0506f493` (`fix: scope macOS supervision to
coordinated readers`). The candidate worktree is clean; the change remains local and
unpushed. Local Linux affected/main/standalone gates pass as recorded in the feature
verification. Native-Mac lifecycle controls are the next platform-specific step; no
PR, push, S3/real-data access, or deployment occurred.

## [2026-11-16] verification | historical S3 window inventory

Using the human-authorized existing raw-data scope, a metadata-only listing found 16
event-family directories and 526 distinct UTC hours; the oldest is 2026-10-25 19:00Z.
The proposed first batch is three hours, [19:00Z, 22:00Z), with 1/8/8 family partitions
and 1/109/118 listed Parquet objects (7,317/4,979,975/4,881,446 bytes). `raw_process`
is absent in the oldest hour and present in each of the next two. Output-prefix checks
found the conventional compacted/entity/metrics/coordination prefixes empty. This was
listing metadata only—no object bodies, writes, or deletes; no compaction/entity/DBT run
has started. The sensor-version attribution is human-provided. Detailed limits are in
[[wiki/work/dbt-compaction-coordination/verification#Initial historical-window inventory — 2026-11-16]].

## [2026-11-16] verification | fresh dynamic-host qualification stopped

A new isolated v5 scope read one hour with deletion disabled. Standalone entity
processing discovered the configured seed plus a second observed host, published
both first-seen snapshots/authority evidence and metrics, and exited zero. Main-side
entity completion still compared the report to the original seed list, reproduced
`Entity CLI host/exclusion scope mismatch`, and blocked the fresh ledger. No compacted
output, deletion, retry, or resolution was run. Under explicit operator direction,
the disposable failed scope was deleted; the main completion contract was corrected
and regression-tested before a fresh next-hour qualification.
<!-- SOURCE: Fresh isolated Linux entity qualification and read-only retained-artifact diagnosis, conversation 2026-11-16. -->

## [2026-11-16] verification | next-hour dynamic-host qualification passed

The replacement fresh v5 scope completed entity bootstrap and one coordinated
20:00Z–21:00Z Linux tick with deletion disabled. Main completion accepted the
cumulative observed host set; the ledger advanced to 21:00Z in `DRAINING`, with
committed authority/snapshots, metrics, and compacted output. Independent entity
verification passed and raw inputs remain present. Verify this hour before advancing.
<!-- SOURCE: Fresh isolated Linux one-hour qualification, retained completion evidence, metrics readback, and independent entity verification, conversation 2026-11-16. -->

## [2026-11-16] verification | first deletion-enabled hour passed

The 21:00Z–22:00Z tick completed with raw deletion enabled. Immutable completion
evidence passed; compacted rows matched source rows, all exact-hour raw objects were
confirmed absent with no deletion failures, and the hourly metrics object remained
present. The ledger advanced to 22:00Z in `DRAINING`; continue only after each
one-hour verification.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, and independent S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | second deletion-enabled hour passed

The 22:00Z–23:00Z tick completed successfully with deletion enabled. Nine output
partitions matched **1,199,017** source/output rows from 166 raw objects; exact-hour
raw absence, zero row delta, metrics presence, and no deletion failures were
independently confirmed. The ledger advanced to 23:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, and corrected independent S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | third deletion-enabled hour passed

The 23:00Z–00:00Z tick completed successfully with deletion enabled. Nine output
partitions matched **1,435,300** source/output rows from 165 raw objects; exact-hour
raw absence, zero row delta, metrics presence, and no deletion failures were
independently confirmed. The ledger advanced to 00:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | fourth deletion-enabled hour passed

The 00:00Z–01:00Z tick completed successfully with deletion enabled. The committed
authority and both entity snapshots were independently read back and matched the
hourly metrics snapshot hashes. Nine output partitions matched **1,532,774**
source/output rows from 165 raw objects; exact-hour raw absence, zero row delta,
metrics presence, and no deletion failures were confirmed. The ledger advanced to
01:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, authority/snapshot readback, metrics readback, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-17] verification | Linux DBT compacted-chunk preflight blocked

Direct Linux DBT configuration passed against the isolated compacted S3 window, but
source preflight failed closed in `validate_entity_authority` because DBT's current
host-set contract rejects the valid cumulative observed-host authority state. No
models, tests, S3 writes, or deletions ran. Native-Mac testing remains deferred.
<!-- SOURCE: Linux direct DBT configuration/source-preflight attempt against the isolated deletion-enabled compacted scope, conversation 2026-11-17. -->

## [2026-11-16] code | DBT cumulative observed-host authority fix qualified

DBT authority validation now accepts cumulative observed hosts while requiring the
immutable seed-host set to remain present. The synthetic regression and focused
57-test suites passed; the real deletion-enabled compacted S3 qualification passed
preflight, build (**146/146**) and explicit test (**87/87**). No S3 mutation occurred;
native-Mac testing remains deferred.
<!-- SOURCE: Linux DBT qualification against the isolated deletion-enabled compacted scope and focused regression runs, conversation 2026-11-16. -->

## [2026-11-16] verification | Linux coordination gates remain green

The entity-service and Linux lifecycle regression modules passed **76 tests** after
the DBT authority repair. No live coordination request, service tick, S3 write or
deletion was performed. The next step requires selection of a fresh private
development manifest and authorized writable ledger/client-state scope; native-Mac
DBT remains deferred.
<!-- SOURCE: Linux local coordination regression run and scope review, conversation 2026-11-16. -->

## [2026-11-16] plan | downstream compacted/entity consumer integration

Updated [[wiki/work/dbt-compaction-coordination/integration-milestone-plan]] with
explicit raw-only, compacted-only, raw-plus-compacted, DBT DuckDB, entity-aware and
authority/status modes. The plan now covers DBT source/coverage labels and
entity-authority/processing-metrics gates; HostActivity compacted/entity discovery,
missing-versus-zero semantics and advisory status; SmokeTests' raw producer-evidence
boundary; and legacy DataQA/EDA compatibility adapters. Added synthetic migration,
overlap, deleted-raw, cumulative-authority and duplicate-count verification gates.
No application source was changed; native-Mac DBT remains deferred.
<!-- SOURCE: DBT routing/authority/metrics sources and Analytics Streamlit consumer inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | tenth deletion-enabled hour passed

The 06:00Z–07:00Z tick completed successfully with deletion enabled. Committed
authority generation 12 and both entity snapshots matched the hourly metrics
snapshot hashes. Nine output partitions matched **1,415,511** source/output rows
from 173 raw objects; exact-hour raw absence, zero row delta, metrics presence, and
no deletion failures were confirmed. The ledger advanced to 07:00Z in `DRAINING`;
no eleventh tick was started.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, authority/snapshot readback, metrics readback, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | ninth deletion-enabled hour passed

The 05:00Z–06:00Z tick completed successfully with deletion enabled. Committed
authority generation 11 and both entity snapshots matched the hourly metrics
snapshot hashes. Nine output partitions matched **1,370,554** source/output rows
from 172 raw objects; exact-hour raw absence, zero row delta, metrics presence, and
no deletion failures were confirmed. The ledger advanced to 06:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, authority/snapshot readback, metrics readback, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | eighth deletion-enabled hour passed

The 04:00Z–05:00Z tick completed successfully with deletion enabled. Committed
authority generation 10 and both entity snapshots matched the hourly metrics
snapshot hashes. Nine output partitions matched **1,548,467** source/output rows
from 172 raw objects; exact-hour raw absence, zero row delta, metrics presence, and
no deletion failures were confirmed. The ledger advanced to 05:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, authority/snapshot readback, metrics readback, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | seventh deletion-enabled hour passed

The 03:00Z–04:00Z tick completed successfully with deletion enabled. Committed
authority generation 9 and both entity snapshots matched the hourly metrics
snapshot hashes. Nine output partitions matched **1,419,050** source/output rows
from 171 raw objects; exact-hour raw absence, zero row delta, metrics presence, and
no deletion failures were confirmed. The ledger advanced to 04:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, authority/snapshot readback, metrics readback, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | sixth deletion-enabled hour passed

The 02:00Z–03:00Z tick completed successfully with deletion enabled. Committed
authority generation 8 and both entity snapshots matched the hourly metrics
snapshot hashes. Nine output partitions matched **1,372,181** source/output rows
from 172 raw objects; exact-hour raw absence, zero row delta, metrics presence, and
no deletion failures were confirmed. The ledger advanced to 03:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, authority/snapshot readback, metrics readback, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-16] verification | fifth deletion-enabled hour passed

The 01:00Z–02:00Z tick completed successfully with deletion enabled. Committed
authority generation 7 and both entity snapshots matched the hourly metrics
snapshot hashes. Nine output partitions matched **1,349,479** source/output rows
from 172 raw objects; exact-hour raw absence, zero row delta, metrics presence, and
no deletion failures were confirmed. The ledger advanced to 02:00Z in `DRAINING`.
<!-- SOURCE: Fresh isolated Linux deletion-enabled tick, immutable completion evidence, authority/snapshot readback, metrics readback, and exact-hour S3 inventory, conversation 2026-11-16. -->

## [2026-11-13] code | DuckDB-backed durable process reducer

The Wintap-PyUtil entity update path now uses DuckDB 2.0.0 relations and SQL
aggregation for working process state instead of retaining one decoded Python
`Evidence` object per process. Parquet remains the durable/interoperable snapshot
and retains `evidence_json` for DBT compatibility; the node-local qualification
uses 16 threads, 128 GB DuckDB memory and 256 GB temporary storage. The standalone
suite passes 140 tests with 2 expected skips, the DBT/config suite passes 56 tests,
and changed-file formatter/linter checks pass. The isolated three-day SQL bootstrap
then completed with all seven snapshots and 2,613,678 entities verified; entity-
enabled DBT and tree QA remain gated on the active build.

## [2026-10-26] code | RHEL 8 CO-RE start-time field compatibility

Added shared CO-RE flavor probes for upstream `task_struct.start_boottime` and
RHEL 8 `task_struct.real_start_time`; Clone and Exit now use the same
best-effort start-boottime helper. On RHEL 8.10 x86_64, all tracer CO-RE
objects compiled and a self-contained RPM built in isolated `<local-path>`
work/output directories (SHA-256
`5737b7cefbec9d394b7648aa387ab25245b9077b8e3e00a54f778b34ecfc3943`). Also
compiled both changed objects against a temporary upstream-style BTF header.
No package installation, BPF load/attach, or live capture was performed.
Updated process semantics and Linux capability documentation; pre-existing
untracked work preserved.

## [2026-10-26] docs | RHEL 8 RPM build prerequisites

Added a clean RHEL 8 x86_64 prerequisite workflow: read-only host/repository/BTF
preflight, approved DNF build dependencies, exact isolated .NET SDK 10.0.402
selection, and source/worktree checks. Explicitly supersedes stale SDK 8
handoff notes and clarifies that kernel-devel does not provide BTF. Linked from
the index; no system packages installed and no source-repo files changed.

## [2026-10-22] code | Clone default TRUE and Ubuntu package acceptance

User authorized Ubuntu/arm tests and separate RHEL handoff. Debian/RPM Clone
env defaults now true with opt-out retained; builders require Clone CO-RE payload
on native/BTF builds. Fresh self-contained arm64 package built and installed on
new disposable VM. Normal ETL startup exposed lazy plugin receipt reset erasing
isolation settings; repaired idempotent initialization and added regression
(127 focused tests pass), rebuilt revision 104. Fallback missing-flags negative
still misclassifies 60 threads and is explicitly warned, not certified. Normal
pipeline/churn/restart/opt-out acceptance ongoing; RHEL dev handoff and verification
created. No commits/pushes; unrelated changes preserved.

## [2026-10-22] code | Durable HOST runtime capability receipts

User-authorized sibling Wintap changes add versioned RuntimeCapabilitiesJson to
HOST, frozen per-run startup logging/publication even with ETL/sensors disabled,
effective config/component settings, selected object hashes and candidate/hook
outcomes. Standardized Linux auxiliary ERR_PTR checks. 126 focused tests and
Ubuntu arm64 core/fallback/restart/disabled HOST validation pass; sequential
clone regression retains all 80 births/zero threads. Concurrent harness attempt
hit API port conflict, not sensor loss. Canonical schema/verification added;
matrix updated. Defaults/packages/DBT unchanged; run ID not added to other event
rows, continuous health and downstream temporal joins remain future work.

## [2026-10-22] docs | Linux capability and resulting-data matrix

Created `wiki/diagnostic/linux-capability-data-quality-matrix.md`: separates
per-sensor object/hook selection from distro evidence; maps process/file/network/
SELinux tiers, build packaging and output modes to data caveats; proposes a
dataset capability receipt. Source review highlights placeholder fallback exit
codes/TCP bytes, missing fallback inode/parent/start evidence, callback-time Stop,
network request/rate-limit semantics, and nonuniform auxiliary ERR_PTR checks.
Named Ubuntu/Fedora/RHEL findings are dated, with new-fix/platform gaps explicit.
Linked from index and clone results. Documentation only; no source/default changes.

## [2026-10-22] code | clone lifecycle follow-up

On current branches, added manifest/libbpf/direct-parquet harnesses and five
resolver regressions. Live Ubuntu 24.04 arm64 baseline confirmed 40 false thread
births and 20 worker-TID parents; new CO-RE child pid/tgid filter and updated
clone3-aware fallback pass 80 process / 60 thread cases with normal hooks.
Fallback with absent hooks remains unsafe for thread classification. Dual-sensor
output confirms three Start observations per fork+exec identity; late clone
resolver guard preserves exec metadata and Stop state without raw deduplication.
Linux build and 88 focused tests pass; broad macOS suite fails/aborts in Windows
tests (603 pass, 16 fail). Defaults/packages unchanged. Plan/results added and
linked from verification/index; durable Linux semantics added to process-events.

## [2026-10-22] docs | Lintap packaging guide and eBPF diagram glossary

Consolidated Debian/RPM build, inspection, installation, and smoke-test
instructions into `../Lintap/packaging/README.md`; reduced format-local guides
to pointers/installed quick references and marked dated review/handoff records
as historical. Added the 36-anchor companion glossary for
`wiki/work/improve-lintap-data-quality/ebpf-quality-flow.drawio`, linked it from
verification and the index, and repaired supported live-path citation moves.
The `[A7]`/`[S8]` definitions explicitly cover TCP and UDP's ten-second EPL
aggregation, not only FileOps batching.
The review also surfaced and documented the current RPM limitation: cross-build
mode disables BTF but payload validation still requires the CO-RE FileOps
object, so the present end-to-end RPM contract is native x86_64 with BTF.
Deterministic checks found zero broken local Markdown links, real wikilinks, or
required-frontmatter omissions. Thirty-six unavailable historical/local-only
or optional external-checkout source anchors remain explicitly unretargeted.

## [2026-10-22] docs | improve-lintap-data-quality eBPF flow diagrams

Added a two-page diagrams.net source covering the Linux eBPF-to-parquet
architecture and normal-delivery/coordinated-shutdown sequence. Stable
`A`/`Q`/`S` anchors now map ring latency, attribution, serializer pressure,
durable shutdown, and downstream completeness evidence to exact flow stages.
Linked the anchors and validation matrix from the feature verification page.

## [2026-10-21] verification | improve-lintap-data-quality acceptance3

The isolated arm64 acceptance3 capture produced 10,000 file and 42 TCP staged
rows with no Unknown/empty identities, owner warnings, or FileOps queue drops.
DBT passed 80/80 and matched every file row, but found one orphan among 27
network increments. The remaining cause was floating-point `/proc` start-time
conversion in the live resolver fallback; it is now integer-only with a
regression test and awaits long-run validation. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-22] closeout | improve-lintap-data-quality accepted

Closed the feature after final source and fresh Debian arm64 acceptance. The
two-hour source run retained all 124,800 workload paths with zero serializer,
writer, sender, or ring loss and completed coordinated shutdown. A kernel-time
network correction then passed a rapid-child source run with zero file/network
orphans or `Unknown` names. Package `0.1.0-102` repeated the gate on a fresh
Ubuntu 24.04 arm64 VM: 5,000/5,000 paths, exactly 40,000 operations, DBT 80/80,
zero attribution failures, and clean final merge. Focused tests passed 383/383;
the arm64 build passed with zero errors. Promoted durable flow/shutdown facts to
the FileOps and Esper pages. Wintap commit: `1c048a8`; no push performed.

## [2026-10-21] code | improve-lintap-data-quality live attribution fallback

Moved the stable PID-hash fallback to the live file/TCP/UDP callback path so
rapid children can be attributed before exit; removed callback-time network
hashes. Local and arm64 source builds passed. The isolated rerun has 24 TCP
rows with no Unknown identities or owner warnings, but FileOps kernel counters
advance while userspace file emission remains zero, so file/DBT acceptance is
blocked rather than inferred from an empty relation. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] verification | improve-lintap-data-quality isolated attribution rerun

The isolated Clone-enabled/retry-10 acceptance rerun is not accepted: staged
output has 20 Unknown file identities in 13,097 rows and one Unknown network
identity in 64 rows, with matching owner-resolution warnings. Its raw merge had
not completed, so no DBT acceptance claim was made. The earlier zero-Unknown
capture remains pilot evidence only; ldq-03 stays open. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] code | improve-lintap-data-quality ldq-04 DBT attribution QA

Added Wintappy's `attribution_quality_summary` monitoring view, reporting
orphan and Unknown-name rows/hashes/rates for file and network relations, and
included it in `build_summary`. DBT passed 80/80. The existing orphan diagnostic
correctly fails on the shared mixed-capture raw root, so aggregate rates are
recorded as baseline/intermediate evidence rather than acceptance. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] code | improve-lintap-data-quality ldq-03 lifecycle attribution

Enabled Clone in the controlled source-build runtime and fixed the observed
cross-poller ownership races: active-cache selection now covers network events,
file/network retries are bounded to ten seconds, and Clone/Execve/`/proc`
process-start conversion shares a clock-tick identity basis. The 200-child
rapid-fork capture recorded 10,769 file rows and 32 network rows with zero
Unknown names/hashes; it does not prove process-user remediation or replace the
pending DBT comparison. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] diagnosis | improve-lintap-data-quality ldq-03 lifecycle coverage

The source-build attribution baseline has an evidence-supported cause for its
file orphans: the active runtime configuration disabled `Clone`. A representative
cron/PAM child produced 150 Unknown file identities and a later Stop record but
no Start/Refresh record; the capture log reports failed owner resolution for the
same PID. The next controlled remediation is enabling Clone for a clean
before/after capture and comparing DBT orphan composition. This does not yet
address process-user Unknown values. Corrected the dev handoff to retain the
completed ldq-00 VM setup rather than restart it. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-21] verification | improve-lintap-data-quality source baseline

Created fresh arm64 `lintap-quality` source-build VM with the LLNL checkout and
feature-isolated Wintappy data mount. The initial 6,000-file run recorded
5,693 paths with zero FileSerializer, FileOps, and BPF ring-buffer drops; a
rebuild/restart run after 45 seconds captured 6,000/6,000 with zero serializer
drops. Queue-limit changes are deferred pending warm-up/attach-state evidence.
Fixed FileSerializer-only lowercase hostname output; refreshed source output
uses `LINTAP-QUALITY` consistently across process, file, and network rows.
DBT passed 79/79; file-orphan/user-attribution counts remain baseline work.
Details: `wiki/work/improve-lintap-data-quality/verification.md` and
`wiki/work/improve-lintap-data-quality/spike.md`.

## [2026-10-21] verification | fresh lintap package mounted-data smoke

Replaced the disposable `validation-host` Multipass deployment, mounted
`../Wintappy/data` at `<local-path>`, installed Debian arm64
package `lintap_0.1.0-101_arm64.deb`, and configured that mount as
`WINTAP_DATA_ROOT`. Package service startup and process/file/network functional
smokes passed; Wintappy DBT passed 79/79. Quality is not accepted: the 6,000
unique-file workload recorded FileSerializer `dropped_total=28533`, although
the current smoke log-text gate returned a false green; DBT found 717
`process_file` orphan rows across 496 unknown process hashes. Recorded details
in `wiki/work/refactor-data-log-paths/verification.md`.

## [2026-10-21] code | smoke QA validation and orphan dashboard drill-down

Updated `../wintap/devtools/file_capture_smoke_test.py` to recognize current
FileSerializer `dropped_total` flush counters against a pre-workload baseline,
and restored Wintappy's early `raw_sensor` DBT-root validation. Added a Top 25
orphan-process-identity drill-down after the dashboard orphan summary, grouped
by relation/host/reported-name/missing-hash and ranked by event impact with
affected item and time-range context. Unit-style parser checks, dashboard SQL,
Marimo syntax/structural checks, and refreshed DBT build passed. The renewed
6,000-file field workload failed at 4,918/6,000 paths and grew the serializer
drop total from 28,533 to 55,938; this remains an acceptance failure. Details:
`wiki/work/refactor-data-log-paths/verification.md`.

## [2026-10-21] feature | improve-lintap-data-quality opened

Completed the adaptive interview and created the `improve-lintap-data-quality`
feature artifacts. Confirmed scope: measured Linux/Lintap-only remediation for
serializer loss, PID-hash orphan attribution, hostname consistency, and
incremental Unknown process/user improvement; source-build iteration first and
fresh packaged arm64 Multipass acceptance last. The benchmark-and-recommendation
spike must set queue and orphan thresholds before implementation chooses a
remedy. Windows parity and RPM acceptance are excluded. Added the feature brief
to `wiki/index.md`.

## [2026-10-20] closeout | fix-hardcoded-agentid

Feature closed after final wiki validation. Changed feature artifacts have
complete frontmatter, valid internal feature links, current validation dates,
and no broken feature wikilinks. Repository-wide lint still reports pre-existing
wiki debt (9 broken template/relative links, 60 stale pages, and 56 orphan-page
candidates), none introduced by this feature.

## [2026-10-20] code | fix-hardcoded-agentid implementation and validation

In `../wintap`, replaced TCP's literal legacy AgentId with the event AgentId,
shared platform-neutral TCP/UDP inactivity wording, sanitized the tracked
`wintap/wintapstate.json` template, and added focused serializer/template
contracts plus a repeat-miss resolver profile. Multipass `validation-host` (Ubuntu
24.04.5, kernel 6.8) build, focused tests, eBPF attachment inspection, traffic
smoke, and fresh TCP staging/raw parquet checks passed. Post-restart raw rows
had the active UUID and zero legacy literal identities; lifecycle output included
connect/send/receive/disconnect. The 621.46-us unresolved lookup profile did
not justify a negative cache without evidence of sustained live miss volume.
Updated `wiki/work/fix-hardcoded-agentid/{implementation_plan,verification}.md`,
`wiki/diagnostic/linux-tcp-investigation-2026-06.md`, and the index.

## [2026-10-20] feature-start | fix-hardcoded-agentid

Interview completed and playback confirmed. Created matching
`fix/hardcoded-agentid` branches in Wintap-Analytics and Wintap. Feature
artifacts created: `wiki/work/fix-hardcoded-agentid/{interview,brief,references,implementation_plan,dev_handoff,verification}.md`.

Scope: restore TCP event AgentId propagation; sanitize only the tracked
`wintap/wintapstate.json` template; make TCP/UDP watchdog text platform-neutral;
validate existing attachment/PID/protocol/rundown behavior; profile before any
bounded resolver negative cache; retain Linux live-validation as a closure gate.
Human estimates recorded verbatim: “3 days” solo, “1 day” AI workflow.

## [2026-10-20] ingest | Linux TCP investigation (June 2026)

Created `wiki/diagnostic/linux-tcp-investigation-2026-06.md` as the
source-policy-compliant Analytics wiki home for
`../wintap/linux-tcp-investigation-2026-06.md`; the live Wintap original remains
read-only. Current-source validation found attachment, socket-keyed PID,
protocol-fallback, Parquet null/logging, and default ProcessRundown claims
addressed; hardcoded TCP AgentId, tracked state-template UUID, and Linux
watchdog wording remain open. Contradictions flagged: none.

## [2026-10-19] code | refactor-data-log-paths Linux default correction

Changed the Linux default top-level to `/var/log/lintap`, with independent defaults
`/var/log/lintap/data` and `<local-path>`. Updated Wintap fallback
resolution/tests/tools, Debian/RPM package roots and maintainer scripts,
pidstat fallbacks, Wintappy documentation, and all active path documentation.
Focused Wintap tests pass 21/21; package rebuild/service smoke is pending VM
network recovery. Commits: Wintap `b3df278`, Lintap `7fa02da`, Wintappy
`6ae485a`.

## [2026-10-19] verification | refactor-data-log-paths validation-host cleanup

Cleaned the test-only `validation-host` instance after installing package
`0.1.0-99`: removed the legacy data tree and stale build/test artifacts,
disabled the broken pidstat unit, and restarted Lintap. Clean-package smoke
verified active output under `<local-path>` and
`<local-path>`.

## [2026-10-15] verification | refactor-data-log-paths Esper staging correction

Moved serializer/meta parquet staging and merge inputs to
`runtime/esper_staging`, leaving finalized output under `data/raw_sensor`.
Wintap build and focused path tests passed 21/21; Debian revision 2 was built,
installed over the default package layout, and its bounded service probe
reported both resolved roots. RPM, shared-mount, and full event-output gates
remain open.

## [2026-10-15] docs | refactor-data-log-paths operator path guide

Added `../Lintap-rdp/packaging/PATHS_AND_CONFIGURATION.md` as the dedicated
operator guide for data/runtime roots, `WINTAP_DATA_ROOT` and
`WINTAP_RUNTIME_ROOT` overrides, shared-mount examples, pidstat exceptions, and
verification commands. Linked it from the repository and package READMEs and
included it in generated Debian/RPM documentation. Corrected the remaining
active TeleTap README example to use direct `raw_sensor/` output.

## [2026-10-15] code | refactor-data-log-paths rdp-01/rdp-02

Implemented the two-root Wintap resolution core and moved runtime-tree
consumers to centralized `Paths` members. Data now directly contains
`raw_sensor/`; runtime owns logs, event store, csv, recordings, diagnostics,
AI state, and workbench state. Added RuntimeRoot config/env support, startup
root logging and same-root warning, uploader relative-key coverage, and test
project execution metadata. Multipass `validation-host` build passed; focused
path tests passed 20/20; grep gates passed. Full suite retains 17 known
Linux-incompatible Windows sensor failures.

## [2026-10-15] code | refactor-data-log-paths rdp-03

Committed Lintap packaging split as `301ff63` on
`feature-branch`. Debian/RPM packages now default to
`/var/log/lintap/data` for shared `raw_sensor/` output and
`<local-path>` for host-local state; maintainer scripts preserve
the data tree and create the `/var/log/lintap/data` and
`<local-path>` roots. Updated pidstat defaults,
tests, and packaging documentation. Shell/static gates passed; pytest was
blocked by missing VM dependencies and unavailable PyPI access.

## [2026-10-15] code | refactor-data-log-paths rdp-04

Committed Wintappy downstream default update as `018f541`: DBT dataset and
day-range discovery now use the direct `WINTAP_DATA_ROOT/raw_sensor` layout,
and the example environment drops `/parquet`. Analytics Streamlit/notebook
scan found no additional live old-layout input coupling.

## [2026-10-15] verification | refactor-data-log-paths rdp-05

Built and installed the Debian arm64 package in `validation-host`; staged and
post-install checks passed for `/var/log/lintap/data` and
`<local-path>`, with the new `/var/log/lintap/data` and
`<local-path>` package directories.
RPM validation is blocked by missing `rpmbuild`; service-start/event-output
acceptance remains pending.

The installed Debian service also passed a bounded 15-second start probe and
reported the split data/raw_sensor/runtime paths in journald; no short-run
event count was used as an acceptance result.

## [2026-10-15] artifact | refactor-data-log-paths Debian arm64

Confirmed the built package is available on the Mac host through the mounted
data directory at `<local-path>`.
SHA-256 `916407eafa64d4347e718d60cae58a50c368667c3dcd3dd83d40ea777d8f55a1`.
Marked ready for external-session testing; rdp-05 remains open.
## [2026-09-03] instruction | fio-03 disable FileSensor fallback diagnostic

Decision made: Architect requested and approved a diagnostic code change to remove Wintap's fallback dictionary from FileSensor emitted path selection so live Parquet output can show whether paths are coming from TraceEvent's `obj.FileName` resolution. Instruction created: `../wintap/developer_docs/instructions/fio-03-disable-file-fallback-diagnostic.md` (Approved 2026-09-03).

Scope: read/write/delete emission should use only TraceEvent-resolved `obj.FileName`; retain dictionary population code, `FileIOInit | DiskFileIO`, and close suppression. Follow-up depends on live validation results.

## [2026-09-03] approval | fio-02 suppress File CLOSE events

Decision made: Architect approved `../wintap/developer_docs/instructions/fio-02-suppress-file-close-events.md` after review amendments. Approved scope suppresses Wintap FileSensor Close emission, preserves read/write/delete/name/create behavior and `FileIOInit | DiskFileIO`, and allows only a temporary local live diagnostic probe to defeat Wintap's fallback resolver for TraceEvent path-provenance measurement; that probe must be reverted before the final production diff.

Instructions updated: `../wintap/developer_docs/instructions/fio-02-suppress-file-close-events.md` status changed from Draft to Approved; Architect approval stamped 2026-09-03.

Open questions: Whether to create a separate FileSensor resolver instrumentation/cleanup unit remains evidence-gated after fio-02 audit/live observations.

## [2026-09-03] instruction | fio-02 suppress File CLOSE events

Finding from Architect live observation after `fio-01`: File path resolution appears to be working, but most emitted File events are `CLOSE`.

Instruction written: `../wintap/developer_docs/instructions/fio-02-suppress-file-close-events.md` (Draft; Architect review pending). Scope: stop subscribing Wintap's FileSensor emission path to `FileIOClose`, preserve write/delete/name/create/read behavior, preserve `FileIOInit | DiskFileIO`, and keep rundown/cache cleanup out of scope. Clarified during review that `obj.FileName` on TraceEvent FileIO read/write/info/simple-op events is already resolved via TraceEvent's internal file-ID lookup, while Wintap's `resolveIoFilePath(...)` is an additional fallback. Draft amended to allow a temporary local live probe that disables Wintap's fallback after checking `obj.FileName`, solely to measure TraceEvent path provenance; any such probe must be reverted before final production diff.

Open questions: Architect review/approval pending. Separate FileSensor resolver cleanup and possible rundown work remain future evidence-gated items.

## [2026-09-03] approval | fio-01 FileIO DiskFileIO path-resolution flag

Decision made: Architect approved `../wintap/developer_docs/instructions/fio-01-fileio-diskfileio-path-resolution.md` as written, with rundown deliberately deferred to a potential later unit if `DiskFileIO` does not sufficiently improve FileSensor path resolution.

Instructions updated: `../wintap/developer_docs/instructions/fio-01-fileio-diskfileio-path-resolution.md` status changed from Draft to Approved; Architect approval stamped 2026-09-03.

Open questions: Whether FileIO rundown needs to be reintroduced remains evidence-gated follow-up after `fio-01` implementation/audit.

## [2026-09-02] instruction | FileIO DiskFileIO path-resolution flag

Sources read: `../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs`; `../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs`; `../wintap/wintap/platform/windows/sensor/shared/EtwKernelCollector.cs`; prior Wintap startup instruction/audit; `<local-path>`; `TraceEventSession.cs`; `TraceEventNativeMethods.cs`; `Microsoft-Windows-Kernel-File.cs`.

Finding: TraceEvent documents `KernelTraceEventParser.Keywords.DiskFileIO` as the classic-kernel flag that logs file-ID to file-name mappings, while real-time default parser tracking keeps `FileNameToObject` enabled. No TraceEvent-grounded FileIO equivalent of the Registry `EnableTraceEx2` capture-filter path was found.

Instruction written: `../wintap/developer_docs/instructions/fio-01-fileio-diskfileio-path-resolution.md` (Draft; Architect approval pending). Scope is intentionally minimal: add `DiskFileIO` beside `FileIOInit` for `FileSensor`, update shared-kernel flag tests, and do not rewrite FileSensor caches or add manifest-provider/capture-filter machinery.

Contradictions flagged: none. Follow-up: separate FileSensor resolver cleanup remains advisable for unsubscribe, split FileKey/FileObject maps, update-over-add behavior, and cache cleanup.

## [2026-09-01] feature-start | Support for Docker contexts on Linux

Interview completed and playback confirmed. Feature artifacts created:
`wiki/work/support-docker-contexts-linux/{interview,brief,references,design,spike,implementation_plan,dev_handoff,verification}.md`.
Scope: compare cgroup filesystem, namespace, eBPF event-time, shared userspace,
OCI/runtime, systemd, and notification approaches for per-event enrichment plus
a separate context stream; phase 1 targets cgroup v2 host/systemd/Docker,
phase 2 targets v1/hybrid/Podman, and normalized schema work is deferred.
Sealed human estimates recorded verbatim in `interview.md`: “2 weeks to get a
working prototype with acceptable data quality” and “3 days”.
Contradictions flagged: none.

## [2026-06-29] init | Wiki scaffold generated by lore-forge

Sources scanned: ../wintap, ../Wintap-Analytics, ../Lintap
Pages created: index.md, log.md, tension/, decision/, concept/, component/, data_model/, event_type/, pipeline/, schema/, tool/, workflow/, repo/, diagnostic/
Notes: Initial scaffold. All pages are stubs — confidence is provisional.
  First ingest pass will revise based on live source files.

## [2026-06-29] ingest | First grounded wiki pass

Sources read: ../wintap/README.md; ../wintap/documentation/wintap-developer-guide.md; ../wintap/shared/WintapAPI/WintapMessage.cs; ../wintap/shared/WintapAPI/Interfaces.cs; ../wintap/wintap/core/infrastructure/EventChannel.cs; ../wintap/wintap/core/infrastructure/WintapSvcCore.cs; ../wintap/wintap/core/infrastructure/SubscriptionManager.cs; ../wintap/wintap/platform/windows/infrastructure/WindowsSubscriptionManager.cs; ../wintap/wintap/platform/windows/sensor/etw/ProcessSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/FileSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/TcpSensor.cs; ../wintap/wintap/platform/windows/sensor/etw/UdpSensor.cs; ../wintap/wintap/core/etl/esper/*.epl; ../wintap/wintap/core/etl/extract/Serializer.cs; ../wintap/diagnostics/nesper-repro/README.md; ../wintap/platform/windows/WintapRecorder; ../wintap/shared/Wintap-Workbench; ../wintap/wintap/core/infrastructure/PluginManager.cs; ../wintap/shared/samples/SimpleEventPlugin/SimpleEventPlugin.cs; ../wintap/shared/ai/wintap_mcp_server/mcp_tools.cs; ../Wintap-Analytics/README.md; ../Wintap-Analytics/requirements.txt; ../Wintap-Analytics/2025-acme4-explore; ../Wintap-Analytics/notebooks/ProcessTrees.md; ../Wintap-Analytics/workshop/5_SQL_Exploration.md; ../Lintap/README.md; ../Lintap/teletap/README.md.
Pages created: none.
Pages updated: index.md; repo/wintap-primary-sensor-repo.md; repo/wintap-analytics-host-repo.md; repo/lintap-supporting-repo.md; component/windows-sensor-service-internals.md; component/wintap-api-shared-data-model.md; component/wintap-recorder.md; component/plugin-and-mcp-samples.md; event_type/process-events.md; event_type/file-events.md; event_type/network-events.md; pipeline/nesper-esper-event-stream-processing.md; diagnostic/nesper-repro.md; tool/wintap-workbench.md; workflow/future-experiment-analysis-workflows.md; decision/wiki-scope-cross-repo-wintap-focused.md; tension/raw-telemetry-vs-normalized-wintap-semantics.md; tension/research-flexibility-vs-production-hardening.md; tension/etw-ebpf-and-cross-platform-compatibility.md.
Contradictions flagged: none.

## [2026-06-29] ingest | Dependency inventory and update status

Sources read: ../Wintap-Analytics/requirements.txt; ../Wintap-Analytics/Pipfile; ../Wintap-Analytics/2025-acme4-explore/pyproject.toml; ../Wintap-Analytics/2025-dmbd/requirements.txt; ../wintap/wintap/Wintap.Common.props; ../wintap/wintap/Wintap.csproj; ../wintap/wintap/Lintap.csproj; ../wintap/shared/Wintap-Workbench/package.json; ../wintap/shared/ai/wintap_mcp_server/wintap_mcp_server.csproj; ../wintap/devtools/requirements.txt; ../Lintap/pyproject.toml.
Update checks: npm outdated for Workbench runtime dependencies; PyPI JSON lookup for Python manifests; NuGet flat-container lookup for PackageReference entries because dotnet was unavailable. uv and dotnet were not installed, so lock-aware Python and restore-aware .NET checks were not performed.
Pages created: diagnostic/dependency-inventory-and-update-status.md.
Pages updated: index.md; log.md.
Contradictions flagged: none.

## [2026-06-30] methodology | [wintap] Methodology bootstrap

Decisions made: Adopted the Architect / Engineer / Developer role-separated workflow with per-developer wikis to avoid git conflicts — each dev only edited their own wiki directory. Adapted from the OpenCode setup and the Karpathy LLM-wiki pattern. Verification gate: stand up xUnit first (unit P1.1). Role boundaries enforced via subagent tool limits plus instruction discipline. Instruction/design/audit docs live under `developer_docs/`.
ADRs written or updated: none yet.
Wiki pages updated: none yet — the Wintap-side wiki was empty and awaiting first ingest.
Instructions written: none yet. Recommended next: P1.1 — stand up xUnit test project under `tests/`.
Open questions: Where exactly should the xUnit project sit relative to the multi-target agents (Wintap/Lintap/Mactap)? What is the first behavior worth covering with tests?

## [2026-06-30] decision | [wintap] P1.1 design settled (test harness)

Decisions made: Resolved both open questions from the bootstrap entry. Open Question 1 (placement) resolved: per-target test projects mirroring the multi-target agents (`tests/Wintap.Tests/`, `tests/Lintap.Tests/`, `tests/Mactap.Tests/`), chosen by the Architect. Open Question 2 (first behavior) resolved: a real test against `WintapMessage` — construct it and assert `MessageType` matches the `MessageTypeEnum` passed to the constructor. Reconciliation: because `WintapMessage` lives in cross-platform `shared/WintapAPI` while the agent projects are OS-bound, P1.1 stands up only `tests/Wintap.Tests/` now, referencing `shared/WintapAPI`; Lintap/Mactap siblings are deferred to P1.2.
ADRs written or updated: `wiki/decision/test-project-structure-and-first-test.md` (Accepted; migrated from `retired developer wiki`).
Wiki pages updated: none beyond the ADR and log.
Instructions written: `../wintap/developer_docs/instructions/P1.1-xunit-test-harness.md` (Status was Draft at the time of the original entry).
Open questions: P1.2 owed — stand up `tests/Lintap.Tests/` and `tests/Mactap.Tests/` siblings; decide per sibling whether it references shared code vs. the OS-bound agent. When the first genuinely Windows-agent-specific behavior is tested, `tests/Wintap.Tests/` will additionally reference `wintap/Wintap.csproj` and its `dotnet test` becomes Windows-only.

## [2026-06-30] decision | [wintap] Stage 0 locked (process identity & attribution contract)

Decisions made: Locked the Stage 0 canonical contract from the architecture assessment. Core owns `PidHash`/`ParentPidHash` generation; sensors supply a flat event-time-knowable field list; Stop events resolve identity and backfill required fields including `ParentPidHash` from a durable store; DuckDB is the starting substrate for durable persistence and hot-path attribution lookups; invariants are mechanism-agnostic so tests survive a later substrate change.
ADRs written or updated: `wiki/decision/process-identity-attribution-contract.md` (Accepted; migrated from `retired developer wiki`).
Wiki pages updated: none beyond the ADR and log.
Assessment updated: `../wintap/documentation/design/architecture-assessment.md` — appended DEC-001..DEC-004 to the Decisions Log; reworded INV-001..INV-005; annotated OQ-001/OQ-002/OQ-004 as resolved and OQ-003/OQ-005 as deferred.
Instructions written: none.
Open questions / follow-up: Stage 1 contract tests recommended next; DEC-004 is evidence-gated and the memory-first optimization should be revisited only if measurement shows a throughput/latency ceiling.

## [2026-07-06] maintenance | LLM-wiki contract alignment

Pages created: decision/feature-work-artifacts.md; concept/llm-assisted-feature-workflow.md; concept/feature-work-template.md; work/
Pages updated: index.md; AGENTS.md
Notes: Validated that all wiki pages have required frontmatter keys, have no broken wikilinks, and that `grounded_by` paths resolve. Added the optional feature-work module pages and aligned AGENTS.md directory names with the on-disk `wiki/decision/` and `wiki/tension/` layout.

## [2026-07-31] research | Lintap process creation validation thread

Sources read: ../wintap/wintap/platform/linux/sensor/ebpf/tracers/execve_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/tracers/clone_tracer.bpf.c; ../wintap/wintap/platform/linux/sensor/ebpf/ExecveSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs; ../wintap/wintap/platform/linux/sensor/ProcessRundownSensor.cs; ../wintap/wintap/platform/linux/sensor/ebpf/helpers/ProcReader.cs; ../wintap/wintap/core/shared/ProcessHash.cs; ../wintap/devtools/process_capture_smoke_test.py; ../../tetragon process lifecycle sources; ../../tracee process lifecycle sources; ../../sysdig capture selection sources; public GitHub issues/PRs for Tetragon, Tracee, and Falco/Sysdig process accuracy risks.
Pages created: work/lintap-process-creation-validation/index.md; work/lintap-process-creation-validation/research-snapshot-2026-07-31.md; work/lintap-process-creation-validation/handoff-validation-next-steps.md.
Pages updated: index.md; log.md.
Contradictions flagged: none.

## [2026-07-31] design | Sensor-neutral process validation harness

Sources read: ../wintap/devtools/process_capture_smoke_test.py; ../wintap/devtools/file_capture_smoke_test.py; ../wintap/devtools/network_capture_smoke_test.py; ../wintap/diagnostics/process-smoke-test/Program.cs; ../wintap/BUILD_AND_TEST.md; ../wintap/devtools/README.md.
Pages created: work/lintap-process-creation-validation/validation-harness-design.md.
Pages updated: work/lintap-process-creation-validation/index.md; index.md; log.md.
Contradictions flagged: none.

## [2026-07-31] test | Process validation mock checks on macOS

Commands run: Python frontmatter/wikilink/source-path checker for wiki/work/lintap-process-creation-validation; Python in-memory mock manifest/evaluator exercise for normalized process events.
Results: frontmatter, wikilinks, checked GROUND_TRUTH paths, and key local source paths passed. Mock evaluator produced expected fork, exec-attempt, exec-success, exit, parent-join, duplicate-start, and identity-collision metrics and detected one deliberately injected duplicate exec-success event.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Limitations: no Linux eBPF attachment, ring-buffer polling, Lintap Parquet output, live reference-sensor output, or load/loss behavior could be tested on macOS.

## [2026-07-31] setup | Linux VM setup for validation

Sources read: ../wintap/BUILD_AND_TEST.md; ../wintap/documentation/Linux Deployment Guide.md; ../wintap/wintap/Makefile; ../wintap/devtools/README.md; ../wintap/devtools/process_capture_smoke_test.py.
Pages created: work/lintap-process-creation-validation/linux-setup.md.
Pages updated: work/lintap-process-creation-validation/index.md; index.md; log.md.
Notes: Recommended Multipass for fastest repeatable CLI setup and UTM for kernel/distro control. Recommended running sensors and workloads inside the Linux VM, with macOS used for SSH orchestration and artifact copying.
Contradictions flagged: none.

## [2026-07-31] code | Initial process validation harness prototype

Files created: validation/process-creation/pyproject.toml; validation/process-creation/uv.lock; validation/process-creation/README.md; validation/process-creation/src/wintap_process_validation/*; validation/process-creation/tests/*.
Implemented: uv-managed Python package with manifest schema, workload generator, mock normalized event writer, evaluator metrics, Lintap process row normalizer, and CLIs `wpv-workload`, `wpv-mock-run`, `wpv-evaluate`, `wpv-normalize-lintap`.
Tests run: `uv run --extra dev pytest` in validation/process-creation, result 5 passed. Also ran `wpv-workload` and `wpv-mock-run` on macOS; execveat was skipped with a manifest note because macOS lacks `os.execveat`, and mock evaluation detected the intentionally injected duplicate exec-success row.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Limitations: live Linux eBPF, Lintap Parquet normalization, and reference sensor output remain untested until a Linux VM is available.

## [2026-08-06] test | Multipass Lintap process smoke test

Environment: Multipass Ubuntu 24.04 arm64; kernel 6.8.0-136-generic; BTF present; Wintap branch feature-branch at 7f93255.
Commands run: VM toolchain checks; `make build_ebpf`; `make build_dotnet`; `UV_PROJECT_ENVIRONMENT=<local-path> uv run --extra dev pytest`; `UV_PROJECT_ENVIRONMENT=<local-path> uv run wpv-mock-run`; `sudo python3 devtools/process_capture_smoke_test.py --start-lintap --lintap-dll <local-path> --timeout 240 --poll-interval 5`.
Results: eBPF and .NET builds passed; validation harness tests passed with 5 tests; mock run passed and detected expected duplicate exec-success warning; Lintap process smoke test passed.
Fixes made: Wintap eBPF tracer now uses `task_struct.start_time` for Ubuntu arm64 CO-RE compatibility; ExecveSensor/CloneSensor attach extra programs by program name instead of unavailable `bpf_object__find_program_by_title`; ExecveSensor parent hash conversion now matches `/proc` clock-tick semantics and uses eBPF parent attribution as fallback; process smoke test ignores `.parquet.active` files and relaxes execveat flag validation when Python lacks `os.execveat`.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Limitations: reference sensors not yet run; true `execveat(2)` validation still needs a C workload because Ubuntu Python 3.12 lacks `os.execveat`.

## [2026-08-06] test | Lintap noisy process state table run

Environment: Multipass Ubuntu 24.04 arm64; Wintap branch feature-branch; Lintap resolver-mode config with Execve and Exit enabled, direct parquet and Esper send disabled, Clone/Network/FileOps/Rundown disabled.
Workload: `wpv-noisy-processes` for 780 seconds, 1888 manifest processes across 166 cases, combining short-lived `bash` processes and longer-lived Python sleep processes.
Fixes applied before final run: disabled BPF diag monitor by default; captured process `task_struct.start_time` in exec eBPF events; used eBPF process start time when `/proc` is unavailable; filtered CO-RE exit tracer to thread-group leader exits; stopped inserting unmatched Stop-only rows; added pending-exit reconciliation in ProcessResolver; made GetPidHash respect exit_time.
Results: final noisy run `noisy-state-1786064182` observed all 1888 manifest PIDs in the `process` table. Table had 1983 rows, 1924 distinct process IDs, 1923 closed rows, and 60 open rows. Manifest-specific open rows were 59/1888, mostly short-lived bash. Final process smoke test also passed after the fixes.
Artifacts: validation/process-creation/noisy-state-summary-multipass-2026-08-06.json; validation/process-creation/smoke-15m-summary-multipass-2026-08-06.json.
Limitations: residual open rows remain; true execveat still needs a C workload; reference sensors were not run.

## [2026-08-06] checkpoint | Process validation implementation commit point

Summary: Prepared commit checkpoint after implementing the first executable validation harness, Multipass setup updates, Lintap eBPF/process-state fixes, and noisy process-state tests.
Validated: Wintap build passed in Multipass; validation harness tests passed on macOS and Linux; Lintap process smoke passed; five 15-minute smoke rounds passed; noisy resolver-mode run observed 1888/1888 manifest PIDs with 60 open process rows remaining.
Pages updated: work/lintap-process-creation-validation/validation-harness-design.md; log.md.
Open follow-up: run a longer one-hour noisy process-state test and investigate the residual short-lived open rows.

## [2026-08-06] test | One-hour Lintap noisy process state run

Environment: Same Multipass Ubuntu 24.04 arm64 validation VM and Wintap process-state fixes as prior noisy run.
Workload: `wpv-noisy-processes` for 3600 seconds with 8732 manifest processes across 767 cases.
Results: all 8732 manifest PIDs were observed in the DuckDB `process` table. Table totals were 10372 rows, 10064 distinct process IDs, 10060 closed rows, and 312 open rows. Manifest-specific open rows were 285/8732, concentrated in short-lived bash workload rows. Longer-lived Python workload rows closed cleanly. A post-run Lintap process smoke test passed.
Artifact: validation/process-creation/noisy-state-1h-summary-multipass-2026-08-06.json.
Limitations: residual short-lived open rows remain; reference sensors and true C-based execveat workload not yet tested.

## [2026-08-06] checkpoint | Current process validation state

Pages created: work/lintap-process-creation-validation/current-state-2026-08-06.md.
Pages updated: work/lintap-process-creation-validation/index.md; index.md; log.md.
Summary: Recorded current commits, validation harness state, one-hour noisy run results, known residual short-lived process leakage, and next-step recommendations.

## [2026-08-07] test | 30-minute all-events normal ETL Parquet run

Environment: Multipass Ubuntu 24.04 arm64; Lintap normal ETL/Parquet config with process, clone, exit, network, file, and process rundown sensors enabled; direct Parquet disabled.
Workload: Existing process/file/network smoke tests plus `wpv-noisy-processes` during a 1878-second capture window.
Results: process smoke passed; file smoke passed; network smoke failed. No TCP/UDP/raw_process_conn_incr Parquet rows were found. Parquet outputs included fileserializer=2996 rows, processserializer=57 rows, processstopserializer=26 rows, raw_process=32013 rows, raw_process_file=300000 rows, raw_host=1 row, raw_macip=1 row. Network logs showed BPF diag misses (`STORE/HIT/MISS = 0/0/62`) but no normal network rows.
Artifacts: validation/process-creation/all-events-30m-summary-multipass-2026-08-07.json; validation/process-creation/all-events-30m-parquet-summary-multipass-2026-08-07.json; validation/process-creation/all-events-30m-network-smoke-multipass-2026-08-07.out.
Open follow-up: diagnose network eBPF/socket PID attribution and why network telemetry is not materialized under normal ETL output.

## [2026-08-07] fix | Network program attachment compatibility

Root cause: NetworkSensor used `bpf_object__find_program_by_title` for additional program attachment, but Ubuntu 24.04 arm64 libbpf did not export that symbol. The network sensor failed startup after the primary program loaded, leaving only diagnostic output and no normal network rows.
Fix: NetworkSensor now attaches additional network programs by BPF function name using `bpf_object__find_program_by_name`, and its diagnostic reporter is gated by `EnableBpfDiagMonitor`.
Validation: direct-Parquet network smoke passed. A short normal ETL all-events run also passed process, file, and network smoke and produced `raw_process_conn_incr` TCP/UDP rows: tcp=165 rows, udp=33 rows.
Artifacts: validation/process-creation/all-events-10m-summary-multipass-2026-08-07.json; validation/process-creation/all-events-10m-parquet-summary-multipass-2026-08-07.json; validation/process-creation/all-events-10m-network-smoke-multipass-2026-08-07.out.

## [2026-08-07] test | One-hour all-events normal ETL dataset with pidstat

Environment: Multipass Ubuntu 24.04 arm64. Normal ETL/Parquet run with process, clone, exit, network, file, and rundown sensors enabled; direct Parquet disabled. Separate pidstat collector wrote to `$WINTAP_DATA_ROOT/pidstat`.
Data root: `<local-path>` in VM, mounted to `<local-path>` on Mac.
Results: process smoke passed; network smoke passed; file smoke failed exact-path validation. Dataset includes pidstat CSV with 47454 lines. Raw sensor outputs include raw_process=67600 rows across hour partitions, raw_process_conn_incr tcp=1409 rows, raw_process_conn_incr udp=62 rows, raw_process_file=560000 rows, plus host/macip rows. Serializer outputs include fileserializer=49591 rows, processserializer=3763 rows, processstopserializer=485 rows, tcpconnectionserializer=108 rows.
Artifacts: validation/process-creation/all-events-1h-summary-multipass-2026-08-07.json; validation/process-creation/all-events-1h-parquet-summary-multipass-2026-08-07.json; validation/process-creation/all-events-1h-file-smoke-multipass-2026-08-07.out; validation/process-creation/all-events-1h-network-smoke-multipass-2026-08-07.out.
Open follow-up: investigate file smoke exact-path miss despite large file telemetry volume.

## [2026-08-11] ingest | raw/Agentic_Coding_for_eBPF.md brainstorming note

Source: raw/Agentic_Coding_for_eBPF.md (previously untracked; added SOURCE/RETRIEVED provenance header — exact origin unrecorded, likely Confluence-retrieved AI-assistant output dated 2026-07-16/17).
Pages created: concept/agentic-ebpf-probe-development.md (confidence low; all claims flagged SPECULATIVE pending verification).
Pages updated: index.md; work/lintap-process-creation-validation/index.md (open question: Sysmon for Linux and Bombini as candidate reference sensors); tension/etw-ebpf-and-cross-platform-compatibility.md (prior-art note: Sysmon for Linux as Windows-event-to-eBPF mapping precedent).
Contradictions flagged: none. Tetragon/Tracee/Falco framing is consistent with the 2026-07-31 research snapshot; new material is the agentic-tooling survey (MCPtrace, GPTtrace, eunomia-bpf/Wasm-bpf) plus Sysmon for Linux and Bombini as unexamined reference candidates.
Notes: nothing on the new page is source-grounded, unlike the validation thread's snapshot pages; verification of tool existence/capability is an explicit open question.

## [2026-08-11] ingest | raw/Agentic_Coding_for_eBPF.md brainstorming note

Source: raw/Agentic_Coding_for_eBPF.md (untracked brainstorming note dated 2026-07-16; provenance header added — exact origin unrecorded, likely Confluence-retrieved AI-assistant output with unresolved domain-level citations).
Pages created: concept/agentic-ebpf-probe-development.md (confidence: low; all claims flagged SPECULATIVE pending verification).
Pages updated: index.md (new concept row); work/lintap-process-creation-validation/index.md (open question: Sysmon for Linux and Bombini as candidate additional reference implementations); tension/etw-ebpf-and-cross-platform-compatibility.md (prior-art note: Sysmon for Linux as Windows-event-to-eBPF mapping precedent).
Contradictions flagged: none. Tetragon/Tracee/Falco framing consistent with research-snapshot-2026-07-31; new material limited to agentic tooling (MCPtrace, GPTtrace, eunomia-bpf/Wasm-bpf), Sysmon for Linux, and Bombini.
Open follow-up: verify existence/viability of MCPtrace and GPTtrace before any adoption discussion; decide whether Sysmon for Linux warrants a local checkout and source-inspection pass as a fourth reference sensor.

## [2026-08-11] ingest | Wintappy (Wintap-PyUtil) repo added to ecosystem scope

Source: `../Wintappy` (README.md, pyproject.toml, wintap_dbt/, review-notes/Architecture.md, DataModel.md, ProjectSummary.md, OpenQuestions.md, ImplementationStatus.md), plus this repo's `streamlit/projects/common/dqautil.py` and `streamlit/projects/DataQA/pages/raw_events.py`.
Summary for human: Wintappy is a fourth core repo in this ecosystem — the canonical Python/DBT/DuckDB post-processing pipeline that turns `raw_sensor` parquet from Wintap/Lintap into bronze/silver/gold analysis-ready models (`process`, `process_path`, `process_summary`, `process_uber_summary`, etc.), superseding a legacy Python ETL path (`rawtorolling`/`rawtostdview`/`ubersummary`) that remains only as reference tooling. It was already referenced by name ("Wintap-PyUtil/wintap_dbt") in the existing Lintap and ETW/eBPF tension pages but had no repo page of its own — an orphan-reference gap this ingest closes. Notably, Wintap-Analytics' own Streamlit DataQA/eda apps import the `wintappy` package directly, making it a runtime code dependency, not just an output-data producer.
Pages created: repo/wintappy-pipeline-repo.md (confidence: high); tension/dbt-duckdb-output-vs-legacy-stdview-parquet.md (confidence: medium, status: open — Wintappy's DuckDB-only current output vs. this repo's documented expectations of published stdview-* parquet).
Pages updated: index.md; AGENTS.md (Repository Layout, repo_scope/implementation_area enums, Domain Context, Operating Modes sibling-repo lists); repo/wintap-analytics-host-repo.md (pipeline dependency section); repo/lintap-supporting-repo.md (link Wintap-PyUtil citation to new page); decision/wiki-scope-cross-repo-wintap-focused.md (extend scope to include Wintappy); component/wintap-api-shared-data-model.md; event_type/process-events.md; event_type/file-events.md; event_type/network-events.md (downstream DBT model cross-links); workflow/future-experiment-analysis-workflows.md (identifies Wintappy as the builder of the standard views this page discusses).
Contradictions flagged: none hard. One new open tension (soft framing gap, not a factual conflict): Wintappy's own review notes mark `stdview-*` parquet as superseded by DBT/DuckDB, while this repo's ACME4/workshop material still documents fetching `stdview`-shaped published parquet datasets; captured as tension/dbt-duckdb-output-vs-legacy-stdview-parquet.md rather than resolved, per Wintappy's own open-questions tracker treating it as unresolved.

## [2026-08-11] update | LLM-assisted feature workflow ported from prior analytics repository

Source: prior analytics repository wiki (wiki/concepts/llm_assisted_feature_workflow.md, wiki/concepts/feature_work_template.md, wiki/work/firmware-corpus/dev_handoff.md), adapted to this wiki's frontmatter contract.
Pages updated: concept/llm-assisted-feature-workflow.md (added when-to-use/skip guidance, grounding practices, dev-handoff stage, operating rule for promoting durable facts, invocation expected behavior); concept/feature-work-template.md (full markdown skeletons for all artifacts — brief, references, design, spike, implementation_plan, dev_handoff, verification — plus an optional research-thread index.md skeleton modeled on the lintap validation thread; only brief.md required); index.md.
AGENTS.md updated: wiki/work/ added to Repository Layout; wiki-maintainer mode gains feature-work uses and the skeleton invocation phrase; code-development mode gains handoff-reading and verification/implementation-plan update rules.
Contradictions flagged: none. Prior stub declared five artifacts "required"; replaced with prior analytics repository's brief.md-only-required stance, matching actual practice in both repos. Existing work/lintap-process-creation-validation folder is grandfathered as the research-thread pattern rather than retrofitted.
Notes: decision/feature-work-artifacts.md intentionally left abbreviated; prior analytics repository retains the full rationale/alternatives history.

## [2026-08-11] feature-work | improve-pidstat-collector started via LLM-assisted feature workflow

Source: raw/Issues/Long_Running_Cleanup.md ("Improve pidstat-collector.sh to run alongside lintap and push data to S3"), plus source inspection of ../Lintap/pidstat-collect.sh, ../Lintap/teletap/*.sql, ../Wintappy/wintap_dbt pidstat macros and bronze/silver models, and ../wintap/wintap/core/etl/load upload adapters.
Pages created: work/improve-pidstat-collector/brief.md (problem, goals, acceptance criteria, open questions, test plan); work/improve-pidstat-collector/references.md (cross-repo source map). First use of the ported feature-work template; design/spike/implementation_plan deferred until the brief's open questions are decided.
Pages updated: index.md (two new Work rows).
Contradictions flagged: none. Noted for design: the lintap validation thread treats ../wintap (Linux/eBPF branch) as canonical Lintap source while the collector script lives in legacy ../Lintap — code-location open question in the brief.
Key facts captured: DBT reads $PIDSTAT_DATA_PATH/**/*.csv tab-delimited with hardcoded columns (rotation-friendly glob already); observed volume 47454 lines/hour at 2s interval; sensor upload pipeline (CacheManager + S3Adapter) is a candidate ride-along path.

## [2026-08-11] feature-work | improve-pidstat-collector: brief decided, design and plan added

Source: human edits to work/improve-pidstat-collector/brief.md (decisions in Goals), plus source verification of ../wintap/wintap/core/etl/load/CacheManager.cs, RawSensorWriter.cs, and adapters/base/Uploader.cs.
Decisions recorded: new script in ../Lintap (old script kept as example); continuous service; 5s configurable interval; parquet output; rotation on the sensor merge cycle with dayPK=/hourPK= partitioning; S3 via the sensor's existing upload mechanism.
Verified mechanism facts: CacheManager.upload() sweeps all *.parquet under raw_sensor/ type-agnostically; Uploader_UploadCompleted deletes after successful upload (local retention free); S3 keys mirror the local relative path; *.active is the existing in-progress-file convention. Ride-along therefore needs no C# changes.
Pages updated: work/improve-pidstat-collector/brief.md (reconciled human decisions: DBT compatibility goal switched to deliberate versioning since parquet breaks the hardcoded tab-CSV bronze reader; acceptance criteria, affected areas, test plan, open questions aligned; ..\Lintap path typo normalized); index.md.
Pages created: work/improve-pidstat-collector/design.md (approach, grounded mechanism facts, edge cases, risks incl. the implicit ride-along contract, alternatives, remaining open questions); work/improve-pidstat-collector/implementation_plan.md (8 steps; flags that ../Lintap and ../Wintappy writes need explicit sibling-repo authorization).
Contradictions flagged: none hard. Human decision "output should be parquet" superseded the brief's original preserve-CSV-compatibility goal; reconciled as a deliberate coordinated Wintappy change rather than left as a conflict.

## [2026-08-11] feature-work | improve-pidstat-collector: dev handoff prepared

Source: work-folder artifacts (brief/design/implementation_plan/references), following the dev_handoff skeleton in concept/feature-work-template.md (first use).
Pages created: work/improve-pidstat-collector/dev_handoff.md — written to be self-contained for a fresh agent on a different system: copy/paste prompt activates code-development mode, grants explicit authorization for ../Lintap only (../wintap and ../Wintappy stay read-only this slice), lists environment expectations (sibling checkouts, pidstat/duckdb/shellcheck, no assumed S3), scopes the first slice to implementation plan steps 1–4 with systemd packaging as stretch, and assigns verification.md/implementation_plan.md/log.md upkeep duties.
Pages updated: index.md.
Contradictions flagged: none.
Notes: this is the workflow's first cross-system handoff test; verification.md is intentionally not pre-created — the dev agent creates it from the template when work starts.

## [2026-08-12] code | Improve pidstat collector first slice

Files created: `../Lintap/pidstat-collector.sh`; `../Lintap/tests/pidstat-collector-tests.sh`; `wiki/work/improve-pidstat-collector/verification.md`.
Pages updated: `wiki/work/improve-pidstat-collector/design.md`; `wiki/work/improve-pidstat-collector/implementation_plan.md`; `wiki/index.md`; `wiki/log.md`.
Results: verified Linux ride-along behavior read-only (`CacheManager` upload loop runs when ETL is enabled, shipped `UploadIntervalSec` is 300, shipped `S3Adapter` remains disabled unless deployment config enables it); implemented spool-then-parquet collector in `../Lintap` with wall-clock rotation, startup salvage, and oldest-first accumulation guard; shell tests passed (4); short live smoke run produced readable parquet from real `pidstat` output.
Limitations: `shellcheck` missing on host; no S3 upload exercised; systemd packaging and Wintappy parquet reader change remain later slices.

## [2026-08-12] test | Improve pidstat collector 15-minute run

Command: `timeout --signal=TERM 905 env WINTAP_DATA_ROOT=<local-path> ../Lintap/pidstat-collector.sh`.
Results: collector ran for 15 minutes with default 5-second sampling and 300-second rotation, producing 4 parquet files under `parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=08/`; DuckDB loaded 15 rows across the files.
Manual follow-up: inspect `<local-path>`.

## [2026-08-12] fix | Improve pidstat collector row-loss bug

Diagnosis: the bad 15-minute output was caused by `normalize_pidstat_line()` inheriting the loop's empty `IFS` and using the wrong field count/index for `pidstat` rows. In practice it only retained commands with embedded spaces, which collapsed the dataset to one `tmux: server`-style row per minute.
Fix: made the parser split on explicit shell whitespace and corrected the `Command` field index/count; added a regression test covering normalization inside the collector's `while IFS= read -r line` loop.
Validation: shell test suite now passes with 5 tests, and a post-fix smoke run at `<local-path>` produced 307 rows in ~16 seconds from the real collector.

## [2026-08-12] fix | Improve pidstat collector joined-record recovery

Diagnosis: a later 15-minute run showed occasional conversion failures because some raw `pidstat` chunks arrived with two records glued together at the sample boundary. The parser was treating the second raw record as part of the first row's command payload.
Fix: made `normalize_pidstat_line()` split glued timestamp tokens, detect a next-record start at the command boundary, and emit multiple normalized rows from one joined raw chunk; added a deterministic joined-record regression test plus a live row-preservation validation that checks raw-detail-row count == normalized-row count == parquet-row count.
Validation: shell test suite now passes with 7 tests.

## [2026-08-12] test | Improve pidstat collector clean 15-minute run

Command: `timeout --signal=TERM 905 env WINTAP_DATA_ROOT=<local-path> ../Lintap/pidstat-collector.sh`.
Results: collector ran cleanly for 15 minutes with explicit `-p ALL`, default 5-second sampling, and 300-second rotation. It produced 4 parquet files under `parquet/raw_sensor/pidstat/dayPK=20260812/hourPK=09/`; DuckDB loaded `59097` rows total with per-file counts `4731`, `19839`, `19631`, and `14896`.
Manual follow-up: inspect `<local-path>`.

## [2026-08-12] feature-work | improve-pidstat-collector: slice-1 review accepted, slice-2 handoff prepared

Source: independent review of ../Lintap c76ea87 and this repo's c16c6b7/c77f026 (test suite re-run on reviewer host: 7/7 passed; sibling-repo boundary check clean; parquet schema confirmed against stg_pidstat_metrics + hostname).
Review verdict: slice accepted. Findings: (1) -p ALL sampling deviated from design — accepted per human decision, documented as a post-review decision in design.md with the ETL-layer-reduction rationale (~5.7M rows/day observed baseline); (2) processing-time sample_date gives ~24h-forward timestamps at midnight; (3) partially malformed glued chunks drop valid leading records; (4) DuckDB conversion errors are swallowed. Findings 2-4 assigned to slice 2.
Pages updated: design.md (post-review -p ALL decision; collector-loop command corrected to include -p ALL); verification.md (Independent Review section); implementation_plan.md (renumbered to nine steps, slice-2 scope marked, review follow-ups added as step 6, checklist expanded); dev_handoff.md (rewritten for slice 2: review fixes, systemd, Wintappy DBT parquet migration; authorization widened to ../Lintap + ../Wintappy, ../wintap still read-only); index.md.
Contradictions flagged: none. The dev's deployment finding (S3Adapter disabled in shipped ETLConfig.json) refines rather than contradicts the design's ride-along mechanism; carried into slice-2 scope and the closeout list.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: feature started

Source: raw/Issues/Long_Running_Cleanup.md (~8M process rows over 10 days, ~1/3 with exit codes, CPU-load-grows-with-DB-size hypothesis), plus source inspection of ../wintap/wintap/core/infrastructure/ProcessResolver.cs (insert-on-Start/update-on-Stop, no delete path; ClearDB only called from Windows ProcessSensor.Initialize), EventChannel.cs (per-event ResolveProcessAtTime + GetPidHash fallback hot path), and ProcessSensor.cs (whole-table replay at startup).
Pages created: work/fix-unbounded-process-table-growth/brief.md (problem, integrity constraints, retention + stale-open reconciliation goals, acceptance criteria, open questions, test plan); work/fix-unbounded-process-table-growth/references.md (change-site map, validation baseline, DuckDB space-reclamation questions).
Pages updated: index.md (two new Work rows).
Contradictions flagged: none. Boundary noted: this feature tolerates missed terminations; fixing their sensor-level root cause stays in the lintap-process-creation-validation thread (~3.3% residual open-row baseline, 2026-08-06). The improve-pidstat-collector feature explicitly deferred the event_store cleanup routine to this feature.
Key facts captured: process table is unbounded within and across runs on Linux (no ClearDB call); all hot-path queries filter unindexed process_id; GetPidHash already has a /proc start-time fallback usable after pruning; design/implementation_plan deferred until the brief's open questions (retention window, stale-open policy, cleanup scheduling, DuckDB space reclamation) are decided.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: stale-open policy decided

Source: human decision in conversation.
Decision recorded: the stale-open reconciliation is liveness-check-based (query /proc on Linux / process snapshot on Windows, close rows for dead PIDs with a synthesized exit_time), and the cross-check is to be implemented as an inherent QA feature — each sweep emits telemetry distinguishing rows closed by real Stop events from rows closed by reconciliation, making sensor termination-tracking quality measurable from a running instance. This supersedes the pure age-based alternative.
Pages updated: work/fix-unbounded-process-table-growth/brief.md (Goals decision note, acceptance criterion for QA telemetry, open question closed with remaining design details: sweep cadence and QA telemetry surface).
Contradictions flagged: none. Note: the QA telemetry deliberately takes over the role of the harness-side stop_only_like metric, which the lintap-process-creation-validation thread had flagged as unreliable after pending-exit reconciliation.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: cleanup scheduling left to developer

Source: human decision in conversation.
Decision recorded: where the cleanup/reconciliation sweep runs (ProcessResolver timer vs. merge/upload cycle vs. EventChannel-driven) is explicitly left to the implementing developer's discretion — it is an implementation detail, not an architectural constraint. The chosen mechanism and rationale are to be recorded in design.md or verification notes when decided.
Pages updated: work/fix-unbounded-process-table-growth/brief.md (open question closed with the delegation note).
Contradictions flagged: none.
Remaining open questions in the brief: retention grace window for exited rows, pruned-row lookup fallback/metrics, DuckDB space reclamation behavior, Windows startup-replay constraints, optional hard-cap backstop.

## [2026-08-12] feature-work | fix-unbounded-process-table-growth: hand edits reconciled, dev handoff prepared

Source: human edit to work/fix-unbounded-process-table-growth/brief.md (retention-miss open question decided: track as retention-miss metric), reconciled into standard decided-question format; dev_handoff.md written per the feature-work template.
Decisions now recorded (3): liveness cross-check as inherent QA feature; cleanup scheduling at developer discretion; pruned-row lookup misses tracked as retention-miss metric (fallback still fires, misses counted for retention-window tuning).
Pages updated: brief.md (retention-miss decision formatted, matching acceptance criterion added); references.md (Decisions To Date section for the dev agent; /proc liveness marked as the decided reconciliation mechanism; retention-miss note on GetPidHash fallback); index.md (dev_handoff row, references summary refreshed).
Pages created: dev_handoff.md — copy/paste prompt authorizing ../wintap changes (../Lintap and ../Wintappy stay read-only; Wintap-Analytics writable only under validation/ and wiki/), summary of mechanism and hard integrity constraints, delegated decisions (scheduling, cadence, telemetry surface, default retention window, DuckDB reclamation), first slice scoped to sweep + reconciliation + QA telemetry + short validation run, multi-day CPU-correlation study deferred to a later slice, closeout duties including developer-authored design.md recording delegated decisions.
Contradictions flagged: none. Remaining open questions (retention window default, DuckDB reclamation mechanics, Windows replay constraints, hard-cap backstop) are delegated to the dev agent to resolve by measurement and record in design.md.

## [2026-08-13] code | Fix unbounded process table growth first slice

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs`; `validation/process-creation/scripts/summarize_lintap_process_table.py`; `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`.
Pages created: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/implementation_plan.md`; `work/fix-unbounded-process-table-growth/verification.md`.
Pages updated: `index.md`; `log.md`.
Results: implemented resolver-owned periodic maintenance with configurable exited-row retention, liveness-based stale-open reconciliation, in-memory recently-pruned PID cache for retention-miss attribution, and DuckDB telemetry table `process_retention_telemetry` for `stop_closed` / `reconciled_closed` / `retention_deleted` / `retention_miss`. Validation in Multipass `validation-host`: `Lintap.csproj` build passed, validation pytest passed (`5 passed`), `Wintap.csproj -p:EnableWindowsTargeting=true` passed after fixing an unrelated missing `using System.IO;` import in `WindowsStateManager.cs`, and a 180-second noisy retention run with aggressive sweep settings produced telemetry totals `stop_closed=507`, `reconciled_closed=28`, `retention_deleted=499` with final process-table size `47` rows.
Limitations: no long-duration plateau/perf run yet, no DuckDB compaction measurement yet, and the short noisy run is not sufficient to tune the final production retention window.

## [2026-08-13] test | Fix unbounded process table growth rundown rerun

Files changed: `validation/process-creation/scripts/summarize_lintap_process_table.py`; `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: summary now reports end-of-run live system process count and open-row liveness classification. Re-checking the earlier short run showed `live_system_processes=143` with the lone tracked-open row classified as stale, clarifying that `open_rows=1` was never a claim that only one Linux process existed. A rerun with `ProcessRundown=true` still ended with `tracked_open_rows=1`, `live_open_rows=0`, `stale_open_rows=1`, while the VM had `live_system_processes=141` and telemetry totals `stop_closed=456`, `reconciled_closed=173`, `retention_deleted=590`.
Open issue surfaced: the new rundown-enabled result suggests a mismatch between rundown-seeded process rows and the liveness-based reconciliation logic, because many apparently live pre-existing processes were counted as reconciliation-closed instead of remaining open/live-tracked.

## [2026-08-13] fix | Add pid_hash to process retention telemetry

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`.
Pages updated: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: `process_retention_telemetry` now stores per-event telemetry rows with `pid_hash` in addition to `metric_name`, `process_name`, and `metric_value`, and the resolver emits telemetry at process-instance granularity rather than only as process-name aggregates. This preserves the existing summary rollups while allowing later joins back to process identity.

## [2026-08-13] fix | Rundown liveness reconciliation accuracy

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `validation/process-creation/scripts/summarize_lintap_process_table.py`.
Pages updated: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Investigation: the new end-of-run summary fields showed that `ProcessRundown=true` initially preserved almost none of the current live process set (`1/141` tracked-open rows in a short run). First fix aligned the resolver's Linux live-start hash derivation with the same `/proc/stat` boot-time basis used by the rundown and exec sensors. That recovered the boot-time process population but still left a subset of long-lived non-boot services (`cron`, `dbus-daemon`, `systemd-networkd`, repeated `sshd`/`sshfs`/`sudo`) being reconciled closed. Final fix made Linux reconciliation use `ProcReader.ReadProcessInfo()` directly and treat close live-start-time matches as the same process instance, preserving or repairing the row instead of closing it.
Validation: a clean 90-second rundown-enabled run (`retention-rundown-fix3b-1786645301`) finished with `live_pids_with_matching_open_row=139/143`, and the previously missing long-lived daemon set stayed open with `exit_time IS NULL`. A 10-minute aggressive-retention run (`retention-rundown-10m-1786645515`) held `live_pids_with_matching_open_row=130/138`; the remaining misses were recent end-of-run processes rather than long-lived baseline services. Telemetry totals for the 10-minute run were `stop_closed=524`, `reconciled_closed=48`, `retention_deleted=541`.
Open follow-up: the remaining small set of misses/stale opens appears to be dominated by shutdown/final-window timing rather than the original rundown identity bug.

## [2026-08-13] fix | End-of-run live snapshot coverage

Files changed: `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`; `validation/process-creation/scripts/summarize_lintap_process_table.py`.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: the validation harness now snapshots `/proc` immediately before shutting down `Lintap` and scores coverage against that pre-stop live process set. This removes the previous measurement artifact where post-stop `python3`/`duckdb` summary processes inflated the apparent miss count. Validation: a snapshot-based 90-second run reached `140/142` live snapshot PIDs covered with `1` stale open row; a snapshot-based 10-minute run reached `131/139` live snapshot PIDs covered with `2` stale open rows. Remaining misses are now a small real tail rather than shutdown-summary self-noise.

## [2026-08-13] validation | Clone sensor closes remaining live-process coverage gap

Files changed: `validation/process-creation/scripts/run_lintap_noisy_state_test.sh`.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.
Results: tightened the live snapshot filter further by excluding the snapshot helper's ancestor chain, which produced a clean clone-disabled 90-second run with `135/135` live snapshot PIDs covered. Investigation of the remaining misses on longer clone-disabled runs showed they were fork-without-exec processes. Added a `CLONE_SENSOR` toggle to the validation runner and reran with `Clone=true`: the 90-second run reached `135/135` live snapshot PIDs covered and the 10-minute run reached `137/137` live snapshot PIDs covered, both with `0` missing live PIDs. Conclusion: the currentish process table is accurate at shutdown when the clone sensor is enabled; the prior residual misses were a sensor-selection issue, not a remaining retention/reconciliation defect.

## [2026-08-13] review | fix-unbounded-process-table-growth slice 1 accepted

Source: independent review of ../wintap 9d9c6fb and this repo's 22702eb/3483ab6/4c797b3. Re-verified in validation-host: Lintap.csproj build (0 errors), validation pytest (5 passed).
Review verdict: slice 1 accepted. Integrity constraints hold by construction (retention delete cannot touch open rows; reconciliation gated by min-age + live-hash mismatch, with start-time-tolerance repair and collision guard). The QA-telemetry-first design surfaced the rundown reconciliation bug via its own metrics — the design decision paid for itself in slice 1.
Findings (minor): (1) Windows runtime behavior compile-verified only — added to Known Gaps and the closeout checklist; (2) GetLinuxBootTimeUtc caches DateTime.UtcNow if btime is unparseable — silent wrong-hash fallback should not be cached; (3) repair-collision warnings re-log uncapped every sweep.
Pages updated: work/fix-unbounded-process-table-growth/verification.md (Independent Review section; Windows-runtime Known Gap); implementation_plan.md (slice-1 acceptance checked; remaining-before-closeout checklist with promotion candidates: event-store currentish retention semantics + env knobs + process_retention_telemetry, /proc btime hash basis, clone-sensor requirement for fork-without-exec coverage); dev_handoff.md (context list expanded to include design/plan/verification); index.md.

## [2026-08-13] test | Windows process table retention runtime check

Environment: Windows validation host; Wintap service deployed from `<local-path>` to `<local-path> Files\Wintap`; validation harness run from `<local-path>` using `uv`.
Commands/actions: `uv run --extra dev pytest`; fixed Windows harness assumptions (`/bin/sh`, `bash`, `sudo duckdb`); fixed current Wintap Windows compile by removing the direct Linux `ProcReader` compile dependency from `ProcessResolver.cs`; `dotnet publish "wintap\Wintap.csproj" -c Debug -r win-x64 --self-contained false`; redeployed Wintap; ran elevated service-mode noisy process workload with aggressive retention settings.
Results: Windows `uv` test suite passed (`5 passed`); Wintap publish passed; service-mode retention run `windows-retention-smoke-20260813143307` produced `390` manifest processes across `35` cases. Final process table had `278` rows (`223` closed, `55` open); `process_retention_telemetry` was present with `reconciled_closed=755` and `retention_deleted=532`. Wintap logs confirmed `ProcessResolver retention: enabled=True` and Windows stale-open reconciliation via `Process.GetProcessById`.
Limitation: this host logged `Log wrap detected! Unable to build process tree, computer reboot required.`, so full Windows `ClearDB` + Security-log startup replay remains unverified; real-time capture, liveness reconciliation, retention deletion, and telemetry were verified.
Pages updated: work/fix-unbounded-process-table-growth/verification.md (marked as `starting-point`); work/fix-unbounded-process-table-growth/implementation_plan.md; index.md; log.md.
Contradictions flagged: none. Cross-feature note: the CPU-vs-table-size correlation step depends on pidstat collector data — pidstat slice 2 (systemd + Wintappy parquet migration) is still pending and unblocks the correlation study.

## [2026-08-13] update | Interview stage added to LLM-assisted feature workflow

Pages updated: `concept/llm-assisted-feature-workflow.md` (new Interview stage row in the stages table; new Interview Stage section defining the protocol — ground in wiki/repo context first, ask adaptive 2–4-question batches, classify answers as decision/constraint/delegated/deferred, stop when the brief can be stated without guessing, play back for confirmation before writing brief.md; invocation now runs the interview by default with a `(no interview)` opt-out); `concept/feature-work-template.md` (optional `interview.md` artifact added to the skeleton list plus a condensed-log template with Interview Log rounds, Decisions/Constraints/Delegations/Deferred sections, and Playback Summary); `AGENTS.md` (wiki-maintainer-mode invocation description now includes the interview step and opt-out); `index.md` (concept summaries refreshed).
Contradictions flagged: none. Rationale: the workflow previously jumped straight from the invocation phrase to skeleton creation, leaving the agent to guess brief content; the interview makes context-building between human and AI an explicit first-class stage while keeping brief.md the single distilled source of truth.

## [2026-08-13] feature | improve-windows-process-collection started via LLM-assisted feature workflow

Pages created: `work/improve-windows-process-collection/interview.md`, `brief.md`, `references.md`, `design.md`. Pages updated: `index.md`; `log.md`.
Interview (3 rounds, all decisions confirmed by human playback): kernel ETW (classic NT Kernel Logger Process events on the shared KernelSession) becomes the single real-time source for process lifecycle; the Security-log 4688/4689 path and the separate KernelProcessSensor are consolidated into one new WindowsProcessSensor (rich stop metrics retained via a manifest-provider subscription); Refresh moves from Security-log tree reconstruction to a live snapshot with exact create times; UserSID comes from the validated sid-extraction-test POC at <local-path> (technique proven, drops in as-is); command line uses ProcessTraceData.CommandLine with live PEB fallback; boot-time coverage via Global Logger boot ETL ingestion is in scope (opt-in setting for slice 1); verification via a Windows adaptation of the sensor-neutral validation harness. Hard constraint: no WintapMessage/ProcessObject schema or PidHash changes; TraceEvent stays at 3.1.23.
Motivation (all four confirmed): stops commented out on the Security-log path, fragile since-boot reconstruction (log-wrap "reboot required" — observed live on the Windows validation host 2026-08-13), event-log-time PidHash corruption, and audit-policy dependency.
Next stage: implementation_plan.md + dev_handoff.md, then implementation and verification.

## [2026-08-13] feature-work | improve-windows-process-collection: implementation plan and dev handoff added

Pages created: `work/improve-windows-process-collection/implementation_plan.md` (three slices mapped to wintap P2.1–P2.8 instruction units — slice 1 P2.1–P2.6: SID helper, sensor core, snapshot refresh, enrichment, stop-metrics merge, wire-in/removal; slice 2 P2.7: opt-in Global Logger boot ETL; slice 3 P2.8: Windows validation harness — each unit sized for one approved instruction document with xUnit tests tagged `[Trait("Category", "P2.x")]` and a done checklist); `work/improve-windows-process-collection/dev_handoff.md` (bridges the Analytics feature artifacts to the wintap Architect/Engineer/Developer loop per `../wintap/CLAUDE.md`: per-unit Engineer dispatch prompt with a P2.1 copy/paste example, primary sources per unit, P2.1-first recommendation, testing gates, and closeout/audit duties).
Pages updated: index.md (two new Work rows); log.md.
Contradictions flagged: none.
Next stage: dispatch the wintap Engineer for the P2.1 instruction document using the handoff prompt, then run the approve/implement/audit loop per unit.

## [2026-08-14] diagnostic | RHEL 8 field test: clone sensor attach, fork-without-exec signature, suspected fork storm

Source: operator-reported Lintap logs from the first real-machine RHEL 8 test (2026-08-14), plus source inspection of CloneSensor.cs, BaseEbpfSensor.cs, clone_tracer.bpf.c, and ../Lintap/packaging/lintap-rpm/lintap.env.
Pages created: diagnostic/rhel8-clone-sensor-and-fork-without-exec.md — three findings: (1) the EventChannel warn signature parentPid = childPid−1 identifies fork-without-exec processes invisible to exec-only sensing, matching the VM-validated clone-sensor coverage requirement; (2) the clone sensor's sched_process_fork attach succeeds on RHEL 8, so the Fedora failure behind the opt-out packaging default does not generalize (candidate: revisit the lintap.env default); (3) warnings persisted ~7 min after clone enable — PID-range rate analysis (~450-700 PIDs/sec per stream, observed wrap at pid_max 4,194,304) suggests a fork storm with multi-minute event-processing lag on a nominally idle machine, with pre-enable backlog and PID namespaces as competing explanations; decisive checks recorded (fork-rate from /proc/stat, top forking parents from raw_process parquet).
Pages updated: work/lintap-process-creation-validation/index.md (field-finding pointer); index.md.
Contradictions flagged: none hard. The packaging comment "sched_process_fork attach failed on Fedora" stands but is now known to be Fedora-specific, not general.
Notes: retention feature ruled unlikely as a contributor by the warn signature; process_retention_telemetry query recorded as the standard rule-out for future triage.

## [2026-08-14] diagnostic | Fork storm root cause: pidstat-collector per-line command substitutions

Source: operator-run top-forkers query on the RHEL 8 machine (bash and date, both root, top 2 in raw_process), matched against ../Lintap/pidstat-collector.sh source structure.
Root cause: the collector's hot loop executes ~7 command-substitution subshells per pidstat output line, two exec'ing date (~700 forks/sec at -p ALL on ~500 processes). This matches the measured PID-advance rate, the top-forker names, and the parentPid = childPid−1 warn signature (each $(...) subshell is a fork-without-exec bash that forks date). The observability collector was flooding the sensor it feeds; raw_process data from affected runs is polluted (bash/date dominate) and unfit for process-mix conclusions.
Pages updated: diagnostic/rhel8-clone-sensor-and-fork-without-exec.md (Root Cause section replacing the fork-storm/namespace open question; remaining open items: confirm fork-rate collapse after stopping the collector, and whether the observed multi-minute event lag at ~700 events/sec merits a sensor-capacity investigation); work/improve-pidstat-collector/implementation_plan.md (new CRITICAL slice-2 step 6b: fork-free hot loop — global-variable normalize, printf '%(%s)T' epoch, window-epoch date column merging the midnight fix, plain path variables, plus a no-child-processes regression guard).
Contradictions flagged: none. Reviewer note: the 2026-08-12 slice-1 review flagged conversion cost but missed the per-line fork cost — recorded here so the review checklist for shell collectors includes hot-loop fork auditing.
Notes: clone-sensor-on-RHEL-8 finding (attach works) is unaffected and stands on its own.

## [2026-08-14] decision | pidstat collector slice 2 redefined: Python rewrite

Source: human decision following the fork-storm diagnosis (diagnostic/rhel8-clone-sensor-and-fork-without-exec.md) — bash+duckdb-CLI stays conceptually but the implementation moves to a single-process Python collector using the duckdb Python API, for fork elimination and readability.
Pages updated: work/improve-pidstat-collector/design.md (new decision section: rationale, carried-over slice-1 semantics restated as requirements, bash pidstat-collector.sh retired while pidstat-collect.sh remains the example; DuckDB-CLI-vs-Python open question resolved; new open question: Python runtime/packaging given RHEL 8's default python3.6 vs duckdb wheel requirements); implementation_plan.md (step 6 rewritten as the Python rewrite absorbing all three review findings, step 6b as the pytest port incl. midnight case and fork regression guard; checklist, files-to-change, and tests sections aligned); dev_handoff.md (slice-2 prompt rewritten: hard single-process requirement, delete-the-bash-collector instruction gated on tests passing, runtime/packaging decision assigned to the dev); index.md.
Contradictions flagged: none. The slice-1 acceptance stands — its behavior and test suite become the specification the Python port must satisfy.

## [2026-08-14] investigation | pidstat collector telemetry source options + container attribution

Source: human questions (is pidstat still the right source for the Python collector? can we get container info?), answered with live verification on validation-host: /proc/<pid>/stat (52 fields incl. minflt/majflt, delayacct_blkio_ticks, guest_time), /proc/<pid>/io, /proc/<pid>/status ctx switches, /proc/<pid>/schedstat, /proc/<pid>/cgroup (v2 unified here; v1/hybrid on RHEL 8), /proc/<pid>/ns/pid readlink; psutil API inspection (no page faults, no guest time, no iodelay on Linux).
Findings: three source options recorded in design.md — A keep-pidstat-child (full schema, one child, text parsing), B stdlib /proc sampler (full schema, zero children, zero new deps, owns rate math), C psutil (schema-incomplete, not recommended). Container attribution (cgroup_path, pid_ns_inode, best-effort runtime/id) is only available via /proc — effectively deciding for option B; new columns coordinate with the same-slice Wintappy bronze migration so the schema changes once. Recommendation: implement B behind a sampler interface with pidstat retained as side-by-side test oracle.
Pages updated: work/improve-pidstat-collector/design.md (Telemetry Source Investigation + Container Attribution sections); brief.md (container-attribution goal added); references.md (proc(5), psutil evaluation); implementation_plan.md (step 6 source-selection + container columns; checklist items); dev_handoff.md (source-selection and container requirements in the copy/paste prompt); index.md. last_validated bumped to 2026-08-14 across the feature artifacts.
Contradictions flagged: none. Note: container/namespace-tagged rows would also let the RHEL 8 diagnostic's interleaved-PID-range question be answered from collector data directly.

## [2026-08-15] feature-work | fix-upload-cache-deletion started; pidstat mechanism fact corrected

Source: overnight RHEL 8 field test (S3 uploader re-sending the same data every cycle) plus code review of ../wintap/wintap/core/etl/load/ (CacheManager.cs, adapters/S3Adapter.cs, SMBFileShareAdapter.cs, SignedS3UrlAdapter.cs, interfaces/IUpload.cs).
Root cause: the delete-after-upload path is dead code — CacheManager subscribes Uploader_UploadCompleted (which deletes), but no adapter ever raises the event (declared-only in S3/SMB adapters; the sole Invoke is commented out in SignedS3UrlAdapter). CacheManager.upload() sets successfulUpload ("any success = all success, for now") and never reads it — the intended delete site. Only pruneCache()'s 256MB cap removes files, and its free-space check uses Windows drive-letter logic, suspect on Linux.
Pages created: work/fix-upload-cache-deletion/brief.md (evidence with GROUND_TRUTH pointers, goals incl. Linux prune fix and empty dayPK/hourPK dir removal from the Long_Running_Cleanup issue, acceptance criteria incl. overnight single-upload validation); work/fix-upload-cache-deletion/dev_handoff.md (../wintap core/etl/load authorization, recommended inline-delete fix shape with the mid-loop event-raise anti-pattern called out, dead-event decision delegated).
Pages corrected: work/improve-pidstat-collector/design.md — the 2026-08-11 mechanism fact "Uploader_UploadCompleted deletes each parquet after successful upload" was true of the handler code but false in effect (event never fires); struck through with dated correction. brief.md bounded-disk goal corrected (accumulation guard is the effective bound); dev_handoff.md known-issue note added; implementation_plan.md S3 end-to-end checklist item marked blocked on the new feature.
Pages updated: index.md (two new Work rows).
Contradictions flagged: one, resolved by correction — recorded mechanism fact contradicted observed field behavior; lesson noted: handler-exists-and-subscribed is not evidence the event fires; verify the raise site when grounding event-driven claims.

## [2026-08-15] review | Upload subsystem robustness pass folded into fix-upload-cache-deletion

Source: follow-up code review of ../wintap/wintap/core/etl/load/ (CacheManager doMerge/HangDetector/pruneCache/getFreeBytes/getCurrentCacheDirSize, S3Adapter client lifecycle and retry, upload loop).
Additional findings (prioritized into the feature): (1) HangDetector_Elapsed deletes ALL parquet under the parquet root on a hung merge — un-uploaded raw_sensor and future pidstat data included; restrict to unmerged working dirs. (2) pruneCache off-by-one (breaks before deleting the threshold-crossing file), cap measured against whole-cache size while deleting only raw_sensor parquet (unreachable-target risk), hardcoded 256MB cap, unused drive-letter getFreeBytes dead code. (3) Unguarded PostUpload loop can silently kill the upload thread; empty catch in delete handler; upload failures logged at Info. (4) Zero-byte parquet files skipped by upload become permanent stragglers post-fix. (5) Double directory enumeration per cycle. Verified-sound and explicitly out of scope: S3 client per-cycle lifecycle, 429 backoff+jitter, credentials, key mirroring, .Result pattern.
Pages updated: work/fix-upload-cache-deletion/brief.md (goals expanded with GROUND_TRUTH pointers; acceptance criteria for merge-hang scoping, prune accounting, PostUpload resilience; deployment note re one-time backlog drain on machines that ran the broken version); dev_handoff.md (cleanup items in priority order with a do-not-change list); index.md.
Contradictions flagged: none.

## [2026-08-15] update | fix-upload-cache-deletion: Windows considerations made explicit

Source: human question (does the design account for Windows?) plus source confirmation that PluginManager (shared core) constructs WintapETL/CacheManager on both platforms — Windows Wintap runs the identical upload path and has the identical re-upload bug.
Assessment: the fix is platform-neutral by construction (shared code; case-insensitive globs and path→S3-key separator normalization already handled), with three Windows specifics now stated explicitly: transient file-lock tolerance on delete (AV/indexer — log, retain, retry next cycle, never kill the upload thread); Directory.Delete failure tolerance for empty-dir removal (which also makes the new-file race safe on both platforms); and a Windows service-mode verification run (same setup as the 2026-08-13 retention check) confirming delete-after-upload across ≥3 cycles.
Pages updated: work/fix-upload-cache-deletion/brief.md (Windows acceptance criteria); dev_handoff.md (Windows correctness requirement + verification addition).
Contradictions flagged: none.

## [2026-08-15] code | Improve pidstat collector slice 2

Files changed: `../Lintap/pidstat-collector.py` (new), `../Lintap/pidstat-collector.sh` (deleted), `../Lintap/tests/test_pidstat_collector.py` (pytest port), `../Lintap/pyproject.toml`, `../Lintap/.python-version`, `../Lintap/README.md`, `../Lintap/packaging/lintap-{rpm,deb}/*pidstat*`, `../Wintappy/wintap_dbt/macros/pidstat.sql`, `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql`, `../Wintappy/Makefile`, `../Wintappy/wintap_dbt/README.md`, plus this feature's work artifacts.
Results: rewrote the collector in Python around a zero-child `/proc` sampler and DuckDB Python conversion; preserved the slice-1 env/spool/partition/salvage/accumulation semantics; added hostname + container attribution columns; ported the test suite to pytest with pidstat-oracle, midnight, and fork-regression coverage; added pinned-interpreter systemd units; migrated Wintappy pidstat bronze from CSV to parquet and validated both fixture and empty-input paths in `validation-host` using `uv`.
Limitations: the pinned `<local-path>` unit path could not be started on the Ubuntu 24.04 validation VM because that interpreter is not installed there; live container fixture coverage and S3/delete-after-upload closeout remain open.

## [2026-08-15] update | Improve pidstat collector runtime packaging switched to uv-managed venv launcher

Source: follow-up implementation request after the hardcoded `<local-path>` path proved too brittle for mixed-host deployment.
Files changed: `../Lintap/pidstat-collector-bootstrap.sh` (new), `../Lintap/pidstat-collector-launch.sh` (new), `../Lintap/packaging/lintap-{rpm,deb}/lintap-pidstat.service`, both `lintap.env` files, packaging READMEs/build scripts, top-level `../Lintap/README.md`, and this feature's work artifacts.
Results: removed the host-interpreter pin; service now launches the collector through `/bin/bash <local-path>`, which resolves `PIDSTAT_VENV_DIR` and execs the collector from a dedicated `uv`-managed venv. Added `pidstat-collector-bootstrap.sh` to create that venv and install DuckDB, defaulting to `PIDSTAT_BOOTSTRAP_PYTHON=3.12` so the runtime stays within the collector's supported `>=3.11,<3.13` range. Validated in `validation-host`: bootstrap created a 3.12.3 venv, launcher produced parquet successfully, and a temp unit with the new `ExecStart` shape passed `systemd-analyze verify`.
Limitations: still not a full package-install/reboot test; the real packaged service must be exercised on a target host later.

## [2026-08-16] review | improve-pidstat-collector slice 2 accepted

Source: independent review of ../Lintap 8eaae5c and ../Wintappy ccbf783 (both on feature-branch) plus this repo's slice-2 wiki commits. Re-verified: pytest 12/12 in ../Lintap (uv, python 3.12).
Review verdict: slice 2 accepted; feature is code-complete. The dev implemented telemetry option B (zero-child /proc sampler) with container attribution, verified stat-field offsets correct against proc(5), pidstat-matching rate semantics (guest-excluded %usr, schedstat-based %wait, delta-tick iodelay), PID-reuse handling via starttime, in-process duckdb conversion with atomic replace and full traceback logging, and all three carried review findings absorbed. Wintappy bronze matches spec (read_parquet + filename provenance + container columns + empty-input typed table). Packaging pivoted mid-slice from a pinned <local-path> to a uv-managed 3.12 venv bootstrap/launcher after field brittleness — decision properly recorded. Boundary check clean (no pidstat changes in ../wintap).
Findings (minor): (1) enforce_accumulation_guard stats files without FileNotFoundError tolerance and runs inside the conversion try — a real race once the upload fix has the sensor deleting concurrently, with a misleading error attribution; queued as a checklist follow-up. (2) Open items honestly tracked: live container fixture, target-host systemd install/reboot, S3 end-to-end (blocked on fix-upload-cache-deletion).
Pages updated: work/improve-pidstat-collector/verification.md (slice-2 Independent Review section); implementation_plan.md (container/systemd checklist reconciliation, acceptance line, guard-race follow-up); design.md (Summary rewritten to match the shipped Python/proc-sampler reality and the pending-deletion caveat); index.md.
Contradictions flagged: none.

## [2026-08-16] query | Small parquet files are merged before upload — no new task

Source: human question (are the frequent small parquet files merged before upload?), answered from ../wintap/wintap/core/etl/load/Merge.cs, CacheManager.cs (doMerge before upload each cycle), RawSensorWriter.cs, and ETLConfig.json.
Answer: yes on both paths. Serializer flush files (SerializationIntervalSec, shipped default 60s — the wiki's "10-second" figures refer to event aggregation windows, not file cadence) are consolidated by doMerge into one file per event type per upload cycle before the sweep; the pidstat collector writes one file per rotation window by construction, matching that granularity. Upload unit is ~12 files/type/hour. No next-slice task added. Optional future consolidation to hourly files (~12× fewer S3 objects, up to 1h local latency) noted in conversation but deliberately not queued.
Pages updated: work/improve-pidstat-collector/design.md (merge-before-upload added to verified mechanism facts).
Contradictions flagged: none.

## [2026-08-16] code | fix-upload-cache-deletion first implementation pass

Source: code-development pass on branch `feature-branch` in `../wintap`, driven by the feature handoff and brief.
Files changed: `../wintap/wintap/core/etl/load/CacheManager.cs`, `interfaces/IUpload.cs`, `adapters/S3Adapter.cs`, `adapters/SMBFileShareAdapter.cs`, `../wintap/wintap/core/etl/model/ETLConfig.cs`, `../wintap/wintap/core/etl/ETLConfig.json`, `../wintap/wintap/core/etl/shared/Utilities.cs`, plus this feature's `brief.md`, new `verification.md`, and `index.md`.
Results: delete-after-upload moved inline to `CacheManager.upload()` after the full uploader loop, preserving the existing any-success policy; dead `UploadCompleted` event plumbing removed from the active load path; zero-byte files now delete instead of spinning forever; empty partition dirs are pruned after delete; `pruneCache()` now measures `raw_sensor` size, deletes the threshold-crossing file, uses a configurable cap, and protects current-window files; merge-hang cleanup now skips `raw_sensor/`, `csv/`, and `merged/`; `PostUpload()` calls are guarded per uploader. Verified in `validation-host`: `dotnet build Lintap.csproj -warnaserror:CS0067` passed. `Wintap.csproj -p:EnableWindowsTargeting=true` remains blocked in this VM by unrelated Windows-target dependency issues.
Limitations: no live uploader target was exercised yet, so single-upload-plus-delete across >=3 cycles still needs target-host verification.

## [2026-08-17] update | improve-windows-process-collection: unit IDs renamed P2.x → wpc-nn

Source: Architect decision in the wintap main session — the P-major numbering was judged unintuitive. New scheme combines the descriptive-slug pattern used by this wiki's Linux feature threads (kebab-case feature names, numbered steps, slices) with the semantic-prefix precedent already in ../wintap's architecture assessment (DEC-/OQ-/INV-).
Scheme: `<feature-abbrev>-<nn>` unit IDs with a descriptive slug in filenames; this feature's abbreviation is `wpc` (windows-process-collection), units wpc-01…wpc-08. xUnit traits become `[Trait("Category", "wpc-<nn>")]`; one unit runs via `dotnet test --filter "Category=wpc-01"`, the whole feature via `Category~wpc`. Instruction docs `developer_docs/instructions/wpc-<nn>-<slug>.md`; audits `developer_docs/audits/wpc-<nn>-<slug>.md`. The wintap bootstrap unit P1.1 (merged, tested, audited) is grandfathered under the old naming.
Pages updated: work/improve-windows-process-collection/implementation_plan.md and dev_handoff.md (all P2.1–P2.8 references renamed, feature abbreviation declared, whole-feature filter documented); index.md (row summaries and Last updated line).
Contradictions flagged: none. ../wintap CLAUDE.md gains the unit-naming convention alongside its existing P1.1 examples.
Next stage: dispatch the wintap Engineer for the wpc-01 instruction document using the handoff prompt, then run the approve/implement/audit loop per unit.

## [2026-08-17] instruction | [wintap] wpc-01 SID helper instruction drafted

Decisions made: Architect approved the wpc-01 instruction for Developer handoff. Drafted the first implementation unit for the improve-windows-process-collection feature from the already-settled Analytics feature design. Kept the unit narrow: port the validated classic kernel ETW `ProcessTraceData` UserSID parser and add synthetic payload tests only; no sensor wiring, account-name lookup, token fallback, command-line fallback, or PidHash/process schema changes.
ADRs written or updated: none.
Wiki pages updated: none beyond this log.
Instructions written: `../wintap/developer_docs/instructions/wpc-01-sid-helper.md` (Status: Approved — Architect approval 2026-08-17).
Scratch notes: `wiki/work/improve-windows-process-collection/sid-helper-notes-2026-08-17.md` (migrated from `retired developer wiki`).
Open questions: none for wpc-01. The Developer can implement wpc-01 and verify with `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-01"`.

## [2026-08-17] audit | [wintap] wpc-01 SID helper completed

Decisions made: none. Developer completed the approved wpc-01 unit as specified: added the classic kernel ETW `ProcessTraceData` UserSID extraction helper, added the internal payload-parser test seam, and added synthetic xUnit coverage for extracted SIDs, null-SID markers, and malformed payload guards. No sensor wiring, schema changes, PidHash/process hash changes, TraceEvent upgrade, or new NuGet dependencies were introduced.
ADRs written or updated: none.
Wiki pages updated: none beyond this log; no new architecture decision was made by the implementation.
Instructions written: none.
Audit artifact: `../wintap/developer_docs/audits/wpc-01-sid-helper.md` (Status: Complete).
Verification: `dotnet build -c Release` passed from `../wintap/tests/Wintap.Tests`; `dotnet test --filter "Category=wpc-01"` passed with 9/9 tests selected and passing.
Open questions: none for wpc-01. Next Windows process-collection unit can wire the helper into the chosen process sensor path.

## [2026-08-17] maintenance | Consolidate Wintap developer wiki into Analytics wiki

Decisions made: recorded the Architect-settled decision that `../Wintap-Analytics/wiki/` is the single Wintap ecosystem knowledge base, that `retired developer wiki` is retired, that Wintap instructions/audits intentionally remain in `../wintap/developer_docs/`, and that the Wintap Engineer is authorized to write to `../Wintap-Analytics/wiki/`.
ADRs written or updated: `wiki/decision/consolidate-developer-wiki-into-analytics-wiki.md`; migrated `wiki/decision/process-identity-attribution-contract.md`; migrated `wiki/decision/test-project-structure-and-first-test.md`.
Wiki pages updated: `wiki/work/improve-windows-process-collection/sid-helper-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`; `../Wintap-Analytics/AGENTS.md`; Wintap repo plumbing docs `../wintap/CLAUDE.md`, `../wintap/.claude/agents/engineer.md`, and `../wintap/.claude/agents/developer.md`; tombstoned `retired developer wiki`.
Instructions written: none.
Open questions: none. Historical `../wintap/developer_docs/instructions/` and `../wintap/developer_docs/audits/` files were intentionally not rewritten; stale `operator-wiki` references there are covered by the tombstone.

## [2026-08-17] instruction | [wintap] wpc-02 sensor core instruction drafted

Decisions made: none. Drafted the wpc-02 instruction from the already-settled improve-windows-process-collection design: add a new `WindowsProcessSensor` core that subscribes classic kernel ProcessStart/ProcessStop on the shared NT Kernel Logger parser, canonicalizes create time with `GetProcessTimes` first and ETW timestamp fallback, keeps an in-memory PID instance map, emits Start/Stop process events, and tests canonicalization fallback, PID-reuse replacement, and Stop-without-Start fallback paths through minimal internal seams.
ADRs written or updated: none. Flagged a decision tension in the draft: the older process identity ADR says core owns PidHash/ParentPidHash generation, while the current WPC feature design and existing sensor practice require sensor-side PidHash population using the unchanged formula.
Wiki pages updated: `wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`.
Instructions written: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` (Status: Draft; Architect approval pending).
Open questions: Architect should explicitly approve or revise the flagged PidHash ownership tension before Developer handoff if the wording is not acceptable. The proposed verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-02"`.

## [2026-08-17] decision | [wintap] wpc-02 live Start time canonicalized to ETW timestamp

Decisions made: Architect selected option 1 for wpc-02 create-time canonicalization: use the classic kernel ETW ProcessStart timestamp as the canonical live Start time for `PidHash` generation. Do not perform `OpenProcess` / `GetProcessTimes` on every process create. Rationale: Wintap has used ETW as process-start ground truth for over 13 years, it has proven reliable, and per-create handle lookups add hot-path performance risk. Snapshot Refresh still uses live process create times and must deduplicate/repair against live Starts by PID + create-time tolerance in the later snapshot unit.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/brief.md`; `references.md`; `design.md`; `implementation_plan.md`; `sensor-core-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` revised to remove per-Start `GetProcessTimes`, remove the process-accessor test seam, and require ETW timestamp canonicalization tests.
Open questions: wpc-02 instruction remains Draft / Architect approval pending as a whole.

## [2026-08-17] decision | [wintap] wpc-02 uses ProcessResolver as sole hot-path identity store

Decisions made: Architect selected `ProcessResolver` for the wpc-02 hot path instead of a sensor-owned in-memory PID map. Starts emit through `EventChannel.Send` so `ProcessResolver` registers the process instance. Stops resolve identity through `EventChannel.GetProcessHistory(pid, stopTimeUtc)` / `ProcessResolver` before emission; resolver misses are counted and fall back to hash-from-stop-time. Rationale: avoid introducing a parallel lifecycle cache when the project already has a PID-reuse-safe resolver designed for process identity.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/references.md`; `design.md`; `implementation_plan.md`; `dev_handoff.md`; `sensor-core-notes-2026-08-17.md`; `wiki/index.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` revised to remove the in-memory PID instance map requirement and replace PID-reuse map tests with resolver-selected-instance tests.
Open questions: wpc-02 instruction remains Draft / Architect approval pending as a whole.

## [2026-08-17] approval | [wintap] wpc-02 sensor core instruction approved

Decisions made: Architect approved the revised wpc-02 instruction for Developer handoff. Final approved scope: new `WindowsProcessSensor` subscribing classic kernel ProcessStart/ProcessStop on the shared kernel parser; ETW ProcessStart timestamp is canonical for live Start `PidHash`; no per-Start `GetProcessTimes`; `ProcessResolver` is the sole hot-path identity store; Stop resolver misses are counted and fall back to hash-from-stop-time. No schema, PidHash formula, TraceEvent version, or NuGet dependency changes.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/wpc-02-sensor-core.md` (Status: Approved — Architect approval 2026-08-17).
Open questions: none for wpc-02 instruction handoff. Developer verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-02"`.

## [2026-08-17] audit | [wintap] wpc-02 sensor core completed

Decisions made: none. Developer completed the approved wpc-02 unit: added `WindowsProcessSensor` core under `../wintap/wintap/platform/windows/sensor/etw/`, added shared-kernel ProcessStart/ProcessStop subscription, ETW-timestamp Start canonicalization, resolver-backed Stop identity stamping, Stop resolver miss counting, and hash-from-stop-time fallback. Runtime wire-in and old sensor deletion remain deferred to wpc-06 as planned.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/implementation_plan.md`; `wiki/work/improve-windows-process-collection/sensor-core-notes-2026-08-17.md`; `wiki/log.md`.
Instructions written: none.
Audit artifact: `../wintap/developer_docs/audits/wpc-02-sensor-core.md` (Status: Complete).
Verification: `dotnet build "wintap\Wintap.csproj" -c Release -p:WarningLevel=0` passed; from `../wintap/tests/Wintap.Tests`, `dotnet test --filter "Category=wpc-02" --logger "console;verbosity=detailed"` selected and passed 5/5 tests. The audit records a verification-command deviation: repo-root `dotnet build -c Release` / root filtered test target `Wintap.sln`, which currently fails under .NET SDK MSBuild on the existing `Wintap-Workbench` website project (`MSB4249`), so project-scoped equivalents were used. The audit also records a narrow internal `genPidHash` test seam to avoid elevation-sensitive `StateManager` initialization; production still defaults to unchanged `ProcessHash.GenPidHash`.
Open questions: none for wpc-02. Next unit is wpc-03 snapshot refresh.


## [2026-08-17] instruction | [wintap] wpc-04 field enrichment instruction approved

Decisions made: none. Architect requested and approved the wpc-04 instruction for Developer handoff. Scope is field enrichment on the already-landed `WindowsProcessSensor`: SID/user via wpc-01 helper, `LookupAccountSid` with bounded SID cache, token fallback for NoSid/Malformed, ETW command line with PEB fallback, and executable path via `QueryFullProcessImageName` with device-path translation fallback. The instruction preserves settled WPC constraints: no schema changes, no PidHash formula changes, TraceEvent stays 3.1.23, no new NuGet dependencies, resolver-backed sensor, runtime wire-in deferred to wpc-06, Stop metrics deferred to wpc-05, boot ETL deferred to wpc-07.
ADRs written or updated: none.
Wiki pages updated: `wiki/log.md` only.
Instructions written: `../wintap/developer_docs/instructions/wpc-04-field-enrichment.md` (Status: Approved — Architect approval 2026-08-17).
Open questions: none for wpc-04 instruction handoff. Developer verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-04"`, with the documented project-scoped fallback if the known `Wintap-Workbench` `MSB4249` solution-level issue appears.

## [2026-08-17] instructions | wpc-05 stop metrics merge draft

Source: Wintap Engineer instruction-draft session for `improve-windows-process-collection` unit wpc-05, with context from `wiki/work/improve-windows-process-collection/{brief,design,implementation_plan,dev_handoff}.md`, prior audits `../wintap/developer_docs/audits/wpc-02-sensor-core.md`, `wpc-03-snapshot-refresh.md`, `wpc-04-field-enrichment.md`, and source inspection of `../wintap/wintap/platform/windows/sensor/etw/{WindowsProcessSensor,ProcessSensor,KernelProcessSensor}.cs` plus resolver/test references.
Instruction written: `../wintap/developer_docs/instructions/wpc-05-stop-metrics-merge.md` as Draft/Pending approval. It scopes manifest `Microsoft-Windows-Kernel-Process` keyword `0x10` ProcessStop metrics correlation into resolver-backed kernel Stop emission, carries forward the old `parseUserModeProcessStop` metric list, requires wpc-05 tests, and preserves no-schema/no-PidHash/no-TraceEvent-upgrade/no-new-dependency constraints.
Pages updated: `wiki/log.md` only.
Notes: Implementation-plan checklist intentionally not updated; that remains closeout work after Developer implementation/audit.

## [2026-08-17] approval | [wintap] wpc-05 stop metrics merge instruction approved

Decisions made: Architect approved the wpc-05 instruction for Developer handoff. Scope is manifest `Microsoft-Windows-Kernel-Process` keyword `0x10` ProcessStop metric subscription and nearest-in-time PID correlation into resolver-backed kernel Stop emission, with a named 5-second window, non-blocking expiry/default emission, and `manifest_metric_misses` counting. The instruction preserves settled WPC constraints: no schema changes, no PidHash formula changes, TraceEvent stays 3.1.23, no new NuGet dependencies, no sensor-owned PID instance map, and runtime wire-in/removal deferred to wpc-06.
ADRs written or updated: none.
Wiki pages updated: `wiki/log.md` only.
Instructions updated: `../wintap/developer_docs/instructions/wpc-05-stop-metrics-merge.md` (Status: Approved — Architect approval 2026-08-17).
Open questions: none for wpc-05 instruction handoff. Developer verification gate is `dotnet build -c Release` plus `dotnet test --filter "Category=wpc-05"`, with the documented project-scoped fallback if the known `Wintap-Workbench` `MSB4249` solution-level issue appears.

## [2026-08-17] process | AI velocity/ROI mini-lab codified

Decisions made: Architect-approved ROI/velocity mini-lab protocol recorded for the LLM-assisted feature workflow. The protocol uses sealed human and AI estimates at feature open, AI design/development and per-unit estimate splits, main-session 15-minute-gap attention-proxy actuals, a three-question hard cap with displacement ratchet, never-gates behavior, close-out reveal/tabulation, and one planned template revision after the next real feature trial.
ADRs written or updated: `wiki/decision/ai-velocity-roi-mini-lab.md` (Accepted).
Wiki pages updated: `wiki/concept/llm-assisted-feature-workflow.md`; `wiki/concept/feature-work-template.md`; `wiki/concept/metrics-template.md`; `wiki/index.md`; `wiki/log.md`.
Wintap process docs updated for Architect review: `../wintap/.claude/agents/engineer.md`; `../wintap/CLAUDE.md`.
Contradictions flagged: none. Notes: the Wintap-side process-doc edits are outside the standard directory-ownership table and are drafted for explicit Architect review, per the ADR ownership note.
Open questions: none for codification; the next real feature is the live trial, after which templates get one planned revision pass.

## [2026-08-17] metrics | [wintap] WPC velocity/ROI retrofit

Decisions made: none. Retrofitted the current `improve-windows-process-collection` feature with mini-lab metrics after the protocol was adopted. The human estimate and reported Design-AI estimate both put solo, no-AI implementation at 3 weeks; recorded as 120 hours assuming 40-hour weeks. Because this was retrofitted after feature open and after the estimate was disclosed, the sealed/independent estimate discipline is explicitly marked broken for this feature.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/interview.md`; `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/index.md`; `wiki/log.md`.
Instructions written: none.
Open questions: human predicted AI-attention estimate was not captured; main-session attention proxy, API cost, close-out question, and per-unit actual hours remain for close-out. Per-unit estimates for wpc-01 through wpc-06 are missing because they were already implemented before the retrofit; wpc-07 has a pre-implementation estimate, and wpc-08 should receive one when its instruction is drafted.

## [2026-08-17] audit | [wintap] wpc-05 and wpc-06 completed — slice 1 of improve-windows-process-collection done

Decisions made: none new. Developer completed the approved wpc-05 (stop-metrics merge) and wpc-06 (wire-in and legacy removal) units; both landed in wintap develop-operator commit 0f273e0 (2026-08-17). Slice 1 (wpc-01 through wpc-06) is complete: the unified `WindowsProcessSensor` is live as the sole Windows process lifecycle sensor — resolver-backed classic kernel ETW Start/Stop, snapshot Refresh with ClearProcessDB-then-Refresh preserved, SID/command-line/path enrichment, manifest-provider Stop metric merge, and QA counter interval/shutdown logging. Legacy `ProcessSensor.cs` (Security-log 4688/4689) and `KernelProcessSensor.cs` were deleted with their settings entries and dead references; no Security-log audit-policy dependency remains for process telemetry.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/implementation_plan.md` (Done Checklist: wpc-05 checked — 4/4 tests, audit filed; wpc-06 amended — elevated manual smoke executed by the Architect 2026-08-17, PASS with audit-policy evidence waived; both units in commit 0f273e0); `wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17.md` (new — out-of-scope smoke observations as follow-up candidates: SensSensor null-value load failure, missing SignedS3UrlAdapter, parent-process resolution warnings, DuckDB unterminated-quote parser errors, cosmetic `[WindowsProcessSensor..ctor]` logger tag on QA lines); `wiki/log.md`.
Audit artifacts: `../wintap/developer_docs/audits/wpc-05-stop-metrics-merge.md` (Complete; 4/4 wpc-05 tests passed); `../wintap/developer_docs/audits/wpc-06-wire-in-removal.md` (Complete; 35/35 wpc tests and 36/36 full test-project regression passed via the documented MSB4249 project-scoped fallback; smoke evidence includes wire-in ordering, Start/Stop/Refresh parquet flow, and parseable interval/shutdown QA counter lines, e.g. snapshot_count=489).
Instructions written: `../wintap/developer_docs/instructions/wpc-07-boot-etl-coverage.md` (Status: Draft — Architect approval pending; slice 2 opt-in Global Logger boot ETL coverage).
Open questions: Architect review of the wpc-07 draft, including the optional logger-tag rider and the `boot_replay_count` QA-counter addition. wpc-08 (validation harness, slice 3) remains after wpc-07.

## [2026-08-17] closeout | improve-pidstat-collector + fix-upload-cache-deletion closed; durable facts promoted

Source: final review of branch feature-branch across all four repos (wintap ecfa746 upload fix; Lintap 8eaae5c Python collector; Wintappy ccbf783 parquet bronze; this repo's verification commits), plus operator field notes from RHEL 8 testing.
Upload-fix review: accepted for merge. Independently re-verified Lintap.csproj build (0 errors, zero CS0067). All specified behaviors landed: gated inline delete after the full uploader loop, dead event removed from IUpload/adapters, zero-byte cleanup, bottom-up empty-partition-dir removal with tolerated failures, merge-hang recovery scoped away from raw_sensor, prune off-by-one fixed with configurable RawSensorMaxCacheSizeBytes measured against raw_sensor only, guarded PostUpload, Warn-level failure logs. Post-merge follow-ups (dev-recorded): 3+ cycle live-uploader run; Windows-targeting build (env-blocked) and service-mode run.
Features closed: both briefs marked reviewed/closed with follow-ups tracked. Durable facts promoted to canonical pages: NEW component/sensor-upload-cache-pipeline.md (layout, merge cycle, type-agnostic ride-along contract, delete-after-upload fix, prune/hang-recovery semantics, deployment prerequisites); repo/lintap-supporting-repo.md (pidstat-collector.py section); repo/wintappy-pipeline-repo.md (parquet-only pidstat bronze section).
Operator field notes recorded: (1) pidstat-collector.py possible high CPU — investigate with multi-system data (pidstat plan follow-ups); (2) Lintap CPU possibly still trending up over long runs — watch; leading hypothesis duckdb event_store size, may need compaction (fix-unbounded plan field-watch item; raises priority of its open DuckDB-reclaim question); (3) pidstat parquet files are NOT merged before upload — 2026-08-16 mechanism fact corrected; generic per-cycle small-file consolidation for all raw_sensor type dirs queued as fix-upload-cache-deletion next slice; (4) attribution below.
Attribution note (per human request): this branch and its features were implemented using Claude (Fable) for design/review/wiki-maintenance and opencode (gpt-5.4) for development.
Contradictions flagged: one, resolved by correction — the 2026-08-16 "no merge step needed for pidstat" mechanism fact contradicted field observation; corrected in the pidstat design page with the consolidation task queued.

## [2026-08-18] closeout | [wintap] wpc-07 boot ETL coverage completed

Decisions made: none new. wpc-07 is closed as complete: the opt-in Global Logger boot ETL coverage path was implemented in `../wintap`, with `EnableBootProcessTrace` defaulting off, startup detect/verify/stop/disarm ordered before `WindowsProcessSensor` and shared kernel session materialization, replay after snapshot + live subscription registration, resolver-backed replay dedup, and `boot_replay_count` QA counter output.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/implementation_plan.md` (wpc-07 checked complete with validation note); `wiki/log.md`.
Audit artifact updated: `../wintap/developer_docs/audits/wpc-07-boot-etl-coverage.md` (post-implementation local validation section added).
Verification: Developer-side verification passed before deployment: `dotnet build "wintap\Wintap.csproj" -c Release -p:WarningLevel=0`; `dotnet build "tests\Wintap.Tests\Wintap.Tests.csproj"`; `dotnet test "tests\Wintap.Tests\Wintap.Tests.csproj" --filter "Category=wpc-07"` (10/10); `--filter "Category~wpc"` (45/45); unfiltered test project (46/46). Architect then published/deployed locally, rebooted, and let the build run overnight; reported results looked good.
Open questions: wpc-08 formal validation harness remains pending if detailed reproducible scoring artifacts are needed; no wpc-07 follow-up is open from this closeout.

## [2026-08-18] instruction | [wintap] wpc-09 minor bug sweep drafted

Decisions made: wpc-08 formal validation harness is skipped, without renumbering, because the Architect accepted manual slice-2 validation on 2026-08-18: process tree back to kernel-era roots, usernames present on all reviewed records, and a stable overnight run. wpc-09 is the final code unit before closeout.
ADRs written or updated: none.
Wiki pages updated: `wiki/work/improve-windows-process-collection/smoke-followups-2026-08-17.md` (2026-08-18 overnight findings recorded); `wiki/work/improve-windows-process-collection/implementation_plan.md` (wpc-08 skip note and wpc-09 unit note); `wiki/work/improve-windows-process-collection/metrics.md` (sealed wpc-09 pre-implementation estimate); `wiki/log.md`.
Instructions written: `../wintap/developer_docs/instructions/wpc-09-bug-sweep.md` (Status: Draft — Architect approval pending).
Open questions: Developer must verify from logs whether the missing-parent warnings are fixable resolution gaps or expected unresolvable-parent races; Developer must verify whether process-name parsing errors share the DuckDB command-line escaping root before changing that path.

## [2026-08-18] approval | [wintap] wpc-09 minor bug sweep instruction approved

Decisions made: Architect approved the wpc-09 minor bug sweep instruction for Developer handoff. Scope remains limited to the final WPC code-unit sweep: boot-trace arm/disarm lifecycle fix, missing-parent warning triage/fix-or-annotation, process-name / DuckDB command-line escaping triage and fix if confirmed, and cosmetic QA-counter logger attribution only if still trivially broken.
ADRs written or updated: none.
Wiki pages updated: `wiki/log.md` only.
Instructions updated: `../wintap/developer_docs/instructions/wpc-09-bug-sweep.md` (Status: Approved — Architect approval 2026-08-18).
Open questions: none for instruction approval; Developer must still record triage dispositions and manual-smoke evidence in `developer_docs/audits/wpc-09-bug-sweep.md`.

## [2026-08-19] closeout | [wintap] improve-windows-process-collection feature closed

Decisions made: Architect approved feature closeout. Outcome: the unified `WindowsProcessSensor` (kernel-ETW Start/Stop on the shared session, ETW-canonical PidHash, snapshot Refresh with dedup, SID/command-line/path enrichment with fallbacks, manifest Stop-metric merge, opt-in Global Logger boot-trace replay, QA counters) fully replaced the Security-log and KernelProcessSensor paths — no audit-policy dependency, no log-wrap failure mode. Final code state: wintap develop-operator `19e89dc` (wpc-07 + wpc-09), 54/54 wpc tests and 55/55 project-wide passing, Release build 0 errors. Final overnight smoke-test 2026-08-18→19 PASS with boot replay confirmed end-to-end (arm at shutdown, owned stop/disarm at startup, replay), resolving the wpc-09 audit's pending item; earlier blocker was an external Code42-AAT lock on the DuckDB event store, and `19e89dc` also fixed the contributing Windows runtime data-root fallback. wpc-08 formal harness remained skipped (Architect decision 2026-08-18; manual validation accepted).
Pages created: `work/improve-windows-process-collection/verification.md` (accepted manual validation evidence, test/build state, wpc-08 skip rationale).
Pages updated: `work/improve-windows-process-collection/metrics.md` (mini-lab close-out: status closed; ts_design_end 2026-08-17, ts_final_audit 2026-08-18; actual_attention_hours 3.47 with proxy method record; human estimates unsealed; close-out answer recorded verbatim — feature only partially attempted solo, SID reverse engineering and PEB lookup not at all; ~120h est. vs 3.47h measured, retrofit seal-break and undercount caveats noted); `event_type/process-events.md` (durable semantics promoted from the feature work folder, regrounded to live `WindowsProcessSensor`/helper sources); `work/improve-windows-process-collection/implementation_plan.md` (done checklist closed: wpc-09 done, wpc-08 explicitly skipped, verification/promotion done); `work/improve-windows-process-collection/smoke-followups-2026-08-17.md` (final disposition: wpc-09 items resolved; SensSensor and SignedS3UrlAdapter remain future candidates outside the feature); `index.md`.
Contradictions flagged: none.
Open questions: none for this feature. Remaining ecosystem follow-up candidates live in `smoke-followups-2026-08-17.md` (SensSensor load failure, missing SignedS3UrlAdapter); deferred measurement of cmdline/SID fallback rates is available via QA counters whenever wanted.

## [2026-08-19] decision | AI velocity/ROI mini-lab revised to v2 (scheduled post-pilot revision)

What changed: headline metrics pivot to boundary/outcome measures — time-to-availability (raw calendar lead time, weekends included, feature open → first Architect-accepted validation artifact) plus throughput (counterfactual-hours delivered per window, weighted by sealed solo estimates); the two sealed interview questions are re-posed in calendar terms under the displacement ratchet; the 15-minute-gap attention proxy is demoted to an optional, coverage-annotated diagnostic (merge-then-cluster rule if ever multi-harness). See `wiki/decision/ai-velocity-roi-mini-lab.md` (Revision History).
Pages updated: `wiki/decision/ai-velocity-roi-mini-lab.md` (v2 in place); `wiki/concept/metrics-template.md` (v2 field set); `wiki/concept/feature-work-template.md` (calendar-posed sealed Q1/Q2); `wiki/concept/llm-assisted-feature-workflow.md` (interview step 7 phrasing); `wiki/work/improve-windows-process-collection/metrics.md` (v2 addendum: lead time 6 calendar days 2026-08-13→19 anchored on the boot-replay-confirming final overnight smoke-test per brief criterion 6; solo counterfactual ~2026-09-02/20 calendar days flagged as a units reconstruction; throughput weight 120h; attention 3.47h kept as coverage-annotated diagnostic); `wiki/index.md`.
Wintap process docs: proposed diffs to `../wintap/.claude/agents/engineer.md` and `../wintap/CLAUDE.md` drafted for Architect review per the ADR ownership note — not applied.
Contradictions flagged: none.
Open questions: none for the revision itself; cross-harness attention adapters remain deferred until a feature routes significant attention through OpenCode.

## [2026-08-19] closeout | [wintap] wpc-09 final scope and verification complete

Decisions made: Architect marked wpc-09 complete. The final sweep includes the boot-trace lifecycle, DuckDB parameterization, parent-warning annotation, QA logger attribution, and restoration of platform-owned runtime data-root defaults after the accidental Windows `<local-path>` location contributed to external DuckDB contention.
ADRs written or updated: `wiki/decision/platform-runtime-data-root-defaults.md` (Accepted).
Wiki pages updated: `wiki/index.md`; `wiki/work/improve-windows-process-collection/implementation_plan.md`; `wiki/work/improve-windows-process-collection/verification.md`; `wiki/log.md`.
Verification: Release build completed with 0 errors; `Category=wpc-09` 19/19 passed; `Category~wpc` 64/64 passed; full test project 65/65 passed. Architect reported the post-reboot Wintap retry operating successfully and directed completion.
Open questions: none for wpc-09; existing implicit `<local-path>` data is intentionally not migrated.

## [2026-08-19] decision | Velocity metric adopted (mini-lab v2.1 after external review)

Decisions made: Architect approved the final **Velocity** protocol (pitch approved 2026-08-19 after an external review cycle; authoritative source `../wintap/developer_docs/design/velocity-pitch-2026-08-19.md`). Headline: Velocity, dimensionless, unit solo-FTE equivalents, canonical formula `Velocity = solo-hours / (5.714 × days)`; 5.714 is a declared one-FTE capacity unit (no realism or conservatism claim, fixed once); two views one unit — Feature Velocity (speedup) and Portfolio Velocity (normalized delivered throughput; not an average — the gap is the parallelism dividend); "solo-hours" replaces "counterfactual-hours"; reporting is point values to one decimal with a stated uncertainty range (band from the two sealed estimates, default ±2×); sealed Q1 becomes a forced counterfactual (hours + realistic calendar date); guardrails adopted: frozen acceptance criteria, availability finality (defect-reopen rule rejected — ledger self-corrects forward), comparability flagging with the capability-vs-willingness distinction; cost stays a companion field.
Pages created: `wiki/concept/velocity-metric.md` (approved pitch carried faithfully into the wiki); `wiki/metrics.md` (cross-feature Velocity rollup, seeded with the WPC row: 6 days, 120 h, Velocity 3.5 uncertainty 2–7, willingness-only flag, retrofit-pilot annotation; Portfolio Velocity pending N≥several with trailing window ≥ 4× median lead time).
Pages updated: `wiki/decision/ai-velocity-roi-mini-lab.md` (v2.1 revision; new Alternatives Considered: per-developer baselines rejected, directional-bias constant framing withdrawn, bands-never-decimals rejected, defect reopen rule rejected); `wiki/concept/metrics-template.md` (v2.1 field set: leading Headline block, `feature_velocity`/`velocity_uncertainty`/`comparability`/`criteria_amendments`, `throughput_weight_hours` → `solo_hours`, `ai_est_solo_hours` added, methodology as links); `wiki/concept/feature-work-template.md` and `wiki/concept/llm-assisted-feature-workflow.md` (forced-counterfactual Q1 / calendar Q2 phrasing); `wiki/work/improve-windows-process-collection/metrics.md` (Velocity addendum: 3.5, uncertainty 2–7, pilot and willingness-not-capability caveats — added, nothing erased); `wiki/index.md`.
Wintap process docs: diffs to `../wintap/.claude/agents/engineer.md` and `../wintap/CLAUDE.md` redrafted against the final protocol and returned for Architect review — not applied, per the ADR ownership note.
Contradictions flagged: none hard. Two v2 statements corrected in place: the raw throughput companion is superseded by normalized Portfolio Velocity (the solo-hour sum survives as its numerator), and v2's "hours are never compared against elapsed time" safety note was removed because the canonical formula compares them deliberately via the declared 5.714 unit.

## [2026-08-20] maintenance | WPC metrics aligned to approved Velocity framing

Pages updated: `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/index.md`; `wiki/log.md`.
Changes: Replaced the accumulated v1/v2/v2.1 narrative and multiple YAML blocks with the canonical single-block Velocity format; made Feature Velocity 3.5 (uncertainty 2–7) the headline; retained the 120 solo-hour, 6-calendar-day, availability-anchor, comparability, per-unit, cost, and attention evidence; explicitly classified the pilot as retrospective/unsealed and illustrative; removed the obsolete attention-based rough-ROI framing and kept 3.47 hours only as a coverage-annotated diagnostic.
Decisions made: none — this is a conformance edit against the Architect-approved `wiki/concept/velocity-metric.md` definition.
Contradictions flagged: none.

## [2026-08-20] maintenance | WPC Velocity scorecard simplified

Pages updated: `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/index.md`; `wiki/log.md`.
Changes: Reworded the feature headline as a plain-language scorecard: estimated delivery speed 3.5× one solo developer's pace, plausible range about 2×–7× faster, low confidence, and a direct explanation for that low confidence. Moved formula-oriented language into a clearly labeled Technical Record while preserving the canonical YAML fields and underlying evidence.
Decisions made: none — presentation-only simplification; the approved metric and recorded values are unchanged.
Contradictions flagged: none.

## [2026-08-20] maintenance | Standardized overnight smoke-test wording

Pages updated: WPC metrics, verification, implementation plan, smoke follow-ups, canonical process-event page, index, and historical log references.
Changes: Replaced “overnight smoke” and “overnight smoke test” with the requested “overnight smoke-test” wording.
Decisions made: none; terminology-only correction.
Contradictions flagged: none.

## [2026-08-20] maintenance | WPC metrics summary labeled Results

Pages updated: `wiki/work/improve-windows-process-collection/metrics.md`; `wiki/log.md`.
Changes: Renamed the plain-language scorecard heading from “Headline” to “Results” so the pilot document models the intended future presentation.
Decisions made: none; presentation-only change.
Contradictions flagged: none.

## [2026-08-20] maintenance | Future feature metrics inherit simplified Results

Pages updated: `wiki/concept/metrics-template.md`; `wiki/concept/velocity-metric.md`; `wiki/concept/feature-work-template.md`; `wiki/concept/llm-assisted-feature-workflow.md`; `wiki/index.md`; `wiki/log.md`.
Changes: Made **Results** the standard reader-facing section for future feature metrics; it now reports estimated delivery speed as a multiple of one solo developer's pace, an “about X×–Y× faster” plausible range, a deterministic Low/Medium/High confidence label, and one direct confidence reason. Canonical formulas and YAML remain under **Technical Record**. Removed inherited “Headline” and reader-facing “uncertainty 2–7” wording from the concept templates and examples.
Decisions made: Presentation convention only; the approved Velocity formula, fields, guardrails, and raw evidence are unchanged.
Contradictions flagged: none.

## [2026-08-20] update | Wintappy pidstat raw_sensor-path bugfix documented

Sources read: `../Wintappy/wintap_dbt/dbt_project.yml`; `../Wintappy/wintap_dbt/macros/paths.sql`; `../Wintappy/wintap_dbt/macros/raw_sources.sql`; `../Wintappy/wintap_dbt/models/bronze/stg_pidstat_metrics.sql`; `../Wintappy/wintap_dbt/README.md`; `../Wintappy/Makefile`.
Pages created: none.
Pages updated: `repo/wintappy-pipeline-repo.md`; `work/improve-pidstat-collector/brief.md`; `work/improve-pidstat-collector/references.md`; `work/improve-pidstat-collector/design.md`; `work/improve-pidstat-collector/dev_handoff.md`; `work/improve-pidstat-collector/implementation_plan.md`; `work/improve-pidstat-collector/verification.md`; `index.md`; `log.md`.
Summary: documented the follow-up bugfix that removed `PIDSTAT_DATA_PATH` and the dedicated pidstat DBT macro/override in Wintappy. `stg_pidstat_metrics` now resolves `raw_sensor/pidstat` from `WINTAP_DBT_RAW_SENSOR_DATASET` through the shared raw-event helpers and uses the same day/hour partition-window narrowing as the other optional raw events.
Contradictions flagged: none.

## [2026-08-23] diagnostic | Lintap runtime high-CPU collector utility

Context: current field host has `<local-path>` running for six days at roughly 8.5 CPU cores, with all major sensors enabled and default process-retention settings. Non-root inspection could not read `<local-path>`, service environment, file descriptors, or full journals.
Files created: `extras/lintap-runtime-diagnostics/README.md`; `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`.
Purpose: root-run, read-only diagnostic bundle for pidhash/process-table runtime performance work. It collects service/process/thread samples, redacted config, journals, filesystem summaries, fork-rate data, optional perf/dotnet/pidstat samples, and read-only DuckDB summaries/`EXPLAIN ANALYZE` output for process-table and retention telemetry investigation.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-23] diagnostic | validation-host Lintap high-CPU field findings

Source: `<local-path>` root-run diagnostics using a copied DuckDB event-store database.
Findings: `process` table retention is working at field scale (`64,742` rows after six days), but `process_retention_telemetry` has grown to `16,190,964` per-identity rows and is now the unbounded table. Runtime CPU remained high (`8.5` cores by `ps`, `13.9-15.2` CPUs by `perf stat`) across many native `Lintap` threads and sensor pollers. Fork rate was low (`~3/sec`), ruling out the earlier pidstat shell fork storm. Schema output showed no `process` indexes and pidhash lookup plans used sequential scans over ~64k rows. Process rows/telemetry were dominated by short-lived monitor commands and `python3.12` rows parented to the pidstat collector, suggesting clone/thread events are being registered as process rows.
Recommended fixes: aggregate and retain/prune `process_retention_telemetry`; filter `CloneSensor` thread clones (`CLONE_THREAD`) so thread IDs do not pollute the pidhash process table; evaluate `process_id, create_time` indexing after reducing telemetry/thread-clone churn.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-23] fix | pidstat collector conversion noise mitigation

Source: validation-host field diagnostic showed many short-lived `python3.12` process rows parented to the pidstat collector while it was manually running with `PIDSTAT_ROTATE_INTERVAL_SEC=10`.
Files changed: `../Lintap/pidstat-collector.py`; `../Lintap/tests/test_pidstat_collector.py`; `../Lintap/README.md`; `../Lintap/packaging/lintap-rpm/lintap.env`; `../Lintap/packaging/lintap-deb/lintap.env`; `../Lintap/packaging/lintap-rpm/README.md`; `../Lintap/packaging/lintap-deb/README.md`.
Fix: clamp rotation to `PIDSTAT_MIN_ROTATE_INTERVAL_SEC` default `300`, add `PIDSTAT_DUCKDB_THREADS=1`, reuse one DuckDB connection for parquet conversion, and log the effective quieting settings at startup. This reduces collector-induced process/clone noise before addressing broader CloneSensor thread filtering.
Validation: `uv run --group dev pytest tests/test_pidstat_collector.py` in `../Lintap` passed (`14 passed`).
Pages updated: `work/improve-pidstat-collector/verification.md`; `log.md`.

## [2026-08-23] diagnostic | pidstat mitigation post-restart check

Source: `<local-path>` after restarting the manual pidstat collector with `PIDSTAT_MIN_ROTATE_INTERVAL_SEC=300` and `PIDSTAT_DUCKDB_THREADS=1`.
Results: collector-induced noise dropped materially: fork-rate sample was effectively zero (`processes_delta_10s=4`), `python3.12` disappeared from the current top process-row producers, and open `python3.12` rows fell from `1117` to `31`. Lintap CPU improved by `perf stat` sample (`13.9-15.2` CPUs before to `9.4` CPUs after) but remained high by `ps` (`~8.5` cores). `process` remained bounded (`47,135` rows), while `process_retention_telemetry` still grew to `16,362,388` rows, adding ~171k rows over ~98 minutes.
Conclusion: pidstat conversion churn is mitigated, but the remaining high-CPU/runtime-quality work should move to `../wintap`: aggregate/prune `process_retention_telemetry`, filter `CloneSensor` thread clones, then reassess process lookup indexing.
Pages updated: `work/improve-pidstat-collector/verification.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-23] fix | process retention telemetry bounded

Files changed: `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `../wintap/shared/ai/wintap_mcp_server/wintap_mcp_server.csproj`.
Fix: `process_retention_telemetry` now writes aggregate rows by default instead of one row per process identity; per-`pid_hash` detail is opt-in via `WINTAP_PROCESS_RETENTION_TELEMETRY_DETAIL_ENABLED=true`. Added `WINTAP_PROCESS_RETENTION_TELEMETRY_RETENTION_SEC` with a 24-hour default and prunes old telemetry rows every maintenance sweep. Startup logging includes the telemetry retention/detail settings.
Build fix: MCP publish had failed because generated files under `shared/ai/wintap_mcp_server/mcp_temp/obj` were included by the MCP project source glob, causing duplicate assembly attributes. The MCP project now excludes `mcp_temp/**` alongside direct `obj/**` and `bin/**`.
Validation: direct MCP publish passed; `dotnet build wintap/Lintap.csproj` in `../wintap` passed with existing warnings and `0` errors.
Pages updated: `work/fix-unbounded-process-table-growth/design.md`; `work/fix-unbounded-process-table-growth/implementation_plan.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] feature | [wintap] windows-sensor-health-check opened: exploration, design, plan, shc-01 draft

Decisions made (Architect, via interview — recorded in `work/windows-sensor-health-check/interview.md`): health checks run in-agent at the WintapMessage egress choke point before serialization; aggregated per-sensor-stream/per-check counters flushed periodically as dedicated health messages into the normal Parquet stream with a capped first-N sample; coverage is all Windows sensors including WindowsProcessSensor; full-stream constant-time checks, no sampling.
Mini-lab: `work/windows-sensor-health-check/metrics.md` created with the Engineer's independent sealed estimates recorded BEFORE reading the interview's sealed section (seal intact): ai_est_solo_hours 48, solo date 2026-09-18, AI-workflow date 2026-08-31. Acceptance criteria frozen at open in `brief.md` per ADR guardrail 1. Per-unit estimate recorded for shc-01 (2.5 h).
Exploration findings (grounded in `../wintap` source): the real choke point is `EventChannel.Send`, but it has two egress branches (DirectParquetSink early-return — pre-enrichment — and the post-enrichment Esper→Serializer→ParquetWriter path), so the hook lands at both emit sites. Surprises: (1) `MemoryMapSensor.cs:308` bypasses Send entirely via direct `SendEventBean` (no AgentId, no self-PID filter); (2) `Watchdog`/`PluginExceptionHandler` WintapAlert messages carry Wintap's own PID and are silently dropped by Send's self-PID filter — self-generated alerts likely never reach output today; (3) `Serializer.Save` NULL_PIDHASH and `DefaultSerializer` payload-reflection failures are silent drop paths the checks will make visible.
Pages created: `work/windows-sensor-health-check/metrics.md`; `brief.md` (nine frozen acceptance criteria); `design.md` (egress hook, check registry, SensorHealth message schema, 60 s flush, sample cap 3, constant-time overhead argument, risks, alternatives); `implementation_plan.md` (abbreviation `shc` declared, no collision; units shc-01 core engine → shc-02 message+flush → shc-03 wire-in+verification).
Instructions written: `../wintap/developer_docs/instructions/shc-01-health-check-core.md` (Status: Draft — Architect approval pending; pure new engine code, no production wiring, independent of all open design questions).
Open questions (Architect, before shc-02/shc-03 drafting): approve the WintapMessage schema addition (SensorHealth enum + payload); MemoryMapSensor coverage approach; EmitSensorHealth vs. Send exemption branch; optional `process_unresolved` check; confirm defaults (60 s / cap 3 / enabled-on-Windows). Side observation: the ptr feature (merged in ../wintap 2026-08-22/23) has no entries in this log — fold-in appears owed.

## [2026-08-24] redirection | [wintap] windows-sensor-health-check simplified to log-only reporting

Decisions made (Architect, same-day redirection — recorded in interview.md Round 2): health results are periodic aggregated Wintap.log entries via WintapLogger, nothing else. Superseded from the first-draft design: the dedicated SensorHealth WintapMessage/Parquet output, any WintapMessage schema change, the EmitSensorHealth path, and the self-PID-filter exemption (the latter two problems disappear with the schema change). Rationale: "This is a supportive feature, not the mission of wintap... start simple and extend if needed." Unchanged: egress choke point in `EventChannel.Send` (both branches), the four v1 checks, full-stream constant-time cost, aggregated counters + capped first-N samples, all-Windows-sensor coverage, low-noise periodic summaries (never per-failure). Adopted defaults without further round-trips (per Architect direction): MemoryMapSensor gets a one-line Inspect at its direct-send site in the wire-in unit; the `process_unresolved` ("Unknown" sentinel) check is deferred to the follow-on sweep feature.
Mini-lab: criteria amendment logged in `work/windows-sensor-health-check/metrics.md` `criteria_amendments` (2026-08-24, reporting channel Parquet→Wintap.log); criteria re-frozen same day in brief.md. Seal on the interview's human estimates remains intact — the Engineer did not read the sealed section. shc-01 per-unit estimate revised pre-implementation from 2.5 h to 3.0 h (flush/log formatting folded into the unit).
Pages updated: `work/windows-sensor-health-check/brief.md` (re-frozen criteria, now eight; amendment banner); `design.md` (log-line reporting design, WintapAlert self-PID drop finding retained as sweep-feature note, alternatives updated with the rejected first-draft message design); `implementation_plan.md` (reduced from three units to two: shc-01 engine+checks+log flush, shc-02 egress wire-in + end-to-end verification); `metrics.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/shc-01-health-check-core.md` rewritten for the merged scope (engine + checks + periodic log flush via injectable sink; hot-path contract and fail-open wrapper retained; all message/flush-to-Parquet plumbing removed; filename slug unchanged — still accurate). Status: Draft — Architect approval pending.
Open questions: none — the redirection and adopted defaults resolved all previously flagged decisions.

## [2026-08-24] amendment | [wintap] windows-sensor-health-check v1 check list made definitive (amendment #2)

Decisions made (Architect review of the shc-01 draft, same day): the v1 conditions are now definitive. (1) "Unknown" process attribution FAILS — reverses the draft's pass note ("this is exactly the failure mode i want to catch"); implemented as a new `process_unresolved` check: ProcessName == "Unknown" (case-insensitive) OR PidHash == the unknown-sentinel hash. (2) `processname_missing` and `payload_mismatch` stand. (3) New `path_unqualified` check: File and Registry payload paths must be fully qualified in their grounded emitted forms; other streams exempt. (4) New stream-liveness condition: File, Registry, MemoryMap, ImageLoad, TcpConnection, UdpPacket must each show nonzero inspected counts per 5-second interval; a zero interval is a critical condition — transition-only logging (one Error STALL line, one Info RECOVERED line with duration), 60 s startup grace, suppression across Stop(). (5) `eventtime_invalid` DROPPED from v1; preserved in design.md as the first candidate future check.
Grounding added to design.md: the unknown sentinel — EventChannel sets literal ProcessName="Unknown" on owner-resolution failure with a *fabricated but indistinguishable* fallback PidHash; the only distinguishable sentinel hash is `ProcessHash.GenPidHash(-1, 0)` (EventChannel's UnknownPidHash, parent-lineage use only today), and it is HOST-SPECIFIC (formula mixes MachineName + AgentId) so it must be computed at runtime / injected in tests. Path forms — File.Path is lowercased with forms `<local-path>`, `\\...` (UNC), `\device\...`; Registry paths are lowercased KCB paths rooted `registry\...` (leading backslash trimmed). Surprise: RegistrySensor's CreateKey/DeleteKey/DeleteValue emit sites are ungated (no StartsWith("registry") filter), so relative key fragments can egress today — `path_unqualified` will count exactly that; fixing the sensor is sweep scope. Parent-lineage "Unknown" sentinels deliberately excluded from v1 (designed ptr best-effort behavior) — candidate future check.
Mini-lab: amendment #2 logged in `work/windows-sensor-health-check/metrics.md` `criteria_amendments`; criteria re-frozen in brief.md (nine criteria); seal on the human estimates remains intact. shc-01 per-unit estimate revised pre-implementation 3.0 h → 4.0 h (two new checks + liveness state machine).
Pages updated: `work/windows-sensor-health-check/brief.md`; `design.md`; `implementation_plan.md`; `metrics.md`; `wiki/log.md`.
Instructions updated: `../wintap/developer_docs/instructions/shc-01-health-check-core.md` rewritten with the definitive five-check registry, injected sentinel seam, grounded path-form matrices, and the liveness state machine + tick seam. Status: Draft — Architect approval pending.
Open questions: none.

## [2026-08-24] audit+instruction | [wintap] shc-01 complete; shc-02 egress wire-in drafted

Decisions made: none new. Developer completed the approved shc-01 unit: standalone health-check engine, five definitive checks, liveness watchdog, and periodic log flush landed as pure new code under `../wintap/wintap/core/infrastructure/health/` with no production files modified. Verification: 33/33 via `dotnet test --filter "Category=shc-01"`, independently re-verified by the main session 2026-08-24; documented deviation — solution-level `dotnet build -c Release` fails with the known Wintap-Workbench MSB4249 issue, approved project-scoped fallback used. Audit: `../wintap/developer_docs/audits/shc-01-health-check-core.md` (Complete). Provenance note recorded in the feature's new verification.md: `/developer_docs/` is gitignored in the wintap repo, so instruction/audit artifacts are local-only process files — the wiki preserves the durable evidence.
Mini-lab: shc-01 `actual_hours` recorded as missing data per never-gates (audit/log carry only the date; no intra-day timestamps and no commit trail for gitignored artifacts). shc-02 per-unit estimate recorded pre-implementation: 3.0 h (three one-line call sites + EventChannel seam + lifecycle + heavy-statics test fixture + manual live run). Seal on the interview's human estimates remains intact.
Instruction drafted: `../wintap/developer_docs/instructions/shc-02-egress-wire-in.md` (Status: Draft — Architect approval pending). Grounded call-site placements: (1) inside the `DirectParquetSink.IsEnabled` block before `Save` (branch returns — exactly one Inspect per message, no double-inspect); (2) normal branch post-enrichment/post-registration, immediately **above** the `skipEsperSend` early return (production-identical; enables integration tests without live Esper — design.md skip-seam edge note revised accordingly); (3) one line in `MemoryMapSensor.refreshSnapshot` before its direct `SendEventBean` (~line 308) via a shared `EventChannel.InspectForHealth` helper with an internal test-seam override. Lifecycle grounded in `WintapSvcCore.cs`: `SensorHealthMonitor.Default.Start()` immediately after `subscriptionMgr.Start()` (not started under `WINTAP_DISABLE_SENSORS`); `Stop()` as the first action of `StopAsync` (suppresses shutdown stall alarms; final flush before logger close).
Surprise found and recorded in design.md: a third direct `SendEventBean` exists at `../wintap/wintap/core/etl/extract/Serializer.cs:150` (`Serializer.Listen`) — dead code with no callers and a "do we still need this?" TODO; it gets no Inspect call and is flagged as a sweep-feature deletion candidate.
Pages updated: `work/windows-sensor-health-check/implementation_plan.md` (shc-01 checked); `work/windows-sensor-health-check/design.md` (Serializer.Listen correction; refined call-site placement + single-inspection guarantee; skip-seam edge note revision; lifecycle grounding); `work/windows-sensor-health-check/metrics.md`; `wiki/log.md`.
Pages created: `work/windows-sensor-health-check/verification.md` (shc-01 evidence; shc-02/manual-run placeholder as availability-anchor candidate).
Open questions: Architect approval of the shc-02 draft, including two flagged points — the small internal `HealthMonitorOverride`/`InspectForHealth` seam added to EventChannel.cs (kept within the allowed-file list) and the integration-test posture around the heavy StateManager/EventChannel type initializers (temp data root + env seams, with a documented fallback for the direct-parquet branch test).

## [2026-08-24] instruction | [wintap] shc-02 paused on diskpart elevation conflict; enabling unit shc-03 (QueryDosDevice drive map) drafted

Decisions made (Architect): the Developer started the approved shc-02 and stopped correctly on an instruction/codebase conflict — the no-admin integration tests fail because the first `EventChannel.Send` initializes `StateManager`, whose ctor calls `WindowsStateManager.RefreshDriveMap()` (`../wintap/wintap/platform/windows/infrastructure/WindowsStateManager.cs:35`), which spawns `diskpart.exe` and requires elevation (`Win32Exception`), with no try/catch around the spawn. No audit filed; shc-02 is paused. Architect inserted enabling unit **shc-03 — replace the diskpart drive mapping with QueryDosDevice** — which lands BEFORE shc-02 resumes despite the number (execution order shc-01 → shc-03 → shc-02, recorded in the implementation plan). Explicitly NOT a criteria amendment: the frozen brief criteria are unchanged.
Grounding (verified in ../wintap): `RefreshDriveMap` has one production caller (`StateManager` ctor, `#if WINDOWS`, once per process — the 60 s state timer never refreshes the drive map) and `DriveMap` has one reader (`BaseWindowsSensor.fromNative`, which rewrites `\device\harddiskvolumeN\...` → `letter:\...` by `VolumeNumber` lookup). Nothing serializes `DiskVolume`; its Label/FileSystem/Type fields are dead. Correctness finding: diskpart's `Volume ###` is an enumeration index, not the NT HarddiskVolumeN number `fromNative` looks up, so today's map silently mismatches and most native-path rewrites land in the hardcode-`c:` fallbacks — QueryDosDevice is the authoritative source and shc-03 is the feature's first genuine accuracy fix. Precedent found: `WindowsProcessSensor` already P/Invokes `QueryDosDevice` (`TryTranslateDevicePathToWin32Path`); shc-03 mirrors that signature. Residual flagged for Architect: `fromNative`'s `volumeNumber <= diskVolumes.Count` guard bypasses the corrected map whenever NT numbers exceed the lettered-drive count (typical: EFI/recovery volumes consume low numbers), hardcoding `c:` on multi-drive hosts — not a regression, but the accuracy fix is unrealized until the guard is removed (follow-up unit or sweep feature). `TranslateTransientPath`'s WMI partition-number parse has a similar authority problem (sweep candidate). A duplicate `DiskVolume` in `platform/windows/WintapCoreSvcMgr` is unaffected.
Mini-lab: shc-03 per-unit estimate recorded pre-implementation in `work/windows-sensor-health-check/metrics.md`: 1.5 h (single-file P/Invoke swap with exact in-repo precedent + pure seam + ~7 no-admin tests); shc-02 pause noted on its unit row, estimate unchanged. Seal on the interview's human estimates remains intact — interview.md was not read this session.
Instructions written: `../wintap/developer_docs/instructions/shc-03-querydosdevice-drive-map.md` (Status: Draft — Architect approval pending; exact P/Invoke signature, normative parse rules and edge-case table, never-throws fail-soft contract, `BuildDriveMap` test seam + lenient live smoke test, scope locked to WindowsStateManager.cs + tests, non-elevated test-run requirement).
Pages updated: `work/windows-sensor-health-check/implementation_plan.md` (three units; execution-order section; shc-02 paused; files/tests/checklist rows); `work/windows-sensor-health-check/design.md` (revision banner #3; new "shc-03 Insert" section: snag record, consumer map, grounded rationale, precedent, residual fromNative-guard flag); `work/windows-sensor-health-check/metrics.md`; `wiki/log.md`.
Open questions: Architect approval of the shc-03 draft; Architect decision on where the `fromNative` guard fix lives (widen shc-03? follow-up shc unit? sweep feature?).

## [2026-08-24] instruction | [wintap] shc-03 widened to include the fromNative guard fix (Architect decision)

Decisions made (Architect, same day): the open question from the previous entry is resolved — **widen shc-03** to include the `BaseWindowsSensor.fromNative` guard fix so the drive-map accuracy fix is realized immediately rather than deferred to the sweep feature. The feature's no-sensor-changes posture gets a **scoped exception** for exactly `BaseWindowsSensor.cs` and exactly this fix. Fix as specified in the instruction: remove the `volumeNumber <= diskVolumes.Count` guard (direct `VolumeNumber` lookup always runs; translate on match); on a genuine miss, preserve today's fallback verbatim (the existing logged `Got null DiskVolume...` line + hardcode `c:` — no new handling invented); remove the single-drive `harddiskvolume1` hack as provably dead logic (it only ran where the lookup already guaranteed `dv.VolumeNumber == volumeNumber`, and it mutated the shared cached DriveMap entry); outer catch and pre-`try` parse untouched. Testability seam kept minimal: `fromNative` accessibility `private` → `internal` only (no delegate injection, no overload); tests construct `BaseWindowsSensor` directly via the existing `InternalsVisibleTo`, the established wpc sensor-test pattern. Five translation-path tests added to the unit (NT number > drive count — the old-guard breakage case; multi-drive correct-letter selection; genuine-miss legacy fallback; rewritten-path format preservation; quoted-path cleanup). Still not a criteria amendment; the frozen brief criteria are unchanged.
Process note: while the widening was being folded in, an "Approved 2026-08-24" stamp appeared on the shc-03 instruction file on disk. Per the Architect's explicit direction that the widened version be read before approval, the header was reverted to Status: Draft / Approval: Pending with an explanatory comment — a pre-widening stamp cannot cover the widened content; flagged to the Architect for the (re-)approval gate.
Mini-lab: shc-03 per-unit estimate revised pre-implementation in `work/windows-sensor-health-check/metrics.md`: 1.5 h → 2.0 h (guard fix + ~5 translation-path tests + accessibility seam). Seal on the interview's human estimates remains intact — interview.md was not read this session.
Instructions updated: `../wintap/developer_docs/instructions/shc-03-querydosdevice-drive-map.md` (widened: two production files; grounded current `fromNative` code and exact replacement method; hard-constraints block carries the scoped sensor-file exception; acceptance criteria and Out of Scope updated; tests 8–12 added). Status: Draft — Architect approval pending on the widened version.
Pages updated: `work/windows-sensor-health-check/implementation_plan.md` (shc-03 description/tests/files widened); `work/windows-sensor-health-check/design.md` (revision banner; residual-guard paragraph rewritten as the recorded widen-not-defer decision with the Architect's realize-now rationale); `work/windows-sensor-health-check/metrics.md`; `wiki/log.md`.
Open questions: Architect approval of the widened shc-03 draft (including confirming the reverted approval stamp).

## [2026-08-24] validation | validation-host post-RPM telemetry bounding check

Source: `<local-path>` after building/installing the new RPM with the telemetry aggregation fix and running for about 2.5 hours.
Results: Lintap PID `1918289` sampled at `1.211` CPUs by `perf stat` (vs. `9.4` after pidstat mitigation and `13.9-15.2` before). Fork rate was quiet (`5` process creations over 10 seconds). `process` table remained bounded at `47,648` rows. `process_retention_telemetry` was reduced to `4,721` aggregate rows, with aggregate totals preserved in `metric_value`. Copied DuckDB size was `19.0 MiB`, down from ~`761 MiB` before the telemetry fix. Process lookup plans still used sequential scans over ~47k rows but query times were small in the copied DB.
Conclusion: process-retention telemetry aggregation/retention fixed the runaway telemetry table and materially reduced Lintap runtime CPU on the field host. Remaining follow-ups: CloneSensor thread-clone filtering and optional lookup indexing.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] diagnostic | process lookup index low leverage in field snapshot

Source: `<local-path>`.
Findings: Lintap remained stable at `1.471` CPUs by `perf stat`; `process` had `48,628` rows and `process_retention_telemetry` had `9,459` aggregate rows. The copied DB included `idx_process_process_id_create_time` on `(process_id, create_time)`, but representative pidhash lookup plans still used sequential scans over ~48k rows, with copied-DB query times around `0.012-0.025s`. Hot threads were sensor pollers (`CloneProcess`, `FileOps`, `ExitProcess`, `ExecveProcess`) rather than telemetry/DB churn.
Conclusion: additional DuckDB indexing is not the next highest-leverage fix. Prefer CloneSensor thread-clone filtering or an in-memory current-process map if further CPU reduction is needed.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] fix | CloneSensor filters thread clones

Files changed: `../wintap/wintap/platform/linux/sensor/ebpf/CloneSensor.cs`.
Fix: CloneSensor now skips clone events with `CLONE_THREAD` (`0x00010000`) before reading `/proc` or emitting process `Start` rows. Unknown clone flags (`0`) and the vfork sentinel remain accepted to preserve fork/vfork/process-like clone coverage.
Rationale: field diagnostics showed thread IDs being registered as processes, polluting the pidhash/process table and increasing stale-open reconciliation work.
Validation: `dotnet build wintap/Lintap.csproj` in `../wintap` passed with existing warnings and `0` errors.
Pages updated: `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] maintenance | Lintap runtime diagnostics utility cleanup

Files updated: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`; `extras/lintap-runtime-diagnostics/README.md`.
Changes: removed hardcoded DuckDB PATH and hardcoded `<local-path>`; added `--db` override; added upfront required/optional command reporting in `requirements.txt`; added DuckDB CLI discovery across PATH and common install locations; added automatic live-DB lock probing and snapshot fallback that copies `main.duckdb` plus `main.duckdb.wal` when present into `duckdb/snapshot/` before running read-only queries; updated manifest and summary notes to record source/query DB paths.
Validation: `bash -n extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` passed; `--help` output verified.

## [2026-08-24] review | Initial FileOps poller optimization note captured

Source: simple source inspection of `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`, `file_ops_tracer.bpf.c`, `file_ops_tracepoint.bpf.c`, and field diagnostics where `FileOps-Poller` remained the dominant hot thread after pidstat/telemetry fixes.
Result: recorded a future-todo note, explicitly marked as an initial review rather than a decided design. Main hypothesis: reduce ring-buffer volume by emitting fd-based file operations only for tracked fds in eBPF, then consider earlier pseudo-path/data-root/parquet filtering and optional op-class toggles.
Pages updated: `work/fix-unbounded-process-table-growth/implementation_plan.md`; `work/fix-unbounded-process-table-growth/verification.md`; `log.md`.

## [2026-08-24] feature | optimize-fileops-poller created and handed off

Source: full design/engineering analysis of `../wintap` FileOps path (`FileOpsSensor.cs`, both `file_ops_*.bpf.c` tracers, `BaseEbpfSensor.cs` poll loop, `EventChannel.Send`, `ProcessHash`, tracers `Makefile`), extending the 2026-08-24 initial review.
Key findings: non-regular-file fds (sockets/pipes) always miss the fd cache, pay an uncached `/proc` readlink per syscall, and are emitted as `socket:[N]` File rows; Wintap's own I/O is fully processed then discarded; per-event `GenPidHash` is dead (overwritten in `EventChannel.Send`) or wrong (DirectParquetSink); `_fdToPath` never evicts on process exit (leak + PID-reuse misattribution); kernel timestamps are discarded; `file_ops_tracer.bpf.o` is not actually CO-RE despite its name.
Plan: seven `fop-nn` slices, measurement-first (counters/baseline), then userspace dead-work removal, kernel self-PID filter, wakeup batching, CO-RE `S_ISREG`/superblock-magic filtering (gated on a human socket/pipe-row decision), compact fd-op records, fd-cache eviction + kernel timestamps. No-loss constraint enforced by a standing A/B differential test; aggregation explicitly deferred per human direction. Work proceeds on `feature-branch` in both repos.
Pages created: `work/optimize-fileops-poller/{brief,references,design,implementation_plan,dev_handoff,verification}.md`.
Pages updated: `work/fix-unbounded-process-table-growth/implementation_plan.md` (future-todo item spun off); `index.md`; `log.md`.

## [2026-08-24] code | optimize-fileops-poller fop-01/fop-02 code slice

Files changed in `../wintap`: `FileOpsSensor.cs`, `LibBpf.cs`, `file_ops_tracer.bpf.c`, `file_ops_tracepoint.bpf.c`.
Files created in this repo: `validation/fileops-differential/README.md`, `compare_fileops.py`, `fileops_workload.py`.
Implemented: kernel emitted/ring-fail counters by FileOps op class in both tracer variants; userspace consumed/emitted/drop/fallback counters and periodic logs; removed dead per-event FileOps `GenPidHash`; memoized successful `/proc/<pid>/fd` fallback paths; skipped `/proc` fallback for close events; direct scalar decode before string materialization; deterministic file workload and parquet A/B comparator that fails on missing regular-file tuples.
Validation: tracer `make clean && make` passed; `dotnet build wintap/Lintap.csproj` passed with existing warnings and 0 errors; Python harness syntax passed; comparator positive and negative synthetic parquet smoke tests passed.
Limitations: deployed fop-01 counter baseline and live A/B differential remain pending.
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-24] fix | FileOps verifier failure on unlink path

Source: `<local-path>` showed the deployed fop build failed verifier on `t_unlinkat` with `R8 invalid mem access 'inv'`, so FileOps did not load and the low CPU sample was not a valid optimization result.
Files changed: `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`; `../wintap/wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c`; `../wintap/wintap/platform/linux/sensor/ebpf/tracers/Makefile`; `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Fix: split pathname emission into saved-buffer and raw-user-pointer helpers; unlink/unlinkat now use `bpf_probe_read_user_str()` via `emit_file_event_user()`. Completed the compact tagged record format for fd vs path events and moved `file_ops_tracer.bpf.o` into the CO-RE Makefile tier.
Validation: `make clean && make` in the tracer directory passed, including CO-RE `file_ops_tracer.bpf.o`; `dotnet build wintap/Lintap.csproj` passed with existing warnings and `0` errors.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] closeout | [wintap] windows-sensor-health-check feature closed (Feature Velocity 7.0)

Feature complete and Architect-accepted against the re-frozen brief criteria. Units: shc-01 (core engine + five checks + liveness + log flush, 33/33, commit `524ecdb`, audited 2026-08-24), shc-03 (QueryDosDevice drive map + fromNative guard fix, 27/27, commit `26ce94c`, audited 2026-08-25), shc-02 (egress wire-in + MemoryMap bypass Inspect + lifecycle, 5 integration tests, commit `b0528f8`, completed 2026-08-25 — **audit never filed**: Developer worked in an external harness; recorded as missing data per never-gates, durable evidence in verification.md). Whole `Category~shc` suite 65/65 independently re-run by the main session 2026-08-25; full suite 165/165; root solution retains the known MSB4249 issue. Deviation (Architect-permitted): shc-02 tests initially hung on the WintapLogger first-touch sync-context issue; same `Env.SetDataRoot` fixture fix as shc-03 applied.
Availability anchor (Architect-accepted): manual live run on the lab host 2026-08-25 05:39–05:41 local, branch build — recorded verbatim in verification.md; first live demonstration of the frozen criteria (QueryDosDevice map active, egress checks flushing aggregated FAIL lines, no false liveness stalls, low-noise). Lead time: opened 2026-08-24 → available 2026-08-25 = 1 calendar day.
Mini-lab close-out (per [[wiki/decision/ai-velocity-roi-mini-lab]] v2.1): human estimates unsealed — solo 40 h (no solo date given — missing data), AI-workflow date "1 - 2 days" (2026-08-25..26). **Feature Velocity = 40 / (5.714 × 1) = 7.0, uncertainty 3.5–17** (two sealed estimates imply 7.0–8.4, widened ±2×). Q3 verbatim: "Yes" — plain counterfactual, capability not exceeded, comparability `none`, included in the fitted trend (first fully valid dual-sealed point). Calibration: human's AI date hit exactly at its optimistic edge; Engineer's AI date (2026-08-31) 6 days pessimistic; solo spread tight (40 vs 48). Per-unit actual hours missing across all three units; attention proxy omitted (multi-harness, not cheap); API cost missing. Rollup row appended to [[wiki/metrics]].
Findings cataloged: the previously cancelled cataloging dispatch had produced nothing — the consolidated **sweep-feature queue** was created at [[wiki/diagnostic/windows-sensor-sweep-queue]] (12 items): WintapLogger BackgroundWorker sync-context capture (WintapLogger.cs:174-176; Developer's proposed dedicated-thread fix recorded), WintapLogger live-log truncation via FileMode.Create (WintapLogger.cs:166), standing Env.SetDataRoot-before-WintapLogger test-fixture guidance (shc-02/shc-03 fixture pattern cited), the health check's first live catch (PID=-1 ActivityType=Refresh Process event egressing as ProcessName=Unknown — likely WindowsProcessSensor snapshot-refresh artifact), cosmetic `[SensorHealthMonitor..ctor]` caller tag, plus the design.md carry-overs (ungated Registry CreateKey/DeleteKey/DeleteValue emit sites, dead `Serializer.Listen`, WintapAlert self-PID drop, `TranslateTransientPath` WMI authority problem, QueryDosDevice consolidation with WindowsProcessSensor, MemoryMap reroute-through-Send question, `eventtime_invalid` future check).
Pages created: `component/sensor-health-monitor.md` (canonical fold-in of stabilized behavior); `diagnostic/windows-sensor-sweep-queue.md`.
Pages updated: `work/windows-sensor-health-check/verification.md` (shc-03/shc-02 evidence + anchor); `metrics.md` (Results, unsealed estimates, tabulation, closed); `implementation_plan.md` (done checklist closed); `design.md` (close-out banner + sweep-queue cross-link); `component/windows-sensor-service-internals.md` (egress health inspection note); `wiki/metrics.md` (rollup row); `wiki/index.md` (shc feature pages indexed — they had been missed at open — plus the two new pages); `wiki/log.md`.
Open questions: none for this feature. Next: the follow-on Windows sensor sweep feature opens from [[wiki/diagnostic/windows-sensor-sweep-queue]]. Standing owed item from 2026-08-24 remains: ptr feature fold-in has no entries in this log.

## [2026-08-25] feature | WRC opened and planned

Opened `improve-windows-registry-collection`, repaired/completed the registry-provider ADR, recorded retroactive POC spikes wrc-01/wrc-02, and created the WRC plan/references. Initial open inputs: session-handle strategy, final keyword mask, minimal schema shape, and capture-loss canary mechanics. Details: [[wiki/decision/registry-provider-strategy]] and [[wiki/work/improve-windows-registry-collection/implementation_plan]].

## [2026-08-25] decision+instruction | WRC design inputs resolved; build units drafted/approved

Resolved the WRC design gates and instruction sequence: Option A guarded reflection for the TraceEvent session handle, append-only registry schema, final 0x5300/0x5700 keyword mask after probe8, and canary settings. Drafted/approved wrc-03, wrc-04, wrc-05, wrc-06, and wrc-07; wrc-06 became the manifest-only RegistrySensor rewrite with read events intentionally carrying no typed value data and `Registry.PID` left legacy-unset. Details live in the WRC implementation plan and instruction files.

## [2026-08-25] decision+instruction | WRC wrc-08 parquet value plumbing added

Rolled in wrc-08 as a scoped Non-Goals exception before closeout so the new registry value fields reached Parquet output. The unit was drafted and approved with the accepted group-by granularity consequence and `""`/`"NONE"` null defaults. Details: [[wiki/work/improve-windows-registry-collection/implementation_plan]].

## [2026-08-25] verification | WRC live verification recorded before closeout

Recorded the Architect-run wrc-07 live verification in [[wiki/work/improve-windows-registry-collection/verification]] and queued sweep findings for short-lived-process attribution and `stop_without_start` monitoring. Closeout still waited on wrc-08 implementation/audit and final Architect acceptance.

## [2026-08-25] closeout | [wintap] improve-windows-registry-collection feature closed (Feature Velocity 42.0)

Closed the WRC feature and promoted durable state into [[wiki/component/registry-sensor]], [[wiki/work/improve-windows-registry-collection/verification]], [[wiki/work/improve-windows-registry-collection/metrics]], and [[wiki/diagnostic/windows-sensor-sweep-queue]]. Final code reference: `../wintap` commit `1f66a47`; feature suite `Category~wrc` 134/134 and full suite 299/299 were recorded in verification. Metrics: Feature Velocity 42.0, uncertainty 7–84. Open questions: none for WRC; follow-ons remain in the sweep queue.

## [2026-08-25] code | optimize-fileops-poller expanded deployment and diagnostics

Source: continued work on `../wintap` FileOps path plus live RHEL8 validation using `<local-path>` (smoke) and `<local-path>` (overnight).
Files changed in `../wintap`: `FileOpsSensor.cs`, `LibBpf.cs`, `file_ops_tracer.bpf.c`, `file_ops_tracepoint.bpf.c`, `tracers/Makefile`. Files changed in this repo: `extras/lintap-runtime-diagnostics/{collect-lintap-diagnostics.sh,README.md}`, `work/optimize-fileops-poller/{verification,dev_handoff,implementation_plan}.md`, `log.md`.
Implemented and validated in the deployed build: self-PID kernel filter and counters; CO-RE regular-file fd filtering; compact tagged fd vs path records; wakeup batching with `force_wakeup_total`; 16 MiB FileOps ring buffer; kernel pseudo-path filtering and `pseudo_drop_total`; deployed-build fingerprinting and optional `bpftool` capture in the diagnostics bundle.
Results: smoke test proved the new build was live, with FileOps attached, 16 MiB ring buffer visible in `bpftool`, and first-minute `ring_fail_total=0` while `pseudo_drop_total` and `nonregular_drop_total` were already large. Overnight validation showed the same deployed hashes remained installed and that the feature made a substantial practical improvement in observability and early-drop volume reduction, but sustained ring-buffer loss still accumulated under long-running host load (`open`, `read`, `close`, `mmap` still rising materially).
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] feature | optimize-fileops-poller enters phase 2 (deep analysis)

Decision: stay in this feature rather than opening a new one. The original scope
(fop-01..fop-06 substance: counters, dead-work removal, self-PID filter, CO-RE
regular-file filter, kernel pseudo-path filter, compact records, wakeup batching,
16 MiB ring buffer) reached its current deployed state implemented with opencode
gpt-5.5 and gpt-5.4; the feature now continues as a deep-analysis phase.
Evidence constraint: raw runtime diagnostics are no longer readable in this
environment (security); analysis used only wiki-recorded summary statistics plus
read-only `../wintap` source.

Deep analysis (`work/optimize-fileops-poller/deep-analysis-2026-08-25.md`):
sustained overnight ring loss (~778 reserve failures/s across open/read/close/
mmap/write over the 9,121s counter window) is a steady-state userspace consumer
shortfall, not kernel emission or burst behavior. Root cause: the single
FileOps-Poller thread processes each surviving event synchronously through
`EventChannel.Send`, which runs a per-event DuckDB query under the process-global
`_dbLock` (plus a second query on miss) and a synchronous Esper `SendEventBean`,
with no queue between the ring buffer and that work (~12-25ms/lookup from the
2026-08-24 diagnostic implies a ~40-80 events/s ceiling). The 16 MiB ring
(~300k compact records) absorbs the smoke-test minute, then saturates. Ranked
next no-loss slices: fop-08 (bounded in-process queue + in-memory pid→pid_hash
current-process cache) front-runner, fop-09 (hoist per-event config lookups),
fop-10 (top-N per-comm/prefix aggregate counters for path-class attribution),
fop-07 still open; fentry/`bpf_d_path` stays deferred. Next slice selection
pending human sign-off.

Human decision recorded (2026-08-25): non-regular-file fd rows (`socket:[N]`,
`pipe:[N]`, `anon_inode:[N]`, ttys) are permanently dropped from the File
stream, ratifying the deployed CO-RE filter; pipe/anon_inode I/O invisibility
recorded as a fidelity gap (candidate future op class); the BTF-less fallback
tier stays as-is with the tier content difference documented.

Pages created: `work/optimize-fileops-poller/deep-analysis-2026-08-25.md`.
Pages updated: `work/optimize-fileops-poller/{brief,design,implementation_plan,dev_handoff,verification}.md`; `index.md`; `log.md`.

## [2026-08-25] direction | fileops phase-2 strategy discussion recorded

Human direction after reviewing the deep analysis: (1) the userspace workflow
optimizations (fop-08 queue + in-memory cache) are endorsed — memory spend on
queues is acceptable and helps spikes; (2) in-kernel short-interval aggregation
of file events by (pid, op class, identity) is now open for consideration,
amending the 2026-08-24 no-aggregation direction — motivated by suspected high
same-(pid,path) open/openat redundancy and by the fact that Esper aggregates
later in the pipeline anyway; recorded as gated candidate fop-11, with fop-10
extended to measure the open duplicate ratio first; (3) future task saved: an
OSS sensor survey (Falco/Sysdig, Tetragon, Tracee, Elastic ebpf, Sysmon for
Linux, osquery) on how peer projects handle event-volume and ring-drop
pressure.
Pages updated: `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] approval | fileops phase-2 plan approved and handed off

Human approved the full phase-2 plan: sequence fop-08 (+fop-09) → fop-10 →
fop-11 go/no-go. `dev_handoff.md` rewritten as the phase-2 dev handoff: the
copy/paste prompt now targets implementing fop-08 (in-memory pid→pid_hash
current-process cache replacing the per-event DuckDB query under `_dbLock`,
plus a bounded in-process queue between the ring callback and resolve/Esper
with depth/drop counters) and fop-09 (hoist per-event config lookups), with
acceptance criteria tied to the ~778/s ring_fail baseline from the deep
analysis and the standing no-loss differential gate. fop-11 aggregation stays
gated (fop-10 duplicate-ratio evidence + separate human go/no-go + verifier
spike + redefined differential contract). OSS sensor survey remains a parallel
future research task.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `index.md`; `log.md`.

## [2026-08-25] code | fileops phase-2 local fop-08/fop-09 slice

Files changed in `../wintap`: `wintap/core/infrastructure/IProcessResolver.cs`; `wintap/core/infrastructure/ProcessResolver.cs`; `wintap/core/infrastructure/EventChannel.cs`; `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: in-memory active-process cache for File-event pid-hash lookup; bounded FileOps sender queue between the ring callback and resolve/Esper; startup-cached `EventChannel` config/env flags; 60s queue depth/high-water/drop logging and File-event process-cache hit/miss logging; queue capacity knob `WINTAP_FILEOPS_MAX_QUEUE_EVENTS` (default `131072`).
Validation: `make clean && make` for tracers passed; `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.
Open follow-up: rerun the no-loss differential harness, deploy to the RHEL8 field host, capture queue/counter reconciliation, and verify whether overnight `ring_fail_total` growth collapses versus the ~778/s baseline.

## [2026-08-25] test | fileops phase-2 field-host non-root smoke workload session

Environment: deployed field host `private-host`, but without root access from this shell.
Validation change: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` now copies `<local-path>` into the diagnostics bundle when present.
Workload run: repeated deterministic FileOps stimulus using `validation/fileops-differential/fileops_workload.py`, session `<local-path>`, spanning `2026-08-25T16:52:00Z` to `2026-08-25T16:59:22Z`, 5 runs total, each with `--files 24 --rounds 4`, all exiting `0`.
Limitation: the existing parquet validator `devtools/file_capture_smoke_test.py` is not usable as this non-root user on the deployed host because default data-root discovery hits `PermissionError` on `/var/log/lintap`.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | fileops phase-2 deployed bundle shows queue saturation instead of ring saturation

Reviewed root-run diagnostics bundle `<local-path>` after the fop-08/fop-09 deployment. Outcome: `ring_fail_total=0` across all recorded FileOps op classes, `FileOps-Poller` is no longer hot, and `FileOps-Sender` is now the dominant CPU thread; however the new bounded userspace queue reaches capacity (`high_water=131072`) and records substantial per-minute drops (examples: `21567`, `47564`, `78368`, `50144`). The copied `<local-path>` session is present in the bundle and aligns with the recorded workload window. This changes the active loss signal from kernel ring drops to userspace queue drops while confirming that the decoupling moved work off the poller as intended.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] code | fileops queue follow-on pre-enqueue identity stamping

Files changed in `../wintap`: `wintap/core/infrastructure/EventChannel.cs`; `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: File events now try to capture current-process identity from the active-process cache before entering the bounded sender queue, and `EventChannel.Send` skips sender-thread re-resolution for File events that already carry `PidHash` + `ProcessName`. Motivation came directly from bundle `<local-path>`, where sender-thread cache misses rose sharply once queue backlog deepened.
Validation: `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | fileops post-identity-stamping bundle removes queue drops in capture window

Reviewed root-run diagnostics bundle `<local-path>` against prior queue-saturation bundle `<local-path>`. Outcome: `ring_fail_total` remains `0`, and unlike the earlier bundle the bounded userspace queue records `drops=0` throughout the captured window even when depth rises above `100k` (`depth=102547`, `high_water=103187`). File-event process-cache behavior under backlog is materially healthier (for example `hit=54026,miss=4834` at the deepest recorded backlog versus prior collapse cases like `hit=139,miss=8388`). `FileOps-Sender` remains the dominant CPU thread, but the immediate loss mode improved from frequent queue drops to no observed queue drops during this collection.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] code | fileops fop-10 measurement slice

Files changed in `../wintap`: `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: bounded 60s FileOps measurement summaries for top-N emitted process-name buckets, top-N emitted path-prefix buckets, and the same-`(pid,path)` short-window open duplicate ratio. Summary state is bounded and logs coarse path-prefix buckets only, not raw paths.
Validation: tracer `make clean && make` passed; `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Pages updated: `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] review | later pre-fop-10 bundle shows queue drops returned

Reviewed additional same-build bundle `<local-path>` after the more encouraging `<local-path>` snapshot. Outcome: kernel `ring_fail_total` still stayed `0`, but userspace queue saturation returned in multiple intervals, including substantial drop bursts (`30591`, `91570`, `385435`, `448425`, `1960545`). `FileOps-Sender` remained the dominant hot thread while `FileOps-Poller` stayed cold, confirming again that the current failure mode is sender-path/queue loss rather than ring loss. This downgrades the earlier zero-drop bundle from “likely stable” to “good short-window sample” and reinforces the need for `fop-10` attribution data before choosing the next reduction step.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | first deployed fop-10 bundle provides attribution and duplicate-open evidence

Reviewed first deployed `fop-10` diagnostics bundle `<local-path>`. Outcome: the new `measure=[...]` section is present in the `FileOps counters` log and reports top process-name buckets, top path-prefix buckets, and the same-`(pid,path)` short-window open duplicate ratio. The duplicate-open ratio is consistently high across sampled intervals (roughly `52.7%` to `83.7%`, commonly `60-80%`), with dominant surviving emitters including `rpm`, `systemd`, `splunkd`, `git`, `setroubleshoot*`, and dominant prefixes `/lib64`, `/usr`, `(relative)`, `/opt`, `/var` or `/`. Kernel `ring_fail_total` stayed `0`; queue drops were `0` in most sampled intervals but did recur later (`2:07:32 PM` interval: `depth=130909`, `high_water=131072`, `drops=39731`). The smoke-workload session `<local-path>` overlaps the pidstat collector flush schedule (`13:55:02` inside the session window, bounded by `13:50:02` and `14:00:02` writes), giving a practical correlation anchor for future pidstat analysis.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] milestone | fileops fop-11 proposal prepared for designer review

Based on the deployed `fop-10` evidence, the feature reached a new milestone: `fop-11` is no longer just a gated candidate but now has a concrete review-ready proposal. New artifact: `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`, recommending emit-first short-interval aggregation of repeat `open` / `openat` activity only, with bounded kernel state and a revised distinct-tuple-plus-count-conservation differential contract. Related feature pages updated to point at the proposal and to mark the `fop-10` review gate as reached.
Pages created: `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`.
Pages updated: `work/optimize-fileops-poller/brief.md`; `work/optimize-fileops-poller/design.md`; `work/optimize-fileops-poller/implementation_plan.md`; `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/verification.md`; `index.md`; `log.md`.

## [2026-08-25] code | fileops fop-12 absolute-path precondition slice

Files changed in `../wintap`: `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`. Files changed in `Wintap-Analytics`: `validation/fileops-differential/compare_fileops.py`; `work/optimize-fileops-poller/verification.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.
Implemented: pre-enqueue relative/openat `open` path resolution through `/proc/<pid>/fd/<fd>` when possible; logged resolution success/miss counters; Linux path-case preservation instead of unconditional lowercasing; File event time sourced from kernel monotonic timestamps converted to wallclock; comparator aligned to preserve Linux case.
Validation: `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests); `python3 -m py_compile validation/fileops-differential/compare_fileops.py` passed.
Open follow-up: deploy, confirm new resolution counters in the 60s FileOps log, verify relative-prefix collapse in `fop-10` measurement output, and rerun the differential harness on Linux-case-preserving output.

## [2026-08-25] review | first deployed fop-12 bundle shows resolution counters but relative-path bucket still large

Reviewed first deployed `fop-12` diagnostics bundle `<local-path>`. Outcome: the new `resolve=[relative_open_resolved=...,relative_open_resolve_miss=...]` section is present and `ring_fail_total` remains `0`; queue drops also stayed `0` in the sampled window. However, the absolute-path precondition is not yet met: relative-open resolution misses remain high (roughly `8.4k-9.8k` per sampled interval) and `(relative)` remains a top path-prefix bucket (`~8.6k-10.3k` total, mostly opens). The deployment therefore improved observability and preserved performance, but did not yet solve relative/openat identity conflation well enough to call `fop-12` accepted.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] review | post-fd0 short bundle improves resolution counts but relative bucket remains large

Reviewed short post-`fd=0` diagnostics bundle `<local-path>`. Outcome: queue drops stayed `0` and kernel `ring_fail_total` stayed `0`; the `fd=0` fix appears to raise relative-path resolution counts in at least some intervals (for example `relative_open_resolved=10654` with `relative_open_resolve_miss=23424` at `4:18:57 PM`, versus prior examples closer to `1.3k-1.7k` resolves). However, `(relative)` remains a major top-prefix bucket (`~8.3k-23.7k` total in reviewed lines) and miss volume is still too high to accept `fop-12` as complete. This confirms the bug fix was necessary but not sufficient, and points toward a next follow-on that preserves more open-time context such as `dirfd` for fallback absolute-path reconstruction.
Pages updated: `work/optimize-fileops-poller/verification.md`; `log.md`.

## [2026-08-25] code | fileops fop-12 follow-on dirfd and cwd fallback

Files changed in `../wintap`: `wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracer.bpf.c`; `wintap/platform/linux/sensor/ebpf/tracers/file_ops_tracepoint.bpf.c`; `wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`.
Implemented: open/openat path records now carry `dirfd`; relative-path resolution now tries opened-fd first, then `cwd` or `dirfd`-base joins pre-enqueue; reason-split resolution counters were added so the next deployed bundle can show exactly which fallback path is recovering absolute paths and which misses remain.
Validation: tracer `make clean && make` passed; `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter ProcessResolverTests` passed (4 tests).
Open follow-up: deploy and compare `resolved_fd` vs `resolved_dirfd` vs `resolved_cwd`, and verify whether the `(relative)` top-prefix bucket finally shrinks materially.

## [2026-08-25] review | fop-11 proposal designer review completed

Reviewed [[wiki/work/optimize-fileops-poller/fop-11-proposal-2026-08-25]] and
the revised validation/semantic contract. Verdict: approved in principle —
the fop-10 evidence is sound (the duplicate measurement uses the same
(pid, path) key and 1000 ms window the proposal specifies, so the 52.7-83.7%
repeat ratios directly predict the design's win). Two hard conditions:
(1) relative-path opens must be excluded from aggregation (or keyed by
dirfd/cwd) — the (relative) bucket conflates distinct files and would break
the emit-first guarantee; (2) summary-record process identity must be stamped
at first-occurrence, not resolved at flush, to avoid reintroducing the
resolve-after-exit failure fop-08 fixed. One recommended re-scoping: implement
dedup in userspace pre-enqueue first (ring_fail is now 0 everywhere, loss is
queue-side, poller has idle headroom, and the fop-10 measurement dictionary is
the needed structure) — kernel promotion stays available later. Contract
notes: op-scope the revised rule, require drop-free runs for count
conservation, spec the repeat-metadata schema and comparator changes in the
spike. Review recorded in the proposal page §Designer Review.
Pages updated: `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`; `log.md`.

## [2026-08-25] direction | fop-11 human review response: scope expanded, fop-12 added

Human response to the fop-11 designer review: (1) relative-path handling
upgraded from "exclude from aggregation" to "resolve to absolute" — accurate
ground truth is the sensor's purpose; recorded as new precondition slice
fop-12 (recommended: readlink /proc/<pid>/fd/<fd> at open-exit, pre-enqueue);
(2) summary-record identity-at-first-occurrence condition accepted;
(3) aggregation direction formally amended: (pid, path, op)-level aggregation
with grouped totals (bytes etc.) and min/max timestamps over short intervals
is acceptable for ALL op classes (2026-08-24 "no aggregation" non-goal struck
in brief.md; sampling still excluded; emit-first semantics stand) — this also
brings the read/write burst loss mode inside fop-11's reach; (4) the OSS
sensor survey (Tetragon/Tracee/Sysdig et al.) stays deliberately deferred —
"improvements still coming"; natural trigger recorded as post-fop-11/12.
Dev handoff copy/paste prompt retargeted from fop-08/09 (deployed) to
fop-12 → fop-11 with the amended contract (count + byte-total conservation on
drop-free runs).
Pages updated: `work/optimize-fileops-poller/{fop-11-proposal-2026-08-25,brief,implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-25] analysis | fop-12 resolution options + additional win candidates

Source analysis of the relative-path resolution problem, recorded as
suggestions in `work/optimize-fileops-poller/dev_handoff.md` §"fop-12
Resolution Analysis + Additional Win Candidates". Ranked options: R1 readlink
`/proc/<pid>/fd/<fd>` at poller decode pre-enqueue (open-exit already emits
the returned fd; kernel resolves symlinks/dot-segments/dirfd in one call;
count misses, never hide them), R2 cwd/dirfd lexical join as fallback only
(openat_state lacks dirfd today; chdir race; symlink-unsafe `..` collapse),
R3 kernel-side not viable on RHEL8 4.18 (`bpf_d_path` is fentry/LSM-only).
Deeper wins found: A1 `NormalizeFilePath` lowercases paths on a
case-sensitive filesystem (`FileOpsSensor.cs:895`) — accuracy bug conflating
distinct files, fix also removes a per-event allocation; A2 kernel timestamps
still unused, needed for fop-11 min/max accuracy; A3 emit (s_dev, i_ino) —
CO-RE tier already reads `f_inode`, giving collision-free aggregation
identity and fd/PID-reuse validation; A4 mmap is collapsed into Read at
decode, erasing load/execution signal; P3 sampled sender cost-split
measurement to steer post-dedup optimization. A1/A4 and optional
full-canonicalization flagged as stream-content changes needing human
sign-off.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] analysis | Esper-layer findings reframe fop-11; A1-A3/P3 decided

Human decisions recorded: A1 path lowercasing becomes a platform-policy
function (Windows lowercases, Linux preserves case; single extraction point,
expandable); A2 kernel timestamps and A3 (s_dev, i_ino) emission and P3
sender cost-split sampling approved; A4 (distinct Mmap activity type)
explained further, sign-off still pending.

Esper-stream analysis (human-requested): `file.epl` already aggregates File
events into 10s batches grouped by (path, PidHash, PID, activityType,
ProcessName) with count(*)/sum(bytes)/min-max(eventTime), and `default.epl`
excludes File from per-event pass-through — so File telemetry is
aggregate-only on disk today, and fop-11 (sub-batch interval, compositional
accumulators) becomes a pure performance change at the parquet output. New
fop-11 hard conditions: File schema repeat-count field (default 1) +
first/last timestamps; file.epl switches count(*) → sum(count field) and
min/max over the new fields. Also noted: the comparator already measures the
aggregated rows (count conservation = asserting eventCount balance), A2
improves the accuracy of the existing firstSeen/lastSeen columns, and PidHash
stamping quality directly shapes output row grouping.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/fop-11-proposal-2026-08-25.md`; `log.md`.

## [2026-08-25] handoff | A4 decided; phase-2 fop-12/fop-11 dev handoff finalized

A4 (distinct Mmap activity type) approved by human sign-off as its own future
feature enhancement, deliberately deferred — not part of fop-12/fop-11;
recorded in the implementation plan's Phase-2 future tasks with the
downstream/comparator notes. Dev handoff for the next phase finalized: the
copy/paste prompt targets fop-12 (absolute-path ground truth via fd readlink,
pre-enqueue) then fop-11 (short-interval (pid, path, op) aggregation,
emit-first, userspace-first) with the Esper composition rules as hard
conditions (schema repeat-count + first/last timestamps, file.epl
count(*) → sum(count), sub-batch interval), plus approved companions A1
(platform path-case policy), A2 (kernel timestamps), A3 (dev:ino emission),
and P3 (sender cost-split sampling).
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] decision | R1 approved in base form; all fop-12/fop-11 sign-offs closed

Human sign-off: fop-12 implements base R1 only — fd-readlink resolution for
relative/openat paths; absolute-path opens keep their as-requested form. The
full-canonicalization extension (resolving all opens, surfacing symlink
targets) was explicitly declined for now and remains a documented future
option (if ever taken, carry both paths as a schema addition). With A1-A4 and
P3 already decided, no stream-content sign-offs remain open; the dev handoff
prompt is fully unblocked for the fop-12 → fop-11 implementation pass.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] milestone | fileops phase-2 wrap-up recorded; fop-11 stays blocked on path identity

Closed the current phase-2 implementation burst with a milestone wrap-up after
reviewing the deployed `fop-12` follow-ons through bundle
`<local-path>`. Outcome:
queue/ring behavior remains materially better than the pre-phase-2 state,
`fop-10` successfully justified the `fop-11` design direction, and the latest
`dirfd`/`cwd` follow-on proved a real `dirfd` recovery contribution while also
showing that `cwd` is negligible. However, `relative_open_resolve_miss` and the
`(relative)` prefix bucket remain too large to accept `fop-12` as the hard
precondition for `fop-11`. A dedicated milestone page now captures the landed
work, strongest supporting evidence, and the best current fix hypotheses for
the next design pass.
Pages created: `work/optimize-fileops-poller/milestone-2026-08-25-phase2-wrapup.md`.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `work/optimize-fileops-poller/implementation_plan.md`; `work/optimize-fileops-poller/verification.md`; `index.md`; `log.md`.

## [2026-08-25] analysis | fop-12 gap diagnosed; fop-13 fix designed

Reviewed the deployed fop-12 work in `../wintap` (commit "Complete fop-12
path recovery") and the milestone evidence. Diagnosis: the ~8k/min
`relative_open_resolve_miss` floor is structural — all fop-12 fallbacks
(opened-fd readlink, cwd, dirfd readlink) read decode-time `/proc` state
while the dominant relative-open producers (`sed`, `awk`, `sh`, `rpm`
helpers) live milliseconds; `dirfd_lookup_miss ≈ relative_open_resolve_miss`
proves both readlinks die together. Structural root cause in the tracer:
O_DIRECTORY opens are discarded at open-exit (the records that would teach
userspace dirfd→path) and directory-fd closes are dropped by is_regular_fd
(so any dirfd knowledge must be identity-keyed, not (pid,fd)-keyed).
Fix recorded as fop-13 in `work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25.md`:
fop-13a miss-cause counter split (measurement-first), fop-13b kernel-time
identity in one record-format slice — dirfd (s_dev,i_ino) stamping, internal
DIR_OPEN records feeding a global (s_dev,i_ino)→dir-path LRU index, and file
dev:ino emission (approved A3) so fop-11 can aggregate on (pid, dev:ino, op)
independent of path quality. Non-fixes recorded (latency shaving, more cwd,
retro-resolution). fop-11 unblocks on the dev:ino track after fop-13b.
Pages created: `work/optimize-fileops-poller/fop-12-gap-analysis-2026-08-25.md`.
Pages updated: `work/optimize-fileops-poller/{implementation_plan,dev_handoff}.md`; `index.md`; `log.md`.

## [2026-08-25] code | fop-13a/fop-13b implemented locally

Files changed in `../wintap`: `FileOpsSensor.cs`, `file_ops_tracer.bpf.c`,
`file_ops_tracepoint.bpf.c`. Files changed in this repo:
`validation/fileops-differential/{compare_fileops.py,fileops_workload.py}`.
Implemented per the gap analysis: DIR_OPEN internal records (O_DIRECTORY opens
no longer discarded; un-flagged directory opens detected via i_mode), file and
dirfd (s_dev, i_ino) captured in-kernel at event time, a global bounded
dir-identity index in userspace giving a race-free resolution step that works
after producer exit, miss-cause counter split (producer-dead vs alive), new
resolve/dir_open counters in the 60s log, comparator relative→absolute upgrade
matching with an opt-in gate, and a deterministic dirfd-relative workload
scenario. Build-time find: the open-exit handlers hit the BPF stack limit with
the new locals; fixed by removing the 264-byte openat_state stack copy
(read map value directly, delete after emit).
Validation: both tracer tiers build; Lintap builds with 0 errors;
Linux-relevant test classes 10/10 (Windows-specific test failures verified
pre-existing on this host); comparator synthetic scenarios 4/4; workload smoke
run clean. Field deployment, counter baselining vs 20260825T234559Z, and the
A/B differential remain pending (RHEL8 host rebuilds its own .bpf.o — objects
are gitignored).
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-25] maintenance | diagnostics resolve-triage extract + fop-13 handoff refresh

`extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh` now emits
`journal/lintap-file-log-fileops-resolve.txt` — a timestamped extract of just
the `resolve=[...]` counter section so the fop-13 recovery mix, miss-cause
split, and dir-index health are reviewable at a glance (the full counter lines
were already captured; awk extraction verified against a synthetic log line;
`bash -n` passed). `dev_handoff.md` refreshed: fop-13 marked implemented
locally, copy/paste prompt retargeted from "implement fop-13" to "deploy on
the RHEL8 host and run field acceptance," including the rebuild-on-host rule
for the gitignored .bpf.o objects and the acceptance checklist vs the
20260825T234559Z baseline.
Pages updated: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`; `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] review | fop-13 first field run triaged; findings dispositioned

First deployed fop-13 bundle (reviewed by the implementing agent, recorded in
verification.md) confirms the gap-analysis diagnosis: relative_open_resolve_miss
collapsed from the ~7997-8814/min floor to 0-945/min, heavy miss windows are
dominated by miss_producer_dead, the dir index is live and healthy
(dir_open_indexed ~11.6k-19.3k, dir_index_size 1055, evictions 0), (relative)
left the top prefixes, and ring_fail_total stayed 0. Queue drops recurring
under load are the expected sender-ceiling problem — designer position: no
separate follow-on; fop-11 pre-enqueue dedup is the queue-drop fix, sequenced
after fop-13 acceptance (full spaced-smoke bundle + differential rerun).

Code-review findings triaged: F1 (global (s_dev,i_ino) keying aliases across
mount namespaces) accepted → new slice fop-13c, mnt_ns-aware index keying,
not an acceptance blocker; F2 (comparator over-credits relative upgrades,
presence-based matching) accepted → count-conserving matcher in the
test/harness hardening slice; F3 (miss-split best-effort under PID reuse)
accepted as documented limitation, no change; F4 (no automated DIR_OPEN /
recovery-path tests) accepted → same hardening slice (extract dir-index logic
into a testable class).
Pages updated: `work/optimize-fileops-poller/implementation_plan.md`; `log.md`.

## [2026-08-25] closeout | fop-12/fop-13 accepted; fop-11 implementation starts

Human acceptance closes fop-12 and fop-13: the path-identity precondition for
fop-11 is met (evidence summarized in verification.md §fop-13 Closeout). The
4x queue capacity (524288) is validated and will become the code default in
the fop-11 slice; RSS accounting deferred to the upcoming longer execution
cycle via the standing pidstat-collector parquet series; the differential
rerun folds into fop-11's standing A/B gate. fop-11 implementation
(pre-enqueue emit-first aggregation per the approved proposal, with P3
cost-split sampling riding along) begins now.
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-25] code | fop-11 implemented locally

Files changed in `../wintap`: `shared/WintapAPI/WintapMessage.cs` (File schema:
EventCount default 1, FirstSeen/LastSeenEventTime FileTime longs),
`wintap/platform/linux/sensor/ebpf/FileOpsAggregator.cs` (new, dependency-free,
unit-testable), `FileOpsSensor.cs` (absorb hook, summary emitter, flush timer,
shutdown drain, agg=/sender= counters, P3 send sampling, queue default 524288),
`wintap/core/etl/esper/file.epl` (count(*) → sum(file.eventCount); min/max over
the new fields with case-fallback to eventTime — parquet columns unchanged,
Windows senders safe via defaults), `tests/Wintap.Tests/FileOpsAggregatorTests.cs`
(new, 9 tests) + test csproj compile-include (linux sources are excluded from
the Wintap assembly). Files changed in this repo: `compare_fileops.py`
(eventCount-weighted tuple counts — the standing gate is now count-conserving
across pre/post-aggregation streams).
Semantics: emit-first at (pid, path, op), 1000ms window (matching the fop-10
measurement), summaries carry repeats-only counts and first-occurrence
identity, bounded table with counted per-event bypass, kill switch
WINTAP_FILEOPS_AGG_ENABLED=false for same-build A/B.
Validation: Lintap build 0 errors; 19/19 targeted tests (incl. 9 new
aggregator tests: count conservation, emit-first, rollover, cap bypass,
identity-at-first-occurrence); comparator synthetic aggregation scenarios
pass (conserved rc=0, shortfall rc=1). Field deployment and A/B acceptance
pending; dev_handoff retargeted to the fop-11 deploy/acceptance pass.
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-25] maintenance | fop-13 field feedback transcribed; wiki confirmed current

Pre-push audit found the fop-13 deployed-bundle reviews existed only in the
field-side clone's summaries, not in this clone's verification.md. Transcribed
them into verification.md §fop-13 Field Runs (first deployed bundle, same-
instance follow-up with the 6:19:29 PM at-scale proof line, and the 4x
queue-capacity experiment bundles 023152/024019), clearly sourced and
delimited so a field-side merge can prefer richer local copies if present.
index.md footer refreshed to the current feature state. Wiki now carries the
complete fop-12/fop-13 record: gap analysis, implementation, field feedback,
review-finding dispositions, closeout, and the fop-11 local slice.
Pages updated: `work/optimize-fileops-poller/verification.md`; `index.md`; `log.md`.

## [2026-08-25] maintenance | collector carries the full fop-11 acceptance evidence; field-side read-only policy recorded

Human direction: the field-side clone stays read-only (policy) — no commits
from that system; bundle reviews continue arriving as summaries and are
transcribed here. Consequence: the diagnostics bundle must carry everything a
review needs. `collect-lintap-diagnostics.sh` extended accordingly:
timestamped `agg=[...]` and `sender=[...]` triage extracts (fold ratio,
cap_bypass/summary_enqueue_fail health, P3 send_sample_avg_us), an
esper-errors extract (a silently failed file.epl deploy would break File
output while sensor counters look healthy), and
`duckdb/fileops-parquet-sanity.txt` — newest File parquet queried for
rows vs sum(eventCount) (composition proof), aggregated-row count,
firstSeen/lastSeen sanity, and zero-firstSeen rows, with a build-agnostic
fallback query. Validated: bash -n, awk extracts against synthetic log
lines, and the sanity SQL against synthetic parquet (3 rows → 6 raw events,
1 aggregated row). SUMMARY.txt key-files list updated. A rerun of the
collector on the field host now yields the remaining fop-11 acceptance
evidence except the A/B differential (which needs the kill-switch run).
Pages updated: `extras/lintap-runtime-diagnostics/collect-lintap-diagnostics.sh`; `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] ingest | dev/field workflow promoted to canonical wiki page

Human direction: project context recorded in agent memory (~/.claude) must
also live in the wiki — the wiki is the shared knowledge base, agent memory
is a private pointer. Promoted the dev/field process knowledge to
`wiki/workflow/lintap-dev-field-workflow.md`: the validation-host / validation-host split,
the field-side read-only policy and dev-side transcription process, the
self-sufficient-diagnostics principle, pull-only deploys with on-host tracer
rebuilds, push mechanics (dev VM has no credentials; the human pushes), and
the agent-memory mirroring policy itself. The agent memory file now points
at the wiki page as canonical.
Pages created: `workflow/lintap-dev-field-workflow.md`.
Pages updated: `index.md`; `log.md`.

## [2026-08-25] handoff | bundle reviewer prompt added for the fop-11 collector

The field-side reviewer's guidance predated the collector update, so a
dedicated reviewer prompt was added to dev_handoff.md (§Bundle Reviewer
Prompt): maps each new bundle file to its acceptance question with expected
healthy values — agg fold ratio (50-80% expected under load) and health
counters, P3 sender headroom arithmetic, queue deltas vs fop-13-era bundles,
resolve regression bounds, the esper-errors stop-ship rule, and the
parquet-sanity composition proof (raw_events > rows; the eventCount
column-error signature identifies a pre-fop-11 build). Output contract:
transcription-ready summary statistics only, per the read-only field policy.
Pages updated: `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-25] review | fop-11 bundle 041718 triaged; dir-index churn dispositioned as fop-13d

Third fop-11 bundle (same execution) transcribed into verification.md: queue
drops stayed 0, ring 0, aggregation health clean (cap_bypass=0,
summary_enqueue_fail=0, substantial repeats_folded), P3 send_sample_avg_us
captured (~356-2202us). New finding: late-run dir-index saturation — the
index pins at its 16384 cap with 133k-144k evictions/interval and
dir_index_miss ≈ total miss (322-357/min), the signature of a filesystem
walk flooding the FIFO-evicted index and flushing hot base directories.
Designer disposition: a fop-13 structural limit exposed by runtime, not a
fop-11 defect — does NOT block fop-11 acceptance (degraded misses are ~4% of
the pre-fop-13 floor and smoke anchors stay clean); new hardening slice
fop-13d added to the plan (touch-on-hit LRU eviction, cap 16384 → 65536 with
env knob). Remaining fop-11 gates unchanged: kill-switch A/B differential and
a post-collector-update bundle (parquet composition sanity).
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-25] code | fop-13c/fop-13d + F2/F4 hardening implemented locally

Human-directed dev pass implementing all deferred hardening. In `../wintap`:
fop-13c — CO-RE tracer stamps the opener's mount-namespace inum on path
records (+8B; fallback tier zeros) and the dir index keys by
(mnt_ns, s_dev, i_ino), closing the bind-mount/container aliasing risk from
review finding F1; fop-13d — the index is extracted into a dependency-free
DirIdentityIndex class (F4) with touch-on-hit LRU eviction and cap 65536
(WINTAP_FILEOPS_DIR_INDEX_MAX), fixing the scan-flood churn from bundle
041718; DirIdentityIndexTests (7) including LRU hot-entry scan-flood
survival. In this repo: F2 — the comparator's relative→absolute matcher is
count-consuming against the candidate's absolute surplus, longest-suffix
first, with over-credit/count-bound/no-double-dip scenarios verified;
stretch — fileops_workload.py --dir-churn N synthetic filesystem-walk
scenario for field validation of the LRU fix.
Validation: both tracer tiers build; Lintap 0 errors; 26/26 targeted tests;
all comparator scenarios pass; churn workload smoke run clean.
DEPLOY NOTE: record format changed — tracers must be rebuilt on the field
host together with Lintap (mixed deploy misreads mnt_ns). Handoff deploy
steps and reviewer prompt updated (post-13d eviction/miss decorrelation
rule).
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-26] acceptance | fop-13c/fop-13d field-accepted; loss point moves downstream (fop-14 candidate)

Bundle 053404Z transcribed: queue drops 0 throughout, aggregation healthy
with ~50-66% folding, dir index at the new 65,536 cap with heavy eviction
churn AND strong resolution (29,469 resolved vs 354 missed in the burst
minute) — the eviction/miss decorrelation rule is satisfied and fop-13c/13d
are field-accepted. Late-run residual miss pockets (48-49/min, producer-dead
+ cwd) are the known transient-process class, not index pressure.
New finding dispositioned as fop-14 candidate (measurement-first): the ETL
serializer/parquet-writer stage dropped ~63k rows in 3.5 min during the
heavy window against its 10,000-row default caps — the active end-to-end
loss point now sits downstream of the sensor, and dedup cannot shrink it
(Esper output is distinct-group-driven). Owner-resolution warnings noted as
producer-lifetime residual + log-hygiene item. fop-11 still owes the
kill-switch A/B and a parquet-sanity bundle.
Pages updated: `work/optimize-fileops-poller/{verification,implementation_plan}.md`; `log.md`.

## [2026-08-26] maintenance | end-of-day sync audit; wiki confirmed consistent

Pre-handoff audit for tomorrow's pickup: dev_handoff Phase 2 Status now
carries the fop-13c/13d field acceptance and the fop-14 disposition; the
copy/paste prompt's goal is refreshed to the actual remaining work (fop-11's
two formal gates — kill-switch A/B and a parquet-sanity bundle from the
updated collector — plus the human's fop-14 go/no-go); index.md footer and
the actively-edited docs' last_validated dates bumped to 2026-08-26. State
at close: fop-01..fop-13d complete and field-accepted; fop-11 deployed and
healthy pending its two gates; fop-14 candidate awaiting decision; deferred
future tasks unchanged (Mmap activity type, OSS sensor survey).
Pages updated: `work/optimize-fileops-poller/{dev_handoff,verification,implementation_plan}.md`; `index.md`; `log.md`.

## [2026-08-26] code | comparator gains cross-run A/B flags for the fop-11 gate

Pre-A/B gap found: the comparator keyed tuples by (pid, path, op), so two
separate executions (different PIDs, different background activity) could
never compare cleanly. Added --ignore-pid (collapse the pid key) and
--path-prefix (restrict to the deterministic workload's work dir), verified
with a synthetic cross-run scenario (fails without the flags, clean with
them). The fop-11 kill-switch A/B procedure uses both flags with the SAME
work-dir path for both runs so workload paths are identical across runs.
Pages updated: `validation/fileops-differential/compare_fileops.py`; `log.md`.

## [2026-08-26] code | fop-11 A/B fully automated after manual procedure failed

The manual A/B produced a vacuous result (zero workload tuples both sides —
time-window parquet copying raced the serializer flush cadence, and the
first diagnostic ran without root so the permission-restricted data root
globbed empty silently). Fixes, in order: comparator gained --ignore-pid and
--path-prefix (cross-run A/B was structurally impossible with pid-keyed
tuples), then an exit-2 vacuous-pass guard (empty prefix-scoped baseline can
never read as success), and finally the whole procedure was scripted:
validation/fileops-differential/run_fop11_ab.sh runs both phases end to end
— kill-switch env management with cleanup-on-exit, agg-state verification
from the live counter log, restart-as-flush boundaries, row-level harvesting
by non-overlapping firstSeen windows + work-dir prefix, serializer-backlog
invalidation (exit 3), and the count-conserving comparison with a verdict
summary. A --simulate mode with a fixture generator
(simulate_ab_fixture.py) tests the full pipeline off-host; the first
simulation caught a window-overlap bug (ON harvest captured both phases'
rows) — fixed by clamping each phase's window to start after the previous
phase's end. Final simulation: baseline 6 raw rows vs candidate 5 aggregated
rows weighing 6 — missing=0, added=0, PASS, exit 0.
Pages updated: `validation/fileops-differential/{run_fop11_ab.sh,simulate_ab_fixture.py,compare_fileops.py}`; `work/optimize-fileops-poller/dev_handoff.md`; `log.md`.

## [2026-08-26] debug | fop-11 A/B FAIL root-caused to file.epl ungrouped-AgentId n² eventCount inflation

Source: first successful field fop-11 A/B runs on validation-host (results 20260826T232412Z and the relative-harvest rerun), preserved per-phase Lintap.log/counters snapshots, and `../wintap` source review (FileOpsAggregator.cs, FileOpsSensor.cs, EventChannel.cs, FileSerializer.cs, esper/*.epl).
Outcome: the comparator FAIL (baseline 5800 event-weighted tuples vs candidate 1470) is NOT a fop-11 defect. `file.epl` (and `registry.epl`) select `AgentId` without grouping or aggregating it, so Esper classifies the statement as aggregated-but-not-fully-aggregated and emits one output row PER INPUT EVENT, each stamped with the batch-group's `sum(eventCount)` — n events in a group become n rows × n counts. Proof from harvested parquet: 32 hot-loop reads → exactly 32 rows × EventCount=32 = 1024; 33 opens → 1090; the aggregated candidate showed 2 rows × group-sum (67/64). `tcp.epl`/`udp.epl` already group AgentId and are unaffected. fop-11 aggregation itself conserved exactly (summary carried 32/32 folded repeats; `summary_enqueue_fail=0`, `cap_bypass=0`).
Fixed in `../wintap` 0e01783 (feature-branch): AgentId added to both group-bys. Consequence for consumers: all production File/Registry `eventCount` values to date are batch-quadratically inflated (larger groups inflate more), which also likely contributed to fop-10's high duplicate-open ratios read from parquet-derived views (the sensor-side `open_dup` measure is pre-Esper and is a separate open question).
Harness hardening landed en route (Wintap-Analytics feature-branch 9139e01..4060483): serializer-count parse fix; harvest narrowed to the real FileSerializer flush schema (`File_Path` lowercased, `FirstSeen` FileTime) and to serializer flush files + raw_sensor/raw_process_file; upload cycle parked via `WINTAP_ETL_UPLOAD_INTERVAL_SEC` (delete-after-upload and startup `clearRawSensor()` were destroying evidence; Lintap.log is LogType.Overwrite so per-phase log snapshots are now saved into the results dir); `WINTAP_ETL_MAX_QUEUE_EVENTS_FILESERIALIZER=100000` for the run (agg-off flood saturates the 10k drop-newest queue and ate the workload burst); zero-row harvest diagnostics; in-window relative rows passed through to the comparator's relative-upgrade matching.
Open follow-up: rebuild/redeploy the fixed sensor on validation-host and rerun the A/B — expected PASS with off-phase hot reads collapsing to 1 row × EventCount 32 per 10s batch. Known operational hazard: an interrupted run leaves the parked upload-interval line in `<local-path>` and a later run's cleanup "restores" it as pre-existing; verify the line is absent after failed runs.
Pages updated: `log.md`.

## [2026-08-27] review | fop-11 A/B PASS on validation-host with fixed EPLs — count conservation accepted

Source: field run `<local-path>` on validation-host with the `../wintap` 0e01783 EPL fix deployed.
Outcome: VERDICT PASS, exit 0. Baseline 1272 event-weighted regular tuples (down from 5800 under the n² inflation — now matching the workload's actual syscall count), candidate 1292, missing=0, added=20 (candidate-side background surplus, tolerated by design), unmatched_relative=0. ON-phase counters healthy: 24.9k repeats folded, 3.9k summaries, `summary_enqueue_fail=0`, `cap_bypass=0`. OFF rows 687 (one row per group per 10s batch, as intended post-fix) vs 1280 in the inflated runs. fop-11 kill-switch count conservation is accepted.
Harness hardening: leftover env-override lines from interrupted runs are now discarded instead of being "restored" into production (the parked upload interval survived two cleanup cycles on validation-host this way; field host cleaned up manually).
Pages updated: `log.md`.

## [2026-08-27] decision | fop closeout dispositions and byte-conservation gate implemented

Human dispositions toward feature closeout:
- **fop-12: ACCEPTED** (post-fop-13 field evidence: relative_open_resolve_miss 0-6/interval, workload relative opens resolving 36/36 via the dir index, vs the 8-10k floor that blocked acceptance).
- **fop-08 differential debt: discharged** by the fop-11 A/B harness runs (OFF phase exercises the full post-fop-08 pipeline; PASS 20260827T032142Z).
- **fop-14: watch long-term** during longer test deployments rather than a dedicated re-measurement now (prior severity number was taken under the per-event-row EPL inflation and is not trusted).
- **EPL-fix mainlining (../wintap 0e01783): deferred** — no production deployments at present, so no urgency beyond normal branch flow.
- **Historical eventCount inflation: check the "ACME" dataset** before treating it as a practical problem — many changes have landed since the last production deployment, so pre-fix inflated parquet may not exist in any dataset anyone consumes. If ACME's File/Registry data predates the last deployment gap, re-baseline or fence it; otherwise close the concern.

Implemented: byte-total conservation in the comparator (`compare_fileops.py --check-bytes`, wired into `run_fop11_ab.sh`, Wintap-Analytics 67f463d) — per regular tuple, candidate summed BytesRequested must not fall below baseline (deficit fails with samples; surplus mirrors tolerated added counts; warn-and-skip when a bytes column is absent). Simulation passes with bytes verified; deficit and missing-column paths unit-tested. The fop-11 differential contract's three invariants (distinct tuples, count conservation, byte conservation) are now all machine-checked; the next field A/B run verifies them together.
Remaining for fop-11 acceptance: the collector-bundle gate (duckdb/fileops-parquet-sanity.txt), then closeout mechanics (verification/brief/index status flips).
Pages updated: `work/optimize-fileops-poller/{implementation_plan,dev_handoff}.md`; `log.md`.

## [2026-08-27] decision | fop-11 differential contract amended: 1% missing-tuple tolerance for capture noise

Run 20260827T141730Z FAILED with missing=8, added=6 of 1278 baseline event-weighted tuples — while bytes conserved exactly (568320 = 568320) and yesterday's identical run passed with missing=0. Every missing/added entry is a paired open+close single on a distinct `fileops-RR-FFF.dat` round-robin file. Diagnosis: the pre-existing open path-record miss (`open: no_path` ≈14-23/interval in every counters line) drops the open AND orphans its close (the fd→path store never learns the fd), losing ~1% of open/close pairs per phase; which phase eats the flake is a coin flip, so a strict any-missing gate flaps. This is per-event capture noise upstream of aggregation — fop-11 defects lose counts at repeat scale (the EPL bug was -75%), not 0.6%.
Contract amendment: `compare_fileops.py --missing-tolerance <fraction>` (default 0 = strict; `run_fop11_ab.sh` passes 0.01). Missing tuples are still fully reported in result.json; within-tolerance passes print an explicit NOTE. Byte conservation and unmatched-relative gates remain strict. Unit-tested at the observed noise scale (1% pair loss: tol 0 fails, tol 0.01 passes with note); simulation unchanged.
Residual product observation (pre-existing, not fop-11): the open/close pair loss itself — candidate root cause is open-event/path-record correlation; visible as `no_path`+`fallback_miss` on opens. Not queued; noted for any future capture-fidelity work.
Pages updated: `log.md`.

## [2026-08-27] decision | fop feature CLOSED — accepted; closeout test plan published

Human accepted all remaining fop items and closed the feature. Final gates: fop-11 A/B byte-verified PASS on run 20260827T141730Z (counts within the documented 1% tolerance, bytes exactly conserved, relative clean) on top of the strict-zero PASS of 20260827T032142Z. Published [[wiki/work/optimize-fileops-poller/test_plan]] — six critical milestone tests (T1 build+unit smoke, T2 harness simulation self-test, T3 deploy smoke checklist, T4 the kill-switch A/B differential as THE milestone test, T5 collector parquet sanity, T6 fop-14 long-term watch) superseding the per-slice intermediate tests, which remain recorded in verification.md for deep-dives. Brief marked CLOSED; index rows updated.
Carried out of the feature: fop-14 long-term watch; ~1% open+close capture flake (product observation, unqueued); ACME dataset historical-inflation check; ../wintap 0e01783 EPL fix must ride any future deploy.
Pages updated: `work/optimize-fileops-poller/{brief,verification,test_plan}.md`; `wiki/index.md`; `log.md`.

## [2026-08-27] decision | fix-unbounded-process-table-growth CLOSED — accepted; long-run acceptance parallelized; canonical promotion done

Human accepted the current state of the parent feature to unblock the branch PR (Windows developer needs the shared-core changes; no production deployments yet). The dev handoff's long-run evidence gate is superseded: long-running acceptance shifts to the new parallel task [[wiki/work/extended-deployment-monitoring/brief]] — 1-2 week human status checks over multi-host test deployments for ~a few weeks, with short focused patch cycles expected; exit criteria and the carried watch items (fop-14, ~1% capture flake, ACME dataset check) recorded there.
Canonical promotion (deferred by the handoff until closeout) done: [[wiki/component/process-table-retention]] (retention sweep, liveness reconciliation, bounded telemetry, CLONE_THREAD filter, plateau figures, DuckDB lock caveat) and [[wiki/component/fileops-event-pipeline]] (stage contracts kernel→parquet, the Esper group-by rule behind the n² eventCount bug, flush schema, caveats). P1 process-creation pytest re-verified green (5/5) as PR preflight; T2 harness sim green.
Pages updated: `work/fix-unbounded-process-table-growth/{brief,verification}.md`; `work/extended-deployment-monitoring/brief.md` (new); `component/{process-table-retention,fileops-event-pipeline}.md` (new); `wiki/index.md`; `log.md`.

## [2026-08-27] feature-open | selinux-monitoring: SELinux as a first-class Lintap eBPF event domain

Opened via the LLM-assisted feature workflow after a three-round interview.
Core decision:
the auditd/TSV batch path (`../Lintap/sql/selinux.sql`, never-committed
collector, known TZ/join losses) was a crude POC and is superseded as a
non-goal; instead SELinux telemetry becomes first-class Lintap events —
eBPF-captured, flowing in parallel with process/file/network through
tracer → sensor → EventChannel → Esper → serializer → raw_sensor parquet.
Signals split by purpose: AVC denials/grants for policy debugging;
transitions + a novel-tuple-deduped (src ctx, tgt ctx, class, perm)
interaction map for monitoring. Constraints: RHEL 9-class kernel only
(existing host available), ../wintap Linux sensor tree for code, EPL
group-by invariant. Four acceptance criteria frozen (provoked denial vs
ausearch, transition coverage, interaction-map DuckDB query, overhead/
no-loss gate). v1 boundary: raw_sensor parquet — dashboards, Wintappy DBT,
and RHEL 8 deferred. Attach points (selinux_audited tracepoint vs BPF LSM
vs kprobes) delegated to an on-host spike; spike stub created. Sealed human
estimates recorded in interview.md (seal intact for downstream agents).
Pages created: `work/selinux-monitoring/{interview,brief,references,spike}.md`.
Pages updated: `wiki/index.md`; `log.md`.

## [2026-09-17] spike | selinux-monitoring attach-point probe executed on localhost (validation-host)

Ran the spike's census + throwaway probes in an Ubuntu 24.04 / kernel 6.8 /
arm64 local validation environment, separate from the RHEL environment: SELinux compiled
in but inactive (AppArmor is the MAC; getenforce Disabled), so attach
mechanics and formats were fully verified while denial/transition
provocation and true AVC rates remained open for the SELinux-enabled environment. Key findings:
(1) `avc:selinux_audited` tracepoint present with scontext/tcontext/tclass
as strings — no SID resolution needed for the denial/audited-grant stream;
(2) BPF LSM programs load AND attach successfully without `bpf` in the
boot lsm= list but silently never fire (0 hits) — do not build on BPF LSM,
or gate hard on /sys/kernel/security/lsm; (3) fentry/kprobe tiers all
attach: `avc_has_perm(ssid,tsid,tclass,requested,…)` is a one-hook source
for the interaction-map tuple (numeric SIDs — SID→context resolution is now
THE design problem), `avc_audit` is inlined (hook `slow_avc_audit`),
transition candidates `selinux_bprm_committed_creds`/`security_transition_sid`
verified attachable; (4) allow-side rate proxy via generic LSM hooks:
~2.5k/s idle → ~118k/s under fs load — in-kernel dedup mandatory, sizing
keys on tuple cardinality not rate. Recommendation: three-hook hybrid
(tracepoint + avc_has_perm fentry w/ novel-tuple dedup + transition kprobe),
no BPF LSM tier. Spike stays open pending the RHEL 9 re-run (backport
deltas, enforcing-mode tests, real rates). Probes were throwaway in
<local-path>; nothing landed in ../wintap.
Pages updated: `work/selinux-monitoring/spike.md` (results+recommendation,
status stub→draft, confidence low→medium); `wiki/index.md`; `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: RHEL 9 spike collector built

Built a temporary self-contained collector that reruns the spike census and every
probe left open by the localhost run: tracepoint capture in a private
tracefs instance vs ausearch ground truth, provoked denials (runcon
attempts designed to be refused), transition workload under a
security_transition_sid/selinux_bprm_committed_creds probe, attach-mode
tests (kfunc/fentry/kprobe + BTF signatures), and 15s idle/load
avc_has_perm rate + distinct-tuple cardinality windows for dedup-map
sizing. Degrades gracefully without bpftrace (tracefs kprobe_profile hit
counts). Output: one self-sufficient tarball per the field-workflow bundle
rule; cleanup trap removes all tracefs state. Smoke-tested end-to-end on
validation-host (SELinux-inactive degraded mode): all phases run, attach tests
and BTF dumps correct, zero-event paths handled. Next: run in the RHEL
validation environment and retain a minimized, sanitized digest; results
are transcribed into spike.md before design.md opens.
Pages updated: `work/selinux-monitoring/spike.md` (prototype location,
follow-ups); `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: RHEL validation results transcribed; collector v2

Collector v1 ran in the RHEL validation environment (bpftrace absent →
tracefs fallback); a sanitized digest was transcribed into spike.md. The
environment confirmed SELinux enabled/Permissive; CONFIG_LSM includes
bpf AND selinux; selinux_audited tracepoint present with the identical
string-bearing field set as 6.8; all candidate kallsyms present; Tier 1
proven end to end (2 provoked runcon denials captured with full context
strings in the private tracefs instance). Real rates via kprobe_profile:
avc_has_perm ~4.6k/s idle, ~13.1k/s under fs load; security_transition_sid
~40/s; slow_avc_audit 0 baseline (denial stream naturally low-volume).
Recommendation updated: kprobe avc_has_perm as verified interaction-map
baseline (fentry as later optimization); BPF LSM viable on RHEL 9 but kept
out of the critical path with the startup lsm-list gate. Collector v2
built and smoke-tested (forced-fallback mode, clean teardown verified):
fixes the ausearch -ts quoting bug that voided ground truth, adds
no-bpftrace distinct-tuple cardinality + transition tuples via tracefs
hist triggers (Entries: line = dedup-map sizing), adds the bprm-commit
kprobe to fallback rates; make-digest now captures active-LSM/auditd
lines. Remaining before design freeze: one v2 validation rerun
(cardinality + ausearch match); design.md can start now on the answered
attach-point basis.
Pages updated: `work/selinux-monitoring/spike.md`; `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: spike ANSWERED (v2 validation run); design.md drafted

Collector v2 ran in the RHEL validation environment; a sanitized digest
was transcribed into spike.md and the spike is now ANSWERED
(confidence high, status reviewed). v2 closed the gaps: active LSM list
confirmed `capability,yama,selinux,bpf`; ausearch ground truth recovered
(19 AVC records, shape-matches the tracepoint — masks vs decoded perm
names); THE sizing number measured via hist trigger: 421 distinct
(ssid,tsid,tclass) tuples over ~30s (212,960 hits, Dropped 0, top tuple
43%, top-10 ≈89%); rates ~2.4k/s idle, ~11.8k/s load; transitions 15
distinct tuples, bprm ~2/s. The window also captured background AVC
denials (file/tcp_socket/dir classes, permissive=1), validating the
feature's policy-debugging purpose. Drafted
work/selinux-monitoring/design.md: three streams on the verified hooks —
tracepoint AVC events; bprm-commit transition kprobe (osid!=sid filter,
blob-offset startup self-handshake); interaction map on
**avc_has_perm_noaudit** (design correction: it's the single choke point —
avc_has_perm wraps it and inode_permission calls it directly) with 16k
in-kernel LRU emit-first dedup; SID→context resolution as slice-1
prototype-then-fallback (sidtab string cache vs /proc-attr + learned
tables); policy-epoch via SELinux netlink; schema/EPL (group-by
invariant)/serializer shapes; kill switch WINTAP_SELINUX_ENABLED;
counters incl. ring_fail_total=0 gate. Brief Open Questions annotated
with answers.
Pages updated: `work/selinux-monitoring/{spike,brief}.md`;
`work/selinux-monitoring/design.md` (new); `wiki/index.md`; `log.md`.

## [2026-09-17] decision | selinux-monitoring design: five open questions decided (human, one-at-a-time review)

All five design.md open questions decided, each taking the recommended
option: (1) SID→context resolution — timeboxed R1 sidtab string-cache
prototype in slice 1, R2+R3 composite as shipping fallback; (2)
interaction-stream permissions — one row per permission, mask exploded at
ETL to match the acceptance tuple; (3) MessageType names FROZEN now:
SELINUX_AVC / SELINUX_TRANSITION / SELINUX_INTERACTION (parquet subdirs
selinux_avc/transition/interaction); (4) flush policy — 30 s default,
zero-delta tuples skipped; (5) fentry — overhead-gated upgrade only
(kprobe ships; switch only if criterion-4 overhead gate is crowded).
design.md Open Questions converted to a Decisions section; body text
synced. Design is now unblocked for implementation_plan.md +
dev_handoff.md (slice-1 outputs to record back: R1 adopt/reject,
avc_has_perm_noaudit rate/cardinality confirmation, measured overhead).
Pages updated: `work/selinux-monitoring/design.md`; `log.md`.

## [2026-09-17] feature-progress | selinux-monitoring: implementation_plan + dev_handoff published

Published the two remaining pre-implementation artifacts. Implementation
plan declares abbreviation `sel`, five slices evidence-first: sel-01
validation-environment measurements (avc_has_perm_noaudit rate/cardinality via the
spike hist method, timeboxed R1 sidtab-cache prototype with adopt/reject
recorded back into design.md, cred-blob self-handshake) — no production
code; sel-02 tracer + sensor skeleton; sel-03 resolver/dedup-flush/
policy-epoch; sel-04 ETL (frozen SELINUX_* types, row-per-permission
explode, EPL group-by rule); sel-05 the four frozen acceptance criteria
in the validation environment with assets in this repo. Dev handoff authorizes
../wintap changes (platform/linux/sensor/ebpf, core/etl, additive-only
collect/models) + Analytics validation/, carries the copy/paste prompt
(with the interview-seal warning), the spike traps (hook noaudit not the
wrapper; avc_audit inlined; BPF LSM silent-inert; ausearch -ts recent),
field-workflow rules (pull-only deploys, environment-local tracer rebuilds,
and minimized, sanitized evidence digests),
delegated decisions, and closeout/promotion duties. Feature is ready for
the code-development agent; recommended first slice sel-01 (sel-02
permitted first if the validation environment is unavailable).
Pages created: `work/selinux-monitoring/{implementation_plan,dev_handoff}.md`.
Pages updated: `wiki/index.md`; `log.md`.

## [2026-09-18] feature-progress | selinux-monitoring sel-02: tracer + sensor skeleton validated; RHEL 8.10 variance flagged

sel-02 executed in ../wintap (SELinux exploration branch; transcribed from
implementor summaries): selinux_tracer.bpf.c (tracepoint + bprm-commit
kprobe + interaction kprobe preferring avc_has_perm_noaudit with runtime
wrapper fallback, ringbuf/stats/self-PID filter, 16k LRU novel-emit dedup),
SELinuxSensor.cs skeleton (census, load/attach+fallback, decode, heartbeat
+ 60s counters; ETL=sel-04, resolver/flush=sel-03), plus registration,
config keys (WINTAP_ENABLE_SELINUX_SENSOR, WINTAP_API_URLS w/ Program.cs
listen-URL configurability), libbpf_get_error P/Invoke, and a
ProcessRundown disable-override fix. build_ebpf/build_dotnet PASS. In the
validation environment, all three streams captured — 16 AVC events, 20 transitions,
interaction stream folding 2,907,492 checks into 2,748 novel tuples
(~99.9% in-kernel fold, decode_errors=0, map occupancy ≪16k — validates
spike sizing). The environment uses RHEL 8.10 with a 4.18-series kernel,
not RHEL 9-class — a soft contradiction was flagged in brief.md against
the "No RHEL 8 in v1" non-goal; spike environment
labels corrected (data stands; tracepoint is a 4.18 backport; fentry
doubtful). New trap: avc_has_perm_noaudit in kallsyms but perf kprobe
attach EINVAL(-22) on this kernel; wrapper fallback runs with the inode
fast-path coverage caveat. GATE added before sel-03 acceptance: fix the
noaudit attach (tracefs form/legacy opts/offset/fentry attempt) or human
scope decision (wrapper-only 8.10 vs out-of-scope). verification.md
created with the full sel-02 record.
Pages created: `work/selinux-monitoring/verification.md`.
Pages updated: `work/selinux-monitoring/{implementation_plan,design,
dev_handoff,brief,spike}.md`; `wiki/index.md`; `log.md`.

## [2026-09-18] lint | selinux-monitoring: hook-language normalization + sel-02 date provenance

Implementor review flagged an interaction-hook naming drift across the
feature docs (spike.md's recommendation had been reworded to plain
"kprobe on avc_has_perm" when measured rates were inserted, while
design.md/dev_handoff.md kept noaudit-preferred). Normalized all three to
one policy statement: preferred production hook remains
`avc_has_perm_noaudit` where attachable (covers the inode fast path); in
the RHEL 8.10 validation environment it is kallsyms-visible but rejects
perf-event kprobe attach with EINVAL, so sel-02 uses `avc_has_perm` as a
validated fallback with an explicit coverage caveat. Also corrected
sel-02 evidence dates 2026-09-17 → 2026-09-18 to match runtime log
provenance (design decisions keep their true 2026-09-17 date), rephrased
the sel-02 checklist note ("implementation and smoke validation
complete via wrapper fallback; formal checkbox open pending decode unit
tests and noaudit attach resolution"), and recorded two sel-02 details
from the code-alignment review: ringbuf wakeup fix (userspace now
receives novel-tuple events) and attach-error surfacing via
libbpf_get_error. sel-03 gate unchanged.
Pages updated: `work/selinux-monitoring/{spike,design,dev_handoff,
implementation_plan,verification,brief}.md`; `wiki/index.md`; `log.md`.

## [2026-09-18] feature-progress | selinux-monitoring sel-03: core mechanics package-validated

sel-03 partial implementation validated under the packaged service in an
RHEL 8.10 validation environment with a 4.18-series kernel. Results were
transcribed from a minimized, sanitized validation summary.
Green across the new mechanics: class/permission decoder (132 classes /
2,150 perms from selinuxfs, per-event class+perm names in samples), R2/R3
resolver skeleton (hit=2854/miss=1365/learned=27 — live source contexts
resolve via /proc/<pid>/attr/current, targets mostly numeric until
learned), interaction LRU flush (rows=1703, events=259171, zero_delta=770,
iterations=2473, errors=0), policy-epoch via /sys/fs/selinux/policy
polling (delegated netlink-vs-poll choice exercised as polling),
unknown-perm-mask telemetry (counted+top-N, never a drop; fd/sem
concentration flagged as a sel-04 decode-test watch item),
decode_errors=0 throughout; in-kernel dedup at packaged scale 322,851
folded vs 1,301 novel per interval. noaudit EINVAL reproduces identically
under the service — wrapper fallback confirmed in both run modes; sel-03
hook-scope GATE unchanged. Doc changes: verification.md sel-03 section;
plan sel-03 "IN PROGRESS — package-validated"; design confirms
unknown-bits-as-telemetry + R2 validation + polling note + explicit
unresolved-context schema rule for sel-04 (SSid/TSid always present,
SContext/TContext nullable when unresolved); handoff records
packaged-service testing as the preferred validation path and documents
the local test-port override; spike gets the volume-prediction-confirmed
follow-up note.
Remaining before sel-03 closes: EventChannel emission, decode/flush/
resolver unit tests (sel-02 holdover included), hook-scope decision.
Pages updated: `work/selinux-monitoring/{verification,implementation_plan,
design,dev_handoff,spike}.md`; `wiki/index.md`; `log.md`.
## [2026-08-27] feature-work | improve-etl-and-qa started via LLM-assisted feature workflow

Source: source inspection of `../Wintappy/Makefile`, `../Wintappy/notebooks/wintap_dbt_overview.py`, `../Wintappy/wintap_dbt/dbt_project.yml`, pidstat/monitoring/silver model SQL under `../Wintappy/wintap_dbt/models/`, and this repo's legacy Streamlit/DataQA imports under `streamlit/projects/`.
Pages created: `work/improve-etl-and-qa/interview.md`; `work/improve-etl-and-qa/brief.md`; `work/improve-etl-and-qa/references.md`.
Pages updated: `index.md`.
Decisions captured: cross-repo scope with Wintappy as center of gravity; all-event-family ETL/QA cleanup rather than pidstat-only; pidstat promoted to first-class bronze/silver/gold; Wintappy Marimo established as the canonical QA entry point; Analytics-side conflicts to be aligned or retired; stronger end-to-end verification required.
Open questions: compatibility window for existing datasets/consumers; final bronze/silver/gold/monitoring contract per event family; which legacy Analytics QA paths should be updated vs. explicitly deprecated.

## [2026-08-27] feature-work | improve-etl-and-qa: design and staged plan added

Source: source inspection of Wintappy gold models (`process_summary`, `process_file_summary`, `process_net_summary`, `process_uber_summary`), monitoring models, and legacy Analytics-side DataQA code paths.
Pages created: `work/improve-etl-and-qa/design.md`; `work/improve-etl-and-qa/implementation_plan.md`.
Pages updated: `index.md`.
Design direction recorded: separate event-family modeling from QA presentation; make pidstat a first-class family with explicit gold output; normalize the bronze/silver/gold story across process, file, network, and pidstat; treat monitoring as a consumer of intentional family outputs; keep Wintappy Marimo canonical and only align or retire conflicting Analytics-side QA paths.
Implementation staged into seven slices: contract decisions, pidstat family implementation, broader event-family cleanup, monitoring cleanup, Marimo alignment, Analytics-side conflict cleanup, and end-to-end verification/canonical promotion.

## [2026-08-27] feature-work | improve-etl-and-qa: Stage 1 contract decisions recorded

Source: consumer-usage inspection across `../Wintappy/notebooks/wintap_dbt_overview.py`, DBT model refs under `../Wintappy/wintap_dbt/models/`, Wintappy review notes, and this repo's legacy DataQA references.
Pages updated: `work/improve-etl-and-qa/design.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
Decisions recorded: preserve current canonical downstream silver/gold relation names already anchoring Marimo/wiki contracts (`process`, `process_file`, `process_net_conn`, `process_summary`, `process_uber_summary`, `pidstat_metrics`); keep monitoring as a distinct cross-family QA layer; rewrite monitoring to prefer intentional silver/gold inputs over accidental bronze/raw-backed dependencies; do not add broad compatibility aliases for legacy raw-name assumptions; first code slice should center on pidstat gold plus monitoring cleanup and Marimo alignment.
Remaining open questions: exact pidstat gold contract, which legacy Analytics pages merit alignment, and whether any non-pidstat family later justifies a deliberate canonical rename.

## [2026-08-27] feature-work | improve-etl-and-qa: first coding slice defined

Source: detailed inspection of Wintappy monitoring SQL (`build_summary`, `telemetry_event_summary`, `process_chart`, `file_chart`, `network_chart`, `perf_chart`) and the pidstat section of `../Wintappy/notebooks/wintap_dbt_overview.py`.
Pages updated: `work/improve-etl-and-qa/design.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
First-slice contract recorded: add `pidstat_process_summary` as the first pidstat gold model; keep `pidstat_metrics` as silver detail; update monitoring to prefer intentional silver/gold inputs (`process_file`, `process_conn_incr`, `pidstat_metrics`) over raw-backed bronze views where feasible; change the notebook pidstat section to use row-based availability and the new pidstat gold summary. File/network chart rewrites are explicitly first-slice targets using current silver timing fields rather than a larger event-time redesign.
Deferred question narrowed: after the first-slice silver-based chart rewrite, decide whether file/network timeline fidelity is sufficient or whether a later slice needs a chart-specific detail contract.

## [2026-08-27] code | improve-etl-and-qa first coding slice implemented

Files changed: `../Wintappy/wintap_dbt/models/gold/pidstat_process_summary.sql` (new); `../Wintappy/wintap_dbt/models/monitoring/{build_summary,telemetry_event_summary,file_chart,network_chart}.sql`; `../Wintappy/notebooks/wintap_dbt_overview.py`; `../Wintappy/wintap_dbt/models/schema.yml`; `wiki/work/improve-etl-and-qa/{implementation_plan,verification}.md`; `wiki/index.md`; `wiki/log.md`.
Implemented: introduced the first pidstat gold model (`pidstat_process_summary`), moved summary-style monitoring queries off raw-backed runtime dependencies and onto intentional silver/detail inputs where feasible, and aligned the Marimo pidstat section to use row-based availability plus the new pidstat gold summary.
Verification: `make dbt-build` passed (`PASS=78`); `make dbt-test` passed (`PASS=39`); direct built-DuckDB query smoke for `build_summary`, `telemetry_event_summary`, `file_chart`, `network_chart`, `perf_chart`, `pidstat_process_summary`, and the notebook pidstat queries all succeeded without creating the DBT raw-source S3 secret in the direct session.
Known gap: the current configured dataset/window still has zero pidstat parquet rows, so pidstat gold is structurally verified but not yet validated with non-empty live pidstat data; `file_chart` currently uses `process_file.min_event` as the first-slice silver timing basis and may need a later higher-fidelity chart contract.

## [2026-08-28] fix | improve-etl-and-qa mixed-schema eventtime hotfix

Source: dbt failure report for `process_registry` (`Conversion Error: Unimplemented type for cast (TIMESTAMP -> BIGINT) when casting from source column EventTime`) during a Wintappy build.
Files changed: `../Wintappy/wintap_dbt/macros/time.sql`; `../Wintappy/wintap_dbt/models/silver/{host,host_ip,process_file,process_registry,process_image_load}.sql`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added `unix_or_timestamp_expr()` and `win32_or_timestamp_expr()` macros so silver models tolerate either timestamp-typed or numeric `eventtime` inputs without blindly casting to `bigint`; updated the affected silver models to use the new macros.
Verification: targeted `dbt run` for `process_registry` plus related dependents passed after the change, and a full `make dbt-build` re-run passed in `129.86s` with `PASS=78`.
Known gap: no dedicated timestamp-vs-epoch regression fixture/test exists yet; validation is currently by successful DBT execution on the current dataset mix.

## [2026-08-28] fix | Wintappy uv workflow cleanup

Source: local failure report showing `uv add` could not use `../Wintappy/.venv` because the environment directory existed but had no Python executable, plus the deprecated `--isolated` Makefile usage and missing `plotly` dependency for the legacy `qa-pidstat` target.
Files changed: `../Wintappy/Makefile`; `../Wintappy/pyproject.toml`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: removed deprecated `uv run --isolated` usage from the Makefile's DBT runner, added a `rebuild-venv` target for one-step local recovery, and added `plotly` to dev dependencies so the `qa-pidstat` marimo path resolves its import.
Verification: `make rebuild-venv` recreated `.venv`; `uv sync --all-extras --dev` completed successfully; `uv run --dev --project . python -c "import plotly, marimo; print(plotly.__version__)"` passed with `plotly==7.0.0`.
Note: the broken `.venv` was a local environment-state problem rather than a repository-tracked file issue; the repo changes only make the recovery path and dependency behavior saner going forward.

## [2026-08-28] feature | Simple pidstat time-series chart added to Marimo QA

Source: now-available pidstat rows in the current Wintappy DuckDB plus notebook-focused design follow-up.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a first-pass pidstat time-series panel to the canonical Marimo QA notebook with a metric dropdown (`CPU %`, `Memory %`, `Read KB/s`, `Write KB/s`), a minimum peak-CPU filter, a max-series cap, and a 1-minute bucketed line chart over `pidstat_metrics` for the selected top processes from `pidstat_process_summary`.
Verification: the backing query returned `2811` rows across `12` plotted series in `0.46s` on the current dataset with a `25%` peak-CPU threshold, and the updated notebook compiled cleanly via `python -m py_compile notebooks/wintap_dbt_overview.py`.
Known limitation: this is intentionally a simple first cut; richer focusing controls (legend-based hiding, host/container selectors, alternative ranking criteria) are left for a later UX iteration if the chart proves useful.

## [2026-08-28] feature | Pidstat chart UX upgraded from prototype dashboard review

Source: review of `../Lintap/teletap/grokdata_marimo.py` as a prototype reference for stronger layout and interaction patterns.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: kept the canonical Wintappy notebook but borrowed key prototype dashboard ideas for the pidstat panel — moved from Altair to Plotly for the pidstat time-series area, switched ranking/filtering to the selected metric instead of always peak CPU, added a host filter, and enabled a range-slider-based interactive time axis.
Verification: notebook compiled cleanly; an example selected-metric smoke query (`Memory %`, threshold `0.1`) returned `5845` rows across `5` plotted series in `0.35s`.
Remaining gap: the overall Wintappy page layout is still more section-oriented than prototype dashboard's full dashboard composition; only the pidstat panel was upgraded in this pass.

## [2026-08-28] feature | Event-volume correlation chart added to pidstat section

Source: follow-up user request to compare Lintap CPU/resource usage against event volume by type over time.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a second Plotly chart directly below the pidstat process-resource chart, using the same host filter and 1-minute buckets to show normalized event counts over time by type (`process`, `file`, `network`, `registry`, and `image_load` when present).
Verification: the backing query returned `5024` rows in `0.33s` on the current dataset, with active series for `process`, `file`, `network`, and `registry`; notebook compile check remained clean.
Known limitation: this is currently a notebook-level correlation view built directly from normalized tables rather than a dedicated DBT monitoring model, and cross-family "event count" semantics remain pragmatic rather than formally unified.

## [2026-08-28] feature | Pidstat command aggregation mode added

Source: follow-up exploration request using `setroubleshootd` as the motivating repeated-instance process family.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a pidstat `Aggregation` control with `Per process` and `By command` modes. `By command` ranks series by the selected metric, aggregates matching process instances into one family series, and includes concurrent PID counts in hover data.
Verification: a targeted `setroubleshootd` smoke query returned `380` rows in `0.27s`, collapsed to one visible command-level series with `concurrent_pids` preserved per bucket. This matched the exploratory finding that `setroubleshootd` instances are largely serial repeats rather than long-lived overlapping processes.
Open follow-up: decide whether command aggregation should later offer alternate rollup semantics such as `sum`, `average per instance`, or `max instance`.

## [2026-08-28] feature | Pidstat controls and chart comparability polished

Source: follow-up UX request for clearer aggregate controls and a more comparable event-volume display.
Files changed: `../Wintappy/notebooks/wintap_dbt_overview.py`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: renamed aggregation options to `Per process instance` and `Aggregate by command`, added a `Command contains` filter for narrowing repeated-instance families like `setroubleshootd`, and enabled a bottom-axis range slider on the event-volume subplot stack so its interaction style more closely matches the pidstat chart above.
Verification: command-filtered aggregate smoke query for `setroubleshootd` returned the expected single family series (`380` rows in `0.27s`); notebook compile check remained clean.
Known limitation: the pidstat and event-volume plots still do not share truly linked zoom because they remain separate Plotly figures.

## [2026-08-28] milestone | improve-etl-and-qa interim checkpoint written

Pages created: `work/improve-etl-and-qa/milestone-2026-08-28.md`.
Pages updated: `index.md`; `log.md`.
Summary: captured the current interim state after the first major wave of code work: pidstat gold landed, the canonical Wintappy QA notebook now supports interactive pidstat exploration plus event-volume correlation, mixed-schema eventtime handling is hardened, uv workflow cleanup is recorded, and the explicit next-slice decisions (monitoring promotion, linked zoom, broader event-family cleanup, Analytics-side conflict pass) are listed in one place.

## [2026-08-28] plan | Lintap stair-step memory-growth instrumentation

Source: analysis of the current run's pidstat and event-volume data for the long-lived `Lintap` process on `validation-host`.
Pages created: `work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md`.
Pages updated: `work/improve-etl-and-qa/implementation_plan.md`; `index.md`; `log.md`.
Summary: current evidence points to burst-correlated memory ratcheting, likely file-pipeline-driven, but pidstat alone cannot distinguish true retained state from allocator/runtime retention. The plan therefore layers `/proc/<pid>/smaps_rollup`, .NET runtime counters, and periodic internal file-pipeline/serializer backlog counters on top of the existing pidstat/event-volume view, with sampling cadences and a prioritized rollout order recorded in the new artifact.

## [2026-08-28] update | Lintap instrumentation plan refined for manual-batch-first execution

Source: follow-up planning request focusing on immediate impact versus eventual long-term sidecar collection.
Pages updated: `work/improve-etl-and-qa/instrumentation-plan-lintap-memory-growth.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
Summary: refined the plan to distinguish two operating modes: (A) manual batch capture now, recommended first for speed and overhead validation; (B) long-term sidecar collection later, using the same raw-style parquet layout. Added concrete proposed event types (`perf_smaps_rollup`, `perf_dotnet_counters`, `perf_lintap_diag`, `perf_fd_map`) and updated Stage 8 to make manual-batch-first the default implementation path.

## [2026-08-28] code | Manual-batch performance collectors added under validation/

Source: implementation follow-through on the memory-growth instrumentation plan's immediate-impact path.
Files created: `validation/perf-collection/pyproject.toml`; `validation/perf-collection/README.md`; `validation/perf-collection/src/wintap_perf_collection/{__init__.py,procfs.py,parquet.py}`; `validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py`; `validation/perf-collection/scripts/run_lintap_perf_batch.sh`; `validation/perf-collection/tests/{test_procfs.py,test_manual_batch.py}`.
Pages updated: `work/improve-etl-and-qa/{implementation_plan,verification}.md`; `log.md`.
Implemented: a standalone manual-batch collection package that samples `/proc/<pid>/smaps_rollup`, `/proc/<pid>/status`, and `/proc/<pid>/{fd,maps}` for a target process and writes partitioned parquet event types (`perf_smaps_rollup`, `perf_proc_status`, `perf_fd_map`) into canonical `raw_sensor/<event_type>/dayPK=/hourPK=` layout. Optional external stdout line capture is supported for provisional `perf_dotnet_counters_raw` and `perf_lintap_diag_raw` event streams so command shape can be iterated before long-term promotion.
Verification: `cd validation/perf-collection && uv run --project . --extra dev pytest` passed (`4 passed`), including an end-to-end fake-procfs test that writes real parquet outputs.
Known gap: not yet exercised against a live Linux `Lintap` process from this repo; external-command capture is structurally implemented but not yet validated with real `dotnet-counters` or future Lintap diagnostic output.

## [2026-08-29] handoff | Host-ready Lintap memory experiment continuation

Pages created: `work/improve-etl-and-qa/dev_handoff.md`.
Pages updated: `index.md`; `log.md`.
Summary: recorded a host-oriented continuation handoff for the live Lintap experiment. It points the next session at the perf-collection package, the current QA notebook, and the new instrumentation plan; captures the real-run parquet row counts already observed on-host; and explicitly elevates embedded DuckDB inside the long-running .NET process as a major memory-growth suspect alongside file-pipeline and runtime/allocator hypotheses.

## [2026-08-29] code | Live-host perf collector tightening on validation-host

Source: direct inspection of `<local-path>` parquet plus follow-up validation commands on the live `validation-host` host against PID `743557` (`<local-path>`).
Files changed: `validation/perf-collection/src/wintap_perf_collection/{procfs.py,cli/manual_batch.py}`; `validation/perf-collection/tests/{test_procfs.py,test_manual_batch.py}`; `validation/perf-collection/README.md`; `wiki/work/improve-etl-and-qa/{implementation_plan.md,verification.md}`; `wiki/log.md`.
Implemented: tightened `smaps_rollup` parsing so the address-range header line no longer becomes a bogus parquet column, and added structured `perf_dotnet_counters` row derivation from captured `dotnet-counters monitor` console output while retaining `perf_dotnet_counters_raw`.
Verification: `cd validation/perf-collection && uv run --project . --extra dev pytest` passed (`6 passed`). Existing on-host raw `dotnet-counters` parquet (`478` lines) now parses into `26` structured counter rows. Existing root-run `smaps`/`status` parquet still points toward anonymous/private memory (`RssAnon 2060344..2112368 kB`, flat `RssFile 169448 kB`, flat `AnonHugePages 1177600 kB`) with stable FD/map counts (`open_fd_count 485..487`, `mapped_regions 4776..4787`).
Permission note: as the current unprivileged user on `validation-host`, fresh live collection against the root-owned `Lintap` service can read `/proc/<pid>/status` but not `/proc/<pid>/smaps_rollup`, `/proc/<pid>/fd`, or the .NET diagnostics socket. End-to-end live verification of the fixed `smaps` path and a new `dotnet-counters` capture therefore remains blocked pending a host permission change.

## [2026-08-29] code | Focused root-wrapper added for live validation-host captures

Source: follow-up implementation request after the `validation-host` permission check showed that the active `Lintap` service is root-owned and blocks fresh unprivileged `smaps`, `fd`, and .NET diagnostics access.
Files changed: `validation/perf-collection/scripts/capture_lintap_perf_for_user.sh`; `validation/perf-collection/README.md`; `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Implemented: added a tactical root-side wrapper that self-escalates via `sudo`, resolves the live `Lintap` PID as `root`, runs `wpc-perf-batch` against that PID, auto-enables `dotnet-counters monitor ...` when available, and `chown`s the output tree back to the invoking user so the resulting parquet is immediately usable without wider host permission changes.
Verification: `cd validation/perf-collection && bash -n scripts/capture_lintap_perf_for_user.sh` passed.

## [2026-08-29] test | Fresh root-wrapper capture validated on validation-host

Source: operator-ran `validation/perf-collection/scripts/capture_lintap_perf_for_user.sh` against the live root-owned `Lintap` service on `validation-host`, producing run `perf-1788028744` under `<local-path>`.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: fresh readable user-owned parquet landed for `perf_smaps_rollup`, `perf_proc_status`, `perf_fd_map`, `perf_dotnet_counters_raw`, and structured `perf_dotnet_counters`. The fixed `smaps_rollup` parser worked on live host data with no bogus header-derived column. Current memory remains mostly anonymous/private (`VmRSS 2405416..2452760 kB`, `RssAnon 2125524..2172868 kB`, flat `RssFile 169448 kB`, `Anonymous 2130236..2176124 kB`, `AnonHugePages 1208320..1292288 kB`) while FD/map counts stayed relatively stable (`open_fd_count 485..487`, `mapped_regions 4770..4791`). Structured runtime counters also landed successfully (`34` parsed rows across `26` counters), including `working_set_mb`, `gc_heap_size_mb`, `gc_committed_bytes_mb`, `cpu_usage`, and `allocation_rate_b_5_sec`.

## [2026-08-29] test | One-hour idle baseline on validation-host

Source: operator-ran `capture_lintap_perf_for_user.sh` with run id `lintap-perf-60m` while the host was mostly idle.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: the one-hour procfs baseline completed with `714` rows each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`, covering `2026-08-29T19:01:21Z -> 2026-08-29T20:01:17Z`. RSS and anonymous memory fluctuated within roughly an 80-90 MB band but ended lower than they started (`smaps.Rss 2421536 -> 2389236 kB`, `status.VmRSS 2419140 -> 2386360 kB`, `Anonymous 2141500 -> 2109196 kB`, `RssAnon 2139248 -> 2106472 kB`), while FD/map counts remained broadly stable (`open_fd_count 486..494`, `mapped_regions 4765..4838`). This is useful negative evidence: on an idle host, the current `Lintap` instance did not keep ratcheting upward over an hour.
Runtime-counter caveat: the raw `perf_dotnet_counters_raw` stream spans the full hour (`478` rows through `2026-08-29T20:01:22Z`), but the structured `perf_dotnet_counters` derivation only captured an initial burst (`44` parsed rows) because later `dotnet-counters monitor` screen-refresh output collapses multiple updates into ANSI-heavy composite lines. That points the next runtime-counter improvement toward `dotnet-counters collect --format json|csv` or a richer ANSI-aware parser.

## [2026-08-29] code | dotnet-counters path moved to collect/json-csv

Source: follow-up implementation request after the hour-long idle baseline showed that the old `dotnet-counters monitor` screen-scrape path was too lossy for durable long-run structured parsing.
Files changed: `validation/perf-collection/src/wintap_perf_collection/cli/manual_batch.py`; `validation/perf-collection/scripts/{capture_lintap_perf_for_user.sh,run_lintap_perf_batch.sh}`; `validation/perf-collection/tests/test_manual_batch.py`; `validation/perf-collection/README.md`; `wiki/work/improve-etl-and-qa/{dev_handoff.md,verification.md}`; `wiki/log.md`.
Implemented: removed the old monitor/raw `.NET` path, added direct parsing for `dotnet-counters collect --format json|csv`, and switched the root wrapper to auto-enable file-based `collect` output by default. The only remaining raw external-command capture in this package is the future-facing `perf_lintap_diag_raw` path.
Verification: `cd validation/perf-collection && uv run --project . --extra dev pytest` passed (`8 passed`), covering JSON parsing, CSV parsing, and a fake-collector end-to-end parquet write. Also verified the real export schema locally by collecting both JSON and CSV from a temporary sample .NET process under `<local-path>`.
Host note: an assistant-run live smoke of the new root wrapper could not complete from this noninteractive session because `sudo` on `validation-host` requires a terminal/password prompt. A user-run rerun on-host is still needed to replace the older monitor-derived `perf_dotnet_counters` host artifacts with new collect-based ones.

## [2026-08-29] test | collect-based dotnet-counters host smoke validated on validation-host

Source: operator-ran `capture_lintap_perf_for_user.sh` with `RUN_ID=lintap-perf-collect-smoke`, `DOTNET_COUNTERS_FORMAT=json`, and `WINTAP_DATA_ROOT=<local-path>` against the live root-owned `Lintap` service.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: the new collect-based `.NET` path worked end to end on the real host. `perf_dotnet_counters` landed as structured parquet with `108` rows across `27` distinct counter keys over `2026-08-29T20:36:46Z -> 2026-08-29T20:37:00Z`, including stable provider/name/type/tag/value fields and counters such as working set, GC heap size, GC committed bytes, allocation rate, CPU usage, exception count, threadpool metrics, and per-generation sizes/counts. Matching procfs smoke rows also landed (`4` each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`). This replaces the old monitor-derived host validation as the preferred runtime-counter capture path.

## [2026-08-29] test | collect-based one-hour rerun on validation-host

Source: operator-ran a second `lintap-perf-60m` host capture after the collector switched to `dotnet-counters collect`, producing fresh `hourPK=21` parquet under `<local-path>`.
Files changed: `wiki/work/improve-etl-and-qa/verification.md`; `wiki/log.md`.
Results: the collect-based long run produced `9720` structured `perf_dotnet_counters` rows across `27` counter keys for `2026-08-29T20:41:27Z -> 2026-08-29T21:41:16Z`, plus `714` matching rows each for `perf_smaps_rollup`, `perf_proc_status`, and `perf_fd_map`. Memory again stayed within a bounded band rather than showing obvious monotonic runaway (`smaps.Rss 2389332 -> 2420164 kB`, range `2313792..2433876`; `VmRSS 2387040 -> 2416260 kB`, range `2308556..2428896`; `Anonymous 2109032 -> 2140112 kB`, range `2033484..2153568`). FD/map counts also stayed broadly stable (`open_fd_count 485..488`, `mapped_regions 4756..4866`). The new `.NET` telemetry spans the full hour cleanly, with examples including `working_set_mb 2384.67 -> 2471.87`, `gc_heap_size_mb 541.85 -> 659.10`, `gc_committed_bytes_mb 1252.23 -> 1254.89`, and `cpu_usage 12.06..23.06`.
Operator note: this rerun reused the historical `run_id` value `lintap-perf-60m`, which caused naive cross-partition queries to blend the earlier monitor-era run with the new collect-based rerun. Future comparison runs should use distinct `RUN_ID`s.

## [2026-08-29] review | Lintap long-run CPU readiness

Sources read: current committed `../wintap` Lintap paths for serializer, FileOps aggregation/cache, cache/upload, EventChannel, and process retention; current `validation/perf-collection` collectors; and the `validation-host` one-hour verification record.
Pages created: `work/improve-etl-and-qa/cpu-growth-review-2026-08-29.md`.
Pages updated: `work/improve-etl-and-qa/dev_handoff.md`; `index.md`; `log.md`.
Findings: the current roughly 19% idle-host CPU result is a baseline, not a growth trend. Review identified queue/flush work, unmatched FileOps FD-path state, aggregation sweeps, cache/upload cycles, and process-retention maintenance as concrete CPU or joint CPU/memory candidates. Next work is measurement-first: long baseline, per-thread/stack attribution, cadence correlation, and low-overhead queue/cache/cycle diagnostics, all gated by zero-drop and count/byte-conservation evidence.

## [2026-08-29] code | Lintap CPU observability and serializer safety first slice

Branch: `../wintap` `feature-branch` from current `develop` after `git fetch --all --prune`.
Files changed: `../wintap/wintap/core/etl/extract/Serializer.cs`; `../wintap/wintap/platform/linux/sensor/ebpf/{FileOpsAggregator,FileOpsSensor}.cs`; `../wintap/wintap/core/etl/load/CacheManager.cs`; `../wintap/wintap/core/infrastructure/ProcessResolver.cs`; `../wintap/tests/Wintap.Tests/FileOpsAggregatorTests.cs`; feature verification/plan/handoff records.
Implemented: serializer flushes cannot overlap, emit drain/duration/remaining-queue/Parquet-backlog diagnostics, and group message types in a single pass. FileOps now reports FD-cache cardinality and aggregation flush timing. Cache/upload and process-retention cycles report elapsed time and bounded-state context. No sensor filters, aggregation semantics, queue limits, or drop policies changed.
Verification: `dotnet build wintap/Lintap.csproj` passed with 0 errors; `dotnet test tests/Wintap.Tests/Wintap.Tests.csproj --filter "FullyQualifiedName~FileOpsAggregatorTests"` passed (10/10). The unfiltered Wintap test project remains Linux-incompatible because pre-existing Windows SID/ETW tests fail and the test host aborts during ETW cleanup.

## [2026-08-30] test | First CPU-observability one-hour Lintap capture

Source: `<local-path>` and `/var/log/lintap/runtime/Logs/Lintap.log` on `validation-host`, targeting Lintap PID `2400026`.
Results: CPU averaged `11.42%`; the first and second halves averaged `11.39%` and `11.44%`, so no within-hour CPU ratchet was observed. This was startup-adjacent, with service start eight minutes before sampling. The critical result is fidelity failure: `fileserializer` reached its active 10,000-event cap continuously and had dropped at least `394529` file events by 17:25 PDT. Its flushes took `2..19 ms` with no overlap, FileOps sender drops were zero, and aggregation cap bypass was zero, isolating the immediate problem to serializer admission/batch cadence. FD-cache metrics rose from `20` PID maps / `24` entries to `1439` / `1784`, confirming the long-run cache-growth risk. Cache-cycle and resolver-maintenance timing are recorded in the verification artifact.

## [2026-08-30] review | FileOps aggregation regression check

Sources read: last-week FileOps/fop history in `../wintap`, current eBPF-to-Esper-to-serializer path, deployed `<local-path>`, `<local-path>`, and deployed BPF-object hashes.
Result: no evidence that the recent fop aggregation work regressed or that aggregation is bypassed. The deployed EPL and FileOps BPF object exactly match current source; the EPL contains the `AgentId` grouping fix for the historical n-squared inflation bug. Positive `repeats_folded` and zero `cap_bypass` show aggregation is active. Its emit-first, `(pid,path,operation)`-keyed, one-second design intentionally does not reduce high-cardinality unique file activity, so it cannot prevent the demonstrated downstream 10,000-event serializer-cap loss by itself. The cap and drop policy predate the last-week fop work.

## [2026-08-30] code | FileSerializer no-drop cadence

Prediction recorded before implementation: a five-second FileSerializer-only flush cadence should keep observed post-aggregation file volume below the existing 10,000-event cap, eliminating serializer-drop warnings without changing FileOps count/byte semantics or other serializers' 60-second cadence.
Branch: `../wintap` `feature-branch`.
Implemented: added `FileSerializationIntervalSec` (default `5`) to ETL configuration and used a unit-tested serializer schedule resolver so only `fileserializer` overrides the general interval. Older ETL configs that omit the field default to five seconds. Extended `devtools/file_capture_smoke_test.py` with a post-start FileSerializer-drop log gate and configurable observation window.
Verification: focused `FileOpsAggregatorTests` plus `SerializerScheduleTests` passed (`14/14`); `dotnet build wintap/Lintap.csproj` passed with 0 errors; `python3 -m py_compile devtools/file_capture_smoke_test.py` passed. Host validation remains required after redeploy.

## [2026-08-30] test | FileSerializer five-second redeploy result

Result: deployment logged `fileserializer: serializer flush interval=5s`, and the bounded no-drop smoke passed. The strict prediction did not hold across early live bursts: the log shows cap hits at `18:59:52` (`dropped=1`) and `19:03:12` (`dropped=434`). Five seconds materially reduced loss from the prior run but did not eliminate it. Next slice: schedule a single non-overlapping immediate FileSerializer drain below the 10,000-event cap, retaining the periodic cadence as a backstop; validate it with a controlled high-volume no-drop test before another long capture.

## [2026-08-30] code | FileSerializer high-water burst drain

Prediction recorded before implementation: one immediate non-overlapping drain at a 5,000-event FileSerializer high-water mark leaves 5,000 events of burst headroom below the existing cap, eliminating serializer drops without changing event semantics or idle batching.
Branch: `../wintap` `feature-branch`.
Implemented: added `FileSerializationHighWaterEvents` default `5000`; FileSerializer schedules one worker at threshold, waits behind an active drain if needed, and rechecks state after completion. High-water drains log `trigger=high_water`. The file smoke test now supports `--unique-file-count` for a high-cardinality burst and avoids per-file fsync for that stress mode.
Verification: focused `FileOpsAggregatorTests` plus `SerializerScheduleTests` passed (`18/18`); `dotnet build wintap/Lintap.csproj` passed with 0 errors; `python3 -m py_compile devtools/file_capture_smoke_test.py` passed. Host stress validation remains required after redeploy.

## [2026-08-30] test | FileSerializer high-water stress gate passed

Source: live `validation-host` `/var/log/lintap/runtime/Logs/Lintap.log` after the high-water redeploy and controlled `--unique-file-count 6000` smoke.
Result: the log recorded the 5,000-event threshold, 18 high-water requests, and corresponding `trigger=high_water` drains of about 5,000 rows. Drains were normally `2..16 ms` with one `86 ms` outlier, had `skipped_overlap=0`, and left only `2..542` rows queued. No new FileSerializer backlog-cap warning appeared after the smoke marker. The controlled no-drop burst prediction passed; next acceptance gate is a warmed-up unique-run-ID one-hour capture with concurrent log review.

## [2026-08-30] review | Lintap eBPF path, diagnostics, and validation audit

Sources read: `../wintap` Linux subscription, eBPF base/sensor/tracer, EventChannel, Esper, devtools, and tests; Analytics performance-collector CLI and both wrappers.
Pages created: `work/improve-etl-and-qa/ebpf-path-audit-2026-08-30.md`.
Pages updated: `index.md`; `log.md`.
Findings: sensor overlap is mostly intentional layered coverage. Concrete cleanup candidates are mismatched documented sensor toggle names, fallback capability visibility, Network extra-attach cleanup, invalid EventChannel rate accounting, bounded FileOps FD-cache cleanup, ambiguous generic BPF map polling, fidelity snapshots in perf capture, stale OpenAt source, and wrapper PID/ownership/counter inconsistencies. The work note also seeds the later developer, architect, and reviewer documentation set.

## [2026-08-30] analysis | Tenable scan storm overwhelms FileOps sender

Source: `lintap-perf-20260830` parquet plus `/var/log/lintap/runtime/Logs/Lintap.log` during the matching hour.
Pages created: `work/improve-etl-and-qa/tenable-scan-storm-response-2026-08-30.md`.
Pages updated: `index.md`; `log.md`.
Results: FileSerializer remained free of backlog warnings, but FileOps sender depth climbed from about 419k to the 524288 cap and then dropped events continuously. Aggregation cap bypass and summary-enqueue failures appeared at saturation. The storm therefore bottlenecks synchronous FileOps sender/EventChannel/Esper work upstream of serialization. Recommended future slice: an opt-in generic kernel exact-`comm` deny policy with per-rule/per-operation pre-ring suppression counters, preceded by local evidence identifying actual worker names; do not hard-code a Tenable name or infer scanner process-tree membership.

## [2026-08-30] code | Generic kernel FileOps deny policy

Prediction: an empty list changes no behavior; each configured exact raw Linux `comm` policy hit is counted by rule and operation before ring reservation, so it removes selected activity from all downstream capacity domains without claiming to count all vendor filesystem activity.
Branch: `../wintap` `feature-branch`.
Implemented: added empty-by-default `FileOpsDenyComms` / `WINTAP_FILEOPS_DENY_COMMS`, a bounded exact-name parser, CO-RE and tracepoint fallback BPF deny maps and policy-stat maps, post-load map installation with fail-closed startup for a configured-but-uninstallable policy, and periodic policy counter deltas in FileOps logs. Rules are exact/case-sensitive, max 15 UTF-8 names, each max 15 bytes.
Verification: both FileOps BPF tiers compiled through `make build_ebpf`; `dotnet build wintap/Lintap.csproj` passed with 0 errors; focused aggregation/policy/schedule tests passed (`22/22`). No live rule test ran because scanner-exclusive worker names have not yet been established.

## [2026-08-30] evidence | First scanner deny-rule candidate identified

Source: live `validation-host` process tree during the active weekly scan.
Result: `nessus-agent-module` runs multiple `tenable-utils-LINUX-x86_64.bin find / ...` workers. Their exact Linux `comm` is `tenable-utils-L` (15 bytes), making it the first defensible policy candidate. Generic helpers (`find`, `rpm`, `sed`, `sh`) remain out of scope. The controlled first rollout is `WINTAP_FILEOPS_DENY_COMMS=tenable-utils-L` with a 10-minute in-scan fidelity check.

## [2026-08-30] test | Tenable worker kernel policy live gate passed

Source: active `validation-host` weekly scan and `/var/log/lintap/runtime/Logs/Lintap.log` FileOps summaries.
Result: `WINTAP_FILEOPS_DENY_COMMS=tenable-utils-L` suppressed `dir_open=114102` then `117327` attempts in consecutive 60-second windows. Sender depth was `853` then `192`, with zero sender drops, aggregation cap bypass, and summary enqueue failures. This contrasts with the prior scan's sustained 524288-entry queue saturation. The policy's pre-ring accounting and containment contract is validated for the observed Tenable utility workers.

## [2026-08-30] code | Normalize pidstat CPU naming and documentation

Sources changed: `../Lintap/pidstat-collector.py`; `../Lintap/README.md`; `../Wintappy/wintap_dbt/models/{silver/pidstat_metrics,gold/pidstat_process_summary}.sql`; `../Wintappy/notebooks/wintap_dbt_overview.py`; `../Wintappy/wintap_dbt/README.md`.
Implemented: retained raw `cpu_percent` compatibility, added normalized `cpu_core_percent` and gold core-percent aliases, updated canonical QA labels to `CPU (core-summed %)`, and documented conversion to host-normalized CPU. Created canonical `concept/lintap-cpu-unit-conventions.md`.
Verification: Lintap pidstat collector tests passed (`14/14`); Wintappy dashboard compiled; full Wintappy `make dbt-build` passed (`PASS=78 WARN=0 ERROR=0`).

## [2026-08-30] test | One-hour Tenable-filtered capture

Source: `lintap-perf-20260830-tenable-filter` perf parquet under `dayPK=20260830/hourPK=20` plus matching Lintap log records.
Results: the capture covered `19:13:55Z -> 20:13:54Z` with 714 procfs samples. The policy-enabled pipeline recorded no FileOps sender drops, aggregation cap bypass, summary enqueue failures, or FileSerializer backlog warnings. Runtime CPU averaged `22.4%` host-normalized, about `7.2` core-summed CPUs on the 32-logical-CPU host. Limitation: the latter half overlapped a Wintappy DBT build, increasing FileOps queue depth and CPU/memory, so this is a no-loss policy/stress success rather than a clean performance baseline. Follow-up: run a quiet-host one-hour comparison after scan and analytics activity finish.

## [2026-08-30] analysis | No-Tenable capture reveals persistent FileOps saturation

Source: `lintap-perf-20260830-no-tenable` perf parquet under `dayPK=20260830/hourPK=22` plus `/var/log/lintap/runtime/Logs/Lintap.log` for the matching `14:49:06-15:49:05 PDT` window.
Pages created: `work/improve-etl-and-qa/no-tenable-run-analysis-2026-08-30.md`.
Pages updated: `work/improve-etl-and-qa/verification.md`; `work/improve-etl-and-qa/dev_handoff.md`; `work/improve-etl-and-qa/tenable-scan-storm-response-2026-08-30.md`; `index.md`; `log.md`.
Results: all 60 policy summaries reported zero suppression, but FileOps sender depth remained near its 524288 cap and the hour recorded `601126` sender drops plus `192774` summary enqueue failures. FileSerializer stayed healthy (`0` warnings, `26` high-water drains, max remaining `170`, max drain `3 ms`). CPU averaged `30.82%` host-normalized; RSS and anonymous memory were stable within the hour. The filtered run's queue had grown `7860 -> 338592` and first dropped 23 minutes after its capture; queue/RSS correlation during that growth was `r=0.749`. Conclusion: the policy controlled its exact Tenable worker, but the non-policy sender path is not sustainable and another long baseline is blocked pending sender CPU/throughput attribution and a zero-loss low-depth gate.

## [2026-08-30] analysis | FileOps sender and Esper throughput

Sources: `../wintap` FileOps sender, EventChannel, ProcessResolver, PluginManager, File EPL/serializer, NEsper 8.9 threading API, the no-Tenable log window, and new isolated benchmark runs in `diagnostics/nesper-repro`.
Pages created: `work/improve-etl-and-qa/esper-sender-path-analysis-2026-08-30.md`.
Pages updated: `pipeline/nesper-esper-event-stream-processing.md`; `component/fileops-event-pipeline.md`; `work/improve-etl-and-qa/{verification,dev_handoff,implementation_plan}.md`; `index.md`; `log.md`.
Code changed in `../wintap`: added deterministic NEsper throughput/fidelity scenarios; stopped deploying the broad all-event subscriber statement when ETL is enabled but no subscriber plugin exists; corrected nested-enum EPL generation from `.` to `$` without enabling the opt-in rewrite.
Results: production-shaped `file.epl` sustained a median `178756` synthetic events/s with exact count/byte conservation, versus the live sender's implied `194.7/s` ceiling and `118.3` process-cache misses/s. The redundant broad statement reduced isolated throughput to `62785/s`. Outbound threading gave no meaningful gain; context aggregation reduced ingress and failed concurrent-boundary fidelity. Lintap build passed with 0 errors and the default NEsper repro passed all queries. No live redeploy was performed because the low-risk Esper cleanup is not sufficient by itself to resolve the dominant process-resolution bottleneck.

## [2026-08-30] code | Bounded historical process identity cache

Sources changed: `../wintap/wintap/core/infrastructure/{BoundedEventTimeCache,IProcessResolver,ProcessResolver,EventChannel}.cs`; `../wintap/wintap/platform/linux/sensor/ebpf/FileOpsSensor.cs`; `../wintap/tests/Wintap.Tests/{BoundedEventTimeCacheTests,ProcessResolverTests}.cs`; `../wintap/diagnostics/nesper-repro/{Program.cs,README.md}`.
Implemented: File-only historical identity resolution now uses a configurable 32,768-entry LRU of closed process intervals before DuckDB; retention seeds entries before deletion and the triggering lookup retries after maintenance. Newest valid create time wins across PID reuse. Event-time and Stop/reconciliation SQL preserves sub-second timestamps. Removed per-query debug logging. FileOps sampled timing now reports atomic average/max totals split into resolve, health, and Esper stages, plus historical-cache counters.
Verification: Lintap build passed with 0 errors; combined cache/resolver/FileOps/policy/serializer tests passed `39/39`; resolver tests include sub-second PID reuse and lookup-triggered retention deletion. Simulated 5 ms miss cost produced about `200/s`, `400/s`, `799/s`, `1995/s`, and `1.06M/s` at 0%, 50%, 75%, 90%, and 100% hits. A 50k-key/32,768-cap run evicted exactly 17,232 entries and stayed bounded. Independent review found no deployment blocker after fixes. Live deployment was not run because noninteractive sudo requires a password.

## [2026-08-30] test | Historical identity-cache ten-minute live gate

Source: operator-deployed `lintap-0.3.4-1.el8.x86_64`, `/var/log/lintap/runtime/Logs/Lintap.log`, and `/var/log/lintap/runtime/esper_staging/fileserializer` on `validation-host`.
Deployment verification: installed DLL hash matched the `0.3.4` publish payload (`7bd7ab38...`); PID `3322161` started at `20:54:30 PDT`; startup logged cache capacity `32768`, plugin count zero, and no redundant broad subscriber EPL.
Results: ten FileOps intervals had queue depth `0..1889`, zero sender drops/summary failures/cap bypass/cache evictions, and an `82.7%` historical-cache hit rate (`32700/39537`). Weighted sender latency fell from the prior `5135.7 us` to `449.7 us`; resolution was `445.1 us` and Esper `2.7 us`. FileSerializer drained `221668` rows through 63 flushes with zero warnings/errors and current Parquet output remained readable. Short gate PASS; continue extended monitoring for cache-capacity and rare ~56 ms resolution stalls.

## [2026-08-31] test | Historical identity-cache overnight and recovery gate

Source: uninterrupted `lintap-0.3.4` PID `3322161`, `/var/log/lintap/runtime/Logs/Lintap.log`, readable serializer Parquet, and the existing 6,000-file high-cardinality smoke.
Pages created: `work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31.md`.
Pages updated: `component/process-table-retention.md`; `work/improve-etl-and-qa/{verification,dev_handoff}.md`; `index.md`; `log.md`.
Passive results: 10h23m, 617 FileOps intervals, queue average/max `5205.5/17387`, cache hit rate `75.4%`, 394252 bounded evictions, sender/resolve/Esper averages `560.6/547.1/12.0 us`, and zero sender drops, summary failures, cap bypass, serializer warnings, or send errors. FileSerializer drained 11.2M rows. Controlled result: 6,000-file smoke PASS with all five activities; queue high-water `71802`, next-interval depth below pre-burst, and zero fidelity loss. Limitation: logs/Parquet-only mode supplied no overnight CPU/RSS/GC/FD/map slopes.

## [2026-08-31] backlog | Adaptive FileOps sampling and diagnostic Parquet

Source: operator future-work requests after the historical-cache overnight validation.
Pages created: `work/improve-etl-and-qa/future-adaptive-fileops-and-diagnostics-data.md`.
Pages updated: `work/improve-etl-and-qa/implementation_plan.md`; `index.md`; `log.md`.
Future items: investigate event-rate/type-aware adaptive sampling that preserves representative scan telemetry with weighted count/byte estimates; convert timing, queue, cache, policy, resolver, serializer, and loss diagnostics from log text into first-class partitioned Parquet and DBT data. No implementation decision was made.

## [2026-08-31] backlog | Reusable Marimo performance analysis

Source: operator request while analyzing the retrieved overnight pidstat aggregate.
Pages updated: `work/improve-etl-and-qa/future-adaptive-fileops-and-diagnostics-data.md`; `work/improve-etl-and-qa/implementation_plan.md`; `log.md`.
Future item: promote the current local-time partition selection, passive/burst phase labeling, pidstat resource trends, FileOps diagnostic alignment, correlations, and recovery metrics into a focused Marimo notebook or a separated section of Wintappy's canonical QA notebook.

## [2026-08-31] analysis | Retrieved overnight pidstat resource trends

Source: `<local-path>`, retrieved from S3 using local `dayPK`/`hourPK` pruning and aligned with the overnight Lintap log.
Pages updated: `work/improve-etl-and-qa/historical-cache-overnight-validation-2026-08-31.md`; `component/fileops-event-pipeline.md`; `work/improve-etl-and-qa/verification.md`; `log.md`.
Results: passive CPU averaged `10.12%` host-normalized and was stable post-warm-up. RSS continued increasing post-22:00 at about `35 MB/hour`, slowing to about `19 MB/hour` over the last four hours. FileOps FD-path entries grew `24 -> 11184` at about `1058/hour`; RSS/entry level correlation was `0.929` overall (`0.938` post-22), while minute-delta correlation was `0.253`. FD-cache cleanup is now the leading residual memory hypothesis. The controlled 6,000-file phase averaged `10.44%` host CPU and did not leave a material RSS step.

## [2026-08-31] closeout | Owning commits anchored and Wintap gates strengthened

Owning commits: `../wintap` `c03d731..2d3f795`; `../Lintap` `1b23f77`; `../Wintappy` `a53cce6..e4b3bc3`.
Wintap cleanup: explicit zero serializer settings now retain inherit/disable semantics, policy counter reporting has an event-independent timer, unresolved historical-cache retries no longer double-count misses, and the high-cardinality smoke requires at least 95% distinct-path coverage.
Verification: Wintap Linux build passed, both BPF tiers built, focused tests passed `41/41`, and the strengthened live smoke captured `6000/6000` distinct paths with open/read/write/close/delete and no serializer loss.

## [2026-08-31] maintenance | ETL/QA documentation current-state cleanup

Pages updated: `work/improve-etl-and-qa/{verification,dev_handoff,implementation_plan,no-tenable-run-analysis-2026-08-30,tenable-scan-storm-response-2026-08-30,esper-sender-path-analysis-2026-08-30,historical-cache-overnight-validation-2026-08-31}.md`; `component/{fileops-event-pipeline,process-table-retention}.md`; `pipeline/nesper-esper-event-stream-processing.md`; `concept/lintap-cpu-unit-conventions.md`; `index.md`; `log.md`.
Summary: removed superseded current-state instructions, separated chronological field results from active gaps, and made partial canonical promotion explicit. Replaced high-confidence `<local-path>` and `<local-path>` frontmatter anchors with durable wiki/source evidence; retained ephemeral locations only as qualified artifact locators with run IDs, exact windows, commands, and SHA-256 values. Canonical pages now carry explicit pending sibling commit placeholders.
Checks: all 116 wiki Markdown files passed required-frontmatter and wikilink
validation; all changed pages passed `grounded_by` and `source_paths` resolution;
no `<local-path>` or `<local-path>` frontmatter anchors remain; hash/coverage commands and
`git diff --check` passed. `.nfs` files were excluded. No commit or push performed.

## [2026-08-31] diagnosis+instruction | [wintap] improve-windows-process-collection reboot lineage follow-ups

Recorded the WPC reboot-lineage follow-up thread at a summary level: wpc-11 repaired parent linkage on boot-replay dedup, wpc-12 addressed DuckDB UTC `DateTimeKind` round-trips, and wpc-13 was drafted for sub-second `ResolveProcessAtTime` comparisons. Open state: wpc-13 awaits approval/implementation; expected evidence is a reboot smoke with increased parent-link repair count and one lineage PASS.

## [2026-10-03] feature-open | Debian package refresh (debian-package-refresh)

Source: operator request "I'd like to now have a package for debian", scoped against `../Lintap/packaging/`.
Key finding: Debian packaging already exists (`../Lintap/packaging/lintap-deb/`, the June 2026 original the RPM was derived from) but drifted behind the field-proven RPM builder: pre-two-tier tracer validation (fails cross-builds), stale lintap.env missing the field 0.3.4 sensor block, no MCP publish isolation/--skip-mcp, repo-mount work root. Feature is a parity refresh, not greenfield.
Interview (2 rounds + playback, confirmed): Ubuntu amd64 + arm64 both validated (native arm64 host available); field-parity env with Snappy kept as deliberate divergence (Ubuntu glibc satisfies libnironcompress); MCP matches RPM behavior incl. --skip-mcp; selinux_tracer.bpf.o packaged if built, never required; ldd-verified Depends and upgrade-case maintainer scripts in scope; lintian/changelog/copyright, hardening, apt hosting, extended gates, RPM-builder and ../wintap changes out of scope. Sealed estimates recorded in interview.md.
Pages created: `work/debian-package-refresh/{interview,brief,references,implementation_plan,dev_handoff,verification}.md`.
Pages updated: `index.md`; `log.md`.

## [2026-10-03] implementation | Debian package refresh arm64 slice

Implemented dpr-01 through dpr-04 and dpr-06 on matching branch
`feature-branch` in `../Lintap`. The Debian builder now uses a
native `<local-path>` work root, tier-aware eBPF validation, separate MCP publish
with `--skip-mcp` isolation, field-parity environment settings while keeping
Snappy, upgrade-safe maintainer scripts, and ldd-based dependency checks. The
arm64 native fresh publish, package inspection, install/start, upgrade, remove,
purge, and skip-MCP checks passed. Ubuntu 24.04 leaves the optional .NET
diagnostic provider's old `liblttng-ust.so.0` unresolved; this is retained as a
warning and documented in the feature verification. dpr-05 amd64 validation is
next.
Branch: `feature-branch` created in Wintap-Analytics. Next: dev handoff (dpr-01+dpr-02 first slice) — implementation writes authorized for ../Lintap/packaging/lintap-deb only.

## [2026-10-03] implementation | Debian package refresh amd64 cross-build

No native x86_64 Multipass host is available on the Apple Silicon validation
machine. Ran the authorized cross-build from `validation-host` (`aarch64`) for
`amd64/linux-x64`: fresh publish, separate MCP publish, package structure, ELF
architecture, maintainer-script syntax, and tracepoint-only object validation
passed. Artifact `lintap_0.1.0-11_amd64.deb` SHA-256 is
`c4bd44e47a94f12498e95aaa2bac7430750d03303e39e9d842232d025179bcda`.
Native amd64 install/start/upgrade smoke remains pending until an x86_64 host
is available.

## [2026-10-03] verification | Debian package refresh native amd64

Native amd64 validation completed on the UTM Debian 12 VM at `<address>`.
Fresh revision `12` build and package inspection passed; revision `13` was
installed over it with the service remaining enabled and active. The service
produced readable parquet output (105 rows across host and macip files).
Remove preserved data and the conffile; purge removed `<local-path>` while
preserving the data marker. Revision `12` SHA-256:
`dccc2f923b3b5f0a9fe300dc67c86b15c965d1bd608cc96534401e4ad12974f9`.
Revision `13` SHA-256:
`497d5ee0aa7720118b8c84db0c808661b5b693237bdd0bc38bcacb0d4a199df9`.
The UTM Debian host required `CPATH=<local-path>` for the
multiarch eBPF headers; no source change was made for that environment issue.

## [2026-10-03] verification | validation-host live sensor smoke tests

Ran the available live integration tests against the running arm64 sensor on
`validation-host` using `/var/log/lintap`: process creation/tree, file activity, and
network activity. All passed. Process coverage included `fork_exec`,
`posix_spawn`, and `execveat_fexecve` with valid parent linkage and hashes; file
coverage captured open/read/write/close/delete; network coverage captured three
rounds of HTTP/HTTPS and UDP traffic with TCP 443 and UDP 53 parquet rows.
SELinux was not tested because the VM has no SELinux filesystem, tools, or
policy packages installed.

## [2026-10-03] release-prep | Debian artifacts rebuilt; RPM stale blocker recorded

Rebuilt Debian arm64 and amd64 artifacts at application version `0.1.0`,
revision `14`: arm64 SHA-256
`c26c48290997a4120a18b227913722b22d288386b8abafd23c02df915325e961`; amd64
SHA-256 `ea2f2659736a1f81d97ee2780315d8033ae4dcdeb7ae835f0c0bc382da8eaa2f`.
The latest RPM remains `0.1.0-3.el8`, built 2026-06-18, SHA-256
`38bfecbad374b2ecc8dc0f9b85cfd50eaaa3c7936aca61b18055ef0b0dd1657f`.
Attempting a fresh RPM build on the arm64 Multipass host stopped at the RPM
builder's obsolete `file_ops_tracer.bpf.o` assertion; no RPM builder changes
were made because that path is outside the authorized feature scope.

## [2026-10-05] documentation | Release README draft for package assets

Created `work/debian-package-refresh/release-README.md` for the proposed RPM
`lintap-0.3.5-12.el8.x86_64.rpm` and Debian `0.1.0-14` amd64/arm64 assets. The
draft documents the mixed package versions explicitly, installation and
service commands, runtime layout, upgrade/removal behavior, Snappy divergence,
and the required `SHA256SUMS` release companion. The final RPM checksum was
verified from `<local-path>` and added to the README.

## [2026-10-05] closeout | Debian package refresh

Closed dpr-01 through dpr-07. Promoted the Debian package-builder contract and
compression divergence to `repo/lintap-supporting-repo.md`; finalized
verification, release README, and missing-data metrics artifacts; and updated
the index. Native arm64 and amd64 Debian validation passed. RPM builder parity
remains explicitly out of scope and the published RPM is documented as an
independently versioned release asset.

## [2026-10-05] closeout | Pull requests opened

Implementation PR: https://github.com/llnl/Lintap/pull/6
Analytics/wiki closeout PR: https://github.com/llnl/Wintap-Analytics/pull/24

## [2026-10-12] future-work | Privileged eBPF helper boundary

Source: `../Lintap` packaging units, packaging review, and README.
Pages created: `wiki/work/privileged-ebpf-helper/future-privileged-ebpf-helper-boundary.md`.
Pages updated: `wiki/index.md`.
Summary: recorded a speculative least-privilege deployment pattern that moves
eBPF loading and BPF-object ownership into a privileged helper while running
the .NET processing service as a dedicated non-root user over a protected
Unix-domain socket. Captured capability, systemd hardening, IPC, migration,
and validation questions; current root-service behavior remains grounded in
Lintap packaging sources.
Contradictions flagged: none.

## [2026-10-15] feature-open | Refactor file system data and log paths (refactor-data-log-paths)

Source: operator request via the LLM-assisted feature workflow invocation.
Grounding: Env.cs/ConfigManager root resolution, ETL Paths.cs derivations,
WintapLogger/ProcessResolver/EventChannel/controllers runtime paths, the
hardcoded `<local-path>` literal in NetworkSensor.cs, Lintap deb/rpm
packaging (`WINTAP_DATA_ROOT=/var/log/lintap`), and the pidstat collector
spool.
Interview (4 rounds + playback, confirmed): split the single mixed root into a
shared archivable `data` tree (today's parquet event tables; the mountable
piece for shared-storage test environment multi-VM shared storage) and a host-only
`runtime` tree (logs, duckdb event store, csv, recordings, spool, diag,
workbench state, ai). Two independent roots: `WINTAP_DATA_ROOT` repurposed to
mean the data tree; new `WINTAP_RUNTIME_ROOT`. FHS-style sibling defaults under
the per-OS app root. Cross-platform code scope; Linux-gated acceptance (package
smoke, two-instance shared-mount simulation, Wintappy DBT run). Constraints:
raw_sensor internals and leaf naming frozen; no auto-migration (wpc-09
precedent). Hostname layer for cross-VM runtime visibility is a mount-time
convention (`<shared>/hosts/<hostname>/`), not sensor code. Partially
supersedes decision/platform-runtime-data-root-defaults at close-out. Sealed
estimates supplied shortly after interview close and recorded verbatim in the
sealed section of interview.md (values not repeated here — sealed until
close-out).
Pages created: `work/refactor-data-log-paths/{interview,brief,references}.md`.
Pages updated: `index.md`; `log.md`.
Contradictions flagged: none.

## [2026-10-15] planning | refactor-data-log-paths design, plan, and dev handoff

Source: continued feature planning on branch `feature-branch`
(created this session), plus design-time scans of ../Wintappy and Analytics
tooling for path couplings.
Key design choices: the repurposed data root directly contains `raw_sensor/`
(no `parquet/` level — keeping it was explicitly rejected; only a human can
un-reject); runtime tree keeps existing child names under a new parent; single
derivation point per tree in Paths.cs with grep gates; Wintappy tracks via one
Makefile default change (`WINTAP_DBT_DATASET` drops `/parquet`) since DBT
macros funnel through `raw_sensor_dataset_path()`; pidstat collector spool
moves to the runtime root. Design-time scan found no hardcoded path couplings
in Analytics streamlit/notebooks (dev agent re-verifies).
Plan: eight rdp-NN slices — two-root core (rdp-01) and consumer moves
(rdp-02) gated before packaging (rdp-03), Wintappy tracking (rdp-04), then
the three acceptance gates (rdp-05..07) and closeout (rdp-08).
Handoff: authorizes ../wintap, ../Lintap packaging+collector, ../Wintappy;
first slice rdp-01+rdp-02; interview.md sealed-section warning included;
micro-range layout conflicts escalate to the human. Implementation moves to
an environment containing shared-storage test environment.
Pages created: `work/refactor-data-log-paths/{design,implementation_plan,dev_handoff}.md`.
Pages updated: `work/refactor-data-log-paths/interview.md` (sealed estimates
recorded); `index.md`; `log.md`.

## [2026-10-19] review | refactor-data-log-paths closeout preparation

Source: final implementation review across `../wintap`, `../Lintap-rdp`, and
`../Wintappy`, plus the disposable `validation-host` package host.

Confirmed: two-root resolution and focused tests, Debian arm64 fresh package
event-output smoke, runtime/data filesystem boundary, manual test-host cleanup,
and Wintappy `make dbt-build` against six fresh files under a direct data root.
Promoted the durable split-root decision and updated upload/cache, Lintap, and
Wintappy canonical pages. Added a deliberately manual cleanup utility for
disposable test hosts; package install and runtime still do not migrate or
delete data.

Open validation: the two-instance shared-mount simulation is not claimed, and
RPM runtime smoke remains unavailable without an EL8/RPM host. The feature is
therefore prepared for closure but remains open until the shared-mount gate is
performed or explicitly waived.

Pages created: `decision/separate-data-and-runtime-roots.md`.
Pages updated: `decision/platform-runtime-data-root-defaults.md`,
`component/sensor-upload-cache-pipeline.md`,
`repo/{lintap-supporting-repo,wintappy-pipeline-repo}.md`,
`work/refactor-data-log-paths/{implementation_plan,verification}.md`,
`index.md`, `log.md`.
Contradictions flagged: none.
Contradictions flagged: none.
## [2026-10-19] documentation | Sanitized Windows attribution validation executive summary

Architect requested preservation of the reviewed developer-archive summary without source references because the original archives are intended for deletion. Created [[wiki/diagnostic/windows-attribution-validation-executive-summary]] and updated the index. The nine-paragraph historical record preserves architecture, reported test counts, attribution metrics, negative/inconclusive outcomes, and evidence limitations while omitting machine-specific identifiers and source locators. Confidence is low because source references are intentionally not retained; no tests were rerun and no current implementation signoff is implied.

Open questions: sustained Registry attribution, validator cleanup reliability, the full 24-hour acceptance gate, and finalized-Parquet linkage verification remain unresolved in the reviewed evidence. No new architecture decision was made. No original archive, source code, or test file was modified or deleted; no commit or push performed.

## [2026-10-19] documentation | Preserve attribution and FILE-path correctness contracts

Created [[wiki/concept/windows-attribution-and-file-path-correctness-contracts]] at the Architect's request and added it to the index. Retained only technical predicates, compatibility boundaries, tradeoffs, regression expectations, and open validation work; separated accepted contracts, reported implementation, and unverified approved design. Original source references and machine-specific observations are omitted. No new architecture decisions, source/test changes, archive deletions, commits, or pushes. Open validation gaps remain as recorded in the companion executive summary.

## [2026-10-21] verification | improve-lintap-data-quality long isolated captures

The recorded DBT snapshots for acceptance4 and acceptance5 have zero PID-hash
orphans and `Unknown` names across file and network relations; their explicit
file workloads also pass. The controlled acceptance6 workload remains clean and
observes `ubuntu`/`nobody` Start users, but a final rebuild after service stop
found a 20-second system-workload lifecycle gap: 21,571 file and 12 network
orphan rows have stable child identities but no matching process row. Its
FileSerializer also reports 32,496 in-memory drops, although FileOps reports
zero sender-queue and ring-reservation drops. Thus no full-capture acceptance
claim is made. The focused restored xUnit suite passed 348/348. Details:
`wiki/work/improve-lintap-data-quality/verification.md`.

## [2026-10-22] code | Named cross-domain field stimulus and Ubuntu package result

Added Wintap Python stdlib workload with named process families, current Linux
FileOps and TCP/UDP stimuli, per-run operation/PID/path/port manifest, explicit
skips/failures and optional native clone/clone3/vfork probes. Two Linux regressions
pass; Ubuntu arm64 default/IPv6/native stimulus runs complete. Documentation
separates generated activity from proven capture and marks mmap-as-Read,
rename/truncate and IPv6 limits. Added tool page, README and RHEL handoff link.
Debian revision 104 normal ETL acceptance completed: 80 baseline/400 churn births,
zero thread Starts/wrong worker parents/identity splits; HOST/restart/opt-out pass.
Counter/overhead review and RHEL remain open. No commits or pushes.

## [2026-10-22] code | Smoke results app and portable cross-host run manifests

User requested per-test Streamlit sections/commands/queries/run grouping and
explicitly allowed smoke-script updates, no legacy-data support. Analytics app
uses independent raw-parquet and portable manifest/upload sources; Wintap scripts
emit UUID/test-host/time/PID/path/endpoint envelopes including failed validation.
Queries normalize ETL/direct schemas/time scales, require host attribution and do
not merge repeated runs by process names. Empty UI and run-isolation/query tests
pass; Linux manifest/workload and actual-object Clone checks pass. Fresh packaged
VM→Mac integration collecting; durable app/tool and work records created. No DBT
state/data modified, no commits/pushes, unrelated dirty files preserved.

## [2026-10-22] verification | Smoke dashboard VM-to-Mac integration

Transferred packaged normal-ETL raw parquet and independent portable manifests
from Ubuntu arm64 Multipass to approved Mac temp storage. App queries 33 files
without errors, renders 36 tables and isolates two repeated runs. Second run
captures process lifecycle/five file activities/client TCP and UDP activity;
server TCP Accept and UDP Receive are absent and displayed as gaps. First run
occurred before sensor readiness and remains empty rather than borrowing data.
Final 11 app/query tests pass; Linux manifest/workload tests pass; diff checks
clean. No full network acceptance claimed. Service stopped; docs and work checklist
updated, no commits/pushes.

## [2026-10-22] plan | Durable smoke evidence and dashboard triage

Investigated live CacheManager/uploader, pidstat producer and Wintappy partition
precedents. Proposed raw_smoke_test typed parquet envelopes with manifest JSON,
immutable run revisions, runtime spool, UTC publication partitions and dataset
auto-discovery. Flagged startup raw-parquet deletion with enabled uploaders,
any-success multi-adapter deletion, partial file-share copy, cache pruning and
default-disabled transport as deployment gates. Proposed red/yellow/green plus
gray summary preserving harness/coverage/arrival distinctions; no green from
stimulus alone or red missing-data from a mere wait timeout. Saved plan and index;
no source/app/DBT or configuration changes, no transport setup/tests performed.

## [2026-10-22] code | Durable smoke parquet and dashboard triage

User accepted normal destination latency/source deletion and authorized coding.
Wintap shared smoke wrapper now optionally exports atomic immutable parquet
snapshots (typed metadata/full JSON/hash) into raw_smoke_test UTC partitions.
Analytics auto-discovers/deduplicates runs and adds host/test severity counts,
history/attention filters and section navigation with bounded event detail reads.
Pending/missing/stimulus-only/limited/ambiguous evidence stays yellow; thread,
identity and explicit parent violations surface. 19 app/query tests, four producer
tests and two Linux workload tests pass. Mounted VM→Mac live capture: 23 telemetry
and six evidence parquet, two isolated runs, no separate manifest transfer/errors.
Known server TCP Accept/UDP Receive gaps remain yellow. Updated canonical tool,
plan/checklist and verification. No uploader hardening, DBT, package rebuild,
commits or pushes; unrelated changes preserved.

## [2026-10-23] feature | Linux capability smoke triage retrospective and commits

User confirmed the cross-repo umbrella feature and authorized commits/PR appendices
on existing feature/improve-lintap-data-quality branches. Reconstructed brief,
interview, design, references, implementation/verification and PR summaries under
wiki/work/linux-capability-smoke-triage; linked existing detailed evidence instead
of duplicating it. No prospective metrics invented. HOST property retained;
user-discarded RawSensorWriter mixed-schema branch is not part of committed scope.
Fresh checks: 127 .NET, 19 dashboard/query, four manifest and two Linux workload
tests pass; both package builders pass bash syntax checks. Wintap commit 859a47b;
Lintap commit cfc3f35; Analytics dashboard/wiki/artifacts committed together.
Wintappy has no tracked change/commit. No pushes/branch changes; local state,
generated data, FUSE/editor artifacts and unrelated experiments remain excluded.
RHEL acceptance, isolated Clone overhead review and server-network gaps stay open.

## [2026-10-23] maintenance | Resolve Analytics PR merge conflicts

Merged origin/main into feature/improve-lintap-data-quality at the user's request.
Resolved wiki/index.md and wiki/log.md by retaining both the capability/smoke
feature records and main's AgentId/TCP investigation records; refreshed the index
date. Verified no unmerged paths or conflict markers, clean staged whitespace,
and preservation of both parents' wiki log entries and index links. Documentation
only; source tests not rerun. Unrelated .claude/ files remain untouched.

## [2026-10-23] code | Smoke dashboard PR review correctness fixes

Preserved red failure/observed-violation severity when overlapping runs add an
ambiguity warning. Validated selector objects and supported domains at manifest
ingestion, rejecting null/non-object entries without aborting valid-run rendering;
empty lifecycle selectors remain valid. Added overlap, malformed-input isolation,
and Streamlit rendering regressions. All 23 dashboard/query tests pass in the
isolated venv. Updated canonical dashboard semantics and umbrella plan/verification.
Packaging README review is separate; unrelated local files remain untouched.

## [2026-10-23] environment | .NET 10 SDK on validation-host

For the Wintap `chore/net10-dependency-prune` upgrade, installed Ubuntu's
`dotnet-sdk-10.0` on the existing Ubuntu 24.04 arm64 Multipass `validation-host`:
`multipass exec validation-host -- sudo apt-get update`, then
`multipass exec validation-host -- sudo apt-get install -y dotnet-sdk-10.0`.
Verified SDK 10.0.113, runtime/ASP.NET Core 10.0.13, clean `apt-get check`, and
a temporary Release `net10.0` console build/run (`Hello, World!`). SDK 8.0.132
and runtimes 8.0.32 remain installed; the shared dotnet host package is now 10.
No Lintap source/build/packaging changes or branch switches performed yet.

## [2026-10-23] environment | Match pinned SDK and compile Lintap

Reproduced repository build failure: `../wintap/global.json` pins SDK 10.0.402
with `latestPatch`, rejecting Ubuntu's 10.0.113 feature band. Installed Microsoft's
10.0.402 linux-arm64 archive (SHA-512 verified against release metadata) into
`/opt/dotnet-10.0.402` on `validation-host`; `/usr/local/bin/dotnet` now points to its
host, leaving apt-managed installations intact. Fresh shell selects 10.0.402.
From `<local-path>`, `dotnet build Lintap.csproj -c Release
-r linux-arm64` passes: 179 warnings, zero errors, output
`bin/Release/net10.0/linux-arm64/Lintap.dll`. Restore left shared WintapAPI and
MCP server package lockfiles modified; no manual source edits or reversions.
The earlier standalone console smoke did not validate the repository SDK pin.

## [2026-10-23] verification | .NET 10 Debian package on mounted validation-host

Installed user-supplied arm64 `lintap_0.1.0-1_arm64.deb` (bundled runtime 10.0.13),
configured fresh mounted data root `net10-package-20261023T220407Z` under
`<local-path>` (Mac `<local-path>`), native runtime,
and 10/15-second serialization/merge. Process Stop/20-child attribution, 100-file
five-activity/no-drop, and outbound TCP/UDP smokes PASS; named/native stimulus
completes. Mac discovers four runs via 12 evidence parquet; Streamlit renders
49 tables without errors, 3 green/1 yellow/4 gray. Named server TCP Accept/UDP
Receive still absent; partial arm64 FileOps legacy hooks, unavailable SELinux,
and unresolved disabled SignedS3UrlAdapter documented. Service left running;
pidstat/DBT/shutdown/long-run gates not tested. Record/index updated; no source
or packaging edits, deletions, branch switches, commits or pushes.

## [2026-10-23] verification-start | .NET 10 packaged 30-minute soak

User authorized 30 minutes on the existing running validation-host package/mounted
dataset. Started native runner in background, five six-minute-spaced rounds of
network, process Stop/20 children, 1,000-file/no-serializer-drop, and named/native
clone smokes, with 30-second service/RSS/CPU sampling and baseline-relative log
loss checks. Each test publishes dashboard evidence to the same mounted root.
Service/configuration unchanged; no source edits. Pending completion, not PASS;
details in wiki/work/net10-dependency-prune/verification.md.

## [2026-10-23] verification | .NET 10 packaged 30-minute soak PASS

Completed exactly 1800 seconds (22:31:44–23:01:44 UTC): all 20 runs exit 0;
5,000/5,000 unique workload file paths retained across five rounds/all activities.
PID unchanged, zero restarts/disruptions, all observed serializer drop totals zero,
no new log errors/loss signals. RSS 507.7→532.7 MiB (range 498.7–569.9), sampled
core-summed CPU 2.92%; diagnostic only, no long-run leak/baseline claim. Mac reads
24 runs/72 evidence parquet with zero query errors; 15 soak validators green,
five named workloads yellow for existing server-network gaps/stimulus-only scope.
Service left running. Verification/index updated; DBT/pidstat/shutdown/other
platform gates remain unrun, no source or package changes/commits/pushes.

## [2026-10-23] code | Shared network endpoint normalization and name-contract regressions

User authorized Wintap/Wintappy fixes plus regression guards, then added same-host
separate-PID and single-process socket ends over a non-loopback interface. Replaced
stale slash-name inbound matching with typed classification, preserved directed
ports in parquet, normalized canonical/legacy SQL counters, added DBT vocabulary
gate and literal audit (broader audit separately flags uppercase STOP comparison).
Normal ETL network smokes now confirm endpoints by default; standalone endpoint
manifest and independent dashboard role/provenance/hash checks added. 26 actual
Windows-targeted .NET tests on Ubuntu, 74 SQL, 8 workload/oracle, 7 audit and 26
dashboard tests pass. Isolated source capture (Oct 24 UTC/Oct 23 local) passes both
corner cases and Mac is green; installed PID/restarts unchanged. Existing DB read
only; original package not replaced, no Windows live/full-network acceptance or
historical repair claim. New work plan/verification and network/dashboard pages
updated. No branch switches, commits/pushes; unrelated dirty work preserved.

Final focused counts after numeric/comma-name rejection and explicit-smoke-opt-out
tests: 28 .NET, 74 SQL, 10 endpoint/workload, 7 audit, 27 dashboard; all pass.

## [2026-10-23] documentation | Foundational identities and cross-host metadata findings

Added high-level agent_id/pid_hash/conn_id versus endpoint-orientation concept,
prominently linked from index and process/network pages. Full canonical tuple
identity is directionless and not socket-lifetime identity; directed ports remain
necessary to validate same-IP/same-PID normalization. Read-only supplied database
confirms validation-host/validation-host share UUID <identifier>,
also present in local initialized state (committed template empty). Copied-state
deployment is plausible, not verified; documented persistence/clone boundary and
future pid_hash impact of rotation. Confirmed Wintappy's four silver/legacy Windows
labels and sensor registry-only OS-name fallback; recorded platform-derived metadata
and cross-host regression proposals. Linked previous AgentId verification with an
explicit scope follow-up. Source, runtime state, services and database untouched.

## [2026-10-23] decision | Process hash excludes AgentId and has one formula definition

User clarified intended pid_hash inputs: hostname, PID and canonical process-start
time only, excluding agent_id, with a single calculation definition across the
entire codebase. Recorded accepted ADR and corrected concept/process/diagnostic
wording to distinguish intended contract from current code. Live source still
includes AgentId and has a second ProcessHash implementation in the separate Windows
WintapCoreSvcMgr project; multiple shared-helper callers are not duplication.
Linked prior process-identity ADR without changing its other decisions. Formula
consolidation, agent-independent regressions and historical/cache migration remain
implementation work; no code, state, service or dataset changes made.

## [2026-10-23] patch | Agent-independent process hash and host-bound AgentId

User authorized source patch for both identity defects. Added one ProcessIdentity
formula (hostname/PID/canonical UTC FILETIME only), source-linked Windows helper,
regressions, explicit unknown instead of event/Stop-time hash fallbacks, and
versioned process-store isolation preserving legacy files. AgentIdentity persists
runtime-root UUID with host binding, reissues legacy/differently bound copied state
once, locks/atomically writes and fails visibly; common publish uses empty template.
148 real-project focused tests pass on Ubuntu, Linux/Windows sensor/helper builds
pass. Two isolated live endpoint captures pass before/after restart, replace seeded
duplicate UUID once, preserve legacy input and retain the new UUID; Mac independently
reads two green runs and verifies six raw process vectors/zero unmatched workload
network hashes. Installed service unchanged (PID 17138/restarts 0); affected hosts,
original DB and history not migrated. Windows-live/package rollout/soak, fully
identical-clone diagnostics and OS-family fix remain separate. Plan/verification,
identity/process/diagnostic pages, accepted ADR and index updated; ADR patch-review
marker retained for deployment details. No commits/pushes or unrelated reversions.

## [2026-10-23] diagnostic | Supplied database runtime-attribution audit

Read-only attached DB/in-memory snapshots, 98 recorded checks including canonical
orphan/PK SQL and 38 schema equivalents (all zero schema failures). Found 89,325
silver file orphan rows/80,683 hashes, 8,068 Stop-only identities, 5,507 missing
parent entities. Exact historical preimage checks identify 80,409 unknown file
hashes using FirstSeen and 8,042 Stops using exit EventTime; PID 16464 produces
11,763 hashes in 0.574s. Unknown-3 confined to six older Oct 19 observations/four
hashes; historical source ties it to failed username enrichment. Also 757 gold
extra rows, zero gold file counters, all 7,557 basic network counters NULL, wrong
duration rows, receive-buffer byte semantics, partial tuples/path/metadata gaps.
Backlog/short-lived proc race is a theory, not proven loss: no logs/receipts and
process ReceiveTime=0. Current Linux ExitSensor still has an exit-time fallback;
added explicit acceptance gap to identity verification/plan without undoing passed
formula/state work. Diagnostic/script/full JSON/index and related diagnostic updated.
Database size/mtime unchanged; no source, installed service, state, or history
modification, commits/pushes, or unrelated-work reversion.

Hard contradiction flagged on the identity concept and new diagnostic: blanket
unknown-sentinel implementation wording versus residual Linux ExitSensor exit-time
fallback. Both set human-review-required; further semantic promotion paused pending
review. Passed core/Windows/state tests are preserved, not treated as all-producer
runtime acceptance.

## [2026-10-23] plan | Attribution recovery and runtime short-lived classification

Created proposed strategic/tactical plan under host-process-identity-patch: early
kernel lifecycle evidence, explicit unresolved attribution, reason-split diagnostics,
producer safeguards/SQL corrections, shadow-mode versioned role/lifetime classification,
network measurement/path/metadata work, and packaged canary/restart/burst/soak gates.
Short-lived confirmed at exit from authoritative birth; role provisional at fork/exec,
missing-birth lifetime unknown. Proposes <=1s experiment with duration bins, not accepted
semantics; preserves raw capture and bounded post-exit identity retention. Current
retry queue/exit ABI reviewed; historical Windows name map not treated as a Linux
runtime classifier. Implementation plan/index linked. Planning only: no code, schema,
service, state, supplied-DB or deployment changes; existing semantic review flags held.

## [2026-10-23] experiment | Short-lived attribution baseline and candidate recovery

User approved multi-round experiments with real-sample comparison. Added candidate
Exit kernel boottime/monotonic start evidence, legacy/extended ABI validation and
explicit unknown instead of exit-time hash; bounded exit-only lifetime/weak-role
shadow JSONL. Wintappy fixes file spelling/Open counters, file/network lifetime-only
grouping, full elapsed duration and gold uniqueness tests. 153 focused .NET and 82
SQL tests pass; Linux/eBPF builds pass. Actual in-memory sample SQL restores all
728,701 file events, removes 757 extra rows from both gold summaries, fixes 195
duration errors and 7,557 all-NULL network counters; 89,325 historical file orphans
remain visible, original DB size/mtime unchanged.

Initial six live rounds reproduce 9,741 file FirstSeen hashes and 32 exit-time hashes
in old package with disabled births; normal old package splits one Start/Stop too.
Candidate normal/burst/restart retain every expected path/event and canonical hash;
210 lifetime classifications match independent proc/kernel duration evidence.
Three longer-settling/legacy-ABI controls confirm absent kernel start yields unknown
lifetime/identity, not fabrication; 75s settling still loses events despite zero
reported ring/sender/serializer drops. Two opt-in post-producer-stop Esper batch-wait
rounds restore all paths/events; first injected round exceeds harness shutdown
deadline, retained as failed graceful-stop gate. Final same-binary barrier-off/on
pair with 120s observation deadline is pending, not retrospectively certified.

Experiment report/JSON/analysis scripts, implementation/verification/plan, diagnostics,
identity concept, pipeline repo page and index updated. Installed service remains
PID 17138/restarts 0. No rollout, historical repair, branch switch, commit/push or
unrelated-work reversal. Execve/Rundown input guards, full birth/role/retention
recovery, permanent shutdown API, network measurement/OS/path fixes and package
release gates remain open; identity review markers preserved.

## [2026-10-23] verification | Final attribution shutdown-drain A/B

Completed thirteen total isolated rounds. Final same-DLL/exit-object, births-disabled
pair uses 30s workload settling and 120s shutdown observation; both exit 0 without
harness interruption. Barrier off retains 1,975/2,088 paths and 13,369/14,616 payload
events; post-producer-stop 11s Esper wait retains all paths/events. Both export 42/42
canonical Stops, exact lifetime bins and only canonical-or-explicit-unknown file
identities. Barrier-on still has 9,984 unresolved file rows: conservation is corrected,
missing-birth attribution is not. Earlier forced-deadline round preserved as failed.
Source evidence supports pending batch loss missed by zero serializer-drop counters;
experimental flag stays opt-in, permanent drain API/platform/budget acceptance pending.
Final JSON/report/implementation/verification/index and devtools documentation updated.
Installed service PID 17138/restarts 0 and supplied DB unchanged; no rollout/commit/
push or unrelated-work reversal. Final focused regression remains 153 .NET/82 SQL.

## [2026-10-23] experiment | Original-host installed-package acceptance

User approved validation-host/validation-host candidate installation/service/mount changes.
Both initially had no package/running service. Fresh native-copy self-contained
.NET 10.0.402 arm64 package installed on both; validation-host service unchanged.
Initial harness failed: EnvironmentFile precedence ignored isolation assignments,
adding new raw output to default shared data and using existing mounted runtime;
SIGINT ended processes without graceful shutdown despite systemd Result=success.
Evidence retained, database unchanged; runtime logs are not historical provenance.
Corrected later EnvironmentFile/SIGTERM/effective-process-environment assertion;
launched default/drain/burst/restart plus TCP endpoint suite in fresh native and
per-host mounted roots. Independent results pending. Added scripts/results/checkpoint,
index and plan approval scope. No production rollout/history repair/commits/pushes.

## [2026-10-23] verification | Installed original-host workload gates and shutdown gap

Corrected eight installed-package rounds pass independently on Mac: 20,880 paths,
146,160 payload events, 840 canonical process/91,487 canonical file observations,
420 lifetime oracles, 16 separate/same-process TCP endpoint cases; persistent
distinct AgentIds and eight graceful stops without restarts. Original DB unchanged.
Whole-capture inspection finds host-B shutdown-only cron PIDs with 119 unresolved
file rows/242 events and two known-hash orphan rows: lifecycle stopped before
FileOps and retry admission closed early. host-A's 15 unknown-named background rows
retain linked identities and exec metadata transitions; not attribution failures.
Added exact anomaly JSON and retained all evidence. Linux-only candidate stops
dependent producers before lifecycle and flushes retries afterward; other-platform
timing unchanged. Revision-2 native build/179 focused .NET tests pass. Revision-1
dual monitored 30-minute package soaks and six isolated revision-2 shutdown A/B
rounds underway; no mid-soak replacement, service change on validation-host, historical
repair, production rollout, commits or pushes. Plan/verification/results/index updated.

## [2026-10-23] experiment | Shutdown-order A/B exposes canonical Clone birth defect

Six isolated shutdown-window rounds exit cleanly; validation-host installed service
unchanged. Baseline reproduces 1,379/0/1,448 known-hash orphan rows and 755/18/906
unresolved rows. Ordered candidate has zero orphan/unresolved rows in all three,
but fails 33 file/six process canonical vectors in round 1: three Clone births
use fork occurrence 10ms later than independent task birth, and Exit inherits
that history hash. Revision 2 remains failed rather than weakening the oracle.
Revision 3 extends Clone CO-RE 48-byte prefix to 56 with task start_boottime,
checks ABI sizes, prefers kernel birth and uses explicit unknown for legacy
missing-proc birth instead of fork/callback hash. New regressions and native
build underway. Original-host revision-1 soaks remain frozen/running; historical
DB and failed evidence preserved. Results/verification/plan updated; remaining
Execve/Rundown and platform/drain acceptance still open.

## [2026-10-23] verification | Revision-3 shutdown-order and canonical Clone birth

Fresh native package build/181 focused .NET tests pass. Repeated six-round A/B
passes all three revision-3 isolated captures: 6,216 file/1,171 process vectors
independently canonical; zero controlled unresolved or known-hash orphan rows;
489 controlled PIDs have captured activity after SIGTERM, verified logged stop
order and all exits graceful. Baseline still fails all three with 16/39/28
unresolved rows; third baseline reproduces another one-tick Clone birth mismatch.
Variable cutoff excludes post-collection conservation claims. All failed earlier
evidence retained and validation-host installed service unchanged. Original-host
revision-1 soaks remain frozen; revision-3 self-contained/SIGTERM missing-birth
and legacy-no-start negative controls underway. Results/verification/plan/index
updated; no historical repair, production rollout, commits/pushes. This isolated
regression pass does not establish general missing-birth or installed release QA.

## [2026-10-23] failure | Revision-3 missing-birth backlog and remote-shell incident

Missing-birth control exceeds 120s shutdown budget, escalates to SIGKILL; legacy
negative never runs. Independent Mac analysis preserves 774/2,088 paths and
4,398/14,616 payload events, 3,571 explicitly unresolved file rows, 42 canonical
Stops, no fabricated timestamp hashes. Truncated sidecar/no summary explicitly
fails a new completeness gate; raw evidence unchanged. Stop hangs at FileOps
sender join with measured slow miss-heavy backlog, not a proven deadlock. Failed
capture archived separately; release/attribution/conservation gates remain open.
During later log search, Multipass shell quoting reconstructed regex as pipeline
and accidentally invoked shutdown on validation-host. Cancellation failed; non-forced
VM stop/start restores SSH and original installed service (PID 701/restarts 0).
Service-unchanged earlier A/B claims are scoped before this incident; failed
negative predates it. Original host-A/host-B soak PIDs remain 6579/12926, zero
restarts. No files/evidence deleted. Complex remote searches now use scripts or
local archive reads. Results/verification/plan/index updated, no rollout/history
repair/commits/pushes. Revision 3 cannot be accepted generally from normal-birth passes.

## [2026-10-23] verification | Dual installed 30-minute soaks pass; revision-3 host follow-up

Independent Mac analysis passes revision-1 original-host soaks: 1,800s/host,
83,520 paths/584,640 payload events conserved; 369,419 file/3,360 process vectors
canonical; 1,680 lifetime/start/class checks, 20 bidirectional endpoint cases,
375 monitor samples/host, stable distinct agents and zero restarts. Whole-capture
204,094/207,699 file rows contain zero unresolved/known-hash orphan rows; 16/245
unknown-named but linked rows visible. Graceful stops 30.87s/51.37s; original DB
unchanged, remote upload and resource budgets not certified. Archives/native QA
preserved. After completion/archival, experimental revision 3 installed on only
host-A/host-B; fresh four-round default/drain/burst/restart and TCP suites underway,
actual-service shutdown-window rounds planned afterward. Missing-birth failure
and release/drain/recovery gates remain open; no production rollout/history repair,
commits/pushes or evidence deletion. Results/plan/verification/index updated.

## [2026-10-23] failure | Installed revision-3 conservation and endpoint gaps

Eight revision-3 installed rounds complete gracefully/no restarts with 840 canonical
process/90,568 canonical file vectors, no whole-capture unresolved/known-hash orphan
file rows, persistent distinct agents. Five pass all gates, three fail conservation:
host-A default loses 29 paths/444 events; host-B default 138/1,110; host-B drain-on
316/2,553. Exact deficient path oracle records all losses in burst cohort. host-B
default separate-process endpoint case entirely absent (not reversed tuples).
host-A serializer/final-merge complete/zero-drop receipts miss upstream loss;
host-B sampled delivery delay is ~25–26s mean/~45s max. Counter interval versus
cumulative bases preclude one-snapshot producer loss subtraction. Fixed 11s wait
is not sufficient drain assurance. Captures/full JSON/loss details retained; actual-
service three-round shutdown-window identity suites now running on both approved
hosts, not used to close conservation/missing-birth/release failures. DB unchanged;
no production rollout/history repair/commits/pushes. Results/plan/verification/index updated.

## [2026-10-23] verification | Installed shutdown tests expose delayed-attribution gap

Six revision-3 actual-service shutdown-window rounds complete: four pass acceptance,
host-B 0/2 retain full payload but have 122/309 unresolved controlled file rows
(437 events/96 PIDs). All six have canonical process hashes, captured activity after
SIGTERM, logged data-before-lifecycle stop order, endpoint coverage and graceful
stops/no restarts; no known-hash orphans or fabricated identities. Affected file
intervals lie within recorded canonical lifetimes; all 96 exit shadows use history,
and read-only native resolver snapshots plus matching WAL contain their lifetimes.
Final-state identity is not earlier availability; ReceiveTime=0 leaves registration/
retry timing unproven. Copied DB alone looked empty until matching WAL replay;
original stores unchanged. Separately run legacy-no-start control fails stop budget
and conservation (1,260 paths/7,702 events, 6,201 unknown file rows); 41 unknown/one
canonical live Stop, all 42 lifetimes unknown, no timestamp substitutes. Truncated
sidecar/native/archives retained. Both original-host services left stopped with
experimental revision 3/overrides; normal conservation and recovery/release gates
remain open. Results/trace JSON/verification/plan/index updated, no production rollout,
historical repair, commits/pushes or evidence deletion.

## [2026-10-23] code | Diagnostic retry-counter candidate without policy tuning

After host-B shutdown unknowns with containing final resolver lifetimes, added
bounded per-stream cumulative retry scheduled/refused/exhausted/invoked/error/
shutdown/pending/high-water snapshots and final logs. No PID/path payloads or
retry-capacity/timing/identity changes; counters do not prove resolved/delivered
events. Regressions distinguish forced final flush from normal exhaustion and
test stream separation/immutable snapshots; initial 183 focused native tests pass,
expanded final tests/revision-4 native build underway. Seven Python harness guards/
compile checks pass; analyzer collects new receipts and prints scoped shutdown
acceptance gates. Stuck pre-retry shutdown still lacks final receipt and remains
incomplete. Feature results/verification/plan updated; delayed attribution, normal
conservation, missing-birth/release gates stay open.

## [2026-10-23] experiment | Revision-4 diagnostic build and host-B retry receipts

Final 184 focused native tests pass; self-contained revision-4 package build succeeds
with recorded package/DLL hashes. Installed only on approved stopped host-B;
fresh three-round shutdown-window experiment now running with preserved native
identity state. host-A remains stopped on revision 3. No retry policy/recovery changes.
Independent parser three tests pass; preserves cumulative reason counters and flags
malformed/duplicate/negative fields, absent receipts not treated as zero. Optional
analysis gates require four default-stream receipts/pending zero/no callback errors,
not proof of attribution success. Build still warns optional diagnostic-provider
host dependency unresolved. Release/conservation/delayed-attribution failures remain
open; prior captures and historical DB preserved. Results/verification updated.

## [2026-10-23] diagnostic | host-B unresolved event counts match retry capacity refusal

Revision-4 three installed shutdown rounds analyzed/archived. Two fail attribution:
218 rows/230 events and 198/218; retry capacity refusals 230/218 with high-water
1024 and zero normal exhaustion. Third passes with no refusals/high-water877.
All 99 affected PIDs have containing canonical Start/Stop observations; aggregate
event counts match refusal counts, not a per-message trace or historical trigger
proof. All TCP/receipts/pending-zero/error-zero/graceful/no-restart gates pass.
host-B left stopped on revision4; host-A stopped on revision3. Revision5 diagnostic
Linux-only exact 1024/2048/4096 selector/default unchanged added for six interleaved
same-binary sensitivity controls; native tests/build pending. No permanent tuning/
never-observed-birth recovery/release acceptance. Results/trace/plan/verification/
index updated; captures and historical DB preserved.

## [2026-10-23] experiment | Bounded same-binary retry-capacity controls launched

Revision5 self-contained native build and 196 focused tests pass. Verified package
hash, installed on only approved inactive host-B, and launched six interleaved
1024/4096 actual-service shutdown captures with same binary/fresh roots/persistent
native identity. Default remains1024, attempt limit10/interval1s unchanged; Linux-
only experimental knob, not release tuning. Independent effective startup receipt
checks added; five parser tests pass including absent/malformed configuration.
host-A remains stopped on revision3; prior failed evidence preserved. Await controls
without polling; conservation/recovery/permanent memory/deadline gates remain open.
Results/plan/verification updated, no production rollout/history repair/commits/pushes.

## [2026-10-23] verification | Same-binary capacity sensitivity supports admission pressure

All six revision5 host-B captures analyzed/archived, same DLL/Exit hashes, matching
effective config, persistent agent, graceful/no-restart stops. Three4096 controls
pass captured identity/attribution/TCP/shadow gates; one1024 control fails336 rows/
358 unresolved events matching358 capacity refusals, all67 PIDs have containing
canonical lifecycle. One4096 control resolves high-water1061 above default; other
pair pressure differs and round1 lacks retry traffic, so no blanket capacity-fix
causality/release claim. All exhausted/error/final-pending counts zero; no known-
hash orphans/fabrication. Default stays1024; missing-birth/conservation/permanent
drain/resource gates open. host-B stopped on revision5 with retained experimental
4096/batch-wait override, host-A stopped on revision3. Original DB unchanged; prior
failures/native/archives retained. Results/summary/plan/verification/index/strategy
updated; next recovery requires early birth/per-event fate/PID-reuse/drain budgets,
not simple queue enlargement. No production rollout/history repair/commits/pushes.

## [2026-10-23] code | Exit-only recovery candidate and retained test failure

Revision6 opt-in kernel-start exit evidence reuses bounded lifetime-keyed history,
without synthetic Start/durable row/active entry. Sidecar marks partial coverage;
default off. Initial compile interface mismatch corrected; next216 tests yield
215pass/1fail: pending-Stop logging bypasses injected sink before late-birth cache
invalidation. Corrected logging and canonical pending-Stop identity matching;
added reused-PID regression. Corrected217 tests and self-contained package build
pass, package/DLL hashes recorded. Four isolated same-binary controls underway
(off/on missing birth, on normal, on legacy-no-start), capacity1024/effective-env
check/30s settle/SIGTERM/120s budget; no installed-service changes. Inline remote
launcher fails parsing before execution; retry uses mounted script directly.
Failed evidence retained. Original hosts stopped on revisions3/5; recovery/drain/
conservation/release gates open. Verification/plan/index updated; no history edits,
commits/pushes or evidence deletion.

## [2026-10-23] verification | Exit-only controlled recovery; installed host-B pairs launched

Four isolated revision6 controls independently analyzed/archived. Missing-birth
recovery on:8,478/8,478 canonical files,42 canonical Stops/partial receipts,no
synthetic births,2,088 paths/14,616events conserved,12s graceful stop. Off:12,053
unknown files/59s stop. Normal passes9,130files/84process vectors; legacy-no-start
retains zero exit evidence,12,519unknown files,32unknown/10canonical live Stops,
all42lifetimes unknown. All conserve payload/graceful; single pair does not certify
resource/drain budgets. Whole missing-birth on-control has200 nonworkload known-
hash orphans (live harness/daemons), zero unknown files; lifecycle export remains
incomplete. Default1024 retry refusals off/on11,980/0; schedules50,544/519 are not
per-event fate. Installed validation-host PID701/restarts0 unchanged; remote upload
unavailable. Source shared semantics concept updated with REVIEW NEEDED, existing
hard review retained.18 independent/harness/parser tests pass. Revision6 package/
DLL verified and installed only on inactive host-B; three actual-service off/on
missing-birth pairs/TCP now running, persistent native state/effective-env/120s stop.
First wrong mount-prefix launcher fails before execution, corrected without mount
changes. host-A stopped revision3. Results/full+summaryJSON/verification/plan/index/
strategy updated, supplied DB unchanged; no release/history repair/commits/pushes.

## [2026-10-23] verification | Installed exit-only recovery passes three controlled pairs

Six host-B same-binary/default1024 off/on controls independently analyzed/archived.
All three on pass25,434canonical files/126canonical Stops+partial receipts,zero
synthetic births,6,264paths/43,848events conserved,six linked TCP cases. Off fails
37,575unknown workload files plus three sentinel network rows per capture despite
orientation passes. All six graceful/no restarts/effective-env+config match/same
DLL+Exit hashes/persistent agent. Whole on-captures retain708nonworkload known-
hash orphans (live harness/daemons/systemctl exits after lifecycle cutoff),zero
unknown files; lifecycle export remains incomplete. Retry schedules off/on140,679/
650 and refusals32,773/0 support controlled recovery,not per-event fate or resource/
drain budgets. Full+summaryJSON and QA/data archive hashes preserved; historical
DB unchanged.18 Python regression tests pass; analyzer now checks installed verified
environment as well as isolated receipts. After analysis host-A upgraded to verified
revision6 and eight dual-host normal-birth default/drain/burst/restart regressions
launched,exit recovery on/default1024/explicit birth sensors/native persistent state.
Results/verification/plan/index/strategy updated; shared semantic review marker
retained. No production rollout,historical repair,commits/pushes or evidence removal.

## [2026-10-23] verification | Dual-host revision6 normal regressions pass

All eight installed normal-birth default/drain/burst/restart rounds independently
pass:20,880paths/146,160payload events conserved,840canonical process observations/
92,571canonical files,420kernel-start/lifetime checks,16linked TCP cases. Whole
104,518files zero unresolved/unknown-named/known-hash orphans. Effective-env/config
match,same binaries,persistent distinct agents,zero retry refusals/errors/final
pending,graceful3.29–16.37s/no restarts. Both default-no-extra-wait rounds pass;
no claim exit cache alone explains prior revision3 losses or defines permanent
drain/resource budgets. Full+summaryJSON/preliminary host-B results/QA+data archives
retained with hashes,supplied DB unchanged. After analysis/archival,six actual-service
shutdown-window rounds launched across both approved hosts,exit recovery on/1024/
enabled birth sensors/native persistent agents; post-cutoff events not conserved
by acceptance. Results/verification/plan/index/strategy/shared review status updated.
No production rollout,historical repair,commits/pushes or failed-evidence removal.

## [2026-10-23] failure | Revision6 saturated shutdown attribution persists

Six shutdown windows independently analyzed/archived:host-A3pass,host-B3fail.
host-B720/437/189unknown file rows,797/467/207events exactly matching capacity
refusals;1,346rows/1,471events total,199distinct PIDs. All have canonical containing
recorded lifetimes and matching closed final-resolver rows (preserved WAL read-only
replay;DB+WAL SHA256 unchanged). Affected sidecars report history,zero retained
exit evidence; raw process ReceiveTime0 cannot show when identity became available.
No exhaustion/callback errors/final pending;all host-B high-water1024. All six
graceful15.08–25.29s/no restarts,post-SIGTERM captured stimulus nonvacuous,TCP linked,
correct stop order/complete effective-config receipts,no known-hash orphans. No
claim full post-cutoff conservation,per-event fate or permanent drain fix.21 Python
tests pass;trace exact birth/both file bounds and no vacuous affected-lifetime proof.
Full+trace summaryJSON/native QA/QA+data archives and hashes retained. Both host
services confirmed stopped on experimental revision6,retained recovery-on/1024/
birth-on/batch-wait overrides. Results/verification/plan/index/strategy updated;
next bounded admission/final-fate and birth-registration timing before early-birth/
staged-drain correction. No queue increase,history writes,production rollout,
commits/pushes or failure deletion.

## [2026-10-24] documentation | Start ecosystem glossary and grouped-retry proposal

At user request, created source-linked living glossary across ecosystem, collection,
identity/lifecycle, clocks/evidence, queues/shutdown, networking and DBT/analysis;
expansion queue retained and existing diagram glossary preserved. Added speculative
grouped-retry notes: local PID+event-time lookup, lifetime-qualified fanout, no blanket
miss denial, per-member deadlines, fair bounded events/bytes and separate adjustable
coalescing wait versus evidence-defined identity validity. Positive caches already
exist; repeated-miss/coordinated wakeup benefit remains unmeasured. Index/strategy
linked; no source/service/config changes or new experiment authorization inferred.

## [2026-10-24] clarification | Collection-edge tolerance and sensor-service shutdown

User accepts incomplete start/end collection observations within an explicit
boundary tolerance. Recorded the principle; numeric edge widths/classification
remain pending. Separate start-edge/interior/end-edge quality,actual collection
from query-slice bounds,and event time from processing/cutoff time; do not extend
identity validity or silently rewrite prior strict failure records. Clarified that
host-B shutdown tests stop lintap.service/collector PID with SIGTERM while test
activity continues,not the VM/OS or host-B application. Glossary/results/strategy/
plan/index updated; no code/config/service changes or new runtime experiments.

## [2026-10-24] requirement | Collector process visible in normal telemetry

User requires Lintap service process in ordinary telemetry for retrospective normal-
dataset validation. Current EventChannel and Linux Rundown self-PID exclusions
verified; not yet changed. Strategy/plan/results/glossary record recommended normal
process-stream identity/metadata and genuine lifecycle semantics,retained file-I/O
feedback suppression,explicit capture boundaries,and no invented self-exit record.
No source/config/service changes; implementation and normal-dataset tests pending.

## [2026-10-24] implementation | Collector visibility candidate and bounded verification

Approved Linux Process-only self-filter exception and collector Rundown inclusion
implemented; missing-birth inventory no longer hashes observation time. Preserved
self-I/O/other-platform filtering, genuine Refresh and no invented exit/cutoff.
New pure-policy/inventory/egress regressions and independent normal-row/restart/DBT
verification tooling;28Python tests pass. Native attempts preserve compile failure,
229pass/7runtime-permission fixture failures,and229pass then45s testhost abort with
dump/sequence. Isolated pure policy avoids test-triggered runtime static dependency;
fresh test/build pending. Canonical collector/boundary draft/index and verification
updated. No installed-host mutation,production rollout or prior evidence deletion yet.

## [2026-10-24] verification | Collector focused suite passes; packaging snapshot corrected

236focused C# tests pass and Linux publish succeeds. Preserved235pass/1egress
failure:fixture isolation flags were set after static routing initialization;
ordering corrected,not runtime registration semantics. Debian staging fails only
because native snapshot lacked three existing pidstat packaging helpers; fresh
complete snapshot/build launched. Strategy/checklist/glossary/pipeline/canonical
collector semantics updated; ordinary installed/DBT proof remains pending.

## [2026-10-24] experiment | Revision7 collector candidate normal/restart rounds launched

Fresh complete native snapshot:236C#tests pass,self-contained revision7 Debian
package succeeds;package/DLL SHA256 recorded in verification. Copied candidate to
approved inactive host-A/host-B; guarded installs/4normal default/drain/burst/restart
rounds launched each with enabled birth inventory,default1024,experimental exit
recovery and persistent native agents. Fresh capture/QA/install roots preserve prior
override/evidence. Ordinary-row collector oracle and fresh canonical DBT model
builds prepared;normal/self-feedback/conservation/endpoint/downstream proof pending.
No production rollout,historical migration or boundary-policy reclassification.

## [2026-10-24] planning | DuckDB 2 ecosystem upgrade

Started `wiki/work/duckdb-2-upgrade/{brief,references,implementation_plan}.md`
and linked index. Verified October21 DuckDB2.0LTS release/Python>=3.11/new-file
storage69; inventoried Wintap embedded1.5.6,Wintappy locked+actual1.5.5/adapter1.9.6/
core1.12.2,Lintap pidstat/bootstrap/CLI and current Analytics paths. Relation
fetchone removal reaches DataQA/shared helpers; latest released adapter1.11.0
predates2.0 and lacks a development-branch result-draining fix. Official .NET
NuGet latest1.5.6.1 has no2.0; unofficial fork exists but not selected/authorized.
Plan separates Python/DBT qualification from native package gate,copy-only DB/WAL
rollback and fresh-output semantic/conservation comparisons. Excludes old notebooks,
arbitrary SQL,legacy cleanup,historical repair and existing defect fixes. Existing
collector DBT completion retained as baseline:8builds retain collector,4exact-birth
failures. No source/dependency/environment/service changes or new runtime experiments.

## [2026-10-24] decision | Hold DuckDB 2 upgrade for official .NET support

User chose to wait on2.0 because official .NET availability is a blocker; brief,
plan and index marked held. Rechecked registries:latest official .NET wrapper
1.5.6.1 still bundles native1.5.6;latest Python1.x is1.5.6. Latest-1.x maintenance
considered separately; no implementation or dependency/environment changes authorized.

## [2026-10-24] maintenance | Latest DuckDB1.5 dependency upgrade verified

User approved the three enumerated components. Wintap official wrapper1.5.6.1 and
five affected locks refreshed; native engine remains1.5.6. Wintappy/Lintap manifests,
uv locks and pidstat bootstrap pin1.5.6; selective lock audits show no unrelated
package-version drift,DBT adapter1.9.6/core1.12.2 retained. NativeSDK10.0.402 tests250
pass,Linux/Windows-helper builds pass;PythonSQL82,pidstat15,SmokeTests27,collector
analyzer7 pass. Fresh fullDBT83nodes (40models/42tests/1hook) pass on retained host-A
drain raw data;collector exact birth/metadata/uniqueness pass,historicalDB size/mtime
unchanged. BroaderPython107pass/1config failure reproduces under1.5.5. Failed command/
platform attempts preserved;unintended uv recreation of MacLintapvenv3.14→3.12
disclosed,prior environment not preserved or falsely claimed. Feature verification/
plan/index and canonicalWintappy dependency note updated. No installed-service,
runtimeDB,agent-state,notebook,history changes or commits/pushes. DuckDB2.0 held.

## [2026-10-24] implementation | Collection-edge overlay and revision8 outstanding-item reruns

User approved10-second start/end edges with1/5/20-second sensitivity. Implemented
integer interval/bracket classification,verified local-clock receipts and endpoint
stimulus intervals;strict gates/counts preserved,no invented capture bounds or
identity extension. Historicalrevision7 lacks independent clock receipts and remains
unclassified. New same-installed-revision7 default+shutdown round per original host
passes all scoped raw gates:normal2,088paths/14,616events each,all TCPcases pass,
31,083whole file rows/no unknowns or known-hash orphans.10-second normal stimulus
interior;shutdown mostly uncertain under broad operational cutoff brackets. host-B
shutdown2,615scheduled/high-water932of1024/no refusals,so prior saturated failure
not reproduced or explained.64work-folder tests pass (45boundary/harness).8historical
plus4fresh DBT model runs all pass/retain collector metadata,exact birth fails same
4historical and3fresh at−1µs. Integer-only diagnostic SQL recovers12/12raw births;
source float macro unchanged and Linux-as-Windows defect persists. BroadPython
107pass/1existing config failure repeats. New QA+data archives SHA256 verified,
binary/AgentId unchanged,both services stopped/PID0/restarts0,historicalDB size/mtime
unchanged. Results/verification/checklists/canonical collector/glossary/index updated.
No package/source-sensor/DBTmacro deployment,prior failure deletion,production rollout,
commits/pushes. Next:qualify integer timestamps,admission/final-fate/registration
timing and preserved loss/TCP provenance;more precise cutoffs if uncertainty matters.

## [2026-10-24] implementation | Integer timestamp proof and bounded attribution trace

Approved continuation fixes canonicalWintappy FILETIME timestamp/minute macros using
integer epoch subtraction/floor-toµs,TIMESTAMPTZ output and integer-text parsing;raw
100ns identity unchanged.209focusedSQLtests pass;234broadpass/1existingDATASETconfig
failure retained. Fresh fullDBT12/12 (83nodes each) restores all12collector births;
2,900raw-integer process lifetimes pass.216common tables retain protected keys,
counters/rows;strict metadata comparison fails and remains archived.12same-old-macro
controls reproduce unordered names/paths/args/derivedfileID drift;qualified comparisons
separate those fields/duration without blanket display/file-ID stability acceptance.
Default-offLinux create-new boundedJSONL admission/lookup/registration/handoff trace
implemented;240nativeSDK10.0.402tests/Linuxbuild pass,initialAPI-property compile
failure and subsequent I/O-drop accounting correction preserved. Limits1024queue/
100kreceipts/32MiB/512characters,explicit refusal/error/truncation,2sclose deadline;
handoff is not durable fate.68wikifoldertests pass;new precision contract/results,
glossary/collector/repo/index/plans/verification updated;frontmatter/links/diffchecks
pass. Native logs/TRX/sourcehashes downloaded to approvedr9-native-evidence root.
No live tracing/newpackage/service changes:active validation-host left alone;host-A/host-B
inactive/PID0/restarts0/Resultsuccess,DLL unchanged,historicalDB size/mtime unchanged.
Self-contained diagnostic captures/export joins,saturation/loss/TCP provenance,
cutoffs,OSlabels and rollout gates remain open. No commits/pushes/DuckDB2upgrade.

## [2026-10-24] diagnostics | Private delivery package and failed observer controls

User approved reproduced-loss milestone. Expanded default-off observer through file
folding/sender/serializer/parquet finalization;244nativeSDK10.0.402tests/Linuxbuild
and self-contained Debian package pass. Four private host-A/host-B controls complete;
no installation/service edits,original DLL/AgentId unchanged. Both traces refuse
receipts (15,925/22,339);shared mounted root combines both hosts,strict path-set gates
fail. Per-host grouping2,088paths/14,616events does not accept contaminated captures.
First-round runtime-log snapshot omission also preserved;edges unclassified.
Archives transferred/SHA256verified;78wikifolderpytest pass. Corrected host-specific
roots/stopped snapshots and explicit bounded delivery trace queue32768 prepared;
retrycapacity1024unchanged. Revision11 inherited post-publish RID lock causesNU1004;
failure/locks preserved,live source locks used for locked requalification. Results,
plans,verification,index/glossary updated. Historical loss/TCP provenance remains open.

## [2026-10-24] proof | Complete scoped delivery traces and reproduced TCP stage gap

Revision11locked-source244tests/Linuxbuild/self-containedpackage pass after preserving
NU1004/post-publish locks. Fourprivate host-isolated controls conserve8,352paths/
58,464events,canonicalidentity/collector/workloadTCPpass. Complete scoped traces:
193,040host-A/190,071host-Breceipts,zero refusals/errors/truncation;finalizedfile/TCProw
multisets match archivedraw,file-stagecounts match. BroaderTCP54prepared/Esper→50serializer
events per host fails;fourmissingSSHcounts overlap startup. SourceasyncETLStart/fixed
5sdelay and networkstartup beforeTCPinit support readinessrace;precise registration/
projection receipts and controlled correction remain required.40,170wholefile rows
zero unknown/orphans;10sedges/1,5,20ssensitivity preserve gates.80wikifoldertests/diffchecks
pass;archivesSHAverified/sourcehashes match,originalDLL/AgentIds/historicalDB unchanged,
servicesinactive/validation-hostactive untouched. Results/verification/plans/index/glossary/
canonicalboundary updated. Prior host-Aloss/workloadTCP/host-Bsaturation unresolved;
no sourcecausefix/rollout/commits.
## [2026-10-24] verification | Exact startup proof and bounded readiness control

Revision12query/listener/callback/projection diagnostics,productionEPL deterministic
test and247native tests/Linuxbuild pass. Live complete traces prove host-B6counts
andhost-A4counts handed off before registration;host-A6additional missing remain separate.
Revision13default-off Linux readiness admits collectors only after successfulquery/
completedconstructors,30sbound,existing5sdelay unchanged.254native tests/Linuxbuild;
four off/on controls conserve8,352paths/58,464events,identity/collector/self-I/O/eight
TCPcases pass.42,005wholefile rows zero unknown/orphans.192,688/190,332complete receipts
prove startup ordering;host-B54→54→54passes,host-A54→54→48fails. ExactacceptedTCProwIDs
31378/31380 absent fromdrain/enqueue/finalized;lateprojection/shutdown cause unproved.
Final→rawjoins pass but not full delivery acceptance.10sprimary/1,5,20s sensitivity
preserved;revision13workloadintervals uncertain,not softened intointerior.88wiki tests
andbothdiffchecks pass. InitialENOSPCattempt archived/949filesbyteverified before only
newdisposable snapshot removal;activePID701 notsignaled,completeI/Oeffect unproved.
Initial253pass/1closebudget failure archived;boundedwriter tests isolated fromparallel
EPLcodegen without changingproduction2sbudget. Packages12/13managed-only derivatives
of11,notclean native rebuilds/installedacceptance. Updatedresults/plans/verification,
index,glossary/boundary pages;addedexactreadiness/delivery-ID joins and JSONreceipts.
Finalservices/DLL/AgentIds/historicalDB unchanged,258testedsourcefiles matchlive;
no runningcaptures/builds. Historicalhost-Aloss/defaultTCP,host-Bsaturation,resource/
cutoff/draining/rollout gates remainopen. No historicalrepair or DuckDB2change.

## [2026-10-24] milestone | Exact shutdown proof and verified disposable Linux delivery

Revision14exact brackets reproduce twohost-BTCProws/fourcounts accepted after
completed shutdown,all undrained. ProductionEPL deterministic control proves
queue-before-final-window strands counts. Revision16Linux/default-off terminal
window/callback barrier qualifies267native tests/locked Linuxbuild;revision15
ambiguous-import compile failure archived and corrected in fresh16snapshot.
Fourrevision16controls conserve8,352paths/58,464events and54host-A/60host-BTCPcounts
through exact accepted/drained/enqueued/finalized row IDs and archivedraw joins.
Samecandidate17 repeats58/58perhost with all payload/endpoint stimuli interior at
1/5/10/20s. Independentidentity/collector/self-I/O/eightTCPcases pass;complete traces
zero refusals/errors/discards/truncation/lateacceptance/cutoffrefusals. Wholefile
39,893rows zero unknown/orphans;10s39,807interior/25start-edge/61uncertain retained.
Scoped observed-delivery milestone verified,not historical loss closure,complete
kernel/durable fate,resource/Windows/customEPL/installed-package/rollout acceptance.
94wikifoldertests/bothdiffchecks pass;archivesSHAverified/262testedsource matches,
originalservices/DLL/AgentIds/historicalDB unchanged;validation-hostPID701 untouched.
Updatedshutdown plan/results,implementation/traceplans/verification,index,canonical
boundary/glossary and JSONreceipts. Managed-only private derivative16,not clean native
rebuild;no install/commit/push/DuckDB2upgrade. No captures/builds remain running.

## [2026-10-24] experiment | Attribution pressure baseline and corrected TCP receipt oracle

User approved samecandidate revision16 pressure with1024capacity unchanged. Independent
32/128/256child file/TCP generator and gated off/on interior/shutdown-tail experiments
created under wiki;no sensor edits or installed rollout.32tier eightcontrols conserve
1,024paths/7,168events;eightfresh fullDBTbuilds pass256births/collector/counters.
Original128revision20 halts escalation on44host-Btrace-off endpointpairs/152apparent
misses. Exact archivedraw proves ALL152present after stimulus+2s but within capture:
TCP EPL FirstSeen uses ReceiveTime,not kernel EventTime. Originalfailure preserved;
deterministic test proves falseabsence and bounded capture-scope oracle correction,
not sensorloss/saturation/time-schema change. Separate20recheck/fourDBTbuilds pass.
Fresh128revision24interior/25tail pass1,024childlifetimes/4,096paths/28,672events,
eightDBTbuilds and complete exact delivery traces;no queue refusal/exhaustion/OOMdelta.
256tier still running;no final envelope claim yet.103wiki tests pass. Plans/results,
verification/glossary/index updated;failed evidence/history/control preservation remain
mandatory. No queue resize,production sizing,historical-loss closure or DuckDB2upgrade.

## [2026-10-24] verification | Controlled pressure envelope complete through256 children

Fresh256interior26/shutdown-tail27 pass after gated128repeat24/25. Sixaccepted
experiments/24off-on hostcontrols conserve3,328childlifetimes/TCPendpointpairs,
13,312payloadpaths/93,184events.24fresh canonical83nodeDBTbuilds pass exactbirths,
collectorretention and raw→silver/goldprotectedfilecounters.12complete traces write
1,013,739receipts with zero refusals/errors/discards/truncation;exactobservedstage/
finalrawjoins pass.256TCPcounts1,857host-A/1,855host-Binterior,1,845eachtail. Highest
sampledpending348/1024,no pressurechildcapacityrefusal/exhaustion;not actualsaturation
or productionqueue sizing.10s/1,5,20s stimulusbands preserved,tailuncertainty not
relabeled. Original20oraclefailure/all152rawobservations/causeproof and separate
fourDBTrechecks preserved. No sensorfix/capacitychange/historyrepair/installedrollout.
Finalaudit28archivesSHAverified/262sourcesmatch,installedDLL/AgentIds/historicalDB
size-mtimeunchanged,host-A/host-Binactive/PID0/restarts0,validation-hostactive/PID701/restarts0.
103wiki tests/bothdiffchecks pass. Plans/results/verification/index/glossary updated.
No builds/captures running. Resource/nativekernel/durable/Windows/package/rollout
acceptance and historicalfailures remain open;DuckDB2held. No commits/pushes.

## [2026-10-24] retrospective | Telemetry identity/data-quality workflow and compact audit

User confirmed the broader retrospective scope beyond .NET10,and explicitly asked
to reduce audit detail in the commit,not merely add an entry point. Created compact
`wiki/work/wintap-telemetry-identity-and-data-quality/` brief,design,reconstructed
implementation,verification,next-phase handoff and evidence provenance. Condensed
old workstream documents from4,442to1,514lines;replaced the repetitive index rollup.
Original193files/62,580,675bytes byte-verified in an external3,840,232byte archive;
SHA256/path/retrieval map recorded in evidence.md.124generated JSON audits
(62,025,196bytes) retained locally but Git-ignored;harnesses/tests/raw/failed evidence
and source/history untouched. Archive is machine-local temporary storage and must
be transferred/verified before cleanup;no durable publication claimed. Updated
canonical evidence citations;sample-db audit remains human-review-required with
REVIEW NEEDED for provenance-only edits,findings unchanged.26pages pass frontmatter/
source/wikilink validation,103work-folder tests and diffcheck pass. No commits/pushes,
new sensor edits,host captures,package installation or long-duration runs. User's
planned package qualification/multi-day real-host collection remains next phase.

## [2026-10-24] commit | Dedicated telemetry-quality branches across four repos

User authorized feature commits and separate PR branches. Created
`feature/telemetry-identity-data-quality` in Wintap, Wintappy, Lintap and Analytics.
Wintap `10a782f` commits identity/network/lifecycle and bounded delivery diagnostics;
Wintappy `4236cbb` commits SQL precision/count/identity fixes and DuckDB maintenance;
Lintap `b793082` commits the qualified DuckDB pin. Analytics commits QA, compact
retrospective, reusable harnesses and wiki semantics in this entry's commit.
Wintap retains its tested .NET10 ancestry: target `chore/net10-dependency-prune`
for an isolated PR until that prerequisite merges. Generated receipts, captured
datasets, initialized AgentId state, local settings and unrelated work stay local.
Preflight: 209 focused SQL tests, 126 Analytics tests plus 7 subtests, and 17 Wintap
Python regressions pass; all staged diff checks pass. Dashboard AppTest collection
is blocked by missing `streamlit.testing` in the selected environment; no environment
changes or new native/host qualification. No pushes or PR publication performed.

## [2026-10-25] documentation | Pinned .NET 10 packaging and operator-assisted RHEL 9

User authorized updating Lintap's packaging guide and adding RHEL 9 prerequisites;
user will execute host commands without direct agent access. Updated live
`../Lintap/packaging/README.md` to select SDK 10.0.402 from Wintap global.json,
distinguish exact qualification checks from latestPatch, and document RHEL 9
inventory/repository/native dependency/build/package inspection and gated service
validation. RHEL 9 remains unqualified. Retained self-contained defaults and flagged
both builders' stale ASP.NET Core 8 framework-dependent metadata; no scripts changed.
Source-verified libbpf SONAME fallback, security preservation and pidstat prerequisites.
Updated supporting-repo page, index and umbrella verification. SDK consistency,
shell-fence syntax and diff checks pass; no RHEL commands, installs, captures or
security changes executed. No new commits or pushes for this documentation update.

## [2026-10-25] plan | Close .NET 10 upgrade oversights, not a package-mode workaround

User clarified that framework-dependent .NET 8 metadata is an oversight in the
original all-.NET-10 upgrade and requested a corrective plan while testing RHEL
dependencies. Tracked source inventory across four repos confirms SDK 10.0.402 and
eight main .NET 10 projects, but five diagnostic/sample net8 projects, both package
builders' runtime-8 dependency declarations, Makefile/provision/run/tooling defaults
and current docs remain stale. Created runtime_alignment_plan.md with package-first
correction, complete target/provision/path alignment, regression inventory and fresh
artifact/live gates; dependency major versions and historical records are distinct.
Updated umbrella implementation/index. No "10 everywhere" or fresh runtime claim;
no source implementation, host execution, commits or pushes under this plan request.

## [2026-10-25] code | .NET 10 source/configuration closure and RHEL build handoff

User authorized correction, commit and push on existing feature branches. All 13
C# projects evaluate to .NET 10 with SDK 10.0.402. Corrected both package runtime
dependencies, exact-SDK/project-directory preflight before cleanup, main runtimeconfig
validation, five targets/sample reference, native generated-source exclusions,
Windows-only sample copy, provisioning and active run/tool/docs defaults. Added five
sample/diagnostic locks; legacy vdproj snapshots explicitly not release packaging.
Six Wintap drift and 22 Lintap packaging regressions pass; five fresh locked sample/
diagnostic builds, both actual linux-x64 managed publish modes and separate MCP
single-file publish pass. Preserved
NU1004 committed API RID-lock mismatch: isolated restore keeps all base hashes/
versions, then locked publishes pass; pristine locked RID release gate remains open.
Generic RHEL 9 prerequisites pass; test system is disposable by user direction.
No host identifiers/raw output persisted, no direct host access/security changes.
Shell/help/link/diff checks pass. Fresh native RPM/Debian inspection and live host
acceptance remain pending; retry/identity/experimental controls unchanged. Commits
and pushes are explicitly authorized; PR publication is not part of this operation.

## [2026-10-25] verification | Operator-reported RHEL 9 package build and installation

Operator reports native self-contained RPM build, satisfactory inspection/transaction
preview and installation with both units inactive. Shared NuGet package/HTTP caches
prefetched on a network-enabled Linux system resolved restricted-network restores;
prefetch must match publish properties/multi-RID graph. No TLS/audit relaxation or
system identifiers/raw output persisted. Runtime/configuration/hook/data/shutdown
acceptance remains pending. Corrected one remaining obsolete framework-dependent
warning in the canonical packaging guide; documentation-only follow-up on same branches.

## [2026-10-25] verification | Bounded RHEL 9 capture, shutdown and downstream smoke

Operator reports host-only/normal startup, process with Stop, basic single-path file,
independent bidirectional same-host TCP identity/endpoints and clean shutdown with no
active files. Pidstat remained inactive and protected data permissions unchanged.
Supplied fresh DBT summary passes 40 models/42 tests/one hook: 83 pass, zero warnings,
errors or skips; engine 1.5.6/adapter 1.9.6/core 1.12.3. Shared official extension
prefetch must INSTALL both httpfs/parquet and use connection-time config_options,
not late settings; failed attempts retained locally, TLS/signature checks intact.
Updated verification, runtime plan and index. No raw output, host identifiers or
system-specific details persisted; generated evidence remains protected/local-only.
Full release/provenance/strict-count/multi-day and other platform/mode gates stay open.

## [2026-10-25] code | Independent periodic Linux stimulus and ground-truth runner

User approved open-ended disposable-host collection, manual stopping and a separate
tmux signal generator on each host; SmokeTests dashboard suffices for ground-truth
analysis. Added Analytics validation/telemetry-soak runner: named process/file/IPv4
TCP/UDP and same-host TCP selectors, existing raw_smoke_test export and private local
JSON/logs, sequential rounds/timeouts, same-root flock and failure continuation.
No collector management, credential/security changes, retention deletion or sibling
code edits. Clarified WINTAP_DATA_ROOT/explicit smoke-data-root (not DATA_PATH),
successful-upload local deletion, stimulus-only outcomes and deferred DBT integration.
Added canonical tool page and updated index/implementation/verification. Eleven
mocked tests, bash syntax and diff checks pass; native pilot/Garage evidence arrival,
signal/timeout and long-running behavior remain pending. No host identifiers or
generated evidence committed; test fixtures are synthetic.

## [2026-10-25] code | Read-only Garage/S3 SmokeTests dashboard source

User selected direct Garage access on the same feature branch and reports one runner
pilot completed, uploader working and smoke evidence reaching S3. Added private
JSON config (credentials rejected), AWS env/profile chain, temporary in-memory
DuckDB secret, path-style listing/reads, connection-time extension cache, inclusive
UTC day pruning, pagination, fail-closed caps and sidebar refresh/source selection.
No object mutations, credential persistence, local dataset sync, collector/uploader
or sibling changes; TLS/signature checks retained. Existing manifest/host/run/triage
semantics and mounted/local mode preserved. Forty-two backend/query/Streamlit tests
pass in an isolated temporary environment; one real synthetic loopback HTTP/S3 test
passes GET/HEAD listing/range-read/ground-truth join after correcting secret syntax.
Actual Garage dashboard validation and long-duration acceptance remain pending;
DBT manifest integration deferred. Updated canonical docs/index/plans/verification.
No real identifiers, credentials, endpoint/prefix configuration or host output filed.
Final suite including real loopback HTTP transport: 43/43 pass; Python parse/diff
checks pass and local config ignore is verified. Commit/push remains on the existing
feature branch; no PR publication.

## [2026-10-25] code | Non-interfering canaries and lazy Streamlit pages

User narrowed recurring scope to canaries that do not interfere with the deployed
sensor, and requested Overview, Canary Tests and Dev-time Tests pages. Expanded
Analytics runner to five distinct canary manifest families using generator-only
adapters: cross-domain, process lifecycle/short-lived, eight-file, optional native
clone and same-host TCP endpoints. Stop requirements are per PID; unsupported
Python execveat/native helper/kernel cases are explicit skips, not coverage claims.
No collector/service/security/tracer/uploader/sibling-code changes or host workloads.
Real Streamlit navigation separates canaries (including legacy stimulus-only runs)
from manual dev-time qualification. Overview reads manifests only; explicit selected
validation materializes one exact-selector working set for reused checks/details,
with fail-closed 100,000-row/256-MB limits and spill disabled. Hidden overlaps,
evidence hashes/conflicts and conservative missing/stimulus-only triage retained.
Native pushdown/partition pruning, passive HOST correlation and cross-rerun caching
remain follow-ups. Local tests use synthetic fixtures/mocked generators; native
expanded canary and live Garage page/validation acceptance remain operator gates.
Private config/profile/credentials/identifiers and live investigation outputs were
not persisted. Updated canonical pages/index/implementation/verification records.
Final checks: 51 dashboard tests (including synthetic real HTTP/S3 transport) and
17 mocked runner/adapter tests pass; shell syntax, Python parse and diff checks pass.
Same feature branch; no PR or live acceptance claim.

## [2026-10-25] code | All-canary validation, passive runtime context and saved summaries

User requested all validations on uploaded canary evidence, one round action, HOST
runtime comparison and result persistence beside data. Added Analytics round metadata,
one bounded shared selector scan, all-family/case/skip/missing/violation summary,
temporal complete-startup context and optional unique inferred short/FQDN correlation.
Exact hostname mismatch initially excluded observations; inferred correlation finds
process lifecycle/Stop, eight-file and both TCP endpoint expectations with no reported
violations. Cross-domain server TCP Accept and UDP Receive remain missing; Network
reports running, so disabled startup does not explain them. Native clone skipped;
all stimulus-only family triage remains yellow. No strict-count/full-capture waiver.
Summary and latest pointer saved/read-verified in Garage's sibling analysis prefix,
not raw telemetry. Fingerprinted reuse, explicit stale warnings, integrity checks,
verified atomic/private local writes, Git/symlink rejection and visible save failures
added; no source configuration/credentials/raw rows in summaries, no private local
investigation artifacts or identifiers committed. Listings/evidence reads still repeat;
no atomic storage snapshot or delivery watermark claimed. 75 dashboard tests including
real synthetic S3 transport and 17 mocked runner/adapter tests pass; Bash/AST/wiki-link/
frontmatter/diff checks pass. Updated canonical tools/index/plans/verification.
No sibling source, service/sensor/tracer/security/SDK/DuckDB/default controls changed;
no running workload restarted or PR published. Operator new UI/multi-host/long-duration
acceptance and native/network coverage remain open. Same feature branch commit/push.

## [2026-10-25] analysis | Canary quality gaps and proposed corrections

Reanalyzed the existing five-family pilot read-only (65.78 seconds, no analysis
errors); no new collection round, raw-data mutation or summary overwrite. Broader
PID/time queries do not recover server TCP Accept/UDP Receive. Current CO-RE source
has no Accept emission call and reads UDP kernel peer context with a user-memory
helper; deployed-object hash differs from local build, so live causal linkage remains
provisional. Live UDP Send tuples have zero endpoint ports; TCP listener-like close
rows also have incomplete peer tuples. All eight file paths have required activities;
selected lifecycle identities have no placeholders/mismatches, but 13 repeated-Start
groups need Clone/Exec provenance classification, not automatic duplicate-birth flags.
Five entirely synthetic evaluator counterexamples expose per-path, lifecycle identity/
repeat/linkage and extra malformed endpoint blind spots. Recorded source-aware fixes,
operation/provenance contracts and separately authorized sensor/pilot sequence in
quality_followup_analysis; updated index, canonical dashboard limitations and handoff.
No private identifiers/configuration/raw rows or investigation payloads filed. No source,
package, service, tracer attachment, security, runtime pin or default control changes.
Capture gaps/native skips and all prior acceptance limits remain open.
Diff whitespace, modified content-page frontmatter/wikilinks and new live grounding
paths pass. Synthetic diagnostics are not committed regressions; no source test-suite
rerun or implementation acceptance claimed. Same feature branch; no PR publication.

## [2026-10-25] code | Strengthened canary quality assertions

User authorized recommended-order fixes and local VM iteration while away. Added
13 synthetic quality regressions and stronger per-path/lifecycle identity/linkage,
source-aware repeated-Start and all-bound network candidate checks. Expected protocols
no longer filter the scan; directed ports also retain malformed host-relative tuples.
Contradictions remain red; incomplete/unbound traffic remains yellow, with summary/UI
warnings and counts. Clone/Exec raw observations are preserved, never counted as
distinct births or deleted. Existing pins/defaults/strict dev-time gates unchanged.
Idle VM uses isolated DuckDB1.5.6/Streamlit1.66.1/boto3 environment; all 88 dashboard
tests pass including real synthetic HTTP/S3, zero skips. Updated canonical tool,
README/plan/verification. Field-host services, raw datasets and private configuration
untouched. Sensor-owned fixes/VM qualification follow separately on existing branch.

## [2026-10-25] code | Local network return correction and qualification

User authorized recommended-order Analytics/Wintap fixes and local VM iteration,
not field rollout. Wintap core Accept now emits at successful return with accepting
TGID/inbound tuple; UDP uses checked kernel pointer provenance and one successful
protocol-return owner per operation. Actual arm64 tests also exposed errno sign-
extension and post-return msg_namelen pitfalls; corrected. Original object fails
strict15-check matrix, corrected object passes; all12 tracers build, managed build
zero errors,159 shared network/receipt/identity/resolver/root tests pass. Added
version-gated operation/sampling/PID-filter receipt facts and distinct UDP client
mode/socket plus per-path activity expectations. Preserved pins/retry/security/
default-off experiments and strict count gates. Evidence remains VM-local. Initial
normal-ETL harness mistakes (receipt phase, evidence ownership) exposed; fresh pilot
review follows. Canonical network/runtime/named-workload/dashboard pages and umbrella
handoff/index/plan updated. Wintap instructions/audit stay in its developer_docs.

Final verification:93 dashboard/17 runner/12 Wintap Python/159 shared managed tests
pass; actual-object repeat15 checks pass. Normal-ETL five-family fresh VM pilot
delivers manifests and observes Accept/all four independent UDP cases, zero evidence/
analysis errors; exact UDP and dedicated TCP endpoint checks have no missing/violation
findings. Local summary integrity/reload/latest passes; raw size/mtime snapshot unchanged.
All triage remains yellow. New tension: normal ETL lowercases Linux file paths despite
complete per-file activities; existing non-Windows behavior is explicitly preserved
by its regression, so no silent case-fold proof or unreviewed compatibility change.
Process projection also omits source breadcrumbs; no command-line/schema mutation
to fabricate provenance. Partial TCP EOF/close tuples remain incomplete. Field
package/install/pilot, file-case and explicit source-column contracts are next gates.

## [2026-10-25] code | Approved greenfield process-source and file-case projections

User explicitly approved both prospective changes; greenfield development does not
require deployment/data migration. Wintap normal Start/Refresh parquet adds nullable
ProcessStartSource from bounded recognized producer Arguments breadcrumbs, not
CommandLine inference. FileSerializer preserves producer case and case-distinct
sensor file-key inputs; Windows behavior/identity formulas/pins/security/retry/default-
off controls unchanged. Analytics prefers explicit source with real Arguments fallback.
Linux build0errors/177warnings;180shared managed and94dashboard tests pass, including
production-schema null/mixed provenance parquet roundtrip and locale/case-key negatives.
Initial new test incorrectly indexed a deserialized null key; corrected assertion,
not writer. Fresh180-second normal-ETL VM pilot delivers five families with0evidence/
analysis errors and0violations. Eight-file/process/clone/dedicated TCP have0missing
checks; all selected repeats source-classify without extra-birth claims. Cross-domain
retains one Delete gap and two incomplete TCP provenance checks; all triage yellow.
Receipt contract2/copied hash, local summary/latest integrity/reload and raw size/mtime
preservation pass; VM collector/observer inactive. Resolved sensor file-case tension;
Wintappy's separate lowercase-derived file_id remains unmodified/uncertified. Updated
canonical process/file/dashboard pages, index, plans, verification and handoff. No
private evidence/identifiers/configuration filed; no Garage writes, field rollout,
Lintap/Wintappy edits or PR. Same feature branches; unrelated work preserved.

## [2026-10-25] review | Senior technical assessment before closing quality round

Reviewed current sensor/projection/generator/dashboard/persistence source and prior
qualification evidence at Wintap c0b6774 / Analytics00dda2d. Synthetic current-code
probes reproduce permissive legacy source parsing and suppression of a known endpoint
contradiction when another field is null. Existing VM pilot read-only investigation
finds the missing relative.bin Delete as a bare relative basename in the same
host/PID/window; unlinkat loses dirfd and managed relative resolution only covers Open.
Created advisor_review with bounded corrective bundle, sampling/churn qualification,
native target-package gate and separate downstream case-ID plan. Prior pass counts
remain scoped; no new collector run or implementation. No private raw evidence,
configuration or identifiers committed. Updated index/handoff; recommendations await
user direction. Temporary synthetic query artifacts removed.

## [2026-10-25] code | Advisory corrective bundle and later RHEL9 validation

User approved Ubuntu source/test implementation and preparation for later RPM
deployment. Fixed strict legacy source parsing (explicit null authoritative) and
known endpoint contradictions with null companion fields. Wintap relative unlink
captures operation-time dirfd/cwd base identity; learned-index-only resolution
preserves unknowns and entry-intent semantics. Added live case-only/cwd stimuli,
conservative directory-resolution regressions, monotonic/outer observer deadlines
and24-lifetime UDP turnover qualification. Network48turnover/15return checks pass;
no forced pointer reuse claim or network sampling change. Linux build0errors/
177warnings;171targeted managed,97dashboard,20runner/CLI and11Wintap Python tests
pass. Broader Ubuntu Windows-targeted suite1160pass/87fail and timed-out isolated
retry of8logging-dependent tests remain explicitly unqualified in verification.

Fresh normal-ETL five-family pilot has0errors/0violations; exact relative/cwd Deletes
and case-only activities/distinct sensor keys pass. All29focused receipt/hash/
projection gates pass; only two partial TCP provenance checks remain incomplete.
Actual collector exits0 without force. CLI summary integrity/latest/reuse verified
without analysis rescan; raw size/mtime/listing preserved. Prepared read-only RPM
payload verifier (synthetic tamper tests) and explicit delivered-round CLI with
strict0/1/2scoped outcome codes. RHEL9 execution/ongoing Garage and multi-host review
remain later steps. Updated canonical file/workload/dashboard pages, review/handoff,
plan/verification/index and new rhel9_validation. Wintap instructions/audit stay in
its developer_docs. No private raw/host/config/credential evidence, field rollout,
Garage writes, runtime-pin/security/default-control changes or Lintap/Wintappy edits.

Wintap source bundle committed as03114f6;15changed production/test files across the
two repos match the qualified VM snapshot byte-for-byte. Same feature branches;
unrelated state/configuration work preserved. No PR or merge.

## [2026-10-25] code | TCP EOF/close tuple attribution before RHEL

User explicitly requested fixing TCP before RPM deployment. State callbacks had
replaced complete cached tuples with teardown's zero local port and reset sampling
clocks. Corrected complete-only existing-entry refresh, connect reset and unconditional
close cleanup; state callbacks cannot resurrect closed entries. TCP requested-entry
byte meaning and one-second sampling retained. Strict10-check actual-object regression
fails prior object/passes correction, including delayed EOF, both connected closes,
separate peerless listener close and empty socket caches. Final48turnover/15return
regressions also pass. SDK10.0.402 build0errors/177warnings;171managed,97dashboard,
21runner/CLI,7network-oracle tests pass. Seven changed production/test sources match VM.

Two fresh normal-ETL pilots, including final rebuilt managed/object pair, have0errors,
0missing checks/violations across five families and34passing receipt/hash/projection
gates. Both TCP provenance checks resolved. Final collector exit0 unforced in184seconds;
collector/observer/testhost inactive. Matching summary reuse/raw-snapshot preservation
pass. CLI remains2/yellow for independent execveat/native-helper skips and repeated-
Start count caveats. Added marker-gated TCP tuple contract1/lifecycle-hook receipt
and required it in later RHEL validation. Canonical network/receipt pages, index,
handoff/plan/verification/procedure updated; private evidence stays outside commits.
Native RHEL package validation and prior broader limitations remain open.

Wintap correction committed/pushed as `c4f6b1d`; Analytics validation/wiki companion
uses the same feature branch. Unrelated working-tree changes remain preserved.

## [2026-10-26] handoff | RHEL canary continuation

Refreshed the telemetry identity/data-quality feature status for computer transition
and replaced the stale dev handoff with a current continuation guide. The user reports
a newer native RHEL package deployment; two completed S3 rounds show declared endpoint,
file and process checks passing, with helper-dependent dedicated clone coverage. The
three-source provenance gate remains incomplete because `sched_exec` was not observed
despite the startup hook being reported attached. Two additional parallel overnight
rounds await stop, upload settlement and separate review; package-to-installed-payload
proof is not recorded. Updated brief, plan, verification, RHEL/network/runtime notes
and index. Persistent updates omit host identifiers, private storage configuration,
raw events and detailed runtime telemetry. No close-out or release claim; no source
changes or S3 writes.

## [2026-10-26] code | Resolve Wintap develop merge conflicts

User-approved merge of develop `c670c26` into the telemetry feature recorded as
Wintap `5afd320` (local, not pushed). The squash tree equals feature ancestor
`c951d21`; retained feature identity, clean state publication and DuckDB1.5.6.1
while removing a silent duplicate supply-chain/version property group. Declared
standalone MCP's Windows/Linux/macOS-build-host RID graph and regenerated its
lock after reproducing NU1004. SDK10.0.402 locked restores and managed builds pass;
113focused managed and6runtime-alignment tests pass. Native/package/runtime
qualification remains separate. Updated verification, plan, handoff and canonical
repo build note. Unrelated local state and untracked work excluded from the merge.

## [2026-10-26] code | Refresh Multipass development provisioning

User authorized Lintap script updates and a fresh development VM. Both launchers
now use qualified SDK10.0.402/CLI-Python DuckDB1.5.6, strict shared dependency
checks, running-kernel BPF tools, guest-native Python/build paths and updated
branch/build examples. Fresh Ubuntu arm64 creation and cloud-init pass; .NET build
has0errors/178warnings; forced rebuild compiles all12 tracer objects.24 packaging/
provisioning regressions pass on host and guest;5 validation-harness tests and its
synthetic mock command pass in the guest. Bash syntax, PowerShell AST and cloud-init
semantic parity pass. Updated Multipass guide, canonical repo page, feature plan/
verification and index. Live sensor/package acceptance is separate.

User subsequently reported successful Debian package builds and authorized
commit/push of the provisioning changes and companion wiki notes. This is
operator-reported build success; package installation/runtime results were not supplied.

## [2026-10-27] docs | Cross-platform package release versioning

Created `wiki/workflow/package-release-versioning.md` with a concise 7.0 release
identity, Debian/RPM/MSI field mapping, shared build-number versus packaging
revision guidance, architecture/EL suffix handling, and build-to-install checklist.
Recorded the selected Debian tilde and current RPM underscore beta encodings;
called out target RPM ordering verification and the still-undefined beta counter
sequence before automation. Linked SemVer, Debian Policy, live Wintap/Lintap
release/build docs, and the page from the index. Documentation only; no source or
release configuration changed.

## [2026-10-29] feature-plan | fix-pidstat-collector Go rewrite

Human reported RHEL 8 sudo bootstrap failure because root lacks uv and accepted a
compatibility-preserving Go binary rewrite rather than requiring root uv installation.
First live validation target explicitly changed to existing Multipass lintap-dev,
Ubuntu arm64; RHEL 8/amd64 runtime proof remains separate. Created brief, staged
implementation plan, authorization-gated dev handoff and pending verification record;
linked from index. Planned pure-Go Parquet/static-build spike, sampler/spool parity,
Debian/RPM integration and bounded implement/test/review/repair loop for a later
OpenCode session. Expected local Wintappy source unavailable; consumer proof pending.
No source/configuration/VM/service changes, tests or automation setup. Existing
untracked .claude work preserved. No new contradictions; sealed estimates not collected.

### Follow-up — renamed downstream checkout and real Python parity gate

Human identified Wintappy's renamed checkout as `../Wintap-PyUtil`; read live pidstat
bronze and shared path/raw-source macros and corrected current feature references.
Strengthened acceptance/plan/handoff/verification to require actual Python-produced
data, exact replay on identical captured real /proc inputs, paired-live comparison
with predefined skew tolerances, and review of all columns, row multiplicity and
unmatched cases. Retain revision-pinned Python reference through acceptance; fixtures
alone cannot close parity. No code/tests/VM changes or comparison execution yet.

## [2026-10-29] code | Prepare bounded pidstat OpenCode runner

User authorized runner/supporting files in Analytics, not collector implementation.
Added Bash/Python external controller, fail-closed verification template, dedicated
fresh implementation/report-only review profiles, private ignored state/logs, finite
attempts, cumulative deterministic gates and candidate/evidence-bound human fpc-01
approval. Config/contracts/check entry points and approved source scope are pinned;
out-of-scope/reviewer mutations stop without reverting work. Explicit one-unit launches,
no continuation/auto-approval/push/field rollout. Checked local OpenCode v2.0.32 help
and official V2 docs;15 offline fake-agent tests, Bash syntax, diff check and ignore
checks pass. Added canonical tool page; updated feature plan/handoff/verification/index.
No actual model sessions, collector code, VM/package/service changes or parity runs.
Real gate wiring, Lintap/VM authorization and effective permissions still required.
Timeout remote-work cancellation is explicitly manual; no automatic uncertain retry.
Existing untracked .claude work preserved; no commit/push.

## [2026-10-30] diagnostic | RHEL 8 Lintap SELinux S3 upload denials

Documented the operator-reported local `lintap-selinux` policy and AVC evidence:
`init_t` TCP `name_connect` to Garage port 3900 and `var_log_t` directory `rmdir`
for raw_sensor partition cleanup. Added the bounded auditd/ausearch workflow,
custom port-type policy build/install steps, scope cautions, and live Wintap/Lintap
source references. Linked the diagnostic from the index. This host-local policy
is not confirmed as part of the canonical Lintap RPM; no sibling-repo changes.

## [2026-10-30] docs | Root-owned smoke workload to S3 operator workflow

Reviewed existing Wintap devtools, Analytics dashboard/soak, packaging/path docs and
live publisher/uploader code. Durable export and sudo interpreter handoff already
existed in separate guides; consolidated the complete one-shot workflow into
`wiki/tool/named-telemetry-smoke-workload.md`. Added root-path discovery, user-side
uv/DuckDB interpreter selection, sudo import check, fresh output/portable manifest,
explicit smoke-data-root, publication/delivery/validation checkpoints and failure
triage. Linked from dashboard/soak pages and index. Clarified workload-only privileges
versus protected parquet export and replaced ambiguous temporary-path advice.
Flagged a soft guidance mismatch: runner README's runtime-root evidence example
also hosts file stimuli, whereas shared workload guidance excludes runtime paths;
the wiki now recommends an external QA root. Source-owned README left cited in place.
Verification: `git diff --check` passes; `bash -n` passes for seven documented shell
blocks; three page frontmatters, 19 wikilinks and the workflow's live source paths
check successfully. Root field-host execution and S3 arrival still require an
operator run; no new capture result claimed.

## [2026-10-30] correction | Persistent smoke Python environment for sudo

Operator attempt exposed a flaw in the preceding documentation: capturing
sys.executable from `uv run --no-project --with ...` returned a temporary
`builds-v0/.tmp.../bin/python` that sudo could not execute after uv exited.
The workload did not launch. Replaced that recipe with user-side `uv venv` in a
named persistent directory, explicit `uv pip install --python` and direct sudo
invocation of the venv interpreter. Added reuse/troubleshooting notes and corrected
dashboard/soak/index pointers. Official uv environment docs and installed CLI help
confirm the creation/install syntax; root field-host publication/S3 validation
remains pending an operator rerun. This supersedes the earlier interpreter recipe.
Checks: named-venv creation followed by a separate direct interpreter invocation
passes locally after uv exits (temporary wiki-local environment removed); seven
documented shell blocks pass `bash -n`, local wikilinks and `git diff --check` pass.
This local check used the available host Python and did not install DuckDB or run sudo.

## [2026-10-30] docs | Live-collector validation diagram

Added `wiki/workflow/live-collector-validation.drawio` with two editable pages:
data/evidence flow and operator workflow. Proposed “live-collector validation” for
the in-situ workflow, with repeated bounded stimuli called telemetry canaries.
The diagram shows persistent user-created venv → sudo workload, independent normal
sensor capture, local raw_smoke_test publication, shared collector S3 upload and
explicit dashboard checks. Added a source-anchored companion page and links from
the named-workload, soak and dashboard pages plus the index. Preserves distinct
generation/publication/delivery/validation checkpoints and stimulus-only limits.
Verification: imported both pages into diagrams.net and visually reviewed layout;
adjusted the expected-activity edge label to clear box borders. XML parsing,
unique cell IDs, edge endpoints and page bounds pass. Required frontmatter and
live source paths pass for the four topic pages; 245 wikilinks across those pages
and the index plus the companion diagram link resolve. `git diff --check` passes.

## [2026-10-30] docs | First-time Streamlit S3 setup

Operator feedback identified the missing analysis-machine setup handoff. Expanded
the dashboard wiki page with a first-time quick start: copy/edit the private JSON,
map an uploaded raw_sensor object to its dataset root, select AWS credentials,
launch Streamlit with uv and open port 8501, then discover and validate the run.
Linked it directly from the named workload, live-collector workflow and index;
updated diagram P7 to make configuration/launch explicit. Grounded in the live
app, S3 config parser, example config, requirements and README.
Verification: four dashboard shell blocks pass `bash -n`; documented JSON matches
the shipped example and is accepted by the live config parser; dataset-root
mapping, wiki/Markdown links and section anchors, updated diagram XML and
`git diff --check` pass. No authenticated S3 session was exercised for this doc update.

## [2026-10-30] code | Replace pidstat controller with native OpenCode workflow

At human request, removed the first-pass external runner, configuration template,
launcher, fake-agent tests and custom profiles. Supersedes the 2026-10-29 runner
entry; its results remain history only. Added native `/pidstat-loop`, bounded skill,
separate-session `/pidstat-review` prompt and deterministic evidence utility for
actual Python capture, exact Parquet comparison, ELF checks and narrow root startup.
OpenCode owns iteration; default three candidate revisions/60 minutes, human pause
after fpc-01, no approval tokens or external state machine. Updated canonical tool
page, README and feature brief/plan/handoff/verification/index; real-Python parity
and Ubuntu arm64 first-target requirements retained. 19 offline tests pass, including
actual Python sampler/writer with controlled inputs, not live Python/Go acceptance.
Recorded test-command evidence, CLI help, source/link/frontmatter/ignore checks and
`git diff --check` pass. Collector implementation, VM work and DBT remain unstarted;
no sibling edits, dependency installs, commit or push. Unrelated work preserved.

## [2026-10-30] code | fpc-01 static Go writer feasibility checkpoint

Human approved scoped Lintap spike and isolated existing Ubuntu arm64 lintap-dev
experiments, plus private pinned DuckDB reference venv. Added unpackaged writer-only
Go1.27.3/parquet-go0.32.0 module/tests/Makefile/docs in `../Lintap/pidstat-go` and
Analytics bounded workload/supplemental actual-Python writer check. Python source
remains unchanged/hash-pinned. Actual live Python captures266/705/1640 rows compare
exactly against Go: all26 columns, physical-column/DuckDB schema, nulls, multiplicity,
partitions/windows, zero unmatched rows/error. Both cgo-disabled Linux ELF builds are
static and reproduce hashes; native root restricted-PATH arm64 startup and1640-row
encoding pass. Five Go tests/vet/module verification, five controlled writer rows and
19 utility regressions pass. Workload observed203.29%CPU, memory/writes and10churnPIDs;
cached reads and missing live container runtime IDs are explicit coverage gaps.
Updated verification/checklist/handoff/brief, canonical repo/tool pages, README/index.
Same-session inspection only; stopped for human review before fpc-02. Sampler,
recovery/configuration, package/service, paired-live, DBT and native RHEL/amd64 remain
pending. No production data/service/package changes, consumer edits, commit or push;
private guest artifacts/evidence retained and unrelated work preserved.

## [2026-10-30] code | fpc-01 approved; fpc-02 sampler/configuration checkpoint

Human approved fpc-01 and requested continuation. Added injected Go proc sampler,
Linux config resolution, native kernel AT_CLKTCK/page discovery, strict raw replay
and bounded diagnostics in Lintap. All3real raw captures reproduce Python TSV and
26-column Parquet exactly (266/705/1640rows), with no unmatched rows/schema errors;
native arm64 raw replay passes. Actual Python controlled52-row fixtures pass at
100Hz/4KiB and250Hz/16KiB;17config cases match;14Go tests/vet/modules/static builds,
5writer rows and19utility regressions pass. Native four-sample run emits411readable
rows, not paired-live qualification. Retained two failures and repaired numeric/path
config fidelity and sub-microsecond midnight rounding/source-window provenance.
Declared malformed-counter per-process skip, bounded cache and monotonic-live-time
differences; valid math/missing optional defaults unchanged. Candidate3of3, stopped
at technical completion/review gate before fpc-03. Updated verification/checklist,
handoff/brief, canonical repo/tool/index and READMEs. Same-session inspection only;
durable spool/recovery, package/service, DBT, paired-live and native RHEL/amd64 remain
pending. Frozen Python/consumer sources unchanged; no shared service/data/package
changes, commits or pushes; private guest evidence and unrelated work retained.

## [2026-10-30] code | fpc-02 approved; fpc-03 durable pidstat checkpoint

Human approved fpc-02 and requested continuation. Added explicit Go collector/recovery/
durable raw-replay modes with legacy TSV/meta, seal/publication journals, exclusive
spool lock, unique active ownership, synced no-overwrite publication, retained failed
inputs, collision/compression handling, scoped caps and signal seal. Exact durable
replay of266/705/1640real Python rows passes all26columns/schema/multiplicity/windows;
actual Python-produced legacy current/pending/missing/invalid-meta spools recover
exactly.26Go tests/vet/modules/static builds and native arm64 fault tests pass;
native SIGTERM/SIGINT each produce411rows/2files, SIGKILL restart recovers137rows,
destination obstruction retries20unchanged-input rows and competing spool lock fails.
Sampler/config/writer/19utility regressions stay green. Retained failures; repaired
legacy suffix/codec coverage, a case-insensitive fixture-path issue, and shared-output
active ownership before final pass. Original host pytest command blocked (not installed),
not counted as PASS. New tension page documents publication/uploader receipt gap:
at-least-once, not exactly-once delivery; full power-loss/resources remain unqualified.
Updated feature/canonical pages, README/index and verification; candidate3of3 stopped
for review before package/service work. Same-session inspection only. Python/consumer
sources, shared services/data and unrelated work unchanged; no commit/push/deployment.

## [2026-10-30] verification-start | Four-hour Go pidstat and latest Lintap VM soak

Human requested four-hour sensor-on qualification before packaging. Existing Ubuntu
arm64 lintap-dev had no installed/running sensor. Built current Wintap66d8297 source
archive natively (12tracers;0managed errors), started normal ETL with isolated retained
data, then unchanged hash-matched fpc-03 candidate3 at default5s/300s. Run begins
2026-10-31T05:18:50Z, planned stop09:18:50Z. Existing recurring five-family smoke
runner reuses persistent DuckDB1.5.6 environment and prebuilt native helper; first
round5/5exit0/recorded. FileOps partial legacy-hook and absent SELinux limits retained.
Added scoped supervisor/inspector automation;30s resource/health records, bounded
SIGTERM seal/drain, pidfd-blocking background retrieval and hash-checked safe extraction.
Native inspector pilot checks1788actual Go rows against actual Python26-column schema
and correctly rejects incomplete-run metadata. Scripts compile; diff check passes.
Startup-log discovery failure retained/repaired before sampling. Preflight make run-env
implicitly built/restored the shared checkout and rewrote a previously modified
WintapAPI NuGet lockfile; original diff unavailable, no restoration claimed. Subsequent
build used isolated archive; no collector/package/source implementation revision.
Updated feature verification/checklist/handoff/index. RUNNING, not PASS; full review
awaits completion. No package install, shared service restart, consumer edits or commit/push.

## [2026-10-31] verification | Four-hour Go pidstat VM data collected and reviewed

Completed14400.022s sensor-on default5s/300s run; smoke/Go/Lintap each exit0, no
forced shutdown. All49pidstat files decode399312rows matching all26Python schema
columns/physical types;2880sample times with uninterrupted5s gaps, contiguous300s
windows including midnight,0duplicates/placement errors, clean final6484-row seal.
16five-family rounds80/80exit0/recorded;436sensor/manifest files readable. Go median
0.47%of one core and16.97MiB RSS, peak44.86MiB; four-hour memory medians stabilize
around17MiB, not general leak or Python resource-improvement proof. Sensor partial
FileOps/absent SELinux/disabled adapter-resolution/parent warnings retained; no full
capture or upload acceptance claimed. Initial SFTP failed on root-private parent;
private archive copy fixed transfer without changing original permissions. Hash
verified archive and safely extracted969files; guest/failed evidence retained.
Secondary DuckDB CREATE VIEW binding failure retained and read-only query repaired.
Created feature soak_review and updated verification/checklist/handoff/index. Scoped
same-session collection check passes; human review/packaging, paired-live Python,
comparative resources, DBT/original pytest and native RHEL/amd64 remain pending.
No collector revision, package install, consumer edits, commit/push or deployment.

## [2026-10-31] code | Source-aware local/S3 DBT preflight

Human approved scoped implementation in `../Wintap-PyUtil`. Make now validates
effective raw input instead of requiring output-root/raw_sensor; S3 needs a valid
URI/explicit dates, not a local placeholder. Local split-input date discovery,
date/hour/output checks and raw-source printing added. DBT/DuckDB operation lists
current bronze event/alias partition prefixes and reads one sample schema before
build; missing optional events allowed, empty supported-input window/access/TLS/
corrupt sample fail. Dashboard checks remain local-only.39new tests including real
DBT and loopback S3 protocol fixtures;248focused tests pass. Broader suite272pass/
1unchanged legacy Dynaconf-default failure, independently reproduced. Initial
Make/test-setup failures fixed; event wildcard narrowed to avoid broad S3 listings.
Updated PyUtil README and canonical wiki; created plan/verification and index entry.
No live S3 requests, operator dataset/env edits, collector changes, commits or pushes.

### DBT source-validation follow-up — operator confirmation and commit authorization

The human reports the new checks work and authorized topic commits on
`work/pidstat-and-dbt-validation`. Recorded this confirmation in feature verification;
it does not substitute for an agent-inspected real-host DBT qualification.

## [2026-10-31] review | Pidstat checkpoint prepared for topic commits

Human authorized grouped commits on working branches across the repositories.
Corrected stale default-cadence/resource and authorization wording; retained
fpc-03/package/paired-live/native acceptance boundaries and all collector code/pins.
19utility tests pass with existing PyUtil Python/DuckDB;10harness sources parse.
Go test rerun is blocked: retained temporary Go1.27.3 cannot locate its standard
library, so no fresh Go test/vet pass is claimed. Existing evidence remains intact.
Private datasets, captures, generated artifacts and local settings remain uncommitted;
the clean nested PyUtil checkout and generated/editor-only Wintap dictionary tree
are not source changes. No live host, package or S3 operations performed.

## [2026-10-27] feature | WindowsShell ETW replacement

Replaced the console-history helper/polling path with default-disabled Microsoft.Windows.Console.Host ETW collection after operator-confirmed LocalSystem prototype success. Reduced the modeled payload to CommandText, SessionId and StartTime, retaining canonical process attribution and dynamic Parquet integration; removed obsolete helper/IPC/config/tests. SDK 10 build, 62 focused tests and 380 nearby regressions pass, including production Parquet roundtrip. Live capture exposed timestamp-skew attribution drops; corrected lifetime validation preserves canonical joins and requires fresh OS verification for bounded differences. Feature documentation remains compact and sanitized. Updated self-contained Windows x64 output is published locally; integrated service/session coverage, live joins, performance and shutdown acceptance remain pending in [[wiki/work/windows-shell/verification]].

## [2026-10-28] feature | PowerShell ETW POC

Opened a native-ETW shape POC for 5.1/7; built and tested a temporary wrapper (35 tests), repaired `-File` path initialization, inspected 5.1 events including interactive `write-host hi`, and added 4104-only output while retaining originals and unchanged collection/loss. The 60-second sample had 89 lost events and five incomplete blocks; the operator reports the focused rerun works, but its new data and formal POC acceptance remain unreviewed. Findings/audits: [[wiki/work/powershell-sensor/findings]], [[wiki/work/powershell-sensor/P0.2-focused-scriptblock-output]]. Logging policy stayed unchanged; integration remains separate.
## [2026-11-03] docs | Queue medium-priority ETL DuckDB instance reuse

Added `wiki/work/reuse-etl-duckdb-instance/brief.md` as a deferred future fix and
linked it from the index. Proposes an ETL-owned long-lived instance, separate from
the resolver, with serialized access, explicit disposal/recovery, unchanged parquet
semantics, matched fresh-versus-reused CPU measurements, and bounded memory/resource
soaks. Benefit and RNG-contention relevance remain unproven; no implementation
approval, source changes, raw telemetry, host identifiers, or deployment.

## [2026-11-03] research | Future scheduler lifecycle vs syscall observations

Created `work/lintap-process-creation-validation/future-scheduler-lifecycle-vs-syscalls.md`
and `tension/linux-process-lifecycle-vs-exec-attempt-observations.md`. Read current
Linux Clone/Execve/Exit producers and callbacks on clean Wintap `develop` at
`c29f973`, plus upstream Linux v6.12 tracepoint definitions and fork/exec/exit paths.
The Linux sensor already uses all three scheduler hooks alongside exec syscall
entry; Windows uses ETW. The topic compares successful lifecycle transitions with
attempt/argument visibility, ordinary vs raw/CO-RE enrichment, duplicate Start work,
thread-group exit and non-leader exec, with a bounded fidelity/performance spike.
Kept the inspected develop baseline separate from dated October feature-branch
evidence, including differing start-time ABIs and unresolved RHEL sched-exec
provenance. No hard contradiction asserted across those distinct snapshots.
Updated index, research-thread navigation and process-event cross-reference.
Performance benefits and schema choices remain hypotheses; no live benchmark run.
Verification: `git diff --check` passed; targeted documentation validation found
all required frontmatter on both new pages, 12 existing local source anchors,
249 resolving wikilinks across checked pages and inbound links to both new pages.

## [2026-11-04] docs | Priority to-do intake for Linux executable attribution

Added `wiki/todo/` as a reusable intake queue for emerging bug, data-quality, and
enhancement findings, with a lightweight priority/lifecycle guide and a P1
finding for nondeterministic silver process executable attribution. Grounded the
issue in current Wintap exec provenance and Wintappy's independent `any_value`
selection; linked the existing validation design and process-lifecycle tension.
The finding remains an intake item: no model choice, feature brief, source-code
change, or implementation authorization was made.

## [2026-11-04] docs | Add Lintap process command-line quality to-do

Added `wiki/todo/lintap-linux-process-command-line-quality.md` and listed it in
the priority queue and master index. Preserved the human-reported focused-VM
counts and marked the database/raw-data analysis as not independently
recomputed for this intake update; verified the cited artifact paths exist.
Grounded the sensor and dbt behavior in live source, linked the related
executable-attribution to-do, and retained the proposed contract, implementation
approach, verification matrix, acceptance criteria, and unresolved decisions.
No sensor, schema, dbt, or raw-data changes were made.

## [2026-11-04] feature-work | SELinux DBT pipeline definition

Pages created: `wiki/work/selinux-dbt-pipeline/{brief,references,design,implementation_plan,verification}.md`
Pages updated: `wiki/index.md`
Contradictions flagged: none.
Notes: Added a separate DBT-only work definition beginning at the existing SELinux raw-sensor parquet boundary. It covers optional bronze models, family-specific silver models, gold summaries, constrained exact-or-temporal process attribution, and validation of counts, timestamps, contexts, and no-data behavior. Existing producer-side SELinux monitoring work remains separate; no source code or raw documents were changed.

## [2026-11-04] implementation | SELinux DBT pipeline

Implemented the SELinux DBT pipeline in `../Wintap-PyUtil` on
`feature/selinux-dbt-pipeline`: optional AVC, interaction, and transition bronze
models; native-grain silver normalization; bounded process attribution; gold
detail/context/family/process summaries; quality monitoring; source validation;
and schema/count/timestamp tests. The supplied sample passed `make dbt-build`
(`PASS=137`, `ERROR=0`) and `make dbt-test` (`PASS=83`, `ERROR=0`); the dataset
without SELinux directories also passed the full build. Updated the feature
implementation and verification records with counts, duplicate/EventCount
deviations, context completeness, and attribution outcomes. No sensor files were
changed and unrelated Wintap-PyUtil untracked files were preserved.

## [2026-11-04] dashboard | SELinux QA views

Added a first-cut SELinux page to the Wintap-PyUtil QA dashboard. It summarizes
family coverage, duplicate/row-retention quality, producer EventCount, context
completeness, attribution outcomes, host/time scope, and hourly volume, with
paginated context, AVC, interaction, transition, and process-attribution detail
views. The page handles databases without the optional SELinux relations and
exported successfully against the supplied sample DuckDB build.

## [2026-11-05] docs | Listening-socket capture and modeling to-do

Added `wiki/todo/listening-socket-capture-and-modeling.md` and linked it from the
to-do queue and master index. Grounded the intake in the Linux socket-state
tracepoint, shared Wintap activity contract, and current Wintappy network models;
preserved the distinction between listener close and accepted-connection close.
Priority, platform scope, event semantics, and model shape remain undecided. No
sensor, schema, or DBT implementation changes were made.

## [2026-11-05] docs | Canonical process-owned network-grain to-do

Added `wiki/todo/canonical-process-owned-network-grains.md` and linked it from
the to-do queue and master index. The intake records the documented increment
key versus current silver grouping, proposes explicit connection/activity
grains and a separate network-observed process identity relation, and requires
conflict visibility plus counter/bounds regression checks. No schema or DBT
implementation changes were made; existing uncommitted wiki edits were
preserved.

## [2026-11-08] docs | Transformer five-tuple connection-key to-do

Added `wiki/todo/transformer-five-tuple-connection-port-key.md` and linked it
from the to-do queue and master index. The intake records the apparent
`HiIPPortInt`-for-both-ports argument at `Transformer.cs:37`, grounded against
the separate low/high tuple properties and key-generator inputs. Collision
impact, intended compatibility, and persisted-ID implications remain
unverified. No Wintap source, schema, or raw documents were changed.

## [2026-11-09] code | DBT named AWS profile selection

Updated Wintap-PyUtil's S3 secret macro to pass `AWS_PROFILE` explicitly as a
DuckDB `credential_chain` profile and added loopback-S3 coverage proving the
selected profile signs requests. Direct `make dbt-check-source` then passed with
the named profile after exporting that profile's configured endpoint URL and
matching TLS; the probe listed one requested-window Parquet file and read its
schema. Updated the pipeline README and wiki guidance. The focused DBT/SQL
regression set passes 249 tests; no full DBT build was run.

## [2026-11-10] docs | Linux process name `exe` fallback to-do

Added `wiki/todo/linux-process-name-exe-fallback.md` and linked it from the
priority queue and master index. Preserved the user's report against the reviewed
DuckDB as unverified data evidence; source review confirms a plausible path where
an unresolved `/proc/<pid>/exe` path is basename-extracted as `exe`, but does not
confirm that path produced the reviewed rows. Recorded row-lineage validation,
producer regression, downstream quality checks, and evidence-backed historical
repair as follow-up work. No sensor, DBT, schema, or data changes were made.

## [2026-11-10] docs | Linux process attribution on NFS network tuple

Inspected the local example DuckDB read-only. One shared NFS TCP five-tuple has
129 rows, including one 264-byte send attributed to `ssh`; the same process has
a separate port-22 SSH connection. The user confirmed that the home directory
is mounted from the NFS device. The same SSH process has 14 home-path
`PROCESS_FILE` rows across six paths under `.ssh` in its six-minute run, but a
nearby Delete row's `min_event` is about five seconds later than `first_seen`,
so exact timing remains unresolved. A roughly 19-hour endpoint-wide summary has
1,619 rows, 254 five-tuples, 770 process hashes, 64,773 network events, and
about 9.6 MB reported; 404 process hashes intersect file activity and 38 have
home-path activity. Seven SSH hashes have 80 `.ssh` rows and 226 file events.
The process mix is plausible for mounted-workload and scanner activity, but the
large generic `exe` bucket and aggregation grain need qualification. Updated
`wiki/todo/linux-nfs-process-network-attribution.md` with anonymized, cursory
findings, the timestamp caveat, and a controlled-reproduction plan. Removed
identifying local database paths and specific user, host, network, PID, and
connection identifiers from the affected TODOs and this entry. No database,
sensor, or DBT changes were made.

## [2026-11-10] feature-work | recent-host-activity-dashboard opened

Completed the adaptive interview and created `wiki/work/recent-host-activity-dashboard/`
artifacts: interview, brief, references, design, spike, implementation plan,
developer handoff, and verification. Confirmed a standalone read-only
Streamlit/DuckDB dashboard over S3 bronze raw rows, rolling 12-hour UTC window,
manual refresh, day/hour partition pruning, event-family selection with host
series, adaptive buckets, and explicit linear/log plus normalized-to-host-peak
views. Families without usable row-level hostname/time are to be skipped and
reported; no universal logical-event count is claimed.

Source review of `../Wintap-PyUtil/wintap_dbt/` confirms the canonical
`<dataset>/raw_sensor/<event_type>/dayPK=YYYYMMDD/hourPK=HH/` layout, optional
nested `protoPK`, and S3 partition-pruning conventions. Analytics SmokeTests
already demonstrates direct read-only DuckDB/S3 access. Neither source identifies
the user's actual bucket roots or live schemas; an operator-configured bounded
S3 pilot remains open. No AWS access, code changes, or sibling-repository writes
were performed. Human estimate values were not supplied.

## [2026-11-10] implementation | recent-host-activity-dashboard

Implemented `streamlit/projects/HostActivity/` as a standalone read-only
Streamlit/DuckDB app. It reads the existing DBT dataset/AWS environment
variables but does not invoke DBT; it discovers only supported event/day/hour
partitions, coalesces compatible host/time aliases across schema drift, applies
exact 12-hour UTC bounds, and fails closed on object/row/point budgets. The
chart supports event-family and host selection, adaptive buckets, linear/log
counts, and per-host-peak normalization. Launch docs, requirements, 15 offline
tests, verification notes, and [[wiki/tool/recent-host-activity-dashboard]]
were added/updated. Focused tests and compile checks pass under DuckDB 1.4.4;
the target DuckDB 1.5.6/Streamlit UI stack and real S3 were unavailable, so live
roots, schemas, and a real app render remain unverified. No AWS access, DBT run,
source/schema/raw-file changes, or sibling-repository writes occurred.

## [2026-11-10] verification | recent-host-activity-dashboard UV setup

Replaced the pip requirements file with an app-scoped `pyproject.toml` and
`uv.lock`, updated launch/test instructions to UV, and synced DuckDB 1.5.6,
Streamlit 1.67.0, Altair 6.3.0, and Pandas 2.3.3. Altair 6 resolved a Python
3.14 incompatibility found during `AppTest`; the initial app render passes and
does not query before manual refresh. All 16 focused tests, compileall, lock
check, and `git diff --check` pass. Updated verification/handoff/index/tool docs;
the bounded live S3 pilot remains pending. No S3 access was attempted.

## [2026-11-10] optimization | recent-host-activity-dashboard partition scan

Reconfirmed that refresh discovery uses exact supported-event and intersecting
`dayPK`/`hourPK` prefixes before recursive Parquet matching, with exact event-time
bounds applied afterward. Hardened discovery to reject any returned key outside
the requested event/day/hour set and made that coarse partition scope visible in
the UI. Combined per-family row/host budgets and bucket aggregation into one
materialized scan, avoiding a second full Parquet row scan per family. The 16
focused UV tests pass, including an out-of-window partition rejection case;
actual S3 listing/read latency remains unmeasured because no live access was
attempted.

## [2026-11-10] live verification | recent-host-activity-dashboard

Using the operator-provided read-only environment, confirmed a 12-hour refresh
selects 13 overlapping `dayPK`/`hourPK` partitions and found 3,988 Parquet object
paths across 8 families; scoped listing took about 26 seconds. `raw_process`
schema inspection of 1,226 objects took about 19 seconds and exact-window
aggregation took about 67 seconds (1,305,103 rows, 6 hosts, 598 chart points).
`raw_process_conn_incr` schema inspection over 990 objects took about 17 seconds
and aggregation about 7 seconds, with no exact-window rows. The user reported a
full refresh exceeding five minutes and `pidstat` failing closed above the
2-million-row budget. This confirms partition-scoped discovery but shows
all-family latency is still too high. The endpoint parser now accepts DBT's bare
authority form. No source values, object keys, hostnames, credentials, or raw
rows were retained; no write operations were issued.

## [2026-11-10] performance | recent-host-activity-dashboard selected-family refresh

After the all-family refresh exceeded five minutes, changed the sidebar so an
explicit refresh scans only the selected family; changing families alone makes
no S3 request. The default is Process, selected as a useful live-data family.
AppTest verifies family switching remains query-free. A bounded `raw_host`
refresh over 59 objects took about 5 seconds end-to-end but had no exact-window
rows; a Process refresh remains about 86 seconds for schema plus aggregation on
the observed source. Existing day/hour pruning and exact timestamp filtering are
unchanged. Seventeen offline tests pass; full per-family latency and the
`pidstat` 2-million-row limit remain to be discussed. No source values,
credentials, object keys, hostnames, or raw rows were recorded.

## [2026-11-10] usability | recent-host-activity-dashboard refresh status

Added an expanded `st.status` panel for partition-scoped listing, schema
inspection, and exact-timestamp aggregation, then collapse it with total elapsed
time on completion/failure. The snapshot also records and displays refresh
duration. Family processing failures use neutral messaging rather than claiming
the schema is unsupported, and the detail expander reflects the selected-family
model. A mocked explicit-refresh regression and real Streamlit `AppTest` verify
that only Process is discovered, each progress stage is written, the DuckDB
connection is closed, elapsed time is surfaced, and status completes; all 18
focused tests pass. No live S3 call was needed for this UI verification.

## [2026-11-10] correctness | recent-host-activity-dashboard event-time encodings

The `process_file` empty result was an encoding mismatch: Wintap's `FileSerializer`
sets raw `EventTime` from Unix seconds at serialization, while its 10-second
activity batch preserves `FirstSeen`/`LastSeen` as FILETIME. The dashboard had
interpreted all integer EventTime columns as FILETIME, placing a 2,000,001-row
sample around 1601. Added family-specific timestamp decoding and made the chosen
timestamp priority visible; synthetic tests cover `FirstSeen`, fallback fields,
Unix seconds, and retain FILETIME semantics for `raw_process`. The source-backed
probe found about 7.9 million `FirstSeen` rows in the reported process-file
window, so the existing 2-million-row safety cap remains fail-closed and the
corrected selected-family aggregate takes about 60 seconds to hit it. Corrected
probes also found 59 `raw_host` rows (6 hosts) and 157,821
`raw_process_conn_incr` rows (5 hosts, 479 points), confirming the earlier zeroes
for these Unix-time families were likewise decoding artifacts. No cap increase or
source write was made; operator direction is needed for process-file's high row
volume. No raw rows, object keys, root, credentials, or host values were
retained.

## [2026-11-10] verification | recent-host-activity-dashboard timestamp correction

Final closeout passed all 20 focused app tests, `compileall`, `uv lock --check`,
and repository `git diff --check`. The suite includes producer-family Unix
seconds versus FILETIME tests, file and connection timestamp priority, selected-
family refresh behavior, and the over-budget no-chart UI path. The 2,000,000-row
cap remains unchanged pending operator direction; wider family coverage and
operational latency acceptance remain open.

## [2026-11-10] strategy exploration | recent-host-activity-dashboard high-volume aggregation

Without changing the app or its 2,000,000-row cap, ran a read-only feasibility
query that grouped selected `raw_process_file` rows directly to exact five-minute
host buckets. On 502 discovered objects it counted 7,923,378 in-window rows and
produced 479 nonempty host/bucket groups across 5 hosts, with no hostless rows;
the aggregate query took about 20 seconds and returned only summary aggregates.
The expected full-window ceiling at five-minute resolution is 720 points for
these hosts, within the existing 1,000-point cap. This suggests an exact
aggregate-only path could be usable without retaining millions of raw rows, but
it still reads all source rows and shifts protection from a raw-row limit to
runtime, memory/intermediate-group, and output-point budgets. The existing capped
query ran in 4.9 seconds on the same file list only after the candidate query had
read the objects, so that warm-cache figure is not a cold comparison. The probe
did not fetch or validate the chart series and is not an end-to-end guarantee.
No source writes, code changes, or cap change; operator approval is still needed
before implementing the alternative.

## [2026-11-10] implementation | recent-host-activity-dashboard exact process-file aggregation

Following operator approval, added a dedicated `raw_process_file` aggregate-only
path. DuckDB now applies the exact timestamp filter and counts directly into
five-minute host groups, then coarsens those compact groups if the chart-point
budget requires it; it does not materialize millions of raw rows in Python.
The standard families retain the 2,000,000-row cap. The new path fails closed at
120 seconds, 1 GB DuckDB memory, 1 GB temporary storage, 20,000 intermediate
groups, or the existing 1,000 chart points. App status/captions explain the exact
strategy. Synthetic checks cover raw-cap bypass only for this family, exact row
totals, hostless accounting, bucket coarsening, group-limit failure, and
interrupt/timeout behavior. The read-only live query returned all 7,923,378
matching rows as 479 five-minute points across 5 hosts in about 20 seconds over
513 objects; counts sum to the exact total. No DBT execution or S3 write occurred.

## [2026-11-10] feature-work | raw_sensor file aggregation opened

Completed the interview and created `wiki/work/raw-sensor-file-aggregation/`
brief, interview, and references. Scope is a standalone manual DuckDB 2.0.0
utility in Wintap-Analytics, reading S3 and writing a separate mirrored
`raw_sensor` dataset root; first milestone is hourly cross-host compaction by
event type and exact hive leaf, with schema union-by-name, configurable
target-size shards, and daily rollup/cron deferred. Sources remain unchanged.
Source review found the current .NET path partitions at UTC merge time and
preserves that key on delayed upload retry, contrary to the user's desired
actual-upload-time partition contract. Created the separate
`wiki/todo/raw-sensor-upload-time-partition.md`, linked it from the upload-pipeline
page and indexes, and recorded the no-lookback scheduled design dependency.
The human estimates were supplied as durations only (4 solo days / 2 AI days);
hours and absolute availability dates were not provided and were not inferred.
No source code, schema, raw document, or S3 object was changed.

## [2026-11-10] planning | raw_sensor compaction implementation and verification

Reviewed the brief against live S3-access patterns, Wintappy consumer macros and
pidstat projections, and official DuckDB 2.0/S3 documentation. Created
`wiki/work/raw-sensor-file-aggregation/implementation_plan.md` with seven delivery
steps, proposed isolated Python/DuckDB packaging, schema/type and exact multiset
conservation requirements, publication/rerun failure tests, consumer-version
checks, and a representative shard-size benchmark mapped to all ten acceptance
criteria. Added the verification scaffold and expanded references/brief/index
links. Created `wiki/tension/raw-sensor-compaction-publication-vs-glob-readers.md`:
multi-object S3 writes are not atomic for current recursive readers. Immutable
window roots with explicit completed-root selection are proposed, not confirmed.
The user clarified that object filenames may change; recorded this in the
interview/brief and applied payload/hive-value equality to consumer acceptance.
The separate upload-time TODO remains the no-lookback scheduling dependency.
Runtime, S3 write, benchmark, and consumer acceptance are not yet executed.
Feature-scoped documentation checks passed: six pages' YAML/required fields and
inbound links, 49 grounding entries, 40 wikilinks, and `git diff --check`.

## [2026-11-10] decision | simplify raw_sensor compaction validation

The user confirmed DuckDB 2.0.0 for Parquet-in/Parquet-out processing and a
shared development/operational check: each partition's total source rows must
equal its total merged rows. Updated the interview, brief, implementation plan,
verification record, references, and index. Replaced the proposed full-row
multiset validation and DuckDB 1.5.6/DBT test gate with name-aligned `UNION ALL`,
small schema fixtures, and a reusable `COUNT(*)` comparison reporting source
rows, merged rows, delta, and status. A count mismatch fails completion and
operational verification. Compactor implementation and runtime tests remain
pending.
Documentation revalidation passed for six pages, 49 grounding entries, and 42
wikilinks; `git diff --check` passed.

## [2026-11-11] implementation | metadata-first recent host activity dashboard

Added a default File metadata query mode for quick herd status. Bounded,
concurrent boto3 `ListObjectsV2` requests enumerate only the selected 12-hour
event/day/hour partitions, use S3 object `Size`, and never GET/open Parquet files.
The dashboard parses `hostname+event_type+FILETIME.parquet`, treats Win32
FILETIME as collect time (not upload/LastModified time), filters the exact
window, and charts per-host file count or size with a host summary. Malformed or
family-mismatched filenames are reported and excluded. The existing DuckDB
raw-row mode remains optional. Added boto3 to the app lock and tests for
pagination, partition scoping, size/file budgets, timestamp parsing, exact
window totals, and a metadata AppTest asserting no Parquet connection/schema/
row query. All 27 tests pass; compileall, lock check, and diff check pass. No live
metadata-mode S3 query was performed, so deployment latency/compatibility remain
open.

## [2026-11-11] implementation | show both metadata time-series charts

Updated the metadata dashboard to display file count and S3 object size as
separate collect-time charts at once, using the same selected hosts and bucket
width. Removed the metric switch and updated app/workflow documentation.

## [2026-11-11] verification | combined PyUtil PR #43 preparation

Validated the SELinux branch containing all source-validation PR ancestry using
the existing environment. Fixed the Python SQL renderer's missing network macro
(baseline 38 failures), added shipping network-ID and nine synthetic SELinux
regressions, and reached 286 passing tests. Config tests pass separately (4);
historical failure evidence remains intact. No live operator data/S3 was accessed.
Documented optional SELinux/count/attribution contracts and temporary five-tuple
ID compatibility in PyUtil README and the canonical pipeline page. Updated both
feature verification/plans and index; canonical SELinux promotion is complete.
The human chose expansion of PR #43 while preserving both branches. Required
review, full combined split-local/authenticated-S3 builds, network-ID consumer
qualification and S3 helper hardening remain outstanding release work.
PyUtil repair/docs commit `21db95e` was pushed to both preserved branches; PR #43
was expanded and marked ready. Main remains blocked by required approving review;
no reviewer is assigned. Private run-env files remain untracked and untouched.

## [2026-11-11] workflow | Wintap/Lintap ETL data-flow diagram

Added an editable draw.io view and wiki guide for host-local raw Parquet → S3 →
Wintap-PyUtil `make dbt-build` → bronze/silver/gold in local DuckDB. Included the
current Makefile config/source/build/test and QA targets, with the bounded source
probe and no-Parquet-export limitations explicit. Linked from the index.

## [2026-11-12] analysis | anonymized process-tree completeness and durable context

Pages created: `wiki/diagnostic/process-tree-context-completeness.md`,
`wiki/workflow/process-ancestry-completeness-qa.md`,
`wiki/concept/durable-process-context-and-stream-table-enrichment.md`, and
`wiki/tension/refresh-republication-vs-durable-process-context.md`.
Preserved calculated six-host root-reachability, seed and ancestor-impact results
using snapshot-local aliases; no real hostnames, IPs, instance hashes, private
dataset path or alias map recorded. Read-only aggregate/graph rechecks confirmed
denominators, root counts, top-three impacts and zero non-root cycles; distinct
absent keys explicitly exclude blanks but can include unresolved sentinels.

Pages updated: collection boundaries, identity, process retention/events, historical
audit, analysis workflows, Esper semantics, glossary and index. Review-required
identity/historical-audit additions are flagged as supplemental links; existing
contradictions and original measurements remain unchanged. No new hard
contradiction promoted or historical-loss conclusion asserted.

Documented durable entity state, stream-table enrichment, snapshot plus changelog,
historical/as-of context and a hybrid reconciliation/context-closure proposal.
Kafka references were read; Splunk lookup capabilities have official-search support
only because direct fetch returned 403. Hourly refresh is an unverified historical
recollection and suggested pilot, not a current setting or selected policy.
No sensor, pipeline, database, raw document or sibling-repo writes; unrelated
working-tree changes preserved. Documentation validation results follow below.

Validation: Ruby/Psych parsed all four new YAML frontmatters and confirmed required
fields/nonempty grounding; 39 scoped wikilinks resolve, all new pages have inbound
links, and all 17 local grounding paths exist. Additions passed a dataset-hostname,
IPv4/hash/UUID/private-path privacy scan and new-page whitespace checks.
`git diff --check -- wiki` passes; repository-wide `git diff --check` remains
blocked solely by pre-existing README trailing whitespace, left unchanged.

## [2026-11-12] design | tactical runtime windows and bounded compactor-fed context

Recorded human tactical guidance: DBT publication inputs should span the relevant
deployed sensor runtimes, including startup/rundown publications, while activity
can remain experiment-windowed. Qualified as context-loss mitigation, not capture
or ancestry completeness certification.
Created `wiki/work/raw-sensor-file-aggregation/process-context-options.md` and
linked it from the brief, durable-context concept and index. Proposed a separate
derived process projection retaining live/recent/pinned seeds and transitive
ancestors, with reachability-based reclamation, slim metadata, explicit context
horizon/grace, archive fallback and row/byte budgets. Exact ancestry for arbitrary
all-time queries cannot be guaranteed by fixed-size state; missing Stops and long
dependency chains require explicit limits and degraded-coverage reporting.
Compaction's UNION ALL/count-conservation acceptance, source retention and
no-lookback scope remain unchanged; implementation/DBT integration are not approved.
No code, raw data, database, sensor or sibling-repo writes.
Validation: three affected page frontmatters parse with required fields and
existing local grounding; 20 wikilinks resolve. New-note privacy-pattern checks
and `git diff --check -- wiki` pass.

## [2026-11-12] clarification | ground-truth collection independent of experiments

User clarified that research means less concern about long-horizon changes and
backward compatibility, not experiment-scoped collection. Updated the optional
compactor-context note, durable-context concept and index: retained telemetry is
the ground-truth dataset; experiments later consume all or subsets. Removed
experiment pins from the proposed working-set policy and replaced experiment
snapshots with dataset-level context checkpoints. Operational live/recent seed
retention plus ancestor closure remains a proposal; bounded derived-state eviction
must not silently discard retained ground truth or imply historical completeness.
No implementation, retention duration, or feature-scope expansion approved.

## [2026-11-12] docs | PowerShell ETW sensor implementation status

Added canonical component and event-type pages for Wintap's native PowerShell
4104 sensor. Recorded its branch status (`6add359` is present on the inspected
feature/develop lines but not Wintap `origin/main` as of this date), default-off
setting, broad provider subscription, event-time attribution, raw Parquet output,
sensitive script-text handling, and the absence of a PowerShell-specific Wintappy
DBT bronze model. Reframed the October native-tool POC brief, handoff, plan,
findings, and verification as historical evidence; cross-linked the distinct
cmd.exe WindowsShell sensor. Code tests and the Windows smoke harness were not run;
live ETW load/loss and host-policy qualification remain open. Merged Analytics
`origin/main`, preserving both sides' index/log entries. No source code, raw data,
or sibling-repository files were changed.

## [2026-11-12] code | raw_sensor compaction first development slice

Started authorized implementation on `work/raw-sensor-file-aggregation` in
`extras/raw-sensor-compact/`: isolated DuckDB 2.0.0 package/lock, read-only
`plan`/`verify`, exact UTC-hour inventory/rechecks, conservative schema checks,
local union-all writer, and shared per-leaf source/merged row-count validation.
81 tests pass on Python 3.14.0/macOS arm64; one opt-in S3 read-only fixture test
skipped. Ruff lint/format and lock checks pass. Tests cover NULL/missing/reordered
fields, within/across-file duplicates, multiple shards, source bytes/drift,
namespace/candidate safeguards, mismatches and timeout; mocked credential tests
share frozen identity and resolved endpoint between boto3/DuckDB.

Updated implementation plan/checklist, verification evidence and index; created
`wiki/tool/raw-sensor-compaction.md` for verified development interfaces only.
No real S3 endpoint or multipart writes tested; no compact/publish CLI exists.
Immutable completed-root selection remains proposed/unapproved, representative
benchmark/shard default pending, refresh unsupported and timeout cooperative.
Scheduling/upstream upload correction and optional process projection remain
outside this slice. No sibling repos, production datasets or raw documents changed.

## [2026-11-12] code | immutable compaction roots and bounded live S3 qualification

Recorded human approval of immutable per-run roots with explicit completed-root
selection, plus `lintap-alpha` profile/config and new-prefix S3 test authorization.
Added `compact`, fresh per-run reservations, final inventories/manifests, fresh
manifest-backed `verify --dataset`, candidate error roots, and conditional metadata
qualification. Local failure/new-generation/drift and lost-response tests pass;
94 tests pass with 2 integration tests skipped by default. Ruff remains clean.

Live direct DuckDB 2.0.0 S3 COPY/fresh count verification passed twice for a bounded
pidstat/host hour: 897,395 rows, 29 → 2 files, all 29 source SHA-256 unchanged.
Tracked opt-in write regression: 1 pass/1 distinct read-only-fixture skip. Outputs
are intentionally unpublished; pidstat bytes grew 3.37× with current settings,
so this is not a compression/performance benchmark or shard-default decision.

Discovered DuckDB unfinished-result extension setup failure; drained internal
results with `.fetchall()`. More importantly, live endpoint silently overwrites
keys despite conditional PUT (HTTP 200). Managed publication now fails closed
on a metadata-only probe before writing Parquet; no live consumer-ready root or
cutover. Added accepted root ADR and a separate conditional-write endpoint tension;
original publication tension held pending qualification. Updated brief/interview,
plan/checklist, verification, canonical tool and index. No silent fallback, source
write/deletion, sibling change or raw-document copy; new destination probes and
unpublished test candidates remain for inspection. Benchmark, credential expiry,
multipart faults, concurrency/SIGKILL and no-op reuse/resume still pending.

## [2026-11-12] code | fixed compaction hours, skip and manual cleanup

Human explicitly superseded UUID generations with
`lintap/raw_sensor/<event>/dayPK/hourPK/...` →
`lintap/compacted/<event>/dayPK/hourPK/...`: skip existing destination event/hours,
otherwise merge all files per exact optional protocol leaf. Row order is immaterial;
no sorting added. Removed manifests/reservations/conditional PUT and generation
publication. Partial failures remain for manual cleanup; existence is not completion.
Source deletion was suggested only as a later phase and is not authorized or available.

Local fixed-root suite: 92 passed/2 opt-in skips. Actual fixed-root S3 integration:
1 passed/1 separate read-only-fixture skip in 33.06 seconds. The pidstat/host hour
preserved 897,395 rows with zero leaf deltas, reduced 29 objects to 2, and retained
all 29 source SHA-256 hashes. Rerun skipped both existing hours with unchanged output
hashes. Destination hours now exist; fresh-write fixture must not be repeated there
unchanged. No source/test deletion, sibling change or consumer cutover performed.

Accepted fixed-hour ADR supersedes immutable-root ADR; publication tension resolved
by scope change and conditional-write tension dissolved, not an endpoint repair.
Updated README, brief/interview/plan/verification, canonical tool and index; earlier
generation evidence/log retained as historical. Benchmark/default, broader live
family/protocol/resource and credential/multipart-fault qualification remain pending.
Pidstat output bytes grew 3.37×; no compression/scan improvement claimed.
Final local rerun: 92 passed/2 skipped in 0.77 seconds; Ruff lint/format (16 files)
and locked dependency checks pass. Implementation remains uncommitted/unpushed on
`work/raw-sensor-file-aggregation`.
Scoped documentation validation passes: 11 frontmatters, 64 existing grounding
paths, 57 resolving wikilinks and inbound links for every scoped page.
`git diff --check` and current direct-root CLI help pass.

## [2026-11-12] code | unioned DBT inputs and validated source-prefix deletion

Human approved raw_sensor + compacted DBT input, accepted transient/failure overlap,
and clarified UTC upload partitions plus 5–10 minute grace permit **prefix** deletion
despite rare clock skew. Added explicit `compact --delete-source`, default 10-minute
grace (minimum 5), whole event/hour validation before deletion, batched/paginated
S3 prefix removal and local symlink refusal. Default retains source; skip never
deletes an existing destination's source. Partial deletion stops for manual repair.

Authorized PyUtil changes on `work/raw-sensor-compacted-union`: shared macros,
event/optional-column/preflight discovery and local date discovery read both roots.
Optional `WINTAP_DBT_COMPACTED_ROOT` is a direct event-root override. No new overlap
deduplication/preference rule; existing bronze accounting stays unchanged. DBT
DuckDB 1.5.6 pin remains; Analytics compactor stays 2.0.0. Both branches uncommitted/
unpushed; private run-env files preserved. No sensor, raw-document or original
live source/output change and no production cutover.

Compactor: 107 pass/2 opt-in skips; PyUtil: 292 pass/2 opt-in skips. Full local
raw/mixed/compacted migration: 7 tests pass, 54 equivalent model results, 139 gates
per state, 28 fixture sources deleted/56 rows conserved. Includes genuine duplicate/
NULL/missing-column, UTC rollover, protocol and explicit non-masked overlap cases.
Copy/schema/validation/second-protocol failures preserve source; deletion failures,
per-key S3 errors/remaining objects, adjacent-prefix and grace boundaries tested.

Copied live S3 migration at `compaction-tests/dbt-union-20261112-02`: 1 pass in
97.25 seconds. Raw-only, mixed event-family and fully compacted inputs each pass
10 scoped DBT gates; 4 host/pidstat models match for 897,395 rows. All 29 test-copy
source objects deleted by validated hour prefix; all 29 original source hashes
unchanged. Passing compacted copies remain for inspection. Initial `-01` fixture
failed only in fresh verification connection's temporary-secret setup before any
merge/deletion; its raw copies remain untouched. Repaired harness and used fresh
`-02`, not automatic recovery/cleanup. Original live deletion is not authorized.

Updated brief/interview/decision/plan/verification, canonical tool/repo and index.
Sorted-result hashes are test comparison only, not production sorting or a new
compactor gate. Source/output verify is pre-deletion/retain-source only; save merge
reports and use a baseline after migration. Rebuild bronze and materialized models
after file migration. Broader live family/gold, transport/resource faults, benchmark/
shard default and scheduling remain open.
Final lint/format and both dependency-lock checks pass, as do `git diff --check`
in both repos. Scoped wiki checks pass: 12 frontmatters, 86 current grounding paths,
74 wikilinks and all scoped inbound links. Fifteen inherited unavailable old
`../Wintappy/` checkout citations in the canonical repo page remain separate debt,
not claimed as revalidated/repaired.

## [2026-11-12] code | expanded all-model copied-S3 migration qualification

Human requested expansion beyond host/pidstat. Added opt-in `all-models` scope to
the PyUtil live-copy regression; default scoped test remains available. Read-only
inventory of the same UTC hour found 399 files/35,471,263 bytes across 9 families,
including file/process/TCP/UDP and all three SELinux families. Image-load/registry
are absent. Full scope builds all 54 models in three fresh databases; compares
names/types/counts/hashes, excluding only pidstat derived filename. Added bounded
fixture file/byte caps and saved local inventory/merge/snapshot evidence. No model
semantics/dependency changes, original source/output changes or production cutover.

Strengthened-comparison local migration: 7 pass, 54 equivalent models/139 gates
per state in 22.77 seconds. PyUtil regression: 292 pass/2 opt-in skips in 48.21
seconds. Black/isort/lock/diff checks and scoped wiki validation pass. Full S3
copy test launched at new `compaction-tests/dbt-union-all-20261112-01`; live result
is pending, not claimed as acceptance. Plan/verification/interview and PyUtil
test guide updated; earlier fixtures preserved.

## [2026-11-12] verification | full DBT live-copy builds pass but equivalence fails

Expanded live-copy regression failed strict raw/mixed comparison in 273.04
seconds: both full builds pass 139 gates, all schemas and all bronze snapshots
match, but 17 model results differ, including downstream file-model counts.
Only copied host data was merged (five rows, zero delta) and deleted (five objects);
remaining 394 copied raw objects remain, alongside one compacted host output.
The fully compacted phase and final original-hash assertion were not reached.
No original live write/delete or earlier-fixture cleanup was performed.

A fresh DBT build over the **same mixed input without further compaction** passes
139 gates and changes 18 model results. Read-only keyed comparisons and a direct
shipping-SQL diagnostic identify unordered `ANY_VALUE` process name/path/parent
and process_file PID representatives; identical reversed rows change derived
filename/file_id. No production model changes, normalization, comparison bypass,
or further deletion were used to manufacture a pass. Other aggregate effects
remain unqualified, not claimed as exhaustively explained.

Created [[wiki/tension/dbt-arbitrary-representatives-vs-compaction-equivalence]];
updated canonical tool/repo, index, plan, verification and PyUtil testing guide.
Full-model migration remains blocked pending explicit representative semantics
or comparison-contract decision. Scoped host/pidstat and synthetic fixture results
remain valid in their stated scope. The expanded mixed fixture is inspectable but
must not be reused by the initially-absent-root regression.
Final local migration with the direct diagnostic: 8 pass in 23.43 seconds;
54 equivalent synthetic models/139 gates per state remain valid. Ordinary PyUtil
suite: 293 pass/2 opt-in skips in 49.96 seconds; the separately run full live
strict-equivalence failure is not claimed as a passing skipped test. Final
Black/isort and both diff checks pass; scoped wiki checks pass (13 frontmatters,
92 current grounding paths, 81 wikilinks), retaining the documented 15 inherited
old-checkout exclusions. No compactor or production DBT model changes in this
expansion; changes remain uncommitted/unpushed.

## [2026-11-12] decision | ANY_VALUE debt is non-blocking for compaction

Human explicitly says existing ANY_VALUE quality issues do not block this task.
Resolved the gate tension by separating source fidelity from analysis-selection
debt, not by repairing representatives. Added explicit full-test
`RAW_COMPACT_DBT_COMPARISON=any-value-diagnostics`; default remains strict. Compute
ANY_VALUE model/dependent closure from manifest; require exact schemas/model set,
bronze results and results outside that closure. Report affected differences
with counts/hashes; do not normalize or claim every difference's cause/equivalence.
No production models, compactor settings/sorting, dependency pins or original
live data changed. Six comparison/closure safety regressions pass; ordinary
PyUtil suite 299 pass/2 opt-in skips in 49.69 seconds.

Started a fresh three-state all-family S3-copy regression at
`compaction-tests/dbt-union-all-20261112-02`, preserving the earlier mixed fixture.
Save initial original hashes alongside evidence and recheck them on completion.
Updated interview/tension/plan/verification/index, canonical tool/repo and PyUtil
guide. Rerun is pending, not yet an all-family acceptance claim. Production
cutover and separate ANY_VALUE semantics repair remain outside scope.

## [2026-11-12] verification | full copied-live compaction and all-model DBT pass

Approved ANY_VALUE diagnostic-mode live-copy rerun at
`compaction-tests/dbt-union-all-20261112-02`: 7 pass (6 safety cases plus live
migration), 502.83 seconds. Full DBT raw/mixed/compacted builds each pass 139
gates and build all 54 models. All model schemas/all 11 bronze results match;
36 model results match across every state. Differences in 18 ANY_VALUE-reachable
models (18 mixed, 17 compacted) are saved with counts/hashes, not hidden or
claimed causally explained/equivalent. No differences outside the closure accepted.

Nine live families/10 protocol leaves conserve 2,668,265 rows with zero deltas.
All 399 isolated copied raw objects deleted after validation, producing 10 outputs;
all 399 original source SHA-256 hashes match their saved pre-copy baseline.
Passing compacted copy survives for read-only full builds; added a fresh-database,
hour-08/no-select command to the PyUtil guide. Previous mixed/scoped fixtures,
private env files, original raw/compacted roots and engine pins remain untouched.
No production cutover. Registry/image-load absent, representative benchmark,
credential/resource faults and ANY_VALUE repair remain separate.

Updated verification/plan done checklist, index and canonical tool/repo; promoted
bounded full-model acceptance and explicit non-equivalence scope. Ordinary PyUtil
299 pass/2 opt-in skips remains current. Implementation is uncommitted/unpushed.
Final changed-Python Black/isort and both diff checks pass. Scoped wiki checks:
13 frontmatters, 94 current grounding paths, 82 wikilinks/inbound links pass;
15 inherited old-checkout grounding exclusions remain separate documentation debt.

## [2026-11-12] relocation | compactor now owned by Wintap-PyUtil

Human explicitly corrected ownership. Moved the standalone package (17 Python
source/test files, README, pyproject, lockfile) from Analytics `extras/` into
`../Wintap-PyUtil/extras/raw-sensor-compact/`, preserving code/test logic and
DuckDB 2.0.0 pin. Fresh nested environment verified; main pipeline remains
DuckDB 1.5.6. Updated both local/S3 integration subprocess paths, PyUtil README
and DBT guide, and added a scoped ignore exception for the nested lockfile.
Archived only verified generated old caches/environment outside the repo;
the old Analytics package directory is absent. No broad deletion or discarded work.

Relocated compactor: 107 pass/2 S3 skips (1.57s). PyUtil: 299 pass/2 opt-in skips
(49.64s). Full isolated-local migration: 8 pass (23.25s), all 54 models equivalent,
139 gates per raw/mixed/compacted state and 28 fixture sources deleted. Both
lock checks, runtime/CLI checks, Ruff/Black/isort and diff checks pass. No S3
operation rerun, dataset change, production cutover, dependency upgrade or
ANY_VALUE semantic repair. Historical live test evidence preserved.

Updated source anchors/ownership in canonical tool/repo, feature brief/interview/
plan/verification, index and relevant decision/tensions. Fixed-hour ADR is still
human-review-required: annotated the source-path-only relocation for review;
accepted behavior unchanged. Analytics retains shared wiki and evidence ownership.
Implementation remains uncommitted/unpushed in the existing branches.
Scoped wiki validation passes: 13 frontmatters, 96 current grounding paths,
83 wikilinks/inbound links; 15 inherited old-checkout exclusions remain unchanged.

## [2026-11-12] cleanup | remove compaction S3 artifacts, preserve source telemetry

Human requested cleanup and committing current changes. Read-only inventory and
identity recheck scoped deletion to 443 objects in this work's nine test prefixes
plus its two initial retain-source pidstat/host outputs under `lintap/compacted`
for day 20261111/hour 08. Removed 445 objects/102,200,467 bytes by exact-key SDK
batch, with 445 confirmations/zero errors; all selected prefixes now empty.
Bucket versioning disabled; zero unfinished multipart uploads in these scopes.
All 399 original raw-source SHA-256 hashes matched the saved baseline before
and after cleanup. No original raw key targeted, broader root removal, production
migration or cutover. Private inventory/results and earlier local evidence retained.

Updated verification/interview, canonical tool/repo, index and PyUtil docs to
record cleanup and mark the saved-fixture DBT command historical. Prior live-test
results remain evidence; no surviving test dataset is advertised. Prepare commits
in both existing branches, excluding private run-env files; no push requested.

PyUtil implementation committed as `aa99efd` on `work/raw-sensor-compacted-union`
(33 files). Analytics wiki/evidence committed separately in this change on
`work/raw-sensor-file-aggregation`. Private run-env files remain unchanged and
untracked; neither branch pushed. Final staged diff checks and scoped wiki checks
pass (13 frontmatters, 96 current grounding paths, 84 wikilinks/inbound links;
15 inherited exclusions unchanged). Regression evidence remains 107 compactor,
299 PyUtil and 8 isolated-local migration passes from relocation verification.

## [2026-11-12] plan | durable process entity manager with S3 Parquet persistence

Human selects first-round S3 Parquet persistence, hourly compaction-job entity
updates and infrequent DBT parent enrichment. Worker has no durable local state;
S3 entity state persists. Created feature brief/design/implementation plan/
verification under `wiki/work/durable-process-entity-manager/`; updated index,
durable concept, original optional-context note and refresh tension.

Proposed defaults: fixed full snapshot per host (rewrite also compacts entity
state), retain all known instances/no initial GC, replay-safe evidence/conflict
sets, explicit bootstrap/rebuild, entity publication/verification before process
source deletion, one writer/no DBT overlap, separate DBT context closure with no
raw lifecycle-count inflation. Avoid ANY_VALUE parent selection and PID-only repair;
unobserved/conflicted ancestors remain unresolved. Proposed schema, policies and
limits await review, not implementation approval.

Read current PyUtil compactor/bronze/silver/path/gold source to ground integration
boundaries. No source code, schema, private config or S3 operation changed; no
entity prototype/tests run. Earlier compactor qualification is separate evidence.

Planning review passes `git diff --check` and scoped structural validation:
7 frontmatters, 35 local grounding paths, 25 wikilinks, 4 feature index entries.
Added explicit entity/raw cross-phase inventory binding to prevent deletion of
new evidence not incorporated in entities, and Parquet metadata for initialized
empty hosts. No entity implementation or endpoint tests run; plan remains uncommitted.

## [2026-11-12] implement | first-round durable process entities and DBT ancestry

Human accepts the plan and explicitly authorizes implementation/testing ("Proceed!").
Implemented in Wintap-PyUtil: canonical evidence JSON in fixed per-host S3 Parquet,
explicit host/namespace/init/replay/verify/new-root rebuild and partial-init resume,
no initial GC, conservative paired-parent/Stop conflicts, resource limits, full
GET verification, entity-before-delete phase and cross-phase process inventory
binding. Main DuckDB remains 1.5.6; standalone writer remains 2.0.0. Main pytest
collection explicitly excludes the independently tested extra.

DBT opt-in materializes state, reduces retained/current evidence, builds activity/
ancestor context, keeps window seeds/counters and original hostname payloads,
and emits terminal root/gap/conflict/cycle QA. A new summary assertion caught and
fixed the normalized-host output join regression. Non-root self-links remain
cycles; accepted roots require recorded self-parent evidence plus declared root
PID candidates. No historical snapshot rows injected into raw telemetry.

Verification: **132 extra passes/2 skips**, **310 main passes/3 skips**, final
targeted locked entity/DBT tests **11 passes**. Actual generated-S3 qualification
**1 pass**; final read-only full build **58 models/145 gates**, **33 complete seed
paths and 33 summaries**, 36 entities, 2 context-only ancestors. Snapshot 5,843
bytes; 32 generated source hashes verified before optional validated deletion.
Retained 14 compacted outputs plus 1 snapshot (48,182 bytes) at the exact synthetic
root recorded in [[wiki/work/durable-process-entity-manager/verification]]. No
original telemetry access/mutation, private run-env edits, broad S3 operation,
output cleanup, production rollout, commits or pushes. Mocked lost-ACK/corrupt
publication/partial-host cases are not a claim of live network-failure qualification.

Created [[wiki/tool/durable-process-entity-manager]] and promoted implemented facts
from work artifacts; updated brief/design/plan/verification, canonical concept/
compactor tool/ancestry QA, original optional-state note, refresh tension and index.
Large-host capacity, actual historical bootstrap/root configuration and external
writer/DBT scheduling exclusion remain production gates, not silently implemented
services. Broad refresh/retention tension and downstream ANY_VALUE debt remain open.

Final scoped wiki validation passes 10 YAML frontmatters, 61 local grounding paths
and 47 wikilinks. Both repo diff checks pass; final locked reducer/store tests pass
25 cases after the publication-report refinement. Work remains uncommitted.

## [2026-11-12] verification | begin earlier-window and week-long actual-data tests

Human authorizes many days/a week of compaction on test telemetry. Clarified that
prior entity proof used synthetic fixtures, not the earlier actual telemetry.
Read-only inventory freezes 71,155 objects/5,958,506,820 bytes: November 5–11 full
available telemetry plus October 25–November 4 process-only bootstrap history.
Located the original six-host materialized audit and its 08–22 process globs;
independent saved-graph audit reproduces its large breakpoint concentration.
Today's inventory is larger, and recorded-self-root QA differs from legacy PID
root policy; neither difference will be mislabeled as enrichment improvement.

Fresh actual-data copies are hash-verified before test mutation. Earlier-hour
raw/mixed/compacted DBT qualification runs separately; 168 hourly tests and default
historical-state capacity probe are prepared. Copy timeout resumed safely; corrected
a test-harness query for nonexistent Refresh counters, with no shipped-code change.
Evidence lives in the private dpe-actual-week-1vnezp50 directory recorded in feature
verification. Expanded results pending; originals read-only, no cleanup/cutover,
private env edits, commits or pushes. Updated verification and plan tracking.

Human adds file-count/byte-size metrics to the active qualification. Prepared
overall/day/hour/event reduction ratios, output-size distribution and throughput
from validated partition reports; exclude failed/partial outputs, bootstrap copies
and entity-state storage from raw-compaction savings. Negative byte savings remain
visible. Helper arithmetic/grouping/failure-exclusion checks pass; live aggregates
pending, not claimed from inventory alone.

## [2026-11-12] verification | earlier actual hour passes; report file and byte savings

Real November 11/hour 08 isolated migration completes: 399 → 10 raw Parquet
files (97.49% fewer, 39.9×); 35,471,263 → 32,792,809 bytes (7.55% saving);
all 2,668,265 rows preserved and 399 original hashes unchanged. Disabled baseline
54 models/140 gates; enabled raw/mixed/compacted 58 models/145 gates each. Bronze,
schema, host-level Start/Stop counters and 40,982 summaries preserved. Four accepted
ANY_VALUE-reachable downstream differences retained explicitly in comparisons.

Entity init/no-op replay/combined-before-delete/compacted replay/verify pass:
40,982 entities, 86 direct parent conflicts, five snapshots/3,277,708 bytes.
Hour-only context does not repair historical ancestry: terminal QA still reports
40,893 missing-ancestor and 89 parent-conflict seeds, zero recorded-root seeds.
Do not confuse integration success with historical completeness; week/bootstrap
qualification is separate and pending.

Metrics expose pidstat expansion (2.339 → 7.892 MB), despite overall saving. Both
layouts use ZSTD, but compacted output has 426 small row groups vs 24 originals.
Local controlled row-group A/B retains counts/all-column row-hash sums; requesting
122,880 rows/group yields 1,122,558 bytes vs 7,969,344 at 2,048. This is a tuning
opportunity, not a shipped change or remote benchmark. Raw plus entity dimension
totals 36,070,517 bytes, 1.69% above raw alone; storage types reported separately.
Full table/timings/private evidence paths saved in feature verification. No
original mutation, cleanup, private config edits, production deployment or commit.

Full 71,155-object copy/hash qualification completes; resumed copy command took
1,628.44 seconds (copy/verification, not compaction). Started historical/default
capacity plus sequential 168-hour driver. Independent SQL raw-evidence reduction
exactly matches 40,982 persisted entity scalar tuples; independent Python graph
walk matches all real-hour DBT terminal-status counts. Full history and week
compaction results remain pending, and no completeness inference is made from
these passing one-hour integration/reducer checks.

## [2026-11-13] verification | week completes; raw savings and entity/deletion limits

Completed November 5–11 copied-data driver: 168 hours attempted, 165 successful raw
compactions and three immediate deletion-verification failures. Successful reports
preserve 360,027,830 rows: 53,415 → 1,650 files (96.91% fewer / 32.37×),
4,841,533,292 → 4,623,379,532 bytes (218,153,760 / 4.51% saving). Recomputed metrics
and successful leaf gates pass; final read-only S3 listing independently matches
output count/bytes. All 71,155 original full-GET hashes remain unchanged.
Successful command time 6.58 hours / 15,197 rows/s; daily/event/runtime breakdowns
and accounting exclusions recorded in feature verification. PIDstat expands
467.563 → 1,395.968 MB; other families save 26.21%. No layout tuning shipped.

Historical entity bootstrap rejects unknown identity before publication/capacity
certification. Week-limited init passes with 33,824 entities/nine snapshots/
2,730,739 bytes; only one combined hour passes, then two PID −1 Refresh
rows stop entity updates and the harness explicitly continues raw-only. Expanded
history also contains positive-PID sentinel-key Stops. Do not label the week a
successful entity-manager or historical DBT qualification; default large-host
budgets, identity policy and original audit-window enrichment remain open.

Failures: November 5/06 network, November 9/11 SELinux transition, November 11/20
SELinux interaction. Those exact event prefixes are empty on later inspection,
but transient/stale listing is only a hypothesis and commands remain failed.
Retain 25 partial output objects/60,900,907 bytes and 142 unprocessed inputs/
28,481,517 bytes for manual reconciliation; no blind reruns/deletes. Pre-week
process copies/entity storage excluded from raw savings. Updated verification,
plan checklist, canonical entity limitations and index. No source changes,
original mutation, private-env edits, cleanup, commits, pushes or deployment.

Final diff check and scoped validation pass: three frontmatters, 24 grounding
paths, six links, all day/event/hour metric totals and identity-category counts.

## [2026-11-13] milestone | commit durable entities and copied-week qualification

Human requests committing current milestone and a complete/next summary. Prepared
[[wiki/work/durable-process-entity-manager/dev_handoff]] with completed code/test/
actual-hour/raw-week evidence and prioritized deletion reconciliation, explicit
identity policy, historical capacity/bootstrap/DBT qualification, separate PIDstat
tuning and production exclusion/operations gates. Corrected stale brief test-status
wording and indexed the handoff. Commit scope is the existing PyUtil implementation
and Analytics wiki feature changes; private run-env files and temporary/raw evidence
are excluded. No push, cleanup or deployment requested.

PyUtil milestone committed as `2cfbad1` on `work/raw-sensor-compacted-union`
(25 files); the two private run-env files remain untracked/excluded. Fresh targeted
checks: 11 DBT/entity passes and 25 reducer/store passes. Staged wiki checks pass:
11 frontmatters, 67 live grounding paths and 360 links; five existing external
citations excluded from local-path checks. Both staged diff checks pass. Analytics
milestone committed separately on its existing branch; neither branch pushed.

## [2026-11-13] policy | centralize persistent-content privacy rule

Following human authorization, the single canonical wiki-content privacy rule is
now in the root `AGENTS.md`. Deleted the interim standalone policy page and its
index link to avoid duplication.

## [2026-11-13] handoff | Garage deletion milestone and on-prem continuation

Recorded the read-only reconciliation: all 25 partial compacted objects from the
three failed hours match immutable local input rows, and all 142 remaining raw
objects match preserved copies. The human accepts the compacted outputs as correct
for this intermediate milestone; the failed delete-verification commands and
historical cause remain explicitly unresolved. Added two synthetic Garage test
passes: normal deletion at 72/24/35 objects succeeded, and an injected post-delete
marker reproduced the exact failure path; all test-prefix objects were cleaned.
Documented the optional every-node Garage debug-log reproduction. Refreshed the
implementation checklist, index and dev handoff for measured on-prem versus
laptop/VPN performance work. No code, qualification data, DBT or production data
was changed. Committed and pushed the Analytics wiki update as requested.

## [2026-11-13] verification | bounded read-only Garage fixture check

The approved one-hour synthetic fixture passed the isolated read-only S3 count test:
24 expected rows, zero source/destination row delta, 24 source objects / 17,544 bytes,
and one compacted object / 970 bytes. Pytest reported 2.18 seconds including process
and test overhead. No S3 mutation, DBT, or preserved qualification-data access occurred.
The same fixture still needs a laptop/VPN run for an apples-to-apples path comparison;
the historical week aggregate is not comparable. Details: durable-process-entity-manager
verification and dev handoff.

## [2026-11-13] verification | Nov 7 one-day raw compaction on-prem

Read-only inventory confirmed the immutable Nov 7 baseline at 7,360 objects,
788,009,194 bytes and 57,047,250 rows for the populated compaction scope. Copied it
to a fresh disposable source in 436.168 seconds, then ran 24 sequential hourly
128-MiB compactions in 612.17 seconds. Eighteen hours completed; six stopped at
source-prefix deletion verification with partial outputs and disposable inputs
retained. Fresh output currently has 209 objects, 669,242,885 bytes and 52,399,728
rows; the full-day read-only verify reports 209/240 partitions present and zero
delta for every emitted partition. No immutable source data, DBT, or entity
bootstrap was changed or run. Details: `wiki/work/raw-sensor-file-aggregation/verification.md`.

## [2026-11-13] diagnosis | Garage post-delete verification failures

The Nov 7 disposable-copy run produced six `Source prefix remains after deletion`
failures, versus three in the prior 168-hour run. All six exact failing prefixes
were empty on a later read-only listing; the staged copy had no producer, and the
implementation reaches this message only after a delete response without reported
per-object errors followed by an immediate positive listing. Evidence therefore
supports, but does not prove, GarageFS/S3-compatible stale read-after-delete
behavior. Recommended mitigation is bounded exact-prefix post-delete retries with
backoff plus a separate deletion-reconciliation path; no code change was made.

## [2026-11-13] code | Garage deletion mitigation implemented

Implemented bounded S3 post-delete exact-prefix confirmation retries with safe
remaining-key and response diagnostics, fail-closed exhaustion, and two-phase
hourly processing so one deletion failure does not stop other event compactions.
Added explicit `reconcile-delete --confirm-delete` validation-gated cleanup with
grace enforcement. The standalone compactor suite passes 137 tests with 2 opt-in
skips; no live S3 rerun was performed. Details:
`wiki/work/raw-sensor-file-aggregation/verification.md`.

## [2026-11-13] verification | mitigated Nov 7 one-day Garage rerun

Re-copied the immutable Nov 7 baseline into a fresh disposable source/destination
and ran all 24 independent hourly compactions with bounded deletion confirmation.
The copy matched 7,360 objects / 788,009,194 bytes in 443.653 seconds; hourly
processing took 731.664 seconds. All 24 commands exited 0 with zero deletion
failures, the disposable source ended empty, and the destination contained 240
objects. Read-only verification against the untouched baseline passed 240/240
partitions with 57,047,250 rows preserved and zero delta. No DBT/entity bootstrap
ran and no immutable source was modified. Details:
`wiki/work/raw-sensor-file-aggregation/verification.md`.

## [2026-11-13] verification | Nov 7 compacted-only DBT with durable enrichment

Ran the exact `make dbt-build` target against the completed 240-file compacted
destination, using the empty disposable source parent and the retained nine-host
durable entity snapshots. Source preflight passed; all 58 models materialized and
85 data tests were evaluated. The durable `process_entity_context_integrity` test
passed. Across 145 resources, the build returned nonzero only for the existing
`unique_selinux_interaction_event_id` test (19 duplicate rows; 127 pass, 17 skip).
Process-tree QA found 919,508 seeds but only
2 root-reached paths: 908,487 missing ancestors, 2,861 parent conflicts, 8,156
sentinel terminals and 2 missing entities. The stale week-limited state therefore
does not provide complete Nov 7 trees and remains unsuitable as a production DBT
entity input. Details: `wiki/work/durable-process-entity-manager/verification.md`.

## [2026-11-13] diagnosis | high Nov 7 ancestry-gap count explained

Reconciled the Nov 7 result with the earlier ancestry audit and QA workflow. The
908,487 `missing_ancestor` results are per-seed terminal impacts, not distinct
missing parents: 88,701 direct context rows collapse to 2,203 distinct missing
parent keys, and the top three breakpoints affect 800,504 seeds (88.1%). More
importantly, the retained durable cache is stale: all 33,824 snapshot rows cover
only partition `2026110500`, zero of 919,508 Nov 7 process keys overlap the cache,
and no current child links to a durable parent. The earlier bootstrap/maintenance
failure and stale-state warning were already recorded. Root-PID policy is not the
main cause: only one self-parent PID-4 root candidate exists and no PID-2 process
record is present. A validated historical bootstrap through Nov 7 is required
before expecting enrichment to improve ancestry completeness.
Details: `wiki/work/durable-process-entity-manager/verification.md`.

## [2026-11-13] code | durable process coverage checkpoints

Added the hourly operational checkpoint contract to Wintap-PyUtil: entity-enabled
init/replay/compact runs publish one verified Parquet row per requested UTC hour
under the sibling `processing_metrics/` prefix. Rows carry source/compacted
process inventory fingerprints, entity snapshot identities, row/file/byte totals,
deletion status and operation status. DBT now fails preflight when selected
`raw_process` hours lack exactly one successful, namespace-compatible checkpoint,
preventing stale durable entity state from being consumed silently. Local focused
tests pass (35 standalone and 12 DBT regressions); S3 qualification remains opt-in.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql -->

## [2026-11-14] verification | three-day raw qualification and DBT baseline

The isolated 72-hour all-event raw qualification preserved 151,733,675 rows,
passed 752/752 partition checks with zero row deltas, and performed no source
deletion. Durable entity bootstrap correctly failed closed on 18 unknown-identity
rows before publishing snapshots or metrics. A separate non-entity DBT baseline
completed 54 models and 84 tests with 140/140 resources passing. Gold direct-parent
coverage was 89.60%; terminal root reachability was 0.0001% because the durable
historical cache was not available. Entity-enabled DBT and post-cache gold QA
remain blocked pending an explicit unknown-identity policy decision.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py; ../Wintap-PyUtil/wintap_dbt/models/gold/process_summary.sql -->

## [2026-11-13] decision | explicit unknown-identity quarantine policy

Resolved the durable entity identity blocker. `reject` remains the default
fail-closed policy. The qualification path explicitly selects `quarantine`:
unknown/sentinel hashes, missing or negative PIDs, and invalid hostnames remain in
raw telemetry but are excluded from durable snapshots. The writer records policy,
per-hour counts, reason/host breakdowns and stable fingerprints in
`processing_metrics`; DBT requires the matching explicit policy and exposes those
rows to QA. No PID-only repair or fabricated ancestor is permitted. Standalone
reducer and DBT durable-context regression tests pass; the three-day quarantine
qualification is running separately.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql -->

## [2026-11-13] code | bounded quarantine identity threshold

Implemented and committed the configurable 5% per-UTC-hour quarantine ceiling in
the entity loader, CLI, version-3 processing checkpoints, DBT preflight and
configuration/docs. Each checkpoint records denominator, numerator, ratio,
ceiling, reasons, hosts and fingerprints; threshold violations fail before
publication and raw evidence remains available. Focused validation passed 139
standalone tests (2 skipped), 56 DBT/config tests and formatter/linter checks.
The isolated three-day rerun is in progress; final bootstrap and tree QA remain
unqualified until its results are recorded.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/processing_metrics.py; ../Wintap-PyUtil/wintap_dbt/macros/process_entities.sql -->

## [2026-11-13] verification | three-day quarantine capacity gate

The threshold-enabled 72-hour bootstrap used the explicit 0.05 per-hour ceiling
and failed closed on the existing decoded-state byte budget before publishing
any entity snapshot or processing checkpoint. The fresh qualification prefixes
remain empty; no source or compacted object was modified. Entity-enabled DBT and
post-cache tree QA were therefore not run. A read-only identity audit of the
preserved compacted process files is retained separately to report denominator,
exclusion and ratio evidence without relaxing capacity limits.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities; ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entities.py §load_inputs -->

## [2026-11-13] verification | read-only identity exclusion evidence

The preserved compacted process history was audited without writes: 71
process-bearing UTC hours, 6,439,029 distinct input rows, and 14 exclusions.
The aggregate ratio was 2.1742408676836212e-06 (0.000217424%), and the maximum
hourly ratio was 2.19346347883e-05, both below the configured 0.05 ceiling.
Reasons were negative_pid=12 and unknown_pid_hash=2; no invalid-hostname or
missing-PID exclusions occurred. Per-hour denominators, counts, ratios,
anonymized host tokens, and fingerprints are recorded in the verification page
and in the project-local machine-readable evidence file. This evidence does not
override the decoded-state byte-budget blocker; no entity DBT or post-cache tree
QA was run.
<!-- EVIDENCE: ../Wintap-PyUtil/.opencode-work/dpe-3day-quarantine-v2/reports/identity-exclusion-evidence.json -->

## [2026-11-13] verification | explicit capacity retry remained blocked

An explicitly configured entity-bootstrap retry used a 10,000,000-row limit, a
2 GiB decoded-state limit, 8 GiB DuckDB memory and 16 GiB temporary storage.
It still failed closed on the decoded-state byte budget before publishing any
entity snapshot or processing checkpoint. The isolated output prefixes remain
empty; the retry did not alter preserved source or compacted evidence. Entity
DBT and post-cache process-tree QA remain blocked.
<!-- GROUND_TRUTH: ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/entity_store.py §update_entities -->

## [2026-11-13] verification | SQL cache and entity DBT ancestry QA

The isolated SQL-backed three-day qualification completed with seven verified
snapshots and 2,613,678 entities; quarantine remained below the 5% hourly ceiling.
Entity-enabled DBT completed 146/146 PASS, and process/process-summary/path row and
key counts matched the non-entity baseline. Post-cache QA found two root-reached
seeds, zero cycles and zero resolved parent-PID mismatches, but the selected window
still lacks historical ancestors; ancestry completeness and production rollout
remain unqualified.
<!-- EVIDENCE: ../Wintap-PyUtil/.opencode-work/dpe-3day-sql/reports/post-cache-qa.json -->

## [2026-11-13] verification | repeat SQL cache qualification

A fresh isolated three-day round reproduced the first result: 27,402 source files
became 752 row-preserving compacted outputs; seven entity snapshots and 71
processing checkpoints verified; both entity-enabled DBT (146/146) and the
non-entity baseline (140/140) passed. Process key/row counts matched again, and
ancestry QA repeated two root-reached seeds, zero cycles and zero resolved
parent-PID mismatches. The selected-window ancestry-completeness limitation is
unchanged.
<!-- EVIDENCE: ../Wintap-PyUtil/.opencode-work/dpe-3day-round2/reports/post-cache-qa.json -->

## [2026-11-13] workflow | ETL diagram compaction and durable entity flow

Extended the ETL diagram/guide with the sibling `/compacted` prefix, validated
hourly compaction and DBT's name-aligned UNION ALL across `raw_sensor` plus
compacted event files. Broke out the optional per-host durable process-entity
snapshot store and its separate DBT context relations, including entity-before-
raw-deletion ordering and overlap/history caveats. Updated the index.
Follow-up: replaced diagram path strings with semantic storage labels and added a
matching path glossary to the guide; removed the interpretation and deployment
footer boxes from the diagram while retaining the important history caveats in
the Markdown.

## [2026-11-13] plan | scheduled DBT and compaction coordination with DuckDB

Human accepts cron-driven coordination through S3 messages and selects a local
DuckDB ledger. Added brief and companion design under
`wiki/work/dbt-compaction-coordination/` plus a two-page editable draw.io sequence:
shared DBT request/grant/build/release, then reader draining and exclusive hourly
compaction. Specified Python modules, cron/config, S3 and local artifacts,
transaction-before-grant ordering, DBT preflight/build wrapper integration,
single-process ledger access, durable catch-up cursor and blocked-writer recovery.
Manual abandoned-reader recovery remains the proposed v1 default. Existing Garage
conditional-write evidence grounds the single-authority design. Updated the index;
implementation and runtime qualification remain future work.
Artifact checks pass: two Markdown frontmatters/source/link checks, JSON example,
draw.io XML/geometry (42 and 44 cells), two-page viewer rendering and vertex-label
bounds, plus whitespace and privacy review.

## [2026-11-13] plan | preserve simple local-only DBT builds

Human requests preserving the direct local-raw path for small single-user environments.
Checked current Makefile defaults, missing-compacted handling, entity-disabled
branches and S3 credential-setup bypass in live PyUtil source. Added explicit
local-only compatibility criteria and mixed-root routing checks to the coordination
brief/design, plus a canonical two-command quick start and shell-override reset
instructions in the ETL guide; updated index summaries. The planned wrapper must
bypass coordination setup/messages/state for entirely local inputs and require
neither a compactor nor durable entity bootstrap. This is source-grounded planning;
wrapper runtime qualification remains future work.
Scoped checks pass: three frontmatters, live grounding paths, links/section targets,
JSON examples, two-page diagram XML and `git diff --check`; additions reviewed for
persistent-content privacy.

## [2026-11-13] handoff | scheduled DBT and compaction implementation plan

Finalized `wiki/work/dbt-compaction-coordination/dev_handoff.md` with a copy/paste
development prompt, five implementation units, live source/artifact map, local-only
compatibility and failure-point acceptance checks. Recorded the clarified polling
budget: one-minute coordinator ticks plus ten-second client polling give a nominal
70-second startup delay and 60-second release-observation delay; successful release
upload lets the client return immediately. Processing/storage/contended-writer
delays are additional. Rechecked the current compactor CLI/report contract and
explicitly covered mixed completed/skipped reports and stderr error JSON. Linked
the handoff from brief/design/index and synchronized the timing explanation.
Coordinator implementation and runtime qualification are the next development task.
Handoff checks pass: three frontmatters, 32 grounding paths, 13 wikilinks/section
targets, live source-table and prompt paths, four shell examples, JSON example,
five work units and two-page diagram XML; whitespace and privacy review pass.

## [2026-11-13] review | integrate durable entity updates and revise coordination handoff

Fast-forwarded Analytics to `d904559` and PyUtil to `c782f63`. Preserved and restored
local ETL/coordination documentation; resolved the log conflict with both workers'
entries, verified stash restoration and removed the temporary preservation stash.
Reviewed the checkpoint/quarantine/SQL-state implementation and imported three-day
qualification. The single-authority lock design remains applicable; added active
processing-metrics root binding, full entity → migration → checkpoint writer
lifetime, independent migration receipts and exclusive all-phase recovery.

Local probes reproduce stale-snapshot acceptance with retained checkpoints, lost
SQL validation checks, reset bootstrap provenance, checkpoint failure after raw
deletion, reconciliation without checkpoint publication, coverage-only completion
statuses and unused metrics-root S3 setup. Recorded findings in
`wiki/work/dbt-compaction-coordination/implementation-review.md`, updated the
brief/design/handoff, canonical entity/ETL guides, qualification cross-reference
and index. Local-shell reset now includes metrics/identity overrides. Fresh tests:
38 standalone passed; 63 main passed, 1 skipped. Remote multi-day evidence is
imported, not rerun. Coordination remains a development handoff.

Final artifact checks pass: seven frontmatters, 100 grounding paths, 38 links/section
targets, 19 live handoff source paths and prompt paths, six shell examples, JSON,
diagram XML/geometry and three rendered diagram pages with fitting vertex labels.
Cleaned up ETL edge-label collisions; reviewed complete changed content for privacy
and whitespace. Both repositories match their pulled upstream heads with no staged
or unmerged files. At review completion, documentation was uncommitted; PyUtil
retained only its two pre-existing untracked environment files.

## [2026-11-13] handoff | publish coordination plan and implementation review

Human requested committing and pushing the completed coordination handoff, source
review, updated ETL/sequence diagrams and canonical guidance. The handoff includes
specific fixes with reproduced evidence, five coordination implementation units
and worker validation gates. Recorded review-time repository status as historical
context for publication.

## [2026-11-13] ingest | initial coordination worker feedback

Recorded the human-relayed worker response in the coordination implementation
review and updated the index. The worker reports independently reproducing SQL
duplicate/scalar validation gaps and bootstrap reset, with the same focused test
counts; all findings remain open. Its recommended first milestone repairs SQL
integrity/provenance before protocol/ledger work. Added assessment criteria for
bounded SQL validation, changed/unchanged update and replay provenance, and
forward-compatible snapshot freshness. The worker's newly saved plan/verification
files are not yet available in this checkout. No contradictions flagged.

## [2026-11-13] planning | worker review and coordination implementation order

Pulled manager commit `91f741e` into Analytics; PyUtil remains at `c782f63`.
Read the new handoff/design and updated canonical guides, then inspected live
entity, checkpoint, CLI and DBT sources supporting findings R1–R5. Created
`wiki/work/dbt-compaction-coordination/implementation_plan.md` and `verification.md`,
and indexed them. The plan proposes integrity/provenance/freshness and phase-evidence
safety prerequisites before real writer/recovery integration, then preserves the
five handoff units. Protocol/ledger tests can start with fake children independently.

Independent baseline reruns pass 38 standalone tests and 63 main DBT/source tests
with one opt-in skip. Three disposable local probes independently reproduce SQL
duplicate/scalar-corruption acceptance and incremental bootstrap reset. Other manager
probes and remote three-day results remain separately attributed evidence.
No coordinator source changes, deployment or push;
implementation awaits human authorization. Temporary test fixtures are isolated
under the approved temporary root and cleaned automatically.
New-page frontmatter/grounding/link checks, diagram XML/reference checks and
complete-addition privacy/whitespace review pass.

## [2026-11-13] code | coordination safety: SQL integrity and bootstrap provenance

Human authorized implementation with four explicit red/green, bounded-SQL,
provenance and rollback/forward-evolution gates. Added independent CLI verification
and update regressions before implementation: 75 failures and ten already-rejected
controls. Restored SQL validation of keys, evidence fields/types, publication bounds
and every derived scalar/flag using separate spillable relations, and retained
validated original bootstrap metadata across changed/unchanged updates, replay and
resumed init. The new suite passes 92 tests; standalone full regressions pass 232
with two opt-in skips. A main cross-runtime rerun exposed lowercase caller-host
handling, now repaired without accepting noncanonical stored hosts; full rerun pending.

A disposable 20,000-entity SQL/no-Python-decoding probe passes initial update and
unchanged replay under explicit 256 MB/512 MB DuckDB memory/spill settings. This is
small-scale evidence, not production budget qualification. An independent real-DBT
probe permits forward evolution with differing historical hashes but still accepts
snapshot rollback with retained checkpoints: freshness remains open. Updated canonical
entity guidance, implementation/checklists, verification and index. No scheduling,
push or real-dataset mutation; unrelated local artifacts preserved.

## [2026-11-13] verification | integrity/provenance final regression gate

Final standalone suite passes 234 tests with two opt-in skips, including 94 new
integrity/provenance/compatibility cases. The main suite passes 315 with three skips
from an isolated working directory. Its initial checkout-root run passed 314 but
failed the default-config test because of a pre-existing ignored local dataset
setting; independently reproduced that dependency and left the settings file intact.
Ruff lint/format, both repositories' whitespace checks, three wiki frontmatters,
32 source anchors, ten wikilinks and privacy/diff review pass. R2/R3 are complete in
the working tree; R1 freshness, phase evidence/recovery and coordination remain open.
No commit, push, scheduler deployment or real-dataset mutation.

## [2026-11-13] milestone | committed SQL integrity and bootstrap provenance

Human requested a milestone commit and continuation of the plan. Committed only
the verified R2/R3 code/tests/README in PyUtil as `7d2b7f8`; this wiki milestone
records the red/green and full regression evidence. Unrelated local artifacts remain
untouched. Continue with formal freshness rollback/forward regressions and a selected
receipt/publication-intent contract. No push or production scheduling.

## [2026-11-13] code | receipt-backed entity freshness and historical lineage

After milestone commits PyUtil `7d2b7f8` and Analytics `739e64f`, added formal R1
regressions before implementation: ten standalone and eight real-DBT failures,
with valid forward-evolution controls passing. Implemented a SQL-owned Parquet
generation journal, recorded before/after publication intent, retained original
bootstrap/binding evidence and version-4 coverage naming its own committed receipt.
Rollback/replacement and receipt corruption fail without comparing historical
hashes to today's aggregate. Expanded focused suites pass 164 standalone and 14
real-DBT tests. Three additional null/window checkpoint cases failed before repair;
full regressions and fresh entity/metrics root cutover checks are running.

Named-struct batched hashing fixes the two DuckDB pins' incompatible unnamed-row
JSON. Preserved existing empty-parent/no-op and snapshot lost-ack semantics with
properly scoped fixtures; added independent authority failure points. Updated
canonical entity/ETL guidance, handoff/design source map, both READMEs and work
artifacts. R4/R5 and real writer/coordinator qualification remain open. Whole-store
rollback still needs an independent high-water mark. No push, production scheduler
or real-dataset mutation; unrelated local artifacts remain untouched.

## [2026-11-13] verification | freshness accepted; phase-evidence regressions recorded

R1 full standalone gate passes 266 tests with two opt-in skips. The isolated main
acceptance rerun passes 335 with three skips after preserving the existing metrics
policy-mismatch diagnostic; the initial main diagnostic-only failure and targeted
pass remain in verification history. Checked off R1, not the combined safety gate.
R4's five active-CLI behavioral tests failed before integration, including a genuine
checkpoint failure after successful source deletion. Selected an independent local
immutable run archive and explicit original-generation checkpoint repair; integration
and failure-point hardening are in progress. No push, scheduler or real-data mutation.

## [2026-11-13] verification | phase evidence and active-root prerequisites accepted

R4 captured additional failure batches of four, two, two and two before repairs,
including same-metadata byte mutation, duplicate JSON and unflushed directory links.
Final standalone passes 307 tests with two skips, including 41 archive/phase cases.
Real two-runtime repair preserves the original generation and entity/archive bytes
after deletion failure and later entity evolution; real DBT full build passes.
R5's two real behavioral failures and missing-resolver failure precede seven passing
routing cases; corrected fixture-only failures retain four active-remote controls.
Combined isolated main passes 343 tests with three skips; final affected-main passes
51 with one skip and includes the directory-link fix. Scoped lint/format, whitespace,
seven page frontmatters, 117 source anchors, 354 links and privacy scans pass.
Checked off R4/R5/dcc-00 as prerequisite regression gates, not endpoint or coordinated
writer certification. Updated verification, plan, index and canonical guidance.

Started dcc-01 tests: 26 missing-module failures are implementation-baseline evidence,
not behavioral regressions. Initial protocol passes 16 tests; real-DuckDB ledger and
failure-point hardening remain in progress. No push, scheduler installation, real
dataset mutation or new commit; unrelated local artifacts remain untouched.

## [2026-11-13] code | transactional coordination protocol and ledger

Implemented dcc-01's strict-message/S3 library and main-runtime local DuckDB ledger.
Captured six protocol and six ledger hardening failures before fixes: bounded/error
handling and cyclic pagination, orphan/overlapping writer intent, stored identity
and schema corruption, nonlocal state and transport/data-root overlap. Initial
16 protocol/10 ledger passes expand to 47 combined after repair, then 54 with real
abrupt-process COMMIT/WAL recovery and additional retention/stream controls.
Reservations/outbox commit before grant PUT; terminal tombstones are retained and
unresolved writer intent blocks restart. No expiry or automatic reopening exists.
Full isolated main acceptance is running; dcc-01 remains unchecked until review.
Updated work artifacts, source README and source map. No scheduler/client, actual
endpoint test, destructive coordinated writer, new commit or push; unrelated local
artifacts remain untouched.

## [2026-11-13] verification | protocol/ledger final focus and artifact review

Final dcc-01 focus passes 54 tests in 6.03 seconds, including abrupt process death
and actual local DuckDB WAL recovery around reader/writer COMMIT. Combined scoped
lint and 20-file format check pass; both whitespace checks and 14 new feature-file
newline scans pass. Seven wiki frontmatters, 127 source anchors, 354 links and
persistent-content privacy review pass. Full isolated main results remain pending;
no scheduler/client, writer-success/reopening API or production operation is claimed.

## [2026-11-13] verification | protocol/ledger full-main acceptance

Full isolated main passes 397 tests with three skips in 414.36 seconds, including
all 54 protocol/ledger cases and the R4 directory-link repair. Checked off dcc-01
after the recorded artifact/privacy review; scheduling, DBT lifetime and actual
writer/endpoint/resource qualification remain open. Continue controlled-clock
scheduling with fake writers, without treating exit zero as migration certification.
No new commit, push or production scheduling.

## [2026-11-13] verification | controlled-clock scheduling baseline

Started dcc-02 with 20 tick tests failing solely because the coordinator module is
absent, in 1.05 seconds. This is implementation-baseline evidence, not behavioral
regression evidence. Admission/draining and persisted-hour selection come next;
unverified writer callbacks must stay blocked without advancing the cursor.
Supervision, verified empty-hour/backlog completion and real CLI integration remain
open. No new commit, push, production scheduling or real-dataset mutation.

## [2026-11-13] code | locked admission/draining tick and atomic input hardening

Implemented dcc-02's controlled-clock tick: oldest-hour/grace selection, overlapping
readers, due-writer draining, exact grant retries and locked committed callback
intent. Captured five behavioral failures before atomic message ingestion, early
command validation and bounded observational diagnostics. Two further missing/
mismatched blocked-reason failures preceded strict reopen checks; one accidental
test placement failure was corrected with the original open-ledger control intact.
Final focus passes 100 tests in 12.35 seconds, including real abrupt tick death,
WAL recovery and a surviving synthetic child without replacement launch/admission.
All callback results remain blocked and the cursor is unchanged. Updated source
README, feature artifacts/index and canonical entity wording. Full main is running;
dcc-02 remains unchecked pending supervision, verified completion/empty hours,
cursor/backlog/reopening and status integration. No real compactor, production
scheduler, new commit or push; unrelated data/environment/settings remain untouched.

## [2026-11-13] verification | admission/draining full regression and supervisor baseline

Full isolated main passes 443 tests with three skips in 558.24 seconds, qualifying
the 100-test admission/draining revision. Scoped lint and 22-file format checks,
both whitespace checks, 16 feature-owned new-file scans, seven wiki frontmatters,
135 source anchors, 355 links and complete-diff privacy review pass. Recorded 16
missing-module failures before Linux isolated-subreaper supervision; the first
implementation passes 16 tests in 2.93 seconds. Further supervision error probes
are in progress and not covered by the earlier full regression. dcc-02 stays open;
no verified completion/reopening, real compactor, scheduling deployment, commit or push.

## [2026-11-13] code | Linux tree supervision and evolving-clock failure probes

Added a Linux/main-thread isolated-subreaper supervisor with bounded sealed-memory
control, private immutable run directories, captured stdout/stderr and exact bounded
JSON report reads. Nine active-path failures precede cleanup/capture/parser/budget/
control/exit-observation repairs; four missing-clock-interface baseline failures
precede evolving UTC refresh checks. Final combined focus passes 142 tests in
23.13 seconds: detached/nested descendants, caller interruption/death, logging/setup
failure, unrelated-child isolation, killed supervisor with surviving workload and
a real locked supervised tick callback. All callback outcomes stay blocked; no
cursor/reopening API is added. Full main for this revision is running, separate
from the earlier 443-pass admission/draining gate. Updated source README, feature
artifacts/index and canonical entity/ETL wording. External-service/non-Linux,
verified completion/high-water, status and real-compactor qualification remain
open. No production scheduler, real-data mutation, new commit or push.

## [2026-11-13] verification | supervisor revision artifact and privacy review

The 142-test supervision/evolving-clock revision passes scoped lint and 24-file
format checks. Both whitespace checks and 18 feature-owned new-file scans pass.
Nine changed wiki files pass seven frontmatters, 145 live source anchors, 355 links
and added-content privacy scans; the complete 1,331-line wiki diff was reviewed.
Full main remains running; no result inferred from focus. dcc-02 is still unchecked,
with verified completion/cursor/backlog/reopening and advisory status outstanding.
Unrelated settings/data and both local milestone commit anchors remain untouched.

## [2026-11-13] verification | supervision and evolving-clock full regression

Full isolated main passes 485 tests with three skips in 609.86 seconds
(`dcc-02-supervision-main-regression.txt`), including the final 142 coordination
cases. Recorded the result in verification, plan, design and index. Linux supervision
and evolving-clock primitives are regression accepted; dcc-02 remains unchecked
until independently verified completion/empty hours, transactional cursor/backlog
advancement, admission reopening and advisory status are integrated. No real
compactor/endpoint or production scheduler, new commit or push.

## [2026-11-14] review | dcc-02 grace boundary and atomic completion

Collaborative review reproduces a writer-priority defect with real local DuckDB
and synthetic S3: ingestion crossing grace still admits a new reader before the
next clock refresh. The control passes; the crossing assertion fails, captured
in `dcc-02-review-ingestion-clock-red.txt`. No reader/writer overlap is demonstrated.
The human confirms queued-at-deadline admission and independent completion/shutdown
verification followed by one atomic completion-evidence/run/cursor/mode COMMIT.
Updated verification, plan, design and index; code repair/success APIs remain
pending and dcc-02 stays unchecked. No code changes, production writer/endpoint,
commit or push; unrelated work is preserved.

## [2026-11-14] requirement | non-secret writer execution/configuration receipt

The human explicitly requires a durable, allowlisted, non-secret receipt binding
the actual writer invocation and resolved effective settings to committed intent
before launch. Missing/mismatched settings refuse launch; post-launch uncertainty
stays blocked. Whole-environment/credential capture and the current partial command
manifest cannot satisfy the requirement. Added the requirement and pending
identity/integrity/budget/secret-exclusion gates to brief, design, handoff, plan,
verification and index. Documentation only; no code/test changes, dcc-02 acceptance,
production operation, commit or push.

## [2026-11-14] commit | entity recovery and coordination prototype snapshot

Committed 32 feature-owned PyUtil code/test/README files as `fe7fcb5` on
`work/raw-sensor-compacted-union`; the paired Analytics wiki snapshot retains all
regression history, the known ingestion/grace defect and human-required execution
receipt/atomic-completion contracts. Fresh isolated coordination focus passes
142 tests in 25.04 seconds. Scoped lint/format passes 23 Python files; the broader
lint's 53 findings match unchanged HEAD findings in two legacy test files.
Staged scope/whitespace and complete wiki privacy/artifact checks pass. dcc-02–05
stay unchecked; no code repair, production operation or fresh full-suite claim.
Unrelated data/environment/settings remain excluded. No pushes; the human will push.

## [2026-11-14] review | pulled entity recovery and coordination milestone

Fast-forwarded Analytics `91f741e` → `660b5a8` and PyUtil `c782f63` → `fe7fcb5`.
Preserved prior feedback, resolved index/log conflicts with both histories retained,
verified restoration and dropped the preservation stash. Read the now-available
worker plan/verification and reviewed live repair, authority, phase-evidence,
DBT routing and coordination sources. Marked the original R1–R5 review as historical
and added their current implemented dispositions.

Independent real-DuckDB/fake-S3 probe confirms the worker's known ingestion/grace
admission defect (R6). A no-source-edit mutation disables SQL integrity validation
yet all 80 corruption negatives pass; direct duplicate/scalar controls prove the
validator works and isolate authority masking in the regression suite (R7).
Fresh macOS standalone suite: 305 passed, two failed, two skipped; focused main:
196 passed, three failed, 35 skipped. All five failures arise from unguarded Linux
test assumptions (R8); real-DBT freshness/repair/local routing cases pass. Linux
supervision and remote/resource qualification retain their separately attributed
worker scope. Added open R6–R8 follow-through to the plan and recorded commands,
results and qualification limits in verification; dcc-02–05 stay open. Updated
review/index/log. Five-file documentation review passes three frontmatters, 65
grounding paths, 15 links/section targets, whitespace and complete-diff privacy
checks. Review additions were uncommitted at review completion. No source changes
or deployment.

## [2026-11-14] publish | milestone review handoff to worker

Human requested committing and pushing the five review documents for worker
follow-through. The handoff records R6–R8, independent probes, fresh macOS suite
results and open implementation checklist items. Publication includes the preserved
initial worker-feedback notes and current R1–R5 dispositions.

## [2026-11-14] planning | coordination completion scope and dependency slices

Reviewed the pulled milestone comments and live coordinator/ledger/supervisor,
DBT routing, CLI/storage resolution and phase/authority verification sources.
Recorded missing completion/history/client/service APIs and the dcc-02 dependency
on dcc-04's independent verifier/high-water integration. Added six bounded slices
to the implementation plan, including R6–R8 red/green repairs, execution receipts,
macOS supervision feasibility, atomic completion, client and audited recovery.

The human selected Linux coordinator/writer, Linux/macOS readers and actual-endpoint
qualification using fresh feature-owned fixtures with exact roots/access confirmed
before writes. Initial resource qualification uses 32 GB RAM / 64 GB disk with
aggregate usage monitoring, prioritizing lifecycle completion before recommending
lower limits; a recommendation is not a qualified reduced-limit pass. Updated
design/handoff links, verification and index. R6–R8/dcc-02–05 remain open. No source
changes, runtime tests, remote operation, deployment or push during this planning.
Scoped checks pass four feature-page frontmatters, 85 grounding paths, 344 links,
whitespace and complete-diff privacy. Existing index/log frontmatter omissions
remain a separately identified baseline exception, not a whole-wiki lint pass.

## [2026-11-14] code | coordination slice A review repairs and execution baseline

R6's six formal controls reproduce four pre-repair failures; post-ingestion clock
refresh now preserves reservations and queues requests crossing grace or clock
failure. R7 retains freshness negatives and adds 80 SQL-specific direct/candidate
negatives; all fail under an in-memory validator no-op and pass normally. R8's two
procfs-denied failures precede portable fstat observations; three actual Linux-only
tick cases are guarded and two unsupported-platform refusal controls added.

Affected suites pass 150 main and 215 standalone; full standalone passes 387 with
two opt-in skips. Full main was launched but its completion is not yet recorded.
Documented fixture/harness corrections separately from behavioral defects. The new
local receipt/launch module begins with 23 missing-API failures; no implementation
or macOS support is inferred. Plan/review/verification/index updated. dcc-02–05,
actual-platform/endpoint/resource gates stay open; no remote operation, production
scheduling, commit or push. Unrelated artifacts remain untouched.

## [2026-11-14] verification | coordination slice A full main regression

The full main slice A run completes with 493 passes and three skips in 616.08 s,
before execution test/module additions. Together with 387 standalone passes/two
skips, this qualifies the repaired baseline, not slice B or integrated completion.
Five new execution hardening failures record over-envelope settings, archive/ledger
overlap, lost intent-COMMIT acknowledgment and secret-bearing launch exceptions;
three injected remote-resolution controls pass without endpoint access. Repairs
are in progress; no macOS, endpoint, production operation, commit or push claim.

## [2026-11-14] code | coordination receipt-bound local launch hardening

Implemented bounded immutable effective receipts, standalone runtime/code identity,
explicit CLI scope/budgets and same-COMMIT intent binding before launch. Eight
recorded active-path failures precede ceiling/archive, lost-COMMIT-acknowledgment,
secret-exception, nonregular-file and argument-budget repairs. Final combined
coordination focus passes 194 tests in 51.80 s (44 receipt/launch cases), including
real local empty/destructive synthetic migrations with original phase evidence.

Injected SDK scope resolution freezes non-secret endpoint/region selection and
ephemeral credentials; no secret values/hashes persist and no endpoint requests
occur. All launches still block without cursor advance; completion/high-water/
history and actual macOS/S3/resource/service gates remain open. Eight-file scoped
lint/format and both whitespace checks pass; full main is running. Updated plan,
design, handoff, verification, canonical ETL/entity pages and index. No production
operation, fixture deletion, commit or push; unrelated work remains untouched.

## [2026-11-14] code | separate completion verifier foundation

The full receipt revision passes 537 main tests (three skips) in 683.54 s, with
tested runtime sources unchanged until notification. Slice C begins with 33
standalone and nine main missing-API failures; an injected scratch prototype's
nine failures are separately attributed, not active-path evidence.

Implemented separate read-only archive/data/current-authority/historical-checkpoint
verification and main committed-receipt/intent/shutdown authentication. Eight
recorded active-path failures precede regular single-link archive reads, exact
boolean/integer checks, live-intent blocking, initialization-candidate rechecks and
sanitized request parsing. Final affected suites pass 259 standalone and 204 main;
six-file scoped Ruff lint/format passes. Original bootstraps, history and candidates
remain retained; forward evolution never compares historical hashes to today's
aggregate.

Success confers no permission transition. Main entity mode refuses until ledger
high-water initialization/enforcement is integrated; the standalone candidate is
evidence only. Ledger upgrade/history/atomic completion, full verifier regressions,
actual macOS reader shutdown, service/client/recovery and actual-S3/resource gates
remain open. README, design, handoff, plan, verification and index synchronized;
dcc-02–05 stay unchecked. No endpoint operation, production scheduling, cleanup,
commit or push; unrelated data/environment/settings remain untouched.

## [2026-11-14] verification | verifier full standalone and high-water baseline

The frozen verifier revision's full standalone run passes 431 tests (two skips)
in 172.52 s; full main remains running. Separately, two disposable active-path
pre-integration negatives fail in 1.19 s: entity reader admission and direct writer
intent creation currently lack independently initialized high-water prerequisites.
No launch occurs in these controls; repair and formal test promotion remain next.

Corrected stale Known Gaps, index identity wording, brief requirement status and
handoff source-map claims; updated plan/design and evidence scope. Fresh 13-file
scoped lint/format and both whitespace checks pass. The final wiki artifact/privacy
audit passes ten changed files, eight frontmatters, 179 grounding paths, 191 inline
sources, 377 links and seven diagram pages; baseline index/log frontmatter exceptions
remain explicit. New source/test files and tracked runtime diffs were reviewed.
Runtime sources stay frozen pending main notification. No endpoint, production scheduling, cleanup,
commit or push; dcc-02–05 remain unchecked.

## [2026-11-14] code | ledger-v2 verified entity authority integration

Frozen verifier-foundation full regressions pass 547 main tests (three skips) in
695.09 s and 431 standalone tests (two skips) in 172.52 s, before ledger integration.
Promoted the two active entity-admission/writer high-water failures into repository
tests; two absent-upgrade and six absent-verifier-interface failures are separately
attributed. Three active rehashed-observation failures precede command/capture/path
authentication repairs; one corrupt-upgrade diagnostic failure and one expected
entity-adapter integration-gate failure precede their respective repairs.

Ledger v2 retains bounded predecessor-linked authority proofs/audits and explicitly
upgrades compatible v1 state without replacing permissions, identities or uncertain
intents. Separately supervised receipt/ledger/dataset-bound initialization requires
confirmation/reason, no prior baseline and zero readers. Entity admission/intent
requires fresh same-locked-session verification; reopen/failure clears freshness and
successful intent consumes it. Main entity verification now passes local migration/
checkpoint checks without changing high-water, cursor or permissions. Forward lineage
passes while whole-journal/snapshot rollback with a retained ledger and a valid-in-
isolation same-ordinal fork refuse. Complete history/budget validation includes a
metadata-only synthetic 257-row batching control, not manufactured data/recovery proof.

Latest focus passes 236 main tests in 204.99 s and 299 standalone tests in 139.30 s;
two fork/history cases pass again after test-only cleanup. Six-file Ruff lint/format
passes. Fixture/selection errors are recorded separately from behavioral defects.
New full authority regressions are running; runtime sources/tests remain frozen until
both notifications. README, design, handoff, plan, verification, brief, canonical
ETL/entity pages and index synchronized. Completed-run history/atomic completion,
service/client/recovery, macOS reader shutdown and actual-S3/representative resource
qualification remain open. No endpoint/production operation, cleanup, commit or push;
dcc-02–05 stay unchecked and unrelated data/environment/settings remain untouched.

## [2026-11-14] verification | authority full standalone regression

The ledger-v2 authority revision's full standalone suite completes with 439 passes
and two skips in 173.60 s. Full main is still pending; runtime sources/tests remain
frozen. Updated current README/plan/handoff/design/index/verification status without
conflating these results with the earlier 547/431 verifier-foundation passes.
Completed-history/atomic completion, macOS/S3/resource and service/client/recovery
gates remain open; no endpoint/production operation, cleanup, commit or push.

## [2026-11-14] review | authority synchronization and completion safety boundary

Finished fresh feature-source review and complete wiki-diff privacy inspection.
The scoped audit passes ten changed wiki files, eight frontmatters, 195 grounding
paths, 214 inline sources, 379 links and seven diagram pages; index/log frontmatter
exceptions remain baseline, not a whole-wiki lint pass. Both whitespace checks and
15-file pinned Ruff lint/format checks pass. Unrelated data/environment/settings
remain excluded and untouched.

Clarified plan/design/handoff: the existing launch API deliberately blocks even
clean success. Normal completion needs its own uninterrupted same-lock live-intent
path with fresh independent verification and atomic evidence/history/high-water/
cursor/backlog COMMIT. Previously blocked/restart-blocked runs still require explicit
audited recovery; passing reports cannot erase uncertainty. No success API is added.
The authority full-main notification remains pending and runtime sources/tests stay
frozen without polling. No endpoint, production operation, cleanup, commit or push;
dcc-02–05 remain open.

## [2026-11-14] verification | authority full main regression and completion continuation

The frozen ledger-v2 authority revision's full main suite completes with 579 passes
and three skips in 791.61 s. Together with 439 standalone passes/two skips, this
closes that revision's full-regression checklist without accepting completion/history,
service/client/recovery, macOS/S3 or representative-resource gates. Both notifications
arrived before the runtime freeze is lifted. Updated current README/plan/handoff/
design/index/verification status; begin retained-history/atomic-completion red tests
next, preserving the conservative blocked-run API and explicit recovery boundary.
No endpoint, production operation, cleanup, commit or push; dcc-02–05 remain open.

## [2026-11-14] code | initial ledger-v3 retained completion prototype

Ten formal completion tests first fail at the missing entrypoint, then pass against
the initial v3 prototype in 66.90 s after syntax/import/format cleanup. This is an
implementation baseline, not active-path hardening or final acceptance. The new
normal-success API obtains fresh independent evidence under the uninterrupted lock;
existing conservative launch and blocked/restart recovery boundaries remain intact.
Retained evidence, run, optional authority, exact-hour cursor and backlog mode share
one transaction. Existing regressions and additional corruption/entity/crash/budget
controls are running; no pending outcome is claimed. dcc-02–05, full regressions and
service/client/recovery/macOS/S3/resource gates remain open. No endpoint operation,
production scheduling, cleanup, commit or push; unrelated artifacts remain untouched.

## [2026-11-14] code | completion-history active hardening repairs

Existing regressions complete with 126 passes and one stale v2-target assertion;
update that assertion without weakening atomic schema/identity checks. Separate
hardening reports retain seven active failures before repairs: inactive checkpoint
values, inconsistent erased audits/history, joint origin/cursor rebasing, same-session
prior-history corruption and missing fresh authority/original archive evidence.
Real local entity advancement and raw abrupt-completion-death controls already pass.

The repaired v3 prototype ties local origin/proof/run/audit/cursor integrity together,
revalidates prior history and rechecks fresh authority captures and original archive
byte identities before the atomic completion transaction. Added entity crash,
genuine-proof v2 compatibility, audit-independent semantic/secret negatives and
three-real-hour instrumented paging controls. Repaired focus is running; no pending
pass or full-regression acceptance is inferred. Two earlier 120-second outer-shell
timeouts are incomplete harness runs, not test outcomes. dcc-02–05 and platform/
endpoint/resource/service/recovery gates remain open. No production operation,
cleanup, commit or push; unrelated artifacts remain untouched.

## [2026-11-14] verification | completion hardening focus and full standalone

Repaired completion/upgrade focus passes 46 tests and independent retained-proof,
genuine-proof v2 compatibility, real paging and secret controls pass 24, before the
final three active budget/clock failures. Those failures are recorded before repairs
and then pass: receipt capture ceilings and the retained prior-completion clock floor.
Completion now has ten active red/green controls, separate from missing-API failures.

Full standalone of the final revision passes 439 tests (two skips) in 170.76 s.
Combined main coordination focus is still pending; runtime sources/tests remain
frozen without polling. Full main and fresh complete feature-source/wiki-diff reviews
remain next. README, canonical ETL/entity guidance, design, handoff, plan, index and
verification reflect local v3 completion scope without accepting dcc-02–05. Service/
client/audited recovery, actual macOS/S3 and representative resource qualification
remain open. No endpoint/production operation, cleanup, commit or push.

## [2026-11-14] verification | v3 combined focus and final source/privacy review

The frozen budget/clock revision's combined main coordination focus passes
298 tests in 517.39 s. Its report is inspected before launching full main through
the disposable-CWD harness (`dcc-completion-v3-full-main.txt`); no full-main result
is recorded yet. Runtime sources/tests remain frozen without polling. Full standalone
already passes 439 tests (two skips) on this revision.

Completed fresh tracked/new feature-source review and the entire wiki-diff privacy
inspection. Corrected stale source-map/design wording about absent local completion;
service/client/audited recovery and actual macOS/S3/resource gates remain open.
Fresh pinned Ruff lint/format passes all 18 feature Python files; both whitespace
checks pass. Scoped artifact/privacy audit passes ten changed wiki files, eight
frontmatters, 204 grounding paths, 238 inline sources, 381 links and seven diagram
pages; index/log omissions remain baseline exceptions, not whole-wiki acceptance.
No endpoint/production operation, cleanup, commit or push; dcc-02–05 stay unchecked
and unrelated data/environment/settings remain untouched.

## [2026-11-14] planning | human-run Mac baseline harness prepared

The human selects a human-run actual-Mac harness. Added the linked Mac qualification
runbook and prepared a private scratch harness/source manifest/feature-only overlay
bundle. Exact public source/lockfile identities and neutral archive metadata pass;
no datasets, credentials, virtual environments or unrelated settings are included.
Harness syntax, final pinned lint/format and actual Linux refusal before tests/output
pass; initial style cleanup is not runtime hardening evidence.

Actual Mac execution and supported reader-backend shutdown remain unqualified;
baseline passes/skips cannot close that gate. Plan/handoff/index/verification record
the selection and separate later backend acceptance. Linux full main is still running
without polling; its runtime/tests stay frozen. No endpoint operation, production
scheduling, external transfer, commit or push; dcc-02–05 stay open.
Final tracked/new wiki artifact/privacy checks pass eleven pages, nine frontmatters,
211 grounding paths, 243 inline sources, 387 links and seven diagram pages, with
index/log baseline exceptions retained. Both whitespace checks pass.

## [2026-11-14] verification | v3 full main regression complete

The unchanged v3 budget/clock revision's full main suite passes 641 tests with
three skips in 1055.19 s. The completed report and notification are inspected;
all feature Python/runtime-lock identities still match the prepared source manifest.
Together with 439 full-standalone passes/two skips and 298 combined main focus passes,
this closes the local completion/history/high-water regression gate. Both full
notifications arrived before lifting the runtime/test freeze; no source/test edits
occur during the run.

README, plan, handoff, design, brief, index, verification and Mac runbook now reflect
the completed gate. Conservative launch, blocked/restart recovery boundaries and
the original evidence/history remain intact. Actual Mac baseline/reader shutdown,
service/client/audited recovery and isolated S3/representative resources remain open;
dcc-02–05 stay unchecked. No endpoint/production operation, cleanup, commit or push.

## [2026-11-14] commit | verified completion snapshot and exact Mac next task

Human authorized feature-only commits and will test on another system. Committed
PyUtil `8ee714c0c58e9781a29b0cdc488e3aaf6ebea181`: 19 receipt/verification/authority/
completion feature files plus durable Mac harness, public manifest and harness
controls (22 files). Unrelated data/environment/settings/virtual environments remain
excluded. All 22 recorded source/runtime-lock identities are unchanged; prior
641-main/439-standalone full regressions remain distinct from harness checks.

Defined **dcc-mac-baseline-01** in
`wiki/work/dbt-compaction-coordination/macos-qualification.md`: actual Mac, exact
committed revision, separate locked native runtimes, private reports and sanitized
summary/runtime/failure/skip evidence. Supersedes the uncommitted overlay; no Mac
reader backend or shutdown acceptance is claimed. Fifteen local harness controls,
20-file pinned Ruff lint/format, syntax, actual Linux refusal and post-commit source
identity checks pass. Final scoped wiki audit passes 11 files, 9 frontmatters,
217 grounding paths, 250 inline sources, 391 links and 7 diagram pages; baseline
index/log exceptions preserved. Feature-only wiki snapshot prepared. No push,
endpoint/production operation, scheduling or cleanup; dcc-02–05 remain open.

## [2026-11-14] docs | ETL CONOPS infographic

Added `wiki/workflow/wintap-etl-conops-infographic.drawio` and its PNG preview,
grounded in the canonical ETL workflow and compaction/entity tool pages. The
local-first happy path, optional S3/compaction/context branches, four storage
concepts and bronze/silver/gold progression use 22–56-pixel type and 5–6-pixel
connectors. Overlap double-counting, bounded QA, entity-before-delete ordering,
checkpoint recovery and deferred production operation remain explicit.

Validation: XML parses with 79 native editable cells, 17 connectors, unique IDs
and valid references; the diagrams.net renderer reports no label overflow.
The 2422 × 1747 PNG was generated from that render and visually inspected.
Scoped geometry/font/connector/link/privacy checks and `git diff --check` pass.
Linked both artifacts from the workflow and updated the index. The existing
detailed diagram and all runtime/source code remain unchanged; this is a
presentation companion, not new implementation or production qualification.

## [2026-11-14] fix | committed Mac lockfile coverage and corrected handoff

The Mac worker reports the original `8ee714c` attempt blocked before either stage
because main `uv.lock` was absent from the clean checkout. Independent Git inspection
confirms 21/22 manifest files; the previous local-only post-commit check passed using
an ignored matching lock. Preserve that historical check with its limitation and the
worker's original blocked result; never relabel it as a pass.

Human-authorized corrective PyUtil commit
`fab647f900196b0bc473fe7977b7dadcf7f4ce52` tracks the exact original 593,615-byte main
lock and adds a root-only ignore exception plus committed-byte validation. Three
new controls fail before the guard; all 18 pass after it. Pinned 20-file Ruff lint/
format, syntax, actual Linux refusal and staged allowlist/identity/whitespace checks
pass. A fresh Git-only clone verifies all 22 committed/local manifest hashes and
the identity validator; all 18 controls pass again without copied ignored files or
virtual environments. Manifest and runtime hashes are unchanged.

Updated Mac runbook/prompt, handoff, plan, verification and index to the exact
corrective revision. The actual-Mac rerun requires a new private report directory;
neither Mac stage was run here. Original 641/439 Linux runtime results remain distinct.
No push, S3/production operation, scheduler installation or unrelated cleanup;
reader-backend/service/client/recovery/resource gates and dcc-02–05 stay open.
Complete six-file wiki diff/privacy review, whitespace and scoped artifact checks
pass: four frontmatters, 115 grounding paths, 129 inline sources, 352 links and two
diagram pages. Index/log frontmatter exceptions remain baseline, not whole-wiki lint.

## [2026-11-14] plan | same-server compaction status utility

Created brief, design, phased implementation plan and verification baseline under
`wiki/work/compaction-status-utility/`; linked the draft from index and canonical
HostActivity page. Human requirements: extend the existing S3 app with compacted
events/optional entity context, all/subset partition compaction, lock state and a
simple run timeline on the compaction server. Proposed four views and bounded
coordinated refreshes, independently available advisory local status, resumable
partition catalog and separate inventory/migration/deletion/coverage evidence.
Added backlog, overlap/late-arrival, storage-benefit and read-only recovery diagnostics.

Live grounding confirms raw filename charts cannot represent compacted host/time,
ordinary ledger open can mutate unresolved-writer recovery, and existing phase
sequences do not uniformly timestamp phases. Status/export/client/completion
interfaces and defaults await worker/human agreement; no new implementation or
review of worker progress beyond PyUtil `fe7fcb5`. Existing offline HostActivity
baseline passes 27 tests in 1.306 seconds on macOS, with non-failing Streamlit
warnings. Documentation checks pass five required-field frontmatters, 86 grounding
path references, 20 added wikilinks, whitespace and complete added-content privacy
review. Documentation only; no live S3, sibling edits, deployment, commit or push.

## [2026-11-14] requirement | live diagnostic observation and optional coordinated refresh

Human approved default uncoordinated Live diagnostic reads and optional Coordinated
refresh for the same-server compaction/status utility, plus an explicit exception
to the coordination contract. Revised utility brief/design/plan/verification and
coordination brief/design/handoff/plan; updated index and the canonical dashboard's
explicitly planned follow-on section. Live diagnostics may intentionally overlap
compaction/entity publication or maintenance, but always disclose partial/duplicate/
mixed-generation observations and unknown/stale writer status. Failed/incomplete
reads stay inconclusive, not zero activity, corruption or migration failure.
Cached/exported results and catalog pages retain mode/time/warnings; coordinated
failure cannot silently fall back. Both modes retain bounded supervised cleanup.

DBT, ordinary ad-hoc queries, authoritative verification, locked ledger access and
exclusive maintenance/recovery remain protected. Diagnostic reads cannot publish
completion evidence, advance the cursor or reopen admissions. The exception is
planning approval, not utility code authorization, a new worker review or dcc-02–05
acceptance. Existing 27-test HostActivity evidence is unchanged; no new app/runtime
tests, live S3, source/sibling changes, deployment, commit or push.

Scoped documentation checks pass 11 changed/new wiki files, nine required-field
frontmatters, 213 grounding path references and 28 added wikilinks/five section
targets, whitespace and added-content privacy-pattern scans. Complete additions
were reviewed for privacy and mode-contract consistency. All utility/runtime gates
remain pending; documentation is uncommitted/unpushed.

## [2026-11-14] review | pulled completion phase and blocked actual-Mac handoff

Committed authorized utility planning, then pulled Analytics `deae3a3` and rebased
the plan as `94a6688`, retaining both log histories through the sole conflict.
PyUtil's fast-forward pull was already current at `8ee714c`. Reviewed R6–R8 source
controls, effective receipts, independent verification, retained authority and v3
atomic normal completion/history; tick service/client/advisory exports/audited
recovery remain open. Refreshed utility dependencies without implementing it.

Entered developer mode for the requested tests and created a clean exact-revision
disposable PyUtil worktree on macOS 26.7.1 arm64. Main locked provisioning exits 2
because root `uv.lock` is absent from Git but required by the committed manifest;
standalone provisioning exits 0. Independent checkout validation also fails; 21/22
manifest files otherwise match. The existing ignored main lock differs and was not
substituted. R9 requests a reproducible worker handoff with the reviewed lock.

Preserved the original provisioning failure and source checks privately; sanitized
evidence is in coordination verification/review/runbook/plan/handoff and index.
Neither test stage ran, no harness summary exists, and no new Mac pass counts are
claimed. Worker Linux 641/439 full-suite and 298 focus results remain attributed.
No source/lockfile repair, real S3, deployment, new review commit or assistant push;
dcc-mac-baseline-01 and dcc-02–05 remain open. Original unrelated artifacts preserved.

## [2026-11-14] verification | repaired exact-Mac coordination baseline passes

Human selected the new worker repair, not a substitute-environment diagnostic run.
Pulled PyUtil `fab647f900196b0bc473fe7977b7dadcf7f4ce52` and Analytics `6459c74`;
rebased authorized utility planning as `1051a8c`. Preserved worker documentation,
utility planning and original `8ee714c` failed-attempt evidence through rebase/stash
resolution; preservation stash retained. No new review commit or assistant push.

New clean detached Mac checkout verifies all 22 manifest files against both local
bytes and committed Git blobs before/after testing. Exact reviewed main lock and
manifest/runtime hashes are unchanged. Both locked provisioning/import gates pass:
Python 3.12.12; main DuckDB 1.5.6/pytest 9.1.1; standalone DuckDB 2.0.0/pytest 9.2.0.
Independent isolated harness controls pass 18 tests in 0.279 s, exit 0.

Committed offline baseline on macOS 26.7.1 arm64 passes **169 main/129 skipped**
(29.53 s harness, 29.05 s pytest) and **267 standalone/zero skipped** (47.51 s harness,
47.12 s pytest), both exit 0 without timeout or failures/errors. Reviewed all 129
skips in 62 groups against committed Linux-only guards; private reports/full skip
inventory retained. Recorded sanitized versions, timings, skip boundaries and R9
repair disposition in review/verification/runbook/handoff/plan/index; refreshed
utility producer dependencies. Original blocked provisioning is not relabeled.

dcc-mac-baseline-01 is checked; dcc-02–05 remain unchecked. Mac reader shutdown,
skipped Linux writer/completion paths, service/client/advisory exports/audited
recovery, actual-S3 and representative resources remain separate. Worker Linux
641/439 full-suite and 298 focus results remain attributed, not this scoped Mac run.
No utility implementation, source repair, real endpoint/dataset operation,
scheduling, deployment, cleanup or assistant push; unrelated artifacts preserved.

Scoped documentation closure passes 11 changed wiki files, nine required-field
frontmatters, 177 grounding paths, 208 inline sources and 394 links/31 section
targets, with no new errors. Existing index/log frontmatter exceptions and one
historical broken log link are preserved baseline issues. Whitespace and complete
diff/privacy inspection pass; all stash conflicts resolved, edits unstaged and
uncommitted, preservation stash retained. Both log histories and original private
failure evidence verified intact; PyUtil unrelated environment artifacts untouched.

## [2026-11-14] finalize | publish Mac review and return remaining gates to worker

Human authorized committing and pushing the finalized wiki review plus the existing
utility planning commit. Added the worker continuation for reader-platform shutdown,
service/client/advisory exports, audited recovery and integrated S3/resource
qualification; corrected the remaining stale Mac-baseline pending statement.
The baseline result remains 169 main passed/129 reviewed Linux-only skips, 267
standalone passed and 18 harness controls passed. Original provisioning failure and
worker/maintainer histories remain separate and preserved.

Publication is documentation only: dcc-02–05 and utility implementation/deployment
remain unaccepted; production rollout and actual-endpoint access require their
existing human gates. Private reports, preservation stash and unrelated source/
environment artifacts are excluded from the commit. No further runtime execution
or sibling-source changes are part of finalization.

Finalization checks pass 11 wiki files/nine required-field frontmatters, 177 grounding
paths, 208 inline sources and 401 wikilinks/37 section targets with no new errors.
Complete diff/privacy and whitespace inspection pass; the existing broken log link
and index/log frontmatter exceptions remain baseline. Pending commit/push scope is
wiki-only; existing log history is preserved.

## [2026-11-14] feasibility | native-Mac reader shutdown needs human review

Pulled the finalized successful Mac review; Analytics is `65bff3d`, PyUtil already
`fab647f`. Scoped infographic edits reapplied without conflicts; preservation stash
and unrelated artifacts remain. Accepted Mac baseline and original failed attempt
are unchanged; no repeat baseline or status-utility implementation.

Pinned Apple source rejects automatic kqueue descendant tracking; historical
launchd cleanup covers a process group only. Installed DBT dependency inspection
and three bounded Linux controls confirm a spawned resource-tracker helper and
expected manifest-construction failure on synthetic helper-launch denial. Existing
Linux supervision rerun passes 34 tests, zero skips, in 5.82 seconds. Runner/system
Python mismatch occurred before pytest and was corrected by explicit main-runtime
invocation; no dependencies changed. This is not actual-Mac backend evidence.

Created [[wiki/tension/native-macos-readers-vs-descendant-shutdown]] and updated
coordination verification/plan/handoff/Mac runbook/index. No safe native backend is
established from investigated candidates; pause broad integration for the existing
human checkpoint. Linux/macOS scope and uncertain-reservation retention remain;
dcc-02–05 stay unchecked. No source edits, endpoint/production operations, scheduling,
commit or push; no sandbox dependency, weaker release or platform deferral selected.

Closure: 22 committed/local source-manifest identities unchanged; scoped eight-page
wiki artifact/privacy audit and both new section targets pass, as does whitespace.
Complete diff/new-page privacy review and preservation checks pass: original
infographic workflow bytes, index/log additions, diagram artifacts and retained
stash remain. Index/log frontmatter exceptions are preserved; no whole-wiki lint.

## [2026-11-14] direction | Linux-first coordination completion

Human directs finishing Linux while the native Mac worker finds its shutdown solution.
Updated coordination handoff/plan/Mac runbook/index and the open native-Mac tension:
the prior broad integration hold no longer blocks Linux. Native-Mac qualification,
uncertain-reservation retention and eventual platform scope remain separate; no weaker
release, runtime restriction or sandbox is selected. Actual-S3 roots/access and
representative sizing still require their existing inputs; no production operations,
utility implementation, commit or push is authorized by this direction.

## [2026-11-14] code | Linux coordination service and durable readers

Implemented an uncommitted PyUtil Linux service/client/root-router/advisory export and
initial audited recovery overlay. Same lock spans receipt-bound writer, independent
verification and completion COMMIT; queued admission refreshes UTC afterward. Local
Makefile preflight/build remain ordinary DBT without AWS/client state. Durable jobs
retain exact transport/request/grant/launch/terminal identities; SIGINT/SIGTERM release
only after exact shutdown evidence, preserving 130/143. Abrupt death stays reserved.

Recorded 13 missing-API failures, five hardening failures, the real SIGTERM failure,
six signal failures, four bounded state/transport/diagnostic failures and four reader
audit-retention failures before repairs. Earlier combined run: 337 passes/one stale
Make-echo assertion failure; actual local build succeeded. Later reader/lifecycle
passes 29 tests; real active-root/Makefile checks pass seven. Final combined/full
full regressions are running on a 34-identity source/runtime-lock freeze, not yet accepted.
Plan/handoff/verification retain complete attribution and preliminary probe timeout.

The combined new-path run finishes with 103 passes/one failure in 178.46 seconds:
overlapping-reader lifecycle timed out before both requests arrived. Subprocess
diagnostics were discarded by cleanup; cause remains unestablished, not attributed
to concurrent load or formatting. Five local import-isolation and four reader-audit
controls pass in that run. Full suites remain separately pending on frozen source.

Standalone full notification passes 439 tests/two skips in 167.93 seconds, exit 0;
all 34 source/runtime-lock identities remain unchanged. Twelve ordinary bounded
two-reader startup probes pass; forced first-start interleaving reproduces a shared
parent `FileExistsError` before one request. This is not proven historical-timeout
attribution. Further active-path probes reproduce cached DBT worker replay, changed
request-window dispatch and terminal retries after missing/changed shutdown or launch
evidence. These newly found gaps remain red pending main completion/source unfreeze;
no timeout extension or safety acceptance is claimed.

Main full notification finishes with 697 passes/three skips/one failure in 828.44
seconds, exit 1: the same two-request startup timeout. All 34 frozen identities
still match. Both suites are complete; source freeze released for the confirmed
reader repairs, with no historical-timeout attribution or green-main claim.

Partial/failed archives cannot reopen; broader checkpoint/deletion recovery, verified
retry and exclusive entity maintenance are unfinished. dcc-02–05, actual isolated S3,
representative sizing and native-Mac shutdown remain open. No utility implementation,
production dataset operation, scheduling installation, commit/push or unrelated cleanup.

## [2026-11-14] repair | Linux reader evidence and transport binding

Recorded 12 formal reader failures before repairing shared-parent creation, cached
DBT-worker replay, changed commands/windows and terminal launch/shutdown/outcome
authentication. Affected client/lifecycle/local-route run passes 49 tests in 15.37 s.
Invocation precedes request PUT; launch binds the manifest; original canonical
single-link records are mandatory. Fixed supervised DBT batching replaces reusable
worker dispatch. Cancellation requires retained signal outcome and no launch.
Lifecycle failure diagnostics retain bounded child exits/stdout/stderr without
changing its ten-second wait or attributing the historical timeout.

Follow-up has three active failures before resolved endpoint/region binding and
contradictory shutdown repair; four cancellation-corruption negatives already pass.
Client/lifecycle/local-route/supervisor/tick run passes 142 tests in 29.32 s before
format cleanup. Historical frozen 697/439 results do not cover repairs; combined/full
reruns and audits remain required. Broader recovery, actual-S3 and representative
resources remain open; native-Mac shutdown stays with its worker. No remote or
production operation, utility implementation, scheduling installation, commit/push.

## [2026-11-14] code | Linux checkpoint maintenance with original failure evidence

Implemented exact already-blocked entity/deletion-writer checkpoint maintenance in
the uncommitted PyUtil overlay. Durable separate receipt/intent precedes supervised
repair; success leaves the original block/cursor. Independent repaired resolution
retains actual original exit 2 and separate authenticated repair/archive evidence,
never rewriting original success. Pending failed/crashed maintenance needs audited
cannot-resume abandonment; explicit replacement retains prior checkpoint rows.
Maintenance history is bounded without pruning and rechecked on reopen.

Preserved formal evidence for missing original pre-launch observations, absent
aggregate-history ceiling, historical-proof/pending-operation conflict and future
terminal-audit acceptance. Intermediate recovery controls pass 32 main tests,
standalone repaired/verifier controls pass 66 and nine extended CLI/crash/replacement/
history controls pass. Initial repair-grammar mismatch is distinguished from fixture
argument errors. Latest scoped Ruff lint/26-file format checks pass.

Full standalone notification passes 460 tests/two skips in 191.79 s, exit 0, with
all 261 frozen source/test/DBT/runtime-lock identities unchanged. Combined affected
main remains pending; full main is not yet launched. Latest main-side timing/count/
abandonment/retained-runtime changes are not regression accepted. Source remains
frozen; historical failed fixtures and original 697/439 pre-repair results are retained.

Updated Linux runbook, README, verification, plan, handoff/index and canonical ETL
guidance with the narrow implemented scope, without full acceptance. Broader incomplete
deletion disposition, verified intentional retry and general exclusive entity
maintenance remain unfinished; dcc-02–05 stay unchecked. Actual isolated S3/access,
representative sizing and native-Mac shutdown remain separate gates. No endpoint or
production operations, installed scheduling, utility implementation, commit/push or
unrelated artifact cleanup. Complete source/wiki diff/privacy audits remain pending.

## [2026-11-14] repair | checkpoint regression paging-wrapper compatibility

Affected-main completion notification records 303 passes/one failure in 723.91 s,
exit 1. Inspected the complete report and retained fixtures/child diagnostics; all
261 original frozen identities still match. Failure is the real three-hour paging
control's connection wrapper lacking the independent cursor used by maintenance
history, not evidence for a runtime safety failure or load attribution.

Released the freeze only for that demonstrated test defect. Added cursor delegation
without changing page/corruption assertions, production validation or the ten-second
lifecycle wait. Focused control passes one test/26 deselected in 14.12 s; fresh
single-file Ruff lint/format checks pass. New 261-identity paging-repair manifest
differs only in that main test; source, standalone tests, DBT and runtime locks are
unchanged. Combined affected-main rerun is running with a separate report; full main
awaits successful affected results and post-notification identity checks. Standalone's
460-pass/two-skip result applies to its unchanged files.

Reconciled stale handoff source-map/service/clean-only recovery descriptions with
the implemented narrow checkpoint path. Broader recovery, endpoint/resource and
native-Mac gates remain open; dcc-02–05 stay unchecked. No remote/production operation,
installed scheduling, utility implementation, commit/push or unrelated cleanup.

## [2026-11-14] audit | Linux overlay source, wiki and privacy closure

Complete tracked feature diffs and new source/tests/configuration inspected;
scoped 30-file source/config/doc audit passes (15 tracked / 15 new), with fresh
Ruff lint/format passing 23 Python targets. Preserved pre-existing source-validation
test formatting; reviewed its complete necessary expectation diff separately.
Complete changed-wiki diff/new-page privacy review and infographic XML/image
inspection pass; user infographic artifacts remain unchanged. Scoped wiki audit
passes nine Markdown files/seven required frontmatters, 207 grounding paths,
257 inline sources, 416 wikilinks and 40 section targets. Zero new broken-link/
section exceptions; index/log frontmatter omissions preserved, no whole-wiki lint.
Both repositories' whitespace checks pass; unrelated data/environment work remains.

Recorded audit closure separately from pending affected-main/full-main regression
acceptance. Source freeze, original failure evidence and all broader recovery,
isolated-S3, resource and native-Mac gates remain; dcc-02–05 stay unchecked.
No runtime/source changes, endpoint/production operations, scheduling installation,
utility implementation, commit or push in this closure.

## [2026-11-14] regression | affected Linux overlay green, full main running

Paging-fixed affected-main notification passes 304 tests in 715.34 s, exit 0.
Inspected the complete report; all 261 paging-repair source/test/DBT/runtime-lock
identities still match. Retained the original 303-pass/one-wrapper-failure report
and fixtures; no historical failure is relabeled. Launched full main on unchanged
source with a separate retained report only after the green result and identity
check. Its final result remains pending; full standalone's 460-pass/two-skip result
covers its unchanged files.

Updated verification, plan, handoff, index and coordination README. Audit closure
remains separate from full regression and Linux acceptance; source stays frozen.
Broader recovery, exact isolated-S3/access, resources and native-Mac shutdown remain
open; dcc-02–05 stay unchecked. No source/runtime changes, remote/production operation,
installed scheduling, utility implementation, commit, push or unrelated cleanup.

Frozen-wait source review records the next recovery boundaries in the implementation
plan/handoff: generic reconciliation compares surviving data and can replay entities;
partial original-run disposition must authenticate retained migration evidence,
while retry/general maintenance must preserve original failures and cursor history.
No new runtime test, recovery operation, schema selection or acceptance is claimed.
Follow-up scoped wiki audit passes nine Markdown/seven frontmatters, 209 grounding
paths, 263 inline sources, 417 wikilinks and 41 section targets; both whitespace
checks pass. New documentation diff inspected for privacy; no source-freeze changes.

## [2026-11-14] regression | full Linux reader/checkpoint overlay green

Full-main completion notification passes 755 tests/three skips in 1156.34 s, exit 0.
Complete report inspected; all 261 paging-repair identities match. Together with
304 affected-main passes and 460 full-standalone passes/two skips on unchanged
standalone files, this closes local regression for the reader/checkpoint revision.
Original 303-pass/one-wrapper-failure and historical startup-failure evidence remain
unchanged and separate; no causal attribution is added.

Verification/plan/handoff/index and README updated. Retained baseline freeze and
reports; released source only for the next original-bound deletion recovery slice,
which requires its own red/green controls and regressions. Broader recovery/retry/
entity maintenance, isolated S3/access, resources and native-Mac shutdown remain
open; dcc-02–05 stay unchecked. No remote/production operation, scheduling installation,
utility implementation, commit, push or unrelated cleanup.

## [2026-11-14] repair | original-bound Linux deletion disposition controls

Provisional deletion-only maintenance preserves real original exit-2 failures and
archives, validates original migrations/current survivors/outputs and creates separate
disposition checkpoints without entity replay. Initial seven-test main integration
passes. Expanded main controls complete with 31 passes/one missing-service-command
failure in 322.34 s; the later capture control separately fails. Standalone red controls
establish exact-type and multi-hour grammar defects; corrected original-link controls
expose integer-terminal and duplicate-checkpoint acceptance. Empty-directory bounds,
pre-discovery validation and checkpoint-interference controls are also red. All complete
reports inspected; failed fixtures and the original masked-test report remain retained.

After notifications, repaired demonstrated exact comparison/order, traversal,
all-hour mutation revalidation and repair-archive/retained-capture binding; added narrow
service dispatch. Two service/capture controls pass in 26.66 s; standalone green rerun,
separate freeze, full regressions and renewed audits remain pending. Restored the
misplaced publication-failure test's retry tail; its separate control passes.
Verification/plan/handoff/index updated without deletion acceptance. Verified intentional
retry, durable exclusive entity maintenance, isolated S3/access, representative resources
and native-Mac shutdown remain open; dcc-02–05 stay unchecked. No remote/production
operation, scheduling installation, utility implementation, commit, push or unrelated
cleanup; existing environments, datasets, artifacts and prior evidence remain preserved.

## [2026-11-14] verification | deletion scope correction and separate source freeze

Initial standalone deletion rerun finishes with 47 passes/two failures in 86.45 s;
complete report and fixtures retained. Both multi-hour repair/original-preservation
assertions pass before the test's appended public one-hour verification tail fails.
Corrected only the test scope: both public multi-hour refusals remain asserted;
lower-level read-only disposition follows independent current-authority setup.
Focused corrected controls pass two tests/30 deselected in 4.33 s, complete report
inspected. No public scope or runtime safety boundary widened.

Scoped 11-target Ruff lint/format passes after formatting/import cleanup. Created
separate 265-identity deletion source/test/DBT/runtime-lock freeze; main and standalone
focused runs are running with distinct retained reports. Updated Linux runbook,
README, canonical ETL guidance, verification and plan with provisional disposition,
separate resolution and retained original failure. Full regressions and renewed
source/wiki/privacy closure remain required; no deletion or dcc-02–05 acceptance.
Broader retry/entity maintenance, isolated S3/access, resources and native-Mac
shutdown remain open. No remote/production operations, scheduling installation,
utility implementation, commit/push or unrelated cleanup.

## [2026-11-14] verification | frozen standalone deletion focus green

Frozen standalone deletion focus passes 49 tests in 90.48 s, exit 0. Complete
retained report inspected after notification; all 265 deletion source/test/DBT/
runtime-lock identities still match. Main focus remains pending; source/tests stay
frozen until its result, full-report inspection and identity check. Affected/full
regressions and renewed source/wiki/privacy closure remain required. No deletion
or dcc-02–05 acceptance, remote/production operation, scheduling installation,
utility implementation, commit, push or unrelated cleanup.

## [2026-11-14] verification | both frozen deletion focuses green

Main deletion focus passes 33 tests in 348.84 s, exit 0; complete report inspected
after notification and all 265 frozen identities match. Together with the 49-pass
standalone focus, this permits separate affected-main/standalone regressions, now
running with distinct retained reports on unchanged source. Full regressions await
successful affected results and post-notification identity checks. Fresh 11-target
Ruff lint/format checks pass; source/tests remain frozen.

Reconciled design/handoff/index with provisional original-bound deletion disposition
and the one-hour public completion boundary. Broader retry/entity maintenance,
isolated S3/access, representative resources and native-Mac shutdown remain open;
dcc-02–05 stay unchecked. No endpoint/production operations, installed scheduling,
utility implementation, commit, push or unrelated cleanup.

## [2026-11-14] audit | deletion source and wiki review closed

Read all 11 deletion runtime/test targets completely and reviewed service/client,
effective-input/configuration/operator guidance. Deletion freeze differs from the
accepted reader/checkpoint baseline in seven existing Python files plus four new
deletion source/test files; all other frozen identities match. Fresh scoped Ruff
lint/format checks pass. Complete changed-wiki diff/new-page privacy inspection,
including the earlier unread retained-diff prefix and subsequent doc updates, is
closed. Scoped audit passes nine Markdown/seven frontmatters, 217 grounding paths,
276 inline sources, 421 wikilinks and 45 sections; zero new errors, with index/log
exceptions preserved. Both whitespace checks pass. Unrelated infographic, dataset,
environment and historical failure artifacts remain untouched.

Affected main/standalone regressions remain running on frozen source; full suites
await successful notifications, complete reports and identity checks. Review closure
does not establish deletion or dcc-02–05 acceptance. Broader retry/entity maintenance,
isolated S3/access, resources and native-Mac shutdown remain open. No remote or
production operations, installed scheduling, utility implementation, commit/push.

## [2026-11-14] regression | deletion affected standalone green

Affected standalone notification passes 203 tests in 177.37 s, exit 0. Complete
report inspected and all 265 deletion source/test/DBT/runtime-lock identities match.
Launched full standalone on unchanged source with its own retained report only
after those checks. Affected main remains pending; full main has not started.
Source/tests stay frozen, and no full-suite or deletion acceptance is inferred.

Verification/plan/handoff/index and coordination README reflect this result and
pending launches. Prior failures, original archives and unrelated artifacts remain
preserved. Verified retry/entity maintenance, isolated S3/access, representative
resources and native-Mac shutdown stay open; dcc-02–05 remain unchecked. No remote
or production operations, installed scheduling, utility implementation, commit/push.

Read-only next-slice review adds planned retry/COMMIT/exclusive entity controls to
the implementation plan, without running them or selecting a new schema. Existing
maintenance remains original-blocked-writer-only; deterministic entity pending
recovery still rejects changed candidates/inputs/provenance. Corrected design wording
to distinguish current verified completion from the separate unimplemented retry
disposition. No frozen source/test identities changed.

## [2026-11-14] regression | deletion full standalone green

Full standalone notification passes 509 tests/two opt-in isolated-S3 skips in
274.88 s, exit 0. Inspected the complete report and verified all 265 deletion
source/test/DBT/runtime-lock identities after notification. The standalone affected
and full gates now pass on the frozen revision; affected main remains pending and
full main has not started. No main result, combined deletion acceptance or actual
endpoint qualification is inferred; source/tests stay frozen.

Verification/plan/handoff/index and coordination README updated. Original failed
reports/archives and unrelated artifacts remain preserved. Retry/entity maintenance,
isolated S3/access, representative resources and native-Mac shutdown remain open;
dcc-02–05 stay unchecked. No remote/production operation, installed scheduling,
utility implementation, commit or push.

## [2026-11-14] regression | deletion affected main green, full main running

Affected main notification passes 515 tests/one explicit isolated-local compactor/DBT
migration opt-in skip in 1345.33 s, exit 0. Inspected the complete report and verified
all 265 deletion source/test/DBT/runtime-lock identities after notification. Full main
is now running on unchanged source with a distinct retained report, launched only
after those checks. Full standalone's 509-pass/two-opt-in-S3-skip result remains
separate; no full-main outcome or combined deletion acceptance is inferred.

Updated verification/plan/handoff/index and coordination README. Source/tests remain
frozen; original failures and unrelated artifacts remain preserved. The elapsed time
does not establish load attribution or alter the lifecycle's ten-second wait. Broader
retry/entity maintenance, exact isolated S3/access, representative resources and
native-Mac shutdown stay open; dcc-02–05 remain unchecked. No remote/production
operations, installed scheduling, utility implementation, commit or push.

## [2026-11-14] regression | deletion combined local gate closed

Full main notification passes 788 tests/three skips in 1492.66 s, exit 0. Complete
report inspected; all 265 deletion source/test/DBT/runtime-lock identities match and
the manifest hash is unchanged. Together with 515 affected-main passes/one opt-in
skip, 203 affected-standalone passes and 509 full-standalone passes/two opt-in S3
skips, this closes deletion's combined local regression gate. Each full suite began
only after its own affected pass, complete-report inspection and identity check.
Historical failures, original archives and elapsed-time interpretations are unchanged.

Reconciled verification, plan, handoff, index, canonical ETL guide, coordination
README and Linux runbook. Retain the accepted freeze/reports and release source for
the separate retry/durable entity-maintenance slice with new red/green controls and
regressions. This is not dcc-02–05 or Linux acceptance: exact isolated S3/access,
representative sizing/reduced-budget rerun and native-Mac shutdown remain open.
No remote/production operation, installed scheduling, utility implementation,
commit, push or unrelated cleanup.

## [2026-11-14] implementation | retry read-only prerequisite red controls

After deletion's local regression closure, retained its baseline and added a narrow
read-only retry preflight with no ledger transition/schema change. Complete red
reports establish 18 standalone and nine main missing-module failures after actual
synthetic merge failures; main retains exit 2 and stopped-child evidence. The first
standalone rerun has two failures/16 scope-masked negative passes because its reused
fixture still enables deletion. Those passes are not active corruption evidence;
retain failures and correct the fixture scope before rerunning all controls.

Verification/plan/handoff updated. Durable retry, exclusive entity maintenance,
new focused/affected/full evidence, isolated S3/access and representative resources
remain open. Native-Mac shutdown stays with its worker; dcc-02–05 stay unchecked.
No remote/production operation, installed scheduling, commit, push or unrelated cleanup.

## [2026-11-14] verification | retry fixture correction exposes late-prefix gaps

Inspected main's complete first-rerun report and retained original receipt: one
failure/eight passes in 27.09 s, with inherited deletion enabled and no verifier
launch. Like standalone's first rerun, these negatives are scope-masked, not active
corruption coverage. Both helpers now disable deletion before the original merge;
runtime deletion/entity/scope refusal remains unchanged and prior evidence retained.

Corrected standalone rerun finishes with 19 passes/two failures in 2.36 s, exit 1;
complete report inspected. Previously masked controls now pass, but late marker and
empty output changes after the second data recheck are wrongly accepted. Retain the
failed fixtures and repair the final-prefix gap before freeze/regression claims.
Corrected main result remains separate. Updated verification/plan/handoff; durable
retry/entity operations, endpoint/resource gates and dcc-02–05 remain open. No
remote/production operation, installed scheduling, commit/push or unrelated cleanup.

## [2026-11-14] implementation | retry late-prefix repair and extended controls

Corrected main preflight passes nine controls in 30.17 s, exit 0; complete report
inspected. Repaired standalone's demonstrated late-marker/output gaps with content
and both-prefix checks after each data observation. Expanded standalone passes
45 controls in 4.34 s, exit 0; complete report inspected. New controls cover strict
request/checksum/regular-file refusal, original archive/context binding, late input/
archive changes and request/result budgets. Main's extended controls remain separate.

All 265 accepted deletion baseline identities still match. Updated source guidance,
design/index/verification/plan; scoped wiki audit passes nine Markdown/seven
frontmatters, 221 grounding paths, 288 inline sources, 423 links and 47 sections;
both whitespace checks pass. Four-target Ruff identifies an import-order issue in
the extended main test, deferred until its run finishes; no fresh lint pass is claimed.
Separate retry freeze/regressions and durable retry/entity operations remain open,
as do isolated S3/resources/native-Mac gates and dcc-02–05. No remote/production
operation, installed scheduling, commit/push or unrelated cleanup.

## [2026-11-14] repair | retry original-intent source-count binding

Extended main report finishes with three failures/30 passes in 112.87 s, exit 1;
complete report inspected. Changed source rows/files/bytes are accepted despite
valid shutdown and consistently rehashed verifier captures; all controls reach
actual independent launch. Preserve these failures/fixtures, without reinterpreting
the earlier nine-control pass or standalone's 45-control result.

Main now reads bounded original migration-intent JSON, authenticates its link to
the captured blocked terminal, bounds individual/aggregate totals and requires exact
independently reported rows/files/bytes. No main data SQL, ledger schema, retry
permission or cursor mutation. Combined the main test's duplicate protocol import;
four-target Ruff lint passes. New 33-main/45-standalone retained reruns are running;
two format-only changes are deferred until their notifications. Separate review,
freeze/focused/affected/full gates remain open. All 265 deletion identities still
match before repair. Updated verification/plan/handoff/index and runtime guidance;
dcc-02–05 and durable retry/entity/S3/resources/native-Mac gates remain open. No
remote/production operation, installed scheduling, commit/push or unrelated cleanup.

## [2026-11-14] verification | retry controls green and separate frozen focuses

Repaired retry preflight passes 33 main controls in 113.08 s and 45 standalone in
4.19 s, exit 0; complete reports inspected after notifications. Main's three changed
rows/files/bytes controls now refuse while retaining the original failed run,
archive, cursor and admission block. Prior failures/fixtures remain unchanged.

After both notifications, applied two format-only changes; fresh four-target Ruff
lint/format checks pass. Read all four new source/test files completely and reviewed
their JSON-only count authentication, request-before-launch, independent data/
capture/recheck and budget/refusal boundaries. Complete changed-wiki diff and new
native-Mac tension page inspected for privacy; scoped audit passes nine Markdown/
seven frontmatters, 221 grounding paths, 289 inline sources, 423 links and 47 sections;
both whitespace checks pass. No whole-wiki lint claim or unrelated cleanup.

Created the separate 269-identity retry freeze; comparison adds only the four retry
files and retains all 265 accepted deletion identities. Frozen standalone focus
passes 45 controls in 4.18 s; frozen main passes 33 in 112.95 s, exit 0. Complete
reports inspected and all identities match after each notification. Launched each
affected regression only after those checks; both affected suites are running and
neither full suite has started. Reconciled stale verification/plan/handoff/index
after two failed documentation patch attempts; historical evidence remains intact.
Source/tests/DBT/runtime locks stay frozen, and each full launch requires its own
affected notification, complete-report inspection and unchanged-identity check.
Preflight grants no retry permission. Durable retry/entity operations, isolated
S3/access, resources and native-Mac shutdown remain open; dcc-02–05 stay unchecked.
No remote/production operation, installed scheduling, utility implementation,
commit or push.

## [2026-11-14] regression | retry affected standalone green

Affected standalone notification passes 248 tests in 179.13 s, exit 0. Complete
report inspected and all 269 retry source/test/DBT/runtime-lock identities match.
Launched full standalone on unchanged source with its own retained report only
after those checks. Affected main remains running; full main has not started.
Source/tests stay frozen; no full-suite or retry permission is inferred.

Verification/plan/handoff/index reflect the result and pending gates. Renewed
scoped wiki and both whitespace checks pass; complete previously reviewed diff
plus documentation-only delta inspected for privacy. Original failures/archives
and unrelated artifacts remain preserved. Durable retry/entity integration,
isolated S3/access, resources and native-Mac shutdown remain open; dcc-02–05 stay
unchecked. No remote/production operation, installed scheduling, utility
implementation, commit or push.

Read-only next-slice review adds explicit ordering to the plan/handoff: v3's single
unresolved owner and genuine completion history preclude fake completion or deletion
of the failed original to enable retry. Entity-only operations need distinct bounded
receipts/verification/ownership, without widening public one-hour `compact` validators.
Existing `init-authority` verifies committed snapshots rather than creating them;
pending entity recovery must retain original candidates/input/window/bootstrap.
No schema version is selected, no new retry/entity result is claimed, and frozen
source/tests remain unchanged. The follow-up scoped audit found one newly added
handoff section-link typo; corrected it to the existing operator-recovery heading.
Rerun passes nine Markdown/seven frontmatters, 221 grounding paths, 294 inline
sources, 424 links and 48 sections. The complete previously reviewed diff plus
all new documentation deltas is privacy-reviewed; fresh four-target Ruff lint/
format and the unchanged 269-identity check pass.

## [2026-11-14] regression | retry full standalone green

Full standalone notification passes 554 tests/two opt-in isolated-S3 skips in
287.54 s, exit 0. Complete report inspected and all 269 retry source/test/DBT/runtime-
lock identities match; manifest hash unchanged. Its full suite began only after the
248-pass affected notification, complete-report inspection and unchanged-identity
check. Both standalone regression gates pass; affected main remains running and
full main has not started. No combined closure, retry permission or endpoint pass
is inferred, and source/tests/DBT/runtime locks stay frozen.

Updated verification/plan/handoff/index. Original failures/archives and unrelated
artifacts remain preserved. Durable retry/entity integration, isolated S3/access,
representative sizing/reduced-budget rerun and native-Mac shutdown remain open;
dcc-02–05 stay unchecked. No remote/production operation, installed scheduling,
utility implementation, commit or push.

## [2026-11-14] regression | retry affected main green, full main running

Affected main notification passes 548 tests/one approval-gated isolated-local
compactor/DBT migration skip in 1446.75 s, exit 0. Complete report inspected and all
269 retry source/test/DBT/runtime-lock identities match; manifest hash unchanged.
Launched full main on unchanged source with its own retained report only after
those checks. Full standalone's 554-pass/two-opt-in-S3-skip result stays separate;
no full-main, combined retry-preflight closure or Linux acceptance is inferred.
Source/tests/DBT/runtime locks remain frozen; elapsed time does not establish load
attribution or change the lifecycle's ten-second wait.

Updated verification/plan/handoff/index, coordination README and Linux runbook.
Original failed reports/archives and unrelated artifacts remain preserved. Durable
retry/entity integration, isolated S3/access, representative sizing/reduced-budget
rerun and native-Mac shutdown remain open; dcc-02–05 stay unchecked. No remote/
production operation, installed scheduling, utility implementation, commit or push.

## [2026-11-14] regression | retry preflight combined local gate closed

Full main notification passes 821 tests/three approval-gated skips in 1602.08 s,
exit 0. Complete report inspected and all 269 retry source/test/DBT/runtime-lock
identities match; manifest hash unchanged. Combined with 548 affected-main passes/
one opt-in skip, 248 affected-standalone passes and 554 full-standalone passes/two
opt-in S3 skips, this closes the read-only preflight local regression gate. Each full
suite began only after its own affected notification, complete-report inspection and
unchanged-identity check. Fresh four-target Ruff lint/format pass; no regression
remains running. Historical failures, scope-masked disclaimers and original archives
stay intact; elapsed time establishes no load attribution or lifecycle wait change.

Reconciled verification/plan/handoff/index, coordination README and Linux runbook;
promoted stabilized read-only semantics to the canonical ETL guide. Retain the
269-identity baseline and reports before new durable retry/entity slices with their
own controls/regressions. No retry disposition, cursor/admission transition or entity
permission is supplied by preflight. Exact isolated S3/access, representative sizing/
reduced-budget rerun, native-Mac shutdown and dcc-02–05 remain open. No remote/
production operation, installed scheduling, utility implementation, commit or push.

Closure review inspected the complete changed-wiki diff and new native-Mac tension
page for privacy. Renewed scoped audit passes nine Markdown/seven frontmatters,
223 grounding paths, 297 inline sources, 425 links and 49 sections; both whitespace
checks pass. Index/log exceptions, unrelated infographic/data/environment artifacts
and retained historical reports remain unchanged; no whole-wiki lint claim.

## [2026-11-14] implementation | intentional-retry ownership red controls started

Final documentation closure delta inspected; renewed scoped audit and both
whitespace checks pass, with all 269 accepted preflight identities unchanged.
Retain that baseline and reports. New genuine failed-merge controls target fresh
receipt/intent ownership, exact original preservation/cursor, actual COMMIT/launch
crashes, lost acknowledgment, evidence refusal and v3-compatible upgrade. First
retained red run is pending; runtime implementation has not changed. Selected design
adds explicit v4 bounded retry dispositions without completing or deleting failed
originals or temporarily reopening admission. Entity-only ownership remains separate;
dcc-02–05 and actual endpoint/resource/native-Mac gates stay open. No remote or
production operation, scheduling installation, utility implementation, commit/push.

First red notification finishes with 11 failures in 28.20 s; complete report
inspected, failed fixtures retained and all 269 baseline identities rechecked before
runtime edits. Initial implementation adds explicit v4 compatible upgrade/bounded
dispositions and fresh receipt-bound retry intent, preserving failed originals and
cursor without reopening. Private launch refactoring preserves conservative and
normal-success APIs. Four-target Ruff lint/format pass; first 11-control rerun is
running. No new retry/service/Linux acceptance is inferred.

First rerun finishes with six failures/five passes in 56.13 s, exit 1; complete
report inspected and failures retained. Fresh synthetic diagnosis finds incorrect
pretty-print reconstruction of actual CLI errors; repair retains/authenticates
their exact original bytes separately from parsed JSON. Extended controls add
late-input and same-count changed-content refusal, including audited recovery.
The first extended run is interrupted, not passed; its report/fixtures remain
intact. Human reports the connection fixed; process inventory shows no surviving
test/compactor from that run. Launched a fresh 13-control rerun on unchanged
source/tests with a distinct report. No service, full-suite or Linux acceptance.

## [2026-11-14] repair | intentional-retry late-input and original-identity gaps

Fresh resumed extended report finishes with two failures/11 passes in 83.33 s,
exit 1; all 68 lines inspected and fixtures retained. The original 11 controls
pass, but post-COMMIT input arrival and same-schema/same-count changed content at
launch wrongly complete. Neither is dismissed as a fixture/connectivity failure.
Reconciled verification/plan/handoff/index. Repair now targets fresh independent
post-COMMIT/pre-launch disposition and exact original/new migration-intent identity
checks shared by normal completion and audited recovery. No successor freeze,
affected/full/service gate, Linux acceptance, remote operation or commit/push.

Distinct independent post-COMMIT/pre-launch observation and exact authenticated
original/new migration-intent identities are implemented. Completion and audited
resolution share the source hash/partition/schema/count checks; the failed original
and exact cursor remain preserved on uncertainty. Repaired 13-control rerun passes
13 in 89.68 s, exit 0; complete report inspected. Five-target Ruff lint/format pass.
Follow-up removes ambient credential re-resolution from completion in favor of
already frozen ephemeral credentials and unchanged storage scope. New retained
history/compatibility/budget/evidence/service controls precede another rerun; no
successor freeze or affected/full gate exists, and Linux/dcc-02–05 remain open.

Extended 41-control run remains pending. Separate existing v2 compatibility control
retains one failure in 3.80 s: the synthetic legacy fixture wrongly includes v4's
retry-history origin. Complete 157-line report inspected. Corrected only its
version-specific event selection; genuine authority/reservation/outbox preservation
and runtime upgrade validation stay intact. Fresh focus passes one in 3.99 s,
exit 0, complete report inspected. Four intended source deltas left 265 of 269
accepted identities unchanged before that fixture correction; no successor freeze
or actual legacy-upgrade defect is inferred.

## [2026-11-14] verification | intentional-retry extended service failures retained

Extended 41-control report finishes with four failures/37 passes in 233.40 s,
exit 1; all 493 lines inspected. All failures reach missing argparse `retry-hour`
dispatch, not accepted service refusal. The 37 passes cover credential reuse,
retained semantics/history/budgets, audited clean-retry resolution and genuine v3
completion/readers/outbox/tombstones. Original report/failed fixtures stay unchanged.
Reconciled verification/plan/handoff/index. Next repair is strict Linux-only
original-receipt dispatch, confirmed/reasoned under uninterrupted exclusion and an
evolving clock, without transport/grants or permissive maintenance flags. No successor
freeze, affected/full gate, Linux acceptance, remote operation, cron install or push.

## [2026-11-14] implementation | Linux intentional-retry service controls green

Linux-only `retry-hour` loads the original receipt and uses the intentional-retry
adapter under one uninterrupted ledger lock with an evolving clock. Confirmation/
reason and early unrelated-flag refusal are mandatory; no transport/grants. Fresh
nine-target Ruff lint/format passes. Repaired original/extended/v2 combined run passes
42 controls in 244.42 s, exit 0; complete report inspected. Prior failures remain
retained. New genuine three-hour history/read-budget/paging/competing-process and
original-settings/clock service controls are lint/format-clean; their separate first
run is pending. Reconciled verification/plan/handoff/index and coordination guides.
No successor freeze or affected/full gate, entity-only ownership, Linux acceptance,
remote/production operation, installed scheduling, commit or push.

## [2026-11-14] verification | retry history restoration ordering failure retained

First genuine three-hour history/exclusion report finishes with one failure/12
passes in 60.14 s, exit 1; all 69 lines inspected and failed fixtures retained.
The late-page missing-audit refusal executes; restoration equality uses unordered
SQL rows after reinserting the original audit, with only the events list differing.
Correct deterministic complete-row test comparison, retaining all columns and runtime
validation/corruption assertions, before a distinct rerun. Other controls cover
read-budget non-pruning, historical-runtime non-reading, actual competing-process
exclusion, early flags and original-settings/evolving-clock behavior. Reconciled work
artifacts/index; no successor freeze/regression or Linux acceptance, remote mutation,
cron installation, commit or push.

## [2026-11-14] verification | retry history and v3 upgrade controls green

Deterministic complete-row comparison changes only the history test helper; runtime
validation/corruption assertions stay unchanged. Distinct history rerun passes 13 in
60.10 s, exit 0, complete report inspected. Actual v3 upgrade before/after-COMMIT
crashes and lost-ack controls pass three in 17.99 s; complete report inspected.
Genuine completion bytes/readers/outbox/tombstones survive, with no manufactured
history. New normal/recovery frozen-credential controls are running on local fixtures,
not S3. Fresh accepted-baseline comparison finds 263/269 identities unchanged; six
intended source/v2-fixture deltas, unchanged standalone/DBT/runtime locks and original
manifest hash verified. New files still need a successor freeze. Reconciled work
artifacts/index/design/ETL pointers and coordination guides. No successor regression,
entity-only permission, Linux/endpoint/resource/native-Mac acceptance, production
operation, installed scheduling, commit or push.

Credential-reuse notification passes two controls in 24.88 s, exit 0; complete report
inspected. Genuine local normal completion and audited resolution reuse the exact
frozen object without another storage resolver call; no S3/provider qualification is
inferred. Complete 14-target successor source/test review and fresh Ruff lint/format
pass, including original receipt/environment, private launch/preflight/history,
completion/recovery identities, legacy completed history and strict service dispatch.
No test run remains pending before successor freeze; affected/full gates are still
unstarted. Historical failures and unrelated artifacts remain untouched.

## [2026-11-14] regression | intentional-retry successor freeze and standalone focus

Separate 275-identity successor freeze created/checked with SHA-256
`01dc68118b911479d666c38d7495ccf6e1493bcc4c36441e0705ae9a21093f95`; accepted
269-identity preflight manifest retained unchanged. Pre-freeze scoped audit passes
nine Markdown/seven frontmatters, 223 grounding paths, 318 inline sources, 430 links
and 54 sections. Both whitespace checks pass; complete 2,600-line tracked wiki diff
privacy scan has zero findings, native-Mac tension page read. Initial scan's system-
Python subprocess incompatibility is corrected by using the explicit main runtime;
no source defect or whole-wiki lint claim.

Frozen standalone focused notification passes 45 tests in 4.20 s, exit 0; complete
report inspected and all 275 identities match. Only then launched its affected suite
with a distinct retained report. Main focus remains pending; no main affected or full
suite launched. Reconciled verification/plan/handoff/index/design and coordination
guides. Source/tests/DBT/runtime locks stay frozen; next stages require each runtime's
own notification, complete report and unchanged identities. Historical failures and
unrelated artifacts preserved. Entity-only ownership, exact isolated S3/access,
representative/reduced-budget resources, native-Mac shutdown and dcc-02–05 remain open.
No remote/production operation, installed scheduling, utility implementation, commit
or push; lifecycle ten-second wait remains unchanged, with no load attribution.

## [2026-11-14] regression | intentional-retry standalone affected green

Frozen standalone affected notification passes 248 tests in 180.48 s, exit 0;
complete report inspected and all 275 successor identities match, manifest hash
unchanged. Only then launched full standalone with its distinct retained report.
Main focus remains pending; no main affected/full suite launched. Earlier post-freeze
reconciliation audit passes nine Markdown/seven frontmatters with unchanged scoped
counts and both whitespace checks; complete 2,685-line tracked wiki diff privacy scan
has zero findings. Updated verification/plan/handoff/index/design and coordination
guides. Source/tests/DBT/runtime locks stay frozen. Historical failures and unrelated
artifacts preserved; elapsed time gives no load attribution or ten-second wait change.
Entity-only ownership, actual isolated S3/access, resources, native-Mac shutdown and
dcc-02–05 remain open. No remote/production operation, cron install, commit or push.

## [2026-11-14] regression | intentional-retry main focused green

Frozen main focused notification passes 119 tests in 512.18 s, exit 0; complete
report inspected and all 275 successor identities match, manifest hash unchanged.
Only then launched main affected with a distinct retained report. Standalone full
remains running; main full has not launched. Updated verification/plan/handoff/index/
design and coordination guides. Source/tests/DBT/runtime locks stay frozen; each full
requires its own affected notification, complete report and unchanged identities.
No Linux/entity-only/endpoint/resource/native-Mac acceptance or dcc-02–05 closure is
inferred. Historical failures and unrelated artifacts remain untouched, with no
ten-second wait change or load attribution. No remote/production operation, scheduling
installation, utility implementation, commit or push.

## [2026-11-14] regression | intentional-retry standalone full green

Frozen full standalone notification passes 554 tests/two opt-in S3 skips in 290.13 s,
exit 0; complete report inspected and all 275 successor identities match, manifest
hash unchanged. Its full launch followed its own affected notification/report/identity
checks. The live S3 approval guards were reread; skips are isolated read-only and
destination-write gates, not endpoint passes. No remote operation attempted.
Standalone successor gates are green; main affected remains running and main full
has not launched, so combined intentional-retry regression stays open. Reconciled
verification/plan/handoff/index/design and coordination guides. Keep source/tests/DBT/
runtime locks frozen. Historical failures and unrelated artifacts remain untouched;
elapsed time establishes no load attribution or ten-second wait change. Entity-only
ownership, Linux/dcc-02–05, isolated S3/access, resources and native-Mac remain open.
No production operation, scheduling installation, utility implementation, commit or push.

## [2026-11-14] regression | intentional-retry main affected green

Frozen main affected notification passes 607 tests/one isolated-local migration
opt-in skip in 1843.36 s, exit 0; complete report inspected and all 275 successor
identities match, manifest hash unchanged. Live migration approval guard reread;
the skip is not an integration or endpoint pass. Only then launched full main with
its distinct retained report. Standalone full remains green at 554/two opt-in S3
skips; full-main result and combined intentional-retry closure are not inferred.
Updated verification/plan/handoff/index/design and coordination guides. Source/tests/
DBT/runtime locks remain frozen; await full-main notification then inspect its complete
report and all identities. Historical failures and unrelated artifacts stay untouched,
with no ten-second wait change or load attribution. Linux/dcc-02–05, entity-only
ownership, exact isolated S3/access, resources and native-Mac shutdown remain open.
No remote/production operation, scheduling installation, utility implementation,
commit or push.

## [2026-11-14] regression | intentional-retry combined local gate closed

Frozen full main notification passes 880 tests/three opt-in skips in 2013.77 s,
exit 0; complete report inspected and all 275 successor identities match, manifest
hash unchanged. Combined with 119 main focus, 607 affected/one opt-in skip, 45
standalone focus, 248 affected and 554 full/two S3 opt-in skips, this closes the
intentional-retry local regression gate. Each full followed its own affected
notification/report/identity checks. Main skip guards reread: copied-S3 migration,
synthetic-S3 entities and isolated-local full migration remain unqualified. Fresh
14-target Ruff lint/format passes; no regression remains running. Retain the freeze/
reports and every historical failure before a separate entity-only slice with its
own active controls and successor gates. Updated verification/plan/handoff/index/
design and coordination guides; promoted stabilized facts to canonical ETL guidance.
Local closure does not qualify Linux/dcc-02–05, entity-only ownership, exact isolated
S3/access, representative/reduced-budget resources or native-Mac shutdown. Original
datasets/configuration/environment and unrelated work remain untouched. No remote/
production operation, scheduling installation, utility implementation, commit or push;
no ten-second wait change, manufactured evidence or unsupported load attribution.

Closure scoped audit passes nine Markdown/seven frontmatters, 223 grounding paths,
328 inline sources, 432 links and 56 sections; both whitespace checks pass. Complete
2,857-line tracked wiki diff privacy scan has zero findings; native-Mac tension page
reread. Initially misplaced closure entry moved to log tail, preserving history.

## [2026-11-14] verification | entity-only first red result retained

First entity-only run finishes with 22 failures in 35.05 s, exit 1. All 749 report
lines inspected; report `/tmp/opencode/dcc-linux-entity-operations-first-red.txt`
and failed fixtures `/tmp/opencode/dcc-retained-8kaw1iqo` retained. Missing entity
execution API causes every failure; four child controls exit 1 instead of 87, so no
entity crash boundary executes. The 22 lint/format-clean controls establish genuine
genesis/replay inputs and actual reader/raw-owner fixtures, not accepted refusal or
entity completion. All 275 intentional-retry accepted identities match afterward;
runtime, standalone verifier, DBT and locks remain unchanged. No test remains pending.
The first documentation patch failed before applying; this reconciliation records
the actual red result rather than a pending run. Updated verification/plan/handoff/
index and coordination guides. Next add standalone verifier red controls and distinct
bounded receipts/compatible ownership; public one-hour validators remain strict.
Linux/dcc-02–05, original-bound publication recovery, isolated S3/access, resources
and native-Mac shutdown remain open. No remote/production operation, installed
scheduling, utility implementation, commit or push.

## [2026-11-14] verification | entity-verifier red report fully reviewed

Standalone first run retains 64 failures in 29.53 s, exit 1. All 2,972 retained
report lines inspected; notification's extra two lines are its fixture-retention
footer. Every failure reaches the missing entity verifier after genuine prelaunch
original fixtures, not an accepted refusal or fixture defect. Preserve report
`/tmp/opencode/dcc-linux-entity-verifier-first-red.txt` and failed fixtures
`/tmp/opencode/dcc-retained-2qrtl4sg`. All 275 accepted retry identities match after
notification. New distinct-receipt controls are lint/format-clean and their separate
first red run is pending. Reconciled verification/plan/handoff/index and coordination
guides. Runtime/standalone implementation/DBT/locks unchanged; public one-hour validators
remain strict. No Linux/dcc-02–05, S3/resource/native-Mac acceptance, remote/production
operation, scheduling installation, utility implementation, commit or push.

## [2026-11-14] implementation | distinct entity receipts initial focused green

Receipt first red retains 26 missing-module failures in 0.51 s, exit 1; all 523
lines inspected and failed fixtures `/tmp/opencode/dcc-retained-_mrkbegp` preserved.
Added separate bounded entity receipt preparation/validation/loading/prelaunch recheck;
no ledger open/upgrade, dataset operation or launch permission. Fresh two-target Ruff
lint/format passes. Distinct first rerun passes 26 controls in 6.16 s, exit 0;
complete report `/tmp/opencode/dcc-linux-entity-execution-first-rerun.txt` inspected
and all 275 accepted retry identities unchanged afterward. No test remains pending.
Reconciled verification/plan/handoff/index and coordination guides. Standalone verifier
and restart-visible entity ownership remain missing; public one-hour validators,
DBT and runtime locks unchanged. Linux/dcc-02–05, original-bound publication recovery,
isolated S3/access, representative/reduced-limit resources and native-Mac shutdown
remain open. No remote/production operation, installed scheduling, utility implementation,
commit or push; no manufactured evidence or ten-second lifecycle change.

## [2026-11-14] verification | entity verifier initial green, review still open

Separate standalone verifier implementation's first rerun passes 64 controls in
36.47 s, exit 0; complete report `/tmp/opencode/dcc-linux-entity-verifier-first-rerun.txt`
inspected and all 275 accepted retry identities unchanged. Retain all first-red evidence.
Review identifies Python invalid-row collection, insufficient original-hour validation,
missing early resource/storage/work-path checks and unauthenticated historical
publication statistics; Ruff import/line-length and formatting are unfinished. Added
genuine review controls before repairs; distinct report
`/tmp/opencode/dcc-linux-entity-verifier-review-red.txt` is running. Keep active source/
controls unchanged until notification/report review. Reconciled verification/plan/
handoff/index and coordination guides. No verifier, ownership, Linux/dcc-02–05,
S3/resource/native-Mac acceptance; public one-hour validators/DBT/runtime locks unchanged.
No remote/production operation, scheduling installation, utility implementation, commit
or push; lifecycle wait and unrelated data/configuration remain untouched.

## [2026-11-14] verification | entity review red retained, fixture corrected

First review finishes with 21 failures/two passes in 5.74 s, exit 1; complete
955-line report inspected and failed fixtures `/tmp/opencode/dcc-retained-edpxkmjv`
preserved. Eighteen failures exercise loader/validation/historical-observation gaps;
three historical-statistic attacks stop at the fixture's nonexistent checkpoint
`write` method. Corrected only that call to the live `publish` API and launched
distinct `/tmp/opencode/dcc-linux-entity-verifier-review-corrected-red.txt`; source
unchanged. All 275 accepted identities rechecked unchanged. No verifier qualification
or historical corruption refusal is inferred; retain both reports before repairs.
Public one-hour validators, DBT/locks, production data, lifecycle wait, S3/resource/
native-Mac gates unchanged; no scheduling installation, utility, commit or push.

## [2026-11-14] implementation | entity verifier repairs awaiting distinct rerun

Corrected review red finishes with 21 failures/two passes in 6.94 s, exit 1; complete
901-line report reviewed and failed fixtures preserved. Genuine rehashed historical
rows/bytes/conflicts are wrongly accepted; no corruption refusal is inferred. All
275 accepted retry identities match. Added verifier-only SQL input projection/counts/
sorting, streaming compatible exclusion fingerprints and bounded diagnostics without
Python invalid-row collections. Existing writer loader/public one-hour validators
remain unchanged. Added exact original hours, early budget/storage/work-path checks,
current parent-conflict validation and separate caller-authenticated historical
publication evidence; never reconstruct history from current snapshots or archives.
Fresh four-target Ruff lint/format passes after patch-only formatting. Distinct
combined `/tmp/opencode/dcc-linux-entity-verifier-repairs-first-rerun.txt` is active;
preserve active source/controls until notification/report/identity review. Reconciled
verification/plan/handoff/index and coordination guides. Verifier, entity ownership,
Linux/dcc-02–05, S3/resource/native-Mac gates remain open. No remote/production operation,
scheduling installation, utility implementation, commit or push; lifecycle unchanged.

## [2026-11-14] verification | failed verifier repairs reviewed, UDF dependency removed

Combined repair and registration reruns each retain 12 failures/75 passes (35.57 s /
35.77 s), exit 1; both complete 1,609-line reports reviewed and failed fixtures
preserved. All 275 accepted retry identities match after latest report review. Valid
input/completion, forward evolution and quarantine fail, so negative passes are not
semantic qualification. Direct diagnostics retain the unfinished-result error and
then missing optional NumPy dependency at DuckDB UDF registration. Replaced only the
verifier UDF path with ephemeral SQL staging and one-record canonical insertion,
keeping SQL projection/sorting/counts and streamed compatible fingerprints; separate
bounded record/report limits, no pruning or runtime-lock change. Direct three-call
loader diagnostic succeeds, not qualification. Expanded compatibility/quarantine/
budgets/publication/request controls pass fresh five-target Ruff lint/format after
patch-only cleanup. Distinct first qualification run is active; combined three-module
rerun still required. Reconciled verification/plan/handoff/index and coordination
guides. Entity ownership, Linux/dcc-02–05, isolated S3/resources and native-Mac remain
open. No remote/production operation, scheduling installation, utility, commit or push;
accepted files, datasets/configuration/environment and lifecycle wait unchanged.

## [2026-11-14] verification | expanded verifier first red and selected-count repair

Expanded qualification first run retains 35 failures/9 passes in 20.71 s, exit 1;
all 4,671 original report lines preserved and reviewed through exact paragraph
deduplication with complete original-range coverage. Failed fixtures preserved and
all 275 accepted retry identities match. Nine loader controls pass; publication/
request positives and excluded-host/lifecycle negatives are masked by the new
verifier's nonexistent Inventory count attribute. Retained read-only stage trace
diagnoses the defect; replaced only that reference with bounded selected group-length
sum. Four genuine original genesis/replay input/completion diagnostics succeed; not
qualification. Fresh five-target Ruff lint/format passes; distinct three-module
combined run is active. Reconciled work artifacts/index and coordination guides.
Ownership and dcc-02–05 remain open; no remote/production operation, scheduling,
utility, commit or push. Public suppression, accepted source identities, runtime
locks, datasets/configuration/environment and lifecycle wait unchanged.

## [2026-11-14] verification | combined entity verifier green and expanded fixture controls

Combined verifier run passes 131 controls in 91.07 s, exit 0; complete report inspected
and all 275 accepted retry identities match. Ten expanded Unicode/quarantine,
SQL-owned single-row materialization, shared-file-budget and genuine nonzero-parent-
conflict controls retain five fixture failures/five passes (8.31 s). Complete 184-line
report and accepted identities reviewed; failed fixtures preserved. Four fixtures
assume Python-derived sentinel selection under legacy SQL with valid PID; one uses
invalid SQL modifier ordering. Fixture-only corrections preserve legacy SQL projection
and lower-level scope, force quarantine with missing PID and fix modifier order.
Distinct corrected run passes ten/44 deselected (8.49 s); complete report and all 275
identities reviewed. Fresh five-target Ruff lint/format passes. Separate expanded
141-control combined rerun is active; source/controls remain fixed pending review.
Completed all 3,417 lines of the retained tracked/new-Markdown privacy review snapshot;
subsequent documentation deltas require separate inspection. Reconciled work artifacts,
index and coordination guides; corrected stale canonical retry-status wording.
Durable main-side publication authentication/entity ownership, Linux/dcc-02–05, isolated
S3/resources and native-Mac shutdown remain open. No remote/production operation,
installed scheduling, utility, commit or push; accepted source/runtime locks, lifecycle
wait and unrelated artifacts remain unchanged.

## [2026-11-14] verification | expanded standalone entity verifier focus closed

Distinct expanded three-module rerun passes 141 controls in 97.91 s, exit 0;
complete four-line report inspected and all 275 accepted retry identities unchanged.
Standalone focused evidence is closed, not durable publication authentication,
ownership or successor-regression acceptance. Complete 317-line documentation delta
review passes privacy inspection; scoped audit passes nine Markdown/seven frontmatters,
223 grounding paths, 341 inline sources, 435 wikilinks and 59 sections. Reconciled
verification/plan/handoff/index and guides. Next ownership design keeps existing v4
initialization/upgrade behavior, adding explicit confirmed opt-in v5; ordinary open
never upgrades. No coordinated entity operation, endpoint/production mutation,
installed scheduling, utility, commit or push. Linux/dcc-02–05, isolated S3/resources,
native-Mac shutdown and whole-ledger rollback freshness remain open.

## [2026-11-14] verification | opt-in v5 and post-verifier ownership red reviewed

Opt-in upgrade first run retains seven failures (35.10 s), exit 1; all 295 report
lines inspected. Unsupported `target_version` masks every upgrade/refusal/crash
control; no boundary executes. Post-verifier ownership rerun retains 22 failures
(44.08 s), exit 1; all 960 report lines inspected, all reaching missing `entity_writer`.
Four child crash boundaries remain unexecuted. Both failed fixture directories and
historical reports preserved. All 275 accepted retry identities match after complete
report reviews, before source changes. Reconciled stale active statuses. Next implement
explicit opt-in v5 schema compatibility before entity permission, keeping default v4
and ordinary-open refusal. No production/remote operation, scheduling installation,
utility, commit or push; Linux/dcc-02–05, resources and native-Mac remain open.

## [2026-11-14] implementation | explicit opt-in v5 schema staging

Added confirmed compatible v1–v4→v5 schema selection under the main-runtime lock and
one actual upgrade COMMIT. Default v4 initialization/upgrade and ordinary-open refusal
remain; existing raw proof/reader/outbox/tombstone/cursor rows are preserved. Separate
entity-run/evidence tables deliberately reject nonempty history pending typed
ownership/publication/completion. First seven-control repaired run passes (36.93 s),
including actual v4 process crash/lost-ack boundaries; expanded compatibility passes
37 (48.43 s). Both complete reports inspected; other 274 accepted identities unchanged,
with only intentional `ledger.py` drift. Four-target Ruff lint/format passes.
Distinct 286-identity focused snapshot retained; 43-control genuine-history and separate
existing-ledger compatibility runs are active with source/tests fixed pending review.
Complete 316-line intervening documentation/privacy delta reviewed; updated feature
artifacts/index/design and operator guides. No entity permission or Linux/dcc-02–05
acceptance, production/remote operation, scheduling installation, utility, commit or
push. Historical failures, unrelated data/configuration, runtime locks and ten-second
lifecycle wait remain unchanged; native-Mac shutdown/resources stay separate.

## [2026-11-14] verification | opt-in v5 genuine-history focused green

Combined schema/history notification passes 43 controls in 109.80 s, exit 0;
complete three-line retained report inspected and all 286 focused identities match,
manifest hash unchanged. Genuine original authority/completion, failed-original retry,
post-v5 raw completion and original proof-corruption controls now have green evidence.
Existing-ledger compatibility remains running; source/tests stay fixed pending its
notification/report/identity review. Updated verification/plan/handoff/index/design
and operator guides. These schema results confer no entity ownership/publication,
service permission or Linux/dcc-02–05 acceptance. S3/access, resources and native-Mac
shutdown remain separate; no remote/production operation, installed scheduling,
utility implementation, commit or push. Historical failures and unrelated work retained.

Complete 371-line schema/history documentation delta inspected for privacy; fresh
scoped audit passes nine Markdown/seven frontmatters, 223 grounding paths, 350 inline
sources, 435 wikilinks and 59 sections. Four-target Ruff lint/format and both repository
whitespace checks pass. This remains scoped, not a whole-wiki or Linux acceptance claim.

## [2026-11-14] verification | retained compatibility red and diagnostic-only repair

Existing-ledger first compatibility finishes with two failures/149 passes in 401.75 s,
exit 1; complete 271-line report inspected and all 286 schema-focused identities match
before repair. Both failures execute actual COMMIT/lost-ack and original-row checks,
then fail the repeat-upgrade diagnostic regex; later assertions did not execute.
Failed fixtures and original report preserved. Restored only exact default-v4 refusal
wording, retaining opt-in-v5 wording, semantics and all tests. Other 274 accepted-retry
and other 285 schema-focused identities match; only ledger.py intentionally differs.
Separate 286-identity diagnostic-repair freeze retained; fresh five-target Ruff lint/
format passes. Repaired 46-control focus and 151-control compatibility runs are active;
source/tests stay fixed until both notifications, complete reports and identity reviews.
Reconciled feature verification/plan/handoff/index/design and operator guides. No entity
ownership/publication or Linux acceptance is claimed; S3/access, resources and native-Mac
shutdown remain separate. No remote/production operation, installed scheduling, utility,
commit or push; historical failures, unrelated artifacts and lifecycle wait retained.

## [2026-11-14] verification | diagnostic-repair focused green, compatibility pending

Repaired focus notification passes 46 controls in 127.49 s, exit 0; complete three-line
report inspected and all 286 diagnostic-repair identities match, manifest hash unchanged.
The separate 151-control compatibility run remains active; source/tests stay fixed
pending its notification/report/identity review. Complete 337-line post-schema-history
documentation delta inspected for privacy. Fresh scoped audit passes nine Markdown/
seven frontmatters, 223 grounding paths, 352 inline sources, 435 wikilinks and 59
sections; five-target Ruff lint/format and both repository whitespace checks pass.
Reconciled feature artifacts and operator guides. No typed entity ownership/publication,
Linux/dcc-02–05 or broader resource/S3/native-Mac qualification is inferred. No remote/
production operation, installed scheduling, utility, commit or push; failures preserved.

## [2026-11-14] verification | diagnostic-repair schema compatibility closed

Repaired compatibility notification passes 151 controls in 399.51 s, exit 0; complete
five-line retained report inspected and all 286 repair identities match, manifest hash
unchanged. Both frozen runs are complete; explicit opt-in-v5 schema compatibility is
closed, not typed entity permission, successor full regressions or Linux acceptance.
The original two-failure report and failed fixtures remain preserved. Complete 288-line
focus-green documentation delta inspected for privacy; reconciled feature artifacts
and operator guides. Next add separately supervised main-side entity-observation
authentication before typed ownership/history and durable publication linkage; keep
empty-history refusal until original-bound validation exists. S3/access, resources and
native-Mac shutdown remain separate. No remote/production operation, installed
scheduling, utility, commit or push; unrelated artifacts and lifecycle wait unchanged.

## [2026-11-14] implementation | read-only main-side entity input authentication

New 21-control first red retains 21 missing-module failures in 16.90 s, exit 1; all
496 report lines inspected and all 286 schema-repair identities match before coding.
Failed fixtures/report preserved. Added only a separate main-side input-observation
adapter and controls; exact canonical receipt/request/command/capture/shutdown and
original-input scope are authenticated under owner-free v5 exclusion. No main data
SQL, dataset/ledger-row mutation, authority initialization, cursor/admission transition
or entity launch. Original observations recheck actual single-link artifacts; bounded
64 KiB result/1 MiB request/128 KiB proof overflow refuses without pruning. Empty-history
guard unchanged; typed post-COMMIT ownership/publication/completion still missing.
Two-target Ruff lint/format passes after patch-only formatting. Distinct first rerun
is active; adapter/controls stay fixed pending notification/report/identity review.
All 286 schema-repair identities remain unchanged. Reconciled feature artifacts/index/
design and guides. Linux/dcc-02–05, S3/access/resources and native-Mac stay open; no
remote/production operation, installed scheduling, utility, commit or push.

## [2026-11-14] verification | entity-input command-byte red retained and repaired

First adapter rerun retains one failure/20 passes in 65.77 s, exit 1; complete 39-line
report inspected and all 286 schema-repair identities match before repair. Original
command.json newline tampering is wrongly accepted through parsed JSON equality;
the actual artifact refusal is not established. Failed fixtures/report and distinct
288-identity first-rerun source snapshot preserved. Added exact canonical command/
shutdown-byte rechecks without changing old controls; six further supervision/stderr
alias/byte controls expand the next run to 27. Two-target Ruff lint/format passes.
Separate 288-identity artifact-repair freeze retained; distinct repaired run is active,
source/controls fixed pending notification/report/identity review. No ownership/data/
authority/cursor/admission change, entity launch or broader acceptance is inferred.
Reconciled feature artifacts/index/design and guides; empty-history guard remains.
S3/access/resources and native-Mac stay separate. No remote/production operation,
installed scheduling, utility, commit or push; historical failures preserved.

## [2026-11-14] verification | entity-input artifact-repair focus green

Repaired notification passes 27 controls in 83.28 s, exit 0; complete three-line report
inspected and all 288 artifact-repair identities match, manifest hash unchanged. This
closes the repaired artifact focus only; broader main-side input qualification remains
next before typed ownership. Complete 526-line intervening documentation delta inspected
for privacy; historical red reports, failed fixtures and distinct snapshots preserved.
Successful fixtures are cleaned by the harness; reports remain the durable green evidence.
Reconciled feature artifacts/index/design and both operator guides. No entity launch,
permission/authority/cursor/admission change, successor full gate or Linux acceptance.
S3/access/resources and native-Mac remain separate. No remote/production operation,
installed scheduling, utility, commit or push; empty-history guard remains unchanged.

## [2026-11-14] verification | expanded main-side entity-input controls active

Added a separate 31-control module for genuine four-hour raw/compacted inputs and an
empty hour, exact selected-hour totals/types/bounds, committed reader/live/restarted
raw exclusion, unanchored state, actual artifacts versus rehashed dictionaries,
duplicate JSON, independent byte budgets, receipt-clock refusal and actual competing
process locks. Three-target Ruff lint/format passes; all original 288 identities match.
First retained run is active on a separate 289-identity snapshot; source/controls stay
fixed pending notification, complete report and identity review. No accepted refusal,
typed ownership/history/publication, entity launch or successor gate is claimed.
Reconciled feature artifacts/index/design and guides. S3/access/resources and native-Mac
remain separate; no remote/production operation, scheduling installation, utility,
commit or push. Historical failures and the empty-history guard remain preserved.

Complete 355-line artifact-green/expanded-pending documentation delta inspected for
privacy. Fresh scoped audit passes nine Markdown/seven frontmatters, 229 grounding
paths, 361 inline sources, 436 wikilinks and 60 section targets; both repository
whitespace checks pass. These remain scoped checks, not broader acceptance.

## [2026-11-14] verification | entity-input exact-total and early-clock reds repaired

Expanded first run retains nine failures/22 passes in 102.92 s, exit 1; complete
245-line report inspected and all 289 identities match before repair. Eight rehashed
contract controls wrongly accept hour/aggregate file/byte mismatches; clock refusal
occurs after an actual read-only verifier launch, with its later row-equality assertion
unexecuted. Neither corrupted-data acceptance nor entity launch/permission is established.
Genuine four-hour inputs, committed exclusions and actual competing locks execute and
pass; general qualification remains open. Failed fixtures/report and original snapshot
preserved. Repaired only the input adapter with exact bounded total equality and
pre-launch receipt-clock checks; all controls unchanged and other 288 identities match.
Fresh three-target Ruff lint/format passes. Separate 289-identity contract-repair freeze
binds an active combined 58-control rerun; source/controls fixed pending complete report
and identity review. Updated feature artifacts/index/design and guides. No entity
ownership/history/publication, successor full gate, Linux/S3/resource/native-Mac
acceptance, remote/production operation, scheduling installation, utility, commit or
push. Empty-history guard and all historical failures remain preserved.

Complete 320-line contract-repair documentation delta inspected for privacy; fresh
scoped audit and both repository whitespace checks pass with unchanged counts. The
58-control notification/result was still pending at this audit; its later review is below.

## [2026-11-15] verification | main-side entity-input authentication focus closed

Combined repaired run passes 58 controls in 185.12 s, exit 0; complete three-line
report reviewed and all 289 contract-repair identities match, manifest hash unchanged.
Main-side read-only input-authentication focus is closed; no test remains running.
Reconciled verification, checked only its focused plan item, handoff/index/design and
operator guides. Preserve historical reds, failed fixtures and distinct freezes.
Next add genuine explicit-v5 typed intent/restart-exclusion controls before source
implementation, reviewing the retained red and identities first. Ownership/history,
post-COMMIT binding, durable publication/completion and successor regressions remain
separate. Linux/dcc-02–05, isolated S3/access/resources and native-Mac shutdown stay
open. No entity operation outside isolated tests, remote/production operation,
scheduling installation, utility implementation, commit or push.

## [2026-11-15] verification | typed entity intent controls active

Added a separate 34-control explicit-v5 intent/restart-exclusion module before source
implementation. Genuine fixtures target multi-hour typed ownership and original-bound
post-COMMIT inputs, committed reader/raw exclusion, early contracts, actual COMMIT
crash/lost-ack, competing processes, corruption and separate read/write budgets.
First retained run was active on a 290-identity snapshot; all prior 289 input-repair
identities unchanged. Source/controls were fixed pending full report and identity review;
no crash boundary/owner acceptance or entity launch is claimed. Promoted stabilized
read-only receipt/input-authentication facts to the canonical ETL guide, preserving
the separate ownership/launch/completion/publication gates. Historical failures,
fixtures, unrelated artifacts and runtime locks retained. No remote/production work,
scheduling installation, utility implementation, commit or push; native-Mac stays separate.

## [2026-11-15] verification | typed intent first red reviewed

First run retains 34 failures (47.41 s), exit 1; complete 1,132-line report inspected
and all 290 first-red identities match after notification. Twenty-six controls reach
missing-module imports after setup, two crash children exit 1 at import rather than
87, and six budget controls fail import before setup. No semantic refusal, intent
COMMIT or crash boundary established. Complete 442-line wiki delta privacy review
passes. Reconciled stale active-run wording; no test remains running. Source work may
begin for bounded typed exclusion and original-bound post-COMMIT inputs only;
launch/completion/publication/recovery/service and broader acceptance stay separate.
Historical reports/fixtures/freezes retained; no remote/production operation or publication.

## [2026-11-15] code | exclusion-only typed entity intent prototype

Added bounded original-bound explicit-v5 intent ownership/history and same-session
post-COMMIT read-only input authentication after complete first-red/identity review.
No entity operation is launched; restart/lost acknowledgment/failed live checks retain
BLOCKED originals, without raw cursor/high-water advancement or reader admission.
Unsupported completion/publication/recovery history still refuses. Distinct 34-control
implementation rerun was active on 291 frozen identities; unchanged controls and 288 prior
identities retained, with only input adapter/ledger changes plus the new typed module.
Four-target Ruff lint/format and both whitespace checks pass; source/controls fixed
pending complete report/identity review. Wider Linux/dcc/S3/resources/native-Mac gates
remain open. No remote/production operation, scheduling installation, utility, commit or push.

## [2026-11-15] repair | typed history transaction visibility

Implementation rerun retains 33 fixture-upgrade failures/one v4 pass (34.61 s), exit 1;
all 291 identities match after notification. Complete lossless 1,307-line review
authenticates the 5,691-line report and shared 138-line body across 33 occurrences.
Typed assertions and both crash-child launches remain masked. Retained diagnosis
finds independent DuckDB cursor visibility failure; read-only fixture inspection
finds expected v4 initialization shape/no v5 residue, without a pre-diagnostic hash
or historical byte claim. Repair uses same-connection SQL-limited keyset pages and
typed history/budgets before owner-ID/JSON reads. Only typed module/ledger change;
other 289 identities and original 34 controls unchanged. Fresh four-target Ruff lint/
format passes. Separate 291-identity repair freeze binds an active unchanged-control
rerun; source/controls fixed pending notification/report/identity review. Reconciled
status in feature artifacts/index/design/guides; newer documentation still needs
complete privacy review. No entity launch/completion/publication/recovery acceptance,
remote/production operation, scheduling installation, utility, commit or push.

Complete 464-line successor documentation/privacy delta inspected, including retained
new Markdown; native-Mac tension remains unchanged. Corrected full comparison is the
review evidence, not the earlier appendix-omitting comparison. Fresh scoped audit passes
nine Markdown/seven frontmatters, 232 grounding paths, 373 inline sources, 437 links/
61 sections; both whitespace checks pass. Repair-result review was still pending.

## [2026-11-15] verification | typed transaction-repair focus green; history controls active

Unchanged repair run passes 34 controls (125.03 s), exit 0; complete three-line report
reviewed and all 291 frozen identities match after notification. Genuine typed COMMIT,
restart/lost-ack, post-COMMIT input/exclusion and original corruption/budget evidence is
established, not entity launch/completion/publication/recovery, wider regressions or
Linux acceptance. Added a separate 24-control staged visibility/corruption/rollback,
budget-before-owner/payload, real keyset-tail and rehashed-semantic module after that
green. Complete new source reviewed, patch-only lint/format fixes retain all intended
controls; fresh five-target Ruff lint/format passes. All 291 repair identities remain
unchanged; distinct 292-identity freeze binds its active first run. Source/controls
fixed pending notification, complete report and identity review. Reconciled result in
verification/plan/handoff/index/design/operator guides and canonical scope limits;
expanded history and combined focus remain separate before exclusion-only closure.
Successful fixtures are cleaned; reports remain durable green evidence. All historical
failures/freezes/fixtures and unrelated artifacts remain preserved. No remote/production
operation, scheduling installation, utility, commit or push; native-Mac stays separate.

## [2026-11-15] verification | expanded typed-history focus green; combined focus active

Separate history run passes 24 controls (79.82 s), exit 0; complete three-line report
reviewed and all 292 first-history identities match after notification, hash unchanged.
All staged-visibility/rollback, budget-before-fetch, real keyset-tail and rehashed-
semantic control groups execute without setup masking. This is expanded focused
evidence only; successful fixtures are cleaned and reports retained. Complete 428-line
successor wiki/privacy delta (including acknowledgment edits/new Markdown) and 78-line
operator delta reviewed. Fresh scoped audit passes nine Markdown/seven frontmatters,
232 grounding paths, 376 inline sources, 437 links/61 sections; both whitespace checks
pass. Separate unchanged 292-identity combined-focus freeze binds active main typed/
input/schema/receipt/original-ledger compatibility and standalone entity-verifier runs.
Source/controls fixed pending both notifications, complete reports and identity review;
exclusion-only closure awaits combined evidence. Reconciled status in feature artifacts/
index/design/operator guides; affected/full, entity execution/publication/recovery,
Linux/dcc-02–05, isolated S3/resources and native-Mac remain separate. Historical
failures and unrelated artifacts retained. No remote/production work, installed
scheduling, utility implementation, commit or push.

Complete 414-line history-green/combined-pending wiki/privacy delta and 84-line
operator delta inspected. Fresh five-target Ruff lint/format, scoped wiki audit
with unchanged counts and both whitespace checks pass. Combined-focus results
were still pending; no broader acceptance inferred.

## [2026-11-15] verification | combined standalone entity-verifier focus green

Standalone notification passes 141 controls (105.56 s), exit 0; complete four-line
report reviewed and all 292 combined-freeze identities match afterward, hash unchanged.
Main combined focus remains active; source/controls fixed pending its notification,
complete report and identity review. Exclusion-only combined closure and affected/full
qualification remain separate. Retain original reports/freezes/failures; no entity
launch/completion/recovery/service or Linux/dcc acceptance, remote/production operation,
installed scheduling, utility implementation, commit or push is inferred.

Complete 283-line standalone-green/main-pending wiki/privacy delta and 86-line operator
delta inspected; fresh scoped wiki audit and both whitespace checks pass with unchanged
counts. Main combined focus remains pending and all source/controls remain frozen.

## [2026-11-15] verification | combined entity-exclusion focus closed

Main notification passes 336 controls (884.70 s), exit 0; complete seven-line retained
report reviewed and all 292 combined-freeze identities match, hash unchanged. Both
main/standalone focuses are complete; standalone passes 141 (105.56 s). Exclusion-only
typed/input/schema/receipt/original-ledger compatibility focused evidence is closed,
not affected/full, entity launch/completion/publication/recovery or Linux acceptance.
Checked only the focused plan items and reconciled feature artifacts/index/design/
operator guides/canonical limits. Next add genuine main current-generation completion
observation red controls before source work, retaining typed original inputs/intent
and actual CLI shutdown, without ownership/authority/cursor transitions or historical
publication fallback. Historical failures/freezes/fixtures remain preserved; no
remote/production work, scheduling installation, utility implementation, commit or push.

## [2026-11-15] verification | separate main completion-observation controls active

Complete 354-line combined-main-green wiki/privacy delta and 90-line operator delta
reviewed; fresh five-target Ruff lint/format, scoped wiki audit and both whitespace
checks pass with unchanged counts. Added a distinct 44-control completion-observation
module before source implementation; complete 392-line source reviewed and new-target
Ruff lint/format passes. Genuine explicit-v5 typed fixtures retain original inputs/
intent, perform a post-COMMIT input check and launch the supervised CLI only in isolated
tests. These launches confer no service permission. All 292 focused identities remain
unchanged; distinct 293-identity freeze binds the active first run. Source/controls
fixed pending notification, complete report and identity review. No completion adapter,
semantic refusal or green is claimed; ownership/authority/cursor transitions, durable
publication/recovery, affected/full, Linux/S3/resources and native-Mac remain separate.
Historical evidence and unrelated artifacts preserved; no remote/production operation,
installed scheduling, utility implementation, commit or push.

## [2026-11-15] verification | completion-observation first red fully reviewed

First run retains 44 failures (342.12 s), exit 1; complete 409-line lossless exact-line
review inspected and reconstruction matches the entire 1,783-line report. All 293 frozen
identities match after notification. Twenty-two missing-module, 19 launch-guard and
three budget import failures mask every completion-adapter assertion after genuine
typed/post-COMMIT/supervised-CLI fixture execution; the forward fixture also launches
its second isolated CLI. No adapter semantic refusal/green established. Failed report,
fixtures and freeze retained; no test remains active. Earlier complete 244-line
completion-pending wiki/privacy delta inspected and scoped audit/whitespace checks pass.
Reconciled feature status; original-bound read-only completion source work may begin.
Ownership/authority/cursor transitions, durable historical publication/recovery,
affected/full, Linux/S3/resources and native-Mac remain separate. No remote/production
operation, installed scheduling, utility implementation, commit or push.

## [2026-11-15] code | read-only current-generation completion adapter active

Added separate main completion adapter after complete first-red/identity review.
It binds original typed/receipt and post-COMMIT prelaunch, actual CLI/archive/canonical
command/shutdown and distinct capture bytes, plus fresh standalone completion core/
transport evidence. Replay bootstrap provenance remains original; exact current
genesis/immediate-successor and `publication: None` preserve historical refusal.
No entity command is launched and no ownership/authority/cursor/acknowledgment transition
occurs, even on refusal. Complete source reviewed; two-target Ruff lint/format and PyUtil
whitespace check pass. All 293 first-red identities unchanged; distinct 294-identity
implementation freeze binds the active unchanged 44-control rerun. Source/controls
fixed pending notification, complete report and identity review before repair. Expanded
completion, affected/full, durable publication/recovery/service, Linux/S3/resources and
native-Mac remain separate. Historical evidence/unrelated artifacts retained; no remote/
production operation, installed scheduling, utility implementation, commit or push.

Complete 496-line red-reviewed/implementation-pending wiki/privacy successor delta
inspected; both operator documents remain unchanged from the pre-completion baseline.
Scoped audit passes nine Markdown/seven frontmatters, 235 grounding paths, 384 inline
sources, 438 links/62 sections; both whitespace checks pass. Implementation result
remains pending, and all source/controls stay fixed. Follow-up review corrected this
acknowledgment's placement under the current entry rather than historical retry work.

## [2026-11-15] verification | completion implementation result reviewed; fixture repair next

Implementation run retains two failures / 42 passes (470.91 s), exit 1. Complete
81-line report inspected and all 294 implementation identities match after notification.
Both duplicate-`prelaunch` helper arguments fail before adapter invocation, masking
missing-prelaunch and precommit-substitution refusals. Initial completion focus remains
unaccepted. Reconciled feature verification/plan/handoff/design/index; no test remains
active. Next rename only the helper positional parameter/default reference and rerun
all 44 controls on a separate freeze, preserving runtime/assertions and historical
reports/fixtures/freezes. Expanded completion, affected/full, durable publication/
recovery/service, Linux/S3/resources and native-Mac remain separate. No remote/production
operation, scheduling installation, utility implementation, commit or push.

## [2026-11-15] repair | completion fixture helper only; all-control rerun active

Renamed only the helper positional `prelaunch` parameter/default-value reference so
keyword overrides reach the adapter. Exact two-line diff reviewed; every assertion,
runtime source and other 293 implementation identities unchanged. Two-target Ruff
lint/format and PyUtil whitespace check pass. Separate 294-identity fixture-repair
freeze binds the active all-44-control rerun. Source/controls fixed pending notification,
complete report and identity review before repair/acceptance. Retain import-red and
implementation-helper reports/freezes/failed fixtures. Expanded completion and broader
entity/service/affected/full, Linux/S3/resources/native-Mac remain separate. No remote/
production work, scheduling installation, utility implementation, commit or push.

Complete 353-line implementation-result/fixture-repair-active wiki/privacy delta
reviewed, including retained new Markdown and prior acknowledgment relocation. Both
operator documents unchanged; scoped audit and both whitespace checks pass. Fixture-
repair result remains pending; no broader acceptance inferred.

## [2026-11-15] verification | initial completion-observation focus closed

Fixture-only rerun passes 44 controls (471.51 s), exit 0; complete three-line retained
report reviewed and all 294 frozen identities match after notification, hash unchanged.
Previously helper-masked missing-prelaunch/precommit refusals now execute without
verifier launch or row/data changes. Initial focus closed, not expanded completion,
affected/full, entity launch/publication/recovery/service or Linux acceptance. Successful
fixtures cleaned; reports remain evidence and historical failed fixtures/freezes retained.
Reconciled feature status and promoted scoped read-only completion facts to the canonical
ETL guide without permission transitions or historical fallback. Next add separate
artifact-rebinding/non-mutation, clock/count/budget and genuine data-corruption controls.
No remote/production operation, scheduling installation, utility implementation, commit
or push; native-Mac shutdown remains separate.

## [2026-11-15] verification | separate completion artifact/data qualification active

Added separate 67-control qualification after initial-green/report/identity review.
Complete 470-line source reviewed; three-target Ruff lint/format passes. All 294 closed
initial-focus identities unchanged; distinct 295-identity freeze binds the active first
run. Targets actual original archive/verifier aliases and duplicate fields, rehashed CLI
statistics/dictionaries versus unchanged original artifacts, both supervision contracts,
shape/count/clock/hash/proof/history budgets, genuine invalid Parquet and a competing
lock process, with unchanged rows/data/authority/live acknowledgment. Contract-only
validation is not original-file/current-data/historical authority. Source/controls fixed
pending notification, complete report and identity review before repair/acceptance.
Historical failures/freezes/fixtures retained; expanded/combined/affected/full and entity
launch/publication/recovery/service, Linux/S3/resources/native-Mac remain separate.
No remote/production work, scheduling installation, utility implementation, commit or push.

Complete 572-line initial-green/expanded-active wiki/privacy successor delta reviewed,
including canonical promotion and retained new Markdown; earlier complete 142-line
fixture-repair acknowledgment also inspected. Both operator documents unchanged; fresh
scoped audit passes nine Markdown/seven frontmatters, 239 grounding paths, 388 inline
sources, 438 links/62 sections and both whitespace checks pass. Expanded result pending.

## [2026-11-15] verification | expanded completion-observation focus closed

Separate expanded run passes 67 controls (353.73 s), exit 0; complete three-line retained
report reviewed and all 295 frozen identities match after notification, hash unchanged.
All artifact/contract/data/lock/budget groups execute without setup masking, retaining
unchanged rows/data/high-water/live acknowledgment. Expanded read-only completion focus
closed, not combined/affected/full or entity launch/publication/recovery/service/Linux
acceptance. Successful fixtures cleaned; historical failed fixtures/reports/freezes and
both operator baselines retained. Reconciled verification/plan/handoff/design/index and
canonical scope. Next freeze a distinct unchanged successor for 447-main/141-standalone
combined focus; keep runtime/controls fixed until both reports and identity checks.
No remote/production operation, scheduling installation, utility implementation, commit
or push; native-Mac shutdown remains separate.

## [2026-11-15] verification | combined read-only completion/exclusion focus active

Created/checked a distinct byte-identical 295-identity combined freeze. Main completion/
input/typed/schema/receipt/original-ledger focus (447 controls) and independent standalone
entity-verifier focus (141 controls) are active with separate retained reports. No runtime/
control changes; fresh three-target Ruff lint/format, scoped wiki audit and both whitespace
checks pass before launch. Keep source/controls fixed until both notifications, complete
reports and frozen-identity checks; combined and affected/full acceptance remain separate.
Expanded read-only evidence grants no entity launch/completion/authority transition or
historical-publication fallback. Both operator baselines and historical failures retained.
Linux/dcc-02–05, isolated S3/resources and native-Mac remain open; no remote/production
operation, scheduling installation, utility implementation, commit or push.

Complete 408-line expanded-green/combined-active wiki/privacy successor delta reviewed,
including retained new Markdown and result/status reconciliation. Both operator documents
unchanged; fresh scoped audit passes nine Markdown/seven frontmatters, 239 grounding
paths/388 inline sources, 438 links/62 sections, and both whitespace checks pass. Both
combined results remain pending; runtime/controls stay fixed and no wider acceptance follows.

## [2026-11-15] verification | combined completion standalone focus green

Standalone notification passes 141 controls (110.49 s), exit 0; complete four-line
report reviewed and all 295 combined-freeze identities match afterward, hash unchanged.
Successful fixtures cleaned; report retained and both operator baselines/historical
failed fixtures preserved. Reconciled feature/index/canonical status. Main combined
focus remains active; keep runtime/controls fixed pending its notification, complete
report and identity check. Combined closure and affected/full, entity launch/publication/
recovery/service, Linux/dcc-02–05, isolated S3/resources and native-Mac remain separate.
No remote/production operation, scheduling installation, utility implementation, commit or push.

Fresh scoped wiki audit and both whitespace checks pass with unchanged scope/counts;
no combined or wider acceptance follows before the main report/identity review.

## [2026-11-15] verification | combined read-only completion/exclusion focus closed

Main notification passes 447 controls (1729.40 s), exit 0; complete nine-line retained
report reviewed and all 295 combined-freeze identities match, hash unchanged. Standalone
passes 141 (110.49 s); both focuses complete. Read-only completion/input/typed/schema/
receipt/original-ledger compatibility focused gate closed, not affected/full or entity
launch/publication/recovery/service/Linux acceptance. Successful fixtures cleaned; reports,
historical failures and both operator baselines preserved. Checked only the combined
focused plan item and reconciled feature/index/canonical status. No test remains active
at review. Next add genuine red controls for durable original-generation publication
retention while independently observed current under the same lock, without ownership/
authority/cursor/launch transition. Preserve current-only completion contracts; later
historical requests require authenticated retained evidence, never caller dictionaries
or today's aggregate. No remote/production work, scheduling installation, utility
implementation, commit or push; native-Mac shutdown remains separate.

Complete 342-line combined-main-green wiki/privacy successor delta inspected against
the last reviewed standalone-green snapshot; retained new Markdown and result/status
reconciliation included. Both operator documents unchanged; fresh three-target Ruff
lint/format, scoped wiki audit with unchanged counts, both whitespace checks and all
295 closed-focus identities pass. No affected/full, entity service or wider acceptance.

## [2026-11-15] verification | separate publication-retention red controls prepared

Added a separate 46-control module before runtime implementation; complete 771-line source
reviewed, patch-only formatting/projection fixes and fresh new-target Ruff lint/format pass.
Isolated collection passes 46 (0.63 s), not execution or acceptance. Distinct 296-identity
first-red freeze adds only the new module; every closed 295-focus identity and both operator
baselines remain unchanged. Controls specify fresh original-generation retention under the
same acknowledged typed lock, exact immutable core/observation/audit, no permission/cursor/
authority transitions, restart without reconstruction, actual COMMIT/process death/lost-ack,
artifact/data/clock/corruption/budget refusal and authenticated historical requests. Publication
and entity-writer runtime modules remain absent; existing history remains fail-closed. First
execution/report review is next; freeze runtime/controls until complete report/identity review
before source work. Wider/affected/full, entity launch/completion/recovery/service, Linux/S3/
resources and native-Mac remain separate. Historical failures/unrelated artifacts preserved;
no remote/production operation, installed scheduling, utility implementation, commit or push.

## [2026-11-15] verification | publication-retention first red active

Complete 488-line prepared wiki/privacy successor delta inspected, including retained
new Markdown; snapshot identity and current bytes match, both operator baselines unchanged.
Fresh new-target Ruff lint/format, scoped audit (nine Markdown/seven frontmatters, 243
grounding paths/391 inline sources, 439 links/63 sections), both whitespace checks and
all 296 first-red identities pass. Launched the distinct retained 46-control first red;
runtime/controls remain fixed until notification, complete report and identity review
before implementation or repair. Missing-module/setup failures establish no semantic
refusal or crash boundary. Historical failures/unrelated artifacts preserved; wider
acceptance, affected/full, entity writer/service/recovery, S3/resources and native-Mac
remain separate. No remote/production work, scheduling installation, utility implementation,
commit or push.

Complete 159-line prepared-to-active wiki/privacy successor delta inspected, including
status reconciliation and retained new Markdown. Both operator documents unchanged;
fresh scoped audit and both whitespace checks pass with unchanged scope/counts. First-red
result remains pending; runtime/controls stay fixed and no wider acceptance follows.

## [2026-11-15] verification | publication-retention first red reviewed

First red retains 46 failures (402.36 s), exit 1; complete 1,772-line report inspected,
SHA-256 `b9e200009bd50754fd980218502b349bc8c007277199d07ce6687b4082d6bc9b`.
All 296 frozen identities match after notification, manifest unchanged. Both retained child
diagnostics directly inspected: genuine setup prints its run identity, then each exits 1 at
missing-module import, not 87. No publication COMMIT boundary or target semantics execute;
the import-masked report establishes no refusal or green. Failed fixtures/report preserved;
both operator baselines unchanged. Reconciled verification/plan/handoff/design/index; no test
remains active and no runtime/control changed. Next implement bounded immutable original-
publication evidence/audit and same-transaction history authentication, preserving current-
only completion contracts, actual-original rechecks, early budgets and no-transition
boundaries. Broader publication/affected/full, entity writer/service/recovery, Linux/S3/
resources and native-Mac remain separate. No remote/production work, scheduling installation,
utility implementation, commit or push.

## [2026-11-15] code | bounded original-publication implementation pending verification

Complete 325-line first-red-reviewed wiki/privacy successor delta inspected; scoped audit
and both whitespace checks pass. Added separate original-publication retention/accessor
after complete report/children/identity review. Fresh current-only completion and actual-
original rechecks precede immutable envelope/core/observation/audit COMMIT; same-connection
bounded typed history/accessor authenticates retained JSON only, never runtime/current-
aggregate reconstruction. Early record/count/shared-history/audit budgets refuse without
pruning. Success changes no ownership/authority/raw-cursor/grants/launch/live acknowledgment;
committed lost acknowledgment retains evidence and blocks the original typed owner, not
completion/recovery. Complete 285-line source and typed-history delta reviewed; four-target
Ruff lint/format and PyUtil whitespace pass. Only typed history and two ledger comments
differ among prior identities; all other 294 first-red identities and every control,
current-only adapter, standalone runtime and both operator baselines unchanged. Distinct
297-identity implementation freeze binds the unchanged 46-control rerun, result pending.
Keep runtime/controls fixed until notification, complete report/children/identity review
before repair or acceptance. Wider publication/combined/affected/full, entity writer/service/
recovery, Linux/S3/resources/native-Mac remain separate. Historical failures/unrelated artifacts
preserved; no remote/production operation, scheduling installation, utility implementation,
commit or push.

## [2026-11-15] verification | publication implementation rerun active

Complete 514-line implementation-pending wiki/privacy successor delta inspected, including
retained new Markdown. Both operator documents unchanged; scoped audit passes nine Markdown/
seven frontmatters, 247 grounding paths/397 inline sources, 439 links/63 sections and both
whitespace checks pass. All 297 implementation identities checked before launch; the distinct
retained unchanged 46-control rerun is active, result pending. Runtime/controls stay fixed
through notification, complete report/children/identity review; no wider acceptance follows.

Complete 157-line pending-to-active wiki/privacy successor delta inspected. Both operator
documents unchanged; fresh scoped audit and both whitespace checks pass with unchanged
counts. Historical first-red idle wording clarified without changing runtime/controls;
implementation result remains pending.

## [2026-11-15] verification | initial original-publication focus closed

Unchanged implementation rerun passes 46 controls (629.02 s), exit 0; complete three-line
report inspected, SHA-256 `90e490a24bf6691114fcd2f66d4f071ce137f979dd516256c97749218e89e0bf`.
All 297 frozen identities match after notification, manifest unchanged. Original artifact/
fresh-data/clock/budget/immutable-core/restart/actual-COMMIT/lost-ack/staged-history/historical
groups now execute without import masking. Successful fixtures cleaned by unchanged runner;
no separately retained green child diagnostics claimed. Historical red fixtures/diagnostics/
report and both operator baselines preserved. Checked only initial publication focus;
reconciled verification/plan/handoff/design/index and promoted scoped immutable-original
semantics to canonical ETL guide. No test remains active at review. Next add separate
rehashed envelope/audit/SQL-byte/keyset-tail qualification and retain new actual crash-child
diagnostics under unchanged runtime/controls. Expanded/combined/affected/full, entity writer/
service/recovery, Linux/S3/resources and native-Mac remain separate. No remote/production
work, scheduling installation, utility implementation, commit or push.

## [2026-11-15] verification | initial publication wiki/privacy review closed

Complete 454-line active-to-initial-green successor delta inspected, including acknowledgment
edits and canonical immutable-original promotion. Fresh four-target Ruff lint/format,
scoped wiki audit (nine Markdown/seven frontmatters, 248 grounding paths/399 inline sources,
439 links/63 sections), both whitespace checks, both operator baselines and all 297 closed
identities pass. Earlier first-red/input statements explicitly scoped to their historical
reviews. No expanded/combined/affected/full, entity permission or wider Linux acceptance;
separate qualification and diagnostic-retaining execution are next. Historical failures,
unrelated artifacts and runtime/controls remain preserved; no remote/production operation,
installed scheduling, utility implementation, commit or push.

## [2026-11-15] verification | expanded publication controls and retained diagnostics prepared

Added separate 651-line/77-control publication qualification and 69-line diagnostic-retaining
runner; complete sources reviewed and six-target Ruff lint/format pass. Targets rehashed
scope/type/core/observation/audit/canonical JSON, actual SQL UTF-8 record/audit byte caps,
positive aggregate/count/equality boundaries before typed identifiers/payloads, same-connection
materialized keyset tails and persisted-corruption reopen. One genuine observed publication/
audited block anchors staged rollback-only corruption; no accepted completed history or
historical evidence is fabricated. Runner refuses report overwrite and is designed to retain
successful crash diagnostics as well as failed fixtures. New controls plus the two unchanged
original process-death controls collect 79 (0.69 s); complete 82-line report inspected, not
execution. All 297 closed identities and both operator baselines unchanged. Distinct 298-identity
successor adds only the new module; runner separately frozen. First execution follows complete
wiki/privacy review/fresh checks; no test is active yet. Preserve runtime/controls/runner through
notification, complete report/actual diagnostics and identity review before repair/acceptance.
Distinct combined 570-main/141-standalone focus follows expanded closure before entity-writer
work; affected/full, Linux/S3/resources and native-Mac remain separate. Historical failures/
unrelated artifacts preserved; no remote/production operation, scheduling installation,
utility implementation, commit or push.

Complete 546-line initial-green-to-qualification-prepared wiki/privacy successor delta
inspected, including acknowledgment edits, retained new Markdown and source/test/result scope.
The new preparation entry is placed at the log tail, preserving prior history in order;
no successful child diagnostics are claimed before execution. Fresh scoped audit passes
nine Markdown/seven frontmatters, 252 grounding paths/402 inline sources, 439 links/63 sections;
both whitespace checks and all 298 successor identities pass, operator documents unchanged.

## [2026-11-15] verification | expanded publication qualification active

Complete 133-line prepared-to-ready wiki/privacy successor delta inspected; operator baselines
and separately frozen runner match. Fresh scoped wiki audit and both whitespace checks pass
with unchanged counts; all 298 successor identities checked and exact successor comparison
confirms only the new qualification module was added. Launched the separate 79-control run
(77 new plus two unchanged actual-COMMIT process-death controls); all fixtures/actual child
diagnostics will be retained on either outcome. Result pending; keep runtime/controls/runner
fixed through notification, complete report/diagnostics and identity review before repair or
expanded acceptance. Combined/affected/full, entity writer/service/recovery, Linux/S3/resources
and native-Mac remain separate. No remote/production work, installed scheduling, utility
implementation, commit or push.

Complete 231-line ready-to-active wiki/privacy successor delta inspected; operator baselines
remain unchanged, fresh scoped audit and both whitespace checks pass with unchanged counts.
Expanded result pending; no runtime/control/runner changes or wider acceptance.

## [2026-11-15] verification | expanded original-publication focus closed

Separate qualification passes 79 controls (100.90 s), exit 0; complete four-line report,
29-line runner sidecar, both actual 93-byte child diagnostics and all 298 source identities/
separate runner/operator baselines reviewed after notification. Both children exit 87 with
empty stderr at the selected before/after publication COMMIT hooks, not import/setup failure.
Required restart/exclusion/unchanged-cursor/absent-before/retained-after publication and
second-reopen assertions execute. Rehashed contracts/canonical JSON/audits, actual UTF-8 SQL
record/audit caps, positive aggregate/count/equality limits, real materialized keyset-tail and
non-mutating corrupted-reopen controls pass. Every fixture and historical failure retained;
no deleted initial-green diagnostics reconstructed or unsupported load attribution made.
No runtime/control/runner repair; expanded focus closed, not permission or wider Linux.
Reconciled verification/plan/handoff/design/index and promoted scoped qualification limits
to canonical ETL guide. No test remains active at this result review. Review complete successor
wiki/privacy delta and fresh scoped checks, then distinct 570-main/141-standalone focus before
entity-writer work. Affected/full, recovery/service, S3/resources and native-Mac stay separate;
no remote/production operation, scheduling installation, utility implementation, commit or push.

Complete 429-line active-to-expanded-green successor wiki/privacy delta inspected, including
all result/diagnostic/identity acknowledgment edits and canonical qualification limits.
Fresh six-target Ruff lint/format, scoped audit (nine Markdown/seven frontmatters, 253 grounding
paths/403 inline sources, 439 links/63 sections), both whitespace checks, all 298 closed source
identities and both operator baselines pass. Scoped expanded record closed, not wider acceptance.

## [2026-11-15] verification | combined publication focus prepared

After expanded closure and complete wiki/privacy/fresh-check review, created distinct unchanged
298-identity combined source freeze and separate diagnostic-retaining runner freeze. Prepared
570-main focus is prior 447 plus original 46/separate 77 publication controls, without duplicate
crash executions; unchanged standalone three-module focus has 141. Both use distinct reports,
retain every fixture/actual diagnostic and preserve historical failures. No run is active yet;
complete prepared wiki/privacy review/fresh checks precede both independent launches. Keep
runtime/controls/runner fixed until both notifications, complete reports/actual diagnostics
and all-identity checks. Entity-writer source work waits for combined closure; affected/full,
Linux/service/recovery, S3/resources and native-Mac stay separate. No remote/production operation,
installed scheduling, utility implementation, commit or push.

## [2026-11-15] verification | combined publication focus active

Complete 312-line green-to-combined-prepared wiki/privacy successor delta inspected; fresh
scoped audit/whitespace checks pass with unchanged counts, all 298 combined identities
checked and both operator baselines/separate runner unchanged. Launched independent 570-main
and 141-standalone focuses with distinct overwrite-refusing reports/all fixtures retained.
Results pending; runtime/controls/runner stay fixed until both notifications, complete
reports/actual diagnostics and all-identity review. Expanded publication remains closed,
not combined acceptance or entity launch/recovery/service permission. Affected/full,
Linux/S3/resources and native-Mac stay separate; no remote/production operation, installed
scheduling, utility implementation, commit or push.

Complete 283-line prepared-to-active wiki/privacy successor delta inspected; both operator
baselines/separate runner unchanged and fresh scoped audit/whitespace checks pass with
unchanged counts. Combined results pending; no runtime/control/runner changes or wider acceptance.

## [2026-11-15] verification | combined publication standalone focus passed, main pending

Standalone focus passes 141 controls (109.28 s), exit 0; complete four-line report and 21-line
runner sidecar inspected. All 298 combined source identities, separate runner and both operator
baselines match after notification, manifest unchanged. All standalone fixtures retained;
no publication crash-child diagnostics expected or found for this focus. Complete 80-line
active-acknowledgment wiki/privacy delta previously inspected; current snapshot matches at
result arrival. Reconciled scoped standalone evidence without runtime/control/runner changes.
Main 570-control focus remains active/result pending; keep all identities fixed through its
notification, complete report/actual diagnostics and all-identity review. No polling/source
work or combined acceptance; affected/full, entity launch/recovery/service, Linux/S3/resources
and native-Mac remain separate. No remote/production operation, scheduling installation,
utility implementation, commit or push.

Complete 296-line active-to-standalone-green wiki/privacy successor delta inspected;
both operator baselines unchanged and fresh scoped audit/whitespace checks pass with
unchanged counts. Main pending; no source/control/runner changes or combined acceptance.

## [2026-11-15] verification | combined publication compatibility focus closed

Main focus passes 570 controls (2430.83 s), exit 0; complete ten-line report/45-line runner
sidecar and both actual 93-byte publication-child diagnostics inspected. Each exits 87 with
empty stderr at its selected before/after COMMIT hook; original exclusion/raw cursor and
absent-before/retained-after publication/second-reopen assertions execute. No physical-power-
loss or load attribution follows from this process-death evidence/duration. All 298 frozen
source identities, separate runner, operator baselines and reviewed standalone report remain
unchanged after notification. Standalone previously passed 141 (109.28 s). Both focuses
complete/all fixtures and historical failures retained; no test active or runtime/control/
runner changes at result review. Complete 80-line standalone acknowledgment delta inspected;
current wiki matches at main-result arrival. Reconciled verification/plan/handoff/design/
index and canonical ETL limits; combined focused gate closed, not affected/full or permission.
Complete successor wiki/privacy/fresh checks precede separate explicit-v5 entity-writer red
controls and source work. Launch/atomic completion-authority linkage, dispatch and original-
clean recovery remain separate/unimplemented; Linux/S3/resources/native-Mac remain open.
No remote/production operation, scheduling installation, utility implementation, commit or push.

## [2026-11-15] verification | combined-green review acknowledged; writer preparation

Complete 383-line combined-green wiki/privacy successor review and fresh six-target Ruff
lint/format, scoped audit and both whitespace checks passed. Complete snapshot, all 298
source identities, separate runner and operator baselines rechecked unchanged before writer
preparation. Original 416-line writer controls retained separately. Next add only local
explicit-v5 fixtures and actual child-diagnostic retention, preserving assertions/shared
helpers, then freeze and review a distinct writer red before runtime source changes.
Combined focused closure is not entity permission/affected/full or wider Linux acceptance.

## [2026-11-15] verification | explicit-v5 writer red prepared

Preserved original 416-line writer controls. Local v5 upgrade wrapper and actual crash/lock
diagnostics are the sole deliberate source-freeze delta; all assertions/parameterizations
and shared default-v4 helpers remain unchanged. Full delta and separate 74-line diagnostic-
retaining runner reviewed; two-target Ruff lint/format and collection of 22 controls pass.
Distinct 298-identity writer-red freeze retains the other 297 closed identities; publication
runner/operators and historical fixtures/failures unchanged. First execution prepared, not
active; complete wiki/privacy/fresh scoped checks precede launch and full red/child/identity
review precedes runtime source work. Successful typed history/completion must not overwrite
original publication or relax intent authority/cursor binding. Wider Linux/affected/full,
S3/resources and native-Mac remain separate; no remote/production/scheduling/commit/push.

## [2026-11-15] verification | explicit-v5 writer red active

Complete 252-line prepared wiki/privacy successor delta inspected; fresh scoped audit,
both whitespace checks and all 298 writer-red identities pass. Launched distinct retained
22-control writer red; result pending, runtime/controls/runner frozen until notification,
complete report/actual child diagnostics and identity review. Missing imports or setup
failures establish no launch/COMMIT/lock/refusal boundaries or entity permission. Historical
fixtures/failures preserved; affected/full, wider Linux, S3/resources and native-Mac separate.

## [2026-11-15] verification | explicit-v5 writer first red reviewed

Writer red completes with 22 import-masked failures (45.76 s), exit 1. Complete 1,010-line
report, 36-line runner sidecar and all four actual 195-byte child diagnostics directly reviewed.
Children exit 1 at the missing writer import before hooks; no competing-lock child ran.
No semantic refusal, launch, COMMIT, lock or recovery boundary is qualified. All 298 frozen
source identities, separate runner and both operator baselines match after notification;
every fixture and historical failure retained. No test active or runtime writer implemented.
Reconciled verification/plan/handoff/design/index; complete active/result wiki/privacy review
and fresh scoped/source/runner/operator/whitespace checks precede runtime coding. Immutable
original publication, original intent authority/cursor binding and unresolved audit-count
refusals must survive a distinct successful completion/history design. Linux/affected/full,
S3/resources and native-Mac stay separate; no remote/production/scheduling/commit/push.

Complete 324-line prepared-to-active/result wiki/privacy successor inspected; fresh scoped
audit, both whitespace checks, two-target Ruff lint/format and all 298 source identities,
both runners/operator baselines/red-evidence identities pass. Red evidence reconciliation
closed only; successful history/completion design and genuine separate controls remain next.

## [2026-11-15] design | distinct typed completion/history red prepared

Selected bounded separately linked typed-event completion records/authority references,
without changing v5 tables/columns or public one-hour validation. Original publications and
original authority/cursor predecessors remain authenticated. Unresolved audit-count allowance
unchanged; retained completion records may supply only their distinct capacity. Separate
257-line/20-control genuine history/recovery module reviewed; lint/format/collection pass.
299-identity successor adds only this module, preserving all 298 writer-red sources/runner/
operators and historical fixtures. Complete wiki/privacy/fresh checks precede first red;
complete report/identity review precedes runtime coding. No writer semantics or wider gate
accepted; no remote/production/scheduling/commit/push.

## [2026-11-15] verification | separate typed history red reviewed

Complete 282-line selected-design/red-prepared wiki/privacy successor and fresh scoped/
whitespace checks pass. Separate history red completes with four failures/16 setup errors
(3.52 s), exit 1, all missing-writer/import-masked. Complete report/19-line sidecar and all
299 unchanged source identities reviewed; every fixture retained, no child diagnostics
produced and no test active. Neither success/corruption/budget nor recovery semantics execute.
Preserve both reds/controls; runtime implementation follows scoped result review, not wider
acceptance. Original publications/public validation/unresolved budgets remain unchanged.

## [2026-11-15] implementation | Linux entity writer source review, unqualified

Acknowledged complete 184-line history-red result successor. Reviewed the five-file runtime
successor, retained its initial unformatted bytes and applied scoped formatting; eight-target
Ruff lint/format pass. Repaired duplicate-completed-receipt refusal and authority SQL-size/
count/keyset-tail validation without changing frozen 22+20 controls, runner, operator documents,
public validators, v5 schema or standalone runtime. Typed completion/authority/history and
supervised original-clean recovery remain unexecuted/unqualified. Retained-completion
acknowledgment resolution explicitly refuses pending separate immutable audited evidence.
Reconciled verification/plan/handoff/design/index; complete successor wiki/privacy/fresh
checks and a distinct source freeze precede the first runtime run. Full evidence/identity
review precedes repairs. No broader Linux/S3/resources/native-Mac acceptance or remote/
production/scheduling/commit/push action.

## [2026-11-15] verification | frozen Linux writer first runtime run active

Distinct 301-identity successor retains both controls/runner/operators and all 296 unchanged
history-red sources; only the reviewed five-file runtime successor differs. Complete 300-line
runtime-prepared wiki/privacy delta inspected; scoped audit and both whitespace checks pass.
Launched unchanged 42 writer/history controls with overwrite-refusing report and all fixtures/
actual diagnostics retained. No result or green yet; keep runtime/controls/runner fixed until
notification and full report/sidecar/child/identity review. Missing retained-completion
acknowledgment resolution and wider Linux/affected/full/S3/resources/native-Mac remain open.

## [2026-11-15] verification | Linux writer first runtime result reviewed

First runtime run completes with 40 passes/two failures (244.11 s), exit 1. Full 245-line
report, 49-line sidecar and seven actual diagnostics reviewed: four intent/launch crash children
exit 87, three lock competitors exit 88, all with empty stderr. All 301 frozen sources,
runner and operator baselines match after notification; every fixture/historical failure retained.
One failure reaches missing immutable committed-completion acknowledgment resolution; the other
refuses January recovery after a real November restart block. Read-only retained state confirms
original publication/completion as applicable remain blocked, with no raw-history/cursor advance.
Preserve both failures; correct only the scoped fixture clock, add early rollback and immutable
resolution controls, then repair through deliberate successors after full wiki/privacy/fresh
review. No run active/full writer-history green or broader Linux acceptance; no remote/
production/scheduling/commit/push.

## [2026-11-15] verification | immutable resolution-control successor prepared

Acknowledged the completely inspected 287-line runtime-result wiki/privacy review and fresh
scoped/whitespace checks. Preserved original history-control bytes; function-scoped synthetic
reopen clock and import formatting leave assertions/parameterizations/shared helpers/all other
functions unchanged by AST checks. Separate complete 407-line/29-control resolution module
reviewed; four-target lint/format and 49-control collection pass. Selected bounded immutable
resolution-event/audit design retains original completion/publication and blocks COMMIT uncertainty.
Distinct 302-identity control-red freeze preserves all other 300 runtime-first identities,
writer/runner/operators and runtime; no repair or result yet. Complete successor wiki/privacy/
fresh checks precede red, and complete report/evidence/all identities precede runtime repair.
Linux/affected/full/service, S3/resources and native-Mac remain open; no remote/production/
scheduling/utility/commit/push action.

## [2026-11-15] verification | resolution-control red reviewed

Separate red completes with 25 passes/nine failures/15 setup errors (343.58 s), exit 1.
Full 1,277-line report/20-line sidecar and all 302 source/runner/operator identities reviewed;
every fixture retained. Actual read-only failed-ledger/capture inspection confirms late
block-clock refusal after successful verification and original-clean recovery's after-COMMIT
DRAINING defect, with original completion/authority/raw cursor preserved. Corrected inspection
uses real supervision fields after an initial diagnostic-only nonexistent-key error. Scoped
fixture clock passes; artifact/budget controls remain masked, not qualified. Preserve the red
unchanged; complete result wiki/privacy/fresh checks precede bounded immutable resolution and
conservative uncertainty repair. No run active, runtime repair, green or wider acceptance;
no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] implementation | immutable resolution source successor reviewed

Acknowledged complete 233-line resolution-red wiki/privacy review/fresh checks. Preserved
original runtime bytes and initial unformatted successor; reviewed complete 343-line two-file
delta and separate 450-line resolution module. Scoped formatting preserves AST except unused
import removal; eight-target lint/format pass. Immutable hash-linked resolution/audit and
uncertainty records preserve original completion/publication/block/authority; early recovery
block-clock checks precede new verifier/artifacts. Distinct 303-identity freeze preserves all
other 300 red-source identities and all controls/runner/operators/public/v5/standalone contracts.
71-control run is prepared, with no result yet; complete wiki/privacy/fresh checks precede
launch and full evidence/identity review precedes further change. Closed publication overflow
and expanded completion-death/SQL-tail/forward-evolution remain separate. No broader Linux/
S3/resources/native-Mac acceptance or remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | immutable resolution runtime qualification active

Complete 470-line prepared wiki/privacy successor inspected; fresh scoped audit and both
whitespace checks pass with all 303 source/runner/operator identities unchanged. Launched
the distinct 71-control writer/history/resolution run using the frozen overwrite-refusing
diagnostic-retaining runner. No result/green yet; keep sources/controls/runner fixed until
notification and complete report/sidecar/actual-child/all-identity review. Every fixture and
historical failure retained. Linux/affected/full/service, S3/resources and native-Mac remain
separate; no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | immutable resolution first runtime reviewed

First run completes with 69 passes/two failures (516.86 s), exit 1. Full 67-line report/50-line
sidecar/seven actual diagnostics and all 303 source/runner/operator identities reviewed;
four crash children exit 87 and three lock competitors exit 88, all with empty stderr.
Original 42 writer/history controls pass; two new positives fail on the test's nonexistent
completion flag after successful disposition, so later immutable original/table/byte/reopen
assertions remain unexecuted. Read-only failed-ledger/capture inspection authenticates the
real direct-module command and canonical completion request/fresh observation, with no mutation.
Preserve failed run/original controls; complete wiki/privacy/fresh checks precede a narrow
exact-command/request control correction, not runtime changes. No run active/full 71-control
green or wider Linux acceptance; no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | resolution command-contract successor prepared

Acknowledged complete 241-line first-runtime result wiki/privacy review and fresh scoped/
whitespace/source/runner/operator checks. Preserved original 407-line resolution-control bytes;
reviewed complete 31-line correction replacing only the nonexistent flag with exact standalone
command, canonical completion request and actual manifest assertions. Text/AST restoration
preserves all other controls; eight-target lint/format and 71-control collection pass. Distinct
303-identity freeze changes only this test module; all 302 other sources/runner/operators and
historical evidence remain unchanged. Prepared all-71 rerun has no result yet; complete wiki/
privacy/fresh checks precede launch, full evidence/identity review precedes further changes.
Closed publication overflow/process-death affected rerun and broader Linux gates stay open.
No remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | resolution command-contract rerun active

Complete 248-line prepared-final wiki/privacy successor reviewed; fresh scoped audit, both
whitespace checks and source/runner/operator identities pass. Launched the distinct frozen
all-71 writer/history/resolution rerun with overwrite-refusing report and diagnostic-retaining
runner. No result yet; keep runtime/controls/runner fixed until notification and complete
retained report/sidecar/actual-child/all-identity review. Every historical failure and fixture
remains intact. Publication affected rerun and broader Linux gates stay open; no remote,
production, scheduling, utility implementation, commit or push action.

## [2026-11-15] verification | initial writer-history-resolution focus closed

Frozen command-contract successor passes all 71 controls (521.59 s), exit 0. Full three-line
report/50-line sidecar/seven actual diagnostics and all 303 source/runner/operator identities
reviewed unchanged; four intent/launch crash children exit 87 and three lock competitors exit
88, all with empty stderr. Corrected positive cases now execute and pass later immutable
original/table/data/artifact/retry-refusal/reopen assertions. Initial focused gate closed,
not expanded completion-death/SQL-tail/forward-evolution, affected/full/service or broader
Linux acceptance. All fixtures/original controls/historical failures retained; no test active
or source/control/runner change indicated. Complete wiki/privacy/fresh checks precede separate
unchanged 123-control publication affected rerun. S3/resources/native-Mac stay separate;
no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | post-resolution publication affected rerun prepared

Acknowledged complete 266-line all-71 green/57-line index historical-current wiki/privacy
reviews and fresh scoped/whitespace checks. Renewed six-target lint/format pass; both unchanged
publication modules are fully reviewed and 123 controls collected, including exact unresolved
four-audit overflow at all five entries and both actual original publication COMMIT deaths.
Distinct byte-identical 303-identity source freeze and separate unchanged runner freeze bind
the prepared retained rerun; runtime/controls/operators/public contracts/locks unchanged.
No test active/result or broader acceptance. Complete prepared wiki/privacy/fresh checks
precede launch; full report/sidecar/actual-child/all-identity review precedes further change.
Expanded entity/integration/S3/resources/native-Mac gates remain open; no remote/production/
scheduling/utility/commit/push action.

## [2026-11-15] verification | post-resolution publication affected rerun active

Complete 233-line prepared wiki/privacy successor reviewed; fresh scoped audit, both whitespace
checks and all 303 source/runner/operator identities pass. Launched the separately frozen
unchanged 123-control publication affected rerun with distinct overwrite-refusing report and
diagnostic-retaining runner. No result yet; keep runtime/controls/runner fixed until notification
and complete retained report/sidecar/actual-child/all-identity review. Every historical failure
and fixture remains intact. Initial all-71 focus is closed; expanded entity/integration/S3/
resources/native-Mac gates stay open. No remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | post-resolution publication affected follow-through closed

Unchanged frozen publication rerun passes all 123 controls (708.64 s), exit 0. Complete four-line
report/29-line sidecar/two actual 93-byte publication COMMIT diagnostics and all 303 source/
runner/operator identities reviewed; both crash children exit 87 with empty stderr. All 46
original/77 expanded controls, including exact unresolved four-audit overflow at all five typed
entries, pass. Every fixture/historical report/original control retained; no run active or source
change. Only this affected follow-through closes, not entity-wide affected/full or wider Linux.
Complete result wiki/privacy/fresh checks precede separate completion-death/stronger SQL-tail/
forward-evolution controls. Maintenance/service/S3/resources/native-Mac and dcc-02–05 remain
open; no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | genuine entity completion-death controls prepared

Acknowledged complete 254-line publication-result wiki/privacy review/fresh checks. Added only
a separate fully reviewed 345-line/12-control module for actual no-unwind process death after
genuine independent verification and at before/after completion/resolution COMMIT hooks. Init/
replay, original-clean recovery and immutable acknowledgment resolution bind actual hashed
captures, precise commands/shutdown/CLI originals and all-or-none typed state without raw/
reader release. Formatting is AST-identical; child parsing/six-target lint/format/collection
pass. Distinct 304-identity source freeze adds only this module; all 303 prior sources/runner/
operators unchanged. First run is prepared, not active/qualified; full wiki/privacy/fresh checks
precede launch and full report/sidecar/actual-child/capture/all-identity review precedes further
changes. Stronger SQL-tail/forward-evolution, maintenance/service/integration and wider Linux/
S3/resources/native-Mac remain open; no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | genuine entity completion-death qualification active

Complete 316-line prepared wiki/privacy successor reviewed; fresh scoped audit, both whitespace
checks and all 304 source/runner/operator identities pass. Launched the distinct frozen 12-control
completion-process-death run with unchanged overwrite-refusing diagnostic-retaining runner.
No result yet; runtime/controls/runner stay fixed until notification and complete retained
report/sidecar/actual-child/boundary-capture/all-identity review. Every historical report/fixture/
control remains intact. SQL-tail/forward-evolution/maintenance/service/integration and wider
Linux/S3/resources/native-Mac gates stay open; no remote/production/scheduling/utility/commit/push.

## [2026-11-15] verification | genuine entity completion-death focused gate closed

Frozen run passes all 12 controls (283.57 s), exit 0. Complete three-line report/68-line sidecar/
12 actual 181-byte exit-89 diagnostics and hash-bound boundary captures authenticated; stderr
empty. Independent read-only inspection validates 48 actual observation-artifact groups and
72 immutable CLI archive records; all 545 retained fixture files and 304 source/runner/operator
identities unchanged. Initial diagnostic-only guessed cursor literal corrected to the actual
original intent; complete corrected inspection passes without runtime/control/fixture changes.
Eight uncommitted cases need fresh audited recovery; four genuine COMMITs retain atomic results.
Raw cursor/history, queued-reader/grant and live authority boundaries hold. Every report/fixture/
original control/freeze retained; no test active. Only this focus closes, not SQL-budget/keyset/
forward-evolution, maintenance/service/staged integration or wider Linux acceptance. Complete
result wiki/privacy/fresh checks precede separately reviewed/frozen controls. S3/resources/
native-Mac and dcc-02–05 remain open; no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | completion-resolution SQL-history controls prepared

Acknowledged complete 307-line crash-result wiki/privacy review/fresh checks. Exact initial
531-line formatting matches and AST preserves retained 329-line source. Full review detects
only new-module fixture/guard defects before execution; complete 98-line correction preserves
all test assertions/parameterizations/other helpers and drafts. Final 548-line/44-control
module is reviewed; eight-target lint/format and final collection pass. Two genuine completion/
resolution/publication originals are planned for early SQL-budget-before-fetch, exact caps,
one-row sequence tails and full-history/audit tails; no results/observations are manufactured.
Typed independent cursors remain rejected, unrelated reader validation/actual writer receipt
prerequisite preserved, and guard failure cannot prevent rollback. Distinct 305-identity freeze
adds only this module; all 304 predecessor sources and runner/operators unchanged. No run active,
result, runtime repair or broader acceptance. Complete prepared wiki/privacy/fresh checks precede
launch and full retained evidence/identities precede further changes. Every historical failure/
fixture preserved; Linux/S3/resources/native-Mac remain open, no remote/production/scheduling/
utility/commit/push action.

## [2026-11-15] verification | completion-resolution SQL-history qualification active

Complete 480-line prepared wiki/privacy successor reviewed; fresh scoped audit, both whitespace
checks and all 305 source/runner/operator identities pass. Launched the distinct frozen 44-control
history run with the unchanged overwrite-refusing diagnostic-retaining runner. No result yet;
runtime/controls/runner remain fixed until notification and full retained report/sidecar/actual
fixture/artifact/identity review. Every historical report/fixture remains intact. Forward-evolution/
maintenance/service/integration and wider Linux/S3/resources/native-Mac remain open; no remote/
production/scheduling/utility/commit/push action.

## [2026-11-15] verification | completion-resolution SQL-history focused gate closed

Frozen history run passes all 44 controls (62.53 s), exit 0. Complete three-line report/
19-line sidecar reviewed; no diagnostic children are expected for these ordinary genuine
CLI/verifier captures. Independent read-only review authenticates ten verifier groups, two
CLI completions, twelve immutable archives and original publication/completion/resolution/
blocker/authority/raw-cursor links. Original guessed-table failure and table-corrected guessed-
count failure remain retained; complete inspection against actual schema/14 typed events passes.
No runtime/test/fixture change. All 84 retained files (83 fixtures plus sidecar)/one symlink
and all 305 source/runner/operator identities unchanged. No test active; only SQL-budget/keyset/
tail focus closes. Complete result wiki/privacy/fresh checks precede separate forward-evolution
controls. Maintenance/service/staged integration and wider Linux/S3/resources/native-Mac/
dcc-02–05 remain open; no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | raw-cursor-authority forward-history controls prepared

Complete closed-history result wiki/privacy/fresh checks precede the separate control-only
successor. Retained 261-line draft receives demonstrated request-clock/anchor-shape corrections
and actual final-CLI semantic comparison; complete 67-line correction/419-line module reviewed.
Formatting preserves corrected AST; lint-only refusal contexts consolidated. Eight-target lint/
format and corrected 23-control collection pass; wrong system-interpreter collection diagnostic
retained, no semantic execution. Three positives/sixteen rollback-only damage/four old-receipt
refusals plan genuine interleaved raw/entity evolution, never fabricated historical evidence.
Distinct 306-identity freeze adds only this module; all 305 predecessors/runner/operators/
closed-history fixtures unchanged. No test active or runtime change. Complete prepared wiki/
privacy/fresh checks precede execution and full genuine retained evidence/identities precede
closure or repair. Maintenance/service/integration and wider Linux/S3/resources/native-Mac/
dcc-02–05 remain open; no remote/production/scheduling/utility/commit/push action.

## [2026-11-15] verification | raw-cursor-authority forward-history qualification active

Complete 340-line prepared wiki/privacy successor reviewed; fresh scoped audit, both whitespace
checks and all 306 source/runner/operator/closed-history fixture identities pass. Launched the
distinct frozen 23-control first run with the unchanged overwrite-refusing retained runner.
No result yet; runtime/controls/runner remain fixed until notification and complete genuine
artifact/ledger/fixture/identity review. Every historical failure retained. Maintenance/service/
integration and wider Linux/S3/resources/native-Mac/dcc-02–05 remain open; no remote/production/
scheduling/utility/commit/push action.

## [2026-11-15] verification | raw-cursor-authority forward-history focused gate closed

Frozen run passes all 23 controls (87.45 s), exit 0. Complete three-line report/19-line sidecar
and independent read-only inspection authenticate 16 verifier groups/four CLI completions/34
immutable archives, original publication/completion/resolution/blocker/raw-cursor/authority links
and generations 1,1,2,3,3,4. Original guessed-DRAINING inspection failure/source retained; separate
read-only diagnostic establishes OPEN at the advanced fixed-hour cursor, as final raw proof
requires. One reader stays WAITING without grants/live authority. Complete diagnostic-only
21-line correction and 12-line final inspection reviewed; no runtime/control/fixture change.
All 150 retained files/one symlink and 306 source/runner/operator/predecessor-fixture identities
unchanged. No test active; only this focused gate closes. Complete result wiki/privacy/fresh
checks precede separate original-bound recovery/maintenance and strict Linux entity dispatch.
Staged both-runtime integration, wider Linux/S3/resources/native-Mac and dcc-02–05 remain open;
no remote/production/scheduling/utility/automatic-expiry/commit/push action.

## [2026-11-15] design | strict Linux entity service controls prepared

Selected existing-library init/replay/clean-original and immutable-ack resolution dispatch,
with separate bounded entity configuration and explicit v5 upgrade selection. Raw tick/v4
defaults and original receipt/storage scope remain unchanged; unrelated flags/confirmation/
platform/scope checks precede configuration. Complete 447-line/71-control module and genuine
child reviewed; lint/collection pass. Separate 307-identity red freeze adds only controls,
preserving all 306 closed-forward sources and unchanged retained runner. Scoped wiki/privacy
and whitespace checks pass; no runtime change or semantic result at preparation. Complete
retained red/evidence/identities precede coding. Pending-publication repair, missing original
migration/deletion coverage, staged both-runtime integration and wider Linux/S3/resources/
native-Mac remain separate; no remote/production/scheduling/utility/expiry/commit/push action.

## [2026-11-15] verification | first frozen Linux entity service red awaiting completion

The distinct 71-control first red was launched with the unchanged retained runner; no
completion notification/result has yet been received or inspected. Runtime/controls/runner
remain fixed pending full report/sidecar/actual diagnostic and identity review. Resumed
read-only checks confirm all 307 identities; complete corrected 297-line preparation delta
reviewed for scope/privacy, preserving the separate omitted-untracked-page diagnostic.
Fresh scoped nine-page wiki audit and both whitespace checks pass. Handoff now distinguishes
the closed forward focus from the pending service red. No runtime repair or broader
acceptance; pending-publication recovery, staged integration, S3/resources/native-Mac and
dcc-02–05 remain separate. No remote/production/scheduling/utility/expiry/commit/push action.

## [2026-11-15] verification | first Linux entity service red reviewed

Frozen first red completes with 71 failures (135.78 s), exit 1. Full lossless 3,052-line
report/607-line review, 28-line sidecar, two actual 719-byte diagnostics and all 307 source/
runner identities authenticate. One unsupported config/64 parser-masked/four absent-loader/
two parser-stopped-child failures demonstrate missing seams, not successful semantic refusals
or service COMMIT boundaries. Read-only snapshot preserves 302 files/eight symlinks and actual
receipt damage without reconstruction. No run active/runtime repair yet. Next narrowly
implement strict dispatch/separate configuration/explicit-v5/original-loader, preserving all
controls/prior evidence; distinct successor review/freeze/rerun required. Pending-publication,
integration/Linux/S3/resources/native-Mac/dcc-02–05 stay open; no remote/production/scheduling/
utility/expiry/commit/push action.

## [2026-11-15] implementation | strict Linux entity service runtime successor prepared

Complete 306-line red-result wiki/privacy review and fresh checks precede the two-file
source successor. Original runtime retained; complete formatted 303-line delta reviewed.
Only service configuration/early flag dispatch/explicit-v5 selection and exact blocked typed
original loader change. Existing library/schema/standalone/public/raw-reader contracts remain
fixed. Distinct 307-identity freeze preserves all 305 other identities, all controls/runtime
locks/runner and 310 retained red-evidence entries. Three-target lint/format and unchanged
71-control collection pass. Runtime rerun prepared, no result yet; full prepared wiki/privacy/
fresh checks precede launch and actual retained evidence/identity review precedes closure or
repair. Pending-publication/integration/Linux/S3/resources/native-Mac/dcc-02–05 stay open;
no remote/production/scheduling/utility/expiry/commit/push action.

## [2026-11-15] verification | strict Linux entity service runtime qualification active

Complete 319-line prepared wiki/privacy successor reviewed; fresh scoped audit, both
whitespace checks and all 307 runtime/runner identities pass. Accepted forward-history
150-file/one-symlink evidence rechecks unchanged without rerun. Launched the distinct
unchanged 71-control runtime qualification with the overwrite-refusing retained runner.
No result yet; runtime/controls/runner stay fixed until completion and full retained report/
sidecar/actual diagnostic/artifact/identity review. Every red/prior fixture remains intact.
Service/maintenance/integration/Linux/S3/resources/native-Mac/dcc-02–05 remain open;
no remote/production/scheduling/utility/expiry/commit/push action.

## [2026-11-15] verification | strict Linux entity service focused gate closed

Unchanged frozen run passes all 71 (251.19 s), exit 0. Full three-line report/28-line sidecar/
two actual exit-91 diagnostics and independent read-only inspection authenticate 23 ledgers,
32 verifier groups/ten clean CLI captures/60 immutable archives, nine atomic typed completions
and one immutable acknowledgment resolution. Before-COMMIT death stays blocked without
completion/authority; after-COMMIT retains both without raw advancement. Actual receipts bind
the diagnostics' null identities; real restart block clock and damaged originals remain intact.
Prepared-only retry receipt has no intent/verifier/launch/archive. Both inspector directory/
configuration-assumption failures and sources retained; reviewed diagnostic-only corrections
pass without runtime/control/fixture changes. All 439 green files/eight symlinks, 310 red entries,
accepted forward 150 files/one symlink and 307 runtime/control/lock/runner identities unchanged.
No test active; only strict-service focus closes after complete result wiki/privacy/fresh checks.
Pending-publication/original-bound maintenance, staged service-affected/both-runtime integration
and wider Linux/S3/resources/native-Mac/dcc-02–05 stay open; no remote/production/scheduling/
utility/automatic-expiry/commit/push action.

## [2026-11-15] verification | unchanged Linux service-affected scope prepared

Acknowledged complete 396-line strict-service result wiki/privacy review; fresh scoped audit,
both whitespace checks, all 307 source/lock identities, original runner and green/red/accepted-
forward evidence pass. Distinct byte-identical freeze and hash-bound scope select 13 existing
service/client/lifecycle/local-route/raw-recovery/maintenance/retry/entity-service modules.
All 307 controls collect (1.48 s); complete collection/32-line sidecar authenticate. No runtime/
control changes or semantic launch/result. Accepted forward module/fixture excluded, ten-second
lifecycle wait unchanged. Prepared review/fresh checks precede distinct retained run; actual
report/diagnostic/artifact/ledger/identity review precedes closure or repair. Pending-publication,
broader both-runtime integration and Linux/S3/resources/native-Mac/dcc-02–05 remain open; no
remote/production/scheduling/utility/expiry/commit/push action.

## [2026-11-15] verification | unchanged Linux service-affected qualification active

Complete 318-line prepared wiki/privacy review and fresh scoped/whitespace/source/runner/
collection/prior-evidence checks precede the distinct 307-control launch. The unchanged
diagnostic-retaining runner uses new fixtures/report and exact frozen 13-module scope.
No completion/result yet; runtime/controls/runner remain fixed until full actual report,
sidecar, diagnostics, artifacts, ledger dispositions and all identities authenticate.
Accepted forward/history and all prior failures remain preserved, not rerun/overwritten.
Only service-affected qualification is active; pending-publication and broader both-runtime/
Linux/S3/resources/native-Mac/dcc-02–05 remain open. No remote/production/scheduling/utility/
expiry/commit/push action.

## [2026-11-15] design | original-bound pending-publication control matrix

Read-only review while service-affected sources remain frozen separates standalone matching-
candidate update from coordinated original-bound maintenance. Partial host publication lacks
successful publication/checkpoint archives; pending journal candidates alone carry no original
coordinator/CLI identities. Planned genuine two-host genesis/replay failures, clean-resolution
refusals, exact candidate/input/original damage, receipt/intent-before-launch, real death/lost-
acknowledgment/clock-floor, repair-versus-resolution and missing migration/deletion coverage
require separate independent evidence. API/representation/original eligibility and pending-
recovery controls remain unselected/unexecuted; no manufactured history or relaxed validators.
Active service-affected runtime/controls/runner and all accepted originals stay unchanged;
broader both-runtime/Linux/S3/resources/native-Mac/dcc-02–05 remain open. No remote/production/
scheduling/utility/expiry/commit/push action.

## [2026-11-15] verification | pending-publication source-planning review closed

Complete 327-line successor/privacy review covers all five planning pages against the retained
active-state baseline; distinct full snapshot/delta retained. Source claims rechecked live;
fresh scoped audit passes nine Markdown files/seven frontmatters, 263 grounding paths,
493 inline sources and 458 wikilinks/82 sections. Both whitespace checks and all 307 frozen
source/control/lock identities pass; prepared/active/planning log placement verified. Historical
strict-focus idle statements now explicitly describe that closure, not the subsequent active
service-affected run. No completion notification/result inspected, runtime/control/API change,
new recovery execution or original eligibility claimed. Service-affected result review and
broader Linux/both-runtime/S3/resources/native-Mac gates remain open; no remote/production/
scheduling/utility/expiry/commit/push action.

## [2026-11-15] verification | Linux service-affected 307-control gate reviewed

The unchanged 13-module service-affected run passes 307 controls in 2,036.10 s, exit 0.
Report/sidecar, all 307 frozen identities, both actual exit-91 child diagnostics, the 5,982-entry
fixture snapshot, prior green/red evidence and accepted forward-history fixture authenticate;
the forward fixture remains unchanged and was not rerun. Read-only ledger review validates 170
of 188 ledgers and maps the 18 expected reopen refusals to explicit corruption controls. The
pre-COMMIT death remains blocked with no typed completion/authority; the post-COMMIT death
retains typed completion/authority through the supported history accessor in `DRAINING`, with
no raw-cursor advance. This closes only the service-affected gate. Pending-publication/missing-
original recovery, broader both-runtime integration, S3, representative resources, native-Mac
shutdown and dcc-02–05 remain open; no runtime changes, remote/production operation, scheduling,
utility, expiry, commit or push.
After updating the status pages, the fresh scoped changed-wiki/privacy audit passes nine Markdown
files/seven frontmatters, 263 grounded paths, 493 inline sources and 458 wikilinks; six linked
diagrams validate. The complete changed-text privacy scan and both repositories' whitespace
checks pass. Index/log frontmatter exceptions remain preserved; no whole-wiki lint is implied.

## [2026-11-15] implementation | authorized advisory utility and independent native review

Isolated Analytics `ee9c27a` / PyUtil `123b9d3` work preserves the busy producer checkout
and environments; interrupted-publication recovery remains producer-worker-owned. Submitted
source/report review authenticates 365 hashes, 76 portable smoke passes/zero skips and exact
307-test collection. Separate provisioned native five-module rerun passes 169/25 reviewed
Linux-only skips with all 83 identities unchanged; initial 24 missing-runtime failures remain
retained. Actual-Mac kqueue refuses tracking; restricted synthetic DBT build/test succeeds
with a prestarted helper. Deprecated Apple/private CPython dependencies are unselected;
closed lifetime/interruption/wrapper-death shutdown remains unqualified and REVIEW NEEDED.

Analytics navigation/pinned manual advisory v1 Status/raw intent Runs and unavailable
Partitions pass 46 offline tests/zero skips with ten unchanged source/lock identities.
First import/selector failures remain retained. Separate-runtime genuine producer-export
read passes with synthetic lock held and files unchanged. Activity stays synchronous/raw-only,
always Live diagnostic — uncoordinated; catalog, entity history, progress, delivery, actual
launch/finish and certificates remain unknown/pending, never permissions.

Pages updated: four utility artifacts, coordination handoff/plan/verification/Mac runbook,
native tension, canonical dashboard/ETL/entity guidance, index; both supporting READMEs.
Page created: isolated qualification procedure/approval worksheet (human-review-required).
Reconciled historical absent/uncommitted claims against submitted source without expanding
71/307 Linux focused/affected scopes or historical 880/554 full regressions. No full latest-HEAD,
S3/resources/native-shutdown/dcc-02–05/rollout acceptance. Concrete isolated environment/fixtures/
roots/access still need approval. No deployment, cron, real-dataset mutation, commit or push.

## [2026-11-15] verification | final scoped audit and cosmetic successor

Complete tracked/untracked review covers 23 changed files/five additions, 15 wiki pages/
13 frontmatters, 327 grounding paths/546 inline sources, 490 wikilinks/92 sections,
five local Markdown links, six Python syntax checks, 38 added Python section references
and three linked diagrams. Fresh final audit exits 0; complete retained diff/privacy review
and both whitespace checks pass. Separate result-recording output preserves the final report.
No new errors/privacy candidates. Index/log exceptions and three historical installed-package
citations absent from isolated Python 3.12 remain explicitly scoped, not whole-wiki lint.
Ruff's initial 14 broad findings/one new-file format mismatch remain retained. New-file
import/default/test-binding/format polish passes four-file default lint/format and six-file
core lint; eight reproduced baseline findings remain, not a full broad lint pass.

Distinct utility successor passes 46/zero skips (1.580 s), with full 76-line stderr/empty
stdout and ten unchanged successor identities. Native style successor passes genuine tiny
build/test (4.269 s), with full 38-line stdout/empty stderr and three unchanged identities.
All 365 submitted-archive sources, 83 producer identities, original reports, 11 pre-polish
source/lock snapshot files and retained runner reauthenticate; all 21 first-audit report
hashes, both retained diff hashes and six polished source identities match. No producer runtime/dependency or
query changes. Deprecated/private native dependencies, full catalog/lifecycles and concrete
Linux/S3/resource approvals remain open. No acceptance expansion, deployment, scheduling,
real-dataset mutation, commit or push.

## [2026-11-15] design | native Mac coordinated-launch review

Read-only tracing found the current coordinated client runs DBT through
`subprocess.call` (including a separate source preflight for `dbt-build`), while the
native restriction probe calls `dbtRunner().invoke()` in-process and observes
subprocess creation denied. The successful synthetic build/test therefore does not
exercise the production coordinated launcher. An in-process adapter would change
the launch contract and still would not prove resource-tracker ownership or complete
interruption/wrapper-death shutdown.

Recommendation: keep native Mac backend selection pending and ordinary local-only
DBT unchanged. Request an explicit human choice of a supportable containment boundary
with installation/ownership costs, or an explicit macOS coordinated-reader scope
amendment. Updated the native tension, coordination verification and index. Static
review only; no runtime/dependency/test changes or acceptance claim.

## [2026-11-15] design | native Mac helper/service boundary review

The human selected preserving native-Mac scope and authorizes design-only work on
an OS-supported helper/service boundary; backend code remains prohibited until
ownership and shutdown proof are accepted. Compared Apple's XPC/launchd lifecycle,
process-group cleanup, Endpoint Security fork/exec events, App Sandbox contract and
Virtualization.framework stop/entitlement API against the reader-release requirement.

No native helper/service contract establishes detached-descendant shutdown: XPC/
launchd service lifecycle is not a subtree contract, Endpoint Security fork is
notification-only, and public App Sandbox documentation does not promise no-fork
or tree-reaping semantics. A Linux guest stopped through Virtualization.framework
is a possible whole-guest boundary, but it is not native macOS DBT and requires an
explicit scope change plus guest/data/credential/resource design. Updated tension,
handoff, implementation plan, Mac qualification, verification and index. No backend,
entitlement request, runtime test or Mac acceptance performed.

## [2026-11-15] decision | native Mac best-effort reader shutdown

The human accepts process-group emptiness as a best-effort normal-release signal
for coordinated native-Mac readers, explicitly accepting the residual risk of an
escaped descendant. Timeout, supervisor death or uncertain group state retains the
reservation for manual verification; no automatic expiry. Native readers remain in
scope without a Linux VM or Docker prerequisite. Linux release rules and direct
local-only DBT remain unchanged. Updated the native tension, coordination design/plan,
handoff, Mac qualification, verification and index. No backend was implemented or
qualified; actual-Mac controls and service/dependency choice remain open.

## [2026-11-15] verification | native-Mac coordinated reader lifecycle

Recorded the isolated native macOS process-group candidate and its corrected PGID
handling in the coordination evidence. On the actual Mac, 12 synthetic lifecycle
controls pass; the focused reader/local-route batch passes 17 with 113 declared Linux
skips, and a final ephemeral stress driver passes 50 normal exits plus 20 same-group
descendant shutdowns. This is limited lifecycle qualification, not real DBT/data, S3,
service, representative-resource or backend/platform acceptance. Local-only DBT and
Linux supervision remain unchanged; source stays uncommitted and no deployment or
producer changes occurred.

## [2026-11-15] code | commit native-Mac coordinated reader overlay

Human authorization followed the scoped review: PyUtil native macOS supervision and
its 12-control synthetic suite are committed locally as `c549424` on the isolated
branch, based on `1f4897a`; the Analytics coordination evidence is committed locally
as well. Handoff notes now identify the exact source baseline and clarify that neither
commit was pushed. Both worktrees are clean. Linux runtime, real DBT/data, S3, service
and representative-resource gates remain open; no deployment or producer changes.

## [2026-11-15] verification | Linux cross-check of native reader candidate

Compared PyUtil `c549424`'s `1f4897a` parent with the prior Linux target `123b9d3`;
the intervening parent adds the feasibility probe and coordination README notes.
The focused Linux supervisor/client/lifecycle/local-route run passes 90 and skips 12
native-Mac-only controls (23.43 s). No Linux behavior change was observed. Black
module check and candidate whitespace check pass; the console launcher has a stale
interpreter reference. The 307-control service-affected gate and broader latest-HEAD,
actual-S3, DBT/data, resource and deployment gates were not rerun or qualified.

## [2026-11-15] planning | next coordination phases; PR deferred

Per human direction, added an ordered continuation plan without opening or preparing
a PR: close original-bound entity pending-publication/missing-original recovery and
entity-maintenance gaps; reauthenticate raw-only retry without broadening it; finish
dcc-04 evidence, dcc-02 service completion and dcc-03 client semantics in dependency order; run frozen
latest-revision platform regressions; then proceed only with a concretely approved,
isolated real-data/S3/resource qualification. The immediate baseline gate is affected
and full main/standalone Linux regression on `c549424`; neither the 90-control focused
run nor the parent's 307-control result substitutes. Native-Mac backend acceptance and
rollout remain separate final decisions. The plan grants no endpoint, data, production
or deployment authorization.

## [2026-11-16] verification | native macOS reader-scope requalification

Reviewed the pulled PyUtil reader-only dispatch repair (`badb67f`) and ran the actual
Mac six-module coordination suite: 67 passed, 116 declared Linux-only skips; the
dedicated native-Mac lifecycle module passes 12/12 on macOS 26.7.1 arm64/Python 3.12.12.
Generic/writer supervision remains Linux-only. Updated the handoff and qualification
records; no PyUtil source, S3/data, deployment or scheduling was changed.

## [2026-11-16] planning | development end-to-end integration first

The human clarifies that the entire sensor/raw-data/ETL/analysis deployment is
developmental and existing telemetry is expendable, not a production preservation
objective. Reviewed current PyUtil `badb67f` source and recorded Linux/Mac results:
Linux service/hourly writer/entity-init/replay and both reader paths exist; actual
S3/DBT combined integration is the leading gap, not missing whole implementations.
Earlier real-data compaction/cache/DBT component runs remain distinct from current
platform/service qualification. No new tests, telemetry/S3 access or source changes.

Created `wiki/work/dbt-compaction-coordination/integration-milestone-plan.md` with a
proposed finite DCC-E2E-01 checklist: actual sensor delivery, fresh cache, successive
hourly migrations, genuine Linux/Mac DBT builds, contested admission and measured
development-load behavior. Supersedes recovery-first sequencing with integration-first
and impact-based bounded repairs; general pending-publication/missing-original repair,
maintenance corners and historical ancestry/scale move to conditional backlog. Reuse
unchanged green suites, reconcile final regressions after repairs stabilize. Unsupported
failures stay blocked; a separately approved fresh disposable scope is preferable to
inventing recovery success. Actual-upload partition/late-arrival risk stays visible.

Updated coordination brief/design/plan/handoff/Mac runbook/development worksheet,
historical entity handoff, canonical ETL deployment context and index. Preserved
pre-existing uncommitted Mac evidence and private untracked environment files. Concrete
runner/data/access/mutation/resource selection remains needed; no broad cleanup,
ledger reset, collector change, scheduling, commit/push or production rollout authorized.
Planning-only validation: whitespace, changed-page frontmatter, new-plan sources/links
and complete diff/privacy review pass. Three migrations are proposed in total, counting
verified pilot hours; the live-delivery requirement remains explicit.

## [2026-11-16] handoff | approved Linux-runner integration plan

The human approved DCC-E2E-01 and this repository's wiki commit/push, and will
deliver the handoff to the Linux runner. Added the active assignment to
`wiki/work/dbt-compaction-coordination/dev_handoff.md`: select concrete scope, use
current evidence, create fresh entities, run hourly migrations and actual Linux/Mac
DBT clients, demonstrate contested admission, measure resources and report defects.
Three migrations count verified pilot hours; historical recovery-first instructions
remain reference/backlog, not the active assignment. Plan approval is not milestone
acceptance, remote execution or an unspecified data/source mutation authorization.

Recorded the strict UTC upload-time bucket contract as a separate later upload-client
review/enforcement task, with downstream delayed-data implications also deferred.
Current compliance is not assumed; no uploader/recompaction redesign or exhaustive
late-arrival campaign precedes the pilot. Updated the integration plan, implementation
plan, runbook, upload-contract TODO and index consistently. No application tests,
source, collector, environment or S3/data operations were performed for this handoff.

## [2026-11-16] implementation | zero-filled host activity chart gaps

Updated metadata and raw-row chart aggregation to emit zero-valued buckets across
the selected interval for each host with at least one accepted observation. The
existing adaptive bucket sizing and chart-point budgets still govern the expanded
series. Absolute raw-row scaling now uses a zero-compatible symmetric-log option;
UI and wiki text clarify that zero means no qualifying result was returned, not
proof of complete collection or true zero activity. Added focused synthetic tests;
all 52 app tests pass. Compile, lock, and diff checks pass; no live S3 validation
was performed.

## [2026-11-16] acceptance | zero-filled host activity chart gaps

The user tested the dashboard's zero-filled missing-bucket behavior and confirmed
it matches expectations. The behavior is accepted; live S3 validation remains
unperformed.

## [2026-11-16] implementation | concise host activity chart hovers

Chart hovers now show only UTC bucket time, host, and the selected metric: file
count or object size for metadata charts, and raw-row count or normalized peak
ratio for row charts. Added chart-spec tests and updated the dashboard README,
canonical tool page, work plan, verification record, and index. The full app suite
passes 54 tests; compile, lock, and diff checks pass.

## [2026-11-16] implementation | custom partition ranges and environment summary

Added a bottom-of-Activity-sidebar info box for effective non-secret dataset/AWS
settings, with credential values hidden. The rolling 12-hour default remains;
custom inclusive UTC `dayPK/hourPK` ranges have no duration cap and warn above
24 hours. Metadata partition requests are lazy and limited to eight concurrent
workers; raw glob discovery runs in 24-hour chunks. Duration-aware chart buckets
and the existing object, row, timeout, group, and chart-point budgets remain
active. App-scoped tests passed (50), compile/lock/diff checks passed. Live S3
custom-range behavior remains unverified.
## [2026-11-16] verification | first bounded real-data run blocked

The raw-only Linux DBT baseline passed 84 checks/56 successful nodes for the selected
three-hour window, and entity initialization completed. The first hourly compaction
published partial compacted/entity/metrics outputs but remained `BLOCKED` at 19:00Z.
Read-only verification isolated a checkpoint contract mismatch: with `delete_source=false`,
`metric_rows` emitted `deletion_status=completed` while the independent verifier requires
`not_requested`; all other migration/generation checks matched. The raw-process source
inventory remained 48 objects and no source deletion occurred. No compaction retry, repair,
cleanup or cursor advance was performed after the block; preserve the blocked ledger/evidence
and obtain explicit approval before recovery. Native-Mac real-data DBT remains pending. Details:
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] code | no-deletion checkpoint status correction

With human authorization, PyUtil now emits `not_requested` for checkpoints when
`delete_source=false`, validates repaired checkpoints against the original run's
deletion setting, and permits no-deletion checkpoint repair in the completion grammar.
Entity-enabled normal-completion and repaired-completion regressions cover the defect.
Six affected standalone modules pass 229 tests; the full standalone suite passes
697 tests with two approval-gated S3 tests skipped; scoped Ruff lint/format checks pass.
The code remains local and uncommitted/unpushed. The retained S3 run is still blocked:
no retry, repair, cursor advance, source deletion, or Mac real-data DBT occurred. The
historical checkpoint/partial outputs and evidence remain preserved pending explicit
approval of a reviewed recovery path. Details:
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] verification | blocked-run recovery eligibility audit

Read-only local inspection confirms the original phase archive records
`delete_source=false` but retains `deletion_status=completed` in both checkpoint
intent and verification; its standalone archive is complete while the separate
coordinator ledger remains blocked with an active writer, zero readers, and no
completion proof. The existing standalone repair validator rejects this immutable
candidate rather than correcting it, and the narrow coordinator repair path targets
an original failed/error CLI report. No existing repair command is established as
eligible; no S3 or ledger data was changed. A new narrowly audited correction path and
explicit approval of its exact S3 write/ledger resolution are required before the
real-data run can continue. Details:
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] cleanup | discard initial three-hour window and run state

At the human's direction, deleted the complete [19:00Z, 22:00Z) window rather than
repairing the blocked run: 228 raw, one partial compacted, three metrics, and two
entity objects. The exact pre-delete inventory matched; the unversioned S3 bucket
returned no errors and all selected prefixes verified empty afterward. Removed the
dedicated 378-file local run scratch after confirming no active process/open file and
matching its private hash inventory. No objects outside the selected hours were
targeted; unrelated PyUtil artifacts remain untouched. The next block begins 22:00Z,
but its end boundary needs human confirmation before fresh state or processing is
started. Exact object keys and local hashes remain in a permission-restricted private
audit under `/tmp/opencode/dcc-cleanup-audit-20261025T19-22Z/`. Details:
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] verification | next block compaction and entity-aware DBT replay

The confirmed [22:00Z, 2026-10-26 01:00Z) block completed fresh v5 entity initialization
and three hourly compactions with raw deletion disabled. Entity-aware Linux DBT source
preflight/build passed against an exact 29-object private snapshot via a read-only
localhost mirror: 59 models, 85 tests, zero mirror writes or out-of-scope reads. This is
offline DBT/entity evidence, not coordinated S3-reader or live-endpoint qualification;
the real ledger correctly remains DRAINING with due backlog. No native-Mac runner was
available; Mac DBT and coordinated-reader qualification remain open. Details:
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] verification | one-hour Linux continuation without Mac gate

With Mac evidence deferred, the human approved one Linux service tick for
[2026-10-26 01:00Z, 02:00Z), raw deletion disabled, then a stop/recheck. The hour
completed with a new proof and `deletion_status=not_requested`; all 86 raw objects
remain. The ledger advances to 02:00Z but remains DRAINING; the next hour has 84 raw
objects and no compacted/metrics outputs, so no coordinated DBT was attempted. The
original offline entity-enabled DBT replay still covers only 22:00Z–01:00Z. No further
hour or Mac run was performed. Details:
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] verification | second Linux-only continuation hour

The human approved and the Linux service completed [2026-10-26 02:00Z, 03:00Z) with
deletion disabled. Five hourly completion proofs now cover 22:00Z–03:00Z; raw inputs
remain, and metrics report `not_requested` with matching source/output counts for this
hour. The ledger remains DRAINING at 03:00Z; the next raw hour has 85 objects and no
compacted/metrics outputs. DBT replay still covers only the first three hours, and Mac
DBT remains deferred. Details: `wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] planning | production-path throughput reporting

Added a lightweight measurement convention for coordinated service-tick wall time,
excluding audits and DBT, with weighted files/s and decimal GB/s from per-hour processing
metrics. The in-flight batch predates monotonic timing, so ledger timestamps will be a
coarse fallback; exact timed samples will be collected on subsequent ticks. No throughput
sample was available at entry time. Details: `wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] verification | deletion-enabled catch-up to 15:00Z

The normal entity-enabled Linux service completed and independently verified eleven
deletion-enabled hours from 04:00Z to 15:00Z; the raw-only 04:00Z–05:00Z DBT baseline
passed (54 models/84 tests). The ledger is clean in DRAINING at 15:00Z with 17 proofs.
The initial ten-hour [05:00Z, 15:00Z) batch yielded a coarse timestamp-based estimate
of 668 seconds for 236 input files, 2,830,513 bytes and 3,069,413 rows, one expected
host per hour; weighted rates were 0.353 files/s and 4,595 rows/s. Exact monotonic
service-tick timing starts with the next batch. Coordinated DBT remains gated and Mac
remains deferred. Details: `wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] verification | monotonic timing and fail-closed stop at 19:00Z

Four deletion-enabled hours [15:00Z, 19:00Z) completed with monotonic service-subprocess
timing: 258.846 seconds total for 96 files, 838,133 input bytes and 836,228 rows; weighted
rates were 0.371 files/s and 3,231 rows/s (one expected host per hour). The next tick,
19:00Z–20:00Z, exited nonzero. Read-only checks show the ledger BLOCKED at 19:00Z with an
active unresolved writer. Read-only child evidence reports an observed host not
explicitly initialized/expected (exit 2); phase evidence shows no completed migration.
The 19:00Z raw partition remains and no compacted/metrics output was listed for that
hour. No retry, resolution or authority change was attempted. Coordinated DBT remains
gated pending an authorized supported resolution of the entity-expectation mismatch.
Details: `wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] analysis | failure classification at 19:00Z

Read-only source/evidence review localizes the failure to the explicit host-scope guard
in `update_entities`, before entity publication and raw compaction/deletion. The human
clarified that any host with data in the hour is valid, so classify this as a deterministic
implementation/requirements mismatch: the failed raw partition contains one additional
valid host beyond the configured/initialized one-host list. Keep run disposition
separately `BLOCKED`: the entity/deletion/multi-event run
is ineligible for current raw-only retry, entity replay is not admitted while BLOCKED,
and no supported recovery route is established for missing migration evidence. No retry
or ledger change was performed. The evidence-based classification rubric is in
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] implementation | dynamic observed-host entity processing

Implemented the PyUtil fix for the clarified requirement that a host observed in an
hour is valid. Entity processing now discovers seed/authority/observed hosts, creates
first-seen snapshots with first-observed-partition provenance, and grows authority host
evidence without weakening integrity checks. Entity-only verification, completion, and
checkpoint receipt validation were updated for cumulative host sets; invalid identity
and lifecycle safeguards remain. Verification: focused dynamic-host tests passed;
full `extras/raw-sensor-compact` suite **700 passed, 2 skipped**; changed production
modules passed Ruff. The blocked ledger and source data were not retried or changed.
Details: `wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] analysis | host-scope timeline review

Read-only comparison found one host in each compacted `raw_process` partition from
15:00Z–18:00Z, but two hosts in the failed 19:00Z raw partition and the following
20:00Z raw partition. The additional valid host has process-event timestamps in the
failed hour beginning 19:00:00Z, plus event timestamps back to September; `ReceiveTime`
is zero in the checked partitions. This does not show a mid-hour first appearance or
determine when the host came online. The fix must support discovered hosts and first-seen
entity initialization, not merely remove the allowlist guard. No host/object identifiers
were retained, and no source/ledger changes or retries occurred. Details:
`wiki/work/dbt-compaction-coordination/verification.md`.

## [2026-11-16] verification | resumed deletion-enabled scope reached 00:00Z

The resumed 23:00Z–00:00Z service tick completed with immutable evidence reporting
exit zero and migration complete. Independent readback found nine compacted exact-hour
objects, zero exact-hour raw objects after deletion, 172 raw objects in the next hour,
authority generation 29 committed, and matching authority/metrics generation IDs.
The ledger is at 00:00Z in `DRAINING` with no readers or waiting jobs. Two entity
snapshots, the authority object and 28 processing-metrics objects are present. This
readback verifies object-level publication and coordination state, not row-count
parity for this final hour; native-Mac DBT remains deferred.
<!-- SOURCE: Resumed Linux deletion-enabled service completion evidence, local ledger readback, S3 object inventory, authority/metrics Parquet readback, conversation 2026-11-17. -->

## [2026-11-16] plan | test-suite organization and classification

Created [[wiki/overview/test-suite-organization-and-classification]] after
inventorying 34 Analytics test files, 80 PyUtil Python test files, and 7 PyUtil
DBT SQL tests. The page classifies maintained regression, contract, integration,
qualification, live, and historical tests; proposes purpose-oriented directories;
identifies coordination/entity, compactor-verifier, Streamlit, and local/S3
review groups; and defines a no-delete review gate. No source or test files were
moved or deleted.
<!-- SOURCE: Read-only test inventory and collection review across Wintap-Analytics and Wintap-PyUtil, conversation 2026-11-16. -->

## [2026-11-17] plan | approved test-suite reorganization todo

Added the high-priority [[wiki/todo/test-suite-reorganization]] note pointing
to the approved [[wiki/overview/test-suite-organization-and-classification]] plan.
The TODO records that implementation is next, while preserving the plan's
no-delete and qualification-evidence review gates. No test files were moved or
deleted.

## [2026-11-17] handoff | parallel native-Mac DBT workstream activated

Updated [[wiki/work/dbt-compaction-coordination/dev_handoff]] for the Mac worker
to begin genuine reader-only DBT work in parallel with Linux/server finalization.
The handoff selects the current PyUtil candidate, requires a fresh isolated client
and output scope, prohibits Mac writer/deletion/ledger bypass, defines the bounded
reader/overlap sequence, and specifies sanitized return evidence. Prior deferred
Mac-DBT statements remain historical; no Mac execution result is claimed here.
<!-- SOURCE: Human direction to start native-Mac DBT in parallel with Linux/server finalization, conversation 2026-11-17. -->

## [2026-11-17] verification | compaction execution boundary reconciled

Recorded the Linux qualification boundary at 07:00Z after ten independently
verified deletion-enabled ticks and preserved the prior candidate-`402ead1` DBT
result (146/146 build, 87/87 explicit tests, 57 focused regressions). The current
verification page now states that no eleventh tick or native-Mac real-data result
is claimed; DCC-E2E-01 remains open for genuine Mac DBT and overlap evidence.
The attempted local rerun was not treated as qualification because the private
runner scope is unavailable and the checked-out main PyUtil environment is stale.
<!-- SOURCE: Linux ten-tick completion and DBT qualification evidence, plus local continuation checks, conversation 2026-11-17. -->
