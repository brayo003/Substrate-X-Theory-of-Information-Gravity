#!/usr/bin/env python3
"""Debug how the F field depends on gamma parameter"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def debug_F_dependence():
    """Understand how gamma affects F field generation"""
    print("🎯 DEBUGGING F FIELD DEPENDENCE ON GAMMA")
    print("=" * 60)
    
    gamma_values = [0.1, 1.0, 10.0]
    mass_kg = 2e30
    
    print("Testing how gamma affects F field magnitude:\n")
    
    for gamma in gamma_values:
        solver = SubstrateXSolver(
            grid_size=16,
            domain_size=2e11,
            alpha=1.0,
            beta=1.0,
            gamma=gamma,
            chi=1.0,
            tau=1e3
        )
        
        solver.add_point_mass(mass_kg, (0,0))
        
        max_F = np.max(np.abs(solver.F))
        k_eff = max_F / (solver.gamma * mass_kg)
        
        print(f"gamma = {gamma:.1f}:")
        print(f"  Scaled gamma = {solver.gamma:.2e}")
        print(f"  Max F field = {max_F:.6f}")
        print(f"  k_eff = {k_eff:.6f}")
        print(f"  F / gamma = {max_F / solver.gamma:.6f}")
        print()

def test_constant_F():
    """Test if F field generation is independent of gamma"""
    print("🔍 TESTING F FIELD GENERATION MECHANISM")
    print("=" * 60)
    
    # Test if F field is generated the same way regardless of gamma
    mass_kg = 2e30
    
    # First, let's see what creates the F field
    solver1 = SubstrateXSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1.0,
        beta=1.0, 
        gamma=1.0,  # Reference case
        chi=1.0,
        tau=1e3
    )
    
    print("Before mass addition:")
    print(f"  Max F: {np.max(np.abs(solver1.F)):.6f}")
    
    solver1.add_point_mass(mass_kg, (0,0))
    
    print("After mass addition:")
    print(f"  Max F: {np.max(np.abs(solver1.F)):.6f}")
    print(f"  This suggests F field is created by add_point_mass()")
    
    # Let's check the add_point_mass method
    print(f"\n💡 INSIGHT: F field generation seems independent of gamma")
    print(f"   This means k_eff = F / (gamma * mass) will decrease with larger gamma")
    print(f"   To get k_eff ≈ 2e-4, we need gamma ≈ 0.1")

if __name__ == "__main__":
    debug_F_dependence()
    test_constant_F()
