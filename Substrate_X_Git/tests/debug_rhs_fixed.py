#!/usr/bin/env python3
"""Debug the RHS computation with correct attribute names"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

# Create a simple solver
solver = SubstrateXSolver(
    grid_size=32,
    domain_size=2e11,
    alpha=1e-2,
    beta=1e-1, 
    gamma=1e-2,
    chi=1.0,
    tau=1e3
)

print("=== RHS DEBUGGING ===")

# Get grid dimensions from array shapes
nx, ny = solver.s.shape
print(f"Grid shape: {solver.s.shape}")
center_x, center_y = nx//2, ny//2

print(f"dx: {solver.dx:.2e}")
print(f"Parameters: α={solver.alpha:.2e}, β={solver.beta:.2e}, γ={solver.gamma:.2e}")

# Add a simple mass
mass_kg = 2e30
solver.rho[center_x, center_y] += mass_kg / (solver.dx * solver.dy)

print(f"\nMass added: {mass_kg/1.989e30:.1f} M_sun")
print(f"Max rho: {np.max(solver.rho):.2e}")
print(f"Rho at center: {solver.rho[center_x, center_y]:.2e}")

# Test RHS computation
print(f"\nTesting RHS computation:")
rhs = solver.compute_static_rhs()
print(f"Max RHS: {np.max(np.abs(rhs)):.2e}")
print(f"Min RHS: {np.min(rhs):.2e}")
print(f"RHS at center: {rhs[center_x, center_y]:.2e}")

# Test individual terms
print(f"\nIndividual terms:")
alpha_term = solver.alpha * solver.rho
print(f"Alpha*rho max: {np.max(np.abs(alpha_term)):.2e}")
print(f"Alpha*rho at center: {alpha_term[center_x, center_y]:.2e}")

beta_term = solver.beta * solver.s**2  
print(f"Beta*s² max: {np.max(np.abs(beta_term)):.2e}")
print(f"Beta*s² at center: {beta_term[center_x, center_y]:.2e}")

gamma_term = solver.gamma * solver.rho
print(f"Gamma*rho max: {np.max(np.abs(gamma_term)):.2e}")
print(f"Gamma*rho at center: {gamma_term[center_x, center_y]:.2e}")

# Test Laplacian
if hasattr(solver, 'compute_laplacian'):
    laplacian_s = solver.compute_laplacian(solver.s)
    print(f"Laplacian(s) max: {np.max(np.abs(laplacian_s)):.2e}")
    print(f"Laplacian(s) at center: {laplacian_s[center_x, center_y]:.2e}")
else:
    print("compute_laplacian method not available")

print(f"\nInitial field values:")
print(f"Max s: {np.max(solver.s):.2e}")
print(f"Min s: {np.min(solver.s):.2e}")
print(f"s at center: {solver.s[center_x, center_y]:.2e}")

print(f"\nField shapes:")
for attr in ['rho', 's']:
    if hasattr(solver, attr):
        arr = getattr(solver, attr)
        print(f"{attr}: {arr.shape}, dtype: {arr.dtype}")
