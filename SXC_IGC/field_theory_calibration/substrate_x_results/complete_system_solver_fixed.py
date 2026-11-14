#!/usr/bin/env python3
"""
Complete Coupled System Solver for Substrate X Theory
Tests the full integration of Substrate X with gravitational coupling.
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
        
        # Store additional parameters
        self.tau = tau  # Relaxation time scale
        
    def initialize_system(self, initial_rho=None, initial_phi=None):
        """Initialize the substrate and gravitational fields"""
        # Initialize substrate X
        if initial_rho is None:
            # Default: Gaussian perturbation at center
            x = np.linspace(-self.domain_size/2, self.domain_size/2, self.grid_size)
            y = np.linspace(-self.domain_size/2, self.domain_size/2, self.grid_size)
            X, Y = np.meshgrid(x, y)
            
            r0 = self.domain_size * 0.1  # 10% of domain
            initial_rho = np.exp(-(X**2 + Y**2) / (2 * r0**2))
        
        self.rho = initial_rho
        
        # Initialize gravitational potential through coupling
        if initial_phi is None:
            initial_phi = np.zeros_like(initial_rho)
        
        self.phi = initial_phi
        
    def compute_coupled_evolution(self, dt, steps=1):
        """Evolve the complete coupled system"""
        results = []
        
        for step in range(steps):
            # 1. Evolve substrate X (includes current phi influence)
            substrate_result = self.evolve_system(dt, self.rho, external_potential=self.phi)
            
            # 2. Update substrate density
            self.rho = substrate_result['rho_next']
            
            # 3. Compute gravitational response to new substrate configuration
            gravity_result = self.gravity_coupling.compute_gravitational_response(
                self.rho, self.phi, dt, self.tau
            )
            
            # 4. Update gravitational potential
            self.phi = gravity_result['phi_next']
            
            # Store results
            results.append({
                'step': step,
                'time': step * dt,
                'rho': self.rho.copy(),
                'phi': self.phi.copy(),
                'total_mass': np.sum(self.rho) * self.dx**2,
                'max_density': np.max(self.rho),
                'max_potential': np.max(self.phi)
            })
            
            # Print progress
            if step % max(1, steps // 10) == 0:
                print(f"Step {step}/{steps}, Max ρ: {np.max(self.rho):.2e}, Max φ: {np.max(self.phi):.2e}")
        
        return results

def test_complete_system():
    """Test the complete coupled system"""
    print("🎯 TESTING COMPLETE COUPLED SYSTEM")
    print("=" * 60)
    
    # Parameters
    params = {
        'grid_size': 32,
        'domain_size': 1e21,  # 1 million light-years in meters
        'alpha': 1e-5,
        'beta': 1.0, 
        'gamma': 1e6,
        'chi': 1.0,
        'tau': 1.0,
        'dim': 2  # Add this line to specify 2D
    }
    
    solver = CompleteSystemSolver(**params)
    
    # Initialize system
    print("Initializing system...")
    solver.initialize_system()
    
    # Run simulation
    print("Running coupled evolution...")
    dt = solver.dt  # Use the computed stable time step
    results = solver.compute_coupled_evolution(dt, steps=10)
    
    # Analyze results
    print("\n=== RESULTS ===")
    final_result = results[-1]
    print(f"Final max density: {final_result['max_density']:.2e}")
    print(f"Final max potential: {final_result['max_potential']:.2e}")
    print(f"Total mass conservation: {final_result['total_mass']:.2e}")
    
    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Initial state
    im1 = axes[0,0].imshow(results[0]['rho'], extent=[-1,1,-1,1], origin='lower')
    axes[0,0].set_title('Initial Density')
    plt.colorbar(im1, ax=axes[0,0])
    
    im2 = axes[0,1].imshow(results[0]['phi'], extent=[-1,1,-1,1], origin='lower')
    axes[0,1].set_title('Initial Potential')
    plt.colorbar(im2, ax=axes[0,1])
    
    # Final state
    im3 = axes[1,0].imshow(final_result['rho'], extent=[-1,1,-1,1], origin='lower')
    axes[1,0].set_title('Final Density')
    plt.colorbar(im3, ax=axes[1,0])
    
    im4 = axes[1,1].imshow(final_result['phi'], extent=[-1,1,-1,1], origin='lower')
    axes[1,1].set_title('Final Potential')
    plt.colorbar(im4, ax=axes[1,1])
    
    plt.tight_layout()
    plt.savefig('complete_system_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return solver, results

if __name__ == "__main__":
    test_complete_system()
