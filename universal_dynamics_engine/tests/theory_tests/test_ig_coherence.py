"""
INTEGRATION VALIDATION TEST: I_G Coherence Integrity
Tests the end-to-end flow from domain metrics to the final URI signal.
Verifies that the IG score transitions cleanly across the EXECUTE/CONTRACT thresholds.
"""
import unittest
import sys
import numpy as np
import os

# Insert the project root and application root into the system path
# This is required because this test is nested four directories deep.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Corrected Imports (will now look in the path we just added)
from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal, EXPAND_THRESHOLD, CONTRACT_THRESHOLD

class TestIGCoherence(unittest.TestCase):
    
    def test_expand_threshold_transition(self):
        """Test that values near EXPAND_THRESHOLD produce correct signals"""
        # Test just below expand threshold
        metrics_below = {
            'complexity': 0.4,
            'entropy': 0.3,
            'resonance': 0.5,
            'velocity': 0.6
        }
        ig_below = calculate_information_gravity(metrics_below)
        signal_below = generate_risk_signal(ig_below)
        
        # Should be in EXECUTE phase
        self.assertEqual(signal_below.split()[0], "EXECUTE")
        
    def test_contract_threshold_transition(self):
        """Test that values near CONTRACT_THRESHOLD produce correct signals"""
        # Test just above contract threshold
        metrics_above = {
            'complexity': 0.8,
            'entropy': 0.9,
            'resonance': 0.7,
            'velocity': 0.8
        }
        ig_above = calculate_information_gravity(metrics_above)
        signal_above = generate_risk_signal(ig_above)
        
        # Should be in CONTRACT phase
        self.assertEqual(signal_above.split()[0], "CONTRACT")
        
    def test_between_thresholds(self):
        """Test values between thresholds produce MONITOR signals"""
        metrics_mid = {
            'complexity': 0.6,
            'entropy': 0.5,
            'resonance': 0.6,
            'velocity': 0.5
        }
        ig_mid = calculate_information_gravity(metrics_mid)
        signal_mid = generate_risk_signal(ig_mid)
        
        # Should be in MONITOR phase
        self.assertEqual(signal_mid.split()[0], "MONITOR")

if __name__ == '__main__':
    unittest.main()
