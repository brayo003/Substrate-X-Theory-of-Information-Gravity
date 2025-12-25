#!/usr/bin/env python3
"""
TEST IF FEEDBACK LOOP IS MISSING
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver_fixed_gamma import SubstrateXSolver

def test_feedback():
    """Test if substrate can modify gravity fields"""
    print("🔍 TESTING FEEDBACK LOOP")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1e10, beta=1e10, gamma=1e10,  # Very strong
        chi=1.0, tau=1e6  # Longer timescale
    )
    
    mass = 2e30
    solver.add_point_mass(mass, (0,0))
    
    print("Initial state:")
    E_initial = solver.E.copy()
    F_initial = solver.F.copy()
    s_initial = solver.s.copy()
    
    print(f"  max|E|: {np.max(np.abs(E_initial)):.2e}")
    print(f"  max|F|: {np.max(np.sqrt(F_initial[:,:,0]**2 + F_initial[:,:,1]**2)):.2e}")
    print(f"  max|s|: {np.max(np.abs(s_initial)):.2e}")
    
    # Add perturbation to s
    solver.s += 1e-5
    
    print("\nAfter adding s perturbation:")
    print(f"  max|s|: {np.max(np.abs(solver.s)):.2e}")
    
    # Evolve a few steps
    print("Evolving 10 steps...")
    for i in range(10):
        try:
            solver.step()
        except Exception as e:
            print(f"  Step {i} failed: {e}")
            break
    
    E_final = solver.E.copy()
    F_final = solver.F.copy() 
    s_final = solver.s.copy()
    
    print("\nFinal state:")
    print(f"  max|E|: {np.max(np.abs(E_final)):.2e} (change: {np.max(np.abs(E_final - E_initial)):.2e})")
    print(f"  max|F|: {np.max(np.sqrt(F_final[:,:,0]**2 + F_final[:,:,1]**2)):.2e} (change: {np.max(np.sqrt((F_final - F_initial)[:,:,0]**2 + (F_final - F_initial)[:,:,1]**2)):.2e})")
    print(f"  max|s|: {np.max(np.abs(s_final)):.2e} (change: {np.max(np.abs(s_final - s_initial)):.2e})")
    
    print(f"\n💡 OBSERVATION:")
    print("If E and F fields don't change when s evolves,")
    print("there's NO FEEDBACK from substrate to gravity!")
    print("This means gravity modification won't happen.")

if __name__ == "__main__":
    test_feedback()
