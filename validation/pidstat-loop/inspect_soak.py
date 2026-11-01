#!/usr/bin/env python3
"""Read every retained pidstat file against an actual Python schema; no live parity claim."""

import argparse
from collections import Counter
import datetime
import json
from pathlib import Path
import statistics
from zoneinfo import ZoneInfo

import duckdb
import evidence


def inspect(root):
    state = json.loads((root / 'state.json').read_text())
    report = {'state': state['status'], 'elapsed_sec': state['elapsed_sec'],
              'shutdown': state['shutdown'], 'files': [], 'issues': [],
              'limits': ['Not paired-live Python parity or comparative resource evidence',
                         'Smoke generation is not sensor capture acceptance',
                         '30-second process observations cannot exclude all transient children',
                         'Not package, DBT, RHEL or native amd64 qualification']}
    reference_rows, reference_schema, version = evidence.read_dataset(root / 'python-reference')
    schema = reference_schema[0]
    expected_columns, expected_physical = schema['columns'], schema['physical']
    report['reference'] = {'sha256': schema['sha256'], 'rows': len(reference_rows),
                           'columns': expected_columns, 'physical': expected_physical,
                           'reader_duckdb': version}
    if state['status'] != 'collected-awaiting-review' or state['elapsed_sec'] < state['duration_sec']:
        report['issues'].append('Duration or graceful collection completion failed')
    if state['shutdown'].get('lintap', {}).get('exit') != 0:
        report['issues'].append('Lintap did not exit cleanly')
    totals = Counter()
    times, windows = set(), []
    for path in sorted((root / 'pidstat-data').rglob('*.parquet')):
        rows, schemas, _ = evidence.read_dataset(path)
        actual = schemas[0]
        item = {'file': str(path.relative_to(root)), 'sha256': actual['sha256'], 'rows': len(rows),
                'columns_match_python': actual['columns'] == expected_columns,
                'physical_match_python': actual['physical'] == expected_physical}
        if not rows or not item['columns_match_python'] or not item['physical_match_python']:
            report['issues'].append('Empty file/schema mismatch: ' + item['file'])
        if rows:
            window = rows[0]['window_start_epoch']
            windows.append(window)
            start = datetime.datetime.fromtimestamp(window, ZoneInfo('America/Phoenix')).replace(tzinfo=None)
            end = start + datetime.timedelta(seconds=300)
            item.update(window_epoch=window, min_time=min(r['time'] for r in rows),
                        max_time=max(r['time'] for r in rows), nulls={name: sum(r[name] is None for r in rows)
                                                                  for name in evidence.COLUMNS})
            partition = ['dayPK=' + start.strftime('%Y%m%d'), 'hourPK=' + start.strftime('%H')]
            bad = sum(r['partition'] != partition or
                      not start - datetime.timedelta(microseconds=1) <= datetime.datetime.fromisoformat(r['time'])
                      <= end for r in rows)
            item['wrong_window_or_partition_rows'] = bad
            if bad or window % 300:
                report['issues'].append('Invalid window placement: ' + item['file'])
            duplicates = Counter((r['time'], r['uid'], r['pid'], r['hostname']) for r in rows)
            item['duplicate_identity_time_rows'] = sum(n - 1 for n in duplicates.values() if n > 1)
            if item['duplicate_identity_time_rows']:
                report['issues'].append('Duplicate identity/time rows: ' + item['file'])
            times.update(r['time'] for r in rows)
            totals['rows'] += len(rows)
        report['files'].append(item)
    if len(report['files']) < 3:
        report['issues'].append('Fewer than three rotations')
    report['total_rows'] = totals['rows']
    report['rotation_windows'] = sorted(windows)
    report['window_gaps_seconds'] = [b - a for a, b in zip(sorted(windows), sorted(windows)[1:])]
    if any(g != 300 for g in report['window_gaps_seconds']):
        report['issues'].append('Duplicate or missing rotation windows')
    ordered_times = sorted(datetime.datetime.fromisoformat(t) for t in times)
    gaps = [(b - a).total_seconds() for a, b in zip(ordered_times, ordered_times[1:])]
    report['sample_times'] = {'count': len(times), 'first': min(times) if times else None,
                            'last': max(times) if times else None,
                            'median_gap_sec': statistics.median(gaps) if gaps else None,
                            'max_gap_sec': max(gaps) if gaps else None}
    report['remaining_pidstat_state'] = [str(p.relative_to(root)) for p in
        list((root / 'pidstat-data').rglob('*.active')) +
        [p for p in (root / 'pidstat-spool').iterdir() if p.name != 'collector.lock']]
    if report['remaining_pidstat_state']:
        report['issues'].append('Unsealed/unpublished pidstat state remains')
    samples = [json.loads(line) for line in (root / 'resources.jsonl').read_text().splitlines()]
    report['resource_sample_count'] = len(samples)
    report['resources'] = {}
    for name in ('pidstat', 'lintap'):
        valid = [s for s in samples if 'read_error' not in s['processes'][name]]
        observations = [s['processes'][name] for s in valid]
        cpu = [((b['processes'][name]['user_ticks'] + b['processes'][name]['system_ticks']) -
                (a['processes'][name]['user_ticks'] + a['processes'][name]['system_ticks'])) /
               state['clk_tck'] / (b['elapsed_sec'] - a['elapsed_sec']) * 100
               for a, b in zip(valid, valid[1:])]
        report['resources'][name] = {
            'read_errors': len(samples) - len(valid),
            'rss_kib_first': observations[0]['rss_kib'], 'rss_kib_last': observations[-1]['rss_kib'],
            'rss_kib_peak': max(o['rss_kib'] for o in observations),
            'rss_kib_median': statistics.median(o['rss_kib'] for o in observations),
            'threads_peak': max(o['threads'] for o in observations),
            'observed_children': sorted({p for o in observations for p in o['children']}),
            'cpu_core_percent_median': statistics.median(cpu) if cpu else None,
            'cpu_core_percent_peak_30s': max(cpu) if cpu else None}
    statuses = []
    for path in Path(state['smoke_root']).rglob('status.tsv'):
        for line in path.read_text().splitlines()[1:]:
            started, test, rc, status = line.split('\t')
            statuses.append({'started_utc': started, 'test': test, 'exit': int(rc), 'evidence': status})
    report['smoke'] = {'entries': statuses, 'counts': dict(Counter(s['test'] for s in statuses)),
                       'failed': [s for s in statuses if s['exit'] or s['evidence'] != 'recorded']}
    report['sensor_files'] = []
    with duckdb.connect() as db:
        for path in sorted((root / 'lintap-data').rglob('*.parquet')):
            try:
                count = db.execute('SELECT count(*) FROM read_parquet(?)', [str(path)]).fetchone()[0]
                report['sensor_files'].append({'file': str(path.relative_to(root)), 'rows': count,
                                               'sha256': evidence.sha(path)})
            except Exception as exc:
                report['sensor_files'].append({'file': str(path.relative_to(root)), 'error': str(exc)})
    report['status'] = 'INSPECTED' if not report['issues'] else 'FINDINGS'
    evidence.write(root / 'inspection.json', report)
    print(json.dumps({k: v for k, v in report.items() if k not in ('files', 'sensor_files', 'reference')}, indent=2))
    return 0 if not report['issues'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    options = parser.parse_args()
    raise SystemExit(inspect(options.root))
