#!/usr/bin/env python3
"""
FINAL FIX: Modify the solver to properly apply k_eff enhancement
"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Let's patch the original solver method
from src.numerical_solver import SubstrateXSolver

# Save original method
original_add_point_mass = SubstrateXSolver.add_point_mass

def patched_add_point_mass(self, mass, position, k_eff=0.0, radius=None):
    """
    Patched version that properly applies k_eff enhancement
    """
    if radius is None:
        radius = 2 * self.G * mass / (self.c**2)
    
    if self.dim == 2:
        x0, y0 = position
        r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
        r_reg = r + self.r_min
        
        # CORRECTED: Proper gravitational potential
        self.E += -self.G * mass / r_reg
        
        # F field: Apply substrate enhancement DIRECTLY
        # The key is to use += carefully to avoid overwriting
        g_newton = self.G * mass / (r_reg**2)
        g_substrate = g_newton * (1 + k_eff)
        
        # Calculate the ENHANCEMENT component only
        g_enhancement = g_newton * k_eff
        
        F_x_enhance = -g_enhancement * (self.X - x0) / (r_reg + 1e-10)
        F_y_enhance = -g_enhancement * (self.Y - y0) / (r_reg + 1e-10)
        
        # Add enhancement to existing F field
        self.F[:,:,0] += F_x_enhance
        self.F[:,:,1] += F_y_enhance
        
        print(f"Added mass {mass/self.M_sun:.3f} M_sun with k_eff={k_eff}")

# Apply patch
SubstrateXSolver.add_point_mass = patched_add_point_mass

def test_patched_calibration():
    """Test with patched solver"""
    print("🎯 TESTING PATCHED SOLVER WITH k_eff ENHANCEMENT")
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
        print(f"   Target k_eff: {case['target_k_eff']:.6f}")
        
        solver = SubstrateXSolver(
            grid_size=32,
            domain_size=case['domain_size'], 
            alpha=1.0, beta=1.0, gamma=1.0, chi=1.0, tau=1e3
        )
        
        # Store initial F field for comparison
        F_initial = solver.F.copy()
        
        # Add mass with enhancement
        solver.add_point_mass(case['mass'], (0,0), k_eff=case['target_k_eff'])
        
        # Calculate the actual enhancement applied
        F_final = solver.F.copy()
        F_enhancement = F_final - F_initial
        
        F_magnitude_enhance = np.sqrt(F_enhancement[:,:,0]**2 + F_enhancement[:,:,1]**2)
        max_enhance = np.max(F_magnitude_enhance)
        
        # Measure at characteristic distance
        char_distance = case['domain_size'] / 10
        distances = np.sqrt(solver.X**2 + solver.Y**2)
        char_idx = np.unravel_index(np.argmin(np.abs(distances - char_distance)), distances.shape)
        
        F_magnitude = np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)
        F_at_char = F_magnitude[char_idx]
        r_measured = distances[char_idx]
        
        g_newton = solver.G * case['mass'] / (r_measured + solver.r_min)**2
        k_eff_measured = (F_at_char - g_newton) / g_newton
        
        print(f"   Measurement at r={r_measured:.1e}m:")
        print(f"     F total = {F_at_char:.6e} m/s²")
        print(f"     g_newton = {g_newton:.6e} m/s²")
        print(f"     k_eff measured = {k_eff_measured:.6f}")
        print(f"     Max enhancement applied = {max_enhance:.6e} m/s²")

def test_incremental_enhancement():
    """Test applying enhancement incrementally"""
    print(f"\n🔧 TESTING INCREMENTAL ENHANCEMENT")
    print("=" * 60)
    
    solver = SubstrateXSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1.0, beta=1.0, gamma=1.0, chi=1.0, tau=1e3
    )
    
    mass = 2e30
    
    # First add Newtonian baseline
    solver.add_point_mass(mass, (0,0), k_eff=0.0)
    
    F_baseline = solver.F.copy()
    F_magnitude_baseline = np.sqrt(F_baseline[:,:,0]**2 + F_baseline[:,:,1]**2)
    
    char_distance = 2e10
    distances = np.sqrt(solver.X**2 + solver.Y**2)
    char_idx = np.unravel_index(np.argmin(np.abs(distances - char_distance)), distances.shape)
    
    F_baseline_char = F_magnitude_baseline[char_idx]
    g_newton = solver.G * mass / (distances[char_idx] + solver.r_min)**2
    
    print(f"Baseline (k_eff=0):")
    print(f"  F at r={distances[char_idx]:.1e}m: {F_baseline_char:.6e}")
    print(f"  g_newton: {g_newton:.6e}")
    print(f"  Baseline k_eff: {(F_baseline_char - g_newton)/g_newton:.6f}")
    
    # Now add enhancement
    k_eff_target = 2e-4
    solver.add_point_mass(0, (0,0), k_eff=k_eff_target)  # Add only enhancement
    
    F_enhanced = solver.F.copy() 
    F_magnitude_enhanced = np.sqrt(F_enhanced[:,:,0]**2 + F_enhanced[:,:,1]**2)
    F_enhanced_char = F_magnitude_enhanced[char_idx]
    
    k_eff_final = (F_enhanced_char - g_newton) / g_newton
    
    print(f"After enhancement (k_eff={k_eff_target}):")
    print(f"  F at same r: {F_enhanced_char:.6e}")
    print(f"  Final k_eff: {k_eff_final:.6f}")

if __name__ == "__main__":
    test_patched_calibration()
    test_incremental_enhancement()
