import numpy as np

def predict_peak(isotope_name, e_transition):
    m_x = 17.01
    # Kinematic limit for opening angle
    theta_min = 2 * np.rad2deg(np.arcsin(m_x / e_transition))
    
    # Branching Ratio prediction (scaled from 8Be)
    br_predicted = 5.0e-6 * (e_transition / 18.15)**3 
    
    print(f"Target: {isotope_name}")
    print(f"  Transition Energy: {e_transition} MeV")
    print(f"  Predicted Peak:    {theta_min:.1f} degrees")
    print(f"  Expected BR:       {br_predicted:.2e}")
    print("-" * 30)

print("--- FUTURE EXPERIMENTAL BLUEPRINT ---")
predict_peak("Oxygen-16", 18.35)
predict_peak("Neon-20", 17.15) # High interest: Transition close to threshold
