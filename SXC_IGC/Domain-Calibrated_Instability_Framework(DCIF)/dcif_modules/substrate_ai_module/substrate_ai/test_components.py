#!/usr/bin/env python3
"""
TEST ALL COMPONENTS INDIVIDUALLY
"""
print("🧪 TESTING SUBSTRATE AI COMPONENTS")
print("="*60)

# Test 1: Substrate Core
print("\n1️⃣ TESTING SUBSTRATE CORE (V12 Physics)...")
try:
    from components.substrate_core import SubstrateDynamics
    substrate = SubstrateDynamics()
    
    # Test tension calculation
    tension = substrate.calculate_tension(0.5, 0.3, 0.2)
    regime = substrate.determine_regime(tension)
    print(f"✅ Substrate Core: tension={tension:.3f}, regime={regime}")
except Exception as e:
    print(f"❌ Substrate Core failed: {e}")

# Test 2: Problem Analyzer
print("\n2️⃣ TESTING PROBLEM ANALYZER...")
try:
    from components.problem_analyzer import ProblemAnalyzer
    analyzer = ProblemAnalyzer()
    
    test_problem = "Compute the integral of x^2 from 0 to 1 using calculus"
    features = analyzer.extract_features(test_problem)
    tension = analyzer.predict_tension_from_features(features)
    
    print(f"✅ Problem Analyzer: features={len(features)}, tension={tension:.3f}")
    print(f"   Problem type: {features.get('problem_type', 'unknown')}")
except Exception as e:
    print(f"❌ Problem Analyzer failed: {e}")

# Test 3: Actuator
print("\n3️⃣ TESTING ACTUATOR (Symbolic Execution)...")
try:
    from components.actuator import PythonActuator
    actuator = PythonActuator()
    
    test_code = """
import sympy
x = sympy.symbols('x')
result = sympy.integrate(x**2, (x, 0, 1))
"""
    result = actuator.execute_math(test_code)
    
    if result['success']:
        print(f"✅ Actuator executed successfully!")
        print(f"   Output: {result['output']}")
    else:
        print(f"⚠️  Actuator execution failed: {result['output']}")
except Exception as e:
    print(f"❌ Actuator failed: {e}")

# Test 4: Ollama Bridge
print("\n4️⃣ TESTING OLLAMA BRIDGE (Local LLM)...")
try:
    from components.ollama_bridge import OllamaBridge
    bridge = OllamaBridge()
    
    # Test if Ollama is running
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama is running")
            print(f"   Available models: {response.json()}")
        else:
            print("⚠️  Ollama not responding properly")
    except:
        print("⚠️  Ollama not running - skipping bridge test")
except Exception as e:
    print(f"❌ Ollama Bridge setup failed: {e}")

print("\n" + "="*60)
print("COMPONENT TEST COMPLETE")
print("="*60)
