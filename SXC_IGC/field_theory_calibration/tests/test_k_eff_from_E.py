#!/usr/bin/env python3
"""Test if k_eff should be calculated from E field instead of s"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def test_k_eff_from_E():
    """Maybe k_eff should be based on E field since mass strongly affects it"""
    print("🎯 TESTING k_eff FROM E FIELD")
    print("=" * 60)
    
    # Use moderate parameters
    solver = SubstrateXSolver(
        grid_size=32,
        domain_size=2e11,
        alpha=1.0,
        beta=1.0,
        gamma=1.0,
        chi=1.0, 
        tau=1e3
    )
    
    mass_kg = 2e30
    
    # Add mass and see which fields change
    print("Before mass addition:")
    print(f"  E: {np.max(np.abs(solver.E)):.2e}")
    print(f"  F: {np.max(np.abs(solver.F)):.2e}") 
    print(f"  s: {np.max(np.abs(solver.s)):.2e}")
    
    solver.add_point_mass(mass_kg, (0,0))
    
    print("\nAfter mass addition:")
    print(f"  E: {np.max(np.abs(solver.E)):.2e} (changed by {np.max(np.abs(solver.E)):.0e})")
    print(f"  F: {np.max(np.abs(solver.F)):.2e} (changed by {np.max(np.abs(solver.F)):.0e})")
    print(f"  s: {np.max(np.abs(solver.s)):.2e} (changed by {np.max(np.abs(solver.s)):.0e})")
    
    # Calculate potential k_eff values from different fields
    k_eff_E = np.max(np.abs(solver.E)) / (solver.alpha * mass_kg) if solver.alpha > 0 else 0
    k_eff_F = np.max(np.abs(solver.F)) / (solver.gamma * mass_kg) if solver.gamma > 0 else 0
    k_eff_s = np.max(np.abs(solver.s)) / (solver.gamma * mass_kg) if solver.gamma > 0 else 0
    
    print(f"\nPotential k_eff values:")
    print(f"  From E field: {k_eff_E:.2e}")
    print(f"  From F field: {k_eff_F:.2e}")
    print(f"  From s field: {k_eff_s:.2e}")
    
    print(f"\n💡 OBSERVATION: E field changes by ~10¹⁰, s field changes by ~10⁻¹³")
    print(f"   This suggests k_eff might be better calculated from E field!")

if __name__ == "__main__":
    test_k_eff_from_E()
