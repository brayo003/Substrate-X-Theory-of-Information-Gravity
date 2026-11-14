import numpy as np

def simulate_baryon_binding(r):
    """
    V12 Logic: Regime-Locked Configuration
    Uses empirical string tension (sigma) and 
    Coulomb-like term (alpha) for QCD potential.
    """
    sigma = 0.9  # GeV/fm (Empirical String Tension)
    alpha = 0.3  # Running coupling approximation
    
    if r <= 0: return 0, "SINGULARITY"
    
    # Potential Energy V(r) - The 'Potential Load' on the substrate
    potential_load = (sigma * r) - (alpha / r)
    
    # Normalized Load Index (NLI) 
    # Scaled to the Proton Charge Radius (~0.84 fm)
    nli = potential_load / 0.756 # Normalized to 1.0 at critical stability
    
    print(f"⚛️ V12 BARYON NODAL ANALYSIS")
    print("-" * 40)
    print(f"Separation (r):    {r:.4f} fm")
    print(f"Normalized Load:   {nli:.4f}")
    
    if nli > 1.3: # Snap point analogy
        status = "FLUX TUBE SNAP"
        verdict = "Substrate Breach: Pair Production Required"
    elif nli < 0.2:
        status = "ASYMPTOTIC FREEDOM"
        verdict = "Low-Interaction Regime"
    else:
        status = "REGIME-LOCKED"
        verdict = "Stable Landscape Configuration"
        
    print(f"STATUS:  {status}")
    print(f"VERDICT: {verdict}")
    print("-" * 40)

if __name__ == "__main__":
    simulate_baryon_binding(0.84) # Proton Radius
    print("\n")
    simulate_baryon_binding(1.6)  # Forced Separation
