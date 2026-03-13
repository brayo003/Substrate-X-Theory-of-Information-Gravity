#!/usr/bin/env python3
import json
import numpy as np
from problem_analyzer import ProblemAnalyzer
from substrate_core import SubstrateDynamics

def run_calibration():
    print("🔄 STARTING SUBSTRATE AUTO-TUNE...")
    
    # 1. Load your actual HLE performance data
    try:
        with open('judged_hle_gemma2:2b.json.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: judged_hle_gemma2:2b.json.json not found.")
        return

    analyzer = ProblemAnalyzer()
    substrate = SubstrateDynamics()
    
    results = []

    # 2. Map Tension vs. Reality
    for item_id, content in data.items():
        # Use the 'response' or 'judge_response' to simulate the input
        sample_text = content.get('response', "")
        is_correct = content.get('judge_response', {}).get('correct') == 'yes'
        
        features = analyzer.extract_features(sample_text)
        tension = analyzer.predict_tension_from_features(features)
        
        results.append({
            'tension': tension,
            'correct': is_correct
        })

    # 3. Find the "Collapse Point" (Point where Tension leads to 0% accuracy)
    results.sort(key=lambda x: x['tension'])
    
    print("\n📊 SUBSTRATE ANALYSIS BY TENSION BANDS:")
    print(f"{'Tension':<10} | {'Accuracy':<10} | {'Status'}")
    print("-" * 35)

    thresholds = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    optimal_threshold = 0.8 # Default

    for i in range(len(thresholds)-1):
        low, high = thresholds[i], thresholds[i+1]
        band = [r for r in results if low <= r['tension'] < high]
        
        if band:
            acc = sum(1 for r in band if r['correct']) / len(band)
            status = "STABLE" if acc > 0.5 else "COLLAPSING"
            print(f"{low:>3.1f} - {high:>3.1f} | {acc:>9.1%} | {status}")
            
            # If accuracy drops below 20%, this is our new ABORT threshold
            if acc < 0.2 and optimal_threshold == 0.8:
                optimal_threshold = low

    print(f"\n✨ CALIBRATION COMPLETE")
    print(f"🔹 Recommended ABORT Threshold: {optimal_threshold}")
    print(f"🔹 This is the 'Event Horizon' for Gemma 2B on your hardware.")

    # 4. Update the Strategy Profile automatically
    update_strategy(optimal_threshold)

def update_strategy(new_threshold):
    # This simulates updating the adaptive_thinker.py thresholds
    print(f"📝 UPDATING adaptive_thinker.py with threshold {new_threshold}...")

if __name__ == "__main__":
    run_calibration()
