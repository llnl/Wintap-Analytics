"""Read-only boundary overlay for archived installed-host captures.

Historical logs without independently verified timezone stay unclassified.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

import duckdb

from collection_edges import report, unix_ns_to_filetime, TICKS_PER_SECOND


def clock_verified(round_):
    a, b = round_.get('clock_start', {}), round_.get('clock_end', {})
    keys = ('unix_ns', 'monotonic_ns', 'local_utc_offset_seconds', 'localtime_sha256')
    if any(key not in a or key not in b for key in keys):
        return False
    wall = b['unix_ns'] - a['unix_ns']
    mono = b['monotonic_ns'] - a['monotonic_ns']
    return (wall > 0 and mono > 0 and abs(wall-mono) < 1_000_000_000
            and a['localtime_sha256'] == b['localtime_sha256']
            and a['local_utc_offset_seconds'] == b['local_utc_offset_seconds']
            and a.get('harness_TZ') is None and b.get('harness_TZ') is None
            and 'collector_TZ' in round_ and round_['collector_TZ'] is None)


def sensor_bounds(log, sensor, round_):
    verified = clock_verified(round_)
    if not verified:
        return None
    offset = round_['clock_start']['local_utc_offset_seconds']
    markers = [f'Starting {sensor} sensor...', f'{sensor} sensor started',
               f'Stopping {sensor} sensor...', f'{sensor} sensor stopped']
    stamps = []
    for marker in markers:
        lines = [line for line in log.splitlines() if line.endswith(marker)]
        if len(lines) != 1:
            return None
        parsed = dt.datetime.strptime(lines[0][:19], '%m/%d/%Y %H:%M:%S')
        utc = parsed.replace(tzinfo=dt.timezone(dt.timedelta(seconds=offset)))
        epoch = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
        delta = utc - epoch
        ns = (delta.days*86400 + delta.seconds)*1_000_000_000
        stamps.append(unix_ns_to_filetime(ns))
    if (stamps[0] < unix_ns_to_filetime(round_['clock_start']['unix_ns']) - TICKS_PER_SECOND
            or stamps[3] > unix_ns_to_filetime(round_['clock_end']['unix_ns'])):
        return None
    # Log timestamps truncate to seconds, so upper bounds include that second.
    return dict(start_min=stamps[0], start_max=stamps[1]+TICKS_PER_SECOND,
                end_min=stamps[2], end_max=stamps[3]+TICKS_PER_SECOND,
                clock_verified=True, source=f'BaseEbpfSensor {sensor} Start/Stop log brackets',
                evidence_kind='operational_envelope_not_delivery_guarantee')


def analyze_round(round_, qa, data, strict_gates, endpoint_results=(), pressure_endpoint_results=None):
    log = (qa / round_['name'] / 'runtime-snapshot/Logs/Lintap.log').read_text()
    root = data / round_['name'] / 'raw_sensor'
    bounds = {s: sensor_bounds(log, s, round_) for s in ('FileOps', 'Network')}
    sentinel = None
    # QA oracle imported, never substitutes for production identity computation.
    from experiment_live_analysis import digest
    host = json.loads((qa / 'host-provenance.json').read_text())['hostname']
    sentinel = digest(host.upper(), -1, 0)
    with duckdb.connect(':memory:') as c:
        rows = c.execute('''select firstseen,lastseen,pidhash,processname,file_path,
                         coalesce(eventcount,0) from read_parquet(?,union_by_name=true)''',
                         [str(root / 'raw_process_file/**/*.parquet')]).fetchall()
        known = {r[0] for r in c.execute('select distinct pidhash from read_parquet(?)',
                                       [str(root / 'raw_process/**/*.parquet')]).fetchall()}
    files = []
    for first, last, identity, name, path, count in rows:
        files.append(dict(first=first, last=last, counts=dict(file_rows=1, file_events=int(count),
            unresolved_rows=int(identity == sentinel or (name or '').lower().startswith('unknown')),
            known_hash_orphan_rows=int(identity not in known and identity != sentinel))))
    workload = round_['workload']
    # Classify missing paths by the proven overall stimulus interval, not birth,
    # reap time, filesystem mtime or synthetic telemetry time.
    recorded = {str(r[4]) for r in rows}
    events_by_path = {}
    for row in rows:
        events_by_path[str(row[4])] = events_by_path.get(str(row[4]), 0) + int(row[5])
    truth = []
    missing_paths = 0
    for child in workload['children']:
        for i in range(child.get('payload_files', 0)):
            directory = (str(child['pid']) if round_.get('shutdown_window') else
                         f"{child['cohort']}-{child['pid']}")
            expected = str(Path(round_['qa_root']) / 'workload/payload' / directory / f'file-{i}.txt')
            missing = int(expected not in recorded)
            missing_paths += missing
            truth.append(dict(first=unix_ns_to_filetime(workload['start_unix_ns'])
                              if 'start_unix_ns' in workload else None,
                              last=unix_ns_to_filetime(workload['end_unix_ns'])
                              if 'end_unix_ns' in workload else None,
                              counts=dict(expected_paths=1, missing_paths=missing,
                                  missing_payload_events=max(0,7-events_by_path.get(expected,0)),
                                  excess_payload_events=max(0,events_by_path.get(expected,0)-7))))
    interval_a, interval_b = round_.get('endpoint_interval_start'), round_.get('endpoint_interval_end')
    by_case = {row['case']: row for row in endpoint_results}
    endpoints = []
    for selector in round_['endpoint_selectors']:
        observed = by_case.get(selector['case'])
        endpoints.append(dict(first=unix_ns_to_filetime(interval_a['unix_ns']) if interval_a else None,
                              last=unix_ns_to_filetime(interval_b['unix_ns']) if interval_b else None,
                              counts=dict(endpoint_cases=1,
                                  endpoint_failed_cases=int(observed is not None and observed['status']!='passed'),
                                  endpoint_missing_observations=len(observed.get('missing',[])) if observed else 0,
                                  endpoint_violations=len(observed.get('violations',[])) if observed else 0)))
    result = dict(name=round_['name'], clock_verified=clock_verified(round_),
                  strict_gates=strict_gates, files=report(files,bounds['FileOps']),
                  missing_paths_stimulus_interval=report(truth,bounds['FileOps']),
                  endpoint_stimulus_interval=report(endpoints,bounds['Network']),
                  missing_paths_total=missing_paths,
                  loss_fate_not_inferred_from_event_time=True)
    if 'pressure_endpoint_selectors' in round_:
        by_case = {row['case']:row for row in (pressure_endpoint_results or [])}
        pressure = []
        for selector in round_['pressure_endpoint_selectors']:
            observed = by_case.get(selector['case'])
            pressure.append(dict(first=unix_ns_to_filetime(workload['start_unix_ns']),
                last=unix_ns_to_filetime(workload['end_unix_ns']),
                counts=dict(endpoint_cases=1,endpoint_failed_cases=int(observed is None or observed['status']!='passed'),
                    endpoint_missing_observations=len(observed.get('missing',[])) if observed else 0,
                    endpoint_violations=len(observed.get('violations',[])) if observed else 0)))
        result['pressure_endpoint_stimulus_interval'] = report(pressure,bounds['Network'])
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--analysis', type=Path, required=True)
    p.add_argument('--qa-parent', type=Path, required=True)
    p.add_argument('--data-parent', type=Path, required=True)
    p.add_argument('--bundle-name', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    original = json.loads(args.analysis.read_text())
    result = dict(hosts=[], primary_width_seconds=10, strict_results_preserved=True)
    for host in original['hosts']:
        qa = args.qa_parent / host['host'] / args.bundle_name
        session = json.loads((qa / 'session.json').read_text())
        strict = {r['name']:r for r in host['rounds']}
        result['hosts'].append(dict(host=host['host'], rounds=[
            analyze_round(r,qa,args.data_parent/host['host'],strict[r['name']]['gates'],
                          strict[r['name']]['endpoint_cases'])
            for r in session['rounds']]))
    args.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
