#!/usr/bin/env python3
"""Debug why F field becomes zero at large scales"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def debug_scaling():
    """Understand the scaling problem"""
    print("🎯 DEBUGGING SCALING ISSUE")
    print("=" * 60)
    
    scales = [
        {'name': 'SOLAR', 'domain': 2e11, 'mass': 2e30},
        {'name': 'GALACTIC', 'domain': 3e20, 'mass': 1e41},
    ]
    
    for scale in scales:
        print(f"\n🔭 {scale['name']} SCALE:")
        print(f"   Domain: {scale['domain']:.1e} m")
        print(f"   Mass: {scale['mass']/1.989e30:.0f} M_sun")
        
        solver = SubstrateXSolver(
            grid_size=16,
            domain_size=scale['domain'],
            alpha=1.0,
            beta=1.0,
            gamma=0.1,
            chi=1.0,
            tau=1e3
        )
        
        print(f"   dx: {solver.dx:.2e} m")
        print(f"   Scaled gamma: {solver.gamma:.2e}")
        
        # Check initial F field
        print(f"   Initial F: max={np.max(np.abs(solver.F)):.6f}")
        
        # Add mass
        solver.add_point_mass(scale['mass'], (0,0))
        
        print(f"   After mass: F max={np.max(np.abs(solver.F)):.6f}")
        print(f"   After mass: E max={np.max(np.abs(solver.E)):.2e}")
        
        # Check if mass was actually added to the right grid cell
        center_x, center_y = solver.s.shape[0]//2, solver.s.shape[1]//2
        print(f"   Center cell: ({center_x}, {center_y})")
        print(f"   F at center: {solver.F[center_x, center_y, :]}")
        
        # Calculate k_eff
        max_F = np.max(np.abs(solver.F))
        if max_F > 0:
            k_eff = max_F / (solver.gamma * scale['mass'])
            print(f"   k_eff = {k_eff:.6f}")
        else:
            print(f"   k_eff = UNDEFINED (F field is zero)")

def check_mass_addition():
    """Check if mass addition works correctly at different scales"""
    print(f"\n🔍 CHECKING MASS ADDITION ALGORITHM")
    print("=" * 60)
    
    # Let's look at the add_point_mass method
    print("The issue might be in add_point_mass() method:")
    print(" - At solar scales: r_reg might be reasonable")
    print(" - At galactic scales: r_reg might be too large/small")
    print(" - Or the regularization might fail at extreme scales")

if __name__ == "__main__":
    debug_scaling()
    check_mass_addition()
