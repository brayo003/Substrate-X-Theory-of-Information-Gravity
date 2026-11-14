import json
import numpy as np
from v12_engine import SXCOmegaEngine

def analyze_bulk_data():
    engine = SXCOmegaEngine(beta=3.8, gamma=0.85)
    
    with open('bulk_signals.json', 'r') as f:
        payload = json.load(f)
    
    signals = []
    # GDC specific path: data -> hits -> diagnoses -> age_at_diagnosis
    for hit in payload.get('data', {}).get('hits', []):
        diags = hit.get('diagnoses', [])
        for d in diags:
            # Using Age at Diagnosis as a proxy for 'Systemic Accumulation Time'
            # Divided by 365 to get age in years as the signal intensity
            val = d.get('age_at_diagnosis')
            if val is not None:
                signals.append(float(val) / 365.0)

    if not signals:
        print("CRITICAL: No numerical signals found in JSON. Checking keys...")
        return

    print(f"LOADED: {len(signals)} Real-World Biological Signals (Patient Ages).")
    print(f"{'INDEX':<6} | {'SIGNAL':<8} | {'T_SYS':<10} | {'PHASE':<10}")
    print("-" * 45)

    for i, s in enumerate(signals[:50]):
        t_sys, phase = engine.step(s)
        print(f"{i:<6} | {s:<8.2f} | {t_sys:<10.4f} | {phase:<10}")
        
        if phase == "FIREWALL" and i > 0:
            # Log the exact point where regulatory coherence failed
            pass

if __name__ == "__main__":
    analyze_bulk_data()
