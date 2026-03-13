# V12_SYNC_VERIFIED: 2026-03-13
import requests
import json

class OllamaBridge:
    def __init__(self):
        self.url = "http://127.0.0.1:11434/api/generate"
        self.model = "tinyllama:latest"

    def simple_inference(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get('response', 'Error: No response key')
            else:
                return f"Error: Status {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_code_payload(self, prompt):
        enhanced_prompt = f"Provide a deterministic code solution for: {prompt}"
        return {"response": self.simple_inference(enhanced_prompt)}
