"""Schema-aware raw-row projections and bounded DuckDB aggregations."""
from __future__ import annotations

import datetime as dt
import math
import threading
from dataclasses import dataclass


MAX_ROWS_PER_FAMILY = 2_000_000
MAX_CHART_POINTS = 1_000
MAX_PROCESS_ACTIVITY_CELLS = 20_000
MAX_AGGREGATE_GROUPS = 20_000
PROCESS_FILE_QUERY_TIMEOUT_SECONDS = 120
PROCESS_FILE_MEMORY_LIMIT = "1GB"
PROCESS_FILE_TEMP_LIMIT = "1GB"
BASE_BUCKET_MINUTES = 5
WINDOW_MINUTES = 12 * 60

# This is intentionally a small, best-effort screen for the experimental
# process-activity metric. It is not an authoritative service inventory and
# should be revised as more datasets are inspected.
PROCESS_ACTIVITY_EXCLUDED_NAMES = frozenset({
    "system", "systemd", "kthreadd", "bash", "sh", "dash", "zsh", "fish",
    "sed", "awk", "grep", "cat", "head", "tail", "cut", "tr", "sort", "uniq",
    "wc", "date", "uname", "dirname", "basename", "printf", "tee", "sleep",
    "timeout", "ps", "top", "vmstat", "iostat", "sar", "sadc", "mpstat",
    "pidstat", "free", "df", "du", "lsof", "netstat", "ss", "who", "w",
    "uptime", "hostname", "env", "id", "login", "su", "sudo", "sshd", "ssh",
    "crond", "cron", "dbus-daemon", "splunkd", "rpm", "urandom", "locale",
    "ksmtuned", "pgrep", "egrep", "ls", "ip", "dmesg", "ausearch", "column",
    "setroubleshootd", "ldconfig", "runc", "sa1",
})
PROCESS_ACTIVITY_EXCLUDED_PREFIXES = ("unknown", "kworker", "migration", "rcu_", "cpuhp")
PROCESS_NAME_COLUMNS = ("ProcessName", "process_name", "Name")
PROCESS_ACTIVITY_COLUMNS = ("ActivityType", "activity_type")
PROCESS_USER_COLUMNS = ("UserName", "Username", "User", "user_name")
PROCESS_ACTIVITY_EXCLUDED_USERS = frozenset({
    "na", "n/a", "unknown", "system", "root", "daemon", "nobody",
    "messagebus", "avahi", "dbus", "systemd", "local service", "network service",
})

# Candidate priority is intentional. `Computer` is an accepted hostname alias;
# no host identity is inferred from S3 paths.
HOST_COLUMNS = (
    "Hostname", "ComputerName", "Computer", "HostHame", "host_name",
)

# Prefer documented event-time names. Integer encodings are resolved by source
# family below; other names require a timestamp/date or parseable ISO string.
TIME_COLUMNS = (
    "EventTime", "event_time", "EventTimestamp", "event_timestamp",
    "Timestamp", "Time",
)
FILETIME_COLUMNS = {
    "eventtime", "event_time", "eventtimestamp", "event_timestamp",
    "firstseen", "lastseen", "firstseenms", "lastseenms",
}
UNIX_SECONDS_EVENT_TYPES = {
    "raw_host",
    "raw_process_file",
    "raw_process_conn_incr",
    "raw_selinuxavc",
    "raw_selinuxinteraction",
    "raw_selinuxtransition",
}
UNIX_EVENT_TIME_COLUMNS = {"eventtime", "event_time", "eventtimestamp", "event_timestamp"}
EVENT_TIME_COLUMN_PRIORITY = {
    "raw_process_file": ("FirstSeen", "LastSeen"),
    "raw_process_conn_incr": ("FirstSeenMs", "LastSeenMs"),
    "raw_selinuxavc": ("FirstSeen", "LastSeen"),
    "raw_selinuxinteraction": ("FirstSeen", "LastSeen"),
    "raw_selinuxtransition": ("FirstSeen", "LastSeen"),
}

EVENT_LABELS = {
    "raw_host": "Host",
    "raw_process": "Process",
    "raw_process_file": "Process file",
    "raw_process_conn_incr": "Process connection (incremental)",
    "raw_macip": "MAC/IP",
    "raw_macip_sensor": "MAC/IP sensor",
    "raw_process_registry": "Process registry",
    "raw_registry": "Registry",
    "raw_imageload": "Image load",
    "raw_image_load": "Image load (alternate source)",
    "raw_selinuxavc": "SELinux AVC",
    "raw_selinuxinteraction": "SELinux interaction",
    "raw_selinuxtransition": "SELinux transition",
    "pidstat": "pidstat",
}


@dataclass(frozen=True)
class FamilyProjection:
    event_type: str
    host_columns: tuple[str, ...]
    time_projections: tuple[tuple[str, str, str, str], ...]
    process_name_column: str | None = None
    activity_column: str | None = None
    user_name_column: str | None = None

    @property
    def host_column(self):
        return self.host_columns[0]

    @property
    def time_column(self):
        return self.time_projections[0][0]

    @property
    def time_type(self):
        return self.time_projections[0][1]

    @property
    def time_mode(self):
        return self.time_projections[0][3]

    @property
    def timestamp_expression(self):
        return "COALESCE(" + ", ".join(item[2] for item in self.time_projections) + ")"


@dataclass(frozen=True)
class FamilyResult:
    event_type: str
    rows: int
    rows_without_hostname: int
    bucket_minutes: int
    host_count: int
    points: tuple[dict, ...]
    process_activity_available: bool = False
    process_activity_points: tuple[dict, ...] = ()


def _identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _process_activity_expression(projection: FamilyProjection) -> str:
    """Return the screened process-name expression used by the experimental metric."""
    if projection.event_type != "raw_process":
        return "NULL::VARCHAR"
    if not projection.process_name_column or not projection.activity_column:
        return "NULL::VARCHAR"
    process_name = f"lower(trim(cast({_identifier(projection.process_name_column)} AS VARCHAR)))"
    activity = f"upper(trim(cast({_identifier(projection.activity_column)} AS VARCHAR)))"
    excluded = ", ".join("'" + name.replace("'", "''") + "'" for name in sorted(PROCESS_ACTIVITY_EXCLUDED_NAMES))
    prefixes = " OR ".join(
        "starts_with(" + process_name + ", '" + prefix.replace("'", "''") + "')"
        for prefix in PROCESS_ACTIVITY_EXCLUDED_PREFIXES
    )
    return (
        "CASE WHEN "
        f"{activity} = 'START' AND {process_name} IS NOT NULL AND {process_name} <> '' "
        f"AND {process_name} NOT IN ({excluded}) "
        f"AND NOT ends_with({process_name}, '.sh') "
        f"AND NOT ({prefixes}) "
        f"THEN {process_name} ELSE NULL END"
    )


def _process_activity_user_expression(projection: FamilyProjection) -> str:
    """Return the normalized, displayable user identity for Start events."""
    if projection.event_type != "raw_process":
        return "NULL::VARCHAR"
    if not projection.user_name_column or not projection.activity_column:
        return "NULL::VARCHAR"
    user_name = f"trim(cast({_identifier(projection.user_name_column)} AS VARCHAR))"
    activity = f"upper(trim(cast({_identifier(projection.activity_column)} AS VARCHAR)))"
    excluded = ", ".join("'" + name.replace("'", "''") + "'" for name in sorted(PROCESS_ACTIVITY_EXCLUDED_USERS))
    return (
        "CASE WHEN "
        f"{activity} = 'START' AND {user_name} IS NOT NULL AND {user_name} <> '' "
        f"AND lower({user_name}) NOT IN ({excluded}) "
        f"AND NOT ends_with({user_name}, '$') "
        f"THEN {user_name} ELSE NULL END"
    )


def _iso_timestamp_projection(ref: str) -> str:
    """Parse ISO strings while converting explicit offsets to UTC without pytz."""
    text = f"trim(cast({ref} AS VARCHAR))"
    zone_suffix = r"[+-][0-9]{2}:?[0-9]{2}$"
    zone_pattern = r"([+-])([0-9]{2}):?([0-9]{2})$"
    base = f"try_cast(regexp_replace({text}, '{zone_suffix}', '') AS TIMESTAMP)"
    sign = f"CASE WHEN regexp_extract({text}, '{zone_pattern}', 1) = '+' THEN 1 ELSE -1 END"
    offset = (
        f"(({sign}) * (try_cast(regexp_extract({text}, '{zone_pattern}', 2) AS INTEGER) * 60 "
        f"+ try_cast(regexp_extract({text}, '{zone_pattern}', 3) AS INTEGER)))"
    )
    offset_timestamp = f"({base} - ({offset}) * INTERVAL '1 minute')"
    zulu = f"try_cast(regexp_replace({text}, '[Zz]$', '') AS TIMESTAMP)"
    naive = f"try_cast({ref} AS TIMESTAMP)"
    return (
        f"CASE WHEN regexp_matches({text}, '[Zz]$') THEN {zulu} "
        f"WHEN regexp_matches({text}, '{zone_suffix}') THEN {offset_timestamp} "
        f"WHEN regexp_full_match({text}, '[+-]?[0-9]+') THEN NULL::TIMESTAMP "
        f"ELSE {naive} END"
    )


def _unix_seconds_projection(ref: str) -> str:
    seconds = f"try_cast({ref} AS DOUBLE)"
    micros = f"try_cast(({seconds}) * 1000000 AS BIGINT)"
    return f"try(make_timestamp({micros}))"


def _timestamp_projection(column: str, column_type: str, event_type: str) -> tuple[str, str | None]:
    """Return a UTC-naive TIMESTAMP expression and encoding mode, or reason."""
    ref = _identifier(column)
    normalized_type = column_type.strip().lower()
    if "timestamp with time zone" in normalized_type or normalized_type == "timestamptz":
        # epoch_us is absolute UTC; make_timestamp yields UTC-naive chart labels.
        return f"make_timestamp(epoch_us({ref}))", "timestamp_tz"
    if normalized_type.startswith("timestamp") or normalized_type == "date":
        return f"try_cast({ref} AS TIMESTAMP)", "timestamp"
    if normalized_type in {"varchar", "text", "string"}:
        name = column.casefold()
        if name in UNIX_EVENT_TIME_COLUMNS and event_type in UNIX_SECONDS_EVENT_TYPES:
            text = f"trim(cast({ref} AS VARCHAR))"
            numeric = f"regexp_full_match({text}, '[+-]?[0-9]+(?:\\.[0-9]+)?')"
            unix = _unix_seconds_projection(ref)
            iso = _iso_timestamp_projection(ref)
            return f"CASE WHEN {numeric} THEN {unix} ELSE {iso} END", "unix_seconds_or_iso_timestamp"
        if name in FILETIME_COLUMNS:
            # Numeric strings in EventTime have the same FILETIME contract as
            # integer EventTime; non-numeric strings are treated as ISO timestamps.
            integer = f"try_cast(trim(cast({ref} AS VARCHAR)) AS HUGEINT)"
            delta = f"(({integer}) - 116444736000000000)"
            micros = f"({delta} // 10 - CASE WHEN ({delta}) % 10 < 0 THEN 1 ELSE 0 END)"
            filetime = f"try(make_timestamp(try_cast({micros} AS BIGINT)))"
            iso = _iso_timestamp_projection(ref)
            return (
                f"CASE WHEN regexp_full_match(trim(cast({ref} AS VARCHAR)), '[+-]?[0-9]+') "
                f"THEN {filetime} ELSE {iso} END",
                "filetime_or_iso_timestamp",
            )
        # Never infer seconds/milliseconds/microseconds from a numeric-looking string.
        if column.casefold() in {"time", "timestamp"}:
            return _iso_timestamp_projection(ref), "iso_timestamp"
        return "", "Timestamp column has an unsupported string encoding"
    unix_numeric_types = {
        "tinyint", "smallint", "integer", "bigint", "hugeint",
        "utinyint", "usmallint", "uinteger", "ubigint", "float", "real", "double",
    }
    if (column.casefold() in UNIX_EVENT_TIME_COLUMNS
            and event_type in UNIX_SECONDS_EVENT_TYPES
            and normalized_type in unix_numeric_types):
        return _unix_seconds_projection(ref), "unix_seconds"
    if normalized_type in {"tinyint", "smallint", "integer", "bigint", "hugeint", "utinyint", "usmallint", "uinteger", "ubigint"}:
        if column.casefold() not in FILETIME_COLUMNS:
            return "", "Numeric time column is not a declared FILETIME field"
        integer = f"try_cast({ref} AS HUGEINT)"
        delta = f"(({integer}) - 116444736000000000)"
        micros = f"({delta} // 10 - CASE WHEN ({delta}) % 10 < 0 THEN 1 ELSE 0 END)"
        return f"try(make_timestamp(try_cast({micros} AS BIGINT)))", "filetime"
    return "", f"Unsupported event-time column type: {column_type}"


def inspect_family(con, event_type: str, paths) -> FamilyProjection:
    """Inspect unioned Parquet schema and select a documented host/time pair."""
    try:
        schema = con.execute(
            "DESCRIBE SELECT * FROM read_parquet(?, union_by_name=true, hive_partitioning=false)",
            [list(paths)],
        ).fetchall()
    except Exception:
        raise ValueError("Parquet schema could not be inspected") from None

    columns = {}
    for name, column_type, *_ in schema:
        key = str(name).casefold()
        if key in columns:
            raise ValueError("Schema contains case-colliding column names")
        columns[key] = (str(name), str(column_type))

    host_columns = tuple(dict.fromkeys(
        columns[name.casefold()][0]
        for name in HOST_COLUMNS
        if name.casefold() in columns
    ))
    if not host_columns:
        raise ValueError("No supported row-level hostname column")

    time_projections = []
    time_reasons = []
    candidates = tuple(dict.fromkeys(EVENT_TIME_COLUMN_PRIORITY.get(event_type, ()) + TIME_COLUMNS))
    for candidate in candidates:
        found = columns.get(candidate.casefold())
        if found is None:
            continue
        expression, mode_or_reason = _timestamp_projection(found[0], found[1], event_type)
        if not expression:
            time_reasons.append(mode_or_reason)
            continue
        time_projections.append((found[0], found[1], expression, mode_or_reason))
    if time_projections:
        process_name_column = None
        activity_column = None
        if event_type == "raw_process":
            process_name_column = next(
                (columns[name.casefold()][0] for name in PROCESS_NAME_COLUMNS if name.casefold() in columns),
                None,
            )
            activity_column = next(
                (columns[name.casefold()][0] for name in PROCESS_ACTIVITY_COLUMNS if name.casefold() in columns),
                None,
            )
            user_name_column = next(
                (columns[name.casefold()][0] for name in PROCESS_USER_COLUMNS if name.casefold() in columns),
                None,
            )
        else:
            user_name_column = None
        return FamilyProjection(
            event_type,
            host_columns,
            tuple(time_projections),
            process_name_column,
            activity_column,
            user_name_column,
        )
    if time_reasons:
        raise ValueError(time_reasons[0])
    raise ValueError("No supported row-level event-time column")


def choose_bucket_minutes(
    host_count: int,
    point_budget: int = MAX_CHART_POINTS,
    window_minutes: int = WINDOW_MINUTES,
) -> int:
    """Keep a full-window host-by-bucket chart under a fixed point budget."""
    if host_count <= 0:
        return BASE_BUCKET_MINUTES
    if point_budget < 1:
        raise ValueError("Point budget must be positive")
    if window_minutes < 1:
        raise ValueError("Window duration must be positive")
    if host_count > point_budget:
        raise ValueError(f"Chart point budget is too small for {host_count:,} hosts; no chart was produced")
    width = BASE_BUCKET_MINUTES
    while host_count * math.ceil(window_minutes / width) > point_budget:
        width = min(width * 2, window_minutes)
    return width


def zero_fill_time_buckets(
    points,
    hostnames,
    start: dt.datetime,
    end: dt.datetime,
    bucket_minutes: int,
    value_fields,
    point_budget: int = MAX_CHART_POINTS,
):
    """Add zero-valued points for every missing host/bucket in the selected window."""
    if end <= start:
        raise ValueError("Window end must be after window start")
    if bucket_minutes < 1:
        raise ValueError("Bucket width must be positive")
    if point_budget < 1:
        raise ValueError("Point budget must be positive")
    hosts = tuple(sorted(set(hostnames)))
    fields = tuple(value_fields)
    if not hosts:
        return ()
    bucket_count = math.ceil((end - start).total_seconds() / (bucket_minutes * 60))
    if len(hosts) * bucket_count > point_budget:
        raise ValueError(f"Chart point budget exceeded ({point_budget:,} points); no chart was produced")

    existing = {
        (point["bucket_utc"], point["hostname"]): point
        for point in points
    }
    filled = []
    for bucket_index in range(bucket_count):
        bucket = start + dt.timedelta(minutes=bucket_index * bucket_minutes)
        if bucket >= end:
            break
        for hostname in hosts:
            point = existing.get((bucket, hostname))
            if point is None:
                point = {"bucket_utc": bucket, "hostname": hostname}
                point.update({field: 0 for field in fields})
            filled.append(point)
    return tuple(filled)


def _execute_with_timeout(con, sql: str, params, timeout_seconds: float):
    timed_out = threading.Event()
    finished = threading.Event()

    def interrupt_query():
        if finished.is_set():
            return
        timed_out.set()
        try:
            con.interrupt()
        except Exception:
            # The execute path below reports a sanitized timeout if the query is
            # still running; interruption errors must not expose driver details.
            pass

    timer = threading.Timer(timeout_seconds, interrupt_query)
    timer.daemon = True
    timer.start()
    try:
        rows = con.execute(sql, params).fetchall()
    except Exception:
        if timed_out.is_set():
            raise ValueError(
                f"Exact aggregation exceeded its {timeout_seconds:g}-second time budget; no chart was produced"
            ) from None
        raise ValueError(
            "Exact aggregation could not complete within its memory, temporary-storage, or read limits; "
            "no chart was produced"
        ) from None
    finally:
        finished.set()
        timer.cancel()
        timer.join()
    if timed_out.is_set():
        raise ValueError(
            f"Exact aggregation exceeded its {timeout_seconds:g}-second time budget; no chart was produced"
        )
    return rows


def _aggregate_process_file(
    con,
    projection: FamilyProjection,
    paths,
    start_utc: dt.datetime,
    end_utc: dt.datetime,
    *,
    point_budget: int,
    max_intermediate_groups: int,
    query_timeout_seconds: float,
    window_minutes: int,
) -> FamilyResult:
    """Aggregate every matching process-file row without materializing raw rows."""
    if (not isinstance(max_intermediate_groups, int) or isinstance(max_intermediate_groups, bool)
            or not 1 <= max_intermediate_groups <= MAX_AGGREGATE_GROUPS):
        raise ValueError(f"Intermediate group budget must be between 1 and {MAX_AGGREGATE_GROUPS:,}")
    if (not isinstance(query_timeout_seconds, (int, float)) or isinstance(query_timeout_seconds, bool)
            or not math.isfinite(query_timeout_seconds)
            or not 0 < query_timeout_seconds <= PROCESS_FILE_QUERY_TIMEOUT_SECONDS):
        raise ValueError(
            f"Aggregate query time budget must be between 0 and {PROCESS_FILE_QUERY_TIMEOUT_SECONDS} seconds"
        )

    host_values = [
        f"nullif(trim(cast({_identifier(column)} AS VARCHAR)), '')"
        for column in projection.host_columns
    ]
    host_expr = "COALESCE(" + ", ".join(host_values) + ")"
    time_expr = projection.timestamp_expression
    base_minutes = BASE_BUCKET_MINUTES
    sql = (
        "WITH grouped AS MATERIALIZED ("
        f"SELECT {host_expr} AS hostname, "
        f"time_bucket(INTERVAL '{base_minutes} minutes', {time_expr}, CAST(? AS TIMESTAMP)) AS bucket_utc, "
        "count(*) AS raw_rows "
        "FROM read_parquet(?, union_by_name=true, hive_partitioning=false) "
        f"WHERE {time_expr} >= CAST(? AS TIMESTAMP) AND {time_expr} < CAST(? AS TIMESTAMP) "
        "GROUP BY hostname, bucket_utc), "
        "stats AS ("
        "SELECT coalesce(sum(raw_rows), 0) AS row_count, "
        "count(DISTINCT hostname) FILTER (WHERE hostname IS NOT NULL) AS host_count, "
        "coalesce(sum(raw_rows) FILTER (WHERE hostname IS NULL), 0) AS null_host_count, "
        "count(*) AS group_count FROM grouped) "
        "SELECT stats.row_count, stats.host_count, stats.null_host_count, stats.group_count, "
        "grouped.bucket_utc, grouped.hostname, grouped.raw_rows "
        "FROM stats LEFT JOIN grouped ON true LIMIT ?"
    )

    try:
        # Bound both DuckDB's in-memory working set and any external aggregation
        # spill. The in-memory connection is closed after this selected-family
        # refresh, which also releases temporary spill files.
        con.execute(f"SET memory_limit='{PROCESS_FILE_MEMORY_LIMIT}'")
        con.execute(f"SET max_temp_directory_size='{PROCESS_FILE_TEMP_LIMIT}'")
    except Exception:
        raise ValueError("DuckDB could not apply the process-file resource limits; no chart was produced") from None

    rows = _execute_with_timeout(
        con,
        sql,
        [start_utc, list(paths), start_utc, end_utc, max_intermediate_groups + 1],
        query_timeout_seconds,
    )
    if not rows:
        raise ValueError("Exact aggregation returned no summary; no chart was produced")

    row_count, host_count, null_host_count, group_count = map(int, rows[0][:4])
    if group_count > max_intermediate_groups:
        raise ValueError(
            f"Intermediate host/time group budget exceeded ({max_intermediate_groups:,} groups); "
            "no chart was produced"
        )

    bucket_minutes = choose_bucket_minutes(host_count, point_budget, window_minutes)
    start_utc = start_utc.replace(tzinfo=None)
    point_counts = {}
    for row in rows:
        bucket_utc, hostname, raw_rows = row[4:]
        if bucket_utc is None or hostname is None:
            continue
        if bucket_minutes != base_minutes:
            elapsed_minutes = (bucket_utc - start_utc).total_seconds() / 60
            offset = math.floor(elapsed_minutes / bucket_minutes) * bucket_minutes
            bucket_utc = start_utc + dt.timedelta(minutes=offset)
        key = (bucket_utc, str(hostname))
        point_counts[key] = point_counts.get(key, 0) + int(raw_rows)

    if len(point_counts) > point_budget:
        raise ValueError(f"Chart point budget exceeded ({point_budget:,} points); no chart was produced")

    points = zero_fill_time_buckets(
        (
            {"bucket_utc": bucket, "hostname": hostname, "raw_rows": count}
            for (bucket, hostname), count in point_counts.items()
        ),
        (hostname for _, hostname in point_counts),
        start_utc,
        end_utc,
        bucket_minutes,
        ("raw_rows",),
        point_budget,
    )
    return FamilyResult(
        projection.event_type,
        row_count - null_host_count,
        null_host_count,
        bucket_minutes,
        host_count,
        points,
    )


def aggregate_family(
    con,
    projection: FamilyProjection,
    paths,
    start: dt.datetime,
    end: dt.datetime,
    *,
    max_rows: int = MAX_ROWS_PER_FAMILY,
    point_budget: int = MAX_CHART_POINTS,
    max_intermediate_groups: int = MAX_AGGREGATE_GROUPS,
    query_timeout_seconds: float = PROCESS_FILE_QUERY_TIMEOUT_SECONDS,
) -> FamilyResult:
    """Count selected-family rows exactly in [start,end), using bounded aggregation."""
    if start.tzinfo is None or end.tzinfo is None or end <= start:
        raise ValueError("Aggregation window must be an increasing timezone-aware interval")
    if max_rows < 1:
        raise ValueError("Row budget must be positive")
    if point_budget < 1:
        raise ValueError("Point budget must be positive")

    host_values = [
        f"nullif(trim(cast({_identifier(column)} AS VARCHAR)), '')"
        for column in projection.host_columns
    ]
    host_expr = "COALESCE(" + ", ".join(host_values) + ")"
    time_expr = projection.timestamp_expression
    start_utc = start.astimezone(dt.timezone.utc).replace(tzinfo=None)
    end_utc = end.astimezone(dt.timezone.utc).replace(tzinfo=None)
    window_minutes = max(1, math.ceil((end_utc - start_utc).total_seconds() / 60))
    if projection.event_type == "raw_process_file":
        # This family uses the exact grouped-result budget rather than the
        # general raw-row cap; the remaining resource guards are family-specific.
        return _aggregate_process_file(
            con,
            projection,
            paths,
            start_utc,
            end_utc,
            point_budget=point_budget,
            max_intermediate_groups=max_intermediate_groups,
            query_timeout_seconds=query_timeout_seconds,
            window_minutes=window_minutes,
        )

    process_expr = _process_activity_expression(projection)
    user_expr = _process_activity_user_expression(projection)
    aggregate_process_activity = (
        projection.event_type == "raw_process"
        and projection.process_name_column is not None
        and projection.activity_column is not None
        and projection.user_name_column is not None
    )
    process_activity_point_budget = (
        MAX_PROCESS_ACTIVITY_CELLS if aggregate_process_activity else point_budget
    )
    bounded_limit = "" if aggregate_process_activity else "LIMIT ?"
    bucket_cases = []
    width = BASE_BUCKET_MINUTES
    while True:
        bucket_cases.append(
            f"WHEN host_count * {math.ceil(window_minutes / width)} <= ? THEN {width}"
        )
        if width == window_minutes:
            break
        width = min(width * 2, window_minutes)
    bucket_case = "CASE " + " ".join(bucket_cases) + " ELSE " + str(window_minutes) + " END"
    sql = (
        "WITH bounded AS MATERIALIZED ("
        f"SELECT {host_expr} AS hostname, {time_expr} AS event_ts, {process_expr} AS process_name, "
        f"{user_expr} AS user_name "
        "FROM read_parquet(?, union_by_name=true, hive_partitioning=false) "
        f"WHERE {time_expr} >= CAST(? AS TIMESTAMP) AND {time_expr} < CAST(? AS TIMESTAMP) "
        f"{bounded_limit}), "
        "stats AS (SELECT count(*) AS row_count, count(DISTINCT hostname) AS host_count, "
        "count(*) FILTER (WHERE hostname IS NULL) AS null_host_count FROM bounded), "
        f"params AS (SELECT *, {bucket_case} AS bucket_minutes FROM stats), "
        "raw_grouped AS (SELECT time_bucket(INTERVAL (params.bucket_minutes) MINUTE, bounded.event_ts, "
        "CAST(? AS TIMESTAMP)) AS bucket_utc, bounded.hostname, count(*) AS raw_rows "
        "FROM bounded CROSS JOIN params "
        "WHERE bounded.hostname IS NOT NULL AND params.host_count <= ? "
        "GROUP BY bucket_utc, bounded.hostname), "
        "activity_grouped AS (SELECT time_bucket(INTERVAL '15 minutes', bounded.event_ts, "
        "TIMESTAMP '2000-01-03 00:00:00') AS bucket_utc, "
        "bounded.hostname, bounded.user_name, count(DISTINCT bounded.process_name) AS process_type_count "
        "FROM bounded CROSS JOIN params "
        "WHERE bounded.hostname IS NOT NULL AND bounded.user_name IS NOT NULL "
        "AND bounded.process_name IS NOT NULL "
        "GROUP BY bucket_utc, bounded.hostname, bounded.user_name), "
        "activity_bounds AS (SELECT time_bucket(INTERVAL '15 minutes', CAST(? AS TIMESTAMP), "
        "TIMESTAMP '2000-01-03 00:00:00') AS start_bucket, "
        "time_bucket(INTERVAL '15 minutes', CAST(? AS TIMESTAMP) - INTERVAL '1 microsecond', "
        "TIMESTAMP '2000-01-03 00:00:00') AS end_bucket), "
        "activity_buckets AS (SELECT series.bucket_utc FROM activity_bounds, "
        "generate_series(activity_bounds.start_bucket, activity_bounds.end_bucket, "
        "INTERVAL '15 minutes') AS series(bucket_utc)), "
        "activity_pairs AS (SELECT DISTINCT bounded.hostname, bounded.user_name FROM bounded "
        "WHERE bounded.hostname IS NOT NULL AND bounded.user_name IS NOT NULL), "
        "activity_limits AS (SELECT count(*) AS pair_count, "
        "(SELECT count(*) FROM activity_buckets) AS bucket_count FROM activity_pairs), "
        "activity_grid AS (SELECT activity_pairs.hostname, activity_pairs.user_name, "
        "activity_buckets.bucket_utc FROM activity_pairs CROSS JOIN activity_buckets "
        "CROSS JOIN activity_limits WHERE activity_limits.pair_count * activity_limits.bucket_count <= ?), "
        "activity_filled AS (SELECT activity_grid.bucket_utc, activity_grid.hostname, "
        "activity_grid.user_name, coalesce(activity_grouped.process_type_count, 0)::BIGINT AS process_type_count "
        "FROM activity_grid LEFT JOIN activity_grouped USING (bucket_utc, hostname, user_name)), "
        "raw_output AS (SELECT params.row_count, params.host_count, params.null_host_count, params.bucket_minutes, "
        "'raw' AS metric_kind, raw_grouped.bucket_utc, raw_grouped.hostname, raw_grouped.raw_rows, "
        "NULL::BIGINT AS process_type_count, NULL::VARCHAR AS user_name "
        "FROM params LEFT JOIN raw_grouped ON true), "
        "activity_output AS (SELECT params.row_count, params.host_count, params.null_host_count, params.bucket_minutes, "
        "'activity' AS metric_kind, activity_filled.bucket_utc, activity_filled.hostname, "
        "NULL::BIGINT AS raw_rows, activity_filled.process_type_count, activity_filled.user_name "
        "FROM params CROSS JOIN activity_filled) "
        "SELECT * FROM raw_output UNION ALL SELECT * FROM activity_output "
        "ORDER BY metric_kind, bucket_utc, hostname"
    )
    params = [list(paths), start_utc, end_utc]
    if not aggregate_process_activity:
        params.append(max_rows + 1)
    params += (
        [point_budget] * len(bucket_cases)
        + [
            start_utc,
            point_budget,
            start_utc,
            end_utc,
            process_activity_point_budget,
        ]
    )
    try:
        if aggregate_process_activity:
            con.execute(f"SET memory_limit='{PROCESS_FILE_MEMORY_LIMIT}'")
            con.execute(f"SET max_temp_directory_size='{PROCESS_FILE_TEMP_LIMIT}'")
            rows = _execute_with_timeout(con, sql, params, PROCESS_FILE_QUERY_TIMEOUT_SECONDS)
        else:
            rows = con.execute(sql, params).fetchall()
    except ValueError:
        raise
    except Exception:
        raise ValueError("Parquet rows could not be read or aggregated") from None
    row_count, host_count, rows_without_hostname, bucket_minutes = map(int, rows[0][:4])
    row_budget_exceeded = row_count > max_rows
    if row_budget_exceeded and not aggregate_process_activity:
        raise ValueError(f"Raw-row budget exceeded ({max_rows:,} rows); no chart was produced")
    if row_budget_exceeded:
        grouped_rows = ()
        points = ()
    else:
        # Preserve the same fail-closed host-count rule as choose_bucket_minutes.
        choose_bucket_minutes(host_count, point_budget, window_minutes)
        grouped_rows = [row for row in rows if row[4] == "raw" and row[5] is not None]
        if len(grouped_rows) > point_budget:
            # Guard sparse data whose actual groups exceed the full-window estimate.
            raise ValueError(f"Chart point budget exceeded ({point_budget:,} points); no chart was produced")

        points = zero_fill_time_buckets(
            (
                {"bucket_utc": row[5], "hostname": str(row[6]), "raw_rows": int(row[7])}
                for row in grouped_rows
            ),
            (str(row[6]) for row in grouped_rows),
            start_utc,
            end_utc,
            bucket_minutes,
            ("raw_rows",),
            point_budget,
        )
    activity_rows = [row for row in rows if row[4] == "activity" and row[5] is not None]
    process_activity_available = (
        projection.event_type == "raw_process"
        and projection.process_name_column is not None
        and projection.activity_column is not None
        and projection.user_name_column is not None
    )
    process_activity_points = (
        tuple(
            {
                "bucket_utc": row[5],
                "hostname": str(row[6]),
                "username": str(row[9]),
                "process_type_count": int(row[8]),
            }
            for row in activity_rows
        )
        if process_activity_available and len(activity_rows) <= process_activity_point_budget
        else ()
    )
    return FamilyResult(
        projection.event_type,
        row_count - rows_without_hostname,
        rows_without_hostname,
        bucket_minutes,
        host_count,
        points,
        process_activity_available,
        process_activity_points,
    )


def chart_points(result: FamilyResult, hosts=None, normalized: bool = False):
    """Return selected chart rows, normalizing each selected host to its own peak."""
    selected = None if hosts is None else set(hosts)
    points = [p for p in result.points if selected is None or p["hostname"] in selected]
    peaks = {}
    if normalized:
        for point in points:
            host = point["hostname"]
            peaks[host] = max(peaks.get(host, 0), point["raw_rows"])
    return [
        {
            "bucket_utc": point["bucket_utc"],
            "hostname": point["hostname"],
            "value": point["raw_rows"] / peaks[point["hostname"]] if normalized and peaks[point["hostname"]] else 0.0,
            "raw_rows": point["raw_rows"],
        }
        for point in points
    ]
