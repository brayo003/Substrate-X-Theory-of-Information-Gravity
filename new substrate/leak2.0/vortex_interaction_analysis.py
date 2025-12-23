import numpy as np
import matplotlib.pyplot as plt

class VortexInteractionAnalyzer:
    def __init__(self, m_X=0.2):
        self.m_X = m_X
    
    def vortex_interaction_potential(self, r):
        """Vortex-vortex interaction from field theory"""
        # For m_X * r >> 1: V(r) ~ K₀(m_X * r) ~ exp(-m_X * r)/√r
        if r == 0:
            return 0
        return np.exp(-self.m_X * r) / np.sqrt(r + 1e-12)
    
    def analyze_vortex_interactions(self, vortex_positions):
        """Analyze interactions between vortices"""
        positions = np.array([(x, y) for x, y, _ in vortex_positions])
        
        if len(positions) < 2:
            print("Need at least 2 vortices for interaction analysis")
            return
        
        interaction_strengths = []
        distances = []
        
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                r = np.linalg.norm(positions[i] - positions[j])
                V = self.vortex_interaction_potential(r)
                interaction_strengths.append(V)
                distances.append(r)
        
        mean_interaction = np.mean(interaction_strengths)
        mean_distance = np.mean(distances)
        
        print(f"=== VORTEX INTERACTION ANALYSIS ===")
        print(f"Number of vortex pairs: {len(interaction_strengths)}")
        print(f"Mean vortex separation: {mean_distance:.4f}")
        print(f"Mean interaction strength: {mean_interaction:.8f}")
        print(f"Substrate mass parameter m_X: {self.m_X}")
        
        # Physical interpretation
        if mean_interaction < 1e-6:
            print("✅ EXTREMELY WEAK INTERACTIONS")
            print("→ Vortices behave like dark matter particles")
            print("→ Prevents over-clustering conflicts")
        elif mean_interaction < 1e-3:
            print("✅ WEAK INTERACTIONS") 
            print("→ Similar to neutrino-like matter")
            print("→ Allows structure formation")
        else:
            print("⚠️ STRONG INTERACTIONS")
            print("→ May cause rapid clustering")
        
        return interaction_strengths, distances
    
    def plot_interaction_profile(self):
        """Plot the vortex interaction potential"""
        r_vals = np.logspace(-2, 2, 100)
        V_vals = [self.vortex_interaction_potential(r) for r in r_vals]
        
        plt.figure(figsize=(10, 6))
        
        plt.subplot(121)
        plt.loglog(r_vals, V_vals, 'b-', linewidth=3)
        plt.xlabel('Vortex Separation r')
        plt.ylabel('Interaction Potential V(r)')
        plt.title('Vortex-Vortex Interaction\nV(r) ~ exp(-m_X r)/√r')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(122)
        plt.semilogy(r_vals, V_vals, 'r-', linewidth=3)
        plt.xlabel('Vortex Separation r')
        plt.ylabel('Interaction Potential V(r)')
        plt.title('Interaction Range')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('vortex_interactions.png', dpi=150, bbox_inches='tight')
        plt.show()

def main():
    """Run complete vortex interaction analysis"""
    print("SUBSTRATE X - VORTEX INTERACTION ANALYSIS")
    print("=" * 50)
    
    # Create analyzer
    analyzer = VortexInteractionAnalyzer(m_X=0.2)
    
    # Test with some vortex positions (from your ensemble simulation)
    # These are example positions - replace with your actual vortex positions
    vortex_positions = [
        (2.1, 3.4, 0), (-1.8, 4.2, 0), (5.1, -2.3, 1),
        (-3.2, -4.1, 1), (1.5, -5.6, 2), (4.8, 1.9, 2)
    ]
    
    # Analyze interactions
    interactions, distances = analyzer.analyze_vortex_interactions(vortex_positions)
    
    # Plot interaction profile
    analyzer.plot_interaction_profile()
    
    print(f"\n=== PHYSICAL IMPLICATIONS ===")
    print(f"With m_X = {analyzer.m_X}:")
    print(f"→ Interaction range: ~{1/analyzer.m_X:.1f} length units")
    print(f"→ Yukawa suppression scale: {1/analyzer.m_X:.1f}")
    print(f"→ Vortices are effectively FREE at large separations")
    print(f"→ Perfect for COLD DARK MATTER analog")

if __name__ == "__main__":
    main()
