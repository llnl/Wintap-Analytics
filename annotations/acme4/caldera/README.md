# ACME4 Caldera Notes

This directory contains small utilities and notes for working with Caldera operation reports for ACME4. Consider this an initial proof of concept for leveraging Caldera Operation JSON Reports.

## Layout

- `load_data.py`: load Caldera `*.json` reports into DuckDB via `dlt`.
- `caldera_explorer.py`: Streamlit explorer for the DuckDB tables described by `caldera_report_schema.json`.
- `convert_caldera.py`: JSON report -> Markdown (+ graph image) generator.
- `generate_markdown.py`: simpler JSON report -> Markdown generator.
- `gen_reports.py`: older JSON report -> Markdown generator (kept for comparison).
- `caldera_report_schema.json`: expected table shape when loading into DuckDB.
- `caldera_report_common.py`: shared helpers used by the generators.
- `reports/`: generated markdown reports (and images).

## Running (uv)

From `annotations/acme4/`:

```sh
uv sync
uv run streamlit run caldera/caldera_explorer.py
uv run python caldera/convert_caldera.py /path/to/report.json
uv run python caldera/load_data.py /path/to/caldera/json/dir
```

# References
Homepage: https://caldera.mitre.org/
Documentation, etc: https://caldera.readthedocs.io/en/latest/
Blog: https://medium.com/@mitrecaldera/welcome-to-the-official-mitre-caldera-blog-page-f34c2cdfef09
Git repo: https://github.com/apache/caldera