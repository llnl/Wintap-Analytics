"""Read-only pressure envelope rollup. No inference from absent/failed experiments."""
import argparse
from collections import Counter
import json
from pathlib import Path

from shutdown_delivery_experiment import HERE, TEMP


def summarize(revisions):
    experiments = []
    for revision in revisions:
        root = TEMP / f'r{revision}-shutdown-evidence'
        expanded = HERE / f'package_r{revision}_pressure_expanded.json'
        checked = HERE / f'package_r{revision}_pressure_scope_checked.json'
        source = checked if checked.exists() else expanded if expanded.exists() else HERE / f'package_r{revision}_pressure_controls.json'
        analysis = json.loads(source.read_text())
        spec = json.loads((root / 'pressure-spec.json').read_text())
        downstream_path = HERE / f'package_r{revision}_pressure_dbt.json'
        downstream = json.loads(downstream_path.read_text()) if downstream_path.exists() else []
        rounds = []
        for host in analysis['hosts']:
            session = json.loads((root / 'analysis' / host['host'] / 'qa/session.json').read_text())
            for row in host['rounds']:
                control = next(r for r in session['rounds'] if r['name'] == row['name'])
                workload = control['workload']
                trace = row.get('trace', {})
                dbt = next((r for r in downstream if r['host'] == host['host'] and r['round'] == row['name']), None)
                run_results = root / 'fresh-dbt' / host['host'] / row['name'] / 'project/target/run_results.json'
                nodes = json.loads(run_results.read_text())['results'] if run_results.exists() else []
                node_status = dict(Counter(r['status'] for r in nodes))
                rounds.append(dict(host=host['host'],round=row['name'], children=workload['expected_children'],
                    payload=row['payload'],raw_gates=row['gates'],whole_capture=row['whole_capture'],
                    workload_duration_seconds=(workload['end_unix_ns']-workload['start_unix_ns'])/1e9,
                    child_io_span_seconds=(max(c['before_exit_monotonic_ns'] for c in workload['children'])-
                        min(c['callback_begin_monotonic_ns'] for c in workload['children']))/1e9,
                    workload_to_stop_seconds=(control['stop_request_clock']['monotonic_ns']-
                        control['workload_interval_end']['monotonic_ns'])/1e9,
                    payload_stimulus_bands=row['collection_edges']['missing_paths_stimulus_interval']['bands'],
                    pressure_endpoint_stimulus_bands=row['collection_edges'].get('pressure_endpoint_stimulus_interval',{}).get('bands'),
                    whole_file_bands=row['collection_edges']['files']['bands'],resources=row['resources'],
                    pressure_endpoint_pairs=len(row['pressure_endpoints']),
                    pressure_failed_endpoint_pairs=sum(x['status']!='passed' for x in row['pressure_endpoints']),
                    trace_counts=trace.get('summary',{}).get('Counts'),trace_gates=trace.get('gates'),
                    tcp_stage_count_joins=trace.get('tcp_stage_count_joins'),
                    tcp_delivery_exact_row_id_joins=trace.get('tcp_delivery_row_id_joins'),
                    retry_stage_counts=row.get('pressure_retry_receipts'),
                    sampled_pending_peak=row.get('pressure_observed_peak_pending'),
                    retry_failure_receipts=row.get('pressure_failure_receipts'),
                    dbt_gates=dbt['gates'] if dbt else None,
                    dbt_exit_code=dbt['dbt_exit_code'] if dbt else None,dbt_node_statuses=node_status,
                    host_memory=row.get('host_memory'),known_os_label=dbt.get('known_os_family_defect') if dbt else None))
        accepted = (len(rounds)==4 and len(downstream)==4 and all(
            all(r['raw_gates'].values()) and (r['trace_gates'] is None or all(r['trace_gates'].values())) and
            r['dbt_exit_code']==0 and r['dbt_gates'] and all(r['dbt_gates'].values()) for r in rounds))
        experiments.append(dict(revision=revision,**spec,analysis_receipt=str(source),accepted=accepted,
            rounds=rounds,archive_receipts=json.loads((root / 'archive-receipts.json').read_text())))
    return dict(experiments=experiments,all_requested_gates_passed=all(e['accepted'] for e in experiments),
        total_children=sum(r['children'] for e in experiments for r in e['rounds']),
        total_payload_paths=sum(r['payload']['paths'] for e in experiments for r in e['rounds']),
        total_payload_events=sum(r['payload']['events'] for e in experiments for r in e['rounds']),
        source_correction_made=False,capacity_changed=False,historical_failures_resolved=False,
        complete_kernel_delivery_proven=False,durable_fate_proven=False,production_sizing_accepted=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revisions',nargs='+',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(args.revisions)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='experiments'}))


if __name__=='__main__':
    main()
