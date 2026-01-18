#!/usr/bin/env python3
"""
DEEP DIVE: Why is urban different?
Not to fix, but to understand the urban physics
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np
import matplotlib.pyplot as plt

print("🏙️  DEEP URBAN ANALYSIS")
print("Understanding urban dynamics, not fixing them")
print("=" * 50)

# Test urban with detailed monitoring
print("Creating urban engine with default parameters...")
urban_engine = create_robust_engine('urban', grid_size=32)

print("\n📊 URBAN PARAMETERS:")
print(f"  M_factor: {urban_engine.M_factor}")
print(f"  dt: {urban_engine.dt}")
print(f"  cubic_damping: {urban_engine.cubic_damping}")
print(f"  rho_cutoff: {urban_engine.rho_cutoff}")
print(f"  delta1: {urban_engine.delta1}, delta2: {urban_engine.delta2}")

print("\n🧪 EVOLVING URBAN STEP-BY-STEP:")
urban_engine.initialize_gaussian(amplitude=0.5)

# Monitor evolution closely
for step in range(50):
    urban_engine.evolve_robust_imex()
    
    stats = urban_engine.get_field_statistics()
    
    if step % 5 == 0 or stats['rho_max'] > 10:
        print(f"Step {step:2d}: ρ_max={stats['rho_max']:12.3f} | "
              f"ρ_min={stats['rho_min']:8.3f} | "
              f"stiffness={stats['stiffness_active']} | "
              f"warnings={stats['stability_warnings']}")
        
        # Check for explosion conditions
        if stats['rho_max'] > 1000:
            print("💥 EXPLOSION DETECTED - analyzing fields...")
            print(f"  ρ range: [{np.min(urban_engine.rho):.3f}, {np.max(urban_engine.rho):.3f}]")
            print(f"  E range: [{np.min(urban_engine.E):.3f}, {np.max(urban_engine.E):.3f}]")
            print(f"  F range: [{np.min(urban_engine.F):.3f}, {np.max(urban_engine.F):.3f}]")
            
            # Check for NaN/inf
            if np.any(np.isnan(urban_engine.rho)):
                print("  ❌ NaN values in ρ!")
            if np.any(np.isinf(urban_engine.rho)):
                print("  ❌ Infinite values in ρ!")
                
            break

print(f"\n🔍 URBAN ANALYSIS COMPLETE")
print("Key question: Is this blowup PHYSICAL or NUMERICAL?")
print("Physical blowup = urban critical transition")
print("Numerical blowup = parameter mismatch")
