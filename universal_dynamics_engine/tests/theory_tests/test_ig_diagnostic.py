"""
DIAGNOSTIC TEST: Identify why IG scores are constant
"""
import sys
import os
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from theory.information_gravity_core import calculate_information_gravity, normalize_complexity, normalize_entropy, normalize_resonance, normalize_velocity

def test_normalization_functions():
    """Test each normalization function individually"""
    print("Testing normalization functions:")
    
    test_values = [0.1, 0.5, 0.9]
    
    for val in test_values:
        c = normalize_complexity(val)
        e = normalize_entropy(val) 
        r = normalize_resonance(val)
        v = normalize_velocity(val)
        print(f"Input: {val} -> Complexity: {c:.3f}, Entropy: {e:.3f}, Resonance: {r:.3f}, Velocity: {v:.3f}")

def test_ig_calculation_steps():
    """Test the IG calculation step by step"""
    print("\nTesting IG calculation steps:")
    
    metrics = {
        'complexity': 0.5,
        'entropy': 0.5, 
        'resonance': 0.5,
        'velocity': 0.5,
        'bio_physics_vr': 0.5,
        'quantum_coherence': 0.5,
        'temporal_stability': 0.5
    }
    
    # Test individual components
    s_c = normalize_complexity(metrics['complexity'])
    s_e = normalize_entropy(metrics['entropy'])
    s_r = normalize_resonance(metrics['resonance']) 
    s_v = normalize_velocity(metrics['velocity'])
    s_bp = 0.5  # Assuming default
    s_qc = 0.5  # Assuming default
    s_ts = 0.5  # Assuming default
    
    print(f"Normalized values: C={s_c:.3f}, E={s_e:.3f}, R={s_r:.3f}, V={s_v:.3f}")
    
    # Calculate weighted sum
    weights = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.10]
    components = [s_c, s_e, s_r, s_v, s_bp, s_qc, s_ts]
    
    weighted_sum = sum(w * c for w, c in zip(weights, components))
    print(f"Weighted sum: {weighted_sum:.3f}")
    
    # Final calculation
    final_ig = calculate_information_gravity(metrics)
    print(f"Final IG: {final_ig:.3f}")

if __name__ == '__main__':
    test_normalization_functions()
    test_ig_calculation_steps()
