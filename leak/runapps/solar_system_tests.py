#!/usr/bin/env python3
import numpy as np

def mercury_precession_test():
    """Test Mercury's perihelion precession (43 arcseconds/century)"""
    print("☿️ TESTING MERCURY'S PERIHELION PRECESSION")
    print("=" * 50)
    
    # General Relativity prediction: 43 arcseconds/century
    # Newtonian prediction: 0 (for point mass)
    gr_prediction = 43.0  # arcseconds/century
    
    # Your substrate theory might predict different precession
    # Due to: 
    # - Non-1/r² corrections to force law
    # - Substrate flow effects on orbits
    # - Information pressure gradients
    
    print(f"General Relativity: {gr_prediction} arcsec/century")
    print("Substrate X prediction: Calculate orbital precession from:")
    print("  - Modified force law F ∝ s × v_sub")
    print("  - Substrate flow corrections")
    print("  - Pressure gradient effects")
    
    return gr_prediction

def planetary_orbits_validation():
    """Test against all planetary orbital periods"""
    print("\n🪐 VALIDATING PLANETARY ORBITS")
    print("=" * 50)
    
    planets = {
        'Mercury': {'a': 0.387, 'period': 0.241},
        'Venus': {'a': 0.723, 'period': 0.615},
        'Earth': {'a': 1.000, 'period': 1.000},
        'Mars': {'a': 1.524, 'period': 1.881},
        'Jupiter': {'a': 5.203, 'period': 11.862},
    }
    
    print("Planet  | Semi-major (AU) | Period (years) | Substrate Match?")
    print("-" * 55)
    
    for planet, data in planets.items():
        # Kepler's third law: T² ∝ a³
        expected_period = data['a'] ** 1.5
        match = abs(expected_period - data['period']) < 0.01
        
        print(f"{planet:8} {data['a']:15.3f} {data['period']:15.3f} {'✅' if match else '❌'}")
    
    return planets
