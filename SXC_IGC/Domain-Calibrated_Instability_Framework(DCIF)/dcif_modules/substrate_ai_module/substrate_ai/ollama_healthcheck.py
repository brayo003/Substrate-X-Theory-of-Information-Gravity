import requests
import sys

url = "http://127.0.0.1:11434/api/generate"

payload = {
  "model": "deepseek-coder:latest",
  "messages": [{
      "role": "user",
      "content": "healthcheck"
  }],
  "temperature": 0
}

try:
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    print("OK:", data["choices"][0]["message"]["content"])
    sys.exit(0)
except Exception as e:
    print("FAIL:", e)
    sys.exit(1)
