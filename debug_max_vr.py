"""
DEBUG: Find the MAX_VR_BIO_PHYSICS value
"""
import sys
import os
sys.path.insert(0, '/home/lenovo/Git/Substrate X Theory of Information Gravity')

from theory.information_gravity_core import MAX_VR_BIO_PHYSICS, MAX_ABS_MOMENTUM_ERROR_PPM

print("=== CRITICAL CONSTANTS ===")
print(f"MAX_VR_BIO_PHYSICS: {MAX_VR_BIO_PHYSICS}")
print(f"MAX_ABS_MOMENTUM_ERROR_PPM: {MAX_ABS_MOMENTUM_ERROR_PPM}")

# Show the math problem
print(f"\n=== THE BUG ===")
test_value = 0.9
result = test_value / MAX_VR_BIO_PHYSICS
print(f"0.9 / {MAX_VR_BIO_PHYSICS} = {result}")
print(f"tanh({result}) = {np.tanh(result)}")  # This is essentially 0!

# Show what it SHOULD be
print(f"\n=== WHAT IT SHOULD BE ===")
reasonable_max = 1.0  # Since bio_physics_vr is already 0-1 normalized
reasonable_result = test_value / reasonable_max
print(f"0.9 / {reasonable_max} = {reasonable_result}")
print(f"tanh({reasonable_result}) = {np.tanh(reasonable_result)}")  # This is ~0.72
