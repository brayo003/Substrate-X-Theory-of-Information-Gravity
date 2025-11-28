"""
TEST: IG Calculation with Correct Metrics
Tests the IG calculation with the metrics it actually expects.
"""
import unittest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal

class TestIGCorrectMetrics(unittest.TestCase):
    
    def create_correct_test_metrics(self, bio_physics_vr=0.5, momentum_error=1000, energy_error=1000):
        """Create metrics that the IG function actually expects"""
        return {
            'bio_physics_vr': bio_physics_vr,
            'planetary_momentum_error_ppm': momentum_error,  # parts per million error
            'planetary_energy_error_ppm': energy_error       # parts per million error
        }
    
    def test_ig_with_correct_metrics(self):
        """Test IG calculation with the expected metrics"""
        print("Testing with correct metrics:")
        
        test_cases = [
            (0.9, 100, 100, "High bio-physics, low error"),
            (0.1, 5000, 5000, "Low bio-physics, high error"),
            (0.5, 2500, 2500, "Medium bio-physics, medium error")
        ]
        
        for bp_vr, mom_err, en_err, desc in test_cases:
            metrics = self.create_correct_test_metrics(bp_vr, mom_err, en_err)
            ig = calculate_information_gravity(metrics)
            signal_tuple = generate_risk_signal(metrics)
            signal_str = signal_tuple[0]
            
            print(f"{desc}: bio_physics_vr={bp_vr}, momentum_error={mom_err}, energy_error={en_err}")
            print(f"  -> IG={ig:.3f}, Signal={signal_str}")
            print()
    
    def test_ig_variation(self):
        """Test if we can get different IG scores with correct metrics"""
        # High stability case
        metrics_high = self.create_correct_test_metrics(
            bio_physics_vr=0.9,    # High pattern coherence
            momentum_error=100,     # Low error  
            energy_error=100        # Low error
        )
        
        # Low stability case  
        metrics_low = self.create_correct_test_metrics(
            bio_physics_vr=0.1,    # Low pattern coherence
            momentum_error=5000,    # High error
            energy_error=5000       # High error
        )
        
        ig_high = calculate_information_gravity(metrics_high)
        ig_low = calculate_information_gravity(metrics_low)
        
        print(f"High stability IG: {ig_high:.3f}")
        print(f"Low stability IG: {ig_low:.3f}")
        
        # These should be different if the function works correctly
        self.assertNotEqual(ig_high, ig_low, 
                           "IG scores should vary with different input metrics")

if __name__ == '__main__':
    unittest.main()
