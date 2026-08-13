from __future__ import annotations

import argparse
from pathlib import Path

from wintap_process_validation.normalizers.lintap import read_lintap_process_parquet, write_lintap_normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Lintap process Parquet into validation JSONL tables")
    parser.add_argument("--parquet-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    rows = read_lintap_process_parquet(args.parquet_root)
    write_lintap_normalized(rows, args.run_id, args.out_dir)
    print(f"normalized {len(rows)} Lintap process row(s) into {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
