#!/usr/bin/env python3
"""
CORRECTED APPROACH: Proper relativistic implementation for Substrate X
We need to modify the fundamental acceleration terms, not just flow speeds.
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
period_seconds = 87.969 * 24 * 3600.0

def calculate_precession(relativistic_correction=True, correction_strength=3.0):
    """
    Proper implementation with relativistic correction to the central force
    """
    
    def equations(t, state):
        r, r_dot, theta, theta_dot = state
        if r <= 0: 
            return [0.0, 0.0, 0.0, 0.0]
        
        # NEWTONIAN radial acceleration
        a_radial_newton = -G * M_sun / (r**2)
        
        # RELATIVISTIC CORRECTION (the key fix)
        if relativistic_correction:
            # Add the 1/r^3 term that causes precession in GR
            relativistic_term = correction_strength * (G * M_sun) / (c**2 * r**3)
            a_radial = a_radial_newton * (1 + relativistic_term * r**2)  # Equivalent to extra 1/r^3 term
        else:
            a_radial = a_radial_newton
        
        # Flow velocity (Newtonian)
        v_flow = np.sqrt(2 * G * M_sun / r)
        
        # Guidance term (convective derivative)
        # This is the key insight: v_r = -v_flow (inward)
        v_r = -v_flow
        u_theta = r * theta_dot
        guidance_term = (u_theta * v_r) / r  # = theta_dot * v_r
        
        # Equations of motion
        r_ddot = r * theta_dot**2 + a_radial
        theta_ddot = (guidance_term - 2.0 * r_dot * theta_dot) / r
        
        return [r_dot, r_ddot, theta_dot, theta_ddot]
    
    # Simulation parameters
    years = 100
    t_end = years * 365.25 * 24 * 3600.0
    n_steps = 200000  # High resolution for small effects
    t_eval = np.linspace(0.0, t_end, n_steps)
    
    # Initial conditions at perihelion
    r_peri = a * (1 - e)
    v_peri = np.sqrt(G * M_sun * (1.0 + e) / (a * (1 - e)))
    state0 = [r_peri, 0.0, 0.0, v_peri / r_peri]
    
    print(f"Running simulation with relativistic_correction={relativistic_correction}...")
    sol = solve_ivp(equations, (0.0, t_end), state0, t_eval=t_eval, rtol=1e-11, atol=1e-13, method='RK45')
    
    # Detect perihelia
    r_vals = sol.y[0]
    theta_vals = sol.y[2]
    idx_min = argrelextrema(r_vals, np.less, order=50)[0]  # Increased order for better detection
    
    if len(idx_min) < 2:
        print("Warning: Not enough perihelia detected")
        return 0.0
    
    peri_thetas = theta_vals[idx_min]
    diffs = np.diff(peri_thetas)
    
    # Unwrap the differences properly
    diffs_unwrapped = []
    for diff in diffs:
        while diff > 2*np.pi + 0.1:  # Allow some tolerance
            diff -= 2*np.pi
        while diff < 2*np.pi - 0.1:
            diff += 2*np.pi
        diffs_unwrapped.append(diff)
    
    avg_delta = np.mean(diffs_unwrapped)
    precession_per_orbit_rad = avg_delta - 2.0 * np.pi
    
    # Convert to arcseconds per century
    orbits_per_century = (100.0 * 365.25 * 24*3600.0) / period_seconds
    precession_per_century_arcsec = (precession_per_orbit_rad * orbits_per_century) * (180.0/np.pi) * 3600.0
    
    print(f"Detected {len(idx_min)} perihelia")
    print(f"Precession: {precession_per_century_arcsec:.2f}''/century")
    
    return precession_per_century_arcsec

# TEST DIFFERENT CORRECTION STRENGTHS
print("=== TESTING RELATIVISTIC CORRECTION STRENGTHS ===")

# Newtonian baseline
print("\n1. Newtonian baseline (no correction):")
precession_newton = calculate_precession(relativistic_correction=False)
print(f"Newtonian precession: {precession_newton:.2f}''/century (should be ~0)")

# Test different correction strengths
correction_strengths = [1.0, 2.0, 3.0, 4.0]
for strength in correction_strengths:
    print(f"\nTesting correction strength = {strength}:")
    precession = calculate_precession(relativistic_correction=True, correction_strength=strength)
    print(f"Strength {strength}: {precession:.2f}''/century")

print(f"\nTarget GR value: 43.0''/century")
