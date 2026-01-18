#!/usr/bin/env python3
"""
Test saturation hypothesis with spacecraft data
"""

import numpy as np

print("="*60)
print("TESTING SATURATION HYPOTHESIS")
print("="*60)

# Saturation model
def eta_saturation(rho, eta_max=0.1, rho_sat=1e-16, b=1.0):
    """η = η_max * [ρ/(ρ + ρ_sat)]^b"""
    return eta_max * (rho / (rho + rho_sat))**b

# Environments and their approximate densities
environments = {
    "Deep Cosmic Void": 1e-30,
    "Cosmic Web Filament": 1e-26,
    "LIGO Path (void)": 1e-27,
    "Galactic Halo": 1e-24,
    "Interstellar Medium": 1e-21,
    "Galactic Disk (Pulsar)": 1e-21,
    "Solar Neighborhood": 1e-20,
    "Outer Solar System": 1e-18,
    "Inner Solar System": 1e-17,
    "Pioneer Region": 1.4e-16,
    "Earth Orbit": 1e-16,
    "Near Earth": 1e-15,
    "Planetary Atmosphere": 1e-10,
    "Laboratory (STP)": 1.2e3,
}

print("\nPredicted viscosities with saturation:")
print("="*50)
print(f"{'Environment':25} {'Density (kg/m³)':20} {'η (predicted)':15}")
print("-"*60)

for env, rho in environments.items():
    eta = eta_saturation(rho)
    
    # Format output
    if eta > 0.01:
        eta_str = f"{eta:.4f}"
    elif eta > 1e-10:
        eta_str = f"{eta:.2e}"
    else:
        eta_str = f"{eta:.1e}"
    
    print(f"{env:25} {rho:20.1e} {eta_str:>15}")

print("\n" + "="*60)
print("KEY OBSERVATIONS:")
print("="*60)

# Calculate ratios
eta_void = eta_saturation(1e-30)
eta_pioneer = eta_saturation(1.4e-16)
eta_lab = eta_saturation(1.2e3)

print(f"1. Void (ρ=1e-30) → Pioneer (ρ=1.4e-16):")
print(f"   Density ratio: {1.4e-16/1e-30:.1e}")
print(f"   η ratio: {eta_pioneer/eta_void:.1f}")
print(f"   → Density increases 1.4e14×, η only {eta_pioneer/eta_void:.1f}×")

print(f"\n2. Pioneer → Lab (ρ=1.2e3):")
print(f"   Density ratio: {1.2e3/1.4e-16:.1e}")
print(f"   η ratio: {eta_lab/eta_pioneer:.3f}")
print(f"   → Density increases 8.6e18×, η only {eta_lab/eta_pioneer:.3f}×")

print(f"\n3. Saturation point:")
rho_sat = 1e-16
eta_at_sat = eta_saturation(rho_sat)
eta_half_sat = eta_saturation(rho_sat/10)
print(f"   At ρ = ρ_sat = {rho_sat:.1e}: η = {eta_at_sat:.4f}")
print(f"   At ρ = ρ_sat/10: η = {eta_half_sat:.4f} ({(eta_half_sat/eta_at_sat*100):.1f}% of max)")

print(f"\n4. TESTABLE PREDICTIONS:")
print(f"   a) Cassini at Saturn (ρ ≈ 1e-17) should find η ≈ {eta_saturation(1e-17):.4f}")
print(f"   b) Galileo at Jupiter (ρ ≈ 5e-17) should find η ≈ {eta_saturation(5e-17):.4f}")
print(f"   c) Different altitudes on Earth show LITTLE variation in η")
print(f"   d) Spacecraft leaving solar system: η DECREASES slowly beyond ~10 AU")

print(f"\n5. IMPLICATIONS FOR YOUR THEORY:")
print(f"   • Tension equation T = βE - γF must produce saturation")
print(f"   • Possibly: γ ∝ 1/(1 + ρ/ρ_sat) or similar")
print(f"   • Information capacity per volume is limited")
print("="*60)

# Save for your framework
with open('saturation_predictions.txt', 'w') as f:
    f.write("# SATURATION MODEL PREDICTIONS\n")
    f.write("# η(ρ) = 0.1 × [ρ/(ρ + 1e-16)]^1.0\n\n")
    f.write("Environment, Density_kg_m3, Predicted_eta\n")
    for env, rho in environments.items():
        eta = eta_saturation(rho)
        f.write(f"{env},{rho:.2e},{eta:.6e}\n")
    
    f.write(f"\n# Critical tests:\n")
    f.write(f"1. Cassini η should be ~{eta_saturation(1e-17):.4f}\n")
    f.write(f"2. η should be constant within solar system\n")
    f.write(f"3. Beyond ~30 AU, η should decrease noticeably\n")

print("\n✓ Predictions saved to 'saturation_predictions.txt'")
print("  Use this to test against spacecraft data!")
