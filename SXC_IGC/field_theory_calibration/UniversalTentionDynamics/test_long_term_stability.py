#!/usr/bin/env python3
"""
Test what happens over longer evolution
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

print("⏰ LONG-TERM STABILITY TEST")
print("When does the explosion happen?")
print("=" * 50)

engine = create_robust_engine(
    'general',
    grid_size=20,
    M_factor=8000,
    rho_cutoff=0.25,
    delta1=1.2,
    delta2=0.8,
    cubic_damping=0.2,
    dt=0.001
)

engine.initialize_gaussian(amplitude=0.6, sigma=0.15)

print("Monitoring long-term evolution...")
explosion_step = None

for step in range(100):  # Longer test
    engine.evolve(1)
    
    ρ_max = np.max(engine.rho)
    
    if step % 10 == 0 or ρ_max > 100:
        print(f"Step {step}: ρ_max={ρ_max:8.1f}")
    
    if ρ_max > 1000 and explosion_step is None:
        explosion_step = step
        print(f"🚨 EXPLOSION DETECTED at step {step}!")
        break

if explosion_step:
    print(f"\n💥 Field exploded after {explosion_step} steps")
    print("This suggests cumulative numerical error or positive feedback")
else:
    print("✅ Fields remained stable for 100 steps")

# Test if it's the stiffness mechanism
print(f"\n🔍 TESTING STIFFNESS ACTIVATION:")
stiffness_active = np.max(engine.rho) > engine.rho_cutoff
print(f"Stiffness active: {stiffness_active}")
if stiffness_active:
    alpha_eff = engine.compute_effective_stiffness(engine.rho)
    stiffness_ratio = np.max(alpha_eff) / engine.alpha
    print(f"Maximum stiffness amplification: {stiffness_ratio:.0f}x")
