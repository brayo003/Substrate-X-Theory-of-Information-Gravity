#!/usr/bin/env python3
"""
BRIDGE WITH MASS/ENERGY CONTRIBUTION
Growth rate r depends on actual mass/energy at scale
"""
import numpy as np

print("="*80)
print("BRIDGE WITH MASS-ENERGY SCALING")
print("="*80)

c = 299792458.0
G = 6.67430e-11
ħ = 1.054571817e-34
Lp = np.sqrt(ħ * G / c**3)
ρp = c**5 / (ħ * G**2)

class MassScaledBridge:
    def __init__(self, scale_L, mass_M=0):
        """
        scale_L: Characteristic length [m]
        mass_M: Mass contained within scale [kg] (0 for vacuum)
        """
        self.L = scale_L
        self.M = mass_M
        self.Lp = Lp
        
        # V12 parameters
        self.a = 1.0
        self.b = 1.0
        
    def calculate_growth_rate(self):
        """Growth rate from total energy density"""
        # Vacuum energy density
        ρ_vac = ħ * c / (self.L**4)
        
        # Matter energy density (if mass given)
        if self.M > 0:
            volume = (4/3) * np.pi * self.L**3
            ρ_matter = self.M / volume * c**2  # E = mc²
        else:
            ρ_matter = 0
        
        # Total effective density
        ρ_total = ρ_vac + ρ_matter
        
        # Normalize and calculate r
        ρ_ratio = ρ_total / ρp
        
        # Different scaling: r = 0.153 * tanh(ρ_ratio)
        # This saturates at 0.153 for high density
        return 0.153 * np.tanh(ρ_ratio**0.25)
    
    def equilibrium_tension(self):
        r = self.calculate_growth_rate()
        discriminant = self.a**2 + 4 * self.b * r
        
        if discriminant >= 0:
            x1 = (self.a + np.sqrt(discriminant)) / (2 * self.b)
            return max(x1, 0.0)
        return 0.0

# Test: Vacuum only
print("\n1. VACUUM ONLY (no mass):")
print(f"{'Scale':<20} {'L (m)':<12} {'r':<12} {'x':<12}")
print("-" * 60)

for name, L in [("Planck", Lp), ("1fm", 1e-15), ("Solar BH", 2954.0)]:
    bridge = MassScaledBridge(L, mass_M=0)
    r = bridge.calculate_growth_rate()
    x = bridge.equilibrium_tension()
    print(f"{name:<20} {L:<12.1e} {r:<12.6f} {x:<12.6f}")

# Test: With solar mass at Schwarzschild radius
print(f"\n2. WITH SOLAR MASS AT SCHWARZSCHILD RADIUS:")
M_sun = 1.989e30
R_s = 2 * G * M_sun / c**2

bridge = MassScaledBridge(R_s, mass_M=M_sun)
r = bridge.calculate_growth_rate()
x = bridge.equilibrium_tension()

print(f"   Scale: R_s = {R_s:.2f} m")
print(f"   Mass: M = {M_sun:.3e} kg")
print(f"   Growth rate: r = {r:.6f}")
print(f"   Tension: x = {x:.6f}")

# What tension do we need for black hole?
print(f"\n3. BLACK HOLE CONDITION:")
print(f"   For a black hole, we want x ≈ 1.0")
print(f"   Current x = {x:.6f}")
print(f"   To get x = 1.0, we need r such that:")
print(f"   1.0 = (1 + √(1 + 4r))/2")
print(f"   → r = (2*1.0 - 1)² - 1 = 0")
print(f"   Wait, that gives r = 0 for x = 1.0!")

# Check the math
print(f"\n4. CHECK THE MATH:")
print(f"   Equation: r·x + x² - x³ = 0 at equilibrium")
print(f"   For x = 1.0: r·1 + 1 - 1 = 0 → r = 0")
print(f"   So black hole (x=1) requires r = 0!")
print(f"   This is strange - it means black holes are at zero growth rate?")

print(f"\n" + "="*80)
print(f"MATHEMATICAL INSIGHT:")
print(f"   The V12 equation has fixed points at x=0 and x=(1 ± √(1+4r))/2")
print(f"   For r=0: x=0 (unstable) and x=1 (stable)")
print(f"   So black hole (x=1) is the STABLE fixed point at r=0")
print(f"   This makes sense: black holes are stable endpoints!")
print(f"="*80)
