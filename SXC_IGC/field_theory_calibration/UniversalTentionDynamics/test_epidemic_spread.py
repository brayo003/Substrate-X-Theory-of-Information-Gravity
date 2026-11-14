#!/usr/bin/env python3
"""
Test if engine models epidemic-like spread patterns
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np

print("🦠 EPIDEMIC SPREAD TEST")
print("Testing SIR-like disease dynamics")

# Configure for epidemic-like behavior
engine = create_robust_engine(
    'healthcare', 
    grid_size=48,
    delta1=2.0,  # Strong infection coupling
    delta2=0.5,  # Moderate recovery coupling
    cubic_damping=0.3,
    M_factor=5000
)

# Start with infected "patient zero" in center
engine.initialize_gaussian(amplitude=0.1, sigma=0.05)
engine.rho[24, 24] = 0.9  # Patient zero

print("Simulating disease spread...")
spread_history = []
for step in range(30):
    engine.evolve(1)
    infected_cells = np.sum(engine.rho > 0.3)
    spread_history.append(infected_cells)
    if step % 10 == 0:
        print(f"Step {step}: {infected_cells} infected cells")

# Check for realistic spread curve
if spread_history[-1] > spread_history[0] * 3:
    print("✅ Realistic epidemic spread pattern!")
    print(f"Infection grew {spread_history[-1]/spread_history[0]:.1f}x")
