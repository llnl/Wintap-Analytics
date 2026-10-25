"""Read-only exact shutdown brackets, late acceptance and stranded row joins.

Complete observer evidence is required for absence claims. This is not proof of
kernel hook cutoffs, fsync/upload, or all native deliveries.
"""
from collections import Counter


def analyze_shutdown(rows, complete):
    boundaries = [r for r in rows if r.get('Component') == 'tcpconnectionserializer' and
                  r.get('Stage') in ('serializer-shutdown-begin', 'serializer-shutdown-end')]
    begins = [r for r in boundaries if r['Stage'] == 'serializer-shutdown-begin']
    ends = [r for r in boundaries if r['Stage'] == 'serializer-shutdown-end']
    qualified = (complete and len(begins) == len(ends) == 1 and
                 begins[0]['MonotonicTicks'] <= ends[0]['MonotonicTicks'])
    def tcp(r):
        return (r.get('Activity') or '').lower().replace('/', '').startswith('tcp')
    accepted = [r for r in rows if r.get('Stage') == 'serializer-accepted' and tcp(r)]
    drained = Counter(r['RowId'] for r in rows if r.get('Stage') == 'serializer-drained' and tcp(r))
    stranded = [r for r in accepted if drained[r['RowId']] == 0] if complete else []
    late = [r for r in accepted if qualified and r['MonotonicTicks'] > ends[0]['MonotonicTicks']]
    service = [r for r in rows if r.get('Component') == 'service']
    barrier_stages = ['esper-shutdown-clock-freeze-begin', 'esper-shutdown-clock-frozen',
                      'esper-shutdown-window-advance-begin', 'esper-shutdown-window-advance-end',
                      'esper-shutdown-callbacks-quiesced']
    barrier = {stage: [r for r in rows if r.get('Stage') == stage] for stage in barrier_stages}
    barrier_qualified = None
    if any(barrier.values()):
        barrier_qualified = complete and all(len(matches) == 1 for matches in barrier.values())
        if barrier_qualified:
            ticks = [barrier[stage][0]['MonotonicTicks'] for stage in barrier_stages]
            barrier_qualified = ticks == sorted(ticks) and qualified and ticks[-1] <= begins[0]['MonotonicTicks']
            # ETL clock receipts label runtime milliseconds in QueueDepth; serializer
            # receipts use that field for queued rows. Never mix the components.
            frozen = barrier['esper-shutdown-clock-frozen'][0]['QueueDepth']
            target = barrier['esper-shutdown-window-advance-begin'][0]['QueueDepth']
            final = barrier['esper-shutdown-window-advance-end'][0]['QueueDepth']
            barrier_qualified = barrier_qualified and target == frozen + 10000 and final == target
    callback_refusals = [r for r in rows if r.get('Stage') in
                         ('serializer-callback-after-cutoff', 'tcp-projection-after-cutoff')]
    failed = [r for r in rows if r.get('Stage') == 'esper-shutdown-barrier-failed']
    joins = [r for r in rows if r.get('Stage') == 'serializer-callbacks-joined']
    joins_by_component = Counter(r['Component'] for r in joins)
    all_begins = Counter(r['Component'] for r in rows if r.get('Stage') == 'serializer-shutdown-begin')
    all_ends = [r for r in rows if r.get('Stage') == 'serializer-shutdown-end']
    end_components = Counter(r['Component'] for r in all_ends)
    all_complete = (complete and bool(all_ends) and all_begins == end_components and
                    all(n == 1 for n in end_components.values()) and
                    all(r.get('Complete') is True and r.get('QueueDepth') == 0 and
                        r.get('ActiveCallbacks') == 0 for r in all_ends))
    etl_end = [r for r in service if r.get('Stage') == 'etl-shutdown-end']
    quiesce_before_drain = None
    if barrier_qualified is not None:
        shutdowns = [r for r in rows if r.get('Stage') == 'serializer-shutdown-begin']
        joined = {r['Component']: r for r in joins}
        quiesce_before_drain = (complete and bool(shutdowns) and
            all(joins_by_component[r['Component']] == 1 and
                joined[r['Component']]['ActiveCallbacks'] == 0 and
                joined[r['Component']]['MonotonicTicks'] <= r['MonotonicTicks'] for r in shutdowns))
    return dict(complete_trace_required=complete, tcp_shutdown_bracket_qualified=qualified,
        shutdown_boundaries=boundaries, service_boundaries=service,
        late_accepted_rows=late, late_accepted_events=sum(r.get('EventCount') or 0 for r in late),
        accepted_without_drain_rows=stranded,
        accepted_without_drain_events=sum(r.get('EventCount') or 0 for r in stranded),
        complete_shutdown_then_late_acceptance=qualified and ends[0].get('Complete') is True and bool(late),
        exact_stranded_rows_are_late=(qualified and bool(stranded) and
            Counter(r['RowId'] for r in stranded) == Counter(r['RowId'] for r in late)),
        late_acceptance_markers=[r for r in rows if r.get('Stage') == 'serializer-accepted-after-shutdown'],
        barrier_order_and_horizon_qualified=barrier_qualified,
        all_serializers_quiesced_before_drain=quiesce_before_drain,
        callback_cutoff_refusals=callback_refusals, barrier_failures=failed,
        all_serializer_shutdowns_complete=all_complete,
        service_reports_etl_complete=complete and len(etl_end) == 1 and etl_end[0].get('Complete') is True,
        shutdown_complete_and_no_late_acceptance=(qualified and ends[0].get('Complete') is True
            and ends[0].get('QueueDepth') == 0 and ends[0].get('ActiveCallbacks') == 0 and not late),
        clock_cutover_receipts=[r for r in rows if r.get('Stage', '').startswith('esper-shutdown-')],
        native_cutoffs_proven=False, historical_failures_resolved=False)
