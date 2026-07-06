import base64
import binascii
import json


def load_report(json_file_path: str) -> dict:
    with open(json_file_path, "r") as f:
        return json.load(f)


def sanitize_operation_name(name: str) -> str:
    name = name or "unnamed_operation"
    return (
        name.replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .lower()
    )


def is_base64(s: str) -> bool:
    if not isinstance(s, (str, bytes)):
        return False
    try:
        base64.b64decode(s, validate=True)
        return True
    except binascii.Error:
        return False


def decode_if_base64(s: str) -> str:
    if not s:
        return s
    if is_base64(s):
        try:
            return base64.b64decode(s).decode("utf-8")
        except Exception:
            return s
    return s


def iter_hosts(report: dict):
    host_group = report.get("host_group", [])
    if not isinstance(host_group, list):
        return
    for host in host_group:
        if isinstance(host, dict):
            yield host


def build_hostmap(report: dict) -> dict:
    hostmap = {}
    for host in iter_hosts(report):
        paw = host.get("paw")
        if paw:
            hostmap[paw] = host.get("host")
    return hostmap


def iter_links(report: dict):
    """Yield link objects regardless of whether they're top-level or per-host."""
    top = report.get("links")
    if isinstance(top, list) and top:
        for link in top:
            if isinstance(link, dict):
                yield link
        return

    for host in iter_hosts(report):
        paw = host.get("paw")
        links = host.get("links", [])
        if not isinstance(links, list):
            continue
        for link in links:
            if not isinstance(link, dict):
                continue
            if paw and "paw" not in link:
                link = dict(link)
                link["paw"] = paw
            yield link


def iter_steps(report: dict):
    """Yield step objects regardless of whether steps are dict[paw]->bundle or a list of bundles."""
    steps = report.get("steps")
    if isinstance(steps, dict):
        for paw, bundle in steps.items():
            if not isinstance(bundle, dict):
                continue
            inner = bundle.get("steps", [])
            if not isinstance(inner, list):
                continue
            for step in inner:
                if not isinstance(step, dict):
                    continue
                if paw and "paw" not in step:
                    step = dict(step)
                    step["paw"] = paw
                yield step
        return

    if isinstance(steps, list):
        for bundle in steps:
            if not isinstance(bundle, dict):
                continue
            paw = bundle.get("paw")
            inner = bundle.get("steps", [])
            if not isinstance(inner, list):
                continue
            for step in inner:
                if not isinstance(step, dict):
                    continue
                if paw and "paw" not in step:
                    step = dict(step)
                    step["paw"] = paw
                yield step
