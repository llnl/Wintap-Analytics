"""Manifest-first pages; telemetry is touched only after an explicit validation."""
import streamlit as st

from queries import TESTS, evaluate_run, mark_overlaps, prepare_data, selector_query

ICONS = {'red': '🔴', 'yellow': '🟡', 'green': '🟢', 'gray': '⚪'}


def is_canary(run):
    return run['test'].startswith('canary-') or run.get('suiteKind') == 'canary' or run.get('stimulusOnly') is True


def manifest_rows(runs, history=False):
    seen, rows = set(), []
    for run in sorted(runs, key=lambda r: r.get('startedAtUtc', ''), reverse=True):
        key = (run['host']['hostname'].lower(), run['test'])
        if not history and key in seen:
            continue
        seen.add(key)
        rows.append(dict(kind='canary' if is_canary(run) else 'dev-time',
            host=key[0], test=TESTS[run['test']], run_id=run['runId'],
            saved_outcome=run.get('status', 'unknown'), capture='not evaluated',
            status='red' if run.get('status') == 'failed' else 'yellow',
            cases=len(run['selectors']), started=run.get('startedAtUtc', '')))
    return rows


def overview_page(ctx):
    st.header('Overview')
    st.info('Manifest-only overview: no telemetry schemas or event scans. Saved success is not a capture PASS.')
    history = st.checkbox('Show older runs in overview', value=False)
    rows = manifest_rows(ctx['visible_runs'], history)
    st.metric('Recorded runs', len(rows))
    st.dataframe(rows, width='stretch')
    st.subheader('Canary coverage inventory')
    recorded = {r['test'] for r in ctx['visible_runs']}
    st.dataframe([dict(test=title, evidence='recorded' if test in recorded else 'not supplied',
        capture='not evaluated') for test, title in TESTS.items() if test.startswith('canary-')], width='stretch')
    st.caption('Older stimulus-only named/endpoint manifests appear on Canary Tests, but do not count as evidence for the new expanded suites. An absent host cannot be inferred from absent manifests.')


def materialize_run(con, run, padding, max_rows=100000):
    """Read the union of selector matches once, without losing overlapping rows.

    A normalized final predicate is authoritative. No unsafe filename/time pruning.
    The extra sentinel row makes row-budget exhaustion fail closed.
    """
    predicates = [selector_query(run, s, padding).removesuffix(' ORDER BY event_time, pid').split(' WHERE ', 1)[1]
                  for s in run['selectors']]
    if not predicates:
        return
    con.execute('CREATE TEMP TABLE selected_events AS SELECT * FROM smoke_data WHERE ' +
                ' OR '.join('(' + p + ')' for p in predicates) + f' LIMIT {max_rows + 1}')
    if con.execute('SELECT count(*) FROM selected_events').fetchone()[0] > max_rows:
        raise ValueError('Run working-set budget exceeded; no truncated validation result is accepted')
    con.execute('CREATE OR REPLACE TEMP VIEW smoke_data AS SELECT * FROM selected_events')


def test_page(ctx, canary):
    st.header('Canary Tests' if canary else 'Dev-time Tests')
    if canary:
        st.info('Bounded recurring stimuli against the already-running sensor. No restarts, configuration changes, tracer attachment or public network probes. Generation success is stimulus-only, not capture certification.')
    else:
        st.warning('Manual qualification, not unattended canaries. Some harnesses start/stop collectors, change Clone settings or attach tracers; use a designated idle host and review the original devtools instructions.')
    with st.expander('How to generate evidence'):
        if canary:
            st.caption('On the Linux collection host, launch the independent runner in a terminal/tmux. Review a one-round pilot before open-ended collection. See validation/telemetry-soak/README.md for required paths and permissions.')
            st.code('bash validation/telemetry-soak/run-smoke-soak.sh '
                    '--python /path/to/python --devtools /path/to/wintap/devtools '
                    '--data-root /path/to/collector-data --evidence-root /path/outside/git/canary-evidence '
                    '--rounds 1', language='bash')
        else:
            st.caption('Use the live Wintap devtools/README.md and the corresponding *_smoke_test.py or validate_*.py --help. Supply a fresh --manifest and --smoke-data-root. The dashboard never launches these commands. network_capture_smoke_test.py uses public network endpoints; obtain approval first.')
    choices = [r for r in ctx['visible_runs'] if is_canary(r) == canary]
    if not choices:
        st.info('No runs supplied for this page.')
        return
    tests = list(dict.fromkeys(r['test'] for r in choices))
    test = st.selectbox('Test family', tests, format_func=lambda t: TESTS[t], key='family-' + str(canary))
    by_id = {r['runId']: r for r in choices if r['test'] == test}
    selected = st.selectbox('Test run', list(by_id), key='run-' + str(canary),
        format_func=lambda k: f"{by_id[k]['host']['hostname']} · {by_id[k].get('startedAtUtc', '?')} · {k}")
    run = by_id[selected]
    st.write(f"Saved outcome: **{run.get('status', 'unknown')}**" + (' (stimulus only)' if is_canary(run) else ''))
    with st.expander('Saved portable manifest'):
        st.json(run)
    for item in (run.get('results') or {}).get('cases', []):
        if isinstance(item, dict) and item.get('status') == 'skipped':
            st.warning(f"Skipped stimulus: {item.get('case', '?')} — {item.get('reason', 'unsupported')}")
    st.dataframe([dict(case=s.get('case', s['domain']), domain=s['domain'],
        expectations=', '.join(s.get('expectedActivities', [])), skips='; '.join(s.get('skips', [])))
        for s in run['selectors']], width='stretch')
    if not st.button('Validate selected run', key='validate-' + str(canary)):
        st.caption('Capture: not evaluated. Validation is explicit and selected-run only; reruns do not automatically repeat it. Row display limits never truncate coverage checks.')
        return
    con = ctx['con']
    errors = []
    try:
        # Disable spill: private telemetry/credentials must not enter a disk cache.
        con.execute("SET temp_directory=''")
        con.execute("SET memory_limit='256MB'")
        with st.spinner('Reading selected-run observations; other runs are not evaluated…'):
            available = False
            if run['selectors']:
                _, errors, available = prepare_data(con, ctx['data_root'], ctx['unlabelled_host'],
                    telemetry_files=ctx['telemetry_files'])
            if available and run['selectors']:
                materialize_run(con, run, ctx['padding'])
            evaluation = evaluate_run(con, run, available, ctx['padding'])
            mark_overlaps(ctx['runs'], {(test, selected): evaluation}, ctx['padding'])
        if errors or ctx['errors']:
            evaluation['reasons'].append('Unreadable dataset/evidence files; completeness is unknown')
            if evaluation['state'] == 'green':
                evaluation['state'] = 'yellow'
        st.write(f"{ICONS[evaluation['state']]} **{evaluation['state'].title()}** — {evaluation['scope']}")
        for reason in evaluation['reasons']:
            st.caption('S3 query unavailable (details suppressed)' if ctx['remote'] and any(c['error'] and c['error'] in reason for c in evaluation['cases']) else reason)
        for case in evaluation['cases']:
            st.subheader(case['selector'].get('case', case['selector']['domain']))
            if case['selector'].get('skips'):
                st.warning('Skipped stimulus: ' + '; '.join(case['selector']['skips']))
            if case['error']:
                st.warning('Selected observations unavailable; no capture PASS' if ctx['remote'] else case['error'])
                continue
            st.dataframe(case['summary'], width='stretch')
            st.dataframe(case['checks'], width='stretch')
            with st.expander('Tailored query (in-memory selected observations)'):
                st.code(case['sql'], language='sql')
            if case.get('receipts'):
                st.json(case['receipts'])
            result = con.execute(f"SELECT * FROM ({case['sql']}) LIMIT {int(ctx['row_limit'])}")
            st.dataframe([dict(zip([c[0] for c in result.description], r)) for r in result.fetchall()], width='stretch')
            st.caption(f"{case['rows']:,} matched rows; displaying at most {ctx['row_limit']}. Checks use the full accepted working set.")
    except Exception as error:
        st.error('Selected-run validation unavailable; no capture PASS. Read or memory budget failed (remote details suppressed).' if ctx['remote'] else str(error))
