#!/usr/bin/env python3
"""Explicit local/exported-round validation for Ubuntu and later RPM pilots.

Uses the dashboard evaluator and summary store. No collector operations or uploads.
Exit 0 means all declared observations and package-scope checks passed, not full
capture certification; 1 means contradiction/failure, 2 means incomplete evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'streamlit/projects/SmokeTests'))
import duckdb
from analysis import (analyze_round, bind_hosts, canary_rounds, hostname_aliases,
                      input_fingerprint, read_receipts)
from queries import load_manifests, selector_query
from result_store import load_result, save_result


def sha256(value):
    if len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise argparse.ArgumentTypeError('Expected lowercase SHA-256')
    return value


def qualification(con, runs, report, receipts, expected):
    """Receipt hashes are temporal context; trusted build/RPM proof is external."""
    checks = []
    def check(name, passed, contradiction=False):
        checks.append(dict(check=name, passed=bool(passed), contradiction=bool(contradiction)))
    for result in report['results']:
        context = result['runtime']
        candidates = [v for host, v in receipts if host == next(
            r['host']['hostname'].lower() for r in runs if r['runId'] == result['run_id']) and
            v.get('captureRunId') == context.get('capture_run_id')]
        check(result['test'] + ': preceding startup context', context['status'] == 'temporal' and bool(candidates))
        for name, digest in expected.items():
            sensors = [v.get('sensors', {}).get(name, {}) for v in candidates]
            check(result['test'] + ': ' + name + ' core object hash', bool(sensors) and all(
                s.get('enabled') is True and s.get('tier') == 'core' and s.get('objectSha256') == digest for s in sensors),
                any(s.get('objectSha256') and s['objectSha256'] != digest for s in sensors))
        features = context.get('sensors', {}).get('Network', {}).get('features', {})
        check(result['test'] + ': TCP tuple lifecycle contract', features.get('tcpTupleContractVersion') == 1 and
              features.get('tcpTupleLifecycleHooksAttached') is True)
        check(result['test'] + ': network return contract', features.get('networkContractVersion') == 2 and all(
            features.get(k) is True for k in ('tcpAcceptReturnAttached', 'udpSendSuccessReturnAttached', 'udpReceiveSuccessReturnAttached')))
        hooks = context.get('sensors', {}).get('FileOps', {}).get('hooks', {})
        check(result['test'] + ': relative unlink/open hooks', all(hooks.get(k) == 'attached' for k in ('t_unlinkat', 't_openat_ent', 'trace_openat')))
    sources, explicit, pairs = set(), [], 0
    for run in runs:
        for selector in run['selectors']:
            if selector['domain'] == 'process':
                for source, projected in con.execute('SELECT start_source, start_source_explicit FROM (' +
                    selector_query(run, selector) + ") WHERE activity IN ('start', 'refresh')").fetchall():
                    explicit.append(projected)
                    if source: sources.add(source)
            if selector['domain'] != 'file':
                continue
            groups = {}
            for item in selector.get('pathExpectations', []):
                groups.setdefault(item['path'].lower(), set()).add(item['path'])
            for paths in groups.values():
                if len(paths) < 2: continue
                pairs += 1
                rows = con.execute('SELECT path, file_hash FROM (' + selector_query(run, selector) + ')').fetchall()
                keys = [{key for path, key in rows if path == wanted} for wanted in paths]
                check('case-only pair: distinct non-null sensor file keys', all(
                    len(k) == 1 and None not in k and '' not in k for k in keys) and
                    len(set.union(*keys)) == len(paths),
                    any((keys[i] & keys[j]) - {None, ''} for i in range(len(keys)) for j in range(i)))
    check('case-only pair supplied', pairs > 0)
    check('Start/Refresh explicit provenance schema', bool(explicit) and all(explicit))
    check('three recognized producer sources observed', sources == {'sched_fork', 'sched_exec', 'execve_or_execveat'})
    return checks


def exit_status(report):
    if (any(c.get('contradiction') for c in report.get('qualification', [])) or
        any(r['harness'] == 'failed' or r['state'] == 'red' or any(c['violations'] for c in r['cases']) for r in report['results'])):
        return 1
    if (report['errors'] or report['missing_families'] or not report['results'] or
        any(not c['passed'] for c in report.get('qualification', [])) or
        any(r['harness'] != 'passed' or r['skips'] or not r['cases'] or any(
            c['missing'] or c['skips'] or c['warnings'] or c['observation'] in ('unavailable', 'absence unconfirmed; no companion')
            for c in r['cases']) for r in report['results'])):
        return 2
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root', required=True, type=Path)
    p.add_argument('--round-key', help='Exact key from --list; required if multiple rounds exist')
    p.add_argument('--list', action='store_true')
    p.add_argument('--network-sha256', type=sha256)
    p.add_argument('--file-sha256', type=sha256)
    p.add_argument('--force', action='store_true')
    args = p.parse_args()
    if duckdb.__version__ != '1.5.6': p.error('DuckDB 1.5.6 required')
    if not args.list and not (args.network_sha256 and args.file_sha256):
        p.error('Both trusted package/build object hashes are required')
    root = args.data_root.resolve()
    if not root.is_dir(): p.error('Dataset root does not exist')
    files = sorted(root.rglob('*.parquet'))
    if len(files) > 10000: p.error('File budget exceeded; scope the input dataset')
    snapshot = {str(f): [f.stat().st_size, f.stat().st_mtime_ns] for f in files}
    with duckdb.connect() as con:
        con.execute("SET memory_limit='256MB'")
        con.execute("SET temp_directory=''")
        runs, errors = load_manifests('', data_root=str(root), connection=con)
        groups = canary_rounds(runs)
        if args.list:
            print(json.dumps([dict(key=g['key'], families=len(g['runs'])) for g in groups]))
            return 2 if errors else 0
        selected = [g for g in groups if not args.round_key or g['key'] == args.round_key]
        if len(selected) != 1: p.error('Select exactly one recorded round with --round-key')
        group = selected[0]
        ctx = dict(remote=False, data_root=str(root), analysis_group=group['key'])
        expected = dict(Network=args.network_sha256, FileOps=args.file_sha256)
        settings = dict(padding=15, max_rows=100000, memory_mb=256, expected=expected, errors=errors,
            cli_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        fingerprint = input_fingerprint(group['runs'], runs, snapshot, settings, str(root))
        report = None if args.force else load_result(ctx, fingerprint)
        reused = report is not None
        if report is None:
            hosts = [f for f in files if 'raw_host' in f.parts]
            telemetry = [f for f in files if 'raw_smoke_test' not in f.parts]
            report = analyze_round(con, group['runs'], runs, telemetry, hosts, data_root=str(root),
                evidence_errors=errors, fingerprint=fingerprint)
            receipts, receipt_errors = read_receipts(con, hosts)
            bound = bind_hosts(group['runs'], hostname_aliases(runs, receipts) if not receipt_errors else {})
            if not report['errors']:
                report['qualification'] = qualification(con, bound, report, receipts, expected)
            else:
                report['qualification'] = [dict(check='Analysis available', passed=False)]
            after = {str(f): [f.stat().st_size, f.stat().st_mtime_ns] for f in root.rglob('*.parquet')}
            if after != snapshot: raise RuntimeError('Input snapshot changed; retry after delivery settles')
            save_result(ctx, report)
        status = exit_status(report)
        print(json.dumps(dict(exit_status=status, reused=reused, errors=len(report['errors']),
            missing_families=len(report['missing_families']), qualification=report.get('qualification', []),
            families=[dict(test=r['test'], triage=r['state'], missing=sum(len(c['missing']) for c in r['cases']),
                violations=sum(len(c['violations']) for c in r['cases'])) for r in report['results']]), indent=2))
        return status


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, duckdb.Error):
        print('Validation unavailable; no acceptance or persistence acknowledged (details suppressed)', file=sys.stderr)
        raise SystemExit(2)
