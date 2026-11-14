import numpy as np
import networkx as nx
from engine_core import get_bit_cost

def run_metric_test():
    # 1. Create a 3D Geometric Graph (Substrate Proxy)
    n_nodes = 1200
    # Higher radius ensures connectivity for valid Hausdorff measurement
    G = nx.random_geometric_graph(n_nodes, 0.18, dim=3)
    
    # 2. Apply Saturation costs from the V12 attractor
    for node in G.nodes():
        # High density bias to test the fractal "congestion" limit
        val = np.random.uniform(1.3, 1.49) 
        G.nodes[node]['cost'] = get_bit_cost(val)

    # 3. Compute distances via Bit-Cost Geodesics
    # Pick a central node to avoid boundary effects
    source = n_nodes // 2
    try:
        path_lengths = nx.single_source_dijkstra_path_length(G, source, weight='cost')
        radii = np.sort(list(path_lengths.values()))
        
        # Filter: Ignore the immediate neighbors and the extreme outliers
        valid = (radii > np.percentile(radii, 5)) & (radii < np.percentile(radii, 85))
        r_vals = radii[valid]
        n_vals = np.arange(1, len(r_vals) + 1)
        
        # 4. Extract Alpha (Hausdorff Dimension)
        log_r = np.log(r_vals)
        log_n = np.log(n_vals)
        alpha_fit = np.polyfit(log_r, log_n, 1)[0]
        
        print(f"Emergent Hausdorff Dimension (Alpha): {alpha_fit:.4f}")
        if 1.1 < alpha_fit < 1.4:
            print("PHASE II RESULT: Substrate geometry scales within fractal range.")
        else:
            print("PHASE II DEVIATION: Scaling deviates from predicted 1.254 limit.")
    except Exception as e:
        print(f"PHASE II FAILED: {e}")

if __name__ == "__main__":
    run_metric_test()
