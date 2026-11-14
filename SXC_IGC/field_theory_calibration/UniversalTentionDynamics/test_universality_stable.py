#!/usr/bin/env python3
"""
Test universality with STABLE parameters
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np
from scipy.ndimage import label

print("🌐 TRUE UNIVERSALITY TEST - STABLE VERSION")
print("Same parameters → Different domains → Similar BUT STABLE patterns")

# Use MORE CONSERVATIVE parameters
stable_params = {
    'grid_size': 32,
    'M_factor': 1000,      # Reduced stiffness
    'rho_cutoff': 0.3,
    'delta1': 0.3,         # Much weaker coupling
    'delta2': 0.2,         
    'cubic_damping': 0.5,  # Stronger damping
    'dt': 0.0001           # Smaller timestep
}

domains = ['finance', 'urban', 'healthcare', 'cosmic']
results = {}

for domain in domains:
    print(f"\n🧪 Testing {domain} with STABLE parameters...")
    engine = create_robust_engine(domain, **stable_params)
    engine.initialize_gaussian(amplitude=0.5, sigma=0.2)
    engine.evolve(30)
    
    # Measure pattern complexity
    pattern_complexity = np.std(engine.rho)
    labeled_array, num_regions = label(engine.rho > np.mean(engine.rho))
    
    results[domain] = {
        'complexity': pattern_complexity,
        'connectivity': num_regions,
        'rho_max': np.max(engine.rho),
        'rho_min': np.min(engine.rho)
    }
    
    print(f"   Complexity: {pattern_complexity:.4f}")
    print(f"   Connectivity: {num_regions} regions")
    print(f"   ρ range: [{np.min(engine.rho):.3f}, {np.max(engine.rho):.3f}]")

print(f"\n📊 STABLE UNIVERSALITY RESULTS:")
complexities = [results[d]['complexity'] for d in domains]
max_diff = max(complexities) - min(complexities)

print(f"Complexity range: {min(complexities):.4f} to {max(complexities):.4f}")
print(f"Maximum difference: {max_diff:.4f}")

similarity_threshold = 0.05
if max_diff < similarity_threshold:
    print("🎉 TRUE UNIVERSALITY: Same parameters → Similar stable patterns!")
else:
    print(f"❌ Domains behave differently (max difference: {max_diff:.4f})")

# Check if all fields stayed in reasonable range
all_stable = all(results[d]['rho_max'] < 10 for d in domains)
print(f"\n🛡️  STABILITY CHECK: All fields < 10 = {all_stable}")
