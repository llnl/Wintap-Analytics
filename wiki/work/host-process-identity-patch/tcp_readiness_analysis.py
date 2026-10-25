"""Conservative registration/handoff brackets and exact projection-to-row joins.

No aggregate is labeled as a particular missing input merely because keys match.
Requires a qualified complete trace before absence evidence is interpretable.
"""
from collections import Counter, defaultdict

from delivery_trace_analysis import activity, compare_multisets, tcp_totals


def analyze_readiness(rows, complete):
    query_rows = [r for r in rows if r.get('Serializer') == 'tcpconnectionserializer'
                  and (r.get('QueryPath') or '').endswith('tcp.epl')]
    by_query = defaultdict(list)
    for row in query_rows:
        by_query[row['QueryName']].append(row)
    required = ['query-registration-begin', 'query-deployed',
                'query-listener-attached', 'query-registration-complete']
    qualified = len(by_query) == 1
    boundaries = {}
    if qualified:
        receipts = next(iter(by_query.values()))
        for stage in required:
            matches = [r for r in receipts if r['Stage'] == stage]
            if len(matches) != 1 or not isinstance(matches[0].get('MonotonicTicks'), int):
                qualified = False
            else:
                boundaries[stage] = matches[0]['MonotonicTicks']
        if qualified:
            qualified = list(boundaries.values()) == sorted(boundaries.values())
        if any(r['Stage'] == 'query-registration-error' for r in receipts):
            qualified = False
    call_rows = [r for r in rows if r.get('Stage') == 'tcp-esper-call']
    calls = {r['EventId']: r for r in call_rows}
    returns = [r for r in rows if r.get('Stage') == 'esper-return' and r.get('Stream') == 'TcpConnection']
    brackets_complete = (len(calls) == len(call_rows) == len(returns) and
                         len({r['EventId'] for r in returns}) == len(returns) and
                         set(calls) == {r['EventId'] for r in returns})
    handoffs = []
    for row in returns:
        call = calls.get(row['EventId'])
        band = 'unclassified'
        if complete and qualified and brackets_complete and call:
            begin, end = call['MonotonicTicks'], row['MonotonicTicks']
            if begin <= end:
                if end < boundaries['query-registration-begin']:
                    band = 'before-registration'
                elif begin > boundaries['query-registration-complete']:
                    band = 'after-listener-ready'
                else:
                    band = 'registration-overlap'
        handoffs.append(dict(event_id=row['EventId'], band=band, receipt=row))
    projections = defaultdict(list)
    for row in rows:
        if 'ProjectionId' in row:
            projections[row['ProjectionId']].append(row)
    accepts = Counter((r['RowId'],) for r in rows if r.get('Stage') == 'serializer-accepted' and
                      r.get('Stream') == 'PROCESS_CONN_INCR' and 'RowId' in r and
                      activity(r.get('Activity')).startswith('tcp'))
    ready = Counter((r['RowId'],) for r in rows if r.get('Stage') == 'tcp-projection-row-ready' and
                    r.get('RowId') is not None)
    projection_errors = [r for r in rows if r.get('Stage') == 'tcp-projection-error']
    projection_terminal = all(
        sum(r['Stage'] == 'tcp-projection-enter' for r in receipts) == 1 and
        sum(r['Stage'] in ('tcp-projection-return', 'tcp-projection-error') for r in receipts) == 1
        for receipts in projections.values())
    stage_joins = {left + ' -> ' + right: compare_multisets(tcp_totals(rows, left), tcp_totals(rows, right))
        for left, right in [('esper-return', 'tcp-projection-enter'),
                            ('tcp-projection-enter', 'tcp-projection-row-ready'),
                            ('tcp-projection-row-ready', 'serializer-accepted')]}
    before = [r['receipt'] for r in handoffs if r['band'] == 'before-registration']
    deficit = tcp_totals(rows, 'esper-return') - tcp_totals(rows, 'tcp-projection-enter')
    before_vs_deficit = compare_multisets(tcp_totals(before, 'esper-return'), deficit)
    startup_stages = ['tcp-callback-initialized', 'etl-callbacks-ready',
                      'etl-readiness-passed', 'collector-start-call']
    startup_receipts = {stage: [r for r in rows if r.get('Stage') == stage] for stage in startup_stages}
    startup_order = None
    if startup_receipts['etl-readiness-passed']:
        startup_order = all(len(startup_receipts[stage]) == 1 for stage in startup_stages)
        if startup_order:
            ticks = [startup_receipts[stage][0]['MonotonicTicks'] for stage in startup_stages]
            startup_order = ticks == sorted(ticks) and all(
                call['MonotonicTicks'] >= ticks[-1] for call in calls.values())
    return dict(complete_trace_required=complete, registration_receipts_qualified=qualified,
        registration_boundaries=boundaries, handoff_bands=dict(Counter(r['band'] for r in handoffs)),
        handoff_brackets_complete=brackets_complete,
        callback_initialization_receipts=[r for r in rows if r.get('Stage') == 'tcp-callback-initialized'],
        collector_start_after_etl_callbacks=startup_order,
        startup_receipts=startup_receipts,
        handoffs=handoffs, projection_errors=projection_errors,
        projection_terminal_receipts_complete=projection_terminal and bool(projections),
        exact_projection_row_ids_vs_acceptance=compare_multisets(ready, accepts),
        before_registration_event_counts_vs_projection_deficit=before_vs_deficit,
        stage_count_joins=stage_joins,
        absence_interpretable=complete and qualified and brackets_complete and
            all(r['band'] != 'unclassified' for r in handoffs),
        historical_failure_resolved=False)
