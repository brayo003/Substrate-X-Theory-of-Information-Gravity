import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Callable

class ReactionDiffusionSystem:
    """
    Bio-Physics Reaction-Diffusion Framework
    Complete pattern formation demonstration
    """
    
    def __init__(self, grid_size: Tuple[int, int] = (100, 100), 
                 domain_size: Tuple[float, float] = (1.0, 1.0)):
        
        self.grid_size = grid_size
        self.domain_size = domain_size
        
        # Grid spacing
        self.dx = domain_size[0] / (grid_size[0] - 1)
        self.dy = domain_size[1] / (grid_size[1] - 1)
        
        # Species concentrations
        self.u = None  # Activator
        self.v = None  # Inhibitor
        
        # Optimized parameters for clear pattern formation
        self.Du = 0.0002  # Slow diffusion for activator
        self.Dv = 0.01    # Fast diffusion for inhibitor
        self.a = 0.1      # Reaction parameter
        self.b = 0.9      # Reaction parameter
        
        # Conservative time step
        max_D = max(self.Du, self.Dv)
        self.dt = 0.5 * min(self.dx**2, self.dy**2) / (4 * max_D)
        
        # Time
        self.time = 0.0
        
        print(f"🧬 REACTION-DIFFUSION SYSTEM INITIALIZED")
        print(f"   Grid: {grid_size}, Domain: {domain_size}")
        print(f"   Grid Spacing: dx={self.dx:.3f}, dy={self.dy:.3f}")
        print(f"   Stable dt: {self.dt:.6f}")

    def initialize_schnakenberg(self):
        """Initialize for Schnakenberg model with pattern-forming parameters"""
        # Homogeneous steady state
        u0 = self.a + self.b
        v0 = self.b / (u0**2)
        
        self.u = np.ones(self.grid_size) * u0
        self.v = np.ones(self.grid_size) * v0
        
        # Add random perturbations with some structure
        noise = 0.005 * np.random.normal(0, 1, self.grid_size)
        # Add some low-frequency components to help pattern formation
        xx, yy = np.meshgrid(np.linspace(0, 2*np.pi, self.grid_size[0]), 
                            np.linspace(0, 2*np.pi, self.grid_size[1]))
        low_freq = 0.003 * (np.sin(3*xx) + np.sin(3*yy))
        
        self.u += noise + low_freq
        self.v += noise + low_freq
        
        # Ensure non-negative concentrations
        self.u = np.maximum(self.u, 0.001)
        self.v = np.maximum(self.v, 0.001)
        
        print("🎯 Schnakenberg model initialized with pattern-forming parameters")

    def laplacian_2d(self, u: np.ndarray) -> np.ndarray:
        """Calculate 2D Laplacian with stable boundaries"""
        laplacian = np.zeros_like(u)
        
        # Central differences in interior
        laplacian[1:-1, 1:-1] = (
            (u[1:-1, 2:] - 2*u[1:-1, 1:-1] + u[1:-1, 0:-2]) / self.dx**2 +
            (u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[0:-2, 1:-1]) / self.dy**2
        )
        
        # Neumann boundaries (zero flux)
        laplacian[0, :] = laplacian[1, :]   # Top
        laplacian[-1, :] = laplacian[-2, :] # Bottom
        laplacian[:, 0] = laplacian[:, 1]   # Left
        laplacian[:, -1] = laplacian[:, -2] # Right
        
        return laplacian

    def reaction_schnakenberg(self) -> Tuple[np.ndarray, np.ndarray]:
        """Schnakenberg reaction terms with stability checks"""
        u_safe = np.maximum(self.u, 0.001)
        v_safe = np.maximum(self.v, 0.001)
        
        u2v = u_safe**2 * v_safe
        f = self.a - u_safe + u2v
        g = self.b - u2v
        
        return f, g

    def step(self):
        """Single time step with stability monitoring"""
        # Calculate Laplacians
        lap_u = self.laplacian_2d(self.u)
        lap_v = self.laplacian_2d(self.v)
        
        # Calculate reaction terms
        f, g = self.reaction_schnakenberg()
        
        # Update concentrations
        du = self.dt * (self.Du * lap_u + f)
        dv = self.dt * (self.Dv * lap_v + g)
        
        self.u += du
        self.v += dv
        
        # Ensure non-negative concentrations
        self.u = np.maximum(self.u, 0.001)
        self.v = np.maximum(self.v, 0.001)
        
        self.time += self.dt

    def calculate_pattern_metrics(self) -> Dict:
        """Calculate comprehensive pattern metrics"""
        return {
            'u_variance': np.var(self.u),
            'v_variance': np.var(self.v),
            'u_range': np.max(self.u) - np.min(self.u),
            'v_range': np.max(self.v) - np.min(self.v),
            'total_u': np.sum(self.u),
            'total_v': np.sum(self.v),
            'pattern_strength': np.var(self.u) / (np.var(self.u) + 1e-10)  # Normalized
        }

def run_complete_pattern_formation():
    """Run pattern formation to completion"""
    print("🧪 COMPLETE TURING PATTERN FORMATION")
    print("=" * 60)
    
    # Create system
    system = ReactionDiffusionSystem(grid_size=(100, 100))
    system.initialize_schnakenberg()
    
    # Store history for analysis
    history = []
    initial_metrics = system.calculate_pattern_metrics()
    history.append({
        'time': system.time,
        'u': system.u.copy(),
        'v': system.v.copy(),
        'metrics': initial_metrics
    })
    
    print("⏳ Evolving system to completion...")
    print("   This will take about 10,000 steps for full pattern stabilization")
    
    # Run for fixed number of steps to see complete evolution
    n_steps = 10000
    stability_count = 0
    last_variance = initial_metrics['u_variance']
    
    for step in range(n_steps):
        system.step()
        
        # Record every 200 steps
        if step % 200 == 0:
            current_metrics = system.calculate_pattern_metrics()
            history.append({
                'time': system.time,
                'u': system.u.copy(),
                'v': system.v.copy(),
                'metrics': current_metrics
            })
            
            variance_ratio = current_metrics['u_variance'] / initial_metrics['u_variance']
            print(f"Step {step:5d}: Time={system.time:6.2f}, Variance Ratio={variance_ratio:7.2f}x")
            
            # Check for stability (convergence)
            variance_change = abs(current_metrics['u_variance'] - last_variance) / last_variance
            if variance_change < 0.01:  # Less than 1% change
                stability_count += 1
            else:
                stability_count = 0
                
            last_variance = current_metrics['u_variance']
            
            # Stop if stable for 5 consecutive checks
            if stability_count >= 5:
                print(f"🎯 Pattern stabilized at step {step}!")
                break
    
    # Final analysis
    final_metrics = history[-1]['metrics']
    initial_metrics = history[0]['metrics']
    
    pattern_formed = final_metrics['u_variance'] > 0.001
    pattern_strength = final_metrics['u_variance'] / initial_metrics['u_variance']
    
    print(f"\n📊 FINAL PATTERN ANALYSIS:")
    print(f"   Total Steps: {len(history) * 200}")
    print(f"   Final Time: {system.time:.2f}")
    print(f"   Pattern Formed: {pattern_formed}")
    print(f"   Pattern Strength: {pattern_strength:.2f}x")
    print(f"   Final Variance: {final_metrics['u_variance']:.6f}")
    print(f"   Concentration Range: U={final_metrics['u_range']:.3f}, V={final_metrics['v_range']:.3f}")
    print(f"   Mass Conservation: U={final_metrics['total_u']/initial_metrics['total_u']:.3f}, "
          f"V={final_metrics['total_v']/initial_metrics['total_v']:.3f}")
    
    # Classify pattern type
    final_u = history[-1]['u']
    grad_x, grad_y = np.gradient(final_u)
    horizontal_structure = np.mean(np.abs(grad_x))
    vertical_structure = np.mean(np.abs(grad_y))
    
    if horizontal_structure > 2 * vertical_structure:
        pattern_type = "STRIPES (horizontal)"
    elif vertical_structure > 2 * horizontal_structure:
        pattern_type = "STRIPES (vertical)"
    elif final_metrics['u_variance'] < 0.0001:
        pattern_type = "HOMOGENEOUS"
    else:
        pattern_type = "SPOTS"
    
    print(f"   Pattern Type: {pattern_type}")
    
    return system, history

def visualize_complete_patterns(system, history):
    """Visualize the complete pattern formation process"""
    if not history:
        print("❌ No history to visualize")
        return
        
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    
    # Select key time points
    time_points = [0, len(history)//4, len(history)//2, -1]
    titles = ['Initial', 'Early Formation', 'Mid Evolution', 'Final Pattern']
    
    for i, idx in enumerate(time_points):
        if idx < len(history):
            # Activator
            im1 = axes[0,i].imshow(history[idx]['u'], cmap='viridis')
            axes[0,i].set_title(f'{titles[i]}\n(t={history[idx]["time"]:.1f})')
            plt.colorbar(im1, ax=axes[0,i])
            
            # Inhibitor
            im2 = axes[1,i].imshow(history[idx]['v'], cmap='plasma')
            axes[1,i].set_title(f'{titles[i]} Inhibitor')
            plt.colorbar(im2, ax=axes[1,i])
    
    # Add pattern evolution plot
    times = [h['time'] for h in history]
    variances = [h['metrics']['u_variance'] for h in history]
    
    # Create a new figure for the evolution
    plt.figure(figsize=(10, 6))
    plt.plot(times, variances, 'b-', linewidth=2)
    plt.xlabel('Time')
    plt.ylabel('Pattern Variance')
    plt.title('Complete Pattern Evolution')
    plt.grid(True)
    plt.savefig('pattern_evolution.png', dpi=300, bbox_inches='tight')
    
    plt.tight_layout()
    plt.savefig('complete_turing_patterns.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("📊 Visualizations saved:")
    print("   - 'complete_turing_patterns.png' (pattern snapshots)")
    print("   - 'pattern_evolution.png' (variance over time)")

if __name__ == "__main__":
    system, history = run_complete_pattern_formation()
    visualize_complete_patterns(system, history)
