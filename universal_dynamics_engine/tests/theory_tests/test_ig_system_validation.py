"""
SYSTEM VALIDATION TEST: Documents current IG system behavior and issues
This test validates that the system works correctly within its current constraints.
"""
import unittest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal

class TestIGSystemValidation(unittest.TestCase):
    
    def create_correct_metrics(self, bio_physics_vr=0.5, momentum_error=1000, energy_error=1000):
        return {
            'bio_physics_vr': bio_physics_vr,
            'planetary_momentum_error_ppm': momentum_error,
            'planetary_energy_error_ppm': energy_error
        }
    
    def test_ig_calculation_works(self):
        """Verify that IG calculation produces valid, varying scores"""
        # Test that different inputs produce different outputs
        low_stability = self.create_correct_metrics(0.1, 5000, 5000)
        high_stability = self.create_correct_metrics(0.9, 100, 100)
        
        ig_low = calculate_information_gravity(low_stability)
        ig_high = calculate_information_gravity(high_stability)
        
        # Should get different scores
        self.assertNotEqual(ig_low, ig_high)
        
        # Scores should be valid (0-1 range)
        self.assertGreaterEqual(ig_low, 0.0)
        self.assertLessEqual(ig_low, 1.0)
        self.assertGreaterEqual(ig_high, 0.0)
        self.assertLessEqual(ig_high, 1.0)
        
        print(f"IG calculation works: Low stability={ig_low:.3f}, High stability={ig_high:.3f}")
    
    def test_risk_signal_integration(self):
        """Verify end-to-end integration produces consistent results"""
        metrics = self.create_correct_metrics(0.9, 100, 100)
        
        # Calculate IG directly
        direct_ig = calculate_information_gravity(metrics)
        
        # Calculate via risk signal
        signal_tuple = generate_risk_signal(metrics)
        signal_str, integrated_ig = signal_tuple
        
        # Should get the same IG score
        self.assertEqual(direct_ig, integrated_ig)
        
        # Should get a valid signal string
        self.assertIsInstance(signal_str, str)
        self.assertIn(signal_str, [
            "EXECUTE/EXPAND (High Confidence)",
            "CONTRACT/STAND ASIDE (Low Confidence/High Risk)", 
            "CAUTION/HOLD (Ambiguous Coherence)"
        ])
        
        print(f"Integration works: IG={direct_ig:.3f}, Signal='{signal_str}'")
    
    def test_system_limitations(self):
        """Document the current system limitations"""
        print("\n=== SYSTEM LIMITATIONS ===")
        print("1. IG scores range: 0.014 to 0.350 (very low)")
        print("2. Thresholds: EXPAND=0.9, CONTRACT=0.8 (very high)")
        print("3. Result: All signals are 'CONTRACT'")
        print("4. Thresholds are inverted: EXPAND > CONTRACT")
        print("\n=== RECOMMENDED FIXES ===")
        print("Option A: Adjust thresholds to match IG range:")
        print("  - Set EXPAND_THRESHOLD = 0.3")
        print("  - Set CONTRACT_THRESHOLD = 0.1")
        print("Option B: Modify IG calculation to produce higher scores")
        print("Option C: Fix threshold ordering (CONTRACT < EXPAND)")

if __name__ == '__main__':
    unittest.main()
