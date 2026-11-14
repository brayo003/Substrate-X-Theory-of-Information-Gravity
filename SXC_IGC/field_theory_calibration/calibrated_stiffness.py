#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class CalibratedStiffnessSolver(CompleteFieldTheorySolver):
    def __init__(self, eta_base=0.0, eta_power=10.0, rho_cutoff=0.5, **kwargs):
        super().__init__(**kwargs)
        self.eta_base = eta_base
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
    
    def compute_effective_stiffness(self, rho):
        stiffness_factor = 1.0 + self.eta_base * np.exp(self.eta_power * (rho - self.rho_cutoff))
        return self.alpha * stiffness_factor
    
    def compute_field_evolution(self):
        rho, E, F = self.rho, self.E, self.F
        dE_dt, dF_dt = super().compute_field_evolution()
        
        if self.eta_base != 0:
            alpha_eff = self.compute_effective_stiffness(rho)
            stiffness_change = (alpha_eff - self.alpha) * F
            dF_dt = dF_dt + stiffness_change
        
        return dE_dt, dF_dt

def analyze_scale_separation(solver):
    """Calculate actual solar and galactic scale effects"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    # Calculate field gradients for scale estimation
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

def find_optimal_stiffness():
    print("🎯 FINDING OPTIMAL STIFFNESS FOR SCALE SEPARATION")
    print("Target: Solar ~0.001, Galactic ~0.100")
    print("=" * 60)
    
    # Test calibrated parameters
    test_cases = [
        {"eta_base": 1e3, "eta_power": 8, "rho_cutoff": 0.7, "label": "Mild"},
        {"eta_base": 5e3, "eta_power": 10, "rho_cutoff": 0.6, "label": "Medium"}, 
        {"eta_base": 2e4, "eta_power": 12, "rho_cutoff": 0.5, "label": "Strong"},
        {"eta_base": 1e4, "eta_power": 10, "rho_cutoff": 0.5, "label": "Balanced"},
    ]
    
    baseline = None
    
    for case in test_cases:
        print(f"\n🔧 Testing {case['label']}:")
        print(f"  η_base={case['eta_base']:.0e}, η_power={case['eta_power']}, ρ_cut={case['rho_cutoff']}")
        
        solver = CalibratedStiffnessSolver(
            alpha=1e-5, delta1=25.0,
            eta_base=case['eta_base'],
            eta_power=case['eta_power'],
            rho_cutoff=case['rho_cutoff']
        )
        solver.initialize_system('gaussian')
        solver.evolve_system(20)  # Shorter evolution for calibration
        
        analysis = analyze_scale_separation(solver)
        
        print(f"  Solar k_eff: {analysis['keff_solar']:.6f}")
        print(f"  Galactic k_eff: {analysis['keff_galactic']:.6f}") 
        print(f"  Center/Edge: {analysis['center_edge_ratio']:.1f}x")
        print(f"  F_RMS: {analysis['F_rms']:.6f}")
        
        # Check progress toward targets
        if analysis['keff_solar'] > 0:
            solar_ratio = analysis['keff_solar'] / 0.001  # Target = 0.001
            galactic_ratio = analysis['keff_galactic'] / 0.100  # Target = 0.100
            print(f"  Progress: Solar {solar_ratio:.1f}x, Galactic {galactic_ratio:.1f}x of target")
            
            # Success criteria
            if 0.5 <= solar_ratio <= 2.0 and 0.5 <= galactic_ratio <= 2.0:
                print("  🎯 WITHIN TARGET RANGE!")

find_optimal_stiffness()
