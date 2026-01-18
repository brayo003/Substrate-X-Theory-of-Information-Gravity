"""
STABLE RG FIXED POINT TEST
Objective: Test if α=1.254 is an RG fixed point for information-conserving substrates
"""

import numpy as np
import networkx as nx
from scipy import stats

class InformationConservingSubstrate:
    """Substrate that conserves total information during coarse-graining"""
    
    def __init__(self, n_nodes=256, initial_alpha=1.254):
        self.n = n_nodes
        self.alpha = initial_alpha
        
        # Create substrate with information conservation
        self.I = np.random.uniform(0, 1.0, n_nodes)  # Information densities
        self.total_I = np.sum(self.I)
        
        # Create connections based on information similarity
        self.create_connections()
    
    def create_connections(self):
        """Create graph where edges conserve local information flow"""
        G = nx.Graph()
        G.add_nodes_from(range(self.n))
        
        # Connect nodes with similar information density
        for i in range(self.n):
            for j in range(i+1, min(i+10, self.n)):
                # Probability of connection based on information similarity
                p = np.exp(-abs(self.I[i] - self.I[j]) / 0.1)
                if np.random.random() < p:
                    G.add_edge(i, j, weight=1.0/(abs(self.I[i] - self.I[j]) + 0.01))
        
        self.G = G
        return G
    
    def measure_alpha(self):
        """Measure α from information scaling"""
        # Measure how information scales with "volume"
        radii = np.linspace(0.1, 1.0, 10)
        I_within_r = []
        
        for r in radii:
            # For each node, count information within radius r
            total = 0
            for i in range(min(20, self.n)):  # Sample nodes
                # BFS to find nodes within effective radius
                visited = {i}
                queue = [(i, 0)]
                local_I = self.I[i]
                
                while queue:
                    node, dist = queue.pop(0)
                    if dist > r:
                        continue
                    
                    for neighbor in self.G.neighbors(node):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            weight = self.G.edges[node, neighbor]['weight']
                            effective_dist = dist + 1.0/weight
                            if effective_dist <= r:
                                local_I += self.I[neighbor]
                                queue.append((neighbor, effective_dist))
                
                total += local_I
            
            I_within_r.append(total / min(20, self.n))
        
        # Fit scaling: I(R) ∝ R^α
        if len(radii) >= 3:
            log_R = np.log(radii + 1e-10)
            log_I = np.log(np.array(I_within_r) + 1e-10)
            slope, intercept, r_value, p_value, std_err = stats.linregress(log_R, log_I)
            return slope, r_value**2
        return None, 0
    
    def coarse_grain_conserving(self):
        """Coarse-grain while conserving total information"""
        # Group nodes into blocks of 4
        new_n = self.n // 4
        if new_n < 16:
            return False  # Too small to continue
        
        new_I = np.zeros(new_n)
        new_G = nx.Graph()
        new_G.add_nodes_from(range(new_n))
        
        # Create new nodes by merging old ones, conserving information
        for block in range(new_n):
            indices = range(block*4, min((block+1)*4, self.n))
            new_I[block] = np.sum(self.I[indices])  # Information conserved
        
        # Renormalize to keep average information constant
        old_avg = np.mean(self.I[:new_n*4])
        new_avg = np.mean(new_I)
        if new_avg > 0:
            new_I = new_I * (old_avg / new_avg)
        
        # Update substrate
        self.n = new_n
        self.I = new_I
        self.total_I = np.sum(self.I)
        self.create_connections()
        
        return True
    
    def rg_flow(self, steps=6):
        """Run RG flow and track α"""
        alphas = []
        r_squared = []
        
        for step in range(steps):
            alpha, r2 = self.measure_alpha()
            if alpha is not None:
                alphas.append(alpha)
                r_squared.append(r2)
                print(f"  RG step {step}: α = {alpha:.4f} (R² = {r2:.4f})")
            
            if not self.coarse_grain_conserving():
                break
        
        return alphas, r_squared

def test_multiple_trajectories(n_trajectories=5):
    """Test multiple independent RG flows"""
    print("STABLE RENORMALIZATION GROUP FLOW TEST")
    print("Testing if α=1.254 is a fixed point for information-conserving substrates")
    print("=" * 70)
    
    all_alphas = []
    
    for traj in range(n_trajectories):
        print(f"\nTrajectory {traj+1}")
        
        # Start near 1.254
        initial_alpha = 1.254 + np.random.uniform(-0.2, 0.2)
        substrate = InformationConservingSubstrate(n_nodes=256, initial_alpha=initial_alpha)
        
        alphas, r2s = substrate.rg_flow(steps=6)
        all_alphas.append(alphas)
        
        if len(alphas) >= 2:
            # Check convergence
            initial = alphas[0]
            final = alphas[-1]
            diff = abs(final - 1.254)
            print(f"  Initial: {initial:.4f}, Final: {final:.4f}, |Δ-1.254| = {diff:.4f}")
    
    # Analyze fixed point behavior
    print(f"\n" + "=" * 70)
    print("FIXED POINT ANALYSIS:")
    
    if all_alphas:
        # Get final α values
        final_alphas = [alphas[-1] for alphas in all_alphas if alphas]
        if final_alphas:
            mean_alpha = np.mean(final_alphas)
            std_alpha = np.std(final_alphas)
            
            print(f"Mean final α: {mean_alpha:.4f} ± {std_alpha:.4f}")
            print(f"Target fixed point: 1.254")
            print(f"Distance: {abs(mean_alpha - 1.254):.4f}")
            
            # Test if it's a fixed point
            is_fixed = (abs(mean_alpha - 1.254) < 0.1) and (std_alpha < 0.2)
            
            if is_fixed:
                print("\n✓ α = 1.254 IS AN RG FIXED POINT")
                print("  Information-conserving substrate flows to α ≈ 1.254")
                return True
            else:
                print(f"\n✗ α = 1.254 IS NOT AN RG FIXED POINT")
                print(f"  Substrate flows to α ≈ {mean_alpha:.4f}")
                return False
    
    return None

def test_without_conservation():
    """Test what happens without information conservation"""
    print("\n" + "=" * 70)
    print("CONTROL TEST: RG flow WITHOUT information conservation")
    print("=" * 70)
    
    # Simple random graph without conservation
    n = 256
    G = nx.erdos_renyi_graph(n, 0.1)
    
    # Random information values (not conserved)
    I = np.random.uniform(0, 2.0, n)
    
    alphas = []
    for step in range(5):
        # Crude α estimation from degree distribution
        degrees = [d for _, d in G.degree()]
        if len(degrees) >= 10:
            # Estimate α from degree distribution scaling
            hist, bins = np.histogram(degrees, bins=10)
            centers = (bins[:-1] + bins[1:]) / 2
            mask = (hist > 0) & (centers > 0)
            if np.sum(mask) >= 3:
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    np.log(centers[mask]), np.log(hist[mask])
                )
                alpha = -slope  # Rough estimate
                alphas.append(alpha)
                print(f"  Step {step}: α = {alpha:.4f}")
        
        # Random coarse-graining (not conserving)
        if len(G) > 32:
            # Merge random pairs
            nodes = list(G.nodes())
            np.random.shuffle(nodes)
            mapping = {}
            for i in range(0, len(nodes)-1, 2):
                mapping[nodes[i+1]] = nodes[i]
            G = nx.contracted_nodes(G, nodes[i], nodes[i+1])
    
    if alphas:
        print(f"\nFinal α without conservation: {alphas[-1]:.4f}")
        print("Expected: Unstable, non-convergent")

def main():
    """Main test"""
    print("=" * 70)
    print("RENORMALIZATION GROUP FIXED POINT TEST FOR α=1.254")
    print("=" * 70)
    
    # Test with information conservation
    is_fixed_point = test_multiple_trajectories(n_trajectories=5)
    
    # Control test
    test_without_conservation()
    
    print("\n" + "=" * 70)
    print("INTERPRETATION:")
    
    if is_fixed_point is True:
        print("✓ α = 1.254 IS A STABLE RG FIXED POINT")
        print("  This means:")
        print("  1. The exponent is universal (independent of microscopic details)")
        print("  2. It emerges from information-conserving dynamics")
        print("  3. It's not just a fitted parameter")
        print("\n  This would be a MAJOR discovery: α is forced by symmetry")
        print("  (information conservation → α = 1.254 fixed point)")
        
    elif is_fixed_point is False:
        print("✗ α = 1.254 IS NOT AN RG FIXED POINT")
        print("  This means:")
        print("  1. The exponent may be system-dependent")
        print("  2. It's not universally forced by information conservation")
        print("  3. It remains a phenomenological parameter")
        print("\n  The search continues for what forces α = 1.254")
        
    else:
        print("? Test inconclusive")
        print("  Need more sophisticated RG scheme or larger systems")
    
    print("\nKey insight: If α IS a fixed point, it's FUNDAMENTAL.")
    print("If not, it's PHENOMENOLOGICAL.")
    print("=" * 70)
    
    return is_fixed_point

if __name__ == "__main__":
    main()
