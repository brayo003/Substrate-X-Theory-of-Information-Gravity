import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class VortexInteractionCorrected:
    def __init__(self, m_X=0.2, n_vortices=6):
        self.m_X = m_X
        self.n_vortices = n_vortices
        # Assign random charges (+1 for vortex, -1 for antivortex)
        self.charges = np.random.choice([-1, 1], size=n_vortices)
        
    def vortex_force(self, r, charge_i, charge_j):
        """Corrected force between vortices with charge dependence"""
        if r < 1e-12:
            return 0
        # Force magnitude: F ~ charge_i * charge_j * exp(-m_X r)/√r
        force_magnitude = charge_i * charge_j * np.exp(-self.m_X * r) / np.sqrt(r)
        return force_magnitude
    
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
                    if r > 1e-12:
                        force_mag = self.vortex_force(r, self.charges[i], self.charges[j])
                        total_force += force_mag * (r_vec / r)
            
            velocities[i] = total_force
        
        return velocities.flatten()
    
    def simulate_clustering(self, initial_positions, t_max=50):
        """Simulate vortex clustering with corrected interactions"""
        initial_state = initial_positions.flatten()
        
        t_eval = np.linspace(0, t_max, 100)
        sol = solve_ivp(self.vortex_dynamics, [0, t_max], initial_state, 
                       t_eval=t_eval, method='RK45', rtol=1e-6)
        
        trajectories = sol.y.reshape((self.n_vortices, 2, len(t_eval)))
        return t_eval, trajectories

def main():
    print("CORRECTED VORTEX INTERACTION SIMULATION")
    print("=" * 50)
    
    # Create system with mixed charges
    vortex_sim = VortexInteractionCorrected(m_X=0.2, n_vortices=6)
    
    print("Vortex charges:", vortex_sim.charges)
    print("Vortices (+1):", np.sum(vortex_sim.charges == 1))
    print("Antivortices (-1):", np.sum(vortex_sim.charges == -1))
    
    # Initial positions
    np.random.seed(42)
    initial_positions = np.random.uniform(-8, 8, (6, 2))
    
    # Simulate
    times, trajectories = vortex_sim.simulate_clustering(initial_positions, t_max=50)
    
    # Analyze results
    final_positions = trajectories[:, :, -1]
    
    # Calculate separations
    distances = []
    for i in range(6):
        for j in range(i+1, 6):
            dist = np.linalg.norm(final_positions[i] - final_positions[j])
            distances.append(dist)
    
    mean_separation = np.mean(distances)
    
    # Check clustering
    clusters = []
    for i in range(6):
        clustered = False
        for cluster in clusters:
            if any(np.linalg.norm(final_positions[i] - final_positions[j]) < 3.0 for j in cluster):
                cluster.append(i)
                clustered = True
                break
        if not clustered:
            clusters.append([i])
    
    print(f"\n=== RESULTS ===")
    print(f"Final mean separation: {mean_separation:.2f}")
    print(f"Cluster configuration: {[len(c) for c in clusters]}")
    
    if len(clusters) < 6:
        print("🎯 CLUSTERING DETECTED!")
        print("Vortex-antivortex pairs are attracting!")
    else:
        print("Still no clustering - need to check interaction potential")
    
    # Visualization
    plt.figure(figsize=(12, 5))
    
    plt.subplot(121)
    colors = ['red' if c == 1 else 'blue' for c in vortex_sim.charges]
    plt.scatter(initial_positions[:, 0], initial_positions[:, 1], s=100, c=colors, alpha=0.7)
    for i, (pos, color) in enumerate(zip(initial_positions, colors)):
        plt.text(pos[0], pos[1], f'{vortex_sim.charges[i]}', fontsize=12, 
                ha='center', va='center', color='white', weight='bold')
    plt.title('Initial: Red=+1, Blue=-1')
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.grid(True, alpha=0.3)
    
    plt.subplot(122)
    plt.scatter(final_positions[:, 0], final_positions[:, 1], s=100, c=colors, alpha=0.7)
    for i, (pos, color) in enumerate(zip(final_positions, colors)):
        plt.text(pos[0], pos[1], f'{vortex_sim.charges[i]}', fontsize=12, 
                ha='center', va='center', color='white', weight='bold')
    plt.title('Final Positions')
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('vortex_interaction_corrected.png', dpi=150, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
