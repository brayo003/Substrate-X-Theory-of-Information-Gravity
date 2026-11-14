#!/usr/bin/env python3
"""Debug actual values of RHS terms"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def debug_term_values():
    """Check actual magnitudes of RHS terms"""
    print("🔍 DEBUGGING RHS TERM VALUES")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=8,
        domain_size=1e10,
        alpha=1e10, beta=1e10, gamma=1e10,
        chi=1.0, tau=1e3
    )
    
    solver.add_point_mass(1e29, (0,0))
    
    # Compute each term's maximum absolute value
    s = solver.s
    s_vel = solver.s_prev
    
    terms = {}
    
    # Wave term
    laplacian_s = solver.compute_laplacian(s)
    terms['wave'] = solver.c**2 * laplacian_s
    
    # Damping term
    terms['damping'] = -(1.0 / solver.tau) * s_vel
    
    # Advection term  
    s_v_sub = s[:,:,np.newaxis] * solver.v_sub
    terms['advection'] = -(1.0 / solver.tau) * solver.compute_divergence(s_v_sub)
    
    # Coherence term
    chi_s_u = solver.chi * s[:,:,np.newaxis] * solver.u
    terms['coherence'] = -(1.0 / solver.tau) * solver.compute_divergence(chi_s_u)
    
    # Energy term (αE)
    terms['energy'] = solver.alpha * solver.E
    
    # Energy advection term (β∇·(E v_sub))
    E_v_sub = solver.E[:,:,np.newaxis] * solver.v_sub  
    terms['energy_adv'] = solver.beta * solver.compute_divergence(E_v_sub)
    
    # Force term (γ∇·F)
    terms['force'] = solver.gamma * solver.compute_divergence(solver.F)
    
    print("Maximum absolute values of each term:")
    for name, term in terms.items():
        max_val = np.max(np.abs(term))
        print(f"  {name:12}: {max_val:.2e}")
    
    print(f"\nField values:")
    print(f"  max|E|: {np.max(np.abs(solver.E)):.2e}")
    print(f"  max|F|: {np.max(np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)):.2e}")
    print(f"  max|∇·F|: {np.max(np.abs(solver.compute_divergence(solver.F))):.2e}")
    
    # Check which terms dominate
    dominant_terms = sorted(terms.items(), key=lambda x: np.max(np.abs(x[1])), reverse=True)
    print(f"\nDominant terms:")
    for name, term in dominant_terms[:3]:
        max_val = np.max(np.abs(term))
        print(f"  {name}: {max_val:.2e}")

if __name__ == "__main__":
    debug_term_values()
