#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class StabilizedSurgicalSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, dt=1e-6, **kwargs):
        # Pass all other arguments to the parent constructor
        super().__init__(**kwargs)
        
        # FIX: Set dt AFTER calling super().__init__ if parent doesn't accept 'dt'
        self.dt = dt
        
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        # Critical diagnostic for verification
        if M_factor > 0:
            self.alpha_eff_max = self.alpha * (1.0 + M_factor)
        else:
            self.alpha_eff_max = self.alpha
        
        print(f"🔧 STABILIZED SURGICAL SOLVER: M={M_factor:.0f}, α_eff_max={self.alpha_eff_max:.3f}")
        print(f"    Reduced dt: {self.dt:.1e} (Stabilization factor: {self.dt/1e-8:.0f}x, assuming base dt is 1e-4)")
        print(f"    Surgical precision: η_power={eta_power}, ρ_cut={rho_cutoff}")
    
    def compute_effective_stiffness(self, rho):
        """Surgical stiffness: α_eff(ρ) = α × (1 + M × max(0, tanh(η_power × (ρ - ρ_cutoff))))"""
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

def clean_scale_analysis(solver):
    """Analysis focused on clean scale separation metrics"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 STABILIZED FIELD ANALYSIS")
    print("=" * 50)
    
    F_rms = np.sqrt(np.mean(F**2))
    F_max, F_min = np.max(F), np.min(F)
    
    print(f"F FIELD: max={F_max:.3f}, min={F_min:.3f}, RMS={F_rms:.3f}")
    
    # Radial profile analysis
    center = (solver.grid_size//2, solver.grid_size//2)
    y, x = np.ogrid[:solver.grid_size, :solver.grid_size]
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2).astype(int)
    
    radial_F = np.bincount(r.ravel(), F.ravel()) / np.bincount(r.ravel())
    
    print(f"\n📈 CLEAN RADIAL PROFILE (First 10 points):")
    print("r\tF(r)")
    for i in range(min(10, len(radial_F))):
        print(f"{i}\t{radial_F[i]:.6f}")
    
    # Stability assessment
    if F_max < 10.0 and F_min > -10.0:
        stability = "✅ STABLE"
    elif F_max < 100.0 and F_min > -100.0:
        stability = "⚠️ MODERATE" 
    else:
        stability = "❌ UNSTABLE"
    
    print(f"\n🎯 STABILITY ASSESSMENT: {stability}")
    print(f"Field range: [{F_min:.3f}, {F_max:.3f}]")
    
    # Scale separation from clean profile
    if len(radial_F) > 5 and abs(radial_F[0]) > 1e-10:
        short_scale = radial_F[0] / radial_F[2] if abs(radial_F[2]) > 1e-10 else np.nan
        long_scale = radial_F[2] / radial_F[5] if abs(radial_F[5]) > 1e-10 else np.nan
        
        print(f"Short-scale (r=0→2): {short_scale:.1f}x")
        print(f"Long-scale (r=2→5): {long_scale:.1f}x")
        
        if short_scale > 10 and long_scale < 5:
            print("💫 CLEAN SCALE SEPARATION DETECTED!")
    
    return {
        'F_rms': F_rms,
        'stability': stability
    }

print("🚀 STABILIZED DT EVOLUTION TEST")
print("M=10000, dt=1e-6, α_eff_max=0.10")
print("Target: Eliminate numerical artifacts, reveal true physics")
print("=" * 70)

# Create stabilized solver with reduced dt
solver = StabilizedSurgicalSolver(
    alpha=1e-5,
    delta1=25.0,
    M_factor=10000.0,
    eta_power=20.0,
    rho_cutoff=0.8,
    dt=1e-6 # Critical: 100x reduction for stability
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

# FIX: Removed print_interval from evolve_system
print("Running 500-step evolution with stabilized dt...")
solver.evolve_system(500) 

print("\nEvolution complete! Analyzing stabilized fields...")
results = clean_scale_analysis(solver)

print(f"\n💫 STABILIZED EVOLUTION COMPLETE")
if results['stability'] == "✅ STABLE":
    print("Numerical stability achieved! Ready for Fourier analysis.")
else:
    print("Numerical issues persist. May need further dt reduction or M dampening.")
