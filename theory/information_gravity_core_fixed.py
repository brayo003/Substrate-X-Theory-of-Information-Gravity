"""
FIXED Information Gravity Core with proper constants
"""
import numpy as np
from typing import Dict

# FIXED CONSTANTS - these were causing the bug!
MAX_VR_BIO_PHYSICS = 1.0  # Was 10,000 - WAY too high for 0-1 normalized values!
MAX_ABS_MOMENTUM_ERROR_PPM = 5000.0  # This one is reasonable

def normalize_bio_physics_vr(variance_ratio: float) -> float:
    """
    FIXED: Normalize bio-physics variance ratio.
    Since input is already 0-1 normalized, we use appropriate scaling.
    """
    # Input is already 0-1 normalized, so we scale appropriately
    # Use sigmoid-like function to map 0-1 to stability score
    scaled = variance_ratio / MAX_VR_BIO_PHYSICS
    return float(np.tanh(scaled))

def normalize_planetary_error(error_ppm: float) -> float:
    """Normalize planetary error (0 = perfect, high = bad)"""
    return 1.0 / (1.0 + (error_ppm / MAX_ABS_MOMENTUM_ERROR_PPM))

def calculate_information_gravity(stability_data: Dict[str, float]) -> float:
    """Calculate IG with FIXED normalization"""
    s_bp = normalize_bio_physics_vr(stability_data.get('bio_physics_vr', 0.0))
    s_pd_mom = normalize_planetary_error(stability_data.get('planetary_momentum_error_ppm', 1000))
    s_pd_en = normalize_planetary_error(stability_data.get('planetary_energy_error_ppm', 1000))
    
    weight_bp, weight_pd = 0.3, 0.7
    composite_pd_stability = (s_pd_mom + s_pd_en) / 2.0
    ig_score = (weight_bp * s_bp) + (weight_pd * composite_pd_stability)
    
    return np.clip(ig_score, 0.0, 1.0)

# Test the fix
if __name__ == "__main__":
    test_metrics = {
        'bio_physics_vr': 0.9,
        'planetary_momentum_error_ppm': 100,
        'planetary_energy_error_ppm': 100
    }
    
    ig = calculate_information_gravity(test_metrics)
    print(f"FIXED IG calculation: {ig:.4f}")
    
    # Test range
    print("\nTesting range:")
    for bp in [0.1, 0.5, 0.9]:
        test_metrics['bio_physics_vr'] = bp
        ig = calculate_information_gravity(test_metrics)
        print(f"bio_physics_vr={bp} -> IG={ig:.4f}")
