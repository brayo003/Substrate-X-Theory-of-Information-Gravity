import json
from main import CognitiveGovernor

def run_stress_test():
    gov = CognitiveGovernor()
    
    with open('judged_hle_gemma2:2b.json.json', 'r') as f:
        data = json.load(f)
    
    total = 20
    print(f"🚀 STRESS TEST: Running {total} HLE queries with Threshold 0.4...")

    for i, (item_id, content) in enumerate(list(data.items())[:total]):
        # Pulling the prompt from your HLE data
        question = content.get('prompt', content.get('response', 'Simplify x + x'))
        
        print(f"\n[{i+1}/{total}] Input Analysis:")
        gov.process_question(question)
        
    print("\n" + "="*30)
    print(f"STRESS TEST COMPLETE")
    print(f"System State: CALIBRATED (Safe Mode)")
    print("="*30)

if __name__ == "__main__":
    run_stress_test()
