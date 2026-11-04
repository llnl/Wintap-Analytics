---
title: "Verification: SELinux DBT pipeline"
type: concept
confidence: high
grounded_by:
  - wiki/work/selinux-dbt-pipeline/implementation_plan.md
  - ../Wintap-PyUtil/Makefile
  - ../Wintap-PyUtil/wintap_dbt/macros/time.sql
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxavc/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxinteraction/
  - ../../../data/lintap-alpha/raw_sensor/raw_selinuxtransition/
policy: agent-editable
last_validated: 2026-11-04
repo_scope: cross-repo
implementation_area: data-pipeline
event_domain: cross-domain
audience: developer
status: reviewed
source_paths: ../Wintap-PyUtil/wintap_dbt; ../../../data/lintap-alpha/raw_sensor
tags: [feature-work, selinux, dbt, lintap, verification]
---

# Verification: SELinux DBT pipeline

## Planning baseline

Implementation and verification were run on the `feature/selinux-dbt-pipeline`
branch in `../Wintap-PyUtil`. No Wintap sensor files were changed.

## Build commands

Run from `../Wintap-PyUtil` with the supplied data root:

```bash
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-check-config
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-check-source
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-build
WINTAP_DATA_ROOT="$HOME/data/lintap-alpha" make dbt-test
```

## Required checks

- All three bronze, silver, and gold family relations exist for the supplied sample.
- A build with the three source directories absent still succeeds and returns typed empty relations.
- Raw-to-bronze row counts and duplicate counts are explained.
- Raw and gold `EventCount` sums are compared by family.
- Timestamp conversions preserve ordering and expected units.
- Blank context rates are reported by family and field.
- Exact, unique-temporal, ambiguous, and unmatched attribution counts are reported separately.
- Gold summary keys are unique at their declared grain.
- Interaction row counts are not presented as individual kernel-event counts.

## Results

### Supplied SELinux sample

All commands below use `WINTAP_DATA_ROOT="$HOME/data/lintap-alpha"` and the
20261104 day window.

```text
make dbt-build: PASS=137 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=137
make dbt-test:  PASS=83  WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=83
```

The build discovered 54 models and 82 data tests, and produced all three bronze,
silver, and gold SELinux family relations. The normalized sample counts are:

| Family | Raw rows | Normalized rows | Duplicate rows | Raw EventCount sum | Normalized/gold EventCount sum |
|---|---:|---:|---:|---:|---:|
| AVC | 3,382 | 3,382 | 0 | 3,382 | 3,382 |
| Interaction | 5,349,253 | 5,348,812 | 441 | 16,904,013,805 | 16,903,971,905 |
| Transition | 2,890 | 2,885 | 5 | 2,890 | 2,885 |

The raw-to-normalized reduction is duplicate removal. Consequently, gold sums
match silver sums exactly, while raw sums retain duplicate contributions. There
are 3 observed hosts and 163 distinct `(family, role, context, policy_epoch)`
rows in `selinux_context` (16 AVC, 115 interaction, and 32 transition rows).
The sample has no blank AVC contexts; interaction source blanks are 5 rows and
interaction target blanks are 2,307,508 rows. Transition context columns are not
represented in the common source/target context columns.

Attribution results are intentionally separated:

| Family | Exact | Unique temporal | Ambiguous | Unmatched |
|---|---:|---:|---:|---:|
| AVC | 0 | 1,328 | 0 | 2,054 |
| Interaction | 0 | 333,768 | 0 | 5,015,044 |
| Transition | 0 | 1,936 | 0 | 949 |

No exact or ambiguous rows occurred in this supplied sample; the models still
retain both statuses and the candidate count for future datasets. Gold summary
key checks found zero duplicate keys for AVC (762 rows), interaction (27,697
rows), and transition (2,885 rows).

### Optional-source behavior

The source-discovery check and full build were rerun with
`WINTAP_DATA_ROOT="$HOME/data/lintap-alpha-no-selinux"`, explicit
`WINTAP_DBT_START_DAY=20261104`, and `WINTAP_DBT_END_DAY=20261104`. The three
SELinux directories were absent; all typed empty branches compiled and the
normal build still completed with `PASS=137 WARN=0 ERROR=0`.

### Deviations and producer observations

- The interaction stream must not be interpreted as one kernel event per row;
  `EventCount` is the producer's folded/permission-expanded count.
- `EventTime` is whole-second serialized data derived from sub-second FILETIME,
  so timestamp ordering verification permits one second of lower-bound skew.
- Attribution is conservative. PID-only ownership was not used, and the absence
  of exact/ambiguous matches in this sample is reported rather than inferred as
  producer-side identity quality.
