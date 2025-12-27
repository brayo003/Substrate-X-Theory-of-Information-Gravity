#!/usr/bin/env python3
"""
Test M_factor sensitivity with PROPER ρ_cutoff to activate stiffness
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')

from universal_dynamics_robust import create_robust_engine
import numpy as np

print("🎯 M_FACTOR SENSITIVITY TEST - FIXED")
print("Testing with ρ_cutoff = 0.3 to ensure stiffness activation")
print("=" * 50)

M_values = [0, 100, 1000, 10000, 100000]
rho_cutoff = 0.3  # LOW enough to activate stiffness with initial ρ_max=0.5
results = {}

for M in M_values:
    print(f"\n🧪 Testing M_factor = {M}, ρ_cutoff = {rho_cutoff}")
    
    engine = create_robust_engine(
        'general', 
        grid_size=32,
        M_factor=M,
        rho_cutoff=rho_cutoff,  # KEY FIX: Lower cutoff
        dt=0.001,
        cubic_damping=0.2
    )
    
    engine.initialize_gaussian(amplitude=0.5, sigma=0.2)
    
    # Check initial stiffness state
    initial_stiffness = np.max(engine.rho) > engine.rho_cutoff
    print(f"   Initial: ρ_max={np.max(engine.rho):.3f}, stiffness_active={initial_stiffness}")
    
    # Evolve and track results
    initial_rho = engine.rho.copy()
    initial_structure = np.std(initial_rho)
    
    engine.evolve(20)  # Longer evolution to see effects
    
    final_rho = engine.rho.copy()
    final_structure = np.std(final_rho)
    
    # Calculate changes
    rho_change = np.mean(final_rho - initial_rho)
    structure_change = final_structure - initial_structure
    final_stiffness_active = np.max(final_rho) > engine.rho_cutoff
    
    results[M] = {
        'rho_change': rho_change,
        'structure_change': structure_change,
        'final_structure': final_structure,
        'final_rho_max': np.max(final_rho),
        'final_rho_min': np.min(final_rho),
        'stiffness_active_initial': initial_stiffness,
        'stiffness_active_final': final_stiffness_active,
        'effective_stiffness_used': M > 0 and final_stiffness_active
    }
    
    print(f"   Final: ρ_max={np.max(final_rho):.3f}, stiffness_active={final_stiffness_active}")
    print(f"   ρ change: {rho_change:+.6f}")
    print(f"   Structure change: {structure_change:+.6f}")
    print(f"   Effective stiffness used: {results[M]['effective_stiffness_used']}")

print(f"\n📊 M_FACTOR SENSITIVITY RESULTS (ρ_cutoff={rho_cutoff}):")
print("M_value | ρ_change | Structure_Change | Stiffness_Used")
print("-" * 55)

for M in M_values:
    result = results[M]
    stiffness_indicator = "✓" if result['effective_stiffness_used'] else "✗"
    print(f"{M:7} | {result['rho_change']:+.4f}  | {result['structure_change']:+.4f}        | {stiffness_indicator}")

# Analyze sensitivity
structure_changes = [results[M]['structure_change'] for M in M_values]
max_change = max(structure_changes)
min_change = min(structure_changes)
sensitivity_range = max_change - min_change

print(f"\n🔍 SENSITIVITY ANALYSIS:")
print(f"   Structure change range: {min_change:.4f} to {max_change:.4f}")
print(f"   Total sensitivity range: {sensitivity_range:.4f}")

if sensitivity_range > 0.01:  # Meaningful difference threshold
    print("✅ SUCCESS: M_factor sensitivity is WORKING!")
    print(f"   Stiffness mechanism creates {sensitivity_range:.4f} variation in structure formation")
    
    # Check if higher M creates more structure (as expected)
    if M_values[-1] > 0 and results[M_values[-1]]['structure_change'] > results[0]['structure_change']:
        print("✅ Higher M_factor increases structure formation (as expected)")
    else:
        print("⚠️  Unexpected: Higher M_factor doesn't increase structure")
else:
    print("❌ WARNING: Limited M_factor sensitivity")
    print("   May need further parameter tuning")

# Test stiffness activation statistics
stiffness_activated_count = sum(1 for M in M_values if results[M]['effective_stiffness_used'])
print(f"\n🔄 STIFFNESS ACTIVATION:")
print(f"   Stiffness activated in {stiffness_activated_count}/{len(M_values)} cases")
print(f"   ρ_cutoff = {rho_cutoff} was appropriate: {stiffness_activated_count > 0}")

print("\n🎯 M_factor sensitivity test with proper ρ_cutoff complete!")
