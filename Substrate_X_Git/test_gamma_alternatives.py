#!/usr/bin/env python3
"""Test alternative gamma terms"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

def test_alternatives():
    """Test different physical quantities for gamma term"""
    print("🎯 TESTING GAMMA TERM ALTERNATIVES")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=8,
        domain_size=1e10,
        alpha=1e10, beta=1e10, gamma=1e10,
        chi=1.0, tau=1e3
    )
    
    solver.add_point_mass(1e29, (0,0))
    
    print("Alternative gamma terms:")
    
    # Option 1: Current (∇·F)
    div_F = solver.compute_divergence(solver.F)
    print(f"1. ∇·F: {np.max(np.abs(div_F)):.2e}")
    
    # Option 2: |F|² (magnitude squared)
    F_mag_sq = solver.F[:,:,0]**2 + solver.F[:,:,1]**2
    print(f"2. |F|²: {np.max(F_mag_sq):.2e}")
    
    # Option 3: |F| (magnitude)
    F_mag = np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)
    print(f"3. |F|: {np.max(F_mag):.2e}")
    
    # Option 4: E (gravitational potential)
    print(f"4. E: {np.max(np.abs(solver.E)):.2e}")
    
    # Option 5: ρ (mass density - would need to compute)
    # For point mass: ρ ≈ mass/dx² at center
    center_x, center_y = solver.s.shape[0]//2, solver.s.shape[1]//2
    mass_density = 1e29 / (solver.dx * solver.dy)
    print(f"5. ρ (approx): {mass_density:.2e}")
    
    print(f"\n💡 RECOMMENDATION:")
    print("Try γ|F|² or γE instead of γ∇·F")
    print("|F|² represents gravitational energy density")
    print("E represents gravitational potential")

def test_with_modified_gamma():
    """Test with a modified gamma term"""
    print(f"\n🔧 TESTING MODIFIED GAMMA TERM")
    print("=" * 60)
    
    # Create a modified solver class
    class ModifiedSolver(SubstrateXSolver):
        def rhs(self, s, s_vel):
            # Copy original RHS but modify gamma term
            rhs_original = super().rhs(s, s_vel)
            
            # Replace gamma term with γ|F|²
            F_mag_sq = self.F[:,:,0]**2 + self.F[:,:,1]**2
            new_gamma_term = self.gamma * F_mag_sq
            
            # Find and replace the old gamma term
            # For now, just add it to see effect
            return rhs_original + new_gamma_term
    
    solver = ModifiedSolver(
        grid_size=8,
        domain_size=1e10,
        alpha=1e10, beta=1e10, gamma=1e10,
        chi=1.0, tau=1e3
    )
    
    solver.add_point_mass(1e29, (0,0))
    
    # Test RHS
    rhs = solver.rhs(solver.s, solver.s_prev)
    print(f"RHS with γ|F|²: [{np.min(rhs):.2e}, {np.max(rhs):.2e}]")
    
    # Test evolution
    s_initial = np.max(solver.s)
    solver.step()
    s_final = np.max(solver.s)
    print(f"s field: {s_initial:.2e} → {s_final:.2e}")
    print(f"Change: {s_final - s_initial:.2e}")

if __name__ == "__main__":
    test_alternatives()
    test_with_modified_gamma()
