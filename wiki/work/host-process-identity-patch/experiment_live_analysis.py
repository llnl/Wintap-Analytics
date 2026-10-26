"""Independent Mac parquet/manifest oracle; old and pid-v2 hashes are not equated."""
import argparse
from collections import Counter
import hashlib
import datetime as dt
import json
from pathlib import Path
import duckdb


def digest(host, pid, start, agent=None):
    # Independent QA oracle, not a second production identity definition.
    pre = f'Process_ID`llnl`{start}`{host}`' + (f'{agent}`' if agent is not None else '') + f'{pid}`'
    attribute = hashlib.md5(pre.encode()).hexdigest().upper()
    return hashlib.md5(f'N`Process`{attribute}`'.encode()).hexdigest().upper()


def exit_evidence_checks(rows, expected_pids, legacy=False):
    """Coverage and recovery are separate from independently checked hash inputs."""
    selected = [r for r in rows if r.get('Pid') in expected_pids]
    retained = [r for r in selected if r.get('ExitEvidenceRetained') is True]
    return dict(
        every_child_has_one_exit_evidence_receipt=len(selected) == len(expected_pids)
        and {r['Pid'] for r in selected} == set(expected_pids),
        every_receipt_explicitly_partial=bool(selected)
        and all(r.get('LifecycleCoverage') == 'exit-only' for r in selected),
        recovery_matches_authoritative_start=bool(selected) and all(
            r.get('ExitEvidenceRetained') is (not legacy)
            and ((r.get('StartBootNs', 0) == 0) if legacy else (r.get('StartBootNs', 0) > 0))
            for r in selected),
        retained_children=len({r['Pid'] for r in retained}),
    )


def analyze(round_, qa, data_root, strict=True):
    name = round_['name']
    fixed = name.startswith('fixed') or round_.get('identity_scheme') == 'pid-v2'
    root = data_root / name / 'raw_sensor'
    c = duckdb.connect(':memory:')
    for short, table in [('p', 'raw_process'), ('f', 'raw_process_file'), ('h', 'raw_host')]:
        c.execute(f'create table {short} as select * from read_parquet(?,union_by_name=true)', [str(root / table / '**/*.parquet')])
    children = round_['workload']['children']
    c.execute('create table truth(pid integer, cohort varchar, start_ticks bigint, clock_ticks bigint)')
    c.executemany('insert into truth values (?,?,?,?)', [(r['pid'], r['cohort'], r['start_ticks'], r['clock_ticks']) for r in children])
    c.execute('create view wp as select p.* from p join truth using(pid)')
    c.execute('create view wf as select f.* from f join truth using(pid)')
    result = dict(name=name, expected_children=len(children), expected_payload_files=round_['workload']['expected_payload_files'])

    def query(key, sql):
        cur = c.execute(sql)
        result[key] = dict(sql=sql, rows=[dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()])

    query('lifecycle', """select t.cohort,count(distinct t.pid) eligible,
      count(distinct p.pid) recorded_pids,
      count(distinct p.pid) filter(where activitytype in ('Start','Refresh')) birth_pids,
      count(distinct p.pid) filter(where activitytype='Stop') exit_pids,
      count(*) filter(where activitytype='Start') start_observations,
      count(*) filter(where activitytype='Stop') stop_observations,
      count(distinct pidhash) hashes from truth t left join wp p using(pid) group by t.cohort order by 1""")
    query('files', """select cohort,count(*) staged_rows,sum(eventcount) events,
      count(distinct f.pid) recorded_pids,count(distinct pidhash) hashes,
      count(distinct file_path) paths,
      count(*) filter(where lower(processname) like 'unknown%') unknown_named_rows,
      count(*) filter(where not exists(select 1 from wp p where p.pidhash=f.pidhash)) orphan_rows,
      count(distinct pidhash) filter(where not exists(select 1 from wp p where p.pidhash=f.pidhash)) orphan_hashes
      from wf f join truth using(pid) group by cohort order by 1""")
    query('payload_paths', """select count(distinct file_path) retained_paths,
      count(*) rows_total,sum(eventcount) events from wf where file_path like '%/payload/%'""")
    query('partial_lifecycle_linkage', """select
      (select count(*) from wp where activitytype in ('Start','Refresh')) birth_observations,
      count(*) filter(where not exists(select 1 from wp p where p.pid=f.pid
        and p.pidhash=f.pidhash and p.activitytype='Stop')) rows_without_matching_stop
      from wf f""")
    query('hash_explosion_by_pid', """select pid,count(*) rows_total,count(distinct pidhash) hashes,
      count(*) filter(where lower(processname) like 'unknown%') unknown_rows,
      (max(lastseen)-min(firstseen))/10000000.0 event_span_seconds
      from wf group by pid order by hashes desc,pid limit 12""")
    provenance = json.loads((qa / 'host-provenance.json').read_text())
    boot_ft = 116444736000000000 + provenance['boot_unix_seconds'] * 10_000_000
    # Independent /proc btime has seconds precision, matching sensor conversion.
    mapping = {r['pid']: boot_ft + r['start_ticks'] * 10_000_000 // r['clock_ticks'] for r in children}
    checks = Counter()
    for pid, host, agent, act, event, value in c.execute('select pid,hostname,agentid,activitytype,eventtime,pidhash from wp').fetchall():
        expected = digest(host.strip().upper() if fixed else host.lower(), pid, mapping[pid], None if fixed else agent)
        checks['process_observations'] += 1
        checks['canonical_hash_matches'] += expected == value
        checks['stop_canonical_matches'] += act == 'Stop' and expected == value
        checks['stop_event_time_hash_matches'] += act == 'Stop' and digest(host.strip().upper() if fixed else host.lower(), pid, event, None if fixed else agent) == value
        checks['unresolved_process_rows'] += digest(host.strip().upper() if fixed else host.lower(), -1, 0, None if fixed else agent) == value
    for pid, host, agent, first, value in c.execute('select pid,hostname,agentid,firstseen,pidhash from wf').fetchall():
        expected = digest(host.strip().upper() if fixed else host.lower(), pid, mapping[pid], None if fixed else agent)
        checks['file_rows'] += 1
        checks['file_canonical_matches'] += expected == value
        checks['file_firstseen_hash_matches'] += digest(host.strip().upper() if fixed else host.lower(), pid, first, None if fixed else agent) == value
        checks['unresolved_file_rows'] += digest(host.strip().upper() if fixed else host.lower(), -1, 0, None if fixed else agent) == value
    result['independent_hash_oracle'] = dict(checks)
    shadow = qa / name / 'lifetime-shadow.jsonl'
    if shadow.exists():
        rows, parse_errors = [], []
        for line_number, line in enumerate(shadow.read_text().splitlines(), 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                if strict:
                    raise
                parse_errors.append(dict(line_number=line_number, error=str(exc), text=line))
        result['shadow_parse_errors'] = parse_errors
        result['shadow_writer_summary'] = [r for r in rows if r.get('Kind') == 'summary']
        selected = [r for r in rows if r.get('Pid') in mapping]
        counts = Counter()
        errors = []
        truth = {r['pid']: r for r in children}
        for r in selected:
            counts['observations'] += 1
            counts['lifetime_' + r['LifetimeClass']] += 1
            counts['identity_' + r['IdentitySource']] += 1
            counts['role_' + r['RoleClass']] += 1
            child = truth[r['Pid']]
            tick_matches = r['StartBootNs'] * child['clock_ticks'] // 1_000_000_000 == child['start_ticks']
            lower = child['before_exit_monotonic_ns'] - r['StartMonotonicNs']
            upper = child['reap_monotonic_ns'] - r['StartMonotonicNs']
            counts['kernel_start_ticks_match'] += tick_matches
            counts['duration_within_independent_bounds'] += r['DurationNs'] is not None and lower <= r['DurationNs'] <= upper
            expected_class = 'unknown' if r['StartMonotonicNs'] == 0 else 'longer-lived' if child['cohort'] == 'long' else 'short-lived'
            counts['lifetime_class_matches'] += r['LifetimeClass'] == expected_class
            if (r['StartBootNs'] > 0 and not tick_matches) or r['LifetimeClass'] != expected_class:
                errors.append(r)
        result['shadow_workload'] = dict(counts= dict(counts), distinct_pids=len({r['Pid'] for r in selected}), discrepancies=errors)
        if round_.get('experiment_exit_recovery') and round_['missing_birth_injection']:
            result['exit_evidence_checks'] = exit_evidence_checks(
                rows, set(mapping), round_.get('legacy_exit_injection', False))
    capabilities = c.execute('select distinct RuntimeCapabilitiesJson from h').fetchall()
    result['runtime_capability_receipts'] = [json.loads(r[0]) if r[0] else None for r in capabilities]
    logs = (qa / name / 'collector.log').read_text()
    result['log_problem_lines'] = [line for line in logs.splitlines() if any(word in line.lower() for word in ['handler error', 'failed', 'overflow', 'dropped', 'segmentation', 'not initialized'])][-80:]
    runtime = Path(round_['runtime_root']).name
    runtime_log = qa / runtime / 'Logs/Lintap.log'
    snapshot_log = qa / name / 'runtime-snapshot/Logs/Lintap.log'
    if snapshot_log.exists():
        runtime_log = snapshot_log
    if runtime_log.exists():
        logs = runtime_log.read_text()
        result['runtime_log_scope'] = 'single-round snapshot' if snapshot_log.exists() else 'shared burst/restart log' if runtime == 'shared-fixed-runtime' else 'single round'
        result['runtime_counter_lines'] = [line for line in logs.splitlines() if any(word in line for word in ['FileOps counters', 'serializer_shutdown', 'final merge', 'sender shutdown', 'queue drain', 'Experimental batch drain', 'Attribution retry cumulative'])]
        result['runtime_error_lines'] = [line for line in logs.splitlines() if '[Error]' in line or 'FILE Error creating' in line][-80:]
        starts = [dt.datetime.strptime(line[:19], '%m/%d/%Y %H:%M:%S') for line in logs.splitlines() if 'Stop command received.' in line]
        ends = [dt.datetime.strptime(line[:19], '%m/%d/%Y %H:%M:%S') for line in logs.splitlines() if 'Shutdown complete.' in line]
        if len(starts) == len(ends) == 1:
            result['logged_shutdown_seconds'] = (ends[0] - starts[0]).total_seconds()
    oracle = result['independent_hash_oracle']
    payload = result['payload_paths']['rows'][0]
    normal = fixed and not round_['missing_birth_injection']
    result['gates'] = dict(
        graceful_without_harness_interruption=round_.get('collector_exit_code') == 0 and not round_.get('forced_termination', False),
        all_expected_paths=payload['retained_paths'] == result['expected_payload_files'],
        exact_payload_event_conservation=payload['events'] == result['expected_payload_files'] * 7,
        every_process_observation_canonical=oracle.get('canonical_hash_matches', 0) == oracle.get('process_observations', 0),
        every_file_row_canonical=oracle.get('file_canonical_matches', 0) == oracle.get('file_rows', 0),
        no_event_time_identity_substitutes=oracle.get('file_firstseen_hash_matches', 0) == 0 and oracle.get('stop_event_time_hash_matches', 0) == 0,
        all_process_identities_canonical_or_explicit_unknown=oracle.get('canonical_hash_matches', 0) + oracle.get('unresolved_process_rows', 0) == oracle.get('process_observations', 0),
        all_file_identities_canonical_or_explicit_unknown=oracle.get('file_canonical_matches', 0) + oracle.get('unresolved_file_rows', 0) == oracle.get('file_rows', 0),
    )
    if shadow.exists():
        result['gates']['shadow_complete_and_parseable'] = not result['shadow_parse_errors'] and len(result['shadow_writer_summary']) == 1
    effective_environment = round_.get('effective_environment', round_.get('verified_process_environment'))
    if effective_environment is not None:
        result['gates']['effective_environment_matches_request'] = all(
            effective_environment.get(k) == v for k, v in round_['env_overrides'].items())
    if round_.get('experiment_exit_recovery') and round_['missing_birth_injection']:
        linkage = result['partial_lifecycle_linkage']['rows'][0]
        result['gates']['no_synthetic_birth_observations'] = linkage['birth_observations'] == 0
        evidence = result.get('exit_evidence_checks', {})
        for key in ('every_child_has_one_exit_evidence_receipt',
                    'every_receipt_explicitly_partial', 'recovery_matches_authoritative_start'):
            result['gates'][key] = evidence.get(key, False)
        if not round_.get('legacy_exit_injection'):
            result['gates']['every_file_row_links_to_captured_stop'] = linkage['rows_without_matching_stop'] == 0
    if normal and strict:
        assert all(result['gates'].values()), (name, result['gates'])
    if 'shadow_workload' in result and strict:
        assert result['shadow_workload']['distinct_pids'] == len(children)
        assert not result['shadow_workload']['discrepancies']
    c.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--qa-root', type=Path, required=True)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('experiment_live_analysis.json'))
    args = parser.parse_args()
    session = json.loads((args.qa_root / 'session.json').read_text())
    results = dict(session=session, rounds=[analyze(r, args.qa_root, args.data_root) for r in session['rounds']])
    args.output.write_text(json.dumps(results, indent=2) + '\n')
    for r in results['rounds']:
        print(json.dumps({k:v for k,v in r.items() if k not in ['runtime_capability_receipts','log_problem_lines']}, indent=2))


if __name__ == '__main__':
    main()
