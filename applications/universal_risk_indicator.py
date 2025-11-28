"""
Universal Risk Indicator (URI) Module
Translates the Information Gravity (IG) scalar into actionable signals.

IG > 0.90 (High Coherence) => EXECUTE / EXPAND
IG < 0.80 (Low Coherence)  => STAND ASIDE / CONTRACT
"""
import numpy as np
import sys
from typing import Dict, Tuple

# Ensure the 'theory' module is accessible
sys.path.append('..')
from theory.information_gravity_core import calculate_information_gravity

# --- URI Constants ---
# Defined thresholds based on validated IG score of 0.95
EXPAND_THRESHOLD = 0.90 
CONTRACT_THRESHOLD = 0.80

def get_current_system_data() -> Dict[str, float]:
    """
    Simulates retrieving the latest stable metrics from the validated UDE domains.
    
    In a live environment, this would pull real-time data from financial, 
    biological, and physical sensors/APIs.
    
    Returns the ideal, validated metrics for initial testing.
    """
    # Using the ideal metrics confirmed in the IG core test (IG = 0.950096)
    return {
        'bio_physics_vr': 12000.0,
        'planetary_momentum_error_ppm': 0.00,
        'planetary_energy_error_ppm': 0.00
    }

def generate_risk_signal(stability_data: Dict[str, float]) -> Tuple[str, float]:
    """
    Calculates the IG score and generates a risk signal based on thresholds.
    
    Returns:
        Tuple[str, float]: (SIGNAL, IG_SCORE)
    """
    ig_score = calculate_information_gravity(stability_data)
    
    if ig_score >= EXPAND_THRESHOLD:
        signal = "EXECUTE/EXPAND (High Confidence)"
    elif ig_score <= CONTRACT_THRESHOLD:
        signal = "CONTRACT/STAND ASIDE (Low Confidence/High Risk)"
    else:
        signal = "CAUTION/HOLD (Ambiguous Coherence)"
        
    return signal, ig_score

def run_uri_module():
    """Main execution function to demonstrate the risk indicator."""
    print("📈 UNIVERSAL RISK INDICATOR (URI) MODULE")
    print("==========================================")
    
    # Get high-coherence data (validated state)
    data = get_current_system_data()
    signal, ig_score = generate_risk_signal(data)
    
    print(f"1. Input System Metrics: V_R={data['bio_physics_vr']}, E_Error={data['planetary_energy_error_ppm']} ppm")
    print(f"2. Calculated Information Gravity (IG): {ig_score:.6f}")
    print(f"3. URI DECISION SIGNAL: **{signal}**")
    
    # Simulate a chaotic state for contrast
    chaotic_data = {
        'bio_physics_vr': 100.0,
        'planetary_momentum_error_ppm': 500.0,
        'planetary_energy_error_ppm': 500.0
    }
    chaotic_signal, chaotic_ig = generate_risk_signal(chaotic_data)
    
    print("\n--- Chaotic State Simulation ---")
    print(f"4. Simulated Chaotic IG: {chaotic_ig:.6f}")
    print(f"5. URI DECISION SIGNAL: **{chaotic_signal}**")


if __name__ == '__main__':
    run_uri_module()
