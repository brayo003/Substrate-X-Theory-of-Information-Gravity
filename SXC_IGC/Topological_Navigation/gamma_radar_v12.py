import numpy as np
from scipy.special import gamma

def get_topological_tension(substrate_health):
    """
    SXC-V12-G Navigation Logic (Agnostic)
    Maps health to the 1909 Gamma Landscape.
    Poles at 0, -1, -2... represent total system collapse.
    """
    try:
        # Absolute value per 1909 Jahnke-Emde plot
        g_val = abs(gamma(substrate_health))
        return g_val
    except Exception:
        return np.inf

def check_pole_proximity(health_score, redline=5.0):
    """
    Agnostic Monitor: Trigger reset if Gamma Tension exceeds redline.
    """
    tension = get_topological_tension(health_score)
    if tension > redline or np.isinf(tension):
        return True, tension  # Trigger Reset (Singularity detected)
    return False, tension     # System Nominal
