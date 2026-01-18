import numpy as np

# UNIVERSAL CONSTANTS
C = 299792458.0
PLANCK_LENGTH = 1.616e-35
HUBBLE_RADIUS_TODAY = 1.37e26

def simulate_full_evolution():
    print(f"{'Scale (m)':<12} | {'Bridge Acceleration (m/s²)':<25} | {'Phase'}")
    print("-" * 65)
    
    # Generate 10 key logarithmic milestones from Planck to Today
    milestones = np.logspace(np.log10(PLANCK_LENGTH), np.log10(HUBBLE_RADIUS_TODAY), 10)
    
    for rh in milestones:
        # THE BRIDGE EQUATION (Spherical Leakage)
        a0 = (C**2) / (4 * np.pi * rh)
        
        if rh < 1e-15:
            phase = "FIREWALL (INFLATION)"
        elif rh < 1e18:
            phase = "NOMINAL (EXPANSION)"
        else:
            phase = "GALACTIC BRIDGE (DARK MATTER SUBSTITUTE)"
            
        print(f"{rh:<12.2e} | {a0:<25.2e} | {phase}")

if __name__ == "__main__":
    simulate_full_evolution()
