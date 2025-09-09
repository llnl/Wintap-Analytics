from bs4 import BeautifulSoup
from collections.abc import Iterator
from contextlib import contextmanager
import duckdb
import json
import logging as lg
from pathlib import Path
import re
import requests


LOG = lg.getLogger(__name__)
WORK = Path("work")
WORK.mkdir(parents=True, exist_ok=True)
_CONFIG = WORK / "config.json"
_URL_ACME4 = "https://gdo168.llnl.gov/data/ACME4/stdview-20240819-20240923/"


@contextmanager
def config() -> Iterator[dict]:
    text = _CONFIG.read_text(encoding="utf-8") if _CONFIG.is_file() else ""
    config = json.loads(text) if text else {}
    yield config
    _CONFIG.write_text(json.dumps(config), encoding="utf-8")


def set_local_dataset(uri: Path | str) -> None:
    with config() as cfg:
        cfg["dataset_local"] = str(uri)


def _iter_dataset() -> Iterator[str]:
    with config() as cfg:
        uri_dataset = cfg.get("dataset_local") or _URL_ACME4
        if re.match(r"^https?://", uri_dataset):
            LOG.info("Access dataset over httpfs")
            parent = uri_dataset
            if not parent.endswith("/"):
                parent += "/"
            resp = requests.get(uri_dataset)
            if resp.ok:
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=re.compile(r".+\.parquet$")):
                    name_pq = a.attrs["href"]
                    name, _ = name_pq.rsplit(".", maxsplit=1)
                    yield name, parent + name_pq
        else:
            LOG.info("Access dataset over local filesystem")
            parent = Path(uri_dataset)
            for path in parent.glob("*.parquet"):
                yield path.with_suffix("").name, path

        
def connect_db():
    conn = duckdb.connect(WORK / "work.db")
    conn.sql("INSTALL httpfs; LOAD httpfs;")
    for name_view, uri_parquet in _iter_dataset():
        LOG.debug(f"Add view {name_view} over {uri_parquet}")
        conn.sql(f"create or replace view {name_view} as select * from '{uri_parquet}'")
    return conn

