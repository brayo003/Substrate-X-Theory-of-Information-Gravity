import json
import os
import numpy as np

print("\n=== TEST 4: CROSS-DOMAIN COEFFICIENT SANITY ===\n")
# This checks the DCIF outputs for obvious red flags

module_paths = [
    "./finance_module/coefficients.json",
    "./seismic_module/coefficients.json",
    "./particle_physics_module/coefficients.json"
]

for path in module_paths:
    if os.path.exists(path):
        try:
            with open(path) as f:
                coeff = json.load(f)
            # Check for extreme, unphysical coefficient values
            # Coefficients should typically be within a few orders of magnitude of 1
            extreme_vals = []
            for key, val in coeff.get('coefficients', {}).items():
                if isinstance(val, (int, float)):
                    if abs(val) > 1e9 or (abs(val) < 1e-9 and abs(val) > 0):
                        extreme_vals.append((key, val))
            
            if extreme_vals:
                print(f"⚠️  {path}: Contains extreme coefficients: {extreme_vals}")
                print("   Review DCIF calibration for this domain.")
            else:
                print(f"✅ {path}: Coefficients within plausible range.")
        except Exception as e:
            print(f"❌ {path}: Error reading file - {e}")
    else:
        print(f"  {path}: Not found (skipping).")
