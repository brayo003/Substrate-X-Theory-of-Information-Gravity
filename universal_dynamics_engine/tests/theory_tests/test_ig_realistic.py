"""
REALISTIC TEST: I_G Coherence with Actual System Behavior
Tests based on the actual IG score ranges and threshold values in the system.
"""
import unittest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal, EXPAND_THRESHOLD, CONTRACT_THRESHOLD

class TestIGRealistic(unittest.TestCase):
    
    def create_correct_metrics(self, bio_physics_vr=0.5, momentum_error=1000, energy_error=1000):
        """Create metrics that the IG function actually expects"""
        return {
            'bio_physics_vr': bio_physics_vr,
            'planetary_momentum_error_ppm': momentum_error,
            'planetary_energy_error_ppm': energy_error
        }
    
    def test_signal_logic_consistency(self):
        """Test that the signal logic is applied consistently"""
        print(f"System thresholds: EXPAND={EXPAND_THRESHOLD}, CONTRACT={CONTRACT_THRESHOLD}")
        
        # Test cases based on actual IG score ranges we observed
        test_cases = [
            (0.01, "Very low IG - should be CONTRACT"),
            (0.35, "Typical high IG - should be CONTRACT"), 
            (0.50, "Medium IG - should be CONTRACT"),
            (0.85, "High IG - should be CONTRACT (still below EXPAND)"),
            (0.95, "Very high IG - should be EXECUTE")
        ]
        
        for ig_expected, description in test_cases:
            # Create metrics that would produce approximately this IG score
            if ig_expected <= 0.35:
                metrics = self.create_correct_metrics(0.9, 100, 100)  # High stability
            else:
                # For testing higher IG scores, we'd need different metric combinations
                metrics = self.create_correct_metrics(0.9, 100, 100)
            
            signal_tuple = generate_risk_signal(metrics)
            signal_str, actual_ig = signal_tuple
            
            print(f"{description}: IG={actual_ig:.3f} -> {signal_str}")
            
            # Verify the signal matches the expected logic
            if actual_ig >= EXPAND_THRESHOLD:
                self.assertEqual(signal_str, "EXECUTE/EXPAND (High Confidence)")
            elif actual_ig <= CONTRACT_THRESHOLD:
                self.assertEqual(signal_str, "CONTRACT/STAND ASIDE (Low Confidence/High Risk)")
            else:
                self.assertEqual(signal_str, "CAUTION/HOLD (Ambiguous Coherence)")
    
    def test_ig_score_ranges(self):
        """Document the actual IG score ranges we can achieve"""
        print("\nActual IG Score Ranges:")
        
        # Test various metric combinations to see achievable IG range
        combinations = [
            (0.1, 5000, 5000, "Worst case"),
            (0.5, 2500, 2500, "Poor case"), 
            (0.9, 1000, 1000, "Average case"),
            (0.9, 100, 100, "Best case we can achieve")
        ]
        
        min_ig = float('inf')
        max_ig = float('-inf')
        
        for bp, mom, en, desc in combinations:
            metrics = self.create_correct_metrics(bp, mom, en)
            ig = calculate_information_gravity(metrics)
            signal_tuple = generate_risk_signal(metrics)
            signal_str = signal_tuple[0]
            
            min_ig = min(min_ig, ig)
            max_ig = max(max_ig, ig)
            
            print(f"  {desc}: bio_physics={bp}, errors=({mom},{en}) -> IG={ig:.3f} -> {signal_str}")
        
        print(f"\nAchievable IG range: {min_ig:.3f} to {max_ig:.3f}")
        print(f"Threshold range: CONTRACT={CONTRACT_THRESHOLD} to EXPAND={EXPAND_THRESHOLD}")
        
        # The issue: our achievable IG range doesn't reach the thresholds
        self.assertLess(max_ig, EXPAND_THRESHOLD, 
                       "System cannot reach EXECUTE threshold with current metric combinations")
    
    def test_threshold_analysis(self):
        """Analyze the threshold logic issue"""
        print(f"\nThreshold Analysis:")
        print(f"EXPAND_THRESHOLD: {EXPAND_THRESHOLD} (should trigger EXECUTE)")
        print(f"CONTRACT_THRESHOLD: {CONTRACT_THRESHOLD} (should trigger CONTRACT)")
        
        # The logical issue: thresholds are inverted
        if EXPAND_THRESHOLD > CONTRACT_THRESHOLD:
            print("ISSUE: Thresholds are inverted (EXPAND > CONTRACT)")
            print("This means: EXECUTE requires higher IG than CONTRACT")
            print("Normal logic: Low IG -> CONTRACT, High IG -> EXECUTE")
        else:
            print("Thresholds are correctly ordered")
            
        # Check if any IG scores can actually reach the thresholds
        high_stability_metrics = self.create_correct_metrics(1.0, 0, 0)  # Perfect stability
        max_achievable_ig = calculate_information_gravity(high_stability_metrics)
        print(f"Maximum achievable IG: {max_achievable_ig:.3f}")

if __name__ == '__main__':
    unittest.main()
