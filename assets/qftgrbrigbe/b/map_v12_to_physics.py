# Save as: map_v12_to_physics.py
import numpy as np

def get_physical_x(mass, radius):
    """
    CORRECTION: x is no longer an abstract tension.
    It is the Schwarzschild curvature at distance 'radius'.
    Units: m^-2
    """
    G = 6.67430e-11
    C = 299792458.0
    # R = (2 * G * M) / (c^2 * r^3)
    return (2 * G * mass) / (C**2 * radius**3)

# Result: For Earth, x ≈ 1.1e-23. 
# Your old code assumed x ≈ 1.0. This is the 10^23 error found!
