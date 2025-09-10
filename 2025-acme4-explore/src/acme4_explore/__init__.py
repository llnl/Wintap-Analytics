from bs4 import BeautifulSoup
from collections.abc import Iterator
from contextlib import contextmanager
import duckdb
import json
import logging as lg
import os
from pathlib import Path
import re
import requests


_LOG = lg.getLogger(__name__)
_URL_ACME4 = "https://gdo168.llnl.gov/data/ACME4/stdview-20240819-20240923/"


@contextmanager
def dir_work() -> Iterator[Path]:
    path = Path(os.environ.get("DIR_WORK") or "./.work")
    path.mkdir(parents=True, exist_ok=True)
    yield path


def _iter_dataset() -> Iterator[str]:
    uri_dataset = os.path.expanduser(
        os.path.expandvars(os.environ.get("URI_DATASET") or _URL_ACME4)
    )
    if re.match(r"^https?://", uri_dataset):
        _LOG.info("Access dataset over httpfs")
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
        _LOG.info("Access dataset over local filesystem")
        parent = Path(uri_dataset)
        for path in parent.glob("*.parquet"):
            yield path.with_suffix("").name, path


def connect_db():
    conn = duckdb.connect()
    conn.sql("INSTALL httpfs; LOAD httpfs;")
    for name_view, uri_parquet in _iter_dataset():
        _LOG.debug(f"Add standard view to {name_view} over {uri_parquet}")
        conn.sql(f"create or replace view {name_view} as select * from '{uri_parquet}'")
    with dir_work() as dir:
        for path in dir.glob("*.parquet"):
            name_view = path.with_suffix("").name
            _LOG.debug(f"View custom data file {path} as {name_view}")
            conn.sql(f"create or replace view {name_view} as select * from '{path}'")
    return conn


def logging_config():
    for name, level in json.loads(os.environ.get("LOG_LEVEL") or "{}").items():
        lg.getLogger(name).setLevel(level)
    return json.loads(os.environ.get("LOGGING") or "{}")
