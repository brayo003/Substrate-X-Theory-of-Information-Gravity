#!/usr/bin/env python3
"""FINAL working calibration with correct k_eff calculation"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

class CorrectedSolver(SubstrateXSolver):
    """Solver with corrected mass addition and proper k_eff calculation"""
    
    def add_point_mass_corrected(self, mass, position, radius=None):
        """Corrected mass addition with proper potential"""
        if radius is None:
            radius = 2 * self.G * mass / (self.c**2)
        
        if self.dim == 2:
            x0, y0 = position
            r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
            r_reg = r + self.r_min
            
            # CORRECTED: Proper gravitational potential
            self.E += -self.G * mass / r_reg
            
            # F field (acceleration) - this is correct
            F_mag = self.G * mass / (r_reg**2)
            F_x = -F_mag * (self.X - x0) / (r_reg + 1e-10)
            F_y = -F_mag * (self.Y - y0) / (r_reg + 1e-10)
            self.F[:,:,0] += F_x
            self.F[:,:,1] += F_y
            
            print(f"Added mass {mass/self.M_sun:.3f} M_sun")

def calculate_proper_k_eff(solver, mass_kg, domain_size):
    """Calculate k_eff properly using substrate physics"""
    # Get maximum F field (acceleration)
    max_F = np.max(np.sqrt(np.sum(solver.F**2, axis=2)))
    
    # Characteristic distance for comparison
    char_distance = domain_size / 10
    
    # Newtonian acceleration at characteristic distance
    g_newton = solver.G * mass_kg / char_distance**2
    
    # The substrate X acceleration enhancement
    # k_eff = (substrate_acceleration - newtonian_acceleration) / newtonian_acceleration
    # But since F field IS the substrate acceleration:
    substrate_acceleration = max_F
    
    # k_eff represents the FRACTIONAL enhancement over Newtonian
    k_eff = (substrate_acceleration - g_newton) / g_newton
    
    print(f"    Substrate acceleration: {substrate_acceleration:.6e} m/s²")
    print(f"    Newtonian acceleration: {g_newton:.6e} m/s²")
    print(f"    Enhancement ratio: {substrate_acceleration/g_newton:.6f}")
    
    return k_eff

def test_final_calibration():
    """Final calibration test"""
    print("🎯 FINAL CALIBRATION WITH CORRECT k_eff")
    print("=" * 60)
    
    # We need to find parameters that give k_eff ≈ 2e-4 for solar, 0.3 for galactic
    # This means substrate acceleration should be slightly higher than Newtonian
    
    test_params = [
        {
            'name': 'SOLAR SYSTEM',
            'domain_size': 2e11,
            'mass': 2e30,
            'target_k_eff': 2e-4,
            'alpha': 1e-10,  # Need to tune these
            'beta': 1e-10,
            'gamma': 1e-10
        },
        {
            'name': 'GALACTIC SCALE',
            'domain_size': 3e20, 
            'mass': 1e11 * 1.989e30,
            'target_k_eff': 0.3,
            'alpha': 1e-10,  # Same physical laws
            'beta': 1e-10,
            'gamma': 1e-10
        }
    ]
    
    for params in test_params:
        print(f"\n🔭 {params['name']}:")
        print(f"   Mass: {params['mass']/1.989e30:.0f} M_sun")
        print(f"   Domain: {params['domain_size']:.1e} m")
        
        solver = CorrectedSolver(
            grid_size=32,
            domain_size=params['domain_size'],
            alpha=params['alpha'],
            beta=params['beta'],
            gamma=params['gamma'],
            chi=1.0,
            tau=1e3
        )
        
        solver.add_point_mass_corrected(params['mass'], (0,0))
        
        k_eff = calculate_proper_k_eff(solver, params['mass'], params['domain_size'])
        
        print(f"   k_eff = {k_eff:.6f}")
        print(f"   Target = {params['target_k_eff']:.6f}")
        
        if abs(k_eff - params['target_k_eff']) < 0.1 * params['target_k_eff']:
            print("   ✅ GOOD MATCH!")
        else:
            print("   ❌ NEEDS TUNING")

def understand_k_eff_physics():
    """Understand what k_eff should physically represent"""
    print(f"\n🔍 PHYSICS OF k_eff")
    print("=" * 60)
    
    print("k_eff should represent the FRACTIONAL enhancement of gravity")
    print("due to substrate X effects:")
    print("")
    print("  g_total = g_newton × (1 + k_eff)")
    print("")
    print("So:")
    print("  k_eff = 2e-4  means 0.02% enhancement (solar system)")
    print("  k_eff = 0.3    means 30% enhancement (galactic scales)")
    print("")
    print("In our solver:")
    print("  F field represents substrate acceleration")
    print("  So: k_eff = (F - g_newton) / g_newton")
    print("")
    print("We need to tune alpha, beta, gamma so that:")
    print("  F ≈ g_newton × (1 + target_k_eff)")

if __name__ == "__main__":
    test_final_calibration()
    understand_k_eff_physics()
