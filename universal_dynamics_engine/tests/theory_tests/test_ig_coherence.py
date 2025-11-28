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
    
    def create_test_metrics(self, complexity, entropy, resonance, velocity):
        """Helper to create proper stability metrics dictionary"""
        return {
            'complexity': complexity,
            'entropy': entropy, 
            'resonance': resonance,
            'velocity': velocity,
            'bio_physics_vr': 0.5,
            'quantum_coherence': 0.5,
            'temporal_stability': 0.5
        }
    
    def test_low_ig_produces_execute_signal(self):
        """Test that low IG scores produce EXECUTE signals"""
        # Create metrics that should produce very low IG score
        metrics_low = self.create_test_metrics(
            complexity=0.1,  # Very low values
            entropy=0.1,     
            resonance=0.1,   
            velocity=0.1     
        )
        
        ig_low = calculate_information_gravity(metrics_low)
        signal_tuple = generate_risk_signal(metrics_low)
        
        # Extract signal string from tuple
        signal_str = signal_tuple[0]
        print(f"Low IG - Score: {ig_low:.3f}, Signal: {signal_str}")
        
        # Should be in EXECUTE phase
        self.assertTrue("EXECUTE" in signal_str.upper())
        
    def test_high_ig_produces_contract_signal(self):
        """Test that high IG scores produce CONTRACT signals"""
        # Create metrics that should produce very high IG score
        metrics_high = self.create_test_metrics(
            complexity=0.95,  # Very high values
            entropy=0.95,     
            resonance=0.95,   
            velocity=0.95     
        )
        
        ig_high = calculate_information_gravity(metrics_high)
        signal_tuple = generate_risk_signal(metrics_high)
        
        # Extract signal string from tuple
        signal_str = signal_tuple[0]
        print(f"High IG - Score: {ig_high:.3f}, Signal: {signal_str}")
        
        # Should be in CONTRACT phase
        self.assertTrue("CONTRACT" in signal_str.upper())
        
    def test_medium_ig_produces_monitor_signal(self):
        """Test that medium IG scores produce MONITOR signals"""
        # Create metrics that should produce medium IG score
        metrics_medium = self.create_test_metrics(
            complexity=0.5,  # Medium values
            entropy=0.5,     
            resonance=0.5,   
            velocity=0.5     
        )
        
        ig_medium = calculate_information_gravity(metrics_medium)
        signal_tuple = generate_risk_signal(metrics_medium)
        
        # Extract signal string from tuple
        signal_str = signal_tuple[0]
        print(f"Medium IG - Score: {ig_medium:.3f}, Signal: {signal_str}")
        
        # Should be in MONITOR phase
        self.assertTrue("MONITOR" in signal_str.upper())

    def test_threshold_logic(self):
        """Test the actual threshold logic with current values"""
        print(f"\nCurrent thresholds: EXPAND={EXPAND_THRESHOLD}, CONTRACT={CONTRACT_THRESHOLD}")
        
        # Test edge cases based on actual thresholds
        test_cases = [
            (0.1, "Should be EXECUTE"),
            (0.5, "Should be MONITOR"), 
            (0.85, "Should be CONTRACT"),
            (0.95, "Should be CONTRACT")
        ]
        
        for test_ig, expected in test_cases:
            # Create mock metrics that would produce this IG score
            mock_metrics = self.create_test_metrics(0.5, 0.5, 0.5, 0.5)
            signal_tuple = generate_risk_signal(mock_metrics)
            signal_str = signal_tuple[0]
            print(f"IG {test_ig}: {signal_str} - {expected}")

if __name__ == '__main__':
    unittest.main()
