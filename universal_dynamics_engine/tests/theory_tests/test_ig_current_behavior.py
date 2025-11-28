"""
TEST: Current IG Behavior Analysis
Tests and documents the current IG calculation behavior to help identify the issue.
"""
import unittest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from theory.information_gravity_core import calculate_information_gravity
from applications.universal_risk_indicator import generate_risk_signal

class TestCurrentIGBehavior(unittest.TestCase):
    
    def create_test_metrics(self, complexity, entropy, resonance, velocity):
        return {
            'complexity': complexity,
            'entropy': entropy, 
            'resonance': resonance,
            'velocity': velocity,
            'bio_physics_vr': 0.5,
            'quantum_coherence': 0.5,
            'temporal_stability': 0.5
        }
    
    def test_ig_consistency(self):
        """Test that IG calculation is consistent (even if currently broken)"""
        test_cases = [
            (0.1, 0.1, 0.1, 0.1, "Very Low"),
            (0.5, 0.5, 0.5, 0.5, "Medium"), 
            (0.9, 0.9, 0.9, 0.9, "Very High")
        ]
        
        results = []
        for c, e, r, v, desc in test_cases:
            metrics = self.create_test_metrics(c, e, r, v)
            ig = calculate_information_gravity(metrics)
            signal_tuple = generate_risk_signal(metrics)
            signal_str = signal_tuple[0]
            
            results.append({
                'description': desc,
                'metrics': (c, e, r, v),
                'ig_score': ig,
                'signal': signal_str
            })
            
            print(f"{desc}: IG={ig:.3f}, Signal={signal_str}")
        
        # All IG scores should be the same with current implementation
        ig_scores = [r['ig_score'] for r in results]
        self.assertTrue(all(score == ig_scores[0] for score in ig_scores), 
                       f"All IG scores should be identical: {ig_scores}")
    
    def test_signal_consistency(self):
        """Test that signals are consistent given current IG behavior"""
        metrics = self.create_test_metrics(0.1, 0.1, 0.1, 0.1)
        signal_tuple = generate_risk_signal(metrics)
        signal_str = signal_tuple[0]
        
        # With current implementation, all signals should be CONTRACT
        self.assertEqual(signal_str, "CONTRACT/STAND ASIDE (Low Confidence/High Risk)")

if __name__ == '__main__':
    unittest.main()
