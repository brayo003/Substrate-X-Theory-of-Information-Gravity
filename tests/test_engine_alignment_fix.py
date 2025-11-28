import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core_math.alignment import compute_alignment

def test_engine_alignment_broken_logic():
    """DEMONSTRATE: Why the engine's alignment calculation is broken"""
    
    # Simulate the engine's current broken logic
    def broken_engine_alignment(tensions, num_domains):
        alignment_variance = np.var(tensions)
        base_alignment = 0.8 / num_domains 
        alignment = np.clip(base_alignment + (0.3 - alignment_variance * 10000), 0.1, 1.0)
        return alignment
    
    # Test case: 3 domains with moderate tensions
    tensions = [0.1, 0.2, 0.3]
    
    # Engine's broken calculation
    engine_alignment = broken_engine_alignment(tensions, num_domains=3)
    
    # Mathematical correct calculation  
    math_alignment = compute_alignment(tensions)
    
    print(f"Tensions: {tensions}")
    print(f"Engine (broken) alignment: {engine_alignment:.4f}")
    print(f"Mathematical alignment: {math_alignment:.4f}")
    print(f"Variance: {np.var(tensions):.6f}")
    print(f"Engine scaling issue: variance * 10000 = {np.var(tensions) * 10000:.1f}")

def test_proposed_engine_fix():
    """PROPOSE: Fixed alignment calculation for engine"""
    
    def fixed_engine_alignment(tensions, num_domains):
        # Use the mathematically proven alignment function
        return compute_alignment(tensions)
    
    # Test various scenarios
    test_cases = [
        ([0.1, 0.1, 0.1], "Identical tensions"),
        ([0.01, 0.1, 0.5, 1.0], "Divergent tensions"),
        ([0.2, 0.25, 0.3], "Moderate alignment")
    ]
    
    print("\nPROPOSED FIX - Mathematical Alignment:")
    for tensions, description in test_cases:
        alignment = fixed_engine_alignment(tensions, len(tensions))
        print(f"  {description:20} → Alignment: {alignment:.4f}")

if __name__ == "__main__":
    test_engine_alignment_broken_logic()
    test_proposed_engine_fix()
