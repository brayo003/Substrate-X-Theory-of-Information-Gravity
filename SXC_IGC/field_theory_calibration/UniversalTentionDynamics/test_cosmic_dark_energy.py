#!/usr/bin/env python3
"""
Investigate the negative density phenomenon - is this dark energy?
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')

from universal_dynamics import create_engine
import numpy as np
import matplotlib.pyplot as plt

print("🌌 DARK ENERGY INVESTIGATION")
print("=" * 50)

# Test different parameter regimes
test_cases = [
    {"name": "Standard Cosmic", "M_factor": 1e8, "rho_cutoff": 0.1},
    {"name": "Weak Stiffness", "M_factor": 1e4, "rho_cutoff": 0.1},
    {"name": "High Threshold", "M_factor": 1e8, "rho_cutoff": 0.5},
    {"name": "No Stiffness", "M_factor": 0, "rho_cutoff": 0.1}
]

for i, case in enumerate(test_cases):
    print(f"\n🧪 Test Case {i+1}: {case['name']}")
    
    engine = create_engine(
        grid_size=64,
        dt=1e6,
        M_factor=case["M_factor"],
        rho_cutoff=case["rho_cutoff"],
        alpha=1e-8,
        delta1=1e-7,
        delta2=1e-7,
        cubic_damping=0.3
    )
    
    engine.initialize_gaussian(amplitude=0.3, sigma=0.3)
    
    # Track density evolution
    initial_density = np.mean(engine.rho)
    
    engine.evolve(10)
    
    final_density = np.mean(engine.rho)
    density_change = final_density - initial_density
    
    print(f"   Initial ρ mean: {initial_density:.6f}")
    print(f"   Final ρ mean: {final_density:.6f}")
    print(f"   Density change: {density_change:+.6f}")
    
    # Analyze field signs
    rho_positive = np.sum(engine.rho > 0)
    rho_negative = np.sum(engine.rho < 0)
    total_cells = engine.rho.size
    
    print(f"   Positive cells: {rho_positive}/{total_cells} ({rho_positive/total_cells:.1%})")
    print(f"   Negative cells: {rho_negative}/{total_cells} ({rho_negative/total_cells:.1%})")
    
    if density_change < 0 and rho_negative > rho_positive:
        print("   🚨 STRONG NEGATIVE DENSITY EMERGENCE!")
    elif np.mean(engine.rho) < 0:
        print("   ⚠️  Overall negative density field")

# Now test if this creates expansion-like behavior
print(f"\n🌠 TESTING COSMIC EXPANSION EFFECTS")

expansion_engine = create_engine(
    grid_size=32,
    dt=1e5,
    M_factor=1e6,
    rho_cutoff=0.2,
    cubic_damping=0.1
)

# Initialize small dense region (early universe)
expansion_engine.initialize_gaussian(amplitude=1.0, sigma=0.1)

print("Initial state: Dense cosmic seed")
initial_size = np.sum(np.abs(expansion_engine.rho) > 0.01)
print(f"   High-density region size: {initial_size} cells")

print("Evolving 15 steps...")
for step in range(15):
    expansion_engine.evolve(1)
    
    if step % 5 == 0:
        current_size = np.sum(np.abs(expansion_engine.rho) > 0.01)
        expansion_factor = current_size / initial_size
        mean_density = np.mean(expansion_engine.rho)
        
        print(f"   Step {step}: Size = {current_size} cells (x{expansion_factor:.1f})")
        print(f"      Mean density: {mean_density:.6f}")

final_size = np.sum(np.abs(expansion_engine.rho) > 0.01)
final_expansion = final_size / initial_size

print(f"\n📈 FINAL EXPANSION FACTOR: {final_expansion:.1f}x")

if final_expansion > 1.2 and np.mean(expansion_engine.rho) < 0:
    print("💫 DARK ENERGY-LIKE BEHAVIOR DETECTED!")
    print("   Negative density + Expansion = Cosmic Acceleration")
elif final_expansion > 1:
    print("🌌 Expansion detected (but positive density)")
else:
    print("🌫️  No significant expansion")

print("\n🎯 Investigation complete!")
