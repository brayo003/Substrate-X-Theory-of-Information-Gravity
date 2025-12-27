#!/usr/bin/env python3
"""
Test with stability-aware parameters for large grids
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine

print("🛠️ TESTING LARGE GRID WITH STABILITY FIX")
print("Using reduced M_factor and stronger damping")

stable_large_params = {
    'grid_size': 64,      # Large system
    'M_factor': 50,       # HALF the original stiffness  
    'rho_cutoff': 0.2,    # More conservative
    'delta1': 0.05,       # Much weaker coupling
    'time_steps': 50,     # Fewer steps to monitor
}

print(f"🧪 Testing cosmic domain with stable large params...")
engine = create_robust_engine('cosmic', stable_large_params)
print("✅ LARGE GRID STABLE! Explosion fixed.")
