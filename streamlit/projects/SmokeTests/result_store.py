"""Summary-only analysis cache beside data, never under raw_sensor or in Git."""
import json
import os
from pathlib import Path
import tempfile

from analysis import SCHEMA_VERSION, digest
from s3_source import dataset_parts

MAX_RESULT_BYTES = 4 * 1024 * 1024


def location(ctx, fingerprint):
    if len(fingerprint) != 64 or any(c not in '0123456789abcdef' for c in fingerprint):
        raise ValueError('Invalid analysis fingerprint')
    group = ctx.get('analysis_group', '')
    if group and (len(group) != 64 or any(c not in '0123456789abcdef' for c in group)):
        raise ValueError('Invalid analysis group identity')
    suffix = 'analysis/smoke-tests/v1/' + (group + '/' if group else '') + fingerprint + '.json'
    if ctx['remote']:
        bucket, raw = dataset_parts(ctx['config']['datasets'][0])
        base = raw.removesuffix('raw_sensor/')
        return bucket, base + suffix
    root = Path(ctx['data_root']).expanduser()
    if not ctx['data_root']:
        raise ValueError('Choose a local dataset root before saving analysis')
    if root.name == 'raw_sensor':
        root = root.parent
    root = root.resolve()
    for ancestor in (root, *root.parents):
        if (ancestor / '.git').exists():
            raise ValueError('Analysis results must stay outside Git working trees')
    target = (root / suffix).resolve()
    if not target.is_relative_to(root):
        raise ValueError('Analysis path escapes the dataset root')
    for ancestor in target.parents:
        if (ancestor / '.git').exists():
            raise ValueError('Analysis path enters a Git working tree')
    return None, target


def validate_report(report, fingerprint):
    if not isinstance(report, dict) or report.get('schema_version') != SCHEMA_VERSION or report.get('fingerprint') != fingerprint:
        raise ValueError('Saved analysis identity/schema mismatch')
    if not isinstance(report.get('results'), list) or not isinstance(report.get('errors'), list) or not isinstance(report.get('missing_families'), list):
        raise ValueError('Invalid saved analysis structure')
    return report


def read_bytes(ctx, bucket, key):
    try:
        if bucket is not None:
            response = ctx['client'].get_object(Bucket=bucket, Key=key)
            try:
                data = response['Body'].read(MAX_RESULT_BYTES + 1)
            finally:
                response['Body'].close()
        else:
            with key.open('rb') as stream:
                data = stream.read(MAX_RESULT_BYTES + 1)
        if len(data) > MAX_RESULT_BYTES:
            raise ValueError('Saved analysis exceeds size budget')
        return data
    except FileNotFoundError:
        return None
    except Exception as error:
        response = getattr(error, 'response', {})
        if response.get('Error', {}).get('Code') in ('NoSuchKey', '404'):
            return None
        raise RuntimeError('Cannot read saved analysis; details suppressed') from None


def load_result(ctx, fingerprint):
    bucket, key = location(ctx, fingerprint)
    data = read_bytes(ctx, bucket, key)
    if data is None:
        return None
    try:
        report = validate_report(json.loads(data), fingerprint)
        checksum = report.get('summary_sha256')
        if checksum != digest({k: v for k, v in report.items() if k != 'summary_sha256'}):
            raise ValueError('Saved analysis checksum mismatch')
        return report
    except Exception:
        raise RuntimeError('Saved analysis corrupt or incompatible; no cached verdict accepted') from None


def latest_location(ctx):
    bucket, key = location(ctx, '0' * 64)
    return bucket, key.rsplit('/', 1)[0] + '/latest.json' if bucket is not None else key.parent / 'latest.json'


def load_latest(ctx):
    bucket, key = latest_location(ctx)
    data = read_bytes(ctx, bucket, key)
    if data is None:
        return None
    try:
        value = json.loads(data)
        if value.get('schema_version') != SCHEMA_VERSION or value.get('group') != ctx.get('analysis_group', ''):
            raise ValueError('Analysis pointer mismatch')
        return load_result(ctx, value['fingerprint'])
    except Exception:
        raise RuntimeError('Previous analysis snapshot unavailable; details suppressed') from None


def write_bytes(ctx, bucket, key, data):
    if len(data) > MAX_RESULT_BYTES:
        raise ValueError('Analysis summary exceeds size budget')
    try:
        if bucket is not None:
            # The user authorizes summary writes only. Never write/delete raw data,
            # collector manifests or credential/configuration files.
            ctx['client'].put_object(Bucket=bucket, Key=key, Body=data, ContentType='application/json')
        else:
            key.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(prefix='.analysis-', suffix='.active', dir=key.parent)
            try:
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, key)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
    except Exception:
        raise RuntimeError('Analysis result save failed; summary not acknowledged as persisted (details suppressed)') from None


def save_result(ctx, report):
    fingerprint = report['fingerprint']
    validate_report(report, fingerprint)
    value = {k: v for k, v in report.items() if k != 'summary_sha256'}
    value['summary_sha256'] = digest(value)
    data = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    bucket, key = location(ctx, fingerprint)
    write_bytes(ctx, bucket, key, data)
    if read_bytes(ctx, bucket, key) != data:
        raise RuntimeError('Analysis write verification failed; persistence not acknowledged')
    bucket, key = latest_location(ctx)
    pointer = json.dumps(dict(schema_version=SCHEMA_VERSION, group=ctx.get('analysis_group', ''), fingerprint=fingerprint)).encode()
    write_bytes(ctx, bucket, key, pointer)
    if read_bytes(ctx, bucket, key) != pointer:
        raise RuntimeError('Analysis pointer verification failed; persistence not acknowledged')
