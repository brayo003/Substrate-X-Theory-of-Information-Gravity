import os
import json
import numpy as np

def run_stress_test(E_shock=0.4, F_load=0.2):
    base_dir = "./dcif_modules"
    results = []
    
    for module in sorted(os.listdir(base_dir)):
        path = os.path.join(base_dir, module, "coefficients.json")
        if not os.path.exists(path): continue
        
        with open(path, 'r') as f:
            data = json.load(f)
        c = data['coefficients']
        
        # Calculate Tension T = α(0) + βE - γF
        T = (c['beta'] * E_shock) - (c['gamma'] * F_load)
        
        # Distance to Tipping Point (assuming critical T=0.6)
        Dtp = 0.6 - T
        results.append({"name": module, "T": T, "Dtp": Dtp, "tax": data.get('taxonomy', 'N/A')})

    # Sort by highest Tension
    results.sort(key=lambda x: x['T'], reverse=True)
    
    print(f"{'SUBSTRATE':<30} | {'TENSION':<10} | {'Dtp':<10} | {'TAXONOMY'}")
    print("-" * 80)
    for r in results:
        status = "⚠️ CRITICAL" if r['T'] >= 0.6 else "✅ STABLE"
        print(f"{r['name']:<30} | {r['T']:>10.4f} | {r['Dtp']:>10.4f} | {r['tax']} {status}")

if __name__ == "__main__":
    print("--- SXC-IGC GLOBAL STRESS TEST: E=0.4, F=0.2 ---")
    run_stress_test()
