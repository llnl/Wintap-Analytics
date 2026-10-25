"""Conservative event-time classification; never modifies strict quality gates.

Bounds bracket possible capture transitions, not guaranteed delivery. No inferred
bounds from collector birth or first/last exported rows. Integer UTC FILETIME only.
"""
from collections import Counter


TICKS_PER_SECOND = 10_000_000
UNIX_EPOCH_FILETIME = 116_444_736_000_000_000
CLASSES = ('start_edge', 'interior', 'end_edge', 'outside', 'uncertain', 'unclassified')


def unix_ns_to_filetime(value):
    return UNIX_EPOCH_FILETIME + value // 100


def validate_bounds(bounds):
    if not bounds or bounds.get('clock_verified') is not True:
        return False
    names = ('start_min', 'start_max', 'end_min', 'end_max')
    if any(type(bounds.get(name)) is not int for name in names):
        return False
    a, b, c, d = (bounds[name] for name in names)
    return 0 < a <= b <= c <= d and bool(bounds.get('source'))


def classify_interval(first, last, bounds, width_seconds=10):
    """Classify only when EVERY possible boundary and event time agrees.

    Start is inclusive, cutoff exclusive; edge bands extend inward. Aggregated
    spans crossing bands, overlapping edge bands, and transition ambiguity remain
    uncertain. Absence of timing or trustworthy bounds stays unclassified.
    """
    if type(width_seconds) is not int or width_seconds <= 0:
        raise ValueError('Edge width must be a positive integer number of seconds')
    if not validate_bounds(bounds) or type(first) is not int or type(last) is not int:
        return 'unclassified'
    if first <= 0 or first > last:
        return 'unclassified'
    a, b, c, d = (bounds[key] for key in ('start_min', 'start_max', 'end_min', 'end_max'))
    w = width_seconds * TICKS_PER_SECOND
    if last < a or first >= d:
        return 'outside'
    if first >= b + w and last < c - w:
        return 'interior'
    if first >= b and last < a + w and last < c - w:
        return 'start_edge'
    if first >= d - w and last < c and first >= b + w:
        return 'end_edge'
    return 'uncertain'


def classify_event(event_time, bounds, width_seconds=10):
    return classify_interval(event_time, event_time, bounds, width_seconds)


def report(records, bounds, widths=(10, 1, 5, 20)):
    """Records carry first/last event time and arbitrary additive counters.

    Missing payloads may use a separately labelled stimulus interval, never an
    invented telemetry event timestamp. Errors count equally in every band.
    """
    output = {}
    for width in widths:
        buckets = {name: Counter() for name in CLASSES}
        for record in records:
            band = classify_interval(record.get('first'), record.get('last'), bounds, width)
            buckets[band]['records'] += 1
            for key, count in record.get('counts', {}).items():
                if type(count) is not int or count < 0:
                    raise ValueError('Counters must be nonnegative integers')
                buckets[band][key] += count
        output[str(width)] = {name: dict(counts) for name, counts in buckets.items()}
    return dict(primary_width_seconds=10, sensitivity_width_seconds=[1, 5, 20],
                bounds=bounds, bounds_valid=validate_bounds(bounds), bands=output,
                strict_gates_unchanged=True,
                edge_classification_is_not_loss_or_identity_acceptance=True)
