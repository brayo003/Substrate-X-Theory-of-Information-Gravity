#!/usr/bin/env python3
import sys
sys.path.insert(0, '../..')
from core_engine.src.universal_dynamics_monitored import create_monitored_engine
import numpy as np

print("🔧 ENGINE STATE DIAGNOSTIC")
engine = create_monitored_engine('general', grid_size=16)

print("BEFORE initialization:")
print(f"ρ: shape={engine.rho.shape}, max={np.max(engine.rho):.6f}")
print(f"E: shape={engine.E.shape}, max={np.max(engine.E):.6f}") 
print(f"F: shape={engine.F.shape}, max={np.max(engine.F):.6f}")

# Try different initialization methods
print("\nTesting initialization methods...")
try:
    engine.initialize_gaussian(amplitude=1.0)
    print("✓ initialize_gaussian(amplitude=1.0) worked")
except Exception as e:
    print(f"✗ initialize_gaussian failed: {e}")

print("\nAFTER initialization:")
print(f"ρ: max={np.max(engine.rho):.6f}, mean={np.mean(engine.rho):.6f}")
print(f"E: max={np.max(engine.E):.6f}, mean={np.mean(engine.E):.6f}")

# Test evolution
print("\nTesting evolution...")
for i in range(5):
    engine.evolve(1, verbose=False)
    print(f"Step {i}: ρ_max={np.max(engine.rho):.6f}")
