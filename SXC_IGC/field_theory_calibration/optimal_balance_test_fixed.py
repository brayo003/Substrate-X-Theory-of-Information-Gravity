#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class OptimalBalanceSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, delta1=15.0, delta2=1.0, **kwargs):
        
        # 1. Initialize base class (may set internal defaults for delta1/2)
        super().__init__(**kwargs) 
        
        # 2. FIX: OVERRIDE base class attributes with custom values
        self.delta1 = delta1 # Set Intermediate Source Strength (40% reduction from 25.0)
        self.delta2 = delta2 # Boost E -> F coupling (3.3x from 0.3)

        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        
        print(f"🎯 GOLDILOCKS SOLVER: M={M_factor:.0f}, η_power={eta_power:.1f}")
        print(f"    FIXED Sourcing: δ₁={self.delta1:.1f}, Boosted Coupling: δ₂={self.delta2:.1f}")
        print(f"    Target: Maintain ρ > 0.8 AND achieve scale separation.")
        
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
            # The field evolution depends on self.delta1/2 which are now correctly set
            dF_dt = dF_dt + (alpha_eff - self.alpha) * F
            
        return dE_dt, dF_dt

def comprehensive_fourier_analysis(solver):
    """Detailed Fourier analysis with multiple k-ranges"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 COMPREHENSIVE FOURIER ANALYSIS")
    print("=" * 50)
    
    # Check ρ health
    print(f"ρ max: {np.max(rho):.3f} (Required >0.8: {'✅' if np.max(rho) > 0.8 else '❌'})")
    
    F_rms = np.sqrt(np.mean(F**2))
    print(f"Field RMS: {F_rms:.3f} (Target: < 100)")
    
    # 2D Fourier analysis
    fft2 = np.fft.fft2(F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = F.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    k_magnitude = np.sqrt(kx**2 + ky**2)
    
    # Define scale ranges
    solar_k_high = (k_magnitude > 10) & (k_magnitude < 50)     # Solar scales
    intermediate_k = (k_magnitude > 2) & (k_magnitude < 10) # Intermediate
    galactic_k_low = (k_magnitude > 0.1) & (k_magnitude < 2)   # Galactic scales
    
    total_energy = np.sum(power_spectrum[k_magnitude > 0])
    
    if total_energy > 0:
        solar_frac = np.sum(power_spectrum[solar_k_high]) / total_energy
        intermediate_frac = np.sum(power_spectrum[intermediate_k]) / total_energy
        galactic_frac = np.sum(power_spectrum[galactic_k_low]) / total_energy
        
        print(f"Solar k (10-50): {solar_frac:.1%}")
        print(f"Intermediate k (2-10): {intermediate_frac:.1%}")
        print(f"Galactic k (0.1-2): {galactic_frac:.1%}")
        
        if F_rms < 100 and galactic_frac > 0.1 and solar_frac > 0.4:
             print("💫 SUCCESS: Scale separation achieved!")
             scale_ratio = solar_frac / galactic_frac
             print(f"Solar/Galactic Energy Ratio: {scale_ratio:.1f}x (Target: Maximize)")
        elif F_rms < 100 and galactic_frac > 0.05:
            print("🔬 PROGRESS: Galactic scales detected, ratio needs improvement.")
        else:
            print("⚠️ Scale separation failed or energy too high.")
    
    return {'F_rms': F_rms, 'galactic_frac': galactic_frac if 'galactic_frac' in locals() else 0}

print("🚀 OPTIMAL BALANCE TEST (FIXED PARAMETERS)")
print("δ₁=15.0, δ₂=1.0, η_power=20.0, M=10000")
print("Target: Stability + Stiffness Activation + Scale Separation")
print("=" * 70)

# Create solver with fixed parameters
solver = OptimalBalanceSolver(
    alpha=1e-5,
    delta1=15.0,  # Intermediate Source
    delta2=1.0,   # Boosted Coupling
    M_factor=10000.0,
    eta_power=20.0,
    rho_cutoff=0.8
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution with fixed parameters...")
solver.evolve_system(500)

print("\nEvolution complete! Analyzing scale distribution...")
results = comprehensive_fourier_analysis(solver)

print(f"\n💫 TEST COMPLETE")
if results.get('F_rms', 0) < 100 and results.get('galactic_frac', 0) > 0.05:
    print("SUCCESS: Parameters found for stable scale separation.")
else:
    print("Further parameter tuning needed.")
