#!/usr/bin/env python3
"""Test alternative gamma terms - FIXED"""
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
    
    # Option 5: ρ (mass density - approximate)
    center_x, center_y = solver.s.shape[0]//2, solver.s.shape[1]//2
    mass_density = 1e29 / (solver.dx * solver.dx)  # dx for both directions
    print(f"5. ρ (approx): {mass_density:.2e} kg/m²")
    
    print(f"\n💡 RECOMMENDATION:")
    print("Try γ|F|² or γE instead of γ∇·F")
    print("|F|² is 10³⁰ times larger than ∇·F!")
    print("This would make gamma term actually contribute")

def test_with_modified_gamma():
    """Test with a modified gamma term"""
    print(f"\n🔧 TESTING MODIFIED GAMMA TERM")
    print("=" * 60)
    
    # Create a modified solver class
    class ModifiedSolver(SubstrateXSolver):
        def rhs(self, s, s_vel):
            # Copy original RHS but modify gamma term
            rhs_original = super().rhs(s, s_vel)
            
            # Replace gamma term with γ|F|² (much larger!)
            F_mag_sq = self.F[:,:,0]**2 + self.F[:,:,1]**2
            new_gamma_term = self.gamma * F_mag_sq
            
            # The original gamma term is already in rhs_original
            # We need to subtract it and add our new one
            old_gamma_term = self.gamma * self.compute_divergence(self.F)
            modified_rhs = rhs_original - old_gamma_term + new_gamma_term
            
            return modified_rhs
    
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
    
    # Compare term magnitudes
    F_mag_sq = solver.F[:,:,0]**2 + solver.F[:,:,1]**2
    new_gamma_val = np.max(solver.gamma * F_mag_sq)
    old_gamma_val = np.max(solver.gamma * solver.compute_divergence(solver.F))
    print(f"Old gamma term: {old_gamma_val:.2e}")
    print(f"New gamma term: {new_gamma_val:.2e}")
    print(f"Improvement: {new_gamma_val/old_gamma_val:.0e}x")
    
    # Test evolution
    s_initial = np.max(solver.s)
    for i in range(10):
        solver.step()
    s_final = np.max(solver.s)
    print(f"s field: {s_initial:.2e} → {s_final:.2e}")
    print(f"Change: {s_final - s_initial:.2e}")

if __name__ == "__main__":
    test_alternatives()
    test_with_modified_gamma()
