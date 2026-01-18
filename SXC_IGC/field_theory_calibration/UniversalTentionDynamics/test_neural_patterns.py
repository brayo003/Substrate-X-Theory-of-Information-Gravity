#!/usr/bin/env python3
"""
Test if engine creates neural-network like connectivity
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import numpy as np
from scipy.ndimage import label

print("🧠 NEURAL PATTERN TEST")
print("Testing if engine creates brain-like connectivity")

engine = create_robust_engine(
    'general',
    grid_size=56,
    M_factor=2000,
    rho_cutoff=0.2,
    delta1=1.5,  # Moderate connection strength
    cubic_damping=0.1
)

# Start with random seeds (like neural stem cells)
np.random.seed(42)
engine.rho = np.random.rand(56, 56) * 0.3

print("Evolving neural-like network...")
engine.evolve(40)

# Analyze connectivity patterns
threshold = np.percentile(engine.rho, 70)
connected_regions, num_regions = label(engine.rho > threshold)

print(f"Connected regions formed: {num_regions}")
avg_region_size = np.sum(engine.rho > threshold) / max(num_regions, 1)

if num_regions > 10 and avg_region_size < 20:
    print("✅ Brain-like modular network formed!")
    print(f"Modularity: {num_regions} regions, avg size: {avg_region_size:.1f} cells")
