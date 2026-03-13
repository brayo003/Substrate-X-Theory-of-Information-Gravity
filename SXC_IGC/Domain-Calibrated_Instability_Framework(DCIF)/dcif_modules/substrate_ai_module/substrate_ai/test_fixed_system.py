# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
TEST FIXED SYSTEM - With proper tension detection
"""
from cognitive_governor import CognitiveGovernor

def test_fixed():
    """Test with proper tension detection"""
    gov = CognitiveGovernor(mode='local')
    
    # Test cases with expected regimes
    test_cases = [
        # Chess - should be VANILLA
        ("Find mate in two moves", 'vanilla'),
        
        # Philosophy - should be TRANSITIONAL
        ("Explain Arrhenius theorem", 'transitional'),
        
        # Math calculation - should be HIGH_TENSION
        ("Calculate integral of x^2 from 0 to 1", 'high_tension'),
        
        # Complex physics - should be SATURATED
        ("Solve Navier-Stokes 3D turbulence", 'saturated'),
    ]
    
    print("🧪 TESTING FIXED TENSION DETECTION")
    print("="*60)
    
    results = []
    for question, expected in test_cases:
        print(f"\nQ: {question}")
        result = gov.process_question(question)
        
        actual = result['regime']
        match = "✅" if actual == expected else "❌"
        
        print(f"{match} Expected: {expected.upper()}, Got: {actual.upper()}")
        
        results.append({
            'question': question[:50],
            'expected': expected,
            'actual': actual,
            'match': actual == expected,
            'tension': result['tension'],
            'strategy': result['strategy']
        })
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    matches = sum(1 for r in results if r['match'])
    accuracy = matches / len(results) * 100
    
    print(f"Accuracy: {accuracy:.1f}% ({matches}/{len(results)})")
    
    print(f"\nDetailed results:")
    for r in results:
        status = "✅" if r['match'] else "❌"
        print(f"{status} {r['question']:40} | Tension: {r['tension']:.2f} | Strategy: {r['strategy']}")
    
    # Print dashboard
    gov.print_dashboard()
    
    return results

if __name__ == "__main__":
    test_fixed()
