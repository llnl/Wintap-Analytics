"""Read-only S3 listing and connection-scoped DuckDB access; no object writes."""
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlsplit

from queries import quote


FIELDS = {"endpoint", "region", "datasets", "start_day", "end_day", "max_files", "extension_directory"}


def day_range(start, end):
    try:
        first = dt.datetime.strptime(start, "%Y%m%d").date()
        last = dt.datetime.strptime(end, "%Y%m%d").date()
        if first.strftime("%Y%m%d") != start or last.strftime("%Y%m%d") != end:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("Partition days must be YYYYMMDD") from None
    if not 0 <= (last - first).days < 31:
        raise ValueError("Select an inclusive partition window of 1–31 days")
    return [(first + dt.timedelta(days=i)).strftime("%Y%m%d") for i in range((last - first).days + 1)]


def dataset_parts(uri):
    if not isinstance(uri, str):
        raise ValueError("Each dataset must be an s3://bucket/prefix string")
    parsed = urlsplit(uri)
    if (parsed.scheme != "s3" or not parsed.netloc or parsed.query or parsed.fragment
            or any(c in uri for c in "*?[]\\") or "@" in parsed.netloc or ":" in parsed.netloc):
        raise ValueError("Datasets require explicit s3://bucket/prefix roots without credentials or globs")
    prefix = parsed.path.strip("/")
    if ".." in prefix.split("/"):
        raise ValueError("Dataset prefixes must not contain parent traversal")
    if not prefix.endswith("/raw_sensor") and prefix != "raw_sensor":
        prefix = (prefix + "/" if prefix else "") + "raw_sensor"
    return parsed.netloc, prefix + "/"


def load_config(path):
    # Never echo config contents: only an allowlist of non-credential fields is accepted.
    try:
        value = json.loads(Path(path).expanduser().read_text())
    except (OSError, ValueError):
        raise ValueError("Cannot read SmokeTests JSON config") from None
    if not isinstance(value, dict) or set(value) - FIELDS:
        raise ValueError("Unsupported config fields; credentials belong in the AWS environment/profile")
    endpoint = value.get("endpoint", "")
    if not isinstance(endpoint, str):
        raise ValueError("endpoint must be an HTTP(S) URL")
    parsed = urlsplit(endpoint)
    if (parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username
            or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("endpoint requires an HTTP(S) origin without credentials, path or query")
    datasets = value.get("datasets")
    if not isinstance(datasets, list) or not 1 <= len(datasets) <= 20:
        raise ValueError("Configure 1–20 S3 dataset roots")
    for uri in datasets:
        dataset_parts(uri)
    region = value.get("region", "us-east-1")
    if not isinstance(region, str) or not region:
        raise ValueError("region must be a nonempty string")
    maximum = value.get("max_files", 10000)
    if isinstance(maximum, bool) or not isinstance(maximum, int) or not 1 <= maximum <= 100000:
        raise ValueError("max_files must be 1–100000")
    extension_directory = value.get("extension_directory")
    if extension_directory is not None and (not isinstance(extension_directory, str) or not extension_directory):
        raise ValueError("extension_directory must be a nonempty local path")
    today = dt.datetime.now(dt.timezone.utc).date()
    value.setdefault("start_day", (today - dt.timedelta(days=1)).strftime("%Y%m%d"))
    value.setdefault("end_day", today.strftime("%Y%m%d"))
    day_range(value["start_day"], value["end_day"])
    return dict(value, region=region, max_files=maximum)


def open_source(config):
    """Resolve standard AWS env/profile credentials; keep them off disk/UI/logs."""
    import boto3
    import duckdb
    from botocore.config import Config

    connection = None
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            raise ValueError("No AWS credentials")
        credentials = credentials.get_frozen_credentials()
        options = {}
        if config.get("extension_directory"):
            options["extension_directory"] = str(Path(config["extension_directory"]).expanduser())
        connection = duckdb.connect(":memory:", config=options)
        connection.install_extension("httpfs")
        connection.load_extension("httpfs")
        endpoint = urlsplit(config["endpoint"])
        fields = ["TYPE S3", "KEY_ID " + quote(credentials.access_key),
                  "SECRET " + quote(credentials.secret_key), "ENDPOINT " + quote(endpoint.netloc),
                  "REGION " + quote(config["region"]), "URL_STYLE 'path'",
                  "USE_SSL " + ("true" if endpoint.scheme == "https" else "false")]
        if credentials.token:
            fields.append("SESSION_TOKEN " + quote(credentials.token))
        # Never persistent: scoped to this in-memory connection only.
        connection.execute("CREATE TEMPORARY SECRET smoke_s3 (" + ", ".join(fields) + ")")
        client = session.client("s3", endpoint_url=config["endpoint"], region_name=config["region"],
                                config=Config(s3={"addressing_style": "path"},
                                              connect_timeout=10, read_timeout=30,
                                              retries={"max_attempts": 2}))
        return connection, client
    except Exception:
        if connection is not None:
            connection.close()
        # SDK/DuckDB exceptions can echo connection SQL or signed URLs. Do not display them.
        raise RuntimeError("S3 connection setup failed. Check AWS credentials/profile, endpoint, TLS trust and cached httpfs extension locally; details suppressed to protect credentials.") from None


def discover_files(client, config, start, end, snapshot=None):
    """Paginated, partition-pruned listing; caps fail closed, never silently truncate."""
    days = day_range(start, end)
    files = set()
    try:
        paginator = client.get_paginator("list_objects_v2")
        for uri in config["datasets"]:
            bucket, root = dataset_parts(uri)
            events = set()
            for page in paginator.paginate(Bucket=bucket, Prefix=root, Delimiter="/"):
                events.update(p["Prefix"] for p in page.get("CommonPrefixes", []))
                if len(events) > 100:
                    raise ValueError("Too many event prefixes; narrow the dataset root")
            for event in sorted(events):
                if not event.startswith(root) or event.count("/") != root.count("/") + 1:
                    raise ValueError("Unexpected S3 event prefix")
                for day in days:
                    partition = event + "dayPK=" + day + "/"
                    for page in paginator.paginate(Bucket=bucket, Prefix=partition):
                        for item in page.get("Contents", []):
                            key = item["Key"]
                            if not key.startswith(partition) or not key.endswith(".parquet"):
                                continue
                            if any(c in key for c in "*?[]\\"):
                                raise ValueError("S3 keys contain unsupported wildcard characters")
                            files.add("s3://" + bucket + "/" + key)
                            if snapshot is not None:
                                snapshot["s3://" + bucket + "/" + key] = object_identity(item)
                            if len(files) > config["max_files"]:
                                raise ValueError("S3 file limit exceeded; narrow the partition window or increase max_files")
    except ValueError:
        raise
    except Exception:
        raise RuntimeError("S3 listing failed; check read/list permissions, connectivity and endpoint. Details suppressed to protect credentials.") from None
    evidence = sorted(p for p in files if "/raw_smoke_test/" in p)
    telemetry = sorted(files - set(evidence))
    return evidence, telemetry


def object_identity(item):
    return [item.get('ETag'), item.get('Size'), str(item.get('LastModified', ''))]


def discover_host_files(client, config, snapshot=None):
    """HOST startup can predate the selected canary day; list receipt history only."""
    files = set()
    try:
        paginator = client.get_paginator('list_objects_v2')
        for uri in config['datasets']:
            bucket, root = dataset_parts(uri)
            for page in paginator.paginate(Bucket=bucket, Prefix=root + 'raw_host/'):
                for item in page.get('Contents', []):
                    key = item['Key']
                    if not key.startswith(root + 'raw_host/') or not key.endswith('.parquet'):
                        continue
                    if any(c in key for c in '*?[]\\'):
                        raise ValueError('Unsupported HOST object key')
                    path = 's3://' + bucket + '/' + key
                    files.add(path)
                    if snapshot is not None:
                        snapshot[path] = object_identity(item)
                    if len(files) > config['max_files']:
                        raise ValueError('HOST history file limit exceeded')
    except ValueError:
        raise
    except Exception:
        raise RuntimeError('HOST history listing unavailable; details suppressed') from None
    return sorted(files)
