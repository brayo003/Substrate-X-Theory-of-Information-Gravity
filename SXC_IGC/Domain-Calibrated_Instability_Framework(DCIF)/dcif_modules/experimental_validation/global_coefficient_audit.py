import os
import json
import pandas as pd

def audit_all_modules():
    results = []
    base_dir = "."
    modules = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and "_module" in d.lower()]
    
    for mod in modules:
        c_path = os.path.join(mod, "coefficients.json")
        if os.path.exists(c_path):
            with open(c_path, 'r') as f:
                data = json.load(f)
                results.append({
                    "Module": mod,
                    "Beta": data.get("beta"),
                    "Gamma": data.get("gamma"),
                    "Ratio": data.get("beta") / data.get("gamma") if data.get("gamma") else 0
                })
    
    df = pd.DataFrame(results).sort_values(by="Ratio")
    print("\nSXC-V12: GLOBAL SUBSTRATE AUDIT")
    print("-" * 50)
    print(df.to_string(index=False))
    df.to_csv("global_audit_results.csv")
    print("-" * 50)
    print("Audit saved to global_audit_results.csv")

if __name__ == "__main__":
    audit_all_modules()
