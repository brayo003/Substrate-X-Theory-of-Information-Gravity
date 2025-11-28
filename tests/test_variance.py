import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from theory.dynamic_metrics_core import calculate_variance

def test_variance_constant_field():
    """PROVE: Constant field → zero variance"""
    constant_history = [
        np.array([1.0, 1.0, 1.0]),
        np.array([1.0, 1.0, 1.0]),
        np.array([1.0, 1.0, 1.0])
    ]
    variance = calculate_variance(constant_history)
    assert np.isclose(variance, 0.0, atol=1e-12), f"Constant field should have zero variance, got {variance}"

def test_variance_varying_field():
    """PROVE: Varying field → positive variance"""
    varying_history = [
        np.array([1.0, 2.0, 3.0]),
        np.array([2.0, 3.0, 4.0]),
        np.array([3.0, 4.0, 5.0])
    ]
    variance = calculate_variance(varying_history)
    assert variance > 0.0, f"Varying field should have positive variance, got {variance}"

def test_variance_bounds():
    """PROVE: Variance within reasonable bounds"""
    test_histories = [
        [np.array([0.1, 0.1]), np.array([0.1, 0.1]), np.array([0.1, 0.1])],  # Constant
        [np.array([0.1, 0.9]), np.array([0.2, 0.8]), np.array([0.3, 0.7])],  # High variance
    ]
    
    for history in test_histories:
        variance = calculate_variance(history)
        assert 0.0 <= variance <= 1.0, f"Variance out of bounds: {variance}"

if __name__ == "__main__":
    test_variance_constant_field()
    test_variance_varying_field()
    test_variance_bounds()
    print("✅ All variance tests passed!")
