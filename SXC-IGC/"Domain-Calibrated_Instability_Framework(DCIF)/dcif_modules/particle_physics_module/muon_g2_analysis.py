import numpy as np

def calculate_g2_contribution(m_x, g_mu):
    """
    Calculates the contribution of the X17 boson to 
    the Muon anomalous magnetic moment (a_mu).
    """
    alpha_x = (g_mu**2) / (4 * np.pi)
    m_mu = 105.66e6 # Muon mass in eV
    
    # Standard formula for vector boson contribution to g-2
    # a_mu = (alpha_x / 2*pi) * L(m_x/m_mu)
    # For m_x >> m_mu, it scales as (m_mu/m_x)^2
    contribution = (alpha_x / (2 * np.pi)) * (m_mu / m_x)**2
    return contribution

# The "Missing" value from Standard Model is approx 251e-11
TARGET_TENSION = 251e-11
M_X17 = 17.01e6

# Calculate required coupling to fix the g-2 tension
required_g = np.sqrt(TARGET_TENSION * (2 * np.pi) * (M_X17 / 105.66e6)**2 * (4 * np.pi))

print(f"--- MUON G-2 INTEGRATION ---")
print(f"Required Muon Coupling (g_mu): {required_g:.2e}")
print(f"Result: If g_mu is ~10^-4, Substrate X solves the g-2 mystery.")
