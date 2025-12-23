#!/usr/bin/env python3
"""
COMPARISON TEST: Energy Correction vs Time-Dilation approaches for Substrate X
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import argrelextrema

# Physical constants
G = 6.67430e-11
c = 299792458.0
M_sun = 1.98847e30

# Mercury orbital parameters
a = 5.7909232e10
e = 0.20563069
period_seconds = 87.969 * 24 * 3600.0

def simulate_precession(approach="energy", k=3.0):
    """Run simulation with specified relativistic approach"""
    
    def v_flow_energy(r):
        return np.sqrt((2 * G * M_sun / r) + (k * (2 * G**2 * M_sun**2) / (r**2 * c**2)))
    
    def v_flow_newt(r):
        return np.sqrt(2.0 * G * M_sun / r)
    
    def equations(t, state):
        r, r_dot, theta, theta_dot = state
        if r <= 0: 
            return [0.0, 0.0, 0.0, 0.0]
        
        # Radial pressure (same for both approaches)
        radial_acc = -G * M_sun / (r**2)
        
        # Tangential guidance (DIFFERENT BETWEEN APPROACHES)
        if approach == "energy":
            v_r = -v_flow_energy(r)  # Uses energy-corrected flow
            guidance = (r * theta_dot * v_r) / r
        else:  # time-dilation approach
            v_r = -v_flow_newt(r)  # Uses Newtonian flow
            vf = v_flow_newt(r)
            Lambda_val = np.sqrt(max(1.0 - (vf**2) / (c**2), 1e-12))  # Avoid negative
            guidance = Lambda_val * (r * theta_dot * v_r) / r
        
        # Equations of motion
        r_ddot = r * theta_dot**2 + radial_acc
        theta_ddot = (guidance - 2.0 * r_dot * theta_dot) / r
        
        return [r_dot, r_ddot, theta_dot, theta_ddot]
    
    # Simulation parameters
    years = 100
    t_end = years * 365.25 * 24 * 3600.0
    n_steps = 100000
    t_eval = np.linspace(0.0, t_end, n_steps)
    
    # Initial conditions at perihelion
    r_peri = a * (1 - e)
    v_peri = np.sqrt(G * M_sun * (1.0 + e) / (a * (1 - e)))
    state0 = [r_peri, 0.0, 0.0, v_peri / r_peri]
    
    # Run simulation
    sol = solve_ivp(equations, (0.0, t_end), state0, t_eval=t_eval, rtol=1e-10, atol=1e-12, method='RK45')
    
    # Detect perihelia and compute precession
    r_vals = sol.y[0]
    theta_vals = sol.y[2]
    idx_min = argrelextrema(r_vals, np.less, order=20)[0]
    
    if len(idx_min) < 2:
        return 0.0
    
    peri_thetas = theta_vals[idx_min]
    diffs = np.diff(peri_thetas)
    diffs = (diffs + np.pi) % (2*np.pi) - np.pi + 2*np.pi
    avg_delta = np.mean(diffs)
    precession_per_orbit_rad = avg_delta - 2.0 * np.pi
    
    # Convert to arcseconds per century
    orbits_per_century = (100.0 * 365.25 * 24*3600.0) / period_seconds
    precession_per_century_arcsec = (precession_per_orbit_rad * orbits_per_century) * (180.0/np.pi) * 3600.0
    
    return precession_per_century_arcsec

# TEST BOTH APPROACHES
print("=== COMPARING RELATIVISTIC APPROACHES ===")
print("Testing Energy Correction approach...")
precession_energy = simulate_precession("energy", k=3.0)

print("Testing Time-Dilation approach...")  
precession_timedil = simulate_precession("time-dilation")

print("\n=== RESULTS ===")
print(f"Energy correction approach: {precession_energy:.1f}''/century")
print(f"Time-dilation approach: {precession_timedil:.1f}''/century") 
print(f"Target (GR): 43.0''/century")

# Determine outcome
if abs(precession_energy - 43.0) < 5 and abs(precession_timedil - 43.0) < 5:
    print("\n🎉 BREAKTHROUGH: Both approaches work! Multiple valid relativistic extensions.")
elif abs(precession_energy - 43.0) < 5:
    print("\n✅ Energy correction works. Time-dilation needs refinement.")
elif abs(precession_timedil - 43.0) < 5:
    print("\n✅ Time-dilation works. Energy correction needs refinement.")
else:
    print("\n❌ Both approaches need fundamental rethinking.")
