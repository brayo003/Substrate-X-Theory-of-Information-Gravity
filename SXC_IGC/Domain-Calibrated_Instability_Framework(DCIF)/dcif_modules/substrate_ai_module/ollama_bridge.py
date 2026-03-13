import requests
import json

class OllamaBridge:
    def __init__(self, model="gemma2:2b"):
        self.url = "http://localhost:11434/api/generate"
        self.model = model

    def generate_code_payload(self, question):
        prompt = f"""
        Question: {question}
        Task: Provide ONLY the Python code using sympy to solve this. 
        No explanation. No markdown. Just code.
        Example:
        from sympy import symbols, solve
        x = symbols('x')
        print(solve(x**2 - 4, x))
        """
        data = {"model": self.model, "prompt": prompt, "stream": False}
        response = requests.post(self.url, json=data)
        return response.json().get('response', '').strip().replace('```python', '').replace('```', '')

