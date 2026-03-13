# V12_SYNC_VERIFIED: 2026-03-13
#!/usr/bin/env python3
"""
YOUR PERSONAL AI TRANSLATOR - Real working version
"""
import json
import sys
import os

# Load YOUR profile
with open('your_substrate_profile.json', 'r') as f:
    YOUR_PROFILE = json.load(f)

print("🤖 YOUR PERSONAL AI TRANSLATOR")
print("="*60)
print(f"Welcome back! I remember your substrate profile:")
print(f"- Expert in: {', '.join([k for k,v in YOUR_PROFILE.items() if isinstance(v, (int, float)) and v > 0.7][:3])}...")
print(f"- Beginner in: {', '.join([k for k,v in YOUR_PROFILE.items() if isinstance(v, (int, float)) and v < 0.3])}")
print(f"- Prefers: {[k.replace('prefers_', '') for k,v in YOUR_PROFILE.get('preferences', {}).items() if v > 0.5]}")
print()

# Topic database with real explanations
TOPIC_DATABASE = {
    "quantum entanglement": {
        "category": "physics",
        "tension": 0.92,
        "explanations": {
            "vanilla": "Quantum entanglement is like having two coins that always land the same way, even miles apart!",
            "transitional": "Entangled particles share a quantum state. Measuring one instantly determines the other's state, defying classical intuition.",
            "high_tension": "Non-separable quantum states exhibiting non-local correlations that violate Bell inequalities.",
            "saturated": "ψ₁₂ = (|01⟩ + |10⟩)/√2 where measurement collapses the wavefunction non-locally."
        }
    },
    "blockchain": {
        "category": "computer_science", 
        "tension": 0.70,
        "explanations": {
            "vanilla": "Blockchain is like a shared Google Doc that everyone can see but no one can erase.",
            "transitional": "A distributed ledger using cryptographic hashes in blocks, with consensus mechanisms like Proof of Work.",
            "high_tension": "Immutable linked-list data structure with Merkle trees enabling decentralized trust via cryptographic verification.",
            "saturated": "Implementing Byzantine fault tolerance through Nakamoto consensus with SHA-256 cryptographic primitives."
        }
    },
    "photosynthesis": {
        "category": "biology",
        "tension": 0.45,
        "explanations": {
            "vanilla": "Plants use sunlight to make food from air and water - like solar-powered kitchens!",
            "transitional": "6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂. Chlorophyll captures light energy for sugar production.",
            "high_tension": "Photophosphorylation in thylakoid membranes drives Calvin cycle carbon fixation via RuBisCO.",
            "saturated": "Non-cyclic electron flow generates proton gradient for ATP synthase while NADP⁺ reduction occurs."
        }
    },
    "machine learning": {
        "category": "computer_science",
        "tension": 0.75,
        "explanations": {
            "vanilla": "Computers that learn from examples, like showing a child many cats until they recognize cats.",
            "transitional": "Algorithms that improve performance on tasks through experience, using training data.",
            "high_tension": "Optimizing loss functions via gradient descent on parameterized models like neural networks.",
            "saturated": "Backpropagation through computational graphs with regularization to prevent overfitting."
        }
    },
    "existentialism": {
        "category": "philosophy",
        "tension": 0.62,
        "explanations": {
            "vanilla": "The idea that we create our own meaning in life, like being authors of our own story.",
            "transitional": "Philosophical movement emphasizing individual existence, freedom, and choice in an absurd universe.",
            "high_tension": "Rejection of essentialism in favor of existential becoming, where existence precedes essence.",
            "saturated": "Heideggerian Dasein's thrownness and Sartrean bad faith in the face of radical freedom."
        }
    }
}

def calculate_your_tension(topic_name):
    """Calculate adjusted tension for YOU"""
    topic = TOPIC_DATABASE.get(topic_name.lower())
    if not topic:
        return None
    
    universal_tension = topic["tension"]
    category = topic["category"]
    
    # Get YOUR skill in this category
    your_skill = YOUR_PROFILE.get(category, 0.5)
    
    # Skill adjustment: experts find things easier
    skill_adjustment = your_skill * 0.5  # Up to 50% reduction
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
    
    return {
        "topic": topic_name,
        "category": category,
        "universal_tension": universal_tension,
        "your_skill": your_skill,
        "adjusted_tension": adjusted_tension,
        "regime": regime
    }

def generate_prompt_for_you(analysis):
    """Generate a prompt for GPT/Ollama based on YOUR profile"""
    topic = analysis["topic"]
    regime = analysis["regime"]
    category = analysis["category"]
    your_skill = analysis["your_skill"]
    
    # Get your preferences
    prefs = YOUR_PROFILE.get('preferences', {})
    visual = prefs.get('prefers_visual', 0) > 0.5
    analogies = prefs.get('prefers_analogies', 0) > 0.5
    technical = prefs.get('prefers_technical', 0) > 0.5
    attention = prefs.get('attention_span', 0.5) * 60  # Convert to minutes
    
    # Skill level description
    if your_skill > 0.7:
        skill_desc = "expert-level understanding"
    elif your_skill > 0.4:
        skill_desc = "intermediate knowledge"
    else:
        skill_desc = "beginner level"
    
    # Build the prompt
    prompt = f"""Explain '{topic}' to someone with:

CONTEXT:
- They have {skill_desc} in {category}
- This is {regime} difficulty for them
- Attention span: {attention:.0f} minutes

LEARNING PREFERENCES:
- {"Prefers visual explanations" if visual else "No strong visual preference"}
- {"Loves analogies" if analogies else "Doesn't prefer analogies"}
- {"Enjoys technical details" if technical else "Prefers conceptual over technical"}

REQUIREMENTS:
1. Match the {regime} difficulty level
2. Respect their learning preferences above
3. Keep it engaging for their attention span
4. Use appropriate depth for their {skill_desc}

Explanation:"""
    
    return prompt

def get_explanation_for_you(topic_name):
    """Get explanation tailored for YOU"""
    analysis = calculate_your_tension(topic_name)
    if not analysis:
        return f"I don't have '{topic_name}' in my database yet."
    
    print(f"\n🎯 TRANSLATING '{topic_name}' FOR YOU")
    print("="*50)
    print(f"📊 Analysis:")
    print(f"   Category: {analysis['category']}")
    print(f"   Universal tension: {analysis['universal_tension']:.2f}")
    print(f"   Your skill: {analysis['your_skill']:.2f}")
    print(f"   Adjusted for YOU: {analysis['adjusted_tension']:.2f}")
    print(f"   Regime: {analysis['regime'].upper()}")
    
    # Get base explanation
    topic_data = TOPIC_DATABASE[topic_name.lower()]
    base_explanation = topic_data["explanations"][analysis["regime"]]
    
    # Get your preferences
    prefs = YOUR_PROFILE.get('preferences', {})
    
    # Enhance with your preferences
    explanation = base_explanation
    
    if prefs.get('prefers_analogies', 0) > 0.5 and "like" not in explanation.lower():
        analogy = "\n\n📖 ANALOGY FOR YOU: "
        if topic_name.lower() == "quantum entanglement":
            analogy += "Think of it as having two magical dice that always show matching numbers, no matter how far apart they are."
        elif topic_name.lower() == "blockchain":
            analogy += "Imagine a public notebook where every page references the previous page, making it impossible to change old entries."
        elif topic_name.lower() == "photosynthesis":
            analogy += "It's like a plant running a solar-powered kitchen that turns air and water into food."
        explanation += analogy
    
    if prefs.get('prefers_visual', 0) > 0.5:
        visual = "\n\n🎨 VISUAL FOR YOU: "
        if topic_name.lower() == "quantum entanglement":
            visual += "Picture two particles connected by an invisible string - measuring one instantly tugs the other."
        elif topic_name.lower() == "blockchain":
            visual += "Visualize a chain of blocks, each containing transactions, linked by cryptographic fingerprints."
        explanation += visual
    
    if prefs.get('prefers_technical', 0) > 0.5 and analysis["regime"] != "vanilla":
        technical = "\n\n🔬 TECHNICAL DETAIL (you prefer these): "
        if topic_name.lower() == "quantum entanglement":
            technical += "The Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2 exhibits maximum entanglement."
        elif topic_name.lower() == "blockchain":
            technical += "Each block contains previous block's hash: Hₙ = SHA256(Hₙ₋₁ + transactions + nonce)."
        explanation += technical
    
    print(f"\n💡 EXPLANATION TAILORED FOR YOU:")
    print("-" * 40)
    print(explanation)
    print("-" * 40)
    
    # Show what GPT prompt would be
    print(f"\n📝 PROMPT I'D SEND TO GPT/OLLAMA:")
    print("-" * 40)
    print(generate_prompt_for_you(analysis))
    print("-" * 40)
    
    return explanation

# Interactive mode
print("💬 YOUR PERSONAL TRANSLATOR IS READY!")
print("I'll explain any topic at the PERFECT level for YOU.")
print("Type 'topics' to see available topics, 'quit' to exit")
print("="*60)

available_topics = list(TOPIC_DATABASE.keys())

while True:
    user_input = input("\n📚 What should I explain for YOU? ").strip().lower()
    
    if user_input in ['quit', 'exit', 'q']:
        print("\n👋 Goodbye! Remember, your profile is saved.")
        print("Next time, I'll remember exactly what you can handle!")
        break
    
    elif user_input == 'topics':
        print("\n📚 AVAILABLE TOPICS:")
        for topic in available_topics:
            topic_data = TOPIC_DATABASE[topic]
            analysis = calculate_your_tension(topic)
            if analysis:
                print(f"  • {topic.title()}: {analysis['regime'].upper()} for you")
        continue
    
    elif user_input == 'profile':
        print(json.dumps(YOUR_PROFILE, indent=2))
        continue
    
    elif user_input == 'test':
        print("\n🧪 TESTING ALL TOPICS FOR YOU:")
        for topic in available_topics:
            get_explanation_for_you(topic)
            input("\nPress Enter for next topic...")
        continue
    
    # Find matching topic
    matched_topic = None
    for topic in available_topics:
        if user_input in topic or topic in user_input:
            matched_topic = topic
            break
    
    if matched_topic:
        get_explanation_for_you(matched_topic)
    else:
        print(f"\n🤔 I don't have '{user_input}' in my detailed database.")
        print("But based on your profile, I know YOU prefer:")
        prefs = YOUR_PROFILE.get('preferences', {})
        if prefs.get('prefers_analogies', 0) > 0.5:
            print("  • Analogies and metaphors")
        if prefs.get('prefers_visual', 0) > 0.5:
            print("  • Visual explanations")
        if prefs.get('prefers_technical', 0) > 0.5:
            print("  • Technical details")
        print(f"\n💡 For '{user_input}', I'd explain it with those preferences in mind!")
