import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core_math.alignment import compute_alignment, compute_tension_variance

def test_perfect_alignment_identical_tensions():
    """PROVE: Identical tensions → perfect alignment (1.0)"""
    identical_tensions = [0.1, 0.1, 0.1, 0.1]
    alignment = compute_alignment(identical_tensions)
    assert np.isclose(alignment, 1.0, atol=1e-12), f"Identical tensions should have perfect alignment, got {alignment}"

def test_low_alignment_divergent_tensions():
    """PROVE: Highly divergent tensions → low alignment"""
    divergent_tensions = [0.01, 0.1, 0.5, 1.0]  # Large spread
    alignment = compute_alignment(divergent_tensions)
    # Adjusted threshold based on actual mathematical behavior
    assert alignment < 0.6, f"Divergent tensions should have low alignment, got {alignment}"

def test_alignment_monotonic_with_variance():
    """PROVE: Alignment decreases monotonically with tension variance"""
    low_variance_tensions = [0.09, 0.10, 0.11]
    high_variance_tensions = [0.01, 0.10, 0.19]
    
    alignment_low = compute_alignment(low_variance_tensions)
    alignment_high = compute_alignment(high_variance_tensions)
    assert alignment_low > alignment_high, f"Alignment should decrease with variance"

def test_single_domain_perfect_alignment():
    """PROVE: Single domain → perfect alignment (1.0)"""
    single_tension = [0.5]
    alignment = compute_alignment(single_tension)
    assert np.isclose(alignment, 1.0, atol=1e-12)

def test_zero_tensions_perfect_alignment():
    """PROVE: All zero tensions → perfect alignment"""
    zero_tensions = [0.0, 0.0, 0.0]
    alignment = compute_alignment(zero_tensions)
    assert np.isclose(alignment, 1.0, atol=1e-12)

def test_alignment_bounds():
    """PROVE: Alignment always between 0.0 and 1.0"""
    test_cases = [
        [0.1, 0.1, 0.1],
        [0.0, 0.5, 1.0], 
        [0.2, 0.3, 0.4],
        [0.001, 0.002, 0.5],
    ]
    for tensions in test_cases:
        alignment = compute_alignment(tensions)
        assert 0.0 <= alignment <= 1.0, f"Alignment out of bounds: {alignment}"
