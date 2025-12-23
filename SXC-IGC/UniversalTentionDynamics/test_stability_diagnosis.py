#!/usr/bin/env python3
"""
Diagnose why fields are exploding to 254,413
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

print("🔧 STABILITY DIAGNOSIS")
print("Finding why fields explode to 250,000+")
print("=" * 50)

# Test with monitoring
engine = create_robust_engine(
    'general',
    grid_size=20,  # Smaller for debugging
    M_factor=8000,
    rho_cutoff=0.25,
    delta1=1.2,
    delta2=0.8,
    cubic_damping=0.2,
    dt=0.001
)

engine.initialize_gaussian(amplitude=0.6, sigma=0.15)

print("Initial state:")
print(f"  ρ range: [{np.min(engine.rho):.3f}, {np.max(engine.rho):.3f}]")
print(f"  E range: [{np.min(engine.E):.3f}, {np.max(engine.E):.3f}]")
print(f"  F range: [{np.min(engine.F):.3f}, {np.max(engine.F):.3f}]")

# Evolve with step-by-step monitoring
print("\n🔄 Evolving with monitoring...")
for step in range(10):
    engine.evolve(1)
    
    ρ_max = np.max(engine.rho)
    E_max = np.max(engine.E) 
    F_max = np.max(engine.F)
    
    print(f"Step {step}: ρ_max={ρ_max:8.1f}, E_max={E_max:8.1f}, F_max={F_max:8.1f}")
    
    if ρ_max > 1000:
        print("  🚨 ρ EXPLODING!")
        break

# Check which term is causing growth
print(f"\n🔍 ANALYZING GROWTH MECHANISM:")
print(f"Current parameters:")
print(f"  delta1 (ρ→F coupling): {engine.delta1}")
print(f"  delta2 (E→F coupling): {engine.delta2}") 
print(f"  M_factor (stiffness): {engine.M_factor}")
print(f"  cubic_damping: {engine.cubic_damping}")

# The problem might be:
# 1. Too strong source terms (delta1, delta2)
# 2. Insufficient damping (cubic_damping too low)
# 3. Stiffness creating positive feedback
