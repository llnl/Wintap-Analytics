"""Canary-round validation, temporal startup context and portable summary results."""
import datetime as dt
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath

from queries import TESTS, evaluate_run, mark_overlaps, prepare_data, quote, selector_query

CANARIES = tuple(t for t in TESTS if t.startswith('canary-'))
SCHEMA_VERSION = 1


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, separators=(',', ':')).encode()).hexdigest()


def round_key(run):
    """Never group by guessed time proximity or silently mix latest family runs."""
    identity = run.get('canaryRoundId')
    method = 'explicit round ID'
    if not identity:
        command = run.get('command') or []
        manifest = None
        for i, arg in enumerate(command):
            if arg == '--manifest' and i + 1 < len(command):
                manifest = command[i + 1]
            elif isinstance(arg, str) and arg.startswith('--manifest='):
                manifest = arg.split('=', 1)[1]
        if manifest and PurePosixPath(manifest).parent.name.startswith('round.'):
            identity = str(PurePosixPath(manifest).parent)
            method = 'shared manifest round directory (older runner)'
        else:
            identity = run['runId']
            method = 'standalone run; no round membership recorded'
    return digest([run['host']['hostname'].lower(), run.get('host', {}).get('bootId'), identity]), method


def canary_rounds(runs):
    groups = {}
    for run in runs:
        if not run['test'].startswith('canary-'):
            continue
        key, method = round_key(run)
        group = groups.setdefault(key, dict(key=key, method=method, host=run['host']['hostname'], runs=[]))
        group['runs'].append(run)
    return sorted(groups.values(), key=lambda g: max(r.get('startedAtUtc', '') for r in g['runs']), reverse=True)


def input_fingerprint(runs, all_runs, snapshot, settings, source_id):
    # Include evaluator implementation, all attribution intervals, object revisions,
    # normalization assertion, window, padding and budgets. No credentials in the result.
    code = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('analysis.py', 'queries.py', 's3_source.py', 'result_store.py')}
    import duckdb
    return digest(dict(runs=runs, attribution=all_runs, snapshot=snapshot, settings=settings,
                       source=source_id, code=code, engine=duckdb.__version__, schema=SCHEMA_VERSION))


def materialize_runs(con, runs, padding=15, max_rows=100000):
    predicates = [selector_query(r, s, padding).removesuffix(' ORDER BY event_time, pid').split(' WHERE ', 1)[1]
                  for r in runs for s in r['selectors']]
    con.execute('DROP TABLE IF EXISTS canary_events')
    if not predicates:
        return
    con.execute('CREATE TEMP TABLE canary_events AS SELECT * FROM smoke_data WHERE ' +
                ' OR '.join('(' + p + ')' for p in predicates) + f' LIMIT {max_rows + 1}')
    if con.execute('SELECT count(*) FROM canary_events').fetchone()[0] > max_rows:
        raise ValueError('Round observation budget exceeded; truncated validation is not accepted')
    con.execute('CREATE OR REPLACE TEMP VIEW smoke_data AS SELECT * FROM canary_events')


def utc(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Startup/run timestamp requires timezone')
    return parsed.astimezone(dt.timezone.utc)


def read_receipts(con, host_files, max_receipts=1000):
    receipts, errors = [], []
    for path in host_files:
        try:
            columns = {r[0].lower(): r[0] for r in con.execute(f'DESCRIBE SELECT * FROM read_parquet({quote(path)})').fetchall()}
            if 'runtimecapabilitiesjson' not in columns or 'hostname' not in columns:
                continue
            from queries import identifier
            rows = con.execute(f"SELECT {identifier(columns['hostname'])}, {identifier(columns['runtimecapabilitiesjson'])} FROM read_parquet({quote(path)}) WHERE {identifier(columns['runtimecapabilitiesjson'])} IS NOT NULL LIMIT {max_receipts + 1}").fetchall()
            for host, text in rows:
                value = json.loads(text)
                if value.get('schemaVersion') != 1 or value.get('phase') != 'startup-complete' or not value.get('captureRunId'):
                    errors.append('Unsupported/incomplete runtime receipt')
                    continue
                if utc(value['completedAtUtc']) < utc(value['startedAtUtc']):
                    raise ValueError('Invalid startup interval')
                receipts.append((str(host).lower(), value))
                if len(receipts) > max_receipts:
                    return [], ['HOST receipt budget exceeded; correlation unavailable']
        except Exception:
            errors.append('HOST receipt unavailable or invalid (details suppressed)')
    return receipts, errors


def hostname_aliases(runs, receipts):
    """A unique short/FQDN relation is an attribution hint, never identity proof."""
    manifests = {r['host']['hostname'].lower() for r in runs}
    hosts = {h for h, _ in receipts}
    aliases = {}
    for host in manifests:
        short = host.split('.')[0]
        candidates = {h for h in hosts if h.split('.')[0] == short}
        related_manifests = {h for h in manifests if h.split('.')[0] == short}
        if host not in hosts and len(candidates) == 1 and len(related_manifests) == 1:
            candidate = next(iter(candidates))
            # Only actual short/FQDN pairs, never two unrelated DNS suffixes.
            if host == short or candidate == short:
                aliases[host] = candidate
    return aliases


def bind_hosts(runs, aliases):
    result = copy.deepcopy(runs)
    for run in result:
        host = run['host']['hostname'].lower()
        run['host']['hostname'] = aliases.get(host, host)
    return result


def runtime_context(run, receipts, receipt_errors=()):
    """Latest preceding startup is temporal context, not exact collector ownership."""
    try:
        start = utc(run['startedAtUtc'])
        end = utc(run.get('completedAtUtc') or run['startedAtUtc'])
        matching = [(utc(v['startedAtUtc']), v) for h, v in receipts if h == run['host']['hostname'].lower()]
        preceding = [(t, v) for t, v in matching if t <= start]
        if receipt_errors or not preceding:
            return dict(status='unknown', reason='No trustworthy preceding HOST receipt in the selected source history', sensors={})
        latest = max(t for t, _ in preceding)
        candidates = {digest(v): v for t, v in preceding if t == latest}
        if len(candidates) != 1 or any(start < t <= end for t, _ in matching):
            return dict(status='ambiguous', reason='Conflicting startup receipts or collector startup during canary interval', sensors={})
        receipt = next(iter(candidates.values()))
        if utc(receipt['completedAtUtc']) > start:
            return dict(status='ambiguous', reason='Canary began before startup completed', sensors={})
        sensors = {}
        for name, sensor in receipt.get('sensors', {}).items():
            sensors[name] = dict(enabled=sensor.get('enabled'), status=sensor.get('status', 'unknown'),
                tier=sensor.get('tier'), hooks={k: h.get('outcome') for k, h in sensor.get('hooks', {}).items()},
                features={k: v for k, v in sensor.get('features', {}).items() if isinstance(v, (bool, int, float))})
        # Only numeric/boolean effective pipeline settings; never persist config paths,
        # arbitrary environment, loaded objects or receipt OS/host details.
        settings = {k: v['effectiveValue'] for k, v in receipt.get('settings', {}).items()
                    if isinstance(v, dict) and isinstance(v.get('effectiveValue'), (bool, int, float))}
        return dict(status='temporal', reason='Latest preceding startup; startup snapshot, not continuous health or exact event ownership',
                    capture_run_id=receipt['captureRunId'], started_at=receipt['startedAtUtc'], sensors=sensors, settings=settings)
    except Exception:
        return dict(status='unknown', reason='Runtime correlation unavailable', sensors={})


def case_context(selector, context):
    names = {'file': ['FileOps'], 'network': ['Network'], 'host': [], 'process': ['Execve', 'Clone', 'Exit']}[selector['domain']]
    if selector['domain'] == 'process' and selector.get('threadIds') and not selector.get('pids'):
        names = ['Clone']
    sensors = context.get('sensors', {})
    relevant = {n: sensors.get(n, {}).get('status', 'unknown') for n in names}
    limited = [n for n, status in relevant.items() if status in ('disabled', 'failed', 'partial') or sensors.get(n, {}).get('enabled') is False]
    reason = 'Collector startup limitations may explain missing observations: ' + ', '.join(limited) if limited else (
        'Relevant collectors reported running; gaps are not explained by a disabled/failed startup' if relevant and all(s == 'running' for s in relevant.values()) else 'Collector expectation unknown')
    return dict(collectors=relevant, explanation=reason)


def summarize(run, evaluation, context):
    cases = []
    reasons = list(evaluation['reasons'])
    companion = any(c['selector']['domain'] == 'process' and c['selector'].get('pids') and
        not c['error'] and any(ch['observed'] and ch['expectation'].startswith('PID ') for ch in c['checks'])
        for c in evaluation['cases'])
    for c in evaluation['cases']:
        error = c['error']
        if error:
            reasons = [r.replace(error, 'Telemetry query unavailable (details suppressed)') for r in reasons]
        missing = [ch['expectation'] for ch in c['checks'] if not ch['observed']]
        observation = 'violation' if c['violations'] else 'unavailable' if error else 'gaps' if missing or not c['rows'] else 'observed'
        # Negative thread evidence requires a positive companion and may have zero rows.
        if not error and not c['violations'] and not missing and c['selector'].get('threadIds') and not c['selector'].get('pids'):
            observation = 'negative observation; companion observed' if companion else 'absence unconfirmed; no companion'
        cases.append(dict(case=c['selector'].get('case', c['selector']['domain']), domain=c['selector']['domain'],
            observation=observation, rows=c['rows'], checks=c['checks'], missing=missing,
            violations=c['violations'], skips=c['selector'].get('skips', []),
            runtime=case_context(c['selector'], context)))
    return dict(test=run['test'], title=TESTS[run['test']], run_id=run['runId'], host=run['host']['hostname'],
        started_at=run['startedAtUtc'], state=evaluation['state'], reasons=reasons, harness=run.get('status', 'unknown'),
        stimulus_only=bool(run.get('stimulusOnly')), cases=cases, runtime=context,
        skips=[c for c in (run.get('results') or {}).get('cases', []) if isinstance(c, dict) and c.get('status') == 'skipped'])


def analyze_round(con, runs, all_runs, telemetry_files, host_files, data_root='', unlabelled_host='', padding=15,
                  max_rows=100000, evidence_errors=(), fingerprint='', allow_hostname_aliases=True):
    con.execute("SET temp_directory=''")
    con.execute("SET memory_limit='256MB'")
    con.execute("SET TimeZone='UTC'")
    receipts, receipt_errors = read_receipts(con, host_files)
    aliases = hostname_aliases(all_runs, receipts) if allow_hostname_aliases and not receipt_errors else {}
    bound_runs = bind_hosts(runs, aliases)
    evaluations = {}
    data_errors = []
    fatal = None
    try:
        available = False
        if any(r['selectors'] for r in bound_runs):
            _, data_errors, available = prepare_data(con, data_root, unlabelled_host, telemetry_files=telemetry_files)
            if available:
                materialize_runs(con, bound_runs, padding, max_rows)
        for run in bound_runs:
            evaluations[(run['test'], run['runId'])] = evaluate_run(con, run, available, padding)
        mark_overlaps(bind_hosts(all_runs, aliases), evaluations, padding)
    except Exception:
        fatal = 'Round validation unavailable: read, selector or memory budget failed (details suppressed)'
    results = []
    for run, bound in zip(runs, bound_runs):
        evaluation = evaluations.get((run['test'], run['runId']))
        if evaluation is None:
            evaluation = dict(state='red' if run.get('status') == 'failed' else 'yellow', reasons=[fatal or 'Validation unavailable'], cases=[])
        if data_errors or evidence_errors or receipt_errors or fatal:
            evaluation['reasons'].append('Incomplete source/runtime evidence; no coverage certification')
            if evaluation['state'] == 'green':
                evaluation['state'] = 'yellow'
        context = runtime_context(bound, receipts, receipt_errors)
        context['hostname_correlation'] = 'inferred unique short/FQDN alias' if run['host']['hostname'].lower() in aliases else 'exact hostname'
        if run['host']['hostname'].lower() in aliases:
            evaluation['reasons'].append('Short/FQDN hostname correlation is inferred, not exact host identity proof')
            if evaluation['state'] == 'green':
                evaluation['state'] = 'yellow'
        results.append(summarize(run, evaluation, context))
    present = {r['test'] for r in runs}
    missing = [t for t in CANARIES if t not in present] if any(t in CANARIES for t in present) else []
    return dict(schema_version=SCHEMA_VERSION, fingerprint=fingerprint,
        analyzed_at=dt.datetime.now(dt.timezone.utc).isoformat(), results=results, missing_families=missing,
        errors=([fatal] if fatal else []) + ['Unreadable telemetry file'] * len(data_errors) +
               ['Evidence validation error'] * len(evidence_errors) + receipt_errors,
        scope='Selected telemetry observations and startup context, not full harness re-validation or release certification')
