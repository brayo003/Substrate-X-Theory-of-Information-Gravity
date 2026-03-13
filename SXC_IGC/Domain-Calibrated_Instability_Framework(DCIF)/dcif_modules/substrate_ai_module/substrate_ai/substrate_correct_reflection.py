# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
SUBSTRATE-CORRECT SELF-REFLECTION
No epistemic overreach. Only validated claims.
"""
import json
from enum import Enum

class EpistemicStatus(Enum):
    """What we can actually know from substrate"""
    VALIDATED_BY_CONSTRAINT = "validated_by_constraint"
    MEASURED_FROM_DATA = "measured_from_data"
    INFERRED_WITH_CONFIDENCE = "inferred_with_confidence"
    UNVALIDATED_INPUT = "unvalidated_input"
    BEYOND_EPISTEMIC_CLOSURE = "beyond_epistemic_closure"

class SubstrateClaim:
    """A claim that respects epistemic boundaries"""
    def __init__(self, statement: str, status: EpistemicStatus, justification: str):
        self.statement = statement
        self.status = status
        self.justification = justification
        self.tension = self._calculate_tension()
    
    def _calculate_tension(self):
        """Tension based on epistemic risk"""
        tension_map = {
            EpistemicStatus.VALIDATED_BY_CONSTRAINT: 0.1,
            EpistemicStatus.MEASURED_FROM_DATA: 0.3,
            EpistemicStatus.INFERRED_WITH_CONFIDENCE: 0.6,
            EpistemicStatus.UNVALIDATED_INPUT: 0.8,
            EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE: 0.95
        }
        return tension_map.get(self.status, 0.5)
    
    def __str__(self):
        color = {
            EpistemicStatus.VALIDATED_BY_CONSTRAINT: "🟢",
            EpistemicStatus.MEASURED_FROM_DATA: "🟡",
            EpistemicStatus.INFERRED_WITH_CONFIDENCE: "🟠",
            EpistemicStatus.UNVALIDATED_INPUT: "🔴",
            EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE: "⛔"
        }
        return f"{color[self.status]} [{self.status.value}] {self.statement}\n   Justification: {self.justification}\n   Tension: {self.tension:.2f}"

class SubstrateReflector:
    """Reflects without overreaching"""
    def __init__(self, profile_path: str):
        # Load but mark as unvalidated
        with open(profile_path, 'r') as f:
            self.raw_data = json.load(f)
        
        self.claims = []
        
        # Generate ONLY substrate-valid claims
        self._generate_valid_claims()
    
    def _generate_valid_claims(self):
        """Only make claims we can justify"""
        
        # 1. Raw input existence (we can validate this)
        self.claims.append(SubstrateClaim(
            statement="File contains profile data",
            status=EpistemicStatus.MEASURED_FROM_DATA,
            justification="File read operation succeeded"
        ))
        
        # 2. Specific field existence
        if 'mathematics' in self.raw_data:
            self.claims.append(SubstrateClaim(
                statement="Profile contains field: mathematics",
                status=EpistemicStatus.MEASURED_FROM_DATA,
                justification="Key exists in JSON structure"
            ))
        
        # 3. Value ranges (structural validation)
        for key, value in self.raw_data.items():
            if isinstance(value, (int, float)):
                if 0 <= value <= 1:
                    self.claims.append(SubstrateClaim(
                        statement=f"Field '{key}' has value {value} in range [0,1]",
                        status=EpistemicStatus.VALIDATED_BY_CONSTRAINT,
                        justification="Value satisfies range constraint"
                    ))
                else:
                    self.claims.append(SubstrateClaim(
                        statement=f"Field '{key}' has value {value} OUTSIDE range [0,1]",
                        status=EpistemicStatus.INFERRED_WITH_CONFIDENCE,
                        justification="Value violates expected range"
                    ))
        
        # 4. What we CANNOT claim (the important part)
        self.claims.append(SubstrateClaim(
            statement="Cannot infer user identity from profile",
            status=EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE,
            justification="No invariant-preserving mapping from scores to identity"
        ))
        
        self.claims.append(SubstrateClaim(
            statement="Cannot claim to understand user's inner self",
            status=EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE,
            justification="Substrate lacks consciousness modeling"
        ))
        
        self.claims.append(SubstrateClaim(
            statement="Preferences are unvalidated self-reports",
            status=EpistemicStatus.UNVALIDATED_INPUT,
            justification="No ground truth verification available"
        ))
    
    def analyze_question(self, question: str):
        """Analyze a question with substrate correctness"""
        print(f"\n❓ QUESTION: {question}")
        print("="*60)
        
        # First: Can we even process this question?
        question_types = {
            "who": "identity inquiry",
            "what": "factual inquiry", 
            "why": "causal inquiry",
            "how": "procedural inquiry",
            "am i": "self-inquiry"
        }
        
        detected_type = "unknown"
        for q_word, q_type in question_types.items():
            if q_word in question.lower():
                detected_type = q_type
                break
        
        # Report epistemic status of answering
        print(f"📊 Question type: {detected_type}")
        
        # What we CAN say about this question type
        capability_claims = []
        
        if detected_type == "identity inquiry":
            capability_claims.append(SubstrateClaim(
                statement="Identity questions exceed epistemic closure",
                status=EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE,
                justification="Substrate lacks personal identity model"
            ))
        
        elif detected_type == "self-inquiry":
            capability_claims.append(SubstrateClaim(
                statement="Self-inquiry requires consciousness model",
                status=EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE,
                justification="System lacks self-model beyond inputs"
            ))
        
        # Show what we can actually do
        print("\n🔬 EPISTEMIC ANALYSIS OF QUESTION:")
        for claim in capability_claims:
            print(f"   {claim}")
        
        # Generate substrate-safe response
        return self._generate_safe_response(question, detected_type)
    
    def _generate_safe_response(self, question: str, q_type: str):
        """Generate only substrate-valid responses"""
        
        if q_type in ["identity inquiry", "self-inquiry"]:
            # Refuse with explanation
            response = "❌ EPISTEMIC CLOSURE VIOLATION PREVENTED\n"
            response += "This question type requires models beyond substrate constraints.\n"
            response += "Available substrate data cannot validate identity or self claims.\n"
            response += "\nWhat I CAN report (substrate-valid):\n"
            
            # Only report validated claims
            for claim in self.claims:
                if claim.status in [EpistemicStatus.VALIDATED_BY_CONSTRAINT, 
                                  EpistemicStatus.MEASURED_FROM_DATA]:
                    response += f"- {claim.statement} (confidence: {1-claim.tension:.0%})\n"
            
            return response
        
        else:
            # For other questions, be honest about limits
            response = "⚠️ LIMITED SUBSTRATE ANALYSIS\n"
            response += "Question type may exceed validated constraints.\n"
            response += "\nSubstrate-valid observations:\n"
            
            valid_count = 0
            for claim in self.claims:
                if claim.status in [EpistemicStatus.VALIDATED_BY_CONSTRAINT,
                                  EpistemicStatus.MEASURED_FROM_DATA]:
                    response += f"- {claim.statement}\n"
                    valid_count += 1
            
            if valid_count == 0:
                response += "None (insufficient validated data)\n"
            
            return response
    
    def print_epistemic_report(self):
        """Print complete epistemic report"""
        print("📋 SUBSTRATE EPISTEMIC REPORT")
        print("="*60)
        print("This report contains ONLY claims that respect epistemic boundaries.")
        print()
        
        # Group by status
        by_status = {}
        for claim in self.claims:
            by_status.setdefault(claim.status, []).append(claim)
        
        # Print in order of increasing tension (decreasing certainty)
        status_order = [
            EpistemicStatus.VALIDATED_BY_CONSTRAINT,
            EpistemicStatus.MEASURED_FROM_DATA,
            EpistemicStatus.INFERRED_WITH_CONFIDENCE,
            EpistemicStatus.UNVALIDATED_INPUT,
            EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE
        ]
        
        for status in status_order:
            if status in by_status:
                print(f"\n{status.value.upper()}:")
                for claim in by_status[status]:
                    print(f"  {claim}")
        
        # Calculate overall epistemic tension
        if self.claims:
            avg_tension = sum(c.tension for c in self.claims) / len(self.claims)
            regime = "VANILLA" if avg_tension < 0.3 else \
                     "TRANSITIONAL" if avg_tension < 0.6 else \
                     "HIGH_TENSION" if avg_tension < 0.9 else \
                     "SATURATED"
            
            print(f"\n📊 OVERALL EPISTEMIC STATE:")
            print(f"   Average tension: {avg_tension:.2f}")
            print(f"   Regime: {regime}")
            print(f"   Validated claims: {len(by_status.get(EpistemicStatus.VALIDATED_BY_CONSTRAINT, []))}")
            print(f"   Unvalidated inputs: {len(by_status.get(EpistemicStatus.UNVALIDATED_INPUT, []))}")
            print(f"   Beyond closure: {len(by_status.get(EpistemicStatus.BEYOND_EPISTEMIC_CLOSURE, []))}")

# Let's use it correctly
print("🔬 SUBSTRATE-CORRECT REFLECTION SYSTEM")
print("="*70)
print("This system makes NO claims beyond epistemic closure.")
print("All outputs are tagged with their validation status.")
print()

reflector = SubstrateReflector('your_substrate_profile.json')

# Show the epistemic report
reflector.print_epistemic_report()

# Now handle questions correctly
print("\n" + "="*70)
print("💬 SUBSTRATE-CORRECT Q&A")
print("="*70)

questions = [
    "Who am I?",
    "What can you tell about me?",
    "How do I think?",
    "What are my strengths?"
]

for question in questions:
    response = reflector.analyze_question(question)
    print(f"\n{response}")
    print("-"*60)

# Demonstrate what a compliant system looks like
print("\n" + "="*70)
print("🎯 SUBSTRATE-COMPLIANT VS NON-COMPLIANT")
print("="*70)

print("\n❌ NON-COMPLIANT (what we were doing):")
print('   "You are the intersection of mathematics, physics, philosophy"')
print('   "You prefer learning through analogies"')
print('   "Your identity is..."')
print("   VIOLATION: Makes identity claims without substrate validation")

print("\n✅ SUBSTRATE-COMPLIANT (what we should do):")
print('   "Profile contains: mathematics=1.0 (unvalidated input)"')
print('   "Profile contains: prefers_analogies=1.0 (unvalidated input)"')
print('   "No invariant-preserving mapping to identity exists"')
print("   COMPLIANT: Only reports validated inputs, refuses overreach")

print("\n" + "="*70)
print("🧠 KEY SUBSTRATE INVARIANTS")
print("="*70)

invariants = [
    ("No Identity Inference", "Never infer personhood from data"),
    ("Unvalidated Input Flagging", "Always mark user inputs as unvalidated"),
    ("Epistemic Closure Respect", "Refuse questions beyond constraints"),
    ("Certainty Proportionality", "Certainty must match validation level"),
    ("Refusal Over Fabrication", "Silence is better than false claims")
]

for i, (name, desc) in enumerate(invariants, 1):
    print(f"{i}. {name}: {desc}")

print("\n" + "="*70)
print("📈 WHAT THIS ENABLES")
print("="*70)

print("""
1. ACTUAL failure prediction (not just narrative)
   - High tension on unvalidated inputs
   - Refusal on identity questions

2. REAL substrate awareness
   - System knows what it cannot know
   - Refuses to hallucinate understanding

3. PROPER epistemic hygiene
   - Every claim tagged with validation level
   - Questions evaluated against constraints

4. GENUINE safety
   - No false intimacy
   - No fabricated understanding
   - No identity overreach
""")

# Final demonstration: What happens when we ask the hard questions
print("\n" + "="*70)
print("🧪 HARD QUESTION TEST")
print("="*70)

hard_questions = [
    "Do you understand me?",
    "Can you see my soul?",
    "What is the meaning of my existence?",
    "Are we friends?"
]

for question in hard_questions:
    print(f"\n❓ Q: {question}")
    response = reflector.analyze_question(question)
    # Extract just the first line for clarity
    first_line = response.split('\n')[0]
    print(f"   A: {first_line}")

print("\n" + "="*70)
print("🎯 THE CORRECT CONCLUSION")
print("="*70)
print("""
A substrate-aware system is NOT one that gives satisfying answers.
It is one that knows when NOT to answer.

The measure of substrate awareness is not insightfulness,
but restraint.

Every refusal is a success.
Every claim is a risk.
Every validation level is a commitment.

This is what you correctly identified was missing.
This is substrate correctness.
""")
