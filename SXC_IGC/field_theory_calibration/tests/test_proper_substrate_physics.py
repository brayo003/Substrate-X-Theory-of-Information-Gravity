#!/usr/bin/env python3
"""Proper substrate physics with modified gravity"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

class SubstrateXPhysicsSolver(SubstrateXSolver):
    """Solver with proper substrate-modified gravity"""
    
    def add_point_mass_substrate(self, mass, position, k_eff=0.0, radius=None):
        """
        Add mass with substrate-modified gravity
        
        Parameters:
        -----------
        mass : float
            Mass in kg
        position : tuple
            (x, y) position
        k_eff : float
            Desired enhancement factor: g_substrate = g_newton × (1 + k_eff)
        radius : float, optional
            Regularization radius
        """
        if radius is None:
            radius = 2 * self.G * mass / (self.c**2)
        
        if self.dim == 2:
            x0, y0 = position
            r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
            r_reg = r + self.r_min
            
            # E field: gravitational potential (corrected)
            self.E += -self.G * mass / r_reg
            
            # F field: substrate-MODIFIED acceleration
            # g_substrate = g_newton × (1 + k_eff)
            g_newton = self.G * mass / (r_reg**2)
            g_substrate = g_newton * (1 + k_eff)
            
            F_x = -g_substrate * (self.X - x0) / (r_reg + 1e-10)
            F_y = -g_substrate * (self.Y - y0) / (r_reg + 1e-10)
            self.F[:,:,0] += F_x
            self.F[:,:,1] += F_y
            
            print(f"Added mass {mass/self.M_sun:.3f} M_sun with k_eff={k_eff}")

def test_direct_k_eff_control():
    """Test directly controlling k_eff in mass addition"""
    print("🎯 DIRECT k_eff CONTROL IN MASS ADDITION")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'SOLAR SYSTEM',
            'domain_size': 2e11,
            'mass': 2e30,
            'target_k_eff': 2e-4
        },
        {
            'name': 'GALACTIC SCALE',
            'domain_size': 3e20,
            'mass': 1e11 * 1.989e30, 
            'target_k_eff': 0.3
        }
    ]
    
    for case in test_cases:
        print(f"\n🔭 {case['name']}:")
        print(f"   Mass: {case['mass']/1.989e30:.0f} M_sun")
        
        solver = SubstrateXPhysicsSolver(
            grid_size=32,
            domain_size=case['domain_size'],
            alpha=1.0,  # These will now affect the DYNAMICS, not static field
            beta=1.0,
            gamma=1.0,
            chi=1.0,
            tau=1e3
        )
        
        # Add mass with DESIRED k_eff directly
        solver.add_point_mass_substrate(case['mass'], (0,0), k_eff=case['target_k_eff'])
        
        # Verify the enhancement
        max_F = np.max(np.sqrt(np.sum(solver.F**2, axis=2)))
        char_distance = case['domain_size'] / 10
        g_newton = solver.G * case['mass'] / char_distance**2
        
        actual_k_eff = (max_F - g_newton) / g_newton
        
        print(f"   Requested k_eff: {case['target_k_eff']:.6f}")
        print(f"   Actual k_eff: {actual_k_eff:.6f}")
        print(f"   Error: {abs(actual_k_eff - case['target_k_eff'])/case['target_k_eff']*100:.1f}%")

def understand_parameter_roles():
    """Understand what alpha, beta, gamma actually do"""
    print(f"\n🔍 UNDERSTANDING PARAMETER ROLES")
    print("=" * 60)
    
    print("From the master equation:")
    print("  ∂²s/∂t² = c²∇²s - (1/τ)∂s/∂t - (1/τ)∇·(s v_sub + χ s u)")
    print("           + αE + β∇·(E v_sub) + γF - σ_irr")
    print("")
    print("Parameter roles:")
    print("  α: Couples E field (potential) to s field evolution")
    print("  β: Couples E field transport to s field") 
    print("  γ: Couples F field (acceleration) to s field")
    print("")
    print("So α, β, γ affect HOW the substrate field s evolves,")
    print("but the static F field (acceleration) is set by mass addition.")
    print("")
    print("For calibration, we have two approaches:")
    print("  1. Set k_eff directly in mass addition (static case)")
    print("  2. Tune α,β,γ to get right s field evolution (dynamic case)")

def test_dynamic_evolution():
    """Test if α,β,γ affect the acceleration through s field evolution"""
    print(f"\n🔬 TESTING DYNAMIC EFFECTS OF α,β,γ")
    print("=" * 60)
    
    # Test if evolving the s field changes the effective acceleration
    solver = SubstrateXPhysicsSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1e-5,  # Try different values
        beta=1e-5,
        gamma=1e-5, 
        chi=1.0,
        tau=1e3
    )
    
    mass = 2e30
    solver.add_point_mass_substrate(mass, (0,0), k_eff=2e-4)
    
    print("Initial state:")
    max_F_initial = np.max(np.sqrt(np.sum(solver.F**2, axis=2)))
    print(f"  Max F: {max_F_initial:.6e}")
    
    # Evolve and see if F field changes
    print("Evolving 100 steps...")
    for i in range(100):
        solver.step()
    
    max_F_final = np.max(np.sqrt(np.sum(solver.F**2, axis=2)))
    print(f"After evolution:")
    print(f"  Max F: {max_F_final:.6e}")
    print(f"  Change: {(max_F_final - max_F_initial)/max_F_initial*100:.2f}%")

if __name__ == "__main__":
    test_direct_k_eff_control()
    understand_parameter_roles()
    test_dynamic_evolution()
