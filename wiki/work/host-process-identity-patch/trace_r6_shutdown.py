"""Read-only reconstruction of revision-6 shutdown unknowns; not retry-time proof."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import duckdb
from experiment_live_analysis import digest


def final_lifetime_contains_files(records, canonical_start, first, last):
    """Require the exact identity birth and both file bounds, not just the tail."""
    if canonical_start is None or first > last:
        return False
    epoch = dt.datetime(1601, 1, 1)
    start = epoch + dt.timedelta(microseconds=canonical_start // 10)
    first_date = epoch + dt.timedelta(microseconds=first // 10)
    last_date = epoch + dt.timedelta(microseconds=last // 10)
    return any(created == start and exited is not None
               and created <= first_date <= last_date <= exited
               for _, _, created, exited, _ in records)


def snapshot_fingerprints(snapshot):
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (snapshot, Path(str(snapshot) + '.wal')) if path.exists()}


def main():
    work = Path(__file__).parent
    analysis = json.loads((work / 'package_r6_shutdown_analysis.json').read_text())
    qa = Path('/private/var/folders/gj/mckt0dsj0xv2vwr1jd1wv8nc0004ys/T/opencode/r6-shutdown')
    data = Path('/Users/johnson30/git/axon-aegis-micro-range/data/lintap/quality-installed-20261024-r6-shutdown')
    output = dict(rounds=[], historical_unchanged=analysis['historical_database_size_mtime_unchanged'])
    for host in analysis['hosts']:
        for result, session in zip(host['rounds'], host['session']['rounds']):
            host_qa = qa / host['host'] / 'quality-installed-20261024-r6-shutdown'
            provenance = json.loads((host_qa / 'host-provenance.json').read_text())
            birth = {r['pid']: 116444736000000000 + provenance['boot_unix_seconds'] * 10_000_000
                     + r['start_ticks'] * 10_000_000 // r['clock_ticks']
                     for r in session['workload']['children']}
            shadow = [json.loads(line) for line in
                      (host_qa / result['name'] / 'lifetime-shadow.jsonl').read_text().splitlines()]
            row = dict(host=host['host'], name=result['name'],
                       gates=result['acceptance_gates'], whole=result['whole_capture_quality'],
                       captured_after_sigterm_pids=result['captured_shutdown_window_pids'],
                       shutdown_seconds=result['shutdown_seconds'],
                       retry_receipts=result['retry_cumulative_receipts'], traces=[])
            root = data / host['host'] / result['name'] / 'raw_sensor'
            snapshot = host_qa / result['name'] / 'runtime-snapshot/event_store/main.pid-v2.duckdb'
            before = snapshot_fingerprints(snapshot)
            # Matching preserved WAL is replayed read-only on a copied snapshot.
            with duckdb.connect(':memory:') as c, duckdb.connect(str(snapshot), read_only=True) as resolver:
                c.execute('create table f as select * from read_parquet(?,union_by_name=true)',
                          [str(root / 'raw_process_file/**/*.parquet')])
                c.execute('create table p as select * from read_parquet(?,union_by_name=true)',
                          [str(root / 'raw_process/**/*.parquet')])
                unknowns = c.execute('''select pid,count(*),sum(eventcount),min(firstseen),max(lastseen)
                    from f where pidhash=? group by pid order by pid''',
                    [digest(host['host'].upper(), -1, 0)]).fetchall()
                for pid, rows, events, first, last in unknowns:
                    expected = digest(host['host'].upper(), pid, birth[pid]) if pid in birth else None
                    lifecycle = c.execute('''select activitytype,eventtime,pidhash,receivetime
                        from p where pid=? order by eventtime''', [pid]).fetchall()
                    starts = [event for activity, event, key, _ in lifecycle
                              if activity in ('Start', 'Refresh') and key == expected]
                    stops = [event for activity, event, key, _ in lifecycle
                             if activity == 'Stop' and key == expected]
                    records = resolver.execute('''select process_id,pid_hash,create_time,exit_time,source
                        from process where process_id=? and pid_hash=?''', [pid, expected]).fetchall()
                    row['traces'].append(dict(pid=pid, rows=rows, events=events, first_seen=first,
                        last_seen=last, canonical_start=birth.get(pid), expected_hash=expected,
                        lifecycle=lifecycle, captured_lifetime_contains_files=bool(starts and stops)
                        and min(starts) <= first <= last <= max(stops),
                        shadow=[r for r in shadow if r.get('Pid') == pid], resolver_records=records,
                        final_resolver_contains_files=final_lifetime_contains_files(
                            records, birth.get(pid), first, last)))
            row['snapshot_hashes'] = before
            row['snapshot_and_wal_unchanged'] = before == snapshot_fingerprints(snapshot)
            if not row['snapshot_and_wal_unchanged']:
                raise RuntimeError('Read-only resolver snapshot changed during analysis')
            row['unknown_rows'] = sum(t['rows'] for t in row['traces'])
            row['unknown_events'] = sum(t['events'] for t in row['traces'])
            row['affected_pids'] = len(row['traces'])
            # No affected rows means not applicable, not proof of recovery.
            row['all_unknowns_have_captured_containing_lifetimes'] = all(
                t['captured_lifetime_contains_files'] for t in row['traces']) if row['traces'] else None
            row['all_unknowns_have_final_resolver_lifetimes'] = all(
                t['final_resolver_contains_files'] for t in row['traces']) if row['traces'] else None
            output['rounds'].append(row)
            print(json.dumps({k: v for k, v in row.items() if k not in ('traces', 'retry_receipts')}))
    archives = [qa.parent / f'{host}-r6-shutdown-evidence.tgz' for host in ('axon', 'caldera')]
    archives += [data.parent / f'{host}-r6-shutdown-data.tgz' for host in ('axon', 'caldera')]
    output['archive_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in archives}
    (work / 'package_r6_shutdown_summary.json').write_text(json.dumps(output, indent=2, default=str) + '\n')


if __name__ == '__main__':
    main()
