#!/usr/bin/env python3
"""
WORKING calibration test using the correct solver methods
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def solve_static_jacobi(solver, mass_kg, position=(0, 0), min_iter=100, max_iter=2000):
    """Solve static case using Jacobi iterations with the correct rhs method"""
    # Get grid dimensions
    nx, ny = solver.s.shape
    print(f"Grid: {nx}x{ny}")
    print(f"Adding mass: {mass_kg/1.989e30:.2f} M_sun at position {position}")
    
    # Use the solver's built-in method to add mass
    solver.add_point_mass(mass_kg, position)
    
    print(f"After mass addition:")
    print(f"  E field: [{np.min(solver.E):.2e}, {np.max(solver.E):.2e}]")
    print(f"  F field: [{np.min(solver.F):.2e}, {np.max(solver.F):.2e}]")
    print(f"  Initial s: [{np.min(solver.s):.2e}, {np.max(solver.s):.2e}]")
    
    print("Iterating to static solution using Jacobi method...")
    
    for i in range(max_iter):
        s_old = solver.s.copy()
        
        # Use the correct rhs method (not compute_static_rhs)
        rhs = solver.rhs(solver.s, solver.s_prev, solver.E, solver.F, solver.u, solver.v_sub)
        
        # Jacobi update for Poisson-like equation: ∇²s = rhs
        # s_new = (rhs * dx^2 + neighbors) / (2*dim)
        s_new = np.zeros_like(solver.s)
        dx2 = solver.dx * solver.dx
        
        # 2D Jacobi iteration
        s_new[1:-1, 1:-1] = 0.25 * (
            solver.s[2:, 1:-1] + solver.s[:-2, 1:-1] + 
            solver.s[1:-1, 2:] + solver.s[1:-1, :-2] - 
            dx2 * rhs[1:-1, 1:-1]
        )
        
        solver.s = s_new
        
        # Apply boundary conditions
        solver.s[0,:] = 0; solver.s[-1,:] = 0
        solver.s[:,0] = 0; solver.s[:,-1] = 0
        
        residual = np.max(np.abs(solver.s - s_old))
        max_s = np.max(np.abs(solver.s))
        
        if i % 100 == 0:
            print(f"  Iter {i}: max_s = {max_s:.2e}, residual = {residual:.2e}")
            rhs_current = solver.rhs(solver.s, solver.s_prev, solver.E, solver.F, solver.u, solver.v_sub)
            print(f"    Max RHS: {np.max(np.abs(rhs_current)):.2e}")
        
        if i > min_iter and residual < 1e-15:
            print(f"✅ Converged after {i} iterations")
            break
    else:
        print(f"⚠️  Max iterations reached: {max_iter}")
    
    return solver.s

def test_calibration_working():
    """Working calibration test using correct methods"""
    print("🎯 WORKING CALIBRATION TEST")
    print("=" * 60)
    
    # Test with much stronger parameters to see ANY effect
    test_params = {
        'alpha': 1e-2,    # Physical parameter
        'beta': 1e-1,     # Physical parameter  
        'gamma': 1e-2,    # Physical parameter
        'chi': 1.0,
        'tau': 1e3
    }
    
    print(f"Using parameters: α={test_params['alpha']:.1e}, β={test_params['beta']:.1e}, γ={test_params['gamma']:.1e}")
    
    # Solar system scale
    solver = SubstrateXSolver(
        grid_size=64,
        domain_size=2e11,  # ~1 AU
        **test_params
    )
    
    print(f"\nSolver scaled parameters:")
    print(f"  α_scaled: {solver.alpha:.2e}")
    print(f"  β_scaled: {solver.beta:.2e}") 
    print(f"  γ_scaled: {solver.gamma:.2e}")
    print(f"  dx: {solver.dx:.2e} m")
    
    # Test mass
    mass_kg = 2e30  # 1 solar mass
    
    # Solve using Jacobi iterations
    s_final = solve_static_jacobi(solver, mass_kg, min_iter=100, max_iter=2000)
    
    # Calculate k_eff
    max_s = np.max(np.abs(s_final))
    if max_s > 0:
        k_eff = max_s / (solver.gamma * mass_kg)
    else:
        k_eff = 0.0
    
    print(f"\n🎯 CALIBRATION RESULT:")
    print(f"  Max s field: {max_s:.2e}")
    print(f"  k_eff = {k_eff:.2e}")
    
    if k_eff == 0:
        print(f"\n🔍 TROUBLESHOOTING:")
        print(f"  The s field remained zero. Possible issues:")
        print(f"  1. Parameters are still too weak")
        print(f"  2. The rhs method might need different arguments") 
        print(f"  3. Mass addition might not affect the s field directly")
        
        # Let's test the rhs method directly
        print(f"\n  Testing rhs method directly:")
        try:
            rhs_test = solver.rhs(solver.s, solver.s_prev, solver.E, solver.F, solver.u, solver.v_sub)
            print(f"    RHS range: [{np.min(rhs_test):.2e}, {np.max(rhs_test):.2e}]")
        except Exception as e:
            print(f"    RHS failed: {e}")
    
    return k_eff

if __name__ == "__main__":
    k_eff = test_calibration_working()
