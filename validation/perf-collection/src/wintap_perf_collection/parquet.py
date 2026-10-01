from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import duckdb
import pandas as pd


def event_partition_dir(data_root: Path, event_type: str, event_time: datetime | None = None) -> Path:
    now = event_time or datetime.now(timezone.utc)
    day_pk = now.strftime("%Y%m%d")
    hour_pk = now.strftime("%H")
    return data_root / "parquet" / "raw_sensor" / event_type / f"dayPK={day_pk}" / f"hourPK={hour_pk}"


def write_partitioned_parquet(rows: list[dict], data_root: Path, event_type: str, run_id: str) -> Path | None:
    if not rows:
        return None
    out_dir = event_partition_dir(data_root, event_type)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{event_type}-{run_id}-{uuid4().hex[:12]}.parquet"

    frame = pd.DataFrame(rows)
    con = duckdb.connect()
    try:
        con.register("rows_df", frame)
        con.execute("copy rows_df to ? (format parquet)", [str(out_path)])
    finally:
        con.close()
    return out_path
