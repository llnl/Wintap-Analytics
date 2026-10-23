"""Run: streamlit run streamlit/projects/SmokeTests/main.py"""
import os

import duckdb
import streamlit as st

from queries import TESTS, evaluate_run, load_manifests, mark_overlaps, overview, prepare_data

ICONS = {"red": "🔴", "yellow": "🟡", "green": "🟢", "gray": "⚪"}

COMMANDS = {
    "telemetry-workload": "python3 devtools/telemetry_smoke_workload.py --output /home/user/qa/stimulus-$RUN --manifest /home/user/qa/manifests/$RUN.json",
    "process-capture": "python3 devtools/process_capture_smoke_test.py --data-root /var/log/lintap/data --timeout 600 --manifest /home/user/qa/manifests/$RUN.json",
    "file-capture": "python3 devtools/file_capture_smoke_test.py --data-root /var/log/lintap/data --file-dir /home/user/qa/files --timeout 600 --manifest /home/user/qa/manifests/$RUN.json",
    "network-capture": "python3 devtools/network_capture_smoke_test.py --data-root /var/log/lintap/data --timeout 600 --manifest /home/user/qa/manifests/$RUN.json",
    "clone-trace": "sudo python3 devtools/validate_clone_trace.py --object /usr/lib/lintap/tracers/clone_core_tracer.bpf.o --runner /native/clone-runner --workload /native/clone-helper --output /native/qa/trace-$RUN --manifest /native/qa/manifests/$RUN.json",
    "clone-pipeline": "sudo python3 devtools/validate_clone_pipeline.py --dll /native/app/Lintap.dll --workload /native/clone-helper --output /native/qa/pipeline-$RUN --manifest /native/qa/manifests/$RUN.json",
    "clone-package": "sudo /native/qa-venv/bin/python devtools/validate_clone_package.py --workload /native/clone-helper --output /native/qa/package-$RUN --manifest /native/qa/manifests/$RUN.json",
    "runtime-capabilities": "sudo /native/qa-venv/bin/python devtools/validate_runtime_capabilities.py --dll /native/app/Lintap.dll --output /native/qa/receipt-$RUN --manifest /native/qa/manifests/$RUN.json",
}


def main():
    st.set_page_config(page_title="Smoke test results", page_icon="🧪", layout="wide")
    st.title("Smoke test results")
    st.caption("Read-only analysis • portable run manifests • raw parquet • no test execution")
    with st.sidebar:
        data_root = st.text_input("Parquet root on this analysis machine", os.environ.get("WINTAP_DATA_ROOT", ""))
        manifest_root = st.text_input("Optional JSON manifest directory", "")
        uploads = st.file_uploader("Or upload completed smoke manifests", type="json", accept_multiple_files=True)
        unlabelled_host = st.text_input("Host for unlabelled direct-parquet files", "",
                                      help="Only set if every unlabelled parquet file under the selected root belongs to this test host. Never the analysis-machine hostname.")
        padding = st.number_input("Time-window tolerance (seconds)", 0, 120, 15)
        row_limit = st.number_input("Displayed rows per case", 10, 10000, 200)
        st.button("Refresh files / results")
    runs, errors = load_manifests(manifest_root, [(f.name, f.getvalue()) for f in uploads or []], data_root=data_root)
    for error in errors:
        st.warning(error)
    st.info("Smoke evidence is discovered automatically in raw_sensor/raw_smoke_test alongside telemetry. JSON upload is optional. Normal transfer latency is expected; missing observations stay yellow, not PASS. VM selector paths are event values, not analysis-local files.")
    con = duckdb.connect(":memory:")
    con.execute("SET TimeZone='UTC'")
    available = False
    data_errors = []
    try:
        if data_root:
            count, data_errors, available = prepare_data(con, data_root, unlabelled_host)
            st.caption(f"{count} finalized parquet files discovered; active files are ignored.")
            for error in data_errors[:10]:
                st.warning(error)
            if available:
                unlabelled = con.execute("SELECT count(*) FROM smoke_data WHERE host IS NULL").fetchone()[0]
                if unlabelled:
                    st.warning(f"{unlabelled:,} rows have no hostname and cannot be attributed. Scope the source root to one host and set its name in the sidebar if appropriate.")
        evaluations = {(r["test"], r["runId"]): evaluate_run(con, r, available, padding) for r in runs}
        mark_overlaps(runs, evaluations, padding)
        if data_errors or errors:
            for evaluation in evaluations.values():
                evaluation["reasons"].append("Some dataset/evidence files could not be read; refresh after transfer")
                if evaluation["state"] == "green":
                    evaluation["state"] = "yellow"
        with st.sidebar:
            host_choices = sorted({r["host"]["hostname"].lower() for r in runs})
            selected_hosts = st.multiselect("Test hosts", host_choices, default=host_choices)
            history = st.checkbox("Show older runs in overview", value=False)
            interesting = st.checkbox("Only red/yellow overview rows", value=False)
        st.subheader("At a glance")
        st.caption("Green is scoped evidence, not platform certification. Yellow includes pending arrival, coverage gaps and ambiguity. Gray means no run supplied. The app cannot detect an entirely absent host without a run manifest.")
        visible_runs = [r for r in runs if r["host"]["hostname"].lower() in selected_hosts]
        summary_rows = overview(visible_runs, evaluations, selected_hosts, history) if selected_hosts else []
        counters = st.columns(4)
        for column, state in zip(counters, ICONS):
            column.metric(f"{ICONS[state]} {state.title()}", sum(row["state"] == state for row in summary_rows))
        displayed = [row for row in summary_rows if not interesting or row["state"] in ("red", "yellow")]
        if displayed:
            st.dataframe([dict(status=f"{ICONS[row['state']]} {row['state']}", host=row["host"], test=row["test"],
                               harness=row["harness"], coverage=row["coverage"], reason=row["reason"], run_id=row["run_id"]) for row in displayed], width="stretch")
            targets = [row for row in displayed if row["run_id"]]
            if targets:
                selected_target = st.selectbox("Inspect an overview result", range(len(targets)),
                                               format_func=lambda i: f"{ICONS[targets[i]['state']]} {targets[i]['host']} · {targets[i]['test']} · {targets[i]['run_id']}", key="overview-target")
                target = targets[selected_target]
                if st.button("Select this run in its section"):
                    st.session_state[target["test_key"]] = target["run_id"]
                st.markdown(f"[Jump to {target['test']}](#smoke-{target['test_key']})")
        else:
            st.caption("No overview results for the current filters.")
        for test, title in TESTS.items():
            st.header(title, anchor=f"smoke-{test}")
            with st.expander("How to run this smoke test", expanded=False):
                st.caption("On the Linux test host, from the Wintap repository. Choose a fresh run name.")
                st.code("RUN=$(date -u +%Y%m%dT%H%M%S)-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')\n" + COMMANDS[test] + " --smoke-data-root /var/log/lintap/data", language="bash")
                st.caption("Use a Python environment with duckdb installed for parquet export. --smoke-data-root contains raw_sensor; change it to your deployment's mounted/durable data root. WINTAP_DATA_ROOT also enables export. JSON remains a fallback; no uploader setup or source retention required.")
                if test == "network-capture":
                    st.warning("This existing test contacts public HTTP(S) and DNS endpoints. Obtain network approval; use the named loopback workload for offline testing.")
                if test in ("clone-trace", "clone-pipeline", "clone-package", "runtime-capabilities"):
                    st.caption("Requires native helper/app/tooling. App-starting harnesses must run sequentially on a designated idle test host; packaged acceptance starts/stops the service and temporarily changes Clone for opt-out.")
            choices = [r for r in visible_runs if r["test"] == test]
            if not choices:
                st.info("No smoke runs available. Run the command above; evidence arrives alongside telemetry, or optionally upload JSON.")
                continue
            by_id = {r["runId"]: r for r in choices}
            selected = st.selectbox("Test run", list(by_id), format_func=lambda key: f"{by_id[key]['host']['hostname']} · {by_id[key].get('startedAtUtc', '?')} · {key}", key=test)
            run = by_id[selected]
            evaluation = evaluations[(test, selected)]
            st.write(f"{ICONS[evaluation['state']]} **{evaluation['state'].title()}** — {evaluation['scope']}")
            for reason in evaluation["reasons"]:
                st.caption(reason)
            st.write(f"Harness result: **{run.get('status', 'unknown')}**" + (" (stimulus only, not capture validation)" if run.get("stimulusOnly") else ""))
            if run.get("error"):
                st.error(run["error"])
            with st.expander("Saved test report / portable manifest"):
                st.json(run)
            if not run["selectors"]:
                st.info("No stimulus selectors recorded; test may have failed before generating activity.")
            for case_result in evaluation["cases"]:
                selector = case_result["selector"]
                st.subheader(selector.get("case", selector["domain"]))
                if selector.get("skips"):
                    st.warning("Skipped stimulus: " + "; ".join(selector["skips"]))
                if test == "clone-trace":
                    st.caption("The saved actual-object report is the primary result. Parquet below is optional correlation only: the trace runner does not write sensor parquet.")
                if not available:
                    st.info("No collected parquet available. The saved run/report can still be inspected above.")
                    continue
                try:
                    if case_result["error"]:
                        raise ValueError(case_result["error"])
                    sql = case_result["sql"]
                    summary = case_result["summary"]
                    with st.expander("Tailored query"):
                        st.code(sql, language="sql")
                    if not summary:
                        if selector.get("threadIds") and not selector.get("pids"):
                            st.info("No process rows for the named thread TIDs. This is the expected negative observation only if companion process cases confirm collection was active; absence alone cannot prove thread filtering.")
                        else:
                            st.info("No matching collected events for this run/case yet. Check host, copied dataset, capture capabilities and flush/merge timing. This is not a passed test.")
                        continue
                    st.dataframe(summary, width="stretch")
                    # Coverage computed over the complete matching set, not the display limit.
                    result = con.execute(f"SELECT * FROM ({sql}) LIMIT {int(row_limit)}")
                    columns = [c[0] for c in result.description]
                    rows = [dict(zip(columns, row)) for row in result.fetchall()]
                    if selector["domain"] == "host":
                        for receipt in case_result.get("receipts", []):
                            st.dataframe([dict(sensor=name, status=sensor["status"], tier=sensor.get("tier")) for name, sensor in receipt.get("sensors", {}).items()], width="stretch")
                    else:
                        st.dataframe(case_result["checks"], width="stretch")
                    st.caption("Coverage indicators show observations, not full harness re-validation. Missing indicators may reflect hooks/filters/aggregation. Start row counts are not distinct-process counts.")
                    st.dataframe(rows[:int(row_limit)], width="stretch")
                    if case_result["rows"] > row_limit:
                        st.caption(f"Displaying {row_limit} of {case_result['rows']:,} matching rows.")
                except Exception as error:
                    st.warning(f"Cannot query this case: {error}")
    except Exception as error:
        st.error(f"Cannot read dataset: {error}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
