"""Standalone recent raw-row activity dashboard; launch with Streamlit."""
from __future__ import annotations

import datetime as dt
import time

import altair as alt
import pandas as pd
import streamlit as st

from queries import EVENT_LABELS, aggregate_family, inspect_family
from s3_source import discover_files, load_settings, open_connection, partition_hours


UTC = dt.timezone.utc


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _refresh(event_type):
    try:
        settings = load_settings()
    except ValueError as exc:
        st.session_state.pop("host_activity_snapshot", None)
        st.error(str(exc))
        return

    end = dt.datetime.now(UTC)
    start = end - dt.timedelta(hours=12)
    refresh_started = time.perf_counter()
    status = st.status(f"Refreshing {EVENT_LABELS.get(event_type, event_type)}", expanded=True)
    con = None
    snapshot = {
        "settings_fingerprint": settings.fingerprint,
        "event_type": event_type,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "refreshed": end.isoformat(),
        "partition_count": len(partition_hours(start, end)),
        "results": {},
        "skipped": {},
        "file_count": 0,
        "error": None,
    }
    try:
        status.write("Listing objects only under the selected event's overlapping day/hour partitions…")
        con = open_connection(settings)
        discovered = discover_files(con, settings, start, end, event_types=(event_type,))
        snapshot["file_count"] = sum(len(paths) for paths in discovered.values())
        for event_type, paths in discovered.items():
            try:
                status.write(f"Inspecting schemas for {len(paths):,} selected-family Parquet objects…")
                projection = inspect_family(con, event_type, paths)
                snapshot["timestamp_sources"] = [
                    {"column": column, "encoding": encoding}
                    for column, _column_type, _expression, encoding in projection.time_projections
                ]
                if event_type == "raw_process_file":
                    status.write("Exactly aggregating process-file rows into bounded host/time groups…")
                else:
                    status.write("Filtering exact event timestamps and aggregating rows…")
                result = aggregate_family(con, projection, paths, start, end)
            except ValueError as exc:
                snapshot["skipped"][event_type] = str(exc)
                continue
            snapshot["results"][event_type] = {
                "rows": result.rows,
                "rows_without_hostname": result.rows_without_hostname,
                "bucket_minutes": result.bucket_minutes,
                "host_count": result.host_count,
                "points": [
                    {
                        "bucket_utc": _iso(point["bucket_utc"]),
                        "hostname": point["hostname"],
                        "raw_rows": point["raw_rows"],
                    }
                    for point in result.points
                ],
            }
    except (RuntimeError, ValueError) as exc:
        # Source helper errors are intentionally sanitized; don't show raw driver
        # messages that can contain endpoints, signed URLs, or object names.
        snapshot["error"] = str(exc)
    except Exception:
        snapshot["error"] = "Refresh failed unexpectedly; no chart was produced. Check local app logs."
    finally:
        if con is not None:
            try:
                con.close()
            except Exception:
                if not snapshot["error"]:
                    snapshot["error"] = "Refresh finished, but the DuckDB connection could not be closed cleanly."
        snapshot["elapsed_seconds"] = round(time.perf_counter() - refresh_started, 1)
        if snapshot.get("error"):
            status.update(
                label=f"Refresh failed after {snapshot['elapsed_seconds']:.1f}s",
                state="error",
                expanded=False,
            )
        else:
            status.update(
                label=f"Refresh finished in {snapshot['elapsed_seconds']:.1f}s",
                state="complete",
                expanded=False,
            )
        st.session_state["host_activity_snapshot"] = snapshot


def _chart(result, selected_hosts, normalized, log_scale):
    from queries import chart_points

    points = chart_points(result, selected_hosts, normalized)
    if not points:
        st.info("No host-attributed rows are available for this selection.")
        return
    frame = pd.DataFrame(points)
    frame["bucket_utc"] = pd.to_datetime(frame["bucket_utc"], utc=True)
    value_column = "value" if normalized else "raw_rows"
    title = "Relative to each host's peak" if normalized else "Raw Parquet rows"
    chart = (
        alt.Chart(frame)
        .mark_line(point=False)
        .encode(
            x=alt.X("bucket_utc:T", title="Time (UTC)"),
            y=alt.Y(
                f"{value_column}:Q",
                title=title,
                scale=alt.Scale(type="log" if log_scale and not normalized else "linear", zero=False),
            ),
            color=alt.Color("hostname:N", title="Hostname"),
            tooltip=[
                alt.Tooltip("bucket_utc:T", title="Bucket (UTC)"),
                alt.Tooltip("hostname:N", title="Hostname"),
                alt.Tooltip(f"{value_column}:Q", title=title, format=".4g"),
                alt.Tooltip("raw_rows:Q", title="Raw rows", format=","),
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)


def main():
    st.set_page_config(page_title="Recent Host Activity", page_icon="📈", layout="wide")
    st.title("Recent Host Activity")
    st.caption("S3 bronze raw_sensor • read-only • raw Parquet row counts (not logical-event totals)")

    try:
        settings = load_settings()
        fingerprint = settings.fingerprint
    except ValueError as exc:
        fingerprint = None
        st.error(str(exc))

    with st.sidebar:
        st.subheader("Source")
        st.caption("Uses DBT dataset/AWS variables and the standard AWS credential chain.")
        family_names = {label: event for event, label in EVENT_LABELS.items()}
        family_labels = sorted(family_names)
        default_label = EVENT_LABELS.get("raw_process", family_labels[0])
        default_index = family_labels.index(default_label)
        selected_label = st.selectbox("Event family", family_labels, index=default_index)
        selected_event = family_names[selected_label]
        refresh = st.button("Refresh last 12 hours", type="primary", use_container_width=True)
        st.caption("Only this family is scanned. Changing the selection does not query S3; click Refresh to load it.")
        st.divider()
        host_selector = st.empty()
        normalized = st.checkbox("Normalize each host to its own peak", value=False)
        log_scale = st.checkbox("Logarithmic absolute scale", value=False, disabled=normalized)

    if refresh:
        _refresh(selected_event)

    snapshot = st.session_state.get("host_activity_snapshot")
    if snapshot is None:
        st.info(f"Select **Refresh last 12 hours** to query the selected **{EVENT_LABELS[selected_event]}** family.")
        return
    if fingerprint is None or snapshot["settings_fingerprint"] != fingerprint:
        st.warning("The source configuration changed since this snapshot. Refresh before viewing its results.")
        return
    if snapshot.get("event_type") != selected_event:
        st.info("This snapshot does not match the selected family. Click **Refresh last 12 hours** to load it.")
        return
    if snapshot.get("error"):
        st.error(snapshot["error"])
        return

    start = dt.datetime.fromisoformat(snapshot["start"])
    end = dt.datetime.fromisoformat(snapshot["end"])
    st.caption(
        f"Event-time window: {start:%Y-%m-%d %H:%M:%S UTC} – {end:%Y-%m-%d %H:%M:%S UTC}  •  "
        f"Refreshed: {dt.datetime.fromisoformat(snapshot['refreshed']):%Y-%m-%d %H:%M:%S UTC}  •  "
        f"Parquet objects: {snapshot['file_count']:,}  •  "
        f"Refresh: {snapshot.get('elapsed_seconds', 0):.1f}s"
    )
    st.caption(
        f"Coarse S3 scan: {snapshot['partition_count']} overlapping UTC day/hour partitions; "
        "event timestamps are then filtered to the exact rolling 12-hour interval."
    )
    timestamp_sources = snapshot.get("timestamp_sources", ())
    if timestamp_sources:
        source_text = " → ".join(
            f"{source['column']} ({source['encoding']})" for source in timestamp_sources
        )
        st.caption(f"Timestamp basis (priority order): {source_text}")
    if selected_event == "raw_process_file":
        st.caption(
            "Process-file rows are counted exactly in DuckDB (not sampled), with a 120-second query limit, "
            "1 GB memory/temp limits, and a 20,000 intermediate host/time-group limit."
        )
    if snapshot["file_count"] == 0:
        st.info("No Parquet objects were found for the selected family in the relevant day/hour partitions.")
        return

    results = snapshot["results"]
    skipped = snapshot["skipped"]
    if skipped:
        with st.expander("Family processing details", expanded=not results):
            for event_type, reason in sorted(skipped.items()):
                st.write(f"**{EVENT_LABELS.get(event_type, event_type)}** (`{event_type}`): {reason}")
    if not results:
        st.warning("No chart was produced for the selected family. See its processing details above.")
        return

    event_type = selected_event
    family = results.get(event_type)
    if family is None:
        st.warning("No chart was produced for the selected family. See its processing details above.")
        return
    if not family["points"]:
        if family["rows_without_hostname"]:
            st.info(
                f"No host-attributed series is available. {family['rows_without_hostname']:,} "
                "in-window rows had a missing or blank hostname."
            )
        else:
            st.info(
                "No rows with a usable event timestamp fell in this exact interval. "
                "This is not a zero-activity or completeness assertion."
            )
        return
    host_names = sorted({point["hostname"] for point in family["points"]})
    selected_hosts = host_selector.multiselect("Hosts", host_names, default=host_names)
    if normalized:
        st.caption("Relative values are each host's raw-row count divided by its own maximum; volume comparisons are intentionally removed.")
    else:
        st.caption("Y-axis: raw Parquet rows per time bucket. No rows are synthesized for gaps.")
    st.caption(
        f"Bucket width: {family['bucket_minutes']} minutes  •  "
        f"Hostnames: {family['host_count']:,}  •  "
        f"Host-attributed raw rows: {family['rows']:,}  •  "
        f"Rows with missing/blank hostname: {family['rows_without_hostname']:,} (not charted)"
    )

    if not selected_hosts:
        st.info("Select one or more hosts to display a time series.")
    else:
        from queries import FamilyResult

        result = FamilyResult(
            event_type=event_type,
            rows=family["rows"],
            rows_without_hostname=family["rows_without_hostname"],
            bucket_minutes=family["bucket_minutes"],
            host_count=family["host_count"],
            points=tuple(
                {
                    "bucket_utc": dt.datetime.fromisoformat(point["bucket_utc"]),
                    "hostname": point["hostname"],
                    "raw_rows": point["raw_rows"],
                }
                for point in family["points"]
            ),
        )
        _chart(result, selected_hosts, normalized, log_scale)

    st.caption("Missing partitions, late arrivals, and rows without usable timestamps are not interpreted as zero activity or collector health.")


if __name__ == "__main__":
    main()
