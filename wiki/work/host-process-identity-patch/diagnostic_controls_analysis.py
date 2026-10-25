"""Independent integer identity/conservation and trace/output gates for private controls."""
import argparse
import json
from pathlib import Path
import sys

import duckdb
from delivery_trace_analysis import analyze_trace
from experiment_live_analysis import digest
from collection_edge_analysis import analyze_round
from collector_process_analysis import collector_checks
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'wintap' / 'devtools'))
from network_endpoint_smoke_test import read_rows, validate_rows


def analyze_host(root):
    qa, data = root / 'qa', root / 'data'
    session = json.loads((qa / 'session.json').read_text())
    if (qa / 'host-provenance.json').exists():
        provenance = json.loads((qa / 'host-provenance.json').read_text())
        boot_evidence = 'capture-start host provenance'
    else:
        # Preserve the missing first-harness receipt. Never insert synthetic provenance into its archive.
        receipt = json.loads((root / 'archive-receipt.json').read_text())
        end = session['clock_end']; late = receipt['after_capture_clock']
        wall_delta = late['unix_ns'] - end['unix_ns']
        mono_delta = late['monotonic_ns'] - end['monotonic_ns']
        if wall_delta < 0 or mono_delta < 0 or abs(wall_delta - mono_delta) > 1_000_000_000:
            raise RuntimeError('Late boot receipt is not continuous with capture clocks')
        provenance = dict(hostname=session['hostname'], boot_unix_seconds=receipt['boot_unix_seconds'])
        boot_evidence = 'after-capture /proc btime with wall/monotonic continuity; not a start receipt'
    results = dict(host=session['hostname'], boot_evidence=boot_evidence, rounds=[],
        installed_controls_unchanged=session['installed_service_before'] == session['installed_service_after']
        and session['installed_dll_sha256'] == session['installed_dll_sha256_after']
        and session['agent_state_source_sha256'] == session['agent_state_source_sha256_after'])
    for round_ in session['rounds']:
        raw = data / round_['name'] / 'raw_sensor'
        boot_ft = 116444736000000000 + provenance['boot_unix_seconds'] * 10_000_000
        mapping = {child['pid']: digest(session['hostname'].strip().upper(), child['pid'],
            boot_ft + child['start_ticks'] * 10_000_000 // child['clock_ticks']) for child in round_['workload']['children']}
        result = dict(name=round_['name'], expected_paths=round_['workload']['expected_payload_files'],
            gates=dict(clean_exit=round_['collector_exit_code'] == 0 and not round_.get('forced_termination'),
                effective_environment=round_['verified_process_environment'] == round_['env_overrides']))
        with duckdb.connect(':memory:') as c:
            c.execute('create table process as select * from read_parquet(?,union_by_name=true)',
                      [str(raw / 'raw_process/**/*.parquet')])
            c.execute('create table files as select * from read_parquet(?,union_by_name=true)',
                      [str(raw / 'raw_process_file/**/*.parquet')])
            result['raw_host_agents'] = c.execute('select distinct Hostname,AgentId from files').fetchall()
            result['gates']['capture_is_host_isolated'] = bool(result['raw_host_agents']) and all(
                host.strip().upper() == session['hostname'].strip().upper()
                and agent == round_['agent_state']['AgentId'] for host, agent in result['raw_host_agents'])
            payload = c.execute("select File_Path,sum(EventCount) from files where contains(File_Path,'/workload/payload/') group by File_Path").fetchall()
            actual = dict(payload)
            expected = {str(Path(round_['qa_root']) / 'workload/payload' / f"{child['cohort']}-{child['pid']}" / f'file-{i}.txt')
                for child in round_['workload']['children'] for i in range(child['payload_files'])}
            result['payload'] = dict(paths=len(actual), events=sum(actual.values()),
                missing_paths=len(expected - actual.keys()), unexpected_paths=len(actual.keys() - expected),
                nonseven_event_paths={p: v for p, v in actual.items() if v != 7})
            result['gates'].update(exact_path_set=actual.keys() == expected,
                exact_per_path_conservation=bool(actual) and all(v == 7 for v in actual.values()))
            for table in ('process', 'files'):
                rows = c.execute(f'select PID,PidHash from {table}').fetchall()
                selected = [(pid, identity) for pid, identity in rows if pid in mapping]
                result[table + '_identity'] = dict(selected_rows=len(selected),
                    canonical_matches=sum(mapping[pid] == identity for pid, identity in selected))
                result['gates'][table + '_independent_identity'] = bool(selected) and all(mapping[pid] == identity for pid, identity in selected)
            sentinel = digest(session['hostname'].strip().upper(), -1, 0)
            result['whole_capture'] = dict(file_rows=c.execute('select count(*) from files').fetchone()[0],
                unresolved_rows=c.execute('select count(*) from files where pidhash=?', [sentinel]).fetchone()[0],
                known_hash_orphans=c.execute('select count(*) from files f where pidhash!=? and not exists(select 1 from process p where p.pidhash=f.pidhash)', [sentinel]).fetchone()[0])
            result['collector'] = collector_checks(c, round_['collector_provenance'], provenance, round_['agent_state']['AgentId'])
            result['gates'].update(result['collector']['gates'])
            result['gates']['collector_self_io_suppressed'] = c.execute('select count(*) from files where pid=?', [round_['collector_provenance']['pid']]).fetchone()[0] == 0
            rows, error = read_rows(raw, round_['endpoint_selectors'])
            result['endpoint_query_error'] = error
            result['endpoints'] = [validate_rows(rows, selector) for selector in round_['endpoint_selectors']]
            known = {r[0] for r in c.execute('select distinct PidHash from process').fetchall()}
            result['gates'].update(tcp_endpoint_orientation=not error and all(x['status'] == 'passed' for x in result['endpoints']),
                tcp_identity_linkage=bool(rows) and all(r['pid_hash'] in known for r in rows))
            trace = qa / round_['name'] / 'attribution.jsonl'
            if trace.exists():
                result['trace'] = analyze_trace(trace, c, raw)
            if 'pressure_phase' in round_:
                result['pressure_lifetimes'] = [dict(pid=child['pid'], pid_hash=mapping[child['pid']],
                    birth_filetime=boot_ft + child['start_ticks'] * 10_000_000 // child['clock_ticks'])
                    for child in round_['workload']['children']]
                result['pressure_phase'] = round_['pressure_phase']
                if 'memory_before' in round_:
                    result['host_memory'] = dict(before=round_['memory_before'],after=round_['memory_after'])
                    result['gates']['host_oom_counter_unchanged'] = round_['memory_before']['oom_kill_count'] == round_['memory_after']['oom_kill_count']
                result['gates']['pressure_generation_complete'] = round_['workload']['complete']
                selected_pids = set(mapping)
                for table in ('process', 'files'):
                    actual_pids = {r[0] for r in c.execute(f'select distinct PID from {table}').fetchall()}
                    result['gates'][table + '_all_pressure_children_observed'] = selected_pids <= actual_pids
                from pressure_endpoint_analysis import read_pressure_rows
                pressure_rows, error = read_pressure_rows(raw, round_['pressure_endpoint_selectors'], round_)
                result['pressure_endpoint_time_scope'] = 'exact capture UTC receipt bounds; TCP EPL FirstSeen=min(ReceiveTime),not kernel EventTime/stimulus completion'
                result['pressure_endpoints'] = [validate_rows(pressure_rows, s) for s in round_['pressure_endpoint_selectors']]
                result['gates']['pressure_tcp_all_endpoints'] = not error and len(result['pressure_endpoints']) == len(mapping) and all(
                    x['status'] == 'passed' for x in result['pressure_endpoints'])
                result['gates']['pressure_tcp_canonical_client_identity'] = bool(pressure_rows) and all(
                    mapping[row['pid']] == row['pid_hash'] for row in pressure_rows if row['pid'] in mapping)
                result['gates']['pressure_tcp_all_process_keys_recorded'] = bool(pressure_rows) and all(
                    row['pid_hash'] in known for row in pressure_rows)
                identities = {}
                for row in pressure_rows:
                    identities.setdefault(row['pid'],set()).add(row['pid_hash'])
                result['gates']['pressure_tcp_each_pid_single_identity'] = bool(identities) and all(
                    len(values)==1 for values in identities.values())
                result['pressure_endpoint_error'] = error
                result['gates']['whole_file_no_unknown_orphans'] = result['whole_capture']['unresolved_rows'] == result['whole_capture']['known_hash_orphans'] == 0
                if trace.exists():
                    from delivery_trace_analysis import load_trace
                    receipts, trace_info = load_trace(trace)
                    relevant = [r for r in receipts if r.get('Pid') in mapping]
                    result['pressure_receipt_stage_counts'] = dict(Counter(r.get('Stage') for r in relevant))
                    result['pressure_failure_receipts'] = [r for r in relevant if r.get('Stage') in (
                        'retry-capacity-refused', 'retry-stopped-refused', 'retry-exhausted', 'retry-callback-error')]
                    result['pressure_failure_absence_qualified'] = trace_info['scoped_observer_complete']
                    result['pressure_observed_peak_pending'] = max((r.get('Pending', 0) for r in relevant), default=0)
                    result['pressure_retry_receipts'] = dict(Counter(r.get('Stage') for r in relevant if r.get('Stage','').startswith('retry-')))
        snapshots = qa / round_['name'] / 'runtime-snapshot/Logs/Lintap.log'
        result['collection_edges'] = analyze_round(round_, qa, data, result['gates'], result['endpoints'],
            result.get('pressure_endpoints')) if snapshots.exists() else dict(status='unclassified', reason='First harness did not snapshot per-round runtime log or collector timezone')
        samples = round_['resource_samples']
        if samples:
            first, last = samples[0], samples[-1]
            elapsed = (last['clock']['monotonic_ns'] - first['clock']['monotonic_ns']) / 1e9
            result['resources'] = dict(samples=len(samples), observed_seconds=elapsed,
                peak_rss_kib=max((int(r['status']['VmRSS'].split()[0]) for r in samples if 'VmRSS' in r['status']), default=None),
                samples_without_rss=sum('VmRSS' not in r['status'] for r in samples),
                core_summed_cpu_percent=100 * ((last['utime_ticks'] + last['stime_ticks']) - (first['utime_ticks'] + first['stime_ticks'])) / session['cpu_clock_ticks'] / elapsed)
        results['rounds'].append(result)
    results['agent_id_stable'] = len({r['agent_state']['AgentId'] for r in session['rounds']}) == 1
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = dict(hosts=[analyze_host(args.root / host) for host in ('axon-target', 'caldera-host')])
    baseline = json.loads(Path(__file__).with_name('package_sample_baseline.json').read_text())
    stat = Path(baseline['path']).stat()
    results['historical_db_size_mtime_unchanged'] = (stat.st_size, stat.st_mtime_ns) == (baseline['size'], baseline['mtime_ns'])
    args.output.write_text(json.dumps(results, indent=2) + '\n')
    for host in results['hosts']:
        for round_ in host['rounds']:
            print(json.dumps(dict(host=host['host'], name=round_['name'], payload=round_['payload'], gates=round_['gates'],
                resources=round_.get('resources'), trace_gates=round_.get('trace', {}).get('gates'))))


if __name__ == '__main__':
    main()
