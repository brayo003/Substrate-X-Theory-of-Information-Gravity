# Save as: scaling_correction.py
import numpy as np

def get_dynamic_r(radius):
    """
    CORRECTION: r cannot be a constant (0.153).
    It must decay with distance to preserve the Inverse Square Law.
    """
    # To get R ∝ 1/L^2, the 'r' parameter in V12 
    # must scale inversely with the radius.
    reference_L = 1.616e-35 # Planck Length
    return (reference_L / radius)

# This forces the V12 engine to follow Newton/Einstein orbits.
