#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class ReducedSourceSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, delta1=10.0, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        self.delta1 = delta1  # Override the source coupling
        
        print(f"🔧 REDUCED SOURCE SOLVER: M={M_factor:.0f}, δ₁={delta1:.1f}")
        print(f"   60% reduction in field sourcing from high-density regions")
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

def comprehensive_fourier_analysis(solver):
    """Detailed Fourier analysis with multiple k-ranges"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 COMPREHENSIVE FOURIER ANALYSIS")
    print("=" * 50)
    
    # Basic field stats first
    F_rms = np.sqrt(np.mean(F**2))
    print(f"Field RMS: {F_rms:.3f} (Target: much lower than 220)")
    
    # 2D Fourier analysis
    fft2 = np.fft.fft2(F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = F.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    kx_grid, ky_grid = np.meshgrid(kx, ky)
    k_magnitude = np.sqrt(kx_grid**2 + ky_grid**2)
    
    # Define multiple scale ranges
    ultra_high_k = (k_magnitude > 50) & (k_magnitude < 200)  # Fine structure
    solar_k = (k_magnitude > 10) & (k_magnitude < 50)        # Solar scales
    intermediate_k = (k_magnitude > 2) & (k_magnitude < 10)  # Intermediate
    galactic_k = (k_magnitude > 0.1) & (k_magnitude < 2)     # Galactic scales
    ultra_low_k = (k_magnitude > 0) & (k_magnitude < 0.1)    # Very large scales
    
    # Calculate energy fractions
    total_energy = np.sum(power_spectrum[k_magnitude > 0])
    
    if total_energy > 0:
        ultra_high_frac = np.sum(power_spectrum[ultra_high_k]) / total_energy
        solar_frac = np.sum(power_spectrum[solar_k]) / total_energy
        intermediate_frac = np.sum(power_spectrum[intermediate_k]) / total_energy
        galactic_frac = np.sum(power_spectrum[galactic_k]) / total_energy
        ultra_low_frac = np.sum(power_spectrum[ultra_low_k]) / total_energy
        
        print(f"Ultra-high k (50-200): {ultra_high_frac:.1%}")
        print(f"Solar k (10-50): {solar_frac:.1%}")
        print(f"Intermediate k (2-10): {intermediate_frac:.1%}")
        print(f"Galactic k (0.1-2): {galactic_frac:.1%}")
        print(f"Ultra-low k (0-0.1): {ultra_low_frac:.1%}")
        
        # Success criteria
        if galactic_frac > 0.05:
            print("💫 SUCCESS: Galactic scales detected!")
            scale_ratio = solar_frac / galactic_frac if galactic_frac > 0 else 0
            print(f"Solar/Galactic energy ratio: {scale_ratio:.1f}x")
        elif intermediate_frac > 0.1:
            print("🔬 PROGRESS: Intermediate scales emerging")
        else:
            print("⚠️  Galactic scales still too weak")
        
        # Check if field energy reduced
        if F_rms < 50:
            print("✅ Field energy significantly reduced")
        elif F_rms < 100:
            print("⚠️  Moderate field energy reduction")
        else:
            print("❌ Field energy still too high")
    
    return {
        'F_rms': F_rms,
        'galactic_frac': galactic_frac if 'galactic_frac' in locals() else 0,
        'solar_frac': solar_frac if 'solar_frac' in locals() else 0
    }

print("🚀 δ₁ REDUCTION TEST")
print("M=10000, δ₁=10.0 (60% source reduction)")
print("Target: Lower field energy, preserve galactic scales")
print("=" * 70)

# Create reduced-source solver
solver = ReducedSourceSolver(
    alpha=1e-5,
    delta1=10.0,  # CRITICAL: 60% reduction in source coupling
    M_factor=10000.0,
    eta_power=20.0,
    rho_cutoff=0.8
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution with reduced sourcing...")
solver.evolve_system(500)

print("\nEvolution complete! Analyzing scale distribution...")
results = comprehensive_fourier_analysis(solver)

print(f"\n💫 δ₁ TEST COMPLETE")
if results.get('galactic_frac', 0) > 0.05 and results.get('F_rms', 0) < 100:
    print("SUCCESS: Reduced sourcing enabled scale separation!")
else:
    print("Further parameter optimization needed.")
