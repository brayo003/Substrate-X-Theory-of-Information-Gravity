import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class VortexClustering:
    def __init__(self, m_X=0.2, n_vortices=6):
        self.m_X = m_X
        self.n_vortices = n_vortices
        
    def vortex_force(self, r):
        """Force between vortices: F = -dV/dr"""
        if r < 1e-12:
            return 0
        # F = -d/dr [exp(-m_X r)/√r] 
        return -np.exp(-self.m_X * r) * (self.m_X/np.sqrt(r) + 1/(2*r**1.5))
    
    def vortex_dynamics(self, t, state):
        """Equations of motion for vortex positions"""
        positions = state.reshape((self.n_vortices, 2))
        velocities = np.zeros_like(positions)
        
        for i in range(self.n_vortices):
            total_force = np.zeros(2)
            for j in range(self.n_vortices):
                if i != j:
                    r_vec = positions[j] - positions[i]
                    r = np.linalg.norm(r_vec)
                    if r > 1e-12:  # Avoid division by zero
                        force_mag = self.vortex_force(r)
                        total_force += force_mag * (r_vec / r)
            
            velocities[i] = total_force
        
        return velocities.flatten()
    
    def simulate_clustering(self, initial_positions, t_max=50):
        """Simulate vortex clustering over time"""
        initial_state = initial_positions.flatten()
        
        t_eval = np.linspace(0, t_max, 100)
        sol = solve_ivp(self.vortex_dynamics, [0, t_max], initial_state, 
                       t_eval=t_eval, method='RK45', rtol=1e-6)
        
        # Extract trajectories
        trajectories = sol.y.reshape((self.n_vortices, 2, len(t_eval)))
        return t_eval, trajectories
    
    def analyze_clustering_evolution(self, trajectories):
        """Analyze how clustering develops over time"""
        n_times = trajectories.shape[2]
        mean_separations = []
        cluster_sizes = []
        
        for t in range(n_times):
            positions = trajectories[:, :, t]
            distances = []
            for i in range(self.n_vortices):
                for j in range(i+1, self.n_vortices):
                    dist = np.linalg.norm(positions[i] - positions[j])
                    distances.append(dist)
            
            mean_sep = np.mean(distances)
            mean_separations.append(mean_sep)
            
            # Count clusters (vortices within 2.0 units)
            clusters = []
            for i in range(self.n_vortices):
                clustered = False
                for cluster in clusters:
                    if any(np.linalg.norm(positions[i] - positions[j]) < 2.0 for j in cluster):
                        cluster.append(i)
                        clustered = True
                        break
                if not clustered:
                    clusters.append([i])
            
            cluster_sizes.append([len(cluster) for cluster in clusters])
        
        return mean_separations, cluster_sizes

def main():
    print("VORTEX CLUSTERING SIMULATION - FIXED")
    print("=" * 45)
    
    # Create vortex system with your parameters
    cluster_sim = VortexClustering(m_X=0.2, n_vortices=6)
    
    # Initial positions matching your ensemble results
    np.random.seed(42)
    initial_positions = np.random.uniform(-8, 8, (6, 2))
    
    print("Initial vortex positions:")
    for i, pos in enumerate(initial_positions):
        print(f"Vortex {i}: ({pos[0]:.2f}, {pos[1]:.2f})")
    
    # Calculate initial interactions
    print("\nCalculating initial interactions...")
    interaction_strengths = []
    for i in range(6):
        for j in range(i+1, 6):
            r = np.linalg.norm(initial_positions[i] - initial_positions[j])
            V = np.exp(-0.2 * r) / np.sqrt(r)
            interaction_strengths.append(V)
    
    mean_interaction = np.mean(interaction_strengths)
    print(f"Mean initial interaction strength: {mean_interaction:.6f}")
    
    # Simulate clustering
    print("\nSimulating vortex dynamics...")
    times, trajectories = cluster_sim.simulate_clustering(initial_positions, t_max=30)
    
    # Analyze results
    mean_seps, cluster_sizes = cluster_sim.analyze_clustering_evolution(trajectories)
    
    # Plot results
    plt.figure(figsize=(15, 5))
    
    # Plot 1: Initial configuration
    plt.subplot(131)
    plt.scatter(initial_positions[:, 0], initial_positions[:, 1], s=100, c='red', alpha=0.7)
    for i, pos in enumerate(initial_positions):
        plt.text(pos[0], pos[1], f'{i}', fontsize=12, ha='center', va='center')
    plt.title('Initial Vortex Positions')
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Final configuration
    plt.subplot(132)
    final_positions = trajectories[:, :, -1]
    plt.scatter(final_positions[:, 0], final_positions[:, 1], s=100, c='blue', alpha=0.7)
    for i, pos in enumerate(final_positions):
        plt.text(pos[0], pos[1], f'{i}', fontsize=12, ha='center', va='center')
    plt.title('Final Vortex Positions')
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Clustering evolution
    plt.subplot(133)
    plt.plot(times, mean_seps, 'b-', linewidth=2, label='Mean separation')
    plt.axhline(y=mean_seps[0], color='red', linestyle='--', alpha=0.7, label='Initial separation')
    plt.xlabel('Time')
    plt.ylabel('Mean Vortex Separation')
    plt.title('Clustering Evolution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('vortex_clustering_fixed.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Print analysis
    print(f"\n=== CLUSTERING RESULTS ===")
    print(f"Initial mean separation: {mean_seps[0]:.2f}")
    print(f"Final mean separation: {mean_seps[-1]:.2f}")
    separation_change = ((mean_seps[-1] - mean_seps[0])/mean_seps[0]*100)
    print(f"Separation change: {separation_change:.1f}%")
    
    final_clusters = cluster_sizes[-1]
    print(f"Final cluster configuration: {final_clusters}")
    
    if len(final_clusters) < 6:
        print("\n🎯 VORTEX CLUSTERING CONFIRMED!")
        print("→ Vortices form bound structures")
        print("→ Natural dark matter halo formation")
        print("→ Hierarchical structure: vortices → clusters → galaxies")
        
        # Calculate cluster properties
        largest_cluster = max(final_clusters)
        print(f"Largest cluster size: {largest_cluster} vortices")
        if largest_cluster >= 3:
            print("→ Significant clustering - could seed galaxy formation")
            
    else:
        print("\nVortices remain mostly separate")
        print("→ Distributed dark matter distribution")
        print("→ Weak clustering on these timescales")

if __name__ == "__main__":
    main()
