#!/usr/bin/env python3
"""
GRAVITATIONAL LENSING TEST - Does light bend correctly?
"""

import numpy as np

def test_gravitational_lensing():
    print("🔭 TESTING GRAVITATIONAL LENSING")
    print("=" * 60)
    
    # Solar parameters
    M_sun = 1.989e30  # [kg]
    R_sun = 6.96e8    # [m]
    G = 6.67430e-11
    c = 3.0e8
    
    # General Relativity prediction
    deflection_GR = 4 * G * M_sun / (c**2 * R_sun)  # radians
    deflection_GR_arcsec = deflection_GR * 206265
    
    print(f"GR prediction: {deflection_GR_arcsec:.2f} arcseconds")
    print(f"Eddington measurement (1919): 1.75 ± 0.05 arcseconds")
    
    # SUBSTRATE X PREDICTION
    # In your theory, light bending comes from:
    # - Substrate refractive index n(r) = 1/Λ(r)
    # - How photons couple to substrate flow v_sub(r)
    
    # PLACEHOLDER - Replace with your actual calculation
    substrate_deflection = deflection_GR  # Start with GR value
    
    print(f"\n📊 SUBSTRATE X PREDICTION:")
    print(f"Deflection: {substrate_deflection * 206265:.2f} arcseconds")
    
    if abs(substrate_deflection - deflection_GR) < 1e-6:
        print("✅ Matches GR prediction")
        return True
    else:
        print("🚨 PREDICTS DIFFERENT LENSING - This would be huge!")
        return "NOVEL_PREDICTION"

if __name__ == "__main__":
    test_gravitational_lensing()
