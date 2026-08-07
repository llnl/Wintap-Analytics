from __future__ import annotations

import argparse
from pathlib import Path
import time

from wintap_process_validation.workload import generate_process_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a sensor-neutral process workload manifest")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--short-lived-children", type=int, default=6)
    args = parser.parse_args()

    run_id = args.run_id or f"process-baseline-{int(time.time())}"
    args.run_dir.mkdir(parents=True, exist_ok=True)
    manifest = generate_process_baseline(run_id, short_lived_children=args.short_lived_children)
    manifest.write(args.run_dir / "manifest.json")
    print(f"wrote {args.run_dir / 'manifest.json'}")
    print(f"cases={len(manifest.cases)} processes={len(manifest.processes)} notes={len(manifest.notes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
