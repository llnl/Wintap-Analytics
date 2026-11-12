"""S3 source setup using the same environment contract as wintap_dbt."""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.parse import urlsplit


# Mirrors the currently supported raw inputs in wintap_dbt/macros/validate_source.sql.
# Keep exact event directory names here; query discovery always includes day/hour
# before any recursive wildcard so S3 LIST requests stay partition-scoped.
RAW_EVENT_TYPES = (
    "raw_host",
    "raw_process",
    "raw_process_file",
    "raw_process_conn_incr",
    "raw_macip",
    "raw_macip_sensor",
    "raw_process_registry",
    "raw_registry",
    "raw_imageload",
    "raw_image_load",
    "raw_selinuxavc",
    "raw_selinuxinteraction",
    "raw_selinuxtransition",
    "pidstat",
)

MAX_S3_FILES = 10_000
MAX_WINDOW = dt.timedelta(hours=12)
UTC = dt.timezone.utc


@dataclass(frozen=True)
class S3Settings:
    dataset_root: str
    raw_sensor_root: str
    profile: str
    region: str
    endpoint_url: str
    use_ssl: bool

    @property
    def fingerprint(self) -> str:
        """Non-secret identity for checking whether the session snapshot is stale."""
        value = "\0".join((self.dataset_root, self.profile, self.region,
                           self.endpoint_url, str(self.use_ssl)))
        return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class S3ObjectMetadata:
    key: str
    event_type: str
    size_bytes: int


def _dataset_root(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Set WINTAP_DBT_RAW_SENSOR_DATASET or WINTAP_DBT_DATASET to an S3 dataset root")
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        raise ValueError("The DBT raw dataset root must be a plain s3://bucket/prefix URI without credentials, globs, or traversal") from None
    path = parsed.path.strip("/")
    if (parsed.scheme != "s3" or not parsed.netloc or parsed.query or parsed.fragment
            or parsed.username or parsed.password or ":" in parsed.netloc
            or any(char in value for char in "*?[]\\")
            or ".." in path.split("/") or not re.fullmatch(r"[A-Za-z0-9._-]+", parsed.netloc)):
        raise ValueError("The DBT raw dataset root must be a plain s3://bucket/prefix URI without credentials, globs, or traversal")
    if path == "raw_sensor" or path.endswith("/raw_sensor"):
        raise ValueError("Use the DBT dataset root containing raw_sensor/, not the raw_sensor directory itself")
    root = "s3://" + parsed.netloc
    return root + ("/" + path if path else "")


def _endpoint(value: str) -> str:
    if not value:
        return ""
    try:
        # DBT accepts either an HTTP(S) URL or a bare endpoint authority such
        # as host:port in AWS_ENDPOINT_URL. DuckDB's S3 secret expects only the
        # authority; TLS is controlled separately by DUCKDB_USE_SSL.
        parsed = urlsplit(value if "://" in value else "//" + value)
    except ValueError:
        raise ValueError("AWS_ENDPOINT_URL must be a host[:port] or HTTP(S) origin without credentials, path, or query") from None
    try:
        valid_port = parsed.port is None or 1 <= parsed.port <= 65535
    except ValueError:
        valid_port = False
    scheme_valid = parsed.scheme in ("", "http", "https")
    if (not scheme_valid or not parsed.hostname or not valid_port
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment):
        raise ValueError("AWS_ENDPOINT_URL must be a host[:port] or HTTP(S) origin without credentials, path, or query")
    return parsed.netloc


def _boolean(value: str, name: str, default: bool) -> bool:
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false")


def load_settings(environ=None) -> S3Settings:
    """Read DBT's dataset and S3 environment variables; no app-specific config."""
    env = os.environ if environ is None else environ
    dataset = (env.get("WINTAP_DBT_DATASET") or env.get("WINTAP_DATA_ROOT") or "").strip()
    raw_dataset = (env.get("WINTAP_DBT_RAW_SENSOR_DATASET") or dataset).strip()
    if not raw_dataset:
        raise ValueError(
            "Set WINTAP_DBT_RAW_SENSOR_DATASET (or WINTAP_DBT_DATASET / WINTAP_DATA_ROOT) to an S3 dataset root"
        )
    root = _dataset_root(raw_dataset)
    profile = (env.get("AWS_PROFILE") or "").strip()
    region = (env.get("AWS_DEFAULT_REGION") or env.get("AWS_REGION") or "").strip()
    endpoint = _endpoint((env.get("AWS_ENDPOINT_URL") or "").strip())
    use_ssl = _boolean(env.get("DUCKDB_USE_SSL"), "DUCKDB_USE_SSL", True)
    return S3Settings(
        dataset_root=root,
        raw_sensor_root=root + "/raw_sensor",
        profile=profile,
        region=region,
        endpoint_url=endpoint,
        use_ssl=use_ssl,
    )


def _sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def secret_sql(settings: S3Settings) -> str:
    """Render DBT-compatible credential-chain settings without key material."""
    clauses = ["TYPE S3", "PROVIDER CREDENTIAL_CHAIN"]
    if settings.profile:
        clauses.extend(("CHAIN 'config'", "PROFILE " + _sql_string(settings.profile)))
    if settings.region:
        clauses.append("REGION " + _sql_string(settings.region))
    if settings.endpoint_url:
        clauses.extend(("ENDPOINT " + _sql_string(settings.endpoint_url), "URL_STYLE 'path'"))
    clauses.append("USE_SSL " + ("true" if settings.use_ssl else "false"))
    return "CREATE OR REPLACE SECRET wintap_activity_s3 (" + ", ".join(clauses) + ")"


def open_connection(settings: S3Settings):
    """Open an in-memory DuckDB connection with an ephemeral, read-only S3 secret."""
    import duckdb

    con = None
    try:
        con = duckdb.connect(":memory:")
        con.install_extension("httpfs")
        con.load_extension("httpfs")
        con.execute("SET TimeZone='UTC'")
        con.execute(secret_sql(settings))
        return con
    except Exception:
        if con is not None:
            con.close()
        raise RuntimeError(
            "DuckDB S3 setup failed. Check the existing AWS profile/credential chain, "
            "AWS_ENDPOINT_URL, region, TLS setting, and local httpfs availability; details suppressed."
        ) from None


def open_metadata_client(settings: S3Settings):
    """Create a boto3 S3 client using the same AWS profile/environment chain."""
    try:
        import boto3
        from botocore.config import Config

        endpoint = None
        if settings.endpoint_url:
            scheme = "https" if settings.use_ssl else "http"
            endpoint = f"{scheme}://{settings.endpoint_url}"
        session = boto3.Session(profile_name=settings.profile or None)
        return session.client(
            "s3",
            endpoint_url=endpoint,
            region_name=settings.region or None,
            config=Config(
                s3={"addressing_style": "path"},
                connect_timeout=10,
                read_timeout=30,
                retries={"max_attempts": 2, "mode": "standard"},
            ),
        )
    except Exception:
        raise RuntimeError(
            "S3 metadata client setup failed. Check the existing AWS profile/credential chain, "
            "endpoint, region, TLS setting, and local boto3 installation; details suppressed."
        ) from None


def partition_hours(start: dt.datetime, end: dt.datetime):
    """Return UTC (YYYYMMDD, HH) partitions intersecting [start, end)."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Window bounds must include a timezone")
    first = start.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    exclusive_end = end.astimezone(UTC)
    if exclusive_end <= start.astimezone(UTC):
        raise ValueError("Window end must be after window start")
    if exclusive_end - start.astimezone(UTC) > MAX_WINDOW:
        raise ValueError("The dashboard source window is limited to 12 hours")
    last = (exclusive_end - dt.timedelta(microseconds=1)).replace(minute=0, second=0, microsecond=0)
    result = []
    current = first
    while current <= last:
        result.append((current.strftime("%Y%m%d"), current.strftime("%H")))
        current += dt.timedelta(hours=1)
    return result


def partition_globs(settings: S3Settings, start: dt.datetime, end: dt.datetime,
                    event_types=RAW_EVENT_TYPES):
    """Build a bounded list of event/day/hour-specific Parquet globs."""
    root = settings.raw_sensor_root.rstrip("/")
    event_types = tuple(event_types)
    if any(event not in RAW_EVENT_TYPES for event in event_types):
        raise ValueError("Unsupported raw_sensor event family")
    hours = partition_hours(start, end)
    return [
        f"{root}/{event}/dayPK={day}/hourPK={hour}/**/*.parquet"
        for event in event_types
        for day, hour in hours
    ]


def discover_files(con, settings: S3Settings, start: dt.datetime, end: dt.datetime,
                   max_files: int = MAX_S3_FILES, event_types=RAW_EVENT_TYPES):
    """List selected supported families in overlapping UTC hour partitions."""
    if not isinstance(max_files, int) or isinstance(max_files, bool) or max_files < 1:
        raise ValueError("S3 file limit must be a positive integer")
    event_types = tuple(dict.fromkeys(event_types))
    patterns = partition_globs(settings, start, end, event_types=event_types)
    expected_hours = set(partition_hours(start, end))
    if not patterns:
        return {}
    try:
        rows = con.execute(
            "SELECT file FROM glob(?) LIMIT ?", [patterns, max_files + 1]
        ).fetchall()
    except Exception:
        raise RuntimeError("S3 partition listing failed; check read/list access and endpoint settings; details suppressed.") from None
    paths = set()
    for row in rows:
        path = row[0]
        if not isinstance(path, str) or any(char in path for char in "*?[]\\"):
            raise RuntimeError("S3 object keys contain unsupported wildcard characters")
        paths.add(path)
    if len(paths) > max_files:
        raise ValueError("S3 file limit exceeded; narrow the source or increase MAX_S3_FILES")

    by_event = {event: [] for event in event_types}
    marker = settings.raw_sensor_root.rstrip("/") + "/"
    for path in sorted(paths):
        if not path.startswith(marker):
            raise RuntimeError("S3 listing returned a path outside the configured raw_sensor root")
        remainder = path[len(marker):]
        parts = remainder.split("/")
        if len(parts) < 4:
            raise RuntimeError("S3 partition listing returned an unexpected object path")
        event, day_part, hour_part = parts[:3]
        day_match = re.fullmatch(r"dayPK=(\d{8})", day_part)
        hour_match = re.fullmatch(r"hourPK=(\d{2})", hour_part)
        if (event not in by_event or day_match is None or hour_match is None
                or (day_match.group(1), hour_match.group(1)) not in expected_hours
                or not parts[-1].endswith(".parquet")):
            # Never trust a broad/incorrect glob result: file paths are the hard
            # partition boundary for all subsequent schema and row scans.
            raise RuntimeError("S3 partition listing returned an object outside the requested event/day/hour partitions")
        by_event[event].append(path)
    return {event: tuple(paths) for event, paths in by_event.items() if paths}


def discover_object_metadata(
    client,
    settings: S3Settings,
    start: dt.datetime,
    end: dt.datetime,
    max_files: int = MAX_S3_FILES,
    event_types=RAW_EVENT_TYPES,
):
    """List S3 keys and object sizes under relevant partitions; never read objects."""
    if not isinstance(max_files, int) or isinstance(max_files, bool) or max_files < 1:
        raise ValueError("S3 file limit must be a positive integer")
    event_types = tuple(dict.fromkeys(event_types))
    if any(event not in RAW_EVENT_TYPES for event in event_types):
        raise ValueError("Unsupported raw_sensor event family")
    hours = partition_hours(start, end)
    parsed_root = urlsplit(settings.raw_sensor_root)
    bucket = parsed_root.netloc
    root = parsed_root.path.strip("/")
    if not bucket or not root:
        raise ValueError("Configured raw_sensor root is invalid")

    objects = {}
    object_lock = threading.Lock()
    stop_listing = threading.Event()

    def list_partition(event_type, day, hour):
        prefix = f"{root}/{event_type}/dayPK={day}/hourPK={hour}/"
        continuation_token = None
        while not stop_listing.is_set():
            request = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
            if continuation_token is not None:
                request["ContinuationToken"] = continuation_token
            response = client.list_objects_v2(**request)
            for item in response.get("Contents", ()):
                if stop_listing.is_set():
                    return
                key = item.get("Key")
                if not isinstance(key, str) or not key.startswith(prefix):
                    raise RuntimeError("S3 metadata listing returned an object outside the requested partition")
                if not key.lower().endswith(".parquet"):
                    continue
                if any(char in key for char in "*?[]\\"):
                    raise RuntimeError("S3 object keys contain unsupported wildcard characters")
                size = item.get("Size")
                if not isinstance(size, int) or isinstance(size, bool) or size < 0:
                    raise RuntimeError("S3 metadata listing returned an invalid object size")
                with object_lock:
                    objects.setdefault(key, S3ObjectMetadata(key, event_type, size))
                    if len(objects) > max_files:
                        stop_listing.set()
                        raise ValueError("S3 file limit exceeded; narrow the source or increase MAX_S3_FILES")
            if not response.get("IsTruncated", False):
                return
            continuation_token = response.get("NextContinuationToken")
            if not continuation_token:
                raise RuntimeError("S3 metadata listing returned an incomplete pagination response")

    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(list_partition, event_type, day, hour)
                for event_type in event_types
                for day, hour in hours
            ]
            try:
                for future in as_completed(futures):
                    future.result()
            except Exception:
                stop_listing.set()
                for future in futures:
                    future.cancel()
                raise
    except ValueError:
        raise
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError(
            "S3 metadata listing failed; check read/list access, connectivity, and endpoint settings; details suppressed."
        ) from None
    return tuple(objects[key] for key in sorted(objects))
