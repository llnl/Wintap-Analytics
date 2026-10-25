"""Read-only, portable-manifest smoke queries. No Streamlit dependency."""
import datetime as dt
import hashlib
import ipaddress
import json
from pathlib import Path

TESTS = {
    "canary-cross-domain": "Canary: named process/file/loopback TCP + UDP",
    "canary-process": "Canary: process lifecycle + short-lived children",
    "canary-file": "Canary: eight-file activity",
    "canary-clone": "Canary: native clone lifecycle",
    "canary-network-endpoints": "Canary: same-host TCP endpoints",
    "telemetry-workload": "Named cross-domain workload",
    "process-capture": "Process capture",
    "file-capture": "File capture",
    "network-capture": "Network capture",
    "network-endpoints": "TCP endpoint normalization",
    "clone-trace": "Clone actual-object trace",
    "clone-pipeline": "Clone direct pipeline",
    "clone-package": "Clone packaged acceptance",
    "runtime-capabilities": "Runtime capability receipts",
}


def validate_manifest(value):
    if not isinstance(value, dict):
        raise ValueError("Manifest must be an object")
    if value.get("smokeManifestVersion") != 1:
        raise ValueError("Expected smokeManifestVersion=1; re-run the updated smoke test")
    if value.get("test") not in TESTS or not value.get("runId"):
        raise ValueError("Unknown smoke test or missing runId")
    if not value.get("host", {}).get("hostname"):
        raise ValueError("Manifest must identify the test hostname")
    if not isinstance(value.get("selectors"), list):
        raise ValueError("Manifest selectors must be a list")
    for index, selector in enumerate(value["selectors"]):
        if not isinstance(selector, dict):
            raise ValueError(f"Manifest selector {index} must be an object")
        if selector.get("domain") not in ("process", "file", "network", "host"):
            raise ValueError(f"Manifest selector {index} requires a supported domain")
    return value


def load_manifests(directory, uploads=(), data_root="", connection=None, evidence_files=None):
    runs, errors = {}, []
    conflicts = set()
    documents = []
    if directory:
        root = Path(directory).expanduser()
        if root.exists():
            try:
                documents.extend((str(p), p.read_bytes()) for p in root.rglob("*.json"))
            except OSError as error:
                errors.append(str(error))
        else:
            errors.append(f"Manifest directory not found: {root}")
    documents.extend(uploads)
    if data_root or evidence_files is not None:
        root = Path(data_root).expanduser()
        if root.name == "raw_sensor":
            evidence = root / "raw_smoke_test"
        else:
            evidence = root / "raw_sensor" / "raw_smoke_test"
        own_connection = connection is None
        if own_connection:
            import duckdb
            connection = duckdb.connect(":memory:")
        try:
            paths = evidence_files if evidence_files is not None else sorted(evidence.rglob("*.parquet"))
            for path in paths:
                try:
                    records = connection.execute(f"SELECT schema_version, run_id, test_name, revision, phase, hostname, manifest_json, manifest_sha256 FROM read_parquet({quote(path)})").fetchall()
                    for version, run_id, test, revision, phase, host, text, digest in records:
                        if version != 1 or hashlib.sha256(text.encode()).hexdigest() != digest:
                            raise ValueError("Unsupported evidence schema or manifest hash mismatch")
                        value = validate_manifest(json.loads(text))
                        if (value["runId"], value["test"], value["host"]["hostname"],
                            value.get("smokeEvidenceRevision"), value.get("smokeEvidencePhase")) != (run_id, test, host, revision, phase):
                            raise ValueError("Typed evidence metadata disagrees with manifest")
                        documents.append((str(path), text))
                except Exception as error:
                    detail = type(error).__name__ if str(path).startswith("s3://") else str(error)
                    errors.append(f"{path}: {detail}; refresh if the file is still arriving")
        finally:
            if own_connection:
                connection.close()
    revisions = {}
    for name, content in documents:
        try:
            value = json.loads(content)
            # Other workload/report/config JSON in the evidence tree is not a run envelope.
            if "smokeManifestVersion" not in value:
                continue
            value = validate_manifest(value)
            key = (value["test"], value["runId"])
            revision = value.get("smokeEvidenceRevision", 0)
            if not isinstance(revision, int) or revision < 0:
                raise ValueError("Invalid evidence revision")
            snapshot_key = (*key, revision)
            if snapshot_key in revisions and revisions[snapshot_key] != value:
                errors.append(f"Conflicting copies for {key}: {name}; use one completed manifest")
                conflicts.add(key)
                continue
            revisions[snapshot_key] = value
            if key not in runs or revision > runs[key].get("smokeEvidenceRevision", 0):
                runs[key] = value
        except (ValueError, TypeError, AttributeError) as error:
            errors.append(f"{name}: {error}")
    return sorted((v for k, v in runs.items() if k not in conflicts),
                  key=lambda r: r.get("startedAtUtc", ""), reverse=True), errors


def quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def identifier(value):
    return '"' + value.replace('"', '""') + '"'


def timestamp(expr):
    """Known Wintap FILETIME and Unix s/ms/us/ns, or ISO/timestamp columns."""
    n = f"TRY_CAST({expr} AS DOUBLE)"
    return f"""CASE WHEN {n} IS NULL THEN TRY_CAST({expr} AS TIMESTAMP)
        WHEN {n} BETWEEN 100000000000000000 AND 300000000000000000
          THEN to_timestamp(({n} - 116444736000000000) / 10000000)
        WHEN {n} > 1000000000000000000 THEN to_timestamp({n} / 1000000000)
        WHEN {n} > 100000000000000 THEN to_timestamp({n} / 1000000)
        WHEN {n} > 100000000000 THEN to_timestamp({n} / 1000)
        ELSE to_timestamp({n}) END"""


def prepare_data(connection, root, unlabelled_host="", telemetry_files=None):
    """Normalize file-by-file, avoiding cross-domain schema collisions.

    Host setting only applies to files with no hostname field. Never inferred from
    analysis machine. User must scope the chosen parquet root to that one host.
    """
    root = Path(root).expanduser()
    connection.execute("SET TimeZone='UTC'")
    files = (telemetry_files if telemetry_files is not None else
             sorted(p for p in root.rglob("*.parquet") if "raw_smoke_test" not in p.parts) if root.exists() else [])
    connection.execute("DROP VIEW IF EXISTS smoke_data")
    errors, groups = [], {}
    for path in files:
        try:
            schema = connection.execute(f"DESCRIBE SELECT * FROM read_parquet({quote(path)})").fetchall()
            columns = tuple(row[0] for row in schema)
            if "manifest_json" in columns and "manifest_version" in columns:
                continue
            groups.setdefault(columns, []).append(path)
        except Exception as error:
            detail = type(error).__name__ if str(path).startswith("s3://") else str(error)
            errors.append(f"{path}: {detail}")
    projections = []
    for columns, paths in groups.items():
        lower = {c.lower(): c for c in columns}
        def col(*names, cast="VARCHAR"):
            found = [f"TRY_CAST({identifier(lower[n.lower()])} AS {cast})" for n in names if n.lower() in lower]
            return "COALESCE(" + ",".join(found + ["NULL"]) + ")" if found else f"CAST(NULL AS {cast})"
        host = col("Hostname", "HostName", "ComputerName")
        if not any(n in lower for n in ("hostname", "computername")) and unlabelled_host:
            host = quote(unlabelled_host)
        event_time = col("FirstSeenMs", "FirstSeen", "EventTime", "CapturedUtc")
        activity = col("IpEvent", "ActivityType")
        kind = col("MessageType")
        file_path = col("File_Path", "Path", "FileName")
        protocol = col("Protocol", "TcpConnection_Protocol", "UdpPacket_Protocol")
        remote_port = col("RemotePort", "TcpConnection_DestinationPort", "UdpPacket_DestinationPort", cast="INTEGER")
        local_port = col("LocalPort", "TcpConnection_SourcePort", "UdpPacket_SourcePort", cast="INTEGER")
        filename = "filename"
        inferred_protocol = f"COALESCE(lower({protocol}), CASE WHEN lower({kind}) LIKE '%tcp%' OR lower({filename}) LIKE '%tcp%' THEN 'tcp' WHEN lower({kind}) LIKE '%udp%' OR lower({filename}) LIKE '%udp%' THEN 'udp' END)"
        domain = f"""CASE WHEN {col('RuntimeCapabilitiesJson')} IS NOT NULL THEN 'host'
            WHEN {file_path} IS NOT NULL OR lower({kind}) LIKE '%file%' OR lower(filename) LIKE '%raw_process_file%' THEN 'file'
            WHEN {remote_port} IS NOT NULL OR lower({kind}) LIKE '%tcp%' OR lower({kind}) LIKE '%udp%' THEN 'network'
            WHEN lower({kind}) = 'process' OR lower(filename) LIKE '%raw_process+%' OR lower(filename) LIKE '%processserializer%' THEN 'process'
            ELSE 'other' END"""
        fields = {
            "host": f"lower({host})", "domain": domain, "event_time": f"CAST(({timestamp(event_time)}) AS TIMESTAMP)",
            "pid": col("PID", cast="BIGINT"), "parent_pid": col("ParentPid", "Process_ParentPID", cast="BIGINT"),
            "pid_hash": col("PidHash"), "activity": f"lower({activity})", "process_name": col("ProcessName", "Process_ProcessName"),
            "command_line": col("CommandLine", "Process_CommandLine"), "path": file_path,
            "start_source": f"NULLIF(regexp_extract({col('Arguments', 'Process_Arguments')}, 'PROC_START_SRC=([a-z_]+)', 1), '')",
            "protocol": inferred_protocol, "local_port": local_port, "remote_port": remote_port,
            "source_port": col("SourcePort", cast="INTEGER"), "destination_port": col("DestinationPort", cast="INTEGER"),
            "local_address": col("LocalIpAddr", "TcpConnection_SourceAddress", "UdpPacket_SourceAddress"),
            "remote_address": col("RemoteIpAddr", "TcpConnection_DestinationAddress", "UdpPacket_DestinationAddress"),
            "event_count": f"COALESCE({col('EventCount', cast='BIGINT')}, 1)",
            "receipt": col("RuntimeCapabilitiesJson"), "source_file": "filename",
        }
        file_list = "[" + ",".join(quote(p) for p in paths) + "]"
        projections.append("SELECT " + ", ".join(f"{expr} AS {name}" for name, expr in fields.items()) +
                           f" FROM read_parquet({file_list}, union_by_name=true, filename=true)")
    if projections:
        connection.execute("CREATE OR REPLACE TEMP VIEW smoke_data AS " + " UNION ALL ".join(projections))
    return len(files), errors, bool(projections)


def selector_query(run, selector, padding=15):
    domain = selector["domain"]
    where = [f"domain = {quote(domain)}", f"host = {quote(run['host']['hostname'].lower())}"]
    if domain == "host":
        where.append(f"json_extract_string(receipt, '$.captureRunId') = {quote(selector['captureRunId'])}")
    else:
        start = selector.get("startedAtUtc") or run["startedAtUtc"]
        end = selector.get("completedAtUtc") or run.get("completedAtUtc")
        if not end:
            raise ValueError("Run has no end time yet; refresh after completion")
        # Parse/validate timestamps before SQL interpolation.
        for value in (start, end):
            dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        where.append(f"event_time BETWEEN CAST({quote(start)} AS TIMESTAMPTZ) - INTERVAL '{int(padding)} seconds' AND CAST({quote(end)} AS TIMESTAMPTZ) + INTERVAL '{int(padding)} seconds'")
        pids = selector.get("pids", [])
        threads = selector.get("threadIds", []) if domain == "process" else []
        candidates = sorted({int(pid) for pid in pids + threads})
        if not candidates:
            raise ValueError("No PID selectors recorded; this test did not reach stimulus generation")
        where.append("pid IN (" + ",".join(map(str, candidates)) + ")")
        if domain == "file":
            if selector.get("pathPrefix"):
                where.append(f"starts_with(lower(path), {quote(selector['pathPrefix'].lower())})")
            elif selector.get("paths"):
                where.append("lower(path) IN (" + ",".join(quote(p.lower()) for p in selector["paths"]) + ")")
            else:
                raise ValueError("File selector requires paths or pathPrefix")
        if domain == "network" and selector.get("ports"):
            ports = ",".join(str(int(p)) for p in selector["ports"])
            where.append(f"(local_port IN ({ports}) OR remote_port IN ({ports}) OR source_port IN ({ports}) OR destination_port IN ({ports}))")
        # Expectations are checks, not acceptance filters. Keep malformed/wrong-
        # protocol candidates inside the same bounded working set.
    return "SELECT * FROM smoke_data WHERE " + " AND ".join(where) + " ORDER BY event_time, pid"


def coverage(rows, selector):
    """Observation indicators, deliberately not equivalent to harness pass/fail."""
    checks = []
    activities = {row["activity"] for row in rows}
    for expected in selector.get("expectedActivities", []):
        checks.append(dict(expectation=expected, observed=expected.lower() in activities))
    for expected in selector.get("expectedProtocols", []):
        checks.append(dict(expectation=expected, observed=expected.lower() in {r["protocol"] for r in rows}))
    if selector.get("expectedPaths"):
        count = len({r["path"] for r in rows if r["path"]})
        checks.append(dict(expectation=f"Distinct paths: {count}/{selector['expectedPaths']}",
                            observed=count >= int(selector["expectedPaths"])))
    if selector['domain'] == 'file' and selector.get('expectedActivities'):
        expected = path_expectations(selector, {r['path'] for r in rows if r['path']})
        paths = list(expected)
        complete = sum(required.issubset({r['activity'] for r in rows if r['path'] == p}) for p, required in expected.items())
        checks.append(dict(expectation=f"Paths with all required activities: {complete}/{len(paths)}",
                           observed=bool(paths) and complete == len(paths)))
    if selector["domain"] == "process":
        starts = {r["pid"] for r in rows if r["activity"] == "start"}
        for pid in selector.get("pids", []):
            checks.append(dict(expectation=f"PID {pid} Start", observed=int(pid) in starts))
        for tid in selector.get("threadIds", []):
            checks.append(dict(expectation=f"Thread {tid}: no process Start", observed=int(tid) not in starts))
        for link in selector.get("links", []):
            matched = [r for r in rows if r["pid"] == link["childPid"] and r["activity"] == "start"]
            checks.append(dict(expectation=f"{link['case']}: parent PID {link['parentPid']}",
                               observed=bool(matched) and all(r["parent_pid"] == link["parentPid"] for r in matched)))
    return checks


def evaluate_case(connection, run, selector, available, padding=15):
    """Aggregate complete matching data; never materialize all events for triage."""
    result = dict(selector=selector, checks=[], summary=[], rows=0, violations=[], warnings=[], error=None)
    if not available:
        result["error"] = "No collected telemetry available yet"
        return result
    try:
        sql = selector_query(run, selector, padding)
        result["sql"] = sql
        result["summary"] = [dict(activity=a, protocol=p, rows=n, event_count=c) for a, p, n, c in
                             connection.execute(f"SELECT activity, protocol, count(*), sum(event_count) FROM ({sql}) GROUP BY 1,2 ORDER BY 1,2").fetchall()]
        result["rows"] = sum(row["rows"] for row in result["summary"])
        activities = {row["activity"] for row in result["summary"]}
        protocols = {row["protocol"] for row in result["summary"]}
        for expected in selector.get("expectedActivities", []):
            result["checks"].append(dict(expectation=expected, observed=expected.lower() in activities))
        for expected in selector.get("expectedProtocols", []):
            result["checks"].append(dict(expectation=expected, observed=expected.lower() in protocols))
        if selector.get("expectedPaths"):
            count = connection.execute(f"SELECT count(DISTINCT path) FROM ({sql})").fetchone()[0]
            result["checks"].append(dict(expectation=f"Distinct paths: {count}/{selector['expectedPaths']}", observed=count >= int(selector["expectedPaths"])))
        if selector['domain'] == 'file' and selector.get('expectedActivities'):
            paths = connection.execute(f"SELECT path, list(DISTINCT activity) FROM ({sql}) GROUP BY path").fetchall()
            by_path = {path: set(activities) for path, activities in paths if path}
            # Linux paths are case-sensitive. Exact expected paths also expose
            # missing paths, even when enough unrelated prefix paths were seen.
            expected = path_expectations(selector, by_path)
            complete = sum(required.issubset(by_path.get(path, set())) for path, required in expected.items())
            result['checks'].append(dict(expectation=f"Paths with all required activities: {complete}/{len(expected)}",
                observed=bool(expected) and complete == len(expected)))
            folded = {}
            for path in by_path:
                folded.setdefault(path.lower(), set()).add(path)
            case_only = sum(path not in by_path and path.lower() in folded for path in expected)
            if case_only:
                result['warnings'].append(f'Expected paths matching only after case folding: {case_only}; exact case-sensitive path identity unconfirmed (projection may discard case)')
        if selector["domain"] == "process":
            starts = connection.execute(f"SELECT pid, count(DISTINCT pid_hash), list(DISTINCT parent_pid) FROM ({sql}) WHERE activity='start' GROUP BY pid").fetchall()
            by_pid = {pid: (identities, parents) for pid, identities, parents in starts}
            for pid in selector.get("pids", []):
                result["checks"].append(dict(expectation=f"PID {pid} Start", observed=int(pid) in by_pid))
            if selector.get("requireStopPerPid"):
                stopped = {r[0] for r in connection.execute(f"SELECT DISTINCT pid FROM ({sql}) WHERE activity='stop'").fetchall()}
                for pid in selector.get("pids", []):
                    result["checks"].append(dict(expectation=f"PID {pid} Stop", observed=int(pid) in stopped))
            for tid in selector.get("threadIds", []):
                observed = int(tid) not in by_pid
                result["checks"].append(dict(expectation=f"Thread {tid}: no process Start", observed=observed))
                if not observed:
                    result["violations"].append(f"Thread {tid} recorded as a process Start")
            for pid, (identities, parents) in by_pid.items():
                if identities > 1:
                    result["violations"].append(f"PID {pid} has multiple Start identities in this window")
            for link in selector.get("links", []):
                entry = by_pid.get(int(link["childPid"]))
                matched = bool(entry) and all(p == int(link["parentPid"]) for p in entry[1])
                result["checks"].append(dict(expectation=f"{link['case']}: parent PID {link['parentPid']}", observed=matched))
                if entry and any(p is not None and p != int(link["parentPid"]) for p in entry[1]):
                    result["violations"].append(f"{link['case']}: wrong parent PID")
            evaluate_lifecycle(connection, sql, selector, result)
        if selector["domain"] == "host":
            receipts = connection.execute(f"SELECT DISTINCT receipt FROM ({sql})").fetchall()
            result["receipts"] = [json.loads(r[0]) for r in receipts]
            result["capability_gaps"] = [f"{name}: {sensor.get('status', 'unknown')}" for receipt in result["receipts"]
                                         for name, sensor in receipt.get("sensors", {}).items()
                                          if sensor.get("status") != "running"]
        if selector["domain"] == "network" and selector.get("endpointExpectations"):
            identities = {}
            for end in selector["endpointExpectations"]:
                protocol = end.get('protocol', 'tcp').lower()
                for activity in (protocol + 'ipsend', protocol + 'iprecv'):
                    inbound = activity.endswith('iprecv')
                    src = int(end["remotePort"] if inbound else end["localPort"])
                    dest = int(end["localPort"] if inbound else end["remotePort"])
                    match = (f"pid={int(end['pid'])} AND lower(replace(activity,'/',''))={quote(activity)} "
                             f"AND source_port={src} AND destination_port={dest}")
                    local_ip = str(int(ipaddress.IPv4Address(end["localIp"])))
                    remote_ip = str(int(ipaddress.IPv4Address(end["remoteIp"])))
                    correct = (f"local_port={int(end['localPort'])} AND remote_port={int(end['remotePort'])} "
                               f"AND local_address IN ({quote(local_ip)}, {quote(end['localIp'])}) "
                               f"AND remote_address IN ({quote(remote_ip)}, {quote(end['remoteIp'])})")
                    complete = 'local_port IS NOT NULL AND remote_port IS NOT NULL AND local_address IS NOT NULL AND remote_address IS NOT NULL'
                    total, wrong = connection.execute(f"SELECT count(*), count(*) FILTER(WHERE {complete} AND NOT COALESCE(({correct}), false)) FROM ({sql}) WHERE {match}").fetchone()
                    label = f"{end['role']}/{activity}: host-relative endpoint + directed provenance"
                    result["checks"].append(dict(expectation=label, observed=total > 0))
                    if wrong:
                        result["violations"].append(label + ": reversed/incorrect endpoint")
                    hashes = {row[0] for row in connection.execute(f"SELECT DISTINCT pid_hash FROM ({sql}) WHERE {match}").fetchall()}
                    if any(not valid_identity(h) for h in hashes):
                        result["violations"].append(label + ": missing process identity")
                    identities.setdefault(int(end["pid"]), set()).update(h for h in hashes if h)
            if any(len(values) > 1 for values in identities.values()):
                result["violations"].append("Inconsistent pid_hash within one process")
            nonempty = [values for values in identities.values() if values]
            if len(nonempty) == 2 and len(set.union(*nonempty)) < 2:
                result["violations"].append("Separate socket processes share pid_hash")
            evaluate_endpoint_candidates(connection, sql, selector, result)
        elif selector['domain'] == 'network' and selector.get('expectedProtocols'):
            unexpected = protocols - {p.lower() for p in selector['expectedProtocols']}
            if unexpected:
                result['warnings'].append('Unexpected/unknown protocol among PID/port candidates; exact socket attribution unconfirmed')
        return result
    except Exception as error:
        result["error"] = str(error)
        return result


def path_expectations(selector, observed_paths):
    if selector.get('pathExpectations'):
        return {entry['path']: {a.lower() for a in entry['expectedActivities']} for entry in selector['pathExpectations']}
    paths = selector.get('paths') or sorted(observed_paths)
    return {path: {a.lower() for a in selector.get('expectedActivities', [])} for path in paths}


def valid_identity(value):
    """Presence gate, not recomputation of the canonical host/birth hash."""
    return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in ('fixmepid', 'unknown', '0', 'null', 'none')


def evaluate_lifecycle(connection, sql, selector, result):
    columns = {c[0] for c in connection.execute(f'DESCRIBE SELECT * FROM ({sql})').fetchall()}
    source = 'start_source' if 'start_source' in columns else 'NULL::VARCHAR'
    groups = connection.execute(f"SELECT pid, pid_hash, activity, {source}, count(*) FROM ({sql}) WHERE activity IN ('start','stop') GROUP BY 1,2,3,4").fetchall()
    starts, stops, observations = {}, {}, {}
    invalid = 0
    for pid, identity, activity, origin, count in groups:
        if not valid_identity(identity):
            invalid += count
        else:
            (starts if activity == 'start' else stops).setdefault(pid, set()).add(identity)
        if activity == 'start':
            entry = observations.setdefault((pid, identity), dict(count=0, classified=0))
            entry['count'] += count
            if origin in ('sched_fork', 'sched_exec', 'execve_or_execveat'):
                entry['classified'] += count
    if invalid:
        result['violations'].append(f'Lifecycle rows with missing/placeholder process identity: {invalid}')
    if groups or selector.get('pids'):
        result['checks'].append(dict(expectation='Lifecycle rows have non-placeholder identity (not canonical hash proof)',
            observed=bool(groups) and not invalid))
    for pid in selector.get('pids', []):
        birth = starts.get(int(pid), set())
        ended = stops.get(int(pid), set())
        if birth and ended and ended - birth:
            result['violations'].append(f'PID {pid} Stop identity differs from observed Start identity')
        if selector.get('requireStopPerPid'):
            result['checks'].append(dict(expectation=f'PID {pid} Start identities linked to Stop',
                observed=bool(birth) and birth.issubset(ended)))
    repeats = [v for v in observations.values() if v['count'] > 1]
    unclassified = sum(v['count'] != v['classified'] for v in repeats)
    result['lifecycle'] = dict(start_rows=sum(n for _, _, a, _, n in groups if a == 'start'),
        stop_rows=sum(n for _, _, a, _, n in groups if a == 'stop'),
        repeated_start_identity_groups=len(repeats), unclassified_repeat_groups=unclassified)
    if repeats:
        result['checks'].append(dict(expectation=f'Repeated Start groups source-classified: {len(repeats) - unclassified}/{len(repeats)}',
            observed=not unclassified))
        result['warnings'].append('Repeated raw Starts are lifecycle/image observations, not distinct births or exact-count proof')


def evaluate_endpoint_candidates(connection, sql, selector, result):
    """Check all attributable Send/Recv rows, not just already-correct provenance.

    A complete expected host-relative OR directed port pair binds a socket role.
    Other shared-PID/port traffic is uncertain, not automatically a red defect.
    Missing provenance is incomplete; non-null contradictory provenance is red.
    """
    rows = connection.execute(f"SELECT pid, pid_hash, lower(replace(activity,'/','')), protocol, local_port, remote_port, source_port, destination_port, local_address, remote_address FROM ({sql}) WHERE lower(replace(activity,'/','')) IN ('tcpipsend','tcpiprecv','udpipsend','udpiprecv')").fetchall()
    unknown, missing = 0, 0
    hashes = {}
    wrong_endpoint, wrong_protocol, bad_identity = 0, 0, 0
    for pid, identity, activity, protocol, local, remote, src, dest, lip, rip in rows:
        ends = [e for e in selector['endpointExpectations'] if int(e['pid']) == pid]
        inbound = activity.endswith('iprecv')
        bound = [e for e in ends if (local, remote) == (int(e['localPort']), int(e['remotePort'])) or
            (src, dest) == (int(e['remotePort'] if inbound else e['localPort']), int(e['localPort'] if inbound else e['remotePort']))]
        if not bound:
            unknown += 1
            continue
        if not valid_identity(identity):
            bad_identity += 1
        else:
            hashes.setdefault(pid, set()).add(identity)
        if not any((protocol or '').lower() == e.get('protocol', 'tcp').lower() and
                   activity.startswith(e.get('protocol', 'tcp').lower() + 'ip') for e in bound):
            wrong_protocol += 1
        if any(v is None for v in (local, remote, src, dest, lip, rip)):
            missing += 1
            continue
        def correct(end):
            local_ips = (end['localIp'], str(int(ipaddress.IPv4Address(end['localIp']))))
            remote_ips = (end['remoteIp'], str(int(ipaddress.IPv4Address(end['remoteIp']))))
            return ((local, remote) == (int(end['localPort']), int(end['remotePort'])) and
                (src, dest) == (int(end['remotePort'] if inbound else end['localPort']), int(end['localPort'] if inbound else end['remotePort'])) and
                str(lip) in local_ips and str(rip) in remote_ips)
        if not any(correct(e) for e in bound):
            wrong_endpoint += 1
    if wrong_endpoint:
        # Existing matching-candidate checks already report reversals. Add a
        # separate finding only for extra malformed provenance that escaped them.
        if not any('reversed/incorrect endpoint' in v for v in result['violations']):
            result['violations'].append(f'Attributed Send/Recv rows have incorrect endpoint/directed provenance: {wrong_endpoint}')
    if wrong_protocol:
        result['violations'].append(f'Attributed socket rows have wrong/unknown protocol: {wrong_protocol}')
    if bad_identity and not any('missing process identity' in v for v in result['violations']):
        result['violations'].append(f'Attributed socket rows have missing process identity: {bad_identity}')
    if any(len(h) > 1 for h in hashes.values()) and 'Inconsistent pid_hash within one process' not in result['violations']:
        result['violations'].append('Inconsistent pid_hash within one process')
    if unknown or missing:
        result['checks'].append(dict(expectation='All Send/Recv candidates have attributable complete endpoint provenance', observed=False))
        result['warnings'].append(f'Unattributed Send/Recv candidates: {unknown}; attributed rows with incomplete provenance: {missing}')


def evaluate_run(connection, run, available, padding=15):
    cases = [evaluate_case(connection, run, s, available, padding) for s in run["selectors"]]
    reasons = []
    status = run.get("status", "unknown")
    if status == "failed":
        reasons.append("Harness/workload failed (not automatically a sensor failure)")
    violations = [v for case in cases for v in case["violations"]]
    reasons.extend(violations)
    red = status == "failed" or bool(violations)
    if status != "passed" or not run.get("completedAtUtc"):
        reasons.append("Run unfinished or outcome unknown")
    if run.get("durableExportError"):
        reasons.append("Evidence export encountered an error")
    if run["test"] == "network-capture" and run.get("endpointChecksRequested") is False:
        reasons.append("Host-relative TCP endpoint confirmation explicitly not run")
    saved = run.get("results") or {}
    skipped = any(s.get("skips") for s in run["selectors"]) or any(
        c.get("status") == "skipped" for c in saved.get("cases", []) if isinstance(c, dict))
    if skipped:
        reasons.append("Some stimulus/checks were skipped")
    trace_only = run["test"] == "clone-trace"
    if trace_only and not saved:
        reasons.append("Actual-object report missing")
    positive_process = any(c["selector"]["domain"] == "process" and c["selector"].get("pids")
                           and any(ch["observed"] and ch["expectation"].startswith("PID ") for ch in c["checks"]) for c in cases)
    if not trace_only:
        if not cases:
            reasons.append("No stimulus selectors recorded")
        for case in cases:
            selector = case["selector"]
            label = selector.get("case", selector["domain"])
            negative_only = selector["domain"] == "process" and selector.get("threadIds") and not selector.get("pids")
            if case["error"]:
                reasons.append(f"{label}: {case['error']}")
            elif negative_only:
                if not positive_process:
                    reasons.append(f"{label}: thread absence has no positive companion capture evidence")
            elif not case["rows"]:
                reasons.append(f"{label}: no matching events yet")
            if any(not c["observed"] for c in case["checks"]):
                reasons.append(f"{label}: required observations missing (arrival/completeness unknown)")
            if case.get("capability_gaps"):
                reasons.append(f"{label}: startup capabilities limited: " + "; ".join(case["capability_gaps"]))
            reasons.extend(f"{label}: {warning}" for warning in case.get('warnings', []))
        if run.get("stimulusOnly"):
            reasons.append("Stimulus completed only; not a capture-validation PASS")
    # Report-only trace success is green for trace scope, never pipeline scope.
    state = "red" if red else "yellow" if reasons else "green"
    return dict(state=state, reasons=reasons, cases=cases,
                harness=status, coverage="trace report only" if trace_only else "gaps/pending" if reasons else "observed",
                scope="actual-object trace" if trace_only else "harness + selected telemetry observations")


def mark_overlaps(runs, evaluations, padding=15):
    """Warn on potentially shared same-host PID/time observations, never certify them."""
    intervals = []
    for run in runs:
        for selector in run["selectors"]:
            if selector["domain"] == "host":
                continue
            try:
                start = dt.datetime.fromisoformat((selector.get("startedAtUtc") or run["startedAtUtc"]).replace("Z", "+00:00"))
                end = dt.datetime.fromisoformat((selector.get("completedAtUtc") or run["completedAtUtc"]).replace("Z", "+00:00"))
                pids = {int(p) for p in selector.get("pids", []) + selector.get("threadIds", [])}
                intervals.append((run, selector["domain"], start.timestamp() - padding, end.timestamp() + padding, pids))
            except (ValueError, KeyError, TypeError):
                continue
    for i, (run, domain, start, end, pids) in enumerate(intervals):
        for other, other_domain, other_start, other_end, other_pids in intervals[i + 1:]:
            if (run["runId"] != other["runId"] and run["host"]["hostname"].lower() == other["host"]["hostname"].lower()
                    and domain == other_domain and pids & other_pids and start <= other_end and other_start <= end):
                for value in (run, other):
                    evaluation = evaluations.get((value["test"], value["runId"]))
                    if evaluation is None:
                        continue
                    reason = "Overlapping same-host runs share PID/time selectors; attribution may be ambiguous"
                    if reason not in evaluation["reasons"]:
                        evaluation["reasons"].append(reason)
                    if evaluation["state"] != "red":
                        evaluation["state"] = "yellow"
                    evaluation["coverage"] = "ambiguous"


def overview(runs, evaluations, hosts=None, history=False):
    """Latest per host/test by default; retain older runs in history view."""
    hosts = hosts or sorted({r["host"]["hostname"].lower() for r in runs})
    rows = []
    for host in hosts:
        for test, title in TESTS.items():
            candidates = sorted((r for r in runs if r["host"]["hostname"].lower() == host.lower() and r["test"] == test),
                                key=lambda r: r.get("startedAtUtc", ""), reverse=True)
            if not candidates:
                rows.append(dict(host=host, test=title, state="gray", reason="Not run / no evidence supplied", run_id="", test_key=test, harness="not run", coverage="unknown"))
            for run in candidates if history else candidates[:1]:
                evaluation = evaluations[(test, run["runId"])]
                rows.append(dict(host=host, test=title, state=evaluation["state"], reason="; ".join(evaluation["reasons"]) or f"Passed within {evaluation['scope']}",
                                 run_id=run["runId"], test_key=test, harness=evaluation["harness"], coverage=evaluation["coverage"]))
    return rows
