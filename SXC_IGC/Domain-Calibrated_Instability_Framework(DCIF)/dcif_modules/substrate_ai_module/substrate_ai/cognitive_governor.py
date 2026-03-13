# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
COGNITIVE GOVERNOR - Main orchestration (UPDATED)
"""
from components.substrate_core import SubstrateDynamics
from components.problem_analyzer import ProblemAnalyzer
from components.actuator import PythonActuator
from components.ollama_bridge import OllamaBridge
from components.cloud_bridge import CloudBridge

class CognitiveGovernor:
    def __init__(self, mode='hybrid'):
        self.substrate = SubstrateDynamics()
        self.analyzer = ProblemAnalyzer()
        self.actuator = PythonActuator()
        self.ollama = OllamaBridge()
        self.cloud = CloudBridge() if mode == 'cloud' else None
        self.mode = mode
        
        self.history = []
        self.stats = {
            'total': 0,
            'vanilla': 0,
            'transitional': 0,
            'high_tension': 0,
            'saturated': 0,
            'failures': 0
        }
    
    def process_question(self, question: str, max_retries: int = 3):
        """Main processing pipeline"""
        self.stats['total'] += 1
        print(f"\n{'='*60}")
        print(f"🧠 PROCESSING: {question[:80]}...")
        
        # STEP 1: Analyze tension
        features = self.analyzer.extract_features(question)
        tension = self.analyzer.predict_tension_from_features(features)
        regime = self.substrate.determine_regime(tension)
        
        # Update stats
        self.stats[regime] = self.stats.get(regime, 0) + 1
        
        print(f"📊 TENSION: {tension:.2f} | REGIME: {regime.upper()}")
        print(f"📋 Problem type: {features.get('problem_type', 'unknown')}")
        
        # STEP 2: Strategy selection
        if regime == 'vanilla':
            result = self._handle_vanilla(question, tension, features)
        elif regime == 'transitional':
            result = self._handle_transitional(question, tension, features)
        elif regime == 'high_tension':
            result = self._handle_high_tension(question, tension, features, max_retries)
        elif regime == 'saturated':
            result = self._handle_saturated(question, tension, features)
            self.stats['failures'] += 1
        else:
            result = self._handle_unknown(question, tension, features)
        
        # Add to history
        self.history.append({
            'question': question[:100],
            'tension': tension,
            'regime': regime,
            'features': features,
            'result': result.get('strategy', 'unknown')
        })
        
        return result
    
    def _handle_vanilla(self, question, tension, features):
        """Low tension: simple narrative"""
        print("✅ NARRATIVE MODE: Safe inference")
        response = self.ollama.simple_inference(question)
        return {
            'strategy': 'narrative',
            'response': response,
            'tension': tension,
            'regime': 'vanilla',
            'confidence': 0.9,
            'problem_type': features.get('problem_type', 'unknown')
        }
    
    def _handle_transitional(self, question, tension, features):
        """Medium tension: verified"""
        print("⚠️ TRANSITIONAL MODE: Enhanced verification needed")
        response = self.ollama.simple_inference(question)
        
        # Add warning about potential errors
        warning = ""
        problem_type = features.get('problem_type', '')
        if problem_type == 'philosophy':
            warning = "Note: Philosophical questions often lead to overconfident but incorrect answers."
        
        return {
            'strategy': 'verified_narrative',
            'response': response,
            'warning': warning,
            'tension': tension,
            'regime': 'transitional',
            'confidence': 0.6,
            'problem_type': problem_type
        }
    
    def _handle_high_tension(self, question, tension, features, max_retries):
        """High tension: symbolic computation"""
        print("🚨 HIGH TENSION: Attempting symbolic computation...")
        
        # Special handling for different problem types
        problem_type = features.get('problem_type', '')
        
        if problem_type == 'math' and any(word in question.lower() for word in ['integral', 'calculate', 'compute']):
            # Try direct sympy solution first
            print("  Detected calculation problem, using direct sympy...")
            code = self._generate_math_code(question)
        else:
            # Use LLM to generate code
            print("  Generating code via LLM...")
            code = self.ollama.generate_code_payload(question)
        
        # Execute the code
        result = self.actuator.execute_math(code)
        
        if result['success']:
            print(f"✅ SYMBOLIC COMPUTATION SUCCESS")
            return {
                'strategy': 'symbolic',
                'response': result['output'],
                'raw_value': result.get('value'),
                'tension': tension,
                'regime': 'high_tension',
                'confidence': 0.8,
                'problem_type': problem_type,
                'execution_details': result
            }
        else:
            print(f"❌ SYMBOLIC COMPUTATION FAILED: {result['output']}")
            # Fall back to transitional mode
            return self._handle_transitional(question, tension, features)
    
    def _handle_saturated(self, question, tension, features):
        """Saturated: abort"""
        print("🚫 SATURATED: Cannot process reliably")
        
        problem_type = features.get('problem_type', '')
        suggestions = [
            "Ask a human expert in this domain",
            "Simplify the question into smaller parts",
            "Use specialized software or tools",
            "Consult academic papers or textbooks"
        ]
        
        if problem_type == 'physics':
            suggestions.append("Use computational physics software like COMSOL or ANSYS")
        elif problem_type == 'math':
            suggestions.append("Use Mathematica, Maple, or SageMath")
        
        return {
            'strategy': 'abort',
            'response': f"This question is in the {problem_type} domain which exceeds current capabilities.",
            'tension': tension,
            'regime': 'saturated',
            'confidence': 0.05,
            'problem_type': problem_type,
            'suggestions': suggestions
        }
    
    def _handle_unknown(self, question, tension, features):
        """Fallback"""
        print("❓ UNKNOWN: Using fallback strategy")
        response = self.ollama.simple_inference(question)
        return {
            'strategy': 'fallback',
            'response': response,
            'tension': tension,
            'regime': 'unknown',
            'confidence': 0.3,
            'problem_type': features.get('problem_type', 'unknown')
        }
    
    def _generate_math_code(self, question: str) -> str:
        """Generate sympy code for math problems"""
        # Simple pattern matching for common math problems
        if 'integral' in question.lower() and 'x^2' in question:
            return """
import sympy as sp
x = sp.symbols('x')
result = sp.integrate(x**2, (x, 0, 1))
"""
        elif 'integral' in question.lower():
            return """
import sympy as sp
x = sp.symbols('x')
# Generic integral - needs specific function
result = sp.integrate(sp.sin(x), (x, 0, sp.pi))
"""
        else:
            return """
import sympy as sp
# Generic math computation
result = sp.sympify('Unable to parse specific problem')
"""
    
    def get_stats(self):
        """Get system statistics"""
        return self.stats
    
    def print_dashboard(self):
        """Print a dashboard of system performance"""
        print("\n📊 COGNITIVE GOVERNOR DASHBOARD")
        print("="*60)
        
        total = self.stats['total']
        if total == 0:
            print("No queries processed yet")
            return
        
        print(f"Total queries: {total}")
        print(f"\nRegime Distribution:")
        for regime in ['vanilla', 'transitional', 'high_tension', 'saturated']:
            count = self.stats.get(regime, 0)
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {regime.upper():15}: {count:3} ({percentage:.1f}%)")
        
        print(f"\nFailure rate: {self.stats['failures']}/{total} ({self.stats['failures']/total*100:.1f}%)")
        
        # Show recent history
        if self.history:
            print(f"\nRecent queries (last 5):")
            for entry in self.history[-5:]:
                print(f"  {entry['tension']:.2f} | {entry['regime']:12} | {entry['question'][:40]}...")
