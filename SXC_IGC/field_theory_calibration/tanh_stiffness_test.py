#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class TanhStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=0.0, eta_power=10.0, rho_cutoff=0.5, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        if M_factor > 0:
            self.alpha_eff_max = self.alpha * (1.0 + M_factor)
        else:
            self.alpha_eff_max = self.alpha
        
        print(f"🔧 TANH STIFFNESS: M={M_factor:.0f}, alpha_eff_max={self.alpha_eff_max:.2e}")
    
    def compute_effective_stiffness(self, rho):
        """α_eff(ρ) = α × (1 + M × max(0, tanh(η_power × (ρ - ρ_cutoff))))"""
        if self.M_factor == 0.0:
            return self.alpha
            
        tanh_term = np.tanh(self.eta_power * (rho - self.rho_cutoff))
        stiffness_factor = 1.0 + self.M_factor * np.maximum(0.0, tanh_term)
        return self.alpha * stiffness_factor
        
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.M_factor != 0.0:
            alpha_eff = self.compute_effective_stiffness(rho)
            dF_dt = dF_dt + (alpha_eff - self.alpha) * F
            
        return dE_dt, dF_dt

def analyze_scales(solver):
    """Calculate solar and galactic scale effects"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    # Calculate field gradients
    grad_F = np.gradient(F, solver.dx, axis=(0, 1))
    grad_F_mag = np.sqrt(grad_F[0]**2 + grad_F[1]**2)
    
    F_rms = np.sqrt(np.mean(F**2))
    grad_F_rms = np.sqrt(np.mean(grad_F_mag**2))
    
    # Solar scale (high gradient regions)
    keff_solar = grad_F_rms / (F_rms + 1e-10)
    
    # Galactic scale (overall field strength)  
    keff_galactic = F_rms
    
    return {
        'keff_solar': keff_solar,
        'keff_galactic': keff_galactic,
        'F_rms': F_rms,
        'center_edge_ratio': abs(F[32,32] / F[0,0]) if F[0,0] != 0 else 0
    }

# Test the tanh stiffness
print("🚀 TANH STIFFNESS CALIBRATION")
print("Target: Solar ~0.001, Galactic ~0.100")
print("=" * 60)

M_factors = [0, 500.0, 2000.0, 5000.0]

for M in M_factors:
    print(f"\n🧪 Testing M = {M}")
    print("-" * 40)
    
    solver = TanhStiffnessSolver(
        alpha=1e-5, 
        delta1=25.0,
        M_factor=M, 
        eta_power=10.0, 
        rho_cutoff=0.5
    )
    
    solver.initialize_system('gaussian')
    solver.evolve_system(50)  # Run for 50 steps
    
    analysis = analyze_scales(solver)
    
    print(f"  Solar k_eff: {analysis['keff_solar']:.6f}")
    print(f"  Galactic k_eff: {analysis['keff_galactic']:.6f}") 
    print(f"  Center/Edge ratio: {analysis['center_edge_ratio']:.1f}x")
    print(f"  F_RMS: {analysis['F_rms']:.6f}")
    
    # Check progress toward targets
    if analysis['keff_solar'] > 0:
        solar_ratio = analysis['keff_solar'] / 0.001
        galactic_ratio = analysis['keff_galactic'] / 0.100
        print(f"  Progress: Solar {solar_ratio:.1f}x, Galactic {galactic_ratio:.1f}x of target")
