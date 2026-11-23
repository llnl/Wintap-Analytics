# SmokeTests contract test inventory

Primary class: **contract**. Execution is offline and synthetic, using temporary
local Parquet, in-memory DuckDB, mocked SDK objects and synthetic manifests/rows.
It requires the installed DuckDB/Boto3 dependencies but does not require
Streamlit, an AWS profile, a collector, a real dataset or network access, and it
does not qualify sensor capture.

## Classified slices (2026-11-22 through 2026-11-23)

| File under `contract/` | Cases | Coverage |
|---|---:|---|
| `test_analysis.py` | 22 | Canary-round analysis, runtime context, budgets, and local/fake-S3 summary persistence. |
| `test_durable.py` | 11 | Live-producer synthetic Parquet publication, manifest integrity, triage, and overlap contracts. |
| `test_pages.py` | 5 | Page working-set materialization, budgets, lifecycle requirements, and overlap behavior without Streamlit UI. |
| `test_queries.py` | 12 | Manifest loading, schema normalization, bounded selectors and endpoint evaluation. |
| `test_quality.py` | 22 | Adversarial file, process-lifecycle and network quality contracts. |
| `test_s3_source.py` | 13 | Config validation, mocked listings/connections, and transport-free local source parity. |
| **Total** | **85** | Whole files moved; only package/path imports changed. |

The remaining root-level files cover default-on, explicitly opt-out loopback HTTP
behavior and actual Streamlit app behavior. They are intentionally outside these
mechanical slices.

## Commands

Run from the SmokeTests project directory using a dedicated compatible environment:

```bash
python -m unittest discover -s tests -t . -p 'test_*.py' -v
```

The existing project-wide command, `python -m unittest discover -s . -p
'test_*.py' -v`, continues to include both this package and the untouched
root-level modules. Do not run app suites together in one interpreter: their
dependency environments and `tests` packages are independent.

Do not retain forwarding files at the former paths because project-root discovery
would collect duplicates. Record any future identity/count change before splitting,
merging, archiving or deleting cases. Real-data checks remain opt-in validation,
not part of this synthetic package.
