"""Comparison gates must retain counter changes and raw-precision failures."""
import importlib.util
from pathlib import Path
import duckdb
import pytest

spec = importlib.util.spec_from_file_location('compare_timestamp_models', Path(__file__).with_name('compare_timestamp_models.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def database(path, offset=0, counter=7, name='birth'):
    with duckdb.connect(str(path)) as c:
        c.execute("create table stg_raw_process as select 'hash' pidhash,'START' activitytype,116444736000000011::bigint eventtime,'birth' processname,'/proof' processpath,'arg' processargs union all select 'hash','STOP',116444736000000032,'exec','/proof','arg'")
        c.execute(f"create table process as select 'hash' pid_hash,'agent' agent_id,make_timestamptz({1+offset}) process_started,make_timestamptz({1+offset}) first_seen,make_timestamptz({3+offset}) last_seen,make_timestamptz({3+offset}) process_term,? process_name,'/proof' process_path,'arg' args", [name])
        c.execute('create table process_summary as select *,epoch(process_term-process_started) duration_seconds from process')
        c.execute('create table counters as select ?::bigint event_count', [counter])


@pytest.mark.parametrize('counter,name,offset,protected_failure,metadata_failure,precision_failure', [
    (7,'exec',0,False,False,False),
    (8,'birth',0,True,False,False),
    (7,'fabricated',0,False,True,False),
    (7,'birth',1,False,False,True)])
def test_comparison_keeps_independent_gates(tmp_path,counter,name,offset,protected_failure,metadata_failure,precision_failure):
    before, after = tmp_path/'old.duckdb', tmp_path/'new.duckdb'
    database(before, offset=-1)
    database(after, offset=offset, counter=counter, name=name)
    result = module.compare(before,after)
    assert any(t['protected_rows_added']>0 for t in result['tables']) == protected_failure
    assert bool(result['unordered_metadata_source_failures']) == metadata_failure
    assert bool(result['precision_failures']) == precision_failure
