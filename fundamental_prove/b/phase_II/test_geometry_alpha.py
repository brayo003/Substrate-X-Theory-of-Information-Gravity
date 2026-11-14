"""
Test: Derive α=1.254 from minimal bit-cost geometry
"""

import numpy as np
import networkx as nx
from scipy import stats

def main():
    print("PHASE II: FORCE α FROM GEOMETRY")
    print("=" * 60)
    
    print("Simulating scale-free graph with saturation penalties...")
    
    # Create a scale-free graph
    n_nodes = 500
    G = nx.barabasi_albert_graph(n_nodes, 3)
    
    # Assign information densities
    np.random.seed(42)
    I_values = np.random.uniform(0, 1.4, n_nodes)
    
    # Cost function that increases near saturation
    def cost(I, bound=1.5):
        distance = bound - abs(I)
        return 1.0 / (distance + 0.1)
    
    C_values = np.array([cost(I) for I in I_values])
    
    # Compute relational distances
    print("Computing relational distances...")
    
    # Sample nodes for distance computation
    sample_nodes = min(100, n_nodes)
    nodes = list(G.nodes())[:sample_nodes]
    
    # Simple distance computation
    from collections import defaultdict
    distances = []
    
    for i in nodes:
        # BFS with cost-weighted edges
        visited = {i: 0}
        queue = [i]
        
        while queue:
            current = queue.pop(0)
            current_dist = visited[current]
            
            for neighbor in G.neighbors(current):
                new_dist = current_dist + (C_values[current] + C_values[neighbor])/2
                if neighbor not in visited or new_dist < visited[neighbor]:
                    visited[neighbor] = new_dist
                    if neighbor in nodes and neighbor != i:
                        distances.append(new_dist)
                    queue.append(neighbor)
    
    if not distances:
        print("No distances computed")
        return False
    
    # Estimate Hausdorff dimension
    distances = np.array(distances)
    distances = distances[distances > 0]
    
    # Bin distances
    max_dist = np.max(distances)
    bins = np.logspace(np.log10(0.1), np.log10(max_dist), 15)
    
    # Count nodes within radius R
    R_values = bins[1:]
    N_counts = []
    
    for R in R_values:
        count = np.sum(distances <= R)
        if count > 0:
            N_counts.append(count)
        else:
            N_counts.append(1)
    
    # Fit power law
    mask = (np.array(N_counts) > 10) & (R_values > 0)
    if np.sum(mask) < 3:
        print("Insufficient data for fitting")
        return False
    
    R_fit = R_values[mask]
    N_fit = np.array(N_counts)[mask]
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        np.log(R_fit), np.log(N_fit)
    )
    
    DH = slope
    print(f"\nEstimated Hausdorff dimension: DH = {DH:.4f}")
    print(f"Target α = 1.254")
    print(f"Difference: {abs(DH - 1.254):.4f}")
    print(f"R² = {r_value**2:.4f}")
    
    print("\n" + "=" * 60)
    if abs(DH - 1.254) < 0.2:
        print("✓ SUCCESS: DH ≈ 1.254 emerges without tuning")
        return True
    else:
        print("✗ FAILURE: DH ≠ 1.254")
        return False

if __name__ == "__main__":
    main()
