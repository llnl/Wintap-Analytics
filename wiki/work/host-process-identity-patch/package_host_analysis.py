"""Read-only Mac oracles for installed package captures, including failed gates."""
import argparse
import json
import re
from pathlib import Path
import sys

import duckdb
from experiment_live_analysis import analyze, digest
from collector_process_analysis import collector_checks

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'wintap' / 'devtools'))
from network_endpoint_smoke_test import read_rows, validate_rows


def retry_receipts(log):
    receipts, errors = [], []
    fields = {'scheduled', 'capacity_refused', 'stopped_refused', 'exhausted',
              'invoked', 'callback_errors', 'shutdown_invoked', 'pending', 'high_water'}
    marker = 'Attribution retry cumulative: '
    for line in log.splitlines():
        if marker not in line:
            continue
        try:
            parts = line.split(marker, 1)[1].split(',')
            row = dict(part.split('=', 1) for part in parts)
            if len(row) != len(parts) or set(row) != fields | {'stream'}:
                raise ValueError('Unexpected retry receipt fields')
            for key in fields:
                row[key] = int(row[key])
                if row[key] < 0:
                    raise ValueError('Negative cumulative retry counter')
            receipts.append(row)
        except ValueError as exc:
            errors.append(dict(line=line, error=str(exc)))
    return receipts, errors


def retry_configurations(log):
    receipts, errors = [], []
    marker = 'Attribution retry configuration: '
    pattern = r'capacity=(\d+),max_attempts=(\d+),interval_ms=(\d+),experimental_capacity=(True|False)'
    for line in log.splitlines():
        if marker not in line:
            continue
        match = re.fullmatch(pattern, line.split(marker, 1)[1])
        if match is None:
            errors.append(line)
        else:
            receipts.append(dict(capacity=int(match[1]), max_attempts=int(match[2]),
                                 interval_ms=int(match[3]), experimental_capacity=match[4] == 'True'))
    return receipts, errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--qa-parent', type=Path, required=True)
    p.add_argument('--data-parent', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--bundle-name', default='quality-installed-20261024-r2')
    p.add_argument('--hosts', nargs='+', choices=['axon-target', 'caldera-host'],
                   default=['axon-target', 'caldera-host'])
    p.add_argument('--require-retry-receipts', action='store_true',
                    help='Require complete default-stream cumulative receipts for the diagnostic candidate')
    p.add_argument('--require-collector-process', action='store_true',
                   help='Require independently canonical normal collector process telemetry')
    args = p.parse_args()
    result = dict(hosts=[])
    agents = []
    for host in args.hosts:
        qa = args.qa_parent / host / args.bundle_name
        session = json.loads((qa / 'session.json').read_text())
        entry = dict(host=host, session=session, rounds=[])
        for r in session['rounds']:
            a = analyze(r, qa, args.data_parent / host, strict=False)
            root = args.data_parent / host / r['name'] / 'raw_sensor'
            rows, error = read_rows(root, r['endpoint_selectors'])
            a['endpoint_query_error'] = error
            a['endpoint_cases'] = [validate_rows(rows, s) for s in r['endpoint_selectors']]
            with duckdb.connect(':memory:') as c:
                c.execute('create table process as select * from read_parquet(?, union_by_name=true)',
                          [str(root / 'raw_process' / '**/*.parquet')])
                if args.require_collector_process:
                    a['collector_process'] = collector_checks(c, r['collector_provenance'],
                        json.loads((qa / 'host-provenance.json').read_text()), r['agent_state']['AgentId'])
                    a['gates'].update(a['collector_process']['gates'])
                expected = {row['pid_hash'] for row in rows}
                recorded = {row[0] for row in c.execute('select distinct pidhash from process').fetchall()}
                a['endpoint_hashes_link_to_process'] = bool(expected) and expected <= recorded
                a['raw_host_agents'] = c.execute('select distinct Hostname,AgentId from read_parquet(?,union_by_name=true)',
                                                [str(root / 'raw_host' / '**/*.parquet')]).fetchall()
                c.execute('create table files as select * from read_parquet(?,union_by_name=true)',
                          [str(root / 'raw_process_file' / '**/*.parquet')])
                if args.require_collector_process:
                    a['collector_process']['self_file_rows'] = c.execute(
                        'select count(*) from files where pid=?', [r['collector_provenance']['pid']]).fetchone()[0]
                    a['gates']['collector_self_file_feedback_suppressed'] = a['collector_process']['self_file_rows'] == 0
                sentinel = digest(host.upper(), -1, 0)
                a['whole_capture_quality'] = dict(
                    process_observations=c.execute('select count(*) from process').fetchone()[0],
                    known_process_identities=c.execute('select count(distinct pidhash) from process where pidhash != ?', [sentinel]).fetchone()[0],
                    unresolved_process_observations=c.execute('select count(*) from process where pidhash = ?', [sentinel]).fetchone()[0],
                    file_rows=c.execute('select count(*) from files').fetchone()[0],
                    unresolved_file_rows=c.execute('select count(*) from files where pidhash = ?', [sentinel]).fetchone()[0],
                    known_identity_file_orphan_rows=c.execute('select count(*) from files f where pidhash != ? and not exists(select 1 from process p where p.pidhash=f.pidhash)', [sentinel]).fetchone()[0],
                    unknown_named_file_rows=c.execute("select count(*) from files where lower(processname) like 'unknown%'").fetchone()[0])
                if r.get('shutdown_window'):
                    c.execute('create table truth(pid integer)')
                    c.executemany('insert into truth values (?)', [(child['pid'],) for child in r['workload']['children']])
                    sigterm_ft = 116444736000000000 + r['workload']['sigterm_unix_ns'] // 100
                    a['captured_shutdown_window_pids'] = c.execute(
                        'select count(distinct pid) from files join truth using(pid) where firstseen>=?', [sigterm_ft]).fetchone()[0]
            a['service_before'] = r['service_before']
            a['service_after'] = r['service_after']
            a['shutdown_seconds'] = r['shutdown_seconds']
            monitor = qa / r['name'] / 'monitor.jsonl'
            if monitor.exists():
                samples = [json.loads(line) for line in monitor.read_text().splitlines()]
                first, last = samples[0], samples[-1]
                elapsed = (last['monotonic_ns'] - first['monotonic_ns']) / 1e9
                clock_ticks = r['workload']['children'][0]['clock_ticks']
                a['monitor_summary'] = dict(samples=len(samples), observed_seconds=elapsed,
                    collector_pids=sorted({s['pid'] for s in samples}),
                    rss_first_kib=first['rss_kib'], rss_last_kib=last['rss_kib'],
                    rss_min_kib=min(s['rss_kib'] for s in samples),
                    rss_max_kib=max(s['rss_kib'] for s in samples),
                    thread_count_min=min(s['threads'] for s in samples),
                    thread_count_max=max(s['threads'] for s in samples),
                    native_free_bytes_min=min(s['native_free_bytes'] for s in samples),
                    core_summed_cpu_percent=(last['cpu_ticks']-first['cpu_ticks'])/clock_ticks/elapsed*100,
                    stimulus_segments=len(r['workload']['segments']),
                    soak_elapsed_seconds=r['workload']['soak_elapsed_seconds'])
                a['gates']['full_30_minute_soak'] = r['workload']['soak_elapsed_seconds'] >= 1800
                a['gates']['twenty_stimulus_segments'] = len(r['workload']['segments']) == 20
                a['gates']['one_collector_pid'] = len(a['monitor_summary']['collector_pids']) == 1
                a['gates']['no_service_restarts'] = 'NRestarts=0\n' in r['service_after']
            a['gates']['endpoint_orientation'] = error is None and all(x['status'] == 'passed' for x in a['endpoint_cases'])
            a['gates']['endpoint_process_linkage'] = a['endpoint_hashes_link_to_process']
            log = (qa / r['name'] / 'runtime-snapshot/Logs/Lintap.log').read_text()
            a['retry_cumulative_receipts'], a['retry_receipt_errors'] = retry_receipts(log)
            a['retry_configuration_receipts'], a['retry_configuration_errors'] = retry_configurations(log)
            if 'WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY' in r['env_overrides']:
                capacity = int(r['env_overrides']['WINTAP_EXPERIMENT_ATTRIBUTION_RETRY_CAPACITY'])
                a['gates']['effective_retry_configuration'] = not a['retry_configuration_errors'] and a['retry_configuration_receipts'] == [
                    dict(capacity=capacity, max_attempts=10, interval_ms=1000, experimental_capacity=capacity != 1024)]
            if args.require_retry_receipts:
                receipts = a['retry_cumulative_receipts']
                a['gates']['retry_receipts_complete'] = not a['retry_receipt_errors'] and len(receipts) == 4 and {
                    d['stream'] for d in receipts} == {'Registry', 'File', 'TcpConnection', 'UdpPacket'}
                a['gates']['retry_final_pending_zero'] = bool(receipts) and all(d['pending'] == 0 for d in receipts)
                a['gates']['retry_callbacks_without_error'] = bool(receipts) and all(d['callback_errors'] == 0 for d in receipts)
            if r.get('shutdown_window'):
                a['post_stop_conservation_not_applicable'] = True
                log = (qa / r['name'] / 'runtime-snapshot/Logs/Lintap.log').read_text()
                dependent_done = [log.find(sensor + ' sensor stopped') for sensor in ('Network', 'FileOps')]
                identity_begin = [log.find('Stopping ' + sensor + ' sensor...') for sensor in ('ExecveProcess', 'CloneProcess', 'ExitProcess')]
                a['logged_dependent_stops_before_identity'] = all(i >= 0 for i in dependent_done + identity_begin) and max(dependent_done) < min(identity_begin)
                a['acceptance_gates'] = {key: value for key, value in a['gates'].items()
                    if key not in ('all_expected_paths', 'exact_payload_event_conservation')}
                a['acceptance_gates'].update(
                    captured_shutdown_window_not_vacuous=a['captured_shutdown_window_pids'] > 0,
                    logged_dependent_stops_before_identity=a['logged_dependent_stops_before_identity'],
                    no_whole_capture_unresolved_files=a['whole_capture_quality']['unresolved_file_rows'] == 0,
                    no_whole_capture_known_hash_file_orphans=a['whole_capture_quality']['known_identity_file_orphan_rows'] == 0)
            entry['rounds'].append(a)
        observed = [r['agent_state']['AgentId'] for r in session['rounds']]
        entry['identity_persisted_across_rounds'] = len(set(observed)) == 1
        if args.require_collector_process:
            identities = [r['collector_process']['expected_pid_hash'] for r in entry['rounds']]
            entry['collector_restart_identities_distinct'] = len(set(identities)) == len(identities) and len(identities) > 1
        entry['state_matches_all_raw_host_agents'] = all(
            a['raw_host_agents'] and all(agent == observed[0] for _, agent in a['raw_host_agents'])
            for a in entry['rounds'])
        agents.append(observed[0])
        result['hosts'].append(entry)
    result['hosts_have_distinct_agents'] = len(set(agents)) == 2 if len(agents) == 2 else None
    baseline = json.loads(Path(__file__).with_name('package_sample_baseline.json').read_text())
    sample = Path(baseline['path']).stat()
    result['historical_database_size_mtime_unchanged'] = (sample.st_size, sample.st_mtime_ns) == (baseline['size'], baseline['mtime_ns'])
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    for host in result['hosts']:
        for r in host['rounds']:
            print(json.dumps(dict(host=host['host'], round=r['name'], payload=r['payload_paths']['rows'],
                                  hashes=r['independent_hash_oracle'], gates=r.get('acceptance_gates', r['gates']))))


if __name__ == '__main__':
    main()
