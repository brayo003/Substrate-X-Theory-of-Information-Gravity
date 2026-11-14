"""
Test with progressively longer prompts to find the threshold.
"""

from llm_service import LLMService, LLMRequest

print("Testing prompt length threshold...")
llm = LLMService()

print("\n[1] Short prompt (50 chars)")
prompt1 = "You are Aria. What should you do? Say hello."
request1 = LLMRequest(prompt=prompt1, timeout=60)
response1 = llm.invoke(request1)
print(f"  Success: {response1.success}")
print(f"  Response: {response1.text[:50]}")

print("\n[2] Medium prompt (100 chars)")
prompt2 = "You are Aria, a villager in a medieval village. Your hunger is 0.82. What should you do?"
request2 = LLMRequest(prompt=prompt2, timeout=60)
response2 = llm.invoke(request2)
print(f"  Success: {response2.success}")
print(f"  Response: {response2.text[:50]}")

print("\n[3] Longer prompt (200 chars)")
prompt3 = """You are Aria, a villager in a medieval village. Your hunger is 0.82 and food inventory is 0.0. You are at village_center. What should you do?"""
request3 = LLMRequest(prompt=prompt3, timeout=60)
response3 = llm.invoke(request3)
print(f"  Success: {response3.success}")
print(f"  Response: {response3.text[:50]}")

print("\n✓ PROMPT LENGTH TEST COMPLETE")
