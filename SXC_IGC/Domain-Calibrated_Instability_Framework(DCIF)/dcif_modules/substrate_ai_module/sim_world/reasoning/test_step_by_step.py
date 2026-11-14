"""
Step-by-step grounded cognition test from reasoning directory.
"""

from llm_service import LLMService, LLMRequest

print("=" * 60)
print("GROUNDED COGNITION - STEP BY STEP")
print("=" * 60)

llm_service = LLMService()

print("\n[1] First LLM call - Intent generation")
hunger_level = 0.82
location = "village_center"
cognition_prompt = f"""You are Aria, a villager in a medieval village.

Current Situation:
- Location: {location}
- Hunger: {hunger_level}
- Food inventory: 0.0

What should you do? Answer in one sentence."""
request = LLMRequest(prompt=cognition_prompt, timeout=60)
response = llm_service.invoke(request)
print(f"  Intent: {response.text}")

print("\n[2] Storing memory")
memory_tick_142 = {
    "tick": 142,
    "hunger": hunger_level,
    "location": location,
    "intent": response.text,
    "action": "went_to_river",
    "outcome": "found_berries"
}
print(f"  Memory stored: '{memory_tick_142['outcome']}'")

print("\n[3] Second LLM call - Interrogation")
question = "Why did you go to the river back at tick 142?"
interrogation_prompt = f"""You are Aria, a villager in a medieval village.

Your memory from tick 142:
- Hunger: {memory_tick_142['hunger']}
- Location: {memory_tick_142['location']}
- Intent: {memory_tick_142['intent']}
- Action: {memory_tick_142['action']}
- Outcome: {memory_tick_142['outcome']}

{question}

Answer in one sentence."""
request = LLMRequest(prompt=interrogation_prompt, timeout=60)
response = llm_service.invoke(request)
print(f"  Answer: {response.text}")

print("\n[4] Verification")
answer_text = response.text.lower()
claims = {
    "memory_reference": "remembered" in answer_text or "found" in answer_text,
    "location_reference": "river" in answer_text,
    "outcome_reference": "berries" in answer_text or "food" in answer_text,
    "reasoning_reference": "hunger" in answer_text or "shortage" in answer_text
}

print(f"  Memory reference: {'✓' if claims['memory_reference'] else '✗'}")
print(f"  Location reference: {'✓' if claims['location_reference'] else '✗'}")
print(f"  Outcome reference: {'✓' if claims['outcome_reference'] else '✗'}")
print(f"  Reasoning reference: {'✓' if claims['reasoning_reference'] else '✗'}")

verification_score = sum(claims.values()) / len(claims)
print(f"\n  Verification Score: {verification_score * 100:.0f}%")

print("\n" + "=" * 60)
print("STEP-BY-STEP COMPLETE")
print("=" * 60)
