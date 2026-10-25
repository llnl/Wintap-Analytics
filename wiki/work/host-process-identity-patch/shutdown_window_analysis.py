"""Read-only oracle for captured shutdown-window events, not post-stop completeness."""
import argparse
import json
from pathlib import Path

import duckdb
from experiment_live_analysis import analyze, digest


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--qa-root', type=Path, required=True)
    p.add_argument('--data-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    session = json.loads((args.qa_root / 'session.json').read_text())
    host = json.loads((args.qa_root / 'host-provenance.json').read_text())['hostname']
    result = dict(session=session, rounds=[])
    for r in session['rounds']:
        a = analyze(r, args.qa_root, args.data_root, strict=False)
        root = args.data_root / r['name'] / 'raw_sensor'
        with duckdb.connect(':memory:') as c:
            for short, table in [('p', 'raw_process'), ('f', 'raw_process_file')]:
                c.execute(f'create table {short} as select * from read_parquet(?,union_by_name=true)',
                          [str(root / table / '**/*.parquet')])
            c.execute('create table truth(pid integer)')
            c.executemany('insert into truth values (?)', [(r['pid'],) for r in r['workload']['children']])
            sql = '''select f.pid,f.pidhash,count(*) file_rows,sum(eventcount) events,
                     min(firstseen) firstseen,max(lastseen) lastseen,
                     exists(select 1 from p where p.pidhash=f.pidhash) lifecycle_linked
                     from f join truth using(pid) group by f.pid,f.pidhash order by f.pid'''
            cur = c.execute(sql)
            a['captured_pid_identities'] = [dict(zip([d[0].lower() for d in cur.description], row)) for row in cur.fetchall()]
            sigterm_filetime = 116444736000000000 + r['workload']['sigterm_unix_ns'] // 100
            cur = c.execute('''select count(*) file_rows, count(distinct f.pid) pids,
                               coalesce(sum(eventcount),0) events from f join truth using(pid)
                               where firstseen >= ?''', [sigterm_filetime])
            a['captured_after_sigterm'] = dict(zip([d[0].lower() for d in cur.description], cur.fetchone()))
        unknown = digest(host.upper(), -1, 0)
        rows = a['captured_pid_identities']
        a['known_hash_orphan_rows'] = sum(row['file_rows'] for row in rows if row['pidhash'] != unknown and not row['lifecycle_linked'])
        a['unresolved_file_rows'] = sum(row['file_rows'] for row in rows if row['pidhash'] == unknown)
        a['stimulus_has_captured_file_events'] = bool(rows)
        # Expected absence after the FileOps cutoff is NOT sensor loss.
        a['post_stop_conservation_not_applicable'] = True
        log = (args.qa_root / r['name'] / 'runtime-snapshot/Logs/Lintap.log').read_text()
        a['shutdown_sensor_lines'] = [line for line in log.splitlines() if ' sensor...' in line and 'Stopping ' in line or 'sensor stopped' in line]
        dependent_done = [log.find(sensor + ' sensor stopped') for sensor in ('Network', 'FileOps')]
        identity_begin = [log.find('Stopping ' + sensor + ' sensor...') for sensor in ('ExecveProcess', 'CloneProcess', 'ExitProcess')]
        a['dependent_stops_precede_identity_stop'] = all(i >= 0 for i in dependent_done + identity_begin) and max(dependent_done) < min(identity_begin)
        a['acceptance_gates'] = dict(
            graceful=a['gates']['graceful_without_harness_interruption'],
            captured_stimulus_not_vacuous=bool(rows),
            captured_shutdown_window_not_vacuous=a['captured_after_sigterm']['pids'] > 0,
            all_captured_files_canonical=a['gates']['every_file_row_canonical'],
            no_known_hash_orphans=a['known_hash_orphan_rows'] == 0,
            no_unresolved_captured_files=a['unresolved_file_rows'] == 0,
            no_event_time_fabrication=a['gates']['no_event_time_identity_substitutes'])
        if '-ordered-' in r['name']:
            a['acceptance_gates']['logged_stop_order'] = a['dependent_stops_precede_identity_stop']
        result['rounds'].append(a)
        print(json.dumps(dict(name=r['name'], captured_pids=len(rows),
                              known_orphans=a['known_hash_orphan_rows'], unresolved=a['unresolved_file_rows'],
                              gates=a['acceptance_gates'])))
    result['installed_service_unchanged'] = session.get('installed_service_before') == session.get('installed_service_after')
    ordered = [r for r in result['rounds'] if '-ordered-' in r['name']]
    baseline = [r for r in result['rounds'] if '-baseline-' in r['name']]
    result['ordered_all_three_rounds_pass'] = len(ordered) == 3 and all(all(r['acceptance_gates'].values()) for r in ordered)
    result['baseline_reproduces_shutdown_attribution_gap'] = len(baseline) == 3 and any(
        r['unresolved_file_rows'] or r['known_hash_orphan_rows'] for r in baseline)
    args.output.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
