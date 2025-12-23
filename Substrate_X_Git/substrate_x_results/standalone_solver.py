#!/usr/bin/env python3
"""
Standalone Complete System Solver
Independent implementation that avoids inheritance issues
"""

import numpy as np
import matplotlib.pyplot as plt

class StandaloneSolver:
    def __init__(self, grid_size=32, domain_size=1e21, alpha=1e-5, beta=1.0, 
                 gamma=1e6, chi=1.0, tau=1.0, dim=2):
        """Initialize standalone solver - completely independent"""
        self.grid_size = grid_size
        self.domain_size = domain_size
        self.dim = dim
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.chi = chi
        self.tau = tau
        
        # Grid parameters
        self.dx = domain_size / grid_size
        self.dy = domain_size / grid_size
        
        # Time step (simplified calculation)
        self.dt = 0.1 * min(self.dx, self.dy)**2 / (2 * alpha)
        
        # Create grid
        x = np.linspace(-domain_size/2, domain_size/2, grid_size)
        y = np.linspace(-domain_size/2, domain_size/2, grid_size)
        self.X, self.Y = np.meshgrid(x, y)
        
        print(f"Standalone Solver: {grid_size}x{grid_size} grid, dx={self.dx:.2e}, dt={self.dt:.2e}")
    
    def initialize_system(self):
        """Initialize density and potential fields"""
        # Gaussian initial condition
        r0 = self.domain_size * 0.1
        self.rho = np.exp(-(self.X**2 + self.Y**2) / (2 * r0**2))
        self.phi = np.zeros_like(self.rho)
    
    def compute_gravitational_potential(self, density):
        """Simple gravitational potential calculation"""
        # Simplified potential calculation
        epsilon = 1e-10 * self.domain_size
        r = np.sqrt(self.X**2 + self.Y**2 + epsilon**2)
        
        # Mock gravitational potential (would use Poisson solver in real implementation)
        potential = -6.67430e-11 * density / (r + epsilon)
        return potential * self.chi
    
    def evolve_substrate(self, dt, external_potential=None):
        """Simple substrate evolution"""
        if external_potential is None:
            external_potential = np.zeros_like(self.rho)
        
        # Simple diffusion + reaction
        laplacian_rho = np.zeros_like(self.rho)
        
        # Finite difference laplacian
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                laplacian_rho[i,j] = (self.rho[i+1,j] + self.rho[i-1,j] + 
                                     self.rho[i,j+1] + self.rho[i,j-1] - 
                                     4 * self.rho[i,j]) / (self.dx * self.dy)
        
        # Simple evolution equation
        drho_dt = (self.alpha * laplacian_rho + 
                  self.beta * self.rho * (1 - self.rho) +
                  self.gamma * external_potential * self.rho)
        
        return self.rho + dt * drho_dt
    
    def evolve_system(self, steps=10):
        """Evolve the complete coupled system"""
        results = []
        
        for step in range(steps):
            # 1. Evolve substrate with current potential
            new_rho = self.evolve_substrate(self.dt, self.phi)
            
            # 2. Update gravitational potential based on new density
            new_phi = self.compute_gravitational_potential(new_rho)
            
            # Relaxation toward new potential
            if self.tau > 0:
                alpha = self.dt / (self.tau + self.dt)
                self.phi = (1 - alpha) * self.phi + alpha * new_phi
            else:
                self.phi = new_phi
            
            self.rho = new_rho
            
            # Store results
            results.append({
                'step': step,
                'time': step * self.dt,
                'rho': self.rho.copy(),
                'phi': self.phi.copy(),
                'max_density': np.max(self.rho),
                'max_potential': np.max(self.phi)
            })
            
            if step % max(1, steps // 5) == 0:
                print(f"Step {step}/{steps}, Max ρ: {np.max(self.rho):.2e}")
        
        return results

def test_standalone_solver():
    """Test the standalone solver"""
    print("🚀 STANDALONE SOLVER TEST")
    print("=" * 50)
    
    # Parameters - using same names but different implementation
    params = {
        'grid_size': 32,
        'domain_size': 1e21,
        'alpha': 1e-5,
        'beta': 1.0, 
        'gamma': 1e6,
        'chi': 1.0,
        'tau': 1.0,
        'dim': 2
    }
    
    solver = StandaloneSolver(**params)
    solver.initialize_system()
    
    print("Running standalone simulation...")
    results = solver.evolve_system(steps=10)
    
    # Plot results
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    
    im1 = axes[0].imshow(results[0]['rho'], extent=[-1,1,-1,1], origin='lower')
    axes[0].set_title('Initial Density')
    plt.colorbar(im1, ax=axes[0])
    
    im2 = axes[1].imshow(results[-1]['rho'], extent=[-1,1,-1,1], origin='lower')
    axes[1].set_title('Final Density')
    plt.colorbar(im2, ax=axes[1])
    
    plt.tight_layout()
    plt.savefig('standalone_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"✅ SUCCESS: Standalone solver completed!")
    print(f"Initial max density: {results[0]['max_density']:.2e}")
    print(f"Final max density: {results[-1]['max_density']:.2e}")
    
    return solver, results

if __name__ == "__main__":
    test_standalone_solver()
