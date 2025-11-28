"""
TEST: Full system with fixed IG calculation
"""
import sys
import os
sys.path.insert(0, '/home/lenovo/Git/Substrate X Theory of Information Gravity')

from theory.information_gravity_core import calculate_information_gravity, normalize_bio_physics_vr
from applications.universal_risk_indicator import generate_risk_signal

print("=== FIXED IG SYSTEM TEST ===")

# Test the normalization fix
print("Bio-Physics Normalization (FIXED):")
for val in [0.1, 0.5, 0.9]:
    norm = normalize_bio_physics_vr(val)
    print(f"  {val} -> {norm:.4f}")

# Test full IG calculation
test_cases = [
    (0.1, 5000, 5000, "Worst case"),
    (0.5, 2000, 2000, "Poor case"),
    (0.9, 100, 100, "Excellent case")
]

print("\nFull IG Calculation:")
for bp, mom, en, desc in test_cases:
    metrics = {
        'bio_physics_vr': bp,
        'planetary_momentum_error_ppm': mom,
        'planetary_energy_error_ppm': en
    }
    ig = calculate_information_gravity(metrics)
    signal, _ = generate_risk_signal(metrics)
    print(f"  {desc:12} | IG={ig:.4f} | {signal}")
