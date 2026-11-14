"""
Test sequential medium prompts with fixed LLM service.
"""

from llm_service import LLMService, LLMRequest

print("Testing sequential medium prompts with fixed service...")
llm = LLMService()

print("\n[1] First call with medium prompt")
prompt1 = """You are Aria, a villager in a medieval village.

Current Situation:
- Location: village_center
- Hunger: 0.82
- Food inventory: 0.0

What should you do? Answer in one sentence."""
request1 = LLMRequest(prompt=prompt1, timeout=60)
response1 = llm.invoke(request1)
print(f"  Success: {response1.success}")
print(f"  Response: {response1.text}")

print("\n[2] Second call with medium prompt")
prompt2 = """You are Aria, a villager in a medieval village.

Your memory from tick 142:
- Hunger: 0.82
- Location: village_center
- Action: went_to_river
- Outcome: found_berries

Why did you go to the river? Answer in one sentence."""
request2 = LLMRequest(prompt=prompt2, timeout=60)
response2 = llm.invoke(request2)
print(f"  Success: {response2.success}")
print(f"  Response: {response2.text}")

print("\n[3] Third call with medium prompt")
prompt3 = """You are Aria, a villager in a medieval village.

Your memory from tick 300:
- Action: visited_market
- Outcome: bought_food

Why did you visit the market? Answer in one sentence."""
request3 = LLMRequest(prompt=prompt3, timeout=60)
response3 = llm.invoke(request3)
print(f"  Success: {response3.success}")
print(f"  Response: {response3.text}")

print("\n✓ FIXED SERVICE SEQUENTIAL TEST COMPLETE")
