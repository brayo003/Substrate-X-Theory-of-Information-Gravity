#!/usr/bin/env python3
"""
FINAL VERSION: Mercury Perihelion Precession Test for Substrate X Theory
This version includes proper error handling and diagnostics.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import argrelextrema
import sys

def main():
    # Physical constants
    G = 6.67430e-11
    c = 299792458.0
    M_sun = 1.98847e30

    # Mercury orbital parameters
    a = 5.7909232e10        # semi-major axis (m)
    e = 0.20563069          # eccentricity
    period_seconds = 87.969 * 24 * 3600.0  # Mercury orbital period

    def substrate_x_equations(t, state, relativistic=True, k=3.0):
        """
        Equations of motion for Substrate X theory
        state = [r, r_dot, theta, theta_dot]
        """
        r, r_dot, theta, theta_dot = state
        
        if r <= 0:
            return [0.0, 0.0, 0.0, 0.0]

        # Radial pressure term (Newtonian)
        a_radial = -G * M_sun / (r**2)
        
        # Add relativistic correction if requested
        if relativistic:
            a_radial *= (1 + (k * G * M_sun) / (c**2 * r))

        # Flow velocity magnitude
        v_flow = np.sqrt(2 * G * M_sun / r)
        
        # Tangential guidance term
        v_r = -v_flow  # inward radial flow
        guidance_term = (r * theta_dot * v_r) / r  # = theta_dot * v_r

        # Equations of motion
        r_ddot = r * theta_dot**2 + a_radial
        theta_ddot = (guidance_term - 2.0 * r_dot * theta_dot) / r

        return [r_dot, r_ddot, theta_dot, theta_ddot]

    def detect_perihelion_precession(relativistic=True, k=3.0, years=10):
        """Detect perihelion precession from simulation data"""
        
        t_end = years * 365.25 * 24 * 3600.0
        n_steps = 100000  # High resolution
        
        # Initial conditions at perihelion
        r_peri = a * (1 - e)
        v_peri = np.sqrt(G * M_sun * (1.0 + e) / (a * (1 - e)))
        state0 = [r_peri, 0.0, 0.0, v_peri / r_peri]
        
        print(f"Running simulation for {years} years...")
        
        try:
            # Solve the differential equations
            sol = solve_ivp(
                lambda t, y: substrate_x_equations(t, y, relativistic, k),
                [0, t_end], 
                state0,
                t_eval=np.linspace(0, t_end, n_steps),
                rtol=1e-10,
                atol=1e-12,
                method='RK45'
            )
            
            if not sol.success:
                print(f"Integration failed: {sol.message}")
                return 0.0
                
            r_vals = sol.y[0]
            theta_vals = sol.y[2]
            
            # Detect perihelia (local minima in radius)
            idx_min = argrelextrema(r_vals, np.less, order=100)[0]
            
            print(f"Found {len(idx_min)} perihelia")
            
            if len(idx_min) < 3:
                print("Not enough perihelia detected for accurate measurement")
                return 0.0
            
            # Calculate angular advances between perihelia
            peri_angles = theta_vals[idx_min]
            angle_differences = np.diff(peri_angles)
            
            # Unwrap the angles to handle 2π crossings
            angle_differences = (angle_differences + np.pi) % (2 * np.pi) - np.pi + 2 * np.pi
            
            avg_angle_per_orbit = np.mean(angle_differences)
            precession_per_orbit = avg_angle_per_orbit - 2 * np.pi
            
            # Convert to arcseconds per century
            orbits_per_century = (100.0 * 365.25 * 24 * 3600.0) / period_seconds
            precession_arcsec = precession_per_orbit * orbits_per_century * (180.0 / np.pi) * 3600.0
            
            return precession_arcsec
            
        except Exception as e:
            print(f"Error during simulation: {e}")
            return 0.0

    # Run the tests
    print("=== MERCURY PERIHELION PRECESSION TEST ===")
    print("Testing Substrate X Theory vs General Relativity")
    print(f"Target value: 43.0 arcseconds/century")
    print()
    
    # Test Newtonian case first
    print("1. Testing Newtonian case (should be ~0):")
    precession_newton = detect_perihelion_precession(relativistic=False, years=50)
    print(f"Newtonian precession: {precession_newton:.2f}''/century")
    print()
    
    # Test relativistic case
    print("2. Testing Relativistic case (k=3.0):")
    precession_rel = detect_perihelion_precession(relativistic=True, k=3.0, years=50)
    print(f"Relativistic precession: {precession_rel:.2f}''/century")
    print()
    
    # Test other k values if needed
    if abs(precession_rel - 43.0) > 5.0:
        print("3. Testing other k values:")
        for k in [2.0, 2.5, 3.0, 3.5, 4.0]:
            precession = detect_perihelion_precession(relativistic=True, k=k, years=20)
            print(f"k = {k}: {precession:.2f}''/century")
    
    print("\n=== RESULTS SUMMARY ===")
    print(f"Substrate X prediction: {precession_rel:.2f}''/century")
    print(f"GR observation: 43.0''/century")
    
    if abs(precession_rel - 43.0) < 2.0:
        print("🎉 SUCCESS: Substrate X theory reproduces GR prediction!")
    else:
        print("❌ Further refinement needed")

if __name__ == "__main__":
    main()