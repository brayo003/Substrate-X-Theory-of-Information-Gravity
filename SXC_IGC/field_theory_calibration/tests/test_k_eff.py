#!/usr/bin/env python3
"""Test k_eff enhancement in the patched solver"""

import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def test_k_effect():
    print("🔍 Testing k_eff enhancement...")
    
    # Create a solver with known parameters
    solver = SubstrateXSolver(
        grid_size=64,
        domain_size=1e11,  # Smaller domain for testing
        alpha=1e-2,
        beta=1e-1,
        gamma=1e-2,
        chi=1.0,
        tau=1e3
    )
    
    # Test mass (1 solar mass)
    mass_kg = 2e30
    position = (solver.grid_size//2, solver.grid_size//2)
    
    # Test with k_eff = 0 (should match Newtonian)
    solver.add_point_mass(mass_kg, position, k_eff=0.0)
    F_newton = solver.F[position[0], position[1], 0]  # x-component of force
    
    # Reset solver
    solver = SubstrateXSolver(
        grid_size=64,
        domain_size=1e11,
        alpha=1e-2,
        beta=1e-1,
        gamma=1e-2,
        chi=1.0,
        tau=1e3
    )
    
    # Test with k_eff = 1.0 (should be 2x Newtonian)
    solver.add_point_mass(mass_kg, position, k_eff=1.0)
    F_enhanced = solver.F[position[0], position[1], 0]  # x-component of force
    
    # Calculate ratio
    ratio = F_enhanced / F_newton if F_newton != 0 else 0
    expected_ratio = 2.0  # (1 + k_eff) = 2.0 when k_eff=1.0
    
    print(f"  Newtonian force: {F_newton:.2e}")
    print(f"  Enhanced force:  {F_enhanced:.2e}")
    print(f"  Ratio: {ratio:.2f} (expected: {expected_ratio:.1f})")
    
    # Check if the ratio is close to expected (within 10%)
    if abs(ratio - expected_ratio) < 0.1 * expected_ratio:
        print("✅ k_eff enhancement works as expected!")
        return True
    else:
        print("❌ k_eff enhancement does not match expected value")
        return False

if __name__ == "__main__":
    test_k_effect()
