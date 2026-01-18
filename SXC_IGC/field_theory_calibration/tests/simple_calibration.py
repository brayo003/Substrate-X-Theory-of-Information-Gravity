#!/usr/bin/env python3
"""
SIMPLE CALIBRATION: The right way to measure k_eff
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def simple_calibration():
    """
    k_eff should measure how much the SUBSTRATE FIELD enhances gravity
    not the static F field which is just Newtonian
    """
    print("🎯 SIMPLE CALIBRATION TRUTH")
    print("=" * 60)
    
    # The REAL calibration process:
    # 1. Add mass (creates Newtonian F field)  
    # 2. Evolve substrate field s
    # 3. Measure how s field modifies the effective gravity
    # 4. k_eff = (g_effective - g_newton) / g_newton
    
    print("Step 1: Add mass to create Newtonian field")
    solver = SubstrateXSolver(
        grid_size=32,
        domain_size=2e11,
        alpha=1e-10,  # These control substrate response
        beta=1e-10,
        gamma=1e-10,
        chi=1.0,
        tau=1e3
    )
    
    mass = 2e30
    solver.add_point_mass(mass, (0,0))
    
    print("Step 2: Measure Newtonian acceleration")
    char_distance = 2e10
    distances = np.sqrt(solver.X**2 + solver.Y**2)
    char_idx = np.unravel_index(np.argmin(np.abs(distances - char_distance)), distances.shape)
    
    F_newton = np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)[char_idx]
    print(f"Newtonian F at r={distances[char_idx]:.1e}m: {F_newton:.6e} m/s²")
    
    print("Step 3: Evolve substrate field")
    s_initial = solver.s.copy()
    for i in range(100):
        solver.step()
    s_final = solver.s.copy()
    
    s_change = np.max(np.abs(s_final - s_initial))
    print(f"Substrate field changed by: {s_change:.6e}")
    
    print("Step 4: k_eff comes from substrate field modifying gravity")
    print("NOT from the static F field!")
    print("")
    print("💡 REAL CALIBRATION PROCESS:")
    print("1. Tune α,β,γ so substrate evolution produces right k_eff")
    print("2. k_eff ≈ 2e-4 means s field causes 0.02% gravity enhancement") 
    print("3. k_eff ≈ 0.3 means s field causes 30% gravity enhancement")
    print("")
    print("The static F field is just Newtonian baseline")
    print("The DYNAMIC s field creates the enhancement via the master equation")

if __name__ == "__main__":
    simple_calibration()
