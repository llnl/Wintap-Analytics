# SmokeTests test inventory

The `contract/` package is offline and synthetic, using temporary local Parquet,
in-memory DuckDB, mocked SDK objects and synthetic manifests/rows. It requires the
installed DuckDB/Boto3 dependencies but does not require Streamlit, an AWS profile,
a collector, a real dataset or network access, and it does not qualify sensor
capture. The separate `transport/` package uses only a loopback HTTP server and
synthetic objects. The `ui/` package exercises the real multipage application with
Streamlit AppTest and synthetic local fixtures.

## Classified slices (2026-11-22 through 2026-11-24)

| File under `contract/` | Cases | Coverage |
|---|---:|---|
| `test_analysis.py` | 22 | Canary-round analysis, runtime context, budgets, and local/fake-S3 summary persistence. |
| `test_durable.py` | 11 | Live-producer synthetic Parquet publication, manifest integrity, triage, and overlap contracts. |
| `test_pages.py` | 5 | Page working-set materialization, budgets, lifecycle requirements, and overlap behavior without Streamlit UI. |
| `test_queries.py` | 12 | Manifest loading, schema normalization, bounded selectors and endpoint evaluation. |
| `test_quality.py` | 22 | Adversarial file, process-lifecycle and network quality contracts. |
| `test_s3_source.py` | 14 | Config validation, hourly evidence/telemetry discovery, mocked connections, and transport-free local source parity. |
| **Total** | **86** | Classified contracts plus one hourly evidence-discovery regression. |

The test tree therefore contains 86 contract cases, one transport case, and 13 UI
cases. The additional UI case covers sanitized remote connection diagnostics; no
forwarding test modules remain at the former project-root paths.

## Commands

Run from the SmokeTests project directory using a dedicated compatible environment:

```bash
python -m unittest discover -s tests/contract -t . -p 'test_*.py' -v
```

Run the default-on loopback transport case separately with:

```bash
python -m unittest -v tests.transport.test_s3_http
```

Run the Streamlit UI package separately with:

```bash
python -m unittest -v tests.ui.test_app
```

Set `SMOKE_S3_HTTP_TEST=0` (or `false`, `no`, or `off`) to opt out. The existing
project-wide command, `python -m unittest discover -s . -p 'test_*.py' -v`,
continues to include the contract, transport, and UI packages. Do not run app
suites together in one interpreter: their dependency environments and `tests`
packages are independent.

Do not retain forwarding files at the former paths because project-root discovery
would collect duplicates. Record any future identity/count change before splitting,
merging, archiving or deleting cases. Real-data checks remain opt-in validation,
not part of this synthetic package.
