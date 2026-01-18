#!/usr/bin/env python3
"""Inspect what fields represent mass/matter in the solver"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

# Create a solver
solver = SubstrateXSolver(
    grid_size=16,  # Small for quick testing
    domain_size=2e11,
    alpha=1e-2,
    beta=1e-1,
    gamma=1e-2,
    chi=1.0,
    tau=1e3
)

print("=== FIELD ANALYSIS ===")
print("Available arrays and their purposes:")

# Check each field's characteristics
fields_to_check = ['s', 'E', 'F', 'u', 'v_sub', 'phi']

for field in fields_to_check:
    if hasattr(solver, field):
        arr = getattr(solver, field)
        print(f"\n{field}:")
        print(f"  Shape: {arr.shape}")
        print(f"  Type: {arr.dtype}")
        print(f"  Range: {np.min(arr):.2e} to {np.max(arr):.2e}")
        print(f"  Norm: {np.linalg.norm(arr):.2e}")

# Check if there are methods to add mass
print(f"\n=== MASS-RELATED METHODS ===")
methods = [method for method in dir(solver) if not method.startswith('_') and callable(getattr(solver, method))]
mass_methods = [m for m in methods if 'mass' in m.lower() or 'rho' in m.lower() or 'add' in m.lower() or 'source' in m.lower()]
for method in mass_methods:
    print(f"  {method}")

# Check the source code for how mass is handled
print(f"\n=== CHECKING SOURCE CODE STRUCTURE ===")
# Look for how mass sources are implemented in the solver
