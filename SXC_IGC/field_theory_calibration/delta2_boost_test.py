#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class Delta2BoostSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, delta1=10.0, delta2=1.0, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        self.delta1 = delta1
        self.delta2 = delta2
        
        print(f"🚀 δ₂ BOOST SOLVER: M={M_factor:.0f}, η_power={eta_power}")
        print(f"   E→F coupling boost: δ₂={delta2:.1f} (3.3× increase)")
        print(f"   Stable base: δ₁={delta1:.1f}, ρ_cut={rho_cutoff}")
        
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

def enhanced_scale_analysis(solver):
    """Analysis focused on galactic scale detection"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 ENHANCED SCALE ANALYSIS")
    print("=" * 50)
    
    # Field health metrics
    rho_max = np.max(rho)
    F_rms = np.sqrt(np.mean(F**2))
    E_rms = np.sqrt(np.mean(E**2))
    
    print(f"ρ max: {rho_max:.3f} (Target: >0.8)")
    print(f"F RMS: {F_rms:.3f} (Indicator of field strength)")
    print(f"E RMS: {E_rms:.3f} (Driving field strength)")
    
    # Check field activation
    if rho_max > solver.rho_cutoff:
        print("✅ Stiffness: ACTIVE")
    else:
        print("❌ Stiffness: INACTIVE")
    
    # Fourier analysis with focus on low-k
    fft2 = np.fft.fft2(F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = F.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    kx_grid, ky_grid = np.meshgrid(kx, ky)
    k_magnitude = np.sqrt(kx_grid**2 + ky_grid**2)
    
    # Detailed scale bands with focus on galactic
    ultra_high_k = (k_magnitude > 100)
    very_high_k = (k_magnitude > 50) & (k_magnitude <= 100)
    high_k = (k_magnitude > 20) & (k_magnitude <= 50)
    medium_k = (k_magnitude > 5) & (k_magnitude <= 20)
    low_k = (k_magnitude > 1) & (k_magnitude <= 5)
    very_low_k = (k_magnitude > 0.1) & (k_magnitude <= 1)
    ultra_low_k = (k_magnitude > 0) & (k_magnitude <= 0.1)
    
    total_energy = np.sum(power_spectrum[k_magnitude > 0])
    
    if total_energy > 0:
        ultra_high_frac = np.sum(power_spectrum[ultra_high_k]) / total_energy
        very_high_frac = np.sum(power_spectrum[very_high_k]) / total_energy
        high_frac = np.sum(power_spectrum[high_k]) / total_energy
        medium_frac = np.sum(power_spectrum[medium_k]) / total_energy
        low_frac = np.sum(power_spectrum[low_k]) / total_energy
        very_low_frac = np.sum(power_spectrum[very_low_k]) / total_energy
        ultra_low_frac = np.sum(power_spectrum[ultra_low_k]) / total_energy
        
        print(f"\n📈 DETAILED SPECTRAL DISTRIBUTION:")
        print(f"Ultra-high k (>100): {ultra_high_frac:.3%}")
        print(f"Very high k (50-100): {very_high_frac:.3%}")
        print(f"High k (20-50): {high_frac:.3%}")
        print(f"Medium k (5-20): {medium_frac:.3%}")
        print(f"Low k (1-5): {low_frac:.3%}")
        print(f"Very low k (0.1-1): {very_low_frac:.3%}")
        print(f"Ultra-low k (0-0.1): {ultra_low_frac:.3%}")
        
        # Galactic scale detection (focus on low k)
        galactic_energy = low_frac + very_low_frac + ultra_low_frac
        solar_energy = ultra_high_frac + very_high_frac + high_frac
        
        print(f"\n🎯 GALACTIC SCALE DETECTION:")
        print(f"Solar scales (k>20): {solar_energy:.3%}")
        print(f"Galactic scales (k<5): {galactic_energy:.3%}")
        
        if galactic_energy > 0.01:  # 1% threshold for detection
            scale_ratio = solar_energy / galactic_energy if galactic_energy > 0 else 0
            print(f"Scale separation ratio: {scale_ratio:.1f}x")
            
            if galactic_energy > 0.05:
                print("💫 SUCCESS: Strong galactic scales detected!")
            elif galactic_energy > 0.02:
                print("🔬 PROGRESS: Galactic scales emerging")
            else:
                print("⚠️  Weak but detectable galactic scales")
        else:
            print("❌ No galactic scales detected")
    
    # Field range assessment
    F_max, F_min = np.max(F), np.min(F)
    F_range = F_max - F_min
    print(f"\n📍 FIELD RANGE: [{F_min:.3f}, {F_max:.3f}] (range: {F_range:.3f})")
    
    return {
        'rho_max': rho_max,
        'F_rms': F_rms,
        'galactic_energy': galactic_energy if 'galactic_energy' in locals() else 0,
        'solar_energy': solar_energy if 'solar_energy' in locals() else 0
    }

print("🚀 δ₂ BOOST TEST")
print("δ₂=1.0, δ₁=10.0, η_power=20.0, M=10000")
print("Target: Boost E→F coupling for galactic scale emergence")
print("=" * 70)

# Create δ₂-boosted solver
solver = Delta2BoostSolver(
    alpha=1e-5,
    delta1=10.0,   # Stable sourcing
    delta2=1.0,    # CRITICAL: 3.3× E→F coupling boost
    M_factor=10000.0,
    eta_power=20.0, # Stable sharpness
    rho_cutoff=0.8
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution with boosted E→F coupling...")
solver.evolve_system(500)

print("\nEvolution complete! Analyzing galactic scale emergence...")
results = enhanced_scale_analysis(solver)

print(f"\n💫 δ₂ BOOST TEST COMPLETE")
if results.get('galactic_energy', 0) > 0.02:
    print("SUCCESS: δ₂ boost created detectable galactic scales!")
else:
    print("δ₂ boost insufficient - may need further coupling increase.")
