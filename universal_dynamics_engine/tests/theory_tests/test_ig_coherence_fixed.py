"""
FIXED INTEGRATION TEST: I_G Coherence Integrity
Uses the correct metrics that the IG calculation actually expects.
"""
import unittest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal, EXPAND_THRESHOLD, CONTRACT_THRESHOLD

class TestIGCoherenceFixed(unittest.TestCase):
    
    def create_correct_metrics(self, bio_physics_vr=0.5, momentum_error=1000, energy_error=1000):
        """Create metrics that the IG function actually expects"""
        return {
            'bio_physics_vr': bio_physics_vr,
            'planetary_momentum_error_ppm': momentum_error,
            'planetary_energy_error_ppm': energy_error
        }
    
    def test_low_ig_produces_execute_signal(self):
        """Test that low IG scores produce EXECUTE signals"""
        # Create metrics that should produce low IG score
        # Low pattern coherence + high errors = low IG
        metrics_low = self.create_correct_metrics(
            bio_physics_vr=0.1,      # Low pattern coherence
            momentum_error=5000,      # High momentum error
            energy_error=5000         # High energy error
        )
        
        ig_low = calculate_information_gravity(metrics_low)
        signal_tuple = generate_risk_signal(metrics_low)
        signal_str = signal_tuple[0]
        
        print(f"Low IG - Score: {ig_low:.3f}, Signal: {signal_str}")
        
        # Should be in EXECUTE phase (IG < EXPAND_THRESHOLD)
        self.assertTrue("EXECUTE" in signal_str.upper())
        self.assertLess(ig_low, EXPAND_THRESHOLD)
        
    def test_high_ig_produces_contract_signal(self):
        """Test that high IG scores produce CONTRACT signals"""
        # Create metrics that should produce high IG score
        # High pattern coherence + low errors = high IG
        metrics_high = self.create_correct_metrics(
            bio_physics_vr=0.9,      # High pattern coherence
            momentum_error=100,       # Low momentum error
            energy_error=100          # Low energy error
        )
        
        ig_high = calculate_information_gravity(metrics_high)
        signal_tuple = generate_risk_signal(metrics_high)
        signal_str = signal_tuple[0]
        
        print(f"High IG - Score: {ig_high:.3f}, Signal: {signal_str}")
        
        # Should be in CONTRACT phase (IG > CONTRACT_THRESHOLD)
        self.assertTrue("CONTRACT" in signal_str.upper())
        self.assertGreater(ig_high, CONTRACT_THRESHOLD)
        
    def test_threshold_values(self):
        """Display current threshold values"""
        print(f"\nCurrent thresholds: EXPAND={EXPAND_THRESHOLD}, CONTRACT={CONTRACT_THRESHOLD}")
        print("Note: With current inverted thresholds (0.9 > 0.8), logic may need adjustment")

if __name__ == '__main__':
    unittest.main()
