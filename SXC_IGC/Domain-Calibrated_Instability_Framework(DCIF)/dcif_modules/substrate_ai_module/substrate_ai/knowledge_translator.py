#!/usr/bin/env python3
"""
KNOWLEDGE TRANSLATOR - Proof of Concept
Using our substrate system to translate knowledge
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.problem_analyzer import ProblemAnalyzer
from components.substrate_core import SubstrateDynamics

class KnowledgeTranslator:
    def __init__(self):
        self.analyzer = ProblemAnalyzer()
        self.substrate = SubstrateDynamics()
        
        # Mock user substrate profile
        self.user_profiles = {
            'beginner': {
                'math_skill': 0.2,
                'science_background': 0.1,
                'abstract_thinking': 0.15
            },
            'intermediate': {
                'math_skill': 0.5,
                'science_background': 0.4,
                'abstract_thinking': 0.45
            },
            'expert': {
                'math_skill': 0.8,
                'science_background': 0.75,
                'abstract_thinking': 0.8
            }
        }
    
    def translate_knowledge(self, topic: str, user_level: str = 'intermediate'):
        """Translate a topic to user's comprehension level"""
        print(f"\n🎯 TRANSLATING: {topic}")
        print(f"👤 For: {user_level} user")
        
        # Analyze topic difficulty
        features = self.analyzer.extract_features(topic)
        universal_tension = self.analyzer.predict_tension_from_features(features)
        problem_type = features.get('problem_type', 'general')
        
        print(f"\n📊 TOPIC ANALYSIS:")
        print(f"   Universal tension: {universal_tension:.2f}")
        print(f"   Problem type: {problem_type}")
        
        # Get user profile
        user_profile = self.user_profiles[user_level]
        
        # Adjust tension for this user
        if problem_type == 'math':
            user_skill = user_profile['math_skill']
        elif problem_type == 'physics' or problem_type == 'science':
            user_skill = user_profile['science_background']
        else:
            user_skill = user_profile['abstract_thinking']
        
        # Simple adjustment: higher skill = lower effective tension
        adjusted_tension = max(0.1, universal_tension - user_skill)
        regime = self.substrate.determine_regime(adjusted_tension)
        
        print(f"\n👤 USER ADJUSTMENT:")
        print(f"   User skill in {problem_type}: {user_skill:.2f}")
        print(f"   Adjusted tension: {adjusted_tension:.2f}")
        print(f"   Regime: {regime.upper()}")
        
        # Generate appropriate explanation
        explanation = self._generate_explanation(topic, regime, user_level)
        
        return {
            'topic': topic,
            'universal_tension': universal_tension,
            'user_level': user_level,
            'adjusted_tension': adjusted_tension,
            'regime': regime,
            'explanation': explanation
        }
    
    def _generate_explanation(self, topic: str, regime: str, user_level: str):
        """Generate explanation at appropriate level"""
        explanations = {
            'vanilla': {
                'math': f"{topic} is like counting things. Easy and fun!",
                'physics': f"{topic} is how things move around. Like balls rolling!",
                'general': f"{topic} is interesting! Here's a simple way to think about it..."
            },
            'transitional': {
                'math': f"{topic} involves calculations. Let me walk you through step by step.",
                'physics': f"{topic} deals with forces and motion. Here's how it works in practice.",
                'general': f"{topic} has some complexity. Let me break it down for you."
            },
            'high_tension': {
                'math': f"{topic} requires advanced mathematical thinking. I'll use analogies to help.",
                'physics': f"{topic} involves complex principles. Let's build up from basics.",
                'general': f"{topic} is quite complex. I'll simplify the key concepts."
            },
            'saturated': {
                'math': f"{topic} is extremely advanced. Let's start with foundational concepts first.",
                'physics': f"{topic} pushes the boundaries of current understanding. Here's what we know at a basic level.",
                'general': f"{topic} is beyond typical comprehension. I'll give you a high-level overview."
            }
        }
        
        # For demo, just use general
        return explanations[regime]['general']

# Test it
translator = KnowledgeTranslator()

test_topics = [
    "Quantum entanglement",
    "Calculus derivatives",
    "Blockchain technology",
    "Photosynthesis process"
]

print("🧪 KNOWLEDGE TRANSLATION DEMO")
print("="*60)

for topic in test_topics:
    for user_level in ['beginner', 'intermediate', 'expert']:
        result = translator.translate_knowledge(topic, user_level)
        print(f"\n💡 EXPLANATION for {user_level}:")
        print(f"   {result['explanation']}")
        print("-" * 60)
