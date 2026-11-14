#!/usr/bin/env python3
"""
PROPER calibration test using the solver's mass methods
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def solve_static_with_mass(solver, mass_kg, position=(0, 0), min_iter=100, max_iter=2000):
    """Solve static case using the proper mass addition method"""
    # Get grid dimensions
    nx, ny = solver.s.shape
    print(f"Grid: {nx}x{ny}")
    print(f"Adding mass: {mass_kg/1.989e30:.2f} M_sun at position {position}")
    
    # Use the solver's built-in method to add mass
    solver.add_point_mass(mass_kg, position)
    
    print(f"After adding mass:")
    print(f"  Max E field: {np.max(np.abs(solver.E)):.2e}")
    print(f"  Max F field: {np.max(np.abs(solver.F)):.2e}")
    print(f"  Max s field: {np.max(np.abs(solver.s)):.2e}")
    
    print("Iterating to static solution...")
    
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
            rhs_debug = solver.compute_static_rhs()
            print(f"    Max RHS: {np.max(np.abs(rhs_debug)):.2e}")
        
        if i > min_iter and residual < 1e-15:
            print(f"✅ Converged after {i} iterations")
            break
    else:
        print(f"⚠️  Max iterations reached: {max_iter}")
    
    return solver.s

def calculate_k_eff(solver, mass_kg):
    """Calculate k_eff from the substrate field"""
    max_s = np.max(np.abs(solver.s))
    
    if max_s == 0:
        return 0.0
    
    # k_eff = max_s / (gamma * mass)
    k_eff = max_s / (solver.gamma * mass_kg)
    return k_eff

def test_calibration_proper():
    """Test calibration using proper mass addition"""
    print("🎯 PROPER CALIBRATION TEST")
    print("=" * 60)
    
    # Test parameters - start with stronger values
    test_cases = [
        {
            'name': 'SOLAR SYSTEM',
            'grid_size': 64,
            'domain_size': 2e11,  # ~1 AU
            'mass': 2e30,         # 1 solar mass
            'params': {
                'alpha': 1e-2,
                'beta': 1e-1, 
                'gamma': 1e-2,
                'chi': 1.0,
                'tau': 1e3
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        print(f"  Domain: {case['domain_size']/1e11:.1f} × 10¹¹ m")
        print(f"  Mass: {case['mass']/1.989e30:.1f} M_sun")
        print(f"  Parameters: α={case['params']['alpha']:.1e}, β={case['params']['beta']:.1e}, γ={case['params']['gamma']:.1e}")
        
        solver = SubstrateXSolver(
            grid_size=case['grid_size'],
            domain_size=case['domain_size'],
            **case['params']
        )
        
        print(f"\nSolver initialized:")
        print(f"  α_scaled: {solver.alpha:.2e}")
        print(f"  β_scaled: {solver.beta:.2e}") 
        print(f"  γ_scaled: {solver.gamma:.2e}")
        
        # Solve with mass
        s_final = solve_static_with_mass(solver, case['mass'])
        
        # Calculate k_eff
        k_eff = calculate_k_eff(solver, case['mass'])
        
        print(f"\n🎯 RESULT:")
        print(f"  Max s field: {np.max(np.abs(s_final)):.2e}")
        print(f"  k_eff = {k_eff:.2e}")
        
        # Debug information
        if k_eff == 0:
            print(f"\n🔍 DEBUG INFO:")
            print(f"  Mass: {case['mass']:.2e} kg")
            print(f"  Gamma: {solver.gamma:.2e}")
            print(f"  Expected scale: {solver.gamma * case['mass']:.2e}")
            print(f"  Actual max s: {np.max(np.abs(s_final)):.2e}")
            
            # Check RHS components
            rhs = solver.compute_static_rhs()
            print(f"  Max RHS: {np.max(np.abs(rhs)):.2e}")
            print(f"  Max E: {np.max(np.abs(solver.E)):.2e}")
            print(f"  Max F: {np.max(np.abs(solver.F)):.2e}")
    
    return k_eff

if __name__ == "__main__":
    k_eff = test_calibration_proper()
