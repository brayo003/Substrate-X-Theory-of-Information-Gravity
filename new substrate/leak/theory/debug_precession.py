#!/usr/bin/env python3
"""
DEBUG: Why are we getting zero precession?
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import argrelextrema

# Physical constants
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30

# Mercury orbit
a = 5.7909232e10
e = 0.20563069

def debug_approaches():
    """Test each component to find the issue"""
    
    print("=== DEBUGGING RELATIVISTIC CORRECTIONS ===\n")
    
    # Test at Mercury's perihelion
    r_peri = a * (1 - e)
    print(f"Testing at Mercury perihelion: r = {r_peri:.3e} m")
    
    # Newtonian flow speed
    v_flow_newt = np.sqrt(2 * G * M_sun / r_peri)
    print(f"Newtonian flow speed: {v_flow_newt:.3e} m/s")
    print(f"v/c ratio: {v_flow_newt/c:.6f}")
    
    # Energy correction approach
    k = 3.0
    energy_correction = (k * (2 * G**2 * M_sun**2) / (r_peri**2 * c**2))
    v_flow_energy = np.sqrt((2 * G * M_sun / r_peri) + energy_correction)
    print(f"\nEnergy correction approach:")
    print(f"  Correction term: {energy_correction:.3e} m²/s²")
    print(f"  Corrected flow speed: {v_flow_energy:.3e} m/s")
    print(f"  Speed increase: {((v_flow_energy/v_flow_newt) - 1)*100:.4f}%")
    
    # Time-dilation approach  
    Lambda_val = np.sqrt(1.0 - (v_flow_newt**2) / (c**2))
    print(f"\nTime-dilation approach:")
    print(f"  Lambda factor: {Lambda_val:.8f}")
    print(f"  Guidance reduction: {(1-Lambda_val)*100:.6f}%")
    
    # Test if corrections are significant enough
    print(f"\n=== SIGNIFICANCE CHECK ===")
    print(f"Are these corrections large enough to cause observable precession?")
    print(f"Energy correction modifies flow by: {((v_flow_energy/v_flow_newt) - 1)*100:.4f}%")
    print(f"Time-dilation modifies guidance by: {(1-Lambda_val)*100:.6f}%")
    
    return v_flow_energy, Lambda_val

def test_newtonian_only():
    """Test pure Newtonian case to establish baseline"""
    print("\n=== TESTING PURE NEWTONIAN ===")
    
    def newtonian_equations(t, state):
        r, r_dot, theta, theta_dot = state
        if r <= 0: return [0.0, 0.0, 0.0, 0.0]
        
        radial_acc = -G * M_sun / (r**2)
        r_ddot = r * theta_dot**2 + radial_acc
        theta_ddot = -2.0 * r_dot * theta_dot / r  # No guidance term
        
        return [r_dot, r_ddot, theta_dot, theta_ddot]
    
    # Simulation
    years = 10
    t_end = years * 365.25 * 24 * 3600.0
    n_steps = 50000
    
    r_peri = a * (1 - e)
    v_peri = np.sqrt(G * M_sun * (1.0 + e) / (a * (1 - e)))
    state0 = [r_peri, 0.0, 0.0, v_peri / r_peri]
    
    sol = solve_ivp(newtonian_equations, (0.0, t_end), state0, t_eval=np.linspace(0, t_end, n_steps), 
                    rtol=1e-10, atol=1e-12, method='RK45')
    
    r_vals = sol.y[0]
    theta_vals = sol.y[2]
    idx_min = argrelextrema(r_vals, np.less, order=20)[0]
    
    if len(idx_min) >= 2:
        peri_thetas = theta_vals[idx_min]
        diffs = np.diff(peri_thetas)
        avg_delta = np.mean(diffs)
        print(f"Newtonian orbits are closed? Avg delta_theta = {avg_delta:.8f} (should be ~6.283185307)")
        print(f"2π = {2*np.pi:.8f}")
        print(f"Difference: {avg_delta - 2*np.pi:.2e} radians")

if __name__ == "__main__":
    debug_approaches()
    test_newtonian_only()
