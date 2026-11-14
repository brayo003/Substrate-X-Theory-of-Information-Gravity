"""
Test very simple LLM call from reasoning directory.
"""

from llm_service import LLMService, LLMRequest

print("Testing simple LLM call...")
llm = LLMService()
request = LLMRequest(prompt="Say hello", timeout=30)
response = llm.invoke(request)
print(f"Success: {response.success}")
print(f"Response: {response.text}")
