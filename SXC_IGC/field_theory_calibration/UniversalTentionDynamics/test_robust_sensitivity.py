#!/usr/bin/env python3
"""
Test that different M_factor values now produce different results
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')

from universal_dynamics_robust import create_robust_engine
import numpy as np

print("🎯 TESTING M_FACTOR SENSITIVITY")
print("Different M values should produce different results")
print("=" * 50)

M_values = [0, 1000, 10000, 100000]
results = {}

for M in M_values:
    print(f"\n🧪 Testing M_factor = {M}")
    
    engine = create_robust_engine(
        'general', 
        grid_size=32,
        M_factor=M,
        rho_cutoff=0.3,
        dt=0.001
    )
    
    engine.initialize_gaussian(amplitude=0.5, sigma=0.2)
    
    # Evolve and track results
    initial_rho = engine.rho.copy()
    engine.evolve(15)
    final_rho = engine.rho.copy()
    
    # Calculate changes
    rho_change = np.mean(final_rho - initial_rho)
    structure_formation = np.std(final_rho)  # Higher = more structure
    
    results[M] = {
        'rho_change': rho_change,
        'structure_formation': structure_formation,
        'final_rho_max': np.max(final_rho),
        'final_rho_min': np.min(final_rho),
        'stiffness_active': np.max(final_rho) > engine.rho_cutoff
    }
    
    print(f"   ρ change: {rho_change:+.6f}")
    print(f"   Structure: {structure_formation:.6f}")
    print(f"   ρ range: [{np.min(final_rho):.3f}, {np.max(final_rho):.3f}]")
    print(f"   Stiffness active: {results[M]['stiffness_active']}")

print(f"\n📊 M_FACTOR SENSITIVITY RESULTS:")
print("M_value | ρ_change | Structure | Stiffness_Active")
print("-" * 50)

for M in M_values:
    result = results[M]
    print(f"{M:7} | {result['rho_change']:+.4f} | {result['structure_formation']:.4f} | {result['stiffness_active']}")

# Check if we have meaningful differences
structure_values = [results[M]['structure_formation'] for M in M_values]
max_structure = max(structure_values)
min_structure = min(structure_values)

if max_structure > min_structure * 1.5:  # At least 50% difference
    print("✅ SUCCESS: M_factor sensitivity working!")
    print(f"   Structure variation: {min_structure:.4f} → {max_structure:.4f}")
else:
    print("❌ WARNING: Limited M_factor sensitivity")
    print("   May need parameter tuning")

# Test positivity guarantee
print(f"\n🛡️  POSITIVITY VERIFICATION:")
all_positive = all(results[M]['final_rho_min'] >= -1e-10 for M in M_values)  # Allow small numerical error

if all_positive:
    print("✅ SUCCESS: All densities remain non-negative!")
else:
    negative_Ms = [M for M in M_values if results[M]['final_rho_min'] < -1e-10]
    print(f"❌ FAILURE: Negative densities for M = {negative_Ms}")

print("\n🎯 Robust engine test complete!")
