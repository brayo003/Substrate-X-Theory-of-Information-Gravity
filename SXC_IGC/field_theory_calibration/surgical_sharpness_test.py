#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class UltraSharpSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=50.0, rho_cutoff=0.8, delta1=10.0, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        self.delta1 = delta1
        
        print(f"🔪 ULTRA-SHARP SURGICAL SOLVER: M={M_factor:.0f}, η_power={eta_power}")
        print(f"   2.5× sharper stiffness transition for concentrated solar energy")
        print(f"   Reduced sourcing: δ₁={delta1:.1f}, ρ_cut={rho_cutoff}")
        
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

def spectral_peak_analysis(solver):
    """Focus on spectral peak separation and concentration"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 SPECTRAL PEAK ANALYSIS")
    print("=" * 50)
    
    # Field energy assessment
    F_rms = np.sqrt(np.mean(F**2))
    print(f"Field RMS: {F_rms:.3f}")
    
    # 2D Fourier analysis
    fft2 = np.fft.fft2(F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = F.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    kx_grid, ky_grid = np.meshgrid(kx, ky)
    k_magnitude = np.sqrt(kx_grid**2 + ky_grid**2)
    
    # Define precise scale bands
    ultra_solar_k = (k_magnitude > 50) & (k_magnitude < 150)  # Target: concentrated solar
    solar_k = (k_magnitude > 20) & (k_magnitude < 50)         # Standard solar
    galactic_k = (k_magnitude > 0.5) & (k_magnitude < 5)      # Galactic scales
    large_scale_k = (k_magnitude > 0) & (k_magnitude < 0.5)   # Very large scales
    
    total_energy = np.sum(power_spectrum[k_magnitude > 0])
    
    if total_energy > 0:
        ultra_solar_frac = np.sum(power_spectrum[ultra_solar_k]) / total_energy
        solar_frac = np.sum(power_spectrum[solar_k]) / total_energy
        galactic_frac = np.sum(power_spectrum[galactic_k]) / total_energy
        large_scale_frac = np.sum(power_spectrum[large_scale_k]) / total_energy
        
        print(f"Ultra-solar k (50-150): {ultra_solar_frac:.1%}")
        print(f"Solar k (20-50): {solar_frac:.1%}")
        print(f"Galactic k (0.5-5): {galactic_frac:.1%}")
        print(f"Large-scale k (0-0.5): {large_scale_frac:.1%}")
        
        # Calculate concentration metrics
        total_solar_energy = ultra_solar_frac + solar_frac
        solar_concentration = ultra_solar_frac / total_solar_energy if total_solar_energy > 0 else 0
        
        print(f"\n🎯 SOLAR ENERGY CONCENTRATION: {solar_concentration:.1%} in ultra-high k")
        
        # Success criteria for sharp surgical effect
        if solar_concentration > 0.6:
            print("💫 SUCCESS: Solar energy highly concentrated!")
        elif solar_concentration > 0.4:
            print("🔬 PROGRESS: Good solar concentration")
        else:
            print("⚠️  Solar energy too spread out")
        
        # Scale separation assessment
        if galactic_frac > 0.05 and total_solar_energy > 0.3:
            scale_ratio = total_solar_energy / galactic_frac
            print(f"Solar/Galactic energy ratio: {scale_ratio:.1f}x")
            
            if scale_ratio > 5:
                print("💫 CLEAN SCALE SEPARATION ACHIEVED!")
        else:
            print("Scale separation needs improvement")
    
    # Radial field profile to check localization
    center = (solver.grid_size//2, solver.grid_size//2)
    y, x = np.ogrid[:solver.grid_size, :solver.grid_size]
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2).astype(int)
    radial_F = np.bincount(r.ravel(), F.ravel()) / np.bincount(r.ravel())
    
    if len(radial_F) > 5:
        center_edge_ratio = abs(radial_F[0] / radial_F[5]) if radial_F[5] != 0 else 0
        print(f"Center/Edge field ratio: {center_edge_ratio:.0f}x")
    
    return {
        'solar_concentration': solar_concentration if 'solar_concentration' in locals() else 0,
        'galactic_frac': galactic_frac if 'galactic_frac' in locals() else 0,
        'F_rms': F_rms
    }

print("🚀 ULTRA-SHARP SURGICAL TEST")
print("η_power=50.0, δ₁=10.0, M=10000")
print("Target: Concentrate solar energy into ultra-high k band")
print("=" * 70)

# Create ultra-sharp solver
solver = UltraSharpSolver(
    alpha=1e-5,
    delta1=10.0,
    M_factor=10000.0,
    eta_power=50.0,  # CRITICAL: 2.5× sharper transition
    rho_cutoff=0.8
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution with ultra-sharp stiffness...")
solver.evolve_system(500)

print("\nEvolution complete! Analyzing spectral concentration...")
results = spectral_peak_analysis(solver)

print(f"\n💫 ULTRA-SHARP TEST COMPLETE")
if results.get('solar_concentration', 0) > 0.6:
    print("SUCCESS: Solar energy highly concentrated at ultra-high k!")
    print("Ready for final scale separation assessment.")
else:
    print("Solar concentration needs further optimization.")
