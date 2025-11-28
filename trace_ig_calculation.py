"""
TRACE: Follow the exact IG calculation in both cases
"""
import sys
import os
sys.path.insert(0, '/home/lenovo/Git/Substrate X Theory of Information Gravity')

from theory.information_gravity_core import calculate_information_gravity, normalize_bio_physics_vr, normalize_planetary_error

def trace_ig_calculation(metrics, label):
    print(f"\n=== {label} ===")
    print(f"Input metrics: {metrics}")
    
    # Trace each normalization step
    s_bp = normalize_bio_physics_vr(metrics.get('bio_physics_vr', 0.0))
    s_pd_mom = normalize_planetary_error(metrics.get('planetary_momentum_error_ppm', 1000))
    s_pd_en = normalize_planetary_error(metrics.get('planetary_energy_error_ppm', 1000))
    
    print(f"Normalized bio_physics: {s_bp:.4f}")
    print(f"Normalized momentum error: {s_pd_mom:.4f}") 
    print(f"Normalized energy error: {s_pd_en:.4f}")
    
    # Calculate final IG
    weight_bp, weight_pd = 0.3, 0.7
    composite_pd_stability = (s_pd_mom + s_pd_en) / 2.0
    ig_score = (weight_bp * s_bp) + (weight_pd * composite_pd_stability)
    
    print(f"Weighted sum: ({weight_bp} * {s_bp:.4f}) + ({weight_pd} * {composite_pd_stability:.4f})")
    print(f"Final IG: {ig_score:.4f}")
    
    return ig_score

# Test case 1: Our standalone test
test_metrics = {
    'bio_physics_vr': 0.9,
    'planetary_momentum_error_ppm': 100,
    'planetary_energy_error_ppm': 100
}
trace_ig_calculation(test_metrics, "STANDALONE TEST")

# Test case 2: What the engine might be using
engine_like_metrics = {
    'bio_physics_vr': 0.95,  # Maybe engine uses higher values
    'planetary_momentum_error_ppm': 50,   # Maybe engine uses lower errors
    'planetary_energy_error_ppm': 50
}
trace_ig_calculation(engine_like_metrics, "ENGINE-LIKE METRICS")
