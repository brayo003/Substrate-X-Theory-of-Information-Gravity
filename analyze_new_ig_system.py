"""
ANALYZE: New IG system behavior after the fix
"""
import sys
import os
sys.path.insert(0, '/home/lenovo/Git/Substrate X Theory of Information Gravity')

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal

print("=== COMPLETE SYSTEM ANALYSIS ===")

# Test the full spectrum of possible states
test_cases = [
    # Extreme cases
    (0.01, 5000, 5000, "Catastrophic"),
    (0.1, 4000, 4000, "Critical"),
    (0.3, 3000, 3000, "High Risk"),
    # Normal operational range
    (0.5, 2000, 2000, "Moderate Risk"),
    (0.7, 1000, 1000, "Stable"),
    (0.9, 500, 500, "Very Stable"),
    (0.95, 100, 100, "Optimal"),
    (1.0, 50, 50, "Perfect")
]

print("FULL SPECTRUM ANALYSIS:")
print("=" * 80)
ig_scores = []
for bp, mom, en, desc in test_cases:
    metrics = {
        'bio_physics_vr': bp,
        'planetary_momentum_error_ppm': mom,
        'planetary_energy_error_ppm': en
    }
    ig = calculate_information_gravity(metrics)
    signal, _ = generate_risk_signal(metrics)
    ig_scores.append(ig)
    print(f"{desc:15} | bio_physics={bp:.2f} errors=({mom:4.0f},{en:4.0f}) | IG={ig:.4f} | {signal}")

# Calculate statistics
min_ig = min(ig_scores)
max_ig = max(ig_scores)
mean_ig = sum(ig_scores) / len(ig_scores)

print(f"\nSTATISTICS:")
print(f"  Range: {min_ig:.4f} to {max_ig:.4f}")
print(f"  Mean:  {mean_ig:.4f}")

# Calculate optimal thresholds (30th and 70th percentiles)
sorted_scores = sorted(ig_scores)
n = len(sorted_scores)
contract_idx = int(0.30 * n)
expand_idx = int(0.70 * n)

contract_threshold = sorted_scores[contract_idx]
expand_threshold = sorted_scores[expand_idx]

print(f"\nRECOMMENDED THRESHOLDS:")
print(f"  CONTRACT_THRESHOLD = {contract_threshold:.3f}  // IG < {contract_threshold:.3f} -> CONTRACT")
print(f"  EXPAND_THRESHOLD = {expand_threshold:.3f}    // IG > {expand_threshold:.3f} -> EXECUTE")
print(f"  Between {contract_threshold:.3f} and {expand_threshold:.3f} -> CAUTION")

# Show distribution
print(f"\nSIGNAL DISTRIBUTION WITH NEW THRESHOLDS:")
contract_count = sum(1 for ig in ig_scores if ig < contract_threshold)
caution_count = sum(1 for ig in ig_scores if contract_threshold <= ig <= expand_threshold)  
expand_count = sum(1 for ig in ig_scores if ig > expand_threshold)

print(f"  CONTRACT signals: {contract_count}/{len(ig_scores)} cases")
print(f"  CAUTION signals:  {caution_count}/{len(ig_scores)} cases")
print(f"  EXECUTE signals:  {expand_count}/{len(ig_scores)} cases")
