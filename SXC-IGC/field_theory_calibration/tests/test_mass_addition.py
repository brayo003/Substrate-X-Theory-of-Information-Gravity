#!/usr/bin/env python3
"""Test the mass addition methods directly"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

# Create solver
solver = SubstrateXSolver(
    grid_size=32,
    domain_size=2e11,
    alpha=1e-2,
    beta=1e-1,
    gamma=1e-2,
    chi=1.0,
    tau=1e3
)

print("=== TESTING MASS ADDITION ===")
print("Initial state:")
print(f"  E field: min={np.min(solver.E):.2e}, max={np.max(solver.E):.2e}")
print(f"  F field: min={np.min(solver.F):.2e}, max={np.max(solver.F):.2e}")
print(f"  s field: min={np.min(solver.s):.2e}, max={np.max(solver.s):.2e}")

# Add a point mass
mass_kg = 2e30  # 1 solar mass
position = (0, 0)  # Center of domain

print(f"\nAdding {mass_kg/1.989e30:.1f} M_sun at {position}")
solver.add_point_mass(mass_kg, position)

print("\nAfter mass addition:")
print(f"  E field: min={np.min(solver.E):.2e}, max={np.max(solver.E):.2e}")
print(f"  F field: min={np.min(solver.F):.2e}, max={np.max(solver.F):.2e}")
print(f"  F field shape: {solver.F.shape}")
print(f"  s field: min={np.min(solver.s):.2e}, max={np.max(solver.s):.2e}")

# Test RHS computation
print(f"\nTesting RHS computation:")
rhs = solver.compute_static_rhs()
print(f"  RHS: min={np.min(rhs):.2e}, max={np.max(rhs):.2e}")
print(f"  RHS shape: {rhs.shape}")

# Test a few iterations
print(f"\nTesting a few iterations:")
for i in range(10):
    s_old = solver.s.copy()
    rhs = solver.compute_static_rhs()
    solver.s = solver.jacobi_update(rhs)
    
    # Boundary conditions
    solver.s[0,:] = 0; solver.s[-1,:] = 0
    solver.s[:,0] = 0; solver.s[:,-1] = 0
    
    residual = np.max(np.abs(solver.s - s_old))
    max_s = np.max(np.abs(solver.s))
    
    print(f"  Iter {i}: max_s={max_s:.2e}, residual={residual:.2e}")
