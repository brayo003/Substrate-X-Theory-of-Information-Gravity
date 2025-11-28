"""
DEBUG: Why is bio_physics normalization returning 0.0001?
"""
import sys
import os
sys.path.insert(0, '/home/lenovo/Git/Substrate X Theory of Information Gravity')

from theory.information_gravity_core import normalize_bio_physics_vr
import inspect

# Check the function source
print("=== normalize_bio_physics_vr SOURCE CODE ===")
print(inspect.getsource(normalize_bio_physics_vr))
print()

# Test different input values
test_values = [0.1, 0.5, 0.9, 0.95, 1.0]
print("=== TESTING NORMALIZATION ===")
for val in test_values:
    result = normalize_bio_physics_vr(val)
    print(f"Input: {val} -> Output: {result}")
