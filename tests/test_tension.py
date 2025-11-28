import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core_math.tension import compute_tension, compute_tension_variance

def test_uniform_concentration_zero_tension():
    """PROVE: Uniform concentration → zero tension"""
    # Test case 1: Perfectly uniform data
    uniform_data = np.ones(100) * 1.2345
    tension = compute_tension(uniform_data)
    
    # Mathematical proof: uniform data → zero gradient → zero tension
    assert np.isclose(tension, 0.0, atol=1e-12), f"Uniform data should have zero tension, got {tension}"
    
    # Test case 2: Another uniform dataset
    uniform_data_2 = np.full(50, 0.789)
    tension_2 = compute_tension(uniform_data_2)
    assert np.isclose(tension_2, 0.0, atol=1e-12), f"Uniform data should have zero tension, got {tension_2}"

def test_linear_gradient_positive_tension():
    """PROVE: Linear gradient → positive tension that scales appropriately"""
    # Create linear gradient
    linear_data = np.linspace(0.0, 1.0, 100)
    tension = compute_tension(linear_data)
    
    # Should be positive
    assert tension > 0.0, f"Linear gradient should have positive tension, got {tension}"
    
    # Stronger gradient should have higher tension
    steeper_data = np.linspace(0.0, 2.0, 100)  # 2x gradient
    steeper_tension = compute_tension(steeper_data)
    assert steeper_tension > tension, f"Steeper gradient should have higher tension"

def test_tension_variance_calculation():
    """PROVE: Tension variance calculation works correctly"""
    # Identical tensions → zero variance
    identical_tensions = [0.1, 0.1, 0.1, 0.1]
    variance = compute_tension_variance(identical_tensions)
    assert np.isclose(variance, 0.0, atol=1e-12), f"Identical tensions should have zero variance, got {variance}"
    
    # Different tensions → positive variance
    different_tensions = [0.1, 0.2, 0.3, 0.4]
    variance_2 = compute_tension_variance(different_tensions)
    assert variance_2 > 0.0, f"Different tensions should have positive variance, got {variance_2}"

def test_tension_invariance_to_constant_shift():
    """PROVE: Tension depends on gradient, not absolute values"""
    original_data = np.array([1.0, 2.0, 3.0, 4.0])
    shifted_data = original_data + 10.0  # Constant shift
    
    tension_original = compute_tension(original_data)
    tension_shifted = compute_tension(shifted_data)
    
    # Gradient is identical → tension should be identical
    assert np.isclose(tension_original, tension_shifted, atol=1e-12), \
        f"Tension should be invariant to constant shift. Original: {tension_original}, Shifted: {tension_shifted}"
