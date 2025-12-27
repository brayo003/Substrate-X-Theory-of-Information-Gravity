#!/usr/bin/env python3
"""
Find exact conditions that cause explosion
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

print("💥 EXPLOSION CONDITION TEST")
print("What triggers the field explosion?")
print("=" * 50)

# Test different grid sizes with original explosive parameters
grid_sizes = [20, 32, 40, 64]
explosion_results = {}

for size in grid_sizes:
    print(f"\n🔍 Testing grid_size = {size}")
    
    engine = create_robust_engine(
        'general',
        grid_size=size,
        M_factor=8000,
        rho_cutoff=0.25,
        delta1=1.2,
        delta2=0.8,
        cubic_damping=0.2,
        dt=0.001
    )
    
    engine.initialize_gaussian(amplitude=0.6, sigma=0.15)
    
    # Evolve and monitor
    exploded = False
    for step in range(50):
        engine.evolve(1)
        ρ_max = np.max(engine.rho)
        
        if ρ_max > 1000:
            exploded = True
            explosion_step = step
            break
    
    explosion_results[size] = {
        'exploded': exploded,
        'explosion_step': explosion_step if exploded else None,
        'final_ρ_max': np.max(engine.rho),
        'stiffness_active': np.max(engine.rho) > engine.rho_cutoff
    }
    
    status = "💥 EXPLODED" if exploded else "✅ STABLE"
    print(f"   Result: {status}")
    if exploded:
        print(f"   Exploded at step {explosion_step}")
    print(f"   Final ρ_max: {np.max(engine.rho):.1f}")
    print(f"   Stiffness active: {explosion_results[size]['stiffness_active']}")

print(f"\n📊 EXPLOSION ANALYSIS:")
print("Grid Size | Exploded | Step | Stiffness Active")
print("-" * 45)
for size in grid_sizes:
    result = explosion_results[size]
    exploded = "YES" if result['exploded'] else "NO"
    step = result['explosion_step'] if result['exploded'] else "N/A"
    stiffness = "YES" if result['stiffness_active'] else "NO"
    print(f"{size:9} | {exploded:8} | {step:4} | {stiffness:15}")

# Find the pattern
exploding_sizes = [size for size in grid_sizes if explosion_results[size]['exploded']]
stable_sizes = [size for size in grid_sizes if not explosion_results[size]['exploded']]

if exploding_sizes:
    print(f"\n🚨 EXPLOSION THRESHOLD: Grids larger than {min(exploding_sizes)} explode")
    print("This suggests numerical instability scales with system size")
