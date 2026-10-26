"""Read-only historical QA; snapshot relations in memory, never rebuild the DB.

Run from Wintap-Analytics root: python3 wiki/work/host-process-identity-patch/sample_db_audit.py
Results include the SQL for reproducibility. No sensor/source changes are made.
"""
import datetime
import hashlib
import json
import re
from pathlib import Path
import duckdb

DB = Path('/Users/johnson30/git/axon-aegis-micro-range/data/lintap/duckdb/wintap.duckdb')
OUT = Path(__file__).with_name('sample_db_audit_results.json')
ROOT = Path(__file__).resolve().parents[3]
c = duckdb.connect(':memory:')
c.execute("ATTACH '" + str(DB).replace("'", "''") + "' AS wintap (READ_ONLY)")
before = DB.stat()
tables = c.execute("select table_name from information_schema.tables where table_catalog='wintap' and table_schema='main'").fetchall()
results = {'database': str(DB), 'run_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'connection': 'in-memory; attached source READ_ONLY; tables/views snapshotted in memory', 'checks': {}}
for (t,) in tables:
    c.execute(f'CREATE TEMP TABLE "{t}" AS SELECT * FROM wintap.main."{t}"')

def check(name, sql):
    sql = sql.replace(' rows,', ' row_count,').replace(' rows from', ' row_count from')
    cursor = c.execute(sql)
    rows = [dict(zip([d[0] for d in cursor.description], row)) for row in cursor.fetchall()]
    results['checks'][name] = {'sql': sql, 'rows': rows}
    print(name, json.dumps(rows, default=str)[:2200], flush=True)
    return rows

check('inventory', "select table_name, estimated_size rows from duckdb_tables() where temporary order by table_name")
# Execute the canonical orphan/PK QA, dropping only DuckDB CLI meta-commands.
qa = (ROOT.parent / 'Wintappy/wintap_dbt/qa/pid_hash_orphan_checks.sql').read_text()
qa = '\n'.join(line for line in qa.splitlines() if not line.startswith('.'))
for index, statement in enumerate(c.extract_statements(qa)):
    check(f'canonical_orphan_qa_{index}', statement.query)

# Run the applicable schema.yml generic tests directly, without DBT rebuilds.
# This file's schema uses scalar test names and one accepted_values block.
schema = (ROOT.parent / 'Wintappy/wintap_dbt/models/schema.yml').read_text()
model = column = None
for line in schema.splitlines():
    if match := re.match(r'  - name: (\w+)$', line):
        model = match[1]
    elif match := re.match(r'      - name: (\w+)$', line):
        column = match[1]
    elif match := re.match(r'          - (not_null|unique|no_forbidden_pid_hash_values)$', line):
        test = match[1]
        if test == 'not_null':
            condition = f'"{column}" is null'
        elif test == 'no_forbidden_pid_hash_values':
            condition = f"lower(cast(\"{column}\" as varchar)) in ('fixmepid','fixparentpidhash') or lower(cast(\"{column}\" as varchar)) like 'unknown-%'"
        else:
            check(f'schema_{model}_{column}_{test}', f'SELECT count(*) failing_groups FROM (SELECT "{column}" FROM "{model}" GROUP BY 1 HAVING count(*)>1)')
            continue
        check(f'schema_{model}_{column}_{test}', f'SELECT count(*) failing_rows FROM "{model}" WHERE {condition}')
check('schema_network_protocol_partition', "select count(*) failing_rows from stg_raw_process_conn_incr where protoPK not in ('tcp','udp')")
network_gate = (ROOT.parent / 'Wintappy/wintap_dbt/tests/network_activity_names.sql').read_text()
network_gate = network_gate.replace("{{ ref('stg_raw_process_conn_incr') }}", 'stg_raw_process_conn_incr')
check('network_activity_vocabulary_gate', network_gate)

check('process_by_host', """select hostname,count(*) identities,
 count(*) filter(where num_process_start=0) stop_only,
 count(*) filter(where num_process_stop=0) start_only,
 count(*) filter(where num_process_start>0 and num_process_stop>0) paired,
 count(*) filter(where num_process_start>1) multiple_start_observations,
 count(*) filter(where process_term<process_started) negative_lifetime,
 count(*) filter(where user_name is null) null_user,
 count(*) filter(where lower(user_name) like 'unknown%') unknown_user,
 count(*) filter(where num_parent_pid_hash>1) multiple_parent_hashes,
 count(*) filter(where num_process_name>1) multiple_names,
 count(*) filter(where num_agent_id>1) multiple_agents
 from process group by hostname""")
check('parents', """select c.hostname,count(*) child_identities,
 count(*) filter(where c.parent_pid_hash is null or c.parent_pid_hash='') missing_parent_hash,
 count(*) filter(where c.parent_pid_hash=c.pid_hash) self_parent,
 count(*) filter(where c.parent_pid_hash is not null and p.pid_hash is null) missing_parent_entity,
 count(*) filter(where p.pid_hash is not null and c.parent_os_pid is not null and c.parent_os_pid!=p.os_pid) parent_pid_disagrees,
 count(*) filter(where p.pid_hash is not null and c.process_started<p.process_started) parent_starts_after_child,
 count(*) filter(where p.pid_hash is not null and c.process_started>p.process_term) child_starts_after_parent_stop
 from process c left join process p on c.parent_pid_hash=p.pid_hash and c.hostname=p.hostname group by 1""")
check('parent_missing_by_lifecycle', """select c.hostname,c.num_process_start>0 has_start,count(*) identities,
 count(*) filter(where c.parent_pid_hash is not null and p.pid_hash is null) missing_parent
 from process c left join process p on c.parent_pid_hash=p.pid_hash and c.hostname=p.hostname group by 1,2""")
for t in ['stg_raw_process','stg_raw_process_file','stg_raw_process_conn_incr']:
    check(t+'_basic', f"""select hostname,activitytype,count(*) rows,count(distinct pidhash) hashes,
 sum(num_dups)-count(*) exact_duplicate_excess,
 count(*) filter(where nullif(trim(pidhash),'') is null) missing_hash,
 count(*) filter(where lower(pidhash) like 'unknown-%' or lower(pidhash) in ('fixmepid','fixparentpidhash')) forbidden_hash,
 count(*) filter(where nullif(trim(processname),'') is null) missing_name,
 count(*) filter(where lower(processname) like 'unknown%') unknown_name,
 count(*) filter(where not regexp_full_match(pidhash,'[0-9A-Fa-f]{{32}}')) non_hex_hash,
 min(eventtime) min_event,max(eventtime) max_event
 from {t} group by 1,2 order by 1,2""")
    check(t+'_identity_integrity', f"""select count(*) conflicting_hash_groups from
 (select pidhash from {t} group by 1 having count(distinct hostname)>1 or count(distinct pid)>1)""")
    check(t+'_raw_parent_join', f"""select r.hostname,count(*) rows,
 count(*) filter(where p.pidhash is null) no_raw_process,
 count(*) filter(where p.has_start is not true) no_raw_start,
 count(distinct r.pidhash) filter(where p.pidhash is null) orphan_hashes
 from {t} r left join (select hostname,pidhash,bool_or(upper(activitytype) in ('START','REFRESH')) has_start from stg_raw_process group by 1,2) p
 on r.hostname=p.hostname and r.pidhash=p.pidhash group by 1""")

check('raw_users', "select hostname,activitytype,username,count(*) rows,count(distinct pidhash) hashes from stg_raw_process group by all order by 4 desc")
check('unknown_user_details', "select hostname,pid,pidhash,agentid,eventtime,processname,processpath,parentpid,parentpidhash,num_dups from stg_raw_process where lower(username) like 'unknown%' order by eventtime")
check('numeric_uid_zero', "select hostname,count(*) rows,count(distinct pidhash) hashes,count(*) filter(where username='0') numeric_zero,count(*) filter(where username='root') root from stg_raw_process where activitytype='Refresh' group by 1")
check('capture_agents', "select hostname,agentid,count(*) rows,min(eventtime) first_event,max(eventtime) last_event from stg_raw_process group by all order by 1,4")
check('host_metadata', "select hostname,agentid,os,osversion,lastboot,wintapversion,etlversion,collectors,count(*) rows,min(eventtime) first_event,max(eventtime) last_event from stg_raw_host group by all")
check('host_family', "select hostname,os_family,os,os_version,arch from host")
check('raw_stop_names', "select hostname,processname,count(*) rows from stg_raw_process where upper(activitytype)='STOP' group by 1,2 order by 3 desc limit 30")
check('raw_start_precision', """select hostname,activitytype,count(*) rows,
 count(*) filter(where eventtime%100000=99999) one_tick_before_10ms,
 count(*) filter(where starttime!=eventtime) starttime_disagrees,
 count(*) filter(where receivetime=0) zero_receivetime,
 count(*) filter(where receivetime>0 and receivetime<eventtime) negative_delivery,
 min((receivetime-eventtime)/10000000.0) filter(where receivetime>0) min_delivery_s,
 max((receivetime-eventtime)/10000000.0) filter(where receivetime>0) max_delivery_s
 from stg_raw_process group by 1,2""")
check('near_identical_start_times', """select hostname,count(*) adjacent_pairs,count(*) filter(where delta=1) one_100ns_tick,
 count(*) filter(where delta>1) other_sub10ms from
 (select hostname,pid,agentid,eventtime,pidhash,eventtime-lag(eventtime) over(partition by hostname,pid,agentid order by eventtime) delta
 from (select distinct hostname,pid,agentid,eventtime,pidhash from stg_raw_process where upper(activitytype) in ('START','REFRESH')))
 where delta>0 and delta<100000 group by 1""")
check('gold_multiplicity', """select 'process_summary' relation,count(*) rows,count(distinct pid_hash) hashes,count(*)-count(distinct pid_hash) extra_rows from process_summary
 union all select 'process_uber_summary',count(*),count(distinct pid_hash),count(*)-count(distinct pid_hash) from process_uber_summary""")
check('fanout_models', """select 'process_file_summary' relation,count(*) hash_groups,sum(n-1) extra_rows from (select pid_hash,count(*) n from process_file_summary group by 1 having count(*)>1)
 union all select 'process_net_summary',count(*),sum(n-1) from (select pid_hash,count(*) n from process_net_summary group by 1 having count(*)>1)""")
check('current_vs_raw_process_keys', """select 'raw_not_silver' direction,count(*) hashes from (select distinct pidhash from stg_raw_process except select pid_hash from process)
 union all select 'silver_not_raw',count(*) from (select pid_hash from process except select distinct pidhash from stg_raw_process)""")
for t,raw in [('process_file','stg_raw_process_file'),('process_conn_incr','stg_raw_process_conn_incr')]:
    check(t+'_orphans_host', f"""select c.hostname,count(*) rows,count(*) filter(where p.pid_hash is null) orphans,
 sum(c.num_raw_rows) raw_rows,sum(c.num_raw_rows) filter(where p.pid_hash is null) orphan_raw_rows,
 count(distinct c.pid_hash) filter(where p.pid_hash is null) orphan_hashes,
 count(*) filter(where p.pid_hash is not null and c.os_pid!=p.os_pid) pid_mismatch,
 count(*) filter(where p.pid_hash is not null and lower(c.process_name)!=lower(p.process_name)) name_mismatch
 from {t} c left join process p on c.pid_hash=p.pid_hash and c.hostname=p.hostname group by 1""")
    check(t+'_orphan_examples', f"""select c.hostname,c.os_pid,c.process_name,c.pid_hash,count(*) rows,min(c.first_seen) first_seen,max(c.last_seen) last_seen
 from {t} c left join process p on c.pid_hash=p.pid_hash and c.hostname=p.hostname where p.pid_hash is null group by 1,2,3,4 order by 5 desc limit 20""")
    check(t+'_lifetimes', f"""select c.hostname,count(*) matched_rows,
 count(*) filter(where c.first_seen<p.process_started-interval '100 milliseconds') before_start,
 count(*) filter(where c.last_seen>p.process_term+interval '1 second') after_stop
 from {t} c join process p on c.pid_hash=p.pid_hash and c.hostname=p.hostname group by 1""")
check('file_quality', """select hostname,count(*) rows,
 count(*) filter(where nullif(trim(file_path),'') is null) missing_path,
 count(*) filter(where file_path not like '/%') not_linux_absolute,
 count(*) filter(where file_path like '/proc/%/fd/%') proc_fd_path,
 count(*) filter(where file_path like '%socket:[%' or file_path like '%pipe:[%' or file_path like '%anon_inode:%') pseudo_path,
 count(*) filter(where bytesrequested<0) negative_bytes,
 count(*) filter(where eventcount<=0) nonpositive_eventcount,
 count(*) filter(where firstseen>lastseen) reversed_range
 from stg_raw_process_file group by 1""")
check('file_counter_spelling', """select activity_type,sum(event_count) observed_events,
 sum(bytes_requested) observed_bytes from process_file group by 1""")
check('file_summary_counters', """select count(*) summary_rows,sum(Close_Events) closes,sum(Read_Events) reads,sum(Write_Events) writes,sum(Delete_Events) deletes,sum(Read_Bytes) read_bytes,sum(Write_Bytes) write_bytes from process_file_summary""")
check('gold_duration_accuracy', """select count(*) terminated_rows,
 count(*) filter(where abs(duration_seconds-epoch(process_term-process_started))>0.001) wrong_duration,
 max(abs(duration_seconds-epoch(process_term-process_started))) maximum_error_seconds
 from process_summary where process_started is not null and process_term is not null""")
check('network_quality', """select hostname,protocol,activitytype,count(*) rows,sum(eventcount) events,sum(packetsize) bytes,
 count(*) filter(where pid<=0) nonpositive_pid,
 count(*) filter(where nullif(trim(connid),'') is null) missing_connid,
 count(*) filter(where localport not between 0 and 65535 or remoteport not between 0 and 65535) invalid_port,
 count(*) filter(where localport=0 or remoteport=0) zero_port,
 count(*) filter(where localipaddr=0 or remoteipaddr=0) zero_ip,
 count(*) filter(where packetsize<0 or eventcount<=0) invalid_measurement,
 count(*) filter(where firstseenms>lastseenms) reversed_range
 from stg_raw_process_conn_incr group by 1,2,3 order by 1,2,3""")
check('network_null_counters', """select hostname,protocol,count(*) rows,
 count(*) filter(where tcp_send_count is null and tcp_recv_count is null and tcp_connect_count is null and tcp_disconnect_count is null and udp_send_count is null and udp_recv_count is null) all_basic_counters_null,
 sum(total_events) events,sum(total_size) bytes from process_conn_incr group by 1,2""")
check('network_connection_tuple_collision', """select count(*) connids_with_distinct_canonical_tuples from (
 select connid from stg_raw_process_conn_incr group by connid having count(distinct (lower(protocol),least((localipaddr,localport),(remoteipaddr,remoteport)),greatest((localipaddr,localport),(remoteipaddr,remoteport))))>1)""")
check('network_local_host_ip', """select n.hostname,n.activitytype,count(*) rows,
 count(*) filter(where n.localipaddr not in (0,16777343) and not exists(select 1 from stg_raw_macip h where h.hostname=n.hostname and h.ipaddr=n.localipaddr)) local_not_in_host_inventory
 from stg_raw_process_conn_incr n group by 1,2 order by 1,2""")

# Historical versus pid-v2 formula checks. This is an independent QA oracle,
# not a second production hash implementation. All timestamp arithmetic is integer.
def digest(host,pid,time,agent=None):
    pre=f'Process_ID`llnl`{time}`{host}`' + (f'{agent}`' if agent is not None else '') + f'{pid}`'
    first=hashlib.md5(pre.encode()).hexdigest().upper()
    return hashlib.md5(f'N`Process`{first}`'.encode()).hexdigest().upper()

groups={}
raw=c.execute('select hostname,pid,agentid,activitytype,eventtime,starttime,pidhash from stg_raw_process').fetchall()
for h,p,a,act,t,start,v in raw:
    g=groups.setdefault((h,act),dict(rows=0,legacy_event_hash=0,legacy_lower_hostname_event_hash=0,legacy_start_hash=0,pid_v2_event_hash=0,legacy_unknown_sentinel=0))
    g['rows']+=1
    if None not in (h,p,a,t):
        g['legacy_event_hash']+=digest(h,p,t,a)==v
        g['legacy_lower_hostname_event_hash']+=digest(h.lower(),p,t,a)==v
        g['legacy_start_hash']+=start is not None and digest(h,p,start,a)==v
        g['pid_v2_event_hash']+=digest(h.strip().upper(),p,t)==v
        g['legacy_unknown_sentinel']+=digest(h,-1,0,a)==v
results['checks']['hash_formula']={'rows':[dict(hostname=h,activity=act,**g) for (h,act),g in groups.items()]}
print('hash_formula',results['checks']['hash_formula'],flush=True)
fg={}
for h,p,a,first,last,event,v,pname in c.execute('select hostname,pid,agentid,firstseen,lastseen,eventtime,pidhash,processname from stg_raw_process_file').fetchall():
    g=fg.setdefault(h,dict(rows=0,firstseen_hash_matches=0,lastseen_hash_matches=0,unknown_firstseen_hash_matches=0))
    g['rows']+=1
    matches=digest(h.lower(),p,first,a)==v
    g['firstseen_hash_matches']+=matches
    g['lastseen_hash_matches']+=digest(h.lower(),p,last,a)==v
    g['unknown_firstseen_hash_matches']+=matches and pname.lower().startswith('unknown')
results['checks']['file_event_time_hash']={'rows':[dict(hostname=h,**g) for h,g in fg.items()]}
print('file_event_time_hash',results['checks']['file_event_time_hash'],flush=True)
check('file_lag', """select hostname,lower(processname)='unknown' unknown_owner,count(*) row_count,
 quantile_cont(eventtime-(firstseen-116444736000000000)/10000000.0,0.5) median_flush_minus_event_s,
 quantile_cont(eventtime-(firstseen-116444736000000000)/10000000.0,0.95) p95_flush_minus_event_s,
 max(eventtime-(firstseen-116444736000000000)/10000000.0) max_flush_minus_event_s
 from stg_raw_process_file group by 1,2""")
check('unknown_file_hotspots', """select hostname,pid,count(*) row_count,count(distinct pidhash) hashes,
 min(firstseen) first_event,max(lastseen) last_event,min(eventtime) first_flush,max(eventtime) last_flush
 from stg_raw_process_file where lower(processname)='unknown' group by 1,2 order by 3 desc limit 12""")
check('file_orphan_classification', """select r.hostname,lower(r.processname)='unknown' unknown_owner,count(*) row_count,
 count(distinct r.pidhash) hashes from stg_raw_process_file r
 where not exists(select 1 from process p where p.pid_hash=r.pidhash and p.hostname=r.hostname) group by 1,2""")
check('birth_stop_pid_pair', """select s.hostname,count(*) stop_only,
 count(*) filter(where exists(select 1 from process b where b.hostname=s.hostname and b.os_pid=s.os_pid and b.num_process_start>0 and b.process_started<=s.process_term and b.process_started>=s.process_term-interval '10 seconds')) same_pid_start_within_10s
 from process s where s.num_process_start=0 group by 1""")
check('known_file_orphan_pid_coverage', """select r.hostname,count(*) row_count,count(distinct r.pidhash) orphan_hashes,
 count(*) filter(where exists(select 1 from process p where p.hostname=r.hostname and p.os_pid=r.pid and p.num_process_start>0)) rows_with_same_pid_start_elsewhere,
 count(*) filter(where exists(select 1 from process p where p.hostname=r.hostname and p.os_pid=r.pid and p.num_process_start>0 and p.process_started<=to_timestamp((r.firstseen-116444736000000000)/10000000.0) and (p.process_term is null or p.process_term>=to_timestamp((r.lastseen-116444736000000000)/10000000.0)))) rows_with_same_pid_covering_lifetime
 from stg_raw_process_file r where lower(r.processname)!='unknown' and not exists(select 1 from process p where p.pid_hash=r.pidhash and p.hostname=r.hostname) group by 1""")
check('pseudo_processes', """select hostname,count(*) identities,
 count(*) filter(where num_process_start=0) stop_only,
 count(*) filter(where process_name like '%socket:[%') socket_name
 from process where process_name like '%socket:[%' or process_name like '%pipe:[%' or process_name='kworker/dying' group by 1""")
# Bounded graph walk independent of recursive SQL; detect actual cycles.
ps=c.execute('select hostname,pid_hash,parent_pid_hash from process').fetchall()
parents={(h,p):par for h,p,par in ps}; cycles=set(); depths=[]
for h,p,par in ps:
    seen=[]; current=p
    while (h,current) in parents and current not in seen:
        seen.append(current); current=parents[(h,current)]
    if current in seen: cycles.add(tuple(sorted(seen[seen.index(current):])))
    depths.append(len(seen))
results['checks']['graph_cycles']={'rows':[dict(cycles=len(cycles),maximum_observed_depth=max(depths),examples=list(cycles)[:5])]}
after=DB.stat()
results['database_file_unchanged']=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns
OUT.write_text(json.dumps(results,default=str,indent=2)+'\n')
print('Results:',OUT,'Database unchanged:',results['database_file_unchanged'])
