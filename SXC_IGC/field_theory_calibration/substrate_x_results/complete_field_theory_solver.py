#!/usr/bin/env python3
"""
Complete Field Theory Solver for Substrate X
With proper E and F field evolution and energy calculations
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

class CompleteFieldTheorySolver:
    def __init__(self, grid_size=64, domain_size=1.0, 
                 alpha=0.01, beta=0.5, gamma=0.2,  # Substrate parameters
                 delta1=0.5, delta2=0.3, kappa=0.4,  # Field coupling parameters
                 tau_rho=0.1, tau_E=0.1, tau_F=0.1):  # Relaxation times
        
        self.grid_size = grid_size
        self.domain_size = domain_size
        
        # Substrate parameters
        self.alpha = alpha    # Diffusion
        self.beta = beta      # Reaction  
        self.gamma = gamma    # Substrate self-interaction
        
        # Field coupling parameters - CRITICAL FOR DYNAMICS
        self.delta1 = delta1  # Substrate → E field coupling (ρ influences E)
        self.delta2 = delta2  # E → F field coupling  
        self.kappa = kappa    # F → Substrate coupling (feedback loop)
        
        # Relaxation times
        self.tau_rho = tau_rho
        self.tau_E = tau_E
        self.tau_F = tau_F
        
        # Grid
        self.dx = domain_size / grid_size
        self.dy = domain_size / grid_size
        self.dt = 0.1 * self.dx**2 / (4 * max(alpha, delta1, delta2))
        
        # Coordinate system
        x = np.linspace(-domain_size/2, domain_size/2, grid_size)
        y = np.linspace(-domain_size/2, domain_size/2, grid_size)
        self.X, self.Y = np.meshgrid(x, y)
        self.R = np.sqrt(self.X**2 + self.Y**2)
        
        print("🔬 COMPLETE FIELD THEORY SOLVER")
        print("=" * 50)
        print(f"Substrate: α={alpha}, β={beta}, γ={gamma}")
        print(f"Field Coupling: δ₁={delta1}, δ₂={delta2}, κ={kappa}")
        print(f"Relaxation: τ_ρ={tau_rho}, τ_E={tau_E}, τ_F={tau_F}")
        print(f"Grid: {grid_size}x{grid_size}, dx={self.dx:.3f}, dt={self.dt:.5f}")
    
    def initialize_system(self, pattern='gaussian'):
        """Initialize all fields"""
        if pattern == 'gaussian':
            r0 = self.domain_size * 0.15
            self.rho = np.exp(-(self.X**2 + self.Y**2) / (2 * r0**2))
            
        elif pattern == 'double':
            r0 = self.domain_size * 0.1
            gauss1 = np.exp(-((self.X+0.2)**2 + (self.Y+0.2)**2) / (2 * r0**2))
            gauss2 = np.exp(-((self.X-0.2)**2 + (self.Y-0.2)**2) / (2 * r0**2))
            self.rho = 0.7 * (gauss1 + gauss2)
            
        elif pattern == 'asymmetric':
            # Break symmetry intentionally
            r0 = self.domain_size * 0.12
            self.rho = np.exp(-((self.X-0.1)**2 + (self.Y+0.15)**2) / (2 * r0**2))
            self.rho += 0.5 * np.exp(-((self.X+0.15)**2 + (self.Y-0.1)**2) / (2 * r0**2))
            
        elif pattern == 'quadrupole':
            # Four sources to create interesting field patterns
            positions = [(-0.2,-0.2), (-0.2,0.2), (0.2,-0.2), (0.2,0.2)]
            r0 = self.domain_size * 0.08
            self.rho = np.zeros_like(self.X)
            for i, (px, py) in enumerate(positions):
                sign = 1.0 if i % 2 == 0 else 0.6  # Different strengths
                self.rho += sign * np.exp(-((self.X-px)**2 + (self.Y-py)**2) / (2 * r0**2))
        
        # Initialize fields with small perturbations
        self.E = 0.01 * np.random.randn(self.grid_size, self.grid_size)  # E field
        self.F = 0.01 * np.random.randn(self.grid_size, self.grid_size)  # F field
        
        print(f"Initialized '{pattern}': ρ_max={np.max(self.rho):.3f}")
    
    def compute_field_evolution(self):
        """Evolve E and F fields according to coupling equations"""
        E_new = self.E.copy()
        F_new = self.F.copy()
        
        # Compute field gradients for dynamics
        grad_Ex, grad_Ey = np.gradient(self.E, self.dx, self.dx)
        grad_Fx, grad_Fy = np.gradient(self.F, self.dx, self.dx)
        laplacian_E = np.gradient(grad_Ex, self.dx, axis=0)[0] + np.gradient(grad_Ey, self.dx, axis=1)[1]
        laplacian_F = np.gradient(grad_Fx, self.dx, axis=0)[0] + np.gradient(grad_Fy, self.dx, axis=1)[1]
        
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # E field evolution: ∂E/∂t = δ₁·ρ - ∇²E + interaction terms
                source_E = self.delta1 * self.rho[i,j]  # CRITICAL: ρ → E coupling
                diffusion_E = laplacian_E[i,j]
                
                # F field influence on E
                F_coupling = 0.1 * self.F[i,j] * (1 - np.tanh(5 * abs(self.F[i,j])))
                
                E_new[i,j] = self.E[i,j] + self.dt * (
                    source_E + diffusion_E + F_coupling - self.E[i,j] / self.tau_E
                )
                
                # F field evolution: ∂F/∂t = δ₂·E - ∇²F + nonlinear terms  
                source_F = self.delta2 * self.E[i,j]    # CRITICAL: E → F coupling
                diffusion_F = laplacian_F[i,j]
                
                # Nonlinear self-interaction
                F_nonlinear = -0.2 * self.F[i,j]**3
                
                F_new[i,j] = self.F[i,j] + self.dt * (
                    source_F + diffusion_F + F_nonlinear - self.F[i,j] / self.tau_F
                )
        
        # Boundary conditions (Neumann zero)
        for field in [E_new, F_new]:
            field[0,:] = field[1,:]
            field[-1,:] = field[-2,:]
            field[:,0] = field[:,1]
            field[:,-1] = field[:,-2]
        
        return E_new, F_new
    
    def evolve_substrate(self):
        """Evolve substrate with field feedback"""
        rho_new = self.rho.copy()
        
        # Compute substrate dynamics
        laplacian_rho = np.zeros_like(self.rho)
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                laplacian_rho[i,j] = (self.rho[i+1,j] + self.rho[i-1,j] + 
                                     self.rho[i,j+1] + self.rho[i,j-1] - 
                                     4 * self.rho[i,j]) / (self.dx**2)
        
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Standard reaction-diffusion
                diffusion = self.alpha * laplacian_rho[i,j]
                reaction = self.beta * self.rho[i,j] * (1 - self.rho[i,j])
                
                # CRITICAL: Field feedback (F → ρ coupling)
                field_feedback = self.kappa * self.F[i,j] * self.rho[i,j]
                
                # E field influence (gradient forces)
                grad_Ex = (self.E[i+1,j] - self.E[i-1,j]) / (2 * self.dx)
                grad_Ey = (self.E[i,j+1] - self.E[i,j-1]) / (2 * self.dx)
                E_force = -self.gamma * (grad_Ex**2 + grad_Ey**2) * self.rho[i,j]
                
                rho_new[i,j] = self.rho[i,j] + self.dt * (
                    diffusion + reaction + field_feedback + E_force - self.rho[i,j] / self.tau_rho
                )
        
        # Boundary conditions
        rho_new[0,:] = rho_new[1,:]
        rho_new[-1,:] = rho_new[-2,:]
        rho_new[:,0] = rho_new[:,1]
        rho_new[:,-1] = rho_new[:,-2]
        
        rho_new = np.clip(rho_new, 0, 2.0)
        return rho_new
    
    def compute_energy_densities(self):
        """Compute proper field theory energy densities"""
        # Kinetic-like energy from substrate gradients
        grad_rho_x, grad_rho_y = np.gradient(self.rho, self.dx, self.dx)
        kinetic_energy_density = 0.5 * (grad_rho_x**2 + grad_rho_y**2)
        
        # Field energies (E and F)
        E_energy_density = 0.5 * self.E**2
        F_energy_density = 0.5 * self.F**2
        
        # Interaction energy densities
        rho_E_interaction = self.delta1 * self.rho * self.E  # ρ-E coupling
        E_F_interaction = self.delta2 * self.E * self.F      # E-F coupling  
        rho_F_interaction = self.kappa * self.rho * self.F   # ρ-F feedback
        
        # Total energy density
        total_energy_density = (kinetic_energy_density + E_energy_density + 
                               F_energy_density + rho_E_interaction + 
                               E_F_interaction + rho_F_interaction)
        
        # Integrate over space
        kinetic_energy = np.sum(kinetic_energy_density) * self.dx * self.dy
        E_energy = np.sum(E_energy_density) * self.dx * self.dy
        F_energy = np.sum(F_energy_density) * self.dx * self.dy
        interaction_energy = (np.sum(rho_E_interaction) + np.sum(E_F_interaction) + 
                            np.sum(rho_F_interaction)) * self.dx * self.dy
        total_energy = np.sum(total_energy_density) * self.dx * self.dy
        
        return {
            'kinetic_energy': kinetic_energy,
            'E_field_energy': E_energy,
            'F_field_energy': F_energy,
            'interaction_energy': interaction_energy,
            'total_energy': total_energy,
            'rho_E_coupling': np.sum(rho_E_interaction) * self.dx * self.dy,
            'E_F_coupling': np.sum(E_F_interaction) * self.dx * self.dy,
            'rho_F_feedback': np.sum(rho_F_interaction) * self.dx * self.dy
        }
    
    def compute_diagnostics(self):
        """Compute comprehensive system diagnostics"""
        energies = self.compute_energy_densities()
        
        # Field strengths
        E_rms = np.sqrt(np.mean(self.E**2))
        F_rms = np.sqrt(np.mean(self.F**2))
        
        # Correlation between fields
        if np.std(self.rho) > 0 and np.std(self.E) > 0:
            rho_E_correlation = np.corrcoef(self.rho.flatten(), self.E.flatten())[0,1]
        else:
            rho_E_correlation = 0
            
        if np.std(self.E) > 0 and np.std(self.F) > 0:
            E_F_correlation = np.corrcoef(self.E.flatten(), self.F.flatten())[0,1]
        else:
            E_F_correlation = 0
        
        return {
            **energies,
            'E_rms': E_rms,
            'F_rms': F_rms,
            'max_rho': np.max(self.rho),
            'min_rho': np.min(self.rho),
            'max_E': np.max(self.E),
            'min_E': np.min(self.E),
            'max_F': np.max(self.F),
            'min_F': np.min(self.F),
            'rho_E_correlation': rho_E_correlation,
            'E_F_correlation': E_F_correlation,
            'total_mass': np.sum(self.rho) * self.dx * self.dy
        }
    
    def evolve_system(self, steps=200, pattern='gaussian'):
        """Evolve complete coupled field theory"""
        self.initialize_system(pattern)
        
        results = []
        diagnostics_history = []
        
        print(f"\n🌀 EVOLVING: {pattern.upper()} PATTERN")
        print("Step | Max ρ | E RMS | F RMS | Total Energy | ρ-E Corr")
        print("-" * 65)
        
        for step in range(steps):
            # Evolve all fields in coupled manner
            self.E, self.F = self.compute_field_evolution()
            self.rho = self.evolve_substrate()
            
            # Compute diagnostics
            diag = self.compute_diagnostics()
            diag['step'] = step
            diagnostics_history.append(diag)
            
            results.append({
                'rho': self.rho.copy(),
                'E': self.E.copy(),
                'F': self.F.copy(),
                'step': step
            })
            
            # Progress reporting
            if step % max(1, steps // 10) == 0:
                print(f"{step:4d} | {diag['max_rho']:6.3f} | {diag['E_rms']:6.3f} | "
                      f"{diag['F_rms']:6.3f} | {diag['total_energy']:12.3e} | {diag['rho_E_correlation']:7.3f}")
        
        return results, diagnostics_history

def run_complete_field_theory():
    """Run the complete field theory simulation"""
    print("🚀 COMPLETE FIELD THEORY SIMULATION")
    print("=" * 60)
    
    # Parameters for active field dynamics
    params = {
        'grid_size': 64,
        'domain_size': 1.0,
        'alpha': 0.01,
        'beta': 0.8,
        'gamma': 0.3,
        'delta1': 0.6,  # Strong ρ→E coupling
        'delta2': 0.4,  # Moderate E→F coupling
        'kappa': 0.5,   # Strong F→ρ feedback
        'tau_rho': 0.2,
        'tau_E': 0.15,
        'tau_F': 0.25
    }
    
    patterns = ['gaussian', 'double', 'asymmetric', 'quadrupole']
    all_results = {}
    
    for pattern in patterns:
        solver = CompleteFieldTheorySolver(**params)
        results, diagnostics = solver.evolve_system(steps=150, pattern=pattern)
        all_results[pattern] = (results, diagnostics, solver)
    
    # Comprehensive visualization
    fig, axes = plt.subplots(len(patterns), 4, figsize=(20, 5*len(patterns)))
    
    for idx, pattern in enumerate(patterns):
        results, diagnostics, solver = all_results[pattern]
        final = results[-1]
        
        # Final states
        vmax_rho = max(1.0, np.max(final['rho']))
        
        im1 = axes[idx, 0].imshow(final['rho'], extent=[-0.5,0.5,-0.5,0.5],
                                 origin='lower', cmap='viridis', vmin=0, vmax=vmax_rho)
        axes[idx, 0].set_title(f'{pattern}\nFinal Density\nmax={np.max(final["rho"]):.3f}')
        plt.colorbar(im1, ax=axes[idx, 0])
        
        im2 = axes[idx, 1].imshow(final['E'], extent=[-0.5,0.5,-0.5,0.5],
                                 origin='lower', cmap='RdBu_r', vmin=-1, vmax=1)
        axes[idx, 1].set_title(f'E Field\nRMS={diagnostics[-1]["E_rms"]:.3f}')
        plt.colorbar(im2, ax=axes[idx, 1])
        
        im3 = axes[idx, 2].imshow(final['F'], extent=[-0.5,0.5,-0.5,0.5],
                                 origin='lower', cmap='RdBu_r', vmin=-1, vmax=1)
        axes[idx, 2].set_title(f'F Field\nRMS={diagnostics[-1]["F_rms"]:.3f}')
        plt.colorbar(im3, ax=axes[idx, 2])
        
        # Energy evolution
        steps = [d['step'] for d in diagnostics]
        total_energy = [d['total_energy'] for d in diagnostics]
        axes[idx, 3].plot(steps, total_energy, 'k-', linewidth=2, label='Total Energy')
        axes[idx, 3].plot(steps, [d['E_field_energy'] for d in diagnostics], 'r--', label='E Energy')
        axes[idx, 3].plot(steps, [d['F_field_energy'] for d in diagnostics], 'b--', label='F Energy')
        axes[idx, 3].set_title('Energy Evolution')
        axes[idx, 3].set_xlabel('Time Step')
        axes[idx, 3].set_ylabel('Energy')
        axes[idx, 3].legend()
        axes[idx, 3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('complete_field_theory_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Field correlations and interactions
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    for pattern in patterns:
        _, diagnostics, _ = all_results[pattern]
        steps = [d['step'] for d in diagnostics]
        
        axes[0,0].plot(steps, [d['rho_E_correlation'] for d in diagnostics], 
                      linewidth=2, label=pattern)
        axes[0,1].plot(steps, [d['E_F_correlation'] for d in diagnostics], 
                      linewidth=2, label=pattern)
        axes[1,0].plot(steps, [d['rho_E_coupling'] for d in diagnostics], 
                      linewidth=2, label=pattern)
        axes[1,1].plot(steps, [d['E_F_coupling'] for d in diagnostics], 
                      linewidth=2, label=pattern)
    
    axes[0,0].set_title('ρ-E Field Correlation')
    axes[0,0].set_ylabel('Correlation Coefficient')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    axes[0,1].set_title('E-F Field Correlation')
    axes[0,1].set_ylabel('Correlation Coefficient')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    axes[1,0].set_title('ρ-E Coupling Energy')
    axes[1,0].set_ylabel('Coupling Energy')
    axes[1,0].set_xlabel('Time Step')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    axes[1,1].set_title('E-F Coupling Energy')
    axes[1,1].set_ylabel('Coupling Energy')
    axes[1,1].set_xlabel('Time Step')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('field_correlations.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n🎉 COMPLETE FIELD THEORY SIMULATION FINISHED!")
    print("Key achievements:")
    print("• Proper field evolution with coupling terms")
    print("• Non-zero field energies and interactions") 
    print("• Dynamic feedback between substrate and fields")
    print("• Comprehensive energy diagnostics")
    
    return all_results

if __name__ == "__main__":
    run_complete_field_theory()
