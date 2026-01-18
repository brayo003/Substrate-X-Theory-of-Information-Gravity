#!/usr/bin/env python3
import numpy as np
from complete_field_theory_solver_fixed import CompleteFieldTheorySolver

class SimpleEtaSolver(CompleteFieldTheorySolver):
    def __init__(self, eta=0.0, **kwargs):
        super().__init__(**kwargs)
        self.eta = eta
    
    def compute_energy_density(self, rho, E, F):
        energy = super().compute_energy_density(rho, E, F)
        if self.eta != 0:
            grad_x = np.gradient(rho, self.dx, axis=0)
            grad_y = np.gradient(rho, self.dx, axis=1)
            grad_mag = np.sqrt(grad_x**2 + grad_y**2)
            energy *= (1.0 + self.eta * grad_mag**2)
        return energy

print("🎯 SYSTEMATIC η TUNING TEST")
print("Target: Galactic ×22 boost, Solar ×4.5 reduction")
print("=" * 60)

# Test different η values
eta_values = [0.0, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
baseline_galactic = None
baseline_solar = None

for eta in eta_values:
    print(f"\n🔧 Testing η = {eta}")
    print("-" * 30)
    
    solver = SimpleEtaSolver(alpha=1e-5, delta1=25.0, eta=eta)
    solver.initialize_system('gaussian')
    solver.evolve_system(40, verbose=False)  # CORRECT: evolve_system
    
    analysis = solver.compute_diagnostics()  # CORRECT: compute_diagnostics
    galactic = analysis['keff_galactic']
    solar = analysis['keff_solar']
    
    # Store baseline for comparison
    if eta == 0.0:
        baseline_galactic = galactic
        baseline_solar = solar
    
    # Calculate improvements relative to baseline
    if baseline_galactic and baseline_solar:
        galactic_boost = galactic / baseline_galactic
        solar_reduction = solar / baseline_solar
    else:
        galactic_boost = 1.0
        solar_reduction = 1.0
    
    print(f"   Galactic: {galactic:.6f} ({galactic_boost:.1f}x)")
    print(f"   Solar:    {solar:.6f} ({solar_reduction:.1f}x)")
    print(f"   G/S Ratio: {galactic/solar:.1f}")
    
    # Check if we're getting closer to targets
    if eta > 0:
        progress_galactic = (galactic_boost - 1.0) / 21.0 * 100  # 21x needed from baseline
        progress_solar = (1.0 - solar_reduction) / 0.78 * 100   # 0.78 reduction needed
        print(f"   Progress: Galactic {progress_galactic:.1f}%, Solar {progress_solar:.1f}%")

print(f"\n📈 BASELINE (η=0): Galactic={baseline_galactic:.6f}, Solar={baseline_solar:.6f}")
