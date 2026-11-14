#!/usr/bin/env python3
"""Debug the RHS computation directly"""
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
print(f"Grid: {solver.Nx}x{solver.Ny}")
print(f"dx: {solver.dx:.2e}")
print(f"Parameters: α={solver.alpha_scaled:.2e}, β={solver.beta_scaled:.2e}, γ={solver.gamma_scaled:.2e}")

# Add a simple mass
center_x, center_y = solver.Nx//2, solver.Ny//2
mass_kg = 2e30
solver.rho[center_x, center_y] += mass_kg / (solver.dx * solver.dy)

print(f"\nMass added: {mass_kg/1.989e30:.1f} M_sun")
print(f"Max rho: {np.max(solver.rho):.2e}")

# Test RHS computation
print(f"\nTesting RHS computation:")
rhs = solver.compute_static_rhs()
print(f"Max RHS: {np.max(np.abs(rhs)):.2e}")
print(f"Min RHS: {np.min(rhs):.2e}")

# Test individual terms
print(f"\nIndividual terms:")
alpha_term = solver.alpha_scaled * solver.rho
print(f"Alpha*rho max: {np.max(np.abs(alpha_term)):.2e}")

beta_term = solver.beta_scaled * solver.s**2  
print(f"Beta*s² max: {np.max(np.abs(beta_term)):.2e}")

gamma_term = solver.gamma_scaled * solver.rho
print(f"Gamma*rho max: {np.max(np.abs(gamma_term)):.2e}")

# Test Laplacian
laplacian_s = solver.compute_laplacian(solver.s)
print(f"Laplacian(s) max: {np.max(np.abs(laplacian_s)):.2e}")

print(f"\nInitial s field:")
print(f"Max s: {np.max(solver.s):.2e}")
print(f"Min s: {np.min(solver.s):.2e}")
