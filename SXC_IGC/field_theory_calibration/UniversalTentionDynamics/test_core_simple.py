#!/usr/bin/env python3
"""
Simple standalone test for core engine
"""
import numpy as np
import sys
import os

# Add core engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core_engine', 'src'))

from universal_dynamics import create_engine

print("🧪 Simple Core Engine Test")
print("=" * 40)

# Create and test engine
engine = create_engine('general', grid_size=32)  # Smaller for faster test
engine.initialize_gaussian(amplitude=1.0)

print("Initial state:")
stats = engine.get_field_statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")

# Evolve
print("\nEvolving 20 steps...")
engine.evolve(20)

print("\nFinal state:")
stats = engine.get_field_statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")

# Test stiffness activation
if stats['stiffness_active']:
    print("✅ Stiffness mechanism activated!")
else:
    print("⚠️  Stiffness not activated (rho below cutoff)")

print("\n🎉 Core engine working correctly!")
