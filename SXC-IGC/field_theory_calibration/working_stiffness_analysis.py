#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class WorkingStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, eta_scale=0.0, **kwargs):
        super().__init__(**kwargs)
        self.eta_scale = eta_scale
    
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.eta_scale != 0:
            alpha_eff = self.alpha * (1.0 + self.eta_scale * rho**2)
            original_stiffness = self.alpha * F
            variable_stiffness = alpha_eff * F
            dF_dt = dF_dt - original_stiffness + variable_stiffness
        
        return dE_dt, dF_dt

def analyze_scale_separation(solver):
    """Calculate solar and galactic scale effects"""
    # Get final fields
    rho, E, F = solver.rho, solver.E, solver.F
    
    # Calculate field gradients to estimate scales
    grad_F = np.gradient(F, solver.dx, axis=(0, 1))
    grad_F_mag = np.sqrt(grad_F[0]**2 + grad_F[1]**2)
    
    # Estimate effective couplings
    F_rms = np.sqrt(np.mean(F**2))
    grad_F_rms = np.sqrt(np.mean(grad_F_mag**2))
    
    # Solar scale (small scale, high gradient)
    keff_solar = grad_F_rms / (F_rms + 1e-10)
    
    # Galactic scale (large scale, low gradient)  
    keff_galactic = F_rms
    
    return {
        'keff_solar': keff_solar,
        'keff_galactic': keff_galactic,
        'F_rms': F_rms,
        'grad_F_rms': grad_F_rms
    }

def test_stiffness_with_analysis():
    print("🔧 WORKING VARIABLE STIFFNESS WITH ANALYSIS")
    print("=" * 60)
    
    eta_values = [0.0, 100.0, 500.0, 1000.0, 5000.0]
    baseline = None
    
    for eta in eta_values:
        print(f"\nTesting η = {eta}")
        solver = WorkingStiffnessSolver(alpha=1e-5, delta1=25.0, eta_scale=eta)
        solver.initialize_system('gaussian')
        solver.evolve_system(30)
        
        analysis = analyze_scale_separation(solver)
        
        g = analysis['keff_galactic']
        s = analysis['keff_solar']
        ratio = g/s if s > 0 else 0
        
        print(f"  Galactic: {g:.6f}")
        print(f"  Solar:    {s:.6f}")
        print(f"  Ratio:    {ratio:.1f}")
        print(f"  F_RMS:    {analysis['F_rms']:.4f}")
        
        if eta == 0.0:
            baseline = analysis
        
        if baseline and eta > 0:
            g_boost = g / baseline['keff_galactic']
            s_reduction = s / baseline['keff_solar']
            print(f"  Boost:    {g_boost:.1f}x galactic, {s_reduction:.1f}x solar")

test_stiffness_with_analysis()
