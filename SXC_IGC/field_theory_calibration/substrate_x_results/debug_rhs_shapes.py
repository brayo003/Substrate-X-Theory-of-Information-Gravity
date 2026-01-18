#!/usr/bin/env python3
"""Debug RHS term shapes"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def debug_rhs_terms():
    """Check shapes of all RHS terms"""
    print("🔍 DEBUGGING RHS TERM SHAPES")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=8,
        domain_size=1e10,
        alpha=1e10, beta=1e10, gamma=1e10,
        chi=1.0, tau=1e3
    )
    
    solver.add_point_mass(1e29, (0,0))
    
    # Manually compute each term to check shapes
    s = solver.s
    s_vel = solver.s_prev
    
    print("Field shapes:")
    print(f"  s: {s.shape}")
    print(f"  E: {solver.E.shape}")
    print(f"  F: {solver.F.shape}")
    print(f"  v_sub: {solver.v_sub.shape}")
    
    print("\nRHS term shapes:")
    
    # Wave term
    laplacian_s = solver.compute_laplacian(s)
    wave_term = solver.c**2 * laplacian_s
    print(f"  wave_term: {wave_term.shape}")
    
    # Damping term  
    damping_term = -(1.0 / solver.tau) * s_vel
    print(f"  damping_term: {damping_term.shape}")
    
    # Advection term
    s_v_sub = s[:,:,np.newaxis] * solver.v_sub
    advection_term = -(1.0 / solver.tau) * solver.compute_divergence(s_v_sub)
    print(f"  advection_term: {advection_term.shape}")
    
    # Coherence term
    chi_s_u = solver.chi * s[:,:,np.newaxis] * solver.u
    coherence_term = -(1.0 / solver.tau) * solver.compute_divergence(chi_s_u)
    print(f"  coherence_term: {coherence_term.shape}")
    
    # Energy term
    energy_term = solver.alpha * solver.E
    print(f"  energy_term: {energy_term.shape}")
    
    # Energy advection term
    E_v_sub = solver.E[:,:,np.newaxis] * solver.v_sub
    energy_advection_term = solver.beta * solver.compute_divergence(E_v_sub)
    print(f"  energy_advection_term: {energy_advection_term.shape}")
    
    # Force term (this is the γ term)
    force_term = solver.gamma * solver.compute_divergence(solver.F)
    print(f"  force_term: {force_term.shape}")
    
    # Check if all terms are same shape
    terms = [wave_term, damping_term, advection_term, coherence_term, 
             energy_term, energy_advection_term, force_term]
    
    shapes = [term.shape for term in terms]
    all_same = all(shape == s.shape for shape in shapes)
    
    print(f"\nAll terms same shape as s? {all_same}")
    
    if all_same:
        print("✅ RHS term shapes are CORRECT!")
    else:
        print("❌ RHS term shapes are WRONG!")
        for i, shape in enumerate(shapes):
            print(f"  Term {i}: {shape}")

def test_rhs_computation():
    """Test if RHS actually computes"""
    print(f"\n🎯 TESTING RHS COMPUTATION")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=8,
        domain_size=1e10,
        alpha=1e10, beta=1e10, gamma=1e10, 
        chi=1.0, tau=1e3
    )
    
    solver.add_point_mass(1e29, (0,0))
    
    try:
        rhs = solver.rhs(solver.s, solver.s_prev)
        print(f"RHS computed successfully!")
        print(f"RHS shape: {rhs.shape}")
        print(f"RHS range: [{np.min(rhs):.2e}, {np.max(rhs):.2e}]")
        
        # Test if we can evolve
        print("Testing evolution...")
        solver.step()
        print("✅ Evolution successful!")
        
    except Exception as e:
        print(f"❌ RHS/Evolution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rhs_terms()
    test_rhs_computation()
