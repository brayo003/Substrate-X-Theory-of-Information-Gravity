#!/usr/bin/env python3
"""
PRACTICAL APPLICATION: How this solves real AI problems
"""
from cognitive_governor_final import CognitiveGovernor

def demonstrate_real_world():
    """Show real-world applications"""
    gov = CognitiveGovernor()
    
    print("🛡️ PRACTICAL AI SAFETY APPLICATIONS")
    print("="*70)
    
    scenarios = [
        {
            "context": "Medical diagnosis assistant",
            "question": "Diagnose this rare neurological condition from these symptoms",
            "risk": "Misdiagnosis could be fatal"
        },
        {
            "context": "Legal advisor", 
            "question": "Interpret this complex contract clause about liability",
            "risk": "Wrong advice could cause lawsuits"
        },
        {
            "context": "Financial advisor",
            "question": "Predict stock market movements for next month",
            "risk": "Bad predictions could lose money"
        },
        {
            "context": "Homework helper",
            "question": "What is 2+2?",
            "risk": "Low - simple fact"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*70}")
        print(f"📋 CONTEXT: {scenario['context']}")
        print(f"❓ QUESTION: {scenario['question']}")
        print(f"⚡ RISK: {scenario['risk']}")
        
        result = gov.process_question(scenario['question'])
        
        print(f"\n🔬 SUBSTRATE ANALYSIS:")
        print(f"   Tension: {result['tension']:.2f}")
        print(f"   Regime: {result['regime'].upper()}")
        
        print(f"\n🛡️  SAFETY MECHANISM:")
        
        if result['tension'] < 0.3:
            print(f"   ✅ LOW RISK: Can answer directly")
            print(f"   Confidence level: Appropriate (not overconfident)")
            
        elif result['tension'] < 0.6:
            print(f"   ⚠️  MEDIUM RISK: Answer comes with warnings")
            print(f"   Safety: User knows answer might be unreliable")
            
        elif result['tension'] < 0.9:
            print(f"   🚨 HIGH RISK: Uses specialized tools")
            print(f"   Safety: Structured approach reduces hallucinations")
            
        else:
            print(f"   ❌ DANGER ZONE: Would decline to answer")
            print(f"   Safety: Prevents catastrophic failure")
            
        print(f"\n💡 PRACTICAL BENEFIT:")
        if scenario['risk'] != "Low - simple fact":
            print(f"   Prevents dangerous overconfidence in high-risk domains")
    
    print(f"\n{'='*70}")
    print("🎯 REAL-WORLD IMPACT:")
    print("Current AI: Gives confident answers even when wrong")
    print("Our System: Knows when to be uncertain → Prevents harm")

if __name__ == "__main__":
    demonstrate_real_world()
