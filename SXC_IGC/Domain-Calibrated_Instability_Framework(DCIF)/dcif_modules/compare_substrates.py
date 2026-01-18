import os
import json
import numpy as np

def audit_all_modules():
    modules = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]
    print(f"{'Module Domain':<30} | {'Beta (Sens)':<10} | {'Gamma (Damp)':<10} | {'State'}")
    print("-" * 70)
    
    for mod in modules:
        config_path = os.path.join(mod, 'coefficients.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                # Extract calibrated weights from each domain's unique JSON
                beta = data.get('beta', 0.0)
                gamma = data.get('gamma', 0.0)
                
                # Determine logical stability state
                state = "STABLE" if gamma > 0 else "DECAYING"
                if abs(gamma) < 0.001 and beta > 1.0: state = "METASTABLE"
                
                print(f"{mod:<30} | {beta:>10.4f} | {gamma:>10.4f} | {state}")

if __name__ == "__main__":
    audit_all_modules()
