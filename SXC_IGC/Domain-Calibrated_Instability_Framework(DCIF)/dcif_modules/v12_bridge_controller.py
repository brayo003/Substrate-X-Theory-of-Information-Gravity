import pandas as pd

def v12_adaptive_controller(current_tension, gamma, domain_name):
    # THE UNIVERSAL CONSTANTS (Certainty)
    K_DISASTER = 0.780  
    SHATTER_POINT = 1.0  
    WARNING_THRESHOLD = 0.7

    # THE CLASS CLASSIFIER
    if gamma < 0.04: cls = "Ultra-Brittle"
    elif gamma < 0.10: cls = "Brittle"
    elif gamma < 0.30: cls = "Stiff"
    elif gamma < 0.70: cls = "Viscous"
    else: cls = "Elastic"

    # THE CERTAINTY CALCULATION
    time_to_death = (SHATTER_POINT - current_tension) * (K_DISASTER / gamma)
    
    print(f"--- V12 BRIDGE STATUS: {domain_name} ---")
    print(f"Class: {cls} | Gamma: {gamma:.4f}")
    print(f"Current Tension: {current_tension:.2f}")
    
    if current_tension >= WARNING_THRESHOLD:
        print(f"⚠️  WARNING: T=0.7 REACHED. EMERGENCY INTERVENTION REQUIRED.")
        print(f"⏳ TIME TO COMPLETE SYSTEM SHATTER: {time_to_death:.4f} units")
    else:
        print(f"✅ STATUS: STABLE. Next check in {time_to_death/2:.4f} units.")

# Executing Test Cases
v12_adaptive_controller(0.72, 0.9000, "Finance_Module")
print("-" * 10)
v12_adaptive_controller(0.72, 0.0403, "Seismic_Module")
