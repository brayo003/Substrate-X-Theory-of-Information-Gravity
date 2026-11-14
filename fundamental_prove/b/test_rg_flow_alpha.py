import networkx as nx
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

def spectral_alpha(G, k=100):
    A = nx.adjacency_matrix(G).astype(float)
    D = np.array(A.sum(axis=1)).flatten()
    Dinv = sp.diags(1.0 / np.where(D == 0, 1, D))
    L = sp.eye(G.number_of_nodes()) - Dinv @ A
    vals = spl.eigsh(L, k=min(k, G.number_of_nodes()-2), which='SM', return_eigenvectors=False)
    vals = np.sort(vals[vals > 1e-8])
    slope = np.polyfit(np.log(vals), np.log(np.arange(1, len(vals)+1)), 1)[0]
    return slope * 2

def coarse_grain(G):
    H = nx.Graph()
    nodes = list(G.nodes())
    np.random.shuffle(nodes)
    for i in range(0, len(nodes)-1, 2):
        H.add_node(i//2)
        if G.has_edge(nodes[i], nodes[i+1]):
            H.add_edge(i//2, i//2)
    return H

G = nx.random_geometric_graph(2000, radius=0.05)
for step in range(5):
    alpha = spectral_alpha(G)
    print(f"RG step {step}: α = {alpha:.4f}")
    G = coarse_grain(G)
