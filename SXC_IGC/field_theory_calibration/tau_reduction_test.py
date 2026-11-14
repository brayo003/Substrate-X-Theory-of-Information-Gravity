#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class LowDissipationSolver(CompleteFieldTheorySolver):
    def __init__(self, M_factor=10000.0, eta_power=20.0, rho_cutoff=0.8, tau_F=0.01, **kwargs):
        super().__init__(**kwargs)
        self.M_factor = M_factor
        self.eta_power = eta_power
        self.rho_cutoff = rho_cutoff
        self.tau_F = tau_F  # Override the dissipation parameter
        
        print(f"🔧 LOW DISSIPATION SOLVER: M={M_factor:.0f}, τ_F={tau_F:.3f}")
        print(f"   10× longer field persistence for galactic scales")
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

def fourier_peak_analysis(solver):
    """Simplified Fourier analysis focusing on scale separation"""
    rho, E, F = solver.rho, solver.E, solver.F
    
    print("\n📊 SIMPLIFIED FOURIER ANALYSIS")
    print("=" * 50)
    
    # Basic 2D Fourier analysis
    fft2 = np.fft.fft2(F)
    power_spectrum = np.abs(fft2)**2
    power_spectrum = np.fft.fftshift(power_spectrum)
    
    n = F.shape[0]
    kx = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    ky = np.fft.fftshift(np.fft.fftfreq(n, solver.dx)) * 2 * np.pi
    kx_grid, ky_grid = np.meshgrid(kx, ky)
    k_magnitude = np.sqrt(kx_grid**2 + ky_grid**2)
    
    # Analyze specific k-ranges
    solar_k_range = (k_magnitude > 20) & (k_magnitude < 100)   # High k - solar scales
    galactic_k_range = (k_magnitude > 0.1) & (k_magnitude < 5) # Low k - galactic scales
    
    solar_energy = np.sum(power_spectrum[solar_k_range])
    galactic_energy = np.sum(power_spectrum[galactic_k_range])
    total_energy = np.sum(power_spectrum[k_magnitude > 0])
    
    if total_energy > 0:
        solar_fraction = solar_energy / total_energy
        galactic_fraction = galactic_energy / total_energy
        
        print(f"Solar scales (k=20-100): {solar_fraction:.1%} of energy")
        print(f"Galactic scales (k=0.1-5): {galactic_fraction:.1%} of energy")
        
        if galactic_fraction > 0:
            scale_ratio = solar_fraction / galactic_fraction
            print(f"Scale energy ratio: {scale_ratio:.1f}x")
            
            if galactic_fraction > 0.1:  # At least 10% energy in galactic scales
                print("💫 SUCCESS: Galactic scales preserved!")
            elif galactic_fraction > 0.05:
                print("🔬 PROGRESS: Some galactic energy detected")
            else:
                print("⚠️  FAILED: Galactic scales too weak")
        else:
            print("❌ CRITICAL: No galactic scale energy detected")
    
    # Check if we have low-k power
    very_low_k = (k_magnitude > 0) & (k_magnitude < 1)
    very_low_energy = np.sum(power_spectrum[very_low_k])
    
    if very_low_energy > 0 and total_energy > 0:
        print(f"Very low-k (k<1): {very_low_energy/total_energy:.1%} of energy")
    
    return {
        'solar_fraction': solar_fraction if 'solar_fraction' in locals() else 0,
        'galactic_fraction': galactic_fraction if 'galactic_fraction' in locals() else 0
    }

print("🚀 τ_F REDUCTION TEST")
print("M=10000, τ_F=0.01 (10× longer field persistence)")
print("Target: Preserve galactic scales while crushing solar scales")
print("=" * 70)

# Create low-dissipation solver
solver = LowDissipationSolver(
    alpha=1e-5,
    delta1=25.0,
    M_factor=10000.0,
    eta_power=20.0,
    rho_cutoff=0.8,
    tau_F=0.01  # CRITICAL: 10× reduction in dissipation
)

print("\nInitializing Gaussian density profile...")
solver.initialize_system('gaussian')

print("Running 500-step evolution with reduced dissipation...")
solver.evolve_system(500)

print("\nEvolution complete! Analyzing scale preservation...")
results = fourier_peak_analysis(solver)

print(f"\n💫 τ_F TEST COMPLETE")
if results.get('galactic_fraction', 0) > 0.1:
    print("SUCCESS: Reduced dissipation preserved galactic scales!")
    print("Scale separation achieved!")
else:
    print("Galactic scales still too weak.")
    print("May need further parameter optimization.")
