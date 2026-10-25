"""Execute actual corrected DBT SQL in memory against the immutable real sample."""
import json
import datetime as dt
import hashlib
from pathlib import Path
import duckdb
import jinja2

ROOT = Path(__file__).resolve().parents[3]
DBT = ROOT.parent / 'Wintappy/wintap_dbt'
DB = Path('/Users/johnson30/git/axon-aegis-micro-range/data/lintap/duckdb/wintap.duckdb')
c = duckdb.connect(':memory:')
c.execute(f"attach '{DB}' as wintap (read_only)")
before = DB.stat()
for (t,) in c.execute("select table_name from information_schema.tables where table_catalog='wintap' and table_schema='main'").fetchall():
    c.execute(f'create temporary table "{t}" as select * from wintap.main."{t}"')
env = jinja2.Environment(undefined=jinja2.StrictUndefined)
module = env.from_string('\n'.join((DBT / 'macros' / n).read_text() for n in ['time.sql', 'ip.sql'])).module
env.globals.update({n: getattr(module, n) for n in dir(module) if not n.startswith('_')})
refs = {}
source_hashes = {}
env.globals['ref'] = lambda name: refs.get(name, name)


def build(name, area):
    path = DBT / 'models' / area / (name + '.sql')
    source_hashes[str(path.relative_to(DBT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    sql = env.from_string(path.read_text()).render()
    target = name + '_corrected'
    c.execute(f'create temporary table {target} as ' + sql)
    refs[name] = target


build('process_file_summary', 'gold')
build('process_conn_incr', 'silver')
build('process_net_conn', 'silver')
build('process_net_summary', 'gold')
build('process_summary', 'gold')
build('process_uber_summary', 'gold')
queries = {
    'summary_multiplicity': "select 'original' variant,count(*) rows_total,count(distinct pid_hash) hashes from process_summary union all select 'corrected',count(*),count(distinct pid_hash) from process_summary_corrected",
    'uber_summary_multiplicity': "select 'original' variant,count(*) rows_total,count(distinct pid_hash) hashes from process_uber_summary union all select 'corrected',count(*),count(distinct pid_hash) from process_uber_summary_corrected",
    'file_counters': "select 'original' variant,sum(Read_Events) reads,sum(Write_Events) writes,sum(Close_Events) closes,sum(Delete_Events) deletes,sum(Read_Bytes) read_bytes,sum(Write_Bytes) write_bytes from process_file_summary union all select 'corrected',sum(Read_Events),sum(Write_Events),sum(Close_Events),sum(Delete_Events),sum(Read_Bytes),sum(Write_Bytes) from process_file_summary_corrected",
    'file_conservation': "select (select sum(event_count) from process_file) input_events,sum(Open_Events+Close_Events+Create_Events+Delete_Events+Rename_Events+SetInfo_Events+Read_Events+Write_Events) output_events from process_file_summary_corrected",
    'network_null_counters': "select 'original' variant,count(*) filter(where tcp_send_count is null and tcp_recv_count is null and tcp_connect_count is null and tcp_disconnect_count is null and udp_send_count is null and udp_recv_count is null) all_basic_null from process_conn_incr union all select 'corrected',count(*) filter(where tcp_send_count is null and tcp_recv_count is null and tcp_connect_count is null and tcp_disconnect_count is null and udp_send_count is null and udp_recv_count is null) from process_conn_incr_corrected",
    'network_conservation': "select (select sum(total_events) from process_conn_incr) input_events,(select sum(total_events) from process_conn_incr_corrected) output_events,(select sum(total_size) from process_conn_incr) input_bytes,(select sum(total_size) from process_conn_incr_corrected) output_bytes",
    'duration_accuracy': "select 'original' variant,count(*) filter(where abs(duration_seconds-epoch(process_term-process_started))>.001) incorrect_rows from process_summary union all select 'corrected',count(*) filter(where abs(duration_seconds-epoch(process_term-process_started))>.001) from process_summary_corrected",
    'orphans_not_hidden': "select count(*) file_orphan_rows from process_file f where not exists(select 1 from process p where p.pid_hash=f.pid_hash)",
}
results = {}
for key, sql in queries.items():
    cur = c.execute(sql)
    results[key] = dict(sql=sql, rows=[dict(zip([d[0] for d in cur.description], row)) for row in cur.fetchall()])
after = DB.stat()
results['source_file_unchanged'] = before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns
results['provenance'] = dict(run_utc=dt.datetime.now(dt.timezone.utc).isoformat(), database=str(DB),
    source_size=before.st_size, source_mtime_ns=before.st_mtime_ns, sql_sha256=source_hashes,
    mode='source attached READ_ONLY; all corrected relations temporary/in-memory')
Path(__file__).with_name('experiment_sample_projection.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
assert results['source_file_unchanged']
assert results['summary_multiplicity']['rows'][1]['rows_total'] == results['summary_multiplicity']['rows'][1]['hashes']
assert results['uber_summary_multiplicity']['rows'][1]['rows_total'] == results['uber_summary_multiplicity']['rows'][1]['hashes']
assert results['file_conservation']['rows'][0]['input_events'] == results['file_conservation']['rows'][0]['output_events']
assert results['duration_accuracy']['rows'][1]['incorrect_rows'] == 0
assert results['network_null_counters']['rows'][1]['all_basic_null'] == 0
network = results['network_conservation']['rows'][0]
assert network['input_events'] == network['output_events']
assert network['input_bytes'] == network['output_bytes']
