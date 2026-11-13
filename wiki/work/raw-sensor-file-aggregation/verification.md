---
title: "Verification: Raw Sensor File Aggregation"
type: concept
confidence: medium
grounded_by:
  - wiki/work/raw-sensor-file-aggregation/brief.md
  - wiki/work/raw-sensor-file-aggregation/implementation_plan.md
  - wiki/work/raw-sensor-file-aggregation/references.md
  - ../Wintap-PyUtil/extras/raw-sensor-compact/pyproject.toml
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/engine.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/compaction.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/tests/test_s3_transport.py
  - ../Wintap-PyUtil/extras/raw-sensor-compact/src/raw_sensor_compact/deletion.py
  - ../Wintap-PyUtil/tests/test_compacted_inputs.py
  - ../Wintap-PyUtil/tests/test_compacted_s3_migration.py
policy: agent-editable
last_validated: 2026-11-12
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: draft
source_paths: wiki/work/raw-sensor-file-aggregation/verification.md
tags: [feature-work, verification, raw_sensor, parquet, duckdb, s3, compaction]
---

# Verification: Raw Sensor File Aggregation

**Current result:** fixed destination hours plus optional validated source-prefix
deletion on DuckDB 2.0.0; PyUtil dual-root input on its unchanged DuckDB 1.5.6.
**107 compactor tests passed, 2 skipped**; **299 PyUtil tests passed, 2 skipped**.
Full local raw/mixed/compacted migration passed: 54 equivalent models and 139 gates
per state. Copied live S3 migration passed: 897,395 rows, 4 equivalent host/pidstat
models and 10 gates per state, 29 copied source objects deleted and 29 original
source hashes unchanged. Initial fixed-root live output remains untouched at
`lintap/compacted` during qualification; those two outputs and all this work's
test fixtures were subsequently removed at the human's request (445 objects).
All 399 original raw hashes matched before/after cleanup. Rerun skip was previously
confirmed. No row sorting, run IDs,
manifests, reservations, conditional PUT or overlap suppression. Failed output is
manually cleaned; existence is not completion. Earlier generation evidence is historical
and superseded by [[wiki/decision/raw-sensor-compaction-fixed-hours-and-manual-cleanup]].
Expanded full live builds pass but strict results differ due to unchanged-input
nondeterminism. Human accepts this ANY_VALUE debt as non-blocking for compaction;
the approved rerun **passed** with exact bronze/schema/unaffected-model gates and
recorded affected downstream differences. All 54 models built in each state,
2,668,265 source rows were conserved, 399 copied objects became 10 outputs, and
all 399 original hashes remained unchanged. See the all-family rerun below.
Benchmark/default and broader transport/fault coverage remain pending. Required
test IDs and acceptance mapping are defined in the
[[wiki/work/raw-sensor-file-aggregation/implementation_plan]].

## Shared Development And Operational Check

Use DuckDB 2.0.0 to count all source rows and all merged rows in each exact
event-type/day/hour/optional-protocol partition. The operation is `UNION ALL`:
duplicates and rows with NULL fields count toward both totals.

```text
source_rows = COUNT(*) across every selected source file in the partition
merged_rows = COUNT(*) across every merged output shard in the partition
row_delta   = merged_rows - source_rows
passed      = (row_delta == 0)
```

Run the same function in development tests, after `compact`, and through the
read-only `verify` command. Report partition keys, both counts, delta, and status;
a mismatch or unreadable/missing required file fails verification. Small schema
fixtures separately check field preservation and name-aligned NULL filling.

## Test Commands

Runnable commands for the current slice, from the Wintap-PyUtil repository root. Actual outcomes
are recorded below; opt-in S3 access needs approved, explicitly scoped fixtures.
Commands in the earlier evidence sections were run before relocation from
Analytics unless explicitly labeled PyUtil; those historical results are preserved.

```bash
uv sync --project extras/raw-sensor-compact --locked --group dev
uv lock --project extras/raw-sensor-compact --check
uv run --project extras/raw-sensor-compact --locked python -c "import duckdb; print(duckdb.__version__); print(duckdb.connect().execute('select version()').fetchall())"
uv run --project extras/raw-sensor-compact --locked ruff check extras/raw-sensor-compact
uv run --project extras/raw-sensor-compact --locked ruff format --check extras/raw-sensor-compact
uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests -m 'not s3'
uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests -m s3
uv run --project extras/raw-sensor-compact --locked raw-sensor-compact --help
git diff --check
```

The `s3` marker covers a seeded read-only count test and a fresh-destination
write/verify/rerun-skip test. See the package README for approval/fixture variables;
no default bucket is selected. A skipped integration suite is not acceptance.
Current `verify` requires direct `--source-root`/`--destination-root` event roots
and explicit UTC hours. There is no manifest-backed verification mode.

## Evidence To Record Per Run

- Date, tool commit, dependency-lock identity, Python/OS, actual DuckDB and
  extension versions.
- Test ID/AC mapping, exact command, exit code, pass/fail/skip counts, duration,
  and evidence location. Sanitize credentials and signed URLs.
- Source inventory identity and scope, endpoint product/version and auth mode,
  fixed output root/hour coverage, destination preexistence and effective settings.
- Per-leaf keys, `source_rows`, `merged_rows`, `row_delta`, pass/fail, file counts,
  bytes, schemas, source immutability evidence, and fresh output read results.
- Injected failure point, observed partial destination state,
  rerun outcome, and destination cleanup outcome for recovery cases.

## Results

| Area | Status | Required evidence |
| --- | --- | --- |
| Source/API review | Complete, 2026-11-10 | Live consumer/S3 patterns and official docs summarized in [[wiki/work/raw-sensor-file-aggregation/references]]. |
| Planning-document validation | Passed, 2026-11-10 | Six pages: YAML/required fields/date/inbound links valid; 49 grounding entries and 42 wikilinks valid after the count-validation clarification. `git diff --check` passed. |
| P0 / runtime and endpoint | Bounded live pass | DuckDB 2.0.0/httpfs/profile reads/COPY/counts work. No conditional PUT required. Refresh/multipart faults and broad endpoint qualification pending. |
| P1–P2 / T01–T05 | Partial local/mocked passes | Exact-hour discovery, name/NULL/schema fixtures, duplicates, shared counts, local shards and file-reduction guard pass. Full partition/sharding/resource matrix and live listing/read checks pending. |
| P3 / T06–T08 | Fixed-root local and bounded live pass | Direct merge, existing-hour/protocol-parent skip, local partial validation failure/manual rebuild, unchanged live source/output hashes. Multipart failures, SIGKILL and broader faults pending; one writer assumed. |
| P4 / T09 | Fresh local and live verification pass | Direct-root CLI totals/deltas tested; fixed S3 output verified with zero delta. Count equality is not full-row multiset proof. |
| P5 / T10 | Not run | Representative S3 benchmark and documented D4 default. |
| P6 / manual workflow | Bounded basics pass; broader acceptance pending | Plan, compact, fresh verify, fixed-layout read and rerun skip pass. Consumer adaptation/representative acceptance pending. |
| T11 / scheduled readiness | Open dependency | [[wiki/todo/raw-sensor-upload-time-partition]] remains unresolved. |

### Planning Checks Executed — 2026-11-10

- `ruby -E UTF-8 -ryaml -rdate -ruri` with an inline read-only validator: passed
  YAML parsing, required fields, validation dates, grounding-path existence/URL
  syntax, and link/inbound-link checks for all five feature pages and the new
  publication tension. Also checked feature links in the existing index/log.
- `git diff --check`: passed. These are documentation checks, not execution of
   any planned compactor or S3 tests.

### Development Slice Executed — 2026-11-12

**Historical first slice:** commands/interfaces/results below preceded the fixed-root correction.

Branch: `work/raw-sensor-file-aggregation`, based on main commit
`6876015`; implementation was uncommitted during these checks. Python 3.14.0,
Darwin 25.6.0 arm64, uv 0.11.26, pytest 9.2.0, Ruff 0.17.5. Lockfile SHA-256:
`934d08aa56a63e9136a8c6218917051dea67664b56774da55cd1e541b79eda5e`.

- `uv sync --project extras/raw-sensor-compact --group dev`: passed; isolated
  environment created without changing Wintappy's dependencies.
- Actual Python/connection SQL version probe: `2.0.0` / `v2.0.0`. DuckDB 2.0.0
  relations no longer have `.fetchone()`; connection `.execute().fetchone()` works.
  Local spike confirmed parameterized `COPY`, explicit Parquet lists, `RETURN_FILES`
  and `FILE_SIZE_BYTES`. This does not prove S3 support.
- `uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-tests-20261112-02`:
  exit 0, **81 passed, 1 skipped**, 0.72 seconds. Skip: unapproved/unconfigured
  opt-in S3 fixture access; no endpoint requests performed.
- `uv run --project extras/raw-sensor-compact --locked ruff check extras/raw-sensor-compact`:
  exit 0, all checks passed. Initial 43 violations repaired without weakening rules.
- `uv run --project extras/raw-sensor-compact --locked ruff format --check extras/raw-sensor-compact`:
  exit 0, 14 files already formatted.
- `uv lock --project extras/raw-sensor-compact --check`: exit 0, 16 packages resolved.
- `uv run --project extras/raw-sensor-compact --locked raw-sensor-compact --help`:
  exit 0, only `plan` and `verify` exposed.
- `git diff --check`: passed (untracked new package also checked by Ruff).
- Scoped Ruby/Psych documentation check: 3 frontmatters satisfy required fields,
  21 local grounding paths exist, 15 wikilinks resolve, and the new canonical
  tool page has an index inbound link. New-package text whitespace scan passed.

Fixture evidence includes source SHA-256 unchanged after compaction, reordered
and missing fields, NULLs, within/across-file duplicate multiplicities, integer
widening, rejected incompatible types before writes, physical `filename`/hive
fields, zero-row schema retention, multiple output shards, fresh candidate
protection, exact leaf/namespace separation, added/modified/removed inventory,
and SQL timeout. Mocked S3 checks cover pagination and frozen identity/session
tokens, endpoint/TLS/profile configuration, extension setup and sanitized failures.
Count equality intentionally cannot detect same-count value changes or balanced
missing/extra rows. No full-row multiset or cross-version DBT gate is claimed.

### Live S3 Tests — 2026-11-12

**Historical generation implementation:** the old CLI/fixtures/manifest checks
below are not current commands or prerequisites. The endpoint observations remain
valid, but the conditional-write blocker was dissolved when those writes were removed.

Authorization: [[wiki/work/raw-sensor-file-aggregation/interview]] §Publication
Approval And Test Authorization. Used `AWS_PROFILE=lintap-alpha`, live
`../Wintap-PyUtil/wintap-run.env-lintap-alpha` source/window settings, and SDK-resolved
profile region/endpoint. The env file's command substitutions were not executed;
boto3 resolved their intended profile settings directly. No Wintappy file was
modified. Endpoint is S3-compatible, HTTP/path-style; product and server version
were not independently identified. Credentials/telemetry row values were not logged.

1. Bounded `plan`, 2026-11-11 08:00–09:00 UTC, pidstat/host, maximum 100 files,
   120-second timeout: passed. Exactly 24 pidstat and 5 host objects selected.
2. S3 setup exposed DuckDB 2.0.0 unfinished-result behavior: `.fetchone()` blocks
   `load_extension`/`install_extension` with `ResourceInUseException`. Fully draining
   internal results with `.fetchall()` repaired it; actual httpfs/COPY then worked.
3. Two fresh-key probes: conflicting `If-None-Match: *` PUT returned HTTP 200 and
   replaced the first object, rather than 412. Only new destination probes mutated.
4. Explicitly **unpublished** data test at
   `s3://lintap-alpha/compaction-tests/raw-sensor-20261112-unpublished-1b75059361d2`:
   direct COPY, actual output listing/schema/counts, fresh operational verify, and
   all source SHA-256 before/after passed in 27.154 seconds (includes hashing and
   verification, not a benchmark phase measurement). No completion manifest.

   | Leaf | Source files → merged | Source rows | Merged rows | Delta | Source bytes | Merged bytes |
   | --- | --- | --- | --- | --- | --- | --- |
   | pidstat / 20261111 / 08 | 24 → 1 | 897390 | 897390 | 0 | 2338885 | 7892113 |
   | raw_host / 20261111 / 08 | 5 → 1 | 5 | 5 | 0 | 37870 | 9418 |

   Explicit 128 MiB experiment target, 2 threads, ZSTD, row-group size 2048,
   1 GB memory/spill, 180-second cooperative timeout. Pidstat bytes **increased**
   about 3.37×; fewer objects does not imply compression/scan improvement.
   All 29 source byte hashes matched. No telemetry payload was stored locally.
5. Managed `compact`, fresh test base, same hour/host leaf: expected exit 2,
   `consumer_ready=false`, ignored-conditional message. Candidate:
   `s3://lintap-alpha/compaction-tests/raw-sensor-20261112-managed-7382f12f44b7/runs/20261112T203241Z-b96f1e44e3b24308bba83ef7968e8981`.
   Listing verified **one reservation object, zero Parquet, zero manifests**.
6. Tracked integration command:

   ```bash
   AWS_PROFILE=lintap-alpha \
   RAW_COMPACT_S3_TEST_APPROVED=isolated-write \
   RAW_COMPACT_S3_TEST_SOURCE=s3://lintap-alpha/lintap \
   RAW_COMPACT_S3_TEST_DESTINATION_BASE=s3://lintap-alpha/compaction-tests/raw-sensor-20261112-regression \
   RAW_COMPACT_S3_TEST_START_HOUR=2026-11-11T08:00:00Z \
   RAW_COMPACT_S3_TEST_END_HOUR=2026-11-11T09:00:00Z \
   RAW_COMPACT_S3_TEST_EVENT_TYPES=pidstat,raw_host \
   RAW_COMPACT_S3_TEST_EXPECTED_ROWS=897395 \
   uv run --project extras/raw-sensor-compact --locked pytest \
     extras/raw-sensor-compact/tests/test_s3_transport.py -m s3 -s \
     --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-s3-tests-20261112-01
   ```

   Exit 0, **1 passed, 1 skipped**, 23.39 seconds. Skip is the separate seeded
   read-only fixture test, not the write test. Same totals/file reduction and
   29 unchanged hashes verified. Candidate:
   `s3://lintap-alpha/compaction-tests/raw-sensor-20261112-regression/unpublished-684f932a8f4445a9ae94d72d9d9ef904`.
   It has no completion manifest and is not consumer-ready.
7. `uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-tests-20261112-04`:
   exit 0, **94 passed, 2 skipped**, 0.87 seconds. New cases cover local manifest
   CLI/fresh verification, new-generation reruns, copy/count/recheck/manifest
   failure isolation, output corruption/removal/addition, metadata lost responses,
   and fail-closed ignored-conditionals. Ruff check passes.

Private aggregate evidence: `raw-sensor-s3-evidence.json` and
`raw-sensor-s3-publication-rejection.json` in the approved session temp directory.
No credentials/telemetry rows; tracked tests/commands are the reproducibility
anchor. Test roots and abandoned metadata probes remain under
`compaction-tests/raw-sensor-20261112*`. No deletion, consumer cutover, or source
write was performed. Multipart protocol/request counts, failures and expiry were
not observed or certified. Historical, now dissolved publication blocker:
[[wiki/tension/raw-sensor-compaction-conditional-writes-vs-endpoint]].

Final local rerun (`--basetemp=.../opencode/raw-sensor-tests-20261112-05`):
**94 passed, 2 skipped**, 0.88 seconds; includes actual built-in Parquet extension
loads after drained startup/count results. Ruff lint passes, format check reports
16 files formatted, lock check and `git diff --check` pass. CLI help exposes
`plan`, `compact`, `verify`. Scoped Ruby/Psych validation passes for 8 frontmatters,
44 local grounding paths, 49 wikilinks and new-page index links. Changes remain
uncommitted/unpushed on `work/raw-sensor-file-aggregation`.

### Fixed Destination Tests — 2026-11-12

**Retain-source milestone:** this evidence predates the subsequently approved
dual-root DBT and optional prefix-deletion implementation below.

The human superseded UUID roots with fixed `lintap/compacted/<event>/dayPK/hourPK/`
output, skip-on-existence and manual cleanup; row order does not matter. Current
implementation has no publication module, reservation, manifest or source-delete API.

- Local command: `uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-tests-20261112-07`:
  exit 0, **92 passed, 2 skipped**, 0.79 seconds. Both skips are opt-in S3 tests.
- New fixed-root cases cover exact direct layout, skipped source not scanned,
  empty local-hour skip, entire protocol-parent skip, separate TCP/UDP merges,
  validation failure leaving partial output, rerun skip and manual fixture removal
  permitting rebuild, incompatible schema before destination creation, next-hour
  processing after a skip, CLI merge/verify/skip, and any-object S3 existence check.
- Bounded live `plan` passed with direct source/destination roots, pidstat/host,
  2026-11-11 08:00–09:00 UTC, maximum 100 files, 120-second timeout.
- Actual tracked fixed-root integration command:

  ```bash
  AWS_PROFILE=lintap-alpha \
  RAW_COMPACT_S3_TEST_APPROVED=isolated-write \
  RAW_COMPACT_S3_TEST_SOURCE=s3://lintap-alpha/lintap/raw_sensor \
  RAW_COMPACT_S3_TEST_DESTINATION_ROOT=s3://lintap-alpha/lintap/compacted \
  RAW_COMPACT_S3_TEST_START_HOUR=2026-11-11T08:00:00Z \
  RAW_COMPACT_S3_TEST_END_HOUR=2026-11-11T09:00:00Z \
  RAW_COMPACT_S3_TEST_EVENT_TYPES=pidstat,raw_host \
  RAW_COMPACT_S3_TEST_EXPECTED_ROWS=897395 \
  uv run --project extras/raw-sensor-compact --locked pytest \
    extras/raw-sensor-compact/tests/test_s3_transport.py -m s3 -s \
    --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-s3-tests-20261112-02
  ```

  Exit 0, **1 passed, 1 skipped**, 33.06 seconds. Separate read-only fixture test
  skipped; write/verify/rerun test passed. Explicit 128 MiB experiment shard target,
  2 threads, 1 GB memory/spill, 180-second cooperative timeout.

  | Leaf | Source files → merged | Source rows | Merged rows | Delta | Source bytes | Merged bytes |
  | --- | --- | --- | --- | --- | --- | --- |
  | pidstat / 20261111 / 08 | 24 → 1 | 897390 | 897390 | 0 | 2338885 | 7893189 |
  | raw_host / 20261111 / 08 | 5 → 1 | 5 | 5 | 0 | 37870 | 9401 |

  All 29 source SHA-256 hashes unchanged. Fresh direct-root `verify` passed. Second
  `compact` skipped both existing hours and merged-output SHA-256 hashes stayed
  unchanged. No source objects or test objects deleted. These destination hours
  now exist: do not rerun the fresh-fixture write test unchanged; use the CLI to
  demonstrate skip, or a separately approved absent-hour fixture for new writes.

Pidstat bytes increased about 3.37×; no compression/scan speedup or default chosen.
The ignored conditional PUT observation does not block this implementation.
Earlier probes/test roots remain untouched; no consumer cutover or sibling changes.

Final local rerun: `uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-tests-20261112-08`:
exit 0, **92 passed, 2 skipped**, 0.77 seconds. Ruff lint passes; format check
reports 16 files already formatted; `uv lock --project extras/raw-sensor-compact
--check` passes (16 packages). Changes remain uncommitted/unpushed on
`work/raw-sensor-file-aggregation`.

Final scoped Ruby/Psych check passes: 11 frontmatters satisfy required fields,
64 grounding paths exist, 57 wikilinks resolve, and every scoped page has an
inbound link. `git diff --check` passes. Current `compact --help` confirms direct
root flags, explicit target and UTC window; no generation/publication mode.

### Dual-Root DBT And Prefix-Deletion Tests — 2026-11-12

Authorization: [[wiki/work/raw-sensor-file-aggregation/interview]] §Dual-Root DBT
And Prefix Deletion Approval. The human accepts transient/failure overlap and
rare clock skew under the sensors' UTC upload-partition contract; prefix deletion
after a 5–10 minute grace is valid for these deployments. Default grace is 10,
minimum 5. Only new isolated copies were deleted; no original live cutover.

Branches remain uncommitted/unpushed: Analytics `work/raw-sensor-file-aggregation`,
PyUtil `work/raw-sensor-compacted-union`. The two existing private PyUtil run-env
files were preserved. No sensor/raw-document/dependency-pin changes.

1. `uv run --project extras/raw-sensor-compact --locked pytest extras/raw-sensor-compact/tests --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-delete-tests-20261112-02`:
   **107 passed, 2 skipped**, 1.09 seconds. New deletion cases cover grace boundary,
   whole exact hour including markers, adjacent-hour preservation, schema/COPY/
   validation/second-protocol failures preserving source, partial local deletion,
   rerun skip, symlink rejection, paginated S3 batches, per-key/transport errors,
   out-of-scope keys and remaining-object rejection.
2. From PyUtil: `uv run --locked --dev pytest tests`: **292 passed, 2 skipped**,
   48.94 seconds. Integration skips are separately opted in below. Existing 40
   source-preflight regressions pass, including private loopback S3 access faults.
3. From PyUtil:

   ```bash
   RAW_COMPACT_DBT_TEST_APPROVED=isolated-local uv run --locked --dev pytest \
     tests/test_compacted_inputs.py -s \
     --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-dbt-migration-20261112-04
   ```

   **7 passed**, 23.01 seconds. Fresh full DBT builds in raw-only, mixed, and
   fully compacted states each pass **139 model/test/hook gates**; all **54 model**
   schemas, row counts and sorted-result SHA-256 match, excluding only pidstat's
   derived source-object filename. Nonempty gold `process_summary` confirms this
   is not only empty-model equivalence. Known fixture: genuine within/across-file
   duplicates, reordered/missing/NULL columns, UTC midnight rollover and separate
   TCP/UDP leaves. **28 fixture source files deleted**, 56 input rows conserved.
   Optional families remain typed empty. Separate deliberate overlap yields six
   pidstat rows (four genuine rows plus two copied overlaps): no masking/dedup.
4. From PyUtil:

   ```bash
   RAW_COMPACT_DBT_TEST_APPROVED=isolated-s3-copy-delete \
   RAW_COMPACT_DBT_TEST_ROOT=s3://lintap-alpha/compaction-tests/dbt-union-20261112-02 \
   uv run --locked --dev pytest tests/test_compacted_s3_migration.py -s \
     --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-dbt-s3-migration-20261112-02
   ```

   **1 passed**, 97.25 seconds. Copied the previously qualified 29 pidstat/host
   source objects for 2026-11-11 08:00 UTC into the new test subtree. Raw-only
   baseline; host migrated/deleted with pidstat still raw; then pidstat migrated/
   deleted. Three fresh scoped DBT builds: **10 gates each**, **4 equivalent
   bronze/silver models**; all **897,395 source rows** conserved. This live test
   is host/pidstat only, not live full-gold/event-family acceptance. Every merged
   leaf has zero count delta. **29 copied source objects deleted by hour prefix**;
   all **29 original source SHA-256 hashes unchanged**. Copied compacted output
   remains for inspection. No deletion of `lintap/raw_sensor` or `lintap/compacted`.

Development repairs: two synthetic fixture SQL aliases required quoting/`AS`;
the initial live-copy attempt failed in the verification harness before any merge
because fresh DuckDB connections need their own temporary S3 secret. Repaired
the harness to configure profile/endpoint access without persistent credentials.
Failed fixture `compaction-tests/dbt-union-20261112-01` retains its raw copies;
the passing run used a fresh `-02` root, not an automatic cleanup/reuse fallback.

Sorted-result hashing is a bounded-memory test comparison, not production row
sorting or a new compactor fidelity gate. Actual deletion is based on prefix
closure plus mandatory per-leaf row counts/schema/inventory validation. After
source deletion, source/output `verify` no longer expresses conservation; retain
the merge report and compare migrated consumer results with a saved baseline.
Failures still stop for manual reconciliation, not automatic delete completion.

Final static checks: compactor Ruff lint/format pass (18 Python files); PyUtil
Black/isort pass for changed Python files. Both lock checks pass (16 compactor,
210 PyUtil packages) with dependency pins unchanged. `git diff --check` passes
in both repositories. Scoped documentation validation: 12 frontmatters, 86
existing current grounding paths, 74 resolving wikilinks and all scoped inbound
links pass. Canonical PyUtil repo page retains **15 pre-existing unavailable
`../Wintappy/` checkout anchors**; these are explicitly excluded from current-path
validation rather than falsely reported as repaired or revalidated.

### Full-Model Live-Copy Expansion — 2026-11-12

The human requested all models after the host/pidstat test instructions.
Read-only inventory of the same original 2026-11-11 08:00 UTC hour found:

| Event | Files | Bytes |
| --- | ---: | ---: |
| pidstat | 24 | 2,338,885 |
| raw_host | 5 | 37,870 |
| raw_macip | 5 | 10,420 |
| raw_process | 114 | 5,696,897 |
| raw_process_conn_incr (TCP/UDP) | 114 | 1,379,558 |
| raw_process_file | 57 | 20,028,444 |
| raw_selinuxavc | 22 | 87,684 |
| raw_selinuxinteraction | 35 | 5,802,861 |
| raw_selinuxtransition | 23 | 88,644 |
| **Total** | **399** | **35,471,263** |

Added `RAW_COMPACT_DBT_TEST_SCOPE=all-models` to the existing opt-in S3-copy
regression. Default remains scoped host/pidstat; invalid scopes fail. Full scope
copies available DBT inputs (including historical aliases) after a 1,000-file/
256-MiB preflight cap, then builds the entire graph in three fresh databases.
Schema comparison now includes column types as well as names; only pidstat's
derived filename is excluded. Inventory, per-state result snapshots and merge
reports are saved in the local fixture directory. Original source/output roots
and earlier S3 fixtures are not modified. Registry/image-load are absent, so
their optional models are included but not nonempty live-family qualification.

Local regression with strengthened schema comparisons:

```bash
RAW_COMPACT_DBT_TEST_APPROVED=isolated-local uv run --locked --dev pytest \
  tests/test_compacted_inputs.py -s \
  --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-dbt-all-local-20261112-01
```

**7 passed**, 22.77 seconds; 54 equivalent models and 139 gates per state.

Ordinary PyUtil regression rerun: `uv run --locked --dev pytest tests`:
**292 passed, 2 opt-in integration skips**, 48.21 seconds. Changed-Python
Black/isort, PyUtil lock check and both repos' `git diff --check` pass. Scoped
wiki checks pass (12 frontmatters, 86 current grounding paths, 74 wikilinks);
15 inherited old checkout anchors remain excluded as previously documented.

Full S3 test launched with a new fixture root, not an existing one:

```bash
RAW_COMPACT_DBT_TEST_APPROVED=isolated-s3-copy-delete \
RAW_COMPACT_DBT_TEST_SCOPE=all-models \
RAW_COMPACT_DBT_TEST_ROOT=s3://lintap-alpha/compaction-tests/dbt-union-all-20261112-01 \
uv run --locked --dev pytest tests/test_compacted_s3_migration.py -s \
  --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-dbt-all-s3-20261112-01
```

**Failed strict equivalence**, 273.04 seconds. Raw-only and mixed full DBT builds
both passed **139 gates** (54 models, 84 tests and one hook). The host merge
validated five rows with zero delta and deleted five copied host source objects;
all other families remained raw. All 11 bronze models matched, as did model
schemas throughout. **17 model result snapshots differed**, including changes
in downstream row counts: `all_files` 6,683 → 6,689, `files` 9,103 → 9,113,
`files_tmp_v1` 9,154 → 9,166, and `process_exe_file_summary` 689 → 701.
The fully compacted state was **not reached**, and the test's final all-source
SHA-256 assertion did not execute. Do not claim all-family migration acceptance.

Rebuilt the **identical mixed fixture**, without S3 compaction/deletion, into
`mixed-repeat/wintap.duckdb` under the same local fixture directory using the
existing `build(..., timeout=600)` and `snapshot(...)` helpers with the same
profile, endpoint, date/hour and dataset root. **139 gates passed** again, but
**18 model snapshots differed** from the previous mixed build; schemas still
matched. `files` 9,113 → 9,110, `files_tmp_v1` 9,166 → 9,160 and
`process_exe_file_summary` 701 → 695. Local `mixed-repeat/comparison.json`
records the complete diff list. This control demonstrates existing full-graph
nondeterminism even without input migration.

Read-only keyed comparisons of materialized raw/mixed results found differences
in `process.process_name` (7,935 identities), `process_path`/derived filename/
file_id (9,090), args (211), user_name (23), parent_pid_hash (55), parent_os_pid
(27); `process_file` differed only in the unordered `os_pid` representative
(36 groups). `process.sql` uses unordered `ANY_VALUE` for those representative
fields, and `process_file.sql` uses `ANY_VALUE(pid)`. Added a direct shipping-SQL
diagnostic that reverses identical two-row input and proves selected path,
filename and file_id change. `uv run --locked --dev pytest
tests/test_compacted_inputs.py::test_existing_process_model_depends_on_row_order`:
**1 passed**, 0.48 seconds. No production model or comparison normalization was
changed to hide this result; unordered aggregate effects elsewhere remain to
be analyzed rather than claimed as fully explained.

Fixture remains at `s3://lintap-alpha/compaction-tests/dbt-union-all-20261112-01`:
**394 raw copied objects + one compacted host output** (9,318 bytes). Do not
rerun the creation test against this existing root. Original live roots and
earlier fixtures were not targeted by any write/delete operation; no production
cutover. Full result-equivalence is blocked by
[[wiki/tension/dbt-arbitrary-representatives-vs-compaction-equivalence]]. A human
must choose deterministic representative semantics or explicitly narrow the
acceptance contract before this gate is changed.

After adding the diagnostic, the full local migration suite was rerun with
`RAW_COMPACT_DBT_TEST_APPROVED=isolated-local uv run --locked --dev pytest
tests/test_compacted_inputs.py -s
--basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-dbt-all-local-20261112-02`:
**8 passed**, 23.43 seconds; the synthetic migration still matches all 54
models/139 gates per state. Final scoped wiki checks pass: 13 frontmatters,
92 current grounding paths, 81 wikilinks and scoped inbound links, with the same
15 inherited old-checkout grounding exclusions. Black/isort and both repos'
`git diff --check` pass.
Final ordinary PyUtil suite: `uv run --locked --dev pytest tests`:
**293 passed, 2 opt-in skips**, 49.96 seconds. Live strict-equivalence failure
is separately recorded above, not counted as a passing skipped integration test.

### Accepted ANY_VALUE Diagnostics And All-Family Rerun — 2026-11-12

The human explicitly says existing ANY_VALUE data-quality issues are **not a
compaction blocker**; [[wiki/work/raw-sensor-file-aggregation/interview]] §ANY_VALUE
Debt Does Not Block Compaction. This resolves the gate conflict by separating
source fidelity from representative semantics, not by fixing the quality issue.

Added explicit `RAW_COMPACT_DBT_COMPARISON=any-value-diagnostics` for full scope;
default remains strict. The test computes 32 ANY_VALUE-containing/dependent
models from the baseline DBT manifest. Every schema and model-set must match;
every bronze result remains exact. Results outside the closure remain exact;
differences inside it are saved with row counts/hash values as diagnostics.
Membership does not prove each difference's cause and is not a full-equivalence
claim. No production DBT model changes, output normalization, deduplication,
thread-count changes or compactor sorting. Six offline regression cases pass
for the closure, explicit diagnostic reporting, strict default and mandatory
bronze/schema/unaffected-model/model-set gates (`pytest
tests/test_compacted_s3_migration.py`: 6 passed/1 live skip, 0.20 seconds).
Ordinary full PyUtil suite: **299 passed, 2 opt-in skips**, 49.69 seconds.

Rerun all three states in a fresh copied dataset so original-hash comparison
can complete end-to-end; the earlier mixed fixture remains untouched:

```bash
RAW_COMPACT_DBT_TEST_APPROVED=isolated-s3-copy-delete \
RAW_COMPACT_DBT_TEST_SCOPE=all-models \
RAW_COMPACT_DBT_COMPARISON=any-value-diagnostics \
RAW_COMPACT_DBT_TEST_ROOT=s3://lintap-alpha/compaction-tests/dbt-union-all-20261112-02 \
uv run --locked --dev pytest tests/test_compacted_s3_migration.py -s \
  --basetemp=/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-dbt-all-s3-20261112-02
```

**7 passed**, 502.83 seconds (8 minutes 22 seconds): six offline safety cases plus
the end-to-end live-copy migration. Raw-only, mixed and compacted-only full DBT
builds each pass **139 gates**; **54 models** built in each state. All **11 bronze
snapshots** and all **54 model schemas** match exactly; **36 model results** match
in every state. Eighteen mixed-state and seventeen compacted-state model results
differ within the approved ANY_VALUE-containing/dependent closure (18 distinct
models overall). Full names/counts/hashes are saved as diagnostics; no difference
outside that closure or in bronze/schema/model sets was accepted.

| Leaf | Source files → outputs | Rows | Delta |
| --- | ---: | ---: | ---: |
| raw_host | 5 → 1 | 5 | 0 |
| pidstat | 24 → 1 | 897,390 | 0 |
| raw_macip | 5 → 1 | 5 | 0 |
| raw_process | 114 → 1 | 120,310 | 0 |
| raw_process_conn_incr / tcp | 57 → 1 | 14,764 | 0 |
| raw_process_conn_incr / udp | 57 → 1 | 3,215 | 0 |
| raw_process_file | 57 → 1 | 1,286,439 | 0 |
| raw_selinuxavc | 22 → 1 | 148 | 0 |
| raw_selinuxinteraction | 35 → 1 | 345,801 | 0 |
| raw_selinuxtransition | 23 → 1 | 188 | 0 |
| **Total** | **399 → 10** | **2,668,265** | **0** |

**399 copied source objects deleted** after validation; no copied raw objects
remain. All **399 original source SHA-256 hashes unchanged** against the saved
pre-copy baseline. Input bytes 35,471,263; output bytes 32,772,727 under these
settings, not a representative scan-speed/compression benchmark. Protocol leaves
stay separate. Registry/image-load inputs were absent, so those optional models
are included but their nonempty live families remain unqualified.

Passing compacted copy survives at
`s3://lintap-alpha/compaction-tests/dbt-union-all-20261112-02/compacted`; this is now
suitable for **read-only full DBT builds**. Use a fresh local database, date
20261111 and inclusive hours 08–08; omit `--select`. See the PyUtil DBT guide's
manual full-model test command. Do not rerun the initially-absent-root migration
test against this existing fixture. Earlier mixed/scoped fixtures, original
`lintap/raw_sensor` and overlapping `lintap/compacted` remain untouched. No live
production migration or consumer cutover.

Evidence under the named local fixture directory: `inventory.json`,
`original-sha256.json`, `mixed-merge.json`, `compacted-merge.json`, `summary.json`,
and each state's DBT target/logs/database plus `snapshot.json` and comparison
diagnostics. No repaired production ANY_VALUE semantics or full downstream
equivalence is claimed.
Final changed-Python Black/isort and both repos' `git diff --check` pass.
Scoped wiki validation passes: 13 frontmatters, 94 current grounding paths,
82 wikilinks and scoped inbound links; the same 15 inherited old-checkout
grounding exclusions remain documented rather than claimed repaired.

## PyUtil Compactor Relocation — 2026-11-12

Following the human ownership correction, the 17 Python source/test files,
README, pyproject and lockfile now live at
`../Wintap-PyUtil/extras/raw-sensor-compact/`. Source/test logic and dependency
pins are unchanged; only README ownership/links/commands and the two DBT
integration subprocess paths changed. Main pipeline dependency files and private
run-env files were not changed by relocation. A scoped `.gitignore` exception
ensures the nested compactor lockfile is included despite PyUtil's blanket
`uv.lock` ignore; generated Ruff cache remains ignored.

The old environment/caches/bytecode were not reused or deleted. After verifying
only generated artifacts remained, archived them outside the repo at
`/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/raw-sensor-compact-pre-relocation-generated-20261112`.
UV created a fresh environment at the new package path. No package directory
remains under Analytics `extras/`; historical evidence and commands above remain
intact and current source anchors now cite PyUtil.

Commands below ran from the PyUtil repository root:

| Command | Result |
| --- | --- |
| `uv run --project extras/raw-sensor-compact --locked --group dev pytest extras/raw-sensor-compact/tests` | **107 passed, 2 opt-in S3 skips**, 1.57 seconds |
| `uv run --locked --dev pytest tests` | **299 passed, 2 opt-in skips**, 49.64 seconds |
| `RAW_COMPACT_DBT_TEST_APPROVED=isolated-local uv run --locked --dev pytest tests/test_compacted_inputs.py -s` | **8 passed**, 23.25 seconds; all **54 models equivalent**, **139 gates per state**, **28 isolated fixture sources deleted** |
| `uv run --project extras/raw-sensor-compact --locked raw-sensor-compact --help` | Pass: unchanged `plan`/`compact`/`verify` CLI |
| Compactor/main `uv run ... python -c "import duckdb; print(duckdb.__version__)"` | **2.0.0** at new standalone package / **1.5.6** in main pipeline |
| `uv lock --project extras/raw-sensor-compact --check`; `uv lock --check` | Pass: 16 / 210 resolved packages |
| Compactor `ruff check` / `ruff format --check` | Pass: 18 Python files formatted |
| Integration tests `black --check` / `isort --check-only` | Pass |
| Both repositories' `git diff --check` | Pass |

No S3 writes, deletions, live-copy test reruns or production cutover were performed.
Prior live qualification remains the recorded evidence, not a new relocation
run. Wiki planning/evidence ownership remains Analytics; executable compaction
and DBT ownership is PyUtil. Changes remain uncommitted/unpushed.
Scoped wiki validation passes: 13 frontmatters, 96 current grounding paths,
83 wikilinks and all scoped inbound links. The same 15 inherited unavailable
`../Wintappy/` anchors remain excluded as documented debt, not repaired here.

## S3 Artifact Cleanup — 2026-11-12

The human approved cleanup of the artifacts created by this work and committing
the current changes. Read-only inventory identified exactly **445 objects /
102,200,467 bytes**. Ownership was grounded in the recorded fixture paths,
November 12 creation times and the initial fixed-output sizes. Before mutation,
the complete selected key/size/ETag/LastModified inventory was saved and rechecked;
any change would stop cleanup before deletion. Only those exact keys were sent
to one batched SDK `delete_objects` call, not a broad bucket/root deletion.

| Artifact prefix (bucket `lintap-alpha`) | Objects removed |
| --- | ---: |
| `compaction-tests/dbt-union-20261112-01/` | 29 |
| `compaction-tests/dbt-union-20261112-02/` | 2 |
| `compaction-tests/dbt-union-all-20261112-01/` | 395 |
| `compaction-tests/dbt-union-all-20261112-02/` | 10 |
| `compaction-tests/raw-sensor-20261112-c202c43f34b1/` | 1 |
| `compaction-tests/raw-sensor-20261112-managed-7382f12f44b7/` | 1 |
| `compaction-tests/raw-sensor-20261112-probe-737f5cd433db4aba9106b0413483e7be/` | 1 |
| `compaction-tests/raw-sensor-20261112-regression/unpublished-684f932a8f4445a9ae94d72d9d9ef904/` | 2 |
| `compaction-tests/raw-sensor-20261112-unpublished-1b75059361d2/` | 2 |
| `lintap/compacted/pidstat/dayPK=20261111/hourPK=08/` | 1 |
| `lintap/compacted/raw_host/dayPK=20261111/hourPK=08/` | 1 |
| **Total** | **445** |

SDK returned **445 exact-key deletion confirmations, zero errors**; subsequent
listings found **zero remaining objects** in every selected prefix. Bucket
versioning is disabled and scoped multipart inventories contain **zero unfinished
uploads**. All **399 original source SHA-256 hashes matched before and after**
cleanup against the saved full-live-test baseline. No `lintap/raw_sensor` key
was a deletion target and no original telemetry was modified.

Private local inventory/results remain at the approved session temp directory:
`raw-sensor-s3-cleanup-20261112-plan.json` (exact keys/identities/source hashes)
and `raw-sensor-s3-cleanup-20261112-result.json` (prefixes/counts/results).
Earlier local DBT/merge/snapshot evidence remains. Historical S3 fixtures and
initial retain-source outputs no longer exist; documentation marks the saved-copy
DBT command as historical rather than advertising an available dataset. No
production migration/cutover or new live qualification was performed.

PyUtil implementation committed as `aa99efd` on
`work/raw-sensor-compacted-union` (33 files; compactor, dual-root DBT, regression
tests and operational documentation). Private run-env files remain untracked
and unchanged. Analytics wiki/evidence is committed separately on
`work/raw-sensor-file-aggregation`; neither branch was pushed. Final staged diff
checks pass; scoped wiki validation passes 13 frontmatters, 96 current grounding
paths and 84 wikilinks/inbound links, retaining the same 15 legacy exclusions.

## Benchmark Record

For each candidate, retain the corpus description and effective size/codec/
threads/row-group settings, repeated cold/warm measurements, per-family file/
byte/row counts and row delta, shard-size distribution, compaction-plus-count time,
peak RSS/spill, and DuckDB 2.0.0 scan time. Include request/transfer measurements
where available. Candidates in the plan are experiments, not an adopted default.

**Selected default:** Undecided. **File reduction demonstrated:** Local synthetic
fixtures and a bounded 9-family/10-leaf live-copy hour, not a representative S3 benchmark.

## Manual Checks And Known Gaps

- Fixed-root/skip/manual-cleanup is approved. One writer per destination and no
  reads of an hour during merge are operating assumptions, not enforced locks.
   Existence does not certify a complete merge. PyUtil's direct compacted-root
   consumer is qualified for the recorded copy; no manifest enforcement is required.
- Apply the confirmed filename rule: object filenames and derived pidstat
  `filename` values may change. Preserve `dayPK`/`hourPK` and existing `protoPK`
  leaves; use small fixtures to check physical payload fields.
- Development and operations share the count check. Failures return errors but
  can leave partial output; later runs skip it until manually cleaned. Broader
  credential-expiry, multipart/COPY/SIGKILL/spill-fault and resource tests pending.
- Compare a stable, recorded source inventory with the output. A completed hour
  alone does not prove that delayed upstream uploads have stopped.
- Prefix deletion is tested on isolated copies. Original live rollout remains
  separately scoped/unperformed; deployment clock risk is explicitly accepted.
  Confirm rollback to source of the same coverage and that a
  fresh consumer database is used when materialized DBT results need rebuilding.

## Follow-Ups

Append real command results as each implementation step completes; update the
plan's checklist and wiki log. Promote supported operating behavior only after
manual acceptance. Track daily compaction and scheduling as later work.
