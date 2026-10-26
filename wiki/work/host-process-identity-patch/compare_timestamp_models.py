"""Read-only multiset comparison: do not hide identity/counter changes as time fixes."""
import argparse
import json
from pathlib import Path
import duckdb


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def compare(old, new):
    with duckdb.connect(':memory:') as c:
        c.execute("attach '"+str(old).replace("'", "''")+"' as baseline (read_only)")
        c.execute("attach '"+str(new).replace("'", "''")+"' as candidate (read_only)")
        tables = c.execute("select table_name from information_schema.tables where table_catalog='baseline' and table_schema='main' order by table_name").fetchall()
        results = []
        for (table,) in tables:
            cols = c.execute("select column_name,data_type from information_schema.columns where table_catalog='baseline' and table_schema='main' and table_name=? order by ordinal_position", [table]).fetchall()
            newcols = c.execute("select column_name,data_type from information_schema.columns where table_catalog='candidate' and table_schema='main' and table_name=? order by ordinal_position", [table]).fetchall()
            if cols != newcols:
                results.append(dict(table=table, schema_equal=False))
                continue
            stable = [name for name, type_ in cols if not type_.startswith('TIMESTAMP')]
            projection = ','.join(map(quote, stable)) if stable else '1'
            before, after = 'baseline.main.'+quote(table), 'candidate.main.'+quote(table)
            removed = c.execute(f'select count(*) from (select {projection} from {before} except all select {projection} from {after})').fetchone()[0]
            added = c.execute(f'select count(*) from (select {projection} from {after} except all select {projection} from {before})').fetchone()[0]
            full_delta = c.execute(f'select count(*) from (select * from {before} except all select * from {after})').fetchone()[0]
            # Explicit second gate, not a rewrite of the strict comparison: these
            # These fields depend on unordered any_value in silver/process.sql.
            permitted = {'process_name', 'process_path', 'args', 'filename', 'file_id'} if table in ('process', 'process_summary') else set()
            if table == 'process_summary':
                permitted.add('duration_seconds')
            protected = [name for name in stable if name not in permitted]
            protected_projection = ','.join(map(quote, protected)) if protected else '1'
            protected_removed = c.execute(f'select count(*) from (select {protected_projection} from {before} except all select {protected_projection} from {after})').fetchone()[0]
            protected_added = c.execute(f'select count(*) from (select {protected_projection} from {after} except all select {protected_projection} from {before})').fetchone()[0]
            results.append(dict(table=table, schema_equal=True,
                old_rows=c.execute(f'select count(*) from {before}').fetchone()[0],
                new_rows=c.execute(f'select count(*) from {after}').fetchone()[0],
                excluded_timestamp_columns=[name for name, type_ in cols if type_.startswith('TIMESTAMP')],
                stable_rows_removed=removed, stable_rows_added=added, full_rows_removed=full_delta,
                explicitly_permitted_non_timestamp_columns=sorted(permitted),
                protected_rows_removed=protected_removed, protected_rows_added=protected_added))
        # Validate every derived process timestamp independently against integer
        # raw inputs, not just the collector. any_value candidates must occur in raw.
        raw = c.execute('select pidhash,activitytype,cast(eventtime as bigint),processname,processpath,processargs from candidate.main.stg_raw_process').fetchall()
        lifetimes = {}
        for identity, activity, ft, name, path, args in raw:
            lifetime = lifetimes.setdefault(identity, dict(all=[], birth=[], stop=[], names=set(), paths=set(), args=set()))
            lifetime['all'].append(ft)
            if activity.upper() in ('START','REFRESH'): lifetime['birth'].append(ft)
            if activity.upper() == 'STOP': lifetime['stop'].append(ft)
            if name: lifetime['names'].add(name)
            if path: lifetime['paths'].add(path)
            if args: lifetime['args'].add(args)
        precision_failures, metadata_failures = [], []
        for identity, birth, first, last, stop, name, path, args in c.execute('select pid_hash,epoch_us(process_started),epoch_us(first_seen),epoch_us(last_seen),epoch_us(process_term),process_name,process_path,args from candidate.main.process').fetchall():
            raw_ = lifetimes[identity]
            expected = [((fn(raw_[field])-116444736000000000)//10 if raw_[field] else None)
                        for field, fn in [('birth',min),('all',min),('all',max),('stop',max)]]
            if [birth, first, last, stop] != expected:
                precision_failures.append(dict(pid_hash=identity, actual=[birth,first,last,stop], expected=expected))
            if (name is not None and name not in raw_['names']) or (path is not None and path not in raw_['paths']) or (args is not None and args not in raw_['args']):
                metadata_failures.append(identity)
        duration_failures = c.execute('select count(*) from candidate.main.process_summary where duration_seconds is distinct from epoch(process_term-process_started)').fetchone()[0]
    return dict(tables=results, process_lifetimes=len(lifetimes), precision_failures=precision_failures,
                unordered_metadata_source_failures=metadata_failures, duration_failures=duration_failures)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--qualified', action='store_true', help='Keep strict deltas but gate protected fields plus raw timestamp/metadata checks')
    args = p.parse_args()
    old = {(r['host'],r['round']):r for r in json.loads(args.baseline.read_text())}
    results = []
    for r in json.loads(args.candidate.read_text()):
        key = r['host'],r['round']
        results.append(dict(host=key[0], round=key[1], **compare(
            Path(old[key]['log']).parent/'collector.duckdb', Path(r['log']).parent/'collector.duckdb')))
    args.output.write_text(json.dumps(results, indent=2)+'\n')
    mode = 'protected' if args.qualified else 'stable'
    assert all(t.get('schema_equal') and t[mode+'_rows_added']==t[mode+'_rows_removed']==0 and t['old_rows']==t['new_rows'] for r in results for t in r['tables'])
    if args.qualified:
        assert all(not r['precision_failures'] and not r['unordered_metadata_source_failures'] and not r['duration_failures'] for r in results)


if __name__ == '__main__':
    main()
