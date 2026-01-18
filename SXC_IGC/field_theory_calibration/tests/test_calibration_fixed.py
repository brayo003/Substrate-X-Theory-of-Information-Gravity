#!/usr/bin/env python3
"""
Proper calibration test with stronger physical parameters
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def solve_static_with_diagnostics(solver, mass_kg, min_iter=100, max_iter=2000):
    """Solve static case with detailed diagnostics"""
    # Get grid dimensions from array shapes
    nx, ny = solver.s.shape
    center_x, center_y = nx//2, ny//2
    
    # Add mass source - ensure it's properly placed
    solver.rho[center_x, center_y] += mass_kg / (solver.dx * solver.dy)
    
    print(f"Mass: {mass_kg/1.989e30:.2f} M_sun at grid position ({center_x}, {center_y})")
    print(f"Mass density at source: {solver.rho[center_x, center_y]:.2e} kg/m²")
    print("Iterating...")
    
    for i in range(max_iter):
        s_old = solver.s.copy()
        
        # Compute RHS with current parameters
        rhs = solver.compute_static_rhs()
        
        # Jacobi update
        solver.s = solver.jacobi_update(rhs)
        
        # Apply boundary conditions
        solver.s[0,:] = 0; solver.s[-1,:] = 0
        solver.s[:,0] = 0; solver.s[:,-1] = 0
        
        residual = np.max(np.abs(solver.s - s_old))
        max_s = np.max(np.abs(solver.s))
        
        if i % 100 == 0:
            print(f"  Iter {i}: max_s = {max_s:.2e}, residual = {residual:.2e}")
            # Debug the RHS computation
            rhs_debug = solver.compute_static_rhs()
            print(f"    Max RHS: {np.max(np.abs(rhs_debug)):.2e}")
            print(f"    Max rho: {np.max(solver.rho):.2e}")
        
        if i > min_iter and residual < 1e-15:
            print(f"✅ Converged after {i} iterations")
            break
    else:
        print(f"⚠️  Max iterations reached: {max_iter}")
    
    return solver.s

def calculate_k_eff(solver, mass_kg):
    """Calculate k_eff from the substrate field"""
    # Get grid dimensions from array shapes
    nx, ny = solver.s.shape
    center_x, center_y = nx//2, ny//2
    
    # Get the maximum substrate field value near the mass
    x_slice = slice(max(0, center_x-1), min(nx, center_x+2))
    y_slice = slice(max(0, center_y-1), min(ny, center_y+2))
    
    max_s = np.max(np.abs(solver.s[x_slice, y_slice]))
    
    if max_s == 0:
        return 0.0
    
    # k_eff = max_s / (gamma * mass)
    k_eff = max_s / (solver.gamma * mass_kg)
    return k_eff

def test_calibration_strong_params():
    """Test with much stronger parameters to see ANY effect"""
    print("🎯 CALIBRATION WITH STRONG PARAMETERS")
    print("=" * 60)
    
    # Use MUCH stronger parameters for testing
    strong_params = {
        'alpha': 1e-2,      # Much stronger - we want to see ANY signal
        'beta': 1e-1,       # Strong nonlinearity
        'gamma': 1e-2,      # Strong information coupling
        'chi': 1.0,
        'tau': 1e3
    }
    
    print(f"\n1. Testing with STRONG parameters:")
    print(f"   α_physical = {strong_params['alpha']:.1e}")
    print(f"   β_physical = {strong_params['beta']:.1e}") 
    print(f"   γ_physical = {strong_params['gamma']:.1e}")
    
    grid_size = 64
    # Solar system scale
    solver = SubstrateXSolver(
        grid_size=grid_size,
        domain_size=2e11,  # ~1 AU
        **strong_params
    )
    
    print(f"\nSolver parameters:")
    print(f"  α_scaled = {solver.alpha:.2e}")
    print(f"  β_scaled = {solver.beta:.2e}")
    print(f"  γ_scaled = {solver.gamma:.2e}")
    print(f"  Grid size: {grid_size}x{grid_size}")
    print(f"  Actual grid shape: {solver.s.shape}")
    
    # Test mass
    mass_kg = 2e30  # 1 solar mass
    
    # Solve
    s_field = solve_static_with_diagnostics(
        solver, mass_kg, min_iter=100, max_iter=2000
    )
    
    # Calculate k_eff
    k_eff = calculate_k_eff(solver, mass_kg)
    
    print(f"\n🎯 FINAL RESULT:")
    print(f"   Max s field: {np.max(np.abs(s_field)):.2e}")
    print(f"   k_eff = {k_eff:.2e}")
    
    # If we still get zero, we need to debug the RHS computation
    if k_eff == 0:
        print(f"\n🔍 DEBUGGING RHS COMPUTATION:")
        print(f"   Mass term: {mass_kg:.2e}")
        print(f"   Gamma term: {solver.gamma:.2e}")
        print(f"   Expected scale: {solver.gamma * mass_kg:.2e}")
        print(f"   Actual max s: {np.max(np.abs(s_field)):.2e}")
        
        # Check individual RHS components
        print(f"\n   RHS Components:")
        alpha_term = solver.alpha * solver.rho
        print(f"   Max alpha*rho: {np.max(np.abs(alpha_term)):.2e}")
        
        beta_term = solver.beta * solver.s**2
        print(f"   Max beta*s²: {np.max(np.abs(beta_term)):.2e}")
        
        gamma_term = solver.gamma * solver.rho
        print(f"   Max gamma*rho: {np.max(np.abs(gamma_term)):.2e}")
        
        # Check Laplacian
        if hasattr(solver, 'compute_laplacian'):
            laplacian_s = solver.compute_laplacian(solver.s)
            print(f"   Max Laplacian(s): {np.max(np.abs(laplacian_s)):.2e}")
    
    return k_eff

if __name__ == "__main__":
    k_eff = test_calibration_strong_params()
