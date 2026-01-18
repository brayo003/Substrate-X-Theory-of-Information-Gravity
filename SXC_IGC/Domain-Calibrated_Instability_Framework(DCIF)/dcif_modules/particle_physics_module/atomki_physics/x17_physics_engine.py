import numpy as np

# Physical Constants (Nuclear Scale)
M_X17 = 17.01e6  # 17.01 MeV (measured)
M_E = 0.511e6    # Electron mass in eV
ALPHA_EM = 1/137.036

def calculate_branching_ratio(coupling_gb, m_x=M_X17):
    """
    Calculates the branching ratio of the X17 emission 
    relative to Gamma-ray emission in 8Be transitions.
    Formula: Gamma_X / Gamma_Gamma
    """
    # Simplified vector boson coupling logic
    br = (coupling_gb**2 / ALPHA_EM) * (1 - (m_x/18.15e6)**2)**1.5
    return br

# Optimized coupling based on Krasznahorkay et al. (2016)
# g_b ~ 10^-3 to 10^-4 for 8Be anomaly
g_b_target = 1.2e-3 
ratio = calculate_branching_ratio(g_b_target)

print(f"X17 ENGINE INITIALIZED")
print(f"----------------------")
print(f"Target Mass: {M_X17/1e6:.2f} MeV")
print(f"Baryonic Coupling (g_b): {g_b_target:.2e}")
print(f"Predicted Branching Ratio: {ratio:.2e}")
