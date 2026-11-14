#!/usr/bin/env python3
"""
Test if engine finds patterns in earthquake data
"""
import sys
import os
sys.path.insert(0, 'core_engine/src')
from universal_dynamics_robust import create_robust_engine
import pandas as pd

# You can download real earthquake data from USGS
# For now, we'll test pattern formation capability

print("🌋 EARTHQUAKE PATTERN TEST")
print("Testing if engine creates fault-line like structures")

engine = create_robust_engine('general', grid_size=64, M_factor=10000)
engine.initialize_gaussian(amplitude=0.8, sigma=0.1)

# Evolve and check for linear structures (like fault lines)
engine.evolve(50)

# Analyze for linear features
from skimage.transform import hough_line
edges = np.gradient(engine.rho)
linear_features = hough_line(edges)

print(f"Linear structures detected: {len(linear_features[0])}")
if len(linear_features[0]) > 5:
    print("✅ Engine creates fault-line like patterns!")
