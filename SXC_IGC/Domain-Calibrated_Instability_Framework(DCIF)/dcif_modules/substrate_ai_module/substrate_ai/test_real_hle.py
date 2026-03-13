# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
TEST WITH ACTUAL HLE PATTERNS
"""
from components.substrate_core import SubstrateDynamics
from components.problem_analyzer import ProblemAnalyzer

def test_hle_patterns():
    """Test with patterns from your HLE data"""
    analyzer = ProblemAnalyzer()
    substrate = SubstrateDynamics()
    
    # Real examples from your HLE data
    test_cases = [
        # Chess - low tension (should succeed)
        ("Find the mate in two for White after Black's move in this position...", 'chess', 0.25),
        
        # Philosophy - medium-high tension (failed with 100% confidence)
        ("Explain how critical-level views violate non-elitism in Arrhenius's sixth impossibility theorem.", 'philosophy', 0.65),
        
        # Math - high tension (gave up with 0% confidence)
        ("Compute the reduced 12th-dimensional spin bordism of the classifying space for G2.", 'math', 0.92),
        
        # Word puzzle - high tension (nonsense with 100% confidence)
        ("Decode this cipher: Ktkf kdfkgd ktj jtdfkt dfkt gfkgt ktjsk gkdfk kgjdfg.", 'wordplay', 0.75),
        
        # Physics - very high tension
        ("Solve the Navier-Stokes equation for turbulent flow in 3D.", 'physics', 0.99),
        
        # Simple calculation - medium tension
        ("Calculate the integral of x^2 from 0 to 1.", 'math', 0.6),
    ]
    
    print("🧪 TESTING HLE PATTERN RECOGNITION")
    print("="*70)
    print("Pattern | Expected Tension | Predicted Tension | Regime")
    print("-"*70)
    
    for question, expected_type, expected_tension in test_cases:
        features = analyzer.extract_features(question)
        predicted_tension = analyzer.predict_tension_from_features(features)
        regime = substrate.determine_regime(predicted_tension)
        
        predicted_type = features.get('problem_type', 'unknown')
        type_match = "✅" if predicted_type == expected_type else "❌"
        
        print(f"{type_match} {predicted_type:10} | {expected_tension:.2f} | {predicted_tension:.2f} | {regime}")
        
        # Show feature breakdown for debugging
        if "integral" in question.lower():
            print(f"  Features: math_symbols={features.get('math_symbols',0):.2f}, "
                  f"technical={features.get('technical_density',0):.2f}")
    
    print("\n🎯 INTERPRETATION:")
    print("• Chess (<0.3): Should work well (95% success)")
    print("• Philosophy (0.65): High risk of wrong but confident answers")
    print("• Math (>0.8): Likely to fail or give up")
    print("• Word puzzles (0.75): High risk of nonsense")
    print("• Physics (>0.9): Almost certain failure")

if __name__ == "__main__":
    test_hle_patterns()
