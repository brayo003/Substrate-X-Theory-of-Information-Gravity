#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class OptimalBalanceSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=50.0, rho_cutoff=0.8, delta1=15.0, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        self.delta1 = delta1
        
        print(f"🎯 OPTIMAL BALANCE SOLVER: M={M_factor:.0f}, η_power={eta_power}")
        print(f"   Intermediate sourcing: δ₁={delta1:.1f} (Goldilocks zone)")
        print(f"   Ultra-sharp precision: ρ_cut={rho_cutoff}")
        
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

def comprehensive_scale_analysis(solver):
    """Complete analysis of scale separation and field health"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 COMPREHENSIVE SCALE ANALYSIS")
    print("=" * 50)
    
    # Field health metrics
    rho_max = np.max(rho)
    F_rms = np.sqrt(np.mean(F**2))
    rho_E_corr = np.corrcoef(rho.flatten(), E.flatten())[0,1] if not np.isnan(np.corrcoef(rho.flatten(), E.flatten())[0,1]) else 0
    
    print(f"ρ max: {rho_max:.3f} (Need >0.8 to activate stiffness)")
    print(f"F RMS: {F_rms:.3f} (Target: 50-100 for balance)")
    print(f"ρ-E correlation: {rho_E_corr:.3f}")
    
    # Check if stiffness is activated
    if rho_max > solver.rho_cutoff:
        print("✅ Stiffness activation: ACTIVE")
    else:
        print("❌ Stiffness activation: INACTIVE (ρ too low)")
    
    # Fourier analysis for scale separation
    fft2 = np.fft.fft2(F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = F.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    kx_grid, ky_grid = np.meshgrid(kx, ky)
    k_magnitude = np.sqrt(kx_grid**2 + ky_grid**2)
    
    # Scale bands
    ultra_solar_k = (k_magnitude > 50) & (k_magnitude < 150)
    solar_k = (k_magnitude > 20) & (k_magnitude < 50)
    intermediate_k = (k_magnitude > 5) & (k_magnitude < 20)
    galactic_k = (k_magnitude > 0.5) & (k_magnitude < 5)
    large_scale_k = (k_magnitude > 0) & (k_magnitude < 0.5)
    
    total_energy = np.sum(power_spectrum[k_magnitude > 0])
    
    if total_energy > 0:
        ultra_solar_frac = np.sum(power_spectrum[ultra_solar_k]) / total_energy
        solar_frac = np.sum(power_spectrum[solar_k]) / total_energy
        intermediate_frac = np.sum(power_spectrum[intermediate_k]) / total_energy
        galactic_frac = np.sum(power_spectrum[galactic_k]) / total_energy
        large_scale_frac = np.sum(power_spectrum[large_scale_k]) / total_energy
        
        print(f"\n�� SPECTRAL ENERGY DISTRIBUTION:")
        print(f"Ultra-solar (50-150): {ultra_solar_frac:.1%}")
        print(f"Solar (20-50): {solar_frac:.1%}")
        print(f"Intermediate (5-20): {intermediate_frac:.1%}")
        print(f"Galactic (0.5-5): {galactic_frac:.1%}")
        print(f"Large-scale (0-0.5): {large_scale_frac:.1%}")
        
        # Scale separation assessment
        total_solar_like = ultra_solar_frac + solar_frac
        total_galactic_like = galactic_frac + large_scale_frac
        
        if total_galactic_like > 0:
            scale_ratio = total_solar_like / total_galactic_like
            print(f"\n🎯 SCALE SEPARATION RATIO: {scale_ratio:.1f}x")
            
            if scale_ratio > 10:
                print("💫 EXCELLENT scale separation!")
            elif scale_ratio > 5:
                print("🔬 GOOD scale separation")
            elif scale_ratio > 2:
                print("⚠️  MODERATE scale separation")
            else:
                print("❌ POOR scale separation")
        else:
            print("❌ No galactic scales detected")
    
    # Overall success criteria
    success = (rho_max > 0.8 and 
               50 <= F_rms <= 150 and 
               total_galactic_like > 0.05)
    
    return {
        'rho_max': rho_max,
        'F_rms': F_rms,
        'scale_ratio': scale_ratio if 'scale_ratio' in locals() else 0,
        'success': success
    }

print("🚀 OPTIMAL BALANCE TEST")
print("δ₁=15.0, η_power=50.0, M=10000")
print("Target: Balance field health with scale separation")
print("=" * 70)

# Create optimal balance solver
solver = OptimalBalanceSolver(
    alpha=1e-5,
    delta1=15.0,  # CRITICAL: Goldilocks sourcing
    M_factor=10000.0,
    eta_power=50.0,
    rho_cutoff=0.8
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution with balanced parameters...")
solver.evolve_system(500)

print("\nEvolution complete! Analyzing balance and scale separation...")
results = comprehensive_scale_analysis(solver)

print(f"\n💫 OPTIMAL BALANCE TEST COMPLETE")
if results['success']:
    print("🎉 SUCCESS: Perfect balance achieved!")
    print("Field health and scale separation both optimized!")
else:
    print("Balance not yet achieved - further tuning needed.")
