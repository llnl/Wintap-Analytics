
"""
I/O utilities for converting an igraph directed tree into the internal TreeData representation.

The paper assumes:
- exactly one root node (in-degree 0), and
- nodes are ordered so that parent precedes child (u <_T v implies u < v),
- and (for exposition) the root is node 0, with ancestor anc(0) = -1.

We support:
- validation that an igraph graph is a directed rooted tree, and
- optional reordering into a valid topological order (root first, parent < child),
  returning TreeData with an `orig_index` mapping so match paths can be reported
  in original node ids.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

import numpy as np

from tree_data import TreeData


def _require_igraph() -> Any:
    try:
        import igraph as ig  # type: ignore
    except Exception as e:  # pragma: no cover
        raise ImportError(
            "igraph is required for igraph_to_treedata but is not installed."
        ) from e
    return ig


def _build_parent_and_children_from_edges(
    n: int, edges: Sequence[Tuple[int, int]]
) -> Tuple[np.ndarray, List[List[int]]]:
    """
    Build parent[] and children lists from a list of directed edges (parent -> child).
    """
    parent = np.full(n, -1, dtype=np.int64)
    children: List[List[int]] = [[] for _ in range(n)]

    for a, b in edges:
        if a < 0 or a >= n or b < 0 or b >= n:
            raise ValueError(f"Edge ({a},{b}) has vertex id outside [0,{n-1}]")
        if a == b:
            raise ValueError(f"Self-loop at node {a} is not allowed in a tree")
        if parent[b] != -1:
            raise ValueError(f"Node {b} has multiple parents: {parent[b]} and {a}")
        parent[b] = a
        children[a].append(b)

    return parent, children


def _validate_rooted_tree(parent: np.ndarray, children: List[List[int]]) -> int:
    """
    Validate: exactly one root, all nodes reachable from root, no missing parents.
    Returns the root id.
    """
    n = int(parent.shape[0])
    roots = np.flatnonzero(parent == -1).tolist()
    if len(roots) != 1:
        raise ValueError(f"Expected exactly one root; found {len(roots)} roots: {roots}")
    root = int(roots[0])

    # Reachability check (also catches disconnected graphs).
    seen = np.zeros(n, dtype=bool)
    stack = [root]
    seen[root] = True
    while stack:
        u = stack.pop()
        for v in children[u]:
            if seen[v]:
                raise ValueError("Cycle detected or node reachable via multiple parent paths")
            seen[v] = True
            stack.append(v)
    if not bool(np.all(seen)):
        missing = np.flatnonzero(~seen).tolist()
        raise ValueError(
            f"Graph is not connected from root; unreachable nodes: "
            f"{missing[:20]}{'...' if len(missing)>20 else ''}"
        )

    # Parent validity (besides root): every other node must have a parent.
    for i in range(n):
        if i == root:
            continue
        if int(parent[i]) == -1:
            raise ValueError(f"Node {i} has no parent but is not the root")

    return root


def _already_valid_order(root: int, parent: np.ndarray) -> bool:
    """
    Check whether the current labelling already meets the conventions:
    root is node 0 and parent[i] < i for all i>0.
    """
    if root != 0:
        return False
    n = int(parent.shape[0])
    if int(parent[0]) != -1:
        return False
    for i in range(1, n):
        p = int(parent[i])
        if p < 0 or p >= i:
            return False
    return True


def _topological_order_tree(
    root: int,
    children: List[List[int]],
    key: Optional[Sequence[Any]] = None,
) -> List[int]:
    """
    Produce an ordering with root first and parent before child.
    If key is provided, nodes in the "frontier" are chosen by increasing key (then node id).
    """
    n = len(children)
    if key is None:
        # Deterministic DFS with children sorted by node id.
        children_sorted = [sorted(ch) for ch in children]
        order: List[int] = []
        stack = [root]
        while stack:
            u = stack.pop()
            order.append(u)
            ch = children_sorted[u]
            for v in reversed(ch):
                stack.append(v)
        if len(order) != n:
            raise ValueError("Topological ordering failed (unexpected)")
        return order

    import heapq
    heap: List[Tuple[Any, int]] = []
    heapq.heappush(heap, (key[root], root))
    order = []
    while heap:
        _, u = heapq.heappop(heap)
        order.append(u)
        for v in children[u]:
            heapq.heappush(heap, (key[v], v))
    if len(order) != n:
        raise ValueError("Timestamp/topological ordering failed (unexpected)")
    return order


def igraph_to_treedata(
    G: Any,
    *,
    phi_name: str = "label",
    order: str = "auto",
    ts_field: Optional[str] = None,
    strict_tree: bool = True,
) -> TreeData:
    """
    Convert an igraph directed tree into internal TreeData.

    Parameters
    ----------
    G:
        igraph.Graph (directed) with edges parent -> child.
    phi_name:
        Vertex attribute name to use as node label ϕ(u).
    order:
        One of:
          - "given": require root==0 and parent[i] < i; no reordering.
          - "topological": reorder to DFS-topological order (root first, parent<child).
          - "timestamp": reorder using ts_field as a tie-break in a heap frontier.
          - "auto": if already valid, keep; otherwise reorder ("timestamp" if ts_field else "topological").
    ts_field:
        Vertex attribute to use for "timestamp" ordering (must be comparable, no None).
    strict_tree:
        If True, require |E| = n-1 (except n=1). This rules out extra edges.

    Returns
    -------
    TreeData
    """
    ig = _require_igraph()
    if not isinstance(G, ig.Graph):  # type: ignore
        raise TypeError("G must be an igraph.Graph")

    if not G.is_directed():
        raise ValueError("G must be directed (edges parent -> child)")

    n = int(G.vcount())
    if n == 0:
        raise ValueError("G has no vertices")

    edges = list(map(tuple, G.get_edgelist()))
    if strict_tree:
        expected = 0 if n == 1 else n - 1
        if len(edges) != expected:
            raise ValueError(f"Expected a tree with {expected} edges; found {len(edges)} edges")

    if phi_name not in G.vs.attributes():
        raise ValueError(f"Missing vertex attribute '{phi_name}'")

    parent_old, children_old = _build_parent_and_children_from_edges(n, edges)
    root_old = _validate_rooted_tree(parent_old, children_old)

    if order not in {"auto", "given", "topological", "timestamp"}:
        raise ValueError("order must be one of: 'auto', 'given', 'topological', 'timestamp'")

    if order == "given":
        if not _already_valid_order(root_old, parent_old):
            raise ValueError(
                "Input graph ordering is not valid for Algorithm 1. "
                "Either reorder the graph externally or use order='auto'/'topological'/'timestamp'."
            )
        order_old = list(range(n))
    else:
        if order == "auto" and _already_valid_order(root_old, parent_old):
            order_old = list(range(n))
        else:
            if order == "timestamp" or (order == "auto" and ts_field is not None):
                if ts_field is None:
                    raise ValueError("order='timestamp' requires ts_field")
                if ts_field not in G.vs.attributes():
                    raise ValueError(f"Missing vertex attribute '{ts_field}' for timestamp ordering")
                ts = list(G.vs[ts_field])
                if any(t is None for t in ts):
                    raise ValueError(f"Null values found in vertex attribute '{ts_field}'")
                order_old = _topological_order_tree(root_old, children_old, key=ts)
            else:
                order_old = _topological_order_tree(root_old, children_old, key=None)

    order_old_arr = np.asarray(order_old, dtype=np.int64)
    old_to_new = np.empty(n, dtype=np.int64)
    old_to_new[order_old_arr] = np.arange(n, dtype=np.int64)

    new_parent = np.full(n, -1, dtype=np.int64)
    for new_i, old_i in enumerate(order_old):
        p_old = int(parent_old[old_i])
        if p_old == -1:
            new_parent[new_i] = -1
        else:
            new_parent[new_i] = int(old_to_new[p_old])

    if int(new_parent[0]) != -1:
        raise ValueError("Internal error: expected new root at index 0")

    for i in range(1, n):
        p = int(new_parent[i])
        if p < 0 or p >= i:
            raise ValueError("Failed to produce a parent-before-child ordering")

    labels_old = list(G.vs[phi_name])
    labels_new = [labels_old[old_i] for old_i in order_old]

    orig_index = order_old_arr.copy()  # internal -> original
    return TreeData(
        parent=new_parent.astype(np.int32, copy=False),
        label=labels_new,
        orig_index=orig_index.astype(np.int32, copy=False),
    )


def validate_igraph_ordering(
    G: Any,
    *,
    phi_name: str = "label",
    strict_tree: bool = True,
) -> None:
    """
    Raise if an igraph directed tree does *not* satisfy the ordering conventions assumed
    in Algorithm 1:

      - root is node 0, with parent[0] = -1
      - for every node i>0, its unique parent satisfies parent[i] < i

    This function validates structure + ordering. It does *not* reorder the graph.
    Use `igraph_to_treedata(..., order="auto"/"topological"/"timestamp")` to reorder.
    """
    _ = igraph_to_treedata(
        G,
        phi_name=phi_name,
        order="given",
        strict_tree=strict_tree,
    )
