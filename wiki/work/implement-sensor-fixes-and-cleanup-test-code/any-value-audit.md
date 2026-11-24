---
title: "ANY_VALUE Column Contract Audit"
type: diagnostic
confidence: medium
grounded_by:
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/host.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/selinux_attribution.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_image_load.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_conn_incr.sql
  - ../Wintap-PyUtil/wintap_dbt/models/silver/process_net_conn.sql
  - ../Wintap-PyUtil/wintap_dbt/models/gold/process_file_summary.sql
  - ../Wintap-PyUtil/wintap_dbt/models/gold/process_net_summary.sql
  - ../Wintap-PyUtil/wintappy/datautils/rawtostdview.sql
policy: agent-editable
last_validated: 2026-11-23
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: mixed
status: draft
source_paths: ../Wintap-PyUtil/wintap_dbt/models; ../Wintap-PyUtil/wintappy/datautils/rawtostdview.sql
tags: [wintap, wintappy, data-pipeline, dbt, data-quality, any-value, process-events]
---

# ANY_VALUE Column Contract Audit

## Baseline and method

This is a read-only source inventory at PyUtil revision
`4085747ea4104403c5c53eec552ca4dc65c164a7` (`2026-11-23`). The source SQL search
was:

```text
grep -RniE --exclude-dir=target --include='*.sql' 'any_value[[:space:]]*\(' .
```

The result is **73 textual matches across 14 source SQL files**: **71 executable
function calls** and **2 comments** in `rawtostdview.sql` (the TODO mentioning
`any_value()` and its warning). Generated `wintap_dbt/target/` copies were excluded;
they are not independent model uses. This count is a baseline and must be rerun at
each pinned revision.

No PyUtil SQL or test file was changed during this inventory.

## File inventory and preliminary disposition

The classifications below are hypotheses from the SQL grouping keys and expressions.
They are not approval to retain or replace a use until the corresponding distinct-
value and null-pattern fixtures pass.

| Layer | File | Calls | Fields/features | Preliminary contract |
|---|---|---:|---|---|
| Silver | `models/silver/process.sql` | 12 | `os_family`, agent/host/PID, name, args, user, parent, path, hashes | Constant `os_family` is invariant-safe. Identity and metadata need group-specific conflict QA. Name/path/args are ordering- or evidence-sensitive; name/path must remain paired. |
| Silver | `models/silver/host.sql` | 9 | `os_family`, OS, version, architecture, processor fields, domain fields | Constant `os_family` is invariant-safe. Other fields already have `num_*` diagnostics; representative values are conflict-visible until invariance is proven. |
| Silver | `models/silver/selinux_attribution.sql` | 10 | direct process identity and temporal fallback identity fields | Direct `process_name` is ordering-sensitive. PID hash, OS PID and lifecycle timestamps need identity/conflict checks. Temporal values are only consumed when `candidate_count = 1`; test that guard and keep ambiguity null. |
| Silver | `models/silver/process_image_load.sql` | 5 | OS PID, agent, hostname, process name, file MD5 | OS PID/agent/host are invariant candidates under the image-load grouping. Name and MD5 require evidence that the `pidhash`/filename group cannot contain changing values. |
| Silver | `models/silver/process_registry.sql` | 1 | OS PID | Likely invariant within the full `group by all` key; retain only with a duplicate/conflict fixture. |
| Silver | `models/silver/process_file.sql` | 1 | OS PID | Likely invariant within the full `group by all` key; retain only with a duplicate/conflict fixture. |
| Silver | `models/silver/process_conn_incr.sql` | 1 | OS PID | Candidate invariant within the connection-increment grouping; test PID reuse and malformed rows. |
| Silver | `models/silver/process_net_conn.sql` | 1 | OS PID | Candidate inherited invariant from `process_conn_incr`; test the second aggregation independently. |
| Silver | `models/silver/host_ip.sql` | 1 | Constant `os_family` | Invariant-safe constant. |
| Gold | `models/gold/process_image_load_summary.sql` | 1 | OS PID | Candidate invariant under `pid_hash`; verify image-load source does not combine conflicting PID values. |
| Gold | `models/gold/process_registry_summary.sql` | 1 | OS PID | Candidate invariant under `pid_hash`; verify registry source does not combine conflicting PID values. |
| Gold | `models/gold/process_file_summary.sql` | 1 | OS PID | Candidate invariant under `pid_hash`; the paired `arg_max` process name is a separate deterministic policy and must not be inferred from this shortcut. |
| Gold | `models/gold/process_net_summary.sql` | 1 | OS PID | Candidate invariant under `pid_hash`; the paired `arg_max` process name is a separate deterministic policy and must not be inferred from this shortcut. |
| Legacy | `wintappy/datautils/rawtostdview.sql` | 28 text / 26 calls | Duplicated host, host-IP, process and image-load projections plus 2 comments | Treat as a compatibility projection. Reconcile each executable call with its DBT counterpart; do not assume a fix in one path repairs the other. |

## Initial field-contract conclusions

### Safe to retain only after proof

The following uses are plausible invariant-safe shortcuts when the grouping key is
correct and the eligible values are normalized consistently:

- literal constants such as `any_value('windows')`;
- OS PID in event summaries grouped by a birth-scoped identity or a complete event
  key;
- agent/hostname fields in a source relation whose grouping key already fixes the
  agent and host; and
- image/file metadata where the grouping key fixes the file identity and source
  semantics guarantee stability.

“Plausible” is not “proven.” Each retained use needs a test showing that all eligible
non-null values are equal. Repeated identical rows are harmless and must not be
reported as conflicts.

### Conflict-visible fields

Host metadata and process metadata already expose distinct-value counts in several
models. Those counts should become explicit contract checks: a representative value
may remain for compatibility, but disagreement must be visible and must not be
silently interpreted as canonical truth. Null-only groups need a separately defined
result.

### Ordering-sensitive fields

The process lifetime projection must not use independent `any_value` selection for:

- `process_name`;
- `process_path`;
- executable-related arguments; or
- any other field whose meaning depends on the selected observation.

These fields can differ across fork/start, failed `exec_attempt`, successful
`exec_success`, Refresh, and Stop observations. A deterministic representative must
select a single eligible row and take paired fields from that row. The lifetime
policy remains open between initial, latest-successful, and latest-observed image.

SELinux temporal fallback is a special case: when more than one candidate lifetime
matches a `(host, pid, event_time)`, all arbitrary candidate fields must remain
semantically suppressed, not merely accompanied by an ambiguity count.

## Downstream consumer trace

The audit must not stop at the model containing `any_value`. The direct DBT
consumer trace at the same checkout includes:

- `process` → `process_summary`, `process_path`, `process_exe_file_summary`,
  `process_chart`, `telemetry_event_summary`, `attribution_quality_summary`, and
  SELinux attribution/summary models;
- `host` → `process_summary`;
- `process_file` → `process_file_summary`, `file_chart`, `files_tmp_v1`,
  `telemetry_event_summary`, and `attribution_quality_summary`;
- `process_conn_incr` → `process_net_conn`, `network_chart`,
  `telemetry_event_summary`, `attribution_quality_summary`, and its not-null test;
- `process_net_conn` → `process_net_summary` and `attribution_quality_summary`;
- `process_registry` → `process_registry_summary`;
- `process_image_load` → `process_image_load_summary` and `files_tmp_v1`; and
- `selinux_attribution` → SELinux event/detail and family summary models.

`process_summary` joins the per-family summaries back to the lifetime `process`
row by `pid_hash`; therefore an arbitrary lifetime name/path can affect multiple
downstream views even when the summary's own `os_pid` shortcut is invariant. The
entity path is a useful contrast: `process_entities.sql` uses `min(...)` plus
explicit conflict flags rather than `any_value`, and its metadata-conflict pattern
should inform the new contract tests.

Existing tests provide useful starting points but do not close this audit:

- `test_compacted_inputs.py` already proves the current process model depends on
  input row order for `process_path` and labels that behavior diagnostic;
- `test_process_gold_quality_sql.py` covers deterministic latest-name behavior in
  the file/network gold paths and counter conservation, but does not audit every
  retained `os_pid` shortcut;
- `test_selinux_sql.py` already verifies that ambiguous temporal candidates produce
  null attribution; and
- `test_compacted_s3_migration.py` identifies the `any_value` model closure for
  migration diagnostics, not semantic correctness.

The fixture work should extend these focused tests rather than treat the current
order-dependence diagnostic or migration closure as a semantic approval.

## Regression fixture matrix

The next test slice should use small DuckDB relations and the exact grouping keys
from each model:

1. repeated identical non-null values return an equivalent value;
2. one non-null value plus nulls returns the non-null value where nulls are defined
   as ineligible;
3. all-null input returns the documented null result;
4. two distinct non-null values set a conflict diagnostic and do not assert a
   particular `any_value` result;
5. process name/path pairs from separate observations cannot be combined by the
   candidate deterministic projection;
6. failed exec targets are ineligible for a successful-image representative;
7. Refresh is eligible for current-state/as-of selection but does not rewrite birth
   identity or historical transition evidence; and
8. temporal SELinux ambiguity suppresses the attributed identity fields.

For each retained shortcut, the test should compare the shortcut result with a
deterministic eligible-row result and assert equivalence—not merely assert that the
query returns a non-null value. For each rejected shortcut, the test should show the
distinct candidates or ordering dependency that makes arbitrary selection unsafe.

### Read-only paired-row prototype — 2026-11-23

The finalized sanitized Linux capture was used for a read-only DuckDB prototype; no
production model, source data or historical data was changed. The candidate relation
filters to `Start`/`Refresh` rows and excludes `exec_attempt`, then ranks complete
rows by observation UTC, comparable monotonic time, receipt time and a stable value
tie-breaker. Selection precedence is latest valid Refresh, latest successful exec,
then an explicit eligible fallback. Name, path and arguments are taken together from
the selected row.

The prototype selected all 5,807 `PidHash` groups: 493 Refresh roles, 4,947
successful-exec roles and 367 fallback roles. It selected all 19 targeted cohorts
with exact policy/pair agreement, selected no failed attempt, and produced identical
results across ten randomized source-order runs. This is design qualification only;
production DBT still needs as-of, tie/ambiguity, non-image-field and regression-test
contracts.

### Production DBT implementation — 2026-11-23

The PyUtil silver process model now applies the qualified paired-row selector. It
excludes failed attempts, prefers latest valid Refresh, falls back to latest
successful exec, and takes changing image fields from one row. Observation-role and
timing fields are exposed for downstream QA. Nullable staging defaults preserve
compatibility with raw Parquet that predates the additive observation columns.

The focused suite passes **32 tests with one existing skip**, and the isolated
finalized capture DBT build passes **139/139** nodes. The explicit as-of relation is
deferred as a future follow-up. Remaining audit work covers ambiguity contracts,
non-image `any_value` classifications, legacy standard-view parity, and native
Windows qualification.

## Next audit actions

1. Expand the inventory table with exact normalized expressions and downstream
   consumers for every call.
2. Add the synthetic contract fixtures without changing production SQL.
3. Run the fixtures against both the DBT process models and the legacy standard-view
   path where the same contract exists.
4. Record which uses are invariant-safe, conflict-visible, or ordering-sensitive.
5. Only then propose the smallest SQL changes, retaining safe shortcuts and replacing
   only semantically unsafe uses.

## Verification status

The source inventory command reproduced the 73-match baseline. With explicit
approval, the stale PyUtil virtual environment was replaced using the locked
development dependencies. The new synthetic contract module is
`../Wintap-PyUtil/tests/test_any_value_contract_sql.py`.

Focused execution:

```text
uv run --locked --offline --no-sync --dev python -m pytest \
  tests/test_any_value_contract_sql.py \
  tests/test_process_gold_quality_sql.py \
  tests/test_selinux_sql.py \
  tests/test_compacted_inputs.py -q
31 passed, 1 skipped
```

The new six-case module passes independently. Black `--check` and Python bytecode
compilation also pass. The expanded contract collection contains 226 cases and the
full selected contract run passes **226/226**. The tests are synthetic/in-memory
only; no live dataset, collector, deployment, historical data, or production SQL
change was involved.

<!-- SYNTHESIS: preliminary classifications inferred from the pinned PyUtil SQL sources; fixture execution is still required. -->
