#!/usr/bin/env python3
"""Bounded stimuli only: never query parquet, configure or manage a collector."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument('--devtools', required=True, type=Path)
    parser.add_argument('--suite', required=True, choices=['cross-domain', 'process', 'file', 'clone'])
    args, remaining = parser.parse_known_args()
    if not sys.platform.startswith('linux'):
        parser.error('Canary stimuli target Linux only')
    sys.path.insert(0, str(args.devtools.resolve()))
    from smoke_manifest import record, smoke_run, epoch_utc, utc_now, process_selector

    @smoke_run('canary-' + args.suite)
    def stimulus():
        record(stimulusOnly=True, suiteKind='canary')
        if os.environ.get('WINTAP_CANARY_ROUND_ID'):
            record(canaryRoundId=os.environ['WINTAP_CANARY_ROUND_ID'])
        if args.suite == 'cross-domain':
            from telemetry_smoke_workload import main as named
            # Reuse the generator, not its outer dev-time manifest wrapper.
            named.__wrapped__()
            return 0
        options = argparse.ArgumentParser(description=__doc__)
        options.add_argument('--output', required=True, type=Path)
        if args.suite == 'clone':
            options.add_argument('--clone-helper', type=Path)
        opts = options.parse_args()
        opts.output.mkdir(parents=True, exist_ok=False)
        if args.suite == 'process':
            from process_capture_smoke_test import spawn_process_suite
            suite = spawn_process_suite(short_lived_children=6)
            skips = []
            if not hasattr(os, 'execveat') or not hasattr(os, 'AT_EMPTY_PATH'):
                skips.append('Python execveat/AT_EMPTY_PATH unavailable; suite child creation is not execveat coverage')
            pids = set(suite.extra_pids) | set(suite.short_lived_child_pids)
            for link in suite.links:
                pids.update((link.parent_pid, link.child_pid))
            if suite.short_lived_parent_pid:
                pids.add(suite.short_lived_parent_pid)
            record(selectors=[dict(domain='process', case='lifecycle-and-short-lived',
                pids=sorted(pids), startedAtUtc=epoch_utc(suite.start_epoch), completedAtUtc=utc_now(),
                expectedActivities=['Start', 'Stop'], requireStopPerPid=True, skips=skips,
                links=[dict(case=l.name, parentPid=l.parent_pid, childPid=l.child_pid) for l in suite.links])],
                results={'validationDeferred': True, 'limitations': ['posix_spawn is a libc-selected best-effort path, not syscall proof']})
        elif args.suite == 'file':
            from file_capture_smoke_test import generate_file_activity
            item = generate_file_activity(opts.output, unique_file_count=8)
            record(selectors=[dict(domain='file', case='eight-distinct-files', pids=[item.pid],
                pathPrefix=item.path_prefix, expectedPaths=8, startedAtUtc=epoch_utc(item.start_epoch),
                completedAtUtc=utc_now(), expectedActivities=['Open', 'Read', 'Write', 'Close', 'Delete'])],
                results={'validationDeferred': True})
        else:
            if not opts.clone_helper:
                record(results={'validationDeferred': True, 'cases': [dict(case='native-clone',
                    status='skipped', reason='No prebuilt clone helper supplied')]})
                return 0
            start = utc_now()
            result = subprocess.run([str(opts.clone_helper.resolve()), '--rounds=1'],
                capture_output=True, text=True, timeout=30, env=dict(os.environ, WINTAP_SMOKE_NAMES='1'))
            (opts.output / 'native.manifest').write_text(result.stdout)
            (opts.output / 'native.stderr').write_text(result.stderr)
            selector = process_selector(result.stdout, start=start)
            selector['links'] = [dict(case=r['case'], parentPid=r['parentPid'], childPid=r['pid'])
                for r in selector['records'] if r['pid'] == r['tid']]
            selector['expectedActivities'] = ['Start', 'Stop']
            selector['requireStopPerPid'] = True
            record(selectors=[selector], results={'validationDeferred': True})
            return result.returncode
        return 0

    sys.argv = [sys.argv[0], *remaining]
    return stimulus()


if __name__ == '__main__':
    raise SystemExit(main())
