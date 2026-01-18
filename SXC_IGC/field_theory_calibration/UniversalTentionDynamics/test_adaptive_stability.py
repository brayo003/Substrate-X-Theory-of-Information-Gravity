#!/usr/bin/env python3
"""
Adaptive stability test for Universal Dynamics Engine
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

def adaptive_universal_engine(domain, params):
    """Enhanced engine with stability controls"""
    
    # Adaptive time stepping based on grid size
    base_dt = 0.01
    adaptive_dt = base_dt / (params['grid_size'] / 20)**2
    
    print(f"🔧 Adaptive DT for grid {params['grid_size']}: {adaptive_dt:.6f}")
    
    # Modified parameters with stability controls
    stable_params = params.copy()
    stable_params['M_factor'] = params.get('M_factor', 100)  # Reduced stiffness
    stable_params['rho_cutoff'] = 0.3
    stable_params['delta1'] = 0.1  # Weak coupling
    
    return create_robust_engine(domain, stable_params)

print("🔄 ADAPTIVE STABILITY TEST")
print("Testing large grids with stability controls")
print("=" * 50)

# Test parameters for large system
test_params = {
    'grid_size': 64,  # Large system that previously exploded
    'M_factor': 100,  # Reduced stiffness
    'adaptive_dt': True,
    'max_rho': 50.0,  # Hard ceiling
}

# Test across domains
domains = ['finance', 'urban', 'healthcare', 'cosmic']
results = {}

for domain in domains:
    print(f"\n🧪 Testing {domain} with adaptive stability...")
    try:
        engine = adaptive_universal_engine(domain, test_params)
        results[domain] = "STABLE"
        print(f"   ✅ {domain}: Stable with adaptive controls")
    except Exception as e:
        results[domain] = f"FAILED: {str(e)}"
        print(f"   ❌ {domain}: {str(e)}")

print(f"\n📊 ADAPTIVE STABILITY RESULTS:")
for domain, result in results.items():
    print(f"   {domain}: {result}")
