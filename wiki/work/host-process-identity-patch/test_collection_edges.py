import pytest

from collection_edges import classify_event, classify_interval, report, validate_bounds
from collection_edge_analysis import clock_verified, sensor_bounds


S = 10_000_000
BOUNDS = dict(start_min=100*S, start_max=102*S, end_min=200*S,
              end_max=202*S, clock_verified=True, source='test brackets')


@pytest.mark.parametrize('second,expected', [
    (99, 'outside'), (100, 'uncertain'), (101, 'uncertain'),
    (102, 'start_edge'), (109, 'start_edge'), (110, 'uncertain'),
    (112, 'interior'), (189, 'interior'), (190, 'uncertain'),
    (192, 'end_edge'), (199, 'end_edge'), (200, 'uncertain'),
    (201, 'uncertain'), (202, 'outside')])
def test_uncertain_transition_brackets(second, expected):
    assert classify_event(second*S, BOUNDS) == expected


def test_half_open_exact_bounds():
    b = dict(BOUNDS, start_max=100*S, end_max=200*S)
    assert classify_event(100*S, b) == 'start_edge'
    assert classify_event(110*S, b) == 'interior'
    assert classify_event(190*S, b) == 'end_edge'
    assert classify_event(200*S, b) == 'outside'


@pytest.mark.parametrize('bounds', [None, {}, dict(BOUNDS, clock_verified=False),
    dict(BOUNDS, start_max=203*S), dict(BOUNDS, source=''),
    dict(BOUNDS, end_max=202.0*S), dict(BOUNDS, start_min=-1)])
def test_unverified_bounds_never_become_edges(bounds):
    assert not validate_bounds(bounds)
    assert classify_event(150*S, bounds) == 'unclassified'


def test_spans_and_short_capture_stay_uncertain():
    assert classify_interval(109*S, 113*S, BOUNDS) == 'uncertain'
    assert classify_interval(150*S, 151*S, BOUNDS) == 'interior'
    assert classify_interval(199*S, 201*S, BOUNDS) == 'uncertain'
    short = dict(BOUNDS, end_min=115*S, end_max=117*S)
    assert classify_event(108*S, short) == 'uncertain'


@pytest.mark.parametrize('first,last', [(None,None), (0,0), (160*S,150*S), ('1','2')])
def test_missing_or_invalid_event_time(first, last):
    assert classify_interval(first, last, BOUNDS) == 'unclassified'


def test_conservation_errors_retained_in_every_sensitivity():
    rows = [dict(first=105*S, last=105*S, counts={'identity_errors': 3}),
            dict(first=150*S, last=151*S, counts={'missing_payload_events': 7}),
            dict(first=None, last=None, counts={'missing_paths': 2})]
    result = report(rows, BOUNDS)
    for bands in result['bands'].values():
        assert sum(b.get('records', 0) for b in bands.values()) == 3
        assert sum(b.get('identity_errors', 0) for b in bands.values()) == 3
        assert sum(b.get('missing_payload_events', 0) for b in bands.values()) == 7
        assert sum(b.get('missing_paths', 0) for b in bands.values()) == 2
    assert result['strict_gates_unchanged']
    assert result['bands']['10']['interior']['missing_payload_events'] == 7


def test_no_clock_or_collector_birth_fallback():
    result = report([dict(first=150*S, last=150*S)], {'collector_birth': 100*S})
    assert result['bands']['10']['unclassified']['records'] == 1


@pytest.mark.parametrize('width', [0, -1, 1.5, True])
def test_bad_width(width):
    with pytest.raises(ValueError):
        classify_event(150*S, BOUNDS, width)


def clock_round():
    import datetime as dt
    start = int(dt.datetime(2026,10,24,14,59,tzinfo=dt.timezone.utc).timestamp())*1_000_000_000
    a = dict(unix_ns=start, monotonic_ns=5_000_000_000,
             local_utc_offset_seconds=-25200, localtime_sha256='zone', harness_TZ=None)
    b = dict(a, unix_ns=start+800_000_000_000, monotonic_ns=805_000_000_000)
    return dict(clock_start=a, clock_end=b, collector_TZ=None)


def test_clock_requires_independent_complete_receipts():
    r = clock_round()
    assert clock_verified(r)
    assert not clock_verified({})
    assert not clock_verified(dict(r, collector_TZ='UTC'))
    r['clock_end']['unix_ns'] += 2_000_000_000
    assert not clock_verified(r)


def test_local_log_offset_and_second_uncertainty():
    log = '\n'.join(f'10/24/2026 08:{minute}:00 [Info]: {marker}' for minute, marker in [
        ('00','Starting FileOps sensor...'), ('01','FileOps sensor started'),
        ('10','Stopping FileOps sensor...'), ('11','FileOps sensor stopped')])
    r = clock_round()
    b = sensor_bounds(log, 'FileOps', r)
    import datetime as dt
    from collection_edges import unix_ns_to_filetime
    expected = unix_ns_to_filetime(int(dt.datetime(2026,10,24,15,1,tzinfo=dt.timezone.utc).timestamp())*1_000_000_000)
    assert b['start_max'] == expected + S
    assert b['evidence_kind'] == 'operational_envelope_not_delivery_guarantee'
    assert sensor_bounds(log, 'FileOps', {}) is None
    assert sensor_bounds(log+'\n'+log, 'FileOps', r) is None


def test_parquet_overlay_keeps_missing_payload_and_tcp_failure(tmp_path):
    import datetime as dt
    import json
    import duckdb
    from collection_edge_analysis import analyze_round
    from collection_edges import unix_ns_to_filetime
    qa, data = tmp_path/'qa', tmp_path/'data'
    logdir = qa/'round/runtime-snapshot/Logs'
    logdir.mkdir(parents=True)
    (qa/'host-provenance.json').write_text(json.dumps({'hostname':'test-host'}))
    lines = []
    for sensor in ('FileOps','Network'):
        lines += [f'10/24/2026 08:{minute}:00 [Info]: {marker}' for minute,marker in [
            ('00',f'Starting {sensor} sensor...'), ('01',f'{sensor} sensor started'),
            ('10',f'Stopping {sensor} sensor...'), ('11',f'{sensor} sensor stopped')]]
    (logdir/'Lintap.log').write_text('\n'.join(lines))
    stamp = int(dt.datetime(2026,10,24,15,5,tzinfo=dt.timezone.utc).timestamp())*1_000_000_000
    ft = unix_ns_to_filetime(stamp)
    raw = data/'round/raw_sensor'
    (raw/'raw_process_file').mkdir(parents=True)
    (raw/'raw_process').mkdir()
    expected = '/native/qa/workload/payload/fast-123/file-0.txt'
    with duckdb.connect(':memory:') as c:
        c.execute('create table files(firstseen bigint,lastseen bigint,pidhash varchar,processname varchar,file_path varchar,eventcount bigint)')
        c.executemany('insert into files values(?,?,?,?,?,?)',[
            (ft,ft,'known','python',expected,3), (ft,ft,'known','python',expected,4)])
        c.execute('copy files to ? (format parquet)',[str(raw/'raw_process_file/files.parquet')])
        c.execute("copy (select 'known' pidhash) to ? (format parquet)",[str(raw/'raw_process/process.parquet')])
    r = dict(clock_round(),name='round',qa_root='/native/qa',
             workload=dict(start_unix_ns=stamp,end_unix_ns=stamp+1_000_000_000,
                           children=[dict(pid=123,cohort='fast',payload_files=2)]),
             endpoint_selectors=[{'case':'tcp'}], endpoint_interval_start={'unix_ns':stamp},
             endpoint_interval_end={'unix_ns':stamp+1_000_000_000})
    strict = {'all_expected_paths':False,'endpoint_orientation':False}
    result = analyze_round(r,qa,data,strict,[dict(case='tcp',status='pending',missing=['server/send'],violations=[])])
    assert result['strict_gates'] == strict
    payload = result['missing_paths_stimulus_interval']['bands']['10']['interior']
    assert payload['missing_paths'] == 1
    assert payload['missing_payload_events'] == 7
    assert payload['excess_payload_events'] == 0
    endpoints = result['endpoint_stimulus_interval']['bands']['10']['interior']
    assert endpoints['endpoint_failed_cases'] == 1
    assert endpoints['endpoint_missing_observations'] == 1
