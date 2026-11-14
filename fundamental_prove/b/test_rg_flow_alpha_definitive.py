import networkx as nx
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

def spectral_alpha(G, k=80, eps=1e-6):
    A = nx.adjacency_matrix(G).astype(float)
    D = np.array(A.sum(axis=1)).flatten()
    mask = D > 0
    A = A[mask][:, mask]
    D = D[mask]
    Dinv = sp.diags(1.0 / D)
    L = sp.eye(len(D)) - Dinv @ A
    L += eps * sp.eye(len(D))  # regularization to stabilize small eigenvalues

    vals = spl.eigsh(L, k=min(k, len(D)-2), which='SM', return_eigenvectors=False)
    vals = np.sort(vals[vals > 1e-8])

    x = np.log(vals)
    y = np.log(np.arange(1, len(vals)+1))
    slope = np.polyfit(x, y, 1)[0]
    return 2 * slope

def block_rg(G, block_size=3):
    G = nx.convert_node_labels_to_integers(G)
    H = nx.Graph()
    blocks = {}

    for n in G.nodes():
        blocks.setdefault(n // block_size, []).append(n)

    for b, nodes in blocks.items():
        H.add_node(b)
        for u in nodes:
            for v in G.neighbors(u):
                if v // block_size != b:
                    H.add_edge(b, v // block_size)

    return H

# use multiple RG trajectories
N_trajectories = 5
block_size = 3
steps = 6
for t in range(N_trajectories):
    G = nx.random_geometric_graph(2500, radius=0.045)
    print(f"Trajectory {t+1}")
    for step in range(steps):
        alpha = spectral_alpha(G)
        print(f"  RG step {step}: α = {alpha:.4f}")
        G = block_rg(G, block_size=block_size)
