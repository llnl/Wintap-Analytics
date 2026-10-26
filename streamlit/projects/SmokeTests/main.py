"""Run: streamlit run streamlit/projects/SmokeTests/main.py"""
import os

import duckdb
import streamlit as st

from queries import load_manifests
from s3_source import discover_files, load_config, open_source


def main():
    st.set_page_config(page_title='Smoke test results', page_icon='🧪', layout='wide')
    st.title('Smoke test results')
    st.caption('Telemetry read-only • saved analysis summaries • no test execution')
    with st.sidebar:
        source = st.radio('Dataset source', ['Local / mounted', 'Garage / S3'],
            index=1 if os.environ.get('WINTAP_SMOKE_CONFIG') else 0)
        remote = source == 'Garage / S3'
        data_root = st.text_input('Parquet root on this analysis machine', os.environ.get('WINTAP_DATA_ROOT', ''))
        manifest_root = st.text_input('Optional JSON manifest directory', '')
        uploads = st.file_uploader('Or upload completed smoke manifests', type='json', accept_multiple_files=True)
        unlabelled_host = st.text_input('Host for unlabelled direct-parquet files', '',
            help='Only assert this for a source root belonging entirely to one test host, never the analysis-machine hostname.')
        padding = st.number_input('Time-window tolerance (seconds)', 0, 120, 15)
        row_limit = st.number_input('Displayed rows per case', 10, 10000, 200)
        if remote:
            path = st.text_input('Local S3 JSON config', os.environ.get('WINTAP_SMOKE_CONFIG', ''))
            if not path:
                st.info('Select a private JSON config; credentials stay in the AWS environment/profile.')
                return
            try:
                config = load_config(path)
            except ValueError as error:
                st.error(str(error))
                return
            start = st.text_input('Start partition day (UTC, YYYYMMDD)', config['start_day'])
            end = st.text_input('End partition day (UTC, YYYYMMDD)', config['end_day'])
            st.caption('Publication/collection partitions are not run boundaries or a completeness watermark. Include adjacent days around midnight.')
            if config['endpoint'].startswith('http://'):
                st.warning('Configured endpoint uses unencrypted HTTP; use HTTPS unless intentionally isolated.')
        st.button('Refresh files / results')
    con = client = None
    try:
        snapshot = {}
        evidence_files = telemetry_files = None
        if remote:
            con, client = open_source(config)
            evidence_files, telemetry_files = discover_files(client, config, start, end, snapshot=snapshot)
            st.caption(f'S3: {len(evidence_files)} evidence files and {len(telemetry_files)} telemetry files listed. Telemetry is read only on explicit validation.')
        else:
            con = duckdb.connect(':memory:')
        runs, errors = load_manifests(manifest_root, [(f.name, f.getvalue()) for f in uploads or []],
            data_root='' if remote else data_root, connection=con, evidence_files=evidence_files)
        for error in errors:
            st.warning(error)
        hosts = sorted({r['host']['hostname'].lower() for r in runs})
        selected_hosts = st.sidebar.multiselect('Test hosts', hosts, default=hosts)
        ctx = dict(con=con, remote=remote, runs=runs, errors=errors,
            client=client, config=config if remote else None, snapshot=snapshot,
            source_id=config['endpoint'] if remote else data_root,
            window=[start, end] if remote else None,
            visible_runs=[r for r in runs if r['host']['hostname'].lower() in selected_hosts],
            data_root='' if remote else data_root, telemetry_files=telemetry_files,
            unlabelled_host=unlabelled_host, padding=padding, row_limit=row_limit)
        st.session_state['_smoke_context'] = ctx
        pages = [st.Page('views/overview.py', title='Overview', default=True, url_path='overview'),
                 st.Page('views/canary.py', title='Canary Tests', url_path='canary-tests'),
                 st.Page('views/devtime.py', title='Dev-time Tests', url_path='devtime-tests')]
        st.navigation(pages).run()
    except Exception as error:
        st.error('Cannot read S3 source; details suppressed to protect credentials.' if remote else str(error))
    finally:
        st.session_state.pop('_smoke_context', None)
        if client is not None and hasattr(client, 'close'):
            client.close()
        if con is not None:
            con.close()


if __name__ == '__main__':
    main()
