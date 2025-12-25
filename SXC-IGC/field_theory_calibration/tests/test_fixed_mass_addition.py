#!/usr/bin/env python3
"""Test with corrected mass addition"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

class FixedSubstrateXSolver(SubstrateXSolver):
    """Substrate X solver with corrected mass addition"""
    
    def add_point_mass_fixed(self, mass, position, radius=None):
        """
        CORRECTED version of add_point_mass
        """
        if radius is None:
            radius = 2 * self.G * mass / (self.c**2)  # Schwarzschild radius
        
        if self.dim == 2:
            x0, y0 = position
            r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
            r_reg = r + self.r_min  # Regularized distance
            
            # CORRECTION: E field should be gravitational potential
            # E = -G·M / r  (energy per unit mass, or potential)
            # Not: -G·M·ρ / r which has wrong units
            self.E += -self.G * mass / r_reg
            
            # F field is correct: F = G·M / r² (acceleration)
            F_mag = self.G * mass / (r_reg**2)
            F_x = -F_mag * (self.X - x0) / (r_reg + 1e-10)
            F_y = -F_mag * (self.Y - y0) / (r_reg + 1e-10)
            self.F[:,:,0] += F_x
            self.F[:,:,1] += F_y
            
            print(f"Added mass {mass/self.M_sun:.3f} M_sun at ({x0/1e9:.2f}, {y0/1e9:.2f}) billion m")

def test_fixed_calibration():
    """Test calibration with corrected mass addition"""
    print("🎯 CALIBRATION WITH FIXED MASS ADDITION")
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
            'mass': 1e11 * 1.989e30,  # 100 billion solar masses
            'target_k_eff': 0.3
        }
    ]
    
    physical_params = {'alpha': 1.0, 'beta': 1.0, 'gamma': 1.0, 'chi': 1.0, 'tau': 1e3}
    
    for case in test_cases:
        print(f"\n🔭 {case['name']}:")
        print(f"   Mass: {case['mass']/1.989e30:.0f} M_sun")
        
        # Test with ORIGINAL (buggy) method
        solver_orig = SubstrateXSolver(
            grid_size=32,
            domain_size=case['domain_size'],
            **physical_params
        )
        solver_orig.add_point_mass(case['mass'], (0,0))
        
        # Test with FIXED method  
        solver_fixed = FixedSubstrateXSolver(
            grid_size=32, 
            domain_size=case['domain_size'],
            **physical_params
        )
        solver_fixed.add_point_mass_fixed(case['mass'], (0,0))
        
        print(f"   ORIGINAL method:")
        print(f"     E: [{np.min(solver_orig.E):.2e}, {np.max(solver_orig.E):.2e}]")
        print(f"     F: {np.max(np.sqrt(np.sum(solver_orig.F**2, axis=2))):.6e}")
        
        print(f"   FIXED method:")
        print(f"     E: [{np.min(solver_fixed.E):.2e}, {np.max(solver_fixed.E):.2e}]")
        print(f"     F: {np.max(np.sqrt(np.sum(solver_fixed.F**2, axis=2))):.6e}")
        
        # Calculate k_eff from F field (acceleration)
        max_F_fixed = np.max(np.sqrt(np.sum(solver_fixed.F**2, axis=2)))
        
        # Compare to Newtonian acceleration at characteristic distance
        char_distance = case['domain_size'] / 10  # Characteristic scale
        g_newton = solver_fixed.G * case['mass'] / char_distance**2
        
        k_eff = max_F_fixed / g_newton if g_newton > 0 else 0
        
        print(f"   k_eff (F/g_newton): {k_eff:.6f}")
        print(f"   Target: {case['target_k_eff']:.6f}")

def analyze_units():
    """Analyze the units issue in the original method"""
    print(f"\n🔍 UNITS ANALYSIS OF THE BUG")
    print("=" * 60)
    
    print("ORIGINAL code (line 178-179):")
    print("  density_scale = mass / (4 * np.pi * r_reg**3)  # [kg/m³]")
    print("  self.E += -self.G * mass * density_scale / r_reg")
    print("")
    print("UNITS ANALYSIS:")
    print("  G: m³/kg/s²")
    print("  mass: kg") 
    print("  density_scale: kg/m³")
    print("  r_reg: m")
    print("  Result: (m³/kg/s²) * kg * (kg/m³) / m = kg/s²")
    print("  ❌ E field has units kg/s² (energy), but should be m²/s² (potential)")
    print("")
    print("CORRECTED version:")
    print("  self.E += -self.G * mass / r_reg")
    print("  Units: (m³/kg/s²) * kg / m = m²/s² ✅")
    print("  This is gravitational potential (energy per unit mass)")

if __name__ == "__main__":
    test_fixed_calibration()
    analyze_units()
