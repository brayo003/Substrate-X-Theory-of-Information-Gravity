#!/usr/bin/env python3
"""Inspect what methods are available in the solver"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

# Create solver
solver = SubstrateXSolver(
    grid_size=16,
    domain_size=2e11,
    alpha=1e-2,
    beta=1e-1,
    gamma=1e-2,
    chi=1.0,
    tau=1e3
)

print("=== AVAILABLE METHODS ===")
methods = [method for method in dir(solver) if not method.startswith('_') and callable(getattr(solver, method))]
for method in sorted(methods):
    print(f"  {method}")

print(f"\n=== STATIC SOLVER METHODS ===")
static_methods = [m for m in methods if 'static' in m.lower() or 'rhs' in m.lower() or 'jacobi' in m.lower()]
for method in static_methods:
    print(f"  {method}")

print(f"\n=== TIME EVOLUTION METHODS ===")
time_methods = [m for m in methods if 'step' in m.lower() or 'evolve' in m.lower() or 'update' in m.lower()]
for method in time_methods:
    print(f"  {method}")
