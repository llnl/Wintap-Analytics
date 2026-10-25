"""Build live canonical DBT models in a fresh temporary copy; never touch sample DB."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import duckdb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analysis', type=Path, required=True)
    parser.add_argument('--data-parent', type=Path, required=True)
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--full-build', action='store_true',
                        help='Build/test all canonical models rather than run only process-summary ancestors')
    parser.add_argument('--baseline-time-project', type=Path,
                        help='Use two retained pre-fix SQL files in the fresh project for a same-build control')
    parser.add_argument('--hosts', nargs='+', choices=['axon-target', 'caldera-host'],
                        default=['axon-target', 'caldera-host'])
    args = parser.parse_args()
    args.work_root.mkdir()
    wintappy = Path(__file__).resolve().parents[4] / 'Wintappy'
    analysis = json.loads(args.analysis.read_text())
    results = []
    for host in analysis['hosts']:
        if host['host'] not in args.hosts:
            continue
        for round_ in host['rounds']:
            root = args.work_root / host['host'] / round_['name']
            root.mkdir(parents=True)
            project = root / 'project'
            shutil.copytree(wintappy / 'wintap_dbt', project,
                            ignore=shutil.ignore_patterns('target', 'logs', 'dbt_packages', '.user.yml'))
            if args.baseline_time_project:
                for relative in ('macros/time.sql', 'models/silver/process_conn_incr.sql'):
                    shutil.copyfile(args.baseline_time_project / relative, project / relative)
            data = args.data_parent / host['host'] / round_['name']
            days = sorted(p.name.split('=', 1)[1] for p in (data / 'raw_sensor/raw_process').glob('dayPK=*'))
            if not days:
                raise RuntimeError('No actual recorded process partitions')
            db = root / 'collector.duckdb'
            env = os.environ.copy()
            env.update(WINTAP_DBT_DATABASE=str(db), WINTAP_DBT_DATASET=str(root),
                       WINTAP_DBT_RAW_SENSOR_DATASET=str(data), WINTAP_DBT_START_DAY=days[0],
                       WINTAP_DBT_END_DAY=days[-1], WINTAP_DBT_START_HOUR='', WINTAP_DBT_END_HOUR='')
            command = [str(wintappy / '.venv/bin/dbt'), 'build' if args.full_build else 'run',
                       '--project-dir', str(project), '--profiles-dir', str(project)]
            if not args.full_build:
                command += ['--select', '+process_summary']
            with (root / 'dbt.log').open('x') as log:
                run = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
            result = dict(host=host['host'], round=round_['name'], dbt_exit_code=run.returncode,
                          command=command, log=str(root / 'dbt.log'), models={}, gates={})
            collector = round_.get('collector_process') or round_['collector']
            expected = collector['expected_pid_hash']
            if run.returncode == 0:
                with duckdb.connect(str(db), read_only=True) as c:
                    for model, key in [('stg_raw_process', 'pidhash'), ('process', 'pid_hash'), ('process_summary', 'pid_hash')]:
                        cur = c.execute(f'select * from {model} where {key}=?', [expected])
                        result['models'][model] = [dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()]
                    result['gates'] = dict(
                        bronze_collector_retained=bool(result['models']['stg_raw_process']),
                        silver_collector_unique=len(result['models']['process']) == 1,
                        gold_collector_unique=len(result['models']['process_summary']) == 1)
                    for model in ('process', 'process_summary'):
                        actual_birth = c.execute(f'select epoch_us(process_started)*10+116444736000000000 from {model} where pid_hash=?', [expected]).fetchall()
                        result['gates'][model + '_actual_birth_retained'] = actual_birth == [(collector['expected_birth_filetime'],)]
                        raw = next((row for row in collector['rows'] if row['activitytype'] == 'Refresh'), None)
                        recorded = result['models'][model]
                        result['gates'][model + '_collector_metadata_retained'] = raw is not None and len(recorded) == 1 and all(
                            recorded[0][dest] == raw[source] for dest, source in (
                                ('agent_id', 'agentid'), ('os_pid', 'pid'), ('process_path', 'processpath'),
                                ('args', 'commandline'), ('user_name', 'username'), ('parent_os_pid', 'parentpid')))
                    # Keep the known Linux-as-Windows defect visible, outside this scope.
                    result['known_os_family_defect'] = [row['os_family'] for row in result['models']['process']]
                    if 'pressure_lifetimes' in round_:
                        result['pressure_lifetimes'] = []
                        for lifetime in round_['pressure_lifetimes']:
                            checks = {}
                            for model in ('process', 'process_summary'):
                                actual = c.execute(f'''select os_pid,epoch_us(process_started)*10+116444736000000000
                                    from {model} where pid_hash=?''', [lifetime['pid_hash']]).fetchall()
                                checks[model + '_canonical_birth_unique'] = actual == [(lifetime['pid'], lifetime['birth_filetime'])]
                            result['pressure_lifetimes'].append(dict(**lifetime, gates=checks))
                        result['gates']['all_pressure_lifetimes_retained'] = bool(result['pressure_lifetimes']) and all(
                            all(lifetime['gates'].values()) for lifetime in result['pressure_lifetimes'])
                        pids = ','.join(str(lifetime['pid']) for lifetime in round_['pressure_lifetimes'])
                        raw_files = str(data / 'raw_sensor/raw_process_file/**/*.parquet')
                        raw_paths = c.execute(f'''select PID,PidHash,File_Path,lower(ActivityType),sum(EventCount),sum(BytesRequested)
                            from read_parquet(?,union_by_name=true) where PID in ({pids})
                            group by all order by all''', [raw_files]).fetchall()
                        silver_paths = c.execute(f'''select os_pid,pid_hash,filename,lower(activity_type),sum(event_count),sum(bytes_requested)
                            from process_file where os_pid in ({pids}) group by all order by all''').fetchall()
                        result['gates']['pressure_file_silver_exact_counters_keys'] = bool(raw_paths) and raw_paths == silver_paths
                        activities = [('open', 'Open_Events'), ('close', 'Close_Events'), ('create', 'Create_Events'),
                            ('delete', 'Delete_Events'), ('rename', 'Rename_Events'), ('setinfo', 'SetInfo_Events'),
                            ('read', 'Read_Events'), ('write', 'Write_Events')]
                        counters = ','.join(f"sum(case when lower(ActivityType)='{activity}' then EventCount else 0 end)" for activity, _ in activities)
                        counters += ",sum(case when lower(ActivityType)='read' then BytesRequested else 0 end),sum(case when lower(ActivityType)='write' then BytesRequested else 0 end)"
                        raw_gold = c.execute(f'''select PidHash,{counters} from read_parquet(?,union_by_name=true)
                            where PID in ({pids}) group by PidHash order by PidHash''', [raw_files]).fetchall()
                        gold_columns = ','.join(column for _, column in activities) + ',Read_Bytes,Write_Bytes'
                        actual_gold = c.execute(f'''select pid_hash,{gold_columns} from process_file_summary
                            where os_pid in ({pids}) order by pid_hash''').fetchall()
                        result['gates']['pressure_file_gold_exact_counters_unique'] = bool(raw_gold) and raw_gold == actual_gold
                        result['pressure_counter_comparison'] = dict(raw_path_activity_groups=len(raw_paths),
                            silver_path_activity_groups=len(silver_paths), raw_lifetime_groups=len(raw_gold),
                            gold_lifetime_groups=len(actual_gold))
            results.append(result)
            args.output.write_text(json.dumps(results, indent=2, default=str) + '\n')
            print(json.dumps({k: v for k, v in result.items() if k not in ('models', 'command', 'pressure_lifetimes')}), flush=True)


if __name__ == '__main__':
    main()
