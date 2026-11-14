#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class CalibratedSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=5000.0, eta_power=20.0, rho_cutoff=0.8, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        if M_factor > 0:
            self.alpha_eff_max = self.alpha * (1.0 + M_factor)
        else:
            self.alpha_eff_max = self.alpha
            
        print(f"🔧 DAMPENED SOLVER: M={M_factor:.0f}, α_eff_max={self.alpha_eff_max:.3f}")
        print(f"    Surgical precision: η_power={eta_power}, ρ_cut={rho_cutoff}")
            
    def compute_effective_stiffness(self, rho):
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

def analyze_final_state(solver):
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 FINAL STATE ANALYSIS")
    print("=" * 50)
    
    # Basic field statistics
    print(f"ρ: max={np.max(rho):.4f}, RMS={np.sqrt(np.mean(rho**2)):.4f}")
    print(f"F: max={np.max(F):.4f}, RMS={np.sqrt(np.mean(F**2)):.4f}")
    
    # Radial analysis
    center = (solver.grid_size//2, solver.grid_size//2)
    y, x = np.ogrid[:solver.grid_size, :solver.grid_size]
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2).astype(int)
    
    radial_rho = np.bincount(r.ravel(), rho.ravel()) / np.bincount(r.ravel())
    radial_F = np.bincount(r.ravel(), F.ravel()) / np.bincount(r.ravel())
    
    print(f"\n📈 RADIAL FIELD PROFILES (First 10 points):")
    print("r\tρ(r)\t\tF(r)\t\tρ/F Ratio")
    for i in range(min(11, len(radial_rho))):
        F_val = radial_F[i]
        ratio = radial_rho[i] / F_val if abs(F_val) > 1e-10 else 0
        print(f"{i}\t{radial_rho[i]:.6f}\t{F_val:.6f}\t{ratio:.2f}")

    # Scale separation metrics
    if len(radial_F) > 10:
        solar_compression = radial_F[0] / radial_F[3] if radial_F[3] != 0 else np.nan
        galactic_preservation = radial_F[10] / radial_F[0] if radial_F[0] != 0 else np.nan
        
        print(f"\n🎯 SCALE SEPARATION METRICS:")
        print(f"Solar compression (r=0→3): {solar_compression:.1f}x (Target: ~100x)")
        print(f"Galactic preservation (r=10/0): {galactic_preservation:.6f}")
        print(f"Center/Edge contrast: {abs(radial_F[0] / radial_F[-1]):.0f}x")

print("🚀 DAMPENED 500-STEP EVOLUTION TEST")
print("Target: Cleaner radial profile with strong scale separation")
print("======================================================================\n")

# Create and run the calibrated solver - FIXED: remove extra parameters
solver = CalibratedSolver(
    alpha=1e-5,
    delta1=25.0,
    M_factor=5000.0, # Dampened value
    eta_power=20.0,
    rho_cutoff=0.8
)

print("Initializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution...")
solver.evolve_system(500)  # FIXED: remove print_interval parameter

print("\nEvolution complete! Performing comprehensive analysis...")
analyze_final_state(solver)

print("\n💫 SIMULATION COMPLETE")
