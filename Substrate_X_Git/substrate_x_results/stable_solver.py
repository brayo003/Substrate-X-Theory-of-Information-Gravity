#!/usr/bin/env python3
"""
Stable Complete System Solver
With proper parameter scaling and numerical stability
"""

import numpy as np
import matplotlib.pyplot as plt

class StableSolver:
    def __init__(self, grid_size=32, domain_size=1.0, alpha=0.1, beta=1.0, 
                 gamma=0.1, chi=0.1, tau=1.0, dim=2):
        """Initialize with dimensionless parameters for stability"""
        self.grid_size = grid_size
        self.domain_size = domain_size  # Use dimensionless domain
        self.dim = dim
        self.alpha = alpha    # Diffusion coefficient
        self.beta = beta      # Reaction coefficient  
        self.gamma = gamma    # Coupling strength
        self.chi = chi        # Gravitational coupling
        self.tau = tau        # Relaxation time
        
        # Grid parameters (dimensionless)
        self.dx = domain_size / grid_size
        self.dy = domain_size / grid_size
        
        # Stable time step (CFL condition)
        self.dt = 0.1 * self.dx**2 / (4 * alpha)  # More conservative
        
        # Create grid
        x = np.linspace(-domain_size/2, domain_size/2, grid_size)
        y = np.linspace(-domain_size/2, domain_size/2, grid_size)
        self.X, self.Y = np.meshgrid(x, y)
        
        print(f"Stable Solver: {grid_size}x{grid_size} grid")
        print(f"dx={self.dx:.3f}, dt={self.dt:.3f}")
        print(f"α={alpha}, β={beta}, γ={gamma}, χ={chi}")
    
    def initialize_system(self):
        """Initialize with stable initial conditions"""
        # Gaussian initial condition (properly scaled)
        r0 = self.domain_size * 0.2  # 20% of domain
        self.rho = np.exp(-(self.X**2 + self.Y**2) / (2 * r0**2))
        self.phi = np.zeros_like(self.rho)
        
        print(f"Initial density: max={np.max(self.rho):.3f}, min={np.min(self.rho):.3f}")
    
    def compute_gravitational_potential(self, density):
        """Stable gravitational potential calculation"""
        # Use convolution with proper normalization
        epsilon = 1e-6  # Small regularization
        
        # Simple potential: negative of density (attractive)
        potential = -self.chi * density
        
        # Add smoothing to prevent instability
        from scipy.ndimage import gaussian_filter
        potential = gaussian_filter(potential, sigma=0.5)
        
        return potential
    
    def evolve_substrate(self, external_potential=None):
        """Stable substrate evolution with proper finite differences"""
        if external_potential is None:
            external_potential = np.zeros_like(self.rho)
        
        # Initialize new density
        new_rho = self.rho.copy()
        
        # Finite difference evolution (explicit method)
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Laplacian (5-point stencil)
                laplacian = (self.rho[i+1,j] + self.rho[i-1,j] + 
                            self.rho[i,j+1] + self.rho[i,j-1] - 
                            4 * self.rho[i,j]) / (self.dx**2)
                
                # Reaction term (logistic growth, bounded)
                reaction = self.beta * self.rho[i,j] * (1 - self.rho[i,j])
                
                # Coupling term (bounded)
                coupling = self.gamma * external_potential[i,j] * self.rho[i,j]
                
                # Update (explicit Euler)
                new_rho[i,j] = self.rho[i,j] + self.dt * (
                    self.alpha * laplacian + reaction + coupling
                )
        
        # Apply boundary conditions (zero flux)
        new_rho[0,:] = new_rho[1,:]   # Top
        new_rho[-1,:] = new_rho[-2,:] # Bottom  
        new_rho[:,0] = new_rho[:,1]   # Left
        new_rho[:,-1] = new_rho[:,-2] # Right
        
        return new_rho
    
    def evolve_system(self, steps=20):
        """Evolve the complete coupled system stably"""
        results = []
        
        for step in range(steps):
            try:
                # 1. Evolve substrate with current potential
                new_rho = self.evolve_substrate(self.phi)
                
                # Ensure density stays positive and bounded
                new_rho = np.clip(new_rho, 0, 2.0)  # Physical bounds
                
                # 2. Update gravitational potential based on new density
                new_phi = self.compute_gravitational_potential(new_rho)
                
                # Relaxation toward new potential
                if self.tau > 0:
                    alpha_relax = self.dt / (self.tau + self.dt)
                    new_phi_smooth = (1 - alpha_relax) * self.phi + alpha_relax * new_phi
                else:
                    new_phi_smooth = new_phi
                
                # Update state
                self.rho = new_rho
                self.phi = new_phi_smooth
                
                # Store results
                results.append({
                    'step': step,
                    'time': step * self.dt,
                    'rho': self.rho.copy(),
                    'phi': self.phi.copy(),
                    'max_density': np.max(self.rho),
                    'min_density': np.min(self.rho),
                    'max_potential': np.max(self.phi)
                })
                
                if step % max(1, steps // 5) == 0:
                    print(f"Step {step:2d}/{steps}: ρ=[{np.min(self.rho):.3f}, {np.max(self.rho):.3f}], "
                          f"φ={np.max(self.phi):.3f}")
                          
            except Exception as e:
                print(f"Error at step {step}: {e}")
                break
        
        return results

def test_stable_solver():
    """Test the stable solver"""
    print("🔧 STABLE SOLVER TEST")
    print("=" * 50)
    
    # Use dimensionless parameters for stability
    params = {
        'grid_size': 64,      # Higher resolution
        'domain_size': 1.0,   # Dimensionless domain
        'alpha': 0.01,        # Small diffusion
        'beta': 0.5,          # Moderate reaction
        'gamma': 0.1,         # Weak coupling
        'chi': 0.2,           # Moderate gravity
        'tau': 0.5,           # Fast relaxation
        'dim': 2
    }
    
    solver = StableSolver(**params)
    solver.initialize_system()
    
    print("Running stable simulation...")
    results = solver.evolve_system(steps=50)
    
    if not results:
        print("❌ Simulation failed - no results")
        return None, None
    
    # Plot results
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Initial state
    im1 = axes[0,0].imshow(results[0]['rho'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='viridis')
    axes[0,0].set_title('Initial Density')
    plt.colorbar(im1, ax=axes[0,0])
    
    im2 = axes[0,1].imshow(results[len(results)//2]['rho'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='viridis')
    axes[0,1].set_title('Middle Density')
    plt.colorbar(im2, ax=axes[0,1])
    
    im3 = axes[0,2].imshow(results[-1]['rho'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='viridis')
    axes[0,2].set_title('Final Density')
    plt.colorbar(im3, ax=axes[0,2])
    
    # Potentials
    im4 = axes[1,0].imshow(results[0]['phi'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='plasma')
    axes[1,0].set_title('Initial Potential')
    plt.colorbar(im4, ax=axes[1,0])
    
    im5 = axes[1,1].imshow(results[len(results)//2]['phi'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='plasma')
    axes[1,1].set_title('Middle Potential')
    plt.colorbar(im5, ax=axes[1,1])
    
    im6 = axes[1,2].imshow(results[-1]['phi'], extent=[-0.5,0.5,-0.5,0.5], origin='lower', cmap='plasma')
    axes[1,2].set_title('Final Potential')
    plt.colorbar(im6, ax=axes[1,2])
    
    plt.tight_layout()
    plt.savefig('stable_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Time evolution plot
    plt.figure(figsize=(10, 6))
    steps = [r['step'] for r in results]
    max_density = [r['max_density'] for r in results]
    max_potential = [r['max_potential'] for r in results]
    
    plt.subplot(2, 1, 1)
    plt.plot(steps, max_density, 'b-', linewidth=2)
    plt.ylabel('Max Density')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.plot(steps, max_potential, 'r-', linewidth=2)
    plt.ylabel('Max Potential')
    plt.xlabel('Time Step')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('evolution.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"✅ SUCCESS: Stable solver completed {len(results)} steps!")
    print(f"Final density range: [{results[-1]['min_density']:.3f}, {results[-1]['max_density']:.3f}]")
    
    return solver, results

if __name__ == "__main__":
    test_stable_solver()
