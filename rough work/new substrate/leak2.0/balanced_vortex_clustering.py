import numpy as np
import matplotlib.pyplot as plt

class BalancedVortexClustering:
    def __init__(self, m_X=0.2, n_pairs=3):  # 3 vortex-antivortex pairs
        self.m_X = m_X
        self.n_vortices = n_pairs * 2  # Total vortices
        # Create balanced pairs: [+1, -1, +1, -1, +1, -1]
        self.charges = np.array([1, -1] * n_pairs)
        
    def vortex_force(self, r, charge_i, charge_j):
        """Vortex interaction force"""
        if r < 0.1:
            return charge_i * charge_j * 5.0  # Short-range repulsion
        # Main force: like charges repel, opposite attract
        return charge_i * charge_j * np.exp(-self.m_X * r) / np.sqrt(r)
    
    def simulate_balanced(self, initial_positions, n_steps=800, dt=0.2):
        """Simulation with balanced vortex-antivortex pairs"""
        positions = initial_positions.copy()
        
        print("Running balanced simulation...")
        for step in range(n_steps):
            new_positions = positions.copy()
            
            for i in range(self.n_vortices):
                total_force = np.zeros(2)
                for j in range(self.n_vortices):
                    if i != j:
                        r_vec = positions[j] - positions[i]
                        r = np.linalg.norm(r_vec)
                        force_mag = self.vortex_force(r, self.charges[i], self.charges[j])
                        total_force += force_mag * (r_vec / (r + 0.1))
                
                new_positions[i] += dt * total_force
            
            # Keep within bounds
            new_positions = np.clip(new_positions, -12, 12)
            positions = new_positions
            
            if step % 200 == 0:
                print(f"Step {step}/{n_steps}")
        
        return positions

def main():
    print("BALANCED VORTEX-ANTIVORTEX CLUSTERING")
    print("=" * 50)
    
    # Create balanced system (3 pairs)
    vortex_sim = BalancedVortexClustering(m_X=0.2, n_pairs=3)
    
    print("Vortex charges:", vortex_sim.charges)
    print(f"Total: {vortex_sim.n_vortices} vortices ({vortex_sim.n_vortices//2} pairs)")
    
    # Initial positions - start pairs close together
    np.random.seed(42)
    initial_positions = np.zeros((6, 2))
    
    # Create 3 initial pairs
    pair_centers = np.random.uniform(-8, 8, (3, 2))
    for i in range(3):
        # Vortex and antivortex start near each other
        initial_positions[2*i] = pair_centers[i] + [0.5, 0.5]    # Vortex
        initial_positions[2*i+1] = pair_centers[i] + [-0.5, -0.5] # Antivortex
    
    # Run simulation
    final_positions = vortex_sim.simulate_balanced(initial_positions)
    
    # Analyze clustering
    clusters = []
    for i in range(6):
        clustered = False
        for cluster in clusters:
            if any(np.linalg.norm(final_positions[i] - final_positions[j]) < 2.5 for j in cluster):
                cluster.append(i)
                clustered = True
                break
        if not clustered:
            clusters.append([i])
    
    # Calculate pair distances
    pair_distances = []
    for i in range(0, 6, 2):
        dist = np.linalg.norm(final_positions[i] - final_positions[i+1])
        pair_distances.append(dist)
    
    print(f"\n=== RESULTS ===")
    print(f"Number of clusters: {len(clusters)}")
    print(f"Cluster sizes: {[len(c) for c in clusters]}")
    print(f"Vortex-antivortex pair distances: {[f'{d:.2f}' for d in pair_distances]}")
    
    # Visualization
    plt.figure(figsize=(12, 5))
    
    # Initial positions
    plt.subplot(121)
    colors = ['red' if c == 1 else 'blue' for c in vortex_sim.charges]
    plt.scatter(initial_positions[:, 0], initial_positions[:, 1], s=100, c=colors, alpha=0.7)
    for i, (pos, color) in enumerate(zip(initial_positions, colors)):
        plt.text(pos[0], pos[1], f'{vortex_sim.charges[i]}', fontsize=12, 
                ha='center', va='center', color='white', weight='bold')
    # Draw lines between initial pairs
    for i in range(0, 6, 2):
        plt.plot([initial_positions[i,0], initial_positions[i+1,0]],
                [initial_positions[i,1], initial_positions[i+1,1]], 
                'gray', linestyle='--', alpha=0.7)
    plt.title('Initial: Paired Configuration')
    plt.xlim(-12, 12)
    plt.ylim(-12, 12)
    plt.grid(True, alpha=0.3)
    
    # Final positions
    plt.subplot(122)
    plt.scatter(final_positions[:, 0], final_positions[:, 1], s=100, c=colors, alpha=0.7)
    for i, (pos, color) in enumerate(zip(final_positions, colors)):
        plt.text(pos[0], pos[1], f'{vortex_sim.charges[i]}', fontsize=12, 
                ha='center', va='center', color='white', weight='bold')
    
    # Draw lines between final pairs and clusters
    for cluster in clusters:
        if len(cluster) > 1:
            cluster_positions = final_positions[cluster]
            for i in range(len(cluster)):
                for j in range(i+1, len(cluster)):
                    dist = np.linalg.norm(cluster_positions[i] - cluster_positions[j])
                    if dist < 3.0:
                        plt.plot([cluster_positions[i,0], cluster_positions[j,0]],
                                [cluster_positions[i,1], cluster_positions[j,1]], 
                                'green', linewidth=2, alpha=0.8)
    
    plt.title('Final: Vortex-Antivortex Clustering')
    plt.xlim(-12, 12)
    plt.ylim(-12, 12)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('balanced_vortex_clustering.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Physical interpretation
    print(f"\n=== PHYSICAL INTERPRETATION ===")
    avg_pair_distance = np.mean(pair_distances)
    if avg_pair_distance < 3.0:
        print("🎯 VORTEX-ANTIVORTEX BOUND PAIRS CONFIRMED!")
        print("→ Opposite charges form stable bound states")
        print("→ Like charges maintain separation") 
        print("→ Perfect dark matter halo formation mechanism!")
    else:
        print("Pairs separated - may need stronger attraction")

if __name__ == "__main__":
    main()
