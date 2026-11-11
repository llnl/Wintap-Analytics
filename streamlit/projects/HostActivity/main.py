"""Standalone metadata-first host activity dashboard; launch with Streamlit."""
from __future__ import annotations

import datetime as dt
import time

import altair as alt
import pandas as pd
import streamlit as st

from file_metadata import aggregate_file_metadata
from queries import EVENT_LABELS, aggregate_family, inspect_family
from s3_source import (
    RAW_EVENT_TYPES,
    discover_files,
    discover_object_metadata,
    load_settings,
    open_connection,
    open_metadata_client,
    partition_hours,
)


UTC = dt.timezone.utc


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _refresh(query_mode, event_type):
    try:
        settings = load_settings()
    except ValueError as exc:
        st.session_state.pop("host_activity_snapshot", None)
        st.error(str(exc))
        return

    end = dt.datetime.now(UTC)
    start = end - dt.timedelta(hours=12)
    refresh_started = time.perf_counter()
    if event_type == "__all__":
        status_label = "all-family file metadata"
    else:
        status_label = EVENT_LABELS.get(event_type, event_type)
    status = st.status(f"Refreshing {status_label}", expanded=True)
    con = None
    metadata_client = None
    snapshot = {
        "settings_fingerprint": settings.fingerprint,
        "query_mode": query_mode,
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
        if query_mode == "File metadata":
            event_types = RAW_EVENT_TYPES if event_type == "__all__" else (event_type,)
            status.write("Listing S3 object metadata under the selected collect-time day/hour partitions…")
            metadata_client = open_metadata_client(settings)
            objects = discover_object_metadata(
                metadata_client, settings, start, end, event_types=event_types
            )
            snapshot["file_count"] = len(objects)
            status.write(f"Aggregating {len(objects):,} object names and sizes; Parquet contents are not read…")
            result = aggregate_file_metadata(objects, start, end)
            snapshot["metadata"] = {
                "listed_files": result.listed_files,
                "files_in_window": result.files_in_window,
                "total_size_bytes": result.total_size_bytes,
                "unparsed_files": result.unparsed_files,
                "unparsed_size_bytes": result.unparsed_size_bytes,
                "outside_window_files": result.outside_window_files,
                "outside_window_size_bytes": result.outside_window_size_bytes,
                "bucket_minutes": result.bucket_minutes,
                "host_count": result.host_count,
                "host_summary": [
                    {
                        "hostname": host["hostname"],
                        "file_count": host["file_count"],
                        "size_bytes": host["size_bytes"],
                        "latest_collect": _iso(host["latest_collect"]),
                    }
                    for host in result.host_summary
                ],
                "points": [
                    {
                        "bucket_utc": _iso(point["bucket_utc"]),
                        "hostname": point["hostname"],
                        "file_count": point["file_count"],
                        "size_bytes": point["size_bytes"],
                    }
                    for point in result.points
                ],
            }
        else:
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
        if metadata_client is not None:
            try:
                metadata_client.close()
            except Exception:
                if not snapshot["error"]:
                    snapshot["error"] = "Refresh finished, but the S3 metadata client could not be closed cleanly."
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


def _metadata_chart(points, selected_hosts, metric):
    points = [point for point in points if point["hostname"] in selected_hosts]
    if not points:
        st.info("No host-attributed file metadata is available for this selection.")
        return
    frame = pd.DataFrame(points)
    frame["bucket_utc"] = pd.to_datetime(frame["bucket_utc"], utc=True)
    if metric == "File size (MiB)":
        frame["metric_value"] = frame["size_bytes"] / (1024 * 1024)
        title = "S3 object size (MiB)"
    else:
        frame["metric_value"] = frame["file_count"]
        title = "Parquet object count"
    chart = (
        alt.Chart(frame)
        .mark_line(point=False)
        .encode(
            x=alt.X("bucket_utc:T", title="Filename collect time (UTC)"),
            y=alt.Y("metric_value:Q", title=title, scale=alt.Scale(zero=True)),
            color=alt.Color("hostname:N", title="Hostname"),
            tooltip=[
                alt.Tooltip("bucket_utc:T", title="Collect time (UTC)"),
                alt.Tooltip("hostname:N", title="Hostname"),
                alt.Tooltip("file_count:Q", title="Files", format=","),
                alt.Tooltip("size_bytes:Q", title="Size (bytes)", format=","),
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)


def _render_file_metadata(metadata, host_selector):
    cols = st.columns(4)
    cols[0].metric("Files in collect-time window", f"{metadata['files_in_window']:,}")
    cols[1].metric("Total object size", f"{metadata['total_size_bytes'] / (1024 * 1024):,.1f} MiB")
    cols[2].metric("Hosts seen", f"{metadata['host_count']:,}")
    cols[3].metric("Unparsed filenames", f"{metadata['unparsed_files']:,}")

    if metadata["unparsed_files"]:
        st.warning(
            f"{metadata['unparsed_files']:,} listed objects ({metadata['unparsed_size_bytes']:,} bytes) "
            "did not match hostname+event_type+FILETIME.parquet and are excluded from the time series."
        )
    if metadata["outside_window_files"]:
        st.caption(
            f"{metadata['outside_window_files']:,} well-formed listed objects had collect times outside "
            "the exact filename collect-time window and are excluded from these totals."
        )

    summary = metadata["host_summary"]
    points = metadata["points"]
    if not points:
        st.info("No parseable, host-attributed file metadata fell in this exact collect-time interval.")
        return

    host_names = [host["hostname"] for host in summary]
    selected_hosts = host_selector.multiselect("Hosts", host_names, default=host_names)
    st.caption(
        f"Filename FILETIME is the collect-time basis; S3 LastModified/upload time is ignored. "
        f"Bucket width: {metadata['bucket_minutes']} minutes. S3 object sizes are reported in MiB (1 MiB = 1,048,576 bytes)."
    )
    visible_summary = [host for host in summary if host["hostname"] in selected_hosts]
    summary_frame = pd.DataFrame([
        {
            "Hostname": host["hostname"],
            "Files": host["file_count"],
            "Total size (MiB)": host["size_bytes"] / (1024 * 1024),
            "Latest collect time (UTC)": host["latest_collect"],
        }
        for host in visible_summary
    ])
    st.dataframe(summary_frame, hide_index=True, use_container_width=True)
    if not selected_hosts:
        st.info("Select one or more hosts to display a time series.")
    else:
        st.subheader("File count by collect time")
        _metadata_chart(points, selected_hosts, "File count")
        st.subheader("S3 object size by collect time (MiB)")
        _metadata_chart(points, selected_hosts, "File size (MiB)")


def main():
    st.set_page_config(page_title="Recent Host Activity", page_icon="📈", layout="wide")
    st.title("Recent Host Activity")
    st.caption("S3 bronze raw_sensor • read-only • metadata mode lists object keys and sizes; it does not read Parquet contents")

    try:
        settings = load_settings()
        fingerprint = settings.fingerprint
    except ValueError as exc:
        fingerprint = None
        st.error(str(exc))

    with st.sidebar:
        st.subheader("Source")
        st.caption("Uses DBT dataset/AWS variables and the standard AWS credential chain.")
        query_mode = st.radio("Query mode", ("File metadata", "Raw Parquet rows"), index=0)
        family_names = {label: event for event, label in EVENT_LABELS.items()}
        family_labels = sorted(family_names)
        if query_mode == "File metadata":
            family_options = ["All event families", *family_labels]
            selected_label = st.selectbox("Event family", family_options, index=0)
            selected_event = "__all__" if selected_label == "All event families" else family_names[selected_label]
            st.caption("File metadata is grouped by host across the selected family set.")
        else:
            default_label = EVENT_LABELS.get("raw_process", family_labels[0])
            default_index = family_labels.index(default_label)
            selected_label = st.selectbox("Event family", family_labels, index=default_index)
            selected_event = family_names[selected_label]
        refresh = st.button("Refresh last 12 hours", type="primary", use_container_width=True)
        st.caption("Changing query/family selection does not access S3; click Refresh to load a new snapshot.")
        st.divider()
        host_selector = st.empty()
        if query_mode == "Raw Parquet rows":
            normalized = st.checkbox("Normalize each host to its own peak", value=False)
            log_scale = st.checkbox("Logarithmic absolute scale", value=False, disabled=normalized)
        else:
            normalized = False
            log_scale = False

    if refresh:
        _refresh(query_mode, selected_event)

    snapshot = st.session_state.get("host_activity_snapshot")
    if snapshot is None:
        if selected_event == "__all__":
            selection_text = "all event families"
        else:
            selection_text = EVENT_LABELS[selected_event]
        st.info(f"Select **Refresh last 12 hours** to load **{selection_text}** in **{query_mode}** mode.")
        return
    if fingerprint is None or snapshot["settings_fingerprint"] != fingerprint:
        st.warning("The source configuration changed since this snapshot. Refresh before viewing its results.")
        return
    if snapshot.get("query_mode") != query_mode or snapshot.get("event_type") != selected_event:
        st.info("This snapshot does not match the selected query/family. Click **Refresh last 12 hours** to load it.")
        return
    if snapshot.get("error"):
        st.error(snapshot["error"])
        return

    start = dt.datetime.fromisoformat(snapshot["start"])
    end = dt.datetime.fromisoformat(snapshot["end"])
    window_label = "Filename collect-time" if query_mode == "File metadata" else "Event-time"
    objects_label = "S3 objects listed" if query_mode == "File metadata" else "Parquet objects"
    st.caption(
        f"{window_label} window: {start:%Y-%m-%d %H:%M:%S UTC} – {end:%Y-%m-%d %H:%M:%S UTC}  •  "
        f"Refreshed: {dt.datetime.fromisoformat(snapshot['refreshed']):%Y-%m-%d %H:%M:%S UTC}  •  "
        f"{objects_label}: {snapshot['file_count']:,}  •  "
        f"Refresh: {snapshot.get('elapsed_seconds', 0):.1f}s"
    )
    if query_mode == "File metadata":
        st.caption(
            f"S3 metadata listing: {snapshot['partition_count']} overlapping UTC day/hour partitions; "
            "the filename FILETIME is then filtered to the exact rolling 12-hour interval."
        )
        if snapshot["file_count"] == 0:
            st.info("No Parquet objects were found for the selected family set in the relevant day/hour partitions.")
            return
        _render_file_metadata(snapshot["metadata"], host_selector)
        st.caption("Object presence/size is an availability signal, not a completeness or collector-health assertion.")
        return

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
