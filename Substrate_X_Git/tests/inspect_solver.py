#!/usr/bin/env python3
"""Inspect the solver object to see available attributes"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

# Create a solver
solver = SubstrateXSolver(
    grid_size=32,
    domain_size=2e11,
    alpha=1e-2,
    beta=1e-1,
    gamma=1e-2,
    chi=1.0,
    tau=1e3
)

print("=== SOLVER ATTRIBUTES ===")
for attr in sorted(dir(solver)):
    if not attr.startswith('_'):  # Skip private attributes
        try:
            value = getattr(solver, attr)
            if not callable(value):  # Skip methods
                print(f"{attr}: {type(value)} = {value}")
        except:
            print(f"{attr}: <cannot display>")

print(f"\n=== GRID DIMENSIONS ===")
# Try common grid dimension attribute names
possible_grid_attrs = ['nx', 'ny', 'Nx', 'Ny', 'grid_size', 'shape', 'n_x', 'n_y']
for attr in possible_grid_attrs:
    if hasattr(solver, attr):
        print(f"{attr}: {getattr(solver, attr)}")

print(f"\n=== ARRAY SHAPES ===")
array_attrs = ['rho', 's', 'phi', 'X', 'Y']
for attr in array_attrs:
    if hasattr(solver, attr):
        arr = getattr(solver, attr)
        if hasattr(arr, 'shape'):
            print(f"{attr}.shape: {arr.shape}")
