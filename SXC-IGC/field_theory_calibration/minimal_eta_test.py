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

# Test baseline vs η=10
print("Baseline (η=0):")
s1 = SimpleEtaSolver(alpha=1e-5, delta1=25.0, eta=0.0)
s1.initialize_system('gaussian')  # FIXED: initialize_system instead of initialize_fields
s1.evolve(30, verbose=False)
a1 = s1.analyze_field_properties()
print(f"Galactic: {a1['keff_galactic']:.6f}, Solar: {a1['keff_solar']:.6f}")

print("\nWith η=10:")
s2 = SimpleEtaSolver(alpha=1e-5, delta1=25.0, eta=10.0)
s2.initialize_system('gaussian')  # FIXED: initialize_system instead of initialize_fields
s2.evolve(30, verbose=False)
a2 = s2.analyze_field_properties()
print(f"Galactic: {a2['keff_galactic']:.6f}, Solar: {a2['keff_solar']:.6f}")

# Calculate improvements
galactic_boost = a2['keff_galactic'] / a1['keff_galactic'] if a1['keff_galactic'] > 0 else 0
solar_change = a2['keff_solar'] / a1['keff_solar'] if a1['keff_solar'] > 0 else 0

print(f"\n📊 Results:")
print(f"Galactic boost: {galactic_boost:.2f}x (need 22x)")
print(f"Solar change: {solar_change:.2f}x (need 0.22x)")
