
"""
Minimal internal tree representation for Algorithm 1 ("Basic Matching Algorithm")
from "The Needle Is A Thread: Finding Planted Paths in Noisy Process Trees".

The DP needs only:
- parent[u]: the unique ancestor anc(u) (=-1 for the root),
- label[u]: the node label ϕ(u).

We additionally store:
- orig_index[u]: mapping back to the original node ids in the input graph,
  because we often reorder nodes to satisfy the paper's ordering convention.

Invariant used throughout this package:
- root is internal node 0 with parent[0] == -1,
- for all i>0, 0 <= parent[i] < i (parent precedes child).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np


@dataclass(frozen=True)
class TreeData:
    """
    A rooted directed tree with nodes indexed 0..n-1.

    Parameters
    ----------
    parent:
        parent[i] is the parent of node i; parent[0] must be -1.
        For i>0, must satisfy 0 <= parent[i] < i (ordering constraint).
    label:
        length-n sequence of labels (often str / tuple[str] / etc).
    orig_index:
        internal -> original vertex id in the source graph.
    """
    parent: np.ndarray
    label: Sequence[Any]
    orig_index: np.ndarray

    def __post_init__(self) -> None:
        parent = np.asarray(self.parent)
        orig = np.asarray(self.orig_index)

        if parent.ndim != 1:
            raise ValueError("parent must be a 1D array")
        n = int(parent.shape[0])

        if n <= 0:
            raise ValueError("TreeData cannot be empty")

        if orig.shape != (n,):
            raise ValueError("orig_index must have shape (n,) matching parent")

        if len(self.label) != n:
            raise ValueError("label must have length n matching parent")

        if int(parent[0]) != -1:
            raise ValueError("Expected parent[0] == -1 (root convention)")

        for i in range(1, n):
            p = int(parent[i])
            if p < 0 or p >= i:
                raise ValueError(f"Invalid parent[{i}]={p}. Expected 0 <= parent[i] < i.")

    @property
    def n(self) -> int:
        return int(np.asarray(self.parent).shape[0])

    def ancestors_shifted(self) -> np.ndarray:
        """
        Return anc_shift[i] = parent[i] + 1. Root has anc_shift[0] = 0.

        This supports "shifted DP" indexing where DP row/col 0 corresponds to the
        virtual node -1 in the paper (so roots and boundaries don't need special cases).
        """
        parent = np.asarray(self.parent, dtype=np.int64)
        return (parent + 1).astype(np.int64, copy=False)
