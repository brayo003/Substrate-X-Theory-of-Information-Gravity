# V12_SYNC_VERIFIED: 2026-03-13
from components.ollama_bridge import OllamaBridge
from components.sxc_omega_v12 import SXCOmegaEngine
import time

class CognitiveGovernor:
    def __init__(self, **kwargs):
        # Maps to your verified Gemma:2b substrate
        self.bridge = OllamaBridge()
        self.v12 = SXCOmegaEngine()
        self.mode = kwargs.get("mode", "local")

    def handle_task(self, user_input):
        # 1. Signal acquisition from Gemma
        raw_response = self.bridge.simple_inference(user_input)
        
        # 2. Logic Audit via SXC-V12
        signal = len(raw_response.split())
        tension, phase = self.v12.step(signal)
        
        print(f"\n [SXC-V12] T_SYS: {tension:.4f} | PHASE: {phase}")

        if phase == "FIREWALL":
            print("🚨 FIREWALL ACTIVE: Switching to symbolic actuator.")
            return self.bridge.generate_code_payload(user_input)
        
        return {"response": raw_response, "tension": tension, "strategy": phase}

    def process_question(self, query):
        # Wrapper to match the call in run_system.py
        return self.handle_task(query)

if __name__ == "__main__":
    gov = CognitiveGovernor()
    print(gov.handle_task("Identify the logic error in a check-then-act race condition."))
