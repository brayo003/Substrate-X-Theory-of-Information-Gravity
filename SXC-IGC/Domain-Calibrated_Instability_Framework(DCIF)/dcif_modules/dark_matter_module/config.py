import numpy as np

# Global Physical Constants
HBAR = 1.054571817e-34
G_CONST = 6.67430e-11
C_LIGHT = 299792458
RHO_PLANCK = (C_LIGHT**5) / (HBAR * G_CONST**2)

# V12 Bridge Parameters (The Validated Set)
# r: Vacuum Tension, a: Coupling, b: Holographic Cap
V12_PARAMS = {
    'r': 0.153,
    'a': 1.0,
    'b': 1.0,
    'dt': 0.05
}

def get_curvature(x):
    """Maps internal tension x to physical Ricci scalar"""
    kappa = (8 * np.pi * G_CONST) / (C_LIGHT**4)
    energy_density = np.tanh(x) * RHO_PLANCK
    return kappa * energy_density * C_LIGHT**2
