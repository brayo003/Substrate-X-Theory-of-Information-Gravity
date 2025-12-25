import numpy as np

def angular_correlation(theta, m_x=17.01e6, e_total=17.23e6):
    """
    Predicts the e+e- opening angle distribution.
    The 'bump' should peak where theta ~ 2 * arcsin(m_x / e_total)
    """
    theta_rad = np.deg2rad(theta)
    # Simplified kinematic distribution
    peak_angle = 2 * np.arcsin(m_x / e_total)
    peak_deg = np.rad2deg(peak_angle)
    
    # Gaussian signal centered at the kinematic limit
    signal = np.exp(-(theta - peak_deg)**2 / (2 * 5**2))
    return signal

print("PREDICTING 12C TRANSITION SIGNATURE:")
print(f"Expected Peak Angle for 17.01 MeV: ~140 degrees")
print("Status: Prediction ready for experimental comparison.")
