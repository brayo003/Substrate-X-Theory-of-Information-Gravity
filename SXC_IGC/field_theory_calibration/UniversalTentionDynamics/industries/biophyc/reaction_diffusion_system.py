import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Callable

class ReactionDiffusionSystem:
    """
    Bio-Physics Reaction-Diffusion Framework
    Stable version with proper parameter tuning
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
        
        # STABLE parameters for Turing patterns
        self.Du = 0.0001  # Slow diffusion for activator
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
        """Initialize for Schnakenberg model with stable parameters"""
        # Homogeneous steady state
        u0 = self.a + self.b
        v0 = self.b / (u0**2)
        
        self.u = np.ones(self.grid_size) * u0
        self.v = np.ones(self.grid_size) * v0
        
        # Add VERY small random perturbations (critical for stability)
        self.u += 0.001 * np.random.normal(0, 1, self.grid_size)
        self.v += 0.001 * np.random.normal(0, 1, self.grid_size)
        
        # Ensure non-negative concentrations
        self.u = np.maximum(self.u, 0.001)
        self.v = np.maximum(self.v, 0.001)
        
        print("🎯 Schnakenberg model initialized with stable parameters")

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
        # f(u,v) = a - u + u²v
        # g(u,v) = b - u²v
        
        # Ensure numerical stability
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
        
        # Apply updates with bounds checking
        self.u += du
        self.v += dv
        
        # Ensure non-negative concentrations
        self.u = np.maximum(self.u, 0.001)
        self.v = np.maximum(self.v, 0.001)
        
        # Check for numerical stability
        if np.any(np.isnan(self.u)) or np.any(np.isnan(self.v)):
            raise ValueError("Numerical instability detected!")
        
        self.time += self.dt

    def calculate_pattern_metrics(self) -> Dict:
        """Calculate pattern metrics"""
        return {
            'u_variance': np.var(self.u),
            'v_variance': np.var(self.v),
            'u_range': np.max(self.u) - np.min(self.u),
            'v_range': np.max(self.v) - np.min(self.v),
            'total_u': np.sum(self.u),
            'total_v': np.sum(self.v)
        }

def demo_turing_patterns():
    """Demonstrate Turing pattern formation with stability"""
    print("🧪 DEMONSTRATING TURING PATTERN FORMATION")
    print("=" * 50)
    
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
    
    # Time evolution
    print("⏳ Evolving system...")
    n_steps = 5000  # More steps for slower pattern formation
    
    try:
        for step in range(n_steps):
            system.step()
            
            if step % 500 == 0:
                current_metrics = system.calculate_pattern_metrics()
                history.append({
                    'time': system.time,
                    'u': system.u.copy(),
                    'v': system.v.copy(),
                    'metrics': current_metrics
                })
                variance_ratio = current_metrics['u_variance'] / initial_metrics['u_variance']
                print(f"Step {step}: Time={system.time:.3f}, Variance Ratio={variance_ratio:.3f}")
                
                # Early stopping if pattern forms
                if variance_ratio > 10:
                    print("🎯 Pattern formation detected! Stopping early.")
                    break
    
    except ValueError as e:
        print(f"❌ {e}")
        return system, history
    
    # Final analysis
    final_metrics = history[-1]['metrics']
    
    pattern_formed = final_metrics['u_variance'] > 0.001
    pattern_strength = final_metrics['u_variance'] / initial_metrics['u_variance']
    
    print(f"\n📊 PATTERN ANALYSIS:")
    print(f"   Pattern Formed: {pattern_formed}")
    print(f"   Pattern Strength: {pattern_strength:.2f}x")
    print(f"   Final Variance: {final_metrics['u_variance']:.6f}")
    print(f"   Concentration Range: U={final_metrics['u_range']:.3f}, V={final_metrics['v_range']:.3f}")
    print(f"   Mass Conservation: U={final_metrics['total_u']/initial_metrics['total_u']:.3f}, "
          f"V={final_metrics['total_v']/initial_metrics['total_v']:.3f}")
    
    return system, history

def visualize_patterns(system, history):
    """Visualize the pattern formation"""
    if not history:
        print("❌ No history to visualize")
        return
        
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Initial state
    im1 = axes[0,0].imshow(history[0]['u'], cmap='viridis')
    axes[0,0].set_title('Initial Activator (u)')
    plt.colorbar(im1, ax=axes[0,0])
    
    # Middle state
    mid_idx = len(history) // 2
    if mid_idx > 0:
        im2 = axes[0,1].imshow(history[mid_idx]['u'], cmap='viridis')
        axes[0,1].set_title(f'Middle (t={history[mid_idx]["time"]:.3f})')
        plt.colorbar(im2, ax=axes[0,1])
    else:
        axes[0,1].text(0.5, 0.5, 'No middle state', ha='center', va='center')
        axes[0,1].set_title('Middle State')
    
    # Final state
    im3 = axes[0,2].imshow(history[-1]['u'], cmap='viridis')
    axes[0,2].set_title(f'Final (t={history[-1]["time"]:.3f})')
    plt.colorbar(im3, ax=axes[0,2])
    
    # Inhibitor evolution
    im4 = axes[1,0].imshow(history[0]['v'], cmap='plasma')
    axes[1,0].set_title('Initial Inhibitor (v)')
    plt.colorbar(im4, ax=axes[1,0])
    
    if mid_idx > 0:
        im5 = axes[1,1].imshow(history[mid_idx]['v'], cmap='plasma')
        axes[1,1].set_title(f'Middle Inhibitor')
        plt.colorbar(im5, ax=axes[1,1])
    else:
        axes[1,1].text(0.5, 0.5, 'No middle state', ha='center', va='center')
        axes[1,1].set_title('Middle Inhibitor')
    
    # Pattern evolution
    times = [h['time'] for h in history]
    variances = [h['metrics']['u_variance'] for h in history]
    
    axes[1,2].plot(times, variances, 'b-', linewidth=2)
    axes[1,2].set_xlabel('Time')
    axes[1,2].set_ylabel('Pattern Variance')
    axes[1,2].set_title('Pattern Formation Over Time')
    axes[1,2].grid(True)
    
    plt.tight_layout()
    plt.savefig('turing_patterns_stable.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("📊 Visualization saved as 'turing_patterns_stable.png'")

if __name__ == "__main__":
    system, history = demo_turing_patterns()
    visualize_patterns(system, history)
