from __future__ import annotations

"""
fast_match.py

Specialized exact matchers for two common scoring families:

1. Equality scoring
       score(label_u, label_v) = token_weight[label] if label_u == label_v else 0

2. Any-overlap scoring on label-sets / multisets
       score(label_u, label_v) = max(token_weight[t] for t in label_u ∩ label_v)
   with default token_weight[t] = 1.

These avoid generic Python weight-function calls inside the O(nm) DP and instead:
- integerize labels/tokens once,
- store compact per-vertex representations,
- run the DP in numba when available.

Notes
-----
- This is intentionally a *separate* module rather than a rewrite of the generic
  matcher. The goal is to give a fast path for the simple special cases above
  while leaving the flexible generic matcher untouched.
- For maximum speed across many pairwise matches, pre-fit one encoder on the full
  dataset and pre-encode each tree once. Then call `predict_encoded(...)`.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Hashable, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

try:  # package import
    from .tree_data import TreeData
    from .igraph_io import igraph_to_treedata
except Exception:  # loose-file import
    from tree_data import TreeData  # type: ignore
    from igraph_io import igraph_to_treedata  # type: ignore

try:
    from numba import njit
    HAVE_NUMBA = True
except Exception:  # pragma: no cover
    HAVE_NUMBA = False
    def njit(*args, **kwargs):
        def deco(fn):
            return fn
        return deco


LabelGetter = Optional[Callable[[Any], Any]]


@dataclass(frozen=True)
class FastAlignmentResult:
    path_internal: List[Tuple[int, int]]
    score: float
    end_internal: Tuple[int, int]
    A: Optional[np.ndarray] = None
    C: Optional[np.ndarray] = None


@dataclass(frozen=True)
class EncodedTreeEquality:
    tree: TreeData
    label_ids: np.ndarray  # shape (n,), int32; -1 means empty / unknown


@dataclass(frozen=True)
class EncodedTreeOverlap:
    tree: TreeData
    offsets: np.ndarray  # shape (n+1,), int32
    flat_token_ids: np.ndarray  # concatenation of per-vertex sorted unique token ids


EncodedTree = Union[EncodedTreeEquality, EncodedTreeOverlap]


def _looks_like_treedata(x: Any) -> bool:
    return hasattr(x, "parent") and hasattr(x, "label") and hasattr(x, "orig_index")


def _as_treedata(
    G: Any,
    *,
    phi_name: str,
    order: str,
    ts_field: Optional[str],
    strict_tree: bool,
) -> TreeData:
    if _looks_like_treedata(G):
        return G  # type: ignore[return-value]
    return igraph_to_treedata(
        G,
        phi_name=phi_name,
        order=order,
        ts_field=ts_field,
        strict_tree=strict_tree,
    )


def _default_extract(label: Any) -> Any:
    """
    Conservative extractor that tries a few common structured-label conventions.
    If you have more complex labels, pass `label_getter=` explicitly.
    """
    if isinstance(label, dict):
        for key in ("Labels", "labels", "label", "sym", "symbol", "name", "token", "tokens", "token_set"):
            if key in label:
                return label[key]
    return label


def _is_scalar_token(x: Any) -> bool:
    return isinstance(x, (str, bytes, int, float, np.integer, np.floating))


def _extract_raw(label: Any, label_getter: LabelGetter) -> Any:
    raw = label_getter(label) if label_getter is not None else _default_extract(label)
    return raw


def _normalize_eq_label(label: Any, label_getter: LabelGetter) -> Optional[Hashable]:
    raw = _extract_raw(label, label_getter)
    if raw is None:
        return None
    if isinstance(raw, dict):
        raise TypeError("Equality mode needs a scalar token or singleton iterable; got dict. Pass label_getter=...")
    if _is_scalar_token(raw):
        try:
            hash(raw)
        except Exception as e:
            raise TypeError(f"Equality-mode label token must be hashable, got {type(raw)}") from e
        return raw  # type: ignore[return-value]
    if isinstance(raw, (list, tuple, set, frozenset, np.ndarray)):
        seq = list(raw)
        if len(seq) == 0:
            return None
        if len(seq) != 1:
            raise ValueError(
                "Equality mode received a multi-token label. Use mode='overlap' or pass a label_getter that extracts one token."
            )
        tok = seq[0]
        try:
            hash(tok)
        except Exception as e:
            raise TypeError(f"Equality-mode label token must be hashable, got {type(tok)}") from e
        return tok  # type: ignore[return-value]
    try:
        hash(raw)
    except Exception as e:
        raise TypeError(f"Equality-mode label token must be hashable, got {type(raw)}") from e
    return raw  # type: ignore[return-value]


def _normalize_overlap_label(label: Any, label_getter: LabelGetter) -> Tuple[Hashable, ...]:
    raw = _extract_raw(label, label_getter)
    if raw is None:
        return ()
    if _is_scalar_token(raw):
        toks = [raw]
    elif isinstance(raw, dict):
        raise TypeError("Overlap mode needs an iterable of tokens or a scalar token; got dict. Pass label_getter=...")
    elif isinstance(raw, np.ndarray):
        toks = raw.tolist()
    else:
        try:
            toks = list(raw)
        except TypeError:
            toks = [raw]

    uniq: Dict[Hashable, None] = {}
    for tok in toks:
        try:
            hash(tok)
        except Exception as e:
            raise TypeError(f"Overlap-mode tokens must be hashable, got {type(tok)}") from e
        uniq[tok] = None
    if not uniq:
        return ()
    # Deterministic order that does not require tokens to be mutually comparable.
    return tuple(sorted(uniq.keys(), key=lambda x: repr((type(x).__name__, x))))


class FastLabelEncoder:
    """
    Integerizes labels/tokens for the specialized fast matchers.

    Parameters
    ----------
    mode:
        "equality" or "overlap".
    label_getter:
        Optional callable extracting the relevant field from each vertex label.
    token_weights:
        Optional mapping token -> score used when a token matches.
        Default weight is `default_weight` for tokens not present here.
    default_weight:
        Default token match weight.
    """

    def __init__(
        self,
        *,
        mode: str = "equality",
        label_getter: LabelGetter = None,
        token_weights: Optional[Mapping[Any, float]] = None,
        default_weight: float = 1.0,
    ) -> None:
        mode = mode.lower().strip()
        if mode not in {"equality", "overlap"}:
            raise ValueError("mode must be 'equality' or 'overlap'")
        self.mode = mode
        self.label_getter = label_getter
        self.token_weights = dict(token_weights or {})
        self.default_weight = float(default_weight)
        self.token_to_id: Dict[Hashable, int] = {}
        self.id_to_token: List[Hashable] = []
        self.weight_by_id: Optional[np.ndarray] = None
        self._fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    def _iter_tokens_from_label(self, label: Any) -> Iterable[Hashable]:
        if self.mode == "equality":
            tok = _normalize_eq_label(label, self.label_getter)
            if tok is not None:
                yield tok
        else:
            for tok in _normalize_overlap_label(label, self.label_getter):
                yield tok

    def fit_from_trees(self, trees: Sequence[TreeData]) -> "FastLabelEncoder":
        token_to_id: Dict[Hashable, int] = {}
        id_to_token: List[Hashable] = []
        for tree in trees:
            for lab in tree.label:
                for tok in self._iter_tokens_from_label(lab):
                    if tok not in token_to_id:
                        token_to_id[tok] = len(id_to_token)
                        id_to_token.append(tok)
        self.token_to_id = token_to_id
        self.id_to_token = id_to_token
        self.weight_by_id = np.asarray(
            [float(self.token_weights.get(tok, self.default_weight)) for tok in id_to_token],
            dtype=np.float32,
        )
        self._fitted = True
        return self

    def _check_fitted(self) -> None:
        if not self._fitted or self.weight_by_id is None:
            raise RuntimeError("FastLabelEncoder is not fitted. Call fit_from_trees(...) first.")

    def transform_tree(self, tree: TreeData) -> EncodedTree:
        self._check_fitted()
        n = tree.n
        if self.mode == "equality":
            ids = np.full(n, -1, dtype=np.int32)
            for i, lab in enumerate(tree.label):
                tok = _normalize_eq_label(lab, self.label_getter)
                if tok is None:
                    continue
                tid = self.token_to_id.get(tok)
                if tid is not None:
                    ids[i] = np.int32(tid)
            return EncodedTreeEquality(tree=tree, label_ids=ids)

        offsets = np.zeros(n + 1, dtype=np.int32)
        flat: List[int] = []
        for i, lab in enumerate(tree.label):
            toks = _normalize_overlap_label(lab, self.label_getter)
            if toks:
                ids_here = sorted({self.token_to_id[tok] for tok in toks if tok in self.token_to_id})
                flat.extend(ids_here)
            offsets[i + 1] = np.int32(len(flat))
        flat_arr = np.asarray(flat, dtype=np.int32)
        return EncodedTreeOverlap(tree=tree, offsets=offsets, flat_token_ids=flat_arr)

    def fit_transform_pair(self, G: TreeData, H: TreeData) -> Tuple[EncodedTree, EncodedTree]:
        self.fit_from_trees([G, H])
        return self.transform_tree(G), self.transform_tree(H)


if HAVE_NUMBA:

    @njit(cache=True)
    def _dp_equality_numba(
        parentG: np.ndarray,
        idsG: np.ndarray,
        parentH: np.ndarray,
        idsH: np.ndarray,
        weight_by_id: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, int, int, float]:
        n = parentG.shape[0]
        m = parentH.shape[0]
        A = np.zeros((n + 1, m + 1), dtype=np.float32)
        C = np.zeros((n + 1, m + 1), dtype=np.uint8)
        ancG = parentG + 1
        ancH = parentH + 1

        best_score = 0.0
        U_star = 1
        V_star = 1

        for U in range(1, n + 1):
            u = U - 1
            ancU = ancG[u]
            idu = idsG[u]
            for V in range(1, m + 1):
                v = V - 1
                ancV = ancH[v]
                opt1 = A[ancU, V]
                opt2 = A[U, ancV]
                w_uv = 0.0
                if idu >= 0 and idu == idsH[v]:
                    w_uv = weight_by_id[idu]
                opt3 = w_uv + A[ancU, ancV]

                if opt3 >= opt2 and opt3 >= opt1:
                    val = opt3
                    choice = 3
                elif opt2 >= opt1:
                    val = opt2
                    choice = 2
                else:
                    val = opt1
                    choice = 1

                A[U, V] = val
                C[U, V] = choice
                if val > best_score:
                    best_score = val
                    U_star = U
                    V_star = V
        return A, C, U_star, V_star, best_score


    @njit(cache=True)
    def _score_overlap_vertex_pair(
        offG: np.ndarray,
        flatG: np.ndarray,
        u: int,
        offH: np.ndarray,
        flatH: np.ndarray,
        v: int,
        weight_by_id: np.ndarray,
    ) -> float:
        i = offG[u]
        i_end = offG[u + 1]
        j = offH[v]
        j_end = offH[v + 1]
        best = 0.0
        while i < i_end and j < j_end:
            a = flatG[i]
            b = flatH[j]
            if a == b:
                w = weight_by_id[a]
                if w > best:
                    best = w
                i += 1
                j += 1
            elif a < b:
                i += 1
            else:
                j += 1
        return best


    @njit(cache=True)
    def _dp_overlap_numba(
        parentG: np.ndarray,
        offG: np.ndarray,
        flatG: np.ndarray,
        parentH: np.ndarray,
        offH: np.ndarray,
        flatH: np.ndarray,
        weight_by_id: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, int, int, float]:
        n = parentG.shape[0]
        m = parentH.shape[0]
        A = np.zeros((n + 1, m + 1), dtype=np.float32)
        C = np.zeros((n + 1, m + 1), dtype=np.uint8)
        ancG = parentG + 1
        ancH = parentH + 1

        best_score = 0.0
        U_star = 1
        V_star = 1

        for U in range(1, n + 1):
            u = U - 1
            ancU = ancG[u]
            for V in range(1, m + 1):
                v = V - 1
                ancV = ancH[v]
                opt1 = A[ancU, V]
                opt2 = A[U, ancV]
                w_uv = _score_overlap_vertex_pair(offG, flatG, u, offH, flatH, v, weight_by_id)
                opt3 = w_uv + A[ancU, ancV]

                if opt3 >= opt2 and opt3 >= opt1:
                    val = opt3
                    choice = 3
                elif opt2 >= opt1:
                    val = opt2
                    choice = 2
                else:
                    val = opt1
                    choice = 1

                A[U, V] = val
                C[U, V] = choice
                if val > best_score:
                    best_score = val
                    U_star = U
                    V_star = V
        return A, C, U_star, V_star, best_score

else:

    def _dp_equality_numba(parentG, idsG, parentH, idsH, weight_by_id):
        n = parentG.shape[0]
        m = parentH.shape[0]
        A = np.zeros((n + 1, m + 1), dtype=np.float32)
        C = np.zeros((n + 1, m + 1), dtype=np.uint8)
        ancG = parentG + 1
        ancH = parentH + 1
        best_score = 0.0
        U_star, V_star = 1, 1
        for U in range(1, n + 1):
            u = U - 1
            ancU = int(ancG[u])
            idu = int(idsG[u])
            for V in range(1, m + 1):
                v = V - 1
                ancV = int(ancH[v])
                opt1 = A[ancU, V]
                opt2 = A[U, ancV]
                w_uv = float(weight_by_id[idu]) if (idu >= 0 and idu == int(idsH[v])) else 0.0
                opt3 = w_uv + A[ancU, ancV]
                if opt3 >= opt2 and opt3 >= opt1:
                    val = opt3
                    choice = 3
                elif opt2 >= opt1:
                    val = opt2
                    choice = 2
                else:
                    val = opt1
                    choice = 1
                A[U, V] = val
                C[U, V] = choice
                if val > best_score:
                    best_score = float(val)
                    U_star = U
                    V_star = V
        return A, C, U_star, V_star, best_score

    def _dp_overlap_numba(parentG, offG, flatG, parentH, offH, flatH, weight_by_id):
        n = parentG.shape[0]
        m = parentH.shape[0]
        A = np.zeros((n + 1, m + 1), dtype=np.float32)
        C = np.zeros((n + 1, m + 1), dtype=np.uint8)
        ancG = parentG + 1
        ancH = parentH + 1
        best_score = 0.0
        U_star, V_star = 1, 1
        for U in range(1, n + 1):
            u = U - 1
            ancU = int(ancG[u])
            for V in range(1, m + 1):
                v = V - 1
                ancV = int(ancH[v])
                opt1 = A[ancU, V]
                opt2 = A[U, ancV]
                i = int(offG[u])
                i_end = int(offG[u + 1])
                j = int(offH[v])
                j_end = int(offH[v + 1])
                best = 0.0
                while i < i_end and j < j_end:
                    a = int(flatG[i])
                    b = int(flatH[j])
                    if a == b:
                        w = float(weight_by_id[a])
                        if w > best:
                            best = w
                        i += 1
                        j += 1
                    elif a < b:
                        i += 1
                    else:
                        j += 1
                opt3 = best + A[ancU, ancV]
                if opt3 >= opt2 and opt3 >= opt1:
                    val = opt3
                    choice = 3
                elif opt2 >= opt1:
                    val = opt2
                    choice = 2
                else:
                    val = opt1
                    choice = 1
                A[U, V] = val
                C[U, V] = choice
                if val > best_score:
                    best_score = float(val)
                    U_star = U
                    V_star = V
        return A, C, U_star, V_star, best_score


def _traceback(parentG: np.ndarray, parentH: np.ndarray, C: np.ndarray, U_star: int, V_star: int) -> List[Tuple[int, int]]:
    """
    Raw traceback: append every diagonal/"match" transition, including 0-score
    transitions that were selected only because of a tie.

    This preserves the previous implementation's behavior and is retained for
    debugging, but public fast-matcher results should usually use the scored
    traceback helpers below.
    """
    ancG = np.asarray(parentG, dtype=np.int64) + 1
    ancH = np.asarray(parentH, dtype=np.int64) + 1
    path_rev: List[Tuple[int, int]] = []
    U, V = int(U_star), int(V_star)
    while U != 0 and V != 0:
        choice = int(C[U, V])
        if choice == 3:
            path_rev.append((U - 1, V - 1))
        if choice == 1:
            U = int(ancG[U - 1])
        elif choice == 2:
            V = int(ancH[V - 1])
        elif choice == 3:
            U = int(ancG[U - 1])
            V = int(ancH[V - 1])
        else:
            raise RuntimeError(f"Invalid traceback state C[{U},{V}]={choice}")
    path_rev.reverse()
    return path_rev


def _traceback_equality_scored(
    parentG: np.ndarray,
    idsG: np.ndarray,
    parentH: np.ndarray,
    idsH: np.ndarray,
    weight_by_id: np.ndarray,
    C: np.ndarray,
    U_star: int,
    V_star: int,
    *,
    keep_zero_weight_matches: bool = False,
) -> List[Tuple[int, int]]:
    """
    Trace back the selected DP route, but only emit vertex pairs that actually
    contribute positive score unless keep_zero_weight_matches=True.

    The DP recurrence may choose a diagonal transition with w_uv == 0 because
    ties are broken toward option 3. Such a transition is useful as a traceback
    step, but it is not a semantic match and should not appear in the returned
    matched path by default.
    """
    ancG = np.asarray(parentG, dtype=np.int64) + 1
    ancH = np.asarray(parentH, dtype=np.int64) + 1
    idsG = np.asarray(idsG, dtype=np.int64)
    idsH = np.asarray(idsH, dtype=np.int64)
    weight_by_id = np.asarray(weight_by_id, dtype=np.float32)

    path_rev: List[Tuple[int, int]] = []
    U, V = int(U_star), int(V_star)
    while U != 0 and V != 0:
        choice = int(C[U, V])
        if choice == 3:
            u = U - 1
            v = V - 1
            idu = int(idsG[u])
            if idu >= 0 and idu == int(idsH[v]):
                w_uv = float(weight_by_id[idu])
            else:
                w_uv = 0.0
            if keep_zero_weight_matches or w_uv > 0.0:
                path_rev.append((u, v))

        if choice == 1:
            U = int(ancG[U - 1])
        elif choice == 2:
            V = int(ancH[V - 1])
        elif choice == 3:
            U = int(ancG[U - 1])
            V = int(ancH[V - 1])
        else:
            raise RuntimeError(f"Invalid traceback state C[{U},{V}]={choice}")

    path_rev.reverse()
    return path_rev


def _score_overlap_vertex_pair_py(
    offG: np.ndarray,
    flatG: np.ndarray,
    u: int,
    offH: np.ndarray,
    flatH: np.ndarray,
    v: int,
    weight_by_id: np.ndarray,
) -> float:
    i = int(offG[u])
    i_end = int(offG[u + 1])
    j = int(offH[v])
    j_end = int(offH[v + 1])
    best = 0.0
    while i < i_end and j < j_end:
        a = int(flatG[i])
        b = int(flatH[j])
        if a == b:
            w = float(weight_by_id[a])
            if w > best:
                best = w
            i += 1
            j += 1
        elif a < b:
            i += 1
        else:
            j += 1
    return best


def _traceback_overlap_scored(
    parentG: np.ndarray,
    offG: np.ndarray,
    flatG: np.ndarray,
    parentH: np.ndarray,
    offH: np.ndarray,
    flatH: np.ndarray,
    weight_by_id: np.ndarray,
    C: np.ndarray,
    U_star: int,
    V_star: int,
    *,
    keep_zero_weight_matches: bool = False,
) -> List[Tuple[int, int]]:
    """Scored traceback for overlap mode; see _traceback_equality_scored."""
    ancG = np.asarray(parentG, dtype=np.int64) + 1
    ancH = np.asarray(parentH, dtype=np.int64) + 1
    offG = np.asarray(offG, dtype=np.int64)
    flatG = np.asarray(flatG, dtype=np.int64)
    offH = np.asarray(offH, dtype=np.int64)
    flatH = np.asarray(flatH, dtype=np.int64)
    weight_by_id = np.asarray(weight_by_id, dtype=np.float32)

    path_rev: List[Tuple[int, int]] = []
    U, V = int(U_star), int(V_star)
    while U != 0 and V != 0:
        choice = int(C[U, V])
        if choice == 3:
            u = U - 1
            v = V - 1
            w_uv = _score_overlap_vertex_pair_py(offG, flatG, u, offH, flatH, v, weight_by_id)
            if keep_zero_weight_matches or w_uv > 0.0:
                path_rev.append((u, v))

        if choice == 1:
            U = int(ancG[U - 1])
        elif choice == 2:
            V = int(ancH[V - 1])
        elif choice == 3:
            U = int(ancG[U - 1])
            V = int(ancH[V - 1])
        else:
            raise RuntimeError(f"Invalid traceback state C[{U},{V}]={choice}")

    path_rev.reverse()
    return path_rev


def _validate_weight_by_id(weight_by_id: np.ndarray, max_token_id: int) -> np.ndarray:
    arr = np.asarray(weight_by_id, dtype=np.float32)
    if arr.ndim != 1:
        raise ValueError("weight_by_id must be a one-dimensional array")
    if max_token_id >= int(arr.shape[0]):
        raise ValueError(
            f"Encoded tree contains token id {max_token_id}, but weight_by_id has length {arr.shape[0]}. "
            "Use the same fitted FastLabelEncoder for both encoded trees and weights."
        )
    return arr


def align_trees_fast_encoded(
    G: EncodedTree,
    H: EncodedTree,
    *,
    weight_by_id: np.ndarray,
    return_matrices: bool = False,
    keep_zero_weight_matches: bool = False,
) -> FastAlignmentResult:
    if isinstance(G, EncodedTreeEquality) and isinstance(H, EncodedTreeEquality):
        max_id = -1
        if G.label_ids.size:
            max_id = max(max_id, int(np.max(G.label_ids)))
        if H.label_ids.size:
            max_id = max(max_id, int(np.max(H.label_ids)))
        weight_arr = _validate_weight_by_id(weight_by_id, max_id)
        A, C, U_star, V_star, score = _dp_equality_numba(
            np.asarray(G.tree.parent, dtype=np.int32),
            np.asarray(G.label_ids, dtype=np.int32),
            np.asarray(H.tree.parent, dtype=np.int32),
            np.asarray(H.label_ids, dtype=np.int32),
            weight_arr,
        )
        path = _traceback_equality_scored(
            G.tree.parent,
            G.label_ids,
            H.tree.parent,
            H.label_ids,
            weight_arr,
            C,
            U_star,
            V_star,
            keep_zero_weight_matches=keep_zero_weight_matches,
        )
        if return_matrices:
            return FastAlignmentResult(path_internal=path, score=float(score), end_internal=(U_star - 1, V_star - 1), A=A, C=C)
        return FastAlignmentResult(path_internal=path, score=float(score), end_internal=(U_star - 1, V_star - 1))

    if isinstance(G, EncodedTreeOverlap) and isinstance(H, EncodedTreeOverlap):
        max_id = -1
        if G.flat_token_ids.size:
            max_id = max(max_id, int(np.max(G.flat_token_ids)))
        if H.flat_token_ids.size:
            max_id = max(max_id, int(np.max(H.flat_token_ids)))
        weight_arr = _validate_weight_by_id(weight_by_id, max_id)
        A, C, U_star, V_star, score = _dp_overlap_numba(
            np.asarray(G.tree.parent, dtype=np.int32),
            np.asarray(G.offsets, dtype=np.int32),
            np.asarray(G.flat_token_ids, dtype=np.int32),
            np.asarray(H.tree.parent, dtype=np.int32),
            np.asarray(H.offsets, dtype=np.int32),
            np.asarray(H.flat_token_ids, dtype=np.int32),
            weight_arr,
        )
        path = _traceback_overlap_scored(
            G.tree.parent,
            G.offsets,
            G.flat_token_ids,
            H.tree.parent,
            H.offsets,
            H.flat_token_ids,
            weight_arr,
            C,
            U_star,
            V_star,
            keep_zero_weight_matches=keep_zero_weight_matches,
        )
        if return_matrices:
            return FastAlignmentResult(path_internal=path, score=float(score), end_internal=(U_star - 1, V_star - 1), A=A, C=C)
        return FastAlignmentResult(path_internal=path, score=float(score), end_internal=(U_star - 1, V_star - 1))

    raise TypeError("Encoded tree types do not match. Use equality+equality or overlap+overlap.")


class FastTreePathMatcher:
    """
    Specialized exact matcher for equality / any-overlap weights.

    Parameters
    ----------
    mode:
        "equality" or "overlap".
    label_getter:
        Optional extractor for the label field to match on.
    token_weights:
        Optional mapping token -> match score.
    default_weight:
        Default token score when a matched token is not in token_weights.
    phi_name, order, ts_field, strict_tree:
        Passed through when converting igraph -> TreeData.
    encoder:
        Optional pre-built FastLabelEncoder. Useful when one encoder is shared across a dataset.
    keep_zero_weight_matches:
        If True, return every diagonal traceback transition, including zero-score
        transitions selected only by tie-breaking. The default False returns only
        pairs with strictly positive contribution, which is usually what callers
        mean by "matched vertices".

    Typical high-throughput workflow
    --------------------------------
    >>> fm = FastTreePathMatcher(mode="equality")
    >>> fm.fit_encoder(list_of_graphs_or_trees)
    >>> enc = [fm.encode_tree(T) for T in list_of_graphs_or_trees]
    >>> path, score = fm.predict_encoded(enc[i], enc[j])
    """

    def __init__(
        self,
        *,
        mode: str = "equality",
        label_getter: LabelGetter = None,
        token_weights: Optional[Mapping[Any, float]] = None,
        default_weight: float = 1.0,
        phi_name: str = "label",
        order: str = "auto",
        ts_field: Optional[str] = None,
        strict_tree: bool = True,
        encoder: Optional[FastLabelEncoder] = None,
        keep_zero_weight_matches: bool = False,
    ) -> None:
        self.mode = mode.lower().strip()
        if self.mode not in {"equality", "overlap"}:
            raise ValueError("mode must be 'equality' or 'overlap'")
        self.label_getter = label_getter
        self.token_weights = dict(token_weights or {})
        self.default_weight = float(default_weight)
        self.phi_name = phi_name
        self.order = order
        self.ts_field = ts_field
        self.strict_tree = strict_tree
        self.keep_zero_weight_matches = bool(keep_zero_weight_matches)
        if encoder is not None and encoder.mode != self.mode:
            raise ValueError(f"encoder.mode={encoder.mode!r} does not match matcher mode={self.mode!r}")
        self.encoder = encoder or FastLabelEncoder(
            mode=self.mode,
            label_getter=self.label_getter,
            token_weights=self.token_weights,
            default_weight=self.default_weight,
        )
        self.treeG_: Optional[TreeData] = None
        self.treeH_: Optional[TreeData] = None
        self.encG_: Optional[EncodedTree] = None
        self.encH_: Optional[EncodedTree] = None

    def _to_tree(self, G: Any) -> TreeData:
        return _as_treedata(
            G,
            phi_name=self.phi_name,
            order=self.order,
            ts_field=self.ts_field,
            strict_tree=self.strict_tree,
        )

    def fit_encoder(self, trees: Sequence[Any]) -> "FastTreePathMatcher":
        td_trees = [self._to_tree(T) for T in trees]
        self.encoder.fit_from_trees(td_trees)
        return self

    def encode_tree(self, G: Any) -> EncodedTree:
        tree = self._to_tree(G)
        if not self.encoder.is_fitted:
            self.encoder.fit_from_trees([tree])
        return self.encoder.transform_tree(tree)

    def fit(self, G: Any, H: Any) -> "FastTreePathMatcher":
        treeG = self._to_tree(G)
        treeH = self._to_tree(H)
        self.treeG_ = treeG
        self.treeH_ = treeH
        if not self.encoder.is_fitted:
            self.encoder.fit_from_trees([treeG, treeH])
        self.encG_ = self.encoder.transform_tree(treeG)
        self.encH_ = self.encoder.transform_tree(treeH)
        return self

    def predict(self, G: Any = None, H: Any = None) -> Tuple[List[Tuple[int, int]], float]:
        if G is not None or H is not None:
            if G is None or H is None:
                raise ValueError("Either provide both G and H, or provide neither.")
            treeG = self._to_tree(G)
            treeH = self._to_tree(H)
            if not self.encoder.is_fitted:
                self.encoder.fit_from_trees([treeG, treeH])
            encG = self.encoder.transform_tree(treeG)
            encH = self.encoder.transform_tree(treeH)
        else:
            if self.encG_ is None or self.encH_ is None:
                raise RuntimeError("Must call fit(G,H) before predict() if no inputs are provided.")
            treeG = self.treeG_  # type: ignore[assignment]
            treeH = self.treeH_  # type: ignore[assignment]
            encG = self.encG_
            encH = self.encH_

        res = align_trees_fast_encoded(
            encG,
            encH,
            weight_by_id=self.encoder.weight_by_id,  # type: ignore[arg-type]
            keep_zero_weight_matches=self.keep_zero_weight_matches,
        )
        path_orig = [
            (int(treeG.orig_index[u]), int(treeH.orig_index[v]))  # type: ignore[union-attr]
            for (u, v) in res.path_internal
        ]
        return path_orig, res.score

    def predict_encoded(self, G: EncodedTree, H: EncodedTree) -> Tuple[List[Tuple[int, int]], float]:
        res = align_trees_fast_encoded(
            G,
            H,
            weight_by_id=self.encoder.weight_by_id,  # type: ignore[arg-type]
            keep_zero_weight_matches=self.keep_zero_weight_matches,
        )
        path_orig = [
            (int(G.tree.orig_index[u]), int(H.tree.orig_index[v]))
            for (u, v) in res.path_internal
        ]
        return path_orig, res.score


__all__ = [
    "HAVE_NUMBA",
    "FastAlignmentResult",
    "EncodedTreeEquality",
    "EncodedTreeOverlap",
    "FastLabelEncoder",
    "FastTreePathMatcher",
    "align_trees_fast_encoded",
]
