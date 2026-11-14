#!/usr/bin/env python3
"""
Enhanced Complete System Solver
With better physics, multiple initial conditions, and advanced analysis
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

class EnhancedSolver:
    def __init__(self, grid_size=64, domain_size=1.0, alpha=0.01, beta=0.5, 
                 gamma=0.2, chi=0.3, tau=0.3, dim=2):
        """Initialize enhanced solver with better physics"""
        self.grid_size = grid_size
        self.domain_size = domain_size
        self.dim = dim
        self.alpha = alpha    # Diffusion
        self.beta = beta      # Reaction (logistic growth)
        self.gamma = gamma    # Substrate-potential coupling
        self.chi = chi        # Density-potential coupling strength
        self.tau = tau        # Potential relaxation time
        
        # Grid parameters
        self.dx = domain_size / grid_size
        self.dy = domain_size / grid_size
        
        # Adaptive time stepping
        self.dt = 0.05 * self.dx**2 / (4 * alpha)
        
        # Create grid
        x = np.linspace(-domain_size/2, domain_size/2, grid_size)
        y = np.linspace(-domain_size/2, domain_size/2, grid_size)
        self.X, self.Y = np.meshgrid(x, y)
        self.R = np.sqrt(self.X**2 + self.Y**2)
        
        print(f"Enhanced Solver: {grid_size}x{grid_size} grid")
        print(f"Parameters: α={alpha}, β={beta}, γ={gamma}, χ={chi}, τ={tau}")
        print(f"Grid: dx={self.dx:.3f}, Time: dt={self.dt:.3f}")
    
    def initialize_system(self, pattern='gaussian'):
        """Initialize with different patterns"""
        if pattern == 'gaussian':
            # Single Gaussian
            r0 = self.domain_size * 0.15
            self.rho = np.exp(-(self.X**2 + self.Y**2) / (2 * r0**2))
            
        elif pattern == 'double':
            # Two Gaussians
            r0 = self.domain_size * 0.1
            x1, y1 = -0.2, -0.2
            x2, y2 = 0.2, 0.2
            gauss1 = np.exp(-((self.X-x1)**2 + (self.Y-y1)**2) / (2 * r0**2))
            gauss2 = np.exp(-((self.X-x2)**2 + (self.Y-y2)**2) / (2 * r0**2))
            self.rho = 0.7 * (gauss1 + gauss2)
            
        elif pattern == 'random':
            # Random perturbations
            r0 = self.domain_size * 0.2
            base = np.exp(-(self.X**2 + self.Y**2) / (2 * r0**2))
            noise = 0.3 * np.random.randn(self.grid_size, self.grid_size)
            self.rho = np.clip(base + gaussian_filter(noise, sigma=1), 0, 1)
            
        elif pattern == 'ring':
            # Ring structure
            r_inner = self.domain_size * 0.2
            r_outer = self.domain_size * 0.3
            ring_mask = (self.R >= r_inner) & (self.R <= r_outer)
            self.rho = 0.8 * ring_mask.astype(float)
        
        self.phi = np.zeros_like(self.rho)
        
        print(f"Initialized '{pattern}' pattern: ρ=[{np.min(self.rho):.3f}, {np.max(self.rho):.3f}]")
    
    def compute_gravitational_potential(self, density):
        """Enhanced potential calculation with proper physics"""
        # Poisson-like equation: ∇²φ = χρ
        # Solved iteratively with relaxation
        
        phi_old = self.phi.copy()
        phi_new = phi_old.copy()
        
        # Gauss-Seidel iteration for Poisson equation
        for _ in range(10):  # Few iterations for speed
            for i in range(1, self.grid_size-1):
                for j in range(1, self.grid_size-1):
                    phi_new[i,j] = 0.25 * (
                        phi_old[i+1,j] + phi_new[i-1,j] + 
                        phi_old[i,j+1] + phi_new[i,j-1] - 
                        self.chi * density[i,j] * self.dx**2
                    )
        
        # Smooth transition
        return 0.7 * phi_new + 0.3 * phi_old
    
    def evolve_substrate(self):
        """Enhanced substrate evolution with proper fluxes"""
        new_rho = self.rho.copy()
        
        # Add small noise to prevent symmetry breaking
        noise_strength = 1e-4
        noise = noise_strength * np.random.randn(self.grid_size, self.grid_size)
        
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Diffusion (Laplacian)
                laplacian = (self.rho[i+1,j] + self.rho[i-1,j] + 
                            self.rho[i,j+1] + self.rho[i,j-1] - 
                            4 * self.rho[i,j]) / (self.dx**2)
                
                # Reaction (logistic with Allee effect)
                reaction = self.beta * self.rho[i,j] * (1 - self.rho[i,j]) * (self.rho[i,j] - 0.1)
                
                # Coupling to potential (density moves toward potential minima)
                grad_phi_x = (self.phi[i+1,j] - self.phi[i-1,j]) / (2 * self.dx)
                grad_phi_y = (self.phi[i,j+1] - self.phi[i,j-1]) / (2 * self.dx)
                
                # Advection toward potential minima
                advection = -self.gamma * (
                    grad_phi_x * (self.rho[i+1,j] - self.rho[i-1,j]) / (2 * self.dx) +
                    grad_phi_y * (self.rho[i,j+1] - self.rho[i,j-1]) / (2 * self.dx)
                )
                
                # Update
                new_rho[i,j] = self.rho[i,j] + self.dt * (
                    self.alpha * laplacian + reaction + advection + noise[i,j]
                )
        
        # Boundary conditions (zero flux)
        new_rho[0,:] = new_rho[1,:]
        new_rho[-1,:] = new_rho[-2,:]
        new_rho[:,0] = new_rho[:,1]
        new_rho[:,-1] = new_rho[:,-2]
        
        # Ensure physical bounds
        new_rho = np.clip(new_rho, 0, 2.0)
        
        return new_rho
    
    def compute_system_metrics(self):
        """Compute various system metrics"""
        total_mass = np.sum(self.rho) * self.dx * self.dy
        center_of_mass_x = np.sum(self.X * self.rho) / np.sum(self.rho)
        center_of_mass_y = np.sum(self.Y * self.rho) / np.sum(self.rho)
        
        # Energy-like quantities
        density_gradient = np.gradient(self.rho, self.dx, self.dx)
        gradient_energy = np.sum(density_gradient[0]**2 + density_gradient[1]**2) * self.dx * self.dy
        
        potential_energy = np.sum(self.rho * self.phi) * self.dx * self.dy
        
        return {
            'total_mass': total_mass,
            'com_x': center_of_mass_x,
            'com_y': center_of_mass_y,
            'gradient_energy': gradient_energy,
            'potential_energy': potential_energy,
            'max_density': np.max(self.rho),
            'min_density': np.min(self.rho),
            'max_potential': np.max(self.phi)
        }
    
    def evolve_system(self, steps=100, pattern='gaussian'):
        """Evolve system with comprehensive analysis"""
        self.initialize_system(pattern)
        
        results = []
        metrics_history = []
        
        print(f"Evolution: {pattern} pattern, {steps} steps")
        
        for step in range(steps):
            # Evolve system
            self.rho = self.evolve_substrate()
            self.phi = self.compute_gravitational_potential(self.rho)
            
            # Compute metrics
            metrics = self.compute_system_metrics()
            metrics['step'] = step
            metrics['time'] = step * self.dt
            
            metrics_history.append(metrics)
            results.append({
                'rho': self.rho.copy(),
                'phi': self.phi.copy(),
                'step': step
            })
            
            # Progress
            if step % max(1, steps // 10) == 0:
                print(f"Step {step:3d}: ρ={metrics['max_density']:.3f}, "
                      f"PE={metrics['potential_energy']:.3f}, COM=({metrics['com_x']:.3f}, {metrics['com_y']:.3f})")
        
        return results, metrics_history

def run_comparative_study():
    """Run comparison of different initial conditions"""
    print("🔬 COMPARATIVE STUDY OF PATTERNS")
    print("=" * 60)
    
    # Common parameters
    base_params = {
        'grid_size': 64,
        'domain_size': 1.0,
        'alpha': 0.01,
        'beta': 0.5,
        'gamma': 0.2,
        'chi': 0.3,
        'tau': 0.3
    }
    
    patterns = ['gaussian', 'double', 'ring', 'random']
    all_results = {}
    
    for pattern in patterns:
        print(f"\n--- Testing {pattern.upper()} pattern ---")
        solver = EnhancedSolver(**base_params)
        results, metrics = solver.evolve_system(steps=80, pattern=pattern)
        all_results[pattern] = (results, metrics, solver)
    
    # Comparative visualization
    fig, axes = plt.subplots(len(patterns), 4, figsize=(20, 5*len(patterns)))
    
    for idx, pattern in enumerate(patterns):
        results, metrics, solver = all_results[pattern]
        
        # Initial density
        im1 = axes[idx, 0].imshow(results[0]['rho'], extent=[-0.5,0.5,-0.5,0.5], 
                                 origin='lower', cmap='viridis')
        axes[idx, 0].set_title(f'{pattern.title()} - Initial Density')
        plt.colorbar(im1, ax=axes[idx, 0])
        
        # Final density
        im2 = axes[idx, 1].imshow(results[-1]['rho'], extent=[-0.5,0.5,-0.5,0.5],
                                 origin='lower', cmap='viridis')
        axes[idx, 1].set_title(f'{pattern.title()} - Final Density')
        plt.colorbar(im2, ax=axes[idx, 1])
        
        # Final potential
        im3 = axes[idx, 2].imshow(results[-1]['phi'], extent=[-0.5,0.5,-0.5,0.5],
                                 origin='lower', cmap='plasma')
        axes[idx, 2].set_title(f'{pattern.title()} - Final Potential')
        plt.colorbar(im3, ax=axes[idx, 2])
        
        # Time evolution of max density
        steps = [m['step'] for m in metrics]
        max_density = [m['max_density'] for m in metrics]
        axes[idx, 3].plot(steps, max_density, 'b-', linewidth=2)
        axes[idx, 3].set_title(f'{pattern.title()} - Density Evolution')
        axes[idx, 3].set_xlabel('Time Step')
        axes[idx, 3].set_ylabel('Max Density')
        axes[idx, 3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('comparative_study.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Energy evolution comparison
    plt.figure(figsize=(12, 8))
    for pattern in patterns:
        _, metrics, _ = all_results[pattern]
        steps = [m['step'] for m in metrics]
        potential_energy = [m['potential_energy'] for m in metrics]
        plt.plot(steps, potential_energy, linewidth=2, label=pattern.title())
    
    plt.xlabel('Time Step')
    plt.ylabel('Potential Energy')
    plt.title('Potential Energy Evolution - All Patterns')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('energy_evolution.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n✅ COMPARATIVE STUDY COMPLETED!")
    print(f"Tested {len(patterns)} different initial conditions")
    
    return all_results

if __name__ == "__main__":
    results = run_comparative_study()
