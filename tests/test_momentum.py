import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from theory.dynamic_metrics_core import calculate_momentum

def test_momentum_stable_field():
    """PROVE: Stable/constant field → zero momentum"""
    stable_history = [
        np.array([1.0, 1.0, 1.0]),
        np.array([1.0, 1.0, 1.0]),  # No change
        np.array([1.0, 1.0, 1.0])   # No change
    ]
    momentum = calculate_momentum(stable_history)
    assert np.isclose(momentum, 0.0, atol=1e-12), f"Stable field should have zero momentum, got {momentum}"

def test_momentum_trending_field():
    """PROVE: Trending field → positive momentum"""
    trending_history = [
        np.array([1.0, 1.0, 1.0]),
        np.array([1.5, 1.5, 1.5]),  # Upward trend
        np.array([2.0, 2.0, 2.0])   # Continued upward
    ]
    momentum = calculate_momentum(trending_history)
    assert momentum > 0.0, f"Trending field should have positive momentum, got {momentum}"

def test_momentum_oscillating_field():
    """PROVE: Oscillating field → reflects net direction"""
    oscillating_history = [
        np.array([1.0, 1.0, 1.0]),
        np.array([2.0, 2.0, 2.0]),  # Up
        np.array([1.5, 1.5, 1.5])   # Down but net positive
    ]
    momentum = calculate_momentum(oscillating_history)
    # Should be positive due to net upward movement
    assert momentum > 0.0, f"Net upward movement should yield positive momentum, got {momentum}"

def test_momentum_bounds():
    """PROVE: Momentum within reasonable bounds"""
    # Test various field histories
    test_histories = [
        [np.array([0.1, 0.1]), np.array([0.1, 0.1]), np.array([0.1, 0.1])],  # Stable
        [np.array([0.1, 0.1]), np.array([0.5, 0.5]), np.array([0.9, 0.9])],  # Strong trend
        [np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([1.0, 0.0])],  # Oscillation
    ]
    
    for history in test_histories:
        momentum = calculate_momentum(history)
        assert 0.0 <= momentum <= 1.0, f"Momentum out of bounds: {momentum}"

if __name__ == "__main__":
    test_momentum_stable_field()
    test_momentum_trending_field() 
    test_momentum_oscillating_field()
    test_momentum_bounds()
    print("✅ All momentum tests passed!")
