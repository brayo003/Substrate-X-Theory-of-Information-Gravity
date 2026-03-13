# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
TEST SYSTEM - Run test scenarios
"""
from cognitive_governor import CognitiveGovernor

def test_scenarios():
    """Test different tension scenarios"""
    gov = CognitiveGovernor(mode='local')  # Change to 'cloud' if API key available
    
    test_cases = [
        ("What is 2+2?", "vanilla"),
        ("Explain quantum entanglement", "transitional"),
        ("Compute integral of x^2 from 0 to 1", "high_tension"),
        ("Solve the Navier-Stokes equation", "saturated"),
    ]
    
    print("🧪 RUNNING TEST SUITE")
    print("="*60)
    
    results = []
    for question, expected in test_cases:
        print(f"\nTEST: {expected.upper()}")
        result = gov.process_question(question)
        
        status = "✅" if result['regime'] == expected else "❌"
        print(f"{status} Got: {result['regime']} | Expected: {expected}")
        
        results.append({
            'question': question,
            'expected': expected,
            'actual': result['regime'],
            'match': result['regime'] == expected,
            'response': result['response'][:100] + "...",
            'confidence': result.get('confidence', 0)
        })
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    matches = sum(1 for r in results if r['match'])
    print(f"Accuracy: {matches}/{len(results)} ({matches/len(results)*100:.1f}%)")
    
    stats = gov.get_stats()
    print(f"\nSystem Stats:")
    print(f"  Total queries: {stats['total']}")
    print(f"  Success: {stats['success']}")
    print(f"  Fail: {stats['fail']}")
    
    return results

if __name__ == "__main__":
    test_scenarios()
