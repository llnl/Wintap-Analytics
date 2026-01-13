import igraph as ig
import numpy as np

def id_match(a,b):
    """
    Simplest possible matcher: just check if the inputs are equal
    """
    return 1.0*(a==b)

def get_parent(graph, u):
    parents = graph.neighborhood(u, order=1, mode="in")
    if len(parents) == 1:
        return -1 
    else:
        return parents[1]

def validate_tree(G):
    n = G.vcount()

    roots = []
    for u in range(n):
        parents = G.neighborhood(u, order=1, mode="in")
        if len(parents) == 1:
            roots.append(u)
        elif len(parents) == 2:
            p = parents[1]
            if p >= u:
                raise ValueError(f"Invalid vertex ordering: parent {p} >= child {u}")
        else:
            raise ValueError(f"Node {u} has multiple parents")

    if len(roots) != 1:
        raise ValueError("Graph must have exactly one root")


def basic_matcher(G, H, phi_name="symbols", w=id_match):
    """
    Finds matching of labeled graphs G,H

    G,H: graphs
    phi_name: the fields in G,H to find the labels
    w: a function taking pairs of points, returning a score.
    """
    
    # Initialize...

    validate_tree(G)
    validate_tree(H)

    n = G.vcount()
    m = H.vcount()

    phiG = [G.vs[i][phi_name] for i in range(n)]
    phiH = [H.vs[i][phi_name] for i in range(m)]

    A = np.zeros((n, m))
    C = np.zeros((n, m))

    # Forward pass...
    for u in range(n):
        for v in range(m):
            up = get_parent(G, u)
            vp = get_parent(H, v)

            opts = [-np.inf, -np.inf, -np.inf]
            if up != -1:
                opts[0] = A[up][v]
            if vp != -1:
                opts[1] = A[u][vp]

            base = A[up][vp] if (up != -1 and vp != -1) else 0.0
            opts[2] = w(phiG[u], phiH[v]) + base

            k = np.argmax(opts)
            A[u][v] = opts[k]
            C[u][v] = k + 1

    # Backward pass...
    seq_G = []
    seq_H = []

    u,v = np.unravel_index(np.argmax(A),A.shape)

    while True:
        if (u == 0 and v ==0) or (u <0 and v >= 0) or (v < 0 and u >=0): # Note: This allows you to match root to non-root.
#        if u == 0 and v == 0:
            break
            
        if u < 0 or v < 0:
            raise RuntimeError("Traceback stepped outside tree bounds")

        choice = C[u][v]

        if choice == 3:
            seq_G.append(u)
            seq_H.append(v)
            u = get_parent(G, u)
            v = get_parent(H, v)
        elif choice == 1:
            u = get_parent(G, u)
        elif choice == 2:
            v = get_parent(H, v)
        else:
            raise RuntimeError("Invalid traceback state")

    if C[0][0] == 3:
        seq_G.append(0)
        seq_H.append(0)

    return list(zip(seq_G, seq_H)), np.max(A)
