#!/usr/bin/env python3
"""Debug WHERE we should measure the F field for k_eff calculation"""
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.numerical_solver import SubstrateXSolver

class DebugSolver(SubstrateXSolver):
    def add_point_mass_debug(self, mass, position, k_eff=0.0):
        """Add mass with debug information"""
        radius = 2 * self.G * mass / (self.c**2)
        x0, y0 = position
        
        if self.dim == 2:
            r = np.sqrt((self.X - x0)**2 + (self.Y - y0)**2)
            r_reg = r + self.r_min
            
            # E field
            self.E += -self.G * mass / r_reg
            
            # F field with desired enhancement
            g_newton = self.G * mass / (r_reg**2)
            g_substrate = g_newton * (1 + k_eff)
            
            F_x = -g_substrate * (self.X - x0) / (r_reg + 1e-10)
            F_y = -g_substrate * (self.Y - y0) / (r_reg + 1e-10)
            self.F[:,:,0] += F_x
            self.F[:,:,1] += F_y
            
            # Debug: Check what we actually set vs what we measure
            center_x, center_y = self.s.shape[0]//2, self.s.shape[1]//2
            
            # Check at different distances from center
            print(f"Debug - Mass addition at ({x0:.1f}, {y0:.1f}):")
            print(f"  Center cell: ({center_x}, {center_y})")
            
            # Check immediate neighbors
            for dx, dy in [(0,0), (1,0), (2,0), (3,0)]:
                dist = np.sqrt((dx*self.dx)**2 + (dy*self.dy)**2)
                if center_x+dx < self.s.shape[0] and center_y+dy < self.s.shape[1]:
                    F_val = np.sqrt(self.F[center_x+dx, center_y+dy, 0]**2 + 
                                  self.F[center_x+dx, center_y+dy, 1]**2)
                    g_newton_local = self.G * mass / (dist + self.r_min)**2
                    g_set = g_newton_local * (1 + k_eff)
                    print(f"  At r={dist:.1e}m: F={F_val:.6e}, g_set={g_set:.6e}, ratio={F_val/g_set:.6f}")

def debug_measurement():
    """Debug where and how to measure F field"""
    print("🎯 DEBUGGING F FIELD MEASUREMENT")
    print("=" * 60)
    
    solver = DebugSolver(
        grid_size=16,
        domain_size=2e11,
        alpha=1.0, beta=1.0, gamma=1.0, chi=1.0, tau=1e3
    )
    
    mass = 2e30
    target_k_eff = 2e-4
    
    print(f"Test case: {mass/1.989e30:.1f} M_sun, target k_eff={target_k_eff}")
    solver.add_point_mass_debug(mass, (0,0), k_eff=target_k_eff)
    
    # Now analyze the entire F field
    print(f"\nF field analysis:")
    F_magnitude = np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)
    
    # Find maximum and its location
    max_idx = np.unravel_index(np.argmax(F_magnitude), F_magnitude.shape)
    max_F = F_magnitude[max_idx]
    max_x = solver.X[max_idx]
    max_y = solver.Y[max_idx] 
    max_r = np.sqrt(max_x**2 + max_y**2)
    
    print(f"  Global max F: {max_F:.6e} at r={max_r:.1e}m")
    
    # What should it be at that distance?
    g_newton_max = solver.G * mass / (max_r + solver.r_min)**2
    g_set_max = g_newton_max * (1 + target_k_eff)
    print(f"  Expected at r={max_r:.1e}m: {g_set_max:.6e}")
    print(f"  Ratio (actual/expected): {max_F/g_set_max:.6f}")
    
    # Check at characteristic distance (domain_size/10)
    char_distance = solver.domain_size / 10
    print(f"\nAt characteristic distance r={char_distance:.1e}m:")
    
    # Find closest grid point to this distance
    distances = np.sqrt(solver.X**2 + solver.Y**2)
    char_idx = np.unravel_index(np.argmin(np.abs(distances - char_distance)), distances.shape)
    char_F = F_magnitude[char_idx]
    char_r = distances[char_idx]
    
    g_newton_char = solver.G * mass / (char_r + solver.r_min)**2
    g_set_char = g_newton_char * (1 + target_k_eff)
    
    print(f"  F at r={char_r:.1e}m: {char_F:.6e}")
    print(f"  Expected: {g_set_char:.6e}")
    print(f"  k_eff measured: {(char_F - g_newton_char)/g_newton_char:.6f}")
    print(f"  k_eff target: {target_k_eff:.6f}")

def test_proper_k_eff_calculation():
    """Test k_eff calculation at proper measurement distance"""
    print(f"\n🎯 PROPER k_eff CALCULATION")
    print("=" * 60)
    
    test_cases = [
        {'domain': 2e11, 'mass': 2e30, 'target': 2e-4, 'name': 'SOLAR'},
        {'domain': 3e20, 'mass': 1e11*1.989e30, 'target': 0.3, 'name': 'GALACTIC'}
    ]
    
    for case in test_cases:
        print(f"\n🔭 {case['name']} SCALE:")
        solver = SubstrateXSolver(
            grid_size=32,
            domain_size=case['domain'],
            alpha=1.0, beta=1.0, gamma=1.0, chi=1.0, tau=1e3
        )
        
        # Add mass with desired k_eff
        # We need to modify the solver to accept k_eff parameter
        # For now, let's see what we get with default
        solver.add_point_mass(case['mass'], (0,0))
        
        # Measure at characteristic distance
        char_distance = case['domain'] / 10
        distances = np.sqrt(solver.X**2 + solver.Y**2)
        char_idx = np.unravel_index(np.argmin(np.abs(distances - char_distance)), distances.shape)
        
        F_magnitude = np.sqrt(solver.F[:,:,0]**2 + solver.F[:,:,1]**2)
        F_at_char = F_magnitude[char_idx]
        r_measured = distances[char_idx]
        
        g_newton = solver.G * case['mass'] / (r_measured + solver.r_min)**2
        
        k_eff_measured = (F_at_char - g_newton) / g_newton
        
        print(f"  Measurement at r={r_measured:.1e}m:")
        print(f"    F = {F_at_char:.6e} m/s²")
        print(f"    g_newton = {g_newton:.6e} m/s²") 
        print(f"    k_eff = {k_eff_measured:.6f}")
        print(f"    Target = {case['target']:.6f}")

if __name__ == "__main__":
    debug_measurement()
    test_proper_k_eff_calculation()
