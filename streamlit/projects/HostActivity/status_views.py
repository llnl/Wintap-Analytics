"""Advisory-only UI. Rendering and navigation never invoke producer commands."""

import datetime as dt
import os

from status_source import STALE_SECONDS, read_snapshot

ADVISORY_WARNING = (
    "Advisory status only — not permission to read, a shutdown proof, a "
    "completion certificate or authority to recover/reopen a dataset."
)
LIVE_WARNING = (
    "Live diagnostic — uncoordinated. Compaction or entity updates may be in "
    "progress. Observations can be partial, duplicated or mixed-generation; "
    "this is not a consistent snapshot or authoritative verification."
)


def render(view, st):
    st.subheader(view)
    st.warning(ADVISORY_WARNING)
    # Changing any pin/path invalidates cached summaries and their clock floor.
    # No source path, binding or raw producer diagnostic is rendered or persisted.
    config = tuple(
        os.environ.get(key, "")
        for key in (
            "WINTAP_STATUS_EXPORT",
            "WINTAP_STATUS_BINDING_SHA256",
            "WINTAP_STATUS_LEDGER_ID",
        )
    )
    if st.session_state.get("status_config") != config:
        st.session_state.pop("status_snapshot", None)
        st.session_state.pop("status_high_water", None)
        st.session_state["status_config"] = config
    if st.button("Refresh advisory status", type="primary"):
        snapshot = read_snapshot(high_water=st.session_state.get("status_high_water"))
        st.session_state["status_snapshot"] = snapshot
        if snapshot.observed_at is not None:
            st.session_state["status_high_water"] = snapshot.observed_at
    st.caption(
        "Manual local-export refresh only. No S3 calls, ledger opens, process-lock probe, grants or recovery actions."
    )
    snapshot = st.session_state.get("status_snapshot")
    if snapshot is None:
        st.info(
            "Refresh the configured advisory export. Unobserved state is unknown, not OPEN or empty."
        )
        return
    if snapshot.availability == "unavailable":
        st.error(snapshot.reason)
        return
    # Re-rendering an old cached result must not reset its age or observation.
    age = max(0, (dt.datetime.now(dt.timezone.utc) - snapshot.observed_at).total_seconds())
    st.caption(
        f"Producer observed: {snapshot.observed_at:%Y-%m-%d %H:%M:%S UTC} · "
        f"Retrieved: {snapshot.retrieved_at:%Y-%m-%d %H:%M:%S UTC} · Observation age: {age:.0f}s"
    )
    if age > STALE_SECONDS:
        st.warning(
            "Stale advisory observation (over 180s). This is not evidence of process death or permission to recover."
        )
    if view == "Status":
        state = snapshot.state
        st.write(f"Last reported mode: **{state['mode']}**")
        st.write(f"Reserved readers: **{state['readers']}** · Queued jobs: **{state['waiting']}**")
        st.caption(
            "Reserved is not delivered: grant-delivery status is unavailable in export v1. OPEN never authorizes access."
        )
        st.write(f"Scheduling cursor: `{state['next_hour']}`")
        st.write(f"Active raw/entity owner: `{state['active_run_id'] or 'not reported'}`")
        if state["block_reason_present"]:
            st.warning(
                "A producer block reason is present; its free-form text is withheld. Use the authorized operator workflow for diagnosis."
            )
        st.info(
            "Process-lock observation, snapshot sequence, progress/launch times, backlog denominator and entity disposition history: unavailable in export v1."
        )
        if snapshot.jobs:
            st.dataframe(list(snapshot.jobs), hide_index=True, width="stretch")
        else:
            st.caption("No jobs in this bounded exported page; not a complete history assertion.")
        if snapshot.has_more["jobs"]:
            st.warning(
                "More jobs exist beyond this exported page. This view does not open the ledger to fetch them."
            )
    elif view == "Runs":
        st.caption(
            "Raw-run intent markers, not measured execution bars. Data hours are separate from intent time; actual launch/finish and certificates are unavailable."
        )
        if snapshot.runs:
            st.dataframe(list(snapshot.runs), hide_index=True, width="stretch")
        else:
            st.info(
                "No raw runs in this bounded page. Entity-only history and unexported pages are unknown, not absent."
            )
        if snapshot.has_more["runs"]:
            st.warning("Incomplete history: more raw runs exist beyond this page.")
        st.caption(
            "COMPLETED is a reported ledger disposition only. FINISHED maintenance is not dataset completion or admission reopening."
        )
        if snapshot.maintenance:
            st.dataframe(list(snapshot.maintenance), hide_index=True, width="stretch")
        if snapshot.has_more["maintenance"]:
            st.warning("More maintenance records exist beyond this page.")
    else:
        st.info(
            "Partition catalog unavailable: export v1 contains no inventory. Unknown counts are not zero or verified deletion. No survey has run."
        )
        st.caption(
            "Raw inventory, compacted inventory, migration evidence, deletion evidence and entity coverage will remain separate axes when a qualified catalog interface is available."
        )
