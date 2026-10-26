#!/usr/bin/env python3
"""Emit existing same-host TCP selectors without racing upload with local queries."""
import argparse
import os
import sys
from pathlib import Path


def main():
    # The shared wrapper consumes --manifest/--smoke-data-root itself.
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("--devtools", required=True, type=Path)
    args, remaining = parser.parse_known_args()
    sys.path.insert(0, str(args.devtools.resolve()))
    from smoke_manifest import record, smoke_run
    from network_endpoint_smoke_test import generate_cases, host_address

    @smoke_run("canary-network-endpoints")
    def stimulus():
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--host-ip")
        options = parser.parse_args()
        record(stimulusOnly=True, suiteKind="canary")
        if os.environ.get('WINTAP_CANARY_ROUND_ID'):
            record(canaryRoundId=os.environ['WINTAP_CANARY_ROUND_ID'])
        selectors = generate_cases(host_address(options.host_ip))
        record(selectors=selectors, results={"validationDeferred": True})
        print("Generated separate-process and same-process TCP ends; capture not validated")
        return 0

    sys.argv = [sys.argv[0], *remaining]
    return stimulus()


if __name__ == "__main__":
    raise SystemExit(main())
