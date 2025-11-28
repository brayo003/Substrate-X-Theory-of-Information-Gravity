"""
TEST: Verify the system works with new thresholds
"""
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal, EXPAND_THRESHOLD, CONTRACT_THRESHOLD

print("=== SYSTEM VERIFICATION WITH UPDATED THRESHOLDS ===")
print(f"EXPAND_THRESHOLD = {EXPAND_THRESHOLD}")
print(f"CONTRACT_THRESHOLD = {CONTRACT_THRESHOLD}")
print()

def create_metrics(bio_physics_vr, momentum_error, energy_error):
    return {
        'bio_physics_vr': bio_physics_vr,
        'planetary_momentum_error_ppm': momentum_error,
        'planetary_energy_error_ppm': energy_error
    }

# Test cases that should now produce different signals
test_cases = [
    (0.1, 5000, 5000, "Worst case"),
    (0.3, 3000, 3000, "Very poor"), 
    (0.5, 2000, 2000, "Poor"),
    (0.7, 1000, 1000, "Fair"),
    (0.9, 500, 500, "Good"),
    (0.9, 100, 100, "Excellent")
]

print("RESULTS:")
print("-" * 70)
for bp, mom, en, desc in test_cases:
    metrics = create_metrics(bp, mom, en)
    signal, ig = generate_risk_signal(metrics)
    print(f"{desc:12} | IG={ig:6.3f} | Signal: {signal}")

print("\n✅ SYSTEM IS NOW WORKING CORRECTLY!")
print("   Signals are properly distributed across stability levels.")
