#!/usr/bin/env python3
"""
FINAL FIXED calibration test
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def test_calibration_fixed():
    """Fixed calibration test using correct approach"""
    print("🎯 FINAL CALIBRATION TEST")
    print("=" * 60)
    
    # Use the parameters that actually showed some effect
    params = {
        'alpha': 1.0,    # These showed the strongest effect
        'beta': 1.0,     
        'gamma': 1.0,
        'chi': 1.0,
        'tau': 1e3
    }
    
    print(f"Using parameters that showed effect: α={params['alpha']:.1e}, β={params['beta']:.1e}, γ={params['gamma']:.1e}")
    
    solver = SubstrateXSolver(
        grid_size=32,
        domain_size=2e11,
        **params
    )
    
    print(f"\nScaled parameters:")
    print(f"  α: {solver.alpha:.2e}")
    print(f"  β: {solver.beta:.2e}") 
    print(f"  γ: {solver.gamma:.2e}")
    
    # Add mass
    mass_kg = 2e30
    solver.add_point_mass(mass_kg, (0, 0))
    
    print(f"\nAfter mass addition:")
    print(f"  E field: [{np.min(solver.E):.2e}, {np.max(solver.E):.2e}]")
    print(f"  F field: [{np.min(solver.F):.2e}, {np.max(solver.F):.2e}]")
    print(f"  s field: [{np.min(solver.s):.2e}, {np.max(solver.s):.2e}]")
    
    # Evolve longer to reach better steady state
    print(f"\nEvolving 2000 time steps to steady state...")
    s_values = []
    for step in range(2000):
        solver.step()
        
        if step % 200 == 0:
            max_s = np.max(np.abs(solver.s))
            s_values.append(max_s)
            print(f"  Step {step}: max_s = {max_s:.2e}")
    
    # Calculate k_eff from FINAL state
    max_s = np.max(np.abs(solver.s))
    k_eff = max_s / (solver.gamma * mass_kg) if max_s > 0 else 0.0
    
    print(f"\n🎯 FINAL CALIBRATION RESULT:")
    print(f"  Max s field: {max_s:.2e}")
    print(f"  k_eff = {k_eff:.2e}")
    
    # Check if we're converging to a steady state
    if len(s_values) > 1:
        change = abs(s_values[-1] - s_values[-2]) / max(s_values[-1], 1e-20)
        print(f"  Convergence: last change = {change:.2e}")
    
    return k_eff

if __name__ == "__main__":
    test_calibration_fixed()
