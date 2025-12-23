#!/usr/bin/env python3
"""
DIAGNOSE WHY SUBSTRATE FIELD WON'T EVOLVE
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver_fixed_gamma import SubstrateXSolver

def diagnose_evolution():
    """Diagnose why s field won't evolve"""
    print("🔍 DIAGNOSING SUBSTRATE EVOLUTION")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1e0, beta=1e0, gamma=1e0,  # Strong parameters
        chi=1.0, tau=1e3
    )
    
    mass = 2e30
    solver.add_point_mass(mass, (0,0))
    
    print("1. Initial conditions:")
    print(f"   s field: {np.max(solver.s):.2e}")
    print(f"   E field: {np.max(solver.E):.2e}")
    print(f"   F field: {np.max(np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)):.2e}")
    
    print("\n2. Testing RHS computation:")
    rhs = solver.rhs(solver.s, solver.s_prev)
    print(f"   RHS range: [{np.min(rhs):.2e}, {np.max(rhs):.2e}]")
    
    # Check if RHS is actually driving evolution
    if np.max(np.abs(rhs)) < 1e-10:
        print("   ❌ RHS is essentially ZERO - no evolution will happen!")
    else:
        print("   ✅ RHS has meaningful values")
    
    print("\n3. Testing individual step:")
    s_old = solver.s.copy()
    try:
        solver.step()
        s_new = solver.s.copy()
        change = np.max(np.abs(s_new - s_old))
        print(f"   Step completed, s change: {change:.2e}")
        
        if change < 1e-15:
            print("   ❌ NO EVOLUTION - s field is dead!")
        else:
            print("   ✅ Evolution detected!")
            
    except Exception as e:
        print(f"   ❌ Step failed: {e}")
    
    print("\n4. Testing with initial s field perturbation:")
    solver2 = SubstrateXSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1e0, beta=1e0, gamma=1e0,
        chi=1.0, tau=1e3
    )
    
    # Add small perturbation to s field
    solver2.s += 1e-10 * np.random.rand(*solver2.s.shape)
    solver2.add_point_mass(mass, (0,0))
    
    s2_old = solver2.s.copy()
    try:
        solver2.step()
        s2_new = solver2.s.copy()
        change2 = np.max(np.abs(s2_new - s2_old))
        print(f"   With perturbation, s change: {change2:.2e}")
    except Exception as e:
        print(f"   Step with perturbation failed: {e}")

def test_minimal_working_case():
    """Test if ANY evolution works"""
    print(f"\n🎯 TESTING MINIMAL WORKING CASE")
    print("=" * 60)
    
    # Try with just wave equation (no sources)
    solver = SubstrateXSolver(
        grid_size=8,
        domain_size=1e10,
        alpha=0, beta=0, gamma=0,  # No coupling
        chi=0, tau=1e3
    )
    
    # Add initial wave
    solver.s[4,4] = 1e-10
    
    print("Testing pure wave evolution (no gravity coupling):")
    s_old = solver.s.copy()
    try:
        solver.step()
        s_new = solver.s.copy()
        change = np.max(np.abs(s_new - s_old))
        print(f"   Wave evolution: {change:.2e}")
        
        if change > 1e-15:
            print("   ✅ Wave equation works!")
        else:
            print("   ❌ Even wave equation is broken!")
            
    except Exception as e:
        print(f"   ❌ Wave evolution failed: {e}")

if __name__ == "__main__":
    diagnose_evolution()
    test_minimal_working_case()
    
    print(f"\n🚨 FUNDAMENTAL DIAGNOSIS:")
    print("If the substrate field won't evolve even with strong parameters,")
    print("there might be issues with:")
    print("1. The time integration scheme")
    print("2. Boundary conditions killing evolution") 
    print("3. Numerical damping being too strong")
    print("4. The field initialization being exactly zero")
