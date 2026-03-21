import json
import os

with open("unified_constants.json", "r") as f:
    data = json.load(f)

print("--- SXC GLOBAL HEALTH CHECK (v1.2.3) ---")
# 1. Drift Check
drifted = 0
for mod, vals in data["modules"].items():
    path = f"../{mod}_module/coefficients.json"
    if os.path.exists(path):
        with open(path) as f:
            current = json.load(f)
            c_g = current.get("coefficients", current).get("gamma")
            if abs(float(c_g) - vals["gamma"]) > 1e-7:
                print(f"❌ DRIFT: {mod}")
                drifted += 1
if drifted == 0: print("✅ COHESION: All modules in sync.")

# 2. Periodic Instability Peak (Shatter Risk)
print("\n--- TOP CROSS-DOMAIN SHATTER RISKS ---")
for entry in data["shatter_analysis"][:5]:
    print(f"🔥 {entry['pair']:25} | Tension: {entry['tension']}")

