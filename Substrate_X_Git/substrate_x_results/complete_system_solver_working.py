#!/usr/bin/env python3
"""
Complete Coupled System Solver - Working Version
"""

import numpy as np
import matplotlib.pyplot as plt
from src.numerical_solver_fixed_gamma import SubstrateXSolver
from src.information_gravity_coupling import InformationGravityCoupling

class CompleteSystemSolver(SubstrateXSolver):
    def __init__(self, grid_size=32, domain_size=1e21, alpha=1e-5, beta=1.0, 
                 gamma=1e6, chi=1.0, tau=1.0, dim=2):
        super().__init__(dim, grid_size, domain_size, alpha, beta, gamma, chi, tau)
        
        # Initialize gravity coupling
        self.gravity_coupling = InformationGravityCoupling(
            grid_size=grid_size,
            domain_size=domain_size,
            coupling_strength=chi
        )
        
        self.tau = tau
        
    def initialize_system(self, initial_rho=None):
        """Initialize the system"""
        if initial_rho is None:
            # Create Gaussian perturbation
            x = np.linspace(-self.domain_size/2, self.domain_size/2, self.grid_size)
            y = np.linspace(-self.domain_size/2, self.domain_size/2, self.grid_size)
            X, Y = np.meshgrid(x, y)
            r0 = self.domain_size * 0.1
            initial_rho = np.exp(-(X**2 + Y**2) / (2 * r0**2))
        
        self.rho = initial_rho
        self.phi = np.zeros_like(initial_rho)
        
    def compute_coupled_evolution(self, dt, steps=1):
        """Evolve the coupled system"""
        results = []
        
        for step in range(steps):
            # 1. Evolve substrate X with current potential
            substrate_result = self.evolve_system(dt, self.rho, external_potential=self.phi)
            self.rho = substrate_result['rho_next']
            
            # 2. Compute gravitational response
            gravity_result = self.gravity_coupling.compute_gravitational_response(
                self.rho, self.phi, dt, self.tau
            )
            self.phi = gravity_result['phi_next']
            
            # Store results
            results.append({
                'step': step,
                'time': step * dt,
                'rho': self.rho.copy(),
                'phi': self.phi.copy(),
                'max_density': np.max(self.rho),
                'max_potential': np.max(self.phi)
            })
            
            if step % max(1, steps // 5) == 0:
                print(f"Step {step}/{steps}, Max ρ: {np.max(self.rho):.2e}")
        
        return results

def test_complete_system():
    """Test the complete system"""
    print("🎯 TESTING COMPLETE COUPLED SYSTEM")
    print("=" * 60)
    
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
    
    solver = CompleteSystemSolver(**params)
    solver.initialize_system()
    
    print("Running simulation...")
    dt = solver.dt
    results = solver.compute_coupled_evolution(dt, steps=5)
    
    # Plot results
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    
    im1 = axes[0].imshow(results[0]['rho'], extent=[-1,1,-1,1], origin='lower')
    axes[0].set_title('Initial Density')
    plt.colorbar(im1, ax=axes[0])
    
    im2 = axes[1].imshow(results[-1]['rho'], extent=[-1,1,-1,1], origin='lower')
    axes[1].set_title('Final Density')
    plt.colorbar(im2, ax=axes[1])
    
    plt.tight_layout()
    plt.savefig('coupled_system_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"Initial max density: {results[0]['max_density']:.2e}")
    print(f"Final max density: {results[-1]['max_density']:.2e}")
    
    return solver, results

if __name__ == "__main__":
    test_complete_system()
