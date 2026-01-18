import numpy as np
import networkx as nx
import scipy.sparse as sp
import scipy.sparse.linalg as spl

def run_precision_search():
    print("REFINING SUBSTRATE OPERATING POINT...")
    data = []
    L_dim = 12  # Increased resolution
    total_nodes = L_dim**3
    adj_base = nx.grid_graph(dim=[L_dim, L_dim, L_dim])
    edges_base = list(adj_base.edges())

    # High-density sampling around the suspected peak
    for density in np.linspace(0.20, 0.40, 100):
        try:
            num_keep = int(len(edges_base) * density)
            keep_idx = np.random.choice(len(edges_base), num_keep, replace=False)
            G = nx.Graph()
            G.add_nodes_from(adj_base.nodes())
            G.add_edges_from([edges_base[i] for i in keep_idx])
            
            A = nx.adjacency_matrix(G).tocsr().astype(float)
            D_vec = np.array(A.sum(axis=1)).flatten()
            D_inv = sp.diags(1.0 / np.where(D_vec == 0, 1, D_vec))
            L = sp.eye(total_nodes) - D_inv.dot(A)
            
            vals = spl.eigsh(L, k=40, which='SM', return_eigenvectors=False)
            vals = np.sort(vals[vals > 1e-7])
            slope = np.polyfit(np.log(vals), np.log(np.arange(1, len(vals)+1)), 1)[0]
            alpha = slope * 2
            
            # Objective: Maximize transport (alpha) while minimizing density (cost)
            efficiency = alpha / (density + 0.1) 
            data.append((density, alpha, efficiency))
        except: continue

    best = sorted(data, key=lambda x: x[2], reverse=True)[0]
    print(f"Optimal Density: {best[0]:.4f}")
    print(f"Resulting Alpha: {best[1]:.4f}")
    print(f"Peak Efficiency: {best[2]:.4f}")

if __name__ == "__main__":
    run_precision_search()
