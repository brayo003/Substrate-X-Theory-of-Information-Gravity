# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
INTEGRATION TEST - Test all components together
"""
import sys
import time
from cognitive_governor import CognitiveGovernor

def test_integration():
    """Test the complete system integration"""
    print("🔧 INTEGRATION TEST - Substrate AI System")
    print("="*60)
    
    # Test 1: Initialize system
    print("1. Initializing Cognitive Governor...")
    try:
        gov = CognitiveGovernor(mode='local')
        print("✅ System initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test 2: Test each regime
    print("\n2. Testing regime detection...")
    test_questions = [
        ("What is 2+2?", "vanilla"),
        ("Explain quantum physics", "transitional"),
        ("Calculate sin(x) integral", "high_tension"),
        ("Solve quantum gravity", "saturated"),
    ]
    
    all_passed = True
    for question, expected in test_questions:
        print(f"\n   Testing: {question[:40]}...")
        result = gov.process_question(question)
        
        if result['regime'] == expected:
            print(f"   ✅ Correct regime: {result['regime']}")
        else:
            print(f"   ❌ Wrong regime: expected {expected}, got {result['regime']}")
            all_passed = False
        
        # Check that we got some response
        if 'response' not in result or not result['response']:
            print(f"   ⚠️  No response generated")
            all_passed = False
    
    # Test 3: Test actuator directly
    print("\n3. Testing symbolic computation...")
    from components.actuator import PythonActuator
    actuator = PythonActuator()
    
    test_code = "import sympy\nx = sympy.symbols('x')\nresult = sympy.integrate(x**2, (x, 0, 1))"
    result = actuator.execute_math(test_code)
    
    if result['success']:
        print(f"✅ Actuator works: {result['output']}")
    else:
        print(f"❌ Actuator failed: {result['output']}")
        all_passed = False
    
    # Test 4: Check system stats
    print("\n4. Checking system statistics...")
    stats = gov.get_stats()
    if stats['total'] == len(test_questions):
        print(f"✅ Stats correct: processed {stats['total']} queries")
    else:
        print(f"❌ Stats mismatch: expected {len(test_questions)}, got {stats['total']}")
        all_passed = False
    
    # Final verdict
    print("\n" + "="*60)
    if all_passed:
        print("🎉 INTEGRATION TEST PASSED!")
        print("All components are working together correctly.")
        return True
    else:
        print("⚠️  INTEGRATION TEST HAD ISSUES")
        print("Some components need attention.")
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
