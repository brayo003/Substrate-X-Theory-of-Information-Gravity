"""
Test sequential LLM calls with simple prompts.
"""

from llm_service import LLMService, LLMRequest

print("Testing sequential LLM calls...")
llm = LLMService()

print("\n[1] First call")
request1 = LLMRequest(prompt="Say hello", timeout=30)
response1 = llm.invoke(request1)
print(f"  Success: {response1.success}")
print(f"  Response: {response1.text}")

print("\n[2] Second call")
request2 = LLMRequest(prompt="Say goodbye", timeout=30)
response2 = llm.invoke(request2)
print(f"  Success: {response2.success}")
print(f"  Response: {response2.text}")

print("\n[3] Third call")
request3 = LLMRequest(prompt="Count to 3", timeout=30)
response3 = llm.invoke(request3)
print(f"  Success: {response3.success}")
print(f"  Response: {response3.text}")

print("\n✓ SEQUENTIAL CALL TEST COMPLETE")
