# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
from substrate_core import SubstrateDynamics
from problem_analyzer import ProblemAnalyzer
from actuator import PythonActuator
from ollama_bridge import OllamaBridge

class CognitiveGovernor:
    def __init__(self):
        self.substrate = SubstrateDynamics()
        self.analyzer = ProblemAnalyzer()
        self.actuator = PythonActuator()
        self.bridge = OllamaBridge()

    def process_question(self, question, max_retries=3):
        f = self.analyzer.extract_features(question)
        t = self.analyzer.predict_tension_from_features(f)
        regime = self.substrate.determine_regime(t)
        
        print(f"\n📊 TENSION: {t:.2f} | REGIME: {regime.upper()}")
        
        if regime == 'formal_required':
            current_prompt = question
            for attempt in range(max_retries):
                print(f"🚨 ATTEMPT {attempt + 1}: Synthesizing Payload...")
                code = self.bridge.generate_code_payload(current_prompt)
                res = self.actuator.execute_math(code)
                
                if res["success"]:
                    print(f"✅ VERIFIED RESULT: {res['output']}")
                    return res["output"]
                else:
                    print(f"❌ EXECUTION FAILED. Sending error logs back to Bridge...")
                    # The "Cognitive Loop": Adding the error to the prompt
                    current_prompt = f"{question}\n\nYour previous code failed with: {res['output']}. Fix it."
            
            return "FAIL: Max retries exceeded."
        
        return "Narrative mode: Inference safe locally."

if __name__ == "__main__":
    gov = CognitiveGovernor()
    gov.process_question("Calculate the integral of x**2 from 0 to 1.")
