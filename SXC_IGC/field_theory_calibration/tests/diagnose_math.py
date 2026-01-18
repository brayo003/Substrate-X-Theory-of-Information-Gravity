#!/usr/bin/env python3
"""
DIAGNOSE THE BROKEN MATHEMATICS
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def diagnose_coupling():
    """Test if the fields actually couple to each other"""
    print("🔍 DIAGNOSING FIELD COUPLING")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1e10,  # Strong coupling
        beta=1e10,
        gamma=1e10,
        chi=1.0,
        tau=1e3
    )
    
    print("1. Initial state:")
    print(f"   s field: {np.max(solver.s):.2e}")
    print(f"   E field: {np.max(solver.E):.2e}") 
    print(f"   F field: {np.max(np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)):.2e}")
    
    print("\n2. After adding mass:")
    solver.add_point_mass(2e30, (0,0))
    print(f"   s field: {np.max(solver.s):.2e} (should respond to mass)")
    print(f"   E field: {np.max(solver.E):.2e} (changed - good)")
    print(f"   F field: {np.max(np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)):.2e} (changed - good)")
    
    print("\n3. Testing RHS computation:")
    try:
        rhs = solver.rhs(solver.s, solver.s_prev)
        print(f"   Max RHS: {np.max(np.abs(rhs)):.2e}")
        print(f"   RHS should drive s evolution")
        
        # Check individual terms in RHS
        print(f"\n4. RHS components:")
        alpha_term = solver.alpha * solver.E
        beta_term = solver.beta * solver.compute_divergence(solver.E * solver.v_sub)
        gamma_term = solver.gamma * solver.F
        
        print(f"   αE term: {np.max(np.abs(alpha_term)):.2e}")
        print(f"   β∇·(E v_sub) term: {np.max(np.abs(beta_term)):.2e}") 
        print(f"   γF term: {np.max(np.abs(gamma_term)):.2e}")
        
        print(f"\n5. Compare to other terms:")
        laplacian_term = solver.c**2 * solver.compute_laplacian(solver.s)
        damping_term = (1/solver.tau) * (solver.s - solver.s_prev) / solver.dt
        
        print(f"   c²∇²s term: {np.max(np.abs(laplacian_term)):.2e}")
        print(f"   damping term: {np.max(np.abs(damping_term)):.2e}")
        
    except Exception as e:
        print(f"   RHS failed: {e}")

def test_minimal_physics():
    """Test if basic physics works at all"""
    print(f"\n🎯 TESTING MINIMAL PHYSICS")
    print("=" * 60)
    
    # Test with just ONE coupling term at a time
    tests = [
        {'alpha': 1e10, 'beta': 0, 'gamma': 0, 'name': 'α ONLY'},
        {'alpha': 0, 'beta': 1e10, 'gamma': 0, 'name': 'β ONLY'},
        {'alpha': 0, 'beta': 0, 'gamma': 1e10, 'name': 'γ ONLY'},
    ]
    
    for test in tests:
        print(f"\n🔬 {test['name']}:")
        solver = SubstrateXSolver(
            grid_size=8,  # Small for stability
            domain_size=1e10,
            alpha=test['alpha'],
            beta=test['beta'], 
            gamma=test['gamma'],
            chi=1.0,
            tau=1e3
        )
        
        solver.add_point_mass(1e29, (0,0))  # Small mass
        
        s_initial = np.max(solver.s)
        
        # Try one step
        try:
            solver.step()
            s_final = np.max(solver.s)
            change = s_final - s_initial
            print(f"   s: {s_initial:.2e} → {s_final:.2e} (Δ={change:.2e})")
            
            if abs(change) > 1e-15:
                print(f"   ✅ COUPLING WORKS!")
            else:
                print(f"   ❌ NO COUPLING")
                
        except Exception as e:
            print(f"   ❌ CRASHED: {e}")

if __name__ == "__main__":
    diagnose_coupling()
    test_minimal_physics()
    
    print(f"\n🚨 FUNDAMENTAL ISSUES IDENTIFIED:")
    print("1. The RHS terms (αE, β∇·(E v_sub), γF) are likely too weak")
    print("2. There's no feedback from s field back to E/F fields")
    print("3. The timescales/parameters don't match physical scales")
    print("4. The mathematical formulation might be inconsistent")
