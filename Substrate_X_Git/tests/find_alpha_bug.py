#!/usr/bin/env python3
"""
FIND THE α TERM BUG
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def debug_alpha_term():
    """Find why αE term fails"""
    print("🔍 DEBUGGING α TERM FAILURE")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=8,
        domain_size=1e10,
        alpha=1e10, beta=0, gamma=0,
        chi=1.0, tau=1e3
    )
    
    solver.add_point_mass(1e29, (0,0))
    
    print("Field shapes:")
    print(f"  s: {solver.s.shape}")
    print(f"  E: {solver.E.shape}") 
    print(f"  F: {solver.F.shape}")
    print(f"  v_sub: {solver.v_sub.shape}")
    
    print("\nTesting αE term directly:")
    alpha_term = solver.alpha * solver.E
    print(f"  αE shape: {alpha_term.shape}")
    print(f"  αE max: {np.max(alpha_term):.2e}")
    
    print("\nTesting β∇·(E v_sub) term:")
    try:
        # E * v_sub should be element-wise
        E_v_sub = solver.E[:,:,np.newaxis] * solver.v_sub  # Broadcast correctly
        print(f"  E * v_sub shape: {E_v_sub.shape}")
        
        div_E_v_sub = solver.compute_divergence(E_v_sub)
        print(f"  ∇·(E v_sub) shape: {div_E_v_sub.shape}")
        
        beta_term = solver.beta * div_E_v_sub
        print(f"  β∇·(E v_sub) shape: {beta_term.shape}")
        print(f"  β∇·(E v_sub) max: {np.max(beta_term):.2e}")
        
    except Exception as e:
        print(f"  β term failed: {e}")
    
    print("\nTesting γF term:")
    try:
        gamma_term = solver.gamma * solver.F
        print(f"  γF shape: {gamma_term.shape}")
        print(f"  γF max: {np.max(gamma_term):.2e}")
    except Exception as e:
        print(f"  γ term failed: {e}")

def test_rhs_manual():
    """Test RHS computation manually"""
    print(f"\n🎯 MANUAL RHS COMPUTATION")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=8,
        domain_size=1e10, 
        alpha=1e10, beta=1e10, gamma=1e10,
        chi=1.0, tau=1e3
    )
    
    solver.add_point_mass(1e29, (0,0))
    
    # Compute RHS manually
    rhs_manual = np.zeros_like(solver.s)
    
    # αE term (scalar field)
    alpha_term = solver.alpha * solver.E
    print(f"αE term: {alpha_term.shape}, max={np.max(alpha_term):.2e}")
    
    # β∇·(E v_sub) term  
    E_v_sub = solver.E[:,:,np.newaxis] * solver.v_sub
    div_E_v_sub = solver.compute_divergence(E_v_sub)
    beta_term = solver.beta * div_E_v_sub
    print(f"β∇·(E v_sub) term: {beta_term.shape}, max={np.max(beta_term):.2e}")
    
    # γF term - PROBLEM: F is vector, needs to be scalar?
    # γF doesn't make sense dimensionally - F is acceleration (vector)
    # but RHS needs to be scalar for s field evolution
    print(f"γF shape: {solver.F.shape}")
    print("🚨 γF TERM IS THE PROBLEM!")
    print("F is vector field (acceleration), but RHS needs scalar")
    print("This suggests γ should multiply ∇·F or F², not F directly")

if __name__ == "__main__":
    debug_alpha_term()
    test_rhs_manual()
    
    print(f"\n🚨 MATHEMATICAL INCONSISTENCIES FOUND:")
    print("1. γF term: F is vector, but RHS needs scalar - DIMENSIONAL ERROR")
    print("2. αE term: Might have shape broadcasting issues") 
    print("3. The master equation has dimensional inconsistencies")
    print("4. γ should probably multiply ∇·F or |F|, not F directly")
