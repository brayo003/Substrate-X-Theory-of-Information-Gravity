import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from theory.information_gravity_core import calculate_information_gravity

def test_ig_perfect_stability():
    """PROVE: Perfect stability metrics → IG = 1.0"""
    perfect_metrics = {
        'bio_physics_vr': 1.0,           # Perfect pattern coherence
        'planetary_momentum_error_ppm': 0,  # No momentum error
        'planetary_energy_error_ppm': 0     # No energy error
    }
    ig = calculate_information_gravity(perfect_metrics)
    assert np.isclose(ig, 1.0, atol=0.01), f"Perfect stability should yield IG=1.0, got {ig}"

def test_ig_chaotic_state():
    """PROVE: Chaotic metrics → IG approaches 0.0"""
    chaotic_metrics = {
        'bio_physics_vr': 0.01,          # No pattern coherence  
        'planetary_momentum_error_ppm': 5000,  # Maximum error
        'planetary_energy_error_ppm': 5000     # Maximum error
    }
    ig = calculate_information_gravity(chaotic_metrics)
    assert ig < 0.1, f"Chaotic state should yield low IG, got {ig}"

def test_ig_monotonic_response():
    """PROVE: IG increases monotonically with improved metrics"""
    # Test improving bio-physics coherence
    metrics_low = {'bio_physics_vr': 0.1, 'planetary_momentum_error_ppm': 1000, 'planetary_energy_error_ppm': 1000}
    metrics_high = {'bio_physics_vr': 0.9, 'planetary_momentum_error_ppm': 1000, 'planetary_energy_error_ppm': 1000}
    
    ig_low = calculate_information_gravity(metrics_low)
    ig_high = calculate_information_gravity(metrics_high)
    
    assert ig_high > ig_low, f"Higher bio-physics should yield higher IG. Low: {ig_low}, High: {ig_high}"

def test_ig_bounds():
    """PROVE: IG always between 0.0 and 1.0"""
    test_cases = [
        {'bio_physics_vr': 0.5, 'planetary_momentum_error_ppm': 2500, 'planetary_energy_error_ppm': 2500},
        {'bio_physics_vr': 0.8, 'planetary_momentum_error_ppm': 100, 'planetary_energy_error_ppm': 100},
        {'bio_physics_vr': 0.2, 'planetary_momentum_error_ppm': 4000, 'planetary_energy_error_ppm': 4000},
    ]
    
    for metrics in test_cases:
        ig = calculate_information_gravity(metrics)
        assert 0.0 <= ig <= 1.0, f"IG out of bounds: {ig} for metrics {metrics}"

if __name__ == "__main__":
    test_ig_perfect_stability()
    test_ig_chaotic_state() 
    test_ig_monotonic_response()
    test_ig_bounds()
    print("✅ All IG aggregation tests passed!")
