# HostActivity test inventory — first cut

Primary class: **contract**. Execution: **offline synthetic**, using temporary
local Parquet/JSON, in-memory DuckDB, fake S3 clients, and Streamlit controls.
No live collector, AWS profile, remote dataset, coordinator database, or opt-in
environment variable is required. This suite does not qualify sensor capture.

## Frozen slice (2026-11-22)

| File under `contract/` | Cases | Coverage and follow-up |
|---|---:|---|
| `test_host_activity.py` | 37 | Configuration, query/schema/metadata contracts; co-resident transport and UI controls. Split by behavior in a later iteration. |
| `test_partition_status.py` | 3 | Metadata presence/overlap contracts plus one chart control. |
| `test_status_source.py` | 19 | Advisory-export contracts plus three Streamlit UI controls. |
| **Total** | **59** | All existing assertions retained; filenames and test method names unchanged. |

The first cut relocates whole files rather than splitting assertions or sharing
fixtures at the same time. `contract/` is the primary classification, not a claim
that every case is a pure unit test. UI/transport separation remains follow-up.

## Commands

Run from the HostActivity project directory, using its own environment:

```bash
uv run --locked --offline --no-sync python -m unittest discover -s tests -t . -p 'test_*.py'
```

For an existing environment, `.venv/bin/python` can replace `uv run ... python`.
The former project-root command (`discover -s .`) still discovers the same cases.
Do not run project suites together in one interpreter: other apps and PyUtil may
also use a `tests` package and have different dependency environments.

Named module example after relocation:

```bash
.venv/bin/python -m unittest tests.contract.test_status_source
```

Do not retain forwarding copies at the old paths; they could duplicate discovery.
Record any future count change and preserve coverage/provenance before merging,
archiving, or deleting tests. Fresh real-dataset checks belong to an explicit
validation command, not this default synthetic suite.
