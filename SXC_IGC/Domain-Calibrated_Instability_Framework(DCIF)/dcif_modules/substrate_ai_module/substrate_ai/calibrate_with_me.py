#!/usr/bin/env python3
"""
CALIBRATE SUBSTRATE WITH YOU - Right now!
"""
import json
import os

def create_your_substrate_profile():
    """Create YOUR personal substrate profile"""
    print("🎯 LET'S CALIBRATE YOUR SUBSTRATE PROFILE")
    print("="*60)
    print("I'll ask about your knowledge levels, then build YOUR AI translator")
    print()
    
    # Your knowledge levels (0-1 scale)
    print("📚 Rate your knowledge level (0 = beginner, 0.5 = intermediate, 1 = expert):")
    
    your_profile = {}
    
    categories = [
        ("mathematics", "How comfortable are you with math?"),
        ("physics", "How much physics do you understand?"),
        ("computer_science", "Your programming/CS knowledge?"),
        ("biology", "Understanding of life sciences?"),
        ("chemistry", "Chemistry knowledge?"),
        ("philosophy", "Philosophical thinking ability?"),
        ("economics", "Understanding of economics?"),
        ("art_history", "Knowledge of art and history?"),
        ("literature", "Literature and writing skills?"),
        ("psychology", "Understanding of human psychology?"),
    ]
    
    for category, question in categories:
        while True:
            try:
                rating = float(input(f"\n{question}\n0-1 scale: "))
                if 0 <= rating <= 1:
                    your_profile[category] = rating
                    print(f"✅ {category}: {rating:.2f}")
                    break
                else:
                    print("Please enter 0-1")
            except:
                print("Please enter a number")
    
    # Learning preferences
    print("\n🎓 LEARNING PREFERENCES:")
    preferences = {}
    
    pref_questions = [
        ("prefers_visual", "Do you prefer visual explanations? (0=no, 1=yes)"),
        ("prefers_examples", "Do you learn better with examples? (0=no, 1=yes)"),
        ("prefers_analogies", "Do analogies help you understand? (0=no, 1=yes)"),
        ("prefers_technical", "Do you like technical details? (0=no, 1=yes)"),
        ("attention_span", "Typical attention span in minutes (5-120): "),
    ]
    
    for pref, question in pref_questions:
        while True:
            try:
                if "minutes" in question:
                    value = float(input(question))
                    if 5 <= value <= 120:
                        preferences[pref] = value / 60  # Convert to hours
                        break
                else:
                    value = float(input(question))
                    if 0 <= value <= 1:
                        preferences[pref] = value
                        break
            except:
                print("Please enter a valid number")
    
    your_profile['preferences'] = preferences
    
    # Save your profile
    with open('your_substrate_profile.json', 'w') as f:
        json.dump(your_profile, f, indent=2)
    
    print(f"\n🎉 YOUR SUBSTRATE PROFILE SAVED!")
    print(f"📁 File: your_substrate_profile.json")
    
    # Show summary
    print(f"\n📊 YOUR PROFILE SUMMARY:")
    print("-" * 40)
    
    # Sort by skill level
    sorted_skills = sorted(your_profile.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
    
    for category, value in sorted_skills:
        if category != 'preferences':
            level = "Beginner" if value < 0.3 else "Intermediate" if value < 0.7 else "Expert"
            print(f"{category:20}: {value:.2f} ({level})")
    
    return your_profile

def build_your_translator():
    """Build a translator specifically for YOU"""
    print(f"\n{'='*60}")
    print("🔧 BUILDING YOUR PERSONAL KNOWLEDGE TRANSLATOR")
    print("="*60)
    
    # Load your profile
    if os.path.exists('your_substrate_profile.json'):
        with open('your_substrate_profile.json', 'r') as f:
            your_profile = json.load(f)
    else:
        print("No profile found. Creating one...")
        your_profile = create_your_substrate_profile()
    
    # Topic database with REAL tension scores
    topic_database = {
        # Science
        "quantum entanglement": {"tension": 0.92, "category": "physics"},
        "calculus derivatives": {"tension": 0.65, "category": "mathematics"},
        "blockchain technology": {"tension": 0.70, "category": "computer_science"},
        "photosynthesis process": {"tension": 0.45, "category": "biology"},
        "general relativity": {"tension": 0.88, "category": "physics"},
        "machine learning": {"tension": 0.75, "category": "computer_science"},
        "quantum computing": {"tension": 0.95, "category": "physics"},
        "neural networks": {"tension": 0.72, "category": "computer_science"},
        "string theory": {"tension": 0.98, "category": "physics"},
        "cryptography": {"tension": 0.68, "category": "computer_science"},
        
        # Humanities
        "existentialism": {"tension": 0.62, "category": "philosophy"},
        "postmodernism": {"tension": 0.78, "category": "philosophy"},
        "renaissance art": {"tension": 0.40, "category": "art_history"},
        "shakespeare": {"tension": 0.55, "category": "literature"},
        "behavioral economics": {"tension": 0.60, "category": "economics"},
        "cognitive psychology": {"tension": 0.58, "category": "psychology"},
        
        # Mixed
        "artificial intelligence ethics": {"tension": 0.70, "category": "philosophy"},
        "climate change science": {"tension": 0.52, "category": "science"},
        "vaccine technology": {"tension": 0.48, "category": "biology"},
    }
    
    # Translation strategies based on YOUR preferences
    translation_strategies = {
        "visual": ["diagram", "visualization", "chart", "graphic"],
        "examples": ["for example", "consider this case", "imagine", "scenario"],
        "analogies": ["it's like", "similar to", "analogous to", "think of it as"],
        "technical": ["technically", "precisely", "mathematically", "formally"]
    }
    
    class YourPersonalTranslator:
        def __init__(self, profile, topics, strategies):
            self.profile = profile
            self.topics = topics
            self.strategies = strategies
            
        def translate_for_you(self, topic):
            """Translate a topic specifically for YOU"""
            print(f"\n🎯 TRANSLATING FOR YOU: {topic}")
            print("-" * 50)
            
            # Get topic info
            topic_info = self.topics.get(topic.lower(), {"tension": 0.5, "category": "general"})
            universal_tension = topic_info["tension"]
            category = topic_info["category"]
            
            print(f"📊 Topic Analysis:")
            print(f"   Universal tension: {universal_tension:.2f}")
            print(f"   Category: {category}")
            
            # Get YOUR skill in this category
            your_skill = self.profile.get(category, 0.5)
            print(f"   Your skill in {category}: {your_skill:.2f}")
            
            # Calculate adjusted tension for YOU
            # Higher skill = lower effective tension
            skill_adjustment = your_skill * 0.5  # Skill reduces tension by up to 50%
            adjusted_tension = max(0.1, universal_tension - skill_adjustment)
            
            # Determine regime
            if adjusted_tension < 0.3:
                regime = "vanilla"
            elif adjusted_tension < 0.6:
                regime = "transitional"
            elif adjusted_tension < 0.9:
                regime = "high_tension"
            else:
                regime = "saturated"
            
            print(f"\n👤 Adjusted for YOU:")
            print(f"   Adjusted tension: {adjusted_tension:.2f}")
            print(f"   Regime: {regime.upper()}")
            
            # Generate explanation using YOUR preferences
            explanation = self._generate_explanation(topic, regime, category)
            
            print(f"\n💡 EXPLANATION TAILORED FOR YOU:")
            print(f"   {explanation}")
            
            return {
                "topic": topic,
                "universal_tension": universal_tension,
                "your_skill": your_skill,
                "adjusted_tension": adjusted_tension,
                "regime": regime,
                "explanation": explanation
            }
        
        def _generate_explanation(self, topic, regime, category):
            """Generate explanation using YOUR preferences"""
            prefs = self.profile.get('preferences', {})
            
            # Base explanation based on regime
            base_explanations = {
                "vanilla": [
                    f"{topic} is actually quite straightforward!",
                    f"Let me give you a clear explanation of {topic}.",
                    f"{topic} is simpler than it seems. Here's why..."
                ],
                "transitional": [
                    f"{topic} has some interesting complexity. Let me walk you through it.",
                    f"I'll explain {topic} step by step so it makes sense.",
                    f"{topic} involves a few key concepts. Here's how they connect."
                ],
                "high_tension": [
                    f"{topic} is quite complex, but I'll break it down for you.",
                    f"This is advanced material about {topic}, so let's build up slowly.",
                    f"{topic} requires careful explanation. I'll simplify the key ideas."
                ],
                "saturated": [
                    f"{topic} is extremely advanced. Let's start with the basics.",
                    f"This topic pushes current understanding. Here's what we know at a foundational level.",
                    f"{topic} is at the cutting edge. I'll give you an accessible overview."
                ]
            }
            
            import random
            base = random.choice(base_explanations[regime])
            
            # Add YOUR preferred learning style
            style_additions = []
            
            if prefs.get('prefers_visual', 0) > 0.5:
                style_additions.append("A visual way to think about this is...")
            
            if prefs.get('prefers_examples', 0) > 0.5:
                style_additions.append("For example...")
            
            if prefs.get('prefers_analogies', 0) > 0.5:
                style_additions.append("An analogy would be...")
            
            if prefs.get('prefers_technical', 0) > 0.5 and regime != "saturated":
                style_additions.append("Technically speaking...")
            
            if style_additions:
                style = random.choice(style_additions)
                return f"{base} {style}"
            else:
                return base
    
    # Create your translator
    translator = YourPersonalTranslator(your_profile, topic_database, translation_strategies)
    
    # Test with some topics
    test_topics = [
        "quantum entanglement",
        "calculus derivatives", 
        "blockchain technology",
        "photosynthesis process",
        "string theory",
        "existentialism"
    ]
    
    print(f"\n🧪 TESTING YOUR PERSONAL TRANSLATOR")
    print("="*60)
    
    results = []
    for topic in test_topics[:4]:  # Test first 4
        result = translator.translate_for_you(topic)
        results.append(result)
        print("-" * 50)
    
    # Show insights about YOU
    print(f"\n{'='*60}")
    print("🔍 INSIGHTS ABOUT YOUR LEARNING PROFILE")
    print("="*60)
    
    # Find easiest and hardest topics for YOU
    easy_topics = []
    hard_topics = []
    
    for topic_name, topic_info in topic_database.items():
        category = topic_info["category"]
        your_skill = your_profile.get(category, 0.5)
        adjusted = max(0.1, topic_info["tension"] - (your_skill * 0.5))
        
        if adjusted < 0.4:
            easy_topics.append((topic_name, adjusted))
        elif adjusted > 0.8:
            hard_topics.append((topic_name, adjusted))
    
    print(f"\n🎯 TOPICS THAT ARE EASIER FOR YOU (adjusted tension < 0.4):")
    for topic, tension in sorted(easy_topics, key=lambda x: x[1])[:5]:
        category = topic_database[topic]["category"]
        your_skill = your_profile.get(category, 0.5)
        print(f"   • {topic}: {tension:.2f} (your {category} skill: {your_skill:.2f})")
    
    print(f"\n🎯 TOPICS THAT ARE HARDER FOR YOU (adjusted tension > 0.8):")
    for topic, tension in sorted(hard_topics, key=lambda x: x[1], reverse=True)[:5]:
        category = topic_database[topic]["category"]
        your_skill = your_profile.get(category, 0.5)
        print(f"   • {topic}: {tension:.2f} (your {category} skill: {your_skill:.2f})")
    
    print(f"\n💡 RECOMMENDATION: Start with topics around tension 0.4-0.6 for optimal learning")
    
    return translator

if __name__ == "__main__":
    translator = build_your_translator()
    
    # Interactive mode
    print(f"\n{'='*60}")
    print("💬 INTERACTIVE MODE - Ask me to translate any topic!")
    print("Type 'quit' to exit, 'profile' to see your profile")
    print("="*60)
    
    while True:
        topic = input("\n📚 What topic should I translate for YOU? ").strip()
        
        if topic.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! Your profile is saved.")
            break
        elif topic.lower() == 'profile':
            with open('your_substrate_profile.json', 'r') as f:
                profile = json.load(f)
            print(json.dumps(profile, indent=2))
            continue
        elif not topic:
            continue
        
        # Check if we have this topic
        topic_lower = topic.lower()
        
        # Add some common topics if not in database
        topic_synonyms = {
            "ai": "artificial intelligence ethics",
            "machine learning": "neural networks",
            "quantum": "quantum entanglement",
            "blockchain": "blockchain technology",
            "photosynthesis": "photosynthesis process",
            "calculus": "calculus derivatives",
            "relativity": "general relativity",
            "strings": "string theory"
        }
        
        actual_topic = topic_synonyms.get(topic_lower, topic_lower)
        
        try:
            translator.translate_for_you(actual_topic)
        except:
            print(f"🤔 I don't have detailed data on '{topic}' yet.")
            print("But based on your profile, I'd explain it at an appropriate level for you.")
