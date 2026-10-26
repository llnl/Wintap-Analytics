"""Read-only joins between bounded diagnostic receipts and archived raw parquet.

File aggregate counts are compared by owner/path/activity, not diagnostic IDs.
Finalized-row multisets retain raw counters/timestamps; no synthetic raw IDs.
Complete scoped observer output is not complete native-kernel delivery evidence.
"""
from collections import Counter
import json
from pathlib import Path


def load_trace(path):
    records, errors = [], []
    for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as error:
            errors.append(dict(line=line_number, error=str(error)))
    summaries = [r for r in records if r.get('Kind') == 'summary']
    rows = [r for r in records if r.get('Kind') != 'summary']
    summary = summaries[0] if len(summaries) == 1 else {}
    counts = summary.get('Counts', {})
    clean = (not errors and len(summaries) == 1 and records[-1] == summary
        and summary.get('RuleVersion') == 'attribution-trace-v2'
        and counts.get('Closed') is True and counts.get('Accepted') == counts.get('Written') == len(rows)
        and all(counts.get(key) == 0 for key in ('Refused', 'ByteRefused', 'Errors', 'DiscardedOnError', 'Truncated'))
        and len({r.get('Sequence') for r in rows}) == len(rows)
        and [r.get('Sequence') for r in rows] == list(range(1, len(rows) + 1)))
    return rows, dict(summary=summary, parse_errors=errors, scoped_observer_complete=clean,
        native_producer_complete=False, durable_fate_proven_by_summary=False)


def activity(value):
    return (value or '').lower().replace('/', '')


def file_totals(rows, stage, include_identity=True):
    result = Counter()
    for row in rows:
        if row.get('Stage') != stage or row.get('Path') is None:
            continue
        key = (row['Pid'], row['Path'], activity(row['Activity']))
        if include_identity:
            key += (row.get('PidHash'),)
        count = row.get('EventCount')
        if not isinstance(count, int) or count < 0:
            raise ValueError(f'Invalid event count at {stage}')
        result[key] += count
    return result


def file_row_key(row):
    return (row['Pid'], row.get('PidHash'), row['Path'], activity(row['Activity']),
        row.get('EventCount'), row.get('BytesRequested'),
        row.get('FirstSeenEventTime'), row.get('LastSeenEventTime'))


def network_row_key(row):
    return (row['Pid'], row.get('PidHash'), activity(row['Activity']), row.get('ConnId'),
        row.get('SourceAddress'), row.get('SourcePort'), row.get('DestinationAddress'), row.get('DestinationPort'),
        row.get('PacketSize'), row.get('EventCount'), row.get('FirstSeenEventTime'), row.get('LastSeenEventTime'))


def tcp_totals(rows, stage, include_identity=True):
    result = Counter()
    for row in rows:
        if row.get('Stage') != stage or row.get('Path') is not None or not activity(row.get('Activity')).startswith('tcp'):
            continue
        key = (row['Pid'], activity(row['Activity']), row.get('SourceAddress'), row.get('SourcePort'),
               row.get('DestinationAddress'), row.get('DestinationPort'))
        if include_identity:
            key += (row.get('PidHash'),)
        # WintapMessage TCP payload represents one event; SQL projection carries count(*).
        count = 1 if 'EventId' in row else row.get('EventCount')
        if not isinstance(count, int) or count < 0:
            raise ValueError(f'Invalid TCP count at {stage}')
        result[key] += count
    return result


def compare_multisets(expected, actual):
    missing, extra = expected - actual, actual - expected
    return dict(equal=expected == actual, expected_rows=sum(expected.values()), actual_rows=sum(actual.values()),
        missing_rows=sum(missing.values()), extra_rows=sum(extra.values()),
        missing_sample=[dict(key=list(k), multiplicity=v) for k, v in list(missing.items())[:10]],
        extra_sample=[dict(key=list(k), multiplicity=v) for k, v in list(extra.items())[:10]])


def analyze_trace(path, connection, raw_root):
    rows, result = load_trace(path)
    prefix = result['summary'].get('FilePrefix')
    if not isinstance(prefix, str) or not prefix.endswith('/'):
        result['scoped_observer_complete'] = False
        result['scope_error'] = 'Expected an explicit normalized workload prefix'
        return result
    # Read every actual file row in the declared scope, not just receipts that matched.
    files = connection.execute('''select PID,PidHash,File_Path,ActivityType,EventCount,BytesRequested,FirstSeen,LastSeen
        from read_parquet(?,union_by_name=true) where starts_with(File_Path,?)''',
        [str(raw_root / 'raw_process_file/**/*.parquet'), prefix]).fetchall()
    raw_file_keys = Counter(tuple((pid, identity, path_, activity(act), count, bytes_, first, last))
        for pid, identity, path_, act, count, bytes_, first, last in files)
    finalized = [r for r in rows if r.get('Stage') == 'parquet-finalized']
    result['finalized_file_rows_vs_archived_raw'] = compare_multisets(
        Counter(file_row_key(r) for r in finalized if r.get('Path') is not None), raw_file_keys)
    network = connection.execute('''select PID,PidHash,IpEvent,ConnId,SourceIpAddressString,SourcePort,
        DestinationIpAddressString,DestinationPort,PacketSize,EventCount,FirstSeenMs,LastSeenMs
        from read_parquet(?,union_by_name=true) where lower(Protocol)='tcp' ''',
        [str(raw_root / 'raw_process_conn_incr/**/*.parquet')]).fetchall()
    result['finalized_tcp_rows_vs_archived_raw'] = compare_multisets(
        Counter(network_row_key(r) for r in finalized if r.get('Path') is None and activity(r.get('Activity')).startswith('tcp')),
        Counter((pid, identity, activity(act), conn, src, sport, dst, dport, size, count, first, last)
                for pid, identity, act, conn, src, sport, dst, dport, size, count, first, last in network))
    stages = ['file-producer-prepared', 'file-sender-admitted', 'esper-return',
              'serializer-accepted', 'serializer-drained', 'parquet-batch-enqueue', 'parquet-finalized']
    result['file_stage_totals'] = {stage: dict(events=sum(file_totals(rows, stage).values()),
        receipts=sum(r.get('Stage') == stage and r.get('Path') is not None for r in rows)) for stage in stages}
    result['file_stage_count_joins'] = {}
    for left, right in zip(stages, stages[1:]):
        # Producer/sender snapshots may precede successful delayed attribution.
        # Protect identity from Esper onward; independently qualify all exported hashes.
        include_identity = left not in ('file-producer-prepared', 'file-sender-admitted')
        result['file_stage_count_joins'][left + ' -> ' + right] = compare_multisets(
            file_totals(rows, left, include_identity), file_totals(rows, right, include_identity))
    result['diagnostic_stage_counts'] = dict(Counter(r.get('Stage') for r in rows))
    tcp_stages = ['network-producer-prepared', 'esper-return', 'serializer-accepted', 'parquet-finalized']
    result['tcp_stage_count_joins'] = {left + ' -> ' + right: compare_multisets(
        tcp_totals(rows, left, left != 'network-producer-prepared'),
        tcp_totals(rows, right, left != 'network-producer-prepared'))
        for left, right in zip(tcp_stages, tcp_stages[1:])}
    delivery_stages = ['serializer-accepted', 'serializer-drained', 'parquet-batch-enqueue', 'parquet-finalized']
    result['tcp_delivery_stage_count_joins'] = {left + ' -> ' + right: compare_multisets(
        tcp_totals(rows, left), tcp_totals(rows, right))
        for left, right in zip(delivery_stages, delivery_stages[1:])}
    def row_ids(stage):
        return Counter((r['RowId'],) for r in rows if r.get('Stage') == stage and
                       'RowId' in r and activity(r.get('Activity')).startswith('tcp'))
    result['tcp_delivery_row_id_joins'] = {left + ' -> ' + right: compare_multisets(
        row_ids(left), row_ids(right)) for left, right in zip(delivery_stages, delivery_stages[1:])}
    if any(r.get('Stage') == 'service-stop-begin' for r in rows):
        from shutdown_trace_analysis import analyze_shutdown
        result['shutdown_evidence'] = analyze_shutdown(rows, result['scoped_observer_complete'])
    result['gates'] = dict(scoped_observer_complete=result['scoped_observer_complete'],
        finalized_file_multiset_matches=result['finalized_file_rows_vs_archived_raw']['equal'] and bool(files),
        finalized_tcp_multiset_matches=result['finalized_tcp_rows_vs_archived_raw']['equal'] and bool(network),
        file_stage_event_count_joins=all(x['equal'] and x['expected_rows'] > 0 for x in result['file_stage_count_joins'].values()),
        tcp_stage_event_count_joins=all(x['equal'] and x['expected_rows'] > 0 for x in result['tcp_stage_count_joins'].values()))
    result['gates'].update(
        tcp_delivery_stage_event_count_joins=all(x['equal'] and x['expected_rows'] > 0
            for x in result['tcp_delivery_stage_count_joins'].values()),
        tcp_delivery_exact_row_id_joins=all(x['equal'] and x['expected_rows'] > 0
            for x in result['tcp_delivery_row_id_joins'].values()))
    if any(r.get('Stage') == 'query-registration-begin' for r in rows):
        from tcp_readiness_analysis import analyze_readiness
        readiness = analyze_readiness(rows, result['scoped_observer_complete'])
        result['tcp_readiness'] = readiness
        result['gates'].update(
            tcp_registration_receipts=readiness['registration_receipts_qualified'],
            tcp_projection_terminal_receipts=readiness['projection_terminal_receipts_complete'],
            tcp_exact_projection_row_links=readiness['exact_projection_row_ids_vs_acceptance']['equal'],
            tcp_projection_error_free=not readiness['projection_errors'])
        if readiness['collector_start_after_etl_callbacks'] is not None:
            result['gates']['collector_start_after_etl_callbacks'] = readiness['collector_start_after_etl_callbacks']
    if 'shutdown_evidence' in result:
        shutdown = result['shutdown_evidence']
        result['gates']['tcp_shutdown_no_late_acceptance'] = shutdown['shutdown_complete_and_no_late_acceptance']
        if shutdown['barrier_order_and_horizon_qualified'] is not None:
            result['gates'].update(
                shutdown_barrier_order_and_horizon=shutdown['barrier_order_and_horizon_qualified'],
                serializers_quiesced_before_drain=shutdown['all_serializers_quiesced_before_drain'],
                shutdown_callback_cutoff_no_refusals=not shutdown['callback_cutoff_refusals'],
                shutdown_barrier_no_failures=not shutdown['barrier_failures'],
                shutdown_all_serializers_complete=shutdown['all_serializer_shutdowns_complete'],
                shutdown_service_reports_etl_complete=shutdown['service_reports_etl_complete'])
    result['interpretation'] = ('Scoped receipt-to-archived-output joins only; no kernel-ring loss, '
        'filesystem fsync, remote upload, or historical lost-event provenance is established.')
    return result
