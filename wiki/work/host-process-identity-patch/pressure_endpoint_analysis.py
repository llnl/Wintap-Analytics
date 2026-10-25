"""Pressure oracle uses exact capture receipt times, not stimulus+arbitrary grace.

Production TCP EPL FirstSeen/LastSeen summarize ReceiveTime (callback receipt), not
the kernel EventTime. Callback backlog may extend beyond completed socket I/O.
Original narrow-stimulus failures are retained separately for audit.
"""
from pathlib import Path
import ipaddress

import duckdb


def capture_filetime(unix_ns):
    if not isinstance(unix_ns, int):
        raise ValueError('Integer capture clock receipt required')
    return 116444736000000000 + unix_ns // 100


def read_pressure_rows(raw, selectors, round_):
    files = sorted(str(p) for p in (raw / 'raw_process_conn_incr').rglob('*.parquet'))
    if not files or not selectors:
        return [], 'Missing pressure network raw/independent selectors'
    pids = sorted({pid for s in selectors for pid in s['pids']})
    ports = sorted({port for s in selectors for port in s['ports']})
    first = capture_filetime(round_['clock_start']['unix_ns'])
    last = capture_filetime(round_['clock_end']['unix_ns'])
    if last <= first:
        raise ValueError('Capture receipt interval is invalid')
    with duckdb.connect(':memory:') as c:
        c.read_parquet(files, union_by_name=True).create_view('network')
        cursor = c.execute(f'''select PID as pid,PidHash as pid_hash,lower(replace(IpEvent,'/','')) as activity,
            cast(LocalIpAddr as ubigint) as local_ip,LocalPort as local_port,
            cast(RemoteIpAddr as ubigint) as remote_ip,RemotePort as remote_port,
            SourcePort as source_port,DestinationPort as destination_port,FirstSeenMs as receipt_first_seen
            from network where PID in ({','.join(map(str,pids))}) and FirstSeenMs between ? and ?
            and (SourcePort in ({','.join(map(str,ports))}) or DestinationPort in ({','.join(map(str,ports))}))''', [first,last])
        columns = [d[0] for d in cursor.description]
        rows = [dict(zip(columns,r)) for r in cursor.fetchall()]
        for row in rows:
            row['local_ip'] = str(ipaddress.IPv4Address(row['local_ip']))
            row['remote_ip'] = str(ipaddress.IPv4Address(row['remote_ip']))
        return rows, None
