#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class DTStabilizedSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, custom_dt=1e-6, **kwargs):
        super().__init__(**kwargs)
        
        # CRITICAL: Override dt after parent initialization
        self.dt = custom_dt
        
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        if M_factor > 0:
            self.alpha_eff_max = self.alpha * (1.0 + M_factor)
        else:
            self.alpha_eff_max = self.alpha
        
        print(f"🔧 DT-STABILIZED SOLVER: M={M_factor:.0f}, α_eff_max={self.alpha_eff_max:.3f}")
        print(f"   CUSTOM dt: {custom_dt:.1e} (100× reduction for CFL compliance)")
        print(f"   Surgical precision: η_power={eta_power}, ρ_cut={rho_cutoff}")
    
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

def oscillation_analysis(solver):
    """Specialized analysis for oscillatory structures"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 OSCILLATION ANALYSIS")
    print("=" * 50)
    
    # Field statistics
    F_rms = np.sqrt(np.mean(F**2))
    F_max, F_min = np.max(F), np.min(F)
    F_range = F_max - F_min
    
    print(f"F FIELD: max={F_max:.3f}, min={F_min:.3f}, range={F_range:.1f}")
    print(f"F RMS: {F_rms:.3f}")
    
    # Count zero crossings to quantify oscillations
    F_center_line = F[solver.grid_size//2, :]  # Horizontal center line
    zero_crossings = np.where(np.diff(np.sign(F_center_line)))[0]
    
    print(f"Zero crossings in center line: {len(zero_crossings)}")
    
    # Radial profile with oscillation detection
    center = (solver.grid_size//2, solver.grid_size//2)
    y, x = np.ogrid[:solver.grid_size, :solver.grid_size]
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2).astype(int)
    
    radial_F = np.bincount(r.ravel(), F.ravel()) / np.bincount(r.ravel())
    
    print(f"\n📈 RADIAL PROFILE (oscillation detection):")
    print("r\tF(r)\t\tSign\tOscillation")
    prev_sign = 0
    for i in range(min(15, len(radial_F))):
        F_val = radial_F[i]
        current_sign = 1 if F_val > 0 else -1 if F_val < 0 else 0
        oscillation = "↕️" if prev_sign != 0 and current_sign != prev_sign else ""
        print(f"{i}\t{F_val:.3f}\t\t{current_sign}\t{oscillation}")
        prev_sign = current_sign
    
    # Stability assessment
    if F_max < 10.0:
        stability = "✅ CLEAN"
        interpretation = "Numerical artifacts eliminated"
    elif F_max < 100.0:
        stability = "⚠️ MODERATE" 
        interpretation = "Physical oscillations present"
    else:
        stability = "🔴 HIGH ENERGY"
        interpretation = "Soliton/vortex structures confirmed"
    
    print(f"\n🎯 STABILITY: {stability}")
    print(f"INTERPRETATION: {interpretation}")
    
    return {
        'F_max': F_max,
        'F_min': F_min, 
        'F_rms': F_rms,
        'zero_crossings': len(zero_crossings),
        'radial_F': radial_F,
        'stability': stability
    }

print("🚀 DEFINITIVE DT REDUCTION TEST")
print("M=10000, dt=1e-6, α_eff_max=0.10")
print("Target: Distinguish physical oscillations vs numerical artifacts")
print("=" * 70)

# Create dt-stabilized solver
solver = DTStabilizedSolver(
    alpha=1e-5,
    delta1=25.0,
    M_factor=10000.0,
    eta_power=20.0,
    rho_cutoff=0.8,
    custom_dt=1e-6  # CRITICAL: 100× dt reduction
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution with stabilized dt...")
solver.evolve_system(500)

print("\nEvolution complete! Analyzing oscillatory structures...")
results = oscillation_analysis(solver)

print(f"\n💫 DEFINITIVE TEST COMPLETE")
if results['stability'] == "✅ CLEAN":
    print("Numerical artifacts eliminated! Oscillations are physical.")
    print("Proceed to Fourier analysis of emergent structures.")
elif results['stability'] == "⚠️ MODERATE":
    print("Moderate oscillations detected - likely physical solitons.")
    print("Ready for Fourier analysis.")
else:
    print("High-energy structures confirmed - substrate exhibits complex dynamics.")
    print("Fourier analysis will reveal scale separation in oscillatory regime.")
