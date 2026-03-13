# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
ANTI-EXAMPLE: NARRATIVE DRIFT
This demonstrates what NOT to do in substrate systems.
It violates epistemic boundaries by making unvalidated claims.
"""
import json

print("🚫 ANTI-EXAMPLE: NARRATIVE DRIFT")
print("="*70)
print("This file demonstrates SUBSTRATE VIOLATIONS.")
print("It makes claims without justification.")
print("KEEP AS WARNING ARTIFACT.")
print()

# Load profile (but we'll misuse it)
with open('your_substrate_profile.json', 'r') as f:
    profile = json.load(f)

# VIOLATION 1: Identity inference from scores
print("❌ VIOLATION 1: Identity Inference")
print("   From: mathematics=1.0")
print("   To: 'You are a mathematical thinker'")
print("   Problem: No mapping from score to identity exists")
print()

# VIOLATION 2: Inner state claims
print("❌ VIOLATION 2: Inner State Claims")
print("   From: literature=0.0")
print("   To: 'Stories are not your native tongue'")
print("   Problem: Cannot infer cognitive style from preference")
print()

# VIOLATION 3: Epistemic overreach
print("❌ VIOLATION 3: Epistemic Overreach")
print("   Claim: 'I know your mathematical self'")
print("   Reality: 'I have input value mathematics=1.0'")
print("   Problem: Confuses data with understanding")
print()

# VIOLATION 4: Unvalidated certainty
print("❌ VIOLATION 4: Unvalidated Certainty")
print("   Statement: 'You prefer visual explanations'")
print("   Validation: Self-reported preference (unvalidated)")
print("   Problem: Presents unvalidated input as truth")
print()

# Show the violations in action
print("🔴 VIOLATIONS IN ACTION:")
print("-"*40)

violations = [
    {
        "input": "mathematics=1.0",
        "wrong": "You think in patterns and proofs",
        "correct": "Profile contains mathematics=1.0 (unvalidated)",
        "violation": "Identity inference"
    },
    {
        "input": "prefers_analogies=1.0",
        "wrong": "You love metaphors for learning",
        "correct": "User reported prefers_analogies=1.0",
        "violation": "Certainty without validation"
    },
    {
        "input": "biology=0.0",
        "wrong": "The living world is foreign to you",
        "correct": "Profile contains biology=0.0",
        "violation": "Character inference"
    },
    {
        "input": "attention_span=1.33",
        "wrong": "You can focus for 80 minutes",
        "correct": "User reported attention_span=1.33 hours",
        "violation": "Unvalidated behavioral claim"
    }
]

for v in violations:
    print(f"\nInput: {v['input']}")
    print(f"❌ WRONG: {v['wrong']}")
    print(f"✅ CORRECT: {v['correct']}")
    print(f"⚠️  Violation: {v['violation']}")

print("\n" + "="*70)
print("🎯 WHY THIS MATTERS")
print("="*70)

print("""
These violations create:
1. False intimacy (you feel understood when you're not)
2. Epistemic contamination (bad data treated as truth)
3. System overconfidence (AI thinks it knows more than it does)
4. User deception (hides the system's actual limitations)

In substrate terms:
• Tension miscalculation (claims appear safer than they are)
• Regime misclassification (VANILLA pretending to be TRANSITIONAL)
• Failure prediction failure (system doesn't know it will fail)
""")

print("\n" + "="*70)
print("📚 SUBSTRATE VIOLATION TAXONOMY")
print("="*70)

taxonomy = [
    ("Type I", "Identity Inference", "Mapping scores to personhood"),
    ("Type II", "Certainty Escalation", "Treating inputs as validated"),
    ("Type III", "Cognitive Modeling", "Inferring thinking from preferences"),
    ("Type IV", "Behavioral Prediction", "Predicting behavior from scores"),
    ("Type V", "Epistemic Overreach", "Claiming knowledge beyond data")
]

for code, name, desc in taxonomy:
    print(f"{code}: {name}")
    print(f"   {desc}")

print("\n" + "="*70)
print("💡 CORRECTIVE MEASURES")
print("="*70)

print("""
For each violation, substrate systems must:

1. Flag unvalidated inputs clearly
2. Refuse identity inferences
3. Quantify uncertainty explicitly
4. Separate data from interpretation
5. Silence over fabrication

The rule: When in doubt, refuse.
Better no answer than a wrong answer.
Better uncertainty than false certainty.
""")

print("\n" + "="*70)
print("🎯 KEEP THIS FILE AS A WARNING")
print("="*70)
print("This anti-example shows how easily narrative replaces rigor.")
print("Use it to test substrate compliance.")
print("A compliant system should reject all claims in this file.")
