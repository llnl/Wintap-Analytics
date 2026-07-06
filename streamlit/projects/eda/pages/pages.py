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
        Page("pages/initial_page.py", "Initial Page"),
        Page("pages/graph_viz_page.py", "Graph Viz"),
        Page("common/debug_page.py", "Debug Stuff Page"),
    ]
