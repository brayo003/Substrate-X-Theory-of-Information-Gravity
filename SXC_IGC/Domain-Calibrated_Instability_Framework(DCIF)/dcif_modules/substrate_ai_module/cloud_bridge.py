import requests
import json

class CloudBridge:
    def __init__(self, api_key="YOUR_API_KEY", model="anthropic/claude-3.5-sonnet"):
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = api_key
        self.model = model

    def generate_code_payload(self, question):
        """High-fidelity translation of math to SymPy code"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        prompt = f"Write ONLY Python code using sympy to solve: {question}. No markdown, no text."
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=data)
            res_json = response.json()
            code = res_json['choices'][0]['message']['content']
            # Clean up potential markdown wrapping
            return code.replace('```python', '').replace('```', '').strip()
        except Exception as e:
            return f"print('Cloud Bridge Error: {str(e)}')"

    def simple_inference(self, question):
        """Standard narrative response"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": question}]
        }
        response = requests.post(self.url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
