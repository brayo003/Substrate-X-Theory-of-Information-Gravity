"""
Information Gravity (IG) Core Module
"""
import numpy as np
from typing import Dict

MAX_VR_BIO_PHYSICS = 1.0
MAX_ABS_MOMENTUM_ERROR_PPM = 5000.0

def normalize_bio_physics_vr(variance_ratio: float) -> float:
    return np.clip(variance_ratio, 0.0, 1.0)

def normalize_planetary_error(error_ppm: float) -> float:
    error_clipped = np.clip(error_ppm, 0.0, MAX_ABS_MOMENTUM_ERROR_PPM)
    return 1.0 - (error_clipped / MAX_ABS_MOMENTUM_ERROR_PPM)

def calculate_information_gravity(stability_data: Dict[str, float]) -> float:
    s_bp = normalize_bio_physics_vr(stability_data.get('bio_physics_vr', 0.0))
    s_pd_mom = normalize_planetary_error(stability_data.get('planetary_momentum_error_ppm', 2500))
    s_pd_en = normalize_planetary_error(stability_data.get('planetary_energy_error_ppm', 2500))
    
    weight_bp, weight_pd = 0.3, 0.7
    composite_pd_stability = (s_pd_mom + s_pd_en) / 2.0
    ig_score = (weight_bp * s_bp) + (weight_pd * composite_pd_stability)
    
    return np.clip(ig_score, 0.0, 1.0)
