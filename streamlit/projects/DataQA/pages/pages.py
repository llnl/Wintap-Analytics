from dataclasses import dataclass


@dataclass
class Page:
    filename: str
    label: str


def app_pages():
    """
    Define metadata for pages used in this app.
    """
    return [
        Page("pages/initial_page.py", "Dataset Summary"),
        Page("pages/raw_events.py", "Raw Events"),
        Page("pages/dll_inspector.py", "DQA DLLs"),
        Page("pages/debug_page.py", "Debug Tools"),
    ]
