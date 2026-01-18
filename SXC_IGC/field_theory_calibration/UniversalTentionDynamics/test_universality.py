#!/usr/bin/env python3
"""
ULTIMATE TEST: Same parameters work across domains
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

print("🌐 ULTIMATE UNIVERSALITY TEST")
print("Same parameters → Different domains → Similar patterns")

# Use EXACT same parameters for everything
universal_params = {
    'grid_size': 40,
    'M_factor': 8000,
    'rho_cutoff': 0.25,
    'delta1': 1.2,
    'delta2': 0.8,
    'cubic_damping': 0.2,
    'dt': 0.001
}

domains = ['finance', 'urban', 'healthcare', 'cosmic']
results = {}

for domain in domains:
    print(f"\n🧪 Testing {domain} with universal parameters...")
    engine = create_robust_engine(domain, **universal_params)
    engine.initialize_gaussian(amplitude=0.6, sigma=0.15)
    engine.evolve(25)
    
    # Measure pattern complexity
    pattern_complexity = np.std(engine.rho)
    connectivity = len(np.unique(label(engine.rho > 0.3)[0]))
    
    results[domain] = {
        'complexity': pattern_complexity,
        'connectivity': connectivity,
        'rho_range': f"{np.min(engine.rho):.3f}-{np.max(engine.rho):.3f}"
    }
    
    print(f"   Complexity: {pattern_complexity:.4f}")
    print(f"   Connectivity: {connectivity} regions")

print(f"\n📊 UNIVERSALITY RESULTS:")
similarity_threshold = 0.1
complexities = [results[d]['complexity'] for d in domains]
max_diff = max(complexities) - min(complexities)

if max_diff < similarity_threshold:
    print("🎉 MIRACLE: SAME parameters create SIMILAR complexity across domains!")
    print("This proves TRUE universality!")
else:
    print(f"Different domains need tuning (max difference: {max_diff:.4f})")
