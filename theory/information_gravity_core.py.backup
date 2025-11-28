"""
Information Gravity (IG) Core Module
This module defines the IG metric, unifying stability data from Finance, Bio-Physics, and Planetary Dynamics.

The core principle is that high IG (high order/low entropy) corresponds to high predictive coherence
and low absolute energy/momentum error.
"""
import numpy as np
from typing import Dict

# --- Constants for Normalization ---
# Target IG value is between 0.0 (Chaotic) and 1.0 (Perfectly Ordered/Predictive)
MAX_VR_BIO_PHYSICS = 10000.0  # Max observed stable Variance Ratio for Turing patterns
MAX_ABS_MOMENTUM_ERROR_PPM = 100.0 # Maximum tolerable PPM error for conservative systems
MIN_ABS_ENERGY_EXPECTED = -0.5 # Minimum expected absolute energy for a bound system

def normalize_bio_physics_vr(variance_ratio: float) -> float:
    """
    Normalizes the Bio-Physics Variance Ratio (VR) to a Stability Score (0.0 to 1.0).
    A high VR (e.g., 10,000x) is mapped near 1.0.
    """
    # Use hyperbolic tangent (tanh) to smoothly map VR onto [0, 1] range,
    # with the MAX_VR acting as the scaling factor for the midpoint/saturation.
    return np.tanh(variance_ratio / MAX_VR_BIO_PHYSICS)

def normalize_planetary_error(error_ppm: float) -> float:
    """
    Normalizes the Planetary Dynamics Error (PPM) to a Stability Score (0.0 to 1.0).
    A low PPM error (e.g., 0.0) is mapped to 1.0.
    """
    # Invert the error: 1.0 / (1.0 + error_ppm) scales error near zero to 1.0, 
    # using MAX_ABS_MOMENTUM_ERROR_PPM for scaling/tolerance.
    return 1.0 / (1.0 + (error_ppm / MAX_ABS_MOMENTUM_ERROR_PPM))

def calculate_information_gravity(stability_data: Dict[str, float]) -> float:
    """
    Calculates the final Information Gravity (IG) scalar by weighting normalized metrics.
    
    Args:
        stability_data: Dictionary containing domain-specific metrics.
            Required keys: 'bio_physics_vr', 'planetary_momentum_error_ppm', 'planetary_energy_error_ppm'.
            
    Returns:
        float: The composite IG score (0.0 to 1.0).
    """
    # 1. Bio-Physics Stability (Pattern Coherence)
    s_bp = normalize_bio_physics_vr(stability_data.get('bio_physics_vr', 0.0))
    
    # 2. Planetary Dynamics Stability (Conservation)
    s_pd_mom = normalize_planetary_error(stability_data.get('planetary_momentum_error_ppm', MAX_ABS_MOMENTUM_ERROR_PPM))
    s_pd_en = normalize_planetary_error(stability_data.get('planetary_energy_error_ppm', MAX_ABS_MOMENTUM_ERROR_PPM))
    
    # Simple Geometric Mean (or Weighted Average) to combine the stable scores.
    # The Finance Domain is implicitly represented by requiring a high s_bp score 
    # (High IG = EXECUTE), but is not explicitly calculated here.
    
    # Weights can be adjusted based on domain importance or stability requirements.
    # Here, we weigh conservation (Energy/Momentum) higher than pattern coherence.
    weight_bp, weight_pd = 0.3, 0.7
    
    composite_pd_stability = (s_pd_mom + s_pd_en) / 2.0
    
    ig_score = (weight_bp * s_bp) + (weight_pd * composite_pd_stability)
    
    return np.clip(ig_score, 0.0, 1.0) # Ensure score is strictly between 0 and 1

def run_ig_test():
    """Demonstrates IG calculation using validated data."""
    
    # Case 1: Ideal Validation Results
    ideal_data = {
        'bio_physics_vr': 12000.0,  # High V_R
        'planetary_momentum_error_ppm': 0.00,
        'planetary_energy_error_ppm': 0.00
    }
    ig_ideal = calculate_information_gravity(ideal_data)
    print(f"📊 IG Calculation (Ideal Data): {ig_ideal:.6f}") # Should be near 1.0

    # Case 2: Near-Chaos (Low V_R, High Error)
    chaotic_data = {
        'bio_physics_vr': 100.0,
        'planetary_momentum_error_ppm': 500.0, # High error
        'planetary_energy_error_ppm': 500.0
    }
    ig_chaotic = calculate_information_gravity(chaotic_data)
    print(f"📊 IG Calculation (Chaotic Data): {ig_chaotic:.6f}") # Should be near 0.0

if __name__ == '__main__':
    run_ig_test()
