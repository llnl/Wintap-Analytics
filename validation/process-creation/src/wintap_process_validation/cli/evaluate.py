from __future__ import annotations

import argparse
from pathlib import Path
import json

from wintap_process_validation.evaluator import evaluate
from wintap_process_validation.schema import Manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate normalized process validation events")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--normalized-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    manifest = Manifest.read(args.manifest)
    report = evaluate(manifest, args.normalized_dir)
    if args.report:
        report.write(args.report)
        print(f"wrote {args.report}")
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
