"""One button for a canary round, persisted summary reuse and collector context."""
from pathlib import Path

import streamlit as st

from analysis import analyze_round, canary_rounds, input_fingerprint
from result_store import load_latest, load_result, save_result
from s3_source import discover_host_files


def show_report(report):
    st.subheader('All-validation summary')
    st.caption(report['scope'])
    st.caption('Analyzed: ' + report['analyzed_at'] + '. Coverage is separate from generation success; disabled/failed collectors explain gaps, not PASS.')
    for error in report['errors']:
        st.warning(error)
    for test in report['missing_families']:
        st.warning('No evidence supplied for expected family: ' + test)
    st.dataframe([dict(test=r['title'], harness=r['harness'], triage=r['state'],
        cases=len(r['cases']), observed=sum(c['observation'] == 'observed' for c in r['cases']),
        missing_checks=sum(len(c['missing']) for c in r['cases']), violations=sum(len(c['violations']) for c in r['cases']),
        skipped=len(r['skips']) + sum(bool(c['skips']) for c in r['cases']), runtime=r['runtime']['status'])
        for r in report['results']], width='stretch')
    st.dataframe([dict(test=r['title'], case=c['case'], domain=c['domain'], observation=c['observation'], rows=c['rows'],
        missing='; '.join(c['missing']), violations='; '.join(c['violations']),
        collectors=', '.join(n + ': ' + s for n, s in c['runtime']['collectors'].items()),
        explanation=c['runtime']['explanation'], skips='; '.join(c['skips']))
        for r in report['results'] for c in r['cases']], width='stretch')
    st.subheader('Sensor runtime configuration comparison')
    for r in report['results']:
        context = r['runtime']
        for skip in r['skips']:
            st.warning(r['title'] + ' — skipped: ' + skip.get('case', 'unsupported') + ' — ' + skip.get('reason', 'unsupported'))
        with st.expander(r['title'] + ' — ' + context['status']):
            st.caption(context['reason'])
            st.caption(context.get('hostname_correlation', 'unknown hostname attribution'))
            st.dataframe([dict(collector=n, enabled=s['enabled'], startup=s['status'], tier=s['tier'],
                hooks=', '.join(k + ': ' + str(v) for k, v in s['hooks'].items())) for n, s in context['sensors'].items()], width='stretch')
            st.json(context.get('settings', {}))
            st.json({n: s.get('features', {}) for n, s in context['sensors'].items()})
            for reason in r['reasons']:
                st.caption(reason)
    with st.expander('Saved summary JSON (no raw events, connection configuration or credentials)'):
        st.json(report)


def canary_batch_page(ctx):
    groups = canary_rounds(ctx['visible_runs'])
    if not groups:
        st.info('No expanded canary rounds supplied yet. Legacy individual stimulus runs remain below.')
        return
    by_id = {g['key']: g for g in groups}
    selected = st.selectbox('Canary round', list(by_id), key='canary-round',
        format_func=lambda k: f"{by_id[k]['host']} · {max(r['startedAtUtc'] for r in by_id[k]['runs'])} · {len(by_id[k]['runs'])} families")
    group = by_id[selected]
    ctx = dict(ctx, analysis_group=selected)
    st.caption('Membership: ' + group['method'] + '. Missing families stay explicit; separate rounds are never silently combined.')
    alias = st.checkbox('Use unique short/FQDN hostname correlation (inferred, never identity certification)', value=True)
    force = st.checkbox('Revalidate even if a saved result matches current inputs', value=False)
    st.caption('Validation writes a summary under analysis/smoke-tests/v1 beside the dataset (first configured S3 root). Raw telemetry and manifests are never modified. Existing results are reused only for matching object/evidence/code/settings fingerprints.')
    try:
        snapshot = dict(ctx['snapshot'])
        if ctx['remote']:
            host_files = discover_host_files(ctx['client'], ctx['config'], snapshot)
            if len(snapshot) > ctx['config']['max_files']:
                raise ValueError('Combined telemetry/HOST history file limit exceeded')
            telemetry = ctx['telemetry_files']
        else:
            root = Path(ctx['data_root']).expanduser()
            files = sorted(root.rglob('*.parquet')) if ctx['data_root'] and root.exists() else []
            snapshot = {str(p.resolve()): [p.stat().st_size, p.stat().st_mtime_ns] for p in files}
            host_files = [p for p in files if 'raw_host' in p.parts]
            telemetry = [p for p in files if 'raw_smoke_test' not in p.parts]
        settings = dict(padding=ctx['padding'], unlabelled_host=ctx['unlabelled_host'], window=ctx['window'],
                        max_rows=100000, memory_mb=256, hostname_aliases=alias, evidence_errors=ctx['errors'])
        fingerprint = input_fingerprint(group['runs'], ctx['runs'], snapshot, settings, ctx['source_id'])
        report = None
        saved = False
        memory = st.session_state.get('_canary_analysis')
        if memory and memory['fingerprint'] == fingerprint:
            report, saved = memory['report'], memory['saved']
        else:
            try:
                report = load_result(ctx, fingerprint)
                saved = report is not None
                if report is None:
                    report = load_latest(ctx)
                    saved = report is not None
            except Exception:
                st.warning('Saved result unavailable; verify analysis-prefix read permissions. You can still validate; private details suppressed.')
        if st.button('Run all validations for this canary', key='validate-canary-round'):
            if report is not None and report['fingerprint'] == fingerprint and not force:
                st.info('Reusing matching saved/in-memory analysis; no telemetry scan.')
            else:
                with st.spinner('Validating all families and runtime context with one shared observation scan…'):
                    report = analyze_round(ctx['con'], group['runs'], ctx['runs'], telemetry, host_files,
                        data_root=ctx['data_root'], unlabelled_host=ctx['unlabelled_host'], padding=ctx['padding'],
                        evidence_errors=ctx['errors'], fingerprint=fingerprint, allow_hostname_aliases=alias)
                saved = False
            if not saved:
                try:
                    save_result(ctx, report)
                    saved = True
                except Exception:
                    st.warning('Computed, but result was NOT persisted. Grant write access only to the analysis prefix; no credentials or raw-data permissions need changing here.')
            st.session_state['_canary_analysis'] = dict(fingerprint=fingerprint, report=report, saved=saved)
        if report is not None:
            if report['fingerprint'] != fingerprint:
                st.warning('STALE snapshot: source objects, manifests, evaluator or settings changed. This is prior analysis, not current coverage. Click Run all validations to recompute.')
            st.caption('Persisted summary loaded; no automatic telemetry validation.' if saved else 'Memory-only summary; not acknowledged as persisted.')
            show_report(report)
        else:
            st.info('This input snapshot has no saved analysis. Click Run all validations for this canary.')
    except Exception:
        st.error('Cannot prepare canary analysis/cache identity; no stale or truncated result accepted (details suppressed).')
